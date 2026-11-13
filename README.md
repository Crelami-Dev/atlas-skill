# Atlas Skill

Research-led frontend design for coding agents. Atlas helps an agent investigate current references, choose a subject-specific composition, handle typography and useful interactions, implement simple robust code, and review the actual browser result.

**Version 4.0.0.** This repository replaces the old Python runtime, preset libraries and generated examples with a portable instruction package and a dependency-free Node.js installer.

## Install from GitHub

Run from the project where you want to use Atlas:

```sh
npx --yes github:Crelami-Dev/atlas-skill
```

The installer asks where Atlas should live:

```text
1. Agents       .agents/skills/atlas
2. Claude Code  .claude/skills/atlas
Choose [1/2]:
```

Choose **Agents** for AI tools that support the shared `.agents/skills` discovery path. This is not restricted to Codex or Antigravity; support depends on the tool. Choose **Claude Code** for its project skill directory. Neither choice installs globally.

For automation, skip the menu with `install --agent agents` or `install --agent claude`. The existing `codex` and `antigravity` flags remain compatible aliases for `agents`.

This repository may be private. Git must already have permission to read it; the installer does not request, store or print credentials. It does not change repository visibility. Node.js 22 or later is required.

The short command `npx atlas-skill install` is **not available from this repository alone**. That command requires a separately published npm package with that name. This repository remains marked private for npm publishing; no npm release is performed by these commands.

For reproducible installs, pin the Git URL to a reviewed commit with `#<commit-sha>`.

## Install destinations

| Target | Project-local destination |
|---|---|
| Agents (shared discovery) | .agents/skills/atlas |
| Claude Code | .claude/skills/atlas |

Without a target flag the terminal shows a menu; there is no silent default. In noninteractive environments pass `--agent` or a dedicated `--dir`. Use `--dir` for tools with another discovery path.

After installation, reload/restart the agent if required and explicitly ask it to use Atlas. File installation and integrity checks do not prove that an agent has activated the skill.

## Update and inspect

```sh
npx --yes github:Crelami-Dev/atlas-skill update --agent claude
npx --yes github:Crelami-Dev/atlas-skill doctor --agent claude
```

Update backs up the complete managed installation under .atlas-skill-backups in the working project before replacing it. Local edits and extra files remain in that backup. Unmanaged/legacy folders are never silently overwritten.

See [installation details](docs/INSTALLATION.md) for dry runs, migration, custom paths, recovery and limitations.

## The skill

Start with [SKILL.md](SKILL.md). One entry point coordinates six modules:

| Module | Responsibility |
|---|---|
| [Plan](skills/atlas-plan/SKILL.md) | Visitor job, honest content, scope, alternatives and verification |
| [Research](skills/atlas-research/SKILL.md) | Current live references, evidence levels, adaptation and rejection |
| [Design](skills/atlas-design/SKILL.md) | Composition, typography, media, color, geometry and mobile behavior |
| [Anti-slop](skills/atlas-anti-slop/SKILL.md) | Challenge generic structures, copied signatures and empty decoration |
| [Lean code](skills/atlas-lean-code/SKILL.md) | Native-first implementation, ownership, lifecycle and simplification |
| [Checker](skills/atlas-checker/SKILL.md) | Technical, behavioral and visual evidence; critique and completion audit |

Supporting [typography](references/typography.md), [interaction](references/interaction-design.md), [idea development](references/idea-development.md), [domain reasoning](references/domain-reasoning.md) and [critical review](references/critical-review.md) guides provide depth without prescribing a visual template.

The [dated research study](research/2026-11-13/README.md) is an example of evidence handling, not a permanent list of trends. A fresh design task must research again.

## Work on this repository

No runtime npm dependencies are needed for installation or package validation.

```sh
npm ci
npm run validate
npm test
npm run test:export
npm pack --dry-run
```

The [scenario review](evals/scenarios.md) checks instruction reasoning separately from automated tests.

### Optional browser audit

Playwright and Chromium must be available in the audit environment. They are not downloaded or installed by the Atlas installer.

```sh
node skills/atlas-checker/scripts/quick-check.mjs http://127.0.0.1:3000 --shots ./maintenance/browser
```

Audit is read-only by default. Add --click-test only for a controlled target where menu/tab actions are appropriate. Zero applicable controls reports SKIPPED.

For an explicitly requested one-screen mobile hero:

```sh
node skills/atlas-checker/scripts/quick-check.mjs http://127.0.0.1:3000 --shots ./maintenance/browser --hero "[data-hero]" --hero-action "[data-primary]" --fit-hero-under 420
```

Selectors must uniquely identify the scene and actual visible primary action. The checker includes 320x568, 375x667, 320x740, 360x800, 375x812, 390x844, 820x1180, 1366x768 and 1440x900.

Run controlled browser regressions with:

```sh
npm run test:browser
```

Set ATLAS_PLAYWRIGHT_PACKAGE to an absolute package.json that resolves Playwright, and ATLAS_BROWSER_PATH if using a particular Chromium.

### Read-only reference capture

```sh
node skills/atlas-research/scripts/capture-references.mjs --out ./maintenance/research --settle-ms 6000 https://example.com/
```

Open captures yourself. A cookie gate, security challenge or blank page is not a completed visual review.

## Package boundaries

The manifest allowlist keeps only instructions, supporting references, tools, controlled test fixtures, scenario evaluations and small research notes. Demos, generated sites, old Python engines, preset databases, screenshots, phase reports, dependencies, secrets and caches are not part of the release.

The legacy plugin.json is informational metadata, not a claim of marketplace registration.

## Limitations

Atlas is guidance plus limited verification tooling. It does not guarantee design quality, agent activation, full WCAG conformance, every interaction, photographic contrast, physical-device behavior or field performance. Critique and actual browser inspection remain required.

No license has been granted for public redistribution through npm in this package; package.json intentionally uses UNLICENSED and private:true until the owner chooses otherwise.
