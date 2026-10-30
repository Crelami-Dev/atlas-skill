"""Atlas-Skill Runtime Engine Package.

Provides the composition engine, scoring heuristic, asset boundary,
canonical library loader, website generator, and browser visual QA harness.
"""
from .assets import (
    AssetRequirement,
    AssetResolver,
    BaseImageProvider,
    TIER_1_NATIVE,
    TIER_2_ARCHIVE,
    TIER_3_CSS_SVG,
)
from .browser_qa import BrowserQAHarness, find_browser_executable
from .capabilities import HostCapabilities, detect_capabilities
from .composer import compose_design_plan
from .contracts import (
    ContractValidationError,
    Diagnostic,
    LIBRARY_VERSION,
    ProductBrief,
    RUNTIME_VERSION,
    compute_plan_id,
    normalize_brief,
)
from .adapters import (
    AgentAdapter,
    LiveHostAdapter,
    NullAgentAdapter,
    SimulatedAgentAdapter,
)
from .orchestration_contracts import (
    ExecutionMode,
    MAX_REVISION_CYCLES,
    OrchestrationValidationError,
    QAVerdict,
    Role,
    TaskDefinition,
    TaskResult,
    TaskStatus,
)
from .orchestrator import AtlasOrchestrator
from .generator import generate_website, render_css, render_html, render_js
from .image_pipeline import (
    ImageGenerationRequest,
    ImageProvider,
    MockImageProvider,
    discover_image_provider,
    execute_asset_pipeline,
)
from .loader import CanonicalLibrary, default_data_dir, freeze_deep, load_library
from .retriever import (
    is_pattern_eligible,
    retrieve_candidates_for_slot,
    retrieve_design_references,
    retrieve_motion_candidates,
)
from .scorer import (
    score_app_shell,
    score_art_direction,
    score_composition,
    score_motion,
    score_palette,
    score_typography,
)
from .anti_slop import AntiSlopFinding, audit_website_content
from .motion_adapter import (
    generate_motion_runtime_script,
    load_motion_patterns,
    plan_motion_for_brief,
    validate_motion_pattern,
)

__version__ = RUNTIME_VERSION

__all__ = [
    "RUNTIME_VERSION",
    "LIBRARY_VERSION",
    "ProductBrief",
    "Diagnostic",
    "ContractValidationError",
    "normalize_brief",
    "compute_plan_id",
    "CanonicalLibrary",
    "load_library",
    "freeze_deep",
    "default_data_dir",
    "is_pattern_eligible",
    "retrieve_candidates_for_slot",
    "score_art_direction",
    "score_composition",
    "score_palette",
    "score_typography",
    "score_app_shell",
    "AssetRequirement",
    "AssetResolver",
    "BaseImageProvider",
    "TIER_1_NATIVE",
    "TIER_2_ARCHIVE",
    "TIER_3_CSS_SVG",
    "compose_design_plan",
    "generate_website",
    "render_html",
    "render_css",
    "render_js",
    "ImageGenerationRequest",
    "ImageProvider",
    "MockImageProvider",
    "discover_image_provider",
    "execute_asset_pipeline",
    "BrowserQAHarness",
    "find_browser_executable",
    "HostCapabilities",
    "detect_capabilities",
    "AgentAdapter",
    "NullAgentAdapter",
    "SimulatedAgentAdapter",
    "LiveHostAdapter",
    "Role",
    "ExecutionMode",
    "TaskStatus",
    "QAVerdict",
    "TaskDefinition",
    "TaskResult",
    "MAX_REVISION_CYCLES",
    "OrchestrationValidationError",
    "AtlasOrchestrator",
]
