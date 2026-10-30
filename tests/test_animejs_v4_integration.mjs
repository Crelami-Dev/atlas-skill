/**
 * Atlas Phase 5 — Standalone Anime.js v4 Real Integration Test
 * 
 * Verifies direct integration between AtlasMotionAdapter and installed animejs@4.5.0
 * without Python dependencies.
 */
import assert from 'node:assert';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import * as animeV4 from 'animejs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const adapterPath = path.resolve(__dirname, '../adapters/motion/animejs-adapter.js');

// 1. Mock minimal DOM environment for Node.js
globalThis.getComputedStyle = (el) => ({
  getPropertyValue: (prop) => (el.style && el.style[prop]) || ''
});

function createMockEl(val) {
  return {
    style: {},
    nodeType: 1,
    innerText: '0',
    getAttribute: (attr) => (attr === 'data-value' ? val : null),
    setAttribute: () => {}
  };
}

const el1 = createMockEl('100');
const el2 = createMockEl('250');
globalThis.document = {
  body: { contains: () => true },
  querySelectorAll: () => [el1, el2]
};

// 2. Load Adapter (CJS/UMD format)
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const AtlasMotionAdapter = require(adapterPath);

// 3. Verify Anime.js v4 exports
assert.strictEqual(typeof animeV4.animate, 'function', 'animejs.animate must be a function');
assert.strictEqual(typeof animeV4.stagger, 'function', 'animejs.stagger must be a function');
assert.strictEqual(typeof animeV4.cubicBezier, 'function', 'animejs.cubicBezier must be a function');
assert.strictEqual(typeof animeV4.remove, 'function', 'animejs.remove must be a function');

// 4. Test Adapter execution with real v4
const adapter = new AtlasMotionAdapter({ anime: animeV4 });

const res = adapter.execute({
  id: 'masked-headline',
  targets: ['.hero h1 [data-line]'],
  timing: { durationMs: 400, delayMs: 50 },
  easing: { token: '--ease-expo' },
  stagger: { intervalMs: 80, startMs: 50 }
});

assert.strictEqual(res.success, true, 'Execution must succeed');
assert.strictEqual(res.mode, 'animejs-v4', 'Mode must be animejs-v4');
assert.ok(res.instance, 'Must have v4 animation instance');
assert.strictEqual(adapter.activeInstances.size, 1);

// 5. Test real v4 destroy
const destroyRes = adapter.destroy('masked-headline');
assert.strictEqual(destroyRes.success, true);
assert.strictEqual(res.instance.paused, true);
assert.strictEqual(res.instance.cancelled, true);

// 6. Test real v4 rolling figures
const rollRes = adapter.execute({
  id: 'rolling-figures',
  targets: ['.stat-number'],
  timing: { durationMs: 150 }
});
assert.strictEqual(rollRes.success, true);
assert.strictEqual(rollRes.mode, 'animejs-v4-counter');

// 7. Test real v4 cleanup
const cleanRes = adapter.cleanup();
assert.strictEqual(cleanRes.success, true);
assert.strictEqual(adapter.activeInstances.size, 0);

console.log('✓ Anime.js v4.5.0 Real Integration Tests: ALL PASSED');

