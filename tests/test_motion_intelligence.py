#!/usr/bin/env python3
"""Atlas Phase 5 Test Suite — Motion Intelligence & Planning.

Validates that motion patterns adhere to schema, support intentional stillness,
and adapt appropriately to diverse project briefs.
"""
import json
import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from runtime.contracts import normalize_brief
from runtime.loader import load_library, default_data_dir
from runtime.motion_adapter import (
    load_motion_patterns,
    plan_motion_for_brief,
    validate_motion_pattern,
)
from runtime.scorer import score_motion


class TestMotionIntelligence(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.motions = load_motion_patterns()
        cls.lib = load_library(default_data_dir())

    def test_all_18_motion_patterns_satisfy_schema(self):
        self.assertEqual(len(self.motions), 18)
        for pattern in self.motions:
            valid, errors = validate_motion_pattern(pattern)
            self.assertTrue(valid, f"Pattern '{pattern.get('id')}' schema violation: {errors}")

    def test_stillness_selected_for_app_and_high_density(self):
        brief_app = normalize_brief({
            "project_name": "Operations Console",
            "page_type": "app",
            "density": "high",
            "category": "finance"
        })
        plan = plan_motion_for_brief(brief_app, self.motions)
        self.assertEqual(plan["primaryPattern"], "stillness")
        self.assertIn("stillness", [p["id"] for p in plan["patterns"]])
        self.assertIn("readability", plan["rationale"].lower())

    def test_editorial_motion_selection(self):
        brief_editorial = normalize_brief({
            "project_name": "Architecture Review",
            "page_type": "editorial",
            "category": "culture",
            "tones": ["editorial", "spacious"]
        })
        plan = plan_motion_for_brief(brief_editorial, self.motions)
        pattern_ids = [p["id"] for p in plan["patterns"]]
        self.assertIn("masked-headline", pattern_ids)
        self.assertIn("shutter-image", pattern_ids)

    def test_fintech_metrics_motion_selection(self):
        brief_fintech = normalize_brief({
            "project_name": "Nova Pay",
            "page_type": "marketing",
            "category": "fintech",
            "slots": ["nav", "hero", "metrics", "features", "cta", "footer"]
        })
        plan = plan_motion_for_brief(brief_fintech, self.motions)
        pattern_ids = [p["id"] for p in plan["patterns"]]
        self.assertIn("masked-headline", pattern_ids)
        self.assertIn("rolling-figures", pattern_ids)

    def test_explicit_motion_constraint_override(self):
        brief = normalize_brief({
            "project_name": "Brand Site",
            "page_type": "marketing",
            "category": "fashion",
            "explicit_constraints": {
                "forced_motion": "edge-marquee"
            }
        })
        plan = plan_motion_for_brief(brief, self.motions)
        self.assertEqual(plan["primaryPattern"], "edge-marquee")
        self.assertIn("forced", plan["rationale"].lower())

    def test_motion_scoring(self):
        brief_app = normalize_brief({"page_type": "app", "density": "high"})
        stillness_pattern = next(m for m in self.motions if m["id"] == "stillness")
        score, rationale = score_motion(stillness_pattern, brief_app)
        self.assertGreater(score, 5.0)
        self.assertIn("stillness prioritized", rationale[1].lower())


if __name__ == "__main__":
    unittest.main()
