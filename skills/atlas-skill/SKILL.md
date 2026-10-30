---
name: atlas-skill
description: Adaptive Taste & Layout Architecture System (ATLAS). Research-driven art direction, motion intelligence, and context-aware frontend design for coding agents. Selects compositions and motion patterns from project context, builds truthful interfaces, and verifies visual quality using browser inspection and anti-slop intelligence.
version: 2.1.0
---

# ATLAS Skill (Agent Edition)

Adaptive Taste & Layout Architecture System for high-fidelity, truthful frontend engineering.

## 1. Core Architectural Contracts (Always Active)
- **Execution Model:** Single-agent mode default with optional multi-agent delegation contracts. Python 3.9+ runtime (retrieval, composition, anti-slop linting) + Node.js 22+ (real browser CDP visual inspection).
- **Asset Hierarchy (DEC-003):** Tier 1 (Native AI generation) → Tier 2 (Licensed museum archive from Met/AIC/Wikimedia) → Tier 3 (Semantic CSS/SVG fallback).
- **Visual Asset & Chart Integrity (P0):** Zero Hallucinated Analytical Visualizations. Quantitative charts, sparklines, telemetry graphs, and ledgers must bind strictly to authentic, verified data. Never generate mock SVG curves with hardcoded or synthetic data points disguised as real analytical telemetry. Tier 3 fallbacks must render category-appropriate architectural or geometric illustrations without fictitious numbers, fake coordinate axes, or fake balance tooltips.

## 2. Content-Aware Layout Intelligence (P0 Contracts)
Before finalizing any interface, anticipate responsive layout stresses across viewports and variable-length content:
1. **The Flex Child Law:** Any flex child containing text that could truncate, wrap, or reflow MUST specify `min-width: 0`. Never apply a fixed pixel `max-width` on a flex item inside a table cell or grid item without `overflow: hidden; text-overflow: ellipsis;`.
2. **Table Column Priority Contract:** Classify columns into:
   - *Primary (Vital):* Entity name, core monetary amount. Must remain visible across all viewports.
   - *Secondary (Operational):* Status, billing cycle, primary action. May reflow into stacked rows.
   - *Tertiary (Descriptive):* Category badges, relative intervals, equivalent rates. Progressively fold or hide on viewports <=768px.
3. **Viewport Unit Constraint:** Page shells and layout containers must use `max-width: 100%`, never `max-width: 100vw`, preventing horizontal scroll blowout on systems with permanent vertical scrollbars (e.g. 17px Windows scrollbars).
4. **Progressive Adaptation Hierarchy:** Constrained horizontal space must adapt in order:
   Wrap Text → Reflow Elements to Stack → Shorten Secondary Text → Progressively Disclose → Clip with Ellipsis. Truncation must never silently discard unique data without access to full content.

## 3. Context-Aware Anti-AI-Slop Rules (P1 Foundations)
1. **Hard Failures:** Broken DOM contracts, missing viewport tags, empty headlines, contrast < 3:1, unresolved template placeholders.
2. **Multi-Accent Saturation Rule (P1.1):** Limit each UI container to one dominant brand accent. Flag containers with 3 or more distinct saturated accent color families (`multi-accent-container`). Reserve secondary saturated hues strictly for semantic status signals (success, warning, error).
3. **Corner Radius Consistency Rule (P1.2):** Peer components within the same structural family (peer cards or peer form controls) in a coherent container must share a consistent corner-radius token (`inconsistent-radius`). Differences $\ge 4\text{px}$ with ratio $\ge 1.5$ are flagged. Intentional component hierarchy (cards containing smaller-radii buttons) and circular avatars/chips (`badge-or-avatar`) are preserved.
4. **Contextual Exceptions:**
   - Operational dashboards legitimately require structured card containers and dense tabular figures.
   - Editorial sites legitimately leverage asymmetric whitespace and display serifs.
   - Playful, eclectic, or asymmetric brief tones contextually permit diverse palettes or varied radii (downgraded to INFO).

## 4. Motion Intelligence & Stillness
- **Stillness as Intentional Craft:** In high-density interfaces, data dashboards, or clinical/minimal contexts, stillness is explicitly selected to respect reader focus and maximize information velocity.
- **Empirical Bézier Tokens:**
  - `--ease-out`: `cubic-bezier(0.22, 1, 0.36, 1)` (snappy interactive feedback <600ms)
  - `--ease-expo`: `cubic-bezier(0.16, 1, 0.3, 1)` (dramatic reveals >=800ms)
  - `--ease-in-out`: `cubic-bezier(0.76, 0, 0.24, 1)` (panel slides, wipes)
  - `--ease-soft`: `cubic-bezier(0.33, 1, 0.68, 1)` (subtle ambient photo scale)
  - `--ease-exit`: `cubic-bezier(0.55, 0.055, 0.675, 0.19)` (clean dismissals)
- **Reduced Motion:** 100% `prefers-reduced-motion` compliance and full lifecycle cleanup via `adapters/motion/animejs-adapter.js`.

## 5. Progressive Reference Loading Protocol (P2 Protocol)
To minimize token consumption and context bloat, agents must follow progressive loading:

### 5.1 Loading Invariants
1. **Zero Default Loading:** Do NOT read reference files by default for routine bug fixes, maintenance, or simple layout adjustments. Core instructions above are self-sufficient.
2. **Just-in-Time Loading:** Read only the reference file(s) strictly mapped to the current task domain before making dependent architectural decisions.
3. **Session De-duplication:** Never re-read a reference file already available in the current context.
4. **Missing Reference Fallback:** If a referenced file is missing or unreadable on disk:
   - Do NOT fabricate or guess reference contents.
   - Proceed using the core contracts in `SKILL.md`.
   - Explicitly document the missing reference in the task output.

### 5.2 Task-to-Reference Mapping Table
Inspect the active task requirements and read only matching references from `knowledge/taste/references/`:

| Task Domain & Intent | Trigger Condition | Reference to Read | Core Guidance Delivered |
|---|---|---|---|
| **Dashboards & Dense Apps** | `page_type: "app"`, high data density, metrics, tables, admin consoles | `knowledge/taste/references/app-screens.md` | Type-driven KPIs over cards, quiet chrome, honest data states, flat surfaces, dense grid hierarchy. |
| **Color & Visual Styling** | Architecting palettes, CSS color tokens, dark/light themes | `knowledge/taste/references/colour.md` | Single-accent discipline (`--accent`), semantic token roles (`--bg`, `--surface`, `--ink`), no rainbow badges. |
| **Layout & Grid Systems** | Page layouts, grid structures, responsive breakpoints, editorial rhythm | `knowledge/taste/references/layout.md` | Deliberate margins, off-center text anchoring, avoiding reflexive centered wrappers, mobile composition. |
| **Anti-Slop & Quality Audit** | Final design review, eliminating AI clichés before shipping | `knowledge/taste/references/tells.md` | Audit against 3-wave AI tells (repetitive 3-card arrays, purple glows, pill fatigue, trapped icons). |
| **Typography & Scale** | Custom typography scales, typeface pairings, fluid type | `knowledge/taste/references/type.md` | Proportional scales, line-length limits (45-75 chars), deliberate display vs text pairings. |
| **Motion & Animation** | Adding interactive animations, complex transitions | `knowledge/taste/references/motion.md` | 18 motion signatures, easing curves, choreography; enforces stillness where appropriate. |
| **Imagery & Focal Points** | Sourcing photography, hero visual composition | `knowledge/taste/references/imagery.md` | 40% hero visual focal ratio, framing, aspect ratios, authentic non-stock visual style. |
| **Copy & Messaging** | Headline copywriting, conversion CTAs, microcopy | `knowledge/taste/references/copy.md` | 2-line headline rule (24-32 chars), honest value propositions, active verbs. |
| **Heuristic Critique** | Formal heuristic review of existing design | `knowledge/taste/references/critique.md` | Structured evaluation checklist across 10 usability and visual dimensions. |
| **Narrative Scenes** | Storytelling, multi-stage scroll journeys | `knowledge/taste/references/scenes.md` | Narrative pacing, episodic section transitions, perspective shifts. |
| **Sector Research** | Exploratory benchmarking for unfamiliar industries | `knowledge/taste/references/research.md` | Cross-sector aesthetic archetypes and domain-specific visual conventions. |

## 6. Execution Lifecycle & Browser QA Gates
1. **Parse & Normalize Brief:** Extract sector, page_type, density, audience, and constraints into `ProductBrief`.
2. **Retrieve Contextual References (On-Demand):** Read only the specific reference file(s) mapped in Section 5.2.
3. **Compose Design Plan:** Synthesize selected patterns into a traceable `DesignPlan` (`brief → retrieved references → design decisions → generated output → validation`).
4. **Generate Semantic Markup & Styling:** Produce semantic HTML5 and fluid modern CSS governed by layout and color rules.
5. **Anti-Slop Linting:** Execute `runtime/anti_slop.py` (checks `multi-accent-container` and `inconsistent-radius`) and review against `tells.md`.
6. **Browser QA Verification (P3 Multi-Tier Gates):**
   - Gate 1: Build & component tests pass (`exit code 0`).
   - Gate 2: Static runtime health check reports zero broken assets.
   - Gate 3: Headless browser CDP inspection verified across 5 standardized viewports (Desktop `1440px`, Landscape Tablet `1024px`, Portrait Tablet `768px`, Modern Mobile `390px`, Small Mobile `320px`) with zero horizontal overflow (`scrollWidth <= clientWidth`).
   - Gate 4: Zero uncontained element collisions measured in rendered DOM (`overlapPx === 0`).
