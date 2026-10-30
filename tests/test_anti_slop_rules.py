#!/usr/bin/env python3
"""Atlas Phase 5 Test Suite — Context-Aware Anti-AI-Slop Intelligence.

Validates that anti-slop rules accurately catch generic AI tropes without
blindly penalizing legitimate contextual requirements (e.g. dashboards
need cards; developer tools need code/monospace).
"""
import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from runtime.anti_slop import audit_website_content
from runtime.contracts import normalize_brief


class TestAntiSlopRules(unittest.TestCase):

    def test_hard_failure_missing_viewport(self):
        html = "<html><head><title>No Viewport</title></head><body><h1>Hello</h1></body></html>"
        res = audit_website_content(html, "body { color: #000; }")
        self.assertEqual(res["status"], "FAIL")
        self.assertGreater(res["failures_count"], 0)
        rule_ids = [f["rule_id"] for f in res["findings"]]
        self.assertIn("missing-viewport", rule_ids)

    def test_hard_failure_unresolved_placeholder(self):
        html = "<meta name='viewport' content='width=device-width'><h1>{{project_name}}</h1>"
        res = audit_website_content(html, "body { color: #000; }")
        self.assertEqual(res["status"], "FAIL")
        rule_ids = [f["rule_id"] for f in res["findings"]]
        self.assertIn("unresolved-placeholder", rule_ids)

    def test_gradient_text_contextual_warning(self):
        html = "<meta name='viewport' content='width=device-width'><h1>Leading Enterprise</h1>"
        css = "h1 { background: linear-gradient(to right, red, blue); -webkit-background-clip: text; }"
        
        # Corporate brief: triggers WARN
        brief_corp = normalize_brief({"category": "enterprise", "tones": ["serious"]})
        res_corp = audit_website_content(html, css, brief_corp)
        finding_corp = next(f for f in res_corp["findings"] if f["rule_id"] == "gradient-text")
        self.assertEqual(finding_corp["severity"], "WARN")

        # Futuristic brief: triggers INFO with rationale
        brief_futuristic = normalize_brief({"category": "ai", "tones": ["futuristic"]})
        res_futuristic = audit_website_content(html, css, brief_futuristic)
        finding_futuristic = next(f for f in res_futuristic["findings"] if f["rule_id"] == "gradient-text")
        self.assertEqual(finding_futuristic["severity"], "INFO")
        self.assertIn("futuristic", finding_futuristic["context_rationale"].lower())

    def test_card_density_contextual_allowance(self):
        # 8 repetitive cards
        cards_html = "<div class='card'>Item</div>" * 8
        html = f"<meta name='viewport' content='width=device-width'><h1>Dashboard</h1>{cards_html}"
        css = ".card { padding: 10px; }"

        # Marketing brief: triggers WARN
        brief_mkt = normalize_brief({"page_type": "marketing", "category": "agency"})
        res_mkt = audit_website_content(html, css, brief_mkt)
        finding_mkt = next((f for f in res_mkt["findings"] if "card" in f["rule_id"]), None)
        self.assertIsNotNone(finding_mkt)
        self.assertEqual(finding_mkt["severity"], "WARN")

        # App / Dashboard brief: triggers INFO with rationale
        brief_app = normalize_brief({"page_type": "app", "category": "dashboard", "density": "high"})
        res_app = audit_website_content(html, css, brief_app)
        finding_app = next((f for f in res_app["findings"] if "card" in f["rule_id"]), None)
        self.assertIsNotNone(finding_app)
        self.assertEqual(finding_app["severity"], "INFO")
        self.assertIn("operational", finding_app["context_rationale"].lower())

    def test_clean_website_passes_cleanly(self):
        html = """<!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>Clean Brand</title>
        </head>
        <body>
          <header><div class="brand">Monument</div></header>
          <main>
            <h1>Clean Heading</h1>
            <p>Direct, truthful prose without buzzwords or excessive ornament.</p>
          </main>
        </body>
        </html>
        """
        css = ":root { --ink: #111; --bg: #f8f9fa; } body { color: var(--ink); background: var(--bg); font-family: sans-serif; }"
        brief = normalize_brief({"category": "culture", "tones": ["minimal"]})
        res = audit_website_content(html, css, brief)
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(res["failures_count"], 0)
        self.assertEqual(res["warnings_count"], 0)
        self.assertEqual(res["score"], 100)

    def test_multi_accent_three_distinct_accents_triggers_warning(self):
        # Case 1: Three distinct saturated accents in one container
        html = """<meta name="viewport" content="width=device-width">
        <div class="metrics-grid">
          <div class="card"><span style="color: #06b6d4;">Cyan Item</span></div>
          <div class="card"><span style="color: #10b981;">Emerald Item</span></div>
          <div class="card"><span style="color: #8b5cf6;">Purple Item</span></div>
        </div>"""
        res = audit_website_content(html, "")
        rule_ids = [f["rule_id"] for f in res["findings"]]
        self.assertIn("multi-accent-container", rule_ids)
        finding = next(f for f in res["findings"] if f["rule_id"] == "multi-accent-container")
        self.assertEqual(finding["severity"], "WARN")
        self.assertIn("metrics-grid", finding["message"])

    def test_multi_accent_one_or_two_accents_no_warning(self):
        # Case 2: One or two accents (or shades of same family) -> no warning
        html = """<meta name="viewport" content="width=device-width">
        <div class="metrics-grid">
          <div class="card"><span style="color: #06b6d4;">Cyan Item</span></div>
          <div class="card"><span style="color: #38bdf8;">Sky Item (Same Family)</span></div>
          <div class="card"><span style="color: #8b5cf6;">Purple Item</span></div>
        </div>"""
        res = audit_website_content(html, "")
        rule_ids = [f["rule_id"] for f in res["findings"]]
        self.assertNotIn("multi-accent-container", rule_ids)

    def test_multi_accent_equivalent_hex_rgb_normalized(self):
        # Case 3: Equivalent hex and RGB representations not counted as distinct
        html = """<meta name="viewport" content="width=device-width">
        <div class="card">
          <span style="color: #38bdf8;">Item 1</span>
          <span style="color: rgb(56, 189, 248);">Item 2</span>
          <span style="color: rgba(56, 189, 248, 0.85);">Item 3</span>
        </div>"""
        res = audit_website_content(html, "")
        rule_ids = [f["rule_id"] for f in res["findings"]]
        self.assertNotIn("multi-accent-container", rule_ids)

    def test_multi_accent_semantic_status_colors_exempt(self):
        # Case 4: Semantic status colors are not penalized as decorative accents
        html = """<meta name="viewport" content="width=device-width">
        <div class="status-summary">
          <div class="badge status-success" style="color: #10b981;">Operational</div>
          <div class="badge status-warning" style="color: #f59e0b;">Degraded</div>
          <div class="badge status-error" style="color: #ef4444;">Outage</div>
          <div class="badge status-info" style="color: #3b82f6;">Maintenance</div>
        </div>"""
        res = audit_website_content(html, "")
        rule_ids = [f["rule_id"] for f in res["findings"]]
        self.assertNotIn("multi-accent-container", rule_ids)

    def test_multi_accent_dataviz_chart_exempt(self):
        # Case 5: Multi-series charts and visualizations are legitimately multi-color
        html = """<meta name="viewport" content="width=device-width">
        <div class="chart-container" role="img" aria-label="Telemetry Chart">
          <svg class="line-chart">
            <path stroke="#06b6d4" d="M0,0 L10,10" />
            <path stroke="#10b981" d="M0,10 L10,0" />
            <path stroke="#8b5cf6" d="M0,5 L10,5" />
            <path stroke="#f59e0b" d="M0,8 L10,8" />
          </svg>
        </div>"""
        res = audit_website_content(html, "")
        rule_ids = [f["rule_id"] for f in res["findings"]]
        self.assertNotIn("multi-accent-container", rule_ids)

    def test_multi_accent_separate_components_not_combined(self):
        # Case 6: Accents across separate components are not bundled into one warning
        html = """<meta name="viewport" content="width=device-width">
        <main>
          <section class="hero"><span style="color: #06b6d4;">Hero Accent</span></section>
          <section class="features"><span style="color: #10b981;">Feature Accent</span></section>
          <section class="pricing"><span style="color: #8b5cf6;">Pricing Accent</span></section>
        </main>"""
        res = audit_website_content(html, "")
        rule_ids = [f["rule_id"] for f in res["findings"]]
        self.assertNotIn("multi-accent-container", rule_ids)

    def test_multi_accent_output_schema_and_contextual_rationale(self):
        # Case 7: Compatibility with output schema and brief rationale
        html = """<meta name="viewport" content="width=device-width">
        <div class="palette-showcase">
          <div class="tile" style="color: #ef4444;">Red</div>
          <div class="tile" style="color: #10b981;">Green</div>
          <div class="tile" style="color: #3b82f6;">Blue</div>
        </div>"""
        brief_playful = normalize_brief({"category": "creative", "tones": ["playful"]})
        res = audit_website_content(html, "", brief_playful)
        self.assertIn("status", res)
        self.assertIn("score", res)
        self.assertIn("findings", res)
        finding = next(f for f in res["findings"] if f["rule_id"] == "multi-accent-container")
        self.assertEqual(finding["severity"], "INFO")
        self.assertIn("context_rationale", finding)

    # -------------------------------------------------------------
    # P1.2 Corner Radius Consistency Tests
    # -------------------------------------------------------------

    def test_inconsistent_radius_peer_cards_warns(self):
        # Case 1: Peer cards in the same grid with inconsistent radii (8px vs 24px)
        html = """<meta name="viewport" content="width=device-width">
        <div class="pricing-grid">
          <div class="card" style="border-radius: 8px;">Plan A</div>
          <div class="card" style="border-radius: 24px;">Plan B</div>
        </div>"""
        res = audit_website_content(html, "")
        rule_ids = [f["rule_id"] for f in res["findings"]]
        self.assertIn("inconsistent-radius", rule_ids)
        finding = next(f for f in res["findings"] if f["rule_id"] == "inconsistent-radius")
        self.assertEqual(finding["severity"], "WARN")
        self.assertIn("pricing-grid", finding["message"])
        self.assertIn("8px", finding["message"])
        self.assertIn("24px", finding["message"])

    def test_inconsistent_radius_peer_cards_matching_passes(self):
        # Case 2: Peer cards sharing unified radius token
        html = """<meta name="viewport" content="width=device-width">
        <div class="card-grid">
          <div class="card rounded-lg">Card 1</div>
          <div class="card rounded-lg">Card 2</div>
          <div class="card rounded-lg">Card 3</div>
        </div>"""
        res = audit_website_content(html, "")
        rule_ids = [f["rule_id"] for f in res["findings"]]
        self.assertNotIn("inconsistent-radius", rule_ids)

    def test_inconsistent_radius_hierarchy_card_vs_button_passes(self):
        # Case 3: Legitimate intentional hierarchy (Card 16px, Button 6px)
        html = """<meta name="viewport" content="width=device-width">
        <div class="card" style="border-radius: 16px;">
          <h3>Feature</h3>
          <button class="btn" style="border-radius: 6px;">Action</button>
        </div>"""
        res = audit_website_content(html, "")
        rule_ids = [f["rule_id"] for f in res["findings"]]
        self.assertNotIn("inconsistent-radius", rule_ids)

    def test_inconsistent_radius_card_with_avatar_pill_passes(self):
        # Case 4: Card containing circular avatar (50%) and pill badge (9999px)
        html = """<meta name="viewport" content="width=device-width">
        <div class="card-grid">
          <div class="card" style="border-radius: 12px;">
            <img class="avatar" style="border-radius: 50%;" src="user.png" alt="User">
            <span class="badge" style="border-radius: 9999px;">Active</span>
          </div>
          <div class="card" style="border-radius: 12px;">
            <img class="avatar" style="border-radius: 50%;" src="user2.png" alt="User 2">
            <span class="badge" style="border-radius: 9999px;">Pending</span>
          </div>
        </div>"""
        res = audit_website_content(html, "")
        rule_ids = [f["rule_id"] for f in res["findings"]]
        self.assertNotIn("inconsistent-radius", rule_ids)

    def test_inconsistent_radius_separate_sections_not_aggregated(self):
        # Case 5: Different sections with intentional distinct radii do not aggregate
        html = """<meta name="viewport" content="width=device-width">
        <main>
          <section id="hero">
            <div class="card" style="border-radius: 16px;">Hero Card</div>
          </section>
          <section id="features">
            <div class="card" style="border-radius: 8px;">Feature Card</div>
          </section>
        </main>"""
        res = audit_website_content(html, "")
        rule_ids = [f["rule_id"] for f in res["findings"]]
        self.assertNotIn("inconsistent-radius", rule_ids)

    def test_inconsistent_radius_css_variable_token_normalization(self):
        # Case 6: Token normalization resolves CSS variable and matching px value
        html = """<meta name="viewport" content="width=device-width">
        <div class="grid">
          <div class="card" style="border-radius: var(--radius-md);">Card 1</div>
          <div class="card" style="border-radius: 8px;">Card 2</div>
        </div>"""
        css = ":root { --radius-md: 8px; }"
        res = audit_website_content(html, css)
        rule_ids = [f["rule_id"] for f in res["findings"]]
        self.assertNotIn("inconsistent-radius", rule_ids)

    def test_inconsistent_radius_output_schema_and_asymmetric_tone(self):
        # Case 7: Schema compliance and INFO severity when asymmetric/eclectic tone
        html = """<meta name="viewport" content="width=device-width">
        <div class="hero-mosaic">
          <div class="card" style="border-radius: 4px;">Mosaic A</div>
          <div class="card" style="border-radius: 24px;">Mosaic B</div>
        </div>"""
        brief_asymmetric = normalize_brief({"category": "creative", "tones": ["asymmetric"]})
        res = audit_website_content(html, "", brief_asymmetric)
        self.assertIn("status", res)
        self.assertIn("score", res)
        self.assertIn("findings", res)
        finding = next(f for f in res["findings"] if f["rule_id"] == "inconsistent-radius")
        self.assertEqual(finding["severity"], "INFO")
        self.assertIn("context_rationale", finding)
        self.assertIn("asymmetric", finding["message"])

    def test_inconsistent_radius_mixed_pill_and_rect_controls_warns(self):
        # Fix B regression: Exact toolbar with 1 pill button and 1 rect button must trigger warning
        html = """<meta name="viewport" content="width=device-width">
        <div class="toolbar">
          <button class="btn rounded-md">Cancel</button>
          <button class="btn rounded-full">Confirm</button>
        </div>"""
        res = audit_website_content(html, "")
        rule_ids = [f["rule_id"] for f in res["findings"]]
        self.assertIn("inconsistent-radius", rule_ids)
        finding = next(f for f in res["findings"] if f["rule_id"] == "inconsistent-radius")
        self.assertEqual(finding["severity"], "WARN")
        self.assertIn("toolbar", finding["message"])
        self.assertIn("rounded-full", finding["message"])

    def test_inconsistent_radius_avatar_remains_exempt_from_card_warning(self):
        # Fix B regression: Circular avatars (rounded-full / 50%) on non-interactive elements remain exempt
        html = """<meta name="viewport" content="width=device-width">
        <div class="card-grid">
          <div class="card" style="border-radius: 12px;">
            <img class="avatar rounded-full" src="user1.png" alt="User 1">
            <span class="user-name">Alice</span>
          </div>
          <div class="card" style="border-radius: 12px;">
            <img class="avatar rounded-full" src="user2.png" alt="User 2">
            <span class="user-name">Bob</span>
          </div>
        </div>"""
        res = audit_website_content(html, "")
        rule_ids = [f["rule_id"] for f in res["findings"]]
        self.assertNotIn("inconsistent-radius", rule_ids)


if __name__ == "__main__":
    unittest.main()
