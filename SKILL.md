---
name: atlas-skill
description: "Use when building, designing, auditing, or upgrading complete web interfaces, landing pages, dashboards, or full-stack web apps end-to-end—automatically running Frontend Design, Real Licensed Photography, CSS Tokens, Anime.js v4 Motion, Visual Browser Verification, AND Full Bug Hunter + Security/CVE Audit with immediate auto-remediation."
---

# Atlas All-in-One: Full Frontend Design + Auto Bug Hunter & Immediate Fix (`v7.0.0`)

Single-command end-to-end orchestrator (`/atlas-skill`) that executes every Atlas frontend design, real photography, CSS token, Anime.js v4 motion, and visual screenshot gate **plus** automatic deep bug hunting, security/live-CVE auditing, and **immediate root-cause auto-fix** without requiring manual sub-skill selection or stopping for approval when defects are discovered. See detailed phase instructions in [phase-workflow.md](references/phase-workflow.md).

## Choose Top-Level Atlas Skill

| Top-Level Skill | When to Use | Behavior |
|---|---|---|
| **`/atlas-skill` (This Skill)** | Full end-to-end web creation, redesign, or upgrade with zero-defect guarantee | Runs **Phases 0–6** (Frontend Design, `fetch-photos.mjs`, CSS Tokens, Anime.js v4, Visual Browser Gate & Critique) **+ Phase 7** (Bug Hunter + Security/CVE Audit + **Immediate Auto-Fix Loop**) |
| **[`/atlas-frontend`](skills/atlas-frontend/SKILL.md)** | Pure frontend design, UI/UX, real photography, motion, and visual browser verification | Runs **Phases 0–6** end-to-end (including mandatory `run-gates.mjs --visual`, `quick-check.mjs`, screenshot inspection, and `atlas-critic`) **without** running the Bug Hunter / Security CVE suite |
| **[`/atlas-bug-hunter`](skills/atlas-bug-hunter/SKILL.md)** | Dedicated bug & security vulnerability hunting (`PROJECT-AUDIT-REPORT.md`) + smart fix switch | **Mode A (Default Read-Only):** Deep bug + security/live-CVE audit & report. **Mode B (When user says fix/benerin/perbaiki):** Auto-switches to `project-fix-and-verify` 100% feature testing & zero-defect re-audit |

## Mandatory End-to-End Execution Pipeline (Phases 0–7)

Execute **all phases in sequence automatically**—never wait for the user to invoke sub-skills manually:

1. **Phase 0 — Visual Direction & Archetype:** Run `node <atlas>/scripts/deal-direction.mjs --prompt "<prompt>" --project <root> --write-tokens` to lock a domain-authentic macro layout and WCAG AA tokens (`design-tokens.css`).
2. **Phase 1 — Plan & Brief:** Read [atlas-plan](skills/atlas-plan/SKILL.md) and write `design-brief.md` using [design-brief.en.md](templates/design-brief.en.md) (Full Mode with 3 alternatives, or Compact Track with `<!-- atlas-brief: light -->` for concise prompts), including `## Image plan` on visual domains.
3. **Phase 2 — Reference Research & Real Licensed Photography:**
   - Read [atlas-research](skills/atlas-research/SKILL.md) when the domain is unfamiliar or research is requested.
   - **On visual domains without user-supplied photos**, run `node <atlas>/scripts/fetch-photos.mjs --query "<subject1>|<subject2>|<subject3>|<subject4>" --out <root>/assets/photos --count 4` to download real high-resolution CC0/CC-BY/Public-Domain photography from Wikimedia Commons (`assets/photos/credits.json`), per [imagery.md](references/imagery.md).
4. **Phase 3 — Visual System, Typography & Surface Cadence:** Read [atlas-design](skills/atlas-design/SKILL.md), [composition-selection.md](references/composition-selection.md), [composition.md](references/composition.md), and [imagery.md](references/imagery.md). Enforce `<= 2` proportional font families (`+ 1` optional monospace), `>= 3` surface polarity tokens, `65ch` reading measure, and `>= 44px` (`2.75rem`) tap targets.
5. **Phase 4 — Implementation, 5-State UI & Anime.js v4 Motion:** Read [atlas-lean-code](skills/atlas-lean-code/SKILL.md), [atlas-ui-architecture](skills/atlas-ui-architecture/SKILL.md), [atlas-fullstack-contracts](skills/atlas-fullstack-contracts/SKILL.md), [atlas-anti-slop](skills/atlas-anti-slop/SKILL.md), and [atlas-motion-animejs](skills/atlas-motion-animejs/SKILL.md).
6. **Phase 5 — Mandatory Deterministic Gates & Real Browser Screenshot Verification:**
   - Read [atlas-checker](skills/atlas-checker/SKILL.md). Always run `node <atlas>/scripts/run-gates.mjs <root> --mode full --strict --visual <entry-html-or-url> --shots-dir maintenance/screenshots` and `node <atlas>/skills/atlas-checker/scripts/quick-check.mjs <url> --shots maintenance/browser` **even if the user prompt did not explicitly ask to run a checker**.
   - Open the rendered PNG screenshots (`1440x900`, `820x1180`, `375x667`) directly with your file/image viewer to verify visual hierarchy, photography framing, alignment, and contrast.
7. **Phase 6 — Adversarial 7-Axis Design Critique:** Read [atlas-critic](skills/atlas-critic/SKILL.md) and score against [critical-review.md](references/critical-review.md). Fix any axis scoring below threshold immediately.
8. **Phase 7 — Automatic Bug Hunter, Security/CVE Audit & Immediate Auto-Fix (No Approval Pause):**
   - Run [project_inventory.py](suites/project-qa/skills/project-bug-hunter/scripts/project_inventory.py), [ui_visual_bug_probe.py](suites/project-qa/skills/project-bug-hunter/scripts/ui_visual_bug_probe.py), [security_scan.py](suites/project-qa/skills/project-security-auditor/scripts/security_scan.py), and [live_cve_osv_check.py](suites/project-qa/skills/project-security-auditor/scripts/live_cve_osv_check.py) (with `--auto-keywords` or `--offline-parse-only` when offline) plus deep logic/async/state tracing per [project-bug-hunter](suites/project-qa/skills/project-bug-hunter/SKILL.md) and [project-security-auditor](suites/project-qa/skills/project-security-auditor/SKILL.md).
   - **Immediate Auto-Remediation Rule:** Under `/atlas-skill`, do **NOT** stop and wait for user approval when bugs, layout defects, console errors, or security vulnerabilities are found—immediately execute [project-fix-and-verify](suites/project-qa/skills/project-fix-and-verify/SKILL.md) (surgical root-cause patching, 100% all-feature testing, [e2e_visual_regression.py](suites/project-qa/skills/project-fix-and-verify/scripts/e2e_visual_regression.py), [verify_feature_coverage.py](suites/project-qa/skills/project-fix-and-verify/scripts/verify_feature_coverage.py), and re-running `run-gates.mjs`) until **0 errors, 0 warnings, and 0 vulnerabilities** remain.

## Hard Rules & Rationale

- **Restrict the 2-column hero + workbench card pattern strictly to applications and dashboards:** Forcing search/filter/Reset toolbars onto restaurant, portfolio, event, or wedding pages makes every site look like a uniform SaaS template.
- **Fetch real licensed photography (`fetch-photos.mjs`) on visual domains instead of crude wireframe or schematic floorplan SVGs:** Real photography establishes immediate visual authenticity, whereas `<rect>` + `<circle>` table/chair schematics (`crude-floorplan-svg`) or placeholder badges destroy visitor trust.
- **Never expose debug state-switcher controls (Populated/Loading/Empty/Error) in production UI:** State-testing dropdowns are developer tools that confuse visitors and must stay hidden behind `?debug=1` if kept for testing.
- **Provide explicit styling rules for all form controls (`input`, `select`, `textarea`, `button`) and `>= 44px` tap targets on links:** Unstyled controls and `< 44px` nav links fail mobile ergonomics and visual cohesion.
- **Keep body copy at least `16px` with a `60–75ch` reading measure (`max-width: 65ch`) and at most 2 proportional font families (+ 1 optional monospace):** Overly wide prose (`> 75ch`) and excessive fonts degrade readability.
- **Never hide initial content with `opacity: 0` in static CSS:** Pages appear blank whenever JavaScript fails, loads slowly, or renders via SSR.
