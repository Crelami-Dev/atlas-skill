# Anime.js v4 Complete API Playbook & Anti-Slop Recipes

Reference manual for authentic **Anime.js v4 (`animejs@^4.0.0`)** implementation. Every snippet below uses verified v4 named exports.

## 1. Complete Named Import Map

```ts
import {
  animate,          // Core JS tween engine: animate(targets, parameters)
  createTimeline,   // Multi-step sequencer: createTimeline(parameters)
  createTimer,      // Precision timer callbacks: createTimer(parameters)
  createScope,      // Component root scoping, mediaQueries, & batch revert()
  createAnimatable, // High-frequency reactive setters (pointer/drag/scrubbing)
  createDraggable,  // Physics-enabled drag & snap controller
  createLayout,     // Automatic FLIP layout transitions across DOM/CSS changes
  onScroll,         // ScrollObserver controller passed to autoplay: onScroll(...)
  stagger,          // Time, value, & 2D grid stagger distributor
  spring,           // SwiftUI perceived ({ bounce, duration }) or physics ({ stiffness, damping, mass }) spring
  cubicBezier,      // Custom cubicBezier(x1, y1, x2, y2) easing generator
  eases,            // Built-in easing functions object
  splitText,        // Accessible responsive line/word/char text splitter
  scrambleText,     // Kinetic character decode/scramble utility (great for technical/CLI metrics)
  svg,              // { createDrawable, createMotionPath, morphTo }
  waapi,            // { animate, convertEase } lightweight Web Animations API engine
  utils,            // { $, get, set, remove, cleanInlineStyles, random, clamp, lerp, damp, mapRange, sync }
  engine,           // Global engine configuration (pauseOnDocumentHidden, fps, timeUnit)
} from 'animejs';
```

## 2. Built-in v4 Easing Strings (No `ease` Prefix!)

- Smooth UI entrances: `'outQuart'`, `'outQuint'`, `'outExpo'`, `'outCubic'`
- Symmetrical state shifts: `'inOutCubic'`, `'inOutQuart'`, `'inOutQuint'`, `'inOutExpo'`
- Crisp exits: `'inQuad'`, `'inCubic'`
- Parametric power/elastic: `'out(3)'`, `'inOut(4)'`, `'outBack(1.4)'`, `'outElastic(1, .6)'`
- Tactile springs: `spring({ bounce: 0.2, duration: 480 })` (perceived model; keep `bounce` between `-0.3` and `0.35` for professional UI—avoid cartoonish `bounce > 0.6`!)

## 3. Recipe A: Masked Editorial Headline (`splitText` + `createScope`)

```ts
import { animate, createScope, splitText, stagger } from 'animejs';

export function initEditorialHeading(rootEl: HTMLElement) {
  return createScope({
    root: rootEl,
    mediaQueries: { reduceMotion: '(prefers-reduced-motion: reduce)' },
  }).add((self) => {
    if (self.matches.reduceMotion) return;

    const split = splitText('[data-split-heading]', {
      lines: { wrap: 'clip' },
      accessible: true,
    });

    split.addEffect(({ lines }) =>
      animate(lines, {
        y: ['105%', '0%'],
        opacity: [0, 1],
        duration: 640,
        delay: stagger(75),
        ease: 'outExpo',
      })
    );

    return () => split.revert();
  });
}
```

## 4. Recipe B: Scroll-Triggered Section Reveal & Scrubbed Progress (`onScroll`)

```ts
import { animate, createScope, onScroll, stagger } from 'animejs';

export function initScrollSection(sectionEl: HTMLElement) {
  return createScope({
    root: sectionEl,
    mediaQueries: { reduceMotion: '(prefers-reduced-motion: reduce)' },
  }).add((self) => {
    if (self.matches.reduceMotion) return;

    // 1. Trigger once when entering viewport
    animate('[data-step-item]', {
      y: [20, 0],
      opacity: [0, 1],
      duration: 520,
      delay: stagger(65),
      ease: 'outQuart',
      autoplay: onScroll({
        target: sectionEl,
        enter: 'bottom-=12% top',
        leave: 'top bottom',
      }),
    });

    // 2. Smoothly scrubbed progress bar tied to reading scroll
    animate('[data-reading-bar]', {
      scaleX: [0, 1],
      ease: 'linear',
      autoplay: onScroll({
        target: sectionEl,
        enter: 'top center',
        leave: 'bottom center',
        sync: 0.35, // Smooth damped scroll sync
      }),
    });
  });
}
```

## 5. Recipe C: Seamless Filter / Tab / Bento FLIP Transition (`createLayout`)

Whenever filtering cards, switching tabs, or toggling compact/expanded views, `createLayout` eliminates abrupt DOM jumps:

```ts
import { createLayout } from 'animejs';

export function transitionFilteredGrid(gridContainer: HTMLElement, mutateStateSync: () => void) {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    mutateStateSync();
    return;
  }
  const layout = createLayout(gridContainer, {
    duration: 380,
    ease: 'outQuart',
  });
  layout.record();
  mutateStateSync(); // Update DOM / flushSync state change
  layout.animate();
}
```

## 6. Recipe D: SVG Architecture / Route Line Drawing & Morphing (`svg`)

```ts
import { animate, stagger, svg } from 'animejs';

// Draw SVG strokes cleanly without manual strokeDasharray math
animate(svg.createDrawable('svg [data-route-line]'), {
  draw: ['0 0', '0 1'],
  duration: 900,
  delay: stagger(120),
  ease: 'inOutQuart',
});

// Morph between two SVG <path> / <polygon> shapes
animate('#icon-shape-primary', {
  d: svg.morphTo('#icon-shape-active'),
  duration: 360,
  ease: 'outQuart',
});
```

## 7. Recipe E: Zero-Rerender Interactive Spotlight / Magnetic Control (`createAnimatable`)

Never put `onMouseMove` coordinates into React `useState`! Use `createAnimatable` so 60-120fps pointer tracking bypasses VDOM renders completely:

```ts
import { createAnimatable } from 'animejs';

export function attachMagneticButton(btn: HTMLElement) {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return () => {};

  const magnetic = createAnimatable(btn, {
    x: 220,
    y: 220,
    ease: 'out(3)',
  });

  const onMove = (e: PointerEvent) => {
    const rect = btn.getBoundingClientRect();
    const dx = (e.clientX - (rect.left + rect.width / 2)) * 0.18;
    const dy = (e.clientY - (rect.top + rect.height / 2)) * 0.18;
    magnetic.x(dx);
    magnetic.y(dy);
  };

  const onLeave = () => {
    magnetic.x(0);
    magnetic.y(0);
  };

  btn.addEventListener('pointermove', onMove);
  btn.addEventListener('pointerleave', onLeave);
  return () => {
    btn.removeEventListener('pointermove', onMove);
    btn.removeEventListener('pointerleave', onLeave);
    magnetic.revert();
  };
}
```
