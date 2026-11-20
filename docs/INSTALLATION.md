# Universal Multi-Agent Installation & Setup Guide (v7.0.0)

Atlas v7.0.0 requires **Node.js 18+** (20/22 LTS recommended) and zero external npm packages for installation and static quality gates. Run it directly via `npx` or local `node bin/atlas-skill.mjs`:

```sh
npx --yes github:Crelami-Dev/atlas-skill install --agent all --with-rules
```

By default, every standard agent installation creates **3 focused top-level skills** in the agent's skills directory:
1. **`atlas-skill` (`/atlas-skill`)** — Full All-in-One: Frontend Design, Real Licensed Photography (`fetch-photos.mjs`), CSS Tokens, Anime.js v4 Motion, Visual Browser Verification **+ Automatic Bug Hunter & Security/CVE Audit + Immediate Auto-Fix**.
2. **`atlas-frontend` (`/atlas-frontend`)** — Dedicated Full Frontend-Only Orchestrator (Phases 0–6 including `run-gates.mjs --visual`, `quick-check.mjs`, screenshot inspection, and `atlas-critic`, without Bug Hunter / Security CVE scans).
3. **`atlas-bug-hunter` (`/atlas-bug-hunter`)** — Dedicated Deep Bug & Security Vulnerability Hunter (Mode A: Read-Only Discovery & `PROJECT-AUDIT-REPORT.md`; Mode B: Auto-switches to `project-fix-and-verify` 100% feature testing & zero-defect re-audit when commanded to fix).

## Supported AI Coding Agents & Paths

| Agent | Project-Local Flag & Path | Global Flag & Path (`--global`) | Optional Rule Adapter (`--with-rules`) |
|---|---|---|---|
| **OpenAI Codex** | `--agent codex` -> `.agents/skills/{atlas-skill,atlas-frontend,atlas-bug-hunter}` | `~/.agents/skills/{atlas-skill,atlas-frontend,atlas-bug-hunter}` | `AGENTS.md` (or `AGENTS.atlas.md`) |
| **Google Antigravity IDE** | `--agent antigravity` -> `.agents/skills/{atlas-skill,atlas-frontend,atlas-bug-hunter}` | `~/.gemini/config/skills/{atlas-skill,atlas-frontend,atlas-bug-hunter}` | `.agents/rules/atlas-frontend-gate.md` (or `~/.gemini/config/rules/`) |
| **Claude Code** | `--agent claude` -> `.claude/skills/{atlas-skill,atlas-frontend,atlas-bug-hunter}` | `~/.claude/skills/{atlas-skill,atlas-frontend,atlas-bug-hunter}` | Compatible with `CLAUDE.md` |
| **Cursor** | `--agent cursor` -> `.cursor/skills/{atlas-skill,atlas-frontend,atlas-bug-hunter}` | `~/.cursor/skills/{atlas-skill,atlas-frontend,atlas-bug-hunter}` | `.cursor/rules/atlas-frontend-gate.mdc` |
| **Windsurf** | `--agent windsurf` -> `.windsurf/skills/{atlas-skill,atlas-frontend,atlas-bug-hunter}` | *(use `--dir`)* | `.windsurf/rules/atlas-frontend-gate.md` |
| **Cline / Roo Code** | `--agent cline` -> `.clinerules/skills/{atlas-skill,atlas-frontend,atlas-bug-hunter}` | *(use `--dir`)* | `.clinerules/atlas-frontend-gate.md` |
| **GitHub Copilot** | `--agent copilot` -> `.github/skills/{atlas-skill,atlas-frontend,atlas-bug-hunter}` | *(use `--dir`)* | *(reference from `.github/copilot-instructions.md`)* |
| **All Major Agents** | `--agent all` -> `.agents` + `.claude` + `.cursor` | `~/.agents` + `~/.gemini/config` + `~/.claude` | Writes non-conflicting rule adapters |

## Key CLI Flags

- `--with-rules`: Writes lightweight native rule triggers (`.agents/rules/atlas-frontend-gate.md`, `.cursor/rules/atlas-frontend-gate.mdc`, `AGENTS.md`) without overwriting any existing user rule file. Essential when using **standard/non-frontier models** so the agent never forgets to run Atlas gates!
- `--expose-subskills`: Optional power-user flag that also exposes the 10 internal phase modules (`atlas-plan`, `atlas-design`, `atlas-motion-animejs`, etc.) as separate sibling skill folders. Leave off by default to keep your IDE slash-command menu clean with just `/atlas-skill`, `/atlas-frontend`, and `/atlas-bug-hunter`.
- `--with-qa`: Optional power-user flag that also exposes the 3 granular QA sub-skills (`project-bug-hunter`, `project-security-auditor`, `project-fix-and-verify`) separately in addition to `/atlas-bug-hunter`.
- `--global`: Installs into your user home config directory so every project inherits Atlas automatically.
- `update`: Backs up the existing managed installation into `.atlas-skill-backups/` before atomic replacement.
- `doctor`: Verifies SHA-256 file integrity, Node version, and optional Playwright/Chromium availability.

Primary external specifications verified:
- [Claude Code Skills](https://code.claude.com/docs/en/skills)
- [Google Antigravity Skills](https://antigravity.google/docs/skills/) & [Antigravity Rules](https://antigravity.google/docs/rules/)
- [OpenAI Codex Build Skills](https://learn.chatgpt.com/docs/build-skills) & [AGENTS.md](https://agents.md/)
- [Anime.js v4 Documentation](https://animejs.com/documentation/scope)
