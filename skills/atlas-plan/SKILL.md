---
name: atlas-plan
description: "Use when planning web page structure, visitor tasks, real content inventory, layout alternatives, and viewport budgets before writing UI code. Do not use for tiny CSS patches or single-line fixes."
---

# Atlas Plan — Structure and Content Planning

Writing a short brief before drafting HTML/JSX prevents agents from copying a uniform centered-hero + 3-card layout. Create `design-brief.md` using [design-brief.en.md](../../templates/design-brief.en.md) (English) or [design-brief.md](../../templates/design-brief.md).

## 1. Full Track vs Compact Track

- **Full Track:** Used for multi-section applications or full redesigns. Covers all 6 brief sections and at least 3 distinct structural alternatives (`### Alternative 1..3` or `### Alternatif 1..3`).
- **Compact Track:** Used for concise prompts or single-purpose pages. Add `<!-- atlas-brief: light -->` at the top of the brief (or run `check-brief.mjs --light`) so you only document the visitor task, real content, final layout choice, and verification plan without requiring 3 full alternatives or `research-notes.md`.

## 2. State One Concrete Visitor Task

Turn vague requests into observable user tasks:
- **Too Vague:** "A modern website for a coffee shop."
- **Specific:** "A visitor arriving from a local map search on a 375x667 phone can check drink price ranges, today's opening hours, and directions in at most two actions."

## 3. Content Honesty

Never write placeholder copy (`Lorem ipsum`, `Your Company`) or invent customer metrics and testimonials, because fabricated claims erode trust and fail `check-brief.mjs` and `slop-scan.mjs`.

## 4. Image Plan (Mandatory for Visual Domains)

For photography-dependent domains (photographers, restaurants, physical products, real estate, travel, fashion, weddings, and events), include an `## Image plan` (or `## Rencana gambar`) section in the brief per [imagery.md](../../references/imagery.md), as visual projects without an asset strategy tend to fall back to generic silhouettes.

## 5. Viewport & Motion Budget

- **Mobile Screens (`320x568` & `375x667`):** Keep the headline within 4 lines and ensure the primary action fits cleanly with zero horizontal overflow (`scrollWidth <= innerWidth`).
- **Anime.js v4 Choreography:** Plan at most 2–3 purposeful motion moments with entrance durations under `1200ms` and `prefers-reduced-motion` support so animation aids orientation without delaying interaction.

## Verification Command

Run `node <atlas>/scripts/check-brief.mjs design-brief.md` (add `--light` for compact track briefs) and confirm it exits with `PASS`.
