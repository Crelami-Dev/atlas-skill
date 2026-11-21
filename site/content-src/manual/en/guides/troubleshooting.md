---
title: Troubleshooting
description: Practical solutions for environments without Python 3, restricted CDNs, doctor SHA-256 warnings, and Windows PowerShell quirks.
---

This page documents real failure modes and supported workarounds directly built into Atlas-skill tools.

## 1. Python 3 Is Not Installed

- **Symptom:** Static Gates 1–5 succeed, while Gate 6 (`run-gates.mjs --visual`) or `suites/project-qa/` Python scripts report missing Python.
- **Cause & Scope:** The CLI installer (`bin/atlas-skill.mjs`), static gates (`check-brief`, `check-tokens`, `check-motion-v4`, `slop-scan`, `check-copy`, `check-visual-proof`), and `quick-check.mjs` run purely on **Node.js 18+**. Only `visual_dom_inspector.py` and the QA Suite (`suites/project-qa/`) require **Python 3**.
- **Fix:**
  1. Run multi-viewport Playwright audits purely in Node.js with `quick-check.mjs`:
     ```sh
     node skills/atlas-checker/scripts/quick-check.mjs http://127.0.0.1:3000 --shots ./maintenance/browser --click-test
     ```
  2. When Python 3 cannot be installed, run `node scripts/run-gates.mjs <project> --mode full --strict` (omitting `--visual`) and accurately report Gate 6 Python & QA scripts as *not executed*.

## 2. Offline / Blocked CDNs

- **Symptom:** Wikimedia downloads in `fetch-photos.mjs` time out, `cdn.jsdelivr.net/npm/animejs@4/+esm` cannot load in a restricted network, or CVE auditing in the QA Suite cannot query OSV.dev / NIST NVD / CISA KEV.
- **Built-in Workarounds:**
  - **Anime.js v4 & Webfonts:** Bundle dependencies or serve `.woff2` files locally inside the project (as documented in `references/scenes.md` fallback mode `rest`), ensuring static HTML remains readable even if JS motion fails to load.
  - **Wikimedia Photos (`fetch-photos.mjs`):** Supports hard per-request caps (`--request-timeout`, default `30s`), total time budgets (`--timeout`, default `120s`), and `offline-fallback` reporting without leaving half-written `credits.json`. In strict air-gapped environments (`--offline`), use user-provided assets or token-styled specification plates (`data-atlas-proof="editorial-plate"`).
  - **QA Suite CVE Check (`live_cve_osv_check.py`):** Pass `--offline-parse-only` to audit dependency manifests locally without sending package lists to external APIs.

## 3. `atlas-skill doctor` Reports Modified Files

- **Symptom:** Running `node bin/atlas-skill.mjs doctor --agent <name>` flags **SHA-256** checksum mismatches or missing files compared to `.atlas-install.json`.
- **Cause:** Installed skill or reference files inside `.agents/skills/atlas-skill/` (or another agent folder) were edited directly or interrupted mid-copy.
- **Fix:**
  1. Inspect local changes; avoid modifying managed package files inside installed skill directories.
  2. Run an atomic update, which backs up the previous installation folder under `.atlas-skill-backups/` before restoring files:
     ```sh
     node bin/atlas-skill.mjs update --agent <name> --with-rules
     ```
  3. Re-run `node bin/atlas-skill.mjs doctor --agent <name>` to verify clean integrity.

## 4. Windows Quirks (PowerShell & Playwright)

- **Python Missing from `PATH`:** When Python is installed under `AppData\Local\Programs\Python\...` without global `PATH` registration, prepend its directory in PowerShell before calling `--visual`:
  ```powershell
  $env:PATH = "$env:LOCALAPPDATA\Programs\Python\Python310;$env:PATH"
  node scripts/run-gates.mjs <project> --mode full --strict --visual <url>
  ```
- **Chromium `file://` Policy or Custom Browser Paths:** `quick-check.mjs` automatically launches a temporary HTTP static server for local HTML files, avoiding `file://` restrictions. If Playwright or Chrome is installed outside default paths, set `ATLAS_PLAYWRIGHT_PACKAGE` or `ATLAS_BROWSER_PATH`.
- **Quoting in PowerShell 5.1:** Invoke Node scripts cleanly as `node scripts/...mjs` and use `--input-type=module` via stdin when passing complex regex snippets to avoid backtick/quote escaping issues.
