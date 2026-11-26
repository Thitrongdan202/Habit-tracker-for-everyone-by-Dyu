"""
generate_loopy_story_assets.py — v4.0 Dynamic Anti-Stiffness Overhaul for 10 Loopy Themes (#61–#70)
Generates 60 expressive, dynamically posed 300x300 transparent RGBA PNG sprites + contact sheet:
  - assets/loopy_red_bow/stage_0..5.png          (#61 Loopy Red Bow Glow-Up — meme tilt + red bow + flower, NO beret!)
  - assets/loopy_taiyaki/stage_0..5.png          (#62 Loopy Taiyaki Street Snack — varied lean/sit/nibble/cheer poses!)
  - assets/loopy_piggy_cafe/stage_0..5.png       (#63 Loopy Piggy Dessert Cafe — varied cozy cafe poses!)
  - assets/loopy_sauna_sheep/stage_0..5.png      (#64 Loopy Sauna Sheep Detox — slouch/towel/lean/WA~/jump!)
  - assets/loopy_honey_bee/stage_0..5.png        (#65 Loopy Honey Bee KPI — curled/sprout/flutter/honey pot/Queen Bee!)
  - assets/loopy_poolside_duck/stage_0..5.png    (#66 Loopy Poolside Duck Chill — shy/hop/splash/float/lounge!)
  - assets/loopy_fluffy_commuter/stage_0..5.png  (#67 Loopy Fluffy Commuter Diary — sleepy/strap/stride/coffee/shrug/jump!)
  - assets/loopy_panda_study/stage_0..5.png      (#68 Loopy Panda Zen Study — scratch head/bulb/write/read/checklist/zen!)
  - assets/loopy_ruffle_sleep/stage_0..5.png     (#69 Loopy Ruffle Sleep Routine — sitting/curtain/pillow/curl/bubble/Zzz!)
  - assets/loopy_hair_roller/stage_0..5.png      (#70 NEW! Loopy Hair Roller GRWM — black hair + big pink roller meme!)
  - previews/assets_contact_sheet_loopy.png      (10-row x 6-stage visual contact sheet)

Character Bible (100% Pure Loopy — ZERO similarity to Lotso!):
  - Pear-shaped soft pastel-pink beaver (#FFA8BC), small round cream-rimmed ears, rounded crimson-berry
    triangle nose (#A83340), ICONIC SINGLE WHITE BUCKTOOTH, soft rosy round cheeks, cute tiny berry paws.
  - Anti-Stiffness Mandate: Every stage uses distinct head tilt, body posture (sit/lean/walk/fly/jump/curl),
    arm/leg motion & real prop interaction!
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

OL = "#5C343A"
PINK = "#FFA8BC"
PINK_LT = "#FFC8D6"
CREAM = "#FFF8F0"
NOSE = "#A83340"
NOSE_HI = "#D96673"
MOUTH = "#D64C5E"
PAW = "#C94A6A"
EYE = "#2B181A"


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


def with_hero_aura(im: Image.Image, rgb: tuple[int, int, int], cy: int = 152, alpha: int = 66) -> Image.Image:
    aura = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
    ad = ImageDraw.Draw(aura)
    r, g, b = rgb
    ad.ellipse([36, cy - 110, 264, cy + 110], fill=(r, g, b, alpha))
    ad.ellipse([72, cy - 76, 228, cy + 76], fill=(255, 251, 224, 92))
    aura = aura.filter(ImageFilter.GaussianBlur(radius=22))
    return Image.alpha_composite(aura, im)


# =========================================================================== #
#  REUSABLE VECTOR DECORATIONS
# =========================================================================== #
def shadow(cx=150, cy=268, rx=64, ry=9.5, op=0.14) -> str:
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{OL}" fill-opacity="{op}"/>'


def soft_blush(cx: float, cy: float, rx: float, ry: float, strong: bool = False) -> str:
    if strong:
        return (
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx:.1f}" ry="{ry:.1f}" fill="#F26382" fill-opacity="0.30"/>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx * 0.68:.1f}" ry="{ry * 0.68:.1f}" fill="#EC4B70" fill-opacity="0.38"/>'
        )
    return (
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx:.1f}" ry="{ry:.1f}" fill="#F57A95" fill-opacity="0.25"/>'
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx * 0.66:.1f}" ry="{ry * 0.66:.1f}" fill="#F26382" fill-opacity="0.32"/>'
    )


def sp4(cx, cy, r=11, fill="#FDE047", stroke="#D97706", sw=2.2) -> str:
    ir = r * 0.28
    d = (
        f"M {cx},{cy - r} Q {cx + ir},{cy - ir} {cx + r},{cy} "
        f"Q {cx + ir},{cy + ir} {cx},{cy + r} "
        f"Q {cx - ir},{cy + ir} {cx - r},{cy} "
        f"Q {cx - ir},{cy - ir} {cx},{cy - r} Z"
    )
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>'


def star5(cx, cy, r=13, fill="#FDE047", stroke="#D97706", sw=2.0, rot=0) -> str:
    pts = []
    for i in range(10):
        ang = math.radians(rot - 90 + i * 36)
        rad = r if i % 2 == 0 else r * 0.45
        pts.append(f"{cx + math.cos(ang) * rad:.1f},{cy + math.sin(ang) * rad:.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>'


def heart(cx, cy, s=13, fill="#FB7185", stroke=OL, sw=2.3, rot=0) -> str:
    d = (
        f"M 0,{s * 0.72} "
        f"C {-s * 1.1},{s * 0.05} {-s * 1.05},{-s * 0.85} {-s * 0.42},{-s * 0.85} "
        f"C {-s * 0.12},{-s * 0.85} 0,{-s * 0.52} 0,{-s * 0.38} "
        f"C 0,{-s * 0.52} {s * 0.12},{-s * 0.85} {s * 0.42},{-s * 0.85} "
        f"C {s * 1.05},{-s * 0.85} {s * 1.1},{s * 0.05} 0,{s * 0.72} Z"
    )
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot})">'
        f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>'
        f'</g>'
    )


def heart_with_eyes(cx, cy, s=21, rot=-12) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot})">'
        f'{heart(0, 0, s=s, fill="#F888A8", stroke="#D85B80", sw=2.5)}'
        f'<ellipse cx="-5.5" cy="-2" rx="4.2" ry="4.8" fill="#FFFFFF"/>'
        f'<ellipse cx="5.5" cy="-2" rx="4.2" ry="4.8" fill="#FFFFFF"/>'
        f'<circle cx="-4.5" cy="-1.5" r="2.3" fill="{EYE}"/><circle cx="6.5" cy="-1.5" r="2.3" fill="{EYE}"/>'
        f'</g>'
    )


def excl_marks(x, y, rot=-14, s=1.0) -> str:
    return (
        f'<g transform="translate({x},{y}) rotate({rot}) scale({s})">'
        f'<path d="M -8,-28 C -12,-14 -7,0 -4,2 C -1,0 1,-15 -4,-28 Z" fill="#FDE047" stroke="#EAB308" stroke-width="1.8" stroke-linejoin="round"/>'
        f'<circle cx="-4" cy="10" r="3.6" fill="#FDE047" stroke="#EAB308" stroke-width="1.6"/>'
        f'<path d="M 8,-33 C 4,-16 8,-2 11,0 C 14,-2 17,-17 12,-33 Z" fill="#FDE047" stroke="#EAB308" stroke-width="1.8" stroke-linejoin="round"/>'
        f'<circle cx="11" cy="9" r="3.6" fill="#FDE047" stroke="#EAB308" stroke-width="1.6"/>'
        f'</g>'
    )


def ditsy_flower(cx, cy, r=7, petal="#F26868", center="#FDE047") -> str:
    pts = []
    for k in range(5):
        a = math.radians(k * 72 - 90)
        pts.append(f'<circle cx="{cx + math.cos(a) * r * 0.78:.1f}" cy="{cy + math.sin(a) * r * 0.78:.1f}" r="{r * 0.42:.1f}" fill="{petal}"/>')
    pts.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.38:.1f}" fill="{center}"/>')
    return "".join(pts)


def _z_vec(x, y, s=1.0) -> str:
    return (
        f'<path d="M {x},{y} L {x + 14 * s},{y} L {x},{y + 16 * s} L {x + 14 * s},{y + 16 * s}" '
        f'fill="none" stroke="{OL}" stroke-width="{3.2 * s:.1f}" stroke-linecap="round" stroke-linejoin="round"/>'
    )


# =========================================================================== #
#  DYNAMIC LOOPY RIG (MULTI-POSE BODY + EXPRESSIVE TILTED HEAD!)
# =========================================================================== #
def loopy_ears(cx=0, cy=0, spread=45, y_off=-51) -> str:
    parts = []
    for side in (-1, 1):
        ex = cx + side * spread
        ey = cy + y_off
        parts.append(
            f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="15.5" fill="{PINK}" stroke="{OL}" stroke-width="4.0"/>'
            f'<circle cx="{ex - side * 1.4:.1f}" cy="{ey + 1.4:.1f}" r="8.0" fill="{CREAM}" stroke="{OL}" stroke-width="2.1"/>'
        )
    return "".join(parts)


def loopy_hair_tuft(cx=0, top_y=-61, s=0.95, rot=0) -> str:
    return (
        f'<g transform="translate({cx},{top_y}) rotate({rot}) scale({s})">'
        f'<path d="M 0,4 C -6,-8 -14,-18 -6,-21 C 0,-23 3,-11 1,2 Z" fill="{PINK}" stroke="{OL}" stroke-width="3.5" stroke-linejoin="round"/>'
        f'<path d="M 1,4 C 2,-10 7,-25 14,-22 C 20,-19 11,-4 3,4 Z" fill="{PINK}" stroke="{OL}" stroke-width="3.5" stroke-linejoin="round"/>'
        f'</g>'
    )


def loopy_body(
    cx=150,
    cy=216,
    rx=50,
    ry=45,
    pose="stand",
    paws="down",
    lean=0,
    coat=PINK,
    belly=True,
) -> str:
    """Dynamic multi-pose Loopy body: stand, sit, jump, walk, lean, hover, slouch!"""
    parts = [f'<g transform="translate({cx},{cy}) rotate({lean})">']
    # Feet by pose
    if pose == "sit":
        parts.append(
            f'<ellipse cx="-35" cy="34" rx="21" ry="17" transform="rotate(-16 -35 34)" fill="{PAW}" stroke="{OL}" stroke-width="3.6"/>'
            f'<ellipse cx="-35" cy="36" rx="10" ry="7.5" transform="rotate(-16 -35 36)" fill="#F08AA4"/>'
            f'<ellipse cx="35" cy="34" rx="21" ry="17" transform="rotate(16 35 34)" fill="{PAW}" stroke="{OL}" stroke-width="3.6"/>'
            f'<ellipse cx="35" cy="36" rx="10" ry="7.5" transform="rotate(16 35 36)" fill="#F08AA4"/>'
        )
    elif pose == "jump":
        parts.append(
            f'<ellipse cx="-30" cy="40" rx="19" ry="11" transform="rotate(-26 -30 40)" fill="{PAW}" stroke="{OL}" stroke-width="3.6"/>'
            f'<ellipse cx="30" cy="40" rx="19" ry="11" transform="rotate(26 30 40)" fill="{PAW}" stroke="{OL}" stroke-width="3.6"/>'
        )
    elif pose == "walk":
        parts.append(
            f'<ellipse cx="-28" cy="44" rx="19" ry="11" transform="rotate(-12 -28 44)" fill="{PAW}" stroke="{OL}" stroke-width="3.6"/>'
            f'<ellipse cx="26" cy="36" rx="19" ry="11" transform="rotate(22 26 36)" fill="{PAW}" stroke="{OL}" stroke-width="3.6"/>'
        )
    elif pose == "hover":
        parts.append(
            f'<ellipse cx="-18" cy="42" rx="16" ry="10" transform="rotate(14 -18 42)" fill="{PAW}" stroke="{OL}" stroke-width="3.6"/>'
            f'<ellipse cx="18" cy="42" rx="16" ry="10" transform="rotate(-14 18 42)" fill="{PAW}" stroke="{OL}" stroke-width="3.6"/>'
        )
    elif pose == "none_feet":
        pass
    else:  # stand / slouch
        parts.append(
            f'<ellipse cx="-23" cy="42" rx="18" ry="10.5" fill="{PAW}" stroke="{OL}" stroke-width="3.6"/>'
            f'<ellipse cx="23" cy="42" rx="18" ry="10.5" fill="{PAW}" stroke="{OL}" stroke-width="3.6"/>'
        )

    # Plump pear torso tucked smoothly behind chin (-44)
    parts.append(
        f'<path d="M {-rx + 10},-44 '
        f'C {-rx - 6},6 {-rx + 10},{ry} 0,{ry} '
        f'C {rx - 10},{ry} {rx + 6},6 {rx - 10},-44 Z" '
        f'fill="{coat}" stroke="{OL}" stroke-width="4.0" stroke-linejoin="round"/>'
    )
    if belly:
        parts.append(f'<ellipse cx="0" cy="12" rx="{rx * 0.56:.1f}" ry="{ry * 0.66:.1f}" fill="{CREAM}"/>')

    # Expressive arm/paw poses
    if paws == "down":
        parts.append(
            f'<path d="M {-rx + 8},-18 C {-rx - 16},-2 {-rx - 10},18 {-rx + 6},14" fill="{coat}" stroke="{OL}" stroke-width="3.8" stroke-linecap="round"/>'
            f'<path d="M {rx - 8},-18 C {rx + 16},-2 {rx + 10},18 {rx - 6},14" fill="{coat}" stroke="{OL}" stroke-width="3.8" stroke-linecap="round"/>'
        )
    elif paws == "wide_up":
        parts.append(
            f'<path d="M {-rx + 10},-16 C {-rx - 24},-32 {-rx - 16},-56 {-rx + 4},-36" fill="{coat}" stroke="{OL}" stroke-width="3.8" stroke-linecap="round"/>'
            f'<path d="M {rx - 10},-16 C {rx + 24},-32 {rx + 16},-56 {rx - 4},-36" fill="{coat}" stroke="{OL}" stroke-width="3.8" stroke-linecap="round"/>'
        )
    elif paws == "wave_r":
        parts.append(
            f'<path d="M {-rx + 8},-16 C {-rx - 16},0 {-rx - 10},18 {-rx + 6},14" fill="{coat}" stroke="{OL}" stroke-width="3.8" stroke-linecap="round"/>'
            f'<path d="M {rx - 10},-16 C {rx + 24},-34 {rx + 18},-56 {rx - 2},-36" fill="{coat}" stroke="{OL}" stroke-width="3.8" stroke-linecap="round"/>'
        )
    elif paws == "walk_swing":
        parts.append(
            f'<path d="M {-rx + 8},-16 C {-rx - 20},-6 {-rx - 16},14 {-rx + 4},10" fill="{coat}" stroke="{OL}" stroke-width="3.8" stroke-linecap="round"/>'
            f'<path d="M {rx - 8},-14 C {rx + 20},-24 {rx + 18},-4 {rx - 4},6" fill="{coat}" stroke="{OL}" stroke-width="3.8" stroke-linecap="round"/>'
        )
    elif paws == "shrug":
        parts.append(
            f'<path d="M {-rx + 8},-18 C {-rx - 22},-18 {-rx - 22},-36 {-rx - 6},-32" fill="{coat}" stroke="{OL}" stroke-width="3.8" stroke-linecap="round"/>'
            f'<path d="M {rx - 8},-18 C {rx + 22},-18 {rx + 22},-36 {rx + 6},-32" fill="{coat}" stroke="{OL}" stroke-width="3.8" stroke-linecap="round"/>'
        )
    elif paws == "center":
        parts.append(
            f'<ellipse cx="-24" cy="-8" rx="16" ry="11" transform="rotate(18 -24 -8)" fill="{coat}" stroke="{OL}" stroke-width="3.6"/>'
            f'<ellipse cx="24" cy="-8" rx="16" ry="11" transform="rotate(-18 24 -8)" fill="{coat}" stroke="{OL}" stroke-width="3.6"/>'
        )
    elif paws == "panic_flail":
        parts.append(
            f'<path d="M {-rx + 8},-18 C {-rx - 24},-22 {-rx - 24},0 {-rx - 4},6" fill="{coat}" stroke="{OL}" stroke-width="3.8" stroke-linecap="round"/>'
            f'<path d="M {rx - 8},-18 C {rx + 24},-10 {rx + 20},14 {rx - 4},12" fill="{coat}" stroke="{OL}" stroke-width="3.8" stroke-linecap="round"/>'
        )
    elif paws == "none":
        pass

    parts.append("</g>")
    return "".join(parts)


def loopy_head(
    cx=150,
    cy=128,
    scale=1.0,
    expr="smile",
    strong_blush=False,
    show_ears=True,
    show_tuft=True,
    head_outline=True,
    blush_hatch=False,
    rot=0,
) -> str:
    """Signature pear-cheeked Loopy head + expressive meme face + single iconic white bucktooth!"""
    parts = [f'<g transform="translate({cx},{cy}) rotate({rot}) scale({scale})">']
    if show_ears:
        parts.append(loopy_ears(0, 0))
    if show_tuft:
        parts.append(loopy_hair_tuft(0, -61))

    sw = "4.0" if head_outline else "0"
    head_d = (
        "M -55,-14 C -57,-48 -31,-63 0,-63 C 31,-63 57,-48 55,-14 "
        "C 65,4 62,34 41,47 C 25,56 -25,56 -41,47 C -62,34 -65,4 -55,-14 Z"
    )
    parts.append(f'<path d="{head_d}" fill="{PINK}" stroke="{OL}" stroke-width="{sw}" stroke-linejoin="round"/>')
    parts.append(soft_blush(-37, 14, 20, 14, strong=strong_blush))
    parts.append(soft_blush(37, 14, 20, 14, strong=strong_blush))
    if blush_hatch:
        parts.append(
            '<line x1="-42" y1="15" x2="-39" y2="11" stroke="#FFFFFF" stroke-width="2.1" stroke-linecap="round"/>'
            '<line x1="-35" y1="16" x2="-32" y2="12" stroke="#FFFFFF" stroke-width="2.1" stroke-linecap="round"/>'
            '<line x1="32" y1="12" x2="35" y2="16" stroke="#FFFFFF" stroke-width="2.1" stroke-linecap="round"/>'
            '<line x1="39" y1="11" x2="42" y2="15" stroke="#FFFFFF" stroke-width="2.1" stroke-linecap="round"/>'
        )

    # Eyes
    if expr in ("smile", "big_smile", "curious", "focused", "puzzled", "proud", "nibble", "meme_scream"):
        rx_e, ry_e = (8.2, 9.2) if expr == "meme_scream" else (7.0, 8.0)
        parts.append(
            f'<ellipse cx="-23" cy="-7" rx="{rx_e}" ry="{ry_e}" fill="{EYE}"/>'
            f'<circle cx="-25.5" cy="-10" r="2.7" fill="#FFFFFF"/>'
            f'<ellipse cx="23" cy="-7" rx="{rx_e}" ry="{ry_e}" fill="{EYE}"/>'
            f'<circle cx="20.5" cy="-10" r="2.7" fill="#FFFFFF"/>'
        )
        if expr == "focused":
            parts.append(
                f'<path d="M -31,-19 L -15,-15" stroke="{OL}" stroke-width="2.8" stroke-linecap="round"/>'
                f'<path d="M 31,-19 L 15,-15" stroke="{OL}" stroke-width="2.8" stroke-linecap="round"/>'
            )
        elif expr == "puzzled":
            parts.append(
                f'<path d="M -30,-20 Q -23,-24 -16,-19" fill="none" stroke="{OL}" stroke-width="2.5" stroke-linecap="round"/>'
                f'<path d="M 16,-18 Q 23,-22 30,-20" fill="none" stroke="{OL}" stroke-width="2.5" stroke-linecap="round"/>'
            )
    elif expr == "deadpan":
        # Iconic half-lidded meme Loopy eyes (for #70 Hair Roller 0%!)
        parts.append(
            f'<ellipse cx="-23" cy="-4" rx="7.2" ry="6.2" fill="{EYE}"/>'
            f'<rect x="-32" y="-14" width="18" height="9" fill="{PINK}"/>'
            f'<path d="M -31,-5 Q -23,-7 -15,-5" fill="none" stroke="{OL}" stroke-width="3.0" stroke-linecap="round"/>'
            f'<ellipse cx="23" cy="-4" rx="7.2" ry="6.2" fill="{EYE}"/>'
            f'<rect x="14" y="-14" width="18" height="9" fill="{PINK}"/>'
            f'<path d="M 15,-5 Q 23,-7 31,-5" fill="none" stroke="{OL}" stroke-width="3.0" stroke-linecap="round"/>'
        )
    elif expr == "wink":
        parts.append(
            f'<ellipse cx="-23" cy="-7" rx="7.2" ry="8.0" fill="{EYE}"/>'
            f'<circle cx="-25.5" cy="-10" r="2.6" fill="#FFFFFF"/>'
            f'<path d="M 16,-12 L 27,-6 L 16,0" fill="none" stroke="{EYE}" stroke-width="4.0" stroke-linecap="round" stroke-linejoin="round"/>'
        )
    elif expr == "happy_squint":
        parts.append(
            f'<path d="M -31,-5 Q -23,-15 -15,-5" fill="none" stroke="{EYE}" stroke-width="4.0" stroke-linecap="round"/>'
            f'<path d="M 15,-5 Q 23,-15 31,-5" fill="none" stroke="{EYE}" stroke-width="4.0" stroke-linecap="round"/>'
        )
    elif expr == "calm_closed":
        parts.append(
            f'<path d="M -30,-6 Q -23,1 -16,-6" fill="none" stroke="{EYE}" stroke-width="3.6" stroke-linecap="round"/>'
            f'<path d="M 16,-6 Q 23,1 30,-6" fill="none" stroke="{EYE}" stroke-width="3.6" stroke-linecap="round"/>'
        )
    elif expr == "sleepy":
        parts.append(
            f'<ellipse cx="-23" cy="-4" rx="6.4" ry="4.2" fill="{EYE}"/>'
            f'<path d="M -31,-9 Q -23,-6 -15,-9" fill="none" stroke="{OL}" stroke-width="2.8" stroke-linecap="round"/>'
            f'<ellipse cx="23" cy="-4" rx="6.4" ry="4.2" fill="{EYE}"/>'
            f'<path d="M 15,-9 Q 23,-6 31,-9" fill="none" stroke="{OL}" stroke-width="2.8" stroke-linecap="round"/>'
        )

    # Signature crimson-berry rounded triangle nose
    parts.append(
        f'<path d="M -13.5,3 C -14.5,-4 -6.5,-7 0,-7 C 6.5,-7 14.5,-4 13.5,3 '
        f'C 12.5,10.5 4.8,14.5 0,14.5 C -4.8,14.5 -12.5,10.5 -13.5,3 Z" fill="{NOSE}" stroke="{OL}" stroke-width="2.5"/>'
        f'<ellipse cx="-4" cy="-1.5" rx="4.0" ry="2.1" transform="rotate(-14 -4 -1.5)" fill="{NOSE_HI}" fill-opacity="0.55"/>'
    )

    # Mouth + SINGLE ICONIC WHITE BUCKTOOTH!
    if expr == "meme_scream":
        # Iconic huge panicked gaping Loopy meme mouth (reference!)
        parts.append(
            f'<ellipse cx="0" cy="31" rx="16" ry="18" fill="#7D1E32" stroke="{OL}" stroke-width="3.0"/>'
            f'<ellipse cx="0" cy="38" rx="11" ry="8" fill="#F27E98"/>'
            f'<rect x="-6.5" y="14.5" width="13" height="8.5" rx="2.6" fill="#FFFFFF" stroke="{OL}" stroke-width="1.8"/>'
        )
    elif expr == "deadpan":
        parts.append(
            f'<path d="M -9,28 Q 0,25 9,28" fill="none" stroke="{OL}" stroke-width="3.0" stroke-linecap="round"/>'
            f'<rect x="-4.5" y="27" width="9" height="5" rx="1.8" fill="#FFFFFF" stroke="{OL}" stroke-width="1.5"/>'
        )
    elif expr in ("big_smile", "happy_squint"):
        parts.append(
            f'<path d="M -15.5,23 C -15.5,19 15.5,19 15.5,23 C 15.5,37 7.5,41 0,41 C -7.5,41 -15.5,37 -15.5,23 Z" '
            f'fill="{MOUTH}" stroke="{OL}" stroke-width="2.7" stroke-linejoin="round"/>'
            f'<rect x="-6.5" y="21" width="13" height="8" rx="2.5" fill="#FFFFFF" stroke="{OL}" stroke-width="1.8"/>'
        )
    elif expr == "sleepy":
        parts.append(
            f'<path d="M -8,27 Q 0,32 8,27" fill="none" stroke="{OL}" stroke-width="2.8" stroke-linecap="round"/>'
            f'<rect x="-4.2" y="27.2" width="8.4" height="5" rx="1.8" fill="#FFFFFF" stroke="{OL}" stroke-width="1.5"/>'
        )
    else:
        parts.append(
            f'<path d="M -12,24 C -12,21 12,21 12,24 C 12,34 6,37 0,37 C -6,37 -12,34 -12,24 Z" '
            f'fill="{MOUTH}" stroke="{OL}" stroke-width="2.5" stroke-linejoin="round"/>'
            f'<rect x="-5.5" y="22.3" width="11" height="7" rx="2.4" fill="#FFFFFF" stroke="{OL}" stroke-width="1.7"/>'
        )

    parts.append("</g>")
    return "".join(parts)


# =========================================================================== #
#  #61 — LOOPY RED BOW GLOW-UP (MEME TILT -> BREATHE -> TIE BOW -> FLOWER, NO BERET!)
# =========================================================================== #
def _red_bow(cx=150, cy=62, s=1.0, rot=0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot}) scale({s})">'
        f'<path d="M -4,4 C -28,-22 -58,-12 -52,12 C -47,30 -20,24 -4,10 Z" fill="#D85A68" stroke="{OL}" stroke-width="3.6" stroke-linejoin="round"/>'
        f'<path d="M 4,4 C 28,-22 58,-12 52,12 C 47,30 20,24 4,10 Z" fill="#D85A68" stroke="{OL}" stroke-width="3.6" stroke-linejoin="round"/>'
        f'<path d="M -12,6 C -26,2 -36,6 -38,11 M 12,6 C 26,2 36,6 38,11" fill="none" stroke="#A63442" stroke-width="2.5" stroke-linecap="round"/>'
        f'<ellipse cx="0" cy="8" rx="11" ry="9.5" fill="#E36E7B" stroke="{OL}" stroke-width="3.4"/>'
        f'</g>'
    )


def _yellow_flower(cx, cy, bloom=True, s=1.0, rot=0) -> str:
    if not bloom:
        return (
            f'<g transform="translate({cx},{cy}) rotate({rot}) scale({s})">'
            f'<path d="M 0,24 Q 2,10 0,-2" fill="none" stroke="#65A30D" stroke-width="4.0" stroke-linecap="round"/>'
            f'<ellipse cx="-7" cy="12" rx="7" ry="3.5" transform="rotate(-25 -7 12)" fill="#84CC16" stroke="{OL}" stroke-width="2.0"/>'
            f'<path d="M -10,-2 C -12,-14 -4,-20 0,-18 C 4,-20 12,-14 10,-2 C 6,4 -6,4 -10,-2 Z" fill="#FDE047" stroke="{OL}" stroke-width="2.5"/>'
            f'</g>'
        )
    petals = []
    for k in range(5):
        ang = math.radians(k * 72 - 90)
        px, py = math.cos(ang) * 14, math.sin(ang) * 14
        petals.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="11" ry="8.5" transform="rotate({k * 72 - 90} {px:.1f} {py:.1f})" fill="#FDE047" stroke="#EAB308" stroke-width="2.2"/>')
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot}) scale({s})">'
        f'<path d="M 4,14 L 12,42" stroke="#65A30D" stroke-width="4.2" stroke-linecap="round"/>'
        f'<ellipse cx="2" cy="28" rx="8" ry="4" transform="rotate(-25 2 28)" fill="#84CC16" stroke="{OL}" stroke-width="2.0"/>'
        f'{"".join(petals)}'
        f'<circle cx="0" cy="0" r="7.5" fill="#F59E0B"/>'
        f'</g>'
    )


def build_61_red_bow() -> list[tuple[str, Image.Image]]:
    # S0: Iconic meme Loopy tilted strongly right (+18°), wide eyes, gaping bucktooth mouth + yellow !!
    s0 = render_svg(
        shadow(154, 268, 66, 9)
        + loopy_body(146, 222, pose="sit", paws="panic_flail", lean=10)
        + loopy_head(164, 130, expr="meme_scream", strong_blush=True, rot=18)
        + excl_marks(56, 114, rot=-18, s=1.15)
    )
    # S1: Sitting upright, both paws cupping chubby cheeks taking a deep calming breath
    s1 = render_svg(
        shadow(150, 268, 68, 9)
        + loopy_body(150, 218, pose="sit", paws="none")
        + loopy_head(150, 128, expr="calm_closed", blush_hatch=True)
        + f'<ellipse cx="104" cy="160" rx="18" ry="13" transform="rotate(-26 104 160)" fill="{PINK}" stroke="{OL}" stroke-width="3.6"/>'
        + f'<ellipse cx="196" cy="160" rx="18" ry="13" transform="rotate(26 196 160)" fill="{PINK}" stroke="{OL}" stroke-width="3.6"/>'
        + '<path d="M 226,112 Q 240,104 252,112 M 230,124 Q 244,118 256,124" fill="none" stroke="#7EAAC8" stroke-width="3.0" stroke-linecap="round"/>'
    )
    # S2: Raising both paws up to tie big red ribbon bow atop head, determined eyes!
    s2 = render_svg(
        shadow()
        + loopy_body(150, 218, pose="stand", paws="none")
        + loopy_head(150, 130, expr="focused", show_tuft=False)
        + _red_bow(150, 66, s=1.08)
        + f'<ellipse cx="94" cy="90" rx="16" ry="12" transform="rotate(-40 94 90)" fill="{PINK}" stroke="{OL}" stroke-width="3.6"/>'
        + f'<ellipse cx="206" cy="90" rx="16" ry="12" transform="rotate(40 206 90)" fill="{PINK}" stroke="{OL}" stroke-width="3.6"/>'
    )
    # S3: Neat red bow, leaning head confidently (-10°), rosy glow getting into rhythm!
    s3 = render_svg(
        shadow()
        + loopy_body(150, 218, pose="walk", paws="wave_r", lean=-6)
        + loopy_head(144, 128, expr="smile", strong_blush=True, blush_hatch=True, show_tuft=False, rot=-10)
        + _red_bow(134, 64, s=1.05, rot=-10)
        + sp4(236, 98, r=9)
    )
    # S4: Tilted head (+8°), left paw propping chin happily, right paw holding yellow flower bud!
    s4 = render_svg(
        shadow(150, 268, 66, 9)
        + loopy_body(150, 218, pose="sit", paws="none", lean=4)
        + loopy_head(154, 128, expr="wink", strong_blush=True, blush_hatch=True, show_tuft=False, rot=8)
        + _red_bow(162, 64, s=1.02, rot=8)
        + f'<ellipse cx="112" cy="176" rx="17" ry="12" transform="rotate(-22 112 176)" fill="{PINK}" stroke="{OL}" stroke-width="3.6"/>'
        + _yellow_flower(214, 186, bloom=False, s=1.22, rot=14)
        + f'<ellipse cx="196" cy="204" rx="16" ry="11" transform="rotate(20 196 204)" fill="{PINK}" stroke="{OL}" stroke-width="3.6"/>'
        + sp4(60, 102, r=9)
    )
    # S5: Jumping joyfully off ground, arms wide, huge bucktooth grin + blooming yellow flower & sparkles!
    s5 = with_hero_aura(render_svg(
        shadow(150, 272, 54, 8, op=0.12)
        + loopy_body(150, 204, pose="jump", paws="wide_up")
        + loopy_head(150, 118, expr="big_smile", strong_blush=True, blush_hatch=True, show_tuft=False, rot=-5)
        + _red_bow(146, 54, s=1.08, rot=-5)
        + _yellow_flower(226, 152, bloom=True, s=1.18, rot=16)
        + sp4(54, 78, r=12) + sp4(248, 80, r=11) + sp4(60, 198, r=9)
        + heart(244, 212, s=11, fill="#F6A6B2", stroke="#D85A68")
    ), (246, 166, 178))
    return [
        ("Quên Việc!!", s0),
        ("Ôm Má Hít Thở", s1),
        ("Buộc Nơ Đỏ", s2),
        ("Tự Tin Vào Nhịp", s3),
        ("Chống Cằm Nụ Hoa", s4),
        ("Nở Rộ Glow-Up!", s5),
    ]


# =========================================================================== #
#  #62 — LOOPY TAIYAKI STREET SNACK (DYNAMIC POSES!)
# =========================================================================== #
def _taiyaki_hat(cx=150, cy=124, rot=0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot})">'
        f'<path d="M -38,-56 C -30,-84 28,-84 40,-56 Z" fill="#F6CCA0" stroke="#C88B4B" stroke-width="4.0" stroke-linejoin="round"/>'
        f'<path d="M 76,-14 C 102,-32 114,-22 108,2 C 114,22 102,32 76,16 Z" fill="#F6CCA0" stroke="#C88B4B" stroke-width="4.0" stroke-linejoin="round"/>'
        f'<path d="M -88,0 C -84,-48 -42,-64 4,-62 C 52,-60 86,-38 86,2 C 86,44 48,60 0,60 C -48,60 -86,42 -88,0 Z" fill="#FAD7AC" stroke="#C88B4B" stroke-width="4.2"/>'
        f'<path d="M -86,-12 C -98,-12 -98,14 -86,14" fill="#F6CCA0" stroke="#C88B4B" stroke-width="3.8" stroke-linecap="round"/>'
        f'<circle cx="-68" cy="-10" r="4.6" fill="#FFF8EE" stroke="#C88B4B" stroke-width="2.4"/>'
        f'<path d="M -46,-54 Q -56,0 -44,48 M 46,-52 Q 58,0 46,48 M 8,-60 Q 14,-36 10,-16" fill="none" stroke="#D19453" stroke-width="4.2" stroke-linecap="round"/>'
        f'<ellipse cx="0" cy="6" rx="52" ry="49" fill="{PINK}" stroke="#C88B4B" stroke-width="3.2"/>'
        f'</g>'
    )


def _taiyaki_bag(x=226, y=228, has_fish=False, s=1.0) -> str:
    parts = [f'<g transform="translate({x},{y}) scale({s})">']
    if has_fish:
        parts.append(
            '<g transform="translate(0,-30) rotate(-18)">'
            '<ellipse cx="0" cy="0" rx="22" ry="14" fill="#F6CCA0" stroke="#C88B4B" stroke-width="3.0"/>'
            '<path d="M -6,-12 Q -2,0 -6,12 M 4,-12 Q 8,0 4,12" fill="none" stroke="#C88B4B" stroke-width="2.4"/>'
            '<circle cx="-12" cy="-3" r="2.2" fill="#8C5927"/></g>'
            '<path d="M -12,-50 Q -16,-58 -10,-65 M 6,-52 Q 2,-60 8,-67" fill="none" stroke="#D99B58" stroke-width="2.4" stroke-linecap="round"/>'
        )
    parts.append(
        '<path d="M -26,-24 L 26,-24 L 22,28 L -22,28 Z" fill="#FFF3DC" stroke="#C88B4B" stroke-width="3.2" stroke-linejoin="round"/>'
        '<ellipse cx="-2" cy="4" rx="11" ry="6.5" fill="none" stroke="#C88B4B" stroke-width="2.2"/>'
        '<polygon points="9,4 15,-1 15,9" fill="none" stroke="#C88B4B" stroke-width="2.0"/>'
    )
    parts.append("</g>")
    return "".join(parts)


def _dango(cx=128, cy=188, rot=26, s=1.0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot}) scale({s})">'
        f'<line x1="0" y1="-26" x2="0" y2="34" stroke="#B6804A" stroke-width="4.2" stroke-linecap="round"/>'
        f'<circle cx="0" cy="14" r="10.5" fill="#FDBA74" stroke="#C88B4B" stroke-width="2.4"/>'
        f'<circle cx="0" cy="-3" r="10.5" fill="#A8D5BA" stroke="#5A8F70" stroke-width="2.4"/>'
        f'<circle cx="0" cy="-20" r="10.5" fill="#B68B60" stroke="#7A5636" stroke-width="2.4"/>'
        f'</g>'
    )


def build_62_taiyaki() -> list[tuple[str, Image.Image]]:
    s0 = render_svg(
        shadow(134, 268, 62, 9)
        + loopy_body(134, 220, pose="sit", paws="shrug", lean=8)
        + loopy_head(140, 132, expr="puzzled", rot=12)
        + _taiyaki_bag(236, 234, has_fish=False, s=0.95)
        + '<text x="228" y="194" font-family="Segoe UI" font-weight="bold" font-size="22" fill="#C88B4B">?</text>'
    )
    s1 = render_svg(
        shadow()
        + loopy_body(150, 218, pose="stand", paws="wide_up", lean=-5)
        + _taiyaki_hat(146, 124, rot=-8)
        + loopy_head(146, 130, scale=0.84, expr="curious", show_ears=False, show_tuft=False, head_outline=False, blush_hatch=True, rot=-8)
    )
    s2 = render_svg(
        shadow(134, 268, 64, 9)
        + loopy_body(134, 216, pose="walk", paws="walk_swing", lean=6)
        + _taiyaki_hat(138, 124, rot=6)
        + loopy_head(138, 130, scale=0.84, expr="smile", show_ears=False, show_tuft=False, head_outline=False, blush_hatch=True, rot=6)
        + _taiyaki_bag(240, 232, has_fish=True, s=0.95)
    )
    s3 = render_svg(
        shadow(140, 268, 66, 9)
        + loopy_body(140, 218, pose="sit", paws="center", lean=-4)
        + _taiyaki_hat(138, 124, rot=-5)
        + loopy_head(138, 130, scale=0.84, expr="smile", show_ears=False, show_tuft=False, head_outline=False, blush_hatch=True, rot=-5)
        + _dango(118, 194, rot=24, s=0.96)
        + _taiyaki_bag(242, 234, has_fish=True, s=0.86)
    )
    s4 = render_svg(
        shadow(150, 268, 66, 9)
        + loopy_body(150, 218, pose="sit", paws="center", lean=6)
        + _taiyaki_hat(154, 124, rot=10)
        + loopy_head(154, 130, scale=0.84, expr="wink", strong_blush=True, show_ears=False, show_tuft=False, head_outline=False, blush_hatch=True, rot=10)
        + _dango(136, 178, rot=28, s=0.98)
        + heart(246, 180, s=11, fill="#93C5FD", stroke="#3B82F6", rot=12)
        + sp4(50, 184, r=10)
    )
    s5 = with_hero_aura(render_svg(
        shadow(142, 272, 56, 8, op=0.12)
        + loopy_body(142, 206, pose="jump", paws="wide_up")
        + _taiyaki_hat(142, 114, rot=-6)
        + loopy_head(142, 120, scale=0.84, expr="happy_squint", strong_blush=True, show_ears=False, show_tuft=False, head_outline=False, blush_hatch=True, rot=-6)
        + _dango(90, 152, rot=-22, s=0.98)
        + _taiyaki_bag(244, 232, has_fish=True, s=0.92)
        + heart(246, 146, s=11, fill="#93C5FD", stroke="#3B82F6", rot=12)
        + sp4(44, 82, r=12) + sp4(248, 76, r=10)
    ), (250, 215, 172))
    return [
        ("Túi Bánh Trống", s0),
        ("Đội Mũ Taiyaki", s1),
        ("Bánh Cá Nóng Hổi", s2),
        ("Ngồi Ôm Dango", s3),
        ("Nháy Mắt Nhấm Nháp", s4),
        ("No Nê Phố Ẩm Thực!", s5),
    ]


# =========================================================================== #
#  #63 — LOOPY PIGGY DESSERT CAFE (DYNAMIC POSES!)
# =========================================================================== #
def _white_glasses(cx=150, cy=124, s=1.0, rot=0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot}) scale({s})">'
        f'<circle cx="-22" cy="-5" r="15" fill="#FFFFFF" fill-opacity="0.22" stroke="#FFFFFF" stroke-width="3.6"/>'
        f'<circle cx="22" cy="-5" r="15" fill="#FFFFFF" fill-opacity="0.22" stroke="#FFFFFF" stroke-width="3.6"/>'
        f'<path d="M -7,-5 Q 0,-9 7,-5" fill="none" stroke="#FFFFFF" stroke-width="3.4"/>'
        f'</g>'
    )


def _piggy_hood(cx=150, cy=118, rot=0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot})">'
        f'<path d="M -72,-10 C -74,-44 -68,-74 -46,-76 C -30,-78 -22,-64 -12,-64 L 12,-64 C 22,-64 30,-78 46,-76 C 68,-74 74,-44 72,-10 C 76,34 54,60 0,60 C -54,60 -76,34 -72,-10 Z" fill="#FFD9E6" stroke="#E89DB7" stroke-width="4.2"/>'
        f'<ellipse cx="-46" cy="-58" rx="12" ry="9" fill="#FFB3CE" fill-opacity="0.7"/>'
        f'<ellipse cx="46" cy="-58" rx="12" ry="9" fill="#FFB3CE" fill-opacity="0.7"/>'
        f'<circle cx="-18" cy="-48" r="3.6" fill="{EYE}"/><circle cx="18" cy="-48" r="3.6" fill="{EYE}"/>'
        f'<ellipse cx="0" cy="-35" rx="14" ry="8.5" fill="#FF9EBC"/>'
        f'<circle cx="-5" cy="-35" r="2.3" fill="#D45B82"/><circle cx="5" cy="-35" r="2.3" fill="#D45B82"/>'
        f'<ellipse cx="0" cy="14" rx="52" ry="44" fill="{PINK}" stroke="#E89DB7" stroke-width="3.2"/>'
        f'</g>'
    )


def _smiling_cheese(cx=232, cy=236, s=1.0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) scale({s})">'
        f'<path d="M -26,8 L -22,-10 L 0,-22 L 26,-6 L 26,14 L -26,14 Z" fill="#FEF08A" stroke="#EAB308" stroke-width="2.6" stroke-linejoin="round"/>'
        f'<circle cx="-12" cy="-6" r="3.5" fill="#FDE047"/><circle cx="12" cy="-4" r="3.0" fill="#FDE047"/>'
        f'<circle cx="-7" cy="4" r="2.2" fill="#38BDF8"/><circle cx="7" cy="4" r="2.2" fill="#38BDF8"/>'
        f'<path d="M -3,7 Q 0,11 3,7" fill="none" stroke="#E11D48" stroke-width="2.2" stroke-linecap="round"/>'
        f'</g>'
    )


def _ice_cream(cx=168, cy=188, scoops=1, s=1.0, rot=-14) -> str:
    parts = [f'<g transform="translate({cx},{cy}) rotate({rot}) scale({s})">']
    parts.append('<polygon points="-10,6 10,6 0,34" fill="#FDE68A" stroke="#D97706" stroke-width="2.4" stroke-linejoin="round"/>')
    if scoops == 1:
        parts.append('<circle cx="0" cy="-2" r="12" fill="#FFFDF5" stroke="#D6BFA0" stroke-width="2.2"/>')
    else:
        parts.append('<circle cx="0" cy="-1" r="12" fill="#A6D8EB" stroke="#5EA9C7" stroke-width="2.2"/>')
        parts.append('<circle cx="0" cy="-17" r="11.5" fill="#FFFDF5" stroke="#D6BFA0" stroke-width="2.2"/>')
    parts.append("</g>")
    return "".join(parts)


def _cherry_cake(cx=238, cy=114, s=1.0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) scale({s})">'
        f'<ellipse cx="0" cy="22" rx="34" ry="12" fill="#BFDBFE" stroke="#7CB8E0" stroke-width="2.4"/>'
        f'<rect x="-24" y="-8" width="48" height="28" rx="6" fill="#FDE8C8" stroke="#D4A373" stroke-width="2.4"/>'
        f'<path d="M -24,-8 C -24,-18 24,-18 24,-8 L 24,2 C 16,8 8,0 0,5 C -8,0 -16,8 -24,2 Z" fill="#F9A8C9" stroke="#E06D97" stroke-width="2.2"/>'
        f'<circle cx="-12" cy="-14" r="5" fill="#FFFFFF"/><circle cx="0" cy="-16" r="5.5" fill="#FFFFFF"/><circle cx="12" cy="-14" r="5" fill="#FFFFFF"/>'
        f'<circle cx="-12" cy="-18" r="4.2" fill="#E11D48"/><circle cx="0" cy="-20" r="4.6" fill="#E11D48"/><circle cx="12" cy="-18" r="4.2" fill="#E11D48"/>'
        f'</g>'
    )


def build_63_piggy_cafe() -> list[tuple[str, Image.Image]]:
    s0 = render_svg(
        shadow(134, 268, 62, 9)
        + loopy_body(134, 218, pose="sit", paws="down", lean=10)
        + loopy_head(140, 130, expr="curious", rot=12)
        + _white_glasses(140, 130, s=1.0, rot=12)
        + _smiling_cheese(236, 240, s=1.0)
    )
    s1 = render_svg(
        shadow()
        + loopy_body(150, 218, pose="stand", paws="wide_up", lean=-5)
        + _piggy_hood(146, 118, rot=-6)
        + loopy_head(146, 134, scale=0.80, expr="smile", show_ears=False, show_tuft=False, head_outline=False, rot=-6)
        + _white_glasses(146, 134, s=0.80, rot=-6)
    )
    s2 = render_svg(
        shadow()
        + loopy_body(150, 216, pose="walk", paws="wave_r", lean=5)
        + _piggy_hood(154, 118, rot=6)
        + loopy_head(154, 134, scale=0.80, expr="smile", show_ears=False, show_tuft=False, head_outline=False, rot=6)
        + _white_glasses(154, 134, s=0.80, rot=6)
        + _ice_cream(216, 168, scoops=1, s=1.0, rot=16)
    )
    s3 = render_svg(
        shadow()
        + loopy_body(150, 218, pose="sit", paws="center", lean=-6)
        + _piggy_hood(146, 118, rot=-8)
        + loopy_head(146, 134, scale=0.80, expr="wink", strong_blush=True, show_ears=False, show_tuft=False, head_outline=False, rot=-8)
        + _white_glasses(146, 134, s=0.80, rot=-8)
        + _ice_cream(166, 194, scoops=2, s=1.02)
        + sp4(56, 128, r=10, fill="#A6D8EB", stroke="#5EA9C7")
    )
    s4 = render_svg(
        shadow(136, 268, 66, 9)
        + loopy_body(136, 216, pose="stand", paws="wave_r", lean=6)
        + _piggy_hood(140, 118, rot=8)
        + loopy_head(140, 134, scale=0.80, expr="big_smile", strong_blush=True, show_ears=False, show_tuft=False, head_outline=False, rot=8)
        + _white_glasses(140, 134, s=0.80, rot=8)
        + _ice_cream(152, 196, scoops=2, s=0.98)
        + _cherry_cake(242, 108, s=0.95)
        + sp4(248, 178, r=10)
    )
    s5 = with_hero_aura(render_svg(
        shadow(146, 268, 74, 9)
        + loopy_body(146, 218, pose="sit", paws="wide_up")
        + _piggy_hood(146, 116, rot=-4)
        + loopy_head(146, 132, scale=0.80, expr="happy_squint", strong_blush=True, show_ears=False, show_tuft=False, head_outline=False, rot=-4)
        + _white_glasses(146, 132, s=0.80, rot=-4)
        + _ice_cream(164, 196, scoops=2, s=1.02)
        + _smiling_cheese(54, 244, s=0.95)
        + _cherry_cake(244, 100, s=0.95)
        + sp4(48, 92, r=12) + heart(246, 170, s=10, fill="#F28FB0", stroke="#D45B82")
    ), (242, 143, 176))
    return [
        ("Ngắm Phô Mai", s0),
        ("Trùm Mũ Heo Hồng", s1),
        ("Bước Đi Cầm Kem", s2),
        ("Kem 2 Tầng Nháy Mắt", s3),
        ("Bánh Kem Cherry", s4),
        ("Đại Tiệc Cafe Ngọt!", s5),
    ]


# =========================================================================== #
#  #64 — LOOPY SAUNA SHEEP DETOX (DYNAMIC POSES!)
# =========================================================================== #
def _black_glasses_slid(cx=150, cy=134, rot=5) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot})">'
        f'<rect x="-42" y="-2" width="34" height="22" rx="6" fill="#FFFFFF" fill-opacity="0.22" stroke="#2D1E22" stroke-width="4.2"/>'
        f'<rect x="8" y="-2" width="34" height="22" rx="6" fill="#FFFFFF" fill-opacity="0.22" stroke="#2D1E22" stroke-width="4.2"/>'
        f'<line x1="-8" y1="6" x2="8" y2="6" stroke="#2D1E22" stroke-width="4.2"/>'
        f'</g>'
    )


def _sheep_towel(cx=150, cy=124, rot=0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot})">'
        f'<path d="M -58,-20 C -56,-70 56,-70 58,-20 C 34,-42 -34,-42 -58,-20 Z" fill="#FFFFFF" stroke="#D17A90" stroke-width="4.2" stroke-linejoin="round"/>'
        f'<ellipse cx="-66" cy="-4" rx="27" ry="31" transform="rotate(-14 -66 -4)" fill="#FFFFFF" stroke="#D17A90" stroke-width="4.2"/>'
        f'<path d="M -68,-14 C -58,-18 -54,-4 -62,6 C -70,14 -78,4 -72,-6" fill="none" stroke="#D17A90" stroke-width="3.2" stroke-linecap="round"/>'
        f'<ellipse cx="66" cy="-4" rx="27" ry="31" transform="rotate(14 66 -4)" fill="#FFFFFF" stroke="#D17A90" stroke-width="4.2"/>'
        f'<path d="M 68,-14 C 58,-18 54,-4 62,6 C 70,14 78,4 72,-6" fill="none" stroke="#D17A90" stroke-width="3.2" stroke-linecap="round"/>'
        f'</g>'
    )


def _steam_curls() -> str:
    return (
        '<path d="M 48,190 Q 38,170 50,154 Q 58,142 46,128" fill="none" stroke="#F49CB2" stroke-width="3.4" stroke-linecap="round" stroke-dasharray="10,7"/>'
        '<path d="M 252,190 Q 262,170 250,154 Q 242,142 254,128" fill="none" stroke="#F49CB2" stroke-width="3.4" stroke-linecap="round" stroke-dasharray="10,7"/>'
    )


def _wa_text(x=176, y=52) -> str:
    return f'<text x="{x}" y="{y}" text-anchor="middle" font-family="Segoe UI" font-weight="900" font-size="30" fill="#8CB8DF" stroke="#5B8EB8" stroke-width="1.2">WA~</text>'


def build_64_sauna_sheep() -> list[tuple[str, Image.Image]]:
    s0 = render_svg(
        shadow() + loopy_body(150, 222, pose="sit", paws="down", lean=-8)
        + loopy_head(144, 134, expr="sleepy", rot=-12)
        + _black_glasses_slid(144, 140, rot=-6)
    )
    s1 = render_svg(
        shadow() + loopy_body(150, 218, pose="stand", paws="wide_up")
        + loopy_head(150, 126, expr="curious", show_ears=False, show_tuft=False, rot=6)
        + _sheep_towel(150, 122, rot=6)
    )
    s2 = render_svg(
        shadow() + loopy_body(150, 218, pose="sit", paws="none")
        + loopy_head(150, 126, expr="calm_closed", strong_blush=True, blush_hatch=True, show_ears=False, show_tuft=False, rot=-6)
        + _sheep_towel(150, 122, rot=-6)
        + f'<ellipse cx="106" cy="166" rx="17" ry="12" transform="rotate(-22 106 166)" fill="{PINK}" stroke="{OL}" stroke-width="3.6"/>'
        + f'<ellipse cx="194" cy="166" rx="17" ry="12" transform="rotate(22 194 166)" fill="{PINK}" stroke="{OL}" stroke-width="3.6"/>'
    )
    s3 = render_svg(
        shadow() + _steam_curls()
        + loopy_body(150, 218, pose="sit", paws="shrug", lean=5)
        + loopy_head(154, 126, expr="smile", strong_blush=True, blush_hatch=True, show_ears=False, show_tuft=False, rot=8)
        + _sheep_towel(154, 122, rot=8)
        + sp4(56, 84, r=11, fill="#E0F2FE", stroke="#7DBCE6") + sp4(246, 86, r=10, fill="#E0F2FE", stroke="#7DBCE6")
    )
    s4 = render_svg(
        shadow() + _steam_curls()
        + loopy_body(150, 216, pose="walk", paws="wide_up", lean=-7)
        + loopy_head(144, 126, expr="big_smile", strong_blush=True, blush_hatch=True, show_ears=False, show_tuft=False, rot=-10)
        + _sheep_towel(144, 122, rot=-10)
        + _wa_text(176, 52) + heart_with_eyes(66, 62, s=20, rot=-12)
    )
    s5 = with_hero_aura(render_svg(
        shadow(150, 272, 54, 8, op=0.12) + _steam_curls()
        + loopy_body(150, 206, pose="jump", paws="wide_up")
        + loopy_head(150, 118, expr="happy_squint", strong_blush=True, blush_hatch=True, show_ears=False, show_tuft=False, rot=4)
        + _sheep_towel(150, 114, rot=4)
        + _wa_text(178, 48) + heart_with_eyes(64, 58, s=21, rot=-12)
        + sp4(250, 82, r=12, fill="#E0F2FE", stroke="#60A5FA") + sp4(46, 224, r=10, fill="#FEF08A", stroke="#D99B58")
    ), (168, 201, 232))
    return [
        ("Kính Trễ Mệt Mỏi", s0),
        ("Quấn Khăn Cừu", s1),
        ("Ôm Má Ấm Áp", s2),
        ("Xông Hơi Thư Giãn", s3),
        ("Reo Vui WA~", s4),
        ("Bật Nhảy Sảng Khoái!", s5),
    ]


# =========================================================================== #
#  #65 — LOOPY HONEY BEE KPI (ANTI-EGG! CURLED -> TILT -> FLY -> HONEY POT -> QUEEN BEE!)
# =========================================================================== #
def _pastel_bear(cx, cy, stroke_col="#93C5FD", rot=0, s=0.68, happy=False) -> str:
    eyes = (
        f'<path d="M -18,-6 L -9,-2 L -18,2 M 18,-6 L 9,-2 L 18,2" fill="none" stroke="{stroke_col}" stroke-width="3.6" stroke-linecap="round"/>'
        if happy else
        f'<circle cx="-14" cy="-3" r="4.2" fill="{stroke_col}"/><circle cx="14" cy="-3" r="4.2" fill="{stroke_col}"/>'
    )
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot}) scale({s})">'
        f'<circle cx="-30" cy="-30" r="14" fill="#FFFFFF" stroke="{stroke_col}" stroke-width="5.5"/>'
        f'<circle cx="30" cy="-30" r="14" fill="#FFFFFF" stroke="{stroke_col}" stroke-width="5.5"/>'
        f'<ellipse cx="0" cy="0" rx="40" ry="34" fill="#FFFFFF" stroke="{stroke_col}" stroke-width="5.5"/>'
        f'{eyes}<ellipse cx="0" cy="6" rx="7.5" ry="5" fill="{stroke_col}"/>'
        f'<path d="M -8,14 Q 0,21 8,14" fill="none" stroke="{stroke_col}" stroke-width="3.2" stroke-linecap="round"/>'
        f'</g>'
    )


def _honey_pot(cx, cy, s=1.0, rot=0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot}) scale({s})">'
        f'<ellipse cx="0" cy="6" rx="22" ry="19" fill="#F5B82E" stroke="#7A5C52" stroke-width="3.0"/>'
        f'<rect x="-15" y="-16" width="30" height="8" rx="4" fill="#FDE047" stroke="#7A5C52" stroke-width="2.6"/>'
        f'<path d="M -14,-8 C -10,4 -4,-2 0,6 C 4,-2 10,4 14,-8 Z" fill="#FDE047"/>'
        f'<ellipse cx="0" cy="8" rx="11" ry="6" fill="#FFFDF2" stroke="#D99B27" stroke-width="1.6"/>'
        f'</g>'
    )


def _bee_hood_and_body(cx=150, cy=150, antennae=False, wings=False, stripes=False, pose="sit", paws="down", lean=0, crown=False) -> str:
    parts = [f'<g transform="translate({cx},{cy}) rotate({lean})">']
    if wings:
        parts.append(
            '<ellipse cx="-66" cy="34" rx="26" ry="14" transform="rotate(-26 -66 34)" fill="#E0F2FE" stroke="#7A5C52" stroke-width="3.2"/>'
            '<ellipse cx="66" cy="34" rx="26" ry="14" transform="rotate(26 66 34)" fill="#E0F2FE" stroke="#7A5C52" stroke-width="3.2"/>'
        )
    # Feet
    if pose == "sit":
        parts.append(
            f'<ellipse cx="-32" cy="94" rx="18" ry="14" transform="rotate(-16 -32 94)" fill="{PAW}" stroke="{OL}" stroke-width="3.4"/>'
            f'<ellipse cx="32" cy="94" rx="18" ry="14" transform="rotate(16 32 94)" fill="{PAW}" stroke="{OL}" stroke-width="3.4"/>'
        )
    elif pose == "fly":
        parts.append(
            f'<ellipse cx="-20" cy="98" rx="16" ry="10" transform="rotate(18 -20 98)" fill="{PAW}" stroke="{OL}" stroke-width="3.4"/>'
            f'<ellipse cx="20" cy="98" rx="16" ry="10" transform="rotate(-18 20 98)" fill="{PAW}" stroke="{OL}" stroke-width="3.4"/>'
        )
    # Body
    body_c = "#FDE068" if stripes else "#FEF5B8"
    parts.append(
        f'<path d="M -44,24 C -54,66 -36,100 0,100 C 36,100 54,66 44,24 Z" fill="{body_c}" stroke="#7A5C52" stroke-width="3.8"/>'
    )
    if stripes:
        parts.append(
            '<path d="M -45,46 Q 0,58 45,46 L 45,62 Q 0,74 -45,62 Z" fill="#7A5C52"/>'
            '<path d="M -39,76 Q 0,86 39,76 L 33,89 Q 0,97 -33,89 Z" fill="#7A5C52"/>'
        )
    # Arms
    if paws == "up":
        parts.append(
            f'<path d="M -38,34 C -68,18 -64,-4 -44,12" fill="{PINK}" stroke="{OL}" stroke-width="3.6" stroke-linecap="round"/>'
            f'<path d="M 38,34 C 68,18 64,-4 44,12" fill="{PINK}" stroke="{OL}" stroke-width="3.6" stroke-linecap="round"/>'
        )
    elif paws == "center":
        parts.append(
            f'<ellipse cx="-24" cy="54" rx="16" ry="11" transform="rotate(18 -24 54)" fill="{PINK}" stroke="{OL}" stroke-width="3.4"/>'
            f'<ellipse cx="24" cy="54" rx="16" ry="11" transform="rotate(-18 24 54)" fill="{PINK}" stroke="{OL}" stroke-width="3.4"/>'
        )
    else:
        parts.append(
            f'<path d="M -42,36 C -60,52 -54,70 -38,66" fill="{PINK}" stroke="{OL}" stroke-width="3.6" stroke-linecap="round"/>'
            f'<path d="M 42,36 C 60,52 54,70 38,66" fill="{PINK}" stroke="{OL}" stroke-width="3.6" stroke-linecap="round"/>'
        )
    # Ears + yellow hood
    parts.append(
        f'<circle cx="-52" cy="-42" r="14" fill="{PINK}" stroke="#E094A8" stroke-width="3.0"/>'
        f'<circle cx="52" cy="-42" r="14" fill="{PINK}" stroke="#E094A8" stroke-width="3.0"/>'
        '<path d="M -66,-6 C -66,-50 -36,-64 0,-64 C 36,-64 66,-50 66,-6 C 66,36 42,52 0,52 C -42,52 -66,36 -66,-6 Z" fill="#FEF3A8" stroke="#D4AA46" stroke-width="4.0"/>'
    )
    if antennae:
        parts.append(
            '<path d="M -18,-60 L -26,-84 M 18,-60 L 26,-84" stroke="#7A5C52" stroke-width="4.8" stroke-linecap="round"/>'
            '<circle cx="-27" cy="-88" r="8.5" fill="#F5B82E" stroke="#7A5C52" stroke-width="2.6"/>'
            '<circle cx="27" cy="-88" r="8.5" fill="#F5B82E" stroke="#7A5C52" stroke-width="2.6"/>'
        )
    if crown:
        parts.append('<polygon points="-16,-62 -12,-82 0,-70 12,-82 16,-62" fill="#FDE047" stroke="#B45309" stroke-width="2.4" stroke-linejoin="round"/>')
    parts.append(f'<ellipse cx="0" cy="-2" rx="46" ry="40" fill="{PINK}"/>')
    parts.append("</g>")
    return "".join(parts)


def build_65_honey_bee() -> list[tuple[str, Image.Image]]:
    # S0: Curled up sleepy in pale-yellow hood (not stiff egg!)
    s0 = render_svg(
        shadow(150, 264, 72, 10)
        + '<ellipse cx="150" cy="212" rx="68" ry="48" fill="#FEF5B8" stroke="#D4AA46" stroke-width="4.0"/>'
        + f'<ellipse cx="146" cy="204" rx="42" ry="34" fill="{PINK}"/>'
        + loopy_head(146, 206, scale=0.72, expr="sleepy", show_ears=False, show_tuft=False, head_outline=False, rot=-10)
        + _z_vec(212, 146, 0.85) + _z_vec(228, 128, 1.05)
    )
    # S1: Sitting up tilting head curiously as antennae sprout!
    s1 = render_svg(
        shadow(150, 266, 62, 9)
        + _bee_hood_and_body(150, 156, antennae=True, wings=False, stripes=False, pose="sit", paws="down", lean=10)
        + loopy_head(152, 154, scale=0.74, expr="curious", show_ears=False, show_tuft=False, head_outline=False, rot=10)
    )
    # S2: Tiny bee wings fluttering lifting off ground!
    s2 = render_svg(
        shadow(150, 272, 48, 7, op=0.12)
        + '<path d="M 48,200 Q 68,214 82,202 M 252,196 Q 232,210 218,198" fill="none" stroke="#93C5FD" stroke-width="3.0" stroke-linecap="round"/>'
        + _bee_hood_and_body(150, 140, antennae=True, wings=True, stripes=True, pose="fly", paws="up", lean=-8)
        + loopy_head(148, 138, scale=0.74, expr="focused", show_ears=False, show_tuft=False, head_outline=False, rot=-8)
    )
    # S3: Hugging little honey pot with 2 pastel outline bears cheering behind!
    s3 = render_svg(
        shadow(150, 266, 70, 9)
        + _pastel_bear(70, 118, "#93C5FD", rot=-14, s=0.70, happy=False)
        + _pastel_bear(230, 118, "#C4B5FD", rot=14, s=0.70, happy=True)
        + _bee_hood_and_body(150, 152, antennae=True, wings=True, stripes=True, pose="sit", paws="center")
        + _honey_pot(150, 214, s=0.92)
        + loopy_head(150, 150, scale=0.74, expr="smile", show_ears=False, show_tuft=False, head_outline=False)
    )
    # S4: Flying happily amid flowers & ring of 4 pastel bears!
    s4 = render_svg(
        _pastel_bear(70, 92, "#F9A8D4", rot=-16, s=0.66, happy=True)
        + _pastel_bear(230, 92, "#93C5FD", rot=16, s=0.66, happy=True)
        + _pastel_bear(62, 214, "#86EFAC", rot=-10, s=0.68, happy=True)
        + _pastel_bear(238, 214, "#C4B5FD", rot=10, s=0.68, happy=False)
        + ditsy_flower(150, 266, 9, "#FDE047", "#F97316") + ditsy_flower(112, 264, 8, "#F9A8D4", "#FDE047") + ditsy_flower(188, 264, 8, "#93C5FD", "#FDE047")
        + _bee_hood_and_body(150, 142, antennae=True, wings=True, stripes=True, pose="fly", paws="up", lean=8)
        + loopy_head(152, 140, scale=0.74, expr="wink", strong_blush=True, show_ears=False, show_tuft=False, head_outline=False, rot=8)
    )
    # S5: Queen Bee Loopy glowing lifting golden honey pot high!
    s5 = with_hero_aura(render_svg(
        _pastel_bear(74, 82, "#F9A8D4", rot=-14, s=0.62, happy=True)
        + _pastel_bear(226, 82, "#93C5FD", rot=14, s=0.62, happy=True)
        + _pastel_bear(62, 224, "#86EFAC", rot=-10, s=0.64, happy=True)
        + _pastel_bear(238, 224, "#FDBA74", rot=10, s=0.64, happy=True)
        + _bee_hood_and_body(150, 146, antennae=True, wings=True, stripes=True, pose="fly", paws="up", crown=True)
        + loopy_head(150, 144, scale=0.76, expr="big_smile", strong_blush=True, show_ears=False, show_tuft=False, head_outline=False)
        + _honey_pot(228, 152, s=0.95, rot=14)
        + sp4(52, 150, r=11) + sp4(254, 118, r=10) + sp4(150, 268, r=10)
    ), (234, 184, 68))
    return [
        ("Cuộn Tròn Ngái Ngủ", s0),
        ("Nghiêng Đầu Mọc Râu", s1),
        ("Vỗ Cánh Bay Nhẹ", s2),
        ("Ôm Hũ Mật Cổ Vũ", s3),
        ("Bay Giữa Hoa & Gấu", s4),
        ("Ong Chúa Mật Vàng!", s5),
    ]


# =========================================================================== #
#  #66 — LOOPY POOLSIDE DUCK CHILL (DYNAMIC POSES!)
# =========================================================================== #
def _duck_float(cx=150, cy=214, s=1.0, rot=0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot}) scale({s})">'
        f'<circle cx="0" cy="-22" r="16" fill="#FFFFFF" stroke="#EAB308" stroke-width="2.4"/>'
        f'<circle cx="0" cy="-19" r="12" fill="#FEF08A"/>'
        f'<circle cx="-4.5" cy="-21" r="1.8" fill="{EYE}"/><circle cx="4.5" cy="-21" r="1.8" fill="{EYE}"/>'
        f'<polygon points="-4,-18 4,-18 0,-13" fill="#F97316"/>'
        f'<rect x="-64" y="-16" width="128" height="36" rx="18" fill="#FDE047" stroke="#EAB308" stroke-width="3.6"/>'
        f'<path d="M -46,-6 Q 0,-12 46,-6" fill="none" stroke="#FEF9C3" stroke-width="5.0" stroke-linecap="round"/>'
        f'</g>'
    )


def _striped_pool_tube(cx=150, cy=158) -> str:
    wedges = []
    for k in range(12):
        a1, a2 = math.radians(k * 30), math.radians((k + 1) * 30)
        col = "#F7CF52" if k % 2 == 0 else "#FFFFFF"
        r_out, r_in = 92, 46
        x1, y1, x2, y2 = cx + math.cos(a1) * r_out, cy + math.sin(a1) * r_out, cx + math.cos(a2) * r_out, cy + math.sin(a2) * r_out
        x3, y3, x4, y4 = cx + math.cos(a2) * r_in, cy + math.sin(a2) * r_in, cx + math.cos(a1) * r_in, cy + math.sin(a1) * r_in
        wedges.append(f'<path d="M {x1:.1f},{y1:.1f} A {r_out},{r_out} 0 0,1 {x2:.1f},{y2:.1f} L {x3:.1f},{y3:.1f} A {r_in},{r_in} 0 0,0 {x4:.1f},{y4:.1f} Z" fill="{col}"/>')
    return (
        f'<ellipse cx="{cx}" cy="{cy}" rx="126" ry="118" fill="#D4F3FC"/>'
        f'<ellipse cx="{cx}" cy="{cy}" rx="114" ry="108" fill="#8CDDF5"/>'
        f'<path d="M 42,118 Q 56,82 90,68 M 216,68 Q 250,84 260,120 M 50,204 Q 72,240 106,252" fill="none" stroke="#FFFFFF" stroke-width="3.8" stroke-linecap="round"/>'
        f'{"".join(wedges)}'
        f'<circle cx="{cx}" cy="{cy}" r="92" fill="none" stroke="#E5A933" stroke-width="3.8"/>'
        f'<circle cx="{cx}" cy="{cy}" r="46" fill="#6EC6E6" stroke="#E5A933" stroke-width="3.2"/>'
    )


def build_66_poolside_duck() -> list[tuple[str, Image.Image]]:
    s0 = render_svg(
        shadow() + loopy_body(146, 218, pose="sit", paws="center", lean=-6)
        + loopy_head(142, 130, expr="curious", rot=-10)
        + _duck_float(182, 224, s=0.68, rot=12)
    )
    s1 = render_svg(
        shadow() + loopy_body(150, 214, pose="walk", paws="wide_up", lean=6)
        + _duck_float(150, 212, s=0.92, rot=5)
        + loopy_head(154, 124, expr="smile", rot=8)
    )
    s2 = render_svg(
        '<ellipse cx="150" cy="256" rx="92" ry="22" fill="#9BE3F7"/>'
        + loopy_body(150, 198, pose="jump", paws="wide_up", lean=-6)
        + _duck_float(148, 198, s=0.94, rot=-8)
        + loopy_head(144, 110, expr="big_smile", strong_blush=True, rot=-8)
        + heart(54, 96, s=16, fill="#FB7185", stroke="#E11D48", rot=-12)
        + heart(246, 136, s=14, fill="#F472B6", stroke="#DB2777", rot=12)
        + '<circle cx="62" cy="222" r="6" fill="#6EC6E6"/><circle cx="242" cy="218" r="6" fill="#6EC6E6"/>'
    )
    s3 = render_svg(
        _striped_pool_tube(150, 162)
        + loopy_body(150, 198, rx=42, ry=36, pose="hover", paws="wave_r", lean=6)
        + loopy_head(154, 128, scale=0.82, expr="smile", blush_hatch=True, rot=8)
    )
    s4 = render_svg(
        _striped_pool_tube(150, 162)
        + f'<ellipse cx="92" cy="146" rx="22" ry="15" transform="rotate(-24 92 146)" fill="{PINK}" stroke="{OL}" stroke-width="3.6"/>'
        + f'<ellipse cx="208" cy="146" rx="22" ry="15" transform="rotate(24 208 146)" fill="{PINK}" stroke="{OL}" stroke-width="3.6"/>'
        + loopy_body(150, 196, rx=42, ry=36, pose="hover", paws="none", lean=-6)
        + loopy_head(146, 130, scale=0.82, expr="wink", strong_blush=True, blush_hatch=True, rot=-8)
        + sp4(64, 58, r=12, fill="#FFFFFF", stroke="#6EC6E6") + sp4(242, 64, r=10, fill="#FFFFFF", stroke="#6EC6E6")
    )
    s5 = with_hero_aura(render_svg(
        _striped_pool_tube(150, 158)
        + f'<ellipse cx="92" cy="144" rx="22" ry="15" transform="rotate(-24 92 144)" fill="{PINK}" stroke="{OL}" stroke-width="3.6"/>'
        + f'<ellipse cx="208" cy="144" rx="22" ry="15" transform="rotate(24 208 144)" fill="{PINK}" stroke="{OL}" stroke-width="3.6"/>'
        + loopy_body(150, 194, rx=42, ry=36, pose="hover", paws="none")
        + loopy_head(150, 128, scale=0.82, expr="calm_closed", strong_blush=True, blush_hatch=True)
        + sp4(62, 54, r=14, fill="#FFFFFF", stroke="#38BDF8") + sp4(240, 58, r=11, fill="#FFFFFF", stroke="#38BDF8")
        + star5(234, 246, r=13, fill="#FFFFFF", stroke="#6EC6E6") + sp4(56, 236, r=10, fill="#FEF08A", stroke="#EAB308")
    ), (110, 198, 230))
    return [
        ("Ôm Phao Vịt Ngại", s0),
        ("Đeo Phao Sẵn Sàng", s1),
        ("Nhảy Ùm Tung Tim", s2),
        ("Phao Sọc Vàng Trắng", s3),
        ("Gối Tay Nổi Chill", s4),
        ("Thư Thái Hồ Nắng!", s5),
    ]


# =========================================================================== #
#  #67 — LOOPY FLUFFY COMMUTER DIARY (DYNAMIC: SLEEPY -> STRAP -> WALK -> COFFEE -> SHRUG -> JUMP!)
# =========================================================================== #
def _fluffy_white_hood(cx=150, cy=124, smiley=True, rot=0) -> str:
    parts = [f'<g transform="translate({cx},{cy}) rotate({rot})">']
    parts.append(
        '<circle cx="-46" cy="-76" r="24" fill="#FFFFFF" stroke="#5C343A" stroke-width="4.0"/>'
        '<ellipse cx="-46" cy="-74" rx="12" ry="13" fill="#F29EB0" stroke="#5C343A" stroke-width="2.2"/>'
        '<circle cx="46" cy="-76" r="24" fill="#FFFFFF" stroke="#5C343A" stroke-width="4.0"/>'
        '<ellipse cx="46" cy="-74" rx="12" ry="13" fill="#F29EB0" stroke="#5C343A" stroke-width="2.2"/>'
        '<path d="M -82,4 C -88,-42 -58,-72 0,-72 C 58,-72 88,-42 82,4 C 84,48 48,66 10,60 C 4,56 -4,56 -10,60 C -48,66 -84,48 -82,4 Z" fill="#FFFFFF" stroke="#5C343A" stroke-width="4.2"/>'
    )
    if smiley:
        parts.append(
            '<circle cx="-13" cy="-38" r="3.2" fill="#4BA3E3"/><circle cx="13" cy="-38" r="3.2" fill="#4BA3E3"/>'
            '<path d="M -4,-34 Q 0,-30 4,-34" fill="none" stroke="#E27D8E" stroke-width="2.4" stroke-linecap="round"/>'
            '<ellipse cx="-26" cy="-29" rx="8" ry="4.5" fill="#F9C5D1"/><ellipse cx="26" cy="-29" rx="8" ry="4.5" fill="#F9C5D1"/>'
        )
    parts.append(f'<ellipse cx="0" cy="14" rx="52" ry="43" fill="{PINK}" stroke="#5C343A" stroke-width="3.2"/>')
    parts.append("</g>")
    return "".join(parts)


def _crossbody_bag(cx=150, cy=218, rot=0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot})">'
        f'<path d="M -30,-32 L 24,18 L 14,28 L -40,-24 Z" fill="#4E3A32" stroke="#2D1E19" stroke-width="2.8"/>'
        f'<rect x="14" y="6" width="44" height="38" rx="9" fill="#5D443B" stroke="#2D1E19" stroke-width="3.2"/>'
        f'<path d="M 14,16 Q 36,28 58,16" fill="none" stroke="#2D1E19" stroke-width="2.8"/>'
        f'<rect x="31" y="18" width="10" height="8" rx="2" fill="#D4A373" stroke="#2D1E19" stroke-width="1.8"/>'
        f'</g>'
    )


def _coffee_cup(cx=86, cy=206) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate(-10)">'
        f'<path d="M -12,-14 L 12,-14 L 9,16 L -9,16 Z" fill="#FFF8EC" stroke="#5C343A" stroke-width="2.6" stroke-linejoin="round"/>'
        f'<rect x="-14" y="-19" width="28" height="7" rx="3" fill="#B87D4B" stroke="#5C343A" stroke-width="2.2"/>'
        f'<rect x="-10" y="-3" width="20" height="10" fill="#D4B499"/>'
        f'</g>'
    )


def build_67_fluffy_commuter() -> list[tuple[str, Image.Image]]:
    # S0: Sitting sleepy pulling on white hood
    s0 = render_svg(
        shadow() + loopy_body(150, 222, pose="sit", paws="down", lean=-8)
        + _fluffy_white_hood(144, 128, smiley=False, rot=-10)
        + loopy_head(144, 144, scale=0.78, expr="sleepy", show_ears=False, show_tuft=False, head_outline=False, rot=-10)
    )
    # S1: Slinging brown leather strap over shoulder adjusting hood!
    s1 = render_svg(
        shadow() + loopy_body(150, 218, pose="stand", paws="none", lean=4)
        + _crossbody_bag(150, 218, rot=4)
        + _fluffy_white_hood(152, 124, smiley=True, rot=6)
        + loopy_head(152, 140, scale=0.78, expr="curious", show_ears=False, show_tuft=False, head_outline=False, rot=6)
        + f'<ellipse cx="96" cy="176" rx="16" ry="11" transform="rotate(-24 96 176)" fill="{PINK}" stroke="{OL}" stroke-width="3.6"/>'
    )
    # S2: Dynamic mid-stride walking forward confidently!
    s2 = render_svg(
        shadow(150, 268, 66, 9)
        + loopy_body(150, 216, pose="walk", paws="walk_swing", lean=9)
        + _crossbody_bag(152, 216, rot=9)
        + _fluffy_white_hood(156, 122, smiley=True, rot=8)
        + loopy_head(156, 138, scale=0.78, expr="focused", show_ears=False, show_tuft=False, head_outline=False, rot=8)
        + '<path d="M 46,238 L 68,238 M 54,250 L 72,250" stroke="#D4B499" stroke-width="3.2" stroke-linecap="round"/>'
    )
    # S3: Walking cheerfully holding warm coffee/tea cup!
    s3 = render_svg(
        shadow(150, 268, 66, 9)
        + loopy_body(150, 216, pose="walk", paws="down", lean=-5)
        + _crossbody_bag(148, 216, rot=-5)
        + _coffee_cup(82, 206)
        + _fluffy_white_hood(146, 122, smiley=True, rot=-6)
        + loopy_head(146, 138, scale=0.78, expr="smile", strong_blush=True, blush_hatch=True, show_ears=False, show_tuft=False, head_outline=False, rot=-6)
    )
    # S4: Clocking out shrugging happily under warm golden stars!
    s4 = render_svg(
        '<circle cx="150" cy="150" r="118" fill="#FEF6D8"/><circle cx="150" cy="150" r="92" fill="#FDEBB8"/>'
        + shadow() + loopy_body(150, 216, pose="stand", paws="shrug", lean=6)
        + _crossbody_bag(152, 216, rot=6)
        + _fluffy_white_hood(154, 122, smiley=True, rot=8)
        + loopy_head(154, 138, scale=0.78, expr="wink", strong_blush=True, blush_hatch=True, show_ears=False, show_tuft=False, head_outline=False, rot=8)
        + star5(50, 112, r=12) + star5(250, 124, r=14)
    )
    # S5: Jumping high celebrating clock-out with light bag & golden stars!
    s5 = with_hero_aura(render_svg(
        '<circle cx="150" cy="150" r="120" fill="#FEF6D8"/><circle cx="150" cy="150" r="94" fill="#FDEBB8"/>'
        + shadow(150, 272, 52, 7, op=0.12)
        + loopy_body(150, 204, pose="jump", paws="wide_up")
        + _crossbody_bag(150, 204, rot=-6)
        + _fluffy_white_hood(150, 114, smiley=True, rot=-5)
        + loopy_head(150, 130, scale=0.78, expr="big_smile", strong_blush=True, blush_hatch=True, show_ears=False, show_tuft=False, head_outline=False, rot=-5)
        + star5(46, 102, r=13) + star5(254, 118, r=15) + sp4(56, 178, r=10) + sp4(248, 62, r=11)
    ), (253, 231, 169))
    return [
        ("Ngái Ngủ Trùm Mũ", s0),
        ("Khoác Túi Chỉnh Trang", s1),
        ("Bước Đi Tự Tin", s2),
        ("Cầm Cà Phê Cười Tươi", s3),
        ("Nhún Vai Tan Làm", s4),
        ("Bật Nhảy Đúng Giờ!", s5),
    ]


# =========================================================================== #
#  #68 — LOOPY PANDA ZEN STUDY (SCRATCH HEAD -> BULB -> WRITE -> READ -> CHECKLIST -> ZEN!)
# =========================================================================== #
def _panda_hood(cx=150, cy=124, sprout=False, perked=False, rot=0) -> str:
    ear_dy = -6 if perked else 0
    parts = [f'<g transform="translate({cx},{cy}) rotate({rot})">']
    if sprout:
        parts.append(
            f'<path d="M 0,-64 C -6,-82 -14,-90 -8,-94 C -3,-97 1,-84 0,-68 Z" fill="#F48A9E" stroke="{OL}" stroke-width="2.6"/>'
            f'<path d="M 0,-64 C 4,-80 12,-88 8,-92 C 3,-94 -1,-82 0,-66 Z" fill="#F48A9E" stroke="{OL}" stroke-width="2.6"/>'
        )
    parts.append(
        '<path d="M -68,14 C -84,48 -88,82 -76,94 C -62,96 -52,66 -54,32 Z" fill="#FFFFFF" stroke="#363B42" stroke-width="3.8"/>'
        '<path d="M 68,14 C 84,48 88,82 76,94 C 62,96 52,66 54,32 Z" fill="#FFFFFF" stroke="#363B42" stroke-width="3.8"/>'
        f'<circle cx="-54" cy="{-52 + ear_dy}" r="26" fill="#FFFFFF" stroke="#363B42" stroke-width="4.0"/>'
        f'<circle cx="-54" cy="{-50 + ear_dy}" r="15" fill="#3C4148"/>'
        f'<circle cx="54" cy="{-52 + ear_dy}" r="26" fill="#FFFFFF" stroke="#363B42" stroke-width="4.0"/>'
        f'<circle cx="54" cy="{-50 + ear_dy}" r="15" fill="#3C4148"/>'
        '<path d="M -72,4 C -74,-44 -42,-66 0,-66 C 42,-66 74,-44 72,4 C 72,44 46,58 0,58 C -46,58 -72,44 -72,4 Z" fill="#FFFFFF" stroke="#363B42" stroke-width="4.2"/>'
        '<ellipse cx="-24" cy="-36" rx="16" ry="11" transform="rotate(-24 -24 -36)" fill="#3C4148"/>'
        '<ellipse cx="24" cy="-36" rx="16" ry="11" transform="rotate(24 24 -36)" fill="#3C4148"/>'
        '<ellipse cx="0" cy="-26" rx="4.2" ry="2.6" fill="#3C4148"/>'
        '<ellipse cx="-42" cy="-24" rx="7" ry="4" fill="#FBCFE8"/><ellipse cx="42" cy="-24" rx="7" ry="4" fill="#FBCFE8"/>'
        f'<ellipse cx="0" cy="14" rx="52" ry="42" fill="{PINK}" stroke="#363B42" stroke-width="3.0"/>'
        '</g>'
    )
    return "".join(parts)


def _ruffled_collar(cx=150, cy=188, sit=False, lean=0) -> str:
    feet = (
        f'<ellipse cx="-32" cy="64" rx="19" ry="15" transform="rotate(-14 -32 64)" fill="{PAW}" stroke="{OL}" stroke-width="3.4"/>'
        f'<ellipse cx="32" cy="64" rx="19" ry="15" transform="rotate(14 32 64)" fill="{PAW}" stroke="{OL}" stroke-width="3.4"/>'
        if sit else
        f'<ellipse cx="-24" cy="70" rx="19" ry="11" fill="{PAW}" stroke="{OL}" stroke-width="3.6"/>'
        f'<ellipse cx="24" cy="70" rx="19" ry="11" fill="{PAW}" stroke="{OL}" stroke-width="3.6"/>'
    )
    return (
        f'<g transform="translate({cx},{cy}) rotate({lean})">'
        f'{feet}'
        f'<path d="M -46,-14 C -54,28 -38,68 0,68 C 38,68 54,28 46,-14 Z" fill="#3C4148" stroke="#25282E" stroke-width="3.8"/>'
        f'<path d="M -40,-10 Q -30,12 -18,2 Q -8,15 0,4 Q 8,15 18,2 Q 30,12 40,-10 Z" fill="#FFFFFF" stroke="#363B42" stroke-width="3.0"/>'
        f'</g>'
    )


def _mint_book(cx=150, cy=238, closed=False) -> str:
    if closed:
        return (
            f'<g transform="translate({cx},{cy}) rotate(-8)">'
            f'<rect x="-28" y="-14" width="56" height="26" rx="5" fill="#87BFA1" stroke="#363B42" stroke-width="2.8"/>'
            f'<line x1="-20" y1="-4" x2="20" y2="-4" stroke="#FFFFFF" stroke-width="2.4" stroke-linecap="round"/>'
            f'</g>'
        )
    return (
        f'<g transform="translate({cx},{cy})">'
        f'<path d="M -38,-10 L 0,-4 L 0,24 L -38,18 Z" fill="#B8DEC9" stroke="#363B42" stroke-width="2.8"/>'
        f'<path d="M 38,-10 L 0,-4 L 0,24 L 38,18 Z" fill="#E6F5EC" stroke="#363B42" stroke-width="2.8"/>'
        f'<line x1="-28" y1="2" x2="-8" y2="5" stroke="#4E545C" stroke-width="2.0"/>'
        f'<line x1="8" y1="5" x2="28" y2="2" stroke="#4E545C" stroke-width="2.0"/>'
        f'</g>'
    )


def _lightbulb(cx=238, cy=74) -> str:
    return (
        f'<g transform="translate({cx},{cy})">'
        f'<circle cx="0" cy="0" r="16" fill="#FEF08A" stroke="#D97706" stroke-width="2.6"/>'
        f'<rect x="-7" y="14" width="14" height="8" rx="3" fill="#CBD5E1" stroke="#475569" stroke-width="2.2"/>'
        f'<path d="M 0,-26 L 0,-20 M -22,-10 L -17,-6 M 22,-10 L 17,-6" stroke="#F59E0B" stroke-width="2.8" stroke-linecap="round"/>'
        f'</g>'
    )


def _checklist_card(cx=236, cy=188) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate(8)">'
        f'<rect x="-22" y="-28" width="44" height="56" rx="6" fill="#FFFFFF" stroke="#363B42" stroke-width="2.8"/>'
        f'<path d="M -14,-14 L -9,-9 L -2,-18 M -14,0 L -9,5 L -2,-4 M -14,14 L -9,19 L -2,10" fill="none" stroke="#16A34A" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<line x1="3" y1="-13" x2="15" y2="-13" stroke="#94A3B8" stroke-width="2.4"/><line x1="3" y1="1" x2="15" y2="1" stroke="#94A3B8" stroke-width="2.4"/><line x1="3" y1="15" x2="15" y2="15" stroke="#94A3B8" stroke-width="2.4"/>'
        f'</g>'
    )


def _bamboo_aura() -> str:
    return (
        '<circle cx="150" cy="150" r="120" fill="#E4F5EC"/><circle cx="150" cy="150" r="92" fill="#CDEBD9"/>'
        '<ellipse cx="46" cy="112" rx="16" ry="6" transform="rotate(-35 46 112)" fill="#7EC49E" stroke="#3E7A5B" stroke-width="2.2"/>'
        '<ellipse cx="58" cy="130" rx="13" ry="5" transform="rotate(-12 58 130)" fill="#9CD6B5" stroke="#3E7A5B" stroke-width="2.0"/>'
        '<ellipse cx="254" cy="108" rx="16" ry="6" transform="rotate(35 254 108)" fill="#7EC49E" stroke="#3E7A5B" stroke-width="2.2"/>'
        '<ellipse cx="242" cy="126" rx="13" ry="5" transform="rotate(14 242 126)" fill="#9CD6B5" stroke="#3E7A5B" stroke-width="2.0"/>'
    )


def build_68_panda_study() -> list[tuple[str, Image.Image]]:
    # S0: Propping chin / scratching head puzzled over open notebook!
    s0 = render_svg(
        shadow() + _ruffled_collar(150, 192, sit=True, lean=-8)
        + _panda_hood(144, 126, sprout=False, rot=-10)
        + loopy_head(144, 142, scale=0.78, expr="puzzled", show_ears=False, show_tuft=False, head_outline=False, rot=-10)
        + f'<ellipse cx="196" cy="170" rx="16" ry="12" transform="rotate(24 196 170)" fill="{PINK}" stroke="{OL}" stroke-width="3.6"/>'
        + _mint_book(146, 240, closed=False)
    )
    # S1: Pink sprout shoots up + glowing lightbulb eureka!
    s1 = render_svg(
        shadow() + _ruffled_collar(150, 190, sit=True, lean=5)
        + _panda_hood(152, 124, sprout=True, rot=6)
        + loopy_head(152, 140, scale=0.78, expr="curious", show_ears=False, show_tuft=False, head_outline=False, rot=6)
        + _lightbulb(242, 76)
    )
    # S2: Sitting neatly holding pen writing focused notes!
    s2 = render_svg(
        shadow() + _ruffled_collar(150, 190, sit=True)
        + _panda_hood(150, 124, sprout=True)
        + loopy_head(150, 140, scale=0.78, expr="focused", show_ears=False, show_tuft=False, head_outline=False)
        + _mint_book(150, 238, closed=False)
        + '<line x1="172" y1="226" x2="206" y2="200" stroke="#3B82F6" stroke-width="5.2" stroke-linecap="round"/>'
        + f'<ellipse cx="190" cy="214" rx="14" ry="10" fill="{PINK}" stroke="{OL}" stroke-width="3.4"/>'
    )
    # S3: Reading calmly beside fresh green bamboo aura!
    s3 = render_svg(
        _bamboo_aura() + shadow() + _ruffled_collar(150, 190, sit=True, lean=-4)
        + _panda_hood(148, 124, sprout=True, rot=-4)
        + loopy_head(148, 140, scale=0.78, expr="calm_closed", blush_hatch=True, show_ears=False, show_tuft=False, head_outline=False, rot=-4)
        + _mint_book(148, 236, closed=False)
    )
    # S4: Holding up nearly completed checklist excitedly!
    s4 = render_svg(
        _bamboo_aura() + shadow() + _ruffled_collar(142, 188, sit=False, lean=6)
        + _panda_hood(146, 124, sprout=True, perked=True, rot=8)
        + loopy_head(146, 140, scale=0.78, expr="smile", strong_blush=True, blush_hatch=True, show_ears=False, show_tuft=False, head_outline=False, rot=8)
        + _checklist_card(236, 184)
        + sp4(56, 76, r=10, fill="#B8DEC9", stroke="#3E7A5B")
    )
    # S5: Closing book beaming with full zen satisfaction & sparkles!
    s5 = with_hero_aura(render_svg(
        _bamboo_aura() + shadow() + _ruffled_collar(150, 186, sit=False)
        + _panda_hood(150, 122, sprout=True, perked=True, rot=-4)
        + loopy_head(150, 138, scale=0.78, expr="happy_squint", strong_blush=True, blush_hatch=True, show_ears=False, show_tuft=False, head_outline=False, rot=-4)
        + _mint_book(150, 236, closed=True)
        + sp4(50, 68, r=12) + sp4(250, 68, r=12) + sp4(250, 200, r=9, fill="#B8DEC9", stroke="#3E7A5B")
    ), (184, 222, 201))
    return [
        ("Chống Cằm Bối Rối", s0),
        ("Bóng Đèn Ý Tưởng!", s1),
        ("Cầm Bút Ghi Chép", s2),
        ("Đọc Sách Trúc Xanh", s3),
        ("Giơ Bảng Checklist", s4),
        ("Khép Sách Mãn Nguyện!", s5),
    ]


# =========================================================================== #
#  #69 — LOOPY RUFFLE SLEEP ROUTINE (DYNAMIC COZY BEDTIME STORY!)
# =========================================================================== #
def _pink_blanket_bed(cy=224) -> str:
    return (
        f'<path d="M 36,{cy + 20} C 26,{cy - 8} 74,{cy - 26} 150,{cy - 22} C 226,{cy - 26} 274,{cy - 8} 264,{cy + 22} '
        f'C 254,268 188,274 150,270 C 112,274 46,268 36,{cy + 20} Z" fill="#FFD6E4" stroke="{OL}" stroke-width="3.6"/>'
        f'<circle cx="76" cy="244" r="3.5" fill="#FFFFFF"/><circle cx="122" cy="252" r="3.5" fill="#FFFFFF"/>'
        f'<circle cx="176" cy="250" r="3.5" fill="#FFFFFF"/><circle cx="222" cy="242" r="3.5" fill="#FFFFFF"/>'
    )


def _ruffled_pillow(cx=184, cy=160) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate(12)">'
        f'<path d="M -58,-28 Q -68,-12 -58,4 Q -68,20 -54,32 Q -36,44 -16,38 Q 4,46 24,38 Q 44,44 58,28 '
        f'Q 68,12 58,-4 Q 68,-20 52,-32 Q 34,-44 14,-36 Q -6,-46 -26,-36 Q -44,-42 -58,-28 Z" fill="#FFFFFF" stroke="#8C6B74" stroke-width="2.8"/>'
        f'<ellipse cx="0" cy="0" rx="46" ry="32" fill="#FFE8F0" stroke="#E892AC" stroke-width="2.2"/>'
        f'</g>'
    )


def _canopy_bow() -> str:
    return (
        '<path d="M 28,242 C 74,200 106,154 116,96 C 148,108 214,102 268,78" fill="none" stroke="#FFFDF5" stroke-width="18" stroke-linecap="round"/>'
        '<path d="M 28,242 C 74,200 106,154 116,96 C 148,108 214,102 268,78" fill="none" stroke="#8C6B74" stroke-width="3.2" stroke-linecap="round"/>'
        '<g transform="translate(136,76) rotate(-14)">'
        '<path d="M -2,4 L -18,36 L -4,30 L 2,38 L 6,6 Z M 4,4 L 18,34 L 28,24 L 12,4 Z" fill="#F8B4C8" stroke="#5C343A" stroke-width="2.6"/>'
        '<path d="M -2,2 C -26,-20 -46,-6 -36,12 C -28,22 -12,14 -2,6 Z M 4,2 C 28,-20 48,-6 38,12 C 30,22 14,14 4,6 Z" fill="#F8B4C8" stroke="#5C343A" stroke-width="2.8"/>'
        '<ellipse cx="1" cy="4" rx="7" ry="6.5" fill="#F49CB5" stroke="#5C343A" stroke-width="2.6"/>'
        '</g>'
    )


def _sleeping_loopy(expr="calm_closed", bubble=False) -> str:
    parts = [
        f'<g transform="translate(138,208) rotate(-26)">'
        f'<ellipse cx="0" cy="0" rx="44" ry="34" fill="{PINK}" stroke="{OL}" stroke-width="3.8"/>'
        f'<ellipse cx="4" cy="6" rx="22" ry="18" fill="{CREAM}"/>'
        f'<ellipse cx="-42" cy="10" rx="14" ry="9" fill="{PAW}" stroke="{OL}" stroke-width="3.0"/>'
        f'<ellipse cx="-32" cy="24" rx="14" ry="9" fill="{PAW}" stroke="{OL}" stroke-width="3.0"/>'
        f'<ellipse cx="2" cy="14" rx="16" ry="11" fill="{PINK}" stroke="{OL}" stroke-width="3.4"/></g>',
        f'<g transform="translate(184,166) rotate(18)">' + loopy_head(0, 0, scale=0.78, expr=expr, strong_blush=True, show_tuft=False) + '</g>',
    ]
    if bubble:
        parts.append(
            '<ellipse cx="198" cy="190" rx="12" ry="9" transform="rotate(-12 198 190)" fill="#E0F2FE" stroke="#60A5FA" stroke-width="2.4"/>'
            '<ellipse cx="195" cy="188" rx="3.5" ry="2" fill="#FFFFFF"/>'
        )
    return "".join(parts)


def build_69_ruffle_sleep() -> list[tuple[str, Image.Image]]:
    s0 = render_svg(
        _pink_blanket_bed() + ditsy_flower(56, 62, 7) + ditsy_flower(244, 68, 7)
        + loopy_body(150, 200, pose="sit", paws="wide_up", lean=6)
        + loopy_head(154, 118, scale=0.90, expr="curious", rot=10)
    )
    s1 = render_svg(
        _pink_blanket_bed() + _canopy_bow()
        + loopy_body(168, 206, pose="sit", paws="wave_r", lean=-8)
        + loopy_head(164, 128, scale=0.84, expr="smile", rot=-8)
    )
    s2 = render_svg(_pink_blanket_bed() + _ruffled_pillow(184, 162) + _sleeping_loopy(expr="sleepy", bubble=False))
    s3 = render_svg(_pink_blanket_bed() + _ruffled_pillow(184, 162) + _sleeping_loopy(expr="calm_closed", bubble=False))
    s4 = render_svg(_pink_blanket_bed() + _ruffled_pillow(184, 162) + _sleeping_loopy(expr="calm_closed", bubble=True) + _z_vec(218, 86, 1.05))
    s5 = with_hero_aura(render_svg(
        _pink_blanket_bed() + _canopy_bow() + _ruffled_pillow(192, 168)
        + '<g transform="translate(8,6)">' + _sleeping_loopy(expr="calm_closed", bubble=True) + '</g>'
        + ditsy_flower(56, 62, 8) + ditsy_flower(96, 124, 7) + ditsy_flower(252, 54, 8)
        + _z_vec(210, 102, 0.72) + _z_vec(226, 84, 0.92) + _z_vec(244, 64, 1.12)
    ), (232, 146, 172))
    return [
        ("Chưa Chịu Ngủ", s0),
        ("Kéo Rèm Nơ Hồng", s1),
        ("Nằm Gối Lim Dim", s2),
        ("Nhắm Mắt Êm Ái", s3),
        ("Bong Bóng Ngủ Ngon", s4),
        ("Giấc Mơ Hoa Zzz!", s5),
    ]


# =========================================================================== #
#  #70 NEW — LOOPY HAIR ROLLER GRWM (ICONIC BLACK HAIR + GIANT PINK ROLLER MEME!)
# =========================================================================== #
def _black_long_hair_back(cx=150, cy=140, rot=0) -> str:
    """Flowing sleek dark charcoal-black hair behind Loopy (matches the viral meme!)."""
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot})">'
        f'<path d="M -68,-26 C -74,-66 -38,-84 0,-84 C 38,-84 74,-66 68,-26 '
        f'C 84,26 88,88 76,126 C 60,132 46,126 42,102 L -42,102 '
        f'C -46,126 -60,132 -76,126 C -88,88 -84,26 -68,-26 Z" '
        f'fill="#2A2026" stroke="#181216" stroke-width="3.8" stroke-linejoin="round"/>'
        # Glossy hair sheen streaks
        f'<path d="M -62,22 Q -68,66 -62,106 M 62,22 Q 68,66 62,106" fill="none" stroke="#4D3D46" stroke-width="4.5" stroke-linecap="round"/>'
        f'</g>'
    )


def _pink_hair_roller(cx=150, cy=78, rot=-8, s=1.0) -> str:
    """Giant iconic pink velcro hair roller across bangs!"""
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot}) scale({s})">'
        f'<rect x="-42" y="-22" width="84" height="44" rx="14" fill="#F48FB1" stroke="{OL}" stroke-width="3.4"/>'
        f'<ellipse cx="40" cy="0" rx="10" ry="21" fill="#FCE7F3" stroke="{OL}" stroke-width="2.8"/>'
        f'<ellipse cx="40" cy="0" rx="5" ry="12" fill="#D8B4C6"/>'
        # Roller velcro texture ribs
        f'<line x1="-26" y1="-20" x2="-26" y2="20" stroke="#C94E78" stroke-width="2.6" stroke-dasharray="5,4"/>'
        f'<line x1="-12" y1="-20" x2="-12" y2="20" stroke="#C94E78" stroke-width="2.6" stroke-dasharray="5,4"/>'
        f'<line x1="2" y1="-20" x2="2" y2="20" stroke="#C94E78" stroke-width="2.6" stroke-dasharray="5,4"/>'
        f'<line x1="16" y1="-20" x2="16" y2="20" stroke="#C94E78" stroke-width="2.6" stroke-dasharray="5,4"/>'
        f'</g>'
    )


def _bouncy_bangs(cx=150, cy=80, rot=0, clip=False) -> str:
    parts = [
        f'<g transform="translate({cx},{cy}) rotate({rot})">'
        f'<path d="M -54,18 C -46,-18 46,-18 54,18 C 36,2 18,12 4,2 C -8,14 -34,4 -54,18 Z" fill="#2A2026" stroke="#181216" stroke-width="2.8"/>'
    ]
    if clip:
        parts.append(
            f'<g transform="translate(36,-6) rotate(16)">'
            f'<path d="M -2,2 C -14,-10 -22,-2 -16,6 C -10,12 -3,8 -2,4 Z M 2,2 C 14,-10 22,-2 16,6 C 10,12 3,8 2,4 Z" fill="#F472B6" stroke="{OL}" stroke-width="2.2"/>'
            f'<circle cx="0" cy="3" r="4.5" fill="#FBCFE8" stroke="{OL}" stroke-width="2.0"/></g>'
        )
    parts.append("</g>")
    return "".join(parts)


def _hand_mirror(cx=232, cy=196, rot=14) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot})">'
        f'<rect x="-5" y="18" width="10" height="30" rx="5" fill="#F48FB1" stroke="{OL}" stroke-width="2.6"/>'
        f'<ellipse cx="0" cy="0" rx="22" ry="26" fill="#F48FB1" stroke="{OL}" stroke-width="3.0"/>'
        f'<ellipse cx="0" cy="0" rx="16" ry="20" fill="#E0F2FE" stroke="#FFFFFF" stroke-width="2.0"/>'
        f'<line x1="-8" y1="-8" x2="6" y2="6" stroke="#FFFFFF" stroke-width="3.0" stroke-linecap="round"/>'
        f'</g>'
    )


def build_70_hair_roller() -> list[tuple[str, Image.Image]]:
    # S0: Hilarious deadpan half-lidded sleepy Loopy with sleek black hair & giant pink roller on forehead!
    s0 = render_svg(
        shadow() + _black_long_hair_back(150, 146)
        + loopy_body(150, 220, pose="sit", paws="down")
        + loopy_head(150, 134, expr="deadpan", show_tuft=False)
        + _pink_hair_roller(150, 80, rot=-6, s=1.06)
    )
    # S1: Still wearing pink roller, sipping warm mug of tea/coffee to wake up!
    s1 = render_svg(
        shadow() + _black_long_hair_back(150, 146, rot=-4)
        + loopy_body(150, 220, pose="sit", paws="center", lean=-4)
        + loopy_head(148, 134, expr="sleepy", show_tuft=False, rot=-4)
        + _pink_hair_roller(144, 80, rot=-10, s=1.02)
        + '<g transform="translate(178,202)"><rect x="-15" y="-14" width="30" height="28" rx="7" fill="#FFFDF5" stroke="#5C343A" stroke-width="2.8"/><path d="M 15,-6 Q 24,-6 24,2 Q 24,10 15,10" fill="none" stroke="#5C343A" stroke-width="2.8"/><path d="M -5,-22 Q -9,-28 -4,-34 M 5,-22 Q 1,-28 6,-34" fill="none" stroke="#F48FB1" stroke-width="2.4" stroke-linecap="round"/></g>'
    )
    # S2: Dabbing blush/skincare on cheek before small hand mirror, waking up bright!
    s2 = render_svg(
        shadow() + _black_long_hair_back(144, 146, rot=5)
        + loopy_body(144, 218, pose="sit", paws="none", lean=5)
        + loopy_head(146, 134, expr="curious", strong_blush=True, show_tuft=False, rot=5)
        + _pink_hair_roller(150, 80, rot=-2, s=1.0)
        + f'<ellipse cx="102" cy="166" rx="16" ry="12" transform="rotate(-24 102 166)" fill="{PINK}" stroke="{OL}" stroke-width="3.6"/>'
        + '<circle cx="114" cy="158" r="7" fill="#FCE7F3" stroke="#D96B8D" stroke-width="2.0"/>'
        + _hand_mirror(234, 198, rot=14)
    )
    # S3: Both paws eagerly unrolling the giant pink roller off bangs!
    s3 = render_svg(
        shadow() + _black_long_hair_back(150, 146)
        + loopy_body(150, 218, pose="stand", paws="none")
        + loopy_head(150, 136, expr="smile", strong_blush=True, show_tuft=False)
        + _pink_hair_roller(150, 62, rot=-14, s=1.02)
        + f'<ellipse cx="96" cy="76" rx="16" ry="11" transform="rotate(-36 96 76)" fill="{PINK}" stroke="{OL}" stroke-width="3.6"/>'
        + f'<ellipse cx="204" cy="64" rx="16" ry="11" transform="rotate(36 204 64)" fill="{PINK}" stroke="{OL}" stroke-width="3.6"/>'
        + sp4(56, 72, r=9)
    )
    # S4: Bouncy bangs pop out perfectly! Winking into hand mirror!
    s4 = render_svg(
        shadow() + _black_long_hair_back(144, 146, rot=-6)
        + loopy_body(144, 218, pose="stand", paws="wave_r", lean=-5)
        + loopy_head(142, 134, expr="wink", strong_blush=True, blush_hatch=True, show_tuft=False, rot=-6)
        + _bouncy_bangs(138, 86, rot=-6, clip=False)
        + _hand_mirror(234, 192, rot=16)
        + sp4(54, 96, r=10) + sp4(236, 98, r=9)
    )
    # S5: Sleek shiny black hair with cute pink ribbon hairclip, beaming radiant GRWM 100%!
    s5 = with_hero_aura(render_svg(
        shadow(150, 272, 56, 8, op=0.12)
        + _black_long_hair_back(150, 138, rot=4)
        + loopy_body(150, 208, pose="jump", paws="wide_up")
        + loopy_head(150, 126, expr="big_smile", strong_blush=True, blush_hatch=True, show_tuft=False, rot=4)
        + _bouncy_bangs(152, 78, rot=4, clip=True)
        + sp4(50, 84, r=12) + sp4(250, 84, r=12) + heart(52, 196, s=12, fill="#F7B4C9", stroke="#D96B8D")
        + heart(248, 194, s=11, fill="#D96B8D", stroke=OL)
    ), (217, 107, 141))
    return [
        ("Lô Cuốn Mái Ngái Ngủ", s0),
        ("Nhấp Trà Tỉnh Hồn", s1),
        ("Chấm Má Hồng Xinh", s2),
        ("Tháo Lô Cuốn Mái", s3),
        ("Mái Bồng Soi Gương", s4),
        ("Xinh Lung Linh GRWM!", s5),
    ]


# =========================================================================== #
#  MAIN GENERATOR + CONTACT SHEET (`previews/assets_contact_sheet_loopy.png`)
# =========================================================================== #
def main():
    builders = [
        ("loopy_red_bow",         build_61_red_bow),
        ("loopy_taiyaki",         build_62_taiyaki),
        ("loopy_piggy_cafe",      build_63_piggy_cafe),
        ("loopy_sauna_sheep",     build_64_sauna_sheep),
        ("loopy_honey_bee",       build_65_honey_bee),
        ("loopy_poolside_duck",   build_66_poolside_duck),
        ("loopy_fluffy_commuter", build_67_fluffy_commuter),
        ("loopy_panda_study",     build_68_panda_study),
        ("loopy_ruffle_sleep",    build_69_ruffle_sleep),
        ("loopy_hair_roller",     build_70_hair_roller),
    ]

    results: dict[str, list[tuple[str, Image.Image]]] = {}
    hashes: set[str] = set()
    total = 0

    for slug, fn in builders:
        stages = fn()
        assert len(stages) == 6
        d = ASSETS_DIR / slug
        d.mkdir(parents=True, exist_ok=True)
        for i, (_, im) in enumerate(stages):
            assert im.size == (300, 300) and im.mode == "RGBA"
            alpha_pixels = sum(1 for a in im.getchannel("A").getdata() if a > 10)
            assert alpha_pixels > 2500, f"Sprite too empty: {slug}/stage_{i}.png"
            out_p = d / f"stage_{i}.png"
            im.save(out_p, "PNG", optimize=True)
            h = hashlib.sha256(out_p.read_bytes()).hexdigest()
            assert h not in hashes, f"DUPLICATE SPRITE: {slug}/stage_{i}.png"
            hashes.add(h)
            total += 1
        results[slug] = stages
        print(f"  [LOOPY v4] {slug:24s} -> 6 dynamic unique 300x300 RGBA PNGs saved")

    print(f"Total Loopy sprites saved: {total}/60 (100% unique SHA-256 hashes!)")

    rows = [
        ("61. Red Bow Glow-Up",      "loopy_red_bow",         (255, 248, 234), (216, 90, 104)),
        ("62. Taiyaki Street Snack", "loopy_taiyaki",         (255, 249, 238), (201, 130, 62)),
        ("63. Piggy Dessert Cafe",   "loopy_piggy_cafe",      (255, 253, 240), (227, 115, 152)),
        ("64. Sauna Sheep Detox",    "loopy_sauna_sheep",     (253, 246, 233), (182, 123, 79)),
        ("65. Honey Bee KPI",        "loopy_honey_bee",       (255, 253, 242), (212, 155, 39)),
        ("66. Poolside Duck Chill",  "loopy_poolside_duck",   (242, 251, 255), (63, 167, 206)),
        ("67. Fluffy Commuter",      "loopy_fluffy_commuter", (255, 251, 242), (123, 91, 76)),
        ("68. Panda Zen Study",      "loopy_panda_study",     (247, 251, 249), (63, 72, 80)),
        ("69. Ruffle Sleep Routine", "loopy_ruffle_sleep",    (253, 251, 233), (201, 113, 146)),
        ("70. Hair Roller GRWM",     "loopy_hair_roller",     (255, 247, 250), (217, 107, 141)),
    ]

    cell_w, cell_h = 204, 272
    left_w, pad, hdr_h = 248, 18, 84
    W = pad * 2 + left_w + cell_w * 6
    H = pad * 2 + hdr_h + cell_h * len(rows)

    sheet = Image.new("RGB", (W, H), (255, 249, 250))
    draw = ImageDraw.Draw(sheet)
    try:
        f_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 27)
        f_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 15.5)
        f_row = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 15)
        f_lbl = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 13)
        f_tiny = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 11)
    except Exception:
        f_title = f_sub = f_row = f_lbl = f_tiny = ImageFont.load_default()

    draw.rectangle([0, 0, W, hdr_h], fill=(216, 90, 104))
    draw.text((pad, 14), "LOOPY PASTEL COLLECTION — #61–#70 (DYNAMIC ANTI-STIFFNESS • 60 UNIQUE SPRITES)", fill=(255, 255, 255), font=f_title)
    draw.text((pad, 50), "Expressive Meme Loopy Poses 0% -> 100% • New #70 Hair Roller GRWM • Transparent 300x300 RGBA • 162px + 44px Sheet Preview", fill=(255, 248, 234), font=f_sub)

    pcts = ["0%", "20%", "40%", "60%", "80%", "100% MAX"]
    for r_i, (title, slug, bg_c, acc_c) in enumerate(rows):
        y0 = hdr_h + pad + r_i * cell_h
        draw.rounded_rectangle([pad, y0 + 4, W - pad, y0 + cell_h - 6], radius=14, fill=bg_c, outline=acc_c, width=2)
        draw.text((pad + 14, y0 + 114), title, fill=acc_c, font=f_row)
        for s_i, (lbl, im) in enumerate(results[slug]):
            x0 = pad + left_w + s_i * cell_w
            is_f = (s_i == 5)
            draw.rounded_rectangle(
                [x0 + 6, y0 + 12, x0 + cell_w - 6, y0 + cell_h - 14],
                radius=10, fill=(255, 255, 255),
                outline=(acc_c if is_f else (235, 224, 226)), width=2 if is_f else 1,
            )
            big = im.resize((162, 162), Image.LANCZOS)
            sheet.paste(big, (x0 + (cell_w - 162) // 2, y0 + 16), big)

            small = im.resize((44, 44), Image.LANCZOS)
            sx, sy = x0 + cell_w - 56, y0 + 182
            draw.rounded_rectangle([sx - 3, sy - 3, sx + 47, sy + 47], radius=6, fill=(255, 250, 251), outline=(228, 214, 218), width=1)
            sheet.paste(small, (sx, sy), small)

            draw.text((x0 + 12, y0 + 184), f"S{s_i} • {pcts[s_i]}", fill=acc_c, font=f_tiny)
            draw.text((x0 + 12, y0 + 206), lbl, fill=(92, 52, 58), font=f_lbl)
            draw.text((sx + 6, sy + 49), "44px", fill=(160, 140, 144), font=f_tiny)

    PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PREVIEWS_DIR / "assets_contact_sheet_loopy.png"
    sheet.save(out_path, "PNG", optimize=True)
    print(f"  [PREVIEW] Saved {out_path} ({sheet.size[0]}x{sheet.size[1]})")


if __name__ == "__main__":
    main()
