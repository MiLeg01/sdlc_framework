---
schema_version: 1
id: ext-github-community-discovery-footprintai-open-sdlc-skills
source_id: github-community-discovery
repository: FootprintAI/open-sdlc-skills
path: pm/sprint-delivery.md
revision: 75b71b8bb038fdf45df07c9c3258bc08641f04fa
trust: COMMUNITY
license: Apache-2.0
license_scope: Repository LICENSE applies to the reviewed Markdown role and workflow files; terms appear to permit modification and redistribution subject to license and notice obligations.
security_class: INSTRUCTIONS ONLY
relationship: INSPIRED-BY
status: PROMOTION-CANDIDATE
reviewed_at: 2026-09-02
---

# Review: open-sdlc project delivery roles

## Review boundary and evidence

Reviewed the revision-pinned repository metadata, README and LICENSE, project-manager sprint workflow,
coordinator status workflow, and the team sprint-cycle orchestration instructions. The source was inspected
as text only. No command, GitHub mutation, deployment, installer, or external code was executed.

## Provenance

Observed fact: the source is a community repository discovered through the configured GitHub community
source. The repository describes a set of Claude Code skills used for a software-delivery lifecycle. The
reviewed revision is immutable and was the default-branch head during discovery.

## License assessment

Observed fact: the repository contains an Apache-2.0 LICENSE. It appears to permit modification and
redistribution subject to its conditions and notice requirements. This review does not provide legal advice.
The promotion uses `INSPIRED-BY`; no source prose, commands, or role definitions are copied.

## Security and supply-chain characteristics

The reviewed files are instructions, but they direct agents to create and edit GitHub issues and labels,
spawn implementation agents, create worktrees, deploy environments, verify releases, push tags, and publish
releases. Those are consequential external and repository mutations even though the source itself is
instruction-only. No such operation was performed during review.

## Semantic comparison with current commons

- `plan-work`: `OVERLAP` on executable planning, dependencies, ownership, validation, risks, and recovery.
- `coordinate-parallel-agents`: `OVERLAP` on isolated ownership and coordinator-controlled integration.
- `implement-ready-slice`: `OVERLAP` on dependency-ready execution and evidence-based completion.
- `audit-delivery-traceability`: `OVERLAP` on proof across delivery stages.
- project-wide operating cadence, RAID, milestone health, and stakeholder status: `EXTENSION`.
- permanent PM or Scrum subagents: `BLOCK_WRONG_ABSTRACTION`; the work is a reusable workflow unless an
  independent review or permission boundary is required.

## Useful novel patterns

- one durable coordination surface backed by actual artifacts rather than chat memory;
- flow-first prioritization and explicit dependency order;
- status derived from issue, change, deployment, and verification evidence;
- a verification queue tied to one known deployed version;
- action-first reporting with a named owner, deadline, and consequence;
- explicit stage gates and backward movement when evidence invalidates an earlier decision.

## Rejected or non-canonical patterns

- Claude-specific command syntax, model-tier names, and worktree invocation details;
- GitHub as a mandatory tracker or source of truth;
- automatic deployment, tagging, release publication, or continuous loops;
- a fixed weekly sprint cadence for every project;
- a permanent project-manager, coordinator, or Scrum agent without independent specialist value;
- full package import or duplicate runtime-specific role bodies.

## Promotion candidates

1. A runtime-neutral `manage-project-delivery` skill for workstreams, dependencies, milestones, RAID,
   evidence-backed health, cadence, decisions, escalation, and action-oriented status.
2. A deterministic delivery-register analyzer that rejects invalid dependency graphs and derives critical
   path, blocked, overdue, unowned, ready, and high-risk signals.
3. An optional consulting-delivery overlay composing delivery management with project financial forecasting
   across development, modernization, and research projects.

The proposed relationship is `INSPIRED-BY`. Existing implementation, testing, and parallel-coordination
skills remain the owners of execution behavior.

## Required evaluations before promotion

- Positive multi-workstream delivery request, negative task implementation request, collision with
  `plan-work` and `coordinate-parallel-agents`, output invariants, stale-evidence handling, and dependency
  failure behavior.
- Executable success, missing dependency, cyclic dependency, overdue, blocked, and unowned-work tests.
- Overlay composition and runtime-adapter validation.

## Final recommendation

`PROMOTION-CANDIDATE`. Promote the generalized delivery-governance workflow and deterministic status
analysis. Do not promote the runtime-specific role pack, automatic release loop, or GitHub-specific command
surface.

No external code was executed and no external capability was installed during this review.
