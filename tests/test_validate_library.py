#!/usr/bin/env python3
"""Unit tests for Atlas composite library validator."""
import os
import subprocess
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIXTURES_DIR = os.path.join(ROOT_DIR, "tests", "fixtures")
TOOLS_DIR = os.path.join(ROOT_DIR, "tools")
sys.path.insert(0, TOOLS_DIR)

from validate_library import ValidationReport, validate_file


class TestLibraryValidator(unittest.TestCase):
    def setUp(self):
        self.report = ValidationReport()

    def test_valid_fixture_passes(self):
        path = os.path.join(FIXTURES_DIR, "valid_sample.json")
        validate_file(path, self.report)
        self.assertTrue(self.report.is_valid, f"Expected valid, got errors: {self.report.errors}")
        self.assertEqual(len(self.report.errors), 0)
        self.assertEqual(self.report.items_checked, 2)

    def test_missing_fields_fails(self):
        path = os.path.join(FIXTURES_DIR, "missing_fields.json")
        validate_file(path, self.report)
        self.assertFalse(self.report.is_valid)
        error_msgs = [e["message"] for e in self.report.errors]
        self.assertTrue(any("name" in m for m in error_msgs))

    def test_invalid_types_and_enums_fails(self):
        path = os.path.join(FIXTURES_DIR, "invalid_types.json")
        validate_file(path, self.report)
        self.assertFalse(self.report.is_valid)
        error_msgs = [e["message"] for e in self.report.errors]
        self.assertTrue(any("Invalid 'layer'" in m for m in error_msgs))
        self.assertTrue(any("Invalid provenance source_project" in m for m in error_msgs))
        self.assertTrue(any("Invalid page_type" in m for m in error_msgs))

    def test_duplicate_ids_fails(self):
        path = os.path.join(FIXTURES_DIR, "duplicate_ids.json")
        validate_file(path, self.report)
        self.assertFalse(self.report.is_valid)
        error_msgs = [e["message"] for e in self.report.errors]
        self.assertTrue(any("Duplicate ID" in m for m in error_msgs))

    def test_incomplete_provenance_fails(self):
        path = os.path.join(FIXTURES_DIR, "incomplete_provenance.json")
        validate_file(path, self.report)
        self.assertFalse(self.report.is_valid)
        error_msgs = [e["message"] for e in self.report.errors]
        self.assertTrue(any("source_file" in m for m in error_msgs))
        self.assertTrue(any("source_id" in m for m in error_msgs))

    def test_missing_attribution_fails(self):
        path = os.path.join(FIXTURES_DIR, "missing_attribution.json")
        validate_file(path, self.report)
        self.assertFalse(self.report.is_valid)
        error_msgs = [e["message"] for e in self.report.errors]
        self.assertTrue(any("attribution" in m for m in error_msgs), f"Expected attribution error, got: {error_msgs}")

    def test_empty_attribution_fails(self):
        path = os.path.join(FIXTURES_DIR, "empty_attribution.json")
        validate_file(path, self.report)
        self.assertFalse(self.report.is_valid)
        error_msgs = [e["message"] for e in self.report.errors]
        self.assertTrue(any("attribution" in m for m in error_msgs), f"Expected attribution error, got: {error_msgs}")

    def test_valid_attribution_passes(self):
        path = os.path.join(FIXTURES_DIR, "valid_sample.json")
        validate_file(path, self.report)
        error_msgs = [e["message"] for e in self.report.errors]
        self.assertFalse(any("attribution" in m for m in error_msgs))

    def test_item_count_matches_actual_items(self):
        path = os.path.join(FIXTURES_DIR, "valid_sample.json")
        validate_file(path, self.report)
        error_msgs = [e["message"] for e in self.report.errors]
        self.assertFalse(any("item_count" in m for m in error_msgs))

    def test_item_count_mismatch_fails(self):
        path = os.path.join(FIXTURES_DIR, "item_count_mismatch.json")
        validate_file(path, self.report)
        self.assertFalse(self.report.is_valid)
        error_msgs = [e["message"] for e in self.report.errors]
        self.assertTrue(any("item_count" in m for m in error_msgs), f"Expected item_count error, got: {error_msgs}")

    def test_invalid_version_fails(self):
        path = os.path.join(FIXTURES_DIR, "invalid_version.json")
        validate_file(path, self.report)
        self.assertFalse(self.report.is_valid)
        error_msgs = [e["message"] for e in self.report.errors]
        self.assertTrue(any("version" in m for m in error_msgs))

    def test_cli_execution_and_exit_codes(self):
        script = os.path.join(TOOLS_DIR, "validate_library.py")
        valid_path = os.path.join(FIXTURES_DIR, "valid_sample.json")
        invalid_path = os.path.join(FIXTURES_DIR, "missing_fields.json")

        cmd_valid = [sys.executable, script, valid_path]
        res_valid = subprocess.run(cmd_valid, capture_output=True, text=True)
        self.assertEqual(res_valid.returncode, 0, f"Expected 0, got {res_valid.returncode}: {res_valid.stdout}")
        self.assertIn("[PASS]", res_valid.stdout)

        cmd_invalid = [sys.executable, script, invalid_path]
        res_invalid = subprocess.run(cmd_invalid, capture_output=True, text=True)
        self.assertEqual(res_invalid.returncode, 1)
        self.assertIn("[FAIL]", res_invalid.stdout)


if __name__ == "__main__":
    unittest.main()
