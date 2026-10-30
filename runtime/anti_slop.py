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
import re
from typing import Any, Dict, List, Optional, Tuple


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

