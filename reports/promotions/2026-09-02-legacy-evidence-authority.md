# Promotion — legacy evidence authority and reference boundaries

- **Promotion ID:** `PROMOTE-2026-09-02-LEGACY-EVIDENCE-AUTHORITY`
- **Date:** 2026-09-02
- **Source review:** project-local `docs/commons-review.md` and `docs/commons-review.json`
- **Selection evidence:** user instruction, “perform with promoting your recommendations”
- **Selected:** `P0-001` legacy oracle authority and readiness; `P0-002` reference application as a discovery prior
- **Excluded:** `P1-001` source-aware legacy test generation, pending a second application profile and a real pilot; all `DNP-*` project-specific artifacts and conclusions
- **Canonical action:** update the existing `design-test-strategy` and `analyze-legacy-system` capabilities

## Revalidation

| Candidate | Selected by | Evidence | Overlap | Action | Disposition | Result |
|---|---|---|---|---|---|---|
| `P0-001` legacy oracle authority and readiness | User approved the review's recommendations | The source workflow distinguishes approved intent, observed source behavior, unresolved expected outcomes, and multiple implementation-readiness states | Existing `design-test-strategy` owns portfolio selection but did not define authority or readiness for legacy-derived oracles | Update | `PROMOTE_UPDATE` | Added reusable authority, readiness, contradiction, and defect-candidate rules without introducing a competing skill |
| `P0-002` reference application as discovery prior | User approved the review's recommendations | The source operating contract uses a separate reference application to prioritize inspection while prohibiting promotion of reference facts into target truth | Existing `analyze-legacy-system` owns evidence-first orchestration but did not formalize this boundary | Update | `PROMOTE_UPDATE` | Added a fingerprinted reference-profile contract, match/non-match recording, and strict target-evidence isolation |

## Revalidation decisions

| Field | `P0-001` | `P0-002` |
|---|---|---|
| Reuse | Applies to legacy test planning wherever intended behavior, observed behavior, and unknown outcomes differ | Applies whenever a legacy analysis has an explicitly authorized comparison or reference application |
| Generalization | Removed project-specific flow names, source paths, fixtures, and outcome values | Removed project names, repository paths, framework names, and target conclusions |
| Abstraction | Update the existing test-strategy skill and its evaluation contract | Update the existing legacy-analysis orchestrator and legacy-migration archetype |
| Maturity | Proven in one source workflow with deterministic regression coverage; no real generated-suite execution is claimed | Proven as an operating boundary in one source portfolio; no cross-project similarity is asserted |
| Confidentiality | Safe after generalization; synthetic fixtures only | Safe after generalization; synthetic target and reference profiles only |
| External provenance | None; `INDEPENDENT-REIMPLEMENTATION` of internally observed workflow behavior | None; `INDEPENDENT-REIMPLEMENTATION` of internally observed workflow behavior |
| Collision risk | Kept inside `design-test-strategy`; no oracle-specific duplicate capability | Kept inside `analyze-legacy-system`; reference patterns remain distinct from target evidence and from external-capability research |

## Canonical changes

**Created**

- `skills/design-test-strategy/references/legacy-oracle-readiness.md`
- `skills/analyze-legacy-system/references/reference-applications.md`
- `evals/tools/test_legacy_evidence_boundaries.py`
- `evals/fixtures/legacy-test-strategy/oracle-evidence.json`
- `evals/fixtures/legacy-reference/target-and-reference.json`
- this promotion report

**Updated**

- Both selected skill bodies, the legacy-migration archetype, capability catalog, and generated capability index.
- Skill scenarios, evaluation fixtures, golden expectations, capability contracts, and nightly/weekly evaluation shards.
- `README.md`, `CHANGELOG.md`, `VERSION`, and the initializer's synchronized library version.
- Generated presentation facts in `presentation/agent-commons.html` and `presentation/assets/library-data.js`.

**Deprecated or deleted:** none.

## Evals and behavior coverage

- Added four deterministic tests covering required reference-profile isolation, match/non-match recording,
  legacy-oracle authority, and readiness gating. The tests failed before the implementation and pass after it.
- Added positive, negative, collision, regression, output, invariant, and failure expectations to the two
  affected skill scenario blocks.
- Added two external semantic scenarios and matching golden records: one for reference-prior analysis and one
  for legacy test strategy.
- Added the updated test-strategy capability to both required Azure evaluation shards.

## Composition, adapters, documentation, and version

- **Archetype:** the existing `legacy-migration` archetype now permits an explicitly authorized separate
  reference application during discovery and states that it can never become target evidence. No new archetype
  or overlay was warranted.
- **Catalog and relationships:** both capabilities expose the new behavior through `provides` and routing
  keywords; their identities and existing ownership boundaries remain unchanged.
- **Adapters and runtimes:** no adapter body or runtime-specific representation changed. All four configured
  runtimes pass canonical adapter validation.
- **Documentation:** README and changelog describe the new reusable behavior. Deterministic presentation facts
  were refreshed. Authored sales narrative and the locked visual system were not changed.
- **Narrative recommendation:** no separate presentation-story update is warranted; this strengthens evidence
  governance without changing the library's architecture, composition model, or agent model.
- **Version:** `1.2.0` to `1.3.0`.

## Confidentiality and provenance

- Added-line scanning found no source-project name, application name, user identity, workstation path, private
  URL, credential, business payload, or proprietary excerpt.
- All fixtures are synthetic and parameterized.
- No third-party material was copied or adapted, so no external license record changed.
- Source-project identity remains only in the read-only source review and is not present in canonical bodies,
  generated presentation data, or this report.

## Validation

| Validation | Result | Evidence or limit |
|---|---|---|
| RED check for `evals.tools.test_legacy_evidence_boundaries` | PASS as RED evidence | Four tests failed before the capability changes because the references and contracts did not exist |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest evals.tools.test_legacy_evidence_boundaries` | PASS | 4 tests passed after implementation |
| Targeted deterministic suite | PASS | 44 tests passed across evidence boundaries, evaluation contracts, archetypes, and capability-index coverage |
| `python3 tools/runtime_adapters.py validate` | PASS | 4 runtimes, 0 errors |
| `python3 tools/resolve_archetypes.py validate` | PASS | 4 archetypes, 9 overlays, 0 errors |
| `python3 tools/resolve_capability_gaps.py validate` | PASS | 0 errors |
| `python3 tools/external_capabilities.py validate` | PASS | 8 sources, 2 candidates, 0 errors, 0 warnings |
| `python3 tools/validate_commons.py` | PASS | 50 skills, 5 agents, 0 errors, 0 warnings |
| Focused fast evaluation for both capabilities | PASS with external limit | 7 results: 4 pass, 3 warnings, 0 hard failures; warnings record unavailable external semantic execution and are not treated as semantic passes |
| `python3.11 tools/evals/run_evals.py --all` | **FAILED** | 105 results: 68 pass, 36 warnings for unavailable semantic execution, and 1 hard failure. The hard failure is the same unrelated public-baseline assertion reproduced against unchanged `HEAD`. |
| `python3 tools/refresh_commons_presentation.py --check` | PASS | Presentation data is current |
| `python3 tools/check_presentation_visual_contract.py` | PASS | Locked visual contract is unchanged |
| Documented Python 3.11 unittest gate | **FAILED** | 474 tests ran. After removing an ignored local `.claude/` marker from the isolated test checkout, the environment-specific initialization case passes. One unrelated public-baseline assertion remains failing. |
| Public-baseline failure against unchanged `HEAD` | **PRE-EXISTING FAILURE** | The same assertion fails at `52071bb`: the test expects an empty external-candidate index while current `HEAD` contains two incorporated candidates. It is outside the selected promotion and was not weakened or repaired. |
| `git diff --check` | PASS | No whitespace errors |
| Added-line confidentiality scan | PASS | No configured private or source-project identifiers found |

## Git boundary and disposition

- **Pre-change status:** clean `main` at `52071bb123b5001edefe4b4436ac4fc228453b28`.
- **Post-change status:** 17 modified files and six new files, all attributable to this promotion.
- **Commit:** pending. The promotion contract requires the complete repository gate to pass before a focused
  promotion commit. The selected changes pass their own deterministic and structural gates, but the pre-existing
  public-baseline failure keeps the repository-wide result at `FAILED`.
- No source-project file was changed by this promotion.

## Remaining limitations and follow-up decisions

1. External semantic execution was unavailable, so the new semantic scenarios are registered and structurally
   valid but not independently judged in this run.
2. `P1-001` remains project-local until a second application profile and a real source-aware generation pilot
   demonstrate broader reuse and safe failure behavior.
3. A separate authorized change must reconcile the public-baseline assertion with the governed external
   capability index. Until then, the promotion stays implemented and uncommitted.

Selected: 2
Promoted: 2
Blocked: 0 candidates; final commit blocked by a pre-existing repository gate failure
No change: 0
Evals: 7 files added or changed, plus 2 CI shard configurations
Adapters: 4 runtimes verified; no adapter body changes
Validation: FAILED because one unrelated current-HEAD public-baseline assertion fails
Version: 1.2.0 -> 1.3.0
Commit: pending; complete repository validation is not green
