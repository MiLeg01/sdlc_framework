# ER diagram pattern

- Best use: domain or selected-schema views of entities/tables, keys, important attributes, and evidenced
  cardinalities.
- Avoid: a 200-table canvas, audit-column clutter, or relationships inferred only from column names.
- Structure: core entities first, dependent entities around them, join tables between related domains, and
  technical tables in separate drilldowns.
- Capacity: 8-24 entities per view. Add a domain overview and subsystem drilldowns for larger schemas.
- Content: show primary/foreign keys and only attributes needed for the purpose; distinguish logical from
  physical and current from proposed.
- Responsive: provide entity/key cards and a relationship table when spatial routing collapses.
- Accessibility: state optionality and cardinality in relationship text rather than line-end symbols alone.
