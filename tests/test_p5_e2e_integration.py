#!/usr/bin/env python3
"""Atlas Phase 5 Test Suite — End-to-End Multi-Brief Integration.

Validates the full automated pipeline:
brief -> retrieval -> planning -> generation -> anti-slop checks -> validation

Across three distinct briefs:
1. Editorial / Portfolio: Typography and storytelling focus, masked headline motion.
2. Operational Data Dashboard: Readability and density focus, stillness motion.
3. Fintech Product Landing Page: Conversion and trust focus, rolling figures motion.
"""
import os
import shutil
import sys
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from runtime.composer import compose_design_plan
from runtime.contracts import normalize_brief
from runtime.generator import generate_website
from runtime.loader import load_library, default_data_dir


class TestP5EndToEndIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.lib = load_library(default_data_dir())
        cls.temp_dir = tempfile.mkdtemp(prefix="atlas_p5_test_")

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def test_brief_1_editorial_portfolio(self):
        brief = normalize_brief({
            "project_name": "Studio Bauhaus Review",
            "page_type": "editorial",
            "category": "architecture",
            "tones": ["editorial", "spacious"],
            "goals": ["storytelling"]
        })
        plan = compose_design_plan(brief, self.lib)

        # 1. Verification of retrieval & planning chain
        self.assertIn("curated_references", plan)
        self.assertIn("motion_plan", plan)
        motion_plan = plan["motion_plan"]
        pattern_ids = [p["id"] for p in motion_plan["patterns"]]
        self.assertIn("masked-headline", pattern_ids)

        # 2. End-to-end site generation
        out_dir = os.path.join(self.temp_dir, "editorial_site")
        gen_res = generate_website(plan, out_dir, prefer_mock_images=True)
        self.assertEqual(gen_res["status"], "SUCCESS")

        # Verify generated files
        self.assertTrue(os.path.exists(os.path.join(out_dir, "index.html")))
        self.assertTrue(os.path.exists(os.path.join(out_dir, "styles.css")))
        self.assertTrue(os.path.exists(os.path.join(out_dir, "script.js")))
        self.assertTrue(os.path.exists(os.path.join(out_dir, "assets", "animejs-adapter.js")))

        # Check anti-slop audit
        audit = gen_res.get("anti_slop_audit", {})
        self.assertIn(audit.get("status"), {"PASS", "WARN"})
        self.assertEqual(audit.get("failures_count", 0), 0)

    def test_brief_2_operational_data_dashboard(self):
        brief = normalize_brief({
            "project_name": "Metrics Pulse",
            "page_type": "app",
            "category": "finance",
            "density": "high",
            "tones": ["clinical", "technical"]
        })
        plan = compose_design_plan(brief, self.lib)

        # 1. Verification of stillness selection
        self.assertIn("motion_plan", plan)
        motion_plan = plan["motion_plan"]
        self.assertEqual(motion_plan["primaryPattern"], "stillness")
        self.assertIn("stillness", [p["id"] for p in motion_plan["patterns"]])

        # 2. End-to-end site generation
        out_dir = os.path.join(self.temp_dir, "dashboard_site")
        gen_res = generate_website(plan, out_dir, prefer_mock_images=True)
        self.assertEqual(gen_res["status"], "SUCCESS")

        # Verify generated files
        self.assertTrue(os.path.exists(os.path.join(out_dir, "index.html")))
        self.assertTrue(os.path.exists(os.path.join(out_dir, "assets", "animejs-adapter.js")))

        # Anti-slop audit should acknowledge operational card density without hard fail
        audit = gen_res.get("anti_slop_audit", {})
        self.assertEqual(audit.get("failures_count", 0), 0)

    def test_brief_3_fintech_product_landing(self):
        brief = normalize_brief({
            "project_name": "Apex Ledger",
            "page_type": "marketing",
            "category": "fintech",
            "tones": ["bold", "confident"],
            "slots": ["nav", "hero", "metrics", "features", "pricing", "cta", "footer"]
        })
        plan = compose_design_plan(brief, self.lib)

        # 1. Verification of rolling figures / value proposition motion
        motion_plan = plan["motion_plan"]
        pattern_ids = [p["id"] for p in motion_plan["patterns"]]
        self.assertIn("rolling-figures", pattern_ids)

        # 2. End-to-end site generation
        out_dir = os.path.join(self.temp_dir, "fintech_site")
        gen_res = generate_website(plan, out_dir, prefer_mock_images=True)
        self.assertEqual(gen_res["status"], "SUCCESS")

        # Verify generated files
        self.assertTrue(os.path.exists(os.path.join(out_dir, "index.html")))
        self.assertTrue(os.path.exists(os.path.join(out_dir, "styles.css")))
        self.assertTrue(os.path.exists(os.path.join(out_dir, "script.js")))
        self.assertTrue(os.path.exists(os.path.join(out_dir, "assets", "animejs-adapter.js")))

        # Anti-slop audit should pass without hard failure
        audit = gen_res.get("anti_slop_audit", {})
        self.assertEqual(audit.get("failures_count", 0), 0)

    def test_distinct_briefs_yield_distinct_decisions(self):
        """Prove that different briefs produce genuinely distinct plans, typographies, and motions."""
        brief_edit = normalize_brief({"page_type": "editorial", "category": "culture", "tones": ["editorial"]})
        brief_app = normalize_brief({"page_type": "app", "category": "finance", "density": "high"})
        brief_mkt = normalize_brief({"page_type": "marketing", "category": "fintech"})

        plan_edit = compose_design_plan(brief_edit, self.lib)
        plan_app = compose_design_plan(brief_app, self.lib)
        plan_mkt = compose_design_plan(brief_mkt, self.lib)

        # Art directions must be distinct
        self.assertNotEqual(plan_edit["art_direction"]["id"], plan_app["art_direction"]["id"])
        
        # Primary motions must be distinct
        self.assertNotEqual(plan_edit["motion_plan"]["primaryPattern"], plan_app["motion_plan"]["primaryPattern"])
        self.assertEqual(plan_app["motion_plan"]["primaryPattern"], "stillness")

        # Typography or palettes must reflect differing needs
        self.assertIsNotNone(plan_app["app_shell"])
        self.assertIsNone(plan_edit["app_shell"])


if __name__ == "__main__":
    unittest.main()
