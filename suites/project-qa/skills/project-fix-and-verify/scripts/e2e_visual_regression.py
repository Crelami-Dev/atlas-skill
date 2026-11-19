#!/usr/bin/env python3
"""
project-fix-and-verify v2.0 OP — Post-Fix Multi-Viewport Screenshot & Zero-Regression Verifier
Captures post-fix Desktop & Mobile PNG screenshots so the agent MUST visually verify via image-vision (view_file / Read)
that all fixes look clean, unslop, and introduced zero layout or runtime regressions across viewports.
"""
import argparse
import importlib
import json
import os
import shutil
import tempfile
import time

def verify_post_fix(target: str, out_dir: str):
    try:
        webdriver = importlib.import_module("selenium.webdriver")
        Options = importlib.import_module("selenium.webdriver.chrome.options").Options
    except ModuleNotFoundError as exc:
        return {
            "target": target,
            "post_fix_screenshots": [],
            "viewports": {},
            "regressions": [f"Python package 'selenium' is not installed ({exc}). Install with 'pip install selenium'."],
            "status": "FAIL",
        }

    os.makedirs(out_dir, exist_ok=True)
    chrome_home = tempfile.mkdtemp(prefix="fixverify_chrome_")
    os.environ["HOME"] = chrome_home
    os.environ["XDG_CONFIG_HOME"] = os.path.join(chrome_home, ".config")
    os.environ["XDG_CACHE_HOME"] = os.path.join(chrome_home, ".cache")

    opts = Options()
    for flag in ["--headless=new", "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu", "--hide-scrollbars", "--window-size=1440,900"]:
        opts.add_argument(flag)
    opts.set_capability("goog:loggingPrefs", {"browser": "ALL"})

    driver = webdriver.Chrome(options=opts)
    out = {"target": target, "post_fix_screenshots": [], "viewports": {}, "regressions": [], "status": "PASS"}

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

        for vw, vh, mob in [(1440, 900, False), (390, 844, True), (375, 667, True), (320, 568, True)]:
            driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {"width": vw, "height": vh, "deviceScaleFactor": 1, "mobile": mob})
            driver.execute_script("window.scrollTo({top: 0, behavior: 'instant'});")
            time.sleep(0.18)
            if vw in (1440, 375):
                p = os.path.abspath(os.path.join(out_dir, f"postfix_verified_{vw}x{vh}.png"))
                driver.save_screenshot(p)
                out["post_fix_screenshots"].append(p)
            m = driver.execute_script("return {iw: window.innerWidth, sw: document.documentElement.scrollWidth};")
            out["viewports"][f"{vw}x{vh}"] = m
            if m["iw"] != vw or m["sw"] > vw + 1:
                out["regressions"].append(f"Viewport {vw}x{vh} overflow/zoom mismatch: {m}")

        for entry in driver.get_log("browser"):
            msg = entry.get("message", "")
            if any(k in msg for k in ["ERR_NAME_NOT_RESOLVED", "ERR_INTERNET_DISCONNECTED", "fonts.googleapis.com", "cdn.jsdelivr.net"]):
                continue
            if entry.get("level") == "SEVERE":
                out["regressions"].append(f"Console SEVERE: {msg}")

        if out["regressions"]:
            out["status"] = "FAIL"
        out["vision_gate"] = "MANDATORY: Inspect 'post_fix_screenshots' via view_file / Read before issuing LAPORAN-VERIFIKASI-PERBAIKAN.md!"
        return out
    finally:
        driver.quit()
        shutil.rmtree(chrome_home, ignore_errors=True)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--out-dir", default="/tmp/postfix_screenshots")
    args = ap.parse_args()
    res = verify_post_fix(args.target, args.out_dir)
    print(json.dumps(res, indent=2))
    if res["status"] != "PASS":
        raise SystemExit(1)
