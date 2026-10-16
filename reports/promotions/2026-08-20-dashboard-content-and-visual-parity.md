# Promotion report: dashboard content and visual parity

- Promotion ID: `PROMOTE-2026-08-20-DASHBOARD-CONTENT-VISUAL-PARITY`
- Date: 2026-08-20
- Source: explicit user instruction, “make sure to improve both,” referring to the project dashboard and the reusable Commons dashboard capability
- Selected: semantic content completeness, executive visual hierarchy, peer-artifact claim parity, deliberate localization, and functional project-record details
- Excluded: client branding, client content, project paths, source text, screenshots, assets, authored Commons sales narrative, new capabilities, and unrelated lifecycle behavior
- Canonical action: update the existing `build-living-dashboard` skill, renderer, validators, browser capture, documentation, and regression evals

## Revalidation

| Candidate | Selected by | Evidence | Overlap | Action | Disposition | Result |
|---|---|---|---|---|---|---|
| Semantic content completeness | Explicit user instruction | A completed dashboard could mark domains available and render standard sections while executive regions remained materially empty | Existing living-dashboard generator and semantic validator | Update | `PROMOTE_UPDATE` | Available domains now require supporting canonical content; completed full modernization dashboards require findings, decision, stakeholder, estimate, roadmap, transition, interface, and risk-gate content |
| Executive visual hierarchy | Explicit user instruction | The operational domain ledger preceded the executive narrative in the initial composition, especially on mobile | Existing canonical dashboard shell and visual contract | Update | `PROMOTE_UPDATE` | Context, status, denominator metrics, findings, and actions now lead; the domain ledger follows, while decision and modernization regions use stronger editorial composition |
| Dashboard/presentation claim parity | Explicit user instruction | Shared headline facts had no deterministic cross-artifact validation surface | Existing semantic validator and dashboard data contract | Update | `PROMOTE_UPDATE` | Optional `dashboard.shared_claims[]` binds non-empty canonical paths to visible peer markers through `--peer-html` validation |
| Deliberate localization | Explicit user instruction | Locale-prefixed source strings could satisfy the previous non-identical translation check | Existing localization completeness gate | Update | `PROMOTE_UPDATE` | Locale-label placeholders such as `DE: <source>` now fail generation; project status and information-domain labels, reasons, and states participate in localization coverage |
| Functional project-record details | Browser review during selected work | Project register rows were rendered as detail buttons but were absent from the detail index; plain strings could also appear as fake links | Existing register and shared detail-dialog interaction family | Update | `PROMOTE_UPDATE` | Structured project records are indexed and keyboard-openable; plain strings render as non-interactive headings |

## Boundary and provenance

- Reuse: all five changes apply to unrelated technical, management, discovery, and modernization dashboards.
- Generalization: the implementation uses generic lifecycle fields, canonical paths, information-domain IDs, visible peer markers, and synthetic eval fixtures.
- Confidentiality: the proposed Commons diff was scanned for client names, repository names, private paths, application terms, host names, URLs, and personal identifiers. No project-specific content was introduced; substring matches were limited to the generic word `shared_claims`.
- External provenance: none. The change is an independent repository-local implementation with no copied or adapted third-party material and no license change.
- Routing collision: the existing skill was updated; no `v2`, project-specific, or competing dashboard capability was created.

## Canonical changes

- Updated the living-dashboard skill and data contract with completed-analysis executive content requirements, available-domain backing, shared-claim parity, and placeholder-translation failure behavior.
- Updated the canonical shell and visual contract with a narrative-first overview, stronger decision and modernization compositions, localized domain records, and functional project detail records.
- Updated deterministic validation for semantic content, peer HTML visible-text markers, shared-claim structure, and localization editorial quality.
- Hardened browser capture so hidden detail surfaces do not cause scroll timeouts and the first visible detail opener is used.
- Updated one executable dashboard eval module with regression coverage for the selected behavior.
- Refreshed generated Commons presentation facts. The refresh detected the changed dashboard template and tools; no authored sales narrative or locked presentation visual system changed.

## Files

- Created: this promotion report.
- Updated: `skills/build-living-dashboard/SKILL.md`, the dashboard data contract, canonical shell, visual contract, generator, semantic validator, browser capture script, dashboard evals, and generated presentation facts.
- Deprecated: none.
- Deleted: none.
- Provenance files: unchanged because no external relationship was introduced.
- Catalog and relationship files: unchanged because capability identity and routing did not change.
- Archetypes and overlays: unchanged; the improvement strengthens existing dashboard behavior across every current composition without adding a new composition boundary.
- Adapters and runtimes: no adapter body changed. Canonical Python and JavaScript entrypoints were exercised through executable evals and Chromium browser capture.

## Compatibility

- Initialized, pending, bounded, adaptive, and non-complete dashboards remain compatible; the expanded executive package is required only for complete `full-legacy-modernization` analysis.
- Existing dashboards without `dashboard.shared_claims` do not require a peer artifact. When shared claims are declared, semantic validation requires `--peer-html` and visible markers.
- Existing real translations remain compatible. Locale-prefixed source placeholders now fail closed.
- Project registers containing strings remain renderable, but no longer claim an unavailable detail interaction.
- Repository version and schema versions remain unchanged under current compatibility policy.

## Validation

| Validation | Result | Evidence or limit |
|---|---|---|
| `python3 -m unittest evals.tools.test_dashboard evals.tools.test_dashboard_visual` | PASS | 44 tests passed in 2.920 seconds |
| `python3 tools/refresh_commons_presentation.py --check` | PASS | Presentation data is current |
| `python3 tools/check_presentation_visual_contract.py` | PASS | Locked Commons presentation visual contract remained unchanged |
| `python3 tools/validate_commons.py` | PASS | `skills=46 agents=4 errors=0 warnings=0` |
| `git diff --check` | PASS | No whitespace errors |
| Chromium dashboard state capture | PASS | All 13 required desktop, laptop, detail, and mobile states passed with no console errors or horizontal overflow |
| Project dashboard structural and semantic validation | PASS | Canonical structure passed; peer-artifact shared claims passed against visible text |
| Project dashboard visual, brand, localization, and accessibility gates | PASS with stated accessibility limits | Visual QA, brand consistency/fidelity, de-AT and English localization, keyboard detail activation, focus restoration, and 390 px/200% reflow passed; no screen reader or axe-core was available |
| Normalized delivery traceability audit | PASS | 87 nodes, 178 reciprocal edges, 0 structural findings; implementation and test completion are not claimed at the current lifecycle stage |
| Confidentiality scan | PASS | No client or project material in the Commons diff; only generic `shared_claims` substring false positives |

## Documentation and narrative impact

- Documentation now makes the executive-content, available-domain, shared-claim, and deliberate-localization contracts explicit.
- Deterministic Commons presentation facts were refreshed and validated.
- Narrative recommendation: no authored Commons sales-story update is warranted. The change improves dashboard product quality and validation, but does not change the library’s capability count, composition model, governance story, or agent model.

## Remaining limits

- Peer parity is marker-based and intentionally bounded; it proves selected visible headline claims, not full semantic equivalence between two narratives.
- Accessibility evidence is a bounded browser and keyboard review, not formal legal certification or an end-to-end screen-reader evaluation.
- The completed-modernization executive package validates meaningful presence and canonical backing; project-specific business acceptance still remains external authority.

Selected: 5
Promoted: 5
Blocked: 0
No change: 0
Evals: 1 executable eval file changed
Adapters: canonical Python and JavaScript runtimes verified; no adapter body change
Validation: PASS
Version: 1.0.0 -> 1.0.0
Commit: this report is contained in the focused promotion commit; the final hash is reported in the handoff
