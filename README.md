# Atlas Frontend & Motion Design + QA Security Skill Suite (v7.0.0)

Universal, research-led, **anti-slop** frontend engineering, application UI architecture, and **Anime.js v4** choreography suite for AI coding agents (**OpenAI Codex, Google Antigravity IDE, Anthropic Claude Code, Cursor, Windsurf, Cline, GitHub Copilot**, and any `AGENTS.md`-compatible agent).

Engineered with **deterministic CLI phase gates** and **side-by-side Bad-vs-Good code guardrails** so even standard/fast models produce responsive, accessible, domain-specific interfaces without generic AI templates or legacy Anime.js v3 hallucinations.

## Quick Install Across AI Agents

Requires **Node.js 18+** (Node 22 LTS recommended) with zero runtime npm dependencies.

```sh
# Install into OpenAI Codex or Google Antigravity IDE (.agents/skills/ + optional rules)
node bin/atlas-skill.mjs install --agent antigravity --with-rules --expose-subskills
node bin/atlas-skill.mjs install --agent codex --with-rules --expose-subskills

# Install into Anthropic Claude Code (.claude/skills/)
node bin/atlas-skill.mjs install --agent claude --expose-subskills

# Install into Cursor (.cursor/skills/ + .cursor/rules/*.mdc)
node bin/atlas-skill.mjs install --agent cursor --with-rules

# Install into Windsurf, Cline, or GitHub Copilot
node bin/atlas-skill.mjs install --agent windsurf --with-rules
node bin/atlas-skill.mjs install --agent cline --with-rules
node bin/atlas-skill.mjs install --agent copilot

# Install to ALL major project agent folders at once (.agents + .claude + .cursor + rules)
node bin/atlas-skill.mjs install --agent all --with-rules --expose-subskills

# Workstation-wide GLOBAL install (active across every project on your machine!)
node bin/atlas-skill.mjs install --agent antigravity --global --with-rules --expose-subskills
node bin/atlas-skill.mjs install --agent claude --global --expose-subskills
node bin/atlas-skill.mjs install --agent codex --global --expose-subskills
```

Or install directly via `npx` from GitHub (or npm) into any target project:

```sh
# Install Frontend + QA & Security Suite + Rules + Sub-skills into all major agents:
npx --yes github:Crelami-Dev/atlas-skill install --agent all --with-rules --expose-subskills --with-qa

# Or install globally for Google Antigravity IDE:
npx --yes github:Crelami-Dev/atlas-skill install --agent antigravity --global --with-rules --expose-subskills --with-qa
```

## Architecture: 1 Orchestrator + 10 Focused Modules (+ Optional QA Suite)

Start at [SKILL.md](SKILL.md). Each phase loads only the module required at that moment to keep context lean:

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

See [installation & multi-agent setup](docs/INSTALLATION.md), [Anime.js v4 playbook](references/animejs-v4-playbook.md), and [18 slop patterns](references/slop-patterns.md) for complete documentation.

## Empirical Evaluation Status (Independent Blind A/B Benchmark)

Evaluasi buta oleh sesi juri independen (menggunakan [protokol evaluasi](evals/run-protocol.md) dan [rubrik penilaian](evals/rubric.md) pada 10 kasus A/B dengan Baseline A non-stub yang dibangun bersih tanpa skill) mencatat hasil berikut pada putaran ke-3 (lihat [ringkasan evaluasi independen](evals/independent-eval-2026-11-18.md) dan [data JSON](evals/independent-eval-2026-11-18.json)):

- **Skor rata-rata (Putaran 3):** Baseline A **2.99 / 5.00** (`209/70`) vs Atlas B **4.04 / 5.00** (`283/70`), dengan **B menang di 10 dari 10 kasus**.
- **Keberagaman layout:** Memenuhi batas keberagaman (tidak ada lebih dari 2 pasangan B yang dinilai berkerangka sama).
- **Temuan terbuka (KRITIS):** Juri independen Putaran 3 menilai badge `"GANTI DENGAN FOTO ASLI"` yang ditampilkan langsung di UI pengunjung pada 5/10 kasus domain visual (`02-photographer`, `03-event`, `05-product`, `06-restaurant`, `10-wedding`) sebagai cacat placeholder template yang belum dibersihkan. Artefak mentah `evals/results/` dan `evals/archive-invalid/` dikecualikan dari paket distribusi agar rilis tetap ramping.

## Repository Validation

```sh
npm run validate
npm test
npm run test:export
```

MIT Licensed.
