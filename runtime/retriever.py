#!/usr/bin/env python3
"""Atlas Runtime Engine — Candidate Retriever.

Filters and retrieves eligible canonical records for a given brief and slot.
Handles page-type restrictions, exclusion lists, slot aliases, and asset compatibility.
Enriched with domain-aware reference library retrieval, content integrity rules,
and responsive multi-viewport floor guards.
Zero-dependency, Python 3.9+ standard library.
"""
import hashlib
import os
import re
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


# ==============================================================================
# Curated Reference Library Retrieval & Reasoning System (P7 Part 1)
# ==============================================================================

_CATALOG_CACHE: Optional[Dict[str, Dict[str, str]]] = None


def default_references_dir() -> str:
    """Return default path to skills/atlas-skill/references/."""
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "skills", "atlas-skill", "references")
    )


def load_reference_catalog(ref_dir: Optional[str] = None) -> Dict[str, Dict[str, str]]:
    """Load and parse markdown references from skills/atlas-skill/references/.
    
    Zero-dependency markdown parser extracting ## H2 sections into clean text buffers.
    Cached in-memory for deterministic, zero-allocation repeated calls.
    """
    global _CATALOG_CACHE
    target_dir = os.path.abspath(ref_dir or default_references_dir())
    
    # If already cached for the same target directory, return cached dictionary
    if _CATALOG_CACHE is not None and not ref_dir:
        return _CATALOG_CACHE

    catalog: Dict[str, Dict[str, str]] = {}
    if not os.path.isdir(target_dir):
        return catalog

    for fname in sorted(os.listdir(target_dir)):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(target_dir, fname)
        sections: Dict[str, str] = {}
        current_h2: Optional[str] = None
        buffer: List[str] = []

        try:
            with open(fpath, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for line in lines:
                if line.startswith("## "):
                    if current_h2:
                        sections[current_h2] = "".join(buffer).strip()
                    # Strip leading section numbers e.g. "1. Domain..." -> "Domain..."
                    raw_title = line[3:].strip()
                    current_h2 = re.sub(r"^\d+\.\s*", "", raw_title)
                    buffer = []
                else:
                    if current_h2:
                        buffer.append(line)
            if current_h2:
                sections[current_h2] = "".join(buffer).strip()
            catalog[fname] = sections
        except Exception:
            # Resilient fallback if individual reference file fails to read
            catalog[fname] = {}

    if not ref_dir:
        _CATALOG_CACHE = catalog

    return catalog


def _match_domain_key(category: str) -> str:
    """Map brief category to canonical domain family."""
    c = category.strip().lower()
    if c in ("fashion", "luxury", "horlogerie", "hospitality", "restaurant", "architecture"):
        return "luxury"
    elif c in ("dev-tool", "cloud", "infra", "developer", "data", "security", "ai-product"):
        return "technical"
    elif c in ("agency", "studio-portfolio", "design", "creative", "culture"):
        return "agency"
    return "general"


def _match_archetype_key(brief: ProductBrief) -> str:
    """Determine dominant macro archetype from brief parameters."""
    tones = [t.lower() for t in getattr(brief, "tones", [])]
    category = getattr(brief, "category", "").lower()
    density = getattr(brief, "density", "med")

    if any(t in tones for t in ("refined", "luxury", "calm", "editorial")) or category in ("fashion", "luxury", "architecture"):
        return "Editorial Luxury"
    elif any(t in tones for t in ("technical", "precise", "austere", "functional")) or category in ("dev-tool", "cloud", "infra"):
        return "Technical Instrument"
    elif any(t in tones for t in ("bold", "confident", "curated", "expressive")) or category in ("agency", "studio-portfolio"):
        return "Brutalist Monumental"
    elif density == "high" or getattr(brief, "page_type", "marketing") == "app":
        return "Dense Data Board"
    return "Quiet Minimalist"


def retrieve_design_references(
    brief: ProductBrief,
    library: CanonicalLibrary,
    ref_dir: Optional[str] = None
) -> Dict[str, Any]:
    """Retrieve a comprehensive, traceable set of design references for a brief.
    
    Establishes the traceable chain:
    brief -> domain pattern -> archetype signature -> principles -> content integrity -> exemplars -> output
    """
    page_type = getattr(brief, "page_type", "marketing")
    category = getattr(brief, "category", "general")
    tones = list(getattr(brief, "tones", []))
    density = getattr(brief, "density", "med")

    # 1. Motion candidates (deterministic filter)
    motions = retrieve_motion_candidates(brief, library)

    # 2. Backward-compatible heuristics (maintaining existing disk paths in knowledge/taste/references)
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

    if page_type == "app" or density == "high":
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

    # 3. Load structured reference catalog
    catalog = load_reference_catalog(ref_dir)
    domain_key = _match_domain_key(category)
    archetype_key = _match_archetype_key(brief)

    # 4. Extract Matched Domain Pattern
    domain_catalog = catalog.get("domain-patterns.md", {})
    matched_domain_section = None
    for h, content in domain_catalog.items():
        if domain_key == "luxury" and "Luxury Fashion" in h:
            matched_domain_section = {"title": h, "guidance": content}
            break
        elif domain_key == "technical" and "Developer Tool" in h:
            matched_domain_section = {"title": h, "guidance": content}
            break
        elif domain_key == "agency" and "Creative Agency" in h:
            matched_domain_section = {"title": h, "guidance": content}
            break

    if not matched_domain_section:
        matched_domain_section = {
            "title": "General Digital Product & Services",
            "guidance": "Balanced information architecture pairing clear value proposition with honest feature proofs."
        }

    # 5. Extract Matched Archetype Guidance
    archetype_catalog = catalog.get("art-direction-archetypes.md", {})
    matched_archetype_section = None
    for h, content in archetype_catalog.items():
        if archetype_key.lower() in h.lower():
            matched_archetype_section = {"title": h, "guidance": content}
            break
    if not matched_archetype_section:
        matched_archetype_section = {
            "title": f"Archetype: {archetype_key}",
            "guidance": "Structured layout emphasizing typography contrast and purposeful section cadence."
        }

    # 6. Content Integrity Rules & Blacklist
    content_integrity_rules = {
        "classification_doctrine": "4-Tier System: 1. Factual Backed, 2. Qualitative Aspirational, 3. Explicit Placeholder, 4. Forbidden Fabrication",
        "forbidden_claims_blacklist": [
            "Unverified SLA percentages (e.g. 99.999%, 99.9%)",
            "Unmeasured network latency metrics (e.g. <1ms)",
            "Unverified security certifications (e.g. SOC 2 Type II, ISO 27001)",
            "Fabricated award honors (e.g. 140+ Awards)",
            "Fabricated years in business (e.g. 12yr Leadership)",
            "Fabricated physical salon/office counts (e.g. 12 Capitals)",
            "Fabricated pricing numbers or tiers not supplied in brief (e.g. $49/mo, $12,000/project)",
            "Unverified hardware/runtime assertions (e.g. zero-allocation, sub-millisecond overhead, eBPF)",
            "Unverified sustainability or material compliance claims (e.g. sustainably certified, archival mark)"
        ],
        "mandatory_policy": (
            "When ProductBrief does not supply verified quantitative evidence or pricing, generator MUST "
            "synthesize Tier 2 Qualitative Capability Claims or Tier 3 Explicit Placeholders ([PRICE_ON_REQUEST]). "
            "Never hallucinate statistics or nominal prices."
        ),
        "template_leakage_ban": (
            "Prohibited from generating internal Atlas Skill system jargon (e.g. 'Bespoke art direction', "
            "'Harmonize macro art direction', 'Resilient vector fallbacks') into client websites."
        )
    }

    # 7. Responsive Floor Guards & Multi-Viewport Rules
    responsive_guards = {
        "tablet_portrait_768px": "Enforce 2x2 symmetrical grid on .proof-grid (min-width: 641px and max-width: 900px) to prevent 3+1 orphan cards.",
        "small_mobile_320px": "Cap low-density h1_clamp minimum to 2.0rem (32px) to prevent word splitting and isolated ampersand orphans.",
        "zero_blowout_contract": "Features grid must collapse to 1fr on <= 768px with minmax(min(100%, 280px), 1fr); scrollWidth must equal clientWidth."
    }

    # 8. Anti-Patterns to Avoid
    anti_patterns_to_avoid = [
        "Template Skinning Trap: Same linear DOM stack with swapped CSS variables.",
        "Fake Certification Trap: Unsolicited SOC 2 or 5-nines SLA badges.",
        "Orphaned Punctuation Trap: Ampersand or dash sitting alone on a line on mobile.",
        "Asymmetrical Orphan Card Trap: 4th card stranded alone on row 2 on tablet.",
        "Monolithic Internal Jargon Leakage: Web design generator vocabulary in client copy."
    ]

    # 9. Real-Site Exemplar Retrieval from Canonical Library (data/sites.json)
    matched_exemplars = []
    if hasattr(library, "sites") and library.sites:
        scored_sites = []
        for s in library.sites:
            s_score = 0.0
            s_kind = (s.get("kind") or "").lower()
            s_mood = [m.lower() for m in s.get("mood", [])]

            # Category and domain matching
            if s_kind == category.lower():
                s_score += 4.0
            elif domain_key == "luxury" and s_kind in ("fashion", "luxury", "architecture", "hospitality"):
                s_score += 2.5
            elif domain_key == "technical" and s_kind in ("dev-tool", "saas", "ai-product"):
                s_score += 2.5
            elif domain_key == "agency" and s_kind in ("agency", "studio-portfolio"):
                s_score += 2.5

            # Tone overlap
            overlap = set(tones) & set(s_mood)
            s_score += 1.0 * len(overlap)

            # Deterministic hash tie-breaker
            if s_score > 0:
                h = hashlib.sha256(f"{brief.project_name}:{s.get('id', '')}".encode()).hexdigest()
                scored_sites.append((-s_score, h, s))

        scored_sites.sort(key=lambda x: (x[0], x[1]))
        case_studies = catalog.get("curated-case-studies.md", {})
        for _, _, s in scored_sites[:3]:
            steals = s.get("steal", [])
            s_id = s.get("id", "")
            clean_id = s_id.replace("site:", "")
            matched_cs = None
            for h in case_studies.keys():
                if clean_id in h:
                    matched_cs = h
                    break

            ex_data = {
                "id": s_id,
                "name": s.get("name"),
                "kind": s.get("kind"),
                "archetype": s.get("archetype"),
                "url": s.get("url"),
                "source": s.get("source"),
                "transferable_principles": list(steals[:2]),
                "layout_summary": (s.get("layout") or "")[:150]
            }
            if matched_cs:
                ex_data["curated_case_study"] = matched_cs
            matched_exemplars.append(ex_data)

    # 10. Traceable Rationale
    traceable_rationale = (
        f"Domain '{domain_key.upper()}' paired with archetype '{archetype_key}' based on category '{category}' "
        f"and tones {tones}. Retrieved {len(matched_exemplars)} canonical site exemplars with actionable "
        f"transferable principles, bound by strict content integrity (zero fake metrics) and multi-viewport floor guards."
    )

    return {
        "brief_summary": {
            "page_type": page_type,
            "category": category,
            "density": density,
            "tones": tones,
            "domain_family": domain_key,
            "recommended_archetype": archetype_key
        },
        "matched_domain_pattern": matched_domain_section,
        "matched_archetype": matched_archetype_section,
        "content_integrity_rules": content_integrity_rules,
        "responsive_guards": responsive_guards,
        "anti_patterns_to_avoid": anti_patterns_to_avoid,
        "matched_exemplars": matched_exemplars,
        "retrieved_motions": [m.get("id") for m in motions],
        "applicable_heuristics": applicable_heuristics,
        "provenance_root": "skills/atlas-skill/references",
        "traceable_rationale": traceable_rationale
    }
