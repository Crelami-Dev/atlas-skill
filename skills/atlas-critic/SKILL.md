---
name: atlas-critic
description: "Use when evaluating final rendered web page quality across the 7-axis design, typography, accessibility, and code leanness rubric to issue PASS or FIX. Do not use before atlas-checker completes."
---

# Atlas Critic — 7-Axis Rubric Evaluation

Review the rendered screenshots from [atlas-checker](../atlas-checker/SKILL.md) alongside [critical-review.md](../../references/critical-review.md), as code inspection alone routinely misses hierarchy and legibility issues. Score out of 100 points across 7 axes:

| Axis | Max Pts | Evaluation Criteria |
|---|---:|---|
| **1. First-Screen Clarity & Visual Proof** | 20 | Visitors immediately grasp the product/service purpose; real visual proof is present (real photos or domain editorial specimen plates with zero `"Replace with photo"` / `"PHOTO SLOT"` badges); primary CTA is crisp at `1440x900` and `375x667`. |
| **2. Domain Specificity & Substitution Test** | 20 | Macro layout and content fit the exact subject; free of 3 generic icon cards and crude wireframe box SVGs. |
| **3. Typography & Readability** | 15 | Max 2 proportional + 1 monospace font families; tabular numerals in tables/metrics; zero leaked raw Markdown backticks in HTML. |
| **4. Surface Rhythm & Contrast** | 15 | Deliberate surface polarity cadence across sections; all text meets WCAG AA contrast (`>= 4.5:1`). |
| **5. Anime.js v4 Choreography** | 10 | Uses `createScope` with `revert()`, GPU transform properties, and `prefers-reduced-motion` support. |
| **6. 5-State Completeness & Mobile Fit** | 10 | Loading, populated, empty, zero-match + Reset, and error states handled cleanly with zero horizontal overflow at `320px`/`375px`. |
| **7. Code Hygiene & Client Security** | 10 | Zero console errors, zero `innerHTML` XSS sinks, zero leaked secrets, and all static gates passing. |

## Verdict Rules

- **`PASS` (`>= 88/100` with zero major functional/visual defects):** Ready for delivery alongside honest verification scope and any remaining limits.
- **`FIX` (`< 88/100` or visible screenshot defects):** Fix up to 3 highest-impact defects, re-capture screenshots, and re-verify (max 3 rounds).
