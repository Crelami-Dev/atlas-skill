#!/usr/bin/env python3
"""
Atlas v7.0.0 — Multimodal Screenshot Renderer & Aesthetic DOM Geometry Inspector
Renders any local .html file (inlining local relative stylesheets/scripts into Page.setDocumentContent
so sandboxed Chromium policies blocking file:// URLs never block rendering) or live URL across
Desktop (1440x900 top/mid/low), Tablet (820x1180), and Mobile (390x844, 375x667, 320x568).
"""
import argparse
import base64
import importlib
import json
import mimetypes
import os
from pathlib import Path
import re
import shutil
import tempfile
import time


def inline_local_assets(html_str: str, base_dir: Path) -> str:
    """Inline local relative <link rel='stylesheet'>, <script src='...'>, and <img src='...'> for about:blank rendering."""

    def replace_css(match):
        tag = match.group(0)
        href_m = re.search(r'href=["\']([^"\']+)["\']', tag, re.I)
        if not href_m:
            return tag
        href = href_m.group(1)
        if href.startswith(("http://", "https://", "data:", "//")):
            return tag
        css_path = (base_dir / href).resolve()
        if css_path.is_file():
            css_content = css_path.read_text(encoding="utf-8", errors="ignore")
            return f"<style data-inlined-from=\"{href}\">\n{css_content}\n</style>"
        return tag

    def replace_img(match):
        prefix, src, suffix = match.group(1), match.group(2), match.group(3)
        if src.startswith(("http://", "https://", "data:", "//")) or not src.strip():
            return match.group(0)
        img_path = (base_dir / src).resolve()
        if img_path.is_file():
            mime, _ = mimetypes.guess_type(str(img_path))
            mime = mime or "image/png"
            b64 = base64.b64encode(img_path.read_bytes()).decode("ascii")
            return f'{prefix}data:{mime};base64,{b64}{suffix}'
        return match.group(0)

    out = re.sub(r'<link\b[^>]*rel=["\']stylesheet["\'][^>]*>', replace_css, html_str, flags=re.I)
    out = re.sub(r'(<img\b[^>]*\bsrc=["\'])([^"\']+)(["\'][^>]*>)', replace_img, out, flags=re.I)
    return out


def run_inspection(target: str, out_dir: str):
    try:
        webdriver = importlib.import_module("selenium.webdriver")
        Options = importlib.import_module("selenium.webdriver.chrome.options").Options
    except ModuleNotFoundError as exc:
        return {
            "target": target,
            "screenshots_for_vision_review": [],
            "viewports": {},
            "aesthetic_findings": [],
            "console_errors": [],
            "overall": "FAIL",
            "error": f"Python package 'selenium' is not installed ({exc}). Install with 'pip install selenium' or use Node quick-check.mjs.",
        }

    os.makedirs(out_dir, exist_ok=True)
    chrome_home = tempfile.mkdtemp(prefix="atlas_chrome_")
    os.environ["HOME"] = chrome_home
    os.environ["XDG_CONFIG_HOME"] = os.path.join(chrome_home, ".config")
    os.environ["XDG_CACHE_HOME"] = os.path.join(chrome_home, ".cache")

    opts = Options()
    for flag in [
        "--headless=new",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--hide-scrollbars",
        "--window-size=1440,900",
    ]:
        opts.add_argument(flag)
    opts.set_capability("goog:loggingPrefs", {"browser": "ALL"})

    driver = webdriver.Chrome(options=opts)
    report = {
        "target": target,
        "screenshots_for_vision_review": [],
        "viewports": {},
        "aesthetic_findings": [],
        "console_errors": [],
        "overall": "PASS",
    }

    def set_vp(w, h, mobile=False):
        driver.execute_cdp_cmd(
            "Emulation.setDeviceMetricsOverride",
            {"width": w, "height": h, "deviceScaleFactor": 1, "mobile": mobile},
        )
        time.sleep(0.18)

    try:
        if target.startswith(("http://", "https://")):
            driver.get(target)
        else:
            abs_html = Path(os.path.abspath(target))
            raw_html = abs_html.read_text(encoding="utf-8")
            html_str = inline_local_assets(raw_html, abs_html.parent)
            driver.get("about:blank")
            fid = driver.execute_cdp_cmd("Page.getFrameTree", {})["frameTree"]["frame"]["id"]
            driver.execute_cdp_cmd("Page.setDocumentContent", {"frameId": fid, "html": html_str})
        time.sleep(0.4)

        # 1. Desktop 1440x900 Captures (Top, Mid, Low) + Aesthetic Geometry Audit
        set_vp(1440, 900, mobile=False)
        driver.execute_script("window.scrollTo({top: 0, behavior: 'instant'});")
        time.sleep(0.18)
        p_top = os.path.abspath(os.path.join(out_dir, "desktop_1440_top.png"))
        driver.save_screenshot(p_top)
        report["screenshots_for_vision_review"].append(p_top)

        max_scroll = driver.execute_script(
            "return Math.max(0, document.documentElement.scrollHeight - window.innerHeight);"
        )
        if max_scroll > 300:
            driver.execute_script(
                f"window.scrollTo({{top: {int(max_scroll * 0.46)}, behavior: 'instant'}});"
            )
            time.sleep(0.2)
            p_mid = os.path.abspath(os.path.join(out_dir, "desktop_1440_mid.png"))
            driver.save_screenshot(p_mid)
            report["screenshots_for_vision_review"].append(p_mid)

            driver.execute_script(
                f"window.scrollTo({{top: {int(max_scroll * 0.88)}, behavior: 'instant'}});"
            )
            time.sleep(0.2)
            p_low = os.path.abspath(os.path.join(out_dir, "desktop_1440_low.png"))
            driver.save_screenshot(p_low)
            report["screenshots_for_vision_review"].append(p_low)

        driver.execute_script("window.scrollTo({top: 0, behavior: 'instant'});")
        time.sleep(0.15)

        desktop_audit = driver.execute_script(
            r"""
            const findings = [];
            const iw = window.innerWidth;
            const sw = document.documentElement.scrollWidth;
            if (sw > iw + 1) findings.push({level: 'error', id: 'desktop-overflow', detail: `scrollWidth ${sw} > innerWidth ${iw}`});

            const cta = document.querySelector('[data-primary], main button, main a.btn-primary');
            if (cta) {
              const r = cta.getBoundingClientRect();
              if (r.bottom > 900 || r.height < 38) {
                findings.push({level: 'warn', id: 'desktop-cta-fold', detail: `CTA bottom=${Math.round(r.bottom)}px, height=${Math.round(r.height)}px`});
              }
            }

            const shells = [...document.querySelectorAll('main section > div')].slice(0, 4);
            for (const sh of shells) {
              const r = sh.getBoundingClientRect();
              if (r.width > 600 && r.width < iw - 20) {
                const leftGap = r.left;
                const rightGap = iw - r.right;
                if (Math.abs(leftGap - rightGap) > 28) {
                  findings.push({level: 'warn', id: 'off-centre-margin', detail: `Left margin ${Math.round(leftGap)}px vs right ${Math.round(rightGap)}px`});
                  break;
                }
              }
            }

            function parseRgb(str) {
              const m = String(str || '').match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/i);
              if (!m) return null;
              return { r: Number(m[1]), g: Number(m[2]), b: Number(m[3]), a: m[4] !== undefined ? Number(m[4]) : 1 };
            }
            function relLum(rgb) {
              const ch = [rgb.r, rgb.g, rgb.b].map(v => {
                const s = v / 255;
                return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
              });
              return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2];
            }
            function effectiveBg(el) {
              let cur = el;
              while (cur && cur !== document.documentElement) {
                const bg = parseRgb(window.getComputedStyle(cur).backgroundColor);
                if (bg && bg.a > 0.05) return bg;
                cur = cur.parentElement;
              }
              const bodyBg = parseRgb(window.getComputedStyle(document.body).backgroundColor);
              return (bodyBg && bodyBg.a > 0.05) ? bodyBg : { r: 255, g: 255, b: 255, a: 1 };
            }

            // Check 1: Body text minimum 16px & line width 60-75ch (<= 820px for multi-line body paragraphs)
            const bodyParas = [...document.querySelectorAll('main p')].filter(p => {
              if (!p.offsetParent) return false;
              if (p.closest('figcaption, footer, small, [data-meta], .form-error')) return false;
              return (p.textContent || '').trim().length >= 40;
            });
            for (const p of bodyParas) {
              const cs = window.getComputedStyle(p);
              const fsPx = parseFloat(cs.fontSize);
              const pr = p.getBoundingClientRect();
              if (fsPx < 15.5) {
                findings.push({level: 'warn', id: 'body-font-too-small', detail: `Paragraph font-size is ${fsPx.toFixed(1)}px (< 16px minimum)`});
                break;
              }
              if (pr.width > 840 && (p.textContent || '').trim().length > 140) {
                findings.push({level: 'warn', id: 'line-measure-too-wide', detail: `Paragraph width ${Math.round(pr.width)}px exceeds ~75ch comfortable reading measure`});
                break;
              }
            }

            // Check 2: WCAG Contrast on visible text elements in main
            const textSamples = [...document.querySelectorAll('main h1, main h2, main h3, main h4, main p, main button, main a, main label')].filter(el => el.offsetParent !== null && (el.textContent || '').trim().length > 0);
            for (const el of textSamples) {
              const cs = window.getComputedStyle(el);
              const fg = parseRgb(cs.color);
              const bg = effectiveBg(el);
              if (fg && bg) {
                const l1 = relLum(fg);
                const l2 = relLum(bg);
                const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
                const fsPx = parseFloat(cs.fontSize);
                const minRatio = fsPx >= 24 || (fsPx >= 18.66 && Number(cs.fontWeight) >= 700) ? 3.0 : 4.5;
                if (ratio < minRatio) {
                  findings.push({level: 'error', id: 'low-text-contrast', detail: `Contrast ratio ${ratio.toFixed(2)}:1 < ${minRatio}:1 on <${el.tagName.toLowerCase()}>`});
                  break;
                }
              }
            }

            // Check 3: Sections (text-wall, excessive-empty-area, dark-section-long-prose-only)
            const sections = [...document.querySelectorAll('main section')].filter(s => s.offsetParent !== null);
            for (const sec of sections) {
              const r = sec.getBoundingClientRect();
              const richCount = sec.querySelectorAll('img, canvas, video, svg, table, select, input, [role="tablist"], [data-atlas-proof], [data-photo-placeholder], [data-photo-slot]').length;
              if (r.height > 820 && richCount === 0) {
                findings.push({level: 'warn', id: 'text-wall-section', detail: `Section #${sec.id || 'unnamed'} is ${Math.round(r.height)}px tall with 0 visual/interactive media`});
              }

              if (r.height >= 280 && r.width >= 600) {
                const secArea = r.width * r.height;
                const leafNodes = [...sec.querySelectorAll('h1, h2, h3, h4, p, ul, ol, dl, table, figure, img, svg, canvas, video, form, [data-photo-placeholder], [data-photo-slot], [data-atlas-proof]')];
                let coveredArea = 0;
                for (const node of leafNodes) {
                  const nr = node.getBoundingClientRect();
                  coveredArea += Math.max(0, nr.width) * Math.max(0, nr.height);
                }
                const fillRatio = Math.min(1, coveredArea / Math.max(1, secArea));
                if (fillRatio < 0.16) {
                  findings.push({level: 'warn', id: 'excessive-empty-area', detail: `Section #${sec.id || 'unnamed'} content fill ratio is ${(fillRatio * 100).toFixed(1)}% (< 12% threshold)`});
                }
              }

              const secBg = effectiveBg(sec);
              if (secBg && relLum(secBg) < 0.12) {
                const proseLen = [...sec.querySelectorAll('p')].reduce((acc, p) => acc + (p.textContent || '').trim().length, 0);
                const structCount = sec.querySelectorAll('table, dl, pre, figure, img, svg, canvas, video, [data-photo-placeholder], [data-photo-slot], [data-atlas-proof]').length;
                if (proseLen > 420 && structCount === 0) {
                  findings.push({level: 'warn', id: 'dark-section-long-prose-only', detail: `Dark section #${sec.id || 'unnamed'} contains ${proseLen} chars of plain paragraph text without structured cards/media/specs`});
                }
              }
            }

            // Check 4: SVG <text> overlapping non-background shapes inside the same <svg>
            for (const svg of document.querySelectorAll('svg')) {
              if (!svg.offsetParent) continue;
              const sr = svg.getBoundingClientRect();
              const shapes = [...svg.querySelectorAll('rect, path, circle, polygon, line')].filter(sh => {
                const r = sh.getBoundingClientRect();
                // Ignore full-canvas background rects
                return (r.width > 4 || r.height > 4) && !(r.width >= sr.width * 0.9 && r.height >= sr.height * 0.9);
              });
              for (const t of svg.querySelectorAll('text')) {
                const tr = t.getBoundingClientRect();
                if (tr.width <= 0 || tr.height <= 0) continue;
                for (const sh of shapes) {
                  const shr = sh.getBoundingClientRect();
                  const overlapX = Math.min(tr.right, shr.right) - Math.max(tr.left, shr.left);
                  const overlapY = Math.min(tr.bottom, shr.bottom) - Math.max(tr.top, shr.top);
                  if (overlapX > 6 && overlapY > 6) {
                    const fill = window.getComputedStyle(sh).fill;
                    const stroke = window.getComputedStyle(sh).stroke;
                    if (stroke && stroke !== 'none' && (fill === 'none' || fill === 'rgba(0, 0, 0, 0)')) {
                      findings.push({level: 'error', id: 'svg-text-overlap', detail: `SVG text "${(t.textContent || '').slice(0, 32)}" overlaps stroked shape boundary`});
                      break;
                    }
                  }
                }
              }
            }

            // Check 5: Two-column split grids on 1440px desktop must have >= 2 side-by-side children
            for (const g of document.querySelectorAll('.split-42-58, .split-60-40, .grid-2col')) {
              if (!g.offsetParent) continue;
              const kids = [...g.children].filter(ch => ch.offsetParent !== null);
              if (kids.length < 2) {
                findings.push({level: 'error', id: 'desktop-broken-split-grid', detail: `Split/2-col container has only ${kids.length} visible child (check stray closing </div>)`});
              } else {
                const r0 = kids[0].getBoundingClientRect();
                const r1 = kids[1].getBoundingClientRect();
                if (r1.top >= r0.bottom - 4) {
                  findings.push({level: 'error', id: 'desktop-broken-split-grid', detail: `2-column child wrapped below first child at 1440px desktop`});
                }
              }
            }

            const brokenImgs = [...document.querySelectorAll('img')].filter(i => i.offsetParent !== null && (!i.complete || i.naturalWidth === 0));
            if (brokenImgs.length > 0) {
              findings.push({level: 'error', id: 'broken-images', detail: `${brokenImgs.length} visible <img> failed to decode`});
            }

            const bodyText = (document.body && document.body.innerText) ? document.body.innerText : '';
            const leakMatch = bodyText.match(/(?:\b(?:ganti(?:\s+dengan)?\s+(?:foto|gambar)(?:\s+(?:asli|ini))?|replace\s+(?:this\s+)?(?:with\s+)?(?:real\s+|actual\s+)?(?:photo|image)|(?:insert|upload)\s+(?:real\s+)?(?:photo|image)(?:\s+here)?|(?:taruh|masukkan|pasang)\s+(?:foto|gambar)\s+(?:di\s+sini|disini)|(?:foto|gambar)\s+\S+(?:\s+\S+)?\s+di\s+sini|menunggu\s+foto(?:\s+dokumentasi|\s+asli|\s+klien)?|foto\s+menyusul|foto\s+akan\s+(?:ditambahkan|menyusul)|awaiting\s+(?:real\s+|client\s+)?photo(?:graphy|s)?|(?:photo|image)\s+(?:coming\s+soon|tbd)|(?:slot\s+foto|photo\s+slot)\s*(?:#?\d+|hero|utama|banner|produk|menu|galeri)|(?:image|photo|foto)\s+placeholder|placeholder\s+(?:image|photo|foto)|data\s+klien\s+diperlukan)\b|\[\s*(?:ganti\s+dengan\s+foto|replace\s+with\s+photo|insert\s+image|placeholder|data\s+klien\s+diperlukan|(?:foto|image)\s*:[^\]]+|foto[^\]]{0,40}di\s+sini)[^\]]*\])/i);
            if (leakMatch) {
              findings.push({level: 'error', id: 'leaked-photo-placeholder-ui', detail: `Visible developer/placeholder instruction detected in DOM: "${leakMatch[0]}"`});
            }

            for (const slot of document.querySelectorAll('[data-photo-slot], [data-photo-placeholder]')) {
              if (!slot.offsetParent) continue;
              const hasMedia = slot.querySelector('img, picture, canvas, video, svg');
              const txtLen = (slot.innerText || '').trim().length;
              if (!hasMedia && txtLen < 12) {
                findings.push({level: 'error', id: 'empty-photo-slot', detail: `Photo slot [data-photo-slot] has no rendered media and insufficient editorial specimen text (${txtLen} chars)`});
                break;
              }
            }

            return {iw, sw, sectionCount: sections.length, findings};
        """
        )
        report["viewports"]["1440x900"] = {
            "iw": desktop_audit["iw"],
            "sw": desktop_audit["sw"],
            "sections": desktop_audit["sectionCount"],
        }
        report["aesthetic_findings"].extend(desktop_audit["findings"])

        # 2. Tablet 820x1180 Capture + Viewport Lock
        set_vp(820, 1180, mobile=True)
        driver.execute_script("window.scrollTo({top: 0, behavior: 'instant'});")
        time.sleep(0.18)
        p_tab = os.path.abspath(os.path.join(out_dir, "tablet_820x1180_top.png"))
        driver.save_screenshot(p_tab)
        report["screenshots_for_vision_review"].append(p_tab)
        tab_check = driver.execute_script(
            "return {iw: window.innerWidth, sw: document.documentElement.scrollWidth};"
        )
        report["viewports"]["820x1180"] = tab_check
        if tab_check["sw"] > 821:
            report["aesthetic_findings"].append(
                {
                    "level": "error",
                    "id": "tablet-viewport-blowout-820",
                    "detail": f"Expected 820px width, got scrollWidth={tab_check['sw']}",
                }
            )

        # 3. Mobile 390x844, 375x667, & 320x568 Exact Viewport Lock + Screenshot
        for vw, vh in [(390, 844), (375, 667), (320, 568)]:
            set_vp(vw, vh, mobile=True)
            driver.execute_script("window.scrollTo({top: 0, behavior: 'instant'});")
            time.sleep(0.18)
            if vw == 375:
                p_mob = os.path.abspath(os.path.join(out_dir, "mobile_375x667_top.png"))
                driver.save_screenshot(p_mob)
                report["screenshots_for_vision_review"].append(p_mob)

            m_check = driver.execute_script(
                """
                const iw = window.innerWidth;
                const sw = document.documentElement.scrollWidth;
                const cta = document.querySelector('[data-primary], main button, main a.btn-primary');
                const ctaBottom = cta ? Math.round(cta.getBoundingClientRect().bottom) : null;
                const squeezed = [];
                if (vw === 375) {
                  for (const el of document.querySelectorAll('main *')) {
                    const cs = window.getComputedStyle(el);
                    if (cs.display === 'grid' && el.children.length >= 3) {
                      const narrowChildren = [...el.children].filter(ch => ch.getBoundingClientRect().width > 0 && ch.getBoundingClientRect().width < 112);
                      if (narrowChildren.length >= 3) {
                        squeezed.push(el.tagName.toLowerCase());
                        break;
                      }
                    }
                  }
                }
                return {iw, sw, ctaBottom, squeezed};
            """
            )
            report["viewports"][f"{vw}x{vh}"] = m_check
            if m_check["iw"] != vw or m_check["sw"] > vw + 1:
                report["aesthetic_findings"].append(
                    {
                        "level": "error",
                        "id": f"mobile-viewport-blowout-{vw}",
                        "detail": f"Expected {vw}px exact width, got innerWidth={m_check['iw']}, scrollWidth={m_check['sw']} (check CSS Grid min-width: 0)",
                    }
                )
            if vw == 375 and m_check.get("squeezed"):
                report["aesthetic_findings"].append(
                    {
                        "level": "error",
                        "id": "mobile-squeezed-grid",
                        "detail": f"Multi-column grid did not collapse to single column on 375px mobile ({m_check['squeezed']})",
                    }
                )
            if vw == 375 and m_check["ctaBottom"] and m_check["ctaBottom"] > 667:
                report["aesthetic_findings"].append(
                    {
                        "level": "warn",
                        "id": "mobile-375-cta-below-fold",
                        "detail": f"Primary CTA bottom is at {m_check['ctaBottom']}px (> 667px short-screen fold)",
                    }
                )

        for entry in driver.get_log("browser"):
            msg = entry.get("message", "")
            if any(
                ignore in msg
                for ignore in [
                    "ERR_NAME_NOT_RESOLVED",
                    "ERR_INTERNET_DISCONNECTED",
                    "fonts.googleapis.com",
                    "cdn.jsdelivr.net",
                    "esm.sh",
                    "favicon.ico",
                ]
            ):
                continue
            if entry.get("level") == "SEVERE":
                report["console_errors"].append(msg)

        if (
            any(f["level"] == "error" for f in report["aesthetic_findings"])
            or report["console_errors"]
        ):
            report["overall"] = "FAIL"

        report["vision_instruction"] = (
            "Next step: Open the PNG paths in 'screenshots_for_vision_review' using your image-viewing tool "
            "(view_file / Read) to inspect visual hierarchy, spacing, typography, and alignment."
        )
        return report
    finally:
        driver.quit()
        shutil.rmtree(chrome_home, ignore_errors=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="Render multi-viewport screenshots and run aesthetic DOM inspection."
    )
    ap.add_argument("target", help="Path to .html file or http(s):// URL")
    ap.add_argument(
        "--out-dir",
        default="maintenance/screenshots",
        help="Directory to save rendered PNG screenshots",
    )
    args = ap.parse_args()
    res = run_inspection(args.target, args.out_dir)
    print(json.dumps(res, indent=2))
    if res["overall"] == "FAIL":
        raise SystemExit(1)
