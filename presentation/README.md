# Agent Commons presentation

This directory contains the standalone, offline Agent Commons technical and executive presentation. It
positions the library as a reusable engineering operating system while preserving the current editorial
visual system and interactive capability exploration.

## Open it

Open [`agent-commons.html`](agent-commons.html) directly in a current browser for the portable single-file
artifact. It embeds all presentation data and has no companion-file, backend, framework, remote font,
analytics, tracking, or runtime API dependency. A local HTTP server is needed only when a browser automation
tool restricts `file:` URLs.

[`index.html`](index.html) is the authored development shell. It deliberately loads the generated local
`assets/library-data.js` file so authored markup and generated repository facts remain separate during
maintenance.

The presentation supports mouse, touch, keyboard navigation, focus mode, search, filters, capability
previews, reduced motion, forced-colors mode, and landscape printing.

Presenter keys: `→` / `PageDown` / `j` advance a chapter, `←` / `PageUp` / `k` go back, `Home` and `End`
jump to the first and last chapter, `F` toggles focus mode, and `Esc` leaves it. `ArrowUp`, `ArrowDown`,
and `Space` are deliberately left unbound so ordinary keyboard scrolling still works. Inside the capability
graph, `Tab` reaches the diagram once, the arrow keys move between nodes, and `Enter` opens a node.

The legacy-modernization use case also shows the post-initialization runtime sequence. Project governance is
written to `AGENTS.md`; `.agent-commons.yaml` records project-specific composition and the next action; the
runtime resolves the selected stable capability ID to the canonical Commons skill. The manifest configures
the workflow but does not execute automatically, and canonical workflow bodies are not copied into projects.

Archetypes participate before runtime execution: initialization resolves one or more project-family profiles,
overlays, and conditions into deduplicated stable skill, agent, tool, and template IDs. The initialized project
retains the archetype selection as configuration and provenance. Day-to-day work invokes the resolved
canonical skills; the archetype itself is not an executable workflow.

## Generated facts

`tools/refresh_commons_presentation.py` reads the canonical repository and atomically regenerates both
`assets/library-data.js` and the portable `agent-commons.html` artifact. The generated payload includes:

- current capability counts;
- navigator records and bounded source previews;
- capability-network nodes and relationships;
- archetype and overlay composition;
- adapter support;
- evaluation relationships;
- deterministic tools and templates;
- current external source-registry metadata.

Do not edit either generated file directly. Correct canonical metadata, the authored shell, or the generator,
then refresh.

The explanatory copy in `index.html` is authored content. Its visual and interaction system is locked by
`visual-contract.json`: CSS, theme metadata, typography, palette, spacing, layout and DOM structure,
navigation, animation, inline SVG, interaction behavior, and runtime scripts must not change. Presentation
maintenance may update only generated facts and textual content. Never rebaseline the contract as part of a
refresh, polish, modernization, or content-update task.

## Refresh and validate

From the repository root:

```bash
python3 tools/refresh_commons_presentation.py
python3 tools/refresh_commons_presentation.py --check
python3 tools/check_presentation_visual_contract.py
python3 -m unittest \
  evals.tools.test_presentation_sync \
  evals.tools.test_presentation_visual_contract \
  evals.tools.test_presentation_maintenance_contract
python3 skills/validate-visual-artifact/scripts/validate_html.py presentation/index.html --json
```

Authored narrative changes also require real-browser QA. At minimum inspect the hero,
architecture explanation, capability network, navigator, a skill preview, an agent preview, desktop,
laptop, tablet, mobile, keyboard interaction, console output, local assets, overflow, print, and offline
behavior.

## Security boundary

Source previews are bounded and sanitized. The presentation must not expose credentials, private project
state, client content, local workstation paths, disposable caches, or development-history artifacts.

The locked visual thesis is `agent-commons-ultraviolet`: a dark ultraviolet technical stage, luminous
capability signals, native technical diagrams, and a neutral Agent Commons identity. Local screenshots and
browser traces belong under ignored output paths and are never canonical presentation input.
