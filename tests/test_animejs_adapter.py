#!/usr/bin/env python3
"""Atlas Phase 5 Test Suite — Anime.js v4 Adapter Unit & Integration Verification.

Executes comprehensive tests on `adapters/motion/animejs-adapter.js` using Node.js to verify:
[Group A - Unit Tests]:
1. Adapter file metadata and Anime.js v4 official target scope documentation.
2. Parameter translation to Anime.js v4 API signature (animate(targets, options), stagger, cubicBezier, remove).
3. Graceful degradation to Native CSS Fallback when Anime.js engine is null/unavailable.
4. Kepatuhan preferensi aksesibilitas `prefers-reduced-motion: reduce`.
5. Lifecycle idempotence for destroy() and cleanup().

[Group B - Integration Tests with Real Anime.js v4.5.0 Binary]:
6. Direct import and execution against installed `node_modules/animejs` (v4.5.0).
7. Execution of motion pattern (masked-headline) using real v4 animate and stagger.
8. Real lifecycle control: instance pausing, cancellation, and active instance tracking.
9. Numerical counter animation (rolling-figures) using real v4 onUpdate handler.
10. Complete teardown with real v4 engine.
"""
import os
import subprocess
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

ADAPTER_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "adapters", "motion", "animejs-adapter.js")
)
NODE_MODULES_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "node_modules")
)


class TestAnimejsAdapter(unittest.TestCase):

    # =========================================================================
    # Group A: Unit Tests (Static & Mock)
    # =========================================================================

    def test_unit_adapter_file_and_v4_scope_documentation(self):
        """[UNIT] Verify adapter file exists and explicitly documents Anime.js v4 target scope."""
        self.assertTrue(os.path.exists(ADAPTER_PATH), f"Adapter missing at {ADAPTER_PATH}")
        with open(ADAPTER_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("AtlasMotionAdapter", content)
        self.assertIn("Anime.js v4", content)
        self.assertIn("executeWithAnimeV4", content)
        self.assertIn("prefers-reduced-motion", content)
        self.assertIn("applyNativeCssFallback", content)
        self.assertIn("destroy", content)
        self.assertIn("cleanup", content)

    def test_unit_adapter_mock_anime_v4_parameter_mapping(self):
        """[UNIT] Verify adapter translates motion specs into correct Anime.js v4 API calls using mock."""
        node_script = """
        const AtlasMotionAdapter = require(process.env.ADAPTER_PATH);
        const assert = require('assert');

        // Mock Anime.js v4 engine
        const animateCalls = [];
        const mockEngine = {
          animate: function(targets, options) {
            animateCalls.push({ targets, options });
            return {
              id: 'mock-v4-instance-' + animateCalls.length,
              targets: targets,
              pause: function() { this.paused = true; },
              cancel: function() { this.cancelled = true; },
              paused: false,
              cancelled: false
            };
          },
          stagger: function(val, opts) {
            return function(el, i) { return (opts.start || 0) + i * val; };
          },
          cubicBezier: function(x1, y1, x2, y2) {
            return function(t) { return t; };
          },
          eases: {
            linear: function(t) { return t; },
            outExpo: function(t) { return t; }
          },
          remove: function(targets) {
            if (Array.isArray(targets)) targets.forEach(t => t.removed = true);
          }
        };

        // Mock DOM Element
        const mockEl = {
          style: {},
          nodeType: 1,
          innerText: '0',
          getAttribute: () => '100',
          setAttribute: () => {}
        };
        global.document = {
          body: { contains: () => true },
          querySelectorAll: () => [mockEl]
        };

        const adapter = new AtlasMotionAdapter({ anime: mockEngine, forceReducedMotion: false });

        // Execute masked-headline
        const res = adapter.execute({
          id: 'masked-headline',
          targets: ['.hero h1 [data-line]'],
          timing: { durationMs: 900, delayMs: 150 },
          easing: { token: '--ease-expo' },
          stagger: { intervalMs: 110, startMs: 150 }
        });

        assert.strictEqual(res.success, true, 'Execution should succeed');
        assert.strictEqual(res.mode, 'animejs-v4', 'Should report animejs-v4 mode');
        assert.strictEqual(animateCalls.length, 1, 'Should call mock animate exactly once');
        assert.strictEqual(animateCalls[0].options.duration, 900, 'Duration should match');
        assert.strictEqual(typeof animateCalls[0].options.ease, 'function', 'Ease should resolve to function in v4');
        assert.deepStrictEqual(animateCalls[0].options.translateY, ['105%', '0%'], 'TranslateY curve should match');

        // Verify active instance recorded
        assert.strictEqual(adapter.activeInstances.size, 1);
        assert.ok(adapter.activeInstances.has('masked-headline'));

        // Test destroy of single pattern
        const destroyRes = adapter.destroy('masked-headline');
        assert.strictEqual(destroyRes.success, true);
        assert.strictEqual(adapter.activeInstances.size, 0);

        console.log('UNIT_MOCK_ANIME_V4_PASSED');
        """

        env = os.environ.copy()
        env["ADAPTER_PATH"] = ADAPTER_PATH
        proc = subprocess.run(["node", "-e", node_script], env=env, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"Unit Mock Anime.js v4 test failed:\n{proc.stderr}")
        self.assertIn("UNIT_MOCK_ANIME_V4_PASSED", proc.stdout)

    def test_unit_adapter_css_fallback_and_reduced_motion(self):
        """[UNIT] Verify Native CSS fallback when Anime is missing, and reduced motion in simulated DOM."""
        node_script = """
        const AtlasMotionAdapter = require(process.env.ADAPTER_PATH);
        const assert = require('assert');

        const mockEl = {
          style: {},
          nodeType: 1,
          innerText: '0',
          getAttribute: () => '100',
          setAttribute: () => {}
        };
        global.document = {
          body: { contains: () => true },
          querySelectorAll: () => [mockEl]
        };

        // 1. Reduced motion preference
        const reducedAdapter = new AtlasMotionAdapter({ forceReducedMotion: true });
        assert.strictEqual(reducedAdapter.isReducedMotion(), true);
        const redRes = reducedAdapter.execute({
          id: 'masked-headline',
          targets: ['.hero h1 [data-line]'],
          reducedMotionFallback: { behavior: 'instant' }
        });
        assert.strictEqual(redRes.success, true);
        assert.strictEqual(redRes.mode, 'reduced-motion-fallback');
        assert.strictEqual(mockEl.style.transition, 'none');
        assert.strictEqual(mockEl.style.transform, 'none');

        // 2. Native CSS fallback when Anime is null
        const fallbackAdapter = new AtlasMotionAdapter({ anime: null, forceReducedMotion: false });
        const cssRes = fallbackAdapter.execute({
          id: 'shutter-image',
          targets: ['.hero [data-shutter]']
        });
        assert.strictEqual(cssRes.success, true);
        assert.strictEqual(cssRes.mode, 'native-css-fallback');
        assert.strictEqual(mockEl.style.opacity, '1');
        assert.strictEqual(mockEl.style.clipPath, 'inset(0)');

        // 3. Stillness pattern (intentional no-animation)
        const stillnessRes = fallbackAdapter.execute({ id: 'stillness' });
        assert.strictEqual(stillnessRes.success, true);
        assert.strictEqual(stillnessRes.mode, 'stillness');

        // 4. Missing / detached DOM elements
        global.document.querySelectorAll = () => [];
        const noopRes = fallbackAdapter.execute({
          id: 'masked-headline',
          targets: ['.detached-or-missing']
        });
        assert.strictEqual(noopRes.success, true);
        assert.strictEqual(noopRes.mode, 'no-op');

        console.log('UNIT_FALLBACK_AND_REDUCED_MOTION_PASSED');
        """

        env = os.environ.copy()
        env["ADAPTER_PATH"] = ADAPTER_PATH
        proc = subprocess.run(["node", "-e", node_script], env=env, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"Fallback and reduced motion unit test failed:\n{proc.stderr}")
        self.assertIn("UNIT_FALLBACK_AND_REDUCED_MOTION_PASSED", proc.stdout)

    def test_unit_adapter_lifecycle_cleanup_idempotence(self):
        """[UNIT] Verify that cleanup() is idempotent and safe to invoke repeatedly."""
        node_script = """
        const AtlasMotionAdapter = require(process.env.ADAPTER_PATH);
        const assert = require('assert');

        const adapter = new AtlasMotionAdapter();
        // Invoke cleanup multiple times on empty adapter
        assert.strictEqual(adapter.cleanup().success, true);
        assert.strictEqual(adapter.cleanup().success, true);
        assert.strictEqual(adapter.cleanup().success, true);
        assert.strictEqual(adapter.destroy('non-existent').success, true);

        console.log('UNIT_LIFECYCLE_IDEMPOTENCE_PASSED');
        """

        env = os.environ.copy()
        env["ADAPTER_PATH"] = ADAPTER_PATH
        proc = subprocess.run(["node", "-e", node_script], env=env, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"Lifecycle idempotence unit test failed:\n{proc.stderr}")
        self.assertIn("UNIT_LIFECYCLE_IDEMPOTENCE_PASSED", proc.stdout)

    # =========================================================================
    # Group B: Integration Tests (Real Anime.js v4 Binary)
    # =========================================================================

    def test_integration_real_animejs_v4_execution(self):
        """[INTEGRATION] Verify adapter with physically installed Anime.js v4.5.0 binary."""
        node_script = """
        global.getComputedStyle = (el) => ({
          getPropertyValue: (prop) => (el.style && el.style[prop]) || ''
        });

        const path = require('path');
        const animeV4 = require(path.join(process.env.NODE_MODULES_PATH, 'animejs'));
        const AtlasMotionAdapter = require(process.env.ADAPTER_PATH);
        const assert = require('assert');

        // 1. Verify real Anime.js v4 exports
        assert.strictEqual(typeof animeV4.animate, 'function', 'animejs.animate must be a function');
        assert.strictEqual(typeof animeV4.stagger, 'function', 'animejs.stagger must be a function');
        assert.strictEqual(typeof animeV4.cubicBezier, 'function', 'animejs.cubicBezier must be a function');
        assert.strictEqual(typeof animeV4.remove, 'function', 'animejs.remove must be a function');

        function createMockEl(val) {
          return {
            style: {},
            nodeType: 1,
            innerText: '0',
            getAttribute: (attr) => (attr === 'data-value' ? val : null),
            setAttribute: () => {}
          };
        }

        const el1 = createMockEl('150');
        const el2 = createMockEl('300');
        global.document = {
          body: { contains: () => true },
          querySelectorAll: () => [el1, el2]
        };

        // 2. Initialize adapter with installed real v4 engine
        const adapter = new AtlasMotionAdapter({ anime: animeV4 });

        // 3. Execute masked-headline with real stagger and cubicBezier
        const res = adapter.execute({
          id: 'masked-headline',
          targets: ['.hero h1 [data-line]'],
          timing: { durationMs: 400, delayMs: 50 },
          easing: { token: '--ease-expo' },
          stagger: { intervalMs: 80, startMs: 50 }
        });

        assert.strictEqual(res.success, true);
        assert.strictEqual(res.mode, 'animejs-v4');
        assert.ok(res.instance, 'Must produce a valid v4 animation instance');
        assert.strictEqual(adapter.activeInstances.size, 1);

        // 4. Test real v4 lifecycle destroy
        const destroyRes = adapter.destroy('masked-headline');
        assert.strictEqual(destroyRes.success, true);
        assert.strictEqual(res.instance.paused, true, 'Instance must be paused on destroy');
        assert.strictEqual(res.instance.cancelled, true, 'Instance must be cancelled on destroy');

        // 5. Test real v4 rolling-figures counter
        const rollRes = adapter.execute({
          id: 'rolling-figures',
          targets: ['.stat-number'],
          timing: { durationMs: 150 }
        });
        assert.strictEqual(rollRes.success, true);
        assert.strictEqual(rollRes.mode, 'animejs-v4-counter');

        // 6. Test real v4 cleanup
        const cleanRes = adapter.cleanup();
        assert.strictEqual(cleanRes.success, true);
        assert.strictEqual(adapter.activeInstances.size, 0);

        console.log('INTEGRATION_REAL_ANIME_V4_PASSED');
        """

        env = os.environ.copy()
        env["ADAPTER_PATH"] = ADAPTER_PATH
        env["NODE_MODULES_PATH"] = NODE_MODULES_PATH
        proc = subprocess.run(["node", "-e", node_script], env=env, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"Real Anime.js v4 integration test failed:\n{proc.stderr}")
        self.assertIn("INTEGRATION_REAL_ANIME_V4_PASSED", proc.stdout)


if __name__ == "__main__":
    unittest.main()
