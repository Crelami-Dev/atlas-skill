#!/usr/bin/env node
/**
 * Atlas-Skill quick-check.mjs (v4)
 * Deep multi-viewport browser audit:
 * - Overflow, broken media, console/page errors, placeholder residue
 * - Post-scroll reveal check (ensures zero visible sections/cards stuck at opacity: 0)
 * - Limited flat-background contrast on headings, paragraphs, buttons & links
 * - Unintentional sibling overlap + line-length measure (>78ch) + mobile tap targets
 * - Mobile navigation completeness (links hidden with no menu control), dead space inside sections,
 *   and elements stuck translucent after their reveal should have finished
 * - Optional visible menu/tab smoke checks, with explicit skipped state
 * - Full-resolution 1:1 captures for top, mid-scroll, low-scroll & full-page folds
 */
import fs from "node:fs";
import path from "node:path";
import http from "node:http";
import { launchBrowser } from "./browser-runtime.mjs";

const VIEWPORTS = [
  { name: "320-short", width: 320, height: 568, folds: false },
  { name: "375-short", width: 375, height: 667, folds: false },
  { name: "320", width: 320, height: 740, folds: false },
  { name: "360", width: 360, height: 800, folds: true },
  { name: "375", width: 375, height: 812, folds: false },
  { name: "390", width: 390, height: 844, folds: false },
  { name: "600", width: 600, height: 960, folds: false },
  { name: "768", width: 768, height: 1024, folds: false },
  { name: "820", width: 820, height: 1180, folds: false },
  { name: "1366", width: 1366, height: 768, folds: true },
  { name: "1440", width: 1440, height: 900, folds: true },
];

const MIME_TYPES = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".mjs": "application/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp",
  ".woff2": "font/woff2",
};

const SLOP_PHRASES = [
  "solusi komprehensif",
  "era digital",
  "mengubah cara anda",
  "transformasi bisnis",
  "inovasi terdepan",
  "next-gen",
  "game-changing",
  "revolutionary",
  "elevate your",
  "streamline your workflow",
  "seamlessly",
  "empowering teams",
];

function usageError(message) {
  return Object.assign(new Error(message), { exitCode: 2 });
}

function parseArgs(argv) {
  const args = argv.slice(2);
  const options = { target: "", shotsDir: "maintenance/browser", verifyClicks: false, heroSelector: "", heroActionSelector: "", fitHeroUnder: 420, help: false };
  const values = { "--shots": "shotsDir", "--hero": "heroSelector", "--hero-action": "heroActionSelector", "--fit-hero-under": "fitHeroUnder" };
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === "--help") options.help = true;
    else if (arg === "--click-test") options.verifyClicks = true;
    else if (arg === "--no-click-test") options.verifyClicks = false;
    else if (values[arg]) {
      if (!args[i + 1] || args[i + 1].startsWith("--")) throw usageError("Missing value for " + arg);
      options[values[arg]] = args[++i];
    } else if (arg.startsWith("--")) throw usageError("Unknown option: " + arg);
    else if (!options.target) options.target = arg;
    else throw usageError("Only one target URL or path is supported.");
  }
  options.fitHeroUnder = Number(options.fitHeroUnder);
  if (!Number.isFinite(options.fitHeroUnder) || options.fitHeroUnder <= 0) throw usageError("--fit-hero-under must be a positive width.");
  if (Boolean(options.heroSelector) !== Boolean(options.heroActionSelector)) throw usageError("Supply both --hero and --hero-action.");
  return options;
}

function startStaticServer(targetPath) {
  const abs = path.resolve(targetPath);
  const stat = fs.statSync(abs);
  const rootDir = stat.isDirectory() ? abs : path.dirname(abs);
  const defaultFile = stat.isDirectory() ? "index.html" : path.basename(abs);
  const server = http.createServer((req, res) => {
    const cleanUrl = (req.url || "/").split("?")[0];
    let decoded;
    try { decoded = decodeURIComponent(cleanUrl); } catch { res.writeHead(400).end("Invalid path encoding"); return; }
    const relPath = decoded === "/" ? defaultFile : decoded.replace(/^\/+/, "");
    const resolved = path.resolve(rootDir, relPath);
    if (path.relative(rootDir, resolved).startsWith("..") || path.isAbsolute(path.relative(rootDir, resolved)) || !fs.existsSync(resolved) || fs.statSync(resolved).isDirectory()) {
      res.writeHead(404).end("Not found");
      return;
    }
    const ext = path.extname(resolved).toLowerCase();
    res.writeHead(200, { "Content-Type": MIME_TYPES[ext] || "application/octet-stream" });
    fs.createReadStream(resolved).pipe(res);
  });
  return new Promise((resolve) => {
    server.listen(0, "127.0.0.1", () => {
      resolve({ server, url: `http://127.0.0.1:${server.address().port}/` });
    });
  });
}

// Elements fully inside the viewport that stay translucent after their reveal should have finished.
// Catches reveals that never complete (washed-out sections in screenshots and for visitors).
async function settledOpacityProbe(page) {
  return page.evaluate(() => {
    const out = [];
    const sel = "main h1, main h2, main h3, main p, main figure, main img, main form, [data-reveal]";
    for (const el of document.querySelectorAll(sel)) {
      if (el.closest("[data-atlas-scene]")) continue;
      const r = el.getBoundingClientRect();
      if (r.width < 8 || r.height < 8 || r.top < 0 || r.bottom > innerHeight) continue;
      let o = 1;
      for (let n = el; n; n = n.parentElement) o *= parseFloat(getComputedStyle(n).opacity);
      if (o > 0.05 && o < 0.8) out.push(`${el.tagName.toLowerCase()}("${(el.innerText || el.alt || "").trim().slice(0, 18)}")=${o.toFixed(2)}`);
    }
    return out;
  });
}

async function scrollSweepAndCapture(page, vp, shotsDir) {
  const sweepWarns = [];
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: "instant" }));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(700);
  if (shotsDir) {
    fs.mkdirSync(shotsDir, { recursive: true });
    await page.screenshot({ path: path.join(shotsDir, `${vp.name}.png`), fullPage: false });
  }

  const maxScroll = await page.evaluate(() => Math.max(0, document.documentElement.scrollHeight - window.innerHeight));
  // Visit every fold; jumping over sections otherwise produces false stuck-reveal failures.
  for (let y = 0; y <= maxScroll; y += Math.max(200, vp.height * 0.7)) {
    await page.evaluate((offset) => window.scrollTo({ top: offset, behavior: "instant" }), y);
    await page.waitForTimeout(100);
  }
  await page.waitForTimeout(700);
  const midY = Math.round(maxScroll * 0.45);
  const lowY = Math.round(maxScroll * 0.88);

  if (maxScroll > 120) {
    await page.evaluate((y) => window.scrollTo({ top: y, behavior: "instant" }), midY);
    await page.waitForTimeout(680);
    if (vp.folds) {
      await page.waitForTimeout(1300);
      const stuck = await settledOpacityProbe(page);
      if (stuck.length) sweepWarns.push(`partial-opacity: ${stuck.length} elements still translucent 2s after reveal at mid-scroll (${stuck.slice(0, 3).join(", ")})`);
    }
    if (shotsDir && vp.folds) {
      await page.screenshot({ path: path.join(shotsDir, `${vp.name}-mid.png`), fullPage: false });
    }

    await page.evaluate((y) => window.scrollTo({ top: y, behavior: "instant" }), lowY);
    await page.waitForTimeout(680);
    if (vp.folds) {
      await page.waitForTimeout(1300);
      const stuck = await settledOpacityProbe(page);
      if (stuck.length) sweepWarns.push(`partial-opacity: ${stuck.length} elements still translucent 2s after reveal at low-scroll (${stuck.slice(0, 3).join(", ")})`);
    }
    if (shotsDir && vp.folds) {
      await page.screenshot({ path: path.join(shotsDir, `${vp.name}-low.png`), fullPage: false });
    }
  }

  if (shotsDir && vp.folds) {
    await page.evaluate(() => window.scrollTo({ top: 0, behavior: "instant" }));
    await page.waitForTimeout(200);
    await page.screenshot({ path: path.join(shotsDir, `${vp.name}-full.png`), fullPage: true });
  }
  return sweepWarns;
}

async function auditViewport(page, vp, shotsDir, slopPhrases, options) {
  await page.setViewportSize({ width: vp.width, height: vp.height });
  const sweepWarns = await scrollSweepAndCapture(page, vp, shotsDir);
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: "instant" }));
  await page.waitForTimeout(100);

  const audit = await page.evaluate(({ vpWidth, slopList, heroSelector, heroActionSelector, fitHeroUnder }) => {
    const fails = [];
    const warns = [];

    const metrics = { contrastChecked: 0, contrastSkipped: 0, hero: null };
    if (heroSelector && vpWidth <= fitHeroUnder) {
      const heroes = document.querySelectorAll(heroSelector);
      const actions = document.querySelectorAll(heroActionSelector);
      if (heroes.length !== 1 || actions.length !== 1) {
        fails.push(`hero-selectors: expected exactly one hero and action, found ${heroes.length}/${actions.length}`);
      } else {
        const hero = heroes[0], action = actions[0];
        const h = hero.getBoundingClientRect(), a = action.getBoundingClientRect();
        const visible = el => {
          const r = el.getBoundingClientRect();
          if (r.width <= 0 || r.height <= 0) return false;
          for (let n = el; n; n = n.parentElement) {
            const s = getComputedStyle(n);
            if (n.hidden || s.display === "none" || s.visibility === "hidden" || Number(s.opacity) <= 0.05) return false;
          }
          return true;
        };
        metrics.hero = { top: h.top, bottom: h.bottom, height: h.height, actionTop: a.top, actionBottom: a.bottom, actionHeight: a.height, actionVisible: visible(action) };
        if (!visible(hero) || !visible(action)) fails.push("hero-visibility: hero or actual action is hidden/zero-sized");
        if (h.bottom > innerHeight + 1 || h.top < -1) fails.push("hero-fit: header plus hero exceeds the requested first screen");
        if (a.top < 0 || a.bottom > innerHeight + 1 || a.height < 44) fails.push("hero-action-fit: actual primary action is clipped, below fold or under 44px high");
      }
    }


    const docOverflow = document.documentElement.scrollWidth - window.innerWidth;
    if (docOverflow > 1) {
      fails.push(`overflow: scrollWidth exceeds viewport by ${docOverflow}px`);
    }

    const brokenImages = [...document.querySelectorAll("img")].filter(
      (img) => img.offsetParent !== null && (!img.complete || img.naturalWidth === 0),
    );
    if (brokenImages.length > 0) {
      fails.push(`broken-images: ${brokenImages.length} unloaded img elements`);
    }

    const bodyText = (document.body.innerText || "").trim();
    const lowerText = bodyText.toLowerCase();
    if (/\btodo:|\blorem ipsum\b|\[company|\btbd\b/i.test(bodyText)) {
      fails.push("placeholder-residue: found TODO / Lorem / Placeholder / TBD in visible text");
    }
    const photoLeak = bodyText.match(/(?:\b(?:ganti(?:\s+dengan)?\s+(?:foto|gambar)(?:\s+(?:asli|ini))?|replace\s+(?:this\s+)?(?:with\s+)?(?:real\s+|actual\s+)?(?:photo|image)|(?:insert|upload)\s+(?:real\s+)?(?:photo|image)(?:\s+here)?|(?:taruh|masukkan|pasang)\s+(?:foto|gambar)\s+(?:di\s+sini|disini)|menunggu\s+foto(?:\s+dokumentasi|\s+asli|\s+klien)?|foto\s+menyusul|awaiting\s+(?:real\s+|client\s+)?photo(?:graphy|s)?|(?:photo|image)\s+(?:coming\s+soon|tbd)|(?:slot\s+foto|photo\s+slot)\s*(?:#?\d+|hero|utama|banner|produk|menu|galeri)|(?:image|photo|foto)\s+placeholder|placeholder\s+(?:image|photo|foto)|data\s+klien\s+diperlukan)\b|\[\s*(?:ganti\s+dengan\s+foto|replace\s+with\s+photo|insert\s+image|placeholder|data\s+klien\s+diperlukan|(?:foto|image)\s*:[^\]]+|foto[^\]]{0,40}di\s+sini)[^\]]*\])/i);
    if (photoLeak) {
      fails.push(`leaked-photo-placeholder-ui: visible developer/placeholder instruction "${photoLeak[0]}"`);
    }

    // Stuck opacity:0 check after scrolling top -> mid -> low -> top
    const stuckHidden = [...document.querySelectorAll("section, article, h1, h2, h3, [data-reveal]")].filter((el) => {
      const st = getComputedStyle(el);
      if (st.display === "none" || st.visibility === "hidden") return false;
      const r = el.getBoundingClientRect();
      return r.height > 8 && r.width > 8 && parseFloat(st.opacity) <= 0.05;
    });
    if (stuckHidden.length > 0) {
      fails.push(`stuck-opacity: ${stuckHidden.length} elements remain effectively invisible (opacity <= 0.05) after scroll`);
    }

    // Mobile tap target size check (ignores hidden/nav collapsed drawers)
    const tinyButtons = [...document.querySelectorAll("a, button, input, select, textarea, summary")].filter((el) => {
      const style = getComputedStyle(el);
      if (style.display === "none" || style.visibility === "hidden" || el.offsetParent === null) return false;
      const r = el.getBoundingClientRect();
      return r.width > 0 && r.height > 0 && (r.height < 44 || r.width < 44) && el.closest("header, main, footer, nav");
    });
    if (tinyButtons.length > 0 && vpWidth <= 420) {
      warns.push(`small-tap-target: ${tinyButtons.length} controls under Atlas comfort target 44px (not a WCAG conformance verdict) (${tinyButtons.slice(0, 3).map((e) => e.textContent.trim().slice(0, 20) || e.tagName).join(", ")})`);
    }

    // Mobile navigation completeness: section links must not vanish without a menu control.
    if (vpWidth <= 820) {
      const header = document.querySelector("header");
      if (header) {
        // Visible means on screen and opaque: a drawer parked off-canvas with a transform keeps a positive
        // size, so geometry alone would wrongly count its links as reachable.
        const shown = (el) => {
          const r = el.getBoundingClientRect();
          const s = getComputedStyle(el);
          if (r.width <= 0 || r.height <= 0 || s.display === "none" || s.visibility === "hidden") return false;
          if (r.right <= 0 || r.left >= innerWidth || r.bottom <= 0 || r.top >= innerHeight) return false;
          let opacity = 1;
          for (let n = el; n; n = n.parentElement) opacity *= parseFloat(getComputedStyle(n).opacity);
          return opacity > 0.05;
        };
        const navLinks = [...header.querySelectorAll("a[href]")].filter((a) => a.closest("nav") || /^\/?#./.test(a.getAttribute("href") || ""));
        const hiddenAll = navLinks.filter((a) => !shown(a));
        const destination = (a) => (a.getAttribute("href") || "").replace(/^\/(?=#)/, "").replace(/\/$/, "");
        const visibleDestinations = new Set(navLinks.filter(shown).map(destination));
        // Separate desktop and mobile markup is fine when a visible link reaches the same destination.
        const hiddenLinks = hiddenAll.filter((a) => !visibleDestinations.has(destination(a)));
        // A control only counts when it plausibly operates the hidden navigation, so an unrelated
        // button (theme switch, search) cannot mask a missing menu.
        const operatesNav = (control) => {
          const id = control.getAttribute("aria-controls");
          if (id) {
            const target = document.getElementById(id);
            return Boolean(target && hiddenAll.some((a) => target.contains(a) || a.contains(target)));
          }
          return control.hasAttribute("aria-expanded");
        };
        const hasToggle =
          [...header.querySelectorAll("button, [role=button]")].some((b) => shown(b) && operatesNav(b)) ||
          [...header.querySelectorAll("summary")].some((sm) => shown(sm) && hiddenAll.some((a) => sm.parentElement?.contains(a))) ||
          [...header.querySelectorAll("label[for]")].some((l) => shown(l) && /^(checkbox|radio)$/.test(document.getElementById(l.getAttribute("for"))?.type || ""));
        if (hiddenLinks.length >= 3 && !hasToggle) {
          fails.push(`mobile-nav-missing: ${hiddenLinks.length} header links are hidden at ${vpWidth}px with no visible menu control (${hiddenLinks.slice(0, 3).map((a) => a.textContent.trim().slice(0, 14)).join(", ")})`);
        } else if (hiddenLinks.length === 2 && !hasToggle) {
          warns.push("mobile-nav-missing: 2 header links are hidden on mobile with no menu control; confirm the content stays reachable");
        }
      }
    }

    // Unintentional dead space: a tall section whose content ends far above its own bottom edge.
    if (vpWidth >= 1200) {
      for (const sec of document.querySelectorAll("main section")) {
        const sr = sec.getBoundingClientRect();
        if (sr.height < innerHeight * 0.6 || sec.closest("[data-atlas-scene]") || sec.matches("[data-atlas-scene]")) continue;
        const all = [...sec.querySelectorAll("*")];
        if (all.some((c) => ["sticky", "fixed"].includes(getComputedStyle(c).position))) continue;
        let bottom = sr.top;
        for (const c of all) {
          const cs = getComputedStyle(c);
          if (cs.display === "none" || cs.visibility === "hidden" || cs.position === "absolute") continue;
          const cr = c.getBoundingClientRect();
          if (cr.width > 0 && cr.height > 0) bottom = Math.max(bottom, cr.bottom);
        }
        const trailing = sr.bottom - (parseFloat(getComputedStyle(sec).paddingBottom) || 0) - bottom;
        if (trailing > Math.max(160, innerHeight * 0.2)) {
          warns.push(`dead-space: section "${(sec.querySelector("h1, h2, h3")?.textContent || sec.id || "section").trim().slice(0, 24)}" ends ${Math.round(trailing)}px of empty space below its content`);
        }
      }
    }

    // Stacked calls to action on phones must share one width and left edge. Two buttons of different
    // widths, or a lone narrow button under a wide one, is the "odd CTA" that looks broken on mobile.
    if (vpWidth <= 540) {
      const groups = new Map();
      for (const el of document.querySelectorAll("main a, main button")) {
        if (!/(?:^|[\s_-])(?:btn|button|cta)/i.test(el.className) && !el.hasAttribute("data-cta-primary")) continue;
        const r = el.getBoundingClientRect();
        if (r.width <= 0 || r.height <= 0 || getComputedStyle(el).display === "none") continue;
        const key = el.parentElement;
        groups.set(key, [...(groups.get(key) || []), el]);
      }
      for (const kids of groups.values()) {
        if (kids.length < 2) continue;
        const rects = kids.map((k) => k.getBoundingClientRect());
        const stackedPairs = rects.slice(1).map((r, i) => ({ a: rects[i], b: r })).filter(({ a, b }) => b.top >= a.bottom - 2);
        const names = kids.map((k) => k.textContent.trim().slice(0, 16)).join('" / "');
        const ragged = stackedPairs.some(({ a, b }) => Math.abs(a.width - b.width) > 3 || Math.abs(a.left - b.left) > 3);
        if (ragged) {
          warns.push(`cta-width-mismatch: stacked buttons "${names}" differ in width or alignment on mobile; use .atlas-cta-row for equal-width stacking`);
        } else if (stackedPairs.length) {
          // Equal but narrow, left-aligned buttons leave a ragged gap on the right: fill the row.
          const parent = kids[0].parentElement;
          const cs = getComputedStyle(parent);
          const inner = parent.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
          if (inner > 0 && Math.min(...rects.map((r) => r.width)) < inner * 0.9) {
            warns.push(`cta-not-full-width: stacked buttons "${names}" do not fill the row on mobile; use .atlas-cta-row so they span the content width`);
          }
        }
      }
    }

    // Small screens: a long single column of media cards should be a carousel (phones) or a grid/bento (tablets).
    if (vpWidth <= 820) {
      for (const parent of document.querySelectorAll("main ul, main ol, main div, main section")) {
        if (getComputedStyle(parent).overflowX !== "visible") continue;
        if (parent.closest("[data-carousel], .atlas-carousel, .atlas-bento, [data-atlas-scene]")) continue;
        const kids = [...parent.children].filter((k) => {
          const r = k.getBoundingClientRect();
          return r.width > 0 && r.height > 120 && k.querySelector("img, picture");
        });
        if (kids.length < 3) continue;
        const rects = kids.map((k) => k.getBoundingClientRect());
        const stacked = rects.every((r, i) => i === 0 || r.top >= rects[i - 1].bottom - 2);
        const total = rects[rects.length - 1].bottom - rects[0].top;
        if (stacked && total > innerHeight * 1.8) {
          warns.push(`mobile-long-stack: ${kids.length} media cards stack into ${(total / innerHeight).toFixed(1)} screens at ${vpWidth}px; use .atlas-carousel (swipe on phones, grid on tablets) or .atlas-bento for galleries`);
          break;
        }
      }
    }

    // Tablet portrait: a picture that fills only part of its row with nothing beside it reads as a mistake.
    if (vpWidth >= 600 && vpWidth <= 1023) {
      for (const img of document.querySelectorAll("main img")) {
        const ir = img.getBoundingClientRect();
        if (ir.width < 240 || ir.height < 120) continue;
        if (img.closest("[data-carousel], .atlas-carousel, .atlas-bento, [data-atlas-scene], .atlas-card, header, nav")) continue;
        const block = img.closest("figure") || img;
        const parent = block.parentElement;
        if (!parent) continue;
        const cs = getComputedStyle(parent);
        const inner = parent.getBoundingClientRect().width - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
        const br = block.getBoundingClientRect();
        if (inner < 360 || br.width > inner * 0.86 || br.width < inner * 0.4) continue;
        const neighbour = [...parent.children].some((c) => {
          if (c === block || getComputedStyle(c).position === "absolute") return false;
          const r = c.getBoundingClientRect();
          return r.width > 0 && r.left >= br.right - 2 && r.top < br.bottom && r.bottom > br.top;
        });
        if (!neighbour) {
          warns.push(`half-empty-row: a ${Math.round(br.width)}px picture fills ${Math.round((br.width / inner) * 100)}% of its row at ${vpWidth}px with nothing beside it; make it full width, pair it with text or a second picture, or use .atlas-bento`);
          break;
        }
      }
    }

    // Paired CTA stagger check
    for (const group of document.querySelectorAll("[data-cta-row]")) {
      const children = [...group.querySelectorAll("a, button")].filter((e) => e.offsetParent !== null);
      if (children.length === 2) {
        const [a, b] = children.map((el) => el.getBoundingClientRect());
        if (Math.abs(a.top - b.top) > 12 && vpWidth <= 390 && a.width + b.width + 12 <= group.getBoundingClientRect().width) {
          warns.push("cta-stagger: paired CTAs stacked despite enough width to pair horizontally");
        }
      }
    }

    // Unintentional overlap check between visible direct siblings in interactive groups & bars
    const checkContainers = [...document.querySelectorAll("header nav, [data-cta-row], [data-audit-group]")];
    for (const box of checkContainers) {
      const kids = [...box.children].filter((c) => c.offsetParent !== null && getComputedStyle(c).position !== "absolute");
      for (let i = 0; i < kids.length; i++) {
        for (let j = i + 1; j < kids.length; j++) {
          const r1 = kids[i].getBoundingClientRect();
          const r2 = kids[j].getBoundingClientRect();
          const overlapX = Math.min(r1.right, r2.right) - Math.max(r1.left, r2.left);
          const overlapY = Math.min(r1.bottom, r2.bottom) - Math.max(r1.top, r2.top);
          if (overlapX > 2 && overlapY > 2) {
            warns.push(`overlap: siblings inside <${box.className || box.tagName}> overlap by ${Math.round(overlapX)}x${Math.round(overlapY)}px`);
          }
        }
      }
    }

    // WCAG contrast audit (desktop & narrow mobile)
    const parseColor = (str) => {
      const m = str.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/);
      if (m) return { r: +m[1], g: +m[2], b: +m[3], a: m[4] === undefined ? 1 : +m[4] };
      // Tailwind v4 may compute opacity variants as color(srgb...) or oklab().
      // Let the browser convert CSS Color 4 rather than silently skipping contrast.
      if (!CSS.supports("color", str)) return null;
      const canvas = document.createElement("canvas");
      canvas.width = canvas.height = 1;
      const ctx = canvas.getContext("2d", { willReadFrequently: true });
      ctx.clearRect(0, 0, 1, 1);
      ctx.fillStyle = str;
      ctx.fillRect(0, 0, 1, 1);
      const [r, g, b, alpha] = ctx.getImageData(0, 0, 1, 1).data;
      return { r, g, b, a: alpha / 255 };
    };
    const composite = (fg, bg) => {
      const a = fg.a;
      return { r: fg.r * a + bg.r * (1 - a), g: fg.g * a + bg.g * (1 - a), b: fg.b * a + bg.b * (1 - a), a: 1 };
    };
    const effectiveBg = (el) => {
      const chain = [];
      for (let cur = el; cur; cur = cur.parentElement) {
        const bg = parseColor(getComputedStyle(cur).backgroundColor);
        if (bg && bg.a > 0) chain.unshift(bg);
      }
      let out = { r: 255, g: 255, b: 255, a: 1 };
      for (const layer of chain) out = composite(layer, out);
      return out;
    };
    const lum = ({ r, g, b }) => {
      const f = (v) => {
        const s = v / 255;
        return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
      };
      return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
    };
    const ratio = (c1, c2) => {
      const l1 = lum(c1);
      const l2 = lum(c2);
      return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
    };

    if (vpWidth === 1440 || vpWidth === 360) {
      const lowContrast = [];
      for (const el of document.querySelectorAll("h1, h2, h3, p, a, button")) {
        if (el.offsetParent === null || !el.innerText.trim()) continue;
        const cs = getComputedStyle(el);
        const fg = parseColor(cs.color);
        if (!fg || fg.a === 0) { metrics.contrastSkipped++; continue; }
        metrics.contrastChecked++;
        const bg = effectiveBg(el);
        const cr = ratio(composite(fg, bg), bg);
        const fsPx = parseFloat(cs.fontSize);
        const bold = parseInt(cs.fontWeight, 10) >= 700;
        const minRatio = fsPx >= 24 || (bold && fsPx >= 18.66) ? 3.0 : 4.5;
        if (cr < minRatio) {
          lowContrast.push(`${el.tagName}("${el.innerText.trim().slice(0, 18)}")=${cr.toFixed(2)}`);
        }
      }
      if (lowContrast.length > 0) {
        fails.push(`contrast: ${lowContrast.slice(0, 3).join(", ")}`);
      }
    }

    if (vpWidth >= 1200) {
      const bodySize = parseFloat(getComputedStyle(document.body).fontSize || "16");
      if (bodySize < 15) warns.push(`tiny-body: base body font-size is ${bodySize}px (< 15px)`);

      for (const p of document.querySelectorAll("main p")) {
        if (p.offsetParent === null || p.innerText.trim().length < 70) continue;
        const charsPerLineEst = p.getBoundingClientRect().width / (parseFloat(getComputedStyle(p).fontSize) * 0.48);
        if (charsPerLineEst > 84 && p.getBoundingClientRect().height > 30) {
          warns.push(`wide-measure: paragraph exceeds comfortable ~80ch width (${Math.round(charsPerLineEst)}ch)`);
          break;
        }
      }

      const radii = new Set();
      for (const el of document.querySelectorAll("main article, main section > div, main button, main input, main .card")) {
        const r = getComputedStyle(el).borderRadius;
        if (r && r !== "0px" && !r.includes("9999px") && !r.includes("50%")) {
          radii.add(r.split(" ")[0]);
        }
      }
      if (radii.size > 3) warns.push(`radius-drift: ${radii.size} corner radii (${[...radii].join(", ")})`);

      const grids = [...document.querySelectorAll("main ul, main div")].filter((g) => {
        const cs = getComputedStyle(g);
        return cs.display === "grid" && g.children.length === 3;
      });
      let twinGrids = 0;
      for (const g of grids) {
        const heights = [...g.children].map((c) => Math.round(c.getBoundingClientRect().height));
        if (heights.every((h) => h > 80 && Math.abs(h - heights[0]) < 12)) twinGrids++;
      }
      if (twinGrids >= 2) warns.push(`twin-cards: ${twinGrids} uniform 3-card grids`);

      const matchedSlop = slopList.filter((phrase) => lowerText.includes(phrase));
      if (matchedSlop.length > 0) warns.push(`slop-words: (${matchedSlop.join(", ")})`);
    }

    return { fails, warns, metrics };
  }, { vpWidth: vp.width, slopList: slopPhrases, heroSelector: options.heroSelector, heroActionSelector: options.heroActionSelector, fitHeroUnder: options.fitHeroUnder });
  audit.warns.push(...sweepWarns);
  return audit;
}

async function runInteractiveSmoke(page) {
  const result = { status: "skipped", checks: [], issues: [] };
  await page.setViewportSize({ width: 360, height: 800 });
  await page.waitForTimeout(200);
  const candidates = page.locator("header button[aria-expanded][aria-controls]");
  for (let i = 0; i < await candidates.count(); i++) {
    const button = candidates.nth(i);
    if (!await button.isVisible()) continue;
    const id = await button.getAttribute("aria-controls");
    const panelIsNavigation = await page.evaluate(id => {
      const panel = document.getElementById(id);
      return Boolean(panel && (panel.tagName === "NAV" || panel.getAttribute("role") === "menu"));
    }, id);
    if (!panelIsNavigation) continue;
    const before = await button.getAttribute("aria-expanded");
    await button.click();
    await page.waitForTimeout(250);
    const after = await button.getAttribute("aria-expanded");
    const panelVisible = await page.evaluate(id => {
      const panel = document.getElementById(id);
      if (!panel) return false;
      const r = panel.getBoundingClientRect();
      const s = getComputedStyle(panel);
      return r.width > 0 && r.height > 0 && s.display !== "none" && s.visibility !== "hidden" && !panel.hidden;
    }, id);
    result.checks.push({ kind: "menu", controlledId: id, before, after, panelVisible });
    if (before === after || panelVisible !== (after === "true")) result.issues.push("Menu expanded state and visible controlled navigation disagree: " + id);
    await button.click();
    await page.waitForTimeout(150);
    break;
  }
  await page.setViewportSize({ width: 1440, height: 900 });
  const tablists = page.locator('[role="tablist"]');
  for (let i = 0; i < await tablists.count(); i++) {
    const tabs = tablists.nth(i).locator('[role="tab"]');
    if (await tabs.count() < 2 || !await tabs.nth(1).isVisible()) continue;
    const selected = tabs.nth(1);
    await selected.click();
    await page.waitForTimeout(200);
    const id = await selected.getAttribute("aria-controls");
    const state = await selected.getAttribute("aria-selected");
    const panelVisible = id ? await page.evaluate(id => {
      const panel = document.getElementById(id);
      if (!panel) return false;
      const r = panel.getBoundingClientRect();
      const s = getComputedStyle(panel);
      return r.width > 0 && r.height > 0 && !panel.hidden && s.display !== "none" && s.visibility !== "hidden";
    }, id) : false;
    result.checks.push({ kind: "tab", controlledId: id, selected: state, panelVisible });
    if (state !== "true" || !panelVisible) result.issues.push("Tab selection and visible controlled panel disagree in tablist " + i);
  }
  result.status = result.issues.length ? "failed" : result.checks.length ? "passed" : "skipped";
  return result;
}

async function main() {
  const options = parseArgs(process.argv);
  const { target, shotsDir, verifyClicks, help } = options;
  if (!target || help) {
    console.log("Usage: node quick-check.mjs <http-url | html-file | dir> [--shots <dir>] [--click-test | --no-click-test] [--hero <selector> --hero-action <selector> --fit-hero-under <width>]");
    process.exitCode = help ? 0 : 2;
    console.log(`${help ? "PASS" : "UNVERIFIED"}: ${help ? "usage requested" : "target URL or path is required"}`);
    return;
  }

  let serverObj = null;
  let targetUrl = target;
  if (!/^https?:\/\//i.test(target)) {
    serverObj = await startStaticServer(target);
    targetUrl = serverObj.url;
  }

  let browser;
  const consoleErrors = [];
  let totalFails = 0;
  let totalWarns = 0;
  const results = [];
  const resources = [];
  let interactive = { status: "skipped", reason: "Not requested: audit is read-only by default", checks: [], issues: [] };

  try {
    browser = await launchBrowser();
    const context = await browser.newContext();
    const page = await context.newPage();
    page.on("pageerror", (err) => consoleErrors.push(err.message));
    page.on("console", (msg) => {
      if (msg.type() === "error") consoleErrors.push(msg.text());
    });

    page.on("response", (res) => {
      if (res.status() >= 400 && !res.url().endsWith("/favicon.ico")) resources.push(`${res.status()} ${res.url()}`);
    });
    page.on("requestfailed", (req) => resources.push(`${req.failure()?.errorText} ${req.url()}`));
    await page.goto(targetUrl, { waitUntil: "domcontentloaded", timeout: 30000 });

    console.log(`Atlas Quick-Check v4: ${targetUrl}`);
    for (const vp of VIEWPORTS) {
      const { fails, warns, metrics } = await auditViewport(page, vp, shotsDir, SLOP_PHRASES, options);
      results.push({ viewport: vp, fails, warns, metrics });
      totalFails += fails.length;
      totalWarns += warns.length;
      const status = fails.length ? "FAIL" : warns.length ? "WARN" : "PASS";
      console.log(`  [${status}] ${vp.width}x${vp.height}`);
      for (const f of fails) console.log(`    FAIL: ${f}`);
      for (const w of warns) console.log(`    WARN: ${w}`);
    }

    if (verifyClicks) {
      interactive = await runInteractiveSmoke(page);
      totalFails += interactive.issues.length;
      console.log(`  [${interactive.status.toUpperCase()}] interactive-smoke: ${interactive.checks.length} checks executed`);
      for (const issue of interactive.issues) console.log(`    FAIL: ${issue}`);
    } else console.log("  [SKIPPED] interactive-smoke: no clicks requested");

    if (resources.length) {
      totalFails += resources.length;
      for (const resource of resources) console.log(`    FAIL resource: ${resource}`);
    }
    if (consoleErrors.length > 0) {
      totalFails += consoleErrors.length;
      console.log(`  [FAIL] console-errors (${consoleErrors.length})`);
      for (const err of consoleErrors) console.log(`    FAIL: ${err}`);
    }

    const finalStatus = totalFails ? "FAIL" : "PASS";
    console.log(`Summary: ${totalFails} FAIL, ${totalWarns} WARN${shotsDir ? ` | Screenshots saved to ${shotsDir}` : ""}`);
    if (shotsDir) fs.writeFileSync(path.join(shotsDir, "report.json"), JSON.stringify({
      version: 4, status: finalStatus, target: targetUrl, reviewedAt: new Date().toISOString(),
      results, consoleErrors, resources, interactive, totalFails, totalWarns,
      claim: "Automated subset only; visual review and explicit interaction verification remain required",
      visualReview: "Required: open screenshots and record judgement in ATLAS-REVIEW.md",
      limitations: ["Browser-converted flat-background contrast only; photo overlays and inherited opacity require review", "Smoke tests cover menu and tab selected state only", "Chromium is not cross-browser certification"]
    }, null, 2));
    console.log(`${finalStatus}: ${totalFails ? "violations found" : "all automated checks passed"}`);
    if (totalFails > 0) process.exitCode = 1;
  } finally {
    await browser?.close();
    if (serverObj) serverObj.server.close();
  }
}

main().catch((err) => {
  const code = err.exitCode || 1;
  console.error(err.message || err);
  console.log(`${code === 2 ? "UNVERIFIED" : "FAIL"}: ${code === 2 ? "browser audit unavailable or invalid invocation" : "checker error"}`);
  process.exitCode = code;
});
