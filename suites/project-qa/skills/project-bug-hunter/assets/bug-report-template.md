# Project Bug Audit Report: <Project Name>

**Audit Date:** <YYYY-MM-DD>
**Current Code Status:** Read-Only (No code modifications applied — awaiting fix approval)

## 1. Executive Summary

| Severity | Finding Count | Impact Summary |
| :--- | :---: | :--- |
| Critical | 0 | Causes application crashes, data loss, or complete failure of core features |
| High | 0 | Primary workflows break under normal use or transaction paths fail |
| Medium | 0 | Edge cases fail, error handling degrades, or UI/state falls out of sync |
| Low | 0 | Minor code quality, lightweight performance, or cosmetic layout issues |
| **Total** | **0** | |

## 2. Inspected Feature Inventory

Complete inventory of features across the project and their initial diagnostic status:

- **[Feature Name 1]** (`path/file`): Status (Defective / Passing) — Brief note.
- **[Feature Name 2]** (`path/file`): Status (Defective / Passing) — Brief note.

## 3. Detailed Bug Findings & Remediation Steps

### [BUG-01] <Specific Bug Title>

- **Severity:** Critical / High / Medium / Low
- **File Location:** `path/to/file.ext:line`
- **Affected Feature:** <Feature name>
- **Reproduction Steps:**
  1. Initial trigger action
  2. Specific input or state condition
  3. Actual outcome vs expected outcome
- **Root Cause:** Technical explanation of why the defect occurs.
- **How to Fix (Technical Remediation):**
  Step-by-step fix instructions and recommended safe code snippet.
- **Fix Readiness & Cross-Feature Impact Analysis (Blast Radius):**
  - Related modules/callers affected by the fix: `path/related_file.ext`
  - Guardrails required to avoid regressions in adjacent features: <notes>

## 4. Awaiting Fix Approval

All findings above have been analyzed with concrete remediation plans without modifying any project files. Reply if you approve applying these fixes (all findings or specific IDs), and full remediation, 100% feature testing, and whole-project re-auditing will proceed.
