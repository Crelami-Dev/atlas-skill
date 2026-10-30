#!/usr/bin/env python3
"""Atlas Runtime Engine — Canonical Library Loader.

Loads, validates, and indexes the canonical design library files.
Preserves source data immutability and provides fast indexed access.
Zero-dependency, Python 3.9+ standard library.
"""
import copy
import importlib
import json
import os
import sys
from types import MappingProxyType
from typing import Any, Dict, List, Optional, Set, Tuple

# Import validator from tools directory
TOOLS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools"))
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

try:
    from tools.validate_library import ValidationReport, validate_file
except ImportError:
    try:
        _val_mod = importlib.import_module("validate_library")
        ValidationReport = getattr(_val_mod, "ValidationReport", None)
        validate_file = getattr(_val_mod, "validate_file", None)
    except Exception:
        # Fallback minimal stub if tools directory is moved
        ValidationReport = None
        validate_file = None

from .contracts import (
    ERR_LIBRARY_MISSING,
    ERR_SCHEMA_VIOLATION,
    LIBRARY_VERSION,
    ContractValidationError,
    Diagnostic,
)

EXPECTED_FILES = {
    "art-directions.json": {"layer": "art_direction", "expected_count": 20},
    "compositions.json": {"layer": "composition", "expected_count": 293},
    "palettes.json": {"layer": "palette", "expected_count": 56},
    "typography.json": {"layer": "typography", "expected_count": 44},
    "sites.json": {"layer": "site", "expected_count": 202},
    "app-shells.json": {"layer": "app_shell", "expected_count": 5},
}

OPTIONAL_FILES = {
    "source-map.json": {"expected_count": 620}
}


def freeze_deep(obj: Any) -> Any:
    """Recursively freeze dicts to MappingProxyType, lists to tuples, sets to frozensets."""
    if isinstance(obj, dict):
        return MappingProxyType({k: freeze_deep(v) for k, v in obj.items()})
    elif isinstance(obj, list):
        return tuple(freeze_deep(v) for v in obj)
    elif isinstance(obj, set):
        return frozenset(freeze_deep(v) for v in obj)
    return obj


class CanonicalLibrary:
    """Immutable, indexed in-memory representation of the Atlas Canonical Library."""

    def __init__(
        self,
        version: str,
        art_directions: List[Dict[str, Any]],
        compositions: List[Dict[str, Any]],
        palettes: List[Dict[str, Any]],
        typography: List[Dict[str, Any]],
        sites: List[Dict[str, Any]],
        app_shells: List[Dict[str, Any]],
        source_map: Optional[List[Dict[str, Any]]] = None,
        motions: Optional[List[Dict[str, Any]]] = None,
        data_dir: Optional[str] = None
    ):
        self._version = version
        self._data_dir = data_dir
        self._art_directions = tuple(freeze_deep(item) for item in copy.deepcopy(art_directions))
        self._compositions = tuple(freeze_deep(item) for item in copy.deepcopy(compositions))
        self._palettes = tuple(freeze_deep(item) for item in copy.deepcopy(palettes))
        self._typography = tuple(freeze_deep(item) for item in copy.deepcopy(typography))
        self._sites = tuple(freeze_deep(item) for item in copy.deepcopy(sites))
        self._app_shells = tuple(freeze_deep(item) for item in copy.deepcopy(app_shells))
        self._source_map = tuple(freeze_deep(item) for item in copy.deepcopy(source_map or []))
        self._motions = tuple(freeze_deep(item) for item in copy.deepcopy(motions or []))

        # Indexing for O(1) retrieval
        self._by_id: Dict[str, Dict[str, Any]] = {}
        self._compositions_by_family: Dict[str, List[Dict[str, Any]]] = {}
        self._art_directions_by_id: Dict[str, Dict[str, Any]] = {}
        self._palettes_by_id: Dict[str, Dict[str, Any]] = {}
        self._typography_by_id: Dict[str, Dict[str, Any]] = {}
        self._app_shells_by_id: Dict[str, Dict[str, Any]] = {}
        self._motions_by_id: Dict[str, Dict[str, Any]] = {}

        # Populate indexes
        for group in (self._art_directions, self._compositions, self._palettes,
                      self._typography, self._sites, self._app_shells, self._motions):
            for item in group:
                self._by_id[item["id"]] = item

        for ad in self._art_directions:
            self._art_directions_by_id[ad["id"]] = ad

        for c in self._compositions:
            fam = c.get("family", "unknown")
            self._compositions_by_family.setdefault(fam, []).append(c)

        for p in self._palettes:
            self._palettes_by_id[p["id"]] = p

        for t in self._typography:
            self._typography_by_id[t["id"]] = t

        for s in self._app_shells:
            self._app_shells_by_id[s["id"]] = s

        for m in self._motions:
            self._motions_by_id[m["id"]] = m

    @property
    def version(self) -> str:
        return self._version

    @property
    def data_dir(self) -> Optional[str]:
        return self._data_dir

    @property
    def art_directions(self) -> Tuple[Dict[str, Any], ...]:
        return self._art_directions

    @property
    def compositions(self) -> Tuple[Dict[str, Any], ...]:
        return self._compositions

    @property
    def palettes(self) -> Tuple[Dict[str, Any], ...]:
        return self._palettes

    @property
    def typography(self) -> Tuple[Dict[str, Any], ...]:
        return self._typography

    @property
    def sites(self) -> Tuple[Dict[str, Any], ...]:
        return self._sites

    @property
    def app_shells(self) -> Tuple[Dict[str, Any], ...]:
        return self._app_shells

    @property
    def motions(self) -> Tuple[Dict[str, Any], ...]:
        return self._motions

    def get_motion_by_id(self, motion_id: str) -> Optional[Dict[str, Any]]:
        return self._motions_by_id.get(motion_id)

    @property
    def source_map(self) -> Tuple[Dict[str, Any], ...]:
        return self._source_map

    @property
    def total_records(self) -> int:
        return (
            len(self._art_directions) +
            len(self._compositions) +
            len(self._palettes) +
            len(self._typography) +
            len(self._sites) +
            len(self._app_shells)
        )

    def get_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve any record by normalized ID. Returns an immutable proxy."""
        item = self._by_id.get(item_id)
        if item is None:
            return None
        return MappingProxyType(item)  # type: ignore

    def get_compositions_by_family(self, family: str) -> List[Dict[str, Any]]:
        """Return all composition items for a given family slot."""
        return list(self._compositions_by_family.get(family, []))

    def get_art_direction(self, ad_id: str) -> Optional[Dict[str, Any]]:
        item = self._art_directions_by_id.get(ad_id)
        return MappingProxyType(item) if item else None  # type: ignore

    def get_palette(self, pal_id: str) -> Optional[Dict[str, Any]]:
        item = self._palettes_by_id.get(pal_id)
        return MappingProxyType(item) if item else None  # type: ignore

    def get_typography(self, typo_id: str) -> Optional[Dict[str, Any]]:
        item = self._typography_by_id.get(typo_id)
        return MappingProxyType(item) if item else None  # type: ignore

    def get_app_shell(self, shell_id: str) -> Optional[Dict[str, Any]]:
        item = self._app_shells_by_id.get(shell_id)
        return MappingProxyType(item) if item else None  # type: ignore


def default_data_dir() -> str:
    """Return the absolute path to atlas-skill/data predictable regardless of cwd."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))


def load_library(
    data_dir: Optional[str] = None,
    validate: bool = False,
    diagnostics: Optional[List[Diagnostic]] = None
) -> CanonicalLibrary:
    """Load canonical datasets from data directory into an immutable CanonicalLibrary.
    
    Args:
        data_dir: Directory containing canonical JSON datasets. Defaults to atlas-skill/data.
        validate: If True, executes the full Phase 1 validator before loading.
        diagnostics: Optional list to receive diagnostics.
        
    Raises:
        ContractValidationError: If required files are missing or schema checks fail.
    """
    target_dir = os.path.abspath(data_dir or default_data_dir())

    if not os.path.isdir(target_dir):
        raise ContractValidationError(
            ERR_LIBRARY_MISSING,
            f"Canonical data directory not found: '{target_dir}'",
            target=target_dir
        )

    # If validate flag is requested and validator is available, run it
    if validate and validate_file and ValidationReport:
        report = ValidationReport()
        for fname in EXPECTED_FILES:
            fpath = os.path.join(target_dir, fname)
            if os.path.isfile(fpath):
                validate_file(fpath, report)
            else:
                report.add_error(fpath, None, f"Required dataset file missing: {fname}")
        if not report.is_valid:
            first_err = report.errors[0]
            raise ContractValidationError(
                ERR_SCHEMA_VIOLATION,
                f"Validation failed for {first_err['file']}: {first_err['message']}",
                target=first_err['file']
            )

    # 1. Pre-flight check: ensure ALL expected canonical dataset files exist
    for fname in EXPECTED_FILES:
        fpath = os.path.join(target_dir, fname)
        if not os.path.isfile(fpath):
            raise ContractValidationError(
                ERR_LIBRARY_MISSING,
                f"Missing required canonical dataset: '{fname}' in '{target_dir}'",
                target=fname
            )

    loaded_groups: Dict[str, List[Dict[str, Any]]] = {}
    detected_version = LIBRARY_VERSION
    seen_ids: Set[str] = set()

    for fname, meta in EXPECTED_FILES.items():
        fpath = os.path.join(target_dir, fname)

        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = json.load(f)
        except json.JSONDecodeError as e:
            raise ContractValidationError(
                ERR_SCHEMA_VIOLATION,
                f"Malformed JSON in dataset '{fname}': {e}",
                target=fname
            )

        if not isinstance(content, dict):
            raise ContractValidationError(
                ERR_SCHEMA_VIOLATION,
                f"Dataset '{fname}' root must be a JSON object",
                target=fname
            )

        # Validate item_count equality
        items = content.get("items")
        if not isinstance(items, list):
            raise ContractValidationError(
                ERR_SCHEMA_VIOLATION,
                f"Dataset '{fname}' missing 'items' array",
                target=fname
            )

        item_count = content.get("item_count")
        if item_count != len(items):
            raise ContractValidationError(
                ERR_SCHEMA_VIOLATION,
                f"Dataset '{fname}' item_count mismatch: header declared {item_count}, found {len(items)} items",
                target=fname
            )

        if meta["expected_count"] is not None and len(items) != meta["expected_count"]:
            raise ContractValidationError(
                ERR_SCHEMA_VIOLATION,
                f"Dataset '{fname}' record count mismatch: expected {meta['expected_count']}, got {len(items)}",
                target=fname
            )

        # Check duplicate IDs and minimal structure
        for item in items:
            if not isinstance(item, dict):
                raise ContractValidationError(
                    ERR_SCHEMA_VIOLATION,
                    f"Dataset '{fname}' contains non-object item",
                    target=fname
                )
            iid = item.get("id")
            if not iid or not isinstance(iid, str):
                raise ContractValidationError(
                    ERR_SCHEMA_VIOLATION,
                    f"Dataset '{fname}' contains item with missing or invalid 'id'",
                    target=fname
                )
            if iid in seen_ids:
                raise ContractValidationError(
                    ERR_SCHEMA_VIOLATION,
                    f"Duplicate item ID '{iid}' detected in dataset '{fname}'",
                    target=iid
                )
            seen_ids.add(iid)

        loaded_groups[fname] = items
        if content.get("version"):
            detected_version = content["version"]

    # Optional source-map.json
    source_map: List[Dict[str, Any]] = []
    map_path = os.path.join(target_dir, "source-map.json")
    if os.path.isfile(map_path):
        try:
            with open(map_path, "r", encoding="utf-8") as f:
                source_map = json.load(f)
        except Exception:
            source_map = []

    # Optional motions.json (from target_dir or knowledge/taste/library/motions.json)
    loaded_motions: List[Dict[str, Any]] = []
    motions_path = os.path.join(target_dir, "motions.json")
    if not os.path.isfile(motions_path):
        motions_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "knowledge", "taste", "library", "motions.json")
        )
    if os.path.isfile(motions_path):
        try:
            with open(motions_path, "r", encoding="utf-8") as f:
                m_content = json.load(f)
                if isinstance(m_content, list):
                    loaded_motions = m_content
                elif isinstance(m_content, dict) and "items" in m_content:
                    loaded_motions = m_content["items"]
        except Exception:
            loaded_motions = []

    return CanonicalLibrary(
        version=detected_version,
        art_directions=loaded_groups["art-directions.json"],
        compositions=loaded_groups["compositions.json"],
        palettes=loaded_groups["palettes.json"],
        typography=loaded_groups["typography.json"],
        sites=loaded_groups["sites.json"],
        app_shells=loaded_groups["app-shells.json"],
        source_map=source_map,
        motions=loaded_motions,
        data_dir=target_dir
    )
