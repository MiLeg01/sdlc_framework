# Changelog

## v1.3.0

- Added legacy oracle-authority and readiness gates to `design-test-strategy`, separating approved intent,
  observed source behavior, unresolved outcomes, characterization, scenario-only drafts, review blockers, and
  execution evidence.
- Added an optional reference-application contract to `analyze-legacy-system`: fingerprinted reference
  patterns may prioritize target discovery, while target matches, non-matches, contradictions, evidence,
  metrics, and completeness remain independently established from target sources.
- Added deterministic and semantic evaluation coverage for both evidence-authority boundaries and updated the
  legacy-migration composition guidance.

## v1.2.0

- Added runtime-neutral `manage-project-delivery` and `forecast-project-financials` skills with deterministic
  delivery-register analysis and project-forecast calculation tools, synthetic templates, behavioral
  evaluations, and an independent `financial-forecast-reviewer` agent.
- Added the optional `consulting-delivery` overlay for development, legacy-migration, and research projects.
  Organization-specific terminology, branding, rate cards, commercial thresholds, approval routes, and client
  identifiers remain project-local so the canonical capabilities stay reusable across harnesses and firms.
- Recorded revision-pinned, license-aware external reviews for the finance-pack and open-sdlc-skills sources;
  the promoted work is an `INSPIRED-BY` reimplementation and does not execute or vendor external code.

## v1.1.0

- Added the `mutation-testing` skill: application mutation testing as a first-class test-quality capability.
  It evaluates whether a test suite would detect defective implementation behavior, scopes mutation by
  lifecycle profile and criticality, classifies every surviving mutant against the approved specification,
  and drives behavioral test hardening. Statuses are derived deterministically, a critical surviving mutant
  fails regardless of aggregate score, an unsupported technology reports `NOT_SUPPORTED` rather than passing,
  and an unstable baseline blocks instead of scoring. `test-driven-development` now delegates the mutation
  quality check after GREEN and REFACTOR, and implementation orchestration, verification, traceability, the
  dashboard test-quality domain, project memory, and both archetypes consume the result. Kept distinct from
  the existing Commons methodology mutation testing under `evals/mutations/`, which now also protects this
  capability against silent weakening.
- Added the `validate-work-item-assumptions` skill: a read-only check of whether a previously filed work
  item's claims about current system state still hold, returning confirmed, changed, and unverified claims
  plus one materiality verdict, with the proceed decision left to the caller.
- Added the `generate-synthetic-fixtures` skill: build committed test fixtures by generating them from a
  reviewed allowlist specification rather than scrubbing sensitive originals, so the specification is the
  audit surface instead of a rendered artifact nobody can audit for what is missing. Load-bearing signal is
  kept and justified by the test that needs it, renderers are pure functions of the specification, and
  identifier detectors act as assertions over output rather than as the transformation. Reproducibility,
  determinism, unapproved-identifier, declared-parity, and signal-presence checks run as ordinary tests.
- Added the `deconstruct-problem-first-principles` skill: a pre-planning check that the problem was framed
  correctly. It separates known facts from inherited framing, restates the problem plainly, names the
  violated invariant or unstated constraint behind it, inverts to find every other site that constraint
  reaches, and requires an explicit recorded choice between intervening at the symptom, the root cause, or
  the structure that permitted the problem. Analysis only; the plan stays with `plan-work`.

## v1.0.0

Initial stable release of Agent Commons.

- Runtime-neutral skills, specialist agents, deterministic tools, templates, and composition metadata.
- Adaptive project initialization and lifecycle continuation.
- Evidence-first legacy modernization with requirements, OpenSpec, TDD, and traceability workflows.
- Living dashboards, technical diagrams, branded HTML artifacts, localization, and presentation support.
- Safe parallel coordination, privacy and security review, Git protection, and consequential-change controls.
- Codex, Claude Code, Cline, and OpenCode adapters with cross-platform installation and verification.
- Governed internal and external capability review with licensing, security, and evaluation gates.
