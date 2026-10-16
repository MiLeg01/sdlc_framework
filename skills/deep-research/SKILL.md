---
name: deep-research
description: Conduct structured evidence-backed topic research for decisions, reports, dashboards, or presentations. Do not use for external agent-capability discovery, unsupported factual invention, or a simple lookup that does not justify a research workflow.
---

# Deep research

Build a decision-useful evidence base rather than a list of links.

## Frame the work

Establish, from supplied context before asking:

1. the research question and what must be learned;
2. the audience and the decision or artifact the findings must support;
3. scope boundaries such as geography, industry, technology, competitors, and time;
4. the requested depth: quick discovery, structured research, or deep research;
5. authoritative inputs, supplied references, and output expectations.

For substantial research, read L0 and retrieve only relevant prior conclusions, terminology, decisions,
unknowns, and source references from project memory. Reuse current findings, but revisit drift-prone external
facts and never cite memory in place of the original source.

Ask only for material missing choices. Record assumptions and exclusions explicitly.

## Plan evidence collection

Create a compact research plan that maps each important question to likely evidence classes. Use any
runtime-supported combination of official documentation, primary sources, reputable secondary sources,
local files, uploaded documents, project repositories, and approved external services. Runtime adapters
decide how search, browsing, connectors, and file access are executed.

Prefer direct and authoritative sources when they can establish the claim. Use secondary sources for
context, comparison, market interpretation, or discovery. Treat source authority, freshness, independence,
methodology, and conflicts of interest as separate quality dimensions.

When supplied attachments are a material evidence class, inventory the bounded files before extraction and
follow `references/attachment-intake.md`. Use the runtime's document, PDF, image, presentation, or spreadsheet
reader appropriate to the format, including visual inspection when layout carries meaning. An attachment can
establish what a human source says; it does not by itself prove a claim about current implementation.

## Research multiple perspectives

For consequential findings, actively look for:

- supporting evidence and quantified evidence where available;
- counterarguments and contradictory findings;
- competing approaches and meaningful alternatives;
- risks, limitations, and uncertainty;
- evidence that would change the provisional conclusion.

Do not force false balance when evidence quality is asymmetric. Preserve real conflicts instead of
silently averaging them.

## Maintain provenance

Give important claims stable source references with enough detail to relocate the evidence. Distinguish:

- observed or sourced fact;
- interpretation or synthesis;
- proposal or recommendation;
- assumption;
- conflict;
- unknown.

Never cite a search result snippet as if it were the underlying source. Do not use visual inspiration as
factual authority.

## Synthesize findings

Organize findings around the research question, not the order in which sources were found. Explain what
the evidence means, where it agrees, where it conflicts, what remains uncertain, and what decision it
supports. A useful synthesis contains implications and prioritized conclusions, not merely summaries.

When the downstream artifact is a presentation, additionally produce a presentation-ready synthesis with:

- strongest findings and quantified proof;
- customer or client pain points when relevant;
- implications and recommended message hierarchy;
- a defensible narrative direction;
- important data, diagrams, or visual opportunities;
- objections, counterarguments, and evidence-backed responses;
- clear boundaries against unsupported factual invention.

## Outputs

Use the project convention when one exists. Otherwise keep a lightweight `research/` evidence base with a
plan, findings, sources, and synthesis. Do not create empty ceremony for a quick lookup.

For research followed by presentation work, the synthesis is the factual handoff. Presentation creation
may reorganize and explain those findings, but must not invent new claims that the evidence base does not
support.

After validation, merge compact conclusions, conflicts, decisions, unknowns, and source pointers into the
relevant memory domain and create a research checkpoint. Do not store downloaded source bodies or browsing
history in memory.

## Validation

- Reconcile the final findings with the research question and declared scope.
- Confirm every consequential factual claim has relocatable evidence.
- Check source freshness when the topic can drift.
- Surface contradictions, weak evidence, and unresolved gaps.
- State validation limits and what was not researched.
