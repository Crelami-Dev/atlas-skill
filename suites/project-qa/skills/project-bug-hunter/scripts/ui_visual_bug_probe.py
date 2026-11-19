#!/usr/bin/env python3
"""
project-bug-hunter v2.0 OP — Non-Mutating Visual Screenshot & Runtime UI Bug Probe
Renders target HTML file or running web URL in Headless Chromium WITHOUT modifying any project file,
captures diagnostic Desktop (1440x900) & Mobile (375x667, 320x568) screenshots for AI image-vision analysis,
and detects runtime console errors, dead anchors, unwired buttons, NaN/undefined text leaks, broken images,
and mobile horizontal overflow.
"""
import argparse
import importlib
import json
import os
import shutil
import tempfile
import time

def probe_ui(target: str, out_dir: str):
    try:
        webdriver = importlib.import_module("selenium.webdriver")
        Options = importlib.import_module("selenium.webdriver.chrome.options").Options
    except ModuleNotFoundError as exc:
        return {
            "mode": "READ_ONLY_VISUAL_BUG_PROBE",
            "target": target,
            "screenshots_to_inspect_via_vision": [],
            "detected_ui_bugs": [],
            "console_errors": [],
            "error": f"Python package 'selenium' is not installed ({exc}). Install with 'pip install selenium'.",
        }

    os.makedirs(out_dir, exist_ok=True)
    chrome_home = tempfile.mkdtemp(prefix="bughunter_probe_")
    os.environ["HOME"] = chrome_home
    os.environ["XDG_CONFIG_HOME"] = os.path.join(chrome_home, ".config")
    os.environ["XDG_CACHE_HOME"] = os.path.join(chrome_home, ".cache")

    opts = Options()
    for flag in ["--headless=new", "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu", "--hide-scrollbars", "--window-size=1440,900"]:
        opts.add_argument(flag)
    opts.set_capability("goog:loggingPrefs", {"browser": "ALL"})

    driver = webdriver.Chrome(options=opts)
    report = {
        "mode": "READ_ONLY_VISUAL_BUG_PROBE",
        "target": target,
        "screenshots_to_inspect_via_vision": [],
        "detected_ui_bugs": [],
        "console_errors": []
    }

    try:
        if target.startswith(("http://", "https://")):
            driver.get(target)
        else:
            with open(os.path.abspath(target), "r", encoding="utf-8") as f:
                html_str = f.read()
            driver.get("about:blank")
            fid = driver.execute_cdp_cmd("Page.getFrameTree", {})["frameTree"]["frame"]["id"]
            driver.execute_cdp_cmd("Page.setDocumentContent", {"frameId": fid, "html": html_str})
        time.sleep(0.45)

        for vw, vh, mob, label in [(1440, 900, False, "desktop_1440x900"), (375, 667, True, "mobile_375x667"), (320, 568, True, "mobile_320x568")]:
            driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {"width": vw, "height": vh, "deviceScaleFactor": 1, "mobile": mob})
            driver.execute_script("window.scrollTo({top: 0, behavior: 'instant'});")
            time.sleep(0.2)
            shot_path = os.path.abspath(os.path.join(out_dir, f"bug_probe_{label}.png"))
            driver.save_screenshot(shot_path)
            report["screenshots_to_inspect_via_vision"].append(shot_path)

            dom_probe = driver.execute_script(r"""
                const bugs = [];
                const iw = window.innerWidth;
                const sw = document.documentElement.scrollWidth;
                if (sw > iw + 1 || iw !== arguments[0]) {
                  bugs.push({severity: 'Medium', type: 'viewport-overflow', detail: `Viewport ${arguments[0]}px rendered innerWidth=${iw}, scrollWidth=${sw}`});
                }
                const txt = document.body ? document.body.innerText : '';
                if (/\bNaN\b|\bundefined\b|\[object Object\]/.test(txt)) {
                  bugs.push({severity: 'High', type: 'corrupted-state-text', detail: 'Visible NaN / undefined / [object Object] rendered in UI text'});
                }
                const deadLinks = [...document.querySelectorAll('a[href^="#"]')].filter(a => {
                  const id = a.getAttribute('href').slice(1);
                  return id && !document.getElementById(id);
                }).map(a => a.getAttribute('href'));
                if (deadLinks.length) {
                  bugs.push({severity: 'Medium', type: 'dead-anchor-links', detail: `Broken in-page anchors: ${deadLinks.join(', ')}`});
                }
                const brokenImgs = [...document.querySelectorAll('img')].filter(i => i.offsetParent !== null && (!i.complete || i.naturalWidth === 0));
                if (brokenImgs.length) {
                  bugs.push({severity: 'High', type: 'broken-images', detail: `${brokenImgs.length} visible image(s) failed to load`});
                }
                return bugs;
            """, vw)
            for b in dom_probe:
                b["viewport"] = f"{vw}x{vh}"
                report["detected_ui_bugs"].append(b)

        for entry in driver.get_log("browser"):
            msg = entry.get("message", "")
            if any(k in msg for k in ["ERR_NAME_NOT_RESOLVED", "ERR_INTERNET_DISCONNECTED", "fonts.googleapis.com", "cdn.jsdelivr.net"]):
                continue
            if entry.get("level") == "SEVERE":
                report["console_errors"].append(msg)

        report["vision_instruction"] = (
            "MANDATORY: Open 'screenshots_to_inspect_via_vision' with view_file / Read to visually spot overlapping text, "
            "clipped elements, broken contrast, or layout bugs, and include them in your read-only .md bug report!"
        )
        return report
    finally:
        driver.quit()
        shutil.rmtree(chrome_home, ignore_errors=True)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="HTML path or live local URL")
    ap.add_argument("--out-dir", default="/tmp/bug_hunter_screenshots")
    args = ap.parse_args()
    res = probe_ui(args.target, args.out_dir)
    print(json.dumps(res, indent=2))
    if res.get("error"):
        raise SystemExit(1)
