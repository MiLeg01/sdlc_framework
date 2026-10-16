# Codex adapter

- Skills: AUTO mode links canonical folders into `~/.agents/skills/` when supported and otherwise installs
  managed copies; Codex documents symlink discovery.
- Agents: generate standalone TOML under `~/.codex/agents/` from canonical role definitions.
- Global instructions: manage one marked section in `~/.codex/AGENTS.md`.
- Project instructions: consume the shared project `AGENTS.md` directly.
- MCP/config: use `~/.codex/config.toml` or trusted project `.codex/config.toml`.
- Precedence and sources: see `adapter.yaml` and its official OpenAI documentation links.

Install and validate:

```bash
python3 install/agent_commons.py install codex
python3 install/agent_commons.py skills
python3 install/agent_commons.py verify codex
```

## Skill does not appear in Codex

1. Run `python3 install/agent_commons.py doctor` and inspect the **Agent Commons Skills** summary.
2. Run `python3 install/agent_commons.py skills --verbose` to compare every canonical skill with
   `$HOME/.agents/skills`.
3. Run `python3 install/agent_commons.py repair codex --skills-only` for missing or broken Commons-managed
   mappings without touching unrelated Codex agents or global instructions.
4. In Codex, run `/skills` or invoke the skill directly as `$<skill-name>`.
5. Restart Codex if the skill was installed or changed after the current session started.

Codex limits the initial skill metadata list. If `skills` reports a valid, enabled, discoverable mapping and
direct invocation works, omission from an abbreviated `$` picker is a Codex listing limitation, not an
installation failure. Do not duplicate global skills into projects or copy the catalog into `AGENTS.md`.
