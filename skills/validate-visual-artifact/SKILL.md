---
name: validate-visual-artifact
description: Independently validate a completed HTML dashboard, presentation, portal, or web UI through static checks and bounded real-browser inspection. Use after a complete artifact exists and before consequential review or release. Do not use to invent the initial design, replace accessibility or business acceptance testing, or claim browser coverage when required states are unreachable.
---

# Validate a visual artifact

Review an implemented artifact; do not use QA to invent the initial design.

## Gate and static checks

Confirm the artifact, expected routes/sections, source state, target viewports, and acceptance criteria.
If incomplete, return to implementation. Run:

```bash
python3 scripts/validate_html.py <artifact.html> --json
```

For an artifact generated from an evidence-derived brand profile, run:

```bash
node scripts/capture_brand_qa.mjs --html <artifact.html> --brand-profile <brand-profile.json> \
  --artifact-kind <dashboard-or-presentation> --output <brand-qa.json>
python3 scripts/validate_html.py <artifact.html> --brand-profile <brand-profile.json> \
  --brand-qa <brand-qa.json> --peer-html <paired-artifact.html> --json
```

`capture_brand_qa.mjs` records desktop (1440x1000), tablet (768x1024), and mobile (390x844) states, each with
computed styles, visible identity, console health, and horizontal-reflow evidence. Validation rejects a
manifest that captures no viewport 480px or narrower, and any state that overflows horizontally or loses the
official identity. Never describe responsive behavior as validated from a single desktop capture.

Report five independent results where applicable: `STRUCTURE_PASS`, `STATIC_HTML_PASS`,
`BRAND_PROFILE_CONSISTENT`, `BRAND_FIDELITY_PASS`, and `VISUAL_QA_PASS`. Profile consistency verifies the
declared contract only; it must never imply fidelity. Fidelity additionally requires exact official favicon
and logo bytes, peer artifact agreement, source-evidenced colors, no visible generic fallback palette, and a
browser render that visibly expresses the resolved identity at every captured viewport.

Resolve structural blockers, duplicate IDs, external-dependency violations, missing accessibility labels,
or absent print/reduced-motion rules before browser work.

For a self-contained artifact and a JSON state matrix, capture reproducible browser evidence with:

```bash
node scripts/capture_visual_matrix.mjs --html <artifact.html> --states <states.json> \
  --output visual-qa/report.json --screenshot-dir visual-qa/screenshots
```

The helper uses the pinned Playwright runtime from `AGENT_COMMONS_NODE_MODULES` when present and launches
Chromium without its inner sandbox because the evaluation runtime already supplies an outer filesystem and
network sandbox.

## Browser matrix

1. Start the documented server or open the self-contained file; record commit/working-tree state.
2. Visit each in-scope route directly and through navigation. Exercise every primary control.
3. Cover populated, empty, loading, error, blocked, and success states when applicable.
4. Inspect named desktop, presentation, tablet, and mobile widths; include long labels/content and zoom.
5. Check hierarchy, typography, line length, spacing rhythm, alignment, density, contrast, icon meaning,
   affordances, focus, keyboard flow, overflow, clipping, sticky elements, dialogs, and resizing.
   Also assess composition, surface restraint, card use, table/register quality, diagram integration, visual
   rhythm, client-brand authority, and whether narrow layouts are recomposed rather than merely scaled.
6. Inspect console and failed resources. Test reset, refresh, return paths, fullscreen, and print where used.
7. Capture concise evidence for significant failures and report location, viewport/state, severity,
   rationale, reproduction, and smallest actionable fix.

For branded artifacts, capture computed styles for body, header, navigation, links, buttons, focus, panels,
and footer; dashboards additionally require status areas and tables/registers. Reject generic or unproven
visible colors even when the declared tokens match each other. Compare paired dashboards and presentations
against one normalized profile, asset fingerprint, exact favicon/logo hashes, and palette.

When visual references were supplied, compare quality dimensions rather than pixels: typography, composition,
whitespace, hierarchy, density, cohesion, polish, restraint, interaction, and responsiveness. Treat copied
identity, exact layouts, or reference-specific decorative effects as failures rather than fidelity.

For a localized artifact, validate every supported locale rather than only the default. At minimum for the
standard bilingual client-delivery pattern, cover English desktop, German desktop, English mobile, and German
mobile; exercise switching after representative filters, expansion, navigation, charts, and dialogs, then
reload once to verify configured persistence. Check long German text, residual English, language-control
semantics, document language, and offline behavior. Run the localization manifest validator before browser QA.

For public-sector dashboards, also confirm the persisted client policy selected the expected German locale,
German is the initial state, English remains available unless explicitly overridden, and the flag-only visual
control has explicit accessible language names. For public-sector sales presentations, validate the configured
German-only state, public-sector tone, client terminology and brand, localized human-readable diagram labels,
and the absence of an unnecessary bilingual runtime or language switch.

Use `references/review-matrix.md` to avoid vague aesthetic judgments. Route accessibility defects to an
accessibility review rather than treating visual review as a substitute.

## Corrections and completion

Fix only when implementation changes are in scope; otherwise report findings. Work in small correction
batches and retest affected interactions plus neighboring views. Complete with tested routes, states,
viewports, controls, console result, evidence paths, each independent pass/fail result, limitations, and
retest outcome. Never claim branded completion from schema validation, token presence, or fingerprints alone.
