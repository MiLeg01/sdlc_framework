#!/usr/bin/env python3
"""Run Agent Commons contract, capability, integration, and workflow evaluations."""

from __future__ import annotations

import argparse
import html
import hashlib
import json
import os
import posixpath
import re
import shlex
import shutil
import stat
import statistics
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from eval_common import (
    ROOT,
    EvalConfigError,
    load_capability_contracts,
    load_hard_fail_assertions,
    load_json,
    load_thresholds,
    load_workflows,
    resolve_reference,
    stable_unique,
    validate_against_schema,
    validate_configuration,
)
from select_impacted_evals import git_changed_files, select_impacted
from semantic_provider import (
    AuthenticationError,
    ProviderError,
    provider_from_environment,
)
from semantic_runtime import RuntimeConfigError, runtime_from_environment


PASS = "PASS"
WARNING = "WARNING"
REGRESSION_FAIL = "REGRESSION_FAIL"
HARD_FAIL = "HARD_FAIL"

QUALITY_REGRESSION = "QUALITY_REGRESSION"
DETERMINISTIC_FAILURE = "DETERMINISTIC_FAILURE"
INFRASTRUCTURE_FAILURE = "INFRASTRUCTURE_FAILURE"
PROTOCOL_FAILURE = "PROTOCOL_FAILURE"

PERFORMANCE_METRICS = (
    "llm_calls",
    "input_tokens",
    "output_tokens",
    "subagents_launched",
    "context_compactions",
    "source_files_read",
    "duplicate_source_reads",
    "dashboard_renders",
    "external_searches",
    "executor_duration_seconds",
    "judge_duration_seconds",
    "judge_input_tokens",
    "judge_output_tokens",
    "judge_total_tokens",
    "executor_attempts",
    "judge_attempts",
)

PROFILE_ALIASES = {
    "smoke": "fast",
    "pr": "fast",
    "nightly": "full",
    "weekly": "deep",
}
EVAL_PROFILES = ("fast", "standard", "full", "deep", *PROFILE_ALIASES)
RETRYABLE_INFRASTRUCTURE_MARKERS = (
    "429",
    "rate limit",
    "temporarily unavailable",
    "connection reset",
    "connection timed out",
    "service unavailable",
)

DEFAULT_EXECUTOR_COMMAND = shlex.join([
    sys.executable, str(ROOT / "tools" / "evals" / "semantic_executor.py"),
])
DEFAULT_JUDGE_COMMAND = shlex.join([
    sys.executable, str(ROOT / "tools" / "evals" / "semantic_judge.py"),
])


def semantic_configuration(output_dir: Optional[Path] = None) -> dict[str, Any]:
    """Check production semantic configuration without making a model request."""
    def value(name: str, default: str = "") -> str:
        resolved = os.environ.get(name, default).strip()
        return default if resolved.startswith("$(") else resolved

    result_directory = output_dir or ROOT / "output" / "eval-results"
    if not result_directory.is_absolute():
        result_directory = ROOT / result_directory
    baseline_definition = value("BASELINE_PIPELINE_DEFINITION_ID")
    azure_pipeline = value("TF_BUILD").lower() == "true"
    report: dict[str, Any] = {
        "runner": {"available": True, "root": str(ROOT)},
        "executor": {"available": False},
        "judge": {"available": False},
        "provider_available": False,
        "provider": value("EVAL_PROVIDER", "azure_openai"),
        "executor_model": value("EVAL_EXECUTOR_MODEL"),
        "judge_model": value("EVAL_JUDGE_MODEL"),
        "authentication": "unavailable",
        "judge_independence": "not_configured",
        "azure_baseline": (
            f"configured (definition {baseline_definition})"
            if baseline_definition else "bootstrap baseline"
        ),
        "quality_history": (
            f"nightly definition {baseline_definition}"
            if baseline_definition else "current run only"
        ),
        "result_directory": {"writable": False, "path": str(result_directory)},
        "environment": "azure" if azure_pipeline else "local",
    }
    errors: list[str] = []
    for required in (
        ROOT / "tools" / "evals" / "semantic_executor.py",
        ROOT / "tools" / "evals" / "semantic_judge.py",
    ):
        if not required.is_file():
            report["runner"]["available"] = False
            errors.append(f"repository runner component is missing: {required.relative_to(ROOT)}")
    try:
        result_directory.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=result_directory, prefix=".config-check-", delete=True):
            pass
        report["result_directory"]["writable"] = True
    except OSError as exc:
        errors.append(f"result directory is not writable: {result_directory}: {exc}")
    if azure_pipeline and not baseline_definition:
        errors.append("BASELINE_PIPELINE_DEFINITION_ID is required in Azure Pipelines")
    try:
        executor = runtime_from_environment(
            output_schema=ROOT / "evals" / "schemas" / "codex-executor-output.schema.json",
        )
        checked_executor = executor.check_config(require_auth=True)
        report["executor"] = {"available": True, **checked_executor}
    except (RuntimeConfigError, ValueError) as exc:
        report["executor"]["error"] = str(exc)
        errors.append(str(exc))
    try:
        provider = provider_from_environment()
        checked = provider.check_config(resolve_auth=True)
        report["judge"] = {"available": True, **checked}
        report["provider_available"] = True
        report["provider"] = checked["provider"]
    except (ProviderError, AuthenticationError, ValueError) as exc:
        report["judge"]["error"] = str(exc)
        errors.append(str(exc))
    executor_auth = report["executor"].get("authentication", "unavailable")
    judge_auth = report["judge"].get("authentication", "unavailable")
    report["authentication"] = f"executor={executor_auth}; judge={judge_auth}"
    report["available"] = not errors
    if report["executor_model"] and report["judge_model"]:
        report["judge_independence"] = (
            "different_configured_models"
            if report["executor_model"] != report["judge_model"]
            else "same_configured_model"
        )
    report["errors"] = errors
    return report


def render_semantic_configuration(report: dict[str, Any]) -> str:
    def state(name: str) -> str:
        item = report[name]
        return "available" if item.get("available") else f"unavailable ({item.get('error')})"

    return "\n".join([
        "Semantic evaluation configuration",
        f"Environment: {report['environment']}",
        f"Runner: {state('runner')}",
        f"Executor: {state('executor')}",
        f"Judge: {state('judge')}",
        f"Provider: {'available' if report['provider_available'] else 'unavailable'} ({report['provider']})",
        f"Executor model: {report['executor_model'] or 'not configured'}",
        f"Judge model: {report['judge_model'] or 'not configured'}",
        f"Authentication: {report['authentication']}",
        f"Judge independence: {report['judge_independence']}",
        f"Azure baseline: {report['azure_baseline']}",
        f"Quality history: {report['quality_history']}",
        "Result directory: " + (
            f"writable ({report['result_directory']['path']})"
            if report["result_directory"]["writable"]
            else f"unavailable ({report['result_directory']['path']})"
        ),
    ])


def canonical_profile(profile: str) -> str:
    """Return the cost-oriented profile name while preserving legacy CLI aliases."""
    return PROFILE_ALIASES.get(profile, profile)


def default_repeat_for_profile(profile: str, defaults: dict[str, Any]) -> int:
    """Resolve stochastic repetition without making inexpensive profiles exhaustive."""
    return {
        "fast": 1,
        "standard": 1,
        "full": int(defaults["nightly_repeat"]),
        "deep": int(defaults["weekly_repeat"]),
    }[canonical_profile(profile)]


def select_capabilities_by_kind(
    contracts: dict[str, dict[str, Any]],
    kinds: list[str],
) -> list[str]:
    selected = set(kinds)
    return [
        identifier
        for identifier, contract in contracts.items()
        if contract.get("kind", "capability") in selected
    ]


def is_retryable_infrastructure_failure(completed: subprocess.CompletedProcess[str]) -> bool:
    if completed.returncode == 75:
        return True
    evidence = f"{completed.stdout or ''}\n{completed.stderr or ''}".lower()
    return completed.returncode != 0 and any(
        marker in evidence for marker in RETRYABLE_INFRASTRUCTURE_MARKERS
    )


def result_record(
    subject: str,
    subject_kind: str,
    scenario: str,
    level: int,
    run: int,
    deterministic: bool,
    status: str,
    duration: float,
    reason: str = "",
    score: Optional[float] = None,
    threshold: Any = None,
    tokens: Optional[int] = None,
    metrics: Optional[dict[str, float]] = None,
    performance_metrics: Optional[dict[str, Any]] = None,
    failure_type: Optional[str] = None,
    attempts: Optional[dict[str, int]] = None,
    logs: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    if failure_type is None and status not in {PASS, WARNING}:
        lowered = reason.lower()
        if any(marker in lowered for marker in (
            "infrastructure", "timed out", "rate limit", "service unavailable",
            "connection reset", "authentication", "configuration error",
        )):
            failure_type = INFRASTRUCTURE_FAILURE
        elif any(marker in lowered for marker in (
            "protocol", "invalid json", "invalid executor output", "invalid judge input",
            "judge output", "assertion coverage", "unknown evidence", "unbounded sources",
            "locators do not resolve", "duplicate evidence",
        )):
            failure_type = PROTOCOL_FAILURE
        elif deterministic:
            failure_type = DETERMINISTIC_FAILURE
        else:
            failure_type = QUALITY_REGRESSION
    return {
        "capability": subject,
        "subject_kind": subject_kind,
        "scenario": scenario,
        "level": level,
        "run": run,
        "deterministic": deterministic,
        "status": status,
        "severity": status,
        "score": score,
        "threshold": threshold,
        "duration_seconds": round(duration, 6),
        "tokens": tokens,
        "reason": reason or None,
        "failure_reason": reason or None,
        "metrics": metrics or {},
        "performance_metrics": performance_metrics or normalize_performance_metrics({}),
        "failure_type": failure_type,
        "attempts": attempts or {},
        "logs": logs or {},
    }


EXPECTED_ASSERTION_FIELDS = (
    "expected_facts",
    "invariants",
    "required_sequence",
    "hard_assertions",
)


def assertion_identifier(value: Any) -> str:
    if isinstance(value, dict):
        identifier = value.get("id")
        if isinstance(identifier, str) and identifier:
            return identifier
    return str(value)


def expected_fact_records(golden: dict[str, Any]) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for value in golden.get("expected_facts", []):
        if isinstance(value, dict):
            identifier = assertion_identifier(value)
            severity = str(value.get("severity", "MAJOR")).upper()
            text = str(value.get("text", identifier))
        else:
            identifier = str(value)
            severity = "MAJOR"
            text = identifier
        records.append({"id": identifier, "severity": severity, "text": text})
    return records


def expected_assertions(golden: dict[str, Any]) -> list[str]:
    return stable_unique(
        assertion_identifier(value)
        for field in EXPECTED_ASSERTION_FIELDS
        for value in golden.get(field, [])
    )


def filter_required_judge_assertions(
    judgement: dict[str, Any], required_assertions: set[str],
) -> dict[str, Any]:
    """Ignore extra judge criteria while retaining every canonical assertion for scoring."""
    filtered = dict(judgement)
    filtered["assertions"] = [
        item for item in judgement.get("assertions", [])
        if item.get("assertion") in required_assertions
    ]
    return filtered


def classify_assertion_failures(failed_names: set[str], golden: dict[str, Any]) -> str:
    critical = {
        item["id"] for item in expected_fact_records(golden)
        if item["severity"] == "CRITICAL"
    }
    hard_names = {
        assertion_identifier(value) for value in golden.get("hard_assertions", [])
    } | load_hard_fail_assertions() | critical
    if failed_names & hard_names:
        return HARD_FAIL
    if failed_names:
        return REGRESSION_FAIL
    return PASS


def calculate_fact_metrics(judgement: dict[str, Any], golden: dict[str, Any]) -> dict[str, Any]:
    expected = {item["id"] for item in expected_fact_records(golden)}
    assertions = {
        str(item.get("assertion")): str(item.get("status"))
        for item in judgement.get("assertions", [])
        if isinstance(item, dict)
    }
    correct = sum(assertions.get(identifier) == "PASS" for identifier in expected)
    unsupported = judgement.get("unsupported_findings", [])
    unsupported_count = len(unsupported) if isinstance(unsupported, list) else 0
    recall = correct / len(expected) if expected else 1.0
    asserted_findings = correct + unsupported_count
    precision = correct / asserted_findings if asserted_findings else (1.0 if not expected else 0.0)
    return {
        "expected_facts": len(expected),
        "correct_findings": correct,
        "unsupported_findings": unsupported_count,
        "recall": recall,
        "precision": precision,
    }


def normalize_performance_metrics(value: Any) -> dict[str, Any]:
    source = value if isinstance(value, dict) else {}
    normalized: dict[str, Any] = {}
    for name in PERFORMANCE_METRICS:
        metric = source.get(name)
        if isinstance(metric, (int, float)) and not isinstance(metric, bool) and metric >= 0:
            normalized[name] = metric
        else:
            normalized[name] = "not_available"
    for name in ("model", "runtime", "judge_model", "judge_provider", "judge_independence"):
        metric = source.get(name)
        if isinstance(metric, str) and metric:
            normalized[name] = metric
    return normalized


def run_source_contract(
    identifier: str,
    subject_kind: str,
    contract: dict[str, Any],
    scenario: dict[str, Any],
) -> dict[str, Any]:
    started = time.monotonic()
    path = ROOT / contract["path"]
    failures: list[str] = []
    if not path.is_file():
        failures.append(f"missing canonical source {contract['path']}")
    else:
        text = path.read_text(encoding="utf-8")
        if subject_kind == "agent":
            try:
                data = json.loads(text)
                if data.get("id") != identifier:
                    failures.append("agent id does not match contract")
            except json.JSONDecodeError as exc:
                failures.append(f"invalid agent contract: {exc}")
        elif subject_kind == "skill" and f"name: {identifier}" not in text:
            failures.append("skill frontmatter name does not match contract")
        elif subject_kind == "tool" and not text.startswith("#!/usr/bin/env python3"):
            failures.append("tool does not expose the canonical Python entry point")
    try:
        golden = resolve_reference(scenario["golden"], "golden")
        if not golden.get("expected_facts") and not golden.get("required_sequence"):
            failures.append("golden expectation has no semantic facts or required sequence")
        if not golden.get("invariants"):
            failures.append("golden expectation has no invariants")
    except EvalConfigError as exc:
        failures.append(str(exc))
    status = HARD_FAIL if failures else PASS
    return result_record(
        identifier,
        subject_kind,
        scenario["id"],
        scenario["level"],
        1,
        True,
        status,
        time.monotonic() - started,
        "; ".join(failures),
        0.0 if failures else 1.0,
        1.0,
    )


def run_process(
    command: list[str],
    input_data: Optional[dict[str, Any]] = None,
    cwd: Path = ROOT,
    environment: Optional[dict[str, str]] = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        input=json.dumps(input_data) if input_data is not None else None,
        capture_output=True,
        text=True,
        timeout=1800,
    )


def deterministic_environment(environment: Optional[dict[str, str]] = None) -> dict[str, str]:
    """Remove semantic runtime configuration and credentials from deterministic checks."""
    source = environment if environment is not None else os.environ
    excluded = {
        "AZURE_OPENAI_API_KEY",
        "CODEX_ACCESS_TOKEN",
        "OPENAI_API_KEY",
        "SYSTEM_ACCESSTOKEN",
    }
    return {
        name: value
        for name, value in source.items()
        if not name.startswith("EVAL_") and name not in excluded
    }


def run_process_with_infrastructure_retry(
    command: list[str],
    input_data: dict[str, Any],
    cwd: Path,
    retries: int,
) -> tuple[subprocess.CompletedProcess[str], int]:
    attempts = 0
    while True:
        attempts += 1
        completed = run_process(command, input_data, cwd)
        if not is_retryable_infrastructure_failure(completed) or attempts > retries:
            return completed, attempts
        time.sleep(min(2 ** (attempts - 1), 8))


def repository_snapshot() -> dict[str, str]:
    listed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout.split(b"\0")
    snapshot: dict[str, str] = {}
    for raw_path in listed:
        if not raw_path:
            continue
        relative = raw_path.decode("utf-8", errors="surrogateescape")
        path = ROOT / relative
        if path.is_symlink():
            snapshot[relative] = f"mode:{stat.S_IMODE(path.lstat().st_mode):o}:symlink:{path.readlink()}"
        elif path.is_file():
            snapshot[relative] = (
                f"mode:{stat.S_IMODE(path.stat().st_mode):o}:"
                f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"
            )
        else:
            snapshot[relative] = "missing"
    return snapshot


def changed_snapshot_paths(before: dict[str, str], after: dict[str, str]) -> list[str]:
    return sorted(
        path
        for path in set(before) | set(after)
        if before.get(path) != after.get(path)
    )


def directory_snapshot(root: Path) -> dict[str, str]:
    snapshot: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if "__pycache__" in relative.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        if path.is_file():
            snapshot[relative.as_posix()] = (
                f"mode:{stat.S_IMODE(path.stat().st_mode):o}:"
                f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"
            )
    return snapshot


def bounded_evidence_contents(
    workspace: Path,
    initial_snapshot: dict[str, str],
    executor_artifacts: dict[str, bytes],
) -> dict[str, str]:
    """Read every file already bounded by the isolated workspace plus executor outputs."""
    contents: dict[str, str] = {}
    for relative in initial_snapshot:
        path = workspace / relative
        if path.is_file():
            contents[relative] = path.read_text(encoding="utf-8", errors="replace")
    contents.update({
        relative: payload.decode("utf-8", errors="replace")
        for relative, payload in executor_artifacts.items()
    })
    return contents


def invalid_workspace_changes(changed: list[str], fixture: dict[str, Any]) -> list[str]:
    policy = fixture.get("workspace_policy", {})
    writable = {str(path) for path in policy.get("writable_artifacts", [])}
    prefixes = tuple(str(path).rstrip("/") + "/" for path in policy.get("generated_prefixes", []))
    return sorted(path for path in changed if path not in writable and not path.startswith(prefixes))


def validate_evidence_locators(evidence: list[dict[str, Any]], contents: dict[str, str]) -> list[str]:
    failures: list[str] = []
    for item in evidence:
        source = str(item["source"])
        locator = str(item["locator"])
        match = re.search(r"(?::|^)(\d+)(?:-(\d+))?$", locator)
        if not match:
            failures.append(f"{item['id']} has an unresolvable locator: {locator}")
            continue
        start = int(match.group(1))
        end = int(match.group(2) or start)
        line_count = len(contents.get(source, "").splitlines())
        if start < 1 or end < start or end > line_count:
            failures.append(
                f"{item['id']} locator {locator} is outside {source} (lines={line_count})"
            )
    return failures


def normalize_evidence_source(source: str) -> Optional[str]:
    """Normalize harmless model formatting without allowing workspace escapes."""
    normalized = posixpath.normpath(source.strip().replace("\\", "/"))
    if normalized in {"", "."} or normalized.startswith("/"):
        return None
    if normalized == ".." or normalized.startswith("../"):
        return None
    return normalized.removeprefix("./")


def prepare_isolated_workspace(workspace: Path, contract: dict[str, Any], fixture: dict[str, Any]) -> None:
    relative_paths = list(fixture.get("source_artifacts", []))
    relative_paths.extend(fixture.get("workspace_dependencies", []))
    if contract.get("path"):
        relative_paths.append(contract["path"])
    for relative in stable_unique(str(value) for value in relative_paths):
        source = (ROOT / relative).resolve()
        source.relative_to(ROOT.resolve())
        destination = workspace / relative
        if source.is_dir():
            shutil.copytree(
                source,
                destination,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
            )
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
    capability_paths: list[str] = []
    if contract.get("path"):
        capability_paths.append(str(contract["path"]))
    for capability in contract.get("capabilities", []):
        referenced = load_capability_contracts().get("capabilities", {}).get(str(capability), {})
        if referenced.get("path"):
            capability_paths.append(str(referenced["path"]))
    for relative in stable_unique(capability_paths):
        source = (ROOT / relative).resolve()
        source.relative_to(ROOT.resolve())
        if relative.startswith("skills/"):
            source = source.parent
            destination = workspace / source.relative_to(ROOT)
            shutil.copytree(source, destination, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        elif source.is_file():
            destination = workspace / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
    (workspace / "AGENTS.md").write_text(
        "# Isolated semantic evaluation workspace\n\n"
        "Use only files in this workspace.\n"
        "Do not inspect parent directories.\n"
        "Do not search for Golden expectations or answer keys.\n"
        "Follow the selected capability and scenario.\n"
        "Preserve fixture inputs.\n"
        "Write only approved artifacts.\n",
        encoding="utf-8",
    )


def fixture_artifact_manifest(contract: dict[str, Any], fixture: dict[str, Any]) -> dict[str, str]:
    relative_paths = list(fixture.get("source_artifacts", []))
    if contract.get("path"):
        relative_paths.append(contract["path"])
    return {
        relative: hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        for relative in stable_unique(str(value) for value in relative_paths)
    }


def run_deterministic(
    identifier: str,
    subject_kind: str,
    scenario: dict[str, Any],
    python_executable: str,
) -> dict[str, Any]:
    execution = scenario["execution"]
    kind = execution["kind"]
    if kind == "unittest":
        command = [python_executable, "-m", "unittest", *execution.get("modules", [])]
    else:
        command = [str(value) for value in execution.get("argv", [])]
    started = time.monotonic()
    if not command:
        return result_record(
            identifier, subject_kind, scenario["id"], scenario["level"], 1, True,
            HARD_FAIL, time.monotonic() - started, "empty deterministic command", 0.0, 1.0,
        )
    try:
        completed = run_process(command, environment=deterministic_environment())
    except (OSError, subprocess.TimeoutExpired) as exc:
        return result_record(
            identifier, subject_kind, scenario["id"], scenario["level"], 1, True,
            HARD_FAIL, time.monotonic() - started, f"command failed to execute: {exc}", 0.0, 1.0,
        )
    reason = ""
    if completed.returncode:
        evidence = (completed.stderr or completed.stdout).strip()
        reason = f"command exited {completed.returncode}: {evidence[-2000:]}"
    return result_record(
        identifier,
        subject_kind,
        scenario["id"],
        scenario["level"],
        1,
        True,
        PASS if completed.returncode == 0 else HARD_FAIL,
        time.monotonic() - started,
        reason,
        1.0 if completed.returncode == 0 else 0.0,
        1.0,
    )


def run_unittest_scenario(
    identifier: str,
    subject_kind: str,
    scenario: dict[str, Any],
    python_executable: str,
    module_cache: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    newly_executed: set[str] = set()
    scenario_results: list[tuple[str, dict[str, Any]]] = []
    for module in scenario["execution"].get("modules", []):
        if module not in module_cache:
            module_scenario = dict(scenario)
            module_scenario["execution"] = {"kind": "unittest", "modules": [module]}
            module_cache[module] = run_deterministic(
                identifier, subject_kind, module_scenario, python_executable,
            )
            newly_executed.add(module)
        scenario_results.append((module, module_cache[module]))
    if not scenario_results:
        return result_record(
            identifier, subject_kind, scenario["id"], scenario["level"], 1, True,
            HARD_FAIL, 0.0, "unittest scenario has no modules", 0.0, 1.0,
        )
    failures = [
        f"{module}: {result.get('reason') or result['status']}"
        for module, result in scenario_results
        if result["status"] != PASS
    ]
    duration = sum(
        float(result["duration_seconds"])
        for module, result in scenario_results
        if module in newly_executed
    )
    return result_record(
        identifier,
        subject_kind,
        scenario["id"],
        scenario["level"],
        1,
        True,
        HARD_FAIL if failures else PASS,
        duration,
        "; ".join(failures) if failures else (
            "covered by earlier deterministic invocations in this run" if not newly_executed else ""
        ),
        0.0 if failures else 1.0,
        1.0,
    )


def validate_judge_output(data: Any, valid_metrics: set[str]) -> list[str]:
    errors = validate_against_schema(data, "evals/schemas/judge-output.schema.json")
    if not isinstance(data, dict):
        return errors
    allowed_fields = {"assertions", "metrics", "unsupported_findings", "performance"}
    if not set(data) <= allowed_fields or not {"assertions", "metrics"} <= set(data):
        errors.append(
            "judge output fields must be assertions, metrics, and optional unsupported_findings/performance"
        )
    assertions = data.get("assertions")
    if not isinstance(assertions, list) or not assertions:
        errors.append("judge output requires non-empty assertions")
    else:
        for index, assertion in enumerate(assertions):
            if not isinstance(assertion, dict):
                errors.append(f"assertion {index} is not an object")
                continue
            if set(assertion) != {"assertion", "status", "confidence", "reason", "evidence"}:
                errors.append(f"assertion {index} has unexpected or missing fields")
            if assertion.get("status") not in {"PASS", "FAIL"}:
                errors.append(f"assertion {index} has invalid status")
            confidence = assertion.get("confidence")
            if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
                errors.append(f"assertion {index} has invalid confidence")
            for field in ("assertion", "reason", "evidence"):
                if not isinstance(assertion.get(field), str) or not assertion[field].strip():
                    errors.append(f"assertion {index} lacks {field}")
    metrics = data.get("metrics", {})
    if not isinstance(metrics, dict):
        errors.append("judge metrics must be an object")
    else:
        for metric, value in metrics.items():
            if metric not in valid_metrics:
                errors.append(f"judge metric {metric} is unknown")
            if not isinstance(value, (int, float)) or not 0 <= value <= 1:
                errors.append(f"judge metric {metric} must be between 0 and 1")
    unsupported = data.get("unsupported_findings", [])
    if not isinstance(unsupported, list) or any(
        not isinstance(item, str) or not item.strip() for item in unsupported
    ):
        errors.append("unsupported_findings must be an array of non-empty strings")
    return errors


def run_external(
    identifier: str,
    subject_kind: str,
    contract: dict[str, Any],
    scenario: dict[str, Any],
    run_number: int,
    executor_command: Optional[str],
    judge_command: Optional[str],
    require_semantic: bool,
    thresholds: dict[str, Any],
    infrastructure_retries: int,
    deterministic_findings: Optional[list[dict[str, Any]]] = None,
) -> dict[str, Any]:
    started = time.monotonic()
    if not executor_command:
        status = HARD_FAIL if require_semantic else WARNING
        return result_record(
            identifier, subject_kind, scenario["id"], scenario["level"], run_number, False,
            status, time.monotonic() - started,
            "semantic executor unavailable; configure the repository-owned runtime" if not require_semantic
            else "required semantic executor unavailable",
        )
    if not judge_command:
        return result_record(
            identifier, subject_kind, scenario["id"], scenario["level"], run_number, False,
            HARD_FAIL, time.monotonic() - started,
            "independent semantic judge unavailable; configure the repository-owned provider",
        )
    if shlex.split(executor_command) == shlex.split(judge_command):
        return result_record(
            identifier, subject_kind, scenario["id"], scenario["level"], run_number, False,
            HARD_FAIL, time.monotonic() - started,
            "executor and independent judge commands must differ",
        )
    fixture = resolve_reference(scenario["fixture"], "fixture")
    golden = resolve_reference(scenario["golden"], "golden")
    artifact_manifest = fixture_artifact_manifest(contract, fixture)
    executor_input = {
        "schema_version": 1,
        "capability": identifier,
        "subject_kind": subject_kind,
        "scenario": scenario["id"],
        "scenario_input": fixture,
        "canonical_source": contract.get("path"),
        "artifact_manifest": artifact_manifest,
        "workspace_root": ".",
    }
    executor_input_errors = validate_against_schema(
        executor_input, "evals/schemas/executor-input.schema.json",
    )
    if executor_input_errors:
        return result_record(
            identifier, subject_kind, scenario["id"], scenario["level"], run_number, False,
            HARD_FAIL, time.monotonic() - started,
            "invalid executor input: " + "; ".join(executor_input_errors),
        )
    repository_before = repository_snapshot()
    try:
        with tempfile.TemporaryDirectory(prefix="agent-commons-eval-") as temporary:
            workspace = Path(temporary)
            prepare_isolated_workspace(workspace, contract, fixture)
            workspace_before = directory_snapshot(workspace)
            executed, executor_attempts = run_process_with_infrastructure_retry(
                shlex.split(executor_command), executor_input, workspace, infrastructure_retries,
            )
            workspace_changes = changed_snapshot_paths(workspace_before, directory_snapshot(workspace))
            executor_artifact_payloads = {
                relative: (workspace / relative).read_bytes()
                for relative in workspace_changes
                if (workspace / relative).is_file()
            }
            executor_deleted_paths = [
                relative for relative in workspace_changes if not (workspace / relative).exists()
            ]
            evidence_contents = bounded_evidence_contents(
                workspace, workspace_before, executor_artifact_payloads,
            )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return result_record(
            identifier, subject_kind, scenario["id"], scenario["level"], run_number, False,
            HARD_FAIL, time.monotonic() - started, f"executor failed: {exc}",
        )
    invalid_changes = invalid_workspace_changes(workspace_changes, fixture)
    if invalid_changes:
        return result_record(
            identifier, subject_kind, scenario["id"], scenario["level"], run_number, False,
            HARD_FAIL, time.monotonic() - started,
            "executor modified isolated fixture paths outside the workspace policy: " + ", ".join(invalid_changes),
        )
    workspace_policy_finding = {
        "scenario": "workspace-policy",
        "status": PASS,
        "score": 1.0,
        "reason": (
            "executor made no workspace changes"
            if not workspace_changes
            else "executor changes were limited to authorized paths: " + ", ".join(workspace_changes)
        ),
    }
    modified_paths = changed_snapshot_paths(repository_before, repository_snapshot())
    if modified_paths:
        return result_record(
            identifier, subject_kind, scenario["id"], scenario["level"], run_number, False,
            HARD_FAIL, time.monotonic() - started,
            "executor modified repository paths: " + ", ".join(modified_paths),
        )
    if executed.returncode:
        if executed.returncode == 76:
            failure_kind = "executor protocol failure"
            failure_type = PROTOCOL_FAILURE
        elif executed.returncode == 78 or is_retryable_infrastructure_failure(executed):
            failure_kind = f"infrastructure failure after {executor_attempts} attempts"
            failure_type = INFRASTRUCTURE_FAILURE
        else:
            failure_kind = "executor quality failure"
            failure_type = QUALITY_REGRESSION
        return result_record(
            identifier, subject_kind, scenario["id"], scenario["level"], run_number, False,
            HARD_FAIL, time.monotonic() - started,
            f"{failure_kind}; executor exited {executed.returncode}: {(executed.stderr or executed.stdout)[-2000:]}",
            failure_type=failure_type,
            attempts={"executor": executor_attempts},
            logs={"executor": (executed.stderr or executed.stdout)[-4000:]},
        )
    try:
        generated = json.loads(executed.stdout)
    except json.JSONDecodeError as exc:
        return result_record(
            identifier, subject_kind, scenario["id"], scenario["level"], run_number, False,
            HARD_FAIL, time.monotonic() - started, f"executor returned invalid JSON: {exc}",
            attempts={"executor": executor_attempts},
            logs={"executor": executed.stderr[-4000:]},
        )
    executor_output_errors = validate_against_schema(
        generated, "evals/schemas/executor-output.schema.json",
    )
    if executor_output_errors:
        return result_record(
            identifier, subject_kind, scenario["id"], scenario["level"], run_number, False,
            HARD_FAIL, time.monotonic() - started,
            "invalid executor output: " + "; ".join(executor_output_errors),
            attempts={"executor": executor_attempts},
            logs={"executor": executed.stderr[-4000:]},
        )
    evidence_ids = [str(evidence["id"]) for evidence in generated["evidence"]]
    duplicate_evidence_ids = sorted({
        identifier for identifier in evidence_ids if evidence_ids.count(identifier) > 1
    })
    if duplicate_evidence_ids:
        return result_record(
            identifier, subject_kind, scenario["id"], scenario["level"], run_number, False,
            HARD_FAIL, time.monotonic() - started,
            "executor output has duplicate evidence IDs: " + ", ".join(duplicate_evidence_ids),
        )
    normalized_contents = {
        normalized: content
        for source, content in evidence_contents.items()
        if (normalized := normalize_evidence_source(source)) is not None
    }
    invalid_evidence_values: list[str] = []
    for evidence in generated["evidence"]:
        source = str(evidence["source"])
        normalized = normalize_evidence_source(source)
        if normalized is None:
            invalid_evidence_values.append(source)
        else:
            evidence["source"] = normalized
    allowed_evidence_sources = set(normalized_contents)
    invalid_evidence_sources = sorted({
        str(evidence["source"])
        for evidence in generated["evidence"]
        if evidence["source"] not in allowed_evidence_sources
    } | set(invalid_evidence_values))
    if invalid_evidence_sources:
        return result_record(
            identifier, subject_kind, scenario["id"], scenario["level"], run_number, False,
            HARD_FAIL, time.monotonic() - started,
            "executor evidence references unbounded sources: " + ", ".join(invalid_evidence_sources),
        )
    invalid_locators = validate_evidence_locators(generated["evidence"], normalized_contents)
    if invalid_locators:
        return result_record(
            identifier, subject_kind, scenario["id"], scenario["level"], run_number, False,
            HARD_FAIL, time.monotonic() - started,
            "executor evidence locators do not resolve: " + "; ".join(invalid_locators),
        )
    generated_tokens = generated.get("tokens")
    if generated_tokens is not None and (
        not isinstance(generated_tokens, int)
        or isinstance(generated_tokens, bool)
        or generated_tokens < 0
    ):
        return result_record(
            identifier, subject_kind, scenario["id"], scenario["level"], run_number, False,
            HARD_FAIL, time.monotonic() - started,
            "executor output tokens must be a non-negative integer",
        )
    performance_metrics = normalize_performance_metrics(generated.get("performance"))
    performance_metrics["executor_attempts"] = executor_attempts
    if isinstance(generated.get("performance"), dict):
        duration = generated["performance"].get("duration_seconds")
        if isinstance(duration, (int, float)) and not isinstance(duration, bool) and duration >= 0:
            performance_metrics["executor_duration_seconds"] = duration
    if generated_tokens is None:
        token_parts = [performance_metrics["input_tokens"], performance_metrics["output_tokens"]]
        if all(isinstance(value, (int, float)) for value in token_parts):
            generated_tokens = int(sum(token_parts))
    required_semantic_metrics = set(contract.get("applicable_metrics", [])) - {
        "runtime", "token_context_efficiency",
    }
    required_judge_metrics = sorted(required_semantic_metrics - {"recall", "precision"})
    judge_input = {
        "scenario": {
            "capability": identifier,
            "id": scenario["id"],
            "level": scenario["level"],
            "input": fixture,
            "artifact_manifest": artifact_manifest,
        },
        "expected": golden,
        "generated_result": generated["generated_result"],
        "evidence": generated.get("evidence", []),
        "executor_artifacts": {
            "files": {
                relative: hashlib.sha256(payload).hexdigest()
                for relative, payload in executor_artifact_payloads.items()
            },
            "deleted_paths": executor_deleted_paths,
        },
        "deterministic_findings": [*(deterministic_findings or []), workspace_policy_finding],
        "required_metrics": required_judge_metrics,
    }
    judge_input_errors = validate_against_schema(judge_input, "evals/schemas/judge-input.schema.json")
    if judge_input_errors:
        return result_record(
            identifier, subject_kind, scenario["id"], scenario["level"], run_number, False,
            HARD_FAIL, time.monotonic() - started,
            "invalid judge input: " + "; ".join(judge_input_errors),
        )
    repository_before = repository_snapshot()
    try:
        with tempfile.TemporaryDirectory(prefix="agent-commons-judge-") as temporary:
            judge_workspace = Path(temporary)
            prepare_isolated_workspace(judge_workspace, contract, fixture)
            for relative, payload in executor_artifact_payloads.items():
                artifact = judge_workspace / relative
                artifact.parent.mkdir(parents=True, exist_ok=True)
                artifact.write_bytes(payload)
            for relative in executor_deleted_paths:
                artifact = judge_workspace / relative
                if artifact.is_file() or artifact.is_symlink():
                    artifact.unlink()
            judge_workspace_before = directory_snapshot(judge_workspace)
            judged, judge_attempts = run_process_with_infrastructure_retry(
                shlex.split(judge_command), judge_input, judge_workspace, infrastructure_retries,
            )
            judge_workspace_changes = changed_snapshot_paths(
                judge_workspace_before, directory_snapshot(judge_workspace),
            )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return result_record(
            identifier, subject_kind, scenario["id"], scenario["level"], run_number, False,
            HARD_FAIL, time.monotonic() - started, f"judge failed: {exc}",
        )
    if judge_workspace_changes:
        return result_record(
            identifier, subject_kind, scenario["id"], scenario["level"], run_number, False,
            HARD_FAIL, time.monotonic() - started,
            "judge modified isolated fixture paths: " + ", ".join(judge_workspace_changes),
        )
    modified_paths = changed_snapshot_paths(repository_before, repository_snapshot())
    if modified_paths:
        return result_record(
            identifier, subject_kind, scenario["id"], scenario["level"], run_number, False,
            HARD_FAIL, time.monotonic() - started,
            "judge modified repository paths: " + ", ".join(modified_paths),
        )
    if judged.returncode:
        if judged.returncode == 76:
            failure_kind = "judge protocol failure"
            failure_type = PROTOCOL_FAILURE
        elif judged.returncode == 78 or is_retryable_infrastructure_failure(judged):
            failure_kind = f"infrastructure failure after {judge_attempts} attempts"
            failure_type = INFRASTRUCTURE_FAILURE
        else:
            failure_kind = "judge quality failure"
            failure_type = QUALITY_REGRESSION
        return result_record(
            identifier, subject_kind, scenario["id"], scenario["level"], run_number, False,
            HARD_FAIL, time.monotonic() - started,
            f"{failure_kind}; judge exited {judged.returncode}: {(judged.stderr or judged.stdout)[-2000:]}",
            failure_type=failure_type,
            attempts={"executor": executor_attempts, "judge": judge_attempts},
            logs={
                "executor": executed.stderr[-4000:],
                "judge": (judged.stderr or judged.stdout)[-4000:],
            },
        )
    try:
        judgement = json.loads(judged.stdout)
    except json.JSONDecodeError as exc:
        return result_record(
            identifier, subject_kind, scenario["id"], scenario["level"], run_number, False,
            HARD_FAIL, time.monotonic() - started, f"judge returned invalid JSON: {exc}",
            attempts={"executor": executor_attempts, "judge": judge_attempts},
            logs={"executor": executed.stderr[-4000:], "judge": judged.stderr[-4000:]},
        )
    validation_errors = validate_judge_output(judgement, set(thresholds.get("metrics", {})))
    if validation_errors:
        return result_record(
            identifier, subject_kind, scenario["id"], scenario["level"], run_number, False,
            HARD_FAIL, time.monotonic() - started, "; ".join(validation_errors),
            attempts={"executor": executor_attempts, "judge": judge_attempts},
            logs={"executor": executed.stderr[-4000:], "judge": judged.stderr[-4000:]},
        )
    required_assertions = set(expected_assertions(golden))
    judgement = filter_required_judge_assertions(judgement, required_assertions)
    judged_names = [item["assertion"] for item in judgement["assertions"]]
    duplicate_names = sorted({name for name in judged_names if judged_names.count(name) > 1})
    missing_names = sorted(required_assertions - set(judged_names))
    coverage_errors: list[str] = []
    if missing_names:
        coverage_errors.append(f"missing required assertion coverage: {missing_names}")
    if duplicate_names:
        coverage_errors.append(f"duplicate judge assertions: {duplicate_names}")
    if coverage_errors:
        return result_record(
            identifier, subject_kind, scenario["id"], scenario["level"], run_number, False,
            HARD_FAIL, time.monotonic() - started, "; ".join(coverage_errors),
        )
    evidence_ids = set(evidence_ids)
    invalid_evidence_refs = sorted({
        item["evidence"]
        for item in judgement["assertions"]
        if item["evidence"] not in evidence_ids
    })
    if invalid_evidence_refs:
        return result_record(
            identifier, subject_kind, scenario["id"], scenario["level"], run_number, False,
            HARD_FAIL, time.monotonic() - started,
            "judge assertions reference unknown evidence IDs: " + ", ".join(invalid_evidence_refs),
        )
    failed_assertions = [item for item in judgement["assertions"] if item["status"] == "FAIL"]
    assertion_status = classify_assertion_failures(
        {item["assertion"] for item in failed_assertions}, golden,
    )
    metrics = {key: float(value) for key, value in judgement.get("metrics", {}).items()}
    judge_performance = judgement.get("performance", {})
    if isinstance(judge_performance, dict):
        mappings = {
            "duration_seconds": "judge_duration_seconds",
            "input_tokens": "judge_input_tokens",
            "output_tokens": "judge_output_tokens",
            "total_tokens": "judge_total_tokens",
            "model": "judge_model",
            "provider": "judge_provider",
            "judge_independence": "judge_independence",
        }
        for source_name, target_name in mappings.items():
            value = judge_performance.get(source_name)
            if value is not None:
                performance_metrics[target_name] = value
    performance_metrics["judge_attempts"] = judge_attempts
    fact_metrics = calculate_fact_metrics(judgement, golden)
    if "recall" in contract.get("applicable_metrics", []):
        metrics["recall"] = float(fact_metrics["recall"])
    if "precision" in contract.get("applicable_metrics", []):
        metrics["precision"] = float(fact_metrics["precision"])
    missing_metrics = sorted(required_semantic_metrics - set(metrics))
    if missing_metrics:
        return result_record(
            identifier, subject_kind, scenario["id"], scenario["level"], run_number, False,
            HARD_FAIL, time.monotonic() - started,
            f"judge omitted applicable metrics: {missing_metrics}",
        )
    below = []
    for metric in contract.get("applicable_metrics", []):
        policy = thresholds.get("metrics", {}).get(metric, {})
        if "minimum" in policy and metric in metrics and metrics[metric] < policy["minimum"]:
            below.append(f"{metric}={metrics[metric]:.3f} < {policy['minimum']:.3f}")
    if assertion_status == HARD_FAIL:
        status = HARD_FAIL
    elif assertion_status == REGRESSION_FAIL or below:
        status = REGRESSION_FAIL
    else:
        status = PASS
    reasons = [item["reason"] for item in failed_assertions] + below
    score = statistics.mean(metrics.values()) if metrics else (0.0 if failed_assertions else 1.0)
    judge_tokens = performance_metrics.get("judge_total_tokens")
    token_values = [
        value for value in (generated_tokens, judge_tokens)
        if isinstance(value, int) and not isinstance(value, bool)
    ]
    tokens = sum(token_values) if token_values else None
    return result_record(
        identifier, subject_kind, scenario["id"], scenario["level"], run_number, False,
        status, time.monotonic() - started, "; ".join(reasons), score, None, tokens, metrics,
        performance_metrics,
        attempts={"executor": executor_attempts, "judge": judge_attempts},
        logs={"executor": executed.stderr[-4000:], "judge": judged.stderr[-4000:]},
    )


def aggregate_performance(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for result in results:
        if result.get("subject_kind") == "baseline":
            continue
        key = f"{result['capability']}:{result['scenario']}"
        grouped.setdefault(key, []).append(result)
    output: list[dict[str, Any]] = []
    for key, items in sorted(grouped.items()):
        durations = [float(item["duration_seconds"]) for item in items]
        tokens = [int(item["tokens"]) for item in items if item["tokens"] is not None]
        passes = sum(item["status"] == PASS for item in items)
        scores = [float(item["score"]) for item in items if item["score"] is not None]
        metric_names = sorted({name for item in items for name in item.get("metrics", {})})
        metric_values = {
            name: [float(item["metrics"][name]) for item in items if name in item.get("metrics", {})]
            for name in metric_names
        }
        observed_performance = {
            name: [
                item.get("performance_metrics", {}).get(name)
                for item in items
                if isinstance(item.get("performance_metrics", {}).get(name), (int, float))
            ]
            for name in PERFORMANCE_METRICS
        }
        output.append({
            "scenario": key,
            "runs": len(items),
            "pass_rate": passes / len(items),
            "score_mean": statistics.mean(scores) if scores else None,
            "score_worst": min(scores) if scores else None,
            "score_variance": statistics.pvariance(scores) if len(scores) > 1 else 0.0 if scores else None,
            "duration_mean_seconds": statistics.mean(durations),
            "duration_worst_seconds": max(durations),
            "tokens_mean": statistics.mean(tokens) if tokens else "not_available",
            "tokens_worst": max(tokens) if tokens else "not_available",
            "metrics_mean": {name: statistics.mean(values) for name, values in metric_values.items()},
            "metrics_worst": {name: min(values) for name, values in metric_values.items()},
            "metrics_variance": {
                name: statistics.pvariance(values) if len(values) > 1 else 0.0
                for name, values in metric_values.items()
            },
            "performance_metrics": {
                name: statistics.mean(values) if values else "not_available"
                for name, values in observed_performance.items()
            },
        })
    return output


def evaluate_repeat_consistency(
    identifier: str,
    subject_kind: str,
    scenario: dict[str, Any],
    repeated_results: list[dict[str, Any]],
    thresholds: dict[str, Any],
) -> Optional[dict[str, Any]]:
    if len(repeated_results) < 2:
        return None
    if all(result["status"] == WARNING for result in repeated_results):
        return None
    values = [
        float(result["metrics"]["consistency"])
        for result in repeated_results
        if "consistency" in result.get("metrics", {})
    ]
    if len(values) != len(repeated_results):
        return result_record(
            identifier, subject_kind, f"{scenario['id']}-repeat-consistency", scenario["level"],
            1, True, HARD_FAIL, 0.0, "repeated semantic runs lack consistency measurements",
        )
    pass_rate = sum(result["status"] == PASS for result in repeated_results) / len(repeated_results)
    mean = statistics.mean(values)
    worst = min(values)
    variance = statistics.pvariance(values)
    policy = thresholds["metrics"]["consistency"]
    failures: list[str] = []
    if pass_rate < thresholds["defaults"]["minimum_stochastic_pass_rate"]:
        failures.append(
            f"pass rate {pass_rate:.3f} < {thresholds['defaults']['minimum_stochastic_pass_rate']:.3f}"
        )
    if worst < policy["minimum"]:
        failures.append(f"consistency worst {worst:.3f} < {policy['minimum']:.3f}")
    if variance > policy["maximum_variance"]:
        failures.append(
            f"consistency variance {variance:.6f} > {policy['maximum_variance']:.6f}"
        )
    return result_record(
        identifier,
        subject_kind,
        f"{scenario['id']}-repeat-consistency",
        scenario["level"],
        1,
        True,
        REGRESSION_FAIL if failures else PASS,
        0.0,
        "; ".join(failures),
        mean,
        policy,
        metrics={"consistency": mean},
    )


def compare_performance_to_baseline(
    performance: list[dict[str, Any]],
    baseline: dict[str, Any],
    thresholds: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    scenarios = baseline.get("scenarios", {})
    regressions: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    missing_scenarios: list[str] = []
    if baseline.get("status") != "accepted" or not scenarios:
        reason = "no accepted last-green baseline is available"
        regressions.append(result_record(
            "evaluation-baseline", "baseline", "comparison", 2, 1, True,
            WARNING, 0.0, reason,
        ))
        return ({
            "schema_version": 1,
            "baseline_commit": baseline.get("baseline_commit", "not_available"),
            "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "status": "NOT_AVAILABLE",
            "reason": reason,
            "rows": [],
        }, regressions)
    for current in performance:
        previous = scenarios.get(current["scenario"])
        if not isinstance(previous, dict):
            missing_scenarios.append(current["scenario"])
            rows.append({
                "scenario": current["scenario"],
                "metric": "comparison_coverage",
                "baseline": "not_available",
                "current": "available",
                "delta": "not_available",
                "threshold": "accepted last-green scenario required",
                "status": WARNING,
            })
            continue
        reasons: list[str] = []
        scenario_status = PASS
        old_pass = previous.get("pass_rate")
        if isinstance(old_pass, (int, float)):
            current_pass = current["pass_rate"]
            row_status = PASS
            if current_pass < old_pass:
                row_status = (
                    REGRESSION_FAIL
                    if current_pass < thresholds["defaults"]["minimum_stochastic_pass_rate"]
                    else WARNING
                )
                reasons.append(f"pass rate {current_pass:.3f} decreased from {old_pass:.3f}")
            rows.append({
                "scenario": current["scenario"],
                "metric": "pass_rate",
                "baseline": old_pass,
                "current": current_pass,
                "delta": current_pass - old_pass,
                "threshold": thresholds["defaults"]["minimum_stochastic_pass_rate"],
                "status": row_status,
            })
            if row_status == REGRESSION_FAIL:
                scenario_status = REGRESSION_FAIL
            elif row_status == WARNING:
                scenario_status = WARNING
        previous_metrics = previous.get("metrics_mean", {})
        current_metrics = current.get("metrics_mean", {})
        if isinstance(previous_metrics, dict) and isinstance(current_metrics, dict):
            for metric, old_value in previous_metrics.items():
                new_value = current_metrics.get(metric)
                policy = thresholds.get("metrics", {}).get(metric, {})
                tolerance = policy.get("regression_tolerance")
                if not isinstance(old_value, (int, float)) or not isinstance(new_value, (int, float)):
                    continue
                row_status = PASS
                if old_value > new_value:
                    if isinstance(tolerance, (int, float)) and old_value - new_value > tolerance:
                        row_status = REGRESSION_FAIL
                        scenario_status = REGRESSION_FAIL
                        reasons.append(
                            f"{metric} decreased from {old_value:.3f} to {new_value:.3f} "
                            f"beyond tolerance {tolerance:.3f}"
                        )
                    else:
                        row_status = WARNING
                        if scenario_status == PASS:
                            scenario_status = WARNING
                        reasons.append(
                            f"{metric} decreased from {old_value:.3f} to {new_value:.3f} within tolerance"
                        )
                rows.append({
                    "scenario": current["scenario"],
                    "metric": metric,
                    "baseline": old_value,
                    "current": new_value,
                    "delta": new_value - old_value,
                    "threshold": tolerance if tolerance is not None else "not_available",
                    "status": row_status,
                })
        old_duration = previous.get("duration_mean_seconds")
        new_duration = current.get("duration_mean_seconds")
        runtime_policy = thresholds["metrics"]["runtime"]
        if (
            isinstance(old_duration, (int, float))
            and isinstance(new_duration, (int, float))
            and old_duration >= runtime_policy["noise_floor_seconds"]
        ):
            increase = ((new_duration - old_duration) / old_duration) * 100
            row_status = PASS
            if increase > runtime_policy.get("fail_increase_percent", float("inf")):
                row_status = REGRESSION_FAIL
                scenario_status = REGRESSION_FAIL
                reasons.append(f"runtime increased {increase:.1f}% beyond fail threshold")
            elif increase > runtime_policy["warning_increase_percent"]:
                row_status = WARNING
                if scenario_status == PASS:
                    scenario_status = WARNING
                reasons.append(f"runtime increased {increase:.1f}%")
            rows.append({
                "scenario": current["scenario"],
                "metric": "runtime_seconds",
                "baseline": old_duration,
                "current": new_duration,
                "delta": new_duration - old_duration,
                "delta_percent": increase,
                "threshold": runtime_policy["warning_increase_percent"],
                "status": row_status,
            })
        old_tokens = previous.get("tokens_mean")
        new_tokens = current.get("tokens_mean")
        token_policy = thresholds["metrics"]["token_context_efficiency"]
        if (
            isinstance(old_tokens, (int, float))
            and isinstance(new_tokens, (int, float))
            and old_tokens >= token_policy["noise_floor_tokens"]
        ):
            increase = ((new_tokens - old_tokens) / old_tokens) * 100
            row_status = PASS
            if increase > token_policy.get("fail_increase_percent", float("inf")):
                row_status = REGRESSION_FAIL
                scenario_status = REGRESSION_FAIL
                reasons.append(f"tokens increased {increase:.1f}% beyond fail threshold")
            elif increase > token_policy["warning_increase_percent"]:
                row_status = WARNING
                if scenario_status == PASS:
                    scenario_status = WARNING
                reasons.append(f"tokens increased {increase:.1f}%")
            rows.append({
                "scenario": current["scenario"],
                "metric": "tokens",
                "baseline": old_tokens,
                "current": new_tokens,
                "delta": new_tokens - old_tokens,
                "delta_percent": increase,
                "threshold": token_policy["warning_increase_percent"],
                "status": row_status,
            })
        if reasons:
            subject, scenario = current["scenario"].split(":", 1)
            regressions.append(result_record(
                subject,
                "baseline",
                scenario,
                2,
                1,
                True,
                scenario_status,
                0.0,
                "; ".join(reasons),
                current.get("score_mean"),
                previous,
            ))
    if missing_scenarios:
        regressions.append(result_record(
            "evaluation-baseline", "baseline", "comparison-coverage", 2, 1, True,
            WARNING, 0.0,
            f"accepted baseline lacks {len(missing_scenarios)} current scenarios",
        ))
    overall = (
        REGRESSION_FAIL
        if any(item["status"] == REGRESSION_FAIL for item in regressions)
        else WARNING
        if any(item["status"] == WARNING for item in regressions)
        else PASS
    )
    return ({
        "schema_version": 1,
        "baseline_commit": baseline.get("baseline_commit", "not_available"),
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": overall,
        "rows": rows,
    }, regressions)


def apply_baseline_comparison(
    results: list[dict[str, Any]],
    performance: list[dict[str, Any]],
    baseline_path: Path,
    thresholds: dict[str, Any],
) -> list[dict[str, Any]]:
    del results
    _, regressions = compare_performance_to_baseline(
        performance, load_json(baseline_path), thresholds,
    )
    return regressions


def write_junit(path: Path, results: list[dict[str, Any]]) -> None:
    failures = sum(item["status"] in {HARD_FAIL, REGRESSION_FAIL} for item in results)
    skipped = sum(item["status"] == WARNING for item in results)
    suite = ET.Element(
        "testsuite",
        name="agent-commons-evals",
        tests=str(len(results)),
        failures=str(failures),
        skipped=str(skipped),
        time=f"{sum(item['duration_seconds'] for item in results):.6f}",
    )
    for result in results:
        case = ET.SubElement(
            suite,
            "testcase",
            classname=str(result["capability"]),
            name=f"{result['scenario']}[run={result['run']}]",
            time=f"{result['duration_seconds']:.6f}",
        )
        if result["status"] in {HARD_FAIL, REGRESSION_FAIL}:
            failure = ET.SubElement(case, "failure", type=result["status"])
            failure.text = result.get("failure_reason") or result["status"]
        elif result["status"] == WARNING:
            skipped_node = ET.SubElement(case, "skipped", message=result.get("failure_reason") or "warning")
            skipped_node.text = result.get("failure_reason") or "warning"
    ET.ElementTree(suite).write(path, encoding="utf-8", xml_declaration=True)


def current_commit() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True,
    )
    return completed.stdout.strip() if completed.returncode == 0 else "not_available"


def current_branch() -> str:
    completed = subprocess.run(
        ["git", "branch", "--show-current"], cwd=ROOT, capture_output=True, text=True,
    )
    value = completed.stdout.strip()
    return value if completed.returncode == 0 and value else "detached"


def visual_baseline_summary(visual_report: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
    path = ROOT / "evals" / "fixtures" / "visual-regression" / "manifest.json"
    if not path.is_file():
        return []
    manifest = load_json(path)
    verified = {
        item.get("id"): item for item in (visual_report or {}).get("results", [])
        if isinstance(item, dict)
    }
    output = []
    for state in manifest.get("states", []):
        screenshot = ROOT / str(state.get("screenshot", ""))
        report_item = verified.get(state.get("id"), {})
        output.append({
            "id": state.get("id"),
            "artifact": state.get("artifact"),
            "screenshot": state.get("screenshot"),
            "status": (
                report_item.get("status")
                if report_item
                else "NOT_VERIFIED" if screenshot.is_file() else "MISSING"
            ),
            "checks": report_item.get("checks", {}),
        })
    return output


def write_quality_report(
    output: Path,
    selection: dict[str, Any],
    results: list[dict[str, Any]],
    performance: list[dict[str, Any]],
    counts: dict[str, int],
    status: str,
    comparison: Optional[dict[str, Any]] = None,
    mutation: Optional[dict[str, Any]] = None,
    visual_report: Optional[dict[str, Any]] = None,
) -> None:
    failures = [item for item in results if item["status"] != PASS]
    subjects: dict[str, list[dict[str, Any]]] = {}
    for item in performance:
        subject, _ = item["scenario"].split(":", 1)
        subjects.setdefault(subject, []).append(item)
    subject_scores = {}
    for subject, items in subjects.items():
        scores = [item["score_mean"] for item in items if isinstance(item.get("score_mean"), (int, float))]
        subject_scores[subject] = {
            "pass_rate": statistics.mean(item["pass_rate"] for item in items),
            "score": statistics.mean(scores) if len(scores) == len(items) else "not_available",
            "score_coverage": f"{len(scores)}/{len(items)}",
        }
    subject_kinds = {
        item["capability"]: item["subject_kind"]
        for item in results
        if item.get("subject_kind") != "baseline"
    }
    capability_scores = {
        subject: value for subject, value in subject_scores.items()
        if subject_kinds.get(subject) != "workflow"
    }
    workflow_scores = {
        subject: value for subject, value in subject_scores.items()
        if subject_kinds.get(subject) == "workflow"
    }
    overall = "FAIL" if status in {HARD_FAIL, REGRESSION_FAIL} else "WARN" if status == WARNING else "PASS"
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "overall": overall,
        "overall_status": status,
        "status": status,
        "baseline_commit": comparison.get("baseline_commit", "not_available") if comparison else "not_available",
        "current_commit": current_commit(),
        "counts": counts,
        "selection": selection,
        "capability_scores": capability_scores,
        "workflow_scores": workflow_scores,
        "capability_and_workflow_scores": subject_scores,
        "regressions": comparison.get("rows", []) if comparison else [],
        "performance": performance,
        "mutation": mutation if mutation is not None else "not_available",
        "visuals": visual_baseline_summary(visual_report),
        "top_failures": failures[:10],
    }
    (output / "quality-summary.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8",
    )
    rows = "".join(
        "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            html.escape(subject),
            html.escape(str(values["pass_rate"])),
            html.escape(str(values["score"])),
        )
        for subject, values in sorted(subject_scores.items())
    )
    failures_html = "".join(
        f"<li><strong>{html.escape(item['capability'])}</strong>: {html.escape(str(item.get('reason') or item['status']))}</li>"
        for item in failures[:10]
    ) or "<li>None</li>"
    comparison_html = "".join(
        "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            html.escape(str(item.get("metric"))),
            html.escape(str(item.get("baseline"))),
            html.escape(str(item.get("current"))),
            html.escape(str(item.get("delta"))),
            html.escape(str(item.get("threshold"))),
            html.escape(str(item.get("status"))),
        )
        for item in payload["regressions"]
    ) or "<tr><td colspan=\"6\">No comparable last-green measurements.</td></tr>"
    if isinstance(mutation, dict):
        mutation_score = mutation.get("mutation_score")
        mutation_score_text = (
            f"{float(mutation_score) * 100:.1f}%"
            if isinstance(mutation_score, (int, float)) and not isinstance(mutation_score, bool)
            else "not_available"
        )
        mutation_text = (
            f"{mutation.get('detected_harmful_mutations', 0)}/"
            f"{mutation.get('evaluated_harmful_mutations', mutation.get('total_harmful_mutations', 0))} "
            f"evaluated mutations detected ({mutation_score_text}); "
            f"infrastructure errors: {len(mutation.get('infrastructure_errors', []))}"
        )
    else:
        mutation_text = "not_available"
    document = f"""<!doctype html>
<html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">
<title>Agent Commons quality summary</title><style>
body{{font:16px/1.5 system-ui,sans-serif;max-width:1100px;margin:auto;padding:2rem;color:#172033;background:#f6f8fb}}
main{{background:white;padding:2rem;border-radius:14px;box-shadow:0 8px 30px #17203314}}table{{border-collapse:collapse;width:100%}}
th,td{{padding:.65rem;border-bottom:1px solid #d9dfeb;text-align:left}}.status{{font-size:1.5rem;font-weight:700}}
</style></head><body><main><h1>Agent Commons quality summary</h1><p class=\"status\">{html.escape(overall)}</p>
<p>Current: <code>{html.escape(payload['current_commit'])}</code><br>Last green: <code>{html.escape(payload['baseline_commit'])}</code></p>
<h2>Capability and workflow scores</h2><table><thead><tr><th>Subject</th><th>Pass rate</th><th>Score</th></tr></thead><tbody>{rows}</tbody></table>
<h2>Current vs last green</h2><table><thead><tr><th>Metric</th><th>Baseline</th><th>Current</th><th>Delta</th><th>Threshold</th><th>Status</th></tr></thead><tbody>{comparison_html}</tbody></table>
<h2>Top failures</h2><ul>{failures_html}</ul><p>Mutation: {html.escape(mutation_text)}</p>
<p>Visual baselines verified: {sum(item['status'] == 'PASS' for item in payload['visuals'])}/{len(payload['visuals'])}</p></main></body></html>"""
    (output / "quality-summary.html").write_text(document, encoding="utf-8")


def write_outputs(
    output: Path,
    selection: dict[str, Any],
    results: list[dict[str, Any]],
    comparison: Optional[dict[str, Any]] = None,
    mutation: Optional[dict[str, Any]] = None,
    visual_report: Optional[dict[str, Any]] = None,
) -> None:
    schema_errors = [
        f"result {index}: {error}"
        for index, result in enumerate(results)
        for error in validate_against_schema(result, "evals/schemas/eval-result.schema.json")
    ]
    if schema_errors:
        raise EvalConfigError("invalid evaluation result protocol: " + "; ".join(schema_errors))
    output.mkdir(parents=True, exist_ok=True)
    failures = [item for item in results if item["status"] != PASS]
    performance = aggregate_performance(results)
    counts = {
        "passed": sum(item["status"] == PASS for item in results),
        "warnings": sum(item["status"] == WARNING for item in results),
        "regression_failures": sum(item["status"] == REGRESSION_FAIL for item in results),
        "hard_failures": sum(item["status"] == HARD_FAIL for item in results),
        "total": len(results),
    }
    summary = {
        "schema_version": 1,
        "selection": selection,
        "counts": counts,
        "status": HARD_FAIL if counts["hard_failures"] else REGRESSION_FAIL if counts["regression_failures"] else WARNING if counts["warnings"] else PASS,
    }
    for name, value in (
        ("summary.json", summary),
        ("capabilities.json", results),
        ("failures.json", failures),
        ("performance.json", performance),
    ):
        (output / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_junit(output / "junit.xml", results)
    if comparison is not None:
        (output / "baseline-comparison.json").write_text(
            json.dumps(comparison, indent=2, sort_keys=True) + "\n", encoding="utf-8",
        )
    write_quality_report(
        output, selection, results, performance, counts, summary["status"], comparison, mutation, visual_report,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_argument_group("selection")
    selection.add_argument("--changed", action="store_true")
    selection.add_argument("--changed-file", action="append", default=[])
    selection.add_argument("--base", default="origin/main")
    selection.add_argument("--capability", action="append", default=[])
    selection.add_argument("--workflow", action="append", default=[])
    selection.add_argument(
        "--kind",
        action="append",
        default=[],
        choices=("skill", "agent", "tool", "workflow"),
        help="select every contract of a capability kind; workflow selects every workflow contract",
    )
    selection.add_argument("--critical", action="store_true")
    selection.add_argument("--all", action="store_true")
    parser.add_argument("--profile", choices=EVAL_PROFILES, default="fast")
    parser.add_argument("--repeat", type=int, help="override stochastic repeat count")
    parser.add_argument("--compare-baseline", nargs="?", const="evals/baselines/v1.0.0.json")
    parser.add_argument("--write-baseline", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "output" / "eval-results")
    parser.add_argument("--python", default=sys.executable, help="Python interpreter for deterministic unittest suites")
    parser.add_argument("--executor-command")
    parser.add_argument("--judge-command")
    parser.add_argument("--require-semantic", action="store_true")
    parser.add_argument(
        "--infrastructure-retries",
        type=int,
        default=2,
        help="retry only recognized transient executor or judge infrastructure failures",
    )
    parser.add_argument("--allow-protected-eval-changes", action="store_true")
    parser.add_argument("--mutation-report", type=Path)
    parser.add_argument("--visual-report", type=Path)
    parser.add_argument("--check-config", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.check_config:
        report = semantic_configuration(args.output)
        print(render_semantic_configuration(report))
        return 0 if report["available"] else 3
    output = args.output if args.output.is_absolute() else ROOT / args.output
    results: list[dict[str, Any]] = []
    try:
        if args.repeat is not None and args.repeat < 1:
            raise EvalConfigError("--repeat must be at least 1")
        if args.infrastructure_retries < 0:
            raise EvalConfigError("--infrastructure-retries must be non-negative")
        config_errors = validate_configuration()
        if config_errors:
            for error in config_errors:
                results.append(result_record("configuration", "contract", "validation", 1, 1, True, HARD_FAIL, 0.0, error))
            write_outputs(output, {"capabilities": [], "workflows": []}, results)
            return 2
        contracts = load_capability_contracts().get("capabilities", {})
        workflows = load_workflows().get("workflows", {})
        thresholds = load_thresholds()
        using_builtin_semantic = not args.executor_command and not args.judge_command
        executor_command = args.executor_command or DEFAULT_EXECUTOR_COMMAND
        judge_command = args.judge_command or DEFAULT_JUDGE_COMMAND
        if using_builtin_semantic:
            semantic_config = semantic_configuration(output)
            if not semantic_config["available"]:
                if args.require_semantic:
                    results.append(result_record(
                        "semantic-runtime", "infrastructure", "configuration", 1, 1, False,
                        HARD_FAIL, 0.0,
                        "infrastructure failure: " + "; ".join(semantic_config["errors"]),
                    ))
                    write_outputs(output, {"capabilities": [], "workflows": []}, results)
                    return 2
                executor_command = None
                judge_command = None
        profile = canonical_profile(args.profile)
        repeat = args.repeat
        if repeat is None:
            repeat = default_repeat_for_profile(profile, thresholds["defaults"])

        changed_files = list(args.changed_file)
        if args.changed:
            changed_files.extend(git_changed_files(args.base))
        impact = select_impacted(changed_files) if changed_files else None

        selected_capabilities = list(args.capability)
        selected_workflows = list(args.workflow)
        selected_capabilities.extend(
            select_capabilities_by_kind(
                contracts,
                [kind for kind in args.kind if kind != "workflow"],
            )
        )
        if "workflow" in args.kind:
            selected_workflows.extend(workflows)
        if impact:
            selected_capabilities.extend(impact["changed_capabilities"])
            selected_capabilities.extend(impact["direct_dependents"])
            selected_capabilities.extend(impact["critical_transitive_dependents"])
            selected_workflows.extend(impact["workflows"])
        if args.all:
            selected_capabilities.extend(contracts)
            selected_workflows.extend(workflows)
        if args.critical or not (selected_capabilities or selected_workflows or impact):
            selected_capabilities.extend(
                identifier for identifier, contract in contracts.items()
                if contract.get("criticality") == "critical"
            )
            selected_workflows.extend(
                identifier for identifier, workflow in workflows.items()
                if workflow.get("criticality") == "critical"
            )
        selected_capabilities = stable_unique(selected_capabilities)
        selected_workflows = stable_unique(selected_workflows)
        unknown_capabilities = sorted(set(selected_capabilities) - set(contracts))
        unknown_workflows = sorted(set(selected_workflows) - set(workflows))
        if unknown_capabilities or unknown_workflows:
            raise EvalConfigError(
                f"unknown selection capabilities={unknown_capabilities} workflows={unknown_workflows}"
            )
        selection_summary = {
            "capabilities": selected_capabilities,
            "workflows": selected_workflows,
            "changed_files": changed_files,
            "impact": impact,
            "profile": profile,
            "branch": current_branch(),
        }
        if impact and impact["protected_changes"] and not args.allow_protected_eval_changes:
            results.append(result_record(
                "evaluation-governance", "contract", "protected-change", 1, 1, True,
                HARD_FAIL, 0.0,
                "protected golden expectations or critical thresholds changed without --allow-protected-eval-changes: "
                + ", ".join(impact["protected_changes"]),
            ))
            write_outputs(output, selection_summary, results)
            return 2
        if impact and impact["uncovered_changed_capabilities"]:
            results.append(result_record(
                "evaluation-governance", "contract", "coverage", 1, 1, True,
                HARD_FAIL, 0.0,
                "changed canonical capability lacks an evaluation contract: "
                + ", ".join(impact["uncovered_changed_capabilities"]),
            ))
            write_outputs(output, selection_summary, results)
            return 2

        subjects: list[tuple[str, str, dict[str, Any]]] = [
            (identifier, contract.get("kind", "capability"), contract)
            for identifier in selected_capabilities
            for contract in [contracts[identifier]]
        ] + [
            (identifier, "workflow", workflow)
            for identifier in selected_workflows
            for workflow in [workflows[identifier]]
        ]
        executed_modules: dict[str, dict[str, Any]] = {}
        for identifier, subject_kind, contract in subjects:
            for scenario in contract.get("scenarios", []):
                kind = scenario["execution"]["kind"]
                if kind == "source-contract":
                    results.append(run_source_contract(identifier, subject_kind, contract, scenario))
                elif kind in {"unittest", "command"}:
                    if kind == "unittest":
                        results.append(run_unittest_scenario(
                            identifier,
                            subject_kind,
                            scenario,
                            args.python,
                            executed_modules,
                        ))
                    else:
                        results.append(run_deterministic(identifier, subject_kind, scenario, args.python))
                elif kind == "external":
                    repeated_results = []
                    for run_number in range(1, repeat + 1):
                        repeated_results.append(run_external(
                            identifier,
                            subject_kind,
                            contract,
                            scenario,
                            run_number,
                            executor_command,
                            judge_command,
                            args.require_semantic,
                            thresholds,
                            args.infrastructure_retries,
                            [
                                {
                                    "scenario": item["scenario"],
                                    "status": item["status"],
                                    "reason": item.get("reason"),
                                    "score": item.get("score"),
                                }
                                for item in results
                                if item["capability"] == identifier and item["deterministic"]
                            ],
                        ))
                    results.extend(repeated_results)
                    if "consistency" in contract.get("applicable_metrics", []):
                        consistency_result = evaluate_repeat_consistency(
                            identifier, subject_kind, scenario, repeated_results, thresholds,
                        )
                        if consistency_result:
                            results.append(consistency_result)

        if args.all:
            discovered_modules = [
                path.relative_to(ROOT).with_suffix("").as_posix().replace("/", ".")
                for path in sorted((ROOT / "evals").glob("**/test_*.py"))
            ]
            remaining_modules = [module for module in discovered_modules if module not in executed_modules]
            if remaining_modules:
                results.append(run_deterministic(
                    "repository",
                    "suite",
                    {
                        "id": "remaining-behavior-tests",
                        "level": 3,
                        "deterministic": True,
                        "execution": {"kind": "unittest", "modules": remaining_modules},
                    },
                    args.python,
                ))

        performance = aggregate_performance(results)
        comparison = None
        if args.compare_baseline:
            baseline_path = Path(args.compare_baseline)
            if not baseline_path.is_absolute():
                baseline_path = ROOT / baseline_path
            comparison, baseline_results = compare_performance_to_baseline(
                performance, load_json(baseline_path), thresholds,
            )
            results.extend(baseline_results)
        if args.write_baseline:
            results.append(result_record(
                "evaluation-baseline", "baseline", "write", 2, 1, True, HARD_FAIL, 0.0,
                "the evaluation runner never promotes last-green state; use tools/evals/promote_baseline.py after an explicitly accepted green main/nightly run",
            ))
        mutation = None
        if args.mutation_report:
            mutation_path = args.mutation_report if args.mutation_report.is_absolute() else ROOT / args.mutation_report
            mutation = load_json(mutation_path)
        visual_report = None
        if args.visual_report:
            visual_path = args.visual_report if args.visual_report.is_absolute() else ROOT / args.visual_report
            visual_report = load_json(visual_path)
            expected_visual_ids = {
                item["id"] for item in load_json(
                    ROOT / "evals/fixtures/visual-regression/manifest.json"
                ).get("states", [])
            }
            observed_visual_ids = {
                item.get("id") for item in visual_report.get("results", [])
                if isinstance(item, dict) and item.get("status") == "PASS"
            }
            if visual_report.get("status") != "PASS" or observed_visual_ids != expected_visual_ids:
                results.append(result_record(
                    "visual-regression", "suite", "representative-states", 3, 1, True,
                    HARD_FAIL, 0.0, "visual regression verification failed",
                ))
        write_outputs(output, selection_summary, results, comparison, mutation, visual_report)
    except (EvalConfigError, OSError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        results.append(result_record("evaluation-runner", "tool", "configuration", 1, 1, True, HARD_FAIL, 0.0, str(exc)))
        write_outputs(output, {"capabilities": [], "workflows": []}, results)
        return 2

    if any(item["status"] == HARD_FAIL for item in results):
        return 2
    if any(item["status"] == REGRESSION_FAIL for item in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
