# Agent Commons company presentation — demo runbook

The demo uses one Apache-2.0 IBM z/OS Connect Redbook sample and four prepared snapshots of the same 77-file source tree. The live commands are genuine, but the presentation never waits for them to finish.

## Demo identity

- Demo ID: `ibm-zos-connect-redbook-modernization`
- Source: IBM z/OS Connect OpenAPI 3 API requester Redbook sample
- License: Apache-2.0, retained in `client_input/LICENSE`
- Source composition: COBOL, PL/I, Java 8, OpenAPI 3, CICS, IMS, Liberty, Gradle
- Portable source fingerprint: `9ce1a9a20f8d49a7c13d6c06f3e292731604b84a6cbb0a77fa7b641f60ce5e31`
- Prepared local root: a sibling directory named `agent-commons-company-demo`

All paths below are parameterized. From the Agent Commons repository root:

```bash
export COMMONS_ROOT="$(pwd)"
export DEMO_ROOT="${DEMO_ROOT:-$(dirname "$COMMONS_ROOT")/agent-commons-company-demo}"
```

## Checkpoint contract

```text
01-fresh/
└── client_input/                 source only

02-initialized/
├── client_input/                 identical source
├── AGENTS.md
├── .agent-commons.yaml
├── README.md
└── dashboard/                    initialized, analysis pending

03-analyzed/
├── client_input/                 identical source
├── analysis/                     inventory, eight slice packets, synthesis
├── requirements/                 20 traceable requirements
├── estimation/                   reviewed three-point estimate
└── dashboard/                    analyzed stakeholder view

04-spec-ready/
├── everything from analyzed state
└── openspec/changes/modernize-redbook-service/
    ├── proposal.md
    ├── design.md
    ├── specs/
    ├── tasks.md
    └── traceability.json
```

Validate the checkpoint state before every rehearsal and presentation:

```bash
python3 presentation/validate-demo-checkpoints.py "$DEMO_ROOT"
```

Expected result:

```text
Demo checkpoint validation: PASS
Demo: ibm-zos-connect-redbook-modernization
Source files: 77
Source fingerprint: 9ce1a9a20f8d49a7c13d6c06f3e292731604b84a6cbb0a77fa7b641f60ce5e31
Stages: 01-fresh, 02-initialized, 03-analyzed, 04-spec-ready
```

Do not proceed with the demo if validation fails. Fix the checkpoint directories; do not weaken the contract.

## Before the presentation

### Files and checkpoints

- Run the checkpoint validator and retain the PASS output in the first terminal.
- Confirm `01-fresh` contains source only.
- Confirm `02-initialized` opens and its next action is `analyze-legacy-system`.
- Confirm `03-analyzed/dashboard/index.html` opens without a network dependency.
- Confirm `04-spec-ready/openspec/changes/modernize-redbook-service/specs/redbook-api/spec.md` opens.
- Confirm all four `client_input` trees are read-only for the demo workflow.

### Terminals and Codex tasks

Prepare three terminals or task panes:

1. **Checkpoint validation** — repository root, PASS already visible.
2. **Initialization** — working directory `$DEMO_ROOT/01-fresh`.
3. **Analysis** — working directory `$DEMO_ROOT/02-initialized`.

Open two Codex tasks in advance if possible. The first is for initialization; the second is for analysis. Authentication must already be complete.

### Browser tabs

Open and position these tabs before presenting:

1. Agent Commons presentation at `presentation/index.html`.
2. Initialized dashboard: `$DEMO_ROOT/02-initialized/dashboard/index.html`.
3. Analyzed dashboard: `$DEMO_ROOT/03-analyzed/dashboard/index.html`.
4. Requirement file: `$DEMO_ROOT/03-analyzed/requirements/modernization-requirements.json`.
5. OpenSpec file: `$DEMO_ROOT/04-spec-ready/openspec/changes/modernize-redbook-service/specs/redbook-api/spec.md`.

For the analyzed dashboard, preselect or bookmark these 4–6 views:

- management overview / decision brief;
- source composition and inventory;
- system landscape or component architecture;
- integrations and five API operations;
- legacy test quality and modernization risks;
- requirement/traceability detail for `MOD-REQ-001` or `MOD-REQ-002`.

### Room and environment

- Use a laptop/projector viewport close to 1440×900 or 1366×768.
- Verify browser zoom is 100%; use 110% only if the room requires it and no content clips.
- Disable notifications and automatic sleep.
- Keep power connected.
- Verify the presentation and dashboards work offline.
- Network is optional for the critical path; the source and checkpoints are local.
- Confirm Codex is authenticated before the audience arrives.
- Keep prepared screenshots or a short screen capture available for fallback Level 3.

## Live demo 1 — initialization

### Starting state

Show `$DEMO_ROOT/01-fresh`. Keep the view shallow: the audience only needs to see `client_input` and the open-source license/readme.

### Runtime invocation

In Codex, invoke the current skill name:

```text
$initialize-project
```

Use this prepared prompt:

```text
Analyze the read-only IBM z/OS Connect Redbook sample under client_input.

Prepare a Java 21, Spring Boot 4.x, and React modernization. Extract traceable requirements, create an evidence-linked three-point estimate and roadmap, prepare OpenSpec for approved behavior, and create a living analysis dashboard for leadership, architects, and engineers.

The source under client_input is read-only. Use Codex. External capability search is not required for the demo critical path.
```

Let genuine work remain visible for roughly 20–40 seconds. Then say:

> This normally takes several minutes. I’m not going to make you watch the terminal, so we’ll leave it running and jump to an earlier completed checkpoint of exactly the same project.

Open `$DEMO_ROOT/02-initialized`.

### Show at the initialized checkpoint

- `.agent-commons.yaml`: selected scopes, runtime, source boundary, OpenSpec/TDD policy, dashboard and architecture selection;
- `dashboard/index.html`: honest initial/pending state;
- the resolved next action: `analyze-legacy-system`.

Do not scroll through the entire manifest.

## Live demo 2 — deep analysis

### Starting state

Use the already initialized checkpoint at `$DEMO_ROOT/02-initialized`.

### Runtime invocation

In Codex, invoke:

```text
$analyze-legacy-system
```

No extra scope qualifier is needed: the configured full analysis is the default. Let the audience see as much of this sequence as is naturally visible:

- inventory resolution;
- non-overlapping slice planning;
- bounded specialist activity;
- coverage/depth state;
- coordinator-owned synthesis stages.

After roughly 20–40 seconds, say:

> This is intentionally a deep analysis, so it takes longer. Let’s jump forward to the completed analyzed checkpoint.

Open `$DEMO_ROOT/03-analyzed/dashboard/index.html`.

## Dashboard payoff

Use no more than six views. The recommended story is:

1. **Coverage:** 76 of 76 relevant artifacts accounted for; eight of eight slices validated.
2. **Composition:** COBOL, PL/I, Java, OpenAPI, generated mapping artifacts, and four host contexts.
3. **Complexity:** integration marshaling and error behavior dominate; raw line count is duplicate/generator inflated.
4. **Architecture:** host callers → z/OS Connect → Java/Liberty API → candidate target architecture.
5. **Quality/risk:** no supplied executable tests or CI; static analysis cannot prove runtime parity.
6. **Concrete finding:** `JAVA-DEF-01` and its downstream requirement/specification links.

## Concrete traceability example

### Source evidence

`analysis/slices/slice-java-api.json` records `JAVA-LIST-003` and defect `JAVA-DEF-01`:

- the API accepts the author filter as a string;
- the implementation looks up that string in `Map<Author, ...>`;
- non-empty author filters therefore return 404 rather than matching by value.

### Finding

`JAVA-DEF-01` — high severity, decision `FIX`.

### Requirements

- `MOD-REQ-001` — list Redbooks with value-based author filtering and a decision-gated empty result.
- `MOD-REQ-002` — retrieve one Redbook using normalized author equality and stable 4xx validation.

### Specification

Open:

```text
$DEMO_ROOT/04-spec-ready/openspec/changes/modernize-redbook-service/specs/redbook-api/spec.md
```

Show the “Filter by author value” scenario. Explain that the next implementation step is a behavior-relevant failing test, followed by RED → GREEN → REFACTOR and broader validation. Do not claim implementation exists; the current project correctly remains planning-blocked on authority decisions.

## Contribution segment

Do not run promotion live.

- Show the presentation’s `review-for-commons` chapter.
- Explain that it creates a sanitized project-local proposal and does not mutate Commons.
- Show `promote-to-commons` as the separate user-selected, revalidated, generalized, evaluated, synchronized, and committed flow.

## Fallback levels

### Level 1 — live command works

- Leave the genuine run visible for 20–40 seconds.
- Continue the talk.
- Use the checkpoint regardless of whether the command later completes.

### Level 2 — command is slow or fails

- Say: “The live environment is not the point of the evidence; the completed checkpoint is.”
- Switch immediately to the next prepared checkpoint.
- Do not debug on stage.
- Mention the reason only if it is obvious and useful; otherwise continue the story.

### Level 3 — runtime, tool, network, or environment is unavailable

- Use the prepared short screen capture or screenshots of:
  - initialization starting;
  - inventory and slice decomposition;
  - checkpoint validation PASS;
  - analyzed dashboard views;
  - finding → requirement → OpenSpec scenario.
- Continue with the same wording and evidence chain.
- The demo critical path must not require network access.

## Final pre-stage checklist

- [ ] `python3 presentation/validate-demo-checkpoints.py "$DEMO_ROOT"` passes.
- [ ] Presentation visual-contract check passes.
- [ ] Presentation, initialized dashboard, and analyzed dashboard load locally.
- [ ] Required tabs are in presentation order.
- [ ] Browser zoom and projector resolution are checked.
- [ ] Codex is authenticated.
- [ ] Both live task working directories are correct.
- [ ] `client_input` is treated as read-only.
- [ ] Screenshot/video fallback is locally available.
- [ ] No external search is needed.
- [ ] The presenter can identify `JAVA-DEF-01`, `MOD-REQ-001`, `MOD-REQ-002`, and the `redbook-api` spec without searching on stage.
