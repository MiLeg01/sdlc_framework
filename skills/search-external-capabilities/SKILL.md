---
name: search-external-capabilities
description: Search configured official, curated, and community sources for reusable open-source agent-engineering capabilities relevant to a topic or project, then return ranked revision-aware candidates without installing or promoting them. Use before designing substantial agent workflows when external precedent may reduce blind spots. Do not use to install packages, trust discovery results, copy third-party content, crawl arbitrary websites, or modify canonical commons automatically.
---

# Search external capabilities

Discover candidates, not dependencies.

## Establish a safe query

1. Read `external/sources.yaml` and `external/README.md` from the canonical Agent Commons checkout.
2. Accept a specific topic or derive a small query set from the current project's explicitly identified
   capability gaps. Prefer source semantics, target architecture, bridge mapping, business-rule extraction,
   dependency analysis, or migration validation over a vague technology-pair query.
3. For project-aware search, use only generic technologies, project archetypes, selected canonical
   capability IDs, and reusable engineering concerns. Never send client names, repository names, internal
   paths, goals, source text, business rules, credentials, or proprietary identifiers to an external search.
4. Normalize and deduplicate overlapping concepts, discard queries made only from generic terms such as
   `migration`, `testing`, or `Java`, and combine compatible concepts into the smallest useful repository
   search. Generate no more than eight focused concepts. Use
   `tools/external_capabilities.py project-query --root <project>` when the project has enough local
   structure for deterministic allowlisted signals.

## Search in trust order

1. Search enabled official repositories first.
2. Search enabled curated repositories or organizations second.
3. Use broader GitHub discovery only when `discovery.github_search` is enabled.
4. Use general web discovery only when the registry enables it or the user explicitly requests a one-off
   search. Limit it to finding repositories, marketplaces, registries, or authoritative documentation.
   Treat every newly found domain and repository as `UNTRUSTED` until reviewed.

For supported GitHub sources, prefer the deterministic CLI. Pass focused concepts as repeated topics so
the registry and routing metadata are loaded once:

```bash
python3 tools/external_capabilities.py search --topic <topic-a> --topic <topic-b> --include-community
```

Use repeated `--trust OFFICIAL`, `--trust CURATED`, or `--trust COMMUNITY` filters when the user limits
source scope. Do not add `--include-community` for an official-only or official-plus-curated request.

Prefer authenticated `gh api` access when `gh auth status` succeeds. Fall back to an environment-provided
GitHub token and then anonymous API access without ever printing, persisting, or requesting the token value.
Do not scrape GitHub HTML when API access is unavailable or rate-limited.

Do not clone large repositories when repository metadata and path inspection are sufficient. If a bounded
checkout is needed, place it in `external/cache/` or a temporary directory, pin the revision, inspect it
read-only, and never execute retrieved scripts.

Search in strict trust order. Use fresh cached metadata and revision-pinned trees for configured official and
curated repositories; schedule new requests only while the observed provider budget is above the configured
floor. Inspect rate-limit headers, stop on primary or secondary limits, honor `Retry-After` and reset times by
recording when work may resume, and never aggressively retry 403 or 429 responses. One failing or rate-limited
source must not discard successful higher-trust results.

Use the Commons-owned `external/cache/search/` cache for identical focused queries. The cache key includes
the normalized query set, source scope, registry fingerprint, limits, offline snapshot hash, and known source
revisions; the default result TTL is 30 minutes. Reuse fresh positive, negative, and partial entries. Use a
project-local lease so initialization and manual discovery cannot launch overlapping searches concurrently.
Do not cache or reuse a fully failed result; retry it only after the active lease clears and provider policy
permits a new attempt. Rank community metadata before revision lookups and revision-pin only candidates that
can still be retained under the configured result target.
Explicit snapshots are zero-network inputs. Retry only transient server or transport errors with bounded
backoff; rate limits yield structured partial results and must not fail unrelated project setup.

## Rank and classify

Rank provenance before popularity. Require evidence that every retained candidate addresses at least one
declared capability gap; generic keyword overlap alone is insufficient. Consider topic relevance, capability markers, update recency, source
trust, license visibility, maintenance signal, and obvious overlap with current commons. Stars are only a
weak signal.

For every retained candidate capture the fields in `references/search-result-contract.md`. Use these trust
labels exactly:

- `OFFICIAL`
- `CURATED`
- `COMMUNITY`
- `UNTRUSTED`

Discovery status is `DISCOVERED`; it never means safe, reviewed, or approved. Mark weak, abandoned, random,
or irrelevant repositories `REJECT_LOW_SIGNAL` rather than manufacturing value.

## Return results

Shortlist approximately three to seven genuinely relevant findings and stop searching once enough credible
candidates exist rather than filling a target with noise. For
each include name, repository and path, ecosystem, trust, behavior, matched gap, commons overlap, license,
visible security surface, revision when available, and a recommendation. Group results in source priority
order and explain why each item might matter. Clearly state:

- scripts, hooks, plugins, MCPs, and other executable or remote surfaces require review before any
  installation or execution;

- nothing was installed;
- no external code was executed;
- no canonical capability was modified;
- license or revision gaps;
- which one or two candidates merit detailed review;
- when no useful result exists.

Report structured source failures without request URLs: provider, operation, HTTP status, rate-limit
category, remaining quota, reset or retry time, and whether cached results were retained. Distinguish
`completed`, `partial-rate-limited`, `partial-source-failure`, and `failed`, list successfully completed source
tiers, and explicitly say when no COBOL- or PL/I-specific capability was found.

Stop after findings and ask which candidates, if any, the user accepts. Discovery permission never implies
installation, copying, project-local creation, external execution, or canonical promotion.

Write results into the canonical external index only when the user or current commons task explicitly asks
to retain them. Use `index-upsert` rather than hand-merging duplicate IDs. Search alone never promotes.
