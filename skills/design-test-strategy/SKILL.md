---
name: design-test-strategy
description: Design a risk-based test strategy that maps observable behavior and failure modes to the smallest credible portfolio of unit, contract, integration, browser, migration, security, performance, and end-to-end tests. Use before implementation, for coverage gaps, or when test-layer choice is disputed. Do not use to write production behavior, inflate coverage metrics, mandate every test layer, or replace focused TDD execution.
---

# Design a test strategy

Start from accepted behavior, architecture boundaries, users, data, operational context, change surface,
known defects, and verification constraints. Coverage percentage is supporting data, not the objective.

When expected behavior comes from a legacy system, generated rule package, characterization run, or other
source-derived evidence, read `references/legacy-oracle-readiness.md` before selecting executable tests. A
source observation is not automatically approved target intent, and a generated expected sentence is not an
oracle.

## Model risk

For each behavior or failure mode, assess impact, likelihood, detectability, blast radius, reversibility,
boundary count, data sensitivity, concurrency, external dependency, migration or compatibility risk, and
cost of a late discovery. Identify the evidence needed to believe the risk is controlled.

## Select layers

Choose the lowest layer that can credibly observe the failure, then add higher layers only for boundaries
or emergent behavior:

- unit or component tests for local rules, transformations, and edge cases;
- contract tests for schemas, protocol semantics, compatibility, and provider/consumer expectations;
- integration tests for persistence, messaging, frameworks, transactions, and real dependency wiring;
- browser or UI tests for user journeys, state transitions, rendering, and interaction contracts;
- migration or characterization tests for source parity, data conversion, reconciliation, and rollback;
- security tests for authorization, isolation, hostile input, secrets, and abuse paths;
- performance tests for explicit latency, throughput, resource, or scale risks;
- end-to-end tests for a small set of critical cross-system outcomes.

## Produce the strategy

Return a risk-to-test matrix with behavior or threat, risk, chosen layer, fixture or environment, oracle,
negative and boundary cases, ownership, command or harness, required evidence, and exit criteria. Identify
deliberate omissions and their residual risk. Keep flaky, slow, or production-dependent tests quarantined
from claims until their reliability is demonstrated.

For legacy-derived obligations, also record oracle authority and readiness. Permit expected-outcome tests only
when approved intent, current matching evidence, a concrete observable oracle, and required execution bindings
are present. Keep observed legacy behavior as characterization evidence when approval is absent. Keep generic
or missing outcomes scenario-only, route contradictory evidence or undispositioned defect candidates to review,
and block malformed, stale, inaccessible, or unsafe evidence. Do not collapse generated, compile-ready,
applied, compiled, executed, passed, failed, blocked, and review-required states into one “automated” label.

Coverage answers whether code was executed, not whether a test would notice incorrect behavior. Where the
technology supports it, name `mutation-testing` as the strength check for the layers carrying the highest
risk, and state the expected mutation scope per risk rather than a single global score.

Use `test-driven-development` to implement each approved behavior. Ask a fresh `test-behavior-reviewer` to
challenge consequential coverage, RED validity, boundary cases, and false confidence.
