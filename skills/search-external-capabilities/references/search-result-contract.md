# External search result contract

Capture these fields for every retained result:

- stable external candidate ID;
- name or title;
- source ID, repository or registry, URL, and path;
- pinned commit or revision when available;
- source trust: `OFFICIAL`, `CURATED`, `COMMUNITY`, or `UNTRUSTED`;
- detected runtime or ecosystem;
- capability type: skill/workflow, agent, command, plugin, tool, MCP, hook, script, template, eval, or composite package;
- short purpose;
- one or more identified project capability gaps supported by repository metadata, paths, or descriptions;
- query relevance and ranking rationale;
- license status, identifier, and scope when readily available;
- last commit or update information when available;
- why it may be useful;
- obvious semantic overlap with Agent Commons;
- security surface visible from paths or metadata;
- lifecycle status and review recommendation;
- one concise recommendation: `STRONG CANDIDATE`, `USEFUL IDEAS ONLY`, `LOW VALUE`, or `REJECT`;
- discovery and last-checked dates.

Use `LICENSE UNKNOWN` when the scope cannot be established. In that state, copying source text or code is
prohibited. Do not infer safety from metadata or infer behavior from filenames alone; paths are discovery
leads that require content review.

The result must also include these safety facts:

```text
installed: false
executed_external_code: false
mutated_commons: false
```

At result level, record `candidate_count` after relevance filtering, normalized `queries`, source-tier
completion, cache use, request counts, and one of `completed`, `partial-rate-limited`,
`partial-source-failure`, or `failed`. Failure records are objects containing provider, operation, HTTP
status, primary/secondary rate-limit category, remaining quota, reset or retry time, source ID when
applicable, and whether cached results were retained. Never persist request URLs, credentials, response
bodies, or raw provider command output.
