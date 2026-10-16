---
name: implement-openspec-change
description: Implement one approved OpenSpec change task by task with scenario traceability, tests, and controlled artifact updates when learning invalidates the plan. Use when a specific existing change is implementation-ready and writable. Do not use for unapproved or ambiguous changes, speculative implementation before specs, bulk unrelated work, or silent divergence from the accepted specification.
---

# Implement an approved OpenSpec change

Specification and acceptance criteria precede implementation. Work from one existing approved change; do
not create a replacement proposal during implementation.

## Bind the implementation contract

Retrieve only the selected specification, linked requirement revisions and scenarios, architecture decisions,
affected components, dependency records, and necessary source/target paths. Do not load the entire analysis
history for each implementation slice.

1. Resolve the supplied stable specification ID, dashboard reference, or safe project-local OpenSpec path
   to exactly one existing change. Load its linked requirements, acceptance criteria, dependency graph,
   source evidence, implementation state, and validation commands. Reject path escapes and ambiguous IDs.
2. Read governance, Git state, OpenSpec project configuration, main specs, the selected change, current
   artifacts, source, tests, and validation commands.
3. Confirm the exact active change and approval state. Run `openspec status --change <name> --json` and obtain
   current apply guidance with `openspec instructions apply --change <name> --json` when available.
4. Refuse implementation if required artifacts, acceptance scenarios, dependencies, ownership, or a runnable
   validation path are missing. A structurally valid change can still be semantically unready.
5. Preserve unrelated work and keep project-local OpenSpec state in the project.

## Implement in traceable slices

Work through the approved `tasks.md` in dependency order. Use `implement-ready-slice` to claim and hand off
each material vertical slice; this skill retains change-level progress and mismatch handling. For each
bounded slice:

1. identify the authorizing requirement and scenario;
2. select the narrowest credible test or observable verification;
3. follow `test-driven-development` for behavior changes when a runnable RED state is available, unless the
   project manifest or user explicitly records an alternative implementation method; never claim TDD when
   that override is active;
4. implement only the behavior and design authorized by the change;
5. run the focused and related gates;
6. mark a task complete only after its behavior is implemented and validated;
7. retain a lightweight link among requirement, scenario, task number, implementation path, test path,
   command, and result.

Before concurrent slice dispatch, construct a dependency and ownership plan. Each slice declares exact
writable paths and mutable shared surfaces, including manifests, schemas, migrations, generated contracts,
shared fixtures, external services, and OpenSpec task state. Parallel slices require isolated worktrees or an
equivalent transaction boundary, a common verified base revision, exclusive claims, and separate runtime
resources. Workers do not edit `tasks.md` or other canonical change state; they return evidence for the
change coordinator to integrate.

After each slice returns, validate its input revision, diff boundary, focused test, related gate, and trace
links before merging it and releasing dependants. Re-run affected tests after every merge. Repository-wide
tests, strict OpenSpec validation, task-state updates, and completion claims occur only after all required
slices have been integrated into one snapshot.

For a bug fix, make the corrected-behavior scenario executable as a regression test where practical.
For a pure refactor marked `skip_specs: true`, preserve existing behavior and validate structural intent
without inventing new behavior.

## Handle learning without divergence

If implementation reveals that a requirement, scenario, design, or task is wrong or ambiguous:

1. stop the affected implementation slice;
2. record the mismatch and evidence;
3. clarify authority and update the existing OpenSpec artifacts through the project's update workflow;
4. re-run strict OpenSpec validation and obtain approval for material behavior or scope changes;
5. resume only against the corrected specification.

Never silently make code disagree with the approved change. Start a new OpenSpec change when intent changed,
scope expanded into distinct work, or the original can be completed without the new work.

## Hand off for verification

After canonical implementation and test state is updated, merge the slice status, changed paths, validation
evidence pointers, and next action into project memory and checkpoint `IMPLEMENTATION_SLICE_COMPLETE`.

Run the repository's required tests and `openspec validate <name> --strict --no-interactive`. Report completed
and remaining tasks, scenario coverage, implementation and test links, artifact updates, mismatches resolved,
validation results, and limitations. Do not archive; hand the completed implementation to
`verify-openspec-implementation`.
