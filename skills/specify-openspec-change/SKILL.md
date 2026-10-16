---
name: specify-openspec-change
description: Create or refine one OpenSpec change so intended behavior, scope, acceptance scenarios, design, and implementation tasks are agreed before code changes. Use for features, behavioral bug fixes, consequential technical changes, and explicitly OpenSpec-managed work. Do not use for implementation, post-hoc specification of finished code, research or presentation work, or a trivial edit that does not justify durable change state.
---

# Specify an OpenSpec change

OpenSpec defines intended software behavior before implementation. Keep canonical Commons guidance here
and all proposals, specs, designs, tasks, configuration, and archive state inside the active project.

## Resolve the change boundary

Load only the selected requirement revisions, linked evidence, architecture decisions, affected components,
dependencies, unknowns, and existing specification state through a bounded project-memory context package.
Verify those pointers against canonical requirements and OpenSpec before authoring.

1. Read project governance, Git state, current `openspec/config.yaml`, main specs, active changes, and the
   requested outcome. Use `openspec list --json` and `openspec status --change <name> --json` when available.
2. Reuse an active change when its intent and scope match. Do not create a second proposal for the same work.
3. If intent is unclear, explore and clarify before creating artifacts. Do not convert guesses into approved
   requirements.
4. If OpenSpec is not initialized, report that boundary and use the official project initialization flow
   before authoring project-local OpenSpec state.
5. Choose the lightest valid treatment:
   - feature or behavior change: proposal plus delta specs with observable scenarios, then design and tasks;
   - bug fix: describe the correct behavior and add or modify a regression scenario;
   - pure refactor, tooling, or documentation change with no intended behavior change: state that invariant,
     use `skip_specs: true`, and do not invent functional requirements;
   - tiny low-risk edit: bypass durable OpenSpec ceremony unless governance or the user explicitly requires it.

When approved requirements already exist, read
`references/requirements-to-openspec.md` and treat them as the behavioral source for the change. Do not merely
rename each requirement into a spec.

## Build coherent artifacts

Follow the project's selected OpenSpec schema rather than assuming every project uses the default. For the
official `spec-driven` schema, keep responsibilities distinct:

- `proposal.md`: intent, problem, scope, non-goals, affected capabilities, and approach;
- `specs/`: ADDED, MODIFIED, or REMOVED behavior requirements with concrete scenarios;
- `design.md`: technical approach, decisions, risks, migration or rollback considerations;
- `tasks.md`: small ordered implementation and validation steps with checkboxes.

Use the project's OpenSpec-generated workflow or `openspec instructions <artifact> --change <name> --json`
to obtain current instructions and dependencies. Use `openspec status` to determine what is ready rather than
hard-coding an artifact order for a customized schema.

Write requirements as observable behavior, not class names or implementation steps. Give each material
requirement at least one testable scenario and include negative, boundary, compatibility, security, or
failure scenarios where risk warrants them. Keep implementation choices in design and task artifacts.

For requirement-driven work, group and split behavior according to implementation coherence. Support one
requirement feeding several specs and several requirements feeding one spec. Record every source requirement
ID plus the revision or fingerprint consumed by the OpenSpec change. Block readiness when an approved
requirement is ambiguous, conflicts with another requirement, or lacks authority needed for an
implementation-facing contract.

## Parallel specification ownership

When approved requirements form independent implementation domains, the coordinator may prepare several
OpenSpec changes concurrently. Before dispatch, the coordinator reserves every change ID and scenario-ID
namespace, assigns exactly one worker to each `openspec/changes/<change-id>/` directory, records the exact
requirement revisions consumed, and declares affected main-spec capabilities as mutable shared surfaces.
Workers treat `openspec/config.yaml`, main specs, other active changes, canonical requirement state, and
archive state as read-only context.

Do not parallelize two workers that modify the same active change, allocate overlapping IDs, resolve the same
behavioral decision, or target the same mutable main-spec surface without serialization. Each worker runs
strict validation for its own change and returns an isolated artifact manifest. The coordinator then performs
one fan-in review for duplicate behavior, terminology, cross-change dependencies, scenario coverage, and
requirement-revision staleness before any change becomes implementation-ready.

## Establish lightweight traceability

Preserve stable requirement IDs, specification/change IDs, acceptance-criterion or scenario IDs, and task
numbers. Before implementation, make it possible to map requirement revision -> specification -> acceptance
criterion -> task -> intended test. Use a compact relationship export or table only when the existing
artifacts do not already make the links clear; do not create a separate requirements-management system.

## Validate and hand off

After the specification validates and readiness state is canonical, merge its stable ID, requirement
revisions, dependencies, status, path, and next action into project memory; do not copy full delta specs.

Run `openspec validate <change> --strict --no-interactive` and inspect the artifacts semantically. Structural
success is not approval. Return the change name, artifact status, scope, unresolved decisions, acceptance
scenarios, task readiness, and validation result. Stop before implementation until the change is approved.

If code already exists, do not write a retrospective specification unless the user explicitly requests
reverse engineering or documentation. Label that exceptional direction clearly.
