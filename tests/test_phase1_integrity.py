#!/usr/bin/env python3
"""Phase 1 End-to-End Integrity and Verification Test Suite."""
import json
import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WORKSPACE_ROOT = os.path.abspath(os.path.join(ROOT_DIR, ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data")
TOOLS_DIR = os.path.join(ROOT_DIR, "tools")
sys.path.insert(0, TOOLS_DIR)

from validate_library import ValidationReport, validate_directory


class TestPhase1Integrity(unittest.TestCase):
    def test_all_normalized_datasets_pass_validation(self):
        report = ValidationReport()
        validate_directory(DATA_DIR, report)
        self.assertTrue(report.is_valid, f"Validation errors: {report.errors}")
        self.assertEqual(len(report.errors), 0)
        self.assertEqual(report.items_checked, 620)
        self.assertEqual(report.files_checked, 6)

    def test_source_mapping_integrity(self):
        map_path = os.path.join(DATA_DIR, "source-map.json")
        self.assertTrue(os.path.isfile(map_path), "source-map.json must exist")
        with open(map_path, "r", encoding="utf-8") as f:
            mapping = json.load(f)
        self.assertEqual(len(mapping), 620, f"Expected 620 mappings, got {len(mapping)}")

        for entry in mapping:
            self.assertIn("normalized_id", entry)
            self.assertIn("source_project", entry)
            self.assertIn("source_file", entry)
            self.assertIn("source_id", entry)
            self.assertIn("target_dataset", entry)
            self.assertIn(entry["source_project"], ["taste-skill", "atlas-frontend-design", "project-atlas-v0.2.0-alpha"])

    def test_count_reconciliation(self):
        expected_counts = {
            "art-directions.json": 20,
            "compositions.json": 293,  # 50 Atlas + 58 Taste heroes + 185 Taste sections
            "palettes.json": 56,
            "typography.json": 44,
            "sites.json": 202,
            "app-shells.json": 5
        }
        actual_total = 0
        for filename, expected in expected_counts.items():
            filepath = os.path.join(DATA_DIR, filename)
            self.assertTrue(os.path.isfile(filepath), f"Missing dataset: {filename}")
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertEqual(data.get("item_count"), expected, f"Item count mismatch in {filename}")
            self.assertEqual(len(data.get("items", [])), expected, f"Actual items length mismatch in {filename}")
            actual_total += expected

        self.assertEqual(actual_total, 620)

    def test_manifest_syntax_and_structure(self):
        manifests = [
            os.path.join(ROOT_DIR, ".claude-plugin", "marketplace.json"),
            os.path.join(ROOT_DIR, ".codex-plugin", "plugin.json"),
            os.path.join(ROOT_DIR, ".agents", "plugins", "marketplace.json"),
            os.path.join(ROOT_DIR, "assets", "manifest.json")
        ]
        for mpath in manifests:
            self.assertTrue(os.path.isfile(mpath), f"Manifest file missing: {mpath}")
            with open(mpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertIsInstance(data, dict, f"Manifest {mpath} must be a JSON object")
            self.assertTrue("name" in data or "version" in data, f"Manifest {mpath} missing name/version")

    def test_source_repositories_remain_unmodified(self):
        protected_sources = [
            os.path.join(WORKSPACE_ROOT, "taste-skill"),
            os.path.join(WORKSPACE_ROOT, "atlas-frontend-design"),
            os.path.join(WORKSPACE_ROOT, "project-atlas-v0.2.0-alpha"),
            os.path.join(WORKSPACE_ROOT, ".taste-skill")
        ]
        for src in protected_sources:
            self.assertTrue(os.path.isdir(src), f"Protected source directory missing: {src}")


if __name__ == "__main__":
    unittest.main()

