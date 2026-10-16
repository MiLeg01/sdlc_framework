---
name: analyze-legacy-system
description: Orchestrate complete configured evidence-first legacy analysis by default, using inventory-backed bounded slices, safe parallel fan-out, cross-system synthesis, requirements, selected OpenSpec preparation, dashboard refresh, and a hard coverage gate. Use as the high-level entry point for initialized legacy projects; use bounded mode only when the user explicitly limits scope. Do not use for target-state invention, implementation, or analysis based only on filenames, comments, or memory.
---

# Analyze a legacy system

Reconstruct observable behavior from exact source evidence. This skill is the system-level coordinator. A
bounded slice is an internal execution unit, not the default completion boundary.

## Enter from an initialized project

The user invokes the stable canonical capability ID through the active runtime; `.agent-commons.yaml` does
not execute automatically and is not native runtime configuration. Before planning analysis, read the
project-local `AGENTS.md`, `.agent-commons.yaml`, canonical structured state, protected source boundaries,
and the minimum relevant project memory. Treat the skill body as the orchestration contract and the manifest
as project-specific configuration for scope, selected capabilities, constraints, methodology, outputs, and
the current next action. Keep all source evidence and lifecycle state inside the project.

## Resolve mode and complete scope

Read project governance, `.agent-commons.yaml`, canonical state, source-authority rules, protected paths, and
the user request. When project memory is enabled, load L0 and the index first, validate the current inventory
fingerprint, reuse unchanged validated slices, and retrieve only the domains/entities needed for stale or
missing work. Read `references/full-analysis-contract.md`.

- `FULL` is the default when the user invokes this skill without an explicit limitation. Resolve every
  configured source root and analyze all eligible in-scope artifacts.
- `BOUNDED` is permitted only when the user explicitly names a subset, path, component, technology, flow,
  or entry point. Report bounded completion without implying system completion.
- `CONTINUE` resumes an interrupted `FULL` or `BOUNDED` run from validated checkpoint state. Reuse unchanged
  inventory, slices, and downstream stages; invalidate source-hash or input-fingerprint drift.

Do not reinterpret “first program found,” a single entry point, or the first completed worker packet as the
configured scope. Do not require confirmation between independent slices.

## Keep reference applications outside target truth

When project configuration explicitly supplies a separate reference application, architecture exemplar, or
company pattern profile, read `references/reference-applications.md`. Treat it only as a discovery prior that
can determine where to look first. Keep its observations in a distinct `REFERENCE_PATTERN` profile with its
own provenance and fingerprint; never copy them into target evidence, dependencies, requirements, capabilities,
metrics, confidence, or completeness.

Record both matches and non-matches against direct target evidence. A resemblance remains an inference until
the target supports it, a target contradiction overrides the prior, and an absent target match remains
unresolved. Projects without an explicitly configured reference profile continue with target evidence alone.

## Establish one denominator and coordinator state

1. If the source inventory is missing, stale, incomplete, or does not cover every authorized root, delegate
   once to `inventory-codebase`. Validate its hashes, failures, exclusions, fingerprint, and non-overlapping
   ownership before interpretation.
2. Run `scripts/coordinate_analysis.py plan` with the resolved semantic mode, inventory, configured
   requirements/OpenSpec/dashboard policy, and a concurrency bound normally between three and six for a
   mixed system. Use fewer workers for a tiny or tightly coupled scope.
3. Treat the emitted coverage register, coverage-plus-depth gate, slice input fingerprints over primary and
   contextual dependencies, bounded context-package requests, DAG, execution stages, ownership, and
   lifecycle status as canonical progress state. Do not let workers rescan the entire repository or maintain
   competing inventories.
4. Give every discovered artifact exactly one coverage record. No relevant source may disappear between
   inventory, analysis, synthesis, requirements, specifications, dashboard, and completion reporting.

## Execute bounded slices

Partition by evidenced technology, subsystem, runtime, domain, flow family, or shared data boundary. Do not
launch one worker per file. Read `references/cobol-and-pli.md`, `references/legacy-java.md`, or
`references/contracts-data-and-batch.md` only for technologies present in the assigned slice. When COBOL,
Java, or SQL structure must be enumerated, read `references/deterministic-extraction.md` and run
`scripts/extract_legacy_structure.py`; lexical output is navigation evidence, not semantic truth.

For two or more independent slices, use `coordinate-parallel-agents`. Each worker receives the exact primary
artifact IDs and hashes, bounded contextual dependencies, one isolated output path, the evidence schema,
validation command, and prohibited shared surfaces. Workers may trace assigned behavior but must not edit
canonical coverage, requirements, OpenSpec state, dashboard HTML, lifecycle state, Git staging, or commits.

For each slice:

1. establish triggers, actors/systems, inputs, guards, authorization, variants, and configuration;
2. follow resolved calls and retain unresolved or dynamic edges with exact coordinates;
3. trace data lineage, rules, decisions, state changes, persistence, integrations, outputs, audit effects,
   errors, retry, and recovery;
4. distinguish reachable behavior, support artifacts, duplicate variants, generated/test/dead code,
   conflicts, assumptions, and unknowns;
5. return one validated packet that explicitly accounts for every primary artifact assigned to the slice.

An executable artifact is not `ANALYZED` from an evidence ID alone. The packet must classify depth, validate
structure, behavior, data, dependencies, business rules, interfaces, error handling, non-functional behavior,
maintainability, and migration significance or explain non-applicability; record semantic counts, unknowns,
defect candidates, and complexity entries whose basis is `MEASURED` or `ASSESSED`.

Integrate each packet centrally with `scripts/coordinate_analysis.py record`. Reject stale fingerprints,
missing artifact dispositions, unresolved evidence coordinates, or incomplete worker validation.
After integration, merge the validated structured delta through `maintain-project-memory`; workers never
write shared memory directly.

## Mandatory fan-in

After all required slices are validated, perform one cross-system synthesis. Reconcile equivalent and
different behavior across languages and variants, Java/API and requester relationships, shared schemas and
copy/includes, boundary contracts, request/response mappings, calls, integrations, defects, conflicts, and
current-versus-target implications. Do not concatenate worker reports and call it synthesis.

When requirements are selected, give sealed analysis/evidence packets to
`derive-modernization-requirements`. Candidate extraction may be parallel, but canonical synthesis is
serialized: deduplicate by observable behavior, resolve conflicts, allocate stable IDs/revisions centrally,
and create reciprocal evidence links. Do not publish per-language duplicate requirements as system totals.

When the configured project mode requires specifications, hand approved canonical requirements to
`specify-openspec-change` and `review-openspec-change` after requirement synthesis. Independent specification
clusters may be prepared concurrently only with exclusive OpenSpec ownership. Preserve
`SOURCE -> EVIDENCE -> REQUIREMENT -> SPECIFICATION` traceability and do not begin implementation.

## Dashboard ownership and progress

One dashboard renderer consumes canonical structured state after integration. Analysis workers never rewrite
`dashboard/index.html`. Refresh the existing canonical dashboard product through `build-living-dashboard`;
represent full-system scope, progress, components, technologies, flows, requirements, specifications,
architecture, risks, traceability, evidence, and the actual next action. A partial run must visibly say
analysis is in progress and must not present the first slice as the system overview.

Every language or technology worker contributes only its structured portion of the shared dashboard model:
deterministic composition and counts, technology-specific inventory, complexity with a `MEASURED` or
`ASSESSED` basis, data/persistence, integrations, flows/rules, test quality, risks, questions, and evidence.
The coordinator merges these records incrementally, preserves every canonical information-domain state, and
invokes the single renderer; a Java, COBOL, PL/I, SQL, frontend, or other worker never creates a competing
dashboard structure.

For a long run, report concise stage progress without pausing between safe slices: inventory, active language
or subsystem domains, synthesis, requirements, specifications, dashboard, and coverage validation.

## Completion gate

Record coordinator-owned fan-in stages with `scripts/coordinate_analysis.py stage`, then run
`scripts/coordinate_analysis.py validate`. `FULL` analysis is complete only when:

- every relevant artifact has a final coverage status and unaccounted relevant sources equal zero;
- every important executable artifact passes the depth gate and critical business components are not partial;
- every required slice is validated and cross-system synthesis is validated;
- requirements and OpenSpec stages required by project mode are reconciled;
- the canonical dashboard is refreshed from structured state and passes its required gates;
- forward and reverse traceability is audited independently;
- blocked items, exclusions, limitations, and actual counts are explicit.

For mixed implementations, synthesis cannot validate until COBOL, PL/I, Java/API, or other relevant variants
are explicitly classified `EQUIVALENT`, `PARTIALLY_EQUIVALENT`, `DIVERGENT`, `MISSING`, or `UNKNOWN` with
evidence, unknowns, and defect decisions. Write the final validated checkpoint to project memory.

Never finish a default invocation with “first bounded slice complete; recommended next slice.” That wording is
valid only for an explicitly bounded request or an interrupted run. Report actual scope counts, languages,
slice counts, requirement/specification counts, traceability status, dashboard path, blockers, validation,
and one exact next canonical action. Legacy analysis may prepare requirements and selected specifications,
but it never begins implementation.
