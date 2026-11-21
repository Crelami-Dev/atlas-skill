import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const script = path.resolve(__dirname, '..', 'scripts', 'fetch-photos.mjs');

// A fake Wikimedia API plus image host on one local port:
//   /good.jpg    serves 20 kB immediately
//   /trickle.jpg sends one byte every 100 ms forever (never idle, so the socket timeout never fires)
//   /flaky.jpg   returns 503 on the first request, then 20 kB
function startFakeCommons() {
  let flakyHits = 0;
  const server = http.createServer((req, res) => {
    const url = new URL(req.url, 'http://127.0.0.1');
    if (url.pathname === '/api') {
      const base = `http://127.0.0.1:${server.address().port}`;
      const page = (id, title, file, author) => ({
        title: `File:${title}`,
        imageinfo: [{
          thumburl: `${base}/${file}`,
          thumbwidth: 1600,
          thumbheight: 1000,
          mime: 'image/jpeg',
          descriptionurl: `${base}/wiki/${id}`,
          extmetadata: { LicenseShortName: { value: 'CC0' }, Artist: { value: author } }
        }]
      });
      const wanted = url.searchParams.get('gsrsearch') || '';
      const pages = {};
      if (wanted.includes('trickle')) pages[1] = page(1, 'Trickle villa.jpg', 'trickle.jpg', 'Slow Author');
      if (wanted.includes('good')) pages[2] = page(2, 'Good villa.jpg', 'good.jpg', 'Fast Author');
      if (wanted.includes('redir')) pages[4] = page(4, 'Redir villa.jpg', 'redir.jpg', 'Redirect Author');
      if (wanted.includes('flaky')) pages[3] = page(3, 'Flaky villa.jpg', 'flaky.jpg', 'Retry Author');
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ query: { pages } }));
      return;
    }
    if (url.pathname === '/good.jpg') {
      res.writeHead(200, { 'Content-Type': 'image/jpeg' });
      res.end(Buffer.alloc(20000, 1));
      return;
    }
    if (url.pathname === '/flaky.jpg') {
      if (flakyHits++ === 0) { res.writeHead(503); res.end(); return; }
      res.writeHead(200, { 'Content-Type': 'image/jpeg' });
      res.end(Buffer.alloc(20000, 2));
      return;
    }
    if (url.pathname === '/redir.jpg') {
      res.writeHead(302, { Location: '/trickle.jpg' });
      res.end();
      return;
    }
    if (url.pathname === '/trickle.jpg') {
      res.writeHead(200, { 'Content-Type': 'image/jpeg' });
      const timer = setInterval(() => res.write('x'), 100);
      res.on('close', () => clearInterval(timer));
      return;
    }
    res.writeHead(404);
    res.end();
  });
  return new Promise((resolve) => server.listen(0, '127.0.0.1', () => resolve(server)));
}

function run(port, query, extraArgs = []) {
  const out = fs.mkdtempSync(path.join(os.tmpdir(), 'atlas-fetch-photos-'));
  return new Promise((resolve, reject) => {
    const started = Date.now();
    const child = spawn(process.execPath, [script, '--query', query, '--out', out, '--count', '4', '--min-width', '1000', ...extraArgs], {
      env: { ...process.env, ATLAS_WIKIMEDIA_API: `http://127.0.0.1:${port}/api` },
      stdio: ['ignore', 'pipe', 'pipe']
    });
    let stdout = '';
    child.stdout.on('data', (c) => { stdout += c; });
    const guard = setTimeout(() => { child.kill(); reject(new Error('fetch-photos hung past the test guard')); }, 40000);
    child.on('close', (code) => {
      clearTimeout(guard);
      resolve({ code, ms: Date.now() - started, out, manifest: JSON.parse(stdout) });
    });
  });
}

test('fetch-photos: a trickling download is cut off by the per-request limit', async () => {
  const server = await startFakeCommons();
  try {
    const result = await run(server.address().port, 'trickle', ['--request-timeout', '2', '--timeout', '20']);
    assert.equal(result.code, 0);
    assert.ok(result.ms < 15000, `expected a bounded run, took ${result.ms} ms`);
    assert.equal(result.manifest.status, 'no-matches');
    assert.ok(result.manifest.problems.some((p) => p.includes('trickle')), 'the trickling candidate must be reported');
  } finally { server.close(); }
});

test('fetch-photos: a redirect into a trickling download is still bounded by the request limit', async () => {
  const server = await startFakeCommons();
  try {
    const result = await run(server.address().port, 'redir', ['--request-timeout', '2', '--timeout', '20']);
    assert.equal(result.manifest.status, 'no-matches');
    assert.ok(result.ms < 10000, `expected a bounded run, took ${result.ms} ms`);
    assert.ok(result.manifest.problems.some((p) => p.includes('Redir')));
  } finally { server.close(); }
});

test('fetch-photos: a slow candidate does not block a later good one, and credits are written', async () => {
  const server = await startFakeCommons();
  try {
    const result = await run(server.address().port, 'trickle|good', ['--request-timeout', '2', '--timeout', '30']);
    assert.equal(result.manifest.count, 1);
    assert.equal(result.manifest.photos[0].author, 'Fast Author');
    assert.equal(result.manifest.status, 'partial');
    const credits = JSON.parse(fs.readFileSync(path.join(result.out, 'credits.json'), 'utf8'));
    assert.equal(credits.photos.length, 1);
    assert.ok(fs.existsSync(path.join(result.out, credits.photos[0].file)));
  } finally { server.close(); }
});

test('fetch-photos: a transient 503 is retried once and succeeds', async () => {
  const server = await startFakeCommons();
  try {
    const result = await run(server.address().port, 'flaky', ['--request-timeout', '5', '--timeout', '30']);
    assert.equal(result.manifest.count, 1);
    assert.equal(result.manifest.photos[0].author, 'Retry Author');
    assert.equal(result.manifest.status, 'ok');
  } finally { server.close(); }
});

test('fetch-photos: the total --timeout budget stops the run and keeps finished photos', async () => {
  const server = await startFakeCommons();
  try {
    const result = await run(server.address().port, 'good|trickle|trickle', ['--request-timeout', '30', '--timeout', '8']);
    assert.ok(result.ms < 20000, `expected the 8s budget to bound the run, took ${result.ms} ms`);
    assert.equal(result.manifest.count, 1);
    assert.ok(fs.existsSync(path.join(result.out, 'credits.json')));
  } finally { server.close(); }
});

test('fetch-photos: an unreachable API reports offline-fallback, not a hang', async () => {
  const result = await run(1, 'anything', ['--request-timeout', '2', '--timeout', '10']);
  assert.equal(result.code, 0);
  assert.equal(result.manifest.status, 'offline-fallback');
  assert.ok(result.ms < 20000);
});
