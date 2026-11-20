# Composition & Visual Density Standards (Atlas v7.0)

This guide defines measurable composition rules so every section carries clear visual weight, scans rapidly, and avoids accidental empty voids.

## 1. One Dominant Focal Point per Section

- Give every `<section>` a single primary visual or typographic anchor leading the visitor's eye (such as a `--text-2xl`/`--text-3xl` key statement, primary comparison table, framed media/specimen plate, or schedule matrix).
- Avoid placing two equally heavy widgets side by side in the same viewport with competing visual loudness and unclear hierarchy.

## 2. Body Copy Minimum 16px

- Keep body `<p>` prose and primary list items (`<li>`) at a computed size of at least `16px` (`1rem` / `var(--text-base)`) for effortless reading across desktop and mobile without pinch-zooming.
- Reserve sizes below `16px` (`--text-sm` or `--text-xs`) strictly for secondary metadata, uppercase eyebrows, table column headers, status badges, and `<figcaption>` captions.

## 3. Comfortable Reading Measure (`60ch–75ch`)

- Cap narrative paragraph containers between `60ch` and `75ch` (for example `max-width: 65ch`).
- Lines spanning a full `1200px+` container tire the eye on line returns, while overly narrow prose columns (`< 45ch` on desktop) create choppy reading rhythm.

## 4. Eliminate Unintentional Empty Voids

- Avoid tall cards, SVG stages, or sections (`> 260px`) leaving more than 85% empty background without deliberate compositional purpose.
- When an illustration or chart is naturally compact, match container height to its intrinsic aspect ratio (`aspect-ratio` or `height: auto`) instead of forcing an empty `min-height: 500px`.

## 5. Practical Card Content Density

- Ensure every card in a grid helps the visitor make a decision (specific heading, 2–3 concrete data points, and a clear next step) rather than repeating single-sentence marketing fluff.
- Cap card items at 3–4 concise facts so cards never turn into narrow walls of text.

## 6. No Long Unstructured Prose on Dark Bands

- Dark-surface sections (`--color-blueprint` / `luminance < 0.12`) serve as rhythmic anchors for technical specs, concise high-impact statements, numeric grids, code specimens, or framed visual plates.
- Never drop raw prose exceeding `420` characters of `<p>` text alone onto a dark background without structured cards (`<article>`), tables, `<dl>` spec lists, or visual media, as extended light-on-dark prose causes halation fatigue.

## 7. Automated Inspection via `visual_dom_inspector.py`

`skills/atlas-checker/scripts/visual_dom_inspector.py` verifies these layout rules directly against the rendered Headless Chromium DOM:
- `body-font-too-small`: Warns when narrative `<p>` elements inside `<main>` (excluding eyebrows/captions/metadata) render below `16px`.
- `line-measure-too-wide`: Warns when long reading paragraphs exceed `840px` rendered width (~`75–80ch`).
- `excessive-empty-area`: Warns when large `<section>` blocks fall below `16%` content fill ratio.
- `dark-section-long-prose-only`: Warns when dark sections hold `> 420` characters of plain paragraph prose with zero cards, tables, specs, or media.
- `low-text-contrast`: Flags an error when computed WCAG contrast falls below `4.5:1` (`3.0:1` for text `>= 24px`).
- `desktop-overflow` / `mobile-viewport-blowout-*`: Flags an error whenever `scrollWidth > innerWidth` on desktop, tablet, or mobile.
