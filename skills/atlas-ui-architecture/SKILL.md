---
name: atlas-ui-architecture
description: "Use when architecting multi-view web applications, operational dashboards, data tables, filter systems, modals/drawers, and interactive forms with 5-state view contracts. Do not use for static articles without data interaction."
---

# Atlas UI Architecture — Application Shells & 5-State Contract

Use this module whenever building applications with multi-view navigation, dynamic lists or tables, search/filter controls, dialogs, or interactive forms.

## 1. Choose an App Shell Matching the Project Type

Match navigation chrome to the user's primary task so screen space is never wasted on unnecessary framing:

| Project Type | Desktop App Shell | Mobile Adaptation (`<= 767px`; tablet portrait 600-1023 px: see [mobile-and-tablet.md](../../references/mobile-and-tablet.md)) |
|---|---|---|
| Editorial / Service Site | Focused top nav bar + primary CTA + footer index | Compact top bar + full-height drawer supporting `Escape` |
| Dashboard / SaaS App | Collapsible left sidebar (`240px` / `64px`) + main workbench | Bottom bar (max 4–5 items) or slide-over drawer with zero overflow |
| Catalog / E-Commerce / Booking | Sticky filter header + catalog grid + order summary | Bottom filter/summary bar opening a sheet dialog |
| Documentation / Knowledge Base | 3-column (`left nav tree` + `68ch guide` + `right TOC rail`) | 1 reading column + expandable `<details>` table of contents at top |

## 2. The 5-State View Contract for Data-Driven Views

Every list, table, chart, or search result must handle all 5 UI states cleanly because real users encounter network delays, empty datasets, and unmatched filters:

1. **Loading State:** Skeleton placeholders (`aria-busy="true"`) matching final dimensions to prevent cumulative layout shift (CLS).
2. **Populated State:** Structured data with safe truncation (`min-width: 0`) and tabular numerals (`font-variant-numeric: tabular-nums`).
3. **Empty Dataset State:** Clear explanation of why no items exist yet plus a direct action button to create or import the first record.
4. **Filtered Zero-Match State:** Distinct from an empty dataset; show the active query/filter criteria and a one-click **"Reset Filters"** button.
5. **Error / Recovery State:** Actionable failure explanation with a **"Retry"** button that preserves all user input.

- **Ban Visible Debug State Switchers in Production UI:** Never expose a state-picker dropdown or toggle bar (`Populated / Loading / Empty / Error`) to end visitors; these are developer test aids. Drive states from real data interactions (or hide debug controls behind `?debug=1` with the `hidden` attribute by default). Never mount `Search / Filter / Reset` toolbars onto short narrative, hospitality, wedding, or portfolio pages.

## 3. Responsive Tables, Dialogs, and Forms

- **Wide Data Tables:** Wrap wide tables inside their own `overflow-x: auto` container so multi-column data never breaks mobile viewport width.
- **Accessible Dialogs & Drawers:** Use native `<dialog>` (or explicitly manage focus trapping, `Escape` dismissal, and focus restoration to the trigger button), since plain `<div onClick>` overlays fail keyboard accessibility.
- **Explicit Labels & Form Validation:** Pair a visible `<label>` with every input (`placeholder` disappears once typing begins), show inline field errors via `aria-invalid="true"`, and disable submit controls while a request is in flight.
