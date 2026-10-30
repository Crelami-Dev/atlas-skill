#!/usr/bin/env python3
"""Atlas Runtime Engine — Capability Detection Model.

Provides an explicit, verifiable, and injectable capability model to determine
whether the host environment genuinely supports multi-agent execution,
task delegation, parallel processing, shared artifacts, and inter-agent messaging.

Zero-dependency, Python 3.9+ standard library.
"""
import json
import os
from typing import Any, Dict, Optional, Set, Union

KNOWN_CAPABILITIES: Set[str] = {
    "supports_subagents",
    "supports_task_delegation",
    "supports_parallel_execution",
    "supports_shared_artifacts",
    "supports_interagent_messaging"
}


class HostCapabilities:
    """Represents the explicit execution capabilities of the host environment."""

    def __init__(
        self,
        supports_subagents: bool = False,
        supports_task_delegation: bool = False,
        supports_parallel_execution: bool = False,
        supports_shared_artifacts: bool = False,
        supports_interagent_messaging: bool = False,
        detection_source: str = "environment_scan",
        custom_capabilities: Optional[Dict[str, bool]] = None
    ):
        self.supports_subagents = bool(supports_subagents)
        self.supports_task_delegation = bool(supports_task_delegation)
        self.supports_parallel_execution = bool(supports_parallel_execution)
        self.supports_shared_artifacts = bool(supports_shared_artifacts)
        self.supports_interagent_messaging = bool(supports_interagent_messaging)
        self.detection_source = str(detection_source)
        self.custom_capabilities: Dict[str, bool] = dict(custom_capabilities or {})

    def is_multi_agent_capable(self) -> bool:
        """Returns True only when the core prerequisites for multi-agent delegation exist."""
        return self.supports_subagents and self.supports_task_delegation

    def to_dict(self) -> Dict[str, Any]:
        """Convert capability set to a serializable dictionary."""
        d = {
            "supports_subagents": self.supports_subagents,
            "supports_task_delegation": self.supports_task_delegation,
            "supports_parallel_execution": self.supports_parallel_execution,
            "supports_shared_artifacts": self.supports_shared_artifacts,
            "supports_interagent_messaging": self.supports_interagent_messaging,
            "is_multi_agent_capable": self.is_multi_agent_capable(),
            "detection_source": self.detection_source
        }
        if self.custom_capabilities:
            d["custom_capabilities"] = self.custom_capabilities
        return d

    def __repr__(self) -> str:
        return f"<HostCapabilities multi_agent={self.is_multi_agent_capable()} source={self.detection_source}>"


def detect_capabilities(
    env: Optional[Dict[str, str]] = None,
    config: Optional[Dict[str, Any]] = None,
    override: Optional[Union[Dict[str, Any], HostCapabilities, str]] = None
) -> HostCapabilities:
    """Detect host execution capabilities.
    
    Safe defaults: unknown capabilities default to False.
    Does NOT infer multi-agent support from model name or host OS.
    Supports explicit programmatic override for reproducible testing.
    """
    target_env = env if env is not None else os.environ

    # 1. Handle explicit test override if passed via argument or environment
    raw_override = override or target_env.get("ATLAS_CAPABILITIES_OVERRIDE")
    if raw_override:
        if isinstance(raw_override, HostCapabilities):
            return raw_override
        if isinstance(raw_override, str):
            try:
                raw_override = json.loads(raw_override)
            except Exception:
                raw_override = None

        if isinstance(raw_override, dict):
            custom = {k: bool(v) for k, v in raw_override.items() if k not in KNOWN_CAPABILITIES}
            return HostCapabilities(
                supports_subagents=bool(raw_override.get("supports_subagents", False)),
                supports_task_delegation=bool(raw_override.get("supports_task_delegation", False)),
                supports_parallel_execution=bool(raw_override.get("supports_parallel_execution", False)),
                supports_shared_artifacts=bool(raw_override.get("supports_shared_artifacts", False)),
                supports_interagent_messaging=bool(raw_override.get("supports_interagent_messaging", False)),
                detection_source="explicit_override",
                custom_capabilities=custom
            )

    # 2. Check explicit configuration dict
    if config and isinstance(config, dict):
        custom = {k: bool(v) for k, v in config.items() if k not in KNOWN_CAPABILITIES and isinstance(v, bool)}
        return HostCapabilities(
            supports_subagents=bool(config.get("supports_subagents", False)),
            supports_task_delegation=bool(config.get("supports_task_delegation", False)),
            supports_parallel_execution=bool(config.get("supports_parallel_execution", False)),
            supports_shared_artifacts=bool(config.get("supports_shared_artifacts", False)),
            supports_interagent_messaging=bool(config.get("supports_interagent_messaging", False)),
            detection_source="configuration",
            custom_capabilities=custom
        )

    # 3. Environment scan
    # In standard Python CLI runtimes without external agent host hooks,
    # capabilities default safely to False.
    # An explicit host integration flag is required.
    subagents = target_env.get("ATLAS_HOST_SUPPORTS_SUBAGENTS", "").strip().lower() in ("1", "true", "yes")
    delegation = target_env.get("ATLAS_HOST_SUPPORTS_DELEGATION", "").strip().lower() in ("1", "true", "yes")
    parallel = target_env.get("ATLAS_HOST_SUPPORTS_PARALLEL", "").strip().lower() in ("1", "true", "yes")
    artifacts = target_env.get("ATLAS_HOST_SUPPORTS_SHARED_ARTIFACTS", "").strip().lower() in ("1", "true", "yes")
    messaging = target_env.get("ATLAS_HOST_SUPPORTS_MESSAGING", "").strip().lower() in ("1", "true", "yes")

    # If subagents is enabled, delegation can be supported
    if subagents and "ATLAS_HOST_SUPPORTS_DELEGATION" not in target_env:
        delegation = True

    return HostCapabilities(
        supports_subagents=subagents,
        supports_task_delegation=delegation,
        supports_parallel_execution=parallel,
        supports_shared_artifacts=artifacts,
        supports_interagent_messaging=messaging,
        detection_source="environment_scan"
    )

