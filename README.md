# Agent Commons

Version: **1.3.0**

Agent Commons is a reusable engineering operating system for AI-assisted delivery. It combines
runtime-neutral methodology, bounded specialist agents, deterministic tools, reusable templates,
composable project profiles, evaluation suites, and thin runtime adapters.

The repository is the canonical source. Projects consume selected capabilities without copying the
library or maintaining runtime-specific versions of the same workflow.

## Architecture

```text
Canonical capability layer
├── skills/       bounded workflows and supporting resources
├── agents/       independently delegated specialist responsibilities
├── tools/        deterministic generation, validation, and reconciliation
├── templates/    reusable structure without embedded judgment
├── archetypes/   project-family composition profiles
├── adapters/     runtime-specific discovery and rendering
├── evals/        behavioral and deterministic regression coverage
└── catalog/      stable IDs, relationships, and routing metadata
```

The core distinction is deliberate:

- A **skill** defines how bounded work is done.
- An **agent** owns an independent delegated perspective or responsibility.
- A **tool** performs deterministic work.
- A **template** supplies reusable structure.
- An **archetype** composes capabilities for a project family.
- An **overlay** adds a cross-cutting concern such as traceability, localization, or dashboards.
- An **adapter** maps canonical capability into a runtime's actual model.

Stable capability IDs live in [`catalog/capabilities.yaml`](catalog/capabilities.yaml). Composition
manifests reference those IDs; runtime adapters never duplicate canonical workflow bodies.

## Core workflow

```text
initialize-project
        ↓
analyze / research / specify
        ↓
approved OpenSpec change
        ↓
test-driven implementation
        ↓
targeted mutation testing and test hardening
        ↓
independent verification
        ↓
complete and archive
```

`continue-project` inspects current project state and selects the next safe lifecycle step when the user
does not already name one.

For substantial development, the default methodology is:

```text
requirements → OpenSpec → RED → GREEN → REFACTOR → tests pass
             → targeted mutation → test hardening → verification
```

Legacy modernization adds an inventory-backed evidence lifecycle before requirements and specification.

### Test quality is not test execution

Three questions are kept distinct, and none substitutes for another:

| Practice | Question it answers |
| --- | --- |
| Code coverage | Was this code executed by tests? |
| Test-driven development | Did we specify the behavior through tests before implementing it? |
| Mutation testing | Would those tests fail if the implementation were wrong? |

Full coverage does not imply test quality, and a green suite does not imply defect detection. Where the
technology has maintained mutation tooling, `test-driven-development` delegates to `mutation-testing` after
GREEN and REFACTOR, which scopes mutation to changed critical code, classifies every surviving mutant against
the approved specification, and drives behavioral test hardening. A critical surviving mutant fails validation
regardless of the aggregate score, mutation score is never the only gate, and a technology with no maintained
engine is reported as `NOT_SUPPORTED` rather than passed. Continuous integration profiles are targeted
mutation on pull requests, broader mutation nightly, and optional deep analysis weekly.

Application mutation testing is separate from the Agent Commons methodology mutation testing under
`evals/mutations/`, which mutates canonical skills to prove the Commons evaluations detect degraded agent
behavior. The two share vocabulary and nothing else; their results are never aggregated.

## Project memory and deep analysis

Agent Commons externalizes verified project knowledge so agents can resume complex work without repeatedly
reloading the complete repository or conversation. Standard substantial projects use lazy, project-local
`.agent-commons/memory/` with a tiny L0 synopsis, domain L1 indexes, entity/component L2 records, and evidence
pointers. Canonical source, analysis, requirements, specifications, code, and tests remain authoritative.

Memory optimizes retrieval, not reasoning depth. Full legacy analysis is deep by default: specialists analyze
important behavior once, preserve rules, data, dependencies, interfaces, complexity, defects, unknowns, and
cross-language differences as structured evidence, then later workflows retrieve only what they need.

When a separate reference application is configured, legacy analysis treats it as a fingerprinted discovery
prior and records target matches and non-matches without promoting reference observations into target truth.
Legacy-derived test strategies also keep approved intent, observed source behavior, and unresolved outcomes
separate so generated scenarios cannot silently become executable assertions.

```text
source -> deep specialist analysis -> structured evidence -> project memory -> selective retrieval
       -> requirements / specifications / implementation / dashboards / presentations
```

## Installation

The installer supports managed user-level installation, status, verification, repair, and removal.

macOS or Linux:

```bash
python3 install/agent_commons.py install
python3 install/agent_commons.py status
python3 install/agent_commons.py doctor
python3 install/agent_commons.py verify
```

Windows PowerShell:

```powershell
py install\agent_commons.py install
py install\agent_commons.py status
py install\agent_commons.py doctor
py install\agent_commons.py verify
```

Codex is the default runtime. Select one runtime explicitly or install every supported adapter:

```bash
python3 install/agent_commons.py install claude-code --install-mode auto
python3 install/agent_commons.py install --all --install-mode auto
```

Use `--dry-run` where supported to inspect planned changes. The installer owns only its managed entries and
does not overwrite unrelated user content. See [`install/README.md`](install/README.md) for destinations,
manual installation, lifecycle commands, and platform behavior.

## Start a project

Create or open a workspace, start the selected runtime, and invoke `initialize-project` through its native
skill mechanism.

| Runtime | Typical invocation |
|---|---|
| Codex | mention `$initialize-project` or select it through `/skills` |
| Claude Code | `/initialize-project` |
| Cline | `/initialize-project` |
| OpenCode | ask it to use the `initialize-project` skill |

The initializer inspects the workspace, consumes facts already present in the request, asks only for
material unresolved choices, previews the plan, and creates the smallest useful scaffold. Existing files
are not overwritten.

For standard projects it evaluates Commons capability coverage immediately. Important partial or missing
coverage starts privacy-safe external discovery against configured GitHub sources as an independent branch;
core setup and the next lifecycle action do not wait for network completion. Discovery state and candidates
remain visible, and no candidate is installed or activated without review and explicit acceptance.

Example:

```text
Initialize a legacy modernization project.
Source: ../legacy-system, read-only.
Target: Java.
Extract requirements, prepare OpenSpec changes, and create a living analysis dashboard.
```

The generated project records its composition in `.agent-commons.yaml` and keeps shared instructions in
`AGENTS.md`. Standard projects also record lazy project memory; tiny projects do not create memory machinery
unless explicitly selected. Runtime-specific project files are thin adapters only.

## Continue a project

Use:

```text
$continue-project
```

or name a specific requirement, specification, dashboard object, or safe project-local path. The workflow
resolves dependencies and approvals without bypassing project constraints.

Common direct routes include:

- `analyze-legacy-system` for complete configured legacy analysis;
- `analyze-legacy-system only <scope>` for an explicitly bounded slice;
- `specify-openspec-change` and `review-openspec-change` before implementation;
- `implement-ready-slice` or `implement-openspec-change` for approved behavior;
- `verify-openspec-implementation` and `complete-openspec-change` for closure;
- `deep-research` for structured research;
- `build-living-dashboard` for a deterministic read-only project view.

## Project composition

The current archetypes are:

- `development`
- `legacy-migration`
- `research`
- `presentation`

Cross-cutting overlays cover architecture documentation, branded HTML, bilingual delivery, durable state,
evidence traceability, living dashboards, public-sector delivery, and sales storytelling.

Hybrid projects select multiple archetypes and overlays directly. The resolver deduplicates capability IDs
and rejects unknown references:

```bash
python3 tools/resolve_archetypes.py resolve \
  --archetype legacy-migration,development \
  --overlay evidence-traceability,living-dashboard
```

See [`archetypes/README.md`](archetypes/README.md) for the composition contract.

## Runtime support

Agent Commons currently supports:

- Codex
- Claude Code
- Cline
- OpenCode

Canonical methodology remains runtime-neutral. Adapter manifests document actual discovery paths,
precedence, native support, mapped behavior, and limitations. Unsupported parity is reported rather than
simulated. See [`adapters/README.md`](adapters/README.md).

## Deterministic projections

Agent Commons keeps generated views synchronized with canonical state:

- `catalog/capability-index.json` is generated from capability metadata.
- `presentation/assets/library-data.js` is generated from catalogs, composition, adapters, evals, and
  current external registry metadata.
- `presentation/agent-commons.html` is the generated single-file, offline presentation for portable delivery.
- Living dashboards are generated from project-owned canonical data.

Living technical dashboards use one canonical grouped information architecture. Management, composition,
complexity, ADM estimation, roadmap, inventory, architecture, persistence/ERD, integrations, flows,
requirements/OpenSpec, traceability, test quality, maintainability, target architecture, risks, questions,
and evidence retain stable locations. Missing content is shown as pending, not applicable, or blocked rather
than silently removing the domain.

Refresh the library presentation with:

```bash
python3 tools/refresh_commons_presentation.py
python3 tools/refresh_commons_presentation.py --check
python3 tools/check_presentation_visual_contract.py
```

Open [`presentation/index.html`](presentation/index.html) directly in a current browser.

## Governance

Project-specific behavior remains in its project. Reusable improvements enter Agent Commons only through
an explicit review and promotion path:

### Git commits

Use short, meaningful human-readable subjects. Do not use Conventional Commit prefixes. Prefix a reliably
detected task ticket as `[TICKET-ID]`, never invent a ticket from an ambiguous number, and do not add
`Co-authored-by` or agent-attribution trailers.

```text
project evidence → review-for-commons → explicit selection → promote-to-commons
```

External discovery is proposal-only:

```text
search → revision-pinned review → license/security/overlap checks → explicit selection → promotion
```

Unknown licensing blocks copying or adaptation. Legally required third-party attribution must be retained
in a current notice mechanism. Confidential data, private paths, client identities, raw logs, and source
project history never belong in canonical capabilities.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for contribution rules.

## Validation

Run the complete deterministic repository gate with Python 3.11 or newer before release:

```bash
python3 tools/evals/run_evals.py --all --output output/eval-results
python3 tools/runtime_adapters.py validate
python3 tools/resolve_archetypes.py validate
python3 tools/resolve_capability_gaps.py validate
python3 tools/external_capabilities.py validate
python3 tools/refresh_commons_presentation.py --check
python3 tools/validate_commons.py
python3 -m unittest \
  evals.installation.test_installer \
  evals.initialization.test_initializer \
  evals.initialization.test_natural_language_briefs \
  evals.initialization.test_public_sector_delivery \
  evals.archetypes.test_archetypes \
  evals.tools.test_adm_estimate \
  evals.tools.test_analysis_coordinator \
  evals.tools.test_anonymize_data \
  evals.tools.test_brand_fidelity_contract \
  evals.tools.test_brand_validation \
  evals.tools.test_capability_index \
  evals.tools.test_completeness_promotion \
  evals.tools.test_commit_policy \
  evals.tools.test_dashboard \
  evals.tools.test_dashboard_visual \
  evals.tools.test_diagram_model \
  evals.tools.test_legacy_structure_extractor \
  evals.tools.test_legacy_evidence_boundaries \
  evals.tools.test_localization \
  evals.tools.test_migration_manifest \
  evals.tools.test_parallel_execution_plan \
  evals.tools.test_presentation_maintenance_contract \
  evals.tools.test_presentation_visual_contract \
  evals.tools.test_presentation_sync \
  evals.tools.test_project_continuation \
  evals.tools.test_project_memory \
  evals.tools.test_project_memory_benchmark \
  evals.tools.test_promote_to_commons \
  evals.tools.test_public_baseline \
  evals.tools.test_trace_graph_audit \
  evals.tools.test_validate_commons \
  evals.evaluation.test_eval_contracts \
  evals.evaluation.test_impact_selector \
  evals.evaluation.test_eval_runner \
  evals.external.test_external_capabilities
```

For pull requests, `python3 tools/evals/run_evals.py --changed --base origin/main` selects changed
capabilities, their related direct and critical transitive impacts, and representative workflows. It reports
unavailable external semantic execution as a warning. The required behavioral CI job must also supply separate
executor and judge commands and pass `--require-semantic`; otherwise Level-2 and Level-4 coverage is not
claimed. See
[`evals/README.md`](evals/README.md) for severity, semantic judging, golden protection, repeats, baselines,
and Azure DevOps result files.

Visual artifacts require static validation plus real-browser inspection. Passing unit tests alone is not
browser, accessibility, or live runtime-discovery evidence.

## Release

The public release label is **v1.3.0**. The canonical semantic version is stored in [`VERSION`](VERSION).
