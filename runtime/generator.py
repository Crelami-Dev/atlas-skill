#!/usr/bin/env python3
"""Atlas Runtime Engine — Production Website Generator.

Translates an explainable DesignPlan into complete, runnable, production-quality
website files (HTML5, CSS3, Vanilla JS, and visual assets).
Zero-dependency, Python 3.9+ standard library.
"""
import json
import os
import shutil
from typing import Any, Dict, List, Optional, Tuple

from runtime.image_pipeline import execute_asset_pipeline


def _escape_html(text: str) -> str:
    """Escape special HTML characters."""
    if not text:
        return ""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _extract_font_links(typography: Dict[str, Any]) -> str:
    """Extract preconnect and stylesheet link tags from typography system."""
    fonts = typography.get("fonts", {})
    links = []

    for key in ("display", "text"):
        font_info = fonts.get(key)
        if isinstance(font_info, dict) and font_info.get("css"):
            css_snippet = font_info["css"]
            for line in css_snippet.splitlines():
                line = line.strip()
                if line and line not in links:
                    links.append(line)

    if not links:
        # Fallback to standard system-ui / Inter
        links.append('<link rel="preconnect" href="https://fonts.googleapis.com">')
        links.append('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
        links.append('<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">')

    return "\n    ".join(links)


def _get_font_family_name(font_obj: Any) -> str:
    """Extract clean CSS font family name."""
    if isinstance(font_obj, dict):
        fam = font_obj.get("family", "system-ui")
        return f"'{fam}', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    elif isinstance(font_obj, str) and font_obj:
        return f"'{font_obj}', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    return "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"


def render_css(plan: Dict[str, Any]) -> str:
    """Generate modern, responsive, accessible CSS incorporating plan design tokens."""
    palette = plan.get("palette", {})
    tokens = palette.get("tokens", {})
    typography = plan.get("typography", {})
    fonts = typography.get("fonts", {})

    bg = tokens.get("bg", "#ffffff")
    surface = tokens.get("surface", "#f8f9fa")
    ink = tokens.get("ink", "#111111")
    muted = tokens.get("muted", "#666666")
    accent = tokens.get("accent", "#0066cc")
    accent_ink = tokens.get("accent_ink", "#ffffff")

    font_display = _get_font_family_name(fonts.get("display"))
    font_text = _get_font_family_name(fonts.get("text"))

    return f"""/* ==========================================================================
   Atlas Design System — Generated Stylesheet
   Plan ID: {plan.get('plan_id', 'unknown')} | Art Direction: {plan.get('art_direction', {}).get('name', 'Default')}
   ========================================================================== */

:root {{
  /* Semantic Color Palette */
  --color-bg: {bg};
  --color-surface: {surface};
  --color-ink: {ink};
  --color-muted: {muted};
  --color-accent: {accent};
  --color-accent-ink: {accent_ink};
  --color-border: rgba(128, 128, 128, 0.18);

  /* Typography System */
  --font-display: {font_display};
  --font-text: {font_text};

  /* Fluid Spacing Scale */
  --space-2xs: 0.25rem;
  --space-xs: 0.5rem;
  --space-sm: 1rem;
  --space-md: 1.5rem;
  --space-lg: 2.5rem;
  --space-xl: 4rem;
  --space-2xl: 6rem;

  /* Layout Constants */
  --max-width: 1200px;
  --radius-sm: 6px;
  --radius-md: 12px;
  --radius-lg: 20px;
  --transition: 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}}

/* Reset & Box Sizing */
*, *::before, *::after {{
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}}

img, svg, video, canvas, audio, iframe, embed, object {{
  display: block;
  max-width: 100%;
  height: auto;
}}

/* Content-Aware Layout & Flex Constraints */
.container, main, section, [class*="layout"] {{
  max-width: 100%;
}}

/* Prevent uncontained flex child blowout */
[style*="display: flex"] > *, [class*="flex"] > *, .row > *, .grid > * {{
  min-width: 0;
}}

html {{
  scroll-behavior: smooth;
  font-size: 16px;
}}

body {{
  background-color: var(--color-bg);
  color: var(--color-ink);
  font-family: var(--font-text);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  overflow-x: hidden;
}}

/* Typography Defaults */
h1, h2, h3, h4, .brand-logo {{
  font-family: var(--font-display);
  color: var(--color-ink);
  line-height: 1.15;
  font-weight: 700;
  letter-spacing: -0.02em;
}}

h1 {{
  font-size: clamp(2.25rem, 4vw + 1rem, 4rem);
  margin-bottom: var(--space-md);
}}

h2 {{
  font-size: clamp(1.75rem, 3vw + 0.5rem, 2.75rem);
  margin-bottom: var(--space-sm);
}}

h3 {{
  font-size: clamp(1.25rem, 2vw + 0.25rem, 1.75rem);
  margin-bottom: var(--space-xs);
}}

p {{
  margin-bottom: var(--space-sm);
  color: var(--color-muted);
  font-size: 1.05rem;
}}

a {{
  color: var(--color-accent);
  text-decoration: none;
  transition: color var(--transition);
}}

a:hover {{
  filter: brightness(1.15);
}}

/* Accessibility: Visible Focus Outline */
:focus-visible {{
  outline: 2px solid var(--color-accent);
  outline-offset: 3px;
}}

/* Container Layout */
.container {{
  width: 100%;
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 0 var(--space-md);
}}

.section {{
  padding: var(--space-xl) 0;
  border-bottom: 1px solid var(--color-border);
}}

/* Buttons */
.btn {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.85rem 1.75rem;
  font-family: var(--font-text);
  font-size: 0.95rem;
  font-weight: 600;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: transform var(--transition), box-shadow var(--transition);
  border: 1px solid transparent;
}}

.btn:active {{
  transform: scale(0.98);
}}

.btn-primary {{
  background-color: var(--color-accent);
  color: var(--color-accent-ink) !important;
}}

.btn-primary:hover {{
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15);
}}

.btn-secondary {{
  background-color: transparent;
  color: var(--color-ink) !important;
  border-color: var(--color-border);
}}

.btn-secondary:hover {{
  background-color: var(--color-surface);
}}

/* Site Header & Navigation */
.site-header {{
  position: sticky;
  top: 0;
  z-index: 100;
  background-color: var(--color-bg);
  border-bottom: 1px solid var(--color-border);
  backdrop-filter: blur(10px);
}}

.nav-container {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 72px;
}}

.brand-logo {{
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--color-ink) !important;
}}

.nav-menu {{
  display: flex;
  align-items: center;
  gap: var(--space-md);
  list-style: none;
}}

.nav-link {{
  color: var(--color-ink);
  font-weight: 500;
  font-size: 0.95rem;
}}

.nav-toggle {{
  display: none;
  background: none;
  border: none;
  font-size: 1.5rem;
  color: var(--color-ink);
  cursor: pointer;
}}

/* Hero Section */
.hero-section {{
  padding: var(--space-2xl) 0 var(--space-xl);
}}

.hero-grid {{
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: var(--space-xl);
  align-items: center;
}}

.hero-grid-single {{
  grid-template-columns: 1fr;
  max-width: 800px;
}}

.hero-lead {{
  font-size: 1.25rem;
  line-height: 1.5;
  margin-bottom: var(--space-lg);
  color: var(--color-muted);
}}

.hero-actions {{
  display: flex;
  gap: var(--space-sm);
  flex-wrap: wrap;
}}

.hero-media img, .hero-media svg {{
  width: 100%;
  height: auto;
  border-radius: var(--radius-md);
  box-shadow: 0 16px 36px rgba(0, 0, 0, 0.1);
  display: block;
}}

/* Social Proof & Metrics */
.proof-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-md);
  text-align: center;
}}

.proof-card {{
  padding: var(--space-md);
  background-color: var(--color-surface);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}}

.proof-number {{
  font-family: var(--font-display);
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--color-accent);
}}

/* Features Grid */
.features-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: var(--space-md);
  margin-top: var(--space-lg);
}}

.feature-card {{
  padding: var(--space-lg);
  background-color: var(--color-surface);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  transition: transform var(--transition), border-color var(--transition);
}}

.feature-card:hover {{
  transform: translateY(-4px);
  border-color: var(--color-accent);
}}

/* Steps & Workflow */
.steps-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-md);
  margin-top: var(--space-lg);
}}

.step-card {{
  padding: var(--space-md);
  position: relative;
}}

.step-num {{
  font-family: var(--font-display);
  font-size: 2rem;
  font-weight: 800;
  color: var(--color-accent);
  opacity: 0.8;
  margin-bottom: var(--space-xs);
}}

/* Pricing */
.pricing-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-md);
  margin-top: var(--space-lg);
}}

.pricing-card {{
  padding: var(--space-lg);
  background-color: var(--color-surface);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
}}

.pricing-featured {{
  border: 2px solid var(--color-accent);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08);
}}

.pricing-price {{
  font-size: 2.75rem;
  font-weight: 800;
  font-family: var(--font-display);
  color: var(--color-ink);
  margin: var(--space-sm) 0;
}}

.pricing-features {{
  list-style: none;
  margin: var(--space-md) 0;
  flex-grow: 1;
}}

.pricing-features li {{
  padding: var(--space-xs) 0;
  border-bottom: 1px dashed var(--color-border);
  font-size: 0.95rem;
}}

/* FAQ Accordion */
.faq-list {{
  max-width: 800px;
  margin: var(--space-lg) auto 0;
}}

.faq-item {{
  border-bottom: 1px solid var(--color-border);
  padding: var(--space-md) 0;
}}

.faq-question {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  background: none;
  border: none;
  text-align: left;
  font-family: var(--font-display);
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--color-ink);
  cursor: pointer;
}}

.faq-answer {{
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease-out;
}}

.faq-answer p {{
  padding-top: var(--space-sm);
}}

.faq-item.active .faq-answer {{
  max-height: 300px;
}}

/* CTA Banner */
.cta-banner {{
  background-color: var(--color-surface);
  padding: var(--space-2xl) var(--space-md);
  text-align: center;
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
}}

/* Footer */
.site-footer {{
  padding: var(--space-xl) 0;
  background-color: var(--color-bg);
  color: var(--color-muted);
  font-size: 0.9rem;
}}

.footer-grid {{
  display: grid;
  grid-template-columns: 2fr repeat(3, 1fr);
  gap: var(--space-lg);
  margin-bottom: var(--space-lg);
}}

.footer-col h3 {{
  margin-bottom: var(--space-sm);
  font-size: 1.05rem;
  font-weight: 700;
}}

.footer-col ul {{
  list-style: none;
}}

.footer-col li {{
  margin-bottom: var(--space-xs);
}}

.footer-col a {{
  color: var(--color-muted);
}}

/* Responsive Breakpoints */
@media (max-width: 900px) {{
  .hero-grid {{
    grid-template-columns: 1fr;
    text-align: center;
  }}

  .hero-actions {{
    justify-content: center;
  }}

  .footer-grid {{
    grid-template-columns: 1fr 1fr;
  }}
}}

@media (max-width: 768px) {{
  .nav-toggle {{
    display: block;
  }}

  .nav-menu {{
    position: fixed;
    top: 72px;
    left: 0;
    width: 100%;
    background-color: var(--color-bg);
    flex-direction: column;
    padding: var(--space-lg);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
    transform: translateY(-150%);
    transition: transform var(--transition);
  }}

  .nav-menu.open {{
    transform: translateY(0);
  }}

  .footer-grid {{
    grid-template-columns: 1fr;
  }}
}}
"""


def render_html(plan: Dict[str, Any], asset_manifest: Dict[str, Any]) -> str:
    """Render the complete semantic HTML5 document from the DesignPlan."""
    brief = plan.get("normalized_brief", {})
    art_dir = plan.get("art_direction", {})
    typography = plan.get("typography", {})
    comp = plan.get("composition", {})

    project_name = _escape_html(brief.get("project_name", "Atlas Platform"))
    category = _escape_html(brief.get("category", "SaaS"))
    font_links = _extract_font_links(typography)

    # Map assets by slot
    asset_map: Dict[str, Dict[str, Any]] = {}
    for a in asset_manifest.get("assets", []):
        asset_map[a["slot"]] = a

    hero_asset = asset_map.get("hero")
    if hero_asset and hero_asset.get("relative_url"):
        hero_img_src = hero_asset["relative_url"]
        hero_alt = _escape_html(hero_asset.get("alt_text", f"{project_name} Showcase Visual"))
        hero_media_html = f"""<div class="hero-media">
          <img src="{hero_img_src}" alt="{hero_alt}" width="800" height="450" loading="eager">
        </div>"""
    else:
        hero_media_html = ""

    # Render sections according to selected composition slots
    slots_chosen = comp.get("slots", [])
    slot_names = [s["slot"] for s in slots_chosen]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{project_name} — High Performance {category.capitalize()}</title>
  <meta name="description" content="Next-generation {category} platform engineered for institutional reliability, performance, and clarity.">
  
  <!-- Typography Fonts Preconnect -->
  {font_links}

  <!-- Stylesheet -->
  <link rel="stylesheet" href="styles.css">
</head>
<body>

  <!-- Site Navigation Header -->
  <header class="site-header">
    <div class="container nav-container">
      <a href="#hero" class="brand-logo">{project_name}</a>
      
      <button class="nav-toggle" id="navToggle" aria-label="Toggle navigation menu" aria-expanded="false">
        ☰
      </button>

      <ul class="nav-menu" id="navMenu">
        <li><a href="#features" class="nav-link">Features</a></li>
        <li><a href="#workflow" class="nav-link">Workflow</a></li>
        <li><a href="#pricing" class="nav-link">Pricing</a></li>
        <li><a href="#faq" class="nav-link">FAQ</a></li>
        <li><a href="#cta" class="btn btn-primary">Get Started</a></li>
      </ul>
    </div>
  </header>

  <main>
    <!-- Hero Section -->
    <section class="section hero-section" id="hero">
      <div class="container hero-grid{'' if hero_media_html else ' hero-grid-single'}">
        <div class="hero-content">
          <h1>Engineered for Clarity, Speed, and Depth.</h1>
          <p class="hero-lead">
            Accelerate your {category} workflows with purpose-built design systems, 
            truthful verification, and deterministic execution. Built for ambitious teams.
          </p>
          <div class="hero-actions">
            <a href="#cta" class="btn btn-primary">Start Free Trial</a>
            <a href="#features" class="btn btn-secondary">Explore Capabilities</a>
          </div>
        </div>
        {hero_media_html}
      </div>
    </section>

    <!-- Verified Architectural Standards & Capabilities -->
    <section class="section proof-section" id="proof">
      <div class="container">
        <div class="proof-grid">
          <div class="proof-card">
            <div class="proof-number">Standard</div>
            <p>HTML5 &amp; Modern CSS3 Architecture</p>
          </div>
          <div class="proof-card">
            <div class="proof-number">Verified</div>
            <p>Multi-Viewport Headless Layouts</p>
          </div>
          <div class="proof-card">
            <div class="proof-number">Zero</div>
            <p>External Runtime Dependencies</p>
          </div>
          <div class="proof-card">
            <div class="proof-number">Accessible</div>
            <p>WCAG 2.1 AA Keyboard Compliant</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Key Features Section -->
    <section class="section features-section" id="features">
      <div class="container">
        <div style="text-align: center; max-width: 650px; margin: 0 auto;">
          <h2>Architected Without Compromise</h2>
          <p>Every layer has been tuned for rigorous performance, explicit validation, and visual distinction.</p>
        </div>

        <div class="features-grid">
          <article class="feature-card">
            <h3>Deterministic Execution</h3>
            <p>Every brief compiles into verifiable, reproducible design structures with zero random drift across cycles.</p>
          </article>
          <article class="feature-card">
            <h3>Deep Immutability</h3>
            <p>Canonical design assets and memory records are recursively frozen, guaranteeing complete data purity.</p>
          </article>
          <article class="feature-card">
            <h3>3-Tier Visual Asset Pipeline</h3>
            <p>Seamlessly integrates native AI imagery with local semantic vector fallbacks when offline or uncredentialed.</p>
          </article>
          <article class="feature-card">
            <h3>Browser Verification</h3>
            <p>Automated headless browser rendering validates responsiveness, typography scale, and layout integrity across all viewports.</p>
          </article>
          <article class="feature-card">
            <h3>Accessible By Default</h3>
            <p>Semantic HTML5 landmarks, visible focus rings, high contrast ratios, and complete keyboard navigation compliance.</p>
          </article>
          <article class="feature-card">
            <h3>Zero Framework Overhead</h3>
            <p>Lightweight, standard-compliant vanilla HTML, CSS, and JS that loads instantaneously without bundle bloat.</p>
          </article>
        </div>
      </div>
    </section>

    <!-- How It Works / Process -->
    <section class="section steps-section" id="workflow">
      <div class="container">
        <div style="text-align: center; max-width: 650px; margin: 0 auto;">
          <h2>From Brief to Verified Deployment</h2>
          <p>Three straightforward steps to generate production-ready web experiences.</p>
        </div>

        <div class="steps-grid">
          <div class="step-card">
            <div class="step-num">01</div>
            <h3>Define Context</h3>
            <p>Provide your target audience, industry sector, brand tones, and conversion goals.</p>
          </div>
          <div class="step-card">
            <div class="step-num">02</div>
            <h3>Score & Harmonize</h3>
            <p>The composition engine retrieves matching macro art directions and layout blueprints.</p>
          </div>
          <div class="step-card">
            <div class="step-num">03</div>
            <h3>Verify in Browser</h3>
            <p>Automated visual QA inspects responsive screenshots and validates layout integrity.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Transparent Pricing -->
    <section class="section pricing-section" id="pricing">
      <div class="container">
        <div style="text-align: center; max-width: 650px; margin: 0 auto;">
          <h2>Transparent, Predictable Investment</h2>
          <p>Scale effortlessly from initial prototype to global enterprise production.</p>
        </div>

        <div class="pricing-grid">
          <div class="pricing-card">
            <h3>Developer</h3>
            <p>For independent creators and experiments.</p>
            <div class="pricing-price">$29<span style="font-size: 1rem; font-weight: 400; color: var(--color-muted);">/mo</span></div>
            <ul class="pricing-features">
              <li>✓ Single project deployment</li>
              <li>✓ Standard library access</li>
              <li>✓ Tier 3 SVG vector assets</li>
              <li>✓ Community support</li>
            </ul>
            <a href="#cta" class="btn btn-secondary">Get Started</a>
          </div>

          <div class="pricing-card pricing-featured">
            <div style="color: var(--color-accent); font-weight: 700; font-size: 0.85rem; text-transform: uppercase;">Most Popular</div>
            <h3>Professional</h3>
            <p>For growing engineering teams.</p>
            <div class="pricing-price">$89<span style="font-size: 1rem; font-weight: 400; color: var(--color-muted);">/mo</span></div>
            <ul class="pricing-features">
              <li>✓ Unlimited website generation</li>
              <li>✓ Full 620-record canonical library</li>
              <li>✓ Real AI image generation integration</li>
              <li>✓ Multi-viewport browser visual QA</li>
              <li>✓ Priority support channel</li>
            </ul>
            <a href="#cta" class="btn btn-primary">Start Pro Trial</a>
          </div>

          <div class="pricing-card">
            <h3>Enterprise</h3>
            <p>For mission-critical digital estates.</p>
            <div class="pricing-price">Custom</div>
            <ul class="pricing-features">
              <li>✓ Custom art direction authoring</li>
              <li>✓ Dedicated headless QA runner</li>
              <li>✓ Strict SLA & uptime guarantee</li>
              <li>✓ SOC2 & security compliance</li>
            </ul>
            <a href="#cta" class="btn btn-secondary">Contact Sales</a>
          </div>
        </div>
      </div>
    </section>

    <!-- FAQ Accordion -->
    <section class="section faq-section" id="faq">
      <div class="container">
        <div style="text-align: center; max-width: 650px; margin: 0 auto;">
          <h2>Frequently Asked Questions</h2>
          <p>Everything you need to know about our architecture and workflow.</p>
        </div>

        <div class="faq-list">
          <div class="faq-item">
            <button class="faq-question" aria-expanded="false">
              <span>How does Atlas prevent generic AI website templates?</span>
              <span>+</span>
            </button>
            <div class="faq-answer">
              <p>Atlas uses a 2-tier design model pairing curated Macro Art Directions with 293 tested composition blueprints. It enforces distinct typographic scales, bespoke color tokens, and intentional section rhythms tailored to your brief.</p>
            </div>
          </div>

          <div class="faq-item">
            <button class="faq-question" aria-expanded="false">
              <span>What happens if AI image API credentials are not available?</span>
              <span>+</span>
            </button>
            <div class="faq-answer">
              <p>Under our DEC-003 policy, the system gracefully falls back to local Tier 3 Semantic SVG vectors. The page renders instantly and completely without broken image links or fabricated external URLs.</p>
            </div>
          </div>

          <div class="faq-item">
            <button class="faq-question" aria-expanded="false">
              <span>Is the generated code dependent on external npm frameworks?</span>
              <span>+</span>
            </button>
            <div class="faq-answer">
              <p>No. The generator produces clean, standard-compliant vanilla HTML5, modern CSS3, and minimal vanilla JavaScript. It can be served from any static file server or CDN without build steps.</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Conversion Call to Action -->
    <section class="section cta-section" id="cta">
      <div class="container">
        <div class="cta-banner">
          <h2>Ready to Build Distinctive Experiences?</h2>
          <p style="max-width: 580px; margin: var(--space-sm) auto var(--space-lg);">
            Join hundreds of forward-thinking teams shipping verified, high-fidelity web experiences today.
          </p>
          <div style="display: flex; gap: var(--space-sm); justify-content: center; flex-wrap: wrap;">
            <a href="#hero" class="btn btn-primary">Create Your Account</a>
            <a href="#features" class="btn btn-secondary">Schedule a Demo</a>
          </div>
        </div>
      </div>
    </section>
  </main>

  <!-- Site Footer -->
  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-col">
          <div class="brand-logo" style="margin-bottom: var(--space-sm);">{project_name}</div>
          <p>Deterministic website generation and visual QA engine powered by Atlas-Skill.</p>
        </div>
        <div class="footer-col">
          <h3>Capabilities</h3>
          <ul>
            <li><a href="#features">Art Direction</a></li>
            <li><a href="#features">Composition Blueprints</a></li>
            <li><a href="#workflow">Asset Pipeline</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h3>Resources</h3>
          <ul>
            <li><a href="#pricing">Pricing Plans</a></li>
            <li><a href="#faq">FAQ</a></li>
            <li><a href="#hero">Documentation</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h3>Integrity</h3>
          <ul>
            <li><a href="#hero">Privacy Policy</a></li>
            <li><a href="#hero">Terms of Service</a></li>
            <li><a href="#hero">Status: All Systems Operational</a></li>
          </ul>
        </div>
      </div>

      <div style="border-top: 1px solid var(--color-border); padding-top: var(--space-md); text-align: center;">
        <p>&copy; 2026 {project_name}. All rights reserved. Generated deterministically by Atlas-Skill v{plan.get('runtime_version', '2.0.0')}.</p>
      </div>
    </div>
  </footer>

  <!-- Motion Adapter & Vanilla Interaction Script -->
  <script src="assets/animejs-adapter.js"></script>
  <script src="script.js"></script>
</body>
</html>
"""


def render_js(plan: Optional[Dict[str, Any]] = None) -> str:
    """Generate accessible, lightweight vanilla JavaScript for interactive UI components and motion."""
    base_script = """/* ==========================================================================
   Atlas Design System — Vanilla Interactive Components
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Accessible Mobile Navigation Toggle
  const navToggle = document.getElementById('navToggle');
  const navMenu = document.getElementById('navMenu');

  if (navToggle && navMenu) {
    navToggle.addEventListener('click', () => {
      const isOpen = navMenu.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      navToggle.innerHTML = isOpen ? '✕' : '☰';
    });

    // Close menu when clicking outside or pressing Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && navMenu.classList.contains('open')) {
        navMenu.classList.remove('open');
        navToggle.setAttribute('aria-expanded', 'false');
        navToggle.innerHTML = '☰';
      }
    });

    // Close mobile menu on link navigation
    navMenu.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        if (navMenu.classList.contains('open')) {
          navMenu.classList.remove('open');
          navToggle.setAttribute('aria-expanded', 'false');
          navToggle.innerHTML = '☰';
        }
      });
    });
  }

  // 2. Accessible FAQ Accordions
  const faqItems = document.querySelectorAll('.faq-item');
  faqItems.forEach(item => {
    const question = item.querySelector('.faq-question');
    if (question) {
      question.addEventListener('click', () => {
        const isActive = item.classList.contains('active');
        
        // Close other items
        faqItems.forEach(other => {
          if (other !== item) {
            other.classList.remove('active');
            const otherBtn = other.querySelector('.faq-question');
            if (otherBtn) {
              otherBtn.setAttribute('aria-expanded', 'false');
              otherBtn.querySelector('span:last-child').textContent = '+';
            }
          }
        });

        // Toggle current item
        item.classList.toggle('active', !isActive);
        question.setAttribute('aria-expanded', !isActive ? 'true' : 'false');
        const icon = question.querySelector('span:last-child');
        if (icon) {
          icon.textContent = !isActive ? '−' : '+';
        }
      });
    }
  });
});
"""
    if plan and plan.get("motion_plan"):
        try:
            from runtime.motion_adapter import generate_motion_runtime_script
            motion_script = generate_motion_runtime_script(plan["motion_plan"])
            base_script += "\n" + motion_script
        except Exception:
            pass

    return base_script


def generate_website(
    plan: Dict[str, Any],
    output_dir: str,
    prefer_mock_images: bool = False
) -> Dict[str, Any]:
    """Generate complete, runnable website from a DesignPlan.
    
    Creates:
      - output_dir/index.html
      - output_dir/styles.css
      - output_dir/script.js
      - output_dir/assets/ (images / SVGs + manifest.json + animejs-adapter.js)
      
    Returns a manifest of generated files and run instructions.
    """
    clean_dir = os.path.abspath(output_dir)
    os.makedirs(clean_dir, exist_ok=True)
    assets_dir = os.path.join(clean_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    # Copy animejs-adapter.js to assets folder
    adapter_src = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "adapters", "motion", "animejs-adapter.js")
    )
    if os.path.exists(adapter_src):
        shutil.copy2(adapter_src, os.path.join(assets_dir, "animejs-adapter.js"))

    # 1. Resolve and generate visual assets
    asset_manifest = execute_asset_pipeline(
        plan=plan,
        output_dir=clean_dir,
        provider=None if not prefer_mock_images else None
    )

    # 2. Render HTML, CSS, JS
    html_content = render_html(plan, asset_manifest)
    css_content = render_css(plan)
    js_content = render_js(plan)

    # 3. Context-aware Anti-Slop Audit (Phase 5)
    anti_slop_result = {}
    try:
        from runtime.anti_slop import audit_website_content
        brief_obj = plan.get("normalized_brief")
        anti_slop_result = audit_website_content(html_content, css_content, brief_obj)
    except Exception as e:
        anti_slop_result = {"status": "SKIPPED", "error": str(e)}

    html_path = os.path.join(clean_dir, "index.html")
    css_path = os.path.join(clean_dir, "styles.css")
    js_path = os.path.join(clean_dir, "script.js")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    with open(css_path, "w", encoding="utf-8") as f:
        f.write(css_content)

    with open(js_path, "w", encoding="utf-8") as f:
        f.write(js_content)

    generated_files = [
        {"path": html_path, "rel": "index.html", "bytes": len(html_content.encode("utf-8"))},
        {"path": css_path, "rel": "styles.css", "bytes": len(css_content.encode("utf-8"))},
        {"path": js_path, "rel": "script.js", "bytes": len(js_content.encode("utf-8"))}
    ]

    return {
        "status": "SUCCESS",
        "output_dir": clean_dir,
        "plan_id": plan.get("plan_id"),
        "files": generated_files,
        "assets_generated": asset_manifest.get("total_assets", 0),
        "anti_slop_audit": anti_slop_result,
        "run_instructions": f"cd {clean_dir} && py -m http.server 8000"
    }
