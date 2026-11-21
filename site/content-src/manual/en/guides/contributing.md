---
title: Contributing Guide
description: Running repository validation and tests, adding new scenes cleanly, and registering new finding codes in sync with docs.
---

Contributions to Atlas-skill must preserve three invariants: **zero runtime npm dependencies in the core package**, **strict manifest integrity**, and **documentation generated straight from source files**.

## 1. Running Built-in Validation & Tests

Before opening a pull request or tagging a release, run every verification script from the repository root:

```sh
# 1. Validate package version sync, SKILL.md YAML frontmatter, JSON, .mjs syntax, and 189+ internal links
node scripts/validate-package.mjs

# 2. Run Node unit tests (including doc generator and scene catalog tests)
node --test tests/*.test.mjs

# 3. Run all 33 checker regression fixtures for quick-check.mjs and slop-scan
node skills/atlas-checker/scripts/self-test.mjs

# 4. Verify distribution tarball contains only core package files (no site/ or site/dist/)
npm pack --dry-run
```

If you modify `site/` or documentation sources, also run:

```sh
node scripts/gen-docs.mjs
node scripts/check-docs.mjs
cd site && npm run build
```

## 2. Adding or Updating a Scene

1. Add the scene entry inside the `scenes` array of `templates/scene-catalog.json` (`id`, `mode`, `family`, `fits`, `look`, `needs`, `never`, `rest`, `cost`).
2. Implement CSS and JS motion hooks in `templates/atlas-scenes.css` / `templates/atlas-scenes.mjs`, add a specimen to `templates/atlas-scenes-demo.html`, and document markup + usage rules in `references/scenes.md`.
3. Run `node scripts/gen-docs.mjs && node scripts/check-docs.mjs` — the scene catalog table and individual `/id/scenes/<id>/` & `/en/scenes/<id>/` pages update automatically.

## 3. Adding a Finding Code to `quick-check.mjs`

1. Implement the browser check and `fails.push("new-code: ...")` / `warns.push("new-code: ...")` in `skills/atlas-checker/scripts/quick-check.mjs`, plus regression fixtures in `skills/atlas-checker/scripts/self-test.mjs`.
2. Add a corresponding entry (`code: new-code`) to `site/content-src/findings.yml` with `severity`, `meaning_id`, `cause_id`, `fix_id`, `meaning_en`, `cause_en`, and `fix_en`.
3. Run `node scripts/gen-docs.mjs && node scripts/check-docs.mjs` so the Findings Dictionary stays 1-to-1 with `quick-check.mjs`.

## 4. Package Hygiene Rules

- Never add `site/`, `site/dist/`, `tests/`, or local working outputs to `"files"` in root `package.json` or `"include"` in `package-manifest.json`.
- Keep root `package.json` free of runtime `dependencies` and `devDependencies`; all Starlight dependencies belong strictly in `site/package.json`.
- Any empirical evaluation figures must come from `evals/` alongside all scope limits.
