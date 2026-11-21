# Self-playing loops: motion that keeps going, politely

Scenes react to scroll. **Loops** play on their own and start over: a demo that types a command, runs, shows a result and begins again; words that swap in place; a ticker; a soft ambient glow. They are how a static page shows a product doing something.

Templates: `atlas-loops.mjs`, `atlas-loops.css`; demo: `templates/atlas-loops-demo.html`; browser proof: `tests/loops.test.mjs`.

```html
<link rel="stylesheet" href="assets/css/atlas-loops.css">
<script type="module">
  import { initAtlasLoops } from './assets/js/atlas-loops.mjs';
  const loops = await initAtlasLoops({ anime: await import('https://cdn.jsdelivr.net/npm/animejs@4/+esm') });
</script>
```

## The five pieces

### 1. Replayable demo card: `[data-loop]`
A mini interface that plays a short story and repeats: **type a line, run a progress bar, bring in rows, pulse the chips, show the result, hold, reset, repeat.** Every part is optional.

```html
<div class="atlas-loop" data-loop data-loop-hold="1800" role="img" aria-label="One sentence saying what this shows.">
  <div class="atlas-loop__bar"><span>assets.mjs</span><code>--license safe</code></div>
  <div class="atlas-loop__field">
    <span data-loop-type="roasted coffee beans">roasted coffee beans</span><i class="atlas-loop__caret"></i>
  </div>
  <i class="atlas-loop__progress" data-loop-progress></i>
  <ul class="atlas-loop__rows">
    <li class="atlas-loop__row" data-loop-row>
      <span class="atlas-loop__text"><span class="atlas-loop__title">Green coffee</span><span class="atlas-loop__meta">Wikimedia</span></span>
      <span class="atlas-loop__chip" data-loop-chip>CC BY-SA<i class="atlas-loop__ring" data-loop-ring></i></span>
    </li>
  </ul>
  <div class="atlas-loop__foot" data-loop-foot><span>3 saved to assets/</span><span>credits recorded</span></div>
</div>
```
- The markup is the **finished frame**. Without JS, with Anime.js blocked or under reduced motion that is what people see.
- Add `atlas-loop--terminal` for an inverted terminal card; several `data-loop-type` lines type one after another.
- Content must be true: use real command names and real captured output, label an illustration as an illustration. A loop that fakes results is a fabricated claim.
- Starts when 15% is visible (same rule as everything else), pauses off screen, resumes when visible again.

### 2. Rotating words: `[data-rotate]`
```html
<h1><span class="sr-only">Build tidy, fast, responsive UI.</span>
  <span aria-hidden="true">Build <span class="atlas-rotator" data-rotate="2600"><span>tidy</span><span>fast</span><span>responsive</span></span> UI</span></h1>
```
All words share one grid cell, so the widest word fixes the width and nothing around it jumps. Give screen readers one static sentence; the script hides the extra words from them. 3-5 real words, each short.

### 3. Ticker: `[data-marquee]`
```html
<div class="atlas-marquee" data-marquee data-speed="40">
  <div class="atlas-marquee__track"><ul class="atlas-marquee__group"><li>Codex</li><li>Cursor</li> …</ul></div>
</div>
```
The script repeats the group until one scrolling half covers the viewport, then duplicates it once for a seamless loop (copies are hidden from assistive tech, have no ids and are out of the tab order), and sets the speed in pixels per second. It recomputes when the width changes. It pauses on hover and focus (tracked separately, so leaving with the pointer never releases a focus hold) and while off screen. `data-direction="right"` reverses it. Without the script it is a wrapping row.

### 4. Ambient layer: `.atlas-fx`
CSS-only glow, rings and marks (`<div class="atlas-fx" aria-hidden="true"><i class="atlas-fx__glow"></i><i class="atlas-fx__ring"></i><i class="atlas-fx__ring atlas-fx__ring--2"></i><i class="atlas-fx__mark"></i></div>`) inside a positioned, `overflow: hidden` parent. One per section. `.atlas-float` is a gentle drift for a decorative card behind a demo. They pause off screen and with the page-level toggle.
Do **not** float the card that holds a pause button: a moving button is hard to hit.

### 5. Page-level pause: `[data-loops-toggle]`
A single button that pauses and resumes every loop on the page (`aria-pressed`, labelled in the page language). It satisfies the pause rule for all loops at once.

## Rules (they are enforced, not suggestions)
| Rule | Why | How |
|---|---|---|
| Anything that moves on its own for more than 5 s can be paused | WCAG 2.2.2 | a pause button on each demo and ticker (built automatically, 44 px). Rotators and ambient layers have none of their own, so they obey the page-level `[data-loops-toggle]`; if the page has none, one floating button is **added automatically**. `quick-check` warns `loop-no-pause` |
| Pause while off screen | battery, CPU, focus | IntersectionObserver; state in `data-loop-state` (`playing`, `paused`, `user-paused`, `static`) |
| Reduced motion means still | vestibular safety | demos show the finished frame, rotators show the first word, tickers wrap and scroll; no pause buttons appear |
| No layout shift | stability | rotators reserve the widest word; typed lines keep an invisible copy of the finished text in the same grid cell, so a card never changes height, even when a long line wraps on a phone |
| A user's pause is respected | control | scrolling away and back does not restart a paused loop |
| Real content only | honesty | commands, names and numbers come from the facts file |

Budget: at most **one demo card playing per screen**, one ambient layer per section, one ticker per page. Loops compete with scenes for attention; if the page has a pinned scene, keep loops small and away from it.

## Translating a page that has loops
Typed text lives in `data-loop-type`. When your language switch changes text, set both the attribute and the text, then re-read:
```js
el.dataset.loopType = newText; el.textContent = newText;   // for each typed line
await loops.refresh();                                      // rebuilds demos and rotators
loops.animated                                              // false when motion is reduced or Anime.js did not load
```

## Checklist
1. Does it show something true, in one short story, that words would explain worse?
2. Is the finished frame correct on its own (view the page with JS off)?
3. Is there a pause control, and does it work by touch (44 px)?
4. Does nothing around it move when a word or line changes?
5. Reduced motion on: does everything stand still and stay readable?
6. `tests/loops.test.mjs` shows the proof in a real browser; run `quick-check.mjs` and open the screenshots.
