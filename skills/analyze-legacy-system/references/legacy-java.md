# Legacy Java analysis

- Resolve modules, build descriptors, framework versions, entry points, configuration profiles,
  controllers/endpoints, services, repositories/DAOs, scheduled/batch jobs, messaging, views, and tests.
- Build call edges from symbols and framework wiring; preserve reflection, XML, string-based lookup, and
  container-managed behavior as explicit uncertainty.
- Trace transaction boundaries, persistence queries/entities, DTO/mapping transformations, validation,
  security, error translation, retries, and integration clients.
- Inspect meaningful method-level branches, state transitions, loops, calculations, side effects, exceptional
  paths, concurrency, logging/audit, resilience, and configuration-dependent behavior. Extract actual rules
  and contract semantics rather than reporting annotations or method names alone.
- Compare Java DTOs/entities/API models and validation with legacy layouts and rules field by field where the
  systems represent the same boundary; classify equivalence and mismatches explicitly.
- Distinguish authored source, generated code, vendor libraries, configuration, migrations, and build
  output. Do not infer behavior from package/class names.
- Use company/reference architecture as a search prior, never as evidence that this application follows it.
