# Mutation run, policy, baseline, and assessment contract

Normalize every tool's native report into this structure before classifying or gating. The structure keeps
runs comparable across ecosystems and keeps the gate derived from data rather than asserted in prose.

`scripts/assess_mutation_quality.py` consumes the run, optional policy, and optional baseline defined here and
emits the assessment. Do not compute a status by hand.

## Application mutation testing is not Commons methodology mutation testing

Two distinct systems share this vocabulary and must never share a result model:

- **Application mutation testing** — this workflow. It mutates implemented application code to evaluate the
  strength of that project's tests.
- **Agent Commons methodology mutation testing** — repository quality infrastructure that mutates canonical
  skills and contracts to verify that the Commons evaluations detect degraded agent behavior.

They may be reported with similar language. They have separate inputs, separate gates, separate baselines, and
separate owners. Never aggregate their scores.

## Mutation run

```json
{
  "schema_version": 1,
  "mutation_run": {
    "scope_profile": "PR",
    "scope": "src/main/java/example/payment/PaymentCalculator.java",
    "changed_scope_only": true,
    "criticality": "FINANCIAL_OR_CALCULATION",
    "technology": "jvm",
    "tool": "pitest",
    "tool_version": "1.15.0",
    "commit": "0f2c9ab",
    "baseline_tests": "PASS",
    "baseline_test_command": "mvn -q -pl payment test",
    "tool_execution": "VALID"
  },
  "metrics": {"total_mutants": 48, "killed": 44, "survived": 4},
  "performance": {
    "runtime_seconds": 184.2,
    "mutants_per_second": 0.26,
    "affected_tests": 63,
    "timeouts": 1,
    "excluded": ["target/generated-sources/**"]
  },
  "survivors": [
    {
      "id": "MUT-017",
      "component": "example.payment.PaymentCalculator",
      "location": "src/main/java/example/payment/PaymentCalculator.java:64",
      "operator": "CONDITIONAL_BOUNDARY",
      "mutation": "threshold comparison < replaced with <=",
      "classification": "TEST_GAP",
      "criticality": "FINANCIAL_OR_CALCULATION",
      "requirement": "REQ-017",
      "specification": "SPEC-004",
      "acceptance_criterion": "AC-004-3",
      "affected_tests": ["PaymentCalculatorTest.appliesReducedRate"],
      "evidence": ["pit-reports/202609/index.html#MUT-017"],
      "recommended_action": "add a boundary test at the exact tax threshold and one value on each side"
    }
  ]
}
```

Field rules:

- `scope_profile` is one of `LOCAL`, `PR`, `NIGHTLY`, `WEEKLY_DEEP`.
- `criticality` is the tier of the mutated scope, from `references/quality-gates.md`. A survivor may override
  it with its own `criticality`.
- `baseline_tests` is `PASS`, `FAIL`, or `FLAKY`. Report `FLAKY` whenever the suite's stability is not
  demonstrated; that produces `BLOCKED_BY_FLAKY_TESTS` rather than an untrustworthy score.
- `tool_execution` is `VALID`, `INVALID`, or `UNAVAILABLE`. `UNAVAILABLE` is how a technology with no
  maintained mutation engine is represented, and it produces `NOT_SUPPORTED`, never a pass.
- `metrics` carries only counts the tool actually produced. The mutation score is **not** an input; it is
  derived, so an incorrect asserted score cannot enter a gate.
- `performance` values are optional and are recorded only when the tool reports them. Do not fabricate them.
- Every survivor requires `id`, `classification`, and `criticality`. An unclassified survivor blocks the
  assessment, because a run with unexamined survivors is not a completed analysis.
- `EQUIVALENT_MUTANT`, `LOW_VALUE_MUTATION`, and `DEAD_CODE` are excluded from the meaningful denominator only
  when the survivor also carries an `accepted_reason`. An unjustified equivalence claim stays in the
  denominator and raises a warning, so a survivor cannot be dismissed by label alone.
- `requirement`, `specification`, and `acceptance_criterion` link the survivor into the existing evidence
  chain. Leave them absent rather than guessing.

## Meaningful mutants and score

Killed mutants are meaningful by definition. Accepted equivalent, low-value, and justified dead-code survivors
are excluded from both terms and reported separately.

```
meaningful mutants  = killed + meaningful survivors
mutation score      = killed / meaningful mutants
```

A survivor is **meaningful** when it is classified `TEST_GAP`, `UNSPECIFIED_BEHAVIOR`, or
`TESTABILITY_PROBLEM`, or when it claims exclusion without a recorded reason. A meaningful survivor is
**critical** when its tier is `SECURITY_CRITICAL`, `FINANCIAL_OR_CALCULATION`, or
`CRITICAL_BUSINESS_LOGIC`.

## Policy

Optional, project-owned, and only as strict as the project deliberately chose.

```json
{
  "schema_version": 1,
  "absolute_minimum": {"default": null, "FINANCIAL_OR_CALCULATION": 0.95},
  "regression_tolerance": 0.02,
  "fail_on_changed_business_logic_survivors": true
}
```

`absolute_minimum` is resolved by the run's criticality tier and falls back to `default`. A null value means no
absolute threshold, which is the default: regression comparison is the primary mechanism.
`fail_on_changed_business_logic_survivors` fails a changed-code run that leaves meaningful survivors in any
business-logic tier, which is the point of a pull-request gate.

## Baseline

One accepted result per scope. Never promoted from a `FAIL`, `BLOCKED`, or `NOT_SUPPORTED` run.

```json
{
  "schema_version": 1,
  "scope": "src/main/java/example/payment/PaymentCalculator.java",
  "tool": "pitest",
  "commit": "9d41c02",
  "accepted_at": "2026-08-14",
  "mutation_score": 0.875,
  "meaningful_mutants": 48,
  "killed": 42,
  "critical_survivors": 0,
  "test_gaps": 8,
  "accepted_equivalent_mutants": 2
}
```

A baseline whose `scope` differs from the current run is not comparable; the assessment reports that instead of
inventing a regression signal.

## Assessment output

```json
{
  "schema_version": 1,
  "status": "FAIL",
  "reasons": ["critical meaningful mutant survives: MUT-017 (FINANCIAL_OR_CALCULATION, TEST_GAP)"],
  "warnings": [],
  "metrics": {
    "total_mutants": 48, "killed": 44, "survived": 4,
    "meaningful_survivors": 2, "accepted_equivalent_or_excluded": 2,
    "meaningful_mutants": 46, "mutation_score": 0.9565
  },
  "critical_survivors": ["MUT-017"],
  "classification_counts": {"TEST_GAP": 2, "EQUIVALENT_MUTANT": 2},
  "baseline_comparison": {"comparable": true, "baseline_score": 0.875, "current_score": 0.9565, "delta": 0.0815, "verdict": "IMPROVED"},
  "traceability": [{"survivor": "MUT-017", "requirement": "REQ-017", "specification": "SPEC-004", "acceptance_criterion": "AC-004-3", "outcome": "SURVIVED"}],
  "performance": {"runtime_seconds": 184.2, "timeouts": 1},
  "run": {"scope": "...", "tool": "pitest", "scope_profile": "PR"}
}
```

Exit codes: `0` for `PASS` and `WARNING`, `2` for `FAIL`, `3` for `NOT_SUPPORTED`, `4` for `BLOCKED`.
`NOT_SUPPORTED` is deliberately non-zero so it cannot be mistaken for a pass; a project may pass
`--allow-not-supported` for a low-risk module while the status is still reported.

## Human summary

Always follow the structured output with a short readable summary. Report scope, tool, baseline result, mutant
totals, killed, survived, meaningful survivors, critical survivors, score, status, the reason for that status,
the linked requirement and specification IDs, and the recommended action. Never output a bare score.

## Compact project-memory state

When project memory is enabled, merge only this much, and reference the raw report rather than storing it:

- last run date, scope, and tool;
- mutation score and status;
- meaningful and critical survivor counts;
- accepted equivalent mutants;
- baseline score and comparison verdict;
- unresolved test gaps with their requirement or specification IDs.
