# Atlas-Skill: Integration Assessment & Disposition Strategy

**Assessment Date:** October 30, 2026  
**Status:** Complete  
**Scope:** `taste-skill`, `atlas-frontend-design`, `project-atlas-v0.2.0-alpha`  

---

## 1. Component Disposition Summary

Every component across the three source repositories has been evaluated and assigned an actionable integration disposition:

| Action | Component Count | Description |
| :--- | :---: | :--- |
| **REUSE** | 48 | Retain substantially unchanged (e.g. `cdp.mjs`, `atlas_select.py`, `atlas_check.py`, `app.css`, `charts.js`, licenses). |
| **MERGE** | 42 | Combine into a single unified artifact (e.g. data libraries, markdown references, manifests, skill workflows). |
| **REWRITE** | 4 | Re-implement to resolve technical limitations (e.g. `frontmatter.mjs` test, image generation adapter, unified selector). |
| **DROP** | 11 | Exclude from the target project with documented justification (e.g. obsolete 20-pattern library, duplicate files). |

---

## 2. Detailed Duplication Analysis

Direct file comparison identified substantial redundancy between `atlas-frontend-design` and `project-atlas-v0.2.0-alpha`:

### 2.1 Identical or Near-Identical Documentation
* **Vanilla Components:**
  * Source 1: `atlas-frontend-design/references/vanilla-patterns.md` (6,509 bytes)
  * Source 2: `project-atlas-v0.2.0-alpha/project-atlas/skills/atlas-design/references/vanilla-patterns.md` (6,509 bytes)
  * *Disposition:* **REUSE** from `atlas-frontend-design`. Identical SHA-256 hash.
* **Large HTML Safeguards:**
  * Source 1: `atlas-frontend-design/references/large-html.md` (3,349 bytes)
  * Source 2: `project-atlas-v0.2.0-alpha/project-atlas/skills/atlas-design/references/large-html-files.md` (3,365 bytes)
  * *Disposition:* **MERGE** into `atlas-skill/skills/atlas-skill/references/large-html-files.md`. The latter has minor typo fixes.
* **Evaluation Rubric:**
  * Source 1: `atlas-frontend-design/references/rubric.md` (3,646 bytes)
  * Source 2: `project-atlas-v0.2.0-alpha/project-atlas/skills/atlas-design/references/evaluation-rubric.md` (3,646 bytes)
  * *Disposition:* **MERGE** into `references/evaluation-rubric.md`.
* **Benchmark Briefs:**
  * Source 1: `atlas-frontend-design/benchmark/briefs.json` (3,120 bytes)
  * Source 2: `project-atlas-v0.2.0-alpha/project-atlas/benchmarks/briefs.json` (3,118 bytes)
  * *Disposition:* **REUSE** the 12 briefs with public/held-out split.

---

## 3. Schema Comparison & Migration Requirements

A critical question of this audit is: **Can the data libraries of Taste-Skill and Atlas be merged directly?**  
**Verified Answer:** **No, a naive merge is impossible due to fundamentally different data models and abstractions.**

### 3.1 Schema Collision & Incompatibility Analysis
1. **Atlas `compositions/library.json` Model:**
   * Abstraction: **Layout Composition Patterns** (slots: `nav`, `hero`, `features`, `pricing`, etc.).
   * Schema: Root object with `version`, `vocabulary`, and `patterns[]`.
   * Sample pattern keys:
     `id`, `family`, `name`, `intent`, `page_types`, `categories`, `tones`, `density`, `requires`, `visual_tags`, `composition`, `responsive`, `motion`, `accessibility`, `avoid_when`, `related`, `incompatible`, `goals`.
2. **Taste-Skill `library/*.json` Model:**
   * Abstraction: **Decomposed Aesthetic Facets** across 9 independent JSON files.
   * `directions.json`: 20 macro art direction concepts (`idea`, `colour`, `paletteTags`, `sectionTags`, `richness`, `pitfalls`).
   * `heroes.json` & `sections.json`: Detailed DOM blueprints (`blueprint` array containing tag, class, and hierarchy definitions) tied to `needs` (e.g. `["photo"]`).
   * `palettes.json`: 56 color palettes with exact hex codes for semantic tokens (`bg`, `surface`, `ink`, `muted`, `accent`, `accentInk`).
   * `type.json`: 44 typography scales, Google Fonts links, and fallback stacks.
3. **Project-Atlas `composition-library.json` (Scaffold):**
   * Early 20-pattern file with keys: `id`, `family`, `name`, `best_for`, `content_needs`, `mobile_rule`, `failure_modes`.
   * *Verdict:* **DROP entirely.** It lacks the machine-readable scoring metadata required by `atlas_select.py`.

### 3.2 Real Conflict Example
```json
// Atlas Pattern (atlas-frontend-design):
{
  "id": "hero-editorial-split",
  "family": "hero",
  "requires": { "assets": ["photo|illustration"] },
  "visual_tags": ["split", "asymmetric"],
  "composition": "Two columns: text left (60%), portrait image right (40%)"
}

// Taste Blueprint (taste-skill):
{
  "id": "field-headline-date",
  "name": "Field headline with date",
  "archetype": "field",
  "needs": ["photo"],
  "blueprint": [
    { "tag": "div", "class": "hero-field", "children": [
      { "tag": "h1", "class": "display-1" },
      { "tag": "time", "class": "date-stamp" }
    ]}
  ]
}
```
* Attempting to concatenate these two structures in one JSON array causes `test_library.py` and `atlas_select.py` to crash due to missing required keys (`visual_tags`, `requires.assets`, etc.).

### 3.3 Proposed Unified Composite Schema
Instead of forcing both into one flat file, Atlas-Skill must implement a **Composite Layered Architecture**:
```text
Layer 1: Art Direction Engine (Taste)
  └── Evaluates Sector & Mood → Deals Macro Direction (Idea, Palette Tokens, Typography Pairing).

Layer 2: Composition Selector (Atlas)
  └── Evaluates Context (Category, Goals, Tones, Real Assets) → Selects Section Blueprints.
      (Combines Atlas's 50 Layout Patterns with Taste's 58 Hero & 185 Section Blueprints).
```
To achieve this, the 243 Taste blueprints (`heroes.json` and `sections.json`) will be tagged with Atlas vocabulary (`categories`, `tones`, `density`, `requires`) and validated against an extended `schema.json`.

---

## 4. Runtime & Scripting Language Coexistence

### 4.1 The Python vs Node.js Dilemma
* **Atlas Tools:** Python 3.9+ (`atlas_select.py`, `atlas_check.py`, `atlas_bench.py`).
* **Taste Tools:** Node.js 22+ (`inspect.mjs`, `cdp.mjs`, `draw.mjs`, `assets.mjs`).

### 4.2 Coexistence Strategy: Hybrid CLI Wrapper
Rather than undertaking a risky and error-prone total rewrite:
1. **Python Domain:** Handles deterministic scoring (`atlas_select.py`), static DOM parsing (`atlas_check.py`), schema validation, and benchmark scoring. Runs purely on standard library modules.
2. **Node.js Domain:** Handles Chrome DevTools Protocol browser driving (`inspect.mjs` + `cdp.mjs`) and open-archive network asset downloads (`assets.mjs`). Zero npm packages required.
3. **Unified CLI Facade:** Provide an executable entry point (`atlas` / `atlas.py` or shell wrapper) that transparently invokes the appropriate engine, verifying environment readiness before execution.

---

## 5. Dual-Entry Point Distribution Strategy

To satisfy the user requirement for both multi-agent environments and web chatbots:

```text
atlas-skill/
├── skills/atlas-skill/
│   ├── SKILL.md            # AGENT ENTRY POINT
│   │                       # - Includes CLI command hooks (`py scripts/atlas_select.py`)
│   │                       # - Enforces CDP browser inspection loop & screenshot verification
│   │                       # - Integrates image generator subagent / adapter
│   │
│   └── SKILL.chatbot.md    # CHATBOT ENTRY POINT
│                           # - 100% Standalone Markdown (Zero CLI / Shell dependency)
│                           # - Self-contained decision trees & token recipes
│                           # - Inlined curated palettes (hex codes) and font pairings
│                           # - Inlined section blueprints & CSS snippets
│                           # - Mental self-critique checklist (replaces Playwright/CDP)
```
This guarantees web chatbots (ChatGPT, Claude web, Gemini web) receive a powerful, complete design system without failing on unavailable shell commands.

