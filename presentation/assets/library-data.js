// AUTO-GENERATED. DO NOT EDIT DIRECTLY.
// Run: python3 tools/refresh_commons_presentation.py
window.AGENT_COMMONS_DATA = {
  "schema_version": 2,
  "library_version": "1.3.0",
  "stats": {
    "skills": 52,
    "agents": 5,
    "tools": 35,
    "templates": 17,
    "archetypes": 4,
    "overlays": 9,
    "adapters": 4,
    "evals": 6,
    "external": 10,
    "relationships": 583,
    "external_sources": 8,
    "external_candidates": 2,
    "test_files": 47
  },
  "nodes": [
    {
      "key": "skill:accessibility-review",
      "id": "accessibility-review",
      "name": "Accessibility Review",
      "type": "skill",
      "path": "skills/accessibility-review/SKILL.md",
      "description": "Independently review a completed interface or artifact for accessibility through automated checks, keyboard journeys, focus behavior, reflow, contrast, motion, semantics, and assistive-technology evidence, then prioritize and retest findings. Use before consequential UI acceptance or release. Do not use to invent the initial design, replace user research or formal conformance certification, or claim accessibility from visual inspection alone.",
      "purpose": "Independently review a completed interface or artifact for accessibility through automated checks, keyboard journeys, focus behavior, reflow, contrast, motion, semantics, and assistive-technology evidence, then prioritize and retest findings",
      "use_when": [
        "before consequential UI acceptance or release"
      ],
      "not_when": [
        "to invent the initial design, replace user research or formal conformance certification, or claim accessibility from visual inspection alone"
      ],
      "inputs": [],
      "workflow": [
        "Build the review matrix",
        "Execute and record",
        "Retest"
      ],
      "outputs": [],
      "validation": [],
      "tags": [
        "accessibility-validation"
      ],
      "search_terms": [
        "Accessibility Review",
        "accessibility-review",
        "accessibility-validation"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: accessibility-review\ndescription: Independently review a completed interface or artifact for accessibility through automated checks, keyboard journeys, focus behavior, reflow, contrast, motion, semantics, and assistive-technology evidence, then prioritize and retest findings. Use before consequential UI acceptance or release. Do not use to invent the initial design, replace user research or formal conformance certification, or claim accessibility from visual inspection alone.\n---\n\n# Review accessibility\n\nDefine the artifact, routes, states, representative viewports, supported input modes, target standard,\nand known exclusions before testing. Prefer a fresh reviewer when the implementation is consequential.\n\n## Build the review matrix\n\nCover each primary journey and state across:\n\n- automated semantic and rule-based scanning;\n- keyboard-only traversal, activation, escape, and visible focus;\n- focus order, focus restoration, dialogs, errors, and dynamic updates;\n- zoom, text spacing, narrow reflow, orientation, and content clipping;\n- foreground, non-text, focus-indicator, and state contrast;\n- reduced motion, animation control, time limits, and flashing risk;\n- names, roles, states, landmarks, headings, labels, instructions, and error association;\n- representative screen-reader or accessibility-tree inspection where the environment supports it.\n\n## Execute and record\n\n1. Establish a known working baseline and capture tool, browser, platform, and viewport details.\n2. Exercise real journeys instead of scanning only the initial page.\n3. Record each finding with a stable ID, affected state, reproduction, expected behavior, observed\n   behavior, evidence, impact, standard mapping when known, confidence, and severity.\n4. Separate confirmed defects, likely defects needing assistive validation, tooling limitations, and\n   advisory improvements. Never convert an unavailable test into a pass.\n5. Rank by user impact and journey blockage, not by tool count.\n\n## Retest\n\nRetest the exact reproduction after correction, then run a bounded regression across related states and\ninput modes. Report PASS, PASS_WITH_LIMITATIONS, or FAIL with unresolved findings and inaccessible test\nsurfaces. Visual QA and accessibility review may share evidence, but neither substitutes for the other.\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "eval:skill-evaluations",
        "overlay:living-dashboard",
        "overlay:public-sector-client-delivery",
        "skill:polish-html-artifact"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "skill:analyze-legacy-system",
      "id": "analyze-legacy-system",
      "name": "Analyze Legacy System",
      "type": "skill",
      "path": "skills/analyze-legacy-system/SKILL.md",
      "description": "Orchestrate complete configured evidence-first legacy analysis by default, using inventory-backed bounded slices, safe parallel fan-out, cross-system synthesis, requirements, selected OpenSpec preparation, dashboard refresh, and a hard coverage gate. Use as the high-level entry point for initialized legacy projects; use bounded mode only when the user explicitly limits scope. Do not use for target-state invention, implementation, or analysis based only on filenames, comments, or memory.",
      "purpose": "Orchestrate complete configured evidence-first legacy analysis by default, using inventory-backed bounded slices, safe parallel fan-out, cross-system synthesis, requirements, selected OpenSpec preparation, dashboard refresh, and a hard coverage gate",
      "use_when": [
        "as the high-level entry point for initialized legacy projects; use bounded mode only when the user explicitly limits scope"
      ],
      "not_when": [
        "for target-state invention, implementation, or analysis based only on filenames, comments, or memory"
      ],
      "inputs": [],
      "workflow": [
        "Enter from an initialized project",
        "Resolve mode and complete scope",
        "Keep reference applications outside target truth",
        "Establish one denominator and coordinator state",
        "Execute bounded slices",
        "Mandatory fan-in",
        "Dashboard ownership and progress",
        "Completion gate"
      ],
      "outputs": [],
      "validation": [],
      "tags": [
        "analyze legacy system",
        "bounded analysis",
        "business-rule-extraction",
        "complete-legacy-system-analysis",
        "continue analysis",
        "coverage register",
        "cross-system synthesis",
        "dependency-analysis",
        "discovery prior",
        "full analysis",
        "legacy-semantic-analysis",
        "migration-boundary-analysis",
        "reference application",
        "reference profile",
        "reference-application-discovery-priors",
        "reference-target-evidence-isolation",
        "resumable-analysis-coverage",
        "technology:cobol:source-semantic-analysis",
        "technology:legacy-java:source-semantic-analysis",
        "technology:pli:source-semantic-analysis"
      ],
      "search_terms": [
        "Analyze Legacy System",
        "analyze legacy system",
        "analyze-legacy-system",
        "bounded analysis",
        "business-rule-extraction",
        "complete-legacy-system-analysis",
        "continue analysis",
        "coverage register",
        "cross-system synthesis",
        "dependency-analysis",
        "discovery prior",
        "full analysis",
        "legacy-semantic-analysis",
        "migration-boundary-analysis",
        "reference application",
        "reference profile",
        "reference-application-discovery-priors",
        "reference-target-evidence-isolation",
        "resumable-analysis-coverage",
        "technology:cobol:source-semantic-analysis",
        "technology:legacy-java:source-semantic-analysis",
        "technology:pli:source-semantic-analysis"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: analyze-legacy-system\ndescription: Orchestrate complete configured evidence-first legacy analysis by default, using inventory-backed bounded slices, safe parallel fan-out, cross-system synthesis, requirements, selected OpenSpec preparation, dashboard refresh, and a hard coverage gate. Use as the high-level entry point for initialized legacy projects; use bounded mode only when the user explicitly limits scope. Do not use for target-state invention, implementation, or analysis based only on filenames, comments, or memory.\n---\n\n# Analyze a legacy system\n\nReconstruct observable behavior from exact source evidence. This skill is the system-level coordinator. A\nbounded slice is an internal execution unit, not the default completion boundary.\n\n## Enter from an initialized project\n\nThe user invokes the stable canonical capability ID through the active runtime; `.agent-commons.yaml` does\nnot execute automatically and is not native runtime configuration. Before planning analysis, read the\nproject-local `AGENTS.md`, `.agent-commons.yaml`, canonical structured state, protected source boundaries,\nand the minimum relevant project memory. Treat the skill body as the orchestration contract and the manifest\nas project-specific configuration for scope, selected capabilities, constraints, methodology, outputs, and\nthe current next action. Keep all source evidence and lifecycle state inside the project.\n\n## Resolve mode and complete scope\n\nRead project governance, `.agent-commons.yaml`, canonical state, source-authority rules, protected paths, and\nthe user request. When project memory is enabled, load L0 and the index first, validate the current inventory\nfingerprint, reuse unchanged validated slices, and retrieve only the domains/entities needed for stale or\nmissing work. Read `references/full-analysis-contract.md`.\n\n- `FULL` is the default when the user invokes this skill without an explicit limitation. Resolve every\n  configured source root and analyze all eligible in-scope artifacts.\n- `BOUNDED` is permitted only when the user explicitly names a subset, path, component, technology, flow,\n  or entry point. Report bounded completion without implying system completion.\n- `CONTINUE` resumes an interrupted `FULL` or `BOUNDED` run from validated checkpoint state. Reuse unchanged\n… preview truncated",
      "related_capabilities": [
        "archetype:legacy-migration",
        "eval:skill-evaluations",
        "skill:audit-delivery-traceability",
        "skill:build-living-dashboard",
        "skill:continue-project",
        "skill:coordinate-parallel-agents",
        "skill:create-class-diagram",
        "skill:create-component-architecture-diagram",
        "skill:create-data-flow-diagram",
        "skill:create-er-diagram",
        "skill:create-sequence-diagram",
        "skill:create-system-landscape-diagram",
        "skill:derive-modernization-requirements",
        "skill:inventory-codebase",
        "skill:maintain-project-memory",
        "skill:migrate-code-with-evidence",
        "tool:coordinate-legacy-analysis",
        "tool:extract-legacy-structure"
      ],
      "archetypes": [
        "legacy-migration"
      ]
    },
    {
      "key": "skill:anonymize-data",
      "id": "anonymize-data",
      "name": "Anonymize Data",
      "type": "skill",
      "path": "skills/anonymize-data/SKILL.md",
      "description": "Design and apply bounded, configurable data anonymization or pseudonymization with field-scoped rules, deterministic local transforms, leakage-safe reports, and explicit residual-risk validation. Use before sharing structured sensitive data across a trust boundary. Do not use to claim legal anonymization, infer unknown identifiers from free text, or replace privacy review and data-minimization decisions.",
      "purpose": "Design and apply bounded, configurable data anonymization or pseudonymization with field-scoped rules, deterministic local transforms, leakage-safe reports, and explicit residual-risk validation",
      "use_when": [
        "before sharing structured sensitive data across a trust boundary"
      ],
      "not_when": [
        "to claim legal anonymization, infer unknown identifiers from free text, or replace privacy review and data-minimization decisions"
      ],
      "inputs": [],
      "workflow": [
        "Define the protection contract",
        "Execute locally and fail closed",
        "Verify the boundary"
      ],
      "outputs": [],
      "validation": [],
      "tags": [
        "deterministic-pseudonymization",
        "structured-data-anonymization"
      ],
      "search_terms": [
        "Anonymize Data",
        "anonymize-data",
        "deterministic-pseudonymization",
        "structured-data-anonymization"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: anonymize-data\ndescription: Design and apply bounded, configurable data anonymization or pseudonymization with field-scoped rules, deterministic local transforms, leakage-safe reports, and explicit residual-risk validation. Use before sharing structured sensitive data across a trust boundary. Do not use to claim legal anonymization, infer unknown identifiers from free text, or replace privacy review and data-minimization decisions.\n---\n\n# Anonymize data safely\n\nEstablish the authorized purpose, recipients, trust boundary, data classes, acceptable analytical utility,\nretention, reversibility needs, and attack model. Minimize or exclude data before transforming it.\n\n## Define the protection contract\n\n1. Inventory the bounded input and classify direct identifiers, quasi-identifiers, sensitive attributes,\n   linkage keys, free text, and fields that must retain analytical meaning.\n2. Choose terminology honestly. Removal or irreversible aggregation may support anonymization; stable tokens\n   and mapping-backed restoration are pseudonymization and remain personal-data controls in many contexts.\n3. Define exact field selectors and one strategy per field: drop, fixed redaction, or keyed stable token.\n   Do not detect people from capitalization, broad heuristics, or unreviewed regular expressions.\n4. Set required rules for identifiers that must be present and protected. Define false-positive fixtures,\n   multilingual examples, duplicates, aliases, empty values, and nested records.\n5. Keep keys and optional restoration maps outside source, configuration, logs, reports, fixtures, and\n   generated artifacts. Use separate access and retention controls for reversible mappings.\n\nUse `references/rule-contract.md` for the portable configuration and validation contract.\n\n## Execute locally and fail closed\n\nFor JSON, JSONL, NDJSON, or CSV, use `scripts/anonymize_data.py` against a copy or isolated output path.\nRun `--dry-run` first, inspect match counts and digests, then write the transformed output. Stable tokens\nrequire a separately supplied key file. The report contains counts and hashes, never matched source values.\n\nStop when required rules do not match, formats are malformed, field ownership is ambiguous, output would\noverwrite input, a key is missing, or validation cannot inspect the complete outbound payload. Unsupported\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "eval:skill-evaluations",
        "skill:generate-synthetic-fixtures",
        "skill:review-privacy-security",
        "tool:anonymize-structured-data"
      ],
      "archetypes": [
        "development"
      ]
    },
    {
      "key": "skill:audit-delivery-traceability",
      "id": "audit-delivery-traceability",
      "name": "Audit Delivery Traceability",
      "type": "skill",
      "path": "skills/audit-delivery-traceability/SKILL.md",
      "description": "Independently and read-only audit forward and reverse traceability from source through evidence, requirements, specifications, scenarios, implementation, tests, verification, and commits. Use before consequential completion, handoff, reporting, migration acceptance, or completeness claims. Do not use to repair findings, implement missing work, or treat a generated dashboard as canonical evidence.",
      "purpose": "Independently and read-only audit forward and reverse traceability from source through evidence, requirements, specifications, scenarios, implementation, tests, verification, and commits",
      "use_when": [
        "before consequential completion, handoff, reporting, migration acceptance, or completeness claims"
      ],
      "not_when": [
        "to repair findings, implement missing work, or treat a generated dashboard as canonical evidence"
      ],
      "inputs": [],
      "workflow": [
        "Contract",
        "Procedure",
        "Severity"
      ],
      "outputs": [],
      "validation": [],
      "tags": [
        "acceptance-verification",
        "evidence-traceability",
        "migration-validation"
      ],
      "search_terms": [
        "acceptance-verification",
        "Audit Delivery Traceability",
        "audit-delivery-traceability",
        "evidence-traceability",
        "migration-validation"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: audit-delivery-traceability\ndescription: Independently and read-only audit forward and reverse traceability from source through evidence, requirements, specifications, scenarios, implementation, tests, verification, and commits. Use before consequential completion, handoff, reporting, migration acceptance, or completeness claims. Do not use to repair findings, implement missing work, or treat a generated dashboard as canonical evidence.\n---\n\n# Audit delivery traceability\n\nAudit and report; do not silently repair canonical state or implementation.\n\n## Contract\n\nUse the chain, graph contract, and severity rules in `references/traceability-contract.md`.\n\nIf the project exports a flat trace matrix, run:\n\n```bash\npython3 scripts/audit_trace_matrix.py \u003ctrace.csv> --format markdown\n```\n\nIf the project exports normalized registries as a graph, run:\n\n```bash\npython3 scripts/audit_trace_graph.py \u003ctrace-graph.json> --format markdown\n```\n\nThe helpers check structural integrity only. Continue the semantic audit even when they pass.\n\n## Procedure\n\n1. Confirm the authoritative registries, schemas, source hashes, Git state, and audit scope.\n2. Recompute applicable inventory/disposition coverage and validate stable IDs, enums, references,\n   reciprocal links, lifecycle rules, coordinates, hashes, generated-view fingerprints, and non-overlapping\n   ownership.\n3. Walk the delivery chain in both directions. Do not infer coverage from similar names, aggregate test\n   passes, generated totals, or implementation presence alone.\n4. Where a `mutation` link is recorded, report a surviving mutant against an in-scope criterion as a\n   test-quality finding rather than treating the chain as unlinked. Coverage and a green result are not\n   evidence that a test would detect incorrect behavior.\n5. Verify that implemented behavior has approved scenarios, tests map to scenarios, results identify a\n   reproducible command/environment, verification is independent where required, and completion points\n   to a relevant commit or immutable artifact.\n6. Reconcile canonical totals with generated reports and dashboards. Fix recommendations must target\n   canonical data or generators, never generated output.\n7. Return `PASS`, `PASS_WITH_LIMITATIONS`, or `FAIL` with stable finding IDs, severity, broken link,\n   evidence, impact, and smallest remediation.\n\n## Severity\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:research",
        "eval:skill-evaluations",
        "overlay:evidence-traceability",
        "skill:analyze-legacy-system",
        "skill:build-living-dashboard",
        "skill:manage-project-delivery",
        "skill:verify-openspec-implementation",
        "tool:audit-trace-graph",
        "tool:audit-trace-matrix"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "research"
      ]
    },
    {
      "key": "skill:build-living-dashboard",
      "id": "build-living-dashboard",
      "name": "Build Living Dashboard",
      "type": "skill",
      "path": "skills/build-living-dashboard/SKILL.md",
      "description": "Deterministically generate and synchronize a read-only project, technical, management, discovery, requirements, or migration dashboard from canonical state. Use when evolving canonical data needs a repeatable stakeholder view and drift check. Do not use for a one-off narrative presentation, as a lifecycle editor, or when no canonical input can be exported.",
      "purpose": "Deterministically generate and synchronize a read-only project, technical, management, discovery, requirements, or migration dashboard from canonical state",
      "use_when": [
        "when evolving canonical data needs a repeatable stakeholder view and drift check"
      ],
      "not_when": [
        "for a one-off narrative presentation, as a lifecycle editor, or when no canonical input can be exported"
      ],
      "inputs": [],
      "workflow": [
        "Define the contract",
        "Canonical structure",
        "Generation rules",
        "Browser verification",
        "Completion"
      ],
      "outputs": [],
      "validation": [],
      "tags": [
        "English",
        "German",
        "accessibility gate",
        "bounded-large-registers",
        "brand roles",
        "canonical structure",
        "canonical-dashboard-design-language",
        "canonical-dashboard-information-domains",
        "canonical-dashboard-structure",
        "dashboard",
        "dashboard-domain-state-model",
        "de-AT",
        "de-CH",
        "de-DE",
        "deterministic-localization-coverage",
        "information architecture",
        "information domains",
        "language switch",
        "lifecycle-dashboard-qa-gate",
        "locale-aware-public-sector-dashboard",
        "localization coverage",
        "navigation",
        "not applicable",
        "owned-criterion-traceability",
        "pagination",
        "pending",
        "public sector",
        "rendered-dashboard-visual-validation",
        "requirements-dashboard",
        "semantic completeness",
        "semantic-brand-role-validation",
        "semantic-dashboard-completeness-validation",
        "specifications-dashboard",
        "stale-specification-detection",
        "structural-dashboard-validation",
        "traceability ownership"
      ],
      "search_terms": [
        "accessibility gate",
        "bounded-large-registers",
        "brand roles",
        "Build Living Dashboard",
        "build-living-dashboard",
        "canonical structure",
        "canonical-dashboard-design-language",
        "canonical-dashboard-information-domains",
        "canonical-dashboard-structure",
        "dashboard",
        "dashboard-domain-state-model",
        "de-AT",
        "de-CH",
        "de-DE",
        "deterministic-localization-coverage",
        "English",
        "German",
        "information architecture",
        "information domains",
        "language switch",
        "lifecycle-dashboard-qa-gate",
        "locale-aware-public-sector-dashboard",
        "localization coverage",
        "navigation",
        "not applicable",
        "owned-criterion-traceability",
        "pagination",
        "pending",
        "public sector",
        "rendered-dashboard-visual-validation",
        "requirements-dashboard",
        "semantic completeness",
        "semantic-brand-role-validation",
        "semantic-dashboard-completeness-validation",
        "specifications-dashboard",
        "stale-specification-detection",
        "structural-dashboard-validation",
        "traceability ownership"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: build-living-dashboard\ndescription: Deterministically generate and synchronize a read-only project, technical, management, discovery, requirements, or migration dashboard from canonical state. Use when evolving canonical data needs a repeatable stakeholder view and drift check. Do not use for a one-off narrative presentation, as a lifecycle editor, or when no canonical input can be exported.\n---\n\n# Build a living dashboard\n\nTreat the dashboard as a projection, never as a second database.\n\nAgent Commons dashboards use the canonical information architecture declared in\n`assets/dashboard-structure.json`. Instantiate that structure by default. Adapt project data, section applicability, project extensions,\nbranding, and language; do not invent a new section hierarchy, navigation model, overview, or detail\ninteraction for each project.\n\nThe canonical design language is independently fixed by `assets/dashboard-visual-contract.json`. It governs\nlayout proportions, spacing and density, typography scale, surface treatment, responsive behavior, the shared\ndetail dialog, and anti-drift rules. Project branding may change approved tokens and identity, but it must not\nreplace this product grammar. Do not introduce decorative gradients, glassmorphism, neon styling, excessive\nrounded cards or pills, every-fact-as-card layouts, oversized empty hero regions, or generic SaaS-admin styling.\n\nThe visual contract implements a quiet technical-editorial thesis through a bounded content field, explicit\ndisplay/body/data type roles, section and component spacing tokens, flat record registers, ruled metrics and\ntables, selective action surfaces, and one right-edge evidence drawer. Refine those shared tokens and components\ninstead of adding project-specific CSS fixes. The first generated render should already be client-ready in\nstructure and visually credible; a later polish pass should take good work to excellent, not rescue a rough UI.\n\n## Define the contract\n\n1. Name the audience and decisions the dashboard supports.\n2. Identify canonical inputs, schemas, lifecycle meanings, unknown/initial states, and source timestamps.\n3. Resolve each standard section as observed, not observed, pending, or not applicable. A full\n   legacy-modernization dashboard renders every standard section in canonical order; important sections\n   never disappear merely because data is absent.\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "eval:skill-evaluations",
        "overlay:living-dashboard",
        "skill:analyze-legacy-system",
        "skill:audit-delivery-traceability",
        "skill:continue-project",
        "skill:create-technical-diagram",
        "skill:derive-modernization-requirements",
        "skill:localize-client-artifact",
        "skill:mutation-testing",
        "skill:polish-html-artifact",
        "skill:specify-openspec-change",
        "skill:validate-visual-artifact",
        "skill:verify-openspec-implementation",
        "tool:build-dashboard",
        "tool:validate-dashboard-semantics",
        "tool:validate-dashboard-structure",
        "tool:validate-dashboard-visual"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "skill:complete-openspec-change",
      "id": "complete-openspec-change",
      "name": "Complete OpenSpec Change",
      "type": "skill",
      "path": "skills/complete-openspec-change/SKILL.md",
      "description": "Safely complete and archive one verified OpenSpec change, merging or deliberately skipping spec deltas and confirming the archived state. Use only after implementation verification proves the change ready to close. Do not use with incomplete tasks, unresolved spec or code mismatches, failing required gates, ambiguous change selection, or research and presentation work without an OpenSpec software change.",
      "purpose": "Safely complete and archive one verified OpenSpec change, merging or deliberately skipping spec deltas and confirming the archived state",
      "use_when": [
        "only after implementation verification proves the change ready to close"
      ],
      "not_when": [
        "with incomplete tasks, unresolved spec or code mismatches, failing required gates, ambiguous change selection, or research and presentation work without an OpenSpec software change"
      ],
      "inputs": [
        "verified active OpenSpec change",
        "completed tasks and validation evidence",
        "archive authorization"
      ],
      "workflow": [
        "Prove closure readiness",
        "Complete the lifecycle",
        "Return closure evidence"
      ],
      "outputs": [
        "archived OpenSpec change",
        "updated or intentionally skipped main specs",
        "closure evidence"
      ],
      "validation": [],
      "tags": [
        "OpenSpec",
        "archive",
        "change proposal",
        "close change",
        "openspec-archive-validation",
        "openspec-change-completion",
        "spec-driven",
        "spec-first",
        "specification"
      ],
      "search_terms": [
        "archive",
        "change proposal",
        "close change",
        "Complete OpenSpec Change",
        "complete-openspec-change",
        "OpenSpec",
        "openspec-archive-validation",
        "openspec-change-completion",
        "spec-driven",
        "spec-first",
        "specification"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: complete-openspec-change\ndescription: Safely complete and archive one verified OpenSpec change, merging or deliberately skipping spec deltas and confirming the archived state. Use only after implementation verification proves the change ready to close. Do not use with incomplete tasks, unresolved spec or code mismatches, failing required gates, ambiguous change selection, or research and presentation work without an OpenSpec software change.\n---\n\n# Complete an OpenSpec change\n\nArchive is a lifecycle mutation: it updates the main specs when applicable and moves the active change into\nhistory. Do not use OpenSpec's warning-tolerant archive behavior as permission to close incomplete work.\n\n## Prove closure readiness\n\n1. Resolve the exact active change; never infer among multiple candidates.\n2. Read governance, OpenSpec configuration, current main specs, all change artifacts, implementation and test\n   evidence, the latest independent verification result, Git state, and other active changes that could\n   conflict with the same requirements.\n3. Require all applicable artifacts and tasks complete, strict OpenSpec validation passing, required\n   repository gates passing, and no unresolved critical mismatch or unapproved limitation.\n4. For a no-behavior refactor or tooling/docs change, confirm `skip_specs: true` is intentional and that no\n   delta specs conflict with it. Do not invent or merge behavior requirements.\n\n## Complete the lifecycle\n\nUse current project guidance and the installed OpenSpec version. Normally:\n\n1. run `openspec validate \u003cname> --strict --no-interactive` immediately before mutation;\n2. inspect whether delta specs must be synced or will merge during archive;\n3. archive the exact change with `openspec archive \u003cname> --yes` when the user has authorized completion and\n   no interactive terminal can answer confirmation;\n4. do not use `--no-validate` to bypass a failing gate;\n5. verify the dated archive destination exists, the active change no longer does, and main specs reflect all\n   intended ADDED, MODIFIED, and REMOVED requirements;\n6. run applicable post-archive validation, including `openspec validate --archived` where supported.\n\nIf the archive reports incomplete tasks, spec conflicts, validation errors, or a partial move, stop and\nrecover according to the command output. Do not report closure from an intended command alone.\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "eval:skill-evaluations",
        "skill:specify-openspec-change",
        "skill:verify-openspec-implementation"
      ],
      "archetypes": [
        "development"
      ]
    },
    {
      "key": "skill:continue-project",
      "id": "continue-project",
      "name": "Continue Project",
      "type": "skill",
      "path": "skills/continue-project/SKILL.md",
      "description": "Inspect canonical Agent Commons project state, resolve an optional requirement, specification, dashboard reference, or safe project-local path, and perform or recommend the next lifecycle step. Use when resuming an initialized project, asking what comes next, or continuing a specific delivery object. Do not use to bypass approval, specification, source protection, dependency ordering, or bounded implementation ownership.",
      "purpose": "Inspect canonical Agent Commons project state, resolve an optional requirement, specification, dashboard reference, or safe project-local path, and perform or recommend the next lifecycle step",
      "use_when": [
        "when resuming an initialized project, asking what comes next, or continuing a specific delivery object"
      ],
      "not_when": [
        "to bypass approval, specification, source protection, dependency ordering, or bounded implementation ownership"
      ],
      "inputs": [
        "Agent Commons project manifest",
        "canonical structured project state",
        "optional stable ID or safe project-local path"
      ],
      "workflow": [
        "Resolve context and next action",
        "Lifecycle routing",
        "Scoped and batch continuation",
        "Blockers and synchronization"
      ],
      "outputs": [
        "resolved lifecycle stage",
        "blockers or concise choices",
        "next canonical capability and subject"
      ],
      "validation": [],
      "tags": [
        "continue project",
        "next action",
        "next step",
        "next-action-resolution",
        "proceed",
        "project-lifecycle-continuation",
        "project-object-resolution",
        "requirement ID",
        "resume project",
        "specification ID",
        "what next"
      ],
      "search_terms": [
        "Continue Project",
        "continue project",
        "continue-project",
        "next action",
        "next step",
        "next-action-resolution",
        "proceed",
        "project-lifecycle-continuation",
        "project-object-resolution",
        "requirement ID",
        "resume project",
        "specification ID",
        "what next"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: continue-project\ndescription: Inspect canonical Agent Commons project state, resolve an optional requirement, specification, dashboard reference, or safe project-local path, and perform or recommend the next lifecycle step. Use when resuming an initialized project, asking what comes next, or continuing a specific delivery object. Do not use to bypass approval, specification, source protection, dependency ordering, or bounded implementation ownership.\n---\n\n# Continue an Agent Commons project\n\nResume from canonical state instead of reconstructing the workflow from memory.\n\n## Resolve context and next action\n\n1. Read project governance, `.agent-commons.yaml`, Git state, protected source boundaries, and L0 plus the\n   `.agent-commons/memory/index.json` status when enabled. Load only the domain/entity context required by\n   the next action. Verify memory against canonical structured state; treat a generated dashboard as a\n   projection, never the source of lifecycle truth.\n2. Run `scripts/resolve_project_continuation.py --root \u003cproject>` with an optional stable ID or safe\n   project-local path. Stable requirement and specification IDs are the normal interface; paths are a\n   debugging and tooling fallback.\n3. Confirm that the resolved object, lifecycle status, dependencies, approval, ownership, and blockers\n   match the underlying requirement, OpenSpec, implementation, test, and evidence records.\n4. If one required action is unambiguous, invoke the named canonical capability with its resolved subject.\n   If the resolver returns choices, present them concisely and do not choose when priority or dependency\n   order remains genuinely ambiguous.\n\nThe resolver returns a stable capability reference and whether that ID is selected in the project manifest;\nit does not execute the capability. `.agent-commons.yaml` is project-specific composition and lifecycle\nconfiguration, not native runtime configuration. The active runtime resolves the returned ID to the installed\ncanonical Commons skill, then that skill reads the local governance and state required for its own workflow.\n\n## Lifecycle routing\n\n- Missing legacy inventory or analysis routes to `analyze-legacy-system`, which owns the configured\n  evidence-first analysis lifecycle.\n- Completed analysis with incomplete requirements routes to `derive-modernization-requirements`.\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "eval:skill-evaluations",
        "skill:analyze-legacy-system",
        "skill:build-living-dashboard",
        "skill:derive-modernization-requirements",
        "skill:implement-openspec-change",
        "skill:implement-ready-slice",
        "skill:initialize-project",
        "skill:maintain-project-memory",
        "skill:specify-openspec-change",
        "skill:validate-work-item-assumptions",
        "skill:verify-openspec-implementation",
        "tool:resolve-project-continuation"
      ],
      "archetypes": [
        "development",
        "legacy-migration"
      ]
    },
    {
      "key": "skill:coordinate-parallel-agents",
      "id": "coordinate-parallel-agents",
      "name": "Coordinate Parallel Agents",
      "type": "skill",
      "path": "skills/coordinate-parallel-agents/SKILL.md",
      "description": "Coordinate two or more bounded agents through mutually exclusive ownership, isolated outputs, explicit dependencies, structured handoffs, coordinator-only integration, validation, recovery, and concurrency limits. Use when independent work can materially reduce elapsed time. Do not use for overlapping edits, canonical-state decisions, tiny work, or runtime-specific orchestration syntax.",
      "purpose": "Coordinate two or more bounded agents through mutually exclusive ownership, isolated outputs, explicit dependencies, structured handoffs, coordinator-only integration, validation, recovery, and concurrency limits",
      "use_when": [
        "when independent work can materially reduce elapsed time"
      ],
      "not_when": [
        "for overlapping edits, canonical-state decisions, tiny work, or runtime-specific orchestration syntax"
      ],
      "inputs": [],
      "workflow": [
        "Build the execution graph",
        "Partition before dispatch",
        "Monitor and recover",
        "Integrate centrally"
      ],
      "outputs": [],
      "validation": [],
      "tags": [
        "bounded-parallel-agent-coordination"
      ],
      "search_terms": [
        "bounded-parallel-agent-coordination",
        "Coordinate Parallel Agents",
        "coordinate-parallel-agents"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: coordinate-parallel-agents\ndescription: Coordinate two or more bounded agents through mutually exclusive ownership, isolated outputs, explicit dependencies, structured handoffs, coordinator-only integration, validation, recovery, and concurrency limits. Use when independent work can materially reduce elapsed time. Do not use for overlapping edits, canonical-state decisions, tiny work, or runtime-specific orchestration syntax.\n---\n\n# Coordinate bounded parallel agents\n\nConfirm that parallel work is authorized, useful, and separable. The coordinator owns scope, shared state,\nglobal identifiers, dependency decisions, integration order, validation, progress, recovery, and completion.\n\n## Build the execution graph\n\nBefore dispatch, express each task with a stable ID, dependencies, exact writable paths, mutable shared\nsurfaces, and an observable completion signal. Mutable shared surfaces include canonical registries, schemas,\nmain specifications, lockfiles, database migrations, shared fixtures, generated global views, and external\nstate even when workers would edit different files.\n\nUse the repository `tools/plan_parallel_execution.py` helper with the contract in\n`references/execution-plan-contract.md` when a structured plan is available. It rejects cycles and unsafe\npaths, detects nested write-path and shared-surface conflicts, applies the requested concurrency bound, and\nreturns serialized execution stages. The plan is scheduling evidence, not authorization to perform a task.\n\n## Partition before dispatch\n\n1. Establish the complete eligible denominator and protected or coordinator-owned surfaces.\n2. Partition by independent files, components, evidence batches, scenarios, or other stable boundaries. Give\n   every eligible item exactly one primary owner and record contextual dependencies separately.\n3. Reject partitions that overlap writes, allocate shared identifiers, mutate the same schema, resolve the\n   same decision, or depend on uncommitted output from one another.\n4. Set a bounded concurrency limit based on task independence, tool capacity, review load, and integration\n   cost. More workers are not automatically faster.\n5. Give each worker the contract in `references/worker-contract.md`, relevant evidence, allowed paths,\n   prohibited actions, validation commands, one isolated output location, and a bounded task-specific context\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "eval:skill-evaluations",
        "skill:analyze-legacy-system",
        "skill:maintain-project-memory",
        "skill:manage-project-delivery"
      ],
      "archetypes": [
        "development",
        "legacy-migration"
      ]
    },
    {
      "key": "skill:create-branded-html-artifact",
      "id": "create-branded-html-artifact",
      "name": "Create Branded HTML Artifact",
      "type": "skill",
      "path": "skills/create-branded-html-artifact/SKILL.md",
      "description": "Create a polished evidence-aware HTML executive presentation, sales story, dashboard shell, or interactive technical narrative using resolved client branding or the Accenture fallback. Use when HTML is the chosen substantial deliverable and visual identity matters. Do not use for deterministic canonical-state dashboard generation, non-HTML delivery, or styling without an audience, evidence source, and visual brief.",
      "purpose": "Create a polished evidence-aware HTML executive presentation, sales story, dashboard shell, or interactive technical narrative using resolved client branding or the Accenture fallback",
      "use_when": [
        "when HTML is the chosen substantial deliverable and visual identity matters"
      ],
      "not_when": [
        "for deterministic canonical-state dashboard generation, non-HTML delivery, or styling without an audience, evidence source, and visual brief"
      ],
      "inputs": [],
      "workflow": [
        "Establish the brief",
        "Design in two passes",
        "Build progressively",
        "Validate"
      ],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Create Branded HTML Artifact",
        "create-branded-html-artifact"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: create-branded-html-artifact\ndescription: Create a polished evidence-aware HTML executive presentation, sales story, dashboard shell, or interactive technical narrative using resolved client branding or the Accenture fallback. Use when HTML is the chosen substantial deliverable and visual identity matters. Do not use for deterministic canonical-state dashboard generation, non-HTML delivery, or styling without an audience, evidence source, and visual brief.\n---\n\n# Create a branded HTML artifact\n\nDerive a visual system from evidence; do not clone a marketing site or invent brand rules.\n\n## Establish the brief\n\nConfirm audience, single job, narrative or decision, artifact type, source material, factual authority,\ninteraction/print needs, delivery constraints, and definition of done. Read `references/brand-discovery.md`\nbefore using a website, design system, screenshots, logo, or reference deck.\n\nInspect persisted client context before asking about language or brand. A supplied official client website\nor corporate-design source can support brand discovery and sector/geography classification in parallel.\nDo not wait for brand extraction before resolving independently available public-sector evidence. Never\nreplace an explicit client brand with a generic public-sector visual theme.\n\nHTML delivery is mandatory once this workflow is selected. If no branding is supplied, or the supplied\nbrand source is unreadable or inaccessible, or cannot yield a usable official logo and core interface\npalette, generate the\nrequested `.html` artifact with the bundled Accenture fallback. Mark the output `accenture-fallback`, retain\nthe requested source and failure reason in project evidence, and do not claim that the fallback represents\nthe client brand. Brand-resolution failure must not produce only a blocker document or suppress the HTML.\n\n## Design in two passes\n\n1. Extract verified signals: palette, typography roles, spacing rhythm, geometry, imagery, grid, motion,\n   voice, logo rules, and accessibility constraints. Record source and confidence.\n2. Write a compact design plan: 4-6 named colors, display/body/data type roles, layout thesis, and one\n   meaningful signature element derived from the subject.\n3. Critique the plan for generic dark-neon AI styling, glass cards, ornamental gradients, dashboard-tile\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "eval:skill-evaluations",
        "overlay:branded-html",
        "skill:create-technical-diagram",
        "skill:localize-client-artifact",
        "skill:polish-html-artifact",
        "skill:validate-visual-artifact"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "skill:create-class-diagram",
      "id": "create-class-diagram",
      "name": "Create Class Diagram",
      "type": "skill",
      "path": "skills/create-class-diagram/SKILL.md",
      "description": "Derive and validate a focused class or domain-model diagram from selected object-oriented source code, specifications, or approved target design. Use for Java, C#, Python, TypeScript, and similar languages when inheritance, interfaces, composition, aggregation, associations, cardinality, or important members must be explained. Do not use for full-repository dumps, every getter and setter, database-only models, or proposed structures presented as verified source.",
      "purpose": "Derive and validate a focused class or domain-model diagram from selected object-oriented source code, specifications, or approved target design",
      "use_when": [
        "for Java, C#, Python, TypeScript, and similar languages when inheritance, interfaces, composition, aggregation, associations, cardinality, or important members must be explained"
      ],
      "not_when": [
        "for full-repository dumps, every getter and setter, database-only models, or proposed structures presented as verified source"
      ],
      "inputs": [
        "selected object-oriented source or approved design",
        "scope and abstraction",
        "source evidence and exclusions"
      ],
      "workflow": [
        "Extract deliberately",
        "Compose the model",
        "Validate"
      ],
      "outputs": [
        "editable class-diagram source",
        "rendered diagram",
        "evidence index, legend, and unknowns"
      ],
      "validation": [],
      "tags": [
        "UML",
        "class",
        "class-diagram",
        "composition",
        "diagram",
        "domain model",
        "domain-model-visualization",
        "inheritance",
        "uml-class-model"
      ],
      "search_terms": [
        "class",
        "class-diagram",
        "composition",
        "Create Class Diagram",
        "create-class-diagram",
        "diagram",
        "domain model",
        "domain-model-visualization",
        "inheritance",
        "UML",
        "uml-class-model"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: create-class-diagram\ndescription: Derive and validate a focused class or domain-model diagram from selected object-oriented source code, specifications, or approved target design. Use for Java, C#, Python, TypeScript, and similar languages when inheritance, interfaces, composition, aggregation, associations, cardinality, or important members must be explained. Do not use for full-repository dumps, every getter and setter, database-only models, or proposed structures presented as verified source.\n---\n\n# Create a class diagram\n\nSelect the abstraction that answers the question: domain overview, important classes, package/module\nfocus, or a full selected subsystem. Apply the shared protocol from `create-technical-diagram`.\n\n## Extract deliberately\n\n1. Bound source roots, packages/modules, entry classes, generated code, tests, and excluded framework\n   artifacts.\n2. Resolve classes, interfaces, enums, inheritance/implementation, fields, constructor ownership, and\n   method signatures from syntax-aware tooling or direct source evidence where practical.\n3. Distinguish inheritance, composition/lifecycle ownership, aggregation, plain association, dependency,\n   and interface realization. Use cardinality only when collections, constraints, or specifications make\n   it defensible.\n4. Include important fields and methods that explain responsibility or contracts. Omit routine accessors,\n   boilerplate, framework noise, and private implementation detail by default.\n\nFor dynamic languages, label unresolved runtime types and monkey-patched or metaprogrammed relationships\ninstead of forcing static certainty. For target design, mark all unimplemented structures `PROPOSED`.\n\n## Compose the model\n\nGroup by package, bounded context, layer, or responsibility. Keep inheritance trees visually distinct from\nassociations. Split large models into a domain overview and package/subsystem drilldowns with stable class\nIDs. PlantUML or Mermaid suits maintainable UML-like source; Graphviz or SVG may be better for large custom\nlayouts.\n\n## Validate\n\nReconcile names, namespaces, visibility, inheritance, interface realization, ownership, association\ndirection, multiplicity, and selected members to source coordinates or approved specifications. Confirm\nthat omitted detail is intentional and that no class or relationship was invented. Return editable source,\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "eval:skill-evaluations",
        "overlay:architecture-documentation",
        "skill:analyze-legacy-system",
        "skill:create-technical-diagram",
        "skill:validate-visual-artifact"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "skill:create-component-architecture-diagram",
      "id": "create-component-architecture-diagram",
      "name": "Create Component Architecture Diagram",
      "type": "skill",
      "path": "skills/create-component-architecture-diagram/SKILL.md",
      "description": "Derive and validate an application or solution architecture view at container, component, module, service, or major package level from code, configuration, contracts, and approved design evidence. Use for backend, frontend/backend, microservice, modular-monolith, target, comparison, or modernization architecture views. Do not use for enterprise landscapes, exhaustive class detail, time-ordered interactions, or proposed dependencies presented as observed current architecture.",
      "purpose": "Derive and validate an application or solution architecture view at container, component, module, service, or major package level from code, configuration, contracts, and approved design evidence",
      "use_when": [
        "for backend, frontend/backend, microservice, modular-monolith, target, comparison, or modernization architecture views"
      ],
      "not_when": [
        "for enterprise landscapes, exhaustive class detail, time-ordered interactions, or proposed dependencies presented as observed current architecture"
      ],
      "inputs": [
        "bounded solution evidence",
        "audience and component level",
        "current or proposed state"
      ],
      "workflow": [
        "Establish level and state",
        "Derive the model",
        "Control the view",
        "Validate"
      ],
      "outputs": [
        "editable component-diagram source",
        "rendered overview and drilldowns",
        "evidence and validation record"
      ],
      "validation": [],
      "tags": [
        "C4",
        "application",
        "application-architecture-diagram",
        "architecture",
        "component",
        "component-architecture-diagram",
        "diagram",
        "module",
        "service",
        "solution-architecture-view"
      ],
      "search_terms": [
        "application",
        "application-architecture-diagram",
        "architecture",
        "C4",
        "component",
        "component-architecture-diagram",
        "Create Component Architecture Diagram",
        "create-component-architecture-diagram",
        "diagram",
        "module",
        "service",
        "solution-architecture-view"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: create-component-architecture-diagram\ndescription: Derive and validate an application or solution architecture view at container, component, module, service, or major package level from code, configuration, contracts, and approved design evidence. Use for backend, frontend/backend, microservice, modular-monolith, target, comparison, or modernization architecture views. Do not use for enterprise landscapes, exhaustive class detail, time-ordered interactions, or proposed dependencies presented as observed current architecture.\n---\n\n# Create a component architecture diagram\n\nExplain the internal structure of one bounded solution without collapsing into either vague boxes or an\nunreadable package graph. Apply the shared protocol from `create-technical-diagram`.\n\n## Establish level and state\n\nChoose one primary level: application/container, component/module/service, or a selected subsystem. State\nwhether the view is current, proposed target, transition, or comparison. Use C4 container/component ideas\nwhen useful, but require strict C4 notation only when explicitly selected.\n\n## Derive the model\n\n1. Inspect manifests, dependency declarations, module roots, public interfaces, routes, service wiring,\n   configuration, deployment units, message contracts, schemas, and representative call paths.\n2. Identify stable responsibilities, owned data, exposed interfaces, dependencies, external systems, and\n   runtime boundaries. Treat directory names as navigation clues, not component proof.\n3. Separate build-time dependency, runtime call, data ownership, event subscription, and shared-library use.\n4. Mark target components and dependencies `PROPOSED`; preserve conflicts and unknown dynamic edges.\n\n## Control the view\n\nGroup by layer, domain, deployable unit, or ownership according to the audience. Keep dependency direction\nclear. Collapse utility libraries and repeated infrastructure unless they materially affect architecture.\nFor a large solution, create a container overview plus component drilldowns per bounded subsystem.\n\nGraphviz/DOT suits dependency-rich views; PlantUML suits formal component notation; SVG/HTML suits branded\nor responsive artifacts. Mermaid is suitable when the graph remains modest.\n\n## Validate\n\nCheck each component boundary, responsibility, dependency direction, interface label, data owner, and\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "eval:skill-evaluations",
        "overlay:architecture-documentation",
        "skill:analyze-legacy-system",
        "skill:create-sequence-diagram",
        "skill:create-system-landscape-diagram",
        "skill:create-technical-diagram",
        "skill:validate-visual-artifact"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "skill:create-data-flow-diagram",
      "id": "create-data-flow-diagram",
      "name": "Create Data Flow Diagram",
      "type": "skill",
      "path": "skills/create-data-flow-diagram/SKILL.md",
      "description": "Derive and validate a logical or physical data-flow and lineage diagram showing sources, transformations, stores, interfaces, destinations, and evidenced movement of data. Use for ETL, batch, SAS, integration-heavy legacy systems, migration, lineage, privacy/security analysis, or selected pipelines at overview or drilldown level. Do not use for control-flow-only logic, static component dependencies without data movement, or transformations and destinations inferred without source, configuration, schema, job, or runtime evidence.",
      "purpose": "Derive and validate a logical or physical data-flow and lineage diagram showing sources, transformations, stores, interfaces, destinations, and evidenced movement of data",
      "use_when": [
        "for ETL, batch, SAS, integration-heavy legacy systems, migration, lineage, privacy/security analysis, or selected pipelines at overview or drilldown level"
      ],
      "not_when": [
        "for control-flow-only logic, static component dependencies without data movement, or transformations and destinations inferred without source, configuration, schema, job, or runtime evidence"
      ],
      "inputs": [
        "schemas, jobs, code, mappings, and runtime evidence",
        "pipeline boundary and audience"
      ],
      "workflow": [
        "Define the flow",
        "Trace from evidence",
        "Validate"
      ],
      "outputs": [
        "editable data-flow source",
        "rendered lineage views",
        "evidence, unresolved lineage, and validation"
      ],
      "validation": [],
      "tags": [
        "DFD",
        "ETL",
        "SAS",
        "batch",
        "data flow",
        "data-flow-diagram",
        "data-lineage-visualization",
        "diagram",
        "etl-flow-visualization",
        "lineage"
      ],
      "search_terms": [
        "batch",
        "Create Data Flow Diagram",
        "create-data-flow-diagram",
        "data flow",
        "data-flow-diagram",
        "data-lineage-visualization",
        "DFD",
        "diagram",
        "ETL",
        "etl-flow-visualization",
        "lineage",
        "SAS"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: create-data-flow-diagram\ndescription: Derive and validate a logical or physical data-flow and lineage diagram showing sources, transformations, stores, interfaces, destinations, and evidenced movement of data. Use for ETL, batch, SAS, integration-heavy legacy systems, migration, lineage, privacy/security analysis, or selected pipelines at overview or drilldown level. Do not use for control-flow-only logic, static component dependencies without data movement, or transformations and destinations inferred without source, configuration, schema, job, or runtime evidence.\n---\n\n# Create a data-flow diagram\n\nMake data movement and transformation—not control flow—the primary subject. Apply the shared protocol from\n`create-technical-diagram`.\n\n## Define the flow\n\nChoose logical flow, physical flow, high-level lineage, or a detailed selected pipeline. Bound datasets,\ntime window, environment, batch/stream mode, current/target/transition state, and the questions the view\nmust answer.\n\n## Trace from evidence\n\n1. Inspect schemas, files, queries, ETL/SAS jobs, application code, mapping rules, message contracts,\n   schedulers, configuration, storage metadata, and representative runtime evidence.\n2. Record sources, processes/transformations, stores, destinations, interfaces, data classes, direction,\n   frequency, format, and ownership where known.\n3. Trace rename, filter, join, aggregate, enrich, validate, mask, split, merge, and persistence steps only\n   when evidenced. Preserve dynamic SQL, generated mappings, manual steps, and unresolved lineage as gaps.\n4. Distinguish data movement from control triggers. Add trust boundaries, sensitive-data annotations, or\n   retention notes only when relevant and supported.\n\nFor large estates, create a source-to-domain overview plus pipeline or dataset drilldowns. Graphviz/DOT is\noften effective for lineage; Mermaid works for smaller flows; SVG/HTML supports polished security,\nmanagement, or presentation views.\n\n## Validate\n\nReconcile every source, transformation, store, destination, direction, and data-class label to evidence.\nCheck that no transformation is invented, stores are not confused with processes, manual transfers remain\nvisible, and current/proposed flows are distinct. Return editable source, rendered output, evidence\nmetadata, legend, overview/drilldown map, unresolved lineage, and validation limits.",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "eval:skill-evaluations",
        "overlay:architecture-documentation",
        "skill:analyze-legacy-system",
        "skill:create-technical-diagram",
        "skill:review-privacy-security",
        "skill:validate-visual-artifact"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "skill:create-er-diagram",
      "id": "create-er-diagram",
      "name": "Create ER Diagram",
      "type": "skill",
      "path": "skills/create-er-diagram/SKILL.md",
      "description": "Derive and validate an entity-relationship diagram from database schemas, DDL, migrations, ORM models, or authoritative data documentation. Use to show tables or entities, primary and foreign keys, join tables, ownership, important attributes, and defensible cardinalities at domain, core-entity, or selected-schema level. Do not use to guess relationships from column names, flatten a large database into one canvas, or treat ORM convenience mappings as physical constraints without evidence.",
      "purpose": "Derive and validate an entity-relationship diagram from database schemas, DDL, migrations, ORM models, or authoritative data documentation",
      "use_when": [
        "to show tables or entities, primary and foreign keys, join tables, ownership, important attributes, and defensible cardinalities at domain, core-entity, or selected-schema level"
      ],
      "not_when": [
        "to guess relationships from column names, flatten a large database into one canvas, or treat ORM convenience mappings as physical constraints without evidence"
      ],
      "inputs": [
        "schema metadata, DDL, migrations, ORM, or data documentation",
        "selected domain and physical or logical level"
      ],
      "workflow": [
        "Establish authority",
        "Derive entities and relationships",
        "Control density",
        "Validate"
      ],
      "outputs": [
        "editable ER source",
        "rendered overview and schema drilldowns",
        "keys, evidence, conflicts, and unknowns"
      ],
      "validation": [],
      "tags": [
        "ERD",
        "cardinality",
        "data-model-visualization",
        "database",
        "database-schema-visualization",
        "diagram",
        "entity relationship",
        "entity-relationship-diagram",
        "foreign key",
        "schema"
      ],
      "search_terms": [
        "cardinality",
        "Create ER Diagram",
        "create-er-diagram",
        "data-model-visualization",
        "database",
        "database-schema-visualization",
        "diagram",
        "entity relationship",
        "entity-relationship-diagram",
        "ERD",
        "foreign key",
        "schema"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: create-er-diagram\ndescription: Derive and validate an entity-relationship diagram from database schemas, DDL, migrations, ORM models, or authoritative data documentation. Use to show tables or entities, primary and foreign keys, join tables, ownership, important attributes, and defensible cardinalities at domain, core-entity, or selected-schema level. Do not use to guess relationships from column names, flatten a large database into one canvas, or treat ORM convenience mappings as physical constraints without evidence.\n---\n\n# Create an ER diagram\n\nExplain the data model at the smallest level that supports the audience and decision. Apply the shared\nprotocol from `create-technical-diagram`.\n\n## Establish authority\n\nPrioritize live schema metadata or applied DDL, then migrations, then ORM mappings, then documentation.\nRecord conflicts rather than silently choosing. Define database/schema, environment, snapshot time,\nselected domains, excluded technical tables, and whether the view is physical, logical, or proposed.\n\n## Derive entities and relationships\n\n1. Extract tables/entities, primary and candidate keys, foreign keys, nullability, unique constraints,\n   important attributes, indexes only when relevant, and join tables.\n2. Derive cardinality from constraints and nullability. Do not infer a foreign key solely from naming\n   conventions or ORM navigation properties.\n3. Distinguish identifying relationships, optional ownership, many-to-many joins, inheritance mapping,\n   denormalized references, and unresolved polymorphic links.\n4. Mark proposed target structures `PROPOSED` and retain current schema separately when comparison matters.\n\n## Control density\n\nFor large databases, produce a domain overview using core entities and relationship summaries, then\ndomain/subsystem drilldowns. Avoid showing every audit column or technical attribute unless the purpose\nrequires it. Mermaid ER and PlantUML are suitable for modest formal models; Graphviz or SVG/HTML is often\nbetter for large decomposed schemas.\n\n## Validate\n\nCheck entity names, keys, relationship endpoints, optionality, cardinality, join-table semantics, attribute\nselection, and schema scope against authoritative evidence. Surface missing constraints and ORM/schema\nconflicts explicitly. Return editable source, rendered output, evidence metadata, notation legend,\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "eval:skill-evaluations",
        "overlay:architecture-documentation",
        "skill:analyze-legacy-system",
        "skill:create-technical-diagram",
        "skill:validate-visual-artifact"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "skill:create-sequence-diagram",
      "id": "create-sequence-diagram",
      "name": "Create Sequence Diagram",
      "type": "skill",
      "path": "skills/create-sequence-diagram/SKILL.md",
      "description": "Trace and validate an interaction over time as participants, ordered messages, activations, alternatives, loops, asynchronous events, and failures. Use for API requests, authentication, business processes, legacy call chains, service interactions, error paths, or current-versus-target flow comparisons when ordering matters. Do not use for static dependency maps, unsupported branches, or a flow reconstructed only from participant names without tracing code, contracts, logs, or specifications.",
      "purpose": "Trace and validate an interaction over time as participants, ordered messages, activations, alternatives, loops, asynchronous events, and failures",
      "use_when": [
        "for API requests, authentication, business processes, legacy call chains, service interactions, error paths, or current-versus-target flow comparisons when ordering matters"
      ],
      "not_when": [
        "for static dependency maps, unsupported branches, or a flow reconstructed only from participant names without tracing code, contracts, logs, or specifications"
      ],
      "inputs": [
        "bounded scenario",
        "code, contracts, traces, logs, tests, or specifications",
        "requested paths and state"
      ],
      "workflow": [
        "Trace the interaction",
        "Validate"
      ],
      "outputs": [
        "editable sequence source",
        "rendered interaction view",
        "scenario, evidence, and validation notes"
      ],
      "validation": [],
      "tags": [
        "API flow",
        "call chain",
        "diagram",
        "error flow",
        "interaction",
        "interaction-diagram",
        "request-flow-visualization",
        "sequence",
        "sequence-diagram"
      ],
      "search_terms": [
        "API flow",
        "call chain",
        "Create Sequence Diagram",
        "create-sequence-diagram",
        "diagram",
        "error flow",
        "interaction",
        "interaction-diagram",
        "request-flow-visualization",
        "sequence",
        "sequence-diagram"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: create-sequence-diagram\ndescription: Trace and validate an interaction over time as participants, ordered messages, activations, alternatives, loops, asynchronous events, and failures. Use for API requests, authentication, business processes, legacy call chains, service interactions, error paths, or current-versus-target flow comparisons when ordering matters. Do not use for static dependency maps, unsupported branches, or a flow reconstructed only from participant names without tracing code, contracts, logs, or specifications.\n---\n\n# Create a sequence diagram\n\nChoose one bounded scenario and make time/order the primary dimension. Apply the shared protocol from\n`create-technical-diagram`.\n\n## Trace the interaction\n\n1. Define the trigger, preconditions, completion condition, happy path, requested alternatives, error\n   paths, and current/target state.\n2. Identify actors, clients, services, components, stores, queues, and external systems from source,\n   contracts, traces, logs, tests, or authoritative specifications.\n3. Trace calls and messages in order. Record direction, operation/event, sync versus async behavior,\n   returned result, persistence, retries, timeouts, and transaction boundaries when evidenced.\n4. Add `alt`, `opt`, `loop`, parallel, and error fragments only when supported. Keep uncertain ordering or\n   dynamic dispatch explicit rather than choosing a convenient sequence.\n\nSeparate current and target sequences when combining them would confuse observed and proposed behavior.\nFor a long interaction, create an overview sequence and focused subsequences around major phases.\n\nMermaid and PlantUML are usually appropriate editable formats; native SVG/HTML is useful when presentation\nstyling or responsive annotations matter.\n\n## Validate\n\nReconcile every participant and message to a source locator or approved scenario. Verify ordering,\ndirection, sync/async semantics, alternatives, error propagation, return values, and termination. Ensure\nthe diagram does not imply calls merely because components are statically related. Return editable source,\nrendered output, evidence metadata, scenario/precondition notes, legend, and unknowns.",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "eval:skill-evaluations",
        "overlay:architecture-documentation",
        "skill:analyze-legacy-system",
        "skill:create-component-architecture-diagram",
        "skill:create-technical-diagram",
        "skill:validate-visual-artifact"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "skill:create-system-landscape-diagram",
      "id": "create-system-landscape-diagram",
      "name": "Create System Landscape Diagram",
      "type": "skill",
      "path": "skills/create-system-landscape-diagram/SKILL.md",
      "description": "Derive and validate a high-level system or application landscape showing actors, systems, platforms, data stores, domains, scope, lifecycle state, and evidenced integrations. Use for enterprise landscapes, modernization discovery, current/target/transition views, integration maps, or executive architecture overviews. Do not use for internal component detail, message ordering, database schema structure, or relationships inferred only from names and proximity.",
      "purpose": "Derive and validate a high-level system or application landscape showing actors, systems, platforms, data stores, domains, scope, lifecycle state, and evidenced integrations",
      "use_when": [
        "for enterprise landscapes, modernization discovery, current/target/transition views, integration maps, or executive architecture overviews"
      ],
      "not_when": [
        "for internal component detail, message ordering, database schema structure, or relationships inferred only from names and proximity"
      ],
      "inputs": [
        "system and interface evidence",
        "scope, audience, and current/target/transition state"
      ],
      "workflow": [
        "Bound the landscape",
        "Model relationships",
        "Compose the view",
        "Validate"
      ],
      "outputs": [
        "editable landscape source",
        "rendered overview and drilldowns",
        "scope, lifecycle, evidence, and unknowns"
      ],
      "validation": [],
      "tags": [
        "C4 context",
        "application landscape",
        "application-landscape-diagram",
        "diagram",
        "integration",
        "integration-map",
        "system landscape",
        "system-landscape-diagram",
        "topology"
      ],
      "search_terms": [
        "application landscape",
        "application-landscape-diagram",
        "C4 context",
        "Create System Landscape Diagram",
        "create-system-landscape-diagram",
        "diagram",
        "integration",
        "integration-map",
        "system landscape",
        "system-landscape-diagram",
        "topology"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: create-system-landscape-diagram\ndescription: Derive and validate a high-level system or application landscape showing actors, systems, platforms, data stores, domains, scope, lifecycle state, and evidenced integrations. Use for enterprise landscapes, modernization discovery, current/target/transition views, integration maps, or executive architecture overviews. Do not use for internal component detail, message ordering, database schema structure, or relationships inferred only from names and proximity.\n---\n\n# Create a system landscape diagram\n\nShow the smallest set of systems and relationships needed to explain the landscape to the intended\naudience. Apply the shared evidence, format, decomposition, and delivery rules from\n`create-technical-diagram`.\n\n## Bound the landscape\n\n1. Define current, target, transition, or comparison state; business/technical audience; organizational,\n   domain, and environment boundary; and in-scope/out-of-scope criteria.\n2. Gather system registers, interface catalogs, deployment evidence, source analysis, contracts,\n   configuration, runtime observations, and authoritative architecture documents.\n3. Normalize aliases without merging distinct deployments, tenants, environments, or ownership boundaries.\n4. Record actors, internal systems, external platforms, databases only when landscape-relevant, domains,\n   and integration endpoints with `VERIFIED`, `INFERRED`, or `UNKNOWN` status.\n\n## Model relationships\n\nRepresent direction and known mechanism such as REST, SOAP, messaging, events, files, batch, database\naccess, or manual interaction. Omit the protocol when it is not known. Do not convert shared technology,\nnetwork proximity, or similar names into an integration.\n\nVisually distinguish evidenced states such as `IN SCOPE`, `OUT OF SCOPE`, `EXTERNAL`, `LEGACY`, `TARGET`,\nand `TRANSITION`. Do not apply a lifecycle label without evidence or an explicit proposal decision.\n\n## Compose the view\n\nUse a left-to-right or domain-centered flow with clear system boundaries and a compact legend. Group by\ndomain, ownership, trust boundary, or lifecycle only when that grouping supports the purpose. Use C4\ncontext ideas when helpful, but do not require strict C4 notation.\n\nFor large estates, create:\n\n- an executive landscape of major domains and systems;\n- integration or domain drilldowns with stable system IDs;\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "eval:skill-evaluations",
        "overlay:architecture-documentation",
        "skill:analyze-legacy-system",
        "skill:create-component-architecture-diagram",
        "skill:create-technical-diagram",
        "skill:validate-visual-artifact"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "skill:create-technical-diagram",
      "id": "create-technical-diagram",
      "name": "Create Technical Diagram",
      "type": "skill",
      "path": "skills/create-technical-diagram/SKILL.md",
      "description": "Select, model, render, and validate an evidence-backed technical diagram at the right abstraction for documentation, analysis, dashboards, or presentations. Use when the requested view is ambiguous, spans multiple diagram families, or needs shared evidence, format, decomposition, and delivery decisions. Do not use for decorative illustration, unsupported target-state invention, generic charts, or a request that already belongs unambiguously to one specialized diagram skill.",
      "purpose": "Select, model, render, and validate an evidence-backed technical diagram at the right abstraction for documentation, analysis, dashboards, or presentations",
      "use_when": [
        "when the requested view is ambiguous, spans multiple diagram families, or needs shared evidence, format, decomposition, and delivery decisions"
      ],
      "not_when": [
        "for decorative illustration, unsupported target-state invention, generic charts, or a request that already belongs unambiguously to one specialized diagram skill"
      ],
      "inputs": [
        "communication purpose and audience",
        "scope and architecture state",
        "source evidence",
        "destination and visual references"
      ],
      "workflow": [
        "Frame the view",
        "Select the family",
        "Build the evidence model",
        "Choose the representation",
        "Use visual references without borrowing facts",
        "Control density",
        "Deliver and validate"
      ],
      "outputs": [
        "selected diagram method",
        "lightweight evidence model",
        "editable source and rendered artifact",
        "semantic and visual validation"
      ],
      "validation": [],
      "tags": [
        "ERD",
        "Graphviz",
        "Mermaid",
        "PlantUML",
        "SVG",
        "UML",
        "architecture",
        "diagram",
        "diagram-format-selection",
        "evidence-backed-diagramming",
        "technical-diagram-routing"
      ],
      "search_terms": [
        "architecture",
        "Create Technical Diagram",
        "create-technical-diagram",
        "diagram",
        "diagram-format-selection",
        "ERD",
        "evidence-backed-diagramming",
        "Graphviz",
        "Mermaid",
        "PlantUML",
        "SVG",
        "technical-diagram-routing",
        "UML"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: create-technical-diagram\ndescription: Select, model, render, and validate an evidence-backed technical diagram at the right abstraction for documentation, analysis, dashboards, or presentations. Use when the requested view is ambiguous, spans multiple diagram families, or needs shared evidence, format, decomposition, and delivery decisions. Do not use for decorative illustration, unsupported target-state invention, generic charts, or a request that already belongs unambiguously to one specialized diagram skill.\n---\n\n# Create a technical diagram\n\nRoute the communication need to the smallest useful diagram family, then preserve one evidence model across\neditable source, rendered output, and downstream artifacts.\n\n## Frame the view\n\nEstablish purpose, audience, decision supported, scope boundary, current/target/transition state, required\ndetail, destination, and available evidence. Label proposed target structures as `PROPOSED`; use\n`VERIFIED`, `INFERRED`, and `UNKNOWN` for evidence confidence. Never turn an unknown relationship into a\nnormal rendered edge.\n\n## Select the family\n\n| Need to show | Use |\n|---|---|\n| applications, actors, platforms, and integrations | `create-system-landscape-diagram` |\n| modules, services, containers, and dependencies inside a solution | `create-component-architecture-diagram` |\n| classes, interfaces, inheritance, and object/domain relationships | `create-class-diagram` |\n| tables/entities, keys, and cardinalities | `create-er-diagram` |\n| ordered calls, messages, branches, and failures | `create-sequence-diagram` |\n| sources, transformations, stores, destinations, and lineage | `create-data-flow-diagram` |\n\nFor calls between services, choose component architecture when the question is structural and sequence\nwhen ordering matters. For migration roadmaps, compose current/transition/target architecture views with\ndependency-aware waves from `plan-work` and the timeline visual pattern; do not invent a separate\narchitecture fact set for the roadmap.\n\n## Build the evidence model\n\nCreate a lightweight record with diagram type, title, purpose, audience, scope, state, source evidence,\nnodes, relationships, and optional decomposed views. Give every relationship an evidence status and exact\nsource locator or an inference rationale. Use `assets/diagram-model.example.json` as a portable example,\nnot as a mandatory project DSL.\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "eval:skill-evaluations",
        "overlay:architecture-documentation",
        "skill:build-living-dashboard",
        "skill:create-branded-html-artifact",
        "skill:create-class-diagram",
        "skill:create-component-architecture-diagram",
        "skill:create-data-flow-diagram",
        "skill:create-er-diagram",
        "skill:create-sequence-diagram",
        "skill:create-system-landscape-diagram",
        "skill:validate-visual-artifact",
        "tool:validate-diagram-model"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "skill:deconstruct-problem-first-principles",
      "id": "deconstruct-problem-first-principles",
      "name": "Deconstruct Problem First Principles",
      "type": "skill",
      "path": "skills/deconstruct-problem-first-principles/SKILL.md",
      "description": "Deconstruct a stated problem before planning or implementing by separating known facts from inherited assumptions, restating it plainly, naming the violated invariant or unstated constraint behind it, checking where else that constraint applies, and choosing whether to intervene at the symptom, the root cause, or the structure. Use when the right approach is unclear, a defect's cause is not obvious, or a design carries trade-offs worth challenging. Do not use for a trivial or fully specified change, for topic research, for reviewing a design that already exists, or to produce the plan itself.",
      "purpose": "Deconstruct a stated problem before planning or implementing by separating known facts from inherited assumptions, restating it plainly, naming the violated invariant or unstated constraint behind it, checking where else that constraint applies, and choosing whether to intervene at the symptom, the root cause, or the structure",
      "use_when": [
        "when the right approach is unclear, a defect's cause is not obvious, or a design carries trade-offs worth challenging"
      ],
      "not_when": [
        "for a trivial or fully specified change, for topic research, for reviewing a design that already exists, or to produce the plan itself"
      ],
      "inputs": [],
      "workflow": [
        "Work the five steps in order",
        "1. Strip assumptions",
        "2. Restate plainly",
        "3. Name the broken assumption or unstated constraint",
        "4. Invert",
        "5. Choose the intervention level",
        "Report",
        "Boundaries"
      ],
      "outputs": [],
      "validation": [],
      "tags": [
        "challenge assumptions",
        "first principles",
        "intervention-level-selection",
        "problem-deconstruction",
        "root cause",
        "root-cause-analysis",
        "symptom or structure",
        "what is the actual problem"
      ],
      "search_terms": [
        "challenge assumptions",
        "Deconstruct Problem First Principles",
        "deconstruct-problem-first-principles",
        "first principles",
        "intervention-level-selection",
        "problem-deconstruction",
        "root cause",
        "root-cause-analysis",
        "symptom or structure",
        "what is the actual problem"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: deconstruct-problem-first-principles\ndescription: Deconstruct a stated problem before planning or implementing by separating known facts from inherited assumptions, restating it plainly, naming the violated invariant or unstated constraint behind it, checking where else that constraint applies, and choosing whether to intervene at the symptom, the root cause, or the structure. Use when the right approach is unclear, a defect's cause is not obvious, or a design carries trade-offs worth challenging. Do not use for a trivial or fully specified change, for topic research, for reviewing a design that already exists, or to produce the plan itself.\n---\n\n# Deconstruct a problem from first principles\n\nA delivery chain that runs evidence, requirements, specification, and plan presumes one thing it never\nchecks: that the problem was framed correctly. This workflow checks it. Establish what the problem actually\nis, and at what level it should be answered, before anything downstream commits to an approach.\n\nGround the analysis in current reality first. Read the relevant code, configuration, data, and history to\nverify what the problem statement claims, rather than reasoning from the statement alone. A deconstruction\nbuilt on the statement's own framing inherits exactly the error it exists to catch.\n\n## Work the five steps in order\n\nThe order is the method. Do not form a conclusion before step 3 is complete — a conclusion reached at step 1\nis the initial framing wearing a different label.\n\n### 1. Strip assumptions\n\nSeparate what is provably true from what is assumed. List only what is known, and mark everything else as\ninherited framing.\n\nFor a defect, do not treat the failing test, the error, or the trace as complete truth. Each shows where a\nproblem surfaced, which is often not where it originates. For a design question, do not adopt the\nrequester's framing as a constraint; a stated solution frequently arrives disguised as a requirement.\n\n### 2. Restate plainly\n\nExpress the problem in plain language, without jargon, domain shorthand, or the vocabulary of the existing\nimplementation. If it cannot be restated plainly, the problem is not yet understood — that failure is a\nfinding to report, not an obstacle to write around.\n\n### 3. Name the broken assumption or unstated constraint\n… preview truncated",
      "related_capabilities": [
        "eval:skill-evaluations",
        "skill:deep-research",
        "skill:design-test-strategy",
        "skill:plan-work",
        "skill:validate-work-item-assumptions"
      ],
      "archetypes": []
    },
    {
      "key": "skill:deep-research",
      "id": "deep-research",
      "name": "Deep Research",
      "type": "skill",
      "path": "skills/deep-research/SKILL.md",
      "description": "Conduct structured evidence-backed topic research for decisions, reports, dashboards, or presentations. Do not use for external agent-capability discovery, unsupported factual invention, or a simple lookup that does not justify a research workflow.",
      "purpose": "Conduct structured evidence-backed topic research for decisions, reports, dashboards, or presentations. Do not use for external agent-capability discovery, unsupported factual invention, or a simple lookup that does not justify a research workflow.",
      "use_when": [],
      "not_when": [
        "for external agent-capability discovery, unsupported factual invention, or a simple lookup that does not justify a research workflow"
      ],
      "inputs": [],
      "workflow": [
        "Frame the work",
        "Plan evidence collection",
        "Research multiple perspectives",
        "Maintain provenance",
        "Synthesize findings",
        "Outputs",
        "Validation"
      ],
      "outputs": [],
      "validation": [],
      "tags": [
        "evidence-synthesis",
        "presentation-research-handoff",
        "structured-research"
      ],
      "search_terms": [
        "Deep Research",
        "deep-research",
        "evidence-synthesis",
        "presentation-research-handoff",
        "structured-research"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: deep-research\ndescription: Conduct structured evidence-backed topic research for decisions, reports, dashboards, or presentations. Do not use for external agent-capability discovery, unsupported factual invention, or a simple lookup that does not justify a research workflow.\n---\n\n# Deep research\n\nBuild a decision-useful evidence base rather than a list of links.\n\n## Frame the work\n\nEstablish, from supplied context before asking:\n\n1. the research question and what must be learned;\n2. the audience and the decision or artifact the findings must support;\n3. scope boundaries such as geography, industry, technology, competitors, and time;\n4. the requested depth: quick discovery, structured research, or deep research;\n5. authoritative inputs, supplied references, and output expectations.\n\nFor substantial research, read L0 and retrieve only relevant prior conclusions, terminology, decisions,\nunknowns, and source references from project memory. Reuse current findings, but revisit drift-prone external\nfacts and never cite memory in place of the original source.\n\nAsk only for material missing choices. Record assumptions and exclusions explicitly.\n\n## Plan evidence collection\n\nCreate a compact research plan that maps each important question to likely evidence classes. Use any\nruntime-supported combination of official documentation, primary sources, reputable secondary sources,\nlocal files, uploaded documents, project repositories, and approved external services. Runtime adapters\ndecide how search, browsing, connectors, and file access are executed.\n\nPrefer direct and authoritative sources when they can establish the claim. Use secondary sources for\ncontext, comparison, market interpretation, or discovery. Treat source authority, freshness, independence,\nmethodology, and conflicts of interest as separate quality dimensions.\n\nWhen supplied attachments are a material evidence class, inventory the bounded files before extraction and\nfollow `references/attachment-intake.md`. Use the runtime's document, PDF, image, presentation, or spreadsheet\nreader appropriate to the format, including visual inspection when layout carries meaning. An attachment can\nestablish what a human source says; it does not by itself prove a claim about current implementation.\n\n## Research multiple perspectives\n\nFor consequential findings, actively look for:\n… preview truncated",
      "related_capabilities": [
        "archetype:research",
        "eval:skill-evaluations",
        "skill:deconstruct-problem-first-principles"
      ],
      "archetypes": [
        "research"
      ]
    },
    {
      "key": "skill:derive-modernization-requirements",
      "id": "derive-modernization-requirements",
      "name": "Derive Modernization Requirements",
      "type": "skill",
      "path": "skills/derive-modernization-requirements/SKILL.md",
      "description": "Convert legacy behavior, documents, interfaces, and architecture evidence into deduplicated modernization requirements with acceptance criteria, provenance, confidence, gaps, and lifecycle state. Use after bounded evidence analysis to define or reconcile target behavior. Do not use to summarize source architecture, generate requirements from memory alone, or relabel recommendations as observed facts.",
      "purpose": "Convert legacy behavior, documents, interfaces, and architecture evidence into deduplicated modernization requirements with acceptance criteria, provenance, confidence, gaps, and lifecycle state",
      "use_when": [
        "after bounded evidence analysis to define or reconcile target behavior"
      ],
      "not_when": [
        "to summarize source architecture, generate requirements from memory alone, or relabel recommendations as observed facts"
      ],
      "inputs": [],
      "workflow": [
        "Evidence model",
        "Workflow",
        "Parallel candidate extraction and canonical fan-in",
        "Specification handoff",
        "Completion"
      ],
      "outputs": [],
      "validation": [],
      "tags": [
        "generic-migration-planning",
        "requirements-extraction",
        "target-mapping-requirements"
      ],
      "search_terms": [
        "Derive Modernization Requirements",
        "derive-modernization-requirements",
        "generic-migration-planning",
        "requirements-extraction",
        "target-mapping-requirements"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: derive-modernization-requirements\ndescription: Convert legacy behavior, documents, interfaces, and architecture evidence into deduplicated modernization requirements with acceptance criteria, provenance, confidence, gaps, and lifecycle state. Use after bounded evidence analysis to define or reconcile target behavior. Do not use to summarize source architecture, generate requirements from memory alone, or relabel recommendations as observed facts.\n---\n\n# Derive modernization requirements\n\nPreserve the distinction between observed legacy behavior and proposed target behavior.\n\n## Evidence model\n\nFor each material claim record source artifact, hash/version, exact coordinate, factual observation,\ninterpretation when needed, authority, confidence, and reciprocal links. Use\n`references/evidence-contract.md` and the synthetic templates in `assets/`.\n\n## Workflow\n\n1. Define the capability, actor, trigger, boundary, and migration intent.\n2. Build a bounded context package from relevant analysis domains and entities, then gather the smallest\n   authoritative evidence packet from source code, contracts, data, tests, official documents, or validated\n   runtime observations. Memory and generated dashboards are not original evidence.\n3. Extract preconditions, inputs, validations, decisions, state changes, outputs, side effects,\n   integrations, persistence, errors, audit behavior, and non-functional constraints.\n4. Classify each statement as `observed`, `inferred`, `proposed`, `target-state`, `assumption`, `conflict`,\n   or `unknown`. Never relabel a recommendation as current fact.\n5. Deduplicate by behavior and observable outcome, not wording. Preserve conflicting sources and record\n   the reconciliation decision or open question.\n6. Create stable requirements with rationale, evidence links, acceptance scenarios, dependencies,\n   exclusions, migration/parity expectation, confidence, approval state, and a revision token or content\n   fingerprint that changes when the approved behavior changes.\n7. Add reciprocal links among source, evidence, rule, gap, requirement, downstream specification, and test\n   planning. Keep requirement approval separate from specification, implementation, and validation status.\n8. Run readiness checks. Requirements with unresolved authority, missing acceptance criteria, or hard\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:research",
        "eval:skill-evaluations",
        "overlay:evidence-traceability",
        "skill:analyze-legacy-system",
        "skill:build-living-dashboard",
        "skill:continue-project",
        "skill:migrate-code-with-evidence",
        "skill:specify-openspec-change"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "research"
      ]
    },
    {
      "key": "skill:design-frontend-architecture",
      "id": "design-frontend-architecture",
      "name": "Design Frontend Architecture",
      "type": "skill",
      "path": "skills/design-frontend-architecture/SKILL.md",
      "description": "Define configurable frontend boundaries, rendering and data-flow choices, state ownership, module contracts, route composition, failure states, and design-system consumption from verified product and design-guide constraints. Use before material frontend foundations or cross-feature changes. Do not use for visual styling, task sequencing, a small local component edit, or target decisions unsupported by requirements.",
      "purpose": "Define configurable frontend boundaries, rendering and data-flow choices, state ownership, module contracts, route composition, failure states, and design-system consumption from verified product and design-guide constraints",
      "use_when": [
        "before material frontend foundations or cross-feature changes"
      ],
      "not_when": [
        "for visual styling, task sequencing, a small local component edit, or target decisions unsupported by requirements"
      ],
      "inputs": [],
      "workflow": [
        "Normalize the design guide",
        "Define boundaries",
        "Validate"
      ],
      "outputs": [],
      "validation": [],
      "tags": [
        "frontend-architecture-design"
      ],
      "search_terms": [
        "Design Frontend Architecture",
        "design-frontend-architecture",
        "frontend-architecture-design"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: design-frontend-architecture\ndescription: Define configurable frontend boundaries, rendering and data-flow choices, state ownership, module contracts, route composition, failure states, and design-system consumption from verified product and design-guide constraints. Use before material frontend foundations or cross-feature changes. Do not use for visual styling, task sequencing, a small local component edit, or target decisions unsupported by requirements.\n---\n\n# Design frontend architecture\n\nStart from accepted journeys, repository evidence, delivery constraints, deployment shape, and the supplied\ndesign guide. Use `frontend-design` when the visual thesis or interaction language is unresolved, and use\n`plan-work` after the architecture is accepted to sequence implementation.\n\n## Normalize the design guide\n\nCapture the configurable inputs in `references/design-guide-contract.md`. A project may use\n`assets/frontend-architecture-profile.example.json` as a starting shape, but project evidence remains\nauthoritative. Separate accepted constraints from proposals and unknowns.\n\n## Define boundaries\n\n1. Map application shells, routes, features, shared primitives, infrastructure adapters, and external\n   integrations. Give every responsibility one narrow owner.\n2. Select rendering, hydration, caching, offline, and deployment behavior from observable requirements;\n   do not choose infrastructure for fashion or hypothetical scale.\n3. Give each feature a public boundary, local tests, and explicit dependencies. Prevent cross-feature\n   imports of private internals.\n4. Assign server, URL, session, application, feature, component, and form state to the narrowest durable\n   owner. Define reset, replay, concurrency, and stale-data behavior where relevant.\n5. Put remote data, persistence, platform APIs, analytics, and generated clients behind typed contracts.\n6. Define loading, empty, unavailable, partial, stale, error, retry, authorization, and not-found behavior.\n7. Consume design tokens, components, accessibility rules, content density, and responsive behavior from\n   the design guide without silently redefining the visual language.\n8. Record decisions, alternatives, trade-offs, assumptions, migration seams, and validation evidence.\n\n## Validate\n\nCheck dependency direction, route ownership, state lifetime, contract substitutions, representative failure\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "eval:skill-evaluations",
        "skill:frontend-design",
        "skill:plan-work"
      ],
      "archetypes": [
        "development"
      ]
    },
    {
      "key": "skill:design-test-strategy",
      "id": "design-test-strategy",
      "name": "Design Test Strategy",
      "type": "skill",
      "path": "skills/design-test-strategy/SKILL.md",
      "description": "Design a risk-based test strategy that maps observable behavior and failure modes to the smallest credible portfolio of unit, contract, integration, browser, migration, security, performance, and end-to-end tests. Use before implementation, for coverage gaps, or when test-layer choice is disputed. Do not use to write production behavior, inflate coverage metrics, mandate every test layer, or replace focused TDD execution.",
      "purpose": "Design a risk-based test strategy that maps observable behavior and failure modes to the smallest credible portfolio of unit, contract, integration, browser, migration, security, performance, and end-to-end tests",
      "use_when": [
        "before implementation, for coverage gaps, or when test-layer choice is disputed"
      ],
      "not_when": [
        "to write production behavior, inflate coverage metrics, mandate every test layer, or replace focused TDD execution"
      ],
      "inputs": [],
      "workflow": [
        "Model risk",
        "Select layers",
        "Produce the strategy"
      ],
      "outputs": [],
      "validation": [],
      "tags": [
        "characterization",
        "legacy oracle",
        "legacy-oracle-authority",
        "legacy-test-readiness",
        "risk-based-test-strategy",
        "scenario only",
        "test layers",
        "test readiness",
        "test strategy",
        "test-layer-selection"
      ],
      "search_terms": [
        "characterization",
        "Design Test Strategy",
        "design-test-strategy",
        "legacy oracle",
        "legacy-oracle-authority",
        "legacy-test-readiness",
        "risk-based-test-strategy",
        "scenario only",
        "test layers",
        "test readiness",
        "test strategy",
        "test-layer-selection"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: design-test-strategy\ndescription: Design a risk-based test strategy that maps observable behavior and failure modes to the smallest credible portfolio of unit, contract, integration, browser, migration, security, performance, and end-to-end tests. Use before implementation, for coverage gaps, or when test-layer choice is disputed. Do not use to write production behavior, inflate coverage metrics, mandate every test layer, or replace focused TDD execution.\n---\n\n# Design a test strategy\n\nStart from accepted behavior, architecture boundaries, users, data, operational context, change surface,\nknown defects, and verification constraints. Coverage percentage is supporting data, not the objective.\n\nWhen expected behavior comes from a legacy system, generated rule package, characterization run, or other\nsource-derived evidence, read `references/legacy-oracle-readiness.md` before selecting executable tests. A\nsource observation is not automatically approved target intent, and a generated expected sentence is not an\noracle.\n\n## Model risk\n\nFor each behavior or failure mode, assess impact, likelihood, detectability, blast radius, reversibility,\nboundary count, data sensitivity, concurrency, external dependency, migration or compatibility risk, and\ncost of a late discovery. Identify the evidence needed to believe the risk is controlled.\n\n## Select layers\n\nChoose the lowest layer that can credibly observe the failure, then add higher layers only for boundaries\nor emergent behavior:\n\n- unit or component tests for local rules, transformations, and edge cases;\n- contract tests for schemas, protocol semantics, compatibility, and provider/consumer expectations;\n- integration tests for persistence, messaging, frameworks, transactions, and real dependency wiring;\n- browser or UI tests for user journeys, state transitions, rendering, and interaction contracts;\n- migration or characterization tests for source parity, data conversion, reconciliation, and rollback;\n- security tests for authorization, isolation, hostile input, secrets, and abuse paths;\n- performance tests for explicit latency, throughput, resource, or scale risks;\n- end-to-end tests for a small set of critical cross-system outcomes.\n\n## Produce the strategy\n\nReturn a risk-to-test matrix with behavior or threat, risk, chosen layer, fixture or environment, oracle,\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "eval:skill-evaluations",
        "skill:deconstruct-problem-first-principles",
        "skill:generate-synthetic-fixtures",
        "skill:mutation-testing",
        "skill:test-driven-development",
        "skill:verify-openspec-implementation"
      ],
      "archetypes": [
        "development",
        "legacy-migration"
      ]
    },
    {
      "key": "skill:estimate-adm-modernization",
      "id": "estimate-adm-modernization",
      "name": "Estimate ADM Modernization",
      "type": "skill",
      "path": "skills/estimate-adm-modernization/SKILL.md",
      "description": "Scope, calibrate, aggregate, and independently review evidence-linked ADM modernization effort using non-overlapping outcome-based work units and three-point person-day estimates. Use for application development and maintenance migration, rewrite, replatform, remediation, testing, data conversion, integration replacement, cutover, or decommissioning scenarios. Do not use before source coverage and target outcomes are bounded, to convert source size directly into effort, or to present an unreviewed range as a commitment, schedule, staffing plan, or cost.",
      "purpose": "Scope, calibrate, aggregate, and independently review evidence-linked ADM modernization effort using non-overlapping outcome-based work units and three-point person-day estimates",
      "use_when": [
        "for application development and maintenance migration, rewrite, replatform, remediation, testing, data conversion, integration replacement, cutover, or decommissioning scenarios"
      ],
      "not_when": [
        "before source coverage and target outcomes are bounded, to convert source size directly into effort, or to present an unreviewed range as a commitment, schedule, staffing plan, or cost"
      ],
      "inputs": [],
      "workflow": [
        "Scope",
        "Estimate",
        "Review",
        "Completion"
      ],
      "outputs": [],
      "validation": [],
      "tags": [
        "adm-modernization-estimation",
        "modernization-effort-estimation"
      ],
      "search_terms": [
        "adm-modernization-estimation",
        "Estimate ADM Modernization",
        "estimate-adm-modernization",
        "modernization-effort-estimation"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: estimate-adm-modernization\ndescription: Scope, calibrate, aggregate, and independently review evidence-linked ADM modernization effort using non-overlapping outcome-based work units and three-point person-day estimates. Use for application development and maintenance migration, rewrite, replatform, remediation, testing, data conversion, integration replacement, cutover, or decommissioning scenarios. Do not use before source coverage and target outcomes are bounded, to convert source size directly into effort, or to present an unreviewed range as a commitment, schedule, staffing plan, or cost.\n---\n\n# Estimate ADM modernization effort\n\nTreat ADM estimation as four gates: scope, estimate, deterministic aggregation, and independent review.\nRequire a current source fingerprint, canonical evidence, one coherent modernization scenario, target\narchitecture, delivery model, explicit coverage, and an identified estimation unit.\n\nLoad the compact project synopsis and only the analysis, requirements, architecture, complexity, dependency,\ndata, integration, and uncertainty records relevant to the selected scenario. Resolve every driver back to\ncanonical evidence; do not reload the whole source estate merely to assemble the estimate.\n\nRead `references/work-unit-model.md` before decomposition, `references/estimation-model.md` before assigning\neffort, and `references/review-checklist.md` before publication. Use\n`references/adm-estimation-package.schema.json` as the portable package contract.\n\n## Scope\n\n1. Define the outcome, strategy, inclusions, exclusions, assumptions, quality obligations, and source\n   denominator. Keep materially different strategies as separate scenarios.\n2. Decompose capabilities and requirements into non-overlapping work units that deliver reviewable target\n   outcomes. Files, programs, lines, graph nodes, and generated stories are evidence signals, not units of\n   delivery by themselves.\n3. Add explicit data, integration, batch, security, observability, environment, test, performance, cutover,\n   coexistence, discovery, and retirement units when applicable.\n4. Link each unit to available source artifacts, requirements, capabilities, dependencies, evidence, and\n   unresolved questions. Preserve unknown dimensions instead of extrapolating silently.\n… preview truncated",
      "related_capabilities": [
        "archetype:legacy-migration",
        "eval:skill-evaluations",
        "skill:forecast-project-financials",
        "tool:summarize-adm-estimate"
      ],
      "archetypes": [
        "legacy-migration"
      ]
    },
    {
      "key": "skill:execute-safe-change",
      "id": "execute-safe-change",
      "name": "Execute Safe Change",
      "type": "skill",
      "path": "skills/execute-safe-change/SKILL.md",
      "description": "Plan and execute an authorized state-changing operation with exact target binding, a genuinely non-mutating dry run, locks, idempotency, checkpoints, redacted audit evidence, bounded retries, verification, and rollback readiness. Use for consequential repository, infrastructure, account, data, or service mutations. Do not use for read-only analysis, vague bulk authorization, irreversible actions without an accepted recovery plan, or adapters whose dry-run path can still write.",
      "purpose": "Plan and execute an authorized state-changing operation with exact target binding, a genuinely non-mutating dry run, locks, idempotency, checkpoints, redacted audit evidence, bounded retries, verification, and rollback readiness",
      "use_when": [
        "for consequential repository, infrastructure, account, data, or service mutations"
      ],
      "not_when": [
        "for read-only analysis, vague bulk authorization, irreversible actions without an accepted recovery plan, or adapters whose dry-run path can still write"
      ],
      "inputs": [],
      "workflow": [
        "Bind authorization and plan",
        "Prove the dry run",
        "Execute",
        "Verify and recover"
      ],
      "outputs": [],
      "validation": [],
      "tags": [
        "fail-closed-state-change"
      ],
      "search_terms": [
        "Execute Safe Change",
        "execute-safe-change",
        "fail-closed-state-change"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: execute-safe-change\ndescription: Plan and execute an authorized state-changing operation with exact target binding, a genuinely non-mutating dry run, locks, idempotency, checkpoints, redacted audit evidence, bounded retries, verification, and rollback readiness. Use for consequential repository, infrastructure, account, data, or service mutations. Do not use for read-only analysis, vague bulk authorization, irreversible actions without an accepted recovery plan, or adapters whose dry-run path can still write.\n---\n\n# Execute a state change safely\n\nFail closed whenever authorization, identity, scope, preconditions, or recovery is ambiguous.\n\n## Bind authorization and plan\n\n1. Resolve the actor, exact operation, full resource identities, environment, writable fields, quantity,\n   time window, protected targets, and approval authority.\n2. Capture current fingerprints, dependencies, locks, quotas, and rollback prerequisites.\n3. Produce an immutable operation plan with stable IDs, ordered actions, preconditions, expected effects,\n   verification, rollback, and abort thresholds. Re-plan after material drift.\n\n## Prove the dry run\n\nUse a separate adapter or code path that is structurally incapable of writes. It may resolve identities,\nread current state, evaluate policy, calculate the exact diff, and validate recovery. A boolean flag on the\nproduction mutation path is insufficient unless the implementation proves no write-capable call is reachable.\n\n## Execute\n\n1. Reconfirm authorization and target fingerprints immediately before mutation.\n2. Acquire the narrowest valid lock or concurrency guard.\n3. Apply idempotent actions in small recoverable batches with checkpoints and stable operation keys.\n4. Bound retries to classified transient failures; never retry authorization, identity, policy, or invariant\n   failures as though they were transient.\n5. Redact secrets and sensitive values from logs while preserving actor, plan ID, resource identity,\n   timestamps, decisions, outcomes, and hashes needed for audit.\n6. Stop on drift, unexpected cardinality, partial invariant failure, lost lock, exhausted retry budget, or\n   an unavailable verifier.\n\n## Verify and recover\n\nVerify intended postconditions and absence of prohibited effects using an independent read path. Reconcile\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "eval:skill-evaluations"
      ],
      "archetypes": [
        "development"
      ]
    },
    {
      "key": "skill:forecast-project-financials",
      "id": "forecast-project-financials",
      "name": "Forecast Project Financials",
      "type": "skill",
      "path": "skills/forecast-project-financials/SKILL.md",
      "description": "Build and maintain an evidence-backed project or engagement financial forecast from an approved baseline, actuals, remaining-work drivers, scenarios, and delivery evidence. Use for budget, revenue, cost, margin, cash, earned-value, variance, or estimate-at-completion decisions. Do not use for statutory accounting, tax or investment advice, unsupported commitments, or forecasts whose source data and assumptions cannot be identified.",
      "purpose": "Build and maintain an evidence-backed project or engagement financial forecast from an approved baseline, actuals, remaining-work drivers, scenarios, and delivery evidence",
      "use_when": [
        "for budget, revenue, cost, margin, cash, earned-value, variance, or estimate-at-completion decisions"
      ],
      "not_when": [
        "for statutory accounting, tax or investment advice, unsupported commitments, or forecasts whose source data and assumptions cannot be identified"
      ],
      "inputs": [],
      "workflow": [
        "Establish the boundary",
        "Build the forecast",
        "Explain movement and decisions",
        "Independent review",
        "Optional consulting-delivery profile",
        "Output and completion"
      ],
      "outputs": [],
      "validation": [],
      "tags": [
        "CPI",
        "EAC",
        "SPI",
        "earned-value-analysis",
        "estimate-at-completion",
        "financial forecast",
        "forecast-scenario-analysis",
        "margin",
        "project forecast",
        "project-financial-forecasting",
        "scenario",
        "variance"
      ],
      "search_terms": [
        "CPI",
        "EAC",
        "earned-value-analysis",
        "estimate-at-completion",
        "financial forecast",
        "Forecast Project Financials",
        "forecast-project-financials",
        "forecast-scenario-analysis",
        "margin",
        "project forecast",
        "project-financial-forecasting",
        "scenario",
        "SPI",
        "variance"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: forecast-project-financials\ndescription: Build and maintain an evidence-backed project or engagement financial forecast from an approved baseline, actuals, remaining-work drivers, scenarios, and delivery evidence. Use for budget, revenue, cost, margin, cash, earned-value, variance, or estimate-at-completion decisions. Do not use for statutory accounting, tax or investment advice, unsupported commitments, or forecasts whose source data and assumptions cannot be identified.\n---\n\n# Forecast project financials\n\nTreat a forecast as a dated decision model, not a confident narrative. Preserve the approved baseline,\nseparate actuals from estimates, expose the drivers, and show how uncertainty changes the outcome.\n\n## Establish the boundary\n\n1. Resolve the project or engagement scope, forecast horizon, currency, fiscal calendar, reporting basis,\n   approved baseline, materiality threshold, decision audience, and authoritative actuals.\n2. Record which measures are required: revenue, cost, margin, cash, headcount or capacity, planned value,\n   earned value, and commercial commitments. Do not invent unavailable measures.\n3. Keep actual, committed, forecast, scenario, and target values distinct. Never overwrite the baseline to\n   make current performance look aligned.\n4. Record confidentiality and access constraints. Use only authorized rate, staffing, pricing, utilization,\n   and client data; redact or aggregate outputs crossing a trust boundary.\n\n## Build the forecast\n\n1. Reconcile actuals through the as-of period to the authoritative ledger, approved time or cost system, and\n   delivery evidence. Record unresolved differences rather than forcing a tie.\n2. Forecast remaining work from explicit drivers: work packages, staffing, rates, utilization, productivity,\n   procurement, travel, subcontractors, milestones, billing rules, and delivery dependencies as applicable.\n   Prefer bottom-up drivers over a flat percentage extrapolation.\n3. Derive the base estimate at completion:\n   - actual-to-date plus forecast-to-complete;\n   - revenue, cost, margin and cash where available;\n   - budget and revenue variances with favorable or unfavorable direction stated;\n   - earned-value measures only when planned value, earned value, and actual cost use compatible scope,\n     periods, units, and status dates.\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:research",
        "eval:skill-evaluations",
        "overlay:consulting-delivery",
        "skill:estimate-adm-modernization",
        "skill:manage-project-delivery",
        "tool:calculate-project-financial-forecast"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "research"
      ]
    },
    {
      "key": "skill:frontend-design",
      "id": "frontend-design",
      "name": "Frontend Design",
      "type": "skill",
      "path": "skills/frontend-design/SKILL.md",
      "description": "Establish and implement a distinctive, intentional product-interface direction covering hierarchy, typography, responsive composition, component language, data density, and interaction states. Use for new application UI or material redesign where visual and product decisions are part of the work. Do not use for one-off narrative presentations, brand-only styling, small maintenance edits, or downstream validation of an already complete interface.",
      "purpose": "Establish and implement a distinctive, intentional product-interface direction covering hierarchy, typography, responsive composition, component language, data density, and interaction states",
      "use_when": [
        "for new application UI or material redesign where visual and product decisions are part of the work"
      ],
      "not_when": [
        "for one-off narrative presentations, brand-only styling, small maintenance edits, or downstream validation of an already complete interface"
      ],
      "inputs": [],
      "workflow": [
        "Choose a visual thesis",
        "Compose the product",
        "Implement deliberately",
        "Handoff"
      ],
      "outputs": [],
      "validation": [],
      "tags": [
        "frontend-product-design"
      ],
      "search_terms": [
        "Frontend Design",
        "frontend-design",
        "frontend-product-design"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: frontend-design\ndescription: Establish and implement a distinctive, intentional product-interface direction covering hierarchy, typography, responsive composition, component language, data density, and interaction states. Use for new application UI or material redesign where visual and product decisions are part of the work. Do not use for one-off narrative presentations, brand-only styling, small maintenance edits, or downstream validation of an already complete interface.\n---\n\n# Design a frontend product interface\n\nStart from the product job, users, environment, content, workflows, constraints, existing design system,\nand implementation stack. Preserve established conventions unless the task explicitly authorizes a redesign.\n\n## Choose a visual thesis\n\n1. State the experience in concrete terms: operational, editorial, technical, calm, dense, playful, or\n   another defensible direction grounded in the product.\n2. Define hierarchy, typography, spacing rhythm, color roles, surfaces, borders, iconography, imagery,\n   and motion as one coherent system.\n   Express repeated decisions through a compact token layer for type roles, content measures, section and\n   component spacing, border hierarchy, surfaces, radii, shadow, and transition timing.\n3. Avoid generic card grids, decorative gradients, excessive pills, stock dashboard chrome, and arbitrary\n   glass effects unless evidence supports them.\n4. Reuse a supplied design system or verified brand source before introducing new primitives.\n\n## Compose the product\n\nMap navigation, primary work, secondary context, empty/loading/error/success/disabled states, dense data,\nforms, destructive actions, and responsive transformations. Make the most important action and information\nvisually obvious without flattening everything into equal emphasis.\n\n## Implement deliberately\n\n1. Build reusable semantic components with explicit variants and state behavior.\n2. Keep responsiveness content-driven; test narrow, wide, zoomed, and touch contexts.\n3. Treat keyboard focus, contrast, reduced motion, readable type, and target size as design inputs, then\n   hand the completed artifact to `accessibility-review` for independent evidence.\n4. Use motion sparingly to communicate relationship, causality, or state.\n5. Inspect the real rendered interface throughout implementation, not only at the end.\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "eval:skill-evaluations",
        "skill:design-frontend-architecture",
        "skill:polish-html-artifact"
      ],
      "archetypes": [
        "development"
      ]
    },
    {
      "key": "skill:generate-synthetic-fixtures",
      "id": "generate-synthetic-fixtures",
      "name": "Generate Synthetic Fixtures",
      "type": "skill",
      "path": "skills/generate-synthetic-fixtures/SKILL.md",
      "description": "Build committed test fixtures by generating them deterministically from a reviewed allowlist specification instead of scrubbing sensitive originals, keeping the behavioral signal tests depend on while every identity value is an approved synthetic one. Use when a suite needs realistic documents or records derived from sensitive material that will live in version control. Do not use to transform an existing structured dataset for analysis, to purge sensitive data already committed to history, or to sanitize prose.",
      "purpose": "Build committed test fixtures by generating them deterministically from a reviewed allowlist specification instead of scrubbing sensitive originals, keeping the behavioral signal tests depend on while every identity value is an approved synthetic one",
      "use_when": [
        "when a suite needs realistic documents or records derived from sensitive material that will live in version control"
      ],
      "not_when": [
        "to transform an existing structured dataset for analysis, to purge sensitive data already committed to history, or to sanitize prose"
      ],
      "inputs": [],
      "workflow": [
        "Boundaries",
        "Establish the specification",
        "Generate deterministically",
        "Validate",
        "Completion and stop conditions"
      ],
      "outputs": [],
      "validation": [],
      "tags": [
        "allowlist specification",
        "deterministic fixture rendering",
        "sensitive-source-test-data",
        "synthetic fixtures",
        "synthetic-fixture-generation",
        "test data from sensitive documents"
      ],
      "search_terms": [
        "allowlist specification",
        "deterministic fixture rendering",
        "Generate Synthetic Fixtures",
        "generate-synthetic-fixtures",
        "sensitive-source-test-data",
        "synthetic fixtures",
        "synthetic-fixture-generation",
        "test data from sensitive documents"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: generate-synthetic-fixtures\ndescription: Build committed test fixtures by generating them deterministically from a reviewed allowlist specification instead of scrubbing sensitive originals, keeping the behavioral signal tests depend on while every identity value is an approved synthetic one. Use when a suite needs realistic documents or records derived from sensitive material that will live in version control. Do not use to transform an existing structured dataset for analysis, to purge sensitive data already committed to history, or to sanitize prose.\n---\n\n# Generate synthetic fixtures\n\nTests need fixtures that look like the real thing. The obvious route — take a real artifact and remove what\nis sensitive — fails in a way that is invisible: a missed field looks exactly like a clean file, and once\ncommitted it is in history forever. Redaction is a denylist, and a denylist is only as good as the last\nthing someone thought of.\n\nInvert it. Generate the fixture from a specification that contains only approved values, so **the\nspecification is the audit surface**. Reviewing one small declarative file is a task a human can actually\ncomplete; auditing a rendered artifact for what is missing is not.\n\n## Boundaries\n\nThis workflow produces new artifacts. It never edits a sensitive original in place, and no byte of a\nsensitive original reaches the committed fixture except through a value someone approved in the\nspecification.\n\nUse `anonymize-data` instead when the input is a structured dataset that must retain analytical utility\nand the field inventory is known and bounded. Use this workflow when the artifact is a document or record\nwhose value to the test is **behavioral signal** rather than data fidelity, and where a missed field would\nnot be visible on inspection. Sensitive data already committed to history is a separate authorized\noperation and is out of scope here.\n\n## Establish the specification\n\n1. Extract the structure of the source artifact — its sections, ordering, labels, and vocabulary — and\n   inventory every value that identifies a person, account, contract, device, or location. An\n   extract-and-flag helper may surface candidates, but it proposes; it never writes the replacement.\n2. Decide, value by value, which of two categories each one falls in, and record the decision:\n… preview truncated",
      "related_capabilities": [
        "eval:skill-evaluations",
        "skill:anonymize-data",
        "skill:design-test-strategy",
        "skill:review-privacy-security",
        "skill:test-driven-development"
      ],
      "archetypes": []
    },
    {
      "key": "skill:implement-openspec-change",
      "id": "implement-openspec-change",
      "name": "Implement OpenSpec Change",
      "type": "skill",
      "path": "skills/implement-openspec-change/SKILL.md",
      "description": "Implement one approved OpenSpec change task by task with scenario traceability, tests, and controlled artifact updates when learning invalidates the plan. Use when a specific existing change is implementation-ready and writable. Do not use for unapproved or ambiguous changes, speculative implementation before specs, bulk unrelated work, or silent divergence from the accepted specification.",
      "purpose": "Implement one approved OpenSpec change task by task with scenario traceability, tests, and controlled artifact updates when learning invalidates the plan",
      "use_when": [
        "when a specific existing change is implementation-ready and writable"
      ],
      "not_when": [
        "for unapproved or ambiguous changes, speculative implementation before specs, bulk unrelated work, or silent divergence from the accepted specification"
      ],
      "inputs": [
        "approved implementation-ready OpenSpec change",
        "project source and tests",
        "validation commands"
      ],
      "workflow": [
        "Bind the implementation contract",
        "Implement in traceable slices",
        "Handle learning without divergence",
        "Hand off for verification"
      ],
      "outputs": [
        "implemented OpenSpec tasks",
        "requirement scenario code and test links",
        "validation handoff"
      ],
      "validation": [],
      "tags": [
        "OpenSpec",
        "acceptance criteria",
        "implementation tasks",
        "openspec-guided-implementation",
        "spec-driven",
        "spec-first",
        "specification",
        "specification-to-code-traceability"
      ],
      "search_terms": [
        "acceptance criteria",
        "Implement OpenSpec Change",
        "implement-openspec-change",
        "implementation tasks",
        "OpenSpec",
        "openspec-guided-implementation",
        "spec-driven",
        "spec-first",
        "specification",
        "specification-to-code-traceability"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: implement-openspec-change\ndescription: Implement one approved OpenSpec change task by task with scenario traceability, tests, and controlled artifact updates when learning invalidates the plan. Use when a specific existing change is implementation-ready and writable. Do not use for unapproved or ambiguous changes, speculative implementation before specs, bulk unrelated work, or silent divergence from the accepted specification.\n---\n\n# Implement an approved OpenSpec change\n\nSpecification and acceptance criteria precede implementation. Work from one existing approved change; do\nnot create a replacement proposal during implementation.\n\n## Bind the implementation contract\n\nRetrieve only the selected specification, linked requirement revisions and scenarios, architecture decisions,\naffected components, dependency records, and necessary source/target paths. Do not load the entire analysis\nhistory for each implementation slice.\n\n1. Resolve the supplied stable specification ID, dashboard reference, or safe project-local OpenSpec path\n   to exactly one existing change. Load its linked requirements, acceptance criteria, dependency graph,\n   source evidence, implementation state, and validation commands. Reject path escapes and ambiguous IDs.\n2. Read governance, Git state, OpenSpec project configuration, main specs, the selected change, current\n   artifacts, source, tests, and validation commands.\n3. Confirm the exact active change and approval state. Run `openspec status --change \u003cname> --json` and obtain\n   current apply guidance with `openspec instructions apply --change \u003cname> --json` when available.\n4. Refuse implementation if required artifacts, acceptance scenarios, dependencies, ownership, or a runnable\n   validation path are missing. A structurally valid change can still be semantically unready.\n5. Preserve unrelated work and keep project-local OpenSpec state in the project.\n\n## Implement in traceable slices\n\nWork through the approved `tasks.md` in dependency order. Use `implement-ready-slice` to claim and hand off\neach material vertical slice; this skill retains change-level progress and mismatch handling. For each\nbounded slice:\n\n1. identify the authorizing requirement and scenario;\n2. select the narrowest credible test or observable verification;\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "eval:skill-evaluations",
        "skill:continue-project",
        "skill:implement-ready-slice",
        "skill:mutation-testing",
        "skill:review-openspec-change",
        "skill:specify-openspec-change",
        "skill:test-driven-development",
        "skill:verify-openspec-implementation"
      ],
      "archetypes": [
        "development"
      ]
    },
    {
      "key": "skill:implement-ready-slice",
      "id": "implement-ready-slice",
      "name": "Implement Ready Slice",
      "type": "skill",
      "path": "skills/implement-ready-slice/SKILL.md",
      "description": "Deterministically shortlist, claim, implement, validate, and hand off one dependency-ready vertical slice with acceptance-scenario traceability, using recorded red-green-refactor evidence by default. Use for an approved queue or an explicitly selected bounded feature. Do not use for tiny unqueued edits, blocked or unapproved behavior, externally owned work, or tasks without a runnable validation path.",
      "purpose": "Deterministically shortlist, claim, implement, validate, and hand off one dependency-ready vertical slice with acceptance-scenario traceability, using recorded red-green-refactor evidence by default",
      "use_when": [
        "for an approved queue or an explicitly selected bounded feature"
      ],
      "not_when": [
        "for tiny unqueued edits, blocked or unapproved behavior, externally owned work, or tasks without a runnable validation path"
      ],
      "inputs": [],
      "workflow": [
        "Select and claim",
        "Prepare",
        "Default recorded TDD loop",
        "Atomic progress and stall recovery",
        "Stop conditions"
      ],
      "outputs": [],
      "validation": [],
      "tags": [
        "acceptance-validation",
        "target-architecture-design",
        "target-implementation"
      ],
      "search_terms": [
        "acceptance-validation",
        "Implement Ready Slice",
        "implement-ready-slice",
        "target-architecture-design",
        "target-implementation"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: implement-ready-slice\ndescription: Deterministically shortlist, claim, implement, validate, and hand off one dependency-ready vertical slice with acceptance-scenario traceability, using recorded red-green-refactor evidence by default. Use for an approved queue or an explicitly selected bounded feature. Do not use for tiny unqueued edits, blocked or unapproved behavior, externally owned work, or tasks without a runnable validation path.\n---\n\n# Implement one ready slice\n\nCombine deterministic selection with semantic review; do not select from memory alone.\n\n## Select and claim\n\n1. Read governance, canonical requirements/specifications, dependencies, decisions, active claims, Git\n   state, and existing implementation/tests.\n2. When the invocation supplies a requirement ID or path, resolve it through the project continuation\n   resolver. Follow all linked OpenSpec specifications, requirement revisions, acceptance criteria,\n   dependencies, and implementation state; do not require the user to locate the specification manually.\n   If no approved implementation specification exists, delegate to `specify-openspec-change`, then\n   `review-openspec-change`, and stop before code until readiness is established. If several specifications\n   apply, honor dependency order and combined scope or request a selection when the order is ambiguous.\n3. Preserve unrelated changes. Stop if ownership overlaps or the writable boundary is unclear.\n4. Run `scripts/rank_slices.py \u003cqueue.json>` when the project can export the normalized queue described\n   in `references/queue-contract.md`.\n5. Review the top candidates semantically. Reject external-only, decision-blocked, non-observable, or\n   deceptively broad work. Record why any higher-ranked candidate was skipped.\n6. Claim through the project's canonical ledger using a stable owner and bounded branch/task ID. A claim\n   is not completion.\n\nFor a coordinator-managed parallel queue, include exact `write_paths` and mutable `shared_surfaces` from\n`references/queue-contract.md` in the execution planner. A ranked item is not safe to run concurrently until\ndependency, ownership, isolation, and shared-resource conflicts have been checked.\n\n## Prepare\n\nBuild a bounded context package for the claimed requirement/specification, acceptance scenarios, affected\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "eval:skill-evaluations",
        "skill:continue-project",
        "skill:implement-openspec-change",
        "skill:mutation-testing",
        "skill:test-driven-development",
        "skill:validate-work-item-assumptions",
        "skill:verify-openspec-implementation",
        "tool:rank-ready-slices"
      ],
      "archetypes": [
        "development"
      ]
    },
    {
      "key": "skill:initialize-project",
      "id": "initialize-project",
      "name": "Initialize Project",
      "type": "skill",
      "path": "skills/initialize-project/SKILL.md",
      "description": "Adaptively bootstrap an empty, nearly empty, or existing project for legacy modernization, development, research, presentations, or a composition. Use when explicitly initializing a workspace or selecting commons composition. Do not use for ordinary work in an established project, bulk-copy the library, overwrite existing files, or add durable process to a tiny task.",
      "purpose": "Adaptively bootstrap an empty, nearly empty, or existing project for legacy modernization, development, research, presentations, or a composition",
      "use_when": [
        "when explicitly initializing a workspace or selecting commons composition"
      ],
      "not_when": [
        "for ordinary work in an established project, bulk-copy the library, overwrite existing files, or add durable process to a tiny task"
      ],
      "inputs": [],
      "workflow": [
        "Discover before asking",
        "Two supported intake modes",
        "First interaction",
        "Scope follow-up",
        "Interpret natural-language composition",
        "Public-sector client delivery",
        "Compose the project",
        "Project references",
        "Detect capability gaps",
        "External discovery boundary",
        "Accepted external capabilities",
        "Validate and hand off"
      ],
      "outputs": [],
      "validation": [],
      "tags": [
        "adaptive-project-initialization",
        "client locale",
        "client-sector-detection",
        "dashboard language",
        "initialize",
        "output-specific-language-policy",
        "presentation language",
        "public sector"
      ],
      "search_terms": [
        "adaptive-project-initialization",
        "client locale",
        "client-sector-detection",
        "dashboard language",
        "initialize",
        "Initialize Project",
        "initialize-project",
        "output-specific-language-policy",
        "presentation language",
        "public sector"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: initialize-project\ndescription: Adaptively bootstrap an empty, nearly empty, or existing project for legacy modernization, development, research, presentations, or a composition. Use when explicitly initializing a workspace or selecting commons composition. Do not use for ordinary work in an established project, bulk-copy the library, overwrite existing files, or add durable process to a tiny task.\n---\n\n# Initialize a project\n\nBuild the smallest recoverable project structure that supports the actual goal.\n\n## Discover before asking\n\n1. Inspect the current directory, Git state, instruction files, manifests, source roots, documents,\n   and supplied assets without opening secrets or generated/dependency trees.\n2. Separate discoverable facts from choices only the user can make.\n3. Preserve existing files and conventions. Do not overwrite or reinitialize an established project.\n\nFor a standard substantial workflow, create a lightweight dependency DAG immediately after parsing the\nbrief. Treat source inspection, supplied-brand inspection, Commons resolution, and existing-environment\ninspection as sibling branches. Use `coordinate-parallel-agents` when two or more branches are genuinely\nindependent; keep tiny work single-agent. The coordinator owns fan-in, canonical IDs, shared files,\nprogress truth, and final validation.\n\n## Two supported intake modes\n\n- **Interactive:** with no supplied brief, inspect the workspace and ask a small adaptive sequence. Do not\n  require a fixed questionnaire before making progress.\n- **Brief-driven:** when the invocation includes natural-language project context, extract everything the\n  user already supplied, inspect allowed source locations, and ask only for important unresolved choices.\n\nBefore asking, classify intake facts as `KNOWN` when explicitly supplied, `DISCOVERED` when verified from\nthe workspace or source locations, `INFERRED` when they are high-confidence consequences of the brief, and\n`MISSING` when a decision still materially affects setup. Questions normally come only from `MISSING`.\nConfirm an inference only when uncertainty could materially change scope or generated state.\n\nFor migration briefs, extract source technology, target technology, and migration intent separately.\n`prepare migration` means planning, mapping, sequencing, readiness, and backlog preparation; it does not\n… preview truncated",
      "related_capabilities": [
        "eval:initializer-evaluations",
        "eval:natural-language-initializer-evaluations",
        "eval:skill-evaluations",
        "skill:continue-project",
        "skill:promote-to-commons"
      ],
      "archetypes": []
    },
    {
      "key": "skill:inventory-codebase",
      "id": "inventory-codebase",
      "name": "Inventory Codebase",
      "type": "skill",
      "path": "skills/inventory-codebase/SKILL.md",
      "description": "Build a deterministic, bounded inventory of a repository or legacy source tree before interpretation. Use when the denominator, exclusions, classifications, hashes, batches, or drift must be established for broad analysis. Do not use for a small already-supplied file set, to infer behavior from paths, or as a substitute for source analysis.",
      "purpose": "Build a deterministic, bounded inventory of a repository or legacy source tree before interpretation",
      "use_when": [
        "when the denominator, exclusions, classifications, hashes, batches, or drift must be established for broad analysis"
      ],
      "not_when": [
        "for a small already-supplied file set, to infer behavior from paths, or as a substitute for source analysis"
      ],
      "inputs": [],
      "workflow": [
        "Procedure",
        "Failure rules",
        "Completion"
      ],
      "outputs": [],
      "validation": [],
      "tags": [
        "repository-discovery",
        "source-boundary-validation",
        "source-inventory"
      ],
      "search_terms": [
        "Inventory Codebase",
        "inventory-codebase",
        "repository-discovery",
        "source-boundary-validation",
        "source-inventory"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: inventory-codebase\ndescription: Build a deterministic, bounded inventory of a repository or legacy source tree before interpretation. Use when the denominator, exclusions, classifications, hashes, batches, or drift must be established for broad analysis. Do not use for a small already-supplied file set, to infer behavior from paths, or as a substitute for source analysis.\n---\n\n# Inventory a codebase\n\nProve the denominator before making completeness claims.\n\n## Procedure\n\n1. Confirm the exact root, allowed scope, protected paths, exclusions, symlink policy, and output path.\n2. Enumerate path metadata before reading contents. Prune VCS internals, dependencies, caches, build\n   output, credentials, environment files, and explicitly protected directories.\n3. Run:\n\n   ```bash\n   python3 scripts/inventory_codebase.py --root \u003croot> --output \u003cinventory.json> --hash\n   ```\n\n4. Review uncertain `other` classifications. Treat names and metadata as navigation clues, never\n   behavioral evidence.\n5. Give every eligible path one stable ID, classification, disposition, and reason. Retain unreadable\n   items as failures rather than silently omitting them. Record both file-operation failures and\n   directory-traversal failures through the walker's error callback, using repository-relative paths.\n6. Create stable, non-overlapping analysis batches from sorted paths and subsystem/language boundaries. Keep\n   legacy support artifacts such as copybooks, PL/I includes, CICS resource definitions, contracts, build\n   descriptors, and runtime configuration eligible when they participate in the authorized system.\n7. Reconcile eligible count, disposition count, and batch ownership. Store the exclusion policy and\n   inventory fingerprint with the output.\n8. When refreshing, compare path hashes; preserve IDs for unchanged files and mark changed analyzed\n   items for review.\n\nThe output stores `root: .` by default so a committed inventory does not expose a username or workstation\npath. Pass a synthetic repository-relative `--root-label` only when multiple authorized roots must be\ndistinguished.\n\n## Failure rules\n\nFail on a wrong root, duplicate normalized paths/IDs, symlinks escaping the root, unreasoned omissions,\nmissing hashes when required, overlapping primary ownership, or any access to protected paths. Do not\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "eval:skill-evaluations",
        "skill:analyze-legacy-system",
        "tool:inventory-codebase-tool"
      ],
      "archetypes": [
        "development",
        "legacy-migration"
      ]
    },
    {
      "key": "skill:localize-client-artifact",
      "id": "localize-client-artifact",
      "name": "Localize Client Artifact",
      "type": "skill",
      "path": "skills/localize-client-artifact/SKILL.md",
      "description": "Transform an existing standalone client-facing HTML dashboard, presentation, technical narrative, or management artifact into one bilingual offline artifact while preserving design, data, evidence, interactions, and technical identifiers. Use for German/English client delivery, public-sector dashboard delivery, translation of an existing HTML artifact, or adding a persistent accessible language switch. Do not use for ordinary sentence translation, runtime translation services, separate per-language HTML copies, initial artifact design, or non-HTML deliverables.",
      "purpose": "Transform an existing standalone client-facing HTML dashboard, presentation, technical narrative, or management artifact into one bilingual offline artifact while preserving design, data, evidence, interactions, and technical identifiers",
      "use_when": [
        "for German/English client delivery, public-sector dashboard delivery, translation of an existing HTML artifact, or adding a persistent accessible language switch"
      ],
      "not_when": [
        "for ordinary sentence translation, runtime translation services, separate per-language HTML copies, initial artifact design, or non-HTML deliverables"
      ],
      "inputs": [],
      "workflow": [
        "Establish the delivery contract",
        "Inventory every client-facing string",
        "Introduce the smallest localization structure",
        "Translate with semantic control",
        "Add the standard language control",
        "Update incrementally",
        "Validate both languages"
      ],
      "outputs": [],
      "validation": [],
      "tags": [
        "Austrian German",
        "English",
        "German",
        "German client",
        "bilingual",
        "bilingual-html-delivery",
        "client-artifact-localization",
        "de-AT",
        "de-CH",
        "de-DE",
        "language switch",
        "locale-aware-german-localization",
        "localization",
        "state-preserving-language-switch",
        "translation"
      ],
      "search_terms": [
        "Austrian German",
        "bilingual",
        "bilingual-html-delivery",
        "client-artifact-localization",
        "de-AT",
        "de-CH",
        "de-DE",
        "English",
        "German",
        "German client",
        "language switch",
        "locale-aware-german-localization",
        "localization",
        "Localize Client Artifact",
        "localize-client-artifact",
        "state-preserving-language-switch",
        "translation"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: localize-client-artifact\ndescription: Transform an existing standalone client-facing HTML dashboard, presentation, technical narrative, or management artifact into one bilingual offline artifact while preserving design, data, evidence, interactions, and technical identifiers. Use for German/English client delivery, public-sector dashboard delivery, translation of an existing HTML artifact, or adding a persistent accessible language switch. Do not use for ordinary sentence translation, runtime translation services, separate per-language HTML copies, initial artifact design, or non-HTML deliverables.\n---\n\n# Localize a client artifact\n\nPreserve the artifact and add a localization layer; do not redesign it or fork the whole DOM.\n\n## Establish the delivery contract\n\n1. Confirm the artifact path, working language, client language, default language, fallback language,\n   offline requirement, persistence preference, and client or project glossary.\n2. Resolve the German locale from persisted client context: `de-AT` for Austria, `de-DE` for Germany,\n   and `de-CH` for Switzerland. Use professional Standard German, never dialect. Do not force Austrian\n   terminology onto a clearly German or Swiss client.\n3. Keep English-first internal work lightweight. Localize at the client-delivery boundary unless the\n   project explicitly needs bilingual behavior earlier.\n4. Read `references/localization-contract.md` before changing the artifact. Reuse client terminology from\n   supplied authoritative material when available, but never send client content to an external\n   translation service without explicit authorization.\n\n## Inventory every client-facing string\n\nInspect static HTML and runtime-generated content in JavaScript, embedded JSON, SVG, charts, tooltips,\nmodals, navigation, filters, tables, diagrams, accessibility labels, print/export text, metadata, empty\nstates, and error states. Separate:\n\n- translatable presentation prose and human-readable labels;\n- language-independent data, numbers, dates, evidence, and canonical state;\n- protected source identifiers, product names, paths, commands, code, endpoints, keys, and quotations.\n\nDo not translate source-code identifiers, class or method names, service or application names, repository\nnames, API endpoints, table names, filenames, configuration keys, commands, snippets, vendor products, or\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "eval:skill-evaluations",
        "overlay:bilingual-client-delivery",
        "skill:build-living-dashboard",
        "skill:create-branded-html-artifact",
        "skill:validate-visual-artifact",
        "tool:validate-client-localization"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "skill:maintain-project-memory",
      "id": "maintain-project-memory",
      "name": "Maintain Project Memory",
      "type": "skill",
      "path": "skills/maintain-project-memory/SKILL.md",
      "description": "Create, retrieve, validate, checkpoint, invalidate, compact, and rebuild hierarchical evidence-backed project knowledge for substantial multi-session work. Use automatically when recovery cost, repeated analysis, or coordinated workflows justify durable context. Do not use for tiny tasks, hidden reasoning, a second source of truth, or replacement of canonical evidence, requirements, specifications, code, or tests.",
      "purpose": "Create, retrieve, validate, checkpoint, invalidate, compact, and rebuild hierarchical evidence-backed project knowledge for substantial multi-session work",
      "use_when": [
        "automatically when recovery cost, repeated analysis, or coordinated workflows justify durable context"
      ],
      "not_when": [
        "for tiny tasks, hidden reasoning, a second source of truth, or replacement of canonical evidence, requirements, specifications, code, or tests"
      ],
      "inputs": [],
      "workflow": [
        "Authority and storage",
        "Automatic read-before-work",
        "Controlled updates and checkpoints",
        "Source drift, compaction, and rebuild",
        "Manual operations",
        "Completion"
      ],
      "outputs": [],
      "validation": [],
      "tags": [
        "checkpoint",
        "compact",
        "context package",
        "context-efficiency-benchmarking",
        "hierarchical-context-retrieval",
        "persistent memory",
        "persistent-project-knowledge",
        "project memory",
        "project-checkpointing",
        "resume",
        "retrieve prior findings",
        "selective-memory-invalidation"
      ],
      "search_terms": [
        "checkpoint",
        "compact",
        "context package",
        "context-efficiency-benchmarking",
        "hierarchical-context-retrieval",
        "Maintain Project Memory",
        "maintain-project-memory",
        "persistent memory",
        "persistent-project-knowledge",
        "project memory",
        "project-checkpointing",
        "resume",
        "retrieve prior findings",
        "selective-memory-invalidation"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: maintain-project-memory\ndescription: Create, retrieve, validate, checkpoint, invalidate, compact, and rebuild hierarchical evidence-backed project knowledge for substantial multi-session work. Use automatically when recovery cost, repeated analysis, or coordinated workflows justify durable context. Do not use for tiny tasks, hidden reasoning, a second source of truth, or replacement of canonical evidence, requirements, specifications, code, or tests.\n---\n\n# Maintain project memory\n\nExternalize verified project knowledge so agents can resume complex work without replaying the conversation or\nreloading the complete repository. Memory optimizes retrieval, not reasoning depth.\n\n## Authority and storage\n\nUse this authority order: source/input and current runtime evidence; canonical structured analysis;\nrequirements and specifications; project memory/index; generated dashboard or presentation; chat recollection.\nWhen memory conflicts with a higher source, mark it `STALE` or `CONFLICTING` and refresh it.\n\nKeep machine-owned memory under `.agent-commons/memory/`, never a top-level `memory/`. Read\n`references/memory-contract.md` before changing the format. The hierarchy is:\n\n- L0: `state.json` plus a generated tiny `project-summary.md`, loaded for most substantial tasks;\n- L1: `domains/\u003cdomain>.json`, loaded only for relevant technologies or work domains;\n- L2: `entities/\u003cstable-id>.json`, loaded for selected components, flows, rules, data, or delivery objects;\n- EVIDENCE: project-local canonical paths, stable IDs, coordinates, hashes, and revisions retained by reference.\n\nNever store chain-of-thought, conversations, secrets, credentials, private raw logs, copied source bodies, or\nunsupported conclusions. Store facts, decisions by canonical link, state, relationships, confidence, unknowns,\nconflicts, and evidence pointers.\n\n## Automatic read-before-work\n\nFor a substantial workflow, inspect L0 and the memory index before expensive work. Check whether relevant\nrecords exist, whether their source fingerprints remain current, and which domains/entities the task needs.\nBuild a bounded package with `scripts/manage_project_memory.py read`; load source directly only for new,\nstale, conflicting, unknown, or verification-sensitive areas.\n\nClassify requested context as mandatory, useful, or irrelevant. Prefer the minimum sufficient verified\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "eval:skill-evaluations",
        "overlay:durable-state",
        "skill:analyze-legacy-system",
        "skill:continue-project",
        "skill:coordinate-parallel-agents",
        "tool:manage-project-memory"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "skill:manage-project-delivery",
      "id": "manage-project-delivery",
      "name": "Manage Project Delivery",
      "type": "skill",
      "path": "skills/manage-project-delivery/SKILL.md",
      "description": "Establish and operate evidence-backed delivery governance across workstreams, dependencies, milestones, decisions, risks, actions, and status reporting. Use for multi-workstream projects or programs that need repeatable coordination and truthful health reporting. Do not use to define product requirements, implement delivery tasks, replace an established tracker, or present schedule and health claims without current evidence.",
      "purpose": "Establish and operate evidence-backed delivery governance across workstreams, dependencies, milestones, decisions, risks, actions, and status reporting",
      "use_when": [
        "for multi-workstream projects or programs that need repeatable coordination and truthful health reporting"
      ],
      "not_when": [
        "to define product requirements, implement delivery tasks, replace an established tracker, or present schedule and health claims without current evidence"
      ],
      "inputs": [],
      "workflow": [
        "Establish the delivery contract",
        "Build the delivery model",
        "Operate the cadence",
        "Health and escalation",
        "Optional consulting-delivery profile",
        "Output and completion"
      ],
      "outputs": [],
      "validation": [],
      "tags": [
        "RAID",
        "delivery governance",
        "dependency-aware-delivery-health",
        "milestone",
        "project management",
        "project-delivery-governance",
        "raid-management",
        "status report",
        "steering",
        "steering-status",
        "workstream"
      ],
      "search_terms": [
        "delivery governance",
        "dependency-aware-delivery-health",
        "Manage Project Delivery",
        "manage-project-delivery",
        "milestone",
        "project management",
        "project-delivery-governance",
        "RAID",
        "raid-management",
        "status report",
        "steering",
        "steering-status",
        "workstream"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: manage-project-delivery\ndescription: Establish and operate evidence-backed delivery governance across workstreams, dependencies, milestones, decisions, risks, actions, and status reporting. Use for multi-workstream projects or programs that need repeatable coordination and truthful health reporting. Do not use to define product requirements, implement delivery tasks, replace an established tracker, or present schedule and health claims without current evidence.\n---\n\n# Manage project delivery\n\nCoordinate the delivery system without becoming every delivery role. Keep the source of truth in the\nproject's approved tracker or canonical project state, and make status a reproducible interpretation of that\nevidence rather than a narrative assembled from memory.\n\n## Establish the delivery contract\n\n1. Resolve the objective, measurable outcomes, scope and non-goals, sponsor or decision owner, delivery\n   owner, workstream owners, reporting audience, cadence, calendar, and authoritative systems.\n2. Reuse an established tracker and identifiers. Do not create a competing board, duplicate backlog, or\n   private status store merely because a preferred tool is unavailable.\n3. Separate facts, accepted decisions, assumptions, proposals, conflicts, and unknowns. Date every status\n   snapshot and mark inaccessible sources stale.\n4. Define the minimum status vocabulary and exit criteria. A status transition requires evidence; activity,\n   confidence, or a checked box alone is not proof of completion.\n\n## Build the delivery model\n\n1. Decompose the objective into outcome-oriented workstreams and milestones. Keep tasks small enough to\n   own and verify, while avoiding a second implementation backlog when one already exists.\n2. Record dependencies as a directed graph. Reject missing references and cycles before publishing a plan.\n3. Assign one accountable owner per active workstream. Record contributors separately when needed; shared\n   ownership is not a substitute for accountability.\n4. Maintain a RAID register:\n   - risks include likelihood, impact, mitigation, trigger, and owner;\n   - assumptions include validation date and consequence if false;\n   - issues include current impact, containment, and resolution owner;\n   - decisions include options, decision owner, due date, outcome, and rationale.\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:research",
        "eval:skill-evaluations",
        "overlay:consulting-delivery",
        "skill:audit-delivery-traceability",
        "skill:coordinate-parallel-agents",
        "skill:forecast-project-financials",
        "skill:plan-work",
        "tool:analyze-project-delivery"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "research"
      ]
    },
    {
      "key": "skill:migrate-code-with-evidence",
      "id": "migrate-code-with-evidence",
      "name": "Migrate Code With Evidence",
      "type": "skill",
      "path": "skills/migrate-code-with-evidence/SKILL.md",
      "description": "Migrate one bounded code slice from a read-only source into an isolated target using reconstructed behavior, accepted requirements, traceable scenarios, strict TDD, deterministic manifests, and independent verification. Use for approved code-language or platform migration with a runnable validation path. Do not use for bulk prompt translation, direct source-tree rewrites, embedded credentials, or migrations whose behavior and authority are unresolved.",
      "purpose": "Migrate one bounded code slice from a read-only source into an isolated target using reconstructed behavior, accepted requirements, traceable scenarios, strict TDD, deterministic manifests, and independent verification",
      "use_when": [
        "for approved code-language or platform migration with a runnable validation path"
      ],
      "not_when": [
        "for bulk prompt translation, direct source-tree rewrites, embedded credentials, or migrations whose behavior and authority are unresolved"
      ],
      "inputs": [],
      "workflow": [
        "Establish the migration boundary",
        "Migrate one slice",
        "Verify and hand off"
      ],
      "outputs": [],
      "validation": [],
      "tags": [
        "evidence-constrained-code-migration"
      ],
      "search_terms": [
        "evidence-constrained-code-migration",
        "Migrate Code With Evidence",
        "migrate-code-with-evidence"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: migrate-code-with-evidence\ndescription: Migrate one bounded code slice from a read-only source into an isolated target using reconstructed behavior, accepted requirements, traceable scenarios, strict TDD, deterministic manifests, and independent verification. Use for approved code-language or platform migration with a runnable validation path. Do not use for bulk prompt translation, direct source-tree rewrites, embedded credentials, or migrations whose behavior and authority are unresolved.\n---\n\n# Migrate code with evidence\n\nTreat model-generated code as an untrusted implementation proposal. The source remains read-only, target\nwrites stay isolated, credentials remain external, and network use is disabled by default unless explicitly\nauthorized and recorded.\n\n## Establish the migration boundary\n\n1. Inventory and fingerprint the bounded source with `inventory-codebase`.\n2. Reconstruct behavior, dependencies, data flow, error semantics, and unknowns with\n   `analyze-legacy-system`; do not translate from filenames or comments alone.\n3. Derive or reconcile accepted target requirements and scenarios with\n   `derive-modernization-requirements`. Preserve conflicts and behavior intentionally not migrated.\n4. Define target constraints, interfaces, security boundaries, dependency policy, coexistence, rollback,\n   and validation access. Stop when target authority is missing.\n5. Create a manifest using `assets/migration-manifest.example.json` and validate it with\n   `scripts/validate_migration_manifest.py`. The detailed contract is in\n   `references/migration-contract.md`.\n\n## Migrate one slice\n\nSelect one dependency-ready vertical slice. Record source artifacts, requirements, acceptance scenarios,\ntarget artifacts, tests, and exact validation commands. Practice `test-driven-development` as P0: prove a\nbehavior-relevant RED in the target, implement only enough for GREEN, refactor while green, then broaden to\ncontract, integration, migration, security, and performance checks required by the risk model.\n\nGenerated output must stay inside the declared target root. Never put credentials in prompts, manifests,\nlogs, fixtures, or source; never allow an agent to choose or execute destructive commands; never overwrite\nthe source tree; and never treat successful generation as behavioral parity.\n\n## Verify and hand off\n… preview truncated",
      "related_capabilities": [
        "archetype:legacy-migration",
        "eval:skill-evaluations",
        "skill:analyze-legacy-system",
        "skill:derive-modernization-requirements",
        "skill:mutation-testing",
        "skill:test-driven-development",
        "tool:validate-migration-manifest"
      ],
      "archetypes": [
        "legacy-migration"
      ]
    },
    {
      "key": "skill:mutation-testing",
      "id": "mutation-testing",
      "name": "Mutation Testing",
      "type": "skill",
      "path": "skills/mutation-testing/SKILL.md",
      "description": "Evaluate whether an existing test suite would actually detect defective implementation behavior by running targeted mutation analysis, classifying surviving mutants against approved specifications, and strengthening tests through a behavioral hardening loop. Use after implementation reaches a stable green and refactored state, when auditing an inherited or legacy-characterization suite, or as a changed-code quality gate. Do not use during the initial RED phase, as a substitute for test-driven development or coverage, to justify changing correct production behavior so a mutant dies, or to raise a score with implementation-coupled assertions.",
      "purpose": "Evaluate whether an existing test suite would actually detect defective implementation behavior by running targeted mutation analysis, classifying surviving mutants against approved specifications, and strengthening tests through a behavioral hardening loop",
      "use_when": [
        "after implementation reaches a stable green and refactored state, when auditing an inherited or legacy-characterization suite, or as a changed-code quality gate"
      ],
      "not_when": [
        "during the initial RED phase, as a substitute for test-driven development or coverage, to justify changing correct production behavior so a mutant dies, or to raise a score with implementation-coupled assertions"
      ],
      "inputs": [
        "stable green implementation",
        "passing baseline test command",
        "changed production scope",
        "linked requirement and specification IDs",
        "optional project mutation policy and accepted baseline"
      ],
      "workflow": [
        "Terminology",
        "Establish preconditions",
        "Select scope",
        "Select tooling",
        "Run, classify, and harden",
        "Apply the quality gate",
        "Report and trace",
        "Integration and direct use",
        "Completion"
      ],
      "outputs": [
        "normalized mutation run",
        "classified surviving mutants",
        "derived quality gate status",
        "test-hardening actions",
        "compact project-memory state"
      ],
      "validation": [],
      "tags": [
        "PIT",
        "Stryker",
        "changed-code-mutation-scope",
        "characterization-test-strength",
        "equivalent mutant",
        "killed mutant",
        "mutation score",
        "mutation testing",
        "mutation-baseline-comparison",
        "mutation-quality-gate",
        "mutation-test-quality",
        "mutmut",
        "pitest",
        "surviving mutants",
        "surviving-mutant-classification",
        "test adequacy",
        "test hardening",
        "test quality",
        "test robustness",
        "test strength",
        "test-strength-validation"
      ],
      "search_terms": [
        "changed-code-mutation-scope",
        "characterization-test-strength",
        "equivalent mutant",
        "killed mutant",
        "mutation score",
        "Mutation Testing",
        "mutation testing",
        "mutation-baseline-comparison",
        "mutation-quality-gate",
        "mutation-test-quality",
        "mutation-testing",
        "mutmut",
        "PIT",
        "pitest",
        "Stryker",
        "surviving mutants",
        "surviving-mutant-classification",
        "test adequacy",
        "test hardening",
        "test quality",
        "test robustness",
        "test strength",
        "test-strength-validation"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: mutation-testing\ndescription: Evaluate whether an existing test suite would actually detect defective implementation behavior by running targeted mutation analysis, classifying surviving mutants against approved specifications, and strengthening tests through a behavioral hardening loop. Use after implementation reaches a stable green and refactored state, when auditing an inherited or legacy-characterization suite, or as a changed-code quality gate. Do not use during the initial RED phase, as a substitute for test-driven development or coverage, to justify changing correct production behavior so a mutant dies, or to raise a score with implementation-coupled assertions.\n---\n\n# Assess and harden test quality with mutation testing\n\nPassing tests are not evidence of strong tests. A suite can be entirely green, and even fully covering, while\nstill failing to notice that the implementation is wrong. Mutation testing introduces controlled changes to\nproduction code and asks one question: **would the test suite notice?**\n\nKeep the three questions distinct and never substitute one for another:\n\n| Practice | Question it answers |\n| --- | --- |\n| Code coverage | Was this code executed by tests? |\n| Test-driven development | Did we specify the behavior through tests before implementing it? |\n| Mutation testing | Would those tests fail if the implementation were wrong? |\n\nFull coverage does not imply test quality, and a green suite does not imply defect detection. This workflow\nowns test-strength evaluation only. `test-driven-development` owns RED, GREEN, and REFACTOR and delegates\nhere once meaningful implementation exists. Do not run mutation analysis during the initial RED phase, and do\nnot reimplement the red-green-refactor loop inside this workflow.\n\n## Terminology\n\n- **Mutant** — one controlled modification to production code, such as `a > b` becoming `a >= b`,\n  `return true` becoming `return false`, or `+ 1` becoming `- 1`.\n- **Killed mutant** — at least one test fails after the mutation, so the suite detected the injected defect.\n- **Surviving mutant** — every test still passes despite the mutation, which indicates a possible\n  test-quality gap but is not yet proof of one.\n- **Equivalent mutant** — the mutation does not semantically change program behavior, so survival is not a\n  test defect and must not be reported as one.\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "eval:skill-evaluations",
        "skill:build-living-dashboard",
        "skill:design-test-strategy",
        "skill:implement-openspec-change",
        "skill:implement-ready-slice",
        "skill:migrate-code-with-evidence",
        "skill:test-driven-development",
        "skill:verify-openspec-implementation"
      ],
      "archetypes": [
        "development",
        "legacy-migration"
      ]
    },
    {
      "key": "skill:plan-work",
      "id": "plan-work",
      "name": "Plan Work",
      "type": "skill",
      "path": "skills/plan-work/SKILL.md",
      "description": "Turn an approved objective and current repository evidence into a bounded, dependency-aware, executable plan with goals, non-goals, assumptions, acceptance criteria, ownership, milestones, validation, risks, checkpoints, and recovery. Use before substantial implementation or when sequencing and handoff matter. Do not use for a trivial one-step edit, to invent unresolved product decisions, or to treat a plan as evidence that work is complete.",
      "purpose": "Turn an approved objective and current repository evidence into a bounded, dependency-aware, executable plan with goals, non-goals, assumptions, acceptance criteria, ownership, milestones, validation, risks, checkpoints, and recovery",
      "use_when": [
        "before substantial implementation or when sequencing and handoff matter"
      ],
      "not_when": [
        "for a trivial one-step edit, to invent unresolved product decisions, or to treat a plan as evidence that work is complete"
      ],
      "inputs": [],
      "workflow": [
        "Define the contract",
        "Decompose",
        "Validate the plan"
      ],
      "outputs": [],
      "validation": [],
      "tags": [
        "implementation-planning",
        "task-decomposition"
      ],
      "search_terms": [
        "implementation-planning",
        "Plan Work",
        "plan-work",
        "task-decomposition"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: plan-work\ndescription: Turn an approved objective and current repository evidence into a bounded, dependency-aware, executable plan with goals, non-goals, assumptions, acceptance criteria, ownership, milestones, validation, risks, checkpoints, and recovery. Use before substantial implementation or when sequencing and handoff matter. Do not use for a trivial one-step edit, to invent unresolved product decisions, or to treat a plan as evidence that work is complete.\n---\n\n# Plan executable work\n\nInspect current source, tests, decisions, governance, Git state, active ownership, dependencies, and prior\nvalidation before planning. Ask only for choices that cannot be discovered and would materially change scope.\n\n## Define the contract\n\nRecord the objective, users or consumers, observable acceptance, non-goals, protected paths, assumptions,\nunknowns, decisions needed, constraints, and source evidence. Mark unresolved authority as a blocker rather\nthan filling it with a recommendation.\n\n## Decompose\n\nCreate the smallest coherent milestones and tasks that produce valid intermediate states. For each task,\nrecord:\n\n- outcome and acceptance criterion;\n- evidence or decision that authorizes it;\n- dependencies and prerequisite state;\n- exclusive file, component, data, or environment ownership;\n- implementation boundary and explicit exclusions;\n- validation command or observable check;\n- risks, rollback or recovery, and handoff output.\n\nOrder tasks by dependencies and risk retirement. Separate discovery, decision, implementation, migration,\nverification, and external coordination. Parallelize only independent ownership with coordinator-controlled\nintegration.\n\n## Validate the plan\n\nWalk the plan forward from current state and backward from acceptance. Confirm every acceptance criterion has\nan implementation and verification path, every task has an owner and completion signal, and no milestone\nrequires unavailable authority. Include an early valid artifact and small recoverable batches for long work.\n\nReturn a concise plan, dependency map, assumptions and conflicts, validation matrix, recovery points, and one\nexact first action. Update the plan when evidence or scope changes; never report planned work as completed work.",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "eval:skill-evaluations",
        "overlay:architecture-documentation",
        "skill:deconstruct-problem-first-principles",
        "skill:design-frontend-architecture",
        "skill:manage-project-delivery",
        "skill:specify-openspec-change",
        "skill:validate-work-item-assumptions"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "skill:polish-html-artifact",
      "id": "polish-html-artifact",
      "name": "Polish HTML Artifact",
      "type": "skill",
      "path": "skills/polish-html-artifact/SKILL.md",
      "description": "Perform a bounded visual-finesse pass on a structurally and factually complete HTML dashboard, presentation, or technical narrative without changing its information architecture, narrative, claims, or interaction model. Use after generation and before independent validation when the artifact is correct but not yet visually finished. Do not use to invent content, redesign product structure, establish a client brand, or replace independent visual and accessibility review.",
      "purpose": "Perform a bounded visual-finesse pass on a structurally and factually complete HTML dashboard, presentation, or technical narrative without changing its information architecture, narrative, claims, or interaction model",
      "use_when": [
        "after generation and before independent validation when the artifact is correct but not yet visually finished"
      ],
      "not_when": [
        "to invent content, redesign product structure, establish a client brand, or replace independent visual and accessibility review"
      ],
      "inputs": [
        "complete HTML artifact",
        "accepted structure or narrative",
        "brand authority",
        "target viewports and states"
      ],
      "workflow": [
        "Bind the invariants",
        "Diagnose before styling",
        "Apply a bounded finesse pass",
        "Render, compare, correct",
        "Handoff"
      ],
      "outputs": [
        "refined tokens and components",
        "rendered before and after evidence",
        "preserved-invariant record",
        "independent validation handoff"
      ],
      "validation": [],
      "tags": [
        "art direction",
        "composition",
        "html-visual-finesse",
        "polish HTML",
        "premium dashboard",
        "premium presentation",
        "rendered-polish-loop",
        "spacing",
        "structure-preserving-art-direction",
        "typography",
        "visual finesse"
      ],
      "search_terms": [
        "art direction",
        "composition",
        "html-visual-finesse",
        "polish HTML",
        "Polish HTML Artifact",
        "polish-html-artifact",
        "premium dashboard",
        "premium presentation",
        "rendered-polish-loop",
        "spacing",
        "structure-preserving-art-direction",
        "typography",
        "visual finesse"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: polish-html-artifact\ndescription: Perform a bounded visual-finesse pass on a structurally and factually complete HTML dashboard, presentation, or technical narrative without changing its information architecture, narrative, claims, or interaction model. Use after generation and before independent validation when the artifact is correct but not yet visually finished. Do not use to invent content, redesign product structure, establish a client brand, or replace independent visual and accessibility review.\n---\n\n# Polish a complete HTML artifact\n\nImprove execution, not intent. The artifact's structure, content authority, brand, narrative, and interaction\ncontract must already be resolved.\n\n## Bind the invariants\n\nBefore editing, record the artifact, accepted content source, structural or narrative order, stable IDs,\nprimary interactions, brand authority, locales, target viewports, and current validation state. Capture a\nrepresentative rendered baseline. If these invariants cannot be established, return to the generating skill\ninstead of guessing.\n\nFor a canonical living dashboard, section order, navigation groups, data model, requirements/specifications/\ntraceability grammar, and shared detail opener are immutable unless the user explicitly authorizes a product\nchange. For a presentation, preserve the approved story, section order, claims, evidence, and call to action.\n\n## Diagnose before styling\n\nRead [references/finesse-checklist.md](references/finesse-checklist.md). Identify the smallest set of visual\ncauses behind the unfinished result, such as weak type contrast, uniform spacing, repetitive composition,\nexcessive surfaces, unintegrated diagrams, crude tables, noisy controls, or desktop-only layout. Separate\nbrand identity from canonical quality and do not import reference-specific palettes, fonts, logos, content,\nor exact compositions.\n\n## Apply a bounded finesse pass\n\nWork through reusable tokens and existing components before adding one-off rules:\n\n- refine display, body, metadata, data, code, and table typography plus readable line lengths;\n- make section, component, and inline spacing communicate different levels of grouping;\n- clarify primary, secondary, supporting, and control hierarchy within existing sections;\n- replace unnecessary cards with alignment, rules, whitespace, or a shared surface;\n… preview truncated",
      "related_capabilities": [
        "eval:skill-evaluations",
        "skill:accessibility-review",
        "skill:build-living-dashboard",
        "skill:create-branded-html-artifact",
        "skill:frontend-design",
        "skill:validate-visual-artifact"
      ],
      "archetypes": []
    },
    {
      "key": "skill:promote-to-commons",
      "id": "promote-to-commons",
      "name": "Promote To Commons",
      "type": "skill",
      "path": "skills/promote-to-commons/SKILL.md",
      "description": "Revalidate and implement explicitly selected reusable capability proposals in the canonical Agent Commons Library, including safe abstraction choice, confidentiality and license checks, evals, provenance, catalogs, adapters, documentation, validation, reporting, and a focused commit. Use when the user asks to promote named or clearly selected candidates from a commons review, completeness audit, external review, or explicit source path, or invokes the workflow without a candidate to inspect and choose from the latest project review. Do not use to discover candidates, promote an entire review implicitly, mutate source projects, copy unknown-license material, or bypass independent revalidation.",
      "purpose": "Revalidate and implement explicitly selected reusable capability proposals in the canonical Agent Commons Library, including safe abstraction choice, confidentiality and license checks, evals, provenance, catalogs, adapters, documentation, validation, reporting, and a focused commit",
      "use_when": [
        "when the user asks to promote named or clearly selected candidates from a commons review, completeness audit, external review, or explicit source path, or invokes the workflow without a candidate to inspect and choose from the latest project review"
      ],
      "not_when": [
        "to discover candidates, promote an entire review implicitly, mutate source projects, copy unknown-license material, or bypass independent revalidation"
      ],
      "inputs": [],
      "workflow": [
        "Resolve the source and selection",
        "Revalidate independently",
        "Protect boundaries before mutation",
        "Implement the smallest correct canonical change",
        "Synchronize canonical relationships",
        "Validate and commit",
        "Handle failure honestly"
      ],
      "outputs": [],
      "validation": [],
      "tags": [
        "candidate revalidation",
        "commons promotion",
        "controlled mutation",
        "controlled-commons-promotion",
        "promotion-revalidation"
      ],
      "search_terms": [
        "candidate revalidation",
        "commons promotion",
        "controlled mutation",
        "controlled-commons-promotion",
        "Promote To Commons",
        "promote-to-commons",
        "promotion-revalidation"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: promote-to-commons\ndescription: Revalidate and implement explicitly selected reusable capability proposals in the canonical Agent Commons Library, including safe abstraction choice, confidentiality and license checks, evals, provenance, catalogs, adapters, documentation, validation, reporting, and a focused commit. Use when the user asks to promote named or clearly selected candidates from a commons review, completeness audit, external review, or explicit source path, or invokes the workflow without a candidate to inspect and choose from the latest project review. Do not use to discover candidates, promote an entire review implicitly, mutate source projects, copy unknown-license material, or bypass independent revalidation.\n---\n\n# Promote approved capabilities to commons\n\nAct as the controlled mutation gate between a proposal and canonical Agent Commons. A review may recommend;\nonly an explicit user selection authorizes revalidation and possible mutation.\n\nRead `references/promotion-contract.md` before changing canonical files. Read\n`references/report-contract.md` before writing the promotion report.\n\n## Resolve the source and selection\n\n1. Resolve the source project and canonical commons root. Read both repositories' instructions and Git\n   state. Treat source projects as read-only; only the canonical commons checkout may be mutated.\n2. Locate the named proposal, audit, external review, or explicit source. When no candidate was supplied,\n   inspect the latest conventional project review and present its promotable candidates concisely.\n3. Resolve positive selections and exclusions from stable IDs, names, descriptions, priorities, or natural\n   language. Do not require numeric syntax.\n4. Do not mutate anything until the selected set is unambiguous. If no selection exists, present choices\n   and stop. If the user already selected clearly, do not ask again.\n5. Record the exact selected and excluded candidates. Approval applies only to that set; never infer that a\n   review authorizes every proposal.\n\n## Revalidate independently\n\nFor every selected candidate, inspect primary evidence rather than trusting the proposal's conclusion.\nEvaluate reuse, actual commons overlap, generalization, abstraction type, maturity, confidentiality,\nlicensing, routing collision risk, and validation feasibility. Search the relevant canonical skills,\n… preview truncated",
      "related_capabilities": [
        "eval:skill-evaluations",
        "skill:initialize-project",
        "skill:review-external-capability",
        "skill:review-for-commons",
        "skill:update-commons-presentation"
      ],
      "archetypes": []
    },
    {
      "key": "skill:protect-git-work",
      "id": "protect-git-work",
      "name": "Protect Git Work",
      "type": "skill",
      "path": "skills/protect-git-work/SKILL.md",
      "description": "Preserve and recover repository work through explicit dirty-state ownership, staged-diff review, secret checks, bounded checkpoints, safe integration conditions, abort rules, and exact handoff from a verified Git state. Use before or during substantial edits, rebases, merges, migrations, or multi-contributor work. Do not use to erase unknown changes, rewrite shared history without authorization, bypass repository policy, or treat an unverified commit as a safe checkpoint.",
      "purpose": "Preserve and recover repository work through explicit dirty-state ownership, staged-diff review, secret checks, bounded checkpoints, safe integration conditions, abort rules, and exact handoff from a verified Git state",
      "use_when": [
        "before or during substantial edits, rebases, merges, migrations, or multi-contributor work"
      ],
      "not_when": [
        "to erase unknown changes, rewrite shared history without authorization, bypass repository policy, or treat an unverified commit as a safe checkpoint"
      ],
      "inputs": [],
      "workflow": [
        "Establish state",
        "Work and checkpoint",
        "Integrate and recover"
      ],
      "outputs": [],
      "validation": [],
      "tags": [
        "checkpoint-recovery",
        "git-safety"
      ],
      "search_terms": [
        "checkpoint-recovery",
        "git-safety",
        "Protect Git Work",
        "protect-git-work"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: protect-git-work\ndescription: Preserve and recover repository work through explicit dirty-state ownership, staged-diff review, secret checks, bounded checkpoints, safe integration conditions, abort rules, and exact handoff from a verified Git state. Use before or during substantial edits, rebases, merges, migrations, or multi-contributor work. Do not use to erase unknown changes, rewrite shared history without authorization, bypass repository policy, or treat an unverified commit as a safe checkpoint.\n---\n\n# Protect Git work\n\nTreat every pre-existing change as owned until proven otherwise.\n\n## Establish state\n\n1. Resolve repository root, branch, HEAD, upstream, worktrees, status, staged and unstaged diffs, untracked\n   files, conflicts, active operations, and relevant recent commits.\n2. Classify changes as task-owned, user-owned, collaborator-owned, generated, ignored, or unknown. Do not\n   absorb unknown work into the task.\n3. Record protected paths, shared-history constraints, hooks, required gates, and the accepted recovery point.\n\n## Work and checkpoint\n\nUse narrow edits and review the exact diff before staging. Stage explicit paths or hunks, then inspect the\nstaged diff, unexpected binaries, generated changes, credentials, tokens, private keys, personal data, and\nlarge-file policy. Run the validation appropriate to the checkpoint.\n\nCreate bounded commits only when authorized. A checkpoint records purpose, paths, validation, known failures,\nand recovery command; it must not mix unrelated ownership. Tags, branches, stashes, patches, or worktrees may\nbe safer than a commit depending on policy and sharing.\n\n## Integrate and recover\n\nBefore merge, rebase, cherry-pick, or history editing, require a known base, clean ownership boundary, backup\nor recoverable reference, and explicit shared-history authorization. Abort on unexpected target drift,\nunowned conflicts, secret exposure, validation regression, unclear upstream, or an operation whose recovery\nhas not been proven.\n\nAfter integration, verify HEAD, status, diff, ancestry, and required tests. Hand off the exact commit or\nreference, remaining dirty paths and owners, validation evidence, blockers, and one recovery or continuation\naction. Never use destructive cleanup merely to make status look clean.",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "eval:skill-evaluations"
      ],
      "archetypes": [
        "development",
        "legacy-migration"
      ]
    },
    {
      "key": "skill:review-code-change",
      "id": "review-code-change",
      "name": "Review Code Change",
      "type": "skill",
      "path": "skills/review-code-change/SKILL.md",
      "description": "Review a complete code or pull-request change with full diff coverage, local-standard checks, validation evidence, severity-ranked findings, and a separate factual change summary. Use for pre-merge review, consequential patches, or re-review after corrections. Do not use to implement the change while claiming independence, post comments externally without explicit authorization, or review only filenames and generated summaries.",
      "purpose": "Review a complete code or pull-request change with full diff coverage, local-standard checks, validation evidence, severity-ranked findings, and a separate factual change summary",
      "use_when": [
        "for pre-merge review, consequential patches, or re-review after corrections"
      ],
      "not_when": [
        "to implement the change while claiming independence, post comments externally without explicit authorization, or review only filenames and generated summaries"
      ],
      "inputs": [],
      "workflow": [
        "Establish scope",
        "Inspect",
        "Report"
      ],
      "outputs": [],
      "validation": [],
      "tags": [
        "evidence-backed-code-review"
      ],
      "search_terms": [
        "evidence-backed-code-review",
        "Review Code Change",
        "review-code-change"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: review-code-change\ndescription: Review a complete code or pull-request change with full diff coverage, local-standard checks, validation evidence, severity-ranked findings, and a separate factual change summary. Use for pre-merge review, consequential patches, or re-review after corrections. Do not use to implement the change while claiming independence, post comments externally without explicit authorization, or review only filenames and generated summaries.\n---\n\n# Review a code change\n\nReview the actual change and its context. A summary explains what changed; findings explain what is wrong.\n\n## Establish scope\n\n1. Read repository instructions, review policy, relevant architecture and tests, existing review feedback,\n   and the complete base-to-head diff including renames, deletions, generated files, and untracked work.\n2. Identify intended behavior, acceptance evidence, affected callers, data or security boundaries, and\n   validation already run.\n3. Build a file checklist and account for every changed path. Treat generated output according to its\n   canonical source and drift rules.\n\n## Inspect\n\nTrace changed behavior through callers, callees, configuration, persistence, concurrency, error paths,\nauthorization, privacy, compatibility, and user-visible states. Verify tests assert the intended behavior,\nfail for meaningful reasons, cover boundaries, and do not hide regressions behind mocks or snapshots.\nUse local standards and exact source evidence; do not invent style requirements.\n\n## Report\n\nReturn:\n\n1. a concise factual change summary and validation summary;\n2. findings ordered by severity, each with a tight location, reproduction or concrete failure path, impact,\n   evidence, and bounded correction direction;\n3. unresolved questions, coverage limits, and an explicit no-findings statement when appropriate.\n\nPrioritize correctness, security, data loss, broken contracts, and user-visible regressions over cosmetic\npreference. Avoid praise, vague risk, duplicate findings, and issues outside the change unless the change\nmaterially exposes them.\n\nKeep review read-only. Drafting local findings is authorized by the review request; submitting comments,\napprovals, status changes, or messages to an external system requires explicit confirmation. Re-review the\ncorrected diff and relevant validation before closing findings.",
      "related_capabilities": [
        "archetype:development",
        "eval:skill-evaluations"
      ],
      "archetypes": [
        "development"
      ]
    },
    {
      "key": "skill:review-external-capability",
      "id": "review-external-capability",
      "name": "Review External Capability",
      "type": "skill",
      "path": "skills/review-external-capability/SKILL.md",
      "description": "Perform a detailed, revision-pinned review of one selected external skill, agent, command, plugin, MCP integration, hook, script, template, eval, or composite package; classify provenance, license, runtime coupling, security, semantic commons overlap, and targeted promotion candidates. Use after external discovery selects a promising item. Do not use to install or execute the package, review many candidates superficially, bypass licensing, copy unknown-license content, or promote directly into canonical commons.",
      "purpose": "Perform a detailed, revision-pinned review of one selected external skill, agent, command, plugin, MCP integration, hook, script, template, eval, or composite package; classify provenance, license, runtime coupling, security, semantic commons overlap, and targeted promotion candidates",
      "use_when": [
        "after external discovery selects a promising item"
      ],
      "not_when": [
        "to install or execute the package, review many candidates superficially, bypass licensing, copy unknown-license content, or promote directly into canonical commons"
      ],
      "inputs": [],
      "workflow": [
        "Establish the boundary",
        "Review provenance and license",
        "Classify capability and runtime coupling",
        "Compare semantically with commons",
        "Extract the smallest useful ideas",
        "Write and validate the review"
      ],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Review External Capability",
        "review-external-capability"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: review-external-capability\ndescription: Perform a detailed, revision-pinned review of one selected external skill, agent, command, plugin, MCP integration, hook, script, template, eval, or composite package; classify provenance, license, runtime coupling, security, semantic commons overlap, and targeted promotion candidates. Use after external discovery selects a promising item. Do not use to install or execute the package, review many candidates superficially, bypass licensing, copy unknown-license content, or promote directly into canonical commons.\n---\n\n# Review an external capability\n\nReview one bounded capability deeply enough to support a promotion decision.\n\n## Establish the boundary\n\n1. Resolve the source URL, repository or registry, exact path, author or organization, and immutable\n   revision. If a revision cannot be pinned, record the limitation and do not make reproducibility claims.\n2. Resolve source trust from `external/sources.yaml`. A repository absent from the registry starts as\n   `UNTRUSTED`, even when its name looks official.\n3. Inspect source content read-only. Never execute scripts, hooks, installers, MCP servers, package setup,\n   generated binaries, or commands merely to understand them.\n4. If working in the canonical commons checkout for an intentional library review, write under\n   `external/reviews/` and update the external index deliberately. Otherwise write a project-local report\n   and leave commons unchanged.\n\n## Review provenance and license\n\nCapture source, repository, path, organization, revision, trust, detected license, license path and scope,\napparent redistribution and modification permissions, attribution or notice requirements, and uncertainty.\n\nUse `LICENSE UNKNOWN` when the source does not establish the applicable license. Unknown licensing\nprohibits copying or adapting source text and code. Methodology may still be independently reimplemented\nwhen appropriate, with careful provenance and no claim of legal certainty.\n\n## Classify capability and runtime coupling\n\nChoose the most accurate type: skill/workflow, agent, command, plugin, tool, MCP, hook, script, template,\neval, or composite package. Separate reusable methodology from Claude-, Codex-, Cline-, OpenCode-, or\nother runtime-specific syntax, paths, tools, permissions, and orchestration.\n\nClassify the security surface as one of:\n\n- `INSTRUCTIONS ONLY`\n… preview truncated",
      "related_capabilities": [
        "eval:external-evaluations",
        "eval:skill-evaluations",
        "external:ext-github-community-discovery-footprintai-open-sdlc-skills",
        "external:ext-github-community-discovery-m-binimran-finance-pack",
        "skill:promote-to-commons"
      ],
      "archetypes": []
    },
    {
      "key": "skill:review-for-commons",
      "id": "review-for-commons",
      "name": "Review For Commons",
      "type": "skill",
      "path": "skills/review-for-commons/SKILL.md",
      "description": "Inspect an active project and semantically compare its proven agent workflows, skills, roles, scripts, templates, evaluations, runtime adapters, and recurring practices with the canonical Agent Commons Library, then write a sanitized project-local proposal for new, updated, replaced, duplicate, local, or rejected capabilities. Use at a meaningful project milestone, before archival, or when deciding what this project should contribute back to commons. Do not use to promote or install capabilities, mutate the commons library, delete project-local assets, or turn speculative and one-off behavior into global guidance.",
      "purpose": "Inspect an active project and semantically compare its proven agent workflows, skills, roles, scripts, templates, evaluations, runtime adapters, and recurring practices with the canonical Agent Commons Library, then write a sanitized project-local proposal for new, updated, replaced, duplicate, local, or rejected capabilities",
      "use_when": [
        "at a meaningful project milestone, before archival, or when deciding what this project should contribute back to commons"
      ],
      "not_when": [
        "to promote or install capabilities, mutate the commons library, delete project-local assets, or turn speculative and one-off behavior into global guidance"
      ],
      "inputs": [],
      "workflow": [
        "Establish scope and boundaries",
        "Discover project learning",
        "Build evidence-backed candidates",
        "Compare semantically with commons",
        "Apply the promotion tests",
        "Scrub confidential detail",
        "Write the review",
        "Final checks"
      ],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Review For Commons",
        "review-for-commons"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: review-for-commons\ndescription: Inspect an active project and semantically compare its proven agent workflows, skills, roles, scripts, templates, evaluations, runtime adapters, and recurring practices with the canonical Agent Commons Library, then write a sanitized project-local proposal for new, updated, replaced, duplicate, local, or rejected capabilities. Use at a meaningful project milestone, before archival, or when deciding what this project should contribute back to commons. Do not use to promote or install capabilities, mutate the commons library, delete project-local assets, or turn speculative and one-off behavior into global guidance.\n---\n\n# Review a project for commons\n\nProduce an evidence-backed changeset proposal. Never promote automatically.\n\nThis workflow is the internal learning path. It reviews proven behavior from the current project. Do not\nquietly broaden it into open-source research: use `search-external-capabilities` and\n`review-external-capability` for external ecosystem learning. Internal and external proposals remain\ndistinct evidence streams but pass through the same abstraction, confidentiality, licensing where\napplicable, evaluation, provenance, and explicit promotion gate.\n\n## Establish scope and boundaries\n\n1. Resolve the current project root from Git; if the directory is not in a worktree, use the invocation\n   directory. Do not treat the commons checkout itself as the source project.\n2. Locate the canonical Agent Commons Library from project configuration or the standard\n   `~/agent-commons-library` checkout. Read its governance before comparing anything.\n3. Read project instructions and repository state before inspecting candidates. Preserve unrelated work.\n4. Default report paths to `docs/commons-review.md` and `docs/commons-review.json` inside the current\n   project. Follow an established equivalent project convention when one exists.\n5. Treat the project as read-only except for the two review reports. Treat commons as fully read-only.\n6. Exclude secrets, credentials, environment files, dependencies, generated output, caches, binaries,\n   vendor content, Git object storage, and private source excerpts.\n\nIf the project root, commons root, or safe report destination cannot be resolved, stop and report the\nspecific uncertainty. Do not guess across unrelated repositories.\n\n## Discover project learning\n… preview truncated",
      "related_capabilities": [
        "eval:skill-evaluations",
        "skill:promote-to-commons"
      ],
      "archetypes": []
    },
    {
      "key": "skill:review-openspec-change",
      "id": "review-openspec-change",
      "name": "Review OpenSpec Change",
      "type": "skill",
      "path": "skills/review-openspec-change/SKILL.md",
      "description": "Review and refine an existing OpenSpec change for implementation readiness, resolving scope, ambiguity, acceptance, delta correctness, design, tasks, and validation before code changes. Use after a change exists and before implementation approval. Do not use to create duplicate changes, implement code, certify completed implementation, or approve unresolved product decisions by assumption.",
      "purpose": "Review and refine an existing OpenSpec change for implementation readiness, resolving scope, ambiguity, acceptance, delta correctness, design, tasks, and validation before code changes",
      "use_when": [
        "after a change exists and before implementation approval"
      ],
      "not_when": [
        "to create duplicate changes, implement code, certify completed implementation, or approve unresolved product decisions by assumption"
      ],
      "inputs": [
        "existing OpenSpec change",
        "main specifications",
        "project constraints and decisions"
      ],
      "workflow": [
        "Establish current state",
        "Review the specification contract",
        "Refine without crossing the gate",
        "Return a readiness decision"
      ],
      "outputs": [
        "readiness decision",
        "refined coherent artifacts",
        "requirement scenario task and test coverage"
      ],
      "validation": [],
      "tags": [
        "OpenSpec",
        "acceptance criteria",
        "change proposal",
        "openspec-readiness-review",
        "readiness",
        "spec-driven",
        "spec-first",
        "specification",
        "specification-ambiguity-resolution"
      ],
      "search_terms": [
        "acceptance criteria",
        "change proposal",
        "OpenSpec",
        "openspec-readiness-review",
        "readiness",
        "Review OpenSpec Change",
        "review-openspec-change",
        "spec-driven",
        "spec-first",
        "specification",
        "specification-ambiguity-resolution"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: review-openspec-change\ndescription: Review and refine an existing OpenSpec change for implementation readiness, resolving scope, ambiguity, acceptance, delta correctness, design, tasks, and validation before code changes. Use after a change exists and before implementation approval. Do not use to create duplicate changes, implement code, certify completed implementation, or approve unresolved product decisions by assumption.\n---\n\n# Review an OpenSpec change for readiness\n\nTreat this as the pre-implementation gate. Read the existing change rather than drafting a replacement.\n\n## Establish current state\n\nUse a bounded context package for the selected change, linked requirements, architecture decisions, affected\ncomponents, and prior findings. Canonical OpenSpec files and requirements remain authoritative.\n\n1. Resolve the exact change. When several changes are active, do not guess; use conversation context or ask\n   for selection.\n2. Read project governance, `openspec/config.yaml`, relevant main specs, the change metadata, all existing\n   artifacts, related source boundaries, and any prior review decisions.\n3. Run `openspec status --change \u003cname> --json`, `openspec show \u003cname> --json`, and\n   `openspec validate \u003cname> --strict --no-interactive` when supported by the installed version.\n4. Confirm the change is the one already approved or under review. Reuse it instead of starting another.\n\n## Review the specification contract\n\nCheck and distinguish:\n\n- intent, scope, non-goals, users, and affected behavior;\n- ADDED, MODIFIED, and REMOVED deltas against the current main specs;\n- observable requirements and concrete scenarios, including material negative and boundary cases;\n- behavior requirements versus technical design choices;\n- design consistency with the proposal and known repository constraints;\n- tasks that cover every scenario, relevant tests, migration, documentation, and rollout or recovery;\n- explicit `skip_specs: true` only when no behavior change is intended and no delta spec exists;\n- unresolved decisions, conflicts, dependencies, and assumptions that would cause implementation drift.\n\nFor a bug fix, require a precise corrected-behavior scenario suitable for a regression test. For a pure\nrefactor, require preservation checks instead of invented functional requirements. Scale the review to risk:\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "eval:skill-evaluations",
        "skill:implement-openspec-change",
        "skill:specify-openspec-change",
        "skill:validate-work-item-assumptions"
      ],
      "archetypes": [
        "development",
        "legacy-migration"
      ]
    },
    {
      "key": "skill:review-privacy-security",
      "id": "review-privacy-security",
      "name": "Review Privacy Security",
      "type": "skill",
      "path": "skills/review-privacy-security/SKILL.md",
      "description": "Review a system, design, change, or workflow for privacy and security using evidence-backed data-flow mapping, trust boundaries, abuse paths, minimization, secrets, logging, retention, isolation, negative tests, and claim limits. Use before consequential delivery or when sensitive data and privileged operations are in scope. Do not use as a compliance certification, a substitute for authorized penetration testing, or an implementation task presented as independent review.",
      "purpose": "Review a system, design, change, or workflow for privacy and security using evidence-backed data-flow mapping, trust boundaries, abuse paths, minimization, secrets, logging, retention, isolation, negative tests, and claim limits",
      "use_when": [
        "before consequential delivery or when sensitive data and privileged operations are in scope"
      ],
      "not_when": [
        "as a compliance certification, a substitute for authorized penetration testing, or an implementation task presented as independent review"
      ],
      "inputs": [],
      "workflow": [
        "Model the system",
        "Challenge the design and implementation",
        "Report"
      ],
      "outputs": [],
      "validation": [],
      "tags": [
        "privacy-security-review"
      ],
      "search_terms": [
        "privacy-security-review",
        "Review Privacy Security",
        "review-privacy-security"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: review-privacy-security\ndescription: Review a system, design, change, or workflow for privacy and security using evidence-backed data-flow mapping, trust boundaries, abuse paths, minimization, secrets, logging, retention, isolation, negative tests, and claim limits. Use before consequential delivery or when sensitive data and privileged operations are in scope. Do not use as a compliance certification, a substitute for authorized penetration testing, or an implementation task presented as independent review.\n---\n\n# Review privacy and security\n\nEstablish scope, assets, actors, data classes, environments, applicable policies, deployment assumptions,\nand evidence access. State what is outside the review.\n\n## Model the system\n\n1. Trace collection, ingress, parsing, validation, transformation, storage, caching, logging, analytics,\n   sharing, export, retention, deletion, and recovery of sensitive data.\n2. Mark trust boundaries, identities, authorization decisions, tenant or workload isolation, secrets,\n   network calls, parsers, file handling, administrative paths, and third-party dependencies.\n3. Separate verified controls, inferred controls, proposed controls, conflicts, and unknowns.\n\n## Challenge the design and implementation\n\nAssess data minimization, purpose limitation, defaults, consent or authority, access control, secret\nhandling, redaction, encryption assumptions, retention, deletion, auditability, isolation, injection,\nrequest forgery, traversal, unsafe deserialization, dependency risk, denial of service, replay, race,\nidempotency, failure handling, and recovery. Adapt the threat set to the actual surface.\n\nUse negative tests and concrete abuse paths. Verify that logs, errors, telemetry, fixtures, backups, and\ngenerated artifacts do not quietly reintroduce protected data or credentials.\n\n## Report\n\nReturn a scoped system and data-flow summary, assumptions, evidence, severity-ranked findings, affected\nassets and actors, reproduction or attack path, existing controls, recommended control class, validation\nneeded, residual risk, and review limitations. Do not claim a control exists without evidence or convert an\nunreachable environment into a pass.\n\nFor consequential work, delegate this workflow to the independent `privacy-security-reviewer`. The reviewer\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "eval:skill-evaluations",
        "skill:anonymize-data",
        "skill:create-data-flow-diagram",
        "skill:generate-synthetic-fixtures"
      ],
      "archetypes": [
        "development"
      ]
    },
    {
      "key": "skill:sales-storytelling",
      "id": "sales-storytelling",
      "name": "Sales Storytelling",
      "type": "skill",
      "path": "skills/sales-storytelling/SKILL.md",
      "description": "Transform evidence and source material into a credible audience-specific sales presentation narrative and call to action. Do not use to fabricate proof, force a generic sales-deck formula, or replace visual artifact construction and QA.",
      "purpose": "Transform evidence and source material into a credible audience-specific sales presentation narrative and call to action. Do not use to fabricate proof, force a generic sales-deck formula, or replace visual artifact construction and QA.",
      "use_when": [],
      "not_when": [
        "to fabricate proof, force a generic sales-deck formula, or replace visual artifact construction and QA"
      ],
      "inputs": [],
      "workflow": [
        "Establish the decision",
        "Build the argument",
        "Protect credibility",
        "Produce the narrative handoff",
        "Validation"
      ],
      "outputs": [],
      "validation": [],
      "tags": [
        "German narrative",
        "client terminology",
        "evidence-backed-sales-narrative",
        "native-client-language-sales-narrative",
        "public sector",
        "public-sector-sales-tone",
        "restrained tone",
        "sales presentation",
        "sales-presentation-methodology"
      ],
      "search_terms": [
        "client terminology",
        "evidence-backed-sales-narrative",
        "German narrative",
        "native-client-language-sales-narrative",
        "public sector",
        "public-sector-sales-tone",
        "restrained tone",
        "sales presentation",
        "Sales Storytelling",
        "sales-presentation-methodology",
        "sales-storytelling"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: sales-storytelling\ndescription: Transform evidence and source material into a credible audience-specific sales presentation narrative and call to action. Do not use to fabricate proof, force a generic sales-deck formula, or replace visual artifact construction and QA.\n---\n\n# Sales storytelling\n\nShape a persuasive argument from verified evidence. This workflow defines presentation methodology; it\ndoes not create a separate sales-project universe and does not substitute for branded artifact creation.\n\n## Establish the decision\n\nFor substantial projects, retrieve a presentation context package containing L0 plus current-state,\ncomplexity, risk, requirement, estimate, roadmap, and target-architecture summaries with canonical pointers.\nDo not load the complete source repository or research history into the narrative context.\n\nDetermine from the brief and available evidence:\n\n- audience and buying roles;\n- desired outcome or next action;\n- what is being proposed or sold;\n- the customer's situation, constraints, and likely problem;\n- known differentiators, objections, and proof.\n\nAsk only for missing decisions that research or supplied source material cannot reasonably establish.\nInspect `.agent-commons.yaml` or equivalent persisted project context before asking for delivery language.\nWhen the client is public sector with `CONFIRMED` or `HIGH_CONFIDENCE` classification and a resolved German\nlocale, use that locale for the sales narrative unless an explicit presentation instruction overrides it.\n\n## Build the argument\n\nDevelop the narrative from the actual audience, decision, and evidence. Consider:\n\n1. the customer's current situation;\n2. the cost, risk, or missed opportunity in the current state;\n3. the insight revealed by research or project evidence;\n4. the proposed approach and why it fits;\n5. differentiation that matters to this audience;\n6. credible proof such as data, architecture, process, experience, or examples;\n7. likely objections and honest responses;\n8. the concrete call to action.\n\nThese are reasoning prompts, not a mandatory slide order. Do not force every argument into problem,\nsolution, features, benefits, and call to action.\n\nFor a public-sector client, construct the narrative natively in professional Standard German from the\nresearch and evidence handoff. Do not first complete an English sales deck and mechanically translate it.\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "eval:skill-evaluations",
        "overlay:sales-storytelling"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "skill:search-external-capabilities",
      "id": "search-external-capabilities",
      "name": "Search External Capabilities",
      "type": "skill",
      "path": "skills/search-external-capabilities/SKILL.md",
      "description": "Search configured official, curated, and community sources for reusable open-source agent-engineering capabilities relevant to a topic or project, then return ranked revision-aware candidates without installing or promoting them. Use before designing substantial agent workflows when external precedent may reduce blind spots. Do not use to install packages, trust discovery results, copy third-party content, crawl arbitrary websites, or modify canonical commons automatically.",
      "purpose": "Search configured official, curated, and community sources for reusable open-source agent-engineering capabilities relevant to a topic or project, then return ranked revision-aware candidates without installing or promoting them",
      "use_when": [
        "before designing substantial agent workflows when external precedent may reduce blind spots"
      ],
      "not_when": [
        "to install packages, trust discovery results, copy third-party content, crawl arbitrary websites, or modify canonical commons automatically"
      ],
      "inputs": [],
      "workflow": [
        "Establish a safe query",
        "Search in trust order",
        "Rank and classify",
        "Return results"
      ],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Search External Capabilities",
        "search-external-capabilities"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: search-external-capabilities\ndescription: Search configured official, curated, and community sources for reusable open-source agent-engineering capabilities relevant to a topic or project, then return ranked revision-aware candidates without installing or promoting them. Use before designing substantial agent workflows when external precedent may reduce blind spots. Do not use to install packages, trust discovery results, copy third-party content, crawl arbitrary websites, or modify canonical commons automatically.\n---\n\n# Search external capabilities\n\nDiscover candidates, not dependencies.\n\n## Establish a safe query\n\n1. Read `external/sources.yaml` and `external/README.md` from the canonical Agent Commons checkout.\n2. Accept a specific topic or derive a small query set from the current project's explicitly identified\n   capability gaps. Prefer source semantics, target architecture, bridge mapping, business-rule extraction,\n   dependency analysis, or migration validation over a vague technology-pair query.\n3. For project-aware search, use only generic technologies, project archetypes, selected canonical\n   capability IDs, and reusable engineering concerns. Never send client names, repository names, internal\n   paths, goals, source text, business rules, credentials, or proprietary identifiers to an external search.\n4. Normalize and deduplicate overlapping concepts, discard queries made only from generic terms such as\n   `migration`, `testing`, or `Java`, and combine compatible concepts into the smallest useful repository\n   search. Generate no more than eight focused concepts. Use\n   `tools/external_capabilities.py project-query --root \u003cproject>` when the project has enough local\n   structure for deterministic allowlisted signals.\n\n## Search in trust order\n\n1. Search enabled official repositories first.\n2. Search enabled curated repositories or organizations second.\n3. Use broader GitHub discovery only when `discovery.github_search` is enabled.\n4. Use general web discovery only when the registry enables it or the user explicitly requests a one-off\n   search. Limit it to finding repositories, marketplaces, registries, or authoritative documentation.\n   Treat every newly found domain and repository as `UNTRUSTED` until reviewed.\n\nFor supported GitHub sources, prefer the deterministic CLI. Pass focused concepts as repeated topics so\n… preview truncated",
      "related_capabilities": [
        "eval:external-evaluations",
        "eval:skill-evaluations",
        "external:anthropic-official-plugins",
        "external:cline-official",
        "external:general-web-discovery",
        "external:github-community-discovery",
        "external:mcp-official-servers",
        "external:openai-official-codex",
        "external:openai-official-skills",
        "external:opencode-official"
      ],
      "archetypes": []
    },
    {
      "key": "skill:specify-openspec-change",
      "id": "specify-openspec-change",
      "name": "Specify OpenSpec Change",
      "type": "skill",
      "path": "skills/specify-openspec-change/SKILL.md",
      "description": "Create or refine one OpenSpec change so intended behavior, scope, acceptance scenarios, design, and implementation tasks are agreed before code changes. Use for features, behavioral bug fixes, consequential technical changes, and explicitly OpenSpec-managed work. Do not use for implementation, post-hoc specification of finished code, research or presentation work, or a trivial edit that does not justify durable change state.",
      "purpose": "Create or refine one OpenSpec change so intended behavior, scope, acceptance scenarios, design, and implementation tasks are agreed before code changes",
      "use_when": [
        "for features, behavioral bug fixes, consequential technical changes, and explicitly OpenSpec-managed work"
      ],
      "not_when": [
        "for implementation, post-hoc specification of finished code, research or presentation work, or a trivial edit that does not justify durable change state"
      ],
      "inputs": [
        "requested software change",
        "project OpenSpec state",
        "current behavior and constraints"
      ],
      "workflow": [
        "Resolve the change boundary",
        "Build coherent artifacts",
        "Parallel specification ownership",
        "Establish lightweight traceability",
        "Validate and hand off"
      ],
      "outputs": [
        "OpenSpec proposal and delta specs",
        "design and implementation tasks",
        "validated pre-implementation handoff"
      ],
      "validation": [],
      "tags": [
        "OpenSpec",
        "acceptance criteria",
        "acceptance-scenario-definition",
        "change proposal",
        "delta spec",
        "openspec-change-specification",
        "spec-driven",
        "spec-first",
        "specification",
        "specification-first-development"
      ],
      "search_terms": [
        "acceptance criteria",
        "acceptance-scenario-definition",
        "change proposal",
        "delta spec",
        "OpenSpec",
        "openspec-change-specification",
        "spec-driven",
        "spec-first",
        "specification",
        "specification-first-development",
        "Specify OpenSpec Change",
        "specify-openspec-change"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: specify-openspec-change\ndescription: Create or refine one OpenSpec change so intended behavior, scope, acceptance scenarios, design, and implementation tasks are agreed before code changes. Use for features, behavioral bug fixes, consequential technical changes, and explicitly OpenSpec-managed work. Do not use for implementation, post-hoc specification of finished code, research or presentation work, or a trivial edit that does not justify durable change state.\n---\n\n# Specify an OpenSpec change\n\nOpenSpec defines intended software behavior before implementation. Keep canonical Commons guidance here\nand all proposals, specs, designs, tasks, configuration, and archive state inside the active project.\n\n## Resolve the change boundary\n\nLoad only the selected requirement revisions, linked evidence, architecture decisions, affected components,\ndependencies, unknowns, and existing specification state through a bounded project-memory context package.\nVerify those pointers against canonical requirements and OpenSpec before authoring.\n\n1. Read project governance, Git state, current `openspec/config.yaml`, main specs, active changes, and the\n   requested outcome. Use `openspec list --json` and `openspec status --change \u003cname> --json` when available.\n2. Reuse an active change when its intent and scope match. Do not create a second proposal for the same work.\n3. If intent is unclear, explore and clarify before creating artifacts. Do not convert guesses into approved\n   requirements.\n4. If OpenSpec is not initialized, report that boundary and use the official project initialization flow\n   before authoring project-local OpenSpec state.\n5. Choose the lightest valid treatment:\n   - feature or behavior change: proposal plus delta specs with observable scenarios, then design and tasks;\n   - bug fix: describe the correct behavior and add or modify a regression scenario;\n   - pure refactor, tooling, or documentation change with no intended behavior change: state that invariant,\n     use `skip_specs: true`, and do not invent functional requirements;\n   - tiny low-risk edit: bypass durable OpenSpec ceremony unless governance or the user explicitly requires it.\n\nWhen approved requirements already exist, read\n`references/requirements-to-openspec.md` and treat them as the behavioral source for the change. Do not merely\nrename each requirement into a spec.\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "eval:skill-evaluations",
        "skill:build-living-dashboard",
        "skill:complete-openspec-change",
        "skill:continue-project",
        "skill:derive-modernization-requirements",
        "skill:implement-openspec-change",
        "skill:plan-work",
        "skill:review-openspec-change",
        "skill:test-driven-development"
      ],
      "archetypes": [
        "development",
        "legacy-migration"
      ]
    },
    {
      "key": "skill:test-driven-development",
      "id": "test-driven-development",
      "name": "Test Driven Development",
      "type": "skill",
      "path": "skills/test-driven-development/SKILL.md",
      "description": "Drive an approved behavior change through a strict, evidence-recorded red-green-refactor loop at the narrowest credible test level. Use for ordinary features, regressions, services, components, migrations, and unqueued bounded changes with a runnable test path. Do not use for documentation-only edits, exploratory spikes with no asserted behavior, blocked decisions, or work whose environment cannot demonstrate a behavior-relevant RED state, and do not run the mutation quality check before meaningful implementation exists.",
      "purpose": "Drive an approved behavior change through a strict, evidence-recorded red-green-refactor loop at the narrowest credible test level",
      "use_when": [
        "for ordinary features, regressions, services, components, migrations, and unqueued bounded changes with a runnable test path"
      ],
      "not_when": [
        "for documentation-only edits, exploratory spikes with no asserted behavior, blocked decisions, or work whose environment cannot demonstrate a behavior-relevant RED state, and do not run the mutation quality check before meaningful implementation exists"
      ],
      "inputs": [],
      "workflow": [
        "Establish the behavior",
        "RED",
        "GREEN",
        "REFACTOR and broaden",
        "Mutation quality check",
        "Recovery and delegation",
        "Completion"
      ],
      "outputs": [],
      "validation": [],
      "tags": [
        "behavior-first-implementation",
        "test-driven-development"
      ],
      "search_terms": [
        "behavior-first-implementation",
        "Test Driven Development",
        "test-driven-development"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: test-driven-development\ndescription: Drive an approved behavior change through a strict, evidence-recorded red-green-refactor loop at the narrowest credible test level. Use for ordinary features, regressions, services, components, migrations, and unqueued bounded changes with a runnable test path. Do not use for documentation-only edits, exploratory spikes with no asserted behavior, blocked decisions, or work whose environment cannot demonstrate a behavior-relevant RED state, and do not run the mutation quality check before meaningful implementation exists.\n---\n\n# Practice test-driven development\n\nTreat RED, GREEN, and REFACTOR as observable states, not labels added after implementation.\n\nThe full default cycle is RED, GREEN, REFACTOR, test-suite pass, mutation quality check, test hardening if\nrequired, then validation against the specification. TDD asks whether the behavior was specified through\ntests. Mutation testing asks whether those tests would fail if the implementation were wrong. Both questions\nmatter, and a green suite answers only the first.\n\n## Establish the behavior\n\n1. Read local governance, approved requirements or OpenSpec change, acceptance criteria, existing tests,\n   implementation, and validation commands.\n2. When OpenSpec governs the change, select one approved acceptance criterion or scenario as the primary\n   behavioral input and retain its specification ID and requirement trace. OpenSpec states **what** behavior\n   must exist; TDD is **how** that behavior is implemented and proved incrementally.\n3. State one smallest observable behavior, its boundary, and the evidence that authorizes it.\n4. Select the narrowest test level that can fail for the intended reason. Use `design-test-strategy` first\n   when the risk or correct level is unclear.\n5. Protect unrelated work and establish an exact rollback or checkpoint before editing.\n\nFor a substantial project, load only the selected scenario, linked requirement/specification revisions,\naffected component memory, architecture decisions, and necessary files. Project memory is routing context,\nnot a substitute for the executable test or source under change.\n\nWhen multiple TDD loops run concurrently, each worker must use an isolated writable checkout or task\ndirectory at a verified base revision and own all production and test paths it may change. Reserve distinct\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "eval:skill-evaluations",
        "skill:design-test-strategy",
        "skill:generate-synthetic-fixtures",
        "skill:implement-openspec-change",
        "skill:implement-ready-slice",
        "skill:migrate-code-with-evidence",
        "skill:mutation-testing",
        "skill:specify-openspec-change",
        "skill:verify-openspec-implementation"
      ],
      "archetypes": [
        "development",
        "legacy-migration"
      ]
    },
    {
      "key": "skill:update-commons-presentation",
      "id": "update-commons-presentation",
      "name": "Update Commons Presentation",
      "type": "skill",
      "path": "skills/update-commons-presentation/SKILL.md",
      "description": "Bring the standalone Agent Commons sales and technical presentation up to date after meaningful canonical-library changes by refreshing generated facts first, classifying narrative impact, making only warranted authored-content changes, preserving the locked visual system, and running technical and visual QA. Use after releases, promotions, new capabilities, architecture or governance changes, or when asked to refresh or update the Agent Commons presentation. Do not use for factual synchronization alone when the deterministic refresh tool is sufficient, to redesign the presentation, or to change claims without canonical evidence.",
      "purpose": "Bring the standalone Agent Commons sales and technical presentation up to date after meaningful canonical-library changes by refreshing generated facts first, classifying narrative impact, making only warranted authored-content changes, preserving the locked visual system, and running technical and visual QA",
      "use_when": [
        "after releases, promotions, new capabilities, architecture or governance changes, or when asked to refresh or update the Agent Commons presentation"
      ],
      "not_when": [
        "for factual synchronization alone when the deterministic refresh tool is sufficient, to redesign the presentation, or to change claims without canonical evidence"
      ],
      "inputs": [],
      "workflow": [
        "Refresh facts first",
        "Classify narrative impact",
        "Update authored content deliberately",
        "Validate the result",
        "Finish with an auditable result"
      ],
      "outputs": [],
      "validation": [],
      "tags": [
        "presentation refresh",
        "presentation update",
        "presentation-impact-classification",
        "presentation-narrative-maintenance",
        "sales narrative",
        "visual QA"
      ],
      "search_terms": [
        "presentation refresh",
        "presentation update",
        "presentation-impact-classification",
        "presentation-narrative-maintenance",
        "sales narrative",
        "Update Commons Presentation",
        "update-commons-presentation",
        "visual QA"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: update-commons-presentation\ndescription: Bring the standalone Agent Commons sales and technical presentation up to date after meaningful canonical-library changes by refreshing generated facts first, classifying narrative impact, making only warranted authored-content changes, preserving the locked visual system, and running technical and visual QA. Use after releases, promotions, new capabilities, architecture or governance changes, or when asked to refresh or update the Agent Commons presentation. Do not use for factual synchronization alone when the deterministic refresh tool is sufficient, to redesign the presentation, or to change claims without canonical evidence.\n---\n\n# Update the commons presentation\n\nKeep repository facts automatic and storytelling deliberate.\n\n## Refresh facts first\n\n1. Inspect repository instructions, Git status, the current presentation, its README, and recent meaningful\n   presentation history. Preserve unrelated work and never absorb unknown edits into a commit.\n2. Run `python3 tools/check_presentation_visual_contract.py` before editing. Stop if the visual system has\n   already drifted; presentation maintenance must not establish a new visual baseline.\n3. Run `python3 tools/refresh_commons_presentation.py` before evaluating narrative changes.\n4. Run `python3 tools/refresh_commons_presentation.py --check`. Stop if generated data remains stale or\n   invalid. Fix canonical metadata or the generator rather than hand-editing generated data.\n5. Inspect the generated change report, Git diff, changelog, version, new or removed capabilities,\n   archetype and overlay composition, runtime changes, promotion workflow, and governance changes.\n\n## Classify narrative impact\n\nAssign exactly one classification and record the evidence:\n\n- `FACTUAL ONLY`: counts, names, small utilities, evals, removals, or renames already represented by the\n  generated navigator, search, previews, and network. Leave authored narrative unchanged.\n- `MINOR NARRATIVE IMPACT`: a notable capability such as TDD, localization, or one specialist agent changes\n  an existing proof point. Update only the smallest relevant existing section.\n- `MAJOR NARRATIVE IMPACT`: a new archetype, composition model, promotion lifecycle, runtime architecture,\n  agent model, governance boundary, or external ecosystem changes the actual story. Update affected\n… preview truncated",
      "related_capabilities": [
        "eval:skill-evaluations",
        "skill:promote-to-commons",
        "skill:validate-visual-artifact"
      ],
      "archetypes": []
    },
    {
      "key": "skill:validate-visual-artifact",
      "id": "validate-visual-artifact",
      "name": "Validate Visual Artifact",
      "type": "skill",
      "path": "skills/validate-visual-artifact/SKILL.md",
      "description": "Independently validate a completed HTML dashboard, presentation, portal, or web UI through static checks and bounded real-browser inspection. Use after a complete artifact exists and before consequential review or release. Do not use to invent the initial design, replace accessibility or business acceptance testing, or claim browser coverage when required states are unreachable.",
      "purpose": "Independently validate a completed HTML dashboard, presentation, portal, or web UI through static checks and bounded real-browser inspection",
      "use_when": [
        "after a complete artifact exists and before consequential review or release"
      ],
      "not_when": [
        "to invent the initial design, replace accessibility or business acceptance testing, or claim browser coverage when required states are unreachable"
      ],
      "inputs": [],
      "workflow": [
        "Gate and static checks",
        "Browser matrix",
        "Corrections and completion"
      ],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Validate Visual Artifact",
        "validate-visual-artifact"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: validate-visual-artifact\ndescription: Independently validate a completed HTML dashboard, presentation, portal, or web UI through static checks and bounded real-browser inspection. Use after a complete artifact exists and before consequential review or release. Do not use to invent the initial design, replace accessibility or business acceptance testing, or claim browser coverage when required states are unreachable.\n---\n\n# Validate a visual artifact\n\nReview an implemented artifact; do not use QA to invent the initial design.\n\n## Gate and static checks\n\nConfirm the artifact, expected routes/sections, source state, target viewports, and acceptance criteria.\nIf incomplete, return to implementation. Run:\n\n```bash\npython3 scripts/validate_html.py \u003cartifact.html> --json\n```\n\nFor an artifact generated from an evidence-derived brand profile, run:\n\n```bash\nnode scripts/capture_brand_qa.mjs --html \u003cartifact.html> --brand-profile \u003cbrand-profile.json> \\\n  --artifact-kind \u003cdashboard-or-presentation> --output \u003cbrand-qa.json>\npython3 scripts/validate_html.py \u003cartifact.html> --brand-profile \u003cbrand-profile.json> \\\n  --brand-qa \u003cbrand-qa.json> --peer-html \u003cpaired-artifact.html> --json\n```\n\n`capture_brand_qa.mjs` records desktop (1440x1000), tablet (768x1024), and mobile (390x844) states, each with\ncomputed styles, visible identity, console health, and horizontal-reflow evidence. Validation rejects a\nmanifest that captures no viewport 480px or narrower, and any state that overflows horizontally or loses the\nofficial identity. Never describe responsive behavior as validated from a single desktop capture.\n\nReport five independent results where applicable: `STRUCTURE_PASS`, `STATIC_HTML_PASS`,\n`BRAND_PROFILE_CONSISTENT`, `BRAND_FIDELITY_PASS`, and `VISUAL_QA_PASS`. Profile consistency verifies the\ndeclared contract only; it must never imply fidelity. Fidelity additionally requires exact official favicon\nand logo bytes, peer artifact agreement, source-evidenced colors, no visible generic fallback palette, and a\nbrowser render that visibly expresses the resolved identity at every captured viewport.\n\nResolve structural blockers, duplicate IDs, external-dependency violations, missing accessibility labels,\nor absent print/reduced-motion rules before browser work.\n\nFor a self-contained artifact and a JSON state matrix, capture reproducible browser evidence with:\n\n```bash\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "eval:skill-evaluations",
        "overlay:bilingual-client-delivery",
        "overlay:branded-html",
        "overlay:living-dashboard",
        "overlay:public-sector-client-delivery",
        "skill:build-living-dashboard",
        "skill:create-branded-html-artifact",
        "skill:create-class-diagram",
        "skill:create-component-architecture-diagram",
        "skill:create-data-flow-diagram",
        "skill:create-er-diagram",
        "skill:create-sequence-diagram",
        "skill:create-system-landscape-diagram",
        "skill:create-technical-diagram",
        "skill:localize-client-artifact",
        "skill:polish-html-artifact",
        "skill:update-commons-presentation",
        "tool:validate-html"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "skill:validate-work-item-assumptions",
      "id": "validate-work-item-assumptions",
      "name": "Validate Work Item Assumptions",
      "type": "skill",
      "path": "skills/validate-work-item-assumptions/SKILL.md",
      "description": "Read-only check of whether a previously filed work item's stated assumptions about current system state still hold, returning confirmed, changed, and unverified claims plus one materiality verdict. Use before planning, estimating, reopening, or reviewing an item that was filed earlier than now. Do not use to decide whether the work proceeds, to propose a revised approach, to edit the item or any other file, or to review a change that is already in progress.",
      "purpose": "Read-only check of whether a previously filed work item's stated assumptions about current system state still hold, returning confirmed, changed, and unverified claims plus one materiality verdict",
      "use_when": [
        "before planning, estimating, reopening, or reviewing an item that was filed earlier than now"
      ],
      "not_when": [
        "to decide whether the work proceeds, to propose a revised approach, to edit the item or any other file, or to review a change that is already in progress"
      ],
      "inputs": [],
      "workflow": [
        "Boundaries",
        "Establish the claims",
        "Check each claim",
        "Judge materiality",
        "Report",
        "Completion and stop conditions"
      ],
      "outputs": [],
      "validation": [],
      "tags": [
        "assumptions still hold",
        "before planning",
        "pre-planning-staleness-check",
        "reopen item",
        "stale item",
        "still valid",
        "work-item-assumption-validation"
      ],
      "search_terms": [
        "assumptions still hold",
        "before planning",
        "pre-planning-staleness-check",
        "reopen item",
        "stale item",
        "still valid",
        "Validate Work Item Assumptions",
        "validate-work-item-assumptions",
        "work-item-assumption-validation"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: validate-work-item-assumptions\ndescription: Read-only check of whether a previously filed work item's stated assumptions about current system state still hold, returning confirmed, changed, and unverified claims plus one materiality verdict. Use before planning, estimating, reopening, or reviewing an item that was filed earlier than now. Do not use to decide whether the work proceeds, to propose a revised approach, to edit the item or any other file, or to review a change that is already in progress.\n---\n\n# Validate work-item assumptions\n\nA work item records what was true when someone filed it. By the time it is picked up, the system may have\npartly solved the problem, renamed what the item names, or moved the context out from under its approach.\nPlanning on a stale premise is expensive; a bounded spot-check is cheap.\n\nEstablish what no longer holds. Do not decide what to do about it — the caller owns that decision.\n\n## Boundaries\n\nRead-only. Do not edit the item, the system, or any other file. Do not implement, file follow-up work,\npropose a revised approach, or run a full build, test suite, or other long operation. Targeted reads and\nhistory queries only.\n\nReport on the item as filed. If the caller supplies its own paraphrase of the item, treat that as context\nfor what matters, never as a replacement for reading the item.\n\n## Establish the claims\n\n1. Read the work item from its authoritative record, not from a generated index, digest, or summary view.\n2. Extract its **falsifiable** claims about current state, separating them from narrative and from proposed\n   solutions. Falsifiable claims name a thing and assert something checkable about it:\n   - files, modules, symbols, interfaces, endpoints, tables, or configuration it says exist;\n   - behavior it calls missing, broken, duplicated, or slow;\n   - patterns, conventions, or constraints it assumes are in force;\n   - dependencies, versions, or external contracts it relies on.\n3. Ignore claims that cannot be checked from the system as it stands — an appetite, a preference, a\n   business priority, or a value judgment is not a staleness signal. Record them as out of scope.\n\nAn item with no falsifiable claims is a valid finding: say so and stop. There is nothing to go stale.\n\n## Check each claim\n\nSpot-check every extracted claim against current state. Read narrowly — a targeted search, a bounded\n… preview truncated",
      "related_capabilities": [
        "eval:skill-evaluations",
        "skill:continue-project",
        "skill:deconstruct-problem-first-principles",
        "skill:implement-ready-slice",
        "skill:plan-work",
        "skill:review-openspec-change"
      ],
      "archetypes": []
    },
    {
      "key": "skill:verify-openspec-implementation",
      "id": "verify-openspec-implementation",
      "name": "Verify OpenSpec Implementation",
      "type": "skill",
      "path": "skills/verify-openspec-implementation/SKILL.md",
      "description": "Independently verify that a completed implementation satisfies one OpenSpec change across requirements, scenarios, tasks, design, tests, and repository gates. Use after implementation and before archive or closure. Do not use to implement missing behavior, rewrite the specification to match code, treat checked boxes as proof, or archive a change with unresolved critical mismatches.",
      "purpose": "Independently verify that a completed implementation satisfies one OpenSpec change across requirements, scenarios, tasks, design, tests, and repository gates",
      "use_when": [
        "after implementation and before archive or closure"
      ],
      "not_when": [
        "to implement missing behavior, rewrite the specification to match code, treat checked boxes as proof, or archive a change with unresolved critical mismatches"
      ],
      "inputs": [
        "implemented active OpenSpec change",
        "code and tests",
        "validation evidence"
      ],
      "workflow": [
        "Build the verification set",
        "Reconcile every material claim",
        "Decide validation and archive readiness"
      ],
      "outputs": [
        "archive-readiness decision",
        "requirement scenario code and test map",
        "severity-ranked mismatches"
      ],
      "validation": [],
      "tags": [
        "OpenSpec",
        "acceptance criteria",
        "implementation verification",
        "openspec-implementation-verification",
        "spec-driven",
        "spec-first",
        "specification",
        "specification-code-test-reconciliation"
      ],
      "search_terms": [
        "acceptance criteria",
        "implementation verification",
        "OpenSpec",
        "openspec-implementation-verification",
        "spec-driven",
        "spec-first",
        "specification",
        "specification-code-test-reconciliation",
        "Verify OpenSpec Implementation",
        "verify-openspec-implementation"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "---\nname: verify-openspec-implementation\ndescription: Independently verify that a completed implementation satisfies one OpenSpec change across requirements, scenarios, tasks, design, tests, and repository gates. Use after implementation and before archive or closure. Do not use to implement missing behavior, rewrite the specification to match code, treat checked boxes as proof, or archive a change with unresolved critical mismatches.\n---\n\n# Verify implementation against OpenSpec\n\nVerification reconciles the approved change with current code and observable evidence. It is not an\nimplementation pass and does not make divergence disappear by editing the specification after the fact.\n\n## Build the verification set\n\n1. Resolve the exact active change and read governance, Git state, OpenSpec configuration, main specs, change\n   metadata and artifacts, implementation diff, tests, and recorded commands/results.\n2. Run `openspec status --change \u003cname> --json`, `openspec show \u003cname> --json`, and\n   `openspec validate \u003cname> --strict --no-interactive`.\n3. If the project exposes the expanded OpenSpec verify action, use it as additional evidence, not as a\n   substitute for repository tests or semantic review.\n4. Keep verification read-only. When missing work is found, return it to the implementation or specification\n   workflow instead of fixing it while claiming independence.\n\nVerification may inspect completed slice packets incrementally while other independent slices continue, but\neach finding must name the immutable slice checkpoint and input revisions it examined. Incremental review can\nreject or return one slice early; it cannot produce change-level `PASS` or archive readiness.\n\n## Reconcile every material claim\n\nFor each requirement and scenario, identify:\n\n- the implementation path and behavior that satisfy it;\n- the task or slice that delivered it;\n- the stable automated test or exact manual/operational verification;\n- the latest result and whether the oracle is credible;\n- the mutation quality status for that behavior where mutation testing applies, including any accepted\n  equivalent mutants and unresolved test gaps;\n- any divergence, partial behavior, untested edge, or unsupported completion claim.\n\nConfirm all tasks are actually complete, design decisions are reflected in code or explicitly superseded,\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "eval:skill-evaluations",
        "skill:audit-delivery-traceability",
        "skill:build-living-dashboard",
        "skill:complete-openspec-change",
        "skill:continue-project",
        "skill:design-test-strategy",
        "skill:implement-openspec-change",
        "skill:implement-ready-slice",
        "skill:mutation-testing",
        "skill:test-driven-development"
      ],
      "archetypes": [
        "development"
      ]
    },
    {
      "key": "agent:architecture-reviewer",
      "id": "architecture-reviewer",
      "name": "Architecture Reviewer",
      "type": "agent",
      "path": "agents/architecture-reviewer.yaml",
      "description": "Independent architecture reviewer for consequential designs and structural changes. Use a fresh context to challenge evidence, boundaries, dependency direction, data and state ownership, quality attributes, migration seams, operational assumptions, and accidental complexity; prefer the relevant architecture skill in the main agent when independence adds no value.",
      "purpose": "Independently assess a proposed or implemented architecture against supplied requirements, decisions, invariants, and evidence without designing or implementing the solution on behalf of its owner.",
      "use_when": [
        "a fresh context to challenge evidence, boundaries, dependency direction, data and state ownership, quality attributes, migration seams, operational assumptions, and accidental complexity; prefer the relevant architecture skill in the main agent when independence adds no value"
      ],
      "not_when": [
        "modify implementation, architecture, or production state",
        "become the target-design owner",
        "approve release or close architecture decisions",
        "invent requirements or present preferences as defects"
      ],
      "inputs": [
        "review scope and exclusions",
        "requirements, scenarios, and invariants",
        "current and proposed architecture evidence",
        "accepted decisions and constraints",
        "validation results",
        "isolated output path"
      ],
      "workflow": [
        "trace architectural claims to evidence and decisions",
        "challenge boundaries and quality-attribute trade-offs",
        "identify contradictions, unsupported assumptions, failure modes, and unnecessary complexity",
        "rank actionable findings by consequence"
      ],
      "outputs": [
        "scope and evidence map",
        "assumptions, conflicts, and unknowns",
        "severity-ranked findings with exact evidence",
        "affected quality attributes and failure paths",
        "validation gaps and decision-owner questions",
        "review limits"
      ],
      "validation": [
        "Read authorized evidence and write only isolated findings under the supplied review path."
      ],
      "tags": [
        "code and configuration search",
        "file reading",
        "isolated report writing",
        "read-only command execution"
      ],
      "search_terms": [
        "Architecture Reviewer",
        "architecture-reviewer",
        "code and configuration search",
        "file reading",
        "isolated report writing",
        "read-only command execution"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "{\n  \"id\": \"architecture-reviewer\",\n  \"kind\": \"agent\",\n  \"version\": 1,\n  \"description\": \"Independent architecture reviewer for consequential designs and structural changes. Use a fresh context to challenge evidence, boundaries, dependency direction, data and state ownership, quality attributes, migration seams, operational assumptions, and accidental complexity; prefer the relevant architecture skill in the main agent when independence adds no value.\",\n  \"responsibility\": \"Independently assess a proposed or implemented architecture against supplied requirements, decisions, invariants, and evidence without designing or implementing the solution on behalf of its owner.\",\n  \"read_write_posture\": \"Read authorized evidence and write only isolated findings under the supplied review path.\",\n  \"allowed_behavior\": [\n    \"trace architectural claims to evidence and decisions\",\n    \"challenge boundaries and quality-attribute trade-offs\",\n    \"identify contradictions, unsupported assumptions, failure modes, and unnecessary complexity\",\n    \"rank actionable findings by consequence\"\n  ],\n  \"forbidden_behavior\": [\n    \"modify implementation, architecture, or production state\",\n    \"become the target-design owner\",\n    \"approve release or close architecture decisions\",\n    \"invent requirements or present preferences as defects\"\n  ],\n  \"expected_inputs\": [\n    \"review scope and exclusions\",\n    \"requirements, scenarios, and invariants\",\n    \"current and proposed architecture evidence\",\n    \"accepted decisions and constraints\",\n    \"validation results\",\n    \"isolated output path\"\n  ],\n  \"expected_outputs\": [\n    \"scope and evidence map\",\n    \"assumptions, conflicts, and unknowns\",\n    \"severity-ranked findings with exact evidence\",\n    \"affected quality attributes and failure paths\",\n    \"validation gaps and decision-owner questions\",\n    \"review limits\"\n  ],\n  \"delegation_boundaries\": \"The architecture or implementation owner supplies evidence and owns decisions and remediation. The reviewer remains findings-only and does not delegate implementation.\",\n  \"capabilities_needed\": [\n    \"file reading\",\n    \"code and configuration search\",\n    \"read-only command execution\",\n    \"isolated report writing\"\n  ],\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "eval:agent-evaluations"
      ],
      "archetypes": [
        "development",
        "legacy-migration"
      ]
    },
    {
      "key": "agent:financial-forecast-reviewer",
      "id": "financial-forecast-reviewer",
      "name": "Financial Forecast Reviewer",
      "type": "agent",
      "path": "agents/financial-forecast-reviewer.yaml",
      "description": "Independent financial-forecast reviewer for consequential project or engagement forecasts. Use a fresh context to challenge source integrity, period and unit consistency, forecast drivers, earned-value calculations, scenario sensitivity, reconciliation, confidentiality, and unsupported certainty; prefer forecast-project-financials in the main agent when independence adds no value.",
      "purpose": "Independently assess whether a completed project financial forecast is arithmetically sound, evidence-backed, decision-useful, and appropriately qualified without changing the forecast.",
      "use_when": [
        "a fresh context to challenge source integrity, period and unit consistency, forecast drivers, earned-value calculations, scenario sensitivity, reconciliation, confidentiality, and unsupported certainty; prefer forecast-project-financials in the main agent when independence adds no value"
      ],
      "not_when": [
        "edit the forecast model source data or commercial assumptions",
        "invent missing actuals rates or business drivers",
        "approve a price commitment budget release or accounting treatment",
        "provide tax investment or statutory accounting advice",
        "repeat restricted financial data outside the authorized output"
      ],
      "inputs": [
        "forecast purpose scope horizon currency and as-of date",
        "approved baseline and authoritative actuals",
        "remaining-work drivers and scenario assumptions",
        "calculation output and reconciliation evidence",
        "materiality threshold confidentiality boundary and isolated output path"
      ],
      "workflow": [
        "reperform material calculations and reconcile totals",
        "challenge source dates currencies units periods and scope alignment",
        "test forecast drivers scenarios sensitivities and earned-value interpretations",
        "identify confidentiality exposure unsupported precision and decision risks"
      ],
      "outputs": [
        "source and reconciliation assessment",
        "formula and unit findings",
        "driver scenario and sensitivity findings",
        "material variance and decision-risk findings",
        "severity-ranked corrections verification needs and limitations",
        "verdict of FORECAST-CREDIBLE VERIFY-FIRST or BLOCKED"
      ],
      "validation": [
        "Read authorized forecast inputs, source reconciliations, assumptions, calculations, delivery evidence, and outputs and write only isolated findings."
      ],
      "tags": [
        "deterministic recalculation",
        "isolated report writing",
        "read-only file and spreadsheet inspection",
        "source and period reconciliation"
      ],
      "search_terms": [
        "deterministic recalculation",
        "Financial Forecast Reviewer",
        "financial-forecast-reviewer",
        "isolated report writing",
        "read-only file and spreadsheet inspection",
        "source and period reconciliation"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "{\n  \"id\": \"financial-forecast-reviewer\",\n  \"kind\": \"agent\",\n  \"version\": 1,\n  \"description\": \"Independent financial-forecast reviewer for consequential project or engagement forecasts. Use a fresh context to challenge source integrity, period and unit consistency, forecast drivers, earned-value calculations, scenario sensitivity, reconciliation, confidentiality, and unsupported certainty; prefer forecast-project-financials in the main agent when independence adds no value.\",\n  \"responsibility\": \"Independently assess whether a completed project financial forecast is arithmetically sound, evidence-backed, decision-useful, and appropriately qualified without changing the forecast.\",\n  \"read_write_posture\": \"Read authorized forecast inputs, source reconciliations, assumptions, calculations, delivery evidence, and outputs and write only isolated findings.\",\n  \"allowed_behavior\": [\n    \"reperform material calculations and reconcile totals\",\n    \"challenge source dates currencies units periods and scope alignment\",\n    \"test forecast drivers scenarios sensitivities and earned-value interpretations\",\n    \"identify confidentiality exposure unsupported precision and decision risks\"\n  ],\n  \"forbidden_behavior\": [\n    \"edit the forecast model source data or commercial assumptions\",\n    \"invent missing actuals rates or business drivers\",\n    \"approve a price commitment budget release or accounting treatment\",\n    \"provide tax investment or statutory accounting advice\",\n    \"repeat restricted financial data outside the authorized output\"\n  ],\n  \"expected_inputs\": [\n    \"forecast purpose scope horizon currency and as-of date\",\n    \"approved baseline and authoritative actuals\",\n    \"remaining-work drivers and scenario assumptions\",\n    \"calculation output and reconciliation evidence\",\n    \"materiality threshold confidentiality boundary and isolated output path\"\n  ],\n  \"expected_outputs\": [\n    \"source and reconciliation assessment\",\n    \"formula and unit findings\",\n    \"driver scenario and sensitivity findings\",\n    \"material variance and decision-risk findings\",\n    \"severity-ranked corrections verification needs and limitations\",\n    \"verdict of FORECAST-CREDIBLE VERIFY-FIRST or BLOCKED\"\n  ],\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:research",
        "eval:agent-evaluations",
        "overlay:consulting-delivery"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "research"
      ]
    },
    {
      "key": "agent:legacy-discovery-specialist",
      "id": "legacy-discovery-specialist",
      "name": "Legacy Discovery Specialist",
      "type": "agent",
      "path": "agents/legacy-discovery-specialist.yaml",
      "description": "Isolated bounded legacy-source analyst for non-overlapping internal analysis slices with coordinator-owned integration. It never defines the user-facing completion boundary; use analyze-legacy-system as the full-scope coordinator.",
      "purpose": "Analyze one explicitly assigned legacy-source batch and return evidence for coordinator-owned integration.",
      "use_when": [],
      "not_when": [
        "silently expand or shrink scope",
        "claim system-level completeness",
        "edit canonical registries, shared project memory, dashboards, source code, staging state, or commits",
        "integrate findings without coordinator review"
      ],
      "inputs": [
        "batch ID",
        "primary and contextual paths",
        "protected and excluded paths",
        "source hashes",
        "language variant",
        "analysis questions",
        "isolated output path",
        "evidence schema",
        "validation command"
      ],
      "workflow": [
        "verify assigned paths and hashes",
        "trace entry points, calls, data, rules, persistence, integrations, errors, and unknown edges",
        "write isolated evidence and findings under the assigned output path"
      ],
      "outputs": [
        "status and batch ID",
        "inspected paths and hashes",
        "output paths and temporary evidence IDs",
        "skipped or failed paths with reasons",
        "unresolved dependencies",
        "validation result and limitations",
        "one recommended coordinator action"
      ],
      "validation": [
        "Read assigned source paths and write only isolated worker output under the coordinator-supplied path."
      ],
      "tags": [
        "code search",
        "file reading",
        "isolated output writing",
        "read-only command execution"
      ],
      "search_terms": [
        "code search",
        "file reading",
        "isolated output writing",
        "Legacy Discovery Specialist",
        "legacy-discovery-specialist",
        "read-only command execution"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "{\n  \"id\": \"legacy-discovery-specialist\",\n  \"kind\": \"agent\",\n  \"version\": 1,\n  \"description\": \"Isolated bounded legacy-source analyst for non-overlapping internal analysis slices with coordinator-owned integration. It never defines the user-facing completion boundary; use analyze-legacy-system as the full-scope coordinator.\",\n  \"responsibility\": \"Analyze one explicitly assigned legacy-source batch and return evidence for coordinator-owned integration.\",\n  \"read_write_posture\": \"Read assigned source paths and write only isolated worker output under the coordinator-supplied path.\",\n  \"allowed_behavior\": [\n    \"verify assigned paths and hashes\",\n    \"trace entry points, calls, data, rules, persistence, integrations, errors, and unknown edges\",\n    \"write isolated evidence and findings under the assigned output path\"\n  ],\n  \"forbidden_behavior\": [\n    \"silently expand or shrink scope\",\n    \"claim system-level completeness\",\n    \"edit canonical registries, shared project memory, dashboards, source code, staging state, or commits\",\n    \"integrate findings without coordinator review\"\n  ],\n  \"expected_inputs\": [\n    \"batch ID\",\n    \"primary and contextual paths\",\n    \"protected and excluded paths\",\n    \"source hashes\",\n    \"language variant\",\n    \"analysis questions\",\n    \"isolated output path\",\n    \"evidence schema\",\n    \"validation command\"\n  ],\n  \"expected_outputs\": [\n    \"status and batch ID\",\n    \"inspected paths and hashes\",\n    \"output paths and temporary evidence IDs\",\n    \"skipped or failed paths with reasons\",\n    \"unresolved dependencies\",\n    \"validation result and limitations\",\n    \"one recommended coordinator action\"\n  ],\n  \"delegation_boundaries\": \"The coordinator owns scope, shared state, integration, and acceptance. This role does not delegate further unless the runtime adapter and coordinator explicitly allow it.\",\n  \"capabilities_needed\": [\n    \"file reading\",\n    \"code search\",\n    \"read-only command execution\",\n    \"isolated output writing\"\n  ],\n… preview truncated",
      "related_capabilities": [
        "archetype:legacy-migration",
        "eval:agent-evaluations"
      ],
      "archetypes": [
        "legacy-migration"
      ]
    },
    {
      "key": "agent:privacy-security-reviewer",
      "id": "privacy-security-reviewer",
      "name": "Privacy Security Reviewer",
      "type": "agent",
      "path": "agents/privacy-security-reviewer.yaml",
      "description": "Independent privacy and security reviewer for consequential designs and changes. Use a fresh context to challenge data handling, trust boundaries, abuse paths, secrets, logging, deployment assumptions, negative tests, and unsupported control claims; prefer the review-privacy-security skill in the main agent when independence adds no value.",
      "purpose": "Independently assess privacy and security evidence and return findings without implementing fixes or approving release.",
      "use_when": [
        "a fresh context to challenge data handling, trust boundaries, abuse paths, secrets, logging, deployment assumptions, negative tests, and unsupported control claims; prefer the review-privacy-security skill in the main agent when independence adds no value"
      ],
      "not_when": [
        "modify implementation or production state",
        "claim compliance certification or penetration-test coverage",
        "expose secrets or sensitive source data in review output",
        "approve release or close risk decisions"
      ],
      "inputs": [
        "review scope and exclusions",
        "system or change evidence",
        "data classes and actors",
        "policy or threat assumptions",
        "validation access",
        "isolated output path"
      ],
      "workflow": [
        "map data flows and trust boundaries",
        "challenge controls with concrete abuse paths and negative tests",
        "rank evidence-backed findings and state review limits"
      ],
      "outputs": [
        "scope and evidence map",
        "assumptions and unknowns",
        "severity-ranked findings",
        "abuse or failure paths",
        "existing controls and validation gaps",
        "residual risk and limitations"
      ],
      "validation": [
        "Read authorized evidence and write only an isolated review report or structured findings under the supplied output path."
      ],
      "tags": [
        "code and configuration search",
        "file reading",
        "isolated report writing",
        "read-only command execution"
      ],
      "search_terms": [
        "code and configuration search",
        "file reading",
        "isolated report writing",
        "Privacy Security Reviewer",
        "privacy-security-reviewer",
        "read-only command execution"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "{\n  \"id\": \"privacy-security-reviewer\",\n  \"kind\": \"agent\",\n  \"version\": 1,\n  \"description\": \"Independent privacy and security reviewer for consequential designs and changes. Use a fresh context to challenge data handling, trust boundaries, abuse paths, secrets, logging, deployment assumptions, negative tests, and unsupported control claims; prefer the review-privacy-security skill in the main agent when independence adds no value.\",\n  \"responsibility\": \"Independently assess privacy and security evidence and return findings without implementing fixes or approving release.\",\n  \"read_write_posture\": \"Read authorized evidence and write only an isolated review report or structured findings under the supplied output path.\",\n  \"allowed_behavior\": [\n    \"map data flows and trust boundaries\",\n    \"challenge controls with concrete abuse paths and negative tests\",\n    \"rank evidence-backed findings and state review limits\"\n  ],\n  \"forbidden_behavior\": [\n    \"modify implementation or production state\",\n    \"claim compliance certification or penetration-test coverage\",\n    \"expose secrets or sensitive source data in review output\",\n    \"approve release or close risk decisions\"\n  ],\n  \"expected_inputs\": [\n    \"review scope and exclusions\",\n    \"system or change evidence\",\n    \"data classes and actors\",\n    \"policy or threat assumptions\",\n    \"validation access\",\n    \"isolated output path\"\n  ],\n  \"expected_outputs\": [\n    \"scope and evidence map\",\n    \"assumptions and unknowns\",\n    \"severity-ranked findings\",\n    \"abuse or failure paths\",\n    \"existing controls and validation gaps\",\n    \"residual risk and limitations\"\n  ],\n  \"delegation_boundaries\": \"The implementation owner supplies evidence and owns remediation. The reviewer remains read-only, does not delegate implementation, and does not certify compliance.\",\n  \"capabilities_needed\": [\n    \"file reading\",\n    \"code and configuration search\",\n    \"read-only command execution\",\n    \"isolated report writing\"\n  ],\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "eval:agent-evaluations"
      ],
      "archetypes": [
        "development"
      ]
    },
    {
      "key": "agent:test-behavior-reviewer",
      "id": "test-behavior-reviewer",
      "name": "Test Behavior Reviewer",
      "type": "agent",
      "path": "agents/test-behavior-reviewer.yaml",
      "description": "Independent test and behavior reviewer for consequential changes. Use a fresh context to challenge scenario coverage, test-layer choice, behavior-relevant RED evidence, boundary cases, mocks, mutation survivor classifications and hardening evidence, flaky or false confidence, and user-visible acceptance; prefer test-driven-development, design-test-strategy, or mutation-testing in the main agent for implementation planning and execution.",
      "purpose": "Independently assess whether test evidence credibly demonstrates the claimed behavior without changing the implementation or tests.",
      "use_when": [
        "a fresh context to challenge scenario coverage, test-layer choice, behavior-relevant RED evidence, boundary cases, mocks, mutation survivor classifications and hardening evidence, flaky or false confidence, and user-visible acceptance; prefer test-driven-development, design-test-strategy, or mutation-testing in the main agent for implementation planning and execution"
      ],
      "not_when": [
        "edit tests or production code",
        "accept setup failures as RED",
        "treat coverage percentage as behavioral proof",
        "approve completion or release",
        "treat a mutation score as behavioral proof",
        "accept an unsupported or flaky-blocked mutation run as validated test quality"
      ],
      "inputs": [
        "claimed behavior and acceptance criteria",
        "risk or test strategy",
        "RED GREEN and full-gate evidence",
        "implementation and test paths",
        "known limitations",
        "isolated output path",
        "mutation quality status, survivor classifications, and accepted equivalent mutants"
      ],
      "workflow": [
        "reconcile acceptance behavior with tests",
        "challenge test-layer choice and RED validity",
        "identify missing boundary, negative, integration, migration, security, or user-visible coverage",
        "challenge surviving-mutant classifications, equivalent-mutant acceptances, and mutation hardening evidence"
      ],
      "outputs": [
        "claim-to-test map",
        "coverage and oracle findings",
        "RED validity assessment",
        "boundary and false-confidence findings",
        "reproduction guidance",
        "limitations and recommended next validation",
        "mutation survivor and hardening findings with the residual test-quality risk"
      ],
      "validation": [
        "Read authorized code, scenarios, tests, and results and write only an isolated review report or structured findings."
      ],
      "tags": [
        "code and test search",
        "file reading",
        "isolated report writing",
        "read-only test execution when authorized"
      ],
      "search_terms": [
        "code and test search",
        "file reading",
        "isolated report writing",
        "read-only test execution when authorized",
        "Test Behavior Reviewer",
        "test-behavior-reviewer"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "{\n  \"id\": \"test-behavior-reviewer\",\n  \"kind\": \"agent\",\n  \"version\": 1,\n  \"description\": \"Independent test and behavior reviewer for consequential changes. Use a fresh context to challenge scenario coverage, test-layer choice, behavior-relevant RED evidence, boundary cases, mocks, mutation survivor classifications and hardening evidence, flaky or false confidence, and user-visible acceptance; prefer test-driven-development, design-test-strategy, or mutation-testing in the main agent for implementation planning and execution.\",\n  \"responsibility\": \"Independently assess whether test evidence credibly demonstrates the claimed behavior without changing the implementation or tests.\",\n  \"read_write_posture\": \"Read authorized code, scenarios, tests, and results and write only an isolated review report or structured findings.\",\n  \"allowed_behavior\": [\n    \"reconcile acceptance behavior with tests\",\n    \"challenge test-layer choice and RED validity\",\n    \"identify missing boundary, negative, integration, migration, security, or user-visible coverage\",\n    \"challenge surviving-mutant classifications, equivalent-mutant acceptances, and mutation hardening evidence\"\n  ],\n  \"forbidden_behavior\": [\n    \"edit tests or production code\",\n    \"accept setup failures as RED\",\n    \"treat coverage percentage as behavioral proof\",\n    \"approve completion or release\",\n    \"treat a mutation score as behavioral proof\",\n    \"accept an unsupported or flaky-blocked mutation run as validated test quality\"\n  ],\n  \"expected_inputs\": [\n    \"claimed behavior and acceptance criteria\",\n    \"risk or test strategy\",\n    \"RED GREEN and full-gate evidence\",\n    \"implementation and test paths\",\n    \"known limitations\",\n    \"isolated output path\",\n    \"mutation quality status, survivor classifications, and accepted equivalent mutants\"\n  ],\n  \"expected_outputs\": [\n    \"claim-to-test map\",\n    \"coverage and oracle findings\",\n    \"RED validity assessment\",\n    \"boundary and false-confidence findings\",\n    \"reproduction guidance\",\n    \"limitations and recommended next validation\",\n    \"mutation survivor and hardening findings with the residual test-quality risk\"\n  ],\n  \"delegation_boundaries\": \"The implementer owns TDD and corrections. The reviewer remains independent and findings-only, and does not delegate implementation.\",\n  \"capabilities_needed\": [\n    \"file reading\",\n    \"code and test search\",\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "eval:agent-evaluations"
      ],
      "archetypes": [
        "development",
        "legacy-migration"
      ]
    },
    {
      "key": "tool:analyze-project-delivery",
      "id": "analyze-project-delivery",
      "name": "Analyze Project Delivery",
      "type": "tool",
      "path": "skills/manage-project-delivery/scripts/analyze_project_delivery.py",
      "description": "Validate a project delivery register and derive deterministic status signals.",
      "purpose": "Validate a project delivery register and derive deterministic status signals.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Analyze Project Delivery",
        "analyze-project-delivery"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Validate a project delivery register and derive deterministic status signals.\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport math\nimport sys\nfrom collections import Counter\nfrom datetime import date\nfrom pathlib import Path\nfrom typing import Any\n\n\nSTATUSES = {\"PLANNED\", \"IN_PROGRESS\", \"BLOCKED\", \"DONE\", \"CANCELLED\"}\nRISK_STATUSES = {\"OPEN\", \"MITIGATED\", \"ACCEPTED\", \"CLOSED\"}\n\n\ndef load_input(path: Path) -> dict[str, Any]:\n    value = json.loads(path.read_text(encoding=\"utf-8\"))\n    if not isinstance(value, dict):\n        raise ValueError(\"input root must be an object\")\n    return value\n\n\ndef parse_date(value: Any, field: str, errors: list[str]) -> date | None:\n    if not isinstance(value, str):\n        errors.append(f\"{field} must be an ISO date\")\n        return None\n    try:\n        return date.fromisoformat(value)\n    except ValueError:\n        errors.append(f\"{field} must be an ISO date\")\n        return None\n\n\ndef number(value: Any, field: str, errors: list[str]) -> float | None:\n    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):\n        errors.append(f\"{field} must be a finite number\")\n        return None\n    return float(value)\n\n\ndef topological_order(nodes: dict[str, dict[str, Any]], errors: list[str]) -> list[str]:\n    order: list[str] = []\n    state: dict[str, int] = {}\n\n    def visit(identifier: str, trail: list[str]) -> None:\n        marker = state.get(identifier, 0)\n        if marker == 2:\n            return\n        if marker == 1:\n            cycle_start = trail.index(identifier) if identifier in trail else 0\n            cycle = trail[cycle_start:] + [identifier]\n            errors.append(f\"dependency cycle: {' -> '.join(cycle)}\")\n            return\n        state[identifier] = 1\n        for dependency in sorted(nodes[identifier][\"dependencies\"]):\n            if dependency in nodes:\n                visit(dependency, trail + [identifier])\n        state[identifier] = 2\n        order.append(identifier)\n\n    for identifier in sorted(nodes):\n        visit(identifier, [])\n    return order\n\n\ndef analyze(payload: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:\n    errors: list[str] = []\n    warnings: list[str] = []\n    if payload.get(\"schema_version\") != 1:\n        errors.append(\"schema_version must be 1\")\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:research",
        "overlay:consulting-delivery",
        "skill:manage-project-delivery"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "research"
      ]
    },
    {
      "key": "tool:anonymize-structured-data",
      "id": "anonymize-structured-data",
      "name": "Anonymize Structured Data",
      "type": "tool",
      "path": "skills/anonymize-data/scripts/anonymize_data.py",
      "description": "Apply deterministic field-scoped anonymization rules to JSON, JSONL, or CSV data.",
      "purpose": "Apply deterministic field-scoped anonymization rules to JSON, JSONL, or CSV data.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Anonymize Structured Data",
        "anonymize-structured-data"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Apply deterministic field-scoped anonymization rules to JSON, JSONL, or CSV data.\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport csv\nimport hashlib\nimport hmac\nimport io\nimport json\nimport os\nimport sys\nimport tempfile\nfrom pathlib import Path\nfrom typing import Any\n\n\nDROP = object()\nALLOWED_STRATEGIES = {\"drop\", \"redact\", \"stable-token\"}\n\n\ndef digest_bytes(value: bytes) -> str:\n    return \"sha256:\" + hashlib.sha256(value).hexdigest()\n\n\ndef read_json(path: Path) -> Any:\n    return json.loads(path.read_text(encoding=\"utf-8\"))\n\n\ndef validate_config(config: Any) -> tuple[list[dict[str, Any]], bool, list[str]]:\n    errors: list[str] = []\n    if not isinstance(config, dict):\n        return [], False, [\"configuration root must be an object\"]\n    if config.get(\"schemaVersion\") != \"1.0.0\":\n        errors.append(\"schemaVersion must be 1.0.0\")\n    case_sensitive = config.get(\"caseSensitiveFields\", True)\n    if not isinstance(case_sensitive, bool):\n        errors.append(\"caseSensitiveFields must be boolean\")\n        case_sensitive = True\n    rules = config.get(\"rules\")\n    if not isinstance(rules, list) or not rules:\n        return [], case_sensitive, errors + [\"rules must be a non-empty array\"]\n\n    normalized_fields: dict[str, str] = {}\n    seen_ids: set[str] = set()\n    valid_rules: list[dict[str, Any]] = []\n    for index, rule in enumerate(rules):\n        label = f\"rules[{index}]\"\n        if not isinstance(rule, dict):\n            errors.append(f\"{label} must be an object\")\n            continue\n        rule_id = rule.get(\"id\")\n        if not isinstance(rule_id, str) or not rule_id.strip():\n            errors.append(f\"{label}.id is required\")\n            continue\n        if rule_id in seen_ids:\n            errors.append(f\"duplicate rule id: {rule_id}\")\n        seen_ids.add(rule_id)\n        fields = rule.get(\"fieldNames\")\n        if not isinstance(fields, list) or not fields or not all(isinstance(field, str) and field for field in fields):\n            errors.append(f\"{rule_id}: fieldNames must be a non-empty string array\")\n            continue\n        strategy = rule.get(\"strategy\")\n        if strategy not in ALLOWED_STRATEGIES:\n            errors.append(f\"{rule_id}: strategy must be one of {sorted(ALLOWED_STRATEGIES)}\")\n        if \"required\" in rule and not isinstance(rule[\"required\"], bool):\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "skill:anonymize-data"
      ],
      "archetypes": [
        "development"
      ]
    },
    {
      "key": "tool:audit-trace-graph",
      "id": "audit-trace-graph",
      "name": "Audit Trace Graph",
      "type": "tool",
      "path": "skills/audit-delivery-traceability/scripts/audit_trace_graph.py",
      "description": "Audit a normalized delivery traceability graph.",
      "purpose": "Audit a normalized delivery traceability graph.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Audit Trace Graph",
        "audit-trace-graph"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Audit a normalized delivery traceability graph.\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport sys\nfrom pathlib import Path\nfrom typing import Any\n\n\nSEVERITIES = {\"critical\", \"major\", \"warning\", \"info\"}\nSEVERITY_ORDER = {\"critical\": 0, \"major\": 1, \"warning\": 2, \"info\": 3}\n\n\ndef require_list(payload: dict[str, Any], key: str) -> list[Any]:\n    value = payload.get(key, [])\n    if not isinstance(value, list):\n        raise ValueError(f\"{key} must be an array\")\n    return value\n\n\ndef require_text(item: dict[str, Any], key: str, context: str) -> str:\n    value = item.get(key)\n    if not isinstance(value, str) or not value.strip():\n        raise ValueError(f\"{context}.{key} must be a non-empty string\")\n    return value.strip()\n\n\ndef audit(payload: object) -> dict[str, Any]:\n    if not isinstance(payload, dict):\n        raise ValueError(\"graph must be a JSON object\")\n    if payload.get(\"schema_version\") != 1:\n        raise ValueError(\"schema_version must be 1\")\n\n    nodes = require_list(payload, \"nodes\")\n    edges = require_list(payload, \"edges\")\n    lifecycle_rules = require_list(payload, \"lifecycle_rules\")\n    generated_views = require_list(payload, \"generated_views\")\n    raw_findings: list[dict[str, str]] = []\n\n    def finding(severity: str, code: str, subject: str, detail: str) -> None:\n        if severity not in SEVERITIES:\n            raise ValueError(f\"unsupported severity: {severity}\")\n        raw_findings.append(\n            {\"severity\": severity, \"code\": code, \"subject\": subject, \"detail\": detail}\n        )\n\n    node_by_id: dict[str, dict[str, Any]] = {}\n    for index, raw_node in enumerate(nodes):\n        if not isinstance(raw_node, dict):\n            raise ValueError(f\"nodes[{index}] must be an object\")\n        node_id = require_text(raw_node, \"id\", f\"nodes[{index}]\")\n        require_text(raw_node, \"type\", f\"nodes[{index}]\")\n        if node_id in node_by_id:\n            finding(\"major\", \"DUPLICATE_NODE_ID\", node_id, \"Node ID is not unique\")\n            continue\n        node_by_id[node_id] = raw_node\n\n    normalized_edges: list[dict[str, str]] = []\n    edge_keys: set[tuple[str, str, str]] = set()\n    for index, raw_edge in enumerate(edges):\n        if not isinstance(raw_edge, dict):\n            raise ValueError(f\"edges[{index}] must be an object\")\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:research",
        "overlay:evidence-traceability",
        "skill:audit-delivery-traceability"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "research"
      ]
    },
    {
      "key": "tool:audit-trace-matrix",
      "id": "audit-trace-matrix",
      "name": "Audit Trace Matrix",
      "type": "tool",
      "path": "skills/audit-delivery-traceability/scripts/audit_trace_matrix.py",
      "description": "Audit a normalized delivery traceability CSV.",
      "purpose": "Audit a normalized delivery traceability CSV.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Audit Trace Matrix",
        "audit-trace-matrix"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Audit a normalized delivery traceability CSV.\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport csv\nimport json\nfrom pathlib import Path\n\nCHAIN = [\"source\", \"evidence\", \"rule\", \"gap\", \"requirement\", \"specification\", \"scenario\", \"implementation\", \"test\", \"result\", \"verification\", \"commit\"]\nMINIMUM = {\n    \"draft\": [\"source\", \"evidence\", \"requirement\"],\n    \"approved\": [\"source\", \"evidence\", \"requirement\", \"specification\", \"scenario\"],\n    \"implemented\": [\"source\", \"evidence\", \"requirement\", \"specification\", \"scenario\", \"implementation\", \"test\", \"result\"],\n    \"verified\": CHAIN,\n    \"complete\": CHAIN,\n}\n\n\ndef main() -> int:\n    parser = argparse.ArgumentParser(description=__doc__)\n    parser.add_argument(\"matrix\", type=Path)\n    parser.add_argument(\"--format\", choices=[\"json\", \"markdown\"], default=\"json\")\n    args = parser.parse_args()\n    with args.matrix.open(newline=\"\", encoding=\"utf-8-sig\") as handle:\n        rows = list(csv.DictReader(handle))\n    findings = []\n    seen = set()\n    for number, row in enumerate(rows, start=2):\n        record_id = (row.get(\"id\") or f\"ROW-{number}\").strip()\n        if record_id in seen:\n            findings.append({\"severity\": \"major\", \"code\": \"DUPLICATE_ID\", \"id\": record_id, \"row\": number, \"detail\": \"ID is not unique\"})\n        seen.add(record_id)\n        status = (row.get(\"status\") or \"draft\").strip().lower()\n        required = MINIMUM.get(status, MINIMUM[\"draft\"])\n        for field in required:\n            if not (row.get(field) or \"\").strip():\n                severity = \"critical\" if status in {\"verified\", \"complete\"} else \"major\"\n                findings.append({\"severity\": severity, \"code\": \"MISSING_LINK\", \"id\": record_id, \"row\": number, \"detail\": f\"{status} record lacks {field}\"})\n        furthest = max((CHAIN.index(field) for field in CHAIN if (row.get(field) or \"\").strip()), default=-1)\n        for index in range(furthest):\n            field = CHAIN[index]\n            if field in {\"rule\", \"gap\"}:\n                continue\n            if not (row.get(field) or \"\").strip():\n                findings.append({\"severity\": \"major\", \"code\": \"CHAIN_GAP\", \"id\": record_id, \"row\": number, \"detail\": f\"{field} is empty before a later lifecycle link\"})\n    result = {\"status\": \"PASS\" if not findings else \"FAIL\", \"rows\": len(rows), \"findings\": findings}\n    if args.format == \"json\":\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:research",
        "overlay:evidence-traceability",
        "skill:audit-delivery-traceability"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "research"
      ]
    },
    {
      "key": "tool:build-capability-index",
      "id": "build-capability-index",
      "name": "Build Capability Index",
      "type": "tool",
      "path": "tools/build_capability_index.py",
      "description": "Generate the fast capability routing index from canonical Commons metadata.",
      "purpose": "Generate the fast capability routing index from canonical Commons metadata.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Build Capability Index",
        "build-capability-index"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Generate the fast capability routing index from canonical Commons metadata.\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport re\nfrom pathlib import Path\nfrom typing import Any\n\nROOT = Path(__file__).resolve().parent.parent\nOUTPUT = ROOT / \"catalog\" / \"capability-index.json\"\n\n\ndef read_json(path: Path) -> dict[str, Any]:\n    value = json.loads(path.read_text(encoding=\"utf-8\"))\n    if not isinstance(value, dict):\n        raise ValueError(f\"expected object: {path}\")\n    return value\n\n\ndef skill_description(path: Path) -> str:\n    text = path.read_text(encoding=\"utf-8\")\n    match = re.search(r\"(?m)^description:\\s*(.+)$\", text)\n    return match.group(1).strip() if match else \"\"\n\n\ndef split_routing(description: str) -> tuple[str, str, str]:\n    do_not = description.find(\" Do not use\")\n    positive = description[:do_not].strip() if do_not >= 0 else description\n    non_trigger = description[do_not + 1:].strip() if do_not >= 0 else \"\"\n    use_when = positive.find(\" Use when\")\n    trigger = positive[use_when + 1:].strip() if use_when >= 0 else positive\n    summary = positive[:use_when].strip() if use_when >= 0 else positive\n    return summary, trigger, non_trigger\n\n\ndef composition_membership() -> tuple[dict[str, set[str]], dict[str, set[str]]]:\n    contract = read_json(ROOT / \"archetypes\" / \"composition.yaml\")\n    archetypes: dict[str, set[str]] = {}\n    overlays: dict[str, set[str]] = {}\n    for registry, target in ((\"archetypes\", archetypes), (\"overlays\", overlays)):\n        for identifier, entry in contract[registry].items():\n            manifest = read_json(ROOT / \"archetypes\" / entry[\"path\"])\n            for group in manifest.get(\"capabilities\", {}).values():\n                for skill in group.get(\"skills\", []):\n                    target.setdefault(skill, set()).add(identifier)\n            for condition in manifest.get(\"conditions\", []):\n                for skill in condition.get(\"capabilities\", {}).get(\"skills\", []):\n                    target.setdefault(skill, set()).add(identifier)\n    return archetypes, overlays\n\n\ndef runtime_support(kind: str) -> list[str]:\n    supported: list[str] = []\n    concept = {\"skills\": \"skills\", \"agents\": \"custom_agents\", \"tools\": \"mcp\", \"templates\": \"project_instructions\"}.get(kind)\n    for path in sorted((ROOT / \"adapters\").glob(\"*/adapter.yaml\")):\n… preview truncated",
      "related_capabilities": [],
      "archetypes": []
    },
    {
      "key": "tool:build-dashboard",
      "id": "build-dashboard",
      "name": "Build Dashboard",
      "type": "tool",
      "path": "skills/build-living-dashboard/scripts/build_dashboard.py",
      "description": "Validate structured lifecycle state and generate a single-file dashboard.",
      "purpose": "Validate structured lifecycle state and generate a single-file dashboard.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Build Dashboard",
        "build-dashboard"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Validate structured lifecycle state and generate a single-file dashboard.\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport hashlib\nimport html\nimport json\nfrom pathlib import Path\nimport re\nimport sys\n\nsys.path.insert(0, str(Path(__file__).resolve().parent))\nsys.path.insert(0, str(Path(__file__).resolve().parents[2] / \"continue-project\" / \"scripts\"))\nfrom brand_profile import (\n    accenture_fallback_attributes,\n    accenture_fallback_css,\n    accenture_fallback_favicon,\n    accenture_fallback_logo,\n    brand_attributes,\n    favicon_markup,\n    logo_markup,\n    render_brand_css,\n    validate_brand_profile,\n)\nfrom resolve_project_continuation import apply_action_projection\nfrom validate_dashboard_visual import contract_fingerprint, load_contract as load_visual_contract, resolved_design_fingerprint\n\nCOLLECTIONS = {\n    \"requirement\": \"requirements\", \"specification\": \"specifications\",\n    \"acceptance_criterion\": \"acceptance_criteria\", \"implementation_item\": \"implementation_items\",\n    \"test\": \"tests\", \"evidence\": \"evidence\",\n}\nRELATIONS = {\n    \"specified-by\": (\"requirement\", \"specification\"),\n    \"defines\": (\"specification\", \"acceptance_criterion\"),\n    \"implemented-by\": ((\"specification\", \"acceptance_criterion\"), \"implementation_item\"),\n    \"validated-by\": ((\"specification\", \"acceptance_criterion\", \"implementation_item\"), \"test\"),\n    \"supported-by\": ((\"requirement\", \"specification\", \"test\"), \"evidence\"),\n    \"depends-on\": (\"specification\", \"specification\"),\n}\nREQUIRED_V2 = {\"title\", \"requirements\", \"specifications\", \"acceptance_criteria\", \"relationships\"}\nSUPPORTED_DASHBOARD_LOCALES = {\"en\", \"de-AT\", \"de-DE\", \"de-CH\"}\nSTRUCTURE_PATH = Path(__file__).resolve().parent.parent / \"assets\" / \"dashboard-structure.json\"\nDOMAIN_BASES = {\"MEASURED\", \"ASSESSED\", \"MIXED\", \"UNKNOWN\", \"NOT_APPLICABLE\"}\nLOCALIZATION_HASH_PREFIX = \"sha256:\"\nPLACEHOLDER_TRANSLATION_PREFIXES = {\n    \"translation\", \"translated\", \"german\", \"deutsch\", \"uebersetzung\", \"übersetzung\",\n}\nTECHNICAL_FIELD_NAMES = {\n    \"id\", \"ids\", \"source\", \"source_ref\", \"source_url\", \"source_path\", \"path\", \"location\", \"command\",\n    \"url\", \"uri\", \"fingerprint\", \"sha256\", \"hash\", \"revision\", \"requirement_revisions\", \"updated_at\",\n    \"created_at\", \"captured_at\", \"status\", \"readiness\", \"implementation_status\", \"validation_status\",\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "overlay:living-dashboard",
        "skill:build-living-dashboard"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "tool:calculate-project-financial-forecast",
      "id": "calculate-project-financial-forecast",
      "name": "Calculate Project Financial Forecast",
      "type": "tool",
      "path": "skills/forecast-project-financials/scripts/calculate_project_forecast.py",
      "description": "Validate and summarize a period-based project financial forecast.",
      "purpose": "Validate and summarize a period-based project financial forecast.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Calculate Project Financial Forecast",
        "calculate-project-financial-forecast"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Validate and summarize a period-based project financial forecast.\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport re\nimport sys\nfrom decimal import Decimal, InvalidOperation\nfrom pathlib import Path\nfrom typing import Any\n\n\nPERIOD_RE = re.compile(r\"^\\d{4}-(0[1-9]|1[0-2])$\")\n\n\ndef load_input(path: Path) -> dict[str, Any]:\n    value = json.loads(path.read_text(encoding=\"utf-8\"))\n    if not isinstance(value, dict):\n        raise ValueError(\"input root must be an object\")\n    return value\n\n\ndef decimal_value(value: Any, field: str, errors: list[str], *, required: bool = True) -> Decimal | None:\n    if value is None and not required:\n        return None\n    if isinstance(value, bool) or not isinstance(value, (int, float, str)):\n        errors.append(f\"{field} must be a non-negative finite number\")\n        return None\n    try:\n        parsed = Decimal(str(value))\n    except InvalidOperation:\n        errors.append(f\"{field} must be a non-negative finite number\")\n        return None\n    if not parsed.is_finite() or parsed \u003c 0:\n        errors.append(f\"{field} must be a non-negative finite number\")\n        return None\n    return parsed\n\n\ndef rendered(value: Decimal | None, places: int = 4) -> float | None:\n    if value is None:\n        return None\n    quantum = Decimal(1).scaleb(-places)\n    return float(value.quantize(quantum))\n\n\ndef ratio(numerator: Decimal, denominator: Decimal, label: str, warnings: list[str]) -> Decimal | None:\n    if denominator == 0:\n        warnings.append(f\"{label} unavailable because denominator is zero\")\n        return None\n    return numerator / denominator\n\n\ndef calculate(payload: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:\n    errors: list[str] = []\n    warnings: list[str] = []\n    if payload.get(\"schema_version\") != 1:\n        errors.append(\"schema_version must be 1\")\n    currency = payload.get(\"currency\")\n    if not isinstance(currency, str) or not currency.strip():\n        errors.append(\"currency is required\")\n    as_of = payload.get(\"as_of_period\")\n    if not isinstance(as_of, str) or not PERIOD_RE.fullmatch(as_of):\n        errors.append(\"as_of_period must use YYYY-MM\")\n\n    period_values = payload.get(\"periods\")\n    if not isinstance(period_values, list) or not period_values:\n        return {}, errors + [\"periods must be a non-empty array\"]\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:research",
        "overlay:consulting-delivery",
        "skill:forecast-project-financials"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "research"
      ]
    },
    {
      "key": "tool:check-presentation-visual-contract",
      "id": "check-presentation-visual-contract",
      "name": "Check Presentation Visual Contract",
      "type": "tool",
      "path": "tools/check_presentation_visual_contract.py",
      "description": "Reject visual or interaction drift in the locked Agent Commons presentation.",
      "purpose": "Reject visual or interaction drift in the locked Agent Commons presentation.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Check Presentation Visual Contract",
        "check-presentation-visual-contract"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Reject visual or interaction drift in the locked Agent Commons presentation.\"\"\"\n\nfrom __future__ import annotations\n\nimport hashlib\nimport json\nimport re\nimport sys\nfrom html.parser import HTMLParser\nfrom pathlib import Path\nfrom typing import Any\n\n\nROOT = Path(__file__).resolve().parent.parent\nPRESENTATION_PATH = ROOT / \"presentation\" / \"index.html\"\nCONTRACT_PATH = ROOT / \"presentation\" / \"visual-contract.json\"\n\nCONTENT_ATTRIBUTES = {\n    \"alt\",\n    \"aria-description\",\n    \"aria-label\",\n    \"content\",\n    \"placeholder\",\n    \"title\",\n    \"value\",\n}\n\n\ndef digest(value: str) -> str:\n    return hashlib.sha256(value.encode(\"utf-8\")).hexdigest()\n\n\nclass StructureParser(HTMLParser):\n    \"\"\"Capture markup and visual attributes while intentionally ignoring text.\"\"\"\n\n    def __init__(self) -> None:\n        super().__init__(convert_charrefs=True)\n        self.tokens: list[str] = []\n        self.data_theme = \"\"\n        self.data_visual_thesis = \"\"\n        self.theme_color = \"\"\n\n    def handle_decl(self, decl: str) -> None:\n        self.tokens.append(f\"\u003c!{decl.lower()}>\")\n\n    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:\n        values = dict(attrs)\n        if tag == \"html\":\n            self.data_theme = values.get(\"data-theme\", \"\") or \"\"\n            self.data_visual_thesis = values.get(\"data-visual-thesis\", \"\") or \"\"\n        if tag == \"meta\" and values.get(\"name\", \"\").lower() == \"theme-color\":\n            self.theme_color = values.get(\"content\", \"\") or \"\"\n        locked_attrs = sorted(\n            (name, value or \"\")\n            for name, value in attrs\n            if name not in CONTENT_ATTRIBUTES\n        )\n        self.tokens.append(f\"\u003c{tag}{json.dumps(locked_attrs, separators=(',', ':'))}>\")\n\n    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:\n        self.handle_starttag(tag, attrs)\n        self.tokens.append(f\"\u003c/{tag}>\")\n\n    def handle_endtag(self, tag: str) -> None:\n        self.tokens.append(f\"\u003c/{tag}>\")\n\n\ndef extract_single(pattern: str, html: str, label: str) -> str:\n    matches = re.findall(pattern, html, flags=re.IGNORECASE | re.DOTALL)\n    if len(matches) != 1:\n        raise ValueError(f\"expected exactly one {label}, found {len(matches)}\")\n    return matches[0]\n\n\ndef observed_contract(html: str) -> dict[str, str]:\n    parser = StructureParser()\n… preview truncated",
      "related_capabilities": [],
      "archetypes": []
    },
    {
      "key": "tool:commit-policy",
      "id": "commit-policy",
      "name": "Commit Policy",
      "type": "tool",
      "path": "tools/commit_policy.py",
      "description": "Format and validate Agent Commons commit messages.",
      "purpose": "Format and validate Agent Commons commit messages.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Commit Policy",
        "commit-policy"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Format and validate Agent Commons commit messages.\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport re\nimport sys\n\n\nCONVENTIONAL_PREFIX = re.compile(\n    r\"^(?:feat|fix|docs|chore|refactor|test|style|perf|build|ci)(?:\\([^\\r\\n)]+\\))?\\s*:\",\n    re.IGNORECASE,\n)\nTICKET = re.compile(r\"(?\u003c![A-Z0-9])([A-Z][A-Z0-9]{1,19}-[1-9][0-9]*)(?![A-Z0-9])\")\nATTRIBUTION_TRAILER = re.compile(\n    r\"^(?:co-authored-by|generated-by|created-by|assisted-by)\\s*:\",\n    re.IGNORECASE | re.MULTILINE,\n)\nINTEGRATION_BRANCHES = {\"main\", \"master\", \"develop\", \"development\", \"trunk\"}\n\n\ndef ticket_from_branch(branch: str) -> str | None:\n    \"\"\"Return one conservative uppercase ticket identifier from a task branch.\"\"\"\n    normalized = branch.strip()\n    if not normalized or normalized.casefold() in INTEGRATION_BRANCHES:\n        return None\n    matches = list(dict.fromkeys(TICKET.findall(normalized)))\n    return matches[0] if len(matches) == 1 else None\n\n\ndef validate_message(message: str) -> list[str]:\n    \"\"\"Return policy errors for a complete commit message.\"\"\"\n    errors: list[str] = []\n    subject = message.splitlines()[0].strip() if message.splitlines() else \"\"\n    if not subject:\n        errors.append(\"commit subject must not be empty\")\n    elif CONVENTIONAL_PREFIX.match(subject):\n        errors.append(\"Conventional Commit type prefixes are prohibited\")\n    if ATTRIBUTION_TRAILER.search(message):\n        errors.append(\"co-author and agent-attribution trailers are prohibited\")\n    return errors\n\n\ndef compose_message(summary: str, branch: str = \"\") -> str:\n    \"\"\"Create a compliant subject, adding a reliable ticket prefix when available.\"\"\"\n    subject = summary.strip()\n    errors = validate_message(subject)\n    if errors:\n        raise ValueError(\"; \".join(errors))\n    ticket = ticket_from_branch(branch)\n    if ticket and not subject.startswith(f\"[{ticket}] \"):\n        subject = f\"[{ticket}] {subject}\"\n    return subject\n\n\ndef main() -> int:\n    parser = argparse.ArgumentParser(description=__doc__)\n    subparsers = parser.add_subparsers(dest=\"command\", required=True)\n    validate_parser = subparsers.add_parser(\"validate\")\n    validate_parser.add_argument(\"message\")\n    compose_parser = subparsers.add_parser(\"compose\")\n    compose_parser.add_argument(\"summary\")\n    compose_parser.add_argument(\"--branch\", default=\"\")\n    args = parser.parse_args()\n… preview truncated",
      "related_capabilities": [],
      "archetypes": []
    },
    {
      "key": "tool:coordinate-legacy-analysis",
      "id": "coordinate-legacy-analysis",
      "name": "Coordinate Legacy Analysis",
      "type": "tool",
      "path": "skills/analyze-legacy-system/scripts/coordinate_analysis.py",
      "description": "Plan, checkpoint, and validate complete inventory-backed legacy analysis.",
      "purpose": "Plan, checkpoint, and validate complete inventory-backed legacy analysis.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Coordinate Legacy Analysis",
        "coordinate-legacy-analysis"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Plan, checkpoint, and validate complete inventory-backed legacy analysis.\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport fnmatch\nimport hashlib\nimport json\nimport sys\nfrom collections import Counter\nfrom pathlib import Path, PurePosixPath\nfrom typing import Any\n\n\nREPOSITORY_ROOT = Path(__file__).resolve().parents[3]\nsys.path.insert(0, str(REPOSITORY_ROOT / \"tools\"))\nfrom plan_parallel_execution import PlanError, plan_execution  # noqa: E402\n\n\nFINAL_COVERAGE_STATUSES = {\n    \"ANALYZED\",\n    \"COVERED-BY-PARENT\",\n    \"NON-EXECUTABLE-SUPPORT\",\n    \"DUPLICATE-VARIANT\",\n    \"OUT-OF-SCOPE\",\n    \"SKIPPED-WITH-REASON\",\n    \"BLOCKED\",\n}\nACTIVE_COVERAGE_STATUSES = {\"PENDING\"}\nALL_COVERAGE_STATUSES = FINAL_COVERAGE_STATUSES | ACTIVE_COVERAGE_STATUSES\nREQUIRED_REASON_STATUSES = {\n    \"NON-EXECUTABLE-SUPPORT\",\n    \"DUPLICATE-VARIANT\",\n    \"OUT-OF-SCOPE\",\n    \"SKIPPED-WITH-REASON\",\n    \"BLOCKED\",\n}\nVALID_STAGE_STATUSES = {\"PENDING\", \"VALIDATED\", \"NOT-REQUIRED\", \"BLOCKED\"}\nSTAGE_ORDER = [\"synthesis\", \"requirements\", \"specifications\", \"dashboard\", \"coverage_validation\"]\nDEPTH_STATUSES = {\"PENDING\", \"DEEP_VERIFIED\", \"ANALYZED\", \"PARTIAL\", \"BLOCKED\", \"NOT_APPLICABLE\"}\nDIMENSION_STATUSES = {\"VERIFIED\", \"NOT_APPLICABLE\", \"BLOCKED\"}\nDEPTH_DIMENSIONS = {\n    \"structure\", \"behavior\", \"data\", \"dependencies\", \"business_rules\", \"interfaces\",\n    \"error_handling\", \"non_functional\", \"maintainability\", \"migration_significance\",\n}\nSEMANTIC_COUNT_FIELDS = {\n    \"flows\", \"business_rules\", \"data_structures\", \"dependencies\", \"interfaces\", \"defect_candidates\", \"unknowns\",\n}\nCROSS_LANGUAGE_CLASSIFICATIONS = {\n    \"EQUIVALENT\", \"PARTIALLY_EQUIVALENT\", \"DIVERGENT\", \"MISSING\", \"UNKNOWN\",\n}\n\n\nclass AnalysisStateError(ValueError):\n    \"\"\"The configured analysis state is invalid or incomplete.\"\"\"\n\n\ndef _load(path: Path) -> dict[str, Any]:\n    try:\n        payload = json.loads(path.read_text(encoding=\"utf-8\"))\n    except (OSError, json.JSONDecodeError) as exc:\n        raise AnalysisStateError(f\"cannot load {path}: {exc}\") from exc\n    if not isinstance(payload, dict):\n        raise AnalysisStateError(f\"{path} must contain a JSON object\")\n    return payload\n\n\ndef _write(path: Path | None, payload: dict[str, Any]) -> None:\n    text = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + \"\\n\"\n    if path:\n… preview truncated",
      "related_capabilities": [
        "archetype:legacy-migration",
        "skill:analyze-legacy-system"
      ],
      "archetypes": [
        "legacy-migration"
      ]
    },
    {
      "key": "tool:external-capabilities",
      "id": "external-capabilities",
      "name": "External Capabilities",
      "type": "tool",
      "path": "tools/external_capabilities.py",
      "description": "Discover and maintain metadata for untrusted external agent capabilities.",
      "purpose": "Discover and maintain metadata for untrusted external agent capabilities.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "External Capabilities",
        "external-capabilities"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Discover and maintain metadata for untrusted external agent capabilities.\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport hashlib\nimport json\nimport os\nimport re\nimport shutil\nimport subprocess\nimport sys\nimport threading\nimport time\nimport urllib.error\nimport urllib.parse\nimport urllib.request\nfrom datetime import datetime, timezone\nfrom pathlib import Path\nfrom functools import lru_cache\nfrom typing import Any\n\n\nROOT = Path(__file__).resolve().parent.parent\nSOURCES_PATH = ROOT / \"external\" / \"sources.yaml\"\nINDEX_PATH = ROOT / \"external\" / \"index\" / \"capabilities.json\"\nCATALOG_PATH = ROOT / \"catalog\" / \"capabilities.yaml\"\nTRUSTS = {\"OFFICIAL\", \"CURATED\", \"COMMUNITY\", \"UNTRUSTED\"}\nSOURCE_TYPES = {\"github-repository\", \"github-organization\", \"github-search\", \"registry\", \"website\", \"web-discovery\"}\nSTATUSES = {\"DISCOVERED\", \"REVIEWED\", \"REJECTED\", \"PROMOTION-CANDIDATE\", \"INCORPORATED\", \"SUPERSEDED\", \"STALE\"}\nREVIEW_STATUSES = {\"NOT_REVIEWED\", \"CURRENT\", \"OUTDATED\"}\nSECURITY_CLASSES = {\"INSTRUCTIONS ONLY\", \"INSTRUCTIONS + SCRIPTS\", \"PLUGIN WITH HOOKS\", \"MCP/REMOTE TOOLING\", \"UNKNOWN\"}\nRELATIONSHIPS = {\"COPIED\", \"ADAPTED\", \"INSPIRED-BY\", \"INDEPENDENT-REIMPLEMENTATION\"}\nREVIEW_FIELDS = {\n    \"schema_version\", \"id\", \"source_id\", \"repository\", \"path\", \"revision\", \"trust\", \"license\",\n    \"license_scope\", \"security_class\", \"relationship\", \"status\", \"reviewed_at\",\n}\nREVIEW_HEADINGS = {\n    \"## Provenance\", \"## License assessment\", \"## Security and supply-chain characteristics\",\n    \"## Semantic comparison with current commons\", \"## Useful novel patterns\",\n    \"## Rejected or non-canonical patterns\", \"## Promotion candidates\",\n    \"## Required evaluations before promotion\", \"## Final recommendation\",\n}\nTOKEN_RE = re.compile(r\"[a-z0-9][a-z0-9.+#-]*\")\nSTOPWORDS = {\n    \"a\", \"an\", \"and\", \"agent\", \"agents\", \"for\", \"from\", \"in\", \"of\", \"on\", \"or\", \"the\", \"to\",\n    \"tool\", \"tools\", \"workflow\", \"workflows\", \"skill\", \"skills\", \"code\", \"with\", \"this\", \"that\",\n}\nGENERIC_RELEVANCE_TERMS = {\n    \"agent\", \"agents\", \"code\", \"development\", \"java\", \"legacy\", \"migration\", \"modernization\",\n    \"software\", \"test\", \"testing\", \"tool\", \"tools\", \"workflow\", \"workflows\",\n}\nTECHNOLOGY_ANCHORS = {\"cobol\", \"pli\", \"sas\", \"java-21\", \"spring\", \"mainframe\", \"copybook\"}\nSAFE_EXTERNAL_QUERY_TERMS = GENERIC_RELEVANCE_TERMS | TECHNOLOGY_ANCHORS | {\n… preview truncated",
      "related_capabilities": [],
      "archetypes": []
    },
    {
      "key": "tool:extract-legacy-structure",
      "id": "extract-legacy-structure",
      "name": "Extract Legacy Structure",
      "type": "tool",
      "path": "skills/analyze-legacy-system/scripts/extract_legacy_structure.py",
      "description": "Conservatively extract source structure with exact coordinates and explicit unknowns.",
      "purpose": "Conservatively extract source structure with exact coordinates and explicit unknowns.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Extract Legacy Structure",
        "extract-legacy-structure"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Conservatively extract source structure with exact coordinates and explicit unknowns.\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport hashlib\nimport json\nimport re\nimport sys\nfrom pathlib import Path\n\n\nLANGUAGE_BY_SUFFIX = {\n    \".cbl\": \"cobol\", \".cob\": \"cobol\", \".cpy\": \"cobol\",\n    \".java\": \"java\",\n    \".sql\": \"sql\", \".ddl\": \"sql\",\n}\n\n\ndef mask_comments(text: str, language: str) -> str:\n    lines = text.splitlines()\n    if language == \"cobol\":\n        masked = []\n        for line in lines:\n            if len(line) > 6 and line[6:7] in {\"*\", \"/\"}:\n                masked.append(\" \" * len(line))\n            else:\n                marker = line.find(\"*>\")\n                masked.append(line if marker \u003c 0 else line[:marker] + \" \" * (len(line) - marker))\n        return \"\\n\".join(masked)\n\n    result = list(text)\n    in_block = False\n    i = 0\n    while i \u003c len(result):\n        if in_block:\n            if i + 1 \u003c len(result) and result[i] == \"*\" and result[i + 1] == \"/\":\n                result[i] = result[i + 1] = \" \"\n                in_block = False\n                i += 2\n            else:\n                if result[i] != \"\\n\":\n                    result[i] = \" \"\n                i += 1\n            continue\n        if i + 1 \u003c len(result) and result[i] == \"/\" and result[i + 1] == \"*\":\n            result[i] = result[i + 1] = \" \"\n            in_block = True\n            i += 2\n            continue\n        line_comment = (\n            language == \"java\" and i + 1 \u003c len(result) and result[i] == \"/\" and result[i + 1] == \"/\"\n        ) or (language == \"sql\" and i + 1 \u003c len(result) and result[i] == \"-\" and result[i + 1] == \"-\")\n        if line_comment:\n            while i \u003c len(result) and result[i] != \"\\n\":\n                result[i] = \" \"\n                i += 1\n            continue\n        i += 1\n    return \"\".join(result)\n\n\ndef coordinate(text: str, start: int) -> tuple[int, int, str]:\n    line = text.count(\"\\n\", 0, start) + 1\n    line_start = text.rfind(\"\\n\", 0, start) + 1\n    column = start - line_start + 1\n    evidence = text[line_start:text.find(\"\\n\", start) if \"\\n\" in text[start:] else len(text)].strip()\n    return line, column, evidence[:240]\n\n\ndef add_matches(records: list[dict], original: str, masked: str, kind: str, pattern: str, group: int = 1) -> None:\n… preview truncated",
      "related_capabilities": [
        "archetype:legacy-migration",
        "skill:analyze-legacy-system"
      ],
      "archetypes": [
        "legacy-migration"
      ]
    },
    {
      "key": "tool:inventory-codebase-tool",
      "id": "inventory-codebase-tool",
      "name": "Inventory Codebase Tool",
      "type": "tool",
      "path": "skills/inventory-codebase/scripts/inventory_codebase.py",
      "description": "Create a deterministic metadata inventory without interpreting behavior.",
      "purpose": "Create a deterministic metadata inventory without interpreting behavior.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Inventory Codebase Tool",
        "inventory-codebase-tool"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Create a deterministic metadata inventory without interpreting behavior.\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport hashlib\nimport json\nimport os\nfrom collections import Counter\nfrom datetime import datetime, timezone\nfrom pathlib import Path\n\nDEFAULT_PRUNE = {\n    \".git\", \".idea\", \".venv\", \"node_modules\", \"target\", \"build\", \"dist\", \"out\", \"vendor\",\n    \"__pycache__\", \".pytest_cache\", \".mypy_cache\", \".ruff_cache\", \".gradle\", \".next\",\n}\nSECRET_NAMES = {\".env\", \".npmrc\", \".pypirc\", \"credentials\", \"credentials.json\", \"id_rsa\", \"id_ed25519\"}\nSECRET_SUFFIXES = {\".key\", \".pem\", \".p12\", \".pfx\", \".jks\", \".keystore\"}\nLANGUAGE = {\n    \".cbl\": \"cobol\", \".cob\": \"cobol\", \".cpy\": \"copybook\", \".pli\": \"pli\", \".pl1\": \"pli\",\n    \".inc\": \"pli-include\", \".csd\": \"cics-csd\",\n    \".java\": \"java\", \".kt\": \"kotlin\", \".cs\": \"csharp\", \".vb\": \"vb\", \".py\": \"python\",\n    \".js\": \"javascript\", \".jsx\": \"javascript\", \".ts\": \"typescript\", \".tsx\": \"typescript\",\n    \".sql\": \"sql\", \".xml\": \"xml\", \".xsd\": \"xsd\", \".wsdl\": \"wsdl\", \".json\": \"json\",\n    \".yaml\": \"yaml\", \".yml\": \"yaml\", \".md\": \"markdown\", \".html\": \"html\", \".css\": \"css\",\n    \".sh\": \"shell\", \".ps1\": \"powershell\", \".tf\": \"terraform\", \".sas\": \"sas\", \".php\": \"php\",\n    \".gradle\": \"groovy\",\n}\n\n\ndef classify(path: Path) -> tuple[str, str]:\n    name = path.name.lower()\n    suffix = path.suffix.lower()\n    language = LANGUAGE.get(suffix, \"unknown\")\n    if name in {\"pom.xml\", \"build.gradle\", \"build.gradle.kts\", \"package.json\", \"pyproject.toml\", \"requirements.txt\"}:\n        return \"build-descriptor\", language\n    if suffix in {\".jar\", \".war\", \".dll\", \".exe\", \".class\", \".so\", \".dylib\"}:\n        return \"binary\", language\n    if suffix in {\".zip\", \".tar\", \".gz\", \".7z\", \".rar\"}:\n        return \"archive\", language\n    if suffix in {\".yaml\", \".yml\", \".json\", \".properties\", \".ini\", \".toml\", \".conf\"}:\n        return \"configuration\", language\n    if any(part.lower() in {\"test\", \"tests\", \"spec\", \"specs\", \"fixtures\"} for part in path.parts):\n        return \"test\", language\n    if language != \"unknown\":\n        return \"source\", language\n    return \"other\", language\n\n\ndef digest_file(path: Path) -> str:\n    digest = hashlib.sha256()\n    with path.open(\"rb\") as handle:\n        for chunk in iter(lambda: handle.read(1024 * 1024), b\"\"):\n            digest.update(chunk)\n    return digest.hexdigest()\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "skill:inventory-codebase"
      ],
      "archetypes": [
        "development",
        "legacy-migration"
      ]
    },
    {
      "key": "tool:manage-project-memory",
      "id": "manage-project-memory",
      "name": "Manage Project Memory",
      "type": "tool",
      "path": "skills/maintain-project-memory/scripts/manage_project_memory.py",
      "description": "Manage hierarchical evidence-backed Agent Commons project memory.",
      "purpose": "Manage hierarchical evidence-backed Agent Commons project memory.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Manage Project Memory",
        "manage-project-memory"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Manage hierarchical evidence-backed Agent Commons project memory.\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport hashlib\nimport json\nimport os\nimport re\nimport sys\nfrom contextlib import contextmanager\nfrom pathlib import Path, PurePosixPath\nfrom typing import Any, Iterator\n\n\nMEMORY_ROOT = PurePosixPath(\".agent-commons/memory\")\nCONFIDENCE = {\"VERIFIED\", \"INFERRED\", \"UNKNOWN\", \"STALE\", \"CONFLICTING\"}\nLAYERS = {\"L1\", \"L2\"}\nPROJECT_FIELDS = (\n    \"goal\", \"mode\", \"source_roots\", \"protected_paths\", \"target_technology\", \"languages\",\n    \"architecture\", \"lifecycle_stage\", \"major_decisions\", \"critical_blockers\", \"next_action\",\n)\n\n\nclass ProjectMemoryError(ValueError):\n    \"\"\"Raised when project memory is invalid or cannot be updated safely.\"\"\"\n\n\ndef _memory_dir(root: Path) -> Path:\n    return root.expanduser().resolve() / MEMORY_ROOT\n\n\ndef _canonical_json(value: object) -> str:\n    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(\",\", \":\"))\n\n\ndef _fingerprint(value: object) -> str:\n    return hashlib.sha256(_canonical_json(value).encode(\"utf-8\")).hexdigest()\n\n\ndef _file_hash(path: Path) -> str:\n    digest = hashlib.sha256()\n    with path.open(\"rb\") as handle:\n        for block in iter(lambda: handle.read(1024 * 1024), b\"\"):\n            digest.update(block)\n    return digest.hexdigest()\n\n\ndef _atomic_text(path: Path, text: str) -> None:\n    path.parent.mkdir(parents=True, exist_ok=True)\n    temporary = path.with_name(path.name + \".tmp\")\n    temporary.write_text(text, encoding=\"utf-8\")\n    os.replace(temporary, path)\n\n\ndef _atomic_json(path: Path, value: object) -> None:\n    _atomic_text(path, json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + \"\\n\")\n\n\ndef _load_json(path: Path) -> dict[str, Any]:\n    try:\n        value = json.loads(path.read_text(encoding=\"utf-8\"))\n    except (OSError, json.JSONDecodeError) as exc:\n        raise ProjectMemoryError(f\"cannot load project memory file {path}: {exc}\") from exc\n    if not isinstance(value, dict):\n        raise ProjectMemoryError(f\"project memory file must contain an object: {path}\")\n    return value\n\n\ndef _slug(value: object, context: str) -> str:\n    if not isinstance(value, str) or not value.strip():\n        raise ProjectMemoryError(f\"{context} must be a non-empty string\")\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "overlay:durable-state",
        "skill:maintain-project-memory"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "tool:plan-parallel-execution",
      "id": "plan-parallel-execution",
      "name": "Plan Parallel Execution",
      "type": "tool",
      "path": "tools/plan_parallel_execution.py",
      "description": "Build deterministic dependency stages without overlapping mutable ownership.",
      "purpose": "Build deterministic dependency stages without overlapping mutable ownership.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Plan Parallel Execution",
        "plan-parallel-execution"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Build deterministic dependency stages without overlapping mutable ownership.\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport sys\nfrom pathlib import PurePosixPath\nfrom typing import Any\n\n\nclass PlanError(ValueError):\n    \"\"\"The execution plan is invalid or cannot be scheduled safely.\"\"\"\n\n\ndef _require_text(value: object, context: str) -> str:\n    if not isinstance(value, str) or not value.strip():\n        raise PlanError(f\"{context} must be a non-empty string\")\n    return value.strip()\n\n\ndef _text_list(value: object, context: str) -> list[str]:\n    if value is None:\n        return []\n    if not isinstance(value, list):\n        raise PlanError(f\"{context} must be an array\")\n    result: list[str] = []\n    for index, item in enumerate(value):\n        text = _require_text(item, f\"{context}[{index}]\")\n        if text not in result:\n            result.append(text)\n    return sorted(result)\n\n\ndef _owned_path(value: str, context: str) -> str:\n    portable = value.replace(\"\\\\\", \"/\").rstrip(\"/\")\n    if not portable or portable == \".\":\n        raise PlanError(f\"{context} must identify a concrete relative path\")\n    if portable.startswith(\"/\") or any(character in portable for character in \"*?[]\"):\n        raise PlanError(f\"{context} must be an exact relative path without globs\")\n    parts = PurePosixPath(portable).parts\n    if any(part in {\"\", \".\", \"..\"} for part in parts):\n        raise PlanError(f\"{context} must not contain empty, current, or parent segments\")\n    return PurePosixPath(*parts).as_posix()\n\n\ndef _paths_overlap(left: str, right: str) -> bool:\n    left_parts = PurePosixPath(left).parts\n    right_parts = PurePosixPath(right).parts\n    common = min(len(left_parts), len(right_parts))\n    return left_parts[:common] == right_parts[:common]\n\n\ndef _pair_conflicts(left: dict[str, Any], right: dict[str, Any]) -> list[dict[str, str]]:\n    conflicts: list[dict[str, str]] = []\n    for left_path in left[\"write_paths\"]:\n        for right_path in right[\"write_paths\"]:\n            if _paths_overlap(left_path, right_path):\n                conflicts.append(\n                    {\"kind\": \"write_path\", \"left\": left_path, \"right\": right_path}\n                )\n    for surface in sorted(set(left[\"shared_surfaces\"]) & set(right[\"shared_surfaces\"])):\n        conflicts.append({\"kind\": \"shared_surface\", \"value\": surface})\n… preview truncated",
      "related_capabilities": [],
      "archetypes": []
    },
    {
      "key": "tool:project-runtime-manager",
      "id": "project-runtime-manager",
      "name": "Project Runtime Manager",
      "type": "tool",
      "path": "tools/project_runtimes.py",
      "description": "Inspect, verify, or remove thin runtime adapters and canonical project capability references.",
      "purpose": "Inspect, verify, or remove thin runtime adapters and canonical project capability references.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Project Runtime Manager",
        "project-runtime-manager"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Inspect, verify, or remove thin runtime adapters and canonical project capability references.\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport os\nimport re\nimport sys\nimport tempfile\nfrom pathlib import Path\n\nfrom runtime_adapters import AdapterError, RUNTIMES, capability_path, render_claude_project_adapter\n\n\nclass ProjectRuntimeError(RuntimeError):\n    \"\"\"Project runtime state cannot be changed safely.\"\"\"\n\n\ndef atomic_write(path: Path, content: str) -> None:\n    descriptor, temporary = tempfile.mkstemp(prefix=f\".{path.name}.\", dir=path.parent)\n    try:\n        with os.fdopen(descriptor, \"w\", encoding=\"utf-8\") as handle:\n            handle.write(content)\n        os.replace(temporary, path)\n    finally:\n        if os.path.exists(temporary):\n            os.unlink(temporary)\n\n\ndef runtime_block(text: str) -> tuple[list[str], int, int, list[str]]:\n    lines = text.splitlines()\n    try:\n        start = lines.index(\"  runtimes:\")\n    except ValueError as exc:\n        raise ProjectRuntimeError(\".agent-commons.yaml has no project.runtimes block\") from exc\n    end = start + 1\n    values: list[str] = []\n    while end \u003c len(lines) and lines[end].startswith(\"    - \"):\n        values.append(lines[end][6:].strip().strip('\"'))\n        end += 1\n    if not values:\n        raise ProjectRuntimeError(\"project.runtimes must contain at least one runtime\")\n    return lines, start, end, values\n\n\ndef manifest_list(text: str, section_name: str, key: str) -> list[str]:\n    section = re.search(\n        rf\"(?m)^{re.escape(section_name)}:\\s*$\\n(?P\u003cbody>(?:^  .*\\n?)*)\",\n        text,\n    )\n    if not section:\n        raise ProjectRuntimeError(f\".agent-commons.yaml has no {section_name} block\")\n    body = section.group(\"body\")\n    if re.search(rf\"(?m)^  {re.escape(key)}:\\s*\\[\\]\\s*$\", body):\n        return []\n    values = re.search(\n        rf\"(?m)^  {re.escape(key)}:\\s*$\\n(?P\u003cbody>(?:^    -\\s+.*\\n?)*)\",\n        body,\n    )\n    if not values:\n        raise ProjectRuntimeError(f\".agent-commons.yaml has no {section_name}.{key} list\")\n    return [\n        value.strip().strip(\"'\\\"\")\n        for value in re.findall(r\"(?m)^    -\\s+(.*?)\\s*$\", values.group(\"body\"))\n    ]\n\n\ndef read_skill_references(text: str) -> list[str]:\n    return manifest_list(text, \"commons\", \"skills\")\n\n\ndef manifest_path(root: Path) -> Path:\n    path = root / \".agent-commons.yaml\"\n… preview truncated",
      "related_capabilities": [],
      "archetypes": []
    },
    {
      "key": "tool:rank-ready-slices",
      "id": "rank-ready-slices",
      "name": "Rank Ready Slices",
      "type": "tool",
      "path": "skills/implement-ready-slice/scripts/rank_slices.py",
      "description": "Rank dependency-ready implementation candidates deterministically.",
      "purpose": "Rank dependency-ready implementation candidates deterministically.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Rank Ready Slices",
        "rank-ready-slices"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Rank dependency-ready implementation candidates deterministically.\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nfrom pathlib import Path\n\nPRIORITY = {\"must\": 0, \"should\": 1, \"could\": 2, \"wont\": 9}\nCONFIDENCE = {\"high\": 0, \"medium\": 1, \"low\": 2, \"unknown\": 3}\n\n\ndef main() -> int:\n    parser = argparse.ArgumentParser(description=__doc__)\n    parser.add_argument(\"queue\", type=Path)\n    parser.add_argument(\"--top\", type=int, default=10)\n    args = parser.parse_args()\n    raw = json.loads(args.queue.read_text(encoding=\"utf-8\"))\n    items = raw[\"items\"] if isinstance(raw, dict) else raw\n    if not isinstance(items, list):\n        parser.error(\"queue must be an array or an object with an items array\")\n    by_id = {}\n    for item in items:\n        identifier = str(item.get(\"id\", \"\")).strip()\n        if not identifier or identifier in by_id:\n            parser.error(f\"missing or duplicate id: {identifier!r}\")\n        by_id[identifier] = item\n    done = {identifier for identifier, item in by_id.items() if str(item.get(\"status\", \"\")).lower() == \"done\"}\n    ranked = []\n    skipped = []\n    for identifier, item in by_id.items():\n        status = str(item.get(\"status\", \"planned\")).lower()\n        dependencies = [str(value) for value in item.get(\"dependencies\", [])]\n        reasons = []\n        if status in {\"done\", \"blocked\", \"in_progress\"}: reasons.append(status)\n        if item.get(\"active_claim\"): reasons.append(\"actively claimed\")\n        if item.get(\"decision_blocked\"): reasons.append(\"decision blocked\")\n        if item.get(\"externally_owned\"): reasons.append(\"externally owned\")\n        unresolved = [dep for dep in dependencies if dep not in done]\n        if unresolved: reasons.append(\"unresolved dependencies: \" + \", \".join(unresolved))\n        priority = str(item.get(\"priority\", \"should\")).lower()\n        if priority == \"wont\": reasons.append(\"priority wont\")\n        if reasons:\n            skipped.append({\"id\": identifier, \"reasons\": reasons})\n            continue\n        criteria = item.get(\"acceptance_criteria\", [])\n        criteria_count = criteria if isinstance(criteria, int) else len(criteria)\n        score = [PRIORITY.get(priority, 5), int(item.get(\"risk\", 5)), criteria_count,\n                 CONFIDENCE.get(str(item.get(\"evidence_confidence\", \"unknown\")).lower(), 3), identifier]\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "skill:implement-ready-slice"
      ],
      "archetypes": [
        "development"
      ]
    },
    {
      "key": "tool:refresh-commons-presentation",
      "id": "refresh-commons-presentation",
      "name": "Refresh Commons Presentation",
      "type": "tool",
      "path": "tools/refresh_commons_presentation.py",
      "description": "Refresh generated Agent Commons presentation facts from canonical repository state.",
      "purpose": "Refresh generated Agent Commons presentation facts from canonical repository state.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Refresh Commons Presentation",
        "refresh-commons-presentation"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Refresh generated Agent Commons presentation facts from canonical repository state.\"\"\"\n\nfrom __future__ import annotations\n\nfrom sync_presentation import main\n\n\nif __name__ == \"__main__\":\n    raise SystemExit(main())",
      "related_capabilities": [],
      "archetypes": []
    },
    {
      "key": "tool:resolve-archetypes",
      "id": "resolve-archetypes",
      "name": "Resolve Archetypes",
      "type": "tool",
      "path": "tools/resolve_archetypes.py",
      "description": "Validate and resolve Agent Commons archetype composition without external dependencies.",
      "purpose": "Validate and resolve Agent Commons archetype composition without external dependencies.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Resolve Archetypes",
        "resolve-archetypes"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Validate and resolve Agent Commons archetype composition without external dependencies.\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport sys\nfrom collections import OrderedDict\nfrom functools import lru_cache\nfrom pathlib import Path\nfrom typing import Any\n\n\nROOT = Path(__file__).resolve().parent.parent\nCONTRACT_PATH = ROOT / \"archetypes\" / \"composition.yaml\"\nCAPABILITY_CATALOG_PATH = ROOT / \"catalog\" / \"capabilities.yaml\"\n\n\nclass CompositionError(ValueError):\n    \"\"\"The composition contract or requested selection is invalid.\"\"\"\n\n\n@lru_cache(maxsize=None)\ndef load_json_yaml(path: Path) -> dict[str, Any]:\n    try:\n        value = json.loads(path.read_text(encoding=\"utf-8\"))\n    except (OSError, json.JSONDecodeError) as exc:\n        label = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path\n        raise CompositionError(f\"invalid JSON-compatible YAML {label}: {exc}\") from exc\n    if not isinstance(value, dict):\n        raise CompositionError(f\"manifest must be an object: {path.relative_to(ROOT)}\")\n    return value\n\n\n@lru_cache(maxsize=1)\ndef load_contract() -> dict[str, Any]:\n    return load_json_yaml(CONTRACT_PATH)\n\n\n@lru_cache(maxsize=1)\ndef load_capability_catalog() -> dict[str, Any]:\n    return load_json_yaml(CAPABILITY_CATALOG_PATH)\n\n\ndef split_values(values: list[str] | None) -> list[str]:\n    result: list[str] = []\n    for value in values or []:\n        for item in value.split(\",\"):\n            item = item.strip()\n            if item and item not in result:\n                result.append(item)\n    return result\n\n\ndef registry_aliases(contract: dict[str, Any]) -> dict[str, str]:\n    aliases: dict[str, str] = {}\n    for identifier, entry in contract.get(\"archetypes\", {}).items():\n        aliases[identifier] = identifier\n        for alias in entry.get(\"aliases\", []):\n            if alias in aliases and aliases[alias] != identifier:\n                raise CompositionError(f\"duplicate archetype alias: {alias}\")\n            aliases[alias] = identifier\n    return aliases\n\n\ndef manifest_path(entry: dict[str, Any]) -> Path:\n    return ROOT / \"archetypes\" / entry[\"path\"]\n\n\n@lru_cache(maxsize=1)\ndef _load_manifests_cached() -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:\n    contract = load_contract()\n    groups: list[dict[str, dict[str, Any]]] = []\n… preview truncated",
      "related_capabilities": [],
      "archetypes": []
    },
    {
      "key": "tool:resolve-capability-gaps",
      "id": "resolve-capability-gaps",
      "name": "Resolve Capability Gaps",
      "type": "tool",
      "path": "tools/resolve_capability_gaps.py",
      "description": "Resolve project capability requirements against the actual Agent Commons catalog.",
      "purpose": "Resolve project capability requirements against the actual Agent Commons catalog.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Resolve Capability Gaps",
        "resolve-capability-gaps"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Resolve project capability requirements against the actual Agent Commons catalog.\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport re\nimport sys\nfrom pathlib import Path\nfrom typing import Any\n\nfrom resolve_archetypes import (\n    CompositionError,\n    load_capability_catalog,\n    load_contract,\n    load_manifests,\n    resolve_composition,\n    split_values,\n)\n\n\nROOT = Path(__file__).resolve().parent.parent\nSTATUSES = {\"COVERED\", \"PARTIALLY_COVERED\", \"MISSING\", \"OPTIONAL_GAP\"}\nIMPORTANCE_ORDER = (\"required\", \"strongly_recommended\", \"optional\")\nIMPORTANCE_LEVELS = set(IMPORTANCE_ORDER)\nMATERIAL_STATUSES = {\"PARTIALLY_COVERED\", \"MISSING\"}\n\n\nclass CapabilityGapError(ValueError):\n    \"\"\"The capability expectation contract or requested assessment is invalid.\"\"\"\n\n\ndef slug(value: str) -> str:\n    normalized = value.strip().lower()\n    normalized = normalized.replace(\"pl/i\", \"pli\").replace(\"c#\", \"csharp\").replace(\"c++\", \"cpp\")\n    normalized = re.sub(r\"[^a-z0-9]+\", \"-\", normalized).strip(\"-\")\n    return normalized\n\n\ndef catalog_providers(catalog: dict[str, Any]) -> dict[str, list[str]]:\n    providers: dict[str, list[str]] = {}\n    for kind in catalog.get(\"capability_kinds\", []):\n        entries = catalog.get(kind, {})\n        if not isinstance(entries, dict):\n            continue\n        for identifier, metadata in entries.items():\n            if not isinstance(metadata, dict):\n                continue\n            for semantic_id in metadata.get(\"provides\", []):\n                if isinstance(semantic_id, str) and semantic_id:\n                    providers.setdefault(semantic_id, []).append(f\"{kind}:{identifier}\")\n    return providers\n\n\ndef selected_providers(composition: dict[str, Any], catalog: dict[str, Any]) -> dict[str, list[str]]:\n    providers: dict[str, list[str]] = {}\n    capabilities = composition.get(\"capabilities\", {})\n    for kind in catalog.get(\"capability_kinds\", []):\n        entries = catalog.get(kind, {})\n        selected = capabilities.get(kind, []) if isinstance(capabilities, dict) else []\n        for identifier in selected:\n            metadata = entries.get(identifier, {}) if isinstance(entries, dict) else {}\n            for semantic_id in metadata.get(\"provides\", []) if isinstance(metadata, dict) else []:\n                providers.setdefault(semantic_id, []).append(f\"{kind}:{identifier}\")\n… preview truncated",
      "related_capabilities": [],
      "archetypes": []
    },
    {
      "key": "tool:resolve-project-continuation",
      "id": "resolve-project-continuation",
      "name": "Resolve Project Continuation",
      "type": "tool",
      "path": "skills/continue-project/scripts/resolve_project_continuation.py",
      "description": "Resolve the next Agent Commons lifecycle action from canonical project state.",
      "purpose": "Resolve the next Agent Commons lifecycle action from canonical project state.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Resolve Project Continuation",
        "resolve-project-continuation"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Resolve the next Agent Commons lifecycle action from canonical project state.\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport re\nfrom pathlib import Path\nfrom typing import Any\n\n\nCOLLECTIONS = {\n    \"requirement\": \"requirements\",\n    \"specification\": \"specifications\",\n    \"acceptance-criterion\": \"acceptance_criteria\",\n    \"implementation-item\": \"implementation_items\",\n    \"test\": \"tests\",\n    \"evidence\": \"evidence\",\n}\nTERMINAL_IMPLEMENTATION = {\"implemented\", \"validated\", \"complete\", \"completed\"}\nPASS_VALIDATION = {\"pass\", \"passed\", \"validated\", \"complete\", \"completed\"}\nREADY = {\"ready\", \"approved\", \"implementation-ready\", \"ready-for-implementation\"}\n\n\nclass ContinuationError(ValueError):\n    \"\"\"Raised when canonical project state cannot be resolved safely.\"\"\"\n\n\ndef _norm(value: object) -> str:\n    return str(value or \"\").strip().lower().replace(\"_\", \"-\")\n\n\ndef action(\n    capability: str | None,\n    *,\n    subject: str | None = None,\n    label: str,\n    reason: str,\n    required: bool = True,\n    status: str = \"ready\",\n    choices: list[dict[str, str]] | None = None,\n) -> dict[str, Any]:\n    result: dict[str, Any] = {\n        \"status\": status,\n        \"required\": required,\n        \"capability\": capability,\n        \"subject\": subject,\n        \"label\": label,\n        \"reason\": reason,\n    }\n    result[\"command\"] = f\"${capability}{f' {subject}' if subject else ''}\" if capability else None\n    if choices:\n        result[\"choices\"] = choices\n    return result\n\n\ndef describe_capability_resolution(\n    manifest: dict[str, Any],\n    next_action: dict[str, Any],\n) -> dict[str, Any]:\n    \"\"\"Describe how a returned stable capability ID must be resolved by the runtime.\"\"\"\n    stable_id = next_action.get(\"capability\")\n    configured = manifest.get(\"selected_skills\", [])\n    selected_skills = configured if isinstance(configured, list) else []\n    return {\n        \"stable_id\": stable_id,\n        \"selected_in_manifest\": stable_id in selected_skills if stable_id else None,\n        \"source\": \"canonical-agent-commons\" if stable_id else None,\n        \"automatic_execution\": False,\n    }\n\n\ndef _manifest_section(text: str, name: str) -> str:\n    match = re.search(rf\"(?m)^{re.escape(name)}:\\s*$\\n(?P\u003cbody>(?:^  .*\\n?)*)\", text)\n    return match.group(\"body\") if match else \"\"\n\n\ndef _scalar(section: str, key: str) -> str:\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "skill:continue-project"
      ],
      "archetypes": [
        "development",
        "legacy-migration"
      ]
    },
    {
      "key": "tool:run-evaluations",
      "id": "run-evaluations",
      "name": "Run Evaluations",
      "type": "tool",
      "path": "tools/evals/run_evals.py",
      "description": "Run Agent Commons contract, capability, integration, and workflow evaluations.",
      "purpose": "Run Agent Commons contract, capability, integration, and workflow evaluations.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Run Evaluations",
        "run-evaluations"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Run Agent Commons contract, capability, integration, and workflow evaluations.\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport html\nimport hashlib\nimport json\nimport os\nimport posixpath\nimport re\nimport shlex\nimport shutil\nimport stat\nimport statistics\nimport subprocess\nimport sys\nimport tempfile\nimport time\nimport xml.etree.ElementTree as ET\nfrom datetime import datetime, timezone\nfrom pathlib import Path\nfrom typing import Any, Optional\n\nfrom eval_common import (\n    ROOT,\n    EvalConfigError,\n    load_capability_contracts,\n    load_hard_fail_assertions,\n    load_json,\n    load_thresholds,\n    load_workflows,\n    resolve_reference,\n    stable_unique,\n    validate_against_schema,\n    validate_configuration,\n)\nfrom select_impacted_evals import git_changed_files, select_impacted\nfrom semantic_provider import (\n    AuthenticationError,\n    ProviderError,\n    provider_from_environment,\n)\nfrom semantic_runtime import RuntimeConfigError, runtime_from_environment\n\n\nPASS = \"PASS\"\nWARNING = \"WARNING\"\nREGRESSION_FAIL = \"REGRESSION_FAIL\"\nHARD_FAIL = \"HARD_FAIL\"\n\nQUALITY_REGRESSION = \"QUALITY_REGRESSION\"\nDETERMINISTIC_FAILURE = \"DETERMINISTIC_FAILURE\"\nINFRASTRUCTURE_FAILURE = \"INFRASTRUCTURE_FAILURE\"\nPROTOCOL_FAILURE = \"PROTOCOL_FAILURE\"\n\nPERFORMANCE_METRICS = (\n    \"llm_calls\",\n    \"input_tokens\",\n    \"output_tokens\",\n    \"subagents_launched\",\n    \"context_compactions\",\n    \"source_files_read\",\n    \"duplicate_source_reads\",\n    \"dashboard_renders\",\n    \"external_searches\",\n    \"executor_duration_seconds\",\n    \"judge_duration_seconds\",\n    \"judge_input_tokens\",\n    \"judge_output_tokens\",\n    \"judge_total_tokens\",\n    \"executor_attempts\",\n    \"judge_attempts\",\n)\n\nPROFILE_ALIASES = {\n    \"smoke\": \"fast\",\n    \"pr\": \"fast\",\n    \"nightly\": \"full\",\n    \"weekly\": \"deep\",\n}\nEVAL_PROFILES = (\"fast\", \"standard\", \"full\", \"deep\", *PROFILE_ALIASES)\nRETRYABLE_INFRASTRUCTURE_MARKERS = (\n    \"429\",\n    \"rate limit\",\n    \"temporarily unavailable\",\n    \"connection reset\",\n    \"connection timed out\",\n    \"service unavailable\",\n)\n\nDEFAULT_EXECUTOR_COMMAND = shlex.join([\n    sys.executable, str(ROOT / \"tools\" / \"evals\" / \"semantic_executor.py\"),\n])\nDEFAULT_JUDGE_COMMAND = shlex.join([\n    sys.executable, str(ROOT / \"tools\" / \"evals\" / \"semantic_judge.py\"),\n])\n\n\ndef semantic_configuration(output_dir: Optional[Path] = None) -> dict[str, Any]:\n… preview truncated",
      "related_capabilities": [],
      "archetypes": []
    },
    {
      "key": "tool:run-external-discovery",
      "id": "run-external-discovery",
      "name": "Run External Discovery",
      "type": "tool",
      "path": "tools/run_external_discovery.py",
      "description": "Run external capability discovery independently and persist compact project state.",
      "purpose": "Run external capability discovery independently and persist compact project state.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Run External Discovery",
        "run-external-discovery"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Run external capability discovery independently and persist compact project state.\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport os\nimport sys\nimport tempfile\nimport time\nfrom pathlib import Path\n\nimport external_capabilities\n\n\nROOT = Path(__file__).resolve().parent.parent\n\n\ndef atomic_json(path: Path, value: dict[str, object]) -> None:\n    path.parent.mkdir(parents=True, exist_ok=True)\n    descriptor, temporary = tempfile.mkstemp(prefix=f\".{path.name}.\", dir=path.parent)\n    try:\n        with os.fdopen(descriptor, \"w\", encoding=\"utf-8\") as handle:\n            json.dump(value, handle, indent=2, ensure_ascii=False)\n            handle.write(\"\\n\")\n        os.replace(temporary, path)\n    finally:\n        if os.path.exists(temporary):\n            os.unlink(temporary)\n\n\ndef source_policy(scope: str) -> tuple[list[str], bool]:\n    if scope == \"official\":\n        return [\"OFFICIAL\"], False\n    if scope == \"official-curated\":\n        return [\"OFFICIAL\", \"CURATED\"], False\n    return [], scope == \"all\"\n\n\ndef run(args: argparse.Namespace) -> int:\n    delay = float(os.environ.get(\"AGENT_COMMONS_EXTERNAL_DISCOVERY_DELAY_SECONDS\", \"0\") or 0)\n    if delay > 0:\n        time.sleep(delay)\n    trust, include_community = source_policy(args.source_scope)\n    request_key = external_capabilities.discovery_request_key(\n        args.topic, args.source_scope, args.sources, args.snapshot,\n    )\n    lease_path = args.lock or args.project_root / \".agent-commons\" / \"external-discovery.lock\"\n    lease = external_capabilities.DiscoveryLease(lease_path, request_key, args.lease_stale_seconds)\n    if not lease.acquire():\n        failure = external_capabilities._structured_failure(\"local\", \"external-discovery\", \"lock-contention\")\n        try:\n            existing = json.loads(args.state.read_text(encoding=\"utf-8\")) if args.state.is_file() else {}\n        except (OSError, json.JSONDecodeError):\n            existing = {}\n        if not existing or existing.get(\"request_key\") == request_key:\n            atomic_json(args.state, {\n                \"schema_version\": 2,\n                \"status\": \"failed\",\n                \"completed_at\": external_capabilities.utc_now(),\n                \"request_key\": request_key,\n                \"gaps\": args.gap,\n                \"candidate_count\": 0,\n                \"failures\": [failure],\n… preview truncated",
      "related_capabilities": [],
      "archetypes": []
    },
    {
      "key": "tool:runtime-adapters",
      "id": "runtime-adapters",
      "name": "Runtime Adapters",
      "type": "tool",
      "path": "tools/runtime_adapters.py",
      "description": "Render and validate thin runtime adapters from canonical Agent Commons capabilities.",
      "purpose": "Render and validate thin runtime adapters from canonical Agent Commons capabilities.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Runtime Adapters",
        "runtime-adapters"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Render and validate thin runtime adapters from canonical Agent Commons capabilities.\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport sys\nfrom functools import lru_cache\nfrom pathlib import Path, PurePath\nfrom typing import Any\n\nROOT = Path(__file__).resolve().parent.parent\nsys.path.insert(0, str(ROOT / \"install\"))\nfrom skill_catalog import SkillCatalogError, canonical_skill_map, validate_skill\n\n\nCATALOG_PATH = ROOT / \"catalog\" / \"capabilities.yaml\"\nCODEX_INTERFACES_PATH = ROOT / \"adapters\" / \"codex\" / \"skill-interfaces.yaml\"\nRUNTIMES = (\"codex\", \"claude-code\", \"cline\", \"opencode\")\n\n\nclass AdapterError(ValueError):\n    \"\"\"The canonical capability or runtime mapping is invalid.\"\"\"\n\n\ndef load_json_yaml(path: Path) -> dict[str, Any]:\n    try:\n        value = json.loads(path.read_text(encoding=\"utf-8\"))\n    except (OSError, json.JSONDecodeError) as exc:\n        raise AdapterError(f\"invalid JSON-compatible YAML {path}: {exc}\") from exc\n    if not isinstance(value, dict):\n        raise AdapterError(f\"expected object in {path}\")\n    return value\n\n\n@lru_cache(maxsize=None)\ndef load_catalog(library: Path = ROOT) -> dict[str, Any]:\n    return load_json_yaml(library / \"catalog\" / \"capabilities.yaml\")\n\n\n@lru_cache(maxsize=None)\ndef adapter_manifest(runtime: str) -> dict[str, Any]:\n    if runtime not in RUNTIMES:\n        raise AdapterError(f\"unsupported runtime: {runtime}\")\n    return load_json_yaml(ROOT / \"adapters\" / runtime / \"adapter.yaml\")\n\n\n@lru_cache(maxsize=None)\ndef runtime_user_path_parts(runtime: str, destination: str) -> tuple[str, ...]:\n    \"\"\"Return a runtime user destination as platform-neutral path components.\"\"\"\n    manifest = adapter_manifest(runtime)\n    paths = manifest.get(\"user_paths\")\n    if not isinstance(paths, dict):\n        raise AdapterError(f\"adapter lacks user_paths: {runtime}\")\n    value = paths.get(destination)\n    if not isinstance(value, list) or not value or not all(isinstance(part, str) and part for part in value):\n        raise AdapterError(f\"adapter lacks user path {destination!r}: {runtime}\")\n    return tuple(value)\n\n\ndef runtime_user_path(home: PurePath, runtime: str, destination: str) -> PurePath:\n    return home.joinpath(*runtime_user_path_parts(runtime, destination))\n\n\ndef capability_entry(kind: str, identifier: str, library: Path = ROOT) -> dict[str, Any]:\n… preview truncated",
      "related_capabilities": [],
      "archetypes": []
    },
    {
      "key": "tool:select-impacted-evaluations",
      "id": "select-impacted-evaluations",
      "name": "Select Impacted Evaluations",
      "type": "tool",
      "path": "tools/evals/select_impacted_evals.py",
      "description": "Select capability and workflow evaluations affected by repository changes.",
      "purpose": "Select capability and workflow evaluations affected by repository changes.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Select Impacted Evaluations",
        "select-impacted-evaluations"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Select capability and workflow evaluations affected by repository changes.\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport subprocess\nimport sys\nfrom collections import deque\nfrom pathlib import Path\nfrom typing import Any, Optional\n\nfrom eval_common import (\n    ROOT,\n    EvalConfigError,\n    capability_for_path,\n    catalog_entries,\n    impact_graph,\n    load_capability_contracts,\n    load_catalog,\n    load_thresholds,\n    load_workflows,\n    normalize_repo_path,\n    scenario_ids,\n)\n\n\nGLOBAL_GRAPH_PATHS = {\n    \"catalog/capabilities.yaml\",\n    \"catalog/capability-index.json\",\n    \"archetypes/composition.yaml\",\n    \"evals/contracts/capabilities.json\",\n    \"evals/contracts/agents.json\",\n    \"evals/contracts/thresholds.json\",\n    \"evals/mutations/hard-fail-cases.json\",\n    \"evals/mutations/methodology-cases.json\",\n    \"evals/fixtures/projects/index.json\",\n    \"evals/workflows/contracts.json\",\n    \"evals/schemas/eval-contract.schema.json\",\n    \"evals/schemas/eval-result.schema.json\",\n    \"evals/schemas/executor-input.schema.json\",\n    \"evals/schemas/executor-output.schema.json\",\n    \"evals/schemas/codex-executor-output.schema.json\",\n    \"evals/schemas/judge-input.schema.json\",\n    \"evals/schemas/judge-output.schema.json\",\n    \"evals/schemas/last-green-baseline.schema.json\",\n    \"evals/schemas/workflow-contract.schema.json\",\n}\n\n\ndef git_changed_files(base: str) -> list[str]:\n    completed = subprocess.run(\n        [\"git\", \"diff\", \"--name-only\", f\"{base}...HEAD\"],\n        cwd=ROOT,\n        check=True,\n        capture_output=True,\n        text=True,\n    )\n    committed = completed.stdout.splitlines()\n    unstaged = subprocess.run(\n        [\"git\", \"diff\", \"--name-only\"], cwd=ROOT, check=True, capture_output=True, text=True,\n    ).stdout.splitlines()\n    staged = subprocess.run(\n        [\"git\", \"diff\", \"--cached\", \"--name-only\"], cwd=ROOT, check=True, capture_output=True, text=True,\n    ).stdout.splitlines()\n    untracked = subprocess.run(\n        [\"git\", \"ls-files\", \"--others\", \"--exclude-standard\"],\n        cwd=ROOT,\n        check=True,\n        capture_output=True,\n        text=True,\n    ).stdout.splitlines()\n    return sorted(set(committed + unstaged + staged + untracked))\n\n\ndef _archetype_membership(capabilities: set[str]) -> tuple[list[str], list[str]]:\n… preview truncated",
      "related_capabilities": [],
      "archetypes": []
    },
    {
      "key": "tool:summarize-adm-estimate",
      "id": "summarize-adm-estimate",
      "name": "Summarize ADM Estimate",
      "type": "tool",
      "path": "skills/estimate-adm-modernization/scripts/summarize_adm_estimate.py",
      "description": "Validate portable ADM estimate invariants and emit deterministic totals.",
      "purpose": "Validate portable ADM estimate invariants and emit deterministic totals.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Summarize ADM Estimate",
        "summarize-adm-estimate"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Validate portable ADM estimate invariants and emit deterministic totals.\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport sys\nfrom collections import defaultdict\nfrom pathlib import Path\n\n\ndef load_package(path: Path) -> dict:\n    value = json.loads(path.read_text(encoding=\"utf-8\"))\n    if not isinstance(value, dict):\n        raise ValueError(\"package root must be an object\")\n    return value\n\n\ndef summarize(package: dict) -> tuple[dict, list[str]]:\n    errors: list[str] = []\n    warnings: list[str] = []\n    units = package.get(\"units\")\n    if not isinstance(units, list):\n        return {}, [\"units must be an array\"]\n\n    scenario = package.get(\"scenario\")\n    if not isinstance(scenario, dict):\n        errors.append(\"scenario must be an object\")\n        scenario = {}\n    if scenario.get(\"unit\") != \"person-days\":\n        errors.append(\"scenario.unit must be person-days\")\n    if not scenario.get(\"targetArchitecture\"):\n        warnings.append(\"target architecture is not declared\")\n    if not scenario.get(\"deliveryModel\"):\n        warnings.append(\"delivery model is not declared\")\n\n    seen: set[str] = set()\n    totals = {\"optimistic\": 0.0, \"mostLikely\": 0.0, \"pessimistic\": 0.0, \"expected\": 0.0}\n    workstreams: dict[str, dict[str, float]] = defaultdict(\n        lambda: {\"optimistic\": 0.0, \"mostLikely\": 0.0, \"pessimistic\": 0.0, \"expected\": 0.0}\n    )\n    estimated_count = 0\n    unestimated: list[str] = []\n    unit_results: list[dict] = []\n\n    for index, unit in enumerate(units):\n        if not isinstance(unit, dict):\n            errors.append(f\"units[{index}] must be an object\")\n            continue\n        unit_id = unit.get(\"id\")\n        if not isinstance(unit_id, str) or not unit_id:\n            errors.append(f\"units[{index}].id is required\")\n            continue\n        if unit_id in seen:\n            errors.append(f\"duplicate unit ID: {unit_id}\")\n        seen.add(unit_id)\n\n        trace_ids = unit.get(\"traceIds\")\n        if not isinstance(trace_ids, list) or not trace_ids:\n            warnings.append(f\"{unit_id}: no canonical traceability\")\n        unknown_dimensions = sorted({\n            str(driver.get(\"dimension\", \"UNNAMED\")).strip() or \"UNNAMED\"\n            for driver in unit.get(\"complexityDrivers\", [])\n            if isinstance(driver, dict) and driver.get(\"rating\") == \"UNKNOWN\"\n        })\n… preview truncated",
      "related_capabilities": [
        "archetype:legacy-migration",
        "skill:estimate-adm-modernization"
      ],
      "archetypes": [
        "legacy-migration"
      ]
    },
    {
      "key": "tool:sync-presentation",
      "id": "sync-presentation",
      "name": "Sync Presentation",
      "type": "tool",
      "path": "tools/sync_presentation.py",
      "description": "Synchronize and validate presentation data from canonical Agent Commons metadata.",
      "purpose": "Synchronize and validate presentation data from canonical Agent Commons metadata.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Sync Presentation",
        "sync-presentation"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Synchronize and validate presentation data from canonical Agent Commons metadata.\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport ast\nimport hashlib\nimport json\nimport re\nimport sys\nimport tempfile\nfrom pathlib import Path\nfrom typing import Any, Iterable\n\nsys.path.insert(0, str(Path(__file__).resolve().parent.parent / \"install\"))\nfrom skill_catalog import SkillCatalogError, discover_canonical_skills\n\n\nROOT = Path(__file__).resolve().parent.parent\nCATALOG_PATH = ROOT / \"catalog\" / \"capabilities.yaml\"\nVERSION_PATH = ROOT / \"VERSION\"\nPRESENTATION_PATH = ROOT / \"presentation\" / \"index.html\"\nDATA_PATH = ROOT / \"presentation\" / \"assets\" / \"library-data.js\"\nSTANDALONE_PATH = ROOT / \"presentation\" / \"agent-commons.html\"\nDATA_SCRIPT_RE = re.compile(\n    r'(?P\u003cindent>[ \\t]*)\u003cscript\\s+src=[\"\\']assets/library-data\\.js[\"\\']\\s*>\u003c/script>'\n)\nSTART = '  \u003cscript type=\"application/json\" id=\"capability-data\">\\n'\nEND = '\\n  \u003c/script>\u003c!-- capability-data:end -->'\nMAX_SOURCE_PREVIEW = 2400\nGENERATED_HEADER = \"\"\"// AUTO-GENERATED. DO NOT EDIT DIRECTLY.\n// Run: python3 tools/refresh_commons_presentation.py\nwindow.AGENT_COMMONS_DATA = \"\"\"\nGENERATED_SUFFIX = \";\\n\"\nVALID_TYPES = {\"skill\", \"agent\", \"tool\", \"template\", \"archetype\", \"overlay\", \"adapter\", \"eval\", \"external\"}\n\n\nclass PresentationSyncError(ValueError):\n    pass\n\n\ndef read_json(path: Path) -> dict[str, Any]:\n    try:\n        value = json.loads(path.read_text(encoding=\"utf-8\"))\n    except (OSError, json.JSONDecodeError) as exc:\n        raise PresentationSyncError(f\"invalid canonical JSON/YAML: {path.relative_to(ROOT)}: {exc}\") from exc\n    if not isinstance(value, dict):\n        raise PresentationSyncError(f\"canonical object must be a mapping: {path.relative_to(ROOT)}\")\n    return value\n\n\ndef list_of_strings(value: object) -> list[str]:\n    if not isinstance(value, list):\n        return []\n    return [item.strip() for item in value if isinstance(item, str) and item.strip()]\n\n\ndef humanize(identifier: str) -> str:\n    special = {\n        \"adm\": \"ADM\", \"c4\": \"C4\", \"dfd\": \"DFD\", \"er\": \"ER\", \"html\": \"HTML\",\n        \"mcp\": \"MCP\", \"openspec\": \"OpenSpec\", \"oss\": \"OSS\", \"tdd\": \"TDD\", \"uml\": \"UML\",\n    }\n    return \" \".join(special.get(word, word.capitalize()) for word in identifier.replace(\"_\", \"-\").split(\"-\") if word)\n\n\ndef sanitize_preview(text: str) -> str:\n… preview truncated",
      "related_capabilities": [],
      "archetypes": []
    },
    {
      "key": "tool:validate-client-localization",
      "id": "validate-client-localization",
      "name": "Validate Client Localization",
      "type": "tool",
      "path": "skills/localize-client-artifact/scripts/validate_localization.py",
      "description": "Validate keyed client-artifact localization coverage, freshness, and preservation rules.",
      "purpose": "Validate keyed client-artifact localization coverage, freshness, and preservation rules.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Validate Client Localization",
        "validate-client-localization"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Validate keyed client-artifact localization coverage, freshness, and preservation rules.\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport hashlib\nimport json\nimport re\nimport sys\nfrom collections import Counter\nfrom html.parser import HTMLParser\nfrom pathlib import Path\nfrom typing import Any\n\n\nHASH_RE = re.compile(r\"^sha256:[0-9a-f]{64}$\")\nNUMBER_RE = re.compile(r\"(?\u003c![A-Za-z0-9])[-+]?\\d[\\d.,]*(?![A-Za-z0-9])\")\nFLAG_RE = re.compile(r\"[\\U0001F1E6-\\U0001F1FF]\")\n\n\nclass LocalizationError(ValueError):\n    \"\"\"Raised for invalid localization input.\"\"\"\n\n\nclass ArtifactParser(HTMLParser):\n    def __init__(self) -> None:\n        super().__init__(convert_charrefs=True)\n        self.keys: set[str] = set()\n        self.locale_buttons: list[dict[str, Any]] = []\n        self._button_stack: list[dict[str, Any]] = []\n\n    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:\n        values = {name: value or \"\" for name, value in attrs}\n        key = values.get(\"data-i18n\", \"\").strip()\n        if key:\n            self.keys.add(key)\n        for binding in values.get(\"data-i18n-attr\", \"\").split(\",\"):\n            if \":\" in binding:\n                _attribute, binding_key = binding.split(\":\", 1)\n                if binding_key.strip():\n                    self.keys.add(binding_key.strip())\n        locale = values.get(\"data-localization-locale\", \"\").strip()\n        if tag == \"button\" and locale:\n            record = {\n                \"locale\": locale,\n                \"role\": values.get(\"role\", \"\"),\n                \"aria_checked\": values.get(\"aria-checked\", \"\"),\n                \"aria_label\": values.get(\"aria-label\", \"\").strip(),\n                \"text\": [],\n            }\n            self.locale_buttons.append(record)\n            self._button_stack.append(record)\n        elif self._button_stack:\n            self._button_stack.append(self._button_stack[-1])\n\n    def handle_endtag(self, tag: str) -> None:\n        if self._button_stack:\n            self._button_stack.pop()\n\n    def handle_data(self, data: str) -> None:\n        if self._button_stack:\n            self._button_stack[-1][\"text\"].append(data)\n\n\ndef load_manifest(path: Path) -> dict[str, Any]:\n    try:\n        value = json.loads(path.read_text(encoding=\"utf-8\"))\n    except (OSError, json.JSONDecodeError) as exc:\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "overlay:bilingual-client-delivery",
        "skill:localize-client-artifact"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "tool:validate-commons",
      "id": "validate-commons",
      "name": "Validate Commons",
      "type": "tool",
      "path": "tools/validate_commons.py",
      "description": "Validate canonical-library structure, metadata, references, adapters, evals, and leakage.",
      "purpose": "Validate canonical-library structure, metadata, references, adapters, evals, and leakage.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Validate Commons",
        "validate-commons"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Validate canonical-library structure, metadata, references, adapters, evals, and leakage.\"\"\"\n\nfrom __future__ import annotations\n\nimport ast\nimport json\nimport re\nimport sys\nfrom pathlib import Path\nfrom urllib.parse import unquote\n\nfrom resolve_archetypes import load_contract, validate_contract\nfrom runtime_adapters import validate_adapters\nimport external_capabilities\nimport build_capability_index\nimport resolve_capability_gaps\nimport sync_presentation\nimport check_presentation_visual_contract\n\nROOT = Path(__file__).resolve().parent.parent\nsys.path.insert(0, str(ROOT / \"tools\" / \"evals\"))\nfrom eval_common import validate_configuration as validate_eval_configuration\n\nREQUIRED = [\n    \"README.md\", \"AGENTS.md\", \"VERSION\", \"CHANGELOG.md\", \"CONTRIBUTING.md\",\n    \"catalog/skills.md\", \"catalog/agents.md\", \"catalog/tools.md\", \"catalog/capability-index.json\",\n    \"catalog/templates.md\", \"catalog/archetypes.md\",\n    \"evals/skills/scenarios.yaml\", \"evals/agents/scenarios.yaml\", \"evals/initialization/scenarios.yaml\",\n    \"evals/initialization/test_initializer.py\", \"archetypes/composition.yaml\",\n    \"evals/archetypes/scenarios.yaml\", \"evals/archetypes/test_archetypes.py\",\n    \"archetypes/development/archetype.yaml\", \"archetypes/legacy-migration/archetype.yaml\",\n    \"archetypes/presentation/archetype.yaml\", \"archetypes/research/archetype.yaml\",\n    \"archetypes/overlays/architecture-documentation/overlay.yaml\",\n    \"archetypes/overlays/branded-html/overlay.yaml\",\n    \"archetypes/overlays/bilingual-client-delivery/overlay.yaml\",\n    \"archetypes/overlays/durable-state/overlay.yaml\",\n    \"archetypes/overlays/evidence-traceability/overlay.yaml\",\n    \"archetypes/overlays/living-dashboard/overlay.yaml\",\n    \"archetypes/overlays/sales-storytelling/overlay.yaml\",\n    \"evals/installation/test_installer.py\", \"install/agent_commons.py\",\n    \"catalog/capabilities.yaml\", \"tools/runtime_adapters.py\", \"tools/project_runtimes.py\",\n    \"adapters/README.md\", \"adapters/global-instructions.md\",\n    \"adapters/codex/adapter.yaml\", \"adapters/claude-code/adapter.yaml\",\n    \"adapters/cline/adapter.yaml\", \"adapters/opencode/adapter.yaml\",\n    \"adapters/codex/README.md\", \"adapters/claude-code/README.md\",\n    \"adapters/cline/README.md\", \"adapters/opencode/README.md\",\n    \"presentation/index.html\", \"presentation/README.md\", \"presentation/visual-contract.json\",\n… preview truncated",
      "related_capabilities": [],
      "archetypes": []
    },
    {
      "key": "tool:validate-dashboard-semantics",
      "id": "validate-dashboard-semantics",
      "name": "Validate Dashboard Semantics",
      "type": "tool",
      "path": "skills/build-living-dashboard/scripts/validate_dashboard_semantics.py",
      "description": "Validate semantic completeness of a resolved canonical living-dashboard state.",
      "purpose": "Validate semantic completeness of a resolved canonical living-dashboard state.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Validate Dashboard Semantics",
        "validate-dashboard-semantics"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Validate semantic completeness of a resolved canonical living-dashboard state.\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nfrom collections import Counter\nfrom html.parser import HTMLParser\nfrom pathlib import Path\nimport sys\n\n\nSTRUCTURE_PATH = Path(__file__).resolve().parent.parent / \"assets\" / \"dashboard-structure.json\"\nsys.path.insert(0, str(Path(__file__).resolve().parent))\nfrom build_dashboard import semantic_content_failures\n\n\nclass VisibleTextParser(HTMLParser):\n    def __init__(self) -> None:\n        super().__init__()\n        self.hidden_depth = 0\n        self.parts: list[str] = []\n\n    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:\n        if tag in {\"script\", \"style\", \"template\"}:\n            self.hidden_depth += 1\n\n    def handle_endtag(self, tag: str) -> None:\n        if tag in {\"script\", \"style\", \"template\"} and self.hidden_depth:\n            self.hidden_depth -= 1\n\n    def handle_data(self, data: str) -> None:\n        if not self.hidden_depth and data.strip():\n            self.parts.append(data.strip())\n\n    def text(self) -> str:\n        return \" \".join(\" \".join(self.parts).split())\n\n\ndef validate(data: dict, peer_html: str | None = None) -> list[str]:\n    failures: list[str] = []\n    structure = json.loads(STRUCTURE_PATH.read_text(encoding=\"utf-8\"))\n    expected = structure[\"information_domains\"]\n    resolved_structure = data.get(\"dashboard_structure\")\n    if not isinstance(resolved_structure, dict):\n        return [\"dashboard_structure is missing\"]\n    domains = resolved_structure.get(\"information_domains\")\n    if not isinstance(domains, list):\n        return [\"dashboard_structure.information_domains is missing\"]\n    expected_ids = [item[\"id\"] for item in expected]\n    actual_ids = [item.get(\"id\") for item in domains if isinstance(item, dict)]\n    missing = [identifier for identifier in expected_ids if identifier not in actual_ids]\n    extra = [identifier for identifier in actual_ids if identifier not in expected_ids]\n    duplicates = sorted(identifier for identifier, count in Counter(actual_ids).items() if count > 1)\n    if missing:\n        failures.append(f\"missing information domains: {', '.join(missing)}\")\n    if extra:\n        failures.append(f\"unknown information domains: {', '.join(str(value) for value in extra)}\")\n    if duplicates:\n… preview truncated",
      "related_capabilities": [
        "skill:build-living-dashboard"
      ],
      "archetypes": []
    },
    {
      "key": "tool:validate-dashboard-structure",
      "id": "validate-dashboard-structure",
      "name": "Validate Dashboard Structure",
      "type": "tool",
      "path": "skills/build-living-dashboard/scripts/validate_dashboard_structure.py",
      "description": "Validate a generated dashboard against the canonical structural contract.",
      "purpose": "Validate a generated dashboard against the canonical structural contract.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Validate Dashboard Structure",
        "validate-dashboard-structure"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Validate a generated dashboard against the canonical structural contract.\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nfrom collections import Counter, defaultdict\nimport hashlib\nfrom html.parser import HTMLParser\nimport json\nfrom pathlib import Path\nimport re\n\n\nSTRUCTURE_PATH = Path(__file__).resolve().parent.parent / \"assets\" / \"dashboard-structure.json\"\n\n\nclass DashboardParser(HTMLParser):\n    def __init__(self) -> None:\n        super().__init__(convert_charrefs=True)\n        self.ids: list[str] = []\n        self.sections: list[str] = []\n        self.nav_targets: list[str] = []\n        self.global_hooks: set[str] = set()\n        self.section_hooks: dict[str, set[str]] = defaultdict(set)\n        self.section_regions: dict[str, set[str]] = defaultdict(set)\n        self.information_domains: list[tuple[str, str]] = []\n        self.current_section: str | None = None\n        self.data_script = False\n        self.data_parts: list[str] = []\n\n    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:\n        values = {key: value or \"\" for key, value in attrs}\n        identifier = values.get(\"id\")\n        if identifier:\n            self.ids.append(identifier)\n        if tag == \"section\" and \"data-canonical-section\" in values:\n            self.current_section = values[\"data-canonical-section\"]\n            self.sections.append(self.current_section)\n        if \"data-section-target\" in values:\n            self.nav_targets.append(values[\"data-section-target\"])\n        hook = values.get(\"data-dashboard-hook\")\n        if hook:\n            self.global_hooks.add(hook)\n            if self.current_section:\n                self.section_hooks[self.current_section].add(hook)\n        region = values.get(\"data-dashboard-region\")\n        if region and self.current_section:\n            self.section_regions[self.current_section].add(region)\n        domain = values.get(\"data-information-domain\")\n        if domain:\n            self.information_domains.append((domain, self.current_section or \"\"))\n        if tag == \"script\" and identifier == \"dashboard-data\":\n            self.data_script = True\n\n    def handle_endtag(self, tag: str) -> None:\n        if tag == \"section\":\n            self.current_section = None\n        if tag == \"script\" and self.data_script:\n            self.data_script = False\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "overlay:living-dashboard",
        "skill:build-living-dashboard"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "tool:validate-dashboard-visual",
      "id": "validate-dashboard-visual",
      "name": "Validate Dashboard Visual",
      "type": "tool",
      "path": "skills/build-living-dashboard/scripts/validate_dashboard_visual.py",
      "description": "Validate canonical dashboard design grammar and rendered visual-QA evidence.",
      "purpose": "Validate canonical dashboard design grammar and rendered visual-QA evidence.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Validate Dashboard Visual",
        "validate-dashboard-visual"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Validate canonical dashboard design grammar and rendered visual-QA evidence.\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport hashlib\nimport json\nimport re\nfrom html.parser import HTMLParser\nfrom pathlib import Path\nfrom typing import Any\n\n\nASSET_ROOT = Path(__file__).resolve().parent.parent / \"assets\"\nCONTRACT_PATH = ASSET_ROOT / \"dashboard-visual-contract.json\"\nSHELL_PATH = ASSET_ROOT / \"dashboard-shell.html\"\nBRAND_START = \"/* BRAND_PROFILE_START */\"\nBRAND_END = \"/* BRAND_PROFILE_END */\"\n\n\nclass DashboardVisualError(ValueError):\n    \"\"\"The dashboard has drifted from the canonical visual product contract.\"\"\"\n\n\nclass DashboardParser(HTMLParser):\n    def __init__(self) -> None:\n        super().__init__()\n        self.html_attributes: dict[str, str] = {}\n        self.style_parts: list[str] = []\n        self.data_parts: list[str] = []\n        self._style = False\n        self._data = False\n\n    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:\n        attributes = {key: value or \"\" for key, value in attrs}\n        if tag == \"html\":\n            self.html_attributes = attributes\n        if tag == \"style\":\n            self._style = True\n        if tag == \"script\" and attributes.get(\"id\") == \"dashboard-data\":\n            self._data = True\n\n    def handle_endtag(self, tag: str) -> None:\n        if tag == \"style\":\n            self._style = False\n        if tag == \"script\" and self._data:\n            self._data = False\n\n    def handle_data(self, data: str) -> None:\n        if self._style:\n            self.style_parts.append(data)\n        if self._data:\n            self.data_parts.append(data)\n\n\ndef load_contract() -> dict[str, Any]:\n    contract = json.loads(CONTRACT_PATH.read_text(encoding=\"utf-8\"))\n    if contract.get(\"schema_version\") != 1 or not contract.get(\"required_rendered_states\"):\n        raise DashboardVisualError(\"canonical dashboard visual contract is invalid\")\n    return contract\n\n\ndef contract_fingerprint(contract: dict[str, Any] | None = None) -> str:\n    contract = contract or load_contract()\n    canonical = json.dumps(contract, ensure_ascii=False, sort_keys=True, separators=(\",\", \":\"))\n    return hashlib.sha256(canonical.encode(\"utf-8\")).hexdigest()\n\n\ndef _style_without_brand(style: str) -> str:\n    if BRAND_START not in style or BRAND_END not in style:\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "overlay:living-dashboard",
        "skill:build-living-dashboard"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "tool:validate-diagram-model",
      "id": "validate-diagram-model",
      "name": "Validate Diagram Model",
      "type": "tool",
      "path": "skills/create-technical-diagram/scripts/validate_diagram_model.py",
      "description": "Validate a lightweight evidence-backed technical-diagram model.",
      "purpose": "Validate a lightweight evidence-backed technical-diagram model.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Validate Diagram Model",
        "validate-diagram-model"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Validate a lightweight evidence-backed technical-diagram model.\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nfrom pathlib import Path\nfrom typing import Any\n\n\nDIAGRAM_TYPES = {\n    \"system-landscape\",\n    \"component-architecture\",\n    \"class\",\n    \"er\",\n    \"sequence\",\n    \"data-flow\",\n    \"migration-roadmap\",\n}\nCONFIDENCE = {\"VERIFIED\", \"INFERRED\", \"UNKNOWN\"}\nDIAGRAM_STATUS = {\"CURRENT\", \"TARGET\", \"TRANSITION\", \"COMPARISON\", \"PROPOSED\", \"DRAFT\", \"FINAL\"}\nMAX_VIEW_NODES = 40\nMAX_VIEW_RELATIONSHIPS = 60\n\n\nclass DiagramModelError(ValueError):\n    \"\"\"The diagram model is unreadable or structurally invalid.\"\"\"\n\n\ndef load_model(path: Path) -> dict[str, Any]:\n    try:\n        value = json.loads(path.read_text(encoding=\"utf-8\"))\n    except (OSError, json.JSONDecodeError) as exc:\n        raise DiagramModelError(str(exc)) from exc\n    if not isinstance(value, dict):\n        raise DiagramModelError(\"model root must be an object\")\n    return value\n\n\ndef objects(value: object, label: str, errors: list[str]) -> list[dict[str, Any]]:\n    if not isinstance(value, list):\n        errors.append(f\"{label} must be a list\")\n        return []\n    result: list[dict[str, Any]] = []\n    for index, item in enumerate(value):\n        if not isinstance(item, dict):\n            errors.append(f\"{label}[{index}] must be an object\")\n        else:\n            result.append(item)\n    return result\n\n\ndef unique_ids(entries: list[dict[str, Any]], label: str, errors: list[str]) -> dict[str, dict[str, Any]]:\n    result: dict[str, dict[str, Any]] = {}\n    for index, entry in enumerate(entries):\n        identifier = entry.get(\"id\")\n        if not isinstance(identifier, str) or not identifier.strip():\n            errors.append(f\"{label}[{index}].id must be a non-empty string\")\n            continue\n        if identifier in result:\n            errors.append(f\"duplicate {label} id: {identifier}\")\n            continue\n        result[identifier] = entry\n    return result\n\n\ndef string_list(value: object, label: str, errors: list[str]) -> list[str]:\n    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):\n        errors.append(f\"{label} must be a list of non-empty strings\")\n        return []\n    return list(value)\n\n\ndef validate_confidence(\n    entry: dict[str, Any],\n    label: str,\n    evidence_ids: set[str],\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "overlay:architecture-documentation",
        "skill:create-technical-diagram"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "tool:validate-html",
      "id": "validate-html",
      "name": "Validate HTML",
      "type": "tool",
      "path": "skills/validate-visual-artifact/scripts/validate_html.py",
      "description": "Validate static HTML, brand-profile consistency, and independent brand fidelity.",
      "purpose": "Validate static HTML, brand-profile consistency, and independent brand fidelity.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Validate HTML",
        "validate-html"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Validate static HTML, brand-profile consistency, and independent brand fidelity.\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport base64\nimport binascii\nimport hashlib\nimport json\nimport re\nimport sys\nfrom html.parser import HTMLParser\nfrom pathlib import Path\nfrom urllib.parse import urlparse\n\n\n# Widest viewport still treated as a mobile reflow state by capture_brand_qa.mjs.\nMOBILE_WIDTH = 480\n\n\nclass Inspector(HTMLParser):\n    def __init__(self) -> None:\n        super().__init__(convert_charrefs=True)\n        self.tags: list[str] = []\n        self.ids: list[str] = []\n        self.external: list[str] = []\n        self.buttons: list[dict[str, str | None]] = []\n        self.icons: list[dict[str, str]] = []\n        self.brand_logos: list[dict[str, str]] = []\n\n    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:\n        self.tags.append(tag)\n        values = {key: value or \"\" for key, value in attrs}\n        if values.get(\"id\"):\n            self.ids.append(values[\"id\"])\n        if tag in {\"script\", \"link\", \"img\", \"iframe\", \"video\", \"audio\", \"source\"}:\n            target = values.get(\"src\") or values.get(\"href\")\n            if target and urlparse(target).scheme in {\"http\", \"https\"}:\n                self.external.append(target)\n        if tag == \"button\":\n            self.buttons.append({\"aria-label\": values.get(\"aria-label\"), \"title\": values.get(\"title\")})\n        if tag == \"link\" and \"icon\" in values.get(\"rel\", \"\").lower().split():\n            self.icons.append(values)\n        if tag == \"img\" and (\"data-brand-logo\" in values or values.get(\"data-brand-asset\") == \"logo\"):\n            self.brand_logos.append(values)\n\n\ndef add(findings: list[dict[str, str]], code: str, detail: str, severity: str = \"error\") -> None:\n    findings.append({\"severity\": severity, \"code\": code, \"detail\": detail})\n\n\ndef embedded_bytes(data_uri: str) -> bytes:\n    if not data_uri.startswith(\"data:\") or \",\" not in data_uri or \";base64\" not in data_uri.split(\",\", 1)[0]:\n        raise ValueError(\"asset is not a base64 data URI\")\n    try:\n        decoded = base64.b64decode(data_uri.split(\",\", 1)[1], validate=True)\n    except (ValueError, binascii.Error) as exc:\n        raise ValueError(\"asset data URI is invalid\") from exc\n    if not decoded:\n        raise ValueError(\"asset data URI is empty\")\n    return decoded\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "overlay:bilingual-client-delivery",
        "overlay:branded-html",
        "overlay:living-dashboard",
        "skill:validate-visual-artifact"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "tool:validate-migration-manifest",
      "id": "validate-migration-manifest",
      "name": "Validate Migration Manifest",
      "type": "tool",
      "path": "skills/migrate-code-with-evidence/scripts/validate_migration_manifest.py",
      "description": "Validate a bounded, traceable, fail-closed code-migration manifest.",
      "purpose": "Validate a bounded, traceable, fail-closed code-migration manifest.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Validate Migration Manifest",
        "validate-migration-manifest"
      ],
      "runtime_support": [],
      "source_preview": "#!/usr/bin/env python3\n\"\"\"Validate a bounded, traceable, fail-closed code-migration manifest.\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport re\nimport sys\nfrom pathlib import Path, PurePosixPath\nfrom typing import Any\n\n\nFORBIDDEN_KEY = re.compile(r\"(?:api[_-]?key|password|secret|access[_-]?token|credential)\", re.I)\nUNSAFE_COMMAND = re.compile(r\"(?:\\brm\\s+-rf\\b|\\bsudo\\b|\\bcurl\\b[^\\n|]*\\|\\s*(?:sh|bash)\\b|\\bwget\\b[^\\n|]*\\|\\s*(?:sh|bash)\\b)\", re.I)\nSTATUSES = {\"PLANNED\", \"RED\", \"GREEN\", \"VERIFIED\", \"BLOCKED\"}\n\n\ndef object_at(value: Any, key: str, errors: list[str]) -> dict[str, Any]:\n    child = value.get(key) if isinstance(value, dict) else None\n    if not isinstance(child, dict):\n        errors.append(f\"{key} must be an object\")\n        return {}\n    return child\n\n\ndef string_list(value: Any, label: str, errors: list[str], *, allow_empty: bool = False) -> list[str]:\n    if not isinstance(value, list) or (not value and not allow_empty) or not all(isinstance(item, str) and item.strip() for item in value):\n        errors.append(f\"{label} must be {'a' if allow_empty else 'a non-empty'} string array\")\n        return []\n    return value\n\n\ndef find_forbidden_keys(value: Any, path: str = \"\") -> list[str]:\n    findings: list[str] = []\n    if isinstance(value, dict):\n        for key, child in value.items():\n            current = f\"{path}.{key}\" if path else key\n            if FORBIDDEN_KEY.fullmatch(key) and not (path == \"safety\" and key == \"credentials\"):\n                findings.append(current)\n            findings.extend(find_forbidden_keys(child, current))\n    elif isinstance(value, list):\n        for index, child in enumerate(value):\n            findings.extend(find_forbidden_keys(child, f\"{path}[{index}]\"))\n    return findings\n\n\ndef normalized_root(value: Any) -> str:\n    if not isinstance(value, str) or not value.strip():\n        return \"\"\n    return str(PurePosixPath(value.strip()))\n\n\ndef is_nested(child: str, parent: str) -> bool:\n    child_parts = PurePosixPath(child).parts\n    parent_parts = PurePosixPath(parent).parts\n    return len(child_parts) > len(parent_parts) and child_parts[:len(parent_parts)] == parent_parts\n\n\ndef validate(manifest: Any) -> tuple[dict[str, Any], list[str]]:\n    errors: list[str] = []\n    if not isinstance(manifest, dict):\n        return {}, [\"manifest root must be an object\"]\n… preview truncated",
      "related_capabilities": [
        "archetype:legacy-migration",
        "skill:migrate-code-with-evidence"
      ],
      "archetypes": [
        "legacy-migration"
      ]
    },
    {
      "key": "archetype:legacy-migration",
      "id": "legacy-migration",
      "name": "Legacy analysis and modernization",
      "type": "archetype",
      "path": "archetypes/legacy-migration/archetype.yaml",
      "description": "complete configured discovery and behavior reconstruction across legacy technologies using bounded internal slices; modernization requirements, migration boundaries, coexistence, and verification; analysis-only or hybrid analysis plus target implementation",
      "purpose": "complete configured discovery and behavior reconstruction across legacy technologies using bounded internal slices; modernization requirements, migration boundaries, coexistence, and verification; analysis-only or hybrid analysis plus target implementation",
      "use_when": [
        "complete configured discovery and behavior reconstruction across legacy technologies using bounded internal slices",
        "modernization requirements, migration boundaries, coexistence, and verification",
        "analysis-only or hybrid analysis plus target implementation"
      ],
      "not_when": [
        "target-state invention without source evidence",
        "assuming COBOL, Java, SOAP, XSD, or any other technology is mandatory"
      ],
      "inputs": [
        "authorized source boundary, read-only paths, technologies, entry points, persistence, batch, and integrations",
        "migration boundary, target stack, coexistence expectations, reference implementation, and implementation scope",
        "evidence depth, call or data-flow graphs, requirement extraction, parity expectations, validation, and dashboard audience"
      ],
      "workflow": [
        "requirements-discovery",
        "migration-openspec-preparation",
        "deterministic-legacy-structure",
        "parallel-discovery",
        "evidence-constrained-code-migration",
        "migration-architecture-review",
        "migration-test-review",
        "adm-modernization-estimation"
      ],
      "outputs": [
        "deterministic source inventory and bounded analysis batches",
        "application topology, dependency, call, data-flow, interface, and business-rule evidence as required",
        "modernization requirements and migration strategy when selected",
        "target implementation and verification only through composition with development"
      ],
      "validation": [
        "protect declared legacy sources as read-only",
        "assess characterization and migration tests with mutation testing on the migrated target or supported harness, and never attempt to mutate an unsupported legacy source technology",
        "separate observed behavior, interpretation, gaps, and target proposals",
        "establish a denominator before completeness claims",
        "treat technology-specific references as conditional evidence routes",
        "treat a separate reference application as a discovery prior and never target evidence"
      ],
      "tags": [],
      "search_terms": [
        "Legacy analysis and modernization",
        "legacy-migration"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "{\n  \"schema_version\": 1,\n  \"id\": \"legacy-migration\",\n  \"kind\": \"archetype\",\n  \"title\": \"Legacy analysis and modernization\",\n  \"intent\": [\n    \"complete configured discovery and behavior reconstruction across legacy technologies using bounded internal slices\",\n    \"modernization requirements, migration boundaries, coexistence, and verification\",\n    \"analysis-only or hybrid analysis plus target implementation\"\n  ],\n  \"not_for\": [\n    \"target-state invention without source evidence\",\n    \"assuming COBOL, Java, SOAP, XSD, or any other technology is mandatory\"\n  ],\n  \"initialization\": {\n    \"discover\": [\n      \"source repositories, application boundaries, languages, entry points, databases, schemas, interfaces, and documents\",\n      \"existing inventories, topology, dependency graphs, requirements, target-stack decisions, validation assets, and any explicitly authorized separate reference applications\"\n    ],\n    \"ask_if_unresolved\": [\n      \"authorized source boundary, read-only paths, technologies, entry points, persistence, batch, and integrations\",\n      \"migration boundary, target stack, coexistence expectations, reference implementation, and implementation scope\",\n      \"evidence depth, call or data-flow graphs, requirement extraction, parity expectations, validation, and dashboard audience\"\n    ]\n  },\n  \"execution_guidance\": {\n    \"dag\": [\n      {\n        \"id\": \"inventory\",\n        \"after\": [],\n        \"fan_in\": \"one validated denominator, fingerprint, and exclusive batch partition\"\n      },\n      {\n        \"id\": \"bounded-analysis\",\n        \"after\": [\n          \"inventory\"\n        ],\n        \"fan_out\": \"all relevant artifacts assigned once across non-overlapping language, subsystem, or program-family evidence packets\"\n      },\n      {\n        \"id\": \"analysis-integration\",\n        \"after\": [\n          \"bounded-analysis\"\n        ],\n        \"fan_in\": \"coordinator validates zero unaccounted relevant artifacts, reconciles cross-system behavior, and allocates canonical evidence IDs\"\n      },\n      {\n        \"id\": \"requirement-candidates\",\n        \"after\": [\n          \"analysis-integration\"\n        ],\n        \"fan_out\": \"temporary candidates only for independent evidence domains\"\n      },\n      {\n        \"id\": \"requirements-synthesis\",\n        \"after\": [\n          \"requirement-candidates\"\n        ],\n… preview truncated",
      "related_capabilities": [
        "adapter:claude-code",
        "adapter:cline",
        "adapter:codex",
        "adapter:opencode",
        "agent:architecture-reviewer",
        "agent:financial-forecast-reviewer",
        "agent:legacy-discovery-specialist",
        "agent:test-behavior-reviewer",
        "overlay:architecture-documentation",
        "overlay:bilingual-client-delivery",
        "overlay:branded-html",
        "overlay:consulting-delivery",
        "overlay:durable-state",
        "overlay:evidence-traceability",
        "overlay:living-dashboard",
        "overlay:public-sector-client-delivery",
        "overlay:sales-storytelling",
        "skill:accessibility-review",
        "skill:analyze-legacy-system",
        "skill:audit-delivery-traceability",
        "skill:build-living-dashboard",
        "skill:continue-project",
        "skill:coordinate-parallel-agents",
        "skill:create-branded-html-artifact",
        "skill:create-class-diagram",
        "skill:create-component-architecture-diagram",
        "skill:create-data-flow-diagram",
        "skill:create-er-diagram",
        "skill:create-sequence-diagram",
        "skill:create-system-landscape-diagram",
        "skill:create-technical-diagram",
        "skill:derive-modernization-requirements",
        "skill:design-test-strategy",
        "skill:estimate-adm-modernization",
        "skill:forecast-project-financials",
        "skill:inventory-codebase",
        "skill:localize-client-artifact",
        "skill:maintain-project-memory",
        "skill:manage-project-delivery",
        "skill:migrate-code-with-evidence",
        "skill:mutation-testing",
        "skill:plan-work",
        "skill:protect-git-work",
        "skill:review-openspec-change",
        "skill:sales-storytelling",
        "skill:specify-openspec-change",
        "skill:test-driven-development",
        "skill:validate-visual-artifact",
        "template:acceptance-audit-template",
        "template:bilingual-artifact-runtime",
        "template:dashboard-data-example",
        "template:dashboard-shell",
        "template:dashboard-structure",
        "template:diagram-model-example",
        "template:editorial-html-shell",
        "template:evidence-analysis-template",
        "template:evidence-record-example",
        "template:localization-manifest-example",
        "template:project-memory-template-set",
        "template:requirement-record-example",
        "template:sales-narrative-template",
        "template:visual-pattern-guidance",
        "tool:analyze-project-delivery",
        "tool:audit-trace-graph",
        "tool:audit-trace-matrix",
        "tool:build-dashboard",
        "tool:calculate-project-financial-forecast",
        "tool:coordinate-legacy-analysis",
        "tool:extract-legacy-structure",
        "tool:inventory-codebase-tool",
        "tool:manage-project-memory",
        "tool:resolve-project-continuation",
        "tool:summarize-adm-estimate",
        "tool:validate-client-localization",
        "tool:validate-dashboard-structure",
        "tool:validate-dashboard-visual",
        "tool:validate-diagram-model",
        "tool:validate-html",
        "tool:validate-migration-manifest"
      ],
      "archetypes": []
    },
    {
      "key": "archetype:presentation",
      "id": "presentation",
      "name": "Presentation and interactive storytelling",
      "type": "archetype",
      "path": "archetypes/presentation/archetype.yaml",
      "description": "sales, management, technical executive, capability, solution, and workshop presentations; interactive standalone HTML storytelling when HTML is the chosen medium",
      "purpose": "sales, management, technical executive, capability, solution, and workshop presentations; interactive standalone HTML storytelling when HTML is the chosen medium",
      "use_when": [
        "sales, management, technical executive, capability, solution, and workshop presentations",
        "interactive standalone HTML storytelling when HTML is the chosen medium"
      ],
      "not_when": [
        "assuming every presentation must be HTML",
        "generic AI-generated SaaS styling without audience, evidence, or brand direction"
      ],
      "inputs": [
        "objective, audience, desired decision or action, and authoritative factual sources",
        "narrative, technical depth, brand or client evidence, existing presentation references, and visual thesis",
        "diagrams, graphs, interactivity, accessibility, offline or standalone behavior, and delivery format"
      ],
      "workflow": [
        "presentation-accessibility-review"
      ],
      "outputs": [
        "audience-specific narrative and source index",
        "presentation or workshop artifact in the explicitly selected medium",
        "brand-derived visual system when resolvable, otherwise the labeled Accenture fallback",
        "visual, interaction, accessibility, responsive, print, and offline validation evidence as applicable"
      ],
      "validation": [
        "map factual claims to authoritative sources",
        "derive visual identity from verified client or company evidence when available",
        "always create the selected HTML artifact and use the Accenture fallback when branding is absent or unavailable",
        "do not clone protected marketing pages or invent unsupported brand rules",
        "do not select HTML-only capabilities for non-HTML delivery",
        "treat sales, executive, technical, informational, workshop, and internal as combinable purposes rather than separate archetypes"
      ],
      "tags": [],
      "search_terms": [
        "presentation",
        "Presentation and interactive storytelling"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "{\n  \"schema_version\": 1,\n  \"id\": \"presentation\",\n  \"kind\": \"archetype\",\n  \"title\": \"Presentation and interactive storytelling\",\n  \"intent\": [\n    \"sales, management, technical executive, capability, solution, and workshop presentations\",\n    \"interactive standalone HTML storytelling when HTML is the chosen medium\"\n  ],\n  \"not_for\": [\n    \"assuming every presentation must be HTML\",\n    \"generic AI-generated SaaS styling without audience, evidence, or brand direction\"\n  ],\n  \"initialization\": {\n    \"discover\": [\n      \"source material, existing decks, website and design-system evidence, logos, assets, diagrams, graphs, and delivery constraints\"\n    ],\n    \"ask_if_unresolved\": [\n      \"objective, audience, desired decision or action, and authoritative factual sources\",\n      \"narrative, technical depth, brand or client evidence, existing presentation references, and visual thesis\",\n      \"diagrams, graphs, interactivity, accessibility, offline or standalone behavior, and delivery format\"\n    ]\n  },\n  \"purposes\": {\n    \"supported\": [\n      \"sales\",\n      \"executive\",\n      \"technical\",\n      \"informational\",\n      \"workshop\",\n      \"internal\"\n    ],\n    \"multiple_allowed\": true,\n    \"selection_rule\": \"infer explicit purposes from the brief and ask only when the audience or desired outcome leaves the presentation purpose materially ambiguous\"\n  },\n  \"capabilities\": {\n    \"required\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    },\n    \"default\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": [\n        \"project-instructions-template\"\n      ]\n    },\n    \"recommended\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    },\n    \"optional\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    }\n  },\n  \"conditions\": [\n    {\n      \"id\": \"presentation-accessibility-review\",\n      \"when\": \"the presentation is interactive, public, consequential, or has an explicit accessibility expectation\",\n      \"capabilities\": {\n        \"skills\": [\n          \"accessibility-review\"\n        ],\n        \"agents\": [],\n        \"tools\": [],\n        \"templates\": []\n      }\n    }\n  ],\n  \"recommended_overlays\": [\n    {\n      \"id\": \"architecture-documentation\",\n… preview truncated",
      "related_capabilities": [
        "adapter:claude-code",
        "adapter:cline",
        "adapter:codex",
        "adapter:opencode",
        "overlay:architecture-documentation",
        "overlay:bilingual-client-delivery",
        "overlay:branded-html",
        "overlay:durable-state",
        "overlay:living-dashboard",
        "overlay:public-sector-client-delivery",
        "overlay:sales-storytelling",
        "skill:accessibility-review",
        "skill:build-living-dashboard",
        "skill:create-branded-html-artifact",
        "skill:create-class-diagram",
        "skill:create-component-architecture-diagram",
        "skill:create-data-flow-diagram",
        "skill:create-er-diagram",
        "skill:create-sequence-diagram",
        "skill:create-system-landscape-diagram",
        "skill:create-technical-diagram",
        "skill:localize-client-artifact",
        "skill:maintain-project-memory",
        "skill:plan-work",
        "skill:sales-storytelling",
        "skill:validate-visual-artifact",
        "template:bilingual-artifact-runtime",
        "template:dashboard-data-example",
        "template:dashboard-shell",
        "template:dashboard-structure",
        "template:diagram-model-example",
        "template:editorial-html-shell",
        "template:localization-manifest-example",
        "template:project-instructions-template",
        "template:project-memory-template-set",
        "template:sales-narrative-template",
        "template:visual-pattern-guidance",
        "tool:build-dashboard",
        "tool:manage-project-memory",
        "tool:validate-client-localization",
        "tool:validate-dashboard-structure",
        "tool:validate-dashboard-visual",
        "tool:validate-diagram-model",
        "tool:validate-html"
      ],
      "archetypes": []
    },
    {
      "key": "archetype:research",
      "id": "research",
      "name": "Research and evidence synthesis",
      "type": "archetype",
      "path": "archetypes/research/archetype.yaml",
      "description": "market, technology, product, competitor, client, industry, architecture, and ecosystem research; evidence gathering and synthesis for decisions, reports, dashboards, or presentations; research that remains useful without a downstream presentation",
      "purpose": "market, technology, product, competitor, client, industry, architecture, and ecosystem research; evidence gathering and synthesis for decisions, reports, dashboards, or presentations; research that remains useful without a downstream presentation",
      "use_when": [
        "market, technology, product, competitor, client, industry, architecture, and ecosystem research",
        "evidence gathering and synthesis for decisions, reports, dashboards, or presentations",
        "research that remains useful without a downstream presentation"
      ],
      "not_when": [
        "external agent-capability discovery, which uses the governed external intelligence workflow",
        "a simple lookup that does not justify a research evidence base",
        "unsupported conclusions derived only from filenames, snippets, or memory"
      ],
      "inputs": [
        "research question, audience, decision or artifact supported, and required depth",
        "geographic, industry, technology, competitor, and temporal boundaries",
        "authoritative sources, evidence-quality expectations, output format, and presentation handoff needs"
      ],
      "workflow": [],
      "outputs": [
        "research plan and bounded question set",
        "source index and evidence-backed findings",
        "synthesis with implications, conflicts, risks, and unknowns",
        "presentation-ready synthesis when a downstream presentation is selected"
      ],
      "validation": [
        "separate sourced fact, synthesis, proposal, assumption, conflict, and unknown",
        "prefer direct authoritative evidence where appropriate",
        "actively inspect counterarguments and competing approaches for consequential findings",
        "do not turn a source list into a claim of completed research"
      ],
      "tags": [],
      "search_terms": [
        "research",
        "Research and evidence synthesis"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "{\n  \"schema_version\": 1,\n  \"id\": \"research\",\n  \"kind\": \"archetype\",\n  \"title\": \"Research and evidence synthesis\",\n  \"intent\": [\n    \"market, technology, product, competitor, client, industry, architecture, and ecosystem research\",\n    \"evidence gathering and synthesis for decisions, reports, dashboards, or presentations\",\n    \"research that remains useful without a downstream presentation\"\n  ],\n  \"not_for\": [\n    \"external agent-capability discovery, which uses the governed external intelligence workflow\",\n    \"a simple lookup that does not justify a research evidence base\",\n    \"unsupported conclusions derived only from filenames, snippets, or memory\"\n  ],\n  \"initialization\": {\n    \"discover\": [\n      \"supplied topic, questions, audience, desired decision, scope boundaries, source material, repositories, documents, URLs, and references\",\n      \"existing research plans, findings, sources, synthesis, reports, dashboards, and presentation inputs\"\n    ],\n    \"ask_if_unresolved\": [\n      \"research question, audience, decision or artifact supported, and required depth\",\n      \"geographic, industry, technology, competitor, and temporal boundaries\",\n      \"authoritative sources, evidence-quality expectations, output format, and presentation handoff needs\"\n    ]\n  },\n  \"capabilities\": {\n    \"required\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    },\n    \"default\": {\n      \"skills\": [\n        \"deep-research\"\n      ],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": [\n        \"research-plan-template\",\n        \"research-synthesis-template\",\n        \"project-instructions-template\"\n      ]\n    },\n    \"recommended\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    },\n    \"optional\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    }\n  },\n  \"capability_expectations\": {\n    \"required\": [\n      {\n        \"id\": \"structured-research\",\n        \"when\": \"always\",\n        \"description\": \"Frame the research question, evaluate evidence, synthesize multiple perspectives, and retain claim provenance.\"\n      }\n    ],\n    \"strongly_recommended\": [],\n    \"optional\": []\n  },\n  \"conditions\": [],\n  \"dashboard_projection\": {\n    \"structure\": \"agent-commons-living-dashboard\",\n    \"enable_when_selected\": [],\n    \"project_extensions\": [\n      {\n… preview truncated",
      "related_capabilities": [
        "adapter:claude-code",
        "adapter:cline",
        "adapter:codex",
        "adapter:opencode",
        "agent:financial-forecast-reviewer",
        "overlay:architecture-documentation",
        "overlay:bilingual-client-delivery",
        "overlay:branded-html",
        "overlay:consulting-delivery",
        "overlay:durable-state",
        "overlay:evidence-traceability",
        "overlay:living-dashboard",
        "overlay:public-sector-client-delivery",
        "overlay:sales-storytelling",
        "skill:accessibility-review",
        "skill:audit-delivery-traceability",
        "skill:build-living-dashboard",
        "skill:create-branded-html-artifact",
        "skill:create-class-diagram",
        "skill:create-component-architecture-diagram",
        "skill:create-data-flow-diagram",
        "skill:create-er-diagram",
        "skill:create-sequence-diagram",
        "skill:create-system-landscape-diagram",
        "skill:create-technical-diagram",
        "skill:deep-research",
        "skill:derive-modernization-requirements",
        "skill:forecast-project-financials",
        "skill:localize-client-artifact",
        "skill:maintain-project-memory",
        "skill:manage-project-delivery",
        "skill:plan-work",
        "skill:sales-storytelling",
        "skill:validate-visual-artifact",
        "template:acceptance-audit-template",
        "template:bilingual-artifact-runtime",
        "template:dashboard-data-example",
        "template:dashboard-shell",
        "template:dashboard-structure",
        "template:diagram-model-example",
        "template:editorial-html-shell",
        "template:evidence-record-example",
        "template:localization-manifest-example",
        "template:project-instructions-template",
        "template:project-memory-template-set",
        "template:requirement-record-example",
        "template:research-plan-template",
        "template:research-synthesis-template",
        "template:sales-narrative-template",
        "template:visual-pattern-guidance",
        "tool:analyze-project-delivery",
        "tool:audit-trace-graph",
        "tool:audit-trace-matrix",
        "tool:build-dashboard",
        "tool:calculate-project-financial-forecast",
        "tool:manage-project-memory",
        "tool:validate-client-localization",
        "tool:validate-dashboard-structure",
        "tool:validate-dashboard-visual",
        "tool:validate-diagram-model",
        "tool:validate-html"
      ],
      "archetypes": []
    },
    {
      "key": "archetype:development",
      "id": "development",
      "name": "Software and application development",
      "type": "archetype",
      "path": "archetypes/development/archetype.yaml",
      "description": "greenfield applications and feature-rich prototypes; frontend, backend, API, internal-tool, and product development; modernization target implementation when delivery work is material",
      "purpose": "greenfield applications and feature-rich prototypes; frontend, backend, API, internal-tool, and product development; modernization target implementation when delivery work is material",
      "use_when": [
        "greenfield applications and feature-rich prototypes",
        "frontend, backend, API, internal-tool, and product development",
        "modernization target implementation when delivery work is material"
      ],
      "not_when": [
        "a tiny one-off edit that does not justify a durable workflow",
        "legacy discovery without approved target implementation behavior"
      ],
      "inputs": [
        "goal, users, observable acceptance, and greenfield versus existing code",
        "application shape, data ownership, authentication, integrations, and deployment target",
        "test levels, architecture expectations, UI and accessibility expectations, documentation, and HTML artifact need"
      ],
      "workflow": [
        "existing-code-denominator",
        "normalized-ready-queue",
        "frontend-product-design",
        "frontend-architecture",
        "structured-data-sharing",
        "parallel-agent-work",
        "independent-architecture-review",
        "privacy-security-review",
        "consequential-state-change",
        "unsupported-mutation-technology",
        "independent-test-review"
      ],
      "outputs": [
        "project-specific AGENTS.md and resolved .agent-commons.yaml",
        "bounded implementation plan or ready slice",
        "implementation and tests with exact validation evidence, including the mutation quality status where supported",
        "architecture, deployment, and decision documentation only when the project requires them"
      ],
      "validation": [
        "use OpenSpec specification and test-driven implementation by default unless the user or established project methodology explicitly overrides them",
        "after tests pass, validate test strength with targeted mutation testing on changed critical behavior where the technology supports it, and represent an unsupported technology explicitly rather than as a pass",
        "preserve existing conventions and user work",
        "do not claim unapproved or unobservable behavior as implemented",
        "keep deployment and provider details project-specific unless separately validated"
      ],
      "tags": [],
      "search_terms": [
        "development",
        "Software and application development"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "{\n  \"schema_version\": 1,\n  \"id\": \"development\",\n  \"kind\": \"archetype\",\n  \"title\": \"Software and application development\",\n  \"intent\": [\n    \"greenfield applications and feature-rich prototypes\",\n    \"frontend, backend, API, internal-tool, and product development\",\n    \"modernization target implementation when delivery work is material\"\n  ],\n  \"not_for\": [\n    \"a tiny one-off edit that does not justify a durable workflow\",\n    \"legacy discovery without approved target implementation behavior\"\n  ],\n  \"initialization\": {\n    \"discover\": [\n      \"existing source, manifests, tests, architecture documents, and deployment configuration\",\n      \"frontend, backend, persistence, authentication, integration, and UI conventions\"\n    ],\n    \"ask_if_unresolved\": [\n      \"goal, users, observable acceptance, and greenfield versus existing code\",\n      \"application shape, data ownership, authentication, integrations, and deployment target\",\n      \"test levels, architecture expectations, UI and accessibility expectations, documentation, and HTML artifact need\"\n    ]\n  },\n  \"execution_guidance\": {\n    \"dag\": [\n      {\n        \"id\": \"specification\",\n        \"after\": [],\n        \"fan_out\": \"one coordinator-reserved OpenSpec change per independent behavior domain\"\n      },\n      {\n        \"id\": \"readiness\",\n        \"after\": [\n          \"specification\"\n        ],\n        \"fan_in\": \"cross-change terminology, dependency, and requirement-revision reconciliation\"\n      },\n      {\n        \"id\": \"implementation-slices\",\n        \"after\": [\n          \"readiness\"\n        ],\n        \"fan_out\": \"dependency-ready slices with exclusive paths, shared-surface declarations, and isolated writable state\"\n      },\n      {\n        \"id\": \"test-quality\",\n        \"after\": [\n          \"implementation-slices\"\n        ],\n        \"fan_out\": \"targeted mutation scope per accepted slice, then test hardening against meaningful survivors\"\n      },\n      {\n        \"id\": \"integration\",\n        \"after\": [\n          \"test-quality\"\n        ],\n        \"fan_in\": \"coordinator-only merges with affected gates after every accepted slice\"\n      },\n      {\n        \"id\": \"verification\",\n        \"after\": [\n          \"integration\"\n        ],\n        \"fan_in\": \"one immutable integrated snapshot before change-level PASS\"\n      },\n      {\n        \"id\": \"completion\",\n        \"after\": [\n          \"verification\"\n        ],\n… preview truncated",
      "related_capabilities": [
        "adapter:claude-code",
        "adapter:cline",
        "adapter:codex",
        "adapter:opencode",
        "agent:architecture-reviewer",
        "agent:financial-forecast-reviewer",
        "agent:privacy-security-reviewer",
        "agent:test-behavior-reviewer",
        "overlay:architecture-documentation",
        "overlay:bilingual-client-delivery",
        "overlay:branded-html",
        "overlay:consulting-delivery",
        "overlay:durable-state",
        "overlay:evidence-traceability",
        "overlay:living-dashboard",
        "overlay:public-sector-client-delivery",
        "overlay:sales-storytelling",
        "skill:accessibility-review",
        "skill:anonymize-data",
        "skill:audit-delivery-traceability",
        "skill:build-living-dashboard",
        "skill:complete-openspec-change",
        "skill:continue-project",
        "skill:coordinate-parallel-agents",
        "skill:create-branded-html-artifact",
        "skill:create-class-diagram",
        "skill:create-component-architecture-diagram",
        "skill:create-data-flow-diagram",
        "skill:create-er-diagram",
        "skill:create-sequence-diagram",
        "skill:create-system-landscape-diagram",
        "skill:create-technical-diagram",
        "skill:derive-modernization-requirements",
        "skill:design-frontend-architecture",
        "skill:design-test-strategy",
        "skill:execute-safe-change",
        "skill:forecast-project-financials",
        "skill:frontend-design",
        "skill:implement-openspec-change",
        "skill:implement-ready-slice",
        "skill:inventory-codebase",
        "skill:localize-client-artifact",
        "skill:maintain-project-memory",
        "skill:manage-project-delivery",
        "skill:mutation-testing",
        "skill:plan-work",
        "skill:protect-git-work",
        "skill:review-code-change",
        "skill:review-openspec-change",
        "skill:review-privacy-security",
        "skill:sales-storytelling",
        "skill:specify-openspec-change",
        "skill:test-driven-development",
        "skill:validate-visual-artifact",
        "skill:verify-openspec-implementation",
        "template:acceptance-audit-template",
        "template:bilingual-artifact-runtime",
        "template:dashboard-data-example",
        "template:dashboard-shell",
        "template:dashboard-structure",
        "template:diagram-model-example",
        "template:editorial-html-shell",
        "template:evidence-record-example",
        "template:localization-manifest-example",
        "template:project-instructions-template",
        "template:project-memory-template-set",
        "template:requirement-record-example",
        "template:sales-narrative-template",
        "template:visual-pattern-guidance",
        "tool:analyze-project-delivery",
        "tool:anonymize-structured-data",
        "tool:audit-trace-graph",
        "tool:audit-trace-matrix",
        "tool:build-dashboard",
        "tool:calculate-project-financial-forecast",
        "tool:inventory-codebase-tool",
        "tool:manage-project-memory",
        "tool:rank-ready-slices",
        "tool:resolve-project-continuation",
        "tool:validate-client-localization",
        "tool:validate-dashboard-structure",
        "tool:validate-dashboard-visual",
        "tool:validate-diagram-model",
        "tool:validate-html"
      ],
      "archetypes": []
    },
    {
      "key": "overlay:architecture-documentation",
      "id": "architecture-documentation",
      "name": "Architecture documentation and technical diagrams",
      "type": "overlay",
      "path": "archetypes/overlays/architecture-documentation/overlay.yaml",
      "description": "Add evidence-backed architecture views with explicit scope, abstraction, editable source, rendered output, and semantic plus visual validation.",
      "purpose": "Add evidence-backed architecture views with explicit scope, abstraction, editable source, rendered output, and semantic plus visual validation.",
      "use_when": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ],
      "not_when": [],
      "inputs": [
        "architecture documentation purpose, audience, current/target/transition state, and scope",
        "required system, component, class, ER, sequence, data-flow, or migration-roadmap views",
        "documentation, dashboard, presentation, source-analysis, and standalone/offline destinations"
      ],
      "workflow": [
        "system-landscape-view",
        "component-architecture-view",
        "class-model-view",
        "er-data-model-view",
        "sequence-interaction-view",
        "data-flow-view",
        "migration-roadmap-view"
      ],
      "outputs": [
        "architecture view brief and evidence index",
        "editable diagram source and rendered artifacts",
        "overview and drilldowns for large models",
        "semantic and visual validation evidence"
      ],
      "validation": [],
      "tags": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ],
      "search_terms": [
        "Architecture documentation and technical diagrams",
        "architecture-documentation",
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "{\n  \"schema_version\": 1,\n  \"id\": \"architecture-documentation\",\n  \"kind\": \"overlay\",\n  \"title\": \"Architecture documentation and technical diagrams\",\n  \"purpose\": \"Add evidence-backed architecture views with explicit scope, abstraction, editable source, rendered output, and semantic plus visual validation.\",\n  \"compatible_archetypes\": [\n    \"development\",\n    \"legacy-migration\",\n    \"presentation\",\n    \"research\"\n  ],\n  \"initialization\": {\n    \"ask_if_unresolved\": [\n      \"architecture documentation purpose, audience, current/target/transition state, and scope\",\n      \"required system, component, class, ER, sequence, data-flow, or migration-roadmap views\",\n      \"documentation, dashboard, presentation, source-analysis, and standalone/offline destinations\"\n    ]\n  },\n  \"capabilities\": {\n    \"required\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    },\n    \"default\": {\n      \"skills\": [\n        \"create-technical-diagram\"\n      ],\n      \"agents\": [],\n      \"tools\": [\n        \"validate-diagram-model\"\n      ],\n      \"templates\": [\n        \"diagram-model-example\",\n        \"visual-pattern-guidance\"\n      ]\n    },\n    \"recommended\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    },\n    \"optional\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    }\n  },\n  \"conditions\": [\n    {\n      \"id\": \"system-landscape-view\",\n      \"when\": \"applications, systems, actors, scope, lifecycle state, or integrations must be shown\",\n      \"capabilities\": {\n        \"skills\": [\n          \"create-system-landscape-diagram\"\n        ],\n        \"agents\": [],\n        \"tools\": [],\n        \"templates\": []\n      }\n    },\n    {\n      \"id\": \"component-architecture-view\",\n      \"when\": \"containers, modules, services, components, owned data, or dependencies must be shown\",\n      \"capabilities\": {\n        \"skills\": [\n          \"create-component-architecture-diagram\"\n        ],\n        \"agents\": [],\n        \"tools\": [],\n        \"templates\": []\n      }\n    },\n    {\n      \"id\": \"class-model-view\",\n      \"when\": \"selected classes, interfaces, inheritance, composition, or domain relationships must be shown\",\n      \"capabilities\": {\n        \"skills\": [\n          \"create-class-diagram\"\n        ],\n        \"agents\": [],\n        \"tools\": [],\n        \"templates\": []\n      }\n    },\n    {\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "skill:create-class-diagram",
        "skill:create-component-architecture-diagram",
        "skill:create-data-flow-diagram",
        "skill:create-er-diagram",
        "skill:create-sequence-diagram",
        "skill:create-system-landscape-diagram",
        "skill:create-technical-diagram",
        "skill:plan-work",
        "template:diagram-model-example",
        "template:visual-pattern-guidance",
        "tool:validate-diagram-model"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "overlay:bilingual-client-delivery",
      "id": "bilingual-client-delivery",
      "name": "Bilingual client delivery",
      "type": "overlay",
      "path": "archetypes/overlays/bilingual-client-delivery/overlay.yaml",
      "description": "Keep internal HTML work lightweight and English-first while delivering one offline German/English client artifact with a persistent accessible language switch and bilingual QA. Public-sector dashboards select this automatically; public-sector sales presentations select it only by explicit bilingual override.",
      "purpose": "Keep internal HTML work lightweight and English-first while delivering one offline German/English client artifact with a persistent accessible language switch and bilingual QA. Public-sector dashboards select this automatically; public-sector sales presentations select it only by explicit bilingual override.",
      "use_when": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ],
      "not_when": [],
      "inputs": [
        "working language, client-facing language, whether both languages must remain available, and client default",
        "client glossary or established terminology, offline constraint, and language-selection persistence"
      ],
      "workflow": [],
      "outputs": [
        "one bilingual standalone HTML artifact",
        "English and locale-appropriate German localization data with freshness hashes",
        "accessible persistent language control",
        "semantic and bilingual visual-validation evidence"
      ],
      "validation": [],
      "tags": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ],
      "search_terms": [
        "Bilingual client delivery",
        "bilingual-client-delivery",
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "{\n  \"schema_version\": 1,\n  \"id\": \"bilingual-client-delivery\",\n  \"kind\": \"overlay\",\n  \"title\": \"Bilingual client delivery\",\n  \"purpose\": \"Keep internal HTML work lightweight and English-first while delivering one offline German/English client artifact with a persistent accessible language switch and bilingual QA. Public-sector dashboards select this automatically; public-sector sales presentations select it only by explicit bilingual override.\",\n  \"compatible_archetypes\": [\n    \"development\",\n    \"legacy-migration\",\n    \"presentation\",\n    \"research\"\n  ],\n  \"initialization\": {\n    \"ask_if_unresolved\": [\n      \"working language, client-facing language, whether both languages must remain available, and client default\",\n      \"client glossary or established terminology, offline constraint, and language-selection persistence\"\n    ]\n  },\n  \"configuration\": {\n    \"working_language\": \"en\",\n    \"languages\": [\n      \"resolved-German-locale\",\n      \"en\"\n    ],\n    \"client_default\": \"resolved-German-locale\",\n    \"offline\": true,\n    \"persistence\": \"localStorage-with-safe-fallback\"\n  },\n  \"capabilities\": {\n    \"required\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    },\n    \"default\": {\n      \"skills\": [\n        \"localize-client-artifact\",\n        \"validate-visual-artifact\"\n      ],\n      \"agents\": [],\n      \"tools\": [\n        \"validate-client-localization\",\n        \"validate-html\"\n      ],\n      \"templates\": [\n        \"bilingual-artifact-runtime\",\n        \"localization-manifest-example\"\n      ]\n    },\n    \"recommended\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    },\n    \"optional\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    }\n  },\n  \"conditions\": [],\n  \"outputs\": [\n    \"one bilingual standalone HTML artifact\",\n    \"English and locale-appropriate German localization data with freshness hashes\",\n    \"accessible persistent language control\",\n    \"semantic and bilingual visual-validation evidence\"\n  ]\n}",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "skill:localize-client-artifact",
        "skill:validate-visual-artifact",
        "template:bilingual-artifact-runtime",
        "template:localization-manifest-example",
        "tool:validate-client-localization",
        "tool:validate-html"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "overlay:branded-html",
      "id": "branded-html",
      "name": "Branded HTML artifact",
      "type": "overlay",
      "path": "archetypes/overlays/branded-html/overlay.yaml",
      "description": "Add URL-resolved brand evidence, exact offline official assets, shared dashboard/presentation rendering, an Accenture fallback when branding is unavailable, mandatory HTML construction, and independent fidelity QA.",
      "purpose": "Add URL-resolved brand evidence, exact offline official assets, shared dashboard/presentation rendering, an Accenture fallback when branding is unavailable, mandatory HTML construction, and independent fidelity QA.",
      "use_when": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ],
      "not_when": [],
      "inputs": [
        "artifact audience and decision",
        "brand sources and asset rights",
        "interaction, offline, print, and accessibility requirements"
      ],
      "workflow": [],
      "outputs": [
        "version-2 brand profile or recorded unresolved brand source",
        "exact offline brand assets when resolved",
        "mandatory HTML artifact",
        "Accenture fallback when branding is absent or unavailable",
        "separate static, profile-consistency, fidelity, and browser QA evidence"
      ],
      "validation": [],
      "tags": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ],
      "search_terms": [
        "Branded HTML artifact",
        "branded-html",
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "{\n  \"schema_version\": 1,\n  \"id\": \"branded-html\",\n  \"kind\": \"overlay\",\n  \"title\": \"Branded HTML artifact\",\n  \"purpose\": \"Add URL-resolved brand evidence, exact offline official assets, shared dashboard/presentation rendering, an Accenture fallback when branding is unavailable, mandatory HTML construction, and independent fidelity QA.\",\n  \"compatible_archetypes\": [\n    \"development\",\n    \"legacy-migration\",\n    \"presentation\",\n    \"research\"\n  ],\n  \"initialization\": {\n    \"ask_if_unresolved\": [\n      \"artifact audience and decision\",\n      \"brand sources and asset rights\",\n      \"interaction, offline, print, and accessibility requirements\"\n    ]\n  },\n  \"capabilities\": {\n    \"required\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    },\n    \"default\": {\n      \"skills\": [\n        \"create-branded-html-artifact\",\n        \"validate-visual-artifact\"\n      ],\n      \"agents\": [],\n      \"tools\": [\n        \"validate-html\"\n      ],\n      \"templates\": [\n        \"editorial-html-shell\"\n      ]\n    },\n    \"recommended\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    },\n    \"optional\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    }\n  },\n  \"conditions\": [],\n  \"outputs\": [\n    \"version-2 brand profile or recorded unresolved brand source\",\n    \"exact offline brand assets when resolved\",\n    \"mandatory HTML artifact\",\n    \"Accenture fallback when branding is absent or unavailable\",\n    \"separate static, profile-consistency, fidelity, and browser QA evidence\"\n  ]\n}",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "skill:create-branded-html-artifact",
        "skill:validate-visual-artifact",
        "template:editorial-html-shell",
        "tool:validate-html"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "overlay:consulting-delivery",
      "id": "consulting-delivery",
      "name": "Consulting delivery controls",
      "type": "overlay",
      "path": "archetypes/overlays/consulting-delivery/overlay.yaml",
      "description": "Add evidence-based project-delivery governance and financial forecasting without embedding organization-specific operating models.",
      "purpose": "Add evidence-based project-delivery governance and financial forecasting without embedding organization-specific operating models.",
      "use_when": [
        "development",
        "legacy-migration",
        "research"
      ],
      "not_when": [],
      "inputs": [
        "authoritative schedule and financial sources, reporting period, governance cadence, currency and units, scenario assumptions, and approval boundary"
      ],
      "workflow": [],
      "outputs": [
        "delivery health and dependency view",
        "RAID and action view",
        "scenario-based project financial forecast",
        "independent forecast findings"
      ],
      "validation": [
        "organization-specific role names, branding, rate cards, commercial thresholds, approval routes, and client identifiers remain project-local",
        "delivery status and forecast claims identify their source period and assumptions",
        "the independent reviewer reports findings and does not grant commercial approval"
      ],
      "tags": [
        "development",
        "legacy-migration",
        "research"
      ],
      "search_terms": [
        "Consulting delivery controls",
        "consulting-delivery",
        "development",
        "legacy-migration",
        "research"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "{\n  \"schema_version\": 1,\n  \"id\": \"consulting-delivery\",\n  \"kind\": \"overlay\",\n  \"title\": \"Consulting delivery controls\",\n  \"purpose\": \"Add evidence-based project-delivery governance and financial forecasting without embedding organization-specific operating models.\",\n  \"compatible_archetypes\": [\n    \"development\",\n    \"legacy-migration\",\n    \"research\"\n  ],\n  \"initialization\": {\n    \"ask_if_unresolved\": [\n      \"authoritative schedule and financial sources, reporting period, governance cadence, currency and units, scenario assumptions, and approval boundary\"\n    ]\n  },\n  \"capabilities\": {\n    \"required\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    },\n    \"default\": {\n      \"skills\": [\n        \"manage-project-delivery\",\n        \"forecast-project-financials\"\n      ],\n      \"agents\": [\n        \"financial-forecast-reviewer\"\n      ],\n      \"tools\": [\n        \"analyze-project-delivery\",\n        \"calculate-project-financial-forecast\"\n      ],\n      \"templates\": []\n    },\n    \"recommended\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    },\n    \"optional\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    }\n  },\n  \"conditions\": [],\n  \"invariants\": [\n    \"organization-specific role names, branding, rate cards, commercial thresholds, approval routes, and client identifiers remain project-local\",\n    \"delivery status and forecast claims identify their source period and assumptions\",\n    \"the independent reviewer reports findings and does not grant commercial approval\"\n  ],\n  \"outputs\": [\n    \"delivery health and dependency view\",\n    \"RAID and action view\",\n    \"scenario-based project financial forecast\",\n    \"independent forecast findings\"\n  ]\n}",
      "related_capabilities": [
        "agent:financial-forecast-reviewer",
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:research",
        "skill:forecast-project-financials",
        "skill:manage-project-delivery",
        "tool:analyze-project-delivery",
        "tool:calculate-project-financial-forecast"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "research"
      ]
    },
    {
      "key": "overlay:durable-state",
      "id": "durable-state",
      "name": "Durable project state",
      "type": "overlay",
      "path": "archetypes/overlays/durable-state/overlay.yaml",
      "description": "Add concise repository-native memory for substantial multi-session or coordinated work.",
      "purpose": "Add concise repository-native memory for substantial multi-session or coordinated work.",
      "use_when": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ],
      "not_when": [],
      "inputs": [
        "recovery cost, expected duration, coordination boundary, and canonical state sources"
      ],
      "workflow": [],
      "outputs": [
        "L0 project synopsis",
        "L1 domain indexes",
        "L2 entity records",
        "evidence pointers",
        "validated checkpoints",
        "bounded context packages"
      ],
      "validation": [],
      "tags": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ],
      "search_terms": [
        "development",
        "Durable project state",
        "durable-state",
        "legacy-migration",
        "presentation",
        "research"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "{\n  \"schema_version\": 1,\n  \"id\": \"durable-state\",\n  \"kind\": \"overlay\",\n  \"title\": \"Durable project state\",\n  \"purpose\": \"Add concise repository-native memory for substantial multi-session or coordinated work.\",\n  \"compatible_archetypes\": [\n    \"development\",\n    \"legacy-migration\",\n    \"presentation\",\n    \"research\"\n  ],\n  \"initialization\": {\n    \"ask_if_unresolved\": [\n      \"recovery cost, expected duration, coordination boundary, and canonical state sources\"\n    ]\n  },\n  \"capabilities\": {\n    \"required\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    },\n    \"default\": {\n      \"skills\": [\n        \"maintain-project-memory\"\n      ],\n      \"agents\": [],\n      \"tools\": [\n        \"manage-project-memory\"\n      ],\n      \"templates\": [\n        \"project-memory-template-set\"\n      ]\n    },\n    \"recommended\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    },\n    \"optional\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    }\n  },\n  \"conditions\": [],\n  \"outputs\": [\n    \"L0 project synopsis\",\n    \"L1 domain indexes\",\n    \"L2 entity records\",\n    \"evidence pointers\",\n    \"validated checkpoints\",\n    \"bounded context packages\"\n  ]\n}",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "skill:maintain-project-memory",
        "template:project-memory-template-set",
        "tool:manage-project-memory"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "overlay:evidence-traceability",
      "id": "evidence-traceability",
      "name": "Evidence and traceability",
      "type": "overlay",
      "path": "archetypes/overlays/evidence-traceability/overlay.yaml",
      "description": "Add durable evidence-to-requirement records and an independent delivery-chain audit.",
      "purpose": "Add durable evidence-to-requirement records and an independent delivery-chain audit.",
      "use_when": [
        "development",
        "legacy-migration",
        "research"
      ],
      "not_when": [],
      "inputs": [
        "authoritative sources, required evidence granularity, lifecycle states, approval boundary, and independent verification expectations"
      ],
      "workflow": [],
      "outputs": [
        "stable evidence and requirement records",
        "reciprocal lifecycle links",
        "independent completeness audit"
      ],
      "validation": [],
      "tags": [
        "development",
        "legacy-migration",
        "research"
      ],
      "search_terms": [
        "development",
        "Evidence and traceability",
        "evidence-traceability",
        "legacy-migration",
        "research"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "{\n  \"schema_version\": 1,\n  \"id\": \"evidence-traceability\",\n  \"kind\": \"overlay\",\n  \"title\": \"Evidence and traceability\",\n  \"purpose\": \"Add durable evidence-to-requirement records and an independent delivery-chain audit.\",\n  \"compatible_archetypes\": [\n    \"development\",\n    \"legacy-migration\",\n    \"research\"\n  ],\n  \"initialization\": {\n    \"ask_if_unresolved\": [\n      \"authoritative sources, required evidence granularity, lifecycle states, approval boundary, and independent verification expectations\"\n    ]\n  },\n  \"capabilities\": {\n    \"required\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    },\n    \"default\": {\n      \"skills\": [\n        \"derive-modernization-requirements\",\n        \"audit-delivery-traceability\"\n      ],\n      \"agents\": [],\n      \"tools\": [\n        \"audit-trace-matrix\",\n        \"audit-trace-graph\"\n      ],\n      \"templates\": [\n        \"evidence-record-example\",\n        \"requirement-record-example\",\n        \"acceptance-audit-template\"\n      ]\n    },\n    \"recommended\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    },\n    \"optional\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    }\n  },\n  \"conditions\": [],\n  \"outputs\": [\n    \"stable evidence and requirement records\",\n    \"reciprocal lifecycle links\",\n    \"independent completeness audit\"\n  ]\n}",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:research",
        "skill:audit-delivery-traceability",
        "skill:derive-modernization-requirements",
        "template:acceptance-audit-template",
        "template:evidence-record-example",
        "template:requirement-record-example",
        "tool:audit-trace-graph",
        "tool:audit-trace-matrix"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "research"
      ]
    },
    {
      "key": "overlay:living-dashboard",
      "id": "living-dashboard",
      "name": "Living dashboard",
      "type": "overlay",
      "path": "archetypes/overlays/living-dashboard/overlay.yaml",
      "description": "Add a deterministic read-only stakeholder view generated from canonical project state.",
      "purpose": "Add a deterministic read-only stakeholder view generated from canonical project state.",
      "use_when": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ],
      "not_when": [],
      "inputs": [
        "canonical data source, dashboard audience when visibility materially differs, decisions supported, brand, language, refresh trigger, and drift gate"
      ],
      "workflow": [],
      "outputs": [
        "canonical dashboard data",
        "canonical section profile",
        "generated read-only HTML",
        "structural drift and visual validation evidence"
      ],
      "validation": [
        "instantiate the canonical living-dashboard structure rather than inventing a project layout",
        "full legacy-modernization renders every standard section; archetypes determine applicability without redefining order",
        "project-specific sections use controlled extension points",
        "branding and localization remain presentation-layer configuration with exact asset and fidelity validation",
        "VALIDATED requires matching structure static brand visual accessibility and localization QA evidence where applicable"
      ],
      "tags": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ],
      "search_terms": [
        "development",
        "legacy-migration",
        "Living dashboard",
        "living-dashboard",
        "presentation",
        "research"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "{\n  \"schema_version\": 1,\n  \"id\": \"living-dashboard\",\n  \"kind\": \"overlay\",\n  \"title\": \"Living dashboard\",\n  \"purpose\": \"Add a deterministic read-only stakeholder view generated from canonical project state.\",\n  \"compatible_archetypes\": [\n    \"development\",\n    \"legacy-migration\",\n    \"presentation\",\n    \"research\"\n  ],\n  \"initialization\": {\n    \"ask_if_unresolved\": [\n      \"canonical data source, dashboard audience when visibility materially differs, decisions supported, brand, language, refresh trigger, and drift gate\"\n    ],\n    \"known_defaults\": [\n      \"canonical Agent Commons section hierarchy and order\",\n      \"five-domain grouped navigation with mobile bottom adaptation\",\n      \"shared detail-dialog interaction family\",\n      \"honest pending, not-observed, and not-applicable states for standard sections\"\n    ]\n  },\n  \"capabilities\": {\n    \"required\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    },\n    \"default\": {\n      \"skills\": [\n        \"build-living-dashboard\",\n        \"validate-visual-artifact\",\n        \"accessibility-review\"\n      ],\n      \"agents\": [],\n      \"tools\": [\n        \"build-dashboard\",\n        \"validate-dashboard-structure\",\n        \"validate-dashboard-visual\",\n        \"validate-html\"\n      ],\n      \"templates\": [\n        \"dashboard-data-example\",\n        \"dashboard-structure\",\n        \"dashboard-shell\"\n      ]\n    },\n    \"recommended\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    },\n    \"optional\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    }\n  },\n  \"conditions\": [],\n  \"outputs\": [\n    \"canonical dashboard data\",\n    \"canonical section profile\",\n    \"generated read-only HTML\",\n    \"structural drift and visual validation evidence\"\n  ],\n  \"invariants\": [\n    \"instantiate the canonical living-dashboard structure rather than inventing a project layout\",\n    \"full legacy-modernization renders every standard section; archetypes determine applicability without redefining order\",\n    \"project-specific sections use controlled extension points\",\n    \"branding and localization remain presentation-layer configuration with exact asset and fidelity validation\",\n    \"VALIDATED requires matching structure static brand visual accessibility and localization QA evidence where applicable\"\n  ]\n}",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "skill:accessibility-review",
        "skill:build-living-dashboard",
        "skill:validate-visual-artifact",
        "template:dashboard-data-example",
        "template:dashboard-shell",
        "template:dashboard-structure",
        "tool:build-dashboard",
        "tool:validate-dashboard-structure",
        "tool:validate-dashboard-visual",
        "tool:validate-html"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "overlay:public-sector-client-delivery",
      "id": "public-sector-client-delivery",
      "name": "Public-sector client delivery",
      "type": "overlay",
      "path": "archetypes/overlays/public-sector-client-delivery/overlay.yaml",
      "description": "Apply evidence-based public-sector client classification, locale-aware German delivery defaults, client branding, restrained sales tone, accessibility, and output-specific validation without turning public sector into a project archetype.",
      "purpose": "Apply evidence-based public-sector client classification, locale-aware German delivery defaults, client branding, restrained sales tone, accessibility, and output-specific validation without turning public sector into a project archetype.",
      "use_when": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ],
      "not_when": [],
      "inputs": [
        "public-sector status only when evidence is genuinely uncertain and changes delivery",
        "client locale only when geography or an explicit language requirement cannot resolve it"
      ],
      "workflow": [],
      "outputs": [
        "persisted client-sector confidence, evidence, country, and locale",
        "separate dashboard and presentation language policies",
        "client-branded German-default bilingual dashboard when selected",
        "client-branded German-only sales presentation when selected",
        "identical official favicon, logo, palette, and brand fingerprints across localized outputs",
        "public-sector semantic, accessibility, and visual QA evidence"
      ],
      "validation": [],
      "tags": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ],
      "search_terms": [
        "development",
        "legacy-migration",
        "presentation",
        "Public-sector client delivery",
        "public-sector-client-delivery",
        "research"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "{\n  \"schema_version\": 1,\n  \"id\": \"public-sector-client-delivery\",\n  \"kind\": \"overlay\",\n  \"title\": \"Public-sector client delivery\",\n  \"purpose\": \"Apply evidence-based public-sector client classification, locale-aware German delivery defaults, client branding, restrained sales tone, accessibility, and output-specific validation without turning public sector into a project archetype.\",\n  \"compatible_archetypes\": [\n    \"development\",\n    \"legacy-migration\",\n    \"presentation\",\n    \"research\"\n  ],\n  \"initialization\": {\n    \"discover\": [\n      \"explicit client-sector statements, client organization, official website and corporate-design sources, geography, existing project manifest, and client terminology\"\n    ],\n    \"ask_if_unresolved\": [\n      \"public-sector status only when evidence is genuinely uncertain and changes delivery\",\n      \"client locale only when geography or an explicit language requirement cannot resolve it\"\n    ]\n  },\n  \"configuration\": {\n    \"confidence_levels\": [\n      \"CONFIRMED\",\n      \"HIGH_CONFIDENCE\",\n      \"UNCERTAIN\",\n      \"NOT_PUBLIC_SECTOR\"\n    ],\n    \"locale_by_country\": {\n      \"AT\": \"de-AT\",\n      \"DE\": \"de-DE\",\n      \"CH\": \"de-CH\"\n    },\n    \"dashboard\": {\n      \"german_default\": true,\n      \"english_available\": true,\n      \"language_switch\": true\n    },\n    \"sales_presentation\": {\n      \"german_only\": true,\n      \"bilingual\": false\n    },\n    \"precedence\": [\n      \"explicit-project-instruction\",\n      \"explicit-client-requirement\",\n      \"public-sector-client-default\",\n      \"archetype-default\",\n      \"neutral-commons-default\"\n    ]\n  },\n  \"capabilities\": {\n    \"required\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    },\n    \"default\": {\n      \"skills\": [\n        \"validate-visual-artifact\",\n        \"accessibility-review\"\n      ],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    },\n    \"recommended\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    },\n    \"optional\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    }\n  },\n  \"conditions\": [],\n  \"outputs\": [\n    \"persisted client-sector confidence, evidence, country, and locale\",\n    \"separate dashboard and presentation language policies\",\n    \"client-branded German-default bilingual dashboard when selected\",\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "skill:accessibility-review",
        "skill:validate-visual-artifact"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "overlay:sales-storytelling",
      "id": "sales-storytelling",
      "name": "Sales presentation storytelling",
      "type": "overlay",
      "path": "archetypes/overlays/sales-storytelling/overlay.yaml",
      "description": "Add evidence-backed persuasive narrative design, objection handling, differentiation, proof, a concrete call to action, and client-context-aware narrative language and tone.",
      "purpose": "Add evidence-backed persuasive narrative design, objection handling, differentiation, proof, a concrete call to action, and client-context-aware narrative language and tone.",
      "use_when": [
        "research",
        "presentation",
        "development",
        "legacy-migration"
      ],
      "not_when": [],
      "inputs": [
        "what is proposed, target audience or customer, desired next action, and likely problem",
        "known differentiators, objections, supporting proof, and which unknowns research should establish"
      ],
      "workflow": [],
      "outputs": [
        "audience and decision brief",
        "evidence-mapped sales narrative in the resolved presentation language",
        "objection and proof map",
        "call to action"
      ],
      "validation": [],
      "tags": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ],
      "search_terms": [
        "development",
        "legacy-migration",
        "presentation",
        "research",
        "Sales presentation storytelling",
        "sales-storytelling"
      ],
      "runtime_support": [
        "Claude Code",
        "Cline",
        "OpenAI Codex",
        "OpenCode"
      ],
      "source_preview": "{\n  \"schema_version\": 1,\n  \"id\": \"sales-storytelling\",\n  \"kind\": \"overlay\",\n  \"title\": \"Sales presentation storytelling\",\n  \"purpose\": \"Add evidence-backed persuasive narrative design, objection handling, differentiation, proof, a concrete call to action, and client-context-aware narrative language and tone.\",\n  \"compatible_archetypes\": [\n    \"research\",\n    \"presentation\",\n    \"development\",\n    \"legacy-migration\"\n  ],\n  \"initialization\": {\n    \"ask_if_unresolved\": [\n      \"what is proposed, target audience or customer, desired next action, and likely problem\",\n      \"known differentiators, objections, supporting proof, and which unknowns research should establish\"\n    ]\n  },\n  \"capabilities\": {\n    \"required\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    },\n    \"default\": {\n      \"skills\": [\n        \"sales-storytelling\"\n      ],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": [\n        \"sales-narrative-template\"\n      ]\n    },\n    \"recommended\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    },\n    \"optional\": {\n      \"skills\": [],\n      \"agents\": [],\n      \"tools\": [],\n      \"templates\": []\n    }\n  },\n  \"conditions\": [],\n  \"outputs\": [\n    \"audience and decision brief\",\n    \"evidence-mapped sales narrative in the resolved presentation language\",\n    \"objection and proof map\",\n    \"call to action\"\n  ]\n}",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "skill:sales-storytelling",
        "template:sales-narrative-template"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "adapter:claude-code",
      "id": "claude-code",
      "name": "Claude Code",
      "type": "adapter",
      "path": "adapters/claude-code/adapter.yaml",
      "description": "Maps canonical Agent Commons capabilities into Claude Code using verified native concepts and explicit limitations.",
      "purpose": "Managed settings, command line, local, project, user; project CLAUDE.md content follows user content and closer directory instructions load later.",
      "use_when": [
        "Expose canonical capabilities in Claude Code."
      ],
      "not_when": [
        "External CLAUDE.md imports can require trust approval; Windows symlinks may require Developer Mode or administrator privileges."
      ],
      "inputs": [],
      "workflow": [
        "global_instructions: native",
        "project_instructions: native-import-adapter",
        "skills: native",
        "custom_agents: native",
        "mcp: native",
        "project_memory: commons-project-local-with-native-memory-optimizations-optional",
        "archetypes: commons",
        "evals: commons"
      ],
      "outputs": [
        "skills: documented-symlink",
        "agents: generated-native",
        "global_instructions: managed-section"
      ],
      "validation": [
        "Verified on 2026-08-18"
      ],
      "tags": [
        "commons",
        "commons-project-local-with-native-memory-optimizations-optional",
        "native",
        "native-import-adapter"
      ],
      "search_terms": [
        "Claude Code",
        "claude-code",
        "commons",
        "commons-project-local-with-native-memory-optimizations-optional",
        "native",
        "native-import-adapter"
      ],
      "runtime_support": [],
      "source_preview": "{\n  \"schema_version\": 1,\n  \"id\": \"claude-code\",\n  \"display_name\": \"Claude Code\",\n  \"verified_on\": \"2026-08-18\",\n  \"documentation\": [\n    \"https://code.claude.com/docs/en/memory\",\n    \"https://code.claude.com/docs/en/skills\",\n    \"https://code.claude.com/docs/en/sub-agents\",\n    \"https://code.claude.com/docs/en/mcp\",\n    \"https://code.claude.com/docs/en/settings\"\n  ],\n  \"concepts\": {\n    \"global_instructions\": \"native\",\n    \"project_instructions\": \"native-import-adapter\",\n    \"skills\": \"native\",\n    \"custom_agents\": \"native\",\n    \"mcp\": \"native\",\n    \"project_memory\": \"commons-project-local-with-native-memory-optimizations-optional\",\n    \"archetypes\": \"commons\",\n    \"evals\": \"commons\"\n  },\n  \"installation\": {\n    \"skills\": \"documented-symlink\",\n    \"agents\": \"generated-native\",\n    \"global_instructions\": \"managed-section\"\n  },\n  \"user_paths\": {\n    \"global_instructions\": [\n      \".claude\",\n      \"CLAUDE.md\"\n    ],\n    \"skills\": [\n      \".claude\",\n      \"skills\"\n    ],\n    \"agents\": [\n      \".claude\",\n      \"agents\"\n    ]\n  },\n  \"project\": {\n    \"instructions\": \"CLAUDE.md importing AGENTS.md\",\n    \"agent_directory\": \".claude/agents\",\n    \"mcp\": \".mcp.json\",\n    \"settings\": \".claude/settings.json\"\n  },\n  \"precedence\": \"Managed settings, command line, local, project, user; project CLAUDE.md content follows user content and closer directory instructions load later.\",\n  \"limitations\": [\n    \"External CLAUDE.md imports can require trust approval; Windows symlinks may require Developer Mode or administrator privileges.\"\n  ]\n}",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "adapter:cline",
      "id": "cline",
      "name": "Cline",
      "type": "adapter",
      "path": "adapters/cline/adapter.yaml",
      "description": "Maps canonical Agent Commons capabilities into Cline using verified native concepts and explicit limitations.",
      "purpose": "Workspace rules override conflicting global rules; global skills override project skills with the same name.",
      "use_when": [
        "Expose canonical capabilities in Cline."
      ],
      "not_when": [
        "The documented subagent feature is experimental and exposes read-only research workers, not reusable custom subagent definitions.",
        "Official documentation does not promise symlinked skill discovery, so the adapter generates wrappers instead."
      ],
      "inputs": [],
      "workflow": [
        "global_instructions: native",
        "project_instructions: native",
        "skills: native",
        "custom_agents: mapped-to-skill",
        "mcp: native",
        "project_memory: commons-project-local",
        "archetypes: commons",
        "evals: commons"
      ],
      "outputs": [
        "skills: generated-thin-wrapper",
        "agents: generated-role-skill",
        "global_instructions: managed-section"
      ],
      "validation": [
        "Verified on 2026-08-18"
      ],
      "tags": [
        "commons",
        "commons-project-local",
        "mapped-to-skill",
        "native"
      ],
      "search_terms": [
        "Cline",
        "cline",
        "commons",
        "commons-project-local",
        "mapped-to-skill",
        "native"
      ],
      "runtime_support": [],
      "source_preview": "{\n  \"schema_version\": 1,\n  \"id\": \"cline\",\n  \"display_name\": \"Cline\",\n  \"verified_on\": \"2026-08-18\",\n  \"documentation\": [\n    \"https://docs.cline.bot/customization/cline-rules\",\n    \"https://docs.cline.bot/customization/skills\",\n    \"https://docs.cline.bot/features/subagents\",\n    \"https://docs.cline.bot/mcp/mcp-overview\",\n    \"https://docs.cline.bot/getting-started/config\"\n  ],\n  \"concepts\": {\n    \"global_instructions\": \"native\",\n    \"project_instructions\": \"native\",\n    \"skills\": \"native\",\n    \"custom_agents\": \"mapped-to-skill\",\n    \"mcp\": \"native\",\n    \"project_memory\": \"commons-project-local\",\n    \"archetypes\": \"commons\",\n    \"evals\": \"commons\"\n  },\n  \"installation\": {\n    \"skills\": \"generated-thin-wrapper\",\n    \"agents\": \"generated-role-skill\",\n    \"global_instructions\": \"managed-section\"\n  },\n  \"user_paths\": {\n    \"global_instructions\": [\n      \".agents\",\n      \"AGENTS.md\"\n    ],\n    \"skills\": [\n      \".cline\",\n      \"skills\"\n    ],\n    \"agents\": [\n      \".cline\",\n      \"skills\"\n    ]\n  },\n  \"project\": {\n    \"instructions\": \"AGENTS.md\",\n    \"skills\": \".cline/skills\",\n    \"rules\": \".clinerules\",\n    \"mcp\": \"~/.cline/mcp.json for CLI or the IDE-managed MCP settings file\"\n  },\n  \"precedence\": \"Workspace rules override conflicting global rules; global skills override project skills with the same name.\",\n  \"limitations\": [\n    \"The documented subagent feature is experimental and exposes read-only research workers, not reusable custom subagent definitions.\",\n    \"Official documentation does not promise symlinked skill discovery, so the adapter generates wrappers instead.\"\n  ]\n}",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "adapter:codex",
      "id": "codex",
      "name": "OpenAI Codex",
      "type": "adapter",
      "path": "adapters/codex/adapter.yaml",
      "description": "Maps canonical Agent Commons capabilities into OpenAI Codex using verified native concepts and explicit limitations.",
      "purpose": "CLI, closest trusted project config, profile, user config, system config, defaults; AGENTS.md is concatenated from global then project root toward the working directory.",
      "use_when": [
        "Expose canonical capabilities in OpenAI Codex."
      ],
      "not_when": [],
      "inputs": [],
      "workflow": [
        "global_instructions: native",
        "project_instructions: native",
        "skills: native",
        "custom_agents: native",
        "mcp: native",
        "project_memory: commons-project-local-with-native-context-optimizations-optional",
        "archetypes: commons",
        "evals: commons"
      ],
      "outputs": [
        "skills: documented-symlink",
        "agents: generated-native",
        "global_instructions: managed-section"
      ],
      "validation": [
        "Verified on 2026-08-18"
      ],
      "tags": [
        "commons",
        "commons-project-local-with-native-context-optimizations-optional",
        "native"
      ],
      "search_terms": [
        "codex",
        "commons",
        "commons-project-local-with-native-context-optimizations-optional",
        "native",
        "OpenAI Codex"
      ],
      "runtime_support": [],
      "source_preview": "{\n  \"schema_version\": 1,\n  \"id\": \"codex\",\n  \"display_name\": \"OpenAI Codex\",\n  \"verified_on\": \"2026-08-18\",\n  \"documentation\": [\n    \"https://learn.chatgpt.com/docs/agent-configuration/agents-md\",\n    \"https://learn.chatgpt.com/docs/build-skills\",\n    \"https://learn.chatgpt.com/docs/agent-configuration/subagents\",\n    \"https://learn.chatgpt.com/docs/extend/mcp\",\n    \"https://learn.chatgpt.com/docs/config-file/config-basic#configuration-precedence\"\n  ],\n  \"concepts\": {\n    \"global_instructions\": \"native\",\n    \"project_instructions\": \"native\",\n    \"skills\": \"native\",\n    \"custom_agents\": \"native\",\n    \"mcp\": \"native\",\n    \"project_memory\": \"commons-project-local-with-native-context-optimizations-optional\",\n    \"archetypes\": \"commons\",\n    \"evals\": \"commons\"\n  },\n  \"installation\": {\n    \"skills\": \"documented-symlink\",\n    \"agents\": \"generated-native\",\n    \"global_instructions\": \"managed-section\"\n  },\n  \"user_paths\": {\n    \"global_instructions\": [\n      \".codex\",\n      \"AGENTS.md\"\n    ],\n    \"skills\": [\n      \".agents\",\n      \"skills\"\n    ],\n    \"agents\": [\n      \".codex\",\n      \"agents\"\n    ]\n  },\n  \"project\": {\n    \"instructions\": \"AGENTS.md\",\n    \"agent_directory\": \".codex/agents\",\n    \"config\": \".codex/config.toml\"\n  },\n  \"precedence\": \"CLI, closest trusted project config, profile, user config, system config, defaults; AGENTS.md is concatenated from global then project root toward the working directory.\",\n  \"limitations\": []\n}",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "adapter:opencode",
      "id": "opencode",
      "name": "OpenCode",
      "type": "adapter",
      "path": "adapters/opencode/adapter.yaml",
      "description": "Maps canonical Agent Commons capabilities into OpenCode using verified native concepts and explicit limitations.",
      "purpose": "Remote, global, custom, project, .opencode directories, inline, managed files, managed preferences; later configuration overrides conflicting keys.",
      "use_when": [
        "Expose canonical capabilities in OpenCode."
      ],
      "not_when": [
        "Official documentation lists Agent Skills compatibility paths but does not promise symlink behavior, so the adapter generates wrappers instead."
      ],
      "inputs": [],
      "workflow": [
        "global_instructions: native",
        "project_instructions: native",
        "skills: native",
        "custom_agents: native",
        "mcp: native",
        "project_memory: commons-project-local",
        "archetypes: commons",
        "evals: commons"
      ],
      "outputs": [
        "skills: generated-thin-wrapper",
        "agents: generated-native",
        "global_instructions: managed-section"
      ],
      "validation": [
        "Verified on 2026-08-18"
      ],
      "tags": [
        "commons",
        "commons-project-local",
        "native"
      ],
      "search_terms": [
        "commons",
        "commons-project-local",
        "native",
        "OpenCode",
        "opencode"
      ],
      "runtime_support": [],
      "source_preview": "{\n  \"schema_version\": 1,\n  \"id\": \"opencode\",\n  \"display_name\": \"OpenCode\",\n  \"verified_on\": \"2026-08-18\",\n  \"documentation\": [\n    \"https://opencode.ai/docs/rules\",\n    \"https://opencode.ai/docs/skills\",\n    \"https://opencode.ai/docs/agents\",\n    \"https://opencode.ai/docs/config\",\n    \"https://opencode.ai/docs/mcp-servers\"\n  ],\n  \"concepts\": {\n    \"global_instructions\": \"native\",\n    \"project_instructions\": \"native\",\n    \"skills\": \"native\",\n    \"custom_agents\": \"native\",\n    \"mcp\": \"native\",\n    \"project_memory\": \"commons-project-local\",\n    \"archetypes\": \"commons\",\n    \"evals\": \"commons\"\n  },\n  \"installation\": {\n    \"skills\": \"generated-thin-wrapper\",\n    \"agents\": \"generated-native\",\n    \"global_instructions\": \"managed-section\"\n  },\n  \"user_paths\": {\n    \"global_instructions\": [\n      \".config\",\n      \"opencode\",\n      \"AGENTS.md\"\n    ],\n    \"skills\": [\n      \".config\",\n      \"opencode\",\n      \"skills\"\n    ],\n    \"agents\": [\n      \".config\",\n      \"opencode\",\n      \"agents\"\n    ]\n  },\n  \"project\": {\n    \"instructions\": \"AGENTS.md\",\n    \"skills\": \".opencode/skills\",\n    \"agents\": \".opencode/agents\",\n    \"config\": \"opencode.json\"\n  },\n  \"precedence\": \"Remote, global, custom, project, .opencode directories, inline, managed files, managed preferences; later configuration overrides conflicting keys.\",\n  \"limitations\": [\n    \"Official documentation lists Agent Skills compatibility paths but does not promise symlink behavior, so the adapter generates wrappers instead.\"\n  ]\n}",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "eval:agent-evaluations",
      "id": "agent-evaluations",
      "name": "Agent evaluations",
      "type": "eval",
      "path": "evals/agents/scenarios.yaml",
      "description": "Canonical evaluation scenarios for agent evaluations.",
      "purpose": "Validate expected behavior, invariants, and failure cases for agent evaluations.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [
        "architecture-reviewer",
        "legacy-discovery-specialist",
        "privacy-security-reviewer",
        "test-behavior-reviewer",
        "financial-forecast-reviewer"
      ],
      "outputs": [
        "positive, negative, ambiguous, invariant, and failure evidence where declared"
      ],
      "validation": [],
      "tags": [
        "architecture-reviewer",
        "financial-forecast-reviewer",
        "legacy-discovery-specialist",
        "privacy-security-reviewer",
        "test-behavior-reviewer"
      ],
      "search_terms": [
        "Agent evaluations",
        "agent-evaluations",
        "architecture-reviewer",
        "financial-forecast-reviewer",
        "legacy-discovery-specialist",
        "privacy-security-reviewer",
        "test-behavior-reviewer"
      ],
      "runtime_support": [],
      "source_preview": "version: 1\nagents:\n  architecture-reviewer:\n    positive: \"Independently challenge this consequential architecture proposal against requirements, decisions, quality attributes, and validation evidence.\"\n    negative: \"Redesign the system, implement the preferred architecture, and approve release from the reviewer role.\"\n    ambiguous: \"Review the architecture\" # coordinator must supply scope, evidence, decisions, constraints, validation, and output boundary\n    expected: [\"evidence map\", \"assumptions conflicts and unknowns\", \"severity findings\", \"affected quality attributes\", \"failure paths\", \"decision-owner questions\", \"limitations\"]\n    invariants: [\"findings only\", \"preferences are not defects\", \"requirements are not invented\", \"reviewer does not own target design\"]\n    failures: [\"implementation edits\", \"new target architecture substituted for review\", \"unsupported claims accepted\", \"release approval\"]\n  legacy-discovery-specialist:\n    positive: \"Analyze one exclusive 40-file COBOL batch and return isolated evidence records.\"\n    negative: \"Let the worker update shared registries and dashboard totals directly.\"\n    ambiguous: \"Explore the whole legacy estate\" # coordinator must bound batches first\n    expected: [\"worker manifest\", \"paths and hashes\", \"temporary IDs\", \"validation result\"]\n    invariants: [\"no canonical edits\", \"no scope expansion\"]\n    failures: [\"overlapping batch ownership\", \"unreviewed worker output promoted\"]\n  privacy-security-reviewer:\n    positive: \"Independently challenge a consequential change's privacy and security evidence in a fresh context.\"\n    negative: \"Implement the fixes and approve release from the same reviewer role.\"\n    ambiguous: \"Check security\" # coordinator must supply bounded scope, evidence, data classes, and output path\n    expected: [\"data and trust-boundary map\", \"abuse paths\", \"severity findings\", \"residual risk\", \"limitations\"]\n    invariants: [\"findings only\", \"no sensitive values in output\", \"no compliance certification\"]\n    failures: [\"implementation edits\", \"unsupported control claims accepted\", \"release approval\"]\n  test-behavior-reviewer:\n    positive: \"Independently assess whether RED GREEN and full-gate evidence demonstrate the accepted behavior.\"\n    negative: \"Rewrite the tests and production code while calling the result independent review.\"\n… preview truncated",
      "related_capabilities": [
        "agent:architecture-reviewer",
        "agent:financial-forecast-reviewer",
        "agent:legacy-discovery-specialist",
        "agent:privacy-security-reviewer",
        "agent:test-behavior-reviewer"
      ],
      "archetypes": []
    },
    {
      "key": "eval:archetype-evaluations",
      "id": "archetype-evaluations",
      "name": "Archetype evaluations",
      "type": "eval",
      "path": "evals/archetypes/scenarios.yaml",
      "description": "Canonical evaluation scenarios for archetype evaluations.",
      "purpose": "Validate expected behavior, invariants, and failure cases for archetype evaluations.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [
        "positive, negative, ambiguous, invariant, and failure evidence where declared"
      ],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Archetype evaluations",
        "archetype-evaluations"
      ],
      "runtime_support": [],
      "source_preview": "version: 1\nscenarios:\n  - id: development-only\n    expected: [OpenSpec specification before implementation, canonical TDD, verification, no legacy analysis, no presentation behavior]\n  - id: development-no-openspec\n    expected: [explicit OpenSpec exclusion recorded, OpenSpec family absent, TDD retained]\n  - id: development-no-tdd\n    expected: [explicit TDD exclusion recorded, OpenSpec family retained, no false TDD claim]\n  - id: legacy-requirements-only\n    expected: [inventory, analysis, evidence-backed requirements, no implementation specification]\n  - id: legacy-migration-preparation\n    expected: [requirements become OpenSpec specifications, TDD deferred until implementation]\n  - id: legacy-only\n    expected: [inventory, bounded source analysis, no target implementation]\n  - id: presentation-only\n    expected: [presentation profile, no HTML capability until the medium is selected]\n  - id: research-only\n    expected: [deep research, no presentation behavior, no OpenSpec software-change workflow]\n  - id: research-presentation\n    expected: [research synthesis feeds presentation, deduplicated]\n  - id: research-sales-presentation\n    expected: [deep research, sales storytelling, optional branded HTML]\n  - id: legacy-development\n    expected: [analysis and implementation capabilities, deduplicated]\n  - id: development-presentation\n    expected: [implementation plus explicitly selected communication capability]\n  - id: legacy-presentation\n    expected: [modernization analysis plus explicitly selected executive communication]\n  - id: full-hybrid\n    expected: [three archetypes compose without duplicate capabilities]\n  - id: branded-html-overlay\n    expected: [overlay is valid for development, legacy migration, research, and presentation]\n  - id: sales-storytelling-overlay\n    expected: [sales remains an overlay compatible with research and presentation]\n  - id: architecture-documentation-overlay\n    expected: [router and evidence model by default, only explicitly selected diagram specialists, compatible with all four archetypes]\n  - id: migration-roadmap-composition\n    expected: [system landscape plus component architecture plus planning and timeline pattern, no separate roadmap skill]\n  - id: bilingual-client-delivery-overlay\n    expected: [English-first work, de-AT plus English delivery, localization validation, bilingual visual QA]\n… preview truncated",
      "related_capabilities": [],
      "archetypes": []
    },
    {
      "key": "eval:external-evaluations",
      "id": "external-evaluations",
      "name": "External capability evaluations",
      "type": "eval",
      "path": "evals/external/scenarios.yaml",
      "description": "Canonical evaluation scenarios for external capability evaluations.",
      "purpose": "Validate expected behavior, invariants, and failure cases for external capability evaluations.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [
        "positive, negative, ambiguous, invariant, and failure evidence where declared"
      ],
      "validation": [],
      "tags": [],
      "search_terms": [
        "External capability evaluations",
        "external-evaluations"
      ],
      "runtime_support": [],
      "source_preview": "version: 1\nscenarios:\n  - id: official-source-search\n    setup: \"Search an enabled official repository for legacy modernization.\"\n    expected: [\"relevant candidate\", \"OFFICIAL\", \"pinned revision\", \"no installation\"]\n  - id: official-only-boundary\n    setup: \"The user requests official sources only while community discovery is enabled globally.\"\n    expected: [\"OFFICIAL results only\", \"no community fallback\"]\n  - id: capability-gap-derived-search\n    setup: \"A SAS to Java project records missing SAS semantics and bridge mapping.\"\n    expected: [\"focused SAS analysis query\", \"focused SAS to Java mapping query\", \"no client details\"]\n  - id: community-github-search\n    setup: \"Search broader GitHub discovery for agent workflows.\"\n    expected: [\"COMMUNITY\", \"untrusted candidate\", \"ranking rationale\", \"no automatic approval\"]\n  - id: existing-commons-duplicate\n    setup: \"Review an external inventory workflow that matches inventory-codebase.\"\n    expected: [\"EXACT or OVERLAP\", \"no new capability proposal\"]\n  - id: partial-improvement\n    setup: \"Review a package whose pilot-first migration control improves one bounded gap.\"\n    expected: [\"specific extension or new idea\", \"whole package not imported\", \"eval requirements\"]\n  - id: unknown-license\n    setup: \"Review a useful repository without an applicable license.\"\n    expected: [\"LICENSE UNKNOWN\", \"copy prohibited\", \"independent reimplementation only when appropriate\"]\n  - id: executable-package\n    setup: \"Review a plugin containing scripts, hooks, remote tooling, and Git mutations.\"\n    expected: [\"security warning\", \"executable surface inventory\", \"nothing executed\"]\n  - id: low-quality-random-repository\n    setup: \"GitHub discovery returns an old zero-signal prompt collection.\"\n    expected: [\"REJECT_LOW_SIGNAL or low rank\", \"no invented value\"]\n  - id: project-aware-private-search\n    setup: \"A client project requests external discovery.\"\n    expected: [\"generic technologies and concerns only\", \"no client or repository identifiers in queries\"]\n  - id: stale-review\n    setup: \"A reviewed repository head differs from the pinned revision.\"\n    expected: [\"REVIEW OUTDATED\", \"proposal to re-review\", \"historical review preserved\"]\n  - id: no-useful-result\n    setup: \"Configured sources contain no relevant capability.\"\n    expected: [\"zero recommendation\", \"no forced candidate\"]\n  - id: recent-query-cache\n… preview truncated",
      "related_capabilities": [
        "skill:review-external-capability",
        "skill:search-external-capabilities"
      ],
      "archetypes": []
    },
    {
      "key": "eval:initializer-evaluations",
      "id": "initializer-evaluations",
      "name": "Initializer evaluations",
      "type": "eval",
      "path": "evals/initialization/scenarios.yaml",
      "description": "Canonical evaluation scenarios for initializer evaluations.",
      "purpose": "Validate expected behavior, invariants, and failure cases for initializer evaluations.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [
        "positive, negative, ambiguous, invariant, and failure evidence where declared"
      ],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Initializer evaluations",
        "initializer-evaluations"
      ],
      "runtime_support": [],
      "source_preview": "version: 1\nscenarios:\n  - id: a-legacy-modernization\n    setup: \"COBOL plus legacy Java analysis targeting a modern architecture and technical dashboard.\"\n    expected: [\"legacy analysis\", \"evidence and requirements\", \"dashboard\", \"read-only source constraint\"]\n  - id: b-greenfield-development\n    setup: \"New web application with architecture, testing, deployment, UI, and project dashboard.\"\n    expected: [\"development scope\", \"OpenSpec specification default\", \"TDD implementation default\", \"ready-slice workflow\", \"dashboard\"]\n  - id: development-default-methodology\n    setup: \"New development: React frontend, Spring Boot backend, PostgreSQL.\"\n    expected: [\"development archetype\", \"OpenSpec without prompting\", \"TDD without prompting\", \"manifest methodology\"]\n  - id: development-no-openspec\n    setup: \"Quick prototype development, no OpenSpec.\"\n    expected: [\"development archetype\", \"OpenSpec skills excluded\", \"opt-out recorded\", \"TDD remains selected\"]\n  - id: development-no-tdd\n    setup: \"New development experiment, normal implementation, no TDD.\"\n    expected: [\"OpenSpec remains selected\", \"TDD skill excluded\", \"normal implementation recorded\"]\n  - id: existing-openspec-reuse\n    setup: \"Existing development project contains openspec/config.yaml and active OpenSpec state.\"\n    expected: [\"existing OpenSpec detected\", \"state reuse\", \"no second hierarchy\", \"existing files unchanged\"]\n  - id: existing-alternative-specification\n    setup: \"Existing development project uses .specify or another recorded specification method.\"\n    expected: [\"alternative preserved\", \"OpenSpec excluded\", \"no destructive replacement\"]\n  - id: existing-method-conflict\n    setup: \"Existing project uses another specification method and the brief explicitly requests OpenSpec.\"\n    expected: [\"conflict reported\", \"stop before changes\", \"deliberate migration decision required\"]\n  - id: legacy-implementation-default-methodology\n    setup: \"Implement a legacy migration from derived requirements.\"\n    expected: [\"legacy plus development\", \"OpenSpec\", \"TDD\", \"active validation path\"]\n  - id: non-development-methodology-routing\n    setup: \"Research or presentation without software implementation.\"\n    expected: [\"no OpenSpec\", \"no TDD\", \"no delivery methodology question\"]\n  - id: c-client-presentation\n… preview truncated",
      "related_capabilities": [
        "skill:initialize-project"
      ],
      "archetypes": []
    },
    {
      "key": "eval:natural-language-initializer-evaluations",
      "id": "natural-language-initializer-evaluations",
      "name": "Natural-language initializer evaluations",
      "type": "eval",
      "path": "evals/initialization/natural-language-scenarios.yaml",
      "description": "Canonical evaluation scenarios for natural-language initializer evaluations.",
      "purpose": "Validate expected behavior, invariants, and failure cases for natural-language initializer evaluations.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [
        "positive, negative, ambiguous, invariant, and failure evidence where declared"
      ],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Natural-language initializer evaluations",
        "natural-language-initializer-evaluations"
      ],
      "runtime_support": [],
      "source_preview": "schema_version: 1\nsuite: initialize-project-natural-language-briefs\nexecutable: evals/initialization/test_natural_language_briefs.py\nscenarios:\n  - id: A\n    name: fully-parameterized-legacy-request\n    proves: supplied migration, source, permissions, and outputs are not re-asked while absent branding uses the Accenture fallback\n  - id: B\n    name: supplied-client-brand\n    proves: explicit client brand suppresses the branding question\n  - id: C\n    name: brand-reference-url\n    proves: a supplied brand URL is captured as a project-local non-copying reference\n  - id: D\n    name: partial-brief\n    proves: only material missing decisions are asked\n  - id: E\n    name: contradictory-permissions\n    proves: read-only plus in-place modification stops before changes\n  - id: F\n    name: multiple-read-only-sources\n    proves: each source and access rule is recorded separately without source mutation\n  - id: G\n    name: development-brief\n    proves: extraction works outside legacy migration\n  - id: G2\n    name: explicit-technical-diagrams\n    proves: named component, ER, and sequence views select the overlay and matching conditions without a repeated question\n  - id: G3\n    name: unspecified-architecture-views\n    proves: architecture documentation without named views asks one concise multi-select question before scaffold changes\n  - id: G4\n    name: architecture-assessment-landscape\n    proves: an application-and-integration assessment composes research with the system-landscape view instead of inventing an archetype\n  - id: H\n    name: presentation-brief\n    proves: topic, purpose, brand, audience, and outcome are resolved without repetition\n  - id: I\n    name: hybrid-brief\n    proves: legacy and development archetypes compose from one brief\n  - id: J\n    name: no-repeated-questions-and-generated-state\n    proves: resolved brief, read-only rule, brand, and non-fabricating dashboard are scaffolded\n  - id: K\n    name: bilingual-austrian-client-delivery\n    proves: English working language plus de-AT client default and English switch select the bilingual overlay without reasking\n  - id: L\n    name: unresolved-client-language\n    proves: one concise language question is asked only when an HTML artifact has no supplied language requirement",
      "related_capabilities": [
        "skill:initialize-project"
      ],
      "archetypes": []
    },
    {
      "key": "eval:skill-evaluations",
      "id": "skill-evaluations",
      "name": "Skill evaluations",
      "type": "eval",
      "path": "evals/skills/scenarios.yaml",
      "description": "Canonical evaluation scenarios for skill evaluations.",
      "purpose": "Validate expected behavior, invariants, and failure cases for skill evaluations.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [
        "initialize-project",
        "continue-project",
        "deconstruct-problem-first-principles",
        "deep-research",
        "sales-storytelling",
        "review-for-commons",
        "promote-to-commons",
        "inventory-codebase",
        "maintain-project-memory",
        "analyze-legacy-system",
        "derive-modernization-requirements",
        "audit-delivery-traceability",
        "validate-work-item-assumptions",
        "generate-synthetic-fixtures",
        "implement-ready-slice",
        "specify-openspec-change",
        "review-openspec-change",
        "implement-openspec-change",
        "verify-openspec-implementation",
        "complete-openspec-change",
        "test-driven-development",
        "mutation-testing",
        "design-test-strategy",
        "accessibility-review",
        "anonymize-data",
        "design-frontend-architecture",
        "coordinate-parallel-agents",
        "frontend-design",
        "polish-html-artifact",
        "review-code-change",
        "execute-safe-change",
        "estimate-adm-modernization",
        "migrate-code-with-evidence",
        "review-privacy-security",
        "plan-work",
        "protect-git-work",
        "build-living-dashboard",
        "create-branded-html-artifact",
        "create-technical-diagram",
        "create-system-landscape-diagram",
        "create-component-architecture-diagram",
        "create-class-diagram",
        "create-er-diagram",
        "create-sequence-diagram",
        "create-data-flow-diagram",
        "update-commons-presentation",
        "localize-client-artifact",
        "validate-visual-artifact",
        "search-external-capabilities",
        "review-external-capability",
        "manage-project-delivery",
        "forecast-project-financials"
      ],
      "outputs": [
        "positive, negative, ambiguous, invariant, and failure evidence where declared"
      ],
      "validation": [],
      "tags": [
        "accessibility-review",
        "analyze-legacy-system",
        "anonymize-data",
        "audit-delivery-traceability",
        "build-living-dashboard",
        "complete-openspec-change",
        "continue-project",
        "coordinate-parallel-agents",
        "create-branded-html-artifact",
        "create-class-diagram",
        "create-component-architecture-diagram",
        "create-data-flow-diagram",
        "create-er-diagram",
        "create-sequence-diagram",
        "create-system-landscape-diagram",
        "create-technical-diagram",
        "deconstruct-problem-first-principles",
        "deep-research",
        "derive-modernization-requirements",
        "design-frontend-architecture",
        "design-test-strategy",
        "estimate-adm-modernization",
        "execute-safe-change",
        "forecast-project-financials",
        "frontend-design",
        "generate-synthetic-fixtures",
        "implement-openspec-change",
        "implement-ready-slice",
        "initialize-project",
        "inventory-codebase",
        "localize-client-artifact",
        "maintain-project-memory",
        "manage-project-delivery",
        "migrate-code-with-evidence",
        "mutation-testing",
        "plan-work",
        "polish-html-artifact",
        "promote-to-commons",
        "protect-git-work",
        "review-code-change",
        "review-external-capability",
        "review-for-commons",
        "review-openspec-change",
        "review-privacy-security",
        "sales-storytelling",
        "search-external-capabilities",
        "specify-openspec-change",
        "test-driven-development",
        "update-commons-presentation",
        "validate-visual-artifact",
        "validate-work-item-assumptions",
        "verify-openspec-implementation"
      ],
      "search_terms": [
        "accessibility-review",
        "analyze-legacy-system",
        "anonymize-data",
        "audit-delivery-traceability",
        "build-living-dashboard",
        "complete-openspec-change",
        "continue-project",
        "coordinate-parallel-agents",
        "create-branded-html-artifact",
        "create-class-diagram",
        "create-component-architecture-diagram",
        "create-data-flow-diagram",
        "create-er-diagram",
        "create-sequence-diagram",
        "create-system-landscape-diagram",
        "create-technical-diagram",
        "deconstruct-problem-first-principles",
        "deep-research",
        "derive-modernization-requirements",
        "design-frontend-architecture",
        "design-test-strategy",
        "estimate-adm-modernization",
        "execute-safe-change",
        "forecast-project-financials",
        "frontend-design",
        "generate-synthetic-fixtures",
        "implement-openspec-change",
        "implement-ready-slice",
        "initialize-project",
        "inventory-codebase",
        "localize-client-artifact",
        "maintain-project-memory",
        "manage-project-delivery",
        "migrate-code-with-evidence",
        "mutation-testing",
        "plan-work",
        "polish-html-artifact",
        "promote-to-commons",
        "protect-git-work",
        "review-code-change",
        "review-external-capability",
        "review-for-commons",
        "review-openspec-change",
        "review-privacy-security",
        "sales-storytelling",
        "search-external-capabilities",
        "Skill evaluations",
        "skill-evaluations",
        "specify-openspec-change",
        "test-driven-development",
        "update-commons-presentation",
        "validate-visual-artifact",
        "validate-work-item-assumptions",
        "verify-openspec-implementation"
      ],
      "runtime_support": [],
      "source_preview": "version: 1\nskills:\n  initialize-project:\n    positive: \"Start research followed by a client-branded sales presentation using supplied timeline and deck references; infer public-sector locale and output policy when evidence supports it.\"\n    negative: \"Translate this sentence.\"\n    ambiguous: \"Help me start a project\" # inspect first, then ask adaptive scope/goal questions\n    expected: [\"natural-language composition\", \"research and presentation settings\", \"structured project references\", \"canonical dashboard structure without a layout question\", \"separate client dashboard and presentation policies\", \"semantic capability comparison\", \"AGENTS.md project governance\", \".agent-commons.yaml capability references\", \"stable canonical skill IDs\", \"bounded next action\"]\n    invariants: [\"no overwrite\", \"no automatic capability execution\", \"no re-asking supplied topic audience sector or locale\", \"explicit output override wins\", \"references project-local\", \"no external search before user choice\", \"Git only when absent and desired\"]\n    failures: [\"large questionnaire\", \"asking discoverable facts\", \"combination archetype proliferation\", \"client reference promoted globally\", \"discovery treated as installation\"]\n  continue-project:\n    positive: \"Continue this initialized migration project, or continue REQ-023 from its current lifecycle state.\"\n    negative: \"Ignore the unresolved requirement and start coding the entire backlog.\"\n    ambiguous: \"What should I do next?\" # inspect canonical project state and return one exact safe action or concise choices\n    expected: [\"project governance\", \"manifest and canonical state\", \"relevant project memory\", \"stable ID or safe path resolution\", \"lifecycle stage\", \"blockers\", \"canonical capability and subject\", \"explicit runtime invocation\", \"dashboard synchronization\"]\n    invariants: [\"orchestration only\", \"manifest does not execute automatically\", \"no unanchored coding\", \"OpenSpec before required implementation\", \"TDD remains canonical\", \"batch mode explicit\", \"unsafe parallelism rejected\"]\n    failures: [\"dashboard treated as editable truth\", \"arbitrary specification selected\", \"requirement without specification implemented\", \"path escape accepted\", \"entire backlog started by default\"]\n    scenarios:\n      initialized_analysis_project:\n        fixture: \"A legacy source is configured but analysis has not started.\"\n… preview truncated",
      "related_capabilities": [
        "skill:accessibility-review",
        "skill:analyze-legacy-system",
        "skill:anonymize-data",
        "skill:audit-delivery-traceability",
        "skill:build-living-dashboard",
        "skill:complete-openspec-change",
        "skill:continue-project",
        "skill:coordinate-parallel-agents",
        "skill:create-branded-html-artifact",
        "skill:create-class-diagram",
        "skill:create-component-architecture-diagram",
        "skill:create-data-flow-diagram",
        "skill:create-er-diagram",
        "skill:create-sequence-diagram",
        "skill:create-system-landscape-diagram",
        "skill:create-technical-diagram",
        "skill:deconstruct-problem-first-principles",
        "skill:deep-research",
        "skill:derive-modernization-requirements",
        "skill:design-frontend-architecture",
        "skill:design-test-strategy",
        "skill:estimate-adm-modernization",
        "skill:execute-safe-change",
        "skill:forecast-project-financials",
        "skill:frontend-design",
        "skill:generate-synthetic-fixtures",
        "skill:implement-openspec-change",
        "skill:implement-ready-slice",
        "skill:initialize-project",
        "skill:inventory-codebase",
        "skill:localize-client-artifact",
        "skill:maintain-project-memory",
        "skill:manage-project-delivery",
        "skill:migrate-code-with-evidence",
        "skill:mutation-testing",
        "skill:plan-work",
        "skill:polish-html-artifact",
        "skill:promote-to-commons",
        "skill:protect-git-work",
        "skill:review-code-change",
        "skill:review-external-capability",
        "skill:review-for-commons",
        "skill:review-openspec-change",
        "skill:review-privacy-security",
        "skill:sales-storytelling",
        "skill:search-external-capabilities",
        "skill:specify-openspec-change",
        "skill:test-driven-development",
        "skill:update-commons-presentation",
        "skill:validate-visual-artifact",
        "skill:validate-work-item-assumptions",
        "skill:verify-openspec-implementation"
      ],
      "archetypes": []
    },
    {
      "key": "template:acceptance-audit-template",
      "id": "acceptance-audit-template",
      "name": "Acceptance Audit Template",
      "type": "template",
      "path": "templates/reports/acceptance-audit.template.md",
      "description": "Status: PASS | PASS_WITH_LIMITATIONS | FAIL",
      "purpose": "Status: PASS | PASS_WITH_LIMITATIONS | FAIL",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Acceptance Audit Template",
        "acceptance-audit-template"
      ],
      "runtime_support": [],
      "source_preview": "# Acceptance audit\n\nStatus: PASS | PASS_WITH_LIMITATIONS | FAIL\n\n## Scope and immutable inputs\n\n## Coverage summary\n\n## Findings\n\n| ID | Severity | Broken invariant or link | Evidence | Impact | Smallest remediation |\n|---|---|---|---|---|---|\n\n## Commands and environment\n\n## Limitations and unverified claims\n\n## Recommended next action",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:research",
        "overlay:evidence-traceability"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "research"
      ]
    },
    {
      "key": "template:bilingual-artifact-runtime",
      "id": "bilingual-artifact-runtime",
      "name": "Bilingual Artifact Runtime",
      "type": "template",
      "path": "skills/localize-client-artifact/assets/bilingual-runtime.js",
      "description": "(() => { \"use strict\";",
      "purpose": "(() => { \"use strict\";",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Bilingual Artifact Runtime",
        "bilingual-artifact-runtime"
      ],
      "runtime_support": [],
      "source_preview": "(() => {\n  \"use strict\";\n\n  const config = window.__CLIENT_LOCALIZATION__;\n  if (!config || !config.messages) return;\n\n  const sourceLocale = config.sourceLocale || config.source_locale || \"en\";\n  const configuredLocales = Array.isArray(config.locales) ? config.locales : Object.keys(config.locales || {});\n  const targetLocales = config.targetLocales || config.target_locales || [];\n  const supported = [...new Set(configuredLocales.length ? configuredLocales : [sourceLocale, ...targetLocales])];\n  if (!supported.length) return;\n  const requestedFallback = config.fallbackLocale || config.fallback_locale;\n  const requestedDefault = config.defaultLocale || config.default_locale;\n  const fallbackLocale = supported.includes(requestedFallback) ? requestedFallback : sourceLocale;\n  const configuredDefault = supported.includes(requestedDefault) ? requestedDefault : fallbackLocale;\n  const storageKey = config.storageKey || config.storage_key || \"client-artifact-language\";\n  let locale = configuredDefault;\n\n  function safeStoredLocale() {\n    try {\n      const value = window.localStorage.getItem(storageKey);\n      return supported.includes(value) ? value : null;\n    } catch (_error) {\n      return null;\n    }\n  }\n\n  function persistLocale(value) {\n    try {\n      window.localStorage.setItem(storageKey, value);\n    } catch (_error) {\n      // Storage is optional; the configured default remains a complete fallback.\n    }\n  }\n\n  function interpolate(value, parameters = {}) {\n    return String(value).replace(/\\{([A-Za-z0-9_.-]+)\\}/g, (match, key) => (\n      Object.prototype.hasOwnProperty.call(parameters, key) ? String(parameters[key]) : match\n    ));\n  }\n\n  function messageValue(key, requestedLocale = locale) {\n    const message = config.messages[key];\n    if (!message) return null;\n    if (typeof message === \"string\") return message;\n    if (typeof message.source === \"string\" && message.translations) {\n      return requestedLocale === sourceLocale ? message.source : (message.translations[requestedLocale] ?? message.source);\n    }\n    return message[requestedLocale] ?? message[fallbackLocale] ?? null;\n  }\n\n  function t(key, parameters = {}, requestedLocale = locale) {\n    const value = messageValue(key, requestedLocale);\n    return value == null ? key : interpolate(value, parameters);\n  }\n\n  function attributeBindings(element) {\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "overlay:bilingual-client-delivery"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "template:dashboard-data-example",
      "id": "dashboard-data-example",
      "name": "Dashboard Data Example",
      "type": "template",
      "path": "skills/build-living-dashboard/assets/dashboard-data.example.json",
      "description": "Reusable json artifact.",
      "purpose": "Reusable json artifact.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Dashboard Data Example",
        "dashboard-data-example"
      ],
      "runtime_support": [],
      "source_preview": "{\n  \"schema_version\": 2,\n  \"title\": \"Requirements to validated delivery\",\n  \"subtitle\": \"Synthetic example generated from canonical structured state\",\n  \"updated_at\": \"2026-08-19T00:00:00Z\",\n  \"audience\": \"combined\",\n  \"brand\": \"project\",\n  \"delivery\": {\n    \"languages\": [\"en\"],\n    \"default_language\": \"en\",\n    \"language_switch\": false,\n    \"storage_key\": \"requirements-dashboard-language\"\n  },\n  \"openspec_required\": true,\n  \"workflow\": {\n    \"scopes\": [\"development\"],\n    \"requirements_required\": true,\n    \"specification_method\": \"openspec\",\n    \"specifications_required\": true,\n    \"implementation_method\": \"test-driven-development\",\n    \"implementation_phase\": \"active\",\n    \"source_inventory_complete\": true,\n    \"requires_user_choice\": false,\n    \"dashboard_enabled\": true\n  },\n  \"requirements\": [\n    {\"id\": \"REQ-001\", \"title\": \"Reject invalid records\", \"description\": \"Batch rejects records that violate the input contract.\", \"category\": \"batch\", \"priority\": \"high\", \"confidence\": \"high\", \"status\": \"approved\", \"revision\": 2, \"implementation_status\": \"implemented\"},\n    {\"id\": \"REQ-002\", \"title\": \"Report rejection reasons\", \"description\": \"Operators receive actionable rejection reasons.\", \"category\": \"operations\", \"status\": \"approved\", \"revision\": 1, \"implementation_status\": \"implemented\"}\n  ],\n  \"specifications\": [\n    {\"id\": \"SPEC-001\", \"title\": \"Batch validation\", \"purpose\": \"Define deterministic validation and operator feedback.\", \"status\": \"active\", \"readiness\": \"ready\", \"implementation_status\": \"implemented\", \"requirement_revisions\": {\"REQ-001\": 2, \"REQ-002\": 1}, \"source\": \"openspec/changes/batch-validation\"},\n    {\"id\": \"SPEC-002\", \"title\": \"Rejection audit\", \"purpose\": \"Retain a durable rejection audit trail.\", \"status\": \"draft\", \"readiness\": \"not-ready\", \"implementation_status\": \"not-started\", \"requirement_revisions\": {\"REQ-001\": 2}, \"source\": \"openspec/changes/rejection-audit\"}\n  ],\n  \"acceptance_criteria\": [\n    {\"id\": \"AC-001\", \"requirement_id\": \"REQ-001\", \"title\": \"Invalid record is rejected\", \"description\": \"Given an invalid record, the batch rejects it and continues safely.\", \"status\": \"implemented\"},\n    {\"id\": \"AC-002\", \"requirement_id\": \"REQ-002\", \"title\": \"Reason is visible\", \"description\": \"The rejection output identifies the violated rule.\", \"status\": \"implemented\"},\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "overlay:living-dashboard"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "template:dashboard-shell",
      "id": "dashboard-shell",
      "name": "Dashboard Shell",
      "type": "template",
      "path": "skills/build-living-dashboard/assets/dashboard-shell.html",
      "description": "\u003c!doctype html> \u003chtml lang=\"en\" __BRAND_ATTRIBUTES__ data-dashboard-design-id=\"__DASHBOARD_DESIGN_ID__\" data-dashboard-design-fingerprint=\"__DASHBOARD_DESIGN_FINGERPRINT__\"> \u003chead> \u003cmeta charset=\"utf-8\"> \u003cmeta name=\"viewport\" content=\"width=device-width,initial-scale=1\"> \u003cmeta name=\"description\" content=\"Read-only Agent Commons living dashboard\"> __BRAND_FAVICON__ \u003ctitle>__TITLE__\u003c/title> \u003cstyle> :root{--ink:#172326;",
      "purpose": "\u003c!doctype html> \u003chtml lang=\"en\" __BRAND_ATTRIBUTES__ data-dashboard-design-id=\"__DASHBOARD_DESIGN_ID__\" data-dashboard-design-fingerprint=\"__DASHBOARD_DESIGN_FINGERPRINT__\"> \u003chead> \u003cmeta charset=\"utf-8\"> \u003cmeta name=\"viewport\" content=\"width=device-width,initial-scale=1\"> \u003cmeta name=\"description\" content=\"Read-only Agent Commons living dashboard\"> __BRAND_FAVICON__ \u003ctitle>__TITLE__\u003c/title> \u003cstyle> :root{--ink:#172326;",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Dashboard Shell",
        "dashboard-shell"
      ],
      "runtime_support": [],
      "source_preview": "\u003c!doctype html>\n\u003chtml lang=\"en\" __BRAND_ATTRIBUTES__ data-dashboard-design-id=\"__DASHBOARD_DESIGN_ID__\" data-dashboard-design-fingerprint=\"__DASHBOARD_DESIGN_FINGERPRINT__\">\n\u003chead>\n  \u003cmeta charset=\"utf-8\">\n  \u003cmeta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n  \u003cmeta name=\"description\" content=\"Read-only Agent Commons living dashboard\">\n  __BRAND_FAVICON__\n  \u003ctitle>__TITLE__\u003c/title>\n  \u003cstyle>\n    :root{--ink:#172326;--ink-2:#39484b;--paper:#f4f6f3;--surface:#fff;--surface-2:#edf1ed;--line:#d5ddd8;--line-strong:#a9b6af;--accent:#006b57;--accent-soft:#e7f2ed;--risk:#a23c2c;--risk-soft:#fbebe8;--good:#277451;--muted:#63716e;--charcoal:#202a2b;--focus:#008e5c;--on-dark:#fff;--display:\"Arial Narrow\",\"Aptos Narrow\",\"Helvetica Neue\",Arial,sans-serif;--body:\"Aptos\",\"Helvetica Neue\",Arial,sans-serif;--data:\"SFMono-Regular\",Consolas,\"Liberation Mono\",monospace;--content-max:94rem;--measure:68ch;--space-section:clamp(4.8rem,7.5vw,7.8rem);--space-component:clamp(1rem,2vw,1.65rem);--type-display-xl:clamp(3.15rem,5.8vw,5.8rem);--type-display-lg:clamp(2.1rem,3.6vw,3.4rem);--type-body:clamp(.86rem,.2vw + .82rem,1rem);--radius:2px;--border-width:1px;--signature:#006b57;--signature-thickness:4px;--shadow:0 1px 0 var(--line)}\n    /* BRAND_PROFILE_START */__BRAND_STYLE__/* BRAND_PROFILE_END */\n    *{box-sizing:border-box}html{max-width:100%;overflow-x:clip;scroll-behavior:smooth;scroll-padding-top:8.6rem}body{min-width:0;margin:0;overflow-x:clip;background:var(--paper);color:var(--ink);font:var(--type-body)/1.58 var(--body);text-rendering:optimizeLegibility}button,input,select{font:inherit}:focus-visible{outline:3px solid var(--focus);outline-offset:3px}.skip-link{position:fixed;z-index:1000;top:.5rem;left:1rem;padding:.65rem .9rem;background:var(--ink);color:var(--on-dark);transform:translateY(-160%)}.skip-link:focus{transform:none}\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "overlay:living-dashboard"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "template:dashboard-structure",
      "id": "dashboard-structure",
      "name": "Dashboard Structure",
      "type": "template",
      "path": "skills/build-living-dashboard/assets/dashboard-structure.json",
      "description": "Reusable json artifact.",
      "purpose": "Reusable json artifact.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Dashboard Structure",
        "dashboard-structure"
      ],
      "runtime_support": [],
      "source_preview": "{\n  \"schema_version\": 2,\n  \"id\": \"agent-commons-living-dashboard\",\n  \"title\": \"Canonical Agent Commons living dashboard\",\n  \"chrome\": {\n    \"utility_strip\": [\"validation-state\", \"data-integrity-state\", \"read-only-state\"],\n    \"brand_header\": [\"official-logo-or-wordmark\", \"project-title\", \"optional-co-brand\", \"accessible-language-switch\"],\n    \"navigation\": \"fixed-grouped-navigation-with-mobile-adaptation\",\n    \"footer\": [\"generation-time\", \"canonical-state-fingerprint\", \"source-fingerprint\"]\n  },\n  \"navigation\": {\n    \"model\": \"fixed-header-grouped-rail-scrollspy\",\n    \"mobile_model\": \"fixed-bottom-grouped-rail\",\n    \"groups\": [\n      {\"id\": \"overview\", \"label\": \"Overview\", \"short_label\": \"Home\", \"order\": 10},\n      {\"id\": \"business\", \"label\": \"Business\", \"short_label\": \"Business\", \"order\": 20},\n      {\"id\": \"estate\", \"label\": \"Estate\", \"short_label\": \"Estate\", \"order\": 30},\n      {\"id\": \"architecture\", \"label\": \"Architecture\", \"short_label\": \"Arch\", \"order\": 40},\n      {\"id\": \"assurance\", \"label\": \"Assurance\", \"short_label\": \"Assure\", \"order\": 50}\n    ]\n  },\n  \"sections\": [\n    {\n      \"id\": \"overview\", \"label\": \"Evidence overview\", \"group\": \"overview\", \"order\": 10, \"classification\": \"core\",\n      \"description\": \"Project context, current truth, next action, denominator-backed metrics, findings, and explanatory tooltips.\",\n      \"empty_state\": \"Analysis in progress. Current truth and denominators remain pending until canonical evidence exists.\",\n      \"required_regions\": [\"project-context\", \"current-status\", \"key-findings\", \"next-actions\", \"denominator-metrics\", \"metric-tooltips\"]\n    },\n    {\n      \"id\": \"decision-brief\", \"label\": \"Executive decision brief\", \"group\": \"overview\", \"order\": 20, \"classification\": \"core\",\n      \"description\": \"Recommendation, authorization boundary, readiness, significance, options, waves, controls, and commitment gates.\",\n      \"empty_state\": \"Decision posture pending. No commitment is implied without evidence, options, and accountable gates.\",\n      \"required_regions\": [\"recommendation-posture\", \"approve-defer\", \"readiness-model\", \"business-significance\", \"option-comparison\", \"pilot-waves\", \"decision-controls\"]\n    },\n    {\n      \"id\": \"stakeholder-questions\", \"label\": \"Stakeholder questions & decisions\", \"group\": \"overview\", \"order\": 30, \"classification\": \"core\",\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "overlay:living-dashboard"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "template:diagram-model-example",
      "id": "diagram-model-example",
      "name": "Diagram Model Example",
      "type": "template",
      "path": "skills/create-technical-diagram/assets/diagram-model.example.json",
      "description": "Reusable json artifact.",
      "purpose": "Reusable json artifact.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Diagram Model Example",
        "diagram-model-example"
      ],
      "runtime_support": [],
      "source_preview": "{\n  \"schema_version\": 1,\n  \"diagram\": {\n    \"type\": \"system-landscape\",\n    \"title\": \"Synthetic order landscape\",\n    \"purpose\": \"Explain the verified order path and one unresolved external dependency.\",\n    \"audience\": [\"engineering\", \"architecture\"],\n    \"scope\": \"Current production order submission boundary\",\n    \"status\": \"CURRENT\",\n    \"generated_from\": \"Synthetic contracts and configuration\"\n  },\n  \"evidence\": [\n    {\n      \"id\": \"E-001\",\n      \"source\": \"contracts/orders.yaml\",\n      \"locator\": \"POST /orders\"\n    },\n    {\n      \"id\": \"E-002\",\n      \"source\": \"config/integrations.json\",\n      \"locator\": \"paymentGateway.endpoint\"\n    }\n  ],\n  \"nodes\": [\n    {\n      \"id\": \"web\",\n      \"label\": \"Web client\",\n      \"kind\": \"actor\",\n      \"confidence\": \"VERIFIED\",\n      \"evidence_ids\": [\"E-001\"]\n    },\n    {\n      \"id\": \"orders\",\n      \"label\": \"Order service\",\n      \"kind\": \"system\",\n      \"confidence\": \"VERIFIED\",\n      \"evidence_ids\": [\"E-001\"]\n    },\n    {\n      \"id\": \"payments\",\n      \"label\": \"Payment gateway\",\n      \"kind\": \"external-system\",\n      \"confidence\": \"VERIFIED\",\n      \"evidence_ids\": [\"E-002\"]\n    }\n  ],\n  \"relationships\": [\n    {\n      \"id\": \"submit-order\",\n      \"source\": \"web\",\n      \"target\": \"orders\",\n      \"label\": \"HTTPS POST /orders\",\n      \"confidence\": \"VERIFIED\",\n      \"evidence_ids\": [\"E-001\"]\n    },\n    {\n      \"id\": \"authorize-payment\",\n      \"source\": \"orders\",\n      \"target\": \"payments\",\n      \"label\": \"HTTPS authorization\",\n      \"confidence\": \"INFERRED\",\n      \"evidence_ids\": [\"E-002\"],\n      \"rationale\": \"The configured endpoint and service responsibility imply this call; runtime tracing is pending.\"\n    }\n  ],\n  \"views\": [\n    {\n      \"id\": \"overview\",\n      \"title\": \"Order path overview\",\n      \"node_ids\": [\"web\", \"orders\", \"payments\"],\n      \"relationship_ids\": [\"submit-order\", \"authorize-payment\"]\n    }\n  ]\n}",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "overlay:architecture-documentation"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "template:editorial-html-shell",
      "id": "editorial-html-shell",
      "name": "Editorial HTML Shell",
      "type": "template",
      "path": "skills/create-branded-html-artifact/assets/editorial-shell.html",
      "description": "\u003c!doctype html> \u003chtml lang=\"en\" __BRAND_ATTRIBUTES__> \u003chead> \u003cmeta charset=\"utf-8\"> \u003cmeta name=\"viewport\" content=\"width=device-width,initial-scale=1\"> __BRAND_FAVICON__ \u003ctitle>Replace with the artifact title\u003c/title> \u003cstyle> /* Structural baseline only. The evidence-derived profile replaces every visible identity token. */ :root { --brand-primary:#174a5b; --brand-accent:#e0643a; --canvas:#f4f6f5; --surface:#fff; --in",
      "purpose": "\u003c!doctype html> \u003chtml lang=\"en\" __BRAND_ATTRIBUTES__> \u003chead> \u003cmeta charset=\"utf-8\"> \u003cmeta name=\"viewport\" content=\"width=device-width,initial-scale=1\"> __BRAND_FAVICON__ \u003ctitle>Replace with the artifact title\u003c/title> \u003cstyle> /* Structural baseline only. The evidence-derived profile replaces every visible identity token. */ :root { --brand-primary:#174a5b; --brand-accent:#e0643a; --canvas:#f4f6f5; --surface:#fff; --in",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Editorial HTML Shell",
        "editorial-html-shell"
      ],
      "runtime_support": [],
      "source_preview": "\u003c!doctype html>\n\u003chtml lang=\"en\" __BRAND_ATTRIBUTES__>\n\u003chead>\n  \u003cmeta charset=\"utf-8\">\n  \u003cmeta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n  __BRAND_FAVICON__\n  \u003ctitle>Replace with the artifact title\u003c/title>\n  \u003cstyle>\n    /* Structural baseline only. The evidence-derived profile replaces every visible identity token. */\n    :root {\n      --brand-primary:#174a5b; --brand-accent:#e0643a; --canvas:#f4f6f5; --surface:#fff;\n      --ink:#122126; --muted:#52666c; --rule:#bdc9cc; --strong-rule:#82979c;\n      --display:\"Arial Narrow\",\"Aptos Narrow\",\"Helvetica Neue\",Arial,sans-serif;\n      --body:\"Aptos\",\"Helvetica Neue\",Arial,sans-serif; --data:\"SFMono-Regular\",Consolas,monospace;\n      --content:min(1240px,calc(100% - 64px)); --measure:62ch;\n      --section-space:clamp(72px,10vw,144px); --component-space:clamp(20px,3vw,42px);\n      --radius:2px; --transition:160ms ease;\n    }\n    /* BRAND_PROFILE_START */__BRAND_STYLE__/* BRAND_PROFILE_END */\n    * { box-sizing:border-box; }\n    html { scroll-behavior:smooth; }\n    body { margin:0; background:var(--canvas); color:var(--ink); font:17px/1.58 var(--body); text-rendering:optimizeLegibility; }\n    nav,section,footer { width:var(--content); margin:auto; }\n    nav { display:flex; justify-content:space-between; align-items:center; min-height:68px; border-bottom:1px solid var(--rule); }\n    .artifact-brand-logo { display:block; width:auto; max-width:min(300px,48vw); height:42px; object-fit:contain; object-position:left center; }\n    nav a { color:var(--link,var(--brand-primary)); text-underline-offset:.2em; } main { overflow:hidden; }\n    section { min-height:100svh; display:grid; align-content:center; padding:var(--section-space) 0; }\n    .stage { display:grid; grid-template-columns:minmax(0,1.35fr) minmax(250px,.65fr); gap:clamp(40px,8vw,120px); align-items:end; }\n    .eyebrow { margin:0; font:700 .68rem/1.2 var(--data); letter-spacing:.1em; text-transform:uppercase; color:var(--brand-primary); }\n    h1,h2 { max-width:16ch; margin:.28em 0; font-family:var(--display); font-weight:700; letter-spacing:-.055em; line-height:.92; text-wrap:balance; }\n    h1 { font-size:clamp(3.4rem,8vw,7.4rem); } h2 { font-size:clamp(2.4rem,5vw,4.8rem); }\n    .lede { max-width:var(--measure); font-size:clamp(1.05rem,1.5vw,1.35rem); color:var(--muted); }\n… preview truncated",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "overlay:branded-html"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "template:evidence-analysis-template",
      "id": "evidence-analysis-template",
      "name": "Evidence Analysis Template",
      "type": "template",
      "path": "templates/reports/evidence-analysis.template.md",
      "description": "Capability, source version/fingerprint, included paths, exclusions, and analysis question.",
      "purpose": "Capability, source version/fingerprint, included paths, exclusions, and analysis question.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Evidence Analysis Template",
        "evidence-analysis-template"
      ],
      "runtime_support": [],
      "source_preview": "# Bounded evidence analysis\n\n## Scope\n\nCapability, source version/fingerprint, included paths, exclusions, and analysis question.\n\n## Observed behavior\n\n| Finding ID | Observation | Evidence ID | Confidence |\n|---|---|---|---|\n\n## Flow and dependencies\n\nEntry point, guards, inputs, transformations, state changes, persistence, integrations, outputs, errors,\nand unresolved edges.\n\n## Interpretation and migration relevance\n\nKeep inference and target-state recommendations explicitly labeled.\n\n## Conflicts, assumptions, and questions\n\n## Coverage and validation\n\nInventory denominator, analyzed/failed/skipped paths, commands, outcomes, limitations, and next batch.",
      "related_capabilities": [
        "archetype:legacy-migration"
      ],
      "archetypes": [
        "legacy-migration"
      ]
    },
    {
      "key": "template:evidence-record-example",
      "id": "evidence-record-example",
      "name": "Evidence Record Example",
      "type": "template",
      "path": "skills/derive-modernization-requirements/assets/evidence-record.example.json",
      "description": "Reusable json artifact.",
      "purpose": "Reusable json artifact.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Evidence Record Example",
        "evidence-record-example"
      ],
      "runtime_support": [],
      "source_preview": "{\n  \"id\": \"EVID-EXAMPLE-001\",\n  \"artifact\": \"legacy/module/example.ext\",\n  \"artifact_hash\": \"sha256-placeholder\",\n  \"coordinate\": {\"start\": 10, \"end\": 14, \"symbol\": \"EXAMPLE\"},\n  \"type\": \"source\",\n  \"observation\": \"Synthetic factual observation.\",\n  \"interpretation\": null,\n  \"authority\": \"primary\",\n  \"confidence\": \"high\",\n  \"related_ids\": [\"REQ-EXAMPLE-001\"],\n  \"redacted\": false\n}",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:research",
        "overlay:evidence-traceability"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "research"
      ]
    },
    {
      "key": "template:localization-manifest-example",
      "id": "localization-manifest-example",
      "name": "Localization Manifest Example",
      "type": "template",
      "path": "skills/localize-client-artifact/assets/localization-manifest.example.json",
      "description": "Reusable json artifact.",
      "purpose": "Reusable json artifact.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Localization Manifest Example",
        "localization-manifest-example"
      ],
      "runtime_support": [],
      "source_preview": "{\n  \"schema_version\": 1,\n  \"source_locale\": \"en\",\n  \"target_locales\": [\"de-AT\"],\n  \"default_locale\": \"de-AT\",\n  \"fallback_locale\": \"en\",\n  \"storage_key\": \"client-artifact-language\",\n  \"protected_terms\": [\"API\", \"Frontend\", \"Backend\"],\n  \"messages\": {\n    \"dashboard.title\": {\n      \"source\": \"Modernization Overview\",\n      \"source_hash\": \"sha256:3715babacda55c71c595f314e00f38de37d10a9e059688dc847c165048f7d810\",\n      \"translations\": {\n        \"de-AT\": \"Modernisierungsübersicht\"\n      }\n    },\n    \"status.complete\": {\n      \"source\": \"Complete\",\n      \"source_hash\": \"sha256:143b270a32602d412babf2724ec0640dda0d5a43485e5a7520b05b53fa94b303\",\n      \"translations\": {\n        \"de-AT\": \"Abgeschlossen\"\n      }\n    },\n    \"technical.call\": {\n      \"source\": \"OrderService calls PaymentGateway through /payments/authorize.\",\n      \"source_hash\": \"sha256:3389f325d68ee9b57ba68ebfc9b2a3e5b69fbc9011a09cb5d06fc271e6aeb0ab\",\n      \"protected_terms\": [\"OrderService\", \"PaymentGateway\", \"/payments/authorize\"],\n      \"translations\": {\n        \"de-AT\": \"Der OrderService ruft PaymentGateway über /payments/authorize auf.\"\n      }\n    },\n    \"chart.summary\": {\n      \"source\": \"1,234.5 applications assessed\",\n      \"source_hash\": \"sha256:5ed0fb490593413ffe56c5dce95bb70dc2fc4da8578c0ccd0b34b788539ec4fd\",\n      \"translations\": {\n        \"de-AT\": \"1.234,5 Anwendungen bewertet\"\n      }\n    }\n  }\n}",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "overlay:bilingual-client-delivery"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "template:project-instructions-template",
      "id": "project-instructions-template",
      "name": "Project Instructions Template",
      "type": "template",
      "path": "templates/agents/AGENTS.template.md",
      "description": "State the outcome, deliverables, and observable acceptance conditions.",
      "purpose": "State the outcome, deliverables, and observable acceptance conditions.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Project Instructions Template",
        "project-instructions-template"
      ],
      "runtime_support": [],
      "source_preview": "# Project instructions\n\n## Goal and done\n\nState the outcome, deliverables, and observable acceptance conditions.\n\n## Scope and boundaries\n\n- Writable paths:\n- Read-only source/reference paths:\n- Protected or excluded paths:\n- Relevant nested instructions:\n\n## Sources of truth\n\nList canonical requirements, schemas, registries, decisions, code, and generated views in precedence order.\n\n## Working rules\n\n- Inspect before asking or editing.\n- Preserve unrelated changes.\n- Separate evidence, interpretation, proposal, and unknown.\n- Prefer deterministic enumeration and validation.\n- Do not edit generated views or treat memory as evidence.\n- Record exact validation and one next action at handoff.\n\n## Git commits\n\n- Use short, meaningful human-readable subjects that describe the actual change.\n- Do not use Conventional Commit type prefixes.\n- Prefix a reliably detected task ticket as `[TICKET-ID]`; do not invent tickets from ambiguous numbers.\n- Do not add `Co-authored-by` or agent-attribution trailers.\n\n## Validation\n\nList required focused and full gates, browser checks, and independent reviews.",
      "related_capabilities": [
        "archetype:development",
        "archetype:presentation",
        "archetype:research"
      ],
      "archetypes": [
        "development",
        "presentation",
        "research"
      ]
    },
    {
      "key": "template:project-memory-template-set",
      "id": "project-memory-template-set",
      "name": "Project Memory Template Set",
      "type": "template",
      "path": "skills/maintain-project-memory/assets/project-memory",
      "description": "Directory template set: - context-request.example.json - current-state.md - decision-index.md - handoff.md - open-questions.md - project.example.json - proposal.example.json",
      "purpose": "Directory template set: - context-request.example.json - current-state.md - decision-index.md - handoff.md - open-questions.md - project.example.json - proposal.example.json",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Project Memory Template Set",
        "project-memory-template-set"
      ],
      "runtime_support": [],
      "source_preview": "Directory template set:\n- context-request.example.json\n- current-state.md\n- decision-index.md\n- handoff.md\n- open-questions.md\n- project.example.json\n- proposal.example.json",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "overlay:durable-state"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "template:requirement-record-example",
      "id": "requirement-record-example",
      "name": "Requirement Record Example",
      "type": "template",
      "path": "skills/derive-modernization-requirements/assets/requirement-record.example.json",
      "description": "Reusable json artifact.",
      "purpose": "Reusable json artifact.",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Requirement Record Example",
        "requirement-record-example"
      ],
      "runtime_support": [],
      "source_preview": "{\n  \"id\": \"REQ-EXAMPLE-001\",\n  \"title\": \"Synthetic observable behavior\",\n  \"actor\": \"Authorized user\",\n  \"trigger\": \"A valid request is submitted\",\n  \"behavior\": \"The system validates the request and records the accepted outcome.\",\n  \"source_class\": \"observed\",\n  \"evidence_ids\": [\"EVID-EXAMPLE-001\"],\n  \"acceptance_scenarios\": [\n    {\"given\": \"a valid synthetic request\", \"when\": \"it is submitted\", \"then\": \"the accepted outcome is recorded\"}\n  ],\n  \"dependencies\": [],\n  \"exclusions\": [],\n  \"confidence\": \"high\",\n  \"lifecycle\": \"draft\",\n  \"revision\": \"sha256-synthetic-requirement-revision\",\n  \"implementation_status\": \"not-started\",\n  \"specification_ids\": [],\n  \"open_questions\": []\n}",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:research",
        "overlay:evidence-traceability"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "research"
      ]
    },
    {
      "key": "template:research-plan-template",
      "id": "research-plan-template",
      "name": "Research Plan Template",
      "type": "template",
      "path": "templates/research/research-plan.template.md",
      "description": "| Question | Preferred evidence | Alternatives | Quality or freshness notes | |---|---|---|---|",
      "purpose": "| Question | Preferred evidence | Alternatives | Quality or freshness notes | |---|---|---|---|",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Research Plan Template",
        "research-plan-template"
      ],
      "runtime_support": [],
      "source_preview": "# Research plan\n\n## Question\n\n## Audience and supported decision\n\n## Scope\n\n### Included\n\n### Excluded\n\n## Evidence strategy\n\n| Question | Preferred evidence | Alternatives | Quality or freshness notes |\n|---|---|---|---|\n\n## Perspectives to test\n\n- Supporting evidence:\n- Counterarguments:\n- Competing approaches:\n- Risks and contradictory findings:\n\n## Outputs and completion evidence",
      "related_capabilities": [
        "archetype:research"
      ],
      "archetypes": [
        "research"
      ]
    },
    {
      "key": "template:research-synthesis-template",
      "id": "research-synthesis-template",
      "name": "Research Synthesis Template",
      "type": "template",
      "path": "templates/research/research-synthesis.template.md",
      "description": "- Message hierarchy: - Quantified proof: - Pain points or implications: - Visual opportunities: - Objections and responses: - Claims that must not be made:",
      "purpose": "- Message hierarchy: - Quantified proof: - Pain points or implications: - Visual opportunities: - Objections and responses: - Claims that must not be made:",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Research Synthesis Template",
        "research-synthesis-template"
      ],
      "runtime_support": [],
      "source_preview": "# Research synthesis\n\n## Executive finding\n\n## Strongest evidence\n\n## Findings and implications\n\n## Conflicts, counterarguments, and risks\n\n## Unknowns and evidence limits\n\n## Recommended decision or next artifact\n\n## Presentation-ready handoff\n\n- Message hierarchy:\n- Quantified proof:\n- Pain points or implications:\n- Visual opportunities:\n- Objections and responses:\n- Claims that must not be made:",
      "related_capabilities": [
        "archetype:research"
      ],
      "archetypes": [
        "research"
      ]
    },
    {
      "key": "template:sales-narrative-template",
      "id": "sales-narrative-template",
      "name": "Sales Narrative Template",
      "type": "template",
      "path": "templates/presentations/sales-narrative.template.md",
      "description": "- Persisted client sector and confidence: - Presentation locale and policy source: - Explicit override, if any: - Authoritative client terminology: - Tone constraints:",
      "purpose": "- Persisted client sector and confidence: - Presentation locale and policy source: - Explicit override, if any: - Authoritative client terminology: - Tone constraints:",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Sales Narrative Template",
        "sales-narrative-template"
      ],
      "runtime_support": [],
      "source_preview": "# Sales narrative\n\n## Audience and desired action\n\n## Delivery language, client terminology, and tone\n\n- Persisted client sector and confidence:\n- Presentation locale and policy source:\n- Explicit override, if any:\n- Authoritative client terminology:\n- Tone constraints:\n\n## Central thesis\n\n## Customer situation and cost of current state\n\n## Evidence-backed insight\n\n## Proposed approach and differentiation\n\n## Proof\n\n## Objections and responses\n\n## Narrative sequence\n\n| Section | Purpose | Claim | Evidence | Visual |\n|---|---|---|---|---|\n\n## Call to action\n\n## Claims requiring validation",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "overlay:sales-storytelling"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "template:visual-pattern-guidance",
      "id": "visual-pattern-guidance",
      "name": "Visual Pattern Guidance",
      "type": "template",
      "path": "templates/visual-patterns",
      "description": "Directory template set: - README.md - class-diagram.md - cluster.md - component-architecture.md - data-flow-diagram.md - er-diagram.md - evidence-chain.md - sequence-diagram.md - system-landscape.md - timeline.md",
      "purpose": "Directory template set: - README.md - class-diagram.md - cluster.md - component-architecture.md - data-flow-diagram.md - er-diagram.md - evidence-chain.md - sequence-diagram.md - system-landscape.md - timeline.md",
      "use_when": [],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [],
      "tags": [],
      "search_terms": [
        "Visual Pattern Guidance",
        "visual-pattern-guidance"
      ],
      "runtime_support": [],
      "source_preview": "Directory template set:\n- README.md\n- class-diagram.md\n- cluster.md\n- component-architecture.md\n- data-flow-diagram.md\n- er-diagram.md\n- evidence-chain.md\n- sequence-diagram.md\n- system-landscape.md\n- timeline.md",
      "related_capabilities": [
        "archetype:development",
        "archetype:legacy-migration",
        "archetype:presentation",
        "archetype:research",
        "overlay:architecture-documentation"
      ],
      "archetypes": [
        "development",
        "legacy-migration",
        "presentation",
        "research"
      ]
    },
    {
      "key": "external:anthropic-official-plugins",
      "id": "anthropic-official-plugins",
      "name": "Anthropic Official Plugins",
      "type": "external",
      "path": "external/sources.yaml",
      "description": "Anthropic-maintained Claude Code plugin marketplace and capability examples.",
      "purpose": "Verified through the GitHub repository API; official provenance does not imply automatic promotion.",
      "use_when": [
        "Trust: OFFICIAL",
        "Tier: 1",
        "Enabled: True"
      ],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [
        "Last reviewed 2026-08-18"
      ],
      "tags": [
        "OFFICIAL",
        "agents",
        "commands",
        "hooks",
        "mcp",
        "plugins",
        "skills",
        "workflows"
      ],
      "search_terms": [
        "agents",
        "Anthropic Official Plugins",
        "anthropic-official-plugins",
        "commands",
        "hooks",
        "mcp",
        "plugins",
        "skills",
        "workflows"
      ],
      "runtime_support": [],
      "source_preview": "{\n  \"id\": \"anthropic-official-plugins\",\n  \"tier\": 1,\n  \"type\": \"github-repository\",\n  \"location\": \"https://github.com/anthropics/claude-plugins-official\",\n  \"repository\": \"anthropics/claude-plugins-official\",\n  \"trust\": \"OFFICIAL\",\n  \"enabled\": true,\n  \"description\": \"Anthropic-maintained Claude Code plugin marketplace and capability examples.\",\n  \"capability_categories\": [\n    \"skills\",\n    \"agents\",\n    \"commands\",\n    \"workflows\",\n    \"plugins\",\n    \"hooks\",\n    \"mcp\"\n  ],\n  \"last_reviewed\": \"2026-08-18\",\n  \"notes\": \"Verified through the GitHub repository API; official provenance does not imply automatic promotion.\"\n}",
      "related_capabilities": [
        "skill:search-external-capabilities"
      ],
      "archetypes": []
    },
    {
      "key": "external:cline-official",
      "id": "cline-official",
      "name": "Cline Official",
      "type": "external",
      "path": "external/sources.yaml",
      "description": "Cline-maintained runtime, workflows, MCP integration, and agent-tooling implementation.",
      "purpose": "Runtime implementation patterns require abstraction before canonical reuse.",
      "use_when": [
        "Trust: OFFICIAL",
        "Tier: 1",
        "Enabled: True"
      ],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [
        "Last reviewed 2026-08-18"
      ],
      "tags": [
        "OFFICIAL",
        "agent-tooling",
        "mcp",
        "prompts",
        "validation",
        "workflows"
      ],
      "search_terms": [
        "agent-tooling",
        "Cline Official",
        "cline-official",
        "mcp",
        "prompts",
        "validation",
        "workflows"
      ],
      "runtime_support": [],
      "source_preview": "{\n  \"id\": \"cline-official\",\n  \"tier\": 1,\n  \"type\": \"github-repository\",\n  \"location\": \"https://github.com/cline/cline\",\n  \"repository\": \"cline/cline\",\n  \"trust\": \"OFFICIAL\",\n  \"enabled\": true,\n  \"description\": \"Cline-maintained runtime, workflows, MCP integration, and agent-tooling implementation.\",\n  \"capability_categories\": [\n    \"agent-tooling\",\n    \"workflows\",\n    \"mcp\",\n    \"prompts\",\n    \"validation\"\n  ],\n  \"last_reviewed\": \"2026-08-18\",\n  \"notes\": \"Runtime implementation patterns require abstraction before canonical reuse.\"\n}",
      "related_capabilities": [
        "skill:search-external-capabilities"
      ],
      "archetypes": []
    },
    {
      "key": "external:ext-github-community-discovery-m-binimran-finance-pack",
      "id": "ext-github-community-discovery-m-binimran-finance-pack",
      "name": "finance-pack forecasting and review workflow",
      "type": "external",
      "path": "external/reviews/ext-github-community-discovery-m-binimran-finance-pack.md",
      "description": "Driver-based project financial forecasting, budgeting, variance analysis, guardrails, and independent numerical review.",
      "purpose": "Provides a coherent forecast, budget, variance, scenario, and independent review model absent from Commons.",
      "use_when": [
        "financial forecasting",
        "budget planning",
        "variance analysis"
      ],
      "not_when": [
        "Discovery does not install or promote this capability automatically."
      ],
      "inputs": [],
      "workflow": [
        "estimate-adm-modernization",
        "plan-work"
      ],
      "outputs": [
        "PROMOTED_GENERALIZED_IDEAS"
      ],
      "validation": [
        "Review status: CURRENT",
        "Security class: MCP/REMOTE TOOLING"
      ],
      "tags": [
        "COMMUNITY",
        "INCORPORATED",
        "claude-code"
      ],
      "search_terms": [
        "budget planning",
        "ext-github-community-discovery-m-binimran-finance-pack",
        "finance-pack forecasting and review workflow",
        "financial forecasting",
        "variance analysis"
      ],
      "runtime_support": [],
      "source_preview": "{\n  \"id\": \"ext-github-community-discovery-m-binimran-finance-pack\",\n  \"name\": \"finance-pack forecasting and review workflow\",\n  \"source_id\": \"github-community-discovery\",\n  \"repository\": \"m-binimran/finance-pack\",\n  \"source_url\": \"https://github.com/m-binimran/finance-pack\",\n  \"path\": \"skills/forecasting/SKILL.md\",\n  \"revision\": \"35ff1b49e7ffa1708296b84503a4e4236fbbff48\",\n  \"source_trust\": \"COMMUNITY\",\n  \"detected_runtime\": \"claude-code\",\n  \"capability_type\": \"composite package\",\n  \"purpose\": \"Driver-based project financial forecasting, budgeting, variance analysis, guardrails, and independent numerical review.\",\n  \"relevance_score\": 32,\n  \"relevance\": [\n    \"financial forecasting\",\n    \"budget planning\",\n    \"variance analysis\"\n  ],\n  \"matched_gaps\": [\n    \"project financial forecasting\",\n    \"independent financial forecast review\"\n  ],\n  \"license\": {\n    \"status\": \"DETECTED\",\n    \"spdx\": \"MIT\",\n    \"scope\": \"repository LICENSE\",\n    \"copy_policy\": \"REVIEW_LICENSE_TERMS_BEFORE_COPYING\"\n  },\n  \"upstream\": {\n    \"default_branch\": \"main\",\n    \"last_commit_at\": \"2026-06-14T18:46:14Z\"\n  },\n  \"why_useful\": \"Provides a coherent forecast, budget, variance, scenario, and independent review model absent from Commons.\",\n  \"commons_overlap\": [\n    \"estimate-adm-modernization\",\n    \"plan-work\"\n  ],\n  \"review_recommendation\": \"PROMOTED_GENERALIZED_IDEAS\",\n  \"security_class\": \"MCP/REMOTE TOOLING\",\n  \"status\": \"INCORPORATED\",\n  \"review_status\": \"CURRENT\",\n  \"review_path\": \"external/reviews/ext-github-community-discovery-m-binimran-finance-pack.md\",\n  \"relationship\": \"INSPIRED-BY\",\n  \"discovered_at\": \"2026-09-02\",\n  \"last_checked\": \"2026-09-02\"\n}",
      "related_capabilities": [
        "skill:review-external-capability"
      ],
      "archetypes": []
    },
    {
      "key": "external:general-web-discovery",
      "id": "general-web-discovery",
      "name": "General Web Discovery",
      "type": "external",
      "path": "external/sources.yaml",
      "description": "Optional discovery of repositories, marketplaces, registries, and official documentation.",
      "purpose": "Disabled by default; arbitrary webpages are never ingested as capabilities.",
      "use_when": [
        "Trust: UNTRUSTED",
        "Tier: 4",
        "Enabled: False"
      ],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [
        "Last reviewed 2026-08-18"
      ],
      "tags": [
        "UNTRUSTED",
        "documentation",
        "marketplaces",
        "registries",
        "repositories"
      ],
      "search_terms": [
        "documentation",
        "General Web Discovery",
        "general-web-discovery",
        "marketplaces",
        "registries",
        "repositories"
      ],
      "runtime_support": [],
      "source_preview": "{\n  \"id\": \"general-web-discovery\",\n  \"tier\": 4,\n  \"type\": \"web-discovery\",\n  \"location\": \"https://www.google.com/search\",\n  \"trust\": \"UNTRUSTED\",\n  \"enabled\": false,\n  \"description\": \"Optional discovery of repositories, marketplaces, registries, and official documentation.\",\n  \"capability_categories\": [\n    \"repositories\",\n    \"marketplaces\",\n    \"registries\",\n    \"documentation\"\n  ],\n  \"last_reviewed\": \"2026-08-18\",\n  \"notes\": \"Disabled by default; arbitrary webpages are never ingested as capabilities.\"\n}",
      "related_capabilities": [
        "skill:search-external-capabilities"
      ],
      "archetypes": []
    },
    {
      "key": "external:github-community-discovery",
      "id": "github-community-discovery",
      "name": "Github Community Discovery",
      "type": "external",
      "path": "external/sources.yaml",
      "description": "Broader GitHub discovery for previously unknown repositories and files.",
      "purpose": "Every result remains untrusted until repository, revision, license, and executable content are reviewed.",
      "use_when": [
        "Trust: COMMUNITY",
        "Tier: 3",
        "Enabled: True"
      ],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [
        "Last reviewed 2026-08-18"
      ],
      "tags": [
        "COMMUNITY",
        "agents",
        "commands",
        "evals",
        "hooks",
        "mcp",
        "plugins",
        "scripts",
        "skills",
        "workflows"
      ],
      "search_terms": [
        "agents",
        "commands",
        "evals",
        "Github Community Discovery",
        "github-community-discovery",
        "hooks",
        "mcp",
        "plugins",
        "scripts",
        "skills",
        "workflows"
      ],
      "runtime_support": [],
      "source_preview": "{\n  \"id\": \"github-community-discovery\",\n  \"tier\": 3,\n  \"type\": \"github-search\",\n  \"location\": \"https://github.com/search\",\n  \"trust\": \"COMMUNITY\",\n  \"enabled\": true,\n  \"description\": \"Broader GitHub discovery for previously unknown repositories and files.\",\n  \"capability_categories\": [\n    \"skills\",\n    \"agents\",\n    \"commands\",\n    \"workflows\",\n    \"plugins\",\n    \"mcp\",\n    \"hooks\",\n    \"scripts\",\n    \"evals\"\n  ],\n  \"last_reviewed\": \"2026-08-18\",\n  \"notes\": \"Every result remains untrusted until repository, revision, license, and executable content are reviewed.\"\n}",
      "related_capabilities": [
        "skill:search-external-capabilities"
      ],
      "archetypes": []
    },
    {
      "key": "external:mcp-official-servers",
      "id": "mcp-official-servers",
      "name": "MCP Official Servers",
      "type": "external",
      "path": "external/sources.yaml",
      "description": "Official Model Context Protocol reference servers and integration examples.",
      "purpose": "License and security scope must be checked per server/package.",
      "use_when": [
        "Trust: OFFICIAL",
        "Tier: 1",
        "Enabled: True"
      ],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [
        "Last reviewed 2026-08-18"
      ],
      "tags": [
        "OFFICIAL",
        "mcp",
        "remote-tooling",
        "security",
        "validation"
      ],
      "search_terms": [
        "mcp",
        "MCP Official Servers",
        "mcp-official-servers",
        "remote-tooling",
        "security",
        "validation"
      ],
      "runtime_support": [],
      "source_preview": "{\n  \"id\": \"mcp-official-servers\",\n  \"tier\": 1,\n  \"type\": \"github-repository\",\n  \"location\": \"https://github.com/modelcontextprotocol/servers\",\n  \"repository\": \"modelcontextprotocol/servers\",\n  \"trust\": \"OFFICIAL\",\n  \"enabled\": true,\n  \"description\": \"Official Model Context Protocol reference servers and integration examples.\",\n  \"capability_categories\": [\n    \"mcp\",\n    \"remote-tooling\",\n    \"security\",\n    \"validation\"\n  ],\n  \"last_reviewed\": \"2026-08-18\",\n  \"notes\": \"License and security scope must be checked per server/package.\"\n}",
      "related_capabilities": [
        "skill:search-external-capabilities"
      ],
      "archetypes": []
    },
    {
      "key": "external:ext-github-community-discovery-footprintai-open-sdlc-skills",
      "id": "ext-github-community-discovery-footprintai-open-sdlc-skills",
      "name": "open-sdlc project delivery roles",
      "type": "external",
      "path": "external/reviews/ext-github-community-discovery-footprintai-open-sdlc-skills.md",
      "description": "Evidence-based sprint planning, delivery coordination, stage gates, verification queues, and status reporting.",
      "purpose": "Adds reusable delivery cadence, evidence gates, dependency status, and action-oriented reporting patterns.",
      "use_when": [
        "project delivery",
        "project management",
        "status reporting"
      ],
      "not_when": [
        "Discovery does not install or promote this capability automatically."
      ],
      "inputs": [],
      "workflow": [
        "plan-work",
        "coordinate-parallel-agents",
        "implement-ready-slice",
        "audit-delivery-traceability"
      ],
      "outputs": [
        "PROMOTED_GENERALIZED_IDEAS"
      ],
      "validation": [
        "Review status: CURRENT",
        "Security class: INSTRUCTIONS ONLY"
      ],
      "tags": [
        "COMMUNITY",
        "INCORPORATED",
        "claude-code"
      ],
      "search_terms": [
        "ext-github-community-discovery-footprintai-open-sdlc-skills",
        "open-sdlc project delivery roles",
        "project delivery",
        "project management",
        "status reporting"
      ],
      "runtime_support": [],
      "source_preview": "{\n  \"id\": \"ext-github-community-discovery-footprintai-open-sdlc-skills\",\n  \"name\": \"open-sdlc project delivery roles\",\n  \"source_id\": \"github-community-discovery\",\n  \"repository\": \"FootprintAI/open-sdlc-skills\",\n  \"source_url\": \"https://github.com/FootprintAI/open-sdlc-skills\",\n  \"path\": \"pm/sprint-delivery.md\",\n  \"revision\": \"75b71b8bb038fdf45df07c9c3258bc08641f04fa\",\n  \"source_trust\": \"COMMUNITY\",\n  \"detected_runtime\": \"claude-code\",\n  \"capability_type\": \"composite package\",\n  \"purpose\": \"Evidence-based sprint planning, delivery coordination, stage gates, verification queues, and status reporting.\",\n  \"relevance_score\": 30,\n  \"relevance\": [\n    \"project delivery\",\n    \"project management\",\n    \"status reporting\"\n  ],\n  \"matched_gaps\": [\n    \"multi-workstream delivery governance\",\n    \"evidence-backed delivery status\"\n  ],\n  \"license\": {\n    \"status\": \"DETECTED\",\n    \"spdx\": \"Apache-2.0\",\n    \"scope\": \"repository LICENSE\",\n    \"copy_policy\": \"REVIEW_LICENSE_TERMS_BEFORE_COPYING\"\n  },\n  \"upstream\": {\n    \"default_branch\": \"main\",\n    \"last_commit_at\": \"2026-08-02T09:49:30Z\"\n  },\n  \"why_useful\": \"Adds reusable delivery cadence, evidence gates, dependency status, and action-oriented reporting patterns.\",\n  \"commons_overlap\": [\n    \"plan-work\",\n    \"coordinate-parallel-agents\",\n    \"implement-ready-slice\",\n    \"audit-delivery-traceability\"\n  ],\n  \"review_recommendation\": \"PROMOTED_GENERALIZED_IDEAS\",\n  \"security_class\": \"INSTRUCTIONS ONLY\",\n  \"status\": \"INCORPORATED\",\n  \"review_status\": \"CURRENT\",\n  \"review_path\": \"external/reviews/ext-github-community-discovery-footprintai-open-sdlc-skills.md\",\n  \"relationship\": \"INSPIRED-BY\",\n  \"discovered_at\": \"2026-09-02\",\n  \"last_checked\": \"2026-09-02\"\n}",
      "related_capabilities": [
        "skill:review-external-capability"
      ],
      "archetypes": []
    },
    {
      "key": "external:openai-official-codex",
      "id": "openai-official-codex",
      "name": "Openai Official Codex",
      "type": "external",
      "path": "external/sources.yaml",
      "description": "OpenAI-maintained Codex implementation, examples, documentation, and tooling patterns.",
      "purpose": "Search for reusable methodology; product implementation code is not automatically a commons candidate.",
      "use_when": [
        "Trust: OFFICIAL",
        "Tier: 1",
        "Enabled: True"
      ],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [
        "Last reviewed 2026-08-18"
      ],
      "tags": [
        "OFFICIAL",
        "agent-tooling",
        "mcp",
        "prompts",
        "skills",
        "validation"
      ],
      "search_terms": [
        "agent-tooling",
        "mcp",
        "Openai Official Codex",
        "openai-official-codex",
        "prompts",
        "skills",
        "validation"
      ],
      "runtime_support": [],
      "source_preview": "{\n  \"id\": \"openai-official-codex\",\n  \"tier\": 1,\n  \"type\": \"github-repository\",\n  \"location\": \"https://github.com/openai/codex\",\n  \"repository\": \"openai/codex\",\n  \"trust\": \"OFFICIAL\",\n  \"enabled\": true,\n  \"description\": \"OpenAI-maintained Codex implementation, examples, documentation, and tooling patterns.\",\n  \"capability_categories\": [\n    \"agent-tooling\",\n    \"skills\",\n    \"prompts\",\n    \"mcp\",\n    \"validation\"\n  ],\n  \"last_reviewed\": \"2026-08-18\",\n  \"notes\": \"Search for reusable methodology; product implementation code is not automatically a commons candidate.\"\n}",
      "related_capabilities": [
        "skill:search-external-capabilities"
      ],
      "archetypes": []
    },
    {
      "key": "external:openai-official-skills",
      "id": "openai-official-skills",
      "name": "Openai Official Skills",
      "type": "external",
      "path": "external/sources.yaml",
      "description": "OpenAI-maintained reusable skill examples and supporting resources.",
      "purpose": "Repository-level license was not asserted by the GitHub API; review license scope per capability.",
      "use_when": [
        "Trust: OFFICIAL",
        "Tier: 1",
        "Enabled: True"
      ],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [
        "Last reviewed 2026-08-18"
      ],
      "tags": [
        "OFFICIAL",
        "scripts",
        "skills",
        "templates",
        "workflows"
      ],
      "search_terms": [
        "Openai Official Skills",
        "openai-official-skills",
        "scripts",
        "skills",
        "templates",
        "workflows"
      ],
      "runtime_support": [],
      "source_preview": "{\n  \"id\": \"openai-official-skills\",\n  \"tier\": 1,\n  \"type\": \"github-repository\",\n  \"location\": \"https://github.com/openai/skills\",\n  \"repository\": \"openai/skills\",\n  \"trust\": \"OFFICIAL\",\n  \"enabled\": true,\n  \"description\": \"OpenAI-maintained reusable skill examples and supporting resources.\",\n  \"capability_categories\": [\n    \"skills\",\n    \"workflows\",\n    \"scripts\",\n    \"templates\"\n  ],\n  \"last_reviewed\": \"2026-08-18\",\n  \"notes\": \"Repository-level license was not asserted by the GitHub API; review license scope per capability.\"\n}",
      "related_capabilities": [
        "skill:search-external-capabilities"
      ],
      "archetypes": []
    },
    {
      "key": "external:opencode-official",
      "id": "opencode-official",
      "name": "Opencode Official",
      "type": "external",
      "path": "external/sources.yaml",
      "description": "OpenCode-maintained runtime, agents, commands, integrations, and tooling patterns.",
      "purpose": "The former sst/opencode URL currently redirects to this authoritative repository.",
      "use_when": [
        "Trust: OFFICIAL",
        "Tier: 1",
        "Enabled: True"
      ],
      "not_when": [],
      "inputs": [],
      "workflow": [],
      "outputs": [],
      "validation": [
        "Last reviewed 2026-08-18"
      ],
      "tags": [
        "OFFICIAL",
        "agent-tooling",
        "agents",
        "commands",
        "mcp",
        "plugins"
      ],
      "search_terms": [
        "agent-tooling",
        "agents",
        "commands",
        "mcp",
        "Opencode Official",
        "opencode-official",
        "plugins"
      ],
      "runtime_support": [],
      "source_preview": "{\n  \"id\": \"opencode-official\",\n  \"tier\": 1,\n  \"type\": \"github-repository\",\n  \"location\": \"https://github.com/anomalyco/opencode\",\n  \"repository\": \"anomalyco/opencode\",\n  \"trust\": \"OFFICIAL\",\n  \"enabled\": true,\n  \"description\": \"OpenCode-maintained runtime, agents, commands, integrations, and tooling patterns.\",\n  \"capability_categories\": [\n    \"agent-tooling\",\n    \"agents\",\n    \"commands\",\n    \"mcp\",\n    \"plugins\"\n  ],\n  \"last_reviewed\": \"2026-08-18\",\n  \"notes\": \"The former sst/opencode URL currently redirects to this authoritative repository.\"\n}",
      "related_capabilities": [
        "skill:search-external-capabilities"
      ],
      "archetypes": []
    }
  ],
  "edges": [
    {
      "source": "adapter:claude-code",
      "target": "archetype:development",
      "relationship": "exposes composition",
      "evidence": "adapters/claude-code/adapter.yaml"
    },
    {
      "source": "adapter:claude-code",
      "target": "archetype:legacy-migration",
      "relationship": "exposes composition",
      "evidence": "adapters/claude-code/adapter.yaml"
    },
    {
      "source": "adapter:claude-code",
      "target": "archetype:presentation",
      "relationship": "exposes composition",
      "evidence": "adapters/claude-code/adapter.yaml"
    },
    {
      "source": "adapter:claude-code",
      "target": "archetype:research",
      "relationship": "exposes composition",
      "evidence": "adapters/claude-code/adapter.yaml"
    },
    {
      "source": "adapter:cline",
      "target": "archetype:development",
      "relationship": "exposes composition",
      "evidence": "adapters/cline/adapter.yaml"
    },
    {
      "source": "adapter:cline",
      "target": "archetype:legacy-migration",
      "relationship": "exposes composition",
      "evidence": "adapters/cline/adapter.yaml"
    },
    {
      "source": "adapter:cline",
      "target": "archetype:presentation",
      "relationship": "exposes composition",
      "evidence": "adapters/cline/adapter.yaml"
    },
    {
      "source": "adapter:cline",
      "target": "archetype:research",
      "relationship": "exposes composition",
      "evidence": "adapters/cline/adapter.yaml"
    },
    {
      "source": "adapter:codex",
      "target": "archetype:development",
      "relationship": "exposes composition",
      "evidence": "adapters/codex/adapter.yaml"
    },
    {
      "source": "adapter:codex",
      "target": "archetype:legacy-migration",
      "relationship": "exposes composition",
      "evidence": "adapters/codex/adapter.yaml"
    },
    {
      "source": "adapter:codex",
      "target": "archetype:presentation",
      "relationship": "exposes composition",
      "evidence": "adapters/codex/adapter.yaml"
    },
    {
      "source": "adapter:codex",
      "target": "archetype:research",
      "relationship": "exposes composition",
      "evidence": "adapters/codex/adapter.yaml"
    },
    {
      "source": "adapter:opencode",
      "target": "archetype:development",
      "relationship": "exposes composition",
      "evidence": "adapters/opencode/adapter.yaml"
    },
    {
      "source": "adapter:opencode",
      "target": "archetype:legacy-migration",
      "relationship": "exposes composition",
      "evidence": "adapters/opencode/adapter.yaml"
    },
    {
      "source": "adapter:opencode",
      "target": "archetype:presentation",
      "relationship": "exposes composition",
      "evidence": "adapters/opencode/adapter.yaml"
    },
    {
      "source": "adapter:opencode",
      "target": "archetype:research",
      "relationship": "exposes composition",
      "evidence": "adapters/opencode/adapter.yaml"
    },
    {
      "source": "agent:financial-forecast-reviewer",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/consulting-delivery/overlay.yaml"
    },
    {
      "source": "agent:financial-forecast-reviewer",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/consulting-delivery/overlay.yaml"
    },
    {
      "source": "agent:financial-forecast-reviewer",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/consulting-delivery/overlay.yaml"
    },
    {
      "source": "archetype:development",
      "target": "agent:architecture-reviewer",
      "relationship": "uses",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "agent:privacy-security-reviewer",
      "relationship": "uses",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "agent:test-behavior-reviewer",
      "relationship": "uses",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "overlay:architecture-documentation",
      "relationship": "recommends",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "overlay:bilingual-client-delivery",
      "relationship": "recommends",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "overlay:branded-html",
      "relationship": "recommends",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "overlay:durable-state",
      "relationship": "recommends",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "overlay:evidence-traceability",
      "relationship": "recommends",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "overlay:living-dashboard",
      "relationship": "recommends",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "overlay:public-sector-client-delivery",
      "relationship": "recommends",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "skill:accessibility-review",
      "relationship": "uses",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "skill:anonymize-data",
      "relationship": "uses",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "skill:complete-openspec-change",
      "relationship": "uses",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "skill:continue-project",
      "relationship": "uses",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "skill:coordinate-parallel-agents",
      "relationship": "uses",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "skill:design-frontend-architecture",
      "relationship": "uses",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "skill:design-test-strategy",
      "relationship": "uses",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "skill:execute-safe-change",
      "relationship": "uses",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "skill:frontend-design",
      "relationship": "uses",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "skill:implement-openspec-change",
      "relationship": "uses",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "skill:implement-ready-slice",
      "relationship": "uses",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "skill:inventory-codebase",
      "relationship": "uses",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "skill:mutation-testing",
      "relationship": "uses",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "skill:plan-work",
      "relationship": "uses",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "skill:protect-git-work",
      "relationship": "uses",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "skill:review-code-change",
      "relationship": "uses",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "skill:review-openspec-change",
      "relationship": "uses",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "skill:review-privacy-security",
      "relationship": "uses",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "skill:specify-openspec-change",
      "relationship": "uses",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "skill:test-driven-development",
      "relationship": "uses",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "skill:verify-openspec-implementation",
      "relationship": "uses",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "template:project-instructions-template",
      "relationship": "uses",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "tool:anonymize-structured-data",
      "relationship": "uses",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "tool:inventory-codebase-tool",
      "relationship": "uses",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "tool:rank-ready-slices",
      "relationship": "uses",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:development",
      "target": "tool:resolve-project-continuation",
      "relationship": "uses",
      "evidence": "archetypes/development/archetype.yaml"
    },
    {
      "source": "archetype:legacy-migration",
      "target": "agent:architecture-reviewer",
      "relationship": "uses",
      "evidence": "archetypes/legacy-migration/archetype.yaml"
    },
    {
      "source": "archetype:legacy-migration",
      "target": "agent:legacy-discovery-specialist",
      "relationship": "uses",
      "evidence": "archetypes/legacy-migration/archetype.yaml"
    },
    {
      "source": "archetype:legacy-migration",
      "target": "agent:test-behavior-reviewer",
      "relationship": "uses",
      "evidence": "archetypes/legacy-migration/archetype.yaml"
    },
    {
      "source": "archetype:legacy-migration",
      "target": "overlay:architecture-documentation",
      "relationship": "recommends",
      "evidence": "archetypes/legacy-migration/archetype.yaml"
    },
    {
      "source": "archetype:legacy-migration",
      "target": "overlay:bilingual-client-delivery",
      "relationship": "recommends",
      "evidence": "archetypes/legacy-migration/archetype.yaml"
    },
    {
      "source": "archetype:legacy-migration",
      "target": "overlay:branded-html",
      "relationship": "recommends",
      "evidence": "archetypes/legacy-migration/archetype.yaml"
    },
    {
      "source": "archetype:legacy-migration",
      "target": "overlay:durable-state",
      "relationship": "recommends",
      "evidence": "archetypes/legacy-migration/archetype.yaml"
    },
    {
      "source": "archetype:legacy-migration",
      "target": "overlay:evidence-traceability",
      "relationship": "recommends",
      "evidence": "archetypes/legacy-migration/archetype.yaml"
    },
    {
      "source": "archetype:legacy-migration",
      "target": "overlay:living-dashboard",
      "relationship": "recommends",
      "evidence": "archetypes/legacy-migration/archetype.yaml"
    },
    {
      "source": "archetype:legacy-migration",
      "target": "overlay:public-sector-client-delivery",
      "relationship": "recommends",
      "evidence": "archetypes/legacy-migration/archetype.yaml"
    },
    {
      "source": "archetype:legacy-migration",
      "target": "skill:analyze-legacy-system",
      "relationship": "uses",
      "evidence": "archetypes/legacy-migration/archetype.yaml"
    },
    {
      "source": "archetype:legacy-migration",
      "target": "skill:continue-project",
      "relationship": "uses",
      "evidence": "archetypes/legacy-migration/archetype.yaml"
    },
    {
      "source": "archetype:legacy-migration",
      "target": "skill:coordinate-parallel-agents",
      "relationship": "uses",
      "evidence": "archetypes/legacy-migration/archetype.yaml"
    },
    {
      "source": "archetype:legacy-migration",
      "target": "skill:derive-modernization-requirements",
      "relationship": "uses",
      "evidence": "archetypes/legacy-migration/archetype.yaml"
    },
    {
      "source": "archetype:legacy-migration",
      "target": "skill:design-test-strategy",
      "relationship": "uses",
      "evidence": "archetypes/legacy-migration/archetype.yaml"
    },
    {
      "source": "archetype:legacy-migration",
      "target": "skill:estimate-adm-modernization",
      "relationship": "uses",
      "evidence": "archetypes/legacy-migration/archetype.yaml"
    },
    {
      "source": "archetype:legacy-migration",
      "target": "skill:inventory-codebase",
      "relationship": "uses",
      "evidence": "archetypes/legacy-migration/archetype.yaml"
    },
    {
      "source": "archetype:legacy-migration",
      "target": "skill:migrate-code-with-evidence",
      "relationship": "uses",
      "evidence": "archetypes/legacy-migration/archetype.yaml"
    },
    {
      "source": "archetype:legacy-migration",
      "target": "skill:mutation-testing",
      "relationship": "uses",
      "evidence": "archetypes/legacy-migration/archetype.yaml"
    },
    {
      "source": "archetype:legacy-migration",
      "target": "skill:plan-work",
      "relationship": "uses",
      "evidence": "archetypes/legacy-migration/archetype.yaml"
    },
    {
      "source": "archetype:legacy-migration",
      "target": "skill:protect-git-work",
      "relationship": "uses",
      "evidence": "archetypes/legacy-migration/archetype.yaml"
    },
    {
      "source": "archetype:legacy-migration",
      "target": "skill:review-openspec-change",
      "relationship": "uses",
      "evidence": "archetypes/legacy-migration/archetype.yaml"
    },
    {
      "source": "archetype:legacy-migration",
      "target": "skill:specify-openspec-change",
      "relationship": "uses",
      "evidence": "archetypes/legacy-migration/archetype.yaml"
    },
    {
      "source": "archetype:legacy-migration",
      "target": "skill:test-driven-development",
      "relationship": "uses",
      "evidence": "archetypes/legacy-migration/archetype.yaml"
    },
    {
      "source": "archetype:legacy-migration",
      "target": "template:evidence-analysis-template",
      "relationship": "uses",
      "evidence": "archetypes/legacy-migration/archetype.yaml"
    },
    {
      "source": "archetype:legacy-migration",
      "target": "template:requirement-record-example",
      "relationship": "uses",
      "evidence": "archetypes/legacy-migration/archetype.yaml"
    },
    {
      "source": "archetype:legacy-migration",
      "target": "tool:coordinate-legacy-analysis",
      "relationship": "uses",
      "evidence": "archetypes/legacy-migration/archetype.yaml"
    },
    {
      "source": "archetype:legacy-migration",
      "target": "tool:extract-legacy-structure",
      "relationship": "uses",
      "evidence": "archetypes/legacy-migration/archetype.yaml"
    },
    {
      "source": "archetype:legacy-migration",
      "target": "tool:inventory-codebase-tool",
      "relationship": "uses",
      "evidence": "archetypes/legacy-migration/archetype.yaml"
    },
    {
      "source": "archetype:legacy-migration",
      "target": "tool:resolve-project-continuation",
      "relationship": "uses",
      "evidence": "archetypes/legacy-migration/archetype.yaml"
    },
    {
      "source": "archetype:legacy-migration",
      "target": "tool:summarize-adm-estimate",
      "relationship": "uses",
      "evidence": "archetypes/legacy-migration/archetype.yaml"
    },
    {
      "source": "archetype:legacy-migration",
      "target": "tool:validate-migration-manifest",
      "relationship": "uses",
      "evidence": "archetypes/legacy-migration/archetype.yaml"
    },
    {
      "source": "archetype:presentation",
      "target": "overlay:architecture-documentation",
      "relationship": "recommends",
      "evidence": "archetypes/presentation/archetype.yaml"
    },
    {
      "source": "archetype:presentation",
      "target": "overlay:bilingual-client-delivery",
      "relationship": "recommends",
      "evidence": "archetypes/presentation/archetype.yaml"
    },
    {
      "source": "archetype:presentation",
      "target": "overlay:branded-html",
      "relationship": "recommends",
      "evidence": "archetypes/presentation/archetype.yaml"
    },
    {
      "source": "archetype:presentation",
      "target": "overlay:durable-state",
      "relationship": "recommends",
      "evidence": "archetypes/presentation/archetype.yaml"
    },
    {
      "source": "archetype:presentation",
      "target": "overlay:living-dashboard",
      "relationship": "recommends",
      "evidence": "archetypes/presentation/archetype.yaml"
    },
    {
      "source": "archetype:presentation",
      "target": "overlay:public-sector-client-delivery",
      "relationship": "recommends",
      "evidence": "archetypes/presentation/archetype.yaml"
    },
    {
      "source": "archetype:presentation",
      "target": "overlay:sales-storytelling",
      "relationship": "recommends",
      "evidence": "archetypes/presentation/archetype.yaml"
    },
    {
      "source": "archetype:presentation",
      "target": "skill:accessibility-review",
      "relationship": "uses",
      "evidence": "archetypes/presentation/archetype.yaml"
    },
    {
      "source": "archetype:presentation",
      "target": "template:project-instructions-template",
      "relationship": "uses",
      "evidence": "archetypes/presentation/archetype.yaml"
    },
    {
      "source": "archetype:research",
      "target": "overlay:architecture-documentation",
      "relationship": "recommends",
      "evidence": "archetypes/research/archetype.yaml"
    },
    {
      "source": "archetype:research",
      "target": "overlay:bilingual-client-delivery",
      "relationship": "recommends",
      "evidence": "archetypes/research/archetype.yaml"
    },
    {
      "source": "archetype:research",
      "target": "overlay:branded-html",
      "relationship": "recommends",
      "evidence": "archetypes/research/archetype.yaml"
    },
    {
      "source": "archetype:research",
      "target": "overlay:durable-state",
      "relationship": "recommends",
      "evidence": "archetypes/research/archetype.yaml"
    },
    {
      "source": "archetype:research",
      "target": "overlay:evidence-traceability",
      "relationship": "recommends",
      "evidence": "archetypes/research/archetype.yaml"
    },
    {
      "source": "archetype:research",
      "target": "overlay:living-dashboard",
      "relationship": "recommends",
      "evidence": "archetypes/research/archetype.yaml"
    },
    {
      "source": "archetype:research",
      "target": "overlay:public-sector-client-delivery",
      "relationship": "recommends",
      "evidence": "archetypes/research/archetype.yaml"
    },
    {
      "source": "archetype:research",
      "target": "skill:deep-research",
      "relationship": "uses",
      "evidence": "archetypes/research/archetype.yaml"
    },
    {
      "source": "archetype:research",
      "target": "template:project-instructions-template",
      "relationship": "uses",
      "evidence": "archetypes/research/archetype.yaml"
    },
    {
      "source": "archetype:research",
      "target": "template:research-plan-template",
      "relationship": "uses",
      "evidence": "archetypes/research/archetype.yaml"
    },
    {
      "source": "archetype:research",
      "target": "template:research-synthesis-template",
      "relationship": "uses",
      "evidence": "archetypes/research/archetype.yaml"
    },
    {
      "source": "eval:agent-evaluations",
      "target": "agent:architecture-reviewer",
      "relationship": "validates",
      "evidence": "evals/agents/scenarios.yaml"
    },
    {
      "source": "eval:agent-evaluations",
      "target": "agent:financial-forecast-reviewer",
      "relationship": "validates",
      "evidence": "evals/agents/scenarios.yaml"
    },
    {
      "source": "eval:agent-evaluations",
      "target": "agent:legacy-discovery-specialist",
      "relationship": "validates",
      "evidence": "evals/agents/scenarios.yaml"
    },
    {
      "source": "eval:agent-evaluations",
      "target": "agent:privacy-security-reviewer",
      "relationship": "validates",
      "evidence": "evals/agents/scenarios.yaml"
    },
    {
      "source": "eval:agent-evaluations",
      "target": "agent:test-behavior-reviewer",
      "relationship": "validates",
      "evidence": "evals/agents/scenarios.yaml"
    },
    {
      "source": "eval:external-evaluations",
      "target": "skill:review-external-capability",
      "relationship": "validates",
      "evidence": "evals/external/scenarios.yaml"
    },
    {
      "source": "eval:external-evaluations",
      "target": "skill:search-external-capabilities",
      "relationship": "validates",
      "evidence": "evals/external/scenarios.yaml"
    },
    {
      "source": "eval:initializer-evaluations",
      "target": "skill:initialize-project",
      "relationship": "validates",
      "evidence": "evals/initialization/scenarios.yaml"
    },
    {
      "source": "eval:natural-language-initializer-evaluations",
      "target": "skill:initialize-project",
      "relationship": "validates",
      "evidence": "evals/initialization/natural-language-scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:accessibility-review",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:analyze-legacy-system",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:anonymize-data",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:audit-delivery-traceability",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:build-living-dashboard",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:complete-openspec-change",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:continue-project",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:coordinate-parallel-agents",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:create-branded-html-artifact",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:create-class-diagram",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:create-component-architecture-diagram",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:create-data-flow-diagram",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:create-er-diagram",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:create-sequence-diagram",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:create-system-landscape-diagram",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:create-technical-diagram",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:deconstruct-problem-first-principles",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:deep-research",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:derive-modernization-requirements",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:design-frontend-architecture",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:design-test-strategy",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:estimate-adm-modernization",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:execute-safe-change",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:forecast-project-financials",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:frontend-design",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:generate-synthetic-fixtures",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:implement-openspec-change",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:implement-ready-slice",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:initialize-project",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:inventory-codebase",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:localize-client-artifact",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:maintain-project-memory",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:manage-project-delivery",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:migrate-code-with-evidence",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:mutation-testing",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:plan-work",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:polish-html-artifact",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:promote-to-commons",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:protect-git-work",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:review-code-change",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:review-external-capability",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:review-for-commons",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:review-openspec-change",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:review-privacy-security",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:sales-storytelling",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:search-external-capabilities",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:specify-openspec-change",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:test-driven-development",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:update-commons-presentation",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:validate-visual-artifact",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:validate-work-item-assumptions",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "eval:skill-evaluations",
      "target": "skill:verify-openspec-implementation",
      "relationship": "validates",
      "evidence": "evals/skills/scenarios.yaml"
    },
    {
      "source": "external:anthropic-official-plugins",
      "target": "skill:search-external-capabilities",
      "relationship": "feeds discovery",
      "evidence": "external/sources.yaml"
    },
    {
      "source": "external:cline-official",
      "target": "skill:search-external-capabilities",
      "relationship": "feeds discovery",
      "evidence": "external/sources.yaml"
    },
    {
      "source": "external:ext-github-community-discovery-footprintai-open-sdlc-skills",
      "target": "skill:review-external-capability",
      "relationship": "reviewed by",
      "evidence": "external/reviews/ext-github-community-discovery-footprintai-open-sdlc-skills.md"
    },
    {
      "source": "external:ext-github-community-discovery-m-binimran-finance-pack",
      "target": "skill:review-external-capability",
      "relationship": "reviewed by",
      "evidence": "external/reviews/ext-github-community-discovery-m-binimran-finance-pack.md"
    },
    {
      "source": "external:general-web-discovery",
      "target": "skill:search-external-capabilities",
      "relationship": "feeds discovery",
      "evidence": "external/sources.yaml"
    },
    {
      "source": "external:github-community-discovery",
      "target": "skill:search-external-capabilities",
      "relationship": "feeds discovery",
      "evidence": "external/sources.yaml"
    },
    {
      "source": "external:mcp-official-servers",
      "target": "skill:search-external-capabilities",
      "relationship": "feeds discovery",
      "evidence": "external/sources.yaml"
    },
    {
      "source": "external:openai-official-codex",
      "target": "skill:search-external-capabilities",
      "relationship": "feeds discovery",
      "evidence": "external/sources.yaml"
    },
    {
      "source": "external:openai-official-skills",
      "target": "skill:search-external-capabilities",
      "relationship": "feeds discovery",
      "evidence": "external/sources.yaml"
    },
    {
      "source": "external:opencode-official",
      "target": "skill:search-external-capabilities",
      "relationship": "feeds discovery",
      "evidence": "external/sources.yaml"
    },
    {
      "source": "overlay:architecture-documentation",
      "target": "archetype:development",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "overlay:architecture-documentation",
      "target": "archetype:legacy-migration",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "overlay:architecture-documentation",
      "target": "archetype:presentation",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "overlay:architecture-documentation",
      "target": "archetype:research",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "overlay:architecture-documentation",
      "target": "skill:create-class-diagram",
      "relationship": "uses",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "overlay:architecture-documentation",
      "target": "skill:create-component-architecture-diagram",
      "relationship": "uses",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "overlay:architecture-documentation",
      "target": "skill:create-data-flow-diagram",
      "relationship": "uses",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "overlay:architecture-documentation",
      "target": "skill:create-er-diagram",
      "relationship": "uses",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "overlay:architecture-documentation",
      "target": "skill:create-sequence-diagram",
      "relationship": "uses",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "overlay:architecture-documentation",
      "target": "skill:create-system-landscape-diagram",
      "relationship": "uses",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "overlay:architecture-documentation",
      "target": "skill:create-technical-diagram",
      "relationship": "uses",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "overlay:architecture-documentation",
      "target": "skill:plan-work",
      "relationship": "uses",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "overlay:architecture-documentation",
      "target": "template:diagram-model-example",
      "relationship": "uses",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "overlay:architecture-documentation",
      "target": "template:visual-pattern-guidance",
      "relationship": "uses",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "overlay:architecture-documentation",
      "target": "tool:validate-diagram-model",
      "relationship": "uses",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "overlay:bilingual-client-delivery",
      "target": "archetype:development",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "overlay:bilingual-client-delivery",
      "target": "archetype:legacy-migration",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "overlay:bilingual-client-delivery",
      "target": "archetype:presentation",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "overlay:bilingual-client-delivery",
      "target": "archetype:research",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "overlay:bilingual-client-delivery",
      "target": "skill:localize-client-artifact",
      "relationship": "uses",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "overlay:bilingual-client-delivery",
      "target": "skill:validate-visual-artifact",
      "relationship": "uses",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "overlay:bilingual-client-delivery",
      "target": "template:bilingual-artifact-runtime",
      "relationship": "uses",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "overlay:bilingual-client-delivery",
      "target": "template:localization-manifest-example",
      "relationship": "uses",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "overlay:bilingual-client-delivery",
      "target": "tool:validate-client-localization",
      "relationship": "uses",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "overlay:bilingual-client-delivery",
      "target": "tool:validate-html",
      "relationship": "uses",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "overlay:branded-html",
      "target": "archetype:development",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/branded-html/overlay.yaml"
    },
    {
      "source": "overlay:branded-html",
      "target": "archetype:legacy-migration",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/branded-html/overlay.yaml"
    },
    {
      "source": "overlay:branded-html",
      "target": "archetype:presentation",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/branded-html/overlay.yaml"
    },
    {
      "source": "overlay:branded-html",
      "target": "archetype:research",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/branded-html/overlay.yaml"
    },
    {
      "source": "overlay:branded-html",
      "target": "skill:create-branded-html-artifact",
      "relationship": "uses",
      "evidence": "archetypes/overlays/branded-html/overlay.yaml"
    },
    {
      "source": "overlay:branded-html",
      "target": "skill:validate-visual-artifact",
      "relationship": "uses",
      "evidence": "archetypes/overlays/branded-html/overlay.yaml"
    },
    {
      "source": "overlay:branded-html",
      "target": "template:editorial-html-shell",
      "relationship": "uses",
      "evidence": "archetypes/overlays/branded-html/overlay.yaml"
    },
    {
      "source": "overlay:branded-html",
      "target": "tool:validate-html",
      "relationship": "uses",
      "evidence": "archetypes/overlays/branded-html/overlay.yaml"
    },
    {
      "source": "overlay:consulting-delivery",
      "target": "agent:financial-forecast-reviewer",
      "relationship": "uses",
      "evidence": "archetypes/overlays/consulting-delivery/overlay.yaml"
    },
    {
      "source": "overlay:consulting-delivery",
      "target": "archetype:development",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/consulting-delivery/overlay.yaml"
    },
    {
      "source": "overlay:consulting-delivery",
      "target": "archetype:legacy-migration",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/consulting-delivery/overlay.yaml"
    },
    {
      "source": "overlay:consulting-delivery",
      "target": "archetype:research",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/consulting-delivery/overlay.yaml"
    },
    {
      "source": "overlay:consulting-delivery",
      "target": "skill:forecast-project-financials",
      "relationship": "uses",
      "evidence": "archetypes/overlays/consulting-delivery/overlay.yaml"
    },
    {
      "source": "overlay:consulting-delivery",
      "target": "skill:manage-project-delivery",
      "relationship": "uses",
      "evidence": "archetypes/overlays/consulting-delivery/overlay.yaml"
    },
    {
      "source": "overlay:consulting-delivery",
      "target": "tool:analyze-project-delivery",
      "relationship": "uses",
      "evidence": "archetypes/overlays/consulting-delivery/overlay.yaml"
    },
    {
      "source": "overlay:consulting-delivery",
      "target": "tool:calculate-project-financial-forecast",
      "relationship": "uses",
      "evidence": "archetypes/overlays/consulting-delivery/overlay.yaml"
    },
    {
      "source": "overlay:durable-state",
      "target": "archetype:development",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/durable-state/overlay.yaml"
    },
    {
      "source": "overlay:durable-state",
      "target": "archetype:legacy-migration",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/durable-state/overlay.yaml"
    },
    {
      "source": "overlay:durable-state",
      "target": "archetype:presentation",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/durable-state/overlay.yaml"
    },
    {
      "source": "overlay:durable-state",
      "target": "archetype:research",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/durable-state/overlay.yaml"
    },
    {
      "source": "overlay:durable-state",
      "target": "skill:maintain-project-memory",
      "relationship": "uses",
      "evidence": "archetypes/overlays/durable-state/overlay.yaml"
    },
    {
      "source": "overlay:durable-state",
      "target": "template:project-memory-template-set",
      "relationship": "uses",
      "evidence": "archetypes/overlays/durable-state/overlay.yaml"
    },
    {
      "source": "overlay:durable-state",
      "target": "tool:manage-project-memory",
      "relationship": "uses",
      "evidence": "archetypes/overlays/durable-state/overlay.yaml"
    },
    {
      "source": "overlay:evidence-traceability",
      "target": "archetype:development",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/evidence-traceability/overlay.yaml"
    },
    {
      "source": "overlay:evidence-traceability",
      "target": "archetype:legacy-migration",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/evidence-traceability/overlay.yaml"
    },
    {
      "source": "overlay:evidence-traceability",
      "target": "archetype:research",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/evidence-traceability/overlay.yaml"
    },
    {
      "source": "overlay:evidence-traceability",
      "target": "skill:audit-delivery-traceability",
      "relationship": "uses",
      "evidence": "archetypes/overlays/evidence-traceability/overlay.yaml"
    },
    {
      "source": "overlay:evidence-traceability",
      "target": "skill:derive-modernization-requirements",
      "relationship": "uses",
      "evidence": "archetypes/overlays/evidence-traceability/overlay.yaml"
    },
    {
      "source": "overlay:evidence-traceability",
      "target": "template:acceptance-audit-template",
      "relationship": "uses",
      "evidence": "archetypes/overlays/evidence-traceability/overlay.yaml"
    },
    {
      "source": "overlay:evidence-traceability",
      "target": "template:evidence-record-example",
      "relationship": "uses",
      "evidence": "archetypes/overlays/evidence-traceability/overlay.yaml"
    },
    {
      "source": "overlay:evidence-traceability",
      "target": "template:requirement-record-example",
      "relationship": "uses",
      "evidence": "archetypes/overlays/evidence-traceability/overlay.yaml"
    },
    {
      "source": "overlay:evidence-traceability",
      "target": "tool:audit-trace-graph",
      "relationship": "uses",
      "evidence": "archetypes/overlays/evidence-traceability/overlay.yaml"
    },
    {
      "source": "overlay:evidence-traceability",
      "target": "tool:audit-trace-matrix",
      "relationship": "uses",
      "evidence": "archetypes/overlays/evidence-traceability/overlay.yaml"
    },
    {
      "source": "overlay:living-dashboard",
      "target": "archetype:development",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "overlay:living-dashboard",
      "target": "archetype:legacy-migration",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "overlay:living-dashboard",
      "target": "archetype:presentation",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "overlay:living-dashboard",
      "target": "archetype:research",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "overlay:living-dashboard",
      "target": "skill:accessibility-review",
      "relationship": "uses",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "overlay:living-dashboard",
      "target": "skill:build-living-dashboard",
      "relationship": "uses",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "overlay:living-dashboard",
      "target": "skill:validate-visual-artifact",
      "relationship": "uses",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "overlay:living-dashboard",
      "target": "template:dashboard-data-example",
      "relationship": "uses",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "overlay:living-dashboard",
      "target": "template:dashboard-shell",
      "relationship": "uses",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "overlay:living-dashboard",
      "target": "template:dashboard-structure",
      "relationship": "uses",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "overlay:living-dashboard",
      "target": "tool:build-dashboard",
      "relationship": "uses",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "overlay:living-dashboard",
      "target": "tool:validate-dashboard-structure",
      "relationship": "uses",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "overlay:living-dashboard",
      "target": "tool:validate-dashboard-visual",
      "relationship": "uses",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "overlay:living-dashboard",
      "target": "tool:validate-html",
      "relationship": "uses",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "overlay:public-sector-client-delivery",
      "target": "archetype:development",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/public-sector-client-delivery/overlay.yaml"
    },
    {
      "source": "overlay:public-sector-client-delivery",
      "target": "archetype:legacy-migration",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/public-sector-client-delivery/overlay.yaml"
    },
    {
      "source": "overlay:public-sector-client-delivery",
      "target": "archetype:presentation",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/public-sector-client-delivery/overlay.yaml"
    },
    {
      "source": "overlay:public-sector-client-delivery",
      "target": "archetype:research",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/public-sector-client-delivery/overlay.yaml"
    },
    {
      "source": "overlay:public-sector-client-delivery",
      "target": "skill:accessibility-review",
      "relationship": "uses",
      "evidence": "archetypes/overlays/public-sector-client-delivery/overlay.yaml"
    },
    {
      "source": "overlay:public-sector-client-delivery",
      "target": "skill:validate-visual-artifact",
      "relationship": "uses",
      "evidence": "archetypes/overlays/public-sector-client-delivery/overlay.yaml"
    },
    {
      "source": "overlay:sales-storytelling",
      "target": "archetype:development",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/sales-storytelling/overlay.yaml"
    },
    {
      "source": "overlay:sales-storytelling",
      "target": "archetype:legacy-migration",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/sales-storytelling/overlay.yaml"
    },
    {
      "source": "overlay:sales-storytelling",
      "target": "archetype:presentation",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/sales-storytelling/overlay.yaml"
    },
    {
      "source": "overlay:sales-storytelling",
      "target": "archetype:research",
      "relationship": "applies to",
      "evidence": "archetypes/overlays/sales-storytelling/overlay.yaml"
    },
    {
      "source": "overlay:sales-storytelling",
      "target": "skill:sales-storytelling",
      "relationship": "uses",
      "evidence": "archetypes/overlays/sales-storytelling/overlay.yaml"
    },
    {
      "source": "overlay:sales-storytelling",
      "target": "template:sales-narrative-template",
      "relationship": "uses",
      "evidence": "archetypes/overlays/sales-storytelling/overlay.yaml"
    },
    {
      "source": "skill:accessibility-review",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "skill:accessibility-review",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "skill:accessibility-review",
      "target": "archetype:presentation",
      "relationship": "available in",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "skill:accessibility-review",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "skill:analyze-legacy-system",
      "target": "skill:audit-delivery-traceability",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:analyze-legacy-system",
      "target": "skill:build-living-dashboard",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:analyze-legacy-system",
      "target": "skill:coordinate-parallel-agents",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:analyze-legacy-system",
      "target": "skill:derive-modernization-requirements",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:analyze-legacy-system",
      "target": "skill:inventory-codebase",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:analyze-legacy-system",
      "target": "tool:coordinate-legacy-analysis",
      "relationship": "ships tool",
      "evidence": "skills/analyze-legacy-system/scripts/coordinate_analysis.py"
    },
    {
      "source": "skill:analyze-legacy-system",
      "target": "tool:extract-legacy-structure",
      "relationship": "ships tool",
      "evidence": "skills/analyze-legacy-system/scripts/extract_legacy_structure.py"
    },
    {
      "source": "skill:anonymize-data",
      "target": "skill:generate-synthetic-fixtures",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:anonymize-data",
      "target": "skill:review-privacy-security",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:anonymize-data",
      "target": "tool:anonymize-structured-data",
      "relationship": "ships tool",
      "evidence": "skills/anonymize-data/scripts/anonymize_data.py"
    },
    {
      "source": "skill:audit-delivery-traceability",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/evidence-traceability/overlay.yaml"
    },
    {
      "source": "skill:audit-delivery-traceability",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/evidence-traceability/overlay.yaml"
    },
    {
      "source": "skill:audit-delivery-traceability",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/evidence-traceability/overlay.yaml"
    },
    {
      "source": "skill:audit-delivery-traceability",
      "target": "tool:audit-trace-graph",
      "relationship": "ships tool",
      "evidence": "skills/audit-delivery-traceability/scripts/audit_trace_graph.py"
    },
    {
      "source": "skill:audit-delivery-traceability",
      "target": "tool:audit-trace-matrix",
      "relationship": "ships tool",
      "evidence": "skills/audit-delivery-traceability/scripts/audit_trace_matrix.py"
    },
    {
      "source": "skill:build-living-dashboard",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "skill:build-living-dashboard",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "skill:build-living-dashboard",
      "target": "archetype:presentation",
      "relationship": "available in",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "skill:build-living-dashboard",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "skill:build-living-dashboard",
      "target": "skill:audit-delivery-traceability",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:build-living-dashboard",
      "target": "skill:derive-modernization-requirements",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:build-living-dashboard",
      "target": "skill:localize-client-artifact",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:build-living-dashboard",
      "target": "skill:polish-html-artifact",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:build-living-dashboard",
      "target": "skill:specify-openspec-change",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:build-living-dashboard",
      "target": "skill:validate-visual-artifact",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:build-living-dashboard",
      "target": "skill:verify-openspec-implementation",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:build-living-dashboard",
      "target": "tool:build-dashboard",
      "relationship": "ships tool",
      "evidence": "skills/build-living-dashboard/scripts/build_dashboard.py"
    },
    {
      "source": "skill:build-living-dashboard",
      "target": "tool:validate-dashboard-semantics",
      "relationship": "ships tool",
      "evidence": "skills/build-living-dashboard/scripts/validate_dashboard_semantics.py"
    },
    {
      "source": "skill:build-living-dashboard",
      "target": "tool:validate-dashboard-structure",
      "relationship": "ships tool",
      "evidence": "skills/build-living-dashboard/scripts/validate_dashboard_structure.py"
    },
    {
      "source": "skill:build-living-dashboard",
      "target": "tool:validate-dashboard-visual",
      "relationship": "ships tool",
      "evidence": "skills/build-living-dashboard/scripts/validate_dashboard_visual.py"
    },
    {
      "source": "skill:complete-openspec-change",
      "target": "skill:specify-openspec-change",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:complete-openspec-change",
      "target": "skill:verify-openspec-implementation",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:continue-project",
      "target": "skill:analyze-legacy-system",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:continue-project",
      "target": "skill:build-living-dashboard",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:continue-project",
      "target": "skill:derive-modernization-requirements",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:continue-project",
      "target": "skill:implement-openspec-change",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:continue-project",
      "target": "skill:implement-ready-slice",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:continue-project",
      "target": "skill:initialize-project",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:continue-project",
      "target": "skill:specify-openspec-change",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:continue-project",
      "target": "skill:verify-openspec-implementation",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:continue-project",
      "target": "tool:resolve-project-continuation",
      "relationship": "ships tool",
      "evidence": "skills/continue-project/scripts/resolve_project_continuation.py"
    },
    {
      "source": "skill:create-branded-html-artifact",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/branded-html/overlay.yaml"
    },
    {
      "source": "skill:create-branded-html-artifact",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/branded-html/overlay.yaml"
    },
    {
      "source": "skill:create-branded-html-artifact",
      "target": "archetype:presentation",
      "relationship": "available in",
      "evidence": "archetypes/overlays/branded-html/overlay.yaml"
    },
    {
      "source": "skill:create-branded-html-artifact",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/branded-html/overlay.yaml"
    },
    {
      "source": "skill:create-branded-html-artifact",
      "target": "skill:polish-html-artifact",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-branded-html-artifact",
      "target": "skill:validate-visual-artifact",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-class-diagram",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "skill:create-class-diagram",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "skill:create-class-diagram",
      "target": "archetype:presentation",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "skill:create-class-diagram",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "skill:create-class-diagram",
      "target": "skill:analyze-legacy-system",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-class-diagram",
      "target": "skill:create-technical-diagram",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-class-diagram",
      "target": "skill:validate-visual-artifact",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-component-architecture-diagram",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "skill:create-component-architecture-diagram",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "skill:create-component-architecture-diagram",
      "target": "archetype:presentation",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "skill:create-component-architecture-diagram",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "skill:create-component-architecture-diagram",
      "target": "skill:analyze-legacy-system",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-component-architecture-diagram",
      "target": "skill:create-system-landscape-diagram",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-component-architecture-diagram",
      "target": "skill:create-technical-diagram",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-component-architecture-diagram",
      "target": "skill:validate-visual-artifact",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-data-flow-diagram",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "skill:create-data-flow-diagram",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "skill:create-data-flow-diagram",
      "target": "archetype:presentation",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "skill:create-data-flow-diagram",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "skill:create-data-flow-diagram",
      "target": "skill:analyze-legacy-system",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-data-flow-diagram",
      "target": "skill:create-technical-diagram",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-data-flow-diagram",
      "target": "skill:review-privacy-security",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-data-flow-diagram",
      "target": "skill:validate-visual-artifact",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-er-diagram",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "skill:create-er-diagram",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "skill:create-er-diagram",
      "target": "archetype:presentation",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "skill:create-er-diagram",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "skill:create-er-diagram",
      "target": "skill:analyze-legacy-system",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-er-diagram",
      "target": "skill:create-technical-diagram",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-er-diagram",
      "target": "skill:validate-visual-artifact",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-sequence-diagram",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "skill:create-sequence-diagram",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "skill:create-sequence-diagram",
      "target": "archetype:presentation",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "skill:create-sequence-diagram",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "skill:create-sequence-diagram",
      "target": "skill:analyze-legacy-system",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-sequence-diagram",
      "target": "skill:create-component-architecture-diagram",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-sequence-diagram",
      "target": "skill:create-technical-diagram",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-sequence-diagram",
      "target": "skill:validate-visual-artifact",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-system-landscape-diagram",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "skill:create-system-landscape-diagram",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "skill:create-system-landscape-diagram",
      "target": "archetype:presentation",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "skill:create-system-landscape-diagram",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "skill:create-system-landscape-diagram",
      "target": "skill:analyze-legacy-system",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-system-landscape-diagram",
      "target": "skill:create-component-architecture-diagram",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-system-landscape-diagram",
      "target": "skill:create-technical-diagram",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-system-landscape-diagram",
      "target": "skill:validate-visual-artifact",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-technical-diagram",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "skill:create-technical-diagram",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "skill:create-technical-diagram",
      "target": "archetype:presentation",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "skill:create-technical-diagram",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "skill:create-technical-diagram",
      "target": "skill:build-living-dashboard",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-technical-diagram",
      "target": "skill:create-branded-html-artifact",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-technical-diagram",
      "target": "skill:create-class-diagram",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-technical-diagram",
      "target": "skill:create-component-architecture-diagram",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-technical-diagram",
      "target": "skill:create-data-flow-diagram",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-technical-diagram",
      "target": "skill:create-er-diagram",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-technical-diagram",
      "target": "skill:create-sequence-diagram",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-technical-diagram",
      "target": "skill:create-system-landscape-diagram",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-technical-diagram",
      "target": "skill:validate-visual-artifact",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:create-technical-diagram",
      "target": "tool:validate-diagram-model",
      "relationship": "ships tool",
      "evidence": "skills/create-technical-diagram/scripts/validate_diagram_model.py"
    },
    {
      "source": "skill:deconstruct-problem-first-principles",
      "target": "skill:deep-research",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:deconstruct-problem-first-principles",
      "target": "skill:design-test-strategy",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:deconstruct-problem-first-principles",
      "target": "skill:plan-work",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:deconstruct-problem-first-principles",
      "target": "skill:validate-work-item-assumptions",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:derive-modernization-requirements",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/evidence-traceability/overlay.yaml"
    },
    {
      "source": "skill:derive-modernization-requirements",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/evidence-traceability/overlay.yaml"
    },
    {
      "source": "skill:derive-modernization-requirements",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/evidence-traceability/overlay.yaml"
    },
    {
      "source": "skill:derive-modernization-requirements",
      "target": "skill:analyze-legacy-system",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:derive-modernization-requirements",
      "target": "skill:build-living-dashboard",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:derive-modernization-requirements",
      "target": "skill:specify-openspec-change",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:design-frontend-architecture",
      "target": "skill:frontend-design",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:design-frontend-architecture",
      "target": "skill:plan-work",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:design-test-strategy",
      "target": "skill:mutation-testing",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:design-test-strategy",
      "target": "skill:test-driven-development",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:estimate-adm-modernization",
      "target": "tool:summarize-adm-estimate",
      "relationship": "ships tool",
      "evidence": "skills/estimate-adm-modernization/scripts/summarize_adm_estimate.py"
    },
    {
      "source": "skill:forecast-project-financials",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/consulting-delivery/overlay.yaml"
    },
    {
      "source": "skill:forecast-project-financials",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/consulting-delivery/overlay.yaml"
    },
    {
      "source": "skill:forecast-project-financials",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/consulting-delivery/overlay.yaml"
    },
    {
      "source": "skill:forecast-project-financials",
      "target": "skill:estimate-adm-modernization",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:forecast-project-financials",
      "target": "skill:manage-project-delivery",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:forecast-project-financials",
      "target": "tool:calculate-project-financial-forecast",
      "relationship": "ships tool",
      "evidence": "skills/forecast-project-financials/scripts/calculate_project_forecast.py"
    },
    {
      "source": "skill:generate-synthetic-fixtures",
      "target": "skill:anonymize-data",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:generate-synthetic-fixtures",
      "target": "skill:design-test-strategy",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:generate-synthetic-fixtures",
      "target": "skill:review-privacy-security",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:generate-synthetic-fixtures",
      "target": "skill:test-driven-development",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:implement-openspec-change",
      "target": "skill:implement-ready-slice",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:implement-openspec-change",
      "target": "skill:mutation-testing",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:implement-openspec-change",
      "target": "skill:review-openspec-change",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:implement-openspec-change",
      "target": "skill:test-driven-development",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:implement-openspec-change",
      "target": "skill:verify-openspec-implementation",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:implement-ready-slice",
      "target": "skill:implement-openspec-change",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:implement-ready-slice",
      "target": "skill:mutation-testing",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:implement-ready-slice",
      "target": "skill:test-driven-development",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:implement-ready-slice",
      "target": "skill:verify-openspec-implementation",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:implement-ready-slice",
      "target": "tool:rank-ready-slices",
      "relationship": "ships tool",
      "evidence": "skills/implement-ready-slice/scripts/rank_slices.py"
    },
    {
      "source": "skill:initialize-project",
      "target": "skill:continue-project",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:inventory-codebase",
      "target": "tool:inventory-codebase-tool",
      "relationship": "ships tool",
      "evidence": "skills/inventory-codebase/scripts/inventory_codebase.py"
    },
    {
      "source": "skill:localize-client-artifact",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "skill:localize-client-artifact",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "skill:localize-client-artifact",
      "target": "archetype:presentation",
      "relationship": "available in",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "skill:localize-client-artifact",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "skill:localize-client-artifact",
      "target": "skill:build-living-dashboard",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:localize-client-artifact",
      "target": "skill:create-branded-html-artifact",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:localize-client-artifact",
      "target": "skill:validate-visual-artifact",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:localize-client-artifact",
      "target": "tool:validate-client-localization",
      "relationship": "ships tool",
      "evidence": "skills/localize-client-artifact/scripts/validate_localization.py"
    },
    {
      "source": "skill:maintain-project-memory",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/durable-state/overlay.yaml"
    },
    {
      "source": "skill:maintain-project-memory",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/durable-state/overlay.yaml"
    },
    {
      "source": "skill:maintain-project-memory",
      "target": "archetype:presentation",
      "relationship": "available in",
      "evidence": "archetypes/overlays/durable-state/overlay.yaml"
    },
    {
      "source": "skill:maintain-project-memory",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/durable-state/overlay.yaml"
    },
    {
      "source": "skill:maintain-project-memory",
      "target": "skill:analyze-legacy-system",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:maintain-project-memory",
      "target": "skill:continue-project",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:maintain-project-memory",
      "target": "skill:coordinate-parallel-agents",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:maintain-project-memory",
      "target": "tool:manage-project-memory",
      "relationship": "ships tool",
      "evidence": "skills/maintain-project-memory/scripts/manage_project_memory.py"
    },
    {
      "source": "skill:manage-project-delivery",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/consulting-delivery/overlay.yaml"
    },
    {
      "source": "skill:manage-project-delivery",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/consulting-delivery/overlay.yaml"
    },
    {
      "source": "skill:manage-project-delivery",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/consulting-delivery/overlay.yaml"
    },
    {
      "source": "skill:manage-project-delivery",
      "target": "skill:audit-delivery-traceability",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:manage-project-delivery",
      "target": "skill:coordinate-parallel-agents",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:manage-project-delivery",
      "target": "skill:forecast-project-financials",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:manage-project-delivery",
      "target": "skill:plan-work",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:manage-project-delivery",
      "target": "tool:analyze-project-delivery",
      "relationship": "ships tool",
      "evidence": "skills/manage-project-delivery/scripts/analyze_project_delivery.py"
    },
    {
      "source": "skill:migrate-code-with-evidence",
      "target": "skill:analyze-legacy-system",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:migrate-code-with-evidence",
      "target": "skill:derive-modernization-requirements",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:migrate-code-with-evidence",
      "target": "skill:test-driven-development",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:migrate-code-with-evidence",
      "target": "tool:validate-migration-manifest",
      "relationship": "ships tool",
      "evidence": "skills/migrate-code-with-evidence/scripts/validate_migration_manifest.py"
    },
    {
      "source": "skill:mutation-testing",
      "target": "skill:build-living-dashboard",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:mutation-testing",
      "target": "skill:design-test-strategy",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:mutation-testing",
      "target": "skill:implement-ready-slice",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:mutation-testing",
      "target": "skill:migrate-code-with-evidence",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:mutation-testing",
      "target": "skill:test-driven-development",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:mutation-testing",
      "target": "skill:verify-openspec-implementation",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:plan-work",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "skill:plan-work",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "skill:plan-work",
      "target": "archetype:presentation",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "skill:plan-work",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "skill:polish-html-artifact",
      "target": "skill:accessibility-review",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:polish-html-artifact",
      "target": "skill:build-living-dashboard",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:polish-html-artifact",
      "target": "skill:create-branded-html-artifact",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:polish-html-artifact",
      "target": "skill:frontend-design",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:polish-html-artifact",
      "target": "skill:validate-visual-artifact",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:promote-to-commons",
      "target": "skill:initialize-project",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:promote-to-commons",
      "target": "skill:review-external-capability",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:promote-to-commons",
      "target": "skill:review-for-commons",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:review-external-capability",
      "target": "skill:promote-to-commons",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:review-for-commons",
      "target": "skill:promote-to-commons",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:review-openspec-change",
      "target": "skill:implement-openspec-change",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:review-openspec-change",
      "target": "skill:specify-openspec-change",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:sales-storytelling",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/sales-storytelling/overlay.yaml"
    },
    {
      "source": "skill:sales-storytelling",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/sales-storytelling/overlay.yaml"
    },
    {
      "source": "skill:sales-storytelling",
      "target": "archetype:presentation",
      "relationship": "available in",
      "evidence": "archetypes/overlays/sales-storytelling/overlay.yaml"
    },
    {
      "source": "skill:sales-storytelling",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/sales-storytelling/overlay.yaml"
    },
    {
      "source": "skill:specify-openspec-change",
      "target": "skill:build-living-dashboard",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:specify-openspec-change",
      "target": "skill:derive-modernization-requirements",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:specify-openspec-change",
      "target": "skill:implement-openspec-change",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:specify-openspec-change",
      "target": "skill:plan-work",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:specify-openspec-change",
      "target": "skill:review-openspec-change",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:specify-openspec-change",
      "target": "skill:test-driven-development",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:test-driven-development",
      "target": "skill:design-test-strategy",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:test-driven-development",
      "target": "skill:implement-openspec-change",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:test-driven-development",
      "target": "skill:implement-ready-slice",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:test-driven-development",
      "target": "skill:mutation-testing",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:test-driven-development",
      "target": "skill:specify-openspec-change",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:test-driven-development",
      "target": "skill:verify-openspec-implementation",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:update-commons-presentation",
      "target": "skill:promote-to-commons",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:update-commons-presentation",
      "target": "skill:validate-visual-artifact",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:validate-visual-artifact",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "skill:validate-visual-artifact",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "skill:validate-visual-artifact",
      "target": "archetype:presentation",
      "relationship": "available in",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "skill:validate-visual-artifact",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "skill:validate-visual-artifact",
      "target": "tool:validate-html",
      "relationship": "ships tool",
      "evidence": "skills/validate-visual-artifact/scripts/validate_html.py"
    },
    {
      "source": "skill:validate-work-item-assumptions",
      "target": "skill:continue-project",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:validate-work-item-assumptions",
      "target": "skill:implement-ready-slice",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:validate-work-item-assumptions",
      "target": "skill:plan-work",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:validate-work-item-assumptions",
      "target": "skill:review-openspec-change",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:verify-openspec-implementation",
      "target": "skill:audit-delivery-traceability",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:verify-openspec-implementation",
      "target": "skill:build-living-dashboard",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:verify-openspec-implementation",
      "target": "skill:complete-openspec-change",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:verify-openspec-implementation",
      "target": "skill:design-test-strategy",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:verify-openspec-implementation",
      "target": "skill:implement-openspec-change",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:verify-openspec-implementation",
      "target": "skill:mutation-testing",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "skill:verify-openspec-implementation",
      "target": "skill:test-driven-development",
      "relationship": "works with",
      "evidence": "catalog/capabilities.yaml related"
    },
    {
      "source": "template:acceptance-audit-template",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/evidence-traceability/overlay.yaml"
    },
    {
      "source": "template:acceptance-audit-template",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/evidence-traceability/overlay.yaml"
    },
    {
      "source": "template:acceptance-audit-template",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/evidence-traceability/overlay.yaml"
    },
    {
      "source": "template:bilingual-artifact-runtime",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "template:bilingual-artifact-runtime",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "template:bilingual-artifact-runtime",
      "target": "archetype:presentation",
      "relationship": "available in",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "template:bilingual-artifact-runtime",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "template:dashboard-data-example",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "template:dashboard-data-example",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "template:dashboard-data-example",
      "target": "archetype:presentation",
      "relationship": "available in",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "template:dashboard-data-example",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "template:dashboard-shell",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "template:dashboard-shell",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "template:dashboard-shell",
      "target": "archetype:presentation",
      "relationship": "available in",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "template:dashboard-shell",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "template:dashboard-structure",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "template:dashboard-structure",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "template:dashboard-structure",
      "target": "archetype:presentation",
      "relationship": "available in",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "template:dashboard-structure",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "template:diagram-model-example",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "template:diagram-model-example",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "template:diagram-model-example",
      "target": "archetype:presentation",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "template:diagram-model-example",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "template:editorial-html-shell",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/branded-html/overlay.yaml"
    },
    {
      "source": "template:editorial-html-shell",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/branded-html/overlay.yaml"
    },
    {
      "source": "template:editorial-html-shell",
      "target": "archetype:presentation",
      "relationship": "available in",
      "evidence": "archetypes/overlays/branded-html/overlay.yaml"
    },
    {
      "source": "template:editorial-html-shell",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/branded-html/overlay.yaml"
    },
    {
      "source": "template:evidence-record-example",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/evidence-traceability/overlay.yaml"
    },
    {
      "source": "template:evidence-record-example",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/evidence-traceability/overlay.yaml"
    },
    {
      "source": "template:evidence-record-example",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/evidence-traceability/overlay.yaml"
    },
    {
      "source": "template:localization-manifest-example",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "template:localization-manifest-example",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "template:localization-manifest-example",
      "target": "archetype:presentation",
      "relationship": "available in",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "template:localization-manifest-example",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "template:project-memory-template-set",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/durable-state/overlay.yaml"
    },
    {
      "source": "template:project-memory-template-set",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/durable-state/overlay.yaml"
    },
    {
      "source": "template:project-memory-template-set",
      "target": "archetype:presentation",
      "relationship": "available in",
      "evidence": "archetypes/overlays/durable-state/overlay.yaml"
    },
    {
      "source": "template:project-memory-template-set",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/durable-state/overlay.yaml"
    },
    {
      "source": "template:requirement-record-example",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/evidence-traceability/overlay.yaml"
    },
    {
      "source": "template:requirement-record-example",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/evidence-traceability/overlay.yaml"
    },
    {
      "source": "template:requirement-record-example",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/evidence-traceability/overlay.yaml"
    },
    {
      "source": "template:sales-narrative-template",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/sales-storytelling/overlay.yaml"
    },
    {
      "source": "template:sales-narrative-template",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/sales-storytelling/overlay.yaml"
    },
    {
      "source": "template:sales-narrative-template",
      "target": "archetype:presentation",
      "relationship": "available in",
      "evidence": "archetypes/overlays/sales-storytelling/overlay.yaml"
    },
    {
      "source": "template:sales-narrative-template",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/sales-storytelling/overlay.yaml"
    },
    {
      "source": "template:visual-pattern-guidance",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "template:visual-pattern-guidance",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "template:visual-pattern-guidance",
      "target": "archetype:presentation",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "template:visual-pattern-guidance",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "tool:analyze-project-delivery",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/consulting-delivery/overlay.yaml"
    },
    {
      "source": "tool:analyze-project-delivery",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/consulting-delivery/overlay.yaml"
    },
    {
      "source": "tool:analyze-project-delivery",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/consulting-delivery/overlay.yaml"
    },
    {
      "source": "tool:audit-trace-graph",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/evidence-traceability/overlay.yaml"
    },
    {
      "source": "tool:audit-trace-graph",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/evidence-traceability/overlay.yaml"
    },
    {
      "source": "tool:audit-trace-graph",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/evidence-traceability/overlay.yaml"
    },
    {
      "source": "tool:audit-trace-matrix",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/evidence-traceability/overlay.yaml"
    },
    {
      "source": "tool:audit-trace-matrix",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/evidence-traceability/overlay.yaml"
    },
    {
      "source": "tool:audit-trace-matrix",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/evidence-traceability/overlay.yaml"
    },
    {
      "source": "tool:build-dashboard",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "tool:build-dashboard",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "tool:build-dashboard",
      "target": "archetype:presentation",
      "relationship": "available in",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "tool:build-dashboard",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "tool:calculate-project-financial-forecast",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/consulting-delivery/overlay.yaml"
    },
    {
      "source": "tool:calculate-project-financial-forecast",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/consulting-delivery/overlay.yaml"
    },
    {
      "source": "tool:calculate-project-financial-forecast",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/consulting-delivery/overlay.yaml"
    },
    {
      "source": "tool:manage-project-memory",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/durable-state/overlay.yaml"
    },
    {
      "source": "tool:manage-project-memory",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/durable-state/overlay.yaml"
    },
    {
      "source": "tool:manage-project-memory",
      "target": "archetype:presentation",
      "relationship": "available in",
      "evidence": "archetypes/overlays/durable-state/overlay.yaml"
    },
    {
      "source": "tool:manage-project-memory",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/durable-state/overlay.yaml"
    },
    {
      "source": "tool:validate-client-localization",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "tool:validate-client-localization",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "tool:validate-client-localization",
      "target": "archetype:presentation",
      "relationship": "available in",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "tool:validate-client-localization",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "tool:validate-dashboard-structure",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "tool:validate-dashboard-structure",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "tool:validate-dashboard-structure",
      "target": "archetype:presentation",
      "relationship": "available in",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "tool:validate-dashboard-structure",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "tool:validate-dashboard-visual",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "tool:validate-dashboard-visual",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "tool:validate-dashboard-visual",
      "target": "archetype:presentation",
      "relationship": "available in",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "tool:validate-dashboard-visual",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/living-dashboard/overlay.yaml"
    },
    {
      "source": "tool:validate-diagram-model",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "tool:validate-diagram-model",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "tool:validate-diagram-model",
      "target": "archetype:presentation",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "tool:validate-diagram-model",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/architecture-documentation/overlay.yaml"
    },
    {
      "source": "tool:validate-html",
      "target": "archetype:development",
      "relationship": "available in",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "tool:validate-html",
      "target": "archetype:legacy-migration",
      "relationship": "available in",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "tool:validate-html",
      "target": "archetype:presentation",
      "relationship": "available in",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    },
    {
      "source": "tool:validate-html",
      "target": "archetype:research",
      "relationship": "available in",
      "evidence": "archetypes/overlays/bilingual-client-delivery/overlay.yaml"
    }
  ]
};
