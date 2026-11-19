---
name: project-security-auditor
description: "Audits software projects in strict read-only mode for OWASP Top 10 flaws, leaked secrets, broken auth/IDOR, injection vectors, and live CVE/OSV/GHSA/CISA-KEV advisories. Pre-plans hardening patches and delivers a Markdown (.md) security report while waiting for user approval. Never use to modify project code directly."
---

# Project Security Auditor — AppSec & Live CVE Intelligence (Read-Only)

Perform a deep, read-only application security audit combining static source-to-sink code analysis with **live vulnerability intelligence** (OSV.dev, GitHub Security Advisories, NIST NVD CVEs, CISA Known Exploited Vulnerabilities, and live web search for newly disclosed framework exploits), prepare non-breaking remediation plans ahead of time, and deliver a comprehensive `.md` security report while waiting for explicit user instruction before modifying project files.

## Decision Tree

- **User asks to check security / find vulnerabilities ONLY** (`cari celah keamanan`, `audit keamanan`, `cek security`): Execute Steps 1 through 6 below in strictly read-only mode, deliver `LAPORAN-AUDIT-KEAMANAN.md`, and wait for user approval.
- **User asks to check BOTH bugs AND security** (`cari bug dan celah keamanan`, `audit projek menyeluruh`): Run both `project-bug-hunter` and `project-security-auditor` and deliver a unified `LAPORAN-AUDIT-PROJEK.md`, waiting for user instruction before patching.
- **User explicitly commands to FIX / PATCH vulnerabilities** (`benerin`, `perbaiki celah keamanan`, `patch semua`): Load and execute `project-fix-and-verify`.

## Path Resolution

Resolve `<SKILL_DIR>` as the directory containing this `SKILL.md` file (e.g., `<workspace>/.agents/skills/project-security-auditor`, `~/.gemini/config/skills/project-security-auditor`, or `suites/project-qa/skills/project-security-auditor`). Use `python3` on macOS/Linux or `python` on Windows.

## Execution Protocol

### Step 1: Enforce the Read-Only & Non-Destructive Security Gate

Never modify, delete, or patch project source or config files during the audit phase. Keep all analysis strictly read-only and never send destructive payloads to live production servers.

### Step 2: Scan Attack Surface, Secrets, and Dangerous Sinks

1. Run [security_scan.py](scripts/security_scan.py) to check for hardcoded secrets, `NEXT_PUBLIC_`/`VITE_` env leaks, SQL/command injection sinks, and unsafe DOM (`innerHTML`/`dangerouslySetInnerHTML`):
   ```bash
   python3 "<SKILL_DIR>/scripts/security_scan.py" "<workspace_root>"
   ```
2. Map all trust boundaries: public vs authenticated API routes, role/admin checks, login/JWT/session handlers, file uploads, webhooks, payment/checkout logic, raw database queries, SSR/DOM sinks, and `.env` / cloud configs.

### Step 3: Search Live Databases & the Web for the Latest Vulnerabilities

Never rely solely on static training-cutoff memory for security advisories. Execute **all three layers** of live threat intelligence:

1. **Layer A — Live OSV.dev, NVD CVE 2.0 & CISA KEV Scanner**:
   Run [live_cve_osv_check.py](scripts/live_cve_osv_check.py) against project lockfiles and manifests (`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `requirements.txt`, `poetry.lock`, `go.mod`, `Cargo.lock`, `composer.lock`):
   ```bash
   python3 "<SKILL_DIR>/scripts/live_cve_osv_check.py" "<workspace_root>" --auto-keywords
   ```
   - **Privacy & Network Notice:** By default, `live_cve_osv_check.py` sends dependency package names and versions over the network to **OSV.dev**, **NIST NVD**, and **CISA KEV** public APIs.
   - **Offline Mode (`--offline-parse-only`):** In air-gapped environments or when external dependency queries are disallowed, pass `--offline-parse-only` to parse manifests locally without outbound network requests.
2. **Layer B — Native Package Manager Security Audit (Read-Only)**:
   Where available, run read-only audit commands (`npm audit --json`, `pnpm audit --json`, `pip-audit`, `govulncheck ./...`, `cargo audit`, `composer audit`) without `--fix`.
3. **Layer C — Targeted Live Web Search for Latest Stack Advisories & Bypass Patterns**:
   Use web search to check recent CVEs, GHSA advisories, and newly discovered architectural bypasses for the exact frameworks, auth libraries, ORMs, and runtimes used by this project (middleware order, route matchers, Server Actions, file upload parsers, ORM filter objects, CORS/CSRF settings, JWT verification).

### Step 4: Verify Source-to-Sink Exploitability & Business Logic Access Control

Walk through [security-audit-checklist.md](references/security-audit-checklist.md) to eliminate false positives:
- **Access Control (OWASP A01):** Audit **IDOR / BOLA** and privilege escalation on every read, update, and delete route (confirming server-side ownership checks against the authenticated session, never trusting client-supplied `userId` or `role`), plus path traversal guards.
- **Auth, Session & Network (OWASP A07 / A10):** Verify JWT algorithm checks, cookie flags (`HttpOnly; Secure; SameSite`), CORS policies, CSRF protections, and SSRF URL validation.

### Step 5: Pre-Plan Safe Hardening Patches and Compatibility Impact

Investigate exact fixes before writing the report so you are ready if instructed to patch:
- Draft the exact secure code pattern or dependency upgrade version for every vulnerability.
- Identify breaking-change risks (rotating leaked credentials, new `.env` keys, tightening CORS/CSP headers without breaking frontend API calls, or major package upgrades).

### Step 6: Deliver the Markdown Security Report and Wait for Approval

1. Follow [security-report-template.md](assets/security-report-template.md) to create `LAPORAN-AUDIT-KEAMANAN.md` (or merge into `LAPORAN-AUDIT-PROJEK.md` alongside `project-bug-hunter`) in the user's language.
2. Cite exact `file:line` locations, CVE/GHSA identifiers and advisory URLs, realistic attack scenarios, step-by-step hardening instructions (`Cara Mengatasi`), and compatibility notes. Redact real secret values (`sk_live_****abcd`).
3. Present the `.md` report and **wait for explicit user instruction** before running `project-fix-and-verify`.
