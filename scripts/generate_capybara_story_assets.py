"""
generate_capybara_story_assets.py — Cohesive Kawaii Vector Overhaul for the 12 Redesigned
Capybara Habit Tracker Themes (#48, #49, #51–#60 = 72 brand-new, 100% unique 300x300 PNGs).

Design Rules (Strict Continuity + Visible Growth + Zero Duplicates):
  1. TINY BABY CAPYBARA AT stage_0 (0%): Every single theme begins with an adorable tiny baby
     Capybara (~45-55% scale, round baby head, big sparkly eyes) in a DISTINCT pose interacting
     with the theme's signature object!
  2. SMOOTH VISIBLE GROWTH (stage_0 -> stage_5): Baby -> curious pup -> growing buddy ->
     chubby teen -> full cozy Capybara -> big radiant Master Hero with soft sunny glow & sparkles!
  3. ONE COHESIVE KAWAII VECTOR ART STYLE: 3x supersampled SVG (PyMuPDF -> LANCZOS 300x300 RGBA),
     warm caramel coat (#D69B66), darker snout/paws (#966140), crisp warm dark-brown outline (#4A3228),
     rosy cheek blush (#F6958D), soft cel-shading, ZERO stick arms, ZERO cross-template duplicates!
  4. STRICT SCOPE: Leaves `assets/capybara_pip_puddle/` (#50) 100% UNTOUCHED!
"""
from __future__ import annotations

import hashlib
import math
from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT / "assets"
PREVIEWS_DIR = ROOT / "previews"

OL = "#4A3228"       # Crisp warm dark-brown outline
FUR = "#D69B66"      # Warm caramel capybara fur
FUR_LT = "#E3AF7E"   # Soft warm baby/highlight caramel
FUR_SHD = "#BC7C49"  # Gentle warm cel-shading
SNOUT = "#966140"    # Iconic darker rounded capybara snout & paws
EAR_IN = "#7C4C31"   # Inner ear brown
BLUSH = "#F6958D"    # Rosy kawaii cheeks


# =========================================================================== #
#  3x SUPERSAMPLED SVG -> 300x300 TRANSPARENT PNG + SOFT HERO AURA
# =========================================================================== #
def render_svg(inner_svg: str, size: int = 300) -> Image.Image:
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
    return im.resize((size, size), Image.LANCZOS)


def with_hero_aura(im: Image.Image, rgb: tuple[int, int, int], cy: int = 160) -> Image.Image:
    """Add a soft luminous pastel Gaussian glow strictly inside the 300x300 canvas (zero hard edge)."""
    aura = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
    ad = ImageDraw.Draw(aura)
    r, g, b = rgb
    ad.ellipse([44, cy - 106, 256, cy + 106], fill=(r, g, b, 62))
    ad.ellipse([76, cy - 74, 224, cy + 74], fill=(255, 251, 218, 88))
    aura = aura.filter(ImageFilter.GaussianBlur(radius=22))
    return Image.alpha_composite(aura, im)


# =========================================================================== #
#  REUSABLE VECTOR DECORATIONS & SPARKLES
# =========================================================================== #
def shd(cx=150, cy=266, rx=78, ry=11, op=0.14) -> str:
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#4A3228" fill-opacity="{op}"/>'


def sp4(cx, cy, r=10, fill="#FDE047", stroke="#B45309", sw=2.3) -> str:
    ir = r * 0.28
    d = (
        f"M {cx},{cy - r} Q {cx + ir},{cy - ir} {cx + r},{cy} "
        f"Q {cx + ir},{cy + ir} {cx},{cy + r} "
        f"Q {cx - ir},{cy + ir} {cx - r},{cy} "
        f"Q {cx - ir},{cy - ir} {cx},{cy - r} Z"
    )
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>'


def heart(cx, cy, s=12, fill="#FB7185", stroke=OL, sw=2.6) -> str:
    d = (
        f"M {cx},{cy + s * 0.72} "
        f"C {cx - s * 1.1},{cy + s * 0.05} {cx - s * 1.05},{cy - s * 0.85} {cx - s * 0.42},{cy - s * 0.85} "
        f"C {cx - s * 0.12},{cy - s * 0.85} {cx},{cy - s * 0.52} {cx},{cy - s * 0.38} "
        f"C {cx},{cy - s * 0.52} {cx + s * 0.12},{cy - s * 0.85} {cx + s * 0.42},{cy - s * 0.85} "
        f"C {cx + s * 1.05},{cy - s * 0.85} {cx + s * 1.1},{cy + s * 0.05} {cx},{cy + s * 0.72} Z"
    )
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>'


def note_svg(cx, cy, s=1.0, col="#2563EB") -> str:
    return (
        f'<g transform="translate({cx},{cy}) scale({s})">'
        f'<ellipse cx="-7" cy="10" rx="6" ry="4.5" transform="rotate(-18 -7 10)" fill="{col}" stroke="{OL}" stroke-width="2.2"/>'
        f'<ellipse cx="9" cy="6" rx="6" ry="4.5" transform="rotate(-18 9 6)" fill="{col}" stroke="{OL}" stroke-width="2.2"/>'
        f'<path d="M -2,9 L -2,-11 L 14,-15 L 14,5" fill="none" stroke="{OL}" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<path d="M -2,-10 L 14,-14" stroke="{col}" stroke-width="4.5" stroke-linecap="round"/>'
        f'</g>'
    )


def zzz_svg(x, y, s=1.0) -> str:
    return (
        f'<g transform="translate({x},{y}) scale({s})">'
        f'<text x="0" y="18" font-family="Segoe UI" font-weight="bold" font-size="18" fill="{OL}">z</text>'
        f'<text x="15" y="4" font-family="Segoe UI" font-weight="bold" font-size="24" fill="{OL}">Z</text>'
        f'</g>'
    )


def daisy(cx, cy, r=8, petal="#FFFFFF", center="#FACC15") -> str:
    pts = []
    for k in range(5):
        ang = math.radians(k * 72 - 90)
        px = cx + math.cos(ang) * r * 0.72
        py = cy + math.sin(ang) * r * 0.72
        pts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r*0.52:.1f}" fill="{petal}" stroke="{OL}" stroke-width="2.2"/>')
    pts.append(f'<circle cx="{cx}" cy="{cy}" r="{r*0.42:.1f}" fill="{center}" stroke="{OL}" stroke-width="2.0"/>')
    return "".join(pts)


# =========================================================================== #
#  UNIFIED KAWAII CHIBI CAPYBARA CHARACTER RIG (BABY -> HERO!)
# =========================================================================== #
def capy_face(cx, cy, s=1.0, mode="normal", look_dx=0.0, look_dy=0.0) -> str:
    """Adorable expressive chibi Capybara face. `baby` mode uses larger sparkling eyes!"""
    parts = [
        f'<ellipse cx="{cx:.1f}" cy="{cy + 13*s:.1f}" rx="{22*s:.1f}" ry="{16.5*s:.1f}" fill="{SNOUT}"/>',
        f'<ellipse cx="{cx - 6.8*s:.1f}" cy="{cy + 7.5*s:.1f}" rx="{2.5*s:.1f}" ry="{2.0*s:.1f}" fill="{OL}"/>',
        f'<ellipse cx="{cx + 6.8*s:.1f}" cy="{cy + 7.5*s:.1f}" rx="{2.5*s:.1f}" ry="{2.0*s:.1f}" fill="{OL}"/>',
        f'<ellipse cx="{cx - 42*s:.1f}" cy="{cy + 15*s:.1f}" rx="{12.5*s:.1f}" ry="{8.2*s:.1f}" fill="{BLUSH}" fill-opacity="0.72"/>',
        f'<ellipse cx="{cx + 42*s:.1f}" cy="{cy + 15*s:.1f}" rx="{12.5*s:.1f}" ry="{8.2*s:.1f}" fill="{BLUSH}" fill-opacity="0.72"/>',
    ]
    # Mouth styles
    if mode == "sip":
        parts.append(
            f'<circle cx="{cx:.1f}" cy="{cy + 20*s:.1f}" r="{5.0*s:.1f}" fill="{OL}"/>'
            f'<circle cx="{cx:.1f}" cy="{cy + 20.5*s:.1f}" r="{2.5*s:.1f}" fill="#FB7185"/>'
        )
    elif mode == "rawr":
        parts.append(
            f'<path d="M {cx - 9*s:.1f},{cy + 16*s:.1f} Q {cx:.1f},{cy + 29*s:.1f} {cx + 9*s:.1f},{cy + 16*s:.1f} Z" '
            f'fill="#FB7185" stroke="{OL}" stroke-width="{3.2*s:.1f}" stroke-linejoin="round"/>'
        )
    elif mode == "munch":
        parts.append(
            f'<path d="M {cx - 8*s:.1f},{cy + 18*s:.1f} Q {cx:.1f},{cy + 27*s:.1f} {cx + 8*s:.1f},{cy + 18*s:.1f} Z" '
            f'fill="#F43F5E" stroke="{OL}" stroke-width="{3.0*s:.1f}" stroke-linejoin="round"/>'
        )
    else:
        parts.append(
            f'<path d="M {cx:.1f},{cy + 13*s:.1f} L {cx:.1f},{cy + 19.5*s:.1f} '
            f'M {cx - 8.5*s:.1f},{cy + 19.5*s:.1f} Q {cx - 4.2*s:.1f},{cy + 24.5*s:.1f} {cx:.1f},{cy + 19.5*s:.1f} '
            f'Q {cx + 4.2*s:.1f},{cy + 24.5*s:.1f} {cx + 8.5*s:.1f},{cy + 19.5*s:.1f}" '
            f'fill="none" stroke="{OL}" stroke-width="{3.4*s:.1f}" stroke-linecap="round" stroke-linejoin="round"/>'
        )

    # Eye styles
    ex = 30 * s
    ey = cy + 0.5 * s
    if mode == "sleepy":
        parts.append(
            f'<path d="M {cx - ex - 7*s:.1f},{ey:.1f} Q {cx - ex:.1f},{ey + 7*s:.1f} {cx - ex + 7*s:.1f},{ey:.1f}" fill="none" stroke="{OL}" stroke-width="{3.8*s:.1f}" stroke-linecap="round"/>'
            f'<path d="M {cx + ex - 7*s:.1f},{ey:.1f} Q {cx + ex:.1f},{ey + 7*s:.1f} {cx + ex + 7*s:.1f},{ey:.1f}" fill="none" stroke="{OL}" stroke-width="{3.8*s:.1f}" stroke-linecap="round"/>'
        )
    elif mode in ("happy", "bliss", "munch"):
        parts.append(
            f'<path d="M {cx - ex - 7*s:.1f},{ey + 3*s:.1f} Q {cx - ex:.1f},{ey - 6.5*s:.1f} {cx - ex + 7*s:.1f},{ey + 3*s:.1f}" fill="none" stroke="{OL}" stroke-width="{4.0*s:.1f}" stroke-linecap="round"/>'
            f'<path d="M {cx + ex - 7*s:.1f},{ey + 3*s:.1f} Q {cx + ex:.1f},{ey - 6.5*s:.1f} {cx + ex + 7*s:.1f},{ey + 3*s:.1f}" fill="none" stroke="{OL}" stroke-width="{4.0*s:.1f}" stroke-linecap="round"/>'
        )
    elif mode == "wink":
        parts.append(
            f'<ellipse cx="{cx - ex:.1f}" cy="{ey:.1f}" rx="{8.2*s:.1f}" ry="{9.4*s:.1f}" fill="{OL}"/>'
            f'<circle cx="{cx - ex - 2.4*s:.1f}" cy="{ey - 2.6*s:.1f}" r="{3.2*s:.1f}" fill="#FFFFFF"/>'
            f'<path d="M {cx + ex - 7*s:.1f},{ey + 2*s:.1f} Q {cx + ex:.1f},{ey - 6.5*s:.1f} {cx + ex + 7*s:.1f},{ey + 2*s:.1f}" fill="none" stroke="{OL}" stroke-width="{4.0*s:.1f}" stroke-linecap="round"/>'
        )
    elif mode == "one_peek":
        # One sleepy closed eye + one tiny peeking open eye!
        parts.append(
            f'<path d="M {cx - ex - 7*s:.1f},{ey:.1f} Q {cx - ex:.1f},{ey + 6.5*s:.1f} {cx - ex + 7*s:.1f},{ey:.1f}" fill="none" stroke="{OL}" stroke-width="{3.8*s:.1f}" stroke-linecap="round"/>'
            f'<ellipse cx="{cx + ex:.1f}" cy="{ey:.1f}" rx="{9.0*s:.1f}" ry="{10.2*s:.1f}" fill="{OL}"/>'
            f'<circle cx="{cx + ex - 2.4*s:.1f}" cy="{ey - 3.0*s:.1f}" r="{3.6*s:.1f}" fill="#FFFFFF"/>'
            f'<circle cx="{cx + ex + 2.6*s:.1f}" cy="{ey + 3.0*s:.1f}" r="{1.6*s:.1f}" fill="#FFFFFF"/>'
        )
    elif mode == "baby":
        # Extra-large glossy baby eyes with double sparkles!
        for sx in (-1, 1):
            px = cx + sx * ex + look_dx * s
            py = ey + look_dy * s
            parts.append(
                f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{9.6*s:.1f}" ry="{10.8*s:.1f}" fill="{OL}"/>'
                f'<circle cx="{px - 2.6*s:.1f}" cy="{py - 3.2*s:.1f}" r="{3.8*s:.1f}" fill="#FFFFFF"/>'
                f'<circle cx="{px + 2.8*s:.1f}" cy="{py + 3.0*s:.1f}" r="{1.8*s:.1f}" fill="#FFFFFF"/>'
            )
    else:  # normal / sip / rawr
        for sx in (-1, 1):
            px = cx + sx * ex + look_dx * s
            py = ey + look_dy * s
            parts.append(
                f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{8.0*s:.1f}" ry="{9.2*s:.1f}" fill="{OL}"/>'
                f'<circle cx="{px - 2.3*s:.1f}" cy="{py - 2.6*s:.1f}" r="{3.1*s:.1f}" fill="#FFFFFF"/>'
            )
    return "".join(parts)


def capy_ears(cx, cy, s=1.0, fur=FUR, sw=5.6) -> str:
    return (
        f'<ellipse cx="{cx - 46*s:.1f}" cy="{cy - 44*s:.1f}" rx="{13.5*s:.1f}" ry="{15.5*s:.1f}" '
        f'transform="rotate(-18 {cx - 46*s:.1f} {cy - 44*s:.1f})" fill="{fur}" stroke="{OL}" stroke-width="{sw*min(1.0, s+0.25):.1f}"/>'
        f'<ellipse cx="{cx - 46*s:.1f}" cy="{cy - 42*s:.1f}" rx="{6.8*s:.1f}" ry="{8.5*s:.1f}" '
        f'transform="rotate(-18 {cx - 46*s:.1f} {cy - 42*s:.1f})" fill="{EAR_IN}"/>'
        f'<ellipse cx="{cx + 46*s:.1f}" cy="{cy - 44*s:.1f}" rx="{13.5*s:.1f}" ry="{15.5*s:.1f}" '
        f'transform="rotate(18 {cx + 46*s:.1f} {cy - 44*s:.1f})" fill="{fur}" stroke="{OL}" stroke-width="{sw*min(1.0, s+0.25):.1f}"/>'
        f'<ellipse cx="{cx + 46*s:.1f}" cy="{cy - 42*s:.1f}" rx="{6.8*s:.1f}" ry="{8.5*s:.1f}" '
        f'transform="rotate(18 {cx + 46*s:.1f} {cy - 42*s:.1f})" fill="{EAR_IN}"/>'
    )


def capy_sit(cx, cy_base, s=1.0, mode="normal", feet=True, fur=FUR, look_dx=0.0, look_dy=0.0,
             extra_head="", extra_belly="", paws="none") -> str:
    """Squishy pear-loaf front-sitting Capybara anchored cleanly at bottom `cy_base`."""
    h_tot = 152 * s
    cy_top = cy_base - h_tot
    cy_face = cy_top + 60 * s
    sw = max(4.2, 6.2 * min(1.05, s + 0.15))
    parts = [
        capy_ears(cx, cy_face, s, fur=fur),
        f'<path d="M {cx - 72*s:.1f},{cy_base - 56*s:.1f} '
        f'C {cx - 76*s:.1f},{cy_top + 32*s:.1f} {cx - 46*s:.1f},{cy_top:.1f} {cx:.1f},{cy_top:.1f} '
        f'C {cx + 46*s:.1f},{cy_top:.1f} {cx + 76*s:.1f},{cy_top + 32*s:.1f} {cx + 72*s:.1f},{cy_base - 56*s:.1f} '
        f'C {cx + 72*s:.1f},{cy_base - 14*s:.1f} {cx + 44*s:.1f},{cy_base:.1f} {cx:.1f},{cy_base:.1f} '
        f'C {cx - 44*s:.1f},{cy_base:.1f} {cx - 72*s:.1f},{cy_base - 14*s:.1f} {cx - 72*s:.1f},{cy_base - 56*s:.1f} Z" '
        f'fill="{fur}" stroke="{OL}" stroke-width="{sw:.1f}" stroke-linejoin="round"/>',
        f'<path d="M {cx - 58*s:.1f},{cy_base - 24*s:.1f} C {cx - 34*s:.1f},{cy_base - 4*s:.1f} '
        f'{cx + 34*s:.1f},{cy_base - 4*s:.1f} {cx + 58*s:.1f},{cy_base - 24*s:.1f} '
        f'C {cx + 44*s:.1f},{cy_base - 1*s:.1f} {cx - 44*s:.1f},{cy_base - 1*s:.1f} {cx - 58*s:.1f},{cy_base - 24*s:.1f} Z" '
        f'fill="{FUR_SHD}" fill-opacity="0.55"/>',
    ]
    if feet:
        parts.append(
            f'<ellipse cx="{cx - 34*s:.1f}" cy="{cy_base - 4*s:.1f}" rx="{17*s:.1f}" ry="{10.5*s:.1f}" fill="{SNOUT}" stroke="{OL}" stroke-width="{max(3.6, 4.8*s):.1f}"/>'
            f'<ellipse cx="{cx + 34*s:.1f}" cy="{cy_base - 4*s:.1f}" rx="{17*s:.1f}" ry="{10.5*s:.1f}" fill="{SNOUT}" stroke="{OL}" stroke-width="{max(3.6, 4.8*s):.1f}"/>'
        )
    parts.append(capy_face(cx, cy_face, s * 0.94, mode=mode, look_dx=look_dx, look_dy=look_dy))
    if extra_belly:
        parts.append(extra_belly)
    if paws == "hug":
        parts.append(
            f'<path d="M {cx - 58*s:.1f},{cy_base - 66*s:.1f} C {cx - 60*s:.1f},{cy_base - 42*s:.1f} {cx - 40*s:.1f},{cy_base - 32*s:.1f} {cx - 24*s:.1f},{cy_base - 40*s:.1f} C {cx - 16*s:.1f},{cy_base - 46*s:.1f} {cx - 22*s:.1f},{cy_base - 60*s:.1f} {cx - 36*s:.1f},{cy_base - 60*s:.1f}" fill="{SNOUT}" stroke="{OL}" stroke-width="{max(3.8, 5.0*s):.1f}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="M {cx + 58*s:.1f},{cy_base - 66*s:.1f} C {cx + 60*s:.1f},{cy_base - 42*s:.1f} {cx + 40*s:.1f},{cy_base - 32*s:.1f} {cx + 24*s:.1f},{cy_base - 40*s:.1f} C {cx + 16*s:.1f},{cy_base - 46*s:.1f} {cx + 22*s:.1f},{cy_base - 60*s:.1f} {cx + 36*s:.1f},{cy_base - 60*s:.1f}" fill="{SNOUT}" stroke="{OL}" stroke-width="{max(3.8, 5.0*s):.1f}" stroke-linecap="round" stroke-linejoin="round"/>'
        )
    elif paws == "wave":
        parts.append(
            f'<ellipse cx="{cx - 46*s:.1f}" cy="{cy_base - 52*s:.1f}" rx="{14*s:.1f}" ry="{10*s:.1f}" transform="rotate(20 {cx - 46*s:.1f} {cy_base - 52*s:.1f})" fill="{SNOUT}" stroke="{OL}" stroke-width="{max(3.6, 4.6*s):.1f}"/>'
            f'<ellipse cx="{cx + 62*s:.1f}" cy="{cy_base - 80*s:.1f}" rx="{15*s:.1f}" ry="{10.5*s:.1f}" transform="rotate(-38 {cx + 62*s:.1f} {cy_base - 80*s:.1f})" fill="{SNOUT}" stroke="{OL}" stroke-width="{max(3.6, 4.6*s):.1f}"/>'
        )
    elif paws == "rawr":
        parts.append(
            f'<ellipse cx="{cx - 56*s:.1f}" cy="{cy_base - 72*s:.1f}" rx="{15*s:.1f}" ry="{11*s:.1f}" transform="rotate(32 {cx - 56*s:.1f} {cy_base - 72*s:.1f})" fill="{SNOUT}" stroke="{OL}" stroke-width="{max(3.8, 4.8*s):.1f}"/>'
            f'<ellipse cx="{cx + 56*s:.1f}" cy="{cy_base - 72*s:.1f}" rx="{15*s:.1f}" ry="{11*s:.1f}" transform="rotate(-32 {cx + 56*s:.1f} {cy_base - 72*s:.1f})" fill="{SNOUT}" stroke="{OL}" stroke-width="{max(3.8, 4.8*s):.1f}"/>'
        )
    elif paws == "poke_right":
        parts.append(
            f'<ellipse cx="{cx + 56*s:.1f}" cy="{cy_base - 48*s:.1f}" rx="{16*s:.1f}" ry="{10*s:.1f}" transform="rotate(-12 {cx + 56*s:.1f} {cy_base - 48*s:.1f})" fill="{SNOUT}" stroke="{OL}" stroke-width="{max(3.6, 4.6*s):.1f}"/>'
        )
    elif paws == "front_hold":
        parts.append(
            f'<ellipse cx="{cx - 32*s:.1f}" cy="{cy_base - 46*s:.1f}" rx="{14*s:.1f}" ry="{10*s:.1f}" fill="{SNOUT}" stroke="{OL}" stroke-width="{max(3.6, 4.6*s):.1f}"/>'
            f'<ellipse cx="{cx + 32*s:.1f}" cy="{cy_base - 46*s:.1f}" rx="{14*s:.1f}" ry="{10*s:.1f}" fill="{SNOUT}" stroke="{OL}" stroke-width="{max(3.6, 4.6*s):.1f}"/>'
        )
    if extra_head:
        parts.append(extra_head)
    return "".join(parts)


def capy_peek_head(cx, cy, s=0.58, mode="baby", fur=FUR_LT, grip_y=None, look_dx=0.0, look_dy=0.0) -> str:
    """Extra-cute round baby Capybara head peeking over a rim (with optional gripping paws drawn AFTER rim!)."""
    sw = max(4.2, 5.8 * min(1.0, s + 0.25))
    return (
        capy_ears(cx, cy, s, fur=fur)
        + f'<ellipse cx="{cx:.1f}" cy="{cy + 6*s:.1f}" rx="{64*s:.1f}" ry="{54*s:.1f}" fill="{fur}" stroke="{OL}" stroke-width="{sw:.1f}"/>'
        + capy_face(cx, cy + 4*s, s * 0.96, mode=mode, look_dx=look_dx, look_dy=look_dy)
    )


def capy_grip_paws(cx, gy, s=0.58, spread=42) -> str:
    sw = max(3.6, 4.8 * min(1.0, s + 0.25))
    return (
        f'<ellipse cx="{cx - spread*s:.1f}" cy="{gy:.1f}" rx="{15*s:.1f}" ry="{10.5*s:.1f}" fill="{SNOUT}" stroke="{OL}" stroke-width="{sw:.1f}"/>'
        f'<ellipse cx="{cx + spread*s:.1f}" cy="{gy:.1f}" rx="{15*s:.1f}" ry="{10.5*s:.1f}" fill="{SNOUT}" stroke="{OL}" stroke-width="{sw:.1f}"/>'
    )


def capy_loaf(cx, cy_base, s=0.72, mode="sleepy", flip=False, fur=FUR, paw_poke=False) -> str:
    """Horizontal squishy Capybara loaf (napping, sniffing, relaxing!)."""
    inner = [
        f'<ellipse cx="-24" cy="-78" rx="11" ry="12.5" transform="rotate(-18 -24 -78)" fill="{fur}" stroke="{OL}" stroke-width="5.2"/>',
        f'<ellipse cx="18" cy="-80" rx="11" ry="12.5" transform="rotate(16 18 -80)" fill="{fur}" stroke="{OL}" stroke-width="5.2"/>',
        f'<path d="M -68,-26 C -72,-66 -48,-86 -6,-86 C 42,-86 76,-64 76,-26 C 76,-4 52,0 0,0 C -50,0 -68,-6 -68,-26 Z" '
        f'fill="{fur}" stroke="{OL}" stroke-width="6.0" stroke-linejoin="round"/>',
        f'<ellipse cx="-44" cy="-6" rx="14" ry="8.5" fill="{SNOUT}" stroke="{OL}" stroke-width="4.5"/>',
        f'<ellipse cx="-4" cy="-5" rx="14" ry="8.5" fill="{SNOUT}" stroke="{OL}" stroke-width="4.5"/>',
        capy_face(-20, -44, s=0.74, mode=mode),
    ]
    if paw_poke:
        inner.append(f'<ellipse cx="-72" cy="-22" rx="15" ry="9.5" transform="rotate(-14 -72 -22)" fill="{SNOUT}" stroke="{OL}" stroke-width="4.5"/>')
    tr = f"translate({cx},{cy_base}) scale({-s if flip else s},{s})"
    return f'<g transform="{tr}">{"".join(inner)}</g>'


def capy_side_sniff(cx, cy_base, s=0.58, fur=FUR_LT, look_right=True) -> str:
    """Adorable tiny baby Capybara in 3/4 side-walk pose sniffing forward!"""
    inner = [
        # Cute stubby back & front legs
        f'<ellipse cx="-30" cy="-6" rx="13" ry="9" fill="{SNOUT}" stroke="{OL}" stroke-width="4.5"/>',
        f'<ellipse cx="26" cy="-6" rx="13" ry="9" fill="{SNOUT}" stroke="{OL}" stroke-width="4.5"/>',
        # Rounded chubby baby loaf body facing right!
        f'<ellipse cx="28" cy="-76" rx="11" ry="12.5" transform="rotate(16 28 -76)" fill="{fur}" stroke="{OL}" stroke-width="5.2"/>',
        f'<path d="M -56,-34 C -58,-68 -32,-82 8,-82 C 44,-82 64,-62 64,-34 C 64,-12 42,-6 2,-6 C -38,-6 -56,-14 -56,-34 Z" '
        f'fill="{fur}" stroke="{OL}" stroke-width="5.8" stroke-linejoin="round"/>',
        f'<ellipse cx="14" cy="-75" rx="10" ry="12" transform="rotate(-14 14 -75)" fill="{fur}" stroke="{OL}" stroke-width="5.0"/>',
        f'<ellipse cx="14" cy="-74" rx="5" ry="6.5" transform="rotate(-14 14 -74)" fill="{EAR_IN}"/>',
        # Side snout & curious big baby eye
        f'<ellipse cx="52" cy="-42" rx="16" ry="14" fill="{SNOUT}"/>',
        f'<ellipse cx="58" cy="-46" rx="2.8" ry="2.2" fill="{OL}"/>',
        f'<path d="M 56,-37 Q 50,-32 45,-36" fill="none" stroke="{OL}" stroke-width="3.2" stroke-linecap="round"/>',
        f'<ellipse cx="32" cy="-54" rx="7.5" ry="8.8" fill="{OL}"/>',
        f'<circle cx="34.5" cy="-56.5" r="3.0" fill="#FFFFFF"/>',
        f'<circle cx="30" cy="-51" r="1.4" fill="#FFFFFF"/>',
        f'<ellipse cx="26" cy="-40" rx="10" ry="6.5" fill="{BLUSH}" fill-opacity="0.72"/>',
    ]
    tr = f"translate({cx},{cy_base}) scale({s if look_right else -s},{s})"
    return f'<g transform="{tr}">{"".join(inner)}</g>'


# =========================================================================== #
#  48. AVOCADO ZEN (Tiny Baby Peeking Over Avocado -> Avocado Zen King!)
# =========================================================================== #
def build_48_avocado() -> list[tuple[str, Image.Image]]:
    skin, lime, flesh, pit, pit_hi, leaf = "#3F6212", "#A3E635", "#ECFCCB", "#854D0E", "#A16207", "#65A30D"

    # S0: Tiny baby Capybara peeking shyly over the rim of a halved green avocado!
    s0 = render_svg("".join([
        shd(150, 266, 74, 11),
        capy_peek_head(150, 108, s=0.52, mode="baby", fur=FUR_LT),
        # Halved green avocado right in front of baby!
        f'<path d="M 150,114 C 186,114 202,148 212,188 C 224,232 198,264 150,264 '
        f'C 102,264 76,232 88,188 C 98,148 114,114 150,114 Z" fill="{skin}" stroke="{OL}" stroke-width="6.2" stroke-linejoin="round"/>',
        f'<path d="M 150,126 C 178,126 192,154 200,190 C 210,226 188,252 150,252 '
        f'C 112,252 90,226 100,190 C 108,154 122,126 150,126 Z" fill="{lime}"/>',
        f'<path d="M 150,136 C 172,136 184,162 192,192 C 200,220 180,242 150,242 '
        f'C 120,242 100,220 108,192 C 116,162 128,136 150,136 Z" fill="{flesh}"/>',
        f'<circle cx="150" cy="204" r="32" fill="{pit}" stroke="{OL}" stroke-width="5"/>',
        f'<ellipse cx="140" cy="193" rx="9" ry="5.5" transform="rotate(-25 140 193)" fill="{pit_hi}" fill-opacity="0.8"/>',
        capy_grip_paws(150, 126, s=0.56, spread=42),
        f'<path d="M 184,132 Q 204,114 212,128 Q 200,140 184,136 Z" fill="{leaf}" stroke="{OL}" stroke-width="4"/>',
    ]))

    # S1: Small baby Capybara curled up napping inside green avocado boat (zzz)
    s1 = render_svg("".join([
        shd(150, 264, 92, 12),
        f'<path d="M 46,198 C 46,160 98,146 164,146 C 226,146 258,170 256,204 C 254,242 212,262 152,262 C 84,262 46,238 46,198 Z" fill="{skin}" stroke="{OL}" stroke-width="6.5"/>',
        f'<path d="M 60,198 C 60,168 106,156 164,156 C 216,156 244,176 242,202 C 240,232 204,248 152,248 C 94,248 60,228 60,198 Z" fill="{lime}"/>',
        f'<path d="M 72,198 C 72,176 114,166 164,166 C 206,166 230,180 230,200 C 228,222 196,236 152,236 C 104,236 72,220 72,198 Z" fill="{flesh}"/>',
        capy_loaf(150, 224, s=0.84, mode="sleepy", fur=FUR),
        zzz_svg(206, 98, 1.05),
    ]))

    # S2: Growing sitting Capybara balancing cute mini halved avocado snugly on head (2 natural paws!)
    head_avo = (
        '<g transform="translate(0,24)">'
        f'<path d="M 150,36 C 169,36 180,58 182,81 C 184,100 169,112 150,112 C 131,112 116,100 118,81 C 120,58 131,36 150,36 Z" fill="{skin}" stroke="{OL}" stroke-width="5.2"/>'
        f'<path d="M 150,45 C 163,45 172,64 173,81 C 174,94 163,102 150,102 C 137,102 126,94 127,81 C 128,64 137,45 150,45 Z" fill="{lime}"/>'
        f'<path d="M 150,53 C 160,53 167,68 167,81 C 167,90 160,96 150,96 C 140,96 133,90 133,81 C 133,68 140,53 150,53 Z" fill="{flesh}"/>'
        f'<circle cx="150" cy="83" r="12" fill="{pit}" stroke="{OL}" stroke-width="3.6"/>'
        f'<path d="M 150,36 Q 167,20 179,32 Q 167,43 150,39 Z" fill="{leaf}" stroke="{OL}" stroke-width="3.6"/>'
        '</g>'
    )
    s2 = render_svg(shd(150, 266, 74, 11) + capy_sit(150, 262, s=0.84, mode="normal", extra_head=head_avo))

    # S3: Chubby Capybara sitting happily hugging a plump smiling kawaii avocado!
    hug_avo = (
        f'<path d="M 150,164 C 173,164 186,188 190,216 C 194,242 175,260 150,260 C 125,260 106,242 110,216 C 114,188 127,164 150,164 Z" fill="{skin}" stroke="{OL}" stroke-width="5.4"/>'
        f'<path d="M 150,174 C 168,174 178,194 180,216 C 182,236 168,250 150,250 C 132,250 118,236 120,216 C 122,194 132,174 150,174 Z" fill="{lime}"/>'
        f'<path d="M 150,182 C 164,182 172,198 173,216 C 174,230 164,242 150,242 C 136,242 126,230 127,216 C 128,198 136,182 150,182 Z" fill="{flesh}"/>'
        f'<circle cx="150" cy="224" r="17" fill="{pit}" stroke="{OL}" stroke-width="3.8"/>'
        f'<circle cx="140" cy="196" r="2.8" fill="{OL}"/><circle cx="160" cy="196" r="2.8" fill="{OL}"/>'
        f'<path d="M 145,200 Q 150,205 155,200" fill="none" stroke="{OL}" stroke-width="2.6" stroke-linecap="round"/>'
    )
    s3 = render_svg(shd(150, 267, 82, 12) + capy_sit(150, 263, s=0.92, mode="happy", extra_belly=hug_avo, paws="hug") + heart(228, 96, 13))

    # S4: Fluffy Capybara wearing cozy green avocado onesie with brown pit tummy!
    s4 = render_svg("".join([
        shd(150, 268, 84, 13),
        f'<path d="M 150,54 Q 128,30 118,46 Q 128,60 150,58 Z" fill="{leaf}" stroke="{OL}" stroke-width="4.5" stroke-linejoin="round"/>',
        f'<path d="M 150,54 Q 172,30 184,46 Q 174,60 150,58 Z" fill="#84CC16" stroke="{OL}" stroke-width="4.5" stroke-linejoin="round"/>',
        f'<path d="M 150,56 C 204,56 232,100 232,162 C 232,226 206,262 150,262 C 94,262 68,226 68,162 C 68,100 96,56 150,56 Z" fill="{skin}" stroke="{OL}" stroke-width="6.5"/>',
        f'<path d="M 150,68 C 194,68 218,106 218,162 C 218,216 196,248 150,248 C 104,248 82,216 82,162 C 82,106 106,68 150,68 Z" fill="{lime}"/>',
        f'<ellipse cx="150" cy="212" rx="52" ry="38" fill="{flesh}" stroke="{OL}" stroke-width="4"/>',
        f'<circle cx="150" cy="216" r="22" fill="{pit}" stroke="{OL}" stroke-width="4.5"/>',
        f'<ellipse cx="143" cy="208" rx="6" ry="4" transform="rotate(-25 143 208)" fill="{pit_hi}"/>',
        f'<ellipse cx="150" cy="128" rx="54" ry="44" fill="{FUR}" stroke="{OL}" stroke-width="5.5"/>',
        f'<path d="M 150,172 Q 134,166 132,178 Q 140,184 150,176 Q 160,184 168,178 Q 166,166 150,172 Z" fill="{leaf}" stroke="{OL}" stroke-width="3.5"/>',
        capy_face(150, 124, s=0.84, mode="normal"),
        f'<ellipse cx="102" cy="198" rx="15" ry="11" transform="rotate(20 102 198)" fill="{SNOUT}" stroke="{OL}" stroke-width="4.8"/>',
        f'<ellipse cx="198" cy="198" rx="15" ry="11" transform="rotate(-20 198 198)" fill="{SNOUT}" stroke="{OL}" stroke-width="4.8"/>',
        f'<ellipse cx="114" cy="258" rx="17" ry="11" fill="{SNOUT}" stroke="{OL}" stroke-width="5"/>',
        f'<ellipse cx="186" cy="258" rx="17" ry="11" fill="{SNOUT}" stroke="{OL}" stroke-width="5"/>',
        sp4(58, 80, 11, "#FDE047", "#B45309"),
        sp4(242, 84, 10, "#BEF264", "#3F6212"),
    ]))

    # S5: Big Avocado Zen King Capybara lounging in lush avocado boat + sprout crown + avocado heart!
    s5_raw = render_svg("".join([
        shd(150, 270, 104, 13, 0.16),
        f'<path d="M 28,204 C 30,158 90,148 150,148 C 210,148 270,158 272,204 C 272,248 220,268 150,268 C 80,268 28,248 28,204 Z" fill="{skin}" stroke="{OL}" stroke-width="6.5"/>',
        f'<path d="M 42,202 C 44,166 98,158 150,158 C 202,158 256,166 258,202 C 258,236 212,254 150,254 C 88,254 42,236 42,202 Z" fill="{lime}"/>',
        f'<path d="M 58,200 C 60,174 104,166 150,166 C 196,166 240,174 242,200 C 242,226 204,242 150,242 C 96,242 58,226 58,200 Z" fill="{flesh}"/>',
        capy_sit(150, 232, s=0.96, mode="happy", feet=False,
                 extra_belly=(
                     f'<rect x="122" y="176" width="56" height="46" rx="12" fill="#D97706" stroke="{OL}" stroke-width="4.5"/>'
                     f'<rect x="128" y="182" width="44" height="34" rx="8" fill="#FEF3C7"/>'
                     f'<rect x="132" y="186" width="36" height="26" rx="6" fill="{lime}"/>'
                     + heart(150, 199, 10, "#FB7185", OL, 2.5)
                     + f'<ellipse cx="118" cy="202" rx="14" ry="10" fill="{SNOUT}" stroke="{OL}" stroke-width="4.5"/>'
                     + f'<ellipse cx="182" cy="202" rx="14" ry="10" fill="{SNOUT}" stroke="{OL}" stroke-width="4.5"/>'
                 ),
                 extra_head=(
                     f'<path d="M 120,84 L 114,50 L 137,66 L 150,40 L 163,66 L 186,50 L 180,84 Z" fill="#FACC15" stroke="{OL}" stroke-width="4.8" stroke-linejoin="round"/>'
                     f'<circle cx="150" cy="68" r="6.5" fill="{leaf}" stroke="{OL}" stroke-width="2.8"/>'
                     f'<circle cx="131" cy="72" r="4.5" fill="#FB7185"/><circle cx="169" cy="72" r="4.5" fill="#FB7185"/>'
                 )),
        sp4(48, 68, 13, "#FDE047", "#B45309"),
        sp4(252, 74, 12, "#FDE047", "#B45309"),
        sp4(38, 146, 9, "#BEF264", "#3F6212"),
        sp4(262, 148, 10, "#FDA4AF", "#9F1239"),
        heart(226, 114, 10),
    ]))
    s5 = with_hero_aura(s5_raw, (190, 242, 100), 165)

    return [
        ("Baby Peek",      s0),
        ("Avocado Boat",   s1),
        ("Head Avocado",   s2),
        ("Avocado Hug",    s3),
        ("Avocado Onesie", s4),
        ("Avocado King!",  s5),
    ]


# =========================================================================== #
#  49. YUZU ONSEN SPA (100% Continuous Wooden Hinoki Tub + Yuzu Story!)
# =========================================================================== #
def _onsen_tub_back(cx=150, top_y=168, w=172, h=92) -> str:
    rx = w / 2
    return (
        f'<ellipse cx="{cx}" cy="{top_y}" rx="{rx}" ry="24" fill="#A16236" stroke="{OL}" stroke-width="6"/>'
        f'<ellipse cx="{cx}" cy="{top_y + 2}" rx="{rx - 10}" ry="17" fill="#BAE6FD" stroke="{OL}" stroke-width="3.5"/>'
        f'<ellipse cx="{cx}" cy="{top_y + 4}" rx="{rx - 20}" ry="12" fill="#E0F2FE"/>'
    )


def _onsen_tub_front(cx=150, top_y=168, w=172, h=92, towel=False) -> str:
    rx = w / 2
    bot_y = top_y + h
    parts = [
        # Front wooden barrel arc
        f'<path d="M {cx - rx:.1f},{top_y} L {cx - rx + 14:.1f},{bot_y - 12} '
        f'Q {cx},{bot_y + 12} {cx + rx - 14:.1f},{bot_y - 12} L {cx + rx:.1f},{top_y} '
        f'A {rx} 24 0 0 1 {cx - rx:.1f},{top_y} Z" fill="#C68550" stroke="{OL}" stroke-width="6.2" stroke-linejoin="round"/>',
        # Barrel metal/bamboo bands
        f'<path d="M {cx - rx + 5:.1f},{top_y + 34} Q {cx},{top_y + 52} {cx + rx - 5:.1f},{top_y + 34}" fill="none" stroke="#8C532A" stroke-width="6"/>',
        f'<path d="M {cx - rx + 10:.1f},{top_y + 64} Q {cx},{top_y + 82} {cx + rx - 10:.1f},{top_y + 64}" fill="none" stroke="#8C532A" stroke-width="6"/>',
        # Vertical plank lines
        f'<line x1="{cx - 44}" y1="{top_y + 21}" x2="{cx - 38}" y2="{bot_y - 4}" stroke="{OL}" stroke-width="3.2"/>',
        f'<line x1="{cx}" y1="{top_y + 24}" x2="{cx}" y2="{bot_y}" stroke="{OL}" stroke-width="3.2"/>',
        f'<line x1="{cx + 44}" y1="{top_y + 21}" x2="{cx + 38}" y2="{bot_y - 4}" stroke="{OL}" stroke-width="3.2"/>',
    ]
    if towel:
        parts.append(
            f'<path d="M {cx + rx - 46:.1f},{top_y + 10} Q {cx + rx - 14:.1f},{top_y + 6} {cx + rx - 12:.1f},{top_y + 26} '
            f'L {cx + rx - 14:.1f},{top_y + 68} Q {cx + rx - 30:.1f},{top_y + 74} {cx + rx - 46:.1f},{top_y + 66} Z" '
            f'fill="#FFFFFF" stroke="{OL}" stroke-width="4.8" stroke-linejoin="round"/>'
            f'<line x1="{cx + rx - 44:.1f}" y1="{top_y + 54}" x2="{cx + rx - 16:.1f}" y2="{top_y + 56}" stroke="#FB923C" stroke-width="4"/>'
        )
    return "".join(parts)


def _yuzu(cx, cy, r=16) -> str:
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#FB923C" stroke="{OL}" stroke-width="4.2"/>'
        f'<ellipse cx="{cx - r*0.3:.1f}" cy="{cy - r*0.3:.1f}" rx="{r*0.28:.1f}" ry="{r*0.18:.1f}" transform="rotate(-25 {cx - r*0.3:.1f} {cy - r*0.3:.1f})" fill="#FEF08A" fill-opacity="0.75"/>'
        f'<path d="M {cx},{cy - r} Q {cx + r*0.8:.1f},{cy - r*1.45:.1f} {cx + r*0.95:.1f},{cy - r*0.85:.1f} Q {cx + r*0.5:.1f},{cy - r*0.7:.1f} {cx},{cy - r*0.9:.1f} Z" fill="#65A30D" stroke="{OL}" stroke-width="2.6"/>'
    )


def _steam(pts: list[tuple[int, int]]) -> str:
    return "".join(
        f'<path d="M {x},{y} Q {x - 8},{y - 18} {x + 4},{y - 34}" fill="none" stroke="#93C5FD" stroke-width="5.2" stroke-linecap="round" stroke-opacity="0.85"/>'
        for x, y in pts
    )


def build_49_onsen() -> list[tuple[str, Image.Image]]:
    # S0: Tiny baby Capybara standing on tiptoes peeking over a steaming wooden onsen tub (tiny yuzu on rim!)
    s0 = render_svg("".join([
        shd(150, 266, 86, 12),
        _steam([(100, 146), (204, 144)]),
        _onsen_tub_back(150, 174, 174, 86),
        capy_peek_head(144, 144, s=0.52, mode="baby", fur=FUR_LT),
        _onsen_tub_front(150, 174, 174, 86),
        capy_grip_paws(144, 172, s=0.55, spread=36),
        _yuzu(206, 166, 14),
    ]))

    # S1: Small Capybara perched on wooden tub edge with folded white towel on head, dipping tiny paw in water!
    s1_towel = f'<rect x="122" y="88" width="44" height="16" rx="7" fill="#FFFFFF" stroke="{OL}" stroke-width="4.2"/>'
    s1 = render_svg("".join([
        shd(150, 266, 92, 12),
        _steam([(92, 144), (218, 140)]),
        _onsen_tub_back(150, 174, 184, 88),
        _yuzu(208, 176, 13),
        capy_sit(144, 186, s=0.62, mode="curious", feet=False, extra_head=s1_towel, paws="poke_right"),
        # Water splash ripple around dipped paw
        '<ellipse cx="182" cy="176" rx="18" ry="6" fill="none" stroke="#38BDF8" stroke-width="3.2"/>',
        _onsen_tub_front(150, 174, 184, 88),
    ]))

    # S2: Growing Capybara climbing halfway into wooden tub, blushing happily with steam
    s2 = render_svg("".join([
        shd(150, 266, 94, 12),
        _steam([(88, 136), (150, 92), (216, 138)]),
        _onsen_tub_back(150, 172, 192, 90),
        _yuzu(94, 174, 14),
        capy_sit(152, 224, s=0.74, mode="happy", feet=False),
        _onsen_tub_front(150, 172, 192, 90),
        # Cute front paws resting on tub rim
        f'<ellipse cx="118" cy="184" rx="14" ry="9" fill="{SNOUT}" stroke="{OL}" stroke-width="4.4"/>',
        f'<ellipse cx="186" cy="184" rx="14" ry="9" fill="{SNOUT}" stroke="{OL}" stroke-width="4.4"/>',
    ]))

    # S3: Chubby Capybara soaking contentedly in wooden tub with 1 bright orange yuzu on its head!
    s3 = render_svg("".join([
        shd(150, 268, 98, 12),
        _steam([(76, 132), (226, 130)]),
        _onsen_tub_back(150, 170, 204, 92),
        _yuzu(94, 174, 14),
        capy_sit(150, 232, s=0.86, mode="bliss", feet=False, extra_head=_yuzu(150, 90, 20)),
        _onsen_tub_front(150, 170, 204, 92),
    ]))

    # S4: Cozy soaking Capybara in steaming tub holding warm cup of yuzu tea with floating yuzus!
    tea_cup = (
        f'<path d="M 134,158 L 138,186 Q 150,192 162,186 L 166,158 Z" fill="#FEF3C7" stroke="{OL}" stroke-width="4.2"/>'
        f'<path d="M 164,164 C 176,164 176,178 164,178" fill="none" stroke="{OL}" stroke-width="4"/>'
        f'<ellipse cx="150" cy="158" rx="16" ry="5" fill="#FDBA74" stroke="{OL}" stroke-width="3.5"/>'
        f'<ellipse cx="128" cy="176" rx="13" ry="9" fill="{SNOUT}" stroke="{OL}" stroke-width="4.2"/>'
        f'<ellipse cx="172" cy="176" rx="13" ry="9" fill="{SNOUT}" stroke="{OL}" stroke-width="4.2"/>'
    )
    s4 = render_svg("".join([
        shd(150, 268, 102, 13),
        _steam([(72, 124), (230, 122)]),
        _onsen_tub_back(150, 170, 214, 94),
        _yuzu(82, 172, 14),
        _yuzu(216, 174, 13),
        capy_sit(150, 238, s=0.92, mode="happy", feet=False, extra_belly=tea_cup, extra_head=_yuzu(150, 86, 19)),
        _onsen_tub_front(150, 170, 214, 94, towel=True),
    ]))

    # S5: Grand Yuzu Onsen Paradise: Big rosy Capybara, stacked yuzus on head, towel, mini duck & sparkles!
    mini_duck = (
        f'<ellipse cx="78" cy="170" rx="15" ry="11" fill="#FDE047" stroke="{OL}" stroke-width="3.8"/>'
        f'<circle cx="84" cy="156" r="10.5" fill="#FDE047" stroke="{OL}" stroke-width="3.8"/>'
        f'<ellipse cx="94" cy="158" rx="5.2" ry="3.4" fill="#FB923C" stroke="{OL}" stroke-width="2.6"/>'
        f'<circle cx="86" cy="154" r="2.2" fill="{OL}"/>'
    )
    s5_raw = render_svg("".join([
        shd(150, 270, 110, 13, 0.16),
        _steam([(60, 118), (242, 118)]),
        _onsen_tub_back(150, 168, 230, 98),
        capy_sit(152, 244, s=1.02, mode="bliss", feet=False,
                 extra_head=_yuzu(152, 82, 20) + _yuzu(152, 50, 13)),
        mini_duck,
        _yuzu(212, 174, 14),
        _onsen_tub_front(150, 168, 230, 98, towel=True),
        sp4(46, 66, 13, "#FDE047", "#C2410C"),
        sp4(254, 70, 12, "#FDBA74", "#C2410C"),
        heart(232, 112, 11, "#FB7185"),
    ]))
    s5 = with_hero_aura(s5_raw, (253, 186, 116), 165)

    return [
        ("Baby Peek",     s0),
        ("Dip Toe",       s1),
        ("Hopping In",    s2),
        ("Yuzu Head",     s3),
        ("Onsen Tea",     s4),
        ("Yuzu Paradise", s5),
    ]


# =========================================================================== #
#  51. BOBA LILY POND (100% Continuous Lily Pad + Strawberry Boba Pond!)
# =========================================================================== #
def _lily_pad(cx=150, cy=242, rx=104, ry=28) -> str:
    return (
        f'<ellipse cx="{cx}" cy="{cy + 8}" rx="{rx + 18}" ry="{ry + 7}" fill="#BAE6FD" fill-opacity="0.72"/>'
        f'<ellipse cx="{cx}" cy="{cy + 6}" rx="{rx + 8}" ry="{ry + 3}" fill="#7DD3FC" fill-opacity="0.55"/>'
        f'<path d="M {cx - rx},{cy} C {cx - rx},{cy - ry} {cx - rx*0.3:.1f},{cy - ry*1.1:.1f} {cx + 12},{cy - ry*0.95:.1f} '
        f'L {cx - 6},{cy - 2} L {cx + 34},{cy - ry*0.85:.1f} '
        f'C {cx + rx*0.85:.1f},{cy - ry*0.65:.1f} {cx + rx},{cy - ry*0.2:.1f} {cx + rx},{cy + 2} '
        f'C {cx + rx},{cy + ry} {cx + rx*0.5:.1f},{cy + ry*1.05:.1f} {cx},{cy + ry*1.05:.1f} '
        f'C {cx - rx*0.6:.1f},{cy + ry*1.05:.1f} {cx - rx},{cy + ry*0.75:.1f} {cx - rx},{cy} Z" '
        f'fill="#4ADE80" stroke="{OL}" stroke-width="5.8" stroke-linejoin="round"/>'
    )


def _boba_cup(cx, cy_bot, s=1.0, tilt=0) -> str:
    w_top, w_bot, h = 64 * s, 48 * s, 90 * s
    y_top = cy_bot - h
    pearls = "".join(
        f'<circle cx="{cx + dx*s:.1f}" cy="{cy_bot - dy*s:.1f}" r="{6.2*s:.1f}" fill="{OL}"/>'
        for dx, dy in [(-14, 14), (0, 11), (14, 14), (-7, 26), (8, 26)]
    )
    inner = (
        # Blue straw
        f'<path d="M {cx - 3*s:.1f},{y_top} L {cx + 3*s:.1f},{y_top - 42*s:.1f} L {cx + 14*s:.1f},{y_top - 40*s:.1f} L {cx + 8*s:.1f},{y_top} Z" fill="#7DD3FC" stroke="{OL}" stroke-width="{max(3.2, 4.0*s):.1f}" stroke-linejoin="round"/>'
        # Cup body
        f'<path d="M {cx - w_top/2:.1f},{y_top} L {cx - w_bot/2:.1f},{cy_bot} Q {cx},{cy_bot + 10*s:.1f} {cx + w_bot/2:.1f},{cy_bot} L {cx + w_top/2:.1f},{y_top} Z" fill="#FDF2F8" stroke="{OL}" stroke-width="{max(4.0, 5.2*s):.1f}" stroke-linejoin="round"/>'
        # Pink strawberry milk wave
        f'<path d="M {cx - w_top*0.45:.1f},{y_top + 28*s:.1f} Q {cx - 12*s:.1f},{y_top + 22*s:.1f} {cx},{y_top + 28*s:.1f} Q {cx + 12*s:.1f},{y_top + 34*s:.1f} {cx + w_top*0.45:.1f},{y_top + 28*s:.1f} L {cx + w_bot/2 - 2:.1f},{cy_bot - 2} Q {cx},{cy_bot + 7*s:.1f} {cx - w_bot/2 + 2:.1f},{cy_bot - 2} Z" fill="#F9A8D4"/>'
        + pearls +
        # Lid
        f'<ellipse cx="{cx}" cy="{y_top}" rx="{w_top/2 + 3*s:.1f}" ry="{9*s:.1f}" fill="#E0F2FE" stroke="{OL}" stroke-width="{max(3.6, 4.8*s):.1f}"/>'
    )
    return f'<g transform="rotate({tilt} {cx} {cy_bot})">{inner}</g>' if tilt else inner


def _lotus_flower(cx, cy, s=1.0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) scale({s})">'
        f'<path d="M 0,10 C -26,8 -34,-12 -18,-22 C -12,-10 -6,-2 0,10 Z" fill="#F472B6" stroke="{OL}" stroke-width="3.8" stroke-linejoin="round"/>'
        f'<path d="M 0,10 C 26,8 34,-12 18,-22 C 12,-10 6,-2 0,10 Z" fill="#F472B6" stroke="{OL}" stroke-width="3.8" stroke-linejoin="round"/>'
        f'<path d="M 0,12 C -16,0 -18,-24 0,-34 C 18,-24 16,0 0,12 Z" fill="#FBCFE8" stroke="{OL}" stroke-width="4.0" stroke-linejoin="round"/>'
        f'<circle cx="0" cy="-4" r="6" fill="#FDE047" stroke="{OL}" stroke-width="2.6"/>'
        f'</g>'
    )


def build_51_boba_pond() -> list[tuple[str, Image.Image]]:
    # S0: Tiny baby Capybara sitting small on green lily pad staring up in awe at a tall pink boba cup!
    s0 = render_svg("".join([
        _lily_pad(150, 238, 102, 26),
        capy_sit(104, 240, s=0.52, mode="baby", fur=FUR_LT, look_dx=4, look_dy=-4),
        _boba_cup(192, 238, s=1.05),
        sp4(234, 114, 9, "#F9A8D4", "#DB2777"),
    ]))

    # S1: Small Capybara hugging pink boba cup tightly on lily pad reaching for straw!
    s1 = render_svg("".join([
        _lily_pad(150, 240, 104, 26),
        capy_sit(132, 244, s=0.66, mode="normal", look_dx=3, look_dy=-3),
        _boba_cup(178, 242, s=0.92, tilt=-8),
        f'<ellipse cx="160" cy="196" rx="13" ry="9" transform="rotate(-18 160 196)" fill="{SNOUT}" stroke="{OL}" stroke-width="4.2"/>',
    ]))

    # S2: Growing Capybara taking first joyful sip through straw on gentle blue ripples!
    s2 = render_svg("".join([
        _lily_pad(150, 240, 108, 27),
        capy_sit(150, 246, s=0.76, mode="sip",
                 extra_belly=_boba_cup(150, 256, s=0.64) + f'<ellipse cx="124" cy="222" rx="13" ry="9" fill="{SNOUT}" stroke="{OL}" stroke-width="4.4"/><ellipse cx="176" cy="222" rx="13" ry="9" fill="{SNOUT}" stroke="{OL}" stroke-width="4.4"/>'),
        heart(218, 128, 11, "#F472B6"),
    ]))

    # S3: Chubby Capybara paddling happily on lily pad holding boba cup with floating pearls & pink bubbles!
    s3 = render_svg("".join([
        _lily_pad(150, 242, 112, 28),
        capy_sit(144, 246, s=0.84, mode="happy",
                 extra_belly=_boba_cup(184, 250, s=0.72, tilt=6) + f'<ellipse cx="162" cy="216" rx="13" ry="9" fill="{SNOUT}" stroke="{OL}" stroke-width="4.4"/><ellipse cx="100" cy="216" rx="14" ry="9" transform="rotate(24 100 216)" fill="{SNOUT}" stroke="{OL}" stroke-width="4.4"/>'),
        '<circle cx="72" cy="148" r="10" fill="#FBCFE8" stroke="#DB2777" stroke-width="2.6"/>',
        '<circle cx="90" cy="118" r="6" fill="#E0F2FE" stroke="#0284C7" stroke-width="2.2"/>',
        '<circle cx="228" cy="134" r="9" fill="#FBCFE8" stroke="#DB2777" stroke-width="2.6"/>',
    ]))

    # S4: Relaxed Capybara lounging under a blooming pink lotus blossom on lily pad sipping creamy boba!
    s4 = render_svg("".join([
        _lily_pad(150, 244, 116, 28),
        # Tall curved lotus blossom umbrella stem behind capybara!
        f'<path d="M 218,240 Q 238,140 166,78" fill="none" stroke="#16A34A" stroke-width="8" stroke-linecap="round"/>',
        f'<path d="M 218,240 Q 238,140 166,78" fill="none" stroke="{OL}" stroke-width="3" stroke-linecap="round"/>',
        _lotus_flower(160, 76, 1.35),
        capy_sit(144, 248, s=0.92, mode="sip",
                 extra_belly=_boba_cup(144, 258, s=0.68) + f'<ellipse cx="116" cy="222" rx="14" ry="10" fill="{SNOUT}" stroke="{OL}" stroke-width="4.6"/><ellipse cx="172" cy="222" rx="14" ry="10" fill="{SNOUT}" stroke="{OL}" stroke-width="4.6"/>'),
        _lotus_flower(76, 232, 0.72),
    ]))

    # S5: Boba Lily Pond Royalty: Big happy Capybara on grand blooming lily pad with jumbo sparkling strawberry-boba!
    s5_raw = render_svg("".join([
        _lily_pad(150, 244, 124, 30),
        capy_sit(150, 248, s=1.02, mode="happy",
                 extra_head=_lotus_flower(150, 82, 0.95),
                 extra_belly=_boba_cup(150, 260, s=0.74) + f'<ellipse cx="116" cy="222" rx="15" ry="10.5" fill="{SNOUT}" stroke="{OL}" stroke-width="4.8"/><ellipse cx="184" cy="222" rx="15" ry="10.5" fill="{SNOUT}" stroke="{OL}" stroke-width="4.8"/>'),
        _lotus_flower(62, 230, 0.85),
        _lotus_flower(238, 228, 0.85),
        sp4(48, 76, 13, "#FDE047", "#0284C7"),
        sp4(252, 78, 12, "#F9A8D4", "#DB2777"),
        heart(224, 124, 12, "#F472B6"),
        heart(74, 126, 10, "#38BDF8"),
    ]))
    s5 = with_hero_aura(s5_raw, (125, 211, 252), 162)

    return [
        ("Baby & Boba",    s0),
        ("Boba Hug",       s1),
        ("First Sip",      s2),
        ("Pond Bubbles",   s3),
        ("Lotus Shade",    s4),
        ("Boba Royalty!",  s5),
    ]


# =========================================================================== #
#  52. BOOKWORM STUDY (100% Continuous Book Tower Scholar Story!)
# =========================================================================== #
def _book_flat(cx, cy_bot, w=156, h=34, cover="#F59E0B", pages="#FFFBEB", ribbon=None) -> str:
    x0 = cx - w / 2
    y0 = cy_bot - h
    out = (
        f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w}" height="{h}" rx="8" fill="{cover}" stroke="{OL}" stroke-width="5.2"/>'
        f'<rect x="{x0 + 18:.1f}" y="{y0 + 7:.1f}" width="{w - 28:.1f}" height="{h - 14:.1f}" rx="3" fill="{pages}" stroke="{OL}" stroke-width="3.0"/>'
    )
    if ribbon:
        out += f'<polygon points="{x0 + 34:.1f},{cy_bot - 12} {x0 + 48:.1f},{cy_bot - 12} {x0 + 48:.1f},{cy_bot + 16} {x0 + 41:.1f},{cy_bot + 8} {x0 + 34:.1f},{cy_bot + 16}" fill="{ribbon}" stroke="{OL}" stroke-width="3.0"/>'
    return out


def _open_book(cx, cy_bot, s=1.0, cover="#FACC15") -> str:
    return (
        f'<g transform="translate({cx},{cy_bot}) scale({s})">'
        f'<path d="M 0,0 Q -36,-10 -66,-2 L -60,-46 Q -30,-54 0,-42 Q 30,-54 60,-46 L 66,-2 Q 36,-10 0,0 Z" fill="{cover}" stroke="{OL}" stroke-width="5.2" stroke-linejoin="round"/>'
        f'<path d="M 0,-5 Q -32,-14 -56,-7 L -52,-42 Q -26,-48 0,-38 Q 26,-48 52,-42 L 56,-7 Q 32,-14 0,-5 Z" fill="#FFFDF5" stroke="{OL}" stroke-width="3.2" stroke-linejoin="round"/>'
        f'<line x1="0" y1="-38" x2="0" y2="-5" stroke="{OL}" stroke-width="3.2"/>'
        f'<line x1="-42" y1="-30" x2="-12" y2="-26" stroke="#D6C4A8" stroke-width="3" stroke-linecap="round"/>'
        f'<line x1="-42" y1="-20" x2="-14" y2="-16" stroke="#D6C4A8" stroke-width="3" stroke-linecap="round"/>'
        f'<line x1="12" y1="-26" x2="42" y2="-30" stroke="#D6C4A8" stroke-width="3" stroke-linecap="round"/>'
        f'<line x1="14" y1="-16" x2="42" y2="-20" stroke="#D6C4A8" stroke-width="3" stroke-linecap="round"/>'
        f'</g>'
    )


def _glasses(cx, cy, s=1.0) -> str:
    ex = 30 * s * 0.94
    return (
        f'<circle cx="{cx - ex:.1f}" cy="{cy:.1f}" r="{15*s:.1f}" fill="#FFFFFF" fill-opacity="0.32" stroke="{OL}" stroke-width="{3.6*s:.1f}"/>'
        f'<circle cx="{cx + ex:.1f}" cy="{cy:.1f}" r="{15*s:.1f}" fill="#FFFFFF" fill-opacity="0.32" stroke="{OL}" stroke-width="{3.6*s:.1f}"/>'
        f'<line x1="{cx - ex + 15*s:.1f}" y1="{cy:.1f}" x2="{cx + ex - 15*s:.1f}" y2="{cy:.1f}" stroke="{OL}" stroke-width="{3.6*s:.1f}"/>'
    )


def _pencil(cx, cy, rot=-35, s=1.0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot}) scale({s})">'
        f'<rect x="-7" y="-26" width="14" height="44" rx="2" fill="#FACC15" stroke="{OL}" stroke-width="3.6"/>'
        f'<rect x="-7" y="-34" width="14" height="10" rx="3" fill="#F472B6" stroke="{OL}" stroke-width="3.4"/>'
        f'<polygon points="-7,18 7,18 0,32" fill="#FDE68A" stroke="{OL}" stroke-width="3.4" stroke-linejoin="round"/>'
        f'<polygon points="-2.5,27 2.5,27 0,32" fill="{OL}"/>'
        f'</g>'
    )


def build_52_bookworm() -> list[tuple[str, Image.Image]]:
    # S0: Tiny baby Capybara resting chin on 1 closed golden book with pencil beside it!
    s0 = render_svg("".join([
        shd(150, 266, 94, 12),
        capy_peek_head(144, 198, s=0.52, mode="baby", fur=FUR_LT),
        _book_flat(144, 262, 168, 38, "#F59E0B", "#FFFBEB", "#EF4444"),
        capy_grip_paws(144, 224, s=0.54, spread=38),
        _pencil(236, 232, rot=24, s=0.85),
    ]))

    # S1: Small Capybara opening book wide on floor & reading curiously!
    s1 = render_svg("".join([
        shd(150, 266, 94, 12),
        capy_sit(150, 250, s=0.66, mode="curious", look_dy=3),
        _open_book(150, 264, s=1.05, cover="#F59E0B"),
        f'<ellipse cx="118" cy="236" rx="12" ry="8" fill="{SNOUT}" stroke="{OL}" stroke-width="4.0"/>',
        f'<ellipse cx="182" cy="236" rx="12" ry="8" fill="{SNOUT}" stroke="{OL}" stroke-width="4.0"/>',
    ]))

    # S2: Growing Capybara wearing cute round study glasses jotting notes with pencil on open book!
    s2 = render_svg("".join([
        shd(150, 266, 96, 12),
        capy_sit(146, 250, s=0.76, mode="normal", extra_head=_glasses(146, 180, 0.76)),
        _open_book(146, 264, s=1.12, cover="#38BDF8"),
        _pencil(196, 222, rot=32, s=0.9),
        f'<ellipse cx="116" cy="234" rx="13" ry="8.5" fill="{SNOUT}" stroke="{OL}" stroke-width="4.2"/>',
        f'<ellipse cx="182" cy="232" rx="13" ry="8.5" fill="{SNOUT}" stroke="{OL}" stroke-width="4.2"/>',
    ]))

    # S3: Chubby Capybara sitting atop 2 stacked pastel books reading calmly with bookmark ribbon!
    s3 = render_svg("".join([
        shd(150, 268, 96, 12),
        _book_flat(150, 264, 174, 34, "#F59E0B", "#FFFBEB", "#FDE047"),
        _book_flat(150, 230, 160, 32, "#F472B6", "#FFF1F2"),
        capy_sit(150, 200, s=0.80, mode="happy", extra_head=_glasses(150, 126, 0.80),
                 extra_belly=_open_book(150, 204, s=0.82, cover="#38BDF8") + f'<ellipse cx="122" cy="184" rx="12" ry="8.5" fill="{SNOUT}" stroke="{OL}" stroke-width="4.2"/><ellipse cx="178" cy="184" rx="12" ry="8.5" fill="{SNOUT}" stroke="{OL}" stroke-width="4.2"/>'),
    ]))

    # S4: Dedicated scholar perched on 3 stacked books studying under warm glowing mini desk lamp!
    lamp = (
        '<circle cx="222" cy="136" r="46" fill="#FEF08A" fill-opacity="0.45"/>'
        f'<path d="M 248,258 L 248,154 Q 248,122 220,126" fill="none" stroke="{OL}" stroke-width="6.5" stroke-linecap="round"/>'
        f'<ellipse cx="248" cy="260" rx="22" ry="8" fill="#0284C7" stroke="{OL}" stroke-width="4.5"/>'
        f'<path d="M 200,136 L 222,114 L 238,136 Z" fill="#0284C7" stroke="{OL}" stroke-width="4.5" stroke-linejoin="round"/>'
    )
    s4 = render_svg("".join([
        shd(146, 268, 108, 12),
        lamp,
        _book_flat(134, 264, 164, 30, "#F59E0B", "#FFFBEB", "#FDE047"),
        _book_flat(138, 234, 152, 30, "#F472B6", "#FFF1F2"),
        _book_flat(132, 204, 156, 28, "#38BDF8", "#F0F9FF"),
        capy_sit(134, 178, s=0.82, mode="normal", extra_head=_glasses(134, 102, 0.82),
                 extra_belly=_open_book(134, 182, s=0.84, cover="#FACC15") + f'<ellipse cx="106" cy="164" rx="12" ry="8.5" fill="{SNOUT}" stroke="{OL}" stroke-width="4.2"/><ellipse cx="162" cy="164" rx="12" ry="8.5" fill="{SNOUT}" stroke="{OL}" stroke-width="4.2"/>'),
    ]))

    # S5: "Capy & Chaptered" Master Scholar atop 4 stacked colorful books, glowing golden book, orange on head, daisies & stars!
    s5_raw = render_svg("".join([
        shd(150, 272, 102, 12, 0.16),
        _book_flat(150, 268, 176, 26, "#F59E0B", "#FFFBEB", "#FDE047"),
        _book_flat(154, 242, 166, 26, "#F472B6", "#FFF1F2"),
        _book_flat(146, 216, 168, 25, "#38BDF8", "#F0F9FF"),
        _book_flat(150, 191, 158, 24, "#4ADE80", "#F0FDF4"),
        capy_sit(150, 170, s=0.86, mode="happy",
                 extra_head=_yuzu(150, 32, 17),
                 extra_belly=_open_book(150, 174, s=0.92, cover="#FACC15") + f'<ellipse cx="118" cy="154" rx="13" ry="9" fill="{SNOUT}" stroke="{OL}" stroke-width="4.4"/><ellipse cx="182" cy="154" rx="13" ry="9" fill="{SNOUT}" stroke="{OL}" stroke-width="4.4"/>'),
        daisy(66, 232, 10),
        daisy(234, 192, 10),
        sp4(46, 72, 12, "#FDE047", "#CA8A04"),
        sp4(254, 76, 12, "#FDE047", "#CA8A04"),
        sp4(54, 150, 9, "#38BDF8", "#0369A1"),
        sp4(248, 144, 9, "#F472B6", "#BE185D"),
    ]))
    s5 = with_hero_aura(s5_raw, (254, 240, 138), 152)

    return [
        ("Baby & Book",   s0),
        ("First Read",    s1),
        ("Study Glasses", s2),
        ("Book Stack",    s3),
        ("Lamp Study",    s4),
        ("Chaptered!",    s5),
    ]


# =========================================================================== #
#  53. LOFI PICNIC BEATS (100% Continuous Red Gingham Mat + Blue Headphones!)
# =========================================================================== #
def _gingham_mat(cx=150, cy=236, rx=120, ry=34) -> str:
    return (
        f'<polygon points="{cx},{cy - ry} {cx + rx},{cy} {cx},{cy + ry} {cx - rx},{cy}" fill="#FFFFFF" stroke="{OL}" stroke-width="5.8" stroke-linejoin="round"/>'
        f'<polygon points="{cx},{cy - ry + 6} {cx + rx - 14},{cy} {cx},{cy + ry - 6} {cx - rx + 14},{cy}" fill="#FECACA" fill-opacity="0.72"/>'
        # Crisp gingham stripe bands across diamond
        f'<line x1="{cx - 56}" y1="{cy - 16}" x2="{cx + 56}" y2="{cy + 16}" stroke="#EF4444" stroke-opacity="0.55" stroke-width="10"/>'
        f'<line x1="{cx - 56}" y1="{cy + 16}" x2="{cx + 56}" y2="{cy - 16}" stroke="#EF4444" stroke-opacity="0.55" stroke-width="10"/>'
        f'<polygon points="{cx},{cy - ry} {cx + rx},{cy} {cx},{cy + ry} {cx - rx},{cy}" fill="none" stroke="{OL}" stroke-width="5.8" stroke-linejoin="round"/>'
    )


def _blue_headphones(cx, cy, s=1.0, on_ground=False) -> str:
    if on_ground:
        return (
            f'<g transform="translate({cx},{cy}) scale({s})">'
            f'<path d="M -36,4 C -36,-34 36,-34 36,4" fill="none" stroke="{OL}" stroke-width="13" stroke-linecap="round"/>'
            f'<path d="M -36,4 C -36,-34 36,-34 36,4" fill="none" stroke="#3B82F6" stroke-width="6.5" stroke-linecap="round"/>'
            f'<ellipse cx="-34" cy="10" rx="13" ry="18" transform="rotate(-14 -34 10)" fill="#60A5FA" stroke="{OL}" stroke-width="4.8"/>'
            f'<ellipse cx="34" cy="10" rx="13" ry="18" transform="rotate(14 34 10)" fill="#60A5FA" stroke="{OL}" stroke-width="4.8"/>'
            f'</g>'
        )
    rx = 66 * s
    return (
        f'<path d="M {cx - rx:.1f},{cy + 4*s:.1f} C {cx - rx:.1f},{cy - 76*s:.1f} {cx + rx:.1f},{cy - 76*s:.1f} {cx + rx:.1f},{cy + 4*s:.1f}" '
        f'fill="none" stroke="{OL}" stroke-width="{14*s:.1f}" stroke-linecap="round"/>'
        f'<path d="M {cx - rx:.1f},{cy + 4*s:.1f} C {cx - rx:.1f},{cy - 76*s:.1f} {cx + rx:.1f},{cy - 76*s:.1f} {cx + rx:.1f},{cy + 4*s:.1f}" '
        f'fill="none" stroke="#3B82F6" stroke-width="{7.2*s:.1f}" stroke-linecap="round"/>'
        f'<ellipse cx="{cx - rx:.1f}" cy="{cy + 6*s:.1f}" rx="{15*s:.1f}" ry="{22*s:.1f}" fill="#60A5FA" stroke="{OL}" stroke-width="{4.8*s:.1f}"/>'
        f'<ellipse cx="{cx + rx:.1f}" cy="{cy + 6*s:.1f}" rx="{15*s:.1f}" ry="{22*s:.1f}" fill="#60A5FA" stroke="{OL}" stroke-width="{4.8*s:.1f}"/>'
        f'<ellipse cx="{cx - rx + 4*s:.1f}" cy="{cy + 6*s:.1f}" rx="{6*s:.1f}" ry="{14*s:.1f}" fill="#1E293B"/>'
        f'<ellipse cx="{cx + rx - 4*s:.1f}" cy="{cy + 6*s:.1f}" rx="{6*s:.1f}" ry="{14*s:.1f}" fill="#1E293B"/>'
    )


def _picnic_basket(cx, cy_bot, s=0.72) -> str:
    return (
        f'<g transform="translate({cx},{cy_bot}) scale({s})">'
        f'<path d="M -38,-46 Q 0,-96 38,-46" fill="none" stroke="{OL}" stroke-width="10" stroke-linecap="round"/>'
        f'<path d="M -38,-46 Q 0,-96 38,-46" fill="none" stroke="#D97706" stroke-width="4.5" stroke-linecap="round"/>'
        f'<circle cx="-18" cy="-48" r="14" fill="#EF4444" stroke="{OL}" stroke-width="4"/>'
        f'<circle cx="14" cy="-48" r="14" fill="#FB923C" stroke="{OL}" stroke-width="4"/>'
        f'<circle cx="0" cy="-54" r="12" fill="#84CC16" stroke="{OL}" stroke-width="4"/>'
        f'<path d="M -46,-46 L -36,0 Q 0,8 36,0 L 46,-46 Z" fill="#FCD34D" stroke="{OL}" stroke-width="5.2" stroke-linejoin="round"/>'
        f'<rect x="-50" y="-52" width="100" height="14" rx="6" fill="#D97706" stroke="{OL}" stroke-width="4.8"/>'
        f'</g>'
    )


def build_53_lofi_picnic() -> list[tuple[str, Image.Image]]:
    # S0: Tiny baby Capybara curled small on red gingham mat poking oversized blue headphones!
    s0 = render_svg("".join([
        _gingham_mat(150, 236, 118, 34),
        capy_loaf(116, 236, s=0.58, mode="baby", flip=True, fur=FUR_LT, paw_poke=True),
        _blue_headphones(200, 212, s=0.82, on_ground=True),
    ]))

    # S1: Small Capybara on gingham mat pulling big oversized blue headphones over tiny ears!
    s1 = render_svg("".join([
        _gingham_mat(150, 238, 120, 34),
        capy_sit(150, 240, s=0.66, mode="curious",
                 extra_head=_blue_headphones(150, 174, s=0.82)),
        f'<ellipse cx="102" cy="184" rx="13" ry="9" transform="rotate(-24 102 184)" fill="{SNOUT}" stroke="{OL}" stroke-width="4.2"/>',
        f'<ellipse cx="198" cy="184" rx="13" ry="9" transform="rotate(24 198 184)" fill="{SNOUT}" stroke="{OL}" stroke-width="4.2"/>',
    ]))

    # S2: Growing Capybara wearing blue headphones on picnic mat, eyes closed blissfully + 1 blue music note!
    s2 = render_svg("".join([
        _gingham_mat(150, 238, 122, 34),
        capy_sit(150, 242, s=0.78, mode="bliss",
                 extra_head=_blue_headphones(150, 168, s=0.82)),
        note_svg(220, 96, 1.1, "#2563EB"),
    ]))

    # S3: Chubby Capybara strumming wooden ukulele on gingham mat beside woven picnic basket!
    uke = (
        f'<g transform="translate(174,198) rotate(-26)">'
        f'<rect x="8" y="-6" width="52" height="10" rx="4" fill="#D97706" stroke="{OL}" stroke-width="3.8"/>'
        f'<ellipse cx="-4" cy="0" rx="22" ry="18" fill="#F59E0B" stroke="{OL}" stroke-width="4.4"/>'
        f'<circle cx="-4" cy="0" r="6" fill="#78350F"/>'
        f'</g>'
    )
    s3 = render_svg("".join([
        _gingham_mat(150, 238, 124, 35),
        _picnic_basket(76, 226, 0.56),
        capy_sit(162, 244, s=0.84, mode="happy",
                 extra_head=_blue_headphones(162, 164, s=0.86),
                 extra_belly=uke + f'<ellipse cx="142" cy="204" rx="13" ry="9" fill="{SNOUT}" stroke="{OL}" stroke-width="4.2"/><ellipse cx="196" cy="186" rx="12" ry="8.5" fill="{SNOUT}" stroke="{OL}" stroke-width="4.2"/>'),
        note_svg(234, 88, 0.95, "#EF4444"),
        note_svg(72, 104, 0.85, "#2563EB"),
    ]))

    # S4: Chill Capybara wearing blue headphones on gingham mat opening cozy teal notebook beside basket!
    s4 = render_svg("".join([
        _gingham_mat(150, 240, 126, 35),
        _picnic_basket(76, 228, 0.62),
        capy_sit(166, 246, s=0.90, mode="normal",
                 extra_head=_blue_headphones(166, 162, s=0.92),
                 extra_belly=_open_book(166, 234, s=0.78, cover="#38BDF8") + f'<ellipse cx="136" cy="216" rx="13" ry="9" fill="{SNOUT}" stroke="{OL}" stroke-width="4.4"/><ellipse cx="196" cy="216" rx="13" ry="9" fill="{SNOUT}" stroke="{OL}" stroke-width="4.4"/>'),
        note_svg(238, 86, 1.0, "#2563EB"),
    ]))

    # S5: Ultimate Lofi Picnic Flow: Big relaxed Capybara in blue headphones, teal book, overflowing fruit basket, notes & sparkles!
    s5_raw = render_svg("".join([
        _gingham_mat(150, 242, 130, 36),
        _picnic_basket(74, 232, 0.70),
        capy_sit(168, 248, s=0.98, mode="happy",
                 extra_head=_blue_headphones(168, 158, s=1.00),
                 extra_belly=_open_book(168, 234, s=0.86, cover="#2DD4BF") + f'<ellipse cx="136" cy="214" rx="14" ry="10" fill="{SNOUT}" stroke="{OL}" stroke-width="4.6"/><ellipse cx="200" cy="214" rx="14" ry="10" fill="{SNOUT}" stroke="{OL}" stroke-width="4.6"/>'),
        note_svg(246, 78, 1.05, "#2563EB"),
        note_svg(66, 92, 0.9, "#EF4444"),
        sp4(46, 62, 11, "#FDE047", "#2563EB"),
        sp4(258, 132, 10, "#93C5FD", "#1D4ED8"),
    ]))
    s5 = with_hero_aura(s5_raw, (147, 197, 253), 160)

    return [
        ("Baby Beats",    s0),
        ("Big Ears",      s1),
        ("Lofi Chill",    s2),
        ("Picnic Uke",    s3),
        ("Flow Notes",    s4),
        ("Lofi Picnic!",  s5),
    ]


# =========================================================================== #
#  54. FOODIE SNACK CLUB (Hungry Baby in Bib -> Deluxe Burger Champion!)
# =========================================================================== #
def _bib(cx, cy, s=1.0) -> str:
    return (
        f'<path d="M {cx - 24*s:.1f},{cy} Q {cx},{cy + 8*s:.1f} {cx + 24*s:.1f},{cy} '
        f'C {cx + 30*s:.1f},{cy + 26*s:.1f} {cx + 18*s:.1f},{cy + 36*s:.1f} {cx:.1f},{cy + 36*s:.1f} '
        f'C {cx - 18*s:.1f},{cy + 36*s:.1f} {cx - 30*s:.1f},{cy + 26*s:.1f} {cx - 24*s:.1f},{cy} Z" '
        f'fill="#FFFFFF" stroke="{OL}" stroke-width="{max(3.2, 4.0*s):.1f}" stroke-linejoin="round"/>'
        + heart(cx, cy + 19*s, 7*s, "#FB7185", OL, 2.0)
    )


def build_54_foodie() -> list[tuple[str, Image.Image]]:
    # S0: Tiny baby Capybara in white foodie bib holding mini spoon peeking over empty snack plate!
    plate = (
        f'<ellipse cx="150" cy="248" rx="80" ry="20" fill="#FFFFFF" stroke="{OL}" stroke-width="5.5"/>'
        f'<ellipse cx="150" cy="248" rx="56" ry="12" fill="#FEF3C7" stroke="#E5D5B8" stroke-width="2.6"/>'
    )
    spoon = (
        f'<g transform="translate(212,188) rotate(22)">'
        f'<rect x="-3.5" y="0" width="7" height="36" rx="3" fill="#E2E8F0" stroke="{OL}" stroke-width="3.2"/>'
        f'<ellipse cx="0" cy="-8" rx="9" ry="12" fill="#E2E8F0" stroke="{OL}" stroke-width="3.4"/>'
        f'</g>'
    )
    s0 = render_svg("".join([
        shd(150, 268, 86, 11),
        capy_sit(150, 240, s=0.58, mode="baby", fur=FUR_LT, feet=False, extra_belly=_bib(150, 206, 0.72)),
        plate,
        spoon,
        f'<ellipse cx="116" cy="224" rx="11" ry="8" fill="{SNOUT}" stroke="{OL}" stroke-width="3.8"/>',
        f'<ellipse cx="198" cy="214" rx="11" ry="8" fill="{SNOUT}" stroke="{OL}" stroke-width="3.8"/>',
    ]))

    # S1: Small Capybara in foodie bib happily sipping pink strawberry milk carton!
    milk = (
        f'<g transform="translate(150,236) scale(0.75)">'
        f'<path d="M -28,-54 L 0,-78 L 28,-54 L 28,16 Q 0,24 -28,16 Z" fill="#FFFFFF" stroke="{OL}" stroke-width="5.2" stroke-linejoin="round"/>'
        f'<rect x="-26" y="-54" width="52" height="14" fill="#F9A8D4" stroke="{OL}" stroke-width="3.6"/>'
        f'<rect x="-26" y="-18" width="52" height="34" fill="#FDA4AF"/>'
        f'<path d="M 0,-76 L 0,-104" stroke="#F43F5E" stroke-width="7" stroke-linecap="round"/>'
        + heart(0, -2, 9, "#E11D48") + '</g>'
    )
    s1 = render_svg(shd(150, 266, 78, 11) + capy_sit(150, 260, s=0.70, mode="sip",
                                                      extra_belly=_bib(150, 210, 0.76) + milk + f'<ellipse cx="122" cy="224" rx="13" ry="9" fill="{SNOUT}" stroke="{OL}" stroke-width="4.2"/><ellipse cx="178" cy="224" rx="13" ry="9" fill="{SNOUT}" stroke="{OL}" stroke-width="4.2"/>'))

    # S2: Growing Capybara munching joyfully on juicy red watermelon slice!
    melon = (
        f'<g transform="translate(150,218)">'
        f'<path d="M -46,-10 A 48 48 0 0 0 46,-10 Z" fill="#16A34A" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
        f'<path d="M -38,-10 A 38 38 0 0 0 38,-10 Z" fill="#ECFCCB"/>'
        f'<path d="M -33,-10 A 33 33 0 0 0 33,-10 Z" fill="#EF4444"/>'
        f'<circle cx="-14" cy="4" r="3" fill="{OL}"/><circle cx="0" cy="10" r="3" fill="{OL}"/><circle cx="14" cy="4" r="3" fill="{OL}"/>'
        f'</g>'
    )
    s2 = render_svg(shd(150, 266, 82, 11) + capy_sit(150, 262, s=0.78, mode="munch",
                                                      extra_belly=melon + f'<ellipse cx="110" cy="214" rx="14" ry="9.5" fill="{SNOUT}" stroke="{OL}" stroke-width="4.4"/><ellipse cx="190" cy="214" rx="14" ry="9.5" fill="{SNOUT}" stroke="{OL}" stroke-width="4.4"/>'))

    # S3: Chubby Capybara hugging striped red-and-white popcorn bucket overflowing!
    popcorn = (
        f'<g transform="translate(150,236)">'
        + "".join(f'<circle cx="{px}" cy="{py}" r="{pr}" fill="#FEF08A" stroke="{OL}" stroke-width="3.6"/>'
                  for px, py, pr in [(-24,-42,12), (-8,-48,14), (10,-46,13), (24,-40,12), (-14,-34,11), (4,-34,12), (18,-32,11)]) +
        f'<path d="M -36,-34 L -28,22 Q 0,28 28,22 L 36,-34 Z" fill="#FFFFFF" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
        f'<polygon points="-24,-33 -10,-33 -8,23 -18,22" fill="#EF4444"/>'
        f'<polygon points="10,-33 24,-33 18,22 8,23" fill="#EF4444"/>'
        f'<path d="M -36,-34 L -28,22 Q 0,28 28,22 L 36,-34 Z" fill="none" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
        f'</g>'
    )
    s3 = render_svg(shd(150, 266, 86, 12) + capy_sit(150, 262, s=0.86, mode="happy",
                                                      extra_belly=popcorn + f'<ellipse cx="108" cy="222" rx="14" ry="10" fill="{SNOUT}" stroke="{OL}" stroke-width="4.5"/><ellipse cx="192" cy="222" rx="14" ry="10" fill="{SNOUT}" stroke="{OL}" stroke-width="4.5"/>'))

    # S4: Happy Capybara taking a delighted bite of melty cheesy pepperoni pizza slice!
    pizza = (
        f'<g transform="translate(156,214) rotate(-14)">'
        f'<path d="M -42,-28 Q 0,-42 42,-28 L 0,44 Z" fill="#FACC15" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
        f'<path d="M -44,-26 Q 0,-42 44,-26 Q 40,-14 0,-22 Q -40,-14 -44,-26 Z" fill="#D97706" stroke="{OL}" stroke-width="4.6"/>'
        f'<circle cx="-12" cy="-6" r="8" fill="#EF4444" stroke="{OL}" stroke-width="2.6"/>'
        f'<circle cx="14" cy="-8" r="7.5" fill="#EF4444" stroke="{OL}" stroke-width="2.6"/>'
        f'<circle cx="0" cy="14" r="7" fill="#EF4444" stroke="{OL}" stroke-width="2.6"/>'
        f'</g>'
    )
    s4 = render_svg(shd(150, 267, 88, 12) + capy_sit(150, 263, s=0.92, mode="munch",
                                                      extra_belly=pizza + f'<ellipse cx="114" cy="212" rx="15" ry="10" fill="{SNOUT}" stroke="{OL}" stroke-width="4.6"/><ellipse cx="188" cy="212" rx="15" ry="10" fill="{SNOUT}" stroke="{OL}" stroke-width="4.6"/>') + heart(232, 92, 11))

    # S5: Foodie Feast Champion: Big blissful Capybara sitting proudly atop giant deluxe cheeseburger holding tiny gold flag!
    burger = (
        f'<g transform="translate(150,248)">'
        # Bottom bun
        f'<path d="M -86,0 L 86,0 C 88,18 68,24 0,24 C -68,24 -88,18 -86,0 Z" fill="#F59E0B" stroke="{OL}" stroke-width="5.5"/>'
        # Juicy patty
        f'<rect x="-90" y="-20" width="180" height="22" rx="10" fill="#78350F" stroke="{OL}" stroke-width="5.2"/>'
        # Melty cheese triangles
        f'<path d="M -86,-20 L 86,-20 L 70,-4 L 40,-20 L 6,-2 L -28,-20 L -60,-6 Z" fill="#FACC15" stroke="{OL}" stroke-width="3.8" stroke-linejoin="round"/>'
        # Crisp lettuce & tomato
        f'<path d="M -92,-24 Q -72,-36 -52,-24 Q -32,-36 -12,-24 Q 8,-36 28,-24 Q 48,-36 68,-24 Q 84,-34 92,-24 L 86,-16 L -86,-16 Z" fill="#4ADE80" stroke="{OL}" stroke-width="4.2"/>'
        f'<rect x="-78" y="-36" width="156" height="12" rx="5" fill="#EF4444" stroke="{OL}" stroke-width="4"/>'
        # Fluffy sesame top bun!
        f'<path d="M -88,-34 C -88,-68 -48,-76 0,-76 C 48,-76 88,-68 88,-34 Z" fill="#F59E0B" stroke="{OL}" stroke-width="5.5"/>'
        f'<ellipse cx="-42" cy="-54" rx="5" ry="2.6" transform="rotate(-18 -42 -54)" fill="#FEF3C7"/>'
        f'<ellipse cx="44" cy="-54" rx="5" ry="2.6" transform="rotate(18 44 -54)" fill="#FEF3C7"/>'
        f'</g>'
    )
    flag = (
        f'<line x1="218" y1="138" x2="218" y2="54" stroke="{OL}" stroke-width="4.5" stroke-linecap="round"/>'
        f'<polygon points="218,56 260,70 218,86" fill="#FACC15" stroke="{OL}" stroke-width="4.0" stroke-linejoin="round"/>'
    )
    s5_raw = render_svg("".join([
        shd(150, 272, 102, 12, 0.16),
        burger,
        capy_sit(148, 184, s=0.90, mode="happy", paws="wave", extra_head=flag),
        sp4(46, 68, 12, "#FDE047", "#D97706"),
        sp4(54, 146, 9, "#FCA5A5", "#DC2626"),
        heart(246, 122, 11, "#EF4444"),
    ]))
    s5 = with_hero_aura(s5_raw, (252, 211, 77), 160)

    return [
        ("Hungry Baby",   s0),
        ("Milk Bib",      s1),
        ("Watermelon",    s2),
        ("Popcorn Hug",   s3),
        ("Cheesy Pizza",  s4),
        ("Burger King!",  s5),
    ]


# =========================================================================== #
#  55. DINO HOODIE PLAY (100% Continuous Green Dino Hoodie + Mini Duckling!)
# =========================================================================== #
def _duckling(cx, cy, s=1.0, cheer=False) -> str:
    wing = (
        f'<ellipse cx="18" cy="-8" rx="9" ry="5" transform="rotate(-38 18 -8)" fill="#FACC15" stroke="{OL}" stroke-width="3.2"/>'
        f'<ellipse cx="-18" cy="-8" rx="9" ry="5" transform="rotate(38 -18 -8)" fill="#FACC15" stroke="{OL}" stroke-width="3.2"/>'
    ) if cheer else ""
    return (
        f'<g transform="translate({cx},{cy}) scale({s})">'
        + wing +
        f'<ellipse cx="0" cy="4" rx="18" ry="14" fill="#FDE047" stroke="{OL}" stroke-width="4.2"/>'
        f'<circle cx="0" cy="-14" r="14" fill="#FDE047" stroke="{OL}" stroke-width="4.2"/>'
        f'<ellipse cx="0" cy="-9" rx="6" ry="3.6" fill="#FB923C" stroke="{OL}" stroke-width="2.8"/>'
        f'<circle cx="-5.5" cy="-16" r="2.3" fill="{OL}"/><circle cx="5.5" cy="-16" r="2.3" fill="{OL}"/>'
        f'</g>'
    )


def _dino_spikes(pts: list[tuple[float, float, float]]) -> str:
    return "".join(
        f'<g transform="translate({x:.1f},{y:.1f}) rotate({ang})">'
        f'<path d="M -11,8 Q 0,-18 11,8 Z" fill="#FACC15" stroke="{OL}" stroke-width="4.2" stroke-linejoin="round"/>'
        f'</g>'
        for x, y, ang in pts
    )


def build_55_dino_hoodie() -> list[tuple[str, Image.Image]]:
    dg, dg_hi, belly = "#4ADE80", "#86EFAC", "#FEF9C3"

    # S0: Tiny baby Capybara peeking curiously at folded pastel-green dino hoodie with tiny yellow duckling on top!
    folded_hoodie = (
        _dino_spikes([(168, 192, -16), (192, 188, 0), (216, 194, 18)]) +
        f'<rect x="134" y="196" width="116" height="64" rx="22" fill="{dg}" stroke="{OL}" stroke-width="5.8"/>'
        f'<path d="M 154,226 Q 192,238 230,226" fill="none" stroke="{OL}" stroke-width="4"/>'
        f'<ellipse cx="192" cy="212" rx="34" ry="12" fill="{dg_hi}" stroke="{OL}" stroke-width="3.5"/>'
        + _duckling(202, 184, 0.78)
    )
    s0 = render_svg("".join([
        shd(150, 266, 98, 12),
        capy_side_sniff(92, 260, s=0.60, fur=FUR_LT, look_right=True),
        folded_hoodie,
    ]))

    # S1: Small Capybara crawling head-first partway into cozy green dino hoodie collar, chubby rear & tail wiggling!
    s1 = render_svg("".join([
        shd(150, 266, 102, 12),
        # Back sleeves & folded plush green dino hoodie body with cute collar opening & drawstrings!
        _dino_spikes([(172, 162, -16), (202, 158, 4), (228, 168, 24)]),
        f'<path d="M 128,176 C 148,154 244,160 256,214 C 260,248 232,262 180,262 L 128,256 Z" fill="{dg}" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>',
        # Yellow striped hoodie pocket / trim + cute collar rim + drawstrings!
        f'<ellipse cx="132" cy="216" rx="22" ry="42" fill="#166534" stroke="{OL}" stroke-width="5.2"/>',
        f'<path d="M 134,174 Q 152,186 148,208" fill="none" stroke="#FEF9C3" stroke-width="4.2" stroke-linecap="round"/>',
        f'<circle cx="148" cy="210" r="4.5" fill="#FACC15" stroke="{OL}" stroke-width="2.2"/>',
        # Chubby caramel rear + little fluffy tail bump + 2 kicking feet!
        f'<ellipse cx="102" cy="222" rx="44" ry="34" fill="{FUR}" stroke="{OL}" stroke-width="5.8"/>',
        f'<circle cx="62" cy="210" r="10" fill="{FUR_SHD}" stroke="{OL}" stroke-width="4.2"/>',
        f'<ellipse cx="70" cy="252" rx="15" ry="9.5" transform="rotate(-22 70 252)" fill="{SNOUT}" stroke="{OL}" stroke-width="4.4"/>',
        f'<ellipse cx="104" cy="256" rx="15" ry="9.5" transform="rotate(8 104 256)" fill="{SNOUT}" stroke="{OL}" stroke-width="4.4"/>',
        # Playful wiggle action lines
        f'<path d="M 46,194 Q 38,206 46,218 M 36,200 Q 30,208 36,216" fill="none" stroke="{OL}" stroke-width="3.6" stroke-linecap="round"/>',
        _duckling(220, 148, 0.80),
    ]))

    # S2: Growing Capybara pulling spiked green dino hood over its ears with rosy cheeks!
    hood_only = (
        _dino_spikes([(116, 108, -32), (150, 96, 0), (184, 108, 32)]) +
        f'<path d="M 88,164 C 84,114 114,98 150,98 C 186,98 216,114 212,164 C 202,134 178,124 150,124 C 122,124 98,134 88,164 Z" fill="{dg}" stroke="{OL}" stroke-width="5.6" stroke-linejoin="round"/>'
    )
    s2 = render_svg("".join([
        shd(150, 266, 84, 12),
        capy_sit(150, 262, s=0.80, mode="happy", extra_head=hood_only),
        # Paws tugging hood sides
        f'<ellipse cx="94" cy="166" rx="14" ry="10" transform="rotate(-24 94 166)" fill="{SNOUT}" stroke="{OL}" stroke-width="4.4"/>',
        f'<ellipse cx="206" cy="166" rx="14" ry="10" transform="rotate(24 206 166)" fill="{SNOUT}" stroke="{OL}" stroke-width="4.4"/>',
        _duckling(230, 248, 0.72),
    ]))

    def _dino_suit_body(cx, cy_base, s=0.90, mode="happy", paws="wave") -> str:
        # Cozy full green dino hoodie with yellow striped belly & cute tail!
        top_y = cy_base - 178 * s
        tail = (
            f'<path d="M {cx + 62*s:.1f},{cy_base - 48*s:.1f} Q {cx + 108*s:.1f},{cy_base - 38*s:.1f} {cx + 102*s:.1f},{cy_base - 14*s:.1f} '
            f'Q {cx + 82*s:.1f},{cy_base - 6*s:.1f} {cx + 56*s:.1f},{cy_base - 18*s:.1f} Z" fill="{dg}" stroke="{OL}" stroke-width="5.5" stroke-linejoin="round"/>'
        )
        spikes = _dino_spikes([
            (cx - 42 * s, top_y + 18 * s, -32),
            (cx,          top_y + 4 * s,  0),
            (cx + 42 * s, top_y + 18 * s, 32),
        ])
        parts = [
            tail, spikes,
            f'<path d="M {cx},{top_y + 8*s:.1f} C {cx + 56*s:.1f},{top_y + 8*s:.1f} {cx + 78*s:.1f},{top_y + 52*s:.1f} {cx + 78*s:.1f},{cy_base - 56*s:.1f} '
            f'C {cx + 78*s:.1f},{cy_base - 12*s:.1f} {cx + 52*s:.1f},{cy_base:.1f} {cx},{cy_base:.1f} '
            f'C {cx - 52*s:.1f},{cy_base:.1f} {cx - 78*s:.1f},{cy_base - 12*s:.1f} {cx - 78*s:.1f},{cy_base - 56*s:.1f} '
            f'C {cx - 78*s:.1f},{top_y + 52*s:.1f} {cx - 56*s:.1f},{top_y + 8*s:.1f} {cx},{top_y + 8*s:.1f} Z" '
            f'fill="{dg}" stroke="{OL}" stroke-width="6.2" stroke-linejoin="round"/>',
            # Yellow striped dino belly
            f'<ellipse cx="{cx}" cy="{cy_base - 44*s:.1f}" rx="{44*s:.1f}" ry="{34*s:.1f}" fill="{belly}" stroke="{OL}" stroke-width="3.8"/>',
            f'<line x1="{cx - 34*s:.1f}" y1="{cy_base - 52*s:.1f}" x2="{cx + 34*s:.1f}" y2="{cy_base - 52*s:.1f}" stroke="#FACC15" stroke-width="5"/>',
            f'<line x1="{cx - 38*s:.1f}" y1="{cy_base - 36*s:.1f}" x2="{cx + 38*s:.1f}" y2="{cy_base - 36*s:.1f}" stroke="#FACC15" stroke-width="5"/>',
            # Hood face opening
            f'<ellipse cx="{cx}" cy="{top_y + 68*s:.1f}" rx="{52*s:.1f}" ry="{43*s:.1f}" fill="{FUR}" stroke="{OL}" stroke-width="5.2"/>',
            capy_face(cx, top_y + 64 * s, s=0.80 * s, mode=mode),
            # Feet
            f'<ellipse cx="{cx - 34*s:.1f}" cy="{cy_base - 4*s:.1f}" rx="{17*s:.1f}" ry="{10.5*s:.1f}" fill="{SNOUT}" stroke="{OL}" stroke-width="4.8"/>',
            f'<ellipse cx="{cx + 34*s:.1f}" cy="{cy_base - 4*s:.1f}" rx="{17*s:.1f}" ry="{10.5*s:.1f}" fill="{SNOUT}" stroke="{OL}" stroke-width="4.8"/>',
        ]
        if paws == "wave":
            parts.append(
                f'<ellipse cx="{cx - 50*s:.1f}" cy="{cy_base - 54*s:.1f}" rx="{15*s:.1f}" ry="{10.5*s:.1f}" transform="rotate(20 {cx - 50*s:.1f} {cy_base - 54*s:.1f})" fill="{dg_hi}" stroke="{OL}" stroke-width="4.6"/>'
                f'<ellipse cx="{cx + 68*s:.1f}" cy="{cy_base - 86*s:.1f}" rx="{16*s:.1f}" ry="{11*s:.1f}" transform="rotate(-38 {cx + 68*s:.1f} {cy_base - 86*s:.1f})" fill="{dg_hi}" stroke="{OL}" stroke-width="4.6"/>'
            )
        elif paws == "rawr":
            parts.append(
                f'<ellipse cx="{cx - 58*s:.1f}" cy="{cy_base - 72*s:.1f}" rx="{16*s:.1f}" ry="{11.5*s:.1f}" transform="rotate(34 {cx - 58*s:.1f} {cy_base - 72*s:.1f})" fill="{dg_hi}" stroke="{OL}" stroke-width="4.6"/>'
                f'<ellipse cx="{cx + 58*s:.1f}" cy="{cy_base - 72*s:.1f}" rx="{16*s:.1f}" ry="{11.5*s:.1f}" transform="rotate(-34 {cx + 58*s:.1f} {cy_base - 72*s:.1f})" fill="{dg_hi}" stroke="{OL}" stroke-width="4.6"/>'
            )
        else:
            parts.append(
                f'<ellipse cx="{cx - 50*s:.1f}" cy="{cy_base - 58*s:.1f}" rx="{15*s:.1f}" ry="{11*s:.1f}" transform="rotate(22 {cx - 50*s:.1f} {cy_base - 58*s:.1f})" fill="{dg_hi}" stroke="{OL}" stroke-width="4.6"/>'
                f'<ellipse cx="{cx + 50*s:.1f}" cy="{cy_base - 58*s:.1f}" rx="{15*s:.1f}" ry="{11*s:.1f}" transform="rotate(-22 {cx + 50*s:.1f} {cy_base - 58*s:.1f})" fill="{dg_hi}" stroke="{OL}" stroke-width="4.6"/>'
            )
        return "".join(parts)

    # S3: Chubby Capybara fully dressed in green dino hoodie waving cheerfully!
    s3 = render_svg(shd(146, 266, 86, 12) + _dino_suit_body(142, 262, s=0.86, mode="happy", paws="wave"))

    # S4: Playful Dino-Hoodie Capybara doing adorable "mini rawr!" while duckling cheers beside it!
    s4 = render_svg("".join([
        shd(146, 268, 96, 12),
        _dino_suit_body(134, 264, s=0.92, mode="rawr", paws="rawr"),
        _duckling(240, 242, 0.90, cheer=True),
        sp4(60, 102, 10, "#FDE047", "#16A34A"),
    ]))

    # S5: Super Dino Hoodie Hero: Big joyful Capybara in full onesie with yellow duckling riding proudly on hood + stars!
    s5_raw = render_svg("".join([
        shd(150, 270, 96, 13, 0.16),
        _dino_suit_body(148, 266, s=0.98, mode="happy", paws="rawr"),
        _duckling(148, 66, 0.96, cheer=True),
        sp4(48, 72, 13, "#FDE047", "#15803D"),
        sp4(252, 76, 12, "#FB923C", "#C2410C"),
        sp4(44, 160, 10, "#86EFAC", "#15803D"),
        sp4(256, 166, 10, "#FDE047", "#A16207"),
    ]))
    s5 = with_hero_aura(s5_raw, (134, 239, 172), 165)

    return [
        ("Baby & Hoodie", s0),
        ("Wiggling In",   s1),
        ("Hood Up!",      s2),
        ("Dino Wave",     s3),
        ("Mini Rawr!",    s4),
        ("Dino Hero!",    s5),
    ]


# =========================================================================== #
#  56. APPLE ORCHARD SWEET (Red Apple Present in ALL 6 Continuous Stages!)
# =========================================================================== #
def _apple(cx, cy, s=1.0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) scale({s})">'
        f'<path d="M 0,-28 L 3,-44" stroke="{OL}" stroke-width="6.5" stroke-linecap="round"/>'
        f'<path d="M 2,-36 Q 22,-50 32,-38 Q 20,-26 2,-32 Z" fill="#22C55E" stroke="{OL}" stroke-width="3.8" stroke-linejoin="round"/>'
        f'<path d="M 0,-24 C -24,-34 -46,-14 -42,16 C -38,44 -16,54 0,48 C 16,54 38,44 42,16 C 46,-14 24,-34 0,-24 Z" fill="#E11D48" stroke="{OL}" stroke-width="5.2" stroke-linejoin="round"/>'
        f'<ellipse cx="-18" cy="-4" rx="7" ry="13" transform="rotate(20 -18 -4)" fill="#FDA4AF" fill-opacity="0.72"/>'
        f'</g>'
    )


def build_56_apple_orchard() -> list[tuple[str, Image.Image]]:
    # S0: Tiny baby Capybara sniffing curiously at a glossy red apple on a green leaf!
    s0 = render_svg("".join([
        shd(150, 264, 96, 12),
        f'<ellipse cx="206" cy="254" rx="44" ry="12" fill="#4ADE80" stroke="{OL}" stroke-width="4.2"/>',
        capy_side_sniff(102, 258, s=0.58, fur=FUR_LT, look_right=True),
        _apple(206, 218, 0.72),
    ]))

    # S1: Small Capybara sitting neatly poking shiny red apple gently with one chubby paw!
    s1 = render_svg("".join([
        shd(150, 266, 94, 12),
        capy_sit(116, 260, s=0.68, mode="curious", look_dx=4, paws="poke_right"),
        _apple(198, 224, 0.72),
    ]))

    # S2: Growing Capybara clutching 1 crisp red apple happily against its tummy with both paws!
    s2 = render_svg("".join([
        shd(150, 266, 84, 12),
        capy_sit(150, 262, s=0.78, mode="happy",
                 extra_belly=_apple(150, 224, 0.68) + f'<ellipse cx="116" cy="222" rx="14" ry="9.5" fill="{SNOUT}" stroke="{OL}" stroke-width="4.4"/><ellipse cx="184" cy="222" rx="14" ry="9.5" fill="{SNOUT}" stroke="{OL}" stroke-width="4.4"/>'),
    ]))

    # S3: Chubby Capybara proudly balancing bright red apple snugly on top of its head!
    s3 = render_svg("".join([
        shd(150, 266, 86, 12),
        capy_sit(150, 262, s=0.86, mode="happy", extra_head=_apple(150, 108, 0.68)),
        heart(228, 122, 11, "#FB7185"),
    ]))

    # S4: Happy Capybara sitting beside wooden orchard harvest basket brimming with shiny red apples!
    basket = (
        _apple(192, 198, 0.44) + _apple(224, 198, 0.44) + _apple(208, 184, 0.46) +
        f'<path d="M 164,202 L 174,258 Q 208,266 242,258 L 252,202 Z" fill="#D97706" stroke="{OL}" stroke-width="5.2" stroke-linejoin="round"/>'
        f'<rect x="160" y="196" width="96" height="14" rx="6" fill="#B45309" stroke="{OL}" stroke-width="4.6"/>'
        f'<line x1="170" y1="226" x2="246" y2="226" stroke="{OL}" stroke-width="3.2"/>'
        f'<line x1="174" y1="244" x2="242" y2="244" stroke="{OL}" stroke-width="3.2"/>'
    )
    s4 = render_svg("".join([
        shd(150, 268, 102, 12),
        capy_sit(116, 264, s=0.88, mode="happy", paws="wave"),
        basket,
    ]))

    # S5: Sweet Orchard Harvest King: Big blissful Capybara hugging giant gleaming red apple + heart speech bubble!
    bubble = (
        f'<path d="M 220,76 C 220,54 268,54 268,76 C 268,94 252,102 236,100 L 222,108 L 226,95 C 222,90 220,84 220,76 Z" fill="#FFFFFF" stroke="{OL}" stroke-width="4.2" stroke-linejoin="round"/>'
        + heart(244, 78, 11, "#E11D48", OL, 2.2)
    )
    s5_raw = render_svg("".join([
        shd(150, 270, 104, 13, 0.16),
        capy_sit(162, 264, s=0.98, mode="happy", feet=True),
        _apple(118, 206, 1.18),
        # Chubby hugging paw wrapped around giant apple
        f'<ellipse cx="164" cy="212" rx="18" ry="12" transform="rotate(-14 164 212)" fill="{SNOUT}" stroke="{OL}" stroke-width="4.8"/>',
        bubble,
        sp4(46, 84, 12, "#FDE047", "#E11D48"),
        sp4(258, 152, 10, "#FDA4AF", "#BE123C"),
    ]))
    s5 = with_hero_aura(s5_raw, (253, 164, 175), 162)

    return [
        ("Apple Sniff",    s0),
        ("Apple Poke",     s1),
        ("Apple Clutch",   s2),
        ("Head Apple",     s3),
        ("Orchard Basket", s4),
        ("Giant Apple!",   s5),
    ]


# =========================================================================== #
#  57. PINK CLOUD CHILL (100% Continuous Pastel Pink Cloud Dream Story!)
# =========================================================================== #
def _pink_cloud(cx=150, cy=224, s=1.0, fill="#FBCFE8") -> str:
    return (
        f'<g transform="translate({cx},{cy}) scale({s})">'
        f'<path d="M -86,16 C -112,16 -116,-28 -82,-36 C -78,-72 -38,-88 -4,-74 '
        f'C 26,-92 72,-72 74,-34 C 108,-28 110,16 84,22 C 58,44 -60,44 -86,16 Z" '
        f'fill="{fill}" stroke="{OL}" stroke-width="5.8" stroke-linejoin="round"/>'
        f'<path d="M -68,12 C -46,28 46,28 68,12" fill="none" stroke="#F472B6" stroke-opacity="0.45" stroke-width="7" stroke-linecap="round"/>'
        f'</g>'
    )


def _crescent_moon(cx, cy, s=1.0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) scale({s})">'
        f'<path d="M 12,-28 A 30 30 0 1 0 12,28 A 22 22 0 1 1 12,-28 Z" fill="#FEF08A" stroke="{OL}" stroke-width="4.2" stroke-linejoin="round"/>'
        f'</g>'
    )


def build_57_pink_chill() -> list[tuple[str, Image.Image]]:
    # S0: Tiny sleepy baby Capybara peeking its round head out from behind fluffy pastel-pink cloud cushion!
    s0 = render_svg("".join([
        shd(150, 266, 84, 11),
        capy_peek_head(150, 152, s=0.52, mode="baby", fur=FUR_LT),
        _pink_cloud(150, 224, 0.88),
        capy_grip_paws(150, 174, s=0.52, spread=36),
    ]))

    # S1: Small Capybara curled up napping peacefully on top of soft pink cloud (zzz)
    s1 = render_svg("".join([
        shd(150, 266, 92, 11),
        _pink_cloud(150, 226, 0.96),
        capy_loaf(148, 206, s=0.72, mode="sleepy"),
        zzz_svg(202, 108, 1.0),
    ]))

    # S2: Growing Capybara rolling happily belly-up on fluffy pink cloud with spaced-apart tiny paws kicking!
    belly_up = (
        f'<g transform="translate(150,188)">'
        # Cute round ears on the left head resting on cloud!
        f'<ellipse cx="-52" cy="14" rx="11" ry="12" transform="rotate(-48 -52 14)" fill="{FUR}" stroke="{OL}" stroke-width="4.8"/>'
        f'<ellipse cx="-24" cy="24" rx="11" ry="12" transform="rotate(-12 -24 24)" fill="{FUR}" stroke="{OL}" stroke-width="4.8"/>'
        # Chubby upside-down loaf body with soft lighter tummy!
        f'<path d="M -68,-4 C -70,-34 -34,-42 12,-42 C 56,-42 74,-22 72,4 C 70,26 42,32 0,32 C -46,32 -68,20 -68,-4 Z" fill="{FUR}" stroke="{OL}" stroke-width="5.8"/>'
        f'<ellipse cx="18" cy="-16" rx="36" ry="18" fill="{FUR_LT}"/>'
        # Spaced-apart front pair & hind pair of tiny stubby paws kicking happily!
        f'<ellipse cx="-8" cy="-38" rx="9.5" ry="13" transform="rotate(-22 -8 -38)" fill="{SNOUT}" stroke="{OL}" stroke-width="4.2"/>'
        f'<ellipse cx="10" cy="-32" rx="9.5" ry="12" transform="rotate(14 10 -32)" fill="{SNOUT}" stroke="{OL}" stroke-width="4.2"/>'
        f'<ellipse cx="42" cy="-36" rx="9.5" ry="13" transform="rotate(-12 42 -36)" fill="{SNOUT}" stroke="{OL}" stroke-width="4.2"/>'
        f'<ellipse cx="60" cy="-22" rx="9.5" ry="12" transform="rotate(34 60 -22)" fill="{SNOUT}" stroke="{OL}" stroke-width="4.2"/>'
        + capy_face(-32, 0, s=0.62, mode="happy") + '</g>'
    )
    s2 = render_svg("".join([
        shd(150, 266, 94, 11),
        _pink_cloud(150, 228, 1.00),
        belly_up,
        heart(224, 110, 10, "#F472B6"),
    ]))

    # S3: Chubby sitting Capybara floating on pink cloud enjoying pastel-pink popsicle!
    pop = (
        f'<g transform="translate(204,174) rotate(18)">'
        f'<rect x="-4" y="16" width="8" height="24" rx="3" fill="#FDE68A" stroke="{OL}" stroke-width="3.2"/>'
        f'<rect x="-15" y="-22" width="30" height="40" rx="14" fill="#F472B6" stroke="{OL}" stroke-width="4.4"/>'
        f'<path d="M -13,-8 C -13,-20 13,-20 13,-8 Q 6,-2 0,-8 Q -6,-2 -13,-8 Z" fill="#FFFFFF"/>'
        f'</g>'
    )
    s3 = render_svg("".join([
        shd(150, 268, 96, 11),
        _pink_cloud(150, 232, 1.02),
        capy_sit(146, 228, s=0.82, mode="happy", paws="front_hold"),
        pop,
    ]))

    # S4: Dreamy Capybara floating on lush swirling pink cloud hugging tiny glowing crescent moon!
    s4 = render_svg("".join([
        shd(150, 268, 100, 12),
        _pink_cloud(150, 234, 1.06),
        capy_sit(150, 230, s=0.88, mode="bliss",
                 extra_belly=_crescent_moon(154, 194, 0.92) + f'<ellipse cx="122" cy="196" rx="14" ry="9.5" fill="{SNOUT}" stroke="{OL}" stroke-width="4.5"/><ellipse cx="178" cy="196" rx="14" ry="9.5" fill="{SNOUT}" stroke="{OL}" stroke-width="4.5"/>'),
        sp4(66, 98, 10, "#FDE047", "#DB2777"),
        sp4(236, 94, 9, "#E9D5FF", "#9333EA"),
    ]))

    # S5: Cloud-9 Chill Master: Big rosy blissful Capybara atop grand fluffy pink cloud + rainbow stars & glowing moon!
    s5_raw = render_svg("".join([
        shd(150, 272, 108, 12, 0.14),
        # Soft pastel rainbow arc behind cloud!
        '<path d="M 48,196 A 102 102 0 0 1 252,196" fill="none" stroke="#F9A8D4" stroke-width="14" stroke-linecap="round" stroke-opacity="0.7"/>',
        '<path d="M 62,196 A 88 88 0 0 1 238,196" fill="none" stroke="#DDD6FE" stroke-width="12" stroke-linecap="round" stroke-opacity="0.7"/>',
        '<path d="M 76,196 A 74 74 0 0 1 224,196" fill="none" stroke="#FEF08A" stroke-width="10" stroke-linecap="round" stroke-opacity="0.7"/>',
        _pink_cloud(150, 236, 1.12, "#FCE7F3"),
        capy_sit(150, 232, s=0.96, mode="happy", paws="hug", extra_belly=heart(150, 198, 18, "#F472B6")),
        _crescent_moon(234, 78, 0.78),
        sp4(54, 78, 13, "#FDE047", "#DB2777"),
        sp4(42, 152, 9, "#E9D5FF", "#9333EA"),
        sp4(258, 148, 10, "#F9A8D4", "#BE185D"),
    ]))
    s5 = with_hero_aura(s5_raw, (249, 168, 212), 160)

    return [
        ("Cloud Peek",    s0),
        ("Cloud Nap",     s1),
        ("Belly Roll",    s2),
        ("Pink Pop",      s3),
        ("Moon Hug",      s4),
        ("Cloud-9 Zen!",  s5),
    ]


# =========================================================================== #
#  58. FAIRY PARTY WISH (100% Continuous Gift Box -> Fairy Party Magic!)
# =========================================================================== #
def _gift_box(cx=150, cy_bot=262, w=128, h=86, open_lid=False) -> str:
    x0 = cx - w / 2
    y0 = cy_bot - h
    out = (
        f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w}" height="{h}" rx="12" fill="#F9A8D4" stroke="{OL}" stroke-width="5.6"/>'
        f'<rect x="{cx - 12:.1f}" y="{y0:.1f}" width="24" height="{h}" fill="#FDE047" stroke="{OL}" stroke-width="3.8"/>'
    )
    if open_lid:
        out += (
            f'<g transform="translate({x0:.1f},{y0:.1f}) rotate(-26)">'
            f'<rect x="-8" y="-22" width="{w + 16}" height="24" rx="8" fill="#F472B6" stroke="{OL}" stroke-width="5.2"/>'
            f'<path d="M {w/2},-22 C {w/2 - 22},-46 {w/2 - 36},-30 {w/2 - 14},-22 Z" fill="#FDE047" stroke="{OL}" stroke-width="3.8"/>'
            f'<path d="M {w/2},-22 C {w/2 + 22},-46 {w/2 + 36},-30 {w/2 + 14},-22 Z" fill="#FDE047" stroke="{OL}" stroke-width="3.8"/>'
            f'</g>'
        )
    else:
        out += f'<rect x="{x0 - 8:.1f}" y="{y0 - 16:.1f}" width="{w + 16}" height="22" rx="7" fill="#F472B6" stroke="{OL}" stroke-width="5.2"/>'
    return out


def _party_hat(cx, cy, s=1.0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) scale({s})">'
        f'<polygon points="-24,0 24,0 0,-52" fill="#F472B6" stroke="{OL}" stroke-width="4.6" stroke-linejoin="round"/>'
        f'<circle cx="-8" cy="-14" r="4" fill="#FDE047"/><circle cx="8" cy="-22" r="4" fill="#A5F3FC"/><circle cx="0" cy="-34" r="3.5" fill="#FFFFFF"/>'
        f'<circle cx="0" cy="-54" r="9" fill="#FDE047" stroke="{OL}" stroke-width="3.6"/>'
        f'</g>'
    )


def _fairy_wings(cx, cy, s=1.0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) scale({s})">'
        f'<path d="M -24,-10 C -84,-64 -106,-10 -58,12 C -94,28 -70,66 -26,30 Z" fill="#BAE6FD" fill-opacity="0.90" stroke="{OL}" stroke-width="4.8" stroke-linejoin="round"/>'
        f'<path d="M 24,-10 C 84,-64 106,-10 58,12 C 94,28 70,66 26,30 Z" fill="#BAE6FD" fill-opacity="0.90" stroke="{OL}" stroke-width="4.8" stroke-linejoin="round"/>'
        f'</g>'
    )


def _star_wand(cx, cy, rot=24, s=1.0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot}) scale({s})">'
        f'<rect x="-3.5" y="0" width="7" height="54" rx="3" fill="#F472B6" stroke="{OL}" stroke-width="3.4"/>'
        + sp4(0, -10, 18, "#FDE047", OL, 3.8) + '</g>'
    )


def build_58_fairy_party() -> list[tuple[str, Image.Image]]:
    # S0: Tiny baby Capybara peeking adorably out of half-open pastel pink gift box!
    s0 = render_svg("".join([
        shd(150, 266, 82, 11),
        capy_peek_head(154, 152, s=0.52, mode="baby", fur=FUR_LT),
        _gift_box(150, 262, 132, 88, open_lid=True),
        capy_grip_paws(154, 174, s=0.54, spread=36),
    ]))

    # S1: Small Capybara hopping out of gift box holding 1 tiny glowing golden wishing star!
    s1 = render_svg("".join([
        shd(150, 266, 98, 12),
        _gift_box(84, 262, 76, 56, open_lid=True),
        capy_sit(172, 260, s=0.68, mode="happy",
                 extra_belly=sp4(172, 224, 17, "#FDE047", OL, 3.8) + f'<ellipse cx="148" cy="226" rx="12" ry="8.5" fill="{SNOUT}" stroke="{OL}" stroke-width="4.0"/><ellipse cx="196" cy="226" rx="12" ry="8.5" fill="{SNOUT}" stroke="{OL}" stroke-width="4.0"/>'),
    ]))

    # S2: Growing Capybara putting on pastel polka-dot party cone hat with cheerful confetti!
    confetti = (
        '<circle cx="72" cy="96" r="6" fill="#F472B6"/><rect x="220" y="88" width="12" height="7" rx="2" transform="rotate(28 226 92)" fill="#38BDF8"/>'
        '<circle cx="236" cy="148" r="5.5" fill="#FACC15"/><rect x="64" y="152" width="11" height="6" rx="2" transform="rotate(-24 70 155)" fill="#A855F7"/>'
    )
    s2 = render_svg("".join([
        shd(150, 266, 84, 12),
        confetti,
        capy_sit(150, 262, s=0.78, mode="happy", paws="wave", extra_head=_party_hat(150, 152, 0.92)),
    ]))

    # S3: Chubby Capybara sprouting baby sky-blue fairy wings holding shiny star magic wand!
    s3 = render_svg("".join([
        shd(150, 266, 86, 12),
        _fairy_wings(150, 186, 0.78),
        capy_sit(150, 262, s=0.84, mode="wink", extra_head=_party_hat(150, 142, 0.96)),
        _star_wand(218, 178, rot=24, s=0.88),
        f'<ellipse cx="204" cy="204" rx="14" ry="9.5" fill="{SNOUT}" stroke="{OL}" stroke-width="4.4"/>',
    ]))

    # S4: Joyful Capybara waving glowing star wand conjuring swirling sparkles over gift box!
    s4 = render_svg("".join([
        shd(150, 268, 102, 12),
        _gift_box(76, 264, 72, 52, open_lid=False),
        _fairy_wings(162, 178, 0.92),
        capy_sit(162, 262, s=0.90, mode="happy", extra_head=_party_hat(162, 132, 1.0)),
        _star_wand(232, 160, rot=26, s=0.95),
        f'<ellipse cx="218" cy="192" rx="14" ry="10" fill="{SNOUT}" stroke="{OL}" stroke-width="4.5"/>',
        sp4(78, 152, 11, "#FDE047", "#9333EA"),
        sp4(104, 118, 9, "#F9A8D4", "#DB2777"),
        sp4(250, 102, 12, "#FDE047", "#B45309"),
    ]))

    # S5: Grand Fairy Party Capybara floating with shimmering sky-blue wings, party hat, star wand & wishing stars!
    s5_raw = render_svg("".join([
        shd(150, 272, 86, 11, 0.14),
        _fairy_wings(150, 166, 1.16),
        capy_sit(150, 252, s=0.96, mode="happy", extra_head=_party_hat(150, 114, 1.08)),
        _star_wand(228, 152, rot=26, s=1.05),
        f'<ellipse cx="212" cy="186" rx="15" ry="10.5" fill="{SNOUT}" stroke="{OL}" stroke-width="4.8"/>',
        f'<ellipse cx="98" cy="198" rx="14" ry="10" transform="rotate(24 98 198)" fill="{SNOUT}" stroke="{OL}" stroke-width="4.6"/>',
        sp4(48, 72, 14, "#FDE047", "#9333EA"),
        sp4(252, 68, 13, "#FDE047", "#DB2777"),
        sp4(54, 212, 10, "#BAE6FD", "#0284C7"),
        sp4(248, 224, 11, "#F9A8D4", "#9333EA"),
        heart(82, 110, 10, "#EC4899"),
    ]))
    s5 = with_hero_aura(s5_raw, (216, 180, 254), 158)

    return [
        ("Gift Box Peek", s0),
        ("Wishing Star",  s1),
        ("Party Hat",     s2),
        ("Fairy Wings",   s3),
        ("Magic Wand",    s4),
        ("Fairy Party!",  s5),
    ]


# =========================================================================== #
#  59. SELFCARE GLOWUP (100% Continuous Morning-to-Glow-Up Skincare Story!)
# =========================================================================== #
def _spa_headband(cx, cy, s=1.0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) scale({s})">'
        f'<path d="M -52,18 C -52,-20 52,-20 52,18" fill="none" stroke="{OL}" stroke-width="16" stroke-linecap="round"/>'
        f'<path d="M -52,18 C -52,-20 52,-20 52,18" fill="none" stroke="#FDA4AF" stroke-width="9" stroke-linecap="round"/>'
        # Fluffy bow on top!
        f'<path d="M 0,-12 C -26,-34 -34,-2 -6,-6 Z" fill="#FB7185" stroke="{OL}" stroke-width="4.2" stroke-linejoin="round"/>'
        f'<path d="M 0,-12 C 26,-34 34,-2 6,-6 Z" fill="#FB7185" stroke="{OL}" stroke-width="4.2" stroke-linejoin="round"/>'
        f'<circle cx="0" cy="-9" r="7" fill="#F43F5E" stroke="{OL}" stroke-width="3.6"/>'
        f'</g>'
    )


def _heart_shades(cx, cy, s=1.0) -> str:
    ex = 29 * s * 0.94
    return (
        heart(cx - ex, cy, 18 * s, "#FB7185", OL, 3.4 * s)
        + heart(cx + ex, cy, 18 * s, "#FB7185", OL, 3.4 * s)
        + f'<line x1="{cx - ex + 15*s:.1f}" y1="{cy - 4*s:.1f}" x2="{cx + ex - 15*s:.1f}" y2="{cy - 4*s:.1f}" stroke="{OL}" stroke-width="{4.0*s:.1f}"/>'
    )


def _heart_mirror(cx, cy, rot=-18, s=1.0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot}) scale({s})">'
        f'<rect x="-5" y="18" width="10" height="34" rx="5" fill="#F43F5E" stroke="{OL}" stroke-width="3.8"/>'
        + heart(0, 0, 26, "#FDA4AF", OL, 4.4)
        + heart(0, 0, 18, "#E0F2FE", OL, 2.6)
        + '<line x1="-8" y1="-6" x2="2" y2="-14" stroke="#FFFFFF" stroke-width="3.6" stroke-linecap="round"/>'
        + '</g>'
    )


def build_59_selfcare() -> list[tuple[str, Image.Image]]:
    # S0: Tiny sleepy baby Capybara tucked under cozy rose-pink duvet peeking 1 eye out beside spa headband!
    s0 = render_svg("".join([
        shd(150, 266, 98, 12),
        # Cozy pillow behind head
        f'<rect x="74" y="142" width="152" height="58" rx="22" fill="#FFF1F2" stroke="{OL}" stroke-width="5.2"/>',
        capy_peek_head(140, 174, s=0.52, mode="one_peek", fur=FUR_LT),
        # Rose-pink duvet blanket tucked neatly across chin!
        f'<path d="M 52,204 Q 150,184 248,204 L 254,256 Q 150,270 46,256 Z" fill="#FDA4AF" stroke="{OL}" stroke-width="5.8" stroke-linejoin="round"/>',
        f'<path d="M 56,208 Q 150,192 244,208" fill="none" stroke="#FFFFFF" stroke-width="9" stroke-linecap="round"/>',
        capy_grip_paws(140, 200, s=0.52, spread=34),
        # Fluffy pink headband resting on corner of bed
        _spa_headband(224, 184, 0.42),
    ]))

    # S1: Small Capybara wearing fluffy pink bow spa headband washing cheeks with shiny soap bubbles!
    bubbles = (
        '<circle cx="76" cy="148" r="14" fill="#E0F2FE" fill-opacity="0.85" stroke="#38BDF8" stroke-width="3"/>'
        '<circle cx="98" cy="118" r="9" fill="#FFFFFF" stroke="#38BDF8" stroke-width="2.5"/>'
        '<circle cx="224" cy="142" r="13" fill="#E0F2FE" fill-opacity="0.85" stroke="#38BDF8" stroke-width="3"/>'
        '<circle cx="208" cy="112" r="8" fill="#FFFFFF" stroke="#38BDF8" stroke-width="2.5"/>'
    )
    s1 = render_svg("".join([
        shd(150, 266, 80, 11),
        capy_sit(150, 260, s=0.72, mode="happy",
                 extra_head=_spa_headband(150, 162, 0.78)),
        f'<ellipse cx="116" cy="206" rx="14" ry="10" transform="rotate(-24 116 206)" fill="{SNOUT}" stroke="{OL}" stroke-width="4.2"/>',
        f'<ellipse cx="184" cy="206" rx="14" ry="10" transform="rotate(24 184 206)" fill="{SNOUT}" stroke="{OL}" stroke-width="4.2"/>',
        bubbles,
    ]))

    # S2: Growing Capybara relaxing blissfully in pastel-green sheet mask + cute cucumber slices!
    mask_svg = (
        f'<ellipse cx="150" cy="194" rx="46" ry="38" fill="#BBF7D0" fill-opacity="0.92" stroke="{OL}" stroke-width="3.6"/>'
        # Cute cucumber slices over eyes!
        f'<circle cx="128" cy="184" r="13" fill="#4ADE80" stroke="{OL}" stroke-width="3.4"/>'
        f'<circle cx="128" cy="184" r="8" fill="#DCFCE7"/>'
        f'<circle cx="172" cy="184" r="13" fill="#4ADE80" stroke="{OL}" stroke-width="3.4"/>'
        f'<circle cx="172" cy="184" r="8" fill="#DCFCE7"/>'
        # Snout peeking through mask
        f'<ellipse cx="150" cy="202" rx="16" ry="12" fill="{SNOUT}"/>'
        f'<path d="M 144,205 Q 150,210 156,205" fill="none" stroke="{OL}" stroke-width="3.0" stroke-linecap="round"/>'
    )
    s2 = render_svg("".join([
        shd(150, 266, 84, 12),
        capy_sit(150, 262, s=0.80, mode="bliss",
                 extra_head=_spa_headband(150, 150, 0.86) + mask_svg),
        sp4(228, 124, 10, "#86EFAC", "#16A34A"),
    ]))

    # S3: Chubby glowing Capybara admiring shiny rosy cheeks in pastel-pink heart hand-mirror!
    s3 = render_svg("".join([
        shd(150, 266, 88, 12),
        capy_sit(136, 262, s=0.86, mode="wink", look_dx=4,
                 extra_head=_spa_headband(136, 144, 0.90)),
        _heart_mirror(216, 186, rot=16, s=0.92),
        f'<ellipse cx="204" cy="214" rx="14" ry="10" fill="{SNOUT}" stroke="{OL}" stroke-width="4.4"/>',
        sp4(72, 120, 10, "#FDE047", "#F43F5E"),
    ]))

    # S4: Stylish Capybara slipping on chic pink heart-shaped sunglasses with tiny sparkle gleams!
    s4 = render_svg("".join([
        shd(150, 268, 90, 12),
        capy_sit(150, 264, s=0.92, mode="happy", paws="wave",
                 extra_head=_spa_headband(150, 134, 0.96) + _heart_shades(150, 172, 0.94)),
        sp4(64, 118, 11, "#FDE047", "#D97706"),
        sp4(238, 112, 11, "#FDA4AF", "#E11D48"),
    ]))

    # S5: Radiant Glow-Up Icon: Big confident sparkling Capybara in heart sunglasses & rose bow, holding skincare serum & heart mirror!
    serum = (
        f'<g transform="translate(86,216) rotate(-14)">'
        f'<rect x="-13" y="-12" width="26" height="34" rx="7" fill="#FFE4E6" stroke="{OL}" stroke-width="4.0"/>'
        f'<rect x="-6" y="-22" width="12" height="10" fill="#FDE047" stroke="{OL}" stroke-width="3.2"/>'
        f'<circle cx="0" cy="-26" r="5" fill="#F43F5E" stroke="{OL}" stroke-width="2.8"/>'
        + heart(0, 6, 7, "#F43F5E") + '</g>'
    )
    s5_raw = render_svg("".join([
        shd(150, 270, 96, 13, 0.16),
        capy_sit(150, 264, s=0.98, mode="happy",
                 extra_head=_spa_headband(150, 124, 1.02) + _heart_shades(150, 166, 1.00)),
        serum,
        _heart_mirror(222, 188, rot=18, s=0.92),
        f'<ellipse cx="102" cy="218" rx="14" ry="10" fill="{SNOUT}" stroke="{OL}" stroke-width="4.6"/>',
        f'<ellipse cx="206" cy="216" rx="14" ry="10" fill="{SNOUT}" stroke="{OL}" stroke-width="4.6"/>',
        sp4(46, 76, 13, "#FDE047", "#D97706"),
        sp4(254, 78, 12, "#FDA4AF", "#E11D48"),
        heart(236, 122, 10, "#F43F5E"),
        heart(64, 134, 9, "#FB7185"),
    ]))
    s5 = with_hero_aura(s5_raw, (253, 164, 175), 162)

    return [
        ("Cozy Wakeup",   s0),
        ("Bubble Wash",   s1),
        ("Sheet Mask",    s2),
        ("Heart Mirror",  s3),
        ("Heart Shades",  s4),
        ("Glow-Up Icon!", s5),
    ]


# =========================================================================== #
#  60. SNAPSHOT TRAVELER (100% Continuous Vintage Camera Traveler Story!)
# =========================================================================== #
def _vintage_cam(cx, cy, s=1.0, flash=False) -> str:
    fl = (
        sp4(cx + 38 * s, cy - 38 * s, 22 * s, "#FEF08A", "#EA580C", 3.4)
        + sp4(cx + 58 * s, cy - 16 * s, 11 * s, "#FFFFFF", "#F59E0B", 2.4)
    ) if flash else ""
    return (
        f'<g transform="translate({cx},{cy}) scale({s})">'
        f'<rect x="-46" y="-28" width="92" height="66" rx="14" fill="#FAF7F2" stroke="{OL}" stroke-width="5.2"/>'
        f'<rect x="-46" y="-10" width="92" height="32" fill="#0D9488" stroke="{OL}" stroke-width="4.2"/>'
        f'<rect x="-32" y="-38" width="22" height="12" rx="4" fill="#EA580C" stroke="{OL}" stroke-width="4.0"/>'
        f'<circle cx="0" cy="6" r="22" fill="#E2E8F0" stroke="{OL}" stroke-width="4.6"/>'
        f'<circle cx="0" cy="6" r="14" fill="#1E293B" stroke="{OL}" stroke-width="3.6"/>'
        f'<circle cx="-5" cy="1" r="4" fill="#FFFFFF" fill-opacity="0.85"/>'
        f'<rect x="22" y="-22" width="15" height="9" rx="3" fill="#FDE047" stroke="{OL}" stroke-width="2.8"/>'
        f'</g>' + fl
    )


def _explorer_cap(cx, cy, s=1.0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) scale({s})">'
        f'<path d="M -48,6 C -48,-32 48,-32 48,6 Z" fill="#0D9488" stroke="{OL}" stroke-width="5.2" stroke-linejoin="round"/>'
        f'<path d="M -52,6 Q 0,14 64,8 Q 52,-4 34,-2 Q 0,-4 -52,6 Z" fill="#14B8A6" stroke="{OL}" stroke-width="4.8" stroke-linejoin="round"/>'
        f'<circle cx="0" cy="-24" r="5" fill="#EA580C" stroke="{OL}" stroke-width="3"/>'
        f'</g>'
    )


def _travel_scarf(cx, cy, s=1.0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) scale({s})">'
        f'<rect x="-48" y="-10" width="96" height="22" rx="10" fill="#F59E0B" stroke="{OL}" stroke-width="4.6"/>'
        f'<path d="M 18,6 L 38,6 L 44,40 L 22,40 Z" fill="#EA580C" stroke="{OL}" stroke-width="4.4" stroke-linejoin="round"/>'
        f'<line x1="-24" y1="-10" x2="-24" y2="12" stroke="#FEF3C7" stroke-width="4"/>'
        f'<line x1="4" y1="-10" x2="4" y2="12" stroke="#FEF3C7" stroke-width="4"/>'
        f'</g>'
    )


def _polaroid(cx, cy, rot=0, s=1.0, bg="#BAE6FD") -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot}) scale({s})">'
        f'<rect x="-22" y="-26" width="44" height="54" rx="4" fill="#FFFFFF" stroke="{OL}" stroke-width="3.6"/>'
        f'<rect x="-16" y="-20" width="32" height="30" rx="2" fill="{bg}" stroke="{OL}" stroke-width="2.4"/>'
        f'<circle cx="6" cy="-10" r="5" fill="#FDE047"/>'
        f'<path d="M -16,10 L -4,-4 L 6,4 L 16,-2 L 16,10 Z" fill="#4ADE80"/>'
        f'</g>'
    )


def build_60_traveler() -> list[tuple[str, Image.Image]]:
    # S0: Tiny baby Capybara peeking curiously over top of vintage teal instant camera + folded mini map!
    mini_map = (
        f'<g transform="translate(226,238) rotate(10)">'
        f'<polygon points="-24,-18 -6,-24 10,-16 26,-22 26,18 10,24 -6,16 -24,22" fill="#FEF3C7" stroke="{OL}" stroke-width="4" stroke-linejoin="round"/>'
        f'<path d="M -14,6 Q 0,-8 14,4" fill="none" stroke="#EA580C" stroke-width="3" stroke-dasharray="4 3"/>'
        f'</g>'
    )
    s0 = render_svg("".join([
        shd(146, 266, 98, 12),
        capy_peek_head(134, 154, s=0.52, mode="baby", fur=FUR_LT),
        _vintage_cam(134, 224, 1.06),
        capy_grip_paws(134, 192, s=0.52, spread=36),
        mini_map,
    ]))

    # S1: Small Capybara putting on pastel explorer cap & tiny canvas backpack, ready to depart!
    backpack = (
        f'<rect x="174" y="182" width="44" height="62" rx="14" fill="#EA580C" stroke="{OL}" stroke-width="5.0"/>'
        f'<rect x="182" y="204" width="28" height="22" rx="6" fill="#FDBA74" stroke="{OL}" stroke-width="3.6"/>'
    )
    s1 = render_svg("".join([
        shd(150, 266, 86, 12),
        backpack,
        capy_sit(142, 260, s=0.70, mode="happy", paws="wave",
                 extra_head=_explorer_cap(142, 160, 0.80)),
    ]))

    # S2: Growing Capybara happily spinning a colorful world globe with tiny travel pins!
    globe = (
        f'<g transform="translate(204,206)">'
        f'<path d="M -26,38 L 26,38 M 0,38 L 0,26" stroke="{OL}" stroke-width="5.2" stroke-linecap="round"/>'
        f'<circle cx="0" cy="-6" r="34" fill="#38BDF8" stroke="{OL}" stroke-width="5.0"/>'
        f'<path d="M -20,-18 Q -4,-26 4,-10 Q -4,4 -18,0 Z" fill="#4ADE80" stroke="{OL}" stroke-width="2.6"/>'
        f'<path d="M 10,-6 Q 26,-12 24,8 Q 14,16 6,6 Z" fill="#4ADE80" stroke="{OL}" stroke-width="2.6"/>'
        f'<circle cx="-8" cy="-16" r="4.5" fill="#EF4444" stroke="{OL}" stroke-width="2"/>'
        f'<circle cx="16" cy="2" r="4.5" fill="#FACC15" stroke="{OL}" stroke-width="2"/>'
        f'</g>'
    )
    s2 = render_svg("".join([
        shd(150, 266, 98, 12),
        capy_sit(124, 262, s=0.78, mode="curious", look_dx=4,
                 extra_head=_explorer_cap(124, 150, 0.86), paws="poke_right"),
        globe,
        sp4(248, 152, 9, "#FDE047", "#0D9488"),
    ]))

    # S3: Chubby traveler Capybara wearing mustard travel scarf lifting vintage teal camera ready to snap!
    s3 = render_svg("".join([
        shd(150, 266, 88, 12),
        capy_sit(150, 262, s=0.84, mode="wink",
                 extra_head=_explorer_cap(150, 140, 0.90),
                 extra_belly=_travel_scarf(150, 218, 0.84) + _vintage_cam(150, 232, 0.66) + f'<ellipse cx="114" cy="232" rx="13" ry="9" fill="{SNOUT}" stroke="{OL}" stroke-width="4.4"/><ellipse cx="186" cy="232" rx="13" ry="9" fill="{SNOUT}" stroke="{OL}" stroke-width="4.4"/>'),
    ]))

    # S4: Excited Capybara pressing shutter — golden flash burst + 1 polaroid snapshot popping out!
    s4 = render_svg("".join([
        shd(150, 268, 94, 12),
        capy_sit(146, 264, s=0.90, mode="happy",
                 extra_head=_explorer_cap(146, 134, 0.96),
                 extra_belly=_travel_scarf(146, 214, 0.88) + _vintage_cam(146, 232, 0.70) + f'<ellipse cx="108" cy="232" rx="14" ry="9.5" fill="{SNOUT}" stroke="{OL}" stroke-width="4.5"/><ellipse cx="184" cy="232" rx="14" ry="9.5" fill="{SNOUT}" stroke="{OL}" stroke-width="4.5"/>'),
        sp4(192, 202, 17, "#FEF08A", "#EA580C", 3.2),
        _polaroid(234, 232, rot=14, s=0.88, bg="#FDE68A"),
    ]))

    # S5: Master Snapshot Traveler: Big joyful Capybara + explorer cap + mustard scarf + teal camera + 3 floating polaroids + compass!
    compass = (
        f'<g transform="translate(248,238)">'
        f'<circle cx="0" cy="0" r="20" fill="#FEF3C7" stroke="{OL}" stroke-width="4.2"/>'
        f'<polygon points="0,-13 5,0 0,13 -5,0" fill="#EF4444" stroke="{OL}" stroke-width="2.2"/>'
        f'<circle cx="0" cy="0" r="3" fill="{OL}"/>'
        f'</g>'
    )
    s5_raw = render_svg("".join([
        shd(150, 270, 98, 13, 0.16),
        _polaroid(56, 122, rot=-18, s=0.84, bg="#BAE6FD"),
        _polaroid(244, 118, rot=16, s=0.84, bg="#FBCFE8"),
        _polaroid(60, 224, rot=-12, s=0.80, bg="#FDE68A"),
        capy_sit(150, 264, s=0.96, mode="happy",
                 extra_head=_explorer_cap(150, 122, 1.02),
                 extra_belly=_travel_scarf(150, 210, 0.90) + _vintage_cam(150, 232, 0.70) + f'<ellipse cx="110" cy="232" rx="14.5" ry="10" fill="{SNOUT}" stroke="{OL}" stroke-width="4.6"/><ellipse cx="190" cy="232" rx="14.5" ry="10" fill="{SNOUT}" stroke="{OL}" stroke-width="4.6"/>'),
        sp4(200, 202, 17, "#FEF08A", "#EA580C", 3.2),
        compass,
        sp4(46, 56, 12, "#FDE047", "#0D9488"),
        sp4(254, 62, 12, "#FDBA74", "#EA580C"),
    ]))
    s5 = with_hero_aura(s5_raw, (94, 234, 212), 160)

    return [
        ("Camera Peek",   s0),
        ("Pack Ready",    s1),
        ("Spin Globe",    s2),
        ("Ready Snap",    s3),
        ("Flash Click!",  s4),
        ("Master Snap!",  s5),
    ]


# =========================================================================== #
#  SAVE ALL 72 NEW SPRITES + RENDER UPDATED 13-ROW CONTACT SHEET (v3.9.1)
# =========================================================================== #
def main():
    builders = [
        ("capybara_avocado",       build_48_avocado),
        ("capybara_onsen",         build_49_onsen),
        ("capybara_boba_pond",     build_51_boba_pond),
        ("capybara_bookworm",      build_52_bookworm),
        ("capybara_lofi_picnic",   build_53_lofi_picnic),
        ("capybara_foodie",        build_54_foodie),
        ("capybara_dino_hoodie",   build_55_dino_hoodie),
        ("capybara_apple_orchard", build_56_apple_orchard),
        ("capybara_pink_chill",    build_57_pink_chill),
        ("capybara_fairy_party",   build_58_fairy_party),
        ("capybara_selfcare",      build_59_selfcare),
        ("capybara_traveler",      build_60_traveler),
    ]

    results: dict[str, list[tuple[str, Image.Image]]] = {}
    hashes: set[str] = set()
    total = 0

    for slug, fn in builders:
        stages = fn()
        assert len(stages) == 6, f"{slug} expected 6 stages"
        d = ASSETS_DIR / slug
        d.mkdir(parents=True, exist_ok=True)
        for i, (_, im) in enumerate(stages):
            out_p = d / f"stage_{i}.png"
            im.save(out_p, "PNG", optimize=True)
            h = hashlib.sha256(out_p.read_bytes()).hexdigest()
            assert h not in hashes, f"DUPLICATE SPRITE DETECTED: {slug}/stage_{i}.png"
            hashes.add(h)
            total += 1
        results[slug] = stages
        print(f"  [STORY] {slug:24s} -> 6 unique 300x300 PNGs saved")

    # Load #50 Pip & Puddle UNTOUCHED from disk for the full 13-row contact sheet!
    pip_lbls = ["Nap Buddies", "Curious Duo", "Hello There!", "Snack Attack", "Besties Scarf", "Sending Love!"]
    results["capybara_pip_puddle"] = [
        (pip_lbls[i], Image.open(ASSETS_DIR / "capybara_pip_puddle" / f"stage_{i}.png").convert("RGBA"))
        for i in range(6)
    ]
    print(f"Total redesigned sprites saved: {total}/72 (100% unique SHA-256 hashes!)")

    # Render updated contact sheet (`previews/assets_contact_sheet_capybara.png`)
    rows = [
        ("48. Avocado Zen [Story]",    "capybara_avocado",       (246, 250, 238), (101, 163, 13)),
        ("49. Yuzu Onsen Spa",         "capybara_onsen",         (255, 251, 242), (249, 115, 22)),
        ("50. Pip & Puddle [Kept]",    "capybara_pip_puddle",    (255, 245, 248), (244, 114, 182)),
        ("51. Boba Lily Pond",         "capybara_boba_pond",     (239, 248, 255), (14, 165, 233)),
        ("52. Bookworm Study",         "capybara_bookworm",      (255, 253, 245), (202, 138, 4)),
        ("53. Lofi Picnic Beats",      "capybara_lofi_picnic",   (240, 247, 255), (37, 99, 235)),
        ("54. Foodie Snack Club",      "capybara_foodie",        (255, 251, 235), (239, 68, 68)),
        ("55. Dino Hoodie Play",       "capybara_dino_hoodie",   (244, 251, 246), (22, 163, 74)),
        ("56. Apple Orchard Sweet",    "capybara_apple_orchard", (255, 246, 237), (225, 29, 72)),
        ("57. Pink Cloud Chill",       "capybara_pink_chill",    (253, 242, 248), (219, 39, 119)),
        ("58. Fairy Party Wish",       "capybara_fairy_party",   (248, 245, 255), (147, 51, 234)),
        ("59. SelfCare GlowUp",        "capybara_selfcare",      (255, 249, 250), (244, 63, 94)),
        ("60. Snapshot Traveler",      "capybara_traveler",      (250, 247, 242), (13, 148, 136)),
    ]
    cell_w, cell_h = 204, 272
    left_w = 248
    pad = 18
    hdr_h = 84
    W = pad * 2 + left_w + cell_w * 6
    H = pad * 2 + hdr_h + cell_h * len(rows)

    sheet = Image.new("RGB", (W, H), (252, 250, 247))
    draw = ImageDraw.Draw(sheet)
    try:
        f_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 27)
        f_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 15.5)
        f_row = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 15)
        f_lbl = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 13)
        f_tiny = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 11)
    except Exception:
        f_title = f_sub = f_row = f_lbl = f_tiny = ImageFont.load_default()

    draw.rectangle([0, 0, W, hdr_h], fill=(74, 50, 40))
    draw.text((pad, 14), "CAPYBARA CHILL COLLECTION — #48–#60 (13 CONTINUOUS STORIES • 78 UNIQUE SPRITES)", fill=(255, 255, 255), font=f_title)
    draw.text((pad, 50), "Tiny Baby Capybara at 0% -> Big Radiant Hero at 100% • Zero Empty Starts • Zero Cross-Template Duplicates • 162px + 44px Excel Preview", fill=(254, 240, 138), font=f_sub)

    pcts = ["0% Baby", "1–24%", "25–49%", "50–74%", "75–99%", "100% MAX"]
    for r_i, (title, slug, bg_c, acc_c) in enumerate(rows):
        y0 = hdr_h + pad + r_i * cell_h
        draw.rounded_rectangle([pad, y0 + 4, W - pad, y0 + cell_h - 6], radius=14, fill=bg_c, outline=acc_c, width=2)
        draw.text((pad + 14, y0 + 114), title, fill=acc_c, font=f_row)
        for s_i, (lbl, im) in enumerate(results[slug]):
            x0 = pad + left_w + s_i * cell_w
            is_f = (s_i == 5)
            draw.rounded_rectangle([x0 + 6, y0 + 12, x0 + cell_w - 6, y0 + cell_h - 14],
                                   radius=10, fill=(255, 255, 255), outline=(acc_c if is_f else (226, 222, 218)), width=2 if is_f else 1)
            big = im.resize((162, 162), Image.LANCZOS)
            sheet.paste(big, (x0 + (cell_w - 162) // 2, y0 + 16), big)

            small = im.resize((44, 44), Image.LANCZOS)
            sx, sy = x0 + cell_w - 56, y0 + 182
            draw.rounded_rectangle([sx - 3, sy - 3, sx + 47, sy + 47], radius=6, fill=(250, 249, 247), outline=(210, 205, 200), width=1)
            sheet.paste(small, (sx, sy), small)

            draw.text((x0 + 12, y0 + 184), f"S{s_i} • {pcts[s_i]}", fill=acc_c, font=f_tiny)
            draw.text((x0 + 12, y0 + 206), lbl, fill=(58, 42, 34), font=f_lbl)
            draw.text((sx + 6, sy + 49), "44px", fill=(150, 142, 136), font=f_tiny)

    out_path = PREVIEWS_DIR / "assets_contact_sheet_capybara.png"
    sheet.save(out_path, "PNG", optimize=True)
    print(f"  [PREVIEW] Saved {out_path} ({sheet.size[0]}x{sheet.size[1]})")


if __name__ == "__main__":
    main()
