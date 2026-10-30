#!/usr/bin/env python3
"""Atlas Runtime Engine — Unit Tests for Capability Detection."""
import json
import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from runtime.capabilities import HostCapabilities, detect_capabilities


class TestCapabilities(unittest.TestCase):
    def test_default_environment_scan_defaults_to_single_agent(self):
        """In standard host environments without multi-agent IPC, all capabilities default safely to False."""
        empty_env = {}
        caps = detect_capabilities(env=empty_env)
        self.assertFalse(caps.supports_subagents)
        self.assertFalse(caps.supports_task_delegation)
        self.assertFalse(caps.supports_parallel_execution)
        self.assertFalse(caps.supports_shared_artifacts)
        self.assertFalse(caps.supports_interagent_messaging)
        self.assertFalse(caps.is_multi_agent_capable())
        self.assertEqual(caps.detection_source, "environment_scan")

    def test_no_inference_from_model_or_platform_names(self):
        """Does not infer multi-agent capabilities merely from model names or OS."""
        env = {
            "MODEL_NAME": "claude-3-5-sonnet",
            "AGENT_TYPE": "subagent-swarm",
            "PLATFORM": "linux"
        }
        caps = detect_capabilities(env=env)
        self.assertFalse(caps.is_multi_agent_capable())

    def test_explicit_env_flags_enable_capabilities(self):
        env = {
            "ATLAS_HOST_SUPPORTS_SUBAGENTS": "1",
            "ATLAS_HOST_SUPPORTS_PARALLEL": "true",
            "ATLAS_HOST_SUPPORTS_SHARED_ARTIFACTS": "yes"
        }
        caps = detect_capabilities(env=env)
        self.assertTrue(caps.supports_subagents)
        self.assertTrue(caps.supports_task_delegation)  # Auto-enabled when subagents is True
        self.assertTrue(caps.supports_parallel_execution)
        self.assertTrue(caps.supports_shared_artifacts)
        self.assertTrue(caps.is_multi_agent_capable())

    def test_unknown_capability_values_default_safely(self):
        config = {
            "supports_subagents": False,
            "supports_telepathy": True,  # Unknown custom capability
            "supports_quantum_entanglement": "yes"  # Non-bool
        }
        caps = detect_capabilities(config=config)
        self.assertFalse(caps.is_multi_agent_capable())
        # Boolean unknown is preserved in custom_capabilities
        self.assertTrue(caps.custom_capabilities.get("supports_telepathy"))
        # Non-boolean is discarded or defaulted
        self.assertNotIn("supports_quantum_entanglement", caps.custom_capabilities)

    def test_explicit_override_via_dict_and_json_string(self):
        # Override via dict
        override_dict = {
            "supports_subagents": True,
            "supports_task_delegation": True,
            "supports_parallel_execution": False
        }
        caps = detect_capabilities(override=override_dict)
        self.assertTrue(caps.supports_subagents)
        self.assertTrue(caps.supports_task_delegation)
        self.assertFalse(caps.supports_parallel_execution)
        self.assertEqual(caps.detection_source, "explicit_override")

        # Override via JSON string
        json_override = json.dumps({"supports_subagents": True, "supports_task_delegation": True})
        caps_str = detect_capabilities(override=json_override)
        self.assertTrue(caps_str.is_multi_agent_capable())

    def test_invalid_override_handles_gracefully(self):
        # Malformed JSON string
        caps = detect_capabilities(override="INVALID_JSON{{{{")
        # Falls through safely to environment scan
        self.assertFalse(caps.is_multi_agent_capable())

    def test_to_dict_serialization(self):
        caps = HostCapabilities(
            supports_subagents=True,
            supports_task_delegation=True,
            custom_capabilities={"feature_x": True}
        )
        d = caps.to_dict()
        self.assertIn("supports_subagents", d)
        self.assertTrue(d["is_multi_agent_capable"])
        self.assertEqual(d["custom_capabilities"], {"feature_x": True})


if __name__ == "__main__":
    unittest.main()

