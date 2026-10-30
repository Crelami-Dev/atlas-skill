#!/usr/bin/env python3
"""Atlas Runtime Engine — Unit Tests for Scoring and Retrieval."""
import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from runtime.contracts import normalize_brief
from runtime.loader import load_library
from runtime.retriever import is_pattern_eligible, retrieve_candidates_for_slot
from runtime.scorer import (
    score_art_direction,
    score_composition,
    score_palette,
    score_typography,
)


class TestScoringAndRetrieval(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = load_library()

    def test_page_type_hard_constraint(self):
        brief_mkt = normalize_brief({"page_type": "marketing"})
        brief_app = normalize_brief({"page_type": "app"})

        # 'atlas:nav-minimal-bar' allows marketing, editorial, app
        nav_item = self.lib.get_by_id("atlas:nav-minimal-bar")
        ok_mkt, _ = is_pattern_eligible(nav_item, brief_mkt)
        ok_app, _ = is_pattern_eligible(nav_item, brief_app)
        self.assertTrue(ok_mkt)
        self.assertTrue(ok_app)

        # 'atlas:app-filter-drawer' only allows 'app'
        app_drawer = self.lib.get_by_id("atlas:app-filter-drawer")
        if app_drawer:
            ok_mkt2, reason = is_pattern_eligible(app_drawer, brief_mkt)
            ok_app2, _ = is_pattern_eligible(app_drawer, brief_app)
            self.assertFalse(ok_mkt2)
            self.assertIn("incompatible page_type", reason)
            self.assertTrue(ok_app2)

    def test_exclude_list_hard_constraint(self):
        brief = normalize_brief({"exclude": ["atlas:nav-minimal-bar"]})
        nav_item = self.lib.get_by_id("atlas:nav-minimal-bar")
        ok, reason = is_pattern_eligible(nav_item, brief)
        self.assertFalse(ok)
        self.assertIn("explicitly excluded", reason)

    def test_hard_incompatibility_rejection(self):
        brief = normalize_brief({"category": "saas"})
        cand1 = {"id": "pat:a", "categories": ["saas"], "tones": [], "incompatible": ["pat:b"]}
        cand2 = {"id": "pat:b", "categories": ["saas"], "tones": [], "incompatible": []}

        # First pattern chosen
        chosen = [cand1]
        score, why = score_composition(cand2, brief, chosen)
        self.assertIsNone(score, "Incompatible pattern must receive None score")
        self.assertIn("hard incompatibility", why[0])

    def test_art_direction_synergy_boost(self):
        brief = normalize_brief({"category": "saas"})
        ad = self.lib.get_by_id("art-dir:name-as-monument")

        # Pattern with category 'name-as-monument'
        hero_synergy = self.lib.get_by_id("taste:hero:name-under-photograph")
        score_with_ad, why_with_ad = score_composition(hero_synergy, brief, [], selected_art_direction=ad)
        score_without_ad, _ = score_composition(hero_synergy, brief, [], selected_art_direction=None)

        self.assertGreater(score_with_ad, score_without_ad)
        self.assertTrue(any("art-direction synergy" in w for w in why_with_ad))

    def test_tone_overlap_scoring(self):
        brief = normalize_brief({"tones": ["bold", "editorial"]})
        item_match = {"id": "pat:1", "categories": ["*"], "tones": ["bold", "editorial"]}
        item_mismatch = {"id": "pat:2", "categories": ["*"], "tones": ["quiet"]}

        s1, why1 = score_composition(item_match, brief, [])
        s2, why2 = score_composition(item_mismatch, brief, [])
        self.assertGreater(s1, s2)
        self.assertTrue(any("tone match" in w for w in why1))

    def test_density_alignment_scoring(self):
        brief_high = normalize_brief({"density": "high"})
        pat_high = {"id": "pat:high", "categories": ["*"], "density": "high"}
        pat_low = {"id": "pat:low", "categories": ["*"], "density": "low"}

        s_high, _ = score_composition(pat_high, brief_high, [])
        s_low, _ = score_composition(pat_low, brief_high, [])
        self.assertGreater(s_high, s_low)

    def test_conventional_preference_penalizes_unconventional_patterns(self):
        brief_conv = normalize_brief({"prefer_conventional": True})
        pat_unconventional = {
            "id": "pat:unc", "categories": ["*"],
            "visual_tags": ["asymmetric", "layered", "offset"]
        }
        pat_clean = {
            "id": "pat:clean", "categories": ["*"],
            "visual_tags": ["grid", "clean", "cards"]
        }

        s_unc, why_unc = score_composition(pat_unconventional, brief_conv, [])
        s_clean, why_clean = score_composition(pat_clean, brief_conv, [])
        self.assertLess(s_unc, s_clean)
        self.assertTrue(any("unconventional layout penalized" in w for w in why_unc))

    def test_deterministic_tie_breaking(self):
        # Two identical candidates must break ties by ID alphabetically
        brief = normalize_brief({"category": "saas"})
        cand_b = {"id": "pat:zebra", "categories": ["saas"], "tones": []}
        cand_a = {"id": "pat:alpha", "categories": ["saas"], "tones": []}

        s_b, _ = score_composition(cand_b, brief, [])
        s_a, _ = score_composition(cand_a, brief, [])
        self.assertEqual(s_b, s_a)

        # Sort key used by engine: (-score, id)
        sorted_cands = sorted([cand_b, cand_a], key=lambda c: (-s_a, c["id"]))
        self.assertEqual(sorted_cands[0]["id"], "pat:alpha")
        self.assertEqual(sorted_cands[1]["id"], "pat:zebra")

    def test_custom_scoring_weights(self):
        brief_default = normalize_brief({"tones": ["bold"]})
        brief_heavy_tone = normalize_brief({"tones": ["bold"], "scoring_weights": {"tones": 5.0}})

        pat = {"id": "pat:1", "categories": ["*"], "tones": ["bold"]}
        s_def, _ = score_composition(pat, brief_default, [])
        s_heavy, _ = score_composition(pat, brief_heavy_tone, [])
        self.assertGreater(s_heavy, s_def)


if __name__ == "__main__":
    unittest.main()

