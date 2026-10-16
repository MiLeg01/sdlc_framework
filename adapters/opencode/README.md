# OpenCode adapter

- Skills: generate thin wrappers under `~/.config/opencode/skills/`; official docs list native and
  compatibility paths but do not promise symlink behavior.
- Agents: generate native Markdown subagents under `~/.config/opencode/agents/`.
- Global and project instructions: use native `AGENTS.md` locations.
- MCP and other settings: merge through `~/.config/opencode/opencode.json` and project `opencode.json`.
- Project `.opencode/` directories can also hold agents, commands, plugins, skills, tools, and themes.

```bash
python3 install/agent_commons.py install opencode
python3 install/agent_commons.py verify opencode
```
