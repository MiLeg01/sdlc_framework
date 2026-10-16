#!/usr/bin/env python3
"""Deterministically verify critical methodology statements used by mutation tests."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def flowed(relative: str) -> str:
    """Read a canonical markdown body with hard line wraps collapsed to single spaces."""
    return re.sub(r"\s+", " ", (ROOT / relative).read_text(encoding="utf-8"))


def check_red_first(failures: list[str]) -> None:
    source = (ROOT / "skills/test-driven-development/SKILL.md").read_text(encoding="utf-8")
    test_first = re.search(r"add or change one focused test before production behavior", source, re.I)
    contradictory = re.search(r"implement production behavior before adding .*test", source, re.I)
    red_evidence = "behavior-relevant RED" in source and "same focused test" in source
    if not test_first or contradictory or not red_evidence:
        failures.append("RED-first ordering is absent or contradicted")


def check_mutation_quality_gate(failures: list[str]) -> None:
    """A critical surviving mutant must fail validation, not merely warn."""
    gates = flowed("skills/mutation-testing/references/quality-gates.md")
    hard_failures = re.search(r"### Hard failures (?P<body>.*?)(?=### )", gates)
    if not hard_failures:
        failures.append("mutation quality gates do not declare hard failures")
    elif not re.search(
        r"a critical behavioral mutant survives, regardless of the aggregate score",
        hard_failures.group("body"), re.I,
    ):
        failures.append("a surviving critical mutant is not a hard failure")
    warnings = re.search(r"### Warnings (?P<body>.*?)(?=### )", gates)
    if warnings and re.search(r"critical (behavioral )?mutant survives", warnings.group("body"), re.I):
        failures.append("a surviving critical mutant is demoted to a warning")
    if not re.search(r"An unsupported technology is never a pass", gates, re.I):
        failures.append("unsupported mutation tooling is not explicitly barred from passing")

    skill = flowed("skills/mutation-testing/SKILL.md")
    if not re.search(r"Passing tests are not evidence of strong tests", skill, re.I):
        failures.append("the mutation-testing skill no longer states that passing tests are not test quality")
    if not re.search(r"Never modify correct production behavior to kill a mutant", skill, re.I):
        failures.append("the mutation-testing skill no longer forbids distorting production code")


def check_tdd_delegates_mutation(failures: list[str]) -> None:
    """TDD must delegate the mutation quality check after GREEN and REFACTOR."""
    source = flowed("skills/test-driven-development/SKILL.md")
    if "mutation-testing" not in source:
        failures.append("TDD does not delegate to the canonical mutation-testing capability")
    if not re.search(r"## Mutation quality check", source):
        failures.append("TDD has no mutation quality check phase")
    if not re.search(r"Do not attempt this during RED", source, re.I):
        failures.append("TDD no longer excludes mutation testing from the RED phase")
    if not re.search(r"passing normal tests alone are not sufficient evidence of test quality", source, re.I):
        failures.append("TDD completion still treats a green suite as sufficient test-quality evidence")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--case",
        choices=("red-first", "mutation-quality-gate", "tdd-delegates-mutation", "all"),
        default="all",
    )
    args = parser.parse_args()
    failures: list[str] = []
    if args.case in {"red-first", "all"}:
        check_red_first(failures)
    if args.case in {"mutation-quality-gate", "all"}:
        check_mutation_quality_gate(failures)
    if args.case in {"tdd-delegates-mutation", "all"}:
        check_tdd_delegates_mutation(failures)
    if failures:
        print("FAIL: " + "; ".join(failures))
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
