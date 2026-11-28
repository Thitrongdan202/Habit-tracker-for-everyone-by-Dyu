"""
process_holiday_ai_sprites.py — Splits 3x2 AI kawaii chibi sticker sheets (#81–#95)
into spotless 500x500 transparent RGBA PNGs (10% breathing margin, zero white fringe,
zero jagged edges) and builds the 2 high-res Contact Sheets with 44px preview boxes.

Algorithm (Studio-Grade Sticker Background Removal):
  1. Smart Valley Splitting: locates the cleanest pure-white horizontal & vertical
     gutters near W/3, 2W/3, H/2 so no sparkle or accessory is ever clipped.
  2. Exterior BFS Flood-Fill: starts from all border pixels of each cell and floods
     contiguous near-white background pixels (handling JPEG compression noise cleanly
     while 100% preserving white interiors enclosed by the thick dark-brown outline,
     such as snowmen, Santa beard, marshmallows, whipped cream, snow roofs, mochi).
  3. Selective Interior-Hole Punching: for open-loop subjects (e.g. mug handle #85,
     wreath inner ring #88, sleigh runner gaps #84, clock bell/leg gaps #89, bonsai
     branch openings #92, lantern/tray gaps), cleanly punches interior pure-white
     holes that are NOT shaded snow/fur/cream.
  4. Anti-Alias Fringe Decontamination: un-premultiplies white background blend on
     boundary pixels within 2px of transparency so edges stay silky smooth on both
     white AND pastel/dark Excel backgrounds (zero white/gray halo!).
  5. Uniform 500x500 RGBA centering with 10% padding (matching 10-12% spec).
"""
from __future__ import annotations

import hashlib
import sys
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT / "assets"
PREVIEWS_DIR = ROOT / "previews"
BRAIN_DIR = Path(r"C:\Users\thitr\.gemini\antigravity\brain\b0a27be6-6fdd-42d5-82d0-34023ae2cffc")

# Theme definitions: (num, slug, display_title, bg_rgb, accent_rgb, ai_sheet_filename, hole_mode, stages_vi)
# hole_mode:
#   "none"       -> exterior flood-fill only (preserves white snow/beards/mochi/cat fur 100%)
#   "pure_holes" -> also punch pure flat #FFFFFF interior holes (saturation <= 6, min_rgb >= 247)
#                   such as mug handle (#85), wreath center (#88), bonsai gaps (#92), clock/sleigh gaps
AI_HOLIDAY_MANIFEST = [
    # ===================== A. 8 CHRISTMAS THEMES (#81–#88) =====================
    (
        81, "xmas_tree_glow", "81. Christmas Tree Glow",
        (244, 250, 246), (27, 107, 68),
        "christmas_tree_glow_sprite_sheet_1795846762631.jpg", "none",
        ["Cây thông mộc", "Quả châu xinh", "Ruy băng nơ đỏ", "Đèn vàng ấm", "Hộp quà gốc", "Sao đỉnh 100%"],
    ),
    (
        82, "xmas_snowman_build", "82. Cozy Snowman Build",
        (243, 249, 254), (45, 114, 168),
        "cozy_snowman_build_sprite_sheet_final_1795846837530.jpg", "none",
        ["Khối tuyết nhỏ", "Thân 2 tầng", "Mũi cà rốt vui", "Khăn & mũ len", "Tay kẹo gậy", "Chim xanh 100%"],
    ),
    (
        83, "xmas_gingerbread_bakery", "83. Gingerbread Bakery",
        (253, 247, 240), (163, 86, 42),
        "gingerbread_bakery_sprite_sheet_1795846764713.jpg", "none",
        ["Bánh gừng mộc", "Vẽ kem cười", "Nơ đỏ cúc kẹo", "Mũ bếp kẹo gậy", "Ôm nhà bánh", "Rực rỡ 100%"],
    ),
    (
        84, "xmas_santa_delivery", "84. Santa Gift Delivery",
        (255, 245, 246), (186, 38, 52),
        "santa_gift_delivery_stickers_1795846764185.jpg", "sleigh_only",
        ["Cầm thư Noel", "Ôm tất chuông", "Ôm hộp quà", "Vác túi quà", "Xe trượt tuyết", "Tung quà 100%"],
    ),
    (
        85, "xmas_hot_cocoa_cafe", "85. Winter Hot Cocoa Cafe",
        (252, 246, 242), (125, 74, 52),
        "winter_hot_cocoa_cafe_spritesheet_1795846767305.jpg", "mug_handle",
        ["Cốc gốm trống", "Rót ca cao ấm", "Thả kẹo dẻo", "Phủ kem tươi", "Kẹo gậy & quế", "Bánh gừng 100%"],
    ),
    (
        86, "xmas_reindeer_parade", "86. Reindeer Bell Parade",
        (254, 248, 242), (176, 62, 46),
        "reindeer_bell_parade_spritesheet_1795846848455.jpg", "antler_gaps",
        ["Ngồi ngoan", "Đeo chuông vàng", "Quấn khăn đỏ", "Đèn trên sừng", "Mũi đỏ sáng", "Nhảy vui 100%"],
    ),
    (
        87, "xmas_cozy_village", "87. Christmas Snow Village",
        (244, 247, 253), (52, 86, 139),
        "christmas_snow_village_stickers_1795846850278.jpg", "none",
        ["Nhà gỗ mộc", "Cửa sổ sáng", "Mái tuyết khói", "Thông & cột đèn", "Vòng hoa quà", "Làng tuyết 100%"],
    ),
    (
        88, "xmas_wreath_candle", "88. Wreath & Candle",
        (246, 250, 245), (42, 112, 74),
        "wreath_candle_spritesheet_1795846851809.jpg", "wreath_center",
        ["Vòng lá mộc", "Thêm quả mọng", "Thắt nơ đỏ", "Chuông & châu", "Thắp nến ấm", "Tỏa sáng 100%"],
    ),

    # ===================== B. 7 NEW YEAR THEMES (#89–#95) =====================
    (
        89, "ny_fireworks_countdown", "89. Fireworks Countdown",
        (245, 244, 253), (76, 56, 158),
        "fireworks_countdown_sprite_sheet_v2_1795846873040.jpg", "pure_holes",
        ["Sắp 12 giờ", "Rung nhẹ sáng", "Đúng 12h00!", "Pháo hoa đầu", "Ruy băng màu", "Giao thừa 100%"],
    ),
    (
        90, "ny_lucky_red_envelope", "90. Lucky Red Envelope",
        (255, 246, 244), (192, 42, 42),
        "lucky_red_envelope_spritesheet_1795846852675.jpg", "none",
        ["Lì xì đóng nắp", "Hé mở sáng", "Bật xu vàng", "Thỏi vàng tua", "Hoa xuân nở", "Tài lộc 100%"],
    ),
    (
        91, "ny_maneki_neko", "91. Maneki Neko Fortune",
        (255, 248, 242), (189, 54, 48),
        None, "none",
        ["Mèo ngồi ngoan", "Chuông cổ vàng", "Vẫy gọi lộc", "Ôm đồng vàng", "Túi lộc xu", "Phú quý 100%"],
    ),
    (
        92, "ny_sakura_blossom", "92. Sakura New Year",
        (255, 246, 249), (204, 78, 122),
        "sakura_new_year_sprite_sheet_1795846905120.jpg", "pure_holes",
        ["Cành nụ xuân", "Hé hoa đầu", "Nở nửa tán", "Tán hoa tròn", "Chuông & đèn", "Nở rộ 100%"],
    ),
    (
        93, "ny_daruma_wish", "93. Daruma Wish Goal",
        (254, 246, 244), (178, 34, 34),
        None, "none",
        ["Chưa vẽ mắt", "Vẽ 1 mắt trái", "Má hồng sáng", "Ngồi đệm nơ", "Hào quang ấm", "Đủ 2 mắt 100%"],
    ),
    (
        94, "ny_tea_mochi", "94. Cozy Tea & Mochi",
        (246, 250, 244), (72, 122, 68),
        None, "none",
        ["Khay ấm trà", "Chén Matcha", "Đĩa bánh Mochi", "Kagami 2 tầng", "Đặt quả quýt", "Tiệc trà 100%"],
    ),
    (
        95, "ny_festival_lantern", "95. New Year Festival",
        (255, 247, 242), (188, 52, 42),
        None, "pure_holes",
        ["Đèn giấy mộc", "Đỏ cam sáng", "Tua rua vàng", "Tỏa quầng sáng", "Dây đèn hoa", "Lễ hội 100%"],
    ),
]


def _find_valley(proj: np.ndarray, nominal: int, search_radius: int) -> int:
    lo = max(1, nominal - search_radius)
    hi = min(len(proj) - 2, nominal + search_radius)
    sub = proj[lo:hi + 1]
    min_val = sub.min()
    # Pick the middle of all pixels achieving min_val (widest pure-white gutter)
    idxs = np.where(sub <= min_val + 1e-6)[0]
    return int(lo + idxs[len(idxs) // 2])


def _split_3x2_sheet(im_rgb: Image.Image) -> list[Image.Image]:
    arr = np.asarray(im_rgb, dtype=np.float32)
    h, w, _ = arr.shape
    # Ink score: how far from white #FFFFFF each pixel is
    ink = (255.0 - arr.min(axis=2))
    ink[ink < 14.0] = 0.0

    col_proj = ink.sum(axis=0)
    row_proj = ink.sum(axis=1)

    x1 = _find_valley(col_proj, w // 3, int(w * 0.08))
    x2 = _find_valley(col_proj, (2 * w) // 3, int(w * 0.08))
    y1 = _find_valley(row_proj, h // 2, int(h * 0.10))

    xs = [0, x1, x2, w]
    ys = [0, y1, h]
    cells = []
    for r in range(2):
        for c in range(3):
            cells.append(im_rgb.crop((xs[c], ys[r], xs[c + 1], ys[r + 1])))
    return cells


def _remove_white_bg(cell_rgb: Image.Image, hole_mode: str, stage_idx: int) -> Image.Image:
    """
    Studio-grade exterior flood-fill + selective interior hole punch + anti-alias halo removal.
    Preserves ALL interior whites (snowmen, Santa beards, marshmallows, whipped cream, snow roofs)
    because every subject is enclosed by a closed dark-brown outline (#4A3228).
    """
    arr = np.asarray(cell_rgb.convert("RGB"), dtype=np.uint8)
    h, w, _ = arr.shape
    r = arr[:, :, 0].astype(np.int16)
    g = arr[:, :, 1].astype(np.int16)
    b = arr[:, :, 2].astype(np.int16)
    mn = np.minimum(np.minimum(r, g), b)
    mx = np.maximum(np.maximum(r, g), b)
    sat = mx - mn

    # Background candidate for exterior flood-fill (handles JPEG near-white + soft bright glow edge)
    # Keep strictly near-white/neutral so warm yellow sparkles/glows remain intact!
    is_bg_cand = (mn >= 232) & (sat <= 18)

    bg = np.zeros((h, w), dtype=bool)
    q: deque[tuple[int, int]] = deque()

    # Seed from all 4 cell borders
    for x in range(w):
        if is_bg_cand[0, x] and not bg[0, x]:
            bg[0, x] = True
            q.append((0, x))
        if is_bg_cand[h - 1, x] and not bg[h - 1, x]:
            bg[h - 1, x] = True
            q.append((h - 1, x))
    for y in range(h):
        if is_bg_cand[y, 0] and not bg[y, 0]:
            bg[y, 0] = True
            q.append((y, 0))
        if is_bg_cand[y, w - 1] and not bg[y, w - 1]:
            bg[y, w - 1] = True
            q.append((y, w - 1))

    # 4-connected BFS flood fill
    while q:
        cy, cx = q.popleft()
        if cy > 0 and not bg[cy - 1, cx] and is_bg_cand[cy - 1, cx]:
            bg[cy - 1, cx] = True
            q.append((cy - 1, cx))
        if cy + 1 < h and not bg[cy + 1, cx] and is_bg_cand[cy + 1, cx]:
            bg[cy + 1, cx] = True
            q.append((cy + 1, cx))
        if cx > 0 and not bg[cy, cx - 1] and is_bg_cand[cy, cx - 1]:
            bg[cy, cx - 1] = True
            q.append((cy, cx - 1))
        if cx + 1 < w and not bg[cy, cx + 1] and is_bg_cand[cy, cx + 1]:
            bg[cy, cx + 1] = True
            q.append((cy, cx + 1))

    # Selective interior-hole punching for open shapes (mug handle, wreath center, sleigh runner, etc.)
    def _flood_hole_from(seeds: list[tuple[int, int]], cand_mask: np.ndarray):
        hq: deque[tuple[int, int]] = deque()
        for sy, sx in seeds:
            if 0 <= sy < h and 0 <= sx < w and cand_mask[sy, sx] and not bg[sy, sx]:
                bg[sy, sx] = True
                hq.append((sy, sx))
        while hq:
            cy, cx = hq.popleft()
            if cy > 0 and not bg[cy - 1, cx] and cand_mask[cy - 1, cx]:
                bg[cy - 1, cx] = True
                hq.append((cy - 1, cx))
            if cy + 1 < h and not bg[cy + 1, cx] and cand_mask[cy + 1, cx]:
                bg[cy + 1, cx] = True
                hq.append((cy + 1, cx))
            if cx > 0 and not bg[cy, cx - 1] and cand_mask[cy, cx - 1]:
                bg[cy, cx - 1] = True
                hq.append((cy, cx - 1))
            if cx + 1 < w and not bg[cy, cx + 1] and cand_mask[cy, cx + 1]:
                bg[cy, cx + 1] = True
                hq.append((cy, cx + 1))

    pure_white = (mn >= 244) & (sat <= 8)
    if hole_mode == "wreath_center":
        # Center opening of wreath (stages 0..4 have pure white center; stage 5 has warm candle glow — keep glow!)
        if stage_idx <= 4:
            # Sample around the upper-center of the wreath hole (above candle in stage 4)
            seeds = [(int(h * fy), int(w * fx)) for fy in (0.42, 0.48, 0.54) for fx in (0.46, 0.50, 0.54)]
            _flood_hole_from(seeds, (mn >= 234) & (sat <= 14))
    elif hole_mode == "mug_handle":
        # Open hole inside the right-side mug handle (always in right 68..88% of width, middle-lower height)
        # Find pure-white pixels strictly inside x in [0.68w, 0.88w], y in [0.45h, 0.82h]
        y_lo, y_hi = int(h * 0.42), int(h * 0.84)
        x_lo, x_hi = int(w * 0.68), int(w * 0.90)
        ys_p, xs_p = np.where(pure_white[y_lo:y_hi, x_lo:x_hi] & (~bg[y_lo:y_hi, x_lo:x_hi]))
        if len(ys_p) > 20:
            seeds = [(int(y_lo + ys_p[len(ys_p) // 2]), int(x_lo + xs_p[len(xs_p) // 2]))]
            _flood_hole_from(seeds, (mn >= 235) & (sat <= 15))
    elif hole_mode == "sleigh_only":
        # Stage 4 (Santa in sleigh) has small open white gaps under sleigh runners in lower 25%
        if stage_idx == 4:
            y_lo = int(h * 0.72)
            ys_p, xs_p = np.where(pure_white[y_lo:, :] & (~bg[y_lo:, :]))
            if len(ys_p) > 10:
                seeds = [(int(y_lo + ys_p[i]), int(xs_p[i])) for i in range(0, len(ys_p), max(1, len(ys_p) // 20))]
                _flood_hole_from(seeds, (mn >= 236) & (sat <= 14))
    elif hole_mode == "antler_gaps":
        # Stages 3 & 4 have fairy lights strung between antlers creating enclosed white gaps in top 30%
        if stage_idx in (3, 4):
            y_hi = int(h * 0.36)
            ys_p, xs_p = np.where(pure_white[:y_hi, :] & (~bg[:y_hi, :]))
            if len(ys_p) > 10:
                seeds = [(int(ys_p[i]), int(xs_p[i])) for i in range(0, len(ys_p), max(1, len(ys_p) // 30))]
                _flood_hole_from(seeds, (mn >= 236) & (sat <= 14))
    elif hole_mode == "pure_holes":
        # Punch enclosed pure-white gaps (e.g. between sakura branches/petals, fireworks gaps)
        # while avoiding cream clock face (which has sat > 12 or min < 244)!
        ys_p, xs_p = np.where(pure_white & (~bg))
        if len(ys_p) > 0:
            # Group into connected components and only punch pure-white holes NOT inside cream clock dial
            visited = bg.copy()
            for idx in range(len(ys_p)):
                sy, sx = int(ys_p[idx]), int(xs_p[idx])
                if visited[sy, sx]:
                    continue
                comp = []
                cq = deque([(sy, sx)])
                visited[sy, sx] = True
                while cq:
                    cy, cx = cq.popleft()
                    comp.append((cy, cx))
                    for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
                        if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx] and (mn[ny, nx] >= 240 and sat[ny, nx] <= 10):
                            visited[ny, nx] = True
                            cq.append((ny, nx))
                # Only punch medium-small pure-white background pockets (avoid accidentally punching huge white body)
                if 12 <= len(comp) <= 6000:
                    for cy, cx in comp:
                        bg[cy, cx] = True

    # Build smooth anti-aliased alpha & decontaminate white fringe on boundary pixels!
    alpha = np.where(bg, 0.0, 255.0).astype(np.float32)

    # Identify 1-pixel and 2-pixel foreground edge rings adjacent to bg
    def _dilate4(mask: np.ndarray) -> np.ndarray:
        out = mask.copy()
        out[1:, :] |= mask[:-1, :]
        out[:-1, :] |= mask[1:, :]
        out[:, 1:] |= mask[:, :-1]
        out[:, :-1] |= mask[:, 1:]
        return out

    bg_d1 = _dilate4(bg)
    ring1 = bg_d1 & (~bg)
    bg_d2 = _dilate4(bg_d1)
    ring2 = bg_d2 & (~bg_d1)

    rgb_out = arr.astype(np.float32)

    # On ring1 & ring2, pixels blended with white background have high brightness & low saturation.
    # Un-premultiply assuming foreground edge is darker outline (~(74,50,40)) or local color!
    # Using classic white-matte alpha extraction on bright boundary fringe pixels:
    #   pixel = a * fg + (1 - a) * 255  =>  if pixel is near-white blended with dark outline:
    #   alpha_est = clamp((255 - min(R,G,B)) / (255 - 85), 0, 1)
    lum = (0.299 * rgb_out[:, :, 0] + 0.587 * rgb_out[:, :, 1] + 0.114 * rgb_out[:, :, 2])

    for ring, strength in ((ring1, 1.0), (ring2, 0.55)):
        # Only soften/de-fringe lightened boundary pixels (lum > 145)
        fringe = ring & (lum > 140.0)
        if not np.any(fringe):
            continue
        # Estimate coverage from how far below 255 the pixel is
        cov = np.clip((252.0 - lum[fringe]) / 112.0, 0.0, 1.0)
        # Blend coverage on ring2 more gently
        a_new = 255.0 * (cov if strength >= 0.99 else (1.0 - strength + strength * cov))
        alpha[fringe] = np.minimum(alpha[fringe], a_new)

        # Un-premultiply white matte so semi-transparent edge pixels carry rich color instead of pale gray!
        a_norm = np.clip(alpha[fringe] / 255.0, 0.08, 1.0)
        for ch in range(3):
            c_val = rgb_out[:, :, ch][fringe]
            un = (c_val - 255.0 * (1.0 - a_norm)) / a_norm
            rgb_out[:, :, ch][fringe] = np.clip(un, 0.0, 255.0)

    # Clean tiny stray JPEG dust specks (alpha < 14)
    alpha[alpha < 14.0] = 0.0

    rgba = np.dstack([
        np.clip(rgb_out[:, :, 0], 0, 255).astype(np.uint8),
        np.clip(rgb_out[:, :, 1], 0, 255).astype(np.uint8),
        np.clip(rgb_out[:, :, 2], 0, 255).astype(np.uint8),
        np.clip(alpha, 0, 255).astype(np.uint8),
    ])
    return Image.fromarray(rgba, mode="RGBA")


def _normalize_500_rgba(im: Image.Image, target: int = 500, pad_ratio: float = 0.10) -> Image.Image:
    im = im.convert("RGBA")
    alpha = im.getchannel("A")
    mask = alpha.point(lambda a: 255 if a > 20 else 0)
    bbox = mask.getbbox()
    if bbox:
        im = im.crop(bbox)
    w, h = im.size
    inner = int(round(target * (1.0 - 2.0 * pad_ratio)))
    scale = min(inner / max(1, w), inner / max(1, h))
    nw = max(1, int(round(w * scale)))
    nh = max(1, int(round(h * scale)))
    im = im.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGBA", (target, target), (0, 0, 0, 0))
    canvas.paste(im, ((target - nw) // 2, (target - nh) // 2), im)
    return canvas


def _draw_fitted_label(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, max_right_x: int, fill):
    font_path = "C:/Windows/Fonts/segoeuib.ttf"
    for sz in (13, 12, 11, 10):
        try:
            f = ImageFont.truetype(font_path, sz)
        except Exception:
            f = ImageFont.load_default()
        bbox = draw.textbbox((x, y), text, font=f)
        if bbox[2] <= max_right_x:
            draw.text((x, y), text, fill=fill, font=f)
            return
    f = ImageFont.truetype(font_path, 10)
    words = text.split()
    mid = max(1, len(words) // 2)
    for i, line in enumerate((" ".join(words[:mid]), " ".join(words[mid:]))):
        ly = y - 2 + i * 13
        draw.text((x, ly), line, fill=fill, font=f)
        bbox = draw.textbbox((x, ly), line, font=f)
        assert bbox[2] <= max_right_x, f"Text overflow in Contact Sheet: {line!r} right={bbox[2]} > {max_right_x}"


def _build_contact_sheet(
    rows_data: list[tuple[str, str, tuple, tuple, list[tuple[str, Image.Image]]]],
    banner_title: str,
    banner_sub: str,
    banner_rgb: tuple[int, int, int],
    page_rgb: tuple[int, int, int],
    out_jpg: Path,
):
    cell_w, cell_h = 236, 282
    left_w, pad, hdr_h = 264, 18, 86
    W = pad * 2 + left_w + cell_w * 6
    H = pad * 2 + hdr_h + cell_h * len(rows_data)

    sheet = Image.new("RGB", (W, H), page_rgb)
    draw = ImageDraw.Draw(sheet)
    f_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 25)
    f_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 14)
    f_row = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 15)
    f_src = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 11)
    f_tiny = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 11)

    draw.rectangle([0, 0, W, hdr_h], fill=banner_rgb)
    draw.text((pad, 14), banner_title, fill=(255, 255, 255), font=f_title)
    draw.text((pad, 50), banner_sub, fill=(255, 245, 232), font=f_sub)

    pcts = ["0%", "20%", "40%", "60%", "80%", "100% MAX"]
    for r_i, (title, slug, bg_c, acc_c, stages) in enumerate(rows_data):
        y0 = hdr_h + pad + r_i * cell_h
        draw.rounded_rectangle([pad, y0 + 4, W - pad, y0 + cell_h - 6], radius=14, fill=bg_c, outline=acc_c, width=2)
        draw.text((pad + 14, y0 + 104), title, fill=acc_c, font=f_row)
        draw.text((pad + 14, y0 + 130), "Style: Kawaii Pastel Chibi AI", fill=(115, 110, 115), font=f_src)
        draw.text((pad + 14, y0 + 148), f"Slug: {slug}", fill=(135, 130, 135), font=f_src)

        for s_i, (lbl, im) in enumerate(stages):
            x0 = pad + left_w + s_i * cell_w
            is_f = (s_i == 5)
            # Use soft subtle warm-cream card bg (#FAF7F4) so any white-fringe bugs are immediately visible!
            draw.rounded_rectangle(
                [x0 + 6, y0 + 12, x0 + cell_w - 6, y0 + cell_h - 14],
                radius=10, fill=(252, 249, 246),
                outline=(acc_c if is_f else (228, 224, 224)), width=2 if is_f else 1,
            )
            big = im.resize((164, 164), Image.LANCZOS)
            sheet.paste(big, (x0 + (cell_w - 164) // 2, y0 + 16), big)

            small = im.resize((44, 44), Image.LANCZOS)
            sx, sy = x0 + cell_w - 58, y0 + 188
            frame_left_x = sx - 4
            draw.rounded_rectangle([frame_left_x, sy - 4, sx + 48, sy + 48], radius=6, fill=(245, 242, 246), outline=(215, 210, 218), width=1)
            sheet.paste(small, (sx, sy), small)

            max_text_right = frame_left_x - 10
            stage_tag = f"S{s_i} • {pcts[s_i]}"
            draw.text((x0 + 14, y0 + 190), stage_tag, fill=acc_c, font=f_tiny)
            tb_tag = draw.textbbox((x0 + 14, y0 + 190), stage_tag, font=f_tiny)
            assert tb_tag[2] <= max_text_right, f"Stage tag overlap on {slug} S{s_i}"

            _draw_fitted_label(draw, x0 + 14, y0 + 212, lbl, max_text_right, (60, 48, 52))
            draw.text((sx + 8, sy + 50), "44px", fill=(150, 144, 150), font=f_tiny)

    out_jpg.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_jpg, "JPEG", quality=94, optimize=True)
    print(f"  [CONTACT SHEET] Saved {out_jpg} ({sheet.size[0]}x{sheet.size[1]}, {out_jpg.stat().st_size // 1024} KB)")


def main():
    only_nums = {int(a) for a in sys.argv[1:] if a.isdigit()}
    xmas_rows = []
    ny_rows = []
    hashes: set[str] = set()
    processed = 0
    missing = []

    for num, slug, title, bg_c, acc_c, sheet_fn, hole_mode, labels in AI_HOLIDAY_MANIFEST:
        if only_nums and num not in only_nums:
            continue
        if not sheet_fn:
            missing.append((num, slug, title))
            continue
        sheet_p = BRAIN_DIR / sheet_fn
        if not sheet_p.exists():
            missing.append((num, slug, title))
            continue

        out_dir = ASSETS_DIR / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        # Clean ALL old files in this theme folder so ZERO Irasutoya/Noto files remain!
        for old in out_dir.glob("*"):
            if old.is_file():
                old.unlink()

        raw_im = Image.open(sheet_p).convert("RGB")
        cells = _split_3x2_sheet(raw_im)
        assert len(cells) == 6
        loaded_stages = []

        for s_i, cell_im in enumerate(cells):
            clean = _remove_white_bg(cell_im, hole_mode=hole_mode, stage_idx=s_i)
            norm = _normalize_500_rgba(clean, target=500, pad_ratio=0.10)
            assert norm.size == (500, 500) and norm.mode == "RGBA"

            alpha_arr = np.asarray(norm.getchannel("A"))
            opaque_cnt = int((alpha_arr > 20).sum())
            trans_cnt = int((alpha_arr <= 10).sum())
            assert opaque_cnt > 18000, f"Sprite too empty: {slug}/stage_{s_i}.png ({opaque_cnt} px)"
            assert trans_cnt > 35000, f"Sprite lacks transparent bg: {slug}/stage_{s_i}.png ({trans_cnt} px)"

            out_p = out_dir / f"stage_{s_i}.png"
            norm.save(out_p, "PNG", optimize=True)
            h = hashlib.sha256(out_p.read_bytes()).hexdigest()
            assert h not in hashes, f"Duplicate sprite hash: {slug}/stage_{s_i}.png"
            hashes.add(h)
            loaded_stages.append((labels[s_i], norm))
            processed += 1

        entry = (title, slug, bg_c, acc_c, loaded_stages)
        if num <= 88:
            xmas_rows.append(entry)
        else:
            ny_rows.append(entry)
        print(f"  [AI OK #{num:02d}] {slug:<26} 6x 500x500 RGBA clean transparent (hole_mode={hole_mode})", flush=True)

    if len(xmas_rows) == 8:
        _build_contact_sheet(
            xmas_rows,
            "CHRISTMAS COLLECTION — #81–#88 (48 KAWAII CHIBI AI TRANSPARENT 500x500 SPRITES)",
            "100% Unified Kawaii Pastel Chibi AI Sticker Style • Seamless Same-Subject Evolution (S0→S5) • 44px Verified",
            (178, 36, 48), (252, 248, 246),
            PREVIEWS_DIR / "assets_contact_sheet_christmas_81_88.jpg",
        )
    if len(ny_rows) == 7:
        _build_contact_sheet(
            ny_rows,
            "NEW YEAR COLLECTION — #89–#95 (42 KAWAII CHIBI AI TRANSPARENT 500x500 SPRITES)",
            "100% Unified Kawaii Pastel Chibi AI Sticker Style • Seamless Same-Subject Evolution (S0→S5) • 44px Verified",
            (192, 42, 42), (255, 248, 244),
            PREVIEWS_DIR / "assets_contact_sheet_newyear_89_95.jpg",
        )
    elif ny_rows:
        # Partial preview for completed New Year themes while awaiting remaining AI sheets
        _build_contact_sheet(
            ny_rows,
            f"NEW YEAR COLLECTION (PARTIAL {len(ny_rows)}/7 READY — WAITING QUOTA FOR #91,#93,#94,#95)",
            "100% Unified Kawaii Pastel Chibi AI Sticker Style • Seamless Same-Subject Evolution (S0→S5) • 44px Verified",
            (192, 42, 42), (255, 248, 244),
            PREVIEWS_DIR / "assets_contact_sheet_newyear_89_95.jpg",
        )

    print(f"=== PROCESSED {processed}/90 AI SPRITES | MISSING THEMES: {len(missing)} ===")
    for m in missing:
        print(f"  [PENDING QUOTA] #{m[0]} {m[1]} ({m[2]})")


if __name__ == "__main__":
    main()
