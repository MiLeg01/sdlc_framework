# System landscape pattern

- Best use: current, target, transition, or comparison views of applications, actors, platforms, domains,
  and evidenced integrations.
- Avoid: component internals, unverified edges, or combining current and target states without a legend.
- Structure: actor/entry edge → in-scope domains and systems → external systems; keep a separate legend for
  scope, lifecycle, and confidence.
- Capacity: about 8-20 systems in an overview. Above that, use domain clusters plus integration drilldowns.
- Edge labels: direction and known mechanism such as API, event, message, file, batch, database, or manual.
- Responsive: preserve domain membership and relationship text in a stacked textual summary.
- Accessibility: expose every system, scope label, and integration in an adjacent list or table.
