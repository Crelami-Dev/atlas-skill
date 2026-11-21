# Atlas Frontend & Motion Design + QA Security Skill Suite (v7.0.0)

Universal, research-led, **anti-slop** frontend engineering, application UI architecture, and **Anime.js v4** choreography suite for AI coding agents (**OpenAI Codex, Google Antigravity IDE, Anthropic Claude Code, Cursor, Windsurf, Cline, GitHub Copilot**, and any `AGENTS.md`-compatible agent).

Engineered with **deterministic CLI phase gates** and **side-by-side Bad-vs-Good code guardrails** so even standard/fast models produce responsive, accessible, domain-specific interfaces without generic AI templates or legacy Anime.js v3 hallucinations.

## Quick Install Across AI Agents

Requires **Node.js 18+** (Node 22 LTS recommended) with zero runtime npm dependencies.

```sh
# Install the 3 focused top-level skills (/atlas-skill, /atlas-frontend, /atlas-bug-hunter) into OpenAI Codex or Google Antigravity IDE
node bin/atlas-skill.mjs install --agent antigravity --with-rules
node bin/atlas-skill.mjs install --agent codex --with-rules

# Install into Anthropic Claude Code (.claude/skills/)
node bin/atlas-skill.mjs install --agent claude

# Install into Cursor (.cursor/skills/ + .cursor/rules/*.mdc)
node bin/atlas-skill.mjs install --agent cursor --with-rules

# Install into Windsurf, Cline, or GitHub Copilot
node bin/atlas-skill.mjs install --agent windsurf --with-rules
node bin/atlas-skill.mjs install --agent cline --with-rules
node bin/atlas-skill.mjs install --agent copilot

# Install to ALL major project agent folders at once (.agents + .claude + .cursor + rules)
node bin/atlas-skill.mjs install --agent all --with-rules

# Workstation-wide GLOBAL install (active across every project on your machine!)
node bin/atlas-skill.mjs install --agent antigravity --global --with-rules
node bin/atlas-skill.mjs install --agent claude --global
node bin/atlas-skill.mjs install --agent codex --global
```

Or install directly via `npx` from GitHub (or npm) into any target project:

```sh
# Install the 3 top-level Atlas skills + Rules into all major agents:
npx --yes github:Crelami-Dev/atlas-skill install --agent all --with-rules

# Or install globally for Google Antigravity IDE:
npx --yes github:Crelami-Dev/atlas-skill install --agent antigravity --global --with-rules
```

## Architecture: 3 Focused Top-Level Entrypoint Skills + 10 Internal Modules

By default, Atlas installs **3 clean top-level skills** so your IDE slash-command menu stays uncluttered while every command runs a complete, self-checking pipeline:

| Top-Level Skill | Slash Command | Responsibility |
|---|---|---|
| [atlas-skill](SKILL.md) | `/atlas-skill` | **Full All-in-One Orchestrator:** Runs Frontend Design, Real Licensed Photography (`fetch-photos.mjs`), CSS Tokens, Anime.js v4 Motion, Visual Browser Verification **+ Automatic Bug Hunter & Security/CVE Audit + Immediate Auto-Fix** |
| [atlas-frontend](skills/atlas-frontend/SKILL.md) | `/atlas-frontend` | **Dedicated Frontend Orchestrator:** Runs Phases 0–6 end-to-end (Design, Real Photography, CSS Tokens, Anime.js v4 Motion, and mandatory `run-gates.mjs --visual` + `quick-check.mjs` + `atlas-critic`) **without** Bug Hunter / Security CVE scans |
| [atlas-bug-hunter](skills/atlas-bug-hunter/SKILL.md) | `/atlas-bug-hunter` | **Dedicated Bug & Security Hunter + Smart Fix Switch:** **Mode A (Default Read-Only):** Deep functional/UI bug + OWASP/live-CVE discovery & Markdown report (`PROJECT-AUDIT-REPORT.md`). **Mode B (When commanded to fix/repair):** Automatically executes [project-fix-and-verify](suites/project-qa/skills/project-fix-and-verify/SKILL.md) with 100% feature testing and zero-defect re-audit |

Each top-level orchestrator automatically loads the 10 internal phase modules as needed:

| Module | Responsibility |
|---|---|
| [atlas-plan](skills/atlas-plan/SKILL.md) | Concrete visitor job, truthful content audit, 3 distinct layout candidates, viewport & motion budget |
| [atlas-research](skills/atlas-research/SKILL.md) | Live browser or agent web-search reference analysis (`DIADAPTASI` mechanisms vs `DITOLAK` clichés) |
| [atlas-design](skills/atlas-design/SKILL.md) | 10 non-slop layout archetypes, intentional 2-family typography, semantic color contrast, media & placeholder strategy |
| [atlas-motion-animejs](skills/atlas-motion-animejs/SKILL.md) | Authentic **Anime.js v4** choreography (`animate`, `createTimeline`, `createScope`, `onScroll`, `spring`, `splitText`, `createLayout`, `svg`, `waapi`) |
| [atlas-ui-architecture](skills/atlas-ui-architecture/SKILL.md) | App shells, mandatory **5-State View Contract**, responsive tables/drawers, styled & accessible forms |
| [atlas-fullstack-contracts](skills/atlas-fullstack-contracts/SKILL.md) | Typed API/mock service boundaries, client security/env hygiene, OpenGraph/SEO/favicon readiness |
| [atlas-anti-slop](skills/atlas-anti-slop/SKILL.md) | 18 detectable AI slop patterns with Bad-vs-Good code contrasts & substitution test |
| [atlas-lean-code](skills/atlas-lean-code/SKILL.md) | Native HTML/CSS-first ladder, narrow client state, zero-CLS geometry, clean lifecycle teardown |
| [atlas-checker](skills/atlas-checker/SKILL.md) | Unified `run-gates.mjs` validator + multi-viewport Playwright / `/browser` screenshot audit |
| [atlas-critic](skills/atlas-critic/SKILL.md) | 100-point 7-axis adversarial rubric issuing `LOLOS` (`PASS`) or actionable `PERBAIKI` (`FIX`) diffs |

### Optional Project QA & Security Suite (`suites/project-qa/` / `--with-qa`)

Pass `--with-qa` during installation (e.g. `node bin/atlas-skill.mjs install --agent codex --with-qa`) to also install the standalone QA skills from [suites/project-qa/package-manifest.json](suites/project-qa/package-manifest.json):

| QA Skill | Responsibility |
|---|---|
| [project-bug-hunter](suites/project-qa/skills/project-bug-hunter/SKILL.md) | Read-only functional, async, and UI screenshot bug discovery |
| [project-security-auditor](suites/project-qa/skills/project-security-auditor/SKILL.md) | Read-only code sink scan and OSV/NVD/CISA dependency audit (supports `--offline-parse-only`) |
| [project-fix-and-verify](suites/project-qa/skills/project-fix-and-verify/SKILL.md) | Root-cause patching and regression verification after user approval |

## Deterministic Quality Gates (`run-gates.mjs`)

Standard models follow deterministic terminal pass/fail gates far more reliably than prose alone:

```sh
# Run Brief + Design Tokens + Anime.js v4 + Anti-Slop checks in one command:
node scripts/run-gates.mjs /path/to/target-project --mode full

# Individual validators:
node scripts/check-brief.mjs /path/to/target-project/design-brief.md
node scripts/check-tokens.mjs /path/to/target-project --tokens /path/to/target-project/design-tokens.css
node scripts/check-motion-v4.mjs /path/to/target-project
node skills/atlas-checker/scripts/slop-scan.mjs /path/to/target-project
```

### Optional Multi-Viewport Browser Audit (`quick-check.mjs`)

When Playwright + Chromium are available in the project or via `ATLAS_PLAYWRIGHT_PACKAGE` / `ATLAS_BROWSER_PATH`:

```sh
node skills/atlas-checker/scripts/quick-check.mjs http://127.0.0.1:3000 --shots ./maintenance/browser --click-test
```

See [installation & multi-agent setup](docs/INSTALLATION.md), [prompt instructions guide](docs/PROMPTS.md), [Anime.js v4 playbook](references/animejs-v4-playbook.md), and [18 slop patterns](references/slop-patterns.md) for complete documentation.

Documentation site (Indonesian & English): https://crelami-dev.github.io/atlas-skill/

## Empirical Evaluation Status (Independent Blind A/B Benchmark)

Blind evaluation conducted by an independent judge session (using the [evaluation protocol](evals/run-protocol.md) and [scoring rubric](evals/rubric.md) across 10 A/B cases with non-stub Baseline A pages built cleanly without the skill) recorded the following Round 3 results (see [independent evaluation summary](evals/independent-eval-2026-11-18.md) and [JSON data](evals/independent-eval-2026-11-18.json)):

- **Mean score (Round 3):** Baseline A **2.99 / 5.00** (`209/70`) vs Atlas B **4.04 / 5.00** (`283/70`), with **B winning 10 out of 10 cases**.
- **Layout diversity:** Met the diversity threshold (no more than 2 B-side pairs sharing the same macro skeleton).
- **Round 3 open finding (`v6.1.0`) & `v7.0.0` status:** On `v6.1.0`, the independent Round 3 judge flagged the visible `"GANTI DENGAN FOTO ASLI"` (`"REPLACE WITH REAL PHOTO"`) badge in visitor-facing UI across 5/10 visual-domain cases as a critical placeholder defect. In **`v7.0.0`**, that badge instruction has been removed from `references/imagery.md` and is automatically blocked via the `leaked-photo-placeholder-ui` rule in `slop-scan.mjs`, `check-visual-proof.mjs`, `quick-check.mjs`, and `visual_dom_inspector.py`; fresh empirical results await the next independent blind evaluation round. Raw `evals/results/` and `evals/archive-invalid/` artifacts remain excluded from the distribution package.

## Repository Validation

```sh
npm run validate
npm test
npm run test:export
```

MIT Licensed.
