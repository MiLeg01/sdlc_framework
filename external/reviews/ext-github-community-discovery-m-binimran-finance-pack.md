---
schema_version: 1
id: ext-github-community-discovery-m-binimran-finance-pack
source_id: github-community-discovery
repository: m-binimran/finance-pack
path: skills/forecasting/SKILL.md
revision: 35ff1b49e7ffa1708296b84503a4e4236fbbff48
trust: COMMUNITY
license: MIT
license_scope: Repository LICENSE applies to the reviewed skill agent hook and template files; terms appear to permit modification and redistribution with notice retention.
security_class: MCP/REMOTE TOOLING
relationship: INSPIRED-BY
status: PROMOTION-CANDIDATE
reviewed_at: 2026-09-02
---

# Review: finance-pack forecasting and review workflow

## Review boundary and evidence

Reviewed the revision-pinned repository metadata, root README and LICENSE, forecasting, budget-planning and
variance-analysis skills, the numbers-reviewer agent, the projection guard, and connector documentation.
The package was read as text only. No installer, hook, connector, test, or downloaded code was executed.

## Provenance

Observed fact: the source is a community repository discovered through the configured GitHub community
source. The reviewed revision is immutable and was the repository's default-branch head during discovery.
The repository describes itself as an early Claude Code pack for financial analysis and FP&A.

## License assessment

Observed fact: the repository contains an MIT LICENSE naming the package contributors. The license appears to
permit modification and redistribution with copyright and permission notice retention. This review does not
provide legal advice. The promotion uses `INSPIRED-BY`; no source wording, hook code, or package structure is
copied.

## Security and supply-chain characteristics

The package contains installers, automatically invoked Python hooks, shell and PowerShell surfaces, agent
definitions, and MCP connector guidance for browser, market-data, and SEC data access. Connector placeholders
can lead to remote services, credentials, licensed data, and untrusted content. None of these executable or
remote surfaces was installed or run. They require separate security, privacy, licensing, and data-boundary
review before any project adopts them.

## Semantic comparison with current commons

- `estimate-adm-modernization`: `OVERLAP` on explicit assumptions, ranges, confidence, and independent review,
  but it estimates modernization effort rather than operating project revenue, cost, margin, cash, and EAC.
- `plan-work`: `OVERLAP` on bounded assumptions and validation; financial modeling is outside its scope.
- spreadsheet support: `OVERLAP` on artifact manipulation, not on the forecast decision model.
- independent reviewer pattern: `EXTENSION`; Commons has architecture, privacy/security, and test reviewers,
  but no financial-forecast specialist.
- project financial forecasting: `NEW`.

## Useful novel patterns

- driver-based forecasting instead of flat percentage extrapolation;
- strict separation of historical actuals, forecasts, scenarios, and targets;
- budget-versus-actual decomposition into price, volume, rate, usage, mix, timing, and structural effects;
- explicit projection labeling and source integrity checks;
- independent numerical review before consequential use.

## Rejected or non-canonical patterns

- Claude-specific commands, directory layout, hooks, models, and installation scripts;
- automatic hook enforcement as a universal control;
- investment-research, DCF, securities, and compliance content outside project financial management;
- placeholder MCP services and provider-specific market-data integration;
- copied wording, naming, examples, and package structure.

## Promotion candidates

1. A runtime-neutral `forecast-project-financials` skill covering baseline, actuals, remaining-work drivers,
   EAC, margin, variance, scenarios, reconciliation, confidence, and decision outputs.
2. A deterministic project-forecast calculator with explicit input/output contracts and boundary tests.
3. A separately delegated `financial-forecast-reviewer` because independent numerical recomputation and
   specialist challenge materially reduce confirmation bias and commercial risk.

The proposed relationship is `INSPIRED-BY`. Organization-specific terminology, rate cards, thresholds, and
approval routes must remain project-local.

## Required evaluations before promotion

- Positive forecast, negative statutory/investment-advice request, collision with ADM estimation, output and
  source invariants, and missing-actuals failure behavior.
- Reviewer independence, no-edit boundary, recalculation evidence, confidential-data handling, and no
  commercial approval.
- Executable success, duplicate-period, missing-input, zero-denominator, and scenario arithmetic tests.
- Targeted mutation testing of financial arithmetic after the normal suite is green.

## Final recommendation

`PROMOTION-CANDIDATE`. Promote only the generalized project-financial methodology, deterministic arithmetic,
and independent review boundary. Do not install or promote the source package, hooks, connectors, or runtime
layout.

No external code was executed and no external capability was installed during this review.
