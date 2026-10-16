# Cline adapter

- Skills: generate thin wrappers under `~/.cline/skills/` because official documentation does not promise
  symlinked skill discovery.
- Roles: map canonical agents to explicit role skills. Cline's documented subagents are experimental,
  read-only research workers rather than reusable custom role definitions.
- Global instructions: manage one marked section in `~/.agents/AGENTS.md`, which Cline documents as a
  cross-tool global instruction source.
- Project instructions: consume shared `AGENTS.md` directly; `.clinerules/` remains available for
  project-specific Cline rules.
- MCP: the CLI uses `~/.cline/mcp.json`; IDE extensions expose their managed MCP settings file.

```bash
python3 install/agent_commons.py install cline
python3 install/agent_commons.py verify cline
```
