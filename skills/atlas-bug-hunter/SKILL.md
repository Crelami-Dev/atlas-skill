---
name: atlas-bug-hunter
description: "Use when auditing a project to find functional bugs, UI layout defects, logic/async flaws, OWASP security vulnerabilities, and live CVE/OSV advisories to produce a deep Markdown audit report—or when commanded to fix/repair discovered bugs with 100% all-feature regression testing."
---

# Atlas Bug Hunter & Security Auditor — Deep Discovery Report + Smart Auto-Fix Switch (`v7.0.0`)

Dedicated, high-precision bug hunting, UI layout defect probing, and application security / live-CVE auditing skill (`/atlas-bug-hunter`) featuring a **Smart 2-Mode Decision Switch**:
- **Mode A — Deep Read-Only Discovery & Root-Cause Report (Default):** Hunts down every functional bug, logic error, async race condition, UI/responsive defect, OWASP security flaw, and live CVE/OSV advisory, pre-analyzes the exact root cause (`file:line`) and blast radius, and delivers a comprehensive Markdown report (`PROJECT-AUDIT-REPORT.md` or `BUG-AUDIT-REPORT.md`) while keeping project files strictly untouched.
- **Mode B — Surgical Remediation, 100% Feature Testing & Zero-Defect Re-Audit (Auto-Triggered on Fix Commands):** The moment the user commands to fix, repair, or patch the issues (`"benerin"`, `"perbaiki"`, `"fix it"`, `"patch semua"`, `"tuntaskan bugnya"`)—**even if the user invokes `/atlas-bug-hunter` again**—this skill automatically switches into full remediation mode, executing the complete [project-fix-and-verify](../../suites/project-qa/skills/project-fix-and-verify/SKILL.md) workflow until 0 defects remain.

## Smart 2-Mode Decision Tree (Read First)

| User Intent / Prompt Signal | Active Mode | Required Action |
|---|---|---|
| **Audit / Hunt / Check / Report** (`"cari bug"`, `"cek bug"`, `"audit project"`, `"find bugs"`, `"check security"`, or bare `/atlas-bug-hunter` with no fix command) | **Mode A — Read-Only Deep Hunt & Report** | Keep all project files **100% read-only**. Execute **Steps A1–A6** below, write `PROJECT-AUDIT-REPORT.md` (or `BUG-AUDIT-REPORT.md`), and present the report while waiting for user instruction. |
| **Fix / Repair / Patch / Resolve** (`"benerin"`, `"perbaiki"`, `"fix"`, `"fix all"`, `"patch"`, `"tuntaskan"`, `"benerin bug tadi"` — **including when `/atlas-bug-hunter` is re-invoked with a fix instruction**) | **Mode B — Full Remediation & 100% Feature Verification** | Immediately switch to **Steps B1–B5** ([project-fix-and-verify](../../suites/project-qa/skills/project-fix-and-verify/SKILL.md)). If no audit report exists yet, run a fast discovery pass first, then immediately patch all root causes, test 100% of project features, and re-audit via **Mode A** until 0 bugs/vulnerabilities remain. |

## Path Resolution

Resolve `<ATLAS_ROOT>` as the root of the installed Atlas package ( two levels up from this `skills/atlas-bug-hunter/SKILL.md` file when inside `atlas-skill`, or sibling `../atlas-skill` when installed as `.agents/skills/atlas-bug-hunter`). The QA scripts and references live under `<ATLAS_ROOT>/suites/project-qa/skills/`. Use `python3` on macOS/Linux or `python` on Windows.

---

## Mode A — Deep Read-Only Bug & Security Discovery Protocol

When in **Mode A**, do **NOT** edit, format, or patch any project source file. Store temporary probe outputs in `/tmp/atlas_bug_probe` (or OS temp directory).

### Step A1: Architecture Mapping & 100% Feature Inventory
Run [project_inventory.py](../../suites/project-qa/skills/project-bug-hunter/scripts/project_inventory.py) to catalog every route, UI page/component, state store, API endpoint, background worker, database schema, and test suite:
```bash
python3 "<ATLAS_ROOT>/suites/project-qa/skills/project-bug-hunter/scripts/project_inventory.py" "<workspace_root>"
```

### Step A2: Non-Mutating Diagnostics & End-to-End Logic/Async Tracing
1. Run existing typecheckers, linters, compilers, and test suites in read-only mode (`tsc --noEmit`, `npm test -- --watchAll=false`, `pytest`, `go vet ./...`, `cargo check`).
2. Follow [bug-hunting-checklist.md](../../suites/project-qa/skills/project-bug-hunter/references/bug-hunting-checklist.md) to trace every data path (`UI -> API -> business logic -> DB -> UI`):
   - Null/undefined dereferences, empty state crashes, off-by-one pagination, NaN/currency rounding errors.
   - Async race conditions, missing `await`, stale closures, double-submit states, memory/listener leaks.
   - Frontend-backend contract mismatches (`camelCase` vs `snake_case`, unhandled HTTP `4xx/5xx`, swallowed `catch {}` blocks).

### Step A3: Visual UI & Responsive Bug Probe (Web Projects)
Run [ui_visual_bug_probe.py](../../suites/project-qa/skills/project-bug-hunter/scripts/ui_visual_bug_probe.py) across Desktop (`1440x900`) and Mobile (`375x667`, `320x568`) and also run Atlas static/visual gates (`node <ATLAS_ROOT>/scripts/run-gates.mjs <workspace_root> --mode light`):
```bash
python3 "<ATLAS_ROOT>/suites/project-qa/skills/project-bug-hunter/scripts/ui_visual_bug_probe.py" "<entry-html-or-url>" --out-dir /tmp/atlas_bug_probe
```
Open the generated PNG screenshots with your image viewer (`read_file`) to catch clipped elements, horizontal overflow, broken grids, overlapped sticky headers, or broken images.

### Step A4: Application Security & 3-Layer Live CVE Intelligence
Follow [project-security-auditor](../../suites/project-qa/skills/project-security-auditor/SKILL.md) and [security-audit-checklist.md](../../suites/project-qa/skills/project-security-auditor/references/security-audit-checklist.md):
1. **Static Sink & Secret Scan:**
   ```bash
   python3 "<ATLAS_ROOT>/suites/project-qa/skills/project-security-auditor/scripts/security_scan.py" "<workspace_root>"
   ```
2. **Live OSV.dev, NIST NVD CVE 2.0 & CISA KEV Dependency Scan:**
   ```bash
   python3 "<ATLAS_ROOT>/suites/project-qa/skills/project-security-auditor/scripts/live_cve_osv_check.py" "<workspace_root>" --auto-keywords
   ```
   *(Pass `--offline-parse-only` in air-gapped environments).*
3. **Source-to-Sink & Access Control Verification:** Audit IDOR/BOLA ownership checks, auth/JWT/session flags, CORS/CSRF, XSS (`innerHTML`/`dangerouslySetInnerHTML`), SQL/command injection, and SSRF.

### Step A5: Pre-Analyze Exact Root Causes, Concrete Patches & Blast Radius
For **every** discovered issue, pre-compute before writing the report:
- **Exact Root Cause Location:** `file:line`, offending function/selector, and why the failure occurs.
- **Concrete Code Fix:** The exact replacement logic, guard condition, token rule, or package version upgrade needed.
- **Cross-Feature Blast Radius:** Every caller, sibling component, API route, or database query that touches the affected code so fixing it will cause zero regressions.

### Step A6: Deliver the Structured Audit Report & Wait for Fix Command
Write `PROJECT-AUDIT-REPORT.md` (or `BUG-AUDIT-REPORT.md` / `SECURITY-AUDIT-REPORT.md`) in the workspace root using [bug-report-template.md](../../suites/project-qa/skills/project-bug-hunter/assets/bug-report-template.md) and [security-report-template.md](../../suites/project-qa/skills/project-security-auditor/assets/security-report-template.md). Group findings by severity (`Critical`, `High`, `Medium`, `Low`) with reproduction steps, `file:line` root causes, proposed code diffs, and blast-radius notes. Stop and tell the user they can say **"Fix all issues"** (even while invoking `/atlas-bug-hunter`) to trigger Mode B.

---

## Mode B — Surgical Remediation, 100% Feature Testing & Zero-Defect Re-Audit Loop

When the user commands to fix/repair/patch issues (e.g. `"benerin"`, `"perbaiki"`, `"fix it"`, `"fix according to report"`), execute [project-fix-and-verify](../../suites/project-qa/skills/project-fix-and-verify/SKILL.md) and [verification-protocol.md](../../suites/project-qa/skills/project-fix-and-verify/references/verification-protocol.md) end-to-end:

1. **Step B1 — Remediation Queue & 100% Feature Matrix:** List every bug/vulnerability from `PROJECT-AUDIT-REPORT.md` (or run Steps A1–A4 first if no report exists yet) from `Critical` down to `Low`, plus a **100% Feature Matrix** of every route, UI flow, API endpoint, and state in the project.
2. **Step B2 — Surgical Root-Cause Fixes & Regression Tests:** Patch root causes cleanly (safe DOM APIs, parameterized queries, server-side auth checks, async race guards, `minmax(0, 1fr)` / `min-width: 0` grid locks, WCAG AA contrast tokens) and add automated unit/integration regression tests.
3. **Step B3 — Active 100% All-Feature Testing & Visual Screenshot Regression:**
   - Run full build, typecheck, linter, and automated test suites until 100% pass.
   - Actively exercise **every** feature in the 100% Feature Matrix (valid inputs, boundary edge cases, and unauthorized/malicious payloads).
   - For web UIs, run [e2e_visual_regression.py](../../suites/project-qa/skills/project-fix-and-verify/scripts/e2e_visual_regression.py) at `1440x900` and `375x667` and inspect the rendered PNG screenshots with `read_file`:
     ```bash
     python3 "<ATLAS_ROOT>/suites/project-qa/skills/project-fix-and-verify/scripts/e2e_visual_regression.py" "<entry-html-or-url>" --out-dir /tmp/atlas_postfix_shots
     ```
4. **Step B4 — Re-Invoke Mode A Full Post-Fix Re-Audit (Zero-Defect Loop):**
   - Run [verify_feature_coverage.py](../../suites/project-qa/skills/project-fix-and-verify/scripts/verify_feature_coverage.py):
     ```bash
     python3 "<ATLAS_ROOT>/suites/project-qa/skills/project-fix-and-verify/scripts/verify_feature_coverage.py" "<workspace_root>"
     ```
   - Re-run **Mode A** (`project_inventory.py`, `ui_visual_bug_probe.py`, `security_scan.py`, `live_cve_osv_check.py`, and `run-gates.mjs`). If **any** remaining bug, visual warning, or security flaw is detected, loop back to **Step B2** and fix it immediately until the re-audit reports **0 defects**.
5. **Step B5 — Final Verification Report:** Write `FIX-VERIFICATION-REPORT.md` using [verification-report-template.md](../../suites/project-qa/skills/project-fix-and-verify/assets/verification-report-template.md).
