# Full legacy-analysis orchestration contract

`analyze-legacy-system` is a system-level coordinator. A bounded slice is one internal execution unit and is
not the default user-facing completion boundary. `FULL` means every relevant artifact is accounted for;
`DEEP` means important behavior is semantically understood. Default completion requires both.

## Modes

- `FULL` is the default. It covers every eligible artifact in the configured inventory denominator.
- `BOUNDED` requires an explicit user selector. Everything outside that selector remains recorded as
  `OUT-OF-SCOPE` with the bounded-scope reason.
- `CONTINUE` requires a checkpoint. It preserves terminal artifact and validated-slice state only when the
  source hash and slice input fingerprint still match; changed inputs and dependent fan-in stages are reset.

Natural-language scope is resolved before calling the deterministic coordinator. CLI spelling is an adapter
concern; the semantic modes are runtime-neutral.

## Canonical state

Run the coordinator against the one validated inventory:

```bash
python3 scripts/coordinate_analysis.py plan \
  --inventory analysis/source-inventory.json \
  --output analysis/analysis-state.json \
  --mode full --max-concurrency 4
```

The state contains the complete artifact coverage register, bounded slices, targeted context artifact IDs,
bounded project-memory context-package requests, the full analysis DAG, safe pending execution stages,
lifecycle fan-in status, ownership, fingerprints, and completion blockers. Slice fingerprints include primary
artifacts plus contextual copy/includes, contracts, configuration, and build dependencies. Workers receive
the exact fingerprint and write only their isolated `analysis/slices/<slice-id>.json` result.

Integrate a worker packet centrally:

```bash
python3 scripts/coordinate_analysis.py record \
  --state analysis/analysis-state.json \
  --result analysis/worker-results/<slice-id>.json \
  --output analysis/analysis-state.json
```

A result accounts for every primary artifact assigned to that slice and supplies evidence IDs for every
`ANALYZED` item. Executable artifacts also supply `depth_status`, every applicable depth dimension, semantic
counts, and complexity entries that distinguish `MEASURED` from `ASSESSED`. The coordinator, not the worker,
validates hashes and depth, accepts the packet, updates canonical coverage, merges validated memory proposals,
and decides when synthesis may begin.

Record serialized fan-in stages with `stage`, then enforce completion with:

```bash
python3 scripts/coordinate_analysis.py validate --state analysis/analysis-state.json
```

Validation fails while any relevant artifact is `PENDING`, any required lifecycle stage is not validated,
or the inventory itself is invalid. `BLOCKED` artifacts are accounted only when their reason is explicit;
they are returned in a `PASS_WITH_BLOCKED` result rather than silently hidden. An `ANALYZED` artifact that
has not passed its depth gate still blocks completion.

## Coverage statuses

Every discovered inventory artifact appears exactly once with source path, hash, language/type, logical
component, assigned slice, status, evidence IDs, related requirements, and exclusion reason when applicable.
Allowed states are `PENDING`, `ANALYZED`, `COVERED-BY-PARENT`, `NON-EXECUTABLE-SUPPORT`,
`DUPLICATE-VARIANT`, `OUT-OF-SCOPE`, `SKIPPED-WITH-REASON`, and `BLOCKED`.

## Depth gate

Use `DEEP_VERIFIED`, `ANALYZED`, `PARTIAL`, `BLOCKED`, or `NOT_APPLICABLE`. COBOL, PL/I, Java, and other
important executable business components require `DEEP_VERIFIED` for full completion. Validate, as applicable:

- structure and meaningful procedure/function control flow;
- inputs, outputs, fields, transformations, persistence, and shared data definitions;
- calls, integrations, runtime services, middleware, protocols, and unresolved dynamic edges;
- explicit business rules, calculations, validations, decisions, exceptions, and side effects;
- interface contracts, faults, security, transactionality, concurrency, logging, resilience, and recovery;
- maintainability, coupling, duplication, complexity, testability, and migration significance;
- unknowns and defect candidates with `PRESERVE`, `FIX`, or `DECISION_REQUIRED` rather than silent repair.

`Detailed` means semantic depth, not line-by-line syntax narration. Stop drilling down only when additional
syntax no longer changes the behavioral understanding.

For multiple implementations, synthesis records `EQUIVALENT`, `PARTIALLY_EQUIVALENT`, `DIVERGENT`,
`MISSING`, or `UNKNOWN` per compared flow/rule/contract with evidence. Names alone never prove equivalence.

## Fan-out and fan-in

Independent technology and support domains may run concurrently within the configured bound. Workers do not
rescan the repository, allocate canonical IDs, reconcile duplicates, edit requirements or OpenSpec state,
write the dashboard, update coverage, commit, or certify completeness. Central fan-in performs cross-system
synthesis, canonical requirement reconciliation, selected OpenSpec preparation, dashboard refresh, and the
final coverage and traceability gate.
