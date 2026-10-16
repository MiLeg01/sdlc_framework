---
name: review-external-capability
description: Perform a detailed, revision-pinned review of one selected external skill, agent, command, plugin, MCP integration, hook, script, template, eval, or composite package; classify provenance, license, runtime coupling, security, semantic commons overlap, and targeted promotion candidates. Use after external discovery selects a promising item. Do not use to install or execute the package, review many candidates superficially, bypass licensing, copy unknown-license content, or promote directly into canonical commons.
---

# Review an external capability

Review one bounded capability deeply enough to support a promotion decision.

## Establish the boundary

1. Resolve the source URL, repository or registry, exact path, author or organization, and immutable
   revision. If a revision cannot be pinned, record the limitation and do not make reproducibility claims.
2. Resolve source trust from `external/sources.yaml`. A repository absent from the registry starts as
   `UNTRUSTED`, even when its name looks official.
3. Inspect source content read-only. Never execute scripts, hooks, installers, MCP servers, package setup,
   generated binaries, or commands merely to understand them.
4. If working in the canonical commons checkout for an intentional library review, write under
   `external/reviews/` and update the external index deliberately. Otherwise write a project-local report
   and leave commons unchanged.

## Review provenance and license

Capture source, repository, path, organization, revision, trust, detected license, license path and scope,
apparent redistribution and modification permissions, attribution or notice requirements, and uncertainty.

Use `LICENSE UNKNOWN` when the source does not establish the applicable license. Unknown licensing
prohibits copying or adapting source text and code. Methodology may still be independently reimplemented
when appropriate, with careful provenance and no claim of legal certainty.

## Classify capability and runtime coupling

Choose the most accurate type: skill/workflow, agent, command, plugin, tool, MCP, hook, script, template,
eval, or composite package. Separate reusable methodology from Claude-, Codex-, Cline-, OpenCode-, or
other runtime-specific syntax, paths, tools, permissions, and orchestration.

Classify the security surface as one of:

- `INSTRUCTIONS ONLY`
- `INSTRUCTIONS + SCRIPTS`
- `PLUGIN WITH HOOKS`
- `MCP/REMOTE TOOLING`
- `UNKNOWN`

Inspect for shell and language scripts, automatic execution, hooks, MCP definitions, remote calls,
credentials and environment access, network use, deletion, Git mutation, dependency installation,
privileged operations, instruction injection, and large or opaque binaries. Stronger provenance never
removes the need for this review.

## Compare semantically with commons

Read the actual relevant capabilities, catalogs, tools, archetypes, evals, provenance, and promotion
rules. Compare trigger, non-trigger, workflow, outputs, methodology, validation, agent boundaries, failure
handling, and deterministic mechanics rather than names.

Assign each responsibility one result:

- `EXACT`
- `OVERLAP`
- `EXTENSION`
- `REPLACEMENT`
- `NEW`
- `NOT RELEVANT`

Explain how many useful ideas are already covered, runtime-specific, rejected, or materially novel.

## Extract the smallest useful ideas

Do not propose importing a package merely because one part is useful. Group related novel ideas into the
smallest coherent canonical change. Prefer relationship type `INSPIRED-BY` or
`INDEPENDENT-REIMPLEMENTATION`; use `COPIED` or `ADAPTED` only when license scope and attribution are clear
and direct reuse is justified.

For each promotion candidate name the likely canonical capability, provenance record, compatibility risk,
positive and negative scenarios, collision case, security validation, license handling, and every affected
runtime adapter. A proposal remains inactive until an explicit commons promotion implements and validates it.

## Write and validate the review

Read `references/review-report-contract.md`. Preserve observed facts, interpretation, recommendation,
assumptions, conflicts, and unknowns as distinct statements. Run:

```bash
python3 tools/external_capabilities.py validate
```

End with `REJECT`, `NO CHANGE`, `REVIEWED`, or `PROMOTION-CANDIDATE`. State that no external code was
executed and no capability was installed. Zero novel ideas is a valid high-quality result.
