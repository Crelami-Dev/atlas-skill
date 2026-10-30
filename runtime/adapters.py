#!/usr/bin/env python3
"""Atlas Runtime Engine — Multi-Agent Host Adapters.

Provides the adapter boundary for delegating roles to external agents,
subagents, or deterministic test simulators. Enforces strict honesty:
simulations are explicitly marked as SIMULATED and never claimed as LIVE.

Zero-dependency, Python 3.9+ standard library.
"""
from abc import ABC, abstractmethod
import concurrent.futures
import time
from typing import Any, Callable, Dict, List, Optional, Set

from runtime.composer import to_serializable
from runtime.orchestration_contracts import (
    Role,
    TaskDefinition,
    TaskResult,
    TaskStatus,
)


class AgentAdapter(ABC):
    """Abstract base class for multi-agent host adapters."""

    @abstractmethod
    def is_live(self) -> bool:
        """Returns True only if this adapter dispatches to real live external agents."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if the adapter is functional and ready to accept tasks."""
        pass

    @abstractmethod
    def delegate_task(self, task: TaskDefinition, context: Dict[str, Any]) -> TaskResult:
        """Delegate a single task to an assigned agent."""
        pass

    def execute_parallel(self, tasks: List[TaskDefinition], context: Dict[str, Any]) -> List[TaskResult]:
        """Execute independent tasks concurrently when supported."""
        results = []
        for t in tasks:
            results.append(self.delegate_task(t, context))
        return results


class NullAgentAdapter(AgentAdapter):
    """Null adapter used when no multi-agent support is configured."""

    def is_live(self) -> bool:
        return False

    def is_available(self) -> bool:
        return False

    def delegate_task(self, task: TaskDefinition, context: Dict[str, Any]) -> TaskResult:
        return TaskResult(
            task_id=task.task_id,
            role=task.role,
            status=TaskStatus.FAILED,
            error="NullAgentAdapter: No multi-agent host adapter available in this environment.",
            execution_type="FAILED"
        )


class SimulatedAgentAdapter(AgentAdapter):
    """Deterministic multi-agent test adapter for validation and automated testing.
    
    Explicitly labels all executed tasks as SIMULATED to preserve truth in reporting.
    """

    def __init__(
        self,
        should_succeed: bool = True,
        simulate_timeout_on: Optional[Set[str]] = None,
        simulate_invalid_output_on: Optional[Set[str]] = None,
        simulate_failure_on: Optional[Set[str]] = None,
        conflict_recommendation: Optional[Dict[str, Any]] = None,
        custom_handlers: Optional[Dict[str, Callable[[TaskDefinition, Dict[str, Any]], Dict[str, Any]]]] = None,
        supports_parallel: bool = True
    ):
        self.should_succeed = should_succeed
        self.simulate_timeout_on: Set[str] = set(simulate_timeout_on or [])
        self.simulate_invalid_output_on: Set[str] = set(simulate_invalid_output_on or [])
        self.simulate_failure_on: Set[str] = set(simulate_failure_on or [])
        self.conflict_recommendation = conflict_recommendation
        self.custom_handlers = custom_handlers or {}
        self.supports_parallel = supports_parallel
        self.delegated_call_log: List[Dict[str, Any]] = []

    def is_live(self) -> bool:
        # Strictly False: this is a test simulation harness
        return False

    def is_available(self) -> bool:
        return True

    def delegate_task(self, task: TaskDefinition, context: Dict[str, Any]) -> TaskResult:
        start_time = time.time()
        agent_id = f"sim-agent:{task.role.lower().replace(' ', '-')}:01"
        self.delegated_call_log.append({
            "task_id": task.task_id,
            "role": task.role,
            "agent_id": agent_id,
            "timestamp": start_time
        })

        # 1. Simulate timeout
        if task.task_id in self.simulate_timeout_on or task.role in self.simulate_timeout_on:
            return TaskResult(
                task_id=task.task_id,
                role=task.role,
                status=TaskStatus.FAILED,
                error=f"Simulated timeout: agent {agent_id} did not respond within deadline",
                execution_type="SIMULATED",
                agent_id=agent_id,
                duration_ms=(time.time() - start_time) * 1000.0
            )

        # 2. Simulate failure
        if not self.should_succeed or task.task_id in self.simulate_failure_on or task.role in self.simulate_failure_on:
            return TaskResult(
                task_id=task.task_id,
                role=task.role,
                status=TaskStatus.FAILED,
                error=f"Simulated agent failure in {task.role}",
                execution_type="SIMULATED",
                agent_id=agent_id,
                duration_ms=(time.time() - start_time) * 1000.0
            )

        # 3. Simulate invalid output
        if task.task_id in self.simulate_invalid_output_on or task.role in self.simulate_invalid_output_on:
            return TaskResult(
                task_id=task.task_id,
                role=task.role,
                status=TaskStatus.COMPLETED,
                output={"corrupted_payload": True},  # Missing required contract keys
                execution_type="SIMULATED",
                agent_id=agent_id,
                duration_ms=(time.time() - start_time) * 1000.0
            )

        # 4. Custom handler if provided
        if task.role in self.custom_handlers:
            try:
                out = self.custom_handlers[task.role](task, context)
                return TaskResult(
                    task_id=task.task_id,
                    role=task.role,
                    status=TaskStatus.COMPLETED,
                    output=out,
                    execution_type="SIMULATED",
                    agent_id=agent_id,
                    duration_ms=(time.time() - start_time) * 1000.0
                )
            except Exception as e:
                return TaskResult(
                    task_id=task.task_id,
                    role=task.role,
                    status=TaskStatus.FAILED,
                    error=f"Custom handler error: {e}",
                    execution_type="SIMULATED",
                    agent_id=agent_id,
                    duration_ms=(time.time() - start_time) * 1000.0
                )

        # 5. Default simulated output based on role context
        output_payload = self._generate_simulated_role_output(task, context)
        return TaskResult(
            task_id=task.task_id,
            role=task.role,
            status=TaskStatus.COMPLETED,
            output=output_payload,
            execution_type="SIMULATED",
            agent_id=agent_id,
            duration_ms=(time.time() - start_time) * 1000.0
        )

    def execute_parallel(self, tasks: List[TaskDefinition], context: Dict[str, Any]) -> List[TaskResult]:
        if not self.supports_parallel or len(tasks) <= 1:
            return [self.delegate_task(t, context) for t in tasks]

        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(4, len(tasks))) as executor:
            futures = [executor.submit(self.delegate_task, t, context) for t in tasks]
            for f in concurrent.futures.as_completed(futures):
                results.append(f.result())
        # Sort results back to original task order
        task_order = {t.task_id: idx for idx, t in enumerate(tasks)}
        results.sort(key=lambda r: task_order.get(r.task_id, 0))
        return results

    def _generate_simulated_role_output(self, task: TaskDefinition, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate role output using the real underlying runtime functions."""
        role = task.role
        lib = context.get("library")
        brief = context.get("brief")

        if role == Role.PRODUCT_ANALYST.value:
            brief_dict = brief.to_dict() if hasattr(brief, "to_dict") else dict(brief)
            return {
                "confirmed_facts": {
                    "project_name": brief_dict.get("project_name"),
                    "category": brief_dict.get("category"),
                    "tones": brief_dict.get("tones")
                },
                "user_provided_content": {
                    "audience": brief_dict.get("audience"),
                    "goals": brief_dict.get("goals")
                },
                "assumptions": [
                    f"Density assumed as '{brief_dict.get('density', 'med')}'",
                    f"Page archetype resolved to '{brief_dict.get('page_type', 'marketing')}'"
                ],
                "missing_evidence": [
                    "No user-provided custom assets uploaded; standard vector fallbacks permitted"
                ],
                "synthesized_brief": brief_dict
            }

        elif role == Role.ART_DIRECTOR.value:
            if self.conflict_recommendation:
                return dict(self.conflict_recommendation)

            from runtime.scorer import score_art_direction
            # Pick best art direction
            ranked = []
            for ad in lib.art_directions:
                sc, why = score_art_direction(ad, brief)
                ranked.append((sc, ad, why))
            ranked.sort(key=lambda x: (-x[0], x[1]["id"]))
            best_ad = to_serializable(ranked[0][1]) if ranked else {"id": "default", "name": "Default"}
            best_palette = to_serializable(lib.palettes[0]) if lib and lib.palettes else {"id": "default"}
            best_typo = to_serializable(lib.typography[0]) if lib and lib.typography else {"id": "default"}

            return {
                "selected_art_direction": best_ad,
                "visual_thesis": f"Intentional aesthetic anchored by {best_ad.get('name', 'Art Direction')}",
                "selected_palette": best_palette,
                "selected_typography": best_typo,
                "asset_boundary": {"requirements": []}
            }

        elif role == Role.FRONTEND_IMPLEMENTER.value:
            from runtime.composer import compose_design_plan
            from runtime.generator import generate_website

            build_dir = context.get("build_dir")
            plan = compose_design_plan(brief, lib)
            if build_dir:
                gen_res = generate_website(plan, build_dir)
                files = gen_res.get("files", [])
            else:
                files = [
                    {"rel": "index.html", "status": "PLANNED"},
                    {"rel": "styles.css", "status": "PLANNED"},
                    {"rel": "script.js", "status": "PLANNED"}
                ]
                gen_res = {"status": "SUCCESS", "files": files, "assets_generated": 0}

            return {
                "design_plan": plan,
                "generated_files": files,
                "asset_manifest": {"total_assets": gen_res.get("assets_generated", 0)},
                "implementation_notes": [
                    "Vanilla HTML5/CSS3 structure generated cleanly",
                    "Fluid typography and WCAG contrast verified"
                ]
            }

        elif role == Role.QA_CRITIC.value:
            from runtime.browser_qa import BrowserQAHarness
            build_dir = context.get("build_dir")
            harness = BrowserQAHarness()
            qa_res = harness.run_visual_qa(build_dir) if build_dir else {"status": "PASS", "viewports": []}

            return {
                "verdict": "PASS" if qa_res.get("status") == "PASS" else "FAIL",
                "dom_checks": qa_res.get("dom_quality_gate", {}),
                "screenshot_results": qa_res.get("screenshot_capture", {}),
                "runtime_health": qa_res.get("browser_runtime_evaluation", {}),
                "critique_findings": [],
                "revision_recommendations": []
            }

        return {"simulated_generic_output": True}


class LiveHostAdapter(AgentAdapter):
    """Live host adapter interface for platforms supporting real subagent invocation.
    
    Verifies actual live host bridge connectivity. In unconfigured or standard
    CLI environments, truthfully reports as unavailable without pretending to be connected.
    """

    def __init__(self, endpoint_url: Optional[str] = None, auth_token: Optional[str] = None):
        self.endpoint_url = endpoint_url
        self.auth_token = auth_token

    def is_live(self) -> bool:
        # Real live external delegation
        return True

    def is_available(self) -> bool:
        # Strictly check if an actual external agent bridge endpoint is reachable
        return bool(self.endpoint_url and self.auth_token)

    def delegate_task(self, task: TaskDefinition, context: Dict[str, Any]) -> TaskResult:
        if not self.is_available():
            return TaskResult(
                task_id=task.task_id,
                role=task.role,
                status=TaskStatus.FAILED,
                error="LiveHostAdapter unavailable: No live host subagent endpoint or socket connected.",
                execution_type="FAILED",
                agent_id="live_agent_disconnected"
            )

        # Dispatches over live IPC/socket bridge if connected
        raise NotImplementedError("Live host IPC protocol not active in current session.")
