# Reference applications as discovery priors

Use a separate reference application only when project configuration explicitly authorizes it. A reference can
accelerate discovery by suggesting likely modules, descriptors, framework bindings, integration shapes, or data
access patterns. It is never evidence that the target contains the same behavior or architecture.

## Reference profile contract

Record the reference profile separately from target registries with:

- state `REFERENCE_PATTERN`;
- source kind and a stable source fingerprint or immutable revision;
- scope and exclusions;
- bounded patterns with exact reference evidence;
- permitted target-search use for each pattern;
- negative findings and known absences;
- unsafe generalizations that must not be made.

Reference paths and observations retain their own provenance. Do not allocate target evidence IDs for reference
observations and do not include reference-only records in target coverage denominators, dependency counts,
requirements, capabilities, estimates, or confidence.

## Target comparison

For every used pattern:

1. state the target question or search route it motivates;
2. inspect the target source, configuration, contracts, or runtime evidence independently;
3. record matches and non-matches with target coordinates;
4. keep ambiguous or absent matches unresolved;
5. let direct target evidence override the prior when the implementations differ.

A matching filename, package, symbol, framework, schema name, or configuration key is only a lead. Promote a
target observation only when target evidence supports the complete claim. A reference-only dependency never
creates a target edge, and a reference rule never becomes a target requirement.

## Conflicts and lifecycle

Preserve the reference pattern and target result as separate records. When they conflict, mark the target
interpretation according to the project's ordinary contradiction or review lifecycle; do not weaken target
evidence to preserve the exemplar. Refresh or retire a reference profile when its fingerprint changes, its
authority expires, or repeated target non-matches show that it is no longer a useful discovery prior.

Projects without a configured reference application need no reference profile and retain the normal
target-only analysis workflow.
