#!/usr/bin/env python3
"""Atlas Runtime Engine — Multi-Agent Orchestration Contracts and Schemas.

Defines role contracts, task lifecycle models, execution reports,
and validation logic for single-agent and multi-agent coordination.
Zero-dependency, Python 3.9+ standard library.
"""
from enum import Enum
import time
from typing import Any, Dict, List, Optional, Set, Union

MAX_REVISION_CYCLES = 3


class Role(str, Enum):
    LEAD_ORCHESTRATOR = "Lead Orchestrator"
    PRODUCT_ANALYST = "Product Analyst"
    ART_DIRECTOR = "Art Director"
    FRONTEND_IMPLEMENTER = "Frontend Implementer"
    QA_CRITIC = "QA Critic"


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class ExecutionMode(str, Enum):
    SINGLE_AGENT_SEQUENTIAL = "SINGLE_AGENT_SEQUENTIAL"
    MULTI_AGENT_DELEGATED = "MULTI_AGENT_DELEGATED"
    MULTI_AGENT_SIMULATED = "MULTI_AGENT_SIMULATED"


class QAVerdict(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


class OrchestrationValidationError(ValueError):
    """Raised when an inter-role contract or delegated output fails validation."""
    def __init__(self, role: str, message: str, code: str = "ERR_CONTRACT_INVALID"):
        super().__init__(f"[{role}] [{code}] {message}")
        self.role = role
        self.message = message
        self.code = code


class TaskDefinition:
    """Describes an assignable task in the orchestration plan."""
    def __init__(
        self,
        task_id: str,
        role: str,
        name: str,
        description: str,
        dependencies: Optional[List[str]] = None,
        inputs: Optional[Dict[str, Any]] = None
    ):
        self.task_id = task_id
        self.role = role
        self.name = name
        self.description = description
        self.dependencies = list(dependencies or [])
        self.inputs = dict(inputs or {})

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "role": self.role,
            "name": self.name,
            "description": self.description,
            "dependencies": self.dependencies,
            "inputs": self.inputs
        }


class TaskResult:
    """Records the outcome of an executed task."""
    def __init__(
        self,
        task_id: str,
        role: str,
        status: TaskStatus,
        output: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        execution_type: str = "DIRECT",  # DIRECT, DELEGATED, SIMULATED
        agent_id: Optional[str] = None,
        duration_ms: float = 0.0
    ):
        self.task_id = task_id
        self.role = role
        self.status = status
        self.output = dict(output or {}) if output else None
        self.error = error
        self.execution_type = execution_type
        self.agent_id = agent_id or ("single_agent_core" if execution_type == "DIRECT" else "external_agent")
        self.duration_ms = duration_ms

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "role": self.role,
            "status": self.status.value if isinstance(self.status, TaskStatus) else str(self.status),
            "output": self.output,
            "error": self.error,
            "execution_type": self.execution_type,
            "agent_id": self.agent_id,
            "duration_ms": round(self.duration_ms, 2)
        }


# --- Role Output Contracts Validation ---

def validate_analysis_output(out: Any) -> Dict[str, Any]:
    """Validate Product Analyst contract."""
    if not isinstance(out, dict):
        raise OrchestrationValidationError(Role.PRODUCT_ANALYST.value, "Output must be a dictionary")
    for req in ("confirmed_facts", "user_provided_content", "assumptions", "synthesized_brief"):
        if req not in out:
            raise OrchestrationValidationError(Role.PRODUCT_ANALYST.value, f"Missing required field: '{req}'")
    if not isinstance(out["synthesized_brief"], dict):
        raise OrchestrationValidationError(Role.PRODUCT_ANALYST.value, "Field 'synthesized_brief' must be a dictionary")
    return out


def validate_art_direction_output(out: Any) -> Dict[str, Any]:
    """Validate Art Director contract."""
    if not isinstance(out, dict):
        raise OrchestrationValidationError(Role.ART_DIRECTOR.value, "Output must be a dictionary")
    for req in ("selected_art_direction", "visual_thesis", "selected_palette", "selected_typography"):
        if req not in out:
            raise OrchestrationValidationError(Role.ART_DIRECTOR.value, f"Missing required field: '{req}'")
    ad = out["selected_art_direction"]
    if not isinstance(ad, dict) or "id" not in ad or "name" not in ad:
        raise OrchestrationValidationError(Role.ART_DIRECTOR.value, "Invalid selected_art_direction record")
    return out


def validate_implementation_output(out: Any) -> Dict[str, Any]:
    """Validate Frontend Implementer contract."""
    if not isinstance(out, dict):
        raise OrchestrationValidationError(Role.FRONTEND_IMPLEMENTER.value, "Output must be a dictionary")
    for req in ("design_plan", "generated_files", "asset_manifest"):
        if req not in out:
            raise OrchestrationValidationError(Role.FRONTEND_IMPLEMENTER.value, f"Missing required field: '{req}'")
    if not isinstance(out["generated_files"], list) or len(out["generated_files"]) == 0:
        raise OrchestrationValidationError(Role.FRONTEND_IMPLEMENTER.value, "Field 'generated_files' must be a non-empty list")
    return out


def validate_qa_critic_output(out: Any) -> Dict[str, Any]:
    """Validate QA Critic contract."""
    if not isinstance(out, dict):
        raise OrchestrationValidationError(Role.QA_CRITIC.value, "Output must be a dictionary")
    for req in ("verdict", "dom_checks", "screenshot_results", "runtime_health"):
        if req not in out:
            raise OrchestrationValidationError(Role.QA_CRITIC.value, f"Missing required field: '{req}'")
    verdict = str(out.get("verdict")).upper()
    if verdict not in ("PASS", "WARN", "FAIL"):
        raise OrchestrationValidationError(Role.QA_CRITIC.value, f"Invalid QA verdict '{verdict}'. Must be PASS, WARN, or FAIL")
    return out

