#!/usr/bin/env python3
"""Atlas Runtime Engine — Unit Tests for Asset Boundary and 3-Tier Fallback."""
import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from runtime.assets import (
    AssetRequirement,
    AssetResolver,
    BaseImageProvider,
    STATUS_FALLBACK_READY,
    STATUS_RESOLVED,
    TIER_1_NATIVE,
    TIER_3_CSS_SVG,
    generate_svg_fallback,
)


class MockActiveImageProvider(BaseImageProvider):
    def is_available(self) -> bool:
        return True

    def generate(self, prompt: str, aspect_ratio: str):
        return {"url": "mock://generated/asset.png", "provider": "mock-native-v1"}


class MockFailingImageProvider(BaseImageProvider):
    def is_available(self) -> bool:
        return True

    def generate(self, prompt: str, aspect_ratio: str):
        # Simulates provider timeout or quota error
        return None


class TestAssetBoundary(unittest.TestCase):
    def setUp(self):
        self.art_dir = {
            "name": "The well-kept board",
            "imagery": "Photographs fill whole tiles with object-fit: cover"
        }
        self.pattern_with_assets = {
            "id": "atlas:hero-split",
            "requires": {"assets": ["photo", "product_ui"]}
        }
        self.pattern_no_assets = {
            "id": "atlas:nav-minimal-bar",
            "requires": {"assets": []}
        }

    def test_default_offline_resolution_uses_tier_3_fallback(self):
        resolver = AssetResolver()  # No provider configured
        reqs = resolver.resolve("hero", self.pattern_with_assets, self.art_dir, "fintech")

        self.assertEqual(len(reqs), 2)
        for req in reqs:
            self.assertEqual(req.resolution_tier, TIER_3_CSS_SVG)
            self.assertEqual(req.status, STATUS_FALLBACK_READY)
            self.assertIn("svg_snippet", req.fallback_descriptor)
            self.assertIn("<svg", req.fallback_descriptor["svg_snippet"])
            self.assertIn("INSTITUTIONAL TREASURY ARCHITECTURE", req.fallback_descriptor["svg_snippet"])
            self.assertIn("MULTI-SIG VERIFIED", req.fallback_descriptor["svg_snippet"])
            # Must NOT contain fabricated quantitative metrics or fake chart curves
            self.assertNotIn("$2,485,920.00 USD", req.fallback_descriptor["svg_snippet"])
            self.assertNotIn("+14.8% APY", req.fallback_descriptor["svg_snippet"])
            self.assertNotIn("$2.50M", req.fallback_descriptor["svg_snippet"])
            self.assertNotIn("Peak: $2.51M", req.fallback_descriptor["svg_snippet"])
            self.assertIn("alt_text", req.fallback_descriptor)
            # Must NOT expose placeholder brackets or internal prompt text
            self.assertNotIn("[photo | 16:9]", req.fallback_descriptor["svg_snippet"])
            self.assertNotIn("[hero_graphic | 16:9]", req.fallback_descriptor["svg_snippet"])
            self.assertNotIn("The well-kept board", req.fallback_descriptor["svg_snippet"])
            # Must NOT claim fake generation URL
            self.assertNotIn("http://", req.prompt_brief)

    def test_active_provider_resolves_tier_1(self):
        provider = MockActiveImageProvider()
        resolver = AssetResolver(provider=provider)
        reqs = resolver.resolve("hero", self.pattern_with_assets, self.art_dir, "saas")

        self.assertEqual(len(reqs), 2)
        for req in reqs:
            self.assertEqual(req.resolution_tier, TIER_1_NATIVE)
            self.assertEqual(req.status, STATUS_RESOLVED)
            self.assertEqual(req.licensing["type"], "ai_generated_original")

    def test_failing_provider_falls_back_safely_to_tier_3(self):
        provider = MockFailingImageProvider()
        resolver = AssetResolver(provider=provider)
        reqs = resolver.resolve("hero", self.pattern_with_assets, self.art_dir, "healthcare")

        self.assertEqual(len(reqs), 2)
        for req in reqs:
            self.assertEqual(req.resolution_tier, TIER_3_CSS_SVG)
            self.assertEqual(req.status, STATUS_FALLBACK_READY)

    def test_svg_fallback_generator_attributes(self):
        desc = generate_svg_fallback("asset:test:1", "illustration", "16:9", "education", "Colour chapters")
        self.assertEqual(desc["aspect_ratio"], "16:9")
        self.assertEqual(desc["width"], 800)
        self.assertEqual(desc["height"], 450)
        self.assertIn("<svg", desc["svg_snippet"])
        self.assertIn("</svg>", desc["svg_snippet"])
        # Must not contain placeholder brackets or metadata leaks
        self.assertNotIn("[illustration | 16:9]", desc["svg_snippet"])


if __name__ == "__main__":
    unittest.main()

