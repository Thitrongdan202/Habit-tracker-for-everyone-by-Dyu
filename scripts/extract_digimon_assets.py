"""
extract_digimon_assets.py — Precision Extraction & Vector Pipeline for the 5 Digimon 7-Stage Themes (35 PNGs):
  36. `digimon_veemon`  (Veemon -> Magnamon, Crest of Miracles)
  37. `digimon_agumon`  (Botamon -> WarGreymon, Crest of Courage)
  38. `digimon_gatomon` (YukimiBotamon -> LovelyAngemon, Crest of Light)
  39. `digimon_gabumon` (Punimon -> MetalGarurumon, Crest of Friendship)
  40. `digimon_piyomon` (Nyokimon -> Phoenixmon, Crest of Love)

Pipeline:
  1. Crops each Digimon directly from the official reference sheets in `references/batch5_digimon/`
     (ZERO off-model hand-drawn armor!).
  2. Removes white backgrounds (flood-fill + anti-aliased edge matting + connected-component cleanup)
     and Gabumon's striped blue tech background (HSV/color-distance border flood-fill + interior gap
     cleaning + edge de-fringing preserving Gabumon's white sticker border & internal blue stripes!).
  3. Vector-draws ONLY the 5 iconic Crest Digi-Eggs (`stage_0`) and Agumon's anime-accurate
     `Botamon` (`stage_1`) & `Koromon` (`stage_2`) via 3x supersampled SVG -> PyMuPDF -> 300x300 PNG.
  4. Bottom-aligns every sprite cleanly on a 300x300px transparent canvas with proportional stage
     scaling and adds a tasteful Crest-colored Digivolution aura behind `stage_6` (Mega).
  5. Renders `previews/assets_contact_sheet_digimon.png` at BOTH 180px large & 44px actual Excel cell size!
"""
from __future__ import annotations

import math
from pathlib import Path

import cv2
import numpy as np
import pymupdf
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
REF_DIR = ROOT / "references" / "batch5_digimon"
ASSETS_DIR = ROOT / "assets"
PREVIEWS_DIR = ROOT / "previews"


# =========================================================================== #
#  SVG -> 300x300 TRANSPARENT PNG HELPER (3x Supersampled via PyMuPDF)
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
    """Crisp kawaii Digimon Digi-Egg silhouette with cel-shading, custom pattern & Crest emblem.
    Note: All patterns stay strictly inside the egg Bezier (no <clipPath>, which PyMuPDF SVG ignores)."""
    egg_path = (
        "M 150,74 C 194,74 224,132 224,188 C 224,238 194,264 150,264 "
        "C 106,264 76,238 76,188 C 76,132 106,74 150,74 Z"
    )
    return "".join([
        '<ellipse cx="150" cy="268" rx="64" ry="12" fill="#2A1F1C" fill-opacity="0.13"/>',
        f'<path d="{egg_path}" fill="{body_fill}"/>',
        pattern_svg,
        # Cel shadow along lower-right curve strictly inside egg
        f'<path d="M 192,102 C 224,148 224,234 150,262 C 118,262 96,248 88,232 '
        f'C 122,250 184,238 198,178 C 204,148 200,120 192,102 Z" fill="{shade_fill}" fill-opacity="0.45"/>',
        # Crisp glossy upper-left highlight
        '<ellipse cx="118" cy="134" rx="13" ry="24" transform="rotate(20 118 134)" fill="#FFFFFF" fill-opacity="0.42"/>',
        '<circle cx="107" cy="166" r="5.5" fill="#FFFFFF" fill-opacity="0.45"/>',
        f'<path d="{egg_path}" fill="none" stroke="{outline}" stroke-width="6.5" stroke-linejoin="round"/>',
        emblem_svg,
        sparkles_svg,
    ])


def draw_digi_egg(slug: str) -> Image.Image:
    if slug == "digimon_veemon":
        # Digi-Egg of Miracles: Royal Veemon Blue + Bold Golden V-Chevron & Miracle Crest (strictly inside egg!)
        pat = (
            '<path d="M 80,172 L 150,224 L 220,172 C 222,184 221,196 218,206 L 150,254 L 82,206 C 79,196 78,184 80,172 Z" '
            'fill="#F5B800" stroke="#0D253F" stroke-width="3.2" stroke-linejoin="round"/>'
            '<path d="M 88,142 L 150,188 L 212,142 C 215,150 217,158 218,166 L 150,214 L 82,166 C 83,158 85,150 88,142 Z" '
            'fill="#60A5FA" fill-opacity="0.58"/>'
        )
        emb = (
            '<path d="M 122,126 L 150,172 L 178,126 L 164,126 L 150,150 L 136,126 Z" '
            'fill="#FDE047" stroke="#0D253F" stroke-width="4.2" stroke-linejoin="round"/>'
            '<circle cx="150" cy="108" r="9" fill="#E53935" stroke="#0D253F" stroke-width="3.8"/>'
        )
        sp = _sparkle4(78, 92, 13, "#FDE047", "#B47812") + _sparkle4(222, 102, 11, "#93C5FD", "#1E40AF")
        return render_svg_to_png(_egg_base("#1E88E5", "#0E4C8A", "#0D253F", pat, emb, sp))

    if slug == "digimon_agumon":
        # Digi-Egg of Courage: Warm Agumon Orange + Flame Red Wave Band + Sun Crest of Courage (strictly inside egg!)
        pat = (
            '<path d="M 80,204 Q 114,186 150,206 Q 186,226 220,204 '
            'C 214,242 188,262 150,262 C 112,262 86,242 80,204 Z" fill="#DC2626"/>'
            '<path d="M 88,136 L 112,148 L 84,162 Z" fill="#DC2626"/>'
            '<path d="M 212,136 L 188,148 L 216,162 Z" fill="#DC2626"/>'
        )
        # Iconic Sun Crest of Courage
        rays = []
        for k in range(8):
            ang = math.radians(k * 45)
            x1, y1 = 150 + math.cos(ang) * 20, 154 + math.sin(ang) * 20
            x2, y2 = 150 + math.cos(ang) * 33, 154 + math.sin(ang) * 33
            rays.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#2B1B12" stroke-width="7.5" stroke-linecap="round"/>')
            rays.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#FDE047" stroke-width="3.8" stroke-linecap="round"/>')
        emb = "".join(rays) + (
            '<circle cx="150" cy="154" r="18" fill="#FBBF24" stroke="#2B1B12" stroke-width="4.2"/>'
            '<circle cx="150" cy="154" r="8" fill="#FFFBEB"/>'
        )
        sp = _sparkle4(222, 92, 13, "#FDE047", "#B45309")
        return render_svg_to_png(_egg_base("#F97316", "#B45309", "#2B1B12", pat, emb, sp))

    if slug == "digimon_gatomon":
        # Digi-Egg of Light: Pearl White + Pastel Rose Lower Curve + Radiant 8-Point Crest of Light + Floating Holy Ring!
        pat = (
            '<path d="M 80,204 Q 150,224 220,204 C 214,242 188,262 150,262 C 112,262 86,242 80,204 Z" '
            'fill="#FBCFE8" fill-opacity="0.82"/>'
            '<path d="M 94,228 Q 150,242 206,228 C 196,252 176,262 150,262 C 124,262 104,252 94,228 Z" '
            'fill="#E9D5FF" fill-opacity="0.72"/>'
        )
        # Floating Golden Holy Ring above egg!
        ring = (
            '<ellipse cx="150" cy="54" rx="34" ry="11" fill="none" stroke="#3B1F3A" stroke-width="11"/>'
            '<ellipse cx="150" cy="54" rx="34" ry="11" fill="none" stroke="#FACC15" stroke-width="6"/>'
            '<ellipse cx="150" cy="54" rx="34" ry="11" fill="none" stroke="#FEF9C3" stroke-width="2" stroke-dasharray="10,12"/>'
        )
        pts = []
        for k in range(16):
            ang = math.radians(k * 22.5 - 90)
            rad = 32 if k % 2 == 0 else 15
            if k % 4 == 2:
                rad = 22
            pts.append(f"{150 + math.cos(ang) * rad:.1f},{164 + math.sin(ang) * rad:.1f}")
        emb = ring + (
            f'<polygon points="{" ".join(pts)}" fill="#F472B6" stroke="#3B1F3A" stroke-width="3.6" stroke-linejoin="round"/>'
            '<circle cx="150" cy="164" r="9" fill="#FEF08A" stroke="#3B1F3A" stroke-width="3"/>'
        )
        sp = _sparkle4(76, 100, 12, "#FDE047", "#A16207") + _sparkle4(226, 98, 12, "#F9A8D4", "#831843")
        return render_svg_to_png(_egg_base("#FFFDFD", "#E9D5FF", "#3B1F3A", pat, emb, sp))

    if slug == "digimon_gabumon":
        # Digi-Egg of Friendship: Frost Ice Blue + Gabumon Indigo Wolf Stripes + Crest of Friendship (strictly inside egg!)
        pat = (
            '<path d="M 84,142 L 116,154 L 82,168 L 114,184 L 78,196 C 78,176 80,158 84,142 Z" fill="#4338CA"/>'
            '<path d="M 216,142 L 184,154 L 218,168 L 186,184 L 222,196 C 222,176 220,158 216,142 Z" fill="#4338CA"/>'
            '<path d="M 86,216 L 150,204 L 214,216 C 204,248 182,262 150,262 C 118,262 96,248 86,216 Z" '
            'fill="#0284C7" fill-opacity="0.82"/>'
        )
        emb = (
            '<polygon points="150,122 176,162 150,202 124,162" fill="#38BDF8" stroke="#0F172A" stroke-width="4.4" stroke-linejoin="round"/>'
            '<polygon points="150,138 164,162 150,186 136,162" fill="#E0F2FE" stroke="#0F172A" stroke-width="3.2" stroke-linejoin="round"/>'
            '<circle cx="150" cy="162" r="6" fill="#0284C7"/>'
        )
        sp = _sparkle4(80, 96, 12, "#7DD3FC", "#0369A1") + _sparkle4(222, 104, 12, "#E0F2FE", "#0F172A")
        return render_svg_to_png(_egg_base("#E0F2FE", "#7DD3FC", "#0F172A", pat, emb, sp))

    # digimon_piyomon — Digi-Egg of Love: Sakura Coral + Golden Feather Curve + Glowing Crest of Love Heart (strictly inside egg!)
    pat = (
        '<path d="M 80,204 Q 116,226 150,198 Q 184,226 220,204 '
        'C 214,242 188,262 150,262 C 112,262 86,242 80,204 Z" fill="#F97316"/>'
        '<path d="M 94,230 Q 124,244 150,224 Q 176,244 206,230 '
        'C 196,252 176,262 150,262 C 124,262 104,252 94,230 Z" fill="#FACC15"/>'
    )
    emb = (
        '<path d="M 150,190 C 118,166 114,134 134,128 C 144,125 150,136 150,142 '
        'C 150,136 156,125 166,128 C 186,134 182,166 150,190 Z" '
        'fill="#EF4444" stroke="#4A1525" stroke-width="4.5" stroke-linejoin="round"/>'
        '<circle cx="139" cy="144" r="4.5" fill="#FECDD3"/>'
    )
    sp = _sparkle4(82, 98, 12, "#FDE047", "#B45309") + _sparkle4(220, 96, 13, "#FDA4AF", "#9F1239")
    return render_svg_to_png(_egg_base("#FB7185", "#E11D48", "#4A1525", pat, emb, sp))


def draw_botamon() -> Image.Image:
    """Anime-accurate Botamon (Agumon Stage 1): fuzzy charcoal-black round baby blob with glowing yellow eyes!"""
    # Soft spiky fuzzy fur ring built smoothly around a round dome
    pts = []
    cx, cy = 150, 198
    n = 28
    for k in range(n):
        ang = math.radians(k * (360 / n))
        # Slightly flatter at bottom, fluffier on top/sides
        rx_base, ry_base = 82, 68
        if math.sin(ang) > 0.35:
            ry_base = 56
            spike = 1.03 if k % 2 == 0 else 0.99
        else:
            spike = 1.08 if k % 2 == 0 else 0.96
        x = cx + math.cos(ang) * rx_base * spike
        y = cy + math.sin(ang) * ry_base * spike
        pts.append((x, y))
    # Smooth closed quadratic spline around spikes
    d_parts = []
    for i in range(n):
        p0 = pts[i]
        p1 = pts[(i + 1) % n]
        mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        if i == 0:
            prev = pts[-1]
            d_parts.append(f"M {(prev[0] + p0[0]) / 2:.1f},{(prev[1] + p0[1]) / 2:.1f}")
        d_parts.append(f"Q {p0[0]:.1f},{p0[1]:.1f} {mx:.1f},{my:.1f}")
    d_parts.append("Z")
    fur_d = " ".join(d_parts)

    svg = "".join([
        '<ellipse cx="150" cy="260" rx="74" ry="12" fill="#1F1612" fill-opacity="0.14"/>',
        f'<path d="{fur_d}" fill="#26262C" stroke="#111114" stroke-width="5.5" stroke-linejoin="round"/>',
        # Soft charcoal fur highlight dome
        '<ellipse cx="136" cy="166" rx="44" ry="26" fill="#464652" fill-opacity="0.55"/>',
        # Iconic glowing yellow anime eyes!
        '<ellipse cx="118" cy="196" rx="16" ry="21" fill="#FACC15" stroke="#111114" stroke-width="4.2"/>',
        '<ellipse cx="118" cy="194" rx="10" ry="14" fill="#FEF08A"/>',
        '<circle cx="113" cy="187" r="4.2" fill="#FFFFFF"/>',
        '<ellipse cx="182" cy="196" rx="16" ry="21" fill="#FACC15" stroke="#111114" stroke-width="4.2"/>',
        '<ellipse cx="182" cy="194" rx="10" ry="14" fill="#FEF08A"/>',
        '<circle cx="177" cy="187" r="4.2" fill="#FFFFFF"/>',
        # Cute subtle cat smile & tiny rosy dots
        '<path d="M 138,224 Q 144,231 150,225 Q 156,231 162,224" fill="none" stroke="#9CA3AF" stroke-width="3.4" stroke-linecap="round"/>',
        '<ellipse cx="96" cy="216" rx="8" ry="4.5" fill="#FB7185" fill-opacity="0.4"/>',
        '<ellipse cx="204" cy="216" rx="8" ry="4.5" fill="#FB7185" fill-opacity="0.4"/>',
    ])
    return render_svg_to_png(svg)


def draw_koromon() -> Image.Image:
    """Anime-accurate Koromon (Agumon Stage 2): squishy pastel-pink round head, 2 long drooping ears, bright red anime eyes!"""
    ol = "#5C2A32"
    pink = "#FBC2CC"
    pink_shd = "#EE9EAE"
    svg = "".join([
        '<ellipse cx="150" cy="264" rx="68" ry="12" fill="#3D2024" fill-opacity="0.13"/>',
        # Left & right iconic long drooping soft Koromon ears!
        f'<path d="M 118,124 C 86,88 46,96 42,138 C 38,176 62,216 78,222 '
        f'C 92,226 94,196 86,166 C 82,148 96,136 114,142 Z" '
        f'fill="{pink}" stroke="{ol}" stroke-width="5.8" stroke-linejoin="round"/>',
        f'<path d="M 182,124 C 214,88 254,96 258,138 C 262,176 238,216 222,222 '
        f'C 208,226 206,196 214,166 C 218,148 204,136 186,142 Z" '
        f'fill="{pink}" stroke="{ol}" stroke-width="5.8" stroke-linejoin="round"/>',
        # Ear soft cel shadow
        f'<path d="M 52,144 C 48,176 66,210 78,215 C 86,214 82,188 76,162 Z" fill="{pink_shd}" fill-opacity="0.55"/>',
        f'<path d="M 248,144 C 252,176 234,210 222,215 C 214,214 218,188 224,162 Z" fill="{pink_shd}" fill-opacity="0.55"/>',
        # Squishy round Koromon body/head!
        f'<path d="M 74,194 C 72,134 106,104 150,104 C 194,104 228,134 226,194 '
        f'C 226,242 194,262 150,262 C 106,262 74,242 74,194 Z" '
        f'fill="{pink}" stroke="{ol}" stroke-width="6" stroke-linejoin="round"/>',
        # Lower cheek shadow & top gloss
        f'<path d="M 84,220 C 106,256 194,256 216,220 C 196,260 104,260 84,220 Z" fill="{pink_shd}" fill-opacity="0.72"/>',
        '<ellipse cx="128" cy="130" rx="22" ry="11" transform="rotate(-14 128 130)" fill="#FFFFFF" fill-opacity="0.45"/>',
        # Bright crimson-red Koromon anime eyes!
        f'<ellipse cx="116" cy="184" rx="16" ry="20" fill="#DC2626" stroke="{ol}" stroke-width="4.2"/>',
        '<ellipse cx="116" cy="186" rx="9" ry="12" fill="#991B1B"/>',
        '<circle cx="110" cy="176" r="5.5" fill="#FFFFFF"/>',
        '<circle cx="121" cy="193" r="2.6" fill="#FFFFFF"/>',
        f'<ellipse cx="184" cy="184" rx="16" ry="20" fill="#DC2626" stroke="{ol}" stroke-width="4.2"/>',
        '<ellipse cx="184" cy="186" rx="9" ry="12" fill="#991B1B"/>',
        '<circle cx="178" cy="176" r="5.5" fill="#FFFFFF"/>',
        '<circle cx="189" cy="193" r="2.6" fill="#FFFFFF"/>',
        # Rosy cheeks & cheeky wide Koromon smile!
        '<ellipse cx="92" cy="204" rx="10" ry="5.5" fill="#F472B6" fill-opacity="0.48"/>',
        '<ellipse cx="208" cy="204" rx="10" ry="5.5" fill="#F472B6" fill-opacity="0.48"/>',
        f'<path d="M 124,218 Q 150,242 176,218 Q 150,224 124,218 Z" fill="#E11D48" stroke="{ol}" stroke-width="3.6" stroke-linejoin="round"/>',
        '<path d="M 136,226 Q 150,236 164,226 Q 150,222 136,226 Z" fill="#FDA4AF"/>',
    ])
    return render_svg_to_png(svg)


# =========================================================================== #
#  PRECISION IMAGE EXTRACTION FROM OFFICIAL REFERENCE SHEETS
# =========================================================================== #
def _mask_boxes(rgb: np.ndarray, boxes: list[tuple[int, int, int, int]], fill_color=(255, 255, 255)) -> np.ndarray:
    out = rgb.copy()
    h, w = out.shape[:2]
    for x1, y1, x2, y2 in boxes:
        out[max(0, y1):min(h, y2), max(0, x1):min(w, x2)] = fill_color
    return out


def extract_on_white_bg(
    sheet_rgb: np.ndarray,
    crop: tuple[int, int, int, int],
    erase_boxes_abs: list[tuple[int, int, int, int]] | None = None,
    white_thr: int = 236,
    sat_thr: int = 24,
    keep_min_area_frac: float = 0.015,
    erode_halo: bool = True,
) -> Image.Image:
    """Extract a Digimon cleanly from a white-background sheet using border flood-fill,
    connected-component text/line removal, and smooth anti-aliased edge matting."""
    x0, y0, x1, y1 = crop
    sub = sheet_rgb[y0:y1, x0:x1].copy()
    if erase_boxes_abs:
        rel = [(a - x0, b - y0, c - x0, d - y0) for a, b, c, d in erase_boxes_abs]
        sub = _mask_boxes(sub, rel, (255, 255, 255))

    # Pad 4px white border so border flood-fill reaches ALL exterior background sides
    pad = 4
    sub = cv2.copyMakeBorder(sub, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    h, w = sub.shape[:2]

    # Candidate white/near-white background pixels (high brightness + low chroma)
    r, g, b = sub[:, :, 0].astype(np.int16), sub[:, :, 1].astype(np.int16), sub[:, :, 2].astype(np.int16)
    cmax = np.maximum(np.maximum(r, g), b)
    cmin = np.minimum(np.minimum(r, g), b)
    sat = cmax - cmin
    is_bg_cand = (cmin >= white_thr) & (sat <= sat_thr)

    # Flood-fill ONLY background connected to the outer image boundary (protects white eyes/fur inside!)
    num_cc, labels = cv2.connectedComponents(is_bg_cand.astype(np.uint8), connectivity=4)
    border_labels = set(labels[0, :].tolist()) | set(labels[-1, :].tolist()) | set(labels[:, 0].tolist()) | set(labels[:, -1].tolist())
    border_labels.discard(0)
    bg_mask = np.isin(labels, list(border_labels))

    # Also catch clean interior white cutouts (e.g., between legs/wings) that are very pure white & >= 20px
    # Wait: only do that if explicitly NOT inside white characters like YukimiBotamon/Gatomon/Salamon!
    fg_mask = (~bg_mask).astype(np.uint8)

    # Connected-component filter on foreground to eliminate any stray text letters or connector line fragments!
    n_fg, fg_labels, stats, _ = cv2.connectedComponentsWithStats(fg_mask, connectivity=8)
    if n_fg > 1:
        areas = stats[1:, cv2.CC_STAT_AREA]
        max_area = int(areas.max())
        min_keep = max(35, int(max_area * keep_min_area_frac))
        clean_fg = np.zeros_like(fg_mask)
        for cid in range(1, n_fg):
            if stats[cid, cv2.CC_STAT_AREA] >= min_keep:
                clean_fg[fg_labels == cid] = 1
        fg_mask = clean_fg

    # Anti-aliased soft alpha & gentle white-fringe removal on 1px outer boundary
    alpha = (fg_mask * 255).astype(np.uint8)
    if erode_halo:
        kernel = np.ones((3, 3), np.uint8)
        eroded = cv2.erode(fg_mask, kernel, iterations=1)
        boundary = (fg_mask == 1) & (eroded == 0)
        # Soften near-white JPEG halo pixels strictly on the 1px outer rim
        rim_bright = boundary & (cmin >= 200) & (sat <= 32)
        alpha[rim_bright] = np.clip((255 - cmin[rim_bright]) * 3.5, 0, 220).astype(np.uint8)
        # Gently un-premultiply white matte on remaining semi-transparent boundary pixels
        soft_b = (alpha > 0) & (alpha < 255)
        if np.any(soft_b):
            af = alpha[soft_b].astype(np.float32) / 255.0
            for ch in range(3):
                vals = sub[:, :, ch][soft_b].astype(np.float32)
                sub[:, :, ch][soft_b] = np.clip((vals - 255.0 * (1.0 - af)) / np.maximum(af, 0.25), 0, 255).astype(np.uint8)

    # Remove padding
    sub = sub[pad:-pad, pad:-pad]
    alpha = alpha[pad:-pad, pad:-pad]
    rgba = np.dstack([sub, alpha])
    return _trim_rgba(Image.fromarray(rgba, "RGBA"))


def extract_gabumon_blue_bg(
    sheet_rgb: np.ndarray,
    crop: tuple[int, int, int, int],
    erase_boxes_abs: list[tuple[int, int, int, int]] | None = None,
    clean_interior_blue: bool = True,
) -> Image.Image:
    """Extract Gabumon forms cleanly from the striped blue tech background!
    Uses exact RGB distance to the 3 background sky-blue tones (main cyan-blue + diagonal light-blue
    stripes + dark chevron arrows) so border flood-fill stops 100% cleanly at each Digimon's solid
    white sticker border and NEVER touches MetalGarurumon's purple-indigo armor, Garurumon's stripes,
    or Tsunomon's grey metallic horn!"""
    x0, y0, x1, y1 = crop
    sub = sheet_rgb[y0:y1, x0:x1].copy()
    bg_sample = (29, 155, 224)
    if erase_boxes_abs:
        rel = [(a - x0, b - y0, c - x0, d - y0) for a, b, c, d in erase_boxes_abs]
        sub = _mask_boxes(sub, rel, bg_sample)

    pad = 4
    sub = cv2.copyMakeBorder(sub, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=bg_sample)
    sub_f = sub.astype(np.float32)

    # Exact background palette on `gabumon.jpg`:
    #   main sky-cyan ~(29, 155, 218), light stripe ~(72, 182, 232), soft light ~(105, 196, 238),
    #   dark chevron arrow ~(15, 76, 125)
    bg_palette = np.array([
        [29, 155, 218],
        [48, 168, 225],
        [78, 184, 233],
        [108, 198, 238],
        [16, 78, 126],
        [22, 110, 165],
    ], dtype=np.float32)
    # Compute minimum RGB Euclidean distance from each pixel to the background palette
    dists = np.min(
        np.linalg.norm(sub_f[:, :, None, :] - bg_palette[None, None, :, :], axis=-1),
        axis=-1,
    )
    r, g, b = sub[:, :, 0].astype(np.int16), sub[:, :, 1].astype(np.int16), sub[:, :, 2].astype(np.int16)
    # Sky-cyan background ALWAYS has G > R + 45 and B > G + 25 (MetalGarurumon armor is purple-blue where G ≈ R!)
    is_sky_cyan = (dists <= 34.0) & ((g - r) >= 40) & ((b - g) >= 22)

    # 1. Flood-fill ONLY background connected to the outer crop border!
    _, labels = cv2.connectedComponents(is_sky_cyan.astype(np.uint8), connectivity=4)
    border_labels = (
        set(labels[0, :].tolist())
        | set(labels[-1, :].tolist())
        | set(labels[:, 0].tolist())
        | set(labels[:, -1].tolist())
    )
    border_labels.discard(0)
    bg_mask = np.isin(labels, list(border_labels))

    # 2. Clean enclosed sky-cyan pockets ONLY (e.g., inside Garurumon's tail loop & between legs)
    # Strict sky-cyan test (G - R >= 75 and dist <= 22): IMPOSSIBLE to match MetalGarurumon armor or Tsunomon horn!
    if clean_interior_blue:
        pure_pocket = (dists <= 22.0) & ((g - r) >= 75) & ((b - g) >= 35) & (~bg_mask)
        n_pb, pb_labels, pb_stats, _ = cv2.connectedComponentsWithStats(pure_pocket.astype(np.uint8), connectivity=4)
        for cid in range(1, n_pb):
            if pb_stats[cid, cv2.CC_STAT_AREA] >= 12:
                # Expand pocket by 1px to swallow its immediate cyan anti-aliasing fringe
                p_mask = (pb_labels == cid).astype(np.uint8)
                p_dil = cv2.dilate(p_mask, np.ones((3, 3), np.uint8), iterations=1).astype(bool)
                bg_mask |= (p_dil & ((g - r) >= 38) & ((b - r) >= 65))

    fg_mask = (~bg_mask).astype(np.uint8)

    # Keep only main Digimon connected component(s) (strips any stray dark arrow fragments!)
    n_fg, fg_labels, stats, _ = cv2.connectedComponentsWithStats(fg_mask, connectivity=8)
    if n_fg > 1:
        max_area = int(stats[1:, cv2.CC_STAT_AREA].max())
        clean_fg = np.zeros_like(fg_mask)
        for cid in range(1, n_fg):
            if stats[cid, cv2.CC_STAT_AREA] >= max(50, int(max_area * 0.05)):
                clean_fg[fg_labels == cid] = 1
        fg_mask = clean_fg

    # Gentle 1px cyan de-fringe strictly on outer boundary touching bg_mask
    kernel = np.ones((3, 3), np.uint8)
    eroded1 = cv2.erode(fg_mask, kernel, iterations=1)
    rim1 = (fg_mask == 1) & (eroded1 == 0)

    alpha = (fg_mask * 255).astype(np.uint8)
    cyan_rim = rim1 & ((g - r) >= 24) & ((b - r) >= 42)
    alpha[cyan_rim] = 0
    # Soften remaining 1px white sticker outer rim slightly for silky anti-aliasing
    still_rim = (alpha > 0) & rim1
    alpha[still_rim] = 225

    sub = sub[pad:-pad, pad:-pad]
    alpha = alpha[pad:-pad, pad:-pad]
    rgba = np.dstack([sub, alpha])
    return _trim_rgba(Image.fromarray(rgba, "RGBA"))


def _trim_rgba(im: Image.Image) -> Image.Image:
    bbox = im.getbbox()
    if bbox is None:
        return im
    return im.crop(bbox)


def compose_300(
    sprite: Image.Image,
    stage: int,
    mega_aura_rgb: tuple[int, int, int] | None = None,
    size: int = 300,
) -> Image.Image:
    """Place extracted sprite cleanly onto a 300x300 transparent canvas, bottom-aligned with
    proportional stage sizing (cute compact Baby -> heroic full-frame Mega) and optional Mega aura!"""
    sprite = _trim_rgba(sprite)
    sw, sh = sprite.size
    if sw == 0 or sh == 0:
        return Image.new("RGBA", (size, size), (0, 0, 0, 0))

    # Proportional visual hierarchy from cute tiny Baby to heroic full-frame Mega
    max_box_by_stage = {
        0: 215,
        1: 188,
        2: 204,
        3: 238,
        4: 274,
        5: 278,
        6: 282,
    }
    bottom_pad_by_stage = {
        0: 14,
        1: 26,
        2: 22,
        3: 16,
        4: 12,
        5: 10,
        6: 10,
    }
    max_dim = max_box_by_stage.get(stage, 250)
    bot_pad = bottom_pad_by_stage.get(stage, 14)

    scale = min(max_dim / sw, max_dim / sh)
    nw = max(1, int(round(sw * scale)))
    nh = max(1, int(round(sh * scale)))
    resized = sprite.resize((nw, nh), Image.LANCZOS)

    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = (size - nw) // 2
    py = size - bot_pad - nh
    py = max(8, py)

    # Tasteful Digivolution glow aura behind Stage 6 (Mega)!
    if stage == 6 and mega_aura_rgb is not None:
        aura = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ad = ImageDraw.Draw(aura)
        acx, acy = size // 2, py + nh // 2
        r_out = int(min(132, max(nw, nh) * 0.54))
        r_in = int(r_out * 0.62)
        ar, ag, ab = mega_aura_rgb
        ad.ellipse((acx - r_out, acy - r_out, acx + r_out, acy + r_out), fill=(ar, ag, ab, 95))
        ad.ellipse((acx - r_in, acy - r_in, acx + r_in, acy + r_in), fill=(255, 252, 232, 130))
        aura = aura.filter(ImageFilter.GaussianBlur(radius=22))
        canvas.alpha_composite(aura)
        # Subtle crisp Crest sparkles in upper corners (away from silhouette)
        sp_svg = _sparkle4(36, 40, 12, "#FEF08A", f"rgb({ar},{ag},{ab})", 2.2) + _sparkle4(264, 44, 11, "#FEF08A", f"rgb({ar},{ag},{ab})", 2.2)
        canvas.alpha_composite(render_svg_to_png(sp_svg, size=size))

    # Soft grounding shadow ellipse under every extracted Digimon (Stage 1..6)
    if stage >= 1:
        sh_im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh_im)
        srx = min(96, max(44, int(nw * 0.36)))
        sry = 9
        sy = size - bot_pad + 2
        sd.ellipse((size // 2 - srx, sy - sry, size // 2 + srx, sy + sry), fill=(35, 28, 30, 32))
        sh_im = sh_im.filter(ImageFilter.GaussianBlur(radius=3))
        canvas.alpha_composite(sh_im)

    canvas.alpha_composite(resized, (px, py))
    return canvas


# =========================================================================== #
#  EXTRACT ALL 5 DIGIMON LINES (35 SPRITES TOTAL)
# =========================================================================== #
DIGIMON_LINES = [
    {
        "slug": "digimon_veemon",
        "title": "36. Veemon — Crest of Miracles",
        "aura": (245, 184, 0),
        "names": ["Digi-Egg", "Chibomon", "DemiVeemon", "Veemon", "Flamedramon", "Paildramon", "Magnamon"],
    },
    {
        "slug": "digimon_agumon",
        "title": "37. Agumon — Crest of Courage",
        "aura": (249, 115, 22),
        "names": ["Digi-Egg", "Botamon", "Koromon", "Agumon", "Greymon", "MetalGreymon", "WarGreymon"],
    },
    {
        "slug": "digimon_gatomon",
        "title": "38. Gatomon — Crest of Light",
        "aura": (244, 114, 182),
        "names": ["Digi-Egg", "YukimiBotamon", "Nyaromon", "Salamon", "Gatomon", "Angewomon", "LovelyAngemon"],
    },
    {
        "slug": "digimon_gabumon",
        "title": "39. Gabumon — Crest of Friendship",
        "aura": (2, 132, 199),
        "names": ["Digi-Egg", "Punimon", "Tsunomon", "Gabumon", "Garurumon", "WereGarurumon", "MetalGarurumon"],
    },
    {
        "slug": "digimon_piyomon",
        "title": "40. Piyomon — Crest of Love",
        "aura": (251, 113, 133),
        "names": ["Digi-Egg", "Nyokimon", "Yokomon", "Biyomon", "Birdramon", "Garudamon", "Phoenixmon"],
    },
]


def extract_all() -> dict[str, list[Image.Image]]:
    veemon_rgb = np.array(Image.open(REF_DIR / "veemon.jpg").convert("RGB"))
    agumon_rgb = np.array(Image.open(REF_DIR / "agumon.jpg").convert("RGB"))
    gatomon_rgb = np.array(Image.open(REF_DIR / "gatomon.jpg").convert("RGB"))
    gabumon_rgb = np.array(Image.open(REF_DIR / "gabumon.jpg").convert("RGB"))
    piyomon_rgb = np.array(Image.open(REF_DIR / "piyomon.jpg").convert("RGB"))

    raw_sprites: dict[str, list[Image.Image]] = {}

    # 36. Veemon line (clean white bg)
    raw_sprites["digimon_veemon"] = [
        draw_digi_egg("digimon_veemon"),
        extract_on_white_bg(veemon_rgb, (6, 4, 108, 88)),
        extract_on_white_bg(veemon_rgb, (136, 4, 238, 116)),
        extract_on_white_bg(veemon_rgb, (238, 4, 372, 144)),
        extract_on_white_bg(veemon_rgb, (364, 2, 482, 191)),
        extract_on_white_bg(veemon_rgb, (128, 165, 252, 336)),
        extract_on_white_bg(veemon_rgb, (618, 4, 730, 175)),
    ]

    # 37. Agumon line (LEFT classic-anime column ONLY — ZERO "JJLCH" watermark!)
    raw_sprites["digimon_agumon"] = [
        draw_digi_egg("digimon_agumon"),
        draw_botamon(),
        draw_koromon(),
        extract_on_white_bg(agumon_rgb, (64, 4, 362, 212)),
        extract_on_white_bg(agumon_rgb, (64, 224, 362, 438)),
        extract_on_white_bg(agumon_rgb, (64, 450, 362, 662)),
        extract_on_white_bg(agumon_rgb, (64, 672, 362, 878)),
    ]

    # 38. Gatomon line (white bg — erase text boxes & connector stubs cleanly)
    raw_sprites["digimon_gatomon"] = [
        draw_digi_egg("digimon_gatomon"),
        extract_on_white_bg(gatomon_rgb, (2, 2, 250, 224), erase_boxes_abs=[(120, 0, 260, 32)]),
        extract_on_white_bg(gatomon_rgb, (0, 272, 264, 540), erase_boxes_abs=[(16, 466, 124, 504), (96, 270, 114, 310)]),
        extract_on_white_bg(gatomon_rgb, (268, 4, 518, 250), erase_boxes_abs=[(420, 0, 514, 32), (268, 204, 330, 250)]),
        extract_on_white_bg(gatomon_rgb, (264, 262, 540, 542), erase_boxes_abs=[(272, 502, 362, 536), (370, 260, 392, 334), (470, 260, 540, 326)]),
        extract_on_white_bg(gatomon_rgb, (544, 0, 764, 266), erase_boxes_abs=[(678, 0, 798, 28), (744, 204, 768, 266)]),
        extract_on_white_bg(gatomon_rgb, (750, 232, 1022, 542), erase_boxes_abs=[(694, 392, 840, 424), (750, 232, 796, 266)]),
    ]

    # 39. Gabumon line (blue striped tech bg + white sticker borders!)
    raw_sprites["digimon_gabumon"] = [
        draw_digi_egg("digimon_gabumon"),
        extract_gabumon_blue_bg(gabumon_rgb, (568, 46, 656, 124)),
        extract_gabumon_blue_bg(gabumon_rgb, (344, 10, 434, 134)),
        extract_gabumon_blue_bg(gabumon_rgb, (76, 8, 230, 152)),
        extract_gabumon_blue_bg(gabumon_rgb, (20, 198, 252, 344)),
        extract_gabumon_blue_bg(gabumon_rgb, (296, 158, 462, 388), erase_boxes_abs=[(296, 360, 405, 382)]),
        extract_gabumon_blue_bg(gabumon_rgb, (488, 164, 734, 346), erase_boxes_abs=[(540, 324, 654, 346)]),
    ]

    # 40. Piyomon line (white bg — erase text boxes & connector stubs cleanly)
    raw_sprites["digimon_piyomon"] = [
        draw_digi_egg("digimon_piyomon"),
        extract_on_white_bg(piyomon_rgb, (6, 2, 240, 264), erase_boxes_abs=[(100, 0, 194, 32)]),
        extract_on_white_bg(piyomon_rgb, (8, 266, 200, 500), erase_boxes_abs=[(154, 470, 234, 498), (174, 266, 200, 316)]),
        extract_on_white_bg(piyomon_rgb, (274, 2, 468, 262), erase_boxes_abs=[(408, 38, 482, 66), (274, 210, 294, 262)]),
        extract_on_white_bg(piyomon_rgb, (312, 262, 484, 498), erase_boxes_abs=[(438, 470, 526, 498), (392, 262, 406, 320)]),
        extract_on_white_bg(piyomon_rgb, (544, 2, 732, 254), erase_boxes_abs=[(694, 0, 784, 26), (712, 180, 732, 254)]),
        extract_on_white_bg(piyomon_rgb, (532, 264, 818, 496), erase_boxes_abs=[(746, 284, 848, 314)]),
    ]

    final_sprites: dict[str, list[Image.Image]] = {}
    for line in DIGIMON_LINES:
        slug = line["slug"]
        aura = line["aura"]
        out_dir = ASSETS_DIR / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        imgs = []
        for s, raw in enumerate(raw_sprites[slug]):
            if s == 0 or (slug == "digimon_agumon" and s in (1, 2)):
                # Already rendered cleanly on 300x300 canvas
                final = raw
            else:
                final = compose_300(raw, stage=s, mega_aura_rgb=aura, size=300)
            out_path = out_dir / f"stage_{s}.png"
            final.save(out_path, optimize=True)
            imgs.append(final)
        final_sprites[slug] = imgs
        print(f"  OK {slug}: 7 PNGs saved to assets/{slug}/", flush=True)

    return final_sprites


def _font(size: int, bold: bool = False):
    for nm in (("segoeuib.ttf" if bold else "segoeui.ttf"), "arial.ttf"):
        try:
            return ImageFont.truetype(nm, size)
        except OSError:
            continue
    return ImageFont.load_default()


def build_digimon_contact_sheet(all_imgs: dict[str, list[Image.Image]], out_path: Path):
    """Render `previews/assets_contact_sheet_digimon.png` showing ALL 5 lines x 7 stages
    at BOTH 180px large AND 44px actual Excel cell size with Digimon names underneath."""
    big = 180
    small = 44
    pad = 16
    row_h = 44 + big + 28 + 14
    W = pad + 7 * (big + 10) + 26 + 7 * (small + 5) + pad
    H = 72 + len(DIGIMON_LINES) * row_h + 16
    canvas = Image.new("RGB", (W, H), (249, 250, 253))
    d = ImageDraw.Draw(canvas)
    f_h = _font(22, True)
    f_l = _font(15, True)
    f_n = _font(12, True)
    f_s = _font(11, False)

    d.text((pad, 16), "DIGIMON 7-STAGE EVOLUTION COLLECTION (v3.7) — LARGE (180px) + ACTUAL EXCEL SIZE (44px)", fill=(24, 34, 54), font=f_h)
    sx0 = pad + 7 * (big + 10) + 22
    d.text((sx0, 26), "Actual 44px Excel Cell Preview (Stage 0 -> 6):", fill=(100, 112, 130), font=f_s)

    pct_labels = ["0%", "1-19%", "20-39%", "40-59%", "60-79%", "80-99%", "100%"]
    for idx, line in enumerate(DIGIMON_LINES):
        slug = line["slug"]
        y0 = 70 + idx * row_h
        d.line((pad, y0, W - pad, y0), fill=(224, 230, 240), width=2)
        d.text((pad, y0 + 10), line["title"], fill=(28, 42, 68), font=f_l)
        ims = all_imgs[slug]
        for s, im in enumerate(ims):
            x = pad + s * (big + 10)
            y = y0 + 36
            d.rounded_rectangle((x, y, x + big, y + big), radius=10, fill=(255, 255, 255), outline=(222, 228, 238), width=1)
            pic = im.resize((big - 10, big - 10), Image.LANCZOS)
            canvas.paste(pic, (x + 5, y + 5), pic)
            nm = line["names"][s]
            d.text((x + big // 2, y + big + 6), f"S{s}: {nm} ({pct_labels[s]})", fill=(60, 72, 92), font=f_n, anchor="mt")

            # 44px cell preview on right
            xs = sx0 + s * (small + 5)
            ys = y + (big - small) // 2
            d.rounded_rectangle((xs - 2, ys - 2, xs + small + 2, ys + small + 2), radius=5, fill=(255, 255, 255), outline=(214, 220, 230), width=1)
            sm = im.resize((small, small), Image.LANCZOS)
            canvas.paste(sm, (xs, ys), sm)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, optimize=True)
    print(f"  OK Contact sheet: {out_path.relative_to(ROOT)} ({out_path.stat().st_size:,} B)", flush=True)


def main():
    imgs = extract_all()
    build_digimon_contact_sheet(imgs, PREVIEWS_DIR / "assets_contact_sheet_digimon.png")


if __name__ == "__main__":
    main()
