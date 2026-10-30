#!/usr/bin/env python3
"""Atlas Phase 5 Test Suite — Knowledge Manifest & Source Verification.

Validates that the Taste Skill knowledge package manifest is complete,
conforms to schema, and accurately classifies all source artifacts.
"""
import json
import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

MANIFEST_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "knowledge", "taste", "manifest.json")
)
SCHEMA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "knowledge", "taste", "schemas", "knowledge-manifest.schema.json")
)
LICENSE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "knowledge", "taste", "LICENSE.taste-skill")
)


class TestTasteKnowledgeManifest(unittest.TestCase):

    def setUp(self):
        self.assertTrue(os.path.exists(MANIFEST_PATH), f"Manifest missing at {MANIFEST_PATH}")
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            self.manifest = json.load(f)

    def test_manifest_metadata(self):
        self.assertEqual(self.manifest.get("schemaVersion"), "1.0.0")
        self.assertEqual(self.manifest.get("totalSourceFiles"), 39)
        self.assertGreater(self.manifest.get("totalSourceBytes"), 2000000)
        self.assertEqual(self.manifest.get("licenseSource"), "taste-skill/LICENSE")

    def test_all_39_source_files_plus_license_present(self):
        files = self.manifest.get("files", [])
        self.assertEqual(len(files), 40)  # 39 source files + 1 parent LICENSE
        paths = {f["path"] for f in files}
        self.assertIn("SKILL.md", paths)
        self.assertIn("README.md", paths)
        self.assertIn("library/motions.json", paths)
        self.assertIn("library/photos.json", paths)
        self.assertIn("references/motion.md", paths)
        self.assertIn("references/tells.md", paths)
        self.assertIn("scripts/lib/rules.mjs", paths)
        self.assertIn("scripts/inspect.mjs", paths)
        self.assertIn("../LICENSE", paths)

    def test_provenance_and_licensing(self):
        for entry in self.manifest.get("files", []):
            self.assertIn("category", entry)
            self.assertIn("action", entry)
            self.assertIn(entry["action"], {"copied", "adapted", "reference-only", "excluded"})
            self.assertIn("license", entry)
            self.assertTrue(len(entry["sha256"]) == 64, f"Invalid SHA-256 for {entry['path']}")
            self.assertTrue(len(entry["rationale"]) > 10, f"Missing rationale for {entry['path']}")

    def test_license_file_copied(self):
        self.assertTrue(os.path.exists(LICENSE_PATH), f"LICENSE.taste-skill missing at {LICENSE_PATH}")
        with open(LICENSE_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("MIT License", content)
        self.assertIn("Copyright (c) 2026 Leonxlnx", content)


if __name__ == "__main__":
    unittest.main()
