# Agent Commons repository governance

## Scope

This repository is the canonical source for validated reusable agent-engineering capabilities. Runtime
adapters may derive native Codex, Claude Code, Cline, or OpenCode representations, but canonical workflow
and role bodies must remain single-source and runtime-neutral.

## Editing rules

- Keep canonical capabilities generic and free of workstation paths, private project identities, and
  historical source-project attribution.
- Never add credentials, internal URLs, client screenshots, proprietary source excerpts, or real
  business data.
- Use synthetic examples and parameterized paths.
- Add or update an evaluation whenever a skill, agent, or archetype changes behavior.
- A canonical capability change is safe only after evaluating its own contract, impacted dependent
  capabilities, and at least one representative workflow. Applicable quality dimensions include correctness,
  completeness, evidence grounding, traceability, runtime, and context efficiency.
- Judge every capability change across `OWN BEHAVIOR + DEPENDENTS + E2E WORKFLOW`. A reduction in correctness,
  completeness, or evidence grounding cannot be justified solely by lower runtime or token use.
- Keep generated output out of canonical source files. Fix generators or canonical inputs instead.
- Put runtime-specific paths, syntax, precedence, and limitations under `adapters/` or installation logic.
- Never maintain one canonical capability body separately for each runtime.
- For supported implementation projects, passing tests alone are not sufficient evidence of test quality.
  After TDD reaches GREEN and REFACTOR, use targeted mutation testing for changed critical behavior and
  strengthen tests against meaningful surviving mutants.
- Run `python3 tools/validate_commons.py` before committing.
- Keep release documentation focused on the current product; do not add development-history reports,
  private provenance, browser traces, or benchmark archaeology.

## Git commits

- Use a short, meaningful, human-readable subject that describes the actual change.
- Never use Conventional Commit type prefixes such as `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`,
  `test:`, `style:`, `perf:`, `build:`, or `ci:` in any capitalization or scoped variant.
- On a task branch, inspect the branch name and prefix a reliably detected ticket as `[TICKET-ID]`; do not
  infer a ticket from an ambiguous number and never invent `[NO-TICKET]` or a similar placeholder.
- Never add `Co-authored-by` or agent-attribution trailers such as `Generated-by`, `Created-by`, or
  `Assisted-by` unless the user explicitly requests such metadata.

## Presentation visual lock

- The visual system in `presentation/index.html` is immutable. Presentation maintenance may update only
  generated facts and authored textual content.
- Never change its CSS, theme metadata, typography, palette, spacing, layout or DOM structure, navigation,
  animation, inline SVG, interaction behavior, or runtime scripts during a presentation refresh.
- Do not reinterpret requests to refresh, update, improve, polish, or modernize the presentation as design
  authorization. Do not update the visual contract as part of the same task.
- Run `python3 tools/check_presentation_visual_contract.py` after every presentation change. A failure blocks
  completion and must be resolved by reverting the visual drift.

## Classification

- A skill explains a bounded workflow.
- An agent exists only when independent delegated judgment adds value.
- A tool performs deterministic work.
- A template provides reusable structure without reasoning.
- An archetype composes capabilities for a project family.
- Project-specific behavior stays in its project and is not promoted into canonical assets.
