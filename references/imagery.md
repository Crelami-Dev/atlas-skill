# Visual Assets, AI Image Generation, & Licensed Photography (`imagery.md`)

This guide governs visual media decisions for photography-dependent and visually rich domains (cafés/restaurants/hospitality, photographer/architect portfolios, physical e-commerce, real estate, travel, fashion, weddings, and live events).

## 1. Visual Asset Decision Tree

1. **Condition A — User Supplies Real Assets:**
   - Use user-provided photography or video directly—real assets are always the most authentic visual proof.
   - Set explicit `width`, `height`, `aspect-ratio`, `loading="lazy"` (for below-the-fold media), and descriptive `alt` text.
2. **Condition B — Visual Domain Without Photo Assets Yet (Generate or Fetch Real Raster Images):**
   - **Never draw manual `<svg>` illustrations or schematic floorplans as a substitute for photography or hero artwork.** Use one of the two real raster-image workflows below and save all assets locally inside `assets/images/` or `assets/photos/`:
   - **Step B1 (Primary — AI Image Generation when available):** If your agent environment provides an image generation tool or subagent (`image-generator`, `generate_image`, or equivalent), **generate bespoke, art-directed raster images** (`.png`/`.webp`/`.jpg`) matching the domain, lighting, aspect ratio, and color palette in `design-tokens.css`. Save them locally (e.g., `assets/images/hero-brew-bar.png`) and embed them with `<img src="assets/images/..." width="..." height="..." alt="...">` inside `<figure class="editorial-plate" data-photo-slot="..." data-atlas-proof="generated-image">`.
   - **Step B2 (Primary Fallback — Fetch Real Licensed Photography):** When image generation is unavailable or authentic documentary photography is preferred, run Atlas's built-in Wikimedia Commons photo downloader to save high-resolution CC0 / CC-BY / Public-Domain photography locally into `assets/photos/` (with attribution metadata in `assets/photos/credits.json`):
     ```sh
     node <atlas>/scripts/fetch-photos.mjs --query "<subject 1>|<subject 2>|<subject 3>|<subject 4>" --out assets/photos --count 4
     ```
     Render the downloaded local images (`<img src="assets/photos/photo-01.jpg" width="..." height="..." alt="...">`) inside `<figure class="editorial-plate" data-photo-slot="..." data-atlas-proof="real-photography">` and include a quiet 1-line attribution credit from `assets/photos/credits.json` in the page footer.
   - **Step B3 (Offline Air-Gapped Fallback Only):** Only when **both** image generation and network access (`--offline`) are unavailable, craft a crisp typographic/specification plate (`data-photo-slot="..." data-atlas-proof="editorial-plate"`) using `--color-*` and `--font-*` tokens—never crude wireframe SVGs or placeholder text.
   - **Strictly Forbidden in Visitor DOM:** Never render owner/developer instructions in visible text or `aria-label`, including `"Ganti dengan foto asli"`, `"Replace with photo"`, `"SLOT FOTO 01"`, `"PHOTO SLOT"`, `"awaiting photo"`, `"Subjek: ..."`, `"[Data Klien Diperlukan]"`, or `.photo-replace-badge`. Never draw schematic `<rect>` table + `<circle>` stool/chair wireframe floorplans (`crude-floorplan-svg`).
   - **Silent Handoff Markup:** Mark swappable frames solely via silent HTML attributes (`data-photo-slot="hero-16x9"`, `data-aspect="16:9"`), list the media slots in `design-brief.md` (`## Image plan`), and invite the user to swap in their own proprietary photography whenever ready.
3. **Condition C — Data-, Code-, or Typography-First Domains:**
   - For operational dashboards, API documentation, or research dossiers, lead with structured tables, live calculators, terminal/code specimens, or measured charts (`<svg data-viz>`) instead of forcing decorative photos.

## 1b. Photo Relevance & Hero Subject (a licence is not enough)

A photo passes only when it also fits the business. Judge every image before it enters the page:

1. **The hero shows the thing being sold.** An architecture studio shows a building or interior, a café shows the room or the plate, a product page shows the product. A landscape, texture or mood image can support the story below the fold but must not be the first image unless the business sells that place.
2. **Local context matches.** A photo from another country, climate or building tradition (e.g. an African beam or a US cliff on a Bali studio page) is allowed only when the page says openly that it is a material or technique study and the caption names the origin. Prefer a local match; otherwise do not use it.
3. **Query for the subject, not the mood, in 2-3 words.** In `fetch-photos.mjs --query`, write `<place> <subject>` (`Bali villa`, `Ubud resort`, `Bali temple wall`, `joglo teak house Java`), not `rammed earth` alone. Longer phrases (5+ words such as `Bali villa interior bamboo roof`) usually return nothing from Wikimedia. Run one query per slot and a second pass with different wording when the first result set is off-topic. Titles often hide the real subject (a "Bali temple wall" query also returns Indian terracotta panels), so open every candidate before using it.
4. **Resolution and crop.** Hero >= 1600px wide and no visible compression artifacts at its rendered size. Reject images with watermarks, people's faces in identifiable close-up (unless the user supplied them), or heavy tourist crowds.
5. **Mixed quality is visible.** In a gallery, drop the weakest frame rather than fill a slot. Four strong images beat six uneven ones; reuse is better than a poor fit.
6. **Evidence panels get context.** A result panel, summary card or configurator that shows an important number may carry one small relevant photo to anchor it; skip it when no fitting photo exists.
7. **Record the decision.** In `## Image plan`, add one line per image: why it fits, what it stands for, and its origin when it is not local.

## 2. Proper `<svg>` Usage Rules

- **Allowed `<svg>` usage:** Small UI icons (`<= 32px`), crisp brand logomarks, and real data-driven charts/graphs (`<svg data-viz>` with real axes, scales, or plotted values).
- **Disallowed `<svg>` usage:** Hand-drawn `<svg>` scenes, café/interior illustrations, product mockups, or floorplan schematics pretending to be photography. Use **Step B1 (Image Generation)** or **Step B2 (`fetch-photos.mjs`)** instead.

## 3. Strictly Forbidden Visual Patterns

- **Hand-Drawn Scene/Floorplan SVGs (`crude-floorplan-svg`, `crude-wireframe-svg`):** Never draw rows of `<rect>` and `<circle>` shapes or manual `<svg>` illustrations inside hero/gallery frames as a substitute for real or generated imagery.
- **Leaked Placeholder Instructions (`leaked-photo-placeholder-ui`):** Never render phrases such as `"Replace with photo"`, `"Ganti dengan foto asli"`, `"PHOTO SLOT 01"`, `"SLOT FOTO 01"`, `"Image Placeholder"`, `"[Data Klien Diperlukan]"`, or `"awaiting photography"` in visible text or `aria-label`.
- **Generic Hill-and-Sun Silhouettes (`generic-hill-sun-svg`):** Never draw an `<svg>` containing a sun `<circle>` over wavy/mountain `<path>`/`<polygon>` placeholders.
- **Stock Icons or Broken Images (`broken-images`):** Never place a lonely camera icon inside an empty box, and never point `<img src="...">` at missing local files or unverified external URLs.
- **SVG Text Overlapping Strokes (`svg-text-overlap`):** Never place `<text>` colliding with `<svg>` stroke boundaries; render captions and metadata in clean HTML outside or around the artwork.

## 4. Mandatory `## Image plan` Section in `design-brief.md`

For every visual-domain project (photographers, restaurants, cafés, physical products, real estate, travel, fashion, weddings, and events), `design-brief.md` must include `## Image plan` (or `## Rencana gambar`) detailing:
- Asset source (user-supplied photography, AI-generated bespoke images via `image-generator` / `generate_image`, or licensed Wikimedia photography via `scripts/fetch-photos.mjs`).
- List of primary media slots, aspect ratios (`16:9`, `4:5`, `4:3`, `1:1`), local file paths (`assets/images/...` or `assets/photos/...`), and alt-text/caption notes.
