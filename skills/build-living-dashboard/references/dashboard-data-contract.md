# Requirements, OpenSpec, and delivery dashboard contract

Use schema version 2 for lifecycle dashboards. The canonical export contains:

- `requirements[]`: discovered or approved behavior with stable ID, revision, evidence, confidence, approval
  status, and separate implementation status;
- `specifications[]`: OpenSpec changes/specs with purpose, project-local source path, status, readiness,
  implementation status, dependencies, and the requirement revisions they consumed;
- `acceptance_criteria[]`: observable criteria with independent status and explicit `requirement_id` whenever
  their specification serves multiple requirements;
- `implementation_items[]`: slices or tasks with paths and delivery status;
- `tests[]`: stable tests or approved verification records with current result;
- `evidence[]`: source/evidence summaries and coordinates safe for the dashboard audience;
- `relationships[]`: typed links among the records.
- `workflow`: manifest-derived lifecycle scope such as archetypes, whether requirements and OpenSpec are
  required, implementation phase, source-inventory completeness, and unresolved project choices.

The generator derives one structured `next_action` for the project and each requirement/specification. An
action contains `capability`, optional stable `subject`, `required`, `status`, `label`, and `reason`; the UI
derives the copyable command from capability plus subject. Do not store a second hard-coded command string
in HTML. Multiple unfinished specifications produce concise choices when dependency and priority do not
determine one safe next item.

Client delivery is a projection, not lifecycle truth. An optional `delivery` object records supported
dashboard locales, initial locale, switch enablement, and the localStorage key. An optional localization
message map may supply keyed translations for project-specific titles, fields, findings, warnings, charts,
and diagrams. Technical IDs and relationship endpoints remain unchanged.

For multilingual delivery, `localization.messages` covers the generator's deterministic
`localization_coverage` inventory. Each message contains the exact English `source`, its `sha256:` source hash,
and non-empty translations for every configured client locale. Missing, stale, empty, unintentionally
identical, or locale-prefixed placeholder translations such as `DE: <source>` fail generation. Technical IDs,
paths, commands, URLs, hashes, and evidence coordinates are excluded from translation.

Dashboard structure is also a projection. The generator resolves the canonical structure from
`assets/dashboard-structure.json` and writes the resolved result to `dashboard_structure`. Input data may
use:

- `dashboard.profile`: `legacy-modernization`, `development`, `research`, or `general`;
- `dashboard.domain_states`: optional overrides keyed by canonical information-domain ID with `status`,
  `reason`, and `basis` (`MEASURED`, `ASSESSED`, `MIXED`, `UNKNOWN`, or `NOT_APPLICABLE`). The renderer fills
  every omitted domain deterministically and never removes its canonical slot;

- `dashboard.enabled_sections[]` to enable known conditional section IDs when scope is known before records
  exist;
- `dashboard.extensions[]` for project-specific sections at a declared controlled extension point;
- `dashboard.shared_claims[]` for optional parity checks against a peer artifact. Every claim has a unique
  `id`, one or more non-empty `dashboard_paths`, and one or more visible `peer_markers`. Run
  `validate_dashboard_semantics.py --peer-html <artifact.html>` when this field is present;
- `project` for objective, scope, status, findings, decisions, risks, next actions, architecture, inventory,
  flows, dependencies, validation, or other project-state summaries.

Do not hand-author `dashboard_structure`. Unknown section IDs, duplicate extension IDs, unsupported
extension points, or out-of-range extension order fail validation. Core sections remain present with honest
pending states when their project data is not yet available.

The visual product contract is also resolved, from `assets/dashboard-visual-contract.json`, and written to
`dashboard_visual_contract` with contract and design fingerprints. Do not hand-author it. The generated HTML
must pass `validate_dashboard_visual.py`; final delivery also supplies the required rendered-state QA manifest.

## Full-analysis projection

A legacy-analysis dashboard may include:

```json
{
  "analysis": {
    "mode": "CONTINUE",
    "target_mode": "FULL",
    "status": "IN-PROGRESS",
    "coverage": {"relevant": 77, "accounted": 52, "unaccounted": 25, "blocked": 0},
    "slices": {"validated": 6, "total": 9},
    "languages": ["COBOL", "PL/I", "Java", "OpenAPI/configuration"]
  }
}
```

Counts must reconcile. A `COMPLETE` state with nonzero unaccounted source is rejected, as is a project status
that says complete while coverage remains partial. Analysis coverage and slice metrics are derived ahead of
requirements/specification metrics so the overview cannot imply that the first analyzed flow is the system.
In `full-legacy-modernization` mode, a complete analysis also requires populated executive findings, decision
recommendation, readiness, option comparison, controls, stakeholder questions, known unknowns, decisions,
assumptions, estimate scenarios, roadmap, transition posture, data/interface implications, and risk gates.

Stable IDs are the primary dashboard interaction. Keep an OpenSpec `source` or `source_path` relative to the
project for technical detail and safe path resolution, but never expose irrelevant absolute workstation
paths in client-facing views.

For a public-sector client with resolved German geography, the normal projection is:

```json
{
  "delivery": {
    "languages": ["de-AT", "en"],
    "default_language": "de-AT",
    "language_switch": true,
    "storage_key": "project-dashboard-language"
  }
}
```

Use `de-DE` or `de-CH` when client geography establishes Germany or Switzerland. Explicit project
instructions override these defaults.

Supported relationship types are `specified-by`, `defines`, `implemented-by`, `validated-by`,
`supported-by`, and `depends-on`. IDs are globally unique so every relationship is navigable.

`defines` identifies the containing specification; criterion ownership identifies the requirement satisfied by
that criterion. A criterion must be defined by exactly one specification. If that specification has one linked
requirement, omitted ownership is inferred for backward compatibility. If it has multiple linked requirements,
`requirement_id` is mandatory and must name one of them. Conflicting, missing, or plural ownership fails instead
of expanding every linked requirement across every criterion.

## State boundaries

Do not collapse these states:

```text
requirement approval -> specification coverage -> implementation readiness
                     -> implementation progress -> validation result
```

Specification validation is `PASS`, `PARTIAL`, `FAIL`, or `BLOCKED`. A green test contributes only to the
acceptance criteria it links to. A requirement is specified only when a real relationship to a specification
exists.

## Staleness

An approved requirement should have a stable revision or content fingerprint. A linked specification records
that value in `requirement_revisions`. When they differ, the generator emits a stale-spec warning. Review the
specification semantically; do not update the consumed revision without confirming the contract remains valid.

## Projection rules

The generator derives metrics, reverse links, validation coverage, warnings, and semantic traceability chains
`Requirement -> Specification -> owned Criterion -> Implementation -> Test`. Do not
hand-maintain those facts in HTML. Use empty arrays and honest empty states when a lifecycle stage is out of
scope or has not started.

System statistics/composition may be `AVAILABLE` only with `MEASURED` deterministic inventory data. Complexity
may be measured, assessed, or mixed, but its basis must be explicit. Database-free, monolith, no-test,
analysis-only, and no-OpenSpec-yet systems keep their canonical domain slots and explain their
`NOT_APPLICABLE`, `AVAILABLE`, or `NOT_YET_ANALYZED` state.
Every domain marked `AVAILABLE` must also resolve to supporting canonical content; an explicit state override
cannot be used to make an empty region look complete.

`dashboard.registers` may override `initial_limit` for requirements, evidence, test quality, and traceability;
traceability may also set `max_depth` from 2 through 5. Defaults are 25 records for the flat registers and 50
chains at depth 5. The UI reports total, filtered, and visible counts, preserves active state across language
changes, and hides show-more when the complete result already fits.
