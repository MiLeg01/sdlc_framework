# ADM work-unit model

Use work units that produce one independently reviewable target outcome and do not count shared work twice.
Prefer requirement slices, data conversions with reconciliation, integration contracts including failure
handling, batch outcomes including restart behavior, user interactions or reports, and named cross-cutting
platform, security, test, environment, cutover, coexistence, discovery, or retirement outcomes.

Link each unit to all available canonical source, requirement, capability, dependency, evidence, and question
records. Source evidence establishes current behavior; target decisions establish the modernization outcome.
Neither substitutes for the other.

Assess supported complexity dimensions separately:

- behavior and rule branching;
- data volume, quality, history, and reconciliation;
- interface count, protocol, transactionality, and external ownership;
- state, restart, concurrency, time dependence, volumes, and service levels;
- security, privacy, audit, regulation, and isolation;
- performance, availability, resilience, observability, and operability;
- UI states, accessibility, localization, and reporting;
- testability, environments, representative data, cutover, and rollback;
- coupling, dynamic dispatch, missing source, contradictions, reuse, and sequencing.

Mark unsupported dimensions `UNKNOWN` and name the missing evidence. Do not infer an application total from a
partial batch or treat lines, files, complexity scores, centrality, stories, or page counts as effort.
