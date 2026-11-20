---
name: atlas-research
description: "Use when conducting domain reference research and UI mechanism comparisons before designing a new project in an unfamiliar domain. Do not use for small, obvious prompts or routine bug fixes."
---

# Atlas Research — Reference Mechanism Analysis

Domain research uncovers information hierarchies appropriate to the subject without copying another site's branding. On the Compact Track (short prompts in well-understood domains), `research-notes.md` is optional unless explicitly requested by the user.

## 1. Evidence Gathering Paths

When research is needed, use the tools available in your environment to populate `research-notes.md` based on [research-template.md](../../references/research-template.md):

1. **Live Browser Inspection:** Use browser tools or `node <atlas>/skills/atlas-research/scripts/capture-references.mjs --out ./maintenance/research <url>` on 3–5 relevant reference sites.
2. **Agent Web Search:** If headless Chromium is unavailable, use web search and page readers to analyze domain references and cross-industry benchmarks.
3. **Offline Environment:** Never invent URLs or pretend to visit live sites when network access is off, because fabricated references mislead design decisions. Record `live research unavailable (offline environment)` and rely on [domain-reasoning.md](../../references/domain-reasoning.md).

## 2. Separating Mechanisms from Visual Clichés

For each examined reference, record two entries in `research-notes.md`:
- **ADAPTED PRINCIPLES:** How information ordering, data density, or control proximity helps visitors complete their task.
- **REJECTED ELEMENTS:** Brand colors, heavy decorative effects, or scroll-jacking intentionally omitted so the implementation stays original and fast on mobile.

## 3. Reusing Research Notes

If `design-brief.md` has not changed and `research-notes.md` is less than 30 days old, reuse existing notes to keep iteration lean.
