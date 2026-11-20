---
name: atlas-fullstack-contracts
description: "Use when connecting frontend UI to typed API/mock data adapters, auth session boundaries, environment variable hygiene, and SEO/OpenGraph metadata. Do not use for pure presentational components without data or page metadata."
---

# Atlas Fullstack Contracts & Production Readiness

This module governs boundaries between UI components and data layers, authentication states, environment variables, and document metadata.

## 1. Data Layer & Service Adapters (`src/data/` or `src/services/`)

Separate type definitions and data access from presentation components, because hardcoding large raw arrays inside JSX/Vue components makes code brittle and hard to test:

- **Typed Domain Schemas:** Define TypeScript types, JSDoc typedefs, or validation schemas for core entities (`Product`, `BookingSlot`, `ApiError`) in dedicated modules.
- **Clear Service Boundaries:** Route reads and mutations through service functions (`getRooms()`, `submitInquiry(payload)`). In frontend prototypes without a live backend, store state locally and label simulations honestly so users never assume live transactions occurred.

## 2. Client-Side Security & Auth Boundaries

- **Environment Secret Hygiene:** Never place private API keys, database credentials, or signing secrets inside `NEXT_PUBLIC_*`, `VITE_*`, `PUBLIC_*`, or client bundles, as all frontend code is readable in the browser. Provide `.env.example` with safe placeholder keys.
- **DOM XSS Prevention:** Never inject untrusted user strings or URL query parameters into `dangerouslySetInnerHTML`, `v-html`, or `.innerHTML`; use text nodes or sanitized templating.
- **Auth Session States:** For authenticated apps, explicitly design signed-out, signing-in, invalid-credentials, and expired-session states.

## 3. Document Metadata, Assets, & CLS Prevention

- Define `<title>`, `<meta name="description">`, `<html lang="...">`, semantic landmarks (`<header>`, `<main id="main-content">`, `<footer>`), and a keyboard skip link.
- Provide OpenGraph metadata (`og:title`, `og:description`, `og:type`) and a local or inline SVG favicon so browsers do not log `404 /favicon.ico` errors.
- Always declare `width` and `height` (or CSS `aspect-ratio`) on `<img>`, `<video>`, and `<svg>` elements so the browser reserves layout space prior to load.
