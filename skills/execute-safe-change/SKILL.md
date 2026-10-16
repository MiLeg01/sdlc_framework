---
name: execute-safe-change
description: Plan and execute an authorized state-changing operation with exact target binding, a genuinely non-mutating dry run, locks, idempotency, checkpoints, redacted audit evidence, bounded retries, verification, and rollback readiness. Use for consequential repository, infrastructure, account, data, or service mutations. Do not use for read-only analysis, vague bulk authorization, irreversible actions without an accepted recovery plan, or adapters whose dry-run path can still write.
---

# Execute a state change safely

Fail closed whenever authorization, identity, scope, preconditions, or recovery is ambiguous.

## Bind authorization and plan

1. Resolve the actor, exact operation, full resource identities, environment, writable fields, quantity,
   time window, protected targets, and approval authority.
2. Capture current fingerprints, dependencies, locks, quotas, and rollback prerequisites.
3. Produce an immutable operation plan with stable IDs, ordered actions, preconditions, expected effects,
   verification, rollback, and abort thresholds. Re-plan after material drift.

## Prove the dry run

Use a separate adapter or code path that is structurally incapable of writes. It may resolve identities,
read current state, evaluate policy, calculate the exact diff, and validate recovery. A boolean flag on the
production mutation path is insufficient unless the implementation proves no write-capable call is reachable.

## Execute

1. Reconfirm authorization and target fingerprints immediately before mutation.
2. Acquire the narrowest valid lock or concurrency guard.
3. Apply idempotent actions in small recoverable batches with checkpoints and stable operation keys.
4. Bound retries to classified transient failures; never retry authorization, identity, policy, or invariant
   failures as though they were transient.
5. Redact secrets and sensitive values from logs while preserving actor, plan ID, resource identity,
   timestamps, decisions, outcomes, and hashes needed for audit.
6. Stop on drift, unexpected cardinality, partial invariant failure, lost lock, exhausted retry budget, or
   an unavailable verifier.

## Verify and recover

Verify intended postconditions and absence of prohibited effects using an independent read path. Reconcile
every planned action as applied, skipped, failed, or rolled back. Execute the accepted rollback when safe;
otherwise contain the change and escalate with exact state and one recovery action.

Complete only when authorization, plan, dry run, execution, verification, audit evidence, and recovery state
reconcile. Provider-specific commands, identities, and policy rules remain project-local adapters.
