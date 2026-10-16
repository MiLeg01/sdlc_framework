---
name: create-component-architecture-diagram
description: Derive and validate an application or solution architecture view at container, component, module, service, or major package level from code, configuration, contracts, and approved design evidence. Use for backend, frontend/backend, microservice, modular-monolith, target, comparison, or modernization architecture views. Do not use for enterprise landscapes, exhaustive class detail, time-ordered interactions, or proposed dependencies presented as observed current architecture.
---

# Create a component architecture diagram

Explain the internal structure of one bounded solution without collapsing into either vague boxes or an
unreadable package graph. Apply the shared protocol from `create-technical-diagram`.

## Establish level and state

Choose one primary level: application/container, component/module/service, or a selected subsystem. State
whether the view is current, proposed target, transition, or comparison. Use C4 container/component ideas
when useful, but require strict C4 notation only when explicitly selected.

## Derive the model

1. Inspect manifests, dependency declarations, module roots, public interfaces, routes, service wiring,
   configuration, deployment units, message contracts, schemas, and representative call paths.
2. Identify stable responsibilities, owned data, exposed interfaces, dependencies, external systems, and
   runtime boundaries. Treat directory names as navigation clues, not component proof.
3. Separate build-time dependency, runtime call, data ownership, event subscription, and shared-library use.
4. Mark target components and dependencies `PROPOSED`; preserve conflicts and unknown dynamic edges.

## Control the view

Group by layer, domain, deployable unit, or ownership according to the audience. Keep dependency direction
clear. Collapse utility libraries and repeated infrastructure unless they materially affect architecture.
For a large solution, create a container overview plus component drilldowns per bounded subsystem.

Graphviz/DOT suits dependency-rich views; PlantUML suits formal component notation; SVG/HTML suits branded
or responsive artifacts. Mermaid is suitable when the graph remains modest.

## Validate

Check each component boundary, responsibility, dependency direction, interface label, data owner, and
external edge against evidence or an explicit design decision. Flag cycles, hidden cross-layer access,
ambiguous ownership, and omitted dynamic dependencies without presenting them as automatically incorrect.
Return editable source, rendered output, evidence metadata, current/proposed legend, and drilldown map.
