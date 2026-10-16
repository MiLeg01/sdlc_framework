---
name: create-class-diagram
description: Derive and validate a focused class or domain-model diagram from selected object-oriented source code, specifications, or approved target design. Use for Java, C#, Python, TypeScript, and similar languages when inheritance, interfaces, composition, aggregation, associations, cardinality, or important members must be explained. Do not use for full-repository dumps, every getter and setter, database-only models, or proposed structures presented as verified source.
---

# Create a class diagram

Select the abstraction that answers the question: domain overview, important classes, package/module
focus, or a full selected subsystem. Apply the shared protocol from `create-technical-diagram`.

## Extract deliberately

1. Bound source roots, packages/modules, entry classes, generated code, tests, and excluded framework
   artifacts.
2. Resolve classes, interfaces, enums, inheritance/implementation, fields, constructor ownership, and
   method signatures from syntax-aware tooling or direct source evidence where practical.
3. Distinguish inheritance, composition/lifecycle ownership, aggregation, plain association, dependency,
   and interface realization. Use cardinality only when collections, constraints, or specifications make
   it defensible.
4. Include important fields and methods that explain responsibility or contracts. Omit routine accessors,
   boilerplate, framework noise, and private implementation detail by default.

For dynamic languages, label unresolved runtime types and monkey-patched or metaprogrammed relationships
instead of forcing static certainty. For target design, mark all unimplemented structures `PROPOSED`.

## Compose the model

Group by package, bounded context, layer, or responsibility. Keep inheritance trees visually distinct from
associations. Split large models into a domain overview and package/subsystem drilldowns with stable class
IDs. PlantUML or Mermaid suits maintainable UML-like source; Graphviz or SVG may be better for large custom
layouts.

## Validate

Reconcile names, namespaces, visibility, inheritance, interface realization, ownership, association
direction, multiplicity, and selected members to source coordinates or approved specifications. Confirm
that omitted detail is intentional and that no class or relationship was invented. Return editable source,
rendered output, evidence metadata, notation legend, exclusions, and unknowns.
