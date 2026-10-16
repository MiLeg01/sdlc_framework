# Evidence and requirement contract

## Evidence

Use a stable ID derived from artifact identity, coordinate, evidence type, and normalized observation.
Record artifact path, version/hash, exact coordinate, evidence type, factual observation, optional labeled
interpretation, authority, confidence, related IDs, and redaction state. Preserve independent or
conflicting sources separately. When source changes, supersede evidence rather than repointing it to an
unrelated location.

## Requirement

Record stable ID, title, actor, trigger, formal behavior, rationale, source class, evidence IDs,
acceptance scenarios, dependencies, exclusions, migration/parity expectation, non-functional constraints,
confidence, lifecycle, conflicts, questions, approval authority, and revision or normalized content hash.
Keep related specification IDs as reciprocal traceability, not as proof that the requirement is implemented.

## Invariants

- Verified/observed claims have resolvable evidence.
- Proposed target-state requirements have explicit rationale and approval state.
- Links are reciprocal and IDs unique.
- Acceptance criteria are observable and do not smuggle in unapproved design.
- Conflicts and unknowns remain visible.
- Requirement approval, specification coverage, implementation, and validation are distinct states.
- A specification derived from a requirement records the requirement revision or fingerprint it consumed.
