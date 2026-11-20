---
name: atlas-frontend
description: "Use when designing, building, or upgrading web interfaces, landing pages, dashboards, CSS token systems, real licensed photography, and Anime.js v4 animations with automatic multi-viewport visual verification—without running the backend/security Bug Hunter & CVE audit suite."
---

# Atlas Frontend Orchestrator — Design, Real Photography, Motion & Visual Gate (`v7.0.0`)

Complete, self-checking frontend design and engineering workflow (`/atlas-frontend`) that automatically orchestrates planning, domain research, real licensed photography (`fetch-photos.mjs`), CSS design tokens, 5-state UI architecture, Anime.js v4 motion, and **mandatory multi-viewport browser screenshot verification**—without running the Bug Hunter / Security CVE audit phase. See [phase-workflow.md](../../references/phase-workflow.md) for detailed technical reference.

## When to Use `/atlas-frontend` vs Other Top-Level Atlas Skills

- Use **`/atlas-frontend`** (this skill) when you want the complete Atlas frontend design, real photography, Anime.js v4 motion, and visual browser gate (`run-gates.mjs --visual` + `quick-check.mjs` + `atlas-critic`) **without** running the Bug Hunter and Security/CVE auditor.
- Use **[`/atlas-skill`](../../SKILL.md)** when you want the full frontend pipeline **plus** automatic Bug Hunter & Security/CVE scanning with immediate auto-remediation.
- Use **[`/atlas-bug-hunter`](../atlas-bug-hunter/SKILL.md)** when you want dedicated deep bug & security vulnerability hunting (`PROJECT-AUDIT-REPORT.md`) and 100% feature-tested remediation.

## Choose Execution Track

| Track | When to Use | Phases & Artifacts Executed |
|---|---|---|
| **Full Mode (New Project / Redesign)** | Multi-section landing page, web app, or complete redesign | Phases 0–6: `deal-direction.mjs`, `design-brief.md` (3 alternatives + `Image plan`), `fetch-photos.mjs`, `design-tokens.css`, `run-gates.mjs --visual`, `quick-check.mjs`, screenshot inspection, and `atlas-critic` |
| **Compact Track (Concise Prompt / Clear Domain)** | Single page or focused prompt with clear domain context | Phases 0, 1, 3–6: `deal-direction.mjs`, light brief (`<!-- atlas-brief: light -->`), `fetch-photos.mjs` (on visual domains), `design-tokens.css`, `run-gates.mjs --visual`, and screenshot inspection |
| **Feature / Component Mode** | Adding UI sections, tables, forms, or motion to an existing app | Phases 3–6: reuse host tokens, implement 5 UI states, Anime.js v4 `createScope`, `run-gates.mjs --mode light`, and visual browser verification |

## Mandatory Self-Checking Frontend Pipeline (Phases 0–6)

Execute every phase automatically in sequence—**always run the visual checker and inspect rendered PNG screenshots in Phase 5 even when the user prompt does not mention checking**:

1. **Phase 0 — Visual Direction & Archetype (`deal-direction.mjs`):**
   ```sh
   node <atlas>/scripts/deal-direction.mjs --prompt "<user prompt>" --project <root> --write-tokens
   ```
   Locks a domain-specific structural archetype (`macroLayout`), 2 proportional fonts (+ 1 optional monospace), and WCAG AA color tokens (`design-tokens.css`).
2. **Phase 1 — Design Brief & Content Inventory ([atlas-plan](../atlas-plan/SKILL.md)):**
   Draft `design-brief.md` using [design-brief.en.md](../../templates/design-brief.en.md) (or [design-brief.md](../../templates/design-brief.md)) with real visitor tasks, honest content (zero fabricated stats or fake quotes), 3 composition alternatives, and `## Image plan`. Validate with `node <atlas>/scripts/check-brief.mjs <root>/design-brief.md`.
3. **Phase 2 — Domain Research & Real/Generated Imagery ([atlas-research](../atlas-research/SKILL.md) + `image-generator` / `fetch-photos.mjs`):**
   - Read [imagery.md](../../references/imagery.md). Whenever building a visual-domain site (café, restaurant, hospitality, portfolio, real estate, e-commerce, travel, fashion, wedding, event) without user-provided photos, never draw manual `<svg>` scenes—either **generate bespoke images** using `image-generator` / `generate_image` into `<root>/assets/images/` or fetch real high-resolution CC0/CC-BY/Public-Domain photography from Wikimedia Commons:
     ```sh
     node <atlas>/scripts/fetch-photos.mjs --query "<subject 1>|<subject 2>|<subject 3>|<subject 4>" --out <root>/assets/photos --count 4
     ```
   - Embed the generated or downloaded local images (`assets/images/...` or `assets/photos/photo-01.jpg`) with explicit `width`, `height`, `aspect-ratio`, and descriptive `alt` text (plus 1-line footer attribution from `assets/photos/credits.json` when using Wikimedia photos).
4. **Phase 3 — Visual System, Typography & Surface Cadence ([atlas-design](../atlas-design/SKILL.md)):**
   Read [composition-selection.md](../../references/composition-selection.md), [composition.md](../../references/composition.md), and [typography.md](../../references/typography.md). Alternate `>= 3` surface polarity tokens (`--color-bg`, `--color-surface`, `--color-surface-elevated`, `--color-blueprint`), enforce `max-width: 65ch` on body copy (`main p, main li`), and ensure `min-height: 2.75rem` (`44px`) on all interactive controls and navigation links (`header a, nav a, footer a`).
5. **Phase 4 — Clean Code, 5-State UI & Anime.js v4 Motion:**
   Read [atlas-lean-code](../atlas-lean-code/SKILL.md), [atlas-ui-architecture](../atlas-ui-architecture/SKILL.md), [atlas-fullstack-contracts](../atlas-fullstack-contracts/SKILL.md), [atlas-anti-slop](../atlas-anti-slop/SKILL.md), and [atlas-motion-animejs](../atlas-motion-animejs/SKILL.md). Use authentic Anime.js v4 named imports (`animate`, `createTimeline`, `createScope`, `stagger`, `onScroll`, `spring`) with `(prefers-reduced-motion: reduce)` support and never hide initial content with static `opacity: 0`.
6. **Phase 5 — Mandatory Quality Gates & Real Browser Screenshot Inspection ([atlas-checker](../atlas-checker/SKILL.md)):**
   - Run all 5 deterministic gates + multi-viewport screenshot renderer:
     ```sh
     node <atlas>/scripts/run-gates.mjs <root> --mode full --strict --visual <entry-html-or-url> --shots-dir <root>/maintenance/screenshots
     ```
   - Run live HTTP/DOM geometry & interaction verification across Desktop (`1440x900`), Tablet (`820x1180`), and Mobile (`375x667`):
     ```sh
     node <atlas>/skills/atlas-checker/scripts/quick-check.mjs <url-or-local-server> --shots <root>/maintenance/browser
     ```
   - **Mandatory Vision Check:** Open the rendered PNG screenshots (`desktop_1440_top.png`, `desktop_1440_mid.png`, `desktop_1440_low.png`, `mobile_375x667_top.png`) using your image/file viewer tool (`read_file` / `view_file`) to inspect real visual quality. If any gate or visual check reports errors, warnings, or awkward layout, fix the code and re-run Phase 5 until `0 FAIL, 0 WARN`.
7. **Phase 6 — Structured 7-Axis Design Critique ([atlas-critic](../atlas-critic/SKILL.md)):**
   Evaluate the final rendered screenshots against [critical-review.md](../../references/critical-review.md) (`>= 88/100` required for `PASS`).
