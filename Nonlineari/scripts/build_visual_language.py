#!/usr/bin/env python3
"""
Build a custom visual language animation from layered poetic input.

Outputs:
  - output/visual_language_animation.svg   (animated SVG)
  - output/visual_language_semantics.json  (semantic timeline + metadata)
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path
from typing import Dict, List, Tuple


# Layer 0: Raw Poetic Input Parser (stream -> semantic foundation)
USER_STREAM = """
In the third man 333 Old Street French Connection
l'apartmente a film about clubbing
in work of machine learning
"""


# Layer 1: Multi-layer Token Association Mapper
TOKENS: Dict[str, str] = {
    "third_man": (
        "shadowy observer / hidden actor in systems "
        "(1949 noir OR metaphorical third element in data triples)"
    ),
    "333_Old_Street": (
        "iconic London club venue (Mother / 333 Club, Hoxton) - legendary "
        "90s-2000s techno/house/electronic nights, sweat-soaked dancefloor history"
    ),
    "French_Connection": (
        "L'Appartement (1996 French thriller, dir. Gilles Mimouni) starring Monica "
        "Bellucci & Vincent Cassel - obsessive love, identity swaps, apartment as liminal space"
    ),
    "l_apartmente": (
        "the apartment - private/intimate container turning into site of mystery, "
        "desire, revelation"
    ),
    "film_about_clubbing": (
        "narrative of nightlife immersion, blurred realities, hedonistic pursuit, "
        "post-club disorientation"
    ),
    "machine_learning": (
        "algorithmic pattern recognition in chaotic data (crowd movement, music flow, "
        "emotional states) -> predictive models for club experiences, recommendation "
        "engines, generative club visuals"
    ),
}


# Layer 2: Narrative Bridge
NARRATIVE_BRIDGE = (
    "Barry Can't Swim Late Night Tales (2026) = continuous electronic/ambient/house journey. "
    "New input = clubbing filmic layer: 333 Old Street as physical dancefloor apartment "
    "where French cinematic obsession meets ML-driven sound design."
)


CANONICAL_PATTERNS: List[Tuple[str, str]] = [
    (r"\bthird\s+man\b", "third_man"),
    (r"\b333\s+old\s+street\b", "333_Old_Street"),
    (r"\bfrench\s+connection\b", "French_Connection"),
    (r"\bl[’']apartmente\b", "l_apartmente"),
    (r"\bfilm\s+about\s+clubbing\b", "film_about_clubbing"),
    (r"\bmachine\s+learning\b", "machine_learning"),
]


@dataclass
class SemanticHit:
    key: str
    phrase: str
    definition: str
    start_char: int
    end_char: int
    index: int


def normalise_text(value: str) -> str:
    text = value.strip().replace("’", "'")
    text = re.sub(r"\s+", " ", text)
    return text


def parse_semantic_hits(stream: str) -> List[SemanticHit]:
    text = normalise_text(stream)
    hits: List[SemanticHit] = []
    for pattern, key in CANONICAL_PATTERNS:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            phrase = match.group(0)
            hits.append(
                SemanticHit(
                    key=key,
                    phrase=phrase,
                    definition=TOKENS[key],
                    start_char=match.start(),
                    end_char=match.end(),
                    index=0,
                )
            )
    hits.sort(key=lambda item: (item.start_char, item.end_char))
    for idx, item in enumerate(hits):
        item.index = idx
    return hits


def key_to_colour(key: str) -> str:
    digest = sha256(key.encode("utf-8")).hexdigest()
    hue = int(digest[:4], 16) % 360
    sat = 68 + (int(digest[4:6], 16) % 18)
    lig = 46 + (int(digest[6:8], 16) % 14)
    return f"hsl({hue} {sat}% {lig}%)"


def key_to_glyph(key: str) -> str:
    glyph_map = {
        "third_man": "◐",
        "333_Old_Street": "▦",
        "French_Connection": "⌬",
        "l_apartmente": "▣",
        "film_about_clubbing": "◍",
        "machine_learning": "◈",
    }
    return glyph_map.get(key, "•")


def intensity_from_definition(definition: str) -> float:
    words = len(re.findall(r"\w+", definition))
    return max(0.35, min(1.0, words / 45.0))


def build_svg(hits: List[SemanticHit], stream: str, out_path: Path) -> None:
    width, height = 1400, 820
    baseline_y = 620
    lane_top = 180
    lane_height = 360
    total = max(len(hits), 1)

    bg_a = "#09090f"
    bg_b = "#161a2a"
    accent = "#9be7ff"
    text_colour = "#e6f6ff"
    muted_text = "#98b7c7"

    pulse_elements: List[str] = []
    orbit_elements: List[str] = []
    label_elements: List[str] = []
    bridge_links: List[str] = []

    for i, hit in enumerate(hits):
        progress = (i + 1) / (total + 1)
        x = 150 + progress * (width - 300)
        y = lane_top + ((i % 4) / 3.0) * lane_height
        colour = key_to_colour(hit.key)
        glyph = key_to_glyph(hit.key)
        intensity = intensity_from_definition(hit.definition)

        radius = 16 + 18 * intensity
        pulse_min = radius * 0.75
        pulse_max = radius * 1.9
        dur = 2.4 + (i % 3) * 0.9
        delay = i * 0.45
        opacity = 0.28 + (0.35 * intensity)

        pulse_elements.append(
            f"""
  <circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.2f}" fill="{colour}" fill-opacity="0.12" stroke="{colour}" stroke-opacity="{opacity:.2f}" stroke-width="2">
    <animate attributeName="r" values="{pulse_min:.2f};{pulse_max:.2f};{pulse_min:.2f}" dur="{dur:.2f}s" begin="{delay:.2f}s" repeatCount="indefinite"/>
    <animate attributeName="stroke-opacity" values="{opacity:.2f};0.12;{opacity:.2f}" dur="{dur:.2f}s" begin="{delay:.2f}s" repeatCount="indefinite"/>
  </circle>
  <text x="{x:.1f}" y="{y + 6:.1f}" text-anchor="middle" font-family="monospace" font-size="{22 + int(10 * intensity)}" fill="{colour}">{glyph}</text>
"""
        )

        orbit_radius = 28 + 12 * intensity
        orbit_elements.append(
            f"""
  <g>
    <circle cx="{x:.1f}" cy="{y:.1f}" r="{orbit_radius:.2f}" fill="none" stroke="{colour}" stroke-opacity="0.25" stroke-dasharray="4 8"/>
    <circle r="4.8" fill="{colour}">
      <animateMotion dur="{4.0 + i * 0.3:.2f}s" begin="{delay:.2f}s" repeatCount="indefinite"
        path="M {x + orbit_radius:.1f} {y:.1f} A {orbit_radius:.1f} {orbit_radius:.1f} 0 1 0 {x - orbit_radius:.1f} {y:.1f} A {orbit_radius:.1f} {orbit_radius:.1f} 0 1 0 {x + orbit_radius:.1f} {y:.1f}"/>
    </circle>
  </g>
"""
        )

        short_label = hit.key.replace("_", " ")
        label_elements.append(
            f"""
  <text x="{x:.1f}" y="{y + 52:.1f}" text-anchor="middle" font-family="monospace" font-size="13" fill="{text_colour}">
    {short_label}
  </text>
"""
        )

        bridge_links.append(
            f"""
  <line x1="{x:.1f}" y1="{y:.1f}" x2="{x:.1f}" y2="{baseline_y:.1f}" stroke="{colour}" stroke-opacity="0.16" stroke-width="1.4">
    <animate attributeName="stroke-opacity" values="0.10;0.32;0.10" dur="{3.6 + i * 0.3:.2f}s" begin="{delay:.2f}s" repeatCount="indefinite"/>
  </line>
"""
        )

    stream_compact = normalise_text(stream)
    bridge_compact = normalise_text(NARRATIVE_BRIDGE)
    wrapped_stream = wrap_text(stream_compact, width=68)
    wrapped_bridge = wrap_text(bridge_compact, width=86)

    stream_lines = "".join(
        [
            f'<tspan x="92" dy="{22 if idx else 0}">{escape_xml(line)}</tspan>'
            for idx, line in enumerate(wrapped_stream)
        ]
    )
    bridge_lines = "".join(
        [
            f'<tspan x="92" dy="{20 if idx else 0}">{escape_xml(line)}</tspan>'
            for idx, line in enumerate(wrapped_bridge)
        ]
    )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{bg_a}" />
      <stop offset="100%" stop-color="{bg_b}" />
    </linearGradient>
    <filter id="softGlow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="3.2" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <rect x="0" y="0" width="{width}" height="{height}" fill="url(#bg)" />
  <rect x="70" y="78" width="{width - 140}" height="{height - 156}" rx="24" fill="none" stroke="{accent}" stroke-opacity="0.25" />

  <text x="90" y="122" font-family="monospace" font-size="24" fill="{text_colour}">Custom Visual Language Animation</text>
  <text x="90" y="150" font-family="monospace" font-size="13" fill="{muted_text}">
    Layered parser -> token mapper -> narrative bridge
  </text>

  <g filter="url(#softGlow)">
    {''.join(bridge_links)}
    {''.join(pulse_elements)}
    {''.join(orbit_elements)}
  </g>
  {''.join(label_elements)}

  <line x1="90" y1="{baseline_y}" x2="{width - 90}" y2="{baseline_y}" stroke="{accent}" stroke-opacity="0.35" stroke-width="1.5"/>
  <text x="92" y="{baseline_y - 14}" font-family="monospace" font-size="12" fill="{muted_text}">
    semantic timeline
  </text>

  <rect x="84" y="{baseline_y + 18}" width="{width - 168}" height="86" rx="10" fill="#0b1020" stroke="{accent}" stroke-opacity="0.22"/>
  <text x="92" y="{baseline_y + 44}" font-family="monospace" font-size="14" fill="{text_colour}">
    {stream_lines}
  </text>

  <rect x="84" y="{baseline_y + 120}" width="{width - 168}" height="114" rx="10" fill="#11172a" stroke="{accent}" stroke-opacity="0.22"/>
  <text x="92" y="{baseline_y + 146}" font-family="monospace" font-size="13" fill="{muted_text}">
    {bridge_lines}
  </text>
</svg>
"""
    out_path.write_text(svg, encoding="utf-8")


def escape_xml(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def wrap_text(text: str, width: int) -> List[str]:
    words = text.split()
    if not words:
        return [""]
    lines: List[str] = []
    current = words[0]
    for word in words[1:]:
        if len(current) + 1 + len(word) <= width:
            current = f"{current} {word}"
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def build_semantic_json(hits: List[SemanticHit], stream: str, out_path: Path) -> None:
    payload = {
        "stream": normalise_text(stream),
        "token_map": TOKENS,
        "narrative_bridge": NARRATIVE_BRIDGE,
        "timeline": [asdict(hit) for hit in hits],
        "visual_grammar": {
            "glyphs": {key: key_to_glyph(key) for key in TOKENS.keys()},
            "colours": {key: key_to_colour(key) for key in TOKENS.keys()},
            "motion": "pulse + orbit mapped to semantic intensity",
        },
    }
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    output_dir = project_root / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    hits = parse_semantic_hits(USER_STREAM)

    svg_path = output_dir / "visual_language_animation.svg"
    json_path = output_dir / "visual_language_semantics.json"

    build_svg(hits, USER_STREAM, svg_path)
    build_semantic_json(hits, USER_STREAM, json_path)

    print(f"Wrote SVG animation: {svg_path}")
    print(f"Wrote semantic JSON: {json_path}")
    print(f"Semantic hits parsed: {len(hits)}")


if __name__ == "__main__":
    main()
