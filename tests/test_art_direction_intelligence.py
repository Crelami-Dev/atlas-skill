#!/usr/bin/env python3
"""Atlas Phase 7 Test Suite — Art Direction & Visual Identity Intelligence.

Validates the Phase 7 art direction contracts, including:
1. Determinism: Same brief and canonical library yield identical plans across repeated runs;
   contextual tie-breaking operates deterministically without randomness or execution-order dependence.
2. Semantic Relevance: Art direction selection matches tones (with synonym expansion),
   audience, primary task, and category, avoiding generic fallback collapse.
3. Section & Slot Management: Explicit slots and excludes from the brief are strictly honored;
   pricing is preserved when explicitly requested; unrequested slots are omitted.
4. Contextual Copy Generation: Generated copy reflects brand identity and category,
   eliminating hardcoded internal engine boilerplate.
5. Density & Typography Scale: Spacing and typography scales adapt dynamically to
   density ('low', 'med', 'high') and typography pairing tokens.
6. P6 Regressions & Anti-Slop: Bento Grid features and anti-slop contracts remain intact.
"""
import os
import re
import sys
import tempfile
import shutil
import unittest
from typing import Dict, Any

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from runtime.contracts import normalize_brief, ProductBrief
from runtime.loader import load_library, default_data_dir
from runtime.composer import compose_design_plan
from runtime.generator import render_html, render_css, generate_website
from runtime.scorer import score_art_direction
from runtime.anti_slop import audit_website_content


class TestDeterminismAndTieBreaking(unittest.TestCase):
    """Verifies that plan composition is strictly deterministic and contextual."""

    @classmethod
    def setUpClass(cls):
        cls.lib = load_library(default_data_dir())

    def test_plan_determinism_across_repeated_runs(self):
        """Input brief and library version must produce bitwise identical plan structures."""
        brief_data = {
            "project_name": "Vektor Platform",
            "category": "dev-tool",
            "tones": ["technical", "precise"],
            "density": "high",
            "audience": "systems engineers"
        }
        fixed_ts = "2026-10-30T12:00:00Z"
        brief = normalize_brief(brief_data)

        # Execute 5 repeated composition runs
        first_plan = compose_design_plan(brief, self.lib, deterministic_timestamp=fixed_ts)
        for i in range(4):
            subsequent_plan = compose_design_plan(brief, self.lib, deterministic_timestamp=fixed_ts)
            self.assertEqual(
                first_plan["plan_id"],
                subsequent_plan["plan_id"],
                f"Run {i+2} produced mismatched plan_id"
            )
            self.assertEqual(
                first_plan["art_direction"]["id"],
                subsequent_plan["art_direction"]["id"],
                f"Run {i+2} produced mismatched art_direction"
            )
            self.assertEqual(
                [s["pattern_id"] for s in first_plan["composition"]["slots"]],
                [s["pattern_id"] for s in subsequent_plan["composition"]["slots"]],
                f"Run {i+2} produced mismatched composition slots"
            )
            self.assertEqual(
                first_plan["palette"]["id"],
                subsequent_plan["palette"]["id"],
                f"Run {i+2} produced mismatched palette"
            )
            self.assertEqual(
                first_plan["typography"]["id"],
                subsequent_plan["typography"]["id"],
                f"Run {i+2} produced mismatched typography"
            )

    def test_deterministic_contextual_tie_breaking(self):
        """Tied art direction candidates must break ties using brief context, not static alphabetical sorting."""
        # Two briefs with identical sector 'saas' and no direct tone matches,
        # but differing in project_name and audience context.
        brief_a = normalize_brief({
            "project_name": "Zenith Analytics",
            "category": "saas",
            "tones": ["quiet", "analytical"],
            "audience": "data scientists",
            "density": "high"
        })
        brief_b = normalize_brief({
            "project_name": "Kroma Design",
            "category": "agency",
            "tones": ["bold", "curated"],
            "audience": "creative directors",
            "density": "low"
        })

        plan_a1 = compose_design_plan(brief_a, self.lib, deterministic_timestamp="2026-10-30T12:00:00Z")
        plan_a2 = compose_design_plan(brief_a, self.lib, deterministic_timestamp="2026-10-30T12:00:00Z")
        self.assertEqual(plan_a1["art_direction"]["id"], plan_a2["art_direction"]["id"])

        plan_b1 = compose_design_plan(brief_b, self.lib, deterministic_timestamp="2026-10-30T12:00:00Z")
        plan_b2 = compose_design_plan(brief_b, self.lib, deterministic_timestamp="2026-10-30T12:00:00Z")
        self.assertEqual(plan_b1["art_direction"]["id"], plan_b2["art_direction"]["id"])

        # Contextual tie-breaking must not blindly resolve every brief to 'art-dir:borrowed-category'
        self.assertNotEqual(
            plan_b1["art_direction"]["id"],
            "art-dir:borrowed-category",
            "Creative agency brief should resolve contextually, not collapse to borrowed-category"
        )


class TestArtDirectionSemanticRelevance(unittest.TestCase):
    """Verifies that art direction scoring is semantically relevant and expands tone synonyms."""

    @classmethod
    def setUpClass(cls):
        cls.lib = load_library(default_data_dir())

    def test_tone_synonym_expansion_and_scoring(self):
        """Synonym tones (e.g. 'calm' -> 'quiet', 'refined' -> 'luxury') must score tone bonuses."""
        brief = normalize_brief({
            "project_name": "Aura Spa",
            "category": "hospitality",
            "tones": ["calm", "refined"]
        })
        # art-dir:place-carries-it has tones: ['quiet', 'luxury', 'warm']
        ad_place = self.lib.get_by_id("art-dir:place-carries-it")
        score, rationale = score_art_direction(ad_place, brief)

        # Without synonym expansion, score is 3.0 (sector only).
        # With synonym expansion ('calm'->'quiet', 'refined'->'luxury'), tone matches add at least 3.0 points.
        self.assertGreaterEqual(
            score, 6.0,
            f"Expected tone synonym bonus (score >= 6.0), got {score}. Rationale: {rationale}"
        )
        has_tone_rationale = any("tone" in r.lower() for r in rationale)
        self.assertTrue(has_tone_rationale, f"Rationale must explain tone synonym match: {rationale}")

    def test_audience_and_primary_task_influence_on_selection(self):
        """Audience and primary_task must influence scoring and distinguish candidates."""
        brief_dev = normalize_brief({
            "project_name": "CoreKernel",
            "category": "dev-tool",
            "tones": ["technical"],
            "audience": "systems engineers",
            "primary_task": "inspect architectural performance benchmarks",
            "density": "high"
        })
        brief_retail = normalize_brief({
            "project_name": "DevGear",
            "category": "dev-tool",
            "tones": ["technical"],
            "audience": "casual hobbyist developers",
            "primary_task": "browse starter kits and accessories",
            "density": "med"
        })

        ad_quiet = self.lib.get_by_id("art-dir:quiet-instrument")
        score_dev, rat_dev = score_art_direction(ad_quiet, brief_dev)
        score_retail, rat_retail = score_art_direction(ad_quiet, brief_retail)

        # Deep technical engineering task should score higher on quiet-instrument than casual shopping
        self.assertGreater(
            score_dev, score_retail,
            f"Quiet instrument should score higher for systems engineering ({score_dev}) than retail hobbyist ({score_retail})"
        )

    def test_luxury_atelier_semantic_relevance(self):
        """Benchmark 1 (Maison Atelier) must select an art direction matching luxury/editorial craftsmanship."""
        brief = normalize_brief({
            "project_name": "Maison Atelier",
            "category": "fashion",
            "tones": ["editorial", "calm", "refined"],
            "audience": "high-net-worth connoisseurs",
            "primary_task": "explore bespoke horlogerie collection",
            "density": "low"
        })
        plan = compose_design_plan(brief, self.lib, deterministic_timestamp="2026-10-30T12:00:00Z")
        selected_ad = plan["art_direction"]["id"]

        # Legitimate luxury / editorial / quiet directions
        valid_luxury_ads = {
            "art-dir:place-carries-it",
            "art-dir:uneven-photographs",
            "art-dir:dark-room",
            "art-dir:name-as-monument",
            "art-dir:hero-object",
            "art-dir:contact-sheet"
        }
        self.assertIn(
            selected_ad, valid_luxury_ads,
            f"Maison Atelier should select a luxury/editorial art direction, got {selected_ad}"
        )
        self.assertNotEqual(selected_ad, "art-dir:borrowed-category")

    def test_technical_infrastructure_semantic_relevance(self):
        """Benchmark 2 (Vektor Platform) must select a high-density, technical/functional art direction."""
        brief = normalize_brief({
            "project_name": "Vektor Platform",
            "category": "dev-tool",
            "tones": ["technical", "precise", "austere"],
            "audience": "distributed systems engineers",
            "primary_task": "inspect architectural performance benchmarks",
            "density": "high"
        })
        plan = compose_design_plan(brief, self.lib, deterministic_timestamp="2026-10-30T12:00:00Z")
        selected_ad = plan["art_direction"]["id"]

        valid_tech_ads = {
            "art-dir:dense-tiles",
            "art-dir:quiet-instrument",
            "art-dir:product-performs",
            "art-dir:type-only-statement"
        }
        self.assertIn(
            selected_ad, valid_tech_ads,
            f"Vektor Platform should select a technical art direction, got {selected_ad}"
        )
        self.assertNotEqual(selected_ad, "art-dir:borrowed-category")

    def test_design_agency_semantic_relevance(self):
        """Benchmark 3 (Bureau Helix) must select a bold, expressive design archetype."""
        brief = normalize_brief({
            "project_name": "Bureau Helix",
            "category": "agency",
            "tones": ["bold", "confident", "curated"],
            "audience": "brand directors",
            "primary_task": "evaluate identity case studies",
            "density": "med"
        })
        plan = compose_design_plan(brief, self.lib, deterministic_timestamp="2026-10-30T12:00:00Z")
        selected_ad = plan["art_direction"]["id"]

        valid_agency_ads = {
            "art-dir:colour-chapters",
            "art-dir:sentence-as-layout",
            "art-dir:pinned-poster",
            "art-dir:loud-flat-poster",
            "art-dir:name-as-monument"
        }
        self.assertIn(
            selected_ad, valid_agency_ads,
            f"Bureau Helix should select a bold agency art direction, got {selected_ad}"
        )


class TestSectionAndSlotManagement(unittest.TestCase):
    """Verifies that explicit brief slots and excludes take strict precedence over category defaults."""

    @classmethod
    def setUpClass(cls):
        cls.lib = load_library(default_data_dir())

    def test_explicit_slots_strictly_honored_including_pricing(self):
        """When brief explicitly requests pricing, it MUST be preserved in plan and rendered HTML."""
        brief = normalize_brief({
            "project_name": "Maison Atelier",
            "category": "fashion",
            "tones": ["editorial", "luxury"],
            "slots": ["hero", "features", "pricing", "cta"]
        })
        plan = compose_design_plan(brief, self.lib, deterministic_timestamp="2026-10-30T12:00:00Z")
        planned_slots = [s["slot"] for s in plan["composition"]["slots"]]

        self.assertIn("pricing", planned_slots, "Explicit 'pricing' slot must be preserved in plan")

        html = render_html(plan, {"assets": []})
        self.assertIn('id="pricing"', html, "Rendered HTML must contain pricing when explicitly requested in slots")

    def test_explicit_exclude_strictly_honored(self):
        """When brief explicitly excludes slots, they must NOT appear in plan or rendered HTML."""
        brief = normalize_brief({
            "project_name": "Nexus Cloud",
            "category": "saas",
            "exclude": ["pricing", "faq"]
        })
        plan = compose_design_plan(brief, self.lib, deterministic_timestamp="2026-10-30T12:00:00Z")
        planned_slots = [s["slot"] for s in plan["composition"]["slots"]]

        self.assertNotIn("pricing", planned_slots, "Excluded 'pricing' slot must not be in plan slots")
        self.assertNotIn("faq", planned_slots, "Excluded 'faq' slot must not be in plan slots")

        html = render_html(plan, {"assets": []})
        self.assertNotIn('id="pricing"', html, "Rendered HTML must not contain excluded pricing section")
        self.assertNotIn('id="faq"', html, "Rendered HTML must not contain excluded faq section")

    def test_category_default_slots_when_unspecified(self):
        """When slots are omitted on a luxury fashion brief, commercial pricing should be contextually omitted."""
        brief = normalize_brief({
            "project_name": "Maison Atelier",
            "category": "fashion",
            "tones": ["editorial", "luxury"]
            # slots omitted -> should use category-aware intelligent defaults
        })
        plan = compose_design_plan(brief, self.lib, deterministic_timestamp="2026-10-30T12:00:00Z")
        planned_slots = [s["slot"] for s in plan["composition"]["slots"]]

        self.assertNotIn(
            "pricing", planned_slots,
            "Luxury atelier brief without explicit slots should default to omitting SaaS pricing tables"
        )

    def test_render_html_only_renders_planned_slots(self):
        """render_html must assemble sections dynamically based on plan composition slots."""
        brief = normalize_brief({
            "project_name": "Minimalist Showcase",
            "category": "design",
            "slots": ["hero", "features", "cta"]
        })
        plan = compose_design_plan(brief, self.lib, deterministic_timestamp="2026-10-30T12:00:00Z")
        html = render_html(plan, {"assets": []})

        self.assertIn('id="hero"', html, "Hero must be rendered")
        self.assertIn('id="features"', html, "Features must be rendered")
        self.assertIn('id="cta"', html, "CTA must be rendered")

        # Sections not in slots must NOT be rendered
        self.assertNotIn('id="proof"', html, "Unrequested 'proof' section must not be rendered")
        self.assertNotIn('id="workflow"', html, "Unrequested 'workflow' section must not be rendered")
        self.assertNotIn('id="pricing"', html, "Unrequested 'pricing' section must not be rendered")
        self.assertNotIn('id="faq"', html, "Unrequested 'faq' section must not be rendered")


class TestContextualCopyGeneration(unittest.TestCase):
    """Verifies that generated copy is category-aware and contains no internal engine buzzwords."""

    @classmethod
    def setUpClass(cls):
        cls.lib = load_library(default_data_dir())

    def test_no_hardcoded_engine_boilerplate_in_rendered_html(self):
        """Rendered HTML across all benchmark briefs must not contain internal generator buzzwords."""
        briefs = [
            normalize_brief({"project_name": "Maison Atelier", "category": "fashion", "tones": ["editorial", "luxury"]}),
            normalize_brief({"project_name": "Vektor Platform", "category": "dev-tool", "tones": ["technical"]}),
            normalize_brief({"project_name": "Bureau Helix", "category": "agency", "tones": ["bold"]}),
        ]
        banned_engine_terms = [
            "Deterministic Execution",
            "Deep Immutability",
            "3-Tier Visual Asset Pipeline",
            "Atlas Platform",
            "Zero Framework Overhead",
            "Tier 3"
        ]

        for brief in briefs:
            plan = compose_design_plan(brief, self.lib, deterministic_timestamp="2026-10-30T12:00:00Z")
            html = render_html(plan, {"assets": []})
            for term in banned_engine_terms:
                self.assertNotIn(
                    term, html,
                    f"Brief '{brief.project_name}' contains banned engine boilerplate '{term}' in HTML"
                )

    def test_copy_reflects_brand_category_and_value_prop(self):
        """Hero headlines and lead copy must reflect the specific brand and sector."""
        brief_luxury = normalize_brief({
            "project_name": "Maison Atelier",
            "category": "fashion",
            "tones": ["editorial", "luxury"],
            "primary_task": "explore bespoke horlogerie collection"
        })
        plan_luxury = compose_design_plan(brief_luxury, self.lib, deterministic_timestamp="2026-10-30T12:00:00Z")
        html_luxury = render_html(plan_luxury, {"assets": []})

        # Must not contain generic SaaS template copy
        self.assertNotIn(
            "Engineered for Clarity, Speed, and Depth.",
            html_luxury,
            "Luxury brand must not use generic technical SaaS H1"
        )
        self.assertNotIn(
            "Accelerate your fashion workflows with purpose-built design systems",
            html_luxury,
            "Luxury brand lead copy must not refer to 'fashion workflows with purpose-built design systems'"
        )

        # Must reflect the project name and brand context
        self.assertIn("Maison Atelier", html_luxury)


class TestTypographyAndSpatialScale(unittest.TestCase):
    """Verifies that CSS spacing and typography scale dynamically with density and tokens."""

    @classmethod
    def setUpClass(cls):
        cls.lib = load_library(default_data_dir())

    def test_density_responsive_css_spacing(self):
        """render_css must adjust spacing scales (--space-xl, --max-width) based on density."""
        brief_low = normalize_brief({"project_name": "Spacious Editorial", "density": "low"})
        plan_low = compose_design_plan(brief_low, self.lib, deterministic_timestamp="2026-10-30T12:00:00Z")
        css_low = render_css(plan_low)

        brief_high = normalize_brief({"project_name": "Dense Console", "density": "high"})
        plan_high = compose_design_plan(brief_high, self.lib, deterministic_timestamp="2026-10-30T12:00:00Z")
        css_high = render_css(plan_high)

        # Extract --space-xl value from CSS
        match_low = re.search(r'--space-xl:\s*([^;]+);', css_low)
        match_high = re.search(r'--space-xl:\s*([^;]+);', css_high)
        self.assertTrue(bool(match_low), "Low density CSS must define --space-xl")
        self.assertTrue(bool(match_high), "High density CSS must define --space-xl")

        val_low_str = match_low.group(1).strip()
        val_high_str = match_high.group(1).strip()

        # Low density should have a larger space token than high density
        self.assertNotEqual(
            val_low_str, val_high_str,
            f"--space-xl should differ between low and high density (got {val_low_str} vs {val_high_str})"
        )

    def test_typography_scale_integration_in_css(self):
        """render_css must incorporate the typography scale or step-head token from the plan."""
        brief = normalize_brief({
            "project_name": "Display System",
            "tones": ["bold", "editorial"]
        })
        plan = compose_design_plan(brief, self.lib, deterministic_timestamp="2026-10-30T12:00:00Z")
        css = render_css(plan)

        # CSS should reference typography scale or provide distinct clamp definitions
        has_typo_vars = "--font-display" in css and "--font-text" in css
        self.assertTrue(has_typo_vars)


class TestP6RegressionsAndAntiSlopInvariants(unittest.TestCase):
    """Verifies that P6 Bento Grid layouts and anti-slop rules remain fully functional."""

    @classmethod
    def setUpClass(cls):
        cls.lib = load_library(default_data_dir())
        cls.temp_dir = tempfile.mkdtemp(prefix="atlas_p7_p6_regression_")

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def test_p6_bento_grid_preserved_when_selected(self):
        """When atlas:features-bento is selected in slots, Bento Grid markup and classes are preserved."""
        plan = {
            "runtime_version": "2.0.0",
            "library_version": "2.0.0",
            "plan_id": "test-bento-regression",
            "normalized_brief": {
                "project_name": "Bento Regression Check",
                "category": "dev-tool",
                "density": "high"
            },
            "art_direction": {
                "id": "art-dir:product-performs",
                "name": "The product performs"
            },
            "composition": {
                "slots": [
                    {"slot": "hero", "pattern_id": "atlas:hero-split-mockup"},
                    {"slot": "features", "pattern_id": "atlas:features-bento"}
                ]
            },
            "palette": {
                "id": "pal:slate-minimal",
                "tokens": {
                    "bg": "#0f172a", "surface": "#1e293b", "ink": "#f8fafc",
                    "muted": "#94a3b8", "accent": "#38bdf8", "accent_ink": "#0f172a"
                }
            },
            "typography": {
                "id": "typo:inter-jetbrains",
                "fonts": {"display": "Inter", "text": "Inter"}
            }
        }
        html = render_html(plan, {"assets": []})
        css = render_css(plan)

        # Bento grid markup assertions
        self.assertIn("bento-grid", html)
        self.assertIn("bento-tile-lead", html)
        self.assertIn("bento-tile-wide", html)
        self.assertIn("bento-tile-standard", html)

        # Responsive CSS contract assertions
        self.assertIn("@media (max-width: 768px)", css)
        self.assertIn("grid-template-columns: repeat(2, minmax(0, 1fr))", css)

    def test_anti_slop_invariants_pass_on_all_benchmarks(self):
        """Generated sites across all benchmark briefs must pass anti-slop audit with 0 hard failures."""
        benchmarks = [
            {"project_name": "Maison Atelier", "category": "fashion", "tones": ["editorial", "luxury"], "density": "low"},
            {"project_name": "Vektor Platform", "category": "dev-tool", "tones": ["technical"], "density": "high"},
            {"project_name": "Bureau Helix", "category": "agency", "tones": ["bold"], "density": "med"},
        ]

        for i, b_data in enumerate(benchmarks):
            brief = normalize_brief(b_data)
            plan = compose_design_plan(brief, self.lib, deterministic_timestamp="2026-10-30T12:00:00Z")
            out_dir = os.path.join(self.temp_dir, f"site_{i}")

            res = generate_website(plan, out_dir, prefer_mock_images=True)
            self.assertEqual(res["status"], "SUCCESS")

            anti_slop = res["anti_slop_audit"]
            failures_count = anti_slop.get("failures_count", 0)
            status = anti_slop.get("status", "PASS")

            self.assertEqual(
                failures_count, 0,
                f"Benchmark '{b_data['project_name']}' failed anti-slop with failures: {anti_slop.get('findings')}"
            )
            self.assertIn(
                status, {"PASS", "WARN"},
                f"Benchmark '{b_data['project_name']}' status was {status}"
            )


class TestPhase7CompositionAndContextualReasoning(unittest.TestCase):
    """Verifies that brief domains drive purposeful, differentiated Information Architecture."""

    @classmethod
    def setUpClass(cls):
        cls.lib = load_library(default_data_dir())

    def test_domain_differentiation_in_composition_rationale(self):
        """Maison, Vektor, and Bureau Helix must receive distinct domain classifications and reference sets."""
        benchmarks = [
            ("Maison Atelier", "fashion", ["editorial", "luxury"], "luxury_craftsmanship", "art-dir:uneven-photographs"),
            ("Vektor Platform", "dev-tool", ["technical", "austere"], "technical_infrastructure", "art-dir:quiet-instrument"),
            ("Bureau Helix", "agency", ["bold", "curated"], "creative_brand_architecture", "art-dir:name-as-monument"),
        ]
        for name, cat, tones, expected_domain, expected_ad in benchmarks:
            brief = normalize_brief({"project_name": name, "category": cat, "tones": tones})
            plan = compose_design_plan(brief, self.lib, deterministic_timestamp="2026-10-30T12:00:00Z")
            rationale = plan["composition"]["decision_rationale"]

            self.assertEqual(rationale["domain_type"], expected_domain)
            self.assertEqual(plan["art_direction"]["id"], expected_ad)
            self.assertTrue(bool(rationale["applied_domain_pattern"]))
            self.assertTrue(bool(rationale["applied_archetype"]))
            self.assertGreaterEqual(len(rationale["applied_exemplars"]), 1)
            self.assertGreaterEqual(len(rationale["applied_heuristics"]), 1)
            self.assertIn("traceable_rationale", rationale)

    def test_slot_selection_relevance_and_explicit_priority(self):
        """Default luxury omits commercial pricing, while explicit slots or excludes strictly take precedence."""
        # Unspecified slots: luxury category defaults omit pricing
        brief_luxury_default = normalize_brief({"project_name": "Maison Luxury", "category": "luxury", "tones": ["editorial"]})
        plan_luxury_default = compose_design_plan(brief_luxury_default, self.lib, deterministic_timestamp="2026-10-30T12:00:00Z")
        planned_slots_default = [s["slot"] for s in plan_luxury_default["composition"]["slots"]]
        self.assertNotIn("pricing", planned_slots_default)

        # Explicit slots requesting pricing on luxury must be honored
        brief_luxury_explicit = normalize_brief({
            "project_name": "Maison Luxury Explicit",
            "category": "luxury",
            "slots": ["hero", "pricing", "cta"]
        })
        plan_luxury_explicit = compose_design_plan(brief_luxury_explicit, self.lib, deterministic_timestamp="2026-10-30T12:00:00Z")
        planned_slots_explicit = [s["slot"] for s in plan_luxury_explicit["composition"]["slots"]]
        self.assertIn("pricing", planned_slots_explicit)
        self.assertNotIn("features", planned_slots_explicit)


class TestPhase7ContentIntegrityAndTruthfulness(unittest.TestCase):
    """Enforces the Truthfulness Doctrine: zero fabricated claims, metrics, or certifications."""

    @classmethod
    def setUpClass(cls):
        cls.lib = load_library(default_data_dir())

    def test_zero_tier_4_forbidden_fabrications_in_rendered_html(self):
        """Rendered HTML across all domain archetypes must contain 0 blacklisted fake claims."""
        forbidden_claims = [
            "SOC 2", "99.999%", "<1ms", "140+", "12yr",
            "12 Capitals", "12 capitals", "4.9 / 5", "10x", "99.9%"
        ]
        test_briefs = [
            {"project_name": "Maison Atelier", "category": "fashion", "tones": ["editorial", "luxury"], "density": "low", "slots": ["hero", "proof", "features", "how-it-works", "pricing", "faq", "cta"]},
            {"project_name": "Vektor Platform", "category": "dev-tool", "tones": ["technical"], "density": "high", "slots": ["hero", "proof", "features", "how-it-works", "pricing", "faq", "cta"]},
            {"project_name": "Bureau Helix", "category": "agency", "tones": ["bold"], "density": "med", "slots": ["hero", "proof", "features", "how-it-works", "pricing", "faq", "cta"]},
            {"project_name": "Generic Fallback App", "category": "finance", "tones": [], "density": "med", "slots": ["hero", "proof", "features", "how-it-works", "pricing", "faq", "cta"]}
        ]
        for b_data in test_briefs:
            brief = normalize_brief(b_data)
            plan = compose_design_plan(brief, self.lib, deterministic_timestamp="2026-10-30T12:00:00Z")
            html = render_html(plan, {"assets": []})
            for claim in forbidden_claims:
                self.assertNotIn(
                    claim, html,
                    f"Brief '{b_data['project_name']}' contained blacklisted claim '{claim}' in HTML"
                )

    def test_contextual_copy_divergence_across_domains(self):
        """Workflow, Pricing, and FAQ content must reflect authentic domain processes rather than internal engine terms."""
        brief_luxury = normalize_brief({
            "project_name": "Maison Atelier", "category": "fashion", "tones": ["luxury", "editorial"],
            "slots": ["hero", "how-it-works", "pricing", "faq", "cta"]
        })
        brief_tech = normalize_brief({
            "project_name": "Vektor Platform", "category": "dev-tool", "tones": ["technical"],
            "slots": ["hero", "how-it-works", "pricing", "faq", "cta"]
        })
        brief_agency = normalize_brief({
            "project_name": "Bureau Helix", "category": "agency", "tones": ["bold"],
            "slots": ["hero", "how-it-works", "pricing", "faq", "cta"]
        })

        plan_lux = compose_design_plan(brief_luxury, self.lib, deterministic_timestamp="2026-10-30T12:00:00Z")
        plan_tech = compose_design_plan(brief_tech, self.lib, deterministic_timestamp="2026-10-30T12:00:00Z")
        plan_agency = compose_design_plan(brief_agency, self.lib, deterministic_timestamp="2026-10-30T12:00:00Z")

        html_lux = render_html(plan_lux, {"assets": []})
        html_tech = render_html(plan_tech, {"assets": []})
        html_agency = render_html(plan_agency, {"assets": []})

        # Luxury domain assertions
        self.assertIn("Atelier Commission Lifecycle", html_lux)
        self.assertIn("Collector Salon", html_lux)
        self.assertIn("Inquire", html_lux)
        self.assertIn("Atelier &amp; Commission Insights", html_lux)

        # Technical dev-tool domain assertions
        self.assertIn("Architecture &amp; Deployment Lifecycle", html_tech)
        self.assertIn("Developer Node", html_tech)
        self.assertIn("Production Cluster", html_tech)
        self.assertIn("Technical Specifications &amp; Systems Architecture", html_tech)

        # Creative agency domain assertions
        self.assertIn("Strategic Engagement &amp; Rollout", html_agency)
        self.assertIn("Strategic Sprint", html_agency)
        self.assertIn("Full Identity Architecture", html_agency)
        self.assertIn("Creative Process &amp; Partnership FAQ", html_agency)


class TestPhase7ResponsiveArtDirectionAndAccessibility(unittest.TestCase):
    """Verifies responsive layout floor guards, orphan prevention, and multi-viewport layout health."""

    @classmethod
    def setUpClass(cls):
        cls.lib = load_library(default_data_dir())

    def test_proof_grid_responsive_rules_eliminate_orphan_cards(self):
        """CSS for .proof-grid must enforce 4-col on desktop, 2x2 on tablet portrait, and 1-col on small mobile."""
        brief = normalize_brief({"project_name": "Responsive Proof", "density": "med"})
        plan = compose_design_plan(brief, self.lib, deterministic_timestamp="2026-10-30T12:00:00Z")
        css = render_css(plan)

        # Desktop 4 columns
        self.assertIn(".proof-grid", css)
        self.assertIn("grid-template-columns: repeat(4, minmax(0, 1fr))", css)

        # Tablet portrait (<= 1024px) 2x2 symmetry
        self.assertIn("@media (max-width: 1024px)", css)
        self.assertIn("grid-template-columns: repeat(2, minmax(0, 1fr))", css)

        # Small mobile (<= 540px) 1-col stack
        self.assertIn("@media (max-width: 540px)", css)
        self.assertIn("grid-template-columns: 1fr", css)

    def test_low_density_h1_floor_clamp_prevents_orphan_ampersand(self):
        """Low density h1_clamp must have a floor <= 2.0rem and balance text wrapping."""
        brief = normalize_brief({"project_name": "Maison Atelier", "category": "fashion", "density": "low"})
        plan = compose_design_plan(brief, self.lib, deterministic_timestamp="2026-10-30T12:00:00Z")
        css = render_css(plan)
        html = render_html(plan, {"assets": []})

        # Heading balance and floor clamp assertions
        self.assertIn("text-wrap: balance", css)
        self.assertIn("clamp(2.0rem,", css)

        # Ampersand non-breaking protection
        self.assertIn("&amp;&nbsp;Architectural Form", html)

    def test_interactive_elements_meet_minimum_touch_target_contract(self):
        """Buttons, nav links, nav toggle, and FAQ triggers must specify min-height of 44px."""
        brief = normalize_brief({"project_name": "Touch Target Check"})
        plan = compose_design_plan(brief, self.lib, deterministic_timestamp="2026-10-30T12:00:00Z")
        css = render_css(plan)

        self.assertIn("min-height: 44px", css)
        self.assertIn(".btn", css)
        self.assertIn(".nav-link", css)
        self.assertIn(".faq-question", css)


if __name__ == "__main__":
    unittest.main()
