# Runtime installation

`agent_commons.py` installs the same canonical Agent Commons checkout for macOS, Windows, and Linux. It
uses symlinks when available and managed copies when they are not, while preserving unrelated runtime
configuration.

## Manual Installation

1. Clone or copy Agent Commons to a permanent local folder.
2. Choose the runtime or runtimes to enable: Codex, Claude Code, Cline, or OpenCode.
3. Locate the runtime user directories listed below or run `agent_commons.py manual-install` to print them.
4. Enumerate every valid canonical directory under `skills/`, then link or copy every runtime-compatible
   skill into Codex/Claude destinations; generate the documented thin wrappers for Cline/OpenCode and native
   role files for supported runtimes. Do not maintain a selected manual subset unless that is intentional.
5. Merge the marked Agent Commons working-agreements section into existing global instructions.
6. Preserve every unrelated skill, agent, setting, instruction, and configuration file.
7. Start the runtime in a temporary project and confirm representative skills are discoverable and directly
   invocable.
8. After library updates, run the installer `skills` and `verify` commands or repeat the complete comparison.

### macOS example

From the canonical checkout, Codex can use symlinks safely when the destination names are free:

```bash
mkdir -p "$HOME/.agents/skills"
for skill in "$PWD"/skills/*; do
  test -f "$skill/SKILL.md" || continue
  target="$HOME/.agents/skills/$(basename "$skill")"
  test ! -e "$target" && test ! -L "$target" || { echo "occupied: $target" >&2; exit 1; }
  ln -s "$skill" "$target"
done
```

Claude Code uses `$HOME/.claude/skills`; generated agents belong under `$HOME/.claude/agents`. Codex agents
belong under `$HOME/.codex/agents`. Do not replace an existing destination. Cline and OpenCode require the
generated wrappers described by their adapters, so prefer the automated installer for those files.

### Windows PowerShell example

Copying works without Developer Mode or administrator symlink privileges:

```powershell
New-Item -ItemType Directory -Force "$HOME\.agents\skills" | Out-Null
Get-ChildItem ".\skills" -Directory | ForEach-Object {
  if (Test-Path (Join-Path $_.FullName "SKILL.md")) {
    $Target = Join-Path "$HOME\.agents\skills" $_.Name
    if (Test-Path $Target) { throw "Occupied skill destination: $Target" }
    Copy-Item -Recurse $_.FullName $Target
  }
}
```

Claude Code uses `$HOME\.claude\skills`; generated agents belong under `$HOME\.claude\agents`. Codex agents
belong under `$HOME\.codex\agents`. If a destination already exists, stop and determine whether it is
Agent Commons-managed; never overwrite it blindly. The installer records copy hashes and can synchronize
them safely, so managed installation is preferable to maintaining manual copies.

### Manual verification

- [ ] The canonical Agent Commons checkout remains intact.
- [ ] The runtime discovers commons skills and `initialize-project` is invocable.
- [ ] Canonical agents are available where the runtime supports them.
- [ ] Unrelated user configuration remains intact.
- [ ] No broken or stale links/copies remain.
- [ ] `agent_commons.py verify` passes for installer-managed artifacts.

## Automated installation

macOS or Linux:

```bash
python3 install/agent_commons.py install codex
python3 install/agent_commons.py verify codex
```

Windows PowerShell:

```powershell
py install\agent_commons.py install codex
py install\agent_commons.py verify codex
```

Install every verified adapter with `--all`. Omitting a runtime remains a backwards-compatible alias for
Codex. Use `--runtime <name>` if an option is more convenient than the positional runtime.

## Commands and strategies

- `install`: create missing managed artifacts and stop on unrelated conflicts.
- `sync`: synchronize unchanged managed copies and generated files after canonical changes.
- `status`: report `CURRENT`, `OUTDATED`, `MISSING`, `MODIFIED`, or `BROKEN` state without failing.
- `skills`: reconcile the complete canonical skill filesystem with Codex metadata, config, installed
  links/copies, duplicate names, and discovery paths. Add `--verbose` for the per-skill matrix or
  `--json --output <path>` for a deterministic portable inventory.
- `verify`: fail unless every selected runtime artifact is current.
- `repair`: back up and restore drifted artifacts already owned by the manifest.
- `uninstall-managed`: remove only the selected runtime's unchanged managed artifacts.
- `doctor`: show platform, Python, repository, recommended strategy, runtime detection, and health.
- `manual-install`: print a platform-aware informational checklist and runtime destinations.

Installation modes are `auto`, `symlink`, and `copy`:

```bash
python3 install/agent_commons.py install codex --install-mode auto
python3 install/agent_commons.py skills --verbose
python3 install/agent_commons.py repair codex --skills-only
python3 install/agent_commons.py sync codex
python3 install/agent_commons.py repair codex
python3 install/agent_commons.py uninstall-managed codex
```

`auto` prefers verified symlinks and falls back to managed copies. Explicit `symlink` fails with an
actionable message when link creation is unavailable. Explicit `copy` always installs managed directory
copies for Codex and Claude Code skills.

Add `--skills-only` to `install`, `sync`, or `repair` when only skill discovery should be managed. The
manifest records that scope so `verify` and `doctor` do not require unrelated agent or global-instruction
artifacts.

If an unrelated user skill already owns the same Codex name and destination, the installer preserves it and
creates a manifest-owned `agent-commons-<name>` alias that reads the canonical workflow. The `skills`
command reports the alias and its explicit invocation name. If both the canonical destination and the safe
alias destination are unrelated, installation stops without overwriting either.

## Codex discovery verification

Codex loads global user skills from `$HOME/.agents/skills` and repository-specific skills from
`.agents/skills`. Agent Commons installs global capabilities only in the user location; it does not copy them
into every project. Each installed mapping must expose a valid `SKILL.md` with non-empty `name` and
`description` metadata, remain enabled in `$HOME/.codex/config.toml`, and avoid unresolved duplicate names.

Use `/skills` or `$<skill-name>` for explicit inspection and invocation. Codex uses progressive disclosure
and bounds the initial metadata list, so a skill may be correctly installed and directly invocable even when
an abbreviated `$` picker does not display the complete catalog.

## Managed state and destinations

The neutral manifest is `$HOME/.agent-commons/install-manifest.json`. It records the canonical checkout,
library version, platform, runtime strategy, source and installed hashes, targets, timestamps, and backups.
Backups live under `$HOME/.agent-commons/backups/`.

| Runtime | Skills | Roles | Global instructions |
|---|---|---|---|
| Codex | `$HOME/.agents/skills/` | generated TOML in `$HOME/.codex/agents/` | managed section in `$HOME/.codex/AGENTS.md` |
| Claude Code | `$HOME/.claude/skills/` | generated Markdown in `$HOME/.claude/agents/` | managed section in `$HOME/.claude/CLAUDE.md` |
| Cline | wrappers in `$HOME/.cline/skills/` | explicit role skills | managed section in `$HOME/.agents/AGENTS.md` |
| OpenCode | wrappers in `$HOME/.config/opencode/skills/` | generated Markdown in `$HOME/.config/opencode/agents/` | managed section in `$HOME/.config/opencode/AGENTS.md` |

Runtime destination components come from `adapters/<runtime>/adapter.yaml`; installer functions do not
duplicate those locations. Use `--home <temporary-home>` for isolated tests and `--library <checkout>` only
when intentionally pointing to another canonical checkout.
