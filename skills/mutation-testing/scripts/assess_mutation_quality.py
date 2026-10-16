#!/usr/bin/env python3
"""Derive an application mutation-testing quality gate from a normalized run, policy, and baseline.

The contract for every input and output field is defined in
``references/mutation-report-contract.md``. The status is derived here so that a prose claim, an
asserted score, or a survivor label alone can never enter a quality gate.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCOPE_PROFILES = ("LOCAL", "PR", "NIGHTLY", "WEEKLY_DEEP")
BASELINE_TEST_STATES = ("PASS", "FAIL", "FLAKY")
TOOL_EXECUTION_STATES = ("VALID", "INVALID", "UNAVAILABLE")
CRITICALITY_TIERS = (
    "SECURITY_CRITICAL",
    "FINANCIAL_OR_CALCULATION",
    "CRITICAL_BUSINESS_LOGIC",
    "INTEGRATION_CONTRACT",
    "NORMAL_BUSINESS_LOGIC",
    "PLUMBING_OR_TRIVIAL",
    "GENERATED_CODE",
)
CRITICAL_TIERS = frozenset(CRITICALITY_TIERS[:3])
BUSINESS_LOGIC_TIERS = frozenset(CRITICALITY_TIERS[:5])
MEANINGFUL_CLASSIFICATIONS = frozenset({"TEST_GAP", "UNSPECIFIED_BEHAVIOR", "TESTABILITY_PROBLEM"})
JUSTIFIABLE_CLASSIFICATIONS = frozenset({"EQUIVALENT_MUTANT", "LOW_VALUE_MUTATION", "DEAD_CODE"})
CLASSIFICATIONS = MEANINGFUL_CLASSIFICATIONS | JUSTIFIABLE_CLASSIFICATIONS | {"FLAKY_OR_INFRASTRUCTURE"}
DEFAULT_REGRESSION_TOLERANCE = 0.02
EXIT_CODES = {"PASS": 0, "WARNING": 0, "FAIL": 2, "NOT_SUPPORTED": 3, "BLOCKED": 4}


class AssessmentError(RuntimeError):
    """The run cannot be assessed because its structure is invalid."""


def load(path: Path, label: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise AssessmentError(f"cannot read {label}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise AssessmentError(f"{label} is not valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise AssessmentError(f"{label} must be a JSON object")
    return value


def validate_run(run: dict) -> tuple[dict, dict, list[dict]]:
    header = run.get("mutation_run")
    if not isinstance(header, dict):
        raise AssessmentError("run lacks a mutation_run object")
    for field in ("scope", "tool", "technology"):
        if not isinstance(header.get(field), str) or not header[field]:
            raise AssessmentError(f"mutation_run.{field} is required")
    if header.get("scope_profile") not in SCOPE_PROFILES:
        raise AssessmentError(f"mutation_run.scope_profile must be one of {list(SCOPE_PROFILES)}")
    if header.get("baseline_tests") not in BASELINE_TEST_STATES:
        raise AssessmentError(f"mutation_run.baseline_tests must be one of {list(BASELINE_TEST_STATES)}")
    if header.get("tool_execution") not in TOOL_EXECUTION_STATES:
        raise AssessmentError(f"mutation_run.tool_execution must be one of {list(TOOL_EXECUTION_STATES)}")
    if header.get("criticality") not in CRITICALITY_TIERS:
        raise AssessmentError(f"mutation_run.criticality must be one of {list(CRITICALITY_TIERS)}")

    metrics = run.get("metrics")
    if header["tool_execution"] == "VALID":
        if not isinstance(metrics, dict):
            raise AssessmentError("a valid run requires a metrics object")
        for field in ("total_mutants", "killed", "survived"):
            if not isinstance(metrics.get(field), int) or metrics[field] < 0:
                raise AssessmentError(f"metrics.{field} must be a non-negative integer")
        if "mutation_score" in metrics:
            raise AssessmentError("metrics must not assert mutation_score; it is derived")
    metrics = metrics if isinstance(metrics, dict) else {}

    survivors = run.get("survivors", [])
    if not isinstance(survivors, list):
        raise AssessmentError("survivors must be a list")
    for index, survivor in enumerate(survivors):
        if not isinstance(survivor, dict):
            raise AssessmentError(f"survivors[{index}] must be an object")
        if not isinstance(survivor.get("id"), str) or not survivor["id"]:
            raise AssessmentError(f"survivors[{index}] lacks an id")
        tier = survivor.get("criticality", header["criticality"])
        if tier not in CRITICALITY_TIERS:
            raise AssessmentError(f"survivor {survivor['id']} has an unknown criticality {tier!r}")
    identifiers = [survivor["id"] for survivor in survivors]
    duplicates = sorted({value for value in identifiers if identifiers.count(value) > 1})
    if duplicates:
        raise AssessmentError(f"survivors have duplicate IDs: {duplicates}")
    if header["tool_execution"] == "VALID" and len(survivors) != metrics.get("survived"):
        raise AssessmentError(
            f"metrics.survived is {metrics.get('survived')} but {len(survivors)} survivors are "
            "recorded; an unaccounted survivor would silently improve the score"
        )
    return header, metrics, survivors


def resolve_minimum(policy: dict, tier: str) -> float | None:
    configured = policy.get("absolute_minimum")
    if isinstance(configured, (int, float)):
        return float(configured)
    if not isinstance(configured, dict):
        return None
    for key in (tier, "default"):
        value = configured.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return None


def compare_baseline(baseline: dict | None, scope: str, score: float | None) -> dict | None:
    if baseline is None:
        return None
    baseline_scope = baseline.get("scope")
    baseline_score = baseline.get("mutation_score")
    if baseline_scope != scope:
        return {
            "comparable": False,
            "reason": "baseline scope differs from the current run",
            "baseline_scope": baseline_scope,
            "current_scope": scope,
        }
    if not isinstance(baseline_score, (int, float)) or score is None:
        return {"comparable": False, "reason": "baseline or current score is not available"}
    delta = round(score - float(baseline_score), 6)
    verdict = "IMPROVED" if delta > 0 else "UNCHANGED" if delta == 0 else "REGRESSED"
    return {
        "comparable": True,
        "baseline_score": float(baseline_score),
        "current_score": score,
        "delta": delta,
        "verdict": verdict,
        "baseline_critical_survivors": baseline.get("critical_survivors"),
        "baseline_test_gaps": baseline.get("test_gaps"),
    }


def assess(run: dict, policy: dict, baseline: dict | None) -> dict:
    header, metrics, survivors = validate_run(run)
    reasons: list[str] = []
    warnings: list[str] = []
    scope = header["scope"]
    run_tier = header["criticality"]

    if header["tool_execution"] == "UNAVAILABLE":
        reason = header.get("not_supported_reason") or "no maintained mutation engine applies to this technology"
        return {
            "schema_version": 1,
            "status": "NOT_SUPPORTED",
            "reasons": [f"mutation tooling unavailable for {header['technology']}: {reason}"],
            "warnings": [],
            "metrics": {"mutation_score": "not_available"},
            "critical_survivors": [],
            "classification_counts": {},
            "baseline_comparison": None,
            "traceability": [],
            "performance": run.get("performance") or {},
            "compensating_verification": header.get("compensating_verification"),
            "run": {key: header.get(key) for key in ("scope", "scope_profile", "tool", "technology")},
        }

    unclassified = [
        survivor["id"] for survivor in survivors
        if survivor.get("classification") not in CLASSIFICATIONS
    ]
    classification_counts: dict[str, int] = {}
    for survivor in survivors:
        key = str(survivor.get("classification"))
        classification_counts[key] = classification_counts.get(key, 0) + 1

    meaningful: list[dict] = []
    excluded: list[dict] = []
    for survivor in survivors:
        classification = survivor.get("classification")
        if classification in JUSTIFIABLE_CLASSIFICATIONS:
            if isinstance(survivor.get("accepted_reason"), str) and survivor["accepted_reason"].strip():
                excluded.append(survivor)
            else:
                meaningful.append(survivor)
                warnings.append(
                    f"survivor {survivor['id']} claims {classification} without a recorded reason "
                    "and stays in the meaningful denominator"
                )
        elif classification in MEANINGFUL_CLASSIFICATIONS:
            meaningful.append(survivor)

    killed = int(metrics.get("killed", 0))
    meaningful_total = killed + len(meaningful)
    score = round(killed / meaningful_total, 6) if meaningful_total else None
    critical_survivors = [
        survivor["id"] for survivor in meaningful
        if survivor.get("criticality", run_tier) in CRITICAL_TIERS
    ]
    baseline_comparison = compare_baseline(baseline, scope, score)

    # Blocking conditions are evaluated before any score-based judgement.
    blocked: list[str] = []
    if header["baseline_tests"] == "FLAKY":
        blocked.append("BLOCKED_BY_FLAKY_TESTS: the baseline suite is not demonstrably stable")
    if any(survivor.get("classification") == "FLAKY_OR_INFRASTRUCTURE" for survivor in survivors):
        flaky = [s["id"] for s in survivors if s.get("classification") == "FLAKY_OR_INFRASTRUCTURE"]
        blocked.append(f"BLOCKED_BY_FLAKY_TESTS: unreliable survivor results {flaky}")
    if unclassified:
        blocked.append(f"survivors are unclassified: {sorted(unclassified)}")
    if header.get("scope_resolved") is False:
        blocked.append("the mutated scope could not be resolved")

    if blocked:
        status = "BLOCKED"
        reasons = blocked
        warnings = []
        score = None
        critical_survivors = []
        baseline_comparison = None
    else:
        if header["baseline_tests"] == "FAIL":
            reasons.append("the normal test suite failed before mutation execution")
        if header["tool_execution"] == "INVALID":
            reasons.append("the mutation tooling reported invalid execution")
        if critical_survivors:
            details = ", ".join(
                f"{survivor['id']} ({survivor.get('criticality', run_tier)}, {survivor.get('classification')})"
                for survivor in meaningful
                if survivor["id"] in set(critical_survivors)
            )
            reasons.append(f"critical meaningful mutant survives: {details}")
        minimum = resolve_minimum(policy, run_tier)
        if minimum is not None and score is not None and score < minimum:
            reasons.append(
                f"mutation score {score:.4f} is below the configured minimum {minimum:.4f} for {run_tier}"
            )
        tolerance = policy.get("regression_tolerance", DEFAULT_REGRESSION_TOLERANCE)
        tolerance = float(tolerance) if isinstance(tolerance, (int, float)) else DEFAULT_REGRESSION_TOLERANCE
        if baseline_comparison and baseline_comparison.get("comparable"):
            delta = baseline_comparison["delta"]
            if delta < -tolerance:
                reasons.append(
                    f"mutation score regressed by {abs(delta):.4f} against the accepted baseline, "
                    f"beyond the {tolerance:.4f} tolerance"
                )
            elif delta < 0:
                warnings.append(
                    f"mutation score deteriorated by {abs(delta):.4f}, within the {tolerance:.4f} tolerance"
                )
        elif baseline_comparison:
            warnings.append(f"baseline is not comparable: {baseline_comparison.get('reason')}")

        changed_gate = policy.get("fail_on_changed_business_logic_survivors", True)
        if changed_gate and header.get("changed_scope_only") is True:
            changed_survivors = [
                survivor["id"] for survivor in meaningful
                if survivor.get("criticality", run_tier) in BUSINESS_LOGIC_TIERS
                and survivor["id"] not in set(critical_survivors)
            ]
            if changed_survivors:
                reasons.append(
                    "changed business logic has surviving meaningful mutants: "
                    f"{sorted(changed_survivors)}"
                )

        non_critical = [
            survivor["id"] for survivor in meaningful
            if survivor.get("criticality", run_tier) not in CRITICAL_TIERS
        ]
        if non_critical:
            warnings.append(f"non-critical meaningful survivors remain: {sorted(non_critical)}")
        if header.get("partial_tooling_unavailable"):
            warnings.append(
                "mutation tooling was unavailable for part of the scope: "
                f"{header['partial_tooling_unavailable']}"
            )
        status = "FAIL" if reasons else ("WARNING" if warnings else "PASS")

    traceability = [
        {
            "survivor": survivor["id"],
            "requirement": survivor.get("requirement"),
            "specification": survivor.get("specification"),
            "acceptance_criterion": survivor.get("acceptance_criterion"),
            "classification": survivor.get("classification"),
            "outcome": "SURVIVED",
        }
        for survivor in survivors
    ]
    return {
        "schema_version": 1,
        "status": status,
        "reasons": reasons,
        "warnings": warnings,
        "metrics": {
            "total_mutants": metrics.get("total_mutants"),
            "killed": killed,
            "survived": metrics.get("survived"),
            "meaningful_survivors": len(meaningful),
            "accepted_equivalent_or_excluded": len(excluded),
            "meaningful_mutants": meaningful_total,
            "mutation_score": score if score is not None else "not_available",
        },
        "critical_survivors": sorted(critical_survivors),
        "classification_counts": dict(sorted(classification_counts.items())),
        "baseline_comparison": baseline_comparison,
        "traceability": traceability,
        "performance": run.get("performance") or {},
        "run": {
            "scope": scope,
            "scope_profile": header["scope_profile"],
            "changed_scope_only": header.get("changed_scope_only"),
            "criticality": run_tier,
            "technology": header["technology"],
            "tool": header["tool"],
            "tool_version": header.get("tool_version"),
            "commit": header.get("commit"),
            "baseline_tests": header["baseline_tests"],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True, help="normalized mutation run JSON")
    parser.add_argument("--policy", type=Path, help="optional project mutation policy JSON")
    parser.add_argument("--baseline", type=Path, help="optional accepted baseline JSON for this scope")
    parser.add_argument("--output", type=Path, help="write the assessment JSON to this path")
    parser.add_argument(
        "--allow-not-supported",
        action="store_true",
        help="exit 0 when the status is NOT_SUPPORTED; the status is still reported",
    )
    args = parser.parse_args()
    try:
        run = load(args.run, "run")
        policy = load(args.policy, "policy") if args.policy else {}
        baseline = load(args.baseline, "baseline") if args.baseline else None
        assessment = assess(run, policy, baseline)
    except AssessmentError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1
    payload = json.dumps(assessment, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    status = assessment["status"]
    if status == "NOT_SUPPORTED" and args.allow_not_supported:
        return 0
    return EXIT_CODES[status]


if __name__ == "__main__":
    raise SystemExit(main())
