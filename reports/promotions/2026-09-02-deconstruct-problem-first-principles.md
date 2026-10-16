# Promotion — deconstruct-problem-first-principles

- **Promotion ID:** PROMO-2026-09-02-02
- **Date:** 2026-09-02
- **Source review:** `docs/commons-review-user.md` / `docs/commons-review-user.json` in the source project (user-level companion review, dated 2026-08-26)
- **Selected:** `P0-008` — first-principles problem deconstruction before planning
- **Also selected in the same invocation:** `P0-003`, promoted separately on its own branch (`PROMO-2026-09-02-01`).
- **Merged in:** `DNP-018`, the domain-general variant of the same method, folded into this body rather than promoted as a second capability.
- **Excluded:** every other candidate across both source reviews.

## Baseline note

Built on `origin/main` at `817242f` after the stale-baseline finding recorded in `PROMO-2026-09-02-01`:
the two earlier promotions were validated against a local `main` 82 commits behind the shared remote. The
overlap analysis below was re-run against the actual canonical tree, and `VERSION` is left unchanged with
the entry appended under the accumulating `v1.1.0` heading, matching the repository's observed convention.

## Revalidation

| Field | Decision |
|---|---|
| Selection evidence | Explicit stable ID `P0-008` |
| Primary evidence | A user-level agent definition carrying the five-step method with a bounded output contract, read-only by construction; its domain-general command sibling; and — the decisive part — the source project's own instructions, which make the deconstruction **mandatory** before planning any non-trivial task, invoke it as a numbered step in the item-implementation workflow, and maintain a companion knowledge asset of worked examples drawn from that project's history. Both source files re-verified present on 2026-09-02. |
| Reuse | Any problem that can be stated and checked against evidence. The engineering framing reflects where it is invoked, not a limit. |
| Existing overlap | Re-run against `origin/main` (49 skills, 4 agents, catalogs, templates). A full-text search for first-principles, assumption-stripping, inversion, and deconstruction language returns **one** hit: the phrase "Broken invariant" as a column header in an acceptance-audit report template — a coincidental match in a reporting structure, not a capability. `plan-work` remains the closest neighbour and still opens from *"an approved objective"*, recording assumptions in its output without ever challenging them. `deep-research` gathers evidence for a topic; `architecture-reviewer` challenges a design that already exists. Nothing occupies the step before planning. |
| Generalization | Merged the two source variants into one body. Removed the runtime model pin, the tool-restriction syntax, the delegation framing, and the source project's example vocabulary. The domain-general variant was authored in mixed German and English; the canonical body is single-language. |
| Abstraction | **Skill.** The value is the method, not independence of judgment. The source expresses it as an agent because its runtime spells "run this in a fresh context" that way; the canonical agent policy is explicit that a wrapper needs to add something a skill delegated to a fresh context cannot. |
| Maturity | Mandatory in the source project's instructions before any non-trivial plan, wired into its implementation workflow, and supported by a maintained corpus of worked examples. |
| Confidentiality | Safe. Diff scan found no identifier, project path, German fragment from the source variant, runtime model pin, or tool-restriction syntax. |
| External provenance | Not applicable. The method is long-standing general practice, independently expressed here; nothing was copied or adapted from a third-party package. |
| Collision risk | Positive: *"before we plan this, work out what the actual problem is."* Negative: *"you already know the cause; write the plan and sequence the tasks"* — routes to `plan-work`. Encoded as evals and in the catalog do-not-use column, and reinforced by the body's explicit hand-off boundary. |
| Action | Create (with `DNP-018` merged in) |
| Disposition | `PROMOTE_MERGE` |

## Candidate table

| Candidate | Selected by | Evidence | Overlap | Action | Disposition | Result |
|---|---|---|---|---|---|---|
| P0-008 first-principles deconstruction | Stable ID `P0-008` | Mandatory pre-planning step in source instructions; agent definition; worked-example corpus | `NEW`; sole textual hit is a coincidental report-template header | Create | `PROMOTE_MERGE` | Promoted as `deconstruct-problem-first-principles`, absorbing `DNP-018` |

## Files

**Created**
- `skills/deconstruct-problem-first-principles/SKILL.md` (82 lines)
- `reports/promotions/2026-09-02-deconstruct-problem-first-principles.md` (this report)

**Updated**
- `evals/skills/scenarios.yaml` — new evaluation block
- `catalog/capabilities.yaml` — new entry
- `catalog/skills.md` — catalog row, placed immediately before `plan-work` so the sequence reads in order
- `catalog/capability-index.json` — regenerated
- `adapters/codex/skill-interfaces.yaml` — native interface entry
- `presentation/assets/library-data.js`, `presentation/agent-commons.html` — deterministic factual refresh
- `CHANGELOG.md` — entry appended under the existing `v1.1.0` heading

**Deprecated / deleted:** none. `VERSION` deliberately unchanged.

## Evals

One block: positive, negative (routes to `plan-work`), ambiguous, six expectations, seven invariants, seven
failure cases, and six scenario fixtures — **one block plus six fixtures added**.

Two fixtures guard against over-application rather than under-application, which is the likelier failure for
a method this appealing: a *local patch is correct* case where choosing the symptom level is the right
answer and must not read as analytical failure, and a *constraint is a product decision* case that must stop
and return rather than inventing a technical approach to cover a business gap. A third — *cannot be
restated* — encodes that failing step 2 is itself the finding.

## Archetype and overlay integration

**None.** Archetypes compose through execution-DAG stages, and this capability sits *before* the
specification stage rather than inside the flow, applying equally to work that never enters an archetype.
Adding it would be visibility-driven, which the promotion contract prohibits. The `related` link to
`plan-work` and the adjacent catalog placement carry discoverability instead.

## Validation

| Validation | Result | Evidence or limit |
|---|---|---|
| `python3 tools/validate_commons.py` | PASS | `skills=49 agents=4 errors=0 warnings=0`, rc=0 |
| `python3 tools/refresh_commons_presentation.py` | PASS | `network relationships: 536 -> 541` |
| `python3 tools/refresh_commons_presentation.py --check` | PASS | `Presentation data: CURRENT`, rc=0 |
| `python3 tools/check_presentation_visual_contract.py` | PASS | `Presentation visual contract: PASS`, rc=0 |
| `python3 tools/runtime_adapters.py validate` | PASS | `runtimes=4 errors=0`; `interfaces: 47` |
| `python3 tools/resolve_archetypes.py validate` | PASS | `archetypes=4 overlays=8 errors=0` |
| `python3 tools/build_capability_index.py` | PASS | regenerated; validator staleness check clean |
| Eval YAML parses | PASS | new block has 6 scenarios, 7 invariants, 7 failures |
| Confidentiality and generalization scan | PASS | No identifier, path, German fragment, model pin, or tool-restriction syntax |
| Behavioral eval execution | **NOT RUN** | Scenarios are declarative; no executable eval harness in this repository. |
| Source-project regression | **NOT APPLICABLE** | Source assets read-only; the user-level originals are untouched and remain in place. |

## Git boundary

- **Base:** `origin/main` at `817242f`.
- **Branch:** `promote-deconstruct-problem`, created fresh and independent of `promote-generate-synthetic-fixtures` so either can land alone.
- **Pre-change status:** clean at the base commit.
- **Post-change status:** 7 modified files plus the new skill directory and this report.
- The two sibling branches touch the same catalog, eval, changelog, and generated files. Whichever merges second will need those regenerated against the updated base — a mechanical rebase, not a content conflict.

## Narrative impact

**None requiring the presentation workflow** on its own. One capability added inside the existing skill
model; no new archetype, composition model, runtime architecture, agent model, or governance boundary.

One signal worth recording for later, not acted on here: this capability sits *before* the library's
existing evidence-to-plan chain rather than inside it, which is a small extension of the lifecycle story
the presentation tells. One skill does not justify rewriting authored narrative. If a second pre-lifecycle
capability is promoted, the framing is worth revisiting via `update-commons-presentation`.

## Limitations and follow-ups

1. **No executable eval harness.** The invariants worth exercising are the two over-application guards — that a symptom-level choice is accepted as correct, and that an unresolved product decision stops the analysis instead of being papered over with a technical approach.
2. **Sequence enforcement is stated, not checkable.** "No conclusion before step 3" is the method's core and nothing can verify it was followed; a deconstruction written backwards from a predetermined answer would look identical.
3. **The user-level originals remain in place.** Both source variants still exist outside this library. Nothing was deleted, per the read-only source rule, but the maintainer may want to retire them in favor of the canonical capability now that it exists.
4. **`P0-005` still needs re-evaluation.** `origin/main` now carries a `mutation-testing` skill that `test-driven-development` delegates to; that proposal must be re-assessed against it before any promotion. Not in this selection.
