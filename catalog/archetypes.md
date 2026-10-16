# Project composition

The registry is `archetypes/composition.yaml`; the registered manifests are the source of truth.

| Archetype | Standard default | Common explicit additions |
|---|---|---|
| `development` | OpenSpec specification, readiness review, bounded ready-slice delivery through canonical TDD, and implementation verification | planning, risk-based testing, code review, Git safety, frontend design and architecture, architecture documentation, structured-data anonymization, bounded parallel coordination, independent architecture review, privacy/security, safe state changes |
| `legacy-migration` | deterministic inventory and bounded source analysis | requirements discovery for analysis-only work; OpenSpec generation for migration preparation; development composition for implementation; architecture documentation, evidence-constrained migration, estimation, and independent review |
| `research` | structured evidence gathering, attachment intake, and synthesis | architecture documentation, presentation composition, traceability, durable state, dashboard, branded HTML |
| `presentation` | no skill until a purpose and medium are selected | architecture documentation, sales storytelling, branded HTML, accessibility review, durable state, canonical dashboard |

Development defaults may be removed only by an explicit user opt-out or detected established project
methodology. The resolver records those exclusions; it does not create a second archetype or overlay.

| Overlay | Cross-cutting concern |
|---|---|
| `architecture-documentation` | evidence-backed system, component, class, ER, sequence, data-flow, and composed migration-roadmap views |
| `branded-html` | brand-derived HTML construction plus visual QA |
| `consulting-delivery` | harness-neutral project-delivery governance, project financial forecasting, and independent numerical review with organization-specific adaptation kept project-local |
| `durable-state` | concise multi-session project memory |
| `evidence-traceability` | evidence/requirement records plus independent audit |
| `living-dashboard` | deterministic read-only canonical-state view |
| `bilingual-client-delivery` | English-first internal work with one German (Austria)/English offline client artifact and bilingual QA |
| `public-sector-client-delivery` | evidence-based sector/locale defaults, client branding, accessible bilingual dashboards, German-only sales delivery, and restrained public-sector tone |
| `sales-storytelling` | evidence-backed persuasive narrative, proof, objections, and call to action |

Run `python3 tools/resolve_archetypes.py validate` to validate the registry and every capability reference.
Hybrid work selects multiple archetypes; tiny projects record their archetype but suppress its defaults.
Sales, executive, technical, informational, workshop, and internal are combinable presentation purposes,
not separate archetypes.
