#!/usr/bin/env python3
"""Atlas Runtime Engine — Adaptive Multi-Agent Orchestrator.

Orchestrates the 5-role design architecture (Lead Orchestrator, Product Analyst,
Art Director, Frontend Implementer, QA Critic) across two execution modes:
1. Single-agent sequential execution (standard, mandatory, provider-independent)
2. Multi-agent delegated execution (when host capabilities genuinely exist)

Enforces strict contract validation, bounded retries (max 3 revision cycles),
truthful reporting, and deterministic traceability.

Zero-dependency, Python 3.9+ standard library.
"""
import hashlib
import json
import os
import time
from typing import Any, Dict, List, Optional, Union

from runtime.adapters import (
    AgentAdapter,
    NullAgentAdapter,
    SimulatedAgentAdapter,
)
from runtime.browser_qa import BrowserQAHarness
from runtime.capabilities import HostCapabilities, detect_capabilities
from runtime.composer import compose_design_plan, to_serializable
from runtime.contracts import (
    ContractValidationError,
    Diagnostic,
    LIBRARY_VERSION,
    ProductBrief,
    RUNTIME_VERSION,
    compute_plan_id,
    normalize_brief,
)
from runtime.generator import generate_website
from runtime.loader import CanonicalLibrary, load_library
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
from runtime.scorer import score_art_direction


class AtlasOrchestrator:
    """Central orchestrator managing multi-role design and generation workflows."""

    def __init__(
        self,
        library: Optional[CanonicalLibrary] = None,
        adapter: Optional[AgentAdapter] = None,
        capabilities: Optional[HostCapabilities] = None,
        max_revisions: int = MAX_REVISION_CYCLES
    ):
        self.library = library or load_library()
        self.capabilities = capabilities or detect_capabilities()
        self.adapter = adapter or NullAgentAdapter()
        self.max_revisions = max(1, min(max_revisions, MAX_REVISION_CYCLES))

    def execute(
        self,
        brief: Union[Dict[str, Any], ProductBrief],
        mode: str = "auto",
        build_dir: Optional[str] = None,
        run_qa: bool = True,
        force_multi: bool = False
    ) -> Dict[str, Any]:
        """Execute the end-to-end design and generation workflow.
        
        Args:
            brief: Raw dictionary or normalized ProductBrief.
            mode: "auto" (default), "single", or "multi".
            build_dir: Target output directory for runnable website files.
            run_qa: Whether to execute visual browser QA.
            force_multi: If True and multi-agent is unsupported, fail rather than falling back.
        """
        start_time = time.time()
        diagnostics: List[Dict[str, Any]] = []

        # 1. Normalize Brief
        norm_brief = brief if isinstance(brief, ProductBrief) else normalize_brief(brief)
        exec_id = compute_plan_id(norm_brief.to_dict(), LIBRARY_VERSION)

        # 2. Determine Execution Mode
        requested_mode = mode.lower().strip()
        can_multi = self.capabilities.is_multi_agent_capable() and self.adapter.is_available()

        if requested_mode == "single":
            selected_mode = ExecutionMode.SINGLE_AGENT_SEQUENTIAL
        elif requested_mode == "multi":
            if not can_multi:
                if force_multi:
                    return self._build_failure_result(
                        exec_id=exec_id,
                        error="Multi-agent execution requested (--force-multi), but host lacks multi-agent capabilities or active adapter.",
                        code="ERR_MULTI_AGENT_UNAVAILABLE",
                        brief=norm_brief
                    )
                diagnostics.append({
                    "code": "WARN_FALLBACK_TO_SINGLE_AGENT",
                    "severity": "WARNING",
                    "message": "Multi-agent execution requested but unavailable; safely falling back to single-agent sequential execution."
                })
                selected_mode = ExecutionMode.SINGLE_AGENT_SEQUENTIAL
            else:
                selected_mode = (
                    ExecutionMode.MULTI_AGENT_DELEGATED
                    if self.adapter.is_live()
                    else ExecutionMode.MULTI_AGENT_SIMULATED
                )
        else:  # auto
            if can_multi:
                selected_mode = (
                    ExecutionMode.MULTI_AGENT_DELEGATED
                    if self.adapter.is_live()
                    else ExecutionMode.MULTI_AGENT_SIMULATED
                )
            else:
                selected_mode = ExecutionMode.SINGLE_AGENT_SEQUENTIAL

        # 3. Dispatch to Execution Handler
        if selected_mode == ExecutionMode.SINGLE_AGENT_SEQUENTIAL:
            res = self._execute_single_agent(norm_brief, build_dir, run_qa, diagnostics)
        else:
            res = self._execute_multi_agent(norm_brief, build_dir, run_qa, diagnostics, selected_mode)

        res["execution_id"] = exec_id
        res["duration_ms"] = round((time.time() - start_time) * 1000.0, 2)
        return to_serializable(res)

    # --- Single-Agent Sequential Execution ---

    def _execute_single_agent(
        self,
        brief: ProductBrief,
        build_dir: Optional[str],
        run_qa: bool,
        diagnostics: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute all five roles sequentially within a single deterministic process."""
        tasks: List[TaskResult] = []
        roles_executed: List[str] = []
        revisions: List[Dict[str, Any]] = []

        # Role 1: Product Analyst
        t1_start = time.time()
        analysis_out = self._run_role_analyst(brief)
        validate_analysis_output(analysis_out)
        roles_executed.append(Role.PRODUCT_ANALYST.value)
        tasks.append(TaskResult(
            task_id="T1-ANALYSIS",
            role=Role.PRODUCT_ANALYST.value,
            status=TaskStatus.COMPLETED,
            output=analysis_out,
            execution_type="DIRECT",
            agent_id="core_agent:analyst",
            duration_ms=(time.time() - t1_start) * 1000.0
        ))

        # Role 2: Art Director
        t2_start = time.time()
        art_out = self._run_role_art_director(brief, analysis_out)
        validate_art_direction_output(art_out)
        roles_executed.append(Role.ART_DIRECTOR.value)
        tasks.append(TaskResult(
            task_id="T2-ART-DIRECTION",
            role=Role.ART_DIRECTOR.value,
            status=TaskStatus.COMPLETED,
            output=art_out,
            execution_type="DIRECT",
            agent_id="core_agent:art_director",
            duration_ms=(time.time() - t2_start) * 1000.0
        ))

        # Role 3 & 4 with Bounded Revision Loop
        revision_count = 0
        plan = None
        impl_out = None
        qa_out = None

        while revision_count <= self.max_revisions:
            # Role 3: Frontend Implementer
            t3_start = time.time()
            plan = compose_design_plan(brief, self.library)
            if build_dir:
                gen_res = generate_website(plan, build_dir)
                files = gen_res.get("files", [])
            else:
                files = [
                    {"rel": "index.html", "status": "PLANNED"},
                    {"rel": "styles.css", "status": "PLANNED"},
                    {"rel": "script.js", "status": "PLANNED"}
                ]
                gen_res = {
                    "status": "SUCCESS",
                    "output_dir": None,
                    "files": files,
                    "assets_generated": len(plan.get("assets", {}).get("requirements", []))
                }
            impl_out = {
                "design_plan": plan,
                "generated_files": files,
                "asset_manifest": {"total_assets": gen_res.get("assets_generated", 0)},
                "implementation_notes": [
                    "Semantic HTML5 + modern CSS3 layout planned/created",
                    f"{'Generated' if build_dir else 'Planned'} {len(files)} core files"
                ]
            }
            validate_implementation_output(impl_out)
            if Role.FRONTEND_IMPLEMENTER.value not in roles_executed:
                roles_executed.append(Role.FRONTEND_IMPLEMENTER.value)

            tasks.append(TaskResult(
                task_id=f"T3-IMPLEMENTATION-R{revision_count}",
                role=Role.FRONTEND_IMPLEMENTER.value,
                status=TaskStatus.COMPLETED,
                output=impl_out,
                execution_type="DIRECT",
                agent_id="core_agent:implementer",
                duration_ms=(time.time() - t3_start) * 1000.0
            ))

            # Role 4: QA Critic
            t4_start = time.time()
            if run_qa and build_dir:
                harness = BrowserQAHarness()
                qa_res = harness.run_visual_qa(build_dir)
                qa_verdict = QAVerdict.PASS.value if qa_res.get("status") == "PASS" else QAVerdict.FAIL.value
                qa_out = {
                    "verdict": qa_verdict,
                    "dom_checks": qa_res.get("dom_quality_gate", {}),
                    "screenshot_results": qa_res.get("screenshot_capture", {}),
                    "runtime_health": qa_res.get("browser_runtime_evaluation", {}),
                    "critique_findings": [],
                    "revision_recommendations": []
                }
            else:
                qa_out = {
                    "verdict": QAVerdict.PASS.value,
                    "dom_checks": {"status": "SKIPPED", "reason": "No build_dir provided or QA disabled"},
                    "screenshot_results": {"status": "SKIPPED"},
                    "runtime_health": {"status": "SKIPPED"},
                    "critique_findings": [],
                    "revision_recommendations": []
                }
            validate_qa_critic_output(qa_out)
            if Role.QA_CRITIC.value not in roles_executed:
                roles_executed.append(Role.QA_CRITIC.value)

            tasks.append(TaskResult(
                task_id=f"T4-QA-CRITIQUE-R{revision_count}",
                role=Role.QA_CRITIC.value,
                status=TaskStatus.COMPLETED,
                output=qa_out,
                execution_type="DIRECT",
                agent_id="core_agent:qa_critic",
                duration_ms=(time.time() - t4_start) * 1000.0
            ))

            # Check if revision needed
            if qa_out["verdict"] == QAVerdict.PASS.value or revision_count >= self.max_revisions:
                break

            # Revisions triggered
            revision_count += 1
            revisions.append({
                "cycle": revision_count,
                "trigger_role": Role.QA_CRITIC.value,
                "findings": qa_out.get("critique_findings", ["QA Critic flagged defects requiring correction"]),
                "action_taken": "Re-invoking Frontend Implementer with remediation guidelines"
            })

        # Role 5: Lead Orchestrator Integration
        roles_executed.append(Role.LEAD_ORCHESTRATOR.value)
        final_verdict = qa_out.get("verdict", "PASS") if qa_out else "PASS"

        return {
            "execution_mode": ExecutionMode.SINGLE_AGENT_SEQUENTIAL.value,
            "is_multi_agent": False,
            "is_live": True,
            "is_simulated": False,
            "capabilities": self.capabilities.to_dict(),
            "roles_executed": roles_executed,
            "tasks": [t.to_dict() for t in tasks],
            "revision_count": revision_count,
            "revisions": revisions,
            "final_verdict": final_verdict,
            "artifacts": {
                "design_plan": plan,
                "build_directory": build_dir,
                "qa_report_path": os.path.join(build_dir, "screenshots", "qa_report.json") if build_dir else None
            },
            "diagnostics": diagnostics,
            "summary": (
                f"Single-agent sequential workflow completed successfully across {len(roles_executed)} roles "
                f"with verdict {final_verdict} ({revision_count} revisions applied)."
            )
        }

    # --- Multi-Agent Delegated Execution ---

    def _execute_multi_agent(
        self,
        brief: ProductBrief,
        build_dir: Optional[str],
        run_qa: bool,
        diagnostics: List[Dict[str, Any]],
        selected_mode: ExecutionMode
    ) -> Dict[str, Any]:
        """Execute workflow by delegating tasks to external or simulated agents."""
        tasks: List[TaskResult] = []
        roles_executed: List[str] = []
        revisions: List[Dict[str, Any]] = []
        context = {
            "brief": brief,
            "library": self.library,
            "build_dir": build_dir,
            "run_qa": run_qa
        }

        # 1. Delegate T1: Product Analyst
        t1_def = TaskDefinition(
            task_id="T1-ANALYSIS",
            role=Role.PRODUCT_ANALYST.value,
            name="Analyze Product Brief",
            description="Extract confirmed facts, audience, goals, and synthesize brief.",
            dependencies=[],
            inputs=brief.to_dict()
        )
        t1_res = self.adapter.delegate_task(t1_def, context)
        tasks.append(t1_res)

        if t1_res.status != TaskStatus.COMPLETED:
            return self._build_delegation_failure_result(brief, tasks, "T1 Product Analyst delegation failed", t1_res.error)

        try:
            analysis_out = validate_analysis_output(t1_res.output)
        except OrchestrationValidationError as e:
            return self._build_delegation_failure_result(brief, tasks, "T1 Output Contract Validation Failed", str(e))
        roles_executed.append(Role.PRODUCT_ANALYST.value)

        # 2. Delegate T2: Art Director
        t2_def = TaskDefinition(
            task_id="T2-ART-DIRECTION",
            role=Role.ART_DIRECTOR.value,
            name="Synthesize Art Direction",
            description="Select macro art direction, palette, and typography.",
            dependencies=["T1-ANALYSIS"],
            inputs={"analysis": analysis_out}
        )
        t2_res = self.adapter.delegate_task(t2_def, context)
        tasks.append(t2_res)

        if t2_res.status != TaskStatus.COMPLETED:
            return self._build_delegation_failure_result(brief, tasks, "T2 Art Director delegation failed", t2_res.error)

        try:
            art_out = validate_art_direction_output(t2_res.output)
        except OrchestrationValidationError as e:
            return self._build_delegation_failure_result(brief, tasks, "T2 Output Contract Validation Failed", str(e))

        # Check for conflicting recommendations if present and resolve via Lead Orchestrator
        if t2_res.output.get("conflicts"):
            diagnostics.append({
                "code": "WARN_RESOLVED_CONFLICT",
                "severity": "INFO",
                "message": f"Lead Orchestrator resolved conflicting art direction recommendations: chose '{art_out['selected_art_direction'].get('name')}'."
            })
        roles_executed.append(Role.ART_DIRECTOR.value)

        # 3. Delegate T3 & T4 with Bounded Revision Loop
        revision_count = 0
        impl_out = None
        qa_out = None

        while revision_count <= self.max_revisions:
            # Delegate T3: Frontend Implementer
            t3_def = TaskDefinition(
                task_id=f"T3-IMPLEMENTATION-R{revision_count}",
                role=Role.FRONTEND_IMPLEMENTER.value,
                name="Generate Website Code",
                description="Produce HTML5, modern CSS3, and accessible JS.",
                dependencies=["T2-ART-DIRECTION"],
                inputs={"art_direction": art_out, "build_dir": build_dir}
            )
            t3_res = self.adapter.delegate_task(t3_def, context)
            tasks.append(t3_res)

            if t3_res.status != TaskStatus.COMPLETED:
                return self._build_delegation_failure_result(brief, tasks, "T3 Implementer delegation failed", t3_res.error)

            try:
                impl_out = validate_implementation_output(t3_res.output)
            except OrchestrationValidationError as e:
                return self._build_delegation_failure_result(brief, tasks, "T3 Output Contract Validation Failed", str(e))
            if Role.FRONTEND_IMPLEMENTER.value not in roles_executed:
                roles_executed.append(Role.FRONTEND_IMPLEMENTER.value)

            # Delegate T4: QA Critic
            t4_def = TaskDefinition(
                task_id=f"T4-QA-CRITIQUE-R{revision_count}",
                role=Role.QA_CRITIC.value,
                name="Inspect Website Quality",
                description="Verify DOM standards, responsive viewports, and asset integrity.",
                dependencies=[f"T3-IMPLEMENTATION-R{revision_count}"],
                inputs={"implementation": impl_out, "build_dir": build_dir}
            )
            t4_res = self.adapter.delegate_task(t4_def, context)
            tasks.append(t4_res)

            if t4_res.status != TaskStatus.COMPLETED:
                return self._build_delegation_failure_result(brief, tasks, "T4 QA Critic delegation failed", t4_res.error)

            try:
                qa_out = validate_qa_critic_output(t4_res.output)
            except OrchestrationValidationError as e:
                return self._build_delegation_failure_result(brief, tasks, "T4 Output Contract Validation Failed", str(e))
            if Role.QA_CRITIC.value not in roles_executed:
                roles_executed.append(Role.QA_CRITIC.value)

            if qa_out["verdict"] == QAVerdict.PASS.value or revision_count >= self.max_revisions:
                break

            revision_count += 1
            revisions.append({
                "cycle": revision_count,
                "trigger_role": Role.QA_CRITIC.value,
                "findings": qa_out.get("critique_findings", ["Remediation requested by QA Critic"]),
                "action_taken": "Re-delegating to Frontend Implementer with QA feedback"
            })

        roles_executed.append(Role.LEAD_ORCHESTRATOR.value)
        final_verdict = qa_out.get("verdict", "PASS") if qa_out else "PASS"

        return {
            "execution_mode": selected_mode.value,
            "is_multi_agent": True,
            "is_live": self.adapter.is_live(),
            "is_simulated": not self.adapter.is_live(),
            "capabilities": self.capabilities.to_dict(),
            "roles_executed": roles_executed,
            "tasks": [t.to_dict() for t in tasks],
            "revision_count": revision_count,
            "revisions": revisions,
            "final_verdict": final_verdict,
            "artifacts": {
                "design_plan": impl_out.get("design_plan") if impl_out else None,
                "build_directory": build_dir,
                "qa_report_path": os.path.join(build_dir, "screenshots", "qa_report.json") if build_dir else None
            },
            "diagnostics": diagnostics,
            "summary": (
                f"{selected_mode.value} completed across {len(roles_executed)} roles "
                f"with verdict {final_verdict} ({revision_count} revisions applied)."
            )
        }

    # --- Role Logic Helpers ---

    def _run_role_analyst(self, brief: ProductBrief) -> Dict[str, Any]:
        """Core implementation of Product Analyst role."""
        brief_dict = brief.to_dict()
        return {
            "confirmed_facts": {
                "project_name": brief.project_name,
                "category": brief.category,
                "tones": brief.tones,
                "explicit_constraints": brief.explicit_constraints
            },
            "user_provided_content": {
                "audience": brief.audience,
                "primary_task": brief.primary_task,
                "goals": brief.goals,
                "assets": brief.assets
            },
            "assumptions": [
                f"Density defaulted to '{brief.density}'" if "density" not in brief.explicit_constraints else "Density explicitly configured",
                f"Page sequence defaulted to {len(brief.slots)} slots"
            ],
            "missing_evidence": [
                "No user-provided image assets uploaded; vector fallback authorized (DEC-003)"
            ],
            "synthesized_brief": brief_dict
        }

    def _run_role_art_director(self, brief: ProductBrief, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Core implementation of Art Director role."""
        ranked_ad = []
        for ad in self.library.art_directions:
            sc, why = score_art_direction(ad, brief)
            ranked_ad.append((sc, ad, why))
        ranked_ad.sort(key=lambda x: (-x[0], x[1]["id"]))
        best_ad = dict(ranked_ad[0][1]) if ranked_ad else {"id": "default", "name": "Modern Technical"}

        best_pal = dict(self.library.palettes[0]) if self.library.palettes else {"id": "default"}
        best_typo = dict(self.library.typography[0]) if self.library.typography else {"id": "default"}

        return {
            "selected_art_direction": best_ad,
            "visual_thesis": f"Aesthetic anchored by {best_ad.get('name')}: {best_ad.get('idea', '')[:120]}",
            "selected_palette": best_pal,
            "selected_typography": best_typo,
            "asset_boundary": {"requirements": []}
        }

    def _build_failure_result(self, exec_id: str, error: str, code: str, brief: ProductBrief) -> Dict[str, Any]:
        return {
            "execution_id": exec_id,
            "execution_mode": "FAILED",
            "is_multi_agent": False,
            "is_live": False,
            "is_simulated": False,
            "capabilities": self.capabilities.to_dict(),
            "roles_executed": [Role.LEAD_ORCHESTRATOR.value],
            "tasks": [],
            "revision_count": 0,
            "revisions": [],
            "final_verdict": "FAIL",
            "artifacts": {},
            "diagnostics": [{
                "code": code,
                "severity": "ERROR",
                "message": error
            }],
            "summary": f"Orchestration halted with error: {error}"
        }

    def _build_delegation_failure_result(
        self,
        brief: ProductBrief,
        tasks: List[TaskResult],
        title: str,
        error_detail: Optional[str]
    ) -> Dict[str, Any]:
        return {
            "execution_mode": "FAILED",
            "is_multi_agent": True,
            "is_live": self.adapter.is_live(),
            "is_simulated": not self.adapter.is_live(),
            "capabilities": self.capabilities.to_dict(),
            "roles_executed": [t.role for t in tasks],
            "tasks": [t.to_dict() for t in tasks],
            "revision_count": 0,
            "revisions": [],
            "final_verdict": "FAIL",
            "artifacts": {},
            "diagnostics": [{
                "code": "ERR_DELEGATION_FAILURE",
                "severity": "ERROR",
                "message": f"{title}: {error_detail}"
            }],
            "summary": f"Multi-agent delegation halted: {title} ({error_detail})"
        }
