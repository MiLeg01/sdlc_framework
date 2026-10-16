---
name: localize-client-artifact
description: Transform an existing standalone client-facing HTML dashboard, presentation, technical narrative, or management artifact into one bilingual offline artifact while preserving design, data, evidence, interactions, and technical identifiers. Use for German/English client delivery, public-sector dashboard delivery, translation of an existing HTML artifact, or adding a persistent accessible language switch. Do not use for ordinary sentence translation, runtime translation services, separate per-language HTML copies, initial artifact design, or non-HTML deliverables.
---

# Localize a client artifact

Preserve the artifact and add a localization layer; do not redesign it or fork the whole DOM.

## Establish the delivery contract

1. Confirm the artifact path, working language, client language, default language, fallback language,
   offline requirement, persistence preference, and client or project glossary.
2. Resolve the German locale from persisted client context: `de-AT` for Austria, `de-DE` for Germany,
   and `de-CH` for Switzerland. Use professional Standard German, never dialect. Do not force Austrian
   terminology onto a clearly German or Swiss client.
3. Keep English-first internal work lightweight. Localize at the client-delivery boundary unless the
   project explicitly needs bilingual behavior earlier.
4. Read `references/localization-contract.md` before changing the artifact. Reuse client terminology from
   supplied authoritative material when available, but never send client content to an external
   translation service without explicit authorization.

## Inventory every client-facing string

Inspect static HTML and runtime-generated content in JavaScript, embedded JSON, SVG, charts, tooltips,
modals, navigation, filters, tables, diagrams, accessibility labels, print/export text, metadata, empty
states, and error states. Separate:

- translatable presentation prose and human-readable labels;
- language-independent data, numbers, dates, evidence, and canonical state;
- protected source identifiers, product names, paths, commands, code, endpoints, keys, and quotations.

Do not translate source-code identifiers, class or method names, service or application names, repository
names, API endpoints, table names, filenames, configuration keys, commands, snippets, vendor products, or
evidence coordinates. Translate explanatory text around them.

## Introduce the smallest localization structure

1. Keep one HTML/layout structure. Use deterministic message keys and two local language datasets rather
   than duplicated pages or large duplicated DOM branches.
2. Store the English source, `de-AT` translation, and source hash in a lightweight manifest. Start from
   `assets/localization-manifest.example.json` when the artifact has no established equivalent.
3. Bind static content with explicit keys such as `data-i18n`. Route runtime-generated text and chart
   labels through the same lookup function. Keep chart values and canonical data unchanged.
4. Inline or adapt `assets/bilingual-runtime.js` when it fits the existing architecture. Existing project
   localization code takes precedence when it already satisfies the contract.
5. Configure the default locale per artifact. For Austrian client delivery, prefer `de-AT`; for internal
   development, `en` may remain the default. Never hard-code one global default for every project.

## Translate with semantic control

- Preserve meaning, technical precision, business implication, hierarchy, tone, and information density.
- Prefer idiomatic German over word-for-word substitution. Keep established English industry terms when
  they are clearer in context, including terms such as API, Backend, Frontend, Cloud, Deployment, DevOps,
  CI/CD, Microservice, Repository, Pull Request, Framework, Runtime, Dashboard, and Proof of Concept.
- Apply project glossary and client terminology consistently. Do not create a global client-specific
  glossary in Commons.
- Preserve raw source evidence and original quotations unless translation is explicitly requested; localize
  the explanatory presentation layer around them.
- Translate human-readable diagram labels while preserving technical node identifiers. Translate chart
  titles, axes, legends, tooltips, and annotations while preserving series data and numeric meaning.
- Use locale-aware dates and number formatting only when it cannot alter interpretation or data behavior.

## Add the standard language control

Add a compact branded flag control. The visible control uses flags only; every button must still expose
an explicit accessible language name through `aria-label`:

```html
<div class="language-switch" role="radiogroup" aria-label="Language">
  <button type="button" role="radio" data-localization-locale="de-AT" aria-checked="true" aria-label="Deutsch (Österreich)">
    <span aria-hidden="true">🇦🇹</span>
  </button>
  <button type="button" role="radio" data-localization-locale="en" aria-checked="false" aria-label="English">
    <span aria-hidden="true">🇬🇧</span>
  </button>
</div>
```

Match the existing design tokens and layout. Keep the control restrained, keyboard usable, visibly
selected, and accessible. The flag may be the only visible content, but it is not the accessible name.
Switching must not reload, navigate, replace the page, or reset filters, selections, expanded sections,
scroll position, or other dashboard state.

Localization must not replace, redraw, translate, or recompress official brand assets. Preserve the same
brand profile, favicon/logo bytes and hashes, exact observed palette, derivation provenance, and asset/theme
fingerprints in every locale. Rerun peer-artifact and browser brand-fidelity validation after localization;
token consistency or a visually similar localized theme is insufficient.

Persist the selected locale with `localStorage` when appropriate and fall back safely to the configured
default if storage is blocked or unavailable. Update the document `lang`, title, metadata, and accessible
labels with the active locale.

## Update incrementally

When rerunning on an already localized artifact:

1. compare current English source values and hashes with the manifest;
2. retain valid German translations for unchanged keys;
3. translate only new or changed source strings;
4. flag changed-source translations as stale rather than silently reusing them;
5. remove or explicitly retain obsolete keys after checking dynamic references;
6. rerun complete semantic and visual validation.

Do not blindly regenerate every German string or overwrite established client terminology.

## Validate both languages

Run the deterministic localization gate:

```bash
python3 scripts/validate_localization.py --manifest <localization.json> --html <artifact.html> --json
```

Then run `validate-visual-artifact` for at least English desktop, German desktop, English mobile, and
German mobile where relevant. Exercise language switching after filters, navigation, expansion, chart, and
modal state changes; reload once when persistence is enabled. Check long German labels, tabs, buttons,
cards, tables, charts, badges, diagrams, print, console health, and offline loading.

Complete only when missing and stale keys are zero, protected identifiers and numbers retain their meaning,
no accidental English remains in the German UI, both locales are visually sound, switching preserves state,
and validation limitations are recorded.
