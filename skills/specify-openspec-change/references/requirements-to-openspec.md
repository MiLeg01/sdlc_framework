# Requirements to OpenSpec

Use this method when approved structured requirements are the source for implementation preparation.

## Transform, do not relabel

1. Select approved requirements and retain their stable IDs, revisions, evidence, constraints, dependencies,
   exclusions, confidence, and unresolved questions.
2. Group requirements that describe one coherent implementation-facing behavior. Split one broad requirement
   when distinct capabilities, release boundaries, or independently testable outcomes require separate
   specifications.
3. Record many-to-many links explicitly. A requirement may feed multiple specs and a spec may derive from
   multiple requirements.
4. Resolve conflicts and missing decisions before implementation readiness. Do not turn an unresolved
   requirement into a guessed acceptance criterion.
5. Write the OpenSpec delta as intended behavior. Keep design choices in design artifacts and work sequencing
   in tasks.
6. Derive observable acceptance criteria covering the approved behavior, constraints, negative paths, and
   relevant parity obligations.
7. Record scope, non-scope, dependencies, source requirement IDs, and the exact requirement revision or
   fingerprint consumed by the specification.
8. Validate both OpenSpec structure and semantic coverage. Requirement coverage does not prove implementation;
   a completed implementation does not validate acceptance criteria that lack credible tests.

## Lightweight trace record

Use project conventions where available. Otherwise preserve equivalent relationships to:

```text
approved requirement revision -> OpenSpec change/specification -> acceptance criterion
                              -> implementation task/slice -> test -> result -> verification
```

The relationship record may be JSON, YAML, a project registry, or fields in an existing canonical export.
It must remain project-local, deterministic, and navigable in the living dashboard.

## Staleness

When a linked requirement revision changes, mark the specification as potentially stale until semantic
review confirms it still matches or updates the OpenSpec artifacts. Do not silently overwrite the consumed
revision and call the specification current.
