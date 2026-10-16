# Delivery traceability contract

Expected chain when applicable:

```text
source -> evidence -> rule -> gap -> requirement -> specification -> scenario
       -> implementation -> test -> result -> verification -> commit
```

Early-lifecycle records may legitimately end before implementation. A later lifecycle claim may not skip
required prior links.

Where mutation testing applies, one optional link extends the chain after `test`:

```text
... -> test -> mutation (KILLED or SURVIVED) -> result -> verification -> commit
```

It is recorded as an extra `mutation` column carrying the mutant ID and outcome, and it is never required for
a valid chain. Its purpose is to distinguish "this acceptance criterion has a test" from "this acceptance
criterion has a test that actually detects incorrect behavior". A recorded `SURVIVED` mutation against a
criterion is a test-quality finding, not a broken chain link, and the audit reports it without repairing it.

Audit forward and reverse links, stable IDs, path existence, source coordinates/hashes, approval state,
scenario coverage, test identity, reproducible results, verifier independence, and commit relevance.
Keep superseded records and unresolved links visible.

The CSV helper expects these columns (extras are permitted):

`id,source,evidence,rule,gap,requirement,specification,scenario,implementation,test,result,verification,commit,status`

Statuses `implemented`, `verified`, or `complete` activate progressively stricter required links.

## Normalized graph export

Use the graph helper when canonical state spans multiple registries and reciprocal relationships or
lifecycle-dependent edges must be checked. The JSON object uses this shape:

```json
{
  "schema_version": 1,
  "nodes": [
    {"id": "REQ-001", "type": "requirement", "status": "approved"},
    {"id": "SPEC-001", "type": "specification", "status": "approved"}
  ],
  "edges": [
    {
      "source": "REQ-001",
      "target": "SPEC-001",
      "type": "specified_by",
      "reciprocal_type": "specifies"
    },
    {"source": "SPEC-001", "target": "REQ-001", "type": "specifies"}
  ],
  "lifecycle_rules": [
    {
      "id": "approved-requirement-has-specification",
      "node_type": "requirement",
      "statuses": ["approved"],
      "direction": "out",
      "edge_type": "specified_by",
      "related_type": "specification",
      "min_count": 1,
      "severity": "major"
    }
  ],
  "generated_views": [
    {
      "id": "stakeholder-dashboard",
      "expected_fingerprint": "canonical-export-sha256",
      "actual_fingerprint": "canonical-export-sha256"
    }
  ]
}
```

Rules:

- Node IDs and edge triples must be unique.
- Every edge endpoint must name an existing node.
- `reciprocal_type` requires the reverse edge with that type.
- Lifecycle rules apply only to the declared node type and statuses. `direction` is `in` or `out`;
  `related_type` constrains the opposite node; `min_count` defaults to one.
- Generated-view fingerprints must be produced by the project from canonical inputs. The helper compares
  supplied values; it does not invent a project-specific hashing algorithm.
- Omit lifecycle rules that are not applicable. Honest early-lifecycle graphs may pass without downstream
  implementation edges.

The graph helper does not prove source authority, behavioral equivalence, semantic correctness, verifier
independence, or commit relevance. Those remain judgment steps in the audit.
