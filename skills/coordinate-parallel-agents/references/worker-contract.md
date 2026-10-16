# Portable worker contract

Each assignment states:

- worker and batch ID;
- execution-plan task and stage ID;
- objective and observable completion signal;
- exact owned inputs and their fingerprints;
- bounded context package path/fingerprint, including mandatory, useful, omitted-relevant, and irrelevant context;
- contextual read-only dependencies;
- exact writable paths, mutable shared surfaces, and prohibited paths or state;
- base revision, isolated worktree/branch/task directory, and shared-resource leases when writes can overlap
  in time;
- required skills, schemas, commands, and output format;
- validation and stop conditions;
- isolated output location and coordinator return channel.

Each return states:

- analyzed or changed inputs and observed fingerprints;
- created outputs, changed paths, output fingerprints, and temporary identifiers;
- evidence, assumptions, conflicts, unknowns, skipped items, and unresolved dependencies;
- exact validation commands and results;
- whether inputs, base revision, resource leases, or ownership drifted or overlapped;
- resulting checkpoint or commit when authorized;
- one recommended coordinator action.

Workers never allocate global IDs, edit coordinator-owned state, integrate another worker, broaden their own
scope, rewrite shared project memory, or claim repository-level completeness. They return a validated memory
proposal to the coordinator when their findings should become reusable project knowledge.
