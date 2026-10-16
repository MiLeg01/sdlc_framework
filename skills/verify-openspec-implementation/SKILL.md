---
name: verify-openspec-implementation
description: Independently verify that a completed implementation satisfies one OpenSpec change across requirements, scenarios, tasks, design, tests, and repository gates. Use after implementation and before archive or closure. Do not use to implement missing behavior, rewrite the specification to match code, treat checked boxes as proof, or archive a change with unresolved critical mismatches.
---

# Verify implementation against OpenSpec

Verification reconciles the approved change with current code and observable evidence. It is not an
implementation pass and does not make divergence disappear by editing the specification after the fact.

## Build the verification set

1. Resolve the exact active change and read governance, Git state, OpenSpec configuration, main specs, change
   metadata and artifacts, implementation diff, tests, and recorded commands/results.
2. Run `openspec status --change <name> --json`, `openspec show <name> --json`, and
   `openspec validate <name> --strict --no-interactive`.
3. If the project exposes the expanded OpenSpec verify action, use it as additional evidence, not as a
   substitute for repository tests or semantic review.
4. Keep verification read-only. When missing work is found, return it to the implementation or specification
   workflow instead of fixing it while claiming independence.

Verification may inspect completed slice packets incrementally while other independent slices continue, but
each finding must name the immutable slice checkpoint and input revisions it examined. Incremental review can
reject or return one slice early; it cannot produce change-level `PASS` or archive readiness.

## Reconcile every material claim

For each requirement and scenario, identify:

- the implementation path and behavior that satisfy it;
- the task or slice that delivered it;
- the stable automated test or exact manual/operational verification;
- the latest result and whether the oracle is credible;
- the mutation quality status for that behavior where mutation testing applies, including any accepted
  equivalent mutants and unresolved test gaps;
- any divergence, partial behavior, untested edge, or unsupported completion claim.

Confirm all tasks are actually complete, design decisions are reflected in code or explicitly superseded,
negative and boundary behavior matches the specification, and relevant focused plus full repository gates
pass. A checked task, aggregate green suite, generated report, coverage percentage, or structural OpenSpec
validation alone is not proof that every scenario is implemented. Where mutation testing applies, consume the
recorded `mutation-testing` gate result as test-quality evidence rather than rerunning that analysis here; a
critical surviving mutant against a criterion in scope prevents `PASS` for that criterion even when its tests
are green.

Before the final decision, rebuild the verification set from one integrated commit or equivalent immutable
snapshot. Confirm that coordinator merges did not change scenario behavior, invalidate tests, overlap owned
paths, or consume stale requirement/specification revisions. Run cross-slice and full repository gates on
that integrated state rather than combining isolated green results arithmetically.

For pure refactors, prove intended behavior remained stable and the stated structural outcome exists. For bug
fixes, require a regression test or an explicit limitation explaining why automation is not credible.

## Decide validation and archive readiness

Classify findings as `CRITICAL`, `WARNING`, or `SUGGESTION`. For each specification return:

- `PASS`: every required acceptance criterion has credible passing evidence and implementation matches;
- `PARTIAL`: some criteria are implemented or tested, but required coverage remains incomplete;
- `FAIL`: observed code or tests contradict the approved specification;
- `BLOCKED`: authority, environment, dependency, or evidence prevents a valid decision.

Also return `READY_TO_COMPLETE`, `READY_WITH_LIMITATIONS`, or `NOT_READY`. Any missing required behavior,
uncovered acceptance criterion, unresolved specification mismatch, stale requirement revision, incomplete
task, failing required test, unresolved critical surviving mutant, invalid change, or unapproved artifact
correction is `NOT_READY`. Green tests cannot produce `PASS` when any acceptance criterion lacks a credible
test or explicit approved verification. An explicit `NOT_SUPPORTED` or `BLOCKED` mutation status is a recorded
limitation, not a substitute for one.

Return a compact requirement/scenario-to-code-and-test map, commands and results, findings, limitations, and
the exact next workflow: specification review, implementation, or completion. Do not archive the change.
