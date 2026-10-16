# Project Memory and Deep Legacy Analysis

This report records the canonical Agent Commons decision and validation evidence for persistent project knowledge, selective context retrieval, and deep-by-default legacy analysis. Project memory is a retrieval and continuation layer; source and canonical structured artifacts remain authoritative.

## 1. Existing memory and context capabilities found

The audit classified the existing capabilities as follows:

| Classification | Existing capability | Finding |
|---|---|---|
| OVERLAPPING | `maintain-project-memory` | Already defined repository-native state, checkpoints, decisions, handoff, and continuation. It was the correct canonical capability to improve. |
| PARTIAL | `durable-state` overlay and templates | Selected durable work products but did not define hierarchical retrieval, invalidation, controlled merge, or context measurement. |
| PARTIAL | `continue-project` | Resolved lifecycle state but did not consume a compact memory index or surface stale/conflicting records. |
| PARTIAL | `analyze-legacy-system` | Had inventory-backed slicing and checkpoints but lacked a hard semantic depth packet and explicit cross-language comparison gate. |
| PARTIAL | `coordinate-parallel-agents` | Defined bounded ownership and fan-in but not a canonical project-memory proposal/merge path. |
| PARTIAL | living dashboard, research, requirements, OpenSpec, TDD, estimation, and presentation workflows | Consumed structured evidence but did not consistently state read-before-work and bounded-memory behavior. |
| MISSING | deterministic hierarchical manager | No canonical tool implemented create/read/update/invalidate/compact/rebuild/validate operations. |
| MISSING | continuation and quality benchmark | No executable comparison measured repeated context while proving semantic coverage was preserved. |

The complete audit covered `skills/`, `agents/`, `tools/`, `templates/`, `archetypes/`, `adapters/`, `catalog/`, and `evals/`.

## 2. Reuse or create decision

The decision was to improve and reconcile `maintain-project-memory`, not create a duplicate `memory` or `project-memory` skill. A deterministic tool named `manage-project-memory` was added beneath the existing skill. The capability remains runtime-neutral and uses standard JSON and Markdown files.

## 3. Memory architecture

The architecture externalizes verified conclusions, decisions, state, relationships, and evidence pointers. It never stores hidden chain-of-thought or treats conversation transcripts as canonical memory.

The source-of-truth order is:

`SOURCE / INPUT` → `CANONICAL STRUCTURED ANALYSIS` → `REQUIREMENTS / SPECS` → `PROJECT MEMORY / INDEX` → `DASHBOARD / PRESENTATION`

Workers return validated proposals. One deterministic merger performs atomic canonical writes, preserves conflicts, and rebuilds the index.

## 4. Storage location

Project-local machine-owned memory lives under `.agent-commons/memory/`. No top-level `memory/` directory is introduced. Normal deliverables remain in `analysis/`, `requirements/`, `openspec/`, `dashboard/`, and `presentation/`.

The manager creates `state.json`, `project-summary.md`, `index.json`, `source-state.json`, `domains/`, `entities/`, `checkpoints/`, `decisions.json`, and `terminology.json` lazily.

## 5. L0, L1, and L2 model

- L0 is the small project synopsis: goal, mode, sources, protected paths, target stack, languages, architecture, lifecycle, major decisions, blockers, and next action.
- L1 contains domain summaries and record indexes, such as COBOL, PL/I, Java/API, contracts, data, integrations, modernization, or estimation.
- L2 contains stable-ID entity records for components, flows, rules, data structures, interfaces, requirements, and decisions.
- EVIDENCE is not copied into memory. Records retain canonical paths, source coordinates where supplied, and hashes so an agent can verify against the original artifact.

## 6. Evidence preservation

Each material record requires `canonical_refs`, `evidence`, `confidence`, an entity ID/type, and a stable record ID. Evidence paths are constrained to the project root. SHA-256 values are validated when supplied. `validate` detects missing references, changed evidence incorrectly marked current, dangling relationships, index hash drift, and malformed conflicts.

Confidence remains one of `VERIFIED`, `INFERRED`, `UNKNOWN`, `STALE`, or `CONFLICTING`. Rebuild and compaction preserve confidence rather than promoting summaries.

## 7. Context-package strategy

`manage-project-memory read` builds deterministic task-specific packages from L0 plus selected L1 domains and L2 entities. Dependency traversal follows both outgoing and incoming project-memory relationships to the requested depth. The request sets record and checkpoint bounds.

Every package identifies mandatory context, useful record IDs, relevant records omitted by the bound, irrelevant record IDs, stale/conflicting records, and measured UTF-8 byte size. Correctness wins over a byte target: omitted relevant IDs remain explicit so the coordinator can widen retrieval or read source when needed.

## 8. Checkpoint strategy

Validated phase checkpoints use stable names such as `INITIALIZATION_COMPLETE`, `INVENTORY_COMPLETE`, `LANGUAGE_ANALYSIS_COMPLETE`, `SYSTEM_SYNTHESIS_COMPLETE`, `REQUIREMENTS_COMPLETE`, `ROADMAP_COMPLETE`, `SPECIFICATIONS_COMPLETE`, `IMPLEMENTATION_SLICE_COMPLETE`, and `VALIDATION_COMPLETE`.

Context packages load only the latest bounded checkpoint set by default. Checkpoints point to canonical outputs and do not replace them.

## 9. Invalidation strategy

The manager records the current source-inventory fingerprint and artifact hashes. Changed or removed hashed evidence marks only directly affected records `STALE`. Dependency propagation then marks records that depend on stale records. Unrelated records remain current. The legacy coordinator also fingerprints each slice from both its primary artifacts and contextual inputs, so a changed copybook, contract, configuration, or source invalidates only dependent slices and downstream synthesis.

## 10. Contradiction handling

Two semantically different proposals for one stable record ID are not overwritten. The merger creates a `CONFLICTING` record containing both variants, combined evidence, canonical references, relationships, and tags. Validation requires at least two preserved variants. `continue-project` surfaces conflicting IDs and routes legacy conflicts back to synthesis.

## 11. Parallel-agent integration

The coordinator owns memory mutation. Each specialist receives L0, owned artifact IDs and hashes, selected domain/entity memory, relevant dependencies, unresolved questions, and evidence locations. Workers write one isolated structured result and a memory proposal. Deterministic validation and controlled fan-in happen before the manager writes canonical memory. Workers never rewrite global memory directly.

## 12. `continue-project` integration

The continuation resolver reads the manifest, `.agent-commons/memory/index.json`, and L0 state without reconstructing project history. It returns the memory fingerprint, latest checkpoint, next action, and stale/conflicting IDs. Unchanged validated work is retained. Stale or conflicting legacy-analysis memory routes back to `analyze-legacy-system` instead of being silently reused.

## 13. `analyze-legacy-system` integration

FULL remains the default scope and DEEP is now the default depth. The coordinator reuses a deterministic inventory, validates primary and contextual fingerprints, creates bounded language/domain slices, requires structured deep results, performs controlled fan-in, requires mixed-language synthesis where applicable, and blocks completion until both coverage and depth pass. The workflow then feeds requirements, optional OpenSpec, dashboard refresh, and a validated memory checkpoint.

## 14. Dashboard integration

The living-dashboard workflow now consumes canonical structured project state plus memory indexes for routing and compact summaries. It does not reread source to render routine updates and does not treat memory as a second truth store. Executive views remain compact; technical drill-down keeps components, flows, rules, data, dependencies, unknowns, and evidence reachable.

## 15. OpenSpec and TDD integration

Specification and implementation workflows load the selected requirement/specification, linked decisions, affected components, related memory, and necessary files. They do not load the complete analysis history. After a verified implementation slice, canonical implementation/test state is updated first, followed by the project-memory delta and checkpoint.

## 16. Token-reduction techniques

Implemented techniques include retrieve-not-reload, L0/L1/L2 hierarchy, delta continuation, stable IDs, evidence pointers, one reusable inventory, dependency retrieval, bounded context packages, bounded checkpoints, controlled deduplication, incremental writes, selective invalidation, and rebuilding HOT summaries from canonical records rather than repeatedly summarizing summaries.

No exact token claim is made because the runtime did not expose token accounting. The benchmark measures UTF-8 payload bytes and repeated-read counts.

## 17. Before and after context measurements

The deterministic mixed-language benchmark measured:

| Measure | Baseline continuation | Optimized continuation |
|---|---:|---:|
| Repeated context bytes | 226,318 | 4,880 |
| Context package bytes | Not applicable | 3,204 |
| Inventory payload/fingerprint bytes | 1,676 reloaded | 1,676 reused |
| Repeated source reads | 5 | 0 |
| Reduction in repeated context | — | 97.84% |

The result exceeds the desired 30–60% reduction range for this fixture. It is a deterministic synthetic measurement, not a claim about production billing or elapsed time.

## 18. Deep-analysis definition

Deep analysis means semantic understanding at the level relevant to modernization: structure, control flow, state/branches/loops, validations and exceptions, data semantics and transformations, dependencies and contracts, business rules, non-functional behavior, maintainability, migration significance, unknowns, and observed defect candidates.

For critical COBOL, PL/I, and Java executables, `DEEP_VERIFIED` requires every depth dimension to be `VERIFIED` or explicitly justified as `NOT_APPLICABLE`, evidence IDs, complete non-negative semantic counts, at least one flow, and complexity entries whose basis is `MEASURED` or `ASSESSED`.

## 19. Depth and coverage gates

Coverage proves every relevant inventory artifact is accounted for. Depth proves important behavior is understood. FULL completion requires both gates plus all required lifecycle stages. A filename-level or import-level observation cannot satisfy the depth gate. PARTIAL or BLOCKED critical artifacts remain completion blockers.

## 20. Mixed-language benchmark

The fixture contains COBOL, PL/I, Java, a copybook, and an API contract. The coordinator plans independent bounded specialists and requires cross-language synthesis with explicit counts for `EQUIVALENT`, `PARTIALLY_EQUIVALENT`, `DIVERGENT`, `MISSING`, and `UNKNOWN`, plus evidence-backed unknowns and defect candidates.

Before and after continuation both retained three `DEEP_VERIFIED` executable artifacts and identical semantic totals: 9 flows, 12 business rules, 8 data structures, 8 dependencies, 5 interfaces, 3 defect candidates, and 3 unknowns. Quality regression was false.

## 21. Resume benchmark

The continuation benchmark resumed from a validated checkpoint with an unchanged inventory. All 5 of 5 slices were reused, the inventory fingerprint matched, and unchanged source reads were zero. Changed primary or contextual input hashes are separately covered by tests that reset only affected slices and downstream fan-in.

## 22. Evals

Executable coverage includes hierarchy creation, automatic substantial-project enablement, tiny-project opt-out, bounded bidirectional dependency retrieval, checkpoint bounds, controlled worker merge, contradictions, selective invalidation, compaction/rebuild, evidence reachability, continuation state resolution, source/context drift, deep semantic packets, coverage-plus-depth completion, mixed-language synthesis, dashboard lifecycle QA, byte reduction, and no semantic regression.

Skill scenarios also cover dashboard consumption and OpenSpec/TDD selective context. The repository validator requires the manager, tests, benchmark, and this report.

## 23. Runtime-adapter behavior

Codex, Claude Code, Cline, and OpenCode adapters expose the same project-local canonical memory model. Native runtime context or memory features may optimize loading, but they never become the only copy or change the canonical format. Global adapter guidance requires compact memory read-before-work for substantial tasks and forbids external sharing unless the task explicitly authorizes it.

## 24. Remaining limitations

- Runtime token billing and elapsed time were not observable; only real UTF-8 payload sizes and deterministic reuse were measured.
- The benchmark is synthetic and intentionally small enough for repository evals; production estates should add project-specific performance observations.
- Source coordinates are preserved when producers supply them, but the manager does not parse every language to invent coordinates.
- Relationship retrieval depends on structured relationships produced by analysis; unknown relationships still require source verification.
- Native runtime memory features are optional adapter optimizations and were not benchmarked.
- Memory enables bounded parallel specialist work but does not itself create agents or relax coordinator ownership and validation gates.
