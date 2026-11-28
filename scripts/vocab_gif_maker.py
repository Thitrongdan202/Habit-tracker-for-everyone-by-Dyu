"""
vocab_gif_maker.py — Generates 5 lightweight animated Chiikawa Vocabulary GIF previews
(`240x240`, 12 frames, < 220 KB each) + 1 grand showcase GIF (`vocab_chiikawa_preview.gif`)
into `assets/previews/vocab/` using Python Pillow (0 AI quota!).
"""
from __future__ import annotations

import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT / "assets"
OUT_DIR = ASSETS_DIR / "previews" / "vocab"

VOCAB_THEMES = [
    (96,  "chiikawa_srs_vocab",    "Chiikawa SRS Daily",      "SRS 1-3-7-14-30d",    (255, 245, 248), (226, 113, 146), (255, 214, 224)),
    (97,  "hachiware_ielts_vocab", "Hachiware IELTS Study",   "Band 7.0–8.5",        (242, 249, 255), (43, 76, 126),   (207, 232, 255)),
    (98,  "usagi_flashcard_vocab", "Usagi Honey Flashcard",   "Quiz 2 Chiều",        (255, 251, 238), (217, 130, 54),  (255, 240, 184)),
    (99,  "momonga_media_vocab",   "Momonga Lavender Media",  "Phim • Nhạc • Truyện",(248, 244, 255), (140, 98, 184),  (229, 212, 255)),
    (100, "shisa_exam_vocab",      "Shisa Matcha Bookshop",   "Ôn Thi & Từ Hay Quên",(246, 251, 244), (76, 140, 90),   (216, 238, 217)),
]


def _draw_4star(draw, cx, cy, r, fill, outline=None):
    if r < 1.2:
        return
    ri = r * 0.34
    pts = []
    for i in range(8):
        a = math.radians(i * 45.0 - 90.0)
        rad = r if i % 2 == 0 else ri
        pts.append((cx + math.cos(a) * rad, cy + math.sin(a) * rad))
    draw.polygon(pts, fill=fill, outline=outline)


def _draw_heart(draw, cx, cy, r, fill):
    if r < 2:
        return
    draw.ellipse([cx - r, cy - r * 0.65, cx, cy + r * 0.35], fill=fill)
    draw.ellipse([cx, cy - r * 0.65, cx + r, cy + r * 0.35], fill=fill)
    draw.polygon([(cx - r * 0.96, cy - r * 0.05), (cx + r * 0.96, cy - r * 0.05), (cx, cy + r * 1.05)], fill=fill)


def _quantize_frames(frames_rgb: list[Image.Image], colors: int = 96) -> list[Image.Image]:
    sample = frames_rgb[::max(1, len(frames_rgb) // 4)]
    w, h = sample[0].size
    strip = Image.new("RGB", (w, h * len(sample)))
    for i, fr in enumerate(sample):
        strip.paste(fr, (0, i * h))
    pal_img = strip.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    return [fr.quantize(palette=pal_img, dither=Image.Dither.FLOYDSTEINBERG) for fr in frames_rgb]


def build_vocab_gif(num: int, slug: str, title: str, badge: str, bg_rgb, acc_rgb, soft_rgb) -> Path:
    s5 = Image.open(ASSETS_DIR / slug / "stage_5.png").convert("RGBA")
    S = 240
    N = 12
    f_badge = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 12)
    rnd = random.Random(num * 73)
    stars = [(rnd.uniform(22, S - 22), rnd.uniform(36, S - 32), rnd.uniform(4.5, 8.0), rnd.uniform(0, 6.28)) for _ in range(9)]
    hearts = [(rnd.uniform(20, S - 20), rnd.uniform(0, S), rnd.uniform(4.5, 6.5), rnd.uniform(0, 6.28)) for _ in range(7)]

    frames = []
    for f in range(N):
        u = f / N
        im = Image.new("RGBA", (S, S), bg_rgb + (255,))
        d = ImageDraw.Draw(im, "RGBA")
        d.rounded_rectangle([4, 4, S - 5, S - 5], radius=22, fill=bg_rgb + (255,), outline=acc_rgb + (190,), width=3)

        # Soft pastel halo
        gr = int(78 + 6 * math.sin(u * 2.0 * math.pi))
        d.ellipse([S // 2 - gr, S // 2 - gr + 12, S // 2 + gr, S // 2 + gr + 12], fill=soft_rgb + (175,))

        # Top pill badge
        tb = d.textbbox((0, 0), badge, font=f_badge)
        pw = (tb[2] - tb[0]) + 22
        px0 = (S - pw) // 2
        d.rounded_rectangle([px0, 11, px0 + pw, 33], radius=11, fill=acc_rgb + (240,))
        d.text((px0 + 11, 14), badge, fill=(255, 255, 255, 255), font=f_badge)

        # Bouncing Chiikawa friend (squash & stretch)
        bounce = abs(math.sin(u * 2.0 * math.pi))
        sx = 1.0 + 0.045 * math.cos(u * 4.0 * math.pi)
        sy = 1.0 - 0.045 * math.cos(u * 4.0 * math.pi)
        sw, sh = int(162 * sx), int(162 * sy)
        sp = s5.resize((sw, sh), Image.LANCZOS)
        sh_w = int(56 - 8 * bounce)
        d.ellipse([S // 2 - sh_w, 208, S // 2 + sh_w, 220], fill=(120, 95, 105, 36))
        im.alpha_composite(sp, ((S - sw) // 2, 212 - sh - int(9 * bounce)))

        # Floating pastel hearts & twinkling stars
        for (hx0, hy0, hr, ph) in hearts:
            hy = (hy0 - u * S) % S
            hx = (hx0 + math.sin(u * 2.0 * math.pi + ph) * 8.0) % S
            _draw_heart(d, hx, hy, hr, acc_rgb + (165,))
        for (sx0, sy0, sr, ph) in stars:
            pulse = 0.45 + 0.55 * abs(math.sin(u * 2.0 * math.pi + ph))
            _draw_4star(d, sx0, sy0, sr * pulse, (253, 224, 71, 240), outline=(180, 120, 30, 160))

        frames.append(im.convert("RGB"))

    q = _quantize_frames(frames, colors=96)
    out_p = OUT_DIR / f"{num:02d}_{slug}_fx.gif"
    q[0].save(out_p, save_all=True, append_images=q[1:], duration=90, loop=0, optimize=True, disposal=2)
    return out_p


def build_vocab_showcase_gif() -> Path:
    W, H = 640, 380
    N = 15
    f_hdr = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 19)
    f_lbl = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 12)
    f_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 12)
    f_w = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 13)
    f_tst = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 12)

    sprites = [Image.open(ASSETS_DIR / t[1] / "stage_5.png").convert("RGBA") for t in VOCAB_THEMES]
    cards = [
        ("SRS 5 Mốc", "Chiikawa", (255, 214, 224), (196, 82, 114)),
        ("IELTS Band 8+", "Hachiware", (207, 232, 255), (43, 76, 126)),
        ("Quiz 2 Chiều", "Usagi", (255, 240, 184), (176, 102, 42)),
        ("Đa Ngôn Ngữ", "Momonga", (229, 212, 255), (104, 72, 152)),
        ("Từ Hay Quên", "Shisa", (216, 238, 217), (62, 118, 72)),
    ]

    rnd = random.Random(96100)
    petals = [(rnd.uniform(10, W - 10), rnd.uniform(0, H), rnd.uniform(4.5, 7.0), rnd.uniform(0, 6.28), i % 5) for i in range(22)]
    p_cols = [(255, 182, 193, 215), (147, 197, 253, 215), (253, 224, 71, 215), (216, 180, 254, 215), (167, 243, 208, 215)]

    frames = []
    for f in range(N):
        u = f / N
        im = Image.new("RGBA", (W, H), (255, 249, 251, 255))
        d = ImageDraw.Draw(im, "RGBA")

        # Header bar
        d.rounded_rectangle([12, 10, W - 12, 58], radius=12, fill=(222, 104, 142, 255))
        hdr = "CHIIKAWA & FRIENDS • 5 VOCABULARY TRACKERS (#96–#100)"
        tb = d.textbbox((0, 0), hdr, font=f_hdr)
        d.text(((W - (tb[2] - tb[0])) // 2, 22), hdr, fill=(255, 255, 255, 255), font=f_hdr)

        # Row of 5 distinct Chiikawa character cards
        cw = 114
        gap = 10
        x_start = (W - (5 * cw + 4 * gap)) // 2
        for idx, (mode_lbl, ch_nm, s_col, a_col) in enumerate(cards):
            x0 = x_start + idx * (cw + gap)
            y0 = 70
            d.rounded_rectangle([x0, y0, x0 + cw, y0 + 132], radius=12, fill=(255, 255, 255, 255), outline=a_col + (180,), width=2)
            d.rounded_rectangle([x0 + 6, y0 + 6, x0 + cw - 6, y0 + 28], radius=7, fill=s_col + (255,))
            tb_m = d.textbbox((0, 0), mode_lbl, font=f_lbl)
            d.text((x0 + (cw - (tb_m[2] - tb_m[0])) // 2, y0 + 9), mode_lbl, fill=a_col + (255,), font=f_lbl)
            b = abs(math.sin((u + idx * 0.2) * 2.0 * math.pi))
            sp = sprites[idx].resize((78, 78), Image.LANCZOS)
            im.alpha_composite(sp, (x0 + (cw - 78) // 2, y0 + 34 - int(5 * b)))
            tb_c = d.textbbox((0, 0), ch_nm, font=f_sub)
            d.text((x0 + (cw - (tb_c[2] - tb_c[0])) // 2, y0 + 112), ch_nm, fill=(85, 65, 75, 255), font=f_sub)

        # Interactive Flashcard & Quiz Toggle preview strip
        d.rounded_rectangle([16, 214, W - 16, 314], radius=14, fill=(255, 255, 255, 255), outline=(222, 104, 142, 140), width=2)
        quiz_hide = (f >= 4 and f <= 10)
        pill_c = (222, 104, 142, 255) if quiz_hide else (240, 236, 240, 255)
        pill_t = (255, 255, 255, 255) if quiz_hide else (90, 75, 85, 255)
        d.rounded_rectangle([28, 224, 242, 248], radius=10, fill=pill_c)
        d.text((40, 229), "Chế độ Dò Bài (Ẩn Nghĩa): " + ("BẬT" if quiz_hide else "TẮT"), fill=pill_t, font=f_lbl)
        d.text((258, 229), "VBA Flashcard Pop-up • SRS 5 Mốc • IELTS • Đa Ngôn Ngữ", fill=(100, 78, 92, 255), font=f_sub)

        demo_rows = [
            ("serendipity", "/ˌser.ənˈdɪp.ə.ti/", "Sự tình cờ may mắn kỳ diệu"),
            ("mitigate",    "/ˈmɪt.ɪ.ɡeɪt/",     "Giảm nhẹ rủi ro (IELTS 8.0)"),
        ]
        for ri, (w, ipa, mean) in enumerate(demo_rows):
            ry = 258 + ri * 26
            d.rounded_rectangle([28, ry, 180, ry + 21], radius=5, fill=(255, 244, 247, 255))
            d.text((36, ry + 3), w, fill=(92, 64, 51, 255), font=f_w)
            d.text((190, ry + 4), ipa, fill=(120, 105, 115, 255), font=f_sub)
            m_bg = (255, 214, 224, 255) if quiz_hide else (248, 250, 252, 255)
            d.rounded_rectangle([328, ry, W - 28, ry + 21], radius=5, fill=m_bg)
            if quiz_hide:
                d.text((342, ry + 4), "• • •  Đang ẩn để dò bài...  • • •", fill=(196, 82, 114, 255), font=f_sub)
            else:
                d.text((340, ry + 3), mean, fill=(62, 48, 56, 255), font=f_sub)

        # Pastel falling sparkles & hearts
        for (px0, py0, pr, ph, ci) in petals:
            py = (py0 + u * H) % H
            px = (px0 + math.sin(u * 2.0 * math.pi + ph) * 10.0) % W
            _draw_4star(d, px, py, pr, p_cols[ci])

        # Bottom-left motivational Toast (strictly >= 20px left margin on ALL frames, zero clipping!)
        toast_msg = "Chiikawa cổ vũ! Bạn đã hoàn thành 100% mục tiêu từ vựng hôm nay!"
        tb_t = d.textbbox((0, 0), toast_msg, font=f_tst)
        tw = tb_t[2] - tb_t[0]
        th = tb_t[3] - tb_t[1]
        tx = 20
        pad_x = 20
        bw = min(W - 40, tw + pad_x * 2)
        bob = int(round(math.sin(u * 2.0 * math.pi) * 2.0))
        ty0 = H - 52 + bob
        ty1 = ty0 + 38
        d.rounded_rectangle(
            [tx, ty0, tx + bw, ty1],
            radius=18,
            fill=(196, 82, 114, 248),
            outline=(255, 232, 240, 255),
            width=2,
        )
        text_x = tx + (bw - tw) // 2 - tb_t[0]
        text_y = ty0 + (38 - th) // 2 - tb_t[1]
        d.text((text_x, text_y), toast_msg, fill=(255, 255, 255, 255), font=f_tst)

        frames.append(im.convert("RGB"))

    q = _quantize_frames(frames, colors=96)
    out_p = OUT_DIR / "vocab_chiikawa_preview.gif"
    q[0].save(out_p, save_all=True, append_images=q[1:], duration=105, loop=0, optimize=True, disposal=2)
    return out_p


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for num, slug, title, badge, bg, acc, soft in VOCAB_THEMES:
        p = build_vocab_gif(num, slug, title, badge, bg, acc, soft)
        print(f"  [VOCAB GIF] {p.name:<36} {p.stat().st_size / 1024.0:6.1f} KB", flush=True)
    sp = build_vocab_showcase_gif()
    print(f"  [VOCAB SHOWCASE] {sp.name:<31} {sp.stat().st_size / 1024.0:6.1f} KB", flush=True)


if __name__ == "__main__":
    main()
