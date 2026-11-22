"""
generate_assets.py
==================

Reproducibly generates the kawaii "growth stage" sprites used by the Excel
habit-tracker templates, plus a contact sheet for visual QA.

Output (relative to the project root):
    assets/<slug>/stage_0.png .. stage_5.png   (256x256 RGBA, transparent)
    previews/assets_contact_sheet.png

Slugs: sunflower, cactus, lotus_stars, botanical, lavender_moon, focus_rocket

Run from the project root:
    python scripts/generate_assets.py

Technique
---------
Every sprite is drawn at 4x (1024 px) with Pillow and downscaled with LANCZOS
for crisp anti-aliasing. Shapes are described in a 256-unit coordinate space
(the final pixel grid) and scaled internally.

Shapes are organised in *groups*. A group is rendered "sticker style":
first every part is drawn grown by the outline width in the outline colour,
then every part is drawn in its own fill colour on top. This produces one
continuous, thick, rounded outline around the whole group (e.g. a stem and
its leaves share a single silhouette outline) with no seams between parts.

Stage semantics (identical for every theme):
    0 = empty base (0%)          1 = seed / tiny sprout (1-24%)
    2 = small stem / baby (25-49%)   3 = leafy / developing (50-74%)
    4 = bud / almost there (75-99%)  5 = full radiant bloom / peak (100%)
"""

from __future__ import annotations

import math
import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

# --------------------------------------------------------------------------
# Global configuration
# --------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT / "assets"
PREVIEW_DIR = ROOT / "previews"

OUT = 300                 # final sprite size (px) — V2.0 high-DPI 300x300
S = 1200                  # 4x supersampling working canvas size (px)
K = S / 256.0             # coordinate scale from 256-unit design space -> 1200 px
OW = 7.0                  # standard outline width (256-unit space, ~2.7%)
BOTTOM = 239.0            # y of the lowest *fill* edge (outline ends ~246)

SLUGS = ["sunflower", "cactus", "lotus_stars", "botanical",
         "lavender_moon", "focus_rocket",
         "sakura_zen", "ocean_coral", "matcha_cafe", "aurora_rpg"]

# Shared accent colours
SPARK_FILL = "#FFD95A"
SPARK_OL = "#E8B730"
FACE_EYE = "#4A3428"
BLUSH = (244, 143, 177, 170)


# --------------------------------------------------------------------------
# Small colour / geometry helpers
# --------------------------------------------------------------------------
def rgb(c):
    """'#RRGGBB' or tuple -> RGB(A) tuple."""
    if isinstance(c, tuple):
        return c
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def mix(c1, c2, t):
    """Linear blend of two colours (t=0 -> c1, t=1 -> c2)."""
    a, b = rgb(c1), rgb(c2)
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def with_alpha(c, a):
    return rgb(c)[:3] + (int(a),)


def quad(p0, p1, p2, n=12):
    """Quadratic bezier sample points from p0 to p2 with control p1."""
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
        pts.append((x, y))
    return pts


def round_poly(pts, r, n=6):
    """Round every corner of a polygon with radius ~r (bezier fillets)."""
    out = []
    N = len(pts)
    for i in range(N):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % N]
        d1 = math.dist(p1, p0)
        d2 = math.dist(p1, p2)
        rr = min(r, d1 / 2, d2 / 2)
        a = (p1[0] + (p0[0] - p1[0]) * rr / d1, p1[1] + (p0[1] - p1[1]) * rr / d1)
        b = (p1[0] + (p2[0] - p1[0]) * rr / d2, p1[1] + (p2[1] - p1[1]) * rr / d2)
        out += quad(a, p1, b, n)
    return out


def leaf_pts(base, ang, length, width, sharp=0.8, n=22):
    """Lens-shaped leaf/petal starting at `base` pointing at angle `ang`
    (degrees, screen coords: -90 = straight up)."""
    bx, by = base
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    left, right = [], []
    for i in range(n + 1):
        t = i / n
        hw = width / 2 * math.sin(math.pi * t) ** sharp
        cx, cy = bx + ux * t * length, by + uy * t * length
        left.append((cx + px * hw, cy + py * hw))
        right.append((cx - px * hw, cy - py * hw))
    return left + right[::-1]


def round_petal_pts(base, ang, length, width, n=22):
    """Petal with a rounded (spoon) tip - used for flowers."""
    bx, by = base
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    left, right = [], []
    for i in range(n + 1):
        t = i / n
        hw = width / 2 * math.sin(math.pi * min(1.0, t ** 0.7)) ** 0.55
        cx, cy = bx + ux * t * length, by + uy * t * length
        left.append((cx + px * hw, cy + py * hw))
        right.append((cx - px * hw, cy - py * hw))
    return left + right[::-1]


def along(base, ang, dist):
    a = math.radians(ang)
    return (base[0] + math.cos(a) * dist, base[1] + math.sin(a) * dist)


def star_pts(cx, cy, R, rot=0.0, inner=0.5, rounding=0.2):
    """Chunky rounded 5-point star."""
    pts = []
    for i in range(10):
        r = R if i % 2 == 0 else R * inner
        a = math.radians(-90 + rot + i * 36)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return round_poly(pts, R * rounding, n=5)


def sparkle_pts(cx, cy, R, fat=2.3, n=56):
    """4-point twinkle (astroid-like) sparkle."""
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        c, s = math.cos(t), math.sin(t)
        pts.append((cx + R * math.copysign(abs(c) ** fat, c),
                    cy + R * math.copysign(abs(s) ** fat, s)))
    return pts


def heart_leaf_pts(base, ang, length, n=60):
    """Heart-shaped (monstera / philodendron) leaf. `base` is the notch where
    the petiole attaches, the tip points along `ang`."""
    s = length / 29.0
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        u = (5 - y) * s          # along the leaf axis (0 = notch, + = tip)
        v = x * s * 0.95         # across the leaf
        pts.append((base[0] + ux * u + px * v, base[1] + uy * u + py * v))
    return pts


def heart_leaf_point(base, ang, length, t, scale=1.0):
    """Point on the heart leaf outline at parameter t, scaled toward midrib."""
    s = length / 29.0
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    x = 16 * math.sin(t) ** 3 * scale
    y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
    u = (5 - y) * s
    v = x * s * 0.95
    return (base[0] + ux * u + px * v, base[1] + uy * u + py * v)


# --------------------------------------------------------------------------
# Part constructors (all coordinates in 256-unit space)
# --------------------------------------------------------------------------
def E(box, fill, ol=None):
    return {"k": "ellipse", "box": box, "fill": fill, "ol": ol}


def C(cx, cy, r, fill, ol=None):
    return E((cx - r, cy - r, cx + r, cy + r), fill, ol)


def RR(box, r, fill, ol=None):
    return {"k": "rrect", "box": box, "r": r, "fill": fill, "ol": ol}


def PG(pts, fill, ol=None):
    return {"k": "poly", "pts": pts, "fill": fill, "ol": ol}


def LN(pts, w, fill, ol=None):
    return {"k": "line", "pts": pts, "w": w, "fill": fill, "ol": ol}


def ARC(box, start, end, w, fill):
    return {"k": "arc", "box": box, "a0": start, "a1": end, "w": w, "fill": fill, "ol": None}


def _sc(pts):
    return [(x * K, y * K) for x, y in pts]


def _draw_part(d, p, color, grow=0.0):
    """Draw one part, optionally grown by `grow` units (for outlines)."""
    k = p["k"]
    g = grow * K
    if k == "ellipse":
        x0, y0, x1, y1 = (v * K for v in p["box"])
        d.ellipse((x0 - g, y0 - g, x1 + g, y1 + g), fill=color)
    elif k == "rrect":
        x0, y0, x1, y1 = (v * K for v in p["box"])
        d.rounded_rectangle((x0 - g, y0 - g, x1 + g, y1 + g),
                            radius=p["r"] * K + g, fill=color)
    elif k == "poly":
        pts = _sc(p["pts"])
        d.polygon(pts, fill=color)
        if g > 0:
            d.line(pts + [pts[0], pts[1]], fill=color, width=int(round(2 * g)), joint="curve")
            step = 1 if len(pts) < 40 else max(1, len(pts) // 40)
            for x, y in pts[::step]:
                d.ellipse((x - g, y - g, x + g, y + g), fill=color)
    elif k == "line":
        pts = _sc(p["pts"])
        w = p["w"] * K + 2 * g
        d.line(pts, fill=color, width=int(round(w)), joint="curve")
        r = w / 2
        for x, y in (pts[0], pts[-1]):
            d.ellipse((x - r, y - r, x + r, y + r), fill=color)
    elif k == "arc":
        if g > 0:
            return
        x0, y0, x1, y1 = (v * K for v in p["box"])
        d.arc((x0, y0, x1, y1), p["a0"], p["a1"], fill=color, width=int(round(p["w"] * K)))


# --------------------------------------------------------------------------
# Sprite canvas
# --------------------------------------------------------------------------
_GRID = None


def _grid():
    """Cached pixel-centre coordinate grids in 256-unit space."""
    global _GRID
    if _GRID is None:
        yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
        _GRID = ((xx + 0.5) / K, (yy + 0.5) / K)
    return _GRID


class Sprite:
    """A 1024 px RGBA working canvas with sticker-style drawing helpers."""

    def __init__(self):
        self.img = Image.new("RGBA", (S, S), (0, 0, 0, 0))

    # ---- core compositing -------------------------------------------------
    def _comp(self, layer):
        self.img = Image.alpha_composite(self.img, layer)

    def group(self, parts, outline=None, ow=OW, clip=None):
        """Render parts as one sticker group. Returns the fill mask (L)."""
        layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        mask = Image.new("L", (S, S), 0)
        dm = ImageDraw.Draw(mask)
        if ow > 0 and outline is not None:
            for p in parts:
                _draw_part(d, p, p["ol"] or outline, grow=ow)
        for p in parts:
            _draw_part(d, p, p["fill"])
            if p["k"] != "arc":
                _draw_part(dm, p, 255)
        if clip is not None:
            a = ImageChops.multiply(layer.getchannel("A"), clip)
            layer.putalpha(a)
        self._comp(layer)
        return mask

    def detail(self, parts, clip=None):
        """Outline-less parts (shading, highlights, veins), optionally clipped."""
        return self.group(parts, outline=None, ow=0, clip=clip)

    # ---- effects ----------------------------------------------------------
    def glow(self, cx, cy, r, color, alpha=170, power=1.7):
        """Soft radial glow (drawn behind subsequent shapes)."""
        X, Y = _grid()
        dist = np.hypot(X - cx, Y - cy) / r
        a = np.clip(1.0 - dist, 0, 1) ** power * alpha
        arr = np.zeros((S, S, 4), np.uint8)
        arr[..., :3] = rgb(color)[:3]
        arr[..., 3] = a.astype(np.uint8)
        self._comp(Image.fromarray(arr, "RGBA"))

    def rays(self, cx, cy, r, color, n=12, alpha=150, rot=0.0, width_deg=None):
        """Radiant burst of soft triangular rays fading outward."""
        width_deg = width_deg or (360 / n) * 0.45
        m = Image.new("L", (S, S), 0)
        d = ImageDraw.Draw(m)
        for i in range(n):
            a0 = math.radians(rot + i * 360 / n - width_deg / 2)
            a1 = math.radians(rot + i * 360 / n + width_deg / 2)
            pts = [(cx, cy), (cx + r * 1.2 * math.cos(a0), cy + r * 1.2 * math.sin(a0)),
                   (cx + r * 1.2 * math.cos(a1), cy + r * 1.2 * math.sin(a1))]
            d.polygon(_sc(pts), fill=255)
        m = m.filter(ImageFilter.GaussianBlur(3 * K))
        X, Y = _grid()
        fall = np.clip(1.0 - np.hypot(X - cx, Y - cy) / r, 0, 1) ** 1.2
        a = (np.asarray(m, np.float32) / 255.0) * fall * alpha
        arr = np.zeros((S, S, 4), np.uint8)
        arr[..., :3] = rgb(color)[:3]
        arr[..., 3] = a.astype(np.uint8)
        self._comp(Image.fromarray(arr, "RGBA"))

    def mask_fill(self, mask_arr, color):
        """Fill a boolean numpy mask with a colour."""
        arr = np.zeros((S, S, 4), np.uint8)
        arr[..., :3] = rgb(color)[:3]
        arr[..., 3] = mask_arr.astype(np.uint8) * (rgb(color)[3] if len(rgb(color)) == 4 else 255)
        self._comp(Image.fromarray(arr, "RGBA"))

    def sparkle(self, cx, cy, R, fill=SPARK_FILL, ol=SPARK_OL, ow=3.5):
        self.group([PG(sparkle_pts(cx, cy, R), fill)], ol, ow=ow)

    def dot(self, cx, cy, r, fill=SPARK_FILL, ol=SPARK_OL, ow=3.0):
        self.group([C(cx, cy, r, fill)], ol, ow=ow)

    def face(self, cx, cy, s=1.0, eye=FACE_EYE, blush=BLUSH):
        """Tiny kawaii face: dot eyes with highlights, smile, blush."""
        ex = 15 * s
        parts = [
            E((cx - 27 * s - 7 * s, cy + 3 * s, cx - 27 * s + 7 * s, cy + 11 * s), blush),
            E((cx + 27 * s - 7 * s, cy + 3 * s, cx + 27 * s + 7 * s, cy + 11 * s), blush),
            E((cx - ex - 5 * s, cy - 6 * s, cx - ex + 5 * s, cy + 6 * s), eye),
            E((cx + ex - 5 * s, cy - 6 * s, cx + ex + 5 * s, cy + 6 * s), eye),
            C(cx - ex - 1.5 * s, cy - 2.5 * s, 1.9 * s, "#FFFFFF"),
            C(cx + ex - 1.5 * s, cy - 2.5 * s, 1.9 * s, "#FFFFFF"),
            ARC((cx - 6.5 * s, cy - 2 * s, cx + 6.5 * s, cy + 8 * s), 20, 160, 3.0 * s, eye),
        ]
        self.detail(parts)

    # ---- output -----------------------------------------------------------
    def final(self):
        return self.img.resize((OUT, OUT), Image.LANCZOS)

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        im = self.final()
        im.save(path, optimize=True)
        # Fall back to an alpha-aware palette if the file is unexpectedly big.
        if path.stat().st_size > 65 * 1024:
            im.quantize(colors=256, method=Image.Quantize.FASTOCTREE,
                        dither=Image.Dither.NONE).save(path, optimize=True)
        return im


# --------------------------------------------------------------------------
# Shared building blocks
# --------------------------------------------------------------------------
def tapered_body(cx, top, bottom, top_hw, bot_hw, r_top=6, r_bot=12):
    """Rounded trapezoid (pot body) points."""
    pts = [(cx - top_hw, top), (cx + top_hw, top), (cx + bot_hw, bottom), (cx - bot_hw, bottom)]
    out = []
    radii = [r_top, r_top, r_bot, r_bot]
    N = len(pts)
    for i in range(N):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % N]
        d1, d2 = math.dist(p1, p0), math.dist(p1, p2)
        rr = min(radii[i], d1 / 2, d2 / 2)
        a = (p1[0] + (p0[0] - p1[0]) * rr / d1, p1[1] + (p0[1] - p1[1]) * rr / d1)
        b = (p1[0] + (p2[0] - p1[0]) * rr / d2, p1[1] + (p2[1] - p1[1]) * rr / d2)
        out += quad(a, p1, b, 6)
    return out


def classic_pot(sp, *, body, body_ol, rim, rim_ol, soil, soil_ol,
                rim_box, body_top, top_hw, bot_hw, soil_box, band=None,
                plant=None, cx=128.0):
    """Terracotta-style pot: body, soil mound, (plant), rim in front.

    `plant` is a callable drawn after the soil and before the rim so that
    stems appear to grow out of the soil behind the rim."""
    body_pts = tapered_body(cx, body_top, BOTTOM, top_hw, bot_hw)
    m = sp.group([PG(body_pts, body)], body_ol)
    # 1-tone shading: darker right side + soft highlight stripe on the left
    sp.detail([PG([(cx + top_hw * 0.42, body_top - 5), (cx + 140, body_top - 5),
                   (cx + 140, BOTTOM + 5), (cx + bot_hw * 0.42, BOTTOM + 5)],
                  mix(body, body_ol, 0.28))], clip=m)
    if band:
        sp.detail([RR((cx - 140, band[0], cx + 140, band[1]), 0, band[2])], clip=m)
    sp.group([E(soil_box, soil)], soil_ol)
    sp.detail([E((soil_box[0] + 14, soil_box[1] + 4, soil_box[0] + 40, soil_box[1] + 9),
                 with_alpha(mix(soil, "#FFFFFF", 0.25), 200))])
    if plant:
        plant(sp)
    mr = sp.group([RR(rim_box, 9, rim)], rim_ol)
    x0, y0, x1, y1 = rim_box
    sp.detail([RR((x0 + 8, y0 + 4, x0 + 34, y0 + 9), 3, with_alpha("#FFFFFF", 110)),
               RR((x0 + (x1 - x0) * 0.72, y0 - 2, x1 + 4, y1 + 4), 0, mix(rim, rim_ol, 0.25))],
              clip=mr)


def stem_leaves_group(sp, stem_pts, stem_w, leaves, stem_col, leaf_col, ol,
                      vein=None):
    """Stem + leaves as one sticker group, then optional midribs."""
    parts = [LN(stem_pts, stem_w, stem_col)]
    for (base, ang, ln, wd) in leaves:
        parts.append(PG(leaf_pts(base, ang, ln, wd), leaf_col))
    sp.group(parts, ol)
    if vein:
        veins = []
        for (base, ang, ln, wd) in leaves:
            if ln >= 26:
                veins.append(LN([along(base, ang, ln * 0.18), along(base, ang, ln * 0.72)],
                                max(2.2, ln * 0.06), vein))
        if veins:
            sp.detail(veins)


def corner_sparkles(sp, spots):
    for (x, y, r) in spots:
        sp.sparkle(x, y, r)


# --------------------------------------------------------------------------
# Theme 1: sunflower
# --------------------------------------------------------------------------
SUN = dict(pot="#C97B5A", pot_ol="#8E4F35", rim="#D68A69", rim_ol="#8E4F35",
           soil="#7A4E3A", soil_ol="#4E3024", stem="#5E9E4F", leaf="#7CC26A",
           green_ol="#3C7232", petal="#F7C531", petal2="#F2A81D", petal_ol="#C98612",
           center="#6B3E26", center_ol="#432616")


def sunflower(stage: int) -> Sprite:
    sp = Sprite()
    c = SUN
    if stage == 5:
        sp.glow(128, 92, 128, "#FFE680", alpha=190)
        corner_sparkles(sp, [(24, 34, 13), (230, 28, 11), (234, 132, 9), (20, 150, 8)])

    def plant(sp):
        if stage == 0:
            return
        G = c["green_ol"]
        if stage == 1:
            stem_leaves_group(sp, [(128, 186), (128, 146)], 10,
                              [((128, 150), -150, 34, 22), ((128, 150), -30, 34, 22)],
                              c["stem"], c["leaf"], G, vein=c["stem"])
        elif stage == 2:
            stem_leaves_group(sp, quad((128, 186), (124, 150), (128, 104)), 11,
                              [((127, 160), -165, 46, 26), ((127, 152), -15, 46, 26),
                               ((128, 112), -128, 32, 20), ((128, 112), -52, 32, 20)],
                              c["stem"], c["leaf"], G, vein=c["stem"])
        elif stage == 3:
            stem_leaves_group(sp, quad((128, 186), (122, 130), (128, 66)), 12,
                              [((126, 166), -168, 58, 32), ((126, 158), -12, 58, 32),
                               ((125, 120), -150, 50, 28), ((126, 112), -30, 50, 28),
                               ((128, 74), -122, 34, 20), ((128, 74), -58, 34, 20)],
                              c["stem"], c["leaf"], G, vein=c["stem"])
        elif stage == 4:
            stem_leaves_group(sp, quad((128, 186), (122, 120), (128, 60)), 13,
                              [((126, 168), -170, 64, 34), ((126, 160), -10, 64, 34),
                               ((125, 126), -152, 56, 30), ((126, 118), -28, 56, 30),
                               ((127, 90), -138, 42, 24), ((127, 90), -42, 42, 24)],
                              c["stem"], c["leaf"], G, vein=c["stem"])
            # yellow petal tips peeking out of the bud
            sp.group([PG(leaf_pts((128, 50), a, 34, 17), c["petal"])
                      for a in (-118, -90, -62)], c["petal_ol"])
            # closed bud with wrapping sepals
            sp.group([E((106, 34, 150, 80), c["leaf"]),
                      PG(leaf_pts((128, 78), -128, 40, 20), c["stem"]),
                      PG(leaf_pts((128, 78), -52, 40, 20), c["stem"]),
                      PG(leaf_pts((128, 80), -90, 30, 18), c["leaf"])], G)
            sp.detail([E((114, 42, 124, 54), with_alpha("#FFFFFF", 90))])
        elif stage == 5:
            stem_leaves_group(sp, quad((128, 186), (124, 150), (128, 110)), 14,
                              [((126, 172), -168, 70, 36), ((126, 166), -12, 70, 36),
                               ((126, 150), -150, 52, 28), ((126, 146), -30, 52, 28)],
                              c["stem"], c["leaf"], G, vein=c["stem"])
            cx, cy = 128, 88
            sp.group([PG(leaf_pts(along((cx, cy), a, 26), a, 50, 26, sharp=0.7), c["petal2"])
                      for a in [i * 360 / 14 + 12.9 for i in range(14)]], c["petal_ol"])
            sp.group([PG(leaf_pts(along((cx, cy), a, 24), a, 46, 24, sharp=0.7), c["petal"])
                      for a in [i * 360 / 14 for i in range(14)]], c["petal_ol"])
            m = sp.group([C(cx, cy, 33, c["center"])], c["center_ol"])
            dots = []
            for ring_r, n in ((22, 12), (12, 7)):
                for i in range(n):
                    a = math.radians(i * 360 / n + ring_r)
                    dots.append(C(cx + ring_r * math.cos(a), cy + ring_r * math.sin(a), 2.6, "#8C5435"))
            sp.detail(dots + [E((cx - 22, cy - 25, cx - 4, cy - 14), with_alpha("#FFFFFF", 60))], clip=m)

    classic_pot(sp, body=c["pot"], body_ol=c["pot_ol"], rim=c["rim"], rim_ol=c["rim_ol"],
                soil=c["soil"], soil_ol=c["soil_ol"], rim_box=(66, 182, 190, 204),
                body_top=200, top_hw=50, bot_hw=36, soil_box=(78, 172, 178, 194),
                plant=plant)
    if stage >= 3:
        sp.face(128, 219, s=0.95)
    return sp


# --------------------------------------------------------------------------
# Theme 2: cactus
# --------------------------------------------------------------------------
CAC = dict(pot="#E39B6B", pot_ol="#A9603A", rim="#D07F4E", rim_ol="#A9603A",
           soil="#7A4E3A", soil_ol="#4E3024", green="#6FBF73", rib="#4E9A56",
           green_ol="#3B7F45", pink="#F48FB1", pink2="#F06292", pink_ol="#C2457A")


def _cactus_body(sp, body_box, arms, arm_w):
    """Column body + L-shaped arms, ribs and spine dots."""
    c = CAC
    x0, y0, x1, y1 = body_box
    w = x1 - x0
    parts = [RR(body_box, w / 2, c["green"])]
    for arm in arms:
        parts.append(LN(arm, arm_w, c["green"]))
    m = sp.group(parts, c["green_ol"])
    cx = (x0 + x1) / 2
    det = [RR((cx + w * 0.18, y0 - 4, x1 + 6, y1 + 6), 0, with_alpha(c["rib"], 120))]
    # ribs
    for off in (-0.22, 0.22):
        det.append(LN([(cx + w * off, y0 + w * 0.35), (cx + w * off, y1 - 6)], 3.2, c["rib"]))
    sp.detail(det, clip=m)
    # highlight + spines
    spines = [RR((cx - w * 0.36, y0 + w * 0.3, cx - w * 0.26, y0 + w * 0.3 + min(40, (y1 - y0) * 0.35)),
                 4, with_alpha("#FFFFFF", 90))]
    h = y1 - y0
    for j in range(int(h // 22)):
        yy = y0 + 18 + j * 22
        for xo in (-0.36, 0.0, 0.36):
            spines.append(C(cx + w * xo, yy + (11 if xo == 0 else 0), 2.1, "#FFFFFF"))
    for arm in arms:
        ex, ey = arm[-1]
        spines.append(C(ex, ey + 10, 2.1, "#FFFFFF"))
    sp.detail(spines, clip=m)


def _pink_flower(sp, cx, cy, r, n=6):
    c = CAC
    sp.group([PG(round_petal_pts((cx, cy), a, r, r * 0.8), c["pink"])
              for a in [i * 360 / n - 90 for i in range(n)]], c["pink_ol"])
    sp.detail([PG(round_petal_pts((cx, cy), a, r * 0.6, r * 0.4), c["pink2"])
               for a in [i * 360 / n - 90 for i in range(n)]])
    sp.group([C(cx, cy, r * 0.32, SPARK_FILL)], "#E0A020", ow=3)


def cactus(stage: int) -> Sprite:
    sp = Sprite()
    c = CAC
    if stage == 5:
        sp.glow(128, 92, 124, "#FFD3E2", alpha=200)
        corner_sparkles(sp, [(26, 36, 13), (228, 30, 12), (230, 140, 9), (22, 142, 8)])

    def plant(sp):
        if stage == 0:
            return
        if stage == 1:
            # seed sprouting: a tiny round nub with two baby leaves
            sp.group([E((110, 142, 146, 180), c["green"])], c["green_ol"])
            sp.detail([C(122, 154, 3, with_alpha("#FFFFFF", 150)), C(128, 150, 2, "#FFFFFF"),
                       C(137, 160, 2, "#FFFFFF")])
        elif stage == 2:
            _cactus_body(sp, (96, 110, 160, 186), [], 0)
        elif stage == 3:
            _cactus_body(sp, (100, 68, 156, 186), [[(104, 140), (74, 140), (74, 104)]], 26)
        elif stage in (4, 5):
            _cactus_body(sp, (98, 50, 158, 186),
                         [[(102, 142), (66, 142), (66, 100)],
                          [(154, 122), (190, 122), (190, 82)]], 28)

    classic_pot(sp, body=c["pot"], body_ol=c["pot_ol"], rim=c["rim"], rim_ol=c["rim_ol"],
                soil=c["soil"], soil_ol=c["soil_ol"], rim_box=(68, 176, 188, 200),
                body_top=196, top_hw=50, bot_hw=36, soil_box=(80, 166, 176, 188),
                plant=plant)
    if stage == 4:
        sp.group([E((114, 26, 142, 58), c["pink"]),
                  PG(leaf_pts((128, 58), -130, 18, 12), c["green"]),
                  PG(leaf_pts((128, 58), -50, 18, 12), c["green"])], c["pink_ol"])
        sp.detail([E((119, 32, 127, 42), with_alpha("#FFFFFF", 120))])
    if stage == 5:
        _pink_flower(sp, 128, 42, 30)
        _pink_flower(sp, 190, 72, 15, n=5)
    if stage >= 3:
        sp.face(128, 217, s=0.95)
    return sp


# --------------------------------------------------------------------------
# Theme 3: lotus_stars (mason jar of stars)
# --------------------------------------------------------------------------
JAR = dict(glass="#D7EAF8", glass2="#C2DDF3", glass_ol="#7FA6CC", lid="#A8C8E8",
           lid_ol="#6B93BD", star="#FFD95A", star_ol="#E2AE22",
           lotus="#F7B6C8", lotus2="#F29BB5", lotus_ol="#D7809E",
           pad="#9ED39A", pad_ol="#5FA160")

# Star slots filling the jar from the bottom (cx, cy, R, rotation)
STAR_SLOTS = [
    (84, 214, 23, 8), (130, 216, 24, -10), (176, 213, 23, 14),            # row 0
    (62, 182, 21, -6), (106, 180, 22, 18), (152, 182, 22, -14), (196, 179, 21, 6),  # row 1
    (84, 148, 22, 12), (130, 146, 23, -4), (176, 149, 22, 20),            # row 2
    (62, 116, 20, -16), (106, 114, 21, 4), (152, 116, 21, -20), (196, 113, 20, 10),  # row 3
    (84, 88, 19, -8), (130, 86, 20, 14), (176, 88, 19, -2),               # row 4 (neck)
]
STAR_COUNT = {0: 0, 1: 1, 2: 3, 3: 7, 4: 11, 5: 17}


def _jar_star(sp, cx, cy, R, rot, clip):
    c = JAR
    sp.group([PG(star_pts(cx, cy, R, rot), c["star"])], c["star_ol"], ow=4.5, clip=clip)
    sp.detail([E((cx - R * 0.42, cy - R * 0.42, cx - R * 0.08, cy - R * 0.12),
                 with_alpha("#FFFFFF", 150))], clip=clip)


def lotus_stars(stage: int) -> Sprite:
    sp = Sprite()
    c = JAR
    body_box = (48, 80, 208, BOTTOM)
    if stage == 5:
        sp.glow(128, 140, 132, "#FFE27A", alpha=210, power=1.4)
    # jar glass (neck + body as one silhouette)
    m = sp.group([RR((66, 64, 190, 92), 10, c["glass"]), RR(body_box, 36, c["glass"])],
                 c["glass_ol"])
    sp.detail([RR((150, 60, 230, 245), 0, c["glass2"])], clip=m)
    # star order: first stars land in the bottom-centre so stage 1/2 look tidy
    order = [1, 0, 2] if stage == 2 else [1, 0, 2]
    slots = [STAR_SLOTS[i] for i in order] + STAR_SLOTS[3:]
    if stage == 1:
        slots = [(128, 208, 28, 0)]
    if stage == 2:
        slots = [(92, 212, 25, 10), (164, 212, 25, -12), (128, 176, 25, 4)]
    n = STAR_COUNT[stage]
    if stage >= 3:
        sp.glow(128, 200, 110, "#FFE27A", alpha=120)
    for (x, y, R, rot) in slots[:n]:
        _jar_star(sp, x, y, R, rot, m)
    # glass highlights on top of the stars
    sp.detail([RR((62, 104, 76, 200), 7, with_alpha("#FFFFFF", 175)),
               C(69, 214, 6, with_alpha("#FFFFFF", 175)),
               RR((184, 110, 192, 150), 4, with_alpha("#FFFFFF", 120))], clip=m)
    # lid
    ml = sp.group([RR((58, 36, 198, 68), 11, c["lid"])], c["lid_ol"])
    sp.detail([LN([(64, 48), (192, 48)], 3.5, mix(c["lid"], c["lid_ol"], 0.45)),
               LN([(64, 57), (192, 57)], 3.5, mix(c["lid"], c["lid_ol"], 0.45)),
               RR((70, 39, 110, 44), 2, with_alpha("#FFFFFF", 140)),
               RR((168, 30, 210, 75), 0, with_alpha(c["lid_ol"], 70))], clip=ml)
    if stage == 5:
        # overflowing stars + sparkles
        for (x, y, R, rot) in [(36, 70, 16, 12), (222, 84, 15, -14), (212, 26, 11, 6)]:
            sp.group([PG(star_pts(x, y, R, rot), c["star"])], c["star_ol"], ow=4)
        sp.sparkle(34, 26, 11)
        sp.sparkle(232, 160, 9)
        sp.sparkle(22, 150, 8)
        # pastel lotus on the lid
        base = (128, 42)
        sp.group([PG(leaf_pts((128, 40), a, 38, 16), c["pad"]) for a in (-168, -12)], c["pad_ol"], ow=5)
        sp.group([PG(leaf_pts(base, a, 36, 21, sharp=0.65), c["lotus2"]) for a in (-152, -28)]
                 + [PG(leaf_pts(base, a, 40, 23, sharp=0.65), c["lotus"]) for a in (-122, -58)],
                 c["lotus_ol"], ow=5)
        sp.group([PG(leaf_pts(base, -90, 40, 25, sharp=0.65), c["lotus"])], c["lotus_ol"], ow=5)
        sp.detail([PG(leaf_pts((128, 38), -90, 24, 10, sharp=0.7), with_alpha("#FFFFFF", 130))])
    return sp


# --------------------------------------------------------------------------
# Theme 4: botanical (monstera in a sage/cream planter)
# --------------------------------------------------------------------------
BOT = dict(pot="#E8D5B7", pot_ol="#AE9168", rim="#F1E4CC", rim_ol="#AE9168",
           band="#9FB8AD", soil="#6E5444", soil_ol="#47342A",
           leaf="#7FA88F", leaf2="#8FB89E", leaf_back="#6C977E", vein="#5C8A70",
           leaf_ol="#46705A", stem="#6E9A7E", flower="#E0A899", flower2="#D48A7A",
           flower_ol="#B66F5F")


def _monstera(sp, base, ang, length, color, slits=2, ol=None):
    """One heart-shaped monstera leaf with midrib and split 'fenestrations'."""
    c = BOT
    sp.group([PG(heart_leaf_pts(base, ang, length), color)], ol or c["leaf_ol"], ow=6)
    det = [LN([along(base, ang, length * 0.02), along(base, ang, length * 0.66)],
              max(2.5, length * 0.055), c["vein"])]
    if slits:
        # side slits run from the edge toward the midrib
        ts = [0.9, 1.35, 1.8][:slits]
        for t in ts:
            for sgn in (1, -1):
                p_edge = heart_leaf_point(base, ang, length, sgn * t + (0 if sgn > 0 else 2 * math.pi), 1.02)
                p_in = heart_leaf_point(base, ang, length, sgn * t + (0 if sgn > 0 else 2 * math.pi), 0.45)
                det.append(LN([p_in, p_edge], max(3.0, length * 0.07), c["leaf_ol"]))
    sp.detail(det)


def _coral_flower(sp, cx, cy, r):
    c = BOT
    sp.group([C(cx + r * 0.62 * math.cos(math.radians(a)), cy + r * 0.62 * math.sin(math.radians(a)),
                r * 0.52, c["flower"]) for a in range(-90, 270, 72)], c["flower_ol"], ow=4.5)
    sp.group([C(cx, cy, r * 0.32, "#F7E3B5")], "#C9A060", ow=3)


def botanical(stage: int) -> Sprite:
    sp = Sprite()
    c = BOT
    if stage == 5:
        sp.glow(128, 100, 128, "#F6D6C8", alpha=210)
        corner_sparkles(sp, [(26, 30, 12), (230, 34, 11), (232, 150, 8), (22, 150, 8)])
    root = (128, 180)

    def petioles(ends, w=6.5):
        sp.group([LN(quad(root, ((root[0] + x) / 2, (root[1] + y) / 2 + 12), (x, y)), w, c["stem"])
                  for (x, y) in ends], c["leaf_ol"], ow=5.5)

    def plant(sp):
        if stage == 0:
            return
        if stage == 1:
            sp.group([LN(quad((128, 180), (122, 166), (130, 150)), 6, c["stem"]),
                      PG(leaf_pts((130, 152), -40, 26, 16), c["leaf2"]),
                      PG(leaf_pts((129, 154), -150, 22, 14), c["leaf"])], c["leaf_ol"], ow=6)
            sp.group([E((104, 166, 126, 182), "#B98458")], "#7D5232", ow=5)
        elif stage == 2:
            petioles([(108, 136), (150, 124)])
            _monstera(sp, (108, 138), -130, 44, c["leaf"], slits=0)
            _monstera(sp, (150, 126), -55, 48, c["leaf2"], slits=0)
        elif stage == 3:
            ends = [(92, 126), (166, 118), (128, 98)]
            petioles(ends)
            _monstera(sp, (92, 128), -148, 60, c["leaf_back"], slits=1)
            _monstera(sp, (166, 120), -32, 62, c["leaf"], slits=1)
            _monstera(sp, (128, 100), -92, 64, c["leaf2"], slits=2)
        elif stage in (4, 5):
            ends = [(78, 136), (178, 130), (98, 92), (160, 84), (128, 68)]
            petioles(ends)
            _monstera(sp, (78, 138), -160, 64, c["leaf_back"], slits=1)
            _monstera(sp, (178, 132), -20, 66, c["leaf_back"], slits=1)
            _monstera(sp, (98, 94), -122, 66, c["leaf"], slits=2)
            _monstera(sp, (160, 86), -60, 68, c["leaf"], slits=2)
            _monstera(sp, (128, 70), -90, 70 if stage == 5 else 62, c["leaf2"], slits=2)

    classic_pot(sp, body=c["pot"], body_ol=c["pot_ol"], rim=c["rim"], rim_ol=c["rim_ol"],
                soil=c["soil"], soil_ol=c["soil_ol"], rim_box=(68, 176, 188, 198),
                body_top=194, top_hw=50, bot_hw=38, soil_box=(80, 166, 176, 188),
                band=(206, 218, c["band"]), plant=plant)
    if stage == 5:
        _coral_flower(sp, 58, 114, 24)
        _coral_flower(sp, 198, 106, 21)
        _coral_flower(sp, 128, 56, 21)
    if stage >= 3:
        sp.face(128, 226, s=0.85)
    return sp


# --------------------------------------------------------------------------
# Theme 5: lavender_moon
# --------------------------------------------------------------------------
LAV = dict(pot="#C8B6E2", pot_ol="#8C76B6", rim="#B9A3DC", rim_ol="#8C76B6",
           soil="#5E4B6B", soil_ol="#3E3049", stem="#7FA36B", stem_ol="#4F7542",
           flower="#A594F9", flower2="#C8B6E2", flower_ol="#6E5BCB",
           moon="#F6E7A8", moon_full="#FFF4C2", moon_dark="#7A7396",
           moon_ol="#5B5470", moon_full_ol="#D9BE62")

MOON_FRACTION = {0: 0.0, 1: 0.18, 2: 0.5, 3: 0.72, 4: 0.88, 5: 1.0}


def _moon(sp, stage, cx=128, cy=74, r=58):
    c = LAV
    f = MOON_FRACTION[stage]
    full = stage == 5
    if full:
        sp.glow(cx, cy, r * 2.15, "#FFF1B0", alpha=220, power=1.5)
    m = sp.group([C(cx, cy, r, c["moon_full"] if full else c["moon_dark"])],
                 c["moon_full_ol"] if full else c["moon_ol"])
    X, Y = _grid()
    nx, ny = (X - cx) / r, (Y - cy) / r
    disk = np.asarray(m) > 127
    a = 1 - 2 * f
    lit = disk & (nx >= a * np.sqrt(np.clip(1 - ny ** 2, 0, 1)))
    if 0 < f < 1:
        sp.mask_fill(lit, c["moon"])
    if f > 0:
        lit_img = Image.fromarray((lit * 255).astype(np.uint8), "L")
        craters = [E((cx + 14, cy - 30, cx + 32, cy - 14), mix(c["moon"], "#D9BE62", 0.45)),
                   E((cx + 24, cy + 6, cx + 36, cy + 18), mix(c["moon"], "#D9BE62", 0.45)),
                   E((cx - 30, cy + 10, cx - 12, cy + 28), mix(c["moon"], "#D9BE62", 0.45)),
                   E((cx - 26, cy - 22, cx - 16, cy - 12), mix(c["moon"], "#D9BE62", 0.45))]
        sp.detail(craters, clip=lit_img)
    if stage == 0:
        sp.detail([E((cx - 34, cy - 38, cx - 14, cy - 24), with_alpha("#FFFFFF", 45))], clip=m)
    if full:
        sp.detail([E((cx - 38, cy - 40, cx - 14, cy - 24), with_alpha("#FFFFFF", 160))], clip=m)


def _lavender_spike(stem_pts, n_buds, bud_r, flower_col):
    """Parts for one stem topped with a lavender flower spike."""
    c = LAV
    parts = [LN(stem_pts, 6, c["stem"])]
    top = stem_pts[-1]
    prev = stem_pts[-4] if len(stem_pts) >= 4 else stem_pts[0]
    ang = math.degrees(math.atan2(top[1] - prev[1], top[0] - prev[0]))
    for i in range(n_buds):
        t = i / max(1, n_buds - 1)
        p = along(top, ang + 180, (1 - t) * bud_r * 1.25 * (n_buds - 1))
        r = bud_r * (1.0 - 0.45 * t)
        side = -1 if i % 2 == 0 else 1
        q = along(p, ang + 90 * side, r * 0.45)
        col = flower_col if i % 3 != 2 else c["flower2"]
        parts.append(C(q[0], q[1], r, col))
    parts.append(C(top[0], top[1], bud_r * 0.5, flower_col))
    return parts


def lavender_moon(stage: int) -> Sprite:
    sp = Sprite()
    c = LAV
    _moon(sp, stage)
    if stage == 5:
        corner_sparkles(sp, [(26, 30, 12), (232, 26, 11), (234, 140, 9), (20, 146, 8)])
    root = (128, 202)

    def plant(sp):
        G = c["stem_ol"]
        if stage == 0:
            return
        if stage == 1:
            sp.group([LN([(128, 204), (128, 180)], 6, c["stem"]),
                      PG(leaf_pts((128, 184), -150, 24, 12), c["stem"]),
                      PG(leaf_pts((128, 184), -30, 24, 12), c["stem"])], G, ow=6)
        elif stage == 2:
            sp.group([LN(quad(root, (124, 170), (128, 140)), 6, c["stem"]),
                      PG(leaf_pts((127, 186), -155, 32, 12), c["stem"]),
                      PG(leaf_pts((127, 178), -25, 32, 12), c["stem"]),
                      PG(leaf_pts((127, 160), -130, 22, 9), c["stem"]),
                      PG(leaf_pts((127, 156), -50, 22, 9), c["stem"])], G, ow=6)
            sp.group([C(128, 138, 6, "#9CC283")], G, ow=5)
        elif stage == 3:
            tops = [(98, 126), (128, 112), (158, 126)]
            parts = [LN(quad(root, ((root[0] + x) / 2, 168), (x, y)), 6, c["stem"]) for x, y in tops]
            parts += [PG(leaf_pts((126, 194), -160, 36, 12), c["stem"]),
                      PG(leaf_pts((130, 194), -20, 36, 12), c["stem"]),
                      PG(leaf_pts((126, 176), -140, 24, 9), c["stem"]),
                      PG(leaf_pts((130, 176), -40, 24, 9), c["stem"])]
            parts += [C(x, y - 2, 7, "#9CC283") for x, y in tops]
            sp.group(parts, G, ow=6)
        elif stage == 4:
            tops = [(90, 108), (128, 92), (166, 108)]
            parts = [PG(leaf_pts((126, 196), -162, 38, 12), c["stem"]),
                     PG(leaf_pts((130, 196), -18, 38, 12), c["stem"])]
            for x, y in tops:
                parts += _lavender_spike(quad(root, ((root[0] + x) / 2, 170), (x, y)), 3, 8.5, c["flower"])
            sp.group(parts, c["flower_ol"], ow=5.5)
        elif stage == 5:
            tops = [(62, 96), (94, 66), (128, 52), (162, 66), (194, 96)]
            parts = [PG(leaf_pts((126, 198), -165, 42, 13), c["stem"]),
                     PG(leaf_pts((130, 198), -15, 42, 13), c["stem"])]
            for x, y in tops:
                parts += _lavender_spike(quad(root, ((root[0] + x) / 2, 168), (x, y)), 5, 9.5, c["flower"])
            sp.group(parts, c["flower_ol"], ow=5.5)

    classic_pot(sp, body=c["pot"], body_ol=c["pot_ol"], rim=c["rim"], rim_ol=c["rim_ol"],
                soil=c["soil"], soil_ol=c["soil_ol"], rim_box=(76, 194, 180, 214),
                body_top=210, top_hw=44, bot_hw=34, soil_box=(86, 186, 170, 204),
                plant=plant)
    if stage >= 3:
        sp.face(128, 226, s=0.72)
    return sp


# --------------------------------------------------------------------------
# Theme 6: focus_rocket
# --------------------------------------------------------------------------
ROC = dict(body="#F7E3E5", body2="#EBC3C8", navy="#2B3452", navy_ol="#161B2E",
           window="#5C6B9C", flame="#FF7A59", flame2="#FFB86B", flame3="#FFE29A",
           flame_ol="#E0573A", smoke="#F1F2F8", smoke_ol="#A9AFC8", pad_top="#46507A")

ROCKET_BOTTOM = {0: 222, 1: 222, 2: 196, 3: 166, 4: 138, 5: 118}
FLAME_LEN = {0: 0, 1: 0, 2: 28, 3: 46, 4: 66, 5: 88}


def _flame_pts(cx, top, w, h):
    """Teardrop flame hanging from (cx, top), round end up, tip down."""
    r = w / 2
    pts = []
    for i in range(13):
        a = math.radians(180 + i * 15)
        pts.append((cx + r * math.cos(a), top + r + r * math.sin(a)))
    pts += quad((cx + r, top + r), (cx + r * 1.05, top + h * 0.62), (cx, top + h), 12)[1:]
    pts += quad((cx, top + h), (cx - r * 1.05, top + h * 0.62), (cx - r, top + r), 12)[1:-1]
    return pts


def _rocket(sp, cx, yb):
    c = ROC
    top = yb - 112
    # fins (behind body)
    lf = round_poly([(cx - 28, yb - 58), (cx - 52, yb - 28), (cx - 54, yb - 4), (cx - 26, yb - 20)], 7)
    rf = [(2 * cx - x, y) for x, y in lf]
    sp.group([PG(lf, c["navy"]), PG(rf, c["navy"]),
              RR((cx - 17, yb - 18, cx + 17, yb), 5, c["navy"])], c["navy_ol"])
    # body
    right = quad((cx, top), (cx + 38, top + 26), (cx + 34, top + 66), 14) + \
        quad((cx + 34, top + 66), (cx + 31, yb - 26), (cx + 24, yb - 12), 8)[1:]
    body = right + [(2 * cx - x, y) for x, y in reversed(right)][1:-1]
    m = sp.group([PG(body, c["body"])], c["navy_ol"])
    sp.detail([RR((cx + 12, top - 4, cx + 50, yb), 0, c["body2"]),
               RR((cx - 60, top - 4, cx + 60, top + 26), 0, c["navy"]),
               RR((cx - 60, yb - 34, cx + 60, yb - 26), 0, c["window"]),
               RR((cx - 22, top + 34, cx - 15, top + 74), 3, with_alpha("#FFFFFF", 200))], clip=m)
    # window
    sp.group([C(cx, top + 54, 16, c["window"])], c["navy"], ow=6)
    sp.detail([E((cx - 10, top + 44, cx - 1, top + 53), with_alpha("#FFFFFF", 220)),
               C(cx + 6, top + 61, 2.5, with_alpha("#FFFFFF", 160))])
    sp.detail([E((cx - 6, top + 6, cx + 1, top + 14), with_alpha("#FFFFFF", 110))])


def _flame(sp, cx, yb, h):
    c = ROC
    sp.group([PG(_flame_pts(cx, yb - 4, 32, h), c["flame"])], c["flame_ol"], ow=5)
    sp.detail([PG(_flame_pts(cx, yb - 2, 20, h * 0.68), c["flame2"]),
               PG(_flame_pts(cx, yb - 1, 10, h * 0.38), c["flame3"])])


def _smoke(sp, cx, cy, s=1.0):
    c = ROC
    sp.group([C(cx - 14 * s, cy + 2 * s, 12 * s, c["smoke"]), C(cx, cy - 6 * s, 14 * s, c["smoke"]),
              C(cx + 15 * s, cy + 2 * s, 12 * s, c["smoke"]),
              RR((cx - 24 * s, cy - 2 * s, cx + 26 * s, cy + 12 * s), 7 * s, c["smoke"])],
             c["smoke_ol"], ow=5)


def focus_rocket(stage: int) -> Sprite:
    sp = Sprite()
    c = ROC
    cx = 128
    yb = ROCKET_BOTTOM[stage]
    if stage == 5:
        sp.rays(cx, 72, 134, SPARK_FILL, n=16, alpha=210)
        sp.glow(cx, 72, 120, "#FFE89A", alpha=225)
        # subtle orbital badge ring behind the rocket
        sp.group([C(cx, 72, 66, with_alpha("#F2D7D9", 95))], "#FFD95A", ow=5)
        sp.group([C(42, 74, 14, "#F2D7D9")], c["navy"], ow=4.5)
        sp.group([C(214, 62, 11, "#A594F9")], c["navy"], ow=4.5)
    # launch pad
    mp = sp.group([RR((56, 222, 200, BOTTOM), 8, c["navy"])], c["navy_ol"])
    sp.detail([RR((60, 222, 196, 227), 3, c["pad_top"])], clip=mp)
    sp.detail([C(x, 233, 3.2, SPARK_FILL) for x in (78, 100, 156, 178)])
    if FLAME_LEN[stage]:
        _flame(sp, cx, yb, FLAME_LEN[stage])
    if stage == 3:
        _smoke(sp, 78, 208, 1.0)
        _smoke(sp, 180, 210, 0.9)
    if stage >= 4:
        _smoke(sp, 82, 212, 0.7)
        _smoke(sp, 176, 212, 0.62)
    _rocket(sp, cx, yb)
    if stage == 1:
        sp.sparkle(98, 212, 9, fill=c["flame2"], ol=c["flame_ol"], ow=3)
        sp.sparkle(158, 212, 9, fill=c["flame2"], ol=c["flame_ol"], ow=3)
        sp.sparkle(128, 228, 7, fill=c["flame3"], ol=c["flame_ol"], ow=3)
    if stage == 4:
        corner_sparkles(sp, [(40, 40, 11), (214, 70, 9), (48, 130, 7)])
    if stage == 5:
        corner_sparkles(sp, [(30, 36, 15), (226, 30, 13), (214, 128, 11), (40, 140, 10),
                             (196, 196, 7), (60, 196, 7)])
    return sp


# --------------------------------------------------------------------------
# Theme 7: sakura_zen (Japanese Washi & Blossoming Sakura Branch)
# --------------------------------------------------------------------------
SAK = dict(vase="#F4ECE3", vase_ol="#8E796D", band="#A8C69F",
           soil="#6D5046", soil_ol="#49332C", wood="#7A5247", wood_ol="#4D3129",
           petal="#F7C5D0", petal2="#F2A4B8", petal_ol="#C9738B",
           center="#FFE184", leaf="#A8C69F", leaf_ol="#5F8456")


def _sakura_flower(sp, cx, cy, r):
    c = SAK
    parts = [C(cx + r * 0.58 * math.cos(math.radians(a)),
               cy + r * 0.58 * math.sin(math.radians(a)),
               r * 0.52, c["petal"]) for a in range(-90, 270, 72)]
    sp.group(parts, c["petal_ol"], ow=4.0)
    sp.group([C(cx, cy, r * 0.28, c["center"])], "#D9A438", ow=2.5)


def sakura_zen(stage: int) -> Sprite:
    sp = Sprite()
    c = SAK
    if stage == 5:
        sp.glow(128, 92, 134, "#FFD6E2", alpha=220, power=1.45)
        corner_sparkles(sp, [(26, 30, 13), (230, 34, 11), (226, 158, 9), (26, 162, 8)])

    def plant(sp):
        # Graceful cherry trunk & branches present from stage 0 (winter bare branch!)
        trunk = LN(quad((128, 186), (120, 145), (132, 102 if stage >= 3 else 128)), 10, c["wood"])
        b_left = LN(quad((124, 150), (96, 136), (72, 114)), 7, c["wood"])
        b_right = LN(quad((128, 136), (158, 122), (186, 106)), 7, c["wood"])
        parts = [trunk, b_left, b_right]
        if stage >= 3:
            parts.append(LN(quad((128, 118), (94, 92), (76, 68)), 6, c["wood"]))
            parts.append(LN(quad((130, 114), (162, 86), (180, 66)), 6, c["wood"]))
        sp.group(parts, c["wood_ol"], ow=5.5)

        if stage == 0:
            return
        if stage == 1:
            # Tiny pink buds on the bare branch
            for bx, by in [(74, 114), (130, 124), (184, 106), (104, 136)]:
                sp.group([C(bx, by, 8.5, c["petal2"])], c["petal_ol"], ow=4.0)
        elif stage == 2:
            # First matcha leaves + 3 small blossoms
            sp.group([PG(leaf_pts((110, 140), -150, 26, 13), c["leaf"]),
                      PG(leaf_pts((154, 124), -25, 26, 13), c["leaf"])], c["leaf_ol"], ow=4.5)
            for fx, fy, fr in [(72, 112, 16), (132, 120, 18), (186, 104, 16)]:
                _sakura_flower(sp, fx, fy, fr)
        elif stage == 3:
            sp.group([PG(leaf_pts((98, 136), -155, 30, 14), c["leaf"]),
                      PG(leaf_pts((160, 122), -20, 30, 14), c["leaf"]),
                      PG(leaf_pts((130, 96), -90, 28, 13), c["leaf"])], c["leaf_ol"], ow=4.5)
            for fx, fy, fr in [(68, 112, 19), (80, 72, 18), (132, 92, 21), (176, 70, 18), (188, 108, 19)]:
                _sakura_flower(sp, fx, fy, fr)
        elif stage >= 4:
            # Lush sakura canopy cloud + layered flowers
            canopy = [C(82, 100, 36, c["petal"]), C(174, 98, 36, c["petal"]),
                      C(104, 66, 38, c["petal"]), C(152, 66, 38, c["petal"]),
                      C(128, 56, 40 if stage == 5 else 34, c["petal"])]
            sp.group(canopy, c["petal_ol"], ow=6.0)
            sp.group([PG(leaf_pts((52, 112), -165, 32, 14), c["leaf"]),
                      PG(leaf_pts((204, 110), -15, 32, 14), c["leaf"]),
                      PG(leaf_pts((128, 108), -90, 26, 12), c["leaf"])], c["leaf_ol"], ow=4.5)
            blooms = [(72, 98, 21), (104, 62, 22), (154, 62, 22), (184, 96, 21), (128, 86, 23)]
            if stage == 5:
                blooms.append((128, 44, 24))
            for fx, fy, fr in blooms:
                _sakura_flower(sp, fx, fy, fr)
            if stage == 5:
                # Floating falling sakura petals
                for px, py, pa in [(38, 138, 25), (218, 132, -30), (50, 56, 45), (208, 54, -40)]:
                    sp.group([PG(leaf_pts((px, py), pa, 18, 10), c["petal2"])], c["petal_ol"], ow=3.0)

    classic_pot(sp, body=c["vase"], body_ol=c["vase_ol"], rim=c["vase"], rim_ol=c["vase_ol"],
                soil=c["soil"], soil_ol=c["soil_ol"], rim_box=(72, 180, 184, 200),
                body_top=196, top_hw=48, bot_hw=38, soil_box=(82, 172, 174, 190),
                band=(208, 220, c["band"]), plant=plant)
    if stage >= 3:
        sp.face(128, 228, s=0.82)
    return sp


# --------------------------------------------------------------------------
# Theme 8: ocean_coral (Coral Reef & Glowing Pearl Oyster)
# --------------------------------------------------------------------------
OCN = dict(sand="#F3DFC1", sand2="#E5C99E", sand_ol="#B59164",
           teal="#2E7D87", teal2="#4FA8B0", teal_ol="#1B525A",
           coral="#F4A582", coral2="#E88468", coral_ol="#B85D46",
           mint="#8FD8CC", mint_ol="#4A9B90",
           shell="#F8C8D4", shell_ol="#C27B91",
           pearl="#FFFDF5", pearl_ol="#D4B86A")


def ocean_coral(stage: int) -> Sprite:
    sp = Sprite()
    c = OCN
    if stage == 5:
        sp.glow(128, 124, 132, "#A8F0E8", alpha=215, power=1.45)
        corner_sparkles(sp, [(28, 34, 13), (228, 30, 12), (232, 140, 9), (24, 146, 8)])

    # Coral & reef behind sandy mound
    if stage >= 2:
        # Left coral branch
        left_coral = [LN(quad((76, 204), (66, 168), (54, 134 if stage >= 3 else 156)), 14, c["coral"]),
                      LN(quad((66, 172), (46, 160), (40, 142)), 11, c["coral"])]
        if stage >= 4:
            left_coral.append(LN(quad((68, 160), (88, 140), (84, 114)), 11, c["coral"]))
        sp.group(left_coral, c["coral_ol"], ow=5.5)

    if stage >= 3:
        # Right lagoon-teal / seafoam coral branch
        right_coral = [LN(quad((182, 204), (192, 162), (206, 122 if stage >= 4 else 144)), 14, c["teal2"]),
                       LN(quad((190, 166), (212, 152), (218, 132)), 11, c["teal2"])]
        if stage >= 4:
            right_coral.append(LN(quad((188, 154), (168, 130), (172, 102)), 11, c["mint"]))
        sp.group(right_coral, c["teal_ol"], ow=5.5)

    if stage >= 4:
        # Back seafoam kelp fronds
        kelp = [PG(leaf_pts((114, 200), -104, 118 if stage == 5 else 96, 22), c["mint"]),
                PG(leaf_pts((142, 200), -76, 118 if stage == 5 else 96, 22), c["mint"])]
        sp.group(kelp, c["mint_ol"], ow=5.0)

    # Sandy seabed mound (consistent base across all 6 stages!)
    m_sand = sp.group([E((36, 186, 220, BOTTOM + 16), c["sand"])], c["sand_ol"], ow=6.5)
    sp.detail([E((54, 212, 206, BOTTOM + 22), c["sand2"]),
               C(68, 222, 5, "#D9B98C"), C(186, 220, 6, "#D9B98C"), C(152, 228, 4, "#D9B98C")],
              clip=m_sand)

    # Foreground center element: seashell -> budding pearl oyster -> radiant pearl!
    if stage == 1:
        sp.group([E((104, 174, 152, 212), c["shell"]),
                  RR((114, 204, 142, 214), 4, c["shell"])], c["shell_ol"], ow=5.0)
        sp.detail([C(156, 154, 6, with_alpha("#D4F1EC", 210)), C(146, 136, 4, with_alpha("#D4F1EC", 190))])
    elif stage in (2, 3):
        sp.group([E((96, 166, 160, 212), c["shell"])], c["shell_ol"], ow=5.5)
        sp.detail([LN([(128, 210), (112, 174)], 3.5, c["shell_ol"]),
                   LN([(128, 210), (128, 170)], 3.5, c["shell_ol"]),
                   LN([(128, 210), (144, 174)], 3.5, c["shell_ol"])])
        if stage == 3:
            sp.face(128, 194, s=0.72)
            for bx, by, br in [(92, 128, 7), (168, 114, 6), (128, 100, 5)]:
                sp.group([C(bx, by, br, "#E8FAF8")], c["teal2"], ow=3.0)
    elif stage >= 4:
        # Open clam oyster revealing radiant glowing pearl!
        sp.group([E((78, 126 if stage == 5 else 138, 178, 204), c["shell"])], c["shell_ol"], ow=6.0)
        sp.group([E((84, 174, 172, 216), "#FBE0E6")], c["shell_ol"], ow=5.5)
        if stage == 5:
            sp.glow(128, 164, 58, "#FFF2B2", alpha=230)
            sp.group([C(128, 164, 24, c["pearl"])], c["pearl_ol"], ow=5.0)
            sp.detail([C(120, 156, 7, "#FFFFFF"), C(136, 172, 3, "#FFFFFF")])
            for bx, by, br in [(64, 88, 9), (194, 82, 8), (128, 60, 7)]:
                sp.group([C(bx, by, br, "#E8FAF8")], c["teal2"], ow=3.0)
        else:
            sp.group([C(128, 172, 16, c["pearl"])], c["pearl_ol"], ow=4.5)
            sp.detail([C(123, 167, 5, "#FFFFFF")])
        sp.face(128, 202, s=0.72)
    return sp


# --------------------------------------------------------------------------
# Theme 9: matcha_cafe (Artisanal Ceremonial Matcha Latte Cup)
# --------------------------------------------------------------------------
MAT = dict(coaster="#C99A6B", coaster_ol="#8A5E3B",
           cup="#FAF4EA", cup2="#EDE2D0", cup_ol="#6B4D3C",
           matcha="#8FA97B", matcha2="#A8C294", matcha_ol="#597349",
           foam="#FFFDF8", foam_ol="#C9B79C",
           caramel="#D4A373", bean="#5C4033", bean_ol="#38241C")


def matcha_cafe(stage: int) -> Sprite:
    sp = Sprite()
    c = MAT
    if stage == 5:
        sp.glow(128, 124, 134, "#D7E8C5", alpha=215, power=1.45)
        corner_sparkles(sp, [(26, 36, 13), (230, 38, 12), (228, 166, 9), (26, 168, 8)])

    # Wooden cafe coaster (consistent base!)
    sp.group([RR((44, 218, 212, BOTTOM), 9, c["coaster"])], c["coaster_ol"], ow=6.0)
    sp.detail([RR((54, 222, 202, 227), 3, "#DFB68B")])

    if stage == 0:
        # Single cute matcha leaf & roasted coffee bean resting on coaster
        sp.group([PG(leaf_pts((114, 212), -145, 42, 20), c["matcha"]),
                  E((122, 184, 162, 214), c["bean"])], c["bean_ol"], ow=5.5)
        sp.detail([LN([(128, 190), (154, 208)], 3.5, "#8C6552")])
        return sp

    # Ceramic cup handle (right side)
    sp.group([E((166, 126, 218, 190), c["cup"])], c["cup_ol"], ow=6.5)
    sp.group([E((176, 140, 204, 176), "#FFFFFF")], c["cup_ol"], ow=4.5)
    # Wait: make inner handle transparent by drawing handle as thick arc/ring instead:
    sp = Sprite()
    if stage == 5:
        sp.glow(128, 124, 134, "#D7E8C5", alpha=215, power=1.45)
        corner_sparkles(sp, [(26, 36, 13), (230, 38, 12), (228, 166, 9), (26, 168, 8)])
    sp.group([RR((44, 218, 212, BOTTOM), 9, c["coaster"])], c["coaster_ol"], ow=6.0)
    sp.detail([RR((54, 222, 202, 227), 3, "#DFB68B")])
    # Handle as thick curved line so hole stays 100% transparent!
    sp.group([LN(quad((176, 134), (218, 152), (174, 184)), 14, c["cup"])], c["cup_ol"], ow=5.5)

    # Cup body
    cup_poly = round_poly([(62, 114), (186, 114), (174, 216), (74, 216)], 18)
    m_cup = sp.group([PG(cup_poly, c["cup"])], c["cup_ol"], ow=6.5)
    sp.detail([RR((148, 110, 194, 220), 0, c["cup2"]),
               RR((74, 132, 84, 190), 5, with_alpha("#FFFFFF", 180))], clip=m_cup)

    # Matcha rim & fill level inside cup top
    if stage == 1:
        sp.group([E((66, 102, 182, 126), "#DFD3C3")], c["cup_ol"], ow=5.5)
    elif stage == 2:
        sp.group([E((66, 102, 182, 126), c["matcha"])], c["cup_ol"], ow=5.5)
        # Pouring green matcha stream!
        sp.group([LN(quad((124, 34), (120, 74), (124, 114)), 10, c["matcha2"])], c["matcha_ol"], ow=4.5)
    elif stage == 3:
        sp.group([E((66, 98, 182, 126), c["matcha"])], c["cup_ol"], ow=5.5)
        sp.group([E((76, 90, 172, 120), c["foam"])], c["foam_ol"], ow=4.5)
    elif stage >= 4:
        # Creamy fluffy foam dome + leaf latte art!
        sp.group([E((64, 96, 184, 126), c["matcha"])], c["cup_ol"], ow=5.5)
        sp.group([E((72, 82, 176, 122), c["foam"]),
                  C(96, 96, 16, c["foam"]), C(152, 96, 16, c["foam"]),
                  C(124, 88, 20, c["foam"])], c["foam_ol"], ow=5.0)
        # Cute green matcha leaf latte art on top of foam
        sp.group([PG(leaf_pts((124, 110), -125, 24, 12), c["matcha"]),
                  PG(leaf_pts((124, 110), -55, 24, 12), c["matcha"]),
                  PG(leaf_pts((124, 108), -90, 22, 10), c["matcha2"])], c["matcha_ol"], ow=3.0)
    if stage == 5:
        # Cozy rising steam swirls above the cup!
        sp.group([LN(quad((96, 68), (84, 48), (100, 30)), 5.5, "#FFFFFF"),
                  LN(quad((124, 62), (112, 40), (128, 22)), 6.0, "#FFFFFF"),
                  LN(quad((152, 68), (140, 48), (156, 30)), 5.5, "#FFFFFF")],
                 c["caramel"], ow=3.2)
    if stage >= 3:
        sp.face(124, 172, s=0.95)
    return sp


# --------------------------------------------------------------------------
# Theme 10: aurora_rpg (Nordic Rune -> Radiant Aurora Crystal & Orb)
# --------------------------------------------------------------------------
AUR = dict(stone="#3B4563", stone2="#242B3D", stone_ol="#151A28",
           mint="#4FD1C5", mint_l="#A3F7EF", mint_ol="#268780",
           violet="#9F7AEA", violet_l="#D6BCFA", violet_ol="#5B3FA8",
           gold="#FFD95A", gold_ol="#D4A324")


def aurora_rpg(stage: int) -> Sprite:
    sp = Sprite()
    c = AUR
    if stage == 5:
        sp.rays(128, 102, 134, c["mint"], n=14, alpha=165)
        sp.glow(128, 102, 128, c["violet"], alpha=190, power=1.45)
        sp.glow(128, 102, 92, c["mint_l"], alpha=210, power=1.6)
        # Aurora orbital halo ring
        sp.group([C(128, 102, 68, with_alpha(c["violet_l"], 65))], c["mint"], ow=5.5)
        sp.group([C(48, 86, 10, c["mint_l"])], c["mint_ol"], ow=3.5)
        sp.group([C(208, 118, 9, c["violet_l"])], c["violet_ol"], ow=3.5)
        corner_sparkles(sp, [(28, 30, 14), (228, 32, 12), (226, 176, 9), (30, 178, 9)])
    elif stage == 4:
        sp.glow(128, 112, 105, c["mint"], alpha=155)
        corner_sparkles(sp, [(42, 48, 10), (214, 58, 9)])

    # Nordic carved stone rune pedestal (consistent base across all 6 stages!)
    ped = round_poly([(62, 206), (194, 206), (208, BOTTOM), (48, BOTTOM)], 10)
    mp = sp.group([PG(ped, c["stone"])], c["stone_ol"], ow=6.0)
    sp.detail([RR((44, 224, 212, BOTTOM + 6), 0, c["stone2"])], clip=mp)
    # Glowing rune dots on pedestal
    rune_col = c["mint_l"] if stage >= 2 else "#647299"
    sp.detail([C(92, 222, 4.5, rune_col), C(128, 222, 5.5, rune_col), C(164, 222, 4.5, rune_col)])

    if stage == 0:
        return sp
    if stage == 1:
        sp.glow(128, 182, 44, c["mint"], alpha=140)
        sp.sparkle(128, 182, 16, fill=c["mint_l"], ol=c["mint_ol"], ow=4.0)
        sp.dot(104, 192, 5, fill=c["violet_l"], ol=c["violet_ol"], ow=2.5)
        sp.dot(152, 190, 5, fill=c["violet_l"], ol=c["violet_ol"], ow=2.5)
    elif stage == 2:
        sp.glow(128, 164, 62, c["mint"], alpha=160)
        flame = [(128, 126), (154, 164), (144, 198), (112, 198), (102, 164)]
        sp.group([PG(round_poly(flame, 10), c["mint"])], c["mint_ol"], ow=5.5)
        sp.detail([PG([(128, 146), (140, 174), (128, 192), (116, 174)], c["mint_l"])])
    elif stage == 3:
        # Floating glowing crystal prism
        sp.glow(128, 142, 78, c["violet"], alpha=150)
        crys = [(128, 86), (164, 134), (128, 192), (92, 134)]
        m = sp.group([PG(crys, c["mint"])], c["stone_ol"], ow=6.0)
        sp.detail([PG([(128, 86), (164, 134), (128, 192)], c["violet"]),
                   PG([(128, 102), (144, 134), (128, 168), (112, 134)], with_alpha("#FFFFFF", 130))], clip=m)
    elif stage >= 4:
        # Large faceted Aurora Crystal + twin side shards
        l_sh = [(76, 114), (96, 146), (80, 186), (58, 152)]
        r_sh = [(180, 114), (198, 152), (176, 186), (160, 146)]
        sp.group([PG(l_sh, c["violet"]), PG(r_sh, c["mint"])], c["stone_ol"], ow=5.5)
        top_y = 38 if stage == 5 else 54
        crys = [(128, top_y), (172, 108), (156, 182), (128, 196), (100, 182), (84, 108)]
        m = sp.group([PG(crys, c["mint"])], c["stone_ol"], ow=6.5)
        sp.detail([PG([(128, top_y), (172, 108), (156, 182), (128, 196)], c["violet"]),
                   PG([(128, top_y + 18), (150, 108), (128, 166), (106, 108)], c["mint_l"]),
                   PG([(114, top_y + 30), (122, 104), (104, 108)], with_alpha("#FFFFFF", 180))], clip=m)
    return sp


# --------------------------------------------------------------------------
# Registry, export and contact sheet
# --------------------------------------------------------------------------
THEMES = {
    "sunflower": sunflower,
    "cactus": cactus,
    "lotus_stars": lotus_stars,
    "botanical": botanical,
    "lavender_moon": lavender_moon,
    "focus_rocket": focus_rocket,
    "sakura_zen": sakura_zen,
    "ocean_coral": ocean_coral,
    "matcha_cafe": matcha_cafe,
    "aurora_rpg": aurora_rpg,
}

# Dedicated overhauled vector-Bezier generators for Templates #20-#23 (`alpaca_*` & `bamboo_panda`)
from generate_assets_alpaca_panda import (  # noqa: E402
    draw_alpaca_blush as alpaca_blush,
    draw_alpaca_cream as alpaca_cream,
    draw_alpaca_matcha as alpaca_matcha,
    draw_bamboo_panda as bamboo_panda,
)


def _font(size, bold=False):
    for name in (("segoeuib.ttf" if bold else "segoeui.ttf"), "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def build_contact_sheet(sprites: dict[str, list[Image.Image]], path: Path):
    """6 rows x 6 stages at 128 px, plus a 44 px strip (actual Excel size)."""
    cream = (253, 248, 238)
    label_w, cell, gap = 190, 128, 18
    strip = 44
    row_h = 24 + cell + 12 + strip + 26
    header = 82
    W = label_w + 6 * (cell + gap) + 10
    H = header + row_h * len(sprites) + 10
    sheet = Image.new("RGBA", (W, H), cream + (255,))
    d = ImageDraw.Draw(sheet)
    f_head, f_lab, f_small = _font(22, True), _font(17, True), _font(12)
    d.text((16, 16), f"Habit Tracker Sprite Collection — {len(sprites)} Themes × 6 Growth Stages", fill=(70, 60, 55), font=f_head)
    for s in range(6):
        x = label_w + s * (cell + gap) + cell // 2
        d.text((x, header - 10), f"Stage {s}", fill=(110, 95, 85), font=f_lab, anchor="ms")
    for r, (slug, ims) in enumerate(sprites.items()):
        y0 = header + r * row_h
        d.line((10, y0 + 4, W - 10, y0 + 4), fill=(232, 222, 205), width=2)
        d.text((16, y0 + 24 + cell // 2), slug, fill=(70, 60, 55), font=f_lab, anchor="lm")
        d.text((16, y0 + 24 + cell + 12 + strip // 2), "44 px (Excel)", fill=(140, 125, 115),
               font=f_small, anchor="lm")
        # 44px strip on a white "cell" background, like Excel
        sx0 = label_w
        d.rectangle((sx0 - 6, y0 + 24 + cell + 6, sx0 + 6 * (strip + 8) + 2, y0 + 24 + cell + 18 + strip),
                    fill=(255, 255, 255), outline=(220, 220, 220))
        for s, im in enumerate(ims):
            x = label_w + s * (cell + gap)
            big = im.resize((cell, cell), Image.LANCZOS)
            sheet.alpha_composite(big, (x, y0 + 24))
            small = im.resize((strip, strip), Image.LANCZOS)
            sheet.alpha_composite(small, (sx0 + s * (strip + 8), y0 + 24 + cell + 12))
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.convert("RGB").save(path, optimize=True)


def main():
    results = {}
    for slug, fn in THEMES.items():
        ims = []
        for stage in range(6):
            out = ASSETS_DIR / slug / f"stage_{stage}.png"
            ims.append(fn(stage).save(out))
            print(f"  {out.relative_to(ROOT)}  {out.stat().st_size / 1024:.1f} KB")
        results[slug] = ims
    sheet_path = PREVIEW_DIR / "assets_contact_sheet.png"
    build_contact_sheet(results, sheet_path)
    print(f"Contact sheet: {sheet_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
