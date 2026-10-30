#!/usr/bin/env python3
"""Atlas Runtime Engine — Unit Tests for Runtime Contracts and Schemas."""
import json
import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from runtime.contracts import (
    ContractValidationError,
    DEFAULT_SLOTS,
    Diagnostic,
    ERR_EMPTY_BRIEF,
    ERR_INVALID_DENSITY,
    ERR_INVALID_PAGE_TYPE,
    ERR_INVALID_WEIGHTS,
    ProductBrief,
    compute_plan_id,
    normalize_brief,
)


class TestRuntimeContracts(unittest.TestCase):
    def test_valid_minimum_brief(self):
        brief = normalize_brief({})
        self.assertIsInstance(brief, ProductBrief)
        self.assertEqual(brief.project_name, "Untitled Project")
        self.assertEqual(brief.page_type, "marketing")
        self.assertEqual(brief.category, "*")
        self.assertEqual(brief.density, "med")
        self.assertEqual(brief.slots, DEFAULT_SLOTS["marketing"])
        self.assertEqual(brief.prefer_conventional, False)
        self.assertEqual(brief.exclude, [])

    def test_editorial_and_app_default_slots(self):
        b_edit = normalize_brief({"page_type": "editorial"})
        self.assertEqual(b_edit.slots, DEFAULT_SLOTS["editorial"])

        b_app = normalize_brief({"page_type": "app"})
        self.assertEqual(b_app.slots, DEFAULT_SLOTS["app"])

    def test_custom_brief_fields_and_overrides(self):
        raw = {
            "project_name": "Atlas Cloud",
            "page_type": "marketing",
            "category": "saas",
            "tones": ["minimal", "technical"],
            "density": "high",
            "goals": ["lead-generation", "sign-up"],
            "slots": ["hero", "features", "pricing"],
            "prefer_conventional": True
        }
        b = normalize_brief(raw)
        self.assertEqual(b.project_name, "Atlas Cloud")
        self.assertEqual(b.category, "saas")
        self.assertEqual(b.tones, ["minimal", "technical"])
        self.assertEqual(b.density, "high")
        self.assertEqual(b.goals, ["lead-generation", "sign-up"])
        self.assertEqual(b.slots, ["hero", "features", "pricing"])
        self.assertTrue(b.prefer_conventional)

    def test_empty_brief_raises_error(self):
        with self.assertRaises(ContractValidationError) as ctx:
            normalize_brief(None)
        self.assertEqual(ctx.exception.code, ERR_EMPTY_BRIEF)

    def test_invalid_page_type_raises_error(self):
        with self.assertRaises(ContractValidationError) as ctx:
            normalize_brief({"page_type": "invalid_archetype"})
        self.assertEqual(ctx.exception.code, ERR_INVALID_PAGE_TYPE)

    def test_invalid_density_raises_error(self):
        with self.assertRaises(ContractValidationError) as ctx:
            normalize_brief({"density": "ultra_dense"})
        self.assertEqual(ctx.exception.code, ERR_INVALID_DENSITY)

    def test_invalid_scoring_weights_raises_error(self):
        with self.assertRaises(ContractValidationError) as ctx:
            normalize_brief({"scoring_weights": {"category": -1.5}})
        self.assertEqual(ctx.exception.code, ERR_INVALID_WEIGHTS)

    def test_comma_separated_string_normalization(self):
        raw = {
            "tones": "bold, editorial, minimal",
            "goals": "lead-generation, conversion",
            "assets": "photo, product_ui"
        }
        b = normalize_brief(raw)
        self.assertEqual(b.tones, ["bold", "editorial", "minimal"])
        self.assertEqual(b.goals, ["lead-generation", "conversion"])
        self.assertEqual(b.assets, ["photo", "product_ui"])

    def test_unknown_asset_emits_diagnostic_warning(self):
        diagnostics = []
        b = normalize_brief({"assets": ["photo", "unknown_hologram_format"]}, diagnostics=diagnostics)
        self.assertEqual(len(diagnostics), 1)
        self.assertEqual(diagnostics[0].severity, "WARNING")
        self.assertIn("unknown_hologram_format", diagnostics[0].message)

    def test_compute_plan_id_determinism(self):
        b1 = normalize_brief({"category": "fintech", "tones": ["bold", "luxury"]})
        b2 = normalize_brief({"category": "fintech", "tones": ["bold", "luxury"]})
        id1 = compute_plan_id(b1.to_dict(), "2.0.0")
        id2 = compute_plan_id(b2.to_dict(), "2.0.0")
        self.assertEqual(id1, id2)
        self.assertEqual(len(id1), 16)


if __name__ == "__main__":
    unittest.main()

