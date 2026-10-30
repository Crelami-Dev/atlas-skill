/**
 * Atlas Runtime Engine — Zero-Dependency Browser CDP Runner.
 * 
 * Drives headless Chrome/Edge over native Node.js 22+ WebSocket.
 * Zero npm dependencies. Supports dynamic SPAs and static files.
 * Provides DOM bounding box collision detection and multi-viewport inspection.
 */
import { spawn } from 'node:child_process';
import { existsSync, mkdtempSync, rmSync, writeFileSync, statSync, createReadStream, mkdirSync } from 'node:fs';
import { createServer } from 'node:http';
import { tmpdir } from 'node:os';
import { join, resolve, extname } from 'node:path';

export const STANDARD_VIEWPORTS = {
  desktop: { width: 1440, height: 900, label: 'Desktop (1440x900)' },
  tablet_landscape: { width: 1024, height: 768, label: 'Tablet Landscape (1024x768)' },
  tablet: { width: 768, height: 1024, label: 'Tablet Portrait (768x1024)' },
  mobile: { width: 390, height: 844, label: 'Modern Mobile (390x844)', mobile: true },
  mobile_small: { width: 320, height: 568, label: 'Small Mobile (320x568)', mobile: true }
};

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon'
};

export function findBrowserExecutable() {
  const env = process.env.CHROME_PATH || process.env.EDGE_PATH;
  if (env && existsSync(env)) return env;

  const pf = process.env.PROGRAMFILES || 'C:\\Program Files';
  const pf86 = process.env['PROGRAMFILES(X86)'] || 'C:\\Program Files (x86)';
  const local = process.env.LOCALAPPDATA || '';

  const candidates = [
    // Windows Chrome
    join(pf, 'Google/Chrome/Application/chrome.exe'),
    join(pf86, 'Google/Chrome/Application/chrome.exe'),
    join(local, 'Google/Chrome/Application/chrome.exe'),
    // Windows Edge
    join(pf, 'Microsoft/Edge/Application/msedge.exe'),
    join(pf86, 'Microsoft/Edge/Application/msedge.exe'),
    // Linux / macOS
    '/usr/bin/google-chrome',
    '/usr/bin/chromium',
    '/usr/bin/chromium-browser',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge'
  ];

  for (const c of candidates) {
    if (c && existsSync(c)) return c;
  }
  return null;
}

export class CDPClient {
  constructor(proc, wsUrl, tempDir) {
    this.proc = proc;
    this.wsUrl = wsUrl;
    this.tempDir = tempDir;
    this.ws = null;
    this.nextId = 1;
    this.pending = new Map();
  }

  async connect() {
    this.ws = new WebSocket(this.wsUrl);
    await new Promise((resolve, reject) => {
      this.ws.onopen = resolve;
      this.ws.onerror = reject;
    });

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.id && this.pending.has(data.id)) {
          const { resolve, reject } = this.pending.get(data.id);
          this.pending.delete(data.id);
          if (data.error) reject(new Error(data.error.message || JSON.stringify(data.error)));
          else resolve(data.result);
        }
      } catch (err) {}
    };
  }

  send(method, params = {}, timeoutMs = 15000) {
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`CDP command timed out (${timeoutMs}ms): ${method}`));
      }, timeoutMs);

      this.pending.set(id, {
        resolve: (val) => { clearTimeout(timer); resolve(val); },
        reject: (err) => { clearTimeout(timer); reject(err); }
      });

      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  async close() {
    try {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.close();
      }
    } catch {}

    try {
      if (this.proc && !this.proc.killed) {
        this.proc.kill();
      }
    } catch {}

    try {
      if (this.tempDir && existsSync(this.tempDir)) {
        rmSync(this.tempDir, { recursive: true, force: true });
      }
    } catch {}
  }
}

export async function launchCDPBrowser({ width = 1440, height = 900 } = {}) {
  const browserPath = findBrowserExecutable();
  if (!browserPath) {
    throw new Error('No compatible headless browser (Chrome or Edge) found on host system.');
  }

  const tempDir = mkdtempSync(join(tmpdir(), 'atlas-cdp-'));
  const proc = spawn(browserPath, [
    '--headless=new',
    '--remote-debugging-port=0',
    `--user-data-dir=${tempDir}`,
    '--disable-gpu',
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-sync',
    '--disable-background-timer-throttling',
    '--disable-renderer-backgrounding',
    `--window-size=${width},${height}`,
    'about:blank'
  ], { stdio: ['ignore', 'ignore', 'pipe'] });

  const wsUrl = await new Promise((resolve, reject) => {
    let output = '';
    const timer = setTimeout(() => {
      proc.kill();
      reject(new Error(`Browser did not output DevTools WebSocket within 10s: ${output}`));
    }, 10000);

    proc.stderr.on('data', (chunk) => {
      output += chunk.toString();
      const match = output.match(/DevTools listening on (ws:\/\/[^\s]+)/);
      if (match) {
        clearTimeout(timer);
        resolve(match[1]);
      }
    });

    proc.on('exit', (code) => {
      clearTimeout(timer);
      reject(new Error(`Browser exited prematurely with code ${code}: ${output}`));
    });
  });

  let pageWsUrl = wsUrl;
  try {
    const portMatch = wsUrl.match(/127\.0\.0\.1:(\d+)/);
    if (portMatch) {
      const port = portMatch[1];
      const listRes = await fetch(`http://127.0.0.1:${port}/json/list`).then(r => r.json());
      const pageTab = listRes.find(t => t.type === 'page');
      if (pageTab && pageTab.webSocketDebuggerUrl) {
        pageWsUrl = pageTab.webSocketDebuggerUrl;
      }
    }
  } catch {}

  const client = new CDPClient(proc, pageWsUrl, tempDir);
  await client.connect();
  return client;
}

export function startStaticServer(targetDirOrFile, port = 0) {
  const isFile = existsSync(targetDirOrFile) && statSync(targetDirOrFile).isFile();
  const rootDir = isFile ? resolve(targetDirOrFile, '..') : resolve(targetDirOrFile);
  const defaultFile = isFile ? resolve(targetDirOrFile) : join(rootDir, 'index.html');

  const server = createServer((req, res) => {
    let reqPath = decodeURIComponent(req.url.split('?')[0]);
    if (reqPath === '/' || reqPath === '') {
      if (existsSync(defaultFile)) {
        res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
        createReadStream(defaultFile).pipe(res);
        return;
      }
    }

    let relativePath = reqPath.startsWith('/') ? reqPath.slice(1) : reqPath;
    let targetPath = join(rootDir, relativePath);

    if (existsSync(targetPath) && statSync(targetPath).isFile()) {
      const ext = extname(targetPath).toLowerCase();
      res.writeHead(200, { 'Content-Type': MIME_TYPES[ext] || 'application/octet-stream' });
      createReadStream(targetPath).pipe(res);
    } else {
      if (existsSync(defaultFile)) {
        res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
        createReadStream(defaultFile).pipe(res);
      } else {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('Not Found');
      }
    }
  });

  return new Promise((resolveServer) => {
    server.listen(port, '127.0.0.1', () => {
      const actualPort = server.address().port;
      resolveServer({
        port: actualPort,
        origin: `http://127.0.0.1:${actualPort}`,
        close: () => new Promise((done) => server.close(done))
      });
    });
  });
}

export const IN_BROWSER_COLLISION_SCRIPT = `
(() => {
  const root = document.documentElement;
  const scrollWidth = root.scrollWidth;
  const clientWidth = root.clientWidth;
  const hasPageOverflow = scrollWidth > clientWidth + 1;

  function isIntentionalOverlay(el) {
    let curr = el;
    while (curr && curr !== document.body && curr !== document.documentElement) {
      const style = window.getComputedStyle(curr);
      const pos = style.position;
      const zIndex = parseInt(style.zIndex, 10);
      const role = curr.getAttribute('role');
      const ariaModal = curr.getAttribute('aria-modal');

      if (pos === 'fixed' || (pos === 'absolute' && !isNaN(zIndex) && zIndex >= 1)) {
        return true;
      }
      if (role === 'dialog' || ariaModal === 'true' || curr.classList.contains('modal-backdrop') || curr.classList.contains('modal-card') || curr.classList.contains('tooltip')) {
        return true;
      }
      curr = curr.parentElement;
    }
    return false;
  }

  function getScrollContainer(el) {
    let curr = el.parentElement;
    while (curr && curr !== document.body && curr !== document.documentElement) {
      const style = window.getComputedStyle(curr);
      if (style.overflowX === 'auto' || style.overflowX === 'scroll') {
        return curr;
      }
      curr = curr.parentElement;
    }
    return null;
  }

  const candidates = [];
  const selector = 'button, input, select, a, p, span, h1, h2, h3, h4, h5, h6, th, td, [class*="badge"], [class*="name"], [class*="title"], [class*="cell"], [class*="btn"], [class*="metric"], [class*="card"]';
  const allElements = document.querySelectorAll(selector);

  for (const el of allElements) {
    if (el.children.length > 4) continue;
    const rect = el.getBoundingClientRect();
    if (rect.width <= 2 || rect.height <= 2) continue;

    const style = window.getComputedStyle(el);
    if (style.display === 'none' || style.visibility === 'hidden' || parseFloat(style.opacity) < 0.05) continue;

    candidates.push({
      el,
      rect,
      isOverlay: isIntentionalOverlay(el),
      scrollContainer: getScrollContainer(el)
    });
  }

  const collisions = [];
  for (let i = 0; i < candidates.length; i++) {
    for (let j = i + 1; j < candidates.length; j++) {
      const a = candidates[i];
      const b = candidates[j];

      if (a.isOverlay || b.isOverlay) continue;
      if (a.el.contains(b.el) || b.el.contains(a.el)) continue;
      if (a.scrollContainer !== b.scrollContainer) continue;

      const xOverlap = Math.min(a.rect.right, b.rect.right) - Math.max(a.rect.left, b.rect.left);
      const yOverlap = Math.min(a.rect.bottom, b.rect.bottom) - Math.max(a.rect.top, b.rect.top);

      if (xOverlap > 2 && yOverlap > 2) {
        const aStyle = window.getComputedStyle(a.el);
        const bStyle = window.getComputedStyle(b.el);
        if (aStyle.position === 'absolute' && bStyle.position === 'absolute' && aStyle.zIndex !== bStyle.zIndex) continue;

        collisions.push({
          elementA: a.el.className ? '.' + Array.from(a.el.classList).join('.') : a.el.tagName.toLowerCase(),
          elementB: b.el.className ? '.' + Array.from(b.el.classList).join('.') : b.el.tagName.toLowerCase(),
          textA: (a.el.innerText || a.el.textContent || '').trim().slice(0, 32),
          textB: (b.el.innerText || b.el.textContent || '').trim().slice(0, 32),
          overlapX: Math.round(xOverlap),
          overlapY: Math.round(yOverlap)
        });
      }
    }
  }

  return {
    scrollWidth,
    clientWidth,
    hasPageOverflow,
    collisionCount: collisions.length,
    collisions
  };
})()
`;

/**
 * Runs full 5-viewport layout inspection against a target URL or directory.
 */
export async function runLayoutAudit(targetUrlOrDir, { screenshotsDir = null, customViewports = null } = {}) {
  let server = null;
  let targetUrl = targetUrlOrDir;

  if (!targetUrlOrDir.startsWith('http://') && !targetUrlOrDir.startsWith('https://')) {
    server = await startStaticServer(targetUrlOrDir);
    targetUrl = server.origin;
  }

  const viewports = customViewports || STANDARD_VIEWPORTS;
  const browser = await launchCDPBrowser();

  try {
    await browser.send('Page.enable');
    await browser.send('DOM.enable');

    const report = {
      targetUrl,
      timestamp: new Date().toISOString(),
      status: 'PASS',
      viewports: {}
    };

    if (screenshotsDir && !existsSync(screenshotsDir)) {
      mkdirSync(screenshotsDir, { recursive: true });
    }

    for (const [key, vp] of Object.entries(viewports)) {
      await browser.send('Emulation.setDeviceMetricsOverride', {
        width: vp.width,
        height: vp.height,
        deviceScaleFactor: 2,
        mobile: Boolean(vp.mobile)
      });

      await browser.send('Page.navigate', { url: targetUrl });
      await new Promise((r) => setTimeout(r, 600));

      const evalRes = await browser.send('Runtime.evaluate', {
        expression: IN_BROWSER_COLLISION_SCRIPT,
        returnByValue: true
      });

      const metrics = evalRes.result.value || {
        scrollWidth: 0,
        clientWidth: 0,
        hasPageOverflow: false,
        collisionCount: 0,
        collisions: []
      };

      let screenshotPath = null;
      if (screenshotsDir) {
        const shot = await browser.send('Page.captureScreenshot', { format: 'png' });
        screenshotPath = join(screenshotsDir, `${key}_${vp.width}x${vp.height}.png`);
        writeFileSync(screenshotPath, Buffer.from(shot.data, 'base64'));
      }

      const vpStatus = (!metrics.hasPageOverflow && metrics.collisionCount === 0) ? 'PASS' : 'FAIL';
      if (vpStatus === 'FAIL') report.status = 'FAIL';

      report.viewports[key] = {
        label: vp.label,
        width: vp.width,
        height: vp.height,
        status: vpStatus,
        scrollWidth: metrics.scrollWidth,
        clientWidth: metrics.clientWidth,
        hasPageOverflow: metrics.hasPageOverflow,
        collisionCount: metrics.collisionCount,
        collisions: metrics.collisions,
        screenshotPath
      };
    }

    return report;
  } finally {
    await browser.close();
    if (server) await server.close();
  }
}

// Standalone CLI invocation
if (process.argv[1] && process.argv[1].endsWith('browser_cdp.mjs')) {
  const target = process.argv[2];
  if (!target) {
    console.error('Usage: node browser_cdp.mjs <url_or_dir> [--shots <dir>]');
    process.exit(1);
  }

  let shotsDir = null;
  const shotsIdx = process.argv.indexOf('--shots');
  if (shotsIdx !== -1 && process.argv[shotsIdx + 1]) {
    shotsDir = resolve(process.argv[shotsIdx + 1]);
  }

  runLayoutAudit(target, { screenshotsDir: shotsDir })
    .then((report) => {
      console.log(JSON.stringify(report, null, 2));
      process.exit(report.status === 'PASS' ? 0 : 1);
    })
    .catch((err) => {
      console.error('CDP layout audit failed:', err);
      process.exit(1);
    });
}
