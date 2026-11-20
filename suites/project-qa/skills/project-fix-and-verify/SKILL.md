---
name: project-fix-and-verify
description: "Executes user-approved bug fixes and security patches, actively tests 100% of all project features (never partial testing), runs visual screenshot regression, and performs a full post-fix bug and security re-audit until zero issues remain. Use ONLY when the user explicitly commands to fix, repair, or patch issues; never use for read-only audit requests."
---

# Project Fix and Verify — Remediation, 100% Feature Testing & Full Re-Audit

Implement user-approved bug and security fixes cleanly at the root cause, test **every single feature** across the entire project (never only the modified files), verify UI layout with screenshots, and execute a complete post-fix bug + security re-audit before signing off.

## Decision Tree

- **User ONLY asked to search/audit/check issues**: Stop immediately! Do NOT modify any project file. Load `project-bug-hunter` and/or `project-security-auditor` instead.
- **User EXPLICITLY instructed to fix issues** (`fix it`, `apply fixes`, `fix according to report`, `fix all`): Proceed through Steps 1 to 5 below without skipping any verification gate.

## Path Resolution

Resolve `<SKILL_DIR>` as the directory containing this `SKILL.md` file (e.g., `<workspace>/.agents/skills/project-fix-and-verify`, `~/.gemini/config/skills/project-fix-and-verify`, or `suites/project-qa/skills/project-fix-and-verify`). Sibling skills (`project-bug-hunter` and `project-security-auditor`) reside in the parent `skills/` directory when installed together.

## Execution Protocol

### Step 1: Build the Remediation Plan & 100% Project Feature Matrix

Read [verification-protocol.md](references/verification-protocol.md) and construct two explicit checklists before editing code:
1. **Remediation Queue**: Every bug and security vulnerability to fix (from the `.md` audit report or current prompt), ordered from Critical/High security and core architecture fixes down to Medium/Low items.
2. **100% Feature Matrix**: Every route, API endpoint, UI page/flow, CLI command, background job, and authentication state in the **entire project**. Never restrict your test plan to touched files.

### Step 2: Apply Surgical Root-Cause Fixes & Regression Tests

- Fix root causes cleanly rather than surface patches: use safe DOM APIs (`textContent`/`createElement` instead of `innerHTML`), parameterized queries, server-side authorization checks, stale async request cancellation, and mobile grid overflow guards (`minmax(0, 1fr)` and `min-width: 0`).
- Upgrade vulnerable dependencies safely when fixing CVE/GHSA findings and verify lockfile consistency.
- Add or update automated unit, integration, and security regression tests covering every patched bug and vulnerability.

### Step 3: Actively Test 100% of Project Features & Visual Regression

Exercise **every feature** in your 100% Feature Matrix, never a partial sample:
1. Run full project compilation, build, typecheck, linter, and automated test suites until 100% pass.
2. Run live runtime verification across all features:
   - **Backend / API / CLI**: Start the local dev/test server or test client and hit **every** endpoint/command with valid inputs, edge-case boundary inputs, and unauthorized/malicious security payloads (confirming proper 400/401/403/422 rejections without 500 crashes).
   - **Web Frontend / Fullstack**: Run production build checks and component/E2E suites; inspect interactive flows (tab navigation, search/filter/reset, form submission, `Escape` dialog dismissal, boundary inputs) via browser verification when available, and run [e2e_visual_regression.py](scripts/e2e_visual_regression.py) at `1440x900` and `375x667`:
     ```bash
     python3 "<SKILL_DIR>/scripts/e2e_visual_regression.py" "<entry-html-or-url>" --out-dir /tmp/postfix_shots
     ```
     Inspect the generated PNG screenshots to confirm fixes did not break layout.
3. If any feature breaks, fix it immediately before moving forward.

### Step 4: Full Post-Fix Re-Audit & Whole-Project End-to-End Re-Test

After all fixes pass feature testing, step back and re-analyze the entire project from scratch to guarantee zero regressions and zero remaining vulnerabilities:
1. Run [verify_feature_coverage.py](scripts/verify_feature_coverage.py):
   ```bash
   python3 "<SKILL_DIR>/scripts/verify_feature_coverage.py" "<workspace_root>"
   ```
2. Re-run `project_inventory.py`, `security_scan.py`, `live_cve_osv_check.py`, and Atlas `run-gates.mjs` (when applicable) and inspect `git diff` / `git status` line-by-line to confirm no leftover debug logs, temporary bypasses, hardcoded test tokens, or new edge-case bugs exist.
3. Execute one final **complete end-to-end test sweep across the entire project** from startup to teardown.
4. **Zero-Defect Loop**: If *any* bug, regression, or security vulnerability is detected during this re-audit, return to Step 2, fix it, and repeat Steps 3 and 4 until 100% clean.

### Step 5: Deliver the Final Verification Report

Generate `FIX-VERIFICATION-REPORT.md` following [verification-report-template.md](assets/verification-report-template.md) in the user's language, documenting every applied patch, the 100% Feature Test Matrix results, and the clean post-fix security and bug re-audit sign-off.
