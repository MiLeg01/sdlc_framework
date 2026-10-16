# Class diagram pattern

- Best use: important classes/interfaces and relationships for a domain, package, or selected subsystem.
- Avoid: whole-repository dumps, accessors, framework boilerplate, or unsupported multiplicities.
- Structure: group by package or bounded context; keep inheritance trees aligned; route associations away
  from member text.
- Capacity: 8-20 types per view. Use a domain overview plus package drilldowns above that.
- Content: include fields/methods only when they explain responsibility, identity, or public contracts.
- Responsive: replace dense members with concise type cards and a separate relationship list.
- Accessibility: spell out relationship type, direction, and cardinality in text.
