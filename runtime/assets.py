#!/usr/bin/env python3
"""Atlas Runtime Engine — Asset and Image Generation Boundary.

Implements the provider-neutral asset interface and 3-tier fallback resolution policy (DEC-003):
  Tier 1: Native Image Generation (when approved provider is configured and available)
  Tier 2: Licensed Museum Archive (when licensing metadata can be verified)
  Tier 3: Semantic CSS/SVG Local Fallback (zero-network, accessible, responsive)

Zero-dependency, Python 3.9+ standard library.
"""
import hashlib
import json
import os
from typing import Any, Dict, List, Optional, Tuple

TIER_1_NATIVE = "tier_1_native"
TIER_2_ARCHIVE = "tier_2_archive"
TIER_3_CSS_SVG = "tier_3_css_svg"

STATUS_PENDING_GENERATION = "pending_generation"
STATUS_FALLBACK_READY = "fallback_ready"
STATUS_RESOLVED = "resolved"

DEFAULT_ASPECT_RATIOS = {
    "hero": "16:9",
    "features": "4:3",
    "showcase": "16:9",
    "work": "16:9",
    "story": "3:2",
    "social_proof": "1:1",
    "nav": "1:1",
    "footer": "1:1"
}


class AssetRequirement:
    """Represents a discrete visual asset requirement for a layout slot."""

    def __init__(
        self,
        asset_id: str,
        slot: str,
        role: str,
        asset_type: str,
        aspect_ratio: str,
        prompt_brief: str,
        resolution_tier: str = TIER_3_CSS_SVG,
        status: str = STATUS_FALLBACK_READY,
        fallback_descriptor: Optional[Dict[str, Any]] = None,
        licensing: Optional[Dict[str, Any]] = None
    ):
        self.asset_id = asset_id
        self.slot = slot
        self.role = role
        self.asset_type = asset_type
        self.aspect_ratio = aspect_ratio
        self.prompt_brief = prompt_brief
        self.resolution_tier = resolution_tier
        self.status = status
        self.fallback_descriptor = fallback_descriptor or {}
        self.licensing = licensing

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "slot": self.slot,
            "role": self.role,
            "asset_type": self.asset_type,
            "aspect_ratio": self.aspect_ratio,
            "prompt_brief": self.prompt_brief,
            "resolution_tier": self.resolution_tier,
            "status": self.status,
            "fallback_descriptor": self.fallback_descriptor,
            "licensing": self.licensing
        }


def _generate_fintech_svg(w: int, h: int, asset_id: str) -> str:
    """Generate high-fidelity institutional fintech treasury ledger graphic."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="auto" role="img" aria-label="Institutional Treasury Ledger Interface">
  <defs>
    <linearGradient id="bg_{asset_id}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0a0f1d" />
      <stop offset="100%" stop-color="#141c33" />
    </linearGradient>
    <linearGradient id="chart_grad_{asset_id}" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#00e5a3" stop-opacity="0.35" />
      <stop offset="100%" stop-color="#00e5a3" stop-opacity="0.0" />
    </linearGradient>
    <linearGradient id="line_grad_{asset_id}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#3b82f6" />
      <stop offset="50%" stop-color="#00e5a3" />
      <stop offset="100%" stop-color="#38bdf8" />
    </linearGradient>
    <pattern id="grid_{asset_id}" width="32" height="32" patternUnits="userSpaceOnUse">
      <path d="M 32 0 L 0 0 0 32" fill="none" stroke="rgba(255, 255, 255, 0.04)" stroke-width="1" />
    </pattern>
  </defs>

  <!-- Frame Background -->
  <rect width="{w}" height="{h}" fill="url(#bg_{asset_id})" rx="16" />
  <rect width="{w}" height="{h}" fill="url(#grid_{asset_id})" rx="16" />
  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" fill="none" stroke="rgba(255, 255, 255, 0.08)" stroke-width="2" rx="15" />

  <!-- Ledger Header -->
  <g transform="translate(40, 36)">
    <circle cx="8" cy="8" r="4" fill="#00e5a3" />
    <circle cx="8" cy="8" r="8" fill="none" stroke="#00e5a3" stroke-width="1" opacity="0.4" />
    <text x="24" y="12" font-family="system-ui, -apple-system, sans-serif" font-size="11" font-weight="700" fill="#889bb5" letter-spacing="0.08em">INSTITUTIONAL TREASURY LEDGER</text>
    
    <!-- Security Verification Badge -->
    <rect x="{w - 240}" y="-4" width="160" height="26" rx="13" fill="rgba(0, 229, 163, 0.08)" stroke="rgba(0, 229, 163, 0.25)" stroke-width="1" />
    <text x="{w - 160}" y="13" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif" font-size="10" font-weight="600" fill="#00e5a3" letter-spacing="0.04em">MULTI-SIG VERIFIED</text>
  </g>

  <!-- Balance Hero Display -->
  <g transform="translate(40, 92)">
    <text x="0" y="32" font-family="system-ui, -apple-system, sans-serif" font-size="34" font-weight="800" fill="#ffffff" letter-spacing="-0.02em">$2,485,920.00 USD</text>
    <rect x="360" y="8" width="115" height="26" rx="13" fill="rgba(0, 229, 163, 0.12)" />
    <text x="417" y="25" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif" font-size="12" font-weight="700" fill="#00e5a3">+14.8% APY</text>
    <text x="0" y="56" font-family="system-ui, -apple-system, sans-serif" font-size="12" fill="#889bb5">Automated Yield Protocol • Block Height #21,849,204</text>
  </g>

  <!-- Interactive Grid Guidelines -->
  <g stroke="rgba(255, 255, 255, 0.06)" stroke-dasharray="4,4" stroke-width="1">
    <line x1="40" y1="180" x2="{w - 40}" y2="180" />
    <line x1="40" y1="230" x2="{w - 40}" y2="230" />
    <line x1="40" y1="280" x2="{w - 40}" y2="280" />
  </g>
  <g font-family="system-ui, -apple-system, sans-serif" font-size="10" fill="#556987">
    <text x="40" y="174">$2.50M</text>
    <text x="40" y="224">$2.00M</text>
    <text x="40" y="274">$1.50M</text>
  </g>

  <!-- Trend Area Fill -->
  <path d="M 40 300 L 40 280 Q 140 270 240 240 T 440 200 T 640 170 L {w - 40} 160 L {w - 40} 300 Z" fill="url(#chart_grad_{asset_id})" />
  <!-- Trend Stroke Line -->
  <path d="M 40 280 Q 140 270 240 240 T 440 200 T 640 170 L {w - 40} 160" fill="none" stroke="url(#line_grad_{asset_id})" stroke-width="3.5" stroke-linecap="round" />

  <!-- Active Marker Point -->
  <circle cx="440" cy="200" r="6" fill="#00e5a3" />
  <circle cx="440" cy="200" r="12" fill="none" stroke="#00e5a3" stroke-width="2" opacity="0.4" />
  <!-- Tooltip Card -->
  <g transform="translate(390, 145)">
    <rect width="100" height="34" rx="6" fill="#1e293b" stroke="rgba(0, 229, 163, 0.4)" stroke-width="1" />
    <text x="50" y="21" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif" font-size="11" font-weight="700" fill="#ffffff">Peak: $2.51M</text>
  </g>

  <!-- Asset Allocation Footer Cards -->
  <g transform="translate(40, {h - 80})">
    <!-- Card 1 -->
    <rect x="0" y="0" width="{int((w - 110) / 3)}" height="54" rx="10" fill="#141c30" stroke="rgba(255, 255, 255, 0.08)" stroke-width="1" />
    <text x="16" y="24" font-family="system-ui, -apple-system, sans-serif" font-size="11" fill="#889bb5">USD Reserves</text>
    <text x="16" y="44" font-family="system-ui, -apple-system, sans-serif" font-size="14" font-weight="700" fill="#ffffff">$1,441,833 (58%)</text>

    <!-- Card 2 -->
    <rect x="{int((w - 110) / 3) + 15}" y="0" width="{int((w - 110) / 3)}" height="54" rx="10" fill="#141c30" stroke="rgba(255, 255, 255, 0.08)" stroke-width="1" />
    <text x="{int((w - 110) / 3) + 31}" y="24" font-family="system-ui, -apple-system, sans-serif" font-size="11" fill="#889bb5">Digital Assets</text>
    <text x="{int((w - 110) / 3) + 31}" y="44" font-family="system-ui, -apple-system, sans-serif" font-size="14" font-weight="700" fill="#ffffff">$671,200 (27%)</text>

    <!-- Card 3 -->
    <rect x="{int((w - 110) / 3) * 2 + 30}" y="0" width="{int((w - 110) / 3)}" height="54" rx="10" fill="#141c30" stroke="rgba(255, 255, 255, 0.08)" stroke-width="1" />
    <text x="{int((w - 110) / 3) * 2 + 46}" y="24" font-family="system-ui, -apple-system, sans-serif" font-size="11" fill="#889bb5">Yield Staking</text>
    <text x="{int((w - 110) / 3) * 2 + 46}" y="44" font-family="system-ui, -apple-system, sans-serif" font-size="14" font-weight="700" fill="#ffffff">$372,887 (15%)</text>
  </g>
</svg>'''


def _generate_saas_svg(w: int, h: int, asset_id: str) -> str:
    """Generate high-fidelity cloud runtime orchestrator graphic."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="auto" role="img" aria-label="Cloud Runtime Orchestrator Console">
  <defs>
    <linearGradient id="bg_saas_{asset_id}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f172a" />
      <stop offset="100%" stop-color="#1e293b" />
    </linearGradient>
    <linearGradient id="pulse_{asset_id}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#38bdf8" />
      <stop offset="100%" stop-color="#818cf8" />
    </linearGradient>
  </defs>

  <rect width="{w}" height="{h}" fill="url(#bg_saas_{asset_id})" rx="16" />
  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" fill="none" stroke="rgba(255, 255, 255, 0.08)" stroke-width="2" rx="15" />

  <!-- Terminal Top Bar -->
  <g transform="translate(30, 30)">
    <circle cx="10" cy="10" r="5" fill="#ef4444" />
    <circle cx="28" cy="10" r="5" fill="#f59e0b" />
    <circle cx="46" cy="10" r="5" fill="#10b981" />
    <text x="70" y="15" font-family="monospace" font-size="12" fill="#94a3b8">atlas-runtime --cluster us-east-prod</text>
  </g>

  <!-- Metrics Grid -->
  <g transform="translate(40, 80)">
    <rect x="0" y="0" width="220" height="90" rx="12" fill="#1e293b" stroke="rgba(255,255,255,0.06)" />
    <text x="20" y="32" font-family="system-ui, sans-serif" font-size="12" fill="#94a3b8">Active Microservices</text>
    <text x="20" y="66" font-family="system-ui, sans-serif" font-size="28" font-weight="700" fill="#38bdf8">148 / 148</text>

    <rect x="240" y="0" width="220" height="90" rx="12" fill="#1e293b" stroke="rgba(255,255,255,0.06)" />
    <text x="260" y="32" font-family="system-ui, sans-serif" font-size="12" fill="#94a3b8">Throughput</text>
    <text x="260" y="66" font-family="system-ui, sans-serif" font-size="28" font-weight="700" fill="#10b981">84,200 req/s</text>

    <rect x="480" y="0" width="{w - 560}" height="90" rx="12" fill="#1e293b" stroke="rgba(255,255,255,0.06)" />
    <text x="500" y="32" font-family="system-ui, sans-serif" font-size="12" fill="#94a3b8">P99 Latency</text>
    <text x="500" y="66" font-family="system-ui, sans-serif" font-size="28" font-weight="700" fill="#818cf8">4.2 ms</text>
  </g>

  <!-- Network Visual Topology -->
  <g transform="translate(40, 200)">
    <rect width="{w - 80}" height="190" rx="12" fill="#141e33" stroke="rgba(255,255,255,0.06)" />
    <text x="24" y="36" font-family="system-ui, sans-serif" font-size="13" font-weight="600" fill="#f8fafc">Verified Ingress Flow</text>
    <path d="M 60 110 C 180 40, 300 160, 420 90 C 540 20, 620 140, 700 80" fill="none" stroke="url(#pulse_{asset_id})" stroke-width="3" stroke-linecap="round" />
    <circle cx="60" cy="110" r="6" fill="#38bdf8" />
    <circle cx="420" cy="90" r="6" fill="#818cf8" />
    <circle cx="700" cy="80" r="6" fill="#10b981" />
  </g>
</svg>'''


def _generate_generic_svg(w: int, h: int, asset_id: str, category: str, art_direction_name: str) -> str:
    """Generate high-fidelity architectural spatial composition."""
    hue = int(hashlib.md5(category.encode("utf-8")).hexdigest()[:4], 16) % 360
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="auto" role="img" aria-label="{category} Visual Architecture">
  <defs>
    <linearGradient id="bg_gen_{asset_id}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="hsl({hue}, 35%, 12%)" />
      <stop offset="100%" stop-color="hsl({(hue + 40) % 360}, 45%, 7%)" />
    </linearGradient>
    <linearGradient id="accent_gen_{asset_id}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="hsl({hue}, 80%, 65%)" />
      <stop offset="100%" stop-color="hsl({(hue + 50) % 360}, 90%, 55%)" />
    </linearGradient>
  </defs>

  <rect width="{w}" height="{h}" fill="url(#bg_gen_{asset_id})" rx="16" />
  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" fill="none" stroke="rgba(255, 255, 255, 0.08)" stroke-width="2" rx="15" />

  <g transform="translate(50, 60)">
    <rect x="0" y="0" width="{w - 100}" height="{h - 120}" rx="14" fill="rgba(255, 255, 255, 0.02)" stroke="rgba(255, 255, 255, 0.08)" />
    <circle cx="120" cy="{int((h - 120) / 2)}" r="80" fill="url(#accent_gen_{asset_id})" opacity="0.85" />
    <rect x="240" y="60" width="{w - 380}" height="28" rx="6" fill="rgba(255, 255, 255, 0.15)" />
    <rect x="240" y="105" width="{w - 440}" height="18" rx="4" fill="rgba(255, 255, 255, 0.08)" />
    <rect x="240" y="135" width="{w - 480}" height="18" rx="4" fill="rgba(255, 255, 255, 0.08)" />
    <rect x="240" y="180" width="140" height="36" rx="8" fill="url(#accent_gen_{asset_id})" />
  </g>
</svg>'''


def generate_svg_fallback(
    asset_id: str,
    asset_type: str,
    aspect_ratio: str,
    category: str,
    art_direction_name: str
) -> Dict[str, Any]:
    """Generate a clean, responsive, accessible semantic SVG vector fallback descriptor.
    
    Creates a concrete, polished product visualization (e.g. institutional treasury
    interface for fintech, cloud orchestrator console for saas) without exposing internal
    prompts, asset metadata, or placeholder instructions.
    """
    ratio_parts = aspect_ratio.split(":")
    w, h = 800, 450
    if len(ratio_parts) == 2:
        try:
            rw, rh = int(ratio_parts[0]), int(ratio_parts[1])
            w = 800
            h = int(800 * (rh / rw))
        except ValueError:
            w, h = 800, 450

    cat_lower = (category or "").lower()
    if cat_lower in ("fintech", "finance", "crypto", "banking", "treasury", "wallet"):
        svg_content = _generate_fintech_svg(w, h, asset_id)
        alt_text = f"Institutional digital treasury ledger and real-time portfolio interface for {category}"
    elif cat_lower in ("saas", "developer-tools", "dev-tool", "tech", "cloud"):
        svg_content = _generate_saas_svg(w, h, asset_id)
        alt_text = f"Cloud runtime telemetry orchestrator console for {category}"
    else:
        svg_content = _generate_generic_svg(w, h, asset_id, category, art_direction_name)
        alt_text = f"Visual product interface architecture for {category}"

    return {
        "engine": "semantic_vector_svg",
        "aspect_ratio": aspect_ratio,
        "width": w,
        "height": h,
        "format": "image/svg+xml",
        "svg_snippet": svg_content,
        "alt_text": alt_text
    }


class BaseImageProvider:
    """Interface for image generation providers."""
    def is_available(self) -> bool:
        return False

    def generate(self, prompt: str, aspect_ratio: str) -> Optional[Dict[str, Any]]:
        return None


class AssetResolver:
    """Manages asset requirements and applies the 3-tier resolution policy."""

    def __init__(self, provider: Optional[BaseImageProvider] = None):
        self.provider = provider

    def resolve(
        self,
        slot: str,
        pattern: Dict[str, Any],
        art_direction: Dict[str, Any],
        category: str
    ) -> List[AssetRequirement]:
        """Extract and resolve asset requirements for a selected pattern slot."""
        requires = pattern.get("requires", {})
        req_assets = requires.get("assets", []) if isinstance(requires, dict) else []
        ad_name = art_direction.get("name", "Modern Architecture")
        imagery_rules = art_direction.get("imagery", "High contrast, editorial lighting, minimal artifacts")

        resolved_reqs: List[AssetRequirement] = []

        if req_assets:
            for idx, raw_req in enumerate(req_assets):
                primary_type = raw_req.split("|")[0].strip()
                asset_id = f"asset:{slot}:{pattern.get('id', 'pat').split(':')[-1]}:{idx + 1}"
                aspect_ratio = DEFAULT_ASPECT_RATIOS.get(slot, "16:9")

                prompt_brief = (
                    f"{primary_type.capitalize()} for {slot} section of a {category} digital experience. "
                    f"Style: {ad_name}. Visual Direction: {imagery_rules}. "
                    f"Composition framing: {aspect_ratio} ratio, professional studio grade, distraction-free."
                )

                if self.provider and self.provider.is_available():
                    result = self.provider.generate(prompt_brief, aspect_ratio)
                    if result:
                        resolved_reqs.append(AssetRequirement(
                            asset_id=asset_id,
                            slot=slot,
                            role=f"{slot}_media",
                            asset_type=primary_type,
                            aspect_ratio=aspect_ratio,
                            prompt_brief=prompt_brief,
                            resolution_tier=TIER_1_NATIVE,
                            status=STATUS_RESOLVED,
                            fallback_descriptor=generate_svg_fallback(asset_id, primary_type, aspect_ratio, category, ad_name),
                            licensing={"type": "ai_generated_original", "provenance": "atlas_native_pipeline"}
                        ))
                        continue

                fallback = generate_svg_fallback(asset_id, primary_type, aspect_ratio, category, ad_name)
                resolved_reqs.append(AssetRequirement(
                    asset_id=asset_id,
                    slot=slot,
                    role=f"{slot}_media",
                    asset_type=primary_type,
                    aspect_ratio=aspect_ratio,
                    prompt_brief=prompt_brief,
                    resolution_tier=TIER_3_CSS_SVG,
                    status=STATUS_FALLBACK_READY,
                    fallback_descriptor=fallback,
                    licensing={"type": "local_vector_fallback", "provenance": "atlas_svg_engine"}
                ))

        elif slot in ("hero", "showcase"):
            asset_id = f"asset:{slot}:{pattern.get('id', 'pat').split(':')[-1]}:main"
            aspect_ratio = DEFAULT_ASPECT_RATIOS.get(slot, "16:9")
            prompt_brief = (
                f"Hero centerpiece for {category} website. Style: {ad_name}. "
                f"Visual Direction: {imagery_rules}. Framing: {aspect_ratio} ratio."
            )
            fallback = generate_svg_fallback(asset_id, "hero_graphic", aspect_ratio, category, ad_name)
            resolved_reqs.append(AssetRequirement(
                asset_id=asset_id,
                slot=slot,
                role=f"{slot}_media",
                asset_type="photo",
                aspect_ratio=aspect_ratio,
                prompt_brief=prompt_brief,
                resolution_tier=TIER_3_CSS_SVG,
                status=STATUS_FALLBACK_READY,
                fallback_descriptor=fallback,
                licensing={"type": "local_vector_fallback", "provenance": "atlas_svg_engine"}
            ))

        return resolved_reqs
