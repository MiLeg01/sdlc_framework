---
name: validate-work-item-assumptions
description: Read-only check of whether a previously filed work item's stated assumptions about current system state still hold, returning confirmed, changed, and unverified claims plus one materiality verdict. Use before planning, estimating, reopening, or reviewing an item that was filed earlier than now. Do not use to decide whether the work proceeds, to propose a revised approach, to edit the item or any other file, or to review a change that is already in progress.
---

# Validate work-item assumptions

A work item records what was true when someone filed it. By the time it is picked up, the system may have
partly solved the problem, renamed what the item names, or moved the context out from under its approach.
Planning on a stale premise is expensive; a bounded spot-check is cheap.

Establish what no longer holds. Do not decide what to do about it — the caller owns that decision.

## Boundaries

Read-only. Do not edit the item, the system, or any other file. Do not implement, file follow-up work,
propose a revised approach, or run a full build, test suite, or other long operation. Targeted reads and
history queries only.

Report on the item as filed. If the caller supplies its own paraphrase of the item, treat that as context
for what matters, never as a replacement for reading the item.

## Establish the claims

1. Read the work item from its authoritative record, not from a generated index, digest, or summary view.
2. Extract its **falsifiable** claims about current state, separating them from narrative and from proposed
   solutions. Falsifiable claims name a thing and assert something checkable about it:
   - files, modules, symbols, interfaces, endpoints, tables, or configuration it says exist;
   - behavior it calls missing, broken, duplicated, or slow;
   - patterns, conventions, or constraints it assumes are in force;
   - dependencies, versions, or external contracts it relies on.
3. Ignore claims that cannot be checked from the system as it stands — an appetite, a preference, a
   business priority, or a value judgment is not a staleness signal. Record them as out of scope.

An item with no falsifiable claims is a valid finding: say so and stop. There is nothing to go stale.

## Check each claim

Spot-check every extracted claim against current state. Read narrowly — a targeted search, a bounded
region of a file, or a history query is enough. Reading whole files is a signal the claim was not
sharp enough to check.

**Prefer disproving a claim over confirming it.** A false "still accurate" is the costly error here: it
sends the caller into a plan built on a premise that no longer holds, and the cost surfaces only after the
work is designed. A false "changed" costs one clarifying question. Search for the evidence that would
refute each claim before accepting the evidence that supports it.

Use history to detect movement, not just presence. A symbol that exists today may have moved, changed
meaning, or been reimplemented since the item was filed; recent changes touching the named paths often
name the work that already addressed part of the item.

Absence of evidence is not disproof. When a claim cannot be checked within the bounded effort — the
surface is external, the behavior needs a running system, the item is too vague to pin down — record it as
unverified. Do not resolve it by assumption in either direction.

## Judge materiality

Classify every changed claim:

- **Material** — it would change the implementation approach, the effort, the sequencing, or whether the
  item is still worth doing.
- **Cosmetic** — the requirement still stands and the approach survives; something was renamed, moved, or
  reworded around it.

Then return **one** materiality verdict for the item as a whole. This single judgment is the most useful
thing the check produces, so make it decisive and justify it in one clause.

**Lean conservative when genuinely torn.** Flag it material and say why the call is uncertain, rather than
waving a stale assumption through. The asymmetry is the reason: a wrongly-approved staleness costs an
entire plan, a wrongly-flagged one costs one question.

## Report

Return three lists and a verdict:

- **Still accurate** — each confirmed claim with the exact evidence that confirms it.
- **Changed** — each refuted claim with what it says, what is true now, when and by what change it moved,
  and whether that is material or cosmetic.
- **Unverified** — each unchecked claim and the specific reason it could not be checked.
- **Verdict** — material or cosmetic for the item overall, in one clause, plus the exact next decision the
  caller now owns.

Be specific enough to act on. Name the file, the symbol, and the change that moved it. "The parser
changed" is unusable; "the named function moved from its original module to another one, in the change
that introduced the replacement path" is actionable. Keep observed evidence separate from interpretation.

## Completion and stop conditions

Complete when every extracted claim is in exactly one of the three lists and the verdict is stated.

Stop and report rather than guessing when the item cannot be located or resolves ambiguously, when the
authoritative record is unreadable, or when the item names a system the current scope cannot reach. An
item that turns out to be already fully resolved is a valid result — report it as such and let the caller
close it.

Do not extend into planning. When the caller needs a revised approach for a materially stale item, that is
a separate act: hand the findings to the planning or problem-analysis workflow rather than drafting the
new approach here.
