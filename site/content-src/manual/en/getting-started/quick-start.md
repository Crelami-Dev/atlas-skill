---
title: Quick Start (5 Minutes)
description: Install Atlas-skill v{{VERSION}}, run your first agent prompt, and verify deterministic phase gate outputs in five minutes.
---

This guide takes a target project from zero to a built web interface that passes both static phase gates and multi-viewport browser checks.

## Prerequisites

- **Node.js 18+** (Node 20/22 LTS recommended) — required for the CLI installer and all static gates (`1–5` + `4b`).
- **Python 3** *(optional, required only for Gate 6 `--visual` and the QA Suite)* alongside Playwright/Chromium if running headless screenshot and DOM contrast inspection.

## Step 1: Install the Skill into Your Project

Run one of the commands below inside your target project root:

```sh
# Install into all major project agent folders (.agents, .claude, .cursor) + rule adapters
npx --yes github:Crelami-Dev/atlas-skill install --agent all --with-rules

# Or install locally from a cloned copy of the Atlas-skill repository:
node bin/atlas-skill.mjs install --agent antigravity --with-rules
```

To also expose the standalone Python QA & Security Suite (`project-bug-hunter`, `project-security-auditor`, `project-fix-and-verify`), append `--with-qa`:

```sh
npx --yes github:Crelami-Dev/atlas-skill install --agent codex --with-rules --with-qa
```

Want to preview paths without writing anything to disk? Add `--dry-run`:

```sh
npx --yes github:Crelami-Dev/atlas-skill install --agent claude --dry-run
```

## Step 2: Run Your First Prompt

Open your project folder in your AI coding agent and issue a slash command (or reference `SKILL.md`):

```text
/atlas-frontend Build a light studio landing page with measured CSS tokens, 15% scroll reveals via Anime.js v4, and verify screenshots at 375/768/1440 px.
```

For end-to-end delivery that also executes automated bug hunting and live-CVE remediation (Phase 7) right after UI verification, invoke `/atlas-skill`:

```text
/atlas-skill Build a scheduling web application with a 5-State UI Contract and auto-fix any QA or CVE findings.
```

## Step 3: Expected Output Artifacts

After your agent finishes [Phases 0–6](/atlas-skill/en/workflow/phase-workflow/), expect the following verified deliverables in your workspace:

| File / Deliverable | Source Phase | Purpose |
|---|---|---|
| `design-brief.md` | Phase 1 (`atlas-plan`) | Visitor task, real content inventory, 3 layout alternatives (or compact track), and image plan. |
| `design-tokens.css` | Phase 0 & 3 (`deal-direction.mjs`) | WCAG AA palette tokens, typography roles (`<= 2` proportional families + 1 optional mono), spacing, and timing tokens. |
| `.atlas-direction.json` / `.atlas-scenes.json` | Phase 0 & 4 | Seeded direction and scene history preventing repetitive layouts across builds. |
| Semantic HTML / CSS / JS | Phase 4 (`atlas-lean-code`, `atlas-scenes`) | Responsive layout with `>= 44 px` controls, zero static `opacity: 0`, and Anime.js v4 motion. |
| Gate 1–6 & Browser Screenshots | Phase 5 (`run-gates.mjs` & `quick-check.mjs`) | Passing checks for `check-brief`, `check-tokens`, `check-motion-v4`, `slop-scan`, `check-copy`, `check-visual-proof`, and `1440/820/375` screenshots. |

## Next Steps

- Review exact agent directories and CLI flags in [Install by Agent](/atlas-skill/en/getting-started/install-by-agent/).
- Read the [Architecture & 10 Modules](/atlas-skill/en/concepts/architecture/) overview generated from package manifests.
- Explore browser diagnostics in the [Findings Dictionary](/atlas-skill/en/checks/findings-dictionary/).
