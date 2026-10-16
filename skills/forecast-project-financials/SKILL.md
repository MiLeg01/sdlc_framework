---
name: forecast-project-financials
description: Build and maintain an evidence-backed project or engagement financial forecast from an approved baseline, actuals, remaining-work drivers, scenarios, and delivery evidence. Use for budget, revenue, cost, margin, cash, earned-value, variance, or estimate-at-completion decisions. Do not use for statutory accounting, tax or investment advice, unsupported commitments, or forecasts whose source data and assumptions cannot be identified.
---

# Forecast project financials

Treat a forecast as a dated decision model, not a confident narrative. Preserve the approved baseline,
separate actuals from estimates, expose the drivers, and show how uncertainty changes the outcome.

## Establish the boundary

1. Resolve the project or engagement scope, forecast horizon, currency, fiscal calendar, reporting basis,
   approved baseline, materiality threshold, decision audience, and authoritative actuals.
2. Record which measures are required: revenue, cost, margin, cash, headcount or capacity, planned value,
   earned value, and commercial commitments. Do not invent unavailable measures.
3. Keep actual, committed, forecast, scenario, and target values distinct. Never overwrite the baseline to
   make current performance look aligned.
4. Record confidentiality and access constraints. Use only authorized rate, staffing, pricing, utilization,
   and client data; redact or aggregate outputs crossing a trust boundary.

## Build the forecast

1. Reconcile actuals through the as-of period to the authoritative ledger, approved time or cost system, and
   delivery evidence. Record unresolved differences rather than forcing a tie.
2. Forecast remaining work from explicit drivers: work packages, staffing, rates, utilization, productivity,
   procurement, travel, subcontractors, milestones, billing rules, and delivery dependencies as applicable.
   Prefer bottom-up drivers over a flat percentage extrapolation.
3. Derive the base estimate at completion:
   - actual-to-date plus forecast-to-complete;
   - revenue, cost, margin and cash where available;
   - budget and revenue variances with favorable or unfavorable direction stated;
   - earned-value measures only when planned value, earned value, and actual cost use compatible scope,
     periods, units, and status dates.
4. Build at least a base and downside case when uncertainty is material. Add an upside case only when its
   assumptions are credible and decision-relevant. Change named drivers rather than arbitrary totals.
5. Run `scripts/calculate_project_forecast.py <forecast.json>` when the input can follow
   `assets/project-financial-forecast.example.json`. The tool validates period completeness and calculates
   baseline, actual-to-date, remaining forecast, estimate at completion, margin, variance, CPI, SPI, TCPI,
   and scenario outcomes deterministically.
6. Reconcile the output back to the source totals and independently reperform material formulas. Tool output
   is calculation evidence, not authorization for a commercial commitment.

## Explain movement and decisions

For each material movement, separate:

- observed variance from budget or previous forecast;
- timing effects from permanent effects;
- price, volume, rate, mix, productivity, scope, schedule, and one-off drivers;
- owner and corrective action;
- impact on remaining work and estimate at completion;
- confidence and evidence freshness.

Show the forecast bridge from the previous approved view to the current view. Label every future value as a
forecast or scenario and state the material assumptions. Avoid false precision; provide ranges when drivers
cannot support a point estimate.

## Independent review

For consequential steering, client reporting, commercial decisions, or externally shared results, delegate
the completed forecast pack to `financial-forecast-reviewer` in a fresh read-only context. The reviewer
challenges sources, period and unit consistency, formula integrity, scenario logic, reconciliation, and
unsupported certainty. The forecast owner remains responsible for corrections and approval.

## Optional consulting-delivery profile

Map the generic model to locally approved engagement roles and governance. Typical roles include engagement
sponsor, delivery lead, workstream lead, commercial owner, finance controller, and client decision owner.
Keep organization-specific rate cards, margin thresholds, approval routes, terminology, branding, and client
identifiers project-local. The canonical calculation and evidence rules remain unchanged.

## Output and completion

Return a dated forecast pack containing source and reconciliation status, baseline, actuals, remaining-work
drivers, estimate at completion, variance bridge, scenarios, assumptions, risks, confidence, decisions, and
review status. Complete only when periods and units reconcile, actuals are sourced, assumptions are explicit,
scenario arithmetic is reproducible, material variances have owners, and limitations are visible.
