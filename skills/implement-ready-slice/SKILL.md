---
name: implement-ready-slice
description: Deterministically shortlist, claim, implement, validate, and hand off one dependency-ready vertical slice with acceptance-scenario traceability, using recorded red-green-refactor evidence by default. Use for an approved queue or an explicitly selected bounded feature. Do not use for tiny unqueued edits, blocked or unapproved behavior, externally owned work, or tasks without a runnable validation path.
---

# Implement one ready slice

Combine deterministic selection with semantic review; do not select from memory alone.

## Select and claim

1. Read governance, canonical requirements/specifications, dependencies, decisions, active claims, Git
   state, and existing implementation/tests.
2. When the invocation supplies a requirement ID or path, resolve it through the project continuation
   resolver. Follow all linked OpenSpec specifications, requirement revisions, acceptance criteria,
   dependencies, and implementation state; do not require the user to locate the specification manually.
   If no approved implementation specification exists, delegate to `specify-openspec-change`, then
   `review-openspec-change`, and stop before code until readiness is established. If several specifications
   apply, honor dependency order and combined scope or request a selection when the order is ambiguous.
3. Preserve unrelated changes. Stop if ownership overlaps or the writable boundary is unclear.
4. Run `scripts/rank_slices.py <queue.json>` when the project can export the normalized queue described
   in `references/queue-contract.md`.
5. Review the top candidates semantically. Reject external-only, decision-blocked, non-observable, or
   deceptively broad work. Record why any higher-ranked candidate was skipped.
6. Claim through the project's canonical ledger using a stable owner and bounded branch/task ID. A claim
   is not completion.

For a coordinator-managed parallel queue, include exact `write_paths` and mutable `shared_surfaces` from
`references/queue-contract.md` in the execution planner. A ranked item is not safe to run concurrently until
dependency, ownership, isolation, and shared-resource conflicts have been checked.

## Prepare

Build a bounded context package for the claimed requirement/specification, acceptance scenarios, affected
components, architecture decisions, dependencies, and required files. Exclude unrelated project history.

Require approved behavior, observable acceptance scenarios, resolved dependencies, exclusive file
ownership, and a runnable validation path. When OpenSpec is required, the slice must name the approved
change/specification, acceptance-criterion IDs, and consumed requirement revisions; a requirement reference
is accepted as input but becomes implementation-ready only after that contract is resolved. Generate a small workpack with evidence, scope, exclusions, decisions, scenarios,
affected boundaries, test plan, and exact gates. Keep partial demonstrability visible.

Concurrent writable slices require a task-specific worktree, branch, or equivalent isolated directory tied
to an immutable base revision. The workpack records the isolation identity, exact writable paths, prohibited
paths, shared-resource leases such as database/port/cache namespaces, and the coordinator return channel.
The worker must stop if its base, claim, ownership, or resource lease drifts.

## Default recorded TDD loop

Follow the canonical `test-driven-development` workflow for each scenario; this slice workflow adds queue,
claim, workpack, and lifecycle requirements rather than defining a competing TDD variant.

If the project manifest or user explicitly opts out of TDD, follow the authorized alternative
implementation method, retain acceptance traceability and appropriate tests, and never claim RED → GREEN →
REFACTOR evidence that did not occur. The opt-out changes the implementation method, not the approved
behavior or validation obligation.

`implement-openspec-change` owns change-level orchestration. This skill owns one dependency-ready vertical
slice within that approved change. Neither replaces the other.

1. Pick the smallest independently testable scenario and narrowest valid test level.
2. Add the focused test first and record a behavior-relevant failure; setup failures do not count.
3. Implement the minimum behavior and record the same test passing.
4. Refactor only while green, then run related contract, integration, security, browser, migration, and
   full gates as applicable.
5. Run the `mutation-testing` quality check over the changed scope before final validation, and harden
   tests against meaningful surviving mutants. Do not require the user to request this step; a supported
   implementation slice includes it by default. Record `NOT_SUPPORTED` or `BLOCKED` rather than skipping it
   silently.
6. Link requirement, specification, scenario, implementation path, stable test, result, mutation quality
   status, verification, and commit/checkpoint.
7. Update canonical state through its deterministic helper. Never patch a dashboard or generated report.

The worker does not merge, update a shared queue, check another slice's task box, or claim change-level
completion. It returns the changed-path manifest, checkpoint or commit, output fingerprint, RED/GREEN and
related-gate evidence, the mutation quality status with any unresolved test gaps, unresolved dependencies, and
limitations. The coordinator validates and integrates
that result before dependent work begins.

Use `design-test-strategy` when the correct test layer is disputed. A coordinator-assigned implementation
or TDD worker executes these skills within exclusive ownership and returns evidence; do not add a permanent
wrapper role with no responsibility beyond the workflow. Ask a fresh `test-behavior-reviewer` to challenge
consequential completion evidence.

## Atomic progress and stall recovery

At each validated slice checkpoint, update canonical delivery state first and then merge the compact memory
delta. Failed or partial work remains explicit and cannot become a completed memory record.

Keep batches small enough to validate and recover. Produce an early valid artifact, checkpoint each green
state, and set an explicit abort threshold for repeated failures or environment drift. When stalled, return
to the last verified checkpoint, isolate the unresolved assumption, preserve partial evidence, and record one
exact continuation step rather than broadening scope or leaving canonical state half-updated.

## Stop conditions

Stop on an unapproved business decision, missing source authority, invalid red phase, dependency drift,
ownership collision, unrelated dirty files, unavailable required verifier, or failing full gate. Record the
blocker and exact continuation step. Do not weaken assertions or mark a mock/partial slice complete.

Completion requires passing focused and full gates, a resolved mutation quality status with no unaddressed
critical surviving mutant, satisfied acceptance criteria, valid traceability, honest lifecycle state,
independent verification where required, and an authorized bounded commit when commits are in scope.
