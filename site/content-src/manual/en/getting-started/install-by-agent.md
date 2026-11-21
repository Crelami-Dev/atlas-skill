---
title: Install by Agent & CLI Reference
description: Destination paths, --global, --with-qa, --expose-subskills, --dry-run, update, and doctor across 7 supported AI coding agents.
---

Atlas-skill supports **7 AI coding agents** plus any `AGENTS.md`-compatible workspace. The CLI installer (`bin/atlas-skill.mjs` `v{{VERSION}}`) performs zero network calls while copying package files and never alters unrelated agent preferences.

## Project-Local Agent Matrix (`PROJECT_TARGETS`)

This table is automatically extracted from `PROJECT_TARGETS` in `bin/atlas-skill.mjs`:

{{AGENT_TABLE}}

## Global Installation Matrix (`--global`)

The following agents define standard user-home global directories (`GLOBAL_TARGETS` in `bin/atlas-skill.mjs`). For Windsurf, Cline, or Copilot custom locations, pass `--dir <PATH>`:

{{GLOBAL_AGENT_TABLE}}

## CLI Subcommands (`install`, `update`, `doctor`, `list`)

| Command | Behavior |
|---|---|
| `install` *(default)* | Copies the 3 core top-level skills (`atlas-skill`, `atlas-frontend`, `atlas-bug-hunter`) and supporting resources into the target agent path, then records SHA-256 hashes in `.atlas-install.json`. |
| `update` | Creates a complete backup of the existing managed installation under `.atlas-skill-backups/` before atomically replacing files. |
| `doctor` | Checks Node.js 18+, optional Playwright/Chromium availability, and validates every installed file's **SHA-256** digest against `.atlas-install.json` to catch drift or missing files. |
| `list` | Prints available frontend skills, QA suite modules, and supported agent paths. |

## Key CLI Flags Explained

### `--with-rules`
Writes lightweight rule adapters (such as `.agents/rules/atlas-frontend-gate.md`, `.cursor/rules/atlas-frontend-gate.mdc`, or `AGENTS.atlas.md`) without overwriting your existing `AGENTS.md` or custom rule files. Recommended especially for standard or fast models so gate verification is never skipped.

### `--with-qa`
Also installs the standalone Python QA & Security Suite from [suites/project-qa/](/atlas-skill/en/qa/project-qa-suite/) (`project-bug-hunter`, `project-security-auditor`, `project-fix-and-verify`). Combined with `--with-rules`, it also adds `qa-security-gate.md`.

### `--expose-subskills`
By default, Atlas exposes only **3 clean top-level commands** (`/atlas-skill`, `/atlas-frontend`, `/atlas-bug-hunter`) so your IDE menu stays concise. Pass `--expose-subskills` to expose all 10 internal phase modules (`atlas-plan`, `atlas-design`, `atlas-motion-animejs`, etc.) as sibling skill directories.

### `--global` and `--dir <PATH>`
- `--global`: Installs into user home directories (`~/.agents`, `~/.gemini/config`, `~/.claude`, `~/.cursor`) across all projects.
- `--dir <PATH>`: Targets an explicit custom directory (cannot be combined with `--agent all`).

### `--dry-run`
Validates the source package and prints the full file installation plan without touching disk.

```sh
node bin/atlas-skill.mjs install --agent antigravity --with-qa --with-rules --dry-run
```

## Live `--help` Output

```text
{{CLI_HELP}}
```
