# Atlas-Skill: Composite Schema Design & Contract Specification

**Schema Version:** 2.0.0  
**Specification File:** `atlas-skill/schemas/composite-library.schema.json`  
**Standard:** JSON Schema Draft 2020-12 Vocabulary (Validated via Custom Offline Python Standard-Library Tooling)  

---

## 1. Architectural Rationale: 2-Tier Design Model

In Phase 0, audit evidence proved that Taste-Skill and Atlas cannot be flattened into a single table without destructive data loss. 
* **Taste-Skill** models *aesthetic direction* (concepts, color tokens, font scales, DOM blueprints).
* **Atlas-Frontend-Design** models *layout composition slots* (content requirements, density, category scoring, responsive rules).

To preserve the strengths of both without schema collisions, Atlas-Skill establishes a **2-Tier Layered Architecture**:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   TIER 1: ART DIRECTION LAYER                         │
│  (Directions, Semantic Palettes, Typography Systems, Reference Sites) │
│                                                                        │
│  • Evaluates business sector, brand tone, and aesthetic mood           │
│  • Deals visual thesis, core concept, color tokens, and font pairing   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ informs tokens & constraints
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│               TIER 2: COMPOSITION & BLUEPRINT LAYER                    │
│      (Atlas Layout Patterns + Taste Hero & Section Blueprints)         │
│                                                                        │
│  • Evaluates context (available assets, page density, conversion goal) │
│  • Selects layout patterns and concrete DOM element structures        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Universal Schema Contract

Every dataset file in `atlas-skill/data/` adheres to the root container contract:

```json
{
  "version": "2.0.0",
  "schema_type": "art_directions | compositions | palettes | typography | sites | app_shells",
  "item_count": 293, // Exact record count in this specific file (len(items)). Global total (620) is aggregated across files.
  "items": [ /* array of normalized records */ ]
}
```

### 2.1 Universal Base Fields (Required on ALL Records)
Every normalized record regardless of layer must implement:

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `string` | Unique, namespaced, stable identifier matching regex `^[a-z0-9_:-]+$`. |
| `layer` | `string` | Layer enum: `art_direction`, `composition`, `palette`, `typography`, `site`, `app_shell`. |
| `name` | `string` | Human-readable title or label (non-empty). |
| `provenance` | `object` | Mandatory source traceability metadata with required attribution (see Section 3). |

---

## 3. Mandatory Provenance Contract

To satisfy licensing and attribution requirements, every record must supply complete, non-empty provenance metadata. Missing or whitespace-only attribution is rejected with a hard validation error:

```json
"provenance": {
  "source_project": "taste-skill | atlas-frontend-design | project-atlas-v0.2.0-alpha",
  "source_file": "relative/path/to/source.json",
  "source_id": "original_source_id",
  "license": "MIT (Leonxlnx) | MIT (Project ATLAS contributors)",
  "attribution": "Mandatory non-empty attribution, copyright, or provenance statement"
}
```

---

## 4. Layer Specifications

### 4.1 Layer: `art_direction` (`art-directions.json`)
Represents high-level art directions derived from the 247 gallery study.
* **Fields:** `sectors` (list), `tones` (list), `needs` (list), `idea` (string), `composition` (string), `typography` (string), `type_classes` (list), `colour` (string), `palette_tags` (list), `imagery` (string), `section_tags` (list), `motion` (string), `richness` (string), `pitfalls` (string), `seen_in` (list of URLs), `allow` (rule exemptions).

### 4.2 Layer: `composition` (`compositions.json`)
Unifies structural patterns and DOM blueprints. Contains 293 records across three source datasets:
* **From Atlas (50 patterns):** Provides layout rules, content requirements, goals, density, and responsive behaviors. `blueprint` is `null`.
* **From Taste Heroes (58 blueprints):** Provides archetype, headline specs, mobile behavior, and detailed `blueprint` DOM node arrays.
* **From Taste Sections (185 blueprints):** Provides section role (`hero`, `showcase`, `features`, `pricing`, `faq`, `cta`, `footer`), shape tag, and `blueprint` DOM node arrays.
* **Fields:** `family` (string), `intent` (string), `page_types` (list: `marketing`, `editorial`, `app`), `categories` (list), `tones` (list), `density` (enum: `low`, `med`, `high`, `null`), `requires` (`{ "assets": [...] }`), `goals` (list), `visual_tags` (list), `composition` (string), `blueprint` (array of DOM nodes or null), `responsive` (string), `motion` (string/null), `accessibility` (string), `avoid_when` (list), `related` (list of IDs), `incompatible` (list of IDs), `seen_in` (list).

### 4.3 Layer: `palette` (`palettes.json`)
Semantic color token recipes (56 records).
* **Fields:** `tags` (list), `bg`, `surface`, `ink`, `muted`, `accent`, `accent_ink`, `fields` (list), `note` (string), `seen_in` (list).

### 4.4 Layer: `typography` (`typography.json`)
Pairings, scale multipliers, and font links (44 records).
* **Fields:** `type_class`, `display` (object), `text` (object), `stands_in_for` (list), `note`, `seen_in`, `links` (Google Font URLs), `scale` (multipliers).

### 4.5 Layer: `site` (`sites.json`)
Empirical teardowns of award-winning websites (202 records).
* **Fields:** `url`, `source`, `kind`, `score`, `idea`, `mood`, `archetype`, `hero`, `type`, `colour`, `imagery`, `layout`, `sections`, `steal`, `media`, `motion`.

### 4.6 Layer: `app_shell` (`app-shells.json`)
Application layout shells and metadata (5 records).
* **Fields:** `family`, `suits` (list), `numbers` (specs), `blueprint` (description), `phone` (mobile folding rules).

---

## 5. Stable ID Namespacing Strategy

To guarantee that IDs remain unique and collisions are mathematically impossible:

| Dataset | Source ID | Normalized ID Pattern | Example |
| :--- | :--- | :--- | :--- |
| **Art Directions** | `colour-chapters` | `art-dir:{source_id}` | `art-dir:colour-chapters` |
| **Atlas Patterns** | `nav-minimal-bar` | `atlas:{source_id}` | `atlas:nav-minimal-bar` |
| **Taste Heroes** | `field-headline-date` | `taste:hero:{source_id}` | `taste:hero:field-headline-date` |
| **Taste Sections** | `archive-dates` | `taste:section:{source_id}` | `taste:section:archive-dates` |
| **Palettes** | `slate-ember` | `palette:{source_id}` | `palette:slate-ember` |
| **Typography** | `grotesk-mono` | `type:{source_id}` | `type:grotesk-mono` |
| **Sites** | `w-and-co` | `site:{source_id}` | `site:w-and-co` |
| **App Shells** | `open-plane` | `app:shell:{source_id}` | `app:shell:open-plane` |

---

## 6. Deprecation and Evolution Policy
* **Additive Changes:** New fields or layers may be added in minor versions (e.g. 2.1.0) without breaking consumers.
* **No Inferred Truth:** When a source dataset lacks a property (e.g. Taste sections have no pre-assigned `density`), the property is set to an explicit default (`med` or `null`) rather than inventing arbitrary tags.

