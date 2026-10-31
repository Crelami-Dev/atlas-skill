#!/usr/bin/env python3
"""Atlas Runtime Engine — Data Contracts and Schemas.

Defines the normalized ProductBrief, DesignPlan, and diagnostic data models,
with validation logic and stable error codes.
Zero-dependency, Python 3.9+ standard library.
"""
import hashlib
import json
import re
from typing import Any, Dict, List, Optional, Tuple, Union

RUNTIME_VERSION = "2.0.0"
LIBRARY_VERSION = "2.0.0"

# Error and Warning Diagnostic Codes
ERR_INVALID_PAGE_TYPE = "ERR_INVALID_PAGE_TYPE"
ERR_INVALID_DENSITY = "ERR_INVALID_DENSITY"
ERR_INVALID_WEIGHTS = "ERR_INVALID_WEIGHTS"
ERR_EMPTY_BRIEF = "ERR_EMPTY_BRIEF"
ERR_INVALID_TYPE = "ERR_INVALID_TYPE"
ERR_HARD_CONSTRAINT_UNSATISFIED = "ERR_HARD_CONSTRAINT_UNSATISFIED"
ERR_LIBRARY_MISSING = "ERR_LIBRARY_MISSING"
ERR_SCHEMA_VIOLATION = "ERR_SCHEMA_VIOLATION"

WARN_LOW_FIT_SCORE = "WARN_LOW_FIT_SCORE"
WARN_FALLBACK_APPLIED = "WARN_FALLBACK_APPLIED"
WARN_UNRESOLVED_SLOT = "WARN_UNRESOLVED_SLOT"
WARN_UNKNOWN_ASSET_TYPE = "WARN_UNKNOWN_ASSET_TYPE"
WARN_MISSING_OPTIONAL_DATA = "WARN_MISSING_OPTIONAL_DATA"

VALID_PAGE_TYPES = {"marketing", "editorial", "app"}
VALID_DENSITIES = {"low", "med", "high"}
VALID_ASSETS = {
    "photo", "video", "illustration", "product_ui", "data", "quote",
    "logo_proof", "icon", "vector",
    "content:comparison_facts", "content:dated_events", "content:plans",
    "content:steps", "content:faq"
}

DEFAULT_SLOTS = {
    "marketing": [
        "nav", "hero", "social_proof", "features", "how-it-works",
        "pricing", "faq", "cta", "footer"
    ],
    "editorial": [
        "nav", "hero", "story", "social_proof", "cta", "footer"
    ],
    "app": [
        "nav", "app_shell", "app_data", "app_form", "footer"
    ]
}

DEFAULT_SCORING_WEIGHTS = {
    "category": 1.0,
    "art_direction_synergy": 1.5,
    "tones": 1.0,
    "density": 0.8,
    "goals": 1.0,
    "conventional": 1.5,
    "sequence_pairing": 0.8,
    "sequence_repetition": 1.0
}


class ContractValidationError(ValueError):
    """Raised when an input contract fails validation."""
    def __init__(self, code: str, message: str, target: Optional[str] = None):
        super().__init__(f"[{code}] {message}" + (f" (target: {target})" if target else ""))
        self.code = code
        self.message = message
        self.target = target

    def to_diagnostic(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "severity": "ERROR",
            "message": self.message,
            "target": self.target
        }


class Diagnostic:
    """Represents an actionable warning or informational finding."""
    def __init__(self, code: str, severity: str, message: str, target: Optional[str] = None):
        self.code = code
        self.severity = severity  # "INFO", "WARNING", "ERROR"
        self.message = message
        self.target = target

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "target": self.target
        }


class ProductBrief:
    """Normalized internal representation of a product/project brief."""
    def __init__(
        self,
        project_name: str = "Untitled Project",
        page_type: str = "marketing",
        category: str = "*",
        audience: Optional[str] = None,
        primary_task: Optional[str] = None,
        goals: Optional[List[str]] = None,
        tones: Optional[List[str]] = None,
        density: str = "med",
        assets: Optional[List[str]] = None,
        slots: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
        pricing_tiers: Optional[List[Dict[str, Any]]] = None,
        prefer_conventional: bool = False,
        explicit_constraints: Optional[Dict[str, Any]] = None,
        scoring_weights: Optional[Dict[str, float]] = None
    ):
        self.project_name = project_name
        self.page_type = page_type
        self.category = category
        self.audience = audience
        self.primary_task = primary_task
        self.goals = list(goals or [])
        self.tones = list(tones or [])
        self.density = density
        self.assets = list(assets or [])
        self.exclude = list(exclude or [])
        self.pricing_tiers = list(pricing_tiers) if pricing_tiers else None
        if slots is not None:
            # 1. Explicit slots provided by brief: honor strictly, minus explicit exclude
            self.slots = [s for s in slots if s not in self.exclude]
        else:
            # 2. Intelligent category & page_type defaults when slots are unspecified
            base_slots = list(DEFAULT_SLOTS.get(page_type, []))
            non_pricing_categories = {
                "fashion", "luxury", "personal-portfolio", "studio-portfolio",
                "architecture", "culture", "art", "hospitality", "restaurant",
                "agency", "design", "creative"
            }
            if category.lower() in non_pricing_categories and "pricing" in base_slots:
                base_slots = [s for s in base_slots if s != "pricing"]
            self.slots = [s for s in base_slots if s not in self.exclude]
        self.prefer_conventional = bool(prefer_conventional)
        self.explicit_constraints = dict(explicit_constraints or {})
        
        # Merge scoring weights with defaults
        weights = dict(DEFAULT_SCORING_WEIGHTS)
        if scoring_weights:
            weights.update(scoring_weights)
        self.scoring_weights = weights

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_name": self.project_name,
            "page_type": self.page_type,
            "category": self.category,
            "audience": self.audience,
            "primary_task": self.primary_task,
            "goals": self.goals,
            "tones": self.tones,
            "density": self.density,
            "assets": self.assets,
            "slots": self.slots,
            "exclude": self.exclude,
            "pricing_tiers": self.pricing_tiers,
            "prefer_conventional": self.prefer_conventional,
            "explicit_constraints": self.explicit_constraints,
            "scoring_weights": self.scoring_weights
        }


def normalize_brief(raw: Union[Dict[str, Any], None], diagnostics: Optional[List[Diagnostic]] = None) -> ProductBrief:
    """Validate and normalize raw input data into a clean ProductBrief instance.
    
    Raises ContractValidationError on critical schema or validation errors.
    Appends warnings to diagnostics list when supplied.
    """
    if raw is None or not isinstance(raw, dict):
        raise ContractValidationError(ERR_EMPTY_BRIEF, "Brief must be a non-empty JSON object", target="brief")

    # 1. Project Name
    project_name = str(raw.get("project_name", "Untitled Project")).strip() or "Untitled Project"

    # 2. Page Type
    page_type = str(raw.get("page_type", "marketing")).strip().lower()
    if page_type not in VALID_PAGE_TYPES:
        raise ContractValidationError(
            ERR_INVALID_PAGE_TYPE,
            f"Invalid page_type '{page_type}'. Allowed: {sorted(VALID_PAGE_TYPES)}",
            target="page_type"
        )

    # 3. Category / Industry
    category = str(raw.get("category", "*")).strip().lower() or "*"

    # 4. Audience and Primary Task
    audience = raw.get("audience")
    if audience is not None:
        audience = str(audience).strip()

    primary_task = raw.get("primary_task")
    if primary_task is not None:
        primary_task = str(primary_task).strip()

    # 5. Goals
    raw_goals = raw.get("goals", [])
    if isinstance(raw_goals, str):
        goals = [g.strip().lower() for g in raw_goals.split(",") if g.strip()]
    elif isinstance(raw_goals, (list, tuple)):
        goals = [str(g).strip().lower() for g in raw_goals if str(g).strip()]
    else:
        raise ContractValidationError(ERR_INVALID_TYPE, "Field 'goals' must be a list or comma-separated string", target="goals")

    # 6. Tones
    raw_tones = raw.get("tones", [])
    if isinstance(raw_tones, str):
        tones = [t.strip().lower() for t in raw_tones.split(",") if t.strip()]
    elif isinstance(raw_tones, (list, tuple)):
        tones = [str(t).strip().lower() for t in raw_tones if str(t).strip()]
    else:
        raise ContractValidationError(ERR_INVALID_TYPE, "Field 'tones' must be a list or comma-separated string", target="tones")

    # 7. Density
    density = str(raw.get("density", "med")).strip().lower()
    if density not in VALID_DENSITIES:
        raise ContractValidationError(
            ERR_INVALID_DENSITY,
            f"Invalid density '{density}'. Allowed: {sorted(VALID_DENSITIES)}",
            target="density"
        )

    # 8. Assets
    raw_assets = raw.get("assets", [])
    if isinstance(raw_assets, str):
        assets = [a.strip() for a in raw_assets.split(",") if a.strip()]
    elif isinstance(raw_assets, (list, tuple)):
        assets = [str(a).strip() for a in raw_assets if str(a).strip()]
    else:
        raise ContractValidationError(ERR_INVALID_TYPE, "Field 'assets' must be a list or comma-separated string", target="assets")

    if diagnostics is not None:
        for a in assets:
            if a not in VALID_ASSETS and not a.startswith("content:"):
                diagnostics.append(Diagnostic(
                    WARN_UNKNOWN_ASSET_TYPE,
                    "WARNING",
                    f"Asset type '{a}' is not in canonical vocabulary; may limit matching patterns",
                    target="assets"
                ))

    # 9. Slots
    raw_slots = raw.get("slots")
    slots = None
    if raw_slots is not None:
        if isinstance(raw_slots, str):
            slots = [s.strip().lower() for s in raw_slots.split(",") if s.strip()]
        elif isinstance(raw_slots, (list, tuple)):
            slots = [str(s).strip().lower() for s in raw_slots if str(s).strip()]
        else:
            raise ContractValidationError(ERR_INVALID_TYPE, "Field 'slots' must be a list or comma-separated string", target="slots")

    # 10. Exclude
    raw_exclude = raw.get("exclude", [])
    if isinstance(raw_exclude, str):
        exclude = [e.strip() for e in raw_exclude.split(",") if e.strip()]
    elif isinstance(raw_exclude, (list, tuple)):
        exclude = [str(e).strip() for e in raw_exclude if str(e).strip()]
    else:
        raise ContractValidationError(ERR_INVALID_TYPE, "Field 'exclude' must be a list of IDs", target="exclude")

    # 11. Pricing Tiers (optional verified brief input)
    raw_pricing = raw.get("pricing_tiers")
    pricing_tiers = None
    if raw_pricing is not None and isinstance(raw_pricing, (list, tuple)):
        pricing_tiers = list(raw_pricing)

    # 12. Prefer Conventional
    prefer_conventional = bool(raw.get("prefer_conventional", False))

    # 13. Explicit Constraints
    explicit_constraints = raw.get("explicit_constraints", {})
    if not isinstance(explicit_constraints, dict):
        raise ContractValidationError(ERR_INVALID_TYPE, "Field 'explicit_constraints' must be a dictionary", target="explicit_constraints")

    # 14. Scoring Weights
    scoring_weights = raw.get("scoring_weights", {})
    if not isinstance(scoring_weights, dict):
        raise ContractValidationError(ERR_INVALID_TYPE, "Field 'scoring_weights' must be a dictionary", target="scoring_weights")
    for k, v in scoring_weights.items():
        if not isinstance(v, (int, float)) or v < 0:
            raise ContractValidationError(
                ERR_INVALID_WEIGHTS,
                f"Weight for '{k}' must be a non-negative number, got {v}",
                target=f"scoring_weights.{k}"
            )

    return ProductBrief(
        project_name=project_name,
        page_type=page_type,
        category=category,
        audience=audience,
        primary_task=primary_task,
        goals=goals,
        tones=tones,
        density=density,
        assets=assets,
        slots=slots,
        exclude=exclude,
        pricing_tiers=pricing_tiers,
        prefer_conventional=prefer_conventional,
        explicit_constraints=explicit_constraints,
        scoring_weights=scoring_weights
    )


def compute_plan_id(normalized_brief_dict: Dict[str, Any], library_version: str) -> str:
    """Compute a deterministic SHA-256 fingerprint from the normalized brief and library version."""
    payload = {
        "brief": normalized_brief_dict,
        "library_version": library_version,
        "runtime_version": RUNTIME_VERSION
    }
    canonical_repr = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical_repr.encode("utf-8")).hexdigest()[:16]

