---
name: atlas-lean-code
description: "Use when writing frontend code with semantic HTML, CSS Grid/Flexbox, narrow local state, and clean lifecycle teardown across React, Next.js, Vue, Svelte, Astro, or Vanilla JS. Do not use for initial design planning."
---

# Atlas Lean Code — Clean Semantics & Narrow State

Simple, web-platform-first code is easier to maintain and suffers far fewer cross-viewport layout regressions.

## 1. Inspect Host Conventions First

- Read `package.json`, `tsconfig.json`, folder layout (`app/`, `pages/`, `src/`), and existing CSS setup before adding files so new work blends cleanly into the repository.
- Reuse built-in framework primitives (`next/image`, `next/font`, native router) instead of reimplementing custom utilities.

## 2. Implementation Simplicity Ladder

Pick the lowest-complexity layer that satisfies the interaction completely, because heavy JS abstractions inflate bundles and state bugs:

1. **Semantic HTML5:** Use `<main>`, `<nav>`, `<header>`, `<section aria-labelledby>`, `<button type="button">`, `<a href>`, `<details>/<summary>`, and `<dialog>`.
2. **Modern CSS Layout:** Use CSS Grid (`minmax(0, 1fr)`), Flexbox (`gap`), `clamp()`, `aspect-ratio`, and `design-tokens.css` variables. Never measure column widths in JS `resize` listeners when CSS handles reflow natively.
3. **Narrow Local State:** Keep state inside the smallest owning component and derive filtered lists or totals (`useMemo` / `computed`) instead of duplicating state.
4. **Motion Cleanup:** Isolate Anime.js v4 calls inside `createScope({ root })` and invoke `scope.revert()` on unmount (see [atlas-motion-animejs](../atlas-motion-animejs/SKILL.md)).

## 3. Preventing 6 Common Frontend Bugs

- **Flex/Grid Overflow:** Add `min-width: 0` on flex/grid children holding long headings, URLs, or tables so content wraps cleanly at `320px`.
- **Async Race Conditions / Double Submit:** Disable submit buttons while `isSubmitting` is active and use `AbortController` on live search so stale responses never overwrite newer results.
- **Stable List Keys:** Use unique entity IDs (`item.id`) rather than array indices as `key` props in filterable or sortable lists.
- **Accessible Controls:** Add `aria-label` on icon-only buttons and maintain crisp `:focus-visible` outlines for keyboard navigation.
- **Valid Asset Paths:** Verify every referenced image, SVG, and font exists on disk to prevent `404` console errors.
- **Final Cleanup:** Remove unused imports, dead CSS classes, and stray `console.log` statements before delivery.
