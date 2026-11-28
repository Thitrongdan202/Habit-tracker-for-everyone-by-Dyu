"""
fetch_holiday_81_95_assets.py — Downloads & normalizes 90 authentic free transparent sprites
for Themes #81–#95 (8 Christmas + 7 New Year) from Irasutoya & Google Noto Emoji.

ZERO AI generation, ZERO procedural character drawing.
- Strict 1-source-per-theme cohesion (all 6 stages S0..S5 share exact same artist/pack).
- Every sprite normalized to 500x500 RGBA transparent PNG, centered with uniform 8% margin.
- Generates 2 high-res inspection Contact Sheets (with 44px preview box & 0-overlap assertion):
    * previews/assets_contact_sheet_christmas_81_88.jpg
    * previews/assets_contact_sheet_newyear_89_95.jpg
- Writes full URL provenance log to `assets/holiday_81_95_sources.md`.
"""
from __future__ import annotations

import hashlib
import io
import json
import sys
import tempfile
import urllib.request
from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT / "assets"
PREVIEWS_DIR = ROOT / "previews"

FLAT_INDEX_PATH = Path(tempfile.gettempdir()) / "irasutoya_flat.json"

# (num, slug, display_title, source_name, bg_rgb, accent_rgb, stages[(label_vi, kind, key)])
# kind == "irasutoya": key is filename in irasutoya_flat.json
# kind == "noto_svg":  key is unicode hex codepoint on fonts.gstatic.com/s/e/notoemoji/latest/<cp>/emoji.svg
HOLIDAY_MANIFEST = [
    # ===================== A. 8 CHRISTMAS THEMES (#81–#88) =====================
    (
        81, "xmas_tree_glow", "81. Christmas Tree Glow", "Irasutoya (irasutoya.com)",
        (244, 250, 246), (27, 107, 68),
        [
            ("Cây thông mộc",  "irasutoya", "christmastree_nude.png"),
            ("Quả châu đỏ",    "irasutoya", "christmas_kugel01_red.png"),
            ("Cây thông nhỏ",  "irasutoya", "christmas_ornament07_tree.png"),
            ("Trang trí đèn",  "irasutoya", "christmastree_decoration.png"),
            ("Ngôi sao đỉnh",  "irasutoya", "christmas_tree.png"),
            ("Rực sáng 100%",  "irasutoya", "christmas_tree_present.png"),
        ],
    ),
    (
        82, "xmas_snowman_build", "82. Cozy Snowman Build", "Irasutoya (irasutoya.com)",
        (243, 249, 254), (45, 114, 168),
        [
            ("Bông tuyết rơi", "irasutoya", "snow_crystal1.png"),
            ("Viên tuyết nhỏ", "irasutoya", "snowball.png"),
            ("Đắp thân tuyết", "irasutoya", "snowman_yukidaruma_tokeru.png"),
            ("Quấn khăn mũ",   "irasutoya", "snowman_yukidaruma_sandan.png"),
            ("Mũi cà rốt vui", "irasutoya", "christmas_snowman.png"),
            ("Gia đình tuyết", "irasutoya", "snowman_yukidaruma_family.png"),
        ],
    ),
    (
        83, "xmas_gingerbread_bakery", "83. Gingerbread Bakery", "Irasutoya (irasutoya.com)",
        (253, 247, 240), (163, 86, 42),
        [
            ("Bột & nguyên liệu", "irasutoya", "food_flour.png"),
            ("Khuôn bánh quy",    "irasutoya", "cookie_kata.png"),
            ("Bánh quy nướng",    "irasutoya", "sweets_cookie.png"),
            ("Bánh gừng cười",    "irasutoya", "christmas_gingerbread.png"),
            ("Nhà bánh gừng",     "irasutoya", "christmas_okashi_house.png"),
            ("Tiệc bánh Noel",    "irasutoya", "christmas_bush_de_noel.png"),
        ],
    ),
    (
        84, "xmas_santa_delivery", "84. Santa Gift Delivery", "Irasutoya (irasutoya.com)",
        (255, 245, 246), (186, 38, 52),
        [
            ("Thư gửi Noel",    "irasutoya", "bunbougu_envelope_letter.png"),
            ("Tất treo quà",    "irasutoya", "christmas_socks.png"),
            ("Núi hộp quà",     "irasutoya", "christmas_presents.png"),
            ("Santa vác quà",   "irasutoya", "christmas_santa_present.png"),
            ("Xe tuần lộc",     "irasutoya", "christmas_santa_sori.png"),
            ("Phát quà 100%",   "irasutoya", "christmas_dance_tonakai_santa.png"),
        ],
    ),
    (
        85, "xmas_hot_cocoa_cafe", "85. Winter Hot Cocoa Cafe", "Irasutoya (irasutoya.com)",
        (252, 246, 242), (125, 74, 52),
        [
            ("Cốc mùa đông",   "irasutoya", "syokki_mug_cup.png"),
            ("Bột ca cao ấm",  "irasutoya", "cocoa.png"),
            ("Kẹo dẻo mềm",    "irasutoya", "marshmallow.png"),
            ("Pha ca cao nóng","irasutoya", "cafe_cocoa.png"),
            ("Kem tươi quế",   "irasutoya", "drink_coffee_cream_chocolate.png"),
            ("Góc cafe Noel",  "irasutoya", "christmas_cake.png"),
        ],
    ),
    (
        86, "xmas_reindeer_parade", "86. Reindeer Bell Parade", "Irasutoya (irasutoya.com)",
        (254, 248, 242), (176, 62, 46),
        [
            ("Chuông vàng",     "irasutoya", "christmas_bell.png"),
            ("Mũ Noel đỏ",      "irasutoya", "christmas_santa_boushi_big.png"),
            ("Bé tuần lộc",     "irasutoya", "animal_tonakai.png"),
            ("Mũi đỏ rạng rỡ",  "irasutoya", "christmas_reindeer.png"),
            ("Áo Noel xinh",    "irasutoya", "christmas_tonakai.png"),
            ("Tung tăng 100%",  "irasutoya", "christmas_dance_tonakai.png"),
        ],
    ),
    (
        87, "xmas_cozy_village", "87. Christmas Snow Village", "Irasutoya (irasutoya.com — fallback from itch.io 403)",
        (244, 247, 253), (52, 86, 139),
        [
            ("Đất tuyết trắng", "irasutoya", "yukigeshiki.png"),
            ("Đèn đường ấm",    "irasutoya", "light_gaitou.png"),
            ("Nhà gỗ tuyết",    "irasutoya", "bessou_log_house.png"),
            ("Mái phủ tuyết",   "irasutoya", "snow_house.png"),
            ("Lò sưởi ấm áp",   "irasutoya", "christmas_danro_present.png"),
            ("Làng tuyết 100%", "irasutoya", "snow_globe_snow_dome.png"),
        ],
    ),
    (
        88, "xmas_wreath_candle", "88. Wreath & Candle", "Irasutoya (irasutoya.com)",
        (246, 250, 245), (42, 112, 74),
        [
            ("Cành thông lá",  "irasutoya", "christmas_hiiragi.png"),
            ("Vòng lá mộc",    "irasutoya", "christmas_ornament02_wreath.png"),
            ("Chuông nơ đỏ",   "irasutoya", "christmas_ornament09_bells.png"),
            ("Vòng hoa xanh",  "irasutoya", "christmas_wreath.png"),
            ("Thắp nến ấm",    "irasutoya", "christmas_candle.png"),
            ("Vòng hoa 100%",  "irasutoya", "christmas_wreath_heart.png"),
        ],
    ),

    # ===================== B. 7 NEW YEAR THEMES (#89–#95) =====================
    (
        89, "ny_fireworks_countdown", "89. Fireworks Countdown", "Google Noto Animated Emoji (fonts.gstatic.com)",
        (245, 244, 253), (76, 56, 158),
        [
            ("Đếm ngược 12h",  "noto_gif", "23f0"),
            ("Pháo tép nhỏ",   "noto_svg", "1f9e8"),
            ("Ánh sao đêm",    "noto_gif", "2728"),
            ("Pháo hoa nở rộ", "noto_gif", "1f386"),
            ("Cầu giấy mừng",  "noto_gif", "1f38a"),
            ("Giao thừa 100%", "noto_gif", "1f389"),
        ],
    ),
    (
        90, "ny_lucky_red_envelope", "90. Lucky Red Envelope", "Irasutoya (irasutoya.com)",
        (255, 246, 244), (192, 42, 42),
        [
            ("Bao lì xì đỏ",   "irasutoya", "syougatsu2_otoshidama.png"),
            ("Đồng xu vàng",   "irasutoya", "coin_kinka.png"),
            ("Túi lộc xuân",   "irasutoya", "fukubukuro.png"),
            ("Núi vàng lộc",   "irasutoya", "money_koban_yamadumi.png"),
            ("Cành mai nở",    "irasutoya", "flower_ume.png"),
            ("Thuyền báu 100%","irasutoya", "takarabune.png"),
        ],
    ),
    (
        91, "ny_maneki_neko", "91. Maneki Neko Fortune", "Irasutoya (irasutoya.com)",
        (255, 248, 242), (189, 54, 48),
        [
            ("Chuông vàng",    "irasutoya", "omocha_suzu.png"),
            ("Đệm đỏ may",     "irasutoya", "zabuton_red.png"),
            ("Mèo ngồi ngoan", "irasutoya", "engi_mark13_manekineko.png"),
            ("Mèo vẫy gọi lộc","irasutoya", "character_manekineko.png"),
            ("Ôm đồng vàng",   "irasutoya", "syougatsu2_manekineko.png"),
            ("Phú quý 100%",   "irasutoya", "kaiun_goods.png"),
        ],
    ),
    (
        92, "ny_sakura_blossom", "92. Sakura New Year", "Irasutoya (irasutoya.com)",
        (255, 246, 249), (204, 78, 122),
        [
            ("Bông hoa đầu",   "irasutoya", "sakura_hanabira.png"),
            ("Khóm hoa xuân",  "irasutoya", "syougatsu_sakura.png"),
            ("Cành chớm nở",   "irasutoya", "sakura_kaika.png"),
            ("Mưa hoa bay",    "irasutoya", "sakura_fubuki.png"),
            ("Cây hoa nở rộ",  "irasutoya", "sakura_tree.png"),
            ("Vườn xuân 100%", "irasutoya", "tree_sakura_shidarezakura.png"),
        ],
    ),
    (
        93, "ny_daruma_wish", "93. Daruma Wish Goal", "Irasutoya (irasutoya.com)",
        (254, 246, 244), (178, 34, 34),
        [
            ("Bùa cầu may",    "irasutoya", "omamori.png"),
            ("Daruma khởi đầu","irasutoya", "daruma8_white.png"),
            ("Đặt mục tiêu",   "irasutoya", "daruma1_red.png"),
            ("Daruma vàng",    "irasutoya", "daruma3_yellow.png"),
            ("Tỏa sáng đạt",   "irasutoya", "juken_goukaku_daruma.png"),
            ("Ước nguyện 100%","irasutoya", "nenga_akemashiteomedetou_daruma.png"),
        ],
    ),
    (
        94, "ny_tea_mochi", "94. Cozy Tea & Mochi", "Irasutoya (irasutoya.com)",
        (246, 250, 244), (72, 122, 68),
        [
            ("Ấm trà đầu năm", "irasutoya", "tea_kyuusu.png"),
            ("Chén trà nóng",  "irasutoya", "agari_yunomi.png"),
            ("Bộ trà đón xuân","irasutoya", "drink_greentea.png"),
            ("Bánh mochi",     "irasutoya", "mochi_shikaku.png"),
            ("Kagami 2 tầng",  "irasutoya", "osyougatsu_kagamimochi_2dan_kazari.png"),
            ("Kagami 3 tầng",  "irasutoya", "osyougatsu_kagamimochi_3dan_kazari.png"),
        ],
    ),
    (
        95, "ny_festival_lantern", "95. New Year Festival", "Irasutoya (irasutoya.com — fallback from itch.io 403)",
        (255, 247, 242), (188, 52, 42),
        [
            ("Đèn lồng trắng", "irasutoya", "chouchin_white.png"),
            ("Thắp đèn đỏ",    "irasutoya", "chouchin_red.png"),
            ("Dãy đèn lễ hội", "irasutoya", "chouchin_kouhaku.png"),
            ("Quầy bánh ấm",   "irasutoya", "building_takoyaki_yatai.png"),
            ("Pháo hoa rực",   "irasutoya", "hanabi_sky.png"),
            ("Lễ hội 100%",    "irasutoya", "kadomatsu_gouka.png"),
        ],
    ),
]


def _download_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def _normalize_500_rgba(im: Image.Image, target: int = 500, pad_ratio: float = 0.08) -> Image.Image:
    """Trim transparent margin, preserve aspect ratio, center neatly on 500x500 transparent RGBA."""
    im = im.convert("RGBA")
    alpha = im.getchannel("A")
    # Threshold faint alpha dust <= 8
    mask = alpha.point(lambda a: 255 if a > 8 else 0)
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


def _gif_peak_frame_to_rgba(gif_bytes: bytes, size: int = 500) -> Image.Image:
    """Extract the brightest, most vibrant mid-burst frame from an official Google Noto Animated Emoji 512.gif."""
    gif = Image.open(io.BytesIO(gif_bytes))
    n = getattr(gif, "n_frames", 1)
    best_im = None
    best_score = -1
    # Scan middle 25%..80% frames and score by bright/colorful opaque pixels (avoids blank dark sky frame 0!)
    start_f = max(0, int(n * 0.25))
    end_f = max(start_f + 1, int(n * 0.85))
    step = max(1, (end_f - start_f) // 12)
    for fi in range(start_f, end_f, step):
        gif.seek(fi)
        rgba = gif.convert("RGBA")
        # Downsample fast to 64x64 to score bright colorful pixels
        sm = rgba.resize((64, 64), Image.BILINEAR)
        score = sum(
            1 for r, g, b, a in sm.getdata()
            if a > 60 and (max(r, g, b) > 150) and ((r + g + b) > 260)
        )
        if score > best_score:
            best_score = score
            best_im = rgba.copy()
    assert best_im is not None
    return _normalize_500_rgba(best_im, target=size)


def _svg_bytes_to_rgba(svg_bytes: bytes, size: int = 500) -> Image.Image:
    doc = pymupdf.open(stream=svg_bytes, filetype="svg")
    try:
        page = doc[0]
        rect = page.rect
        zoom = max(4.0, (size * 1.5) / max(1.0, max(rect.width, rect.height)))
        pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=True)
        im = Image.frombytes("RGBA", (pix.width, pix.height), pix.samples)
    finally:
        doc.close()
    return _normalize_500_rgba(im, target=size)


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
    rows_data: list[tuple[str, str, str, tuple, tuple, list[tuple[str, Image.Image]]]],
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
    f_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 26)
    f_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 15)
    f_row = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 15)
    f_src = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 11)
    f_tiny = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 11)

    draw.rectangle([0, 0, W, hdr_h], fill=banner_rgb)
    draw.text((pad, 14), banner_title, fill=(255, 255, 255), font=f_title)
    draw.text((pad, 50), banner_sub, fill=(255, 245, 232), font=f_sub)

    pcts = ["0%", "20%", "40%", "60%", "80%", "100% MAX"]
    for r_i, (title, slug, src_name, bg_c, acc_c, stages) in enumerate(rows_data):
        y0 = hdr_h + pad + r_i * cell_h
        draw.rounded_rectangle([pad, y0 + 4, W - pad, y0 + cell_h - 6], radius=14, fill=bg_c, outline=acc_c, width=2)
        draw.text((pad + 14, y0 + 106), title, fill=acc_c, font=f_row)
        short_src = src_name.split(" (")[0]
        draw.text((pad + 14, y0 + 132), f"Source: {short_src}", fill=(115, 110, 115), font=f_src)
        draw.text((pad + 14, y0 + 150), f"Slug: {slug}", fill=(135, 130, 135), font=f_src)

        for s_i, (lbl, im) in enumerate(stages):
            x0 = pad + left_w + s_i * cell_w
            is_f = (s_i == 5)
            draw.rounded_rectangle(
                [x0 + 6, y0 + 12, x0 + cell_w - 6, y0 + cell_h - 14],
                radius=10, fill=(255, 255, 255),
                outline=(acc_c if is_f else (228, 224, 224)), width=2 if is_f else 1,
            )
            big = im.resize((164, 164), Image.LANCZOS)
            sheet.paste(big, (x0 + (cell_w - 164) // 2, y0 + 16), big)

            small = im.resize((44, 44), Image.LANCZOS)
            sx, sy = x0 + cell_w - 58, y0 + 188
            frame_left_x = sx - 4
            draw.rounded_rectangle([frame_left_x, sy - 4, sx + 48, sy + 48], radius=6, fill=(250, 250, 252), outline=(218, 214, 220), width=1)
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
    assert FLAT_INDEX_PATH.exists(), f"Missing Irasutoya index at {FLAT_INDEX_PATH}"
    ir_db = json.loads(FLAT_INDEX_PATH.read_text(encoding="utf-8"))

    hashes: set[str] = set()
    log_lines = [
        "# Holiday Themes (#81–#95) Authentic Asset Sources Log",
        "",
        "All 90 sprites (15 themes × 6 stages S0–S5) were downloaded directly from free, clean transparent sources (ZERO AI generation, ZERO procedural character drawing) and normalized to `500x500` RGBA transparent PNG.",
        "",
        "- Note on `#87` & `#95`: `itch.io` returned `HTTP 403 Forbidden` to automated requests, so both themes were cleanly switched to **Irasutoya** (100% single-source cohesive 6-stage sets).",
        "",
    ]

    xmas_rows = []
    ny_rows = []
    total = 0

    for num, slug, title, src_name, bg_c, acc_c, stages in HOLIDAY_MANIFEST:
        out_dir = ASSETS_DIR / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        loaded_stages = []
        log_lines.append(f"## #{num} — {title} (`{slug}`)")
        log_lines.append(f"- **Unified Source:** {src_name}")

        for s_i, (lbl, kind, key) in enumerate(stages):
            if kind == "irasutoya":
                assert key in ir_db, f"Missing Irasutoya key {key!r} for #{num} {slug} S{s_i}"
                url = ir_db[key]["url"]
                raw = _download_bytes(url)
                im = _normalize_500_rgba(Image.open(io.BytesIO(raw)), target=500)
            elif kind == "noto_svg":
                url = f"https://fonts.gstatic.com/s/e/notoemoji/latest/{key}/emoji.svg"
                raw = _download_bytes(url)
                im = _svg_bytes_to_rgba(raw, size=500)
            elif kind == "noto_gif":
                url = f"https://fonts.gstatic.com/s/e/notoemoji/latest/{key}/512.gif"
                raw = _download_bytes(url)
                im = _gif_peak_frame_to_rgba(raw, size=500)
            else:
                raise ValueError(f"Unknown kind: {kind}")

            assert im.size == (500, 500) and im.mode == "RGBA"
            alpha_vals = list(im.getchannel("A").getdata())
            opaque_cnt = sum(1 for a in alpha_vals if a > 20)
            trans_cnt = sum(1 for a in alpha_vals if a <= 10)
            assert opaque_cnt > 12000, f"Sprite too empty: {slug}/stage_{s_i}.png ({opaque_cnt} px)"
            assert trans_cnt > 20000, f"Sprite lacks transparent background: {slug}/stage_{s_i}.png ({trans_cnt} px)"

            out_p = out_dir / f"stage_{s_i}.png"
            im.save(out_p, "PNG", optimize=True)
            h = hashlib.sha256(out_p.read_bytes()).hexdigest()
            assert h not in hashes, f"DUPLICATE SPRITE HASH: {slug}/stage_{s_i}.png"
            hashes.add(h)
            loaded_stages.append((lbl, im))
            log_lines.append(f"  - `stage_{s_i}.png` ({lbl}): {url}")
            total += 1

        log_lines.append("")
        entry = (title, slug, src_name, bg_c, acc_c, loaded_stages)
        if num <= 88:
            xmas_rows.append(entry)
        else:
            ny_rows.append(entry)
        print(f"  [OK #{num:02d}] {slug:<26} 6x 500x500 RGBA from {src_name.split(' (')[0]}", flush=True)

    assert total == 90, f"Expected 90 sprites, got {total}"
    (ASSETS_DIR / "holiday_81_95_sources.md").write_text("\n".join(log_lines), encoding="utf-8")

    _build_contact_sheet(
        xmas_rows,
        "CHRISTMAS COLLECTION — #81–#88 (48 AUTHENTIC TRANSPARENT 500x500 SPRITES)",
        "100% Real Downloaded Free Assets (Irasutoya) • Zero AI • Single-Source Cohesion per Theme • 44px Preview Verified",
        (178, 36, 48), (252, 248, 246),
        PREVIEWS_DIR / "assets_contact_sheet_christmas_81_88.jpg",
    )
    _build_contact_sheet(
        ny_rows,
        "NEW YEAR COLLECTION — #89–#95 (42 AUTHENTIC TRANSPARENT 500x500 SPRITES)",
        "100% Real Downloaded Free Assets (Google Noto Emoji #89 & Irasutoya #90–#95) • Zero AI • 44px Preview Verified",
        (192, 42, 42), (255, 248, 244),
        PREVIEWS_DIR / "assets_contact_sheet_newyear_89_95.jpg",
    )
    print(f"=== ALL {total}/90 AUTHENTIC SPRITES + 2 CONTACT SHEETS READY ===")


if __name__ == "__main__":
    main()
