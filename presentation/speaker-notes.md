# Agent Commons company presentation — speaker notes

Planned duration: **27 minutes 30 seconds**, leaving roughly 2 minutes 30 seconds for navigation variance, a slow demo handoff, or one audience question.

The recommended route is intentionally not a simple top-to-bottom scroll. After the vocabulary chapter, jump to `#initialize`, start the live initialization, then show `#architecture` while it runs. Return to the initialized checkpoint, start analysis, and use the prepared analyzed/spec-ready checkpoints. Show the capability graph and navigator near the end as optional proof rather than making the audience learn the repository before they understand the outcome.

## 1. Before the work, comes the setup — 00:00–01:20

**Priority:** MUST SHOW
**Target duration:** 1:20
**Key message:** AI-assisted projects repeatedly spend time teaching the environment how to work before doing the actual project.

### Spoken wording

“When we start an AI-assisted project, the first work is often not the project itself.

We define the goal. We explain which source is read-only. We establish how evidence should be recorded, how testing works, what a dashboard should contain, and what the agent is allowed to change.

Then another project starts, and we do a surprising amount of that again.

The project may be different—modernization, development, research, architecture—but much of the engineering method is reusable. Agent Commons changes the starting point. Instead of teaching the environment from zero, we begin with methods that have already been reviewed and tested.”

“Think of the usual first week of an unfamiliar project. Before anyone can trust an answer, we need rules for source access, evidence, testing, documentation, and completion. Those decisions are valuable engineering work. The waste appears when they are solved in isolation every time, or survive only as fragments in somebody’s previous repository.”

### Transition

“So the problem is not that every project is the same. The problem is that the reusable foundation keeps being rebuilt inside each different project.”

### Demo action

None. Keep the opening clean and under 90 seconds.

### Optional content

Do not read the four proof lines at the bottom. Use them only if the audience needs a concrete example of “setup.”

### Presenter warning

Do not begin with repository counts, runtime names, or agent terminology. The audience must understand the repetition problem first.

## 2. Every project rebuilds the same foundation — 01:20–02:40

**Priority:** MUST SHOW
**Target duration:** 1:20
**Key message:** Different missions share recurring setup, rules, documentation, and validation work.

### Spoken wording

“These three projects genuinely need different domain knowledge. A legacy assessment is not a greenfield build, and neither is a research engagement.

But underneath them, we repeatedly recreate the same kinds of method: inventory before interpretation, traceable evidence, acceptance criteria, testing discipline, validation, dashboards, and handoff rules.

When that method remains inside one project, it gets copied, adapted, forgotten, and eventually recreated. The organization paid to learn it, but the next team cannot reliably start with it.”

“The repeated foundation is also where inconsistency enters. One team records evidence carefully, another relies on summaries. One team treats tests as proof, another adds them after the implementation. One team produces a decision-ready dashboard, another leaves findings scattered across files. Shared methods give teams a common starting quality without pretending their projects are identical.”

### Transition

“The useful move is to separate project truth from reusable method.”

### Demo action

None.

### Optional content

Skip the individual examples on the three project cards if running late.

### Presenter warning

Do not imply that every project should use an identical process. The claim is reusable building blocks, not one rigid methodology.

## 3. Keep the facts local. Share the method. — 02:40–03:55

**Priority:** MUST SHOW
**Target duration:** 1:15
**Key message:** Project-specific truth stays local; reusable engineering method can become a governed shared asset.

### Spoken wording

“Here is the whole idea in one sentence: keep the project facts in the project, and share the reusable way of working.

The left side is everything specific to the engagement: source code, business rules, credentials, decisions, and brand. That stays local.

The right side is the playbook: how we analyze, test, create diagrams, build dashboards, and validate the result. That can be reviewed, generalized, and reused by the next team.

So Agent Commons is not a central store for project data. It is a shared library of proven ways to do the work.”

### Transition

“That library uses a few terms. I’ll define them once in plain language, then use them in the demo.”

### Demo action

None.

### Optional content

None; this boundary prevents privacy and governance misunderstandings later.

### Presenter warning

Use the single sentence first. Point left for project facts and right for reusable method. Do not explain the governance process yet.

## 4. Plain-language building blocks — 03:55–05:40

**Priority:** MUST SHOW for definitions; navigator is OPTIONAL IF TIME
**Target duration:** 1:45 now, with up to 0:45 later for the navigator
**Key message:** Each capability type has one distinct responsibility.

### Spoken wording

“A skill is a reusable playbook: how a piece of work should be done.

An agent is closer to a specialist colleague. It gets an independent responsibility when separation of judgment is useful.

A tool is deterministic. It counts, inventories, renders, validates, or transforms something where guessing would be irresponsible.

An archetype is a project recipe. It says which capabilities normally belong together for development, modernization, research, or presentation work.

An overlay is a cross-cutting concern—traceability, a living dashboard, durable project memory, branding, or localization.

An adapter is the bridge into Codex, Claude Code, Cline, or OpenCode. The method remains single-source even though each runtime exposes it differently.

And an eval is the automated behavior check that tells us whether a capability still keeps its promise.”

“These categories prevent a common failure mode: treating everything as a prompt. If exact enumeration is needed, use a tool. If one perspective needs independent judgment, use an agent. If several capabilities form a repeatable project shape, use an archetype. The names make ownership and validation explicit.”

### Transition

“That is enough vocabulary to use the system. Let’s start a real project.”

### Demo action

Jump directly to `#initialize`. Do not explore the navigator yet.

### Optional content

Template definition; repository tree; capability navigator; source preview.

### Presenter warning

Do not read all eight definitions from the screen. Give the one-line analogy, then move on.

## 5. Install once. Initialize the project you actually have — 05:40–08:20

**Priority:** MUST SHOW
**Target duration:** 2:40
**Key message:** A real goal and source boundary are enough to compose a useful project; runtime syntax differs, while the method remains shared.

### Spoken wording

“Installation is managed by the repository installer. Codex is the default runtime, and the same canonical methods are adapted for Claude Code, Cline, and OpenCode according to what each runtime actually supports.

For this demo I’m using an Apache-licensed IBM z/OS Connect sample. It contains COBOL, PL/I, Java, OpenAPI, CICS, and IMS material. The source is read-only.

I’ll start from the fresh checkpoint, which contains essentially only `client_input`. Then I invoke `initialize-project` with the outcome: analyze the source, derive requirements, estimate modernization, prepare OpenSpec, and create a dashboard.

Notice what I do not do. I do not choose 40 individual skills.

The diagram has two reading directions. Follow the numbered arrows down the left: human input, the initializer, an optional human checkpoint, deterministic tools, and output. Inside the initializer lane, read left to right: inspect, interpret, compose, initialize.

The output is deliberately practical: project instructions, a composition manifest, an optional dashboard shell, and one explicit next action.”

“The supported runtimes use different adapters. In Codex the skill is selected with a dollar-prefixed name. Claude Code and Cline expose slash commands. OpenCode can be asked to use the skill. That is a user-interface difference, not a fork of the engineering method.”

### Demo action

1. Show `$DEMO_ROOT/01-fresh`.
2. In the prepared Codex task, invoke `$initialize-project` with the prompt from `demo-runbook.md`.
3. Let output run for 20–40 seconds.
4. Say: “This normally takes several minutes. I’m not going to make you watch a terminal, so I’ll leave it running and show you an earlier completed checkpoint of exactly the same source.”
5. Jump to `#architecture` while the command continues.

### Optional content

Installer `status`, `doctor`, and `verify` commands; exact manifest fields; capability-gap discovery details.

### Presenter warning

The skill invocation is runtime UI input, not a shell command. Never imply that the supported runtimes have identical native agent behavior.

## 6. One method, adapted to each tool — 08:20–10:30

**Priority:** MUST SHOW
**Target duration:** 2:10
**Key message:** Agent Commons maintains one method, adapters fit it to each AI tool, and project evidence remains local.

### Spoken wording

“While initialization runs, the architecture is easiest to read from left to right.

First, Agent Commons holds one reviewed version of each playbook. Second, a small adapter puts that playbook into the form each AI tool understands. Third, the tool uses it inside the project, where the source and decisions remain local.

That is the top row: one method adapted to different tools without maintaining separate copies.

The lower row is the whole project flow: describe the need, apply the right playbooks, keep evidence with the project, and verify the outputs.

That is all you need to remember: Commons provides the method; the AI tool applies it; the project remains the source of truth.”

### Transition

“Now let’s look at what the initializer produced before any deep analysis was complete.”

### Demo action

Open `$DEMO_ROOT/02-initialized`.

### Optional content

Runtime-specific installation details and the mechanics of parallel specialist work.

### Presenter warning

Read the top row left to right, then summarize the lower row in one sentence. Say “one method, adapted to each tool,” not “all tools behave identically.”

## Demo interlude A: initialized checkpoint — 10:30–11:40

**Priority:** MUST SHOW
**Target duration:** 1:10
**Key message:** Initialization creates a governed starting state and an explicit next action; it does not perform the whole project instantly.

### Spoken wording

“This is the completed initialization checkpoint of the same source.

The important files are the project instructions and `.agent-commons.yaml`. The manifest records the selected archetypes, runtime, read-only source boundary, deliverables, OpenSpec and TDD policy, dashboard configuration, and capability state.

The dashboard is already a valid shell, but it is honest about what is not analyzed yet. And the next action is explicit: run `analyze-legacy-system`.”

“That honesty is important. An initialized project is not an analyzed project. The scaffold says what has been selected, what remains unknown, and what capability should run next. It gives the team a recoverable state instead of an optimistic completion message.”

### Demo action

Show only:

- `.agent-commons.yaml`: scopes, read-only source, selected lifecycle;
- `dashboard/index.html`: initial state and next action;
- avoid reading the complete YAML.

### Transition

“Initialization tells us how to work. Analysis now has to establish what is actually true.”

### Presenter warning

Do not claim initialization found the later defects or estimates.

## Demo interlude B: start deep analysis — 11:40–12:20

**Priority:** MUST SHOW
**Target duration:** 0:40
**Key message:** The live analysis visibly inventories and decomposes work, but the talk does not depend on completion.

### Spoken wording

“From the initialized checkpoint I’ll now start `analyze-legacy-system`.

The first visible steps should be inventory, bounded slices, ownership, and the coverage gate. This is intentionally deep, so it takes longer than a stage demo should. We’ll let it continue and jump forward again.”

### Demo action

Invoke `$analyze-legacy-system` from `$DEMO_ROOT/02-initialized`. Let the audience see inventory and decomposition output if available, then leave it running.

### Transition

“These checkpoints are how we keep the demo honest without turning the presentation into a loading screen.”

## 7. One real project. Traceable checkpoints — 12:20–13:30

**Priority:** MUST SHOW
**Target duration:** 1:10
**Key message:** Every stage uses the same source fingerprint, and each checkpoint is validated for the lifecycle state it claims.

### Spoken wording

“These checkpoint folders are not separate demos.

They contain the same 77 source files with the same portable fingerprint. The first has source only. The second is initialized. The third has completed analysis, requirements, estimate, and dashboard. The fourth adds the reviewed OpenSpec planning package.

A small validator checks both sides: files that must exist and later-stage files that must not exist. That prevents me from accidentally opening the wrong folder on stage.”

“The folders are intentionally boring. They are not separate branches of a fictional success story. They are frozen lifecycle points from the same project, so we can move forward in time without pretending the work is instantaneous.”

### Demo action

If useful, show the one-line `Demo checkpoint validation: PASS` result. Then open `$DEMO_ROOT/03-analyzed/dashboard/index.html`.

### Optional content

Do not explain how the portable fingerprint is calculated unless asked.

### Presenter warning

Call these “previously completed runs,” not simulated output.

## Demo interlude C: analyzed dashboard payoff — 13:30–18:30

**Priority:** MUST SHOW
**Target duration:** 5:00
**Key message:** Deep analysis turns source into decision-ready evidence for multiple audiences, with explicit limitations.

### Spoken wording

“This is the main payoff.

First, the management overview: all 76 relevant artifacts are accounted for, across eight validated analysis slices. The dashboard also states the limitation: this is an IBM public tutorial sample, not evidence for a ministry-scale production estimate.

Second, source composition and complexity. The source spans COBOL, PL/I, Java, OpenAPI, CICS, IMS, and generated mapping artifacts. The line count is large, but the analysis explains that much of it is duplicated or generated. The harder problem is the integration and error-handling boundary.

Third, architecture and integrations. We can see the host callers, z/OS Connect boundary, Java service, API operations, and the candidate target shape.

Fourth, test quality and risk. No executable test suite or CI configuration was supplied, so static evidence cannot prove runtime parity. Characterization tests are a gate, not an afterthought.

And here is one concrete finding. The Java endpoint accepts an author query as a string, but looks it up in a map keyed by `Author` objects. A non-empty author filter therefore returns 404 instead of matching by value. The analysis records that as `JAVA-DEF-01` with source coordinates.”

“That finding is useful for three reasons. It is specific enough to verify. It affects externally visible API behavior. And it shows why a summary chart is not the end product: the evidence can drive a requirement and a testable contract.”

“The dashboard also keeps uncertainty visible. The sample uses in-memory maps, has no production system of record, and does not tell us production volumes, recovery objectives, security ownership, or which host callers must coexist. Those are not details to guess. They become named decision gates in the roadmap and estimate.”

“For leadership, the view answers: what do we know, what remains uncertain, what is the next safe investment? For architects, it exposes systems, data, interfaces, and transition choices. For engineers, the same evidence links into requirements, specifications, tests, and open questions.”

### Demo action

Show 4–6 views only:

1. Overview / decision brief.
2. Inventory and source composition.
3. System landscape or component architecture.
4. Integrations / API operations.
5. Test quality and risks.
6. Requirement or traceability detail for `MOD-REQ-001` or `MOD-REQ-002`.

### Transition

“A finding becomes useful when it survives the jump from source evidence into an implementation contract.”

### Presenter warning

Do not present the 590 person-day scenario as a fixed price or measured production estimate. It is a low-confidence, evidence-linked scenario for the public sample.

## 8. Project recipes / concrete traceability — 18:30–21:00

**Priority:** MUST SHOW the legacy and OpenSpec + TDD tabs; other tabs are DEEP-DIVE ONLY
**Target duration:** 2:30
**Key message:** The lifecycle preserves traceability from evidence to requirement to specification, then uses TDD for implementation evidence.

### Spoken wording

“This is the chain we care about.

The source evidence becomes finding `JAVA-DEF-01`: author filtering is broken by a type mismatch in the lookup.

That feeds `MOD-REQ-001` and `MOD-REQ-002`, which define value-based author matching and stable validation behavior.

The `redbook-api` OpenSpec turns those requirements into observable scenarios. Only after review and approval should implementation begin.

Then TDD is concrete: write the failing author-filter test, see RED for the right reason, make the smallest change, see GREEN, refactor, and run the broader validation. The project currently stops before implementation because authority decisions remain open. That is a feature of the governance, not a failure of the demo.”

“OpenSpec is not a decorative document added after coding. It is the agreed behavior contract before coding. The scenario says what a caller can observe, while design and task files hold implementation choices and sequencing. Traceability tells us which requirement revision the specification consumed.”

“A green unit test alone would still not finish the lifecycle. The implementation must satisfy the scenario, broader gates must pass, and independent verification must reconcile the source requirement, specification, code, tests, and evidence.”

### Demo action

1. In `03-analyzed`, open the requirement detail.
2. Switch to `$DEMO_ROOT/04-spec-ready`.
3. Show `openspec/changes/modernize-redbook-service/specs/redbook-api/spec.md`.
4. Select the “OpenSpec + TDD” tab on the presentation.

### Optional content

Research → sales and hybrid tabs; complete task list; all 20 requirements.

### Presenter warning

Do not imply that an implementation was completed. The checkpoint is spec-ready/planning state, and several decisions correctly block implementation.

## 9. Capability network — 21:00–21:40

**Priority:** OPTIONAL IF TIME
**Target duration:** 0:40
**Key message:** Relationships are generated from canonical evidence; the library is more than a prompt folder.

### Spoken wording

“This graph is useful proof that the library is composed, not just collected. Skills connect to archetypes, tools, agents, adapters, and evals through generated relationships.

I can focus on `analyze-legacy-system` and see the neighborhood that supports it. The graph is here for exploration; it is not something we need to tour node by node.”

### Demo action

Search for `analyze-legacy-system`, select it, and stop after the focused neighborhood appears.

### Optional content

Skip the entire graph if the dashboard demo ran long.

### Presenter warning

Do not attempt to explain every node or relationship.

## 10. Capability navigator — 21:40–22:20

**Priority:** OPTIONAL IF TIME
**Target duration:** 0:40
**Key message:** Developers can inspect the actual capability source and relationships after the talk.

### Spoken wording

“The navigator is the practical deep-dive surface. Search by problem, select a capability, read its purpose and boundaries, inspect a safe source preview, and see where it is used.

The important point is not the count. It is that the presentation is generated from the same canonical catalog rather than maintained as a separate marketing inventory.”

### Demo action

Return to `#inside`, search for `initialize-project`, and show the overview. Avoid opening long source previews unless asked.

### Optional content

Skip if under 8 minutes remaining.

### Presenter warning

Do not turn this into a repository tour.

## 11. review-for-commons — 22:20–23:35

**Priority:** MUST SHOW
**Target duration:** 1:15
**Key message:** Project learning becomes a sanitized proposal first; review does not mutate Commons.

### Spoken wording

“Projects will create useful local methods. We do not copy those directly into Commons.

`review-for-commons` asks whether the behavior is reusable, whether Commons already covers it, whether it is safe to generalize, and what kind of capability it should become.

Its output stays in the project as a sanitized proposal. Nothing is installed, activated, or promoted automatically. A person selects the exact candidate—or decides that it should remain local.”

“This protects both sides. Commons is not flooded with near-duplicates, and the project does not accidentally publish client assumptions or proprietary evidence. A strong local capability can be valuable even when the correct decision is to keep it local.”

### Transition

“Selection authorizes a second, independent gate. It does not guarantee promotion.”

### Demo action

Show the prepared review flow only. Do not run it live.

### Optional content

Detailed classification vocabulary such as EXACT, OVERLAP, EXTENSION, and VARIATION.

### Presenter warning

Keep external open-source discovery separate from internal project promotion; both use review boundaries, but they are not the same source flow.

## 12. promote-to-commons — 23:35–24:45

**Priority:** MUST SHOW
**Target duration:** 1:10
**Key message:** Promotion generalizes and revalidates one selected candidate, adds evals, synchronizes adapters, and may still decline the change.

### Spoken wording

“`promote-to-commons` binds the exact approved candidate and challenges it again.

Is the evidence strong enough? Is there confidential detail? Is the license understood? Does the proposal duplicate an existing capability? What is the smallest runtime-neutral abstraction?

Only then do we change the canonical library, add or update evals, synchronize catalogs and adapters, refresh generated presentation data, run the repository gates, and commit.

Promotion is not copying. It is generalization under governance.”

“The result may be a new capability, but it may also be an extension to an existing one, a split, a merge, a deprecation, or a deliberate no-change decision. The classification matters less than preserving one coherent canonical responsibility.”

### Transition

“That governance is what turns repeated project experience into an organizational asset.”

### Demo action

None; use the prepared slide.

### Optional content

Skip the runtime row and individual blocking labels if running late.

### Presenter warning

Never say user approval guarantees inclusion. It authorizes revalidation of one candidate.

## 13. Good engineering methodology compounds — 24:45–26:10

**Priority:** MUST SHOW
**Target duration:** 1:25
**Key message:** The credible company benefits are faster starts, consistent practice, protected quality, retained knowledge, and runtime flexibility.

### Spoken wording

“This is the company-level value.

Teams spend less time recreating setup. They use a more consistent vocabulary and engineering baseline. Reusable behavior is protected by evals and deterministic checks. Useful methods survive beyond one project or one tool.

We do not need an invented percentage saving to make the case. The compounding loop is concrete: a project starts with Commons, learns something, reviews it, promotes only the reusable part, and the next project starts better.”

“That also reduces tool lock-in. Teams can change their coding-agent runtime without throwing away the methodology, because the canonical capability lives above the adapter. The experience will not be identical in every runtime, but the engineering intent, boundaries, and validation remain shared.”

### Transition

“That leaves one practical question: where should we try it next?”

### Demo action

None.

### Optional content

Skip the detailed loop after stating the four benefits if under two minutes.

### Presenter warning

Avoid unsupported cost or productivity claims.

## 14. Every project teaches us — 26:10–27:30

**Priority:** MUST SHOW
**Target duration:** 1:20
**Key message:** The next team should benefit from verified project learning; invite a concrete follow-up.

### Spoken wording

“Every project teaches us something. The question is whether that knowledge stays in the project where it was discovered, or whether the next team can begin with it.

Agent Commons gives us a governed path from project experience, through review, into reusable capability—and back into the next project.

If your team has a real project where this could help, invite me for a deeper walkthrough. We can try the method against the actual use case, the actual constraints, and the actual evidence.”

### Transition

Stop. Take questions.

### Demo action

If the live initialization or analysis completed, mention it in one sentence after the close. Do not reopen the story or extend the technical tour.

### Optional content

None.

### Presenter warning

End on the invitation, not on architecture, repository counts, or a command prompt.

## Rehearsal notes

- Planned spoken content: **27:30**.
- Expected live-demo interaction variance: **±1:00**.
- First cut if behind: capability navigator, then capability graph.
- Second cut: architecture memory and diagram-family details.
- Never cut: opening problem, project-local boundary, glossary, both live command starts, analyzed dashboard, concrete finding, requirements/OpenSpec/TDD chain, contribution boundary, company benefit, closing invitation.
- Most difficult transition: jumping from the glossary to `#initialize`, then back to `#architecture`. Rehearse the anchor navigation twice.
- Highest click risk: analyzed dashboard navigation. Keep the six selected views open in tabs before the talk.
- Terminology risk: “OpenSpec” first appears visually in initialization. Define it aloud as “the agreed behavior contract before implementation.”
