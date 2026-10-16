---
name: derive-modernization-requirements
description: Convert legacy behavior, documents, interfaces, and architecture evidence into deduplicated modernization requirements with acceptance criteria, provenance, confidence, gaps, and lifecycle state. Use after bounded evidence analysis to define or reconcile target behavior. Do not use to summarize source architecture, generate requirements from memory alone, or relabel recommendations as observed facts.
---

# Derive modernization requirements

Preserve the distinction between observed legacy behavior and proposed target behavior.

## Evidence model

For each material claim record source artifact, hash/version, exact coordinate, factual observation,
interpretation when needed, authority, confidence, and reciprocal links. Use
`references/evidence-contract.md` and the synthetic templates in `assets/`.

## Workflow

1. Define the capability, actor, trigger, boundary, and migration intent.
2. Build a bounded context package from relevant analysis domains and entities, then gather the smallest
   authoritative evidence packet from source code, contracts, data, tests, official documents, or validated
   runtime observations. Memory and generated dashboards are not original evidence.
3. Extract preconditions, inputs, validations, decisions, state changes, outputs, side effects,
   integrations, persistence, errors, audit behavior, and non-functional constraints.
4. Classify each statement as `observed`, `inferred`, `proposed`, `target-state`, `assumption`, `conflict`,
   or `unknown`. Never relabel a recommendation as current fact.
5. Deduplicate by behavior and observable outcome, not wording. Preserve conflicting sources and record
   the reconciliation decision or open question.
6. Create stable requirements with rationale, evidence links, acceptance scenarios, dependencies,
   exclusions, migration/parity expectation, confidence, approval state, and a revision token or content
   fingerprint that changes when the approved behavior changes.
7. Add reciprocal links among source, evidence, rule, gap, requirement, downstream specification, and test
   planning. Keep requirement approval separate from specification, implementation, and validation status.
8. Run readiness checks. Requirements with unresolved authority, missing acceptance criteria, or hard
   decisions remain blocked rather than being made implementation-ready.

## Parallel candidate extraction and canonical fan-in

For a large system with two or more sealed, non-overlapping evidence packets, bounded workers may extract
requirement candidates concurrently. Each worker receives exact evidence IDs and fingerprints, one domain or
capability boundary, an isolated output path, and the candidate contract in
`references/requirements-candidate-contract.md`. Workers use temporary IDs only. They do not allocate
canonical requirement IDs, approve behavior, mutate the requirements registry, resolve cross-domain
conflicts, or update dashboards.

The coordinator validates every returned packet against its input fingerprint before fan-in. Then one
canonical synthesis step groups candidates by observable behavior, reconciles overlap and conflict, records
rejections or supersession, assigns stable requirement IDs and revisions, and creates reciprocal evidence
links. Validate each accepted domain incrementally, but do not publish canonical totals or readiness until
cross-domain dependencies and duplicates have been reconciled. Small or tightly coupled scopes stay
single-threaded.

When called from a `FULL` legacy analysis, candidate extraction is not a user-facing completion boundary.
Continue until every selected analysis packet has a recorded candidate disposition and the system-level fan-in
is complete; do not stop after the first language, program family, or flow packet.

## Specification handoff

When implementation or migration preparation is in scope, export the approved requirements as structured
records that `specify-openspec-change` can consume. Include stable ID, current revision, behavior, constraints,
acceptance scenarios, dependencies, exclusions, evidence IDs, confidence, approval state, and open questions.
Do not create OpenSpec artifacts here and do not assume a one-to-one requirement/specification mapping.

For analysis-only work, the workflow may stop at requirements plus a living dashboard. Record that
specification generation is out of scope rather than treating every approved requirement as unspecified work.

## Completion

Complete the bounded scope only when every requirement has evidence or an explicit proposal rationale,
every evidence location resolves, duplicates/conflicts have outcomes, unknowns remain visible, and totals
reconcile with the analyzed inventory. When a downstream specification exists, its relationship points to
the exact requirement revision it consumed. Generated views must not mutate lifecycle state.
After canonical requirements and reciprocal evidence links validate, merge only their stable IDs, revisions,
status, dependencies, unknowns, and canonical paths into project memory and record `REQUIREMENTS_COMPLETE`.
