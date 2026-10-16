---
name: create-er-diagram
description: Derive and validate an entity-relationship diagram from database schemas, DDL, migrations, ORM models, or authoritative data documentation. Use to show tables or entities, primary and foreign keys, join tables, ownership, important attributes, and defensible cardinalities at domain, core-entity, or selected-schema level. Do not use to guess relationships from column names, flatten a large database into one canvas, or treat ORM convenience mappings as physical constraints without evidence.
---

# Create an ER diagram

Explain the data model at the smallest level that supports the audience and decision. Apply the shared
protocol from `create-technical-diagram`.

## Establish authority

Prioritize live schema metadata or applied DDL, then migrations, then ORM mappings, then documentation.
Record conflicts rather than silently choosing. Define database/schema, environment, snapshot time,
selected domains, excluded technical tables, and whether the view is physical, logical, or proposed.

## Derive entities and relationships

1. Extract tables/entities, primary and candidate keys, foreign keys, nullability, unique constraints,
   important attributes, indexes only when relevant, and join tables.
2. Derive cardinality from constraints and nullability. Do not infer a foreign key solely from naming
   conventions or ORM navigation properties.
3. Distinguish identifying relationships, optional ownership, many-to-many joins, inheritance mapping,
   denormalized references, and unresolved polymorphic links.
4. Mark proposed target structures `PROPOSED` and retain current schema separately when comparison matters.

## Control density

For large databases, produce a domain overview using core entities and relationship summaries, then
domain/subsystem drilldowns. Avoid showing every audit column or technical attribute unless the purpose
requires it. Mermaid ER and PlantUML are suitable for modest formal models; Graphviz or SVG/HTML is often
better for large decomposed schemas.

## Validate

Check entity names, keys, relationship endpoints, optionality, cardinality, join-table semantics, attribute
selection, and schema scope against authoritative evidence. Surface missing constraints and ORM/schema
conflicts explicitly. Return editable source, rendered output, evidence metadata, notation legend,
overview/drilldown map, and unresolved relationships.
