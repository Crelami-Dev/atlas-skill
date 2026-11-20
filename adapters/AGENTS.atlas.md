# Atlas 3-Skill Architecture & Quality Guardrail (v7.0.0)

1. **All-in-One Full Stack + Auto Bug Hunter (`/atlas-skill`):**
   - Read and follow `.agents/skills/atlas-skill/SKILL.md` (or `.claude/skills/atlas-skill/SKILL.md`).
   - Run `deal-direction.mjs`, fetch real licensed photography on visual domains (`scripts/fetch-photos.mjs`), enforce WCAG AA contrast, `65ch` measure, `>= 44px` tap targets, and Anime.js v4 motion (`createScope`), verify with `run-gates.mjs --visual` + `quick-check.mjs` + screenshot inspection, and **automatically run Bug Hunter + Security/CVE scan with immediate auto-remediation (`project-fix-and-verify`)**.

2. **Frontend-Only Orchestrator (`/atlas-frontend`):**
   - Read and follow `.agents/skills/atlas-frontend/SKILL.md` when the user wants full frontend design, real photography, Anime.js v4 motion, and visual browser verification without running the Bug Hunter / Security CVE suite.

3. **Dedicated Bug & Security Hunter + Smart Fix Switch (`/atlas-bug-hunter`):**
   - Read and follow `.agents/skills/atlas-bug-hunter/SKILL.md`. Default to **Mode A (Read-Only Deep Hunt & `PROJECT-AUDIT-REPORT.md`)**, and automatically switch to **Mode B (`project-fix-and-verify` 100% feature testing & zero-defect re-audit)** whenever the user commands to fix/repair/patch issues.
