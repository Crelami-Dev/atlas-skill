#!/usr/bin/env python3
"""Atlas Runtime Engine — Unit Tests for Single-Agent Sequential Orchestration."""
import os
import sys
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from runtime.contracts import normalize_brief
from runtime.loader import load_library
from runtime.orchestration_contracts import ExecutionMode, Role
from runtime.orchestrator import AtlasOrchestrator


class TestSingleAgentOrchestration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = load_library()
        cls.brief = normalize_brief({
            "project_name": "Apex Institutional",
            "category": "fintech",
            "tones": ["bold", "luxury"],
            "density": "med"
        })

    def test_single_agent_executes_all_five_roles_in_exact_sequence(self):
        orch = AtlasOrchestrator(library=self.lib)
        res = orch.execute(self.brief, mode="single")

        self.assertEqual(res["execution_mode"], ExecutionMode.SINGLE_AGENT_SEQUENTIAL.value)
        self.assertFalse(res["is_multi_agent"])
        self.assertTrue(res["is_live"])
        self.assertFalse(res["is_simulated"])
        self.assertEqual(res["final_verdict"], "PASS")

        # Verify exact role sequence
        expected_roles = [
            Role.PRODUCT_ANALYST.value,
            Role.ART_DIRECTOR.value,
            Role.FRONTEND_IMPLEMENTER.value,
            Role.QA_CRITIC.value,
            Role.LEAD_ORCHESTRATOR.value
        ]
        self.assertEqual(res["roles_executed"], expected_roles)

        # Verify task list
        task_roles = [t["role"] for t in res["tasks"]]
        self.assertIn(Role.PRODUCT_ANALYST.value, task_roles)
        self.assertIn(Role.ART_DIRECTOR.value, task_roles)
        self.assertIn(Role.FRONTEND_IMPLEMENTER.value, task_roles)
        self.assertIn(Role.QA_CRITIC.value, task_roles)

    def test_single_agent_with_website_generation_and_browser_qa(self):
        orch = AtlasOrchestrator(library=self.lib)
        with tempfile.TemporaryDirectory() as tmpdir:
            res = orch.execute(self.brief, mode="single", build_dir=tmpdir, run_qa=True)

            self.assertEqual(res["final_verdict"], "PASS")
            self.assertEqual(res["revision_count"], 0)

            # Check files were generated on disk
            self.assertTrue(os.path.isfile(os.path.join(tmpdir, "index.html")))
            self.assertTrue(os.path.isfile(os.path.join(tmpdir, "styles.css")))
            self.assertTrue(os.path.isfile(os.path.join(tmpdir, "script.js")))

    def test_single_agent_revision_loop_halts_at_max_cycles(self):
        """Verify that when QA repeatedly fails, the revision loop terminates at max_revisions."""
        orch = AtlasOrchestrator(library=self.lib, max_revisions=3)

        # Monkey-patch BrowserQAHarness to simulate repeated FAIL verdict
        from runtime import orchestrator
        orig_qa = orchestrator.BrowserQAHarness

        class FailingQAHarness:
            def run_visual_qa(self, site_dir):
                return {
                    "status": "FAIL",
                    "dom_quality_gate": {"passed": False},
                    "screenshot_capture": {"status": "FAIL"},
                    "browser_runtime_evaluation": {"status": "FAIL"}
                }

        try:
            orchestrator.BrowserQAHarness = FailingQAHarness
            with tempfile.TemporaryDirectory() as tmpdir:
                res = orch.execute(self.brief, mode="single", build_dir=tmpdir, run_qa=True)

                self.assertEqual(res["final_verdict"], "FAIL")
                # Exactly 3 revision cycles applied before halting
                self.assertEqual(res["revision_count"], 3)
                self.assertEqual(len(res["revisions"]), 3)
                for r in res["revisions"]:
                    self.assertEqual(r["trigger_role"], Role.QA_CRITIC.value)
        finally:
            orchestrator.BrowserQAHarness = orig_qa

    def test_deterministic_execution_id_matches_brief(self):
        orch = AtlasOrchestrator(library=self.lib)
        res1 = orch.execute(self.brief, mode="single")
        res2 = orch.execute(self.brief, mode="single")
        self.assertEqual(res1["execution_id"], res2["execution_id"])


if __name__ == "__main__":
    unittest.main()

