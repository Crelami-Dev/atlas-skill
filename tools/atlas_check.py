#!/usr/bin/env python3
"""ATLAS quality gate.

Static checks (stdlib only) always run. Browser checks run only when Playwright and a
Chromium build are available; otherwise they are listed under "skipped" and never
reported as passed.

Severity:
  fail  objectively detectable defect
  warn  heuristic; needs human judgement
  info  informational

Usage:
  python3 scripts/atlas_check.py page.html --type marketing|editorial|app [--browser] [--json out.json] [--strict]
"""
import argparse, json, os, re, sys
from html.parser import HTMLParser

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
PLACEHOLDER_RE = re.compile(r"lorem ipsum|dolor sit amet|your text here|company name|john doe|item \d\b|\bTODO\b|\bTBD\b", re.I)
MARKER_RE = re.compile(r"<!--\s*(GANTI|REPLACE|KONFIRMASI|CONFIRM)\b[^>]*-->", re.I)
VIEWPORTS = {"mobile": (390, 844), "tablet": (768, 1024), "desktop": (1440, 900)}


class Node:
    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.parent = tag, dict(attrs), parent
        self.children, self.text = [], []

    def iter(self):
        yield self
        for c in self.children:
            yield from c.iter()

    def own_text(self):
        return " ".join("".join(self.text).split())

    def all_text(self):
        return " ".join(" ".join(n.own_text() for n in self.iter()).split())

    def has_ancestor(self, tag):
        n = self.parent
        while n:
            if n.tag == tag:
                return True
            n = n.parent
        return False


class DOM(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", [], None)
        self.cur = self.root
        self.style_text, self.script_text = [], []
        self._raw = None

    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs, self.cur)
        self.cur.children.append(n)
        if tag in ("style", "script"):
            self._raw = tag
        if tag not in VOID:
            self.cur = n

    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(Node(tag, attrs, self.cur))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        n = self.cur
        while n and n.tag != tag:
            n = n.parent
        if n and n.parent:
            self.cur = n.parent
        if tag in ("style", "script"):
            self._raw = None

    def handle_data(self, data):
        if self._raw == "style":
            self.style_text.append(data)
        elif self._raw == "script":
            self.script_text.append(data)
        elif self.cur.tag not in ("style", "script"):
            self.cur.text.append(data)


def parse(html):
    d = DOM()
    d.feed(html)
    d.close()
    return d


def accessible_name(n):
    a = n.attrs
    if a.get("aria-label", "").strip() or a.get("aria-labelledby") or a.get("title", "").strip():
        return True
    if n.all_text():
        return True
    for c in n.iter():
        if c.tag == "img" and c.attrs.get("alt", "").strip():
            return True
        if c.tag == "svg" and (c.attrs.get("aria-label") or any(x.tag == "title" for x in c.iter())):
            return True
    if n.tag == "input" and a.get("type") in ("submit", "button") and a.get("value"):
        return True
    return False


def static_checks(html, path, page_type):
    out, run = [], []
    dom = parse(html)
    nodes = list(dom.root.iter())
    css = "\n".join(dom.style_text)
    base = os.path.dirname(os.path.abspath(path)) if path else "."

    def add(id, sev, msg, where=""):
        out.append({"id": id, "severity": sev, "message": msg, "where": where})

    # document
    run += ["S001", "S002", "S003"]
    htmls = [n for n in nodes if n.tag == "html"]
    if not htmls or not htmls[0].attrs.get("lang"):
        add("S001", "fail", "<html> has no lang attribute")
    titles = [n for n in nodes if n.tag == "title"]
    if not titles or not titles[0].all_text():
        add("S002", "fail", "Missing or empty <title>")
    if not any(n.tag == "meta" and n.attrs.get("name") == "viewport" for n in nodes):
        add("S003", "fail", "Missing viewport meta tag")

    # headings
    run += ["S010", "S011"]
    heads = [n for n in nodes if re.fullmatch(r"h[1-6]", n.tag)]
    h1 = [h for h in heads if h.tag == "h1"]
    if page_type == "app":
        if len(h1) > 1:
            add("S010", "fail", "More than one <h1> (%d)" % len(h1))
        elif not heads:
            add("S010", "warn", "App screen has no headings")
    else:
        if len(h1) != 1:
            add("S010", "fail", "Expected exactly one <h1>, found %d" % len(h1))
    last = 0
    for h in heads:
        lvl = int(h.tag[1])
        if last and lvl > last + 1:
            add("S011", "warn", "Heading level skips from h%d to h%d" % (last, lvl), h.all_text()[:50])
        last = lvl

    # images, links
    run += ["S020", "S021", "S022", "S090"]
    ids = [n.attrs["id"] for n in nodes if "id" in n.attrs]
    for n in nodes:
        if n.tag == "img":
            if "alt" not in n.attrs:
                add("S020", "fail", "<img> without alt attribute", n.attrs.get("src", "")[:60])
            src = n.attrs.get("src", "")
            if src and not re.match(r"(https?:|data:|//|#)", src):
                if not os.path.exists(os.path.join(base, src.split("?")[0].split("#")[0])):
                    add("S021", "fail", "Missing local image file", src)
            if not (n.attrs.get("width") and n.attrs.get("height")) and "aspect-ratio" not in css:
                add("S090", "warn", "<img> without width/height (layout shift risk)", src[:60])
        if n.tag == "a":
            href = n.attrs.get("href")
            if href is None:
                continue
            if href == "#":
                add("S022", "warn", "Link with empty '#' target", n.all_text()[:40])
            elif href.startswith("#"):
                if href[1:] not in ids:
                    add("S022", "fail", "Anchor target does not exist", href)
            elif not re.match(r"(https?:|mailto:|tel:|//|javascript:|data:)", href):
                if not os.path.exists(os.path.join(base, href.split("#")[0].split("?")[0])):
                    add("S022", "fail", "Link to missing local file", href)

    # names / labels
    run += ["S030", "S031"]
    labels_for = {n.attrs["for"] for n in nodes if n.tag == "label" and "for" in n.attrs}
    for n in nodes:
        if n.tag in ("input", "select", "textarea"):
            t = n.attrs.get("type", "text")
            if t in ("hidden", "submit", "button", "reset", "image"):
                continue
            if n.attrs.get("aria-label") or n.attrs.get("aria-labelledby") or n.attrs.get("title"):
                continue
            if n.attrs.get("id") in labels_for or n.has_ancestor("label"):
                continue
            add("S030", "fail", "Form control without an associated label", n.attrs.get("name", n.attrs.get("id", n.tag)))
        if n.tag == "button" or (n.tag == "a" and "href" in n.attrs):
            if not accessible_name(n):
                add("S031", "fail", "%s without accessible name" % n.tag, str(n.attrs)[:60])

    # ids
    run.append("S040")
    seen = set()
    for i in ids:
        if i in seen:
            add("S040", "fail", "Duplicate id", i)
        seen.add(i)

    # placeholders / emptiness
    run += ["S050", "S051", "S052"]
    visible = " ".join(n.own_text() for n in nodes if n.tag not in ("style", "script", "title"))
    m = PLACEHOLDER_RE.search(visible)
    if m:
        add("S050", "fail", "Placeholder text found", m.group(0))
    markers = MARKER_RE.findall(html)
    if markers:
        add("S052", "info", "%d marked placeholder(s) pending (GANTI/KONFIRMASI)" % len(markers))
    for n in nodes:
        if n.tag in ("section", "article") and not n.all_text():
            media = any(c.tag in ("img", "svg", "canvas", "video", "iframe", "input", "picture") for c in n.iter())
            if not media:
                add("S051", "fail", "Empty <%s>" % n.tag, n.attrs.get("id", ""))

    # css / motion / focus
    run += ["S060", "S061", "S062", "S063", "S070"]
    for n in nodes:
        try:
            if int(n.attrs.get("tabindex", "0")) > 0:
                add("S060", "fail", "Positive tabindex", str(n.attrs)[:60])
        except ValueError:
            pass
    if re.search(r"transition\s*:\s*all\b", css):
        add("S061", "warn", "transition: all (animate specific properties)")
    if re.search(r"outline\s*:\s*(none|0)\b", css) and not re.search(r":focus-visible", css):
        add("S062", "warn", "outline removed without a :focus-visible style")
    if re.search(r"@keyframes|transition\s*:|animation\s*:", css) and "prefers-reduced-motion" not in css:
        add("S063", "fail", "Motion in CSS but no prefers-reduced-motion handling")
    big = sum(len(x) for x in re.findall(r"data:[a-z/+\-]+;base64,[A-Za-z0-9+/=]{1000,}", html))
    if big > 200_000:
        add("S070", "warn", "Inline base64 assets total %d KB" % (big // 1024))
    return out, run


BROWSER_JS_LAYOUT = r"""
() => {
  const vw = document.documentElement.clientWidth;
  const res = {scrollW: document.documentElement.scrollWidth, vw, leaks: [], small: [], tiny: [],
               pageH: document.documentElement.scrollHeight};
  const inScroller = el => { let p = el.parentElement; while (p && p !== document.body) {
      const o = getComputedStyle(p).overflowX; if (o === 'auto' || o === 'scroll' || o === 'hidden') return true; p = p.parentElement; } return false; };
  for (const el of document.querySelectorAll('body *')) {
    const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const r = el.getBoundingClientRect(); if (!r.width || !r.height) continue;
    if (r.right > vw + 1 && !inScroller(el) && cs.position !== 'fixed') res.leaks.push(el.tagName.toLowerCase() + '.' + [...el.classList].join('.'));
    const interactive = el.matches('a[href],button,input:not([type=hidden]),select,textarea,summary,[role=button],[role=tab]');
    if (interactive && (r.width < 44 || r.height < 44)) {
      const inline = el.tagName === 'A' && cs.display === 'inline';
      if (!inline) res.small.push(el.tagName.toLowerCase() + ':' + (el.textContent || el.getAttribute('aria-label') || '').trim().slice(0, 24) + ' ' + Math.round(r.width) + 'x' + Math.round(r.height));
    }
    const fs = parseFloat(cs.fontSize);
    if (fs < 12 && [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) res.tiny.push(el.tagName.toLowerCase() + ' ' + fs + 'px');
  }
  return res;
}
"""

BROWSER_JS_CONTRAST = r"""
() => {
  const parse = c => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(',').map(s => parseFloat(s)); return {r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1}; };
  const lum = c => { const f = v => { v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }; return .2126 * f(c.r) + .7152 * f(c.g) + .0722 * f(c.b); };
  const blend = (top, bot) => ({r: top.r * top.a + bot.r * (1 - top.a), g: top.g * top.a + bot.g * (1 - top.a), b: top.b * top.a + bot.b * (1 - top.a), a: 1});
  const bgOf = el => { const layers = []; let p = el;
    while (p) { const cs = getComputedStyle(p); if (cs.backgroundImage !== 'none') return null;
      const c = parse(cs.backgroundColor); if (c && c.a > 0) { layers.push(c); if (c.a === 1) break; } p = p.parentElement; }
    let base = {r: 255, g: 255, b: 255, a: 1}; for (let i = layers.length - 1; i >= 0; i--) base = blend(layers[i], base); return base; };
  const bad = [], skipped = {n: 0}; let measured = 0;
  for (const el of document.querySelectorAll('body *')) {
    const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    if (![...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) continue;
    const r = el.getBoundingClientRect(); if (!r.width || !r.height) continue;
    const fg = parse(cs.color); const bg = bgOf(el); if (!fg || !bg) { skipped.n++; continue; }
    const f = blend(fg, bg); const L1 = lum(f), L2 = lum(bg); const ratio = (Math.max(L1, L2) + .05) / (Math.min(L1, L2) + .05);
    const size = parseFloat(cs.fontSize), bold = parseInt(cs.fontWeight) >= 700; const large = size >= 24 || (size >= 18.66 && bold);
    measured++; if (ratio < (large ? 3 : 4.5)) bad.push(el.tagName.toLowerCase() + ' "' + el.textContent.trim().slice(0, 24) + '" ' + ratio.toFixed(2) + ':1');
  }
  return {bad, measured, unmeasurable: skipped.n};
}
"""

BROWSER_JS_HIDDEN = r"""
() => {
  const out = [];
  for (const el of document.querySelectorAll('body *')) {
    if (!(el.childNodes && [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()))) continue;
    if (el.closest('[hidden],[aria-hidden="true"],dialog:not([open]),template')) continue;
    let p = el, skip = false;
    while (p) { const cs = getComputedStyle(p); if (cs.display === 'none') { skip = true; break; } p = p.parentElement; }
    if (skip) continue;
    let op = 1, q = el; while (q) { op *= parseFloat(getComputedStyle(q).opacity); q = q.parentElement; }
    const cs = getComputedStyle(el);
    if (op < 0.05 || cs.visibility === 'hidden') out.push(el.tagName.toLowerCase() + ' "' + el.textContent.trim().slice(0, 30) + '"');
  }
  return out;
}
"""

BROWSER_JS_LAYOUT_ALIGN = r"""
() => {
  const rows = [];
  for (const s of document.querySelectorAll('main > section, body > section')) {
    if (s.hasAttribute('data-bleed')) continue;
    const t = s.querySelector('h1,h2,h3,p'); if (!t) continue;
    let carded = false, q = t.parentElement;
    while (q && q !== s) { const c = getComputedStyle(q).backgroundColor; if (c !== 'rgba(0, 0, 0, 0)' && c !== 'transparent') { carded = true; break; } q = q.parentElement; }
    if (carded) continue;   // text sits inside a padded card/panel by design
    const r = t.getBoundingClientRect(); if (r.width) rows.push({id: s.id || s.className || 'section', left: Math.round(r.left)});
  }
  return rows;
}
"""


def have_browser():
    try:
        from playwright.sync_api import sync_playwright  # noqa
    except Exception as e:
        return False, "playwright not importable: %s" % e
    return True, ""


def browser_checks(url, page_type, shots_dir=None):
    from playwright.sync_api import sync_playwright
    out, run, skipped = [], [], []

    def add(id, sev, msg, vp="", where=""):
        out.append({"id": id, "severity": sev, "message": msg, "viewport": vp, "where": where})

    with sync_playwright() as pw:
        try:
            browser = pw.chromium.launch()
        except Exception as e:
            return [], [], ["browser launch failed: %s" % str(e)[:120]]
        for name, (w, h) in VIEWPORTS.items():
            ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1, has_touch=(name == "mobile"))
            page = ctx.new_page()
            errors, failed = [], []
            page.on("console", lambda m, e=errors: e.append(m.text) if m.type == "error" else None)
            page.on("pageerror", lambda ex, e=errors: e.append(str(ex)))
            page.on("requestfailed", lambda r, f=failed: f.append(r.url))
            page.goto(url, wait_until="load")
            page.add_style_tag(content="html{scroll-behavior:auto !important}")  # deterministic scrolling
            page.wait_for_timeout(400)
            run += ["B001", "B002", "B003", "B004", "B010", "B020", "B021"]
            lay = page.evaluate(BROWSER_JS_LAYOUT)
            if lay["scrollW"] > lay["vw"] + 1:
                add("B001", "fail", "Horizontal overflow: scrollWidth %d > viewport %d" % (lay["scrollW"], lay["vw"]), name)
            if lay["leaks"]:
                add("B002", "warn", "Elements extend past the right edge: " + "; ".join(lay["leaks"][:4]), name)
            if name == "mobile" and lay["small"]:
                add("B020", "warn", "%d tap target(s) under 44px, e.g. %s" % (len(lay["small"]), "; ".join(lay["small"][:3])), name)
            if lay["tiny"]:
                add("B021", "warn", "Text under 12px: " + "; ".join(lay["tiny"][:3]), name)
            for e in errors:
                add("B003", "fail", "Console/page error: " + e[:140], name)
            for u in failed:
                local = u.startswith("file:") or "localhost" in u or "127.0.0.1" in u
                add("B004", "fail" if local else "warn", "Failed request: " + u[:120], name)
            con = page.evaluate(BROWSER_JS_CONTRAST)
            for b in con["bad"][:8]:
                add("B010", "fail", "Contrast below WCAG AA: " + b, name)
            out.append({"id": "B010", "severity": "info", "viewport": name, "where": "",
                        "message": "contrast measured on %d text elements; %d unmeasurable (background image/gradient)" % (con["measured"], con["unmeasurable"])})
            if page_type != "app":
                run.append("B030")
                vis = page.evaluate("""() => { const h = document.querySelector('h1'); if (!h) return null; const r = h.getBoundingClientRect();
                  return {top: r.top, bottom: r.bottom, vh: innerHeight}; }""")
                if vis and not (vis["top"] >= 0 and vis["bottom"] <= vis["vh"]):
                    add("B030", "warn", "<h1> not fully visible in the first screen", name)
            if page_type == "marketing":
                run.append("B031")
                cta = page.evaluate("""() => { const els = [...document.querySelectorAll('main a[href],main button,header a[href].btn,a.btn,button')];
                  return els.some(e => { const r = e.getBoundingClientRect(); const cs = getComputedStyle(e); return r.width > 0 && r.top >= 0 && r.bottom <= innerHeight && cs.display !== 'none'; }); }""")
                if not cta:
                    add("B031", "warn", "No call to action visible in the first screen", name)
            if name == "desktop":
                run.append("B040")
                rows = page.evaluate(BROWSER_JS_LAYOUT_ALIGN)
                if len(rows) >= 3:
                    lefts = sorted(r["left"] for r in rows)
                    mode = max(set(lefts), key=lefts.count)
                    odd = [r for r in rows if abs(r["left"] - mode) > 12]
                    if odd:
                        add("B040", "warn", "Content left edge differs from the common edge (%dpx) in: %s" % (mode, ", ".join("%s@%d" % (o["id"], o["left"]) for o in odd[:5])), name)
            # reveal-on-scroll and hidden content
            run.append("B050")
            height = page.evaluate("document.documentElement.scrollHeight")
            y = 0
            while y < height:
                page.evaluate("window.scrollTo(0, %d)" % y); page.wait_for_timeout(60); y += max(h - 100, 200)
            page.wait_for_timeout(1400)  # let reveal transitions finish before judging visibility
            hid = page.evaluate(BROWSER_JS_HIDDEN)
            if hid:
                add("B050", "fail", "Content stuck invisible after scrolling: " + "; ".join(hid[:4]), name)
            page.evaluate("window.scrollTo(0,0)"); page.wait_for_timeout(300)
            if shots_dir:
                os.makedirs(shots_dir, exist_ok=True)
                page.screenshot(path=os.path.join(shots_dir, "%s-%d.png" % (name, w)), full_page=True)
            out.append({"id": "B070", "severity": "info", "viewport": name, "where": "",
                        "message": "page height %d px = %.1f screens" % (lay["pageH"], lay["pageH"] / h)})
            ctx.close()
        # reduced motion
        ctx = browser.new_context(viewport={"width": 390, "height": 844}, reduced_motion="reduce")
        page = ctx.new_page(); page.goto(url, wait_until="load"); page.wait_for_timeout(500)
        run.append("B051")
        hid = page.evaluate(BROWSER_JS_HIDDEN)
        if hid:
            add("B051", "fail", "With reduced motion, content is invisible before any scroll/animation: " + "; ".join(hid[:4]), "mobile-reduced")
        inf = page.evaluate("document.getAnimations().filter(a => a.effect && a.effect.getTiming().iterations === Infinity && a.playState === 'running').length")
        if inf:
            add("B051", "warn", "%d infinite animation(s) still running under reduced motion" % inf, "mobile-reduced")
        ctx.close()
        # keyboard + mobile nav
        for name in ("desktop", "mobile"):
            w, h = VIEWPORTS[name]
            ctx = browser.new_context(viewport={"width": w, "height": h}); page = ctx.new_page()
            page.goto(url, wait_until="load"); page.wait_for_timeout(300)
            run.append("B060")
            reached, noring, hidden_focus = 0, [], []
            for _ in range(45):
                page.keyboard.press("Tab")
                info = page.evaluate("""() => { const e = document.activeElement; if (!e || e === document.body) return null;
                  const r = e.getBoundingClientRect(); const cs = getComputedStyle(e);
                  const ring = (cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) > 0) || cs.boxShadow !== 'none';
                  const vis = r.width > 0 && r.height > 0 && cs.visibility !== 'hidden';
                  return {label: (e.textContent || e.getAttribute('aria-label') || e.tagName).trim().slice(0, 24), ring, vis}; }""")
                if info:
                    reached += 1
                    if not info["vis"]: hidden_focus.append(info["label"])
                    elif not info["ring"]: noring.append(info["label"])
            if reached == 0:
                add("B060", "fail", "Keyboard Tab reaches no focusable element", name)
            if noring:
                add("B060", "warn", "No visible focus indicator on: " + "; ".join(sorted(set(noring))[:4]), name)
            if hidden_focus:
                add("B060", "warn", "Focus lands on invisible elements: " + "; ".join(sorted(set(hidden_focus))[:4]), name)
            if name == "mobile":
                run.append("B061")
                tog = page.query_selector("button[aria-controls][aria-expanded]")
                navlinks_hidden = page.evaluate("""() => { const n = document.querySelector('header nav, nav'); if (!n) return false;
                  const links = [...n.querySelectorAll('a[href]')]; return links.length > 0 && links.every(a => a.getBoundingClientRect().width === 0); }""")
                if tog and tog.is_visible():
                    tog.click(); page.wait_for_timeout(350)
                    opened = tog.get_attribute("aria-expanded") == "true"
                    page.keyboard.press("Escape"); page.wait_for_timeout(350)
                    closed = tog.get_attribute("aria-expanded") == "false"
                    if not opened: add("B061", "fail", "Menu toggle does not set aria-expanded=true on open", name)
                    if not closed: add("B061", "fail", "Escape does not close the mobile menu", name)
                elif navlinks_hidden:
                    add("B061", "fail", "Navigation links are hidden on mobile and no menu toggle exists", name)
            ctx.close()
        browser.close()
    return out, run, skipped


def run_all(path, page_type, use_browser, shots_dir=None):
    with open(path, encoding="utf-8") as f:
        html = f.read()
    res, checks = static_checks(html, path, page_type)
    skipped = []
    if use_browser:
        ok, why = have_browser()
        if ok:
            b, r, s = browser_checks("file://" + os.path.abspath(path), page_type, shots_dir)
            res += b; checks += r; skipped += s
        else:
            skipped.append("browser checks: " + why)
    else:
        skipped.append("browser checks: not requested (--browser)")
    for s in skipped:
        res.append({"id": "SKIP", "severity": "info", "message": s, "where": ""})
    summary = {k: sum(1 for x in res if x["severity"] == k) for k in ("fail", "warn", "info")}
    return {"file": path, "page_type": page_type, "checks_run": sorted(set(checks)), "skipped": skipped,
            "summary": summary, "results": res}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file"); ap.add_argument("--type", default="marketing", choices=["marketing", "editorial", "app"])
    ap.add_argument("--browser", action="store_true"); ap.add_argument("--json")
    ap.add_argument("--shots", help="directory for viewport screenshots (needs --browser)")
    ap.add_argument("--strict", action="store_true", help="treat pending GANTI/KONFIRMASI markers as failures")
    a = ap.parse_args(argv)
    rep = run_all(a.file, a.type, a.browser, a.shots)
    if a.strict and any(r["id"] == "S052" for r in rep["results"]):
        rep["summary"]["fail"] += 1
        rep["results"].append({"id": "STRICT", "severity": "fail", "message": "Pending placeholder markers in strict mode", "where": ""})
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(rep, f, indent=1, ensure_ascii=False)
    for r in rep["results"]:
        if r["severity"] == "info" and r["id"] not in ("SKIP", "S052", "B070") and "contrast measured" not in r["message"]:
            continue
        print("[%s] %s %s%s %s" % (r["severity"].upper(), r["id"], ("(" + r["viewport"] + ") ") if r.get("viewport") else "", r["message"], ("| " + r["where"]) if r.get("where") else ""))
    print("checks executed:", ", ".join(rep["checks_run"]))
    print("summary:", rep["summary"])
    return 1 if rep["summary"]["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
