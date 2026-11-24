"""
extract_capybara_assets.py — Precision Extraction + Custom Kawaii Vector Pipeline for the
13 Capybara Themes (#48–#60, v3.9 — 78 Transparent 300x300px PNGs):
  48. `capybara_avocado`       (Custom 6-stage ultra-cute Avocado Capybara vector art!)
  49. `capybara_onsen`         (Yuzu Onsen Spa)
  50. `capybara_pip_puddle`    (Pip & Puddle Besties Duo)
  51. `capybara_boba_pond`     (Boba Lily Pond)
  52. `capybara_bookworm`      (Bookworm Study — Capy & Chaptered)
  53. `capybara_lofi_picnic`   (Lofi Picnic Beats)
  54. `capybara_foodie`        (Foodie Snack Club)
  55. `capybara_dino_hoodie`   (Dino Hoodie Play)
  56. `capybara_apple_orchard` (Apple Orchard Sweet)
  57. `capybara_pink_chill`    (Pink Cloud Chill)
  58. `capybara_fairy_party`   (Fairy Party Wish)
  59. `capybara_selfcare`      (SelfCare GlowUp)
  60. `capybara_traveler`      (Snapshot Traveler)

Outputs:
  - 78 transparent 300x300px PNGs in `assets/capybara_*/stage_0..5.png`
  - `previews/assets_contact_sheet_capybara.png` (BOTH 180px large & 44px actual Excel cell size!)
"""
from __future__ import annotations

import math
from pathlib import Path

import cv2
import numpy as np
import pymupdf
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
REF_DIR = ROOT / "references" / "batch7_capybara"
ASSETS_DIR = ROOT / "assets"
PREVIEWS_DIR = ROOT / "previews"

OL = "#4A3228"       # Warm thick Capybara dark-brown outline matching the sticker sheets!
FUR = "#D89E6A"      # Soft warm caramel capybara coat
FUR_SHD = "#C2824F"  # Gentle warm caramel shading
SNOUT = "#9A6644"    # Iconic darker rounded capybara snout
EAR_IN = "#875538"   # Inner ear brown
BLUSH = "#F6958D"    # Rosy kawaii cheek blush


# =========================================================================== #
#  3x SUPERSAMPLED SVG -> 300x300 TRANSPARENT PNG HELPER
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


def _sp4(cx, cy, r=10, fill="#FDE047", stroke="#B45309", sw=2.2) -> str:
    ir = r * 0.30
    d = (
        f"M {cx},{cy - r} Q {cx + ir},{cy - ir} {cx + r},{cy} "
        f"Q {cx + ir},{cy + ir} {cx},{cy + r} "
        f"Q {cx - ir},{cy + ir} {cx - r},{cy} "
        f"Q {cx - ir},{cy - ir} {cx},{cy - r} Z"
    )
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>'


def _mini_heart(cx, cy, s=12, fill="#FB7185", stroke=OL, sw=2.6) -> str:
    d = (
        f"M {cx},{cy + s * 0.72} "
        f"C {cx - s * 1.1},{cy + s * 0.05} {cx - s * 1.05},{cy - s * 0.85} {cx - s * 0.42},{cy - s * 0.85} "
        f"C {cx - s * 0.12},{cy - s * 0.85} {cx},{cy - s * 0.52} {cx},{cy - s * 0.38} "
        f"C {cx},{cy - s * 0.52} {cx + s * 0.12},{cy - s * 0.85} {cx + s * 0.42},{cy - s * 0.85} "
        f"C {cx + s * 1.05},{cy - s * 0.85} {cx + s * 1.1},{cy + s * 0.05} {cx},{cy + s * 0.72} Z"
    )
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>'


def _chibi_capy_head_face(cx, cy, scale=1.0, sleepy=False, happy=False) -> str:
    """Adorable chubby chibi Capybara face matching `09_photo.jpg` & `05_ref_b.jpg` proportions."""
    s = scale
    parts = [
        # Soft darker rounded snout centered neatly
        f'<ellipse cx="{cx:.1f}" cy="{cy + 14*s:.1f}" rx="{23*s:.1f}" ry="{18*s:.1f}" fill="{SNOUT}"/>',
        # Cute little nostrils
        f'<ellipse cx="{cx - 7*s:.1f}" cy="{cy + 8*s:.1f}" rx="{2.7*s:.1f}" ry="{2.1*s:.1f}" fill="{OL}"/>',
        f'<ellipse cx="{cx + 7*s:.1f}" cy="{cy + 8*s:.1f}" rx="{2.7*s:.1f}" ry="{2.1*s:.1f}" fill="{OL}"/>',
        # Sweet ":3" capybara mouth
        f'<path d="M {cx:.1f},{cy + 14*s:.1f} L {cx:.1f},{cy + 21*s:.1f} '
        f'M {cx - 9*s:.1f},{cy + 21*s:.1f} Q {cx - 4.5*s:.1f},{cy + 26*s:.1f} {cx:.1f},{cy + 21*s:.1f} '
        f'Q {cx + 4.5*s:.1f},{cy + 26*s:.1f} {cx + 9*s:.1f},{cy + 21*s:.1f}" '
        f'fill="none" stroke="{OL}" stroke-width="{3.6*s:.1f}" stroke-linecap="round" stroke-linejoin="round"/>',
        # Rosy kawaii cheeks
        f'<ellipse cx="{cx - 44*s:.1f}" cy="{cy + 16*s:.1f}" rx="{13*s:.1f}" ry="{9*s:.1f}" fill="{BLUSH}" fill-opacity="0.72"/>',
        f'<ellipse cx="{cx + 44*s:.1f}" cy="{cy + 16*s:.1f}" rx="{13*s:.1f}" ry="{9*s:.1f}" fill="{BLUSH}" fill-opacity="0.72"/>',
    ]
    if sleepy:
        parts.append(
            f'<path d="M {cx - 38*s:.1f},{cy + 2*s:.1f} Q {cx - 30*s:.1f},{cy + 9*s:.1f} {cx - 22*s:.1f},{cy + 2*s:.1f}" '
            f'fill="none" stroke="{OL}" stroke-width="{4.0*s:.1f}" stroke-linecap="round"/>'
            f'<path d="M {cx + 22*s:.1f},{cy + 2*s:.1f} Q {cx + 30*s:.1f},{cy + 9*s:.1f} {cx + 38*s:.1f},{cy + 2*s:.1f}" '
            f'fill="none" stroke="{OL}" stroke-width="{4.0*s:.1f}" stroke-linecap="round"/>'
        )
    elif happy:
        parts.append(
            f'<path d="M {cx - 38*s:.1f},{cy + 5*s:.1f} Q {cx - 30*s:.1f},{cy - 5*s:.1f} {cx - 22*s:.1f},{cy + 5*s:.1f}" '
            f'fill="none" stroke="{OL}" stroke-width="{4.2*s:.1f}" stroke-linecap="round"/>'
            f'<path d="M {cx + 22*s:.1f},{cy + 5*s:.1f} Q {cx + 30*s:.1f},{cy - 5*s:.1f} {cx + 38*s:.1f},{cy + 5*s:.1f}" '
            f'fill="none" stroke="{OL}" stroke-width="{4.2*s:.1f}" stroke-linecap="round"/>'
        )
    else:
        parts.append(
            f'<ellipse cx="{cx - 31*s:.1f}" cy="{cy + 1*s:.1f}" rx="{8.2*s:.1f}" ry="{9.5*s:.1f}" fill="{OL}"/>'
            f'<circle cx="{cx - 33.5*s:.1f}" cy="{cy - 2.2*s:.1f}" r="{3.2*s:.1f}" fill="#FFFFFF"/>'
            f'<ellipse cx="{cx + 31*s:.1f}" cy="{cy + 1*s:.1f}" rx="{8.2*s:.1f}" ry="{9.5*s:.1f}" fill="{OL}"/>'
            f'<circle cx="{cx + 28.5*s:.1f}" cy="{cy - 2.2*s:.1f}" r="{3.2*s:.1f}" fill="#FFFFFF"/>'
        )
    return "".join(parts)


# =========================================================================== #
#  TEMPLATE 48: CUSTOM ULTRA-CUTE AVOCADO CAPYBARA (6 STAGES!)
# =========================================================================== #
def build_avocado_capybara_set() -> list[tuple[str, Image.Image]]:
    """6 bespoke, ultra-cute squishy kawaii Avocado Capybara stages (300x300 transparent PNGs)."""
    skin = "#3F6212"
    lime = "#A3E635"
    flesh = "#ECFCCB"
    pit = "#854D0E"
    pit_hi = "#A16207"
    leaf = "#65A30D"

    # Stage 0: Cute half-cut smiling green avocado cushion with cozy round pit hollow & tiny leaf
    s0_svg = "".join([
        '<ellipse cx="150" cy="264" rx="74" ry="12" fill="#365314" fill-opacity="0.14"/>',
        # Tiny sprout leaf on top
        f'<path d="M 150,74 Q 124,48 114,66 Q 126,82 150,78 Z" fill="{leaf}" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>',
        f'<path d="M 150,74 Q 174,46 186,62 Q 174,80 150,78 Z" fill="#84CC16" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>',
        # Outer dark green pear-shaped avocado skin
        f'<path d="M 150,74 C 190,74 206,120 218,166 C 232,220 202,262 150,262 '
        f'C 98,262 68,220 82,166 C 94,120 110,74 150,74 Z" fill="{skin}" stroke="{OL}" stroke-width="6.5" stroke-linejoin="round"/>',
        # Bright lime-green inner rim + creamy butter flesh
        f'<path d="M 150,88 C 182,88 196,128 206,170 C 218,214 192,250 150,250 '
        f'C 108,250 82,214 94,170 C 104,128 118,88 150,88 Z" fill="{lime}"/>',
        f'<path d="M 150,100 C 176,100 188,136 196,172 C 206,208 184,238 150,238 '
        f'C 116,238 94,208 104,172 C 112,136 124,100 150,100 Z" fill="{flesh}"/>',
        # Cozy round brown pit hollow cushion
        f'<circle cx="150" cy="192" r="38" fill="{pit}" stroke="{OL}" stroke-width="5.5"/>',
        f'<ellipse cx="138" cy="178" rx="11" ry="7" transform="rotate(-25 138 178)" fill="{pit_hi}" fill-opacity="0.75"/>',
        # Cute little kawaii face on the upper avocado flesh!
        f'<circle cx="128" cy="134" r="5.5" fill="{OL}"/><circle cx="126.5" cy="132" r="2" fill="#FFFFFF"/>',
        f'<circle cx="172" cy="134" r="5.5" fill="{OL}"/><circle cx="170.5" cy="132" r="2" fill="#FFFFFF"/>',
        f'<path d="M 142,138 Q 150,147 158,138" fill="none" stroke="{OL}" stroke-width="3.8" stroke-linecap="round"/>',
        f'<ellipse cx="116" cy="142" rx="8" ry="4.5" fill="{BLUSH}" fill-opacity="0.65"/>',
        f'<ellipse cx="184" cy="142" rx="8" ry="4.5" fill="{BLUSH}" fill-opacity="0.65"/>',
    ])

    # Stage 1: Tiny sleepy baby Capybara curled up napping peacefully inside hollowed green avocado boat (zzz)
    s1_svg = "".join([
        '<ellipse cx="150" cy="264" rx="92" ry="13" fill="#365314" fill-opacity="0.14"/>',
        # Horizontal green avocado boat
        f'<path d="M 46,196 C 46,158 98,144 166,144 C 228,144 260,168 258,202 '
        f'C 256,242 214,262 152,262 C 84,262 46,238 46,196 Z" fill="{skin}" stroke="{OL}" stroke-width="6.5" stroke-linejoin="round"/>',
        f'<path d="M 60,196 C 60,166 106,154 166,154 C 218,154 246,174 244,200 '
        f'C 242,232 206,248 152,248 C 94,248 60,228 60,196 Z" fill="{lime}"/>',
        f'<path d="M 72,196 C 72,174 114,164 166,164 C 208,164 232,178 232,198 '
        f'C 230,222 198,236 152,236 C 104,236 72,220 72,196 Z" fill="{flesh}"/>',
        # Cozy pit hollow bed
        f'<ellipse cx="152" cy="202" rx="68" ry="26" fill="{pit}" fill-opacity="0.22"/>',
        # Tiny baby Capybara curled up napping inside!
        # Tiny rounded ears
        f'<ellipse cx="114" cy="142" rx="11" ry="12" transform="rotate(-18 114 142)" fill="{FUR}" stroke="{OL}" stroke-width="5"/>',
        f'<ellipse cx="158" cy="140" rx="11" ry="12" transform="rotate(16 158 140)" fill="{FUR}" stroke="{OL}" stroke-width="5"/>',
        # Squishy loaf body
        f'<path d="M 88,196 C 84,158 106,138 144,138 C 188,138 220,160 220,196 '
        f'C 220,218 196,226 152,226 C 106,226 88,218 88,196 Z" fill="{FUR}" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>',
        # Cute front paws tucked
        f'<ellipse cx="106" cy="218" rx="13" ry="8" fill="{SNOUT}" stroke="{OL}" stroke-width="4.5"/>',
        f'<ellipse cx="144" cy="220" rx="13" ry="8" fill="{SNOUT}" stroke="{OL}" stroke-width="4.5"/>',
        # Sleepy baby face (shifted left)
        _chibi_capy_head_face(128, 178, scale=0.72, sleepy=True),
        # Cute floating "z Z"
        f'<text x="206" y="128" font-family="Segoe UI" font-weight="bold" font-size="22" fill="{OL}">z</text>',
        f'<text x="224" y="108" font-family="Segoe UI" font-weight="bold" font-size="28" fill="{OL}">Z</text>',
    ])

    # Stage 2: Squishy sitting Capybara balancing a cute mini halved avocado on top of its head!
    s2_svg = "".join([
        '<ellipse cx="150" cy="266" rx="78" ry="12" fill="#365314" fill-opacity="0.14"/>',
        # Rounded ears
        f'<ellipse cx="102" cy="116" rx="14" ry="16" transform="rotate(-18 102 116)" fill="{FUR}" stroke="{OL}" stroke-width="5.8"/>',
        f'<ellipse cx="102" cy="118" rx="7" ry="9" transform="rotate(-18 102 118)" fill="{EAR_IN}"/>',
        f'<ellipse cx="198" cy="116" rx="14" ry="16" transform="rotate(18 198 116)" fill="{FUR}" stroke="{OL}" stroke-width="5.8"/>',
        f'<ellipse cx="198" cy="118" rx="7" ry="9" transform="rotate(18 198 118)" fill="{EAR_IN}"/>',
        # Squishy pear-loaf chibi Capybara body (matching 09_photo.jpg!)
        f'<path d="M 78,202 C 74,142 104,106 150,106 C 196,106 226,142 224,202 '
        f'C 224,244 196,262 150,262 C 104,262 78,244 78,202 Z" fill="{FUR}" stroke="{OL}" stroke-width="6.5" stroke-linejoin="round"/>',
        # Soft bottom warm shading
        f'<path d="M 90,236 C 114,258 186,258 210,236 C 196,260 104,260 90,236 Z" fill="{FUR_SHD}" fill-opacity="0.65"/>',
        # Cute stubby tucked front feet (2 natural paws!)
        f'<ellipse cx="118" cy="256" rx="18" ry="11" fill="{SNOUT}" stroke="{OL}" stroke-width="5"/>',
        f'<ellipse cx="182" cy="256" rx="18" ry="11" fill="{SNOUT}" stroke="{OL}" stroke-width="5"/>',
        # Adorable chibi face
        _chibi_capy_head_face(150, 166, scale=1.0),
        # Cute mini halved avocado balanced on top of head!
        f'<path d="M 150,34 C 170,34 182,58 184,82 C 186,102 170,114 150,114 '
        f'C 130,114 114,102 116,82 C 118,58 130,34 150,34 Z" fill="{skin}" stroke="{OL}" stroke-width="5.5"/>',
        f'<path d="M 150,44 C 164,44 174,64 175,82 C 176,96 164,104 150,104 '
        f'C 136,104 124,96 125,82 C 126,64 136,44 150,44 Z" fill="{lime}"/>',
        f'<path d="M 150,52 C 160,52 168,68 168,82 C 168,92 160,98 150,98 '
        f'C 140,98 132,92 132,82 C 132,68 140,52 150,52 Z" fill="{flesh}"/>',
        f'<circle cx="150" cy="84" r="13" fill="{pit}" stroke="{OL}" stroke-width="3.8"/>',
        f'<path d="M 150,34 Q 168,18 180,30 Q 168,42 150,38 Z" fill="{leaf}" stroke="{OL}" stroke-width="3.8"/>',
    ])

    # Stage 3: Happy chubby Capybara sitting neatly and hugging a plump smiling kawaii avocado!
    s3_svg = "".join([
        '<ellipse cx="150" cy="268" rx="86" ry="13" fill="#365314" fill-opacity="0.14"/>',
        # Rounded ears
        f'<ellipse cx="102" cy="88" rx="14" ry="16" transform="rotate(-18 102 88)" fill="{FUR}" stroke="{OL}" stroke-width="5.8"/>',
        f'<ellipse cx="102" cy="90" rx="7" ry="9" transform="rotate(-18 102 90)" fill="{EAR_IN}"/>',
        f'<ellipse cx="198" cy="88" rx="14" ry="16" transform="rotate(18 198 88)" fill="{FUR}" stroke="{OL}" stroke-width="5.8"/>',
        f'<ellipse cx="198" cy="90" rx="7" ry="9" transform="rotate(18 198 90)" fill="{EAR_IN}"/>',
        # Chubby sitting body
        f'<path d="M 74,186 C 72,114 102,78 150,78 C 198,78 228,114 226,186 '
        f'C 226,242 198,264 150,264 C 102,264 74,242 74,186 Z" fill="{FUR}" stroke="{OL}" stroke-width="6.5" stroke-linejoin="round"/>',
        # Happy smiling face
        _chibi_capy_head_face(150, 128, scale=0.96, happy=True),
        # Plump kawaii avocado hugged right in front of belly!
        f'<path d="M 150,162 C 174,162 188,188 192,216 C 196,244 176,262 150,262 '
        f'C 124,262 104,244 108,216 C 112,188 126,162 150,162 Z" fill="{skin}" stroke="{OL}" stroke-width="5.5"/>',
        f'<path d="M 150,172 C 168,172 180,194 182,216 C 184,238 170,252 150,252 '
        f'C 130,252 116,238 118,216 C 120,194 132,172 150,172 Z" fill="{lime}"/>',
        f'<path d="M 150,180 C 164,180 174,198 175,216 C 176,232 164,244 150,244 '
        f'C 136,244 124,232 125,216 C 126,198 136,180 150,180 Z" fill="{flesh}"/>',
        f'<circle cx="150" cy="224" r="18" fill="{pit}" stroke="{OL}" stroke-width="4"/>',
        # Tiny kawaii smile on the hugged avocado
        f'<circle cx="139" cy="196" r="3" fill="{OL}"/><circle cx="161" cy="196" r="3" fill="{OL}"/>',
        f'<path d="M 145,200 Q 150,205 155,200" fill="none" stroke="{OL}" stroke-width="2.8" stroke-linecap="round"/>',
        # Chubby curved hugging paws wrapping the avocado neatly (ZERO stick arms!)
        f'<path d="M 88,188 C 86,214 106,226 124,218 C 134,212 128,194 114,194" fill="{SNOUT}" stroke="{OL}" stroke-width="5.2" stroke-linecap="round" stroke-linejoin="round"/>',
        f'<path d="M 212,188 C 214,214 194,226 176,218 C 166,212 172,194 186,194" fill="{SNOUT}" stroke="{OL}" stroke-width="5.2" stroke-linecap="round" stroke-linejoin="round"/>',
        # Cute stubby sitting feet beside avocado
        f'<ellipse cx="98" cy="258" rx="18" ry="11" fill="{SNOUT}" stroke="{OL}" stroke-width="5"/>',
        f'<ellipse cx="202" cy="258" rx="18" ry="11" fill="{SNOUT}" stroke="{OL}" stroke-width="5"/>',
        _mini_heart(228, 92, 14, "#FB7185"),
    ])

    # Stage 4: Adorable Capybara wearing a cozy GREEN AVOCADO ONESIE/HOODIE with brown pit tummy!
    s4_svg = "".join([
        '<ellipse cx="150" cy="268" rx="84" ry="13" fill="#365314" fill-opacity="0.14"/>',
        # Sprout leaf on top of avocado hood!
        f'<path d="M 150,56 Q 128,32 118,48 Q 128,62 150,60 Z" fill="{leaf}" stroke="{OL}" stroke-width="4.5" stroke-linejoin="round"/>',
        f'<path d="M 150,56 Q 172,32 184,48 Q 174,62 150,60 Z" fill="#84CC16" stroke="{OL}" stroke-width="4.5" stroke-linejoin="round"/>',
        # Cozy plush green Avocado Onesie silhouette (matches Dino Hoodie charm!)
        f'<path d="M 150,58 C 204,58 232,102 232,162 C 232,226 206,262 150,262 '
        f'C 94,262 68,226 68,162 C 68,102 96,58 150,58 Z" fill="{skin}" stroke="{OL}" stroke-width="6.5" stroke-linejoin="round"/>',
        # Bright lime hoodie lining
        f'<path d="M 150,70 C 194,70 218,108 218,162 C 218,216 196,248 150,248 '
        f'C 104,248 82,216 82,162 C 82,108 106,70 150,70 Z" fill="{lime}"/>',
        # Creamy avocado belly patch + round brown pit tummy!
        f'<ellipse cx="150" cy="212" rx="52" ry="38" fill="{flesh}" stroke="{OL}" stroke-width="4"/>',
        f'<circle cx="150" cy="216" r="22" fill="{pit}" stroke="{OL}" stroke-width="4.5"/>',
        f'<ellipse cx="143" cy="208" rx="6" ry="4" transform="rotate(-25 143 208)" fill="{pit_hi}"/>',
        # Cozy hood opening showing cute Capybara face!
        f'<ellipse cx="150" cy="128" rx="54" ry="44" fill="{FUR}" stroke="{OL}" stroke-width="5.5"/>',
        # Cute little hood tie-bow under chin!
        f'<path d="M 150,172 Q 134,166 132,178 Q 140,184 150,176 Q 160,184 168,178 Q 166,166 150,172 Z" fill="#65A30D" stroke="{OL}" stroke-width="3.5"/>',
        # Cute Capybara face inside hood
        _chibi_capy_head_face(150, 124, scale=0.84),
        # Cute stubby paws & feet poking out of onesie
        f'<ellipse cx="102" cy="198" rx="15" ry="11" transform="rotate(20 102 198)" fill="{SNOUT}" stroke="{OL}" stroke-width="4.8"/>',
        f'<ellipse cx="198" cy="198" rx="15" ry="11" transform="rotate(-20 198 198)" fill="{SNOUT}" stroke="{OL}" stroke-width="4.8"/>',
        f'<ellipse cx="114" cy="258" rx="17" ry="11" fill="{SNOUT}" stroke="{OL}" stroke-width="5"/>',
        f'<ellipse cx="186" cy="258" rx="17" ry="11" fill="{SNOUT}" stroke="{OL}" stroke-width="5"/>',
        _sp4(60, 82, 11, "#FDE047", "#B45309"),
        _sp4(240, 86, 10, "#BEF264", "#3F6212"),
    ])

    # Stage 5: Blissful Chill King Avocado Capybara lounging in lush avocado boat, tiny crown + avocado toast heart + sunny soft aura!
    s5_svg = "".join([
        '<ellipse cx="150" cy="268" rx="102" ry="13" fill="#365314" fill-opacity="0.16"/>',
        # Lush big Avocado Boat!
        f'<path d="M 32,202 C 34,158 92,148 150,148 C 208,148 266,158 268,202 '
        f'C 268,246 218,266 150,266 C 82,266 32,246 32,202 Z" fill="{skin}" stroke="{OL}" stroke-width="6.5" stroke-linejoin="round"/>',
        f'<path d="M 46,200 C 48,166 100,158 150,158 C 200,158 252,166 254,200 '
        f'C 254,234 210,252 150,252 C 90,252 46,234 46,200 Z" fill="{lime}"/>',
        f'<path d="M 62,198 C 64,174 106,166 150,166 C 194,166 236,174 238,198 '
        f'C 238,224 202,240 150,240 C 98,240 62,224 62,198 Z" fill="{flesh}"/>',
        # Happy King Capybara lounging upright in the avocado boat!
        f'<ellipse cx="106" cy="96" rx="13" ry="15" transform="rotate(-18 106 96)" fill="{FUR}" stroke="{OL}" stroke-width="5.5"/>',
        f'<ellipse cx="194" cy="96" rx="13" ry="15" transform="rotate(18 194 96)" fill="{FUR}" stroke="{OL}" stroke-width="5.5"/>',
        f'<path d="M 86,184 C 84,122 108,86 150,86 C 192,86 216,122 214,184 '
        f'C 214,218 188,230 150,230 C 112,230 86,218 86,184 Z" fill="{FUR}" stroke="{OL}" stroke-width="6.2" stroke-linejoin="round"/>',
        # Blissful happy face
        _chibi_capy_head_face(150, 136, scale=0.92, happy=True),
        # Golden Avocado King Crown + tiny sprout on head!
        f'<path d="M 122,86 L 116,52 L 138,68 L 150,44 L 162,68 L 184,52 L 178,86 Z" '
        f'fill="#FACC15" stroke="{OL}" stroke-width="4.8" stroke-linejoin="round"/>',
        f'<circle cx="150" cy="70" r="6.5" fill="{leaf}" stroke="{OL}" stroke-width="2.8"/>',
        f'<circle cx="131" cy="74" r="4.5" fill="#FB7185"/>',
        f'<circle cx="169" cy="74" r="4.5" fill="#FB7185"/>',
        # Cute Avocado Toast Heart held neatly by chubby paws!
        f'<rect x="122" y="176" width="56" height="46" rx="12" fill="#D97706" stroke="{OL}" stroke-width="4.5"/>',
        f'<rect x="128" y="182" width="44" height="34" rx="8" fill="#FEF3C7"/>',
        f'<rect x="132" y="186" width="36" height="26" rx="6" fill="{lime}"/>',
        _mini_heart(150, 199, 10, "#FB7185", OL, 2.5),
        f'<ellipse cx="118" cy="202" rx="14" ry="10" fill="{SNOUT}" stroke="{OL}" stroke-width="4.5"/>',
        f'<ellipse cx="182" cy="202" rx="14" ry="10" fill="{SNOUT}" stroke="{OL}" stroke-width="4.5"/>',
        # Golden & lime sparkles!
        _sp4(54, 72, 13, "#FDE047", "#B45309"),
        _sp4(248, 76, 12, "#FDE047", "#B45309"),
        _sp4(42, 146, 9, "#BEF264", "#3F6212"),
        _sp4(258, 148, 10, "#FDA4AF", "#9F1239"),
        _mini_heart(224, 114, 10, "#FB7185"),
    ])

    s5_im = render_svg(s5_svg)
    # Add clean, soft sunny lime-gold Gaussian aura strictly inside canvas (zero hard circle edge!)
    aura = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
    ad = ImageDraw.Draw(aura)
    ad.ellipse([48, 46, 252, 250], fill=(217, 249, 157, 72))
    ad.ellipse([76, 74, 224, 222], fill=(254, 249, 195, 92))
    aura = aura.filter(ImageFilter.GaussianBlur(radius=22))
    s5_final = Image.alpha_composite(aura, s5_im)

    return [
        ("Avocado\nCushion",  render_svg(s0_svg)),
        ("Nap Boat",          render_svg(s1_svg)),
        ("Head\nAvocado",     render_svg(s2_svg)),
        ("Avocado\nHug",      render_svg(s3_svg)),
        ("Avocado\nOnesie",   render_svg(s4_svg)),
        ("Avocado\nKing!",    s5_final),
    ]


# =========================================================================== #
#  CUSTOM THICK-OUTLINE KAWAII STAGE_0 BASE ICONS FOR TEMPLATES 49..60
# =========================================================================== #
def draw_capy_stage0(kind: str) -> Image.Image:
    shd = '<ellipse cx="150" cy="264" rx="76" ry="12" fill="#4A3228" fill-opacity="0.13"/>'
    if kind == "onsen":
        svg = shd + (
            # Steam puffs
            f'<path d="M 112,118 Q 104,96 116,80 M 150,108 Q 142,84 154,66 M 188,118 Q 180,96 192,80" '
            f'fill="none" stroke="#93C5FD" stroke-width="6.5" stroke-linecap="round"/>'
            # Wooden hinoki tub
            f'<path d="M 64,158 L 78,252 Q 150,270 222,252 L 236,158 Z" fill="#C2824F" stroke="{OL}" stroke-width="6.5" stroke-linejoin="round"/>'
            f'<ellipse cx="150" cy="158" rx="86" ry="24" fill="#BAE6FD" stroke="{OL}" stroke-width="6.5"/>'
            f'<ellipse cx="150" cy="158" rx="72" ry="16" fill="#E0F2FE"/>'
            # Floating cute yuzu
            f'<circle cx="132" cy="156" r="15" fill="#FB923C" stroke="{OL}" stroke-width="4"/>'
            f'<path d="M 132,141 Q 144,132 148,140 Q 140,146 132,144 Z" fill="#65A30D" stroke="{OL}" stroke-width="2.5"/>'
            # Folded white spa towel on right edge
            f'<path d="M 186,162 Q 214,162 216,184 L 214,224 Q 198,230 184,222 L 182,174 Z" fill="#FFFFFF" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
            # Wooden plank lines
            f'<line x1="106" y1="180" x2="112" y2="256" stroke="{OL}" stroke-width="3.5"/>'
            f'<line x1="150" y1="184" x2="150" y2="262" stroke="{OL}" stroke-width="3.5"/>'
        )
    elif kind == "boba_pond":
        svg = shd + (
            # Water ripple & lily pad
            '<ellipse cx="150" cy="236" rx="108" ry="26" fill="#BAE6FD" fill-opacity="0.7"/>'
            f'<path d="M 56,226 C 56,196 102,184 150,188 L 136,216 L 172,190 C 216,194 246,208 244,230 '
            f'C 242,254 198,262 150,262 C 98,262 56,250 56,226 Z" fill="#86EFAC" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>'
            # Cute strawberry boba cup
            f'<path d="M 148,118 L 154,68 L 166,70 L 160,118 Z" fill="#93C5FD" stroke="{OL}" stroke-width="4.2"/>'
            f'<path d="M 114,126 L 124,220 Q 150,228 176,220 L 186,126 Z" fill="#FCE7F3" stroke="{OL}" stroke-width="5.5" stroke-linejoin="round"/>'
            f'<path d="M 118,156 Q 134,148 150,156 Q 166,164 182,156 L 176,218 Q 150,226 124,218 Z" fill="#F9A8D4"/>'
            f'<ellipse cx="150" cy="126" rx="38" ry="10" fill="#E0F2FE" stroke="{OL}" stroke-width="5"/>'
            + "".join(f'<circle cx="{bx}" cy="{by}" r="6.5" fill="{OL}"/>' for bx, by in [(136,204),(150,208),(164,204),(143,190),(157,190)])
        )
    elif kind == "bookworm":
        svg = shd + (
            # Stack of 3 colorful books (gold, rose, sky)
            f'<rect x="66" y="212" width="168" height="44" rx="10" fill="#F59E0B" stroke="{OL}" stroke-width="5.8"/>'
            f'<rect x="86" y="220" width="136" height="28" rx="4" fill="#FFFBEB" stroke="{OL}" stroke-width="3.5"/>'
            f'<rect x="78" y="168" width="152" height="44" rx="10" fill="#F472B6" stroke="{OL}" stroke-width="5.8"/>'
            f'<rect x="88" y="176" width="124" height="28" rx="4" fill="#FFF1F2" stroke="{OL}" stroke-width="3.5"/>'
            f'<rect x="72" y="124" width="156" height="44" rx="10" fill="#38BDF8" stroke="{OL}" stroke-width="5.8"/>'
            f'<rect x="92" y="132" width="124" height="28" rx="4" fill="#F0F9FF" stroke="{OL}" stroke-width="3.5"/>'
            # Cute bookmark ribbon + tiny orange on top
            f'<polygon points="104,228 120,228 120,270 112,260 104,270" fill="#FDE047" stroke="{OL}" stroke-width="3.5"/>'
            f'<circle cx="150" cy="96" r="26" fill="#FB923C" stroke="{OL}" stroke-width="5.5"/>'
            f'<path d="M 150,70 Q 170,54 180,68 Q 168,78 150,74 Z" fill="#65A30D" stroke="{OL}" stroke-width="3.8"/>'
        )
    elif kind == "lofi_picnic":
        svg = shd + (
            # Red gingham picnic mat diamond
            f'<polygon points="150,174 264,218 150,264 36,218" fill="#FFFFFF" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>'
            f'<polygon points="150,184 244,218 150,254 56,218" fill="#FB7185" fill-opacity="0.55"/>'
            # Woven picnic basket
            f'<path d="M 104,148 Q 150,82 196,148" fill="none" stroke="{OL}" stroke-width="10" stroke-linecap="round"/>'
            f'<path d="M 104,148 Q 150,82 196,148" fill="none" stroke="#D97706" stroke-width="4.5" stroke-linecap="round"/>'
            f'<circle cx="132" cy="144" r="18" fill="#EF4444" stroke="{OL}" stroke-width="4.5"/>'
            f'<circle cx="166" cy="144" r="18" fill="#FB923C" stroke="{OL}" stroke-width="4.5"/>'
            f'<path d="M 92,148 L 106,218 Q 150,228 194,218 L 208,148 Z" fill="#FCD34D" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>'
            f'<rect x="86" y="140" width="128" height="18" rx="8" fill="#D97706" stroke="{OL}" stroke-width="5.5"/>'
        )
    elif kind == "foodie":
        svg = shd + (
            # Cute strawberry milk carton!
            f'<path d="M 102,130 L 150,82 L 198,130 L 198,252 Q 150,262 102,252 Z" fill="#FFFFFF" stroke="{OL}" stroke-width="6.2" stroke-linejoin="round"/>'
            f'<rect x="104" y="130" width="92" height="18" fill="#F9A8D4" stroke="{OL}" stroke-width="4.5"/>'
            f'<path d="M 106,184 Q 128,174 150,184 Q 172,194 194,184 L 194,248 Q 150,256 106,248 Z" fill="#FDA4AF"/>'
            f'<path d="M 140,86 L 140,56 L 172,46" fill="none" stroke="{OL}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="M 140,86 L 140,56 L 172,46" fill="none" stroke="#F43F5E" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>'
            + _mini_heart(150, 214, 15, "#E11D48")
        )
    elif kind == "dino_hoodie":
        svg = shd + (
            # Green clover cushion + tiny smiling yellow duckling!
            f'<ellipse cx="150" cy="236" rx="82" ry="24" fill="#86EFAC" stroke="{OL}" stroke-width="6"/>'
            f'<ellipse cx="150" cy="186" rx="54" ry="44" fill="#FDE047" stroke="{OL}" stroke-width="6"/>'
            f'<circle cx="150" cy="134" r="36" fill="#FDE047" stroke="{OL}" stroke-width="6"/>'
            f'<ellipse cx="150" cy="144" rx="14" ry="9" fill="#FB923C" stroke="{OL}" stroke-width="4"/>'
            f'<circle cx="134" cy="130" r="5" fill="{OL}"/><circle cx="166" cy="130" r="5" fill="{OL}"/>'
            f'<ellipse cx="122" cy="140" rx="7" ry="4" fill="{BLUSH}" fill-opacity="0.7"/>'
            f'<ellipse cx="178" cy="140" rx="7" ry="4" fill="{BLUSH}" fill-opacity="0.7"/>'
        )
    elif kind == "apple_orchard":
        svg = shd + (
            f'<path d="M 150,104 L 154,68" stroke="{OL}" stroke-width="8" stroke-linecap="round"/>'
            f'<path d="M 152,88 Q 186,62 204,84 Q 184,106 152,94 Z" fill="#22C55E" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
            f'<path d="M 150,114 C 114,96 70,126 74,182 C 78,236 116,262 150,256 '
            f'C 184,262 222,236 226,182 C 230,126 186,96 150,114 Z" fill="#E11D48" stroke="{OL}" stroke-width="6.5" stroke-linejoin="round"/>'
            '<ellipse cx="112" cy="152" rx="12" ry="22" transform="rotate(20 112 152)" fill="#FDA4AF" fill-opacity="0.7"/>'
            + _mini_heart(224, 96, 13, "#FB7185")
        )
    elif kind == "pink_chill":
        svg = shd + (
            # Soft pastel pink cloud pillow with rosy cheeks
            f'<path d="M 64,220 C 44,220 42,174 72,164 C 74,126 114,108 148,122 '
            f'C 178,104 222,124 224,162 C 256,168 258,220 232,226 '
            f'C 210,254 90,254 64,220 Z" fill="#FBCFE8" stroke="{OL}" stroke-width="6.5" stroke-linejoin="round"/>'
            f'<circle cx="126" cy="184" r="6" fill="{OL}"/><circle cx="174" cy="184" r="6" fill="{OL}"/>'
            f'<path d="M 142,190 Q 150,198 158,190" fill="none" stroke="{OL}" stroke-width="4" stroke-linecap="round"/>'
            f'<ellipse cx="108" cy="192" rx="10" ry="5.5" fill="#F472B6" fill-opacity="0.55"/>'
            f'<ellipse cx="192" cy="192" rx="10" ry="5.5" fill="#F472B6" fill-opacity="0.55"/>'
        )
    elif kind == "fairy_party":
        svg = shd + (
            # Pastel pink wrapped gift box with gold ribbon & wishing star
            f'<rect x="78" y="138" width="144" height="122" rx="14" fill="#F9A8D4" stroke="{OL}" stroke-width="6.5"/>'
            f'<rect x="68" y="114" width="164" height="34" rx="10" fill="#F472B6" stroke="{OL}" stroke-width="6.5"/>'
            f'<rect x="136" y="114" width="28" height="146" fill="#FDE047" stroke="{OL}" stroke-width="4.5"/>'
            f'<path d="M 150,114 C 118,74 96,98 122,114 Z" fill="#FDE047" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
            f'<path d="M 150,114 C 182,74 204,98 178,114 Z" fill="#FDE047" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
            + _sp4(228, 76, 14, "#FDE047", "#B45309")
        )
    elif kind == "selfcare":
        svg = shd + (
            # Cozy pink vanity mirror & golden sparkles!
            f'<rect x="138" y="198" width="24" height="62" rx="10" fill="#FB7185" stroke="{OL}" stroke-width="5.8"/>'
            f'<ellipse cx="150" cy="134" rx="58" ry="70" fill="#FDA4AF" stroke="{OL}" stroke-width="6.2"/>'
            f'<ellipse cx="150" cy="134" rx="44" ry="54" fill="#E0F2FE" stroke="{OL}" stroke-width="4.2"/>'
            '<line x1="122" y1="112" x2="146" y2="88" stroke="#FFFFFF" stroke-width="7" stroke-linecap="round"/>'
            '<line x1="126" y1="138" x2="162" y2="102" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round"/>'
            + _sp4(150, 52, 13, "#FDE047", "#B45309") + _sp4(224, 102, 10, "#C4B5FD", "#6D28D9")
        )
    else:  # traveler
        svg = shd + (
            # Cute vintage teal & sand instant polaroid camera!
            f'<rect x="64" y="114" width="172" height="134" rx="22" fill="#FAF7F2" stroke="{OL}" stroke-width="6.5"/>'
            f'<rect x="64" y="148" width="172" height="62" fill="#0D9488" stroke="{OL}" stroke-width="5"/>'
            f'<rect x="88" y="96" width="38" height="20" rx="6" fill="#EA580C" stroke="{OL}" stroke-width="5"/>'
            f'<circle cx="150" cy="180" r="38" fill="#E2E8F0" stroke="{OL}" stroke-width="5.5"/>'
            f'<circle cx="150" cy="180" r="25" fill="#1E293B" stroke="{OL}" stroke-width="4.5"/>'
            '<circle cx="141" cy="171" r="7" fill="#FFFFFF" fill-opacity="0.8"/>'
            f'<rect x="192" y="124" width="24" height="14" rx="4" fill="#FDE047" stroke="{OL}" stroke-width="3.5"/>'
        )
    return render_svg(svg)


# =========================================================================== #
#  EXTRACTION HELPERS FOR ALL 9 CAPYBARA REFERENCE SHEETS
# =========================================================================== #
def _trim(im: Image.Image) -> Image.Image:
    bb = im.getbbox()
    return im if bb is None else im.crop(bb)


def extract_flat_bg(
    rgb: np.ndarray,
    crop: tuple[int, int, int, int] | None = None,
    bg_rgb: tuple[int, int, int] | None = None,
    dist_thr: float = 34.0,
    also_white: bool = False,
    erase_boxes: list[tuple[int, int, int, int]] | None = None,
    keep_min_area_frac: float = 0.002,
    min_keep_px: int = 18,
    strip_gray_border: bool = False,
    punch_interior_bg_thr: float = 0.0,
) -> Image.Image:
    """Border-flood-fill removal for flat-background Capybara stickers (preserves ALL interior white/pink!)."""
    if crop is not None:
        x0, y0, x1, y1 = crop
        sub = rgb[y0:y1, x0:x1].copy()
    else:
        x0, y0 = 0, 0
        sub = rgb.copy()

    if bg_rgb is None:
        bg_rgb = tuple(int(v) for v in sub[2, 2])

    if erase_boxes:
        h, w = sub.shape[:2]
        for a, b, c, d in erase_boxes:
            sub[max(0, b - y0):min(h, d - y0), max(0, a - x0):min(w, c - x0)] = bg_rgb

    pad = 4
    sub = cv2.copyMakeBorder(sub, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=bg_rgb)
    sub_f = sub.astype(np.float32)
    bg_arr = np.array(bg_rgb, dtype=np.float32)
    dist = np.linalg.norm(sub_f - bg_arr[None, None, :], axis=-1)

    r, g, b = sub[:, :, 0].astype(np.int16), sub[:, :, 1].astype(np.int16), sub[:, :, 2].astype(np.int16)
    cmin = np.minimum(np.minimum(r, g), b)
    cmax = np.maximum(np.maximum(r, g), b)
    sat = cmax - cmin

    is_bg = dist <= dist_thr
    if also_white:
        # Also remove white die-cut sticker rim & faint beige outer shadow around `05_ref_b.jpg`, stopping hard at dark brown outline!
        is_bg = is_bg | ((cmin >= 212) & (sat <= 38))
    if strip_gray_border:
        # For `09_photo.jpg` subtle gray die-cut outer sticker ring
        is_bg = is_bg | ((cmin >= 200) & (sat <= 16))

    _, labels = cv2.connectedComponents(is_bg.astype(np.uint8), connectivity=4)
    border_labels = (
        set(labels[0, :].tolist()) | set(labels[-1, :].tolist())
        | set(labels[:, 0].tolist()) | set(labels[:, -1].tolist())
    )
    border_labels.discard(0)
    bg_mask = np.isin(labels, list(border_labels))
    if punch_interior_bg_thr > 0.0:
        # Clean enclosed exact-sky holes (e.g. under headphone arch in `06_img.jpg`)
        bg_mask = bg_mask | (dist <= punch_interior_bg_thr)
    fg_mask = (~bg_mask).astype(np.uint8)

    # Filter stray dust specks while preserving cute floating hearts, Zzz, music notes, stars!
    n_fg, fg_labels, stats, _ = cv2.connectedComponentsWithStats(fg_mask, connectivity=8)
    if n_fg > 1:
        max_area = int(stats[1:, cv2.CC_STAT_AREA].max())
        min_keep = max(min_keep_px, int(max_area * keep_min_area_frac))
        clean_fg = np.zeros_like(fg_mask)
        for cid in range(1, n_fg):
            if stats[cid, cv2.CC_STAT_AREA] >= min_keep:
                clean_fg[fg_labels == cid] = 1
        fg_mask = clean_fg

    # Smooth 1px anti-aliased edge matting (zero colored fringe!)
    alpha = (fg_mask * 255).astype(np.uint8)
    k3 = np.ones((3, 3), np.uint8)
    eroded = cv2.erode(fg_mask, k3, iterations=1)
    rim = (fg_mask == 1) & (eroded == 0)
    rim_bgish = rim & (dist <= dist_thr * 1.9)
    alpha[rim_bgish] = np.clip((dist[rim_bgish] / (dist_thr * 1.9)) * 230, 0, 225).astype(np.uint8)

    sub = sub[pad:-pad, pad:-pad]
    alpha = alpha[pad:-pad, pad:-pad]
    return _trim(Image.fromarray(np.dstack([sub, alpha]), "RGBA"))


def compose_capy_300(
    sprite: Image.Image,
    stage: int,
    sparkle_rgb: tuple[int, int, int] | None = None,
    size: int = 300,
) -> Image.Image:
    """Bottom-align sprite cleanly onto 300x300 transparent canvas + tasteful sparkles on stage_5!"""
    sprite = _trim(sprite)
    sw, sh = sprite.size
    if sw == 0 or sh == 0:
        return Image.new("RGBA", (size, size), (0, 0, 0, 0))

    max_box = {0: 214, 1: 230, 2: 244, 3: 256, 4: 268, 5: 278}[stage]
    bot_pad = {0: 18, 1: 16, 2: 14, 3: 13, 4: 12, 5: 10}[stage]
    scale = min(max_box / sw, max_box / sh)
    nw = max(1, int(round(sw * scale)))
    nh = max(1, int(round(sh * scale)))
    resized = sprite.resize((nw, nh), Image.LANCZOS)

    x = (size - nw) // 2
    # Lift wide-aspect duos slightly toward vertical center so they never sit squashed at the bottom edge
    if nh < nw * 0.68:
        y = max(4, int(size - bot_pad - nh - (size - nh - 2 * bot_pad) * 0.34))
    else:
        y = max(4, size - bot_pad - nh)

    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    if sparkle_rgb is not None:
        aura = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ad = ImageDraw.Draw(aura)
        ar, ag, ab = sparkle_rgb
        cx, cy = size // 2, y + nh // 2
        ad.ellipse([cx - 114, cy - 114, cx + 114, cy + 114], fill=(ar, ag, ab, 36))
        ad.ellipse([cx - 78, cy - 78, cx + 78, cy + 78], fill=(255, 250, 220, 58))
        aura = aura.filter(ImageFilter.GaussianBlur(radius=18))
        canvas = Image.alpha_composite(canvas, aura)

        sd = ImageDraw.Draw(canvas)
        sp_pts = (
            [(38, 38, 11), (262, 42, 10), (76, 76, 7), (226, 72, 8)]
            if y > 88 else
            [(36, 40, 11), (264, 44, 10), (30, 174, 8), (270, 178, 9)]
        )
        for sx, sy, sr in sp_pts:
            pts = [
                (sx, sy - sr), (sx + sr * 0.3, sy - sr * 0.3),
                (sx + sr, sy), (sx + sr * 0.3, sy + sr * 0.3),
                (sx, sy + sr), (sx - sr * 0.3, sy + sr * 0.3),
                (sx - sr, sy), (sx - sr * 0.3, sy - sr * 0.3),
            ]
            sd.polygon(pts, fill=(255, 248, 195, 235), outline=(ar, ag, ab, 210))

    canvas.alpha_composite(resized, (x, y))
    return canvas


# =========================================================================== #
#  BUILD ALL 13 CAPYBARA SETS (78 TRANSPARENT 300x300 PNGs)
# =========================================================================== #
def build_all_capybara_assets() -> dict[str, list[tuple[str, Image.Image]]]:
    r01 = np.array(Image.open(REF_DIR / "01_ref_a.jpg").convert("RGB"))     # Pip & Puddle 9-panel
    r02 = np.array(Image.open(REF_DIR / "02_boba.png").convert("RGB"))      # Boba on lily pad
    r03 = np.array(Image.open(REF_DIR / "03_bundle.png").convert("RGB"))    # Pink clipart 9 poses
    r04 = np.array(Image.open(REF_DIR / "04_set.png").convert("RGB"))       # SVG bundle 21 stickers
    r05 = np.array(Image.open(REF_DIR / "05_ref_b.jpg").convert("RGB"))     # 12 stickers on cream
    r06 = np.array(Image.open(REF_DIR / "06_img.jpg").convert("RGB"))       # Lofi picnic blue headphones
    r07 = np.array(Image.open(REF_DIR / "07_apple.jpg").convert("RGB"))     # Apple hugger
    r08 = np.array(Image.open(REF_DIR / "08_istock.jpg").convert("RGB"))    # Capy & Chaptered
    r09 = np.array(Image.open(REF_DIR / "09_photo.jpg").convert("RGB"))     # Chibi yuzu sticker

    # Reusable clean extractions from the 9 sheets
    def ex01(box, erase=None):
        return extract_flat_bg(r01, box, bg_rgb=(255, 253, 248), dist_thr=28, erase_boxes=erase, keep_min_area_frac=0.001, min_keep_px=12)
    def ex03(box):
        return extract_flat_bg(r03, box, bg_rgb=(238, 207, 231), dist_thr=34, keep_min_area_frac=0.005, min_keep_px=40)
    def ex04(box, erase=None):
        return extract_flat_bg(r04, box, bg_rgb=(255, 255, 255), dist_thr=24, erase_boxes=erase, keep_min_area_frac=0.002, min_keep_px=12)
    def ex05(box, erase=None):
        return extract_flat_bg(r05, box, bg_rgb=(253, 246, 236), dist_thr=32, also_white=True, erase_boxes=erase, keep_min_area_frac=0.002, min_keep_px=15)

    out: dict[str, list[tuple[str, Image.Image]]] = {}

    # 48. Avocado Zen (Custom Ultra-Cute Vector!)
    out["capybara_avocado"] = build_avocado_capybara_set()

    # 49. Yuzu Onsen Spa
    out["capybara_onsen"] = [
        ("Onsen Tub",     compose_capy_300(draw_capy_stage0("onsen"), 0)),
        ("Spa Stretch",   compose_capy_300(ex03((695, 115, 1245, 555)), 1)),
        ("Chibi Yuzu",    compose_capy_300(extract_flat_bg(r09, bg_rgb=(255, 255, 255), dist_thr=24, strip_gray_border=True), 2)),
        ("Yuzu Chill",    compose_capy_300(ex05((48, 215, 256, 478)), 3)),
        ("Cozy Tea",      compose_capy_300(ex05((762, 538, 1006, 756)), 4)),
        ("Yuzu Onsen!",   compose_capy_300(ex05((38, 780, 290, 1054)), 5, sparkle_rgb=(249, 115, 22))),
    ]

    # 50. Pip & Puddle Besties
    out["capybara_pip_puddle"] = [
        ("Nap Buddies",   compose_capy_300(ex01((56, 892, 404, 1086)), 0)),
        ("Curious Duo",   compose_capy_300(ex01((56, 232, 404, 456)), 1)),
        ("Hello There!",  compose_capy_300(ex01((460, 232, 788, 456), erase=[(562, 242, 650, 296)]), 2)),
        ("Snack Attack",  compose_capy_300(ex01((460, 892, 788, 1078)), 3)),
        ("Besties Scarf", compose_capy_300(ex01((460, 582, 788, 790)), 4)),
        ("Sending Love!", compose_capy_300(ex01((840, 234, 1184, 464)), 5, sparkle_rgb=(244, 114, 182))),
    ]

    # 51. Boba Lily Pond
    out["capybara_boba_pond"] = [
        ("Lily Boba",     compose_capy_300(draw_capy_stage0("boba_pond"), 0)),
        ("Iced Latte",    compose_capy_300(ex04((10, 10, 118, 118)), 1)),
        ("Reed Pond",     compose_capy_300(ex03((675, 925, 1375, 1445)), 2)),
        ("Lotus Leaf",    compose_capy_300(ex05((790, 232, 1004, 492)), 3)),
        ("Brown Boba",    compose_capy_300(ex05((564, 232, 742, 468)), 4)),
        ("Lily Boba!",    compose_capy_300(extract_flat_bg(r02, bg_rgb=(215, 239, 253), dist_thr=26), 5, sparkle_rgb=(244, 114, 182))),
    ]

    # 52. Bookworm Study
    capy_chaptered = extract_flat_bg(
        r08, bg_rgb=(255, 241, 212), dist_thr=28,
        erase_boxes=[(120, 25, 296, 132), (296, 25, 480, 92), (386, 78, 480, 132)],
        keep_min_area_frac=0.0008, min_keep_px=10,
    )
    out["capybara_bookworm"] = [
        ("Book Stack",    compose_capy_300(draw_capy_stage0("bookworm"), 0)),
        ("Writing",       compose_capy_300(ex04((210, 112, 330, 206)), 1)),
        ("Laptop Study",  compose_capy_300(ex04((128, 12, 228, 104)), 2)),
        ("ABC Board",     compose_capy_300(ex04((434, 126, 566, 228)), 3)),
        ("On Books",      compose_capy_300(ex04((132, 112, 202, 212)), 4)),
        ("Chaptered!",    compose_capy_300(capy_chaptered, 5, sparkle_rgb=(234, 179, 8))),
    ]

    # 53. Lofi Picnic Beats
    out["capybara_lofi_picnic"] = [
        ("Picnic Basket", compose_capy_300(draw_capy_stage0("lofi_picnic"), 0)),
        ("Strolling",     compose_capy_300(ex03((1445, 865, 1935, 1345)), 1)),
        ("Heart Guitar",  compose_capy_300(ex04((126, 456, 224, 558)), 2)),
        ("Vibing Duo",    compose_capy_300(ex01((840, 582, 1184, 790)), 3)),
        ("Club Sandwich", compose_capy_300(ex04((338, 460, 446, 568)), 4)),
        ("Lofi Picnic!",  compose_capy_300(extract_flat_bg(r06, bg_rgb=(199, 230, 250), dist_thr=32, keep_min_area_frac=0.0008, min_keep_px=10, punch_interior_bg_thr=16.0), 5, sparkle_rgb=(37, 99, 235))),
    ]

    # 54. Foodie Snack Club
    out["capybara_foodie"] = [
        ("Milk Carton",   compose_capy_300(draw_capy_stage0("foodie"), 0)),
        ("Sipping Milk",  compose_capy_300(ex04((18, 356, 108, 422)), 1)),
        ("Watermelon",    compose_capy_300(ex05((40, 512, 240, 736)), 2)),
        ("Popcorn",       compose_capy_300(ex04((410, 236, 560, 342)), 3)),
        ("Pizza Slice",   compose_capy_300(ex04((438, 348, 538, 434)), 4)),
        ("Burger King!",  compose_capy_300(ex04((336, 360, 432, 462)), 5, sparkle_rgb=(245, 158, 11))),
    ]

    # 55. Dino Hoodie Play
    out["capybara_dino_hoodie"] = [
        ("Tiny Duck",     compose_capy_300(draw_capy_stage0("dino_hoodie"), 0)),
        ("Sleepy Duck",   compose_capy_300(ex05((506, 812, 768, 1012)), 1)),
        ("Awake Duck",    compose_capy_300(ex05((278, 266, 558, 448)), 2)),
        ("Flower Crown",  compose_capy_300(ex05((294, 486, 496, 760)), 3)),
        ("Wild Bouquet",  compose_capy_300(ex05((788, 802, 978, 1046)), 4)),
        ("Dino Hoodie!",  compose_capy_300(ex05((524, 514, 740, 750)), 5, sparkle_rgb=(74, 222, 128))),
    ]

    # 56. Apple Orchard Sweet
    out["capybara_apple_orchard"] = [
        ("Red Apple",     compose_capy_300(draw_capy_stage0("apple_orchard"), 0)),
        ("Sleepy Loaf",   compose_capy_300(ex03((95, 915, 585, 1345)), 1)),
        ("Looking Up",    compose_capy_300(ex03((1415, 1425, 1895, 1935)), 2)),
        ("Orchard Trot",  compose_capy_300(ex03((1445, 865, 1935, 1345)), 3)),
        ("Heart Hug",     compose_capy_300(ex04((232, 10, 324, 112)), 4)),
        ("Apple Hug!",    compose_capy_300(extract_flat_bg(r07, bg_rgb=(253, 218, 188), dist_thr=30), 5, sparkle_rgb=(225, 29, 72))),
    ]

    # 57. Pink Cloud Chill
    out["capybara_pink_chill"] = [
        ("Pink Pillow",   compose_capy_300(draw_capy_stage0("pink_chill"), 0)),
        ("Pink Popsicle", compose_capy_300(ex04((4, 434, 128, 564)), 1)),
        ("Belly Roll",    compose_capy_300(ex03((755, 1555, 1325, 1925)), 2)),
        ("Front Smile",   compose_capy_300(ex03((115, 115, 525, 565)), 3)),
        ("Happy Trot",    compose_capy_300(ex03((1445, 865, 1935, 1345)), 4)),
        ("Pond Chill!",   compose_capy_300(ex03((675, 925, 1375, 1445)), 5, sparkle_rgb=(232, 121, 249))),
    ]

    # 58. Fairy Party Wish
    out["capybara_fairy_party"] = [
        ("Gift Box",      compose_capy_300(draw_capy_stage0("fairy_party"), 0)),
        ("Wishing Star",  compose_capy_300(ex04((12, 118, 110, 226)), 1)),
        ("Pastel Heart",  compose_capy_300(ex04((232, 10, 324, 112)), 2)),
        ("Star Shades",   compose_capy_300(ex04((128, 358, 226, 458)), 3)),
        ("Crown Gift",    compose_capy_300(ex04((458, 438, 568, 564)), 4)),
        ("Fairy Wish!",   compose_capy_300(ex04((438, 4, 562, 122)), 5, sparkle_rgb=(244, 114, 182))),
    ]

    # 59. SelfCare GlowUp
    out["capybara_selfcare"] = [
        ("Vanity Mirror", compose_capy_300(draw_capy_stage0("selfcare"), 0)),
        ("Cozy Bed",      compose_capy_300(ex04((232, 358, 334, 462)), 1)),
        ("Fresh Morning", compose_capy_300(ex04((342, 12, 424, 112)), 2)),
        ("Glow Mirror",   compose_capy_300(ex04((230, 446, 342, 562)), 3)),
        ("Heart Shades",  compose_capy_300(ex05((324, 812, 494, 1040)), 4)),
        ("Glow Bouquet!", compose_capy_300(ex05((788, 802, 978, 1046)), 5, sparkle_rgb=(251, 113, 133))),
    ]

    # 60. Snapshot Traveler
    out["capybara_traveler"] = [
        ("Instant Cam",   compose_capy_300(draw_capy_stage0("traveler"), 0)),
        ("World Globe",   compose_capy_300(ex04((330, 114, 430, 202)), 1)),
        ("Tea Time",      compose_capy_300(ex01((56, 582, 404, 798)), 2)),
        ("Lotus Explore", compose_capy_300(ex05((790, 232, 1004, 492)), 3)),
        ("Travel Scarf",  compose_capy_300(ex01((460, 582, 788, 790)), 4)),
        ("Snap Moments!", compose_capy_300(ex01((840, 892, 1184, 1086)), 5, sparkle_rgb=(13, 148, 136))),
    ]

    total = 0
    for slug, stages in out.items():
        d = ASSETS_DIR / slug
        d.mkdir(parents=True, exist_ok=True)
        for i, (_, im) in enumerate(stages):
            im.save(d / f"stage_{i}.png", "PNG", optimize=True)
            total += 1
        print(f"  [ASSETS] {slug:24s} -> {len(stages)} PNGs saved")
    print(f"Total Capybara sprites saved: {total}")
    return out


def render_capybara_contact_sheet(results: dict[str, list[tuple[str, Image.Image]]]) -> Path:
    """Render `previews/assets_contact_sheet_capybara.png` showing ALL 13 sets (#48-#60, 78 PNGs)
    at BOTH 180px large AND 44px actual Excel cell size!"""
    rows = [
        ("48. Avocado Zen [Custom]",  "capybara_avocado",       (246, 250, 238), (101, 163, 13)),
        ("49. Yuzu Onsen Spa",        "capybara_onsen",         (255, 251, 242), (249, 115, 22)),
        ("50. Pip & Puddle Besties",  "capybara_pip_puddle",    (255, 245, 248), (244, 114, 182)),
        ("51. Boba Lily Pond",        "capybara_boba_pond",     (239, 248, 255), (14, 165, 233)),
        ("52. Bookworm Study",        "capybara_bookworm",      (255, 253, 245), (202, 138, 4)),
        ("53. Lofi Picnic Beats",     "capybara_lofi_picnic",   (240, 247, 255), (37, 99, 235)),
        ("54. Foodie Snack Club",     "capybara_foodie",        (255, 251, 235), (239, 68, 68)),
        ("55. Dino Hoodie Play",      "capybara_dino_hoodie",   (244, 251, 246), (22, 163, 74)),
        ("56. Apple Orchard Sweet",   "capybara_apple_orchard", (255, 246, 237), (225, 29, 72)),
        ("57. Pink Cloud Chill",      "capybara_pink_chill",    (253, 242, 248), (219, 39, 119)),
        ("58. Fairy Party Wish",      "capybara_fairy_party",   (248, 245, 255), (147, 51, 234)),
        ("59. SelfCare GlowUp",       "capybara_selfcare",      (255, 249, 250), (244, 63, 94)),
        ("60. Snapshot Traveler",     "capybara_traveler",      (250, 247, 242), (13, 148, 136)),
    ]
    cell_w, cell_h = 204, 272
    left_w = 244
    pad = 18
    hdr_h = 84
    W = pad * 2 + left_w + cell_w * 6
    H = pad * 2 + hdr_h + cell_h * len(rows)

    sheet = Image.new("RGB", (W, H), (252, 250, 247))
    draw = ImageDraw.Draw(sheet)
    try:
        f_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 28)
        f_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 16)
        f_row = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 15)
        f_lbl = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 13)
        f_tiny = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 11)
    except Exception:
        f_title = f_sub = f_row = f_lbl = f_tiny = ImageFont.load_default()

    draw.rectangle([0, 0, W, hdr_h], fill=(74, 50, 40))
    draw.text((pad, 14), "CAPYBARA CHILL COLLECTION — #48–#60 (13 THEMES • 78 SPRITES, v3.9)", fill=(255, 255, 255), font=f_title)
    draw.text((pad, 50), "Custom Vector Avocado Capybara (#48) + 12 Bespoke Sticker Themes (#49–#60) • Large 168px + Actual 44px Excel Preview", fill=(254, 240, 138), font=f_sub)

    pcts = ["0%", "1–24%", "25–49%", "50–74%", "75–99%", "100% MAX"]
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
            draw.multiline_text((x0 + 12, y0 + 202), lbl, fill=(58, 42, 34), font=f_lbl, spacing=1)
            draw.text((sx + 6, sy + 49), "44px", fill=(150, 142, 136), font=f_tiny)

    out_path = PREVIEWS_DIR / "assets_contact_sheet_capybara.png"
    sheet.save(out_path, "PNG", optimize=True)
    print(f"  [PREVIEW] Saved {out_path} ({sheet.size[0]}x{sheet.size[1]})")
    return out_path


if __name__ == "__main__":
    res = build_all_capybara_assets()
    render_capybara_contact_sheet(res)
