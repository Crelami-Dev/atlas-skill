# Motion Resilience, Causality, and Lifecycle Contract

Motion explains spatial continuity, hierarchy, or cause-and-effect state changes. It is never a substitute for weak typography or missing content.

## 1. Tool Selection Ladder

1. **CSS Transitions (`var(--duration-micro)`, `var(--ease-standard)`)**: Simple single-element hover, focus ring, border, or color state feedback (`120ms - 220ms`).
2. **Anime.js v4 `waapi.animate()`**: Lightweight hardware-accelerated multi-target opacity/transform micro-feedback.
3. **Anime.js v4 Core (`animate`, `createTimeline`, `createScope`, `onScroll`, `createLayout`, `splitText`, `svg`, `spring`)**: Coordinated multi-element choreography, masked text reveals, FLIP layout changes, scroll-linked progress, draggable physics, and SVG line/shape animations. See [atlas-motion-animejs](../skills/atlas-motion-animejs/SKILL.md) and [Anime.js v4 Playbook](animejs-v4-playbook.md).

## 2. Visibility & Progressive Enhancement Contract

- **Start Visible in Static CSS:** Never write static CSS rules like `.reveal { opacity: 0; }` that leave sections invisible if JavaScript fails, SSR streams slowly, or automated screenshots run before scroll observers fire.
- **No Pointer Traps:** Never animate a button away from the user's cursor on hover or block click/submit handlers until an animation finishes.
- **Rapid Input Interruption:** Rapidly clicking tabs, filters, or toggles must smoothly interrupt or replace in-flight animations rather than queueing laggy backlogs.

## 3. Lifecycle & Cleanup Ownership

Every animation, ScrollObserver, TextSplitter, Draggable, or Animatable instance must have a deterministic cleanup owner:

- Wrap component effects inside `const scope = createScope({ root }).add(...)` and return `() => scope.revert()` on unmount.
- Restore only animation-owned inline styles (`scope.revert()` or `utils.cleanInlineStyles(animation)`) without stripping legitimate static transforms.

## 4. Accessibility (`prefers-reduced-motion`) & Timing Caps

- Honor `(prefers-reduced-motion: reduce)` in both CSS tokens and `createScope({ mediaQueries })`: skip spatial travel (`x`/`y`/parallax/scrubbing) and render the complete final state immediately or via subtle `<150ms` opacity crossfade.
- Keep total entrance choreography (including stagger tails) under `1500ms` so visitors can read and act without waiting.
