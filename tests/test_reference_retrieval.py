#!/usr/bin/env python3
"""Atlas Runtime Engine — Unit Tests for Curated Reference Library & Retrieval.
Part 1 of Phase 7 Remediation.
Zero-dependency, Python 3.9+ standard library.
"""
import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from runtime.contracts import normalize_brief
from runtime.loader import load_library
from runtime.retriever import (
    default_references_dir,
    load_reference_catalog,
    retrieve_design_references,
)


class TestReferenceRetrieval(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = load_library()
        cls.ref_dir = default_references_dir()

    def test_reference_catalog_loads_all_markdown_files(self):
        """Reference catalog must discover and parse all 8 reference markdown files."""
        self.assertTrue(os.path.isdir(self.ref_dir), f"Reference dir not found: {self.ref_dir}")
        catalog = load_reference_catalog(self.ref_dir)
        
        expected_files = {
            "design-principles.md",
            "art-direction-archetypes.md",
            "domain-patterns.md",
            "content-integrity.md",
            "responsive-patterns.md",
            "visual-anti-patterns.md",
            "reference-index.md",
            "curated-case-studies.md"
        }
        for ef in expected_files:
            self.assertIn(ef, catalog, f"Missing catalog file: {ef}")
            self.assertGreater(len(catalog[ef]), 0, f"File {ef} should have parsed sections")

    def test_deterministic_reference_retrieval(self):
        """Repeated retrieval for the same brief must produce byte-identical results."""
        brief = normalize_brief({
            "project_name": "DeterministicCorp",
            "category": "saas",
            "tones": ["technical", "quiet"],
            "density": "high"
        })
        run1 = retrieve_design_references(brief, self.lib)
        run2 = retrieve_design_references(brief, self.lib)
        self.assertEqual(run1, run2, "Reference retrieval must be strictly deterministic")

    def test_luxury_atelier_reference_matching(self):
        """Maison Atelier must retrieve luxury domain patterns, editorial archetype, and luxury exemplars."""
        brief = normalize_brief({
            "project_name": "Maison Atelier",
            "category": "fashion",
            "tones": ["editorial", "calm", "refined"],
            "audience": "high-net-worth connoisseurs",
            "primary_task": "explore bespoke horlogerie collection",
            "density": "low"
        })
        refs = retrieve_design_references(brief, self.lib)

        # Domain pattern match
        domain_pattern = refs.get("matched_domain_pattern", {})
        self.assertIn("Luxury Fashion", domain_pattern.get("title", ""))

        # Archetype match
        archetype = refs.get("matched_archetype", {})
        self.assertIn("Editorial Luxury", archetype.get("title", ""))

        # Exemplars should be relevant to fashion/luxury/architecture
        exemplars = refs.get("matched_exemplars", [])
        self.assertGreaterEqual(len(exemplars), 1)
        kinds = {ex["kind"] for ex in exemplars}
        self.assertTrue(bool(kinds & {"fashion", "hospitality", "architecture", "luxury"}))

        # Must have transferable principles
        for ex in exemplars:
            self.assertIn("transferable_principles", ex)
            self.assertGreater(len(ex["transferable_principles"]), 0)

        # Verify curated case study link if exemplar matches curated library
        curated_matches = [ex for ex in exemplars if ex.get("curated_case_study")]
        self.assertGreaterEqual(len(curated_matches), 1, "Expected at least one exemplar to link to curated case studies")

    def test_technical_infrastructure_reference_matching(self):
        """Vektor Platform must retrieve technical domain patterns, instrument archetype, and dev-tool exemplars."""
        brief = normalize_brief({
            "project_name": "Vektor Platform",
            "category": "dev-tool",
            "tones": ["technical", "precise", "austere"],
            "audience": "distributed systems engineers",
            "primary_task": "inspect architectural performance benchmarks",
            "density": "high"
        })
        refs = retrieve_design_references(brief, self.lib)

        # Domain pattern match
        domain_pattern = refs.get("matched_domain_pattern", {})
        self.assertIn("Developer Tool", domain_pattern.get("title", ""))

        # Archetype match
        archetype = refs.get("matched_archetype", {})
        self.assertIn("Technical Instrument", archetype.get("title", ""))

        # Exemplars should be dev-tool or saas
        exemplars = refs.get("matched_exemplars", [])
        self.assertGreaterEqual(len(exemplars), 1)
        kinds = {ex["kind"] for ex in exemplars}
        self.assertTrue(bool(kinds & {"dev-tool", "saas", "ai-product"}))

    def test_creative_agency_reference_matching(self):
        """Bureau Helix must retrieve agency domain patterns and brutalist monumental archetype."""
        brief = normalize_brief({
            "project_name": "Bureau Helix",
            "category": "agency",
            "tones": ["bold", "confident", "curated"],
            "audience": "brand directors",
            "primary_task": "evaluate identity case studies",
            "density": "med"
        })
        refs = retrieve_design_references(brief, self.lib)

        # Domain pattern match
        domain_pattern = refs.get("matched_domain_pattern", {})
        self.assertIn("Creative Agency", domain_pattern.get("title", ""))

        # Archetype match
        archetype = refs.get("matched_archetype", {})
        self.assertIn("Brutalist Monumental", archetype.get("title", ""))

        # Exemplars should be agency or studio-portfolio
        exemplars = refs.get("matched_exemplars", [])
        self.assertGreaterEqual(len(exemplars), 1)
        kinds = {ex["kind"] for ex in exemplars}
        self.assertTrue(bool(kinds & {"agency", "studio-portfolio"}))

    def test_content_integrity_rules_included(self):
        """Retrieved references must enforce content truthfulness doctrine and blacklist fabricated claims."""
        brief = normalize_brief({"project_name": "AuditCorp", "category": "dev-tool"})
        refs = retrieve_design_references(brief, self.lib)

        integrity = refs.get("content_integrity_rules", {})
        self.assertIn("classification_doctrine", integrity)
        self.assertIn("forbidden_claims_blacklist", integrity)
        blacklist = integrity["forbidden_claims_blacklist"]
        self.assertTrue(any("SOC 2" in b for b in blacklist), "Blacklist must forbid fake SOC 2 certifications")
        self.assertTrue(any("99.999%" in b for b in blacklist), "Blacklist must forbid fake SLA claims")

    def test_responsive_floor_guards_included(self):
        """Retrieved references must include multi-viewport floor guards for 768px and 320px."""
        brief = normalize_brief({"project_name": "MobileCorp", "category": "fashion"})
        refs = retrieve_design_references(brief, self.lib)

        guards = refs.get("responsive_guards", {})
        self.assertIn("tablet_portrait_768px", guards)
        self.assertIn("small_mobile_320px", guards)
        self.assertIn("orphan", guards["tablet_portrait_768px"].lower())

    def test_backward_compatibility_preserved(self):
        """Existing keys and heuristic disk paths must remain valid for legacy tests."""
        brief = normalize_brief({"project_name": "LegacyTest", "category": "saas"})
        refs = retrieve_design_references(brief, self.lib)

        self.assertIn("applicable_heuristics", refs)
        self.assertIn("retrieved_motions", refs)
        self.assertIn("provenance_root", refs)
        self.assertIn("traceable_rationale", refs)

        for h in refs["applicable_heuristics"]:
            source_path = os.path.join(ROOT_DIR, h["source"])
            self.assertTrue(os.path.exists(source_path), f"Citing missing heuristic file: {source_path}")


if __name__ == "__main__":
    unittest.main()

