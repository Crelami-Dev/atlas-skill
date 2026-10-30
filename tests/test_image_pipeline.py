#!/usr/bin/env python3
"""Atlas Runtime Engine — Unit Tests for Image Pipeline and Provider Adapter."""
import os
import sys
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from runtime.composer import compose_design_plan
from runtime.contracts import normalize_brief
from runtime.image_pipeline import (
    GeminiImagenProvider,
    ImageGenerationRequest,
    MockImageProvider,
    STATUS_FALLBACK_USED,
    STATUS_INTEGRATED,
    STATUS_VALIDATED,
    TIER_1_NATIVE,
    TIER_3_CSS_SVG,
    build_art_directed_prompt,
    discover_image_provider,
    execute_asset_pipeline,
)
from runtime.loader import load_library


class TestImagePipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = load_library()
        cls.brief = normalize_brief({"category": "saas", "tones": ["minimal"]})
        cls.plan = compose_design_plan(cls.brief, cls.lib)

    def test_mock_image_provider_success(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            provider = MockImageProvider(should_succeed=True)
            self.assertTrue(provider.is_available())

            out_img = os.path.join(tmpdir, "test.png")
            req = ImageGenerationRequest(
                request_id="req_1",
                asset_id="asset:hero:1",
                slot="hero",
                role="hero_media",
                prompt="Futuristic clean SaaS hero",
                negative_prompt="blurry",
                aspect_ratio="16:9",
                width=1200,
                height=675,
                art_direction_name="Clean Minimal",
                output_filename="test.png"
            )
            ok, msg = provider.generate_image(req, out_img)
            self.assertTrue(ok)
            self.assertTrue(os.path.isfile(out_img))
            self.assertGreater(os.path.getsize(out_img), 0)

    def test_mock_image_provider_failure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            provider = MockImageProvider(should_succeed=False, failure_reason="Simulated API Quota Error")
            out_img = os.path.join(tmpdir, "test_fail.png")
            req = ImageGenerationRequest(
                request_id="req_2",
                asset_id="asset:hero:2",
                slot="hero",
                role="hero_media",
                prompt="Test prompt",
                negative_prompt="blurry",
                aspect_ratio="16:9",
                width=1200,
                height=675,
                art_direction_name="Clean Minimal",
                output_filename="test_fail.png"
            )
            ok, msg = provider.generate_image(req, out_img)
            self.assertFalse(ok)
            self.assertIn("Simulated API Quota Error", msg)
            self.assertFalse(os.path.isfile(out_img))

    def test_offline_asset_pipeline_creates_svg_fallback(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Uncredentialed provider forces Tier 3 fallback
            manifest = execute_asset_pipeline(self.plan, tmpdir, provider=None)
            self.assertGreaterEqual(manifest["total_assets"], 1)
            self.assertEqual(manifest["native_ai_count"], 0)
            self.assertEqual(manifest["svg_fallback_count"], manifest["total_assets"])

            for a in manifest["assets"]:
                self.assertEqual(a["tier_selected"], TIER_3_CSS_SVG)
                self.assertTrue(a["fallback_used"])
                self.assertTrue(os.path.isfile(a["disk_path"]))
                self.assertTrue(a["disk_path"].endswith(".svg"))
                with open(a["disk_path"], "r", encoding="utf-8") as svg_f:
                    svg_content = svg_f.read()
                # Ensure no placeholder instruction leaks
                self.assertNotIn("[photo |", svg_content)
                self.assertNotIn("Dressed as something else", svg_content)

    def test_mock_provider_executes_tier_1_native(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            prov = MockImageProvider(should_succeed=True)
            manifest = execute_asset_pipeline(self.plan, tmpdir, provider=prov)
            self.assertGreaterEqual(manifest["native_ai_count"], 1)
            first_asset = manifest["assets"][0]
            self.assertEqual(first_asset["tier_selected"], TIER_1_NATIVE)
            self.assertFalse(first_asset["fallback_used"])
            self.assertTrue(os.path.isfile(first_asset["disk_path"]))
            self.assertTrue(first_asset["disk_path"].endswith(".png"))

    def test_art_directed_prompt_builder(self):
        ad = {"name": "The well-kept board", "imagery": "Photographs fill whole tiles", "colour": "Muted earth"}
        prompt, neg = build_art_directed_prompt("hero", "photo", "16:9", "education", ad, ["warm", "playful"])
        self.assertIn("education", prompt)
        self.assertIn("The well-kept board", prompt)
        self.assertIn("16:9", prompt)
        self.assertIn("blurry", neg)

    def test_gemini_provider_unconfigured_safety(self):
        # When no API key is passed, provider is safely reported as unavailable
        prov = GeminiImagenProvider(api_key=None)
        # Should not throw or crash
        self.assertFalse(prov.is_available())


if __name__ == "__main__":
    unittest.main()

