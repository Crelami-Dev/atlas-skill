---
name: atlas-skill
description: Adaptive Taste & Layout Architecture System (ATLAS). Research-driven art direction, motion intelligence, and context-aware frontend design for coding agents. Selects compositions and motion patterns from project context, builds truthful interfaces, and verifies visual quality using browser inspection and anti-slop intelligence.
version: 2.0.0
---

# ATLAS Skill (Agent Edition)

> **Phase 5 Release:** Fully integrated Taste knowledge package, verified Anime.js motion adapter, contextual anti-AI-slop linting, and explainable design planning.

## 1. Architectural Contracts
- **Canonical Design Library:** Unified datasets in `data/` and `knowledge/taste/library/` (`art-directions.json`, `compositions.json`, `palettes.json`, `typography.json`, `motions.json`, `photos.json`, `app-shells.json`).
- **Runtime Execution Model:** Hybrid Python 3.9+ (retrieval, scoring, composition, anti-slop linting) + Node.js 22+ (real browser CDP visual inspection, screenshot QA).
- **Asset Hierarchy (DEC-003):** Tier 1 (Native AI generation) → Tier 2 (Licensed archive imagery from Met/AIC/Wikimedia) → Tier 3 (Semantic CSS/SVG fallback).
- **Adaptive Execution:** Single-agent mode default with optional multi-agent delegation contracts when supported by host.

## 2. Motion Intelligence & Anime.js Adapter
- **18 Researched Motion Signatures:** `masked-headline`, `shutter-image`, `scaling-wordmark`, `pinned-story`, `index-preview`, `curtain-footer`, `slow-crossfade`, `edge-marquee`, `drag-row`, `colour-on-scroll`, `stillness`, `opening-window`, `ink-fill`, `sheet-over`, `sideways-gallery`, `pushed-line`, `rolling-figures`, `carried-picture`.
- **Stillness as Intentional Craft:** In high-density interfaces, data dashboards, or clinical/minimal contexts, stillness is explicitly selected to respect reader focus and maximize information velocity.
- **Empirical Bézier Tokens:**
  - `--ease-out`: `cubic-bezier(0.22, 1, 0.36, 1)` (snappy interactive feedback <600ms)
  - `--ease-expo`: `cubic-bezier(0.16, 1, 0.3, 1)` (dramatic reveals >=800ms)
  - `--ease-in-out`: `cubic-bezier(0.76, 0, 0.24, 1)` (panel slides, wipes)
  - `--ease-soft`: `cubic-bezier(0.33, 1, 0.68, 1)` (subtle ambient photo scale)
  - `--ease-exit`: `cubic-bezier(0.55, 0.055, 0.675, 0.19)` (clean dismissals)
- **Runtime Adapter (`adapters/motion/animejs-adapter.js`):** Standalone zero-dependency runtime adapter translating motion specs into Anime.js v3/v4 execution or graceful native CSS transitions with 100% `prefers-reduced-motion` compliance and full lifecycle cleanup.

## 3. Context-Aware Anti-AI-Slop Rules
Rather than enforcing rigid, universal prohibitions, Atlas distinguishes:
1. **Hard Failures:** Broken DOM contracts, missing viewport tags, empty headlines, contrast < 3:1, unresolved template placeholders.
2. **Contextual Warnings:** Gratuitous neon purple/indigo gradients, repetitive identical cards with small icons, emoji bullet points in serious business contexts, monospace overload outside code.
3. **Design Rationale & Exceptions:**
   - Operational dashboards legitimately require structured card containers and dense tabular figures.
   - Editorial sites legitimately leverage asymmetric whitespace and large display serifs.
   - Minimalist sites deliberately employ stillness and generous negative space.
   - Futuristic/AI products may contextually utilize luminous gradients where motivated by the brief.

## 4. The 10-Step Execution Run
1. **Parse & Normalize Brief:** Extract sector, page_type, density, audience, and constraints into `ProductBrief`.
2. **Retrieve Contextual References:** Query `CanonicalLibrary` for eligible art directions, layouts, typographies, and motion patterns.
3. **Score & Rank Candidates:** Calculate multi-dimensional fit scores factoring sector synergy, density alignment, and tone overlap.
4. **Compose Design Plan:** Synthesize selected patterns into a deterministic, traceable `DesignPlan` (`brief → retrieved references → design decisions → generated output → validation`).
5. **Plan Motion Architecture:** Assign primary/secondary motion patterns or enforce stillness.
6. **Resolve Assets:** Source authentic imagery (AI generated or museum archive) satisfying the 40% hero focal area rule.
7. **Generate Semantic Markup:** Produce valid HTML5, fluid modern CSS (clamp, grid), and modular JavaScript.
8. **Inject Motion Adapter:** Bundle `animejs-adapter.js` and initialize motion triggers with reduced-motion safeguards.
9. **Audit Against Anti-Slop Intelligence:** Run `runtime/anti_slop.py` to flag cliches and verify contextual rationale.
10. **Visual QA & Browser Verification:** Validate layout integrity, contrast, and responsive viewports.
