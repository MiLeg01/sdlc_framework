---
name: initialize-project
description: Adaptively bootstrap an empty, nearly empty, or existing project for legacy modernization, development, research, presentations, or a composition. Use when explicitly initializing a workspace or selecting commons composition. Do not use for ordinary work in an established project, bulk-copy the library, overwrite existing files, or add durable process to a tiny task.
---

# Initialize a project

Build the smallest recoverable project structure that supports the actual goal.

## Discover before asking

1. Inspect the current directory, Git state, instruction files, manifests, source roots, documents,
   and supplied assets without opening secrets or generated/dependency trees.
2. Separate discoverable facts from choices only the user can make.
3. Preserve existing files and conventions. Do not overwrite or reinitialize an established project.

For a standard substantial workflow, create a lightweight dependency DAG immediately after parsing the
brief. Treat source inspection, supplied-brand inspection, Commons resolution, and existing-environment
inspection as sibling branches. Use `coordinate-parallel-agents` when two or more branches are genuinely
independent; keep tiny work single-agent. The coordinator owns fan-in, canonical IDs, shared files,
progress truth, and final validation.

## Two supported intake modes

- **Interactive:** with no supplied brief, inspect the workspace and ask a small adaptive sequence. Do not
  require a fixed questionnaire before making progress.
- **Brief-driven:** when the invocation includes natural-language project context, extract everything the
  user already supplied, inspect allowed source locations, and ask only for important unresolved choices.

Before asking, classify intake facts as `KNOWN` when explicitly supplied, `DISCOVERED` when verified from
the workspace or source locations, `INFERRED` when they are high-confidence consequences of the brief, and
`MISSING` when a decision still materially affects setup. Questions normally come only from `MISSING`.
Confirm an inference only when uncertainty could materially change scope or generated state.

For migration briefs, extract source technology, target technology, and migration intent separately.
`prepare migration` means planning, mapping, sequencing, readiness, and backlog preparation; it does not
select full implementation. It does imply approved requirements should be transformed into OpenSpec
specifications and that canonical TDD is planned for the later implementation phase. `implement migration`
composes `legacy-migration` with `development` and activates OpenSpec plus test-driven-development.

For ordinary development, OpenSpec specification and `test-driven-development` are defaults, not questions.
Do not ask whether to enable them. Respect explicit phrases such as `no OpenSpec`, `without OpenSpec`,
`no TDD`, or `normal implementation, no TDD` by recording an exclusion and the resolved alternative in
`.agent-commons.yaml`.

`mutation-testing` follows the same rule. When the detected technology has maintained mutation tooling and
implementation or TDD is in scope, select it from the archetype defaults without asking. Surface one concise
question only when the adapter choice has a material consequence, when the expected run cost is unusually
high for the project's size, or when repository policy restricts adding build tooling. Record an unsupported
technology explicitly rather than omitting the capability, so the project state distinguishes "not applicable
here" from "never considered".

Before resolving methodology in an existing target, inspect `.agent-commons.yaml`,
`openspec/config.yaml`, existing OpenSpec specs/changes, `.specify/`, and explicit specification directories.
Reuse an existing OpenSpec hierarchy. Preserve a clearly established alternative specification or
implementation method unless the user deliberately requests a migration; report a conflict instead of
creating or overwriting an incompatible hierarchy.

## First interaction

Ask adaptively, normally one to three related questions at a time:

1. **Archetype:** legacy migration/analysis, development/new application, research, presentation, or a
   composition. Permit multiple selections and use the canonical manifests under `archetypes/`. Sales is
   a presentation purpose and storytelling overlay, not a separate archetype.
2. **Runtime:** detect Codex, Claude Code, Cline, or OpenCode from existing native files. Confirm only
   when no runtime is evident or the evidence conflicts. Permit deliberate multi-runtime projects.
3. **Goal:** desired outcome, concrete deliverables, and observable definition of done.
4. **Context:** personal/internal, client, generic, or product. Ask for company details only when useful.
5. **HTML artifact:** for substantial work, propose a project, technical, or management dashboard;
   executive or sales presentation; or a combination. Allow `none`.
   When a dashboard is selected, instantiate the canonical Agent Commons living-dashboard structure.
   Do not ask the user to design its section hierarchy or navigation. Full legacy-modernization mode keeps
   every standard section in canonical order and records pending/not-observed/not-applicable states;
   only brand, audience visibility, language, and genuinely project-specific extension needs remain contextual.
6. **Visual identity:** when an HTML dashboard or presentation is requested and no brand was supplied, use
   Accenture branding as the delivery fallback. Reuse a supplied website, design system, screenshot, asset,
   logo, or reference without asking for it again; if it cannot be resolved, retain the failure evidence and
   continue with the Accenture fallback.
7. **Client-facing language:** when an HTML dashboard or presentation is selected and language remains
   unresolved, ask once for English, German (Austria), German plus English switch, or another language.
   Do not ask when the brief already states working language, client language, Austrian German, bilingual
   delivery, or that English must remain available. Before asking, resolve persisted client context and the
   canonical public-sector policy below.
8. **Project references:** local files or directories, URLs, existing projects, natural-language examples,
   and what to use or ignore from each. References are optional and project-local.
9. **Capability gaps:** after the brief and archetypes are clear, resolve required, strongly recommended,
   and optional capability families against the actual commons catalog. External research is one possible
   response to a material gap, never a default assumption or automatic action.

When the user supplies a client-brand URL or artifact, branding is a required delivery constraint rather
than optional inspiration. Start brand inspection alongside source discovery. Follow redirects and inspect
HTML, linked stylesheets, manifest, metadata, official favicon/logo assets, and exact source colors. Record
one version-2 evidence-derived brand profile and exact asset set; both dashboard and presentation renderers
must consume it when valid. If resolution is blocked or unreadable, both renderers use the Accenture fallback
and still create their `.html` outputs. Record client-brand fidelity as unresolved and never infer it from
fallback token consistency.

Resolve a website once with the resolver supplied by `create-branded-html-artifact`, persist the validated
result at `brand/profile.json`, and pass that same normalized object to the canonical living-dashboard
renderer and the presentation renderer. When both artifacts are selected, verify that their profile, theme,
and asset fingerprints and their embedded logo and favicon bytes all match before writing the project.

When substantial development, migration, or architecture work explicitly requests architecture
documentation, capture the requested views without asking again. If architecture documentation is wanted
but the views are genuinely unspecified, ask one concise multiple-selection question covering system
landscape, component architecture, class/domain model, ER/data model, sequence, data flow, migration
roadmap, or letting the analysis determine the views.

Never ask for information already present in the workspace. Read
`references/question-routing.md` only for the selected scope and stop questioning once enough is known
to create a useful first checkpoint.

## Scope follow-up

- For legacy work, determine languages, application boundary, target technology, integrations,
  schemas/interfaces, persistence, reference systems, existing documentation, traceability depth,
  architecture views, graph needs, implementation boundary, and deployment target.
- For development, determine greenfield versus existing, product behavior, frontend/backend,
  persistence, authentication, integrations, architecture constraints, testing, deployment, and UI.
- For research, determine the topic or question, audience, supported decision or artifact, boundaries,
  evidence expectations, depth, and desired outputs. Do not ask again for topic, audience, or output when
  the brief already supplies them.
- For presentations, determine topic, audience, decision or call to action, one or more purposes from
  sales, executive, technical, informational, workshop, and internal, evidence sources, narrative depth,
  brand source, interaction model, diagrams/graphs, and delivery format.
- For sales presentations, determine what is proposed, the likely customer situation, desired next action,
  differentiators, objections, and proof only when those are neither supplied nor intentionally delegated
  to research.

## Interpret natural-language composition

Treat explicit language as selection, not as a question to repeat. Examples include research alone,
presentation alone, research plus presentation, research followed by a sales presentation, or legacy
analysis followed by an executive presentation. Resolve combinations into multiple archetypes and
overlays; never create a fixed archetype for each sentence shape.

Infer explicit technical diagram needs conservatively:

- applications and integrations → system landscape;
- modules, components, or service structure → component architecture;
- object/domain structure → class diagram;
- database entities and relationships → ER diagram;
- ordered request, login, or service-call behavior → sequence diagram;
- batch, ETL, lineage, or data movement → data-flow diagram;
- migration waves, coexistence, transition architecture, or retirement → composed migration roadmap.

Interpret localization requirements compositionally. `Working language: English; client delivery:
Austrian German + English switch`, `Dashboard should be German/English`, and `final presentation in
German, keep English available` select `bilingual-client-delivery`, record `en` plus `de-AT`, and use
`de-AT` as the client default without asking again. Do not require every dashboard to be bilingual from
the start; English-first working artifacts remain normal until client delivery.

## Public-sector client delivery

Persist client classification separately from project type. Public sector is a client/delivery context,
not an archetype. Use explicit statements, organization identity, official website or brand sources,
discovered organization metadata, and existing project configuration. Classify useful decisions as
`CONFIRMED`, `HIGH_CONFIDENCE`, `UNCERTAIN`, or `NOT_PUBLIC_SECTOR`. A government-style domain is one
signal, never sufficient when stronger evidence contradicts it.

For `CONFIRMED` or `HIGH_CONFIDENCE` public-sector clients with resolved German geography, apply without
asking again:

- Austria: `de-AT`; Germany: `de-DE`; Switzerland: `de-CH`;
- dashboard: resolved German locale plus `en`, German initially selected, one state-preserving language
  switch in the same HTML file; for `de-AT`, render only Austrian (`🇦🇹`) and UK (`🇬🇧`) flags in that
  control, with accessible German (Austria) and English names;
- sales/client presentation: resolved German locale only, no English version or localization runtime by
  default;
- client branding and terminology remain in force;
- public-sector presentation tone is precise, factual, restrained, credible, and outcome-oriented.

If sector or locale is genuinely uncertain and changes delivery, ask once. Do not ask when client identity,
official source, geography, and sector make the answer obvious. Resolve brand evidence and sector/locale
evidence concurrently where possible, then combine them into the delivery policy.

Precedence is: explicit project instruction, explicit client requirement, public-sector client policy,
archetype default, neutral Commons default. Instructions such as `presentation must be English`, `dashboard
German only`, `dashboard English first`, or `bilingual sales deck` override only the named output.

When a brief includes labeled or conversational values such as topic, audience, desired outcome, sales
objective, brand, source material, or references, record them directly. Ask only unresolved important
decisions. Multiple presentation purposes may be selected together.

Treat supplied source permissions as hard constraints. Inspect a read-only source only enough to discover
its technologies, build structure, documentation, tests, schemas, and interfaces; never create project
files, initialize Git, reformat, or write analysis artifacts there. Record each source separately because
multiple sources may have different access policies. Generated project instructions must state:

> Source repositories/directories designated read-only may be analyzed but must never be modified.

If the brief requests both read-only access and in-place modification, or both analysis-only scope and full
implementation, stop before changes and surface the conflict for resolution.

## Compose the project

For every standard-scale legacy, development, research, or presentation project, select the existing
`durable-state` overlay automatically and record lazy hierarchical project memory under
`.agent-commons/memory/`. Tiny projects keep memory disabled unless the user explicitly selects durable
state. Do not ask a routine "do you want memory" question.

Read `archetypes/composition.yaml` and the selected archetype manifests rather than maintaining another
capability list here. Select only relevant commons capabilities and record them by reference in
`.agent-commons.yaml`; do not copy the full library. Prefer overlays for evidence traceability, branded
HTML, living dashboards, or durable state. Activate conditional capabilities only when their manifest
condition is actually true.

Use `branded-html` whenever an HTML artifact is selected and `living-dashboard` when that artifact is a
canonical-state dashboard. Do not add evidence traceability or durable state merely because the project is
standard-sized; select them when their stated concern is present. Compose `legacy-migration` with
`development` when target implementation is material rather than inventing an implementation overlay.
The living-dashboard overlay always resolves the canonical information architecture. Archetypes determine
applicability and data population for inventory, requirements, specifications, architecture, modernization,
implementation, or validation, but they must not invent a different dashboard structure.
Normal development defaults to OpenSpec specifications followed by the canonical
`test-driven-development` skill. Analysis-only legacy work may stop at evidence-backed requirements;
migration preparation adds OpenSpec specifications without claiming production implementation.
Explicit methodology exclusions remove only the named default capabilities and remain visible in the
resolved manifest; they do not weaken acceptance, testing, validation, or truthful completion obligations.
Use `bilingual-client-delivery` only when both working and client languages must remain available in one
HTML artifact. Record working language, client language, supported locales, default locale, offline
behavior, and persistence in `.agent-commons.yaml`.
Use `public-sector-client-delivery` when the public-sector classification and locale are confirmed or high
confidence. Persist client sector, confidence, country, locale, and evidence. Record dashboard and
presentation policies separately under their own manifest sections; do not collapse them into one generic
language field. The bilingual overlay is selected for a bilingual dashboard or an explicitly bilingual
presentation, not for a default German-only public-sector sales deck.
Classify a one-off utility or similarly small task as `tiny`; it receives no default skills, agents,
`docs/`, dashboard, or presentation. Use `standard` only when durable state or a multi-step workflow adds
real value. Presentation scope without an HTML deliverable must not select HTML skills.

Select `architecture-documentation` when explicit technical diagrams or architecture documentation are
requested. Activate only the matching view conditions; do not enable every diagram capability. Record the
views in `.agent-commons.yaml` so documentation, dashboard, and presentation work share the same model.

Use `sales-storytelling` whenever sales is an explicit or clearly inferred presentation purpose. Compose
research and presentation when new evidence gathering is requested; do not add research when a
presentation is based on sufficient existing source material. Research without presentation creates no
presentation scaffold. When both are selected, research synthesis is the factual handoff to presentation
narrative and unsupported claims must not appear later.

## Project references

Treat references as guidance about visual quality, storytelling, structure, density, diagrams, timelines,
clusters, typography, interaction, navigation, brand, or content structure. Accept paths, directories,
existing projects, URLs, and natural-language descriptions. Capture the user's positive and negative
intent, such as “use structure and density, not colors.”

Record a lightweight machine-readable reference entry with source, type, applies-to, use, ignore,
read-only access, project-local scope, and whether copying is allowed. Default copying to false. Create a
small project reference index only when references exist; do not copy referenced files by default or create
unused category directories.

Reference precedence is:

1. explicit project reference;
2. project brand or design system;
3. canonical commons visual-pattern guidance;
4. Accenture fallback.

Extract the relevant principle instead of blindly cloning an example. Client branding and previous-project
material never become canonical commons automatically. Reusable learning must later pass through
`review-for-commons`, generalization, validation, and explicit promotion.

## Detect capability gaps

After resolving composition, read the selected archetype `capability_expectations`, the semantic
`provides` metadata in `catalog/capabilities.yaml`, and the actual selected capability sources. Use
`tools/resolve_capability_gaps.py` for the deterministic comparison. Do not infer sufficient coverage from
a generic skill name.

Classify requirements as required, strongly recommended, or optional and coverage as:

- `COVERED`: actual selected commons behavior is sufficient;
- `PARTIALLY_COVERED`: generic behavior exists but a material specialist aspect is absent;
- `MISSING`: no sufficient behavior exists;
- `OPTIONAL_GAP`: useful but not required for safe initialization.

For migrations, always assess three independent dimensions: source-technology understanding,
target-technology architecture/implementation, and the source-to-target bridge. Separate source and target
coverage never proves the bridge. Prefer reusable composition over inventing a permanent skill for every
technology pair.

Required or strongly recommended gaps trigger external discovery automatically for standard projects unless
the user explicitly selected `skip`, `project-local-later`, or `generic-only`. Do not ask again when the brief
already authorizes online search. Record optional gaps without starting broad discovery when all important
capabilities are covered.

External discovery is not on the initialization critical path. Persist its `running`, `completed`,
`partial-rate-limited`, `partial-source-failure`, or `failed` state under
`.agent-commons/external-discovery.json`, continue core setup, and allow the next canonical lifecycle action
to proceed. Reuse a fresh matching completed, partial, or running result instead of launching a duplicate
process. If a different project-local discovery lease is active, preserve its state and defer the new search;
never classify a mismatched active run as a matching cached result. Never reuse a fully failed result.
Respect source constraints such as official only, official plus
curated, GitHub-wide, or all enabled tiers. General-web discovery remains opt-in according to
`external/sources.yaml`.

## External discovery boundary

Invoke `search-external-capabilities` as an actual independent process using three to eight focused queries
derived from the identified gaps and the privacy-safe parts of the full brief. Continue safe independent
setup in parallel: source inventory, project instructions, draft manifest, brand resolution, and the
canonical dashboard shell do not depend on accepting an external specialist. Search
official configured sources first, then curated sources, then community GitHub discovery when allowed, and
general web only when explicitly enabled or requested. Do not search for a vague technology pair when
specific semantic-analysis, dependency, business-rule, mapping, or validation gaps are known.

Return approximately three to seven genuinely relevant candidates. For each show name; repository and path;
ecosystem; trust; concise behavior; matched gap; commons overlap; license; visible security surface;
revision when available; and recommendation. State that discovery installed nothing, executed no external
code, and modified no commons capability. Candidate discovery never changes active project methodology;
review and explicit acceptance remain separate. Search permission is not installation permission.

Support granular answers such as one candidate, several candidates, none, deeper review of one result, or
methodology-only use. Review selected scripts, hooks, plugins, MCPs, dependencies, or other executable
surfaces for license and security before any installation or execution.

## Accepted external capabilities

Integrate only explicitly accepted findings and default their scope to the current project. Choose the
safest justified form: methodology only, independently implemented project-local skill, project-local agent,
reviewed external tool integration, or inspiration only. Do not copy unknown-license material or execute
unreviewed code. Prefer `INSPIRED-BY` or `INDEPENDENT-REIMPLEMENTATION` when practical.

Record compact provenance in `.agent-commons.yaml`: source repository, path, revision, license, trust,
relationship, integration type, review date, matched gap, and optional `future_commons_candidate`. Do not
store external source contents there. Acceptance for one project never modifies the canonical commons
library. Reusable experience may later flow through `review-for-commons`, generalization, evals, and an
explicit promotion decision.

For the project-local-later strategy, record unresolved gaps and add the early task: define and validate the
missing project-specific capabilities before deep analysis begins. For generic-only, record that no
validated technology-specific capability is available and never later claim specialist completeness
without evidence.

Preview first:

```bash
python3 scripts/initialize_project.py --root <project> --name <name> \
  --scope legacy-migration,development --scale standard \
  --runtime codex --runtime claude-code \
  --overlay evidence-traceability --html-artifact technical-dashboard \
  --source-technology SAS --target-technology Java \
  --capability-gap-strategy project-local-later \
  --goal <outcome> --done <acceptance-check> --dry-run
```

The deterministic script also accepts a natural-language brief and extracts explicit composition and
reference intent. For example:

```text
research + sales presentation about legacy modernization
Audience: CIO + enterprise architects
Desired outcome: approve a workshop
Brand: client
References:
- timeline-example.png for timeline structure, not colors
- cluster-example.png for cluster design
- example-deck.pdf for storytelling and density
```

A legacy example may be supplied directly as positional brief text or with `--brief`:

```text
legacy migration, SAS -> Java
source ../legacy-sas is read-only
extract requirements, prepare migration, and create a living analysis dashboard
```

This already selects legacy migration, the technology pair, read-only source policy, requirements,
migration preparation, and a dashboard. Ask for dashboard brand or audience only when they remain absent;
ask once for client-facing language when it remains absent; never repeat supplied facts.

An architecture example may request views directly:

```text
development project with architecture documentation
Need a component architecture, ER diagram, and login sequence diagram.
```

This selects the architecture-documentation overlay and the component, ER, and sequence conditions. Do
not ask whether those views are wanted.

Then run without `--dry-run` after reviewing the plan. Record known technologies, references,
deliverables, constraints, and validation with the repeatable flags shown by `--help`. Add `--no-git`
only when Git is explicitly undesired. Add `--initial-commit` only for a new repository after the
preview. The script refuses to overwrite files and will not initialize a nested repository.

Expected minimum output is context-dependent: shared `AGENTS.md`, `.agent-commons.yaml`, `README.md`,
`.gitignore`, and only justified runtime adapters or artifact paths. Claude Code receives a thin
`CLAUDE.md` import adapter; Codex, Cline, and OpenCode consume the shared `AGENTS.md` directly. Do not
create empty runtime directories or copy canonical workflows. Default `commons.agents` to empty;
delegation is a task-time decision, not scaffolding.

`AGENTS.md` is the project-governance handoff. `.agent-commons.yaml` records the resolved scope, stable
capability IDs, constraints, source boundaries, methodology, lifecycle state, and exact next action. It is
not native Codex or other runtime configuration and does not execute a capability automatically. The active
runtime exposes the installed canonical skill by stable ID; the user or `continue-project` explicitly invokes
that referenced workflow, whose source remains in Agent Commons rather than being copied into the project.

## Validate and hand off

- Confirm existing files are unchanged and created paths match the selected scope.
- Confirm `.agent-commons.yaml` records the small manifest version, library version/revision, scale, goal,
  done criteria, selected runtimes, archetypes, overlays, conditions, resolved skills/agents/tools/templates,
  intake mode, source/target/migration intent, per-source access and bounded discovery, dashboard purpose
  and audience, research and presentation settings, sales objective, artifact choice, brand source,
  client organization, sector confidence, country and locale, working language, separate dashboard and
  presentation languages/defaults/switches,
  structured project-local references, capability coverage/gaps, chosen resolution, and accepted external
  provenance without secrets or copied source contents.
- If Git was initialized, report the branch and status; do not create a remote.
- End every successful initialization with an explicit `NEXT ACTION` derived from the resolved archetype,
  methodology, scope, source state, and lifecycle stage. Include the exact canonical capability and subject
  when one exists, plus `continue-project` as the convenient fallback. Do not return only a generic
  completion statement or encourage unanchored coding.
- Persist the structured action in `.agent-commons.yaml` and dashboard data when selected so generated views
  and the initializer result use the same capability and subject.
- Persist `dashboard.template: canonical`, the canonical structure/template ID, visual-contract ID, and a
  blocking fallback policy. If those resources cannot be resolved, stop with a dashboard blocker rather than
  creating an improvised shell.
- Persist every canonical dashboard information domain with an explicit available, in-progress,
  not-yet-analyzed, not-applicable, or blocked state from initialization onward.
- Generated `AGENTS.md` must include the managed Git commit policy: meaningful subjects, no Conventional
  Commit prefixes, a reliable `[TICKET-ID]` prefix when present, and no co-author or agent-attribution trailers.
- Persist brand source/profile/theme/asset fingerprints and exact official favicon/logo hashes when a brand
  URL is supplied. Handoff must distinguish structural, static, profile-consistency, fidelity, and visual-QA
  results.
- Always create the selected dashboard or presentation `.html`. Missing or inaccessible branding selects the
  Accenture fallback and records the unresolved client-brand reason; it never produces only a branding blocker.
- Do not claim the project is designed or implemented by scaffolding alone.
