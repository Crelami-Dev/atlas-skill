# Design Brief

## Visitor and primary task

Describe who the visitor is, their entry context and primary device, and one concrete sentence stating the task they need to complete during this visit.

## Real content

List verified copy, factual data, available media assets, and honesty boundaries (what is real vs simulated/demo). Never use lorem ipsum or fabricated claims.

## Image plan

State the visual asset strategy: (a) use user-supplied photography/media, or (b) generate bespoke domain imagery (`image-generator` / `generate_image` into `assets/images/`) or fetch real licensed photography (`scripts/fetch-photos.mjs` into `assets/photos/`), marked silently via `data-photo-slot` + `data-atlas-proof` with fixed aspect ratios and zero visitor-visible `"Replace with photo"` badges. Never draw manual SVG scenes/floorplans or hill-and-sun silhouettes as a substitute for photos.

## Signature idea

One distinctive move that comes from the subject (see `references/creative-direction.md`): the physical truth, the move, `scene: <id from templates/scene-catalog.json | none>`, and why it serves the visitor. Keep everything else calm.

## Three composition alternatives

### Alternative 1

Subject-specific structural concept, primary strength for the visitor's task, and main trade-off or risk.

### Alternative 2

Genuinely different structural layout (not just a left-right swap), primary strength, and main trade-off or risk.

### Alternative 3

Third distinct reading/interaction flow, primary strength, and main trade-off or risk.

## Final choice and rationale

State the selected alternative, grid/typography archetype, surface polarity cadence, and purposeful Anime.js v4 motion plan (triggers, duration, easing, and reduced-motion behavior).

## Deliberately rejected and why

Record generic AI clichés (slop), empty decorative elements, or reference effects intentionally excluded and why.

## Verification plan

List gate commands (`run-gates.mjs`, build, tests), desktop and mobile viewports to screenshot and inspect, and the 5 UI states and interactions to verify.
