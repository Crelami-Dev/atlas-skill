#!/usr/bin/env python3
"""Atlas Runtime Engine — Unit Tests for Website Generator."""
import json
import os
import sys
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from runtime.composer import compose_design_plan
from runtime.contracts import normalize_brief
from runtime.generator import generate_website, render_css, render_html, render_js
from runtime.loader import load_library


class TestWebsiteGenerator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = load_library()
        cls.brief = normalize_brief({
            "project_name": "Apex Finance",
            "category": "fintech",
            "tones": ["bold", "luxury"],
            "density": "med"
        })
        cls.plan = compose_design_plan(cls.brief, cls.lib)

    def test_generate_website_creates_expected_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            res = generate_website(self.plan, tmpdir)
            self.assertEqual(res["status"], "SUCCESS")
            self.assertGreaterEqual(res["assets_generated"], 1)

            index_path = os.path.join(tmpdir, "index.html")
            css_path = os.path.join(tmpdir, "styles.css")
            js_path = os.path.join(tmpdir, "script.js")
            manifest_path = os.path.join(tmpdir, "assets", "manifest.json")

            self.assertTrue(os.path.isfile(index_path))
            self.assertTrue(os.path.isfile(css_path))
            self.assertTrue(os.path.isfile(js_path))
            self.assertTrue(os.path.isfile(manifest_path))

            # Check non-empty byte sizes
            self.assertGreater(os.path.getsize(index_path), 5000)
            self.assertGreater(os.path.getsize(css_path), 3000)
            self.assertGreater(os.path.getsize(js_path), 500)

    def test_index_html_contains_brief_content_and_semantics(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            generate_website(self.plan, tmpdir)
            with open(os.path.join(tmpdir, "index.html"), "r", encoding="utf-8") as f:
                html = f.read()

            self.assertIn("Apex Finance", html)
            self.assertIn("<header", html)
            self.assertIn("<main", html)
            self.assertIn("<footer", html)
            self.assertIn('class="btn btn-primary"', html)
            self.assertIn('aria-expanded="false"', html)
            # Fonts preconnect link
            self.assertTrue("fonts.googleapis.com" in html or "api.fontshare.com" in html)

    def test_css_contains_plan_tokens_and_responsive_queries(self):
        css = render_css(self.plan)
        tokens = self.plan["palette"]["tokens"]

        self.assertIn(tokens["bg"], css)
        self.assertIn(tokens["accent"], css)
        self.assertIn(":root", css)
        self.assertIn("@media (max-width: 768px)", css)
        self.assertIn(":focus-visible", css)

    def test_vanilla_js_accessible_handlers(self):
        js = render_js()
        self.assertIn("navToggle", js)
        self.assertIn("aria-expanded", js)
        self.assertIn("Escape", js)
        self.assertIn("faqItems", js)

    def test_remediation_no_placeholders_or_invented_metrics_in_generated_output(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            generate_website(self.plan, tmpdir)

            with open(os.path.join(tmpdir, "index.html"), "r", encoding="utf-8") as f:
                html = f.read()

            # Finding 2: Zero placeholder leakage in HTML
            self.assertNotIn("Dressed as something else", html)
            self.assertNotIn("[photo | 16:9]", html)
            self.assertNotIn("[hero_graphic | 16:9]", html)
            self.assertNotIn("Dressed as", html)

            # Finding 3: Zero invented business metrics
            self.assertNotIn("99.99%", html)
            self.assertNotIn("10M+", html)
            self.assertNotIn("3.2x", html)

            # Finding 4: Concrete fintech SVG asset generated
            svg_files = [f for f in os.listdir(os.path.join(tmpdir, "assets")) if f.endswith(".svg")]
            self.assertGreaterEqual(len(svg_files), 1)

            for svg_name in svg_files:
                with open(os.path.join(tmpdir, "assets", svg_name), "r", encoding="utf-8") as sf:
                    svg_content = sf.read()
                # Must not contain placeholder text
                self.assertNotIn("Dressed as something else", svg_content)
                self.assertNotIn("[photo | 16:9]", svg_content)
                self.assertNotIn("[hero_graphic | 16:9]", svg_content)
                # Must contain institutional treasury architectural elements without fabricated metrics
                self.assertIn("<svg", svg_content)
                self.assertIn("</svg>", svg_content)
                self.assertIn('role="img"', svg_content)
                self.assertIn("INSTITUTIONAL TREASURY ARCHITECTURE", svg_content)
                self.assertIn("MULTI-SIG VERIFIED", svg_content)
                # Must NOT contain fabricated quantitative metrics or fake chart curves
                self.assertNotIn("$2,485,920.00 USD", svg_content)
                self.assertNotIn("+14.8% APY", svg_content)
                self.assertNotIn("$2.50M", svg_content)
                self.assertNotIn("Peak: $2.51M", svg_content)

    def test_zero_asset_plan_omits_hero_image_reference(self):
        # Case A1: When composition has 0 asset requirements, no broken hero img is emitted
        app_brief = normalize_brief({
            "project_name": "Cloud Monitor",
            "category": "saas",
            "page_type": "app",
            "density": "high",
            "tones": ["minimal", "precise"]
        })
        app_plan = compose_design_plan(app_brief, self.lib)
        self.assertEqual(app_plan["assets"]["summary"]["total_required"], 0)

        with tempfile.TemporaryDirectory() as tmpdir:
            res = generate_website(app_plan, tmpdir)
            self.assertEqual(res["status"], "SUCCESS")
            with open(os.path.join(tmpdir, "index.html"), "r", encoding="utf-8") as f:
                html = f.read()

            self.assertNotIn("assets/hero.svg", html)
            self.assertNotIn('<div class="hero-media">', html)
            self.assertIn("hero-grid-single", html)

    def test_asset_required_plan_preserves_hero_image_reference(self):
        # Case A2: When composition requires visual asset, image reference is preserved
        with tempfile.TemporaryDirectory() as tmpdir:
            res = generate_website(self.plan, tmpdir)
            self.assertEqual(res["status"], "SUCCESS")
            with open(os.path.join(tmpdir, "index.html"), "r", encoding="utf-8") as f:
                html = f.read()

            self.assertIn('<div class="hero-media">', html)
            self.assertIn('<img src="assets/', html)
            svg_files = [f for f in os.listdir(os.path.join(tmpdir, "assets")) if f.endswith(".svg")]
            self.assertGreaterEqual(len(svg_files), 1)


if __name__ == "__main__":
    unittest.main()

