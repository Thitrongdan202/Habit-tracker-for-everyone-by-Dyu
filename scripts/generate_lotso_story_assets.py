"""
generate_lotso_story_assets.py — v4.1 Precision Plush Bear Art Overhaul for 10 Lotso Themes (#71-#80)
Fixes ALL 3 core drawing flaws across ALL 60 Lotso sprites:
  1. Natural Curved Chubby Teddy Arms: ZERO detached round/oval blob arms! Every single arm
     uses seamless tapered Bezier curves smoothly flowing out of the plush bear shoulders
     with clear elbow bend (hugging, reaching down to pick flowers, cupping cheeks, waving!).
  2. Clean Head-Gear / Headband Fit: Snug lavender bunny headband (#79) & flower crown (#73)
     hugging Lotso's crown neatly between his round plush bear ears.
  3. Zero Contact Sheet Text Collision: Every label is crisp (<=16 chars), auto-measured via
     PIL textlength/textbbox, and hard-asserted `text_right_x <= preview_44px_left_x - 10`!

Rebuilt Signature Storylines:
  - #77 Floral Sweet Dreams: Strolling admiring red flowers -> bending to pick first flower ->
    tying small bouquet -> hugging bouquet looking at cloud -> lavender sheep smiling in cloud ->
    waving gently beside bouquet & fluffy sheep dream!
  - #78 Daisy Cheek Glow: Walking briskly spotting tiny daisy on ground -> bending down picking up daisy ->
    sitting admiring daisy in paws -> tucking daisy behind round ear -> cupping cheeks winking ->
    radiant cheek-cup wink with floating daisy petals!
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


def with_hero_aura(im: Image.Image, rgb: tuple[int, int, int], cy: int = 152, alpha: int = 64) -> Image.Image:
    aura = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
    ad = ImageDraw.Draw(aura)
    r, g, b = rgb
    ad.ellipse([36, cy - 108, 264, cy + 108], fill=(r, g, b, alpha))
    ad.ellipse([74, cy - 74, 226, cy + 74], fill=(255, 250, 232, 90))
    aura = aura.filter(ImageFilter.GaussianBlur(radius=22))
    return Image.alpha_composite(aura, im)


# =========================================================================== #
#  v4.1 3-LAYER SEAMLESS SILHOUETTE TEDDY ARM ENGINE (48-STEP CURVATURE-CLAMPED)
# =========================================================================== #
def _norm(dx: float, dy: float) -> tuple[float, float]:
    d = math.hypot(dx, dy)
    if d < 1e-6:
        return (0.0, -1.0)
    return (dx / d, dy / d)


def _to_local(pt: tuple[float, float], cx: float, cy: float, lean_deg: float) -> tuple[float, float]:
    dx, dy = pt[0] - cx, pt[1] - cy
    rad = math.radians(-lean_deg)
    ca, sa = math.cos(rad), math.sin(rad)
    return (dx * ca - dy * sa, dx * sa + dy * ca)


def _clamp_shoulder_local(
    p0: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
    rx: float,
    ry: float,
) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]:
    """Pulls teddy shoulder anchor deep inside upper torso interior (ZERO shoulder bumps/horns/gaps)."""
    lx, ly = p0
    side = -1.0 if lx < 0 else 1.0
    nx0 = side * max(rx * 0.24, min(abs(lx), rx * 0.46))
    ny0 = max(-ry * 0.34, min(ly, -ry * 0.10))
    np0 = (nx0, ny0)
    np1 = p1
    if math.hypot(p1[0] - nx0, p1[1] - ny0) < 14.0:
        np1 = (nx0 + side * 16.0, ny0 + 14.0)
    return np0, np1, p2


def _smooth_poly(pts: list[tuple[float, float]], passes: int = 3) -> list[tuple[float, float]]:
    cur = list(pts)
    n = len(cur)
    for _ in range(passes):
        nxt = [cur[0]]
        for i in range(1, n - 1):
            nxt.append((
                0.25 * cur[i - 1][0] + 0.5 * cur[i][0] + 0.25 * cur[i + 1][0],
                0.25 * cur[i - 1][1] + 0.5 * cur[i][1] + 0.25 * cur[i + 1][1],
            ))
        nxt.append(cur[-1])
        cur = nxt
    return cur


def _enforce_monotonic(
    pts: list[tuple[float, float]],
    tangents: list[tuple[float, float]],
) -> list[tuple[float, float]]:
    out = [pts[0]]
    for i in range(1, len(pts)):
        px, py = out[-1]
        cx, cy = pts[i]
        tx, ty = tangents[i]
        dot = (cx - px) * tx + (cy - py) * ty
        if dot < 0.0:
            cx = cx - dot * tx + 0.35 * tx
            cy = cy - dot * ty + 0.35 * ty
        out.append((cx, cy))
    return out


def _sample_arm_mesh(
    p0: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
    w0: float,
    w1: float,
    w2: float,
    steps: int = 48,
    body_ref: tuple[float, float] = (0.0, 4.0),
) -> dict:
    """High-density 48-step curvature-clamped chubby plush teddy arm tube."""
    x0, y0 = p0
    x1, y1 = p1
    x2, y2 = p2
    centers: list[tuple[float, float]] = []
    tangents: list[tuple[float, float]] = []
    normals: list[tuple[float, float]] = []
    left_pts: list[tuple[float, float]] = []
    right_pts: list[tuple[float, float]] = []

    ddx = 2.0 * (x0 - 2.0 * x1 + x2)
    ddy = 2.0 * (y0 - 2.0 * y1 + y2)

    for i in range(steps + 1):
        t = i / steps
        omt = 1.0 - t
        bx = omt * omt * x0 + 2.0 * omt * t * x1 + t * t * x2
        by = omt * omt * y0 + 2.0 * omt * t * y1 + t * t * y2
        dx = 2.0 * omt * (x1 - x0) + 2.0 * t * (x2 - x1)
        dy = 2.0 * omt * (y1 - y0) + 2.0 * t * (y2 - y1)
        spd = math.hypot(dx, dy)
        tx, ty = _norm(dx, dy)
        nx, ny = -ty, tx
        w = omt * omt * w0 + 2.0 * omt * t * w1 + t * t * w2
        kappa = (dx * ddy - dy * ddx) / max(spd ** 3, 1e-5)
        w_left = w
        w_right = w
        if abs(kappa) > 1e-4:
            max_r = 0.78 / abs(kappa)
            if kappa > 0:
                w_left = min(w_left, max_r)
            else:
                w_right = min(w_right, max_r)
        centers.append((bx, by))
        tangents.append((tx, ty))
        normals.append((nx, ny))
        left_pts.append((bx + nx * w_left, by + ny * w_left))
        right_pts.append((bx - nx * w_right, by - ny * w_right))

    left_pts = _smooth_poly(_enforce_monotonic(left_pts, tangents), passes=4)
    right_pts = _smooth_poly(_enforce_monotonic(right_pts, tangents), passes=4)

    tx2, ty2 = tangents[-1]
    nx2, ny2 = normals[-1]
    tip_cap: list[tuple[float, float]] = []
    cap_steps = 14
    for k in range(1, cap_steps):
        ang = math.pi * (k / cap_steps)
        cn = math.cos(ang)
        ct = math.sin(ang) * 1.08
        tip_cap.append((x2 + nx2 * cn * w2 + tx2 * ct * w2, y2 + ny2 * cn * w2 + ty2 * ct * w2))

    tx0, ty0 = tangents[0]
    nx0, ny0 = normals[0]
    root_cap: list[tuple[float, float]] = []
    root_steps = 8
    for k in range(1, root_steps):
        ang = math.pi * (k / root_steps)
        cn = -math.cos(ang)
        ct = -math.sin(ang) * 0.62
        root_cap.append((x0 + nx0 * cn * w0 + tx0 * ct * w0, y0 + ny0 * cn * w0 + ty0 * ct * w0))

    chk = steps // 4
    dl = math.hypot(left_pts[chk][0] - body_ref[0], left_pts[chk][1] - body_ref[1])
    dr = math.hypot(right_pts[chk][0] - body_ref[0], right_pts[chk][1] - body_ref[1])
    inner_is_right = dr < dl

    def _pts_d(pts: list[tuple[float, float]], close: bool = False) -> str:
        segs = [f"M {pts[0][0]:.1f},{pts[0][1]:.1f}"]
        segs.extend(f"L {px:.1f},{py:.1f}" for px, py in pts[1:])
        if close:
            segs.append("Z")
        return " ".join(segs)

    full_poly = left_pts + tip_cap + list(reversed(right_pts)) + root_cap
    full_d = _pts_d(full_poly, close=True)

    def sub_fill_d(t_start: float) -> str:
        idx = max(1, min(steps - 2, int(round(t_start * steps))))
        tx_i, ty_i = tangents[idx]
        l_i, r_i = left_pts[idx], right_pts[idx]
        mid_back = (
            0.5 * (l_i[0] + r_i[0]) - tx_i * 5.0,
            0.5 * (l_i[1] + r_i[1]) - ty_i * 5.0,
        )
        poly = left_pts[idx:] + tip_cap + list(reversed(right_pts[idx:])) + [mid_back]
        return _pts_d(poly, close=True)

    def sub_stroke_d(t_in: float, t_out: float) -> str:
        i_in = max(1, min(steps - 1, int(round(t_in * steps))))
        i_out = max(1, min(steps - 1, int(round(t_out * steps))))
        if inner_is_right:
            pts = right_pts[i_in:] + list(reversed(tip_cap)) + list(reversed(left_pts[i_out:]))
        else:
            pts = left_pts[i_in:] + tip_cap + list(reversed(right_pts[i_out:]))
        return _pts_d(pts, close=False)

    return {
        "full_d": full_d,
        "sub_fill_d": sub_fill_d,
        "sub_stroke_d": sub_stroke_d,
        "p2": p2,
        "t2": tangents[-1],
        "n2": normals[-1],
        "w2": w2,
    }


def _paw_pad_svg(mesh: dict) -> str:
    x2, y2 = mesh["p2"]
    t2x, t2y = mesh["t2"]
    w2 = mesh["w2"]
    px = x2 + t2x * (w2 * 0.25)
    py = y2 + t2y * (w2 * 0.25)
    return f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{w2 * 0.42:.1f}" fill="#FFF5E6" fill-opacity="0.72"/>'


def arm_spec(
    p0: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
    w0: float = 13.8,
    w1: float = 11.8,
    w2: float = 10.2,
    fill: str | None = None,
    stroke: str = OL,
    sw: float = 4.0,
    paw_pad: bool = False,
    layer: str = "front",
    local: bool = False,
    t_fill: float = 0.24,
    t_in: float = 0.28,
    t_out: float = 0.48,
    t_oh: float = 0.32,
) -> dict:
    return {
        "p0": p0, "p1": p1, "p2": p2,
        "w0": w0, "w1": w1, "w2": w2,
        "fill": fill, "stroke": stroke, "sw": sw,
        "paw_pad": paw_pad, "layer": layer, "local": local,
        "t_fill": t_fill, "t_in": t_in, "t_out": t_out, "t_oh": t_oh,
    }


def _bear_torso_d(rx: float, ry: float) -> str:
    """100% C1-continuous chubby plush teddy pear torso (ZERO upper-shoulder corners!)."""
    top_y = -ry + 4.0
    mid_y = ry * 0.16
    return (
        f"M 0,{top_y:.1f} "
        f"C {rx * 0.66:.1f},{top_y:.1f} {rx * 1.04:.1f},{-ry * 0.32:.1f} {rx * 1.04:.1f},{mid_y:.1f} "
        f"C {rx * 1.04:.1f},{ry * 0.68:.1f} {rx * 0.64:.1f},{ry:.1f} 0,{ry:.1f} "
        f"C {-rx * 0.64:.1f},{ry:.1f} {-rx * 1.04:.1f},{ry * 0.68:.1f} {-rx * 1.04:.1f},{mid_y:.1f} "
        f"C {-rx * 1.04:.1f},{-ry * 0.32:.1f} {-rx * 0.66:.1f},{top_y:.1f} 0,{top_y:.1f} Z"
    )


def bear_arm(
    p0: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
    w0: float = 15.0,
    w1: float = 13.0,
    w2: float = 11.2,
    fill: str = FUR,
    stroke: str = OL,
    sw: float = 4.0,
    paw_pad: bool = False,
    seamless_shoulder: bool = True,
) -> str:
    """Standalone high-density 48-step curved teddy arm (for box-rim paws etc.)."""
    mesh = _sample_arm_mesh(p0, p1, p2, w0, w1, w2)
    if seamless_shoulder:
        out = (
            f'<path d="{mesh["full_d"]}" fill="{fill}" stroke="none"/>'
            f'<path d="{mesh["sub_stroke_d"](0.24, 0.24)}" fill="none" stroke="{stroke}" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>'
        )
    else:
        out = (
            f'<path d="{mesh["full_d"]}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{sw}" stroke-linejoin="round"/>'
        )
    if paw_pad:
        out += _paw_pad_svg(mesh)
    return out


# =========================================================================== #
#  REUSABLE VECTOR DECORATIONS
# =========================================================================== #
def shadow(cx=150, cy=270, rx=74, ry=9.5, op=0.14) -> str:
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


def sp4(cx, cy, r=11, fill="#FDE047", stroke="#D97706", sw=2.1) -> str:
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
#  CHUBBY PLUSH BEAR LOTSO RIG (SEAMLESS CURVED TEDDY ARMS + WHITE TOE-BEANS!)
# =========================================================================== #
def _toe_bean_foot(fx, fy, rot=0) -> str:
    return (
        f'<g transform="translate({fx},{fy}) rotate({rot})">'
        f'<ellipse cx="0" cy="0" rx="24" ry="19" fill="{FUR}" stroke="{OL}" stroke-width="3.9"/>'
        f'<ellipse cx="0" cy="4" rx="12.5" ry="9.0" fill="#FFFFFF"/>'
        f'<circle cx="-8.5" cy="-7.5" r="3.6" fill="#FFFFFF"/>'
        f'<circle cx="0" cy="-10.0" r="3.6" fill="#FFFFFF"/>'
        f'<circle cx="8.5" cy="-7.5" r="3.5" fill="#FFFFFF"/>'
        f'</g>'
    )


def bear_body(
    cx=150,
    cy=216,
    rx=62,
    ry=46,
    pose="sit",
    paws="down",
    outfit="none",
    lean=0,
    arms: list[dict] | None = None,
    mid_props: str = "",
    head_svg: str = "",
    custom_arms: str = "",
) -> str:
    """v4.1 3-Layer Seamless Silhouette Plush Bear Body:
      Layer 1: Unified dark outline (2*sw round join) of C1 pear teddy torso + ALL arms.
      Layer 2: Unified seamless fill fusing shoulders 100% into torso + belly/outfit.
      Mid-Layer: World-space props held in front of torso (`mid_props`).
      Layer 3: Foreground forearm fill + smooth inner forearm crease (ZERO shoulder horns!).
      Head + Over-Head Pass: `head_svg` followed by upper forearms (`layer == 'over_head'`)."""
    torso_c = "#598C5E" if outfit in ("green_shirt", "overalls") else FUR
    arm_c = torso_c
    sx_l, sx_r = -rx * 0.54, rx * 0.54
    sy = -ry * 0.32
    spec_list: list[dict] = []

    if paws == "down":
        spec_list += [
            arm_spec((sx_l, sy), (sx_l - 24, sy + 14), (sx_l - 12, sy + 36), 14.2, 12.2, 10.4, fill=arm_c, layer="front", local=True, t_fill=0.30, t_in=0.30, t_out=0.54),
            arm_spec((sx_r, sy), (sx_r + 24, sy + 14), (sx_r + 12, sy + 36), 14.2, 12.2, 10.4, fill=arm_c, layer="front", local=True, t_fill=0.30, t_in=0.30, t_out=0.54),
        ]
    elif paws == "wide_up":
        spec_list += [
            arm_spec((sx_l, sy), (sx_l - 26, sy - 4), (sx_l - 34, sy - 30), 14.2, 12.2, 10.6, fill=arm_c, paw_pad=(arm_c == FUR), layer="out", local=True),
            arm_spec((sx_r, sy), (sx_r + 26, sy - 4), (sx_r + 34, sy - 30), 14.2, 12.2, 10.6, fill=arm_c, paw_pad=(arm_c == FUR), layer="out", local=True),
        ]
    elif paws == "wave_r":
        spec_list += [
            arm_spec((sx_l, sy), (sx_l - 22, sy + 14), (sx_l - 10, sy + 34), 14.0, 12.0, 10.2, fill=arm_c, layer="front", local=True, t_fill=0.30, t_in=0.30, t_out=0.54),
            arm_spec((sx_r, sy), (sx_r + 28, sy - 4), (sx_r + 34, sy - 32), 14.2, 12.2, 10.6, fill=arm_c, paw_pad=(arm_c == FUR), layer="out", local=True),
        ]
    elif paws == "walk_swing":
        spec_list += [
            arm_spec((sx_l, sy), (sx_l - 24, sy + 16), (sx_l - 26, sy + 32), 14.0, 12.0, 10.2, fill=arm_c, layer="out", local=True),
            arm_spec((sx_r, sy), (sx_r + 26, sy + 4), (sx_r + 16, sy + 24), 14.0, 12.0, 10.2, fill=arm_c, layer="front", local=True, t_fill=0.30, t_in=0.30, t_out=0.54),
        ]
    elif paws == "hug_center":
        spec_list += [
            arm_spec((sx_l, sy), (sx_l - 18, sy + 22), (-18, sy + 22), 13.8, 11.8, 10.2, fill=arm_c, layer="front", local=True, t_fill=0.24, t_in=0.28, t_out=0.48),
            arm_spec((sx_r, sy), (sx_r + 18, sy + 22), (18, sy + 22), 13.8, 11.8, 10.2, fill=arm_c, layer="front", local=True, t_fill=0.24, t_in=0.28, t_out=0.48),
        ]

    if arms:
        spec_list.extend(arms)

    built_arms: list[tuple[dict, dict]] = []
    for sp in spec_list:
        if sp["local"]:
            lp0, lp1, lp2 = sp["p0"], sp["p1"], sp["p2"]
        else:
            lp0 = _to_local(sp["p0"], cx, cy, lean)
            lp1 = _to_local(sp["p1"], cx, cy, lean)
            lp2 = _to_local(sp["p2"], cx, cy, lean)
        lp0, lp1, lp2 = _clamp_shoulder_local(lp0, lp1, lp2, rx, ry)
        mesh = _sample_arm_mesh(lp0, lp1, lp2, sp["w0"], sp["w1"], sp["w2"])
        built_arms.append((sp, mesh))

    tf = f'translate({cx},{cy}) rotate({lean})'
    torso_d = _bear_torso_d(rx, ry)
    torso_sw = 4.1

    feet_svg = ""
    if pose == "sit":
        feet_svg = _toe_bean_foot(-43, 30, rot=-18) + _toe_bean_foot(43, 30, rot=18)
    elif pose == "float":
        feet_svg = _toe_bean_foot(-35, 42, rot=-28) + _toe_bean_foot(35, 42, rot=28)
    elif pose == "jump":
        feet_svg = _toe_bean_foot(-40, 38, rot=-34) + _toe_bean_foot(40, 38, rot=34)
    elif pose == "walk":
        feet_svg = (
            f'<ellipse cx="-29" cy="44" rx="22" ry="12.5" transform="rotate(-12 -29 44)" fill="{FUR_SHD}" stroke="{OL}" stroke-width="3.8"/>'
            f'<ellipse cx="27" cy="34" rx="22" ry="12.5" transform="rotate(24 27 34)" fill="{FUR_SHD}" stroke="{OL}" stroke-width="3.8"/>'
        )
    elif pose == "hidden":
        feet_svg = ""
    else:
        feet_svg = (
            f'<ellipse cx="-27" cy="42" rx="22" ry="12.5" fill="{FUR_SHD}" stroke="{OL}" stroke-width="3.8"/>'
            f'<ellipse cx="27" cy="42" rx="22" ry="12.5" fill="{FUR_SHD}" stroke="{OL}" stroke-width="3.8"/>'
        )

    parts: list[str] = []
    if feet_svg:
        parts.append(f'<g transform="{tf}">{feet_svg}</g>')

    # Layer 1 (Unified 2*sw Outline) + Layer 2 (Unified Seamless Fill) + Belly/Outfit
    l1 = [f'<path d="{torso_d}" fill="none" stroke="{OL}" stroke-width="{torso_sw * 2:.1f}" stroke-linejoin="round" stroke-linecap="round"/>']
    l2 = [f'<path d="{torso_d}" fill="{torso_c}" stroke="none"/>']
    for sp, mesh in built_arms:
        a_fill = sp["fill"] if sp["fill"] is not None else arm_c
        l1.append(f'<path d="{mesh["full_d"]}" fill="none" stroke="{sp["stroke"]}" stroke-width="{sp["sw"] * 2:.1f}" stroke-linejoin="round" stroke-linecap="round"/>')
        l2.append(f'<path d="{mesh["full_d"]}" fill="{a_fill}" stroke="none"/>')

    if outfit == "none":
        l2.append(f'<ellipse cx="0" cy="11" rx="{rx * 0.62:.1f}" ry="{ry * 0.68:.1f}" fill="{CREAM}"/>')
    elif outfit == "apron":
        l2.append(
            f'<ellipse cx="0" cy="11" rx="{rx * 0.62:.1f}" ry="{ry * 0.68:.1f}" fill="{CREAM}"/>'
            f'<path d="M -32,-16 L 32,-16 L 40,38 Q 0,46 -40,38 Z" fill="#FFFDF5" stroke="#B87D8C" stroke-width="3.0" stroke-linejoin="round"/>'
            f'<path d="M -26,-16 L -22,-34 M 26,-16 L 22,-34" stroke="#B87D8C" stroke-width="4.0" stroke-linecap="round"/>'
            + strawberry(0, 14, s=0.65, ripe=True)
        )
    elif outfit == "overalls":
        l2.append(
            f'<path d="M -38,-28 L -24,-28 L -24,-4 L 24,-4 L 24,-28 L 38,-28 L 46,12 '
            f'C 48,{ry - 4} 28,{ry} 0,{ry} C -28,{ry} -48,{ry - 4} -46,12 Z" '
            f'fill="{CREAM}" stroke="{OL}" stroke-width="3.6" stroke-linejoin="round"/>'
            f'<circle cx="-29" cy="-4" r="4.5" fill="#B87D4B" stroke="{OL}" stroke-width="2.0"/>'
            f'<circle cx="29" cy="-4" r="4.5" fill="#B87D4B" stroke="{OL}" stroke-width="2.0"/>'
            f'<rect x="-20" y="4" width="40" height="27" rx="8" fill="#FFF8EC" stroke="{OL}" stroke-width="2.4"/>'
            + heart(0, 17, s=8.5, fill="#DE5B73", stroke=OL, sw=1.8)
        )

    parts.append(f'<g transform="{tf}">{"".join(l1)}{"".join(l2)}</g>')

    # Mid-Layer (World Space Props)
    if mid_props:
        parts.append(mid_props)

    # Layer 3 (Foreground Forearms + Smooth Inner Forearm Creases + Paw Pads)
    l3: list[str] = []
    for sp, mesh in built_arms:
        a_fill = sp["fill"] if sp["fill"] is not None else arm_c
        if sp["layer"] == "front":
            l3.append(f'<path d="{mesh["sub_fill_d"](sp["t_fill"])}" fill="{a_fill}" stroke="none"/>')
            l3.append(
                f'<path d="{mesh["sub_stroke_d"](sp["t_in"], sp["t_out"])}" fill="none" '
                f'stroke="{sp["stroke"]}" stroke-width="{sp["sw"]:.1f}" stroke-linecap="round" stroke-linejoin="round"/>'
            )
            if sp["paw_pad"]:
                l3.append(_paw_pad_svg(mesh))
        elif sp["layer"] == "out" and sp["paw_pad"]:
            l3.append(_paw_pad_svg(mesh))
    if custom_arms:
        l3.append(custom_arms)
    if l3:
        parts.append(f'<g transform="{tf}">{"".join(l3)}</g>')

    # Head Layer (World Space)
    if head_svg:
        parts.append(head_svg)

    # Group 4 (Over-Head Pass — Forearm & Paw overlapping cheek/ear/headband)
    l4: list[str] = []
    for sp, mesh in built_arms:
        if sp["layer"] == "over_head":
            a_fill = sp["fill"] if sp["fill"] is not None else arm_c
            t_oh = sp["t_oh"]
            l4.append(f'<path d="{mesh["sub_fill_d"](t_oh)}" fill="{a_fill}" stroke="none"/>')
            l4.append(
                f'<path d="{mesh["sub_stroke_d"](t_oh, t_oh)}" fill="none" '
                f'stroke="{sp["stroke"]}" stroke-width="{sp["sw"]:.1f}" stroke-linecap="round" stroke-linejoin="round"/>'
            )
            if sp["paw_pad"]:
                l4.append(_paw_pad_svg(mesh))
    if l4:
        parts.append(f'<g transform="{tf}">{"".join(l4)}</g>')

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
                f'<circle cx="{ex}" cy="{ey}" r="20.5" fill="{FUR}" stroke="{OL}" stroke-width="4.1"/>'
                f'<circle cx="{ex - side * 1.5}" cy="{ey + 1.5}" r="11.0" fill="{CREAM}" stroke="{OL}" stroke-width="2.1"/>'
            )

    head_d = (
        "M -64,-12 C -64,-44 -36,-56 0,-56 C 36,-56 64,-44 64,-12 "
        "C 78,6 72,38 46,48 C 26,56 -26,56 -46,48 C -72,38 -78,6 -64,-12 Z"
    )
    parts.append(f'<path d="{head_d}" fill="{FUR}" stroke="{OL}" stroke-width="4.1" stroke-linejoin="round"/>')

    if sheet_mask:
        parts.append(
            '<path d="M -58,-8 C -56,-36 -30,-46 0,-46 C 30,-46 56,-36 58,-8 '
            'C 66,8 60,34 38,42 C 20,49 -20,49 -38,42 C -60,34 -66,8 -58,-8 Z" '
            'fill="#FFFFFF" stroke="#E5D5E8" stroke-width="2.8"/>'
        )
    else:
        parts.append(f'<ellipse cx="0" cy="20" rx="44" ry="27" fill="{CREAM}" stroke="{CREAM_SHD}" stroke-width="1.6"/>')

    parts.append(soft_blush(-49, 10, 18, 12, strong=strong_blush))
    parts.append(soft_blush(49, 10, 18, 12, strong=strong_blush))
    parts.append(
        '<line x1="-54" y1="12" x2="-50" y2="7" stroke="#C23B64" stroke-width="2.2" stroke-linecap="round"/>'
        '<line x1="-47" y1="13" x2="-43" y2="8" stroke="#C23B64" stroke-width="2.2" stroke-linecap="round"/>'
        '<line x1="43" y1="8" x2="47" y2="13" stroke="#C23B64" stroke-width="2.2" stroke-linecap="round"/>'
        '<line x1="50" y1="7" x2="54" y2="12" stroke="#C23B64" stroke-width="2.2" stroke-linecap="round"/>'
    )

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
    else:
        parts.append(
            f'<ellipse cx="-25" cy="-30" rx="13.5" ry="5.6" transform="rotate(-8 -25 -30)" fill="{BROW}" stroke="{OL}" stroke-width="1.8"/>'
            f'<ellipse cx="25" cy="-30" rx="13.5" ry="5.6" transform="rotate(8 25 -30)" fill="{BROW}" stroke="{OL}" stroke-width="1.8"/>'
        )

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

    parts.append(
        f'<ellipse cx="0" cy="6" rx="21" ry="12.5" fill="{NOSE}" stroke="{OL}" stroke-width="2.8"/>'
        f'<ellipse cx="-6.5" cy="2" rx="6.5" ry="2.8" transform="rotate(-14 -6.5 2)" fill="{NOSE_HI}" fill-opacity="0.6"/>'
    )

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
    else:
        parts.append(f'<path d="M -8,30 Q 0,34 8,29" fill="none" stroke="{OL}" stroke-width="3.0" stroke-linecap="round"/>')

    parts.append("</g>")
    return "".join(parts)


# =========================================================================== #
#  #71 — LOTSO STRAWBERRY HARVEST (NATURAL HUGGING CURVED ARMS!)
# =========================================================================== #
def _lotso_chubby_back() -> str:
    return (
        shadow(150, 270, 80, 10)
        + f'<circle cx="96" cy="80" r="20" fill="{FUR}" stroke="{OL}" stroke-width="4.1"/>'
        + f'<circle cx="204" cy="80" r="20" fill="{FUR}" stroke="{OL}" stroke-width="4.1"/>'
        + f'<ellipse cx="150" cy="208" rx="66" ry="51" fill="{FUR}" stroke="{OL}" stroke-width="4.1"/>'
        + f'<ellipse cx="150" cy="124" rx="67" ry="51" fill="{FUR}" stroke="{OL}" stroke-width="4.1"/>'
        + f'<circle cx="150" cy="238" r="16.5" fill="{FUR_LT}" stroke="{OL}" stroke-width="3.5"/>'
        + _toe_bean_foot(92, 242, rot=-22) + _toe_bean_foot(208, 242, rot=22)
        + '<path d="M 222,82 L 238,72 M 228,94 L 246,92" stroke="#E56B8C" stroke-width="3.4" stroke-linecap="round"/>'
    )


def build_71_strawberry() -> list[tuple[str, Image.Image]]:
    s0 = render_svg(_lotso_chubby_back())
    s1 = render_svg(
        shadow()
        + '<path d="M 38,158 Q 22,112 56,78 M 262,158 Q 278,112 244,78" fill="none" stroke="#E56B8C" stroke-width="3.2" stroke-linecap="round" stroke-dasharray="8,6"/>'
        + bear_body(150, 218, pose="sit", paws="down", lean=6)
        + bear_head(154, 124, expr="curious", rot=11)
    )
    s2 = render_svg(
        shadow(140, 270, 76, 10)
        + bear_body(140, 216, pose="sit", paws="wave_r", lean=-5)
        + bear_head(136, 122, expr="sparkle_eyes", rot=-7)
        + strawberry(240, 232, s=1.08, ripe=False, rot=14)
        + sp4(242, 192, r=8, fill="#8AC48E", stroke="#46754A")
    )
    s3 = render_svg(
        shadow()
        + bear_body(
            150, 216, pose="sit", paws="none",
            mid_props=strawberry(150, 216, s=1.70, ripe=True),
            arms=[
                arm_spec((114, 198), (94, 224), (128, 220), 14.0, 12.0, 10.4, layer="front"),
                arm_spec((186, 198), (206, 224), (172, 220), 14.0, 12.0, 10.4, layer="front"),
            ],
            head_svg=bear_head(150, 122, expr="smile", rot=4),
        )
    )
    s4 = render_svg(
        shadow()
        + bear_body(
            150, 216, pose="sit", paws="none", lean=-5,
            mid_props=strawberry(146, 216, s=1.72, ripe=True, rot=-6),
            arms=[
                arm_spec((114, 198), (92, 224), (124, 220), 14.0, 12.0, 10.4, layer="front"),
                arm_spec((186, 198), (206, 224), (170, 220), 14.0, 12.0, 10.4, layer="front"),
            ],
            head_svg=bear_head(144, 122, expr="wink", strong_blush=True, rot=-9),
        )
        + star5(242, 84, r=12) + sp4(52, 102, r=9)
    )
    s5 = with_hero_aura(render_svg(
        shadow(150, 272, 62, 8, op=0.12)
        + bear_body(
            150, 206, pose="jump", paws="none",
            mid_props=strawberry(150, 206, s=1.75, ripe=True),
            arms=[
                arm_spec((114, 188), (94, 214), (126, 208), 14.0, 12.0, 10.4, layer="front"),
                arm_spec((186, 188), (206, 214), (174, 208), 14.0, 12.0, 10.4, layer="front"),
            ],
            head_svg=bear_head(150, 114, expr="heart_eyes", strong_blush=True, rot=5),
        )
        + heart(48, 84, s=14, fill="#FF6E94", rot=-12) + heart(252, 88, s=13, fill="#E56B8C", rot=12)
        + sp4(52, 174, r=10) + sp4(250, 174, r=10)
    ), (229, 107, 140))
    return [
        ("Quay Lưng Lì", s0),
        ("Quay Lại Tò Mò", s1),
        ("Dâu Xanh Nhú", s2),
        ("Ôm Dâu Chín", s3),
        ("Nháy Mắt Ngọt", s4),
        ("Mắt Tim Dâu!", s5),
    ]


# =========================================================================== #
#  #72 — LOTSO STRAWBERRY MILK CAFE (CURVED ARMS POURING, SIPPING & CHEERING!)
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


def _milk_carton(cx=226, cy=188, rot=-18, s=1.0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot}) scale({s})">'
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
    # S0: Slouched on wooden counter propping chin with natural curved arm beside empty glass
    s0 = render_svg(
        bear_body(
            134, 218, pose="sit", paws="none", lean=-6,
            mid_props=_wood_table(246) + _milk_glass(228, 220, filled=False),
            arms=[
                arm_spec((98, 202), (68, 208), (98, 174), 13.5, 11.8, 10.2, layer="over_head", t_oh=0.38),
                arm_spec((168, 202), (192, 228), (166, 234), 13.5, 11.8, 10.2, layer="front", t_fill=0.30, t_in=0.34, t_out=0.52),
            ],
            head_svg=bear_head(130, 128, expr="sleepy", brows="pout_sad", rot=-9),
        )
    )
    # S1: Putting on strawberry apron holding milk carton with curved right arm
    s1 = render_svg(
        shadow() + bear_body(
            142, 216, pose="stand", paws="none", outfit="apron", lean=4,
            mid_props=_milk_carton(228, 184, rot=10),
            arms=[
                arm_spec((106, 198), (76, 218), (88, 236), 14.0, 12.0, 10.4, layer="out"),
                arm_spec((178, 198), (214, 202), (216, 186), 14.0, 12.0, 10.4, layer="front", t_fill=0.30, t_in=0.32, t_out=0.54),
            ],
            head_svg=bear_head(146, 122, expr="curious", rot=6),
        )
    )
    # S2: Pouring pink strawberry milk cleanly into glass (carton shifted clear of right cheek!)
    pour_stream = (
        '<path d="M 227,178 Q 240,192 241,208" fill="none" stroke="#F9B4C8" stroke-width="7.2" stroke-linecap="round"/>'
        '<path d="M 228,179 Q 238,191 239,205" fill="none" stroke="#FFF1F5" stroke-width="2.2" stroke-linecap="round"/>'
    )
    s2 = render_svg(
        bear_body(
            118, 216, pose="sit", paws="none", outfit="apron", lean=5,
            mid_props=_wood_table(246) + pour_stream + _milk_carton(214, 168, rot=46, s=0.90) + _milk_glass(242, 220, filled=True, cream_top=False),
            arms=[
                arm_spec((84, 200), (64, 224), (82, 236), 13.8, 11.8, 10.2, layer="front", t_fill=0.28, t_in=0.30, t_out=0.52),
                arm_spec((154, 198), (186, 196), (202, 178), 13.8, 11.8, 10.2, layer="front", t_fill=0.28, t_in=0.30, t_out=0.52),
            ],
            head_svg=bear_head(122, 122, expr="smile", rot=6),
        )
    )
    # S3: Topping glass with whipped cream & fresh strawberry!
    s3 = render_svg(
        bear_body(
            136, 216, pose="sit", paws="none", outfit="apron", lean=-4,
            mid_props=_wood_table(246) + _milk_glass(226, 220, filled=True, cream_top=True),
            arms=[
                arm_spec((100, 202), (76, 224), (98, 234), 13.8, 11.8, 10.2, layer="front", t_fill=0.30, t_in=0.34, t_out=0.52),
                arm_spec((172, 200), (200, 202), (214, 184), 13.8, 11.8, 10.2, layer="front", t_fill=0.34, t_in=0.34, t_out=0.34),
            ],
            head_svg=bear_head(134, 122, expr="sparkle_eyes", strong_blush=True, rot=-6),
        )
        + sp4(248, 166, r=10) + sp4(60, 108, r=9)
    )
    # S4: Curved chubby arms hugging strawberry milk glass sipping happily!
    s4 = render_svg(
        shadow() + bear_body(
            150, 216, pose="sit", paws="none", outfit="apron", lean=5,
            mid_props=_milk_glass(154, 212, filled=True, cream_top=True, s=1.12),
            arms=[
                arm_spec((114, 198), (94, 226), (132, 220), 14.0, 12.0, 10.4, layer="front"),
                arm_spec((186, 198), (206, 226), (176, 220), 14.0, 12.0, 10.4, layer="front"),
            ],
            head_svg=bear_head(152, 122, expr="happy_squint", strong_blush=True, rot=7),
        )
        + heart(242, 102, s=13, fill="#F7B2C4", stroke="#D65076")
    )
    # S5: Celebrating beside strawberry milk & shortcake slice with curved cheering arms!
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
        ("Đeo Tạp Dề Dâu", s1),
        ("Rót Sữa Dâu", s2),
        ("Thêm Kem Tươi", s3),
        ("Ôm Ly Hút Ngon", s4),
        ("Tiệc Sữa Dâu!", s5),
    ]


# =========================================================================== #
#  #73 — LOTSO BERRY FLOWER CROWN (CURVED ARMS + SNUG CROWN!)
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
        shadow() + bear_body(
            150, 216, pose="stand", paws="none", lean=4,
            arms=[
                arm_spec((114, 200), (82, 216), (92, 234), 14.0, 12.0, 10.4, layer="out"),
                arm_spec((186, 200), (236, 152), (212, 92), 14.0, 12.0, 10.4, layer="over_head", t_oh=0.56),
            ],
            head_svg=bear_head(154, 122, expr="smile", rot=7) + daisy(208, 74, r=13),
        )
    )
    s2 = render_svg(
        shadow() + bear_body(150, 216, pose="walk", paws="walk_swing", lean=-6)
        + bear_head(146, 122, expr="smile", strong_blush=True, rot=-7)
        + _berry_crown(142, 66, level="half", rot=-7)
    )
    s3 = render_svg(
        shadow() + bear_body(150, 216, pose="sit", paws="hug_center")
        + bear_head(150, 122, expr="wink", strong_blush=True, rot=5)
        + _berry_crown(152, 66, level="full", rot=5) + sp4(52, 92, r=9)
    )
    s4 = render_svg(
        shadow() + bear_body(
            146, 216, pose="walk", paws="none", lean=-4,
            mid_props=_berry_cluster(232, 184, s=0.98),
            arms=[
                arm_spec((110, 198), (78, 216), (90, 234), 14.0, 12.0, 10.4, layer="out"),
                arm_spec((182, 196), (218, 194), (222, 174), 14.0, 12.0, 10.4, layer="front", t_fill=0.30, t_in=0.32, t_out=0.54),
            ],
            head_svg=bear_head(144, 122, expr="big_smile", strong_blush=True, rot=-6) + _berry_crown(140, 66, level="full", rot=-6),
        )
    )
    s5 = with_hero_aura(render_svg(
        shadow(150, 272, 62, 8, op=0.12)
        + bear_body(150, 204, pose="jump", paws="wide_up")
        + bear_head(150, 114, expr="happy_squint", strong_blush=True, rot=4)
        + _berry_crown(152, 58, level="full", rot=4)
        + _berry_cluster(240, 148, s=1.0)
        + daisy(48, 88, r=12) + daisy(254, 78, r=11) + daisy(52, 200, r=10) + sp4(248, 224, r=10)
    ), (217, 74, 107))
    return [
        ("Vườn Trống Chờ", s0),
        ("Cài Cúc Lên Tai", s1),
        ("Bước Đi Kết Lá", s2),
        ("Vương Miện Dâu", s3),
        ("Cầm Chùm Dâu", s4),
        ("Hoàng Tử Dâu!", s5),
    ]


# =========================================================================== #
#  #74 — LOTSO OVERALLS TOY WORKSHOP (CURVED SLEEVE ARMS!)
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
        + bear_head(132, 124, expr="sleepy", rot=-9) + _pizza_slice(238, 236)
    )
    s1 = render_svg(
        shadow() + bear_body(150, 216, pose="stand", paws="hug_center", outfit="overalls", lean=5)
        + bear_head(154, 122, expr="curious", rot=6)
    )
    s2 = render_svg(
        shadow() + bear_body(146, 216, pose="walk", paws="wave_r", outfit="overalls", lean=-5)
        + bear_head(144, 122, expr="smile", strong_blush=True, rot=-7) + _hi_badge(244, 88)
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
        ("Xưởng Đồ Chơi!", s5),
    ]


# =========================================================================== #
#  #75 — LOTSO LO-FI EARPHONES FLOW (CURVED ARMS SWAYING TO BEATS!)
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
        shadow() + bear_body(
            150, 218, pose="sit", paws="hug_center", lean=-6,
            mid_props=_earphones("tangled"),
            head_svg=bear_head(146, 124, expr="curious", brows="pout_sad", rot=-8),
        )
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
        _soundwaves(False) + shadow() + bear_body(150, 218, pose="sit", paws="hug_center")
        + bear_head(150, 124, expr="calm_closed", strong_blush=True, rot=6) + _earphones("both", 150, 124)
        + music_note(54, 92, double=False, col="#B83E62")
    )
    s4 = render_svg(
        _soundwaves(False) + shadow() + bear_body(150, 214, pose="walk", paws="wave_r", lean=-8)
        + bear_head(142, 120, expr="happy_squint", strong_blush=True, rot=-12) + _earphones("both", 142, 120)
        + music_note(242, 92, double=True, col="#B83E62", s=1.05) + music_note(52, 102, double=False, col="#E56B8C", s=0.9)
    )
    s5 = with_hero_aura(render_svg(
        _soundwaves(True) + shadow(150, 272, 62, 8, op=0.12)
        + bear_body(150, 204, pose="jump", paws="wide_up", lean=5)
        + bear_head(154, 114, expr="big_smile", strong_blush=True, rot=7) + _earphones("both", 154, 114)
        + music_note(48, 84, double=True, col="#B83E62", s=1.05) + music_note(250, 88, double=True, col="#E56B8C", s=1.05)
        + sp4(52, 204, r=10) + sp4(250, 204, r=10)
    ), (184, 62, 98))
    return [
        ("Gỡ Dây Rối", s0),
        ("Đeo 1 Bên Tai", s1),
        ("Nốt Nhạc Vui", s2),
        ("Sóng Nhạc Flow", s3),
        ("Đung Đưa Hát", s4),
        ("Phiêu Nhạc 100%", s5),
    ]


# =========================================================================== #
#  #76 — LOTSO MOOD DETOX COMIC (COOKIE -> BAND-AID -> BALLOONS -> FLOAT -> HEART RAIN!)
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
            '<path d="M 222,172 Q 232,132 240,100" fill="none" stroke="#8C5266" stroke-width="2.4"/>'
            + heart(242, 84, s=22, fill="#FF85A6", stroke=OL, sw=2.6, rot=12)
        )
    if count == 2:
        return (
            '<path d="M 76,174 Q 68,134 60,96 M 224,174 Q 232,134 240,96" fill="none" stroke="#8C5266" stroke-width="2.4"/>'
            + heart(58, 80, s=23, fill="#FF85A6", stroke=OL, sw=2.6, rot=-14)
            + heart(242, 80, s=23, fill="#F47294", stroke=OL, sw=2.6, rot=14)
        )
    return (
        '<path d="M 80,158 Q 74,112 68,72 M 84,158 Q 100,112 112,56 M 216,158 Q 200,112 188,56 M 220,158 Q 226,112 232,72" fill="none" stroke="#8C5266" stroke-width="2.2"/>'
        + heart(66, 62, s=21, fill="#F7B2C4", stroke=OL, sw=2.4, rot=-16)
        + heart(112, 46, s=22, fill="#FF85A6", stroke=OL, sw=2.4, rot=-6)
        + heart(188, 46, s=22, fill="#F47294", stroke=OL, sw=2.4, rot=6)
        + heart(234, 62, s=21, fill="#E8799B", stroke=OL, sw=2.4, rot=16)
    )


def build_76_mood_detox() -> list[tuple[str, Image.Image]]:
    s0 = render_svg(
        shadow() + bear_body(
            150, 218, pose="sit", paws="none",
            mid_props=_cookie_state(150, 216, mended=False),
            arms=[
                arm_spec((114, 200), (96, 224), (126, 218), 13.8, 11.8, 10.2, layer="front"),
                arm_spec((186, 200), (204, 224), (174, 218), 13.8, 11.8, 10.2, layer="front"),
            ],
            head_svg=bear_head(150, 124, expr="grumpy", brows="grump_cute", rot=-6),
        )
        + _lightning(46, 72, -16) + _lightning(254, 72, 16) + _lightning(42, 178, -22, 0.85) + _lightning(258, 178, 22, 0.85)
    )
    s1 = render_svg(
        shadow() + bear_body(
            150, 218, pose="sit", paws="none", lean=4,
            mid_props=_cookie_state(152, 218, mended=True),
            arms=[
                arm_spec((114, 200), (96, 224), (132, 218), 13.8, 11.8, 10.2, layer="front"),
                arm_spec((186, 200), (204, 224), (170, 218), 13.8, 11.8, 10.2, layer="front"),
            ],
            head_svg=bear_head(154, 124, expr="calm_smile", brows="pout_sad", rot=7),
        )
    )
    s2 = render_svg(
        shadow() + _balloon_bunch(1)
        + bear_body(146, 216, pose="stand", paws="wave_r", lean=-4)
        + bear_head(144, 122, expr="smile", rot=-6)
    )
    s3 = render_svg(
        shadow() + _balloon_bunch(2)
        + bear_body(150, 216, pose="walk", paws="wide_up", lean=5)
        + bear_head(154, 122, expr="smile", strong_blush=True, rot=7)
    )
    s4 = render_svg(
        shadow(150, 278, 46, 6, op=0.10) + _balloon_bunch(4)
        + bear_body(150, 200, pose="float", paws="wide_up", lean=-5)
        + bear_head(146, 114, expr="wink", strong_blush=True, rot=-7)
    )
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
        ("Dán Băng Tim", s1),
        ("Cầm Bóng Tim", s2),
        ("Ôm 2 Bóng Bay", s3),
        ("Bay Bổng Bóng", s4),
        ("Mưa Tim Detox!", s5),
    ]


# =========================================================================== #
#  #77 — LOTSO FLORAL SWEET DREAMS (REBUILT: STROLL -> PICK -> TIE -> HUG -> SHEEP -> WAVE!)
# =========================================================================== #
def _rose(cx, cy, s=1.0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) scale({s})">'
        f'<circle cx="-7" cy="-4" r="7.5" fill="#E11D48" stroke="{OL}" stroke-width="2.0"/>'
        f'<circle cx="7" cy="-4" r="7.5" fill="#E11D48" stroke="{OL}" stroke-width="2.0"/>'
        f'<circle cx="0" cy="-10" r="7.5" fill="#F43F5E" stroke="{OL}" stroke-width="2.0"/>'
        f'<circle cx="0" cy="2" r="7.5" fill="#E11D48" stroke="{OL}" stroke-width="2.0"/>'
        f'<circle cx="0" cy="-4" r="4.8" fill="#FDE047" stroke="#C98A1A" stroke-width="1.6"/></g>'
    )


def _roadside_flowers(cx=238, cy=246, picked=False) -> str:
    parts = [
        f'<g transform="translate({cx},{cy})">'
        f'<ellipse cx="0" cy="14" rx="34" ry="12" fill="#A6D8B0" stroke="#4D8B58" stroke-width="2.4"/>'
        f'<path d="M -16,10 L -20,-12 M 0,10 L 0,-18 M 14,10 L 18,-10" stroke="#4D8B58" stroke-width="3.4" stroke-linecap="round"/>'
        + _rose(-20, -14, 0.85) + _rose(18, -12, 0.80)
    ]
    if not picked:
        parts.append(_rose(0, -20, 0.92))
    parts.append("</g>")
    return "".join(parts)


def _bouquet(cx=150, cy=214, blooms=3, ribbon=True) -> str:
    parts = [
        f'<g transform="translate({cx},{cy})">'
        '<path d="M -8,28 L -18,-12 M 0,30 L 0,-18 M 8,28 L 18,-12" stroke="#4D8B58" stroke-width="4.0" stroke-linecap="round"/>'
        '<ellipse cx="-20" cy="4" rx="11" ry="5.5" transform="rotate(-30 -20 4)" fill="#78B886" stroke="#3D6E46" stroke-width="2.0"/>'
        '<ellipse cx="20" cy="4" rx="11" ry="5.5" transform="rotate(30 20 4)" fill="#78B886" stroke="#3D6E46" stroke-width="2.0"/>'
    ]
    if ribbon:
        parts.append(
            '<path d="M -12,12 L 12,12" stroke="#E892AC" stroke-width="5.5" stroke-linecap="round"/>'
            '<path d="M -2,12 C -14,4 -18,16 -10,20 C -5,22 -2,16 -2,12 Z M 2,12 C 14,4 18,16 10,20 C 5,22 2,16 2,12 Z" fill="#F49CB5" stroke="#5A1F33" stroke-width="1.9"/>'
        )
    if blooms >= 1:
        parts.append(_rose(0, -18, 0.96))
    if blooms >= 2:
        parts.append(_rose(-17, -10, 0.88) + _rose(17, -10, 0.88))
    if blooms >= 3:
        parts.append(_rose(-10, -24, 0.84) + _rose(10, -24, 0.84))
    parts.append("</g>")
    return "".join(parts)


def _dream_cloud(mode="empty") -> str:
    parts = [
        '<circle cx="198" cy="94" r="6.5" fill="#FFF2F7" stroke="#9D82C9" stroke-width="2.2"/>',
        '<path d="M 192,70 C 178,70 174,52 186,44 C 188,28 214,22 228,34 C 244,24 268,36 264,54 C 272,68 256,82 238,76 C 224,82 204,80 192,70 Z" fill="#FFF2F7" stroke="#9D82C9" stroke-width="2.6"/>',
    ]
    if mode == "sheep":
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
    # S0 (0%): Strolling beside roadside flower patch, leaning curiously admiring blooming red flowers!
    s0 = render_svg(
        shadow(122, 270, 70, 9)
        + _roadside_flowers(236, 248, picked=False)
        + bear_body(118, 218, pose="walk", paws="walk_swing", lean=9)
        + bear_head(126, 124, expr="curious", rot=12)
    )
    # S1 (20%): Reaching curved right arm gently down to pick first red rose with warm smile!
    s1 = render_svg(
        shadow(124, 270, 72, 9)
        + _roadside_flowers(240, 250, picked=True)
        + bear_body(
            122, 218, pose="stand", paws="none", lean=11,
            mid_props='<path d="M 218,228 L 226,204" stroke="#4D8B58" stroke-width="3.6" stroke-linecap="round"/>' + _rose(228, 200, 0.96),
            arms=[
                arm_spec((88, 200), (64, 218), (76, 234), 13.6, 11.8, 10.2, layer="out"),
                arm_spec((156, 204), (192, 218), (218, 220), 13.6, 11.8, 10.2, layer="front", t_fill=0.30, t_in=0.32, t_out=0.54),
            ],
            head_svg=bear_head(132, 124, expr="smile", strong_blush=True, rot=12),
        )
    )
    # S2 (40%): Sitting cleanly tying several red roses into a neat pink-ribbon bouquet!
    s2 = render_svg(
        shadow()
        + bear_body(
            150, 218, pose="sit", paws="none", lean=-3,
            mid_props=_bouquet(150, 216, blooms=2, ribbon=True),
            arms=[
                arm_spec((114, 198), (94, 224), (132, 220), 13.8, 11.8, 10.2, layer="front"),
                arm_spec((186, 198), (206, 224), (168, 220), 13.8, 11.8, 10.2, layer="front"),
            ],
            head_svg=bear_head(148, 122, expr="smile", strong_blush=True, rot=-5),
        )
    )
    # S3 (60%): Hugging full red bouquet looking up at dreamy cream-pink thought cloud appearing!
    s3 = render_svg(
        shadow()
        + bear_body(
            142, 216, pose="sit", paws="none", lean=4,
            mid_props=_bouquet(144, 216, blooms=3, ribbon=True),
            arms=[
                arm_spec((106, 198), (88, 224), (126, 220), 13.8, 11.8, 10.2, layer="front"),
                arm_spec((178, 198), (196, 224), (162, 220), 13.8, 11.8, 10.2, layer="front"),
            ],
            head_svg=bear_head(144, 122, expr="sparkle_eyes", strong_blush=True, rot=7),
        )
        + _dream_cloud("empty")
    )
    # S4 (80%): Lavender pastel sheep smiling peacefully inside dream cloud, Lotso blushing dreamy!
    s4 = render_svg(
        shadow()
        + bear_body(
            142, 216, pose="sit", paws="none", lean=-5,
            mid_props=_bouquet(140, 216, blooms=3, ribbon=True),
            arms=[
                arm_spec((106, 198), (88, 224), (122, 220), 13.8, 11.8, 10.2, layer="front"),
                arm_spec((178, 198), (196, 224), (158, 220), 13.8, 11.8, 10.2, layer="front"),
            ],
            head_svg=bear_head(138, 124, expr="calm_closed", strong_blush=True, rot=-7),
        )
        + _dream_cloud("sheep")
    )
    # S5 (100%): Soft pink cloud backdrop, hugging vibrant bouquet & gently waving hello to sheep dream!
    s5 = with_hero_aura(render_svg(
        '<ellipse cx="150" cy="160" rx="124" ry="96" fill="#FCECF3"/>'
        + shadow()
        + bear_body(
            134, 214, pose="sit", paws="none", lean=3,
            mid_props=_bouquet(112, 216, blooms=3, ribbon=True),
            arms=[
                arm_spec((98, 196), (76, 220), (104, 220), 13.8, 11.8, 10.2, layer="front"),
                arm_spec((170, 196), (216, 188), (226, 152), 14.0, 12.0, 10.4, paw_pad=True, layer="out"),
            ],
            head_svg=bear_head(136, 124, expr="happy_squint", strong_blush=True, rot=5),
        )
        + _dream_cloud("sheep")
        + sp4(46, 84, r=11, fill="#FDE047", stroke="#9D82C9") + sp4(48, 198, r=9, fill="#E9DDFB", stroke="#8B6BB8")
    ), (184, 158, 219))
    return [
        ("Ngắm Khóm Hoa", s0),
        ("Hái Hoa Đầu", s1),
        ("Buộc Bó Hoa", s2),
        ("Ôm Hoa Ngắm Mây", s3),
        ("Mơ Cừu Tím", s4),
        ("Giấc Mơ Cừu!", s5),
    ]


# =========================================================================== #
#  #78 — LOTSO DAISY CHEEK GLOW (REBUILT: WALK -> BEND PICK -> SIT ADMIRE -> TUCK EAR -> WINK -> GLOW!)
# =========================================================================== #
def _ground_daisy(cx=238, cy=252) -> str:
    return (
        f'<g transform="translate({cx},{cy})">'
        f'<ellipse cx="0" cy="10" rx="22" ry="6" fill="#C9E6CE"/>'
        f'<path d="M 0,8 Q 2,-2 0,-12" fill="none" stroke="#6D9F71" stroke-width="3.6" stroke-linecap="round"/>'
        f'<ellipse cx="-7" cy="0" rx="7" ry="3.5" transform="rotate(-24 -7 0)" fill="#8AC48E" stroke="{OL}" stroke-width="1.8"/>'
        + daisy(0, -16, r=13, rot=12) + '</g>'
    )


def build_78_daisy_glow() -> list[tuple[str, Image.Image]]:
    # S0 (0%): Walking cheerfully (natural stride + swinging curved arms) spotting tiny white daisy on ground!
    s0 = render_svg(
        shadow(120, 270, 70, 9)
        + _ground_daisy(238, 252)
        + bear_body(118, 218, pose="walk", paws="walk_swing", lean=8)
        + bear_head(126, 124, expr="curious", rot=12)
        + '<path d="M 212,216 L 222,208 M 224,224 L 234,218" stroke="#EAB308" stroke-width="2.6" stroke-linecap="round"/>'
    )
    # S1 (20%): Bending forward reaching curved right arm down to gently pick up the daisy!
    s1 = render_svg(
        shadow(126, 270, 72, 9)
        + '<ellipse cx="238" cy="262" rx="20" ry="5" fill="#C9E6CE"/>'
        + bear_body(
            124, 218, pose="stand", paws="none", lean=14,
            mid_props='<path d="M 222,238 L 236,222" stroke="#6D9F71" stroke-width="3.6" stroke-linecap="round"/>' + daisy(238, 218, r=14, rot=14),
            arms=[
                arm_spec((92, 200), (66, 218), (76, 234), 13.6, 11.8, 10.2, layer="out"),
                arm_spec((158, 206), (194, 224), (218, 234), 13.6, 11.8, 10.2, layer="front", t_fill=0.30, t_in=0.32, t_out=0.54),
            ],
            head_svg=bear_head(138, 126, expr="smile", strong_blush=True, rot=15),
        )
    )
    # S2 (40%): Sitting down cradling the white daisy tenderly in both curved paws, gentle smile!
    s2 = render_svg(
        shadow()
        + bear_body(
            150, 218, pose="sit", paws="none",
            mid_props='<path d="M 150,236 L 150,212" stroke="#6D9F71" stroke-width="3.8" stroke-linecap="round"/>' + daisy(150, 206, r=16, rot=8),
            arms=[
                arm_spec((114, 198), (94, 226), (132, 222), 13.8, 11.8, 10.2, layer="front"),
                arm_spec((186, 198), (206, 226), (168, 222), 13.8, 11.8, 10.2, layer="front"),
            ],
            head_svg=bear_head(150, 122, expr="calm_smile", strong_blush=True, rot=-4),
        )
    )
    # S3 (60%): Raising curved right arm to tuck the daisy neatly behind his round bear ear, cheeks blushing!
    s3 = render_svg(
        shadow()
        + bear_body(
            150, 218, pose="sit", paws="none", lean=-4,
            arms=[
                arm_spec((114, 200), (82, 218), (98, 234), 13.8, 11.8, 10.2, layer="out"),
                arm_spec((186, 200), (236, 152), (210, 92), 13.8, 11.8, 10.2, layer="over_head", t_oh=0.56),
            ],
            head_svg=bear_head(148, 122, expr="smile", strong_blush=True, rot=-6) + daisy(202, 74, r=16, rot=18),
        )
        + sp4(56, 94, r=9, fill="#F6CE55", stroke="#C98A1A")
    )
    # S4 (80%): Daisy tucked behind ear, BOTH curved arms lifting naturally to cup chubby cheeks, charming wink!
    s4 = render_svg(
        shadow()
        + bear_body(
            150, 216, pose="sit", paws="none", lean=-5,
            arms=[
                arm_spec((116, 202), (64, 186), (86, 146), 13.6, 11.8, 10.2, layer="over_head", t_oh=0.22),
                arm_spec((184, 198), (234, 182), (204, 142), 13.6, 11.8, 10.2, layer="over_head", t_oh=0.22),
            ],
            head_svg=bear_head(146, 122, expr="wink", strong_blush=True, rot=-8) + daisy(196, 70, r=16, rot=18),
        )
    )
    # S5 (100%): Radiant cheek-cup wink with ear daisy + gently floating white petals & warm sunshine glow!
    s5 = with_hero_aura(render_svg(
        shadow(150, 272, 66, 9, op=0.12)
        + bear_body(
            150, 210, pose="jump", paws="none",
            arms=[
                arm_spec((114, 194), (64, 180), (90, 142), 13.8, 11.8, 10.2, layer="over_head", t_oh=0.22),
                arm_spec((186, 194), (236, 180), (210, 142), 13.8, 11.8, 10.2, layer="over_head", t_oh=0.22),
            ],
            head_svg=bear_head(150, 118, expr="wink", strong_blush=True, rot=5) + daisy(206, 74, r=17, rot=22),
        )
        # Floating soft white daisy petals + golden sparkles
        + '<ellipse cx="52" cy="94" rx="10" ry="5.5" transform="rotate(-28 52 94)" fill="#FFFFFF" stroke="#C99A6B" stroke-width="1.8"/>'
        + '<ellipse cx="254" cy="116" rx="10" ry="5.5" transform="rotate(32 254 116)" fill="#FFFFFF" stroke="#C99A6B" stroke-width="1.8"/>'
        + '<ellipse cx="56" cy="206" rx="9" ry="5" transform="rotate(18 56 206)" fill="#FFFFFF" stroke="#C99A6B" stroke-width="1.8"/>'
        + '<ellipse cx="248" cy="212" rx="9" ry="5" transform="rotate(-24 248 212)" fill="#FFFFFF" stroke="#C99A6B" stroke-width="1.8"/>'
        + sp4(150, 34, r=11, fill="#EFC143", stroke="#C98A1A") + sp4(62, 146, r=8, fill="#EFC143", stroke="#C98A1A")
    ), (239, 193, 67))
    return [
        ("Thấy Hoa Cúc", s0),
        ("Cúi Nhặt Hoa", s1),
        ("Ngắm Hoa Cúc", s2),
        ("Cài Lên Tai", s3),
        ("Áp Má Nháy Mắt", s4),
        ("Hoa Cúc Rạng Rỡ", s5),
    ]


# =========================================================================== #
#  #79 — LOTSO BUNNY HEADBAND SELFCARE (SNUG HEADBAND + CURVED ARMS!)
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


def _lavender_headband(cx=150, cy=70, bouncy=False, rot=0) -> str:
    """Snug plush lavender bunny headband hugging Lotso's crown neatly between his bear ears!"""
    ang = 26 if bouncy else 16
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot})">'
        f'<ellipse cx="-24" cy="-24" rx="12.5" ry="29" transform="rotate(-{ang} -24 -24)" fill="#CFA0CB" stroke="{OL}" stroke-width="3.3"/>'
        f'<ellipse cx="-24" cy="-22" rx="6.0" ry="18" transform="rotate(-{ang} -24 -22)" fill="#FBCFE8"/>'
        f'<ellipse cx="24" cy="-24" rx="12.5" ry="29" transform="rotate({ang} 24 -24)" fill="#CFA0CB" stroke="{OL}" stroke-width="3.3"/>'
        f'<ellipse cx="24" cy="-22" rx="6.0" ry="18" transform="rotate({ang} 24 -22)" fill="#FBCFE8"/>'
        f'<path d="M -58,20 C -42,-12 42,-12 58,20 C 34,2 -34,2 -58,20 Z" fill="#E3C7F0" stroke="#7A4C9E" stroke-width="3.0" stroke-linejoin="round"/>'
        f'<path d="M -2,-2 C -16,-14 -26,-4 -18,6 C -12,12 -4,8 -2,4 Z M 2,-2 C 16,-14 26,-4 18,6 C 12,12 4,8 2,4 Z" fill="#E57294" stroke="{OL}" stroke-width="2.2"/>'
        f'<circle cx="0" cy="1" r="5" fill="#F49CB5" stroke="{OL}" stroke-width="2.2"/></g>'
    )


def build_79_bunny_selfcare() -> list[tuple[str, Image.Image]]:
    s0 = render_svg(
        shadow() + bear_body(
            150, 218, pose="sit", paws="none", lean=-4,
            mid_props=_bunny_phone(148, 222, s=0.90),
            arms=[
                arm_spec((114, 198), (94, 226), (132, 224), 13.8, 11.8, 10.2, layer="front"),
                arm_spec((186, 198), (206, 226), (166, 224), 13.8, 11.8, 10.2, layer="front"),
            ],
            head_svg=bear_head(146, 124, expr="curious", rot=-7),
        )
    )
    s1 = render_svg(
        shadow() + bear_body(
            150, 218, pose="sit", paws="none", lean=4,
            mid_props='<g transform="translate(152,222) scale(0.62)">' + _lavender_headband(0, 0) + '</g>',
            arms=[
                arm_spec((114, 198), (94, 226), (126, 224), 13.8, 11.8, 10.2, layer="front"),
                arm_spec((186, 198), (206, 226), (176, 224), 13.8, 11.8, 10.2, layer="front"),
            ],
            head_svg=bear_head(154, 122, expr="smile", rot=6),
        )
    )
    s2 = render_svg(
        shadow() + bear_body(
            150, 216, pose="stand", paws="none", lean=-4,
            arms=[
                arm_spec((114, 200), (50, 138), (94, 86), 13.8, 11.8, 10.2, layer="over_head", t_oh=0.58),
                arm_spec((186, 200), (250, 138), (202, 86), 13.8, 11.8, 10.2, layer="over_head", t_oh=0.58),
            ],
            head_svg=bear_head(148, 124, expr="smile", strong_blush=True, rot=-6) + _lavender_headband(144, 72, rot=-6),
        )
    )
    s3 = render_svg(
        shadow() + bear_body(150, 218, pose="sit", paws="down")
        + bear_head(150, 124, expr="calm_closed", sheet_mask=True) + _lavender_headband(150, 72)
        + strawberry(46, 134, s=0.76, rot=-14) + strawberry(254, 134, s=0.76, rot=14) + strawberry(250, 224, s=0.72, rot=10)
    )
    s4 = render_svg(
        shadow() + bear_body(150, 216, pose="walk", paws="wave_r", lean=-7)
        + bear_head(144, 122, expr="wink", strong_blush=True, rot=-10) + _lavender_headband(138, 72, rot=-10)
        + heart(46, 114, s=13, fill="#E11D48", rot=-12) + heart(252, 108, s=13, fill="#E57294", rot=12)
    )
    s5 = with_hero_aura(render_svg(
        shadow(150, 272, 62, 8, op=0.12)
        + bear_body(150, 206, pose="jump", paws="wide_up")
        + bear_head(150, 116, expr="happy_squint", strong_blush=True, rot=5) + _lavender_headband(152, 64, bouncy=True, rot=5)
        + heart(44, 86, s=15, fill="#E57294", rot=-14) + heart(256, 86, s=15, fill="#E11D48", rot=14)
        + heart(48, 198, s=12, fill="#F47294", rot=-10) + sp4(252, 196, r=11, fill="#FDE047", stroke="#93528B")
    ), (147, 82, 139))
    return [
        ("Lướt Điện Thoại", s0),
        ("Cầm Bờm Tai Thỏ", s1),
        ("Đeo Bờm Nơ Xinh", s2),
        ("Đắp Mặt Nạ Dâu", s3),
        ("Tự Tin Nghiêng", s4),
        ("Rạng Ngời Spa!", s5),
    ]


# =========================================================================== #
#  #80 — LOTSO BERRY GIFT BOX PARTY (CURVED ARMS POPPING OUT & HUGGING CUPCAKE!)
# =========================================================================== #
def _gift_box(cx=150, cy=218, lid_mode="closed", s=1.0) -> str:
    parts = [f'<g transform="translate({cx},{cy}) scale({s})">']
    parts.append(
        f'<rect x="-66" y="-22" width="132" height="72" rx="10" fill="#F9B4C8" stroke="{OL}" stroke-width="3.8"/>'
        f'<rect x="-14" y="-22" width="28" height="72" fill="#FFF3DC" stroke="{OL}" stroke-width="2.4"/>'
    )
    if lid_mode == "closed":
        parts.append(
            f'<rect x="-74" y="-44" width="148" height="24" rx="7" fill="#F396B4" stroke="{OL}" stroke-width="3.8"/>'
            f'<rect x="-14" y="-44" width="28" height="24" fill="#FFF3DC" stroke="{OL}" stroke-width="2.4"/>'
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
        f'<path d="M -24,4 C -26,-11 -10,-18 0,-16 C 10,-18 26,-11 24,4 Z" fill="#FFFDF5" stroke="#D9A8B8" stroke-width="2.6"/>'
        f'<rect x="-2.8" y="-28.5" width="5.6" height="12.5" rx="2" fill="#F396B4" stroke="{OL}" stroke-width="1.9"/>'
        f'<circle cx="0" cy="-34" r="7.5" fill="#FEF08A" fill-opacity="0.45"/>'
        f'<path d="M 0,-40 C -5.2,-33.5 -3.6,-28.5 0,-28.5 C 3.6,-28.5 5.2,-33.5 0,-40 Z" fill="#FDE047" stroke="#EA580C" stroke-width="1.7"/>'
        f'<ellipse cx="0" cy="-32" rx="1.6" ry="2.4" fill="#FFFBEB"/>'
        + strawberry(13, -9, s=0.42, ripe=True, rot=14)
        + '</g>'
    )


def build_80_gift_box() -> list[tuple[str, Image.Image]]:
    s0 = render_svg(
        shadow(150, 270, 80, 10)
        + f'<circle cx="108" cy="144" r="19" fill="{FUR}" stroke="{OL}" stroke-width="4.0"/><circle cx="109" cy="145" r="10" fill="{CREAM}"/>'
        + f'<circle cx="192" cy="144" r="19" fill="{FUR}" stroke="{OL}" stroke-width="4.0"/><circle cx="191" cy="145" r="10" fill="{CREAM}"/>'
        + f'<ellipse cx="150" cy="170" rx="54" ry="26" fill="{FUR}" stroke="{OL}" stroke-width="4.0"/>'
        + f'<circle cx="132" cy="166" r="5.5" fill="{EYE}"/><circle cx="130" cy="164" r="2.0" fill="#FFFFFF"/>'
        + f'<circle cx="168" cy="166" r="5.5" fill="{EYE}"/><circle cx="166" cy="164" r="2.0" fill="#FFFFFF"/>'
        + _gift_box(150, 218, lid_mode="closed")
    )
    s1 = render_svg(
        shadow(150, 270, 80, 10)
        + bear_head(150, 148, scale=0.88, expr="curious", rot=6)
        + _gift_box(150, 218, lid_mode="tilted")
        + bear_arm((106, 188), (94, 198), (112, 198), 12.5, 11.0, 9.8, seamless_shoulder=False)
        + bear_arm((194, 188), (206, 198), (188, 198), 12.5, 11.0, 9.8, seamless_shoulder=False)
    )
    s2 = render_svg(
        shadow(150, 270, 80, 10)
        + bear_body(150, 194, pose="hidden", paws="wide_up", lean=-4)
        + bear_head(146, 122, scale=0.92, expr="smile", strong_blush=True, rot=-6)
        + _party_hat(140, 62, rot=-8)
        + _gift_box(150, 224, lid_mode="open")
        + sp4(56, 86, r=9) + sp4(246, 90, r=9)
    )
    # S3 & S4: Lowered cupcake + compact candle with bright golden flame clearly separated below chin!
    s3 = render_svg(
        shadow() + bear_body(
            150, 216, pose="sit", paws="none",
            mid_props=_strawberry_cupcake(150, 226, s=0.96),
            arms=[
                arm_spec((114, 198), (94, 226), (130, 226), 13.8, 11.8, 10.2, layer="front"),
                arm_spec((186, 198), (206, 226), (170, 226), 13.8, 11.8, 10.2, layer="front"),
            ],
            head_svg=bear_head(150, 120, expr="sparkle_eyes", strong_blush=True, rot=4) + _party_hat(154, 60, rot=6),
        )
    )
    s4 = render_svg(
        shadow() + bear_body(
            150, 216, pose="sit", paws="none", lean=-4,
            mid_props=_strawberry_cupcake(148, 226, s=0.98),
            arms=[
                arm_spec((114, 198), (94, 226), (128, 226), 13.8, 11.8, 10.2, layer="front"),
                arm_spec((186, 198), (206, 226), (168, 226), 13.8, 11.8, 10.2, layer="front"),
            ],
            head_svg=bear_head(146, 120, expr="happy_squint", strong_blush=True, rot=-7) + _party_hat(138, 60, rot=-9),
        )
        + star5(52, 82, r=12) + star5(248, 86, r=13) + heart(50, 178, s=11, fill="#F396B4") + heart(250, 178, s=11, fill="#C43E67")
    )
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
        ("Ước Nguyện Xinh", s4),
        ("Nhảy Confetti!", s5),
    ]


# =========================================================================== #
#  CONTACT SHEET RENDERER WITH HARD 10PX NON-OVERLAP BOUNDING-BOX ASSERTION!
# =========================================================================== #
def _draw_fitted_label(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    text: str,
    max_right_x: int,
    fill: tuple[int, int, int],
    font_path: str = "C:/Windows/Fonts/segoeuib.ttf",
) -> None:
    max_w = max_right_x - x
    for sz in (13, 12, 11, 10):
        try:
            f = ImageFont.truetype(font_path, sz)
        except Exception:
            f = ImageFont.load_default()
        w = draw.textlength(text, font=f)
        if w <= max_w:
            draw.text((x, y), text, fill=fill, font=f)
            bbox = draw.textbbox((x, y), text, font=f)
            assert bbox[2] <= max_right_x, f"Text {text!r} right={bbox[2]} > max_right={max_right_x}"
            return

    try:
        f = ImageFont.truetype(font_path, 11)
    except Exception:
        f = ImageFont.load_default()
    words = text.split()
    mid = max(1, len(words) // 2)
    l1, l2 = " ".join(words[:mid]), " ".join(words[mid:])
    for i, line in enumerate((l1, l2)):
        ly = y - 3 + i * 14
        draw.text((x, ly), line, fill=fill, font=f)
        bbox = draw.textbbox((x, ly), line, font=f)
        assert bbox[2] <= max_right_x, f"Wrapped text {line!r} right={bbox[2]} > max_right={max_right_x}"


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
        print(f"  [LOTSO v4.1] {slug:24s} -> 6 natural-arm 300x300 RGBA PNGs saved")

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

    cell_w, cell_h = 228, 276
    left_w, pad, hdr_h = 246, 18, 84
    W = pad * 2 + left_w + cell_w * 6
    H = pad * 2 + hdr_h + cell_h * len(rows)

    sheet = Image.new("RGB", (W, H), (255, 247, 249))
    draw = ImageDraw.Draw(sheet)
    try:
        f_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 27)
        f_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 15.5)
        f_row = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 15)
        f_tiny = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 11)
    except Exception:
        f_title = f_sub = f_row = f_tiny = ImageFont.load_default()

    draw.rectangle([0, 0, W, hdr_h], fill=(196, 62, 103))
    draw.text((pad, 14), "LOTSO CHUBBY PLUSH BEAR COLLECTION — #71–#80 (v4.1 SEAMLESS ARMS • 60 SPRITES)", fill=(255, 255, 255), font=f_title)
    draw.text((pad, 50), "3-Layer Seamless Plush Bear Arms • Prop Clearance (#72 Milk Pour & #80 Cupcake) • Transparent 300x300 RGBA • 0/60 Overlaps", fill=(255, 243, 220), font=f_sub)

    pcts = ["0%", "20%", "40%", "60%", "80%", "100% MAX"]
    verified_cells = 0
    for r_i, (title, slug, bg_c, acc_c) in enumerate(rows):
        y0 = hdr_h + pad + r_i * cell_h
        draw.rounded_rectangle([pad, y0 + 4, W - pad, y0 + cell_h - 6], radius=14, fill=bg_c, outline=acc_c, width=2)
        draw.text((pad + 14, y0 + 116), title, fill=acc_c, font=f_row)
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
            sx, sy = x0 + cell_w - 58, y0 + 184
            frame_left_x = sx - 4
            draw.rounded_rectangle([frame_left_x, sy - 4, sx + 48, sy + 48], radius=6, fill=(255, 250, 252), outline=(230, 214, 220), width=1)
            sheet.paste(small, (sx, sy), small)

            # Strict minimum 10px clearance between right edge of text and left edge of 44px preview frame!
            max_text_right = frame_left_x - 10
            stage_tag = f"S{s_i} • {pcts[s_i]}"
            draw.text((x0 + 14, y0 + 186), stage_tag, fill=acc_c, font=f_tiny)
            tb_tag = draw.textbbox((x0 + 14, y0 + 186), stage_tag, font=f_tiny)
            assert tb_tag[2] <= max_text_right, f"Stage tag overlap on {slug} S{s_i}"

            _draw_fitted_label(draw, x0 + 14, y0 + 208, lbl, max_text_right, (87, 34, 52))
            draw.text((sx + 7, sy + 50), "44px", fill=(160, 138, 146), font=f_tiny)
            verified_cells += 1

    assert verified_cells == 60
    PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PREVIEWS_DIR / "assets_contact_sheet_lotso.png"
    sheet.save(out_path, "PNG", optimize=True)
    print(f"  [PREVIEW] Saved {out_path} ({sheet.size[0]}x{sheet.size[1]}) | 0/60 label overlaps verified (>=10px gap)!")


if __name__ == "__main__":
    main()
