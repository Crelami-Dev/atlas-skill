#!/usr/bin/env python3
'''Zero-dependency static security sink and secret exposure scanner.'''

import argparse
import json
import os
import re
import sys

IGNORE_DIRS = {
    ".git", ".agents", ".agent", "node_modules", "venv", ".venv", "env",
    "__pycache__", "dist", "build", ".next", ".nuxt", "coverage", "target", "vendor"
}

TEXT_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".kt",
    ".php", ".rb", ".cs", ".sql", ".sh", ".yaml", ".yml", ".json",
    ".toml", ".ini", ".conf", ".env", ".html", ".vue", ".svelte"
}

RULES = [
    ("CRITICAL", "Hardcoded Private Key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("CRITICAL", "AWS Access Key Pattern", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("CRITICAL", "Google API Key Pattern", re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b")),
    ("HIGH", "Hardcoded Secret Assignment", re.compile(r"(?i)\b(api[_-]?key|secret[_-]?key|jwt[_-]?secret|access[_-]?token|private[_-]?key|db[_-]?password|password)\s*[:=]\s*['\"][^'\"$\s]{8,}['\"]")),
    ("HIGH", "SQL String Interpolation Candidate", re.compile(r"(?i)(\bf['\"][^'\"]*\b(?:SELECT|INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM)\b[^'\"]*\{[A-Za-z_]|\b(?:SELECT|INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM)\b.*(?:\+\s*\w+|\$\{|%[sd]|\.format\())")),
    ("HIGH", "Dynamic Code Execution (eval/exec/Function)", re.compile(r"\b(eval|exec|Function)\s*\(")),
    ("HIGH", "Shell Command Execution Sink", re.compile(r"\b(os\.system|child_process\.exec|child_process\.execSync|shell_exec|passthru)\s*\(|subprocess\.\w+\([^)]*shell\s*=\s*True")),
    ("HIGH", "Unsafe Deserialization Sink", re.compile(r"\b(pickle\.loads?|yaml\.load\s*\([^)]*(?!SafeLoader)|unserialize\s*\()")),
    ("MEDIUM", "DOM XSS Sink (innerHTML / dangerouslySetInnerHTML)", re.compile(r"\b(dangerouslySetInnerHTML|\.innerHTML\s*=|v-html\s*=|document\.write\s*\()")),
    ("MEDIUM", "Permissive Wildcard CORS", re.compile(r"(?i)(Access-Control-Allow-Origin['\"\s:,]+['\"]\*['\"]|cors\(\s*\{?\s*origin\s*:\s*['\"]\*['\"])")),
    ("MEDIUM", "Disabled TLS Verification", re.compile(r"\b(verify\s*=\s*False|NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*['\"]?0|InsecureSkipVerify\s*:\s*true)\b")),
    ("MEDIUM", "Weak Crypto/Password Hash (MD5/SHA1)", re.compile(r"\b(hashlib\.(?:md5|sha1)|crypto\.createHash\(\s*['\"](?:md5|sha1)['\"]|md5\s*\(|sha1\s*\()")),
]


def redact_line(line: str) -> str:
    trimmed = line.strip()[:160]
    return re.sub(
        r"(['\"])([A-Za-z0-9_\-\/+=]{4})[A-Za-z0-9_\-\/+=]{6,}([A-Za-z0-9_\-\/+=]{3})(['\"])",
        r"\1\2****\3\4",
        trimmed,
    )


def scan_security(root_path: str, max_findings: int = 300) -> dict:
    findings = []
    env_files = []
    gitignore_path = os.path.join(root_path, ".gitignore")
    gitignore_has_env = False

    if os.path.isfile(gitignore_path):
        try:
            with open(gitignore_path, "r", encoding="utf-8", errors="ignore") as gf:
                content = gf.read()
                gitignore_has_env = bool(re.search(r"(?m)^\s*\.env(\*|\..+)?\s*$", content))
        except OSError:
            pass

    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for fname in filenames:
            rel_path = os.path.relpath(os.path.join(dirpath, fname), root_path).replace("\\", "/")
            _, ext = os.path.splitext(fname)

            if fname == ".env" or (fname.startswith(".env.") and not fname.endswith((".example", ".sample", ".template"))):
                env_files.append(rel_path)

            if ext.lower() not in TEXT_EXTENSIONS and not fname.startswith(".env"):
                continue

            full_path = os.path.join(dirpath, fname)
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    for lineno, line in enumerate(f, start=1):
                        for severity, label, pattern in RULES:
                            if pattern.search(line) and len(findings) < max_findings:
                                findings.append({
                                    "severity_hint": severity,
                                    "rule": label,
                                    "location": f"{rel_path}:{lineno}",
                                    "redacted_snippet": redact_line(line),
                                    "verification_required": "Trace input source to sink and check middleware/sanitizers before confirming.",
                                })
            except OSError:
                continue

    return {
        "project_root": os.path.abspath(root_path),
        "env_files_present": env_files,
        "gitignore_protects_env": gitignore_has_env,
        "candidate_findings_count": len(findings),
        "candidate_findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scan a project directory for hardcoded secret patterns, exposed .env files, and dangerous security sinks."
    )
    parser.add_argument("project_dir", nargs="?", default=".", help="Path to target project root (default: current directory)")
    parser.add_argument("--max-findings", type=int, default=300, help="Maximum candidate findings to output")
    args = parser.parse_args()

    if not os.path.isdir(args.project_dir):
        print(json.dumps({"error": f"Directory not found: {args.project_dir}"}), file=sys.stderr)
        return 1

    print(json.dumps(scan_security(args.project_dir, max_findings=args.max_findings), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
