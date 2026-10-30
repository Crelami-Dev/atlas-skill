#!/usr/bin/env python3
"""Atlas Runtime Engine — Command-Line Interface.

Exposes the composition engine and canonical library through a clean,
deterministic command-line interface. Emits pure JSON to stdout and diagnostics to stderr.
Zero-dependency, Python 3.9+ standard library.

Usage:
  py -m runtime.cli --brief brief.json
  py -m runtime.cli --category saas --tones bold,editorial --density high
  py -m runtime.cli --validate-only
"""
import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional

# Add parent directory to sys.path to allow module execution
PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from runtime.adapters import LiveHostAdapter, NullAgentAdapter, SimulatedAgentAdapter
from runtime.browser_qa import BrowserQAHarness
from runtime.capabilities import detect_capabilities
from runtime.composer import compose_design_plan
from runtime.contracts import (
    ContractValidationError,
    Diagnostic,
    LIBRARY_VERSION,
    RUNTIME_VERSION,
    normalize_brief,
)
from runtime.generator import generate_website
from runtime.loader import load_library
from runtime.orchestrator import AtlasOrchestrator


def print_summary(plan: Dict[str, Any], file=sys.stdout):
    """Print human-readable text summary of a design plan."""
    print("=" * 70, file=file)
    print(f" ATLAS DESIGN PLAN — {plan['plan_id']}", file=file)
    print(f" Runtime: v{plan['runtime_version']} | Library: v{plan['library_version']}", file=file)
    print("=" * 70, file=file)

    ad = plan["art_direction"]
    print(f"\n[MACRO ART DIRECTION]\n  ID:    {ad['id']}\n  Name:  {ad['name']}\n  Score: {ad['score']:.1f}", file=file)
    print(f"  Idea:  {ad['idea'][:80]}...", file=file)

    comp = plan["composition"]
    print(f"\n[LAYOUT COMPOSITION SLOTS] (Total Score: {comp['total_score']:.2f})", file=file)
    for s in comp["slots"]:
        print(f"  • {s['slot']:<14} -> {s['pattern_id']:<38} (score: {s['score']:.2f})", file=file)
        if s["rationale"]:
            print(f"    Rationale: {'; '.join(s['rationale'][:2])}", file=file)

    if comp["skipped_slots"]:
        print("\n[SKIPPED SLOTS]", file=file)
        for sk in comp["skipped_slots"]:
            print(f"  • {sk['slot']}: {sk['reason']}", file=file)

    pal = plan["palette"]
    print(f"\n[SEMANTIC PALETTE]\n  ID:    {pal['id']}\n  Name:  {pal['name']}", file=file)
    tok = pal["tokens"]
    print(f"  Tokens: bg={tok['bg']} | surface={tok['surface']} | ink={tok['ink']} | accent={tok['accent']}", file=file)

    typo = plan["typography"]
    print(f"\n[TYPOGRAPHY SYSTEM]\n  ID:    {typo['id']}\n  Name:  {typo['name']}\n  Class: {typo['type_class']}", file=file)
    print(f"  Fonts: Display='{typo['fonts']['display']}' | Text='{typo['fonts']['text']}'", file=file)

    if plan.get("app_shell"):
        sh = plan["app_shell"]
        print(f"\n[APP SHELL]\n  ID:    {sh['id']}\n  Name:  {sh['name']}", file=file)

    assets = plan["assets"]
    print(f"\n[VISUAL ASSET BOUNDARY]\n  Summary: {assets['summary']}", file=file)
    for req in assets["requirements"]:
        print(f"  • {req['asset_id']} ({req['aspect_ratio']}) -> {req['resolution_tier']} [{req['status']}]", file=file)

    if plan.get("warnings"):
        print("\n[WARNINGS]", file=file)
        for w in plan["warnings"]:
            print(f"  ! {w}", file=file)
    print("=" * 70, file=file)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="atlas",
        description="Atlas-Skill Runtime Engine — Deterministic, explainable design planning from canonical libraries.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--brief", "-b", help="Path to input product brief JSON file.")
    parser.add_argument("--category", "-c", help="Product category/industry (e.g. saas, fintech, dev-tool).")
    parser.add_argument("--page-type", choices=["marketing", "editorial", "app"], default="marketing",
                        help="Page archetype: marketing (default), editorial, or app.")
    parser.add_argument("--tones", "-t", help="Comma-separated brand tones (e.g. bold, editorial, minimal).")
    parser.add_argument("--goals", "-g", help="Comma-separated conversion goals (e.g. lead-generation, sign-up).")
    parser.add_argument("--density", "-d", choices=["low", "med", "high"], default="med",
                        help="Content density: low, med (default), or high.")
    parser.add_argument("--assets", "-a", help="Comma-separated available asset types (e.g. photo, product_ui).")
    parser.add_argument("--slots", "-s", help="Comma-separated custom slot sequence.")
    parser.add_argument("--exclude", "-x", help="Comma-separated pattern IDs to exclude.")
    parser.add_argument("--conventional", action="store_true", help="Penalize unconventional layouts.")
    parser.add_argument("--library", "-l", help="Path to custom canonical data directory.")
    parser.add_argument("--output", "-o", help="File path to write generated DesignPlan JSON.")
    parser.add_argument("--build", "-B", help="Output directory to generate complete, runnable website files.")
    parser.add_argument("--qa", action="store_true", help="Execute headless browser visual QA and capture screenshots.")
    parser.add_argument("--shots-dir", help="Custom directory path to save visual QA screenshots.")
    parser.add_argument("--mock-images", action="store_true", help="Use deterministic mock image provider for testing.")
    parser.add_argument("--format", choices=["json", "summary"], default="json",
                        help="Output format: json (default) or human-readable summary.")
    parser.add_argument("--validate-only", action="store_true", help="Validate library and inputs only, then exit.")
    parser.add_argument("--capabilities", action="store_true", help="Inspect detected host execution capabilities and exit.")
    parser.add_argument("--orchestrate", action="store_true", help="Execute via adaptive multi-role orchestrator.")
    parser.add_argument("--mode", choices=["auto", "single", "multi"], default="auto",
                        help="Orchestration mode: auto (default), single, or multi.")
    parser.add_argument("--adapter", choices=["none", "simulated", "live"], default="none",
                        help="Multi-agent adapter: none (default), simulated (test harness), or live.")
    parser.add_argument("--force-multi", action="store_true",
                        help="Strictly enforce multi-agent execution; fail if unsupported rather than falling back.")
    parser.add_argument("--max-revisions", type=int, default=3,
                        help="Maximum revision cycles permitted for QA critique (default: 3).")
    parser.add_argument("--version", "-v", action="version",
                        version=f"Atlas Runtime v{RUNTIME_VERSION} (Library v{LIBRARY_VERSION})")

    args = parser.parse_args(argv)

    # Fast-path for capability inspection
    if args.capabilities:
        caps = detect_capabilities()
        print(json.dumps(caps.to_dict(), indent=2))
        return 0

    # 1. Load Library
    try:
        lib = load_library(data_dir=args.library, validate=args.validate_only)
    except ContractValidationError as e:
        print(f"[FATAL] Library loading error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"[FATAL] Unexpected error loading library: {e}", file=sys.stderr)
        return 2

    if args.validate_only and not args.brief:
        print(f"[OK] Library v{lib.version} validated successfully ({lib.total_records} records).", file=sys.stderr)
        return 0

    # 2. Build Raw Brief Dictionary
    raw_brief: Dict[str, Any] = {}
    if args.brief:
        if not os.path.isfile(args.brief):
            print(f"[ERROR] Brief file not found: '{args.brief}'", file=sys.stderr)
            return 1
        try:
            with open(args.brief, "r", encoding="utf-8") as f:
                raw_brief = json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to read brief JSON: {e}", file=sys.stderr)
            return 1

    # CLI arguments override or supply fields
    if args.category:
        raw_brief["category"] = args.category
    if args.page_type:
        raw_brief["page_type"] = args.page_type
    if args.tones:
        raw_brief["tones"] = args.tones
    if args.goals:
        raw_brief["goals"] = args.goals
    if args.density:
        raw_brief["density"] = args.density
    if args.assets:
        raw_brief["assets"] = args.assets
    if args.slots:
        raw_brief["slots"] = args.slots
    if args.exclude:
        raw_brief["exclude"] = args.exclude
    if args.conventional:
        raw_brief["prefer_conventional"] = True

    # 3. Normalize Brief
    diagnostics: List[Diagnostic] = []
    try:
        brief = normalize_brief(raw_brief, diagnostics=diagnostics)
    except ContractValidationError as e:
        print(f"[ERROR] Brief validation failed: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[ERROR] Unexpected validation error: {e}", file=sys.stderr)
        return 1

    if args.validate_only:
        print(f"[OK] Brief and Library v{lib.version} validated successfully.", file=sys.stderr)
        return 0

    # 4. Adaptive Orchestrator Execution (if --orchestrate requested)
    if args.orchestrate:
        if args.adapter == "simulated":
            adapter = SimulatedAgentAdapter()
            caps = detect_capabilities(override={
                "supports_subagents": True,
                "supports_task_delegation": True,
                "supports_parallel_execution": True,
                "supports_shared_artifacts": True,
                "supports_interagent_messaging": True
            })
        elif args.adapter == "live":
            adapter = LiveHostAdapter()
            caps = None
        else:
            adapter = NullAgentAdapter()
            caps = None

        orchestrator = AtlasOrchestrator(
            library=lib,
            adapter=adapter,
            capabilities=caps,
            max_revisions=args.max_revisions
        )
        orch_res = orchestrator.execute(
            brief=brief,
            mode=args.mode,
            build_dir=args.build,
            run_qa=args.qa,
            force_multi=args.force_multi
        )

        if args.output:
            try:
                with open(args.output, "w", encoding="utf-8") as f:
                    json.dump(orch_res, f, indent=2, ensure_ascii=False)
                print(f"[INFO] Orchestration result written to {args.output}", file=sys.stderr)
            except Exception as e:
                print(f"[ERROR] Failed to write orchestration result to {args.output}: {e}", file=sys.stderr)
                return 2

        print(json.dumps(orch_res, indent=2, ensure_ascii=False))
        return 0 if orch_res.get("final_verdict") in ("PASS", "WARN") and orch_res.get("execution_mode") != "FAILED" else 1

    # 5. Direct Compose Plan (Legacy/Direct mode)
    try:
        plan = compose_design_plan(brief, lib, diagnostics=diagnostics)
    except ContractValidationError as e:
        print(f"[ERROR] Composition failed: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[FATAL] Composition engine error: {e}", file=sys.stderr)
        return 2

    # 5. Output Design Plan JSON
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(plan, f, indent=2, ensure_ascii=False)
            print(f"[INFO] Design plan written to {args.output}", file=sys.stderr)
        except Exception as e:
            print(f"[ERROR] Failed to write plan to {args.output}: {e}", file=sys.stderr)
            return 2

    # 6. Generate Website Files (if --build requested)
    if args.build:
        try:
            gen_res = generate_website(plan, args.build, prefer_mock_images=args.mock_images)
            print(f"[OK] Website generated in '{gen_res['output_dir']}' ({len(gen_res['files'])} core files, {gen_res['assets_generated']} assets).", file=sys.stderr)
            print(f"[INFO] Run locally via: {gen_res['run_instructions']}", file=sys.stderr)
        except Exception as e:
            print(f"[FATAL] Website generation failed: {e}", file=sys.stderr)
            return 2

        # 7. Run Browser Visual QA (if --qa requested)
        if args.qa:
            try:
                qa_harness = BrowserQAHarness()
                if not qa_harness.is_available():
                    print("[WARN] Headless browser not found on host; skipping browser screenshots.", file=sys.stderr)
                else:
                    qa_res = qa_harness.run_visual_qa(args.build, args.shots_dir)
                    print(f"[OK] Browser Visual QA completed with status '{qa_res['status']}' using {qa_res['browser_used']}.", file=sys.stderr)
                    for vp in qa_res["viewports"]:
                        print(f"  • {vp['label']}: {vp['status']} ({vp['screenshot_bytes']} bytes) -> {vp.get('screenshot_path')}", file=sys.stderr)
            except Exception as e:
                print(f"[WARN] Visual QA execution error: {e}", file=sys.stderr)

    if args.format == "summary":
        print_summary(plan, file=sys.stdout)
    else:
        json_output = json.dumps(plan, indent=2, ensure_ascii=False)
        print(json_output)

    return 0


if __name__ == "__main__":
    sys.exit(main())

