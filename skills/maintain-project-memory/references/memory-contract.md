# Project-memory contract

## Source-of-truth hierarchy

`SOURCE / INPUT -> CANONICAL STRUCTURED ANALYSIS -> REQUIREMENTS / SPECIFICATIONS -> PROJECT MEMORY / INDEX -> GENERATED VIEWS`

Memory is a retrieval and operational state layer. It never outranks the evidence or canonical records it
indexes. Dashboards and presentations consume compact memory to locate canonical state; they do not turn
memory into a second truth store.

## Storage layout

```text
.agent-commons/
`-- memory/
    |-- index.json
    |-- state.json
    |-- project-summary.md
    |-- source-state.json
    |-- decisions.json
    |-- terminology.json
    |-- domains/<domain>.json
    |-- entities/<stable-id>.json
    `-- checkpoints/<checkpoint-id>.json
```

Do not create one growing `memory.md`. Keep L0 small enough to load by default, L1 bounded by domain, and L2
bounded by stable entity/component/flow/rule IDs. Original source, canonical reports, requirements, and
specifications stay in their normal project locations.

## L0 project synopsis

Record only goal, project mode, source roots, protected paths, target technology, discovered languages,
high-level architecture, lifecycle stage, major decision IDs, critical blockers, and one next action.
`project-summary.md` is generated from `state.json`; rebuild it from structured state rather than from an older
summary.

## L1 and L2 records

Domain records summarize a relevant domain and list L2 stable IDs. An L2 record contains:

- stable record ID, layer, domain, entity ID/type, and compact statement;
- confidence: `VERIFIED`, `INFERRED`, `UNKNOWN`, `STALE`, or `CONFLICTING`;
- status, canonical references, evidence paths/coordinates/hashes, relationships, and tags;
- preserved variants when confidence is `CONFLICTING`.

COBOL, PL/I, Java, contracts, data, integrations, runtime/build, business rules, requirements, modernization,
estimation, and delivery are example domains, not a fixed list. Entity types may include program, class,
module, service, endpoint, transaction, copybook, table, interface, batch job, business flow, requirement,
specification, implementation slice, or validation result.

## Proposals and merge ownership

Only the coordinator writes canonical memory. Workers return a versioned proposal with a validated producer,
domain summaries, records, and an optional checkpoint. The deterministic merger rejects unvalidated packets,
unsafe paths, malformed hashes, and dangling internal relationships. Identical records deduplicate. Two
different claims under one stable ID become `CONFLICTING` variants; neither is silently overwritten.

Writes use a project-local lock and atomic replacement. A worker must not allocate shared IDs, compact the
store, or change global memory state.

## Retrieval and context budget

A context request identifies a task, relevant domains, entity IDs, dependency depth, and a maximum record
count. The package always includes L0, then selected L1/L2 records and relationship dependencies. It reports
included, omitted-relevant, irrelevant, stale, and conflicting IDs plus measured package bytes. An omitted
relevant record is a visible budget decision, never silent truncation.

## Invalidation and confidence

Compare evidence hashes with the current deterministic source inventory. Mark directly changed records
`STALE`, retain their prior confidence, and propagate invalidation through recorded dependencies. Do not
discard unaffected memory because one source changed. Summary or repetition never upgrades `INFERRED` or
`UNKNOWN` to `VERIFIED`.

## Validation

Validation checks JSON parsing, index hashes, safe project-local paths, evidence/canonical path existence,
current evidence hashes, stable IDs, domain membership, relationship targets, conflict variants, and stale
state. Exact runtime token counts and elapsed time are recorded only when the runtime exposes them; otherwise
use byte counts, record counts, repeated file reads, and inventory reuse without fake precision.
