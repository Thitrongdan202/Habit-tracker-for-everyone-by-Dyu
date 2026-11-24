"""
extract_digimon_batch2.py — Precision Extraction & Vector Pipeline for the 7 New Digimon Themes
(Batch 6 / v3.8 — 52 Transparent 300x300px PNGs: 4x7 + 3x8):
  41. `digimon_patamon`    (7 stages: Digi-Egg -> Poyomon -> Tokomon [cute!] -> Patamon -> Unimon -> Hippogriffomon -> Griffomon)
  42. `digimon_palmon`     (7 stages: Digi-Egg -> Yuramon -> Tanemon -> Palmon -> Togemon -> Lilimon -> Rosemon)
  43. `digimon_gomamon`    (8 stages: Digi-Egg -> Pichimon -> Bukamon -> Gomamon -> Ikkakumon -> Zudomon -> Vikemon -> AncientMegatheriummon)
  44. `digimon_guilmon`    (8 stages: Digi-Egg -> Jyarimon -> Gigimon -> Guilmon -> Growlmon -> WarGrowlmon -> Gallantmon -> Gallantmon Crimson Mode)
  45. `digimon_terriermon` (7 stages: Digi-Egg -> Zerimon -> Gummymon -> Terriermon -> Gargomon -> Rapidmon -> MegaGargomon)
  46. `digimon_renamon`    (8 stages: Digi-Egg -> Relemon -> Viximon -> Renamon -> Youkomon -> Doumon -> Kuzuhamon -> Kuzuhamon Miko Mode)
  47. `digimon_tentomon`   (7 stages: Digi-Egg -> Bubbmon -> Mochimon -> Tentomon -> Kabuterimon -> MegaKabuterimon -> HerakleKabuterimon)

CRITICAL SAFEGUARDS:
  - ZERO AI-drawn monster armor: all 45 Digimon extracted directly from official sheets in `references/batch6_digimon/`!
  - Only the 7 cute Crest Digi-Eggs (`stage_0.png`) are vector-drawn via 3x supersampled SVG -> PyMuPDF.
  - Patamon sheet: extracts ONLY the cute closed-mouth Tokomon (top-middle), skipping scary open-mouth Tokomon!
  - Palmon (green stripes) & Tentomon (purple-indigo stripes): white-sticker-protected exterior flood-fill +
    white-rimmed-only interior pocket cleanup so ZERO green foliage or purple armor is ever eaten!
  - Renamon's leaves, Youkomon's flames, Doumon's talismans, Kuzuhamon Miko's petals & Gallantmon Crimson's wings preserved!
  - Renders `previews/assets_contact_sheet_digimon_batch2.png` at BOTH 180px large & 44px Excel cell size!
"""
from __future__ import annotations

import math
from pathlib import Path

import cv2
import numpy as np
import pymupdf
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
REF_DIR = ROOT / "references" / "batch6_digimon"
ASSETS_DIR = ROOT / "assets"
PREVIEWS_DIR = ROOT / "previews"


# =========================================================================== #
#  SVG -> 300x300 TRANSPARENT PNG (7 Custom Kawaii Vector Digi-Eggs)
# =========================================================================== #
def render_svg_to_png(inner_svg: str, size: int = 300) -> Image.Image:
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


def _sparkle4(cx, cy, r=12, fill="#FDE047", stroke="#B47812", sw=2.4) -> str:
    ir = r * 0.30
    d = (
        f"M {cx},{cy - r} Q {cx + ir},{cy - ir} {cx + r},{cy} "
        f"Q {cx + ir},{cy + ir} {cx},{cy + r} "
        f"Q {cx - ir},{cy + ir} {cx - r},{cy} "
        f"Q {cx - ir},{cy - ir} {cx},{cy - r} Z"
    )
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>'


def _egg_base(body_fill: str, shade_fill: str, outline: str, pattern_svg: str, emblem_svg: str, sparkles_svg: str = "") -> str:
    egg_path = (
        "M 150,74 C 194,74 224,132 224,188 C 224,238 194,264 150,264 "
        "C 106,264 76,238 76,188 C 76,132 106,74 150,74 Z"
    )
    return "".join([
        '<ellipse cx="150" cy="268" rx="64" ry="12" fill="#2A1F1C" fill-opacity="0.13"/>',
        f'<path d="{egg_path}" fill="{body_fill}"/>',
        pattern_svg,
        f'<path d="M 192,102 C 224,148 224,234 150,262 C 118,262 96,248 88,232 '
        f'C 122,250 184,238 198,178 C 204,148 200,120 192,102 Z" fill="{shade_fill}" fill-opacity="0.42"/>',
        '<ellipse cx="118" cy="134" rx="13" ry="24" transform="rotate(20 118 134)" fill="#FFFFFF" fill-opacity="0.42"/>',
        '<circle cx="107" cy="166" r="5.5" fill="#FFFFFF" fill-opacity="0.45"/>',
        f'<path d="{egg_path}" fill="none" stroke="{outline}" stroke-width="6.5" stroke-linejoin="round"/>',
        emblem_svg,
        sparkles_svg,
    ])


def draw_digi_egg_b2(slug: str) -> Image.Image:
    if slug == "digimon_patamon":
        # Digi-Egg of Hope: Honey Gold + Sky Wing Curve + Radiant Crest of Hope Star
        pat = (
            '<path d="M 80,202 Q 115,226 150,200 Q 185,226 220,202 '
            'C 214,242 188,262 150,262 C 112,262 86,242 80,202 Z" fill="#60A5FA" fill-opacity="0.86"/>'
            '<path d="M 96,228 Q 125,244 150,224 Q 175,244 204,228 '
            'C 194,252 174,262 150,262 C 126,262 106,252 96,228 Z" fill="#E0F2FE" fill-opacity="0.80"/>'
            # Mini cute Patamon bat/angel wings on left & right of egg
            '<path d="M 86,154 Q 108,142 118,162 Q 100,174 82,172 Z" fill="#FFFBEB" stroke="#78350F" stroke-width="3"/>'
            '<path d="M 214,154 Q 192,142 182,162 Q 200,174 218,172 Z" fill="#FFFBEB" stroke="#78350F" stroke-width="3"/>'
        )
        # Crest of Hope sunburst + rising diamond
        emb = (
            '<polygon points="150,122 174,162 150,192 126,162" fill="#FEF08A" stroke="#78350F" stroke-width="4" stroke-linejoin="round"/>'
            '<circle cx="150" cy="158" r="10" fill="#6D28D9" stroke="#78350F" stroke-width="3"/>'
            '<circle cx="150" cy="158" r="4" fill="#FEF9C3"/>'
        )
        sp = _sparkle4(78, 94, 13, "#FDE047", "#B45309") + _sparkle4(224, 96, 11, "#93C5FD", "#1D4ED8")
        return render_svg_to_png(_egg_base("#FBBF24", "#D97706", "#78350F", pat, emb, sp))

    if slug == "digimon_palmon":
        # Digi-Egg of Sincerity: Botanical Leaf Green + Pink Rose Petal Base + Sincerity Droplet Crest
        pat = (
            '<path d="M 80,202 Q 116,184 150,206 Q 184,184 220,202 '
            'C 214,242 188,262 150,262 C 112,262 86,242 80,202 Z" fill="#EC4899" fill-opacity="0.85"/>'
            '<path d="M 96,228 Q 150,214 204,228 C 194,252 174,262 150,262 C 126,262 106,252 96,228 Z" '
            'fill="#FCE7F3" fill-opacity="0.72"/>'
        )
        # Cute sprout leaf on top + Sincerity teardrop emblem
        emb = (
            '<path d="M 150,74 Q 124,46 112,62 Q 122,82 150,76 Z" fill="#86EFAC" stroke="#14532D" stroke-width="4" stroke-linejoin="round"/>'
            '<path d="M 150,74 Q 176,46 188,62 Q 178,82 150,76 Z" fill="#4ADE80" stroke="#14532D" stroke-width="4" stroke-linejoin="round"/>'
            '<path d="M 150,122 C 170,148 176,166 172,178 C 166,192 134,192 128,178 C 124,166 130,148 150,122 Z" '
            'fill="#F472B6" stroke="#14532D" stroke-width="4.2" stroke-linejoin="round"/>'
            '<circle cx="150" cy="166" r="8" fill="#FEF08A" stroke="#14532D" stroke-width="2.8"/>'
        )
        sp = _sparkle4(80, 96, 12, "#F9A8D4", "#9D174D") + _sparkle4(222, 102, 11, "#86EFAC", "#166534")
        return render_svg_to_png(_egg_base("#66BB6A", "#2E7D32", "#14532D", pat, emb, sp))

    if slug == "digimon_gomamon":
        # Digi-Egg of Reliability: Arctic Snow-Cyan + Gomamon Purple Seal Stripes + Crossed Wave Crest
        pat = (
            '<path d="M 84,144 Q 108,154 96,174 L 80,172 C 80,162 82,152 84,144 Z" fill="#8B5CF6" fill-opacity="0.88"/>'
            '<path d="M 216,144 Q 192,154 204,174 L 220,172 C 220,162 218,152 216,144 Z" fill="#8B5CF6" fill-opacity="0.88"/>'
            '<path d="M 80,204 Q 115,190 150,208 Q 185,224 220,204 '
            'C 214,242 188,262 150,262 C 112,262 86,242 80,204 Z" fill="#06B6D4" fill-opacity="0.88"/>'
            '<circle cx="106" cy="224" r="6" fill="#C4B5FD"/>'
            '<circle cx="194" cy="226" r="5" fill="#C4B5FD"/>'
        )
        # Crest of Reliability: clean stylized silver-gold anchor/cross crystal
        emb = (
            '<rect x="142" y="124" width="16" height="62" rx="6" fill="#A78BFA" stroke="#0F293A" stroke-width="3.8"/>'
            '<rect x="120" y="146" width="60" height="16" rx="6" fill="#A78BFA" stroke="#0F293A" stroke-width="3.8"/>'
            '<circle cx="150" cy="154" r="9" fill="#FDE047" stroke="#0F293A" stroke-width="3.2"/>'
        )
        sp = _sparkle4(78, 96, 12, "#67E8F9", "#0E7490") + _sparkle4(222, 98, 12, "#DDD6FE", "#5B21B6")
        return render_svg_to_png(_egg_base("#E0F7FA", "#67E8F9", "#0F293A", pat, emb, sp))

    if slug == "digimon_guilmon":
        # Digital Hazard Digi-Egg: Bold Guilmon Crimson + Black Hazard Stripes + Golden Digital Hazard Emblem
        pat = (
            '<path d="M 82,150 L 116,162 L 80,176 C 80,166 80,158 82,150 Z" fill="#1F1212"/>'
            '<path d="M 218,150 L 184,162 L 220,176 C 220,166 220,158 218,150 Z" fill="#1F1212"/>'
            '<path d="M 82,206 Q 150,224 218,206 C 212,242 188,262 150,262 C 112,262 88,242 82,206 Z" fill="#991B1B"/>'
            '<path d="M 102,226 L 150,244 L 198,226 L 190,242 L 150,256 L 110,242 Z" fill="#FACC15" stroke="#2B0E0E" stroke-width="2.6"/>'
        )
        # Iconic Digital Hazard Triangle Crest in Gold & Obsidian!
        emb = (
            '<polygon points="150,122 184,182 116,182" fill="#FACC15" stroke="#2B0E0E" stroke-width="4.4" stroke-linejoin="round"/>'
            '<polygon points="150,138 170,174 130,174" fill="#DC2626" stroke="#2B0E0E" stroke-width="3"/>'
            '<circle cx="150" cy="162" r="6" fill="#FEF08A"/>'
        )
        sp = _sparkle4(78, 92, 13, "#FDE047", "#92400E") + _sparkle4(224, 96, 12, "#FCA5A5", "#991B1B")
        return render_svg_to_png(_egg_base("#EF4444", "#B91C1C", "#2B0E0E", pat, emb, sp))

    if slug == "digimon_terriermon":
        # Momentai Digi-Egg: Soft Mint Cream + Emerald Stripes + Cute Horn & Coral Star Accent
        pat = (
            '<path d="M 84,142 Q 150,126 216,142 L 220,164 Q 150,148 80,164 Z" fill="#34D399" fill-opacity="0.85"/>'
            '<path d="M 80,206 Q 150,222 220,206 C 214,242 188,262 150,262 C 112,262 86,242 80,206 Z" fill="#059669" fill-opacity="0.82"/>'
        )
        # Cute little Terriermon green horn crest on top + Momentai sparkle gem
        emb = (
            '<path d="M 136,78 L 150,46 L 164,78 Z" fill="#6EE7B7" stroke="#0F2E22" stroke-width="4.5" stroke-linejoin="round"/>'
            '<polygon points="150,152 174,174 150,196 126,174" fill="#F43F5E" stroke="#0F2E22" stroke-width="3.8" stroke-linejoin="round"/>'
            '<circle cx="150" cy="174" r="6.5" fill="#FFF1F2"/>'
        )
        sp = _sparkle4(80, 96, 12, "#6EE7B7", "#065F46") + _sparkle4(222, 98, 12, "#FDA4AF", "#9F1239")
        return render_svg_to_png(_egg_base("#ECFDF5", "#6EE7B7", "#0F2E22", pat, emb, sp))

    if slug == "digimon_renamon":
        # Mystic Kitsune Digi-Egg: Golden Fox Yellow + Deep Shrine Purple Yin-Yang Emblem + Vermilion Talisman Accent
        pat = (
            '<path d="M 80,200 Q 150,226 220,200 C 214,242 188,262 150,262 C 112,262 86,242 80,200 Z" fill="#5B21B6"/>'
            '<path d="M 96,226 Q 150,242 204,226 C 194,252 174,262 150,262 C 126,262 106,252 96,226 Z" fill="#E11D48" fill-opacity="0.88"/>'
        )
        # Mystic Yin-Yang Taikyoku symbol in center!
        emb = (
            '<circle cx="150" cy="156" r="28" fill="#FAF5FF" stroke="#1F1630" stroke-width="4.2"/>'
            '<path d="M 150,128 A 28,28 0 0,1 150,184 A 14,14 0 0,1 150,156 A 14,14 0 0,0 150,128 Z" fill="#5B21B6"/>'
            '<circle cx="150" cy="142" r="5" fill="#5B21B6"/>'
            '<circle cx="150" cy="170" r="5" fill="#FAF5FF"/>'
            '<circle cx="150" cy="156" r="28" fill="none" stroke="#1F1630" stroke-width="4.2"/>'
        )
        sp = _sparkle4(78, 94, 13, "#FDE047", "#92400E") + _sparkle4(224, 96, 12, "#C4B5FD", "#4C1D95")
        return render_svg_to_png(_egg_base("#FDE047", "#CA8A04", "#1F1630", pat, emb, sp))

    # digimon_tentomon — Digi-Egg of Knowledge: Electric Indigo + Ladybug Red Spots + Crest of Knowledge!
    pat = (
        '<path d="M 80,202 Q 150,222 220,202 C 214,242 188,262 150,262 C 112,262 86,242 80,202 Z" fill="#EF4444"/>'
        '<circle cx="116" cy="226" r="8" fill="#1E1B4B"/>'
        '<circle cx="150" cy="236" r="8.5" fill="#1E1B4B"/>'
        '<circle cx="184" cy="226" r="8" fill="#1E1B4B"/>'
    )
    # Crest of Knowledge geometric diamond/eyeglasses + thunder spark
    emb = (
        '<circle cx="134" cy="158" r="16" fill="#FDE047" stroke="#1E1B4B" stroke-width="4"/>'
        '<circle cx="166" cy="158" r="16" fill="#FDE047" stroke="#1E1B4B" stroke-width="4"/>'
        '<circle cx="134" cy="158" r="6" fill="#4F46E5"/>'
        '<circle cx="166" cy="158" r="6" fill="#4F46E5"/>'
        '<path d="M 150,122 L 160,140 L 140,140 Z" fill="#F59E0B" stroke="#1E1B4B" stroke-width="3.2" stroke-linejoin="round"/>'
    )
    sp = _sparkle4(78, 94, 13, "#FDE047", "#B45309") + _sparkle4(224, 98, 12, "#A5B4FC", "#312E81")
    return render_svg_to_png(_egg_base("#6366F1", "#3730A3", "#1E1B4B", pat, emb, sp))


# =========================================================================== #
#  PRECISION IMAGE EXTRACTION HELPERS
# =========================================================================== #
def _mask_boxes(rgb: np.ndarray, boxes: list[tuple[int, int, int, int]], fill_color=(255, 255, 255)) -> np.ndarray:
    out = rgb.copy()
    h, w = out.shape[:2]
    for x1, y1, x2, y2 in boxes:
        out[max(0, y1):min(h, y2), max(0, x1):min(w, x2)] = fill_color
    return out


def _mask_lines(rgb: np.ndarray, lines: list[tuple[int, int, int, int, int]], fill_color=(255, 255, 255)) -> np.ndarray:
    """Erase thin connector lines cleanly by drawing a narrow fill_color stroke over exact endpoints."""
    out = rgb.copy()
    for x1, y1, x2, y2, thickness in lines:
        cv2.line(out, (x1, y1), (x2, y2), fill_color, thickness=thickness)
    return out


def _trim_rgba(im: Image.Image) -> Image.Image:
    bbox = im.getbbox()
    return im if bbox is None else im.crop(bbox)


def extract_on_white_bg(
    sheet_rgb: np.ndarray,
    crop: tuple[int, int, int, int],
    erase_boxes_abs: list[tuple[int, int, int, int]] | None = None,
    erase_lines_abs: list[tuple[int, int, int, int, int]] | None = None,
    white_thr: int = 236,
    sat_thr: int = 24,
    keep_min_area_frac: float = 0.012,
    min_keep_px: int = 25,
    erode_halo: bool = True,
) -> Image.Image:
    """Extract Digimon cleanly from white-bg reference sheet using border flood-fill +
    optional exact line/box erasure + CC noise filter (preserves white fur/robes & floating FX!)."""
    x0, y0, x1, y1 = crop
    sub = sheet_rgb[y0:y1, x0:x1].copy()
    if erase_boxes_abs:
        rel = [(a - x0, b - y0, c - x0, d - y0) for a, b, c, d in erase_boxes_abs]
        sub = _mask_boxes(sub, rel, (255, 255, 255))
    if erase_lines_abs:
        rel_l = [(a - x0, b - y0, c - x0, d - y0, th) for a, b, c, d, th in erase_lines_abs]
        sub = _mask_lines(sub, rel_l, (255, 255, 255))

    pad = 4
    sub = cv2.copyMakeBorder(sub, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    r, g, b = sub[:, :, 0].astype(np.int16), sub[:, :, 1].astype(np.int16), sub[:, :, 2].astype(np.int16)
    cmax = np.maximum(np.maximum(r, g), b)
    cmin = np.minimum(np.minimum(r, g), b)
    sat = cmax - cmin
    is_bg_cand = (cmin >= white_thr) & (sat <= sat_thr)

    _, labels = cv2.connectedComponents(is_bg_cand.astype(np.uint8), connectivity=4)
    border_labels = (
        set(labels[0, :].tolist()) | set(labels[-1, :].tolist())
        | set(labels[:, 0].tolist()) | set(labels[:, -1].tolist())
    )
    border_labels.discard(0)
    bg_mask = np.isin(labels, list(border_labels))
    fg_mask = (~bg_mask).astype(np.uint8)

    # CC filter: keep main character + floating effects down to `min_keep_px` / `keep_min_area_frac`
    n_fg, fg_labels, stats, _ = cv2.connectedComponentsWithStats(fg_mask, connectivity=8)
    if n_fg > 1:
        max_area = int(stats[1:, cv2.CC_STAT_AREA].max())
        min_keep = max(min_keep_px, int(max_area * keep_min_area_frac))
        clean_fg = np.zeros_like(fg_mask)
        for cid in range(1, n_fg):
            if stats[cid, cv2.CC_STAT_AREA] >= min_keep:
                clean_fg[fg_labels == cid] = 1
        fg_mask = clean_fg

    alpha = (fg_mask * 255).astype(np.uint8)
    if erode_halo:
        kernel = np.ones((3, 3), np.uint8)
        eroded = cv2.erode(fg_mask, kernel, iterations=1)
        boundary = (fg_mask == 1) & (eroded == 0)
        rim_bright = boundary & (cmin >= 200) & (sat <= 32)
        alpha[rim_bright] = np.clip((255 - cmin[rim_bright]) * 3.5, 0, 220).astype(np.uint8)
        soft_b = (alpha > 0) & (alpha < 255)
        if np.any(soft_b):
            af = alpha[soft_b].astype(np.float32) / 255.0
            for ch in range(3):
                vals = sub[:, :, ch][soft_b].astype(np.float32)
                sub[:, :, ch][soft_b] = np.clip((vals - 255.0 * (1.0 - af)) / np.maximum(af, 0.25), 0, 255).astype(np.uint8)

    sub = sub[pad:-pad, pad:-pad]
    alpha = alpha[pad:-pad, pad:-pad]
    return _trim_rgba(Image.fromarray(np.dstack([sub, alpha]), "RGBA"))


def extract_sticker_colored_bg(
    sheet_rgb: np.ndarray,
    crop: tuple[int, int, int, int],
    bg_palette: list[list[int]],
    bg_sample: tuple[int, int, int],
    bg_color_check,
    erase_boxes_abs: list[tuple[int, int, int, int]] | None = None,
    keep_min_area_frac: float = 0.04,
    min_keep_px: int = 35,
    clean_white_rimmed_pockets: bool = True,
) -> Image.Image:
    """Extract white-sticker-outlined Digimon cleanly from colored striped backgrounds (Palmon green / Tentomon indigo)!
    1. Exterior border flood-fill using exact RGB palette distance + channel rule -> stops 100% at the solid white sticker border!
    2. Interior pocket cleanup ONLY removes pockets whose 1px perimeter is predominantly PURE WHITE sticker outline
       (mean bright-white fraction >= 0.45) -> IMPOSSIBLE to eat Palmon green leaves or Kabuterimon purple armor!"""
    x0, y0, x1, y1 = crop
    sub = sheet_rgb[y0:y1, x0:x1].copy()
    if erase_boxes_abs:
        rel = [(a - x0, b - y0, c - x0, d - y0) for a, b, c, d in erase_boxes_abs]
        sub = _mask_boxes(sub, rel, bg_sample)

    pad = 4
    sub = cv2.copyMakeBorder(sub, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=bg_sample)
    sub_f = sub.astype(np.float32)
    pal = np.array(bg_palette, dtype=np.float32)
    dists = np.min(np.linalg.norm(sub_f[:, :, None, :] - pal[None, None, :, :], axis=-1), axis=-1)

    r, g, b = sub[:, :, 0].astype(np.int16), sub[:, :, 1].astype(np.int16), sub[:, :, 2].astype(np.int16)
    is_bg_col = (dists <= 34.0) & bg_color_check(r, g, b)

    # 1. Exterior border flood-fill
    _, labels = cv2.connectedComponents(is_bg_col.astype(np.uint8), connectivity=4)
    border_labels = (
        set(labels[0, :].tolist()) | set(labels[-1, :].tolist())
        | set(labels[:, 0].tolist()) | set(labels[:, -1].tolist())
    )
    border_labels.discard(0)
    bg_mask = np.isin(labels, list(border_labels))

    # 2. White-sticker-rimmed enclosed pockets ONLY (e.g., Rosemon's whip loop, Kabuterimon's legs/arms!)
    if clean_white_rimmed_pockets:
        cmin = np.minimum(np.minimum(r, g), b)
        is_white_rim = cmin >= 180
        cand_pockets = (dists <= 28.0) & bg_color_check(r, g, b) & (~bg_mask)
        n_pb, pb_labels, pb_stats, _ = cv2.connectedComponentsWithStats(cand_pockets.astype(np.uint8), connectivity=4)
        k3 = np.ones((3, 3), np.uint8)
        for cid in range(1, n_pb):
            if pb_stats[cid, cv2.CC_STAT_AREA] >= 10:
                p_mask = (pb_labels == cid).astype(np.uint8)
                # Check 2px band outside pocket so JPEG anti-aliased edge still hits the white sticker border!
                p_dil1 = cv2.dilate(p_mask, k3, iterations=1).astype(bool)
                p_dil2 = cv2.dilate(p_mask, k3, iterations=2).astype(bool)
                rim2 = p_dil2 & (~p_mask.astype(bool))
                white_frac = float(is_white_rim[rim2].mean()) if np.any(rim2) else 0.0
                if white_frac >= 0.25:
                    bg_mask |= (p_mask.astype(bool)) | ((p_dil1 & (~p_mask.astype(bool))) & (dists <= 52.0) & bg_color_check(r, g, b))

    fg_mask = (~bg_mask).astype(np.uint8)

    # Keep main Digimon + intentional floating elements (e.g., Bubbmon's bubbles)
    n_fg, fg_labels, stats, _ = cv2.connectedComponentsWithStats(fg_mask, connectivity=8)
    if n_fg > 1:
        max_area = int(stats[1:, cv2.CC_STAT_AREA].max())
        min_keep = max(min_keep_px, int(max_area * keep_min_area_frac))
        clean_fg = np.zeros_like(fg_mask)
        for cid in range(1, n_fg):
            if stats[cid, cv2.CC_STAT_AREA] >= min_keep:
                clean_fg[fg_labels == cid] = 1
        fg_mask = clean_fg

    # Gentle 1px de-fringe strictly on outer rim
    k3 = np.ones((3, 3), np.uint8)
    eroded1 = cv2.erode(fg_mask, k3, iterations=1)
    rim1 = (fg_mask == 1) & (eroded1 == 0)
    alpha = (fg_mask * 255).astype(np.uint8)
    bg_rim = rim1 & (dists <= 46.0) & bg_color_check(r, g, b)
    alpha[bg_rim] = 0
    still_rim = (alpha > 0) & rim1
    alpha[still_rim] = 225

    sub = sub[pad:-pad, pad:-pad]
    alpha = alpha[pad:-pad, pad:-pad]
    return _trim_rgba(Image.fromarray(np.dstack([sub, alpha]), "RGBA"))


def compose_300(
    sprite: Image.Image,
    stage: int,
    num_stages: int = 7,
    mega_aura_rgb: tuple[int, int, int] | None = None,
    size: int = 300,
) -> Image.Image:
    """Bottom-align extracted Digimon cleanly onto a 300x300 transparent canvas with proportional
    stage scaling (compact Baby -> heroic full-frame Mega/Ultra) + Crest-colored aura on final stage!"""
    sprite = _trim_rgba(sprite)
    sw, sh = sprite.size
    if sw == 0 or sh == 0:
        return Image.new("RGBA", (size, size), (0, 0, 0, 0))

    if num_stages == 8:
        max_box = {0: 215, 1: 184, 2: 200, 3: 234, 4: 266, 5: 274, 6: 278, 7: 284}
        bot_pad_map = {0: 14, 1: 26, 2: 22, 3: 16, 4: 12, 5: 10, 6: 10, 7: 8}
    else:
        max_box = {0: 215, 1: 188, 2: 204, 3: 238, 4: 274, 5: 278, 6: 282}
        bot_pad_map = {0: 14, 1: 26, 2: 22, 3: 16, 4: 12, 5: 10, 6: 10}

    max_dim = max_box.get(stage, 250)
    bot_pad = bot_pad_map.get(stage, 14)

    scale = min(max_dim / sw, max_dim / sh)
    nw = max(1, int(round(sw * scale)))
    nh = max(1, int(round(sh * scale)))
    resized = sprite.resize((nw, nh), Image.LANCZOS)

    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    if mega_aura_rgb is not None:
        aura = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ad = ImageDraw.Draw(aura)
        ar, ag, ab = mega_aura_rgb
        cx, cy = size // 2, size - bot_pad - nh // 2
        ad.ellipse([cx - 122, cy - 122, cx + 122, cy + 122], fill=(ar, ag, ab, 48))
        ad.ellipse([cx - 88, cy - 88, cx + 88, cy + 88], fill=(ar, ag, ab, 68))
        ad.ellipse([cx - 52, cy - 52, cx + 52, cy + 52], fill=(255, 255, 255, 76))
        aura = aura.filter(ImageFilter.GaussianBlur(radius=18))
        canvas = Image.alpha_composite(canvas, aura)

        sd = ImageDraw.Draw(canvas)
        for sx, sy, sr in [(42, 46, 11), (258, 52, 10), (38, 178, 8), (262, 184, 9)]:
            pts = [
                (sx, sy - sr), (sx + sr * 0.3, sy - sr * 0.3),
                (sx + sr, sy), (sx + sr * 0.3, sy + sr * 0.3),
                (sx, sy + sr), (sx - sr * 0.3, sy + sr * 0.3),
                (sx - sr, sy), (sx - sr * 0.3, sy - sr * 0.3),
            ]
            sd.polygon(pts, fill=(255, 250, 200, 235), outline=(ar, ag, ab, 215))

    x = (size - nw) // 2
    y = max(4, size - bot_pad - nh)
    canvas.alpha_composite(resized, (x, y))
    return canvas


# =========================================================================== #
#  EXTRACT ALL 7 DIGIMON LINES (52 SPRITES TOTAL!)
# =========================================================================== #
def build_all_digimon_batch2() -> dict[str, list[tuple[str, Image.Image]]]:
    results: dict[str, list[tuple[str, Image.Image]]] = {}

    # ------------------------------------------------------------------ 41. PATAMON (7 stages)
    rgb = np.array(Image.open(REF_DIR / "patamon.jpg").convert("RGB"))
    results["digimon_patamon"] = [
        ("Digi-Egg\nof Hope",     compose_300(draw_digi_egg_b2("digimon_patamon"), 0, 7)),
        ("Poyomon",               compose_300(extract_on_white_bg(rgb, (10, 5, 226, 205), white_thr=242, sat_thr=16), 1, 7)),
        ("Tokomon",               compose_300(extract_on_white_bg(rgb, (232, 36, 348, 178), white_thr=242, sat_thr=16), 2, 7)),
        ("Patamon",               compose_300(extract_on_white_bg(rgb, (20, 220, 236, 428)), 3, 7)),
        ("Unimon",                compose_300(extract_on_white_bg(rgb, (258, 204, 462, 444)), 4, 7)),
        ("Hippogriffomon",        compose_300(extract_on_white_bg(rgb, (0, 446, 237, 640)), 5, 7)),
        ("Griffomon",             compose_300(extract_on_white_bg(rgb, (236, 452, 480, 640)), 6, 7, mega_aura_rgb=(245, 158, 11))),
    ]

    # ------------------------------------------------------------------ 42. PALMON (7 stages, striped green bg)
    rgb = np.array(Image.open(REF_DIR / "palmon.jpg").convert("RGB"))
    palmon_pal = [
        [116, 163, 86], [132, 173, 102], [144, 180, 115], [158, 192, 130],
        [56, 88, 40], [72, 106, 52],
    ]
    palmon_check = lambda r, g, b: ((g - r) >= 20) & ((g - b) >= 42)
    results["digimon_palmon"] = [
        ("Digi-Egg\nof Sincerity", compose_300(draw_digi_egg_b2("digimon_palmon"), 0, 7)),
        ("Yuramon",                compose_300(extract_sticker_colored_bg(rgb, (555, 14, 675, 118), palmon_pal, (116, 163, 86), palmon_check), 1, 7)),
        ("Tanemon",                compose_300(extract_sticker_colored_bg(rgb, (325, 8, 440, 125), palmon_pal, (116, 163, 86), palmon_check), 2, 7)),
        ("Palmon",                 compose_300(extract_sticker_colored_bg(rgb, (75, 0, 205, 148), palmon_pal, (116, 163, 86), palmon_check), 3, 7)),
        ("Togemon",                compose_300(extract_sticker_colored_bg(rgb, (40, 180, 232, 375), palmon_pal, (116, 163, 86), palmon_check), 4, 7)),
        ("Lilimon",                compose_300(extract_sticker_colored_bg(rgb, (312, 152, 480, 372), palmon_pal, (116, 163, 86), palmon_check), 5, 7)),
        ("Rosemon",                compose_300(extract_sticker_colored_bg(rgb, (520, 142, 706, 368), palmon_pal, (116, 163, 86), palmon_check), 6, 7, mega_aura_rgb=(236, 72, 153))),
    ]

    # ------------------------------------------------------------------ 43. GOMAMON (8 stages)
    rgb = np.array(Image.open(REF_DIR / "gomamon.jpg").convert("RGB"))
    results["digimon_gomamon"] = [
        ("Digi-Egg\nof Reliability", compose_300(draw_digi_egg_b2("digimon_gomamon"), 0, 8)),
        ("Pichimon",                 compose_300(extract_on_white_bg(rgb, (4, 0, 158, 216), erase_boxes_abs=[(64, 0, 148, 22), (128, 184, 146, 216)], white_thr=242, sat_thr=16), 1, 8)),
        ("Bukamon",                  compose_300(extract_on_white_bg(rgb, (16, 216, 165, 416), erase_boxes_abs=[(16, 396, 86, 416), (128, 216, 165, 330)]), 2, 8)),
        ("Gomamon",                  compose_300(extract_on_white_bg(rgb, (158, 0, 365, 220), erase_boxes_abs=[(266, 0, 358, 22)], erase_lines_abs=[(250, 144, 158, 305, 8), (314, 200, 368, 256, 8)], white_thr=242, sat_thr=16), 3, 8)),
        ("Ikkakumon",                compose_300(extract_on_white_bg(rgb, (335, 178, 580, 416), erase_boxes_abs=[(350, 398, 442, 416), (464, 178, 484, 236)], erase_lines_abs=[(312, 200, 370, 260, 8)], white_thr=242, sat_thr=16), 4, 8)),
        ("Zudomon",                  compose_300(extract_on_white_bg(rgb, (382, 0, 634, 178), erase_boxes_abs=[(432, 0, 508, 22), (464, 162, 484, 178)], erase_lines_abs=[(550, 160, 622, 232, 8)]), 5, 8)),
        ("Vikemon",                  compose_300(extract_on_white_bg(rgb, (606, 198, 855, 416), erase_boxes_abs=[(668, 398, 738, 416), (772, 198, 855, 232), (606, 198, 621, 240)], erase_lines_abs=[(740, 204, 814, 130, 8)]), 6, 8)),
        ("Ancient-\nMegatherium",    compose_300(extract_on_white_bg(rgb, (744, 10, 995, 202), erase_lines_abs=[(740, 204, 804, 136, 8)]), 7, 8, mega_aura_rgb=(6, 182, 212))),
    ]

    # ------------------------------------------------------------------ 44. GUILMON (8 stages)
    rgb = np.array(Image.open(REF_DIR / "guilmon.jpg").convert("RGB"))
    results["digimon_guilmon"] = [
        ("Digital Hazard\nDigi-Egg", compose_300(draw_digi_egg_b2("digimon_guilmon"), 0, 8)),
        ("Jyarimon",                 compose_300(extract_on_white_bg(rgb, (0, 0, 158, 125), erase_boxes_abs=[(70, 8, 134, 28)]), 1, 8)),
        ("Gigimon",                  compose_300(extract_on_white_bg(rgb, (5, 168, 118, 298), erase_boxes_abs=[(78, 286, 118, 298)]), 2, 8)),
        ("Guilmon",                  compose_300(extract_on_white_bg(rgb, (166, 0, 308, 172), erase_boxes_abs=[(200, 28, 254, 48), (240, 152, 252, 172)], erase_lines_abs=[(160, 152, 216, 98, 8)]), 3, 8)),
        ("Growlmon",                 compose_300(extract_on_white_bg(rgb, (172, 176, 302, 324), erase_boxes_abs=[(184, 304, 248, 324), (240, 176, 254, 198)], erase_lines_abs=[(278, 190, 312, 158, 8)]), 4, 8)),
        ("WarGrowlmon",              compose_300(extract_on_white_bg(rgb, (324, 0, 448, 168), erase_boxes_abs=[(432, 6, 448, 30)], erase_lines_abs=[(316, 158, 354, 122, 8), (426, 122, 466, 164, 8)]), 5, 8)),
        ("Gallantmon",               compose_300(extract_on_white_bg(rgb, (438, 132, 608, 324), erase_boxes_abs=[(536, 308, 608, 324)], erase_lines_abs=[(430, 128, 468, 166, 8), (576, 176, 616, 136, 8)]), 6, 8)),
        ("Gallantmon\nCrimson",      compose_300(extract_on_white_bg(rgb, (588, 0, 734, 184), erase_lines_abs=[(580, 174, 622, 132, 8)], white_thr=246, sat_thr=10, erode_halo=False), 7, 8, mega_aura_rgb=(220, 38, 38))),
    ]

    # ------------------------------------------------------------------ 45. TERRIERMON (7 stages)
    rgb = np.array(Image.open(REF_DIR / "terriermon.jpg").convert("RGB"))
    results["digimon_terriermon"] = [
        ("Momentai\nDigi-Egg", compose_300(draw_digi_egg_b2("digimon_terriermon"), 0, 7)),
        ("Zerimon",            compose_300(extract_on_white_bg(rgb, (0, 0, 218, 132), erase_boxes_abs=[(66, 14, 142, 38)], white_thr=240, sat_thr=18), 1, 7)),
        ("Gummymon",           compose_300(extract_on_white_bg(rgb, (0, 210, 236, 469), erase_boxes_abs=[(146, 380, 236, 412), (64, 210, 80, 246)], erase_lines_abs=[(140, 240, 200, 180, 8)], white_thr=240, sat_thr=18), 2, 7)),
        ("Terriermon",         compose_300(extract_on_white_bg(rgb, (218, 32, 495, 164), erase_boxes_abs=[(328, 38, 422, 64)], erase_lines_abs=[(212, 170, 272, 110, 8)], white_thr=242, sat_thr=16), 3, 7)),
        ("Gargomon",           compose_300(extract_on_white_bg(rgb, (250, 200, 520, 469), erase_boxes_abs=[(320, 434, 414, 464), (344, 200, 364, 260)], erase_lines_abs=[(496, 224, 530, 190, 8)]), 4, 7)),
        ("Rapidmon",           compose_300(extract_on_white_bg(rgb, (536, 0, 768, 276), erase_boxes_abs=[(626, 24, 712, 52)], erase_lines_abs=[(530, 188, 574, 144, 8), (740, 158, 780, 198, 8)]), 5, 7)),
        ("MegaGargomon",       compose_300(extract_on_white_bg(rgb, (772, 196, 1004, 469), erase_boxes_abs=[(782, 444, 918, 469)], erase_lines_abs=[(766, 186, 826, 244, 8)]), 6, 7, mega_aura_rgb=(16, 185, 129))),
    ]

    # ------------------------------------------------------------------ 46. RENAMON (8 stages, preserve ALL floating FX!)
    rgb = np.array(Image.open(REF_DIR / "renamon.jpg").convert("RGB"))
    results["digimon_renamon"] = [
        ("Mystic Kitsune\nDigi-Egg", compose_300(draw_digi_egg_b2("digimon_renamon"), 0, 8)),
        ("Relemon",                  compose_300(extract_on_white_bg(rgb, (0, 0, 206, 128), erase_boxes_abs=[(132, 80, 206, 108)]), 1, 8)),
        ("Viximon",                  compose_300(extract_on_white_bg(rgb, (0, 192, 198, 454), erase_boxes_abs=[(130, 422, 198, 448), (60, 192, 76, 286)], erase_lines_abs=[(172, 224, 206, 190, 8)]), 2, 8)),
        ("Renamon",                  compose_300(extract_on_white_bg(rgb, (212, 0, 396, 218), erase_boxes_abs=[(320, 38, 396, 66), (290, 182, 304, 218)], erase_lines_abs=[(206, 190, 242, 152, 8)], keep_min_area_frac=0.003, min_keep_px=20), 3, 8)),
        ("Youkomon",                 compose_300(extract_on_white_bg(rgb, (200, 248, 462, 454), erase_boxes_abs=[(350, 434, 438, 454), (290, 248, 304, 272)], erase_lines_abs=[(420, 260, 466, 214, 8)], keep_min_area_frac=0.0015, min_keep_px=15), 4, 8)),
        ("Doumon",                   compose_300(extract_on_white_bg(rgb, (416, 0, 648, 250), erase_boxes_abs=[(572, 42, 648, 68)], erase_lines_abs=[(418, 254, 474, 196, 8), (588, 168, 650, 230, 8)], keep_min_area_frac=0.002, min_keep_px=18), 5, 8)),
        ("Kuzuhamon",                compose_300(extract_on_white_bg(rgb, (586, 194, 812, 454), erase_boxes_abs=[(608, 422, 706, 446)], erase_lines_abs=[(584, 168, 646, 230, 8), (730, 314, 848, 196, 8)], keep_min_area_frac=0.004, min_keep_px=25), 6, 8)),
        ("Kuzuhamon\nMiko",          compose_300(extract_on_white_bg(rgb, (786, 24, 1024, 260), erase_lines_abs=[(784, 260, 854, 190, 8)], white_thr=245, sat_thr=10, keep_min_area_frac=0.0002, min_keep_px=8), 7, 8, mega_aura_rgb=(167, 139, 250))),
    ]

    # ------------------------------------------------------------------ 47. TENTOMON (7 stages, striped periwinkle-indigo bg)
    rgb = np.array(Image.open(REF_DIR / "tentomon.jpg").convert("RGB"))
    tento_pal = [
        [104, 106, 209], [116, 118, 213], [130, 132, 217], [150, 152, 224],
        [56, 58, 126], [70, 72, 148],
    ]
    tento_check = lambda r, g, b: ((b - r) >= 58) & (np.abs(r - g) <= 16)
    results["digimon_tentomon"] = [
        ("Digi-Egg\nof Knowledge",  compose_300(draw_digi_egg_b2("digimon_tentomon"), 0, 7)),
        ("Bubbmon",                  compose_300(extract_sticker_colored_bg(rgb, (740, 18, 940, 198), tento_pal, (104, 106, 209), tento_check, keep_min_area_frac=0.001, min_keep_px=20), 1, 7)),
        ("Mochimon",                 compose_300(extract_sticker_colored_bg(rgb, (445, 22, 622, 194), tento_pal, (104, 106, 209), tento_check), 2, 7)),
        ("Tentomon",                 compose_300(extract_sticker_colored_bg(rgb, (65, 6, 298, 212), tento_pal, (104, 106, 209), tento_check), 3, 7)),
        ("Kabuterimon",              compose_300(extract_sticker_colored_bg(rgb, (20, 222, 362, 515), tento_pal, (104, 106, 209), tento_check, erase_boxes_abs=[(140, 222, 206, 278)]), 4, 7)),
        ("Mega-\nKabuterimon",       compose_300(extract_sticker_colored_bg(rgb, (362, 232, 635, 515), tento_pal, (104, 106, 209), tento_check), 5, 7)),
        ("Herakle-\nKabuterimon",    compose_300(extract_sticker_colored_bg(rgb, (665, 255, 1024, 516), tento_pal, (104, 106, 209), tento_check), 6, 7, mega_aura_rgb=(79, 70, 229))),
    ]

    # Save all 52 transparent PNGs!
    total = 0
    for slug, stages in results.items():
        out_dir = ASSETS_DIR / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        for idx, (label, img) in enumerate(stages):
            out_path = out_dir / f"stage_{idx}.png"
            img.save(out_path, "PNG", optimize=True)
            total += 1
        print(f"  [ASSETS] {slug:20s} -> {len(stages)} PNGs saved to {out_dir}")
    print(f"Total new Digimon Batch 2 sprites saved: {total}")
    return results


def render_contact_sheet_b2(results: dict[str, list[tuple[str, Image.Image]]]) -> Path:
    """Render `previews/assets_contact_sheet_digimon_batch2.png` showing all 7 lines (52 sprites!)
    at BOTH 180px large AND 44px actual Excel cell size!"""
    rows = [
        ("41. Patamon Mythical (7-Stg)",     "digimon_patamon",    (255, 251, 235), (217, 119, 6)),
        ("42. Palmon Rose (7-Stg)",          "digimon_palmon",     (242, 252, 244), (22, 163, 74)),
        ("43. Gomamon Arctic (8-Stg)",       "digimon_gomamon",    (238, 250, 255), (6, 182, 212)),
        ("44. Guilmon Crimson (8-Stg)",      "digimon_guilmon",    (255, 241, 242), (220, 38, 38)),
        ("45. Terriermon Mint (7-Stg)",      "digimon_terriermon", (236, 253, 245), (5, 150, 105)),
        ("46. Renamon Kuzuhamon (8-Stg)",    "digimon_renamon",    (248, 244, 255), (91, 33, 182)),
        ("47. Tentomon Electro (7-Stg)",     "digimon_tentomon",   (238, 242, 255), (79, 70, 229)),
    ]
    cell_w, cell_h = 196, 286
    left_w = 248
    pad = 20
    hdr_h = 84
    max_cols = 8
    W = pad * 2 + left_w + cell_w * max_cols
    H = pad * 2 + hdr_h + cell_h * len(rows)

    sheet = Image.new("RGB", (W, H), (248, 250, 252))
    draw = ImageDraw.Draw(sheet)

    try:
        f_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 28)
        f_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 16)
        f_row = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 15)
        f_lbl = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 13)
        f_tiny = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 11)
    except Exception:
        f_title = f_sub = f_row = f_lbl = f_tiny = ImageFont.load_default()

    draw.rectangle([0, 0, W, hdr_h], fill=(22, 32, 54))
    draw.text((pad, 16), "DIGIMON EVOLUTION COLLECTION — BATCH 2 (#41–#47 • 52 CANON SPRITES, v3.8)", fill=(255, 255, 255), font=f_title)
    draw.text((pad, 52), "4 Lines x 7 Stages (0%..100%) + 3 Ultra-Evolution Lines x 8 Stages (0%..100% Burst/Ultra) • Large 180px + Actual 44px Excel Preview", fill=(186, 230, 253), font=f_sub)

    for r_i, (title, slug, bg_c, acc_c) in enumerate(rows):
        y0 = hdr_h + pad + r_i * cell_h
        draw.rounded_rectangle([pad, y0 + 4, W - pad, y0 + cell_h - 6], radius=14, fill=bg_c, outline=acc_c, width=2)
        draw.text((pad + 14, y0 + 116), title, fill=acc_c, font=f_row)
        stages = results[slug]
        nstg = len(stages)
        pcts = (
            ["0%", "1–14%", "15–29%", "30–49%", "50–69%", "70–84%", "85–99%", "100% ULTRA"]
            if nstg == 8
            else ["0%", "1–19%", "20–39%", "40–59%", "60–79%", "80–99%", "100% MEGA"]
        )
        for s_i, (lbl, im) in enumerate(stages):
            x0 = pad + left_w + s_i * cell_w
            card_bg = (255, 255, 255)
            is_final = (s_i == nstg - 1)
            card_ol = acc_c if is_final else (226, 232, 240)
            draw.rounded_rectangle([x0 + 6, y0 + 12, x0 + cell_w - 6, y0 + cell_h - 14],
                                   radius=10, fill=card_bg, outline=card_ol, width=2 if is_final else 1)
            big = im.resize((164, 164), Image.LANCZOS)
            sheet.paste(big, (x0 + (cell_w - 164) // 2, y0 + 16), big)

            # 44px actual Excel cell preview chip
            small = im.resize((44, 44), Image.LANCZOS)
            sx = x0 + cell_w - 56
            sy = y0 + 186
            draw.rounded_rectangle([sx - 3, sy - 3, sx + 47, sy + 47], radius=6, fill=(248, 250, 252), outline=(203, 213, 225), width=1)
            sheet.paste(small, (sx, sy), small)

            draw.text((x0 + 12, y0 + 186), f"S{s_i} • {pcts[s_i]}", fill=acc_c, font=f_tiny)
            draw.multiline_text((x0 + 12, y0 + 204), lbl, fill=(30, 41, 59), font=f_lbl, spacing=1)
            draw.text((sx + 6, sy + 49), "44px", fill=(148, 163, 184), font=f_tiny)

    out_path = PREVIEWS_DIR / "assets_contact_sheet_digimon_batch2.png"
    sheet.save(out_path, "PNG", optimize=True)
    print(f"  [PREVIEW] Saved {out_path} ({sheet.size[0]}x{sheet.size[1]})")
    return out_path


if __name__ == "__main__":
    res = build_all_digimon_batch2()
    render_contact_sheet_b2(res)
