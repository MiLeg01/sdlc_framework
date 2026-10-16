---
name: continue-project
description: Inspect canonical Agent Commons project state, resolve an optional requirement, specification, dashboard reference, or safe project-local path, and perform or recommend the next lifecycle step. Use when resuming an initialized project, asking what comes next, or continuing a specific delivery object. Do not use to bypass approval, specification, source protection, dependency ordering, or bounded implementation ownership.
---

# Continue an Agent Commons project

Resume from canonical state instead of reconstructing the workflow from memory.

## Resolve context and next action

1. Read project governance, `.agent-commons.yaml`, Git state, protected source boundaries, and L0 plus the
   `.agent-commons/memory/index.json` status when enabled. Load only the domain/entity context required by
   the next action. Verify memory against canonical structured state; treat a generated dashboard as a
   projection, never the source of lifecycle truth.
2. Run `scripts/resolve_project_continuation.py --root <project>` with an optional stable ID or safe
   project-local path. Stable requirement and specification IDs are the normal interface; paths are a
   debugging and tooling fallback.
3. Confirm that the resolved object, lifecycle status, dependencies, approval, ownership, and blockers
   match the underlying requirement, OpenSpec, implementation, test, and evidence records.
4. If one required action is unambiguous, invoke the named canonical capability with its resolved subject.
   If the resolver returns choices, present them concisely and do not choose when priority or dependency
   order remains genuinely ambiguous.

The resolver returns a stable capability reference and whether that ID is selected in the project manifest;
it does not execute the capability. `.agent-commons.yaml` is project-specific composition and lifecycle
configuration, not native runtime configuration. The active runtime resolves the returned ID to the installed
canonical Commons skill, then that skill reads the local governance and state required for its own workflow.

## Lifecycle routing

- Missing legacy inventory or analysis routes to `analyze-legacy-system`, which owns the configured
  evidence-first analysis lifecycle.
- Completed analysis with incomplete requirements routes to `derive-modernization-requirements`.
- Approved requirements without required specifications route to `specify-openspec-change`.
- A specification with readiness gaps routes to `review-openspec-change`.
- A ready specification routes to `implement-openspec-change`; a requirement reference routes through
  `implement-ready-slice` only after its linked specification contract is resolved.
- Implemented behavior whose tests pass but whose test quality is unresolved routes to `mutation-testing`,
  and unresolved meaningful surviving mutants route back to test hardening. Green implementation with critical
  survivors outstanding is not complete; the next action is to strengthen those tests, not to report the
  implementation as done.
- Implemented behavior with a resolved mutation quality status but no verification routes to
  `verify-openspec-implementation`.
- A current lifecycle reports no required action and may offer optional review, dashboard refresh, or
  planning without inventing work.

Never replace these capabilities with embedded analysis, specification, implementation, TDD, mutation,
validation, or dashboard logic. This skill owns orchestration and blocker-aware handoff only.

## Scoped and batch continuation

Accept a stable ID, `requirement REQ-023`, `specification SPEC-007`, a dashboard object reference, or a safe
relative/absolute project-local path. Reject paths outside the project and ambiguous matches.

Batch mode requires an explicit request such as implementing all ready specifications or a named requirement
range. Resolve the full specification set, dependency-order it, and use bounded concurrency only when write
ownership, mutable schemas/contracts, runtime resources, and integration order are independent. Otherwise
serialize. Do not enter batch implementation merely because several items are ready.

## Blockers and synchronization

Stop before downstream work when requirements are unresolved, specifications are incomplete, external
dependencies are blocked, source authority is missing, or the writable target is unclear. Distinguish
unrelated baseline test failures from new failures, and distinguish a mutation result blocked by an unstable
baseline from a genuine test-quality gap.

After a delegated step, update canonical project state through its owning deterministic helper, regenerate
the living dashboard when selected, and verify that the displayed next action matches the structured state.
Merge the validated project-memory delta and checkpoint only after canonical state is current. Never
hand-edit generated HTML or use a dashboard control or memory record to mutate lifecycle truth.
