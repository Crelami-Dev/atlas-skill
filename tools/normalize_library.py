#!/usr/bin/env python3
"""Atlas Design Library Normalization Pipeline.

Deterministically transforms source datasets from taste-skill and atlas-frontend-design
into the unified composite library format adhering to composite-library.schema.json.

Safety:
- Source repositories are strictly READ-ONLY.
- All output is written to atlas-skill/data/.
- Generates source-to-output mapping for complete auditability.

Usage:
  py tools/normalize_library.py --sample
  py tools/normalize_library.py --dry-run
  py tools/normalize_library.py
"""
import argparse
import json
import os
import sys

# Paths
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, ".."))
WORKSPACE_ROOT = os.path.abspath(os.path.join(PROJECT_ROOT, ".."))

TASTE_LIB = os.path.join(WORKSPACE_ROOT, "taste-skill", "skills", "taste-skill", "library")
ATLAS_LIB = os.path.join(WORKSPACE_ROOT, "atlas-frontend-design", "compositions", "library.json")
OUTPUT_DATA_DIR = os.path.join(PROJECT_ROOT, "data")
OUTPUT_DOCS_DIR = os.path.join(PROJECT_ROOT, "docs", "phase-1")


def verify_source_boundaries():
    """Confirms that source paths exist and are outside target project directory."""
    assert os.path.isdir(TASTE_LIB), f"Taste library not found: {TASTE_LIB}"
    assert os.path.isfile(ATLAS_LIB), f"Atlas library not found: {ATLAS_LIB}"
    assert not TASTE_LIB.startswith(PROJECT_ROOT), "Taste source must not be inside target directory"
    assert not ATLAS_LIB.startswith(PROJECT_ROOT), "Atlas source must not be inside target directory"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def normalize_art_directions(sample_limit=None):
    source_file = os.path.join(TASTE_LIB, "directions.json")
    raw_data = load_json(source_file)
    items = raw_data[:sample_limit] if sample_limit else raw_data

    normalized = []
    source_map = []
    for item in items:
        norm_id = f"art-dir:{item['id']}"
        record = {
            "id": norm_id,
            "layer": "art_direction",
            "name": item.get("name", item["id"]),
            "sectors": item.get("sectors", []),
            "tones": item.get("tones", []),
            "needs": item.get("needs", []),
            "idea": item.get("idea", ""),
            "composition": item.get("composition", ""),
            "typography": item.get("typography", ""),
            "type_classes": item.get("typeClasses", []),
            "colour": item.get("colour", ""),
            "palette_tags": item.get("paletteTags", []),
            "imagery": item.get("imagery", ""),
            "section_tags": item.get("sectionTags", []),
            "motion": item.get("motion", ""),
            "richness": item.get("richness", ""),
            "pitfalls": item.get("pitfalls", ""),
            "seen_in": item.get("seenIn", []),
            "allow": item.get("allow", []),
            "provenance": {
                "source_project": "taste-skill",
                "source_file": "skills/taste-skill/library/directions.json",
                "source_id": item["id"],
                "license": "MIT (Leonxlnx)",
                "attribution": "Curated from 247 gallery websites study (Leonxlnx/taste-skill)"
            }
        }
        normalized.append(record)
        source_map.append({
            "normalized_id": norm_id,
            "layer": "art_direction",
            "source_project": "taste-skill",
            "source_file": "library/directions.json",
            "source_id": item["id"],
            "target_dataset": "art-directions.json"
        })

    container = {
        "version": "2.0.0",
        "schema_type": "art_directions",
        "item_count": len(normalized),
        "items": normalized
    }
    return container, source_map


def normalize_compositions(sample_limit=None):
    normalized = []
    source_map = []

    # 1. Atlas patterns (50 items)
    atlas_data = load_json(ATLAS_LIB).get("patterns", [])
    atlas_items = atlas_data[:sample_limit] if sample_limit else atlas_data
    for p in atlas_items:
        norm_id = f"atlas:{p['id']}"
        record = {
            "id": norm_id,
            "layer": "composition",
            "family": p.get("family", "section"),
            "name": p.get("name", p["id"]),
            "intent": p.get("intent", ""),
            "page_types": p.get("page_types", ["marketing"]),
            "categories": p.get("categories", ["*"]),
            "tones": p.get("tones", []),
            "density": p.get("density", "med"),
            "requires": p.get("requires", {"assets": []}),
            "goals": p.get("goals", []),
            "visual_tags": p.get("visual_tags", []),
            "composition": p.get("composition", ""),
            "blueprint": None,
            "responsive": p.get("responsive", ""),
            "motion": p.get("motion", ""),
            "accessibility": p.get("accessibility", ""),
            "avoid_when": p.get("avoid_when", []),
            "related": [f"atlas:{x}" for x in p.get("related", [])],
            "incompatible": [f"atlas:{x}" for x in p.get("incompatible", [])],
            "provenance": {
                "source_project": "atlas-frontend-design",
                "source_file": "compositions/library.json",
                "source_id": p["id"],
                "license": "MIT (Project ATLAS contributors)",
                "attribution": "ATLAS frontend design pattern library v1.0.0"
            }
        }
        normalized.append(record)
        source_map.append({
            "normalized_id": norm_id,
            "layer": "composition",
            "source_project": "atlas-frontend-design",
            "source_file": "compositions/library.json",
            "source_id": p["id"],
            "target_dataset": "compositions.json"
        })

    # 2. Taste heroes (58 items)
    heroes_file = os.path.join(TASTE_LIB, "heroes.json")
    heroes_data = load_json(heroes_file)
    heroes_items = heroes_data[:sample_limit] if sample_limit else heroes_data
    for h in heroes_items:
        norm_id = f"taste:hero:{h['id']}"
        record = {
            "id": norm_id,
            "layer": "composition",
            "family": "hero",
            "name": h.get("name", h["id"]),
            "intent": f"Hero archetype: {h.get('archetype', 'hero')}",
            "page_types": ["marketing", "editorial"],
            "categories": h.get("directions", ["*"]),
            "tones": [],
            "density": "med",
            "requires": {"assets": h.get("needs", [])},
            "goals": ["engage", "introduce"],
            "visual_tags": [h.get("archetype", "hero"), "taste-hero"],
            "composition": f"Headline: {h.get('headline', '')}. Mobile: {h.get('mobile', '')}",
            "blueprint": h.get("blueprint", []),
            "responsive": h.get("mobile", ""),
            "motion": h.get("motion", ""),
            "accessibility": "Semantic HTML structure with clear heading hierarchy",
            "avoid_when": [],
            "seen_in": h.get("seenIn", []),
            "provenance": {
                "source_project": "taste-skill",
                "source_file": "skills/taste-skill/library/heroes.json",
                "source_id": h["id"],
                "license": "MIT (Leonxlnx)",
                "attribution": "Taste v2 hero blueprint (Leonxlnx/taste-skill)"
            }
        }
        normalized.append(record)
        source_map.append({
            "normalized_id": norm_id,
            "layer": "composition",
            "source_project": "taste-skill",
            "source_file": "library/heroes.json",
            "source_id": h["id"],
            "target_dataset": "compositions.json"
        })

    # 3. Taste sections (185 items)
    sections_file = os.path.join(TASTE_LIB, "sections.json")
    sections_data = load_json(sections_file)
    sections_items = sections_data[:sample_limit] if sample_limit else sections_data
    for s in sections_items:
        norm_id = f"taste:section:{s['id']}"
        role = s.get("role", "section")
        record = {
            "id": norm_id,
            "layer": "composition",
            "family": role,
            "name": s.get("name", s["id"]),
            "intent": f"Section role: {role}",
            "page_types": ["marketing", "editorial"],
            "categories": s.get("directions", ["*"]),
            "tones": [],
            "density": "med",
            "requires": {"assets": s.get("needs", [])},
            "goals": [role],
            "visual_tags": s.get("tags", []) + [s.get("shape", "section")],
            "composition": f"Shape: {s.get('shape', '')}. Mobile: {s.get('mobile', '')}",
            "blueprint": s.get("blueprint", []),
            "responsive": s.get("mobile", ""),
            "motion": None,
            "accessibility": "Ensure landmark container and accessible hierarchy",
            "avoid_when": [],
            "seen_in": s.get("seenIn", []),
            "provenance": {
                "source_project": "taste-skill",
                "source_file": "skills/taste-skill/library/sections.json",
                "source_id": s["id"],
                "license": "MIT (Leonxlnx)",
                "attribution": "Taste v2 section blueprint (Leonxlnx/taste-skill)"
            }
        }
        normalized.append(record)
        source_map.append({
            "normalized_id": norm_id,
            "layer": "composition",
            "source_project": "taste-skill",
            "source_file": "library/sections.json",
            "source_id": s["id"],
            "target_dataset": "compositions.json"
        })

    container = {
        "version": "2.0.0",
        "schema_type": "compositions",
        "item_count": len(normalized),
        "items": normalized
    }
    return container, source_map


def normalize_palettes(sample_limit=None):
    source_file = os.path.join(TASTE_LIB, "palettes.json")
    raw_data = load_json(source_file)
    items = raw_data[:sample_limit] if sample_limit else raw_data

    normalized = []
    source_map = []
    for item in items:
        norm_id = f"palette:{item['id']}"
        record = {
            "id": norm_id,
            "layer": "palette",
            "name": item.get("name", item["id"]),
            "tags": item.get("tags", []),
            "bg": item.get("bg", ""),
            "surface": item.get("surface", ""),
            "ink": item.get("ink", ""),
            "muted": item.get("muted", ""),
            "accent": item.get("accent", ""),
            "accent_ink": item.get("accentInk", ""),
            "fields": item.get("fields", []),
            "note": item.get("note", ""),
            "seen_in": item.get("seenIn", []),
            "provenance": {
                "source_project": "taste-skill",
                "source_file": "skills/taste-skill/library/palettes.json",
                "source_id": item["id"],
                "license": "MIT (Leonxlnx)",
                "attribution": "Curated palette tokens (Leonxlnx/taste-skill)"
            }
        }
        normalized.append(record)
        source_map.append({
            "normalized_id": norm_id,
            "layer": "palette",
            "source_project": "taste-skill",
            "source_file": "library/palettes.json",
            "source_id": item["id"],
            "target_dataset": "palettes.json"
        })

    container = {
        "version": "2.0.0",
        "schema_type": "palettes",
        "item_count": len(normalized),
        "items": normalized
    }
    return container, source_map


def normalize_typography(sample_limit=None):
    source_file = os.path.join(TASTE_LIB, "type.json")
    raw_data = load_json(source_file)
    items = raw_data[:sample_limit] if sample_limit else raw_data

    normalized = []
    source_map = []
    for item in items:
        norm_id = f"type:{item['id']}"
        record = {
            "id": norm_id,
            "layer": "typography",
            "name": item.get("name", item["id"]),
            "type_class": item.get("class", ""),
            "display": item.get("display", {}),
            "text": item.get("text", {}),
            "stands_in_for": item.get("standsInFor", []),
            "note": item.get("note", ""),
            "seen_in": item.get("seenIn", []),
            "links": item.get("links", []),
            "scale": item.get("scale", {}),
            "provenance": {
                "source_project": "taste-skill",
                "source_file": "skills/taste-skill/library/type.json",
                "source_id": item["id"],
                "license": "MIT (Leonxlnx)",
                "attribution": "Typography pairings and scale multipliers (Leonxlnx/taste-skill)"
            }
        }
        normalized.append(record)
        source_map.append({
            "normalized_id": norm_id,
            "layer": "typography",
            "source_project": "taste-skill",
            "source_file": "library/type.json",
            "source_id": item["id"],
            "target_dataset": "typography.json"
        })

    container = {
        "version": "2.0.0",
        "schema_type": "typography",
        "item_count": len(normalized),
        "items": normalized
    }
    return container, source_map


def normalize_sites(sample_limit=None):
    source_file = os.path.join(TASTE_LIB, "sites.json")
    raw_data = load_json(source_file)
    items = raw_data[:sample_limit] if sample_limit else raw_data

    normalized = []
    source_map = []
    for item in items:
        norm_id = f"site:{item['id']}"
        record = {
            "id": norm_id,
            "layer": "site",
            "name": item.get("name", item["id"]),
            "url": item.get("url", ""),
            "source": item.get("source", ""),
            "kind": item.get("kind", ""),
            "score": item.get("score", 0),
            "idea": item.get("idea", ""),
            "mood": item.get("mood", ""),
            "archetype": item.get("archetype", ""),
            "hero": item.get("hero", ""),
            "type": item.get("type", ""),
            "colour": item.get("colour", ""),
            "imagery": item.get("imagery", ""),
            "layout": item.get("layout", ""),
            "sections": item.get("sections", []),
            "steal": item.get("steal", ""),
            "media": item.get("media", {}),
            "motion": item.get("motion", ""),
            "provenance": {
                "source_project": "taste-skill",
                "source_file": "skills/taste-skill/library/sites.json",
                "source_id": item["id"],
                "license": "MIT (Leonxlnx)",
                "attribution": "Studied reference site teardown (Leonxlnx/taste-skill)"
            }
        }
        normalized.append(record)
        source_map.append({
            "normalized_id": norm_id,
            "layer": "site",
            "source_project": "taste-skill",
            "source_file": "library/sites.json",
            "source_id": item["id"],
            "target_dataset": "sites.json"
        })

    container = {
        "version": "2.0.0",
        "schema_type": "sites",
        "item_count": len(normalized),
        "items": normalized
    }
    return container, source_map


def normalize_app_shells(sample_limit=None):
    source_file = os.path.join(TASTE_LIB, "app.json")
    raw_data = load_json(source_file)

    normalized_items = []
    source_map = []

    # Map app shells from list
    shells = raw_data.get("shells", [])
    if isinstance(shells, list):
        shell_items = shells[:sample_limit] if sample_limit else shells
        for item in shell_items:
            norm_id = f"app:shell:{item['id']}"
            record = {
                "id": norm_id,
                "layer": "app_shell",
                "name": item.get("name", item["id"]),
                "family": "app_shell",
                "suits": item.get("suits", []),
                "numbers": item.get("numbers", {}),
                "blueprint": item.get("blueprint", ""),
                "phone": item.get("phone", ""),
                "provenance": {
                    "source_project": "taste-skill",
                    "source_file": "skills/taste-skill/library/app.json",
                    "source_id": item["id"],
                    "license": "MIT (Leonxlnx)",
                    "attribution": "App shell architecture from taste-skill v2"
                }
            }
            normalized_items.append(record)
            source_map.append({
                "normalized_id": norm_id,
                "layer": "app_shell",
                "source_project": "taste-skill",
                "source_file": "library/app.json",
                "source_id": item["id"],
                "target_dataset": "app-shells.json"
            })

    container = {
        "version": "2.0.0",
        "schema_type": "app_shells",
        "item_count": len(normalized_items),
        "items": normalized_items,
        "metadata": {
            "version": str(raw_data.get("version", "1.0.0")),
            "styles": raw_data.get("styles", []),
            "kinds": raw_data.get("kinds", {}),
            "patterns": raw_data.get("patterns", [])
        }
    }
    return container, source_map


def main():
    parser = argparse.ArgumentParser(description="Normalize design libraries into Atlas composite schema.")
    parser.add_argument("--sample", action="store_true", help="Run on a small sample (3 items per source) for inspection")
    parser.add_argument("--dry-run", action="store_true", help="Preview normalization counts without saving files")
    args = parser.parse_args()

    verify_source_boundaries()
    sample_limit = 3 if args.sample else None

    print("=== Atlas Library Normalization Pipeline ===")
    if args.sample:
        print("Mode: SAMPLE RUN (3 items per source dataset)")
    elif args.dry_run:
        print("Mode: DRY RUN (No files will be written)")
    else:
        print("Mode: FULL MIGRATION RUN")

    total_source_map = []

    # 1. Art Directions
    art_dirs, sm_art = normalize_art_directions(sample_limit)
    total_source_map.extend(sm_art)
    print(f"  Art Directions : {art_dirs['item_count']} items")

    # 2. Compositions
    compositions, sm_comp = normalize_compositions(sample_limit)
    total_source_map.extend(sm_comp)
    print(f"  Compositions   : {compositions['item_count']} items (Atlas patterns + Taste heroes & sections)")

    # 3. Palettes
    palettes, sm_pal = normalize_palettes(sample_limit)
    total_source_map.extend(sm_pal)
    print(f"  Palettes       : {palettes['item_count']} items")

    # 4. Typography
    typography, sm_typ = normalize_typography(sample_limit)
    total_source_map.extend(sm_typ)
    print(f"  Typography     : {typography['item_count']} items")

    # 5. Sites
    sites, sm_site = normalize_sites(sample_limit)
    total_source_map.extend(sm_site)
    print(f"  Sites          : {sites['item_count']} items")

    # 6. App Shells
    app_shells, sm_app = normalize_app_shells(sample_limit)
    total_source_map.extend(sm_app)
    print(f"  App Shells     : {app_shells['item_count']} items")

    print(f"Total Source Map Entries: {len(total_source_map)}")

    if not args.dry_run:
        os.makedirs(OUTPUT_DATA_DIR, exist_ok=True)
        save_json(os.path.join(OUTPUT_DATA_DIR, "art-directions.json"), art_dirs)
        save_json(os.path.join(OUTPUT_DATA_DIR, "compositions.json"), compositions)
        save_json(os.path.join(OUTPUT_DATA_DIR, "palettes.json"), palettes)
        save_json(os.path.join(OUTPUT_DATA_DIR, "typography.json"), typography)
        save_json(os.path.join(OUTPUT_DATA_DIR, "sites.json"), sites)
        save_json(os.path.join(OUTPUT_DATA_DIR, "app-shells.json"), app_shells)
        save_json(os.path.join(OUTPUT_DATA_DIR, "source-map.json"), total_source_map)
        print(f"\n[OK] Generated dataset files written to: {OUTPUT_DATA_DIR}")
    else:
        print("\n[DRY RUN] No files written.")


if __name__ == "__main__":
    main()
