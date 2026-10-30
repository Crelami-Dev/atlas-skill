#!/usr/bin/env python3
"""Atlas Runtime Engine — Context-Aware Anti-AI-Slop Intelligence.

Detects repetitive, unmotivated, and clichéd AI-generated patterns while
explicitly honoring contextual design requirements (e.g., dashboards need
structured cards and tables; minimal sites use intentional stillness;
editorial sites use typography and whitespace).

Distinguishes:
1. Hard Failures: Broken contracts, critical accessibility violations (contrast < 3:1), broken assets.
2. Contextual Warnings: Overused AI tropes that lack contextual justification.
3. Design Rationale: Explicit reasons why a choice is valid for the brief.

Zero-dependency, Python 3.9+ standard library.
"""
import colorsys
from html.parser import HTMLParser
import re
from typing import Any, Dict, List, Optional, Set, Tuple


# -------------------------------------------------------------
# Color Normalization & Multi-Accent AST Infrastructure (P1.1)
# -------------------------------------------------------------

COLOR_VALUE_RE = re.compile(
    r"(?:#[0-9a-fA-F]{3,8}|rgba?\([^)]+\)|hsla?\([^)]+\))"
)

TAILWIND_COLOR_MAP = {
    "red": "red", "rose": "red",
    "orange": "amber", "amber": "amber",
    "yellow": "yellow",
    "green": "green", "emerald": "green", "lime": "green",
    "teal": "cyan", "cyan": "cyan", "sky": "blue",
    "blue": "blue",
    "indigo": "purple", "violet": "purple", "purple": "purple",
    "fuchsia": "pink", "pink": "pink"
}

TAILWIND_RADIUS_MAP = {
    "rounded-none": (0.0, "0px"),
    "rounded-sm": (2.0, "2px"),
    "rounded": (4.0, "4px"),
    "rounded-md": (6.0, "6px"),
    "rounded-lg": (8.0, "8px"),
    "rounded-xl": (12.0, "12px"),
    "rounded-2xl": (16.0, "16px"),
    "rounded-3xl": (24.0, "24px"),
    "rounded-full": (9999.0, "rounded-full")
}

TAILWIND_CLASS_RE = re.compile(
    r"\b(?:bg|text|fill|stroke|border)-(red|rose|orange|amber|yellow|green|emerald|lime|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink)-(?:[1-9]00|500)\b",
    re.I
)

DATAVIZ_TAGS = {"svg", "canvas", "chart", "figure"}
DATAVIZ_CLASS_RE = re.compile(
    r"\b(?:chart|dataviz|visualization|graph|map|plot|legend|recharts|apexcharts|svg-container)\b",
    re.I
)

SEMANTIC_CLASS_RE = re.compile(
    r"\b(?:status|alert|success|warning|danger|error|info|state-|is-valid|is-invalid|badge-success|badge-warning|badge-error|badge-danger|badge-info)\b",
    re.I
)

PAGE_SHELL_TAGS = {"html", "body", "main", "head"}
PAGE_SHELL_CLASS_RE = re.compile(r"\b(?:root|app|site-wrapper|page-wrapper|layout-root)\b", re.I)


def parse_color_tuple(val: str) -> Optional[Tuple[int, int, int]]:
    """Parse color string (hex, rgb, rgba, hsl, hsla) to normalized (r, g, b) integers."""
    val = val.strip().lower()
    if val.startswith("#"):
        h = val.lstrip("#")
        if len(h) == 3:
            return (int(h[0] * 2, 16), int(h[1] * 2, 16), int(h[2] * 2, 16))
        elif len(h) >= 6:
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    elif val.startswith("rgb"):
        m = re.match(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)", val)
        if m:
            return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    elif val.startswith("hsl"):
        m = re.match(r"hsla?\(\s*(\d+)\s*,\s*(\d+)%?\s*,\s*(\d+)%?", val)
        if m:
            h_norm = int(m.group(1)) / 360.0
            s_norm = int(m.group(2)) / 100.0
            l_norm = int(m.group(3)) / 100.0
            r, g, b = colorsys.hls_to_rgb(h_norm, l_norm, s_norm)
            return (int(r * 255), int(g * 255), int(b * 255))
    return None


def get_saturated_accent_family(rgb: Tuple[int, int, int]) -> Optional[str]:
    """Determine if a color is a saturated accent and return its canonical hue family name."""
    r, g, b = rgb
    h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)

    # Filter out neutrals:
    # Low saturation (< 20%) -> greys, slate, neutral, zinc
    if s < 0.20:
        return None
    # Extreme lightness (< 12% near black, > 92% near white)
    if l < 0.12 or l > 0.92:
        return None

    hue_deg = h * 360.0
    if hue_deg >= 345 or hue_deg < 15:
        return "red"
    elif 15 <= hue_deg < 55:
        return "amber"
    elif 55 <= hue_deg < 75:
        return "yellow"
    elif 75 <= hue_deg < 165:
        return "green"
    elif 165 <= hue_deg < 205:
        return "cyan"
    elif 205 <= hue_deg < 245:
        return "blue"
    elif 245 <= hue_deg < 285:
        return "purple"
    else:
        return "pink"


def parse_px_radius(val: str) -> Optional[float]:
    """Extract numeric pixel equivalent from radius string."""
    val = val.strip().lower()
    m_px = re.match(r"^([\d.]+)\s*px$", val)
    if m_px:
        return float(m_px.group(1))
    m_rem = re.match(r"^([\d.]+)\s*rem$", val)
    if m_rem:
        return float(m_rem.group(1)) * 16.0
    if val in ("0", "0px"):
        return 0.0
    return None


def normalize_radius(val: str, css_tokens: Dict[str, str]) -> Optional[Tuple[float, str]]:
    """Normalizes radius into (px_value, token_name)."""
    val = val.strip().lower()
    var_m = re.search(r"var\(\s*(--[a-zA-Z0-9_-]+)\s*\)", val)
    if var_m:
        tok = var_m.group(1)
        if tok in css_tokens:
            px = parse_px_radius(css_tokens[tok])
            if px is not None:
                return (px, tok)
        return (None, tok)
    px = parse_px_radius(val)
    if px is not None:
        for t_name, t_val in css_tokens.items():
            if parse_px_radius(t_val) == px:
                return (px, t_name)
        return (px, f"{int(px) if px.is_integer() else px}px")
    if val in ("50%", "9999px", "999px"):
        return (9999.0, "rounded-full")
    return None


class ASTElement:
    """Lightweight DOM tree node for container-scoped aesthetic analysis."""
    def __init__(self, tag: str, attrs: List[Tuple[str, Optional[str]]], parent: Optional['ASTElement']):
        self.tag = tag.lower()
        self.attrs = {k.lower(): (v or "") for k, v in attrs}
        self.parent = parent
        self.children: List['ASTElement'] = []
        self.accent_families: Set[str] = set()
        self.role_family: Optional[str] = None
        self.radius: Optional[Tuple[float, str]] = None

    def get_role_family(self) -> Optional[str]:
        """Identifies peer component family: 'card', 'control', 'badge-or-avatar', or None."""
        cls = self.attrs.get("class", "")
        # Form controls & buttons take precedence over shape-based classes
        if self.tag in ("input", "button", "select", "textarea"):
            return "control"
        if re.search(r"\b(?:btn|button|form-control|input-field|select-input)\b", cls, re.I):
            return "control"
        # Pills, badges, circular icons, avatars
        if re.search(r"\b(?:avatar|icon-wrap|icon-box|status-dot|pill|badge|chip)\b", cls, re.I):
            return "badge-or-avatar"
        if "rounded-full" in cls.lower():
            return "badge-or-avatar"
        # Cards
        if re.search(r"\b(?:card|tile|metric-card|feature-card|pricing-card|panel|summary-card)\b", cls, re.I):
            return "card"
        return None

    def extract_radius(self, css_tokens: Dict[str, str], css_class_radii: Dict[str, Tuple[float, str]]) -> Optional[Tuple[float, str]]:
        """Extracts and normalizes border-radius into (px_value, token_name)."""
        # 1. Inline style
        style = self.attrs.get("style", "")
        if style:
            m = re.search(r"border-radius\s*:\s*([^;\"'>]+)", style, re.I)
            if m:
                rad = normalize_radius(m.group(1), css_tokens)
                if rad:
                    return rad
        # 2. Tailwind class
        classes = self.attrs.get("class", "").split()
        for c in classes:
            c_lower = c.lower()
            if c_lower in TAILWIND_RADIUS_MAP:
                return TAILWIND_RADIUS_MAP[c_lower]
        # 3. CSS class rule
        for c in classes:
            if c in css_class_radii:
                return css_class_radii[c]
        return None

    def is_dataviz(self) -> bool:
        if self.tag in DATAVIZ_TAGS:
            return True
        cls = self.attrs.get("class", "")
        role = self.attrs.get("role", "")
        aria = self.attrs.get("aria-label", "")
        if DATAVIZ_CLASS_RE.search(cls) or role in ("img", "graphics-document") or "chart" in aria.lower():
            return True
        if self.parent and self.parent.is_dataviz():
            return True
        return False

    def is_semantic_status(self) -> bool:
        cls = self.attrs.get("class", "")
        role = self.attrs.get("role", "")
        if SEMANTIC_CLASS_RE.search(cls) or role == "alert" or "data-status" in self.attrs:
            return True
        if self.parent and (SEMANTIC_CLASS_RE.search(self.parent.attrs.get("class", "")) or self.parent.attrs.get("role") == "alert"):
            return True
        return False

    def is_page_shell(self) -> bool:
        if self.tag in PAGE_SHELL_TAGS:
            return True
        cls = self.attrs.get("class", "")
        elem_id = self.attrs.get("id", "")
        if elem_id in ("root", "app") or PAGE_SHELL_CLASS_RE.search(cls):
            return True
        return False

    def is_container_boundary(self) -> bool:
        """Determines if this node represents an independent component or container."""
        if self.is_page_shell():
            return False
        if self.tag in ("section", "article", "header", "footer", "nav", "aside", "form", "table"):
            return True
        cls = self.attrs.get("class", "")
        if re.search(r"\b(?:card|cards|grid|metrics|panel|bento|features|toolbar|badge-group|tile|list|group)\b", cls, re.I):
            return True
        return len(self.children) >= 2


class DOMTreeBuilder(HTMLParser):
    """Zero-dependency HTML Parser producing an AST for container auditing."""
    VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = ASTElement("#root", [], None)
        self.cur = self.root
        self.all_nodes: List[ASTElement] = []

    def handle_starttag(self, tag, attrs):
        node = ASTElement(tag, attrs, self.cur)
        self.cur.children.append(node)
        self.all_nodes.append(node)
        if tag.lower() not in self.VOID_TAGS:
            self.cur = node

    def handle_endtag(self, tag):
        if tag.lower() in self.VOID_TAGS:
            return
        n = self.cur
        while n and n.tag != tag.lower():
            n = n.parent
        if n and n.parent:
            self.cur = n.parent


def find_multi_accent_containers(html: str, css: str) -> List[Tuple[str, List[str]]]:
    """Finds containers that exhibit suspicious multi-accent saturation (>= 3 families)."""
    # 1. Parse CSS class rules for color declarations
    css_class_colors: Dict[str, Set[str]] = {}
    for m in re.finditer(r"\.([a-zA-Z0-9_-]+)\s*\{([^}]+)\}", css):
        cls_name = m.group(1)
        body = m.group(2)
        for cm in re.finditer(r"(?:color|background(?:-color)?|fill|stroke)\s*:\s*([^;]+)", body):
            val = cm.group(1).strip()
            for c_val in COLOR_VALUE_RE.findall(val):
                rgb = parse_color_tuple(c_val)
                if rgb:
                    family = get_saturated_accent_family(rgb)
                    if family:
                        css_class_colors.setdefault(cls_name, set()).add(family)

    # 2. Build DOM AST
    parser = DOMTreeBuilder()
    try:
        parser.feed(html)
    except Exception:
        return []

    # 3. Associate accents with non-exempt leaf nodes
    for node in parser.all_nodes:
        if node.is_dataviz() or node.is_semantic_status():
            continue

        style = node.attrs.get("style", "")
        if style:
            for cm in re.finditer(r"(?:color|background(?:-color)?|fill|stroke)\s*:\s*([^;\"'>]+)", style):
                for c_val in COLOR_VALUE_RE.findall(cm.group(1)):
                    rgb = parse_color_tuple(c_val)
                    if rgb:
                        fam = get_saturated_accent_family(rgb)
                        if fam:
                            node.accent_families.add(fam)

        classes = node.attrs.get("class", "").split()
        for cls in classes:
            cls_lower = cls.lower()
            tm = TAILWIND_CLASS_RE.match(cls_lower)
            if tm:
                fam = TAILWIND_COLOR_MAP.get(tm.group(1).lower())
                if fam:
                    node.accent_families.add(fam)
            if cls in css_class_colors:
                node.accent_families.update(css_class_colors[cls])

    # 4. Evaluate container boundaries
    flagged_candidates: List[Tuple[ASTElement, str, List[str]]] = []

    for node in parser.all_nodes:
        if not node.is_container_boundary():
            continue

        has_child_sections = any(c.tag in ("section", "article") for c in node.children)
        container_accents: Set[str] = set()

        def collect_accents(n: ASTElement):
            container_accents.update(n.accent_families)
            for ch in n.children:
                if has_child_sections and ch.tag in ("section", "article"):
                    continue
                collect_accents(ch)

        collect_accents(node)

        if len(container_accents) >= 3:
            cls_desc = f" class='{node.attrs.get('class')}'" if node.attrs.get("class") else ""
            desc = f"<{node.tag}{cls_desc}>"
            flagged_candidates.append((node, desc, sorted(container_accents)))

    # Deduplicate: if a child container already captured this multi-accent issue, prefer the inner container
    final_violations: List[Tuple[str, List[str]]] = []
    for node, desc, families in flagged_candidates:
        has_flagged_descendant = False
        for other_node, _, _ in flagged_candidates:
            if other_node is not node:
                curr = other_node.parent
                while curr:
                    if curr is node:
                        has_flagged_descendant = True
                        break
                    curr = curr.parent
            if has_flagged_descendant:
                break

        if not has_flagged_descendant:
            final_violations.append((desc, families))

    return final_violations


def find_inconsistent_radius_containers(html: str, css: str) -> List[Tuple[str, str, List[str], str]]:
    """Identifies containers where peer components (cards or controls) have materially inconsistent radii."""
    # 1. Parse CSS tokens (--radius-*)
    css_tokens: Dict[str, str] = {}
    for m in re.finditer(r"(--radius-[a-zA-Z0-9_-]+)\s*:\s*([^;]+);", css, re.I):
        css_tokens[m.group(1).lower()] = m.group(2).strip()

    # 2. Parse CSS class rules for border-radius
    css_class_radii: Dict[str, Tuple[float, str]] = {}
    for m in re.finditer(r"\.([a-zA-Z0-9_-]+)\s*\{([^}]+)\}", css):
        cls_name = m.group(1)
        body = m.group(2)
        rm = re.search(r"border-radius\s*:\s*([^;]+)", body, re.I)
        if rm:
            rad = normalize_radius(rm.group(1), css_tokens)
            if rad:
                css_class_radii[cls_name] = rad

    # 3. Build AST
    parser = DOMTreeBuilder()
    try:
        parser.feed(html)
    except Exception:
        return []

    # 4. Attach role_family and radius to nodes
    for node in parser.all_nodes:
        node.role_family = node.get_role_family()
        node.radius = node.extract_radius(css_tokens, css_class_radii)

    # 5. Check container boundaries
    flagged_candidates: List[Tuple[ASTElement, str, str, List[str], str]] = []

    for node in parser.all_nodes:
        if not node.is_container_boundary():
            continue

        has_child_sections = any(c.tag in ("section", "article") for c in node.children)
        scoped_nodes: List[ASTElement] = []

        def collect_scoped(n: ASTElement):
            scoped_nodes.append(n)
            for ch in n.children:
                if has_child_sections and ch.tag in ("section", "article"):
                    continue
                collect_scoped(ch)

        collect_scoped(node)

        # Check peer cards
        cards = [n for n in scoped_nodes if n.role_family == "card" and n.radius is not None and n.radius[0] < 999.0]
        if len(cards) >= 2:
            card_radii = {n.radius[1]: n.radius[0] for n in cards if n.radius[0] is not None}
            if len(card_radii) >= 2:
                values = list(card_radii.values())
                min_r, max_r = min(values), max(values)
                # Material difference: delta >= 4px and ratio >= 1.5
                if (max_r - min_r >= 4.0) and (min_r > 0 and (max_r / min_r >= 1.5) or min_r == 0):
                    cls_desc = f" class='{node.attrs.get('class')}'" if node.attrs.get("class") else ""
                    desc = f"<{node.tag}{cls_desc}>"
                    token_names = sorted(card_radii.keys())
                    rec = next((t for t in token_names if t.startswith("--")), token_names[0])
                    flagged_candidates.append((node, desc, "cards", token_names, rec))
                    continue

        # Check peer controls
        controls = [n for n in scoped_nodes if n.role_family == "control" and n.radius is not None]
        if len(controls) >= 2:
            has_pill = any(n.radius[0] >= 999.0 for n in controls)
            has_rect = any(n.radius[0] < 999.0 for n in controls)
            if has_pill and has_rect:
                cls_desc = f" class='{node.attrs.get('class')}'" if node.attrs.get("class") else ""
                desc = f"<{node.tag}{cls_desc}>"
                token_names = sorted(set(n.radius[1] for n in controls))
                rec = next((t for t in token_names if t.startswith("--")), "var(--radius-sm)")
                flagged_candidates.append((node, desc, "controls", token_names, rec))
                continue
            rect_controls = [n for n in controls if n.radius[0] < 999.0 and n.radius[0] is not None]
            if len(rect_controls) >= 2:
                ctrl_radii = {n.radius[1]: n.radius[0] for n in rect_controls}
                if len(ctrl_radii) >= 2:
                    values = list(ctrl_radii.values())
                    min_r, max_r = min(values), max(values)
                    if (max_r - min_r >= 4.0) and (min_r > 0 and (max_r / min_r >= 1.5) or min_r == 0):
                        cls_desc = f" class='{node.attrs.get('class')}'" if node.attrs.get("class") else ""
                        desc = f"<{node.tag}{cls_desc}>"
                        token_names = sorted(ctrl_radii.keys())
                        rec = next((t for t in token_names if t.startswith("--")), token_names[0])
                        flagged_candidates.append((node, desc, "controls", token_names, rec))

    # Deduplicate: if a child container was flagged, suppress parent
    final_violations: List[Tuple[str, str, List[str], str]] = []
    for node, desc, role, token_names, rec in flagged_candidates:
        has_flagged_descendant = False
        for other_node, _, _, _, _ in flagged_candidates:
            if other_node is not node:
                curr = other_node.parent
                while curr:
                    if curr is node:
                        has_flagged_descendant = True
                        break
                    curr = curr.parent
            if has_flagged_descendant:
                break
        if not has_flagged_descendant:
            final_violations.append((desc, role, token_names, rec))

    return final_violations


class AntiSlopFinding:
    """Represents a single audit finding."""
    def __init__(
        self,
        rule_id: str,
        severity: str,  # "FAIL", "WARN", "INFO"
        message: str,
        fix: str,
        context_rationale: Optional[str] = None
    ):
        self.rule_id = rule_id
        self.severity = severity
        self.message = message
        self.fix = fix
        self.context_rationale = context_rationale

    def to_dict(self) -> Dict[str, Any]:
        out = {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "message": self.message,
            "fix": self.fix
        }
        if self.context_rationale:
            out["context_rationale"] = self.context_rationale
        return out


def audit_website_content(
    html: str,
    css: str,
    brief: Optional[Any] = None,
    allow_rules: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Perform context-aware design and anti-slop audit on generated HTML/CSS.
    
    Args:
        html: Raw HTML string of the generated website.
        css: Raw CSS string of the generated website.
        brief: Optional ProductBrief object providing context.
        allow_rules: Optional list of rule IDs to bypass.
        
    Returns:
        Dict with overall status ('PASS', 'WARN', 'FAIL'), score, and structured findings.
    """
    allow = set(allow_rules or [])
    findings: List[AntiSlopFinding] = []

    page_type = getattr(brief, "page_type", "marketing") if brief else "marketing"
    category = getattr(brief, "category", "general") if brief else "general"
    density = getattr(brief, "density", "med") if brief else "med"
    tones = set(getattr(brief, "tones", [])) if brief else set()

    # -------------------------------------------------------------
    # 1. HARD FAILURES: Critical Functionality & Accessibility
    # -------------------------------------------------------------

    # Missing viewport meta
    if "name=\"viewport\"" not in html and "name='viewport'" not in html:
        findings.append(AntiSlopFinding(
            rule_id="missing-viewport",
            severity="FAIL",
            message="HTML document lacks responsive viewport meta tag.",
            fix="Add <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"> to <head>."
        ))

    # Empty headline
    if re.search(r"<h1[^>]*>\s*</h1>", html, re.IGNORECASE):
        findings.append(AntiSlopFinding(
            rule_id="empty-h1",
            severity="FAIL",
            message="H1 element is empty.",
            fix="Provide a meaningful, concise headline (max 2 lines)."
        ))

    # Unescaped raw template placeholders
    placeholder_matches = re.findall(r"\{\{[^}]+\}\}|\[photo \| [^\]]+\]", html)
    if placeholder_matches:
        findings.append(AntiSlopFinding(
            rule_id="unresolved-placeholder",
            severity="FAIL",
            message=f"Found {len(placeholder_matches)} unresolved placeholder(s): {placeholder_matches[:3]}",
            fix="Resolve all template variables before generating output."
        ))

    # Extremely low contrast or missing ink variables
    if "--ink: #ffffff" in css and "--bg: #ffffff" in css:
        findings.append(AntiSlopFinding(
            rule_id="contrast-zero",
            severity="FAIL",
            message="Foreground ink color is identical to background color (#ffffff on #ffffff).",
            fix="Ensure high contrast ratio (at least 4.5:1 for body copy)."
        ))

    # -------------------------------------------------------------
    # 2. CONTEXTUAL ANTI-SLOP RULES: Evaluated With Context
    # -------------------------------------------------------------

    # Rule: AI Cliché Gradient Text (linear-gradient text-fill clip)
    has_gradient_text = bool(
        re.search(r"-webkit-background-clip:\s*text", css, re.IGNORECASE) or
        re.search(r"background-clip:\s*text", css, re.IGNORECASE)
    )
    if has_gradient_text and "gradient-text" not in allow:
        # Contextual check: Is it an experimental or futuristic AI brief where gradient is explicitly requested?
        if "futuristic" in tones or "experimental" in tones:
            findings.append(AntiSlopFinding(
                rule_id="gradient-text",
                severity="INFO",
                message="Gradient text detected, accepted under 'futuristic'/'experimental' brief tone.",
                fix="Ensure text remains legible across all display devices.",
                context_rationale="Explicitly permitted by brief tone 'futuristic'."
            ))
        else:
            findings.append(AntiSlopFinding(
                rule_id="gradient-text",
                severity="WARN",
                message="Gradient-filled text detected. Clichéd AI landing page signature.",
                fix="Use solid, high-contrast ink color for headings.",
                context_rationale="Headlines with solid color achieve superior clarity and timelessness."
            ))

    # Rule: Neon AI-Purple Cliché (#7c3aed, #8b5cf6, #6366f1)
    has_ai_purple = bool(re.search(r"#7c3aed|#8b5cf6|#6366f1|hsl\(260|rgb\(124,\s*58,\s*237\)", css, re.IGNORECASE))
    if has_ai_purple and "ai-purple" not in allow:
        if "ai-product" in category or "cyberpunk" in tones:
            findings.append(AntiSlopFinding(
                rule_id="palette-ai-purple",
                severity="INFO",
                message="Violet/purple accent present; justified by AI product / cyberpunk brief category.",
                fix="Consider distinct brand accents from the library if differentiation is desired.",
                context_rationale="Contextually justified for tech/AI products."
            ))
        else:
            findings.append(AntiSlopFinding(
                rule_id="palette-ai-purple",
                severity="WARN",
                message="Default AI-assistant violet/indigo hue detected without specific brief requirement.",
                fix="Select a distinctive palette from the canonical library.",
                context_rationale="Avoid default assistant branding tropes."
            ))

    # Rule: Card Spam (excessive identical cards with small icons)
    card_count = len(re.findall(r"class=[\"'][^\"']*\b(?:card|feature-card|tile)\b[^\"']*[\"']", html, re.IGNORECASE))
    if card_count >= 8 and "card-spam" not in allow:
        if page_type == "app" or density == "high" or category in {"dashboard", "saas", "fintech"}:
            findings.append(AntiSlopFinding(
                rule_id="card-density",
                severity="INFO",
                message=f"High card density ({card_count} cards) accepted for {page_type}/dashboard operational interface.",
                fix="Maintain clear visual grouping and distinct hierarchy among card tiers.",
                context_rationale="Operational applications and data dashboards legitimately require structured card containers."
            ))
        else:
            findings.append(AntiSlopFinding(
                rule_id="card-spam",
                severity="WARN",
                message=f"Found {card_count} repetitive card components. Over-reliance on boxed cards creates monotonous layout.",
                fix="Vary composition using narrative splits, typography lists, or asymmetric bento grids.",
                context_rationale="Marketing and editorial pages benefit from diverse layout rhythms rather than endless card grids."
            ))

    # Rule: Buzzword Overload in Copy
    buzzwords = ["supercharge", "unleash", "elevate your", "cutting-edge", "game-changer", "next-gen", "all-in-one platform"]
    found_buzzwords = [bw for bw in buzzwords if bw in html.lower()]
    if found_buzzwords and "buzzwords" not in allow:
        findings.append(AntiSlopFinding(
            rule_id="copy-buzzwords",
            severity="WARN",
            message=f"AI-generated marketing buzzwords found: {found_buzzwords}",
            fix="State the concrete capability or product outcome using plain, honest language.",
            context_rationale="Substantive claims build greater trust than generic buzzword superlatives."
        ))

    # Rule: Emoji as Bullets or UI Icons
    emoji_matches = re.findall(r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F900-\U0001F9FF\U0001FA70-\U0001FAFF]", html)
    if emoji_matches and "emoji" not in allow:
        if "playful" in tones or "casual" in tones:
            findings.append(AntiSlopFinding(
                rule_id="emoji-usage",
                severity="INFO",
                message=f"Emoji present ({len(emoji_matches)}), permitted by playful/casual brief tone.",
                fix="Ensure screen readers have appropriate aria-label if emoji convey information.",
                context_rationale="Permitted for playful/casual tones."
            ))
        else:
            findings.append(AntiSlopFinding(
                rule_id="emoji-usage",
                severity="WARN",
                message=f"Found {len(emoji_matches)} emoji used in UI/copy: {emoji_matches[:4]}",
                fix="Replace emoji with precise words or authentic SVG iconography.",
                context_rationale="Professional interfaces communicate more effectively without decorative emoji bullets."
            ))

    # Rule: Monospace everywhere outside code
    has_mono_everywhere = "font-family: monospace" in css and "<code" not in html and "<pre" not in html
    if has_mono_everywhere and "mono" not in allow:
        if "technical" in tones or "developer" in category:
            findings.append(AntiSlopFinding(
                rule_id="mono-usage",
                severity="INFO",
                message="Monospace font used across interface; contextually justified for technical/developer audience.",
                fix="Ensure body text line length and spacing remain comfortable for extended reading.",
                context_rationale="Technical and developer tools legitimately use monospace typography."
            ))
        else:
            findings.append(AntiSlopFinding(
                rule_id="mono-usage",
                severity="WARN",
                message="Monospace font used as primary body voice without code/developer context.",
                fix="Reserve monospace for literal code and data tables; use clean proportional type for prose.",
                context_rationale="Proportional fonts provide significantly better reading ergonomics."
            ))

    # Rule: Suspicious Multi-Accent Saturation in a Single Container (P1.1)
    if "multi-accent-container" not in allow and "multi-accent" not in allow:
        multi_accent_violations = find_multi_accent_containers(html, css)
        if multi_accent_violations:
            is_playful_or_colorful = bool(
                "playful" in tones or "colorful" in tones or "rainbow" in tones or
                "multi-accent" in tones or "multi-accent" in category or "creative" in tones
            )
            for container_desc, families in multi_accent_violations:
                families_str = ", ".join(families)
                if is_playful_or_colorful:
                    findings.append(AntiSlopFinding(
                        rule_id="multi-accent-container",
                        severity="INFO",
                        message=f"Multi-accent saturation ({len(families)} families: {families_str}) in {container_desc}; contextually permitted by brief tone/category.",
                        fix="Ensure color contrasts remain accessible and intentional.",
                        context_rationale="Playful or creative briefs contextually utilize diverse accent palettes."
                    ))
                else:
                    findings.append(AntiSlopFinding(
                        rule_id="multi-accent-container",
                        severity="WARN",
                        message=f"Suspicious multi-accent saturation detected in {container_desc}: found {len(families)} distinct saturated accent color families ({families_str}).",
                        fix="Limit container to one dominant brand accent. Reserve secondary saturated hues strictly for semantic status signals (success, warning, error).",
                        context_rationale="Restricting accent colors reinforces visual hierarchy and avoids the AI-generated 'rainbow card' template aesthetic."
                    ))

    # Rule: Context-Aware Corner Radius Inconsistency (P1.2)
    if "inconsistent-radius" not in allow and "radius" not in allow:
        radius_violations = find_inconsistent_radius_containers(html, css)
        if radius_violations:
            is_asymmetric_or_eclectic = bool(
                "asymmetric" in tones or "eclectic" in tones or "experimental" in tones
            )
            for container_desc, role_family, radii_list, fix_rec in radius_violations:
                radii_str = ", ".join(radii_list)
                if is_asymmetric_or_eclectic:
                    findings.append(AntiSlopFinding(
                        rule_id="inconsistent-radius",
                        severity="INFO",
                        message=f"Variable corner radius ({radii_str}) among peer {role_family} in {container_desc}; contextually permitted by asymmetric/eclectic brief tone.",
                        fix="Ensure variation serves deliberate visual hierarchy.",
                        context_rationale="Asymmetric or experimental briefs contextually utilize diverse geometric radii."
                    ))
                else:
                    findings.append(AntiSlopFinding(
                        rule_id="inconsistent-radius",
                        severity="WARN",
                        message=f"Inconsistent corner radius detected among peer {role_family} in {container_desc}: found conflicting radii ({radii_str}).",
                        fix=f"Align peer {role_family} to use a unified design token (e.g. {fix_rec}).",
                        context_rationale=f"Peer components of the same family ({role_family}) within a coherent container should share a consistent corner-radius token to maintain structural visual rhythm."
                    ))

    # -------------------------------------------------------------
    # 3. Overall Verdict Determination
    # -------------------------------------------------------------
    has_fail = any(f.severity == "FAIL" for f in findings)
    has_warn = any(f.severity == "WARN" for f in findings)

    status = "FAIL" if has_fail else ("WARN" if has_warn else "PASS")

    # Score out of 100
    score = 100
    for f in findings:
        if f.severity == "FAIL":
            score -= 30
        elif f.severity == "WARN":
            score -= 10
    score = max(0, score)

    return {
        "status": status,
        "score": score,
        "total_findings": len(findings),
        "failures_count": sum(1 for f in findings if f.severity == "FAIL"),
        "warnings_count": sum(1 for f in findings if f.severity == "WARN"),
        "info_count": sum(1 for f in findings if f.severity == "INFO"),
        "findings": [f.to_dict() for f in findings]
    }

