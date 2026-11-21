# Phones and tablets: design them on purpose

Most visitors arrive on a phone. A desktop page squeezed into one long column is the most common reason a good layout looks messy at 375 and 768 px. Design the small screens first as their own compositions, then widen.

## Three size bands

| Band | Width | What it is | Default layout |
|---|---|---|---|
| Phone | up to 599 px | one hand, thumb reach | one column; cards swipe; galleries are a 2-column mosaic or a swipe row |
| Tablet portrait | 600-1023 px | the weakest layout in most builds | two columns, never a lone half-width picture; the odd last card becomes a horizontal card |
| Desktop | 1024 px and up | pointer, wide | three or four columns; scenes can pin and follow scroll |

Review 320, 375, 390, 600, 768, 820, 1024, 1366 and 1440 px. `quick-check.mjs` audits all of them and adds the small-screen checks below.

## Pattern by content (use these instead of a long stack)

| Content | Phone | Tablet portrait | Desktop |
|---|---|---|---|
| 3-6 cards (services, project types, plans) | `.atlas-carousel` swipe row, next card peeking, dots | 2-column grid; an odd last card spans the row as a horizontal card | 3-4 columns (`.atlas-carousel--grid-up`) |
| Gallery of photos | `.atlas-bento` 2-column mosaic, or an `--always` carousel for 6+ plates | `.atlas-bento` 2 columns with a feature tile | `.atlas-bento` 4 columns |
| Process or steps | `step-assemble` (stacked, plays once) or a numbered list | 2 columns | one row of 3-5 |
| Facts and figures | `.atlas-stats` in 2 columns | 3 columns | one row |
| Long comparison or table | card per row, or horizontal scroll with a visible edge | same | table |
| Testimonials, logos | carousel, one at a time | 2 up | 3 up or a row |
| Hero | headline, one line, full-width CTA row, then the picture | same, picture can sit beside on landscape | split layout |
| Navigation | a visible Menu button (every desktop destination stays reachable) | Menu button or inline links | inline links |
| Forms | one column, labels above, 44 px fields, native pickers | two columns for short pairs | two columns |

Rules that keep it tidy:
- **A single column of three or more picture cards taller than 1.8 screens is a mistake** (`mobile-long-stack`). Make it a carousel or a mosaic.
- **A picture never sits alone in part of its row** (`half-empty-row`): full width, beside text, or in a grid.
- **Two columns on tablet portrait, not three.** Three narrow columns at 768 px make cramped text and thumbnails.
- **Text never sits on a photograph.** Cards hold the photo on top and words below; bento tiles are either a photo or a text/figure tile.
- Keep the peek: a carousel slide is about 84% wide so the next card shows and invites a swipe.
- One main action per screen: stacked CTAs are equal width and full width (`.atlas-cta-row`).
- Thumb zone: primary actions near the bottom half; use the phone action bar (`.atlas-mobile-bar`) once the hero action scrolls away.
- Tap targets 44 px or more, including carousel dots and arrows.

## Components (in `templates/atlas-components.css`, behaviour in `atlas-interact.mjs`)

```html
<!-- Cards: swipe on phones, grid from 600 px -->
<div class="atlas-carousel atlas-carousel--grid-up" data-carousel aria-label="Project types">
  <ul class="atlas-carousel__track">
    <li class="atlas-carousel__slide">
      <article class="atlas-card atlas-card--media atlas-card--lift">
        <div class="atlas-card__media"><img src="…" width="800" height="600" alt="…"></div>
        <div class="atlas-card__body"><h3>Private Villa</h3><p>One short line.</p></div>
      </article>
    </li> …
  </ul>
</div>

<!-- Gallery: a mosaic that always lands in whole rows -->
<div class="atlas-bento">
  <figure class="atlas-bento__item atlas-bento__item--feature"><img …></figure>
  <figure class="atlas-bento__item"><img …></figure>
  <div class="atlas-bento__item atlas-bento__item--text atlas-bento__item--accent"><p class="atlas-bento__figure">14 weeks</p><p>From visit to keys.</p></div>
  <figure class="atlas-bento__item atlas-bento__item--tall"><img …></figure>
  <figure class="atlas-bento__item atlas-bento__item--wide"><img …></figure>
</div>
```

Carousel variants: `--grid-up` (grid from 600 px, controls hidden), `--always` (stays a carousel, 2 slides on tablet, 3 on desktop), `--wide` (larger slides). Controls, dots (a counter past 5 slides), keyboard arrows, Home and End, and the carousel ARIA roles are added by `initAtlasInteract()` (or `initAtlasCarousels()` alone). With no JS it is still a native swipe row.

Bento tile modifiers: `--feature` (2x2), `--wide` (2x1), `--tall` (1x2), `--text` and `--accent` for words and figures. Use it only when the page really has a gallery; otherwise do not invent one.

`templates/atlas-patterns-demo.html` shows every pattern, and `tests/small-screens.test.mjs` proves the behaviour in a real browser at 375, 768 and 1440 px.

## Motion on small screens

The rule is the same on every device: **a section starts when 15% of it is on screen**, and it plays smoothly and a little slowly so it feels deliberate.

| Where | What happens |
|---|---|
| Desktop (1024 px and up) | reveals at 15%; one heavy scene pins and follows scroll, up to two light scenes follow scroll |
| Tablet portrait and phones | reveals at 15%; every scene plays **once** at 15% visible, about 1.7 s, `outQuart`, no pinning and no scroll-jacking |
| `prefers-reduced-motion` | opacity-only fades at 15%, no travel or scale; scenes show their finished composition |
| No JS or Anime.js blocked | everything visible and still |

Defaults in `initAtlasMotion`: reveal 1250 ms, hero 1100 ms, stagger 110 ms, scene 1700 ms (`data-motion-ms` on a scene overrides it), `ease: 'outQuart'`, start `y: 36, opacity 0.14, scale 0.975`. Keep entrance chains under about 2000 ms. `<html data-atlas-motion="scrub|play|soft|rest">` says which mode a device got, which is the first thing to check when "nothing moves".

Why a phone can look static: the system "reduce motion" or battery-saver setting is on (soft mode: fades only), Anime.js failed to load (rest), or the page used an old `atlas-scenes.mjs` that left heavy scenes still below 768 px. Update the template and read `data-atlas-motion`.

## Loops on small screens

Self-playing demos, rotators and tickers (see [loops.md](loops.md)) work the same on phones: they start at 15% visible, pause off screen, show a 44 px pause button, and stand still under reduced motion. Keep one demo card playing per screen; on a phone a card should be at most one screen tall, and long typed lines wrap instead of overflowing.

## Checks

`quick-check.mjs` adds, for small screens: `mobile-nav-missing`, `cta-width-mismatch`, `cta-not-full-width`, `mobile-long-stack`, `half-empty-row`, plus the existing overflow and tap-target checks at 320-820 px. Open the screenshots; a green log does not prove the layout is calm.
