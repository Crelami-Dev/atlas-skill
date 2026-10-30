#!/usr/bin/env python3
"""Atlas Runtime Engine — Unit Tests for Multi-Agent Orchestration Contracts."""
import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from runtime.orchestration_contracts import (
    ExecutionMode,
    MAX_REVISION_CYCLES,
    OrchestrationValidationError,
    QAVerdict,
    Role,
    TaskDefinition,
    TaskResult,
    TaskStatus,
    validate_analysis_output,
    validate_art_direction_output,
    validate_implementation_output,
    validate_qa_critic_output,
)


class TestOrchestrationContracts(unittest.TestCase):
    def test_five_canonical_roles_defined(self):
        expected_roles = {
            "Lead Orchestrator",
            "Product Analyst",
            "Art Director",
            "Frontend Implementer",
            "QA Critic"
        }
        actual_roles = {r.value for r in Role}
        self.assertEqual(actual_roles, expected_roles)

    def test_max_revision_cycles_constant(self):
        self.assertEqual(MAX_REVISION_CYCLES, 3)

    def test_validate_analysis_output(self):
        valid = {
            "confirmed_facts": {"project": "Fintech App"},
            "user_provided_content": {},
            "assumptions": ["Density is med"],
            "synthesized_brief": {"category": "fintech"}
        }
        res = validate_analysis_output(valid)
        self.assertEqual(res, valid)

        # Missing synthesized_brief
        invalid = dict(valid)
        del invalid["synthesized_brief"]
        with self.assertRaises(OrchestrationValidationError):
            validate_analysis_output(invalid)

    def test_validate_art_direction_output(self):
        valid = {
            "selected_art_direction": {"id": "ad-1", "name": "Minimal Clean"},
            "visual_thesis": "Clean aesthetic",
            "selected_palette": {"id": "pal-1"},
            "selected_typography": {"id": "typo-1"}
        }
        res = validate_art_direction_output(valid)
        self.assertEqual(res, valid)

        # Invalid selected_art_direction record
        invalid = dict(valid)
        invalid["selected_art_direction"] = "not_a_dict"
        with self.assertRaises(OrchestrationValidationError):
            validate_art_direction_output(invalid)

    def test_validate_implementation_output(self):
        valid = {
            "design_plan": {"plan_id": "p123"},
            "generated_files": [{"rel": "index.html", "bytes": 100}],
            "asset_manifest": {"total_assets": 1}
        }
        res = validate_implementation_output(valid)
        self.assertEqual(res, valid)

        # Empty files list
        invalid = dict(valid)
        invalid["generated_files"] = []
        with self.assertRaises(OrchestrationValidationError):
            validate_implementation_output(invalid)

    def test_validate_qa_critic_output(self):
        valid = {
            "verdict": "PASS",
            "dom_checks": {"passed": True},
            "screenshot_results": {"desktop": "PASS"},
            "runtime_health": {"status": "PASS"}
        }
        res = validate_qa_critic_output(valid)
        self.assertEqual(res["verdict"], "PASS")

        # Invalid verdict string
        invalid = dict(valid)
        invalid["verdict"] = "MAYBE"
        with self.assertRaises(OrchestrationValidationError):
            validate_qa_critic_output(invalid)

    def test_task_definition_and_result_models(self):
        t_def = TaskDefinition(
            task_id="T1",
            role=Role.PRODUCT_ANALYST.value,
            name="Analysis",
            description="Analyze brief",
            dependencies=["T0"],
            inputs={"key": "val"}
        )
        d = t_def.to_dict()
        self.assertEqual(d["task_id"], "T1")
        self.assertEqual(d["dependencies"], ["T0"])

        t_res = TaskResult(
            task_id="T1",
            role=Role.PRODUCT_ANALYST.value,
            status=TaskStatus.COMPLETED,
            output={"done": True},
            execution_type="DIRECT",
            agent_id="agent-01",
            duration_ms=12.5
        )
        rd = t_res.to_dict()
        self.assertEqual(rd["status"], "COMPLETED")
        self.assertEqual(rd["execution_type"], "DIRECT")
        self.assertEqual(rd["duration_ms"], 12.5)


if __name__ == "__main__":
    unittest.main()

