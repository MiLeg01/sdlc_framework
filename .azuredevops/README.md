# Azure DevOps quality-pipeline architecture

Agent Commons uses four repository-owned YAML pipelines with explicit cost profiles. For the
click-by-click Azure DevOps configuration, variable values, permissions, first-run order, and troubleshooting,
follow [`SETUP.md`](SETUP.md).

## Pipeline architecture

| YAML entry point | Profile | Scope | Baseline promotion |
| --- | --- | --- | --- |
| `commons-pr-validation.yml` | `fast` | Static checks plus changed capabilities, dependents, and affected workflows | Never |
| `commons-main-validation.yml` | `standard` | Static checks plus critical capabilities and workflows in bounded parallel shards | Never |
| `commons-nightly-quality.yml` | `full`, three stochastic runs | Complete capability/workflow portfolio, visual validation, aggregation, and retained trends | Only after warning-free PASS |
| `commons-weekly-deep-eval.yml` | `deep`, five stochastic runs | Complete portfolio, visual validation, methodology mutation tests, and weekly report | Never |

### Two mutation systems, never one score

`templates/mutation-validation.yml` runs **Agent Commons methodology mutation testing**: it mutates canonical
skills and contracts to prove the Commons evaluations detect degraded agent behavior. It is repository quality
infrastructure for this library.

**Application mutation testing** is a different system, owned by the `mutation-testing` skill, which mutates a
delivery project's application code to evaluate the strength of that project's tests. It runs in the
project's own pipeline against the project's own build, is gated by the project's own baseline, and must not
depend on this repository's semantic executor, judge, or eval baselines. Do not aggregate results from the two
systems, and do not reuse this repository's mutation artifact names for application runs.

Recommended profiles for a delivery project's own pipeline, expressed as methodology rather than as
provider-specific YAML, are defined in `skills/mutation-testing/references/quality-gates.md`: targeted
mutation on changed critical production code for pull requests, broader targeted mutation on main where run
cost permits, a broader suite nightly with baseline comparison, and optional full or deep analysis weekly.
Agent Commons does not currently generate pipeline templates for delivery projects, so that guidance stays in
the canonical skill and the project supplies its own CI wiring.

Main, Nightly, and Weekly first run the low-cost `smoke` alias of FAST against `inventory-codebase`. That stage
checks semantic executor/judge connectivity, verifies the configured Nightly definition and Azure history
access, resolves the accepted baseline or bootstrap fallback, and publishes one complete result artifact before
expensive jobs begin. PR semantic execution remains optional so deterministic changed-impact validation can
still report useful evidence when model access is unavailable. PR validation is credential-free: it does not
import the semantic variable group, does not map `System.AccessToken`, and compares only with the checked-in
versioned bootstrap.

All jobs use Microsoft-hosted `ubuntu-24.04` agents. Templates install Python 3.11, pinned Node.js and Codex
components where required, and pinned Playwright/Chromium dependencies only for visual jobs.

## Semantic execution boundary

`templates/setup.yml` installs `@openai/codex@0.150.1`. The unified runner invokes
`tools/evals/semantic_executor.py` and `tools/evals/semantic_judge.py` directly; executable commands are not
pipeline configuration.

The Codex executor runs noninteractively in an isolated temporary workspace with schema-constrained output.
Golden expectations are not copied into that workspace. The independent judge uses a separate provider path,
receives hidden expectations only after execution, revalidates transferred artifact hashes, and cannot execute
the capability. The executor environment excludes judge, Azure pipeline, and unrelated credentials.

The supported judge transports are OpenAI, direct Azure OpenAI, and Azure OpenAI behind APIM. The operational
setup reproduces the existing user-level Codex APIM provider for both executor and judge while keeping the
judge process and hidden expectations separate. APIM credentials are environment-backed and explicitly
filtered from executor shell commands. Current YAML does not reference an Azure Resource Manager service
connection.

## Baseline and history model

The sole Azure definition reference is `baselinePipelineDefinitionId`, which identifies
`commons-nightly-quality.yml`. It serves both purposes:

- resolve the newest successful `main` Nightly build containing a `last-green-baseline` artifact;
- read retained Nightly `quality-aggregate` artifacts for 7-day and 30-day reporting.

If no eligible Nightly artifact exists yet, evaluation uses the checked-in `evals/baselines/v1.0.0.json`
bootstrap.
Nightly promotion requires `main`, profile `full`, overall `PASS`, and zero warnings or failures. Only then is
the new baseline artifact published. Failed, warning-bearing, Main, PR, and Weekly runs cannot replace the
accepted baseline.

`System.AccessToken` is mapped only on trusted Main/Nightly/Weekly definition, baseline, and history reads.
Repository checkout does not persist credentials, and PR validation never receives the token mapping.

## Failure and retry policy

Results distinguish `QUALITY_REGRESSION`, `DETERMINISTIC_FAILURE`, `PROTOCOL_FAILURE`, and
`INFRASTRUCTURE_FAILURE`. Quality or assertion failures are never retried. Executor and judge calls retry only
bounded, recognized transient conditions such as HTTP 429, temporary service failures, connection resets, and
timeouts. Final logs and attempt counts remain in the published result.

## Published evidence

Quality jobs publish JUnit plus `summary.json`, `quality-summary.json`, `quality-summary.html`,
`capabilities.json`, `performance.json`, `failures.json`, and runner logs. Azure build summaries link the
important status and failure information directly from the run. Visual jobs publish actual screenshots and
their comparison report. Nightly and Weekly aggregates publish consolidated dashboards; Weekly also emits
`weekly-quality-report.html`.

Unavailable baseline, history, token, model, and visual evidence is represented explicitly. Cross-runtime
validation checks adapter and installation contracts for Codex, Claude Code, Cline, and OpenCode without
claiming native execution where only generated wrappers or metadata exist.

## Repository validation

The primary configuration check makes no model request:

```bash
python3 tools/evals/run_evals.py --check-config --output output/config-check
```

The local semantic smoke command is:

```bash
python3 tools/evals/run_evals.py --profile smoke --capability inventory-codebase --repeat 1 \
  --require-semantic --compare-baseline evals/baselines/v1.0.0.json --output output/eval-smoke
```

Azure adds the Nightly definition/history check and publication contract around that command. Exact local
commands for all four profiles are maintained in [`SETUP.md`](SETUP.md).
