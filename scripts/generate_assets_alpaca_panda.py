"""
generate_assets_alpaca_panda.py — Scoped Kawaii Vector SVG -> 300x300px PNG Overhaul
for 4 genuinely distinct sprite sets (24 sprites total):
  1. `bamboo_panda`  (Template 23) — Ultra-round squishy mochi panda (ZERO muscular standing poses!)
  2. `alpaca_cream`  (Template 20) — Concept A: Cozy Cafe & Knit Scarf Alpaca (caramel cushion -> beret & latte)
  3. `alpaca_blush`  (Template 21) — Concept B: Dreamy Fairy Garden Alpaca (flower basket -> prancing -> rose crown)
  4. `alpaca_matcha` (Template 22) — Concept C: Japanese Matcha Picnic Explorer Alpaca (gingham cloth -> saddle -> sunhat & butterfly)

Renders via PyMuPDF native SVG rasterizer at 3x supersampling (900x900 RGBA -> 300x300 Lanczos PNG).
Also renders:
  - `previews/assets_contact_sheet_alpaca_panda_fix.png` (200px large + 44px actual Excel cell size)
  - `previews/assets_contact_sheet_batch3.png` (refreshed directly from current `assets/`)
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

ASSETS_DIR = ROOT / "assets"
PREVIEWS_DIR = ROOT / "previews"


def render_svg_to_png(inner_svg: str, out_path: Path | None = None, size: int = 300) -> Image.Image:
    svg_str = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 300 300">{inner_svg}</svg>'
    )
    doc = pymupdf.open(stream=svg_str.encode("utf-8"), filetype="svg")
    try:
        pix = doc[0].get_pixmap(matrix=pymupdf.Matrix(3, 3), alpha=True)
        im = Image.frombytes("RGBA", (pix.width, pix.height), pix.samples)
    finally:
        doc.close()
    im = im.resize((size, size), Image.LANCZOS)
    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        im.save(out_path, optimize=True)
    return im


# =========================================================================== #
#  SHARED VECTOR PRIMITIVES (Solid fills + fill-opacity cel-shading)
# =========================================================================== #
def shadow(cx=150, cy=262, rx=74, ry=13, opacity=0.11) -> str:
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#3D2B22" fill-opacity="{opacity}"/>'


def sparkle4(cx, cy, r=14, fill="#FDE047", stroke="#B47812", sw=2.6) -> str:
    ir = r * 0.30
    d = (
        f"M {cx},{cy - r} Q {cx + ir},{cy - ir} {cx + r},{cy} "
        f"Q {cx + ir},{cy + ir} {cx},{cy + r} "
        f"Q {cx - ir},{cy + ir} {cx - r},{cy} "
        f"Q {cx - ir},{cy - ir} {cx},{cy - r} Z"
    )
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>'


def heart(cx, cy, s=13, fill="#F48A9E", stroke="#6B3442", sw=2.6, rot=0) -> str:
    d = (
        f"M 0,{s * 0.85} "
        f"C {-s * 1.15},{s * 0.15} {-s * 1.15},{-s * 0.75} {-s * 0.48},{-s * 0.75} "
        f"C {-s * 0.12},{-s * 0.75} 0,{-s * 0.38} 0,{-s * 0.28} "
        f"C 0,{-s * 0.38} {s * 0.12},{-s * 0.75} {s * 0.48},{-s * 0.75} "
        f"C {s * 1.15},{-s * 0.75} {s * 1.15},{s * 0.15} 0,{s * 0.85} Z"
    )
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" transform="translate({cx},{cy}) rotate({rot})"/>'


def petal(cx, cy, s=11, rot=20, fill="#FBB6CE", stroke="#A64D79") -> str:
    d = (
        f"M 0,{s} C {-s * 0.85},{s * 0.3} {-s * 0.75},{-s * 0.65} {-s * 0.2},{-s * 0.9} "
        f"L 0,{-s * 0.55} L {s * 0.2},{-s * 0.9} "
        f"C {s * 0.75},{-s * 0.65} {s * 0.85},{s * 0.3} 0,{s} Z"
    )
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="2.2" stroke-linejoin="round" transform="translate({cx},{cy}) rotate({rot})"/>'


def leaf_shape(cx, cy, length=28, width=13, rot=0, fill="#74C365", stroke="#2F5928", sw=3.2) -> str:
    d = (
        f"M 0,0 C {length * 0.32},{-width} {length * 0.78},{-width * 0.7} {length},0 "
        f"C {length * 0.78},{width * 0.7} {length * 0.32},{width} 0,0 Z"
    )
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot})">'
        f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>'
        f'<path d="M 3,0 Q {length * 0.5},-1.5 {length * 0.82},0" fill="none" stroke="{stroke}" stroke-width="2" stroke-linecap="round" stroke-opacity="0.6"/>'
        f'</g>'
    )


def tiny_flower(cx, cy, r=10, petal_col="#F9A8D4", center_col="#FDE047", stroke="#7A3B5E", sw=2.2) -> str:
    parts = [f'<g transform="translate({cx},{cy})">']
    for k in range(5):
        ang = math.radians(k * 72 - 90)
        px = math.cos(ang) * r * 0.62
        py = math.sin(ang) * r * 0.62
        parts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r * 0.52:.1f}" fill="{petal_col}" stroke="{stroke}" stroke-width="{sw}"/>')
    parts.append(f'<circle cx="0" cy="0" r="{r * 0.36:.1f}" fill="{center_col}" stroke="{stroke}" stroke-width="{sw * 0.85:.1f}"/>')
    parts.append("</g>")
    return "".join(parts)


def zzz(x, y, col="#8C7260") -> str:
    return (
        f'<text x="{x}" y="{y}" font-family="Segoe UI, Arial, sans-serif" font-weight="800" font-size="22" fill="{col}">z</text>'
        f'<text x="{x + 16}" y="{y - 16}" font-family="Segoe UI, Arial, sans-serif" font-weight="800" font-size="16" fill="{col}" fill-opacity="0.8">z</text>'
    )


# =========================================================================== #
#  1. BAMBOO PANDA (`assets/bamboo_panda/`) — ULTRA-ROUND SQUISHY MOCHI PANDA!
# =========================================================================== #
P_OL = "#2D2926"
P_BLK = "#353338"
P_BLK_HI = "#524F58"
P_WHT = "#FFFDF9"
P_SHD = "#EAE5DC"
P_BLUSH = "#FFA8B8"
P_BAM = "#78C864"
P_BAM2 = "#9CE086"
P_BAM_DK = "#48853A"
P_BASK = "#DDA86B"
P_BASK_DK = "#BA8143"
P_BASK_HI = "#F0C992"


def _panda_basket(cx=150, top_y=188, w=150, h=70) -> str:
    hw = w / 2
    bw = hw * 0.78
    bot_y = top_y + h
    parts = [
        # Basket body trapezoid with rounded bottom
        f'<path d="M {cx - hw + 6},{top_y + 10} L {cx - bw},{bot_y - 12} '
        f'Q {cx - bw + 2},{bot_y} {cx - bw + 16},{bot_y} '
        f'L {cx + bw - 16},{bot_y} Q {cx + bw - 2},{bot_y} {cx + bw},{bot_y - 12} '
        f'L {cx + hw - 6},{top_y + 10} Z" fill="{P_BASK}" stroke="{P_OL}" stroke-width="5.5" stroke-linejoin="round"/>',
        # Soft side shading
        f'<path d="M {cx + hw - 26},{top_y + 12} L {cx + bw - 2},{bot_y - 10} '
        f'Q {cx + bw - 2},{bot_y - 3} {cx + bw - 16},{bot_y - 3} L {cx + bw - 34},{bot_y - 3} '
        f'L {cx + hw - 44},{top_y + 12} Z" fill="{P_BASK_DK}" fill-opacity="0.35"/>',
    ]
    # Horizontal bamboo weave bands
    for frac in (0.38, 0.68):
        wy = top_y + 10 + (h - 12) * frac
        ww = hw - 6 - (hw - bw) * frac - 4
        parts.append(f'<path d="M {cx - ww:.1f},{wy:.1f} Q {cx},{wy + 6:.1f} {cx + ww:.1f},{wy:.1f}" fill="none" stroke="#8C5928" stroke-width="3.2" stroke-linecap="round"/>')
    # Vertical weave ribs
    for dx in (-38, -13, 13, 38):
        parts.append(f'<line x1="{cx + dx}" y1="{top_y + 14}" x2="{cx + dx * 0.84:.1f}" y2="{bot_y - 4}" stroke="#8C5928" stroke-width="2.6" stroke-opacity="0.65" stroke-linecap="round"/>')
    # Chunky woven top rim
    parts.append(
        f'<rect x="{cx - hw - 4}" y="{top_y - 4}" width="{w + 8}" height="20" rx="10" '
        f'fill="{P_BASK_HI}" stroke="{P_OL}" stroke-width="5.5"/>'
    )
    for rx in range(int(cx - hw + 14), int(cx + hw - 8), 24):
        parts.append(f'<path d="M {rx},{top_y - 2} Q {rx + 6},{top_y + 6} {rx},{top_y + 14}" fill="none" stroke="#9C6530" stroke-width="2.8" stroke-linecap="round"/>')
    return "".join(parts)


def _panda_head(cx, cy, sc=1.0, tilt=0.0, happy=False, munch=False, blush=True) -> str:
    """Giant ultra-round marshmallow panda head with glossy kawaii eyes and rosy cheeks."""
    parts = [f'<g transform="translate({cx},{cy}) rotate({tilt}) scale({sc})">']
    # Round chubby black ears
    parts.append(f'<circle cx="-46" cy="-42" r="22" fill="{P_BLK}" stroke="{P_OL}" stroke-width="5.5"/>')
    parts.append(f'<circle cx="-49" cy="-46" r="7" fill="{P_BLK_HI}" fill-opacity="0.5"/>')
    parts.append(f'<circle cx="46" cy="-42" r="22" fill="{P_BLK}" stroke="{P_OL}" stroke-width="5.5"/>')
    parts.append(f'<circle cx="43" cy="-46" r="7" fill="{P_BLK_HI}" fill-opacity="0.5"/>')
    # Squishy mochi head silhouette (wider chubby cheeks!)
    parts.append(
        f'<path d="M -66,4 C -68,-34 -42,-58 0,-58 C 42,-58 68,-34 66,4 '
        f'C 66,38 42,54 0,54 C -42,54 -66,38 -66,4 Z" '
        f'fill="{P_WHT}" stroke="{P_OL}" stroke-width="5.5" stroke-linejoin="round"/>'
    )
    # Soft bottom cheek cel-shadow
    parts.append(
        f'<path d="M -56,20 C -42,46 42,46 56,20 C 44,48 -44,48 -56,20 Z" fill="{P_SHD}" fill-opacity="0.8"/>'
    )
    # Tilted cute oval panda eye patches
    parts.append(f'<ellipse cx="-26" cy="2" rx="18" ry="15" transform="rotate(-18 -26 2)" fill="{P_BLK}"/>')
    parts.append(f'<ellipse cx="26" cy="2" rx="18" ry="15" transform="rotate(18 26 2)" fill="{P_BLK}"/>')
    # Eyes
    if happy:
        parts.append('<path d="M -33,3 Q -25,-6 -18,3" fill="none" stroke="#FFFFFF" stroke-width="4.2" stroke-linecap="round"/>')
        parts.append('<path d="M 18,3 Q 25,-6 33,3" fill="none" stroke="#FFFFFF" stroke-width="4.2" stroke-linecap="round"/>')
    else:
        parts.append('<circle cx="-24" cy="1" r="7.2" fill="#171518"/>')
        parts.append('<circle cx="-21.5" cy="-1.8" r="3.1" fill="#FFFFFF"/>')
        parts.append('<circle cx="-26.5" cy="3.5" r="1.4" fill="#FFFFFF"/>')
        parts.append('<circle cx="24" cy="1" r="7.2" fill="#171518"/>')
        parts.append('<circle cx="26.5" cy="-1.8" r="3.1" fill="#FFFFFF"/>')
        parts.append('<circle cx="21.5" cy="3.5" r="1.4" fill="#FFFFFF"/>')
    # Rosy pink cheeks
    if blush:
        parts.append(f'<ellipse cx="-44" cy="20" rx="11" ry="6.5" fill="{P_BLUSH}" fill-opacity="0.72"/>')
        parts.append(f'<ellipse cx="44" cy="20" rx="11" ry="6.5" fill="{P_BLUSH}" fill-opacity="0.72"/>')
    # Tiny rounded nose & kawaii mouth
    parts.append(f'<ellipse cx="0" cy="13" rx="6.8" ry="4.5" fill="{P_OL}"/>')
    if munch:
        parts.append(f'<path d="M -11,22 Q -5,28 0,22 Q 5,28 11,22" fill="none" stroke="{P_OL}" stroke-width="3.6" stroke-linecap="round"/>')
        parts.append(f'<path d="M -5,24 Q 0,34 5,24 Z" fill="#F48A9E" stroke="{P_OL}" stroke-width="2.6"/>')
    else:
        parts.append(f'<path d="M -10,22 Q -5,29 0,21 Q 5,29 10,22" fill="none" stroke="{P_OL}" stroke-width="3.6" stroke-linecap="round"/>')
    parts.append("</g>")
    return "".join(parts)


def _panda_sitting_mochi_body(cx=150, cy=206, sc=1.0) -> str:
    """Super-round squishy pear/mochi sitting body — narrow sloping cute black band, ZERO muscular shoulders!"""
    parts = [f'<g transform="translate({cx},{cy}) scale({sc})">']
    # Plump round white mochi tummy
    parts.append(
        f'<path d="M -46,-20 C -58,8 -56,48 0,50 C 56,48 58,8 46,-20 '
        f'C 36,-42 -36,-42 -46,-20 Z" fill="{P_WHT}" stroke="{P_OL}" stroke-width="5.5" stroke-linejoin="round"/>'
    )
    # Soft bottom belly shading
    parts.append(
        f'<path d="M -44,24 C -28,46 28,46 44,24 C 30,48 -30,48 -44,24 Z" fill="{P_SHD}" fill-opacity="0.75"/>'
    )
    # Narrow soft rounded black shoulder band (stays strictly tucked inside head width!)
    parts.append(
        f'<path d="M -44,-22 C -32,-42 32,-42 44,-22 C 30,-10 -30,-10 -44,-22 Z" '
        f'fill="{P_BLK}" stroke="{P_OL}" stroke-width="4.5" stroke-linejoin="round"/>'
    )
    # Chubby seated stubby hind feet with cute pink paw pads!
    for sx in (-1, 1):
        parts.append(f'<ellipse cx="{sx * 36}" cy="40" rx="20" ry="15" transform="rotate({sx * -18} {sx * 36} 40)" fill="{P_BLK}" stroke="{P_OL}" stroke-width="5"/>')
        parts.append(f'<ellipse cx="{sx * 36}" cy="42" rx="7.5" ry="5.5" fill="{P_BLUSH}" fill-opacity="0.82"/>')
        parts.append(f'<circle cx="{sx * 30}" cy="34" r="2.6" fill="{P_BLUSH}" fill-opacity="0.82"/>')
        parts.append(f'<circle cx="{sx * 37}" cy="32" r="2.6" fill="{P_BLUSH}" fill-opacity="0.82"/>')
        parts.append(f'<circle cx="{sx * 43}" cy="35" r="2.5" fill="{P_BLUSH}" fill-opacity="0.82"/>')
    parts.append("</g>")
    return "".join(parts)


def draw_bamboo_panda(stage: int) -> str:
    if stage == 0:
        # Cozy woven bamboo basket with two fresh green bamboo leaves peeking out
        return "".join([
            shadow(150, 260, 74, 13),
            # Fresh bamboo culm & leaves peeking cleanly out of basket
            f'<path d="M 142,190 Q 134,154 114,132" fill="none" stroke="{P_BAM_DK}" stroke-width="7" stroke-linecap="round"/>',
            f'<path d="M 156,190 Q 166,154 188,136" fill="none" stroke="{P_BAM_DK}" stroke-width="7" stroke-linecap="round"/>',
            leaf_shape(132, 160, 48, 17, -148, P_BAM, P_OL, 4.2),
            leaf_shape(164, 162, 50, 17, -34, P_BAM2, P_OL, 4.2),
            leaf_shape(148, 176, 36, 13, -95, P_BAM2, P_OL, 3.8),
            _panda_basket(150, 186, 152, 72),
        ])

    if stage == 1:
        # Tiny round baby panda peeking adorably over the woven basket rim, two stubby paws on edge
        return "".join([
            shadow(150, 260, 76, 13),
            leaf_shape(96, 178, 34, 12, -142, P_BAM, P_OL, 3.6),
            leaf_shape(204, 178, 34, 12, -38, P_BAM2, P_OL, 3.6),
            _panda_head(150, 146, sc=0.92),
            _panda_basket(150, 186, 152, 72),
            # Two stubby round black paws resting adorably on basket rim
            f'<ellipse cx="114" cy="188" rx="18" ry="13" fill="{P_BLK}" stroke="{P_OL}" stroke-width="5"/>',
            f'<ellipse cx="186" cy="188" rx="18" ry="13" fill="{P_BLK}" stroke="{P_OL}" stroke-width="5"/>',
            f'<ellipse cx="111" cy="184" rx="5" ry="3" fill="{P_BLK_HI}" fill-opacity="0.55"/>',
            f'<ellipse cx="183" cy="184" rx="5" ry="3" fill="{P_BLK_HI}" fill-opacity="0.55"/>',
        ])

    if stage == 2:
        # Ultra-cute chubby baby panda lying/lounging lazily on its round white tummy (belly flop!)
        return "".join([
            shadow(152, 248, 92, 15),
            # Tiny kicking hind black feet at the back right
            f'<ellipse cx="222" cy="184" rx="16" ry="12" transform="rotate(-24 222 184)" fill="{P_BLK}" stroke="{P_OL}" stroke-width="5"/>',
            f'<ellipse cx="238" cy="204" rx="16" ry="12" transform="rotate(14 238 204)" fill="{P_BLK}" stroke="{P_OL}" stroke-width="5"/>',
            f'<circle cx="222" cy="184" r="5" fill="{P_BLUSH}" fill-opacity="0.8"/>',
            # Round squishy belly-flop white body
            f'<path d="M 88,212 C 88,168 148,158 196,174 C 232,186 238,226 206,240 '
            f'C 168,252 96,246 88,212 Z" fill="{P_WHT}" stroke="{P_OL}" stroke-width="5.5" stroke-linejoin="round"/>',
            f'<path d="M 102,226 C 138,244 196,242 214,226 C 194,248 122,248 102,226 Z" fill="{P_SHD}"/>',
            # Soft black back/shoulder saddle patch
            f'<path d="M 134,166 C 158,162 178,168 184,186 C 166,192 146,190 132,182 Z" fill="{P_BLK}" stroke="{P_OL}" stroke-width="4"/>',
            # Cute tiny round white tail puff
            f'<circle cx="228" cy="218" r="11" fill="{P_WHT}" stroke="{P_OL}" stroke-width="4.5"/>',
            # Big round marshmallow head resting forward
            _panda_head(118, 174, sc=0.95, tilt=-7, happy=False),
            # Chubby stubby front paws tucked under chin!
            f'<ellipse cx="86" cy="228" rx="17" ry="12" transform="rotate(-12 86 228)" fill="{P_BLK}" stroke="{P_OL}" stroke-width="5"/>',
            f'<ellipse cx="144" cy="232" rx="18" ry="12" transform="rotate(10 144 232)" fill="{P_BLK}" stroke="{P_OL}" stroke-width="5"/>',
        ])

    if stage == 3:
        # REPLACES muscular standing panda: Plump sitting mochi panda hugging a cute Japanese onigiri with ^w^ smile!
        return "".join([
            shadow(150, 258, 72, 13),
            _panda_sitting_mochi_body(150, 206, sc=1.0),
            _panda_head(150, 122, sc=1.02, happy=True),
            # Cute chubby Japanese triangle onigiri rice ball hugged at tummy!
            f'<path d="M 150,174 C 162,174 176,198 178,214 C 179,224 170,228 150,228 '
            f'C 130,228 121,224 122,214 C 124,198 138,174 150,174 Z" '
            f'fill="#FFFFFF" stroke="{P_OL}" stroke-width="4.8" stroke-linejoin="round"/>',
            # Crisp dark nori seaweed wrap on bottom of onigiri
            f'<path d="M 134,208 L 166,208 L 168,227 L 132,227 Z" fill="#2A4434" stroke="{P_OL}" stroke-width="3.6" stroke-linejoin="round"/>',
            # Tiny cute sesame speckles on rice ball
            '<circle cx="146" cy="192" r="1.8" fill="#4A4540"/>',
            '<circle cx="155" cy="196" r="1.8" fill="#4A4540"/>',
            '<circle cx="150" cy="186" r="1.6" fill="#4A4540"/>',
            # Two short stubby black paws hugging the onigiri tightly!
            f'<ellipse cx="116" cy="198" rx="17" ry="13" transform="rotate(24 116 198)" fill="{P_BLK}" stroke="{P_OL}" stroke-width="5"/>',
            f'<ellipse cx="184" cy="198" rx="17" ry="13" transform="rotate(-24 184 198)" fill="{P_BLK}" stroke="{P_OL}" stroke-width="5"/>',
        ])

    if stage == 4:
        # Happy round sitting panda munching a leafy green bamboo twig + cute tiny green sprout on head!
        return "".join([
            shadow(150, 258, 72, 13),
            _panda_sitting_mochi_body(150, 206, sc=1.02),
            # Tiny fresh green sprout perched on top of head!
            f'<path d="M 150,64 Q 150,48 150,42" fill="none" stroke="{P_BAM_DK}" stroke-width="4.5" stroke-linecap="round"/>',
            leaf_shape(150, 44, 24, 10, -148, P_BAM, P_OL, 3.2),
            leaf_shape(150, 44, 24, 10, -32, P_BAM2, P_OL, 3.2),
            _panda_head(150, 122, sc=1.02, tilt=-3, munch=True),
            # Leafy green bamboo twig held diagonally in front of tummy/mouth
            f'<path d="M 100,224 L 200,152" fill="none" stroke="{P_OL}" stroke-width="14" stroke-linecap="round"/>',
            f'<path d="M 100,224 L 200,152" fill="none" stroke="{P_BAM}" stroke-width="7.5" stroke-linecap="round"/>',
            f'<line x1="132" y1="201" x2="138" y2="208" stroke="{P_BAM_DK}" stroke-width="3" stroke-linecap="round"/>',
            f'<line x1="168" y1="175" x2="174" y2="182" stroke="{P_BAM_DK}" stroke-width="3" stroke-linecap="round"/>',
            leaf_shape(196, 154, 34, 12, -50, P_BAM2, P_OL, 3.4),
            leaf_shape(186, 162, 32, 11, 14, P_BAM, P_OL, 3.4),
            # Stubby paws holding the bamboo twig
            f'<ellipse cx="122" cy="202" rx="16" ry="12" transform="rotate(-18 122 202)" fill="{P_BLK}" stroke="{P_OL}" stroke-width="5"/>',
            f'<ellipse cx="174" cy="186" rx="16" ry="12" transform="rotate(18 174 186)" fill="{P_BLK}" stroke="{P_OL}" stroke-width="5"/>',
        ])

    # Stage 5: Blissful Fluffy Zen Panda beside lush green bamboo stalks, tiny red Japanese scarf, munching bamboo + golden sparkles!
    return "".join([
        shadow(154, 260, 86, 14),
        # Lush bamboo stalks behind/left of panda
        # Stalk 1 (left-back)
        f'<rect x="46" y="70" width="18" height="182" rx="8" fill="{P_BAM}" stroke="{P_OL}" stroke-width="4.8"/>',
        f'<rect x="50" y="74" width="5" height="174" rx="2.5" fill="{P_BAM2}" fill-opacity="0.7"/>',
        f'<line x1="46" y1="126" x2="64" y2="126" stroke="{P_OL}" stroke-width="4.2"/>',
        f'<line x1="46" y1="186" x2="64" y2="186" stroke="{P_OL}" stroke-width="4.2"/>',
        # Stalk 2 (right-back, taller)
        f'<rect x="234" y="54" width="18" height="198" rx="8" fill="{P_BAM}" stroke="{P_OL}" stroke-width="4.8"/>',
        f'<rect x="238" y="58" width="5" height="190" rx="2.5" fill="{P_BAM2}" fill-opacity="0.7"/>',
        f'<line x1="234" y1="112" x2="252" y2="112" stroke="{P_OL}" stroke-width="4.2"/>',
        f'<line x1="234" y1="176" x2="252" y2="176" stroke="{P_OL}" stroke-width="4.2"/>',
        # Fresh bamboo leaf clusters
        leaf_shape(52, 86, 40, 14, -155, P_BAM2, P_OL, 3.4),
        leaf_shape(62, 102, 36, 12, -30, P_BAM, P_OL, 3.4),
        leaf_shape(244, 72, 40, 14, -25, P_BAM2, P_OL, 3.4),
        leaf_shape(236, 94, 36, 12, -152, P_BAM, P_OL, 3.4),
        # Plump sitting mochi panda
        _panda_sitting_mochi_body(150, 208, sc=1.02),
        # Cute tiny red Japanese neck scarf with fluttering knot tail!
        f'<path d="M 106,164 Q 150,188 194,164 Q 198,178 190,184 Q 150,202 110,184 Q 102,178 106,164 Z" '
        f'fill="#E55353" stroke="{P_OL}" stroke-width="4.8" stroke-linejoin="round"/>',
        f'<path d="M 176,180 L 198,202 Q 204,208 194,212 L 174,196 Z" fill="#D43E3E" stroke="{P_OL}" stroke-width="4.2" stroke-linejoin="round"/>',
        # White scarf stitch dots
        '<circle cx="132" cy="181" r="2.6" fill="#FFE8E8"/>',
        '<circle cx="150" cy="184" r="2.6" fill="#FFE8E8"/>',
        '<circle cx="168" cy="181" r="2.6" fill="#FFE8E8"/>',
        # Happy Zen panda head
        _panda_head(150, 122, sc=1.02, happy=True, munch=True),
        # Little bamboo sprig held in stubby paws (clearer leaf tip above scarf!)
        f'<path d="M 116,214 L 194,174" fill="none" stroke="{P_OL}" stroke-width="11" stroke-linecap="round"/>',
        f'<path d="M 116,214 L 194,174" fill="none" stroke="{P_BAM}" stroke-width="5.5" stroke-linecap="round"/>',
        leaf_shape(192, 176, 30, 11, -34, P_BAM2, P_OL, 3.0),
        leaf_shape(182, 184, 24, 9, 18, P_BAM, P_OL, 2.8),
        f'<ellipse cx="122" cy="206" rx="16" ry="12" transform="rotate(18 122 206)" fill="{P_BLK}" stroke="{P_OL}" stroke-width="5"/>',
        f'<ellipse cx="174" cy="204" rx="16" ry="12" transform="rotate(-18 174 204)" fill="{P_BLK}" stroke="{P_OL}" stroke-width="5"/>',
        # Soft golden sparkles (cleanly placed away from ears!)
        sparkle4(84, 46, 14),
        sparkle4(216, 46, 14),
        sparkle4(214, 140, 10),
    ])


# =========================================================================== #
#  2. ALPACA CREAM (`assets/alpaca_cream/`) — CONCEPT A: COZY CAFE & KNIT SCARF
# =========================================================================== #
AC_OL = "#593E2E"
AC_WOOL = "#FFF6E8"
AC_SHD = "#EED9BD"
AC_CAR = "#D69458"
AC_CAR_DK = "#B37039"
AC_HOOF = "#6E4730"
AC_BERET = "#7C4D30"
AC_BLUSH = "#F6A6A0"


def _cream_cushion(cx=150, cy=234, rx=84, ry=26) -> str:
    return "".join([
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{AC_CAR}" stroke="{AC_OL}" stroke-width="5.5"/>',
        f'<ellipse cx="{cx}" cy="{cy - 4}" rx="{rx - 14}" ry="{ry - 8}" fill="#E6AE74"/>',
        # Quilted knit stitch dashes around cushion edge
        f'<path d="M {cx - rx + 18},{cy + 6} Q {cx},{cy + ry - 3} {cx + rx - 18},{cy + 6}" '
        f'fill="none" stroke="{AC_CAR_DK}" stroke-width="3.2" stroke-dasharray="9,7" stroke-linecap="round"/>',
        # Center tuft button
        f'<ellipse cx="{cx}" cy="{cy - 4}" rx="9" ry="5" fill="{AC_CAR_DK}" fill-opacity="0.5"/>',
    ])


def _cream_alpaca_head(cx, cy, sc=1.0, tilt=0.0, sleepy=False, happy=False, beret=False) -> str:
    """Fluffy cream alpaca head with distinct upright teardrop alpaca ears & curly bangs."""
    parts = [f'<g transform="translate({cx},{cy}) rotate({tilt}) scale({sc})">']
    # Tall upright teardrop alpaca ears (unmistakably alpaca!)
    parts.append(
        f'<path d="M -30,-30 C -40,-66 -28,-86 -14,-78 C -4,-72 -6,-46 -12,-30 Z" '
        f'fill="{AC_WOOL}" stroke="{AC_OL}" stroke-width="5.2" stroke-linejoin="round"/>'
    )
    parts.append(
        f'<path d="M -25,-38 C -31,-58 -24,-70 -16,-66 C -11,-63 -13,-46 -16,-38 Z" fill="#F8C8C4"/>'
    )
    parts.append(
        f'<path d="M 30,-30 C 40,-66 28,-86 14,-78 C 4,-72 6,-46 12,-30 Z" '
        f'fill="{AC_WOOL}" stroke="{AC_OL}" stroke-width="5.2" stroke-linejoin="round"/>'
    )
    parts.append(
        f'<path d="M 25,-38 C 31,-58 24,-70 16,-66 C 11,-63 13,-46 16,-38 Z" fill="#F8C8C4"/>'
    )
    # Fluffy scalloped alpaca head cloud outline (crisp soft scallops!)
    parts.append(
        f'<path d="M -48,4 C -54,-18 -40,-42 -20,-42 C -10,-52 10,-52 20,-42 '
        f'C 40,-42 54,-18 48,4 C 52,28 32,44 0,44 C -32,44 -52,28 -48,4 Z" '
        f'fill="{AC_WOOL}" stroke="{AC_OL}" stroke-width="5.5" stroke-linejoin="round"/>'
    )
    # Warm cel-shadow on lower cheek
    parts.append(f'<path d="M -40,20 C -26,40 26,40 40,20 C 28,42 -28,42 -40,20 Z" fill="{AC_SHD}" fill-opacity="0.8"/>')
    # Smooth peach-cream face oval inside wool framing
    parts.append(f'<ellipse cx="0" cy="10" rx="34" ry="26" fill="#FFFBF4"/>')
    # Fluffy forehead curl bangs
    parts.append(
        f'<path d="M -24,-18 Q -12,-6 0,-16 Q 12,-6 24,-18" fill="{AC_WOOL}" stroke="{AC_OL}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
    )
    # Eyes
    if sleepy:
        parts.append(f'<path d="M -22,7 Q -15,14 -8,7" fill="none" stroke="{AC_OL}" stroke-width="3.8" stroke-linecap="round"/>')
        parts.append(f'<path d="M 8,7 Q 15,14 22,7" fill="none" stroke="{AC_OL}" stroke-width="3.8" stroke-linecap="round"/>')
    elif happy:
        parts.append(f'<path d="M -22,9 Q -15,1 -8,9" fill="none" stroke="{AC_OL}" stroke-width="3.8" stroke-linecap="round"/>')
        parts.append(f'<path d="M 8,9 Q 15,1 22,9" fill="none" stroke="{AC_OL}" stroke-width="3.8" stroke-linecap="round"/>')
    else:
        parts.append(f'<circle cx="-15" cy="7" r="5.8" fill="{AC_OL}"/>')
        parts.append('<circle cx="-13" cy="5" r="2.3" fill="#FFFFFF"/>')
        parts.append(f'<circle cx="15" cy="7" r="5.8" fill="{AC_OL}"/>')
        parts.append('<circle cx="17" cy="5" r="2.3" fill="#FFFFFF"/>')
    # Rosy cheeks
    parts.append(f'<ellipse cx="-26" cy="16" rx="8" ry="4.8" fill="{AC_BLUSH}" fill-opacity="0.65"/>')
    parts.append(f'<ellipse cx="26" cy="16" rx="8" ry="4.8" fill="{AC_BLUSH}" fill-opacity="0.65"/>')
    # Classic cute Y-shaped alpaca snout!
    parts.append(f'<path d="M -5,14 L 0,18 L 5,14" fill="none" stroke="{AC_OL}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>')
    parts.append(f'<path d="M 0,18 L 0,23 M -8,23 Q -4,28 0,23 Q 4,28 8,23" fill="none" stroke="{AC_OL}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>')
    # Optional cute brown cafe artist beret tilted playfully on top!
    if beret:
        parts.append(
            f'<g transform="translate(10,-48) rotate(14)">'
            f'<path d="M -38,8 C -40,-16 -18,-26 4,-26 C 30,-26 42,-12 38,8 C 22,16 -22,16 -38,8 Z" '
            f'fill="{AC_BERET}" stroke="{AC_OL}" stroke-width="4.8" stroke-linejoin="round"/>'
            f'<path d="M -24,-6 C -8,-16 12,-16 24,-6" fill="none" stroke="#A6704C" stroke-width="3.2" stroke-linecap="round" stroke-opacity="0.75"/>'
            f'<path d="M 2,-26 L 6,-35" fill="none" stroke="{AC_OL}" stroke-width="4.8" stroke-linecap="round"/>'
            f'</g>'
        )
    parts.append("</g>")
    return "".join(parts)


def _cream_latte_cup(cx, cy, sc=1.0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) scale({sc})">'
        # Steam curls
        f'<path d="M -8,-30 Q -12,-38 -6,-44" fill="none" stroke="#C89E7C" stroke-width="3.2" stroke-linecap="round"/>'
        f'<path d="M 6,-32 Q 10,-40 4,-46" fill="none" stroke="#C89E7C" stroke-width="3.2" stroke-linecap="round"/>'
        # Handle
        f'<path d="M 19,-10 C 33,-10 33,12 19,12" fill="none" stroke="{AC_OL}" stroke-width="5" stroke-linecap="round"/>'
        # Cup body
        f'<path d="M -21,-18 L -17,18 Q -16,24 0,24 Q 16,24 17,18 L 21,-18 Z" fill="#FFFFFF" stroke="{AC_OL}" stroke-width="4.8" stroke-linejoin="round"/>'
        # Caramel coffee sleeve band with tiny heart icon
        f'<path d="M -19,-4 L 19,-4 L 18,12 L -18,12 Z" fill="{AC_CAR}" stroke="{AC_OL}" stroke-width="3.2"/>'
        f'<circle cx="-3" cy="3" r="3" fill="#FFF6E8"/>'
        f'<circle cx="3" cy="3" r="3" fill="#FFF6E8"/>'
        f'<path d="M -5.8,4 L 0,9.5 L 5.8,4 Z" fill="#FFF6E8"/>'
        # Latte foam top
        f'<ellipse cx="0" cy="-18" rx="21" ry="7.2" fill="#D4955A" stroke="{AC_OL}" stroke-width="4.2"/>'
        f'<ellipse cx="0" cy="-18" rx="9" ry="3.2" fill="#FFF6E8"/>'
        f'</g>'
    )


def _knit_scarf(cx=140, cy=146, sc=1.0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) scale({sc})">'
        # Hanging scarf tail with fringe
        f'<path d="M 10,8 L 28,44 L 8,48 L -6,12 Z" fill="{AC_CAR}" stroke="{AC_OL}" stroke-width="4.6" stroke-linejoin="round"/>'
        f'<line x1="6" y1="22" x2="20" y2="19" stroke="#FFF6E8" stroke-width="4.2"/>'
        f'<line x1="11" y1="34" x2="25" y2="31" stroke="#FFF6E8" stroke-width="4.2"/>'
        # Tiny fringes
        f'<line x1="10" y1="48" x2="11" y2="56" stroke="{AC_OL}" stroke-width="3" stroke-linecap="round"/>'
        f'<line x1="18" y1="47" x2="20" y2="55" stroke="{AC_OL}" stroke-width="3" stroke-linecap="round"/>'
        f'<line x1="25" y1="45" x2="28" y2="53" stroke="{AC_OL}" stroke-width="3" stroke-linecap="round"/>'
        # Main neck wrap
        f'<path d="M -34,-4 Q 0,14 34,-4 Q 38,14 32,20 Q 0,34 -32,20 Q -38,14 -34,-4 Z" '
        f'fill="{AC_CAR}" stroke="{AC_OL}" stroke-width="4.8" stroke-linejoin="round"/>'
        # Warm cream knit stripes on collar
        f'<path d="M -16,4 L -14,22" stroke="#FFF6E8" stroke-width="5" stroke-linecap="round"/>'
        f'<path d="M 4,8 L 4,25" stroke="#FFF6E8" stroke-width="5" stroke-linecap="round"/>'
        f'<path d="M 20,4 L 18,21" stroke="#FFF6E8" stroke-width="5" stroke-linecap="round"/>'
        f'</g>'
    )


def draw_alpaca_cream(stage: int) -> str:
    if stage == 0:
        # Cozy knitted caramel cushion + cute cream wool yarn ball + wooden knitting needle (NO cloud blob!)
        return "".join([
            shadow(150, 260, 86, 13),
            _cream_cushion(150, 232, 86, 28),
            # Curly trailing yarn strand
            f'<path d="M 184,218 C 206,228 222,216 218,204 C 214,196 202,204 210,214" fill="none" stroke="{AC_OL}" stroke-width="4" stroke-linecap="round"/>',
            # Tiny wooden knitting needle sticking cleanly through yarn ball
            f'<line x1="112" y1="158" x2="188" y2="210" stroke="{AC_OL}" stroke-width="9" stroke-linecap="round"/>',
            f'<line x1="112" y1="158" x2="188" y2="210" stroke="#C98A4E" stroke-width="4.2" stroke-linecap="round"/>',
            f'<circle cx="110" cy="156" r="7.5" fill="{AC_BERET}" stroke="{AC_OL}" stroke-width="3.6"/>',
            # Fluffy cream yarn ball resting on cushion
            f'<circle cx="150" cy="194" r="34" fill="{AC_WOOL}" stroke="{AC_OL}" stroke-width="5.2"/>',
            f'<path d="M 122,188 Q 150,172 180,188" fill="none" stroke="{AC_CAR}" stroke-width="3.6" stroke-linecap="round"/>',
            f'<path d="M 120,202 Q 150,188 182,202" fill="none" stroke="{AC_CAR}" stroke-width="3.6" stroke-linecap="round"/>',
            f'<path d="M 136,164 Q 156,194 142,226" fill="none" stroke="{AC_CAR_DK}" stroke-width="3.2" stroke-linecap="round"/>',
            f'<path d="M 156,162 Q 172,192 162,224" fill="none" stroke="{AC_CAR_DK}" stroke-width="3.2" stroke-linecap="round"/>',
        ])

    if stage == 1:
        # Sleepy baby cream alpaca curled snugly on the caramel cushion with tiny brown hooves & tall alpaca ears!
        return "".join([
            shadow(150, 260, 86, 13),
            _cream_cushion(150, 232, 86, 28),
            # Curled fluffy wool body on cushion
            f'<path d="M 124,186 C 146,162 206,168 214,202 C 218,224 198,236 164,236 '
            f'C 134,236 112,226 116,204 Z" fill="{AC_WOOL}" stroke="{AC_OL}" stroke-width="5.4" stroke-linejoin="round"/>',
            f'<circle cx="212" cy="196" r="14" fill="{AC_WOOL}" stroke="{AC_OL}" stroke-width="4.8"/>',
            # Clearly visible tiny dark brown hooves peeking at cushion edge
            f'<ellipse cx="148" cy="234" rx="11" ry="8" fill="{AC_HOOF}" stroke="{AC_OL}" stroke-width="4"/>',
            f'<ellipse cx="182" cy="234" rx="11" ry="8" fill="{AC_HOOF}" stroke="{AC_OL}" stroke-width="4"/>',
            # Sleepy baby alpaca head with upright ears
            _cream_alpaca_head(118, 178, sc=0.82, tilt=-8, sleepy=True),
            zzz(178, 140, "#A67C52"),
        ])

    if stage == 2:
        # Fluffy cream baby alpaca sitting down neatly (tucked legs) with rosy cheeks & small caramel ribbon
        return "".join([
            shadow(150, 256, 76, 13),
            # Fluffy tail puff
            f'<circle cx="210" cy="212" r="17" fill="{AC_WOOL}" stroke="{AC_OL}" stroke-width="5"/>',
            # Neat sitting fluffy alpaca body + neck
            f'<path d="M 102,214 C 98,176 110,146 114,132 L 154,132 C 158,154 166,172 190,178 '
            f'C 214,184 216,222 198,238 C 180,252 114,252 104,238 Z" '
            f'fill="{AC_WOOL}" stroke="{AC_OL}" stroke-width="5.5" stroke-linejoin="round"/>',
            f'<path d="M 110,232 C 134,248 180,248 196,232 C 178,250 128,250 110,232 Z" fill="{AC_SHD}"/>',
            # Tucked front legs with cute brown hooves
            f'<path d="M 112,226 C 102,232 102,248 118,248 L 136,248 C 142,248 144,236 136,232" fill="{AC_WOOL}" stroke="{AC_OL}" stroke-width="4.8" stroke-linecap="round"/>',
            f'<ellipse cx="110" cy="242" rx="10" ry="7.5" fill="{AC_HOOF}" stroke="{AC_OL}" stroke-width="4"/>',
            f'<ellipse cx="152" cy="244" rx="10" ry="7.5" fill="{AC_HOOF}" stroke="{AC_OL}" stroke-width="4"/>',
            # Small caramel ribbon bow at neck
            f'<path d="M 110,152 Q 134,162 158,152" fill="none" stroke="{AC_CAR}" stroke-width="8" stroke-linecap="round"/>',
            f'<path d="M 134,158 L 120,149 L 120,167 Z" fill="{AC_CAR}" stroke="{AC_OL}" stroke-width="3.4" stroke-linejoin="round"/>',
            f'<path d="M 134,158 L 148,149 L 148,167 Z" fill="{AC_CAR}" stroke="{AC_OL}" stroke-width="3.4" stroke-linejoin="round"/>',
            f'<circle cx="134" cy="158" r="5.5" fill="{AC_CAR_DK}" stroke="{AC_OL}" stroke-width="3"/>',
            # Head
            _cream_alpaca_head(132, 114, sc=0.92),
        ])

    if stage == 3:
        # Cozy seated cream alpaca (distinct relaxed cafe sitting pose!) wearing a warm knitted caramel-stripe scarf!
        return "".join([
            shadow(150, 260, 82, 13),
            # Fluffy tail puff on right
            f'<circle cx="218" cy="208" r="19" fill="{AC_WOOL}" stroke="{AC_OL}" stroke-width="5.2"/>',
            # Plush scalloped sitting body
            f'<path d="M 94,206 C 90,174 102,146 106,128 L 154,128 C 158,152 166,170 194,176 '
            f'C 220,182 222,222 202,242 C 182,256 112,256 98,240 Z" '
            f'fill="{AC_WOOL}" stroke="{AC_OL}" stroke-width="5.5" stroke-linejoin="round"/>',
            f'<path d="M 106,236 C 134,252 184,252 202,236 C 182,254 126,254 106,236 Z" fill="{AC_SHD}"/>',
            # Soft wool curl accent
            f'<path d="M 158,198 Q 168,190 178,198 Q 186,206 176,214" fill="none" stroke="{AC_SHD}" stroke-width="4" stroke-linecap="round"/>',
            # Tucked front legs + brown hooves
            f'<path d="M 104,228 C 94,234 94,250 112,250 L 132,250 C 140,250 142,238 134,232" fill="{AC_WOOL}" stroke="{AC_OL}" stroke-width="4.8" stroke-linecap="round"/>',
            f'<ellipse cx="104" cy="244" rx="11" ry="8" fill="{AC_HOOF}" stroke="{AC_OL}" stroke-width="4.2"/>',
            f'<ellipse cx="154" cy="246" rx="11" ry="8" fill="{AC_HOOF}" stroke="{AC_OL}" stroke-width="4.2"/>',
            # Warm knitted caramel-stripe scarf!
            _knit_scarf(130, 148, sc=1.0),
            # Happy head
            _cream_alpaca_head(128, 108, sc=0.95),
        ])

    if stage == 4:
        # Cheerful cream alpaca with knit scarf + brown artist beret + steaming latte cup nearby!
        return "".join([
            shadow(150, 262, 86, 13),
            # Back legs
            f'<rect x="102" y="210" width="22" height="44" rx="10" fill="{AC_SHD}" stroke="{AC_OL}" stroke-width="5"/>',
            f'<rect x="102" y="242" width="22" height="14" rx="6" fill="{AC_HOOF}" stroke="{AC_OL}" stroke-width="4.5"/>',
            f'<rect x="160" y="210" width="22" height="44" rx="10" fill="{AC_SHD}" stroke="{AC_OL}" stroke-width="5"/>',
            f'<rect x="160" y="242" width="22" height="14" rx="6" fill="{AC_HOOF}" stroke="{AC_OL}" stroke-width="4.5"/>',
            # Fluffy tail
            f'<circle cx="198" cy="186" r="18" fill="{AC_WOOL}" stroke="{AC_OL}" stroke-width="5.2"/>',
            # Body
            f'<path d="M 92,188 C 88,162 96,138 98,122 L 144,122 C 146,144 152,158 176,162 '
            f'C 202,166 206,204 188,220 C 168,234 104,234 94,218 Z" '
            f'fill="{AC_WOOL}" stroke="{AC_OL}" stroke-width="5.5" stroke-linejoin="round"/>',
            # Front legs
            f'<rect x="112" y="212" width="22" height="46" rx="10" fill="{AC_WOOL}" stroke="{AC_OL}" stroke-width="5"/>',
            f'<rect x="112" y="244" width="22" height="15" rx="6" fill="{AC_HOOF}" stroke="{AC_OL}" stroke-width="4.5"/>',
            f'<rect x="170" y="212" width="22" height="46" rx="10" fill="{AC_WOOL}" stroke="{AC_OL}" stroke-width="5"/>',
            f'<rect x="170" y="244" width="22" height="15" rx="6" fill="{AC_HOOF}" stroke="{AC_OL}" stroke-width="4.5"/>',
            _knit_scarf(122, 146, sc=0.95),
            _cream_alpaca_head(120, 102, sc=0.94, beret=True),
            # Steaming cozy latte cup right beside hooves!
            _cream_latte_cup(234, 232, sc=0.95),
        ])

    # Stage 5: Grand Cozy Cafe Cream Alpaca — ultra-fluffy wool curls, caramel knit scarf, brown beret, latte + heart + golden sparkles!
    return "".join([
        shadow(150, 262, 92, 14),
        # Back legs
        f'<rect x="98" y="210" width="22" height="44" rx="10" fill="{AC_SHD}" stroke="{AC_OL}" stroke-width="5"/>',
        f'<rect x="98" y="242" width="22" height="14" rx="6" fill="{AC_HOOF}" stroke="{AC_OL}" stroke-width="4.5"/>',
        f'<rect x="158" y="210" width="22" height="44" rx="10" fill="{AC_SHD}" stroke="{AC_OL}" stroke-width="5"/>',
        f'<rect x="158" y="242" width="22" height="14" rx="6" fill="{AC_HOOF}" stroke="{AC_OL}" stroke-width="4.5"/>',
        # Extra-plush curled tail
        f'<circle cx="198" cy="182" r="21" fill="{AC_WOOL}" stroke="{AC_OL}" stroke-width="5.2"/>',
        # Ultra-fluffy scalloped wool body
        f'<path d="M 88,186 C 80,164 92,140 96,120 L 146,120 C 148,142 154,154 176,158 '
        f'C 206,162 210,196 196,216 C 186,232 162,234 140,232 C 114,234 90,224 88,186 Z" '
        f'fill="{AC_WOOL}" stroke="{AC_OL}" stroke-width="5.5" stroke-linejoin="round"/>',
        # Soft fluffy wool curl accents on side
        f'<path d="M 150,188 Q 160,180 170,188 Q 178,196 168,204" fill="none" stroke="{AC_SHD}" stroke-width="4" stroke-linecap="round"/>',
        # Front legs
        f'<rect x="110" y="212" width="22" height="46" rx="10" fill="{AC_WOOL}" stroke="{AC_OL}" stroke-width="5"/>',
        f'<rect x="110" y="244" width="22" height="15" rx="6" fill="{AC_HOOF}" stroke="{AC_OL}" stroke-width="4.5"/>',
        f'<rect x="168" y="212" width="22" height="46" rx="10" fill="{AC_WOOL}" stroke="{AC_OL}" stroke-width="5"/>',
        f'<rect x="168" y="244" width="22" height="15" rx="6" fill="{AC_HOOF}" stroke="{AC_OL}" stroke-width="4.5"/>',
        _knit_scarf(120, 146, sc=0.98),
        _cream_alpaca_head(118, 100, sc=0.96, happy=True, beret=True),
        _cream_latte_cup(236, 232, sc=1.0),
        heart(204, 118, 13, "#F48A9E", AC_OL, 2.8, rot=12),
        sparkle4(56, 78, 14),
        sparkle4(236, 76, 15),
        sparkle4(254, 150, 10),
    ])


# =========================================================================== #
#  3. ALPACA BLUSH (`assets/alpaca_blush/`) — CONCEPT B: DREAMY FAIRY GARDEN
# =========================================================================== #
AB_OL = "#663B5B"
AB_WOOL = "#FFF0F7"
AB_LAV = "#E6D4FB"
AB_SHD = "#F4CFE2"
AB_PINK = "#F48FB1"
AB_PINK2 = "#FBC2D9"
AB_LILAC = "#C3A4F5"
AB_LEAF = "#7DC98A"
AB_HOOF = "#A06A8E"


def _blush_alpaca_head(cx, cy, sc=1.0, tilt=0.0, happy=False, daisy_ear=False, tulip_mouth=False, flower_crown=False) -> str:
    """Softer, curlier fairy-garden blush alpaca head with cotton-candy bangs & rosy starry cheeks."""
    parts = [f'<g transform="translate({cx},{cy}) rotate({tilt}) scale({sc})">']
    # Soft curved fairy alpaca ears (slightly wider & softer than Cream!)
    parts.append(
        f'<path d="M -32,-28 C -46,-62 -34,-82 -18,-74 C -6,-68 -8,-44 -14,-28 Z" '
        f'fill="{AB_WOOL}" stroke="{AB_OL}" stroke-width="5" stroke-linejoin="round"/>'
    )
    parts.append(f'<path d="M -28,-36 C -35,-54 -28,-66 -19,-62 C -14,-59 -16,-44 -18,-36 Z" fill="{AB_PINK2}"/>')
    parts.append(
        f'<path d="M 32,-28 C 46,-62 34,-82 18,-74 C 6,-68 8,-44 14,-28 Z" '
        f'fill="{AB_WOOL}" stroke="{AB_OL}" stroke-width="5" stroke-linejoin="round"/>'
    )
    parts.append(f'<path d="M 28,-36 C 35,-54 28,-66 19,-62 C 14,-59 16,-44 18,-36 Z" fill="{AB_PINK2}"/>')
    # Extra-curly scalloped marshmallow head
    parts.append(
        f'<path d="M -48,2 C -56,-14 -46,-36 -28,-40 C -18,-54 18,-54 28,-40 '
        f'C 46,-36 56,-14 48,2 C 54,24 34,44 0,44 C -34,44 -54,24 -48,2 Z" '
        f'fill="{AB_WOOL}" stroke="{AB_OL}" stroke-width="5.2" stroke-linejoin="round"/>'
    )
    # Soft lilac-pink under-chin tint
    parts.append(f'<path d="M -38,20 C -22,40 22,40 38,20 C 24,42 -24,42 -38,20 Z" fill="{AB_LAV}" fill-opacity="0.7"/>')
    parts.append(f'<ellipse cx="0" cy="11" rx="33" ry="25" fill="#FFF9FC"/>')
    # Curly cotton-candy bangs
    parts.append(
        f'<path d="M -26,-16 C -20,-4 -8,-6 -2,-16 C 4,-4 18,-6 26,-16" '
        f'fill="{AB_WOOL}" stroke="{AB_OL}" stroke-width="3.8" stroke-linecap="round" stroke-linejoin="round"/>'
    )
    # Sparkling eyes
    if happy:
        parts.append(f'<path d="M -22,9 Q -15,1 -8,9" fill="none" stroke="{AB_OL}" stroke-width="3.8" stroke-linecap="round"/>')
        parts.append(f'<path d="M 8,9 Q 15,1 22,9" fill="none" stroke="{AB_OL}" stroke-width="3.8" stroke-linecap="round"/>')
    else:
        parts.append(f'<circle cx="-15" cy="7" r="6.2" fill="{AB_OL}"/>')
        parts.append('<circle cx="-13" cy="4.6" r="2.6" fill="#FFFFFF"/>')
        parts.append('<circle cx="-17" cy="9.5" r="1.2" fill="#FFFFFF"/>')
        parts.append(f'<circle cx="15" cy="7" r="6.2" fill="{AB_OL}"/>')
        parts.append('<circle cx="17" cy="4.6" r="2.6" fill="#FFFFFF"/>')
        parts.append('<circle cx="13" cy="9.5" r="1.2" fill="#FFFFFF"/>')
    # Rosy cheeks
    parts.append(f'<ellipse cx="-27" cy="16" rx="8.5" ry="5" fill="{AB_PINK}" fill-opacity="0.55"/>')
    parts.append(f'<ellipse cx="27" cy="16" rx="8.5" ry="5" fill="{AB_PINK}" fill-opacity="0.55"/>')
    # Y-mouth
    parts.append(f'<path d="M -4,14 L 0,18 L 4,14" fill="none" stroke="{AB_OL}" stroke-width="3" stroke-linecap="round"/>')
    parts.append(f'<path d="M 0,18 L 0,23 M -7,23 Q -3.5,27 0,23 Q 3.5,27 7,23" fill="none" stroke="{AB_OL}" stroke-width="3" stroke-linecap="round"/>')
    # Optional tulip held in mouth (Stage 3 — larger, facing right cleanly!)
    if tulip_mouth:
        parts.append(
            f'<g transform="translate(6,22)">'
            f'<path d="M 0,0 Q 22,5 40,-10" fill="none" stroke="#4D9458" stroke-width="4.6" stroke-linecap="round"/>'
            f'<path d="M 40,-10 C 52,-18 52,-34 40,-36 L 35,-24 L 30,-36 C 20,-31 24,-14 40,-10 Z" '
            f'fill="#F472B6" stroke="{AB_OL}" stroke-width="3.4" stroke-linejoin="round"/>'
            f'</g>'
        )
    # Optional tiny pink daisy behind ear (Stage 2!)
    if daisy_ear:
        parts.append(tiny_flower(28, -32, 11, "#FBC2D9", "#FDE047", AB_OL, 2.2))
    # Optional lush pink-and-lavender rose flower crown (Stage 5!)
    if flower_crown:
        parts.append(leaf_shape(-34, -34, 24, 10, -155, AB_LEAF, AB_OL, 2.6))
        parts.append(leaf_shape(34, -34, 24, 10, -25, AB_LEAF, AB_OL, 2.6))
        parts.append(tiny_flower(-23, -40, 13, AB_LILAC, "#FEF08A", AB_OL, 2.4))
        parts.append(tiny_flower(23, -40, 13, AB_LILAC, "#FEF08A", AB_OL, 2.4))
        parts.append(tiny_flower(0, -45, 16, AB_PINK, "#FDE047", AB_OL, 2.6))
    parts.append("</g>")
    return "".join(parts)


def draw_alpaca_blush(stage: int) -> str:
    if stage == 0:
        # Soft pastel pink & lavender woven flower basket with tiny rosebuds (NO cloud blob!)
        return "".join([
            shadow(150, 260, 74, 13),
            # Lush leaves & pastel rosebuds peeking over rim
            leaf_shape(114, 182, 40, 14, -145, AB_LEAF, AB_OL, 3.6),
            leaf_shape(186, 182, 40, 14, -35, AB_LEAF, AB_OL, 3.6),
            leaf_shape(150, 178, 34, 12, -90, "#9AE0A4", AB_OL, 3.4),
            tiny_flower(118, 174, 15, AB_PINK, "#FEF08A", AB_OL, 2.8),
            tiny_flower(182, 174, 15, AB_LILAC, "#FEF08A", AB_OL, 2.8),
            tiny_flower(150, 162, 18, "#F9A8D4", "#FDE047", AB_OL, 3.0),
            # Pastel lavender-pink woven flower basket
            f'<path d="M 86,192 L 100,248 Q 102,258 116,258 L 184,258 Q 198,258 200,248 L 214,192 Z" '
            f'fill="{AB_LAV}" stroke="{AB_OL}" stroke-width="5.2" stroke-linejoin="round"/>',
            f'<path d="M 96,218 Q 150,226 204,218" fill="none" stroke="#9B7BC2" stroke-width="3.2" stroke-linecap="round"/>',
            f'<path d="M 102,240 Q 150,248 198,240" fill="none" stroke="#9B7BC2" stroke-width="3.2" stroke-linecap="round"/>',
            f'<rect x="78" y="182" width="144" height="20" rx="10" fill="{AB_PINK2}" stroke="{AB_OL}" stroke-width="5.2"/>',
            # Cute bow on front of flower basket
            f'<path d="M 150,206 L 136,198 L 136,214 Z" fill="{AB_PINK}" stroke="{AB_OL}" stroke-width="3"/>',
            f'<path d="M 150,206 L 164,198 L 164,214 Z" fill="{AB_PINK}" stroke="{AB_OL}" stroke-width="3"/>',
            f'<circle cx="150" cy="206" r="5" fill="#EC6CA0" stroke="{AB_OL}" stroke-width="2.8"/>',
        ])

    if stage == 1:
        # Bashful tiny pastel blush-lavender alpaca peeking out from behind blooming pink flowers!
        return "".join([
            shadow(150, 256, 86, 13),
            # Shy baby alpaca peeking over flower bush
            _blush_alpaca_head(150, 154, sc=0.92),
            # Lush pastel flower patch in foreground
            f'<path d="M 68,248 C 66,214 96,198 124,206 C 140,192 166,192 182,206 '
            f'C 210,198 236,216 232,248 Z" fill="#A9E5B2" stroke="{AB_OL}" stroke-width="5" stroke-linejoin="round"/>',
            leaf_shape(86, 224, 30, 11, -145, AB_LEAF, AB_OL, 3.0),
            leaf_shape(214, 224, 30, 11, -35, AB_LEAF, AB_OL, 3.0),
            tiny_flower(100, 222, 16, AB_PINK, "#FEF08A", AB_OL, 2.8),
            tiny_flower(150, 214, 18, "#F9A8D4", "#FDE047", AB_OL, 3.0),
            tiny_flower(200, 222, 16, AB_LILAC, "#FEF08A", AB_OL, 2.8),
            tiny_flower(126, 238, 12, AB_LILAC, "#FEF08A", AB_OL, 2.4),
            tiny_flower(176, 238, 12, AB_PINK2, "#FEF08A", AB_OL, 2.4),
            sparkle4(84, 118, 10, "#FDE047", "#B88424", 2.2),
            sparkle4(216, 118, 10, "#FDE047", "#B88424", 2.2),
        ])

    if stage == 2:
        # Fluffy marshmallow blush alpaca loafing/lying peacefully in a flower patch with tiny pink daisy behind ear!
        return "".join([
            shadow(150, 254, 94, 14),
            # Soft flower patch base
            f'<ellipse cx="150" cy="242" rx="94" ry="20" fill="#B8ECC0" stroke="{AB_OL}" stroke-width="4.5"/>',
            # Fluffy lavender cotton-candy tail on left
            f'<circle cx="78" cy="202" r="19" fill="{AB_LAV}" stroke="{AB_OL}" stroke-width="5"/>',
            # Relaxed marshmallow loaf body (facing right-3/4!)
            f'<path d="M 86,216 C 84,174 134,166 176,174 C 210,180 222,212 206,232 '
            f'C 188,246 102,246 86,216 Z" fill="{AB_WOOL}" stroke="{AB_OL}" stroke-width="5.2" stroke-linejoin="round"/>',
            f'<path d="M 98,224 C 130,240 184,240 202,224 C 184,244 120,244 98,224 Z" fill="{AB_LAV}" fill-opacity="0.65"/>',
            # Tucked little front hooves
            f'<ellipse cx="182" cy="236" rx="11" ry="7.5" fill="{AB_HOOF}" stroke="{AB_OL}" stroke-width="4"/>',
            # Head facing slightly right with tiny pink daisy tucked behind ear!
            _blush_alpaca_head(184, 154, sc=0.90, tilt=5, happy=True, daisy_ear=True),
            # Little flowers in the patch
            tiny_flower(82, 240, 11, AB_PINK, "#FEF08A", AB_OL, 2.2),
            tiny_flower(218, 240, 11, AB_LILAC, "#FEF08A", AB_OL, 2.2),
            tiny_flower(148, 248, 10, "#F9A8D4", "#FDE047", AB_OL, 2.0),
        ])

    if stage == 3:
        # Sweet standing blush alpaca facing RIGHT (distinct silhouette from Cream/Matcha!) holding pastel tulip + fluffy lavender tail!
        return "".join([
            shadow(150, 262, 74, 13),
            # Back legs
            f'<rect x="106" y="210" width="21" height="44" rx="10" fill="{AB_LAV}" stroke="{AB_OL}" stroke-width="4.8"/>',
            f'<rect x="106" y="242" width="21" height="14" rx="6" fill="{AB_HOOF}" stroke="{AB_OL}" stroke-width="4.2"/>',
            f'<rect x="164" y="210" width="21" height="44" rx="10" fill="{AB_LAV}" stroke="{AB_OL}" stroke-width="4.8"/>',
            f'<rect x="164" y="242" width="21" height="14" rx="6" fill="{AB_HOOF}" stroke="{AB_OL}" stroke-width="4.2"/>',
            # Fluffy pastel-lavender cotton-candy tail on LEFT!
            f'<path d="M 96,174 C 72,160 60,184 74,198 C 64,212 86,224 100,210 Z" '
            f'fill="{AB_LAV}" stroke="{AB_OL}" stroke-width="4.8" stroke-linejoin="round"/>',
            # Soft cotton-candy standing body facing RIGHT-3/4
            f'<path d="M 192,188 C 196,162 188,136 184,120 L 140,120 C 138,144 132,158 110,162 '
            f'C 84,166 80,204 98,220 C 118,234 180,234 190,218 Z" '
            f'fill="{AB_WOOL}" stroke="{AB_OL}" stroke-width="5.2" stroke-linejoin="round"/>',
            # Front legs
            f'<rect x="96" y="212" width="21" height="46" rx="10" fill="{AB_WOOL}" stroke="{AB_OL}" stroke-width="4.8"/>',
            f'<rect x="96" y="244" width="21" height="14" rx="6" fill="{AB_HOOF}" stroke="{AB_OL}" stroke-width="4.2"/>',
            f'<rect x="154" y="212" width="21" height="46" rx="10" fill="{AB_WOOL}" stroke="{AB_OL}" stroke-width="4.8"/>',
            f'<rect x="154" y="244" width="21" height="14" rx="6" fill="{AB_HOOF}" stroke="{AB_OL}" stroke-width="4.2"/>',
            # Head facing right holding pastel tulip in mouth!
            _blush_alpaca_head(164, 102, sc=0.92, tilt=4, tulip_mouth=True),
        ])

    if stage == 4:
        # Playful PRANCING / LEAPING pastel fairy alpaca wearing a delicate pink blossom collar!
        return "".join([
            shadow(150, 266, 70, 11, opacity=0.09),
            # Back leaping legs springing cleanly back-right!
            f'<g transform="translate(184,218) rotate(-26)">'
            f'<rect x="-10" y="0" width="20" height="42" rx="10" fill="{AB_LAV}" stroke="{AB_OL}" stroke-width="4.8"/>'
            f'<rect x="-10" y="30" width="20" height="13" rx="6" fill="{AB_HOOF}" stroke="{AB_OL}" stroke-width="4"/>'
            f'</g>',
            f'<g transform="translate(198,212) rotate(-38)">'
            f'<rect x="-10" y="0" width="20" height="42" rx="10" fill="{AB_WOOL}" stroke="{AB_OL}" stroke-width="4.8"/>'
            f'<rect x="-10" y="30" width="20" height="13" rx="6" fill="{AB_HOOF}" stroke="{AB_OL}" stroke-width="4"/>'
            f'</g>',
            # Fluffy cotton-candy tail bouncing up!
            f'<path d="M 206,162 C 232,146 244,170 228,186 C 238,200 214,212 200,196 Z" '
            f'fill="{AB_LAV}" stroke="{AB_OL}" stroke-width="4.8" stroke-linejoin="round"/>',
            # Front prancing legs lifted joyfully!
            f'<g transform="translate(108,204) rotate(42)">'
            f'<rect x="-10" y="0" width="20" height="40" rx="10" fill="{AB_LAV}" stroke="{AB_OL}" stroke-width="4.8"/>'
            f'<rect x="-10" y="28" width="20" height="13" rx="6" fill="{AB_HOOF}" stroke="{AB_OL}" stroke-width="4"/>'
            f'</g>',
            # Dynamic tilted prancing body
            f'<g transform="translate(154,182) rotate(-12)">'
            f'<path d="M -50,12 C -54,-14 -44,-40 -40,-56 L 4,-56 C 8,-34 14,-20 36,-16 '
            f'C 62,-12 64,22 48,38 C 28,50 -36,52 -48,34 Z" '
            f'fill="{AB_WOOL}" stroke="{AB_OL}" stroke-width="5.2" stroke-linejoin="round"/>'
            f'</g>',
            f'<g transform="translate(122,208) rotate(32)">'
            f'<rect x="-10" y="0" width="20" height="40" rx="10" fill="{AB_WOOL}" stroke="{AB_OL}" stroke-width="4.8"/>'
            f'<rect x="-10" y="28" width="20" height="13" rx="6" fill="{AB_HOOF}" stroke="{AB_OL}" stroke-width="4"/>'
            f'</g>',
            # Delicate pink blossom collar around neck!
            tiny_flower(104, 152, 10, AB_PINK, "#FEF08A", AB_OL, 2.2),
            tiny_flower(124, 158, 11, "#F9A8D4", "#FDE047", AB_OL, 2.2),
            tiny_flower(146, 154, 10, AB_LILAC, "#FEF08A", AB_OL, 2.2),
            # Joyful head
            _blush_alpaca_head(122, 102, sc=0.92, tilt=-6, happy=True),
            # Little fairy sparkles around hooves
            sparkle4(76, 232, 10, "#FDE047", "#B88424", 2.2),
            sparkle4(226, 124, 11, "#FBC2D9", AB_OL, 2.2),
        ])

    # Stage 5: Dreamy Fairy Princess Blush Alpaca — facing RIGHT-3/4 graceful stance, lush pink-lavender rose crown, ribboned tail, petals & stars!
    return "".join([
        shadow(150, 262, 82, 14),
        # Back legs
        f'<rect x="108" y="210" width="21" height="44" rx="10" fill="{AB_LAV}" stroke="{AB_OL}" stroke-width="4.8"/>',
        f'<rect x="108" y="242" width="21" height="14" rx="6" fill="{AB_HOOF}" stroke="{AB_OL}" stroke-width="4.2"/>',
        f'<rect x="168" y="210" width="21" height="44" rx="10" fill="{AB_LAV}" stroke="{AB_OL}" stroke-width="4.8"/>',
        f'<rect x="168" y="242" width="21" height="14" rx="6" fill="{AB_HOOF}" stroke="{AB_OL}" stroke-width="4.2"/>',
        # Fluffy cotton-candy tail on LEFT tied with a pastel pink silk ribbon bow!
        f'<path d="M 102,168 C 70,148 52,176 70,196 C 58,214 86,226 102,210 Z" '
        f'fill="{AB_LAV}" stroke="{AB_OL}" stroke-width="4.8" stroke-linejoin="round"/>',
        f'<path d="M 92,188 L 80,178 L 80,198 Z" fill="#EC6CA0" stroke="{AB_OL}" stroke-width="2.8" stroke-linejoin="round"/>',
        f'<path d="M 92,188 L 104,178 L 104,198 Z" fill="#EC6CA0" stroke="{AB_OL}" stroke-width="2.8" stroke-linejoin="round"/>',
        f'<circle cx="92" cy="188" r="4.5" fill="#F9A8D4" stroke="{AB_OL}" stroke-width="2.4"/>',
        # Graceful cotton-candy body facing RIGHT-3/4
        f'<path d="M 198,188 C 202,162 192,136 188,120 L 142,120 C 140,144 134,158 112,162 '
        f'C 84,166 80,204 98,220 C 118,234 184,234 194,218 Z" '
        f'fill="{AB_WOOL}" stroke="{AB_OL}" stroke-width="5.2" stroke-linejoin="round"/>',
        # Front legs
        f'<rect x="98" y="212" width="21" height="46" rx="10" fill="{AB_WOOL}" stroke="{AB_OL}" stroke-width="4.8"/>',
        f'<rect x="98" y="244" width="21" height="14" rx="6" fill="{AB_HOOF}" stroke="{AB_OL}" stroke-width="4.2"/>',
        f'<rect x="158" y="212" width="21" height="46" rx="10" fill="{AB_WOOL}" stroke="{AB_OL}" stroke-width="4.8"/>',
        f'<rect x="158" y="244" width="21" height="14" rx="6" fill="{AB_HOOF}" stroke="{AB_OL}" stroke-width="4.2"/>',
        # Delicate blossom collar
        tiny_flower(144, 152, 9.5, AB_LILAC, "#FEF08A", AB_OL, 2.0),
        tiny_flower(166, 158, 10.5, "#F9A8D4", "#FDE047", AB_OL, 2.0),
        tiny_flower(188, 152, 9.5, AB_PINK, "#FEF08A", AB_OL, 2.0),
        # Head with lush pink-lavender rose flower crown!
        _blush_alpaca_head(166, 104, sc=0.94, tilt=3, happy=True, flower_crown=True),
        # Floating pink petals & pastel stars (cleanly away from ears/crown!)
        petal(64, 114, 11, -24, "#FBC2D9", AB_OL),
        petal(238, 122, 11, 28, "#F9A8D4", AB_OL),
        petal(234, 206, 10, -36, AB_LILAC, AB_OL),
        sparkle4(66, 62, 13, "#FDE047", "#B88424", 2.4),
        sparkle4(242, 64, 14, "#FDE047", "#B88424", 2.4),
        sparkle4(52, 154, 10, "#F9A8D4", AB_OL, 2.2),
    ])


# =========================================================================== #
#  4. ALPACA MATCHA (`assets/alpaca_matcha/`) — CONCEPT C: MATCHA PICNIC EXPLORER
# =========================================================================== #
AM_OL = "#2C4D34"
AM_WOOL = "#E2F7DC"
AM_SHD = "#B8E3B2"
AM_LEAF = "#53B058"
AM_LEAF2 = "#82D47C"
AM_HOOF = "#4A6E4E"
AM_STRAW = "#F5D487"
AM_STRAW_DK = "#C9963B"
AM_CORAL = "#E87456"
AM_GOLD = "#F5B82E"
AM_TEAL = "#3C8DAD"


def _picnic_cloth(cx=150, cy=236) -> str:
    """Cute folded green-and-white gingham picnic cloth (clean perspective diamond, NO cloud blob!)."""
    return "".join([
        # Folded cloth silhouette (cozy rounded diamond)
        f'<path d="M {cx},{cy - 28} L {cx + 88},{cy - 2} Q {cx + 94},{cy + 2} {cx + 86},{cy + 6} '
        f'L {cx},{cy + 28} L {cx - 86},{cy + 6} Q {cx - 94},{cy + 2} {cx - 88},{cy - 2} Z" '
        f'fill="#FFFFFF" stroke="{AM_OL}" stroke-width="5" stroke-linejoin="round"/>',
        # Soft mint gingham bands
        f'<path d="M {cx - 46},{cy - 14} L {cx + 42},{cy + 16} L {cx + 22},{cy + 22} L {cx - 64},{cy - 8} Z" fill="#A6E0A8" fill-opacity="0.72"/>',
        f'<path d="M {cx + 46},{cy - 14} L {cx - 42},{cy + 16} L {cx - 22},{cy + 22} L {cx + 64},{cy - 8} Z" fill="#A6E0A8" fill-opacity="0.72"/>',
        f'<path d="M {cx - 18},{cy - 23} L {cx + 66},{cy + 5} L {cx + 50},{cy + 10} L {cx - 34},{cy - 18} Z" fill="#6EC274" fill-opacity="0.55"/>',
        f'<path d="M {cx + 18},{cy - 23} L {cx - 66},{cy + 5} L {cx - 50},{cy + 10} L {cx + 34},{cy - 18} Z" fill="#6EC274" fill-opacity="0.55"/>',
        # Crisp re-stroke outer edge
        f'<path d="M {cx},{cy - 28} L {cx + 88},{cy - 2} Q {cx + 94},{cy + 2} {cx + 86},{cy + 6} '
        f'L {cx},{cy + 28} L {cx - 86},{cy + 6} Q {cx - 94},{cy + 2} {cx - 88},{cy - 2} Z" '
        f'fill="none" stroke="{AM_OL}" stroke-width="5" stroke-linejoin="round"/>',
    ])


def _matcha_alpaca_head(cx, cy, sc=1.0, tilt=0.0, sleepy=False, happy=False, head_leaf=False, sunhat=False, clover=False) -> str:
    """Chubbier, rounder chibi matcha alpaca head with cute compact proportions!"""
    parts = [f'<g transform="translate({cx},{cy}) rotate({tilt}) scale({sc})">']
    # Cute rounded chibi matcha ears
    parts.append(
        f'<path d="M -30,-26 C -42,-58 -28,-74 -15,-68 C -6,-62 -8,-40 -12,-26 Z" '
        f'fill="{AM_WOOL}" stroke="{AM_OL}" stroke-width="5.2" stroke-linejoin="round"/>'
    )
    parts.append(f'<path d="M -25,-34 C -31,-48 -24,-59 -17,-56 C -13,-53 -14,-40 -16,-34 Z" fill="#F8C8C4"/>')
    parts.append(
        f'<path d="M 30,-26 C 42,-58 28,-74 15,-68 C 6,-62 8,-40 12,-26 Z" '
        f'fill="{AM_WOOL}" stroke="{AM_OL}" stroke-width="5.2" stroke-linejoin="round"/>'
    )
    parts.append(f'<path d="M 25,-34 C 31,-48 24,-59 17,-56 C 13,-53 14,-40 16,-34 Z" fill="#F8C8C4"/>')
    # Rounder chubbier chibi face silhouette
    parts.append(
        f'<path d="M -52,6 C -56,-16 -42,-42 0,-44 C 42,-42 56,-16 52,6 '
        f'C 54,30 34,44 0,44 C -34,44 -54,30 -52,6 Z" '
        f'fill="{AM_WOOL}" stroke="{AM_OL}" stroke-width="5.4" stroke-linejoin="round"/>'
    )
    parts.append(f'<path d="M -42,20 C -26,40 26,40 42,20 C 28,42 -28,42 -42,20 Z" fill="{AM_SHD}" fill-opacity="0.78"/>')
    parts.append(f'<ellipse cx="0" cy="11" rx="35" ry="25" fill="#F5FDF2"/>')
    # Cute puffy matcha tuft
    parts.append(f'<path d="M -20,-16 Q -8,-6 0,-15 Q 8,-6 20,-16" fill="{AM_WOOL}" stroke="{AM_OL}" stroke-width="3.8" stroke-linecap="round"/>')
    # Eyes
    if sleepy:
        parts.append(f'<path d="M -22,8 Q -15,14 -8,8" fill="none" stroke="{AM_OL}" stroke-width="3.8" stroke-linecap="round"/>')
        parts.append(f'<path d="M 8,8 Q 15,14 22,8" fill="none" stroke="{AM_OL}" stroke-width="3.8" stroke-linecap="round"/>')
    elif happy:
        parts.append(f'<path d="M -22,10 Q -15,1 -8,10" fill="none" stroke="{AM_OL}" stroke-width="3.8" stroke-linecap="round"/>')
        parts.append(f'<path d="M 8,10 Q 15,1 22,10" fill="none" stroke="{AM_OL}" stroke-width="3.8" stroke-linecap="round"/>')
    else:
        parts.append(f'<circle cx="-16" cy="7" r="6" fill="{AM_OL}"/>')
        parts.append('<circle cx="-14" cy="5" r="2.4" fill="#FFFFFF"/>')
        parts.append(f'<circle cx="16" cy="7" r="6" fill="{AM_OL}"/>')
        parts.append('<circle cx="18" cy="5" r="2.4" fill="#FFFFFF"/>')
    # Rosy peach cheeks
    parts.append('<ellipse cx="-28" cy="17" rx="8.5" ry="5" fill="#F8A89A" fill-opacity="0.65"/>')
    parts.append('<ellipse cx="28" cy="17" rx="8.5" ry="5" fill="#F8A89A" fill-opacity="0.65"/>')
    # Cute Y snout
    parts.append(f'<path d="M -4,14 L 0,18 L 4,14" fill="none" stroke="{AM_OL}" stroke-width="3.2" stroke-linecap="round"/>')
    parts.append(f'<path d="M 0,18 L 0,23 M -8,23 Q -4,28 0,23 Q 4,28 8,23" fill="none" stroke="{AM_OL}" stroke-width="3.2" stroke-linecap="round"/>')
    # Optional clover sprig being munched (Stage 2 — clearly extending outside cheek!)
    if clover:
        parts.append(
            f'<g transform="translate(10,22)">'
            f'<path d="M 0,0 Q 20,6 38,-6" fill="none" stroke="#3E8A44" stroke-width="4.4" stroke-linecap="round"/>'
            f'<circle cx="40" cy="-14" r="8" fill="{AM_LEAF}" stroke="{AM_OL}" stroke-width="2.8"/>'
            f'<circle cx="49" cy="-6" r="8" fill="{AM_LEAF2}" stroke="{AM_OL}" stroke-width="2.8"/>'
            f'<circle cx="40" cy="2" r="8" fill="{AM_LEAF}" stroke="{AM_OL}" stroke-width="2.8"/>'
            f'<circle cx="31" cy="-6" r="8" fill="{AM_LEAF2}" stroke="{AM_OL}" stroke-width="2.8"/>'
            f'</g>'
        )
    # Optional tiny fresh tea leaf balanced on head (Stage 1!)
    if head_leaf:
        parts.append(leaf_shape(0, -44, 28, 11, -28, AM_LEAF, AM_OL, 3.2))
    # Optional cute mini woven straw sunhat with green ribbon (Stages 4 & 5!)
    if sunhat:
        parts.append(
            f'<g transform="translate(0,-48) rotate(-6)">'
            # Wide curved straw brim
            f'<ellipse cx="0" cy="12" rx="45" ry="12" fill="{AM_STRAW}" stroke="{AM_OL}" stroke-width="4.6"/>'
            # Hat dome
            f'<path d="M -26,10 C -26,-14 -15,-22 0,-22 C 15,-22 26,-14 26,10 Z" '
            f'fill="{AM_STRAW}" stroke="{AM_OL}" stroke-width="4.6" stroke-linejoin="round"/>'
            # Green ribbon band + fluttering ribbon tail
            f'<path d="M -25,4 Q 0,10 25,4 L 26,10 Q 0,16 -26,10 Z" fill="{AM_LEAF}" stroke="{AM_OL}" stroke-width="2.8"/>'
            f'<path d="M 24,8 L 36,18 L 28,21 L 20,12 Z" fill="{AM_LEAF}" stroke="{AM_OL}" stroke-width="2.4" stroke-linejoin="round"/>'
            # Tiny straw weave line
            f'<path d="M -18,-6 Q 0,-11 18,-6" fill="none" stroke="{AM_STRAW_DK}" stroke-width="2.6" stroke-linecap="round"/>'
            f'</g>'
        )
    parts.append("</g>")
    return "".join(parts)


def _andean_saddle(cx=158, cy=188, pom_poms=False) -> str:
    """Colorful woven Andean/matcha explorer saddle blanket with decorative zigzag & tassels/pom-poms!"""
    parts = [f'<g transform="translate({cx},{cy})">']
    # Curved draped blanket over alpaca back
    parts.append(
        f'<path d="M -30,-22 Q 0,-28 30,-22 L 34,20 Q 0,28 -34,20 Z" '
        f'fill="{AM_CORAL}" stroke="{AM_OL}" stroke-width="4.6" stroke-linejoin="round"/>'
    )
    # Teal woven center stripe
    parts.append(f'<path d="M -31,-6 Q 0,-10 31,-6 L 32,8 Q 0,14 -32,8 Z" fill="{AM_TEAL}"/>')
    # Cream zigzag Andean embroidery
    parts.append(
        f'<polyline points="-26,2 -18,-5 -10,4 -2,-5 6,4 14,-5 22,4 28,-2" '
        f'fill="none" stroke="#FFF8DC" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>'
    )
    # Golden top trim
    parts.append(f'<path d="M -28,-16 Q 0,-20 28,-16" fill="none" stroke="{AM_GOLD}" stroke-width="3.6" stroke-linecap="round"/>')
    # Hanging tassels or festive pom-poms along hem!
    for tx, col in [(-24, AM_GOLD), (0, "#FFF6CC" if pom_poms else AM_GOLD), (24, AM_GOLD)]:
        if pom_poms:
            parts.append(f'<circle cx="{tx}" cy="27" r="6.5" fill="{col}" stroke="{AM_OL}" stroke-width="3"/>')
        else:
            parts.append(f'<path d="M {tx},22 L {tx - 4},33 L {tx + 4},33 Z" fill="{col}" stroke="{AM_OL}" stroke-width="2.6" stroke-linejoin="round"/>')
    parts.append("</g>")
    return "".join(parts)


def _butterfly(cx, cy, sc=1.0, rot=-15) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot}) scale({sc})">'
        f'<ellipse cx="-10" cy="-7" rx="11" ry="8" transform="rotate(-24 -10 -7)" fill="#FDE047" stroke="{AM_OL}" stroke-width="3"/>'
        f'<ellipse cx="10" cy="-7" rx="11" ry="8" transform="rotate(24 10 -7)" fill="#FDE047" stroke="{AM_OL}" stroke-width="3"/>'
        f'<ellipse cx="-8" cy="6" rx="8" ry="6" transform="rotate(20 -8 6)" fill="#FBBF24" stroke="{AM_OL}" stroke-width="2.8"/>'
        f'<ellipse cx="8" cy="6" rx="8" ry="6" transform="rotate(-20 8 6)" fill="#FBBF24" stroke="{AM_OL}" stroke-width="2.8"/>'
        f'<ellipse cx="0" cy="0" rx="3.2" ry="9" fill="{AM_OL}"/>'
        f'<path d="M -1,-8 Q -5,-15 -8,-14 M 1,-8 Q 5,-15 8,-14" fill="none" stroke="{AM_OL}" stroke-width="2" stroke-linecap="round"/>'
        f'</g>'
    )


def draw_alpaca_matcha(stage: int) -> str:
    if stage == 0:
        # Cute folded green gingham picnic cloth with a fresh sprouting matcha tea leaf (NO cloud blob!)
        return "".join([
            shadow(150, 260, 88, 12),
            _picnic_cloth(150, 232),
            # Tiny ceramic matcha saucer/sprout center
            f'<path d="M 150,224 Q 150,188 150,174" fill="none" stroke="{AM_OL}" stroke-width="6.5" stroke-linecap="round"/>',
            f'<path d="M 150,224 Q 150,188 150,174" fill="none" stroke="{AM_LEAF}" stroke-width="3" stroke-linecap="round"/>',
            leaf_shape(150, 178, 44, 16, -142, AM_LEAF, AM_OL, 4.0),
            leaf_shape(150, 178, 44, 16, -38, AM_LEAF2, AM_OL, 4.0),
            leaf_shape(150, 198, 28, 11, -155, AM_LEAF2, AM_OL, 3.4),
        ])

    if stage == 1:
        # Sleepy mint-green baby alpaca napping happily on the gingham picnic cloth with tiny leaf on head!
        return "".join([
            shadow(150, 260, 88, 12),
            _picnic_cloth(150, 234),
            # Curled napping chubby matcha body
            f'<path d="M 122,190 C 146,166 206,172 214,204 C 218,224 196,236 164,236 '
            f'C 134,236 114,226 116,206 Z" fill="{AM_WOOL}" stroke="{AM_OL}" stroke-width="5.2" stroke-linejoin="round"/>',
            f'<circle cx="212" cy="198" r="14" fill="{AM_WOOL}" stroke="{AM_OL}" stroke-width="4.8"/>',
            f'<ellipse cx="146" cy="234" rx="10" ry="7" fill="{AM_HOOF}" stroke="{AM_OL}" stroke-width="3.8"/>',
            f'<ellipse cx="182" cy="234" rx="10" ry="7" fill="{AM_HOOF}" stroke="{AM_OL}" stroke-width="3.8"/>',
            _matcha_alpaca_head(118, 178, sc=0.82, tilt=-7, sleepy=True, head_leaf=True),
            zzz(184, 144, "#4A7A52"),
        ])

    if stage == 2:
        # Chubby front-facing chibi sitting matcha alpaca happily munching a fresh green four-leaf clover!
        return "".join([
            shadow(150, 258, 72, 13),
            # Super-chubby front-sitting dumpling body (distinct silhouette!)
            f'<path d="M 96,204 C 90,164 114,146 150,146 C 186,146 210,164 204,204 '
            f'C 206,240 184,254 150,254 C 116,254 94,240 96,204 Z" '
            f'fill="{AM_WOOL}" stroke="{AM_OL}" stroke-width="5.4" stroke-linejoin="round"/>',
            f'<path d="M 106,232 C 126,250 174,250 194,232 C 176,252 124,252 106,232 Z" fill="{AM_SHD}"/>',
            # Cute front sitting hooves tucked neatly on tummy
            f'<ellipse cx="120" cy="244" rx="16" ry="11" fill="{AM_WOOL}" stroke="{AM_OL}" stroke-width="4.8"/>',
            f'<ellipse cx="116" cy="246" rx="9" ry="7" fill="{AM_HOOF}" stroke="{AM_OL}" stroke-width="3.6"/>',
            f'<ellipse cx="180" cy="244" rx="16" ry="11" fill="{AM_WOOL}" stroke="{AM_OL}" stroke-width="4.8"/>',
            f'<ellipse cx="184" cy="246" rx="9" ry="7" fill="{AM_HOOF}" stroke="{AM_OL}" stroke-width="3.6"/>',
            # Front chibi head munching clover!
            _matcha_alpaca_head(150, 118, sc=0.96, happy=False, clover=True),
        ])

    if stage == 3:
        # Curious matcha alpaca in crisp side-explorer stance wearing colorful woven Andean saddle with golden tassels!
        return "".join([
            shadow(150, 262, 78, 13),
            # Back legs
            f'<rect x="112" y="210" width="22" height="44" rx="10" fill="{AM_SHD}" stroke="{AM_OL}" stroke-width="4.8"/>',
            f'<rect x="112" y="242" width="22" height="14" rx="6" fill="{AM_HOOF}" stroke="{AM_OL}" stroke-width="4.2"/>',
            f'<rect x="176" y="210" width="22" height="44" rx="10" fill="{AM_SHD}" stroke="{AM_OL}" stroke-width="4.8"/>',
            f'<rect x="176" y="242" width="22" height="14" rx="6" fill="{AM_HOOF}" stroke="{AM_OL}" stroke-width="4.2"/>',
            # Fluffy mint tail
            f'<circle cx="216" cy="186" r="18" fill="{AM_WOOL}" stroke="{AM_OL}" stroke-width="5"/>',
            # Chubbier explorer body (facing right-to-left explorer stride!)
            f'<path d="M 98,186 C 94,160 104,136 108,122 L 154,122 C 156,144 162,158 190,162 '
            f'C 218,166 222,204 202,222 C 182,236 112,236 102,218 Z" '
            f'fill="{AM_WOOL}" stroke="{AM_OL}" stroke-width="5.4" stroke-linejoin="round"/>',
            # Front legs
            f'<rect x="122" y="212" width="22" height="46" rx="10" fill="{AM_WOOL}" stroke="{AM_OL}" stroke-width="4.8"/>',
            f'<rect x="122" y="244" width="22" height="14" rx="6" fill="{AM_HOOF}" stroke="{AM_OL}" stroke-width="4.2"/>',
            f'<rect x="186" y="212" width="22" height="46" rx="10" fill="{AM_WOOL}" stroke="{AM_OL}" stroke-width="4.8"/>',
            f'<rect x="186" y="244" width="22" height="14" rx="6" fill="{AM_HOOF}" stroke="{AM_OL}" stroke-width="4.2"/>',
            # Colorful woven Andean saddle blanket with tassels!
            _andean_saddle(172, 186, pom_poms=False),
            _matcha_alpaca_head(126, 106, sc=0.92),
        ])

    if stage == 4:
        # Cheerful TROTTING matcha alpaca wearing mini woven straw sunhat + ornate saddle blanket!
        return "".join([
            shadow(150, 264, 82, 12),
            # Trotting alternating back legs
            f'<g transform="translate(116,214) rotate(18)">'
            f'<rect x="-10" y="0" width="21" height="44" rx="10" fill="{AM_SHD}" stroke="{AM_OL}" stroke-width="4.8"/>'
            f'<rect x="-10" y="32" width="21" height="13" rx="6" fill="{AM_HOOF}" stroke="{AM_OL}" stroke-width="4.2"/>'
            f'</g>',
            f'<g transform="translate(184,214) rotate(-20)">'
            f'<rect x="-10" y="0" width="21" height="44" rx="10" fill="{AM_SHD}" stroke="{AM_OL}" stroke-width="4.8"/>'
            f'<rect x="-10" y="32" width="21" height="13" rx="6" fill="{AM_HOOF}" stroke="{AM_OL}" stroke-width="4.2"/>'
            f'</g>',
            # Fluffy tail bouncing
            f'<circle cx="218" cy="180" r="18" fill="{AM_WOOL}" stroke="{AM_OL}" stroke-width="5"/>',
            # Trotting body
            f'<path d="M 96,184 C 92,158 102,134 106,120 L 152,120 C 154,142 162,156 190,160 '
            f'C 218,164 222,202 202,220 C 182,234 112,234 100,216 Z" '
            f'fill="{AM_WOOL}" stroke="{AM_OL}" stroke-width="5.4" stroke-linejoin="round"/>',
            # Trotting front legs
            f'<g transform="translate(128,214) rotate(-22)">'
            f'<rect x="-10" y="0" width="21" height="44" rx="10" fill="{AM_WOOL}" stroke="{AM_OL}" stroke-width="4.8"/>'
            f'<rect x="-10" y="32" width="21" height="13" rx="6" fill="{AM_HOOF}" stroke="{AM_OL}" stroke-width="4.2"/>'
            f'</g>',
            f'<g transform="translate(194,212) rotate(18)">'
            f'<rect x="-10" y="0" width="21" height="44" rx="10" fill="{AM_WOOL}" stroke="{AM_OL}" stroke-width="4.8"/>'
            f'<rect x="-10" y="32" width="21" height="13" rx="6" fill="{AM_HOOF}" stroke="{AM_OL}" stroke-width="4.2"/>'
            f'</g>',
            _andean_saddle(172, 184, pom_poms=False),
            _matcha_alpaca_head(124, 108, sc=0.92, tilt=-4, happy=False, sunhat=True),
        ])

    # Stage 5: Joyful Matcha Meadow Explorer Alpaca — ornate pom-pom saddle + mini straw sunhat + fluttering yellow butterfly + sparkles!
    return "".join([
        shadow(150, 264, 84, 13),
        # Trotting back legs
        f'<g transform="translate(114,214) rotate(16)">'
        f'<rect x="-10" y="0" width="21" height="44" rx="10" fill="{AM_SHD}" stroke="{AM_OL}" stroke-width="4.8"/>'
        f'<rect x="-10" y="32" width="21" height="13" rx="6" fill="{AM_HOOF}" stroke="{AM_OL}" stroke-width="4.2"/>'
        f'</g>',
        f'<g transform="translate(182,214) rotate(-18)">'
        f'<rect x="-10" y="0" width="21" height="44" rx="10" fill="{AM_SHD}" stroke="{AM_OL}" stroke-width="4.8"/>'
        f'<rect x="-10" y="32" width="21" height="13" rx="6" fill="{AM_HOOF}" stroke="{AM_OL}" stroke-width="4.2"/>'
        f'</g>',
        # Tail
        f'<circle cx="218" cy="180" r="19" fill="{AM_WOOL}" stroke="{AM_OL}" stroke-width="5"/>',
        # Body
        f'<path d="M 94,184 C 90,158 100,134 104,120 L 152,120 C 154,142 162,156 190,160 '
        f'C 218,164 222,202 202,220 C 182,234 110,234 98,216 Z" '
        f'fill="{AM_WOOL}" stroke="{AM_OL}" stroke-width="5.4" stroke-linejoin="round"/>',
        # Trotting front legs
        f'<g transform="translate(126,214) rotate(-20)">'
        f'<rect x="-10" y="0" width="21" height="44" rx="10" fill="{AM_WOOL}" stroke="{AM_OL}" stroke-width="4.8"/>'
        f'<rect x="-10" y="32" width="21" height="13" rx="6" fill="{AM_HOOF}" stroke="{AM_OL}" stroke-width="4.2"/>'
        f'</g>',
        f'<g transform="translate(192,212) rotate(16)">'
        f'<rect x="-10" y="0" width="21" height="44" rx="10" fill="{AM_WOOL}" stroke="{AM_OL}" stroke-width="4.8"/>'
        f'<rect x="-10" y="32" width="21" height="13" rx="6" fill="{AM_HOOF}" stroke="{AM_OL}" stroke-width="4.2"/>'
        f'</g>',
        # Ornate pom-pom woven saddle!
        _andean_saddle(172, 184, pom_poms=True),
        # Joyful head with mini straw sunhat
        _matcha_alpaca_head(122, 108, sc=0.93, tilt=-4, happy=True, sunhat=True),
        # Cute fluttering yellow butterfly perched near ear!
        _butterfly(214, 92, sc=1.05, rot=-18),
        # Dotted flight trail
        f'<path d="M 228,112 Q 242,124 236,142" fill="none" stroke="{AM_LEAF}" stroke-width="2.6" stroke-dasharray="4,5" stroke-linecap="round"/>',
        sparkle4(56, 74, 14),
        sparkle4(248, 66, 13),
        sparkle4(250, 164, 10),
    ])


# =========================================================================== #
#  REGISTRY & DUAL-SCALE CONTACT SHEET RENDERER (200px LARGE + 44px EXCEL)
# =========================================================================== #
OVERHAUL_THEMES = [
    ("bamboo_panda",  "23. Bamboo Panda (Round Mochi — Basket -> Belly-Flop -> Onigiri -> Zen Scarf)", draw_bamboo_panda),
    ("alpaca_cream",  "20. Cream Alpaca (Concept A — Cozy Cafe: Cushion -> Knit Scarf -> Beret & Latte)", draw_alpaca_cream),
    ("alpaca_blush",  "21. Blush Alpaca (Concept B — Fairy Garden: Flower Basket -> Loaf -> Prancing -> Rose Crown)", draw_alpaca_blush),
    ("alpaca_matcha", "22. Matcha Alpaca (Concept C — Picnic Explorer: Gingham Cloth -> Clover -> Saddle -> Sunhat & Butterfly)", draw_alpaca_matcha),
]

BATCH3_SLUGS = [
    "alpaca_cream", "alpaca_blush", "alpaca_matcha", "bamboo_panda",
    "royal_cat_cash", "ginger_kitten", "purple_cat", "hatching_chick",
    "candy_jar", "rose_bouquet", "shiba_inu", "akita_inu",
]


def _font(size: int, bold: bool = False):
    for nm in (("segoeuib.ttf" if bold else "segoeui.ttf"), "arial.ttf"):
        try:
            return ImageFont.truetype(nm, size)
        except OSError:
            continue
    return ImageFont.load_default()


def build_fix_contact_sheet(all_imgs: dict[str, list[Image.Image]], out_path: Path):
    big = 200
    small = 44
    pad = 16
    row_h = 46 + big + 18
    W = pad + 6 * (big + 12) + 28 + 6 * (small + 6) + pad
    H = 68 + len(OVERHAUL_THEMES) * row_h + 16
    canvas = Image.new("RGB", (W, H), (252, 249, 244))
    d = ImageDraw.Draw(canvas)
    f_h = _font(22, True)
    f_l = _font(15, True)
    f_s = _font(12, False)

    d.text((pad, 16), "ALPACA & PANDA ART OVERHAUL — LARGE (200px) + ACTUAL EXCEL CELL SIZE (44px)", fill=(58, 42, 34), font=f_h)
    sx0 = pad + 6 * (big + 12) + 24
    d.text((sx0, 26), "Actual 44px Excel Cell Preview (Stage 0 -> 5):", fill=(120, 100, 90), font=f_s)

    for idx, (slug, label, _) in enumerate(OVERHAUL_THEMES):
        y0 = 66 + idx * row_h
        d.line((pad, y0, W - pad, y0), fill=(230, 220, 206), width=2)
        d.text((pad, y0 + 10), label, fill=(64, 48, 40), font=f_l)
        ims = all_imgs[slug]
        for s, im in enumerate(ims):
            x = pad + s * (big + 12)
            y = y0 + 38
            d.rounded_rectangle((x, y, x + big, y + big), radius=12, fill=(255, 255, 255), outline=(230, 222, 212), width=1)
            canvas.paste(im.resize((big - 12, big - 12), Image.LANCZOS), (x + 6, y + 6), im.resize((big - 12, big - 12), Image.LANCZOS))
            d.text((x + 8, y + big - 18), f"S{s}", fill=(140, 128, 118), font=f_s)

            # 44px cell preview on right
            xs = sx0 + s * (small + 6)
            ys = y + (big - small) // 2
            d.rounded_rectangle((xs - 2, ys - 2, xs + small + 2, ys + small + 2), radius=5, fill=(255, 255, 255), outline=(218, 210, 200), width=1)
            sm = im.resize((small, small), Image.LANCZOS)
            canvas.paste(sm, (xs, ys), sm)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, optimize=True)


def main():
    from generate_assets import build_contact_sheet

    all_imgs: dict[str, list[Image.Image]] = {}
    for slug, _, fn in OVERHAUL_THEMES:
        ims = []
        for s in range(6):
            out = ASSETS_DIR / slug / f"stage_{s}.png"
            im = render_svg_to_png(fn(s), out, size=300)
            ims.append(im)
        all_imgs[slug] = ims
        print(f"  OK {slug}: 6 PNGs written to assets/{slug}/", flush=True)

    fix_sheet = PREVIEWS_DIR / "assets_contact_sheet_alpaca_panda_fix.png"
    build_fix_contact_sheet(all_imgs, fix_sheet)
    print(f"  OK Contact sheet: {fix_sheet.relative_to(ROOT)} ({fix_sheet.stat().st_size:,} B)", flush=True)

    # Immediately refresh previews/assets_contact_sheet_batch3.png from current assets/!
    b3_imgs = {
        slug: [Image.open(ASSETS_DIR / slug / f"stage_{s}.png").convert("RGBA") for s in range(6)]
        for slug in BATCH3_SLUGS
    }
    b3_out = PREVIEWS_DIR / "assets_contact_sheet_batch3.png"
    build_contact_sheet(b3_imgs, b3_out)
    print(f"  OK Refreshed Batch 3 sheet: {b3_out.relative_to(ROOT)} ({b3_out.stat().st_size:,} B)", flush=True)


if __name__ == "__main__":
    main()
