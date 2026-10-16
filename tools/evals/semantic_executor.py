#!/usr/bin/env python3
"""Production repository-owned semantic executor entry point."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Optional

from semantic_runtime import (
    RuntimeConfigError,
    RuntimeExecutionError,
    runtime_from_environment,
    sanitized_executor_environment,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_SCHEMA = ROOT / "evals" / "schemas" / "codex-executor-output.schema.json"


def _workspace_path(workspace: Path, relative: str, *, label: str) -> Path:
    candidate = Path(relative)
    if candidate.is_absolute():
        raise RuntimeConfigError(f"{label} must be a relative workspace path")
    resolved = (workspace / candidate).resolve()
    try:
        resolved.relative_to(workspace.resolve())
    except ValueError as exc:
        raise RuntimeConfigError(f"{label} escapes the isolated workspace") from exc
    return resolved


def _path_is_writable(relative: str, policy: dict[str, Any]) -> bool:
    normalized = Path(relative).as_posix()
    writable = {Path(str(path)).as_posix() for path in policy.get("writable_artifacts", [])}
    prefixes = tuple(
        Path(str(path)).as_posix().rstrip("/") + "/"
        for path in policy.get("generated_prefixes", [])
    )
    return normalized in writable or normalized.startswith(prefixes)


def _browser_report_passed(report: dict[str, Any]) -> bool:
    status = report.get("status")
    if status in {"PASS", "PARTIAL"}:
        visual = report.get("results", {}).get("VISUAL_QA_PASS", {})
        return visual.get("status", "PASS") == "PASS"
    if status is not None:
        return False
    browser_render = report.get("browser_render", {})
    return browser_render.get("brand_visible") is True


def run_declared_browser_validations(
    request: dict[str, Any],
    workspace: Path,
    output: dict[str, Any],
    *,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> list[dict[str, Any]]:
    """Run trusted fixture-declared browser checks outside the Codex sandbox."""
    scenario = request.get("scenario_input", {})
    inputs = scenario.get("inputs", {})
    commands = [
        (str(name), value)
        for name, value in inputs.items()
        if str(name).endswith("browser_command") and isinstance(value, str) and value.strip()
    ]
    if not commands:
        return []
    declared_sources = {Path(str(path)).as_posix() for path in scenario.get("source_artifacts", [])}
    policy = scenario.get("workspace_policy", {})
    generated_result = output.get("generated_result")
    evidence = output.get("evidence")
    if not isinstance(generated_result, dict) or not isinstance(evidence, list):
        raise RuntimeExecutionError("executor output cannot receive trusted browser validation")
    validations: list[dict[str, Any]] = []
    existing_evidence_ids = {
        str(item.get("id")) for item in evidence if isinstance(item, dict) and item.get("id")
    }
    for index, (input_name, raw_command) in enumerate(commands, start=1):
        command = shlex.split(raw_command)
        if len(command) < 2 or command[0] != "node":
            raise RuntimeConfigError(f"{input_name} must invoke a declared Node.js script")
        script_relative = Path(command[1]).as_posix()
        if script_relative not in declared_sources:
            raise RuntimeConfigError(f"{input_name} script is not a declared source artifact")
        script_path = _workspace_path(workspace, script_relative, label=f"{input_name} script")
        if not script_path.is_file() or script_path.suffix not in {".js", ".mjs"}:
            raise RuntimeConfigError(f"{input_name} script is unavailable")
        try:
            output_index = command.index("--output") + 1
            output_relative = Path(command[output_index]).as_posix()
        except (ValueError, IndexError) as exc:
            raise RuntimeConfigError(f"{input_name} must declare --output") from exc
        if not _path_is_writable(output_relative, policy):
            raise RuntimeConfigError(f"{input_name} output is outside the workspace policy")
        report_path = _workspace_path(workspace, output_relative, label=f"{input_name} output")
        try:
            completed = runner(
                command,
                cwd=workspace,
                env=sanitized_executor_environment(os.environ),
                capture_output=True,
                text=True,
                timeout=180,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise RuntimeExecutionError(
                f"trusted browser validation could not run: {exc}", transient=True,
            ) from exc
        if completed.returncode:
            detail = (completed.stderr or completed.stdout or "browser validation failed")[-2000:]
            raise RuntimeExecutionError(
                f"trusted browser validation exited {completed.returncode}: {detail}",
                transient=True,
            )
        if not report_path.is_file():
            raise RuntimeExecutionError(
                f"trusted browser validation did not write {output_relative}"
            )
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeExecutionError(
                f"trusted browser validation report is invalid: {output_relative}"
            ) from exc
        if not isinstance(report, dict) or not _browser_report_passed(report):
            detail = json.dumps(report, sort_keys=True)[-2000:]
            raise RuntimeExecutionError(
                f"trusted browser validation reported failure: {output_relative}: {detail}"
            )
        evidence_id = f"E-TRUSTED-BROWSER-QA-{index}"
        while evidence_id in existing_evidence_ids:
            index += 1
            evidence_id = f"E-TRUSTED-BROWSER-QA-{index}"
        existing_evidence_ids.add(evidence_id)
        line_count = max(1, len(report_path.read_text(encoding="utf-8").splitlines()))
        evidence.append({
            "id": evidence_id,
            "source": output_relative,
            "locator": f"{output_relative}:1-{line_count}",
            "claim": "Trusted runner browser validation completed successfully.",
        })
        validations.append({
            "input": input_name,
            "command": raw_command,
            "report": output_relative,
            "status": "PASS",
        })
    return validations


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-config", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        runtime = runtime_from_environment(output_schema=OUTPUT_SCHEMA)
        if args.check_config:
            checked = runtime.check_config(require_auth=True)
            print(json.dumps({"status": "available", **checked}, sort_keys=True))
            return 0
        request = json.load(sys.stdin)
        if "expected" in request or "golden" in request:
            raise RuntimeConfigError("executor input must not contain Golden expectations")
        result = runtime.execute(request, Path.cwd())
        output = dict(result.output)
        run_declared_browser_validations(request, Path.cwd(), output)
        performance = output.setdefault("performance", {})
        performance.update({
            "llm_calls": 1,
            "input_tokens": result.input_tokens,
            "output_tokens": result.output_tokens,
            "model": result.model,
            "runtime": result.runtime,
            "duration_seconds": round(result.duration_seconds, 6),
        })
        performance = {key: value for key, value in performance.items() if value is not None}
        output["performance"] = performance
        if result.total_tokens is not None:
            output["tokens"] = result.total_tokens
        print(json.dumps({
            "event": "semantic_executor.completed",
            "runtime": result.runtime,
            "model": result.model,
            "duration_seconds": round(result.duration_seconds, 6),
            "input_tokens": result.input_tokens,
            "output_tokens": result.output_tokens,
            "total_tokens": result.total_tokens,
        }, sort_keys=True), file=sys.stderr)
        print(json.dumps(output, sort_keys=True))
        return 0
    except RuntimeConfigError as exc:
        print(f"configuration error: {exc}", file=sys.stderr)
        return 78
    except RuntimeExecutionError as exc:
        print(f"runtime failure: {exc}", file=sys.stderr)
        return 75 if exc.transient else 1
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(f"protocol failure: {exc}", file=sys.stderr)
        return 76


if __name__ == "__main__":
    raise SystemExit(main())
