---
trigger: always_on
description: "Enforces strict read-only audit gate (deliver .md report with pre-analyzed fixes before modifying code), live CVE/advisory lookup, and mandatory 100% all-feature testing plus full post-fix re-audit when fixing project issues."
---
# QA, Bug Hunting, and Security Audit Governance Gate

Apply these non-negotiable engineering invariants whenever the user asks to check bugs, audit security vulnerabilities, or repair reported issues in this project:

1. **Strict Read-Only Discovery Gate (Search & Report First)**:
   - When the user asks to find bugs, check errors, or scan security vulnerabilities (`find bugs`, `check errors`, `security audit`, `audit project`, `security check`), **never modify, refactor, or patch any project source or config file**.
   - Activate the `project-bug-hunter` and/or `project-security-auditor` skills.
   - Pre-investigate exact root causes, concrete code-level fixes, and cross-feature blast radius in advance so you are ready if instructed to fix later, then write a standalone Markdown (`.md`) report explaining every issue and how to fix it, and **wait for explicit user approval** before editing project code.

2. **Mandatory Live Security Advisory & Latest CVE Research**:
   - During any security check, never rely solely on static knowledge. Always run `live_cve_osv_check.py` against project manifests/lockfiles **and** search the web for the latest CVEs, GitHub Security Advisories (GHSA), CISA KEV entries, and newly disclosed framework bypasses affecting the detected stack and versions.

3. **Gated Remediation, 100% Feature Testing, and Full Re-Audit**:
   - Modify project code **only** after the user explicitly commands you to fix the issues (`fix it`, `apply fixes`, `patch vulnerabilities`, `fix all`).
   - Activate the `project-fix-and-verify` skill: implement root-cause fixes, actively test **100% of all project features** (never test only changed files or a subset of features), and then re-audit the entire codebase from scratch for both bugs and security vulnerabilities followed by a complete end-to-end regression pass until zero issues remain.
