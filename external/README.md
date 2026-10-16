# External capability intelligence

This subsystem records what Agent Commons has discovered and deliberately reviewed outside the library.
It is an intelligence and proposal layer, not an installation surface.

```text
configured sources -> discovery -> review -> trust/license/security checks
                   -> semantic comparison -> generalized proposal -> eval -> promotion gate
```

No discovered capability becomes active merely because it appears here. Canonical skills, agents, tools,
templates, archetypes, and adapters still change only through the normal promotion workflow.

## Canonical and disposable paths

| Path | Status | Purpose |
|---|---|---|
| `sources.yaml` | Canonical | Lightweight registry of allowed discovery channels and source trust |
| `schema/` | Canonical | Machine-readable contracts for sources, index metadata, and reviews |
| `index/capabilities.json` | Canonical metadata | Small, revision-pinned discovery index; never a downloaded package cache |
| `reviews/` | Canonical evidence | Intentional reviews of selected external capabilities |
| `cache/` | Disposable | Optional temporary retrieval material; contents are ignored by Git |

External repositories, package archives, generated search dumps, and binaries do not belong in the
canonical index or review folders.

## Source tiers

1. **Official** — vendor- or standard-maintained authoritative repositories. This increases provenance
   confidence but does not bypass evaluation.
2. **Curated** — sources deliberately added by a maintainer after source-level review.
3. **Community** — broader GitHub discovery. Results are untrusted candidates until reviewed.
4. **General web** — optional repository, registry, marketplace, or documentation discovery. It is
   disabled by default and must never turn arbitrary webpages into reusable capabilities automatically.

GitHub discovery is not equivalent to trust. Stars, freshness, or an official-looking name are ranking
signals only.

## Add a source

Edit `external/sources.yaml`, add a stable ID, choose a supported source type, record its location, trust,
tier, enabled state, description, categories, review date, and notes, then run:

```bash
python3 tools/external_capabilities.py validate
```

Current deterministic search support covers GitHub repositories and organizations plus broader GitHub
repository discovery. Registry and website entries can guide an explicit human/agent review, but the CLI
does not crawl them. General web discovery remains an opt-in skill step and is disabled in the registry.

## Search and review

```bash
python3 tools/external_capabilities.py search \
  --topic "legacy modernization" \
  --include-community

python3 tools/external_capabilities.py project-query --root <project>
python3 tools/external_capabilities.py check-stale
```

Search prints ranked metadata. It does not install packages, execute code, or mutate commons. Use the
canonical `search-external-capabilities` workflow for scoped discovery and
`review-external-capability` for the deliberate review of one selected result.

Configured repository searches reuse cached metadata and revision-pinned trees, inspect GitHub request
budgets before scheduling more work, and retry only transient server or transport failures. Primary and
secondary rate limits are recorded without request URLs and are not retried aggressively. The search cache
keys normalized query sets by source scope, registry fingerprint, source revision, and snapshot identity;
fresh positive, negative, and partial entries are reusable. Project-local leases prevent duplicate manual and
initializer searches. A failing or rate-limited source produces structured partial discovery state without
discarding successful higher-trust results or blocking project setup.

When initialization identifies material capability gaps, derive three to eight focused queries from those
gaps instead of searching only for a technology pair. Preserve user source restrictions: official-only
must not fall through to curated or community discovery. Return a short project-aware shortlist, then stop.
Initialization may run this search concurrently and persist its state under project-owned `.agent-commons/`
metadata while core setup remains usable. Discovery does not authorize installation, copying, execution,
project-local creation, or commons changes;
the user must explicitly accept individual findings first.

## Promotion rule

Prefer extracting the smallest useful principle and independently implementing it in the canonical
model. Every promoted external-derived change must preserve one relationship type:

- `COPIED`
- `ADAPTED`
- `INSPIRED-BY`
- `INDEPENDENT-REIMPLEMENTATION`

`INSPIRED-BY` and `INDEPENDENT-REIMPLEMENTATION` are preferred when no source text or code must be copied.
Unknown licensing prohibits copying. Executable content requires stronger security review. Promotion must
still add evidence, evaluations, provenance, versioning, and runtime-adapter verification.
