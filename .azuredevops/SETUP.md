# Azure DevOps setup

This is the operational setup guide for an existing Azure DevOps repository. The current release version is
stored in `VERSION`. Pipeline commands, package versions, result paths, and publication steps are already
encoded in the repository; do not create command variables or wrapper scripts.

The checked-in configuration uses Microsoft-hosted Ubuntu agents and reproduces the existing user-level Codex
provider in `~/.codex/config.toml`: Azure OpenAI is reached through Azure API Management (APIM) by both the
Codex executor and the independent judge process. Private endpoint and header values stay in Azure DevOps
variables; the repository contains only their names and validation rules. No Azure Resource Manager service
connection is referenced.

## Pipelines to create

| Recommended Azure Pipeline name | YAML path | Purpose | Trigger and schedule | Runtime profile | Semantic model access | Baseline/history access |
| --- | --- | --- | --- | --- | --- | --- |
| `Agent Commons - PR Validation` | `.azuredevops/commons-pr-validation.yml` | Static checks plus changed/impacted capability evaluation | Azure Repos branch policy for PRs targeting `main`; no push trigger or schedule | `fast`, one run | Not used; the Codex runtime is not installed and non-deterministic scenarios report warnings | Credential-free checked-in `evals/baselines/v1.0.0.json`; no Azure history access |
| `Agent Commons - Main Validation` | `.azuredevops/commons-main-validation.yml` | Critical capability, workflow, installer, and end-to-end validation | Every push to `main`; no schedule | `standard` once | Not used; the Codex runtime is not installed and non-deterministic scenarios report warnings | Reads the accepted Nightly baseline |
| `Agent Commons - Nightly Quality` | `.azuredevops/commons-nightly-quality.yml` | Full semantic portfolio, visual checks, aggregation, trends, and guarded baseline promotion | Daily at `0 1 * * *` (01:00 UTC) on `main`; no push trigger | `smoke`, then `full` three times | Required | Reads prior Nightly artifacts/history and publishes a new accepted baseline only after a warning-free PASS |
| `Agent Commons - Weekly Deep Eval` | `.azuredevops/commons-weekly-deep-eval.yml` | Deep semantic portfolio, mutation tests, visual checks, aggregation, and weekly report | Sunday at `0 2 * * 0` (02:00 UTC) on `main`; no push trigger | `smoke`, then `deep` five times | Required | Uses the Nightly definition for accepted baseline and retained quality history; never promotes |

YAML files do not create Azure Pipeline definitions automatically. Create all four definitions as described
below. All four may also be queued manually.

## 1. Create the three semantic pipelines' variable group

Go to **Azure DevOps → Pipelines → Library → + Variable group**. Name the group exactly
`agent-commons-evals`. Leave **Allow access to all pipelines** disabled.

The PR pipeline deliberately does not import this group. It is credential-free, uses the checked-in bootstrap
baseline, and must not be authorized to semantic secrets. This prevents contributor-controlled PR code from
receiving the executor or judge credentials. Keep PR validation in a separate, credential-free trust boundary;
for repositories accepting untrusted forks, also use Azure DevOps' normal fork protections and a narrowly
scoped project Build Service identity.

### Required normal configuration

| Variable | Exact value or format | Secret | Required by | Meaning and where to obtain it |
| --- | --- | --- | --- | --- |
| `EVAL_EXECUTOR_RUNTIME` | `codex` | No | Main, Nightly, Weekly | Selects the repository-owned Codex CLI adapter. |
| `EVAL_EXECUTOR_PROVIDER` | `azure_openai_apim` | No | Main, Nightly, Weekly | Makes the pinned Codex CLI use the APIM custom-provider adapter instead of direct OpenAI authentication. |
| `EVAL_EXECUTOR_MODEL` | `gpt-5.6-sol` | No | Main, Nightly, Weekly | Copy the top-level `model` value from the working user-level `.codex/config.toml`. For this APIM route it is the identifier accepted by the gateway; do not replace it with a base-model label or an Azure deployment name unless the gateway configuration is changed. |
| `EVAL_PROVIDER` | `azure_openai_apim` | No | Main, Nightly, Weekly | Selects the implemented APIM-backed Responses API judge transport. |
| `EVAL_ENDPOINT` | Copy the complete `base_url` from `[model_providers.azure]` in the working user-level `.codex/config.toml` | No | Main, Nightly, Weekly | Use the full HTTPS APIM base URL, including its existing path, but without a trailing `/responses`. The runtime appends `/responses`, requires the host to end in `.azure-api.net`, and never prints this value during `--check-config`. |
| `EVAL_APIM_ALLOWED_HOST` | The hostname portion of that `base_url`, without `https://` or any path | No | Main, Nightly, Weekly | Exact destination pin for both clients. For `https://gateway.azure-api.net/team/openai`, enter `gateway.azure-api.net`. The run fails before sending credentials if this does not exactly match `EVAL_ENDPOINT`. |
| `EVAL_API_VERSION` | `2025-04-01-preview` | No | Main, Nightly, Weekly | Copy `query_params.api-version` from `[model_providers.azure]`. The executor and judge append it as the `api-version` query parameter. |
| `EVAL_JUDGE_MODEL` | `gpt-5.6-sol` | No | Main, Nightly, Weekly | The current Codex configuration supplies one gateway model identifier, so the initial executor and judge values are the same. The judge remains a separate process with hidden expectations; use a different APIM-supported judge identifier later if one is provisioned. |
| `EVAL_APIM_CLIENT_USERNAME` | Copy the value of `http_headers.x-client-username` from `[model_providers.azure]` | No | Main, Nightly, Weekly | Client identity header required by the existing APIM policy. It is configuration rather than an authentication secret; restrict variable-group access because it is user-identifying metadata. |
| `baselinePipelineDefinitionId` | Positive numeric ID of `Agent Commons - Nightly Quality`, for example `42` | No | Main, Nightly, Weekly | Identifies the sole source of accepted baselines and retained quality history. Obtain it after creating the Nightly definition in step 3. |

There is no `qualityHistoryPipelineDefinitionId`. Nightly is the single baseline/history source, so Main,
Nightly, and Weekly all reuse `baselinePipelineDefinitionId`.

### Required secrets for the checked-in configuration

| Variable | Value source | Secret | Required by | Meaning |
| --- | --- | --- | --- | --- |
| `AZURE_OPENAI_API_KEY` | The environment variable named by `env_key` in `[model_providers.azure]`; the working config names `AZURE_OPENAI_API_KEY` | Yes; select the lock icon | Main, Nightly, Weekly | Sent as `Authorization: Bearer ...` to APIM by both repository-owned clients. Copy the value from the secure source that currently populates this environment variable; never copy it into YAML or documentation. |
| `EVAL_APIM_SUBSCRIPTION_KEY` | Copy the value of `http_headers.Ocp-Apim-Subscription-Key` from `[model_providers.azure]` | Yes; select the lock icon | Main, Nightly, Weekly | APIM subscription key sent as `Ocp-Apim-Subscription-Key`. Obtain or rotate it under Azure portal → the APIM instance → **Subscriptions**, if the workstation value is later replaced. |
| `EVAL_APIM_CLIENT_USER_KEY` | Copy the value of `http_headers.x-client-userkey` from `[model_providers.azure]` | Yes; select the lock icon | Main, Nightly, Weekly | Gateway-specific client key required by the current APIM policy. Its source of record is the existing Codex provider configuration or the APIM owner. |

### Optional configuration

Do not create these unless changing the documented defaults. Unconfigured Azure macros are treated as absent,
not as literal values.

| Variable | Default | Secret | Meaning |
| --- | --- | --- | --- |
| `EVAL_EXECUTOR_TIMEOUT_SECONDS` | `1500` | No | Maximum seconds for one Codex executor attempt. |
| `EVAL_JUDGE_TIMEOUT_SECONDS` | `180` | No | Maximum seconds for one judge HTTP request. |
| `EVAL_JUDGE_MAX_EVIDENCE_BYTES` | `500000` | No | Maximum declared fixture/artifact bytes transferred into one judge request. |
| `EVAL_API_KEY` | unset | Yes | Provider-neutral judge-key override. Do not set it when using `AZURE_OPENAI_API_KEY`. |
| `EVAL_BEARER_TOKEN` | unset | Yes | Short-lived judge bearer token. Do not store a long-lived token here. |
| `OPENAI_API_KEY` | unset | Yes | Only needed if `EVAL_EXECUTOR_PROVIDER` is deliberately changed back to direct `openai`; it is not used by the documented APIM setup. |

Do not create executable-command variables. `.azuredevops/templates/setup.yml` installs
`@openai/codex@0.150.1`; the YAML invokes the repository-owned Python entry points directly.

### Azure built-in values

Do not add these to the variable group:

| Built-in value | Actual use |
| --- | --- |
| `$(System.AccessToken)` | Mapped as `SYSTEM_ACCESSTOKEN` only in Main/Nightly/Weekly steps that read Azure build definitions and artifacts. It is not mapped in PR validation. |
| `$(System.CollectionUri)` | Current Azure DevOps organization/collection URI. |
| `$(System.TeamProjectId)` | Current Azure DevOps project ID. |
| `$(Pipeline.Workspace)` | Isolated dependency, artifact, baseline, and history workspace. |
| `$(Build.ArtifactStagingDirectory)` | Writable result and publication root. |

## 2. Create every Azure Pipeline definition

When the wizard offers **Save and run**, open its dropdown and select **Save** until the variable group,
Nightly ID, and permissions are ready.

### Agent Commons - PR Validation

1. Go to **Azure DevOps → Pipelines → Pipelines → New pipeline**.
2. Select **Azure Repos Git**.
3. Select the repository containing Agent Commons.
4. Select **Existing Azure Pipelines YAML file**.
5. Set **Branch** to `main`.
6. Set **Path** to `.azuredevops/commons-pr-validation.yml`.
7. Select **Continue**, then **Save**.
8. Open **More actions → Rename/move** and name it exactly `Agent Commons - PR Validation`.

Do not authorize this definition to `agent-commons-evals` or any service connection.

### Agent Commons - Main Validation

Repeat **Pipelines → New pipeline → Azure Repos Git → repository → Existing Azure Pipelines YAML file**,
select branch `main`, select `.azuredevops/commons-main-validation.yml`, save, and rename it exactly
`Agent Commons - Main Validation`.

Open **Edit → More actions → Triggers → YAML** and clear **Override the YAML continuous integration trigger
from here**. Then open **More actions → Settings** and confirm **Processing of new run requests** is
**Enabled**. The checked-in YAML owns this definition's CI trigger and batches updates to
`refs/heads/main`; a UI override or paused queue prevents pushes from creating runs.

### Agent Commons - Nightly Quality

Repeat the same flow with `.azuredevops/commons-nightly-quality.yml`, then rename it exactly
`Agent Commons - Nightly Quality`.

### Agent Commons - Weekly Deep Eval

Repeat the same flow with `.azuredevops/commons-weekly-deep-eval.yml`, then rename it exactly
`Agent Commons - Weekly Deep Eval`.

## 3. Record the Nightly pipeline definition ID

Open **Pipelines → Agent Commons - Nightly Quality**. The browser URL contains a query value such as
`definitionId=42`; copy only the positive integer. Then go to
**Pipelines → Library → agent-commons-evals**, add `baselinePipelineDefinitionId`, leave its lock icon open,
and save.

Azure CLI alternative, after setting the CLI organization and project defaults:

```bash
az pipelines list \
  --name "Agent Commons - Nightly Quality" \
  --query "[0].id" \
  --output tsv
```

The smoke stage verifies that this ID resolves specifically to
`.azuredevops/commons-nightly-quality.yml`. Main or Weekly IDs fail before expensive evaluation starts.

Baseline discovery requires no tag and no second ID. The resolver scans recent successful Nightly builds on
`main` and uses the newest one containing the `last-green-baseline` artifact. Until such an artifact exists, it
uses `evals/baselines/v1.0.0.json`. Retained reports are read from the same definition's `quality-aggregate`
artifacts.

## 4. Authorize only the three secret-consuming pipelines

Go to **Pipelines → Library → agent-commons-evals → Pipeline permissions → +** and add:

- `Agent Commons - Main Validation`
- `Agent Commons - Nightly Quality`
- `Agent Commons - Weekly Deep Eval`

Do not add `Agent Commons - PR Validation`, and do not enable open access. If a first run pauses with
**This pipeline needs permission to access a resource**, verify the named resource is `agent-commons-evals`
and the requesting pipeline is one of the three above, then select **Permit**. Permit each intended definition
individually.

On the same variable-group page, open **Security**. Keep the variable group's **Administrator** role limited to
trusted secret administrators; ordinary pipeline users should not be able to edit both `EVAL_ENDPOINT` and
`EVAL_APIM_ALLOWED_HOST`. Pipeline authorization grants use of the group, not permission to administer it.

## 5. Enable System.AccessToken and least-privilege build access

Do not create a variable named `SYSTEM_ACCESSTOKEN`. The checked-in YAML performs the required mapping:

```yaml
env:
  SYSTEM_ACCESSTOKEN: $(System.AccessToken)
```

That mapping exists only on Main/Nightly/Weekly Azure REST and artifact-read steps. No pipeline pushes Git
changes, so `checkout: self` does not use `persistCredentials: true`.

For YAML pipelines, the job access token is created by Azure DevOps and becomes available through the explicit
environment mapping above. The classic build checkbox **Allow scripts to access the OAuth token** is not a
separate setup step for this implementation.

Keep tokens project-scoped:

1. Go to **Project settings → Pipelines → Settings**.
2. Turn on **Limit job authorization scope to current project for non-release pipelines**.
3. Turn on **Limit variables that can be set at queue time** so a person who can only queue a run cannot replace
   `EVAL_ENDPOINT` or its exact-host pin.
4. Keep the Nightly definition and all consumers in this same Azure DevOps project.

Grant the project-scoped identity `Project Name Build Service (Organization Name)` only the reads it needs:

1. Go to **Pipelines → Pipelines → More actions → Manage security**.
2. Search for `Project Name Build Service (Organization Name)`.
3. Set **View build pipeline** to **Allow**.
4. Set **View builds** to **Allow**.
5. Leave edit, queue-management, delete, retention, and administrative permissions unset.

`View builds` covers reading published pipeline artifacts; there is no separate permission needed to add a
baseline tag because this implementation does not add build tags. If the organization intentionally uses a
collection-scoped job token, configure the corresponding
`Project Collection Build Service (Organization Name)` identity instead, but project scope is recommended.

## 6. Semantic evaluator setup

The existing user-level `~/.codex/config.toml` is the source configuration. Do not commit it. Under its active
`[model_providers.azure]` table it already defines the APIM `base_url`, `env_key`, `api-version`, and the three
required header names. Azure DevOps cannot read that workstation file, so copy the values once into
`agent-commons-evals` using the mapping above.

1. **Execution:** `@openai/codex@0.150.1` receives an ephemeral custom provider named `azure_apim`. The runtime
   supplies the APIM URL, API version, bearer-key environment variable, and environment-backed HTTP headers.
2. **Judging:** `tools/evals/semantic_judge.py` independently calls the same APIM Responses endpoint after the
   executor finishes. It receives hidden expectations that are never exposed to the executor.
3. **Model identifiers:** set both model variables to `gpt-5.6-sol`, the exact identifier in the working Codex
   config. This is not inferred from an Azure base-model name. If APIM later exposes a separate judge route,
   change only `EVAL_JUDGE_MODEL` to that accepted gateway identifier.
4. **Azure resource:** the pipeline needs the existing APIM gateway and its already configured Azure OpenAI
   backend. It does not need direct access to the backend resource endpoint.
5. **Authentication:** `AZURE_OPENAI_API_KEY` becomes a bearer token; APIM also requires
   `Ocp-Apim-Subscription-Key`, `x-client-userkey`, and `x-client-username`.
6. **Redirects:** configure this APIM operation to return the model response directly, not an HTTP 3xx redirect.
   The Python judge strips credentials on cross-origin redirects, but redirect behavior inside the external
   Codex CLI is not controlled by repository code.

To enter the authentication values, go to **Azure DevOps → Pipelines → Library → agent-commons-evals → +
Add**, add the exact variables in the two tables above, lock the three credential variables, and save. Never
paste a credential into a pipeline variable override at queue time because it may not receive secret masking.

The YAML does not use `AzureCLI@2`, managed identity, or an Azure Resource Manager service connection. Do not
create a service connection for this implementation. The Azure DevOps Build Service therefore needs no RBAC
role on the Azure OpenAI backend; APIM and its backend identity or policy own that authorization. A direct Azure
identity flow would be a different provider configuration and is not supported by this APIM path.

## 7. Agent pool and dependency requirements

Every job specifies `vmImage: ubuntu-24.04`; Microsoft-hosted agents are supported and recommended. Nightly
and Weekly run independent jobs in parallel, so the Azure DevOps organization needs enough parallel-job
capacity or the jobs will wait in the queue.

Handled automatically by YAML:

- repository checkout and full Git history;
- Python 3.11 through `UsePythonVersion@0`;
- Ubuntu's distro `bubblewrap` and `bwrap-userns-restrict` AppArmor profile for Codex sandboxing;
- Node.js 22.14.0 where semantic/browser execution needs it;
- Codex CLI 0.150.1 in `$(Pipeline.Workspace)`;
- Playwright 1.55.0, Chromium, and Linux browser dependencies for visual jobs;
- isolated result directories, JUnit publication, pipeline artifacts, and Azure summary upload.

You must provide externally:

- Microsoft-hosted parallel-job capacity;
- outbound HTTPS access to the APIM hostname copied from the working Codex config;
- the existing APIM/Azure OpenAI route and enough model quota for `gpt-5.6-sol`;
- `AZURE_OPENAI_API_KEY` plus the three required APIM header values from the working Codex config;
- the variable-group authorizations for Main, Nightly, and Weekly;
- the Nightly definition ID and Build Service read permissions.

Docker and a self-hosted agent are not required. If policy requires self-hosting, use Linux with Git, Python
3.11, Node.js 22, npm, Chromium dependencies, and outbound HTTPS to APIM, Azure DevOps, and
Azure artifact storage. Register it with the Azure Pipelines Agent in a dedicated pool, change each YAML
`pool` deliberately, use an ephemeral or cleaned workspace per job, and never reuse a persistent Codex login
for PR jobs.

## 8. Schedules and branch behavior

| Pipeline | Branch | Actual YAML trigger/schedule | Vienna local time |
| --- | --- | --- | --- |
| PR Validation | PR source branch targeting `main` | `trigger: none`; Azure Repos branch policy queues it | N/A |
| Main Validation | `main` | Push trigger for `main` | Every accepted push |
| Nightly Quality | `main` | `0 1 * * *` daily at 01:00 UTC | 03:00 CEST / 02:00 CET |
| Weekly Deep Eval | `main` | `0 2 * * 0` Sunday at 02:00 UTC | 04:00 CEST / 03:00 CET |

Azure YAML schedules stay in UTC and do not move with daylight-saving time, so Vienna wall-clock time changes
between CET and CEST. Both schedules use `always: true`. Do not create a UI schedule; a UI-defined schedule
overrides YAML schedules.

For `Agent Commons - Main Validation`, keep **Override the YAML continuous integration trigger from here**
cleared. The project-level **Disable implied YAML CI trigger** setting does not disable this pipeline because
the YAML declares an explicit trigger, but a pipeline-level UI override still takes precedence. Keep
**Processing of new run requests** enabled for all four definitions.

## 9. Configure the `main` PR branch policy

Azure Repos Git requires build validation policy configuration; the YAML file alone does not enforce PRs.
After the PR definition has completed successfully once:

1. Go to **Repos → Branches**.
2. Find `main`, open **More options → Branch policies**.
3. Under **Build validation**, select **+**.
4. Select `Agent Commons - PR Validation`.
5. Leave **Path filter** empty so canonical assets, adapters, evals, pipelines, and docs are covered.
6. Set **Trigger** to **Automatic**.
7. Set **Policy requirement** to **Required**.
8. Set build expiration to **Immediately when main is updated**.
9. Set display name to `Agent Commons PR validation` and save.

Do not add Main Validation as another PR policy. Main is deliberately more expensive and consumes secrets only
after changes merge to `main`.

## 10. Verify configuration and run the cheap smoke

The local no-model-call configuration check is:

```bash
python3 tools/evals/run_evals.py --check-config --output output/config-check
```

It prints no secret values and reports:

- local or Azure environment;
- repository runner availability;
- Codex executor and executable;
- judge/provider availability;
- executor model ID and judge deployment name;
- executor and judge authentication type;
- configured model-identifier relationship;
- baseline definition/history configuration;
- writable result directory.

In Azure, missing `baselinePipelineDefinitionId` is an error. Locally, absence of Azure pipeline context reports
the checked-in bootstrap baseline and current-run-only history.

The cheap local semantic smoke is:

```bash
python3 tools/evals/run_evals.py \
  --profile smoke \
  --capability inventory-codebase \
  --repeat 1 \
  --require-semantic \
  --compare-baseline evals/baselines/v1.0.0.json \
  --output output/eval-smoke
```

`smoke` aliases the FAST thresholds and makes one small executor call and one judge call. The Azure
`SemanticSmoke` stage additionally validates that the configured definition is the Nightly YAML, verifies
read access to completed Nightly builds, resolves an accepted baseline artifact or cleanly uses the bootstrap,
and publishes `quality-semantic-smoke` with JUnit and quality reports.

For a read-only Azure setup check from an agent/job that has the built-in token mapped, run:

```bash
SYSTEM_ACCESSTOKEN="$SYSTEM_ACCESSTOKEN" python3 tools/evals/verify_azure_pipeline_access.py \
  --collection-uri "$SYSTEM_COLLECTIONURI" \
  --project "$SYSTEM_TEAMPROJECTID" \
  --definition "$BASELINE_PIPELINE_DEFINITION_ID" \
  --expected-yaml-path .azuredevops/commons-nightly-quality.yml \
  --output output/azure-pipeline-access.json
```

This helper performs read-only definition/history calls. It never changes permissions, definitions, tags, or
variable groups and never writes the token to its report.

## 11. First activation sequence

1. Create `agent-commons-evals` with the APIM values copied from the working user-level `.codex/config.toml`:
   the nine required non-secret values except the not-yet-known Nightly ID, plus the three locked secrets.
2. Create all four pipeline definitions without running them.
3. Copy the Nightly definition ID into non-secret `baselinePipelineDefinitionId`.
4. Authorize only Main, Nightly, and Weekly to the variable group.
5. Grant the project Build Service **View build pipeline** and **View builds**.
6. Queue `Agent Commons - PR Validation` on a feature branch or open a test PR targeting `main`.
   Expected: Static, Impact, and TargetedBehavior are green without secret-resource authorization.
7. Queue `Agent Commons - Main Validation` on `main`.
   Expected: `SemanticSmoke` is green, `quality-semantic-smoke` is published, and Integration is green.
8. Queue `Agent Commons - Nightly Quality` manually on `main`.
   Expected: all FullQuality jobs are green, `quality-aggregate` is published, and a warning-free PASS publishes
   `last-green-baseline`.
9. Queue Nightly a second time. Expected: baseline logs report source `accepted-nightly`, proving the first
   run's artifact replaced bootstrap fallback for comparison.
10. Queue `Agent Commons - Weekly Deep Eval` manually on `main`.
    Expected: semantic, mutation, visual, and deep shards are green and `weekly-quality-report.html` exists in
    `quality-aggregate`.
11. Add the required PR branch policy.
12. Open each scheduled definition's **More actions → Scheduled runs** and confirm the next UTC run.

## 12. Manual runs and local equivalents

To run a pipeline manually, go to **Pipelines → Pipelines**, select its exact name, select **Run pipeline**,
choose the branch, and select **Run**.

### PR Validation

Use a feature branch with at least one change relative to `origin/main`; a real PR is the authoritative test.

```bash
git fetch origin main --no-tags
python3 tools/evals/run_evals.py --changed --base origin/main --profile fast --repeat 1 \
  --compare-baseline evals/baselines/v1.0.0.json --output output/eval-pr
```

### Main Validation

```bash
python3 tools/evals/run_evals.py --critical --profile standard --repeat 1 --require-semantic \
  --compare-baseline evals/baselines/v1.0.0.json --output output/eval-main
```

### Nightly Quality

```bash
python3 tools/evals/run_evals.py --all --profile full --repeat 3 --require-semantic \
  --compare-baseline evals/baselines/v1.0.0.json --output output/eval-nightly
```

Azure additionally runs visual capture, isolated shard aggregation, retained-history download, and guarded
baseline publication.

### Weekly Deep Eval

```bash
python3 tools/evals/run_mutations.py --output output/eval-weekly/mutation-report.json
python3 tools/evals/run_evals.py --all --profile deep --repeat 5 --require-semantic \
  --mutation-report output/eval-weekly/mutation-report.json \
  --compare-baseline evals/baselines/v1.0.0.json --output output/eval-weekly
```

Azure additionally runs visual capture, Nightly history download, aggregation, and weekly HTML generation.

## 13. What success looks like

| Pipeline | Green stages | Published evidence |
| --- | --- | --- |
| PR Validation | `Static`, `Impact`, `TargetedBehavior` | `impact-selection`, `quality-targeted`, JUnit under **Tests**, quality HTML/JSON, performance/failure reports, runner log |
| Main Validation | `Static`, `SemanticSmoke`, `Integration` | `quality-semantic-smoke`, seven bounded `quality-critical-*` shard artifacts, JUnit and Azure summaries |
| Nightly Quality | `Static`, `SemanticSmoke`, `FullQuality`, `Aggregate` | `quality-semantic-smoke`, `quality-skills`, `quality-agents`, `quality-workflows`, `quality-visual`, `quality-aggregate`, and on eligible PASS `last-green-baseline` |
| Weekly Deep Eval | `Static`, `SemanticSmoke`, `DeepQuality`, `Aggregate` | Nightly-style evidence plus `quality-mutation`; `quality-aggregate/weekly-quality-report.html` |

Quality artifacts contain `quality-summary.html`, `quality-summary.json`, `summary.json`, `capabilities.json`,
`performance.json`, `failures.json`, `junit.xml`, and `runner.log` where applicable. Visual output includes
screenshots, a visual report, and logs.

Fully configured success means the Azure run is **Succeeded**, overall quality is `PASS`, semantic smoke shows
both executor and judge healthy, `azure-pipeline-access.json` reports the expected Nightly YAML and readable
history, and baseline resolution reports either `bootstrap` on the first run or `accepted-nightly` thereafter.
Warnings are allowed only where policy says so; any warning prevents Nightly baseline publication.

## 14. Troubleshooting

| Symptom | Likely cause | Actual fix |
| --- | --- | --- |
| Pipeline cannot access variable group | Main, Nightly, or Weekly was not authorized | Go to **Pipelines → Library → agent-commons-evals → Pipeline permissions → +** and add only the failing trusted definition, or select **Permit** on its paused run. PR should not have access. |
| `System.AccessToken` returns 401/403 | Wrong Build Service identity, cross-project scope, or missing read permission | Keep the Nightly definition in the same project. Under **Pipelines → More actions → Manage security**, grant the project Build Service **View build pipeline** and **View builds**. Do not create a replacement secret token. |
| Baseline not found | No eligible Nightly artifact yet or the definition ID is wrong | Inspect `azure-pipeline-access.json`. A correct first run uses bootstrap. Run Nightly to a warning-free PASS, then rerun; source should become `accepted-nightly`. If the YAML path check fails, replace `baselinePipelineDefinitionId` with the Nightly definition ID. |
| Semantic executor unavailable | Codex install failed or one APIM variable is missing | Inspect **Install pinned Codex semantic runtime**. Verify `EVAL_EXECUTOR_RUNTIME=codex`, `EVAL_EXECUTOR_PROVIDER=azure_openai_apim`, model `gpt-5.6-sol`, and every APIM variable, then rerun `--check-config`. |
| Codex fails with `bwrap: loopback: Failed RTM_NEWADDR` | Ubuntu 24.04 AppArmor blocks the user namespace needed by the Codex sandbox | Inspect **Configure Codex Linux sandbox**. It installs the distro `bubblewrap`, copies `bwrap-userns-restrict` from `apparmor-profiles`, loads it with `apparmor_parser`, and runs a restricted-network preflight without disabling AppArmor's global user-namespace restriction. |
| Judge fails JSON parsing | The APIM-routed model did not satisfy the structured judge protocol | Confirm `EVAL_JUDGE_MODEL=gpt-5.6-sol` is accepted by the gateway and the route supports Responses structured JSON. Inspect `runner.log` for `PROTOCOL_FAILURE`; do not replace the judge with a shell command. |
| Azure OpenAI/APIM 401 or 403 | Bearer key or one gateway header is missing, expired, or mismatched | Recopy `AZURE_OPENAI_API_KEY`, `Ocp-Apim-Subscription-Key`, `x-client-userkey`, and `x-client-username` from the working config or secret source. Verify the variable group is authorized to this pipeline. |
| Azure OpenAI 429 | APIM or backend model quota is exhausted | Check APIM diagnostics and the backing deployment quota/TPM, reduce concurrent semantic work or increase quota, then rerun. Retries are bounded. |
| APIM endpoint is rejected before a request | Endpoint is HTTP, includes user information or a custom port, or is not an Azure APIM hostname | Copy the complete `base_url` from `[model_providers.azure]` in the working user-level `.codex/config.toml`. It must use HTTPS on the default port and end in `.azure-api.net`; do not append `/responses`. |
| APIM host pin mismatch | `EVAL_APIM_ALLOWED_HOST` does not exactly match the hostname in `EVAL_ENDPOINT` | Copy only the hostname from the configured `base_url`, without scheme, path, slash, or port. Do not weaken the check to another `*.azure-api.net` tenant. |
| Playwright fails | Chromium/Linux dependencies were not installed or a stale cache is corrupt | Inspect **Install pinned Chromium runtime**. On hosted agents rerun after clearing the `agent-commons-browser` cache; on self-hosted Linux run the same Playwright `install --with-deps chromium` command. |
| Pipeline succeeds but no JUnit appears | `junit.xml` is missing at the publication path or publication was skipped | Open the quality artifact and confirm `junit.xml`. Inspect **Publish JUnit quality results**; it reads `${outputDir}/junit.xml` under `condition: always()`. |
| Push to `main` creates no Main Validation run | The push contained no new commit, the definition is paused, or a pipeline-level UI setting overrides the YAML CI trigger | Confirm the commit is new on `main`, open **Agent Commons - Main Validation → Edit → More actions → Triggers → YAML**, clear **Override the YAML continuous integration trigger from here**, and confirm **Processing of new run requests** is **Enabled** under pipeline settings. |
| Scheduled run does not appear | A UI schedule overrides YAML or the schedule was not loaded from `main` | Remove UI schedules under **Edit → Triggers**, save the YAML on `main`, then inspect **More actions → Scheduled runs**. |
| Smoke reports the wrong YAML path | The configured definition ID points to Main, Weekly, or another definition | Retrieve the ID from `Agent Commons - Nightly Quality`, update the non-secret variable-group value, and rerun. |

## Official reference points

- [Create and manage variable groups](https://learn.microsoft.com/en-us/azure/devops/pipelines/library/variable-groups?view=azure-devops)
- [Use `System.AccessToken` in YAML](https://learn.microsoft.com/en-us/azure/devops/pipelines/build/variables?view=azure-devops#systemaccesstoken)
- [Codex sandbox prerequisites](https://learn.chatgpt.com/docs/sandboxing#prerequisites)
- [Job authorization scope and Build Service identities](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/access-tokens?view=azure-devops)
- [Pipeline permissions](https://learn.microsoft.com/en-us/azure/devops/pipelines/policies/permissions?view=azure-devops)
- [Build validation branch policies](https://learn.microsoft.com/en-us/azure/devops/repos/git/branch-policies?view=azure-devops#set-build-validation)
- [UTC scheduled triggers](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/scheduled-triggers?view=azure-devops)
- [Azure OpenAI resource/deployment setup](https://learn.microsoft.com/en-us/azure/foundry-classic/openai/how-to/create-resource)
- [Azure OpenAI endpoint and deployment-name semantics](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/switching-endpoints)
- [Codex custom provider configuration](https://learn.chatgpt.com/docs/config-file/config-reference#configtoml)

## What you need to configure

1. Create variable group `agent-commons-evals`; keep **Allow access to all pipelines** off.
2. Add non-secret `EVAL_EXECUTOR_RUNTIME=codex`, `EVAL_EXECUTOR_PROVIDER=azure_openai_apim`, and
   `EVAL_PROVIDER=azure_openai_apim`.
3. Add non-secret `EVAL_EXECUTOR_MODEL=gpt-5.6-sol`, `EVAL_JUDGE_MODEL=gpt-5.6-sol`, and
   `EVAL_API_VERSION=2025-04-01-preview`.
4. Copy the complete private `base_url` from `[model_providers.azure]` in the working user-level
   `.codex/config.toml` into non-secret `EVAL_ENDPOINT`; do not add `/responses`.
5. Put only that URL's hostname into non-secret `EVAL_APIM_ALLOWED_HOST`, and enable **Limit variables that can
   be set at queue time** under **Project settings → Pipelines → Settings**.
6. Copy `http_headers.x-client-username` into non-secret `EVAL_APIM_CLIENT_USERNAME`.
7. Add locked `AZURE_OPENAI_API_KEY` from the environment variable named by `env_key`, locked
   `EVAL_APIM_SUBSCRIPTION_KEY` from `http_headers.Ocp-Apim-Subscription-Key`, and locked
   `EVAL_APIM_CLIENT_USER_KEY` from `http_headers.x-client-userkey`.
8. Create the four definitions with the exact names and YAML paths in the first table.
9. Copy the numeric Nightly `definitionId` into non-secret `baselinePipelineDefinitionId`.
10. Authorize only Main, Nightly, and Weekly to `agent-commons-evals`; never authorize PR Validation.
11. Grant the project Build Service **View build pipeline** and **View builds** only.
12. Run PR Validation, Main Validation/`SemanticSmoke`, Nightly twice, then Weekly.
13. Confirm `quality-aggregate` and `last-green-baseline` are published and the second Nightly resolves source
    `accepted-nightly`.
14. Make `Agent Commons - PR Validation` an Automatic, Required build validation policy on `main`.
