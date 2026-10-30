#!/usr/bin/env python3
"""Atlas Composite Library Validator.

Offline, zero-dependency validator for the Atlas composite design library.
Validates structural integrity, ID uniqueness, schema compliance, and
complete source provenance.

Usage:
  py tools/validate_library.py data/compositions.json
  py tools/validate_library.py --dir data/
  py tools/validate_library.py <file.json> --json report.json
"""
import argparse
import json
import os
import re
import sys

ID_PATTERN = re.compile(r"^[a-z0-9_:-]+$")
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
VALID_LAYERS = {"art_direction", "composition", "palette", "typography", "site", "app_shell"}
VALID_PROJECTS = {"taste-skill", "atlas-frontend-design", "project-atlas-v0.2.0-alpha"}
VALID_PAGE_TYPES = {"marketing", "editorial", "app", "all"}
VALID_DENSITIES = {"low", "med", "high", None}


class ValidationReport:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.files_checked = 0
        self.items_checked = 0

    def add_error(self, file_path, item_id, message):
        self.errors.append({
            "severity": "ERROR",
            "file": os.path.basename(file_path),
            "item_id": item_id or "ROOT",
            "message": message
        })

    def add_warning(self, file_path, item_id, message):
        self.warnings.append({
            "severity": "WARNING",
            "file": os.path.basename(file_path),
            "item_id": item_id or "ROOT",
            "message": message
        })

    @property
    def is_valid(self):
        return len(self.errors) == 0

    def to_dict(self):
        return {
            "valid": self.is_valid,
            "files_checked": self.files_checked,
            "items_checked": self.items_checked,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings
        }


def validate_file(file_path, report, known_ids=None):
    """Validates a single composite JSON file."""
    if not os.path.isfile(file_path):
        report.add_error(file_path, None, f"File does not exist: {file_path}")
        return

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        report.add_error(file_path, None, f"JSON parse failure: {str(e)}")
        return

    report.files_checked += 1

    if not isinstance(data, dict):
        report.add_error(file_path, None, "Root data structure must be a JSON object")
        return

    # Check root fields
    version = data.get("version")
    if not version or not isinstance(version, str) or not VERSION_PATTERN.match(version):
        report.add_error(file_path, None, f"Invalid or missing root 'version': {version}")

    schema_type = data.get("schema_type")
    if not schema_type or not isinstance(schema_type, str):
        report.add_error(file_path, None, f"Missing or invalid root 'schema_type': {schema_type}")

    items = data.get("items")
    if not isinstance(items, list):
        report.add_error(file_path, None, "Missing or non-array root 'items'")
        return

    expected_count = data.get("item_count")
    if expected_count is None or not isinstance(expected_count, int):
        report.add_error(file_path, None, "Missing or non-integer root 'item_count' (must represent number of records in this file)")
    elif expected_count != len(items):
        report.add_error(file_path, None, f"item_count ({expected_count}) does not match actual items length ({len(items)})")

    local_ids = set()

    for idx, item in enumerate(items):
        report.items_checked += 1
        if not isinstance(item, dict):
            report.add_error(file_path, f"item[{idx}]", "Item must be a JSON object")
            continue

        item_id = item.get("id")
        if not item_id or not isinstance(item_id, str):
            report.add_error(file_path, f"item[{idx}]", "Item missing required string 'id'")
            continue

        if not ID_PATTERN.match(item_id):
            report.add_error(file_path, item_id, f"Item ID format invalid: '{item_id}'")

        if item_id in local_ids:
            report.add_error(file_path, item_id, f"Duplicate ID detected in file: '{item_id}'")
        local_ids.add(item_id)

        if known_ids is not None:
            if item_id in known_ids:
                report.add_error(file_path, item_id, f"Global ID collision across datasets: '{item_id}'")
            known_ids.add(item_id)

        # Name
        name = item.get("name")
        if not name or not isinstance(name, str):
            report.add_error(file_path, item_id, "Missing or empty required field 'name'")

        # Layer
        layer = item.get("layer")
        if not layer or layer not in VALID_LAYERS:
            report.add_error(file_path, item_id, f"Invalid 'layer': '{layer}'. Allowed: {sorted(VALID_LAYERS)}")

        # Provenance verification
        prov = item.get("provenance")
        if not isinstance(prov, dict):
            report.add_error(file_path, item_id, "Missing required 'provenance' object")
        else:
            proj = prov.get("source_project")
            if not proj or proj not in VALID_PROJECTS:
                report.add_error(file_path, item_id, f"Invalid provenance source_project: '{proj}'")
            if not prov.get("source_file"):
                report.add_error(file_path, item_id, "Missing provenance source_file")
            if not prov.get("source_id"):
                report.add_error(file_path, item_id, "Missing provenance source_id")
            if not prov.get("license"):
                report.add_error(file_path, item_id, "Missing required 'license' in provenance")
            attr = prov.get("attribution")
            if not attr or not isinstance(attr, str) or not attr.strip():
                report.add_error(file_path, item_id, "Missing or empty required field 'attribution' in provenance")

        # Composition-specific checks
        if layer == "composition" or item.get("page_types") is not None:
            page_types = item.get("page_types")
            if page_types is not None:
                if not isinstance(page_types, list):
                    report.add_error(file_path, item_id, "'page_types' must be a list")
                else:
                    for pt in page_types:
                        if pt not in VALID_PAGE_TYPES:
                            report.add_error(file_path, item_id, f"Invalid page_type: '{pt}'")

        if layer == "composition" or item.get("density") is not None:
            density = item.get("density")
            if density not in VALID_DENSITIES:
                report.add_error(file_path, item_id, f"Invalid density: '{density}'")

        if layer == "composition" or item.get("requires") is not None:
            req = item.get("requires")
            if req is not None and not isinstance(req, dict):
                report.add_error(file_path, item_id, "'requires' must be an object")

        # Reference consistency (incompatible / related symmetry & format)
        incompat = item.get("incompatible")
        if incompat and isinstance(incompat, list):
            for ref_id in incompat:
                if not isinstance(ref_id, str) or not ID_PATTERN.match(ref_id):
                    report.add_warning(file_path, item_id, f"Invalid reference format in incompatible: '{ref_id}'")


def validate_directory(dir_path, report):
    """Validates all JSON files in a data directory."""
    known_ids = set()
    if not os.path.isdir(dir_path):
        report.add_error(dir_path, None, f"Directory does not exist: {dir_path}")
        return

    for fname in sorted(os.listdir(dir_path)):
        if fname.endswith(".json") and fname != "source-map.json":
            fpath = os.path.join(dir_path, fname)
            validate_file(fpath, report, known_ids=known_ids)


def main():
    parser = argparse.ArgumentParser(description="Validate Atlas composite design library files.")
    parser.add_argument("target", nargs="?", default=None, help="JSON file or directory to validate")
    parser.add_argument("--dir", default=None, help="Validate all JSON datasets in this directory")
    parser.add_argument("--json", dest="json_out", default=None, help="Save machine-readable JSON report")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    args = parser.parse_args()

    report = ValidationReport()
    target_dir = args.dir or (args.target if args.target and os.path.isdir(args.target) else None)
    target_file = args.target if args.target and os.path.isfile(args.target) else None

    if target_dir:
        validate_directory(target_dir, report)
    elif target_file:
        validate_file(target_file, report)
    else:
        # Default fallback to data/ if present
        default_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        if os.path.isdir(default_dir):
            validate_directory(default_dir, report)
        else:
            parser.print_help()
            sys.exit(2)

    # Print human summary
    status_str = "PASS" if report.is_valid else "FAIL"
    print(f"\n[{status_str}] Atlas Composite Library Validation Summary")
    print(f"Files checked : {report.files_checked}")
    print(f"Items checked : {report.items_checked}")
    print(f"Errors        : {len(report.errors)}")
    print(f"Warnings      : {len(report.warnings)}")

    if report.errors:
        print("\n--- Hard Errors ---")
        for err in report.errors[:20]:
            print(f"  [ERROR] {err['file']} ({err['item_id']}): {err['message']}")
        if len(report.errors) > 20:
            print(f"  ... and {len(report.errors) - 20} more errors.")

    if report.warnings:
        print("\n--- Warnings ---")
        for warn in report.warnings[:10]:
            print(f"  [WARN] {warn['file']} ({warn['item_id']}): {warn['message']}")

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as jf:
            json.dump(report.to_dict(), jf, indent=2)
        print(f"\nMachine-readable report written to: {args.json_out}")

    exit_code = 0 if report.is_valid and (not args.strict or len(report.warnings) == 0) else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
