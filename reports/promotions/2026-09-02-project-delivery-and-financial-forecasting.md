# Promotion — project delivery and financial forecasting

- **Promotion ID:** PROMO-2026-09-02-01
- **Date:** 2026-09-02
- **Selected external candidates:** `ext-github-community-discovery-footprintai-open-sdlc-skills` and `ext-github-community-discovery-m-binimran-finance-pack`
- **Relationship:** `INSPIRED-BY`
- **Excluded:** all runtime-specific commands, hooks, MCP integrations, installation layouts, automatic tracker/deployment/release mutation, investment-analysis content, and permanent coordinator or Scrum wrappers.

## Revalidation

Both sources were re-reviewed at immutable Git revisions before implementation. The review inspected source
text and repository metadata only; no external package, hook, connector, installer, or command was executed.

| Candidate | Revision | License | Reusable contribution | Promotion result |
|---|---|---|---|---|
| `m-binimran/finance-pack` | `35ff1b49e7ffa1708296b84503a4e4236fbbff48` | MIT | driver-based project forecasting, actual/forecast separation, scenario analysis, and independent numerical review | New skill, calculator, synthetic example, and reviewer agent |
| `FootprintAI/open-sdlc-skills` | `75b71b8bb038fdf45df07c9c3258bc08641f04fa` | Apache-2.0 | cross-workstream delivery governance, evidence-derived status, dependency flow, RAID, and action-oriented reporting | New skill, analyzer, synthetic example, and composition overlay |

The implementation was written from the generalized concepts and existing Commons conventions. No external
source prose, code, package structure, or runtime-specific role definition was copied.

## Abstraction and overlap decisions

- `manage-project-delivery` is a **skill** because it is a reusable governance workflow. It owns delivery
  health, dependencies, milestones, RAID, decisions, cadence, and status; it does not replace `plan-work`,
  `coordinate-parallel-agents`, `implement-ready-slice`, or `audit-delivery-traceability`.
- `forecast-project-financials` is a **skill** because the forecasting workflow is reusable and does not need
  an independent execution context. It is distinct from `estimate-adm-modernization`, which estimates effort
  before or during modernization planning rather than reconciling live project revenue, cost, margin, and EAC.
- `financial-forecast-reviewer` is an **agent** because independent recomputation and specialist numerical
  challenge materially reduce confirmation bias for consequential forecasts. It is read-only and cannot grant
  commercial approval.
- The delivery analyzer and forecast calculator are **tools** because their validation and arithmetic are
  deterministic.
- The examples are **templates** containing synthetic data only.

## Harness neutrality and optional consulting adaptation

Canonical instructions contain no Codex, Claude Code, Cline, OpenCode, GitHub, MCP, or provider-specific
orchestration. The existing adapter generator renders the canonical skills and reviewer into supported runtime
representations.

The optional `consulting-delivery` overlay composes both skills, both deterministic tools, both synthetic
examples, and the independent reviewer for development, legacy-migration, and research projects. It is safe
for an Accenture project to select the overlay and map generic responsibilities to approved local titles and
methods. Accenture names, branding, rate cards, commercial thresholds, approval routes, client identifiers,
and business data deliberately remain in project-local configuration and artifacts rather than Commons.

## Files

**Created**

- `skills/manage-project-delivery/` — workflow, analyzer, and delivery-register example.
- `skills/forecast-project-financials/` — workflow, calculator, and financial-forecast example.
- `agents/financial-forecast-reviewer.yaml` — independent numerical reviewer.
- `archetypes/overlays/consulting-delivery/overlay.yaml` — optional composition profile.
- `evals/fixtures/project-controls/` and `evals/tools/test_project_controls.py` — deterministic fixtures and tests.
- Two revision-pinned external reviews under `external/reviews/`.

**Updated**

- Capability, skill, agent, tool, archetype, adapter, evaluation, Golden, and contract registries.
- External capability index with both reviewed candidates marked `INCORPORATED` and `INSPIRED-BY`.
- Generated capability index and presentation data.
- `VERSION`, `README.md`, `CHANGELOG.md`, and initializer version to `1.2.0`.

**Deleted or deprecated:** none.

## TDD and mutation evidence

- RED: `python3 -m unittest evals.tools.test_project_controls` initially failed because neither deterministic
  tool existed.
- GREEN/REFACTOR: the suite passes with 13 tests covering valid calculations, dependency cycles, unknown
  dependencies, blocked and unowned work, due-date and risk boundaries, completed delivery, duplicate or empty
  periods, missing historical actuals, zero denominators, scenario arithmetic, and explicit output paths.
- Targeted mutation testing used `mutmut 2.5.1` in an isolated temporary environment with only arithmetic and
  comparison operators enabled. The first run exposed meaningful survivors for empty-input validation, EVM
  cost and schedule variance, EVM variance at completion, risk bounds, complete-state detection, and due-date
  boundaries. Tests were strengthened and those mutants were killed.
- Final targeted result: 57 operator mutants, 51 killed, 6 survived. The six remaining mutants affect only
  type-annotation syntax or the CLI `__main__`/newline boundary that mutmut's import-based subprocess isolation
  cannot exercise; repository subprocess tests cover both CLI execution and JSON output. No meaningful
  financial or delivery-rule mutant survived.
- `mutmut 3.3.1` was also attempted first but produced process-crash statuses on this macOS/Python 3.9
  environment. That run was rejected as infrastructure evidence and was not reported as a pass.

## Validation

| Validation | Result |
|---|---|
| Project-control unit suite | PASS — 13 tests |
| Archetype composition suite | PASS — 29 tests |
| Targeted operator mutation run | PASS with six classified non-behavioral/tool-isolation survivors; all meaningful survivors killed |
| `python3 tools/resolve_archetypes.py validate` | PASS — 4 archetypes, 9 overlays, 0 errors |
| `python3 tools/runtime_adapters.py validate` | PASS — 4 runtimes, 0 errors |
| `python3 tools/external_capabilities.py validate` | PASS — 8 sources, 2 candidates, 0 errors, 0 warnings |
| `python3 tools/refresh_commons_presentation.py --check` | PASS — presentation data current |
| `python3 tools/check_presentation_visual_contract.py` | PASS — immutable visual contract preserved |
| `python3 tools/validate_commons.py` | PASS — 50 skills, 5 agents, 0 errors, 0 warnings |
| Changed-scope standard evaluation | 65 PASS, 34 WARN, 1 environment-local HARD_FAIL. Warnings are unavailable semantic executor results. The hard failure is the `initialize-project` no-argument fixture expecting an unresolved runtime while this checkout contains an ignored `.claude/` runtime marker; the same test passes against a clean archive of `HEAD`. Project-control, external-index, Azure-shard, installer, archetype, and deterministic contracts pass under Python 3.11. |

The promotion report is contained in the same focused commit as the promoted capabilities.

## Confidentiality and provenance

All examples use synthetic identifiers and values. No client data, credentials, internal URLs, workstation
paths, proprietary excerpts, or source-project identities are present in canonical capability bodies. External
source identity is retained only in the governed provenance index and review records.

## Narrative impact

**MINOR NARRATIVE IMPACT.** The capability model is unchanged, but the library gains a new optional overlay and
an independent reviewer specialization. The deterministic presentation data was refreshed and its visual
contract verified. Authored presentation text and design were not changed; a later presentation-maintenance
task may add a concise delivery-controls proof point if product messaging requires it.
