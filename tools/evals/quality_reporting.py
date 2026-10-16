"""Build the engineering quality dashboard from canonical evaluation outputs."""

from __future__ import annotations

import html
import json
import shlex
import shutil
import statistics
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from eval_common import ROOT, load_capability_contracts, load_thresholds, load_workflows


PASS = "PASS"
WARNING = "WARNING"
REGRESSION_FAIL = "REGRESSION_FAIL"
HARD_FAIL = "HARD_FAIL"
NOT_AVAILABLE = "not_available"

QUALITY_REGRESSION = "QUALITY_REGRESSION"
PERFORMANCE_REGRESSION = "PERFORMANCE_REGRESSION"
TOKEN_REGRESSION = "TOKEN_REGRESSION"
STABILITY_REGRESSION = "STABILITY_REGRESSION"
VISUAL_REGRESSION = "VISUAL_REGRESSION"
CONTRACT_REGRESSION = "CONTRACT_REGRESSION"
INFRASTRUCTURE_FAILURE = "INFRASTRUCTURE_FAILURE"
PROTOCOL_FAILURE = "PROTOCOL_FAILURE"
DETERMINISTIC_FAILURE = "DETERMINISTIC_FAILURE"

STATUS_RANK = {PASS: 0, WARNING: 1, REGRESSION_FAIL: 2, HARD_FAIL: 3}
QUALITY_METRICS = ("correctness", "completeness", "evidence_grounding")


def _numeric(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _mean(values: list[Any]) -> float | str:
    numeric = [float(value) for value in values if _numeric(value)]
    return statistics.mean(numeric) if numeric else NOT_AVAILABLE


def _sum_if_complete(values: list[Any]) -> float | str:
    if not values or any(not _numeric(value) for value in values):
        return NOT_AVAILABLE
    return sum(float(value) for value in values)


def _worst_status(values: list[str]) -> str:
    return max(values or [PASS], key=lambda value: STATUS_RANK.get(value, 0))


def _percent_delta(baseline: Any, current: Any) -> float | str:
    if not _numeric(baseline) or not _numeric(current) or float(baseline) == 0:
        return NOT_AVAILABLE
    return ((float(current) - float(baseline)) / float(baseline)) * 100


def _metric_delta(baseline: Any, current: Any, percentage: bool = False) -> float | str:
    if not _numeric(baseline) or not _numeric(current):
        return NOT_AVAILABLE
    return _percent_delta(baseline, current) if percentage else float(current) - float(baseline)


def _build_name(profile: str) -> str:
    return {
        "fast": "Pull request",
        "standard": "Main validation",
        "full": "Nightly",
        "deep": "Weekly deep",
    }.get(profile, profile or "Evaluation")


def _version() -> str:
    value = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    return f"v{value}"


def _subject_paths() -> dict[str, str]:
    paths = {
        identifier: str(contract.get("path", ""))
        for identifier, contract in load_capability_contracts().get("capabilities", {}).items()
    }
    paths.update({identifier: "evals/workflows/contracts.json" for identifier in load_workflows().get("workflows", {})})
    return paths


def _last_changed(path: str) -> str:
    if not path:
        return NOT_AVAILABLE
    completed = subprocess.run(
        ["git", "log", "-1", "--format=%H", "--", path],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    value = completed.stdout.strip()
    return value if completed.returncode == 0 and value else NOT_AVAILABLE


def _impact_label(subject: str, kind: str, impact: dict[str, Any]) -> str:
    if subject in impact.get("changed_capabilities", []):
        return "CHANGED"
    if subject in impact.get("direct_dependents", []):
        return "DIRECT_DEPENDENT"
    if subject in impact.get("critical_transitive_dependents", []):
        return "CRITICAL_TRANSITIVE"
    if kind == "workflow" and subject in impact.get("workflows", []):
        return "AFFECTED_WORKFLOW"
    return "EVALUATED"


def _portfolio_metrics(performance: list[dict[str, Any]]) -> dict[str, Any]:
    metrics: dict[str, Any] = {
        "pass_rate": _mean([item.get("pass_rate") for item in performance]),
        "runtime_seconds": sum(float(item.get("duration_mean_seconds", 0)) for item in performance),
        "tokens": _sum_if_complete([item.get("tokens_mean") for item in performance]),
    }
    for metric in QUALITY_METRICS:
        metrics[metric] = _mean([
            item.get("metrics_mean", {}).get(metric)
            for item in performance
        ])
    return metrics


def _comparison_trend(
    comparison: dict[str, Any] | None,
    performance: list[dict[str, Any]],
    baseline: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    current_metrics = _portfolio_metrics(performance)
    rows = comparison.get("rows", []) if isinstance(comparison, dict) else []
    current_by_scenario = {str(item.get("scenario")): item for item in performance}
    baseline_scenarios = (
        baseline.get("scenarios", {})
        if isinstance(baseline, dict) and baseline.get("status") == "accepted"
        else {}
    )
    output: list[dict[str, Any]] = []
    for metric in (*QUALITY_METRICS, "pass_rate", "runtime_seconds", "tokens"):
        comparable = [row for row in rows if row.get("metric") == metric]
        baseline_values = []
        current_values = []
        matched_scenarios = 0
        for scenario, current_row in current_by_scenario.items():
            baseline_row = baseline_scenarios.get(scenario)
            if not isinstance(baseline_row, dict):
                continue
            matched_scenarios += 1
            if metric in QUALITY_METRICS:
                baseline_value = baseline_row.get("metrics_mean", {}).get(metric)
                current_value = current_row.get("metrics_mean", {}).get(metric)
            elif metric == "runtime_seconds":
                baseline_value = baseline_row.get("duration_mean_seconds")
                current_value = current_row.get("duration_mean_seconds")
            elif metric == "tokens":
                baseline_value = baseline_row.get("tokens_mean")
                current_value = current_row.get("tokens_mean")
            else:
                baseline_value = baseline_row.get("pass_rate")
                current_value = current_row.get("pass_rate")
            if _numeric(baseline_value) and _numeric(current_value):
                baseline_values.append(baseline_value)
                current_values.append(current_value)
        if metric in {"runtime_seconds", "tokens"}:
            baseline_value = _sum_if_complete(baseline_values)
            current = _sum_if_complete(current_values)
            percentage = True
        else:
            baseline_value = _mean(baseline_values)
            current = _mean(current_values)
            percentage = False
        if not baseline_values:
            current = current_metrics.get(metric, NOT_AVAILABLE)
        current_available = sum(
            _numeric(
                item.get("metrics_mean", {}).get(metric)
                if metric in QUALITY_METRICS else
                item.get("duration_mean_seconds")
                if metric == "runtime_seconds" else
                item.get("tokens_mean")
                if metric == "tokens" else
                item.get("pass_rate")
            )
            for item in performance
        )
        denominator = matched_scenarios if baseline_scenarios else len(performance)
        output.append({
            "metric": metric,
            "baseline": baseline_value,
            "current": current,
            "delta": _metric_delta(baseline_value, current, percentage),
            "delta_unit": "percent" if percentage else "absolute",
            "status": (
                _worst_status([str(row.get("status", PASS)) for row in comparable])
                if comparable else PASS if baseline_values else "NOT_AVAILABLE"
            ),
            "comparable_scenarios": len(baseline_values),
            "coverage": f"{len(baseline_values)}/{matched_scenarios}" if baseline_scenarios else f"{current_available}/{denominator}",
            "partial": bool(denominator and (len(baseline_values) if baseline_scenarios else current_available) < denominator),
        })
    return output


def _comparison_delta(
    performance: list[dict[str, Any]],
    baseline: dict[str, Any] | None,
    subject: str,
    metric: str,
) -> tuple[float | str, str]:
    baseline_scenarios = (
        baseline.get("scenarios", {})
        if isinstance(baseline, dict) and baseline.get("status") == "accepted"
        else {}
    )
    baseline_values = []
    current_values = []
    matched = 0
    field = "duration_mean_seconds" if metric == "runtime_seconds" else "tokens_mean"
    for current_row in performance:
        scenario = str(current_row.get("scenario", ""))
        if not scenario.startswith(f"{subject}:"):
            continue
        baseline_row = baseline_scenarios.get(scenario)
        if not isinstance(baseline_row, dict):
            continue
        matched += 1
        baseline_value = baseline_row.get(field)
        current_value = current_row.get(field)
        if _numeric(baseline_value) and _numeric(current_value):
            baseline_values.append(baseline_value)
            current_values.append(current_value)
    return (
        _percent_delta(sum(baseline_values), sum(current_values)) if baseline_values else NOT_AVAILABLE,
        f"{len(baseline_values)}/{matched}",
    )


def _capability_rows(
    results: list[dict[str, Any]],
    performance: list[dict[str, Any]],
    baseline: dict[str, Any] | None,
    impact: dict[str, Any],
) -> list[dict[str, Any]]:
    result_groups: dict[str, list[dict[str, Any]]] = {}
    kinds: dict[str, str] = {}
    for item in results:
        if item.get("subject_kind") == "baseline":
            continue
        subject = str(item.get("capability"))
        result_groups.setdefault(subject, []).append(item)
        kinds.setdefault(subject, str(item.get("subject_kind", "capability")))
    performance_groups: dict[str, list[dict[str, Any]]] = {}
    for item in performance:
        subject = str(item.get("scenario", "")).split(":", 1)[0]
        performance_groups.setdefault(subject, []).append(item)
    paths = _subject_paths()
    output = []
    for subject in sorted(result_groups):
        items = result_groups[subject]
        perf = performance_groups.get(subject, [])
        metrics = {
            metric: _mean([row.get("metrics_mean", {}).get(metric) for row in perf])
            for metric in QUALITY_METRICS
        }
        kind = kinds[subject]
        runtime_delta, runtime_coverage = _comparison_delta(perf, baseline, subject, "runtime_seconds")
        token_delta, token_coverage = _comparison_delta(perf, baseline, subject, "tokens")
        output.append({
            "capability": subject,
            "kind": kind,
            "status": _worst_status([str(item.get("status", PASS)) for item in items]),
            "correctness": metrics["correctness"],
            "completeness": metrics["completeness"],
            "evidence": metrics["evidence_grounding"],
            "stability": _mean([row.get("pass_rate") for row in perf]),
            "runtime_delta_percent": runtime_delta,
            "runtime_coverage": runtime_coverage,
            "token_delta_percent": token_delta,
            "token_coverage": token_coverage,
            "last_changed": _last_changed(paths.get(subject, "")),
            "impact": _impact_label(subject, kind, impact),
        })
    return output


def _inventory(capabilities: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    names = {"skill": "skills", "agent": "agents", "tool": "tools", "workflow": "workflows"}
    output = {name: {"passed": 0, "total": 0} for name in names.values()}
    for item in capabilities:
        name = names.get(str(item.get("kind")))
        if not name:
            continue
        output[name]["total"] += 1
        output[name]["passed"] += item.get("status") == PASS
    return output


def _classification_for_metric(metric: str) -> str:
    if metric == "runtime_seconds":
        return PERFORMANCE_REGRESSION
    if metric == "tokens":
        return TOKEN_REGRESSION
    if metric in {"pass_rate", "consistency", "score_variance", "metrics_variance"}:
        return STABILITY_REGRESSION
    return QUALITY_REGRESSION


def _classification_for_result(item: dict[str, Any]) -> str:
    explicit = item.get("failure_type")
    if explicit in {QUALITY_REGRESSION, INFRASTRUCTURE_FAILURE, PROTOCOL_FAILURE, DETERMINISTIC_FAILURE}:
        return str(explicit)
    text = " ".join(str(item.get(name, "")) for name in ("capability", "scenario", "reason")).lower()
    if any(marker in text for marker in (
        "infrastructure", "semantic executor unavailable", "semantic judge unavailable",
        "service unavailable", "rate limit", "connection reset", "timed out",
    )):
        return INFRASTRUCTURE_FAILURE
    if "visual" in text:
        return VISUAL_REGRESSION
    if "token" in text:
        return TOKEN_REGRESSION
    if "runtime" in text or "duration" in text:
        return PERFORMANCE_REGRESSION
    if any(marker in text for marker in ("pass rate", "consistency", "variance", "flaky")):
        return STABILITY_REGRESSION
    if item.get("subject_kind") == "contract" or "contract" in str(item.get("scenario", "")):
        return CONTRACT_REGRESSION
    if item.get("capability") in {"mutation-testing", "evaluation-governance"}:
        return CONTRACT_REGRESSION
    return QUALITY_REGRESSION


def _candidate_commits(capability: str, impact: dict[str, Any]) -> list[str]:
    capability_commits = impact.get("capability_commits", {})
    if isinstance(capability_commits, dict) and isinstance(capability_commits.get(capability), list):
        return [str(value) for value in capability_commits[capability]]
    if capability in impact.get("changed_capabilities", []):
        return [str(item.get("commit")) for item in impact.get("commits", []) if item.get("commit")]
    return []


def _classified_regressions(
    results: list[dict[str, Any]],
    comparison: dict[str, Any] | None,
    mutation: dict[str, Any] | None,
    visual_failures: list[dict[str, Any]],
    impact: dict[str, Any],
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    metric_policies = load_thresholds().get("metrics", {})
    subject_kinds = {
        str(item.get("capability")): str(item.get("subject_kind", "capability"))
        for item in results
        if item.get("subject_kind") != "baseline"
    }
    for item in results:
        if item.get("status") == PASS or item.get("subject_kind") == "baseline":
            continue
        capability = str(item.get("capability", "unknown"))
        expected: Any = item.get("threshold", NOT_AVAILABLE)
        actual: Any = item.get("score") if _numeric(item.get("score")) else item.get("status")
        delta: Any = (
            float(item["score"]) - float(item["threshold"])
            if _numeric(item.get("score")) and _numeric(item.get("threshold"))
            else NOT_AVAILABLE
        )
        if expected is None:
            metrics = {
                str(name): float(value)
                for name, value in item.get("metrics", {}).items()
                if _numeric(value)
            }
            minimums = {
                name: float(metric_policies[name]["minimum"])
                for name in metrics
                if _numeric(metric_policies.get(name, {}).get("minimum"))
            }
            expected = {"status": PASS, "metric_minimums": minimums}
            actual = {
                "status": item.get("status"),
                "score": item.get("score", NOT_AVAILABLE),
                "metrics": metrics,
            }
            delta = {
                "status": "regressed",
                "metrics": {
                    name: round(metrics[name] - minimum, 6)
                    for name, minimum in minimums.items()
                },
            }
        findings.append({
            "classification": _classification_for_result(item),
            "status": item.get("status"),
            "capability": capability,
            "scenario": item.get("scenario"),
            "metric": None,
            "reason": item.get("reason") or item.get("status"),
            "baseline": expected,
            "current": actual,
            "delta": delta,
            "candidate_commits": _candidate_commits(capability, impact),
            "subject_kind": item.get("subject_kind"),
        })
    for row in (comparison or {}).get("rows", []):
        if row.get("status") == PASS:
            continue
        scenario = str(row.get("scenario", "unknown"))
        capability = scenario.split(":", 1)[0]
        findings.append({
            "classification": _classification_for_metric(str(row.get("metric"))),
            "status": row.get("status"),
            "capability": capability,
            "scenario": scenario.split(":", 1)[-1],
            "metric": row.get("metric"),
            "reason": f"{row.get('metric')} changed relative to the accepted baseline",
            "baseline": row.get("baseline", NOT_AVAILABLE),
            "current": row.get("current", NOT_AVAILABLE),
            "delta": row.get("delta", NOT_AVAILABLE),
            "candidate_commits": _candidate_commits(capability, impact),
            "subject_kind": subject_kinds.get(capability, "capability"),
        })
    for item in visual_failures:
        findings.append({
            "classification": VISUAL_REGRESSION,
            "status": HARD_FAIL,
            "capability": "visual-regression",
            "scenario": item.get("scenario"),
            "metric": "visual",
            "reason": "visual checks failed",
            "baseline": "accepted screenshot",
            "current": item.get("checks", {}),
            "delta": item.get("pixel_difference_ratio", NOT_AVAILABLE),
            "candidate_commits": [str(entry.get("commit")) for entry in impact.get("commits", []) if entry.get("commit")],
            "subject_kind": "suite",
        })
    for item in (mutation or {}).get("results", []):
        if item.get("status") == "DETECTED":
            continue
        mutation_error = item.get("status") == "ERROR"
        findings.append({
            "classification": INFRASTRUCTURE_FAILURE if mutation_error else CONTRACT_REGRESSION,
            "status": HARD_FAIL if item.get("critical") else REGRESSION_FAIL,
            "capability": "mutation-testing",
            "scenario": item.get("id"),
            "metric": "mutation_detection",
            "reason": "mutation execution failed" if mutation_error else "harmful mutation was not detected",
            "baseline": item.get("expected_failure", "detected"),
            "current": item.get("status"),
            "delta": NOT_AVAILABLE,
            "candidate_commits": [str(entry.get("commit")) for entry in impact.get("commits", []) if entry.get("commit")],
            "subject_kind": "suite",
        })
    unique: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()
    for item in findings:
        key = (item["classification"], item["capability"], item["scenario"], item["metric"])
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return sorted(
        unique,
        key=lambda item: (-STATUS_RANK.get(str(item.get("status")), 0), str(item.get("capability")), str(item.get("scenario"))),
    )


def _reproduction_command(capability: str, kind: str, profile: str) -> str:
    if capability == "visual-regression":
        return (
            "npm install --prefix output/visual-deps --no-save --no-package-lock "
            "playwright@1.62.1 pixelmatch@7.1.0 pngjs@7.0.0 && "
            "output/visual-deps/node_modules/.bin/playwright install chromium && "
            "node tools/evals/capture_visual_baselines.mjs "
            "--node-modules output/visual-deps/node_modules "
            "--output output/visual-screenshots --report output/visual-report.json"
        )
    if capability == "mutation-testing":
        return "python3 tools/evals/run_mutations.py --output output/mutation-report.json"
    if capability == "ci-aggregation":
        return (
            "python3 tools/evals/aggregate_results.py --input-root output/eval-shards "
            "--output output/repro-aggregate --profile full --branch main"
        )
    selector = "--workflow" if kind == "workflow" else "--capability"
    repeat = " --repeat 3" if profile in {"full", "deep"} else ""
    safe = "".join(character if character.isalnum() or character in "-_" else "-" for character in capability)
    return (
        f"python3 tools/evals/run_evals.py {selector} {shlex.quote(capability)} "
        f"--profile {shlex.quote(profile)}{repeat} --output {shlex.quote(f'output/repro-{safe}')}"
    )


def _diagnostics(
    findings: list[dict[str, Any]],
    impact: dict[str, Any],
    profile: str,
) -> list[dict[str, Any]]:
    changed = [str(value) for value in impact.get("changed_capabilities", [])]
    direct = set(impact.get("direct_dependents", []))
    transitive = set(impact.get("critical_transitive_dependents", []))
    workflows = set(impact.get("workflows", []))
    output = []
    for item in findings:
        capability = str(item["capability"])
        if capability in changed:
            impacted_by = [capability]
        elif capability in direct or capability in transitive or capability in workflows:
            impacted_by = changed
        else:
            impacted_by = []
        classification = item["classification"]
        artifact = (
            "visual-report.json" if classification == VISUAL_REGRESSION
            else "mutation-report.json" if capability == "mutation-testing"
            else "baseline-comparison.json" if item.get("subject_kind") == "baseline"
            else "failures.json"
        )
        output.append({
            "scenario": item.get("scenario"),
            "capability": capability,
            "classification": classification,
            "expected": item.get("baseline", NOT_AVAILABLE),
            "actual": item.get("current", NOT_AVAILABLE),
            "delta": item.get("delta", NOT_AVAILABLE),
            "relevant_artifact": artifact,
            "likely_impacted_by": impacted_by,
            "candidate_commits": item.get("candidate_commits", []),
            "local_reproduction_command": _reproduction_command(
                capability, str(item.get("subject_kind", "capability")), profile,
            ),
        })
    return output


def _visual_failures(
    output: Path,
    visual_report: dict[str, Any] | None,
    evidence_dir: Path | None,
) -> list[dict[str, Any]]:
    failures = []
    for item in (visual_report or {}).get("results", []):
        if item.get("status") == PASS:
            continue
        source_value = str(item.get("evidence_screenshot") or item.get("screenshot", ""))
        filename = Path(source_value).name
        copied = False
        if filename:
            candidates = []
            if evidence_dir:
                candidates.append(evidence_dir / filename)
            repository_candidate = (ROOT / source_value).resolve()
            if repository_candidate == ROOT.resolve() or ROOT.resolve() in repository_candidate.parents:
                candidates.append(repository_candidate)
            for candidate in candidates:
                if candidate.is_file():
                    destination = output / "screenshots" / filename
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(candidate, destination)
                    copied = True
                    break
        failures.append({
            "scenario": item.get("id"),
            "artifact": item.get("artifact") or str(item.get("id", "unknown")).split("-", 1)[0],
            "status": item.get("status"),
            "checks": item.get("checks", {}),
            "pixel_difference_ratio": item.get("pixel_difference_ratio", NOT_AVAILABLE),
            "thumbnail": f"screenshots/{filename}" if copied else NOT_AVAILABLE,
            "evidence": f"screenshots/{filename}" if copied else source_value or NOT_AVAILABLE,
        })
    return failures


def _mutation_measure(mutation: dict[str, Any] | None) -> dict[str, Any]:
    result_rows = (mutation or {}).get("results", [])
    evaluated = [item for item in result_rows if item.get("status") in {"DETECTED", "SURVIVED"}]
    detected = sum(item.get("status") == "DETECTED" for item in evaluated)
    return {
        "score": detected / len(evaluated) if evaluated else NOT_AVAILABLE,
        "evaluated_harmful_mutations": len(evaluated),
        "critical_survivors": [
            item.get("id") for item in evaluated
            if item.get("critical") and item.get("status") == "SURVIVED"
        ],
        "infrastructure_errors": [
            item.get("id") for item in result_rows if item.get("status") == "ERROR"
        ],
    }


def _mutation_view(
    mutation: dict[str, Any] | None,
    history: list[dict[str, Any]],
    generated_at: str,
    current_commit: str,
) -> dict[str, Any]:
    result_rows = (mutation or {}).get("results", [])
    measure = _mutation_measure(mutation)
    rows = [{
        "mutation": item.get("id"),
        "expected_detection": item.get("expected_failure", "detector failure"),
        "actual_detection": item.get("status"),
        "status": PASS if item.get("status") == "DETECTED" else "FAIL",
        "critical": bool(item.get("critical")),
    } for item in result_rows]
    trend = []
    for summary in history:
        prior = summary.get("mutation")
        prior_measure = _mutation_measure(prior if isinstance(prior, dict) else None)
        if _numeric(prior_measure["score"]):
            trend.append({
                "generated_at": summary.get("generated_at"),
                "commit": summary.get("current_commit", NOT_AVAILABLE),
                "score": prior_measure["score"],
            })
    if isinstance(mutation, dict) and _numeric(measure["score"]):
        trend.append({"generated_at": generated_at, "commit": current_commit, "score": measure["score"]})
    return {
        **measure,
        "rows": rows,
        "trend": trend,
    }


def _history_point(summary: dict[str, Any]) -> dict[str, Any]:
    metrics = _portfolio_metrics(summary.get("performance", []))
    return {
        "generated_at": summary.get("generated_at"),
        "commit": summary.get("current_commit", NOT_AVAILABLE),
        "overall": summary.get("overall", NOT_AVAILABLE),
        **metrics,
        "mutation_score": _mutation_measure(
            summary.get("mutation") if isinstance(summary.get("mutation"), dict) else None
        )["score"],
    }


def _history_view(
    history: list[dict[str, Any]],
    current: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    now = datetime.now(timezone.utc)
    summaries = [*history, current]
    unique: dict[tuple[Any, Any], dict[str, Any]] = {}
    for summary in summaries:
        key = (summary.get("generated_at"), summary.get("current_commit"))
        unique[key] = summary
    dated = []
    for summary in unique.values():
        try:
            generated = datetime.fromisoformat(str(summary["generated_at"]).replace("Z", "+00:00"))
            if generated.tzinfo is None:
                generated = generated.replace(tzinfo=timezone.utc)
        except (KeyError, TypeError, ValueError):
            continue
        dated.append((generated, summary))
    dated.sort(key=lambda item: item[0])
    return {
        "7_day": [_history_point(summary) for generated, summary in dated if generated >= now - timedelta(days=7)],
        "30_day": [_history_point(summary) for generated, summary in dated if generated >= now - timedelta(days=30)],
    }


def _scenario_runs(results: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in results:
        if item.get("subject_kind") == "baseline":
            continue
        key = f"{item.get('capability')}:{item.get('scenario')}"
        grouped.setdefault(key, []).append({
            "run": int(item.get("run", 1)),
            "status": item.get("status"),
            "score": item.get("score"),
        })
    return {
        scenario: sorted(rows, key=lambda row: row["run"])
        for scenario, rows in sorted(grouped.items())
    }


def _flakiness(
    history: list[dict[str, Any]],
    current: dict[str, Any],
    current_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    summaries = sorted(
        [*history, current],
        key=lambda item: str(item.get("generated_at", "")),
    )
    current_runs = _scenario_runs(current_results)
    grouped: dict[str, list[dict[str, Any]]] = {}
    for summary in summaries:
        for item in summary.get("performance", []):
            grouped.setdefault(str(item.get("scenario")), []).append(item)
    output = []
    for scenario, rows in grouped.items():
        runs = [int(row.get("runs", 1)) for row in rows]
        pass_rates = [float(row.get("pass_rate", 0)) for row in rows]
        total_runs = sum(runs)
        last_n_pass_rate = (
            sum(rate * run_count for rate, run_count in zip(pass_rates, runs)) / total_runs
            if total_runs else 0.0
        )
        variances = [
            float(value)
            for row in rows
            for value in [row.get("score_variance")]
            if _numeric(value)
        ] + [
            float(value)
            for row in rows
            for value in row.get("metrics_variance", {}).values()
            if _numeric(value)
        ]
        worst_scores = [float(row["score_worst"]) for row in rows if _numeric(row.get("score_worst"))]
        ordered_runs = []
        for summary in summaries:
            scenario_runs = summary.get("scenario_runs", {})
            if isinstance(scenario_runs, dict):
                ordered_runs.extend(scenario_runs.get(scenario, []))
        ordered_runs.extend(current_runs.get(scenario, []))
        consecutive = 0
        for run in reversed(ordered_runs):
            if run.get("status") not in {REGRESSION_FAIL, HARD_FAIL}:
                break
            consecutive += 1
        if len(rows) > 1 or any(run > 1 for run in runs):
            output.append({
                "scenario": scenario,
                "capability": scenario.split(":", 1)[0],
                "observed_runs": total_runs,
                "last_n_pass_rate": last_n_pass_rate,
                "variance": max(variances or [statistics.pvariance(pass_rates) if len(pass_rates) > 1 else 0.0]),
                "worst_score": min(worst_scores) if worst_scores else NOT_AVAILABLE,
                "consecutive_failures": consecutive,
                "consecutive_failure_basis": "ordered_evaluation_runs",
                "ordered_run_coverage": len(ordered_runs),
            })
    return sorted(output, key=lambda item: (item["last_n_pass_rate"], -item["consecutive_failures"], item["scenario"]))


def build_quality_summary(
    base: dict[str, Any],
    results: list[dict[str, Any]],
    performance: list[dict[str, Any]],
    comparison: dict[str, Any] | None,
    baseline: dict[str, Any] | None,
    mutation: dict[str, Any] | None,
    visual_report: dict[str, Any] | None,
    history: list[dict[str, Any]],
    output: Path,
    visual_evidence_dir: Path | None,
) -> dict[str, Any]:
    selection = base.get("selection", {})
    profile = str(selection.get("profile", "unknown"))
    impact = selection.get("impact") if isinstance(selection.get("impact"), dict) else {}
    impact = {
        "status": "AVAILABLE" if impact else "NOT_AVAILABLE",
        "baseline_commit": base.get("baseline_commit", NOT_AVAILABLE),
        "current_commit": base.get("current_commit", NOT_AVAILABLE),
        "changed_files": selection.get("changed_files", []),
        "changed_capabilities": [],
        "direct_dependents": [],
        "critical_transitive_dependents": [],
        "workflows": [],
        "commits": [],
        "capability_commits": {},
        **impact,
    }
    capabilities = _capability_rows(results, performance, baseline, impact)
    visual_failures = _visual_failures(output, visual_report, visual_evidence_dir)
    findings = _classified_regressions(results, comparison, mutation, visual_failures, impact)
    generated_at = str(base.get("generated_at"))
    enriched = {
        **base,
        "build": {
            "name": _build_name(profile),
            "profile": profile,
            "version": _version(),
            "branch": selection.get("branch", NOT_AVAILABLE),
            "commit": base.get("current_commit", NOT_AVAILABLE),
            "baseline_commit": base.get("baseline_commit", NOT_AVAILABLE),
        },
        "inventory": _inventory(capabilities),
        "quality_trend": _comparison_trend(comparison, performance, baseline),
        "capabilities": capabilities,
        "change_impact": impact,
        "classified_regressions": findings,
        "history": _history_view(history, base),
        "scenario_runs": _scenario_runs(results),
        "flakiness": _flakiness(history, base, results),
        "mutation_view": _mutation_view(
            mutation, history, generated_at, str(base.get("current_commit", NOT_AVAILABLE)),
        ),
        "visual_failures": visual_failures,
        "diagnostics": _diagnostics(findings, impact, profile),
    }
    enriched["critical_regressions"] = len({
        str(item.get("capability"))
        for item in findings
        if item.get("status") in {REGRESSION_FAIL, HARD_FAIL}
        and item.get("classification") != INFRASTRUCTURE_FAILURE
    })
    return enriched


def _display(value: Any, *, percent: bool = False, signed: bool = False) -> str:
    if not _numeric(value):
        return html.escape(str(value))
    number = float(value)
    if percent:
        return f"{number * 100:+.1f}%" if signed else f"{number * 100:.1f}%"
    if signed:
        return f"{number:+.2f}"
    return f"{number:.2f}"


def _table(headers: list[str], rows: list[list[Any]], empty: str) -> str:
    head = "".join(f"<th>{html.escape(value)}</th>" for value in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{value}</td>" for value in row) + "</tr>"
        for row in rows
    ) or f'<tr><td colspan="{len(headers)}">{html.escape(empty)}</td></tr>'
    return f"<div class=\"table-wrap\"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"


def render_quality_html(summary: dict[str, Any]) -> str:
    build = summary["build"]
    inventory = summary["inventory"]
    trend_rows = []
    for row in summary["quality_trend"]:
        quality_metric = row["metric"] not in {"runtime_seconds", "tokens"}
        delta = (
            f"{float(row['delta']) * 100:+.1f} pp"
            if quality_metric and _numeric(row["delta"])
            else f"{float(row['delta']):+.1f}%"
            if row.get("delta_unit") == "percent" and _numeric(row["delta"])
            else _display(row["delta"])
        )
        trend_rows.append([
            html.escape(str(row["metric"])),
            _display(row["baseline"], percent=quality_metric),
            _display(row["current"], percent=quality_metric),
            delta,
            html.escape(str(row["status"])), html.escape(str(row["coverage"])),
        ])
    capability_rows = [[
        html.escape(str(row["capability"])), html.escape(str(row["status"])),
        _display(row["correctness"], percent=True), _display(row["completeness"], percent=True),
        _display(row["evidence"], percent=True), _display(row["stability"], percent=True),
        (
            f"{float(row['runtime_delta_percent']):+.1f}%"
            if _numeric(row["runtime_delta_percent"]) else html.escape(str(row["runtime_delta_percent"]))
        ),
        (
            f"{float(row['token_delta_percent']):+.1f}%"
            if _numeric(row["token_delta_percent"]) else html.escape(str(row["token_delta_percent"]))
        ),
        html.escape(str(row["token_coverage"])), html.escape(str(row["last_changed"]))[:12], html.escape(str(row["impact"])),
    ] for row in summary["capabilities"]]
    classification_rows = [[
        html.escape(str(row["classification"])), html.escape(str(row["capability"])),
        html.escape(str(row["scenario"])), html.escape(str(row["status"])),
        html.escape(str(row["reason"])),
    ] for row in summary["classified_regressions"]]
    flakiness_rows = [[
        html.escape(str(row["scenario"])), str(row["observed_runs"]),
        _display(row["last_n_pass_rate"], percent=True), _display(row["variance"]),
        _display(row["worst_score"]), str(row["consecutive_failures"]),
    ] for row in summary["flakiness"]]
    mutation_rows = [[
        html.escape(str(row["mutation"])), html.escape(str(row["expected_detection"])),
        html.escape(str(row["actual_detection"])), html.escape(str(row["status"])),
    ] for row in summary["mutation_view"]["rows"]]
    mutation_trend_rows = [[
        html.escape(str(row["generated_at"])), html.escape(str(row["commit"]))[:12],
        _display(row["score"], percent=True),
    ] for row in summary["mutation_view"]["trend"]]
    visual_cards = "".join(
        '<article class="visual"><h3>{}</h3>{}<p>{}</p></article>'.format(
            html.escape(str(item["scenario"])),
            f'<a href="{html.escape(str(item["evidence"]))}"><img src="{html.escape(str(item["thumbnail"]))}" alt="Failed visual scenario {html.escape(str(item["scenario"]))}"></a>'
            if item["thumbnail"] != NOT_AVAILABLE else "",
            html.escape(json.dumps(item.get("checks", {}), sort_keys=True)),
        )
        for item in summary["visual_failures"]
    ) or "<p>No failed visual scenarios.</p>"
    diagnostic_rows = [[
        html.escape(str(row["scenario"])), html.escape(str(row["capability"])),
        html.escape(str(row["classification"])), html.escape(str(row["expected"])),
        html.escape(str(row["actual"])), html.escape(str(row["delta"])),
        html.escape(str(row["relevant_artifact"])),
        html.escape(", ".join(row["likely_impacted_by"]) or "none"),
        f"<code>{html.escape(str(row['local_reproduction_command']))}</code>",
    ] for row in summary["diagnostics"]]
    impact = summary["change_impact"]
    inspect_first = summary["diagnostics"][0]["capability"] if summary["diagnostics"] else "none"
    seven = summary["history"]["7_day"]
    thirty = summary["history"]["30_day"]
    history_rows = lambda values: [[
        html.escape(str(row["generated_at"])), html.escape(str(row["commit"]))[:12],
        html.escape(str(row["overall"])), _display(row["correctness"], percent=True),
        _display(row["runtime_seconds"]), _display(row["tokens"]),
    ] for row in values]
    cards = []
    for label in ("skills", "agents", "workflows"):
        value = inventory[label]
        cards.append(f'<div class="metric"><span>{label.title()}</span><strong>{value["passed"]} / {value["total"]}</strong></div>')
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Agent Commons quality summary</title><style>
:root{{--ink:#13111a;--muted:#655f70;--line:#ddd7e5;--paper:#fff;--wash:#f5f2f8;--accent:#a100ff;--danger:#b42318;--ok:#067647}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--wash);color:var(--ink);font:15px/1.45 Inter,system-ui,sans-serif}}
main{{max-width:1440px;margin:auto;padding:32px}}header{{background:var(--ink);color:#fff;padding:28px;border-top:6px solid var(--accent)}}
h1{{margin:0;font-size:clamp(28px,4vw,48px);letter-spacing:.04em}}h2{{margin-top:34px;border-bottom:2px solid var(--ink);padding-bottom:8px}}
.meta,.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-top:18px}}.metric{{background:var(--paper);border:1px solid var(--line);padding:14px}}
.metric span{{display:block;color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.08em}}.metric strong{{font-size:22px}}.status{{color:var(--accent)}}
.table-wrap{{overflow:auto;background:var(--paper);border:1px solid var(--line)}}table{{border-collapse:collapse;width:100%;min-width:760px}}th,td{{padding:10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{background:#eee8f2;font-size:12px;text-transform:uppercase}}
code{{white-space:pre-wrap;word-break:break-word}}.visuals{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}}.visual{{background:#fff;padding:14px;border:1px solid var(--line)}}.visual img{{width:100%;height:auto;border:1px solid var(--line)}}
.note{{color:var(--muted)}}a:focus-visible{{outline:3px solid var(--accent);outline-offset:3px}}
@media(prefers-reduced-motion:reduce){{*,*::before,*::after{{scroll-behavior:auto!important;animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important}}}}
@media print{{body{{background:#fff}}main{{max-width:none;padding:0}}header{{background:#fff;color:#000;border-color:#000}}.table-wrap{{overflow:visible}}table{{min-width:0;font-size:10px}}}}
@media(max-width:700px){{main{{padding:14px}}header{{padding:20px}}}}
</style></head><body><main><header><h1>AGENT COMMONS QUALITY</h1><div class="meta">
<div><small>Build</small><br><strong>{html.escape(str(build['name']))}</strong></div><div><small>Version</small><br><strong>{html.escape(str(build['version']))}</strong></div>
<div><small>Commit</small><br><strong>{html.escape(str(build['commit']))[:12]}</strong></div><div><small>Baseline</small><br><strong>{html.escape(str(build['baseline_commit']))[:12]}</strong></div>
<div><small>Overall</small><br><strong class="status">{html.escape(str(summary['overall']))}</strong></div><div><small>Inspect first</small><br><strong>{html.escape(inspect_first)}</strong></div>
</div></header><div class="grid">{''.join(cards)}<div class="metric"><span>Critical regressions</span><strong>{summary['critical_regressions']}</strong></div>
<div class="metric"><span>Warnings</span><strong>{summary.get('counts', {}).get('warnings', 0)}</strong></div><div class="metric"><span>Mutation score</span><strong>{_display(summary['mutation_view']['score'], percent=True)}</strong></div></div>
<h2>Current vs baseline</h2>{_table(['Metric','Baseline','Current','Delta','Status','Coverage'], trend_rows, 'No comparable last-green metrics.')}
<h2>Capability impact</h2>{_table(['Capability','Status','Correctness','Completeness','Evidence','Stability','Runtime delta %','Token delta %','Token coverage','Last changed','Impact'], capability_rows, 'No capability results.')}
<h2>Change impact</h2><p>Changed: <strong>{html.escape(', '.join(impact.get('changed_capabilities', [])) or 'not available')}</strong></p>
<p>Affected: {html.escape(', '.join([*impact.get('direct_dependents', []), *impact.get('critical_transitive_dependents', []), *impact.get('workflows', [])]) or 'none identified')}</p>
<p class="note">Causality is a Git-and-relationship correlation, not proof. Candidate commits: {html.escape(', '.join(str(item.get('commit'))[:12] for item in impact.get('commits', [])) or 'not available')}.</p>
<h2>Regression classifications</h2>{_table(['Class','Capability','Scenario','Status','Reason'], classification_rows, 'No regressions or infrastructure failures.')}
<h2>7-day trend</h2>{_table(['Run','Commit','Overall','Correctness','Runtime seconds','Tokens'], history_rows(seven), 'No retained 7-day history.')}
<h2>30-day trend</h2>{_table(['Run','Commit','Overall','Correctness','Runtime seconds','Tokens'], history_rows(thirty), 'No retained 30-day history.')}
<h2>Flakiness</h2><p class="note">Flaky scenarios, Pass-rate variance, Runtime trends, and Token trends cover retained reports plus the current report. Consecutive failures count ordered evaluation runs when per-run evidence is available. Worst capability regression and Top unstable capability are listed first in the tables below when present.</p>{_table(['Scenario','Runs','Last N pass rate','Variance','Worst score','Consecutive failing runs'], flakiness_rows, 'No stochastic or historically flaky scenarios.')}
<h2>Mutation diagnostics</h2>{_table(['Mutation','Expected detection','Actual detection','Status'], mutation_rows, 'Mutation data not available.')}
<h3>Mutation score trend</h3>{_table(['Run','Commit','Score'], mutation_trend_rows, 'No retained mutation history.')}
<h2>Visual regressions</h2><div class="visuals">{visual_cards}</div>
<h2>Developer diagnostics</h2>{_table(['Scenario','Capability','Class','Expected','Actual','Delta','Artifact','Likely impacted by','Local reproduction'], diagnostic_rows, 'No failures to reproduce.')}
</main></body></html>"""


def write_quality_outputs(
    output: Path,
    results: list[dict[str, Any]],
    performance: list[dict[str, Any]],
    comparison: dict[str, Any] | None,
    baseline: dict[str, Any] | None,
    mutation: dict[str, Any] | None,
    visual_report: dict[str, Any] | None,
    history: list[dict[str, Any]],
    visual_evidence_dir: Path | None = None,
) -> dict[str, Any]:
    base = json.loads((output / "quality-summary.json").read_text(encoding="utf-8"))
    summary = build_quality_summary(
        base, results, performance, comparison, baseline, mutation, visual_report, history, output, visual_evidence_dir,
    )
    (output / "quality-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8",
    )
    (output / "quality-summary.html").write_text(render_quality_html(summary), encoding="utf-8")
    return summary
