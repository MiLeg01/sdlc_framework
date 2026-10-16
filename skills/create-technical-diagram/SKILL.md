---
name: create-technical-diagram
description: Select, model, render, and validate an evidence-backed technical diagram at the right abstraction for documentation, analysis, dashboards, or presentations. Use when the requested view is ambiguous, spans multiple diagram families, or needs shared evidence, format, decomposition, and delivery decisions. Do not use for decorative illustration, unsupported target-state invention, generic charts, or a request that already belongs unambiguously to one specialized diagram skill.
---

# Create a technical diagram

Route the communication need to the smallest useful diagram family, then preserve one evidence model across
editable source, rendered output, and downstream artifacts.

## Frame the view

Establish purpose, audience, decision supported, scope boundary, current/target/transition state, required
detail, destination, and available evidence. Label proposed target structures as `PROPOSED`; use
`VERIFIED`, `INFERRED`, and `UNKNOWN` for evidence confidence. Never turn an unknown relationship into a
normal rendered edge.

## Select the family

| Need to show | Use |
|---|---|
| applications, actors, platforms, and integrations | `create-system-landscape-diagram` |
| modules, services, containers, and dependencies inside a solution | `create-component-architecture-diagram` |
| classes, interfaces, inheritance, and object/domain relationships | `create-class-diagram` |
| tables/entities, keys, and cardinalities | `create-er-diagram` |
| ordered calls, messages, branches, and failures | `create-sequence-diagram` |
| sources, transformations, stores, destinations, and lineage | `create-data-flow-diagram` |

For calls between services, choose component architecture when the question is structural and sequence
when ordering matters. For migration roadmaps, compose current/transition/target architecture views with
dependency-aware waves from `plan-work` and the timeline visual pattern; do not invent a separate
architecture fact set for the roadmap.

## Build the evidence model

Create a lightweight record with diagram type, title, purpose, audience, scope, state, source evidence,
nodes, relationships, and optional decomposed views. Give every relationship an evidence status and exact
source locator or an inference rationale. Use `assets/diagram-model.example.json` as a portable example,
not as a mandatory project DSL.

When using this model, run:

```bash
python3 scripts/validate_diagram_model.py <diagram-model.json>
```

Resolve validator errors before rendering. A passing structural check does not prove semantic correctness.

## Choose the representation

- Prefer Mermaid for maintainable small class, ER, sequence, and flow diagrams when its layout is adequate.
- Prefer PlantUML for formal UML semantics when a portable renderer is already available.
- Prefer Graphviz/DOT for dependency-heavy graphs needing automatic layout.
- Prefer native SVG or self-contained HTML for polished branded, responsive, or presentation-grade output.

Record the editable source and renderer/version when rendering is tool-dependent. Avoid external runtime
dependencies in standalone HTML when practical; embed generated SVG rather than requiring a browser CDN.

## Use visual references without borrowing facts

Inspect supplied project visual-reference or diagram-reference folders before styling the rendered view.
Follow bounded instructions such as “use the grouping style, not the colors” and reuse
only the requested layout, density, clustering, hierarchy, or annotation behavior. A visual reference is
presentation guidance, not evidence that a system, class, table, participant, or relationship exists.
Project brand direction controls aesthetics; the evidence model controls technical content.

## Control density

Cluster by domain, layer, ownership, or lifecycle. Collapse repeated edges and low-value detail. When one
view would be unreadable, produce an overview plus named drilldowns that reuse stable element IDs. Do not
hide unresolved or dynamic behavior merely to simplify the picture.

## Deliver and validate

Return:

- editable source and the rendered SVG, PNG, PDF, or standalone HTML artifact;
- metadata and evidence index;
- legend for status, scope, and notation;
- overview/drilldown map when decomposed;
- validation results and explicit unknowns.

Reconcile every rendered node and edge against the evidence model. Inspect labels, hierarchy, crossings,
spacing, contrast, grouping, responsive behavior, and destination fit. Use `validate-visual-artifact` for
HTML/dashboard delivery and preserve the same semantic model when adapting the visual language for a
presentation.
