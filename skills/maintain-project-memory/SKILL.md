---
name: maintain-project-memory
description: Create, retrieve, validate, checkpoint, invalidate, compact, and rebuild hierarchical evidence-backed project knowledge for substantial multi-session work. Use automatically when recovery cost, repeated analysis, or coordinated workflows justify durable context. Do not use for tiny tasks, hidden reasoning, a second source of truth, or replacement of canonical evidence, requirements, specifications, code, or tests.
---

# Maintain project memory

Externalize verified project knowledge so agents can resume complex work without replaying the conversation or
reloading the complete repository. Memory optimizes retrieval, not reasoning depth.

## Authority and storage

Use this authority order: source/input and current runtime evidence; canonical structured analysis;
requirements and specifications; project memory/index; generated dashboard or presentation; chat recollection.
When memory conflicts with a higher source, mark it `STALE` or `CONFLICTING` and refresh it.

Keep machine-owned memory under `.agent-commons/memory/`, never a top-level `memory/`. Read
`references/memory-contract.md` before changing the format. The hierarchy is:

- L0: `state.json` plus a generated tiny `project-summary.md`, loaded for most substantial tasks;
- L1: `domains/<domain>.json`, loaded only for relevant technologies or work domains;
- L2: `entities/<stable-id>.json`, loaded for selected components, flows, rules, data, or delivery objects;
- EVIDENCE: project-local canonical paths, stable IDs, coordinates, hashes, and revisions retained by reference.

Never store chain-of-thought, conversations, secrets, credentials, private raw logs, copied source bodies, or
unsupported conclusions. Store facts, decisions by canonical link, state, relationships, confidence, unknowns,
conflicts, and evidence pointers.

## Automatic read-before-work

For a substantial workflow, inspect L0 and the memory index before expensive work. Check whether relevant
records exist, whether their source fingerprints remain current, and which domains/entities the task needs.
Build a bounded package with `scripts/manage_project_memory.py read`; load source directly only for new,
stale, conflicting, unknown, or verification-sensitive areas.

Classify requested context as mandatory, useful, or irrelevant. Prefer the minimum sufficient verified
context. Do not truncate evidence needed for correctness merely to hit a budget.

## Controlled updates and checkpoints

Workers never rewrite shared memory. They return one validated proposal with stable IDs, canonical references,
evidence pointers, confidence, relationships, and their input fingerprint. A coordinator runs
`scripts/manage_project_memory.py update`, which locks the store, validates the proposal, writes atomically,
deduplicates identical facts, and preserves incompatible variants as `CONFLICTING` for synthesis.

Where mutation testing applies, keep only compact test-quality state: last run date, scope, tool, mutation
score and status, meaningful and critical survivor counts, accepted equivalent mutants, the accepted baseline
and its comparison verdict, and unresolved test gaps with their requirement or specification IDs. Reference the
raw mutation report by path or artifact ID. Never place a full mutation report, per-mutant detail, or tool log
in hot memory.

After a material phase, write a validated checkpoint such as `INITIALIZATION_COMPLETE`, `INVENTORY_COMPLETE`,
`LANGUAGE_ANALYSIS_COMPLETE`, `SYSTEM_SYNTHESIS_COMPLETE`, `REQUIREMENTS_COMPLETE`,
`SPECIFICATIONS_COMPLETE`, `IMPLEMENTATION_SLICE_COMPLETE`, `TEST_QUALITY_VALIDATED`, or
`VALIDATION_COMPLETE`. Checkpoints point to
canonical artifacts; they do not duplicate them. When histories overlap, compose from the earliest valid
checkpoint and merge later verified deltas rather than creating a second memory timeline.

## Source drift, compaction, and rebuild

Run `invalidate` against the current deterministic inventory. Direct hash changes mark affected records
`STALE`; relationship propagation invalidates dependent knowledge without discarding unrelated domains.

Run `compact` to deduplicate indexes and regenerate HOT state without deleting L2 records or evidence. Run
`rebuild` to regenerate L0/L1 views from canonical structured records rather than repeatedly summarizing prior
summaries. Run `validate` before handoff or completion to check parseability, hashes, paths, stable IDs,
relationships, conflicts, and stale/current consistency.

## Manual operations

Normal workflows call the manager automatically. Manual use is appropriate to inspect, refresh, compact,
validate, or rebuild memory. The portable lifecycle is `create`, `read`, `update`, `invalidate`, `compact`,
`rebuild`, and `validate`; `benchmark` reports measured UTF-8 bytes and never invents token precision.

## Completion

A fresh runtime session must be able to load L0, see current checkpoints, stale/conflicting records, blockers,
protected paths, and one exact next action; then retrieve only the domains and entities required for that action.
