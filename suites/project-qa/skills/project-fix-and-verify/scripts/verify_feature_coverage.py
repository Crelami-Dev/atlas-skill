#!/usr/bin/env python3
'''Post-fix diff hygiene and route/test inventory verifier.'''

import argparse
import json
import os
import re
import subprocess
import sys

LEFTOVER_PATTERNS = [
    ("debug_print", re.compile(r"\b(console\.debug|debugger;|pdb\.set_trace\(\)|breakpoint\(\))")),
    ("todo_temp", re.compile(r"\b(FIXME|TEMP_BYPASS|HACK|TODO:\s*remove)\b", re.IGNORECASE)),
    ("disabled_security", re.compile(r"\b(verify\s*=\s*False|NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*['\"]?0|InsecureSkipVerify\s*:\s*true)\b")),
]


def check_git_diff(root_path: str) -> dict:
    try:
        status_out = subprocess.check_output(
            ["git", "-C", root_path, "status", "--porcelain"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        diff_out = subprocess.check_output(
            ["git", "-C", root_path, "diff", "--unified=0"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except Exception:
        return {"git_available": False, "modified_files": [], "diff_warnings": []}

    modified_files = [line[3:].strip() for line in status_out.splitlines() if len(line) > 3]
    warnings = []
    current_file = ""
    for line in diff_out.splitlines():
        if line.startswith("+++ b/"):
            current_file = line[6:]
        elif line.startswith("+") and not line.startswith("+++"):
            added = line[1:]
            for kind, pat in LEFTOVER_PATTERNS:
                if pat.search(added):
                    warnings.append({
                        "type": kind,
                        "file": current_file,
                        "added_line": added.strip()[:140],
                    })

    return {
        "git_available": True,
        "modified_files_count": len(modified_files),
        "modified_files": modified_files[:200],
        "diff_warnings_count": len(warnings),
        "diff_warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect modified files and git diff after remediation to catch leftover debug statements, temporary bypasses, or unverified edits."
    )
    parser.add_argument("project_dir", nargs="?", default=".", help="Path to target project root (default: current directory)")
    args = parser.parse_args()

    if not os.path.isdir(args.project_dir):
        print(json.dumps({"error": f"Directory not found: {args.project_dir}"}), file=sys.stderr)
        return 1

    result = {
        "project_root": os.path.abspath(args.project_dir),
        "post_fix_hygiene": check_git_diff(args.project_dir),
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
