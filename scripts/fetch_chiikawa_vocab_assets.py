"""
fetch_chiikawa_vocab_assets.py — Downloads 30 hand-picked, full-resolution transparent PNG
sprites from `https://chiikawawallpaper.com/png/` for the 5 Chiikawa Vocabulary Trackers
(#96–#100), cleans alpha edges cleanly, normalizes to `500x500` RGBA (10% padding),
and renders `previews/assets_contact_sheet_vocab_chiikawa_96_100.jpg` (with 44px preview
boxes & 0-overlap assertion) + provenance log `assets/vocab_chiikawa_96_100_sources.md`.
"""
from __future__ import annotations

import hashlib
import io
import json
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT / "assets"
PREVIEWS_DIR = ROOT / "previews"
CATALOG_PATH = Path(r"C:\Users\thitr\.gemini\antigravity\brain\b0a27be6-6fdd-42d5-82d0-34023ae2cffc\scratch\chiikawa_pool\catalog.json")

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"}

# Hand-picked by visual inspection of picker_*.jpg (exact natural S0 -> S5 study progression!)
# (num, slug, display_title, char_key, bg_rgb, accent_rgb, picks[(label_vi, catalog_idx)])
CHIIKAWA_MANIFEST = [
    (
        96, "chiikawa_srs_vocab", "96. Chiikawa Strawberry Milk (SRS)", "chiikawa",
        (255, 246, 248), (196, 82, 114),
        [
            ("Mới mở sách",    29),
            ("Khởi động nhẹ",  25),
            ("Chăm chỉ học",    4),
            ("Hiểu bài vui",   10),
            ("Hứng khởi sao",  28),
            ("Thuộc 100%!",    11),
        ],
    ),
    (
        97, "hachiware_ielts_vocab", "97. Hachiware Sky Study (IELTS)", "hachiware",
        (242, 249, 255), (43, 76, 126),
        [
            ("Bỡ ngỡ đầu",     26),
            ("Sẵn sàng ôn",     5),
            ("Ghi chú kỹ",     22),
            ("Tiến bộ nhanh",   8),
            ("Cổ vũ hết mình", 14),
            ("Band 8.5 100%",  28),
        ],
    ),
    (
        98, "usagi_flashcard_vocab", "98. Usagi Honey Flashcard (Quiz)", "usagi",
        (255, 250, 235), (176, 102, 42),
        [
            ("Nằm nghỉ nạp",   10),
            ("Mở thẻ ôn",       4),
            ("Luyện nói mic",  16),
            ("Nhảy hào hứng",   9),
            ("Cổ vũ Speaking", 22),
            ("Siêu sao 100%",  13),
        ],
    ),
    (
        99, "momonga_media_vocab", "99. Momonga Lavender (Media)", "momonga",
        (248, 244, 255), (104, 72, 152),
        [
            ("Mơ màng ngủ",     5),
            ("Đọc sách say",   10),
            ("Chill kem ngon",  4),
            ("Tỏa sáng tự tin", 3),
            ("Sưu tầm quà",     9),
            ("Bay bổng 100%",   2),
        ],
    ),
    (
        100, "shisa_exam_vocab", "100. Shisa Matcha Bookshop (Exam)", "shisa",
        (246, 251, 244), (62, 118, 72),
        [
            ("Ngó bài chút",   12),
            ("Ngồi nghiêm túc", 2),
            ("Chăm chép bài",  16),
            ("Mắt sáng hiểu",   6),
            ("Hào hứng ôn",     8),
            ("Đỗ đạt 100%!",    5),
        ],
    ),
]


def _download(url: str) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read()


def _clean_and_normalize_500(im: Image.Image, target: int = 500, pad_ratio: float = 0.10) -> Image.Image:
    im = im.convert("RGBA")
    arr = np.asarray(im, dtype=np.uint8).copy()
    # Wipe faint dust alpha <= 12
    arr[:, :, 3] = np.where(arr[:, :, 3] <= 12, 0, arr[:, :, 3])
    im = Image.fromarray(arr, mode="RGBA")
    alpha = im.getchannel("A")
    bbox = alpha.point(lambda a: 255 if a > 20 else 0).getbbox()
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
        f = ImageFont.truetype(font_path, sz)
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
        assert bbox[2] <= max_right_x, f"Text overflow in Chiikawa Contact Sheet: {line!r}"


def _build_contact_sheet(rows_data, out_jpg: Path):
    cell_w, cell_h = 236, 282
    left_w, pad, hdr_h = 286, 18, 86
    W = pad * 2 + left_w + cell_w * 6
    H = pad * 2 + hdr_h + cell_h * len(rows_data)

    sheet = Image.new("RGB", (W, H), (255, 249, 251))
    draw = ImageDraw.Draw(sheet)
    f_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 25)
    f_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 14)
    f_row = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 14)
    f_src = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 11)
    f_tiny = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 11)

    draw.rectangle([0, 0, W, hdr_h], fill=(214, 96, 134))
    draw.text((pad, 14), "CHIIKAWA VOCABULARY TRACKER — #96–#100 (30 TRANSPARENT 500x500 SPRITES)", fill=(255, 255, 255), font=f_title)
    draw.text((pad, 50), "100% Clean Transparent PNGs from chiikawawallpaper.com/png/ • 5 Distinct Characters • 44px Verified", fill=(255, 242, 248), font=f_sub)

    pcts = ["0%", "20%", "40%", "60%", "80%", "100% MAX"]
    for r_i, (title, slug, char_k, bg_c, acc_c, stages) in enumerate(rows_data):
        y0 = hdr_h + pad + r_i * cell_h
        draw.rounded_rectangle([pad, y0 + 4, W - pad, y0 + cell_h - 6], radius=14, fill=bg_c, outline=acc_c, width=2)
        draw.text((pad + 14, y0 + 102), title, fill=acc_c, font=f_row)
        draw.text((pad + 14, y0 + 128), f"Character: {char_k.capitalize()} (chiikawawallpaper.com)", fill=(115, 105, 115), font=f_src)
        draw.text((pad + 14, y0 + 146), f"Slug: {slug}", fill=(135, 125, 135), font=f_src)

        for s_i, (lbl, im) in enumerate(stages):
            x0 = pad + left_w + s_i * cell_w
            is_f = (s_i == 5)
            draw.rounded_rectangle(
                [x0 + 6, y0 + 12, x0 + cell_w - 6, y0 + cell_h - 14],
                radius=10, fill=(252, 249, 248),
                outline=(acc_c if is_f else (228, 222, 226)), width=2 if is_f else 1,
            )
            big = im.resize((164, 164), Image.LANCZOS)
            sheet.paste(big, (x0 + (cell_w - 164) // 2, y0 + 16), big)

            small = im.resize((44, 44), Image.LANCZOS)
            sx, sy = x0 + cell_w - 58, y0 + 188
            frame_left_x = sx - 4
            draw.rounded_rectangle([frame_left_x, sy - 4, sx + 48, sy + 48], radius=6, fill=(245, 240, 246), outline=(215, 208, 218), width=1)
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
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    hashes: set[str] = set()
    rows_data = []
    log_lines = [
        "# Chiikawa Vocabulary Tracker (#96–#100) Authentic PNG Sources Log",
        "",
        "All 30 sprites (5 characters × 6 stages S0–S5) downloaded directly from `https://chiikawawallpaper.com/png/` (0 AI quota) and normalized to `500x500` RGBA transparent PNG.",
        "",
    ]

    total = 0
    for num, slug, title, char_k, bg_c, acc_c, picks in CHIIKAWA_MANIFEST:
        out_dir = ASSETS_DIR / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        for old in out_dir.glob("*"):
            if old.is_file():
                old.unlink()

        loaded = []
        log_lines.append(f"## #{num} — {title} (`{slug}`)")
        for s_i, (lbl, c_idx) in enumerate(picks):
            url = catalog[char_k][c_idx]["url"]
            raw = _download(url)
            im = _clean_and_normalize_500(Image.open(io.BytesIO(raw)), target=500, pad_ratio=0.10)
            assert im.size == (500, 500) and im.mode == "RGBA"
            a_arr = np.asarray(im.getchannel("A"))
            assert int((a_arr > 20).sum()) > 15000, f"Sprite too empty: {slug}/stage_{s_i}.png"
            assert int((a_arr <= 10).sum()) > 40000, f"Sprite not transparent: {slug}/stage_{s_i}.png"

            out_p = out_dir / f"stage_{s_i}.png"
            im.save(out_p, "PNG", optimize=True)
            h = hashlib.sha256(out_p.read_bytes()).hexdigest()
            assert h not in hashes, f"Duplicate sprite hash: {slug}/stage_{s_i}.png"
            hashes.add(h)
            loaded.append((lbl, im))
            log_lines.append(f"  - `stage_{s_i}.png` ({lbl}): {url}")
            total += 1
        log_lines.append("")
        rows_data.append((title, slug, char_k, bg_c, acc_c, loaded))
        print(f"  [CHIIKAWA OK #{num}] {slug:<24} 6x 500x500 RGBA from chiikawawallpaper.com/png/{char_k}", flush=True)

    assert total == 30
    (ASSETS_DIR / "vocab_chiikawa_96_100_sources.md").write_text("\n".join(log_lines), encoding="utf-8")
    _build_contact_sheet(rows_data, PREVIEWS_DIR / "assets_contact_sheet_vocab_chiikawa_96_100.jpg")
    print("=== ALL 30/30 CHIIKAWA SPRITES + CONTACT SHEET READY ===")


if __name__ == "__main__":
    main()
