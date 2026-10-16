# Agent Commons evaluations

Agent Commons capabilities are evaluated as production behavior, not only as parseable files. The canonical
architecture extends the existing scenario catalogs and unittest suites rather than replacing them.

## Evaluation levels

1. **Static / contract** validates canonical structure, IDs, schemas, references, and hard safety invariants.
2. **Capability behavioral** exercises one skill, agent, or tool against semantic facts and invariants.
3. **Cross-capability / integration** verifies handoffs and dependency boundaries across related capabilities.
4. **End-to-end project** evaluates a representative legacy, development, research, or Commons-governance flow.

Contracts under `contracts/` declare criticality, applicable metrics, scenarios, execution mode, and golden
references. Existing deterministic tests remain under their current directories. Workflow contracts compose
those tests and optional runtime-driven scenarios.

Small representative project fixtures live under `fixtures/projects/`. Each project has an `input/` boundary
for executor-visible material and a sibling `golden/` boundary used only by validation. Executors receive only
declared input artifacts and canonical source identity; they never receive Golden expectations. The independent
judge receives the fixture, generated result, evidence, and Golden expectations after execution. The portfolio
covers mixed-language legacy modernization, OpenSpec/TDD delivery, deterministic local research, dashboard
quality, and synthetic Austrian public-sector delivery.

## Reconciliation with the existing suite

- `skills/scenarios.yaml` and `agents/scenarios.yaml` remain the broad behavioral catalogs.
- Existing fixtures and unittest modules remain in place and are invoked by contract instead of being copied.
- `tools/validate_commons.py` remains the canonical structural validator and now also validates eval contracts.
- `catalog/capabilities.yaml` and the generated capability index remain the relationship source for impact
  selection; workflow contracts add explicit end-to-end membership.
- Assertions belong at the layer that produces the behavior. Template checks cover placeholders and runtime
  hooks; rendered-output tests cover generated locale controls and brand content.

## Quality and severity

`contracts/thresholds.json` defines the reusable quality dimensions and tolerances. A contract selects only
the dimensions that apply to it.

- **HARD_FAIL** protects non-negotiable behavior such as read-only source, valid structured output, evidence
  integrity, required dashboard domains, TDD RED evidence, ownership boundaries, coverage, and canonical
  structure.
- **REGRESSION_FAIL** indicates a quality score or stochastic pass rate below its configured threshold or
  accepted baseline tolerance.
- **WARNING** reports non-blocking drift such as runtime or tokens above their relative warning tolerance, or a semantic scenario
  that was selected without an external executor. Noise floors prevent meaningless timing/token warnings.

Exit code `0` means pass or warnings only, `1` means regression failure, and `2` means hard failure.

## Independent semantic judging

The runner prefers deterministic checks. A scenario uses semantic judging only when correctness cannot be
established deterministically. Production execution uses repository-owned entry points by default:

```bash
python3 tools/evals/run_evals.py --check-config
python3 tools/evals/run_evals.py --critical --repeat 3 --require-semantic
```

Use Python 3.11 or newer for the complete repository suite. When the launcher itself uses another Python,
pass `--python /path/to/python3.11` (or newer) for deterministic unittest subprocesses. Those subprocesses
run without inherited semantic-runtime settings or model credentials, so nested runner tests remain local and
deterministic even inside semantic CI jobs.

`tools/evals/semantic_executor.py` implements the runtime-neutral executor interface with Codex CLI as the
initial production runtime. `tools/evals/semantic_judge.py` implements the independent judge through the
provider-neutral OpenAI-compatible Responses API adapter. The runner invokes these paths internally; command
strings are not configuration and are not secrets. The legacy `--executor-command` and `--judge-command`
overrides remain only for protocol tests and deliberately supplied alternate adapters.

Both repository entry points receive one JSON object on standard input and return JSON on standard output. The executor must
return `generated_result`, bounded evidence records (`id`, fixture `source`, and `locator`), and optional
token/runtime metrics. The judge receives the same immutable fixture copy, scenario input,
expected facts/invariants, generated result, and evidence. Its output must match
the corresponding schemas under `schemas/`; the executor input schema deliberately has no golden-expectation
field. Judge assertions include PASS/FAIL, confidence, reason, evidence, and bounded metric
scores. Golden facts may be classified `CRITICAL`, `MAJOR`, or `MINOR`. Every declared expected fact,
invariant, required sequence item, and hard assertion must be covered
exactly once. The runner rejects incomplete, duplicate, or unexpected assertion coverage and rejects one
command serving as both executor and judge. Executors run from an isolated copy of the bounded fixture files
and selected capability resources. Codex runs non-interactively with an ephemeral session, schema-constrained
final output, a workspace-only permission profile, disabled command networking, and a fixed timeout.
Fixtures may declare `workspace_dependencies` for tools and supporting files needed to execute the scenario;
these files are copied into the isolated workspace but are not eligible evidence and are not exposed to the
judge as source artifacts.
Fixtures are read-only by default; a fixture may explicitly allow bounded source edits and generated build
paths for implementation scenarios such as TDD. Evidence locators must resolve to lines in the declared source;
approved executor changes and test logs are content-addressed and overlaid into the judge's independent
workspace. The judge receives their hashes and its own isolated copy. The runner fingerprints the canonical worktree
around executor and judge calls and hard-fails persistent writes.
Run semantic CI in an exclusive checkout: concurrent edits are deliberately treated as unsafe mutation rather
than attributed to a particular process.

The provider adapter supports direct OpenAI, direct Azure OpenAI, and Azure OpenAI behind an HTTPS Azure API
Management `*.azure-api.net` route. APIM mode mirrors Codex custom-provider semantics: bearer authentication
from `AZURE_OPENAI_API_KEY`, an explicit `api-version`, and environment-backed gateway headers. Exact Azure
DevOps variable names and the mapping from a working user-level `.codex/config.toml` are documented in
[`.azuredevops/SETUP.md`](../.azuredevops/SETUP.md).

## Golden expectations and baselines

`golden/` stores semantic facts, invariants, critical findings, and required relationships. It never stores a
full Markdown answer for string comparison. Golden files and critical thresholds are protected: changed-file
runs fail unless `--allow-protected-eval-changes` is explicit. The hard-fail mutation registry is protected by
the same gate. This flag records intent; it does not replace review of why an expectation, threshold, or hard
gate changed.

Baselines under `baselines/` store the deliberately promoted last-green run separately from Golden truth.
Comparisons emit baseline, current, delta, threshold, and status rows. Quality regressions are stricter than
performance regressions; large configured runtime or token regressions can fail, while smaller changes warn.
Lower runtime or token use never compensates for reduced correctness, completeness, or evidence grounding.
Every capability change is judged across its own behavior, dependent capabilities, and an end-to-end workflow.
The evaluation runner never promotes the baseline. Use `tools/evals/promote_baseline.py` only after an explicitly
accepted, warning-free nightly run whose report records the `main` branch. A PR run must not rewrite baseline
state. Until such a run is deliberately promoted, the bootstrap baseline reports comparison as `NOT_AVAILABLE`.

For known facts, the runner calculates recall from passed expected facts and precision from correct findings
versus explicitly reported unsupported findings. Missing a `CRITICAL` fact is a hard failure regardless of the
aggregate score. Optional executor observability includes LLM calls, input/output tokens, subagents, context
compactions, source reads, duplicate reads, dashboard renders, and external searches. Unreported values are
written as `not_available`.

## Dependency-aware execution

The selector maps changed paths to canonical IDs, follows the current catalog `related` graph as a symmetric
impact graph, includes critical transitive impacts, and adds affected archetypes, overlays, and workflows:

```bash
python3 tools/evals/select_impacted_evals.py \
  --changed-file skills/maintain-project-memory/SKILL.md
python3 tools/evals/select_impacted_evals.py --capability maintain-project-memory
```

Run selected evaluations directly from Git changes or by stable ID:

```bash
python3 tools/evals/run_evals.py --changed --base origin/main --output output/eval-results
python3 tools/evals/run_evals.py --capability analyze-legacy-system --repeat 3
python3 tools/evals/run_evals.py --workflow legacy-modernization --repeat 5
python3 tools/evals/run_evals.py --critical --profile nightly
python3 tools/evals/run_evals.py --all --compare-baseline
```

Those commands use production semantic execution whenever configuration is available; otherwise optional
semantic scenarios report a warning. A required local or CI behavioral gate uses the built-in commands with
`--require-semantic`:

```bash
python3 tools/evals/run_evals.py --changed --base origin/main --repeat 3 \
  --require-semantic --output output/eval-results
```

The production wiring smoke test is intentionally cheap:

```bash
python3 tools/evals/run_evals.py --capability inventory-codebase \
  --profile smoke --repeat 1 --require-semantic --output output/semantic-smoke
```

It exercises Codex execution, provider authentication, both JSON protocols, independent judging, and result
aggregation before the expensive full and deep profiles. Model and provider environment variables are listed
authoritatively in [`.azuredevops/README.md`](../.azuredevops/README.md).

Without `--require-semantic`, an absent executor intentionally does not claim Level-2 or Level-4 behavioral
coverage. A changed canonical capability without an evaluation contract is always a hard failure.

Deterministic checks run once even when `--repeat` is greater than one. Only external stochastic scenarios are
repeated. The explicit cost profiles are `fast`, `standard`, `full`, and `deep`. They default to one, one,
three, and five stochastic runs respectively; the legacy `pr`, `nightly`, and `weekly` names remain compatible
aliases for `fast`, `full`, and `deep`; `smoke` is the explicit low-cost alias for `fast`. `--repeat` overrides
the profile. `--kind skill`, `--kind agent`,
`--kind tool`, and `--kind workflow` support deterministic CI sharding without changing evaluation semantics.
For contracts that declare `consistency`, repeated runs enforce the configured worst-score,
variance, and pass-rate policy. Each run writes `summary.json`, `capabilities.json`, `failures.json`,
`performance.json`, `quality-summary.json`, `quality-summary.html`, and `junit.xml`. Baseline comparisons also
write `baseline-comparison.json`.

The aggregate nightly report adds an engineering summary, current-versus-last-green quality and cost metrics,
per-capability status and Git impact, explicit regression classes, developer reproduction commands, stochastic
flakiness, mutation diagnostics, and links or thumbnails for failed visual scenarios. It derives 7-day and
30-day trends from retained Azure artifacts when available; generated nightly history is not committed to Git.
Missing token, history, baseline, or visual evidence remains `not_available` rather than being estimated.

The Azure DevOps pipeline topology, secure-variable setup, baseline policy, UTC schedules, branch-policy
instructions, and local equivalents are documented in [`.azuredevops/README.md`](../.azuredevops/README.md).

Run critical methodology mutations in disposable repository copies:

```bash
python3 tools/evals/run_mutations.py --output output/eval-results/mutation-report.json
```

The mutation score is detected harmful mutations divided by mutations whose detector completed with a
`DETECTED` or `SURVIVED` result. Mutations exercise the specific behavioral/unit gate (and the RED-first
semantic contract check) in an isolated copy. A detector or setup `ERROR` is reported separately as
infrastructure, is excluded from the score and survivor list, and still fails the run. Any surviving critical
mutation fails the run as a contract regression.

Verify representative dashboard and presentation screenshots without changing the baselines:

```bash
node tools/evals/capture_visual_baselines.mjs --node-modules /path/to/node_modules \
  --report output/eval-results/visual-report.json
```

Use `--update` only for deliberate reviewed rebaselining. Verification enforces target visibility, required
content, canonical DOM grammar, overflow, browser errors, dimensions, and a bounded perceptual-difference
tolerance; exact hashes are informative rather than the sole criterion. Pass the report to `run_evals.py` with
`--visual-report` so failures become hard failures and the quality report records per-state checks.

The representative workflow contracts are `legacy-modernization`, `development-delivery`,
`research-presentation`, `dashboard-quality`, `public-sector-delivery`, and `commons-governance`.
