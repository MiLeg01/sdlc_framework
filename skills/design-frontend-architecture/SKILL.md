---
name: design-frontend-architecture
description: Define configurable frontend boundaries, rendering and data-flow choices, state ownership, module contracts, route composition, failure states, and design-system consumption from verified product and design-guide constraints. Use before material frontend foundations or cross-feature changes. Do not use for visual styling, task sequencing, a small local component edit, or target decisions unsupported by requirements.
---

# Design frontend architecture

Start from accepted journeys, repository evidence, delivery constraints, deployment shape, and the supplied
design guide. Use `frontend-design` when the visual thesis or interaction language is unresolved, and use
`plan-work` after the architecture is accepted to sequence implementation.

## Normalize the design guide

Capture the configurable inputs in `references/design-guide-contract.md`. A project may use
`assets/frontend-architecture-profile.example.json` as a starting shape, but project evidence remains
authoritative. Separate accepted constraints from proposals and unknowns.

## Define boundaries

1. Map application shells, routes, features, shared primitives, infrastructure adapters, and external
   integrations. Give every responsibility one narrow owner.
2. Select rendering, hydration, caching, offline, and deployment behavior from observable requirements;
   do not choose infrastructure for fashion or hypothetical scale.
3. Give each feature a public boundary, local tests, and explicit dependencies. Prevent cross-feature
   imports of private internals.
4. Assign server, URL, session, application, feature, component, and form state to the narrowest durable
   owner. Define reset, replay, concurrency, and stale-data behavior where relevant.
5. Put remote data, persistence, platform APIs, analytics, and generated clients behind typed contracts.
6. Define loading, empty, unavailable, partial, stale, error, retry, authorization, and not-found behavior.
7. Consume design tokens, components, accessibility rules, content density, and responsive behavior from
   the design guide without silently redefining the visual language.
8. Record decisions, alternatives, trade-offs, assumptions, migration seams, and validation evidence.

## Validate

Check dependency direction, route ownership, state lifetime, contract substitutions, representative failure
states, accessibility implications, bundle and runtime constraints, build/test packaging, and deployment
assumptions. Use architecture tests where boundaries can be enforced mechanically.

Return a route and shell map, module boundaries, state-ownership table, data-flow and interface contracts,
design-guide mappings, decisions, open questions, and exact validation results. Do not implement feature
behavior while presenting the work as an independent architecture review.
