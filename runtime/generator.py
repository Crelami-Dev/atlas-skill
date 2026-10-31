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

    density = plan.get("normalized_brief", {}).get("density", "med")
    if density == "low":
        space_2xs = "0.35rem"
        space_xs = "0.75rem"
        space_sm = "1.25rem"
        space_md = "2rem"
        space_lg = "3.5rem"
        space_xl = "5.5rem"
        space_2xl = "8rem"
        max_width = "1320px"
        h1_clamp = "clamp(2.0rem, 4.5vw + 0.8rem, 4.75rem)"
        h2_clamp = "clamp(1.65rem, 3vw + 0.5rem, 3.0rem)"
    elif density == "high":
        space_2xs = "0.2rem"
        space_xs = "0.4rem"
        space_sm = "0.75rem"
        space_md = "1.15rem"
        space_lg = "1.85rem"
        space_xl = "2.75rem"
        space_2xl = "4.5rem"
        max_width = "1140px"
        h1_clamp = "clamp(1.75rem, 2.5vw + 0.5rem, 2.75rem)"
        h2_clamp = "clamp(1.35rem, 2vw + 0.25rem, 2.0rem)"
    else:  # med
        space_2xs = "0.25rem"
        space_xs = "0.5rem"
        space_sm = "1rem"
        space_md = "1.5rem"
        space_lg = "2.5rem"
        space_xl = "4rem"
        space_2xl = "6rem"
        max_width = "1200px"
        h1_clamp = "clamp(2.0rem, 3.5vw + 0.75rem, 3.75rem)"
        h2_clamp = "clamp(1.5rem, 2.5vw + 0.5rem, 2.5rem)"

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
  --space-2xs: {space_2xs};
  --space-xs: {space_xs};
  --space-sm: {space_sm};
  --space-md: {space_md};
  --space-lg: {space_lg};
  --space-xl: {space_xl};
  --space-2xl: {space_2xl};

  /* Layout Constants */
  --max-width: {max_width};
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
  text-wrap: balance;
  overflow-wrap: break-word;
}}

h1 {{
  font-size: {h1_clamp};
  margin-bottom: var(--space-md);
  letter-spacing: -0.025em;
}}

h2 {{
  font-size: {h2_clamp};
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
  line-height: 1.6;
  max-width: 65ch;
  overflow-wrap: break-word;
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
  min-height: 44px;
  min-width: 44px;
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
  min-height: 44px;
  display: inline-flex;
  align-items: center;
}}

.nav-toggle {{
  display: none;
  background: none;
  border: none;
  font-size: 1.5rem;
  color: var(--color-ink);
  cursor: pointer;
  min-height: 44px;
  min-width: 44px;
  align-items: center;
  justify-content: center;
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
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--space-md);
  text-align: center;
}}

.proof-card {{
  padding: var(--space-md);
  background-color: var(--color-surface);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  min-height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}}

.proof-number {{
  font-family: var(--font-display);
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--color-accent);
  line-height: 1.1;
  margin-bottom: var(--space-2xs);
}}

/* Features Grid */
.features-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 280px), 1fr));
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

/* Asymmetric Bento Grid (atlas:features-bento) */
.bento-grid {{
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  grid-auto-rows: minmax(180px, auto);
  grid-auto-flow: dense;
  gap: var(--space-md);
  margin-top: var(--space-lg);
  max-width: 100%;
}}

.bento-tile {{
  padding: var(--space-lg);
  background-color: var(--color-surface);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  gap: var(--space-xs);
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
  transition: transform var(--transition), border-color var(--transition);
}}

.bento-tile:hover {{
  transform: translateY(-3px);
  border-color: var(--color-accent);
}}

.bento-tile-lead {{
  grid-column: span 2;
  grid-row: span 2;
  border-color: var(--color-accent);
  min-height: 410px;
  justify-content: space-between;
}}

.bento-tile-wide {{
  grid-column: span 2;
  grid-row: span 1;
}}

.bento-tile-standard {{
  grid-column: span 1;
  grid-row: span 1;
}}

.bento-kicker {{
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-accent);
}}

.bento-tile h3 {{
  font-size: clamp(1.1rem, 1.5vw + 0.25rem, 1.4rem);
  line-height: 1.25;
  margin-bottom: 0;
  overflow-wrap: break-word;
}}

.bento-tile-lead h3 {{
  font-size: clamp(1.45rem, 2.2vw + 0.35rem, 2rem);
}}

.bento-tile p {{
  margin-bottom: 0;
  font-size: 0.95rem;
  line-height: 1.5;
  overflow-wrap: break-word;
}}

.bento-lead-diagram {{
  width: 100%;
  height: auto;
  margin-top: var(--space-sm);
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  background-color: var(--color-bg);
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
  min-height: 44px;
  padding: var(--space-sm) 0;
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
  visibility: hidden;
  transition: max-height 0.3s ease-out;
}}

.faq-answer p {{
  padding-top: var(--space-sm);
}}

.faq-item.active .faq-answer {{
  max-height: 300px;
  visibility: visible;
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
@media (max-width: 1024px) {{
  .proof-grid {{
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: var(--space-md);
  }}

  .bento-grid {{
    grid-template-columns: repeat(2, minmax(0, 1fr));
    grid-auto-rows: auto;
  }}

  .bento-tile-lead {{
    grid-column: span 2;
    grid-row: span 1;
    min-height: 0;
  }}

  .bento-tile-wide {{
    grid-column: span 2;
    grid-row: span 1;
  }}

  .bento-tile-standard {{
    grid-column: span 1;
    grid-row: span 1;
  }}
}}

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
    display: inline-flex;
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

  .proof-grid {{
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: var(--space-sm);
  }}

  .steps-grid {{
    grid-template-columns: 1fr;
  }}

  .features-grid {{
    grid-template-columns: 1fr;
  }}

  .bento-grid {{
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: var(--space-sm);
  }}

  .bento-tile {{
    padding: var(--space-md);
  }}

  .bento-tile-lead,
  .bento-tile-wide {{
    grid-column: span 2;
    grid-row: span 1;
  }}

  .bento-tile-standard {{
    grid-column: span 1;
    grid-row: span 1;
  }}

  .bento-tile h3 {{
    font-size: 1rem;
  }}

  .bento-tile-lead h3 {{
    font-size: 1.25rem;
  }}

  .bento-tile p {{
    font-size: 0.85rem;
  }}

  .footer-grid {{
    grid-template-columns: 1fr;
  }}
}}

@media (max-width: 540px) {{
  .proof-grid {{
    grid-template-columns: 1fr;
    gap: var(--space-sm);
  }}

  .proof-card {{
    padding: var(--space-sm);
  }}

  .proof-number {{
    font-size: 1.85rem;
  }}

  .pricing-grid {{
    grid-template-columns: 1fr;
  }}

  .container {{
    padding: 0 16px;
  }}

  .hero-actions {{
    flex-direction: column;
    align-items: stretch;
  }}

  .hero-actions .btn {{
    width: 100%;
  }}
}}
"""


DEFAULT_BENTO_ITEMS: List[Dict[str, str]] = [
    {
        "kicker": "Primary Architecture",
        "title": "Modular Component Composition",
        "description": (
            "Hierarchical layout architecture organizing varied functional capabilities "
            "through proportional card geometry and explicit design tokens."
        ),
    },
    {
        "kicker": "Document Outline",
        "title": "Semantic HTML5 Landmarks",
        "description": (
            "Structured navigation, main, and section regions supporting assistive "
            "technologies and clear document hierarchy."
        ),
    },
    {
        "kicker": "Design Tokens",
        "title": "Cohesive Token Pacing",
        "description": (
            "Unified spatial increments, fluid typographic scale, and balanced "
            "surface contrast across components."
        ),
    },
    {
        "kicker": "Responsive Systems",
        "title": "Fluid Viewport Adaptation",
        "description": (
            "Multi-viewport grid rules maintaining structured presentation across "
            "desktop, tablet, and two-column mobile displays."
        ),
    },
    {
        "kicker": "Visual Verification",
        "title": "Automated Layout Inspection",
        "description": (
            "Headless browser verification checking bounding-box containment, "
            "responsive breakpoints, and DOM structure."
        ),
    },
]


def _render_bento_features_grid(plan: Dict[str, Any]) -> str:
    """Render an asymmetric Bento Grid for the atlas:features-bento composition pattern."""
    raw_items = plan.get("bento_items")
    if isinstance(raw_items, (list, tuple)) and len(raw_items) >= 4:
        items = list(raw_items)
    else:
        items = list(DEFAULT_BENTO_ITEMS)

    lead_svg = (
        '<svg role="img" aria-label="Modular component composition blueprint" '
        'class="bento-lead-diagram" viewBox="0 0 480 160" width="480" height="160" '
        'xmlns="http://www.w3.org/2000/svg">'
        '<rect x="12" y="12" width="210" height="136" rx="8" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.35"/>'
        '<rect x="28" y="28" width="110" height="12" rx="4" fill="currentColor" opacity="0.45"/>'
        '<rect x="28" y="50" width="178" height="8" rx="4" fill="currentColor" opacity="0.2"/>'
        '<rect x="28" y="66" width="150" height="8" rx="4" fill="currentColor" opacity="0.2"/>'
        '<rect x="28" y="96" width="178" height="36" rx="6" fill="currentColor" opacity="0.1"/>'
        '<rect x="238" y="12" width="230" height="62" rx="8" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.25"/>'
        '<rect x="254" y="28" width="96" height="10" rx="4" fill="currentColor" opacity="0.35"/>'
        '<rect x="254" y="46" width="180" height="8" rx="4" fill="currentColor" opacity="0.18"/>'
        '<rect x="238" y="86" width="109" height="62" rx="8" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.25"/>'
        '<rect x="359" y="86" width="109" height="62" rx="8" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.25"/>'
        '</svg>'
    )

    tile_html_parts: List[str] = []
    for idx, item in enumerate(items):
        kicker = _escape_html(item.get("kicker", f"Capability 0{idx + 1}"))
        title = _escape_html(item.get("title", f"Capability {idx + 1}"))
        desc = _escape_html(item.get("description", "Structured architectural capability."))

        if idx == 0:
            role_cls = "bento-tile bento-tile-lead"
            extra_visual = f"\n            {lead_svg}"
        elif idx == 3:
            role_cls = "bento-tile bento-tile-wide"
            extra_visual = ""
        else:
            role_cls = "bento-tile bento-tile-standard"
            extra_visual = ""

        tile_html_parts.append(
            f"""          <div class="{role_cls}">
            <span class="bento-kicker">{kicker}</span>
            <h3>{title}</h3>
            <p>{desc}</p>{extra_visual}
          </div>"""
        )

    tiles_joined = "\n".join(tile_html_parts)
    return f"""        <div class="bento-grid">
{tiles_joined}
        </div>"""


def _resolve_brief_content(plan: Dict[str, Any]) -> Dict[str, Any]:
    """Synthesize category-aware, authentic brand copy from the normalized brief."""
    brief = plan.get("normalized_brief", {})
    project_name = _escape_html(brief.get("project_name", "Atlas Platform"))
    category = _escape_html(brief.get("category", "saas")).lower()
    tones = [t.lower() for t in brief.get("tones", [])]

    is_luxury = any(t in tones for t in ("luxury", "editorial", "calm", "refined", "quiet")) or category in (
        "fashion", "luxury", "hospitality", "restaurant", "architecture", "personal-portfolio"
    )
    is_technical = any(t in tones for t in ("technical", "austere", "precise", "functional")) or category in (
        "dev-tool", "developer", "cloud", "infra", "security", "data"
    )
    is_agency = any(t in tones for t in ("bold", "curated", "confident", "expressive")) or category in (
        "agency", "design", "studio-portfolio", "creative"
    )

    if is_luxury:
        h1 = f"{project_name} — Timeless Craftsmanship &amp;&nbsp;Architectural Form"
        hero_lead = f"Immerse yourself in bespoke creations defined by peerless materiality, meticulous finishing, and quiet distinction. Handcrafted for discerning patrons worldwide."
        features_title = "Artisanal Mastery"
        features_subtitle = "Every silhouette is refined through exacting restraint and time-honored atelier traditions."
        feature_cards = [
            ("Bespoke Craftsmanship", "Every creation embodies peerless artisanal mastery, tactile purity, and sculptural discipline."),
            ("Curated Exclusivity", "Rare, limited-edition commissions tailored to discerning collectors and international patrons."),
            ("Architectural Silhouette", "Proportional harmony balanced with uncompromising contemporary restraint and presence."),
            ("Heritage & Provenance", "Rooted in storied traditions, executed with forward-looking aesthetic integrity."),
            ("Impeccable Finishing", "Exacting attention to detail across every touchpoint, seam, contour, and surface."),
            ("Private Concierge", "Discreet, dedicated consultation addressing bespoke requests, private viewings, and acquisitions.")
        ]
        proof_items = [
            ("Bespoke", "Handcrafted in Private Ateliers"),
            ("Limited", "Numbered Collector Editions"),
            ("Heritage", "Time-Honored Provenance"),
            ("Atelier", "Private Client Viewings &amp; Salons")
        ]
        workflow_title = "Atelier Commission Lifecycle"
        workflow_subtitle = "A contemplative progression from material provenance to final hand-finished masterpiece."
        workflow_steps = [
            ("01", "Material Sourcing &amp; Provenance", "Curating rare, sustainably certified precious metals and ethically sourced stones of peerless purity."),
            ("02", "Sculptural Form &amp; Prototyping", "Iterative hand-modeling in our atelier, harmonizing anatomical comfort with architectural volume."),
            ("03", "Master Finishing &amp; Archival Seal", "Precision hand-polishing, microscopic setting, individual serial engraving, and archival registration.")
        ]
        pricing_title = "Private Acquisitions &amp; Bespoke Commissions"
        pricing_subtitle = "Every creation is crafted to individual commission or issued in strictly numbered, registered editions."
        pricing_tiers = [
            {
                "name": "Collector Salon",
                "badge": None,
                "price": "Inquire",
                "period": "",
                "description": "Private acquisition of limited-edition numbered atelier releases.",
                "features": [
                    "Numbered atelier certificate of provenance",
                    "Hand-crafted presentation vault",
                    "Archival registration with master atelier record",
                    "Private salon preview invitation"
                ],
                "cta_text": "Inquire Availability",
                "cta_cls": "btn btn-secondary"
            },
            {
                "name": "Bespoke Commission",
                "badge": "Haute Exclusive",
                "price": "Custom",
                "period": "",
                "description": "One-of-a-kind creation designed in personal dialogue with our master artisan.",
                "features": [
                    "Private atelier consultation with head artisan",
                    "Exclusive noble material sourcing and stone curation",
                    "Custom sculptural casing and hand-engraved monogram",
                    "Lifetime atelier maintenance and inspection",
                    "Private white-glove salon handover"
                ],
                "cta_text": "Request Consultation",
                "cta_cls": "btn btn-primary"
            },
            {
                "name": "Heritage Patron",
                "badge": None,
                "price": "Private",
                "period": "",
                "description": "Sustained collaborative patronage for multi-piece collector series.",
                "features": [
                    "First-right access to rare material allocations",
                    "Direct atelier archive documentation access",
                    "Bespoke horological or jewelry suite creation",
                    "Global private courier and concierge delivery"
                ],
                "cta_text": "Contact Concierge",
                "cta_cls": "btn btn-secondary"
            }
        ]
        faq_title = "Atelier &amp; Commission Insights"
        faq_subtitle = "Essential details regarding our bespoke process, numbered editions, and private consultations."
        faq_items = [
            ("How can I arrange a private atelier consultation?",
             "Consultations may be arranged through our private concierge. We accommodate clients via private salon appointments and offer personalized consultations for international patrons."),
            ("Are your creations issued in limited numbered quantities?",
             "Yes. Every collection is strictly limited in volume, with each individual piece engraved with an archival serial mark and accompanied by an official certificate of provenance."),
            ("What bespoke customization options are available?",
             "Our master artisans accommodate bespoke commissions ranging from specific precious material selections and gemstone settings to completely unique sculptural silhouettes crafted from the ground up.")
        ]
        cta_h2 = "Experience Bespoke Distinction"
        cta_lead = "Schedule a private consultation at our flagship atelier to explore bespoke commissions."
        cta_btn1 = "Request Private Appointment"
        cta_btn2 = "Explore Atelier"
        footer_desc = "Curated haute creation and timeless design executed with bespoke artisanal integrity."
    elif is_technical:
        h1 = f"{project_name} — High-Throughput Infrastructure Architecture"
        hero_lead = f"Engineered for sub-millisecond telemetry, deterministic consistency, and low-latency operational throughput across cloud and distributed environments."
        features_title = "Architected for Critical Workloads"
        features_subtitle = "Rigorous telemetry, deterministic state transitions, and low-latency throughput at scale."
        feature_cards = [
            ("Kernel Telemetry", "Granular, real-time observability across distributed nodes with sub-millisecond overhead."),
            ("Zero-Allocation Runtime", "High-efficiency execution pathways engineered for continuous sustained throughput."),
            ("Deterministic Consistency", "Strong transactional invariants guaranteed across heterogeneous network partitions."),
            ("Continuous Verification", "Automated contract verification validating system invariants before every deployment."),
            ("Native Concurrency", "Non-blocking asynchronous event loops scaled linearly across available computing cores."),
            ("Declarative Schemas", "Infrastructure-as-code orchestration specifications versioned cleanly in your repository.")
        ]
        proof_items = [
            ("Kernel", "Sub-Millisecond Low Latency"),
            ("Zero-Alloc", "High-Throughput Memory Loops"),
            ("Invariants", "Deterministic State Transitions"),
            ("Telemetry", "Continuous Distributed Observability")
        ]
        workflow_title = "Architecture &amp; Deployment Lifecycle"
        workflow_subtitle = "A disciplined pipeline from kernel telemetry integration to verified distributed execution."
        workflow_steps = [
            ("01", "Instrument &amp; Integrate", "Embed lightweight eBPF hooks and SDK telemetry probes directly into your microservice runtime."),
            ("02", "Ingestion &amp; Stream Processing", "Stream high-frequency metric events through low-latency memory-mapped ring buffers without garbage-collection pauses."),
            ("03", "Continuous Verification", "Enforce invariant validation and real-time anomaly detection across every distributed node partition.")
        ]
        pricing_title = "Transparent, Infrastructure-Aligned Capacity"
        pricing_subtitle = "Predictable capacity tiers engineered for high-throughput operational workloads."
        pricing_tiers = [
            {
                "name": "Developer Node",
                "badge": None,
                "price": "$49",
                "period": "/mo",
                "description": "For individual systems engineers, staging clusters, and local benchmarking.",
                "features": [
                    "Up to 5 telemetry partition nodes",
                    "Sub-millisecond kernel ring buffer ingestion",
                    "Automated invariant checks in CI/CD pipelines",
                    "Standard metrics retention and Prometheus export",
                    "Developer community and issue tracker access"
                ],
                "cta_text": "Deploy Node",
                "cta_cls": "btn btn-secondary"
            },
            {
                "name": "Production Cluster",
                "badge": "Recommended",
                "price": "$199",
                "period": "/mo",
                "description": "For high-throughput production infrastructure with continuous operational load.",
                "features": [
                    "Unlimited partition node clustering",
                    "Zero-allocation memory pipeline runtime",
                    "Distributed consensus & replication engine",
                    "Prometheus & OpenTelemetry native exporters",
                    "Dedicated technical engineering support"
                ],
                "cta_text": "Launch Production",
                "cta_cls": "btn btn-primary"
            },
            {
                "name": "Enterprise Dedicated",
                "badge": None,
                "price": "Custom",
                "period": "",
                "description": "For global high-concurrency systems requiring custom SLA boundaries.",
                "features": [
                    "Dedicated bare-metal cluster deployment",
                    "Custom kernel module extensions",
                    "Air-gapped VPC and on-premise installation",
                    "Custom telemetry retention policies",
                    "24/7 dedicated site reliability escalation"
                ],
                "cta_text": "Contact Engineering",
                "cta_cls": "btn btn-secondary"
            }
        ]
        faq_title = "Technical Specifications &amp; Systems Architecture"
        faq_subtitle = "Detailed technical answers regarding telemetry latency, runtime invariants, and integration."
        faq_items = [
            ("How does the runtime maintain low latency under sustained load?",
             "The engine utilizes zero-allocation ring buffers and memory-mapped IPC channels, bypassing runtime garbage collection pauses and ensuring deterministic event dispatching."),
            ("Can the platform integrate into existing OpenTelemetry pipelines?",
             "Yes. Native OpenTelemetry and Prometheus metric exporters are integrated into the core kernel, allowing continuous export of span metrics and trace headers with zero third-party agent overhead."),
            ("What failure modes are handled during network partition events?",
             "The cluster employs distributed state invariants that detect partition boundaries instantly, maintaining local causal consistency and reconciling diverging logs upon partition healing.")
        ]
        cta_h2 = "Deploy Scalable Infrastructure Today"
        cta_lead = "Get started in minutes with our native CLI, automated benchmarks, and comprehensive SDK."
        cta_btn1 = "Deploy Kernel"
        cta_btn2 = "Inspect Benchmarks"
        footer_desc = "High-performance systems infrastructure and telemetry architecture engineered for reliability."
    elif is_agency:
        h1 = f"{project_name} — Distinctive Brand Architecture &amp; Strategy"
        hero_lead = f"Partnering with ambitious founders and cultural leaders to articulate authentic brand identities, systemic typography, and singular digital experiences."
        features_title = "Strategic Craft &amp; Vision"
        features_subtitle = "Transforming strategic clarity into resonant visual identities and commanding brand presence."
        feature_cards = [
            ("Brand Architecture", "Structured strategic frameworks that crystallize identity and amplify market differentiation."),
            ("Editorial Direction", "Compelling narratives and visual rhythms that captivate high-intent audiences."),
            ("Systemic Typography", "Custom type design and spatial hierarchies establishing distinct brand authority."),
            ("Digital Touchpoints", "Fluid, responsive interactive environments that translate vision into lasting engagement."),
            ("Cultural Resonance", "Insight-driven creative direction tuned to modern culture and audience sensibilities."),
            ("Comprehensive Rollout", "Unified production pipelines from conceptual genesis to multi-channel execution.")
        ]
        proof_items = [
            ("Strategy", "Systemic Brand Architecture"),
            ("Typography", "Proprietary Type Systems"),
            ("Digital", "Responsive Interactive Spaces"),
            ("Impact", "Cross-Disciplinary Cultural Reach")
        ]
        workflow_title = "Strategic Engagement &amp; Rollout"
        workflow_subtitle = "From foundational strategic clarity to comprehensive multi-surface brand rollout."
        workflow_steps = [
            ("01", "Immersion &amp; Positioning", "Uncovering fundamental brand truth, market whitespace, and cultural context through executive dialogue."),
            ("02", "Systemic Identity Design", "Crafting proprietary typography, generative color systems, and layout hierarchies that command attention."),
            ("03", "Multi-Touchpoint Rollout", "Orchestrating design systems across responsive digital platforms, physical collateral, and environmental spaces.")
        ]
        pricing_title = "Commission &amp; Partnership Models"
        pricing_subtitle = "Tailored engagement structures for brand architecture, design systems, and digital flagships."
        pricing_tiers = [
            {
                "name": "Strategic Sprint",
                "badge": None,
                "price": "$12,000",
                "period": "/project",
                "description": "Focused 4-week engagement to define brand positioning and identity foundations.",
                "features": [
                    "Brand strategy & audience architecture",
                    "Core visual direction & design tokens",
                    "Typographic system specification",
                    "Executive readout and asset toolkit",
                    "Design guidelines handbook"
                ],
                "cta_text": "Book Strategic Sprint",
                "cta_cls": "btn btn-secondary"
            },
            {
                "name": "Full Identity Architecture",
                "badge": "Flagship",
                "price": "$35,000",
                "period": "/project",
                "description": "End-to-end design transformation from strategic genesis to multi-surface rollout.",
                "features": [
                    "Comprehensive brand identity & narrative system",
                    "Proprietary typographic scale & custom vector marks",
                    "Responsive digital design system & component library",
                    "Cross-platform design guidelines & asset bundles",
                    "Dedicated creative director supervision"
                ],
                "cta_text": "Initiate Commission",
                "cta_cls": "btn btn-primary"
            },
            {
                "name": "Creative Retainer",
                "badge": None,
                "price": "$8,500",
                "period": "/mo",
                "description": "Ongoing creative direction and design evolution for high-growth enterprises.",
                "features": [
                    "Continuous design sprint cadence",
                    "Product UI & marketing campaign assets",
                    "Senior design team integration",
                    "Quarterly strategic brand alignment",
                    "Priority creative availability"
                ],
                "cta_text": "Explore Partnership",
                "cta_cls": "btn btn-secondary"
            }
        ]
        faq_title = "Creative Process &amp; Partnership FAQ"
        faq_subtitle = "Everything you need to know about our studio process, timelines, and deliverables."
        faq_items = [
            ("What does your strategic immersion phase entail?",
             "We conduct deep stakeholder interviews, market whitespace analysis, and cultural trend research to identify the authentic narrative core of your brand before sketching a single layout or choosing a font."),
            ("Do you deliver production-ready code or design tokens?",
             "We deliver comprehensive design systems including fully documented design tokens, accessible color palettes, modular component guidelines, and standards-compliant production frontends."),
            ("What is the typical timeline for an end-to-end brand architecture project?",
             "Strategic sprints typically span 4 weeks, while full brand transformations with digital platform rollouts range from 8 to 14 weeks depending on the breadth of touchpoints and surface requirements.")
        ]
        cta_h2 = "Shape Your Next Brand Chapter"
        cta_lead = "Let us articulate your market narrative with strategic clarity, uncompromising craft, and visual distinction."
        cta_btn1 = "Initiate Commission"
        cta_btn2 = "Review Case Studies"
        footer_desc = "Strategic design, brand architecture, and digital experience direction for ambitious enterprises."
    else:
        h1 = f"{project_name} — Purpose-Built for {category.capitalize()} Excellence"
        hero_lead = f"Accelerate your outcomes with purpose-built operational workflows, reliable data pipelines, and intelligent interfaces."
        features_title = "Engineered for Performance"
        features_subtitle = "Tuned for rigorous performance, explicit validation, and operational clarity."
        feature_cards = [
            ("Continuous Automation", "Streamline multi-step workflows with reliable, trigger-based pipeline automation."),
            ("Unified Data Layer", "Synchronize operational intelligence across your entire organizational footprint."),
            ("Enterprise Security", "End-to-end data encryption, role-based access governance, and strict compliance."),
            ("Real-Time Telemetry", "Instantaneous visual analytics and actionable insights on demand."),
            ("Collaborative Workspaces", "Shared operational environments engineered for frictionless cross-team alignment."),
            ("Extensible Architecture", "Modular API-first integrations connecting directly with your toolchain.")
        ]
        proof_items = [
            ("Automation", "End-to-End Pipeline Automation"),
            ("Modular", "Extensible Service Architecture"),
            ("Security", "Role-Based Access Governance"),
            ("Observability", "Continuous Real-Time Telemetry")
        ]
        workflow_title = f"{category.capitalize()} Operational Lifecycle"
        workflow_subtitle = "A structured, reliable progression engineered for operational clarity and speed."
        workflow_steps = [
            ("01", "Connect &amp; Configure", "Integrate your existing data sources and initialize operational parameters with minimal configuration."),
            ("02", "Automate &amp; Transform", "Execute deterministic validation rules and streamline pipeline throughput across operations."),
            ("03", "Monitor &amp; Optimize", "Track operational metrics with real-time observability, telemetry dashboards, and actionable insights.")
        ]
        pricing_title = "Predictable, Value-Driven Investment"
        pricing_subtitle = f"Transparent plans designed to scale seamlessly with your {category} requirements."
        pricing_tiers = [
            {
                "name": "Starter Tier",
                "badge": None,
                "price": "$39",
                "period": "/mo",
                "description": f"Essential operational capabilities for early-stage {category} teams.",
                "features": [
                    "Core workflow automation pipelines",
                    "Standard data connector integrations",
                    "Operational dashboard reporting",
                    "Standard email support"
                ],
                "cta_text": "Start Free Trial",
                "cta_cls": "btn btn-secondary"
            },
            {
                "name": "Professional Tier",
                "badge": "Most Popular",
                "price": "$99",
                "period": "/mo",
                "description": f"Advanced tooling and capacity for scaling {category} operations.",
                "features": [
                    "High-volume data processing throughput",
                    "Custom transformation and validation rules",
                    "Multi-user workspace collaboration",
                    "Priority operational assistance"
                ],
                "cta_text": "Upgrade to Pro",
                "cta_cls": "btn btn-primary"
            },
            {
                "name": "Enterprise Tier",
                "badge": None,
                "price": "Custom",
                "period": "",
                "description": f"Comprehensive custom infrastructure for enterprise-scale {category} operations.",
                "features": [
                    "Custom integrations and dedicated throughput",
                    "Role-based security governance",
                    "Dedicated account management",
                    "Custom SLA and onboarding assistance"
                ],
                "cta_text": "Contact Sales",
                "cta_cls": "btn btn-secondary"
            }
        ]
        faq_title = "Frequently Asked Questions"
        faq_subtitle = "Essential insights into our platform capabilities, onboarding, and architecture."
        faq_items = [
            (f"How quickly can we integrate {project_name} into our existing workflow?",
             "Most teams deploy within hours using our modular connectors, declarative configurations, and step-by-step onboarding walkthroughs."),
            ("What security controls are enforced across the platform?",
             "We implement strict role-based access control, cryptographic verification for all pipeline transitions, and comprehensive audit logging across all workspace actions."),
            ("Can we customize and extend the default automation pipelines?",
             "Yes. The platform provides an extensible API and modular hook architecture, allowing you to attach custom validation rules, external webhooks, and automated notifications.")
        ]
        cta_h2 = "Ready to Build Distinctive Experiences?"
        cta_lead = f"Join forward-thinking teams shipping verified, high-fidelity {category} experiences today."
        cta_btn1 = "Get Started Free"
        cta_btn2 = "Schedule Consultation"
        footer_desc = f"Purpose-built {category} platform engineered for operational reliability and user experience."

    return {
        "h1": h1,
        "hero_lead": hero_lead,
        "features_title": features_title,
        "features_subtitle": features_subtitle,
        "feature_cards": feature_cards,
        "proof_items": proof_items,
        "workflow_title": workflow_title,
        "workflow_subtitle": workflow_subtitle,
        "workflow_steps": workflow_steps,
        "pricing_title": pricing_title,
        "pricing_subtitle": pricing_subtitle,
        "pricing_tiers": pricing_tiers,
        "faq_title": faq_title,
        "faq_subtitle": faq_subtitle,
        "faq_items": faq_items,
        "cta_h2": cta_h2,
        "cta_lead": cta_lead,
        "cta_btn1": cta_btn1,
        "cta_btn2": cta_btn2,
        "footer_desc": footer_desc
    }


def render_html(plan: Dict[str, Any], asset_manifest: Dict[str, Any]) -> str:
    """Render the complete semantic HTML5 document from the DesignPlan."""
    brief = plan.get("normalized_brief", {})
    typography = plan.get("typography", {})
    comp = plan.get("composition", {})

    project_name = _escape_html(brief.get("project_name", "Atlas Platform"))
    category = _escape_html(brief.get("category", "SaaS"))
    font_links = _extract_font_links(typography)
    content = _resolve_brief_content(plan)

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

    # Composition slots filtering
    slots_chosen = comp.get("slots", [])
    planned_slots = [s["slot"] for s in slots_chosen] if slots_chosen else ["hero", "features", "cta"]
    features_slot = next((s for s in slots_chosen if s.get("slot") == "features"), None)
    is_bento_features = bool(
        features_slot and features_slot.get("pattern_id") == "atlas:features-bento"
    )

    if is_bento_features:
        features_body_html = _render_bento_features_grid(plan)
    else:
        card_htmls = []
        for title, desc in content["feature_cards"]:
            card_htmls.append(f"""          <article class="feature-card">
            <h3>{title}</h3>
            <p>{desc}</p>
          </article>""")
        cards_joined = "\n".join(card_htmls)
        features_body_html = f"""        <div class="features-grid">
{cards_joined}
        </div>"""

    # Assemble sections dynamically based on planned slots
    sections_html = []

    # 1. Hero Section
    if "hero" in planned_slots or "app_shell" in planned_slots:
        sections_html.append(f"""    <!-- Hero Section -->
    <section class="section hero-section" id="hero">
      <div class="container hero-grid{'' if hero_media_html else ' hero-grid-single'}">
        <div class="hero-content">
          <h1>{content["h1"]}</h1>
          <p class="hero-lead">
            {content["hero_lead"]}
          </p>
          <div class="hero-actions">
            <a href="#cta" class="btn btn-primary">{content["cta_btn1"]}</a>
            <a href="#features" class="btn btn-secondary">{content["cta_btn2"]}</a>
          </div>
        </div>
        {hero_media_html}
      </div>
    </section>""")

    # 2. Proof Section
    if "proof" in planned_slots or "social_proof" in planned_slots:
        proof_card_htmls = []
        for num, text in content["proof_items"]:
            proof_card_htmls.append(f"""          <div class="proof-card">
            <div class="proof-number">{num}</div>
            <p>{text}</p>
          </div>""")
        proof_cards_joined = "\n".join(proof_card_htmls)
        sections_html.append(f"""    <!-- Verified Capabilities & Proof -->
    <section class="section proof-section" id="proof">
      <div class="container">
        <div class="proof-grid">
{proof_cards_joined}
        </div>
      </div>
    </section>""")

    # 3. Features Section
    if "features" in planned_slots:
        sections_html.append(f"""    <!-- Key Features Section -->
    <section class="section features-section" id="features">
      <div class="container">
        <div style="text-align: center; max-width: 650px; margin: 0 auto;">
          <h2>{content["features_title"]}</h2>
          <p>{content["features_subtitle"]}</p>
        </div>

{features_body_html}
      </div>
    </section>""")

    # 4. Workflow Section
    if any(s in planned_slots for s in ("workflow", "how-it-works", "steps")):
        step_cards = []
        for step_num, step_title, step_desc in content.get("workflow_steps", []):
            step_cards.append(f"""          <div class="step-card">
            <div class="step-num">{step_num}</div>
            <h3>{step_title}</h3>
            <p>{step_desc}</p>
          </div>""")
        step_cards_joined = "\n".join(step_cards)
        workflow_title = content.get("workflow_title", "Operational Workflow")
        workflow_subtitle = content.get("workflow_subtitle", "A structured methodology engineered for operational clarity.")
        sections_html.append(f"""    <!-- How It Works / Process -->
    <section class="section steps-section" id="workflow">
      <div class="container">
        <div style="text-align: center; max-width: 650px; margin: 0 auto;">
          <h2>{workflow_title}</h2>
          <p>{workflow_subtitle}</p>
        </div>

        <div class="steps-grid">
{step_cards_joined}
        </div>
      </div>
    </section>""")

    # 5. Pricing Section
    if "pricing" in planned_slots:
        pricing_cards = []
        for tier in content.get("pricing_tiers", []):
            tier_name = _escape_html(tier.get("name", "Tier"))
            badge = tier.get("badge")
            badge_html = f'\n            <div style="color: var(--color-accent); font-weight: 700; font-size: 0.85rem; text-transform: uppercase;">{_escape_html(badge)}</div>' if badge else ""
            featured_cls = " pricing-featured" if badge else ""
            desc = _escape_html(tier.get("description", ""))
            price = _escape_html(tier.get("price", ""))
            period = _escape_html(tier.get("period", ""))
            period_html = f'<span style="font-size: 1rem; font-weight: 400; color: var(--color-muted);">{period}</span>' if period else ""
            cta_text = _escape_html(tier.get("cta_text", "Get Started"))
            cta_cls = tier.get("cta_cls", "btn btn-secondary")
            
            features_li = "\n".join(f"              <li>✓ {_escape_html(f)}</li>" for f in tier.get("features", []))
            
            pricing_cards.append(f"""          <div class="pricing-card{featured_cls}">{badge_html}
            <h3>{tier_name}</h3>
            <p>{desc}</p>
            <div class="pricing-price">{price}{period_html}</div>
            <ul class="pricing-features">
{features_li}
            </ul>
            <a href="#cta" class="{cta_cls}">{cta_text}</a>
          </div>""")
        pricing_cards_joined = "\n".join(pricing_cards)
        pricing_title = content.get("pricing_title", "Predictable Investment")
        pricing_subtitle = content.get("pricing_subtitle", "Scale effortlessly with transparent, value-driven tiers.")
        sections_html.append(f"""    <!-- Transparent Pricing -->
    <section class="section pricing-section" id="pricing">
      <div class="container">
        <div style="text-align: center; max-width: 650px; margin: 0 auto;">
          <h2>{pricing_title}</h2>
          <p>{pricing_subtitle}</p>
        </div>

        <div class="pricing-grid">
{pricing_cards_joined}
        </div>
      </div>
    </section>""")

    # 6. FAQ Section
    if "faq" in planned_slots:
        faq_items = []
        for q, a in content.get("faq_items", []):
            faq_items.append(f"""          <div class="faq-item">
            <button class="faq-question" aria-expanded="false">
              <span>{_escape_html(q)}</span>
              <span>+</span>
            </button>
            <div class="faq-answer">
              <p>{_escape_html(a)}</p>
            </div>
          </div>""")
        faq_joined = "\n".join(faq_items)
        faq_title = content.get("faq_title", "Frequently Asked Questions")
        faq_subtitle = content.get("faq_subtitle", "Essential insights into our approach, architecture, and engagement.")
        sections_html.append(f"""    <!-- FAQ Accordion -->
    <section class="section faq-section" id="faq">
      <div class="container">
        <div style="text-align: center; max-width: 650px; margin: 0 auto;">
          <h2>{faq_title}</h2>
          <p>{faq_subtitle}</p>
        </div>

        <div class="faq-list">
{faq_joined}
        </div>
      </div>
    </section>""")

    # 7. CTA Section
    if "cta" in planned_slots:
        sections_html.append(f"""    <!-- Conversion Call to Action -->
    <section class="section cta-section" id="cta">
      <div class="container">
        <div class="cta-banner">
          <h2>{content["cta_h2"]}</h2>
          <p style="max-width: 580px; margin: var(--space-sm) auto var(--space-lg);">
            {content["cta_lead"]}
          </p>
          <div style="display: flex; gap: var(--space-sm); justify-content: center; flex-wrap: wrap;">
            <a href="#hero" class="btn btn-primary">{content["cta_btn1"]}</a>
            <a href="#features" class="btn btn-secondary">{content["cta_btn2"]}</a>
          </div>
        </div>
      </div>
    </section>""")

    main_content_html = "\n\n".join(sections_html)

    # Dynamic Navigation Menu Links
    nav_links = []
    if "features" in planned_slots:
        nav_links.append('<li><a href="#features" class="nav-link">Features</a></li>')
    if any(s in planned_slots for s in ("workflow", "how-it-works", "steps")):
        nav_links.append('<li><a href="#workflow" class="nav-link">Workflow</a></li>')
    if "pricing" in planned_slots:
        nav_links.append('<li><a href="#pricing" class="nav-link">Pricing</a></li>')
    if "faq" in planned_slots:
        nav_links.append('<li><a href="#faq" class="nav-link">FAQ</a></li>')
    if "cta" in planned_slots:
        nav_links.append(f'<li><a href="#cta" class="btn btn-primary">{content["cta_btn1"]}</a></li>')
    nav_menu_html = "\n        ".join(nav_links)

    # Footer navigation links
    footer_nav = []
    if "features" in planned_slots:
        footer_nav.append('<li><a href="#features">Features</a></li>')
    if any(s in planned_slots for s in ("workflow", "how-it-works", "steps")):
        footer_nav.append('<li><a href="#workflow">Workflow</a></li>')
    if "pricing" in planned_slots:
        footer_nav.append('<li><a href="#pricing">Pricing</a></li>')
    if "faq" in planned_slots:
        footer_nav.append('<li><a href="#faq">FAQ</a></li>')
    footer_nav_html = "\n            ".join(footer_nav)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{project_name} — High Performance {category.capitalize()}</title>
  <meta name="description" content="Distinctive {category} web experience engineered for performance, clarity, and visual resonance.">
  
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
        {nav_menu_html}
      </ul>
    </div>
  </header>

  <main>
{main_content_html}
  </main>

  <!-- Site Footer -->
  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-col">
          <div class="brand-logo" style="margin-bottom: var(--space-sm);">{project_name}</div>
          <p>{content["footer_desc"]}</p>
        </div>
        <div class="footer-col">
          <h3>Navigation</h3>
          <ul>
            {footer_nav_html}
          </ul>
        </div>
        <div class="footer-col">
          <h3>Legal</h3>
          <ul>
            <li><a href="#hero">Privacy Policy</a></li>
            <li><a href="#hero">Terms of Service</a></li>
            <li><a href="#hero">Cookie Settings</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h3>Status</h3>
          <ul>
            <li><a href="#hero">Systems Operational</a></li>
            <li><a href="#hero">Global Network Status</a></li>
          </ul>
        </div>
      </div>

      <div style="border-top: 1px solid var(--color-border); padding-top: var(--space-md); text-align: center;">
        <p>&copy; 2026 {project_name}. All rights reserved.</p>
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
