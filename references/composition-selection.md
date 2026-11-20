# Structural Archetype & Composition Selection (Atlas v7.0)

Consult this guide before writing UI code. Swapping color palettes, typefaces, or corner radii on top of the exact same macro skeleton does not count as structural variety. Every domain must adopt a structural archetype suited to how its visitors evaluate information.

## Hard Rule: Restrict the Workbench Hero Pattern

The **"2-column hero + search/filter/Reset workbench card"** pattern is restricted strictly to **interactive software applications and operational dashboards** (`split-screen` SaaS apps or `dashboard-shell`). Never force it onto restaurants, photographer/architect portfolios, events/festivals, weddings, law firms, clinics, travel itineraries, fashion lookbooks, or nonprofit/NGO pages.

## 10 Official Structural Archetypes

| Archetype ID | Core Structure | When to Use (`whenToUse`) | When Forbidden (`whenForbidden`) |
|---|---|---|---|
| `editorial-index-rail` | Sticky numbered left index rail + practice/service matrix (`01–04`) + partner directory & consultation desk | Law firms, management/tax consultancies, corporate profiles, policy institutes | Forbidden for single-product retail storefronts, real-time dashboards, or celebration invites |
| `poster-full-bleed` | Full-width architectural or typographic poster masthead (oversized date/venue or atmospheric cover) + timetable or 2-column print menu | Festivals, conferences, concerts, public events, and hospitality venues (restaurants, roasteries, cafés) | Forbidden for analytics dashboards, API documentation, or law/audit firms |
| `split-screen` | Asymmetric split screen (`42/58`) pairing product thesis with a live domain calculator or interactive estimator | B2B SaaS web apps, productivity/automation tools, financial simulators | Forbidden for restaurants, photo portfolios, weddings, legal firms, travel, or longform narratives |
| `dashboard-shell` | Full-viewport app shell (`left sidebar + KPI strip + dense filterable data table + slide-over detail drawer`), zero marketing hero | Operational tools, logistics/fleet dispatch, POS, CRM/ERP workspaces, telemetry consoles | Forbidden for public landing pages, restaurants, portfolios, events, or corporate profiles |
| `ledger-table-first` | Immediate service triage bar + structured practitioner/rate schedule matrix table + preparation protocol | Medical clinics, hospitals, labs, financial/accounting rate boards, course timetables | Forbidden for fashion lookbooks, wedding invitations, or photography monographs |
| `narrative-long-scroll` | Centered single reading column (`65ch–68ch`) + margin callouts + inline allocation bar + audited distribution table & pledge sheet | Nonprofits/NGOs, donation campaigns, annual impact reports, public research, data journalism | Forbidden for multi-variant e-commerce stores, operational dashboards, or SDK docs |
| `gallery-masonry` | Minimal top colophon + asymmetric multi-ratio exhibition plates (`16:9`, `4:5`, `1:1`) numbered curatorial `01–06` + commission sheet | Photography portfolios, architecture studios, creative agencies, art galleries, fashion lookbooks | Forbidden to include search bars/filter/Reset toolbars; forbidden for B2B apps or clinics |
| `docs-three-pane` | 3-pane docs layout (`left nav tree + center technical guide & code tabs + right on-this-page TOC`), leading with install command | SDK/API documentation, developer CLIs, open-source libraries, infrastructure guides | Forbidden for consumer retail storefronts, restaurants, events, real estate, or portfolios |
| `catalogue-grid` | Multi-angle product/property stage (`60/40`) or curated unit grid + variant/floorplan selector + measured specification table | Physical product e-commerce, real estate developments, structured course catalogs | Forbidden to use fake scarcity countdowns; single-product pages must not mount filter toolbars |
| `timeline-story` | Centered ceremonial crest or expedition cover + chronological rundown/itinerary + venue/route map + RSVP/booking sheet | Wedding invitations, celebrations, travel/tour itineraries, cultural heritage timelines | Forbidden to use SaaS pricing tiers, corporate dashboard widgets, or data filter toolbars |

## Documenting Three Alternatives in `design-brief.md`

1. Under `## Three composition alternatives`, pick **3 different structural archetypes** from the table above and describe what the visitor sees above the fold in each option.
2. Under `## Final choice and rationale`, state the chosen `Archetype ID` (matching `selectedArchetype.id` from `scripts/deal-direction.mjs`) and explain why the other two alternatives were set aside.
3. Under `## Deliberately rejected and why`, record every pattern forbidden by `selectedArchetype.whenForbidden` so none leak into implementation.

## Vary Page Closers (Avoid Ending Uniformity)

- Do not close every domain with a dark 2-column band (contact info on left, white form card on right). For hospitality/restaurants (`linen-espresso-craft`), close with a calm light or tinted surface band separating roasting schedules and group-table booking from event/wedding conventions.
