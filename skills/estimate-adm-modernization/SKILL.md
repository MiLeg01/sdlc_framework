---
name: estimate-adm-modernization
description: Scope, calibrate, aggregate, and independently review evidence-linked ADM modernization effort using non-overlapping outcome-based work units and three-point person-day estimates. Use for application development and maintenance migration, rewrite, replatform, remediation, testing, data conversion, integration replacement, cutover, or decommissioning scenarios. Do not use before source coverage and target outcomes are bounded, to convert source size directly into effort, or to present an unreviewed range as a commitment, schedule, staffing plan, or cost.
---

# Estimate ADM modernization effort

Treat ADM estimation as four gates: scope, estimate, deterministic aggregation, and independent review.
Require a current source fingerprint, canonical evidence, one coherent modernization scenario, target
architecture, delivery model, explicit coverage, and an identified estimation unit.

Load the compact project synopsis and only the analysis, requirements, architecture, complexity, dependency,
data, integration, and uncertainty records relevant to the selected scenario. Resolve every driver back to
canonical evidence; do not reload the whole source estate merely to assemble the estimate.

Read `references/work-unit-model.md` before decomposition, `references/estimation-model.md` before assigning
effort, and `references/review-checklist.md` before publication. Use
`references/adm-estimation-package.schema.json` as the portable package contract.

## Scope

1. Define the outcome, strategy, inclusions, exclusions, assumptions, quality obligations, and source
   denominator. Keep materially different strategies as separate scenarios.
2. Decompose capabilities and requirements into non-overlapping work units that deliver reviewable target
   outcomes. Files, programs, lines, graph nodes, and generated stories are evidence signals, not units of
   delivery by themselves.
3. Add explicit data, integration, batch, security, observability, environment, test, performance, cutover,
   coexistence, discovery, and retirement units when applicable.
4. Link each unit to available source artifacts, requirements, capabilities, dependencies, evidence, and
   unresolved questions. Preserve unknown dimensions instead of extrapolating silently.
5. Reconcile shared services and cross-cutting work once. Set estimates to null and status to `SCOPED`.

## Estimate

1. Select calibration in this order: comparable organizational actuals, comparable team actuals, validated
   external benchmark, structured expert judgment, or unavailable. Record provenance and comparability.
2. Use external factor catalogs only as sourced taxonomies unless their delivery population, inclusions,
   technology, quality bar, and normalization establish comparable actuals.
3. Estimate each unit in person-days with `0 <= optimistic <= mostLikely <= pessimistic`. Put known work in
   the most-likely value and named uncertainty in credible favorable and adverse paths.
4. Keep structural, behavioral, operational, data, interface, security, test, and environment drivers
   separate. Evidence for one dimension does not clear another `UNKNOWN` dimension.
5. Keep effort distinct from elapsed schedule, staffing, cost, and calendar contingency. Avoid duplicate
   buffers for risks already represented in pessimistic values.
6. Set status to `ESTIMATED` and run
   `scripts/summarize_adm_estimate.py <package.json> --output <summary.json>`.

## Review

Delegate the completed package and summary to a fresh reviewer when independence matters. The reviewer
checks fingerprint, coverage, traceability, calibration, factor mappings, arithmetic, shared-work accounting,
omissions, optimism, precision, and scenario consistency without changing estimator values.

Use `BLOCKED` for stale fingerprints, malformed totals, incoherent scenarios, or material untraceable scope.
Use `NEEDS_REWORK` for correctable omissions or bias. Set package status to `REVIEWED` only after PASS or an
explicitly accepted residual finding with an owner.

## Completion

Return the scoped package, deterministic summary, review findings, coverage limits, calibration provenance,
unresolved questions, and presentation-safe ranges. An uncalibrated estimate remains rough-order-of-magnitude
with LOW confidence. Re-estimate prospectively from delivery actuals; never rewrite historical estimates to
match actual effort.
After review, checkpoint the scenario ID, source/requirement revisions, summarized ranges, assumptions,
uncertainties, and canonical package paths in project memory.
