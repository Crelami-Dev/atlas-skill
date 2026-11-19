# 100% Feature & Visual Screenshot Verification Protocol (v2.0 OP)

## 1. Zero Partial Testing Mandate
Fixing one file frequently breaks sibling routes, shared CSS Grid containers, auth middleware, or state stores. You MUST enumerate **100% of all project features** in a checklist and actively exercise every single one:
- Every page/view/tab and navigation link
- Every interactive control, filter, form validation, modal/drawer (`Escape` close), and copy/export action
- All 5 UI states (loading, populated, empty, zero-match + reset, error + retry)
- Security guards (invalid inputs, XSS strings rendered safely via `textContent`, unauthorized route rejection)

## 2. Mandatory Post-Fix Screenshot & Image-Vision Verification
Whenever the project has a web/HTML/GUI frontend:
1. Run `python3 <skill_dir>/scripts/e2e_visual_regression.py <entry-html-or-url> --out-dir /tmp/postfix_shots` (and `run-gates` if `atlas-frontend-design` is installed).
2. **Open the captured post-fix PNG screenshots (`postfix_verified_1440x900.png`, `postfix_verified_375x667.png`) with your image-viewing tool (`view_file` / `Read`)** to visually confirm:
   - Zero layout breakage, clipping, or mobile horizontal overflow (`innerWidth === viewportWidth`)
   - Calm, unslop visual craft preserved across desktop and mobile
3. Re-run `project_inventory.py`, `security_scan.py`, and `live_cve_osv_check.py` from scratch. Loop until **0 bugs, 0 CVEs, and 0 visual regressions** remain!
