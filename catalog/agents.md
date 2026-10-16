# Canonical agents and roles

| Agent | Independent value | Prefer a skill when |
|---|---|---|
| `architecture-reviewer` | A fresh findings-only context can challenge architecture evidence, boundaries, quality-attribute trade-offs, migration seams, and accidental complexity | The task is to design the architecture, implement it, or perform a low-consequence self-check |
| `financial-forecast-reviewer` | A fresh findings-only context can independently recompute consequential project forecasts and challenge source, period, unit, scenario, and reconciliation integrity | The task is to build the forecast, change its inputs, negotiate a commercial position, or grant approval |
| `legacy-discovery-specialist` | Isolated bounded workers can analyze non-overlapping source batches while a coordinator protects canonical state | The analysis is single-threaded or small |
| `privacy-security-reviewer` | A fresh adversarial context can challenge data handling, trust boundaries, abuse paths, controls, and unsupported claims | Independence adds no value or the task is remediation rather than review |
| `test-behavior-reviewer` | A fresh context can challenge RED validity, test layers, oracles, boundary cases, mocks, and false confidence | The task is to design the strategy or execute TDD rather than review evidence |

Canonical runtime-neutral sources live under `agents/`. Runtime adapters render native Codex TOML,
Claude Code Markdown, and OpenCode Markdown. Cline receives an explicit role-skill
mapping because its documented reusable subagent surface does not provide equivalent custom-role parity.

Traceability, frontend, accessibility, and visual QA remain skills that can be delegated to a fresh
general-purpose agent when independence matters; dedicated wrappers added no specialist behavior.
Implementation and TDD workers likewise execute canonical skills under coordinator ownership. Architecture
review is the narrow exception because independent adversarial judgment across decisions and quality
attributes is distinct from target design. No coordinator, product-owner, or framework-specific implementer
agent is promoted.
