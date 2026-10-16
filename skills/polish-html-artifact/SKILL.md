---
name: polish-html-artifact
description: Perform a bounded visual-finesse pass on a structurally and factually complete HTML dashboard, presentation, or technical narrative without changing its information architecture, narrative, claims, or interaction model. Use after generation and before independent validation when the artifact is correct but not yet visually finished. Do not use to invent content, redesign product structure, establish a client brand, or replace independent visual and accessibility review.
---

# Polish a complete HTML artifact

Improve execution, not intent. The artifact's structure, content authority, brand, narrative, and interaction
contract must already be resolved.

## Bind the invariants

Before editing, record the artifact, accepted content source, structural or narrative order, stable IDs,
primary interactions, brand authority, locales, target viewports, and current validation state. Capture a
representative rendered baseline. If these invariants cannot be established, return to the generating skill
instead of guessing.

For a canonical living dashboard, section order, navigation groups, data model, requirements/specifications/
traceability grammar, and shared detail opener are immutable unless the user explicitly authorizes a product
change. For a presentation, preserve the approved story, section order, claims, evidence, and call to action.

## Diagnose before styling

Read [references/finesse-checklist.md](references/finesse-checklist.md). Identify the smallest set of visual
causes behind the unfinished result, such as weak type contrast, uniform spacing, repetitive composition,
excessive surfaces, unintegrated diagrams, crude tables, noisy controls, or desktop-only layout. Separate
brand identity from canonical quality and do not import reference-specific palettes, fonts, logos, content,
or exact compositions.

## Apply a bounded finesse pass

Work through reusable tokens and existing components before adding one-off rules:

- refine display, body, metadata, data, code, and table typography plus readable line lengths;
- make section, component, and inline spacing communicate different levels of grouping;
- clarify primary, secondary, supporting, and control hierarchy within existing sections;
- replace unnecessary cards with alignment, rules, whitespace, or a shared surface;
- improve tables, record registers, navigation, dialogs or drawers, diagrams, charts, and evidence paths;
- recompose existing responsive layouts so priority survives narrow widths and long localized text;
- add only short state or relationship transitions and preserve reduced-motion parity;
- keep focus, contrast, keyboard behavior, print/offline requirements, and client-brand tokens intact.

Do not change facts merely to fit a layout. Do not hide difficult content, collapse required sections, alter
stable IDs, reorder the story, replace useful tables with cards, or create visual effects to compensate for
weak hierarchy.

## Render, compare, correct

Inspect actual browser output at the required states and viewports. Compare typography, composition,
whitespace, hierarchy, density, cohesion, restraint, interaction, and responsiveness against the accepted
brief rather than pixel similarity to a reference. Make at least one small correction batch after rendered
inspection when the task calls for a dedicated polish pass.

Then hand the completed artifact to `validate-visual-artifact` and, for consequential delivery, to
`accessibility-review`. The person or agent performing independent validation should not rely on the polish
author's aesthetic claim.

## Handoff

Report protected invariants, visual causes found, token and component changes, rendered states reviewed,
correction iterations, validation handoff, remaining limitations, and exact changed paths. Completion means
the artifact is materially more composed while its structure, content, brand authority, and behavior remain
unchanged.
