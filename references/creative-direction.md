# Creative direction: one distinctive move that comes from the subject

A page that follows every rule can still be forgettable. The remedy is not decoration; it is one idea that could only belong to this subject, carried out well, with everything else kept calm.

## The signature idea (Phase 1, in `design-brief.md`)

Add a short `## Signature idea` section. Four lines are enough:

```
## Signature idea
Truth: Walls of earth and timber that cool a house without machines.
Move: a detail of a hand-cut joint pulls back to show the whole roof it carries.
scene: pull-back
Why it serves the visitor: shows craft and scale in one gesture, no claims needed.
```

`scene:` is an id from `templates/scene-catalog.json` or `none`; the brief gate rejects unknown ids.

### How to find the move

1. **State the physical truth of the subject.** A material, a process, a rhythm, a measurement. Not a feeling.
2. **Ask what the visitor cannot judge from words.** Craft, scale, change over time, sequence, taste, fit.
3. **Generate three moves from different families:** a *scene* (see [scenes.md](scenes.md)), a *type* move (giant type, word light, a number that counts), an *interaction* (a configurator, a before/after, a hover that reveals). Write each in one sentence.
4. **Reject on purpose.** Drop any move that would work unchanged for an unrelated business (the template-substitution test in [visual-review.md](visual-review.md)), that repeats the last project's move (`deal-scene.mjs` records history), or that adds weight without answering step 2.
5. **Pick one.** Build it well. The rest of the page stays quiet so the move reads.

### Subject to move: starting points, not assignments

| Subject | Physical truth | Candidate moves |
|---|---|---|
| Architecture, villas | Material, shade, scale | `pull-back` (detail to whole), `split-wipe` (restoration), a materials `horizontal-rail` |
| Restaurant, cafe | Heat, time, a plate | `drift-type` of the menu's real nouns, `mask-zoom` on the signature dish, a count-up of daily covers only if real |
| Photographer | The frame | `horizontal-rail` of plates, `window-reveal` on one hero image |
| Product shop | The object and its parts | `pull-back` on a detail, `step-assemble` for how it is made, magnetic CTA |
| Clinic, repair, service | Before and after, steps | `split-wipe`, `step-assemble`, a results strip with real figures |
| Event, wedding | A date and a place | `type-parting` of the two names or the date, `word-light` for the invitation line |
| Software | A result in seconds | A live product UI first; `step-assemble`; a count-up of one real metric |
| Docs, legal, research | Findability | No heavy scene. Calm layout, a strong table of contents, `word-light` at most |

## Boldness ladder

Choose the level before designing, from the visitor's stakes, not from taste.

| Level | When | What it allows |
|---|---|---|
| Calm | legal, finance, health records, documentation | One accent, no pinned scene, motion limited to reveals |
| Confident | most businesses | One heavy or two light scenes, one ambient background, magnetic CTA |
| Bold | events, creative studios, launches, hospitality | One heavy scene plus one light, oversized type, a distinctive colour pair |

Bold never means more things at once. It means one thing louder.

## Ambient surfaces and interaction

- **Backgrounds** (`templates/atlas-backgrounds.css`): `mesh`, `grain`, `contour`, `blueprint`, `spotlight`, `paper`. One per section, texture only, built from the page's own tokens. Match the subject: `contour` for terrain and craft, `blueprint` for studios, `paper` for hospitality.
- **Interaction** (`templates/atlas-interact.mjs`): `data-magnetic` on the main CTA, `data-tilt` on a feature card, `data-spotlight` with `atlas-bg-spotlight`, `data-count` for real figures, and `data-mobile-bar` for a phone action bar. All are opt-in and off under reduced motion.
- **Components** (`templates/atlas-components.css`): `.atlas-cta-row` (equal-width stacking on phones), `.atlas-link`, `.atlas-stats`, `.atlas-mobile-bar`.

## Responsive behaviour is part of the design

- Heavy scenes become a finished composition on phones; light scenes stay cheap.
- Calls to action stack at equal width, primary first (`.atlas-cta-row`); the checker flags `cta-width-mismatch`.
- Every desktop destination stays reachable on a phone (`mobile-nav-missing`).
- Check 320, 375, 390, 820, 1366 and 1440 px, and look at the screenshots.

## Guard rails against slop

- No gradient-blob heroes, no three identical feature cards, no stock "Welcome to…" lines.
- One scene idea per page; if you cannot say why the visitor needs it, use `scene: none`.
- Real photographs that fit the subject ([imagery.md](imagery.md) section 1b), real figures, real names.
- Short, specific copy ([copy-concise.md](copy-concise.md)).
