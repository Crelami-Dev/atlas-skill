---
name: atlas-checker
description: "Use when running the 5 static run-gates.mjs validators plus multi-viewport browser screenshot and DOM aesthetic inspection before delivering any UI project. Do not use for projects without web UI code."
---

# Atlas Checker — Unified Gate & Screenshot Verification

Code that passes static syntax checks can still exhibit clipped headings, overlapping elements, or horizontal overflow in a real browser. Phase 5 pairs 5 deterministic static checks with multi-viewport screenshot inspection.

## Step 1 — Run Static Gates & Capture Screenshots

Execute the unified `run-gates.mjs` runner:

```sh
node <atlas>/scripts/run-gates.mjs <project-root> --mode full --visual <entry-html-or-url> --shots-dir maintenance/screenshots
```

Checks executed in order:
1. [check-brief.mjs](../../scripts/check-brief.mjs) — Validates required brief sections (English or Indonesian, full mode or `--light`).
2. [check-tokens.mjs](../../scripts/check-tokens.mjs) — Enforces max 2 proportional + 1 monospace font families and blocks raw color/scale values outside `design-tokens.css`.
3. [check-motion-v4.mjs](../../scripts/check-motion-v4.mjs) — Verifies Anime.js v4 syntax, `createScope` cleanup, and zero static `opacity: 0` traps on primary content.
4. [slop-scan.mjs](scripts/slop-scan.mjs) — Scans for AI clichés, placeholder text, leaked debug state switchers, and Anime.js v3 syntax.
5. [check-visual-proof.mjs](../../scripts/check-visual-proof.mjs) — Verifies real visual proof elements, catches leaked Markdown backticks in HTML, and blocks crude wireframe SVGs (pass `--strict` to elevate visual-proof warnings to errors).
6. [visual_dom_inspector.py](scripts/visual_dom_inspector.py) or [quick-check.mjs](scripts/quick-check.mjs) — Renders `1440x900`, `820x1180`, `390x844`, `375x667`, and `320x568` viewports via Chromium/CDP, saves PNG screenshots, and checks horizontal overflow, contrast, and broken media.

## Step 2 — Inspect Rendered PNG Screenshots Directly

Open the generated PNGs (`desktop_1440_top.png`, `desktop_1440_mid.png`, `mobile_375x667_top.png`) using your image/file reader (`view_file` or `Read`) because visual layout flaws often do not show up in JSON stdout:
- Confirm headings, tables, and primary actions remain fully legible and unclipped at `1440x900` and `375x667`.
- Confirm surface polarity transitions and editorial specimen plates look cohesive across dark and light sections.
- If any screenshot reveals visual defects, fix the CSS/HTML and re-run verification before proceeding to [atlas-critic](../atlas-critic/SKILL.md).
