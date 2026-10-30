#!/usr/bin/env python3
"""Atlas Runtime Engine — Unit Tests for Composition Engine."""
import json
import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from runtime.composer import compose_design_plan
from runtime.contracts import normalize_brief
from runtime.loader import load_library


class TestCompositionEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = load_library()
        schema_path = os.path.join(ROOT_DIR, "schemas", "design-plan.schema.json")
        with open(schema_path, "r", encoding="utf-8") as f:
            cls.schema = json.load(f)

    def test_full_marketing_plan_generation(self):
        brief = normalize_brief({
            "project_name": "SaaS Platform",
            "page_type": "marketing",
            "category": "saas",
            "tones": ["minimal", "technical"],
            "goals": ["lead-generation"]
        })
        plan = compose_design_plan(brief, self.lib)

        # 1. Structure and version
        self.assertEqual(plan["runtime_version"], "2.0.0")
        self.assertEqual(plan["library_version"], "2.0.0")
        self.assertEqual(len(plan["plan_id"]), 16)

        # 2. Art direction
        self.assertTrue(plan["art_direction"]["id"].startswith("art-dir:"))
        self.assertIn("name", plan["art_direction"])
        self.assertGreater(len(plan["art_direction"]["rationale"]), 0)

        # 3. Composition slots
        slots = plan["composition"]["slots"]
        self.assertGreaterEqual(len(slots), 5)
        for s in slots:
            self.assertIn(s["slot"], brief.slots)
            # Must be a real canonical ID from library
            self.assertIsNotNone(self.lib.get_by_id(s["pattern_id"]), f"Pattern ID {s['pattern_id']} not in library")
            self.assertGreater(len(s["rationale"]), 0)

        # 4. Palette and Typography
        self.assertTrue(plan["palette"]["id"].startswith("palette:"))
        self.assertIsNotNone(self.lib.get_by_id(plan["palette"]["id"]))
        self.assertTrue(plan["typography"]["id"].startswith("type:"))
        self.assertIsNotNone(self.lib.get_by_id(plan["typography"]["id"]))

        # 5. App shell must be None for marketing
        self.assertIsNone(plan["app_shell"])

        # 6. Assets
        self.assertIn("summary", plan["assets"])
        self.assertGreaterEqual(plan["assets"]["summary"]["total_required"], 1)

    def test_app_page_type_includes_app_shell(self):
        brief = normalize_brief({
            "project_name": "Crypto Wallet App",
            "page_type": "app",
            "category": "finance",
            "density": "high"
        })
        plan = compose_design_plan(brief, self.lib)
        self.assertIsNotNone(plan["app_shell"])
        self.assertTrue(plan["app_shell"]["id"].startswith("app:shell:"))
        self.assertIsNotNone(self.lib.get_by_id(plan["app_shell"]["id"]))

    def test_deterministic_output_across_repeated_runs(self):
        brief_dict = {
            "category": "education",
            "tones": ["warm", "playful"],
            "density": "low"
        }
        b1 = normalize_brief(brief_dict)
        b2 = normalize_brief(brief_dict)

        plan1 = compose_design_plan(b1, self.lib, deterministic_timestamp="2026-10-30T00:00:00Z")
        plan2 = compose_design_plan(b2, self.lib, deterministic_timestamp="2026-10-30T00:00:00Z")

        # Must produce identical plan ID and JSON serialization
        self.assertEqual(plan1["plan_id"], plan2["plan_id"])
        json1 = json.dumps(plan1, sort_keys=True)
        json2 = json.dumps(plan2, sort_keys=True)
        self.assertEqual(json1, json2)

    def test_skipped_slots_handling(self):
        # Exclude all hero patterns so hero slot cannot be fulfilled
        hero_ids = [p["id"] for p in self.lib.compositions if p.get("family") == "hero"]
        brief = normalize_brief({
            "slots": ["hero", "pricing"],
            "exclude": hero_ids
        })
        plan = compose_design_plan(brief, self.lib)
        skipped = plan["composition"]["skipped_slots"]
        self.assertEqual(len(skipped), 1)
        self.assertEqual(skipped[0]["slot"], "hero")
        self.assertTrue(any("hero" in w for w in plan["warnings"]))


if __name__ == "__main__":
    unittest.main()

