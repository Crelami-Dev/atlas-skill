# Concise copy that still makes people curious

Most visitors decide in a few seconds whether a page is for them. Long copy is rarely read; short copy that is specific is. The aim is not fewer words for their own sake: it is the fewest words that name the offer, create a reason to keep going, and prove a result.

`node <atlas>/scripts/check-copy.mjs <project-root>` enforces the budgets below on static HTML (it runs as gate 4b in `run-gates.mjs`; `--strict` turns warnings into failures). Opt out of the length rules for documentation, legal text and articles with `<!-- atlas-copy: long-form -->`.

## The shape of a first screen

| Part | Budget | Job |
|---|---|---|
| Eyebrow | 2-5 words | Category and place, so the headline can be about the offer |
| Headline | 2-8 words (warn at 10, fail at 16) | The offer or the outcome, never a mood |
| Supporting line | one sentence, up to 24 words (warn at 28) | Who it is for and the one thing that sets it apart |
| Actions | one main, at most one secondary | A verb plus what the visitor gets |
| Whole first screen | under 55 words (fail at 85) | Finishable in five seconds |

The first screen carries **one concrete fact**: a number, a price, a place, a date. "Villas and pavilions in Ubud and Menteng" beats "Spaces that inspire".

## Curiosity plus result

A line that makes people want the next one has two halves: a **tension** (something the reader recognises or did not expect) and a **result** (what they get or can verify). Cut either half and the line fails.

| Flat | Curious, with a result |
|---|---|
| We offer high-quality coffee roasting services | Roasted to order, in your cup within 48 hours |
| Welcome to our architecture studio | Houses that stay cool without air conditioning |
| Our process is simple and transparent | Four steps from first visit to keys in hand |
| Learn more about our platform | See your invoice go out in 20 seconds |

Rules of thumb:
- Lead with the result, then the means. "Cool houses, made of earth and teak", not "We use earth and teak to…".
- Prefer a number to an adjective. "48 hours" proves; "fast" does not.
- Name the thing. Every heading holds a noun a stranger could picture.
- Leave one question open, never a riddle. The reader should know what the page is about and want to see how.
- No invented figures, clients or testimonials. If a number is not in the brief, do not write one; ask, or show the thing instead.

## Budgets below the fold

| Element | Budget |
|---|---|
| Section heading | up to 9 words |
| Paragraph | up to 45 words (fail at 80), at most 3 sentences |
| Prose per section | up to 110 words; past that, show it (image, figure, list, table) or cut it |
| Whole landing page | roughly 700 words |
| Caption or scene line | 4-12 words |

One idea per paragraph. If a paragraph needs a second idea, it needs a second element: a list, a figure, a pull quote.

## Buttons

A button is a verb plus what happens: **Book a visit**, **Hitung estimasi biaya**, **See the menu**. One to five words. Never "Learn more", "Read more", "Click here", "Selengkapnya", "Pelajari lebih lanjut", "Submit" (the checker fails these). The main action keeps one wording everywhere (nav, hero, close, phone bar).

## Language

Write in the language of the user's prompt, including buttons, form labels and errors. Keep one language per page unless the brief asks for two.

## Editing pass

1. Read the headline aloud. If you need a breath, cut.
2. Delete the first sentence of every paragraph; if nothing is lost, keep it deleted.
3. Replace every adjective with a number, a name or nothing.
4. Check each section: what can the visitor now do or verify that they could not before?
5. Run `check-copy.mjs` and read the warnings as questions, not orders.
