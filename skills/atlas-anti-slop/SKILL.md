---
name: atlas-anti-slop
description: "Use when writing or reviewing UI copy, component structure, and styling to eliminate 18 AI slop clichés using slop-scan.mjs. Do not use for non-UI backend logic."
---

# Atlas Anti-Slop — Eliminating AI UI Clichés

AI *slop* appears when pages rely on generic template scaffolding and empty marketing buzzwords disconnected from the subject. Read [slop-patterns.md](../../references/slop-patterns.md) and run `slop-scan.mjs` during Phases 4 and 6.

## 1. Bad vs Good Code Contrasts

### Contrast A: Hero Section & Copy

Avoid (generic purple-blue SaaS template with unsubstantiated claims):
```html
<section class="text-center py-24 bg-gradient-to-r from-purple-600 to-blue-600">
  <span class="rounded-full px-4 py-1 bg-white/10">✨ Comprehensive Solution for the Digital Era</span>
  <h1 class="bg-clip-text text-transparent">Seamlessly Transform Your Business Workflow</h1>
  <p>Trusted by 10,000+ innovative teams worldwide.</p>
</section>
```

Prefer (domain-specific, evidence-backed, tokenized):
```html
<section class="hero-split" data-hero>
  <div class="hero-copy">
    <p class="eyebrow">Mechanical Watch Restoration • Midtown Bench, Est. 2014</p>
    <h1 data-hero-title>Swiss &amp; Japanese automatic overhaul with a 12-month rate warranty.</h1>
    <p class="lead">Complimentary beat-error amplitude check while you wait. Standard service turnaround is 5–10 business days subject to OEM part availability.</p>
    <div class="hero-actions">
      <a data-primary class="btn-primary" href="#estimate">Check Service Estimate</a>
      <a class="btn-secondary" href="#hours">Hours &amp; Bench Location</a>
    </div>
  </div>
  <figure class="hero-evidence">
    <img src="/assets/timegrapher-bench.webp" width="960" height="720" alt="Mechanical movement positional timing inspection on a bench timegrapher" />
    <figcaption>Five-position timing calibration recorded prior to pickup.</figcaption>
  </figure>
</section>
```

### Contrast B: Features & Proof Presentation

- **Ban 3 Symmetric Emoji/Icon Cards:** Three identical cards labeled `🚀 Fast`, `🔒 Secure`, and `💎 Best` convey zero domain facts and could be pasted onto any website unchanged.
- **Lead with Domain Proof:** Replace generic adjectives with specification tables, transparent pricing breakdowns, live domain calculators, or measurable process timelines.

## 2. Pre-Delivery Checklist

1. **Substitution Test:** If changing the brand name to "CloudAI" keeps 90% of the page plausible, rewrite the first two sections around domain-specific workflows and numbers.
2. **Zero Buzzword Clichés:** Remove phrases like `unlock the power of`, `revolutionize your`, `seamlessly integrate`, `elevate your digital`, `next-generation platform`, and `"Not just X, it's Y"`.
3. **Zero Empty Ornament:** Avoid decorative glowing blur blobs, fake macOS window traffic lights on non-developer sites, and infinite floating loops next to prose.
4. **Scanner Check:** Run `node <atlas>/skills/atlas-checker/scripts/slop-scan.mjs <project-root>` until it reports `0` errors and resolve every actionable warning.

- **Visible Debug State Controls:** Never render `Populated / Loading / Empty / Error` dropdowns or buttons in production UI; if retained for local testing, hide them with `hidden` and guard behind `?debug=1`.
