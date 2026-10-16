---
name: create-branded-html-artifact
description: Create a polished evidence-aware HTML executive presentation, sales story, dashboard shell, or interactive technical narrative using resolved client branding or the Accenture fallback. Use when HTML is the chosen substantial deliverable and visual identity matters. Do not use for deterministic canonical-state dashboard generation, non-HTML delivery, or styling without an audience, evidence source, and visual brief.
---

# Create a branded HTML artifact

Derive a visual system from evidence; do not clone a marketing site or invent brand rules.

## Establish the brief

Confirm audience, single job, narrative or decision, artifact type, source material, factual authority,
interaction/print needs, delivery constraints, and definition of done. Read `references/brand-discovery.md`
before using a website, design system, screenshots, logo, or reference deck.

Inspect persisted client context before asking about language or brand. A supplied official client website
or corporate-design source can support brand discovery and sector/geography classification in parallel.
Do not wait for brand extraction before resolving independently available public-sector evidence. Never
replace an explicit client brand with a generic public-sector visual theme.

HTML delivery is mandatory once this workflow is selected. If no branding is supplied, or the supplied
brand source is unreadable or inaccessible, or cannot yield a usable official logo and core interface
palette, generate the
requested `.html` artifact with the bundled Accenture fallback. Mark the output `accenture-fallback`, retain
the requested source and failure reason in project evidence, and do not claim that the fallback represents
the client brand. Brand-resolution failure must not produce only a blocker document or suppress the HTML.

## Design in two passes

1. Extract verified signals: palette, typography roles, spacing rhythm, geometry, imagery, grid, motion,
   voice, logo rules, and accessibility constraints. Record source and confidence.
2. Write a compact design plan: 4-6 named colors, display/body/data type roles, layout thesis, and one
   meaningful signature element derived from the subject.
3. Critique the plan for generic dark-neon AI styling, glass cards, ornamental gradients, dashboard-tile
   clutter, default serif/cream editorial styling, or copied website composition. Revise before coding.
4. Keep proprietary fonts and assets out unless licensed and supplied. Use intentional local fallbacks.

Define a compact finesse layer as part of the plan: display/body/data type roles, readable measures, section and
component spacing, content widths, border and surface hierarchy, restrained radii and shadow, transition timing,
and chart/table/diagram treatment. Assign each major section a content role such as statement, evidence,
architecture, comparison, timeline, transition, or close so the artifact gains rhythm without changing its
narrative. Avoid repeating headline plus equal cards when the content relationship calls for a ledger, flow,
comparison, table, or single proof anchor.

For a supplied official URL, read `references/brand-profile-contract.md` and run
`scripts/resolve_brand_profile.py`. Required client branding remains unresolved until redirects, HTML,
linked stylesheets, manifest, metadata, inline SVG and image identity candidates, official favicon/logo
bytes, and exact source colors were inspected.
Map every emitted token to evidence and retain source, asset, theme, and profile fingerprints; do not treat
the presence of a URL or the word `client` as successful brand resolution.

Treat complete `--brand-*` custom properties as the highest-confidence fast path. When they are absent,
continue with semantic CSS interpretation: associate exact colors with selectors and declarations for
headers, navigation, links, primary controls, focus, errors, success, text, borders, cards, and page
backgrounds; include whether selectors match elements observed in the captured HTML, then rank candidates by
semantic strength, visible use, repetition, contrast, and accessibility. Resolve ordinary custom-property
references such as `var(--color-primary)` through their concrete definitions before interpreting the selector;
ignore scoped self-references that would erase an earlier concrete value. Associate error and success meaning
with the styled subject or directly related state, not merely an ancestor page name, and cap repetitive generic
link evidence so it cannot overwhelm explicit primary controls and tokens. Evaluate accessibility according to
the rendered role: text roles must contrast with their surface, while a fill accent must provide an accessible
foreground rather than also behaving as body text. A logo fill alone never proves a
global interface color, and a danger color never becomes the primary or header color. If an optional
functional color is unsuitable for text, prefer another exact evidenced color for that role or derive the
minimum accessible lightness adjustment while retaining the original observation. Missing optional status,
typography, or geometry tokens may use explicit low-confidence accessible defaults rather than discarding a
valid identity and core palette. Record observed parents, deterministic rules, confidence, and source
references for every derivation. Apply the Accenture fallback only when the official site cannot be inspected
or the logo or core primary/background/text palette remains unresolved; report all missing core evidence, not
only the first absent custom property.

Request identity transfer encoding and safely decode bounded gzip or deflate responses when an ordinary
server still returns compressed HTML, CSS, or assets. Unsupported encodings, invalid compressed bytes, and
decoded content over the capture limit remain fail-closed evidence failures.

Treat inline SVG as an official logo candidate only when its element or surrounding markup carries logo,
wordmark, brand, or header identity semantics. Preserve the exact captured SVG fragment, but reject scripts,
event handlers, foreign objects, document/entity declarations, and non-embedded external references before
hashing and embedding it. Also consider explicit image elements, logo metadata and structured data, linked
logo assets, visible logo-semantic CSS `background-image`, `mask`, or `content` declarations, manifest
identity icons, and favicons in descending semantic confidence. CSS data-URI SVG logos must pass the same
static-SVG validation as linked and inline SVG. A failed explicit logo
must not be silently replaced by a weaker candidate; a favicon may serve as identity only when no stronger
logo candidate exists. Never use an Open Graph preview image alone as the logo.

If that resolution does not complete, stop consuming the incomplete profile and switch the artifact to the
Accenture fallback. Keep client-brand status `UNRESOLVED` or `BLOCKED` separately from artifact-generation
status so the `.html` is usable while the fidelity gap remains visible.

## Build progressively

- Define one message per slide/section and map major claims to evidence before detailed styling.
- Construct in small recoverable batches: semantic shell and tokens; representative sections; remaining
  content; interactions; static validation; browser QA.
- Prefer self-contained HTML with inline CSS/JS/SVG when offline delivery matters. Otherwise document the
  local build and asset contract.
- Provide keyboard navigation, visible controls, focus, reduced motion, responsive layouts, print styles,
  honest empty/error states, and no dead decorative controls.
- Label verified fact, interpretation, recommendation, target state, assumption, illustration, and open
  validation point distinctly. Never invent metrics or decorative charts.
- Build the first render from the refined token and composition baseline. Do not defer typography, responsive
  hierarchy, tables, navigation, dialog treatment, or reduced-motion behavior to a cleanup phase.
- Always write the requested HTML output path. A branding failure changes the applied identity and QA claim;
  it does not change the deliverable into Markdown or a planning-only handoff.

Use `assets/editorial-shell.html` only as a structural accessibility baseline; replace its visual tokens,
signature, and content from the real brief. It is deliberately not a finished generic theme.

Translate the evidenced identity into the requested artifact. Do not copy the source website's layout,
navigation, content, or component composition.

Render the presentation shell with `scripts/render_branded_html.py` so it consumes the same normalized
version-2 profile and exact asset set as the living-dashboard renderer. Never leave a placeholder mark,
synthetic favicon, hot-linked asset, or visible generic shell palette after branding.

## Validate

Run static checks first. When content, structure, and brand are correct but execution still needs a dedicated
finesse pass, use `polish-html-artifact`; then run `validate-visual-artifact` independently across representative
sections, longest content, all primary controls, target viewports, console health, and print/fullscreen behavior
as applicable. Make small correction batches; do not restart the design during QA.

When a structured client profile drives the artifact, pass the same profile to static validation, browser
brand QA, and `--peer-html` comparison with the paired dashboard or presentation. A required client profile
that matches a generic theme is a client-brand failure; generate with the Accenture fallback and report that
fidelity limit. `BRAND_PROFILE_CONSISTENT` is only a contract check; completion also requires independent
`BRAND_FIDELITY_PASS` and `VISUAL_QA_PASS`. For fallback output, validate the fallback identity and explicitly
report client-brand fidelity as unresolved rather than failed HTML generation.

For bilingual client delivery, complete the artifact and its visual system first, then compose with
`localize-client-artifact`. Preserve the established design while adding the restrained language control,
local message data, and German/English browser matrix; do not create separate language-specific HTML files.

For public-sector client work, apply the persisted output-specific policy: living dashboards use the
resolved German default plus English switch, while sales/client presentations are authored directly in the
resolved German locale and remain monolingual unless explicitly overridden. Do not add a hidden English
dictionary or language control to a German-only sales presentation.
