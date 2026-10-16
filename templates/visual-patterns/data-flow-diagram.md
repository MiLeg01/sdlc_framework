# Data-flow diagram pattern

- Best use: logical or physical movement from sources through transformations and stores to destinations.
- Avoid: control flow disguised as data flow, unlabeled arrows, or transformations inferred without evidence.
- Structure: sources → processes/transformations → stores/interfaces → destinations; group by pipeline,
  domain, trust boundary, or batch/stream mode.
- Capacity: 8-20 primary elements per overview. Use dataset or pipeline drilldowns for dense lineage.
- Edge labels: data object/class, format, direction, frequency, and protocol only when known.
- Responsive: preserve lineage as ordered source-transform-store-destination records.
- Accessibility: provide a textual lineage table and do not rely on shape or color alone for element type.
