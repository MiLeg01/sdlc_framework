# Agent Commons v1.0.0 governance and dashboard hardening

This report records a refinement of the existing `v1.0.0` baseline. It is not a new release.

## 1–5. Commit governance

Canonical `AGENTS.md` now requires meaningful human-readable subjects, prohibits Conventional Commit type
prefixes, adds a conservative `[TICKET-ID]` prefix only when a reliable branch identifier exists, and
prohibits co-author and agent-attribution trailers. `tools/commit_policy.py` provides deterministic formatting
and validation. The regression suite covers main, ticket-branch, ambiguous-number, and trailer cases.

## 6–8. Initialization and external discovery

Previously, capability gaps produced a blocking decision or search handoff. Initialization now performs the
fast Commons coverage comparison immediately and starts `tools/run_external_discovery.py` as an independent
process for important partial or missing coverage, or for an explicit external-research request. Project
instructions, manifest, source inventory, branding work, and dashboard generation remain on the core path.

Discovery uses the configured source registry, focused privacy-safe queries, bounded concurrency, shallow
metadata inspection, deduplication, revision-aware candidates, bounded exponential backoff, and the
Commons-owned `external/cache/search/` cache with a 30-minute default TTL. Project state records `running`,
`completed`, or `partial`, including rate-limit failures. Discovery never installs, executes, accepts, or
promotes a candidate.

## 9–12. Canonical dashboard contract and state model

The existing five-group product structure remains canonical: Overview, Business, Estate, Architecture, and
Assurance. A machine-readable information-domain layer now maps the required management, analysis,
architecture, requirements, delivery, quality, and evidence concerns into those groups without creating a
large tab set.

Every domain has one stable location and one state: `AVAILABLE`, `IN_PROGRESS`, `NOT_YET_ANALYZED`,
`NOT_APPLICABLE`, or `BLOCKED`. The initialized dashboard uses the same structure as later analysis; pending
work changes state and data, not navigation. The renderer remains the single writer of `dashboard/`.

## 13–18. Quantitative, complexity, estimation, roadmap, inventory, and data behavior

System composition is available only from `MEASURED` deterministic inventory data. Complexity records a
`MEASURED`, `ASSESSED`, or `MIXED` basis. ADM estimation and roadmap retain canonical slots before execution.
Inventory remains technology-neutral at the contract level and supports language-specific records from
COBOL, PL/I, Java, SQL, frontend, and other workers. Data and persistence remain visible for database-free
systems; the ER model becomes `NOT_APPLICABLE` with an explicit no-relational-schema reason.

## 19–22. Diagrams, requirements/OpenSpec, test quality, and open questions

System landscape, component architecture, service topology, ERD, integrations, and target architecture map to
stable dashboard domains backed by the existing diagram capabilities. A monolith remains a monolith; missing
diagram evidence stays pending. Requirements, OpenSpec, and traceability remain directly linked. Specifications
can be `NOT_YET_ANALYZED` without disappearing. Legacy test quality remains visible even when zero tests exist,
and open questions retain a first-class state and location.

## 23. Semantic completeness validation

`validate_dashboard_semantics.py` independently checks the complete domain set, canonical order and placement,
valid states, state reasons, and measured/assessed basis. `validate_dashboard_structure.py` also verifies that
every resolved domain is rendered exactly once in its canonical section.

## 24–25. Benchmarks and evaluations

The executable suites cover automatic discovery, explicit search without reconfirmation, slow GitHub,
rate-limit classification, cache reuse, candidate non-installation, commit-message policy, initialized-domain
states, mixed-language composition, database-free persistence, monolith topology, no tests, no OpenSpec yet,
and missing-domain rejection. Final command results are recorded in the completion section after the full gate.

## 26. Version verification

`VERSION`, changelog, README, installer metadata, presentation data, catalogs, and generated surfaces remain
`1.0.0` / `v1.0.0`. No version increment or new release entry is introduced.

## Completion evidence

Validation completed on 20 August 2026:

- `python3 tools/validate_commons.py`: 46 skills, 4 agents, 0 errors, 0 warnings.
- Runtime adapters, archetypes, capability expectations, and external source/index validation: pass.
- Modified skill packages: four of four pass the canonical skill validator.
- Python compilation and `git diff --check`: pass.
- Complete evaluation matrix: 332 tests pass, including 52 installation/archetype, 81 initialization,
  84 dashboard and supporting tool, and 115 remaining tool/external tests.
- Presentation data synchronization, visual-contract check, and static HTML validation: pass with zero errors
  and zero warnings.
- Browser QA at 1440x900, 1024x768, and 390x844: no clipping or horizontal overflow; keyboard focus remains
  visible; console inspection reports no warnings or errors.
- `VERSION` and release surfaces remain `1.0.0` / `v1.0.0`; no later-version marker is present.

The final commit and clean-worktree check are recorded in Git rather than duplicated as mutable report text.
