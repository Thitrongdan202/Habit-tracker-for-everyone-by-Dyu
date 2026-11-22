"""
generate_assets_pets_overhaul.py — Kawaii Vector SVG -> High-DPI 300x300px PNG Overhaul
for the 6 affected pet sprite sets (36 sprites total):
  1. `shiba_inu`      (Template 30) — True Shiba Inu dog (wide dog ears, urajiro cheeks, maro eyebrows,
                                       protruding snout, curled donut tail, karakusa bandana, bone treat; NO crown!)
  2. `akita_inu`      (Template 31) — Distinct Snow Akita Inu (plush bear-like head, thick white neck ruff,
                                       rounded bear ears, big black dog nose, shimenawa collar + snowflakes; NO crown!)
  3. `ginger_kitten`  (Template 25) — Chubby Peach-Ginger Tabby Kitten (wicker basket, forehead M stripes,
                                       cozy loaf, batting mint yarn on all fours, mint bow tie + fish plushie; NO crown!)
  4. `royal_cat_cash` (Template 24) — Exclusive Golden Crown owner! Minimalist comic white cat (tilted box ->
                                       peeking box -> coin -> piggy bank -> velvet pillow -> Golden Crown + coins)
  5. `purple_cat`     (Template 26) — Dreamy Lavender British Shorthair / Starry Moon Cat (moon pillow ->
                                       napping -> lilac yarn -> pink ribbon + star charm -> crescent moon ->
                                       starlight lavender beret + constellation stars; NO box, NO crown!)
  6. `mochi_cat`      (Template 33) — Ultra-Squishy Japanese Mochi Blob Cat (orange parcel box -> ears peeking ->
                                       paws on rim ^w^ -> dumpling loaf -> mikan tangerine on head ->
                                       blissful mochi cat with mikan, taiyaki fish snack & peach hearts; NO crown!)

Renders via PyMuPDF native SVG rasterizer at 3x supersampling (900x900 RGBA -> 300x300 Lanczos PNG).
Also renders `previews/assets_contact_sheet_pets_overhaul.png` showing BOTH large (180px) AND 44px Excel size!
"""
from __future__ import annotations

import math
from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
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
#  SHARED VECTOR PRIMITIVES (Sparkles, Hearts, Sakura Petals, Snowflakes, Shadow)
# =========================================================================== #
def shadow(cx=150, cy=262, rx=74, ry=13, opacity=0.11) -> str:
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#4A3228" fill-opacity="{opacity}"/>'


def sparkle4(cx, cy, r=14, fill="#FCD34D", stroke="#B47812", sw=2.6) -> str:
    ir = r * 0.30
    d = (
        f"M {cx},{cy - r} Q {cx + ir},{cy - ir} {cx + r},{cy} "
        f"Q {cx + ir},{cy + ir} {cx},{cy + r} "
        f"Q {cx - ir},{cy + ir} {cx - r},{cy} "
        f"Q {cx - ir},{cy - ir} {cx},{cy - r} Z"
    )
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>'


def heart(cx, cy, s=14, fill="#F48A9E", stroke="#6B3442", sw=2.6, rot=0) -> str:
    d = (
        f"M 0,{s * 0.85} "
        f"C {-s * 1.15},{s * 0.15} {-s * 1.15},{-s * 0.75} {-s * 0.48},{-s * 0.75} "
        f"C {-s * 0.12},{-s * 0.75} 0,{-s * 0.38} 0,{-s * 0.28} "
        f"C 0,{-s * 0.38} {s * 0.12},{-s * 0.75} {s * 0.48},{-s * 0.75} "
        f"C {s * 1.15},{-s * 0.75} {s * 1.15},{s * 0.15} 0,{s * 0.85} Z"
    )
    tr = f' transform="translate({cx},{cy}) rotate({rot})"'
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"{tr}/>'


def sakura_petal(cx, cy, s=11, rot=20, fill="#FBB6CE", stroke="#B85B7B") -> str:
    d = (
        f"M 0,{s} C {-s * 0.85},{s * 0.3} {-s * 0.75},{-s * 0.65} {-s * 0.2},{-s * 0.9} "
        f"L 0,{-s * 0.55} L {s * 0.2},{-s * 0.9} "
        f"C {s * 0.75},{-s * 0.65} {s * 0.85},{s * 0.3} 0,{s} Z"
    )
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="2.2" stroke-linejoin="round" transform="translate({cx},{cy}) rotate({rot})"/>'


def snowflake(cx, cy, r=12, col="#7DD3FC", stroke="#3B82C4") -> str:
    parts = [f'<circle cx="{cx}" cy="{cy}" r="{r * 0.26}" fill="#FFFFFF" stroke="{stroke}" stroke-width="2.2"/>']
    for k in range(6):
        ang = math.radians(k * 60)
        x2 = cx + math.cos(ang) * r
        y2 = cy + math.sin(ang) * r
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="3.2" stroke-linecap="round"/>')
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="1.6" stroke-linecap="round"/>')
    return "".join(parts)


def paw_print(cx, cy, s=1.0, fill="#E09B46") -> str:
    return (
        f'<g transform="translate({cx},{cy}) scale({s})">'
        f'<ellipse cx="0" cy="6" rx="11" ry="8.5" fill="{fill}"/>'
        f'<circle cx="-11" cy="-6" r="4.6" fill="{fill}"/>'
        f'<circle cx="-4" cy="-12" r="4.8" fill="{fill}"/>'
        f'<circle cx="4" cy="-12" r="4.8" fill="{fill}"/>'
        f'<circle cx="11" cy="-6" r="4.6" fill="{fill}"/>'
        f'</g>'
    )


# =========================================================================== #
#  1. SHIBA INU (`assets/shiba_inu/`) — TRUE SHIBA INU DOG (NO CAT FACE, NO CROWN!)
# =========================================================================== #
def _shiba_head(cx, cy, sc=1.0, tilt=0.0, sleepy=False, tongue=False, happy_sq=False, ear_perk=False) -> str:
    """True Shiba Inu head: wider-set tilted dog ears, marshmallow urajiro cheeks,
    two cream maro eyebrow dots, protruding cream snout with real dog nose!"""
    OL = "#4A3228"
    FUR = "#E69545"
    SHD = "#CC7A2D"
    CRM = "#FFF5E4"
    EAR_IN = "#F7C5A8"
    BLUSH = "#F5989D"

    ear_l_rot = -8 if ear_perk else 0
    ear_r_rot = 14 if ear_perk else 0

    # Left & Right Shiba Dog Ears — wide-set, thick rounded triangles tilted outward (NOT vertical cat ears!)
    ear_l = (
        f'<g transform="rotate({ear_l_rot}, -42, -38)">'
        f'<path d="M -54,-22 C -68,-44 -68,-72 -50,-78 C -34,-82 -18,-62 -14,-44 Z" '
        f'fill="{FUR}" stroke="{OL}" stroke-width="6.8" stroke-linejoin="round"/>'
        f'<path d="M -50,-32 C -58,-46 -58,-64 -47,-68 C -38,-70 -27,-56 -24,-43 Z" fill="{EAR_IN}"/>'
        f'</g>'
    )
    ear_r = (
        f'<g transform="rotate({ear_r_rot}, 42, -38)">'
        f'<path d="M 54,-22 C 68,-44 68,-72 50,-78 C 34,-82 18,-62 14,-44 Z" '
        f'fill="{FUR}" stroke="{OL}" stroke-width="6.8" stroke-linejoin="round"/>'
        f'<path d="M 50,-32 C 58,-46 58,-64 47,-68 C 38,-70 27,-56 24,-43 Z" fill="{EAR_IN}"/>'
        f'</g>'
    )

    # Plump toasted-marshmallow Shiba head silhouette (wider fluffy cheeks!)
    head_base = (
        f'<path d="M 0,-54 C 34,-54 58,-36 62,-8 C 66,18 54,40 30,45 '
        f'C 16,48 -16,48 -30,45 C -54,40 -66,18 -62,-8 C -58,-36 -34,-54 0,-54 Z" '
        f'fill="{FUR}" stroke="{OL}" stroke-width="7.2" stroke-linejoin="round"/>'
    )
    # Soft top highlight
    head_hi = '<ellipse cx="-14" cy="-37" rx="22" ry="8" fill="#FFF2DC" fill-opacity="0.32"/>'

    # Iconic Shiba `urajiro` cream cheek & jaw mask (curves up cleanly under eyes & around snout!)
    urajiro = (
        f'<path d="M -59,3 C -45,-3 -26,-5 -14,2 C -6,-8 6,-8 14,2 C 26,-5 45,-3 59,3 '
        f'C 59,24 46,41 26,44 C 12,46 -12,46 -26,44 C -46,41 -59,24 -59,3 Z" '
        f'fill="{CRM}"/>'
    )
    # Re-stroke outer lower cheek rim so outline stays razor-crisp over urajiro
    head_outline = (
        f'<path d="M 0,-54 C 34,-54 58,-36 62,-8 C 66,18 54,40 30,45 '
        f'C 16,48 -16,48 -30,45 C -54,40 -66,18 -62,-8 C -58,-36 -34,-54 0,-54 Z" '
        f'fill="none" stroke="{OL}" stroke-width="7.2" stroke-linejoin="round"/>'
    )

    # Iconic tiny cream Shiba eyebrow dots (`maro`)!
    maro = (
        f'<ellipse cx="-21" cy="-22" rx="6.2" ry="4.4" fill="{CRM}" transform="rotate(-14,-21,-22)"/>'
        f'<ellipse cx="21" cy="-22" rx="6.2" ry="4.4" fill="{CRM}" transform="rotate(14,21,-22)"/>'
    )

    # Eyes
    if sleepy:
        eyes = (
            f'<path d="M -32,-4 Q -24,4 -16,-4" fill="none" stroke="{OL}" stroke-width="4.8" stroke-linecap="round"/>'
            f'<path d="M 16,-4 Q 24,4 32,-4" fill="none" stroke="{OL}" stroke-width="4.8" stroke-linecap="round"/>'
        )
    elif happy_sq:
        eyes = (
            f'<path d="M -32,-1 Q -24,-12 -16,-1" fill="none" stroke="{OL}" stroke-width="5.2" stroke-linecap="round"/>'
            f'<path d="M 16,-1 Q 24,-12 32,-1" fill="none" stroke="{OL}" stroke-width="5.2" stroke-linecap="round"/>'
        )
    else:
        eyes = (
            f'<circle cx="-24" cy="-6" r="6.4" fill="{OL}"/>'
            f'<circle cx="-26.2" cy="-8.2" r="2.3" fill="#FFFFFF"/>'
            f'<circle cx="24" cy="-6" r="6.4" fill="{OL}"/>'
            f'<circle cx="21.8" cy="-8.2" r="2.3" fill="#FFFFFF"/>'
        )

    # Blush cheeks
    blush = (
        f'<ellipse cx="-39" cy="9" rx="9" ry="5.2" fill="{BLUSH}" fill-opacity="0.55"/>'
        f'<ellipse cx="39" cy="9" rx="9" ry="5.2" fill="{BLUSH}" fill-opacity="0.55"/>'
    )

    # Protruding cream dog snout cushion + real rounded-triangle DOG NOSE + doggy smile/tongue!
    snout_pad = '<ellipse cx="0" cy="14" rx="22" ry="15" fill="#FFFDF8" stroke="#E8D3B5" stroke-width="2.2"/>'
    dog_nose = (
        f'<path d="M -9,4 C -9,0 9,0 9,4 C 9,9 4,14 0,14 C -4,14 -9,9 -9,4 Z" fill="{OL}"/>'
        f'<ellipse cx="-2.5" cy="4.2" rx="2.8" ry="1.4" fill="#FFFFFF" fill-opacity="0.55"/>'
    )
    if tongue:
        mouth = (
            f'<path d="M -11,17 Q -5,24 0,18 Q 5,24 11,17" fill="none" stroke="{OL}" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="M -5.5,20 C -6,32 6,32 5.5,20 Z" fill="#F47E8E" stroke="{OL}" stroke-width="3.2" stroke-linejoin="round"/>'
            f'<line x1="0" y1="21" x2="0" y2="27" stroke="#D1566A" stroke-width="2" stroke-linecap="round"/>'
        )
    else:
        mouth = (
            f'<line x1="0" y1="13" x2="0" y2="19" stroke="{OL}" stroke-width="3.8" stroke-linecap="round"/>'
            f'<path d="M -12,18 Q -6,26 0,19 Q 6,26 12,18" fill="none" stroke="{OL}" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round"/>'
        )

    return (
        f'<g transform="translate({cx},{cy}) rotate({tilt}) scale({sc})">'
        f'{ear_l}{ear_r}{head_base}{head_hi}{urajiro}{head_outline}{maro}{blush}{snout_pad}{eyes}{dog_nose}{mouth}'
        f'</g>'
    )


def _shiba_bandana(cx, cy, sc=1.0) -> str:
    """Red Japanese karakusa (swirl-pattern) triangle bandana."""
    OL = "#4A3228"
    return (
        f'<g transform="translate({cx},{cy}) scale({sc})">'
        f'<path d="M -38,-4 C -16,4 16,4 38,-4 L 4,32 C 1,35 -1,35 -4,32 Z" '
        f'fill="#D9443C" stroke="{OL}" stroke-width="5.6" stroke-linejoin="round"/>'
        f'<path d="M -18,4 C -12,12 -4,8 -8,2" fill="none" stroke="#FFE9C7" stroke-width="3" stroke-linecap="round"/>'
        f'<path d="M 16,4 C 10,12 2,8 6,2" fill="none" stroke="#FFE9C7" stroke-width="3" stroke-linecap="round"/>'
        f'<circle cx="0" cy="18" r="3.6" fill="none" stroke="#FFE9C7" stroke-width="2.6"/>'
        f'</g>'
    )


def _shiba_donut_tail(cx, cy, sc=1.0, rot=0) -> str:
    """Fluffy curled Shiba donut tail."""
    OL = "#4A3228"
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot}) scale({sc})">'
        f'<path d="M -10,18 C 18,22 36,4 32,-16 C 28,-34 4,-38 -8,-24 '
        f'C -16,-14 -8,0 4,-4 C 12,-6 12,-16 4,-16" '
        f'fill="#E69545" stroke="{OL}" stroke-width="6.6" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<circle cx="4" cy="-14" r="7" fill="#FFF5E4"/>'
        f'</g>'
    )


def _dog_bone(cx, cy, sc=1.0, rot=0) -> str:
    OL = "#4A3228"
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot}) scale({sc})">'
        f'<path d="M -18,-6 C -26,-12 -32,-2 -24,0 C -32,4 -24,14 -16,6 L 16,6 '
        f'C 24,14 32,4 24,0 C 32,-2 26,-12 18,-6 Z" '
        f'fill="#FFF7E6" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
        f'<line x1="-10" y1="-1" x2="10" y2="-1" stroke="#EED9B7" stroke-width="3" stroke-linecap="round"/>'
        f'</g>'
    )


def _sitting_paws(cx, y_bot, fill, ol, spread=17, paw_rx=12.5, paw_ry=9.0, leg_h=24) -> str:
    """Organic kawaii chibi seated front paws — open plump chest above, cute curved toes below (NO stiff piano-bar lines!)."""
    lx, rx_p = cx - spread, cx + spread
    y_top = y_bot - leg_h
    return (
        f'<path d="M {lx - 10},{y_top} C {lx - 12},{y_bot - 6} {lx - 13},{y_bot} {lx},{y_bot} '
        f'C {lx + 11},{y_bot} {lx + 11},{y_bot - 6} {lx + 9},{y_top + 4}" '
        f'fill="{fill}" stroke="{ol}" stroke-width="5.6" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<path d="M {rx_p + 10},{y_top} C {rx_p + 12},{y_bot - 6} {rx_p + 13},{y_bot} {rx_p},{y_bot} '
        f'C {rx_p - 11},{y_bot} {rx_p - 11},{y_bot - 6} {rx_p - 9},{y_top + 4}" '
        f'fill="{fill}" stroke="{ol}" stroke-width="5.6" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<line x1="{lx - 2}" y1="{y_bot - 7}" x2="{lx - 2}" y2="{y_bot - 1}" stroke="{ol}" stroke-width="3" stroke-linecap="round"/>'
        f'<line x1="{rx_p + 2}" y1="{y_bot - 7}" x2="{rx_p + 2}" y2="{y_bot - 1}" stroke="{ol}" stroke-width="3" stroke-linecap="round"/>'
    )


def draw_shiba_inu(stage: int) -> str:
    OL = "#4A3228"
    FUR = "#E69545"
    SHD = "#CC7A2D"
    CRM = "#FFF5E4"

    cushion = (
        shadow(150, 248, 92, 16, 0.13)
        + f'<ellipse cx="150" cy="230" rx="88" ry="30" fill="#D9443C" stroke="{OL}" stroke-width="7"/>'
        + f'<ellipse cx="150" cy="224" rx="68" ry="20" fill="#FFF3DC" stroke="#B6312A" stroke-width="3.2"/>'
        + paw_print(150, 224, 0.95, "#E5A04B")
    )

    if stage == 0:
        return cushion + _dog_bone(216, 250, 0.72, -12)

    if stage == 1:
        # Sleepy Shiba puppy curled into a round "cinnamon roll" on the red cushion
        roll = (
            f'<path d="M 92,216 C 84,182 114,158 158,162 C 198,166 220,192 210,218 '
            f'C 202,236 168,242 132,238 C 106,236 96,228 92,216 Z" '
            f'fill="{FUR}" stroke="{OL}" stroke-width="7" stroke-linejoin="round"/>'
            f'<path d="M 176,174 C 198,176 208,196 196,214 C 186,226 168,224 166,212 '
            f'C 164,200 176,194 184,200" fill="{CRM}" stroke="{OL}" stroke-width="5.6" stroke-linecap="round"/>'
        )
        zzz = (
            '<text x="206" y="138" font-family="Segoe UI, Arial" font-weight="bold" font-size="24" fill="#D97736">z</text>'
            '<text x="224" y="118" font-family="Segoe UI, Arial" font-weight="bold" font-size="18" fill="#E69545">z</text>'
        )
        return cushion + roll + _shiba_head(134, 184, sc=0.72, tilt=-8, sleepy=True) + zzz

    if stage == 2:
        # Curious baby Shiba sitting neatly on haunches, head slightly tilted, one ear perked!
        body = (
            shadow(150, 260, 62, 12)
            + _shiba_donut_tail(204, 214, sc=0.80, rot=-10)
            + f'<path d="M 106,184 C 94,214 96,250 120,258 C 136,263 164,263 180,258 '
              f'C 204,250 206,214 194,184 C 182,164 118,164 106,184 Z" '
              f'fill="{FUR}" stroke="{OL}" stroke-width="7" stroke-linejoin="round"/>'
            + f'<ellipse cx="150" cy="224" rx="31" ry="30" fill="{CRM}"/>'
            + _sitting_paws(150, 258, CRM, OL, spread=16, leg_h=22)
        )
        return body + _shiba_head(150, 140, sc=0.88, tilt=7, ear_perk=True)

    if stage == 3:
        # Happy Shiba sitting proudly wearing red Japanese karakusa bandana
        body = (
            shadow(150, 262, 68, 13)
            + _shiba_donut_tail(210, 212, sc=0.92, rot=-6)
            + f'<path d="M 100,176 C 88,210 90,252 116,260 C 134,265 166,265 184,260 '
              f'C 210,252 212,210 200,176 C 186,156 114,156 100,176 Z" '
              f'fill="{FUR}" stroke="{OL}" stroke-width="7.2" stroke-linejoin="round"/>'
            + f'<ellipse cx="150" cy="224" rx="34" ry="32" fill="{CRM}"/>'
            + _sitting_paws(150, 260, CRM, OL, spread=18, leg_h=24)
        )
        return body + _shiba_bandana(150, 180, sc=1.02) + _shiba_head(150, 128, sc=0.95)

    if stage == 4:
        # Playful Shiba in joyful natural doggy PLAY BOW pose (chest low, rump & curly tail high!), tongue blep + heart!
        play_bow = (
            shadow(156, 262, 86, 13)
            + _shiba_donut_tail(228, 152, sc=0.95, rot=-24)
            + f'<path d="M 200,206 L 204,250 C 204,258 222,258 222,250 L 222,202" '
              f'fill="{CRM}" stroke="{OL}" stroke-width="6.4" stroke-linecap="round" stroke-linejoin="round"/>'
            + f'<path d="M 102,196 C 118,174 166,154 202,158 C 228,162 238,188 226,214 '
              f'C 214,234 180,234 148,236 C 116,238 96,220 102,196 Z" '
              f'fill="{FUR}" stroke="{OL}" stroke-width="7.2" stroke-linejoin="round"/>'
            + f'<path d="M 122,226 C 148,236 184,232 204,218 C 190,208 156,210 124,216 Z" fill="{CRM}"/>'
            + f'<path d="M 184,196 C 174,216 178,238 182,252 C 182,260 202,260 202,252 L 204,218" '
              f'fill="{FUR}" stroke="{OL}" stroke-width="6.4" stroke-linecap="round" stroke-linejoin="round"/>'
            + f'<ellipse cx="192" cy="254" rx="11" ry="7" fill="{CRM}" stroke="{OL}" stroke-width="5.2"/>'
            + f'<path d="M 124,224 L 84,244 C 74,248 76,260 88,258 L 136,244" '
              f'fill="{CRM}" stroke="{OL}" stroke-width="6.2" stroke-linecap="round" stroke-linejoin="round"/>'
            + f'<path d="M 136,230 L 106,252 C 98,258 106,266 118,262 L 152,246" '
              f'fill="{CRM}" stroke="{OL}" stroke-width="6.2" stroke-linecap="round" stroke-linejoin="round"/>'
        )
        return (
            play_bow
            + _shiba_bandana(116, 206, sc=0.82)
            + _shiba_head(112, 152, sc=0.90, tilt=-8, tongue=True)
            + heart(228, 86, 16, "#F47E8E", OL, 3.0, 12)
            + sparkle4(44, 96, 12)
        )

    # Stage 5: Radiant Proud Shiba Inu with red karakusa bandana, crunchy dog bone treat, sakura petals & golden stars — NO CROWN!
    body = (
        shadow(150, 264, 74, 14)
        + _shiba_donut_tail(216, 206, sc=1.04, rot=-8)
        + f'<path d="M 96,172 C 84,210 86,254 114,262 C 132,267 168,267 186,262 '
          f'C 214,254 216,210 204,172 C 188,152 112,152 96,172 Z" '
          f'fill="{FUR}" stroke="{OL}" stroke-width="7.4" stroke-linejoin="round"/>'
        + f'<ellipse cx="150" cy="224" rx="36" ry="34" fill="{CRM}"/>'
        + _sitting_paws(150, 262, CRM, OL, spread=22, leg_h=24)
    )
    deco = (
        sparkle4(56, 70, 16)
        + sparkle4(244, 70, 15)
        + sakura_petal(56, 148, 12, -25)
        + sakura_petal(246, 144, 12, 32)
        + sakura_petal(150, 36, 11, 8)
    )
    return (
        deco
        + body
        + _shiba_bandana(150, 178, sc=1.08)
        + _shiba_head(150, 122, sc=0.98, happy_sq=True, tongue=True)
        + _dog_bone(150, 248, sc=1.08, rot=-5)
    )


# =========================================================================== #
#  2. AKITA INU (`assets/akita_inu/`) — PLUSH BEAR-LIKE SNOW AKITA (NO CROWN!)
# =========================================================================== #
def _akita_head(cx, cy, sc=1.0, tilt=0.0, sleepy=False, calm_smile=False) -> str:
    """Distinct Akita Inu head: bigger rounder bear-like plush head, shorter thicker
    forward-leaning bear ears, paler apricot-snow coat, huge white cheek fluff & big black dog nose!"""
    OL = "#334155"
    APRI = "#ECC49C"
    SNOW = "#FFFFFF"
    EAR_IN = "#F6D8C8"
    NOSE = "#1E293B"
    BLUSH = "#F6A9B0"

    # Thick rounded bear-like Akita ears (shorter & rounder than Shiba!)
    ear_l = (
        f'<path d="M -56,-20 C -66,-44 -60,-68 -42,-70 C -26,-72 -14,-54 -14,-38 Z" '
        f'fill="{APRI}" stroke="{OL}" stroke-width="6.8" stroke-linejoin="round"/>'
        f'<path d="M -50,-28 C -56,-42 -52,-58 -41,-60 C -32,-62 -24,-48 -23,-38 Z" fill="{EAR_IN}"/>'
    )
    ear_r = (
        f'<path d="M 56,-20 C 66,-44 60,-68 42,-70 C 26,-72 14,-54 14,-38 Z" '
        f'fill="{APRI}" stroke="{OL}" stroke-width="6.8" stroke-linejoin="round"/>'
        f'<path d="M 50,-28 C 56,-42 52,-58 41,-60 C 32,-62 24,-48 23,-38 Z" fill="{EAR_IN}"/>'
    )

    # Extra-wide plush bear-like head silhouette with fluffy side cheek tufts!
    head_shape = (
        "M 0,-54 C 36,-54 62,-34 65,-6 C 72,6 70,28 52,40 "
        "C 34,50 -34,50 -52,40 C -70,28 -72,6 -65,-6 C -62,-34 -36,-54 0,-54 Z"
    )
    head_base = f'<path d="{head_shape}" fill="{APRI}" stroke="{OL}" stroke-width="7.2" stroke-linejoin="round"/>'
    # Wide snow-white fluffy Akita face mask (covers lower 65% of face + plush cheeks!)
    snow_mask = (
        f'<path d="M -64,-2 C -46,-10 -24,-10 -12,-2 C -4,-14 4,-14 12,-2 C 24,-10 46,-10 64,-2 '
        f'C 70,12 64,34 46,42 C 28,49 -28,49 -46,42 C -64,34 -70,12 -64,-2 Z" fill="{SNOW}"/>'
    )
    head_ol = f'<path d="{head_shape}" fill="none" stroke="{OL}" stroke-width="7.2" stroke-linejoin="round"/>'

    # Eyes (sweet calm loyal Akita eyes)
    if sleepy:
        eyes = (
            f'<path d="M -32,-6 Q -24,2 -16,-6" fill="none" stroke="{OL}" stroke-width="4.8" stroke-linecap="round"/>'
            f'<path d="M 16,-6 Q 24,2 32,-6" fill="none" stroke="{OL}" stroke-width="4.8" stroke-linecap="round"/>'
        )
    elif calm_smile:
        eyes = (
            f'<path d="M -33,-3 Q -24,-12 -15,-3" fill="none" stroke="{OL}" stroke-width="5.2" stroke-linecap="round"/>'
            f'<path d="M 15,-3 Q 24,-12 33,-3" fill="none" stroke="{OL}" stroke-width="5.2" stroke-linecap="round"/>'
        )
    else:
        eyes = (
            f'<circle cx="-25" cy="-7" r="5.8" fill="{NOSE}"/>'
            f'<circle cx="-27" cy="-9" r="2.1" fill="#FFFFFF"/>'
            f'<circle cx="25" cy="-7" r="5.8" fill="{NOSE}"/>'
            f'<circle cx="23" cy="-9" r="2.1" fill="#FFFFFF"/>'
        )

    blush = (
        f'<ellipse cx="-44" cy="11" rx="9.5" ry="5.5" fill="{BLUSH}" fill-opacity="0.48"/>'
        f'<ellipse cx="44" cy="11" rx="9.5" ry="5.5" fill="{BLUSH}" fill-opacity="0.48"/>'
    )

    # Big black bear-like Akita dog nose + gentle calm smile
    nose = (
        f'<path d="M -11,3 C -11,-2 11,-2 11,3 C 11,10 5,16 0,16 C -5,16 -11,10 -11,3 Z" fill="{NOSE}"/>'
        f'<ellipse cx="-3" cy="3.5" rx="3.2" ry="1.6" fill="#FFFFFF" fill-opacity="0.5"/>'
    )
    mouth = (
        f'<line x1="0" y1="15" x2="0" y2="22" stroke="{OL}" stroke-width="3.8" stroke-linecap="round"/>'
        f'<path d="M -13,20 Q -6,28 0,22 Q 6,28 13,20" fill="none" stroke="{OL}" stroke-width="4.2" stroke-linecap="round"/>'
    )

    return (
        f'<g transform="translate({cx},{cy}) rotate({tilt}) scale({sc})">'
        f'{ear_l}{ear_r}{head_base}{snow_mask}{head_ol}{blush}{eyes}{nose}{mouth}'
        f'</g>'
    )


def _akita_ruff(cx, cy, sc=1.0) -> str:
    """Thick fluffy snow-white Akita neck ruff (clearly distinguishes Akita from Shiba!)."""
    OL = "#334155"
    return (
        f'<g transform="translate({cx},{cy}) scale({sc})">'
        f'<path d="M -52,-6 C -60,8 -48,24 -32,20 C -22,30 -8,32 0,24 '
        f'C 8,32 22,30 32,20 C 48,24 60,8 52,-6 Z" '
        f'fill="#FFFFFF" stroke="{OL}" stroke-width="6.2" stroke-linejoin="round"/>'
        f'</g>'
    )


def _akita_shimenawa_collar(cx, cy, sc=1.0) -> str:
    """Japanese Indigo & Gold Braided Collar (`shimenawa`) with crimson accents & gleaming golden bell!"""
    OL = "#334155"
    return (
        f'<g transform="translate({cx},{cy}) scale({sc})">'
        f'<path d="M -42,-6 C -22,12 22,12 42,-6 C 46,4 38,14 24,18 C 8,22 -8,22 -24,18 C -38,14 -46,4 -42,-6 Z" '
        f'fill="#2E538A" stroke="{OL}" stroke-width="5.6" stroke-linejoin="round"/>'
        # Gold & crimson braided rope twists across collar
        f'<ellipse cx="-24" cy="8" rx="9" ry="5.5" fill="#F6C851" stroke="{OL}" stroke-width="3" transform="rotate(24,-24,8)"/>'
        f'<ellipse cx="-8" cy="12" rx="9" ry="5.5" fill="#D94B4B" stroke="{OL}" stroke-width="3" transform="rotate(10,-8,12)"/>'
        f'<ellipse cx="8" cy="12" rx="9" ry="5.5" fill="#F6C851" stroke="{OL}" stroke-width="3" transform="rotate(-10,8,12)"/>'
        f'<ellipse cx="24" cy="8" rx="9" ry="5.5" fill="#D94B4B" stroke="{OL}" stroke-width="3" transform="rotate(-24,24,8)"/>'
        # Gleaming golden bell hanging in center
        f'<circle cx="0" cy="24" r="11" fill="#FCD34D" stroke="{OL}" stroke-width="4.5"/>'
        f'<line x1="-7" y1="26" x2="7" y2="26" stroke="{OL}" stroke-width="3" stroke-linecap="round"/>'
        f'<circle cx="0" cy="26" r="2.6" fill="{OL}"/>'
        f'<circle cx="-3.5" cy="20" r="2.4" fill="#FFFFFF" fill-opacity="0.75"/>'
        f'</g>'
    )


def _akita_fluffy_tail(cx, cy, sc=1.0, rot=0) -> str:
    """Super fluffy snow-white curled Akita tail."""
    OL = "#334155"
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot}) scale({sc})">'
        f'<path d="M -10,20 C 24,24 44,2 38,-22 C 32,-42 4,-46 -12,-30 '
        f'C -22,-18 -14,-2 0,-6 C 12,-8 12,-20 2,-20" '
        f'fill="#FFFFFF" stroke="{OL}" stroke-width="6.8" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<path d="M 14,-32 C 26,-30 34,-18 32,-6" fill="none" stroke="#ECC49C" stroke-width="7" stroke-linecap="round"/>'
        f'</g>'
    )


def _pine_sprig(cx, cy, sc=1.0, rot=0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot}) scale({sc})">'
        f'<path d="M 0,18 Q 2,0 0,-18" fill="none" stroke="#2D6A4F" stroke-width="4" stroke-linecap="round"/>'
        f'<path d="M 0,8 L -14,-2 M 0,8 L 14,-2 M 0,-2 L -13,-12 M 0,-2 L 13,-12 M 0,-10 L -8,-20 M 0,-10 L 8,-20" '
        f'stroke="#40916C" stroke-width="3.6" stroke-linecap="round"/>'
        f'<circle cx="0" cy="14" r="4.2" fill="#D94B4B" stroke="#334155" stroke-width="2"/>'
        f'</g>'
    )


def draw_akita_inu(stage: int) -> str:
    OL = "#334155"
    APRI = "#ECC49C"
    SNOW = "#FFFFFF"

    cushion = (
        shadow(150, 250, 90, 15, 0.12)
        + f'<rect x="62" y="206" width="176" height="44" rx="18" fill="#2E538A" stroke="{OL}" stroke-width="7"/>'
        + f'<rect x="78" y="214" width="144" height="22" rx="10" fill="#E6F0FA" stroke="#1E3A63" stroke-width="2.8"/>'
        + f'<circle cx="62" cy="228" r="8" fill="#D94B4B" stroke="{OL}" stroke-width="4.2"/>'
        + f'<circle cx="238" cy="228" r="8" fill="#D94B4B" stroke="{OL}" stroke-width="4.2"/>'
        + paw_print(150, 225, 0.72, "#3B6CB7")
    )

    if stage == 0:
        return cushion + snowflake(150, 158, 16)

    if stage == 1:
        # Fluffy Akita puppy curled snugly on the indigo tatami cushion
        pup_body = (
            f'<path d="M 96,214 C 90,180 120,156 162,160 C 202,164 218,190 210,214 '
            f'C 202,230 166,232 132,230 C 108,228 98,224 96,214 Z" '
            f'fill="{SNOW}" stroke="{OL}" stroke-width="7"/>'
            f'<path d="M 134,162 C 166,158 196,170 202,190 C 180,182 156,180 134,186 Z" fill="{APRI}"/>'
            f'<path d="M 96,214 C 90,180 120,156 162,160 C 202,164 218,190 210,214" fill="none" stroke="{OL}" stroke-width="7"/>'
        )
        return cushion + pup_body + _akita_head(134, 180, sc=0.70, tilt=-6, sleepy=True) + snowflake(216, 134, 13)

    if stage == 2:
        # Chubby plush Akita pup sitting neatly with thick white neck ruff
        body = (
            shadow(150, 260, 66, 13)
            + _akita_fluffy_tail(208, 212, sc=0.82, rot=-8)
            + f'<path d="M 102,182 C 92,216 94,250 118,258 C 136,264 164,264 182,258 '
              f'C 206,250 208,216 198,182 C 186,162 114,162 102,182 Z" '
              f'fill="{SNOW}" stroke="{OL}" stroke-width="7"/>'
            + f'<path d="M 104,190 C 96,214 98,240 112,248 C 118,230 118,208 116,192 Z" fill="{APRI}"/>'
            + f'<path d="M 196,190 C 204,214 202,240 188,248 C 182,230 182,208 184,192 Z" fill="{APRI}"/>'
            + f'<path d="M 102,182 C 92,216 94,250 118,258 C 136,264 164,264 182,258 C 206,250 208,216 198,182" fill="none" stroke="{OL}" stroke-width="7"/>'
            + _sitting_paws(150, 259, SNOW, OL, spread=17, leg_h=22)
        )
        return body + _akita_ruff(150, 184, sc=0.92) + _akita_head(150, 136, sc=0.88)

    if stage == 3:
        # Loyal Akita sitting tall with indigo scarf collar & golden bell
        body = (
            shadow(150, 262, 70, 13)
            + _akita_fluffy_tail(214, 210, sc=0.92, rot=-6)
            + f'<path d="M 98,176 C 88,212 90,252 116,260 C 134,265 166,265 184,260 '
              f'C 210,252 212,212 202,176 C 188,156 112,156 98,176 Z" '
              f'fill="{SNOW}" stroke="{OL}" stroke-width="7.2"/>'
            + f'<path d="M 100,188 C 92,212 94,242 110,250 C 118,232 118,208 116,188 Z" fill="{APRI}"/>'
            + f'<path d="M 200,188 C 208,212 206,242 190,250 C 182,232 182,208 184,188 Z" fill="{APRI}"/>'
            + f'<path d="M 98,176 C 88,212 90,252 116,260 C 134,265 166,265 184,260 C 210,252 212,212 202,176" fill="none" stroke="{OL}" stroke-width="7.2"/>'
            + _sitting_paws(150, 260, SNOW, OL, spread=18, leg_h=24)
        )
        collar = (
            f'<path d="M 110,174 C 132,190 168,190 190,174 C 192,186 174,198 150,198 C 126,198 108,186 110,174 Z" '
            f'fill="#2E538A" stroke="{OL}" stroke-width="5.6" stroke-linejoin="round"/>'
            f'<circle cx="150" cy="202" r="9.5" fill="#FCD34D" stroke="{OL}" stroke-width="4.2"/>'
            f'<line x1="145" y1="204" x2="155" y2="204" stroke="{OL}" stroke-width="2.6" stroke-linecap="round"/>'
        )
        return body + _akita_ruff(150, 184, sc=1.0) + collar + _akita_head(150, 128, sc=0.94)

    if stage == 4:
        # Noble Akita in proud natural FOUR-LEGGED STANDING stance (fluffy chest + curled tail aloft!)
        stand = (
            shadow(154, 264, 88, 13)
            + _akita_fluffy_tail(226, 152, sc=0.98, rot=-18)
            + f'<path d="M 124,206 L 122,254 C 122,262 138,262 138,254 L 140,210" fill="#E8EEF5" stroke="{OL}" stroke-width="5.8" stroke-linecap="round"/>'
            + f'<path d="M 202,202 L 204,254 C 204,262 220,262 220,254 L 220,200" fill="#E8EEF5" stroke="{OL}" stroke-width="5.8" stroke-linecap="round"/>'
            + f'<path d="M 94,174 C 102,156 154,154 204,162 C 232,166 238,194 226,214 '
              f'C 214,232 164,234 118,228 C 94,224 86,196 94,174 Z" '
              f'fill="{SNOW}" stroke="{OL}" stroke-width="7.2" stroke-linejoin="round"/>'
            + f'<path d="M 134,158 C 166,156 206,162 222,178 C 204,190 166,188 134,182 Z" fill="{APRI}"/>'
            + f'<path d="M 94,174 C 102,156 154,154 204,162 C 232,166 238,194 226,214" fill="none" stroke="{OL}" stroke-width="7.2"/>'
            + f'<path d="M 102,204 L 100,256 C 100,264 118,264 118,256 L 122,210" fill="{SNOW}" stroke="{OL}" stroke-width="6.2" stroke-linecap="round"/>'
            + f'<path d="M 184,198 C 178,218 182,240 184,256 C 184,264 204,264 204,256 L 204,210" fill="{SNOW}" stroke="{OL}" stroke-width="6.2" stroke-linecap="round"/>'
        )
        collar = (
            f'<path d="M 86,174 C 104,188 130,186 144,172 C 146,184 130,194 112,194 C 94,194 84,184 86,174 Z" '
            f'fill="#2E538A" stroke="{OL}" stroke-width="5.2" stroke-linejoin="round"/>'
            f'<circle cx="110" cy="198" r="8.5" fill="#FCD34D" stroke="{OL}" stroke-width="3.8"/>'
        )
        return (
            stand
            + _akita_ruff(112, 178, sc=0.82)
            + collar
            + _akita_head(112, 128, sc=0.90, tilt=-4)
            + snowflake(44, 62, 13)
            + snowflake(244, 74, 14)
        )

    # Stage 5: Grand Loyal Snow Akita Inu with Japanese Indigo & Gold Braided Shimenawa Collar + golden bell + snowflakes & winter pine sprigs — NO CROWN!
    body = (
        shadow(150, 264, 76, 14)
        + _akita_fluffy_tail(220, 204, sc=1.06, rot=-8)
        + f'<path d="M 94,172 C 84,210 86,252 114,260 C 134,266 166,266 186,260 '
          f'C 214,252 216,210 206,172 C 190,152 110,152 94,172 Z" '
          f'fill="{SNOW}" stroke="{OL}" stroke-width="7.4"/>'
        + f'<path d="M 96,184 C 88,210 92,242 108,250 C 116,232 116,208 114,186 Z" fill="{APRI}"/>'
        + f'<path d="M 204,184 C 212,210 208,242 192,250 C 184,232 184,208 186,186 Z" fill="{APRI}"/>'
        + f'<path d="M 94,172 C 84,210 86,252 114,260 C 134,266 166,266 186,260 C 214,252 216,210 206,172" fill="none" stroke="{OL}" stroke-width="7.4"/>'
        + _sitting_paws(150, 262, SNOW, OL, spread=19, leg_h=24)
    )
    deco = (
        snowflake(54, 72, 15)
        + snowflake(248, 74, 15)
        + snowflake(150, 36, 12)
        + _pine_sprig(54, 218, 1.05, -24)
        + _pine_sprig(248, 224, 1.0, 26)
        + sparkle4(240, 146, 11)
    )
    return (
        deco
        + body
        + _akita_ruff(150, 184, sc=1.06)
        + _akita_shimenawa_collar(150, 178, sc=1.06)
        + _akita_head(150, 122, sc=0.98, calm_smile=True)
    )


# =========================================================================== #
#  3. GINGER KITTEN (`assets/ginger_kitten/`) — CHUBBY TABBY KITTEN (ZERO WHEEL-BLOB, ZERO STICK-ARMS!)
# =========================================================================== #
def _ginger_head(cx, cy, sc=1.0, tilt=0.0, sleepy=False, happy_sq=False) -> str:
    """Chubby warm peach-ginger tabby kitten head with forehead M stripes, whiskers & tiny pink nose!"""
    OL = "#4A3228"
    FUR = "#F5AD6B"
    STR = "#C86E2B"
    CRM = "#FFF6EA"
    EAR_IN = "#F8C2B8"
    BLUSH = "#F5989D"

    ear_l = (
        f'<path d="M -46,-18 L -52,-68 C -52,-74 -44,-76 -38,-72 L -12,-46 Z" '
        f'fill="{FUR}" stroke="{OL}" stroke-width="6.8" stroke-linejoin="round"/>'
        f'<path d="M -42,-28 L -45,-60 L -23,-43 Z" fill="{EAR_IN}"/>'
    )
    ear_r = (
        f'<path d="M 46,-18 L 52,-68 C 52,-74 44,-76 38,-72 L 12,-46 Z" '
        f'fill="{FUR}" stroke="{OL}" stroke-width="6.8" stroke-linejoin="round"/>'
        f'<path d="M 42,-28 L 45,-60 L 23,-43 Z" fill="{EAR_IN}"/>'
    )

    head_path = (
        "M 0,-48 C 34,-48 58,-30 60,-2 C 62,24 44,44 0,44 C -44,44 -62,24 -60,-2 C -58,-30 -34,-48 0,-48 Z"
    )
    head = f'<path d="{head_path}" fill="{FUR}" stroke="{OL}" stroke-width="7" stroke-linejoin="round"/>'
    muzzle = f'<ellipse cx="0" cy="18" rx="34" ry="20" fill="{CRM}"/>'
    head_ol = f'<path d="{head_path}" fill="none" stroke="{OL}" stroke-width="7" stroke-linejoin="round"/>'

    # Iconic forehead `M` tabby stripes + cute cheek tabby stripes!
    stripes = (
        f'<path d="M -14,-44 L -10,-28 M 0,-46 L 0,-26 M 14,-44 L 10,-28" '
        f'stroke="{STR}" stroke-width="5" stroke-linecap="round"/>'
        f'<path d="M -54,4 L -40,6 M -52,16 L -38,15 M 54,4 L 40,6 M 52,16 L 38,15" '
        f'stroke="{STR}" stroke-width="4.4" stroke-linecap="round"/>'
    )

    if sleepy:
        eyes = (
            f'<path d="M -30,-2 Q -22,6 -14,-2" fill="none" stroke="{OL}" stroke-width="4.8" stroke-linecap="round"/>'
            f'<path d="M 14,-2 Q 22,6 30,-2" fill="none" stroke="{OL}" stroke-width="4.8" stroke-linecap="round"/>'
        )
    elif happy_sq:
        eyes = (
            f'<path d="M -30,2 Q -22,-10 -14,2" fill="none" stroke="{OL}" stroke-width="5" stroke-linecap="round"/>'
            f'<path d="M 14,2 Q 22,-10 30,2" fill="none" stroke="{OL}" stroke-width="5" stroke-linecap="round"/>'
        )
    else:
        eyes = (
            f'<circle cx="-22" cy="-3" r="6.4" fill="{OL}"/>'
            f'<circle cx="-24.2" cy="-5.4" r="2.4" fill="#FFFFFF"/>'
            f'<circle cx="22" cy="-3" r="6.4" fill="{OL}"/>'
            f'<circle cx="19.8" cy="-5.4" r="2.4" fill="#FFFFFF"/>'
        )

    blush = (
        f'<ellipse cx="-35" cy="12" rx="8.5" ry="4.8" fill="{BLUSH}" fill-opacity="0.52"/>'
        f'<ellipse cx="35" cy="12" rx="8.5" ry="4.8" fill="{BLUSH}" fill-opacity="0.52"/>'
    )
    nose_mouth = (
        f'<polygon points="-5,8 5,8 0,14" fill="#E87A82" stroke="{OL}" stroke-width="2.4" stroke-linejoin="round"/>'
        f'<path d="M -11,18 Q -5.5,25 0,18 Q 5.5,25 11,18" fill="none" stroke="{OL}" stroke-width="4" stroke-linecap="round"/>'
    )
    whiskers = (
        f'<path d="M -46,8 L -66,4 M -46,16 L -66,18 M 46,8 L 66,4 M 46,16 L 66,18" '
        f'stroke="{OL}" stroke-width="3" stroke-linecap="round" stroke-opacity="0.72"/>'
    )

    return (
        f'<g transform="translate({cx},{cy}) rotate({tilt}) scale({sc})">'
        f'{ear_l}{ear_r}{head}{muzzle}{stripes}{head_ol}{blush}{eyes}{nose_mouth}{whiskers}'
        f'</g>'
    )


def _wicker_basket(cx=150, cy=218) -> str:
    """Cozy woven wicker cat basket with soft cream cushion inside."""
    OL = "#4A3228"
    return (
        shadow(cx, cy + 44, 86, 13, 0.13)
        # Soft cream cushion peeking inside top
        + f'<ellipse cx="{cx}" cy="{cy - 22}" rx="74" ry="18" fill="#FFF7EA" stroke="{OL}" stroke-width="6"/>'
        # Basket body trapezoid with rounded bottom
        + f'<path d="M {cx - 82},{cy - 20} L {cx - 66},{cy + 34} C {cx - 62},{cy + 44} {cx + 62},{cy + 44} {cx + 66},{cy + 34} '
          f'L {cx + 82},{cy - 20} Z" fill="#D49558" stroke="{OL}" stroke-width="7" stroke-linejoin="round"/>'
        # Woven horizontal & vertical wicker lines
        + f'<line x1="{cx - 76}" y1="{cy - 2}" x2="{cx + 76}" y2="{cy - 2}" stroke="#9C6430" stroke-width="4.2"/>'
        + f'<line x1="{cx - 70}" y1="{cy + 16}" x2="{cx + 70}" y2="{cy + 16}" stroke="#9C6430" stroke-width="4.2"/>'
        + f'<line x1="{cx - 42}" y1="{cy - 18}" x2="{cx - 34}" y2="{cy + 36}" stroke="#B3753B" stroke-width="3.2"/>'
        + f'<line x1="{cx}" y1="{cy - 18}" x2="{cx}" y2="{cy + 38}" stroke="#B3753B" stroke-width="3.2"/>'
        + f'<line x1="{cx + 42}" y1="{cy - 18}" x2="{cx + 34}" y2="{cy + 36}" stroke="#B3753B" stroke-width="3.2"/>'
        # Braided wicker top rim
        + f'<rect x="{cx - 88}" y="{cy - 30}" width="176" height="20" rx="10" fill="#E3AA6E" stroke="{OL}" stroke-width="6.8"/>'
    )


def _mint_yarn_ball(cx, cy, r=24) -> str:
    OL = "#4A3228"
    return (
        f'<g transform="translate({cx},{cy})">'
        f'<path d="M {r - 2},{r * 0.5} C {r + 18},{r * 0.8} {r + 24},{r * 0.1} {r + 36},{r * 0.65}" '
        f'fill="none" stroke="#53B195" stroke-width="5.2" stroke-linecap="round"/>'
        f'<circle cx="0" cy="0" r="{r}" fill="#85D6BE" stroke="{OL}" stroke-width="5.8"/>'
        f'<path d="M {-r * 0.72},{-r * 0.28} Q 0,{-r * 0.65} {r * 0.78},{-r * 0.1}" fill="none" stroke="#4D9E85" stroke-width="3.6" stroke-linecap="round"/>'
        f'<path d="M {-r * 0.65},{r * 0.35} Q 2,{-r * 0.05} {r * 0.68},{r * 0.38}" fill="none" stroke="#4D9E85" stroke-width="3.6" stroke-linecap="round"/>'
        f'<path d="M {-r * 0.2},{-r * 0.78} Q {r * 0.25},0 {-r * 0.1},{r * 0.78}" fill="none" stroke="#4D9E85" stroke-width="3.4" stroke-linecap="round"/>'
        f'</g>'
    )


def _mint_bow_tie(cx, cy, sc=1.0) -> str:
    OL = "#4A3228"
    return (
        f'<g transform="translate({cx},{cy}) scale({sc})">'
        f'<path d="M 0,0 L -24,-13 C -28,-6 -28,6 -24,13 Z" fill="#7FD1B9" stroke="{OL}" stroke-width="4.8" stroke-linejoin="round"/>'
        f'<path d="M 0,0 L 24,-13 C 28,-6 28,6 24,13 Z" fill="#7FD1B9" stroke="{OL}" stroke-width="4.8" stroke-linejoin="round"/>'
        f'<circle cx="0" cy="0" r="7.5" fill="#53B195" stroke="{OL}" stroke-width="4.5"/>'
        f'</g>'
    )


def _fish_plushie(cx, cy, sc=1.0, rot=-10) -> str:
    OL = "#4A3228"
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot}) scale({sc})">'
        f'<path d="M 22,0 L 38,-14 C 42,-4 42,4 38,14 Z" fill="#7FD1B9" stroke="{OL}" stroke-width="4.6" stroke-linejoin="round"/>'
        f'<ellipse cx="-2" cy="0" rx="26" ry="15" fill="#A5E5D2" stroke="{OL}" stroke-width="4.8"/>'
        f'<circle cx="-14" cy="-3" r="2.8" fill="{OL}"/>'
        f'<path d="M 2,-10 Q 8,0 2,10 M 10,-9 Q 15,0 10,9" fill="none" stroke="#53B195" stroke-width="3" stroke-linecap="round"/>'
        f'</g>'
    )


def draw_ginger_kitten(stage: int) -> str:
    OL = "#4A3228"
    FUR = "#F5AD6B"
    STR = "#C86E2B"
    CRM = "#FFF6EA"

    if stage == 0:
        return _wicker_basket(150, 218)

    if stage == 1:
        # Sleepy ginger kitten curled snugly inside the wicker basket
        back_curl = (
            f'<ellipse cx="164" cy="186" rx="48" ry="26" fill="{FUR}" stroke="{OL}" stroke-width="6.8"/>'
            f'<path d="M 166,162 L 164,178 M 182,166 L 178,180" stroke="{STR}" stroke-width="4.8" stroke-linecap="round"/>'
        )
        # Draw basket back cushion, sleeping kitten, then basket front rim so kitten sits INSIDE!
        cushion_back = shadow(150, 262, 86, 13, 0.13) + f'<ellipse cx="150" cy="196" rx="74" ry="18" fill="#FFF7EA" stroke="{OL}" stroke-width="6"/>'
        basket_front = (
            f'<path d="M 68,198 L 84,252 C 88,262 212,262 216,252 L 232,198 Z" fill="#D49558" stroke="{OL}" stroke-width="7" stroke-linejoin="round"/>'
            f'<line x1="74" y1="216" x2="226" y2="216" stroke="#9C6430" stroke-width="4.2"/>'
            f'<line x1="80" y1="234" x2="220" y2="234" stroke="#9C6430" stroke-width="4.2"/>'
            f'<rect x="62" y="188" width="176" height="20" rx="10" fill="#E3AA6E" stroke="{OL}" stroke-width="6.8"/>'
        )
        zzz = '<text x="206" y="142" font-family="Segoe UI, Arial" font-weight="bold" font-size="22" fill="#C86E2B">z</text>'
        return cushion_back + back_curl + _ginger_head(132, 174, sc=0.72, tilt=-7, sleepy=True) + basket_front + zzz

    if stage == 2:
        # Awake ginger kitten peeking curiously over the basket rim with two curved front paws resting on rim!
        cushion_back = shadow(150, 262, 86, 13, 0.13) + f'<ellipse cx="150" cy="196" rx="74" ry="18" fill="#FFF7EA" stroke="{OL}" stroke-width="6"/>'
        basket_front = (
            f'<path d="M 68,198 L 84,252 C 88,262 212,262 216,252 L 232,198 Z" fill="#D49558" stroke="{OL}" stroke-width="7" stroke-linejoin="round"/>'
            f'<line x1="74" y1="216" x2="226" y2="216" stroke="#9C6430" stroke-width="4.2"/>'
            f'<line x1="80" y1="234" x2="220" y2="234" stroke="#9C6430" stroke-width="4.2"/>'
            f'<rect x="62" y="188" width="176" height="20" rx="10" fill="#E3AA6E" stroke="{OL}" stroke-width="6.8"/>'
        )
        paws_on_rim = (
            f'<ellipse cx="116" cy="195" rx="14" ry="11" fill="{CRM}" stroke="{OL}" stroke-width="5.8"/>'
            f'<ellipse cx="184" cy="195" rx="14" ry="11" fill="{CRM}" stroke="{OL}" stroke-width="5.8"/>'
        )
        return cushion_back + _ginger_head(150, 152, sc=0.84, tilt=3) + basket_front + paws_on_rim

    if stage == 3:
        # Chubby loaf / sitting ginger kitten outside the basket, paws neatly tucked, curved striped tail wrapped around side!
        # (COMPLETELY REPLACES the deformed wheel-blob!)
        tail_wrap = (
            f'<path d="M 198,236 C 234,236 244,198 228,176 C 220,164 206,170 210,182 '
            f'C 218,198 212,216 196,220" fill="{FUR}" stroke="{OL}" stroke-width="6.8" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="M 222,194 L 234,190 M 218,210 L 232,212" stroke="{STR}" stroke-width="4.6" stroke-linecap="round"/>'
        )
        body = (
            shadow(150, 260, 72, 13)
            + tail_wrap
            # Plump pear-shaped chubby sitting kitten silhouette
            + f'<path d="M 102,174 C 86,204 86,248 118,258 C 138,264 162,264 182,258 '
              f'C 214,248 214,204 198,174 C 184,154 116,154 102,174 Z" '
              f'fill="{FUR}" stroke="{OL}" stroke-width="7.2" stroke-linejoin="round"/>'
            # Soft cream tummy patch
            + f'<ellipse cx="150" cy="222" rx="34" ry="32" fill="{CRM}"/>'
            # Subtle side tabby stripes
            + f'<path d="M 94,208 L 108,210 M 94,224 L 110,224 M 206,208 L 192,210 M 206,224 L 190,224" '
              f'stroke="{STR}" stroke-width="4.8" stroke-linecap="round"/>'
            + _sitting_paws(150, 260, CRM, OL, spread=17, leg_h=22)
        )
        return body + _ginger_head(150, 128, sc=0.92)

    if stage == 4:
        # Playful ginger kitten on ALL FOURS batting gently at a soft mint yarn ball! (NO stiff standing arms!)
        tail_up = (
            f'<path d="M 218,184 C 242,162 246,120 226,106 C 214,98 202,110 212,120 '
            f'C 222,130 220,154 206,170" fill="{FUR}" stroke="{OL}" stroke-width="6.8" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="M 222,128 L 236,126 M 220,148 L 234,150" stroke="{STR}" stroke-width="4.4" stroke-linecap="round"/>'
        )
        crouch = (
            shadow(154, 262, 92, 13)
            + tail_up
            # Far hind leg
            + f'<path d="M 206,214 L 210,252 C 210,260 226,260 226,252 L 226,208" fill="{CRM}" stroke="{OL}" stroke-width="5.8" stroke-linecap="round"/>'
            # Natural curved all-fours kitten torso (playful slight arch!)
            + f'<path d="M 116,192 C 138,162 192,158 218,176 C 236,190 236,218 220,232 '
              f'C 202,244 156,244 130,236 C 110,230 104,210 116,192 Z" '
              f'fill="{FUR}" stroke="{OL}" stroke-width="7.2" stroke-linejoin="round"/>'
            # Back tabby stripes on arched back
            + f'<path d="M 164,166 L 166,184 M 184,164 L 184,182 M 202,168 L 198,184" stroke="{STR}" stroke-width="5" stroke-linecap="round"/>'
            # Near hind leg
            + f'<path d="M 190,204 C 182,224 186,242 188,254 C 188,262 208,262 208,254 L 208,216" '
              f'fill="{FUR}" stroke="{OL}" stroke-width="6.2" stroke-linecap="round"/>'
            + f'<ellipse cx="198" cy="256" rx="11" ry="7" fill="{CRM}" stroke="{OL}" stroke-width="5"/>'
            # Planted right front paw + playful curved left paw batting the mint yarn ball!
            + f'<path d="M 134,216 L 130,254 C 130,262 148,262 148,254 L 150,220" fill="{CRM}" stroke="{OL}" stroke-width="5.8" stroke-linecap="round"/>'
            + _mint_yarn_ball(74, 240, 23)
            + f'<path d="M 122,208 C 106,214 96,222 92,232 C 88,240 100,248 108,240 C 116,232 126,226 134,222" '
              f'fill="{CRM}" stroke="{OL}" stroke-width="5.8" stroke-linecap="round" stroke-linejoin="round"/>'
        )
        return crouch + _ginger_head(122, 146, sc=0.88, tilt=-8) + heart(178, 92, 13, "#F5989D", OL, 2.6, 10)

    # Stage 5: Joyful Chubby Ginger Cat sitting proudly with pastel mint bow tie, fish plushie & golden sparkles — NO CROWN, NO STICK ARMS!
    tail_wrap = (
        f'<path d="M 204,236 C 242,236 254,192 234,168 C 224,156 210,164 216,176 '
        f'C 224,194 218,216 200,220" fill="{FUR}" stroke="{OL}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<path d="M 228,188 L 242,184 M 224,208 L 238,210" stroke="{STR}" stroke-width="4.8" stroke-linecap="round"/>'
    )
    body = (
        shadow(150, 264, 78, 14)
        + tail_wrap
        + f'<path d="M 98,172 C 82,204 84,250 116,260 C 138,266 162,266 184,260 '
          f'C 216,250 218,204 202,172 C 188,152 112,152 98,172 Z" '
          f'fill="{FUR}" stroke="{OL}" stroke-width="7.4" stroke-linejoin="round"/>'
        + f'<ellipse cx="150" cy="222" rx="36" ry="34" fill="{CRM}"/>'
        + f'<path d="M 90,206 L 106,208 M 90,224 L 108,224 M 210,206 L 194,208 M 210,224 L 192,224" '
          f'stroke="{STR}" stroke-width="5" stroke-linecap="round"/>'
        + _sitting_paws(150, 262, CRM, OL, spread=22, leg_h=23)
    )
    deco = sparkle4(58, 76, 15) + sparkle4(244, 72, 15) + sparkle4(54, 168, 10)
    return (
        deco
        + body
        + _mint_bow_tie(150, 174, sc=1.08)
        + _ginger_head(150, 122, sc=0.96, happy_sq=True)
        + _fish_plushie(150, 248, sc=0.96, rot=-6)
    )


# =========================================================================== #
#  4. ROYAL CAT SAVING CASH (`assets/royal_cat_cash/`) — EXCLUSIVE GOLDEN CROWN OWNER!
# =========================================================================== #
def _comic_white_cat_head(cx, cy, sc=1.0, tilt=0.0, happy=False, crown=False) -> str:
    """Minimalist thick-line comic white cat (honoring the Raising Cats & Saving Cash ref)."""
    OL = "#3A2E2B"
    WHT = "#FFFFFF"
    BLUSH = "#F6B0B8"

    ear_l = (
        f'<path d="M -44,-18 L -50,-64 C -50,-70 -42,-72 -36,-68 L -12,-44 Z" '
        f'fill="{WHT}" stroke="{OL}" stroke-width="6.8" stroke-linejoin="round"/>'
        f'<path d="M -40,-28 L -43,-56 L -22,-42 Z" fill="#F9D5DA"/>'
    )
    ear_r = (
        f'<path d="M 44,-18 L 50,-64 C 50,-70 42,-72 36,-68 L 12,-44 Z" '
        f'fill="{WHT}" stroke="{OL}" stroke-width="6.8" stroke-linejoin="round"/>'
        f'<path d="M 40,-28 L 43,-56 L 22,-42 Z" fill="#F9D5DA"/>'
    )
    head = (
        f'<path d="M 0,-46 C 34,-46 58,-28 58,-2 C 58,24 40,42 0,42 C -40,42 -58,24 -58,-2 C -58,-28 -34,-46 0,-46 Z" '
        f'fill="{WHT}" stroke="{OL}" stroke-width="7" stroke-linejoin="round"/>'
    )
    if happy:
        eyes = (
            f'<path d="M -28,0 Q -20,-10 -12,0" fill="none" stroke="{OL}" stroke-width="5" stroke-linecap="round"/>'
            f'<path d="M 12,0 Q 20,-10 28,0" fill="none" stroke="{OL}" stroke-width="5" stroke-linecap="round"/>'
        )
    else:
        eyes = (
            f'<circle cx="-20" cy="-2" r="5.6" fill="{OL}"/>'
            f'<circle cx="-22" cy="-4.2" r="2.1" fill="#FFFFFF"/>'
            f'<circle cx="20" cy="-2" r="5.6" fill="{OL}"/>'
            f'<circle cx="18" cy="-4.2" r="2.1" fill="#FFFFFF"/>'
        )
    face = (
        f'<ellipse cx="-34" cy="10" rx="8.5" ry="4.8" fill="{BLUSH}" fill-opacity="0.6"/>'
        f'<ellipse cx="34" cy="10" rx="8.5" ry="4.8" fill="{BLUSH}" fill-opacity="0.6"/>'
        f'<circle cx="0" cy="6" r="3.4" fill="#E88A96"/>'
        f'<path d="M -10,14 Q -5,21 0,14 Q 5,21 10,14" fill="none" stroke="{OL}" stroke-width="4" stroke-linecap="round"/>'
        f'<path d="M -46,6 L -64,3 M -46,14 L -64,16 M 46,6 L 64,3 M 46,14 L 64,16" stroke="{OL}" stroke-width="3.2" stroke-linecap="round"/>'
    )
    crown_svg = ""
    if crown:
        crown_svg = (
            f'<path d="M -26,-44 L -32,-80 L -10,-62 L 0,-86 L 10,-62 L 32,-80 L 26,-44 Z" '
            f'fill="#FCD34D" stroke="{OL}" stroke-width="5.8" stroke-linejoin="round"/>'
            f'<circle cx="0" cy="-58" r="4.5" fill="#E11D48"/>'
            f'<circle cx="-16" cy="-55" r="3.2" fill="#38BDF8"/>'
            f'<circle cx="16" cy="-55" r="3.2" fill="#38BDF8"/>'
        )
    return (
        f'<g transform="translate({cx},{cy}) rotate({tilt}) scale({sc})">'
        f'{ear_l}{ear_r}{head}{eyes}{face}{crown_svg}'
        f'</g>'
    )


def _gold_coin(cx, cy, r=16) -> str:
    OL = "#3A2E2B"
    return (
        f'<g transform="translate({cx},{cy})">'
        f'<circle cx="0" cy="0" r="{r}" fill="#FCD34D" stroke="{OL}" stroke-width="4.5"/>'
        f'<circle cx="0" cy="0" r="{r * 0.72}" fill="none" stroke="#D99B1E" stroke-width="2.6"/>'
        f'<text x="0" y="{r * 0.36}" text-anchor="middle" font-family="Segoe UI, Arial" font-weight="bold" font-size="{int(r * 1.1)}" fill="#925E08">$</text>'
        f'</g>'
    )


def draw_royal_cat_cash(stage: int) -> str:
    OL = "#3A2E2B"
    WHT = "#FFFFFF"
    BOX = "#C9A17A"
    BOX_DK = "#AD825B"

    if stage == 0:
        # Funny white cat hiding under a tilted cardboard box ("broke start")!
        cat_under = (
            shadow(150, 256, 76, 13)
            + f'<ellipse cx="150" cy="228" rx="48" ry="26" fill="{WHT}" stroke="{OL}" stroke-width="6.8"/>'
            + f'<circle cx="134" cy="226" r="4.8" fill="{OL}"/>'
            + f'<circle cx="166" cy="226" r="4.8" fill="{OL}"/>'
            + f'<ellipse cx="122" cy="234" rx="7" ry="4" fill="#F6B0B8" fill-opacity="0.65"/>'
            + f'<ellipse cx="178" cy="234" rx="7" ry="4" fill="#F6B0B8" fill-opacity="0.65"/>'
            + f'<path d="M 142,235 Q 146,240 150,235 Q 154,240 158,235" fill="none" stroke="{OL}" stroke-width="3.6" stroke-linecap="round"/>'
        )
        tilted_box = (
            f'<g transform="translate(150,174) rotate(-8)">'
            f'<path d="M -68,-38 L 68,-38 L 82,42 L -82,42 Z" fill="{BOX}" stroke="{OL}" stroke-width="7" stroke-linejoin="round"/>'
            f'<path d="M -52,-38 L 52,-38 L 58,42 L -58,42 Z" fill="#D5AF8A" stroke="{OL}" stroke-width="5"/>'
            f'<rect x="-18" y="8" width="36" height="10" rx="5" fill="{OL}"/>'
            f'</g>'
        )
        return cat_under + tilted_box

    if stage == 1:
        # White cat peeking happily out of upright open cardboard box
        box_back = shadow(150, 260, 76, 13) + f'<rect x="92" y="166" width="116" height="90" rx="8" fill="{BOX_DK}" stroke="{OL}" stroke-width="7"/>'
        box_front = (
            f'<path d="M 92,172 L 66,154 L 80,140 L 106,166 Z" fill="{BOX}" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>'
            f'<path d="M 208,172 L 234,154 L 220,140 L 194,166 Z" fill="{BOX}" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>'
            f'<rect x="92" y="170" width="116" height="86" rx="8" fill="{BOX}" stroke="{OL}" stroke-width="7"/>'
            f'<rect x="136" y="170" width="28" height="22" fill="#E6CAA8" stroke="{OL}" stroke-width="4"/>'
        )
        paws = (
            f'<ellipse cx="118" cy="172" rx="13" ry="10" fill="{WHT}" stroke="{OL}" stroke-width="5.6"/>'
            f'<ellipse cx="182" cy="172" rx="13" ry="10" fill="{WHT}" stroke="{OL}" stroke-width="5.6"/>'
        )
        return box_back + _comic_white_cat_head(150, 144, sc=0.82) + box_front + paws

    if stage == 2:
        # Calm white cat sitting neatly beside a gleaming gold coin
        tail = f'<path d="M 186,238 C 224,238 234,198 220,180 C 212,170 200,178 206,188 C 214,202 208,220 186,222" fill="{WHT}" stroke="{OL}" stroke-width="6.8" stroke-linecap="round"/>'
        body = (
            shadow(142, 260, 68, 13)
            + tail
            + f'<path d="M 98,176 C 84,210 86,250 116,258 C 132,263 152,263 168,258 C 198,250 200,210 186,176 C 174,158 110,158 98,176 Z" '
              f'fill="{WHT}" stroke="{OL}" stroke-width="7" stroke-linejoin="round"/>'
            + _sitting_paws(142, 259, WHT, OL, spread=16, leg_h=21)
        )
        return body + _comic_white_cat_head(142, 134, sc=0.90) + _gold_coin(222, 242, 20)

    if stage == 3:
        # Happy chubby white cat hugging a blush-pink piggy bank + coin stack!
        tail = f'<path d="M 190,238 C 228,238 238,196 224,178 C 216,168 204,176 210,186 C 218,200 212,220 190,222" fill="{WHT}" stroke="{OL}" stroke-width="6.8" stroke-linecap="round"/>'
        body = (
            shadow(146, 262, 74, 13)
            + tail
            + f'<path d="M 96,174 C 82,208 84,250 116,258 C 134,264 158,264 176,258 C 208,250 210,208 196,174 C 182,156 110,156 96,174 Z" '
              f'fill="{WHT}" stroke="{OL}" stroke-width="7.2" stroke-linejoin="round"/>'
        )
        piggy = (
            f'<g transform="translate(146,230)">'
            f'<rect x="-20" y="20" width="11" height="11" rx="4" fill="#F392AA" stroke="{OL}" stroke-width="4"/>'
            f'<rect x="10" y="20" width="11" height="11" rx="4" fill="#F392AA" stroke="{OL}" stroke-width="4"/>'
            f'<ellipse cx="0" cy="4" rx="34" ry="24" fill="#F8B4C4" stroke="{OL}" stroke-width="5.6"/>'
            f'<ellipse cx="-26" cy="4" rx="11" ry="8" fill="#F392AA" stroke="{OL}" stroke-width="4.4"/>'
            f'<circle cx="-29" cy="3" r="2" fill="{OL}"/><circle cx="-23" cy="3" r="2" fill="{OL}"/>'
            f'<circle cx="-12" cy="-4" r="3" fill="{OL}"/>'
            f'<rect x="-6" y="-17" width="16" height="5" rx="2.5" fill="{OL}"/>'
            f'<path d="M -20,-14 L -26,-26 L -10,-19 Z" fill="#F8B4C4" stroke="{OL}" stroke-width="4.4" stroke-linejoin="round"/>'
            f'</g>'
        )
        hug_paws = (
            f'<ellipse cx="108" cy="224" rx="13" ry="10" fill="{WHT}" stroke="{OL}" stroke-width="5.4"/>'
            f'<ellipse cx="184" cy="224" rx="13" ry="10" fill="{WHT}" stroke="{OL}" stroke-width="5.4"/>'
        )
        return body + _comic_white_cat_head(146, 128, sc=0.92, happy=True) + piggy + hug_paws + _gold_coin(222, 246, 17)

    if stage == 4:
        # Proud white cat sitting regally atop a royal velvet pillow with gold tassels!
        pillow = (
            shadow(150, 264, 92, 13)
            + f'<path d="M 68,224 C 68,210 232,210 232,224 C 238,242 232,260 218,260 L 82,260 C 68,260 62,242 68,224 Z" '
              f'fill="#A84458" stroke="{OL}" stroke-width="6.8" stroke-linejoin="round"/>'
            + f'<circle cx="64" cy="244" r="9" fill="#FCD34D" stroke="{OL}" stroke-width="4.5"/>'
            + f'<circle cx="236" cy="244" r="9" fill="#FCD34D" stroke="{OL}" stroke-width="4.5"/>'
            + f'<path d="M 86,226 Q 150,236 214,226" fill="none" stroke="#FCD34D" stroke-width="3.6" stroke-linecap="round"/>'
        )
        tail = f'<path d="M 192,216 C 228,214 238,176 224,158 C 216,148 204,156 210,166 C 218,180 212,198 190,200" fill="{WHT}" stroke="{OL}" stroke-width="6.6" stroke-linecap="round"/>'
        body = (
            tail
            + f'<path d="M 102,160 C 90,190 92,228 120,234 C 138,238 162,238 180,234 C 208,228 210,190 198,160 C 186,144 114,144 102,160 Z" '
              f'fill="{WHT}" stroke="{OL}" stroke-width="7" stroke-linejoin="round"/>'
            + _sitting_paws(150, 235, WHT, OL, spread=16, leg_h=19)
        )
        return pillow + body + _comic_white_cat_head(150, 118, sc=0.90) + heart(224, 84, 14, "#F48A9E", OL, 2.8, 12)

    # Stage 5: THE ONLY ROYAL WHITE CAT WEARING A GOLDEN CROWN + velvet pillow + sparkling gold coins!
    pillow = (
        shadow(150, 266, 94, 13)
        + f'<path d="M 66,226 C 66,212 234,212 234,226 C 240,244 234,262 220,262 L 80,262 C 66,262 60,244 66,226 Z" '
          f'fill="#A84458" stroke="{OL}" stroke-width="6.8" stroke-linejoin="round"/>'
        + f'<circle cx="62" cy="246" r="9" fill="#FCD34D" stroke="{OL}" stroke-width="4.5"/>'
        + f'<circle cx="238" cy="246" r="9" fill="#FCD34D" stroke="{OL}" stroke-width="4.5"/>'
        + f'<path d="M 86,228 Q 150,238 214,228" fill="none" stroke="#FCD34D" stroke-width="3.6" stroke-linecap="round"/>'
    )
    tail = f'<path d="M 192,218 C 230,216 240,176 226,158 C 218,148 206,156 212,166 C 220,180 214,200 192,202" fill="{WHT}" stroke="{OL}" stroke-width="6.6" stroke-linecap="round"/>'
    body = (
        tail
        + f'<path d="M 102,164 C 90,194 92,230 120,236 C 138,240 162,240 180,236 C 208,230 210,194 198,164 C 186,148 114,148 102,164 Z" '
          f'fill="{WHT}" stroke="{OL}" stroke-width="7" stroke-linejoin="round"/>'
        + _sitting_paws(150, 237, WHT, OL, spread=16, leg_h=19)
    )
    coins = _gold_coin(78, 250, 16) + _gold_coin(222, 250, 16) + _gold_coin(206, 258, 13)
    deco = sparkle4(58, 76, 16) + sparkle4(244, 74, 15) + sparkle4(248, 164, 11)
    return deco + pillow + body + _comic_white_cat_head(150, 124, sc=0.90, happy=True, crown=True) + coins


# =========================================================================== #
#  5. PURPLE CAT (`assets/purple_cat/`) — DREAMY LAVENDER BRITISH SHORTHAIR / STARRY MOON CAT (NO BOX, NO CROWN!)
# =========================================================================== #
def _bsh_lilac_head(cx, cy, sc=1.0, tilt=0.0, sleepy=False, happy=False, beret=False) -> str:
    """Plush round British Shorthair grey-lilac cat: extra wide plush cheeks, smaller rounded ears, dreamy eyes!"""
    OL = "#3D3354"
    FUR = "#B0A6C8"
    CRM = "#F0ECF8"
    EAR_IN = "#F4B6CE"
    BLUSH = "#F49EC0"

    # Smaller rounded British Shorthair ears set cleanly on the plush dome
    ear_l = (
        f'<path d="M -46,-18 C -56,-42 -50,-64 -34,-62 C -20,-60 -12,-46 -12,-34 Z" '
        f'fill="{FUR}" stroke="{OL}" stroke-width="6.8" stroke-linejoin="round"/>'
        f'<path d="M -41,-26 C -46,-40 -42,-52 -33,-52 C -26,-52 -20,-42 -20,-34 Z" fill="{EAR_IN}"/>'
    )
    ear_r = (
        f'<path d="M 46,-18 C 56,-42 50,-64 34,-62 C 20,-60 12,-46 12,-34 Z" '
        f'fill="{FUR}" stroke="{OL}" stroke-width="6.8" stroke-linejoin="round"/>'
        f'<path d="M 41,-26 C 46,-40 42,-52 33,-52 C 26,-52 20,-42 20,-34 Z" fill="{EAR_IN}"/>'
    )

    # Extra-round chubby British Shorthair cheek silhouette
    head_path = (
        "M 0,-48 C 36,-48 62,-28 64,0 C 66,28 46,46 0,46 C -46,46 -66,28 -64,0 C -62,-28 -36,-48 0,-48 Z"
    )
    head = f'<path d="{head_path}" fill="{FUR}" stroke="{OL}" stroke-width="7.2" stroke-linejoin="round"/>'
    # Soft cream-lilac chubby muzzle pillows
    muzzle = (
        f'<ellipse cx="-11" cy="18" rx="16" ry="12" fill="{CRM}"/>'
        f'<ellipse cx="11" cy="18" rx="16" ry="12" fill="{CRM}"/>'
    )
    if sleepy:
        eyes = (
            f'<path d="M -32,-2 Q -24,6 -16,-2" fill="none" stroke="{OL}" stroke-width="4.8" stroke-linecap="round"/>'
            f'<path d="M 16,-2 Q 24,6 32,-2" fill="none" stroke="{OL}" stroke-width="4.8" stroke-linecap="round"/>'
        )
    elif happy:
        eyes = (
            f'<path d="M -32,1 Q -24,-10 -16,1" fill="none" stroke="{OL}" stroke-width="5" stroke-linecap="round"/>'
            f'<path d="M 16,1 Q 24,-10 32,1" fill="none" stroke="{OL}" stroke-width="5" stroke-linecap="round"/>'
        )
    else:
        # Big dreamy amber-violet sparkling eyes!
        eyes = (
            f'<circle cx="-23" cy="-3" r="7.5" fill="{OL}"/>'
            f'<circle cx="-25.4" cy="-5.8" r="2.8" fill="#FFFFFF"/>'
            f'<circle cx="-20.5" cy="0" r="1.4" fill="#FDE68A"/>'
            f'<circle cx="23" cy="-3" r="7.5" fill="{OL}"/>'
            f'<circle cx="20.6" cy="-5.8" r="2.8" fill="#FFFFFF"/>'
            f'<circle cx="25.5" cy="0" r="1.4" fill="#FDE68A"/>'
        )
    face = (
        f'<ellipse cx="-41" cy="12" rx="9" ry="5" fill="{BLUSH}" fill-opacity="0.55"/>'
        f'<ellipse cx="41" cy="12" rx="9" ry="5" fill="{BLUSH}" fill-opacity="0.55"/>'
        f'<polygon points="-5,8 5,8 0,14" fill="#E98AB4" stroke="{OL}" stroke-width="2.2" stroke-linejoin="round"/>'
        f'<path d="M -11,18 Q -5.5,25 0,18 Q 5.5,25 11,18" fill="none" stroke="{OL}" stroke-width="4" stroke-linecap="round"/>'
    )
    beret_svg = ""
    if beret:
        # Cute tilted lavender starry artist/witch beret (100% NOT a crown!)
        beret_svg = (
            f'<g transform="translate(8,-48) rotate(14)">'
            f'<path d="M -38,6 C -42,-16 -14,-28 8,-24 C 30,-20 42,-4 34,10 C 16,14 -20,14 -38,6 Z" '
            f'fill="#9D7AD6" stroke="{OL}" stroke-width="5.8" stroke-linejoin="round"/>'
            f'<path d="M 2,-24 Q 6,-34 12,-32" fill="none" stroke="{OL}" stroke-width="5" stroke-linecap="round"/>'
            f'{sparkle4(-8, -6, 8, "#FDE68A", "#9D7AD6", 1.8)}'
            f'</g>'
        )
    return (
        f'<g transform="translate({cx},{cy}) rotate({tilt}) scale({sc})">'
        f'{ear_l}{ear_r}{head}{muzzle}{eyes}{face}{beret_svg}'
        f'</g>'
    )


def _crescent_moon(cx, cy, sc=1.0, rot=0, fill="#FDE68A", stroke="#3D3354") -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot}) scale({sc})">'
        f'<path d="M 48,-42 C 12,-46 -22,-18 -20,22 C -18,62 20,86 58,76 '
        f'C 22,102 -36,88 -54,42 C -70,-2 -44,-56 6,-64 C 24,-66 38,-56 48,-42 Z" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="6.8" stroke-linejoin="round"/>'
        f'</g>'
    )


def _lilac_yarn_ball(cx, cy, r=36) -> str:
    OL = "#3D3354"
    return (
        f'<g transform="translate({cx},{cy})">'
        f'<path d="M {r - 4},{r * 0.65} C {r + 18},{r * 0.9} {r + 28},{r * 0.2} {r + 42},{r * 0.65}" '
        f'fill="none" stroke="#B68DF2" stroke-width="6" stroke-linecap="round"/>'
        f'<circle cx="0" cy="0" r="{r}" fill="#D8B4FE" stroke="{OL}" stroke-width="6.4"/>'
        f'<path d="M {-r * 0.72},{-r * 0.28} Q 0,{-r * 0.66} {r * 0.78},{-r * 0.1}" fill="none" stroke="#9D7AD6" stroke-width="4.2" stroke-linecap="round"/>'
        f'<path d="M {-r * 0.68},{r * 0.32} Q 2,{-r * 0.08} {r * 0.7},{r * 0.36}" fill="none" stroke="#9D7AD6" stroke-width="4.2" stroke-linecap="round"/>'
        f'<path d="M {-r * 0.22},{-r * 0.78} Q {r * 0.26},0 {-r * 0.1},{r * 0.78}" fill="none" stroke="#9D7AD6" stroke-width="3.8" stroke-linecap="round"/>'
        f'</g>'
    )


def draw_purple_cat(stage: int) -> str:
    OL = "#3D3354"
    FUR = "#B0A6C8"
    CRM = "#F0ECF8"

    moon_pillow = (
        shadow(150, 256, 88, 14, 0.12)
        + f'<path d="M 70,198 C 60,234 94,260 150,260 C 206,260 240,234 230,198 '
          f'C 216,218 186,226 150,226 C 114,226 84,218 70,198 Z" '
          f'fill="#C4B5FD" stroke="{OL}" stroke-width="7" stroke-linejoin="round"/>'
        + f'<ellipse cx="150" cy="222" rx="70" ry="22" fill="#EDE9FE" stroke="{OL}" stroke-width="5.6"/>'
        + sparkle4(150, 224, 12, "#FDE68A", "#9D7AD6", 2.2)
    )

    if stage == 0:
        return moon_pillow + sparkle4(88, 160, 13, "#FDE68A", "#9D7AD6", 2.2) + sparkle4(214, 152, 11, "#DDD6FE", "#7C3AED", 2.0)

    if stage == 1:
        # Plush round lilac kitten napping curled on the moon pillow
        curl = (
            f'<ellipse cx="164" cy="196" rx="46" ry="26" fill="{FUR}" stroke="{OL}" stroke-width="6.8"/>'
            f'<path d="M 198,208 C 216,202 220,180 206,174" fill="none" stroke="{OL}" stroke-width="6.4" stroke-linecap="round"/>'
        )
        return moon_pillow + curl + _bsh_lilac_head(134, 184, sc=0.72, tilt=-8, sleepy=True) + sparkle4(212, 134, 12, "#FDE68A", "#9D7AD6", 2.2)

    if stage == 2:
        # Chubby lilac kitten peeking playfully behind a pastel lilac wool yarn ball (with tucked body behind!)
        back_body = (
            f'<path d="M 146,184 C 142,216 148,252 184,256 C 214,258 228,236 222,204 C 218,184 196,174 172,176 Z" '
            f'fill="{FUR}" stroke="{OL}" stroke-width="6.8" stroke-linejoin="round"/>'
            f'<path d="M 218,236 C 244,234 250,204 236,192" fill="none" stroke="{OL}" stroke-width="6.4" stroke-linecap="round"/>'
        )
        paw_on_yarn = f'<ellipse cx="118" cy="202" rx="15" ry="12" fill="{CRM}" stroke="{OL}" stroke-width="5.6"/>'
        return (
            shadow(156, 258, 86, 13)
            + back_body
            + _bsh_lilac_head(168, 146, sc=0.86, tilt=7)
            + _lilac_yarn_ball(120, 222, 38)
            + paw_on_yarn
            + sparkle4(232, 108, 11, "#FDE68A", "#9D7AD6", 2.0)
        )

    if stage == 3:
        # Plush sitting British Shorthair lilac cat with pastel pink neck ribbon & silver star charm!
        tail = f'<path d="M 196,238 C 232,238 242,198 228,178 C 218,166 206,176 212,188 C 220,202 214,220 194,222" fill="{FUR}" stroke="{OL}" stroke-width="6.8" stroke-linecap="round"/>'
        body = (
            shadow(150, 262, 72, 13)
            + tail
            + f'<path d="M 98,176 C 84,210 86,250 116,258 C 136,264 164,264 184,258 C 214,250 216,210 202,176 C 188,158 112,158 98,176 Z" '
              f'fill="{FUR}" stroke="{OL}" stroke-width="7.2" stroke-linejoin="round"/>'
            + f'<ellipse cx="150" cy="222" rx="32" ry="30" fill="{CRM}"/>'
            + _sitting_paws(150, 260, CRM, OL, spread=17, leg_h=22)
        )
        ribbon = (
            f'<path d="M 110,174 C 132,188 168,188 190,174 C 190,184 172,194 150,194 C 128,194 110,184 110,174 Z" '
            f'fill="#F48FB1" stroke="{OL}" stroke-width="5.2" stroke-linejoin="round"/>'
            f'{sparkle4(150, 200, 12, "#F1F5F9", OL, 3.0)}'
        )
        return body + ribbon + _bsh_lilac_head(150, 128, sc=0.92)

    if stage == 4:
        # Happy starry lilac cat perched gracefully on a glowing pastel crescent moon!
        moon = _crescent_moon(150, 178, sc=1.22, rot=-52, fill="#FDE68A", stroke=OL)
        body = (
            f'<path d="M 110,168 C 98,196 102,226 128,232 C 144,236 164,236 180,230 C 202,222 204,192 192,168 Z" '
            f'fill="{FUR}" stroke="{OL}" stroke-width="6.8" stroke-linejoin="round"/>'
            f'<ellipse cx="150" cy="204" rx="28" ry="22" fill="{CRM}"/>'
            f'<ellipse cx="132" cy="226" rx="12" ry="9" fill="{CRM}" stroke="{OL}" stroke-width="5.2"/>'
            f'<ellipse cx="168" cy="226" rx="12" ry="9" fill="{CRM}" stroke="{OL}" stroke-width="5.2"/>'
        )
        ribbon = f'<path d="M 118,166 C 138,178 164,178 184,166 C 184,175 168,184 150,184 C 132,184 118,175 118,166 Z" fill="#F48FB1" stroke="{OL}" stroke-width="4.8"/>'
        stars = sparkle4(62, 86, 13, "#FDE68A", "#9D7AD6", 2.2) + sparkle4(240, 96, 14, "#FDE68A", "#9D7AD6", 2.2) + sparkle4(232, 224, 10, "#DDD6FE", "#7C3AED", 2.0)
        return shadow(150, 266, 78, 12, 0.10) + stars + moon + body + ribbon + _bsh_lilac_head(150, 124, sc=0.86)

    # Stage 5: Magical Lavender Starlight Cat on cloud + crescent moon with cute tilted lavender starry beret & constellation stars — NO CROWN!
    cloud = (
        shadow(150, 268, 92, 12, 0.10)
        + f'<path d="M 76,258 C 56,258 50,236 68,226 C 68,206 94,198 112,210 '
          f'C 126,196 174,196 188,210 C 206,198 232,206 232,226 C 250,236 244,258 224,258 Z" '
          f'fill="#F3E8FF" stroke="{OL}" stroke-width="6.4" stroke-linejoin="round"/>'
    )
    moon = _crescent_moon(152, 174, sc=1.24, rot=-52, fill="#FDE68A", stroke=OL)
    body = (
        f'<path d="M 112,168 C 102,194 106,222 130,228 C 146,232 164,232 178,226 C 200,218 202,190 190,168 Z" '
        f'fill="{FUR}" stroke="{OL}" stroke-width="6.8" stroke-linejoin="round"/>'
        f'<ellipse cx="150" cy="202" rx="26" ry="20" fill="{CRM}"/>'
        f'<ellipse cx="132" cy="222" rx="12" ry="9" fill="{CRM}" stroke="{OL}" stroke-width="5.2"/>'
        f'<ellipse cx="168" cy="222" rx="12" ry="9" fill="{CRM}" stroke="{OL}" stroke-width="5.2"/>'
    )
    ribbon = (
        f'<path d="M 118,166 C 138,178 164,178 184,166 C 184,175 168,184 150,184 C 132,184 118,175 118,166 Z" '
        f'fill="#F48FB1" stroke="{OL}" stroke-width="4.8"/>'
        f'{sparkle4(150, 188, 10, "#F1F5F9", OL, 2.6)}'
    )
    constellation = (
        f'<path d="M 52,78 L 82,58 L 114,68" fill="none" stroke="#C4B5FD" stroke-width="2.6" stroke-dasharray="4 4"/>'
        f'{sparkle4(52, 78, 14, "#FDE68A", "#7C3AED", 2.2)}'
        f'{sparkle4(82, 58, 9, "#DDD6FE", "#7C3AED", 2.0)}'
        f'{sparkle4(244, 72, 15, "#FDE68A", "#7C3AED", 2.2)}'
        f'{sparkle4(250, 158, 11, "#FBCFE8", "#9D7AD6", 2.0)}'
        f'{sparkle4(54, 162, 10, "#DDD6FE", "#7C3AED", 2.0)}'
    )
    return constellation + moon + body + ribbon + _bsh_lilac_head(150, 124, sc=0.86, happy=True, beret=True) + cloud


# =========================================================================== #
#  6. MOCHI CAT (`assets/mochi_cat/`) — ULTRA-SQUISHY JAPANESE MOCHI BLOB CAT (NO NARROW NECK, NO CROWN!)
# =========================================================================== #
def _mikan_orange(cx, cy, sc=1.0) -> str:
    """Cute Japanese mikan (tangerine orange with fresh green leaf) balanced on mochi cat's head!"""
    OL = "#6B4440"
    return (
        f'<g transform="translate({cx},{cy}) scale({sc})">'
        f'<ellipse cx="0" cy="4" rx="22" ry="17" fill="#FF9234" stroke="{OL}" stroke-width="5.2"/>'
        f'<ellipse cx="-6" cy="-1" rx="8" ry="4" fill="#FFD09B" fill-opacity="0.65" transform="rotate(-18,-6,-1)"/>'
        f'<path d="M 0,-12 Q 2,-22 8,-24" fill="none" stroke="{OL}" stroke-width="4.2" stroke-linecap="round"/>'
        f'<path d="M 4,-16 C 14,-28 28,-22 22,-10 C 16,-6 8,-10 4,-16 Z" fill="#63B86E" stroke="{OL}" stroke-width="4.4" stroke-linejoin="round"/>'
        f'</g>'
    )


def _taiyaki_snack(cx, cy, sc=1.0, rot=-12) -> str:
    """Cute golden Japanese taiyaki fish pastry snack!"""
    OL = "#6B4440"
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot}) scale({sc})">'
        f'<path d="M 20,0 L 34,-12 C 38,-4 38,4 34,12 Z" fill="#E39D54" stroke="{OL}" stroke-width="4.4" stroke-linejoin="round"/>'
        f'<ellipse cx="-2" cy="0" rx="24" ry="14" fill="#F0B570" stroke="{OL}" stroke-width="4.6"/>'
        f'<circle cx="-13" cy="-2" r="2.6" fill="{OL}"/>'
        f'<path d="M -2,-8 Q 4,0 -2,8 M 6,-8 Q 12,0 6,8" fill="none" stroke="#C47D34" stroke-width="2.8" stroke-linecap="round"/>'
        f'</g>'
    )


def _mochi_face(cx, cy, sc=1.0, happy_w=True) -> str:
    OL = "#6B4440"
    BLUSH = "#F9A8A8"
    if happy_w:
        eyes = (
            f'<path d="M -30,-4 Q -22,-14 -14,-4" fill="none" stroke="{OL}" stroke-width="5.2" stroke-linecap="round"/>'
            f'<path d="M 14,-4 Q 22,-14 30,-4" fill="none" stroke="{OL}" stroke-width="5.2" stroke-linecap="round"/>'
        )
    else:
        eyes = (
            f'<circle cx="-22" cy="-5" r="5.4" fill="{OL}"/>'
            f'<circle cx="-24" cy="-7" r="2" fill="#FFFFFF"/>'
            f'<circle cx="22" cy="-5" r="5.4" fill="{OL}"/>'
            f'<circle cx="20" cy="-7" r="2" fill="#FFFFFF"/>'
        )
    return (
        f'<g transform="translate({cx},{cy}) scale({sc})">'
        f'<ellipse cx="-38" cy="8" rx="11" ry="6.2" fill="{BLUSH}" fill-opacity="0.72"/>'
        f'<ellipse cx="38" cy="8" rx="11" ry="6.2" fill="{BLUSH}" fill-opacity="0.72"/>'
        f'{eyes}'
        f'<path d="M -10,8 Q -5,15 0,8 Q 5,15 10,8" fill="none" stroke="{OL}" stroke-width="4.2" stroke-linecap="round"/>'
        f'<path d="M -48,4 L -64,2 M -48,12 L -64,14 M 48,4 L 64,2 M 48,12 L 64,14" stroke="{OL}" stroke-width="3" stroke-linecap="round" stroke-opacity="0.65"/>'
        f'</g>'
    )


def _orange_parcel_box(cx=150, cy=212, closed=True) -> str:
    OL = "#6B4440"
    BOX = "#F4A462"
    BOX_LT = "#FBC08B"
    if closed:
        return (
            shadow(cx, cy + 48, 80, 13, 0.12)
            + f'<rect x="{cx - 72}" y="{cy - 34}" width="144" height="84" rx="10" fill="{BOX}" stroke="{OL}" stroke-width="6.8"/>'
            + f'<rect x="{cx - 78}" y="{cy - 44}" width="156" height="22" rx="8" fill="{BOX_LT}" stroke="{OL}" stroke-width="6.6"/>'
            + f'<rect x="{cx - 16}" y="{cy - 44}" width="32" height="44" rx="4" fill="#FFF3DF" stroke="{OL}" stroke-width="4.4"/>'
            + paw_print(cx + 38, cy + 20, 0.65, "#E07A5F")
        )
    return (
        f'<path d="M {cx - 72},{cy - 32} L {cx - 94},{cy - 50} L {cx - 78},{cy - 62} L {cx - 56},{cy - 36} Z" fill="{BOX_LT}" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>'
        f'<path d="M {cx + 72},{cy - 32} L {cx + 94},{cy - 50} L {cx + 78},{cy - 62} L {cx + 56},{cy - 36} Z" fill="{BOX_LT}" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>'
        f'<rect x="{cx - 72}" y="{cy - 34}" width="144" height="84" rx="10" fill="{BOX}" stroke="{OL}" stroke-width="6.8"/>'
        f'<rect x="{cx - 14}" y="{cy - 34}" width="28" height="24" rx="3" fill="#FFF3DF" stroke="{OL}" stroke-width="4.2"/>'
        f'{paw_print(cx + 38, cy + 20, 0.65, "#E07A5F")}'
    )


def draw_mochi_cat(stage: int) -> str:
    OL = "#6B4440"
    WHT = "#FFFDFB"
    SHD = "#FDE6D8"

    if stage == 0:
        return _orange_parcel_box(150, 212, closed=True)

    if stage == 1:
        # Two tiny white cat ears & rosy forehead peeking out from open orange box flaps!
        box_bg = shadow(150, 260, 80, 13, 0.12) + f'<rect x="78" y="176" width="144" height="84" rx="10" fill="#DC8641" stroke="{OL}" stroke-width="6.8"/>'
        peek = (
            f'<path d="M 102,178 C 102,144 198,144 198,178 Z" fill="{WHT}" stroke="{OL}" stroke-width="6.8"/>'
            f'<path d="M 110,162 L 106,128 C 106,122 114,122 118,126 L 136,150 Z" fill="{WHT}" stroke="{OL}" stroke-width="6.4" stroke-linejoin="round"/>'
            f'<path d="M 114,154 L 112,135 L 128,150 Z" fill="#FBC5C5"/>'
            f'<path d="M 190,162 L 194,128 C 194,122 186,122 182,126 L 164,150 Z" fill="{WHT}" stroke="{OL}" stroke-width="6.4" stroke-linejoin="round"/>'
            f'<path d="M 186,154 L 188,135 L 172,150 Z" fill="#FBC5C5"/>'
            f'<ellipse cx="126" cy="172" rx="8" ry="4.5" fill="#F9A8A8" fill-opacity="0.7"/>'
            f'<ellipse cx="174" cy="172" rx="8" ry="4.5" fill="#F9A8A8" fill-opacity="0.7"/>'
        )
        return box_bg + peek + _orange_parcel_box(150, 212, closed=False)

    if stage == 2:
        # Squishy white mochi cat resting chubby paws on the orange box rim, smiling ^w^!
        box_bg = shadow(150, 260, 80, 13, 0.12) + f'<rect x="78" y="176" width="144" height="84" rx="10" fill="#DC8641" stroke="{OL}" stroke-width="6.8"/>'
        mochi_top = (
            f'<path d="M 100,144 L 94,104 C 94,98 104,96 110,102 L 132,124 Z" fill="{WHT}" stroke="{OL}" stroke-width="6.6" stroke-linejoin="round"/>'
            f'<path d="M 104,134 L 102,112 L 122,126 Z" fill="#FBC5C5"/>'
            f'<path d="M 200,144 L 206,104 C 206,98 196,96 190,102 L 168,124 Z" fill="{WHT}" stroke="{OL}" stroke-width="6.6" stroke-linejoin="round"/>'
            f'<path d="M 196,134 L 198,112 L 178,126 Z" fill="#FBC5C5"/>'
            f'<path d="M 90,188 C 86,144 114,118 150,118 C 186,118 214,144 210,188 Z" fill="{WHT}" stroke="{OL}" stroke-width="7"/>'
        )
        paws = (
            f'<ellipse cx="116" cy="180" rx="16" ry="12" fill="{WHT}" stroke="{OL}" stroke-width="5.8"/>'
            f'<ellipse cx="184" cy="180" rx="16" ry="12" fill="{WHT}" stroke="{OL}" stroke-width="5.8"/>'
        )
        return box_bg + mochi_top + _mochi_face(150, 156, sc=0.86, happy_w=True) + _orange_parcel_box(150, 212, closed=False) + paws

    if stage == 3:
        # Ultra-squishy dumpling-shaped white mochi cat loafing cozily right beside a mini orange box!
        mini_box = (
            f'<rect x="196" y="212" width="60" height="44" rx="7" fill="#F4A462" stroke="{OL}" stroke-width="5.6"/>'
            f'<rect x="192" y="206" width="68" height="14" rx="5" fill="#FBC08B" stroke="{OL}" stroke-width="5.2"/>'
            f'<rect x="219" y="206" width="14" height="22" fill="#FFF3DF" stroke="{OL}" stroke-width="3.2"/>'
        )
        loaf = (
            shadow(136, 260, 84, 13)
            # Tiny tucked mochi tail
            + f'<path d="M 76,238 C 52,238 48,210 64,204 C 74,200 78,212 72,220" fill="{WHT}" stroke="{OL}" stroke-width="6.4" stroke-linecap="round"/>'
            # Stubby ears on top of ONE continuous squishy daifuku dumpling silhouette (ZERO narrow neck!)
            + f'<path d="M 94,158 L 88,122 C 88,116 98,114 104,120 L 122,140 Z" fill="{WHT}" stroke="{OL}" stroke-width="6.6" stroke-linejoin="round"/>'
            + f'<path d="M 98,148 L 96,129 L 114,142 Z" fill="#FBC5C5"/>'
            + f'<path d="M 178,158 L 184,122 C 184,116 174,114 168,120 L 150,140 Z" fill="{WHT}" stroke="{OL}" stroke-width="6.6" stroke-linejoin="round"/>'
            + f'<path d="M 174,148 L 176,129 L 158,142 Z" fill="#FBC5C5"/>'
            + f'<path d="M 136,134 C 178,134 212,166 214,218 C 216,252 186,260 136,260 '
              f'C 86,260 56,252 58,218 C 60,166 94,134 136,134 Z" fill="{WHT}" stroke="{OL}" stroke-width="7.2" stroke-linejoin="round"/>'
            + f'<path d="M 68,236 C 92,256 180,256 204,236 C 194,252 168,256 136,256 C 104,256 78,252 68,236 Z" fill="{SHD}"/>'
            # Stubby tucked loaf paws
            + f'<ellipse cx="114" cy="244" rx="14" ry="9" fill="{WHT}" stroke="{OL}" stroke-width="5.2"/>'
            + f'<ellipse cx="158" cy="244" rx="14" ry="9" fill="{WHT}" stroke="{OL}" stroke-width="5.2"/>'
        )
        return mini_box + loaf + _mochi_face(136, 194, sc=0.92, happy_w=False)

    if stage == 4:
        # Happy squishy mochi dumpling cat balancing a cute Japanese MIKAN tangerine on its head!
        blob = (
            shadow(150, 264, 82, 13)
            + f'<path d="M 218,240 C 246,238 252,202 234,192 C 224,186 216,198 224,208 C 230,216 226,226 216,228" fill="{WHT}" stroke="{OL}" stroke-width="6.6" stroke-linecap="round"/>'
            + f'<path d="M 102,134 L 94,94 C 94,88 104,86 112,92 L 132,114 Z" fill="{WHT}" stroke="{OL}" stroke-width="6.8" stroke-linejoin="round"/>'
            + f'<path d="M 106,124 L 103,102 L 124,116 Z" fill="#FBC5C5"/>'
            + f'<path d="M 198,134 L 206,94 C 206,88 196,86 188,92 L 168,114 Z" fill="{WHT}" stroke="{OL}" stroke-width="6.8" stroke-linejoin="round"/>'
            + f'<path d="M 194,124 L 197,102 L 176,116 Z" fill="#FBC5C5"/>'
            # ONE continuous super-squishy daifuku mochi blob (ZERO narrow neck!)
            + f'<path d="M 150,108 C 194,108 226,144 228,208 C 230,252 198,262 150,262 '
              f'C 102,262 70,252 72,208 C 74,144 106,108 150,108 Z" fill="{WHT}" stroke="{OL}" stroke-width="7.4" stroke-linejoin="round"/>'
            + f'<path d="M 80,236 C 108,258 192,258 220,236 C 210,254 184,258 150,258 C 116,258 90,254 80,236 Z" fill="{SHD}"/>'
            # Cute stubby mochi nubbin paws tucked neatly at bottom
            + f'<ellipse cx="122" cy="242" rx="13" ry="8.5" fill="{WHT}" stroke="{OL}" stroke-width="5"/>'
            + f'<ellipse cx="178" cy="242" rx="13" ry="8.5" fill="{WHT}" stroke="{OL}" stroke-width="5"/>'
        )
        return blob + _mochi_face(150, 174, sc=0.96, happy_w=True) + _mikan_orange(150, 96, sc=1.02) + sparkle4(66, 98, 12, "#FCD34D", "#C87A20", 2.2)

    # Stage 5: Blissful Fluffy White Mochi Cat with mikan tangerine on head, taiyaki fish snack & warm floating peach hearts — NO CROWN!
    blob = (
        shadow(150, 266, 86, 14)
        + f'<path d="M 220,242 C 250,240 256,202 238,190 C 228,184 220,196 228,206 C 234,216 228,226 218,228" fill="{WHT}" stroke="{OL}" stroke-width="6.6" stroke-linecap="round"/>'
        + f'<path d="M 100,136 L 92,94 C 92,88 102,86 110,92 L 132,116 Z" fill="{WHT}" stroke="{OL}" stroke-width="6.8" stroke-linejoin="round"/>'
        + f'<path d="M 104,126 L 101,102 L 122,118 Z" fill="#FBC5C5"/>'
        + f'<path d="M 200,136 L 208,94 C 208,88 198,86 190,92 L 168,116 Z" fill="{WHT}" stroke="{OL}" stroke-width="6.8" stroke-linejoin="round"/>'
        + f'<path d="M 196,126 L 199,102 L 178,118 Z" fill="#FBC5C5"/>'
        + f'<path d="M 150,110 C 196,110 228,146 230,210 C 232,254 200,264 150,264 '
          f'C 100,264 68,254 70,210 C 72,146 104,110 150,110 Z" fill="{WHT}" stroke="{OL}" stroke-width="7.4" stroke-linejoin="round"/>'
        + f'<path d="M 78,238 C 108,260 192,260 222,238 C 212,256 184,260 150,260 C 116,260 88,256 78,238 Z" fill="{SHD}"/>'
        + f'<ellipse cx="112" cy="236" rx="13" ry="8.5" fill="{WHT}" stroke="{OL}" stroke-width="5"/>'
        + f'<ellipse cx="188" cy="236" rx="13" ry="8.5" fill="{WHT}" stroke="{OL}" stroke-width="5"/>'
    )
    deco = (
        heart(56, 86, 15, "#F69393", OL, 2.8, -16)
        + heart(244, 82, 16, "#F69393", OL, 2.8, 16)
        + heart(248, 158, 10, "#FBB6A8", OL, 2.4, 12)
        + sparkle4(56, 164, 12, "#FCD34D", "#C87A20", 2.2)
    )
    return (
        deco
        + blob
        + _mochi_face(150, 174, sc=0.98, happy_w=True)
        + _mikan_orange(150, 96, sc=1.06)
        + _taiyaki_snack(150, 240, sc=0.96, rot=-8)
    )


# =========================================================================== #
#  MASTER GENERATOR + DUAL-SCALE CONTACT SHEET (LARGE 180px + ACTUAL 44px EXCEL!)
# =========================================================================== #
PET_SPECS = [
    ("shiba_inu",      "30. Shiba Inu (Dog — Karakusa Bandana + Bone, NO Crown)", draw_shiba_inu),
    ("akita_inu",      "31. Akita Inu (Snow Bear Dog — Shimenawa + Snowflakes)",  draw_akita_inu),
    ("ginger_kitten",  "25. Ginger Kitten (Wicker Basket -> Loaf -> Mint Yarn)",  draw_ginger_kitten),
    ("royal_cat_cash", "24. Royal Cat Cash (EXCLUSIVE Golden Crown Owner!)",      draw_royal_cat_cash),
    ("purple_cat",     "26. Purple Starlight Cat (BSH — Moon + Starry Beret)",    draw_purple_cat),
    ("mochi_cat",      "33. Peach Mochi Cat (Squishy Blob — Box + Mikan + Taiyaki)", draw_mochi_cat),
]


def _font(size: int, bold: bool = False):
    for name in ("segoeuib.ttf" if bold else "segoeui.ttf", "arialbd.ttf" if bold else "arial.ttf"):
        p = Path("C:/Windows/Fonts") / name
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def build_dual_contact_sheet(all_imgs: dict[str, list[Image.Image]], out_path: Path):
    """Render BOTH large (180px) AND actual 44px Excel cell size side-by-side for visual QA!"""
    big_sz = 176
    cell_w = 184
    mini_sz = 44
    mini_gap = 50
    left_pad = 24
    right_panel_x = left_pad + 6 * cell_w + 32
    W = right_panel_x + 6 * mini_gap + 28
    row_h = 224
    top_pad = 64
    H = top_pad + len(PET_SPECS) * row_h + 24

    canvas = Image.new("RGB", (W, H), (252, 250, 248))
    draw = ImageDraw.Draw(canvas)
    f_title = _font(22, bold=True)
    f_lbl = _font(15, bold=True)
    f_sub = _font(12, bold=False)

    draw.text((left_pad, 18), "PETS SPRITE OVERHAUL — LARGE (176px) + ACTUAL EXCEL CELL SIZE (44px)", fill=(58, 42, 36), font=f_title)
    draw.text((right_panel_x, 42), "Actual 44px Excel Cell Preview (Stage 0 -> 5):", fill=(110, 88, 78), font=f_sub)

    for r, (slug, title, _) in enumerate(PET_SPECS):
        y0 = top_pad + r * row_h
        draw.line([(left_pad, y0 - 4), (W - 20, y0 - 4)], fill=(230, 222, 215), width=1)
        draw.text((left_pad, y0 + 2), title, fill=(74, 50, 40), font=f_lbl)

        imgs = all_imgs[slug]
        for s_idx, im in enumerate(imgs):
            # Large tile
            lx = left_pad + s_idx * cell_w
            ly = y0 + 26
            draw.rounded_rectangle([lx, ly, lx + big_sz, ly + big_sz], radius=10, fill=(255, 255, 255), outline=(235, 228, 222))
            big_im = im.resize((big_sz - 6, big_sz - 6), Image.LANCZOS)
            canvas.paste(big_im, (lx + 3, ly + 3), big_im)
            draw.text((lx + 6, ly + big_sz - 16), f"S{s_idx}", fill=(140, 125, 118), font=f_sub)

            # Actual 44px Excel tile
            mx = right_panel_x + s_idx * mini_gap
            my = y0 + 88
            draw.rounded_rectangle([mx, my, mx + mini_sz, my + mini_sz], radius=4, fill=(255, 255, 255), outline=(224, 215, 208))
            mini_im = im.resize((mini_sz - 2, mini_sz - 2), Image.LANCZOS)
            canvas.paste(mini_im, (mx + 1, my + 1), mini_im)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, optimize=True)


def main():
    all_imgs: dict[str, list[Image.Image]] = {}
    for slug, title, fn in PET_SPECS:
        imgs = []
        for s in range(6):
            svg = fn(s)
            out_p = ASSETS_DIR / slug / f"stage_{s}.png"
            im = render_svg_to_png(svg, out_p, size=300)
            imgs.append(im)
        all_imgs[slug] = imgs
        print(f"  ✓ Rendered 6 high-DPI vector sprites -> assets/{slug}/stage_0..5.png", flush=True)

    cs_path = PREVIEWS_DIR / "assets_contact_sheet_pets_overhaul.png"
    build_dual_contact_sheet(all_imgs, cs_path)
    print(f"  ✓ Saved dual-scale contact sheet -> {cs_path}", flush=True)


if __name__ == "__main__":
    main()
