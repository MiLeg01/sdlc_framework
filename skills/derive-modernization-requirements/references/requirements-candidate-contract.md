# Requirement candidate packet

A parallel extraction worker returns one isolated JSON or equivalent structured packet containing:

- packet and worker IDs, domain/capability boundary, and output fingerprint;
- input analysis/evidence packet IDs and exact fingerprints;
- temporary candidate IDs scoped to the packet;
- actor, trigger, proposed observable behavior, rationale, evidence IDs, and source classification;
- acceptance-scenario candidates, constraints, dependencies, exclusions, parity expectation, and confidence;
- overlap keys, possible duplicates, conflicts, assumptions, unknowns, and authority questions;
- analyzed, skipped, and failed inputs plus validation commands and results.

Candidate packets are proposals for synthesis. They carry no canonical requirement ID, approval, readiness,
specification, implementation, or completion state. During fan-in, the coordinator records a disposition for
every temporary candidate: accepted with canonical mapping, merged into another requirement, rejected with
reason, blocked, or retained as an unresolved conflict.
