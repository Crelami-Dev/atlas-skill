# Atlas-Skill: Risks, Deviations & Deferred Scope

**Status:** Active  
**Phase:** Phase 1 Only  
**Last Updated:** October 30, 2026  

---

## 1. Learnings from Sample Run

Executing the normalization pipeline on a representative sample before full migration proved essential in catching two real implementation quirks:

1. **`app.json` Data Structure:**
   * *Observation:* In `app.json`, `shells` is an array of 5 objects, while `kinds` is a dictionary of 13 keys. Initial code assumed `shells` was a dictionary.
   * *Resolution:* Corrected the schema mapping to iterate `shells` as a list, extracting the 5 shell blueprints cleanly into `app-shells.json` with metadata preserved.
2. **Argparse Attribute Convention:**
   * *Observation:* Python `argparse` maps `--dry-run` to `args.dry_run`, not `args.dry_run` with a hyphen.
   * *Resolution:* Corrected attribute access prior to the full migration run.

---

## 2. Scope Deviations & Compliance

* **Zero Deviations from Binding Decisions:** Phase 1 strictly complied with DEC-001 through DEC-008.
* **No Unapproved Dependencies:** Zero npm packages and zero third-party pip packages were introduced. All tools and tests operate using standard Python 3.9+ libraries.
* **Preservation of Source Repositories:** Verified 100% read-only adherence. No source files were touched.

---

## 3. Explicitly Deferred Phase 2 Scope

In compliance with prompt instructions, the following capabilities are deferred to Phase 2:
1. **Full Skill Orchestration:** Authoring complete multi-agent workflows in `skills/atlas-skill/SKILL.md`.
2. **Chatbot Prompt Inlining:** Writing complete standalone cheatsheets, color recipes, and CSS snippets in `skills/atlas-skill/SKILL.chatbot.md`.
3. **Browser Automation Tools:** Porting and integrating `atlas_check.py` and `inspect.mjs` into a unified `tools/` runner.
4. **Image Pipeline Execution:** Building live image generator subagent hooks and archive fetchers.
5. **End-to-End Benchmark Execution:** Running full blind reviews across the 12 briefs.

