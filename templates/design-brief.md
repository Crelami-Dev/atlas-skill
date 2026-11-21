# Design Brief

## Visitor and primary task

Describe who the visitor is, where they arrive from, their primary device, and one concrete sentence defining the task they must finish in this visit.

## Real content

List factual copy, real figures, available media assets, and honesty boundaries (what is live vs simulated/demo). Never use lorem ipsum or fabricated claims.

## Image plan

State the visual asset strategy: (a) use user-provided photography/media, or (b) generate bespoke domain imagery (`image-generator` / `generate_image` into `assets/images/`) or fetch real licensed photography (`scripts/fetch-photos.mjs` into `assets/photos/`), marked silently via `data-photo-slot` + `data-atlas-proof` with fixed aspect ratios and zero visitor-visible `"Replace with photo"` instructions. Never draw manual SVG scenes/floorplans or generic hill-and-sun silhouettes as a substitute for photos.

## Signature idea

One distinctive move that comes from the subject (see `references/creative-direction.md`): the physical truth, the move, `scene: <id from templates/scene-catalog.json | none>`, and why it serves the visitor. Keep everything else calm.

## Three composition alternatives

### Alternative 1

Subject-specific structural concept, key strength for the visitor task, and main trade-off.

### Alternative 2

Genuinely different structural layout (not just a left-right swap), key strength, and main trade-off.

### Alternative 3

Third distinct flow of proof/interaction, key strength, and main trade-off.

## Final choice and rationale

State the chosen alternative, structural archetype/typography pairing, surface polarity cadence, and Anime.js v4 motion plan (trigger, duration, easing, and reduced-motion behavior).

## Deliberately rejected and why

Note AI clichés (slop), empty ornament, or reference patterns intentionally excluded and why.

## Verification plan

List gate commands (`run-gates.mjs`, build, tests), mobile/desktop screenshot viewports to inspect, and interactive states to verify.
