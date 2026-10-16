# External capability sources

The canonical registry is `external/sources.yaml`. This catalog summarizes its current discovery surface;
the registry remains the machine-readable authority.

| Tier | Trust | Current sources | Behavior |
|---|---|---|---|
| 1 | `OFFICIAL` | Anthropic plugins, OpenAI skills and Codex, Cline, OpenCode, official MCP servers | Search first; still require license, security, semantic, and eval review |
| 2 | `CURATED` | Maintainer-added repositories, organizations, registries, or sites | Search after official sources; approval applies to source provenance, not individual capabilities |
| 3 | `COMMUNITY` | Broader GitHub discovery | Untrusted candidates, ranked and clearly labeled |
| 4 | `UNTRUSTED` | Optional general web discovery | Disabled by default; only discover repositories, registries, marketplaces, or authoritative documentation |

The external index at `external/index/capabilities.json` contains metadata only. Reviews under
`external/reviews/` are revision-pinned evidence and proposals, not installed capabilities.
