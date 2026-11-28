"""
generate_holiday_decor.py — Generates crisp super-sampled (2x->1x LANCZOS) transparent PNG
holiday corner decorations in the exact unified kawaii pastel chibi sticker aesthetic
(smooth dark-brown outline #4A3228, soft cel-shading, warm holiday colors, ZERO AI quota):

  Christmas (#81-#88):
    - xmas_banner_tl.png / xmas_banner_tr.png : Red & gold ribbon bow + pine sprigs + holly berries
    - xmas_hero_tl.png   / xmas_hero_tr.png   : Compact pine sprig + mini red bow + snowflake corner

  New Year Apricot / Hoa Mai Vàng (#89, #90, #91, #93):
    - ny_apricot_banner_tl.png / tr.png       : Curved branch of blooming golden Hoa Mai + mini red lantern/tassel
    - ny_apricot_hero_tl.png   / tr.png       : Compact Hoa Mai corner spray + tiny gold sparkle

  New Year Sakura / Hoa Đào (#92, #94, #95):
    - ny_sakura_banner_tl.png  / tr.png       : Curved branch of pastel-pink Hoa Đào/Anh Đào + mini red lantern/tassel
    - ny_sakura_hero_tl.png    / tr.png       : Compact Hoa Đào corner spray + drifting petals

Saved into `assets/_holiday_decor/` (0 impact on #01-#80).
"""
from __future__ import annotations

import math
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
DECOR_DIR = ROOT / "assets" / "_holiday_decor"
OUTLINE = (74, 50, 40, 255)  # #4A3228 warm dark-brown kawaii sticker outline


def _cubic_bezier(p0, p1, p2, p3, steps=180):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        mt = 1.0 - t
        x = (mt**3)*p0[0] + 3*(mt**2)*t*p1[0] + 3*mt*(t**2)*p2[0] + (t**3)*p3[0]
        y = (mt**3)*p0[1] + 3*(mt**2)*t*p1[1] + 3*mt*(t**2)*p2[1] + (t**3)*p3[1]
        pts.append((x, y))
    return pts


def _draw_thick_curve(draw: ImageDraw.ImageDraw, pts, radius: float, fill, outline=OUTLINE, outline_w: float = 4.0):
    # Outline pass
    r_out = radius + outline_w
    for x, y in pts:
        draw.ellipse([x - r_out, y - r_out, x + r_out, y + r_out], fill=outline)
    # Fill pass
    for x, y in pts:
        draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=fill)


def _draw_tapered_branch(draw: ImageDraw.ImageDraw, pts, r_start: float, r_end: float,
                         fill=(146, 98, 66, 255), hi=(178, 128, 92, 255), outline_w: float = 4.5):
    n = max(1, len(pts) - 1)
    # Outline pass
    for i, (x, y) in enumerate(pts):
        r = r_start + (r_end - r_start) * (i / n) + outline_w
        draw.ellipse([x - r, y - r, x + r, y + r], fill=OUTLINE)
    # Main wood fill
    for i, (x, y) in enumerate(pts):
        r = r_start + (r_end - r_start) * (i / n)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=fill)
    # Soft top highlight
    for i, (x, y) in enumerate(pts):
        r = max(1.5, (r_start + (r_end - r_start) * (i / n)) * 0.42)
        draw.ellipse([x - r, y - r - r * 0.45, x + r, y + r - r * 0.45], fill=hi)


def _draw_leaf(draw: ImageDraw.ImageDraw, cx: float, cy: float, length: float, width: float,
               angle_deg: float, fill=(104, 174, 108, 255), hi=(142, 206, 138, 255), outline_w: float = 4.0):
    ang = math.radians(angle_deg)
    ca, sa = math.cos(ang), math.sin(ang)

    def rot(px, py):
        return (cx + px * ca - py * sa, cy + px * sa + py * ca)

    # Almond polygon
    poly = []
    steps = 16
    for i in range(steps + 1):
        u = i / steps
        x = u * length
        y = math.sin(u * math.pi) * width * 0.5
        poly.append(rot(x, y))
    for i in range(steps, -1, -1):
        u = i / steps
        x = u * length
        y = -math.sin(u * math.pi) * width * 0.5
        poly.append(rot(x, y))

    # Draw thick outline via polygon + thick line
    draw.polygon(poly, fill=fill, outline=OUTLINE)
    for i in range(len(poly)):
        p1 = poly[i]
        p2 = poly[(i + 1) % len(poly)]
        draw.line([p1, p2], fill=OUTLINE, width=int(round(outline_w)))
    # Re-fill interior cleanly
    inner = []
    s = 0.84
    for i in range(steps + 1):
        u = i / steps
        inner.append(rot(u * length * s + length * 0.08, math.sin(u * math.pi) * width * 0.38))
    for i in range(steps, -1, -1):
        u = i / steps
        inner.append(rot(u * length * s + length * 0.08, -math.sin(u * math.pi) * width * 0.38))
    draw.polygon(inner, fill=fill)
    # Soft vein highlight
    draw.line([rot(length * 0.16, 0), rot(length * 0.78, 0)], fill=hi, width=max(2, int(width * 0.12)))


def _draw_blossom(draw: ImageDraw.ImageDraw, cx: float, cy: float, radius: float,
                  petal_c, petal_hi, center_c, outline_w: float = 4.0, rot_deg: float = 0.0):
    petals = []
    for k in range(5):
        a = math.radians(rot_deg + k * 72.0)
        px = cx + math.cos(a) * radius * 0.56
        py = cy + math.sin(a) * radius * 0.56
        pr = radius * 0.48
        petals.append((px, py, pr))

    # Outline circles first
    for px, py, pr in petals:
        r_o = pr + outline_w
        draw.ellipse([px - r_o, py - r_o, px + r_o, py + r_o], fill=OUTLINE)
    # Petal fills
    for px, py, pr in petals:
        draw.ellipse([px - pr, py - pr, px + pr, py + pr], fill=petal_c)
    # Soft inner glow
    for px, py, pr in petals:
        r_h = pr * 0.58
        draw.ellipse([px - r_h, py - r_h, px + r_h, py + r_h], fill=petal_hi)
    # Center bud + stamens
    cr = radius * 0.25
    draw.ellipse([cx - cr - 2, cy - cr - 2, cx + cr + 2, cy + cr + 2], fill=OUTLINE)
    draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=center_c)
    for k in range(5):
        a = math.radians(rot_deg + 36.0 + k * 72.0)
        sx = cx + math.cos(a) * radius * 0.36
        sy = cy + math.sin(a) * radius * 0.36
        draw.ellipse([sx - 3.5, sy - 3.5, sx + 3.5, sy + 3.5], fill=center_c)


def _draw_4star(draw: ImageDraw.ImageDraw, cx: float, cy: float, r_out: float, fill=(253, 224, 71, 255), outline_w: int = 3):
    r_in = r_out * 0.34
    pts = []
    for i in range(8):
        a = math.radians(i * 45.0 - 90.0)
        r = r_out if i % 2 == 0 else r_in
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    # Outline
    for dx, dy in ((-outline_w, 0), (outline_w, 0), (0, -outline_w), (0, outline_w)):
        draw.polygon([(x + dx, y + dy) for x, y in pts], fill=OUTLINE)
    draw.polygon(pts, fill=fill)


def _draw_snowflake(draw: ImageDraw.ImageDraw, cx: float, cy: float, r: float,
                    fill=(219, 234, 254, 255), stroke=(147, 197, 253, 255)):
    for k in range(3):
        a = math.radians(k * 60.0)
        dx, dy = math.cos(a) * r, math.sin(a) * r
        draw.line([(cx - dx, cy - dy), (cx + dx, cy + dy)], fill=stroke, width=6)
        draw.line([(cx - dx, cy - dy), (cx + dx, cy + dy)], fill=fill, width=3)
    draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=fill, outline=stroke, width=2)


def _draw_mini_lantern(draw: ImageDraw.ImageDraw, cx: float, cy: float, scale: float = 1.0):
    # String
    draw.line([(cx, cy - 28 * scale), (cx, cy - 12 * scale)], fill=OUTLINE, width=int(4 * scale))
    # Body
    rx, ry = 18 * scale, 15 * scale
    draw.ellipse([cx - rx - 4, cy - ry - 4, cx + rx + 4, cy + ry + 4], fill=OUTLINE)
    draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(239, 68, 68, 255))
    # Warm center glow
    draw.ellipse([cx - rx * 0.58, cy - ry * 0.65, cx + rx * 0.58, cy + ry * 0.65], fill=(252, 165, 105, 255))
    # Gold caps
    cw, ch = 10 * scale, 4.5 * scale
    for yy in (cy - ry - 1, cy + ry - ch + 2):
        draw.rounded_rectangle([cx - cw - 3, yy - 3, cx + cw + 3, yy + ch + 3], radius=4, fill=OUTLINE)
        draw.rounded_rectangle([cx - cw, yy, cx + cw, yy + ch], radius=3, fill=(251, 191, 36, 255))
    # Gold tassel
    ty0 = cy + ry + 4 * scale
    draw.line([(cx, ty0), (cx, ty0 + 18 * scale)], fill=OUTLINE, width=int(7 * scale))
    draw.line([(cx, ty0), (cx, ty0 + 17 * scale)], fill=(251, 191, 36, 255), width=int(4 * scale))
    draw.ellipse([cx - 4 * scale, ty0 + 14 * scale, cx + 4 * scale, ty0 + 22 * scale], fill=(239, 68, 68, 255), outline=OUTLINE, width=2)


def _draw_kawaii_bow(draw: ImageDraw.ImageDraw, cx: float, cy: float, sc: float = 1.0,
                     red=(225, 72, 82, 255), hi=(248, 128, 134, 255), gold=(251, 191, 36, 255)):
    # Two trailing ribbon tails
    for side in (-1, 1):
        pts = _cubic_bezier(
            (cx, cy + 6 * sc),
            (cx + side * 14 * sc, cy + 28 * sc),
            (cx + side * 28 * sc, cy + 44 * sc),
            (cx + side * 38 * sc, cy + 56 * sc),
            steps=24,
        )
        _draw_thick_curve(draw, pts, radius=8.5 * sc, fill=red, outline_w=4.0 * sc)
        _draw_thick_curve(draw, pts[2:-2], radius=2.5 * sc, fill=gold, outline_w=0.0)

    # Left & right bow loops
    for side in (-1, 1):
        lx = cx + side * 26 * sc
        ly = cy - 4 * sc
        rx, ry = 26 * sc, 18 * sc
        draw.ellipse([lx - rx - 4 * sc, ly - ry - 4 * sc, lx + rx + 4 * sc, ly + ry + 4 * sc], fill=OUTLINE)
        draw.ellipse([lx - rx, ly - ry, lx + rx, ly + ry], fill=red)
        draw.ellipse([lx - rx * 0.6, ly - ry * 0.55, lx + rx * 0.5, ly + ry * 0.18], fill=hi)

    # Center knot
    kr = 13 * sc
    draw.ellipse([cx - kr - 4 * sc, cy - kr - 4 * sc, cx + kr + 4 * sc, cy + kr + 4 * sc], fill=OUTLINE)
    draw.ellipse([cx - kr, cy - kr, cx + kr, cy + kr], fill=red)
    draw.ellipse([cx - kr * 0.55, cy - kr * 0.55, cx + kr * 0.35, cy + kr * 0.15], fill=hi)


def _draw_holly_berries(draw: ImageDraw.ImageDraw, cx: float, cy: float, r: float = 9.0):
    offsets = [(-r * 0.9, r * 0.3), (r * 0.9, r * 0.3), (0, -r * 0.65)]
    for ox, oy in offsets:
        draw.ellipse([cx + ox - r - 3.5, cy + oy - r - 3.5, cx + ox + r + 3.5, cy + oy + r + 3.5], fill=OUTLINE)
    for ox, oy in offsets:
        draw.ellipse([cx + ox - r, cy + oy - r, cx + ox + r, cy + oy + r], fill=(220, 48, 62, 255))
        draw.ellipse([cx + ox - r * 0.45, cy + oy - r * 0.55, cx + ox - r * 0.05, cy + oy - r * 0.15], fill=(255, 210, 214, 255))


def build_xmas_banner_tl() -> Image.Image:
    # 2x supersampled (760 x 280 -> 380 x 140)
    im = Image.new("RGBA", (760, 280), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # Graceful golden-red ribbon swoop across top-left
    pts_rib = _cubic_bezier((16, 18), (190, 24), (360, 72), (690, 26), steps=220)
    _draw_thick_curve(d, pts_rib, radius=13, fill=(225, 72, 82, 255), outline_w=5.0)
    _draw_thick_curve(d, pts_rib[6:-6], radius=4.5, fill=(252, 211, 77, 255), outline_w=0.0)

    # Delicate hanging golden fairy light bulbs along the ribbon
    for idx in (58, 102, 146, 184):
        bx, by = pts_rib[idx]
        d.line([(bx, by + 10), (bx, by + 34)], fill=OUTLINE, width=4)
        d.ellipse([bx - 16, by + 26, bx + 16, by + 58], fill=(254, 240, 138, 120))
        d.ellipse([bx - 11, by + 31, bx + 11, by + 53], fill=OUTLINE)
        d.ellipse([bx - 8, by + 34, bx + 8, by + 50], fill=(253, 224, 71, 255))

    # Pine sprigs fanning out from corner bow
    for ang, ln, wd in ((8, 125, 42), (32, 132, 42), (60, 118, 40), (88, 108, 38), (-18, 98, 36)):
        _draw_leaf(d, 106, 78, ln, wd, ang, fill=(78, 152, 92, 255), hi=(124, 194, 128, 255), outline_w=5.0)

    # Big cute Christmas bow & holly berries
    _draw_kawaii_bow(d, 104, 76, sc=1.55)
    _draw_holly_berries(d, 174, 112, r=12)

    # Cute pastel snowflakes & golden stars
    _draw_snowflake(d, 274, 120, 20)
    _draw_4star(d, 378, 112, 18)
    _draw_4star(d, 560, 96, 15)

    return im.resize((380, 140), Image.LANCZOS)


def build_xmas_hero_tl() -> Image.Image:
    im = Image.new("RGBA", (360, 360), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for ang, ln, wd in ((6, 138, 46), (34, 142, 46), (62, 136, 44), (86, 126, 42)):
        _draw_leaf(d, 64, 62, ln, wd, ang, fill=(78, 152, 92, 255), hi=(124, 194, 128, 255), outline_w=5.5)
    _draw_kawaii_bow(d, 74, 72, sc=1.45)
    _draw_holly_berries(d, 132, 126, r=13)
    _draw_snowflake(d, 232, 54, 22)
    _draw_4star(d, 56, 236, 20)
    return im.resize((180, 180), Image.LANCZOS)


def build_blossom_banner_tl(kind: str) -> Image.Image:
    # kind: "apricot" (Hoa Mai Vàng) or "sakura" (Hoa Đào / Anh Đào)
    im = Image.new("RGBA", (760, 280), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    if kind == "apricot":
        p_c, p_hi, c_c = (252, 211, 77, 255), (254, 243, 199, 255), (234, 88, 12, 255)
        leaf_c, leaf_hi = (106, 174, 96, 255), (154, 212, 132, 255)
    else:
        p_c, p_hi, c_c = (249, 168, 212, 255), (253, 232, 242, 255), (219, 39, 119, 255)
        leaf_c, leaf_hi = (116, 182, 118, 255), (166, 218, 158, 255)

    # Main curved branch sweeping gracefully from top-left
    b_main = _cubic_bezier((8, 26), (170, 14), (360, 96), (676, 48), steps=200)
    b_sub1 = _cubic_bezier((155, 36), (190, 96), (225, 148), (274, 174), steps=120)
    b_sub2 = _cubic_bezier((350, 66), (420, 108), (470, 126), (528, 122), steps=120)
    _draw_tapered_branch(d, b_main, 16, 5.5, outline_w=5.0)
    _draw_tapered_branch(d, b_sub1, 10, 4.5, outline_w=4.5)
    _draw_tapered_branch(d, b_sub2, 9, 4.0, outline_w=4.5)

    # Fresh spring leaves
    for (lx, ly, ln, wd, ang) in (
        (110, 44, 72, 28, 130),
        (256, 52, 68, 26, -32),
        (430, 62, 66, 26, -24),
        (560, 56, 62, 24, 34),
    ):
        _draw_leaf(d, lx, ly, ln, wd, ang, fill=leaf_c, hi=leaf_hi, outline_w=4.5)

    # Cute mini festive lantern hanging from lower twig
    _draw_mini_lantern(d, 264, 198, scale=1.55)

    # Clusters of kawaii 5-petal blossoms along branches
    for (bx, by, br, rot) in (
        (68, 56, 42, 12),
        (158, 46, 36, 38),
        (216, 112, 34, 18),
        (332, 64, 44, 24),
        (454, 106, 36, 8),
        (522, 68, 34, 42),
        (634, 52, 30, 15),
    ):
        _draw_blossom(d, bx, by, br, p_c, p_hi, c_c, outline_w=4.5, rot_deg=rot)

    # Tiny floating petals & golden sparkles
    _draw_4star(d, 128, 152, 17)
    _draw_4star(d, 388, 144, 16)
    _draw_4star(d, 696, 84, 15)
    for (px, py) in ((334, 158), (576, 132), (170, 214)):
        d.ellipse([px - 10, py - 6, px + 10, py + 6], fill=p_c, outline=OUTLINE, width=3)

    return im.resize((380, 140), Image.LANCZOS)


def build_blossom_hero_tl(kind: str) -> Image.Image:
    im = Image.new("RGBA", (360, 360), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if kind == "apricot":
        p_c, p_hi, c_c = (252, 211, 77, 255), (254, 243, 199, 255), (234, 88, 12, 255)
    else:
        p_c, p_hi, c_c = (249, 168, 212, 255), (253, 232, 242, 255), (219, 39, 119, 255)

    b1 = _cubic_bezier((12, 24), (96, 36), (178, 52), (264, 34), steps=36)
    b2 = _cubic_bezier((34, 32), (56, 116), (62, 186), (44, 252), steps=36)
    _draw_tapered_branch(d, b1, 14, 5.0, outline_w=5.0)
    _draw_tapered_branch(d, b2, 12, 4.5, outline_w=5.0)

    _draw_leaf(d, 128, 44, 68, 26, 26, outline_w=4.5)
    _draw_leaf(d, 58, 148, 66, 26, 72, outline_w=4.5)

    for (bx, by, br, rot) in (
        (68, 58, 48, 10),
        (166, 48, 38, 35),
        (64, 152, 40, 22),
        (246, 38, 30, 5),
        (48, 236, 30, 40),
    ):
        _draw_blossom(d, bx, by, br, p_c, p_hi, c_c, outline_w=4.5, rot_deg=rot)

    _draw_4star(d, 152, 140, 18)
    return im.resize((180, 180), Image.LANCZOS)


def main():
    DECOR_DIR.mkdir(parents=True, exist_ok=True)
    items = {
        "xmas_banner_tl.png": build_xmas_banner_tl(),
        "xmas_hero_tl.png": build_xmas_hero_tl(),
        "ny_apricot_banner_tl.png": build_blossom_banner_tl("apricot"),
        "ny_apricot_hero_tl.png": build_blossom_hero_tl("apricot"),
        "ny_sakura_banner_tl.png": build_blossom_banner_tl("sakura"),
        "ny_sakura_hero_tl.png": build_blossom_hero_tl("sakura"),
    }
    for name, im in list(items.items()):
        im.save(DECOR_DIR / name, "PNG", optimize=True)
        # Create mirrored top-right variant automatically
        tr_name = name.replace("_tl.png", "_tr.png")
        im.transpose(Image.FLIP_LEFT_RIGHT).save(DECOR_DIR / tr_name, "PNG", optimize=True)
        print(f"  [DECOR] {name} + {tr_name} ({im.size[0]}x{im.size[1]})")


if __name__ == "__main__":
    main()
