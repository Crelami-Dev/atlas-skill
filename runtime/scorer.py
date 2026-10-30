#!/usr/bin/env python3
"""Atlas Runtime Engine — Scoring and Ranking Module.

Calculates multi-dimensional fit scores for art directions, composition patterns,
palettes, typography, and app shells against a normalized ProductBrief.
Guarantees deterministic ranking, stable tie-breaking, and transparent rationale.
Zero-dependency, Python 3.9+ standard library.
"""
from typing import Any, Dict, List, Optional, Set, Tuple

from runtime.contracts import ProductBrief

DENSITY_NUMERIC = {"low": 0, "med": 1, "high": 2}


def score_art_direction(art_dir: Dict[str, Any], brief: ProductBrief) -> Tuple[float, List[str]]:
    """Score an Art Direction against the ProductBrief.
    
    Returns (score: float, rationale: List[str]).
    """
    w = brief.scoring_weights
    score = 0.0
    rationale: List[str] = []

    # 1. Sector / Category match
    sectors = art_dir.get("sectors", [])
    if brief.category in sectors:
        pts = 3.0 * w.get("category", 1.0)
        score += pts
        rationale.append(f"sector match (+{pts:.1f}): '{brief.category}'")
    elif brief.category == "*":
        pts = 1.0 * w.get("category", 1.0)
        score += pts
        rationale.append(f"general sector fit (+{pts:.1f})")
    else:
        pts = -1.5 * w.get("category", 1.0)
        score += pts
        rationale.append(f"sector mismatch ({pts:.1f})")

    # 2. Tone overlap
    dir_tones = set(art_dir.get("tones", []))
    brief_tones = set(brief.tones)
    tone_overlap = dir_tones & brief_tones
    if tone_overlap:
        pts = 1.5 * w.get("tones", 1.0) * len(tone_overlap)
        score += pts
        rationale.append(f"tone match (+{pts:.1f}): {', '.join(sorted(tone_overlap))}")

    # 3. Density / Richness alignment
    richness = art_dir.get("richness")
    if richness:
        if (brief.density == "high" and richness == "high") or (brief.density == "low" and richness == "low"):
            pts = 1.0 * w.get("density", 0.8)
            score += pts
            rationale.append(f"density/richness match (+{pts:.1f}): {richness}")
        elif (brief.density == "high" and richness == "low") or (brief.density == "low" and richness == "high"):
            pts = -0.8 * w.get("density", 0.8)
            score += pts
            rationale.append(f"density/richness tension ({pts:.1f})")

    # 4. Explicit constraint bonus
    forced_id = brief.explicit_constraints.get("art_direction_id")
    if forced_id and art_dir.get("id") == forced_id:
        score += 100.0
        rationale.append("explicit constraint override (+100.0)")

    return round(score, 3), rationale


def score_composition(
    pattern: Dict[str, Any],
    brief: ProductBrief,
    chosen_patterns: List[Dict[str, Any]],
    selected_art_direction: Optional[Dict[str, Any]] = None
) -> Tuple[Optional[float], List[str]]:
    """Score a candidate composition pattern in sequence context.
    
    Returns (score: Optional[float], rationale: List[str]).
    If the pattern is incompatible with an already chosen pattern, score is None.
    """
    w = brief.scoring_weights
    score = 0.0
    rationale: List[str] = []
    pid = pattern.get("id", "")

    # 1. Check sequence incompatibility (Hard constraint)
    for c in chosen_patterns:
        c_incompat = c.get("incompatible", [])
        p_incompat = pattern.get("incompatible", [])
        if pid in c_incompat or c.get("id") in p_incompat:
            return None, [f"hard incompatibility with chosen section {c.get('id')}"]

    # 2. Art Direction Synergy
    if selected_art_direction:
        ad_id = selected_art_direction.get("id", "")
        # Base slug e.g. "art-dir:name-as-monument" -> "name-as-monument"
        ad_slug = ad_id.split(":", 1)[-1]
        pattern_cats = pattern.get("categories", [])
        if ad_slug in pattern_cats:
            pts = 4.0 * w.get("art_direction_synergy", 1.5)
            score += pts
            rationale.append(f"art-direction synergy (+{pts:.1f}): '{ad_slug}'")

    # 3. Category match
    pattern_cats = pattern.get("categories", [])
    if brief.category in pattern_cats:
        pts = 3.0 * w.get("category", 1.0)
        score += pts
        rationale.append(f"category match (+{pts:.1f}): '{brief.category}'")
    elif "*" in pattern_cats:
        pts = 1.0 * w.get("category", 1.0)
        score += pts
        rationale.append(f"general-purpose pattern (+{pts:.1f})")
    elif not (selected_art_direction and ad_slug in pattern_cats):
        pts = -1.5 * w.get("category", 1.0)
        score += pts
        rationale.append(f"category mismatch ({pts:.1f})")

    # 4. Tone overlap
    p_tones = set(pattern.get("tones", []))
    b_tones = set(brief.tones)
    t_overlap = p_tones & b_tones
    if t_overlap:
        pts = 1.2 * w.get("tones", 1.0) * len(t_overlap)
        score += pts
        rationale.append(f"tone match (+{pts:.1f}): {', '.join(sorted(t_overlap))}")

    # 5. Density fit
    p_density = pattern.get("density", "med")
    if brief.density in DENSITY_NUMERIC and p_density in DENSITY_NUMERIC:
        diff = abs(DENSITY_NUMERIC[brief.density] - DENSITY_NUMERIC[p_density])
        if diff == 0:
            pts = 1.0 * w.get("density", 0.8)
            score += pts
            rationale.append(f"density exact match (+{pts:.1f}): '{p_density}'")
        elif diff == 1:
            pts = 0.4 * w.get("density", 0.8)
            score += pts
            rationale.append(f"density adjacent (+{pts:.1f}): '{p_density}'")
        else:
            pts = -0.8 * w.get("density", 0.8)
            score += pts
            rationale.append(f"density tension ({pts:.1f}): brief '{brief.density}' vs '{p_density}'")

    # 6. Goals fit
    p_goals = set(pattern.get("goals", []))
    b_goals = set(brief.goals)
    g_overlap = p_goals & b_goals
    if g_overlap:
        pts = 1.0 * w.get("goals", 1.0) * len(g_overlap)
        score += pts
        rationale.append(f"goal alignment (+{pts:.1f}): {', '.join(sorted(g_overlap))}")

    # 7. Conventional vs Unconventional preference
    v_tags = set(pattern.get("visual_tags", []))
    unconventional_tags = {"asymmetric", "offset", "layered", "overlap", "overlay"}
    if brief.prefer_conventional:
        unc_present = v_tags & unconventional_tags
        if unc_present:
            pts = -4.0 * w.get("conventional", 1.5)
            score += pts
            rationale.append(f"unconventional layout penalized ({pts:.1f}): {', '.join(sorted(unc_present))}")
        else:
            pts = 1.2 * w.get("conventional", 1.5)
            score += pts
            rationale.append(f"conventional structure fit (+{pts:.1f})")

    # 8. Sequence pairing and rhythm adjustments
    for c in chosen_patterns:
        if pid in c.get("related", []) or c.get("id") in pattern.get("related", []):
            pts = 0.8 * w.get("sequence_pairing", 0.8)
            score += pts
            rationale.append(f"pairs with chosen {c.get('id')} (+{pts:.1f})")

    if chosen_patterns:
        prev = chosen_patterns[-1]
        prev_tags = set(prev.get("visual_tags", []))
        shared_tags = v_tags & prev_tags
        if shared_tags:
            pts = -1.0 * w.get("sequence_repetition", 1.0) * len(shared_tags)
            score += pts
            rationale.append(f"avoids repeating rhythm of {prev.get('id')} ({pts:.1f}): {', '.join(sorted(shared_tags))}")

    # 9. Explicit constraint bonus
    forced_patterns = brief.explicit_constraints.get("required_patterns", [])
    if pid in forced_patterns:
        score += 100.0
        rationale.append("explicit constraint override (+100.0)")

    return round(score, 3), rationale


def score_palette(
    palette: Dict[str, Any],
    brief: ProductBrief,
    selected_art_direction: Optional[Dict[str, Any]] = None
) -> Tuple[float, List[str]]:
    """Score a semantic palette against brief tones and art direction palette tags."""
    score = 0.0
    rationale: List[str] = []
    pal_tags = set(palette.get("tags", []))

    # Match against Art Direction palette tags (highest synergy)
    if selected_art_direction:
        ad_pal_tags = set(selected_art_direction.get("palette_tags", []))
        tag_overlap = pal_tags & ad_pal_tags
        if tag_overlap:
            score += 3.0 * len(tag_overlap)
            rationale.append(f"art-direction palette synergy (+{3.0 * len(tag_overlap):.1f}): {', '.join(sorted(tag_overlap))}")

    # Match against brief tones
    b_tones = set(brief.tones)
    tone_overlap = pal_tags & b_tones
    if tone_overlap:
        score += 1.5 * len(tone_overlap)
        rationale.append(f"tone match (+{1.5 * len(tone_overlap):.1f}): {', '.join(sorted(tone_overlap))}")

    # Explicit constraint
    forced_id = brief.explicit_constraints.get("palette_id")
    if forced_id and palette.get("id") == forced_id:
        score += 100.0
        rationale.append("explicit palette constraint override (+100.0)")

    return round(score, 3), rationale


def score_typography(
    typography: Dict[str, Any],
    brief: ProductBrief,
    selected_art_direction: Optional[Dict[str, Any]] = None
) -> Tuple[float, List[str]]:
    """Score a typography pairing against brief tones and art direction type classes."""
    score = 0.0
    rationale: List[str] = []
    t_class = typography.get("type_class", "")

    # Match against Art Direction type_classes
    if selected_art_direction:
        ad_classes = set(selected_art_direction.get("type_classes", []))
        if t_class in ad_classes:
            score += 4.0
            rationale.append(f"art-direction typography class match (+4.0): '{t_class}'")

    # Match against brief tones (e.g. bold, editorial, quiet)
    if "bold" in brief.tones and any(k in t_class for k in ("heavy", "black", "extended")):
        score += 1.5
        rationale.append("tone alignment with bold typography (+1.5)")
    if "editorial" in brief.tones and "serif" in t_class:
        score += 1.5
        rationale.append("tone alignment with editorial serif typography (+1.5)")
    if "minimal" in brief.tones and "grotesk" in t_class:
        score += 1.5
        rationale.append("tone alignment with minimal grotesk typography (+1.5)")

    # Explicit constraint
    forced_id = brief.explicit_constraints.get("typography_id")
    if forced_id and typography.get("id") == forced_id:
        score += 100.0
        rationale.append("explicit typography constraint override (+100.0)")

    return round(score, 3), rationale


def score_app_shell(
    app_shell: Dict[str, Any],
    brief: ProductBrief
) -> Tuple[float, List[str]]:
    """Score an application shell layout against brief category and primary tasks."""
    score = 0.0
    rationale: List[str] = []
    suits = set(app_shell.get("suits", []))

    if brief.category in suits:
        score += 4.0
        rationale.append(f"app category suit match (+4.0): '{brief.category}'")
    else:
        score += 1.0
        rationale.append("general app shell baseline (+1.0)")

    # Density alignment
    if brief.density == "high" and "devtools" in suits:
        score += 1.0
        rationale.append("high-density task alignment (+1.0)")

    # Explicit constraint
    forced_id = brief.explicit_constraints.get("app_shell_id")
    if forced_id and app_shell.get("id") == forced_id:
        score += 100.0
        rationale.append("explicit app shell constraint override (+100.0)")

    return round(score, 3), rationale


def score_motion(
    motion: Dict[str, Any],
    brief: ProductBrief
) -> Tuple[float, List[str]]:
    """Score a motion pattern against brief page_type, category, tones, and density.
    
    Returns (score: float, rationale: List[str]).
    """
    mid = motion.get("id", "")
    score = 1.0
    rationale = ["base motion score (+1.0)"]

    page_type = getattr(brief, "page_type", "marketing")
    density = getattr(brief, "density", "med")
    tones = set(getattr(brief, "tones", []))
    category = getattr(brief, "category", "general")

    # App mode or high density
    if page_type == "app" or density == "high":
        if mid == "stillness":
            score += 5.0
            rationale.append("stillness prioritized for high-density / application readability (+5.0)")
        elif mid == "rolling-figures":
            score += 2.0
            rationale.append("rolling figures suitable for quantitative metrics (+2.0)")
        else:
            score -= 2.0
            rationale.append("decorative motion de-emphasized in dense application mode (-2.0)")

    # Editorial mode
    elif page_type == "editorial" or "editorial" in tones:
        if mid in {"masked-headline", "shutter-image"}:
            score += 4.0
            rationale.append(f"signature editorial reveal (+4.0): {mid}")
        elif mid in {"ink-fill", "sheet-over", "slow-crossfade"}:
            score += 2.5
            rationale.append(f"narrative pacing synergy (+2.5): {mid}")

    # Marketing / Product
    else:
        if mid in {"masked-headline", "shutter-image"}:
            score += 3.0
            rationale.append(f"strong value proposition reveal (+3.0): {mid}")
        if mid == "rolling-figures" and ("metrics" in getattr(brief, "slots", []) or category in {"finance", "fintech", "saas"}):
            score += 3.5
            rationale.append("rolling figures matched to quantifiable proof (+3.5)")

    # Explicit override
    forced_motion = brief.explicit_constraints.get("forced_motion")
    if forced_motion and mid == forced_motion:
        score += 100.0
        rationale.append("explicit motion constraint override (+100.0)")

    return round(score, 3), rationale
