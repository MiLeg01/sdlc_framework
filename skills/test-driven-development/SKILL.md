---
name: test-driven-development
description: Drive an approved behavior change through a strict, evidence-recorded red-green-refactor loop at the narrowest credible test level. Use for ordinary features, regressions, services, components, migrations, and unqueued bounded changes with a runnable test path. Do not use for documentation-only edits, exploratory spikes with no asserted behavior, blocked decisions, or work whose environment cannot demonstrate a behavior-relevant RED state, and do not run the mutation quality check before meaningful implementation exists.
---

# Practice test-driven development

Treat RED, GREEN, and REFACTOR as observable states, not labels added after implementation.

The full default cycle is RED, GREEN, REFACTOR, test-suite pass, mutation quality check, test hardening if
required, then validation against the specification. TDD asks whether the behavior was specified through
tests. Mutation testing asks whether those tests would fail if the implementation were wrong. Both questions
matter, and a green suite answers only the first.

## Establish the behavior

1. Read local governance, approved requirements or OpenSpec change, acceptance criteria, existing tests,
   implementation, and validation commands.
2. When OpenSpec governs the change, select one approved acceptance criterion or scenario as the primary
   behavioral input and retain its specification ID and requirement trace. OpenSpec states **what** behavior
   must exist; TDD is **how** that behavior is implemented and proved incrementally.
3. State one smallest observable behavior, its boundary, and the evidence that authorizes it.
4. Select the narrowest test level that can fail for the intended reason. Use `design-test-strategy` first
   when the risk or correct level is unclear.
5. Protect unrelated work and establish an exact rollback or checkpoint before editing.

For a substantial project, load only the selected scenario, linked requirement/specification revisions,
affected component memory, architecture decisions, and necessary files. Project memory is routing context,
not a substitute for the executable test or source under change.

When multiple TDD loops run concurrently, each worker must use an isolated writable checkout or task
directory at a verified base revision and own all production and test paths it may change. Reserve distinct
ports, databases, containers, caches, coverage outputs, temporary directories, and generated artifacts.
Shared fixtures, snapshots, schemas, lockfiles, and external state are mutable shared surfaces and force
serialization unless the coordinator proves isolation.

## RED

1. Add or change one focused test before production behavior.
2. Run it and confirm that it fails because the behavior is absent or wrong.
3. Record the command, relevant failure, and intended assertion. Compilation, fixture, dependency,
   permission, or environment failures are setup failures and do not count as RED.
4. If the test passes immediately, prove the behavior already exists, strengthen the test, or stop the
   duplicate change. Never manufacture a failure by weakening or breaking unrelated code.

## GREEN

1. Implement only enough production behavior to satisfy the focused test.
2. Run the identical test and record it passing.
3. Run directly related tests to detect a local regression. Do not alter the assertion merely to obtain
   green unless the approved behavior or evidence changed.

Return the focused RED/GREEN evidence as soon as the smallest behavior is green so the coordinator can
validate and integrate incrementally. This does not release the worker from refactor, related tests, or the
required broader gate, and it does not authorize dependent work until the coordinator accepts the checkpoint.

## REFACTOR and broaden

1. Improve names, structure, duplication, and boundaries only while focused tests remain green.
2. Add boundary, negative, contract, integration, browser, security, migration, or end-to-end coverage
   only where the risk model requires it.
3. Run the repository's full required gate. Keep pre-existing and new failures distinct.
4. Link acceptance scenario, test, implementation path, command, result, and checkpoint or commit.
5. Record the RED, GREEN, and REFACTOR evidence against the acceptance criterion without marking the whole
   specification validated. Green tests prove only the behaviors they credibly cover.
6. After canonical test and implementation state is recorded, merge the bounded validation delta and next
   action into project memory; do not store raw test logs.

## Mutation quality check

Passing tests are not evidence of strong tests. Once the implementation is stable and green and the refactor
step is complete, delegate test-strength evaluation to `mutation-testing` for the changed scope. Do not
attempt this during RED, and do not reimplement mutation tooling, scope selection, survivor classification, or
gate logic here; that workflow owns them.

1. Hand over the changed production paths, the acceptance criterion and specification IDs, the passing test
   command, and the criticality of the behavior.
2. When a meaningful mutant survives, follow the returned test-hardening loop: add or improve one behavioral
   test, prove it fails against the mutant, prove it passes against the correct implementation, and rerun the
   targeted mutation scope. Never change correct production behavior to kill a mutant, and never add
   implementation-coupled assertions to raise a score.
3. Record `TESTS_PASS`, then `MUTATION_CHECKED`, then `TEST_QUALITY_VALIDATED` as separate observable states.
   A green suite establishes only the first. Report `NOT_SUPPORTED` or `BLOCKED` honestly when the technology
   has no maintained mutation engine or the baseline suite is not stable enough to trust the result.

If the acceptance criterion is incorrect, ambiguous, or incompatible with authoritative constraints, stop
the TDD loop and return to the specification workflow. Do not change the test and production behavior to a
different contract while leaving the approved OpenSpec change untouched.

## Recovery and delegation

Work in small recoverable batches and leave an early valid test artifact. If progress stalls, return to
the last green checkpoint, isolate the failing assumption, and record one exact continuation step. A
coordinator-assigned TDD worker follows this workflow and returns evidence; it does not need a permanent
wrapper role. For consequential claims, delegate the completed evidence to a fresh
`test-behavior-reviewer` rather than asking the implementer to certify its own work.

## Completion

Complete only when RED was behavior-relevant, the same focused test is green, required broader gates pass,
the mutation quality check reached `TEST_QUALITY_VALIDATED` or reported an explicit `NOT_SUPPORTED`,
`BLOCKED`, or accepted-survivor result, acceptance behavior is satisfied, trace links resolve, and limitations
are explicit. Where mutation testing applies, passing normal tests alone are not sufficient evidence of test
quality. Hand the result to
`verify-openspec-implementation` when OpenSpec governs the change; only that broader reconciliation can mark
the specification PASS, PARTIAL, FAIL, or BLOCKED. If any TDD phase cannot be demonstrated, report the work
as partial or blocked rather than retroactively claiming TDD.
