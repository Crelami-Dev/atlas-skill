# Project Security Audit Report: <Project Name>

**Audit Date:** <YYYY-MM-DD>
**Current Risk Posture:** Critical / High / Medium / Low
**Current Code Status:** Read-Only (No code modifications applied — awaiting fix approval)

## 1. Security Executive Summary

| Severity | Finding Count | Attack Risk Summary |
| :--- | :---: | :--- |
| Critical | 0 | Full system/account takeover, sensitive credential leak, RCE, or SQLi |
| High | 0 | Authorization bypass (IDOR), stored XSS, exposed secrets, or SSRF |
| Medium | 0 | Weak CORS/CSRF configuration, missing rate limiting, or partial input validation |
| Low | 0 | HTTP header hardening, exposed version banners, or defense-in-depth improvements |
| **Total** | **0** | |

## 2. Analyzed Attack Surface Map

- **Authentication & Sessions:** <summary of checked handlers>
- **Public & Private Endpoints / Inputs:** <list of audited routes/modules>
- **Data Storage & Secrets:** <database, uploads, environment variables>
- **External Integrations & Dependencies:** <third-party packages / webhooks / external APIs>

## 3. Detailed Security Findings & Remediation Steps

### [SEC-01] <Vulnerability Title>

- **Severity:** Critical / High / Medium / Low
- **Category:** <e.g., OWASP A01 - Broken Access Control / IDOR>
- **File Location:** `path/to/file.ext:line`
- **Attack Scenario (How It Can Be Exploited):**
  Concrete attack path from attacker-controlled input to impact.
- **Root Vulnerability:** Why the current implementation is vulnerable.
- **How to Fix (Remediation & Hardening):**
  Concrete remediation steps with secure code patterns or upgraded package versions.
- **Patch Compatibility & Feature Impact Analysis:**
  - Config / environment variables / callers needing updates when applying the patch: <notes>
  - How to ensure legitimate workflows continue working safely after hardening: <notes>

## 4. Awaiting Fix Approval

All security findings and pre-planned hardening patches above have been prepared without altering project files. Reply to authorize remediation, and patching, 100% all-feature testing, and a complete post-fix security re-audit will be executed.
