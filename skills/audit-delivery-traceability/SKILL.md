---
name: audit-delivery-traceability
description: Independently and read-only audit forward and reverse traceability from source through evidence, requirements, specifications, scenarios, implementation, tests, verification, and commits. Use before consequential completion, handoff, reporting, migration acceptance, or completeness claims. Do not use to repair findings, implement missing work, or treat a generated dashboard as canonical evidence.
---

# Audit delivery traceability

Audit and report; do not silently repair canonical state or implementation.

## Contract

Use the chain, graph contract, and severity rules in `references/traceability-contract.md`.

If the project exports a flat trace matrix, run:

```bash
python3 scripts/audit_trace_matrix.py <trace.csv> --format markdown
```

If the project exports normalized registries as a graph, run:

```bash
python3 scripts/audit_trace_graph.py <trace-graph.json> --format markdown
```

The helpers check structural integrity only. Continue the semantic audit even when they pass.

## Procedure

1. Confirm the authoritative registries, schemas, source hashes, Git state, and audit scope.
2. Recompute applicable inventory/disposition coverage and validate stable IDs, enums, references,
   reciprocal links, lifecycle rules, coordinates, hashes, generated-view fingerprints, and non-overlapping
   ownership.
3. Walk the delivery chain in both directions. Do not infer coverage from similar names, aggregate test
   passes, generated totals, or implementation presence alone.
4. Where a `mutation` link is recorded, report a surviving mutant against an in-scope criterion as a
   test-quality finding rather than treating the chain as unlinked. Coverage and a green result are not
   evidence that a test would detect incorrect behavior.
5. Verify that implemented behavior has approved scenarios, tests map to scenarios, results identify a
   reproducible command/environment, verification is independent where required, and completion points
   to a relevant commit or immutable artifact.
6. Reconcile canonical totals with generated reports and dashboards. Fix recommendations must target
   canonical data or generators, never generated output.
7. Return `PASS`, `PASS_WITH_LIMITATIONS`, or `FAIL` with stable finding IDs, severity, broken link,
   evidence, impact, and smallest remediation.

## Severity

- Critical: a verified/completed claim lacks authoritative behavior or required evidence integrity.
- Major: a required chain link is missing, stale, invalid, or uncovered.
- Warning: hygiene is weak and likely to drift, but no completion claim is currently false.
- Info: an honest early-lifecycle gap.

Stop when every in-scope chain was checked and limitations are explicit. A clean audit does not authorize
state mutation, implementation, or commit.
