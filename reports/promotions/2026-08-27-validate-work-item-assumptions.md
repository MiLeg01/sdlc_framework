# Promotion — validate-work-item-assumptions

- **Promotion ID:** PROMO-2026-08-27-01
- **Date:** 2026-08-27
- **Source review:** `docs/commons-review.md` / `docs/commons-review.json` in the source project (dated 2026-08-26)
- **Selected:** `P0-002` — Work-item currency validation before planning
- **Excluded:** every other candidate in that review and in its user-level companion report (`P0-001`, `P0-003` – `P0-008`, all `P1-*`, all `DNP-*`). Approval covers the selected candidate only.

## Revalidation

Primary evidence was inspected directly rather than trusting the review's conclusion.

| Field | Decision |
|---|---|
| Selection evidence | Explicit stable ID `P0-002` |
| Primary evidence | Source project's read-only staleness-validator agent definition, plus its invocation as a numbered pre-planning step in the project's item-implementation workflow. Behavior pre-existed inline in that workflow and was extracted into a standalone reusable asset on 2026-07-22 — a refactor of practiced behavior, not a fresh invention. |
| Reuse | Applies to any tracker holding items filed before pickup (backlog, issue, ticket, spec, change request). Independent of language, stack, and tracker. |
| Existing overlap | Inspected `continue-project`, `implement-ready-slice`, `review-openspec-change`, `plan-work`, `audit-delivery-traceability`, `inventory-codebase`. Closest is `review-openspec-change`, which assesses whether a change is *internally* ready (scope, ambiguity, delta correctness, tasks) and may refine it. None checks whether an item's claims about **current system state** still hold, and none is read-only-with-verdict. `implement-ready-slice` rejects unsuitable candidates at selection and stops on base drift *during* work — neither is premise validation at pickup. |
| Generalization | Removed the project's item-ID scheme, directory layout, module-path routing table, and worked example naming real modules and a real change. Replaced with tracker-neutral wording. |
| Abstraction | **Skill.** Contract question — *why a separately delegated specialist rather than a skill?* The source runs it as a delegated read-only agent for **token economy** ("the file-reading fan-out is disposable; only its verdict needs to land in the caller's context"), not because independent judgment changes the answer. Context isolation is achievable by delegating this skill to a fresh general-purpose context, which is exactly the canonical agent policy's stated position. No permission boundary is required beyond the skill's own read-only contract. Promoted as a skill. |
| Maturity | Practiced behavior, extracted and wired as a mandatory step. **Limit:** no stored run transcript was found, so execution frequency is not evidenced — see limitations. |
| Confidentiality | Safe after generalization. Scan of the full diff plus the new file returned no project, client, personal, host, path, or business-domain identifiers. |
| External provenance | Not applicable — internal project origin, no third-party material copied or adapted. |
| Collision risk | Resolved by responsibility, not synonyms. Positive: *"before planning this item filed months ago, check whether the code it describes still looks the way it says."* Negative: *"this item is stale — update its approach and start implementing."* Collision with `review-openspec-change`: that skill owns an existing change's internal readiness and may refine it; this one owns whether an item's external premises survived and never edits. |
| Action | Create |
| Disposition | `PROMOTE_NEW` |

**Rename during revalidation:** proposed as `validate-work-item-currency`; promoted as **`validate-work-item-assumptions`**. "Currency" is ambiguous against monetary reading, and "assumptions" names precisely what the workflow extracts and checks. Recorded so the review's `P0-002` remains traceable to this capability.

## Candidate table

| Candidate | Selected by | Evidence | Overlap | Action | Disposition | Result |
|---|---|---|---|---|---|---|
| P0-002 work-item assumption validation | Stable ID `P0-002` | Source project agent definition + mandatory pre-planning wiring; extracted 2026-07-22 from inline practiced behavior | `NEW`; closest neighbour `review-openspec-change`, separated by responsibility and read-only stance | Create | `PROMOTE_NEW` | Promoted as `validate-work-item-assumptions` |

## Files

**Created**
- `skills/validate-work-item-assumptions/SKILL.md` (98 lines)
- `reports/promotions/2026-08-27-validate-work-item-assumptions.md` (this report)

**Updated**
- `evals/skills/scenarios.yaml` — new evaluation block
- `catalog/capabilities.yaml` — capability entry with `provides`, `keywords`, `related`
- `catalog/skills.md` — catalog row with use / do-not-use
- `catalog/capability-index.json` — regenerated
- `adapters/codex/skill-interfaces.yaml` — native interface entry
- `presentation/assets/library-data.js` — deterministic factual refresh
- `VERSION`, `CHANGELOG.md`, `README.md` — 1.0.0 → 1.1.0
- `skills/initialize-project/scripts/initialize_project.py` — `LIBRARY_VERSION` synchronized to the bumped `VERSION` (required by the validator; no behavior change)

**Deprecated / deleted:** none.

## Evals

One new block covering the required minimum plus six fixtures — **7 evaluation units added**.

- Positive: check a months-old item's claims before planning.
- Negative: "it's stale — revise the approach and implement" (the workflow must refuse to plan or edit).
- Ambiguous: "is this still worth doing?" — check claims, return a verdict, leave worth to the caller.
- Expected outputs, invariants (read-only, no edits, no proposed approach, no follow-up filed, caller decides, unverifiable stays unverified, conservative when torn, targeted reads only), and failure cases (stale claim confirmed from the item's own wording, whole-file reads or a full test run used as the check, assumption used to resolve an unverifiable claim, non-falsifiable priority treated as a staleness signal, verdict withheld as "it depends", findings extended into a plan).
- Scenario fixtures: symbol moved; item partly solved by later work; cosmetic rename; unreachable external claim; item with no falsifiable claims; item already fully resolved.

Collision coverage is carried by the negative and ambiguous cases plus the catalog's do-not-use column; the closest capability is separated by responsibility rather than by added synonyms.

## Archetype and overlay integration

**None, deliberately.** The archetypes in this library compose through execution-DAG stages and capability expectations, not a flat skill list. Adding this capability to the `development` archetype would require introducing a DAG stage, which is a structural change to that archetype's model and is not warranted by one skill that applies to any tracker rather than specifically to the OpenSpec-driven development flow. Per the promotion contract, a capability is not added to an archetype merely to increase visibility. Discoverability is served by the capability catalog, the skills catalog, keywords, `related` links, and the refreshed presentation index.

## Validation

| Validation | Result | Evidence or limit |
|---|---|---|
| `python3 tools/validate_commons.py` | PASS | `skills=47 agents=4 errors=0 warnings=0`, rc=0 |
| `python3 tools/refresh_commons_presentation.py` | PASS | `Skills: 46 -> 47`; `network relationships: 515 -> 520`; re-run after the version bump |
| `python3 tools/refresh_commons_presentation.py --check` | PASS | `Presentation data: CURRENT`, rc=0 |
| `python3 tools/check_presentation_visual_contract.py` | PASS | `Presentation visual contract: PASS`, rc=0 — no CSS, theme, structure, SVG, or interaction drift |
| `python3 tools/runtime_adapters.py validate` | PASS | `runtimes=4 errors=0` |
| `python3 tools/resolve_archetypes.py validate` | PASS | `archetypes=4 overlays=8 errors=0` |
| `python3 tools/build_capability_index.py` | PASS | index regenerated; validator's staleness check subsequently clean |
| Eval YAML parses | PASS | 47 skill blocks; new block exposes all 7 keys and 6 scenarios |
| Confidentiality scan of full diff + new file | PASS | No project, client, personal, host, path, or business-domain identifier. One illustrative phrase traceable to a real source change was neutralized before commit. |
| Behavioral eval execution | **NOT RUN** | This repository's eval scenarios are declarative expectations, not an executable harness. The promoted behavior was not exercised against a live model. Recorded as a limit, not converted into a pass. |
| Source-project regression | **NOT APPLICABLE** | The source project is read-only in this workflow and keeps its own local asset; nothing there was changed or removed. |

Two validator errors surfaced mid-promotion and were fixed rather than worked around: presentation staleness after the version bump, and `VERSION` disagreeing with the initializer's `LIBRARY_VERSION`.

## Git boundary

- **Pre-change status:** clean at `cec57b6` (`initial commit`), no staged, unstaged, or untracked work.
- **Post-change status:** 10 modified files plus one new skill directory and this report — every path attributable to this promotion.
- No unrelated work existed to preserve, and none was absorbed.

## Narrative impact

**None requiring the presentation workflow.** This adds one capability inside the existing skill model; it introduces no new archetype, composition model, promotion model, runtime architecture, agent model, or governance boundary. Only generated factual data changed (counts, navigator, search, previews, network nodes). The authored hero, value proposition, architecture story, and use-case storyline were not touched and do not need revision. `update-commons-presentation` is **not** recommended for this change.

## Limitations and follow-ups

1. **Execution frequency unevidenced.** Adoption rests on the capability being wired as a mandatory pre-planning step and on its extraction from previously inline behavior. No stored run transcript was located, so how often it has actually run is unknown. The eval block encodes the intended contract; the first real uses should be checked against it.
2. **No executable eval harness.** Scenarios are declarative. The invariants most worth exercising early are *read-only* and *caller decides* — both are behaviors a model can plausibly violate under pressure to be helpful.
3. **Pre-existing adapter gap, deliberately untouched.** The Codex skill-interface registry was already missing `polish-html-artifact` before this promotion. The validator only rejects unknown extras, not omissions, so this is not a gate failure. It was left alone to keep the promotion commit free of unrelated work; it is worth a separate fix.
4. **Remaining candidates unapproved.** Seven further P0 candidates across the two source reviews remain proposals. Their IDs stay valid selectors; none is authorized by this promotion.
