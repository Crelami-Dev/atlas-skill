# Atlas Frontend Design & Optional QA Guardrail (v7.0.0)

1. **Frontend Design & Motion Workflow (`atlas-frontend-design` v7.0.0):**
   - Read and follow `.agents/skills/atlas-frontend-design/SKILL.md` (or `.claude/skills/atlas-frontend-design/SKILL.md`).
   - Run `deal-direction.mjs` when host tokens do not exist yet, choose **Full Mode** or **Compact Track** (`<!-- atlas-brief: light -->` for small prompts), enforce WCAG AA contrast and 5-state UI views, use Anime.js v4 (`createScope`, `spring`, GPU transforms), and verify with `run-gates.mjs`.
   - When a browser tool is available, capture and inspect desktop (`1440x900`), tablet (`820x1180`), and mobile (`375x667`) screenshots before concluding.

2. **Optional Project QA Suite (`--with-qa` / `suites/project-qa/`):**
   - For bug discovery or security auditing, run `project-bug-hunter` and `project-security-auditor` in read-only mode first, and only modify project files via `project-fix-and-verify` after explicit user approval.
