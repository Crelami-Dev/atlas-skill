# 18 Detectable AI Slop Patterns (Bad vs Good Reference)

`slop-scan.mjs` catches automated code signals; patterns marked **[Visual/Critic]** are verified during screenshot inspection and `atlas-critic` review.

| # | Slop Pattern | Detection | Why It Fails | Concrete Unslop Replacement |
|---|---|---|---|---|
| 1 | Purple-to-blue neon gradient identity | `slop-scan` (`warn`) | Screams default LLM SaaS template | Tinted neutral canvas (`#faf8f5` / `#0f172a`) + 1 domain-grounded solid accent |
| 2 | Rainbow `bg-clip-text` hero headings | `slop-scan` (`warn`) | Destroys legibility and looks machine-generated | High-contrast ink color + expressive display font weight/scale |
| 3 | Emoji used as UI/button/card icons (`🚀✨🔒`) | `slop-scan` (`warn`) | Inconsistent across OSes; looks amateur | Crisp 1.5px stroke SVG icons (Lucide/Phosphor) only where aiding action scanning, or pure typography |
| 4 | Placeholder copy & leaked photo badges (`Lorem ipsum`, `Your Company`, `Ganti dengan foto asli`, `SLOT FOTO 01`, `[Data Klien Diperlukan]`) | `slop-scan` & `check-visual-proof` (`error`) | Fakes completion or leaks developer/template instructions to visitors | Real domain copy + silent `data-photo-slot` editorial specimen plates (ask user for assets in chat, never in DOM) |
| 5 | AI marketing buzzwords (`di era digital`, `seamless`, `elevate`) | `slop-scan` (`warn`) | Zero informational content | Concrete nouns, measurable mechanisms, and direct Indonesian/English phrasing |
| 6 | Anime.js v3 legacy syntax (`anime({ targets })`, `easing:`) | `slop-scan` & `check-motion-v4` (`error`) | Crashes at runtime on Anime.js v4 | Named v4 imports: `animate(targets, { ease: 'outQuart' })` + `createScope` |
| 7 | Static CSS `opacity: 0` on `.reveal` / `[data-animate]` | `check-motion-v4` (`error`) | Leaves blank page on SSR, no-JS, or reduced-motion | Keep base CSS `opacity: 1`; pass `[0, 1]` keyframes inside `createScope()` |
| 8 | Font proliferation (`> 2` font families) | `slop-scan` & `check-tokens` (`error`) | Visual chaos & slow LCP | Max 2 intentional roles (`--font-display` + `--font-sans` or `--font-mono`) |
| 9 | Unchosen system-Arial/Roboto default with uniform weights | **[Visual/Critic]** | No typographic voice or hierarchy | Pair deliberate webfont roles with fluid `clamp()` scale and tight display tracking |
| 10 | Centered Hero + 2 Pill Buttons + 3 Symmetric Icon Cards | `slop-scan` (`warn`) + **[Visual]** | Interchangeable across every industry | Use Editorial Asymmetric Split, Interactive Workbench, or Swiss Spec Ledger |
| 11 | Unmotivated glassmorphism (`backdrop-blur` on every card) | `slop-scan` (`warn`) | Lowers text contrast & GPU frame rate | Solid layered surface tokens (`--color-bg` vs `--color-surface-elevated`) + crisp `1px` borders |
| 12 | Fabricated social proof (`10,000+ users`, `4.9/5 stars`, fake quotes) | **[Visual/Critic]** | Dishonest & legally/ethically flawed | Show real product mechanics, transparent pricing/process, or verifiable specs |
| 13 | Decorative fake widgets (charts/calculators ignoring inputs) | **[Visual/Critic]** | Breaks user trust immediately on click | Wire real math/filtering logic or use a clear static diagram |
| 14 | Uniform pill badges above every single `<h2>` section | **[Visual/Critic]** | Repetitive scaffolding masquerading as hierarchy | Reserve eyebrows only where section category context is genuinely needed |
| 15 | Infinite floating/pulsing animations next to reading text | `check-motion-v4` + **[Visual]** | Violates WCAG 2.2.2 & distracts reading | Event-driven or one-shot entrance motion (`<= 1200ms`) that settles to calm static state |
| 16 | Desktop grid stacked blindly into a 9-screen mobile scroll | **[Visual/Critic]** | Exhausting on `375x667` phones | Recompose mobile density: compact horizontal specs, accordions for secondary detail, sticky CTA |
| 17 | Low-contrast muted grey text (`#9ca3af` on `#f3f4f6`) | `quick-check` (`error`) | Fails WCAG 4.5:1 readability | Calibrate `--color-muted` to `>= 4.5:1` against both `--color-bg` and `--color-surface` |
| 18 | Happy-path-only lists/forms with zero empty or error states | **[Visual/Critic]** | Breaks as soon as user filters or submits invalid input | Implement the full 5-State View Contract from `atlas-ui-architecture` |
