---
name: create-system-landscape-diagram
description: Derive and validate a high-level system or application landscape showing actors, systems, platforms, data stores, domains, scope, lifecycle state, and evidenced integrations. Use for enterprise landscapes, modernization discovery, current/target/transition views, integration maps, or executive architecture overviews. Do not use for internal component detail, message ordering, database schema structure, or relationships inferred only from names and proximity.
---

# Create a system landscape diagram

Show the smallest set of systems and relationships needed to explain the landscape to the intended
audience. Apply the shared evidence, format, decomposition, and delivery rules from
`create-technical-diagram`.

## Bound the landscape

1. Define current, target, transition, or comparison state; business/technical audience; organizational,
   domain, and environment boundary; and in-scope/out-of-scope criteria.
2. Gather system registers, interface catalogs, deployment evidence, source analysis, contracts,
   configuration, runtime observations, and authoritative architecture documents.
3. Normalize aliases without merging distinct deployments, tenants, environments, or ownership boundaries.
4. Record actors, internal systems, external platforms, databases only when landscape-relevant, domains,
   and integration endpoints with `VERIFIED`, `INFERRED`, or `UNKNOWN` status.

## Model relationships

Represent direction and known mechanism such as REST, SOAP, messaging, events, files, batch, database
access, or manual interaction. Omit the protocol when it is not known. Do not convert shared technology,
network proximity, or similar names into an integration.

Visually distinguish evidenced states such as `IN SCOPE`, `OUT OF SCOPE`, `EXTERNAL`, `LEGACY`, `TARGET`,
and `TRANSITION`. Do not apply a lifecycle label without evidence or an explicit proposal decision.

## Compose the view

Use a left-to-right or domain-centered flow with clear system boundaries and a compact legend. Group by
domain, ownership, trust boundary, or lifecycle only when that grouping supports the purpose. Use C4
context ideas when helpful, but do not require strict C4 notation.

For large estates, create:

- an executive landscape of major domains and systems;
- integration or domain drilldowns with stable system IDs;
- separate current and target views unless a combined transition view remains legible.

Graphviz/DOT often suits integration-heavy landscapes; SVG/HTML suits polished dashboards and
presentations. Mermaid is acceptable for smaller landscapes with controlled edges.

## Validate

Reconcile every system and edge to the evidence index. Check boundary placement, direction, protocol
labels, duplicated aliases, external/in-scope distinctions, lifecycle states, crossings, and legibility.
Return editable source, rendered output, evidence metadata, legend, unknowns, and decomposition map.
