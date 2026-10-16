# ADM estimate review checklist

## Scenario and coverage

- One modernization strategy and target outcome are coherent.
- Architecture, quality attributes, environments, delivery model, inclusions, and exclusions are explicit.
- Source fingerprint and analyzed coverage are current.
- Data, interfaces, security, batch, operations, testing, coexistence, cutover, and retirement are included
  or explicitly excluded.

## Traceability and decomposition

- Material units link to source evidence and target decisions.
- Dynamic calls, missing sources, contradictions, and runtime questions remain visible.
- Shared components are counted once and consumers are linked.
- Units are outcome-based rather than file-based.

## Calibration and bias

- Calibration is real, dated, normalized, and comparable.
- External taxonomies are distinguished from delivery actuals.
- Target classifications come from target evidence, not a reference application's counts or ratings.
- Structural and operational unknowns remain separate.
- Productivity, automation, reuse, team, and pessimistic-case assumptions are explicit.
- Anchoring, optimism, mechanical narrow ranges, and unsupported precision are visible.

## Arithmetic and publication

- Every estimate satisfies `0 <= optimistic <= mostLikely <= pessimistic`.
- Deterministic aggregation reproduces unit and workstream totals.
- Unestimated units and warnings remain visible beside totals.
- Effort, schedule, staffing, contingency, and cost are distinct.

Classify findings as BLOCKER, HIGH, MEDIUM, or LOW. Return findings without silently changing values.
