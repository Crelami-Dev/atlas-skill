# Atlas-Skill: Architectural Decisions & Confirmed Constraints

**Status:** Confirmed by Project Owner  
**Last Updated:** October 30, 2026  
**Phase:** Phase 0 Completion Baseline  

---

## 1. Confirmed Project Constraints & Owner Decisions

The following foundational decisions and constraints have been formally confirmed by the Project Owner:

### DEC-001: Hybrid CLI Tooling Architecture (Python + Node.js)
* **Decision:** **CONFIRMED (Hybrid Engine).**
* **Technical Boundaries:**
  * **Python 3.9+ (Standard Library):** Drives deterministic context scoring (`atlas_select.py`), static DOM quality gate checks (`atlas_check.py`), composition schema validation, and scientific benchmark scoring (`atlas_bench.py`).
  * **Node.js 22+ (Zero-Dependency):** Drives real-browser inspection over native WebSockets via Chrome DevTools Protocol (`inspect.mjs` + `cdp.mjs`) and handles open-archive imagery fetching (`assets.mjs`).
  * **Unified Wrapper:** An environment-aware launcher (`atlas.py` / `atlas.bat` / `atlas.sh`) transparently resolves host runtime aliases (e.g. `py -3` on Windows) and routes tasks to the appropriate engine.
* **Rationale & Impact:** Eliminates the need to force a risky total rewrite of either toolset. Leverages Taste's zero-dependency CDP browser inspection (which works on any host with Chrome/Edge without installing Playwright) alongside Atlas's standard-library static checkers.

### DEC-002: Dual-Entry Point Distribution Strategy (`SKILL.md` vs `SKILL.chatbot.md`)
* **Decision:** **CONFIRMED (Dual-Flavor Distribution).**
* **File Architecture:**
  1. `skills/atlas-skill/SKILL.md` (Agent Edition): Tailored for tool-using coding agents (Claude Code, OpenAI Codex, Antigravity). Contains CLI command hooks, automated Playwright/CDP screenshot inspection loops, and subagent orchestration.
  2. `skills/atlas-skill/SKILL.chatbot.md` (Chatbot Edition): 100% self-contained prompt document designed for standalone web chatbots (ChatGPT, Claude web, Gemini web, Le Chat). Contains inlined design archetypes, semantic token recipes, curated hex palettes, Google Fonts links, component snippets, and a mental self-critique rubric without terminal or filesystem dependencies.
* **Rationale & Impact:** Completely prevents command execution failures in web chats while preserving automated QA for CLI agents.

### DEC-003: Multi-Tiered Image & Asset Generation Pipeline
* **Decision:** **CONFIRMED (Native-First → Licensed Archive → Semantic CSS/SVG).**
* **Hierarchy:**
  * **Tier 1 (Native-First AI Generation):** If running within an agent that provides native image generation (e.g. Antigravity's `image-generator` subagent) or has a configured image generation API key in the environment, generate bespoke visual assets from visual briefs.
  * **Tier 2 (Licensed Archive Imagery):** If native generation is unavailable, offline, or rejected by QA, invoke `atlas_assets.mjs` to search and download historical, cultural, or documentary photographs under CC0, Public Domain, or CC-BY licenses from Wikimedia Commons, Met Museum, Art Institute of Chicago, and Openverse with automated credit injection.
  * **Tier 3 (Semantic CSS / SVG / Typographic Fallback):** If network access is restricted or no imagery is suitable, fall back safely to type-led compositions, geometric vector motifs, and semantic surface contrast. Never invent fake stock photos or broken URLs.
* **Metadata Tracking:** Every asset is catalogued in `assets/manifest.json` with prompt, provenance, dimensions, license, and crop parameters.

### DEC-004: Language & Documentation Strategy
* **Decision:** **CONFIRMED (English-First Technical Core; Bilingual User Layer).**
* **Execution Rules:**
  * **Technical Core:** System prompts, `SKILL.md`, `SKILL.chatbot.md`, schema definitions, code comments, and CLI outputs are authored in **English**. This guarantees maximum token efficiency, attention accuracy, and multi-agent instruction adherence across frontier LLMs.
  * **User Layer:** User documentation (`README.md`, setup guides, examples) and conversational interactions may be bilingual (English / Indonesian) based on user preference and context. The skill accepts design briefs in any language.

### DEC-005: Implementation Stack Strategy
* **Decision:** **CONFIRMED (Vanilla-First; Strict Stack Respect).**
* **Execution Rules:**
  * **Greenfield Builds:** Default to vanilla-first architecture (semantic HTML5, modern CSS Grid/Flexbox with semantic custom properties, native ES modules). No external npm/bundler dependencies are introduced unless explicitly required by the brief.
  * **Existing Codebases:** When editing or extending an existing project, the skill must first inspect project structure (`package.json`, framework configs) and strictly conform to the existing stack (React, Vue, Svelte, Tailwind, Next.js, etc.) and design system conventions without imposing arbitrary rewrites.

### DEC-006: Layered Composite Design Library Schema
* **Decision:** **CONFIRMED (2-Tier Composite Architecture).**
* **Structure:**
  * **Tier 1 (Macro Art Direction - Taste):** 20 researched art directions dealing visual concept, semantic palette tokens (`palettes.json`), typography pairings (`type.json`), and mood.
  * **Tier 2 (Context-Scored Composition Blueprints - Atlas + Taste):** 243 Taste blueprints (`heroes.json`, `sections.json`) enriched with Atlas metadata tags (`categories`, `tones`, `density`, `requires.assets`, `goals`) alongside Atlas's 50 core structural patterns, scored deterministically via `atlas_select.py`.

### DEC-007: Formal Multi-Agent Role Contracts (`AGENTS.md`)
* **Decision:** **CONFIRMED (5 Sequential / Orchestrated Roles).**
* **Roles:** (1) Lead Orchestrator, (2) Product Analyst, (3) Art Director, (4) Frontend Implementer, (5) QA & Critic.
* **Termination & Guardrails:** QA Critic rejects only on objective **FAIL** findings. Subjective aesthetic issues are treated as **WARN**. A strict maximum limit of **3 revision cycles** is enforced to avoid infinite loops and token thrashing.

### DEC-008: Multi-Platform Manifest Standard
* **Decision:** **CONFIRMED.**
* Maintain native manifests:
  * Claude Code: `.claude-plugin/marketplace.json`
  * OpenAI Codex: `.codex-plugin/plugin.json`
  * Antigravity / Agent Marketplace: `.agents/plugins/marketplace.json`

---

## 2. Status of Previous Questions

All three questions presented at the initial Phase 0 review have been conclusively resolved by the project owner:

| Question | Owner Decision | Resulting Action |
| :--- | :--- | :--- |
| **1. Image Generation Scope** | Native-first, then licensed archive imagery, then CSS/SVG | Formulated as DEC-003 with 3-tier fallback matrix. |
| **2. Language Strategy** | English-first technical core; bilingual user documentation | Formulated as DEC-004. |
| **3. Framework Scope** | Vanilla-first by default; respect existing project stack | Formulated as DEC-005. |

---

## 3. Remaining Blockers & Next Actions

* **Critical Blockers:** **NONE.** All architectural ambiguities, licensing terms, and data schemas have been analyzed and resolved.
* **Non-Blocking Prerequisites for Phase 1 Kickoff:**
  1. Formal user authorization to begin Phase 1 implementation.
  2. Creation of unified library schema validator in Phase 1 before merging JSON files.
