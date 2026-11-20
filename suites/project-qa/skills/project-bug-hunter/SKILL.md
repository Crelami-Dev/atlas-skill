---
name: project-bug-hunter
description: "Audits software projects in strict read-only mode to find functional bugs, logic flaws, async race conditions, UI layout defects, and build/test failures. Pre-analyzes root causes and blast radius, and delivers a Markdown (.md) bug report while waiting for user approval. Use when asked to find bugs, check project errors, or audit feature quality; never use to modify code without explicit approval."
---

# Project Bug Hunter — Read-Only Bug & UI Defect Discovery

Systematically discover functional defects, logic errors, unhandled edge cases, async race conditions, and UI layout issues across a codebase while keeping all project source files strictly read-only until the user explicitly commands remediation.

## Decision Tree

- **User asks to find/check bugs ONLY** (`find bugs`, `check errors`, `audit bugs`): Execute Steps 1 through 6 below in strictly read-only mode, write `BUG-AUDIT-REPORT.md`, and stop to wait for user instruction.
- **User asks to check BOTH bugs AND security vulnerabilities** (`find bugs and security vulnerabilities`, `full project audit`): Run both `project-bug-hunter` and `project-security-auditor`, combine all findings into one unified `PROJECT-AUDIT-REPORT.md`, and wait for user approval before touching project files.
- **User explicitly commands to FIX issues** (`fix it`, `apply fixes`, `fix all`): Do not stop at reporting; immediately load and execute `project-fix-and-verify`.

## Path Resolution

Resolve `<SKILL_DIR>` as the directory containing this `SKILL.md` file (e.g., `<workspace>/.agents/skills/project-bug-hunter`, `~/.gemini/config/skills/project-bug-hunter`, or `suites/project-qa/skills/project-bug-hunter`). Use `python3` on macOS/Linux or `python` on Windows.

## Execution Protocol

### Step 1: Enforce the Read-Only Discovery Gate

Do not edit, format, or patch any project file during discovery. Premature edits obscure root causes and violate user control. Store any temporary outputs or screenshots outside the project source tree (e.g., `/tmp/bug_probe_shots`).

### Step 2: Map Full Project Architecture and 100% Feature Inventory

1. Run [project_inventory.py](scripts/project_inventory.py) to map routes, UI views, state stores, API handlers, database models, and test files:
   ```bash
   python3 "<SKILL_DIR>/scripts/project_inventory.py" "<workspace_root>"
   ```
2. Inspect manifests, entry points, routers, controllers, UI pages/components, state stores, background workers, and database schemas to compile a **complete inventory of all project features**.

### Step 3: Run Non-Mutating Diagnostics and Deep Logic Tracing

1. Run existing typecheckers, linters, compilers, and test suites in read-only mode (e.g., `tsc --noEmit`, `npm test -- --watchAll=false`, `pytest`, `go vet ./...`, `cargo check`) when available.
2. Walk through [bug-hunting-checklist.md](references/bug-hunting-checklist.md) and trace end-to-end data flows across UI -> API -> business logic -> database -> response:
   - Null/undefined/None dereferences, empty arrays, zero/negative numbers, NaN, and pagination off-by-one bugs.
   - Async race conditions, missing `await`, stale closures, double-submit states, and uncleaned listeners/connections.
   - Frontend-backend payload/type mismatches (`camelCase` vs `snake_case`, HTTP status handling, missing error states).
   - Partial database writes lacking transactions and swallowed exceptions (`catch {}` / `except: pass`).

### Step 4: Visual UI Bug Probe with Screenshots (Web UI Projects)

1. Run [ui_visual_bug_probe.py](scripts/ui_visual_bug_probe.py) at Desktop (`1440x900`) and Mobile (`375x667`, `320x568`):
   ```bash
   python3 "<SKILL_DIR>/scripts/ui_visual_bug_probe.py" "<html-or-local-url>" --out-dir /tmp/bug_probe_shots
   ```
2. Inspect the generated PNG screenshots with your image/file viewer because code inspection alone misses clipped columns, sticky headers overlapping content, or mobile grid overflows.

### Step 5: Pre-Analyze Exact Fixes and Cross-Feature Blast Radius

Prepare full remediation readiness during discovery in case the user tells you to fix the bugs right after reading the report:
- Identify the true root cause of each bug (`file:line`, function, guard condition, and data flow adjustment).
- Map the **blast radius**: list every caller, sibling feature, shared component, API contract, or database table that depends on the affected code so future fixes will not introduce regressions.

### Step 6: Generate the Markdown Report and Wait for User Command

1. Follow [bug-report-template.md](assets/bug-report-template.md) and create `BUG-AUDIT-REPORT.md` (or `PROJECT-AUDIT-REPORT.md` when merged with `project-security-auditor`) in the workspace root, matching the user's language.
2. Include severity (`Critical`, `High`, `Medium`, `Low`), exact `file:line` references, concrete reproduction scenarios, step-by-step remediation instructions, and pre-analyzed blast-radius notes.
3. Present the report path clearly to the user and **stop and wait** for explicit instructions before running `project-fix-and-verify`.
