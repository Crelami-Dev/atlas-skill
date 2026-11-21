# Atlas Phase Workflow Guide (Phase 0 – Phase 7)

This document details the technical execution steps for each workflow phase referenced from [SKILL.md](../SKILL.md) (`/atlas-skill`) and [atlas-frontend](../skills/atlas-frontend/SKILL.md) (`/atlas-frontend`).

## Phase 0 — Visual Direction Selection (`deal-direction.mjs`)

Whenever the project lacks an existing design-token system, run the deterministic art-direction dealer:

```sh
node <atlas>/scripts/deal-direction.mjs --prompt "<user request>" --project <project-root> --write-tokens
```

Rationale: language models tend to revert to generic purple-blue gradients or flat gray backgrounds if palette polarity and font pairings are not locked upfront.

## Phase 1 — Design Brief Planning (`atlas-plan`)

Read [atlas-plan](../skills/atlas-plan/SKILL.md), [design-brief.en.md](../templates/design-brief.en.md) (or [design-brief.md](../templates/design-brief.md)), and [composition-selection.md](composition-selection.md).

- **Full Track:** Write 3 distinct structural alternatives (`### Alternative 1..3`) and validate with `node <atlas>/scripts/check-brief.mjs design-brief.md`.
- **Compact Track (for concise/clear prompts):** Add `<!-- atlas-brief: light -->` at the top of `design-brief.md` (or run `check-brief.mjs --light`) to document visitor job, real content, chosen layout, and verification plan without drafting 3 full alternatives.
- **Content Honesty:** Never fabricate customer counts or fake testimonials; fabricated data harms credibility and fails anti-slop checks.

## Phase 2 — Domain Research & Real/Generated Imagery (`atlas-research` + `image-generator` / `fetch-photos.mjs`)

Read [atlas-research](../skills/atlas-research/SKILL.md), [imagery.md](imagery.md), [research-template.md](research-template.md), and [domain-reasoning.md](domain-reasoning.md).

- **Generated or Real Photography on Visual Domains:** Whenever building for a visual domain (cafés, restaurants, hospitality, portfolios, real estate, e-commerce, travel, fashion, weddings, events) without user-provided photography, never draw manual `<svg>` scenes—either **generate bespoke images** (`image-generator` / `generate_image` into `<project-root>/assets/images/`) or download real CC0/CC-BY/Public-Domain photos from Wikimedia Commons:
  ```sh
  node <atlas>/scripts/fetch-photos.mjs --query "<subject 1>|<subject 2>|<subject 3>|<subject 4>" --out <project-root>/assets/photos --count 4
  ```
- **Photo Relevance Gate:** Before placing any image, apply [imagery.md](imagery.md) section 1b: hero shows the business's own subject, local context matches, and every image gets a one-line fit note in `## Image plan`. Run `fetch-photos.mjs` twice with differently phrased queries when the first batch is off-topic, and drop weak frames instead of filling slots.
- **Signature Idea:** Add `## Signature idea` to the brief (one distinctive move from the subject plus a `scene:` id or `none`), following [creative-direction.md](creative-direction.md). Optional assets: `atlas-backgrounds.css` (six token-built surfaces) and `atlas-interact.mjs`.
- **Content Language:** Write visitor copy in the language of the user's prompt (an Indonesian prompt gets Indonesian copy, including buttons, form labels and errors). Keep one language per page unless the brief asks for more.
- Skip `research-notes.md` on small prompts with familiar domains unless the user explicitly asks for reference research or the domain is unfamiliar.
- When running research, log adapted functional mechanisms (`ADAPTED`) and rejected visual clichés (`REJECTED`) so the layout learns structural solutions without cloning any single source site.

## Phase 3 — Token System & Surface Rhythm (`atlas-design`)

Read [atlas-design](../skills/atlas-design/SKILL.md), [typography.md](typography.md), and [interaction-design.md](interaction-design.md).

1. **Max 2 Proportional Font Families (+ 1 Optional Monospace):** Limit typography to at most 2 proportional font families (display & body) plus 1 optional monospace family for numeric/code alignment in `design-tokens.css` to keep page loads fast and hierarchy clear.
2. **Surface Polarity Cadence:** Alternate at least 3 calm surface color roles (`bg`, `surface`, `elevated`, `tint`, `blueprint`) so section transitions scan naturally.
3. **Token Validation:** Run `node <atlas>/scripts/check-tokens.mjs <project-root> --tokens <token-file>` to verify zero raw hex or scale values leak outside the token file.

## Phase 4 — UI Implementation, Visual Proof, & Motion (`atlas-lean-code` + `atlas-motion-animejs`)

Read [atlas-anti-slop](../skills/atlas-anti-slop/SKILL.md), [atlas-motion-animejs](../skills/atlas-motion-animejs/SKILL.md), [animejs-v4-playbook.md](animejs-v4-playbook.md), [atlas-lean-code](../skills/atlas-lean-code/SKILL.md), and [accessibility-and-behavior.md](accessibility-and-behavior.md).

1. **Real Visual Proof:** Include authentic visual proof (`<img>`, `<picture>`, `<canvas>`, `<video>`, `<svg data-viz>`, or `[data-atlas-proof]`) on landing pages so visitors grasp the subject rapidly. For pure documentation or typography pages, opt out via `<!-- atlas-proof: not-applicable -->`.
2. **Avoid Crude Wireframe Box or Floorplan SVGs:** Never draw raw box/polygon `<svg>` diagrams or `<rect>` table + `<circle>` chair schematics (`crude-floorplan-svg`) as a substitute for real photography or UI.
3. **Anime.js v4 Syntax, `15%` Scroll Reveals, & Signature Scenes:** Copy [atlas-scenes.mjs](../templates/atlas-scenes.mjs) + [atlas-scenes.css](../templates/atlas-scenes.css) and import Anime.js v4 named APIs (`animate`, `createScope`, `onScroll`, `stagger`, `utils`; or `https://cdn.jsdelivr.net/npm/animejs@4/+esm` in plain HTML). Trigger `[data-reveal]` sections at **`15%` viewport visibility (`threshold: 0.15` / `enter: 'bottom-=15% top'`)** with smooth, slightly slow `1100–1600ms` timing (`outQuart`) on every device, pair **one heavy and up to two light `data-atlas-scene` scenes** picked with `node <atlas>/scripts/deal-scene.mjs --prompt "<brief>" --project <root> --write` (ten scenes, see [scenes.md](scenes.md)), and never hide initial content with static `opacity: 0`.
4. **Phones & Tablets:** Design 320-1023 px as their own compositions per [mobile-and-tablet.md](mobile-and-tablet.md): cards become an `.atlas-carousel` (swipe on phones, 2-column grid on tablet portrait), galleries become an `.atlas-bento` mosaic or an `--always` carousel, no lone half-width pictures, no long single-column stacks (`mobile-long-stack`, `half-empty-row`). Below 1024 px every scene plays once at 15% visible instead of pinning; `html[data-atlas-motion]` reports the mode.
5. **Calls to Action & Copy:** Put actions in `.atlas-cta-row` from `templates/atlas-components.css` (equal-width stack on phones, primary first, at most two per row; the checker flags `cta-width-mismatch`). Write copy to the budgets in [copy-concise.md](copy-concise.md): headline 2-8 words, one supporting line, one concrete fact on the first screen, verb-led buttons. `check-copy.mjs` runs as gate 4b.
6. **Mobile Navigation Parity:** Every desktop header destination stays reachable at `<= 820px` through a visible menu control (`button[aria-expanded][aria-controls]`) or visible links; a lone call-to-action is not enough (`mobile-nav-missing`).
7. **Settled Reveals & No Dead Space:** Reveal animations must finish at full opacity (`partial-opacity`) and tall sections must not end far above their bottom edge (`dead-space`); fix both before critique.
8. **Lock Mobile Grid Widths (`min-width: 0`):** Use `minmax(0, 1fr)` and `min-width: 0` on CSS Grid children so wide tables or code specimens never overflow horizontally on `320px–375px` phones.

## Phase 5 — Gate Checks & Screenshot Inspection (`atlas-checker`)

Read [atlas-checker](../skills/atlas-checker/SKILL.md) and [visual-review.md](visual-review.md).

Run unified verification:
```sh
node <atlas>/scripts/run-gates.mjs <project-root> --mode full --strict --visual <entry-html-or-url> --shots-dir maintenance/screenshots
```
Open the resulting PNG screenshots (`1440x900`, `820x1180`, and `375x667`) directly using your image viewer, and resolve **all errors AND all warnings (`0 FAIL, 0 WARN`)** before proceeding.

## Phase 6 — Rubric Evaluation (`atlas-critic`)

Read [atlas-critic](../skills/atlas-critic/SKILL.md) and [critical-review.md](critical-review.md). Score the result across all 7 axes and issue `PASS` only if the total reaches at least `88/100` with **`0` errors, `0` warnings**, and verified visual/motion craft, or `FIX` with concrete, testable diffs.

## Phase 7 — Automatic Bug Hunter, Security/CVE Audit & Immediate Fix (`/atlas-skill` Only)

When running under `/atlas-skill` ([SKILL.md](../SKILL.md)), automatically execute [atlas-bug-hunter](../skills/atlas-bug-hunter/SKILL.md) (`project_inventory.py`, `ui_visual_bug_probe.py`, `security_scan.py`, `live_cve_osv_check.py`) and **immediately remediate all findings via [project-fix-and-verify](../suites/project-qa/skills/project-fix-and-verify/SKILL.md) without stopping for user approval** until 0 bugs and 0 security flaws remain. (Skipped when invoked via `/atlas-frontend`).
