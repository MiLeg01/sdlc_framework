---
name: coordinate-parallel-agents
description: Coordinate two or more bounded agents through mutually exclusive ownership, isolated outputs, explicit dependencies, structured handoffs, coordinator-only integration, validation, recovery, and concurrency limits. Use when independent work can materially reduce elapsed time. Do not use for overlapping edits, canonical-state decisions, tiny work, or runtime-specific orchestration syntax.
---

# Coordinate bounded parallel agents

Confirm that parallel work is authorized, useful, and separable. The coordinator owns scope, shared state,
global identifiers, dependency decisions, integration order, validation, progress, recovery, and completion.

## Build the execution graph

Before dispatch, express each task with a stable ID, dependencies, exact writable paths, mutable shared
surfaces, and an observable completion signal. Mutable shared surfaces include canonical registries, schemas,
main specifications, lockfiles, database migrations, shared fixtures, generated global views, and external
state even when workers would edit different files.

Use the repository `tools/plan_parallel_execution.py` helper with the contract in
`references/execution-plan-contract.md` when a structured plan is available. It rejects cycles and unsafe
paths, detects nested write-path and shared-surface conflicts, applies the requested concurrency bound, and
returns serialized execution stages. The plan is scheduling evidence, not authorization to perform a task.

## Partition before dispatch

1. Establish the complete eligible denominator and protected or coordinator-owned surfaces.
2. Partition by independent files, components, evidence batches, scenarios, or other stable boundaries. Give
   every eligible item exactly one primary owner and record contextual dependencies separately.
3. Reject partitions that overlap writes, allocate shared identifiers, mutate the same schema, resolve the
   same decision, or depend on uncommitted output from one another.
4. Set a bounded concurrency limit based on task independence, tool capacity, review load, and integration
   cost. More workers are not automatically faster.
5. Give each worker the contract in `references/worker-contract.md`, relevant evidence, allowed paths,
   prohibited actions, validation commands, one isolated output location, and a bounded task-specific context
   package. Never give every worker the complete project history when L0 plus selected L1/L2 records suffice.
6. For concurrent writable work, require separate worktrees, branches, task directories, or an equivalent
   coordinator-verified isolation boundary. Disjoint declared paths do not make one shared Git index, build
   cache, database, service port, or generated output safe.

## Monitor and recover

Track dispatched, active, needs-attention, completed, validated, integrated, and superseded states. A worker
must surface missing authority, stale inputs, overlap, failed validation, and skipped scope rather than
guessing. If orchestration fails, retain the deterministic partition and execute the same batch sequentially.

## Integrate centrally

Validate ownership, input fingerprints, completeness, schema, evidence, exclusions, and worker checks before
accepting output. Integrate one batch at a time in dependency order. Reconcile duplicates and conflicts,
allocate canonical IDs centrally, run shared gates after integration, and record rejected or superseded
proposals. Workers do not certify overall completeness.

Validate incrementally after each stage: verify worker input fingerprints and owned outputs, integrate the
smallest accepted unit, run its focused gate, and only then release dependent tasks. Run cross-cutting and
repository-wide gates after all required fan-in stages. If an input, ownership declaration, or shared surface
drifts, invalidate the affected downstream stages and re-plan rather than continuing against stale work.

Do not parallelize shared-state transitions, canonical registry edits, conflict resolution, release approval,
progress truth, generated global views, commits, or destructive operations unless the runtime provides an
explicitly isolated and coordinator-verified transaction boundary.
