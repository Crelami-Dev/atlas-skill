#!/usr/bin/env python3
"""Atlas-Skill Phase 2 Integrity, Determinism, and Source Protection Test Suite."""
import glob
import hashlib
import json
import os
import subprocess
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WORKSPACE_ROOT = os.path.abspath(os.path.join(ROOT_DIR, ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data")
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from runtime.composer import compose_design_plan
from runtime.contracts import normalize_brief
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


class TestPhase2Integrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = load_library()

    def test_canonical_datasets_maintain_exact_sha256(self):
        """Verify that canonical dataset files in data/ have not been altered."""
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
        # 1. taste-skill git status check
        taste_dir = os.path.join(WORKSPACE_ROOT, "taste-skill")
        self.assertTrue(os.path.isdir(taste_dir), "taste-skill directory missing")
        proc = subprocess.run(
            ["git", "-C", taste_dir, "status", "--short"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertEqual(proc.returncode, 0, "git status check failed on taste-skill")
        self.assertEqual(proc.stdout.strip(), "", "taste-skill repository has untracked or modified files!")

        # 2. Non-git source repositories file count checks
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

    def test_end_to_end_planning_across_multiple_sectors(self):
        """Verify that the engine generates valid plans across multiple diverse sectors."""
        sectors = ["saas", "fintech", "education", "agency", "ecommerce"]
        for sec in sectors:
            brief = normalize_brief({"category": sec, "tones": ["bold", "editorial"]})
            plan = compose_design_plan(brief, self.lib)
            self.assertEqual(plan["normalized_brief"]["category"], sec)
            self.assertGreater(plan["composition"]["total_score"], 0)
            self.assertGreater(len(plan["composition"]["slots"]), 4)

    def test_repeated_runs_deterministic_equality(self):
        """Verify that running planning 5 times on identical inputs produces identical results."""
        brief_data = {
            "project_name": "Deterministic Verification",
            "category": "developer-tools",
            "tones": ["technical", "minimal"],
            "density": "high"
        }
        fixed_time = "2026-10-30T10:00:00Z"

        first_plan = compose_design_plan(normalize_brief(brief_data), self.lib, deterministic_timestamp=fixed_time)
        first_json = json.dumps(first_plan, sort_keys=True)

        for i in range(4):
            subsequent_plan = compose_design_plan(normalize_brief(brief_data), self.lib, deterministic_timestamp=fixed_time)
            subsequent_json = json.dumps(subsequent_plan, sort_keys=True)
            self.assertEqual(
                first_json,
                subsequent_json,
                f"Nondeterministic plan difference observed on iteration {i + 1}"
            )


if __name__ == "__main__":
    unittest.main()

