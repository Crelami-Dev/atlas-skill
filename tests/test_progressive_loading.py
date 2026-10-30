#!/usr/bin/env python3
"""Atlas Phase 2 Test Suite — Progressive Reference Loading & Invariant Verification.

Validates that:
1. All reference paths specified in SKILL.md exist on disk in the repository.
2. The task-to-reference mapping covers all reference files without hallucinated paths.
3. Core architectural, layout, asset integrity, and anti-slop invariants are preserved.
4. Missing reference handling is safe and non-hallucinating.
"""
import os
import re
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

SKILL_MD_PATH = os.path.join(ROOT_DIR, "skills", "atlas-skill", "SKILL.md")
REFERENCES_DIR = os.path.join(ROOT_DIR, "knowledge", "taste", "references")


class TestProgressiveLoading(unittest.TestCase):

    def setUp(self):
        self.assertTrue(os.path.exists(SKILL_MD_PATH), f"SKILL.md missing at {SKILL_MD_PATH}")
        with open(SKILL_MD_PATH, "r", encoding="utf-8") as f:
            self.skill_content = f.read()

    def test_mandatory_contracts_and_invariants_present(self):
        """Verify that SKILL.md strictly preserves all mandatory P0, P1.1, and P1.2 contracts."""
        # P0 Layout Invariants
        self.assertIn("The Flex Child Law", self.skill_content)
        self.assertIn("min-width: 0", self.skill_content)
        self.assertIn("max-width: 100%", self.skill_content)
        self.assertIn("Table Column Priority", self.skill_content)
        self.assertIn("Progressive Adaptation Hierarchy", self.skill_content)

        # P0 Asset & Chart Invariants
        self.assertIn("Zero Hallucinated Analytical Visualizations", self.skill_content)
        self.assertIn("Tier 3", self.skill_content)

        # P1.1 and P1.2 Anti-Slop Rules
        self.assertIn("multi-accent-container", self.skill_content)
        self.assertIn("inconsistent-radius", self.skill_content)

        # P2 Loading Protocols
        self.assertIn("Zero Default Loading", self.skill_content)
        self.assertIn("Session De-duplication", self.skill_content)
        self.assertIn("Missing Reference Fallback", self.skill_content)

    def test_all_referenced_files_exist_on_disk(self):
        """Extract every file path matching knowledge/taste/references/*.md and verify it exists."""
        matches = re.findall(r"knowledge/taste/references/([a-zA-Z0-9_-]+\.md)", self.skill_content)
        self.assertGreater(len(matches), 0, "No reference paths discovered in SKILL.md")

        unique_refs = set(matches)
        for ref_filename in unique_refs:
            full_path = os.path.join(REFERENCES_DIR, ref_filename)
            self.assertTrue(
                os.path.exists(full_path),
                f"Referenced file '{ref_filename}' listed in SKILL.md does not exist at {full_path}"
            )

    def test_mapping_table_covers_all_reference_files(self):
        """Verify that all 11 reference manuals under knowledge/taste/references/ are accounted for."""
        disk_files = {f for f in os.listdir(REFERENCES_DIR) if f.endswith(".md")}
        table_matches = set(re.findall(r"knowledge/taste/references/([a-zA-Z0-9_-]+\.md)", self.skill_content))

        self.assertEqual(
            disk_files,
            table_matches,
            f"Mismatch between disk reference files and SKILL.md mapping table: {disk_files ^ table_matches}"
        )

    def test_runtime_heuristic_provenance_paths_exist(self):
        """Verify that all heuristic provenance sources cited by runtime/retriever exist on disk."""
        from runtime.retriever import retrieve_design_references
        from runtime.loader import load_library, default_data_dir
        from runtime.composer import ProductBrief

        brief = ProductBrief(
            category="fintech",
            page_type="app",
            density="high",
            tones=["minimal", "precise"]
        )
        lib = load_library(default_data_dir())
        refs = retrieve_design_references(brief, lib)

        self.assertIn("applicable_heuristics", refs)
        for h in refs["applicable_heuristics"]:
            # Every cited heuristic source in runtime must match an existing file on disk
            source_path = os.path.join(ROOT_DIR, h["source"])
            self.assertTrue(os.path.exists(source_path), f"Runtime heuristic cites non-existent file: {source_path}")

    def test_skill_instructions_explicitly_forbid_fabricating_missing_references(self):
        """Verify that SKILL.md text explicitly commands agents not to fabricate missing references.
        
        Important: This is static instruction-text verification only; it proves the prompt contract
        exists, but cannot prove that an external LLM agent will comply at runtime.
        """
        self.assertIn("Do NOT fabricate or guess reference contents", self.skill_content)
        self.assertIn("Proceed using the core contracts in `SKILL.md`", self.skill_content)
        self.assertIn("Explicitly document the missing reference in the task output", self.skill_content)


if __name__ == "__main__":
    unittest.main()
