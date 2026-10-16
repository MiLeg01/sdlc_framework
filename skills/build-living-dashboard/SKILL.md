---
name: build-living-dashboard
description: Deterministically generate and synchronize a read-only project, technical, management, discovery, requirements, or migration dashboard from canonical state. Use when evolving canonical data needs a repeatable stakeholder view and drift check. Do not use for a one-off narrative presentation, as a lifecycle editor, or when no canonical input can be exported.
---

# Build a living dashboard

Treat the dashboard as a projection, never as a second database.

Agent Commons dashboards use the canonical information architecture declared in
`assets/dashboard-structure.json`. Instantiate that structure by default. Adapt project data, section applicability, project extensions,
branding, and language; do not invent a new section hierarchy, navigation model, overview, or detail
interaction for each project.

The canonical design language is independently fixed by `assets/dashboard-visual-contract.json`. It governs
layout proportions, spacing and density, typography scale, surface treatment, responsive behavior, the shared
detail dialog, and anti-drift rules. Project branding may change approved tokens and identity, but it must not
replace this product grammar. Do not introduce decorative gradients, glassmorphism, neon styling, excessive
rounded cards or pills, every-fact-as-card layouts, oversized empty hero regions, or generic SaaS-admin styling.

The visual contract implements a quiet technical-editorial thesis through a bounded content field, explicit
display/body/data type roles, section and component spacing tokens, flat record registers, ruled metrics and
tables, selective action surfaces, and one right-edge evidence drawer. Refine those shared tokens and components
instead of adding project-specific CSS fixes. The first generated render should already be client-ready in
structure and visually credible; a later polish pass should take good work to excellent, not rescue a rough UI.

## Define the contract

1. Name the audience and decisions the dashboard supports.
2. Identify canonical inputs, schemas, lifecycle meanings, unknown/initial states, and source timestamps.
3. Resolve each standard section as observed, not observed, pending, or not applicable. A full
   legacy-modernization dashboard renders every standard section in canonical order; important sections
   never disappear merely because data is absent.
4. When analysis is complete, export a meaningful executive package: findings, recommendation, readiness,
   options, controls, stakeholder questions, known unknowns, decisions, assumptions, estimate scenarios,
   roadmap, transition posture, interface implications, and risk gates. Completed analysis with empty
   executive regions fails semantic validation.
5. Keep large graphs bounded by search, capability, neighborhood, or depth. Surface truncation.
6. Treat acceptance-criterion ownership as lifecycle truth. When one specification serves multiple
   requirements, every criterion declares exactly one owning `requirement_id`; missing, conflicting, or
   ambiguous ownership fails validation. A single-requirement specification may omit it for compatibility.

## Canonical structure

The fixed navigation domains and standard sections are:

- Overview: evidence overview, executive decision brief, stakeholder questions and decisions, modernization.
- Business: capability atlas, requirements explorer, specifications explorer, application and business flows.
- Estate: repository/application/module inventory, database access/ownership/ER model.
- Architecture: interfaces, dependencies, external estate, application/system/C4 map.
- Assurance: progress and checkpoints, traceability, evidence explorer, test quality and modernization
  safety, questions/risks/uncertainty.

Within those stable groups, `assets/dashboard-structure.json` also defines the canonical information-domain
contract: management overview, system statistics/composition, complexity, ADM estimation, roadmap, inventory,
system landscape, component architecture, service topology, data/persistence and ERD, integrations, business
flows/rules, requirements, OpenSpec, traceability, legacy test quality, maintainability, target architecture,
risks/decisions, open questions, and evidence. Do not turn these into a separate tab each. Every domain keeps
its canonical location and one explicit state: `AVAILABLE`, `IN_PROGRESS`, `NOT_YET_ANALYZED`,
`NOT_APPLICABLE`, or `BLOCKED`.

`assets/dashboard-structure.json` also fixes the `test_quality_model` for the test-quality domain. Expose
test strength rather than only test execution: tests, coverage where available, mutation score, killed
mutants, surviving meaningful mutants, critical survivors, accepted equivalent mutants, mutation trend against
the last accepted baseline, and one test-quality status. Coverage answers whether code was executed; mutation
testing answers whether the tests would notice incorrect behavior, so never present coverage as a substitute
for mutation quality. When mutation testing applies but has not run, show `NOT_YET_ANALYZED`; when no
maintained engine exists for the technology, show `NOT_SUPPORTED` with the compensating verification; when the
baseline suite is unstable, show `BLOCKED_BY_FLAKY_TESTS`. Do not omit the information in any of those cases.

Management Overview carries only the aggregate test-quality status, critical survivor count, and trend.
Technical drill-down from test quality reaches module, changed-code scope, individual survivor, mutation
operator, linked requirement and specification, linked tests, and recommended action. Never place individual
mutants in Management Overview, and never aggregate application mutation results with Agent Commons
methodology mutation results; they are separate test systems.

The chrome contract also fixes a validation/data-integrity utility strip, an official-identity header with
project title, optional co-brand slot and accessible language switch, grouped desktop/mobile navigation,
and a footer with generation time plus canonical-state and source fingerprints. Exact section order and
required regions are defined in `assets/dashboard-structure.json`.

Use only the controlled extension points `after-overview`, `operational`, `business-domain`,
`architecture-domain`, and `appendix-evidence`. Project-specific sections must declare one of those points
through `dashboard.extensions[]`; they must not reorder canonical sections. Requirements, specifications,
evidence, and traceability use the shared filter/list-or-table/detail-dialog interaction family.

The first view always contains project context, current status, key findings, and next actions. Management
users receive decision posture, coverage, progress, risks, and next actions before technical details.
Technical users drill into the same product through canonical section navigation and the shared detail
dialog. When a core section has no data, show an honest pending state such as `Analysis in progress`.

For requirements/specification/delivery dashboards, read `references/dashboard-data-contract.md`. Copy the
synthetic `assets/dashboard-data.example.json` structure and export canonical project state into it. Then run:

```bash
python3 scripts/build_dashboard.py --data <canonical-export.json> --dashboard-mode full-legacy-modernization --output dashboard/index.html
python3 scripts/build_dashboard.py --data <canonical-export.json> --output dashboard/index.html --check
python3 scripts/validate_dashboard_structure.py --html dashboard/index.html
python3 scripts/validate_dashboard_semantics.py --data <canonical-export.json> [--peer-html presentation/index.html]
python3 scripts/validate_dashboard_visual.py --html dashboard/index.html --qa-manifest dashboard/visual-qa.json --require-qa
```

When client branding is required, first use the `create-branded-html-artifact` workflow to resolve its
evidence-derived version-2 brand profile and exact official favicon/logo assets, then add
`--brand-profile <brand-profile.json>` to both commands. The profile is presentation configuration rather
than lifecycle truth, but its normalized content and fingerprints participate in deterministic dashboard
generation and drift detection.

If branding is absent or profile resolution is blocked, unreadable, inaccessible, unsafe, or otherwise
invalid, generate `dashboard/index.html` with the bundled Accenture fallback. Preserve the requested brand
source and resolution failure in canonical project state, mark the rendered identity `accenture-fallback`,
and do not claim client-brand fidelity. Branding failure must never replace the HTML with a blocker file.

## Generation rules

Use L0 and memory indexes to locate the canonical structured records needed by enabled dashboard sections.
The renderer may consume a bounded dashboard context package for navigation and update speed, but every
displayed claim, count, relationship, and next action must still derive from canonical project state. If
memory and canonical data disagree, refresh memory rather than projecting the stale value.

- Validate canonical inputs first and fail on duplicate IDs, invalid links, impossible totals, or schema
  errors.
- Fail when an information domain is marked `AVAILABLE` without supporting canonical content. In completed
  full legacy-modernization mode, fail when the executive decision and modernization regions are materially
  empty.
- When a dashboard and presentation share headline facts, declare `dashboard.shared_claims[]` with canonical
  dashboard paths and visible peer markers, then run semantic validation with `--peer-html`; script/style-only
  markers do not count.
- Derive every count and status deterministically. Show unknown instead of inventing denominators.
- Derive the project, requirement, and specification `next_action` from structured lifecycle state. Render
  canonical capability IDs and stable subjects as copyable command references; never hard-code workflow
  commands in generated HTML or expose absolute workstation paths when a stable ID exists.
- Keep requirement approval, specification coverage/readiness, implementation, and validation as separate
  states. Derive missing-spec, unsupported-spec, uncovered-criterion, missing-test, and stale-spec warnings.
- Make requirements, specifications, acceptance criteria, implementation items, tests, and evidence
  openable, with relationship navigation and a bounded traceability view.
- Initially bound requirements, evidence, tests, and traceability. Show total, filtered, and visible counts,
  active filters, and an accessible show-more control. Do not paginate a small result set. Traceability also
  exposes bounded chain depth or neighborhood.
- Use progressive disclosure: management receives coverage, readiness, delivery, validation, decisions, and
  risks first; technical users can drill into source evidence, OpenSpec details, criteria, dependencies,
  implementation paths, and tests.
- Generate files atomically and make the UI visibly read-only.
- Reject unresolved, stale, incompletely evidenced, or unsafe input as client branding, then render the
  Accenture fallback instead. Never translate a supplied client URL into a generic `project` theme or claim
  that the fallback is the requested client identity.
- Validate distinct semantic roles for primary, secondary, highlight, identity, danger, success, focus, and
  header/navigation use. Logo-only or highlight-only colors do not become global chrome without usage
  evidence. Danger remains distinguishable from the global accent, including for valid red-primary brands.
- Fix canonical data or the generator, never hand-edit generated metrics.
- Use empty states that explain the missing prerequisite rather than sample production data.
- Canonical mode renders every standard section and information-domain slot. `dashboard.enabled_sections`
  remains a backward-compatible adaptive-mode control only; it must not be used to silently remove required
  domains from substantial dashboards. Full legacy-modernization mode applies the same complete structure.
- Treat `dashboard.extensions` as controlled project-specific insertions, not permission to redesign the
  information architecture.
- Treat the embedded dashboard design ID and fingerprint as required generation evidence. If the canonical
  structure, shell, visual contract, or renderer is missing or invalid, report a blocker; do not improvise a
  fallback dashboard and call it successful.
- Keep one renderer/refresher as the sole owner of `dashboard/`. Parallel analysis and requirement workers
  write structured isolated outputs only; they never rewrite generated HTML.
- Keep action controls read-only: copying a command is permitted, but the dashboard never runs it or mutates
  lifecycle state. Human labels follow the selected locale while canonical capability IDs remain unchanged.

## Browser verification

Serve locally and use `polish-html-artifact` when a dedicated visual-finesse correction pass is in scope, then
use the independent `validate-visual-artifact` workflow for final review. Generate the required state matrix with
`scripts/capture_dashboard_visual_qa.mjs`. At minimum inspect overview, decision brief, stakeholder questions,
modernization, requirements, specifications, application map, traceability, the detail opener, desktop, laptop,
mobile, mobile navigation, and mobile detail; for bilingual delivery, cover German and English states. Compare
whitespace, margins, content width, type
scale, density, navigation, borders, table/list treatment, grouping, and dialogs against the canonical product
rather than against client colors. Exercise filters, search, detail links, keyboard focus, empty/error/loading
states, responsive layouts, reduced motion, overflow, console health, and representative large datasets.

Record each required rendered state, viewport, locale, screenshot path, PASS/PARTIAL/FAIL result, and matching
HTML, design, canonical-data, and applicable brand fingerprints in `dashboard/visual-qa.json`. Final readiness
requires independent `STRUCTURE_PASS`, `STATIC_HTML_PASS`, `VISUAL_QA_PASS`, and `ACCESSIBILITY_PASS` results;
branded delivery additionally requires `BRAND_PROFILE_CONSISTENT` and `BRAND_FIDELITY_PASS`, and multilingual
delivery requires `LOCALIZATION_PASS` for every configured language. Profile consistency alone is never brand
fidelity. An unavailable browser or missing manifest yields `BLOCKED` or `PARTIAL`, never `VALIDATED`.
Fallback delivery requires validation of the Accenture fallback identity and an explicit unresolved
client-brand fidelity note; the dashboard HTML itself remains a required output.

For an existing dashboard, deliberately upgrade it by exporting its canonical data into the current data
contract, preserving or re-resolving its version-2 brand profile and localization policy, regenerating with
this skill, and running the structural, fidelity, and browser validators. Do not rewrite historical dashboards
automatically. After migration the
generated template, not the original reference, is the source of truth.

When client delivery requires German/English output, keep the canonical dashboard and generator English-first
unless earlier localization is explicitly useful, then run `localize-client-artifact` on the generated HTML.
Localization must remain a presentation-layer projection: do not fork canonical data, duplicate the dashboard,
or translate evidence identifiers. After the English dashboard changes, rerun localization freshness checks
before client delivery.

Before resolving client-facing language, inspect `.agent-commons.yaml` and current project context. A
`CONFIRMED` or `HIGH_CONFIDENCE` public-sector client with a resolved German locale automatically receives
one client-branded dashboard with that German locale selected initially and English available through the
standard state-preserving switch. For Austrian German (`de-AT`), that switch renders only the Austrian flag
(`🇦🇹`) and UK flag (`🇬🇧`)—never visible language words—and gives both controls explicit accessible language
names. This applies equally to new and existing projects. Explicit dashboard instructions override the
policy; do not reuse the separate sales-presentation language setting.

The dashboard export may carry a `delivery` projection with `languages`, `default_language`,
`language_switch`, and `storage_key`. Keep client-facing message data separate from lifecycle truth. Built-in
navigation and lifecycle terms use the shared localization runtime; project-specific titles, prose, findings,
risks, architecture descriptions, chart labels, diagram labels, tooltips, and accessibility labels must have
complete keyed translations before public-sector delivery.

Before rendering multilingual output, deterministically enumerate every human-readable rendered field,
including nested project objects, extension content, record detail, diagram labels, tooltips, and accessible
names. Require an exact source hash plus a non-empty, fresh, intentionally different translation for every
required client locale. Reject source text merely prefixed with a locale label such as `DE:` as a placeholder,
even though it is technically different. Keep technical IDs, paths, commands, URLs, hashes, and evidence coordinates unchanged.
Language switching preserves filters, pagination, open navigation and detail regions, diagram state, the active
detail record, and scroll position.

## Completion

Complete only when structural and semantic completeness validation pass, the applicable lifecycle-QA hard
gate is `VALIDATED`, `--check` detects no drift, totals
reconcile with canonical inputs, affected interactions work, and the handoff records generation time, matching
HTML/input/structure/design fingerprints, applicable brand fingerprints, localization coverage, limitations,
and next action. The generated HTML itself says lifecycle QA is pending until independent evidence exists.
