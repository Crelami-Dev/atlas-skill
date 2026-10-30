#!/usr/bin/env python3
"""Atlas Runtime Engine — Composition Engine.

Harmonizes Macro Art Direction, Slot-by-Slot Compositions, Semantic Palettes,
Typography Systems, and Application Shells into an explainable, deterministic DesignPlan.
Zero-dependency, Python 3.9+ standard library.
"""
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Dict, List, Optional, Tuple

from .assets import AssetRequirement, AssetResolver
from .contracts import (
    ERR_HARD_CONSTRAINT_UNSATISFIED,
    LIBRARY_VERSION,
    RUNTIME_VERSION,
    WARN_LOW_FIT_SCORE,
    WARN_UNRESOLVED_SLOT,
    ContractValidationError,
    Diagnostic,
    ProductBrief,
    compute_plan_id,
)
from .loader import CanonicalLibrary
from .motion_adapter import plan_motion_for_brief
from .retriever import retrieve_candidates_for_slot, retrieve_design_references
from .scorer import (
    score_app_shell,
    score_art_direction,
    score_composition,
    score_palette,
    score_typography,
)


def to_serializable(obj: Any) -> Any:
    """Recursively convert MappingProxyType to dict, and tuple/set to list for JSON serialization."""
    if isinstance(obj, (dict, MappingProxyType)):
        return {k: to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [to_serializable(v) for v in obj]
    elif isinstance(obj, (set, frozenset)):
        return [to_serializable(v) for v in sorted(obj)]
    return obj


def compose_design_plan(
    brief: ProductBrief,
    library: CanonicalLibrary,
    asset_resolver: Optional[AssetResolver] = None,
    diagnostics: Optional[List[Diagnostic]] = None,
    deterministic_timestamp: Optional[str] = None
) -> Dict[str, Any]:
    """Generate a fully coherent, explainable DesignPlan from a ProductBrief.
    
    Args:
        brief: Normalized ProductBrief.
        library: Loaded CanonicalLibrary.
        asset_resolver: AssetResolver instance (defaults to offline 3-tier resolver).
        diagnostics: Optional list to collect diagnostics.
        deterministic_timestamp: Optional fixed timestamp for reproducible testing.
        
    Returns:
        Dict representing the complete machine-readable DesignPlan.
    """
    if diagnostics is None:
        diagnostics = []

    resolver = asset_resolver or AssetResolver()
    warnings: List[str] = []

    # 1. Select Art Direction
    ranked_ad: List[Tuple[float, Dict[str, Any], List[str]]] = []
    for ad in library.art_directions:
        sc, why = score_art_direction(ad, brief)
        ranked_ad.append((sc, ad, why))

    # Tie-break: score descending, then alphabetical ID
    ranked_ad.sort(key=lambda x: (-x[0], x[1]["id"]))
    if not ranked_ad:
        raise ContractValidationError(ERR_HARD_CONSTRAINT_UNSATISFIED, "No art directions found in library", target="art_directions")

    top_ad_score, top_ad, top_ad_why = ranked_ad[0]
    if top_ad_score < 0:
        w_msg = f"Top art direction '{top_ad['id']}' has low fit score ({top_ad_score:.1f})"
        warnings.append(w_msg)
        diagnostics.append(Diagnostic(WARN_LOW_FIT_SCORE, "WARNING", w_msg, target=top_ad["id"]))

    art_direction_plan = {
        "id": top_ad["id"],
        "name": top_ad["name"],
        "score": top_ad_score,
        "rationale": top_ad_why,
        "idea": top_ad.get("idea", ""),
        "composition_rules": top_ad.get("composition", ""),
        "imagery_rules": top_ad.get("imagery", ""),
        "color_rules": top_ad.get("colour", ""),
        "typography_rules": top_ad.get("typography", ""),
        "richness": top_ad.get("richness", "medium")
    }

    # 2. Sequential Composition Slots
    chosen_patterns: List[Dict[str, Any]] = []
    slot_picks: List[Dict[str, Any]] = []
    skipped_slots: List[Dict[str, Any]] = []
    all_asset_requirements: List[AssetRequirement] = []

    for slot in brief.slots:
        candidates = retrieve_candidates_for_slot(slot, brief, library)
        scored_candidates: List[Tuple[float, Dict[str, Any], List[str]]] = []

        for cand in candidates:
            sc, why = score_composition(cand, brief, chosen_patterns, selected_art_direction=top_ad)
            if sc is not None:
                scored_candidates.append((sc, cand, why))

        # Tie-break: score descending, then alphabetical ID
        scored_candidates.sort(key=lambda x: (-x[0], x[1]["id"]))

        if not scored_candidates:
            reason = f"No eligible pattern found for slot '{slot}' (incompatible page_type, excluded, or conflict)"
            skipped_slots.append({"slot": slot, "reason": reason})
            warnings.append(reason)
            diagnostics.append(Diagnostic(WARN_UNRESOLVED_SLOT, "WARNING", reason, target=slot))
            continue

        best_score, best_pattern, best_why = scored_candidates[0]
        chosen_patterns.append(best_pattern)

        alternatives = [
            {"id": c[1]["id"], "name": c[1].get("name", c[1]["id"]), "score": c[0]}
            for c in scored_candidates[1:4]
        ]

        slot_picks.append({
            "slot": slot,
            "pattern_id": best_pattern["id"],
            "pattern_name": best_pattern.get("name", best_pattern["id"]),
            "score": best_score,
            "rationale": best_why,
            "density": best_pattern.get("density"),
            "visual_tags": list(best_pattern.get("visual_tags", [])),
            "blueprint": best_pattern.get("blueprint", ""),
            "alternatives": alternatives
        })

        # Extract and resolve assets
        reqs = resolver.resolve(slot, best_pattern, top_ad, brief.category)
        all_asset_requirements.extend(reqs)

    total_comp_score = round(sum(p["score"] for p in slot_picks), 3)

    # 3. Select Semantic Palette
    ranked_pal: List[Tuple[float, Dict[str, Any], List[str]]] = []
    for pal in library.palettes:
        sc, why = score_palette(pal, brief, selected_art_direction=top_ad)
        ranked_pal.append((sc, pal, why))
    ranked_pal.sort(key=lambda x: (-x[0], x[1]["id"]))
    top_pal_score, top_pal, top_pal_why = ranked_pal[0]

    palette_plan = {
        "id": top_pal["id"],
        "name": top_pal.get("name", top_pal["id"]),
        "score": top_pal_score,
        "rationale": top_pal_why,
        "tokens": {
            "bg": top_pal.get("bg", "#ffffff"),
            "surface": top_pal.get("surface", "#f8f9fa"),
            "ink": top_pal.get("ink", "#111111"),
            "muted": top_pal.get("muted", "#666666"),
            "accent": top_pal.get("accent", "#0066cc"),
            "accent_ink": top_pal.get("accent_ink", "#ffffff")
        }
    }

    # 4. Select Typography Pairing
    ranked_typo: List[Tuple[float, Dict[str, Any], List[str]]] = []
    for typo in library.typography:
        sc, why = score_typography(typo, brief, selected_art_direction=top_ad)
        ranked_typo.append((sc, typo, why))
    ranked_typo.sort(key=lambda x: (-x[0], x[1]["id"]))
    top_typo_score, top_typo, top_typo_why = ranked_typo[0]

    typography_plan = {
        "id": top_typo["id"],
        "name": top_typo.get("name", top_typo["id"]),
        "score": top_typo_score,
        "rationale": top_typo_why,
        "type_class": top_typo.get("type_class", ""),
        "fonts": {
            "display": top_typo.get("display", "system-ui"),
            "text": top_typo.get("text", "system-ui")
        },
        "scale": top_typo.get("scale", "modular-1.25")
    }

    # 5. App Shell (Optional, for app page_type or explicit request)
    app_shell_plan: Optional[Dict[str, Any]] = None
    if brief.page_type == "app" or "app_shell" in brief.slots:
        ranked_shell: List[Tuple[float, Dict[str, Any], List[str]]] = []
        for sh in library.app_shells:
            sc, why = score_app_shell(sh, brief)
            ranked_shell.append((sc, sh, why))
        ranked_shell.sort(key=lambda x: (-x[0], x[1]["id"]))
        top_sh_score, top_sh, top_sh_why = ranked_shell[0]
        app_shell_plan = {
            "id": top_sh["id"],
            "name": top_sh.get("name", top_sh["id"]),
            "score": top_sh_score,
            "rationale": top_sh_why,
            "blueprint": top_sh.get("blueprint", ""),
            "phone_adaptation": top_sh.get("phone", "")
        }

    # 6. Asset Summary
    tier_1_c = sum(1 for a in all_asset_requirements if a.resolution_tier == "tier_1_native")
    tier_2_c = sum(1 for a in all_asset_requirements if a.resolution_tier == "tier_2_archive")
    tier_3_c = sum(1 for a in all_asset_requirements if a.resolution_tier == "tier_3_css_svg")

    asset_summary = {
        "total_required": len(all_asset_requirements),
        "tier_1_native": tier_1_c,
        "tier_2_archive": tier_2_c,
        "tier_3_css_svg": tier_3_c
    }

    # 7. Motion Intelligence & References Integration (Phase 5)
    motion_plan = plan_motion_for_brief(brief, library.motions)
    curated_references = retrieve_design_references(brief, library)

    timestamp = deterministic_timestamp or datetime.now(timezone.utc).isoformat()
    brief_dict = brief.to_dict()
    plan_id = compute_plan_id(brief_dict, library.version)

    plan_dict = {
        "runtime_version": RUNTIME_VERSION,
        "library_version": library.version,
        "plan_id": plan_id,
        "generated_at": timestamp,
        "normalized_brief": brief_dict,
        "art_direction": art_direction_plan,
        "composition": {
            "total_score": total_comp_score,
            "slots": slot_picks,
            "skipped_slots": skipped_slots
        },
        "palette": palette_plan,
        "typography": typography_plan,
        "app_shell": app_shell_plan,
        "motion_plan": motion_plan,
        "curated_references": curated_references,
        "assets": {
            "summary": asset_summary,
            "requirements": [req.to_dict() for req in all_asset_requirements]
        },
        "warnings": warnings,
        "diagnostics": [d.to_dict() for d in diagnostics]
    }
    return to_serializable(plan_dict)
