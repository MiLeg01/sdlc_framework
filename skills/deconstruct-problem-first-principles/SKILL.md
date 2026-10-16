---
name: deconstruct-problem-first-principles
description: Deconstruct a stated problem before planning or implementing by separating known facts from inherited assumptions, restating it plainly, naming the violated invariant or unstated constraint behind it, checking where else that constraint applies, and choosing whether to intervene at the symptom, the root cause, or the structure. Use when the right approach is unclear, a defect's cause is not obvious, or a design carries trade-offs worth challenging. Do not use for a trivial or fully specified change, for topic research, for reviewing a design that already exists, or to produce the plan itself.
---

# Deconstruct a problem from first principles

A delivery chain that runs evidence, requirements, specification, and plan presumes one thing it never
checks: that the problem was framed correctly. This workflow checks it. Establish what the problem actually
is, and at what level it should be answered, before anything downstream commits to an approach.

Ground the analysis in current reality first. Read the relevant code, configuration, data, and history to
verify what the problem statement claims, rather than reasoning from the statement alone. A deconstruction
built on the statement's own framing inherits exactly the error it exists to catch.

## Work the five steps in order

The order is the method. Do not form a conclusion before step 3 is complete — a conclusion reached at step 1
is the initial framing wearing a different label.

### 1. Strip assumptions

Separate what is provably true from what is assumed. List only what is known, and mark everything else as
inherited framing.

For a defect, do not treat the failing test, the error, or the trace as complete truth. Each shows where a
problem surfaced, which is often not where it originates. For a design question, do not adopt the
requester's framing as a constraint; a stated solution frequently arrives disguised as a requirement.

### 2. Restate plainly

Express the problem in plain language, without jargon, domain shorthand, or the vocabulary of the existing
implementation. If it cannot be restated plainly, the problem is not yet understood — that failure is a
finding to report, not an obstacle to write around.

### 3. Name the broken assumption or unstated constraint

Defects are violated invariants: something the author believed would always hold, and which does not hold
here. Design problems are unstated constraints: something the request requires but never says. Name it
explicitly. This is the root cause or the real requirement, and everything after depends on getting it right.

### 4. Invert

If that assumption is wrong here, ask where else it is wrong. The same belief usually appears in more than
one place, so check the rest of the design before fixing only the reported case. Report every other site
found, including ones outside the current scope — an unreported second site becomes the next defect.

### 5. Choose the intervention level

Decide explicitly whether to act at the **symptom**, the **root cause**, or the **structure that permitted
the problem**, and record the choice with its reason.

All three are legitimate. A local fix is sometimes correct, and a structural change is sometimes
disproportionate. What is never correct is making the choice implicitly: an unrecorded decision to patch a
symptom is indistinguishable from failing to notice there was a deeper option, and neither the author nor a
later reader can tell which happened.

## Report

Return a concise analysis — this is input to a decision, not a document:

- **Known versus assumed** — what is established, and what was inherited from the framing.
- **Real constraint** — the violated invariant or unstated requirement, stated once and precisely.
- **Inversion findings** — every other site where the same constraint applies, in or out of scope.
- **Recommended level** — symptom, root cause, or structure, with the reason for that level.

Separate observed evidence from interpretation. Where the analysis could not be grounded, say so rather
than filling the gap with a plausible reconstruction.

## Boundaries

Analysis only. Do not implement, and do not write the plan — hand the findings to the planning workflow,
which owns sequencing, ownership, and validation. Keep this read-only where the environment allows it, so
the deconstruction cannot quietly become the fix.

The method is domain-general and applies to any problem that can be stated and checked against evidence.
The framing here is engineering because that is where it is invoked most, not because it is limited to it.

Stop and report rather than proceeding when the problem statement cannot be verified against any available
evidence, when the real constraint turns out to be an unresolved product or business decision rather than a
technical one, or when the analysis shows the requested problem is not the one worth solving. Each of those
is a result, not a failure — returning it early is the point of running this before planning.
