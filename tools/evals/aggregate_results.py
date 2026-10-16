#!/usr/bin/env python3
"""Aggregate isolated CI evaluation shards into one authoritative quality report."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from eval_common import ROOT, EvalConfigError, load_capability_contracts, load_thresholds, stable_unique
from quality_reporting import write_quality_outputs
from run_evals import (
    HARD_FAIL,
    REGRESSION_FAIL,
    WARNING,
    aggregate_performance,
    canonical_profile,
    compare_performance_to_baseline,
    result_record,
    write_outputs,
)
from select_impacted_evals import select_impacted


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def discover_shards(root: Path, output: Path, excluded: list[Path]) -> list[Path]:
    return sorted({
        path.parent
        for path in root.rglob("capabilities.json")
        if (path.parent / "summary.json").is_file()
        if output not in path.parents
        and not any(exclusion == path or exclusion in path.parents for exclusion in excluded)
    })


def merge_impacts(impacts: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not impacts:
        return None
    list_fields = {
        "changed_files", "requested_capability_ids", "changed_capabilities",
        "uncovered_changed_capabilities", "changed_archetypes", "changed_overlays",
        "direct_dependents", "critical_transitive_dependents", "archetypes", "overlays",
        "workflows", "required_scenarios", "protected_changes",
    }
    merged: dict[str, Any] = {
        "schema_version": 1,
        "relationship_semantics": impacts[0].get(
            "relationship_semantics", "catalog related links are symmetric evaluation-impact edges",
        ),
        "all_capabilities": any(bool(item.get("all_capabilities")) for item in impacts),
    }
    for field in list_fields:
        merged[field] = sorted({
            str(value)
            for impact in impacts
            for value in impact.get(field, [])
        })
    return merged


def load_shards(paths: list[Path]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    results: list[dict[str, Any]] = []
    capabilities: list[str] = []
    workflows: list[str] = []
    changed_files: list[str] = []
    impacts: list[dict[str, Any]] = []
    for path in paths:
        shard_results = read_json(path / "capabilities.json")
        if not isinstance(shard_results, list):
            raise EvalConfigError(f"CI shard is not a result array: {path / 'capabilities.json'}")
        results.extend(shard_results)
        summary_path = path / "summary.json"
        if not summary_path.is_file():
            continue
        selection = read_json(summary_path).get("selection", {})
        capabilities.extend(selection.get("capabilities", []))
        workflows.extend(selection.get("workflows", []))
        changed_files.extend(selection.get("changed_files", []))
        if isinstance(selection.get("impact"), dict):
            impacts.append(selection["impact"])
    return results, {
        "capabilities": stable_unique(capabilities),
        "workflows": stable_unique(workflows),
        "changed_files": sorted(set(changed_files)),
        "impact": merge_impacts(impacts),
    }


def unavailable_comparison(baseline: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "baseline_commit": baseline.get("baseline_commit", "not_available"),
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": "NOT_AVAILABLE",
        "reason": "no accepted last-green baseline is available; this green full run may bootstrap it",
        "rows": [],
    }


def load_history(root: Path | None, days: int = 30) -> list[dict[str, Any]]:
    if root is None or not root.exists():
        return []
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    summaries: list[dict[str, Any]] = []
    for path in root.rglob("quality-summary.json"):
        try:
            payload = read_json(path)
            generated = datetime.fromisoformat(str(payload["generated_at"]).replace("Z", "+00:00"))
            if generated.tzinfo is None:
                generated = generated.replace(tzinfo=timezone.utc)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError, OSError):
            continue
        if generated >= cutoff:
            summaries.append(payload)
    return sorted(summaries, key=lambda item: item["generated_at"])


def git_change_impact(
    baseline_commit: str,
    current_commit: str,
    repository: Path = ROOT,
) -> dict[str, Any]:
    unavailable = {
        "status": "NOT_AVAILABLE",
        "reason": "the accepted baseline commit is unavailable in this checkout",
        "baseline_commit": baseline_commit,
        "current_commit": current_commit,
    }
    if baseline_commit in {"", "not_available"}:
        return unavailable
    exists = subprocess.run(
        ["git", "cat-file", "-e", f"{baseline_commit}^{{commit}}"],
        cwd=repository,
        capture_output=True,
        text=True,
    )
    if exists.returncode:
        return unavailable
    changed = subprocess.run(
        ["git", "diff", "--name-only", f"{baseline_commit}..{current_commit}"],
        cwd=repository,
        capture_output=True,
        text=True,
    )
    if changed.returncode:
        return {**unavailable, "reason": changed.stderr.strip() or "Git diff failed"}
    changed_files = [value for value in changed.stdout.splitlines() if value]
    impact = select_impacted(changed_files)
    log = subprocess.run(
        ["git", "log", "--reverse", "--format=%H%x09%s", f"{baseline_commit}..{current_commit}", "--", *changed_files],
        cwd=repository,
        capture_output=True,
        text=True,
    )
    commits = []
    if log.returncode == 0:
        for line in log.stdout.splitlines():
            commit, _, subject = line.partition("\t")
            if commit:
                commits.append({"commit": commit, "subject": subject})
    paths = {
        identifier: contract.get("path")
        for identifier, contract in load_capability_contracts().get("capabilities", {}).items()
    }
    capability_commits: dict[str, list[str]] = {}
    for capability in impact.get("changed_capabilities", []):
        path = paths.get(capability)
        if not path:
            continue
        capability_log = subprocess.run(
            ["git", "log", "--format=%H", f"{baseline_commit}..{current_commit}", "--", str(path)],
            cwd=repository,
            capture_output=True,
            text=True,
        )
        if capability_log.returncode == 0:
            capability_commits[capability] = [value for value in capability_log.stdout.splitlines() if value]
    return {
        **impact,
        "status": "AVAILABLE",
        "baseline_commit": baseline_commit,
        "current_commit": current_commit,
        "commits": commits,
        "capability_commits": capability_commits,
    }


def write_azure_summary(output: Path) -> None:
    summary = read_json(output / "quality-summary.json")
    impact = summary.get("change_impact", {})
    changed = len(impact.get("changed_capabilities", []))
    impacted = sum(len(impact.get(name, [])) for name in ("changed_capabilities", "direct_dependents", "critical_transitive_dependents"))
    workflows = len(impact.get("workflows", []))
    classifications: dict[str, int] = {}
    for row in summary.get("classified_regressions", []):
        name = str(row.get("classification"))
        classifications[name] = classifications.get(name, 0) + 1
    classification_text = ", ".join(f"{name}={count}" for name, count in sorted(classifications.items())) or "none"
    counts = summary.get("counts", {})
    inspect_first = summary.get("diagnostics", [{}])[0].get("capability", "none") if summary.get("diagnostics") else "none"
    text = f"""# Agent Commons Quality

Overall: **{summary.get('overall', 'FAIL')}**

- Build: {summary.get('build', {}).get('name', 'Evaluation')}
- Version: {summary.get('build', {}).get('version', 'not_available')}
- Changed: {changed} capabilities
- Impacted: {impacted} capabilities, {workflows} workflows
- Critical regressions: {summary.get('critical_regressions', 0)}
- Warnings: {counts.get('warnings', 0)}
- Baseline: `{summary.get('baseline_commit', 'not_available')}`
- Current: `{summary.get('current_commit', 'not_available')}`
- Regression classes: {classification_text}
- Inspect first: `{inspect_first}`

Open `quality-summary.html` for capability trends, flakiness, mutations, visual evidence, and reproduction commands.
"""
    (output / "azure-summary.md").write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", type=Path, default=[])
    parser.add_argument("--input-root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--mutation-report", type=Path)
    parser.add_argument("--visual-report", type=Path)
    parser.add_argument("--history-dir", type=Path)
    parser.add_argument("--required-shard", action="append", default=[])
    parser.add_argument("--weekly-report", action="store_true")
    args = parser.parse_args()

    output = args.output.resolve()
    shard_paths = [path.resolve() for path in args.input]
    if args.input_root:
        excluded = [args.history_dir.resolve()] if args.history_dir else []
        shard_paths.extend(discover_shards(args.input_root.resolve(), output, excluded))
    shard_paths = sorted(set(shard_paths))
    results, selection = load_shards(shard_paths)
    if not shard_paths:
        results.append(result_record(
            "ci-aggregation", "tool", "shard-discovery", 3, 1, True, HARD_FAIL, 0.0,
            "no evaluation shard outputs were available; classify upstream failure as infrastructure",
        ))
    available_shards = {path.name for path in shard_paths}
    missing_shards = sorted(set(args.required_shard) - available_shards)
    if missing_shards:
        results.append(result_record(
            "ci-aggregation", "tool", "required-shards", 3, 1, True, HARD_FAIL, 0.0,
            "infrastructure failure; missing required shard artifacts: " + ", ".join(missing_shards),
        ))
    selection.update({"profile": canonical_profile(args.profile), "branch": args.branch})

    mutation = read_json(args.mutation_report) if args.mutation_report and args.mutation_report.is_file() else None
    if args.mutation_report and mutation is None:
        results.append(result_record(
            "mutation-testing", "suite", "critical-mutations", 4, 1, True, HARD_FAIL, 0.0,
            "infrastructure failure; mutation report artifact is missing",
        ))
    if mutation and mutation.get("status") != "PASS":
        mutation_errors = [
            item.get("id", "unknown")
            for item in mutation.get("results", [])
            if item.get("status") == "ERROR"
        ]
        results.append(result_record(
            "mutation-testing", "suite", "critical-mutations", 4, 1, True, HARD_FAIL, 0.0,
            (
                "infrastructure failure; mutation execution error: " + ", ".join(mutation_errors)
                if mutation_errors
                else "critical mutation survived"
            ),
        ))
    visual = read_json(args.visual_report) if args.visual_report and args.visual_report.is_file() else None
    if args.visual_report and visual is None:
        results.append(result_record(
            "visual-regression", "suite", "representative-states", 3, 1, True, HARD_FAIL, 0.0,
            "infrastructure failure; visual report artifact is missing",
        ))
    if visual and visual.get("status") != "PASS":
        results.append(result_record(
            "visual-regression", "suite", "representative-states", 3, 1, True, HARD_FAIL, 0.0,
            "visual regression verification failed",
        ))

    comparison = None
    baseline = None
    if args.baseline and args.baseline.is_file():
        baseline = read_json(args.baseline)
        if baseline.get("status") == "accepted":
            comparison, baseline_results = compare_performance_to_baseline(
                aggregate_performance(results), baseline, load_thresholds(),
            )
            results.extend(baseline_results)
        else:
            comparison = unavailable_comparison(baseline)

    current = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True,
    ).stdout.strip() or "not_available"
    existing_impact = selection.get("impact") if isinstance(selection.get("impact"), dict) else None
    if existing_impact:
        selection["impact"] = {
            "status": "AVAILABLE",
            "baseline_commit": baseline.get("baseline_commit", "not_available") if baseline else "not_available",
            "current_commit": current,
            "commits": [],
            "capability_commits": {},
            **existing_impact,
        }
    else:
        selection["impact"] = git_change_impact(
            baseline.get("baseline_commit", "not_available") if baseline else "not_available",
            current,
        )

    history = load_history(args.history_dir, 30)
    write_outputs(output, selection, results, comparison, mutation, visual)
    performance = aggregate_performance(results)
    write_quality_outputs(
        output,
        results,
        performance,
        comparison,
        baseline,
        mutation,
        visual,
        history,
        args.visual_report.parent / "screenshots" if args.visual_report else None,
    )
    write_azure_summary(output)
    summary = read_json(output / "quality-summary.json")
    if args.weekly_report:
        shutil.copy2(output / "quality-summary.html", output / "weekly-quality-report.html")
    status = summary.get("overall_status")
    return 2 if status == HARD_FAIL else 1 if status == REGRESSION_FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
