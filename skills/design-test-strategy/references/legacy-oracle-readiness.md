# Legacy oracle authority and readiness

Use this contract when a test strategy starts from reconstructed legacy behavior, generated rule or flow
packages, characterization output, migration evidence, or source-derived test vectors. It governs the
authority of the expected outcome before test-layer selection; it does not approve business behavior.

## Oracle authority

Assign exactly one authority state to each obligation:

- `APPROVED_INTENT`: an accountable owner approved the expected behavior, with a decision reference and date.
- `OBSERVED_SOURCE`: current source or runtime evidence supports an observable legacy behavior, but no owner has
  approved it as target intent.
- `UNRESOLVED`: the expected result is missing, generic, contradictory, stale, inaccessible, or otherwise not
  strong enough to support a behavioral assertion.

Confidence, priority, test count, generated prose, or a source-derived status never upgrades oracle authority.
When approval depends on source evidence, bind it to the current evidence fingerprint; source drift requires
revalidation rather than silent rebasing.

## Readiness

Derive one readiness state independently of the selected test layer:

- `READY_FOR_EXPECTED_OUTCOMES`: approved intent, current matching evidence, a concrete observable oracle, and
  the required construction, fixture, environment, and execution bindings are present.
- `CHARACTERIZATION_ONLY`: observable legacy behavior can be captured, but it is not approved target intent.
- `SCENARIO_ONLY`: the inputs, preconditions, or actions are useful for design, but the expected outcome is
  absent, generic, or not currently verifiable.
- `REVIEW_REQUIRED`: contradictory evidence, an undispositioned suspected defect, stale approval, or another
  material decision prevents assertion generation.
- `BLOCKED`: malformed, inaccessible, unsafe, or materially stale evidence prevents even a credible scenario.

A suspected defect stays `CHARACTERIZATION_ONLY` or `REVIEW_REQUIRED` until an accountable decision explicitly
chooses preservation, correction, or exclusion. Observed behavior that conflicts with approved intent remains
visible as characterization evidence and never silently replaces the approved oracle.

## Generation and execution status

Track artifact and execution progress separately from readiness. Generated output is not proof that it compiles,
runs, or detects incorrect behavior. At minimum distinguish:

1. generated template or proposal;
2. generated compile-ready artifact;
3. applied to an authorized test root;
4. compiled;
5. executed;
6. passed or failed;
7. blocked or review-required.

Never call a scenario executable merely because a framework dependency, test directory, endpoint name, selector,
or source method exists. Require the concrete bindings needed by the selected layer, protect human-authored
tests, and record any environment or data prerequisite that remains external.

## Output requirements

For each legacy-derived row in the risk-to-test matrix record:

- behavior or failure mode and exact evidence links;
- oracle authority and readiness;
- selected layer and why it is the lowest credible observer;
- expected observation, or the exact missing/contradictory evidence;
- fixture, environment, construction, data, and runtime bindings;
- suspected-defect disposition when relevant;
- artifact status and execution status as separate fields;
- owner, exit criteria, residual risk, and next decision.

Ordinary non-legacy strategies with accepted behavior may use the standard workflow without these extra states.
