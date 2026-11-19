#!/usr/bin/env python3
'''Zero-dependency project architecture, route, test, and code-smell scanner.'''

import argparse
import json
import os
import re
import sys
from collections import Counter

IGNORE_DIRS = {
    ".git", ".agents", ".agent", "node_modules", "venv", ".venv", "env",
    "__pycache__", "dist", "build", ".next", ".nuxt", "coverage", "target",
    "vendor", ".idea", ".vscode", ".pytest_cache", ".mypy_cache"
}

CODE_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java",
    ".kt", ".php", ".rb", ".cs", ".cpp", ".c", ".swift", ".vue", ".svelte"
}

MANIFEST_FILES = {
    "package.json": "Node.js / JS / TS",
    "package-lock.json": "npm Lockfile",
    "pnpm-lock.yaml": "pnpm Lockfile",
    "yarn.lock": "Yarn Lockfile",
    "pyproject.toml": "Python (pyproject)",
    "requirements.txt": "Python (requirements)",
    "poetry.lock": "Python (Poetry Lockfile)",
    "go.mod": "Go Modules",
    "Cargo.toml": "Rust (Cargo)",
    "composer.json": "PHP (Composer)",
    "pom.xml": "Java (Maven)",
    "build.gradle": "Java / Kotlin (Gradle)",
}

SMELL_PATTERNS = [
    ("todo_fixme", re.compile(r"\b(TODO|FIXME|HACK|BUG|XXX)\b"), "Unresolved marker"),
    ("empty_except_py", re.compile(r"except\s*(?:Exception|BaseException)?\s*:\s*pass\b"), "Swallowed Python exception"),
    ("bare_except_py", re.compile(r"^\s*except\s*:\s*$"), "Bare Python except clause"),
    ("empty_catch_js", re.compile(r"catch\s*\([^)]*\)\s*\{\s*\}"), "Empty JS/TS catch block"),
    ("debugger_stmt", re.compile(r"^\s*(debugger;|import\s+pdb|pdb\.set_trace\(\)|breakpoint\(\))"), "Leftover debugger statement"),
]

ROUTE_PATTERNS = [
    re.compile(r"@(?:app|router|bp)\.(?:get|post|put|patch|delete|route)\(\s*['\"]([^'\"]+)['\"]"),
    re.compile(r"(?<!@)\b(?:app|router)\.(?:get|post|put|patch|delete|use)\(\s*['\"]([^'\"]+)['\"]"),
    re.compile(r"Route::(?:get|post|put|patch|delete|any)\(\s*['\"]([^'\"]+)['\"]"),
]


def scan_project(root_path: str, max_items: int = 250) -> dict:
    ext_counts = Counter()
    manifests = []
    test_files = []
    routes = []
    nextjs_pages = []
    smells = []
    total_files = 0

    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for fname in filenames:
            total_files += 1
            rel_path = os.path.relpath(os.path.join(dirpath, fname), root_path).replace("\\", "/")
            _, ext = os.path.splitext(fname)

            if fname in MANIFEST_FILES:
                manifests.append({"file": rel_path, "type": MANIFEST_FILES[fname]})

            if re.search(r"(^|/)(app|pages)/.+/(page|route)\.(tsx|ts|jsx|js)$", rel_path):
                nextjs_pages.append(rel_path)

            if ext.lower() in CODE_EXTENSIONS:
                ext_counts[ext.lower()] += 1
                low_name = fname.lower()
                if (
                    "test" in low_name
                    or "spec" in low_name
                    or "/tests/" in f"/{rel_path.lower()}/"
                    or "/__tests__/" in f"/{rel_path.lower()}/"
                ):
                    test_files.append(rel_path)

                full_path = os.path.join(dirpath, fname)
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        for lineno, line in enumerate(f, start=1):
                            for kind, pat, label in SMELL_PATTERNS:
                                if pat.search(line) and len(smells) < max_items:
                                    smells.append({
                                        "type": kind,
                                        "label": label,
                                        "location": f"{rel_path}:{lineno}",
                                        "snippet": line.strip()[:140],
                                    })
                            for rpat in ROUTE_PATTERNS:
                                m = rpat.search(line)
                                if m and len(routes) < max_items:
                                    routes.append({
                                        "route": m.group(1),
                                        "location": f"{rel_path}:{lineno}",
                                    })
                                    break
                except OSError:
                    continue

    return {
        "project_root": os.path.abspath(root_path),
        "total_scanned_files": total_files,
        "detected_manifests": manifests,
        "code_files_by_extension": dict(ext_counts.most_common()),
        "test_files_count": len(test_files),
        "test_files": test_files[:max_items],
        "detected_api_routes": routes,
        "detected_file_routes": nextjs_pages[:max_items],
        "code_smells_count": len(smells),
        "code_smells": smells,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scan a project directory to inventory stacks, routes, test files, and code-quality smells (read-only)."
    )
    parser.add_argument("project_dir", nargs="?", default=".", help="Path to the target project root (default: current directory)")
    parser.add_argument("--max-items", type=int, default=250, help="Maximum routes/smells to emit in JSON output")
    args = parser.parse_args()

    if not os.path.isdir(args.project_dir):
        print(json.dumps({"error": f"Directory not found: {args.project_dir}"}), file=sys.stderr)
        return 1

    print(json.dumps(scan_project(args.project_dir, max_items=args.max_items), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
