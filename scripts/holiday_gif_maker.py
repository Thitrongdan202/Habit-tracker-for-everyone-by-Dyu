"""
holiday_gif_maker.py — Generates lightweight, silky-smooth animated `.gif` previews
for Holiday Themes (#81–#95) using Pillow (ZERO AI quota!):

  1. Individual animated GIFs (`260x260`, 14 frames, < 220 KB each) for all ready themes:
       assets/previews/holiday/<num>_<slug>_fx.gif
     - Squash-and-stretch cheerful bouncing S5 character
     - Corner festive decor (Christmas ribbon/pine or New Year Hoa Mai / Hoa Đào)
     - Falling wavy snowflakes + twinkling gold stars (#81–#88)
     - Bursting mini fireworks + diagonal drifting petals + gold glints (#89–#95)

  2. Two Grand Showcase GIFs (`640x380`, 18 frames, lightweight for GitHub README):
       assets/previews/holiday/holiday_christmas_fx_preview.gif
       assets/previews/holiday/holiday_newyear_fx_preview.gif
     - Mockup of the live Habit Tracker Pro header (with ribbons / apricot & sakura branches),
       Hero card at 100%, mini habit checklist, full animated Holiday Finale FX, and
       bottom-left Vietnamese Celebration Toast pill!
"""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT / "assets"
DECOR_DIR = ASSETS_DIR / "_holiday_decor"
OUT_DIR = ASSETS_DIR / "previews" / "holiday"

# (num, slug, title, kind, sub_kind, bg_rgb, accent_rgb, soft_rgb)
HOLIDAY_THEMES = [
    (81, "xmas_tree_glow",          "Christmas Tree Glow",     "xmas",    "snow",    (244, 250, 246), (27, 107, 68),  (226, 244, 232)),
    (82, "xmas_snowman_build",      "Cozy Snowman Build",      "xmas",    "snow",    (243, 249, 254), (45, 114, 168), (224, 239, 252)),
    (83, "xmas_gingerbread_bakery", "Gingerbread Bakery",      "xmas",    "snow",    (253, 247, 240), (163, 86, 42),  (249, 234, 218)),
    (84, "xmas_santa_delivery",     "Santa Gift Delivery",     "xmas",    "snow",    (255, 245, 246), (186, 38, 52),  (254, 226, 229)),
    (85, "xmas_hot_cocoa_cafe",     "Winter Hot Cocoa Cafe",   "xmas",    "snow",    (252, 246, 242), (125, 74, 52),  (245, 232, 223)),
    (86, "xmas_reindeer_parade",    "Reindeer Bell Parade",    "xmas",    "snow",    (254, 248, 242), (176, 62, 46),  (252, 234, 224)),
    (87, "xmas_cozy_village",       "Christmas Snow Village",  "xmas",    "snow",    (244, 247, 253), (52, 86, 139),  (226, 234, 249)),
    (88, "xmas_wreath_candle",      "Wreath & Candle",         "xmas",    "snow",    (246, 250, 245), (42, 112, 74),  (228, 243, 229)),
    (89, "ny_fireworks_countdown",  "Fireworks Countdown",     "newyear", "apricot", (245, 244, 253), (76, 56, 158),  (232, 229, 250)),
    (90, "ny_lucky_red_envelope",   "Lucky Red Envelope",      "newyear", "apricot", (255, 246, 244), (192, 42, 42),  (254, 228, 224)),
    (91, "ny_maneki_neko",          "Maneki Neko Fortune",     "newyear", "apricot", (255, 248, 242), (189, 54, 48),  (254, 234, 222)),
    (92, "ny_sakura_blossom",       "Sakura New Year",         "newyear", "sakura",  (255, 246, 249), (204, 78, 122), (253, 228, 238)),
    (93, "ny_daruma_wish",          "Daruma Wish Goal",        "newyear", "apricot", (254, 246, 244), (178, 34, 34),  (252, 228, 224)),
    (94, "ny_tea_mochi",            "Cozy Tea & Mochi",        "newyear", "sakura",  (246, 250, 244), (72, 122, 68),  (228, 242, 226)),
    (95, "ny_festival_lantern",     "New Year Festival",       "newyear", "sakura",  (255, 247, 242), (188, 52, 42),  (253, 232, 222)),
]

# Ready AI-drawn subset by default (pass "all" to process all 15 once #91,#93,#94,#95 are ready)
READY_DEFAULT = {81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 92}


def _draw_4star(draw: ImageDraw.ImageDraw, cx: float, cy: float, r: float, fill, outline=None):
    if r < 1.2:
        return
    ri = r * 0.34
    pts = []
    for i in range(8):
        a = math.radians(i * 45.0 - 90.0)
        rad = r if i % 2 == 0 else ri
        pts.append((cx + math.cos(a) * rad, cy + math.sin(a) * rad))
    draw.polygon(pts, fill=fill, outline=outline)


def _draw_snowflake(draw: ImageDraw.ImageDraw, cx: float, cy: float, r: float, col=(255, 255, 255, 235), rim=(147, 197, 253, 210)):
    for k in range(3):
        a = math.radians(k * 60.0)
        dx, dy = math.cos(a) * r, math.sin(a) * r
        draw.line([(cx - dx, cy - dy), (cx + dx, cy + dy)], fill=rim, width=2)
        draw.line([(cx - dx, cy - dy), (cx + dx, cy + dy)], fill=col, width=1)
    draw.ellipse([cx - 1.5, cy - 1.5, cx + 1.5, cy + 1.5], fill=col)


def _draw_petal(draw: ImageDraw.ImageDraw, cx: float, cy: float, r: float, ang_deg: float, fill, outline=(120, 62, 54, 170)):
    a = math.radians(ang_deg)
    ca, sa = math.cos(a), math.sin(a)
    pts = []
    for i in range(10):
        th = (i / 10.0) * 2.0 * math.pi
        px = math.cos(th) * r * 1.25
        py = math.sin(th) * r * 0.68
        pts.append((cx + px * ca - py * sa, cy + px * sa + py * ca))
    draw.polygon(pts, fill=fill, outline=outline)


def _draw_firework(draw: ImageDraw.ImageDraw, cx: float, cy: float, progress: float, max_r: float, colors: list[tuple[int, int, int]]):
    """progress in [0..1]: expands radially, brightens then fades into dainty sparks."""
    if progress <= 0.02 or progress >= 0.98:
        return
    alpha = int(255 * math.sin(progress * math.pi) ** 0.75)
    n_rays = 12
    r_now = max_r * (1.0 - (1.0 - progress) ** 2.2)
    r_tail = max(0.0, r_now * 0.52)
    for k in range(n_rays):
        ang = (k / n_rays) * 2.0 * math.pi + 0.15
        col = colors[k % len(colors)] + (alpha,)
        x1 = cx + math.cos(ang) * r_tail
        y1 = cy + math.sin(ang) * r_tail + (progress ** 2) * 8.0
        x2 = cx + math.cos(ang) * r_now
        y2 = cy + math.sin(ang) * r_now + (progress ** 2) * 12.0
        draw.line([(x1, y1), (x2, y2)], fill=col, width=2)
        dot_r = 2.6 * (1.0 - 0.45 * progress)
        draw.ellipse([x2 - dot_r, y2 - dot_r, x2 + dot_r, y2 + dot_r], fill=col)


def _quantize_frames(frames_rgb: list[Image.Image], colors: int = 128) -> list[Image.Image]:
    # Build one shared global palette from a vertical strip of sampled frames -> zero palette flicker & super small size!
    sample = frames_rgb[::max(1, len(frames_rgb) // 4)]
    w, h = sample[0].size
    strip = Image.new("RGB", (w, h * len(sample)))
    for i, fr in enumerate(sample):
        strip.paste(fr, (0, i * h))
    pal_img = strip.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    return [fr.quantize(palette=pal_img, dither=Image.Dither.FLOYDSTEINBERG) for fr in frames_rgb]


def build_theme_gif(num: int, slug: str, kind: str, sub_kind: str, bg_rgb, acc_rgb, soft_rgb) -> Path:
    s5_path = ASSETS_DIR / slug / "stage_5.png"
    assert s5_path.exists(), f"Missing {s5_path}"
    sprite = Image.open(s5_path).convert("RGBA")

    if kind == "xmas":
        d_tl = Image.open(DECOR_DIR / "xmas_hero_tl.png").convert("RGBA").resize((58, 58), Image.LANCZOS)
        d_tr = Image.open(DECOR_DIR / "xmas_hero_tr.png").convert("RGBA").resize((58, 58), Image.LANCZOS)
    elif sub_kind == "apricot":
        d_tl = Image.open(DECOR_DIR / "ny_apricot_hero_tl.png").convert("RGBA").resize((60, 60), Image.LANCZOS)
        d_tr = Image.open(DECOR_DIR / "ny_apricot_hero_tr.png").convert("RGBA").resize((60, 60), Image.LANCZOS)
    else:
        d_tl = Image.open(DECOR_DIR / "ny_sakura_hero_tl.png").convert("RGBA").resize((60, 60), Image.LANCZOS)
        d_tr = Image.open(DECOR_DIR / "ny_sakura_hero_tr.png").convert("RGBA").resize((60, 60), Image.LANCZOS)

    S = 240
    N_FRAMES = 12
    rnd = random.Random(num * 101)

    # Pre-seed particles for seamless cyclic loop!
    flakes = [(rnd.uniform(14, S - 14), rnd.uniform(0, S), rnd.uniform(3.2, 6.0), rnd.uniform(0, 6.28)) for _ in range(14)]
    stars = [(rnd.uniform(22, S - 22), rnd.uniform(22, S - 36), rnd.uniform(4.5, 8.5), rnd.uniform(0, 6.28)) for _ in range(9)]
    petals = [(rnd.uniform(0, S), rnd.uniform(0, S), rnd.uniform(4.2, 6.8), rnd.uniform(0, 360)) for _ in range(12)]
    fw_centers = [(54, 56, 0.0), (208, 62, 0.35), (132, 42, 0.68)]
    fw_cols = [(239, 68, 68), (245, 158, 11), (244, 114, 182), (139, 92, 246), (56, 189, 248)]

    frames: list[Image.Image] = []
    for f in range(N_FRAMES):
        u = f / N_FRAMES  # 0 .. 1 cyclic
        base = Image.new("RGBA", (S, S), bg_rgb + (255,))
        d = ImageDraw.Draw(base, "RGBA")

        # Subtle soft card border & inner halo
        d.rounded_rectangle([4, 4, S - 5, S - 5], radius=22, fill=bg_rgb + (255,), outline=acc_rgb + (180,), width=3)
        glow_r = int(86 + 6 * math.sin(u * 2.0 * math.pi))
        d.ellipse([S // 2 - glow_r, S // 2 - glow_r + 6, S // 2 + glow_r, S // 2 + glow_r + 6], fill=soft_rgb + (170,))

        # Background fireworks (for New Year)
        if kind == "newyear":
            for (fx, fy, ph) in fw_centers:
                prog = (u + ph) % 1.0
                _draw_firework(d, fx, fy, prog, 38.0, fw_cols)

        # Corner holiday decorations
        base.alpha_composite(d_tl, (8, 8))
        base.alpha_composite(d_tr, (S - 8 - d_tr.width, 8))

        # Cute squash & stretch bouncy S5 character
        bounce = abs(math.sin(u * 2.0 * math.pi))
        sx = 1.0 + 0.045 * math.cos(u * 4.0 * math.pi)
        sy = 1.0 - 0.045 * math.cos(u * 4.0 * math.pi)
        sp_w = int(round(172 * sx))
        sp_h = int(round(172 * sy))
        dy = int(round(-9.0 * bounce))
        sp_im = sprite.resize((sp_w, sp_h), Image.LANCZOS)
        # Soft ground shadow shrinks as character hops
        sh_w = int(62 - 9 * bounce)
        d.ellipse([S // 2 - sh_w, 206, S // 2 + sh_w, 219], fill=(120, 100, 95, 38))
        base.alpha_composite(sp_im, ((S - sp_w) // 2, 210 - sp_h + dy))

        # Foreground seasonal particles
        if kind == "xmas":
            for (fx0, fy0, fr, ph) in flakes:
                fy = (fy0 + u * S) % S
                fx = (fx0 + math.sin(u * 2.0 * math.pi + ph) * 10.0) % S
                _draw_snowflake(d, fx, fy, fr)
            for (sx0, sy0, sr, ph) in stars:
                pulse = 0.45 + 0.55 * abs(math.sin(u * 2.0 * math.pi + ph))
                _draw_4star(d, sx0, sy0, sr * pulse, (251, 191, 36, 240), outline=(180, 110, 20, 180))
        else:
            p_fill = (252, 211, 77, 235) if sub_kind == "apricot" else (249, 168, 212, 235)
            for (px0, py0, pr, ang0) in petals:
                px = (px0 + u * S * 0.65) % S
                py = (py0 + u * S) % S
                _draw_petal(d, px, py, pr, ang0 + u * 360.0, p_fill)
            for (sx0, sy0, sr, ph) in stars:
                pulse = 0.45 + 0.55 * abs(math.sin(u * 2.0 * math.pi + ph))
                _draw_4star(d, sx0, sy0, sr * pulse, (253, 224, 71, 240), outline=(185, 85, 25, 180))

        frames.append(base.convert("RGB"))

    q_frames = _quantize_frames(frames, colors=96)
    out_p = OUT_DIR / f"{num:02d}_{slug}_fx.gif"
    q_frames[0].save(
        out_p, save_all=True, append_images=q_frames[1:],
        duration=90, loop=0, optimize=True, disposal=2,
    )
    return out_p


def build_showcase_gif(kind: str) -> Path:
    """Build grand 640x380 tracker + Holiday Finale FX showcase GIF for README / user preview."""
    W, H = 640, 380
    N_FRAMES = 15
    f_hdr = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 19)
    f_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 12)
    f_lbl = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 12)
    f_big = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 28)
    f_tst = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 12)

    if kind == "xmas":
        page_c = (252, 248, 246)
        pri_c = (178, 38, 52)
        soft_c = (253, 232, 234)
        ink_c = (68, 36, 40)
        b_tl = Image.open(DECOR_DIR / "xmas_banner_tl.png").convert("RGBA").resize((136, 50), Image.LANCZOS)
        b_tr = Image.open(DECOR_DIR / "xmas_banner_tr.png").convert("RGBA").resize((136, 50), Image.LANCZOS)
        h_tl = Image.open(DECOR_DIR / "xmas_hero_tl.png").convert("RGBA").resize((48, 48), Image.LANCZOS)
        sp_main = Image.open(ASSETS_DIR / "xmas_tree_glow" / "stage_5.png").convert("RGBA")
        sp_side = Image.open(ASSETS_DIR / "xmas_santa_delivery" / "stage_5.png").convert("RGBA")
        banner_txt = "CHRISTMAS PRO EDITION • WINTER MAGIC FINALE"
        toast_txt = "Giang Sinh An Lanh! Hoan thanh 100% muc tieu hom nay!"
        toast_vn = "Giáng Sinh An Lành! Hoàn thành 100% mục tiêu hôm nay!"
        out_p = OUT_DIR / "holiday_christmas_fx_preview.gif"
    else:
        page_c = (255, 248, 244)
        pri_c = (192, 42, 42)
        soft_c = (254, 234, 224)
        ink_c = (74, 34, 34)
        b_tl = Image.open(DECOR_DIR / "ny_apricot_banner_tl.png").convert("RGBA").resize((142, 52), Image.LANCZOS)
        b_tr = Image.open(DECOR_DIR / "ny_sakura_banner_tr.png").convert("RGBA").resize((142, 52), Image.LANCZOS)
        h_tl = Image.open(DECOR_DIR / "ny_apricot_hero_tl.png").convert("RGBA").resize((48, 48), Image.LANCZOS)
        sp_main = Image.open(ASSETS_DIR / "ny_lucky_red_envelope" / "stage_5.png").convert("RGBA")
        sp_side = Image.open(ASSETS_DIR / "ny_maneki_neko" / "stage_5.png").convert("RGBA")
        ny_strip = [
            Image.open(ASSETS_DIR / s / "stage_5.png").convert("RGBA").resize((36, 36), Image.LANCZOS)
            for s in ("ny_fireworks_countdown", "ny_lucky_red_envelope", "ny_maneki_neko",
                      "ny_sakura_blossom", "ny_daruma_wish", "ny_tea_mochi", "ny_festival_lantern")
            if (ASSETS_DIR / s / "stage_5.png").exists()
        ]
        banner_txt = "NEW YEAR PRO EDITION • GRAND FIREWORKS FINALE"
        toast_vn = "Khai Xuân Rực Rỡ! Chúc mừng đạt 100% — Vạn Sự Như Ý!"
        out_p = OUT_DIR / "holiday_newyear_fx_preview.gif"

    rnd = random.Random(2026 if kind == "xmas" else 2027)
    flakes = [(rnd.uniform(16, W - 16), rnd.uniform(0, H), rnd.uniform(3.5, 7.0), rnd.uniform(0, 6.28)) for _ in range(28)]
    petals = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(4.5, 7.5), rnd.uniform(0, 360), i % 2) for i in range(26)]
    fw_specs = [(115, 118, 0.0, 56), (325, 96, 0.25, 64), (530, 122, 0.50, 58), (225, 138, 0.72, 52)]
    fw_cols = [(239, 68, 68), (251, 191, 36), (244, 114, 182), (167, 139, 250), (56, 189, 248)]

    frames: list[Image.Image] = []
    for f in range(N_FRAMES):
        u = f / N_FRAMES
        im = Image.new("RGBA", (W, H), page_c + (255,))
        d = ImageDraw.Draw(im, "RGBA")

        # 1. Top Header Banner
        d.rounded_rectangle([12, 10, W - 12, 62], radius=12, fill=pri_c + (255,))
        tb = d.textbbox((0, 0), banner_txt, font=f_hdr)
        d.text(((W - (tb[2] - tb[0])) // 2, 24), banner_txt, fill=(255, 255, 255, 255), font=f_hdr)
        im.alpha_composite(b_tl, (12, 10))
        im.alpha_composite(b_tr, (W - 12 - b_tr.width, 10))

        # 2. Left Hero Card (100% MAX)
        d.rounded_rectangle([16, 76, 224, 312], radius=14, fill=(255, 255, 255, 255), outline=pri_c + (160,), width=2)
        d.rounded_rectangle([24, 84, 216, 110], radius=8, fill=soft_c + (255,))
        d.text((52, 90), "HERO • 100% MAX!", fill=pri_c + (255,), font=f_lbl)
        im.alpha_composite(h_tl, (18, 112))
        bounce = abs(math.sin(u * 2.0 * math.pi))
        sx = 1.0 + 0.05 * math.cos(u * 4.0 * math.pi)
        sy = 1.0 - 0.05 * math.cos(u * 4.0 * math.pi)
        mw, mh = int(146 * sx), int(146 * sy)
        sp_m = sp_main.resize((mw, mh), Image.LANCZOS)
        im.alpha_composite(sp_m, (120 - mw // 2, 274 - mh - int(9 * bounce)))
        d.text((88, 282), "100%", fill=pri_c + (255,), font=f_big)

        # 3. Right Mini Habit Grid + Companion Card
        d.rounded_rectangle([238, 76, W - 16, 218], radius=14, fill=(255, 255, 255, 255), outline=pri_c + (120,), width=2)
        d.rounded_rectangle([246, 84, W - 24, 108], radius=7, fill=soft_c + (255,))
        d.text((258, 89), "DAILY HABIT CHECKLIST • PERFECT DAY 100%", fill=ink_c + (255,), font=f_lbl)
        habits = ["Uong du 2L nuoc", "Tap the duc 30p", "Doc sach 20 phut", "Ngu som truoc 23h"]
        habits_vn = ["Uống đủ 2L nước", "Tập thể dục 30p", "Đọc sách 20 phút", "Ngủ sớm trước 23h"]
        for hi, htxt in enumerate(habits_vn):
            ry = 118 + hi * 23
            d.text((256, ry), htxt, fill=ink_c + (255,), font=f_sub)
            for ci in range(7):
                cx0 = 398 + ci * 30
                checked = not (hi == 3 and ci == 6 and f < 3)
                fill_cb = pri_c + (255,) if checked else (235, 232, 235, 255)
                d.rounded_rectangle([cx0, ry, cx0 + 18, ry + 16], radius=4, fill=fill_cb)
                if checked:
                    d.line([(cx0 + 4, ry + 8), (cx0 + 8, ry + 12), (cx0 + 14, ry + 4)], fill=(255, 255, 255, 255), width=2)

        # Companion mini preview card (bottom-right)
        d.rounded_rectangle([238, 230, W - 16, 312], radius=14, fill=(255, 255, 255, 255), outline=pri_c + (120,), width=2)
        sp_s = sp_side.resize((72, 72), Image.LANCZOS)
        im.alpha_composite(sp_s, (250, 236 - int(4 * bounce)))
        d.text((334, 240), "PRO MACRO EXCLUSIVE FX", fill=pri_c + (255,), font=f_lbl)
        sub_line = ("Tuyết rơi đa tầng + Sao lấp lánh + Toast góc trái dưới"
                    if kind == "xmas" else "Pháo hoa 4 đợt + Cánh Mai/Đào bay + 7 Chủ Đề Năm Mới")
        d.text((334, 258), sub_line, fill=ink_c + (255,), font=f_sub)
        if kind == "newyear" and ny_strip:
            for si, mini in enumerate(ny_strip):
                im.alpha_composite(mini, (334 + si * 40, 274 - int(2 * abs(math.sin((u + si * 0.14) * 2.0 * math.pi)))))
        else:
            d.text((334, 280), "Bật/Tắt linh hoạt • Tự dọn sạch 100% shape tạm!", fill=(115, 105, 110, 255), font=f_sub)

        # 4. Animated Holiday FX Layer!
        if kind == "xmas":
            # Radial gold star & pastel bauble burst around Hero
            for k in range(10):
                ang = (k / 10.0) * 2.0 * math.pi + 0.2
                dist = 32.0 + 78.0 * ((u + 0.1) % 1.0)
                bx = 120 + math.cos(ang) * dist
                by = 195 + math.sin(ang) * dist
                if k % 2 == 0:
                    _draw_4star(d, bx, by, 7.5 * (1.0 - 0.35 * u), (251, 191, 36, 245))
                else:
                    bc = [(225, 29, 72, 230), (52, 211, 153, 230), (251, 191, 36, 230)][k % 3]
                    d.ellipse([bx - 5, by - 5, bx + 5, by + 5], fill=bc)
            # Multi-layer wavy snowfall across entire sheet
            for (fx0, fy0, fr, ph) in flakes:
                fy = (fy0 + u * H) % H
                fx = (fx0 + math.sin(u * 2.0 * math.pi + ph) * 14.0) % W
                _draw_snowflake(d, fx, fy, fr)
        else:
            # 4 staggered multi-color radial fireworks
            for (fx, fy, ph, mr) in fw_specs:
                _draw_firework(d, fx, fy, (u + ph) % 1.0, mr, fw_cols)
            # Diagonal drifting apricot & sakura petals
            for (px0, py0, pr, ang0, ptype) in petals:
                px = (px0 + u * W * 0.55) % W
                py = (py0 + u * H) % H
                pcol = (252, 211, 77, 235) if ptype == 0 else (249, 168, 212, 235)
                _draw_petal(d, px, py, pr, ang0 + u * 360.0, pcol)

        # 5. Bottom-Left Celebration Toast Pill (sliding smoothly into view!)
        slide = min(1.0, f / 3.0)
        tx = int(16 - 42 * (1.0 - slide))
        ty = H - 52
        d.rounded_rectangle([tx, ty, tx + 430, ty + 38], radius=18, fill=pri_c + (245,), outline=(254, 240, 138, 255), width=2)
        d.text((tx + 18, ty + 11), toast_vn, fill=(255, 255, 255, 255), font=f_tst)

        frames.append(im.convert("RGB"))

    q_frames = _quantize_frames(frames, colors=96)
    q_frames[0].save(
        out_p, save_all=True, append_images=q_frames[1:],
        duration=100, loop=0, optimize=True, disposal=2,
    )
    return out_p


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    run_all = ("all" in sys.argv[1:])
    target_nums = set(range(81, 96)) if run_all else READY_DEFAULT

    made = []
    for num, slug, title, kind, sub_kind, bg_rgb, acc_rgb, soft_rgb in HOLIDAY_THEMES:
        if num not in target_nums:
            continue
        p = build_theme_gif(num, slug, kind, sub_kind, bg_rgb, acc_rgb, soft_rgb)
        kb = p.stat().st_size / 1024.0
        made.append((p.name, kb))
        print(f"  [GIF] {p.name:<38} {kb:6.1f} KB", flush=True)

    for k in ("xmas", "newyear"):
        p = build_showcase_gif(k)
        kb = p.stat().st_size / 1024.0
        made.append((p.name, kb))
        print(f"  [SHOWCASE GIF] {p.name:<30} {kb:6.1f} KB", flush=True)

    print(f"=== GENERATED {len(made)} HOLIDAY ANIMATED GIFs in {OUT_DIR} ===")


if __name__ == "__main__":
    main()
