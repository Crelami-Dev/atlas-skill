---
name: atlas-motion-animejs
description: "Use when designing or implementing web animations, FLIP layout transitions, scroll choreography, and spring physics with Anime.js v4 (animejs@^4.0.0). Do not use for simple color hover effects handled cleanly by CSS transitions."
---

# Atlas Motion Engine — Anime.js v4 Choreography

Use **Anime.js v4 (`animejs@^4.0.0`)** when an interface needs deliberate **15%-viewport scroll reveals (`850–1050ms`)**, continuous **Signature Scroll Scenes (`atlas-scenes.mjs`)**, spring physics, FLIP layout transitions, or SVG path drawing. For single-property hover changes, use standard CSS `transition` rules.

Read the [Anime.js v4 Playbook](../../references/animejs-v4-playbook.md), [Scope Helper Template](../../templates/animejs-v4-scope.ts), and **Signature Scroll Scene Engine** ([atlas-scenes.mjs](../../templates/atlas-scenes.mjs) + [atlas-scenes.css](../../templates/atlas-scenes.css)) before writing animation code.

- **Plain HTML / No-Bundler Projects:** Copy `templates/atlas-scenes.mjs` + `templates/atlas-scenes.css` alongside your site and import Anime.js v4 from **`https://cdn.jsdelivr.net/npm/animejs@4/+esm`** (never leave a landing page static/un-animated unless reduced motion is active).
- **Signature Scroll Scenes (`data-atlas-scene`):** Use **at most 1 continuous scroll-scrubbed scene per page** (`window-reveal`, `mask-zoom`, `type-parting`, or `parallax-depth`) driven via `onScroll({ enter: 'top top', leave: 'bottom bottom', sync: 0.3 })`. It automatically switches to crisp static `.is-rest` on `< 768px` mobile and `prefers-reduced-motion: reduce` without forcing `100svh` voids on ordinary sections.

## 1. Anime.js v4 Syntax vs Legacy v3

Never mix Anime.js v3 syntax into a v4 codebase, as module exports and option keys have changed and fail at runtime:

| Capability | Legacy v3 Syntax (Blocked by Linter) | Official Anime.js v4 Syntax |
|---|---|---|
| Module Import | `import anime from 'animejs'` | `import { animate, createTimeline, createScope, stagger, spring, onScroll } from 'animejs'` |
| Basic Call | `anime({ targets: '.card', translateY: 20 })` | `animate('.card', { y: [20, 0], opacity: [0, 1] })` |
| Property & Ease Name | `easing: 'easeOutExpo'` | `ease: 'outExpo'` |
| Spring Physics | `easing: 'spring(1, 80, 10, 0)'` | `ease: spring({ bounce: 0.25, duration: 500 })` |
| Timeline | `anime.timeline({ ... })` | `createTimeline({ defaults: { ease: 'outQuart' } })` |
| Stagger | `delay: anime.stagger(60)` | `delay: stagger(60, { from: 'first' })` |
| Alternation | `direction: 'alternate'` | `alternate: true` or `reversed: true` |
| Scroll Trigger (15% In-View) | Manual IntersectionObserver without cleanup | `autoplay: onScroll({ target, enter: 'bottom-=15% top', leave: 'top bottom', sync: 'play none', repeat: false })` or `initAtlasMotion({ threshold: 0.15 })` |
| Text Splitting | Third-party SplitType | `splitText(el, { lines: { wrap: 'clip' }, words: true })` |
| SVG Line Drawing | `strokeDashoffset: [anime.setDashoffset, 0]` | `animate(svg.createDrawable('path.route'), { draw: ['0 0', '0 1'] })` |
| FLIP Layout Transitions | Manual bounding-box diffs | `const layout = createLayout(root); layout.record(); updateDOM(); layout.animate();` |
| Lifecycle Cleanup | `anime.remove()` | `const scope = createScope({ root }).add(...); return () => scope.revert();` |

## 2. Isolate Lifecycle with `createScope()`

Wrap component animation initialization inside `createScope({ root, mediaQueries })` and call `scope.revert()` on unmount so scroll listeners and timers never leak:

```tsx
'use client';
import { useEffect, useRef } from 'react';
import { createScope, createTimeline, stagger } from 'animejs';

export function HeroShowcase() {
  const rootRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (!rootRef.current) return;
    const scope = createScope({
      root: rootRef.current,
      mediaQueries: { reduceMotion: '(prefers-reduced-motion: reduce)' },
    }).add((self) => {
      if (self.matches.reduceMotion) return;
      createTimeline({ defaults: { ease: 'outQuart', duration: 520 } })
        .add('[data-hero-title]', { opacity: [0, 1], y: [18, 0] })
        .add('[data-hero-cta]', { opacity: [0, 1], y: [12, 0], delay: stagger(60) }, '-=280');
    });
    return () => scope.revert();
  }, []);

  return <section ref={rootRef} data-hero>...</section>;
}
```

## 3. Progressive Visibility & GPU Performance

- **Never Hide Content in Static CSS:** Never write `[data-reveal] { opacity: 0; }` in global CSS, or SSR, slow networks, and disabled-JS browsers will show a blank page. Leave elements visible by default and pass `opacity: [0, 1]` keyframes inside `animate()`.
- **Animate GPU-Composited Properties:** Animate `x`, `y`, `scale`, `scaleX`, `scaleY`, `rotate`, or `opacity`, avoiding `top`, `left`, `width`, or `height` which trigger per-frame layout reflows.
- **Make Motion Clearly Visible:** Trigger section reveals once **15%** enters the viewport (`threshold: 0.15` / `enter: 'bottom-=15% top'`) using deliberate durations (`850–1050ms`) and real travel (`y: [36, 0], opacity: [0.14, 1], scale: [0.975, 1]`, keeping total chain `< 1500ms`)—never tiny imperceptible `opacity: [0.85, 1]` micro-nudges.
- **Duration Cap:** Keep single entrance sequences under `1500ms` (`850–1050ms` ideal) so motion feels luxurious without delaying interaction.

## Verification Command

Run `node <atlas>/scripts/check-motion-v4.mjs <project-root>` to verify v4 syntax, `createScope` cleanup, and zero static `opacity: 0` traps.
