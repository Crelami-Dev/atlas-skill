import fs from 'node:fs';
import os from 'node:os';
import net from 'node:net';
import http from 'node:http';
import path from 'node:path';
import crypto from 'node:crypto';
import { spawn } from 'node:child_process';
import { createRequire } from 'node:module';

export function loadPlaywright() {
  const candidates = [
    process.env.ATLAS_PLAYWRIGHT_PACKAGE,
    path.join(process.cwd(), 'package.json'),
    process.env.APPDATA && path.join(process.env.APPDATA, 'npm/node_modules/dev-browser/package.json'),
    process.env.HOME && path.join(process.env.HOME, '.npm-global/lib/node_modules/dev-browser/package.json'),
  ].filter(Boolean);
  for (const candidate of candidates) {
    try {
      const playwright = createRequire(path.resolve(candidate))('playwright');
      if (playwright.chromium) return playwright;
    } catch { /* Try the next explicitly supported installation. */ }
  }
  throw new Error('Playwright unavailable. Set ATLAS_PLAYWRIGHT_PACKAGE to a package.json that resolves playwright, or install it in your audit environment.');
}

export function findBrowserExecutable() {
  if (process.env.ATLAS_BROWSER_PATH) {
    if (!fs.existsSync(process.env.ATLAS_BROWSER_PATH)) throw new Error('ATLAS_BROWSER_PATH does not exist.');
    return process.env.ATLAS_BROWSER_PATH;
  }
  const candidates = [
    'C:/Program Files/Google/Chrome/Application/chrome.exe',
    'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
    'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser',
  ];
  return candidates.find(candidate => fs.existsSync(candidate));
}

function connectRawWebSocket(wsUrl) {
  return new Promise((resolve, reject) => {
    const parsed = new URL(wsUrl);
    const key = crypto.randomBytes(16).toString('base64');
    const socket = net.createConnection({ host: parsed.hostname, port: Number(parsed.port) });
    let upgraded = false;
    let buf = Buffer.alloc(0);
    let fragments = [];
    const handlers = { message: [], close: [] };

    const sendFrame = (opcode, payloadBuf) => {
      const mask = crypto.randomBytes(4);
      const len = payloadBuf.length;
      const head = [0x80 | opcode];
      if (len < 126) head.push(0x80 | len);
      else if (len < 65536) head.push(0x80 | 126, (len >> 8) & 0xff, len & 0xff);
      else {
        head.push(0x80 | 127);
        const lenBuf = Buffer.alloc(8);
        lenBuf.writeBigUInt64BE(BigInt(len));
        head.push(...lenBuf);
      }
      const masked = Buffer.allocUnsafe(len);
      for (let i = 0; i < len; i++) masked[i] = payloadBuf[i] ^ mask[i % 4];
      socket.write(Buffer.concat([Buffer.from(head), mask, masked]));
    };

    const parseFrames = () => {
      while (buf.length >= 2) {
        const b1 = buf[0];
        const b2 = buf[1];
        const fin = (b1 & 0x80) !== 0;
        const opcode = b1 & 0x0f;
        const isMasked = (b2 & 0x80) !== 0;
        let len = b2 & 0x7f;
        let offset = 2;
        if (len === 126) {
          if (buf.length < 4) return;
          len = buf.readUInt16BE(2);
          offset = 4;
        } else if (len === 127) {
          if (buf.length < 10) return;
          len = Number(buf.readBigUInt64BE(2));
          offset = 10;
        }
        const maskLen = isMasked ? 4 : 0;
        if (buf.length < offset + maskLen + len) return;
        const payload = Buffer.from(buf.subarray(offset + maskLen, offset + maskLen + len));
        if (isMasked) {
          const maskKey = buf.subarray(offset, offset + 4);
          for (let i = 0; i < payload.length; i++) payload[i] ^= maskKey[i % 4];
        }
        buf = buf.subarray(offset + maskLen + len);
        if (opcode === 0x8) {
          socket.end();
          return;
        }
        if (opcode === 0x9) {
          sendFrame(0xA, payload);
          continue;
        }
        if (opcode === 0xA) continue;
        fragments.push(payload);
        if (fin && (opcode === 0x0 || opcode === 0x1 || opcode === 0x2)) {
          const text = Buffer.concat(fragments).toString('utf8');
          fragments = [];
          for (const cb of handlers.message) cb(text);
        }
      }
    };

    socket.on('error', reject);
    socket.on('close', () => { for (const cb of handlers.close) cb(); });
    socket.on('data', chunk => {
      buf = Buffer.concat([buf, chunk]);
      if (!upgraded) {
        const idx = buf.indexOf('\r\n\r\n');
        if (idx === -1) return;
        const headerText = buf.subarray(0, idx).toString('ascii');
        if (!headerText.includes(' 101 ')) {
          reject(new Error(`CDP WebSocket upgrade failed: ${headerText.split('\r\n')[0]}`));
          socket.destroy();
          return;
        }
        upgraded = true;
        buf = buf.subarray(idx + 4);
        resolve({
          send: text => sendFrame(0x1, Buffer.from(text, 'utf8')),
          onMessage: cb => handlers.message.push(cb),
          onClose: cb => handlers.close.push(cb),
          close: () => { try { socket.end(); socket.destroy(); } catch { /* ignore */ } },
        });
      }
      if (upgraded && buf.length) parseFrames();
    });

    socket.on('connect', () => {
      socket.write(
        `GET ${parsed.pathname}${parsed.search} HTTP/1.1\r\n` +
        `Host: ${parsed.host}\r\n` +
        `Upgrade: websocket\r\n` +
        `Connection: Upgrade\r\n` +
        `Sec-WebSocket-Key: ${key}\r\n` +
        `Sec-WebSocket-Version: 13\r\n\r\n`
      );
    });
  });
}

function getFreePort() {
  return new Promise((resolve, reject) => {
    const srv = net.createServer();
    srv.unref();
    srv.on('error', reject);
    srv.listen(0, '127.0.0.1', () => {
      const { port } = srv.address();
      srv.close(() => resolve(port));
    });
  });
}

function httpGetJson(url) {
  return new Promise((resolve, reject) => {
    http.get(url, res => {
      let data = '';
      res.on('data', chunk => { data += chunk; });
      res.on('end', () => {
        try { resolve(JSON.parse(data)); } catch (err) { reject(err); }
      });
    }).on('error', reject);
  });
}

async function launchCdpBrowser(executablePath) {
  if (!executablePath) {
    throw new Error('Playwright unavailable and no Chrome/Edge executable found. Set ATLAS_BROWSER_PATH or install Playwright.');
  }
  const port = await getFreePort();
  const userDataDir = fs.mkdtempSync(path.join(os.tmpdir(), 'atlas-cdp-profile-'));
  const proc = spawn(executablePath, [
    '--headless=new',
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--hide-scrollbars',
    '--window-size=1440,900',
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${userDataDir}`,
    '--remote-allow-origins=*',
    '--no-first-run',
    '--no-default-browser-check',
    'about:blank',
  ], { stdio: 'ignore' });

  let wsUrl = null;
  const deadline = Date.now() + 15000;
  while (Date.now() < deadline) {
    if (proc.exitCode !== null) throw new Error(`Headless browser exited early with code ${proc.exitCode}`);
    try {
      const targets = await httpGetJson(`http://127.0.0.1:${port}/json/list`);
      const pageTarget = targets.find(t => t.type === 'page' && t.webSocketDebuggerUrl);
      if (pageTarget) { wsUrl = pageTarget.webSocketDebuggerUrl; break; }
    } catch { /* retry until CDP endpoint is ready */ }
    await new Promise(r => setTimeout(r, 100));
  }
  if (!wsUrl) {
    proc.kill();
    fs.rmSync(userDataDir, { recursive: true, force: true });
    throw new Error('Timed out waiting for Chrome DevTools WebSocket endpoint.');
  }

  const ws = await connectRawWebSocket(wsUrl);
  let nextId = 1;
  const pending = new Map();
  const cdpEventListeners = new Set();

  ws.onMessage(raw => {
    const msg = JSON.parse(raw);
    if (msg.id && pending.has(msg.id)) {
      const { resolve, reject } = pending.get(msg.id);
      pending.delete(msg.id);
      if (msg.error) reject(new Error(`CDP ${msg.error.message || JSON.stringify(msg.error)}`));
      else resolve(msg.result || {});
    } else if (msg.method) {
      for (const listener of cdpEventListeners) listener(msg.method, msg.params || {});
    }
  });

  const cdp = (method, params = {}) => new Promise((resolve, reject) => {
    const id = nextId++;
    pending.set(id, { resolve, reject });
    ws.send(JSON.stringify({ id, method, params }));
  });

  const createPage = () => {
    const listeners = { pageerror: [], console: [], response: [], requestfailed: [] };
    const requests = new Map();
    cdpEventListeners.add((method, params) => {
      if (method === 'Runtime.exceptionThrown') {
        const d = params.exceptionDetails || {};
        const message = d.exception?.description || d.text || 'Uncaught page error';
        for (const cb of listeners.pageerror) cb(new Error(message));
      } else if (method === 'Runtime.consoleAPICalled') {
        const type = params.type || 'log';
        const text = (params.args || []).map(a => a.value ?? a.description ?? '').join(' ');
        for (const cb of listeners.console) cb({ type: () => type, text: () => text });
      } else if (method === 'Network.requestWillBeSent') {
        requests.set(params.requestId, params.request?.url || '');
      } else if (method === 'Network.responseReceived') {
        const status = params.response?.status ?? 200;
        const url = params.response?.url || requests.get(params.requestId) || '';
        for (const cb of listeners.response) cb({ status: () => status, url: () => url });
      } else if (method === 'Network.loadingFailed') {
        const url = requests.get(params.requestId) || '';
        const errorText = params.errorText || 'net::ERR_FAILED';
        for (const cb of listeners.requestfailed) cb({ failure: () => ({ errorText }), url: () => url });
      }
    });

    const evalRaw = async (expression) => {
      const res = await cdp('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
      if (res.exceptionDetails) {
        const d = res.exceptionDetails;
        throw new Error(d.exception?.description || d.text || 'Page evaluation failed');
      }
      return res.result?.value;
    };

    const resolveChainExpr = (chain) => `(function() {
      const steps = ${JSON.stringify(chain)};
      let nodes = [document];
      for (const step of steps) {
        const next = [];
        for (const root of nodes) {
          if (root && root.querySelectorAll) next.push(...root.querySelectorAll(step.sel));
        }
        nodes = step.index !== undefined ? (next[step.index] ? [next[step.index]] : []) : next;
      }
      return nodes;
    })()`;

    const makeLocator = (chain) => ({
      locator: subSel => makeLocator([...chain, { sel: subSel }]),
      nth: idx => {
        const next = chain.slice();
        next[next.length - 1] = { ...next[next.length - 1], index: idx };
        return makeLocator(next);
      },
      count: () => evalRaw(`${resolveChainExpr(chain)}.length`),
      isVisible: () => evalRaw(`(function() {
        const el = ${resolveChainExpr(chain)}[0];
        if (!el) return false;
        const r = el.getBoundingClientRect();
        if (r.width <= 0 || r.height <= 0) return false;
        for (let n = el; n; n = n.parentElement) {
          const s = getComputedStyle(n);
          if (n.hidden || s.display === 'none' || s.visibility === 'hidden' || Number(s.opacity) <= 0.05) return false;
        }
        return true;
      })()`),
      getAttribute: name => evalRaw(`(function() {
        const el = ${resolveChainExpr(chain)}[0];
        return el ? el.getAttribute(${JSON.stringify(name)}) : null;
      })()`),
      click: async () => {
        const pt = await evalRaw(`(function() {
          const el = ${resolveChainExpr(chain)}[0];
          if (!el) return null;
          el.scrollIntoView({ block: 'center', inline: 'center', behavior: 'instant' });
          const r = el.getBoundingClientRect();
          return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
        })()`);
        if (!pt) throw new Error('Locator element not found for click()');
        await cdp('Input.dispatchMouseEvent', { type: 'mousePressed', x: pt.x, y: pt.y, button: 'left', clickCount: 1 });
        await cdp('Input.dispatchMouseEvent', { type: 'mouseReleased', x: pt.x, y: pt.y, button: 'left', clickCount: 1 });
      },
    });

    return {
      on: (ev, cb) => { if (listeners[ev]) listeners[ev].push(cb); },
      goto: async (url, opts = {}) => {
        await cdp('Page.enable');
        await cdp('Runtime.enable');
        await cdp('Network.enable');
        let loadFired = false;
        const onEvent = (method) => { if (method === 'Page.loadEventFired') loadFired = true; };
        cdpEventListeners.add(onEvent);
        await cdp('Page.navigate', { url });
        const timeout = opts.timeout || 30000;
        const end = Date.now() + timeout;
        while (Date.now() < end) {
          const state = await evalRaw('document.readyState');
          if (opts.waitUntil === 'domcontentloaded' ? (state === 'interactive' || state === 'complete') : (loadFired || state === 'complete')) {
            break;
          }
          await new Promise(r => setTimeout(r, 50));
        }
        // Allow subresources started during parse to settle briefly
        await new Promise(r => setTimeout(r, 150));
        cdpEventListeners.delete(onEvent);
      },
      setViewportSize: async ({ width, height }) => {
        await cdp('Emulation.setDeviceMetricsOverride', {
          width,
          height,
          deviceScaleFactor: 1,
          mobile: width <= 820,
        });
      },
      evaluate: (fn, arg) => {
        const serializedArg = arg === undefined ? '' : JSON.stringify(arg);
        return evalRaw(`(${fn.toString()})(${serializedArg})`);
      },
      waitForTimeout: ms => new Promise(r => setTimeout(r, ms)),
      screenshot: async ({ path: outPath, fullPage = false } = {}) => {
        let params = { format: 'png' };
        if (fullPage) {
          const metrics = await cdp('Page.getLayoutMetrics');
          const content = metrics.cssContentSize || metrics.contentSize;
          params = {
            format: 'png',
            captureBeyondViewport: true,
            clip: {
              x: 0,
              y: 0,
              width: Math.max(1, Math.ceil(content.width)),
              height: Math.max(1, Math.ceil(content.height)),
              scale: 1,
            },
          };
        }
        const { data } = await cdp('Page.captureScreenshot', params);
        if (outPath) fs.writeFileSync(outPath, Buffer.from(data, 'base64'));
        return Buffer.from(data, 'base64');
      },
      locator: selector => makeLocator([{ sel: selector }]),
    };
  };

  return {
    newContext: async () => ({
      newPage: async () => createPage(),
    }),
    close: async () => {
      ws.close();
      if (proc.exitCode === null) {
        proc.kill();
        await new Promise(resolve => {
          const t = setTimeout(resolve, 2000);
          proc.once('exit', () => { clearTimeout(t); resolve(); });
        });
      }
      fs.rmSync(userDataDir, { recursive: true, force: true });
    },
  };
}

export async function launchBrowser() {
  const executablePath = findBrowserExecutable();
  try {
    const { chromium } = loadPlaywright();
    // If no system browser is found, Playwright resolves its own managed browser.
    return await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  } catch {
    return launchCdpBrowser(executablePath);
  }
}
