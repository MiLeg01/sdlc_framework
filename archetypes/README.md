# Project archetypes and overlays

An archetype is a reusable composition profile for a class of projects. It answers four questions:

1. Which facts should initialization discover before asking the user?
2. Which unresolved choices matter for this project family?
3. Which validated commons capabilities are normally relevant?
4. Which outputs and cross-cutting overlays are useful?

An archetype is not a copied project tree, a skill, an agent, another instruction file, or a second
implementation of `initialize-project`. Its manifest contains selection metadata and references; the
capability behavior remains in `skills/`, `agents/`, tools, and templates.

## Contract

`composition.yaml` is the registry and resolution contract. Each registered archetype has one small
`archetype.yaml`; each registered overlay has one `overlay.yaml`. These files use JSON-compatible YAML so
the standard-library resolver can load them without a runtime package dependency.

Capability references use four kinds:

- skills, agents, tools, and templates use stable IDs from `catalog/capabilities.yaml`;
- `required`, `default`, `recommended`, and `optional` express selection strength;
- condition blocks activate only when their explicit condition ID is selected.

Resolution includes `required` and `default` capabilities, preserves first-source order, promotes a repeated
capability to its strongest level, and emits each `(kind, ID)` once. Unknown IDs fail. Nested includes are
forbidden, so circular composition is structurally unavailable and hybrid selection remains visible at the
root.

Validate or inspect a composition with:

```bash
python3 tools/resolve_archetypes.py validate
python3 tools/resolve_archetypes.py resolve \
  --archetype legacy-migration,development \
  --overlay evidence-traceability,branded-html
```

## Available profiles

- `development`: normal software and application delivery. Its standard default is OpenSpec specification
  and readiness, bounded ready-slice implementation through the canonical RED → GREEN → REFACTOR skill,
  and specification verification; inventory, durable state, dashboards, and HTML remain conditional. An
  explicit user opt-out or clearly established project methodology removes the relevant defaults.
- `legacy-migration`: technology-neutral inventory and bounded legacy analysis. Requirements,
  traceability, implementation, dashboards, and presentation work are composed only when selected;
  analysis-only can stop at requirements, preparation adds OpenSpec, and implementation composes development.
- `research`: structured topic research, evidence evaluation, synthesis, and an optional
  presentation-ready handoff without assuming a presentation is required.
- `presentation`: presentation intent and adaptive questions without assuming HTML. Select
  `branded-html` only when HTML is the delivery medium. Sales, executive, technical, informational,
  workshop, and internal are combinable purposes, not separate archetypes.

Overlays are cross-cutting concerns that change both initialization and capability composition:

- `architecture-documentation`: evidence-backed technical diagram routing, source models, rendering, and
  conditional system, component, class, ER, sequence, data-flow, or composed migration-roadmap views;
- `bilingual-client-delivery`: English-first internal work plus one offline locale-appropriate
  German/English client artifact with a persistent accessible language switch and bilingual QA;
- `branded-html`: official-URL resolution, exact offline identity assets, shared artifact rendering, and fidelity QA;
- `durable-state`: hierarchical project-local memory, bounded context packages, selective invalidation, and validated checkpoints for substantial work;
- `evidence-traceability`: evidence/requirement records and independent audit for legacy migration or
  evidence-heavy development;
- `living-dashboard`: deterministic read-only projection of canonical project state using the complete fixed
  Agent Commons information architecture; archetypes set applicability without inventing layouts or silently
  removing standard sections in full legacy-modernization mode.
- `public-sector-client-delivery`: evidence-based client-sector and locale policy, client branding,
  German-default bilingual dashboards, German-only sales presentations, accessibility, and restrained tone;
- `sales-storytelling`: evidence-backed persuasive narrative, proof, objections, and call to action for
  sales-oriented presentations.

Each overlay applies to at least two archetypes. Deployment and executive reporting remain explicit gaps;
architecture documentation is now covered by a validated overlay and specialist diagram capabilities.

## Initializer and hybrids

`initialize-project` discovers the project and active runtime or runtimes, selects one or more archetypes, chooses justified overlays and
conditions, and calls the same resolver. Its generated `.agent-commons.yaml` records the canonical
archetypes, overlays, conditions, resolution levels, and final deduplicated skill, agent, tool, and template
references.

For standard-scale projects, initialization selects `durable-state` automatically and records lazy
`.agent-commons/memory/`; tiny projects keep it disabled unless the overlay is explicitly requested.

Hybrid projects select multiple archetypes directly. For example:

```text
legacy-migration + development + branded-html + evidence-traceability
```

```text
research + presentation + sales-storytelling + branded-html
```

There is no `hybrid` archetype. Tiny projects still record their selected archetype but suppress archetype
defaults; explicit overlays remain explicit.
