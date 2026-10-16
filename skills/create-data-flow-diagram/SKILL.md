---
name: create-data-flow-diagram
description: Derive and validate a logical or physical data-flow and lineage diagram showing sources, transformations, stores, interfaces, destinations, and evidenced movement of data. Use for ETL, batch, SAS, integration-heavy legacy systems, migration, lineage, privacy/security analysis, or selected pipelines at overview or drilldown level. Do not use for control-flow-only logic, static component dependencies without data movement, or transformations and destinations inferred without source, configuration, schema, job, or runtime evidence.
---

# Create a data-flow diagram

Make data movement and transformation—not control flow—the primary subject. Apply the shared protocol from
`create-technical-diagram`.

## Define the flow

Choose logical flow, physical flow, high-level lineage, or a detailed selected pipeline. Bound datasets,
time window, environment, batch/stream mode, current/target/transition state, and the questions the view
must answer.

## Trace from evidence

1. Inspect schemas, files, queries, ETL/SAS jobs, application code, mapping rules, message contracts,
   schedulers, configuration, storage metadata, and representative runtime evidence.
2. Record sources, processes/transformations, stores, destinations, interfaces, data classes, direction,
   frequency, format, and ownership where known.
3. Trace rename, filter, join, aggregate, enrich, validate, mask, split, merge, and persistence steps only
   when evidenced. Preserve dynamic SQL, generated mappings, manual steps, and unresolved lineage as gaps.
4. Distinguish data movement from control triggers. Add trust boundaries, sensitive-data annotations, or
   retention notes only when relevant and supported.

For large estates, create a source-to-domain overview plus pipeline or dataset drilldowns. Graphviz/DOT is
often effective for lineage; Mermaid works for smaller flows; SVG/HTML supports polished security,
management, or presentation views.

## Validate

Reconcile every source, transformation, store, destination, direction, and data-class label to evidence.
Check that no transformation is invented, stores are not confused with processes, manual transfers remain
visible, and current/proposed flows are distinct. Return editable source, rendered output, evidence
metadata, legend, overview/drilldown map, unresolved lineage, and validation limits.
