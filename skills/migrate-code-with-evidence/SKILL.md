---
name: migrate-code-with-evidence
description: Migrate one bounded code slice from a read-only source into an isolated target using reconstructed behavior, accepted requirements, traceable scenarios, strict TDD, deterministic manifests, and independent verification. Use for approved code-language or platform migration with a runnable validation path. Do not use for bulk prompt translation, direct source-tree rewrites, embedded credentials, or migrations whose behavior and authority are unresolved.
---

# Migrate code with evidence

Treat model-generated code as an untrusted implementation proposal. The source remains read-only, target
writes stay isolated, credentials remain external, and network use is disabled by default unless explicitly
authorized and recorded.

## Establish the migration boundary

1. Inventory and fingerprint the bounded source with `inventory-codebase`.
2. Reconstruct behavior, dependencies, data flow, error semantics, and unknowns with
   `analyze-legacy-system`; do not translate from filenames or comments alone.
3. Derive or reconcile accepted target requirements and scenarios with
   `derive-modernization-requirements`. Preserve conflicts and behavior intentionally not migrated.
4. Define target constraints, interfaces, security boundaries, dependency policy, coexistence, rollback,
   and validation access. Stop when target authority is missing.
5. Create a manifest using `assets/migration-manifest.example.json` and validate it with
   `scripts/validate_migration_manifest.py`. The detailed contract is in
   `references/migration-contract.md`.

## Migrate one slice

Select one dependency-ready vertical slice. Record source artifacts, requirements, acceptance scenarios,
target artifacts, tests, and exact validation commands. Practice `test-driven-development` as P0: prove a
behavior-relevant RED in the target, implement only enough for GREEN, refactor while green, then broaden to
contract, integration, migration, security, and performance checks required by the risk model.

Generated output must stay inside the declared target root. Never put credentials in prompts, manifests,
logs, fixtures, or source; never allow an agent to choose or execute destructive commands; never overwrite
the source tree; and never treat successful generation as behavioral parity.

## Verify and hand off

Compare source evidence and target observations at the scenario boundary. Record intentional differences,
unsupported constructs, manual conversions, false positives, failures, and residual risk.

Before replacing or refactoring complex business logic, use `mutation-testing` to check whether the
characterization or parity tests meaningfully constrain the behavior they claim to pin down. Apply it to the
migrated target implementation, the characterization harness, or an equivalent supported implementation. Do
not attempt to mutate an unsupported legacy source language; record `NOT_SUPPORTED` for that source and state
which supported artifact was assessed instead. Run complete target
gates plus `audit-delivery-traceability`; use `review-code-change`, `privacy-security-reviewer`, and
`test-behavior-reviewer` when consequence and independence justify them.

Complete only when the slice has a resolved evidence-to-test chain, identical focused RED/GREEN command,
isolated target output, broader validation, a resolved mutation quality status where supported, reviewer
disposition, and recovery point. Otherwise report the
slice as partial or blocked.
