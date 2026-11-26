"""
generate_lotso_story_assets.py — v4.0 CHUBBY PLUSH BEAR Redesign for 10 Lotso Themes (#71–#80)
Generates 60 unmistakably PLUSH TEDDY BEAR Lotso sprites (100% distinct silhouette from Loopy!) + contact sheet:
  - assets/lotso_strawberry/stage_0..5.png       (#71 Lotso Strawberry Harvest — chubby back-view toe-beans -> heart eyes!)
  - assets/lotso_milk_cafe/stage_0..5.png        (#72 NEW! Lotso Strawberry Milk Cafe — replaces Cane Boss!)
  - assets/lotso_flower_crown/stage_0..5.png     (#73 Lotso Berry Flower Crown — dynamic garden poses!)
  - assets/lotso_overalls/stage_0..5.png         (#74 Lotso Overalls Toy Workshop — dynamic craft/rocket poses!)
  - assets/lotso_lofi/stage_0..5.png             (#75 Lotso LoFi Earphones Flow — swaying & singing!)
  - assets/lotso_mood_detox/stage_0..5.png       (#76 Lotso Mood Detox Comic — cookie -> heart band-aid -> balloons -> float, NO bunny ears!)
  - assets/lotso_sweet_dreams/stage_0..5.png     (#77 Lotso Floral Sweet Dreams — bouquet + pastel sheep cloud!)
  - assets/lotso_daisy_glow/stage_0..5.png       (#78 Lotso Daisy Cheek Glow — cupping cheeks & winking!)
  - assets/lotso_bunny_selfcare/stage_0..5.png   (#79 Lotso Bunny Headband Selfcare — phone -> headband -> sheet mask -> glow!)
  - assets/lotso_gift_box/stage_0..5.png         (#80 NEW! Lotso Berry Gift Box Party — replaces Berry Squad!)
  - previews/assets_contact_sheet_lotso.png      (10-row x 6-stage visual contact sheet)

Character Bible (100% Distinct Chubby Plush Bear — ZERO resemblance to Loopy!):
  - BROAD horizontal chubby teddy bear head (rx=70, ry=50) with extra-chubby wide lower cheeks!
  - MASSIVE warm buttercream oval muzzle (rx=44, ry=27) spanning across the lower face!
  - HUGE wide chocolate-berry oval bean nose (rx=21, ry=12) + thick friendly curved dark-brown eyebrows!
  - WIDE chubby plush bear body (rx=62, ry=46) + broad cream belly + stubby round paws + white toe-beans!
  - ZERO stiff repeated poses: varied tilts, sitting/leaning/pouring/floating/popping-out-of-box/jumping!
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

OL = "#5A1F33"          # Deep warm berry-plum plush outline
FUR = "#DC4E78"         # Rich warm raspberry-strawberry bear plush
FUR_LT = "#F27FA2"      # Plush highlight
FUR_SHD = "#C23B64"     # Warm plush shadow
CREAM = "#FFF2D8"       # Massive warm buttercream muzzle & belly
CREAM_SHD = "#F2DFBE"   # Subtle muzzle contour
BROW = "#633224"        # Thick soft curved friendly dark-brown bear eyebrows
NOSE = "#692034"        # Oversized wide deep-chocolate-berry bear nose
NOSE_HI = "#A65068"     # Soft nose shine
EYE = "#2B131C"         # Friendly glossy bear eyes
MOUTH = "#9E2A4B"       # Warm happy open bear mouth
TONGUE = "#FF8AA8"      # Playful pink tongue


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


def with_hero_aura(im: Image.Image, rgb: tuple[int, int, int], cy: int = 152, alpha: int = 68) -> Image.Image:
    aura = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
    ad = ImageDraw.Draw(aura)
    r, g, b = rgb
    ad.ellipse([36, cy - 110, 264, cy + 110], fill=(r, g, b, alpha))
    ad.ellipse([72, cy - 76, 228, cy + 76], fill=(255, 250, 232, 92))
    aura = aura.filter(ImageFilter.GaussianBlur(radius=22))
    return Image.alpha_composite(aura, im)


# =========================================================================== #
#  REUSABLE VECTOR DECORATIONS
# =========================================================================== #
def shadow(cx=150, cy=270, rx=76, ry=10, op=0.14) -> str:
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{OL}" fill-opacity="{op}"/>'


def soft_blush(cx: float, cy: float, rx: float, ry: float, strong: bool = False) -> str:
    if strong:
        return (
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx:.1f}" ry="{ry:.1f}" fill="#FF6E94" fill-opacity="0.34"/>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx * 0.66:.1f}" ry="{ry * 0.66:.1f}" fill="#F44E7A" fill-opacity="0.38"/>'
        )
    return (
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx:.1f}" ry="{ry:.1f}" fill="#FF85A6" fill-opacity="0.28"/>'
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx * 0.64:.1f}" ry="{ry * 0.64:.1f}" fill="#F45D84" fill-opacity="0.30"/>'
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


def star5(cx, cy, r=12, fill="#FDE047", stroke="#D97706", sw=2.0, rot=0) -> str:
    pts = []
    for i in range(10):
        ang = math.radians(rot - 90 + i * 36)
        rad = r if i % 2 == 0 else r * 0.45
        pts.append(f"{cx + math.cos(ang) * rad:.1f},{cy + math.sin(ang) * rad:.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>'


def heart(cx, cy, s=13, fill="#F43F5E", stroke=OL, sw=2.2, rot=0) -> str:
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


def daisy(cx, cy, r=15, rot=0, petal="#FFFFFF", center="#F6CE55", stroke="#A67C52") -> str:
    petals = []
    for k in range(6):
        ang = math.radians(k * 60 + rot)
        px, py = cx + math.cos(ang) * r * 0.72, cy + math.sin(ang) * r * 0.72
        petals.append(
            f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{r * 0.54:.1f}" ry="{r * 0.38:.1f}" '
            f'transform="rotate({k * 60 + rot} {px:.1f} {py:.1f})" fill="{petal}" stroke="{stroke}" stroke-width="1.8"/>'
        )
    petals.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.38:.1f}" fill="{center}" stroke="#C98A1A" stroke-width="1.8"/>')
    return "".join(petals)


def strawberry(cx, cy, s=1.0, ripe=True, rot=0, dashed_sticker=False) -> str:
    body_c = "#EE4D6E" if ripe else "#8AC48E"
    seed_c = "#FFF3DC" if ripe else "#46754A"
    parts = [f'<g transform="translate({cx},{cy}) rotate({rot}) scale({s})">']
    if dashed_sticker:
        parts.append('<circle cx="0" cy="2" r="24" fill="#FFFFFF" stroke="#B87D8C" stroke-width="2.2" stroke-dasharray="4,3"/>')
    parts.append(
        f'<path d="M -16,-6 C -18,12 -6,22 0,24 C 6,22 18,12 16,-6 C 14,-15 -14,-15 -16,-6 Z" fill="{body_c}" stroke="{OL}" stroke-width="2.8"/>'
        f'<path d="M -14,-10 Q -6,-18 0,-11 Q 6,-18 14,-10 Q 6,-6 0,-8 Q -6,-6 -14,-10 Z" fill="#64A975" stroke="{OL}" stroke-width="2.2"/>'
        f'<path d="M 0,-12 L 0,-18" stroke="#3D7A48" stroke-width="2.8" stroke-linecap="round"/>'
        f'<circle cx="-6" cy="0" r="1.7" fill="{seed_c}"/><circle cx="6" cy="0" r="1.7" fill="{seed_c}"/>'
        f'<circle cx="0" cy="6" r="1.7" fill="{seed_c}"/><circle cx="-5" cy="12" r="1.6" fill="{seed_c}"/><circle cx="5" cy="12" r="1.6" fill="{seed_c}"/>'
    )
    parts.append("</g>")
    return "".join(parts)


def music_note(cx, cy, double=False, col="#C84B6E", s=1.0) -> str:
    if not double:
        return (
            f'<g transform="translate({cx},{cy}) scale({s})">'
            f'<ellipse cx="-4" cy="10" rx="7" ry="5" transform="rotate(-18 -4 10)" fill="{col}" stroke="{OL}" stroke-width="2.0"/>'
            f'<path d="M 2,8 L 2,-14 Q 14,-10 12,-2" fill="none" stroke="{OL}" stroke-width="3.2" stroke-linecap="round"/>'
            f'</g>'
        )
    return (
        f'<g transform="translate({cx},{cy}) scale({s})">'
        f'<ellipse cx="-10" cy="12" rx="6.5" ry="4.8" transform="rotate(-18 -10 12)" fill="{col}" stroke="{OL}" stroke-width="2.0"/>'
        f'<ellipse cx="10" cy="7" rx="6.5" ry="4.8" transform="rotate(-18 10 7)" fill="{col}" stroke="{OL}" stroke-width="2.0"/>'
        f'<path d="M -4,10 L -4,-12 L 16,-16 L 16,5" fill="none" stroke="{OL}" stroke-width="3.2" stroke-linecap="round"/>'
        f'<path d="M -4,-10 L 16,-14" stroke="{col}" stroke-width="4.4" stroke-linecap="round"/>'
        f'</g>'
    )


# =========================================================================== #
#  CHUBBY PLUSH BEAR LOTSO RIG (WIDE CHEEKS, BIG MUZZLE, BIG NOSE, TOE-BEANS!)
# =========================================================================== #
def _toe_bean_foot(fx, fy, rot=0) -> str:
    return (
        f'<g transform="translate({fx},{fy}) rotate({rot})">'
        f'<ellipse cx="0" cy="0" rx="25" ry="20" fill="{FUR}" stroke="{OL}" stroke-width="4.0"/>'
        f'<ellipse cx="0" cy="4" rx="13" ry="9.5" fill="#FFFFFF"/>'
        f'<circle cx="-9" cy="-8" r="3.8" fill="#FFFFFF"/>'
        f'<circle cx="0" cy="-10.5" r="3.8" fill="#FFFFFF"/>'
        f'<circle cx="9" cy="-8" r="3.6" fill="#FFFFFF"/>'
        f'</g>'
    )


def bear_body(
    cx=150,
    cy=216,
    rx=64,
    ry=47,
    pose="sit",
    paws="down",
    outfit="none",
    lean=0,
) -> str:
    """Wide chubby plush teddy bear body with stubby arms & white toe-bean feet!"""
    parts = [f'<g transform="translate({cx},{cy}) rotate({lean})">']

    # Feet by pose (prominent chubby teddy bear soles with white toe-beans!)
    if pose == "sit":
        parts.append(_toe_bean_foot(-44, 30, rot=-18) + _toe_bean_foot(44, 30, rot=18))
    elif pose == "float":
        parts.append(_toe_bean_foot(-36, 42, rot=-28) + _toe_bean_foot(36, 42, rot=28))
    elif pose == "jump":
        parts.append(_toe_bean_foot(-42, 38, rot=-34) + _toe_bean_foot(42, 38, rot=34))
    elif pose == "walk":
        parts.append(
            f'<ellipse cx="-30" cy="44" rx="23" ry="13" transform="rotate(-12 -30 44)" fill="{FUR_SHD}" stroke="{OL}" stroke-width="3.8"/>'
            f'<ellipse cx="28" cy="34" rx="23" ry="13" transform="rotate(24 28 34)" fill="{FUR_SHD}" stroke="{OL}" stroke-width="3.8"/>'
        )
    elif pose == "hidden":
        pass
    else:  # stand
        parts.append(
            f'<ellipse cx="-28" cy="42" rx="23" ry="13" fill="{FUR_SHD}" stroke="{OL}" stroke-width="3.8"/>'
            f'<ellipse cx="28" cy="42" rx="23" ry="13" fill="{FUR_SHD}" stroke="{OL}" stroke-width="3.8"/>'
        )

    # Extra-chubby round plush torso tucked smoothly under chin (-42)
    torso_c = "#598C5E" if outfit in ("green_shirt", "overalls") else FUR
    parts.append(
        f'<path d="M {-rx + 12},-42 '
        f'C {-rx - 10},6 {-rx + 8},{ry} 0,{ry} '
        f'C {rx - 8},{ry} {rx + 10},6 {rx - 12},-42 Z" '
        f'fill="{torso_c}" stroke="{OL}" stroke-width="4.2" stroke-linejoin="round"/>'
    )

    if outfit == "none":
        parts.append(f'<ellipse cx="0" cy="11" rx="{rx * 0.62:.1f}" ry="{ry * 0.68:.1f}" fill="{CREAM}"/>')
    elif outfit == "apron":
        # Cream cafe apron with cute red strawberry emblem!
        parts.append(
            f'<ellipse cx="0" cy="11" rx="{rx * 0.62:.1f}" ry="{ry * 0.68:.1f}" fill="{CREAM}"/>'
            f'<path d="M -32,-16 L 32,-16 L 40,38 Q 0,46 -40,38 Z" fill="#FFFDF5" stroke="#B87D8C" stroke-width="3.0" stroke-linejoin="round"/>'
            f'<path d="M -26,-16 L -22,-34 M 26,-16 L 22,-34" stroke="#B87D8C" stroke-width="4.0" stroke-linecap="round"/>'
            + strawberry(0, 14, s=0.65, ripe=True)
        )
    elif outfit == "overalls":
        parts.append(
            f'<path d="M -38,-28 L -24,-28 L -24,-4 L 24,-4 L 24,-28 L 38,-28 L 46,12 '
            f'C 48,{ry - 4} 28,{ry} 0,{ry} C -28,{ry} -48,{ry - 4} -46,12 Z" '
            f'fill="{CREAM}" stroke="{OL}" stroke-width="3.6" stroke-linejoin="round"/>'
            f'<circle cx="-29" cy="-4" r="4.5" fill="#B87D4B" stroke="{OL}" stroke-width="2.0"/>'
            f'<circle cx="29" cy="-4" r="4.5" fill="#B87D4B" stroke="{OL}" stroke-width="2.0"/>'
            f'<rect x="-20" y="4" width="40" height="27" rx="8" fill="#FFF8EC" stroke="{OL}" stroke-width="2.4"/>'
            + heart(0, 17, s=8.5, fill="#DE5B73", stroke=OL, sw=1.8)
        )

    # Stubby chubby round plush arms!
    arm_c = "#598C5E" if outfit in ("green_shirt", "overalls") else FUR
    if paws == "down":
        parts.append(
            f'<ellipse cx="{-rx - 4}" cy="0" rx="18" ry="22" transform="rotate(20 {-rx - 4} 0)" fill="{arm_c}" stroke="{OL}" stroke-width="4.0"/>'
            f'<ellipse cx="{rx + 4}" cy="0" rx="18" ry="22" transform="rotate(-20 {rx + 4} 0)" fill="{arm_c}" stroke="{OL}" stroke-width="4.0"/>'
        )
    elif paws == "wide_up":
        parts.append(
            f'<ellipse cx="{-rx - 8}" cy="-26" rx="22" ry="16" transform="rotate(34 {-rx - 8} -26)" fill="{arm_c}" stroke="{OL}" stroke-width="4.0"/>'
            f'<ellipse cx="{rx + 8}" cy="-26" rx="22" ry="16" transform="rotate(-34 {rx + 8} -26)" fill="{arm_c}" stroke="{OL}" stroke-width="4.0"/>'
        )
    elif paws == "wave_r":
        parts.append(
            f'<ellipse cx="{-rx - 4}" cy="2" rx="18" ry="21" transform="rotate(18 {-rx - 4} 2)" fill="{arm_c}" stroke="{OL}" stroke-width="4.0"/>'
            f'<ellipse cx="{rx + 10}" cy="-28" rx="22" ry="16" transform="rotate(-38 {rx + 10} -28)" fill="{arm_c}" stroke="{OL}" stroke-width="4.0"/>'
        )
    elif paws == "center":
        parts.append(
            f'<ellipse cx="-30" cy="-2" rx="20" ry="15" transform="rotate(18 -30 -2)" fill="{FUR}" stroke="{OL}" stroke-width="3.8"/>'
            f'<ellipse cx="30" cy="-2" rx="20" ry="15" transform="rotate(-18 30 -2)" fill="{FUR}" stroke="{OL}" stroke-width="3.8"/>'
        )
    elif paws == "none":
        pass

    parts.append("</g>")
    return "".join(parts)


def bear_head(
    cx=150,
    cy=122,
    scale=1.0,
    expr="smile",
    brows="friendly",
    strong_blush=False,
    show_ears=True,
    rot=0,
    sheet_mask=False,
) -> str:
    """UNMISTAKABLY LOTSO CHUBBY PLUSH BEAR HEAD:
    Broad horizontal plush cheeks, HUGE buttercream oval muzzle, WIDE chocolate bean nose,
    thick soft curved friendly dark-brown eyebrows!"""
    parts = [f'<g transform="translate({cx},{cy}) rotate({rot}) scale({scale})">']
    if show_ears:
        for side in (-1, 1):
            ex, ey = side * 54, -44
            parts.append(
                f'<circle cx="{ex}" cy="{ey}" r="21" fill="{FUR}" stroke="{OL}" stroke-width="4.2"/>'
                f'<circle cx="{ex - side * 1.5}" cy="{ey + 1.5}" r="11.5" fill="{CREAM}" stroke="{OL}" stroke-width="2.2"/>'
            )

    # WIDE plush teddy bear head (distinctly broader horizontally than Loopy!)
    head_d = (
        "M -64,-12 C -64,-44 -36,-56 0,-56 C 36,-56 64,-44 64,-12 "
        "C 78,6 72,38 46,48 C 26,56 -26,56 -46,48 C -72,38 -78,6 -64,-12 Z"
    )
    parts.append(f'<path d="{head_d}" fill="{FUR}" stroke="{OL}" stroke-width="4.2" stroke-linejoin="round"/>')

    if sheet_mask:
        parts.append(
            '<path d="M -58,-8 C -56,-36 -30,-46 0,-46 C 30,-46 56,-36 58,-8 '
            'C 66,8 60,34 38,42 C 20,49 -20,49 -38,42 C -60,34 -66,8 -58,-8 Z" '
            'fill="#FFFFFF" stroke="#E5D5E8" stroke-width="2.8"/>'
        )
    else:
        # MASSIVE buttercream horizontal oval muzzle!
        parts.append(f'<ellipse cx="0" cy="20" rx="44" ry="27" fill="{CREAM}" stroke="{CREAM_SHD}" stroke-width="1.6"/>')

    # Wide rosy plush cheeks + 2 cute hatch lines
    parts.append(soft_blush(-49, 10, 18, 12, strong=strong_blush))
    parts.append(soft_blush(49, 10, 18, 12, strong=strong_blush))
    parts.append(
        '<line x1="-54" y1="12" x2="-50" y2="7" stroke="#C23B64" stroke-width="2.2" stroke-linecap="round"/>'
        '<line x1="-47" y1="13" x2="-43" y2="8" stroke="#C23B64" stroke-width="2.2" stroke-linecap="round"/>'
        '<line x1="43" y1="8" x2="47" y2="13" stroke="#C23B64" stroke-width="2.2" stroke-linecap="round"/>'
        '<line x1="50" y1="7" x2="54" y2="12" stroke="#C23B64" stroke-width="2.2" stroke-linecap="round"/>'
    )

    # Thick soft curved FRIENDLY dark-brown eyebrows (NEVER villainous!)
    if brows == "pout_sad":
        parts.append(
            f'<ellipse cx="-25" cy="-29" rx="13" ry="5.5" transform="rotate(-14 -25 -29)" fill="{BROW}" stroke="{OL}" stroke-width="1.8"/>'
            f'<ellipse cx="25" cy="-29" rx="13" ry="5.5" transform="rotate(14 25 -29)" fill="{BROW}" stroke="{OL}" stroke-width="1.8"/>'
        )
    elif brows == "grump_cute":
        parts.append(
            f'<ellipse cx="-24" cy="-28" rx="13" ry="5.5" transform="rotate(12 -24 -28)" fill="{BROW}" stroke="{OL}" stroke-width="1.8"/>'
            f'<ellipse cx="24" cy="-28" rx="13" ry="5.5" transform="rotate(-12 24 -28)" fill="{BROW}" stroke="{OL}" stroke-width="1.8"/>'
        )
    else:  # friendly soft arch!
        parts.append(
            f'<ellipse cx="-25" cy="-30" rx="13.5" ry="5.6" transform="rotate(-8 -25 -30)" fill="{BROW}" stroke="{OL}" stroke-width="1.8"/>'
            f'<ellipse cx="25" cy="-30" rx="13.5" ry="5.6" transform="rotate(8 25 -30)" fill="{BROW}" stroke="{OL}" stroke-width="1.8"/>'
        )

    # Eyes
    if expr in ("smile", "big_smile", "curious", "grumpy", "tongue", "calm_smile"):
        parts.append(
            f'<ellipse cx="-23" cy="-11" rx="6.6" ry="7.4" fill="{EYE}"/><circle cx="-25" cy="-13.5" r="2.4" fill="#FFFFFF"/>'
            f'<ellipse cx="23" cy="-11" rx="6.6" ry="7.4" fill="{EYE}"/><circle cx="21" cy="-13.5" r="2.4" fill="#FFFFFF"/>'
        )
    elif expr == "sparkle_eyes":
        parts.append(
            f'<ellipse cx="-23" cy="-11" rx="7.6" ry="8.4" fill="{EYE}"/><circle cx="-25.5" cy="-14" r="3.0" fill="#FFFFFF"/><circle cx="-20.5" cy="-8.5" r="1.5" fill="#FFFFFF"/>'
            f'<ellipse cx="23" cy="-11" rx="7.6" ry="8.4" fill="{EYE}"/><circle cx="20.5" cy="-14" r="3.0" fill="#FFFFFF"/><circle cx="25.5" cy="-8.5" r="1.5" fill="#FFFFFF"/>'
        )
    elif expr == "wink":
        parts.append(
            f'<ellipse cx="-23" cy="-11" rx="6.8" ry="7.6" fill="{EYE}"/><circle cx="-25" cy="-13.5" r="2.4" fill="#FFFFFF"/>'
            f'<path d="M 15,-15 L 27,-10 L 15,-5" fill="none" stroke="{EYE}" stroke-width="4.0" stroke-linecap="round" stroke-linejoin="round"/>'
        )
    elif expr == "heart_eyes":
        parts.append(
            heart(-23, -10, s=11.5, fill="#E11D48", stroke=OL, sw=2.0)
            + heart(23, -10, s=11.5, fill="#E11D48", stroke=OL, sw=2.0)
            + '<circle cx="-26" cy="-13" r="2.2" fill="#FFFFFF"/><circle cx="20" cy="-13" r="2.2" fill="#FFFFFF"/>'
        )
    elif expr == "happy_squint":
        parts.append(
            f'<path d="M -31,-9 Q -23,-18 -15,-9" fill="none" stroke="{EYE}" stroke-width="4.2" stroke-linecap="round"/>'
            f'<path d="M 15,-9 Q 23,-18 31,-9" fill="none" stroke="{EYE}" stroke-width="4.2" stroke-linecap="round"/>'
        )
    elif expr == "calm_closed":
        parts.append(
            f'<path d="M -30,-10 Q -23,-3 -16,-10" fill="none" stroke="{EYE}" stroke-width="3.8" stroke-linecap="round"/>'
            f'<path d="M 16,-10 Q 23,-3 30,-10" fill="none" stroke="{EYE}" stroke-width="3.8" stroke-linecap="round"/>'
        )
    elif expr == "sleepy":
        parts.append(
            f'<ellipse cx="-23" cy="-9" rx="6.2" ry="4.0" fill="{EYE}"/><path d="M -31,-14 Q -23,-11 -15,-14" fill="none" stroke="{OL}" stroke-width="3.0" stroke-linecap="round"/>'
            f'<ellipse cx="23" cy="-9" rx="6.2" ry="4.0" fill="{EYE}"/><path d="M 15,-14 Q 23,-11 31,-14" fill="none" stroke="{OL}" stroke-width="3.0" stroke-linecap="round"/>'
        )

    # HUGE WIDE DARK-CHOCOLATE BEAR NOSE!
    parts.append(
        f'<ellipse cx="0" cy="6" rx="21" ry="12.5" fill="{NOSE}" stroke="{OL}" stroke-width="2.8"/>'
        f'<ellipse cx="-6.5" cy="2" rx="6.5" ry="2.8" transform="rotate(-14 -6.5 2)" fill="{NOSE_HI}" fill-opacity="0.6"/>'
    )

    # Warm Plush Mouth (NO bucktooth!)
    if expr in ("smile", "wink", "calm_closed", "calm_smile", "sparkle_eyes"):
        parts.append(f'<path d="M -11,26 Q 0,36 11,26" fill="none" stroke="{OL}" stroke-width="3.4" stroke-linecap="round"/>')
    elif expr in ("big_smile", "happy_squint"):
        parts.append(
            f'<path d="M -16,24 C -16,20 16,20 16,24 C 16,38 7,42 0,42 C -7,42 -16,38 -16,24 Z" fill="{MOUTH}" stroke="{OL}" stroke-width="2.8"/>'
            f'<ellipse cx="0" cy="36" rx="8.5" ry="4.5" fill="{TONGUE}"/>'
        )
    elif expr in ("heart_eyes", "tongue"):
        parts.append(
            f'<path d="M -13,25 Q 0,32 13,25" fill="none" stroke="{OL}" stroke-width="3.4" stroke-linecap="round"/>'
            f'<path d="M -7,28 C -8,41 8,41 7,28 Z" fill="{TONGUE}" stroke="{OL}" stroke-width="2.4"/>'
        )
    elif expr == "grumpy":
        parts.append(f'<path d="M -12,33 Q 0,24 12,33" fill="none" stroke="{OL}" stroke-width="3.4" stroke-linecap="round"/>')
    else:  # curious / sleepy
        parts.append(f'<path d="M -8,30 Q 0,34 8,29" fill="none" stroke="{OL}" stroke-width="3.0" stroke-linecap="round"/>')

    parts.append("</g>")
    return "".join(parts)


# =========================================================================== #
#  #71 — LOTSO STRAWBERRY HARVEST (CHUBBY BACK VIEW -> PEEK -> REACH -> HUG -> WINK -> JUMP HEART-EYES!)
# =========================================================================== #
def _lotso_chubby_back() -> str:
    return (
        shadow(150, 270, 82, 10)
        + f'<circle cx="96" cy="80" r="20" fill="{FUR}" stroke="{OL}" stroke-width="4.2"/>'
        + f'<circle cx="204" cy="80" r="20" fill="{FUR}" stroke="{OL}" stroke-width="4.2"/>'
        + f'<ellipse cx="150" cy="208" rx="68" ry="52" fill="{FUR}" stroke="{OL}" stroke-width="4.2"/>'
        + f'<ellipse cx="150" cy="124" rx="68" ry="52" fill="{FUR}" stroke="{OL}" stroke-width="4.2"/>'
        + f'<circle cx="150" cy="238" r="17" fill="{FUR_LT}" stroke="{OL}" stroke-width="3.6"/>'
        + _toe_bean_foot(92, 242, rot=-22) + _toe_bean_foot(208, 242, rot=22)
        + '<path d="M 222,82 L 238,72 M 228,94 L 246,92" stroke="#E56B8C" stroke-width="3.4" stroke-linecap="round"/>'
    )


def build_71_strawberry() -> list[tuple[str, Image.Image]]:
    s0 = render_svg(_lotso_chubby_back())
    s1 = render_svg(
        shadow()
        + '<path d="M 38,158 Q 22,112 56,78 M 262,158 Q 278,112 244,78" fill="none" stroke="#E56B8C" stroke-width="3.2" stroke-linecap="round" stroke-dasharray="8,6"/>'
        + bear_body(150, 218, pose="sit", paws="down", lean=6)
        + bear_head(154, 124, expr="curious", rot=12)
    )
    s2 = render_svg(
        shadow(140, 270, 78, 10)
        + bear_body(140, 216, pose="sit", paws="wide_up", lean=-5)
        + bear_head(136, 122, expr="sparkle_eyes", rot=-8)
        + strawberry(242, 232, s=1.08, ripe=False, rot=14)
        + sp4(244, 192, r=8, fill="#8AC48E", stroke="#46754A")
    )
    s3 = render_svg(
        shadow()
        + bear_body(150, 216, pose="sit", paws="none")
        + strawberry(150, 214, s=1.72, ripe=True)
        + f'<ellipse cx="114" cy="214" rx="20" ry="15" transform="rotate(18 114 214)" fill="{FUR}" stroke="{OL}" stroke-width="3.8"/>'
        + f'<ellipse cx="186" cy="214" rx="20" ry="15" transform="rotate(-18 186 214)" fill="{FUR}" stroke="{OL}" stroke-width="3.8"/>'
        + bear_head(150, 122, expr="smile", rot=4)
    )
    s4 = render_svg(
        shadow()
        + bear_body(150, 216, pose="sit", paws="none", lean=-6)
        + strawberry(146, 214, s=1.75, ripe=True, rot=-6)
        + f'<ellipse cx="110" cy="212" rx="20" ry="15" transform="rotate(14 110 212)" fill="{FUR}" stroke="{OL}" stroke-width="3.8"/>'
        + f'<ellipse cx="184" cy="216" rx="20" ry="15" transform="rotate(-22 184 216)" fill="{FUR}" stroke="{OL}" stroke-width="3.8"/>'
        + bear_head(144, 122, expr="wink", strong_blush=True, rot=-10)
        + star5(242, 84, r=12) + sp4(52, 102, r=9)
    )
    s5 = with_hero_aura(render_svg(
        shadow(150, 272, 62, 8, op=0.12)
        + bear_body(150, 206, pose="jump", paws="none")
        + strawberry(150, 204, s=1.78, ripe=True)
        + f'<ellipse cx="112" cy="202" rx="20" ry="15" transform="rotate(18 112 202)" fill="{FUR}" stroke="{OL}" stroke-width="3.8"/>'
        + f'<ellipse cx="188" cy="202" rx="20" ry="15" transform="rotate(-18 188 202)" fill="{FUR}" stroke="{OL}" stroke-width="3.8"/>'
        + bear_head(150, 114, expr="heart_eyes", strong_blush=True, rot=5)
        + heart(48, 84, s=14, fill="#FF6E94", rot=-12) + heart(252, 88, s=13, fill="#E56B8C", rot=12)
        + sp4(52, 174, r=10) + sp4(250, 174, r=10)
    ), (229, 107, 140))
    return [
        ("Quay Lưng Lì Lợm", s0),
        ("Quay Lại Tò Mò", s1),
        ("Dâu Xanh Vừa Nhú", s2),
        ("Ôm Dâu Chín Mọng", s3),
        ("Nháy Mắt Ngọt Ngào", s4),
        ("Mắt Tim Thu Hoạch!", s5),
    ]


# =========================================================================== #
#  #72 NEW — LOTSO STRAWBERRY MILK CAFE (REPLACES CANE BOSS!)
# =========================================================================== #
def _wood_table(y=248) -> str:
    return f'<rect x="28" y="{y}" width="244" height="18" rx="8" fill="#D4A373" stroke="{OL}" stroke-width="3.2"/>'


def _milk_glass(cx=224, cy=218, filled=False, cream_top=False, s=1.0) -> str:
    parts = [f'<g transform="translate({cx},{cy}) scale({s})">']
    if filled:
        parts.append('<line x1="6" y1="-44" x2="-4" y2="14" stroke="#E11D48" stroke-width="4.5" stroke-linecap="round"/>')
        parts.append('<path d="M -17,-14 L 17,-14 L 13,24 L -13,24 Z" fill="#F9B4C8"/>')
    parts.append(f'<path d="M -18,-22 L 18,-22 L 14,26 L -14,26 Z" fill="none" stroke="{OL}" stroke-width="3.0" stroke-linejoin="round"/>')
    if cream_top:
        parts.append('<ellipse cx="0" cy="-22" rx="18" ry="8" fill="#FFFFFF" stroke="#E6D5DC" stroke-width="2.0"/>')
        parts.append('<circle cx="-6" cy="-28" r="8" fill="#FFFFFF"/><circle cx="6" cy="-28" r="8" fill="#FFFFFF"/>')
        parts.append(strawberry(10, -34, s=0.48, ripe=True, rot=18))
    parts.append("</g>")
    return "".join(parts)


def _milk_carton(cx=226, cy=188, rot=-18) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot})">'
        f'<polygon points="-16,-14 0,-28 16,-14" fill="#FDECEF" stroke="{OL}" stroke-width="2.6" stroke-linejoin="round"/>'
        f'<rect x="-16" y="-14" width="32" height="40" rx="4" fill="#F9B4C8" stroke="{OL}" stroke-width="2.8"/>'
        f'<rect x="-16" y="-2" width="32" height="16" fill="#FFFFFF"/>'
        + strawberry(0, 6, s=0.38, ripe=True)
        + '</g>'
    )


def _shortcake_slice(cx=64, cy=224) -> str:
    return (
        f'<g transform="translate({cx},{cy})">'
        f'<ellipse cx="0" cy="18" rx="30" ry="8" fill="#E6F5EC" stroke="#8CC5A3" stroke-width="2.2"/>'
        f'<polygon points="-22,14 24,14 24,-10 -22,2" fill="#FFF8E6" stroke="{OL}" stroke-width="2.6" stroke-linejoin="round"/>'
        f'<line x1="-20" y1="7" x2="23" y2="2" stroke="#F47294" stroke-width="4.5"/>'
        f'<path d="M -22,2 L 24,-10 L 18,-18 L -20,-4 Z" fill="#FFFFFF" stroke="{OL}" stroke-width="2.2"/>'
        + strawberry(4, -22, s=0.52, ripe=True)
        + '</g>'
    )


def build_72_milk_cafe() -> list[tuple[str, Image.Image]]:
    # S0: Sitting resting chin on wooden table beside empty glass, slightly sluggish
    s0 = render_svg(
        bear_body(134, 218, pose="sit", paws="none", lean=-6)
        + bear_head(130, 128, expr="sleepy", brows="pout_sad", rot=-10)
        + _wood_table(246)
        + f'<ellipse cx="102" cy="182" rx="18" ry="14" transform="rotate(-16 102 182)" fill="{FUR}" stroke="{OL}" stroke-width="3.6"/>'
        + _milk_glass(228, 220, filled=False)
    )
    # S1: Putting on strawberry cafe apron holding pink strawberry milk carton excitedly!
    s1 = render_svg(
        shadow() + bear_body(142, 216, pose="stand", paws="wave_r", outfit="apron", lean=5)
        + bear_head(146, 122, expr="curious", rot=6)
        + _milk_carton(230, 184, rot=12)
    )
    # S2: Pouring pink strawberry milk into glass with striped straw!
    s2 = render_svg(
        bear_body(134, 216, pose="sit", paws="wave_r", outfit="apron", lean=8)
        + bear_head(140, 122, expr="smile", rot=8)
        + _wood_table(246)
        + '<path d="M 206,174 Q 222,190 224,206" fill="none" stroke="#F9B4C8" stroke-width="7.0" stroke-linecap="round"/>'
        + _milk_carton(196, 160, rot=54)
        + _milk_glass(228, 220, filled=True, cream_top=False)
    )
    # S3: Topping glass with fresh strawberry & whipped cream, starry eyes!
    s3 = render_svg(
        bear_body(138, 216, pose="sit", paws="center", outfit="apron", lean=-4)
        + bear_head(136, 122, expr="sparkle_eyes", strong_blush=True, rot=-6)
        + _wood_table(246)
        + _milk_glass(226, 220, filled=True, cream_top=True)
        + sp4(248, 166, r=10) + sp4(60, 108, r=9)
    )
    # S4: Chubby paws hugging full strawberry milk glass sipping happily, rosy cheeks!
    s4 = render_svg(
        shadow() + bear_body(150, 216, pose="sit", paws="none", outfit="apron", lean=5)
        + _milk_glass(154, 212, filled=True, cream_top=True, s=1.12)
        + f'<ellipse cx="116" cy="214" rx="20" ry="15" transform="rotate(18 116 214)" fill="{FUR}" stroke="{OL}" stroke-width="3.8"/>'
        + f'<ellipse cx="192" cy="214" rx="20" ry="15" transform="rotate(-18 192 214)" fill="{FUR}" stroke="{OL}" stroke-width="3.8"/>'
        + bear_head(152, 122, expr="happy_squint", strong_blush=True, rot=8)
        + heart(242, 102, s=13, fill="#F7B2C4", stroke="#D65076")
    )
    # S5: Sitting joyfully beside full-topping strawberry milk & shortcake slice + floating hearts!
    s5 = with_hero_aura(render_svg(
        bear_body(150, 212, pose="sit", paws="wide_up", outfit="apron")
        + bear_head(150, 118, expr="big_smile", strong_blush=True, rot=-4)
        + _wood_table(248)
        + _shortcake_slice(62, 224)
        + _milk_glass(234, 222, filled=True, cream_top=True, s=1.02)
        + heart(54, 86, s=14, fill="#D65076", rot=-12) + heart(248, 86, s=13, fill="#F7B2C4", rot=12)
        + sp4(150, 34, r=11)
    ), (214, 80, 118))
    return [
        ("Uể Oải Ly Rỗng", s0),
        ("Đeo Tạp Dề Sữa Dâu", s1),
        ("Rót Sữa Dâu Hồng", s2),
        ("Thêm Kem & Dâu Tươi", s3),
        ("Ôm Ly Hút Ngon Lành", s4),
        ("Tiệc Sữa Dâu Shortcake!", s5),
    ]


# =========================================================================== #
#  #73 — LOTSO BERRY FLOWER CROWN (CHUBBY BEAR + DYNAMIC POSES!)
# =========================================================================== #
def _berry_crown(cx=150, cy=66, level="full", rot=0) -> str:
    if level == "half":
        return (
            f'<g transform="translate({cx},{cy}) rotate({rot})">'
            f'<ellipse cx="-34" cy="6" rx="16" ry="7" transform="rotate(-24 -34 6)" fill="#64A975" stroke="{OL}" stroke-width="2.2"/>'
            f'<ellipse cx="34" cy="6" rx="16" ry="7" transform="rotate(24 34 6)" fill="#64A975" stroke="{OL}" stroke-width="2.2"/>'
            f'<ellipse cx="0" cy="-4" rx="18" ry="7" fill="#64A975" stroke="{OL}" stroke-width="2.2"/>'
            + daisy(-22, 2, r=11) + daisy(22, 2, r=11) + daisy(0, -6, r=12) + '</g>'
        )
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot})">'
        f'<ellipse cx="-44" cy="8" rx="16" ry="7" transform="rotate(-28 -44 8)" fill="#64A975" stroke="{OL}" stroke-width="2.2"/>'
        f'<ellipse cx="44" cy="8" rx="16" ry="7" transform="rotate(28 44 8)" fill="#64A975" stroke="{OL}" stroke-width="2.2"/>'
        f'<ellipse cx="-16" cy="-4" rx="16" ry="7" transform="rotate(-10 -16 -4)" fill="#64A975" stroke="{OL}" stroke-width="2.2"/>'
        f'<ellipse cx="16" cy="-4" rx="16" ry="7" transform="rotate(10 16 -4)" fill="#64A975" stroke="{OL}" stroke-width="2.2"/>'
        + strawberry(-26, -4, s=0.62, rot=-18) + strawberry(26, -4, s=0.62, rot=18) + strawberry(0, -10, s=0.68)
        + daisy(-46, 6, r=10) + daisy(46, 6, r=10) + daisy(-14, 4, r=9) + daisy(14, 4, r=9) + '</g>'
    )


def _berry_cluster(cx=228, cy=184, s=1.0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) scale({s})">'
        f'<path d="M 0,-26 Q -14,-8 -14,6 M 0,-26 Q 14,-6 14,10" fill="none" stroke="#4D8B58" stroke-width="3.4" stroke-linecap="round"/>'
        + strawberry(-14, 14, s=0.82, rot=-10) + strawberry(14, 18, s=0.82, rot=12) + daisy(0, -24, r=9) + '</g>'
    )


def build_73_flower_crown() -> list[tuple[str, Image.Image]]:
    s0 = render_svg(
        shadow() + bear_body(150, 216, pose="sit", paws="down", lean=-4)
        + bear_head(148, 122, expr="sparkle_eyes", rot=-6)
        + '<ellipse cx="72" cy="266" rx="18" ry="5" fill="#C4E3C9"/><ellipse cx="228" cy="266" rx="18" ry="5" fill="#C4E3C9"/>'
    )
    s1 = render_svg(
        shadow() + bear_body(150, 216, pose="stand", paws="wave_r", lean=5)
        + bear_head(154, 122, expr="smile", rot=8)
        + daisy(208, 72, r=13)
    )
    s2 = render_svg(
        shadow() + bear_body(150, 216, pose="walk", paws="down", lean=-6)
        + bear_head(146, 122, expr="smile", strong_blush=True, rot=-8)
        + _berry_crown(142, 66, level="half", rot=-8)
    )
    s3 = render_svg(
        shadow() + bear_body(150, 216, pose="sit", paws="center")
        + bear_head(150, 122, expr="wink", strong_blush=True, rot=5)
        + _berry_crown(152, 66, level="full", rot=5) + sp4(52, 92, r=9)
    )
    s4 = render_svg(
        shadow() + bear_body(146, 216, pose="walk", paws="wave_r", lean=-4)
        + bear_head(144, 122, expr="big_smile", strong_blush=True, rot=-6)
        + _berry_crown(140, 66, level="full", rot=-6)
        + _berry_cluster(236, 184, s=0.98)
    )
    s5 = with_hero_aura(render_svg(
        shadow(150, 272, 62, 8, op=0.12)
        + bear_body(150, 204, pose="jump", paws="wide_up")
        + bear_head(150, 114, expr="happy_squint", strong_blush=True, rot=4)
        + _berry_crown(152, 58, level="full", rot=4)
        + _berry_cluster(242, 148, s=1.02)
        + daisy(48, 88, r=12) + daisy(254, 78, r=11) + daisy(52, 200, r=10) + sp4(248, 224, r=10)
    ), (217, 74, 107))
    return [
        ("Vườn Trống Háo Hức", s0),
        ("Cài Hoa Cúc Tai", s1),
        ("Bước Đi Vòng Lá", s2),
        ("Vương Miện Dâu Đầy", s3),
        ("Cầm Chùm Dâu Chín", s4),
        ("Nhảy Mừng Vườn Dâu!", s5),
    ]


# =========================================================================== #
#  #74 — LOTSO OVERALLS TOY WORKSHOP (CHUBBY BEAR + DYNAMIC POSES!)
# =========================================================================== #
def _pizza_slice(cx=238, cy=236) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate(14)">'
        f'<path d="M -22,-16 Q 0,-24 22,-16 L 4,22 Z" fill="#FDE047" stroke="{OL}" stroke-width="2.6"/>'
        f'<path d="M -24,-14 Q 0,-24 24,-14" fill="none" stroke="#D99B58" stroke-width="7.0" stroke-linecap="round"/>'
        f'<circle cx="-5" cy="-4" r="4.2" fill="#DE5B73"/><circle cx="7" cy="2" r="4.0" fill="#DE5B73"/><circle cx="2" cy="12" r="3.2" fill="#598C5E"/>'
        f'</g>'
    )


def _toy_rocket(cx=242, cy=96, rot=24, s=0.90) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot}) scale({s})">'
        f'<circle cx="0" cy="0" r="34" fill="#FFFFFF" stroke="#B87D8C" stroke-width="2.2" stroke-dasharray="4,3"/>'
        f'<path d="M -6,18 Q 0,32 6,18 Z" fill="#F97316"/>'
        f'<path d="M -12,12 L -20,22 L -10,18 Z M 12,12 L 20,22 L 10,18 Z" fill="#DE5B73" stroke="{OL}" stroke-width="2.0"/>'
        f'<path d="M 0,-24 C 12,-14 14,4 11,18 L -11,18 C -14,4 -12,-14 0,-24 Z" fill="#FDE047" stroke="{OL}" stroke-width="2.6"/>'
        f'<circle cx="0" cy="-2" r="6" fill="#93C5FD" stroke="{OL}" stroke-width="2.2"/></g>'
    )


def _piggy_pal(cx=52, cy=224, s=0.88) -> str:
    return (
        f'<g transform="translate({cx},{cy}) scale({s})">'
        f'<circle cx="0" cy="0" r="28" fill="#FFFFFF" stroke="#B87D8C" stroke-width="2.2" stroke-dasharray="4,3"/>'
        f'<circle cx="-14" cy="-14" r="7" fill="#F9B4C8" stroke="{OL}" stroke-width="2.2"/><circle cx="14" cy="-14" r="7" fill="#F9B4C8" stroke="{OL}" stroke-width="2.2"/>'
        f'<ellipse cx="0" cy="2" rx="19" ry="16" fill="#FFC8D8" stroke="{OL}" stroke-width="2.4"/>'
        f'<circle cx="-7" cy="-2" r="2.2" fill="{EYE}"/><circle cx="7" cy="-2" r="2.2" fill="{EYE}"/>'
        f'<ellipse cx="0" cy="6" rx="7" ry="4.8" fill="#F48AA8" stroke="{OL}" stroke-width="1.8"/>'
        f'<circle cx="-2.5" cy="6" r="1.2" fill="{OL}"/><circle cx="2.5" cy="6" r="1.2" fill="{OL}"/></g>'
    )


def _hi_badge(x=242, y=90) -> str:
    return (
        f'<g transform="translate({x},{y})">'
        f'<rect x="-26" y="-18" width="52" height="32" rx="14" fill="#FFFDF5" stroke="#DE5B73" stroke-width="3.0"/>'
        f'<text x="0" y="5" text-anchor="middle" font-family="Segoe UI" font-weight="900" font-size="18" fill="#DE5B73">Hi!</text></g>'
    )


def build_74_overalls() -> list[tuple[str, Image.Image]]:
    s0 = render_svg(
        shadow(136, 270, 72, 10) + bear_body(136, 218, pose="sit", paws="down", outfit="green_shirt", lean=-6)
        + bear_head(132, 124, expr="sleepy", rot=-10) + _pizza_slice(238, 236)
    )
    s1 = render_svg(
        shadow() + bear_body(150, 216, pose="stand", paws="center", outfit="overalls", lean=5)
        + bear_head(154, 122, expr="curious", rot=6)
    )
    s2 = render_svg(
        shadow() + bear_body(146, 216, pose="walk", paws="wave_r", outfit="overalls", lean=-5)
        + bear_head(144, 122, expr="smile", strong_blush=True, rot=-8) + _hi_badge(244, 88)
    )
    s3 = render_svg(
        shadow() + bear_body(150, 216, pose="sit", paws="wide_up", outfit="overalls", lean=4)
        + bear_head(152, 122, expr="wink", strong_blush=True, rot=6)
        + strawberry(52, 102, s=0.86, ripe=True, rot=-12, dashed_sticker=True)
        + strawberry(248, 214, s=0.84, ripe=False, rot=14, dashed_sticker=True)
    )
    s4 = render_svg(
        shadow() + bear_body(146, 214, pose="walk", paws="wide_up", outfit="overalls", lean=-6)
        + bear_head(142, 120, expr="big_smile", strong_blush=True, rot=-6)
        + strawberry(50, 112, s=0.82, ripe=True, rot=-14, dashed_sticker=True)
        + _toy_rocket(246, 94) + sp4(250, 186, r=10)
    )
    s5 = with_hero_aura(render_svg(
        shadow(150, 272, 62, 8, op=0.12)
        + bear_body(150, 204, pose="jump", paws="wide_up", outfit="overalls")
        + bear_head(150, 114, expr="happy_squint", strong_blush=True, rot=4)
        + strawberry(52, 84, s=0.80, ripe=True, rot=-12, dashed_sticker=True)
        + _toy_rocket(246, 86) + _piggy_pal(52, 224)
        + strawberry(248, 222, s=0.78, ripe=False, rot=12, dashed_sticker=True) + sp4(150, 34, r=10)
    ), (89, 140, 94))
    return [
        ("Áo Xanh Ngái Ngủ", s0),
        ("Mặc Yếm Trái Tim", s1),
        ("Vẫy Tay Chào Hi!", s2),
        ("Sticker Sổ Tay", s3),
        ("Tên Lửa Tăng Tốc", s4),
        ("Xưởng Đồ Chơi 100%!", s5),
    ]


# =========================================================================== #
#  #75 — LOTSO LO-FI EARPHONES FLOW (CHUBBY BEAR + SWAYING/SINGING POSES!)
# =========================================================================== #
def _earphones(mode="both", cx=150, cy=122) -> str:
    if mode == "tangled":
        return (
            '<path d="M 114,204 C 132,228 172,190 186,214 C 196,232 146,246 132,224" fill="none" stroke="#6B3A2E" stroke-width="3.6" stroke-linecap="round"/>'
            '<circle cx="114" cy="204" r="6" fill="#6B3A2E"/><circle cx="186" cy="214" r="6" fill="#6B3A2E"/>'
        )
    if mode == "one":
        return (
            f'<path d="M {cx - 60},{cy} C {cx - 78},{cy + 36} {cx - 58},{cy + 72} {cx - 34},{cy + 94}" fill="none" stroke="#6B3A2E" stroke-width="3.6" stroke-linecap="round"/>'
            f'<ellipse cx="{cx - 62}" cy="{cy}" rx="8.5" ry="11" fill="#6B3A2E" stroke="#3D1F17" stroke-width="2.0"/>'
        )
    return (
        f'<path d="M {cx - 60},{cy} C {cx - 78},{cy + 36} {cx - 56},{cy + 74} {cx - 26},{cy + 96}" fill="none" stroke="#6B3A2E" stroke-width="3.6" stroke-linecap="round"/>'
        f'<path d="M {cx + 60},{cy} C {cx + 78},{cy + 36} {cx + 56},{cy + 74} {cx + 26},{cy + 96}" fill="none" stroke="#6B3A2E" stroke-width="3.6" stroke-linecap="round"/>'
        f'<ellipse cx="{cx - 62}" cy="{cy}" rx="8.5" ry="11" fill="#6B3A2E" stroke="#3D1F17" stroke-width="2.0"/>'
        f'<ellipse cx="{cx + 62}" cy="{cy}" rx="8.5" ry="11" fill="#6B3A2E" stroke="#3D1F17" stroke-width="2.0"/>'
    )


def _soundwaves(bright=False) -> str:
    c1, c2 = ("#F4A4BA", "#FCE3C2") if bright else ("#F6C2D0", "#FDECD8")
    return (
        f'<circle cx="150" cy="148" r="124" fill="none" stroke="{c2}" stroke-width="8"/>'
        f'<circle cx="150" cy="148" r="106" fill="none" stroke="{c1}" stroke-width="5" stroke-dasharray="18,12"/>'
        f'<circle cx="150" cy="148" r="88" fill="none" stroke="{c2}" stroke-width="4"/>'
    )


def build_75_lofi() -> list[tuple[str, Image.Image]]:
    s0 = render_svg(
        shadow() + bear_body(150, 218, pose="sit", paws="center", lean=-6)
        + _earphones("tangled") + bear_head(146, 124, expr="curious", brows="pout_sad", rot=-8)
    )
    s1 = render_svg(
        shadow() + bear_body(150, 216, pose="sit", paws="down", lean=5)
        + bear_head(154, 122, expr="calm_smile", rot=6) + _earphones("one", 154, 122)
    )
    s2 = render_svg(
        shadow() + bear_body(150, 216, pose="stand", paws="wave_r", lean=-4)
        + bear_head(148, 122, expr="smile", rot=-5) + _earphones("both", 148, 122)
        + music_note(240, 92, double=False, col="#B83E62")
    )
    s3 = render_svg(
        _soundwaves(False) + shadow() + bear_body(150, 218, pose="sit", paws="center")
        + bear_head(150, 124, expr="calm_closed", strong_blush=True, rot=6) + _earphones("both", 150, 124)
        + music_note(54, 92, double=False, col="#B83E62")
    )
    s4 = render_svg(
        _soundwaves(False) + shadow() + bear_body(150, 214, pose="walk", paws="wave_r", lean=-9)
        + bear_head(142, 120, expr="happy_squint", strong_blush=True, rot=-14) + _earphones("both", 142, 120)
        + music_note(242, 92, double=True, col="#B83E62", s=1.05) + music_note(52, 102, double=False, col="#E56B8C", s=0.9)
    )
    s5 = with_hero_aura(render_svg(
        _soundwaves(True) + shadow(150, 272, 62, 8, op=0.12)
        + bear_body(150, 204, pose="jump", paws="wide_up", lean=6)
        + bear_head(154, 114, expr="big_smile", strong_blush=True, rot=8) + _earphones("both", 154, 114)
        + music_note(48, 84, double=True, col="#B83E62", s=1.05) + music_note(250, 88, double=True, col="#E56B8C", s=1.05)
        + sp4(52, 204, r=10) + sp4(250, 204, r=10)
    ), (184, 62, 98))
    return [
        ("Dây Rối Xao Nhãng", s0),
        ("Đeo 1 Bên Tai", s1),
        ("Nốt Nhạc Bắt Nhịp", s2),
        ("Sóng Nhạc Deep Flow", s3),
        ("Đung Đưa Ngân Nga", s4),
        ("Phiêu Nhạc 100%!", s5),
    ]


# =========================================================================== #
#  #76 — LOTSO MOOD DETOX COMIC (COOKIE -> HEART BAND-AID -> 1 BALLOON -> 2 -> FLOAT -> HEART RAIN, NO BUNNY EARS!)
# =========================================================================== #
def _lightning(cx, cy, rot=0, s=0.95) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot}) scale({s})">'
        f'<polygon points="-4,-18 8,-4 0,-2 6,16 -8,2 0,0" fill="#EAB844" stroke="#B45309" stroke-width="2.0" stroke-linejoin="round"/></g>'
    )


def _cookie_state(cx=150, cy=214, mended=False) -> str:
    if not mended:
        return (
            f'<g transform="translate({cx},{cy})">'
            f'<path d="M -30,0 A 20,20 0 0,1 -5,-18 L -9,-6 L -3,4 L -9,18 A 20,20 0 0,1 -30,0 Z" fill="#FDE08B" stroke="#B45309" stroke-width="2.6"/>'
            f'<circle cx="-17" cy="-4" r="2.2" fill="{OL}"/>'
            f'<path d="M 30,0 A 20,20 0 0,0 5,-18 L 9,-6 L 3,4 L 9,18 A 20,20 0 0,0 30,0 Z" fill="#FDE08B" stroke="#B45309" stroke-width="2.6"/>'
            f'<circle cx="17" cy="-4" r="2.2" fill="{OL}"/></g>'
        )
    # Mended smiley cookie with a cute pink heart band-aid across the crack!
    return (
        f'<g transform="translate({cx},{cy})">'
        f'<circle cx="0" cy="0" r="22" fill="#FDE08B" stroke="#B45309" stroke-width="2.6"/>'
        f'<path d="M 0,-21 L -3,-6 L 3,6 L 0,21" fill="none" stroke="#B45309" stroke-width="1.8"/>'
        f'<circle cx="-9" cy="-5" r="2.3" fill="{OL}"/><circle cx="9" cy="-5" r="2.3" fill="{OL}"/>'
        f'<path d="M -7,7 Q 0,13 7,7" fill="none" stroke="{OL}" stroke-width="2.2" stroke-linecap="round"/>'
        f'<rect x="-13" y="-6" width="26" height="11" rx="5" transform="rotate(-12)" fill="#F9B4C8" stroke="{OL}" stroke-width="2.0"/>'
        + heart(0, 0, s=4.8, fill="#E11D48", stroke="none")
        + '</g>'
    )


def _balloon_bunch(count=1) -> str:
    if count == 1:
        return (
            '<path d="M 218,186 Q 232,140 240,104" fill="none" stroke="#8C5266" stroke-width="2.4"/>'
            + heart(242, 86, s=22, fill="#FF85A6", stroke=OL, sw=2.6, rot=12)
        )
    if count == 2:
        return (
            '<path d="M 90,188 Q 70,142 60,96 M 210,188 Q 230,142 240,96" fill="none" stroke="#8C5266" stroke-width="2.4"/>'
            + heart(58, 80, s=23, fill="#FF85A6", stroke=OL, sw=2.6, rot=-14)
            + heart(242, 80, s=23, fill="#F47294", stroke=OL, sw=2.6, rot=14)
        )
    # Bunch of 4 floating heart balloons lifting Lotso off the ground!
    return (
        '<path d="M 96,174 Q 76,120 68,72 M 102,174 Q 108,116 112,56 M 198,174 Q 192,116 188,56 M 204,174 Q 224,120 232,72" fill="none" stroke="#8C5266" stroke-width="2.2"/>'
        + heart(66, 62, s=21, fill="#F7B2C4", stroke=OL, sw=2.4, rot=-16)
        + heart(112, 46, s=22, fill="#FF85A6", stroke=OL, sw=2.4, rot=-6)
        + heart(188, 46, s=22, fill="#F47294", stroke=OL, sw=2.4, rot=6)
        + heart(234, 62, s=21, fill="#E8799B", stroke=OL, sw=2.4, rot=16)
    )


def build_76_mood_detox() -> list[tuple[str, Image.Image]]:
    # S0: Frowning snapping smiley cookie amid 4 yellow lightning zaps
    s0 = render_svg(
        shadow() + bear_body(150, 218, pose="sit", paws="center")
        + _cookie_state(150, 214, mended=False)
        + bear_head(150, 124, expr="grumpy", brows="grump_cute", rot=-6)
        + _lightning(46, 72, -16) + _lightning(254, 72, 16) + _lightning(42, 178, -22, 0.85) + _lightning(258, 178, 22, 0.85)
    )
    # S1: Sitting calmly sticking a pink heart band-aid to mend the cookie!
    s1 = render_svg(
        shadow() + bear_body(150, 218, pose="sit", paws="center", lean=5)
        + _cookie_state(152, 216, mended=True)
        + bear_head(154, 124, expr="calm_smile", brows="pout_sad", rot=8)
    )
    # S2: Relieved gentle smile holding 1 small pink heart balloon!
    s2 = render_svg(
        shadow() + _balloon_bunch(1)
        + bear_body(146, 216, pose="stand", paws="wave_r", lean=-4)
        + bear_head(144, 122, expr="smile", rot=-6)
    )
    # S3: Cheering up hugging 2 swaying heart balloons!
    s3 = render_svg(
        shadow() + _balloon_bunch(2)
        + bear_body(150, 216, pose="walk", paws="wide_up", lean=6)
        + bear_head(154, 122, expr="smile", strong_blush=True, rot=8)
    )
    # S4: Floating lightly off ground holding bunch of heart balloons (toe-beans lifted!)
    s4 = render_svg(
        shadow(150, 278, 46, 6, op=0.10) + _balloon_bunch(4)
        + bear_body(150, 200, pose="float", paws="wide_up", lean=-5)
        + bear_head(146, 114, expr="wink", strong_blush=True, rot=-8)
    )
    # S5: Blissful radiant smile amidst pastel heart rain — 100% stress detox!
    s5 = with_hero_aura(render_svg(
        shadow(150, 272, 62, 8, op=0.12)
        + bear_body(150, 206, pose="jump", paws="wide_up")
        + bear_head(150, 116, expr="happy_squint", strong_blush=True, rot=4)
        + heart(48, 78, s=15, fill="#E11D48", rot=-14) + heart(252, 82, s=14, fill="#F43F5E", rot=14)
        + heart(44, 174, s=12, fill="#FB7185", rot=-8) + heart(256, 174, s=12, fill="#E11D48", rot=8)
        + heart(150, 26, s=12, fill="#FF85A6") + sp4(88, 46, r=9) + sp4(212, 46, r=9)
    ), (170, 58, 96))
    return [
        ("Vỡ Bánh Tia Sét", s0),
        ("Dán Băng Trái Tim", s1),
        ("Cầm Bóng Tim Nhỏ", s2),
        ("Ôm 2 Bóng Bay", s3),
        ("Bay Bổng Chùm Bóng", s4),
        ("Mưa Tim Detox 100%!", s5),
    ]


# =========================================================================== #
#  #77 — LOTSO FLORAL SWEET DREAMS (CHUBBY BEAR + BOUQUET + PASTEL SHEEP CLOUD!)
# =========================================================================== #
def _rose(cx, cy, s=1.0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) scale({s})">'
        f'<circle cx="-7" cy="-4" r="8" fill="#E11D48" stroke="{OL}" stroke-width="2.0"/>'
        f'<circle cx="7" cy="-4" r="8" fill="#E11D48" stroke="{OL}" stroke-width="2.0"/>'
        f'<circle cx="0" cy="-10" r="8" fill="#F43F5E" stroke="{OL}" stroke-width="2.0"/>'
        f'<circle cx="0" cy="2" r="8" fill="#E11D48" stroke="{OL}" stroke-width="2.0"/>'
        f'<circle cx="0" cy="-4" r="5" fill="#FDE047" stroke="#C98A1A" stroke-width="1.6"/></g>'
    )


def _bouquet(cx=150, cy=214, blooms=0) -> str:
    parts = [
        f'<g transform="translate({cx},{cy})">'
        '<path d="M -8,28 L -20,-12 M 0,30 L 0,-18 M 8,28 L 20,-12" stroke="#4D8B58" stroke-width="4.2" stroke-linecap="round"/>'
        '<ellipse cx="-22" cy="4" rx="12" ry="6" transform="rotate(-30 -22 4)" fill="#78B886" stroke="#3D6E46" stroke-width="2.0"/>'
        '<ellipse cx="22" cy="4" rx="12" ry="6" transform="rotate(30 22 4)" fill="#78B886" stroke="#3D6E46" stroke-width="2.0"/>'
        '<path d="M -12,12 L 12,12" stroke="#E892AC" stroke-width="5.5" stroke-linecap="round"/>'
    ]
    if blooms >= 1:
        parts.append(_rose(0, -18, 1.0))
    if blooms >= 2:
        parts.append(_rose(-18, -10, 0.9) + _rose(18, -10, 0.9))
    if blooms >= 3:
        parts.append(_rose(-10, -24, 0.85) + _rose(10, -24, 0.85))
    parts.append("</g>")
    return "".join(parts)


def _dream_cloud(mode="small") -> str:
    if mode == "small":
        return (
            '<circle cx="206" cy="94" r="6" fill="#FCEEF3" stroke="#9D82C9" stroke-width="2.2"/>'
            '<path d="M 218,74 C 210,74 206,62 214,56 C 216,46 232,44 238,52 C 248,48 258,58 254,68 C 258,76 246,82 236,78 Z" fill="#FFF2F7" stroke="#9D82C9" stroke-width="2.4"/>'
        )
    parts = [
        '<circle cx="198" cy="94" r="6.5" fill="#FFF2F7" stroke="#9D82C9" stroke-width="2.2"/>',
        '<path d="M 192,70 C 178,70 174,52 186,44 C 188,28 214,22 228,34 C 244,24 268,36 264,54 C 272,68 256,82 238,76 C 224,82 204,80 192,70 Z" fill="#FFF2F7" stroke="#9D82C9" stroke-width="2.6"/>',
    ]
    if mode == "ear":
        parts.append('<ellipse cx="222" cy="54" rx="16" ry="9" transform="rotate(-16 222 54)" fill="#C4B5FD" stroke="#6D4C9E" stroke-width="2.4"/>')
    elif mode == "sheep":
        parts.append(
            '<ellipse cx="206" cy="56" rx="11" ry="6" transform="rotate(-24 206 56)" fill="#B89EDB" stroke="#6D4C9E" stroke-width="2.0"/>'
            '<ellipse cx="242" cy="56" rx="11" ry="6" transform="rotate(24 242 56)" fill="#B89EDB" stroke="#6D4C9E" stroke-width="2.0"/>'
            '<circle cx="224" cy="54" r="16" fill="#E9DDFB" stroke="#6D4C9E" stroke-width="2.2"/>'
            '<circle cx="218" cy="40" r="7" fill="#D8C2F6"/><circle cx="228" cy="40" r="7" fill="#D8C2F6"/>'
            '<path d="M 215,54 Q 218,50 221,54 M 227,54 Q 230,50 233,54" fill="none" stroke="#4C2E78" stroke-width="2.2" stroke-linecap="round"/>'
            '<path d="M 220,60 Q 224,63 228,60" fill="none" stroke="#4C2E78" stroke-width="2.0" stroke-linecap="round"/>'
        )
    return "".join(parts)


def build_77_sweet_dreams() -> list[tuple[str, Image.Image]]:
    s0 = render_svg(shadow() + bear_body(150, 218, pose="sit", paws="center", lean=-5) + _bouquet(148, 214, 0) + bear_head(146, 124, expr="calm_smile", rot=-8))
    s1 = render_svg(shadow() + bear_body(150, 216, pose="sit", paws="center", lean=4) + _bouquet(152, 214, 1) + bear_head(154, 122, expr="smile", rot=6))
    s2 = render_svg(shadow() + bear_body(146, 216, pose="stand", paws="center", lean=-4) + _bouquet(144, 214, 2) + bear_head(144, 122, expr="smile", strong_blush=True, rot=-6) + _dream_cloud("small"))
    s3 = render_svg(shadow() + bear_body(144, 216, pose="sit", paws="center", lean=5) + _bouquet(146, 214, 3) + bear_head(148, 122, expr="smile", strong_blush=True, rot=8) + _dream_cloud("ear"))
    s4 = render_svg(shadow() + bear_body(144, 216, pose="sit", paws="center", lean=-5) + _bouquet(142, 214, 3) + bear_head(140, 124, expr="calm_closed", strong_blush=True, rot=-8) + _dream_cloud("sheep"))
    s5 = with_hero_aura(render_svg(
        '<ellipse cx="150" cy="160" rx="124" ry="96" fill="#FCECF3"/>'
        + shadow() + bear_body(134, 214, pose="sit", paws="wave_r", lean=4)
        + _bouquet(114, 212, 3)
        + bear_head(138, 124, expr="happy_squint", strong_blush=True, rot=5)
        + _dream_cloud("sheep") + sp4(46, 84, r=11, fill="#FDE047", stroke="#9D82C9") + sp4(48, 198, r=9, fill="#E9DDFB", stroke="#8B6BB8")
    ), (184, 158, 219))
    return [
        ("Ôm Cành Lá Xanh", s0),
        ("Hoa Hồng Đầu Tiên", s1),
        ("Mây Suy Nghĩ Nhỏ", s2),
        ("Tai Cừu Lấp Ló", s3),
        ("Cừu Tím Cười Tít", s4),
        ("Giấc Mơ Cừu Bông!", s5),
    ]


# =========================================================================== #
#  #78 — LOTSO DAISY CHEEK GLOW (CHUBBY BEAR CUPPING CHEEKS & WINKING!)
# =========================================================================== #
def _daisy_bud(cx=240, cy=244) -> str:
    return (
        f'<g transform="translate({cx},{cy})">'
        f'<path d="M 0,18 Q 2,6 0,-4" fill="none" stroke="#6D9F71" stroke-width="3.6" stroke-linecap="round"/>'
        f'<ellipse cx="-7" cy="8" rx="7" ry="3.5" transform="rotate(-24 -7 8)" fill="#8AC48E" stroke="{OL}" stroke-width="1.8"/>'
        f'<circle cx="0" cy="-6" r="8" fill="#FFFFFF" stroke="#A67C52" stroke-width="2.0"/><circle cx="0" cy="-6" r="3.5" fill="#EFC143"/></g>'
    )


def build_78_daisy_glow() -> list[tuple[str, Image.Image]]:
    s0 = render_svg(shadow() + bear_body(150, 218, pose="sit", paws="down", lean=-6) + bear_head(146, 124, expr="curious", rot=-10) + _daisy_bud(240, 244))
    s1 = render_svg(
        shadow() + bear_body(150, 218, pose="sit", paws="none", lean=5)
        + bear_head(154, 124, expr="calm_smile", strong_blush=True, rot=8)
        + f'<ellipse cx="206" cy="154" rx="20" ry="15" transform="rotate(24 206 154)" fill="{FUR}" stroke="{OL}" stroke-width="3.8"/>'
        + _daisy_bud(240, 244)
    )
    s2 = render_svg(
        shadow() + bear_body(150, 216, pose="stand", paws="none", lean=-5)
        + bear_head(146, 122, expr="smile", strong_blush=True, rot=-8)
        + f'<ellipse cx="200" cy="154" rx="20" ry="15" transform="rotate(24 200 154)" fill="{FUR}" stroke="{OL}" stroke-width="3.8"/>'
        + daisy(56, 184, r=19, rot=10)
    )
    s3 = render_svg(
        shadow() + bear_body(150, 218, pose="sit", paws="none")
        + bear_head(150, 122, expr="smile", strong_blush=True, rot=4)
        + f'<ellipse cx="94" cy="154" rx="20" ry="15" transform="rotate(-24 94 154)" fill="{FUR}" stroke="{OL}" stroke-width="3.8"/>'
        + f'<ellipse cx="206" cy="154" rx="20" ry="15" transform="rotate(24 206 154)" fill="{FUR}" stroke="{OL}" stroke-width="3.8"/>'
        + daisy(52, 194, r=18, rot=14)
    )
    s4 = render_svg(
        shadow() + bear_body(150, 216, pose="sit", paws="none", lean=-6)
        + bear_head(146, 122, expr="wink", strong_blush=True, rot=-10)
        + f'<ellipse cx="90" cy="156" rx="20" ry="15" transform="rotate(-28 90 156)" fill="{FUR}" stroke="{OL}" stroke-width="3.8"/>'
        + f'<ellipse cx="202" cy="150" rx="20" ry="15" transform="rotate(20 202 150)" fill="{FUR}" stroke="{OL}" stroke-width="3.8"/>'
        + daisy(52, 198, r=18, rot=14) + daisy(244, 72, r=19, rot=22)
    )
    s5 = with_hero_aura(render_svg(
        shadow(150, 272, 66, 9, op=0.12)
        + bear_body(150, 210, pose="jump", paws="none")
        + bear_head(150, 118, expr="wink", strong_blush=True, rot=6)
        + f'<ellipse cx="94" cy="150" rx="20" ry="15" transform="rotate(-24 94 150)" fill="{FUR}" stroke="{OL}" stroke-width="3.8"/>'
        + f'<ellipse cx="206" cy="150" rx="20" ry="15" transform="rotate(24 206 150)" fill="{FUR}" stroke="{OL}" stroke-width="3.8"/>'
        + daisy(48, 84, r=17, rot=8) + daisy(250, 78, r=20, rot=24) + daisy(48, 206, r=18, rot=16) + daisy(248, 208, r=16, rot=6)
        + sp4(150, 34, r=11, fill="#EFC143", stroke="#C98A1A")
    ), (239, 193, 67))
    return [
        ("Nụ Cúc Ngại Ngùng", s0),
        ("Chạm Nhẹ Má Hồng", s1),
        ("Hoa Cúc Đầu Nở", s2),
        ("Áp Má Cười Hiền", s3),
        ("Nháy Mắt Duyên Dáng", s4),
        ("Rạng Rỡ Hoa Cúc!", s5),
    ]


# =========================================================================== #
#  #79 — LOTSO BUNNY HEADBAND SELFCARE (CHUBBY BEAR + BUNNY SPA ROUTINE!)
# =========================================================================== #
def _bunny_phone(cx=150, cy=212, s=1.0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) scale({s})">'
        f'<ellipse cx="-9" cy="-26" rx="5.5" ry="12" transform="rotate(-10 -9 -26)" fill="#F9A8C9" stroke="{OL}" stroke-width="2.4"/>'
        f'<ellipse cx="9" cy="-26" rx="5.5" ry="12" transform="rotate(10 9 -26)" fill="#F9A8C9" stroke="{OL}" stroke-width="2.4"/>'
        f'<rect x="-19" y="-20" width="38" height="52" rx="9" fill="#F9A8C9" stroke="{OL}" stroke-width="2.8"/>'
        f'<rect x="-13" y="-12" width="26" height="36" rx="4" fill="#FFFDF7"/>'
        f'<line x1="-8" y1="-4" x2="8" y2="-4" stroke="#E05C80" stroke-width="2.4" stroke-linecap="round"/>'
        f'<line x1="-8" y1="6" x2="8" y2="6" stroke="#95C799" stroke-width="2.4" stroke-linecap="round"/></g>'
    )


def _lavender_headband(cx=150, cy=68, bouncy=False, rot=0) -> str:
    ang = 28 if bouncy else 16
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot})">'
        f'<ellipse cx="-26" cy="-26" rx="13" ry="30" transform="rotate(-{ang} -26 -26)" fill="#CFA0CB" stroke="{OL}" stroke-width="3.4"/>'
        f'<ellipse cx="-26" cy="-24" rx="6.5" ry="19" transform="rotate(-{ang} -26 -24)" fill="#FBCFE8"/>'
        f'<ellipse cx="26" cy="-26" rx="13" ry="30" transform="rotate({ang} 26 -26)" fill="#CFA0CB" stroke="{OL}" stroke-width="3.4"/>'
        f'<ellipse cx="26" cy="-24" rx="6.5" ry="19" transform="rotate({ang} 26 -24)" fill="#FBCFE8"/>'
        f'<path d="M -56,14 Q -36,-8 0,-10 Q 36,-8 56,14 Q 30,2 0,2 Q -30,2 -56,14 Z" fill="#E3C7F0" stroke="#7A4C9E" stroke-width="3.0"/>'
        f'<path d="M -2,-4 C -16,-16 -26,-6 -18,4 C -12,10 -4,6 -2,2 Z M 2,-4 C 16,-16 26,-6 18,4 C 12,10 4,6 2,2 Z" fill="#E57294" stroke="{OL}" stroke-width="2.2"/>'
        f'<circle cx="0" cy="-1" r="5" fill="#F49CB5" stroke="{OL}" stroke-width="2.2"/></g>'
    )


def build_79_bunny_selfcare() -> list[tuple[str, Image.Image]]:
    s0 = render_svg(shadow() + bear_body(150, 218, pose="sit", paws="center", lean=-5) + _bunny_phone(148, 212) + bear_head(146, 124, expr="curious", rot=-8))
    s1 = render_svg(shadow() + bear_body(150, 218, pose="sit", paws="center", lean=5) + bear_head(154, 122, expr="smile", rot=6) + '<g transform="translate(152,218) scale(0.66)">' + _lavender_headband(0, 0) + '</g>')
    s2 = render_svg(shadow() + bear_body(150, 216, pose="stand", paws="wide_up", lean=-4) + bear_head(148, 124, expr="smile", strong_blush=True, rot=-6) + _lavender_headband(144, 68, rot=-6))
    s3 = render_svg(
        shadow() + bear_body(150, 218, pose="sit", paws="down")
        + bear_head(150, 124, expr="calm_closed", sheet_mask=True) + _lavender_headband(150, 68)
        + strawberry(46, 134, s=0.76, rot=-14) + strawberry(254, 134, s=0.76, rot=14) + strawberry(250, 224, s=0.72, rot=10)
    )
    s4 = render_svg(
        shadow() + bear_body(150, 216, pose="walk", paws="wave_r", lean=-8)
        + bear_head(144, 122, expr="wink", strong_blush=True, rot=-12) + _lavender_headband(136, 68, rot=-12)
        + heart(46, 114, s=13, fill="#E11D48", rot=-12) + heart(252, 108, s=13, fill="#E57294", rot=12)
    )
    s5 = with_hero_aura(render_svg(
        shadow(150, 272, 62, 8, op=0.12)
        + bear_body(150, 206, pose="jump", paws="wide_up")
        + bear_head(150, 116, expr="happy_squint", strong_blush=True, rot=5) + _lavender_headband(152, 60, bouncy=True, rot=5)
        + heart(44, 86, s=15, fill="#E57294", rot=-14) + heart(256, 86, s=15, fill="#E11D48", rot=14)
        + heart(48, 198, s=12, fill="#F47294", rot=-10) + sp4(252, 196, r=11, fill="#FDE047", stroke="#93528B")
    ), (147, 82, 139))
    return [
        ("Lướt Điện Thoại Thỏ", s0),
        ("Cầm Bờm Tai Thỏ", s1),
        ("Đeo Bờm Nơ Xinh", s2),
        ("Đắp Mặt Nạ Dâu", s3),
        ("Nghiêng Đầu Tự Tin", s4),
        ("Rạng Ngời Self-Care!", s5),
    ]


# =========================================================================== #
#  #80 NEW — LOTSO BERRY GIFT BOX PARTY (REPLACES BERRY SQUAD!)
# =========================================================================== #
def _gift_box(cx=150, cy=218, lid_mode="closed", s=1.0) -> str:
    """Blush-pink gift box with cream ribbon bow (closed / ajar / open!)."""
    parts = [f'<g transform="translate({cx},{cy}) scale({s})">']
    # Box base
    parts.append(
        f'<rect x="-66" y="-22" width="132" height="72" rx="10" fill="#F9B4C8" stroke="{OL}" stroke-width="3.8"/>'
        f'<rect x="-14" y="-22" width="28" height="72" fill="#FFF3DC" stroke="{OL}" stroke-width="2.4"/>'
    )
    if lid_mode == "closed":
        parts.append(
            f'<rect x="-74" y="-44" width="148" height="24" rx="7" fill="#F396B4" stroke="{OL}" stroke-width="3.8"/>'
            f'<rect x="-14" y="-44" width="28" height="24" fill="#FFF3DC" stroke="{OL}" stroke-width="2.4"/>'
            # Cream ribbon bow on top!
            f'<path d="M -2,-44 C -24,-68 -44,-54 -34,-42 C -26,-34 -10,-40 -2,-44 Z M 2,-44 C 24,-68 44,-54 34,-42 C 26,-34 10,-40 2,-44 Z" fill="#FFF3DC" stroke="{OL}" stroke-width="3.0"/>'
            f'<circle cx="0" cy="-44" r="7" fill="#FDE7A9" stroke="{OL}" stroke-width="2.6"/>'
        )
    elif lid_mode == "tilted":
        parts.append(
            f'<g transform="translate(-54,-52) rotate(-26)">'
            f'<rect x="-46" y="-12" width="128" height="22" rx="7" fill="#F396B4" stroke="{OL}" stroke-width="3.6"/>'
            f'<rect x="6" y="-12" width="26" height="22" fill="#FFF3DC" stroke="{OL}" stroke-width="2.2"/></g>'
        )
    parts.append("</g>")
    return "".join(parts)


def _party_hat(cx=150, cy=62, rot=0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot})">'
        f'<polygon points="-24,14 0,-34 24,14" fill="#F5CB69" stroke="{OL}" stroke-width="3.2" stroke-linejoin="round"/>'
        f'<line x1="-14" y1="-4" x2="14" y2="-4" stroke="#F396B4" stroke-width="5.0"/>'
        f'<circle cx="0" cy="-36" r="8" fill="#FFF3DC" stroke="{OL}" stroke-width="2.4"/>'
        f'</g>'
    )


def _strawberry_cupcake(cx=150, cy=212, s=1.0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) scale({s})">'
        f'<polygon points="-20,4 20,4 15,28 -15,28" fill="#F5CB69" stroke="{OL}" stroke-width="2.6" stroke-linejoin="round"/>'
        f'<path d="M -24,4 C -26,-12 -10,-20 0,-18 C 10,-20 26,-12 24,4 Z" fill="#FFFDF5" stroke="#D9A8B8" stroke-width="2.6"/>'
        f'<rect x="-3" y="-36" width="6" height="18" rx="2" fill="#F396B4" stroke="{OL}" stroke-width="2.0"/>'
        f'<path d="M 0,-48 C -6,-40 -4,-35 0,-35 C 4,-35 6,-40 0,-48 Z" fill="#FDE047" stroke="#EA580C" stroke-width="1.8"/>'
        + strawberry(12, -10, s=0.44, ripe=True, rot=14)
        + '</g>'
    )


def build_80_gift_box() -> list[tuple[str, Image.Image]]:
    # S0: Closed blush-pink gift box with cream ribbon — just 2 plush bear ears & eyes peeking out!
    s0 = render_svg(
        shadow(150, 270, 82, 10)
        + f'<circle cx="108" cy="144" r="19" fill="{FUR}" stroke="{OL}" stroke-width="4.0"/><circle cx="109" cy="145" r="10" fill="{CREAM}"/>'
        + f'<circle cx="192" cy="144" r="19" fill="{FUR}" stroke="{OL}" stroke-width="4.0"/><circle cx="191" cy="145" r="10" fill="{CREAM}"/>'
        + f'<ellipse cx="150" cy="170" rx="54" ry="26" fill="{FUR}" stroke="{OL}" stroke-width="4.0"/>'
        + f'<circle cx="132" cy="166" r="5.5" fill="{EYE}"/><circle cx="130" cy="164" r="2.0" fill="#FFFFFF"/>'
        + f'<circle cx="168" cy="166" r="5.5" fill="{EYE}"/><circle cx="166" cy="164" r="2.0" fill="#FFFFFF"/>'
        + _gift_box(150, 218, lid_mode="closed")
    )
    # S1: Pushing box lid ajar, chubby paws gripping box rim curiously!
    s1 = render_svg(
        shadow(150, 270, 82, 10)
        + bear_head(150, 148, scale=0.88, expr="curious", rot=6)
        + _gift_box(150, 218, lid_mode="tilted")
        + f'<ellipse cx="104" cy="194" rx="18" ry="13" fill="{FUR}" stroke="{OL}" stroke-width="3.6"/>'
        + f'<ellipse cx="196" cy="194" rx="18" ry="13" fill="{FUR}" stroke="{OL}" stroke-width="3.6"/>'
    )
    # S2: Popping halfway out of gift box wearing pastel party hat!
    s2 = render_svg(
        shadow(150, 270, 82, 10)
        + bear_body(150, 194, pose="hidden", paws="wide_up", lean=-4)
        + bear_head(146, 122, scale=0.92, expr="smile", strong_blush=True, rot=-6)
        + _party_hat(140, 62, rot=-8)
        + _gift_box(150, 224, lid_mode="open")
        + sp4(56, 86, r=9) + sp4(246, 90, r=9)
    )
    # S3: Stepping completely out hugging strawberry cupcake with lit candle!
    s3 = render_svg(
        shadow() + bear_body(150, 216, pose="sit", paws="none")
        + _strawberry_cupcake(150, 216, s=1.08)
        + f'<ellipse cx="110" cy="214" rx="20" ry="15" transform="rotate(18 110 214)" fill="{FUR}" stroke="{OL}" stroke-width="3.8"/>'
        + f'<ellipse cx="190" cy="214" rx="20" ry="15" transform="rotate(-18 190 214)" fill="{FUR}" stroke="{OL}" stroke-width="3.8"/>'
        + bear_head(150, 122, expr="sparkle_eyes", strong_blush=True, rot=4)
        + _party_hat(154, 62, rot=6)
    )
    # S4: Making a wish with happy squint eyes as gold stars & hearts pop!
    s4 = render_svg(
        shadow() + bear_body(150, 216, pose="sit", paws="none", lean=-5)
        + _strawberry_cupcake(148, 216, s=1.10)
        + f'<ellipse cx="108" cy="214" rx="20" ry="15" transform="rotate(16 108 214)" fill="{FUR}" stroke="{OL}" stroke-width="3.8"/>'
        + f'<ellipse cx="188" cy="214" rx="20" ry="15" transform="rotate(-16 188 214)" fill="{FUR}" stroke="{OL}" stroke-width="3.8"/>'
        + bear_head(146, 122, expr="happy_squint", strong_blush=True, rot=-8)
        + _party_hat(138, 62, rot=-10)
        + star5(52, 82, r=12) + star5(248, 86, r=13) + heart(50, 178, s=11, fill="#F396B4") + heart(250, 178, s=11, fill="#C43E67")
    )
    # S5: Jumping arms wide celebrating beside open gift box, cupcake & confetti shower!
    s5 = with_hero_aura(render_svg(
        shadow(150, 272, 74, 9, op=0.12)
        + _gift_box(66, 242, lid_mode="open", s=0.58)
        + _strawberry_cupcake(238, 232, s=0.92)
        + bear_body(150, 204, pose="jump", paws="wide_up")
        + bear_head(150, 114, expr="big_smile", strong_blush=True, rot=4)
        + _party_hat(154, 54, rot=6)
        + star5(46, 78, r=13) + star5(254, 78, r=13) + sp4(88, 42, r=9) + sp4(212, 42, r=9)
        + heart(44, 152, s=12, fill="#C43E67", rot=-12) + heart(256, 152, s=12, fill="#F396B4", rot=12)
    ), (196, 62, 103))
    return [
        ("Hộp Quà Lấp Ló", s0),
        ("Đẩy Nắp Tò Mò", s1),
        ("Chui Ra Mũ Tiệc", s2),
        ("Ôm Bánh Cupcake", s3),
        ("Nhắm Mắt Ước Nguyện", s4),
        ("Nhảy Mừng Confetti!", s5),
    ]


# =========================================================================== #
#  MAIN GENERATOR + CONTACT SHEET (`previews/assets_contact_sheet_lotso.png`)
# =========================================================================== #
def main():
    builders = [
        ("lotso_strawberry",     build_71_strawberry),
        ("lotso_milk_cafe",      build_72_milk_cafe),
        ("lotso_flower_crown",   build_73_flower_crown),
        ("lotso_overalls",       build_74_overalls),
        ("lotso_lofi",           build_75_lofi),
        ("lotso_mood_detox",     build_76_mood_detox),
        ("lotso_sweet_dreams",   build_77_sweet_dreams),
        ("lotso_daisy_glow",     build_78_daisy_glow),
        ("lotso_bunny_selfcare", build_79_bunny_selfcare),
        ("lotso_gift_box",       build_80_gift_box),
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
        print(f"  [LOTSO v4] {slug:24s} -> 6 chubby dynamic 300x300 RGBA PNGs saved")

    print(f"Total Lotso sprites saved: {total}/60 (100% unique SHA-256 hashes!)")

    rows = [
        ("71. Strawberry Harvest",    "lotso_strawberry",     (255, 247, 249), (217, 85, 122)),
        ("72. Strawberry Milk Cafe",  "lotso_milk_cafe",      (255, 248, 245), (214, 80, 118)),
        ("73. Berry Flower Crown",    "lotso_flower_crown",   (255, 249, 245), (204, 63, 99)),
        ("74. Overalls Workshop",     "lotso_overalls",       (255, 251, 240), (89, 140, 94)),
        ("75. LoFi Earphones Flow",   "lotso_lofi",           (255, 244, 242), (184, 62, 98)),
        ("76. Mood Detox Comic",      "lotso_mood_detox",     (253, 246, 250), (170, 58, 96)),
        ("77. Floral Sweet Dreams",   "lotso_sweet_dreams",   (255, 247, 251), (180, 75, 106)),
        ("78. Daisy Cheek Glow",      "lotso_daisy_glow",     (255, 249, 242), (174, 67, 92)),
        ("79. Bunny Headband Spa",    "lotso_bunny_selfcare", (252, 247, 252), (147, 82, 139)),
        ("80. Berry Gift Box Party",  "lotso_gift_box",       (255, 246, 249), (196, 62, 103)),
    ]

    cell_w, cell_h = 204, 272
    left_w, pad, hdr_h = 248, 18, 84
    W = pad * 2 + left_w + cell_w * 6
    H = pad * 2 + hdr_h + cell_h * len(rows)

    sheet = Image.new("RGB", (W, H), (255, 247, 249))
    draw = ImageDraw.Draw(sheet)
    try:
        f_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 27)
        f_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 15.5)
        f_row = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 15)
        f_lbl = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 13)
        f_tiny = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 11)
    except Exception:
        f_title = f_sub = f_row = f_lbl = f_tiny = ImageFont.load_default()

    draw.rectangle([0, 0, W, hdr_h], fill=(196, 62, 103))
    draw.text((pad, 14), "LOTSO CHUBBY PLUSH BEAR COLLECTION — #71–#80 (DYNAMIC • 60 UNIQUE SPRITES)", fill=(255, 255, 255), font=f_title)
    draw.text((pad, 50), "Chubby Plush Teddy Bear Silhouette • New #72 Milk Cafe & #80 Gift Box Party • Transparent 300x300 RGBA • 162px + 44px Preview", fill=(255, 243, 220), font=f_sub)

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
                outline=(acc_c if is_f else (238, 224, 228)), width=2 if is_f else 1,
            )
            big = im.resize((162, 162), Image.LANCZOS)
            sheet.paste(big, (x0 + (cell_w - 162) // 2, y0 + 16), big)

            small = im.resize((44, 44), Image.LANCZOS)
            sx, sy = x0 + cell_w - 56, y0 + 182
            draw.rounded_rectangle([sx - 3, sy - 3, sx + 47, sy + 47], radius=6, fill=(255, 250, 252), outline=(230, 214, 220), width=1)
            sheet.paste(small, (sx, sy), small)

            draw.text((x0 + 12, y0 + 184), f"S{s_i} • {pcts[s_i]}", fill=acc_c, font=f_tiny)
            draw.text((x0 + 12, y0 + 206), lbl, fill=(87, 34, 52), font=f_lbl)
            draw.text((sx + 6, sy + 49), "44px", fill=(160, 138, 146), font=f_tiny)

    PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PREVIEWS_DIR / "assets_contact_sheet_lotso.png"
    sheet.save(out_path, "PNG", optimize=True)
    print(f"  [PREVIEW] Saved {out_path} ({sheet.size[0]}x{sheet.size[1]})")


if __name__ == "__main__":
    main()
