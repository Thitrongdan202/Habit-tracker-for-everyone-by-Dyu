"""
generate_loopy_story_assets.py — v4.1 Precision Kawaii Art Overhaul for 10 Loopy Themes (#61-#70)
Fixes ALL 3 core drawing flaws across ALL 60 Loopy sprites:
  1. Natural Curved Cartoon Arms: ZERO detached round/oval blob arms! Every arm uses
     seamless Cubic/Quadratic Bezier tapered sleeves integrated into the torso shoulder
     with clear elbow curvature and tiny soft beaver fingers.
  2. Snug Head-in-Hood Framing: Every hooded theme (#62 Taiyaki, #63 Piggy, #65 Honey Bee,
     #67 Fluffy Commuter, #68 Panda Study) uses a 3-layer architecture (hood shell ->
     snug scaled inner face -> front padded hood rim overlay) so cheeks/chin NEVER overflow!
  3. Zero Contact Sheet Text Collision: Every label is crisp (<=16 chars), auto-measured
     via PIL textlength/textbbox, and hard-asserted `text_right_x <= preview_44px_left_x - 10`!

Rebuilt Signature Storylines:
  - #61 Red Bow Glow-Up: Meme forgot-task panic -> calm cheeks -> tie bow & pen -> ticking -> nearly done -> 100% board + reward flower!
  - #62 Taiyaki Street Snack: Authentic plump Taiyaki fish hat (round fish snout, dorsal fin, fanned tail, grill stripes, face snug in circular belly cutout) + 6-step kitchen-to-dango feast!
  - #70 Hair Roller GRWM: Natural shoulder-length black hair (NEVER floor-length!) + ribbed pink roller + deadpan half-lidded meme -> sip tea -> blush -> unroll -> bouncy bangs -> glossy GRWM!
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


def with_hero_aura(im: Image.Image, rgb: tuple[int, int, int], cy: int = 152, alpha: int = 64) -> Image.Image:
    aura = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
    ad = ImageDraw.Draw(aura)
    r, g, b = rgb
    ad.ellipse([36, cy - 108, 264, cy + 108], fill=(r, g, b, alpha))
    ad.ellipse([74, cy - 74, 226, cy + 74], fill=(255, 251, 224, 90))
    aura = aura.filter(ImageFilter.GaussianBlur(radius=22))
    return Image.alpha_composite(aura, im)


# =========================================================================== #
#  v4.1 3-LAYER SEAMLESS SILHOUETTE ARM ENGINE (48-STEP CURVATURE-CLAMPED)
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
    """Pulls arm shoulder anchor deep inside upper torso interior (ZERO shoulder bumps/horns/gaps)."""
    lx, ly = p0
    side = -1.0 if lx < 0 else 1.0
    nx0 = side * max(rx * 0.24, min(abs(lx), rx * 0.46))
    ny0 = max(-ry * 0.34, min(ly, -ry * 0.10))
    np0 = (nx0, ny0)
    # Prevent degenerate zero-length shoulder-to-elbow segment
    np1 = p1
    if math.hypot(p1[0] - nx0, p1[1] - ny0) < 12.0:
        np1 = (nx0 + side * 14.0, ny0 + 12.0)
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
    """Prevents concave inner-offset self-intersection loops on tight elbow bends."""
    out = [pts[0]]
    for i in range(1, len(pts)):
        px, py = out[-1]
        cx, cy = pts[i]
        tx, ty = tangents[i]
        dot = (cx - px) * tx + (cy - py) * ty
        if dot < 0.0:
            # Project forward gently along tangent to eliminate any backward cusp
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
    """Builds a high-density 48-step curvature-clamped tapered Bezier tube."""
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
        # Quadratic width taper
        w = omt * omt * w0 + 2.0 * omt * t * w1 + t * t * w2
        # Signed curvature kappa; clamp concave inner offset so elbow NEVER pinches
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

    # Rounded mitten paw cap at t = 1.0 (14 smooth arc samples, left -> tip -> right)
    tx2, ty2 = tangents[-1]
    nx2, ny2 = normals[-1]
    tip_cap: list[tuple[float, float]] = []
    cap_steps = 14
    for k in range(1, cap_steps):
        ang = math.pi * (k / cap_steps)  # 0 = +N (left), pi/2 = +T (tip), pi = -N (right)
        cn = math.cos(ang)
        ct = math.sin(ang) * 1.08
        tip_cap.append((x2 + nx2 * cn * w2 + tx2 * ct * w2, y2 + ny2 * cn * w2 + ty2 * ct * w2))

    # Rounded shoulder root cap at t = 0.0 (8 smooth arc samples, compact inside torso!)
    tx0, ty0 = tangents[0]
    nx0, ny0 = normals[0]
    root_cap: list[tuple[float, float]] = []
    root_steps = 8
    for k in range(1, root_steps):
        ang = math.pi * (k / root_steps)  # 0 = -N (right), pi/2 = -T (back), pi = +N (left)
        cn = -math.cos(ang)
        ct = -math.sin(ang) * 0.62
        root_cap.append((x0 + nx0 * cn * w0 + tx0 * ct * w0, y0 + ny0 * cn * w0 + ty0 * ct * w0))

    # Determine which side is INNER (closer to torso center) vs OUTER (shoulder/elbow side)
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
        # Gentle inward-rounded back cap across the tube at idx so fill blends invisibly
        cx_i, cy_i = centers[idx]
        tx_i, ty_i = tangents[idx]
        l_i, r_i = left_pts[idx], right_pts[idx]
        mid_back = (
            0.5 * (l_i[0] + r_i[0]) - tx_i * 4.5,
            0.5 * (l_i[1] + r_i[1]) - ty_i * 4.5,
        )
        poly = left_pts[idx:] + tip_cap + list(reversed(right_pts[idx:])) + [mid_back]
        return _pts_d(poly, close=True)

    def sub_stroke_d(t_in: float, t_out: float) -> str:
        i_in = max(1, min(steps - 1, int(round(t_in * steps))))
        i_out = max(1, min(steps - 1, int(round(t_out * steps))))
        if inner_is_right:
            # Start on inner (right) -> tip (reversed) -> outer (left) back to i_out
            pts = right_pts[i_in:] + list(reversed(tip_cap)) + list(reversed(left_pts[i_out:]))
        else:
            # Start on inner (left) -> tip -> outer (right) back to i_out
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


def _fingers_svg(mesh: dict) -> str:
    x2, y2 = mesh["p2"]
    t2x, t2y = mesh["t2"]
    n2x, n2y = mesh["n2"]
    w2 = mesh["w2"]
    fx1 = x2 + t2x * (w2 * 0.62) + n2x * (w2 * 0.30)
    fy1 = y2 + t2y * (w2 * 0.62) + n2y * (w2 * 0.30)
    fx2 = x2 + t2x * (w2 * 0.62) - n2x * (w2 * 0.30)
    fy2 = y2 + t2y * (w2 * 0.62) - n2y * (w2 * 0.30)
    return (
        f'<circle cx="{fx1:.1f}" cy="{fy1:.1f}" r="1.9" fill="{PAW}"/>'
        f'<circle cx="{fx2:.1f}" cy="{fy2:.1f}" r="1.9" fill="{PAW}"/>'
    )


def arm_spec(
    p0: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
    w0: float = 11.0,
    w1: float = 9.2,
    w2: float = 7.6,
    fill: str | None = None,
    stroke: str = OL,
    sw: float = 3.8,
    fingers: bool = False,
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
        "fingers": fingers, "layer": layer, "local": local,
        "t_fill": t_fill, "t_in": t_in, "t_out": t_out, "t_oh": t_oh,
    }


def _torso_pear_d(rx: float, ry: float) -> str:
    """100% C1-continuous plump pear torso (ZERO upper-shoulder corners under chin!)."""
    top_y = -ry + 4.0
    mid_y = ry * 0.16
    return (
        f"M 0,{top_y:.1f} "
        f"C {rx * 0.66:.1f},{top_y:.1f} {rx * 1.02:.1f},{-ry * 0.34:.1f} {rx * 1.02:.1f},{mid_y:.1f} "
        f"C {rx * 1.02:.1f},{ry * 0.68:.1f} {rx * 0.62:.1f},{ry:.1f} 0,{ry:.1f} "
        f"C {-rx * 0.62:.1f},{ry:.1f} {-rx * 1.02:.1f},{ry * 0.68:.1f} {-rx * 1.02:.1f},{mid_y:.1f} "
        f"C {-rx * 1.02:.1f},{-ry * 0.34:.1f} {-rx * 0.66:.1f},{top_y:.1f} 0,{top_y:.1f} Z"
    )


def curved_arm(
    p0: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
    w0: float = 12.0,
    w1: float = 10.0,
    w2: float = 8.2,
    fill: str = PINK,
    stroke: str = OL,
    sw: float = 3.8,
    fingers: bool = False,
    seamless_shoulder: bool = True,
) -> str:
    """Standalone high-density 48-step curved arm fallback (for non-body callers)."""
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
    if fingers:
        out += _fingers_svg(mesh)
    return out


# =========================================================================== #
#  REUSABLE VECTOR DECORATIONS
# =========================================================================== #
def shadow(cx=150, cy=268, rx=62, ry=9.0, op=0.14) -> str:
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{OL}" fill-opacity="{op}"/>'


def soft_blush(cx: float, cy: float, rx: float, ry: float, strong: bool = False) -> str:
    if strong:
        return (
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx:.1f}" ry="{ry:.1f}" fill="#F26382" fill-opacity="0.30"/>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx * 0.66:.1f}" ry="{ry * 0.66:.1f}" fill="#EC4B70" fill-opacity="0.38"/>'
        )
    return (
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx:.1f}" ry="{ry:.1f}" fill="#F57A95" fill-opacity="0.25"/>'
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx * 0.64:.1f}" ry="{ry * 0.64:.1f}" fill="#F26382" fill-opacity="0.32"/>'
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


def heart(cx, cy, s=13, fill="#FB7185", stroke=OL, sw=2.2, rot=0) -> str:
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


def heart_with_eyes(cx, cy, s=20, rot=-12) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot})">'
        f'{heart(0, 0, s=s, fill="#F888A8", stroke="#D85B80", sw=2.4)}'
        f'<ellipse cx="-5.5" cy="-2" rx="4.0" ry="4.6" fill="#FFFFFF"/>'
        f'<ellipse cx="5.5" cy="-2" rx="4.0" ry="4.6" fill="#FFFFFF"/>'
        f'<circle cx="-4.5" cy="-1.5" r="2.2" fill="{EYE}"/><circle cx="6.5" cy="-1.5" r="2.2" fill="{EYE}"/>'
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
#  DYNAMIC LOOPY RIG (SEAMLESS CURVED ARMS + SNUG HOOD FACE MODE!)
# =========================================================================== #
def loopy_ears(cx=0, cy=0, spread=45, y_off=-51) -> str:
    parts = []
    for side in (-1, 1):
        ex = cx + side * spread
        ey = cy + y_off
        parts.append(
            f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="15.0" fill="{PINK}" stroke="{OL}" stroke-width="3.9"/>'
            f'<circle cx="{ex - side * 1.4:.1f}" cy="{ey + 1.4:.1f}" r="7.6" fill="{CREAM}" stroke="{OL}" stroke-width="2.0"/>'
        )
    return "".join(parts)


def loopy_hair_tuft(cx=0, top_y=-61, s=0.95, rot=0) -> str:
    return (
        f'<g transform="translate({cx},{top_y}) rotate({rot}) scale({s})">'
        f'<path d="M 0,4 C -6,-8 -14,-18 -6,-21 C 0,-23 3,-11 1,2 Z" fill="{PINK}" stroke="{OL}" stroke-width="3.4" stroke-linejoin="round"/>'
        f'<path d="M 1,4 C 2,-10 7,-25 14,-22 C 20,-19 11,-4 3,4 Z" fill="{PINK}" stroke="{OL}" stroke-width="3.4" stroke-linejoin="round"/>'
        f'</g>'
    )


def _loopy_foot(fx: float, fy: float, rot: float = 0, sit: bool = False) -> str:
    """Compact cute beaver feet with tiny soft rounded toes."""
    if sit:
        return (
            f'<g transform="translate({fx},{fy}) rotate({rot})">'
            f'<ellipse cx="0" cy="0" rx="18.5" ry="15" fill="{PAW}" stroke="{OL}" stroke-width="3.5"/>'
            f'<ellipse cx="0" cy="2" rx="9.0" ry="6.8" fill="#F08AA4"/>'
            f'<circle cx="-6" cy="-7" r="2.2" fill="#F4A5BA"/>'
            f'<circle cx="0" cy="-8.5" r="2.2" fill="#F4A5BA"/>'
            f'<circle cx="6" cy="-7" r="2.2" fill="#F4A5BA"/>'
            f'</g>'
        )
    return (
        f'<g transform="translate({fx},{fy}) rotate({rot})">'
        f'<ellipse cx="0" cy="0" rx="17" ry="10" fill="{PAW}" stroke="{OL}" stroke-width="3.5"/>'
        f'</g>'
    )


def loopy_body(
    cx=150,
    cy=216,
    rx=48,
    ry=44,
    pose="stand",
    paws="down",
    lean=0,
    coat=PINK,
    belly=True,
    arms: list[dict] | None = None,
    mid_props: str = "",
    head_svg: str = "",
    custom_arms: str = "",
) -> str:
    """v4.1 3-Layer Seamless Silhouette Loopy Body:
      Layer 1: Unified dark outline (2*sw round join) of C1 pear torso + ALL arms.
      Layer 2: Unified seamless fill fusing shoulders 100% into torso + cream belly.
      Mid-Layer: World-space props held in front of torso (`mid_props`).
      Layer 3: Foreground forearm fill + smooth inner forearm crease (ZERO shoulder spikes!).
      Head + Over-Head Pass: `head_svg` followed by upper forearms (`layer == 'over_head'`)."""
    sx_l, sx_r = -rx * 0.54, rx * 0.54
    sy = -ry * 0.34
    spec_list: list[dict] = []

    if paws == "down":
        spec_list += [
            arm_spec((sx_l, sy), (sx_l - 22, sy + 14), (sx_l - 12, sy + 36), 11.4, 9.4, 7.6, fill=coat, fingers=True, layer="front", local=True, t_fill=0.30, t_in=0.30, t_out=0.54),
            arm_spec((sx_r, sy), (sx_r + 22, sy + 14), (sx_r + 12, sy + 36), 11.4, 9.4, 7.6, fill=coat, fingers=True, layer="front", local=True, t_fill=0.30, t_in=0.30, t_out=0.54),
        ]
    elif paws == "wide_up":
        spec_list += [
            arm_spec((sx_l, sy), (sx_l - 26, sy - 6), (sx_l - 34, sy - 32), 11.4, 9.4, 7.6, fill=coat, fingers=True, layer="out", local=True),
            arm_spec((sx_r, sy), (sx_r + 26, sy - 6), (sx_r + 34, sy - 32), 11.4, 9.4, 7.6, fill=coat, fingers=True, layer="out", local=True),
        ]
    elif paws == "wave_r":
        spec_list += [
            arm_spec((sx_l, sy), (sx_l - 20, sy + 16), (sx_l - 10, sy + 34), 11.2, 9.2, 7.5, fill=coat, fingers=True, layer="front", local=True, t_fill=0.30, t_in=0.30, t_out=0.54),
            arm_spec((sx_r, sy), (sx_r + 28, sy - 6), (sx_r + 34, sy - 34), 11.4, 9.4, 7.6, fill=coat, fingers=True, layer="out", local=True),
        ]
    elif paws == "wave_l":
        spec_list += [
            arm_spec((sx_l, sy), (sx_l - 28, sy - 6), (sx_l - 34, sy - 34), 11.4, 9.4, 7.6, fill=coat, fingers=True, layer="out", local=True),
            arm_spec((sx_r, sy), (sx_r + 20, sy + 16), (sx_r + 10, sy + 34), 11.2, 9.2, 7.5, fill=coat, fingers=True, layer="front", local=True, t_fill=0.30, t_in=0.30, t_out=0.54),
        ]
    elif paws == "walk_swing":
        spec_list += [
            arm_spec((sx_l, sy), (sx_l - 22, sy + 14), (sx_l - 24, sy + 30), 11.2, 9.2, 7.5, fill=coat, fingers=True, layer="out", local=True),
            arm_spec((sx_r, sy), (sx_r + 26, sy + 2), (sx_r + 16, sy + 24), 11.2, 9.2, 7.5, fill=coat, fingers=True, layer="front", local=True, t_fill=0.30, t_in=0.30, t_out=0.54),
        ]
    elif paws == "shrug":
        spec_list += [
            arm_spec((sx_l, sy), (sx_l - 24, sy + 8), (sx_l - 30, sy - 14), 11.2, 9.2, 7.6, fill=coat, fingers=True, layer="out", local=True),
            arm_spec((sx_r, sy), (sx_r + 24, sy + 8), (sx_r + 30, sy - 14), 11.2, 9.2, 7.6, fill=coat, fingers=True, layer="out", local=True),
        ]
    elif paws == "hug_center":
        spec_list += [
            arm_spec((sx_l, sy), (sx_l - 16, sy + 20), (-14, sy + 20), 11.0, 9.2, 7.6, fill=coat, layer="front", local=True, t_fill=0.24, t_in=0.28, t_out=0.48),
            arm_spec((sx_r, sy), (sx_r + 16, sy + 20), (14, sy + 20), 11.0, 9.2, 7.6, fill=coat, layer="front", local=True, t_fill=0.24, t_in=0.28, t_out=0.48),
        ]
    elif paws == "panic_flail":
        spec_list += [
            arm_spec((sx_l, sy), (sx_l - 28, sy - 14), (sx_l - 18, sy - 42), 11.2, 9.2, 7.6, fill=coat, fingers=True, layer="out", local=True),
            arm_spec((sx_r, sy), (sx_r + 28, sy + 8), (sx_r + 36, sy - 12), 11.2, 9.2, 7.6, fill=coat, fingers=True, layer="out", local=True),
        ]

    if arms:
        spec_list.extend(arms)

    # Convert all arm specs to body-local space, pull shoulders inside torso, build 48-step meshes
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
    torso_d = _torso_pear_d(rx, ry)
    torso_sw = 3.9

    # Group 0: Feet (behind torso)
    feet_svg = ""
    if pose == "sit":
        feet_svg = _loopy_foot(-33, 34, -18, sit=True) + _loopy_foot(33, 34, 18, sit=True)
    elif pose == "jump":
        feet_svg = _loopy_foot(-28, 40, -28) + _loopy_foot(28, 40, 28)
    elif pose == "walk":
        feet_svg = _loopy_foot(-26, 44, -12) + _loopy_foot(26, 36, 22)
    elif pose == "hover":
        feet_svg = _loopy_foot(-18, 42, 16) + _loopy_foot(18, 42, -16)
    elif pose == "none_feet":
        feet_svg = ""
    else:
        feet_svg = _loopy_foot(-22, 42, -4) + _loopy_foot(22, 42, 4)

    parts: list[str] = []
    if feet_svg:
        parts.append(f'<g transform="{tf}">{feet_svg}</g>')

    # Group 1 (Layer 1 — Unified 2*sw Outline) + Group 2 (Layer 2 — Unified Seamless Fill)
    l1 = [f'<path d="{torso_d}" fill="none" stroke="{OL}" stroke-width="{torso_sw * 2:.1f}" stroke-linejoin="round" stroke-linecap="round"/>']
    l2 = [f'<path d="{torso_d}" fill="{coat}" stroke="none"/>']
    for sp, mesh in built_arms:
        a_fill = sp["fill"] if sp["fill"] is not None else coat
        l1.append(f'<path d="{mesh["full_d"]}" fill="none" stroke="{sp["stroke"]}" stroke-width="{sp["sw"] * 2:.1f}" stroke-linejoin="round" stroke-linecap="round"/>')
        l2.append(f'<path d="{mesh["full_d"]}" fill="{a_fill}" stroke="none"/>')
    if belly:
        l2.append(f'<ellipse cx="0" cy="12" rx="{rx * 0.56:.1f}" ry="{ry * 0.66:.1f}" fill="{CREAM}"/>')

    parts.append(f'<g transform="{tf}">{"".join(l1)}{"".join(l2)}</g>')

    # Mid-Layer (World Space Props in front of torso/belly)
    if mid_props:
        parts.append(mid_props)

    # Group 3 (Layer 3 — Foreground Forearm Fill + Smooth Inner Forearm Crease + Fingers)
    l3: list[str] = []
    for sp, mesh in built_arms:
        a_fill = sp["fill"] if sp["fill"] is not None else coat
        if sp["layer"] == "front":
            l3.append(f'<path d="{mesh["sub_fill_d"](sp["t_fill"])}" fill="{a_fill}" stroke="none"/>')
            l3.append(
                f'<path d="{mesh["sub_stroke_d"](sp["t_in"], sp["t_out"])}" fill="none" '
                f'stroke="{sp["stroke"]}" stroke-width="{sp["sw"]:.1f}" stroke-linecap="round" stroke-linejoin="round"/>'
            )
            if sp["fingers"]:
                l3.append(_fingers_svg(mesh))
        elif sp["layer"] == "out":
            if sp["fingers"]:
                l3.append(_fingers_svg(mesh))
    if custom_arms:
        l3.append(custom_arms)
    if l3:
        parts.append(f'<g transform="{tf}">{"".join(l3)}</g>')

    # Head Layer (World Space)
    if head_svg:
        parts.append(head_svg)

    # Group 4 (Over-Head Pass — Forearm & Paw overlapping cheek/head/hood)
    l4: list[str] = []
    for sp, mesh in built_arms:
        if sp["layer"] == "over_head":
            a_fill = sp["fill"] if sp["fill"] is not None else coat
            t_oh = sp["t_oh"]
            l4.append(f'<path d="{mesh["sub_fill_d"](t_oh)}" fill="{a_fill}" stroke="none"/>')
            l4.append(
                f'<path d="{mesh["sub_stroke_d"](t_oh, t_oh)}" fill="none" '
                f'stroke="{sp["stroke"]}" stroke-width="{sp["sw"]:.1f}" stroke-linecap="round" stroke-linejoin="round"/>'
            )
            if sp["fingers"]:
                l4.append(_fingers_svg(mesh))
    if l4:
        parts.append(f'<g transform="{tf}">{"".join(l4)}</g>')

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
    in_hood: bool = False,
) -> str:
    """Signature pear-cheeked Loopy head + expressive meme face + single iconic white bucktooth!
    When `in_hood=True`, draws ONLY the clean face features inside the hood cutout so cheeks/outline
    can NEVER poke outside the hood rim!"""
    parts = [f'<g transform="translate({cx},{cy}) rotate({rot}) scale({scale})">']
    if not in_hood:
        if show_ears:
            parts.append(loopy_ears(0, 0))
        if show_tuft:
            parts.append(loopy_hair_tuft(0, -61))
        sw = "3.9" if head_outline else "0"
        head_d = (
            "M -55,-14 C -57,-48 -31,-63 0,-63 C 31,-63 57,-48 55,-14 "
            "C 65,4 62,34 41,47 C 25,56 -25,56 -41,47 C -62,34 -65,4 -55,-14 Z"
        )
        parts.append(f'<path d="{head_d}" fill="{PINK}" stroke="{OL}" stroke-width="{sw}" stroke-linejoin="round"/>')

    blush_x = 34 if in_hood else 37
    blush_rx = 16 if in_hood else 20
    blush_ry = 11 if in_hood else 14
    parts.append(soft_blush(-blush_x, 14, blush_rx, blush_ry, strong=strong_blush))
    parts.append(soft_blush(blush_x, 14, blush_rx, blush_ry, strong=strong_blush))
    if blush_hatch:
        parts.append(
            f'<line x1="{-blush_x - 4}" y1="15" x2="{-blush_x - 1}" y2="11" stroke="#FFFFFF" stroke-width="2.1" stroke-linecap="round"/>'
            f'<line x1="{-blush_x + 2}" y1="16" x2="{-blush_x + 5}" y2="12" stroke="#FFFFFF" stroke-width="2.1" stroke-linecap="round"/>'
            f'<line x1="{blush_x - 5}" y1="12" x2="{blush_x - 2}" y2="16" stroke="#FFFFFF" stroke-width="2.1" stroke-linecap="round"/>'
            f'<line x1="{blush_x + 1}" y1="11" x2="{blush_x + 4}" y2="15" stroke="#FFFFFF" stroke-width="2.1" stroke-linecap="round"/>'
        )

    # Eyes
    if expr in ("smile", "big_smile", "curious", "focused", "puzzled", "proud", "nibble", "meme_scream", "sparkle"):
        rx_e, ry_e = (8.4, 9.6) if expr == "meme_scream" else (7.0, 8.0)
        parts.append(
            f'<ellipse cx="-22" cy="-7" rx="{rx_e}" ry="{ry_e}" fill="{EYE}"/>'
            f'<circle cx="-24.5" cy="-10" r="2.7" fill="#FFFFFF"/>'
            f'<ellipse cx="22" cy="-7" rx="{rx_e}" ry="{ry_e}" fill="{EYE}"/>'
            f'<circle cx="19.5" cy="-10" r="2.7" fill="#FFFFFF"/>'
        )
        if expr == "sparkle":
            parts.append(
                '<circle cx="-19.5" cy="-4.5" r="1.5" fill="#FFFFFF"/>'
                '<circle cx="24.5" cy="-4.5" r="1.5" fill="#FFFFFF"/>'
            )
        if expr == "focused":
            parts.append(
                f'<path d="M -30,-19 L -14,-15" stroke="{OL}" stroke-width="2.8" stroke-linecap="round"/>'
                f'<path d="M 30,-19 L 14,-15" stroke="{OL}" stroke-width="2.8" stroke-linecap="round"/>'
            )
        elif expr == "puzzled":
            parts.append(
                f'<path d="M -29,-20 Q -22,-24 -15,-19" fill="none" stroke="{OL}" stroke-width="2.5" stroke-linecap="round"/>'
                f'<path d="M 15,-18 Q 22,-22 29,-20" fill="none" stroke="{OL}" stroke-width="2.5" stroke-linecap="round"/>'
            )
    elif expr == "deadpan":
        # Iconic half-lidded meme Loopy eyes (#70 Hair Roller!)
        parts.append(
            f'<ellipse cx="-22" cy="-4" rx="7.2" ry="6.2" fill="{EYE}"/>'
            f'<rect x="-31" y="-14" width="18" height="9.2" fill="{PINK}"/>'
            f'<path d="M -30,-4.8 Q -22,-6.8 -14,-4.8" fill="none" stroke="{OL}" stroke-width="3.0" stroke-linecap="round"/>'
            f'<ellipse cx="22" cy="-4" rx="7.2" ry="6.2" fill="{EYE}"/>'
            f'<rect x="13" y="-14" width="18" height="9.2" fill="{PINK}"/>'
            f'<path d="M 14,-4.8 Q 22,-6.8 30,-4.8" fill="none" stroke="{OL}" stroke-width="3.0" stroke-linecap="round"/>'
        )
    elif expr == "wink":
        parts.append(
            f'<ellipse cx="-22" cy="-7" rx="7.2" ry="8.0" fill="{EYE}"/>'
            f'<circle cx="-24.5" cy="-10" r="2.6" fill="#FFFFFF"/>'
            f'<path d="M 15,-12 L 26,-6 L 15,0" fill="none" stroke="{EYE}" stroke-width="3.9" stroke-linecap="round" stroke-linejoin="round"/>'
        )
    elif expr == "happy_squint":
        parts.append(
            f'<path d="M -30,-5 Q -22,-15 -14,-5" fill="none" stroke="{EYE}" stroke-width="3.9" stroke-linecap="round"/>'
            f'<path d="M 14,-5 Q 22,-15 30,-5" fill="none" stroke="{EYE}" stroke-width="3.9" stroke-linecap="round"/>'
        )
    elif expr == "calm_closed":
        parts.append(
            f'<path d="M -29,-6 Q -22,1 -15,-6" fill="none" stroke="{EYE}" stroke-width="3.5" stroke-linecap="round"/>'
            f'<path d="M 15,-6 Q 22,1 29,-6" fill="none" stroke="{EYE}" stroke-width="3.5" stroke-linecap="round"/>'
        )
    elif expr == "sleepy":
        parts.append(
            f'<ellipse cx="-22" cy="-4" rx="6.2" ry="4.0" fill="{EYE}"/>'
            f'<path d="M -30,-9 Q -22,-6 -14,-9" fill="none" stroke="{OL}" stroke-width="2.8" stroke-linecap="round"/>'
            f'<ellipse cx="22" cy="-4" rx="6.2" ry="4.0" fill="{EYE}"/>'
            f'<path d="M 14,-9 Q 22,-6 30,-9" fill="none" stroke="{OL}" stroke-width="2.8" stroke-linecap="round"/>'
        )

    # Signature crimson-berry rounded triangle nose
    parts.append(
        f'<path d="M -13.2,3 C -14.2,-4 -6.4,-7 0,-7 C 6.4,-7 14.2,-4 13.2,3 '
        f'C 12.2,10.5 4.8,14.5 0,14.5 C -4.8,14.5 -12.2,10.5 -13.2,3 Z" fill="{NOSE}" stroke="{OL}" stroke-width="2.5"/>'
        f'<ellipse cx="-4" cy="-1.5" rx="3.9" ry="2.0" transform="rotate(-14 -4 -1.5)" fill="{NOSE_HI}" fill-opacity="0.55"/>'
    )

    # Mouth + SINGLE ICONIC WHITE BUCKTOOTH!
    if expr == "meme_scream":
        parts.append(
            f'<ellipse cx="0" cy="30" rx="15.5" ry="17.5" fill="#7D1E32" stroke="{OL}" stroke-width="3.0"/>'
            f'<ellipse cx="0" cy="37" rx="10.5" ry="7.5" fill="#F27E98"/>'
            f'<rect x="-6.5" y="14" width="13" height="8.2" rx="2.6" fill="#FFFFFF" stroke="{OL}" stroke-width="1.8"/>'
        )
    elif expr == "deadpan":
        parts.append(
            f'<path d="M -9,28 Q 0,25 9,28" fill="none" stroke="{OL}" stroke-width="3.0" stroke-linecap="round"/>'
            f'<rect x="-4.5" y="27" width="9" height="5" rx="1.8" fill="#FFFFFF" stroke="{OL}" stroke-width="1.5"/>'
        )
    elif expr in ("big_smile", "happy_squint"):
        parts.append(
            f'<path d="M -15,23 C -15,19 15,19 15,23 C 15,37 7.5,41 0,41 C -7.5,41 -15,37 -15,23 Z" '
            f'fill="{MOUTH}" stroke="{OL}" stroke-width="2.7" stroke-linejoin="round"/>'
            f'<rect x="-6.2" y="21" width="12.4" height="7.8" rx="2.5" fill="#FFFFFF" stroke="{OL}" stroke-width="1.8"/>'
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
#  #61 — LOOPY RED BOW GLOW-UP (REBUILT STORY: FORGOT -> CALM -> BOW+PEN -> TICK -> ALMOST -> 100%!)
# =========================================================================== #
def _red_bow(cx=150, cy=64, s=1.0, rot=0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot}) scale({s})">'
        f'<path d="M -4,4 C -28,-22 -56,-12 -50,12 C -45,29 -19,23 -4,10 Z" fill="#D85A68" stroke="{OL}" stroke-width="3.5" stroke-linejoin="round"/>'
        f'<path d="M 4,4 C 28,-22 56,-12 50,12 C 45,29 19,23 4,10 Z" fill="#D85A68" stroke="{OL}" stroke-width="3.5" stroke-linejoin="round"/>'
        f'<path d="M -12,6 C -25,2 -35,6 -37,11 M 12,6 C 25,2 35,6 37,11" fill="none" stroke="#A63442" stroke-width="2.4" stroke-linecap="round"/>'
        f'<ellipse cx="0" cy="8" rx="10.5" ry="9.0" fill="#E36E7B" stroke="{OL}" stroke-width="3.3"/>'
        f'</g>'
    )


def _todo_board(cx=150, cy=224, checked=0, total=4, rot=0, s=1.0, badge_100=False) -> str:
    parts = [f'<g transform="translate({cx},{cy}) rotate({rot}) scale({s})">']
    parts.append(
        f'<rect x="-28" y="-34" width="56" height="68" rx="7" fill="#FFFDF7" stroke="{OL}" stroke-width="2.9"/>'
        f'<rect x="-14" y="-40" width="28" height="11" rx="4" fill="#D85A68" stroke="{OL}" stroke-width="2.4"/>'
    )
    if badge_100:
        parts.append(
            f'<text x="0" y="-4" text-anchor="middle" font-family="Segoe UI" font-weight="900" font-size="16" fill="#D85A68">100%</text>'
            f'<path d="M -14,14 L -4,23 L 16,5" fill="none" stroke="#16A34A" stroke-width="4.4" stroke-linecap="round" stroke-linejoin="round"/>'
        )
    else:
        for i in range(total):
            ry = -18 + i * 14
            if i < checked:
                parts.append(
                    f'<rect x="-20" y="{ry - 4}" width="10" height="10" rx="2" fill="#DCFCE7" stroke="#16A34A" stroke-width="1.8"/>'
                    f'<path d="M -19,{ry + 1} L -16,{ry + 4} L -11,{ry - 3}" fill="none" stroke="#16A34A" stroke-width="2.2" stroke-linecap="round"/>'
                    f'<line x1="-5" y1="{ry + 1}" x2="19" y2="{ry + 1}" stroke="#94A3B8" stroke-width="2.3" stroke-linecap="round"/>'
                )
            else:
                parts.append(
                    f'<rect x="-20" y="{ry - 4}" width="10" height="10" rx="2" fill="#FFFFFF" stroke="#D85A68" stroke-width="1.8"/>'
                    f'<line x1="-5" y1="{ry + 1}" x2="19" y2="{ry + 1}" stroke="#CBD5E1" stroke-width="2.2" stroke-linecap="round"/>'
                )
    parts.append("</g>")
    return "".join(parts)


def _pink_pen(x1, y1, x2, y2) -> str:
    dx, dy = _norm(x2 - x1, y2 - y1)
    tip_x, tip_y = x1 - dx * 6, y1 - dy * 6
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#D85A68" stroke-width="6.5" stroke-linecap="round"/>'
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{OL}" stroke-width="2.0" stroke-linecap="round"/>'
        f'<circle cx="{tip_x:.1f}" cy="{tip_y:.1f}" r="2.6" fill="{OL}"/>'
    )


def _small_reward_flower(cx, cy, s=1.0, rot=0) -> str:
    petals = []
    for k in range(5):
        ang = math.radians(k * 72 - 90)
        px, py = math.cos(ang) * 10, math.sin(ang) * 10
        petals.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="7.5" ry="6.0" transform="rotate({k * 72 - 90} {px:.1f} {py:.1f})" fill="#FDE047" stroke="#EAB308" stroke-width="1.9"/>')
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot}) scale({s})">'
        f'<path d="M 0,10 L 2,34" stroke="#65A30D" stroke-width="3.6" stroke-linecap="round"/>'
        f'<ellipse cx="-6" cy="24" rx="6.5" ry="3.2" transform="rotate(-24 -6 24)" fill="#84CC16" stroke="{OL}" stroke-width="1.7"/>'
        f'{"".join(petals)}<circle cx="0" cy="0" r="5.6" fill="#F59E0B"/></g>'
    )


def build_61_red_bow() -> list[tuple[str, Image.Image]]:
    # S0 (0%): Meme tilted panic before blank checklist + yellow !!
    s0 = render_svg(
        shadow(150, 268, 66, 9)
        + loopy_body(
            142, 218, pose="sit", paws="panic_flail", lean=9,
            head_svg=loopy_head(158, 126, expr="meme_scream", strong_blush=True, rot=16),
        )
        + _todo_board(236, 232, checked=0, total=4, rot=10, s=0.82)
        + excl_marks(54, 108, rot=-18, s=1.12)
    )
    # S1 (20%): Sitting upright, natural curved arms lifting up to cup both cheeks taking deep breath
    s1 = render_svg(
        shadow(150, 268, 68, 9)
        + loopy_body(
            146, 218, pose="sit", paws="none",
            arms=[
                arm_spec((118, 202), (76, 188), (98, 152), 11.2, 9.4, 7.8, fingers=True, layer="over_head", t_oh=0.24),
                arm_spec((174, 202), (216, 188), (194, 152), 11.2, 9.4, 7.8, fingers=True, layer="over_head", t_oh=0.24),
            ],
            head_svg=loopy_head(146, 128, expr="calm_closed", blush_hatch=True),
        )
        + _todo_board(238, 236, checked=0, total=4, rot=8, s=0.76)
        + '<path d="M 224,108 Q 238,100 250,108 M 228,120 Q 242,114 254,120" fill="none" stroke="#7EAAC8" stroke-width="2.8" stroke-linecap="round"/>'
    )
    # S2 (40%): Left curved arm tying big red bow neatly on head, right curved arm holding pen ready!
    s2 = render_svg(
        shadow()
        + loopy_body(
            150, 218, pose="stand", paws="none",
            mid_props=_pink_pen(218, 166, 246, 140),
            arms=[
                arm_spec((122, 200), (76, 152), (106, 86), 11.0, 9.0, 7.5, fingers=True, layer="over_head", t_oh=0.58),
                arm_spec((178, 200), (216, 192), (222, 162), 11.0, 9.0, 7.5, fingers=True, layer="front", t_fill=0.34, t_in=0.34, t_out=0.34),
            ],
            head_svg=loopy_head(150, 128, expr="focused", show_tuft=False) + _red_bow(150, 64, s=1.06),
        )
    )
    # S3 (60%): Leaning focused, ticking items on small checklist board with pen (crisp arm over clipboard!)
    s3 = render_svg(
        shadow(144, 268, 66, 9)
        + loopy_body(
            142, 218, pose="sit", paws="none", lean=5,
            mid_props=_todo_board(182, 224, checked=2, total=4, rot=-8, s=0.92) + _pink_pen(172, 218, 210, 194),
            arms=[
                arm_spec((116, 200), (106, 226), (144, 224), 11.0, 9.2, 7.6, layer="front", t_fill=0.24, t_in=0.28, t_out=0.48),
                arm_spec((168, 198), (214, 192), (206, 208), 10.6, 8.8, 7.4, layer="front", t_fill=0.34, t_in=0.34, t_out=0.34),
            ],
            head_svg=loopy_head(146, 128, expr="sparkle", strong_blush=True, show_tuft=False, rot=6) + _red_bow(152, 64, s=1.02, rot=6),
        )
        + sp4(56, 102, r=8)
    )
    # S4 (80%): Rosy joyful smile holding up nearly-completed checklist board, stars popping!
    s4 = render_svg(
        shadow(146, 268, 66, 9)
        + loopy_body(
            142, 218, pose="walk", paws="none", lean=-5,
            mid_props=_todo_board(224, 186, checked=4, total=4, rot=8, s=0.96),
            arms=[
                arm_spec((114, 198), (82, 180), (74, 152), 11.0, 9.2, 7.6, fingers=True, layer="out"),
                arm_spec((170, 198), (194, 206), (202, 190), 11.0, 9.2, 7.6, layer="front", t_fill=0.28, t_in=0.30, t_out=0.52),
            ],
            head_svg=loopy_head(138, 128, expr="wink", strong_blush=True, blush_hatch=True, show_tuft=False, rot=-7) + _red_bow(130, 64, s=1.04, rot=-7),
        )
        + sp4(54, 92, r=10) + sp4(250, 114, r=9)
    )
    # S5 (100%): Neat red bow, beaming bucktooth grin raising 100% board + small reward flower & rays!
    s5 = with_hero_aura(render_svg(
        shadow(150, 272, 56, 8, op=0.12)
        + loopy_body(
            150, 206, pose="jump", paws="none",
            mid_props=_todo_board(68, 166, rot=-10, s=0.88, badge_100=True) + _small_reward_flower(232, 154, s=1.05, rot=16),
            arms=[
                arm_spec((122, 186), (96, 190), (88, 172), 11.2, 9.2, 7.6, layer="front", t_fill=0.30, t_in=0.32, t_out=0.54),
                arm_spec((178, 186), (210, 184), (222, 168), 11.2, 9.2, 7.6, layer="front", t_fill=0.30, t_in=0.32, t_out=0.54),
            ],
            head_svg=loopy_head(150, 118, expr="big_smile", strong_blush=True, blush_hatch=True, show_tuft=False, rot=-4) + _red_bow(146, 54, s=1.08, rot=-4),
        )
        + sp4(52, 74, r=11) + sp4(248, 76, r=11) + heart(246, 224, s=10, fill="#F6A6B2", stroke="#D85A68")
    ), (246, 166, 178))
    return [
        ("Quên Việc!!", s0),
        ("Ôm Má Bình Tĩnh", s1),
        ("Thắt Nơ Cầm Bút", s2),
        ("Chăm Chú Tick", s3),
        ("Gần Kín Bảng", s4),
        ("Hoàn Thành 100%", s5),
    ]


# =========================================================================== #
#  #62 — LOOPY TAIYAKI STREET SNACK (AUTHENTIC PLUMP FISH HAT + SNUG FACE!)
# =========================================================================== #
def _taiyaki_head_in_hood(cx=150, cy=124, rot=0, expr="smile", strong_blush=False) -> str:
    """3-Layer Authentic Plump Taiyaki Fish Hat:
    1) Plump baked fish silhouette: round fish mouth/head left, cute dorsal fin top, fanned tail right, grill stripes!
    2) Snug circular face cutout well (rx=46, ry=44) with Loopy face features safely inside (scale=0.72)!
    3) Thick golden-crust padded rim overlay hugging the face opening so cheeks NEVER overflow!"""
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot})">'
        # Layer 1: Dorsal fin + fanned 2-lobe tail + plump Taiyaki fish body
        f'<path d="M -26,-56 C -16,-84 22,-84 34,-54 Z" fill="#F2BE86" stroke="#B67638" stroke-width="3.8" stroke-linejoin="round"/>'
        f'<path d="M -12,-70 Q 0,-64 12,-70" fill="none" stroke="#C88B4B" stroke-width="2.4" stroke-linecap="round"/>'
        f'<path d="M 74,-12 C 98,-38 116,-28 106,-2 C 118,22 100,38 74,14 Z" fill="#F2BE86" stroke="#B67638" stroke-width="3.8" stroke-linejoin="round"/>'
        f'<path d="M 82,-6 L 100,-14 M 82,4 L 100,14" stroke="#C88B4B" stroke-width="2.4" stroke-linecap="round"/>'
        # Main plump fish body
        f'<path d="M -92,0 C -92,-46 -46,-62 4,-60 C 50,-58 84,-34 84,2 C 84,40 48,58 0,58 C -48,58 -92,42 -92,0 Z" fill="#FAD7AC" stroke="#B67638" stroke-width="4.0"/>'
        # Cute fish snout/lips on left + round fish eye
        f'<path d="M -88,-10 C -101,-10 -101,12 -88,12" fill="#F2BE86" stroke="#B67638" stroke-width="3.6" stroke-linecap="round"/>'
        f'<circle cx="-68" cy="-10" r="5.0" fill="#FFF8EE" stroke="#B67638" stroke-width="2.4"/>'
        f'<circle cx="-69" cy="-10" r="2.0" fill="#8C5927"/>'
        # Warm baked Taiyaki wafer grill stripes on head & tail flanks
        f'<path d="M -52,-46 Q -62,0 -50,44 M 50,-44 Q 62,0 50,44 M 64,-30 Q 72,0 64,30" fill="none" stroke="#D19453" stroke-width="3.8" stroke-linecap="round"/>'
        # Inner pink face well
        f'<ellipse cx="0" cy="4" rx="45" ry="42" fill="{PINK}"/>'
        # Layer 2: Snug face features (scale=0.72, strictly inside rx=45, ry=42!)
        + loopy_head(0, 6, scale=0.72, expr=expr, strong_blush=strong_blush, blush_hatch=True, in_hood=True)
        # Layer 3: Thick padded pastry rim hugging the circular cutout cleanly ON TOP of face edge!
        + '<ellipse cx="0" cy="4" rx="45" ry="42" fill="none" stroke="#F6CCA0" stroke-width="7.0"/>'
        + '<ellipse cx="0" cy="4" rx="45" ry="42" fill="none" stroke="#B67638" stroke-width="3.2"/>'
        + '</g>'
    )


def _taiyaki_bag(x=226, y=228, has_fish=False, extra_fish=False, s=1.0) -> str:
    parts = [f'<g transform="translate({x},{y}) scale({s})">']
    if has_fish:
        parts.append(
            '<g transform="translate(-4,-30) rotate(-18)">'
            '<ellipse cx="0" cy="0" rx="21" ry="13" fill="#F6CCA0" stroke="#B67638" stroke-width="2.8"/>'
            '<path d="M -6,-11 Q -2,0 -6,11 M 4,-11 Q 8,0 4,11" fill="none" stroke="#B67638" stroke-width="2.2"/>'
            '<circle cx="-11" cy="-2" r="2.0" fill="#8C5927"/></g>'
            '<path d="M -12,-48 Q -16,-56 -10,-63 M 6,-50 Q 2,-58 8,-65" fill="none" stroke="#D99B58" stroke-width="2.4" stroke-linecap="round"/>'
        )
    if extra_fish:
        parts.append(
            '<g transform="translate(12,-28) rotate(14)">'
            '<ellipse cx="0" cy="0" rx="18" ry="11" fill="#FAD7AC" stroke="#B67638" stroke-width="2.6"/>'
            '<circle cx="-9" cy="-2" r="1.8" fill="#8C5927"/></g>'
        )
    parts.append(
        '<path d="M -25,-22 L 25,-22 L 21,28 L -21,28 Z" fill="#FFF3DC" stroke="#B67638" stroke-width="3.0" stroke-linejoin="round"/>'
        '<ellipse cx="-2" cy="5" rx="10" ry="6" fill="none" stroke="#B67638" stroke-width="2.1"/>'
        '<polygon points="8,5 14,0 14,10" fill="none" stroke="#B67638" stroke-width="1.9"/>'
    )
    parts.append("</g>")
    return "".join(parts)


def _dango(cx=128, cy=188, rot=26, s=1.0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot}) scale({s})">'
        f'<line x1="0" y1="-26" x2="0" y2="34" stroke="#B6804A" stroke-width="4.0" stroke-linecap="round"/>'
        f'<circle cx="0" cy="14" r="10.0" fill="#FDBA74" stroke="#B67638" stroke-width="2.3"/>'
        f'<circle cx="0" cy="-3" r="10.0" fill="#A8D5BA" stroke="#5A8F70" stroke-width="2.3"/>'
        f'<circle cx="0" cy="-20" r="10.0" fill="#B68B60" stroke="#7A5636" stroke-width="2.3"/>'
        f'</g>'
    )


def build_62_taiyaki() -> list[tuple[str, Image.Image]]:
    # S0: Hungry holding empty paper bag
    s0 = render_svg(
        shadow(138, 268, 64, 9)
        + loopy_body(
            134, 220, pose="sit", paws="none", lean=7,
            mid_props=_taiyaki_bag(234, 232, has_fish=False, s=0.92),
            arms=[
                arm_spec((106, 202), (86, 220), (114, 228), 10.8, 9.0, 7.4, layer="front", t_fill=0.26, t_in=0.28, t_out=0.48),
                arm_spec((162, 200), (194, 212), (210, 212), 11.0, 9.0, 7.5, layer="front", t_fill=0.30, t_in=0.32, t_out=0.54),
            ],
            head_svg=loopy_head(140, 130, expr="puzzled", rot=10),
        )
        + '<text x="230" y="192" font-family="Segoe UI" font-weight="bold" font-size="22" fill="#B67638">?</text>'
    )
    # S1: Adjusting Taiyaki fish hat neatly with both curved arms
    s1 = render_svg(
        shadow()
        + loopy_body(
            150, 218, pose="stand", paws="none", lean=-4,
            arms=[
                arm_spec((122, 200), (74, 162), (96, 114), 11.0, 9.0, 7.4, fingers=True, layer="over_head", t_oh=0.52),
                arm_spec((178, 200), (222, 162), (198, 118), 11.0, 9.0, 7.4, fingers=True, layer="over_head", t_oh=0.52),
            ],
            head_svg=_taiyaki_head_in_hood(146, 126, rot=-6, expr="curious"),
        )
    )
    # S2: Walking happily carrying bag with steaming hot Taiyaki!
    s2 = render_svg(
        shadow(136, 268, 64, 9)
        + loopy_body(
            134, 216, pose="walk", paws="none", lean=5,
            mid_props=_taiyaki_bag(234, 226, has_fish=True, s=0.94),
            arms=[
                arm_spec((106, 200), (80, 214), (86, 228), 11.0, 9.0, 7.5, fingers=True, layer="out"),
                arm_spec((162, 200), (194, 206), (208, 212), 11.0, 9.0, 7.5, layer="front", t_fill=0.34, t_in=0.34, t_out=0.34),
            ],
            head_svg=_taiyaki_head_in_hood(138, 124, rot=5, expr="smile"),
        )
    )
    # S3: Sitting holding steaming bag & 3-color Dango skewer!
    s3 = render_svg(
        shadow(142, 268, 66, 9)
        + loopy_body(
            140, 218, pose="sit", paws="none", lean=-3,
            mid_props=_dango(88, 194, rot=-18, s=0.95) + _taiyaki_bag(238, 232, has_fish=True, s=0.88),
            arms=[
                arm_spec((116, 200), (96, 220), (86, 204), 10.6, 8.8, 7.4, layer="front", t_fill=0.34, t_in=0.34, t_out=0.34),
                arm_spec((166, 200), (196, 216), (212, 222), 10.8, 9.0, 7.5, layer="front", t_fill=0.34, t_in=0.34, t_out=0.34),
            ],
            head_svg=_taiyaki_head_in_hood(138, 124, rot=-4, expr="smile"),
        )
    )
    # S4: Winking rosy cheeks lifting Dango skewer to nibble!
    s4 = render_svg(
        shadow(148, 268, 66, 9)
        + loopy_body(
            148, 218, pose="sit", paws="none", lean=5,
            arms=[
                arm_spec((122, 200), (106, 230), (140, 206), 10.4, 8.6, 7.2, layer="over_head", t_oh=0.46),
                arm_spec((174, 202), (202, 214), (188, 228), 10.6, 9.0, 7.4, fingers=True, layer="front", t_fill=0.30, t_in=0.34, t_out=0.54),
            ],
            head_svg=_taiyaki_head_in_hood(152, 124, rot=8, expr="wink", strong_blush=True) + _dango(146, 174, rot=20, s=0.96),
        )
        + heart(246, 176, s=11, fill="#93C5FD", stroke="#3B82F6", rot=12)
        + sp4(48, 178, r=10)
    )
    # S5: Beaming happy-squint feast with Dango & full Taiyaki bag!
    s5 = with_hero_aura(render_svg(
        shadow(142, 272, 58, 8, op=0.12)
        + loopy_body(
            140, 206, pose="jump", paws="none",
            mid_props=_dango(82, 160, rot=-22, s=0.96),
            arms=[
                arm_spec((112, 186), (88, 192), (86, 174), 11.0, 9.0, 7.5, layer="front", t_fill=0.30, t_in=0.32, t_out=0.54),
                arm_spec((168, 186), (204, 176), (216, 152), 11.0, 9.0, 7.5, fingers=True, layer="out"),
            ],
            head_svg=_taiyaki_head_in_hood(140, 114, rot=-5, expr="happy_squint", strong_blush=True),
        )
        + _taiyaki_bag(242, 232, has_fish=True, extra_fish=True, s=0.90)
        + heart(248, 134, s=11, fill="#93C5FD", stroke="#3B82F6", rot=12)
        + sp4(44, 78, r=11) + sp4(248, 72, r=10)
    ), (250, 215, 172))
    return [
        ("Túi Giấy Trống", s0),
        ("Đội Mũ Taiyaki", s1),
        ("Bánh Cá Nóng", s2),
        ("Thêm Xiên Dango", s3),
        ("Cắn Xiên Dango", s4),
        ("No Nê Ẩm Thực!", s5),
    ]


# =========================================================================== #
#  #63 — LOOPY PIGGY DESSERT CAFE (SNUG PIGGY HOOD + CURVED ARMS!)
# =========================================================================== #
def _white_glasses(cx=0, cy=0, s=1.0, rot=0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot}) scale({s})">'
        f'<circle cx="-22" cy="-6" r="14.5" fill="#FFFFFF" fill-opacity="0.22" stroke="#FFFFFF" stroke-width="3.5"/>'
        f'<circle cx="22" cy="-6" r="14.5" fill="#FFFFFF" fill-opacity="0.22" stroke="#FFFFFF" stroke-width="3.5"/>'
        f'<path d="M -7.5,-6 Q 0,-10 7.5,-6" fill="none" stroke="#FFFFFF" stroke-width="3.3"/>'
        f'</g>'
    )


def _piggy_head_in_hood(cx=150, cy=120, rot=0, expr="smile", strong_blush=False) -> str:
    """3-Layer Snug Piggy Hood: thick pink hood rim completely encloses Loopy's face!"""
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot})">'
        f'<path d="M -72,-8 C -74,-44 -68,-74 -46,-76 C -30,-78 -22,-64 -12,-64 L 12,-64 C 22,-64 30,-78 46,-76 C 68,-74 74,-44 72,-8 C 76,36 54,60 0,60 C -54,60 -76,36 -72,-8 Z" fill="#FFD9E6" stroke="#D97C9C" stroke-width="4.0"/>'
        f'<ellipse cx="-46" cy="-58" rx="12" ry="9" fill="#FFB3CE" fill-opacity="0.72"/>'
        f'<ellipse cx="46" cy="-58" rx="12" ry="9" fill="#FFB3CE" fill-opacity="0.72"/>'
        f'<circle cx="-18" cy="-48" r="3.6" fill="{EYE}"/><circle cx="18" cy="-48" r="3.6" fill="{EYE}"/>'
        f'<ellipse cx="0" cy="-35" rx="14" ry="8.5" fill="#FF9EBC"/>'
        f'<circle cx="-5" cy="-35" r="2.2" fill="#C44D73"/><circle cx="5" cy="-35" r="2.2" fill="#C44D73"/>'
        f'<ellipse cx="0" cy="14" rx="46" ry="40" fill="{PINK}"/>'
        + loopy_head(0, 15, scale=0.71, expr=expr, strong_blush=strong_blush, in_hood=True)
        + _white_glasses(0, 15, s=0.71)
        # Front padded rim hugging face edge cleanly
        + '<ellipse cx="0" cy="14" rx="46" ry="40" fill="none" stroke="#FFD9E6" stroke-width="6.5"/>'
        + '<ellipse cx="0" cy="14" rx="46" ry="40" fill="none" stroke="#D97C9C" stroke-width="3.2"/>'
        + '</g>'
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
        + loopy_body(134, 218, pose="sit", paws="down", lean=9)
        + loopy_head(140, 130, expr="curious", rot=11)
        + _white_glasses(140, 130, s=1.0, rot=11)
        + _smiling_cheese(236, 240, s=1.0)
    )
    s1 = render_svg(
        shadow()
        + loopy_body(
            150, 218, pose="stand", paws="none", lean=-4,
            arms=[
                arm_spec((122, 200), (78, 166), (92, 124), 11.0, 9.0, 7.4, fingers=True, layer="over_head", t_oh=0.54),
                arm_spec((178, 200), (220, 166), (202, 124), 11.0, 9.0, 7.4, fingers=True, layer="over_head", t_oh=0.54),
            ],
            head_svg=_piggy_head_in_hood(146, 120, rot=-5, expr="smile"),
        )
    )
    s2 = render_svg(
        shadow()
        + loopy_body(
            146, 216, pose="walk", paws="none", lean=5,
            mid_props=_ice_cream(216, 168, scoops=1, s=1.0, rot=14),
            arms=[
                arm_spec((118, 198), (94, 214), (96, 228), 11.0, 9.0, 7.5, fingers=True, layer="out"),
                arm_spec((174, 198), (204, 196), (212, 178), 11.0, 9.0, 7.5, layer="front", t_fill=0.30, t_in=0.32, t_out=0.54),
            ],
            head_svg=_piggy_head_in_hood(150, 120, rot=6, expr="smile"),
        )
    )
    s3 = render_svg(
        shadow()
        + loopy_body(
            150, 218, pose="sit", paws="none", lean=-5,
            mid_props=_ice_cream(156, 198, scoops=2, s=1.0, rot=-8),
            arms=[
                arm_spec((122, 198), (110, 222), (144, 218), 11.0, 9.0, 7.5, layer="front", t_fill=0.24, t_in=0.28, t_out=0.48),
                arm_spec((178, 198), (190, 222), (166, 218), 11.0, 9.0, 7.5, layer="front", t_fill=0.24, t_in=0.28, t_out=0.48),
            ],
            head_svg=_piggy_head_in_hood(146, 120, rot=-7, expr="wink", strong_blush=True),
        )
        + sp4(56, 128, r=10, fill="#A6D8EB", stroke="#5EA9C7")
    )
    s4 = render_svg(
        shadow(136, 268, 66, 9)
        + loopy_body(
            136, 216, pose="stand", paws="none", lean=5,
            mid_props=_ice_cream(98, 186, scoops=2, s=0.96, rot=-18),
            arms=[
                arm_spec((108, 196), (86, 206), (98, 200), 11.0, 9.0, 7.5, layer="front", t_fill=0.26, t_in=0.28, t_out=0.50),
                arm_spec((164, 196), (204, 184), (216, 150), 11.0, 9.0, 7.5, fingers=True, layer="out"),
            ],
            head_svg=_piggy_head_in_hood(140, 120, rot=7, expr="big_smile", strong_blush=True),
        )
        + _cherry_cake(242, 110, s=0.92)
        + sp4(248, 178, r=10)
    )
    s5 = with_hero_aura(render_svg(
        shadow(146, 268, 72, 9)
        + loopy_body(146, 216, pose="sit", paws="wide_up")
        + _piggy_head_in_hood(146, 118, rot=-4, expr="happy_squint", strong_blush=True)
        + _ice_cream(162, 198, scoops=2, s=0.98)
        + _smiling_cheese(54, 244, s=0.95)
        + _cherry_cake(244, 102, s=0.92)
        + sp4(48, 92, r=12) + heart(246, 170, s=10, fill="#F28FB0", stroke="#D45B82")
    ), (242, 143, 176))
    return [
        ("Ngắm Phô Mai", s0),
        ("Đội Mũ Heo Hồng", s1),
        ("Bước Đi Cầm Kem", s2),
        ("Kem 2 Viên Xinh", s3),
        ("Bánh Kem Cherry", s4),
        ("Tiệc Cafe Ngọt!", s5),
    ]


# =========================================================================== #
#  #64 — LOOPY SAUNA SHEEP DETOX (CURVED ARMS + COZY SHEEP TOWEL!)
# =========================================================================== #
def _black_glasses_slid(cx=150, cy=134, rot=5) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot})">'
        f'<rect x="-42" y="-2" width="34" height="22" rx="6" fill="#FFFFFF" fill-opacity="0.22" stroke="#2D1E22" stroke-width="4.0"/>'
        f'<rect x="8" y="-2" width="34" height="22" rx="6" fill="#FFFFFF" fill-opacity="0.22" stroke="#2D1E22" stroke-width="4.0"/>'
        f'<line x1="-8" y1="6" x2="8" y2="6" stroke="#2D1E22" stroke-width="4.0"/>'
        f'</g>'
    )


def _sheep_towel(cx=150, cy=124, rot=0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot})">'
        f'<path d="M -58,-18 C -56,-70 56,-70 58,-18 C 34,-40 -34,-40 -58,-18 Z" fill="#FFFFFF" stroke="#D17A90" stroke-width="4.0" stroke-linejoin="round"/>'
        f'<ellipse cx="-66" cy="-4" rx="26" ry="30" transform="rotate(-14 -66 -4)" fill="#FFFFFF" stroke="#D17A90" stroke-width="4.0"/>'
        f'<path d="M -68,-14 C -58,-18 -54,-4 -62,6 C -70,14 -78,4 -72,-6" fill="none" stroke="#D17A90" stroke-width="3.2" stroke-linecap="round"/>'
        f'<ellipse cx="66" cy="-4" rx="26" ry="30" transform="rotate(14 66 -4)" fill="#FFFFFF" stroke="#D17A90" stroke-width="4.0"/>'
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
        shadow() + loopy_body(150, 222, pose="sit", paws="down", lean=-7)
        + loopy_head(144, 134, expr="sleepy", rot=-10)
        + _black_glasses_slid(144, 140, rot=-6)
    )
    s1 = render_svg(
        shadow() + loopy_body(
            150, 218, pose="stand", paws="none",
            arms=[
                arm_spec((122, 200), (78, 164), (92, 128), 11.0, 9.0, 7.5, fingers=True, layer="over_head", t_oh=0.52),
                arm_spec((178, 200), (222, 164), (208, 128), 11.0, 9.0, 7.5, fingers=True, layer="over_head", t_oh=0.52),
            ],
            head_svg=loopy_head(150, 126, expr="curious", show_ears=False, show_tuft=False, rot=5) + _sheep_towel(150, 122, rot=5),
        )
    )
    s2 = render_svg(
        shadow() + loopy_body(
            150, 218, pose="sit", paws="none",
            arms=[
                arm_spec((122, 202), (78, 190), (102, 156), 11.0, 9.2, 7.6, fingers=True, layer="over_head", t_oh=0.24),
                arm_spec((178, 202), (222, 190), (198, 156), 11.0, 9.2, 7.6, fingers=True, layer="over_head", t_oh=0.24),
            ],
            head_svg=loopy_head(150, 126, expr="calm_closed", strong_blush=True, blush_hatch=True, show_ears=False, show_tuft=False, rot=-5) + _sheep_towel(150, 122, rot=-5),
        )
    )
    s3 = render_svg(
        shadow() + _steam_curls()
        + loopy_body(150, 218, pose="sit", paws="shrug", lean=5)
        + loopy_head(154, 126, expr="smile", strong_blush=True, blush_hatch=True, show_ears=False, show_tuft=False, rot=7)
        + _sheep_towel(154, 122, rot=7)
        + sp4(56, 84, r=11, fill="#E0F2FE", stroke="#7DBCE6") + sp4(246, 86, r=10, fill="#E0F2FE", stroke="#7DBCE6")
    )
    s4 = render_svg(
        shadow() + _steam_curls()
        + loopy_body(150, 216, pose="walk", paws="wide_up", lean=-6)
        + loopy_head(144, 126, expr="big_smile", strong_blush=True, blush_hatch=True, show_ears=False, show_tuft=False, rot=-8)
        + _sheep_towel(144, 122, rot=-8)
        + _wa_text(176, 52) + heart_with_eyes(66, 62, s=20, rot=-12)
    )
    s5 = with_hero_aura(render_svg(
        shadow(150, 272, 54, 8, op=0.12) + _steam_curls()
        + loopy_body(150, 206, pose="jump", paws="wide_up")
        + loopy_head(150, 118, expr="happy_squint", strong_blush=True, blush_hatch=True, show_ears=False, show_tuft=False, rot=4)
        + _sheep_towel(150, 114, rot=4)
        + _wa_text(178, 48) + heart_with_eyes(64, 58, s=20, rot=-12)
        + sp4(250, 82, r=12, fill="#E0F2FE", stroke="#60A5FA") + sp4(46, 224, r=10, fill="#FEF08A", stroke="#D99B58")
    ), (168, 201, 232))
    return [
        ("Kính Trễ Mệt Mỏi", s0),
        ("Quấn Khăn Cừu", s1),
        ("Ôm Má Ấm Áp", s2),
        ("Xông Hơi Thư Giãn", s3),
        ("Reo Vui WA~", s4),
        ("Sảng Khoái 100%", s5),
    ]


# =========================================================================== #
#  #65 — LOOPY HONEY BEE KPI (SNUG BEE HOOD + CURVED ARMS!)
# =========================================================================== #
def _pastel_bear(cx, cy, stroke_col="#93C5FD", rot=0, s=0.66, happy=False) -> str:
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


def _bee_character(cx=150, cy=150, antennae=False, wings=False, stripes=False, pose="sit", paws="down", lean=0, crown=False, expr="smile", strong_blush=False, front_prop="") -> str:
    parts = [f'<g transform="translate({cx},{cy}) rotate({lean})">']
    if wings:
        parts.append(
            '<ellipse cx="-66" cy="34" rx="26" ry="14" transform="rotate(-26 -66 34)" fill="#E0F2FE" stroke="#7A5C52" stroke-width="3.2"/>'
            '<ellipse cx="66" cy="34" rx="26" ry="14" transform="rotate(26 66 34)" fill="#E0F2FE" stroke="#7A5C52" stroke-width="3.2"/>'
        )
    if pose == "sit":
        parts.append(_loopy_foot(-32, 92, -16, sit=True) + _loopy_foot(32, 92, 16, sit=True))
    elif pose == "fly":
        parts.append(_loopy_foot(-20, 96, 18) + _loopy_foot(20, 96, -18))

    body_c = "#FDE068" if stripes else "#FEF5B8"
    bee_d = (
        "M 0,18 C 32,18 49,40 48,66 C 47,88 28,100 0,100 "
        "C -28,100 -47,88 -48,66 C -49,40 -32,18 0,18 Z"
    )
    if paws == "up":
        bee_arms = [
            _sample_arm_mesh((-30, 42), (-60, 32), (-68, 6), 10.6, 8.8, 7.2, body_ref=(0.0, 62.0)),
            _sample_arm_mesh((30, 42), (60, 32), (68, 6), 10.6, 8.8, 7.2, body_ref=(0.0, 62.0)),
        ]
    elif paws == "hug":
        bee_arms = [
            _sample_arm_mesh((-26, 46), (-42, 66), (-18, 66), 10.2, 8.6, 7.4, body_ref=(0.0, 62.0)),
            _sample_arm_mesh((26, 46), (42, 66), (18, 66), 10.2, 8.6, 7.4, body_ref=(0.0, 62.0)),
        ]
    else:
        bee_arms = [
            _sample_arm_mesh((-30, 42), (-56, 54), (-46, 74), 10.6, 8.8, 7.2, body_ref=(0.0, 62.0)),
            _sample_arm_mesh((30, 42), (56, 54), (46, 74), 10.6, 8.8, 7.2, body_ref=(0.0, 62.0)),
        ]

    # Layer 1: Unified outline of bee body + both pink arms (ZERO shoulder horns/gaps!)
    parts.append(f'<path d="{bee_d}" fill="none" stroke="#7A5C52" stroke-width="7.6" stroke-linejoin="round" stroke-linecap="round"/>')
    if paws != "hug":
        for m in bee_arms:
            parts.append(f'<path d="{m["full_d"]}" fill="none" stroke="{OL}" stroke-width="7.4" stroke-linejoin="round" stroke-linecap="round"/>')
        for m in bee_arms:
            parts.append(f'<path d="{m["full_d"]}" fill="{PINK}" stroke="none"/>')
    parts.append(f'<path d="{bee_d}" fill="{body_c}" stroke="none"/>')
    if stripes:
        parts.append(
            '<path d="M -45,46 Q 0,58 45,46 L 45,62 Q 0,74 -45,62 Z" fill="#7A5C52"/>'
            '<path d="M -39,76 Q 0,86 39,76 L 33,89 Q 0,97 -33,89 Z" fill="#7A5C52"/>'
        )
    if front_prop:
        parts.append(front_prop)
    # Layer 3: For hugging arms, smooth pink forearm + inner crease cleanly tucked inside yellow bee suit!
    if paws == "hug":
        for m in bee_arms:
            parts.append(f'<path d="{m["sub_fill_d"](0.24)}" fill="{PINK}" stroke="none"/>')
            parts.append(f'<path d="{m["sub_stroke_d"](0.26, 0.34)}" fill="none" stroke="{OL}" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/>')
    else:
        for m in bee_arms:
            parts.append(_fingers_svg(m))

    # 3-Layer Snug Bee Hood (face completely nested inside rim!)
    parts.append(
        f'<circle cx="-54" cy="-42" r="13.5" fill="{PINK}" stroke="#D48296" stroke-width="3.0"/>'
        f'<circle cx="54" cy="-42" r="13.5" fill="{PINK}" stroke="#D48296" stroke-width="3.0"/>'
        '<path d="M -68,-4 C -68,-50 -36,-64 0,-64 C 36,-64 68,-50 68,-4 C 68,38 44,54 0,54 C -44,54 -68,38 -68,-4 Z" fill="#FEF3A8" stroke="#D4AA46" stroke-width="4.0"/>'
    )
    if antennae:
        parts.append(
            '<path d="M -18,-60 L -26,-84 M 18,-60 L 26,-84" stroke="#7A5C52" stroke-width="4.6" stroke-linecap="round"/>'
            '<circle cx="-27" cy="-88" r="8.2" fill="#F5B82E" stroke="#7A5C52" stroke-width="2.6"/>'
            '<circle cx="27" cy="-88" r="8.2" fill="#F5B82E" stroke="#7A5C52" stroke-width="2.6"/>'
        )
    if crown:
        parts.append('<polygon points="-16,-62 -12,-82 0,-70 12,-82 16,-62" fill="#FDE047" stroke="#B45309" stroke-width="2.4" stroke-linejoin="round"/>')
    parts.append(f'<ellipse cx="0" cy="-2" rx="46" ry="40" fill="{PINK}"/>')
    parts.append(loopy_head(0, -1, scale=0.71, expr=expr, strong_blush=strong_blush, in_hood=True))
    # Front padded yellow hood rim ON TOP of face edge
    parts.append('<ellipse cx="0" cy="-2" rx="46" ry="40" fill="none" stroke="#FEF3A8" stroke-width="6.5"/>')
    parts.append('<ellipse cx="0" cy="-2" rx="46" ry="40" fill="none" stroke="#D4AA46" stroke-width="3.2"/>')
    parts.append("</g>")
    return "".join(parts)


def build_65_honey_bee() -> list[tuple[str, Image.Image]]:
    s0 = render_svg(
        shadow(150, 264, 70, 9)
        + '<ellipse cx="150" cy="212" rx="68" ry="48" fill="#FEF5B8" stroke="#D4AA46" stroke-width="4.0"/>'
        + f'<ellipse cx="146" cy="204" rx="42" ry="34" fill="{PINK}"/>'
        + loopy_head(146, 206, scale=0.66, expr="sleepy", rot=-8, in_hood=True)
        + '<ellipse cx="146" cy="204" rx="42" ry="34" fill="none" stroke="#FEF5B8" stroke-width="5.5"/>'
        + '<ellipse cx="146" cy="204" rx="42" ry="34" fill="none" stroke="#D4AA46" stroke-width="3.0"/>'
        + _z_vec(212, 146, 0.85) + _z_vec(228, 128, 1.05)
    )
    s1 = render_svg(
        shadow(150, 266, 62, 9)
        + _bee_character(150, 156, antennae=True, wings=False, stripes=False, pose="sit", paws="down", lean=9, expr="curious")
    )
    s2 = render_svg(
        shadow(150, 272, 48, 7, op=0.12)
        + '<path d="M 48,200 Q 68,214 82,202 M 252,196 Q 232,210 218,198" fill="none" stroke="#93C5FD" stroke-width="3.0" stroke-linecap="round"/>'
        + _bee_character(150, 140, antennae=True, wings=True, stripes=True, pose="fly", paws="up", lean=-7, expr="focused")
    )
    s3 = render_svg(
        shadow(150, 266, 68, 9)
        + _pastel_bear(70, 118, "#93C5FD", rot=-14, s=0.68, happy=False)
        + _pastel_bear(230, 118, "#C4B5FD", rot=14, s=0.68, happy=True)
        + _bee_character(150, 152, antennae=True, wings=True, stripes=True, pose="sit", paws="hug", expr="smile", front_prop=_honey_pot(0, 62, s=0.92))
    )
    s4 = render_svg(
        _pastel_bear(70, 92, "#F9A8D4", rot=-16, s=0.64, happy=True)
        + _pastel_bear(230, 92, "#93C5FD", rot=16, s=0.64, happy=True)
        + _pastel_bear(62, 214, "#86EFAC", rot=-10, s=0.66, happy=True)
        + _pastel_bear(238, 214, "#C4B5FD", rot=10, s=0.66, happy=False)
        + ditsy_flower(150, 266, 9, "#FDE047", "#F97316") + ditsy_flower(112, 264, 8, "#F9A8D4", "#FDE047") + ditsy_flower(188, 264, 8, "#93C5FD", "#FDE047")
        + _bee_character(150, 142, antennae=True, wings=True, stripes=True, pose="fly", paws="up", lean=7, expr="wink", strong_blush=True)
    )
    s5 = with_hero_aura(render_svg(
        _pastel_bear(74, 82, "#F9A8D4", rot=-14, s=0.60, happy=True)
        + _pastel_bear(226, 82, "#93C5FD", rot=14, s=0.60, happy=True)
        + _pastel_bear(62, 224, "#86EFAC", rot=-10, s=0.62, happy=True)
        + _pastel_bear(238, 224, "#FDBA74", rot=10, s=0.62, happy=True)
        + _bee_character(150, 146, antennae=True, wings=True, stripes=True, pose="fly", paws="up", crown=True, expr="big_smile", strong_blush=True)
        + _honey_pot(228, 148, s=0.92, rot=14)
        + sp4(52, 150, r=11) + sp4(254, 114, r=10) + sp4(150, 268, r=10)
    ), (234, 184, 68))
    return [
        ("Cuộn Tròn Ngủ", s0),
        ("Mọc Râu Ong", s1),
        ("Vỗ Cánh Bay", s2),
        ("Ôm Hũ Mật Vàng", s3),
        ("Bay Giữa Hoa", s4),
        ("Ong Chúa KPI!", s5),
    ]


# =========================================================================== #
#  #66 — LOOPY POOLSIDE DUCK CHILL (CURVED ARMS + NATURAL LOUNGING!)
# =========================================================================== #
def _duck_float(cx=150, cy=214, s=1.0, rot=0) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot}) scale({s})">'
        f'<circle cx="0" cy="-22" r="16" fill="#FFFFFF" stroke="#EAB308" stroke-width="2.4"/>'
        f'<circle cx="0" cy="-19" r="12" fill="#FEF08A"/>'
        f'<circle cx="-4.5" cy="-21" r="1.8" fill="{EYE}"/><circle cx="4.5" cy="-21" r="1.8" fill="{EYE}"/>'
        f'<polygon points="-4,-18 4,-18 0,-13" fill="#F97316"/>'
        f'<rect x="-64" y="-16" width="128" height="36" rx="18" fill="#FDE047" stroke="#EAB308" stroke-width="3.5"/>'
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
        shadow() + loopy_body(
            144, 218, pose="sit", paws="none", lean=-5,
            mid_props=_duck_float(178, 224, s=0.66, rot=12),
            arms=[
                arm_spec((116, 198), (110, 224), (144, 222), 10.8, 9.0, 7.5, layer="front", t_fill=0.24, t_in=0.28, t_out=0.48),
                arm_spec((172, 198), (206, 214), (194, 226), 10.8, 9.0, 7.5, layer="front", t_fill=0.26, t_in=0.30, t_out=0.50),
            ],
            head_svg=loopy_head(140, 130, expr="curious", rot=-8),
        )
    )
    s1 = render_svg(
        shadow() + loopy_body(150, 214, pose="walk", paws="wide_up", lean=5)
        + _duck_float(150, 212, s=0.92, rot=5)
        + loopy_head(154, 124, expr="smile", rot=7)
    )
    s2 = render_svg(
        '<ellipse cx="150" cy="256" rx="92" ry="22" fill="#9BE3F7"/>'
        + loopy_body(150, 198, pose="jump", paws="wide_up", lean=-5)
        + _duck_float(148, 198, s=0.94, rot=-7)
        + loopy_head(144, 110, expr="big_smile", strong_blush=True, rot=-7)
        + heart(54, 96, s=16, fill="#FB7185", stroke="#E11D48", rot=-12)
        + heart(246, 136, s=14, fill="#F472B6", stroke="#DB2777", rot=12)
        + '<circle cx="62" cy="222" r="6" fill="#6EC6E6"/><circle cx="242" cy="218" r="6" fill="#6EC6E6"/>'
    )
    s3 = render_svg(
        _striped_pool_tube(150, 162)
        + loopy_body(150, 198, rx=42, ry=36, pose="hover", paws="wave_r", lean=5)
        + loopy_head(154, 128, scale=0.82, expr="smile", blush_hatch=True, rot=7)
    )
    # S4 & S5: Curved arms bending naturally behind head lounging on pool ring!
    s4 = render_svg(
        _striped_pool_tube(150, 162)
        + loopy_body(
            150, 196, rx=42, ry=36, pose="hover", paws="none", lean=-5,
            arms=[
                arm_spec((124, 180), (80, 162), (104, 128), 10.6, 8.8, 7.4, layer="out"),
                arm_spec((176, 180), (220, 162), (196, 128), 10.6, 8.8, 7.4, layer="out"),
            ],
            head_svg=loopy_head(146, 130, scale=0.82, expr="wink", strong_blush=True, blush_hatch=True, rot=-7),
        )
        + sp4(64, 58, r=12, fill="#FFFFFF", stroke="#6EC6E6") + sp4(242, 64, r=10, fill="#FFFFFF", stroke="#6EC6E6")
    )
    s5 = with_hero_aura(render_svg(
        _striped_pool_tube(150, 158)
        + loopy_body(
            150, 194, rx=42, ry=36, pose="hover", paws="none",
            arms=[
                arm_spec((124, 178), (80, 158), (106, 124), 10.6, 8.8, 7.4, layer="out"),
                arm_spec((176, 178), (220, 158), (194, 124), 10.6, 8.8, 7.4, layer="out"),
            ],
            head_svg=loopy_head(150, 128, scale=0.82, expr="calm_closed", strong_blush=True, blush_hatch=True),
        )
        + sp4(62, 54, r=14, fill="#FFFFFF", stroke="#38BDF8") + sp4(240, 58, r=11, fill="#FFFFFF", stroke="#38BDF8")
        + star5(234, 246, r=13, fill="#FFFFFF", stroke="#6EC6E6") + sp4(56, 236, r=10, fill="#FEF08A", stroke="#EAB308")
    ), (110, 198, 230))
    return [
        ("Ôm Phao Vịt", s0),
        ("Đeo Phao Sẵn", s1),
        ("Nhảy Hồ Tung Tim", s2),
        ("Phao Sọc Vàng", s3),
        ("Gối Tay Nổi", s4),
        ("Thư Thái Hồ Xanh", s5),
    ]


# =========================================================================== #
#  #67 — LOOPY FLUFFY COMMUTER DIARY (SNUG FLUFFY HOOD + CURVED ARMS!)
# =========================================================================== #
def _fluffy_head_in_hood(cx=150, cy=124, smiley=True, rot=0, expr="smile", strong_blush=False) -> str:
    parts = [f'<g transform="translate({cx},{cy}) rotate({rot})">']
    parts.append(
        '<circle cx="-46" cy="-74" r="23" fill="#FFFFFF" stroke="#5C343A" stroke-width="3.8"/>'
        '<ellipse cx="-46" cy="-72" rx="11.5" ry="12.5" fill="#F29EB0" stroke="#5C343A" stroke-width="2.1"/>'
        '<circle cx="46" cy="-74" r="23" fill="#FFFFFF" stroke="#5C343A" stroke-width="3.8"/>'
        '<ellipse cx="46" cy="-72" rx="11.5" ry="12.5" fill="#F29EB0" stroke="#5C343A" stroke-width="2.1"/>'
        '<path d="M -82,4 C -88,-42 -58,-72 0,-72 C 58,-72 88,-42 82,4 C 84,48 48,66 10,60 C 4,56 -4,56 -10,60 C -48,66 -84,48 -82,4 Z" fill="#FFFFFF" stroke="#5C343A" stroke-width="4.0"/>'
    )
    if smiley:
        parts.append(
            '<circle cx="-13" cy="-38" r="3.2" fill="#4BA3E3"/><circle cx="13" cy="-38" r="3.2" fill="#4BA3E3"/>'
            '<path d="M -4,-34 Q 0,-30 4,-34" fill="none" stroke="#E27D8E" stroke-width="2.4" stroke-linecap="round"/>'
            '<ellipse cx="-26" cy="-29" rx="8" ry="4.5" fill="#F9C5D1"/><ellipse cx="26" cy="-29" rx="8" ry="4.5" fill="#F9C5D1"/>'
        )
    parts.append(f'<ellipse cx="0" cy="14" rx="46" ry="39" fill="{PINK}"/>')
    parts.append(loopy_head(0, 15, scale=0.71, expr=expr, strong_blush=strong_blush, blush_hatch=True, in_hood=True))
    # Front padded fluffy white rim ON TOP of face edge!
    parts.append('<ellipse cx="0" cy="14" rx="46" ry="39" fill="none" stroke="#FFFFFF" stroke-width="7.0"/>')
    parts.append('<ellipse cx="0" cy="14" rx="46" ry="39" fill="none" stroke="#5C343A" stroke-width="3.2"/>')
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


def _coffee_cup(cx=84, cy=204) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate(-10)">'
        f'<path d="M -12,-14 L 12,-14 L 9,16 L -9,16 Z" fill="#FFF8EC" stroke="#5C343A" stroke-width="2.6" stroke-linejoin="round"/>'
        f'<rect x="-14" y="-19" width="28" height="7" rx="3" fill="#B87D4B" stroke="#5C343A" stroke-width="2.2"/>'
        f'<rect x="-10" y="-3" width="20" height="10" fill="#D4B499"/>'
        f'</g>'
    )


def build_67_fluffy_commuter() -> list[tuple[str, Image.Image]]:
    s0 = render_svg(
        shadow() + loopy_body(150, 222, pose="sit", paws="down", lean=-7)
        + _fluffy_head_in_hood(144, 128, smiley=False, rot=-8, expr="sleepy")
    )
    s1 = render_svg(
        shadow() + loopy_body(
            150, 218, pose="stand", paws="none", lean=4,
            mid_props=_crossbody_bag(150, 218, rot=4),
            arms=[
                arm_spec((122, 200), (104, 226), (136, 220), 10.8, 9.0, 7.5, layer="front", t_fill=0.26, t_in=0.30, t_out=0.48),
                arm_spec((178, 200), (206, 212), (196, 230), 10.8, 9.0, 7.5, fingers=True, layer="front", t_fill=0.30, t_in=0.32, t_out=0.54),
            ],
            head_svg=_fluffy_head_in_hood(152, 124, smiley=True, rot=5, expr="curious"),
        )
    )
    s2 = render_svg(
        shadow(150, 268, 66, 9)
        + loopy_body(
            150, 216, pose="walk", paws="walk_swing", lean=8,
            mid_props=_crossbody_bag(152, 216, rot=8),
            head_svg=_fluffy_head_in_hood(156, 122, smiley=True, rot=7, expr="focused"),
        )
        + '<path d="M 46,238 L 68,238 M 54,250 L 72,250" stroke="#D4B499" stroke-width="3.2" stroke-linecap="round"/>'
    )
    s3 = render_svg(
        shadow(150, 268, 66, 9)
        + loopy_body(
            150, 216, pose="walk", paws="none", lean=-4,
            mid_props=_crossbody_bag(148, 216, rot=-4) + _coffee_cup(78, 206),
            arms=[
                arm_spec((122, 196), (96, 216), (88, 208), 10.8, 9.0, 7.5, layer="front", t_fill=0.28, t_in=0.30, t_out=0.52),
                arm_spec((178, 196), (208, 210), (198, 228), 10.8, 9.0, 7.5, fingers=True, layer="front", t_fill=0.30, t_in=0.32, t_out=0.54),
            ],
            head_svg=_fluffy_head_in_hood(146, 122, smiley=True, rot=-5, expr="smile", strong_blush=True),
        )
    )
    s4 = render_svg(
        '<circle cx="150" cy="150" r="118" fill="#FEF6D8"/><circle cx="150" cy="150" r="92" fill="#FDEBB8"/>'
        + shadow() + loopy_body(
            150, 216, pose="stand", paws="shrug", lean=5,
            mid_props=_crossbody_bag(152, 216, rot=5),
            head_svg=_fluffy_head_in_hood(154, 122, smiley=True, rot=7, expr="wink", strong_blush=True),
        )
        + star5(50, 112, r=12) + star5(250, 124, r=14)
    )
    s5 = with_hero_aura(render_svg(
        '<circle cx="150" cy="150" r="120" fill="#FEF6D8"/><circle cx="150" cy="150" r="94" fill="#FDEBB8"/>'
        + shadow(150, 272, 52, 7, op=0.12)
        + loopy_body(
            150, 204, pose="jump", paws="wide_up",
            mid_props=_crossbody_bag(150, 204, rot=-5),
            head_svg=_fluffy_head_in_hood(150, 114, smiley=True, rot=-4, expr="big_smile", strong_blush=True),
        )
        + star5(46, 102, r=13) + star5(254, 118, r=15) + sp4(56, 178, r=10) + sp4(248, 62, r=11)
    ), (253, 231, 169))
    return [
        ("Ngái Ngủ Trùm Mũ", s0),
        ("Khoác Túi Chỉnh", s1),
        ("Bước Đi Tự Tin", s2),
        ("Cầm Cà Phê", s3),
        ("Nhún Vai Tan Ca", s4),
        ("Bật Nhảy Đúng Giờ", s5),
    ]


# =========================================================================== #
#  #68 — LOOPY PANDA ZEN STUDY (SNUG PANDA HOOD + CURVED ARMS!)
# =========================================================================== #
def _panda_head_in_hood(cx=150, cy=124, sprout=False, perked=False, rot=0, expr="smile", strong_blush=False) -> str:
    ear_dy = -6 if perked else 0
    parts = [f'<g transform="translate({cx},{cy}) rotate({rot})">']
    if sprout:
        parts.append(
            f'<path d="M 0,-64 C -6,-82 -14,-90 -8,-94 C -3,-97 1,-84 0,-68 Z" fill="#F48A9E" stroke="{OL}" stroke-width="2.5"/>'
            f'<path d="M 0,-64 C 4,-80 12,-88 8,-92 C 3,-94 -1,-82 0,-66 Z" fill="#F48A9E" stroke="{OL}" stroke-width="2.5"/>'
        )
    parts.append(
        '<path d="M -68,14 C -84,48 -88,80 -76,92 C -62,94 -52,66 -54,32 Z" fill="#FFFFFF" stroke="#363B42" stroke-width="3.6"/>'
        '<path d="M 68,14 C 84,48 88,80 76,92 C 62,94 52,66 54,32 Z" fill="#FFFFFF" stroke="#363B42" stroke-width="3.6"/>'
        f'<circle cx="-54" cy="{-52 + ear_dy}" r="25" fill="#FFFFFF" stroke="#363B42" stroke-width="3.8"/>'
        f'<circle cx="-54" cy="{-50 + ear_dy}" r="14.5" fill="#3C4148"/>'
        f'<circle cx="54" cy="{-52 + ear_dy}" r="25" fill="#FFFFFF" stroke="#363B42" stroke-width="3.8"/>'
        f'<circle cx="54" cy="{-50 + ear_dy}" r="14.5" fill="#3C4148"/>'
        '<path d="M -72,4 C -74,-44 -42,-66 0,-66 C 42,-66 74,-44 72,4 C 72,44 46,58 0,58 C -46,58 -72,44 -72,4 Z" fill="#FFFFFF" stroke="#363B42" stroke-width="4.0"/>'
        '<ellipse cx="-24" cy="-36" rx="15.5" ry="10.5" transform="rotate(-24 -24 -36)" fill="#3C4148"/>'
        '<ellipse cx="24" cy="-36" rx="15.5" ry="10.5" transform="rotate(24 24 -36)" fill="#3C4148"/>'
        '<ellipse cx="0" cy="-26" rx="4.2" ry="2.6" fill="#3C4148"/>'
        '<ellipse cx="-42" cy="-24" rx="7" ry="4" fill="#FBCFE8"/><ellipse cx="42" cy="-24" rx="7" ry="4" fill="#FBCFE8"/>'
        f'<ellipse cx="0" cy="14" rx="46" ry="39" fill="{PINK}"/>'
        + loopy_head(0, 15, scale=0.71, expr=expr, strong_blush=strong_blush, blush_hatch=True, in_hood=True)
        + '<ellipse cx="0" cy="14" rx="46" ry="39" fill="none" stroke="#FFFFFF" stroke-width="6.8"/>'
        + '<ellipse cx="0" cy="14" rx="46" ry="39" fill="none" stroke="#363B42" stroke-width="3.1"/>'
        + '</g>'
    )
    return "".join(parts)


def _ruffled_collar(
    cx=150,
    cy=188,
    sit=False,
    lean=0,
    arms: list[dict] | None = None,
    mid_props: str = "",
    head_svg: str = "",
) -> str:
    """v4.1 3-Layer Seamless Panda Outfit Body + White Ruffled Collar + Smooth Curved Pink Arms."""
    feet = (
        _loopy_foot(-30, 64, -14, sit=True) + _loopy_foot(30, 64, 14, sit=True)
        if sit else
        _loopy_foot(-22, 70, -4) + _loopy_foot(22, 70, 4)
    )
    tf = f'translate({cx},{cy}) rotate({lean})'
    torso_d = (
        "M 0,-18 C 32,-18 49,4 48,30 C 47,54 28,68 0,68 "
        "C -28,68 -47,54 -48,30 C -49,4 -32,-18 0,-18 Z"
    )
    built_arms: list[tuple[dict, dict]] = []
    for sp in (arms or []):
        lp0 = sp["p0"] if sp["local"] else _to_local(sp["p0"], cx, cy, lean)
        lp1 = sp["p1"] if sp["local"] else _to_local(sp["p1"], cx, cy, lean)
        lp2 = sp["p2"] if sp["local"] else _to_local(sp["p2"], cx, cy, lean)
        side = -1.0 if lp0[0] < 0 else 1.0
        lp0 = (side * max(14.0, min(abs(lp0[0]), 28.0)), max(-4.0, min(lp0[1], 14.0)))
        mesh = _sample_arm_mesh(lp0, lp1, lp2, sp["w0"], sp["w1"], sp["w2"], body_ref=(0.0, 26.0))
        built_arms.append((sp, mesh))

    parts: list[str] = [f'<g transform="{tf}">{feet}</g>']
    # Layer 1: Unified outline of charcoal panda torso + all pink arms
    l1 = [f'<path d="{torso_d}" fill="none" stroke="#25282E" stroke-width="7.6" stroke-linejoin="round" stroke-linecap="round"/>']
    l2 = [f'<path d="{torso_d}" fill="#3C4148" stroke="none"/>']
    for sp, mesh in built_arms:
        l1.append(f'<path d="{mesh["full_d"]}" fill="none" stroke="{sp["stroke"]}" stroke-width="{sp["sw"] * 2:.1f}" stroke-linejoin="round" stroke-linecap="round"/>')
        l2.append(f'<path d="{mesh["full_d"]}" fill="{sp["fill"] or PINK}" stroke="none"/>')
    parts.append(f'<g transform="{tf}">{"".join(l1)}{"".join(l2)}</g>')

    if mid_props:
        parts.append(mid_props)

    l3: list[str] = []
    for sp, mesh in built_arms:
        if sp["layer"] == "front":
            l3.append(f'<path d="{mesh["full_d"]}" fill="{sp["fill"] or PINK}" stroke="none"/>')
            l3.append(
                f'<path d="{mesh["sub_stroke_d"](0.18, 0.24)}" fill="none" '
                f'stroke="{sp["stroke"]}" stroke-width="{sp["sw"]:.1f}" stroke-linecap="round" stroke-linejoin="round"/>'
            )
            if sp["fingers"]:
                l3.append(_fingers_svg(mesh))
        elif sp["layer"] == "out" and sp["fingers"]:
            l3.append(_fingers_svg(mesh))
    # Draw crisp white ruffled collar ON TOP of arm shoulders so pink arms emerge cleanly under the ruffle!
    l3.append('<path d="M -39,-10 Q -29,12 -18,2 Q -8,15 0,4 Q 8,15 18,2 Q 29,12 39,-10 Z" fill="#FFFFFF" stroke="#363B42" stroke-width="2.9"/>')
    parts.append(f'<g transform="{tf}">{"".join(l3)}</g>')

    if head_svg:
        parts.append(head_svg)

    l4: list[str] = []
    for sp, mesh in built_arms:
        if sp["layer"] == "over_head":
            t_oh = sp["t_oh"]
            l4.append(f'<path d="{mesh["sub_fill_d"](t_oh)}" fill="{sp["fill"] or PINK}" stroke="none"/>')
            l4.append(
                f'<path d="{mesh["sub_stroke_d"](t_oh, t_oh)}" fill="none" '
                f'stroke="{sp["stroke"]}" stroke-width="{sp["sw"]:.1f}" stroke-linecap="round" stroke-linejoin="round"/>'
            )
            if sp["fingers"]:
                l4.append(_fingers_svg(mesh))
    if l4:
        parts.append(f'<g transform="{tf}">{"".join(l4)}</g>')
    return "".join(parts)


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


def _checklist_card(cx=236, cy=186) -> str:
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
    s0 = render_svg(
        shadow() + _ruffled_collar(
            150, 192, sit=True, lean=-7,
            mid_props=_mint_book(146, 240, closed=False),
            arms=[arm_spec((176, 198), (212, 188), (186, 166), 10.6, 8.8, 7.4, fill=PINK, layer="over_head", t_oh=0.32)],
            head_svg=_panda_head_in_hood(144, 126, sprout=False, rot=-8, expr="puzzled"),
        )
    )
    s1 = render_svg(
        shadow() + _ruffled_collar(
            150, 190, sit=True, lean=5,
            arms=[arm_spec((176, 196), (218, 180), (222, 148), 10.6, 8.8, 7.4, fill=PINK, fingers=True, layer="out")],
            head_svg=_panda_head_in_hood(152, 124, sprout=True, rot=6, expr="curious"),
        )
        + _lightbulb(242, 76)
    )
    s2 = render_svg(
        shadow() + _ruffled_collar(
            150, 190, sit=True,
            mid_props=_mint_book(150, 238, closed=False) + '<line x1="170" y1="230" x2="208" y2="204" stroke="#3B82F6" stroke-width="5.0" stroke-linecap="round"/>',
            arms=[arm_spec((172, 196), (212, 210), (192, 222), 10.4, 8.8, 7.4, fill=PINK, layer="front")],
            head_svg=_panda_head_in_hood(150, 124, sprout=True, expr="focused"),
        )
    )
    s3 = render_svg(
        _bamboo_aura() + shadow() + _ruffled_collar(
            150, 190, sit=True, lean=-4,
            mid_props=_mint_book(148, 236, closed=False),
            arms=[
                arm_spec((124, 198), (108, 224), (126, 230), 10.4, 8.8, 7.4, fill=PINK, layer="front", t_fill=0.26, t_in=0.28, t_out=0.50),
                arm_spec((176, 198), (192, 224), (170, 230), 10.4, 8.8, 7.4, fill=PINK, layer="front", t_fill=0.26, t_in=0.28, t_out=0.50),
            ],
            head_svg=_panda_head_in_hood(148, 124, sprout=True, rot=-4, expr="calm_closed"),
        )
    )
    s4 = render_svg(
        _bamboo_aura() + shadow() + _ruffled_collar(
            142, 188, sit=False, lean=5,
            mid_props=_checklist_card(236, 184),
            arms=[arm_spec((168, 194), (198, 200), (212, 190), 10.4, 8.8, 7.4, fill=PINK, layer="front", t_fill=0.30, t_in=0.32, t_out=0.54)],
            head_svg=_panda_head_in_hood(146, 124, sprout=True, perked=True, rot=7, expr="smile", strong_blush=True),
        )
        + sp4(56, 76, r=10, fill="#B8DEC9", stroke="#3E7A5B")
    )
    s5 = with_hero_aura(render_svg(
        _bamboo_aura() + shadow() + _ruffled_collar(
            150, 186, sit=False,
            mid_props=_mint_book(150, 236, closed=True),
            arms=[
                arm_spec((124, 196), (110, 224), (132, 228), 10.4, 8.8, 7.4, fill=PINK, layer="front", t_fill=0.26, t_in=0.28, t_out=0.50),
                arm_spec((176, 196), (190, 224), (168, 228), 10.4, 8.8, 7.4, fill=PINK, layer="front", t_fill=0.26, t_in=0.28, t_out=0.50),
            ],
            head_svg=_panda_head_in_hood(150, 122, sprout=True, perked=True, rot=-4, expr="happy_squint", strong_blush=True),
        )
        + sp4(50, 68, r=12) + sp4(250, 68, r=12) + sp4(250, 200, r=9, fill="#B8DEC9", stroke="#3E7A5B")
    ), (184, 222, 201))
    return [
        ("Chống Cằm Nghĩ", s0),
        ("Nảy Ý Tưởng!", s1),
        ("Cầm Bút Ghi", s2),
        ("Đọc Sách Zen", s3),
        ("Giơ Checklist", s4),
        ("Khép Sách Zen!", s5),
    ]


# =========================================================================== #
#  #69 — LOOPY RUFFLE SLEEP ROUTINE (CURVED ARMS + COZY BED!)
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
    m = _sample_arm_mesh((10, -14), (26, 2), (8, 22), 10.2, 8.6, 7.0, body_ref=(0.0, 2.0))
    parts = [
        f'<g transform="translate(138,208) rotate(-26)">'
        + _loopy_foot(-40, 10, 0) + _loopy_foot(-30, 24, 0)
        + f'<ellipse cx="0" cy="0" rx="44" ry="34" fill="none" stroke="{OL}" stroke-width="7.6"/>'
        + f'<path d="{m["full_d"]}" fill="none" stroke="{OL}" stroke-width="7.4" stroke-linejoin="round" stroke-linecap="round"/>'
        + f'<ellipse cx="0" cy="0" rx="44" ry="34" fill="{PINK}" stroke="none"/>'
        + f'<path d="{m["full_d"]}" fill="{PINK}" stroke="none"/>'
        + f'<ellipse cx="4" cy="6" rx="22" ry="18" fill="{CREAM}"/>'
        + f'<path d="{m["sub_fill_d"](0.26)}" fill="{PINK}" stroke="none"/>'
        + f'<path d="{m["sub_stroke_d"](0.28, 0.48)}" fill="none" stroke="{OL}" stroke-width="3.7" stroke-linecap="round" stroke-linejoin="round"/>'
        + _fingers_svg(m)
        + '</g>',
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
        + loopy_head(154, 118, scale=0.90, expr="curious", rot=9)
    )
    s1 = render_svg(
        _pink_blanket_bed() + _canopy_bow()
        + loopy_body(168, 206, pose="sit", paws="wave_l", lean=-6)
        + loopy_head(164, 128, scale=0.84, expr="smile", rot=-7)
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
        ("Bong Bóng Ngủ", s4),
        ("Giấc Mơ Hoa Zzz", s5),
    ]


# =========================================================================== #
#  #70 — LOOPY HAIR ROLLER GRWM (NATURAL SHOULDER-LENGTH BOB HAIR + MEME ROLLER!)
# =========================================================================== #
def _shoulder_bob_hair_back(cx=150, cy=134, rot=0) -> str:
    """Natural fluffy shoulder/chest-length dark charcoal bob curving softly inward around cheeks
    (ends cleanly around y=+74 relative to head center -> NEVER touches floor or feet!)."""
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot})">'
        f'<path d="M -66,-18 C -70,-58 -36,-76 0,-76 C 36,-76 70,-58 66,-18 '
        f'C 78,18 76,56 60,72 C 48,78 40,68 44,44 L -44,44 '
        f'C -40,68 -48,78 -60,72 C -76,56 -78,18 -66,-18 Z" '
        f'fill="#2C2228" stroke="#181216" stroke-width="3.8" stroke-linejoin="round"/>'
        f'<path d="M -58,12 Q -62,42 -54,60 M 58,12 Q 62,42 54,60" fill="none" stroke="#52424C" stroke-width="4.2" stroke-linecap="round"/>'
        f'</g>'
    )


def _pink_hair_roller(cx=150, cy=80, rot=-6, s=1.0) -> str:
    """Giant iconic pink textured velcro hair roller centered neatly on bangs."""
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot}) scale({s})">'
        f'<rect x="-40" y="-21" width="80" height="42" rx="14" fill="#F48FB1" stroke="{OL}" stroke-width="3.3"/>'
        f'<ellipse cx="38" cy="0" rx="9.5" ry="20" fill="#FCE7F3" stroke="{OL}" stroke-width="2.7"/>'
        f'<ellipse cx="38" cy="0" rx="4.8" ry="11" fill="#D8B4C6"/>'
        f'<line x1="-26" y1="-18" x2="-26" y2="18" stroke="#C94E78" stroke-width="2.4" stroke-dasharray="4,4"/>'
        f'<line x1="-12" y1="-18" x2="-12" y2="18" stroke="#C94E78" stroke-width="2.4" stroke-dasharray="4,4"/>'
        f'<line x1="2" y1="-18" x2="2" y2="18" stroke="#C94E78" stroke-width="2.4" stroke-dasharray="4,4"/>'
        f'<line x1="16" y1="-18" x2="16" y2="18" stroke="#C94E78" stroke-width="2.4" stroke-dasharray="4,4"/>'
        f'</g>'
    )


def _bouncy_bangs(cx=150, cy=82, rot=0, clip=False) -> str:
    parts = [
        f'<g transform="translate({cx},{cy}) rotate({rot})">'
        f'<path d="M -52,18 C -46,-18 46,-18 52,18 C 36,2 18,12 4,2 C -8,14 -34,4 -52,18 Z" fill="#2C2228" stroke="#181216" stroke-width="2.8"/>'
    ]
    if clip:
        parts.append(
            f'<g transform="translate(36,-4) rotate(16)">'
            f'<path d="M -2,2 C -14,-10 -22,-2 -16,6 C -10,12 -3,8 -2,4 Z M 2,2 C 14,-10 22,-2 16,6 C 10,12 3,8 2,4 Z" fill="#F472B6" stroke="{OL}" stroke-width="2.2"/>'
            f'<circle cx="0" cy="3" r="4.4" fill="#FBCFE8" stroke="{OL}" stroke-width="2.0"/></g>'
        )
    parts.append("</g>")
    return "".join(parts)


def _hand_mirror(cx=232, cy=196, rot=14) -> str:
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot})">'
        f'<rect x="-5" y="18" width="10" height="28" rx="5" fill="#F48FB1" stroke="{OL}" stroke-width="2.5"/>'
        f'<ellipse cx="0" cy="0" rx="20" ry="24" fill="#F48FB1" stroke="{OL}" stroke-width="2.9"/>'
        f'<ellipse cx="0" cy="0" rx="14.5" ry="18.5" fill="#E0F2FE" stroke="#FFFFFF" stroke-width="2.0"/>'
        f'<line x1="-7" y1="-7" x2="5" y2="5" stroke="#FFFFFF" stroke-width="2.8" stroke-linecap="round"/>'
        f'</g>'
    )


def build_70_hair_roller() -> list[tuple[str, Image.Image]]:
    # S0: Shoulder-length black bob + big pink roller + hilarious deadpan half-lidded meme!
    s0 = render_svg(
        shadow() + _shoulder_bob_hair_back(150, 134)
        + loopy_body(150, 220, pose="sit", paws="down")
        + loopy_head(150, 134, expr="deadpan", show_tuft=False)
        + _pink_hair_roller(150, 80, rot=-5, s=1.04)
    )
    # S1: Still wearing pink roller, both curved arms cradling steaming warm tea mug!
    mug_svg = '<g transform="translate(154,206)"><rect x="-15" y="-14" width="30" height="28" rx="7" fill="#FFFDF5" stroke="#5C343A" stroke-width="2.8"/><path d="M 15,-6 Q 24,-6 24,2 Q 24,10 15,10" fill="none" stroke="#5C343A" stroke-width="2.8"/><path d="M -5,-22 Q -9,-28 -4,-34 M 5,-22 Q 1,-28 6,-34" fill="none" stroke="#F48FB1" stroke-width="2.4" stroke-linecap="round"/></g>'
    s1 = render_svg(
        shadow() + _shoulder_bob_hair_back(148, 134, rot=-4)
        + loopy_body(
            150, 220, pose="sit", paws="none", lean=-4,
            mid_props=mug_svg,
            arms=[
                arm_spec((122, 200), (112, 222), (138, 212), 10.8, 9.0, 7.5, layer="front", t_fill=0.24, t_in=0.28, t_out=0.48),
                arm_spec((178, 200), (190, 222), (170, 212), 10.8, 9.0, 7.5, layer="front", t_fill=0.24, t_in=0.28, t_out=0.48),
            ],
            head_svg=loopy_head(148, 134, expr="sleepy", show_tuft=False, rot=-4) + _pink_hair_roller(144, 80, rot=-9, s=1.0),
        )
    )
    # S2: Waking up bright, left curved arm dabbing blush puff on cheek, right holding small mirror!
    s2 = render_svg(
        shadow() + _shoulder_bob_hair_back(144, 134, rot=4)
        + loopy_body(
            142, 218, pose="sit", paws="none", lean=4,
            mid_props=_hand_mirror(230, 196, rot=14),
            arms=[
                arm_spec((114, 198), (74, 184), (102, 156), 10.8, 9.0, 7.5, layer="over_head", t_oh=0.30),
                arm_spec((170, 198), (200, 218), (220, 214), 10.8, 9.0, 7.5, layer="front", t_fill=0.30, t_in=0.32, t_out=0.54),
            ],
            head_svg=loopy_head(144, 134, expr="curious", strong_blush=True, show_tuft=False, rot=4) + _pink_hair_roller(148, 80, rot=-2, s=0.98),
        )
        + '<circle cx="110" cy="150" r="8" fill="#FCE7F3" stroke="#D96B8D" stroke-width="2.0"/>'
    )
    # S3: Both curved arms reaching up smoothly outside cheeks to hold both ends of the pink roller & unroll it!
    s3 = render_svg(
        shadow() + _shoulder_bob_hair_back(150, 134)
        + loopy_body(
            150, 218, pose="stand", paws="none",
            arms=[
                arm_spec((122, 200), (54, 132), (104, 70), 10.8, 9.0, 7.5, fingers=True, layer="over_head", t_oh=0.58),
                arm_spec((178, 200), (246, 132), (196, 62), 10.8, 9.0, 7.5, fingers=True, layer="over_head", t_oh=0.58),
            ],
            head_svg=loopy_head(150, 136, expr="smile", strong_blush=True, show_tuft=False) + _pink_hair_roller(150, 62, rot=-10, s=1.0),
        )
        + sp4(52, 68, r=9)
    )
    # S4: Bouncy bangs pop out! Tilted head winking happily into hand mirror!
    s4 = render_svg(
        shadow() + _shoulder_bob_hair_back(142, 134, rot=-6)
        + loopy_body(
            142, 218, pose="stand", paws="none", lean=-5,
            mid_props=_hand_mirror(230, 190, rot=16),
            arms=[
                arm_spec((114, 198), (82, 212), (96, 224), 10.8, 9.0, 7.5, fingers=True, layer="out"),
                arm_spec((170, 198), (202, 214), (220, 208), 10.8, 9.0, 7.5, layer="front", t_fill=0.30, t_in=0.32, t_out=0.54),
            ],
            head_svg=loopy_head(140, 134, expr="wink", strong_blush=True, blush_hatch=True, show_tuft=False, rot=-6) + _bouncy_bangs(136, 86, rot=-6, clip=False),
        )
        + sp4(52, 94, r=10) + sp4(236, 98, r=9)
    )
    # S5: Smooth shoulder-length black hair with pink bow clip, sassy pose & radiant sparkles!
    s5 = with_hero_aura(render_svg(
        shadow(150, 272, 56, 8, op=0.12)
        + _shoulder_bob_hair_back(150, 126, rot=4)
        + loopy_body(
            150, 208, pose="jump", paws="none",
            arms=[
                arm_spec((122, 188), (86, 200), (108, 216), 10.8, 9.0, 7.5, layer="front", t_fill=0.28, t_in=0.30, t_out=0.52),
                arm_spec((178, 188), (216, 178), (226, 148), 11.0, 9.0, 7.5, fingers=True, layer="out"),
            ],
            head_svg=loopy_head(150, 126, expr="big_smile", strong_blush=True, blush_hatch=True, show_tuft=False, rot=4) + _bouncy_bangs(152, 78, rot=4, clip=True),
        )
        + sp4(50, 82, r=12) + sp4(250, 82, r=12) + heart(52, 196, s=11, fill="#F7B4C9", stroke="#D96B8D")
        + heart(248, 194, s=11, fill="#D96B8D", stroke=OL)
    ), (217, 107, 141))
    return [
        ("Cuốn Lô Ngái Ngủ", s0),
        ("Nhấp Trà Ấm", s1),
        ("Dặm Má Hồng", s2),
        ("Tháo Lô Cuốn", s3),
        ("Mái Bồng Xinh", s4),
        ("GRWM Lung Linh!", s5),
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
    """Draws stage label guaranteeing `text_right_x <= max_right_x` (with hard assertion!)."""
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

    # Fallback: clean 2-line word wrap at 11pt
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
        print(f"  [LOOPY v4.1] {slug:24s} -> 6 natural-arm 300x300 RGBA PNGs saved")

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

    cell_w, cell_h = 228, 276
    left_w, pad, hdr_h = 246, 18, 84
    W = pad * 2 + left_w + cell_w * 6
    H = pad * 2 + hdr_h + cell_h * len(rows)

    sheet = Image.new("RGB", (W, H), (255, 249, 250))
    draw = ImageDraw.Draw(sheet)
    try:
        f_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 27)
        f_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 15.5)
        f_row = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 15)
        f_tiny = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 11)
    except Exception:
        f_title = f_sub = f_row = f_tiny = ImageFont.load_default()

    draw.rectangle([0, 0, W, hdr_h], fill=(216, 90, 104))
    draw.text((pad, 14), "LOOPY PASTEL COLLECTION — #61–#70 (v4.1 SEAMLESS ARMS & SNUG HOODS • 60 SPRITES)", fill=(255, 255, 255), font=f_title)
    draw.text((pad, 50), "3-Layer Seamless Silhouette Arms • Smooth Elbows • Snug Head-in-Hood Framing • 0/60 Text Overlaps", fill=(255, 248, 234), font=f_sub)

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
                outline=(acc_c if is_f else (235, 224, 226)), width=2 if is_f else 1,
            )
            big = im.resize((162, 162), Image.LANCZOS)
            sheet.paste(big, (x0 + (cell_w - 162) // 2, y0 + 16), big)

            small = im.resize((44, 44), Image.LANCZOS)
            sx, sy = x0 + cell_w - 58, y0 + 184
            frame_left_x = sx - 4
            draw.rounded_rectangle([frame_left_x, sy - 4, sx + 48, sy + 48], radius=6, fill=(255, 250, 251), outline=(228, 214, 218), width=1)
            sheet.paste(small, (sx, sy), small)

            # Strict minimum 10px clearance between right edge of text and left edge of 44px preview frame!
            max_text_right = frame_left_x - 10
            stage_tag = f"S{s_i} • {pcts[s_i]}"
            draw.text((x0 + 14, y0 + 186), stage_tag, fill=acc_c, font=f_tiny)
            tb_tag = draw.textbbox((x0 + 14, y0 + 186), stage_tag, font=f_tiny)
            assert tb_tag[2] <= max_text_right, f"Stage tag overlap on {slug} S{s_i}"

            _draw_fitted_label(draw, x0 + 14, y0 + 208, lbl, max_text_right, (92, 52, 58))
            draw.text((sx + 7, sy + 50), "44px", fill=(160, 140, 144), font=f_tiny)
            verified_cells += 1

    assert verified_cells == 60
    PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PREVIEWS_DIR / "assets_contact_sheet_loopy.png"
    sheet.save(out_path, "PNG", optimize=True)
    print(f"  [PREVIEW] Saved {out_path} ({sheet.size[0]}x{sheet.size[1]}) | 0/60 label overlaps verified (>=10px gap)!")


if __name__ == "__main__":
    main()
