# Universal Multi-Agent Installation & Setup Guide (v7.0.0)

Atlas v7.0.0 requires **Node.js 18+** (20/22 LTS recommended) and zero external npm packages for installation and static quality gates. Run it directly via `npx` or local `node bin/atlas-skill.mjs`:

```sh
npx --yes github:Crelami-Dev/atlas-skill install --agent all --with-rules --expose-subskills --with-qa
```

## Supported AI Coding Agents & Paths

| Agent | Project-Local Flag & Path | Global Flag & Path (`--global`) | Optional Rule Adapter (`--with-rules`) |
|---|---|---|---|
| **OpenAI Codex** | `--agent codex` -> `.agents/skills/atlas-frontend-design` | `~/.agents/skills/atlas-frontend-design` | `AGENTS.md` (or `AGENTS.atlas.md`) |
| **Google Antigravity IDE** | `--agent antigravity` -> `.agents/skills/atlas-frontend-design` | `~/.gemini/config/skills/atlas-frontend-design` | `.agents/rules/atlas-frontend-gate.md` (or `~/.gemini/config/rules/`) |
| **Claude Code** | `--agent claude` -> `.claude/skills/atlas-frontend-design` | `~/.claude/skills/atlas-frontend-design` | Compatible with `CLAUDE.md` |
| **Cursor** | `--agent cursor` -> `.cursor/skills/atlas-frontend-design` | `~/.cursor/skills/atlas-frontend-design` | `.cursor/rules/atlas-frontend-gate.mdc` |
| **Windsurf** | `--agent windsurf` -> `.windsurf/skills/atlas-frontend-design` | *(use `--dir`)* | `.windsurf/rules/atlas-frontend-gate.md` |
| **Cline / Roo Code** | `--agent cline` -> `.clinerules/skills/atlas-frontend-design` | *(use `--dir`)* | `.clinerules/atlas-frontend-gate.md` |
| **GitHub Copilot** | `--agent copilot` -> `.github/skills/atlas-frontend-design` | *(use `--dir`)* | *(reference from `.github/copilot-instructions.md`)* |
| **All Major Agents** | `--agent all` -> `.agents` + `.claude` + `.cursor` | `~/.agents` + `~/.gemini/config` + `~/.claude` | Writes non-conflicting rule adapters |

## Key CLI Flags

- `--with-rules`: Writes lightweight native rule triggers (`.agents/rules/atlas-frontend-gate.md`, `.cursor/rules/atlas-frontend-gate.mdc`, `AGENTS.md`) without overwriting any existing user rule file. Essential when using **standard/non-frontier models** so the agent never forgets to run Atlas gates!
- `--expose-subskills`: Creates sibling skill folders (`atlas-motion-animejs`, `atlas-ui-architecture`, `atlas-anti-slop`, etc.) alongside `atlas-frontend-design` so slash commands like `/atlas-motion-animejs` and `/atlas-critic` appear directly in Antigravity IDE, Claude Code, and Codex CLI menus.
- `--global`: Installs into your user home config directory so every project inherits Atlas automatically.
- `update`: Backs up the existing managed installation into `.atlas-skill-backups/` before atomic replacement.
- `doctor`: Verifies SHA-256 file integrity, Node version, and optional Playwright/Chromium availability.

Primary external specifications verified:
- [Claude Code Skills](https://code.claude.com/docs/en/skills)
- [Google Antigravity Skills](https://antigravity.google/docs/skills/) & [Antigravity Rules](https://antigravity.google/docs/rules/)
- [OpenAI Codex Build Skills](https://learn.chatgpt.com/docs/build-skills) & [AGENTS.md](https://agents.md/)
- [Anime.js v4 Documentation](https://animejs.com/documentation/scope)
