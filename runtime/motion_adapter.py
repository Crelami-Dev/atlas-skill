#!/usr/bin/env python3
"""Atlas Runtime Engine — Motion Adapter & Intelligence.

Translates high-level motion intentions from Taste and Atlas into validated,
reproducible motion plans with first-class Anime.js integration, strict
reduced-motion fallbacks, and intentional stillness selection.

Zero-dependency, Python 3.9+ standard library.
"""
import copy
import json
import os
from typing import Any, Dict, List, Optional, Tuple

SCHEMA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "knowledge", "taste", "schemas", "motion-pattern.schema.json")
)
MOTIONS_DATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "knowledge", "taste", "library", "motions.json")
)


def load_motion_patterns(data_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load enriched canonical motion patterns from disk."""
    path = data_path or MOTIONS_DATA_PATH
    if not os.path.exists(path):
        # Fallback to data/motions.json
        alt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "motions.json"))
        if os.path.exists(alt_path):
            path = alt_path
        else:
            return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_motion_pattern(pattern: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate a single motion pattern dictionary against required schema fields."""
    required_fields = [
        "id", "name", "intent", "useCase", "trigger", "targets",
        "timing", "easing", "reducedMotionFallback",
        "performanceConsiderations", "lifecycle",
        "responsiveBehavior", "sourceProvenance"
    ]
    errors = []
    for field in required_fields:
        if field not in pattern:
            errors.append(f"Missing required field: '{field}'")
    
    # Check trigger enum
    valid_triggers = {"load", "scroll", "hover", "press", "click", "state-change", "none"}
    if pattern.get("trigger") not in valid_triggers:
        errors.append(f"Invalid trigger: '{pattern.get('trigger')}'. Must be one of {valid_triggers}")

    # Check timing
    timing = pattern.get("timing")
    if not isinstance(timing, dict) or "durationMs" not in timing:
        errors.append("Field 'timing' must be a dict containing 'durationMs'")

    # Check easing
    easing = pattern.get("easing")
    if not isinstance(easing, dict) or "token" not in easing or "bezier" not in easing:
        errors.append("Field 'easing' must be a dict containing 'token' and 'bezier'")

    return (len(errors) == 0, errors)


def plan_motion_for_brief(
    brief: Any,
    motions_library: List[Dict[str, Any]],
    user_override_pattern: Optional[str] = None
) -> Dict[str, Any]:
    """Select context-appropriate motion patterns based on brief category, tone, and page type.
    
    Principles:
    - Operational dashboards / dense data: 'stillness' or minimal 'rolling-figures'.
    - Editorial / portfolio: 'masked-headline' + 'shutter-image'.
    - Marketing / fintech product: 'masked-headline' + 'rolling-figures' or 'shutter-image'.
    - Minimalist / high-trust: 'stillness' as an active, dignified design choice.
    """
    by_id = {m["id"]: m for m in motions_library}
    page_type = getattr(brief, "page_type", "marketing")
    density = getattr(brief, "density", "med")
    tones = set(getattr(brief, "tones", []))
    category = getattr(brief, "category", "general")
    explicit_constraints = getattr(brief, "explicit_constraints", {}) or {}

    selected_patterns = []
    rationale = []

    # Check explicit user constraint
    forced_motion = user_override_pattern or explicit_constraints.get("forced_motion")
    if forced_motion and forced_motion in by_id:
        selected_patterns.append(by_id[forced_motion])
        rationale.append(f"Explicitly forced motion pattern '{forced_motion}' requested by brief.")
    elif page_type == "app" or density == "high" or "clinical" in tones or "minimal" in tones:
        # High density or app mode: select intentional stillness
        stillness = by_id.get("stillness")
        if stillness:
            selected_patterns.append(stillness)
            rationale.append(
                "Selected 'stillness' for high-density / application layout to maximize data "
                "readability and eliminate decorative distraction."
            )
    elif page_type == "editorial" or "editorial" in tones or category in {"portfolio", "culture", "publishing"}:
        masked = by_id.get("masked-headline")
        shutter = by_id.get("shutter-image")
        if masked:
            selected_patterns.append(masked)
            rationale.append("Selected 'masked-headline' to establish rhythmic typographic presence on load.")
        if shutter:
            selected_patterns.append(shutter)
            rationale.append("Selected 'shutter-image' to dramatize the single primary focal photograph.")
    else:
        # Marketing / Product landing page
        masked = by_id.get("masked-headline")
        if masked:
            selected_patterns.append(masked)
            rationale.append("Selected 'masked-headline' for crisp value proposition presentation.")
        if "metrics" in getattr(brief, "slots", []) or "fintech" in category or "saas" in category:
            rolling = by_id.get("rolling-figures")
            if rolling:
                selected_patterns.append(rolling)
                rationale.append("Selected 'rolling-figures' to highlight key numerical metrics.")
        else:
            shutter = by_id.get("shutter-image")
            if shutter:
                selected_patterns.append(shutter)
                rationale.append("Selected 'shutter-image' for hero visual aperture reveal.")

    # Fallback to stillness if nothing matched
    if not selected_patterns and "stillness" in by_id:
        selected_patterns.append(by_id["stillness"])
        rationale.append("Fallback to 'stillness'.")

    return {
        "engine": "animejs-v4-with-css-fallback",
        "engineCompatibility": "Anime.js v4.x official runtime target; native CSS fallback when library is not loaded",
        "primaryPattern": selected_patterns[0]["id"] if selected_patterns else "stillness",
        "patterns": selected_patterns,
        "reducedMotionBehavior": "instant",
        "rationale": " ".join(rationale),
        "tokens": {
            "easeOut": "cubic-bezier(0.22, 1, 0.36, 1)",
            "easeExpo": "cubic-bezier(0.16, 1, 0.3, 1)",
            "easeSoft": "cubic-bezier(0.33, 1, 0.68, 1)",
            "easeExit": "cubic-bezier(0.55, 0.055, 0.675, 0.19)",
            "durationRevealMs": 800,
            "durationHeroMs": 1100,
            "staggerLineMs": 110
        }
    }


def generate_motion_runtime_script(motion_plan: Dict[str, Any]) -> str:
    """Generate inline JavaScript to initialize the motion adapter in generated web pages."""
    plan_json = json.dumps(motion_plan, indent=2)
    return f"""
    // Atlas Motion Adapter Runtime Integration
    (function() {{
      const motionPlan = {plan_json};
      
      function runMotion() {{
        if (typeof AtlasMotionAdapter === 'undefined') {{
          // Graceful fallback if adapter script failed to load
          document.querySelectorAll('.lines [data-line], .hero h1 [data-line]').forEach(el => {{
            el.style.transform = 'none';
            el.style.opacity = '1';
          }});
          return;
        }}
        
        const adapter = new AtlasMotionAdapter();
        if (motionPlan.patterns && motionPlan.patterns.length > 0) {{
          motionPlan.patterns.forEach(spec => {{
            adapter.execute(spec);
          }});
        }}
        window.__atlasMotionAdapterInstance = adapter;
      }}
      
      if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', runMotion);
      }} else {{
        runMotion();
      }}
    }})();
"""

