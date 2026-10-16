---
name: manage-project-delivery
description: Establish and operate evidence-backed delivery governance across workstreams, dependencies, milestones, decisions, risks, actions, and status reporting. Use for multi-workstream projects or programs that need repeatable coordination and truthful health reporting. Do not use to define product requirements, implement delivery tasks, replace an established tracker, or present schedule and health claims without current evidence.
---

# Manage project delivery

Coordinate the delivery system without becoming every delivery role. Keep the source of truth in the
project's approved tracker or canonical project state, and make status a reproducible interpretation of that
evidence rather than a narrative assembled from memory.

## Establish the delivery contract

1. Resolve the objective, measurable outcomes, scope and non-goals, sponsor or decision owner, delivery
   owner, workstream owners, reporting audience, cadence, calendar, and authoritative systems.
2. Reuse an established tracker and identifiers. Do not create a competing board, duplicate backlog, or
   private status store merely because a preferred tool is unavailable.
3. Separate facts, accepted decisions, assumptions, proposals, conflicts, and unknowns. Date every status
   snapshot and mark inaccessible sources stale.
4. Define the minimum status vocabulary and exit criteria. A status transition requires evidence; activity,
   confidence, or a checked box alone is not proof of completion.

## Build the delivery model

1. Decompose the objective into outcome-oriented workstreams and milestones. Keep tasks small enough to
   own and verify, while avoiding a second implementation backlog when one already exists.
2. Record dependencies as a directed graph. Reject missing references and cycles before publishing a plan.
3. Assign one accountable owner per active workstream. Record contributors separately when needed; shared
   ownership is not a substitute for accountability.
4. Maintain a RAID register:
   - risks include likelihood, impact, mitigation, trigger, and owner;
   - assumptions include validation date and consequence if false;
   - issues include current impact, containment, and resolution owner;
   - decisions include options, decision owner, due date, outcome, and rationale.
5. Define milestone acceptance through observable evidence. Route implementation planning to `plan-work`,
   delivery execution to the appropriate implementation skill, and multi-agent execution to
   `coordinate-parallel-agents`.

When the project can export the example structure in `assets/delivery-register.example.json`, run
`scripts/analyze_project_delivery.py <register.json>` to validate dependencies and derive status counts,
blocked and overdue workstreams, unowned work, high risks, ready work, and the planned critical path.
Treat the tool result as a deterministic control summary, not as a substitute for delivery judgment.

## Operate the cadence

For every reporting cycle:

1. Re-read the authoritative work items, milestones, decisions, risks, financial baseline, and validation
   evidence changed since the previous snapshot.
2. Reconcile workstream status against completion evidence. Distinguish completed, in progress, blocked,
   planned, cancelled, and stale or unknown states.
3. Recompute dependencies, critical path, overdue work, unresolved decisions, high risks, and milestone
   confidence. Name the evidence and calculation date.
4. Integrate financial status from `forecast-project-financials` when budget, revenue, margin, burn, earned
   value, or estimate-at-completion matters. Do not hide schedule risk inside financial commentary or vice
   versa.
5. Produce an action-first update:
   - objective and overall health;
   - material change since the previous snapshot;
   - milestone and workstream status;
   - blockers, dependencies, risks, assumptions, issues, and decisions;
   - financial headline when applicable;
   - one to three owner-bound next actions with due dates;
   - evidence freshness and limitations.
6. Persist the update in the project's established coordination surface only when authorized. A chat summary
   is not canonical project state.

## Health and escalation

- `ON_TRACK`: current evidence supports the committed outcome and no unresolved item threatens it.
- `AT_RISK`: an overdue dependency, unowned active item, high open risk, material forecast variance, or stale
  evidence threatens the outcome but recovery remains credible.
- `BLOCKED`: work cannot proceed without a named decision, dependency, access, resource, or remediation.
- `COMPLETE`: every in-scope outcome meets its acceptance evidence and open exceptions are explicitly owned.

Never average red and green signals into a reassuring status. Escalate the smallest decision that unlocks
progress, name its owner and due date, and state the consequence of delay. Do not assign people, change scope,
move deadlines, waive evidence, or commit commercial outcomes without authorization.

## Optional consulting-delivery profile

For a consulting engagement, map the generic roles to locally approved titles such as engagement sponsor,
delivery lead, workstream lead, client decision owner, finance controller, and quality reviewer. Keep
organization-specific terminology, branding, rate cards, commercial thresholds, approval routes, and client
identifiers in project-local configuration. Never embed them in this canonical skill.

## Output and completion

Return the dated delivery snapshot, dependency and milestone view, RAID and decision summary, health rationale,
evidence freshness, financial linkage when relevant, and exact next actions. Complete only when counts
reconcile to the authoritative register, every active workstream has an owner, dependency cycles are absent,
status claims cite evidence, and limitations remain visible.
