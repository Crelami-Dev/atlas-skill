/**
 * Atlas Phase 1 — CDP Collision & Overflow Fixture Verification Test
 * 
 * Verifies that the native WebSocket CDP runner and collision detector
 * correctly differentiate genuine collisions and blowouts from intentional overlays
 * and legitimate scroll containers, with zero false positives.
 */
import assert from 'node:assert';
import { existsSync, mkdirSync, writeFileSync } from 'node:fs';
import { resolve, dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  launchCDPBrowser,
  startStaticServer,
  IN_BROWSER_COLLISION_SCRIPT
} from '../runtime/browser_cdp.mjs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const FIXTURES_DIR = resolve(__dirname, 'fixtures/collision_scenarios');
const ARTIFACTS_DIR = resolve(__dirname, 'artifacts');

if (!existsSync(ARTIFACTS_DIR)) {
  mkdirSync(ARTIFACTS_DIR, { recursive: true });
}

async function runFixturesTest() {
  console.log('--- Starting Atlas Phase 1 CDP Fixtures Test ---');

  const server = await startStaticServer(FIXTURES_DIR);
  console.log(`Local static fixture server running at: ${server.origin}`);

  const browser = await launchCDPBrowser({ width: 768, height: 1024 });
  console.log('Connected to headless browser over native WebSocket.');

  await browser.send('Page.enable');
  await browser.send('DOM.enable');

  const results = [];

  // Helper to test a fixture
  async function testFixture(fixtureFile, viewportWidth = 768) {
    await browser.send('Emulation.setDeviceMetricsOverride', {
      width: viewportWidth,
      height: 1024,
      deviceScaleFactor: 2,
      mobile: false
    });

    const url = `${server.origin}/${fixtureFile}`;
    await browser.send('Page.navigate', { url });
    await new Promise((r) => setTimeout(r, 600)); // wait for layout settle

    const evalResult = await browser.send('Runtime.evaluate', {
      expression: IN_BROWSER_COLLISION_SCRIPT,
      returnByValue: true
    });

    const metrics = evalResult.result.value;

    // Capture screenshot
    const shot = await browser.send('Page.captureScreenshot', { format: 'png' });
    const shotPath = join(ARTIFACTS_DIR, `${fixtureFile.replace('.html', '')}.png`);
    writeFileSync(shotPath, Buffer.from(shot.data, 'base64'));

    return { metrics, shotPath };
  }

  try {
    // 1. Fixture 1: Genuine Text Overlap
    console.log('\nTesting Fixture 1 (Genuine Text Overlap)...');
    const f1 = await testFixture('fixture_1_text_overlap.html', 768);
    console.log(`  Collisions: ${f1.metrics.collisionCount}, Overlap: ${JSON.stringify(f1.metrics.collisions)}`);
    assert.strictEqual(f1.metrics.hasPageOverflow, false, 'Fixture 1 should not have page overflow');
    assert.ok(f1.metrics.collisionCount >= 1, 'Fixture 1 MUST detect at least 1 collision');
    assert.ok(f1.metrics.collisions[0].overlapX >= 40, 'Fixture 1 must detect ~50px text overlap');
    console.log('  [PASS] Genuine text overlap correctly caught as FAIL.');
    results.push({ fixture: 'Fixture 1: Text Overlap', expected: 'COLLISION', actual: 'COLLISION', passed: true });

    // 2. Fixture 2: Intentional Modal Overlay
    console.log('\nTesting Fixture 2 (Intentional Modal Overlay)...');
    const f2 = await testFixture('fixture_2_intentional_overlay.html', 768);
    console.log(`  Collisions: ${f2.metrics.collisionCount}, Overlap: ${JSON.stringify(f2.metrics.collisions)}`);
    assert.strictEqual(f2.metrics.collisionCount, 0, 'Fixture 2 MUST have 0 collisions (modal exempted)');
    assert.strictEqual(f2.metrics.hasPageOverflow, false, 'Fixture 2 should not have page overflow');
    console.log('  [PASS] Modal overlay correctly exempted without false positive.');
    results.push({ fixture: 'Fixture 2: Intentional Overlay', expected: 'ZERO_COLLISIONS', actual: 'ZERO_COLLISIONS', passed: true });

    // 3. Fixture 3: Normal Adjacent Elements
    console.log('\nTesting Fixture 3 (Normal Adjacent Elements)...');
    const f3 = await testFixture('fixture_3_normal_adjacent.html', 768);
    console.log(`  Collisions: ${f3.metrics.collisionCount}, Overlap: ${JSON.stringify(f3.metrics.collisions)}`);
    assert.strictEqual(f3.metrics.collisionCount, 0, 'Fixture 3 MUST have 0 collisions (normal adjacent elements)');
    assert.strictEqual(f3.metrics.hasPageOverflow, false, 'Fixture 3 should not have page overflow');
    console.log('  [PASS] Normal adjacent flex layout verified clean with 0 collisions.');
    results.push({ fixture: 'Fixture 3: Normal Adjacent', expected: 'ZERO_COLLISIONS', actual: 'ZERO_COLLISIONS', passed: true });

    // 4. Fixture 4: Legitimate Horizontal Scroll Container
    console.log('\nTesting Fixture 4 (Legitimate Horizontal Scroll Container)...');
    const f4 = await testFixture('fixture_4_scroll_container.html', 600);
    console.log(`  ScrollWidth: ${f4.metrics.scrollWidth}, ClientWidth: ${f4.metrics.clientWidth}, PageOverflow: ${f4.metrics.hasPageOverflow}`);
    assert.strictEqual(f4.metrics.hasPageOverflow, false, 'Fixture 4 MUST have 0 page-level overflow');
    assert.strictEqual(f4.metrics.collisionCount, 0, 'Fixture 4 MUST have 0 collisions');
    console.log('  [PASS] Container-level scroll successfully isolated without page blowout.');
    results.push({ fixture: 'Fixture 4: Scroll Container', expected: 'NO_PAGE_OVERFLOW', actual: 'NO_PAGE_OVERFLOW', passed: true });

    // 5. Fixture 5: Accidental Page-Level Horizontal Overflow
    console.log('\nTesting Fixture 5 (Accidental Page-Level Horizontal Overflow)...');
    const f5 = await testFixture('fixture_5_page_overflow.html', 600);
    console.log(`  ScrollWidth: ${f5.metrics.scrollWidth}, ClientWidth: ${f5.metrics.clientWidth}, PageOverflow: ${f5.metrics.hasPageOverflow}`);
    assert.strictEqual(f5.metrics.hasPageOverflow, true, 'Fixture 5 MUST detect page-level horizontal overflow');
    console.log('  [PASS] Accidental page blowout correctly caught as FAIL.');
    results.push({ fixture: 'Fixture 5: Page Overflow', expected: 'PAGE_OVERFLOW', actual: 'PAGE_OVERFLOW', passed: true });

    console.log('\n========================================');
    console.log('ALL 5 FIXTURE TESTS PASSED WITH 100% ACCURACY!');
    console.log('Zero false positives on intentional overlays and scroll containers.');
    console.log('Zero false negatives on real collisions and blowouts.');
    console.log('========================================');

  } finally {
    await browser.close();
    await server.close();
  }
}

runFixturesTest().catch((err) => {
  console.error('Fixture test failed with error:', err);
  process.exit(1);
});

