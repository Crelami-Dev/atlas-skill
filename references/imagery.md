# Visual Assets, Photography, & Editorial Specimen Plates (`imagery.md`)

This guide governs visual media decisions for photography-dependent domains (photographer portfolios, restaurants/hospitality, physical e-commerce, real estate, travel, fashion, weddings, and live events).

## 1. Visual Asset Decision Tree

1. **Condition A — User Supplies Real Assets:**
   - Use user-provided photography or video directly—real assets are always the most honest visual proof.
   - Set explicit `width`, `height`, `aspect-ratio`, `loading="lazy"` (for below-the-fold media), and descriptive `alt` text.
2. **Condition B — Visual Domain Without Photo Assets Yet:**
   - **Step B1 (Primary — Fetch Real Licensed Photography When Online):** Run Atlas's built-in Wikimedia Commons photo downloader to save high-resolution CC0 / CC-BY / Public-Domain photography locally into `assets/photos/` (with attribution metadata in `assets/photos/credits.json`):
     ```sh
     node <atlas>/scripts/fetch-photos.mjs --query "<subject 1>|<subject 2>|<subject 3>|<subject 4>" --out assets/photos --count 4
     ```
     Render the downloaded local images (`<img src="assets/photos/photo-01.jpg" width="..." height="..." alt="...">`) inside `<figure class="editorial-plate" data-photo-slot="..." data-atlas-proof="real-photography">` and include a quiet 1-line attribution credit from `assets/photos/credits.json` in the page footer.
   - **Step B2 (Fallback — Offline or Technical/Architectural Diagrams Only):** Only when offline (`--offline`) or when an analytical diagram is more informative than a photograph, deliver a **100% finished-looking page** using **Domain-Specific Editorial / Technical Specimen Plates (`data-photo-slot="..."` + `data-atlas-proof="..."`)** with `<linearGradient>`/`<radialGradient>` and bezier curve (`C`/`S`/`Q`/`A`) `<path>` artwork, keeping all developer notes out of the visitor DOM.
   - **Strictly Forbidden in Visitor DOM:** Never render owner/developer instructions in visible text or `aria-label`, including `"Ganti dengan foto asli"`, `"Replace with photo"`, `"SLOT FOTO 01"`, `"PHOTO SLOT"`, `"awaiting photo"`, `"Subjek: ..."`, `"[Data Klien Diperlukan]"`, or `.photo-replace-badge`. Never draw schematic `<rect>` table + `<circle>` stool/chair wireframe floorplans (`crude-floorplan-svg`).
   - **Silent Handoff Markup:** Mark swappable frames solely via silent HTML attributes (`data-photo-slot="hero-16x9"`, `data-aspect="16:9"`), list the media slots in `design-brief.md` (`## Image plan`), and invite the user to swap in their own proprietary photography whenever ready.
3. **Condition C — Data-, Code-, or Typography-First Domains:**
   - For operational dashboards, API documentation, or research dossiers, lead with structured tables, live calculators, terminal/code specimens, or measured charts instead of forcing decorative photos.

## 2. Domain-Specific Specimen Plate Patterns (Condition B)

When building under **Condition B**, populate each `<figure data-photo-slot="..." data-atlas-proof="...">` with meaningful domain composition backed by `--color-*` and `--font-*` tokens:

- **Photographer / Architecture:** Exhibition Monograph & Exposure Plate (`PLATE I`, series title, optical/lighting metadata `35mm • f/2.8 • 1/125s • ISO 400`, layered light-study SVG/gradients, and curatorial caption).
- **Event / Symposium / Festival:** Stage Acoustic Diagram or Architectural Venue Elevation (seating capacity, stage sightlines, and schedule notes).
- **Physical Product / E-Commerce:** Technical Material Cross-Section & Dimension Plate (millimeter tolerances, layered finish tones, weight specs, and interactive finish swatches).
- **Restaurant / Café / Culinary:** Architectural Tasting Bar Illustration & Harvest Origin Plate (layered counter/light scene, origin elevation, roast curve, tasting notes, and food pairings).
- **Wedding / Ceremonial:** Engraved Monogram Crest & Venue Coordinate Plate (typographic initials, venue coordinates/route diagram, and ceremony timeline cues).

Clean specimen plate example (layered architectural SVG composition, zero raw wireframe boxes, zero leaked placeholder text):

```html
<figure class="editorial-plate" data-photo-slot="cibeunying-bar-16x9" data-aspect="16:9" data-atlas-proof="editorial-plate">
  <div class="editorial-plate-stage" role="img" aria-label="Architectural morning light illustration across a teak pour-over bar counter with gooseneck kettle and porcelain cups">
    <div class="editorial-plate-meta">
      <span>PLATE 01 · EAST BAR COUNTER</span>
      <span>16:9 · 07:30 LOCAL · MORNING LIGHT</span>
    </div>
    <svg viewBox="0 0 760 240" width="760" height="240" aria-hidden="true">
      <defs>
        <linearGradient id="morningBeam" x1="0%" y1="0%" x2="85%" y2="100%">
          <stop offset="0%" stop-color="currentColor" stop-opacity="0.16"/>
          <stop offset="100%" stop-color="currentColor" stop-opacity="0.02"/>
        </linearGradient>
      </defs>
      <!-- Arched east window & morning light beam (stops cleanly at counter y=168) -->
      <path d="M96 168 L96 78 A68 68 0 0 1 232 78 L232 168 Z" fill="url(#morningBeam)"/>
      <path d="M96 168 L96 78 A68 68 0 0 1 232 78 L232 168" fill="none" stroke="currentColor" stroke-opacity="0.28" stroke-width="1.5"/>
      <polygon points="104,132 224,132 392,168 164,168" fill="currentColor" fill-opacity="0.06"/>
      <!-- Teak bar counter surface -->
      <path d="M40 168 L720 168 L720 204 L40 204 Z" fill="currentColor" fill-opacity="0.12"/>
      <line x1="40" y1="168" x2="720" y2="168" stroke="currentColor" stroke-opacity="0.45" stroke-width="2"/>
      <!-- Gooseneck kettle & porcelain cups -->
      <path d="M312 168 L322 108 L368 108 L378 168 Z" fill="currentColor" fill-opacity="0.72"/>
      <path d="M322 132 C292 132 292 104 276 102" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
      <path d="M368 118 C392 118 392 152 374 152" fill="none" stroke="currentColor" stroke-width="2.5"/>
      <path d="M432 138 L476 138 L470 168 L438 168 Z" fill="currentColor" fill-opacity="0.45"/>
      <path d="M498 142 L538 142 L533 168 L503 168 Z" fill="currentColor" fill-opacity="0.32"/>
      <!-- Pendant lamp -->
      <line x1="590" y1="12" x2="590" y2="66" stroke="currentColor" stroke-opacity="0.35" stroke-width="1.5"/>
      <path d="M556 90 A34 24 0 0 1 624 90 Z" fill="currentColor" fill-opacity="0.24" stroke="currentColor" stroke-opacity="0.4" stroke-width="1.5"/>
    </svg>
    <p class="editorial-plate-caption">Three-meter teak pour-over counter bathed in morning east-window daylight with 45 cm seating spacing.</p>
  </div>
  <figcaption>Main brew counter seating 18 guests along the sunlit east garden wall.</figcaption>
</figure>
```

## 3. Strictly Forbidden Visual Patterns

- **Raw Wireframe Boxes Inside Plates:** Never draw rows of empty stroked `<rect>` and `<circle>` shapes inside `.editorial-plate-stage` that resemble a crude CAD schematic; compose layered SVGs using opacity gradients, filled domain silhouettes, lighting geometry, or measured curves.
- **Leaked Placeholder Instructions (`leaked-photo-placeholder-ui`):** Never render phrases such as `"Replace with photo"`, `"Ganti dengan foto asli"`, `"PHOTO SLOT 01"`, `"SLOT FOTO 01"`, `"Image Placeholder"`, `"[Data Klien Diperlukan]"`, or `"awaiting photography"` in visible text or `aria-label`.
- **Generic Hill-and-Sun Silhouettes (`generic-hill-sun-svg`):** Never draw an `<svg>` containing a sun `<circle>` over wavy/mountain `<path>`/`<polygon>` placeholders.
- **Stock Icons or Broken Images (`broken-images`):** Never place a lonely camera icon inside an empty box, and never point `<img src="...">` at missing local files or unverified external URLs.
- **SVG Text Overlapping Strokes (`svg-text-overlap`):** Never place `<text>` colliding with `<svg>` stroke boundaries; render captions and metadata in clean HTML outside or around the artwork.

## 4. Mandatory `## Image plan` Section in `design-brief.md`

For every visual-domain project (photographers, restaurants, physical products, real estate, travel, fashion, weddings, and events), `design-brief.md` must include `## Image plan` (or `## Rencana gambar`) detailing:
- Asset source (user-supplied photography vs editorial specimen plates tagged silently with `data-photo-slot`).
- List of primary media slots, aspect ratios (`16:9`, `4:5`, `1:1`), and specific real photos to request from the user in the final chat message.
