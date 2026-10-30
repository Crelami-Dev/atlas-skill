#!/usr/bin/env python3
"""Atlas Runtime Engine — Unit Tests for Orchestrator Fallbacks and Regressions."""
import hashlib
import os
import subprocess
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WORKSPACE_ROOT = os.path.abspath(os.path.join(ROOT_DIR, ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data")
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from runtime.adapters import NullAgentAdapter
from runtime.capabilities import detect_capabilities
from runtime.contracts import normalize_brief
from runtime.loader import load_library
from runtime.orchestration_contracts import ExecutionMode
from runtime.orchestrator import AtlasOrchestrator

CANONICAL_HASHES = {
    "app-shells.json": "0bc195f25367a60b4c4080f6ab7b93f049fb20963c68d8245078d8c5ba16b798",
    "art-directions.json": "f5bb6c7ff3f9bb2a68ddbbb6ffffcb2a977f12699a912ecc753395a38e3e8055",
    "compositions.json": "1074899a06e9a6255b60ddad251de7be31d5a5dfa0ea216e9a868ef63e00c17e",
    "palettes.json": "b1e587ccb3c13535efe0eae6c1da7eccec89407c134eb57c576f418c23a86b09",
    "sites.json": "1eef1a8dc1a73f119462505c3c02c70d0314eaaac5e937f47852f941517f7bd0",
    "source-map.json": "5edf16ac5fc03ae85332fa692a160421ee2659f677572f52cdeec3ee5d9bd7e4",
    "typography.json": "a46a500155e8f3954cfc22082a27b6d2c7daddf349acd3f4e64f014416cc428f"
}


class TestOrchestratorFallbacks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = load_library()
        cls.brief = normalize_brief({"project_name": "Fallback Test", "category": "dev-tool"})

    def test_automatic_fallback_when_multi_agent_unsupported(self):
        """Requesting mode='multi' without adapter or capabilities falls back safely to single-agent."""
        no_caps = detect_capabilities(env={})
        orch = AtlasOrchestrator(
            library=self.lib,
            adapter=NullAgentAdapter(),
            capabilities=no_caps
        )
        res = orch.execute(self.brief, mode="multi", force_multi=False)

        # Execution must succeed in single-agent sequential mode
        self.assertEqual(res["execution_mode"], ExecutionMode.SINGLE_AGENT_SEQUENTIAL.value)
        self.assertFalse(res["is_multi_agent"])
        self.assertEqual(res["final_verdict"], "PASS")

        # Must record fallback diagnostic
        codes = [d["code"] for d in res["diagnostics"]]
        self.assertIn("WARN_FALLBACK_TO_SINGLE_AGENT", codes)

    def test_force_multi_rejects_silent_fallback(self):
        """When force_multi=True, an unavailable multi-agent host halts with explicit error."""
        no_caps = detect_capabilities(env={})
        orch = AtlasOrchestrator(
            library=self.lib,
            adapter=NullAgentAdapter(),
            capabilities=no_caps
        )
        res = orch.execute(self.brief, mode="multi", force_multi=True)

        self.assertEqual(res["execution_mode"], "FAILED")
        self.assertEqual(res["final_verdict"], "FAIL")
        codes = [d["code"] for d in res["diagnostics"]]
        self.assertIn("ERR_MULTI_AGENT_UNAVAILABLE", codes)

    def test_canonical_datasets_maintain_exact_hashes(self):
        """Verify that data/ files have not been modified during Phase 4."""
        for fname, expected_hash in CANONICAL_HASHES.items():
            fpath = os.path.join(DATA_DIR, fname)
            with open(fpath, "rb") as f:
                actual_hash = hashlib.sha256(f.read()).hexdigest()
            self.assertEqual(actual_hash, expected_hash, f"Hash mismatch in {fname}")

    def test_source_repositories_remain_clean_and_untouched(self):
        """Verify that taste-skill and reference source directories are unmodified."""
        taste_dir = os.path.join(WORKSPACE_ROOT, "taste-skill")
        proc = subprocess.run(
            ["git", "-C", taste_dir, "status", "--short"],
            capture_output=True,
            text=True
        )
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout.strip(), "", "taste-skill has modified/untracked files!")


if __name__ == "__main__":
    unittest.main()

