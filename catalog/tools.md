# Canonical deterministic tools

| Tool | Location | Purpose |
|---|---|---|
| Evaluation runner | `tools/evals/run_evals.py` | Run selected static, behavioral, integration, and end-to-end contracts with repeat, baseline, JSON, and JUnit support |
| Impacted-evaluation selector | `tools/evals/select_impacted_evals.py` | Resolve changed capabilities, related impacts, archetypes, workflows, scenarios, and protected evaluation changes |
| Structured data anonymizer | `skills/anonymize-data/scripts/anonymize_data.py` | Apply exact field-scoped drop, redaction, or keyed stable-token rules to JSON, JSONL, NDJSON, or CSV with leakage-safe reports |
| Project initializer | `skills/initialize-project/scripts/initialize_project.py` | Non-overwriting scaffold and optional Git initialization |
| Project continuation resolver | `skills/continue-project/scripts/resolve_project_continuation.py` | Resolve lifecycle stage, blockers, stable requirement/specification references, safe project-local paths, and the next canonical capability |
| Project delivery analyzer | `skills/manage-project-delivery/scripts/analyze_project_delivery.py` | Validate delivery registers and derive dependency-aware health, blockers, overdue work, ready work, high risks, and critical path |
| Project financial forecast calculator | `skills/forecast-project-financials/scripts/calculate_project_forecast.py` | Validate period data and deterministically calculate EAC, variance, margin, earned-value metrics, warnings, and scenarios |
| Codebase inventory | `skills/inventory-codebase/scripts/inventory_codebase.py` | Stable artifact IDs, classification, hashes, fingerprint, batches |
| Legacy structure extractor | `skills/analyze-legacy-system/scripts/extract_legacy_structure.py` | Conservative COBOL, Java, and SQL lexical observations with exact coordinates and unresolved dynamic constructs |
| Legacy analysis coordinator | `skills/analyze-legacy-system/scripts/coordinate_analysis.py` | Plan full/bounded/continue modes, coverage, safe slice stages, resumable checkpoints, serialized fan-in, and the hard completion gate |
| Project memory manager | `skills/maintain-project-memory/scripts/manage_project_memory.py` | Create, retrieve, merge, invalidate, compact, rebuild, validate, and benchmark hierarchical project-local memory |
| ADM estimate summarizer | `skills/estimate-adm-modernization/scripts/summarize_adm_estimate.py` | Validate three-point estimate invariants and aggregate unit and workstream person-day ranges deterministically |
| Migration manifest validator | `skills/migrate-code-with-evidence/scripts/validate_migration_manifest.py` | Reject writable sources, shared roots, embedded credential keys, missing trace links, unsafe commands, and weakened migration safety defaults |
| Trace matrix audit | `skills/audit-delivery-traceability/scripts/audit_trace_matrix.py` | Detect lifecycle chain gaps in a normalized CSV |
| Trace graph audit | `skills/audit-delivery-traceability/scripts/audit_trace_graph.py` | Detect duplicate IDs, missing endpoints, asymmetric edges, lifecycle gaps, and stale generated fingerprints in normalized JSON |
| Slice ranker | `skills/implement-ready-slice/scripts/rank_slices.py` | Deterministically shortlist dependency-ready work |
| Dashboard generator | `skills/build-living-dashboard/scripts/build_dashboard.py` | Instantiate/check the canonical living-dashboard structure, owned-criterion traceability, bounded registers, brand roles, and localization coverage |
| Dashboard structure validator | `skills/build-living-dashboard/scripts/validate_dashboard_structure.py` | Detect structural drift, missing bounded-register controls, and premature lifecycle-validation claims |
| Dashboard semantic validator | `skills/build-living-dashboard/scripts/validate_dashboard_semantics.py` | Require every canonical information domain, valid lifecycle state, stable placement, and measured/assessed basis |
| Dashboard visual fidelity validator | `skills/build-living-dashboard/scripts/validate_dashboard_visual.py` | Enforce design grammar and the applicable structure/static/brand/visual/accessibility/localization hard gate with matching fingerprints |
| HTML static validator | `skills/validate-visual-artifact/scripts/validate_html.py` | Structural, dependency, focus, print, and reduced-motion checks |
| Diagram model validator | `skills/create-technical-diagram/scripts/validate_diagram_model.py` | Check evidence references, endpoints, confidence states, unknown-edge handling, and large-model decomposition |
| Client localization validator | `skills/localize-client-artifact/scripts/validate_localization.py` | Detect missing, stale, obsolete, identifier-changing, and number-changing message records plus inaccessible language controls and HTML key gaps |
| Commons validator | `tools/validate_commons.py` | Check candidate structure, metadata, references, eval coverage, and leakage |
| Archetype resolver | `tools/resolve_archetypes.py` | Validate manifests and resolve deduplicated hybrid capability selections |
| Capability-gap resolver | `tools/resolve_capability_gaps.py` | Compare project requirements, including migration source/target/bridge dimensions, with semantic coverage declared by actual commons capabilities |
| Commit-message policy | `tools/commit_policy.py` | Validate meaningful non-Conventional subjects, conservative task-ticket prefixes, and prohibited attribution trailers |
| Runtime adapter renderer | `tools/runtime_adapters.py` | Validate adapter manifests and render thin native workflow or role representations |
| Commons presentation refresh | `tools/refresh_commons_presentation.py` | Regenerate/check standalone presentation counts, navigator, search, previews, and evidence-backed network data |
| Presentation visual-contract checker | `tools/check_presentation_visual_contract.py` | Reject CSS, theme, structure, SVG, interaction, or runtime drift while permitting textual content updates |
| Presentation data generator | `tools/sync_presentation.py` | Build, validate, compare, and atomically write the deterministic payload behind the public refresh command while preserving the legacy sync/validate interface |
| Project runtime manager | `tools/project_runtimes.py` | Verify or remove thin project adapters without deleting shared project context |
| External capability intelligence | `tools/external_capabilities.py` | Validate sources/reviews/indexes, normalize GitHub locations, search configured sources, derive privacy-safe project queries, maintain metadata, and detect stale revisions |
| External discovery worker | `tools/run_external_discovery.py` | Run cached bounded external discovery independently and persist completed, partial, or rate-limited project state |

The external source registry is canonical metadata at `external/sources.yaml`; discovered packages remain
inactive and external cache material is disposable.

Scripts deliberately stop before semantic decisions that require evidence-aware judgment.
