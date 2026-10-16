# Component architecture pattern

- Best use: one solution boundary with containers, modules, services, components, owned data, and external
  dependencies.
- Avoid: mixing package, class, component, and enterprise-system levels on one canvas.
- Structure: system boundary → deployable/container layer → selected components; show interfaces and data
  ownership separately from generic dependency arrows.
- Capacity: 6-18 components per view. Use a container overview and subsystem drilldowns for larger models.
- Direction: make dependency/call direction explicit and distinguish runtime, build-time, data, and event edges.
- Responsive: stack layers or subsystems while keeping boundary and interface labels visible.
- Accessibility: provide a component responsibility and dependency table beside the visual.
