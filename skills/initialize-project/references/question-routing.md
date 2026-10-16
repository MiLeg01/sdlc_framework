# Adaptive question routing

Ask only unresolved choices. Inspect files first and group at most three related questions.

## Shared minimum

- What outcome matters and who will use it?
- Which concrete artifacts are expected?
- What observable evidence means done?
- Should the project include an HTML artifact? If yes, for whom and for what decision?
- What is the authoritative visual source, or should the design remain neutral?
- Are there optional visual, presentation, diagram, timeline, cluster, website, brand, or existing-project
  references, and what should or should not be borrowed from them?

## Legacy route

Ask only missing items: source applications/languages; migration boundary; target stack; reference
systems; database; batch and integration technologies; schemas/contracts; documents; required evidence
granularity; call/dependency/data-flow graphs; parity or implementation scope; deployment target.

Inspect supplied source paths before asking discoverable technical questions. Record access per source.
A read-only source remains strictly read-only, and contradictory in-place modification requests require
explicit resolution before initialization.

## Development route

Ask only missing items: product behavior; greenfield/existing; frontend/backend; data ownership;
authentication/authorization; integrations; architecture constraints; UI expectations; test levels;
operational/deployment target.

## Architecture documentation route

When architecture documentation is requested but no views are named, ask one concise multiple-selection
question: system/application landscape; component architecture; class/domain model; ER/data model;
sequence/interaction; data flow; migration roadmap; or let the analysis determine. Do not ask for views
already explicit in the brief. Record selected views and activate only their overlay conditions.

Infer natural language conservatively: applications + integrations → landscape; modules/services →
component; object/domain structure → class; database relationships → ER; ordered calls/login/request flow
→ sequence; batch/ETL/lineage/data movement → data flow; migration waves/coexistence/retirement → roadmap.

## Presentation route

Ask only missing items: audience; decision/call to action; factual sources; technical versus executive
depth; one or more purposes from sales, executive, technical, informational, workshop, and internal;
narrative; brand sources; static/interactive/offline needs; diagrams/charts; presentation context.

When an HTML dashboard or presentation is already selected but its brand is missing, offer Client brand,
Organization brand, Neutral premium, and Other/reference. Do not ask again when a client website, brand guide,
visual reference, or explicit brand choice is already present.

When its client-facing language is unresolved, ask one concise language question with English, German
(Austria), German plus English switch, and Other. Do not ask when working language and delivery language,
German/English, Austrian German, bilingual delivery, or `keep English available` is already supplied.

## Research route

Ask only missing items: topic or research question; supported audience and decision; geographical,
industry, technology, competitor, and temporal boundaries; source classes; evidence depth; output format;
and whether the synthesis must become presentation input.

## Sales route

Ask only missing items: proposed offer or approach; target customer; likely problem; desired next action;
known differentiators; known objections; and supporting proof. If research was explicitly selected to
discover pain points, competitors, differentiation, or objections, record those as research questions
instead of asking the user to provide the answers up front.

## Reference route

When visual, dashboard, or presentation work is selected and no examples were supplied, optionally ask for
screenshots, presentations, HTML, diagrams, timelines, cluster visualizations, websites, existing projects,
or brand/design-system material. Accept paths, URLs, or descriptions. This question never blocks
initialization.

For each supplied reference, capture what applies, what to reuse, and what to ignore. Keep local and client
references read-only and project-local unless the user explicitly authorizes copying.

## Stop rule

Stop when one useful bounded first action can be taken safely. Record unknowns instead of front-loading a
large questionnaire.

## Composition routing

- Existing files answer questions; archetype manifests route the remaining questions.
- HTML deliverables select `branded-html`; canonical-state dashboards also select `living-dashboard`.
- Sales presentation purpose selects `sales-storytelling`.
- Research followed by presentation selects both archetypes and uses the research synthesis as the factual handoff.
- Legacy or development work with high-confidence source-to-verification needs selects
  `evidence-traceability`.
- Explicit architecture documentation or diagram views select `architecture-documentation` and only the
  corresponding view conditions.
- Substantial multi-session recovery needs select `durable-state`.
- Legacy target implementation composes `legacy-migration` with `development`.
- Independent non-overlapping legacy batches may activate `parallel-discovery`; do not select its agent by
  default.

## Capability-gap routing

- Resolve capability families after the brief and archetypes, using actual catalog `provides` metadata.
- For migrations, identify source, target, and bridge needs independently.
- Do not interrupt for optional gaps or specialist niceties that cannot materially change correctness.
- For material gaps, ask one choice: external discovery, project-local capability later, or generic-only.
- If discovery is selected, ask source scope only when the user has not already constrained it.
- Stop after presenting a three-to-seven item shortlist. Candidate acceptance is a separate user decision.
- After explicit acceptance, default to project-local methodology or capability integration and record
  provenance; never promote directly into commons.
