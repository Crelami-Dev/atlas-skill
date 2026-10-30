#!/usr/bin/env python3
"""Atlas Runtime Engine — Unit Tests for Browser Visual QA Harness."""
import os
import sys
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from runtime.browser_qa import BrowserQAHarness, find_browser_executable
from runtime.composer import compose_design_plan
from runtime.contracts import normalize_brief
from runtime.generator import generate_website
from runtime.loader import load_library


class TestBrowserQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = load_library()
        cls.brief = normalize_brief({"project_name": "QA Test", "category": "saas", "tones": ["minimal"]})
        cls.plan = compose_design_plan(cls.brief, cls.lib)

    def test_browser_discovery(self):
        browser = find_browser_executable()
        # Browser should be discovered on this host (Chrome or Edge)
        self.assertIsNotNone(browser)
        self.assertTrue(os.path.isfile(browser))

    def test_harness_renders_and_captures_all_viewports(self):
        harness = BrowserQAHarness()
        self.assertTrue(harness.is_available())

        with tempfile.TemporaryDirectory() as tmpdir:
            generate_website(self.plan, tmpdir)
            qa_res = harness.run_visual_qa(tmpdir)

            self.assertEqual(qa_res["status"], "PASS")
            self.assertEqual(len(qa_res["viewports"]), 3)

            for vp in qa_res["viewports"]:
                self.assertEqual(vp["status"], "PASS")
                self.assertGreater(vp["screenshot_bytes"], 10000)
                self.assertIsNotNone(vp["screenshot_path"])
                self.assertTrue(os.path.isfile(vp["screenshot_path"]))

            # Verify qa_report.json created
            report_file = os.path.join(tmpdir, "screenshots", "qa_report.json")
            self.assertTrue(os.path.isfile(report_file))

    def test_missing_browser_marks_viewports_skipped(self):
        # Force invalid browser binary path
        harness = BrowserQAHarness(browser_path="/non_existent/fake_browser")
        self.assertFalse(harness.is_available())

        with tempfile.TemporaryDirectory() as tmpdir:
            generate_website(self.plan, tmpdir)
            qa_res = harness.run_visual_qa(tmpdir)

            self.assertEqual(len(qa_res["viewports"]), 3)
            for vp in qa_res["viewports"]:
                self.assertEqual(vp["status"], "SKIPPED")
                self.assertIsNone(vp["screenshot_path"])


if __name__ == "__main__":
    unittest.main()

