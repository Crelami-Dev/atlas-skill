#!/usr/bin/env python3
"""Atlas-Skill Phase 3 End-to-End Integrity, Immutability, and Source Protection Test Suite."""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WORKSPACE_ROOT = os.path.abspath(os.path.join(ROOT_DIR, ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data")
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from runtime.browser_qa import BrowserQAHarness
from runtime.composer import compose_design_plan
from runtime.contracts import normalize_brief
from runtime.generator import generate_website
from runtime.loader import load_library

EXPECTED_HASHES = {
    "app-shells.json": "0bc195f25367a60b4c4080f6ab7b93f049fb20963c68d8245078d8c5ba16b798",
    "art-directions.json": "f5bb6c7ff3f9bb2a68ddbbb6ffffcb2a977f12699a912ecc753395a38e3e8055",
    "compositions.json": "1074899a06e9a6255b60ddad251de7be31d5a5dfa0ea216e9a868ef63e00c17e",
    "palettes.json": "b1e587ccb3c13535efe0eae6c1da7eccec89407c134eb57c576f418c23a86b09",
    "sites.json": "1eef1a8dc1a73f119462505c3c02c70d0314eaaac5e937f47852f941517f7bd0",
    "source-map.json": "5edf16ac5fc03ae85332fa692a160421ee2659f677572f52cdeec3ee5d9bd7e4",
    "typography.json": "a46a500155e8f3954cfc22082a27b6d2c7daddf349acd3f4e64f014416cc428f"
}


class TestPhase3Integrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = load_library()

    def test_canonical_datasets_maintain_exact_sha256(self):
        """Verify that canonical datasets in data/ have not been altered."""
        for fname, expected_hash in EXPECTED_HASHES.items():
            fpath = os.path.join(DATA_DIR, fname)
            self.assertTrue(os.path.isfile(fpath), f"Missing data file: {fname}")
            with open(fpath, "rb") as f:
                actual_hash = hashlib.sha256(f.read()).hexdigest()
            self.assertEqual(
                actual_hash,
                expected_hash,
                f"SHA-256 hash mismatch in {fname}! Expected {expected_hash}, got {actual_hash}"
            )

    def test_source_repositories_remain_unmodified(self):
        """Verify that source repositories have not been altered or deleted."""
        # 1. taste-skill git clean check
        taste_dir = os.path.join(WORKSPACE_ROOT, "taste-skill")
        self.assertTrue(os.path.isdir(taste_dir), "taste-skill directory missing")
        proc = subprocess.run(
            ["git", "-C", taste_dir, "status", "--short"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout.strip(), "", "taste-skill repository has untracked or modified files!")

        # 2. Non-git source folders file counts
        expected_counts = {
            "atlas-frontend-design": 41,
            "project-atlas-v0.2.0-alpha": 18,
            ".taste-skill": 11
        }
        for src_name, expected_fcount in expected_counts.items():
            src_path = os.path.join(WORKSPACE_ROOT, src_name)
            self.assertTrue(os.path.isdir(src_path), f"Source directory {src_name} missing")
            actual_count = sum(len(files) for _, _, files in os.walk(src_path))
            self.assertEqual(
                actual_count,
                expected_fcount,
                f"File count mismatch in source {src_name}: expected {expected_fcount}, found {actual_count}"
            )

    def test_deep_immutability_of_shared_canonical_records(self):
        """Verify that nested metadata, arrays, and objects cannot be mutated."""
        for item in self.lib.compositions[:10]:
            # Top-level mutation fails
            with self.assertRaises(TypeError):
                item["name"] = "corrupted"

            # Nested dict mutation fails
            if isinstance(item.get("requires"), dict):
                with self.assertRaises(TypeError):
                    item["requires"]["assets"] = []

            # Nested list/tuple mutation fails
            if isinstance(item.get("page_types"), (tuple, list)):
                with self.assertRaises(TypeError):
                    item["page_types"][0] = "corrupted"

    def test_full_pipeline_end_to_end_execution(self):
        """Verify full pipeline: Brief -> Plan -> Website -> Browser QA -> Screenshots."""
        brief = normalize_brief({
            "project_name": "Integrity Test Suite",
            "category": "developer-tools",
            "tones": ["technical", "minimal"],
            "density": "high"
        })
        plan = compose_design_plan(brief, self.lib)

        with tempfile.TemporaryDirectory() as tmpdir:
            # 1. Generate website
            gen_res = generate_website(plan, tmpdir)
            self.assertEqual(gen_res["status"], "SUCCESS")

            # 2. Browser QA and Screenshots
            harness = BrowserQAHarness()
            if harness.is_available():
                qa_res = harness.run_visual_qa(tmpdir)
                self.assertEqual(qa_res["status"], "PASS")
                self.assertEqual(len(qa_res["viewports"]), 3)
                for vp in qa_res["viewports"]:
                    self.assertEqual(vp["status"], "PASS")
                    self.assertGreater(vp["screenshot_bytes"], 10000)

            # 3. Static DOM Gate
            check_tool = os.path.join(ROOT_DIR, "tools", "atlas_check.py")
            chk_proc = subprocess.run(
                [sys.executable, check_tool, os.path.join(tmpdir, "index.html"), "--type", "marketing"],
                capture_output=True,
                text=True
            )
            self.assertEqual(chk_proc.returncode, 0, f"atlas_check failed: {chk_proc.stderr}")


if __name__ == "__main__":
    unittest.main()

