#!/usr/bin/env python3
"""Atlas Runtime Engine — Unit Tests for Multi-Agent Orchestration & Adapters."""
import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from runtime.adapters import LiveHostAdapter, NullAgentAdapter, SimulatedAgentAdapter
from runtime.capabilities import detect_capabilities
from runtime.contracts import normalize_brief
from runtime.loader import load_library
from runtime.orchestration_contracts import ExecutionMode, Role, TaskDefinition, TaskStatus
from runtime.orchestrator import AtlasOrchestrator


class TestMultiAgentOrchestration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = load_library()
        cls.brief = normalize_brief({
            "project_name": "MultiAgent Test",
            "category": "saas",
            "tones": ["minimal"]
        })
        cls.multi_caps = detect_capabilities(override={
            "supports_subagents": True,
            "supports_task_delegation": True,
            "supports_parallel_execution": True,
            "supports_shared_artifacts": True,
            "supports_interagent_messaging": True
        })

    def test_simulated_multi_agent_execution_honesty(self):
        """Simulated adapter executions must be explicitly labeled as SIMULATED, not LIVE."""
        sim_adapter = SimulatedAgentAdapter()
        orch = AtlasOrchestrator(
            library=self.lib,
            adapter=sim_adapter,
            capabilities=self.multi_caps
        )
        res = orch.execute(self.brief, mode="multi")

        self.assertEqual(res["execution_mode"], ExecutionMode.MULTI_AGENT_SIMULATED.value)
        self.assertTrue(res["is_multi_agent"])
        self.assertFalse(res["is_live"])
        self.assertTrue(res["is_simulated"])
        self.assertEqual(res["final_verdict"], "PASS")

        # Verify tasks have agent IDs and SIMULATED execution type
        for t in res["tasks"]:
            self.assertEqual(t["execution_type"], "SIMULATED")
            self.assertTrue(t["agent_id"].startswith("sim-agent:"))

    def test_delegated_agent_timeout_handling(self):
        """Simulated timeout on a task causes explicit delegation failure."""
        sim_adapter = SimulatedAgentAdapter(simulate_timeout_on={"T1-ANALYSIS"})
        orch = AtlasOrchestrator(
            library=self.lib,
            adapter=sim_adapter,
            capabilities=self.multi_caps
        )
        res = orch.execute(self.brief, mode="multi")

        self.assertEqual(res["execution_mode"], "FAILED")
        self.assertEqual(res["final_verdict"], "FAIL")
        self.assertTrue(any("timeout" in d["message"].lower() for d in res["diagnostics"]))

    def test_delegated_invalid_contract_output_rejection(self):
        """Invalid delegated payload is caught by contract validator and rejected."""
        sim_adapter = SimulatedAgentAdapter(simulate_invalid_output_on={"T2-ART-DIRECTION"})
        orch = AtlasOrchestrator(
            library=self.lib,
            adapter=sim_adapter,
            capabilities=self.multi_caps
        )
        res = orch.execute(self.brief, mode="multi")

        self.assertEqual(res["execution_mode"], "FAILED")
        self.assertEqual(res["final_verdict"], "FAIL")
        self.assertTrue(any("validation failed" in d["message"].lower() for d in res["diagnostics"]))

    def test_live_host_adapter_unconnected_reports_unavailable(self):
        """Unconnected LiveHostAdapter reports available=False and fails cleanly."""
        live_adapter = LiveHostAdapter()  # No endpoint or token
        self.assertTrue(live_adapter.is_live())
        self.assertFalse(live_adapter.is_available())

        t_def = TaskDefinition("T1", Role.PRODUCT_ANALYST.value, "Test", "Desc")
        t_res = live_adapter.delegate_task(t_def, {})
        self.assertEqual(t_res.status, TaskStatus.FAILED)
        self.assertIn("unavailable", t_res.error.lower())

    def test_simulated_adapter_parallel_task_execution(self):
        """Verify parallel execution of independent tasks via thread pool."""
        sim_adapter = SimulatedAgentAdapter(supports_parallel=True)
        tasks = [
            TaskDefinition("P1", Role.PRODUCT_ANALYST.value, "Task 1", "Desc"),
            TaskDefinition("P2", Role.PRODUCT_ANALYST.value, "Task 2", "Desc"),
            TaskDefinition("P3", Role.PRODUCT_ANALYST.value, "Task 3", "Desc")
        ]
        context = {"brief": self.brief, "library": self.lib}
        results = sim_adapter.execute_parallel(tasks, context)

        self.assertEqual(len(results), 3)
        self.assertEqual([r.task_id for r in results], ["P1", "P2", "P3"])
        for r in results:
            self.assertEqual(r.status, TaskStatus.COMPLETED)
            self.assertEqual(r.execution_type, "SIMULATED")

    def test_conflicting_recommendation_resolution(self):
        """Lead Orchestrator resolves conflicting recommendations from Art Director."""
        conflict_rec = {
            "selected_art_direction": {"id": "art-dir:selected", "name": "Selected Winner"},
            "visual_thesis": "Thesis",
            "selected_palette": {"id": "pal-1"},
            "selected_typography": {"id": "typo-1"},
            "conflicts": [
                {"alternative_id": "art-dir:rejected", "score_delta": -2.5}
            ]
        }
        sim_adapter = SimulatedAgentAdapter(conflict_recommendation=conflict_rec)
        orch = AtlasOrchestrator(
            library=self.lib,
            adapter=sim_adapter,
            capabilities=self.multi_caps
        )
        res = orch.execute(self.brief, mode="multi")

        self.assertEqual(res["final_verdict"], "PASS")
        self.assertTrue(any("resolved conflicting" in d["message"].lower() for d in res["diagnostics"]))


if __name__ == "__main__":
    unittest.main()

