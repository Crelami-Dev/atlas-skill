#!/usr/bin/env python3
"""Atlas Skill P6 — Bento Grid Layout & Visual Polish Test Suite.

Covers:
1. Anti-slop radius threshold invariants (diff >= 4.0 AND ratio >= 1.5) and AST scoping.
2. Anti-slop multi-accent violation detection vs. intentional dataviz/semantic exemptions.
3. Composition selection routing (atlas:features-bento vs. conventional .features-grid).
4. Semantic tile hierarchy, accessibility heading order, and variable tile counts (>= 4).
5. Content integrity (no unsupported benchmark claims or fabricated metrics).
6. Real browser-rendered assertions via Headless Chrome CDP across:
   - Desktop (1440 x 900)
   - Tablet (768 x 1024)
   - Mobile (390 x 844) — 2-column Bento contract with at most 2 full-width tiles
   - Intentional inner horizontal scroll container vs. accidental page-level overflow
"""
import copy
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from runtime.anti_slop import (
    DOMTreeBuilder,
    audit_website_content,
    find_inconsistent_radius_containers,
    find_multi_accent_containers,
)
from runtime.composer import compose_design_plan
from runtime.contracts import normalize_brief
from runtime.generator import generate_website, render_css, render_html
from runtime.loader import load_library

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CDP_MODULE_PATH = os.path.join(REPO_ROOT, "runtime", "browser_cdp.mjs")


class TestBentoGridLayout(unittest.TestCase):
    """Test suite for P6 Advanced Bento Grid Layouts & Visual Polish."""

    @classmethod
    def setUpClass(cls):
        cls.lib = load_library()

        # Plan A: Explicitly selects atlas:features-bento
        cls.bento_brief = normalize_brief({
            "project_name": "Nexus Engine",
            "category": "tech",
            "page_type": "marketing",
            "tones": ["modern", "energetic", "friendly"],
            "density": "med",
            "explicit_constraints": {
                "required_patterns": ["atlas:features-bento"]
            }
        })
        cls.bento_plan = compose_design_plan(cls.bento_brief, cls.lib)

        # Plan B: Conventional non-bento features pattern
        cls.conventional_brief = normalize_brief({
            "project_name": "Standard Platform",
            "category": "saas",
            "page_type": "marketing",
            "tones": ["minimal", "precise"],
            "density": "med",
            "exclude": ["atlas:features-bento"]
        })
        cls.conventional_plan = compose_design_plan(cls.conventional_brief, cls.lib)

        # Run browser-rendered CDP inspection once for the generated Bento site
        cls.cdp_metrics = cls._capture_cdp_bento_metrics()

    @classmethod
    def _capture_cdp_bento_metrics(cls):
        """Render the Bento website in a temporary directory and inspect via Chrome CDP."""
        tmpdir = tempfile.mkdtemp(prefix="atlas_p6_bento_test_")
        try:
            generate_website(cls.bento_plan, tmpdir)

            # Create a second page variant with an intentional horizontal scroll container inside a tile
            index_path = os.path.join(tmpdir, "index.html")
            scroll_html_path = os.path.join(tmpdir, "scroll_variant.html")
            with open(index_path, "r", encoding="utf-8") as f:
                raw_html = f.read()

            scroll_snippet = (
                '<div class="bento-code-scroll" style="overflow-x: auto; max-width: 100%;">'
                '<div class="inner-wide-spec" style="width: 600px;">'
                'scroll-container-specification-line'
                '</div></div>'
            )
            if 'class="bento-tile' in raw_html:
                # Inject intentional scroll container inside the first bento-tile
                modified_html = re.sub(
                    r'(<div[^>]*class="[^"]*\bbento-tile\b[^"]*"[^>]*>)',
                    r"\1" + scroll_snippet,
                    raw_html,
                    count=1
                )
            else:
                modified_html = raw_html.replace("</main>", scroll_snippet + "</main>")

            with open(scroll_html_path, "w", encoding="utf-8") as f:
                f.write(modified_html)

            node_script = """
import { pathToFileURL } from 'node:url';

const cdpUrl = pathToFileURL(process.env.CDP_MODULE_PATH).href;
const { launchCDPBrowser, startStaticServer, IN_BROWSER_COLLISION_SCRIPT } = await import(cdpUrl);

const siteDir = process.env.SITE_DIR;
const server = await startStaticServer(siteDir);
const browser = await launchCDPBrowser({ width: 1440, height: 900 });

const IN_BROWSER_BENTO_INSPECT = `(() => {
  const root = document.documentElement;
  const grid = document.querySelector('.bento-grid');
  if (!grid) {
    return {
      hasBentoGrid: false,
      scrollWidth: root.scrollWidth,
      innerWidth: window.innerWidth,
      clientWidth: root.clientWidth
    };
  }
  const gridStyle = window.getComputedStyle(grid);
  const templateCols = gridStyle.gridTemplateColumns
    ? gridStyle.gridTemplateColumns.trim().split(/\\\\s+/).filter(Boolean)
    : [];
  const gridRect = grid.getBoundingClientRect();

  const tiles = Array.from(grid.querySelectorAll('.bento-tile')).map((el) => {
    const r = el.getBoundingClientRect();
    return {
      className: el.className,
      isLead: el.classList.contains('bento-tile-lead'),
      isWide: el.classList.contains('bento-tile-wide'),
      isStandard: el.classList.contains('bento-tile-standard'),
      left: r.left,
      top: r.top,
      right: r.right,
      bottom: r.bottom,
      width: r.width,
      height: r.height,
      area: r.width * r.height
    };
  });

  const scrollEl = document.querySelector('.bento-code-scroll');
  const scrollMetrics = scrollEl ? {
    scrollWidth: scrollEl.scrollWidth,
    clientWidth: scrollEl.clientWidth,
    overflowX: window.getComputedStyle(scrollEl).overflowX
  } : null;

  return {
    hasBentoGrid: true,
    columnCount: templateCols.length,
    templateCols,
    scrollWidth: root.scrollWidth,
    innerWidth: window.innerWidth,
    clientWidth: root.clientWidth,
    gridRect: {
      left: gridRect.left,
      top: gridRect.top,
      right: gridRect.right,
      bottom: gridRect.bottom,
      width: gridRect.width,
      height: gridRect.height
    },
    tiles,
    scrollMetrics
  };
})()`;

try {
  await browser.send('Page.enable');
  await browser.send('DOM.enable');

  const configs = [
    { key: 'desktop', width: 1440, height: 900, mobile: false, page: '/index.html' },
    { key: 'tablet', width: 768, height: 1024, mobile: false, page: '/index.html' },
    { key: 'mobile', width: 390, height: 844, mobile: true, page: '/index.html' },
    { key: 'mobile_scroll', width: 390, height: 844, mobile: true, page: '/scroll_variant.html' }
  ];

  const results = {};
  for (const cfg of configs) {
    await browser.send('Emulation.setDeviceMetricsOverride', {
      width: cfg.width,
      height: cfg.height,
      deviceScaleFactor: 2,
      mobile: cfg.mobile
    });
    await browser.send('Page.navigate', { url: server.origin + cfg.page });
    await new Promise((r) => setTimeout(r, 450));

    const bentoEval = await browser.send('Runtime.evaluate', {
      expression: IN_BROWSER_BENTO_INSPECT,
      returnByValue: true
    });
    const collisionEval = await browser.send('Runtime.evaluate', {
      expression: IN_BROWSER_COLLISION_SCRIPT,
      returnByValue: true
    });

    results[cfg.key] = {
      bento: bentoEval.result.value,
      collision: collisionEval.result.value
    };
  }

  console.log(JSON.stringify(results));
} finally {
  await browser.close();
  await server.close();
}
"""
            env = os.environ.copy()
            env["CDP_MODULE_PATH"] = CDP_MODULE_PATH
            env["SITE_DIR"] = tmpdir
            proc = subprocess.run(
                ["node", "--input-type=module", "-e", node_script],
                env=env,
                capture_output=True,
                text=True,
                timeout=45
            )
            if proc.returncode != 0:
                return {"error": proc.stderr or proc.stdout}
            return json.loads(proc.stdout.strip().splitlines()[-1])
        except Exception as exc:
            return {"error": str(exc)}
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    # =========================================================================
    # A. Anti-Slop Behavioral & Threshold Invariant Tests
    # =========================================================================

    def test_anti_slop_bento_radius_violation_detected_above_threshold(self):
        """1. Verify inconsistent-radius triggers on .bento-grid when diff >= 4.0 AND ratio >= 1.5."""
        html = """<meta name="viewport" content="width=device-width">
        <section id="features">
          <div class="bento-grid">
            <div class="bento-tile tile-a">Lead Tile</div>
            <div class="bento-tile tile-b">Support Tile</div>
          </div>
        </section>"""

        # Case 1: --radius-md (12px) vs --radius-lg (20px) -> diff = 8.0, ratio = 1.67
        css_case_1 = """
        :root { --radius-md: 12px; --radius-lg: 20px; }
        .tile-a { border-radius: var(--radius-md); }
        .tile-b { border-radius: var(--radius-lg); }
        """
        res_1 = audit_website_content(html, css_case_1)
        findings_1 = [f for f in res_1["findings"] if f["rule_id"] == "inconsistent-radius"]
        self.assertEqual(len(findings_1), 1, "Expected inconsistent-radius for 12px vs 20px on bento tiles")
        self.assertEqual(findings_1[0]["severity"], "WARN")
        self.assertIn("bento-grid", findings_1[0]["message"])

        # Case 2: Exact boundary 8px vs 12px -> diff = 4.0, ratio = 1.50
        css_case_2 = """
        .tile-a { border-radius: 8px; }
        .tile-b { border-radius: 12px; }
        """
        res_2 = audit_website_content(html, css_case_2)
        findings_2 = [f for f in res_2["findings"] if f["rule_id"] == "inconsistent-radius"]
        self.assertEqual(len(findings_2), 1, "Expected inconsistent-radius at exact boundary 8px vs 12px")
        self.assertEqual(findings_2[0]["severity"], "WARN")

    def test_anti_slop_bento_radius_passes_below_delta_or_ratio_threshold(self):
        """2. Verify inconsistent-radius does NOT trigger when diff < 4.0 OR ratio < 1.5."""
        html = """<meta name="viewport" content="width=device-width">
        <section id="features">
          <div class="bento-grid">
            <div class="bento-tile bento-tile-lead">Lead Tile</div>
            <div class="bento-tile bento-tile-standard">Standard Tile</div>
          </div>
        </section>"""

        # Sub-case A: diff = 4.0 (16 - 12), but ratio = 1.33 (< 1.5)
        css_sub_a = """
        .bento-tile-lead { border-radius: 16px; }
        .bento-tile-standard { border-radius: 12px; }
        """
        res_a = audit_website_content(html, css_sub_a)
        self.assertNotIn("inconsistent-radius", [f["rule_id"] for f in res_a["findings"]])

        # Sub-case B: ratio = 1.5 (6 / 4), but diff = 2.0 (< 4.0)
        css_sub_b = """
        .bento-tile-lead { border-radius: 6px; }
        .bento-tile-standard { border-radius: 4px; }
        """
        res_b = audit_website_content(html, css_sub_b)
        self.assertNotIn("inconsistent-radius", [f["rule_id"] for f in res_b["findings"]])

        # Sub-case C: Unified var(--radius-md) with pill badge inside tile
        html_with_badge = """<meta name="viewport" content="width=device-width">
        <div class="bento-grid">
          <div class="bento-tile"><span class="badge" style="border-radius: 9999px;">Tag</span></div>
          <div class="bento-tile">Standard</div>
        </div>"""
        css_sub_c = ":root { --radius-md: 12px; } .bento-tile { border-radius: var(--radius-md); }"
        res_c = audit_website_content(html_with_badge, css_sub_c)
        self.assertNotIn("inconsistent-radius", [f["rule_id"] for f in res_c["findings"]])

    def test_anti_slop_bento_multi_accent_violation_vs_intentional_exemptions(self):
        """3. Verify multi-accent-container catches >= 3 saturated accents on tiles while exempting dataviz/status."""
        # Violation case: 3 distinct saturated accent families (red, green, blue) on bento tiles
        html_violation = """<meta name="viewport" content="width=device-width">
        <div class="bento-grid">
          <div class="bento-tile" style="border-color: #ef4444; color: #ef4444;">Red Tile</div>
          <div class="bento-tile" style="border-color: #10b981; color: #10b981;">Green Tile</div>
          <div class="bento-tile" style="border-color: #3b82f6; color: #3b82f6;">Blue Tile</div>
        </div>"""
        res_viol = audit_website_content(html_violation, "")
        viol_Ids = [f["rule_id"] for f in res_viol["findings"]]
        self.assertIn("multi-accent-container", viol_Ids)

        # Valid case: 1 brand accent (#3b82f6), neutral slate surfaces, plus multi-color SVG diagram and status badge
        html_valid = """<meta name="viewport" content="width=device-width">
        <div class="bento-grid">
          <div class="bento-tile" style="background-color: #0f172a; color: #3b82f6;">
            <svg role="img" aria-label="Architecture diagram">
              <rect fill="#ef4444" width="10" height="10"/>
              <rect fill="#10b981" width="10" height="10"/>
            </svg>
          </div>
          <div class="bento-tile" style="background-color: #1e293b; color: #f8fafc;">
            <span class="badge-success" style="color: #10b981;">Verified</span>
          </div>
          <div class="bento-tile" style="background-color: #1e293b; color: #94a3b8;">
            Neutral Tile
          </div>
        </div>"""
        res_valid = audit_website_content(html_valid, "")
        valid_ids = [f["rule_id"] for f in res_valid["findings"]]
        self.assertNotIn("multi-accent-container", valid_ids)

    def test_generated_bento_website_passes_anti_slop_audit_cleanly(self):
        """4. Verify generated Bento HTML/CSS is actively scoped by DOMTreeBuilder and passes anti_slop."""
        html = render_html(self.bento_plan, {"assets": []})
        css = render_css(self.bento_plan)

        # Parse CSS tokens & class radii to confirm AST actually extracts card radii on .bento-tile
        parser = DOMTreeBuilder()
        parser.feed(html)
        bento_containers = [
            n for n in parser.all_nodes
            if "bento-grid" in n.attrs.get("class", "").split()
        ]
        self.assertEqual(len(bento_containers), 1, "Generated HTML must contain one .bento-grid container")

        bento_node = bento_containers[0]
        has_child_sections = any(c.tag in ("section", "article") for c in bento_node.children)
        self.assertFalse(
            has_child_sections,
            ".bento-grid children must not be <article>/<section> tags that bypass anti_slop container scoping"
        )

        bento_cards = [
            ch for ch in bento_node.children
            if ch.get_role_family() == "card"
        ]
        self.assertGreaterEqual(len(bento_cards), 4, "Bento grid must contain at least 4 auditable card tiles")

        res = audit_website_content(html, css, self.bento_brief)
        rule_ids = [f["rule_id"] for f in res["findings"]]
        self.assertNotIn("inconsistent-radius", rule_ids)
        self.assertNotIn("multi-accent-container", rule_ids)

    # =========================================================================
    # B. Composition Contract, Hierarchy & Content Integrity Tests
    # =========================================================================

    def test_bento_selected_only_when_composition_plan_chooses_features_bento(self):
        """5. Verify .bento-grid renders only when atlas:features-bento is selected in plan slots."""
        feat_slot_bento = next(
            s for s in self.bento_plan["composition"]["slots"] if s["slot"] == "features"
        )
        self.assertEqual(feat_slot_bento["pattern_id"], "atlas:features-bento")

        bento_html = render_html(self.bento_plan, {"assets": []})
        self.assertIn('class="bento-grid"', bento_html)
        self.assertNotIn('class="features-grid"', bento_html)

        feat_slot_conv = next(
            s for s in self.conventional_plan["composition"]["slots"] if s["slot"] == "features"
        )
        self.assertNotEqual(feat_slot_conv["pattern_id"], "atlas:features-bento")

        conv_html = render_html(self.conventional_plan, {"assets": []})
        self.assertIn('class="features-grid"', conv_html)
        self.assertNotIn('class="bento-grid"', conv_html)

    def test_bento_semantic_hierarchy_and_accessibility_contract(self):
        """6. Verify mixed-size tile roles, non-link tiles, heading order (h2 -> h3), and lead SVG graphic."""
        html = render_html(self.bento_plan, {"assets": []})
        parser = DOMTreeBuilder()
        parser.feed(html)

        bento_grid = next(
            (n for n in parser.all_nodes if "bento-grid" in n.attrs.get("class", "").split()),
            None
        )
        self.assertIsNotNone(bento_grid, "Expected .bento-grid element in rendered HTML")

        tiles = [ch for ch in bento_grid.children if "bento-tile" in ch.attrs.get("class", "").split()]
        self.assertGreaterEqual(len(tiles), 4, "Bento grid must have at least 4 tiles")

        # Tiles must not all be <a> links
        link_tiles = [t for t in tiles if t.tag == "a"]
        self.assertEqual(len(link_tiles), 0, "Bento tiles must not be raw <a> wrapper links")

        # Role distribution: 1 lead tile, 1 wide tile, >= 2 standard tiles
        lead_tiles = [t for t in tiles if "bento-tile-lead" in t.attrs.get("class", "").split()]
        wide_tiles = [t for t in tiles if "bento-tile-wide" in t.attrs.get("class", "").split()]
        std_tiles = [t for t in tiles if "bento-tile-standard" in t.attrs.get("class", "").split()]

        self.assertEqual(len(lead_tiles), 1, "Expected exactly 1 .bento-tile-lead")
        self.assertEqual(len(wide_tiles), 1, "Expected exactly 1 .bento-tile-wide")
        self.assertGreaterEqual(len(std_tiles), 2, "Expected at least 2 .bento-tile-standard tiles")

        # Heading order inside each tile: must contain an <h3>
        for idx, tile in enumerate(tiles):
            h3_children = [c for c in tile.children if c.tag == "h3"]
            self.assertGreaterEqual(len(h3_children), 1, f"Tile #{idx + 1} must contain an <h3> heading")

        # Lead tile must contain an architectural <svg role="img">
        lead_svgs = [c for c in lead_tiles[0].children if c.tag == "svg" and c.attrs.get("role") == "img"]
        self.assertGreaterEqual(len(lead_svgs), 1, "Lead tile must include an accessible <svg role='img'> diagram")

    def test_bento_supports_variable_tile_counts_minimum_four(self):
        """7. Verify Bento generator supports variable item counts (4, 5, 6) without exceeding 2 full-width mobile tiles."""
        for count in (4, 5, 6):
            custom_plan = copy.deepcopy(self.bento_plan)
            custom_plan["bento_items"] = [
                {"title": f"Capability {i + 1}", "description": f"Verifiable capability description {i + 1}."}
                for i in range(count)
            ]
            html = render_html(custom_plan, {"assets": []})
            parser = DOMTreeBuilder()
            parser.feed(html)

            bento_grid = next(
                (n for n in parser.all_nodes if "bento-grid" in n.attrs.get("class", "").split()),
                None
            )
            self.assertIsNotNone(bento_grid, f"Expected .bento-grid for count={count}")
            tiles = [ch for ch in bento_grid.children if "bento-tile" in ch.attrs.get("class", "").split()]
            self.assertEqual(len(tiles), count, f"Expected exactly {count} rendered tiles")

            full_width_mobile_tiles = [
                t for t in tiles
                if any(c in t.attrs.get("class", "").split() for c in ("bento-tile-lead", "bento-tile-wide"))
            ]
            self.assertLessEqual(
                len(full_width_mobile_tiles), 2,
                f"At most 2 full-width mobile tiles allowed for count={count}"
            )

    def test_bento_content_integrity_no_fabricated_metrics_or_unsupported_claims(self):
        """8. Verify rendered Bento HTML contains no unsupported benchmark claims or fabricated metrics."""
        html = render_html(self.bento_plan, {"assets": []})
        self.assertIn('class="bento-grid"', html)

        forbidden_phrases = [
            "Zero Framework Overhead",
            "100% Deterministic",
            "99.99%",
            "+14.8%",
            "$2,485,920",
            "$2.48M",
            "[photo",
            "[hero_graphic",
        ]
        for phrase in forbidden_phrases:
            self.assertNotIn(phrase, html, f"Forbidden claim or placeholder '{phrase}' found in HTML")

    # =========================================================================
    # C. Browser-Rendered Assertions via Headless Chrome CDP
    # =========================================================================

    def test_bento_browser_rendered_desktop_1440x900_layout(self):
        """9. Verify computed 3-column layout and lead/wide/standard bounding boxes at Desktop 1440x900."""
        self.assertNotIn("error", self.cdp_metrics, f"CDP runner error: {self.cdp_metrics.get('error')}")
        desk = self.cdp_metrics["desktop"]["bento"]
        coll = self.cdp_metrics["desktop"]["collision"]

        self.assertTrue(desk["hasBentoGrid"], "Desktop DOM must contain .bento-grid")
        self.assertEqual(desk["columnCount"], 3, f"Desktop .bento-grid must have 3 columns, got {desk['templateCols']}")
        self.assertEqual(desk["scrollWidth"], desk["clientWidth"], "Desktop must not have horizontal page overflow")
        self.assertLessEqual(desk["scrollWidth"], desk["innerWidth"], "Desktop scrollWidth must not exceed innerWidth")
        self.assertFalse(coll["hasPageOverflow"])
        self.assertEqual(coll["collisionCount"], 0, f"Desktop collisions detected: {coll['collisions']}")

        lead = next((t for t in desk["tiles"] if t["isLead"]), None)
        wide = next((t for t in desk["tiles"] if t["isWide"]), None)
        stds = [t for t in desk["tiles"] if t["isStandard"]]

        self.assertIsNotNone(lead)
        self.assertIsNotNone(wide)
        self.assertGreaterEqual(len(stds), 2)

        std_ref = stds[0]
        self.assertGreater(lead["width"], std_ref["width"] * 1.8, "Lead tile must span 2 columns on desktop")
        self.assertGreater(lead["height"], std_ref["height"] * 1.5, "Lead tile must span 2 rows on desktop")
        self.assertGreater(wide["width"], std_ref["width"] * 1.8, "Wide tile must span 2 columns on desktop")

        max_std_area = max(s["area"] for s in stds)
        self.assertGreater(lead["area"], max_std_area * 3.0, "Lead tile area must dominate standard tiles (> 3x)")

        # Every tile must stay inside grid bounds
        g = desk["gridRect"]
        for t in desk["tiles"]:
            self.assertGreaterEqual(t["left"], g["left"] - 1.5)
            self.assertLessEqual(t["right"], g["right"] + 1.5)

    def test_bento_browser_rendered_tablet_768x1024_layout(self):
        """10. Verify computed 2-column layout and side-by-side standard tiles at Tablet 768x1024."""
        self.assertNotIn("error", self.cdp_metrics, f"CDP runner error: {self.cdp_metrics.get('error')}")
        tab = self.cdp_metrics["tablet"]["bento"]
        coll = self.cdp_metrics["tablet"]["collision"]

        self.assertTrue(tab["hasBentoGrid"], "Tablet DOM must contain .bento-grid")
        self.assertEqual(tab["columnCount"], 2, f"Tablet .bento-grid must have 2 columns, got {tab['templateCols']}")
        self.assertEqual(tab["scrollWidth"], tab["clientWidth"], "Tablet must not have horizontal page overflow")
        self.assertLessEqual(tab["scrollWidth"], tab["innerWidth"], "Tablet scrollWidth must not exceed innerWidth")
        self.assertFalse(coll["hasPageOverflow"])
        self.assertEqual(coll["collisionCount"], 0, f"Tablet collisions detected: {coll['collisions']}")

        g = tab["gridRect"]
        lead = next((t for t in tab["tiles"] if t["isLead"]), None)
        wide = next((t for t in tab["tiles"] if t["isWide"]), None)
        stds = [t for t in tab["tiles"] if t["isStandard"]]

        self.assertAlmostEqual(lead["width"], g["width"], delta=2.0, msg="Lead tile must span 2 columns on tablet")
        self.assertAlmostEqual(wide["width"], g["width"], delta=2.0, msg="Wide tile must span 2 columns on tablet")

        # Verify at least two standard tiles sit side-by-side on the same row
        side_by_side_found = False
        for i in range(len(stds)):
            for j in range(i + 1, len(stds)):
                if abs(stds[i]["top"] - stds[j]["top"]) <= 2.0 and abs(stds[i]["left"] - stds[j]["left"]) > 20.0:
                    side_by_side_found = True
                    break
        self.assertTrue(side_by_side_found, "Expected standard tiles to sit side-by-side in 2 columns on tablet")

    def test_bento_browser_rendered_mobile_390x844_two_column_and_max_two_full_width(self):
        """11. Verify mobile 390x844 contract: 2-column Bento grid with at most 2 full-width tiles."""
        self.assertNotIn("error", self.cdp_metrics, f"CDP runner error: {self.cdp_metrics.get('error')}")
        mob = self.cdp_metrics["mobile"]["bento"]
        coll = self.cdp_metrics["mobile"]["collision"]

        self.assertTrue(mob["hasBentoGrid"], "Mobile DOM must contain .bento-grid")
        self.assertEqual(
            mob["columnCount"], 2,
            f"Mobile 390x844 must render a 2-column Bento grid, got {mob['templateCols']}"
        )
        self.assertEqual(mob["scrollWidth"], mob["innerWidth"], "Mobile 390x844 must not overflow horizontally")
        self.assertFalse(coll["hasPageOverflow"])
        self.assertEqual(coll["collisionCount"], 0, f"Mobile collisions detected: {coll['collisions']}")

        g = mob["gridRect"]
        full_width_tiles = [t for t in mob["tiles"] if t["width"] >= g["width"] * 0.85]
        half_width_tiles = [t for t in mob["tiles"] if t["width"] <= g["width"] * 0.55]

        self.assertGreaterEqual(len(full_width_tiles), 1, "Mobile bento must have at least 1 full-width focal tile")
        self.assertLessEqual(
            len(full_width_tiles), 2,
            f"Mobile bento contract allows at most 2 full-width tiles, found {len(full_width_tiles)}"
        )
        self.assertGreaterEqual(
            len(half_width_tiles), 2,
            "Remaining tiles on mobile must be 1-column tiles in the 2-column grid"
        )

        # Confirm side-by-side placement of 1-column tiles on mobile
        side_by_side_mobile = False
        for i in range(len(half_width_tiles)):
            for j in range(i + 1, len(half_width_tiles)):
                if (
                    abs(half_width_tiles[i]["top"] - half_width_tiles[j]["top"]) <= 2.0
                    and abs(half_width_tiles[i]["left"] - half_width_tiles[j]["left"]) > 20.0
                ):
                    side_by_side_mobile = True
                    break
        self.assertTrue(side_by_side_mobile, "1-column tiles must sit side-by-side on mobile 390x844")

        for t in mob["tiles"]:
            self.assertLessEqual(t["right"], mob["innerWidth"] + 1.0, "No tile may overflow the 390px viewport")

    def test_bento_browser_rendered_intentional_scroll_container_vs_page_overflow(self):
        """12. Verify intentional inner overflow-x:auto container scrolls locally without page overflow."""
        self.assertNotIn("error", self.cdp_metrics, f"CDP runner error: {self.cdp_metrics.get('error')}")
        mob_scroll = self.cdp_metrics["mobile_scroll"]["bento"]
        coll_scroll = self.cdp_metrics["mobile_scroll"]["collision"]

        self.assertTrue(mob_scroll["hasBentoGrid"], "Scroll variant must render .bento-grid")
        self.assertIsNotNone(mob_scroll["scrollMetrics"], "Expected .bento-code-scroll container in DOM")
        self.assertEqual(mob_scroll["scrollMetrics"]["overflowX"], "auto")
        self.assertGreater(
            mob_scroll["scrollMetrics"]["scrollWidth"],
            mob_scroll["scrollMetrics"]["clientWidth"],
            "Inner scroll container should have scrollable horizontal content"
        )
        self.assertEqual(
            mob_scroll["scrollWidth"],
            mob_scroll["innerWidth"],
            "Inner scroll container must not cause page-level horizontal overflow at 390x844"
        )
        self.assertFalse(coll_scroll["hasPageOverflow"])
        self.assertEqual(coll_scroll["collisionCount"], 0)


if __name__ == "__main__":
    unittest.main()

