# Promotion report: build-living-dashboard P0 hardening

- Promotion ID: `PROMOTE-2026-08-20-BUILD-LIVING-DASHBOARD-P0`
- Date: 2026-08-20
- Source: explicit user-selected generic improvements P0-001 through P0-005
- Selected: P0-001, P0-002, P0-003, P0-004, P0-005
- Excluded: P1-001 and all project-specific names, colors, text, URLs, screenshots, and assets
- Canonical action: update the existing `build-living-dashboard` capability and deterministic tools

## Revalidation

| Candidate | Selected by | Evidence | Overlap | Action | Disposition | Result |
|---|---|---|---|---|---|---|
| P0-001 traceability ownership | Explicit user selection | Existing generator expanded each requirement across every criterion of a shared specification | Existing dashboard and traceability audit capabilities | Update | `PROMOTE_UPDATE` | Criterion ownership is explicit for shared specifications; invalid ownership fails closed |
| P0-002 bounded registers | Explicit user selection | Existing browser renderer emitted every record and chain initially | Existing dashboard interaction family | Update | `PROMOTE_UPDATE` | Requirements, evidence, tests, and traceability are bounded with counts, filters, show-more, and trace depth |
| P0-003 semantic brand roles | Explicit user selection | Existing profile proved colors but not role-appropriate visible use | Existing brand profile and visual fidelity validation | Update | `PROMOTE_UPDATE` | Primary, secondary, highlight, identity, danger, success, focus, and header roles are validated |
| P0-004 lifecycle QA gate | Explicit user selection | Generated chrome claimed validation before independent visual, accessibility, and localization results | Existing structure, visual, brand, localization, and coordinator gates | Update | `PROMOTE_UPDATE` | Applicable independent results and matching fingerprints are mandatory for `VALIDATED` |
| P0-005 localization coverage | Explicit user selection | Existing keyed messages did not deterministically enumerate nested rendered fields | Existing localization runtime and validator | Update | `PROMOTE_UPDATE` | Rendered human strings are inventoried and missing, empty, stale, or accidental identity fails multilingual generation |

## Boundary and provenance

- Reuse: all five changes apply to unrelated large modernization dashboards.
- Generalization: only synthetic fixtures and generic lifecycle, brand, register, QA, and localization rules were used.
- Confidentiality: no client name, application name, internal URL, workstation path, screenshot, or proprietary asset was introduced.
- External provenance: none; implementation is an independent repository-local update with no copied or adapted third-party material.
- Routing collision: the existing capability was updated; no competing dashboard skill or versioned duplicate was created.
- Archetype integration: the existing living-dashboard overlay now composes accessibility review and the dashboard visual validator because those gates are mandatory when applicable.
- Adapters: no native representation change; adapter validation remains covered by canonical catalog and installer checks.

## Canonical changes

- Dashboard skill, data contract, synthetic example, shell, visual contract, generator, structure validator,
  visual/lifecycle validator, brand profile validator, and browser capture script.
- Initial project generation now records requested client languages but emits an English pending dashboard until
  complete translations exist, preventing an initialized scaffold from masquerading as client-ready localized output.
- Capability, skill, tool, template, overlay, generated capability index, and generated presentation facts were synchronized.
- No new provenance record was required because there is no external source relationship.

## Evals

- `evals/tools/test_dashboard.py`: shared-spec ownership, conflicting/missing ownership, simple-chain
  compatibility, 150/300 bounded-register regression, state-preservation contract, localization missing/empty/stale/identical failures, red-primary compatibility, logo-only rejection, and premature status rejection.
- `evals/tools/test_dashboard_visual.py`: complete applicable gate success plus missing accessibility/visual gate failure.
- `evals/skills/scenarios.yaml`: routing, invariants, failure modes, semantic brand roles, bounded registers, and hard-gate expectations.
- Coordinator lifecycle-QA regression is present in the current canonical HEAD.
- Presentation-maintenance and public-baseline factual regression snapshots were refreshed deterministically.

## Compatibility

- Stable lifecycle IDs and correct simple chains remain compatible. A criterion under a specification linked to
  exactly one requirement may still omit `requirement_id`; the owner is inferred.
- Shared specifications now require singular criterion `requirement_id`; previously ambiguous or cartesian data fails.
- Visual QA manifests advance to schema version 2 and require HTML, design, data, and applicable brand fingerprints.
- Multilingual dashboards now require complete keyed messages before generation. Initialization preserves the
  requested delivery languages as pending configuration while keeping the initial dashboard English-only.
- Repository and capability catalog versions remain `1.0.0` and schema version `1` per repository policy.

## Validation

| Validation | Result | Evidence or limit |
|---|---|---|
| Dashboard/brand/localization/coordinator/capability-index/initialization eval set | PASS | 113 tests passed in 481.831 seconds |
| Final dashboard and visual regression rerun | PASS | 37 tests passed in 17.776 seconds after including derived record actions in localization coverage |
| Synthetic Chromium large-register and locale-state journey | PASS | 25/150 evidence, 50/300 traces, no small-register pagination, filter/dialog/50-record limit/localized nested title preserved, scroll delta 25 px, zero console errors |
| Canonical rendered-state Chromium capture | PASS/PARTIAL by design | All required visual states passed; manifest remained `PARTIAL` because only `VISUAL_QA_PASS` had been produced |
| Branded Chromium semantic-role capture | PASS/PARTIAL by design | All eight visible semantic roles and profile/theme/asset fingerprints matched; missing independent lifecycle results correctly blocked validation |
| `python3 tools/refresh_commons_presentation.py --check` | PASS | `Presentation data: CURRENT` |
| `python3 tools/validate_commons.py` | PASS | `skills=46 agents=4 errors=0 warnings=0` |
| `git diff --check` | PASS | No whitespace errors |
| Extra repository-wide eval probe | KNOWN UNRELATED FAILURE | `test_merge_decisions_are_composed_not_duplicated` expects `earliest valid` in `maintain-project-memory`; the same absence exists in current HEAD and is outside P0-001 through P0-005 |

## Git and lifecycle notes

- Initial observed HEAD: `5206d81` with a clean worktree.
- During validation, HEAD advanced externally to `94fbdeb` (`feat: add hierarchical project memory and deep analysis gates`).
- No commit was created by this promotion. The final dashboard promotion remains uncommitted on top of the new HEAD.
- P1-001 remains a separate follow-up proposal.

## Remaining limits

- Accessibility and localization acceptance remain independent external QA activities; synthetic manifests prove
  gate behavior but do not substitute for a real client artifact review.
- The generic register search indexes serialized record content; specialized semantic search remains out of scope.
- Trace chains preserve criterion-level implementation/test semantics; richer many-implementation test ownership
  can be introduced later only with an explicit canonical relationship contract.

Selected: 5
Promoted: 5
Blocked: 0
No change: 0
Evals: 5 files added or changed, including generated factual regression snapshots
Adapters: canonical catalogs and installer surface verified; no adapter body change required
Validation: PASS for the selected scope; one unrelated pre-existing repository eval remains failing
Version: 1.0.0 -> 1.0.0
Commit: not created by explicit user instruction; external HEAD advanced independently to `94fbdeb`
