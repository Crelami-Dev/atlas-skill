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


if __name__ == "__main__":
    unittest.main()
