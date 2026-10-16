# Promotion contract

Use this contract to turn an explicit selection into an auditable canonical disposition.

## Source classes

Accept candidates from:

- project reviews such as `docs/commons-review.md` and `docs/commons-review.json`;
- completeness or reconciliation audits;
- external capability reviews with explicit approval;
- an explicit user-specified source path.

Treat every non-canonical source as read-only. If multiple plausible latest reviews exist, present them
instead of guessing. Prefer the structured report for identifiers and the Markdown report for evidence.

## Selection rules

A selection can be expressed by stable ID, name, description, priority, source path, or natural language.
Honor exclusions such as “but not”, “except”, and “only”. “All approved P0 candidates” is explicit only
for candidates whose source report actually classifies them as approved P0 items.

If no candidate is supplied:

1. search the current project for its conventional commons review or established equivalent;
2. list candidate ID, name, proposed action/type, priority, and one-line rationale;
3. ask which candidate or candidates to promote;
4. do not mutate commons.

Never interpret the existence of a review as approval. Never widen one selected candidate to a whole
section, file, or source package.

## Revalidation record

Record these fields for every selected candidate before implementation:

| Field | Required decision |
|---|---|
| Selection evidence | Exact user phrase or stable candidate IDs |
| Primary evidence | Sanitized source paths and proof of actual use |
| Reuse | Value across unrelated future projects |
| Existing overlap | Capabilities inspected and semantic comparison |
| Generalization | Project assumptions removed or parameterized |
| Abstraction | Skill, agent, tool, template, archetype, overlay, eval, guidance, or adapter |
| Maturity | Proven behavior and validation surface |
| Confidentiality | Safe, generalized, or blocked |
| External provenance | Source, revision, trust, license, relationship when relevant |
| Collision risk | Positive, negative, and collision routing distinction |
| Action | Create, update, merge, split, deprecate, or no promotion |
| Disposition | One allowed disposition |

Allowed dispositions are:

- `PROMOTE_NEW`
- `PROMOTE_UPDATE`
- `PROMOTE_MERGE`
- `PROMOTE_DEPRECATION`
- `BLOCK_CONFIDENTIAL`
- `BLOCK_LICENSE`
- `BLOCK_DUPLICATE`
- `BLOCK_INSUFFICIENT_EVIDENCE`
- `BLOCK_WRONG_ABSTRACTION`
- `NEEDS_USER_DECISION`

## Artifact rules

### Skills

Follow the repository's actual skill schema. Define a bounded purpose, trigger and non-trigger in the
description, inputs, ordered workflow, outputs, validation, and failure boundaries. Keep canonical bodies
runtime-neutral.

### Agents

Require a written answer to: “Why should this be a separately delegated specialist rather than a skill?”
Accept only independent review, context isolation, specialist expertise, a real permission boundary,
parallel investigation, or adversarial challenge that materially improves the result. Otherwise use or
update a skill.

### Tools

Prefer a deterministic tool for scanning, graphing, validation, conversion, extraction, or repeatable
generation. Define ordinary inputs, stable outputs, exit codes, usage, synthetic fixtures, and executable
tests. Do not hide deterministic work in repeated prose.

### Templates, archetypes, and overlays

Keep templates free of client branding and content. Compose archetypes from stable capability IDs instead
of duplicating behavior. Require overlays to apply meaningfully across multiple archetypes.

### Existing capability changes

Update the canonical capability instead of creating `-v2`, `better-`, or project-named variants unless a
separate trigger and responsibility can be defended with collision scenarios. Preserve useful behavior and
add regression evals for the improvement.

## Confidentiality gate

Search candidate evidence and the proposed diff for:

- client, company, user, application, repository, host, or internal package names;
- private URLs, paths, credentials, tokens, environment data, and access details;
- proprietary code, schemas, business rules, screenshots, assets, and documentation excerpts;
- personal or regulated data.

Parameterize safe structure. If abstraction removes the candidate's value, use `BLOCK_CONFIDENTIAL` or
keep it project-local. Do not copy sensitive content into provenance or reports.

## External gate

Record:

```text
source
repository or URL
path
immutable revision
trust tier
license and scope
relationship
```

The relationship must be one of `COPIED`, `ADAPTED`, `INSPIRED-BY`, or
`INDEPENDENT-REIMPLEMENTATION`. Prefer the latter two where the idea can be implemented without copying.
Unknown or incompatible license blocks copying and adaptation. Source authority never bypasses license,
security, abstraction, or evaluation.

## Evaluation minimum

For a new skill add:

1. a clear positive invocation;
2. a similar negative invocation;
3. a collision with the closest capability;
4. output and invariant expectations;
5. a relevant failure case.

For an updated capability add regression coverage for the improvement. For a new agent test delegation
value, role independence, output, permission boundary, and no unnecessary mutation. For tools add
executable success, invalid-input, and boundary tests.

## Routing audit

Compare the new or changed description with every related capability. Do not solve ambiguity by adding
synonyms. Clarify positive and negative responsibilities, merge overlapping capabilities, or block the
change when separation cannot be defended.

## Synchronization order

Use this order so generated views follow canonical state:

1. canonical capability and deterministic tests;
2. behavioral evals;
3. provenance;
4. capability and relationship catalogs;
5. archetype or overlay composition when genuinely applicable;
6. runtime adapter interface or renderer changes;
7. deterministic presentation factual refresh with `python3 tools/refresh_commons_presentation.py`, then
   `python3 tools/refresh_commons_presentation.py --check`;
8. README or contributor governance when user behavior changed;
9. version and changelog;
10. complete validation and focused commit.

The factual refresh is part of a successful promotion and requires no second approval. It may update only
generated counts, navigator/search data, previews, network nodes, and evidence-backed relationships. Do not
automatically rewrite authored sales narrative. When the promotion changes architecture, composition,
governance, runtime, or agent-model storytelling, record the signal and recommend the
`update-commons-presentation` workflow.

## Git boundary

Inspect status before mutation. Preserve unrelated tracked, staged, and untracked work. If a required file
already contains unknown edits, isolate the promotion hunks deterministically or stop. Never make a
promotion commit that silently absorbs unrelated work. Record the pre-change and post-change status in the
promotion report.
