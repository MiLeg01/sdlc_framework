---
name: plan-work
description: Turn an approved objective and current repository evidence into a bounded, dependency-aware, executable plan with goals, non-goals, assumptions, acceptance criteria, ownership, milestones, validation, risks, checkpoints, and recovery. Use before substantial implementation or when sequencing and handoff matter. Do not use for a trivial one-step edit, to invent unresolved product decisions, or to treat a plan as evidence that work is complete.
---

# Plan executable work

Inspect current source, tests, decisions, governance, Git state, active ownership, dependencies, and prior
validation before planning. Ask only for choices that cannot be discovered and would materially change scope.

## Define the contract

Record the objective, users or consumers, observable acceptance, non-goals, protected paths, assumptions,
unknowns, decisions needed, constraints, and source evidence. Mark unresolved authority as a blocker rather
than filling it with a recommendation.

## Decompose

Create the smallest coherent milestones and tasks that produce valid intermediate states. For each task,
record:

- outcome and acceptance criterion;
- evidence or decision that authorizes it;
- dependencies and prerequisite state;
- exclusive file, component, data, or environment ownership;
- implementation boundary and explicit exclusions;
- validation command or observable check;
- risks, rollback or recovery, and handoff output.

Order tasks by dependencies and risk retirement. Separate discovery, decision, implementation, migration,
verification, and external coordination. Parallelize only independent ownership with coordinator-controlled
integration.

## Validate the plan

Walk the plan forward from current state and backward from acceptance. Confirm every acceptance criterion has
an implementation and verification path, every task has an owner and completion signal, and no milestone
requires unavailable authority. Include an early valid artifact and small recoverable batches for long work.

Return a concise plan, dependency map, assumptions and conflicts, validation matrix, recovery points, and one
exact first action. Update the plan when evidence or scope changes; never report planned work as completed work.
