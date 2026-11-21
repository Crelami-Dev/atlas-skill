# Scenes: ten ways to make one moment worth scrolling for

A scene is one choreographed section tied to scroll. Atlas ships ten, in two weights, and a dealer that picks by what the subject has to show. The point is variety with a reason: a villa studio and a coffee roaster should not get the same moment.

**Budget per page:** at most **one heavy** scene (desktop; phones get the finished composition) and at most **two light** scenes from different families. A page may use none: documents, legal text and plain brochures usually should.

## Choosing

```sh
node <atlas>/scripts/deal-scene.mjs --prompt "<the brief>" --project <root> --write
```

The dealer reads the subject (place, product, process, proof, portfolio, event, software, docs), scores each scene against it, adds a seeded jitter so near-ties differ between projects, and avoids scenes used earlier in this project (`.atlas-scenes.json`). If nothing fits it returns no heavy scene: that is a valid result; spend the effort on the hero instead.

Record the choice in the brief under `## Signature idea` as `scene: <id>` (or `scene: none`) with one line on why it serves this visitor.

## Wiring

```html
<link rel="stylesheet" href="assets/css/atlas-scenes.css">
<section class="atlas-scene" data-atlas-scene="pull-back"> … </section>
<script type="module">
  import { initAtlasMotion } from './assets/js/atlas-scenes.mjs';
  initAtlasMotion({ anime: await import('https://cdn.jsdelivr.net/npm/animejs@4/+esm') });
</script>
```

Without JS, on phones (heavy scenes) and under `prefers-reduced-motion` every scene shows a complete, readable composition. Never write `opacity: 0` in static CSS for scene content. `templates/atlas-scenes-demo.html` shows all ten with working markup; open it with `?scene=<id>` to isolate one.

## Heavy scenes (sticky, ~1.45 viewports; one per page)

### pull-back
A tight crop of one detail pulls back until the whole subject is in frame; the caption changes from the detail's line to the whole's line.
Fits place, product, portfolio. Needs one high-resolution photo whose whole and a detail both read, a 4-8 word detail line, a 6-12 word whole line. Options: `data-zoom` (default 1.8), `data-origin="30% 62%"` (the detail's position). **Crispness rule:** at the start the photo is magnified `data-zoom` times, so its pixel width must be at least `zoom x displayed width` (a 1280 px frame at zoom 1.8 needs about 2300 px). With a 1600 px photo keep the zoom at 1.2-1.3, or fetch a bigger file with `fetch-photos.mjs --width 3200`.
```html
<section class="atlas-scene" data-atlas-scene="pull-back" data-zoom="1.8" data-origin="30% 62%">
  <div class="atlas-scene__stage">
    <div class="atlas-scene__frame"><div class="atlas-scene__backdrop"><img src="…" width="…" height="…" alt="…"></div></div>
    <div class="atlas-scene__captions">
      <p class="atlas-scene__caption atlas-scene__caption--from">A joint, cut by hand.</p>
      <p class="atlas-scene__caption atlas-scene__caption--to">Four hundred of them hold the roof.</p>
    </div>
  </div>
</section>
```
Never with a photo too small for the zoom (it turns soft) or as the hero.

### split-wipe
A divider travels across one frame and the second state of the same place takes over: before/after, raw/finished, day/night. Fits proof, place. Needs two photos from the same angle and honest labels. Never invent a "before".
```html
<div class="atlas-scene__compare">
  <div class="atlas-scene__after-wrap"><img …><span class="atlas-scene__tag atlas-scene__tag--after">After</span></div>
  <div class="atlas-scene__before-clip"><img …><span class="atlas-scene__tag atlas-scene__tag--before">Before</span></div>
  <span class="atlas-scene__divider"></span>
</div>
```
Rest state: both images side by side (stacked on phones), each labelled.

### horizontal-rail
Vertical scroll drives a strip of 4-7 numbered plates. Fits portfolio, product, place, event. Never more than seven plates or text-heavy cards. Rest state: a native scroll-snap row.
```html
<div class="atlas-scene__head"><h2>Five materials</h2></div>
<div class="atlas-scene__rail"><ul class="atlas-scene__track">
  <li class="atlas-scene__plate"><figure><img …><figcaption>01 Earth</figcaption></figure></li> …
</ul></div>
```

### window-reveal
Twin panels in the page's ground colour part to open a full-bleed photograph. Fits place, event. Not for dark moody sites where the panels would look like a stuck curtain. Markup: `.atlas-scene__frame > .atlas-scene__backdrop > img` plus `.atlas-scene__shutter--left/--right`.

### mask-zoom
A rounded aperture grows from a small window to the whole frame. Fits product, event, portfolio. The subject must sit near the centre of the photo.

### type-parting
Two giant word pairs separate around a centerpiece. Fits statement, event. Two short phrases (2 words each) and one small image; markup `.atlas-scene__typewall > .atlas-scene__line > .atlas-scene__half--left/--right` around `.atlas-scene__centerpiece`.

## Light scenes (no pinning; two per page, different families)

### parallax-depth (depth)
Media and copy drift at different speeds beside each other. Fits place, portfolio, product, docs. Use once.

### word-light (type)
A one-sentence statement lights up word by word. Fits statement, process, place, docs. **Plain text only** (no links, no inline markup, no numbers the visitor must find).
```html
<section class="atlas-scene" data-atlas-scene="word-light">
  <div class="atlas-scene__stage"><p class="atlas-scene__statement">We start with the ground, then the timber, then the stone that stays cold underfoot.</p></div>
</section>
```

### step-assemble (process)
Three to five steps start scattered and settle into a row while a line draws across them. Fits process, software, event. Each step: a verb plus a result in under 12 words. Never more than five steps.
```html
<span class="atlas-scene__line atlas-scene__line--h"></span>
<ol class="atlas-steps"><li class="atlas-step"><h3>Visit</h3><p>We walk the site together.</p></li> …</ol>
```

### drift-type (type)
Two lines of giant type, one solid and one outlined, drift in opposite directions. Fits statement, event, product. Fill them with real nouns from the subject (materials, menu items, services), never adjectives. The rows are decorative: mark them `aria-hidden="true"` and keep the real information elsewhere on the page.

## Writing for scenes

- Caption and statement lines are copy: apply [copy-concise.md](copy-concise.md).
- Photos that get zoomed, wiped or panned must be at least 1600 px wide and fit [imagery.md](imagery.md) section 1b.
- A scene earns its place by showing something words cannot (a detail becoming a whole, a change, a sequence). If it only decorates, use `scene: none`.
- Verify at 1440 and 390 px in a real browser, at the start, middle and end of the scroll. `scripts/check-motion-v4.mjs` and `quick-check.mjs` (`partial-opacity`, `dead-space`) catch the common failures.
