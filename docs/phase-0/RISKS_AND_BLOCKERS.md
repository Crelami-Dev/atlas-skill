# Atlas-Skill: Risk Register & Blocker Analysis

**Status:** Active  
**Last Updated:** October 30, 2026  

---

## 1. Itemized Risk Register

| Risk ID | Title | Severity | Impact | Blocks Phase 1? |
| :--- | :--- | :---: | :--- | :---: |
| **RSK-001** | Windows Python Aliases and PATH Ambiguity | **HIGH** | CLI scripts fail when invoked via `python` or `python3` on Windows hosts. | **NO** (Mitigated) |
| **RSK-002** | Incompatible Data Schemas (Taste vs Atlas) | **CRITICAL** | Naive JSON merge corrupts pattern validation and crashes `atlas_select.py`. | **NO** (Architecture Defined) |
| **RSK-003** | Missing Python Playwright & Pillow Packages | **MEDIUM** | Python-based screenshot capture (`atlas_shoot.py`) skips execution. | **NO** (Mitigated by CDP) |
| **RSK-004** | Outbound Network Latency on Open Archives | **MEDIUM** | `assets.mjs` hangs or times out in restricted/firewalled sandboxes. | **NO** (Fallback Designed) |
| **RSK-005** | Image Generation Tooling Fragmentation | **HIGH** | Inconsistent AI image capabilities across Claude, Codex, Antigravity, and Chatbots. | **NO** (Adapter Required) |
| **RSK-006** | Token Context Window Bloat in `SKILL.chatbot.md` | **HIGH** | Inlining too much library data exceeds context limits in standard chat models. | **NO** (Design Specified) |
| **RSK-007** | Broken `frontmatter.mjs` Test in Taste-Skill | **LOW** | Node test fails on missing third-party `yaml` package. | **NO** (Non-runtime) |
| **RSK-008** | Multi-Agent Endless Revision Thrashing | **MEDIUM** | QA Critic rejects code repeatedly over subjective styling preferences. | **NO** (Loop Rules Defined) |

---

## 2. Detailed Risk Profiles

### RSK-001: Windows Python Aliases and PATH Ambiguity
* **Severity:** **HIGH**
* **Evidence:** Executing `python -c ...` on this host returned exit code 1 (`Python was not found; run without arguments to install from the Microsoft Store`). Only `py` launcher succeeded.
* **Impact:** Cross-platform scripts that hardcode `python3` or `python` fail out of the box on standard Windows environments.
* **Proposed Mitigation:** The unified CLI wrapper and test runners will use dynamic executable detection (`py -3` on Windows, `python3` on POSIX) or provide explicit launcher scripts (`atlas.bat` and `atlas.sh`).
* **Blocks Phase 1:** **NO.** Solution is fully understood and verified.

---

### RSK-002: Incompatible Data Schemas (Taste vs Atlas)
* **Severity:** **CRITICAL**
* **Evidence:** `atlas-frontend-design/compositions/library.json` uses a single dictionary with 18 mandatory fields per pattern. `taste-skill/skills/taste-skill/library/` uses 9 distinct JSON files with completely different models (`heroes.json` has `blueprint` DOM trees; `palettes.json` has hex roles).
* **Impact:** If merged without an explicit translation schema, pattern selection breaks, and test suites will fail.
* **Proposed Mitigation:** Implement a two-layer composite schema in Phase 1: macro art direction (Taste) seeds semantic design tokens, while section blueprints are enriched with Atlas taxonomy tags (`tones`, `requires.assets`, `density`) to allow unified scoring in `atlas_select.py`.
* **Blocks Phase 1:** **NO.** Architecture is defined in `INTEGRATION_ASSESSMENT.md`.

---

### RSK-003: Missing Python Playwright & Pillow Packages
* **Severity:** **MEDIUM**
* **Evidence:** `test_check.py` reported: `test_detects_horizontal_overflow_on_mobile (test_check.BrowserTests) ... skipped 'playwright not available'`.
* **Impact:** Python-based screenshot generation (`atlas_shoot.py`) and visual diff calculation (`atlas_compare.py`) cannot run without external package installation.
* **Proposed Mitigation:** Leverage Taste-Skill's zero-dependency CDP inspector (`inspect.mjs` + `cdp.mjs`). CDP drives the host's existing Chrome or Edge browser directly over native WebSockets, providing fold and full-page screenshots without installing `pip` or `npm` packages.
* **Blocks Phase 1:** **NO.** Verified working via `.taste-skill/inspect/report.json`.

---

### RSK-004: Outbound Network Latency on Open Archives
* **Severity:** **MEDIUM**
* **Evidence:** `node assets.mjs "machinery" --limit 2` timed out in this background task execution when attempting external HTTPS calls to open museum APIs.
* **Impact:** Offline workflows, sandboxed environments, or restricted network proxies cannot fetch live imagery during the design run.
* **Proposed Mitigation:** Implement a 3-tier fallback matrix: (1) Outbound archive search with short (5s) timeout, (2) Local cached photo collections (`library/photos.json`), (3) Fallback to semantic typographic hero or vector brand geometry with zero network requests.
* **Blocks Phase 1:** **NO.** Fallback behavior is specified.

---

### RSK-005: Image Generation Tooling Fragmentation
* **Severity:** **HIGH**
* **Evidence:** Antigravity provides an `image-generator` subagent; Claude Code and Codex rely on custom tools or MCP servers; Web Chatbots have no tool execution capability.
* **Impact:** Hardcoding a single image generation mechanism will break compatibility on other platforms.
* **Proposed Mitigation:** Design an `atlas_image_pipeline` adapter module:
  * In Antigravity: Routes visual briefs to the `image-generator` subagent.
  * In CLI environments with API keys: Calls configurable image generation endpoints (Imagen / DALL-E).
  * In Chatbots / Offline: Emits an exact visual prompt and placeholder tag (`<!-- GANTI: image prompt="..." -->`) for manual user generation.
* **Blocks Phase 1:** **NO.** Adapter pattern resolves cross-platform divergence.

---

### RSK-006: Token Context Window Bloat in `SKILL.chatbot.md`
* **Severity:** **HIGH**
* **Evidence:** The raw source JSON libraries across both projects exceed 1.8 MB. Inlining this into a chatbot prompt would consume over 450,000 tokens, exceeding model context limits and degrading reasoning.
* **Impact:** Chatbots would either reject the prompt or hallucinate due to attention degradation.
* **Proposed Mitigation:** For `SKILL.chatbot.md`, distill the database into a curated reference cheatsheet:
  * 6 Core Archetypes (instead of 20 raw JSON entries).
  * 12 Curated Palettes with direct hex codes (covering dark, warm, minimal, bold, institutional).
  * 8 Proven Typography Pairings with Google Fonts import URLs.
  * 10 Most Versatile Section Blueprints written as concise HTML/CSS snippets.
* **Blocks Phase 1:** **NO.** Distillation criteria established.

---

### RSK-007: Broken `frontmatter.mjs` Test in Taste-Skill
* **Severity:** **LOW**
* **Evidence:** `node taste-skill\tests\frontmatter.mjs` failed with `This check needs the "yaml" package: npm install --no-save --no-package-lock yaml@2.6.1`.
* **Impact:** Taste-skill CI test fails in an environment without npm packages installed.
* **Proposed Mitigation:** In Atlas-Skill, replace the external `yaml` dependency with a standard regex/frontmatter parser in Python (`test_skill_format.py`), which already passed 100% using standard library modules.
* **Blocks Phase 1:** **NO.** Clean Python replacement is verified.

---

### RSK-008: Multi-Agent Endless Revision Thrashing
* **Severity:** **MEDIUM**
* **Evidence:** In multi-agent configurations, subjective aesthetic disagreements between the Art Director and QA Critic can trigger recursive edit loops.
* **Impact:** Token exhaustion and failure to deliver final code.
* **Proposed Mitigation:** Enforce a strict protocol in `AGENTS.md`:
  * QA Critic can only trigger a hard rejection for objective **FAIL** criteria (broken layout, missing alt, overflow, contrast failure, non-functional buttons).
  * Subjective aesthetic issues are logged as **WARN**.
  * A hard limit of **maximum 3 revision rounds** is enforced. If warnings remain after round 3, the project must be delivered with documented trade-offs.
* **Blocks Phase 1:** **NO.** Protocol formalized.

