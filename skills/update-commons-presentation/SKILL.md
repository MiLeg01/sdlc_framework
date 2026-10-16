---
name: update-commons-presentation
description: Bring the standalone Agent Commons sales and technical presentation up to date after meaningful canonical-library changes by refreshing generated facts first, classifying narrative impact, making only warranted authored-content changes, preserving the locked visual system, and running technical and visual QA. Use after releases, promotions, new capabilities, architecture or governance changes, or when asked to refresh or update the Agent Commons presentation. Do not use for factual synchronization alone when the deterministic refresh tool is sufficient, to redesign the presentation, or to change claims without canonical evidence.
---

# Update the commons presentation

Keep repository facts automatic and storytelling deliberate.

## Refresh facts first

1. Inspect repository instructions, Git status, the current presentation, its README, and recent meaningful
   presentation history. Preserve unrelated work and never absorb unknown edits into a commit.
2. Run `python3 tools/check_presentation_visual_contract.py` before editing. Stop if the visual system has
   already drifted; presentation maintenance must not establish a new visual baseline.
3. Run `python3 tools/refresh_commons_presentation.py` before evaluating narrative changes.
4. Run `python3 tools/refresh_commons_presentation.py --check`. Stop if generated data remains stale or
   invalid. Fix canonical metadata or the generator rather than hand-editing generated data.
5. Inspect the generated change report, Git diff, changelog, version, new or removed capabilities,
   archetype and overlay composition, runtime changes, promotion workflow, and governance changes.

## Classify narrative impact

Assign exactly one classification and record the evidence:

- `FACTUAL ONLY`: counts, names, small utilities, evals, removals, or renames already represented by the
  generated navigator, search, previews, and network. Leave authored narrative unchanged.
- `MINOR NARRATIVE IMPACT`: a notable capability such as TDD, localization, or one specialist agent changes
  an existing proof point. Update only the smallest relevant existing section.
- `MAJOR NARRATIVE IMPACT`: a new archetype, composition model, promotion lifecycle, runtime architecture,
  agent model, governance boundary, or external ecosystem changes the actual story. Update affected
  sections while preserving every still-correct section.

When evidence is ambiguous, prefer the lower-impact classification and report the uncertainty. Do not use
the desire for a fresher presentation as evidence of an architectural change.

## Update authored content deliberately

- Treat `presentation/index.html` as the authored shell and its local generated `library-data.js` asset as
  canonical presentation data. Never edit the generated asset directly.
- The visual system is immutable. Only generated facts and authored textual content may change. Never modify
  CSS, theme metadata, typography, palette, spacing, layout or DOM structure, navigation, animation, inline SVG,
  visual identity, interaction behavior, runtime scripts, or offline operation.
- Do not treat requests to refresh, update, improve, polish, or modernize this presentation as permission to
  change its design. Do not update or rebaseline `presentation/visual-contract.json` during this workflow.
- Keep claims traceable to current canonical files. Do not present planned capabilities, unsupported
  runtimes, obsolete paths, or inferred relationships as implemented.
- Fit a minor change into an existing section. For a major change, revise only the sections whose argument
  is no longer correct; do not restructure the whole presentation by default.
- Keep capability counts, navigator entries, previews, search terms, and network relationships out of
  authored copy whenever generated data can supply them.

## Validate the result

For factual-only changes, run the deterministic check and presentation static validation. For any authored
narrative change, also read and apply the canonical `validate-visual-artifact` skill rather than copying its
methodology.

At minimum verify:

- hero, architecture explanation, capability network, navigator, one skill preview, one agent preview, and
  the affected sales sections;
- desktop, laptop, and mobile widths, plus any presentation viewport already required by repository policy;
- console health, keyboard interaction, local asset loading, responsive overflow, and offline behavior;
- every changed claim against current repository state;
- `python3 tools/check_presentation_visual_contract.py` with no visual-contract drift;
- `python3 tools/refresh_commons_presentation.py --check` and repository-required validation.

Report unavailable browser or viewport coverage as a limit, never as a pass.

## Finish with an auditable result

State the impact classification, generated factual changes, authored sections changed or intentionally left
unchanged, technical validation, visual QA evidence or limits, remaining stale narrative risk, and the exact
commit boundary. Do not claim completion while factual data is stale or a changed claim is unsupported.
