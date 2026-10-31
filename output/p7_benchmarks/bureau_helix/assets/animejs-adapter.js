/**
 * Atlas Anime.js Motion Adapter (v2.0.0 — Anime.js v4 Official Target)
 * 
 * Translates validated Atlas/Taste motion specifications into production-grade,
 * lifecycle-managed animations using the official Anime.js v4 modular/core API,
 * with bulletproof reduced-motion fallbacks, DOM detachment resilience,
 * and graceful degradation to native CSS styling when anime.js is not loaded.
 * 
 * Version & API Scope:
 * - Targets Anime.js v4.x official API (animate(targets, params), stagger(), cubicBezier(), eases, remove()).
 * - Resolves easing tokens to cubicBezier functions to comply with v4 easing requirements.
 * - In the absence of Anime.js v4, safely degrades to native CSS styling (static opacity
 *   and transform reset) without throwing runtime exceptions.
 * - Full prefers-reduced-motion compliance (instant reveal, zero spatial translation).
 * - Complete teardown and idempotent memory cleanup via pause(), cancel(), and remove().
 * 
 * Zero external compile dependencies. Compatible with modern browsers and Node test runners.
 */

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define([], factory);
  } else if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.AtlasMotionAdapter = factory();
  }
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  // Recognized Bézier curves from Taste research (coordinates for v4 cubicBezier)
  var BEZIER_COORDS = {
    '--ease-out': [0.22, 1, 0.36, 1],
    '--ease-expo': [0.16, 1, 0.3, 1],
    '--ease-in-out': [0.76, 0, 0.24, 1],
    '--ease-soft': [0.33, 1, 0.68, 1],
    '--ease-exit': [0.55, 0.055, 0.675, 0.19],
    'linear': 'linear'
  };

  // Supported pattern catalogue (18 patterns)
  var SUPPORTED_PATTERNS = [
    'masked-headline',
    'shutter-image',
    'scaling-wordmark',
    'pinned-story',
    'index-preview',
    'curtain-footer',
    'slow-crossfade',
    'edge-marquee',
    'drag-row',
    'colour-on-scroll',
    'stillness',
    'opening-window',
    'ink-fill',
    'sheet-over',
    'sideways-gallery',
    'pushed-line',
    'rolling-figures',
    'carried-picture'
  ];

  function AtlasMotionAdapter(options) {
    options = options || {};
    this.options = options;
    
    // Resolve Anime.js v4 engine
    if (options.anime !== undefined) {
      this.animeEngine = options.anime;
    } else {
      var engine = null;
      if (typeof window !== 'undefined') {
        engine = window.anime || (typeof window.animate === 'function' ? window : null);
      }
      if (!engine && typeof globalThis !== 'undefined') {
        engine = globalThis.anime || (typeof globalThis.animate === 'function' ? globalThis : null);
      }
      if (!engine && typeof require === 'function') {
        try {
          engine = require('animejs');
        } catch (e) {
          engine = null;
        }
      }
      this.animeEngine = engine;
    }

    this.activeInstances = new Map();
    this.activeObservers = [];
    this.activeListeners = [];
    this._reducedMotionOverride = options.forceReducedMotion !== undefined ? options.forceReducedMotion : null;
  }

  /**
   * Check if prefers-reduced-motion is currently active.
   */
  AtlasMotionAdapter.prototype.isReducedMotion = function () {
    if (this._reducedMotionOverride !== null) {
      return Boolean(this._reducedMotionOverride);
    }
    if (typeof window !== 'undefined' && window.matchMedia) {
      return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    }
    return false;
  };

  /**
   * Return array of all supported motion pattern IDs.
   */
  AtlasMotionAdapter.prototype.getSupportedPatterns = function () {
    return SUPPORTED_PATTERNS.slice();
  };

  /**
   * Resolve targets safely. Handles strings, elements, or arrays.
   * Returns empty array if targets are missing or detached from DOM.
   */
  AtlasMotionAdapter.prototype.resolveTargets = function (targetSpec) {
    if (!targetSpec) return [];
    if (typeof targetSpec === 'string') {
      if (typeof document === 'undefined') return [];
      try {
        var nodeList = document.querySelectorAll(targetSpec);
        return Array.prototype.slice.call(nodeList).filter(function (el) {
          return document.body && document.body.contains(el);
        });
      } catch (e) {
        return [];
      }
    }
    if (Array.isArray(targetSpec)) {
      var self = this;
      var out = [];
      targetSpec.forEach(function (t) {
        out = out.concat(self.resolveTargets(t));
      });
      return out;
    }
    if (typeof targetSpec === 'object' && targetSpec.nodeType) {
      if (typeof document !== 'undefined' && document.body && document.body.contains(targetSpec)) {
        return [targetSpec];
      }
    }
    return [];
  };

  /**
   * Resolve easing parameter for Anime.js v4.
   */
  AtlasMotionAdapter.prototype.resolveEase = function (engine, easingToken, bezierString) {
    var coords = BEZIER_COORDS[easingToken] || BEZIER_COORDS['--ease-expo'];
    if (coords === 'linear') {
      return (engine && engine.eases && engine.eases.linear) ? engine.eases.linear : 'linear';
    }
    if (Array.isArray(coords) && engine && typeof engine.cubicBezier === 'function') {
      return engine.cubicBezier(coords[0], coords[1], coords[2], coords[3]);
    }
    if (bezierString && engine && typeof engine.cubicBezier === 'function') {
      var m = bezierString.match(/\(([^)]+)\)/);
      if (m) {
        var parts = m[1].split(',').map(function (s) { return parseFloat(s.trim()); });
        if (parts.length === 4 && !parts.some(isNaN)) {
          return engine.cubicBezier(parts[0], parts[1], parts[2], parts[3]);
        }
      }
    }
    if (engine && engine.eases && engine.eases.outExpo) {
      return engine.eases.outExpo;
    }
    return 'out(2)';
  };

  /**
   * Execute a motion pattern specification.
   */
  AtlasMotionAdapter.prototype.execute = function (motionSpec) {
    if (!motionSpec || !motionSpec.id) {
      return { success: false, reason: 'Invalid motion spec: missing pattern id' };
    }

    var id = motionSpec.id;
    if (SUPPORTED_PATTERNS.indexOf(id) === -1) {
      return { success: false, reason: 'Unsupported motion pattern: ' + id };
    }

    // 1. Stillness pattern: intentional zero animation
    if (id === 'stillness') {
      return {
        success: true,
        patternId: id,
        mode: 'stillness',
        message: 'Stillness pattern applied: zero entrance animation, instant UI interactivity.'
      };
    }

    // 2. Reduced motion handling
    if (this.isReducedMotion()) {
      return this.applyReducedMotionFallback(motionSpec);
    }

    // 3. Resolve DOM targets
    var targets = this.resolveTargets(motionSpec.targets);
    if (!targets.length) {
      return {
        success: true,
        patternId: id,
        mode: 'no-op',
        message: 'No matching or attached DOM targets found for pattern ' + id
      };
    }

    // 4. Check Anime.js v4 engine availability
    var engine = this.animeEngine;
    if (!engine || (typeof engine.animate !== 'function' && typeof engine !== 'function')) {
      // Graceful degradation to native CSS fallback
      return this.applyNativeCssFallback(motionSpec, targets);
    }

    // 5. Execute via Anime.js v4 API
    try {
      return this.executeWithAnimeV4(engine, motionSpec, targets);
    } catch (err) {
      // If Anime.js execution fails, fall back to native CSS without throwing
      return this.applyNativeCssFallback(motionSpec, targets);
    }
  };

  /**
   * Apply Anime.js v4 animation based on pattern configuration.
   */
  AtlasMotionAdapter.prototype.executeWithAnimeV4 = function (engine, spec, targets) {
    var animateFn = typeof engine.animate === 'function' ? engine.animate.bind(engine) : engine;
    var staggerFn = typeof engine.stagger === 'function' ? engine.stagger.bind(engine) : null;

    var easingToken = (spec.easing && spec.easing.token) || '--ease-expo';
    var bezierString = spec.easing && spec.easing.bezier;
    var ease = this.resolveEase(engine, easingToken, bezierString);

    var duration = (spec.timing && spec.timing.durationMs) !== undefined ? spec.timing.durationMs : 800;
    var delay = (spec.timing && spec.timing.delayMs) || 0;

    var animOptions = {
      duration: duration,
      delay: delay,
      ease: ease
    };

    // Stagger configuration (v4 stagger(interval, { start, from }))
    if (spec.stagger && spec.stagger.intervalMs && staggerFn) {
      animOptions.delay = staggerFn(spec.stagger.intervalMs, {
        start: spec.stagger.startMs || delay,
        from: spec.stagger.from || 'first'
      });
    }

    // Specific pattern properties in v4 format
    switch (spec.id) {
      case 'masked-headline':
        animOptions.translateY = ['105%', '0%'];
        animOptions.opacity = [1, 1];
        break;

      case 'shutter-image':
        animOptions.clipPath = ['inset(0 100% 0 0)', 'inset(0 0% 0 0)'];
        animOptions.scale = [1.12, 1.0];
        break;

      case 'scaling-wordmark':
        animOptions.scale = [1.0, 1.08];
        break;

      case 'pinned-story':
        animOptions.opacity = [0.8, 1.0];
        break;

      case 'index-preview':
        animOptions.opacity = [0, 1];
        animOptions.scale = [0.96, 1.0];
        break;

      case 'curtain-footer':
        animOptions.translateY = ['10%', '0%'];
        animOptions.opacity = [0.9, 1.0];
        break;

      case 'slow-crossfade':
        animOptions.opacity = [0, 1];
        break;

      case 'edge-marquee':
        animOptions.translateX = ['0%', '-50%'];
        animOptions.loop = true;
        animOptions.ease = (engine.eases && engine.eases.linear) ? engine.eases.linear : 'linear';
        break;

      case 'drag-row':
        animOptions.opacity = [0.95, 1.0];
        break;

      case 'colour-on-scroll':
        animOptions.opacity = [0.9, 1.0];
        break;

      case 'opening-window':
        animOptions.scale = [1.1, 1.0];
        animOptions.opacity = [0.8, 1.0];
        break;

      case 'ink-fill':
        animOptions.opacity = [0.45, 1.0];
        break;

      case 'sheet-over':
        animOptions.translateY = ['5%', '0%'];
        break;

      case 'sideways-gallery':
        animOptions.translateX = ['0%', '-30%'];
        break;

      case 'pushed-line':
        animOptions.translateX = ['-10%', '0%'];
        animOptions.opacity = [0, 1];
        break;

      case 'carried-picture':
        animOptions.scale = [0.98, 1.0];
        animOptions.opacity = [0.9, 1.0];
        break;

      case 'rolling-figures':
        // Rolling figure counter with v4 onUpdate
        var self = this;
        targets.forEach(function (el) {
          var targetVal = parseFloat(el.getAttribute('data-value') || el.innerText || '0');
          var counter = { val: 0 };
          var counterAnim = animateFn(counter, {
            val: targetVal,
            duration: duration,
            ease: ease,
            onUpdate: function () {
              el.innerText = Math.round(counter.val).toLocaleString();
            }
          });
          self.activeInstances.set(spec.id + '-' + Math.random().toString(36).substr(2, 5), counterAnim);
        });
        return {
          success: true,
          patternId: spec.id,
          mode: 'animejs-v4-counter',
          targetsCount: targets.length
        };

      default:
        if (spec.adapterConfig && spec.adapterConfig.anime) {
          Object.assign(animOptions, spec.adapterConfig.anime);
        } else {
          animOptions.opacity = [0, 1];
          animOptions.translateY = ['20px', '0px'];
        }
        break;
    }

    // Call v4 animate(targets, animOptions)
    var anim = animateFn(targets, animOptions);
    this.activeInstances.set(spec.id, anim);

    return {
      success: true,
      patternId: spec.id,
      mode: 'animejs-v4',
      instance: anim,
      targetsCount: targets.length
    };
  };

  /**
   * Graceful fallback when Anime.js is not present: applies instant CSS styles or native transitions.
   */
  AtlasMotionAdapter.prototype.applyNativeCssFallback = function (spec, targets) {
    targets.forEach(function (el) {
      el.style.opacity = '1';
      el.style.transform = 'none';
      if (spec.id === 'shutter-image' || el.style.clipPath) el.style.clipPath = 'inset(0)';
      if (spec.id === 'rolling-figures') {
        var targetVal = el.getAttribute('data-value');
        if (targetVal) el.innerText = targetVal;
      }
    });

    return {
      success: true,
      patternId: spec.id,
      mode: 'native-css-fallback',
      message: 'Anime.js not detected; native CSS styling safely applied without layout disturbance.',
      targetsCount: targets.length
    };
  };

  /**
   * Apply accessible reduced-motion fallback (instant reveal, zero spatial translation).
   */
  AtlasMotionAdapter.prototype.applyReducedMotionFallback = function (spec) {
    var targets = this.resolveTargets(spec.targets);
    var fallback = spec.reducedMotionFallback || { behavior: 'instant' };

    targets.forEach(function (el) {
      el.style.transition = 'none';
      el.style.animation = 'none';
      el.style.transform = 'none';
      el.style.opacity = '1';
      if (spec.id === 'shutter-image' || el.style.clipPath) el.style.clipPath = 'inset(0)';

      if (spec.id === 'rolling-figures') {
        var targetVal = el.getAttribute('data-value');
        if (targetVal) el.innerText = targetVal;
      }
    });

    return {
      success: true,
      patternId: spec.id,
      mode: 'reduced-motion-fallback',
      behavior: fallback.behavior || 'instant',
      targetsCount: targets.length
    };
  };

  /**
   * Stop and remove a specific active animation pattern instance using v4 API.
   */
  AtlasMotionAdapter.prototype.destroy = function (patternId) {
    if (!patternId) return this.cleanup();
    var instance = this.activeInstances.get(patternId);
    if (instance) {
      if (typeof instance.pause === 'function') instance.pause();
      if (typeof instance.cancel === 'function') instance.cancel();

      var engine = this.animeEngine;
      if (engine && typeof engine.remove === 'function') {
        try {
          if (instance.targets) engine.remove(instance.targets);
        } catch (e) {}
      }
      this.activeInstances.delete(patternId);
      return { success: true, patternId: patternId, message: 'Pattern instance stopped and cleaned up.' };
    }
    return { success: true, patternId: patternId, message: 'No active instance found for pattern.' };
  };

  /**
   * Clean up all active animation instances, observers, and listeners using v4 lifecycle.
   * Fully idempotent: safe to invoke repeatedly without side effects.
   */
  AtlasMotionAdapter.prototype.cleanup = function () {
    var engine = this.animeEngine;
    this.activeInstances.forEach(function (instance) {
      if (instance) {
        if (typeof instance.pause === 'function') instance.pause();
        if (typeof instance.cancel === 'function') instance.cancel();
        if (engine && typeof engine.remove === 'function' && instance.targets) {
          try { engine.remove(instance.targets); } catch (e) {}
        }
      }
    });
    this.activeInstances.clear();

    this.activeObservers.forEach(function (obs) {
      if (obs && typeof obs.disconnect === 'function') obs.disconnect();
    });
    this.activeObservers = [];

    this.activeListeners.forEach(function (listener) {
      if (listener && typeof listener.remove === 'function') listener.remove();
    });
    this.activeListeners = [];

    return { success: true, message: 'All active motion instances and observers cleaned up.' };
  };

  return AtlasMotionAdapter;
}));
