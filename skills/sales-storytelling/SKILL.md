---
name: sales-storytelling
description: Transform evidence and source material into a credible audience-specific sales presentation narrative and call to action. Do not use to fabricate proof, force a generic sales-deck formula, or replace visual artifact construction and QA.
---

# Sales storytelling

Shape a persuasive argument from verified evidence. This workflow defines presentation methodology; it
does not create a separate sales-project universe and does not substitute for branded artifact creation.

## Establish the decision

For substantial projects, retrieve a presentation context package containing L0 plus current-state,
complexity, risk, requirement, estimate, roadmap, and target-architecture summaries with canonical pointers.
Do not load the complete source repository or research history into the narrative context.

Determine from the brief and available evidence:

- audience and buying roles;
- desired outcome or next action;
- what is being proposed or sold;
- the customer's situation, constraints, and likely problem;
- known differentiators, objections, and proof.

Ask only for missing decisions that research or supplied source material cannot reasonably establish.
Inspect `.agent-commons.yaml` or equivalent persisted project context before asking for delivery language.
When the client is public sector with `CONFIRMED` or `HIGH_CONFIDENCE` classification and a resolved German
locale, use that locale for the sales narrative unless an explicit presentation instruction overrides it.

## Build the argument

Develop the narrative from the actual audience, decision, and evidence. Consider:

1. the customer's current situation;
2. the cost, risk, or missed opportunity in the current state;
3. the insight revealed by research or project evidence;
4. the proposed approach and why it fits;
5. differentiation that matters to this audience;
6. credible proof such as data, architecture, process, experience, or examples;
7. likely objections and honest responses;
8. the concrete call to action.

These are reasoning prompts, not a mandatory slide order. Do not force every argument into problem,
solution, features, benefits, and call to action.

For a public-sector client, construct the narrative natively in professional Standard German from the
research and evidence handoff. Do not first complete an English sales deck and mechanically translate it.
Keep established technical vocabulary such as API, Backend, Frontend, CI/CD, Cloud, DevOps, Spring Boot,
Java, OpenSpec, and TDD where it remains clearer than an artificial translation.

## Protect credibility

- Trace claims to the evidence base or supplied source material.
- Separate proof from assertion and differentiation from unverified marketing language.
- Preserve uncertainty and material limitations.
- Avoid invented customer pain, quantified benefits, logos, endorsements, or case studies.
- When research is intended to discover pain points, competitors, or objections, do not interrogate the
  user for answers that the approved research workflow should establish.
- For public-sector senior technical audiences, prefer precise, factual, confident, restrained, and
  outcome-oriented German. Avoid hype, unsupported ROI, aggressive pressure, and decorative AI claims.
  The presentation must still sell through business value, technical proof, and delivery credibility.
- Reuse terminology established by client websites, corporate-design material, procurement documents,
  project documents, or approved glossaries.

## Produce the narrative handoff

Create a presentation-ready narrative containing:

- audience and desired action;
- central thesis and message hierarchy;
- section or scene sequence with the job of each section;
- evidence and visuals mapped to each claim;
- differentiators and proof;
- objections and responses;
- call to action and follow-up path;
- claims or gaps that require validation before delivery.

Also assign a visual job to each section from the evidence relationship: statement, proof, comparison,
architecture, timeline, objection, transition, or close. This is a rendering handoff, not permission to reorder
the argument. Use contrast between dense evidence and short takeaways to create rhythm; do not default every
section to one headline and three equal cards.

Hand this narrative to the selected presentation medium. For HTML, compose with the branded HTML workflow,
apply a bounded visual-finesse pass when needed, and finish with independent visual validation. Brand and visual
references guide expression; they do not become factual evidence.
Public-sector sales/client presentations are monolingual German by default. Do not create an English
version, duplicate English slides, hidden English message data, or a language switch unless explicitly
requested.

## Validation

- The requested next action is explicit and proportionate.
- The narrative is specific to the audience and decision.
- Every material claim is supported or clearly labeled as a proposal.
- Objections are answered without hiding tradeoffs.
- The deck can be reordered only with a stated reasoning consequence, not because a generic template says so.
