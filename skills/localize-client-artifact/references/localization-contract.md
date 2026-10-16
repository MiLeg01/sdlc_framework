# Client-artifact localization contract

## Contents

1. Architecture
2. Manifest
3. String coverage
4. Protected content
5. Incremental updates
6. Semantic review
7. Visual and interaction review
8. Failure boundaries

## Architecture

Use one artifact with shared structure:

```text
HTML and interaction structure
  + language-independent canonical data
  + keyed local client-facing messages
  + configured locale and persistence
```

Do not maintain `artifact-en.html` and `artifact-de.html`. Do not introduce a framework, backend, build
system, remote font, translation API, or runtime network dependency solely for localization.

Prefer explicit keys over translating arbitrary rendered text. Arbitrary text replacement is fragile when
the same English text has different meanings, when dynamic content changes, or when a translation matches a
technical identifier by accident.

## Manifest

The example manifest records:

- `source_locale`: normally `en`;
- `target_locales`: normally `de-AT`;
- configurable `default_locale`, `fallback_locale`, and `storage_key`;
- keyed English `source` values and `sha256:` source hashes;
- target translations;
- optional protected terms for exact preservation;
- optional `preserve_numbers: false` only when a reviewed locale formatter intentionally changes a value's
  representation without changing its meaning.

Projects may use an equivalent established structure. The invariant is deterministic key coverage and a
way to detect when source text changed after translation.

For public-sector dashboards, resolve the target locale from persisted client geography and keep English
available unless an explicit project instruction overrides it. Public-sector sales presentations use their
separate presentation policy and are not made bilingual merely because the dashboard is bilingual.

## String coverage

Inspect page title, metadata, headings, navigation, tabs, buttons, filters, labels, placeholders, tooltips,
legends, chart titles and axes, status labels, prose, findings, recommendations, captions, table headings,
empty/loading/error states, dialogs, diagram labels, `aria-*` attributes, print/export text, embedded SVG,
and JavaScript-generated content.

For dynamic interfaces, route content through `t(key, parameters)` at creation time or mark generated nodes
with explicit localization keys. On language change, update chart, diagram, or canvas labels through their
supported update API without recreating unrelated application state.

## Protected content

Keep these exact unless the item is explicitly a translatable business label:

- code identifiers, symbols, types, methods, classes, services, and application names;
- APIs, endpoints, database tables/columns, repositories, filenames, paths, commands, and configuration;
- vendor and product names;
- code, logs, raw evidence, source coordinates, and quotations.

Numbers, dates, chart data, and canonical state remain unchanged. Locale formatting may change display only
after verifying that parsing, filtering, sorting, export, and comparison still use the original values.

## Incremental updates

Use the English source hash as the translation freshness boundary:

```text
same key + same source hash -> preserve reviewed German
same key + changed source hash -> German is stale
new key -> translation missing
unreferenced key -> obsolete candidate, inspect dynamic use before removal
```

Do not infer freshness from the key alone. Do not silently update a stored hash without reviewing the German
translation against the changed source.

## Semantic review

Check that German is professional standard language appropriate for Austrian enterprise and public-sector
clients. Prefer client-established terminology. Avoid dialect and unnecessarily Germany-specific
bureaucratic vocabulary when an Austrian-compatible term is established.

Review claims, negation, modality, confidence, risk severity, approvals, timeframes, units, ownership, and
technical causality. Preserve distinctions among fact, interpretation, recommendation, assumption, conflict,
and unknown. Translation must not strengthen evidence or invent certainty.

## Visual and interaction review

German strings are often longer. Test representative longest content in both desktop and mobile layouts.
Prefer measured wrapping, width, grid, or spacing adjustments over materially shrinking type. Check tab and
navigation reachability, card height, table columns, status badges, chart labels, and diagram collisions.

Switch language after changing representative page state. The state before and after must match except for
localized presentation values and locale formatting. Reload to verify persistence when configured. Block
network access or inspect requests to prove offline operation.

The compact language control may display flags only when each control has a clear accessible language name,
radio semantics, selected state, keyboard behavior, and sufficient contrast. Do not expose a flag-only
accessible name.

## Failure boundaries

Stop and report rather than guessing when:

- client terminology conflicts or the authoritative source is unclear;
- source and translation meaning cannot be reconciled;
- a dynamic string has no stable key or rerender hook;
- a diagram or chart cannot update labels without losing state;
- the artifact depends on external resources despite an offline requirement;
- visual overflow cannot be corrected without redesign authority;
- source changes make existing translations stale.
