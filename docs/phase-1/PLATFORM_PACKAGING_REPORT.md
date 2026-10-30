# Atlas-Skill: Platform Packaging & Metadata Verification Report

**Report Date:** October 30, 2026  
**Status:** Statically Verified  
**Scope:** Manifests, Directory Layout, Scaffolding  

---

## 1. Package Layout & Entry Points

Phase 1 established the clean, modular layout for the unified skill:

```text
atlas-skill/
├── .agents/plugins/marketplace.json        # Antigravity marketplace manifest
├── .claude-plugin/marketplace.json         # Claude Code plugin manifest
├── .codex-plugin/plugin.json               # OpenAI Codex plugin manifest
├── assets/
│   └── manifest.json                      # Asset priority & provenance manifest
├── data/                                   # 6 Normalized JSON datasets + source-map
├── schemas/                                # Versioned JSON Schema Draft 2020-12
├── skills/
│   └── atlas-skill/
│       ├── SKILL.md                       # Coding Agent entry point scaffold
│       └── SKILL.chatbot.md               # Standalone Chatbot entry point scaffold
├── tools/                                  # Validation and normalization scripts
├── tests/                                  # Integrity and validator test suites
└── docs/                                   # Phase 0 and Phase 1 documentation
```

---

## 2. Multi-Platform Manifest Status

In accordance with strict reporting standards, manifest compatibility is divided into **statically verified** vs **unverified runtime execution**:

| Platform Target | Manifest File | Syntax & Schema Status | Runtime Installation Status | Notes & Limitations |
| :--- | :--- | :---: | :---: | :--- |
| **Claude Code** | `.claude-plugin/marketplace.json` | **VERIFIED** | **UNVERIFIED** | JSON valid. Defines plugin name `atlas-skill`, version `1.0.0`, skills path `./skills/atlas-skill`. Live install command (`/plugin install`) not executed in Phase 1. |
| **OpenAI Codex** | `.codex-plugin/plugin.json` | **VERIFIED** | **UNVERIFIED** | JSON valid. Defines display name `Atlas Skill`, category `Design`, default prompts, and skill directory `./skills/`. Live Codex extension load not executed in Phase 1. |
| **Antigravity** | `.agents/plugins/marketplace.json` | **VERIFIED** | **UNVERIFIED** | JSON valid. Conforms to local source plugin spec (`"source": "local"`). Runtime discovery verified structurally, live plugin registration deferred to Phase 2. |

---

## 3. Dual-Entry Distribution Architecture

To implement DEC-002, two entry points are established under `skills/atlas-skill/`:

### 3.1 `skills/atlas-skill/SKILL.md` (Agent Edition)
* **Target:** AI coding agents with terminal and tool execution (Claude Code, Codex, Antigravity).
* **Role:** Declares skill frontmatter (`name: atlas-skill`, `description: ...`), links to data models, specifies the hybrid runtime, and prepares for Phase 2 CLI tool hooks and browser CDP verification loops.

### 3.2 `skills/atlas-skill/SKILL.chatbot.md` (Chatbot Edition)
* **Target:** Web chatbots (ChatGPT, Claude web, Gemini web, Le Chat).
* **Role:** Standalone document requiring zero terminal or filesystem access. Declares frontmatter (`name: atlas-skill-chatbot`), establishing the architecture for inlined cheatsheets, color palettes, and mental self-critique rubrics.

---

## 4. Asset Manifest (`assets/manifest.json`)
Implements DEC-003 asset priority tiers:
1. `tier_1_native`: Native AI generation via host agent / API.
2. `tier_2_archive`: Licensed open museum imagery via `atlas_assets.mjs`.
3. `tier_3_fallback`: Semantic CSS/SVG vector graphics and type-led fallback.
All future generated or downloaded assets will be registered with dimensions, license, and crop parameters.

