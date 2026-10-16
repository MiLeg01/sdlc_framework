---
name: review-for-commons
description: Inspect an active project and semantically compare its proven agent workflows, skills, roles, scripts, templates, evaluations, runtime adapters, and recurring practices with the canonical Agent Commons Library, then write a sanitized project-local proposal for new, updated, replaced, duplicate, local, or rejected capabilities. Use at a meaningful project milestone, before archival, or when deciding what this project should contribute back to commons. Do not use to promote or install capabilities, mutate the commons library, delete project-local assets, or turn speculative and one-off behavior into global guidance.
---

# Review a project for commons

Produce an evidence-backed changeset proposal. Never promote automatically.

This workflow is the internal learning path. It reviews proven behavior from the current project. Do not
quietly broaden it into open-source research: use `search-external-capabilities` and
`review-external-capability` for external ecosystem learning. Internal and external proposals remain
distinct evidence streams but pass through the same abstraction, confidentiality, licensing where
applicable, evaluation, provenance, and explicit promotion gate.

## Establish scope and boundaries

1. Resolve the current project root from Git; if the directory is not in a worktree, use the invocation
   directory. Do not treat the commons checkout itself as the source project.
2. Locate the canonical Agent Commons Library from project configuration or the standard
   `~/agent-commons-library` checkout. Read its governance before comparing anything.
3. Read project instructions and repository state before inspecting candidates. Preserve unrelated work.
4. Default report paths to `docs/commons-review.md` and `docs/commons-review.json` inside the current
   project. Follow an established equivalent project convention when one exists.
5. Treat the project as read-only except for the two review reports. Treat commons as fully read-only.
6. Exclude secrets, credentials, environment files, dependencies, generated output, caches, binaries,
   vendor content, Git object storage, and private source excerpts.

If the project root, commons root, or safe report destination cannot be resolved, stop and report the
specific uncertainty. Do not guess across unrelated repositories.

## Discover project learning

Inspect only relevant project-owned evidence. Prioritize:

- runtime instruction and configuration files, local skills, rules, roles, commands, and adapters;
- deterministic scripts, automation, templates, prompts, and repeated manual instructions;
- architecture, requirements, testing, validation, dashboard, presentation, bootstrap, migration, and
  deployment workflows;
- project memory, decisions, reports, and Git history when they establish actual use or evolution.

Use `rg --files` or another deterministic inventory before semantic inspection. Prune broad dependency and
generated trees. Filenames and comments are leads, not evidence.

For each explicit capability ask why it exists locally. Also search ordinary scripts, prompts, commits,
and successful repeated behavior for useful methods that were never packaged as a skill.

## Build evidence-backed candidates

Record project-relative source paths and concrete use evidence without copying confidential content.
Redact sensitive path segments, for example `.agents/skills/<client-workflow>/SKILL.md`. Classify each finding:

- `POTENTIALLY_REUSABLE`: useful across unrelated projects after parameterization;
- `PROJECT_LOCAL`: depends on client, application, business, or one-off project context;
- `VARIATION`: changes behavior already represented in commons;
- `LOCAL_DUPLICATE`: commons already covers the behavior adequately;
- `REJECTED`: speculative, trivial, immature, obsolete, or weakly evidenced.

Separate observed evidence from interpretation, recommendation, assumption, conflict, and unknown. A file
that exists once is not automatically a reusable capability.

## Compare semantically with commons

Inspect relevant commons skills, agents, tools, templates, archetypes, evaluations, catalogs, provenance,
and replacement or deprecation metadata. Compare responsibility, trigger, non-trigger, workflow, outputs,
validation, safety, and abstraction rather than names alone.

Assign one comparison result:

- `EXACT`: commons already provides the same behavior;
- `OVERLAP`: commons handles most of it;
- `EXTENSION`: the project adds meaningful behavior;
- `REPLACEMENT`: the project approach is materially stronger;
- `NEW`: no meaningful equivalent exists;
- `PROJECT_LOCAL`: safe generalization would destroy the value.

If two capabilities cannot state meaningfully different positive, negative, and collision scenarios,
recommend merging or renaming instead of keeping both.

## Apply the promotion tests

Before recommending a new capability, require all of the following:

1. plausible value in at least two unrelated future projects;
2. value survives removal of project and client details;
3. a clear bounded problem, trigger, and non-trigger;
4. no adequate commons equivalent;
5. the correct abstraction type: skill, agent, tool, template, archetype, global instruction, or eval;
6. mature, successful behavior rather than speculation;
7. net simplification or clear value despite added commons surface area.

Before recommending an update or replacement, require a concrete functional, routing, output, validation,
edge-case, performance, determinism, safety, decomposition, consolidation, abstraction-boundary, or reusable
visual-design improvement. Reject style-only differences.

For living dashboards, compare any proposed structural improvement with the canonical
`dashboard-structure` template catalog entry. Project branding, language, wording, metrics, and
one-off sections are not structural improvements. A candidate must show a reusable improvement to section
hierarchy, navigation, overview layering, interaction patterns, extension points, responsive behavior, or
structural validation. Record it as a proposal for explicit promotion; never treat one project dashboard as
permission to silently redefine the global structure.

## Scrub confidential detail

Remove or parameterize client and company names, application names, usernames, repository and internal
URLs, credentials, hostnames, private package names, source code, schemas, business rules, screenshots,
private assets, and documentation excerpts. Paths can leak the same details: use project-relative paths,
replace sensitive segments with descriptive placeholders, and represent roots as `.` and
`<commons-root>`. If safe abstraction is not possible, classify the candidate as `PROJECT_LOCAL`.

## Write the review

Read `references/report-contract.md` and create both reports unless the user explicitly requests only one.
Keep the Markdown evidence-rich and the JSON concise. Ensure counts reconcile with the detailed entries.
Assign every candidate a stable ID using the report contract. Preserve existing IDs when refreshing a
review; do not renumber candidates merely because priority or ordering changed.

End with:

- P0: high-confidence promotion or update proposals, including exact likely commons files and
  required evals;
- P1: candidates needing more evidence or validation;
- Do not promote: local, duplicate, unsafe, immature, or rejected findings.

For every proposed commons change, name source evidence paths, compatibility risk, and validation needed.
Do not edit those commons files.

## Final checks

Before reporting completion:

1. confirm the commons worktree is unchanged by this review;
2. confirm only intended project report files changed;
3. reconcile Markdown and JSON counts;
4. scan the reports for sensitive material;
5. state inspection and validation limits.

Print a concise summary with actual counts, high-confidence proposals, and report paths. Zero proposals is
a valid high-quality result.
