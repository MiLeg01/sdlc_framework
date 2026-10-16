# Claude Code adapter

- Skills: AUTO mode links canonical folders into `~/.claude/skills/` when supported and otherwise installs
  managed copies; Claude Code documents symlink discovery.
- Agents: generate native Markdown definitions under `~/.claude/agents/`.
- Global instructions: manage one marked section in `~/.claude/CLAUDE.md`.
- Project instructions: generate a thin `CLAUDE.md` that imports shared `AGENTS.md`.
- MCP/config: user servers live in `~/.claude.json`; shared project servers use `.mcp.json`; settings use
  `.claude/settings.json` and `.claude/settings.local.json`.
- External imports can require trust approval. Windows AUTO mode falls back to managed copies when
  symlinks require unavailable Developer Mode or administrator privileges.

```bash
python3 install/agent_commons.py install claude-code
python3 install/agent_commons.py verify claude-code
```
