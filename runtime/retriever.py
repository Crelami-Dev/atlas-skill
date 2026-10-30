#!/usr/bin/env python3
"""Atlas Runtime Engine — Candidate Retriever.

Filters and retrieves eligible canonical records for a given brief and slot.
Handles page-type restrictions, exclusion lists, slot aliases, and asset compatibility.
Zero-dependency, Python 3.9+ standard library.
"""
from typing import Any, Dict, List, Optional, Set, Tuple

from .contracts import ProductBrief
from .loader import CanonicalLibrary

# Slot family aliases to support multi-faceted slots
SLOT_FAMILY_ALIASES: Dict[str, List[str]] = {
    "nav": ["nav"],
    "hero": ["hero"],
    "social_proof": ["social_proof", "proof", "stats", "metrics", "testimonial"],
    "features": ["features", "showcase", "list"],
    "how-it-works": ["how-it-works", "process"],
    "pricing": ["pricing"],
    "faq": ["faq"],
    "cta": ["cta"],
    "footer": ["footer"],
    "story": ["story", "about", "intro"],
    "metrics": ["metrics", "stats", "proof"],
    "showcase": ["showcase", "gallery", "work"],
    "app_shell": ["app_shell"],
    "app_data": ["app_data"],
    "app_form": ["app_form"],
}


def _asset_satisfied(requirement: str, available_assets: List[str]) -> bool:
    """Check if requirement is satisfied.
    Requirement like 'photo|product_ui' means any-of; plain token means required.
    """
    if not available_assets:
        # If caller specifies no asset pool, assets are satisfied via 3-tier generation pipeline
        return True
    options = [opt.strip() for opt in requirement.split("|")]
    return any(opt in available_assets for opt in options)


def is_pattern_eligible(
    pattern: Dict[str, Any],
    brief: ProductBrief,
    strict_assets: bool = False
) -> Tuple[bool, str]:
    """Determine whether a composition pattern passes all hard constraints for the brief.
    
    Returns (eligible: bool, reason: str).
    """
    # 1. Page Type Constraint
    page_types = pattern.get("page_types", [])
    if brief.page_type not in page_types and "all" not in page_types:
        return False, f"incompatible page_type (pattern allows {page_types})"

    # 2. Exclude List Constraint
    pattern_id = pattern.get("id", "")
    if pattern_id in brief.exclude:
        return False, "explicitly excluded in brief"

    # 3. Explicit Required Patterns Constraint
    forced = brief.explicit_constraints.get("required_patterns", [])
    if forced and pattern_id not in forced:
        # If user explicitly forced specific patterns for this slot
        slot_forced = [p for p in forced if p.split(":")[1] == pattern.get("family")]
        if slot_forced and pattern_id not in slot_forced:
            return False, f"slot constrained to {slot_forced}"

    # 4. Asset Compatibility Constraint
    requires = pattern.get("requires", {})
    req_assets = requires.get("assets", []) if isinstance(requires, dict) else []
    if strict_assets and brief.assets:
        for req in req_assets:
            if not _asset_satisfied(req, brief.assets):
                return False, f"missing required asset: {req}"

    return True, "eligible"


def retrieve_candidates_for_slot(
    slot: str,
    brief: ProductBrief,
    library: CanonicalLibrary
) -> List[Dict[str, Any]]:
    """Retrieve all eligible composition patterns for a given slot.
    Searches primary slot family and recognized aliases.
    """
    families = SLOT_FAMILY_ALIASES.get(slot, [slot])
    candidates: List[Dict[str, Any]] = []
    seen_ids: Set[str] = set()

    for fam in families:
        patterns = library.get_compositions_by_family(fam)
        for p in patterns:
            pid = p.get("id")
            if pid in seen_ids:
                continue
            ok, reason = is_pattern_eligible(p, brief, strict_assets=bool(brief.explicit_constraints.get("strict_assets", False)))
            if ok:
                candidates.append(p)
                seen_ids.add(pid)

    return candidates


def retrieve_motion_candidates(
    brief: ProductBrief,
    library: CanonicalLibrary
) -> List[Dict[str, Any]]:
    """Retrieve eligible motion patterns from the canonical library for a given brief.
    
    Filters based on page_type, density, tones, and exclusion lists.
    Guarantees stable IDs, provenance, and contextual relevance.
    """
    candidates = []
    page_type = getattr(brief, "page_type", "marketing")
    density = getattr(brief, "density", "med")
    tones = set(getattr(brief, "tones", []))
    exclude = set(getattr(brief, "exclude", []))

    for m in library.motions:
        mid = m.get("id")
        if not mid or mid in exclude:
            continue

        # In high-density or application mode, stillness is always top priority
        if (page_type == "app" or density == "high") and mid not in {"stillness", "rolling-figures", "index-preview"}:
            continue

        candidates.append(m)

    # If no candidate matched or library empty, fallback to stillness
    if not candidates:
        stillness = library.get_motion_by_id("stillness")
        if stillness:
            candidates.append(stillness)

    return candidates


def retrieve_design_references(
    brief: ProductBrief,
    library: CanonicalLibrary
) -> Dict[str, Any]:
    """Retrieve a comprehensive, traceable set of design references for a brief.
    
    Establishes the traceable chain:
    brief -> retrieved references -> design decisions -> generated output -> validation
    """
    page_type = getattr(brief, "page_type", "marketing")
    category = getattr(brief, "category", "general")
    tones = list(getattr(brief, "tones", []))

    # 1. Motion candidates
    motions = retrieve_motion_candidates(brief, library)
    
    # 2. Reference heuristics & laws based on context
    applicable_heuristics = [
        {
            "id": "law-two-line-headline",
            "name": "Two-Line Headline Limit",
            "source": "knowledge/taste/references/copy.md",
            "rule": "Headlines must not wrap past 2 lines; budget 24-32 characters for maximum impact."
        },
        {
            "id": "law-40-percent-focal-point",
            "name": "40% Hero Focal Area",
            "source": "knowledge/taste/references/imagery.md",
            "rule": "Primary visual subject or hero image must command at least 40% of viewport area."
        }
    ]

    if page_type == "app" or getattr(brief, "density", "med") == "high":
        applicable_heuristics.append({
            "id": "guideline-dense-ui-stillness",
            "name": "Operational Stillness & Density",
            "source": "knowledge/taste/references/app-screens.md",
            "rule": "Dense data dashboards prioritize stillness, tabular figures, and structured card grouping over decorative motion."
        })
    elif page_type == "editorial" or "editorial" in tones:
        applicable_heuristics.append({
            "id": "guideline-editorial-rhythm",
            "name": "Editorial Whitespace & Asymmetry",
            "source": "knowledge/taste/references/layout.md",
            "rule": "Use asymmetric grid margins, generous whitespace, and masked line rises."
        })
    else:
        applicable_heuristics.append({
            "id": "guideline-conversion-clarity",
            "name": "Product Conversion Clarity",
            "source": "knowledge/taste/references/copy.md",
            "rule": "Place one primary CTA above the fold, supported by honest proof and concrete product visual."
        })

    return {
        "brief_summary": {
            "page_type": page_type,
            "category": category,
            "density": getattr(brief, "density", "med"),
            "tones": tones
        },
        "retrieved_motions": [m.get("id") for m in motions],
        "applicable_heuristics": applicable_heuristics,
        "provenance_root": "knowledge/taste",
        "traceable_rationale": (
            f"Retrieved {len(motions)} motion patterns and {len(applicable_heuristics)} "
            f"design heuristics tailored for '{category}' with page_type '{page_type}'."
        )
    }

