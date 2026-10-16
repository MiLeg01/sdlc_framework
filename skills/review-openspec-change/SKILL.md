---
name: review-openspec-change
description: Review and refine an existing OpenSpec change for implementation readiness, resolving scope, ambiguity, acceptance, delta correctness, design, tasks, and validation before code changes. Use after a change exists and before implementation approval. Do not use to create duplicate changes, implement code, certify completed implementation, or approve unresolved product decisions by assumption.
---

# Review an OpenSpec change for readiness

Treat this as the pre-implementation gate. Read the existing change rather than drafting a replacement.

## Establish current state

Use a bounded context package for the selected change, linked requirements, architecture decisions, affected
components, and prior findings. Canonical OpenSpec files and requirements remain authoritative.

1. Resolve the exact change. When several changes are active, do not guess; use conversation context or ask
   for selection.
2. Read project governance, `openspec/config.yaml`, relevant main specs, the change metadata, all existing
   artifacts, related source boundaries, and any prior review decisions.
3. Run `openspec status --change <name> --json`, `openspec show <name> --json`, and
   `openspec validate <name> --strict --no-interactive` when supported by the installed version.
4. Confirm the change is the one already approved or under review. Reuse it instead of starting another.

## Review the specification contract

Check and distinguish:

- intent, scope, non-goals, users, and affected behavior;
- ADDED, MODIFIED, and REMOVED deltas against the current main specs;
- observable requirements and concrete scenarios, including material negative and boundary cases;
- behavior requirements versus technical design choices;
- design consistency with the proposal and known repository constraints;
- tasks that cover every scenario, relevant tests, migration, documentation, and rollout or recovery;
- explicit `skip_specs: true` only when no behavior change is intended and no delta spec exists;
- unresolved decisions, conflicts, dependencies, and assumptions that would cause implementation drift.

For a bug fix, require a precise corrected-behavior scenario suitable for a regression test. For a pure
refactor, require preservation checks instead of invented functional requirements. Scale the review to risk:
a small contained change may have short artifacts, while cross-team, contract, migration, security, or
ambiguous changes need fuller scenarios and design evidence.

## Refine without crossing the gate

Refine planning artifacts only when the requested intent authorizes the edit. If the correction changes
intent materially, recommend a new change rather than disguising different work as refinement. Keep proposal,
specs, design, and tasks coherent in both directions, then re-run status and strict validation.

Do not implement code. Do not declare readiness while a material requirement, scenario, dependency, or
decision remains ambiguous. Structural validation cannot resolve product authority.

## Return a readiness decision

Return `READY`, `READY_WITH_LIMITATIONS`, or `NOT_READY` with:

- change identity and artifact status;
- requirement/scenario-to-task and intended-test coverage;
- validation command and result;
- resolved refinements, remaining decisions, and limitations;
- the exact approval or next correction required before implementation.
