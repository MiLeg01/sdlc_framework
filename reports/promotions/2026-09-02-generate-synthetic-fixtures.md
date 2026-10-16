# Promotion — generate-synthetic-fixtures

- **Promotion ID:** PROMO-2026-09-02-01
- **Date:** 2026-09-02
- **Source review:** `docs/commons-review.md` / `docs/commons-review.json` in the source project (dated 2026-08-26)
- **Selected:** `P0-003` — generate synthetic fixtures from a reviewed allowlist spec
- **Also selected in the same invocation:** `P0-008`, promoted separately on its own branch (`PROMO-2026-09-02-02`) because the two are unrelated capabilities.
- **Excluded:** every other candidate across both source reviews. `P0-002` landed previously; `P0-004` is still in flight on its own branch.

## Baseline correction

This promotion is the first to be built on the **actual** canonical state. The two prior promotions were
validated against a local `main` that was **82 commits behind `origin/main`**, because the earlier Git
boundary check inspected working-tree status and recent history on the current branch but never
`git log --all`, `git branch --all`, or `git remote --verbose`. The library is a shared remote repository,
not the local-only checkout those promotions assumed.

Consequences, established by re-checking rather than assumed:

- `validate-work-item-assumptions` (`P0-002`) **is** on `origin/main`, byte-identical to what was written.
- The `test-driven-development` change (`P0-004`) is **not** on `origin/main`. It sits on its own branch,
  merged via a pull request into a feature branch, still awaiting its own merge.
- Version handling in the prior promotions was wrong in form though harmless in effect: they bumped a minor
  version per promotion, while the repository accumulates entries under one unreleased heading. The team
  reconciled this by folding the `P0-002` entry into `v1.1.0` beside another contributor's work.
- The overlap analysis was therefore run against a stale tree. It has been **re-run against `origin/main`**
  for this candidate; the conclusion is unchanged, and the closest neighbour is byte-identical to the tree
  originally compared.

This promotion follows the observed convention: `VERSION` is unchanged and the entry is appended under the
existing `v1.1.0` heading.

## Revalidation

| Field | Decision |
|---|---|
| Selection evidence | Explicit stable ID `P0-003` |
| Primary evidence | Source project's fixture workflow: a declarative specification, a deterministic renderer, an extract-and-flag helper, structured-identifier detectors, and a dedicated test module asserting five distinct guarantees. Every committed fixture in that project is produced this way, and two accepted decision records establish the approach. Re-verified present at the source revision on 2026-09-02. |
| Reuse | Any suite needing realistic documents or records derived from sensitive originals that will be committed. Independent of language, document type, and domain. |
| Existing overlap | Re-run against `origin/main` (49 skills). `anonymize-data` is the only real neighbour and is **byte-identical** to the tree originally compared, so the boundary holds: it transforms structured records field by field and explicitly defers on binary documents and free text, stating they require an explicit extraction and review plan. This workflow is that plan, taking the generative rather than transformative route. No other capability generates test artifacts. |
| Generalization | Removed the entire persona and approved-value table, all real-format synthetic identifiers, addresses, personal and institution names, document-family renderer names, domain vocabulary, the specification's domain-specific content fields, and the language and toolchain. Promoted the *contract* — approved-value set, per-entry renderer selector, classification labels, content fields, dependent tokens — not the instance. |
| Abstraction | **Skill.** The core is judgment that cannot be automated: deciding, value by value, whether something is identity or load-bearing signal. The deterministic parts (renderer, detectors, checks) are project-owned artifacts the skill directs, not library tools, because their shape follows the document type. |
| Maturity | Every fixture in the source project is generated this way, with five guarantees enforced as ordinary tests in the normal suite. |
| Confidentiality | **This was the highest-risk candidate reviewed.** Its source evidence is a table of identity values and a domain vocabulary. Nothing from it was carried. Diff scan returned no identifier, persona value, address, institution, domain term, project path, or toolchain reference. |
| External provenance | Not applicable — internal origin, nothing copied or adapted. |
| Collision risk | Positive: *"build these fixtures so nothing real can leak into the repository."* Negative: *"strip the personal fields out of this production export before we commit it"* — routes to `anonymize-data`. Both directions are encoded as evals and in both catalog do-not-use columns. |
| Action | Create |
| Disposition | `PROMOTE_NEW` |

## Candidate table

| Candidate | Selected by | Evidence | Overlap | Action | Disposition | Result |
|---|---|---|---|---|---|---|
| P0-003 synthetic fixture generation | Stable ID `P0-003` | Specification, deterministic renderer, detectors, five enforced guarantees; two accepted decision records | `NEW`; `anonymize-data` neighbour re-verified unchanged on `origin/main` | Create | `PROMOTE_NEW` | Promoted as `generate-synthetic-fixtures` |

## Files

**Created**
- `skills/generate-synthetic-fixtures/SKILL.md` (89 lines)
- `reports/promotions/2026-09-02-generate-synthetic-fixtures.md` (this report)

**Updated**
- `evals/skills/scenarios.yaml` — new evaluation block
- `catalog/capabilities.yaml` — new entry, plus the reciprocal `related` link on `anonymize-data`
- `catalog/skills.md` — catalog row
- `catalog/capability-index.json` — regenerated
- `adapters/codex/skill-interfaces.yaml` — native interface entry
- `presentation/assets/library-data.js`, `presentation/agent-commons.html` — deterministic factual refresh
- `CHANGELOG.md` — entry appended under the existing `v1.1.0` heading

**Deprecated / deleted:** none. `VERSION` deliberately unchanged.

## Evals

One block: positive, negative (routes to `anonymize-data`), ambiguous, five expectations, seven invariants,
six failure cases, and six scenario fixtures — **one block plus six fixtures added**.

The fixtures encode the failures that matter: a reviewer proposing redaction because the result *looks*
clean; a public institution name that is load-bearing rather than identity; an unapproved identifier
appearing after regeneration (the specification is corrected, never the detector weakened); a structured
dataset that should route to `anonymize-data`; a renderer that reads the clock; and a structureless scan
that must be authored from its type rather than derived.

## Archetype and overlay integration

**None.** Archetypes here compose through execution-DAG stages and capability expectations rather than a
skill list. This capability applies wherever sensitive-source fixtures are needed and is not a stage in the
development or migration flow, so adding it would be visibility-driven, which the promotion contract
prohibits. Discoverability comes from the catalogs, keywords, the reciprocal `anonymize-data` relationship,
and the refreshed presentation index.

## Validation

| Validation | Result | Evidence or limit |
|---|---|---|
| `python3 tools/validate_commons.py` | PASS | `skills=49 agents=4 errors=0 warnings=0`, rc=0 |
| `python3 tools/refresh_commons_presentation.py` | PASS | `+ skill:generate-synthetic-fixtures`; `network relationships: 536 -> 542` |
| `python3 tools/refresh_commons_presentation.py --check` | PASS | `Presentation data: CURRENT`, rc=0 |
| `python3 tools/check_presentation_visual_contract.py` | PASS | `Presentation visual contract: PASS`, rc=0 |
| `python3 tools/runtime_adapters.py validate` | PASS | `runtimes=4 errors=0` |
| `python3 tools/resolve_archetypes.py validate` | PASS | `archetypes=4 overlays=8 errors=0` |
| `python3 tools/build_capability_index.py` | PASS | regenerated; validator staleness check clean |
| Eval YAML parses | PASS | 49 skill blocks; new block has 6 scenarios and 7 invariants |
| Adapter registry parses | PASS after repair | An intermediate edit wrote invalid JSON (missing separator) before validating. Caught by the parse check, repaired, and the edit re-applied parse-before-write. `interfaces: 47`. |
| Confidentiality scan | PASS | No identifier, persona value, address, institution, domain term, project path, or toolchain reference in the diff or the new file |
| Behavioral eval execution | **NOT RUN** | Scenarios are declarative; this repository has no executable eval harness. The promoted behavior was not exercised against a live model. |
| Source-project regression | **NOT APPLICABLE** | Source project read-only; nothing there changed. |

## Git boundary

- **Base:** `origin/main` at `817242f`, chosen explicitly after the stale-baseline finding above.
- **Branch:** `promote-generate-synthetic-fixtures`, created fresh so this promotion does not entangle with the in-flight `P0-004` branch.
- **Pre-change status:** clean at the base commit; no staged, unstaged, or untracked work.
- **Post-change status:** 7 modified files plus the new skill directory and this report — every path attributable to this promotion.
- No unrelated work was absorbed. The in-flight `P0-004` branch is untouched.

## Narrative impact

**None requiring the presentation workflow.** One capability added inside the existing skill model; no new
archetype, composition model, promotion model, runtime architecture, agent model, or governance boundary.
Only generated factual data changed. `update-commons-presentation` is **not** recommended.

## Limitations and follow-ups

1. **No executable eval harness.** The invariant most worth exercising is the routing split against `anonymize-data`, since the two are genuinely adjacent and a wrong route sends someone back to redaction — the exact failure this capability exists to prevent.
2. **Detector completeness is bounded by design.** Structured formats are detectable; personal names are not. The skill says so rather than implying otherwise, but a reader who skims could still over-trust the checks.
3. **No deterministic tool was promoted.** The renderer and detectors stay project-owned because their shape follows the document type. If several projects adopt this, a shared specification-schema validator would be the natural extraction — the validation contract is already stated precisely enough to build one against.
4. **Prior promotions were built on a stale baseline.** Their content revalidates, but their version bumps and catalog syncs were computed against a tree 82 commits behind. `P0-004` is still in flight and will need its version handling reconciled to the accumulating-heading convention when it merges.
5. **`P0-005` needs re-evaluation before any promotion.** `origin/main` now carries a `mutation-testing` skill that `test-driven-development` delegates to after GREEN and REFACTOR. Parts of that proposal may now be duplicate, and the remainder may belong as an update to that new skill rather than to `design-test-strategy`. It was not in this selection and was not acted on.
