#!/usr/bin/env python3
"""Atlas Runtime Engine — Unit Tests for Library Loading and Immutability."""
import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from runtime.contracts import (
    ContractValidationError,
    ERR_LIBRARY_MISSING,
    ERR_SCHEMA_VIOLATION,
)
from runtime.loader import (
    CanonicalLibrary,
    default_data_dir,
    load_library,
)


class TestLibraryLoader(unittest.TestCase):
    def setUp(self):
        self.data_dir = default_data_dir()

    def test_successful_canonical_loading(self):
        lib = load_library(self.data_dir)
        self.assertIsInstance(lib, CanonicalLibrary)
        self.assertEqual(lib.total_records, 620)
        self.assertEqual(len(lib.art_directions), 20)
        self.assertEqual(len(lib.compositions), 293)
        self.assertEqual(len(lib.palettes), 56)
        self.assertEqual(len(lib.typography), 44)
        self.assertEqual(len(lib.sites), 202)
        self.assertEqual(len(lib.app_shells), 5)
        self.assertEqual(lib.version, "2.0.0")

    def test_records_are_immutable(self):
        lib = load_library(self.data_dir)
        item = lib.get_by_id("atlas:nav-minimal-bar")
        self.assertIsNotNone(item)
        with self.assertRaises(TypeError):
            item["name"] = "mutation_attempt"

    def test_nested_records_and_arrays_are_deeply_immutable(self):
        lib = load_library(self.data_dir)
        item = lib.get_by_id("atlas:nav-minimal-bar")
        self.assertIsNotNone(item)
        # 1. Mutate nested dict
        with self.assertRaises(TypeError):
            item["requires"]["assets"] = ("fake",)
        # 2. Mutate nested tuple
        with self.assertRaises(AttributeError):
            item["requires"]["assets"].append("fake")
        # 3. Mutate array by index
        with self.assertRaises(TypeError):
            item["page_types"][0] = "corrupt"

    def test_missing_data_directory_fails(self):
        with self.assertRaises(ContractValidationError) as ctx:
            load_library(os.path.join(self.data_dir, "non_existent_subdir"))
        self.assertEqual(ctx.exception.code, ERR_LIBRARY_MISSING)

    def test_missing_required_dataset_file_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create incomplete data dir missing compositions.json
            with open(os.path.join(tmpdir, "art-directions.json"), "w", encoding="utf-8") as f:
                json.dump({"version": "2.0.0", "item_count": 0, "items": []}, f)
            with self.assertRaises(ContractValidationError) as ctx:
                load_library(tmpdir)
            self.assertEqual(ctx.exception.code, ERR_LIBRARY_MISSING)

    def test_malformed_json_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            for fname in ["art-directions.json", "compositions.json", "palettes.json", "typography.json", "sites.json", "app-shells.json"]:
                with open(os.path.join(tmpdir, fname), "w", encoding="utf-8") as f:
                    if fname == "compositions.json":
                        f.write("{ invalid json content ...")
                    else:
                        json.dump({"version": "2.0.0", "item_count": 0, "items": []}, f)
            with self.assertRaises(ContractValidationError) as ctx:
                load_library(tmpdir)
            self.assertEqual(ctx.exception.code, ERR_SCHEMA_VIOLATION)

    def test_duplicate_id_in_dataset_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create directory with duplicate ID in art directions
            ad_items = [
                {"id": "art-dir:sample", "layer": "art_direction", "name": "One", "provenance": {"source_project": "taste-skill", "source_file": "a", "source_id": "1", "license": "MIT", "attribution": "Taste"}},
                {"id": "art-dir:sample", "layer": "art_direction", "name": "Duplicate", "provenance": {"source_project": "taste-skill", "source_file": "a", "source_id": "2", "license": "MIT", "attribution": "Taste"}}
            ]
            for fname, meta in [
                ("art-directions.json", ad_items),
                ("compositions.json", []),
                ("palettes.json", []),
                ("typography.json", []),
                ("sites.json", []),
                ("app-shells.json", [])
            ]:
                with open(os.path.join(tmpdir, fname), "w", encoding="utf-8") as f:
                    json.dump({"version": "2.0.0", "item_count": len(meta), "items": meta}, f)

            with self.assertRaises(ContractValidationError) as ctx:
                load_library(tmpdir)
            self.assertEqual(ctx.exception.code, ERR_SCHEMA_VIOLATION)

    def test_item_count_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            for fname in ["art-directions.json", "compositions.json", "palettes.json", "typography.json", "sites.json", "app-shells.json"]:
                with open(os.path.join(tmpdir, fname), "w", encoding="utf-8") as f:
                    # Declare item_count 5 but supply 0 items
                    json.dump({"version": "2.0.0", "item_count": 5, "items": []}, f)
            with self.assertRaises(ContractValidationError) as ctx:
                load_library(tmpdir)
            self.assertEqual(ctx.exception.code, ERR_SCHEMA_VIOLATION)


if __name__ == "__main__":
    unittest.main()

