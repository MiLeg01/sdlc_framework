---
name: promote-to-commons
description: Revalidate and implement explicitly selected reusable capability proposals in the canonical Agent Commons Library, including safe abstraction choice, confidentiality and license checks, evals, provenance, catalogs, adapters, documentation, validation, reporting, and a focused commit. Use when the user asks to promote named or clearly selected candidates from a commons review, completeness audit, external review, or explicit source path, or invokes the workflow without a candidate to inspect and choose from the latest project review. Do not use to discover candidates, promote an entire review implicitly, mutate source projects, copy unknown-license material, or bypass independent revalidation.
---

# Promote approved capabilities to commons

Act as the controlled mutation gate between a proposal and canonical Agent Commons. A review may recommend;
only an explicit user selection authorizes revalidation and possible mutation.

Read `references/promotion-contract.md` before changing canonical files. Read
`references/report-contract.md` before writing the promotion report.

## Resolve the source and selection

1. Resolve the source project and canonical commons root. Read both repositories' instructions and Git
   state. Treat source projects as read-only; only the canonical commons checkout may be mutated.
2. Locate the named proposal, audit, external review, or explicit source. When no candidate was supplied,
   inspect the latest conventional project review and present its promotable candidates concisely.
3. Resolve positive selections and exclusions from stable IDs, names, descriptions, priorities, or natural
   language. Do not require numeric syntax.
4. Do not mutate anything until the selected set is unambiguous. If no selection exists, present choices
   and stop. If the user already selected clearly, do not ask again.
5. Record the exact selected and excluded candidates. Approval applies only to that set; never infer that a
   review authorizes every proposal.

## Revalidate independently

For every selected candidate, inspect primary evidence rather than trusting the proposal's conclusion.
Evaluate reuse, actual commons overlap, generalization, abstraction type, maturity, confidentiality,
licensing, routing collision risk, and validation feasibility. Search the relevant canonical skills,
agents, tools, templates, archetypes, overlays, adapters, evals, catalogs, and provenance.

Assign exactly one internal disposition:

- `PROMOTE_NEW`, `PROMOTE_UPDATE`, `PROMOTE_MERGE`, or `PROMOTE_DEPRECATION`;
- `BLOCK_CONFIDENTIAL`, `BLOCK_LICENSE`, `BLOCK_DUPLICATE`,
  `BLOCK_INSUFFICIENT_EVIDENCE`, or `BLOCK_WRONG_ABSTRACTION`;
- `NEEDS_USER_DECISION`.

Stop only the failing candidate unless its failure invalidates shared work. Explain blocked and no-change
results; never force a mutation merely because promotion was requested.

## Protect boundaries before mutation

1. Inspect `git status`, staged changes, untracked files, and recent history in commons.
2. Preserve unrelated work. If selected changes overlap unknown edits and cannot be isolated safely, stop
   before mutation and request a clean boundary or explicit ownership decision.
3. Scan source material for client names, application names, internal URLs, credentials, private paths,
   screenshots, proprietary code, schemas, business rules, and personal data. Generalize or block it.
4. For external material, verify source, repository, path, immutable revision, trust, license scope, and
   relationship. Unknown license prohibits copying or adaptation.
5. Do not execute unreviewed third-party code. Keep external cache and source projects outside the trusted
   activation boundary.

## Implement the smallest correct canonical change

Choose `CREATE`, `UPDATE`, `MERGE`, `SPLIT`, `DEPRECATE`, or `DO_NOT_PROMOTE` semantically. Prefer updating
an existing capability over creating a versioned or project-named duplicate.

- Put reusable judgment in a runtime-neutral skill.
- Create an agent only when independent delegation adds material value through isolation, adversarial
  review, specialist expertise, permission boundaries, or parallel investigation.
- Put deterministic repeatable work in a tool with input/output contracts, exit behavior, tests, and
  synthetic fixtures.
- Keep templates structural, archetypes compositional, and overlays cross-cutting across multiple
  archetypes.
- Put universal policy in global guidance and native discovery or representation differences in adapters.
- Generalize instead of copying project-local source verbatim.

For every behavior change, add positive, negative, collision, output/invariant, regression, and relevant
failure evaluations. For new agents, test delegation value and permission boundaries. For deterministic
tools, add executable tests. A promotion without appropriate evals is incomplete.

## Synchronize canonical relationships

Update actual relationships only where supported:

- stable capability catalog and human-readable catalogs;
- related skills, agents, tools, evals, archetypes, and overlays;
- provenance and external relationship metadata;
- runtime adapter interface metadata or renderers when native representation changes;
- generated presentation/navigation data and user documentation when discoverability or lifecycle changes;
- version and changelog according to repository policy.

Do not add a governance capability to project archetypes merely to increase visibility. Add it only when
the archetype genuinely composes it. Canonical behavior comes first; adapters remain thin.

## Validate and commit

1. Run targeted checks while implementing and every repository-required validation before completion.
2. Validate schemas, catalogs, skills, agents, tools, archetype composition, adapters, provenance, external
   licensing when relevant, and evals. Test the promoted behavior directly.
3. After successful canonical mutation, evals, catalog synchronization, and adapter validation, run
   `python3 tools/refresh_commons_presentation.py`. This deterministic factual refresh requires no separate
   user confirmation. It updates counts, navigator data, search terms, previews, network nodes, and
   evidence-backed relationships only.
4. Run `python3 tools/refresh_commons_presentation.py --check`. If generated factual data remains stale,
   fail the promotion rather than hand-editing the presentation.
5. Do not rewrite the hero, sales narrative, architecture story, value proposition, or use-case storyline
   automatically. If the promotion introduces a new archetype, composition or promotion model, runtime
   architecture, agent model, governance boundary, or similarly meaningful story change, report the
   narrative-impact evidence and recommend the `update-commons-presentation` workflow.
6. Treat any failure as a blocker until fixed or explicitly reported. Never claim success over a failing
   gate. Failed validation prevents success and the final promotion commit.
7. Review the final diff for confidential leakage, routing ambiguity, generated-file drift, unrelated
   changes, and missing reverse traceability.
8. Write the promotion report using `references/report-contract.md`.
9. Stage only the promotion. Commit with a message describing the actual create, update, merge, or
   deprecation. Do not absorb unrelated work.
10. Report selected, promoted, blocked, eval, adapter, presentation-refresh, narrative-impact, validation,
   version, and commit results with actual
   values.

## Handle failure honestly

If evidence supports no promotion, leave canonical behavior unchanged and record why. If approval,
license, confidentiality, abstraction, dirty-state ownership, validation, or commit isolation remains
unresolved, stop at that boundary and return the exact next decision needed.
