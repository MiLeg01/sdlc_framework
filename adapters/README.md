# Runtime adapters

Agent Commons keeps workflows, roles, tools, templates, archetypes, and evaluations canonical. Adapters
only describe or generate the native files a runtime needs.

```text
canonical capability ID
        ↓
runtime-neutral source
        ↓
thin runtime adapter
        ↓
native discovery surface
```

## Verified capability matrix

| Commons concept | Codex | Claude Code | Cline | OpenCode |
|---|---|---|---|---|
| Global instructions | native `~/.codex/AGENTS.md` | native `~/.claude/CLAUDE.md` | native `~/.agents/AGENTS.md` compatibility | native `~/.config/opencode/AGENTS.md` |
| Project instructions | native `AGENTS.md` | `CLAUDE.md` imports shared `AGENTS.md` | native `AGENTS.md` | native `AGENTS.md` |
| Skills/workflows | native Agent Skills; documented symlinks | native Agent Skills; documented symlinks | native Agent Skills; generated wrapper | native Agent Skills; generated wrapper |
| Custom agents/roles | native TOML custom agents | native Markdown subagents | mapped to an explicit role skill; no claimed parity | native Markdown primary/subagents |
| MCP/tools | native `config.toml` | native user/project scopes | native runtime-managed JSON | native `opencode.json` |
| Archetypes | commons resolver | commons resolver | commons resolver | commons resolver |
| Evals | commons test suite | commons test suite | commons test suite | commons test suite |

The machine-readable source for this matrix is each `adapter.yaml`. Research was refreshed against the
official documentation URLs recorded there on 2026-08-18.

## Ownership

- Edit canonical behavior in `skills/`, `agents/`, `tools/`, `templates/`, `archetypes/`, and `evals/`.
- Edit runtime mapping, documentation URLs, native paths, and limitations in `adapters/`.
- Do not edit generated files under a runtime home. Run `sync`, `verify`, or `repair` through the installer.
- Wrapper skills contain only a canonical-source pointer and runtime limitation note; they are not a copy
  of the workflow body.

## Installation strategies

Codex and Claude Code explicitly document symlinked Agent Skill directories. AUTO mode uses links when the
host can create them and managed directory copies otherwise. Cline and OpenCode document skill locations
but do not promise symlink behavior; their adapters generate small `SKILL.md` wrappers that tell the runtime
to read the canonical source. Adapter `user_paths` entries are the single source for user-level destinations.
All generated files and managed copies are tracked in `$HOME/.agent-commons/install-manifest.json`.

Canonical project memory is runtime-neutral and remains inside each project under
`.agent-commons/memory/`. Codex or Claude Code may use native context or memory features as an optimization,
but those features never replace the portable Commons records. Cline and OpenCode consume the same files
through the canonical skill and deterministic manager.

## Adding another runtime

1. Research official current documentation for global and project instructions, skills or rules, custom
   roles, MCP/tools, configuration, precedence, discovery, symlinks, and safe automation.
2. Add `adapters/<runtime>/adapter.yaml` with documented support levels and limitations.
3. Add a renderer only for representation differences. Never copy canonical workflow bodies.
4. Declare user-level destinations in adapter metadata and extend lifecycle behavior without changing
   unrelated runtime state.
5. Add adapter generation, isolation, multi-runtime, removal, and unsupported-feature evaluations.
6. Update this matrix, README installation examples, reports, version, and changelog.
