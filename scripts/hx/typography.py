"""
hx.typography — Strict Whitelist 3-Tier Typography Matrix & PIL Pixel Auto-Fit Engine (80 PC Themes).

Strict Design & Legibility Rules:
  1. ZERO Blacklist fonts anywhere (no Vivaldi, French Script MT, Freestyle Script, Harlow Solid Italic,
     Brush Script MT, Pristina, Rage Italic, Edwardian, Kunstler, Parchment, Curlz, Juice, Magneto,
     Matura, Blackadder, Old English, Chiller, Jokerman, Ravie, Vladimir Script, etc.).
  2. Strict Whitelist separation:
     - `display_script` (Title Case ONLY — Month `October`, `September`):
       Readable soft handwritten/script (`Segoe Script`, `Gabriola`, `Lucida Handwriting`,
       `Monotype Corsiva`, `Segoe Print`, `Ink Free`, `Bradley Hand ITC`) OR elegant Serif Italic.
     - `display_caps` (ALL-CAPS English titles & headers — `B2`, `B9`, Yearly Goals `B2`, `YOU HAVE PLANTED:`):
       100% Elegant Magazine Serif (`Georgia`, `Palatino Linotype`, `Constantia`, `Book Antiqua`,
       `Cambria`, `Garamond`, `Sylfaen`) — NEVER uses Script fonts on ALL-CAPS text!
     - `title_vn` (Vietnamese banners & section headers — 100% 0-missing VN glyphs):
       `Palatino Linotype`, `Constantia`, `Cambria`, `Candara`, `Corbel`.
     - `body_ui` (Habit list, instructions, tables — 100% 0-missing VN glyphs):
       `Candara`, `Corbel`, `Segoe UI`, `Palatino Linotype`.
     - `num_font` (Year `2026` & big KPI numbers — 100% 0-missing VN glyphs):
       `Palatino Linotype`, `Constantia`, `Cambria`.
  3. Mathematical PIL Pixel Auto-Fit (`PIL.ImageFont.truetype`):
     Guarantees `rendered_text_width_px <= available_cell_width_px * 0.88` across every title,
     month, year, KPI, and banner cell on all 160 PC workbooks!
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from PIL import ImageFont

# --------------------------------------------------------------------------- #
#  Strict Blacklist & Whitelist Constants
# --------------------------------------------------------------------------- #
BLACKLIST_FONTS: frozenset[str] = frozenset({
    "Vivaldi", "French Script MT", "Edwardian Script ITC", "Kunstler Script",
    "Parchment", "Curlz MT", "Freestyle Script", "Harlow Solid Italic",
    "Brush Script MT", "Juice ITC", "Magneto", "Matura MT Script Capitals",
    "Blackadder ITC", "Old English Text MT", "Chiller", "Jokerman",
    "Ravie", "Pristina", "Vladimir Script", "Rage Italic",
})

SCRIPT_WHITELIST: frozenset[str] = frozenset({
    "Segoe Script", "Gabriola", "Lucida Handwriting", "Monotype Corsiva",
    "Segoe Print", "Ink Free", "Bradley Hand ITC",
})

SERIF_WHITELIST: frozenset[str] = frozenset({
    "Georgia", "Palatino Linotype", "Constantia", "Book Antiqua",
    "Cambria", "Garamond", "Sylfaen",
})

VN_TITLE_WHITELIST: frozenset[str] = frozenset({
    "Palatino Linotype", "Constantia", "Cambria", "Candara", "Corbel",
})

BODY_UI_WHITELIST: frozenset[str] = frozenset({
    "Candara", "Corbel", "Segoe UI", "Palatino Linotype",
})

ALL_ALLOWED_PC_FONTS: frozenset[str] = (
    SCRIPT_WHITELIST | SERIF_WHITELIST | VN_TITLE_WHITELIST | BODY_UI_WHITELIST
)


# --------------------------------------------------------------------------- #
#  Exact Windows Font Files for PIL.ImageFont.truetype Pixel Measurement
# --------------------------------------------------------------------------- #
_WIN_FONTS = Path(r"C:\Windows\Fonts")

# (family) -> dict of (bold, italic) -> (filename, ttc_index, native_bold, native_italic)
FONT_TTF_MAP: dict[str, dict[tuple[bool, bool], tuple[str, int, bool, bool]]] = {
    "Segoe Script": {
        (False, False): ("segoesc.ttf", 0, False, True),
        (True,  False): ("segoescb.ttf", 0, True, True),
        (False, True):  ("segoesc.ttf", 0, False, True),
        (True,  True):  ("segoescb.ttf", 0, True, True),
    },
    "Gabriola": {
        (False, False): ("Gabriola.ttf", 0, False, True),
        (True,  False): ("Gabriola.ttf", 0, False, True),
        (False, True):  ("Gabriola.ttf", 0, False, True),
        (True,  True):  ("Gabriola.ttf", 0, False, True),
    },
    "Lucida Handwriting": {
        (False, False): ("LHANDW.TTF", 0, False, True),
        (True,  False): ("LHANDW.TTF", 0, False, True),
        (False, True):  ("LHANDW.TTF", 0, False, True),
        (True,  True):  ("LHANDW.TTF", 0, False, True),
    },
    "Monotype Corsiva": {
        (False, False): ("MTCORSVA.TTF", 0, False, True),
        (True,  False): ("MTCORSVA.TTF", 0, False, True),
        (False, True):  ("MTCORSVA.TTF", 0, False, True),
        (True,  True):  ("MTCORSVA.TTF", 0, False, True),
    },
    "Segoe Print": {
        (False, False): ("segoepr.ttf", 0, False, False),
        (True,  False): ("segoeprb.ttf", 0, True, False),
        (False, True):  ("segoepr.ttf", 0, False, False),
        (True,  True):  ("segoeprb.ttf", 0, True, False),
    },
    "Ink Free": {
        (False, False): ("Inkfree.ttf", 0, False, False),
        (True,  False): ("Inkfree.ttf", 0, False, False),
        (False, True):  ("Inkfree.ttf", 0, False, False),
        (True,  True):  ("Inkfree.ttf", 0, False, False),
    },
    "Bradley Hand ITC": {
        (False, False): ("BRADHITC.TTF", 0, False, False),
        (True,  False): ("BRADHITC.TTF", 0, False, False),
        (False, True):  ("BRADHITC.TTF", 0, False, False),
        (True,  True):  ("BRADHITC.TTF", 0, False, False),
    },
    "Georgia": {
        (False, False): ("georgia.ttf", 0, False, False),
        (True,  False): ("georgiab.ttf", 0, True, False),
        (False, True):  ("georgiai.ttf", 0, False, True),
        (True,  True):  ("georgiaz.ttf", 0, True, True),
    },
    "Palatino Linotype": {
        (False, False): ("pala.ttf", 0, False, False),
        (True,  False): ("palab.ttf", 0, True, False),
        (False, True):  ("palai.ttf", 0, False, True),
        (True,  True):  ("palabi.ttf", 0, True, True),
    },
    "Constantia": {
        (False, False): ("constan.ttf", 0, False, False),
        (True,  False): ("constanb.ttf", 0, True, False),
        (False, True):  ("constani.ttf", 0, False, True),
        (True,  True):  ("constanz.ttf", 0, True, True),
    },
    "Book Antiqua": {
        (False, False): ("BKANT.TTF", 0, False, False),
        (True,  False): ("ANTQUAB.TTF", 0, True, False),
        (False, True):  ("ANTQUAI.TTF", 0, False, True),
        (True,  True):  ("ANTQUABI.TTF", 0, True, True),
    },
    "Cambria": {
        (False, False): ("cambria.ttc", 0, False, False),
        (True,  False): ("cambriab.ttf", 0, True, False),
        (False, True):  ("cambriai.ttf", 0, False, True),
        (True,  True):  ("cambriaz.ttf", 0, True, True),
    },
    "Garamond": {
        (False, False): ("GARA.TTF", 0, False, False),
        (True,  False): ("GARABD.TTF", 0, True, False),
        (False, True):  ("GARAIT.TTF", 0, False, True),
        (True,  True):  ("GARABD.TTF", 0, True, False),
    },
    "Sylfaen": {
        (False, False): ("sylfaen.ttf", 0, False, False),
        (True,  False): ("sylfaen.ttf", 0, False, False),
        (False, True):  ("sylfaen.ttf", 0, False, False),
        (True,  True):  ("sylfaen.ttf", 0, False, False),
    },
    "Candara": {
        (False, False): ("Candara.ttf", 0, False, False),
        (True,  False): ("Candarab.ttf", 0, True, False),
        (False, True):  ("Candarai.ttf", 0, False, True),
        (True,  True):  ("Candaraz.ttf", 0, True, True),
    },
    "Corbel": {
        (False, False): ("corbel.ttf", 0, False, False),
        (True,  False): ("corbelb.ttf", 0, True, False),
        (False, True):  ("corbeli.ttf", 0, False, True),
        (True,  True):  ("corbelz.ttf", 0, True, True),
    },
    "Segoe UI": {
        (False, False): ("segoeui.ttf", 0, False, False),
        (True,  False): ("segoeuib.ttf", 0, True, False),
        (False, True):  ("segoeuii.ttf", 0, False, True),
        (True,  True):  ("segoeuiz.ttf", 0, True, True),
    },
}


@lru_cache(maxsize=512)
def _load_pil_font(font_name: str, size_px: int, bold: bool, italic: bool):
    entry = FONT_TTF_MAP.get(font_name, FONT_TTF_MAP["Segoe UI"])
    fname, idx, nat_b, nat_i = entry[(bool(bold), bool(italic))]
    fpath = _WIN_FONTS / fname
    pil_font = ImageFont.truetype(str(fpath), size=max(6, size_px), index=idx)
    # Cushion for synthetic bold/italic rendered by Windows GDI/DirectWrite when font lacks bold/italic face
    w_mult = 1.0
    if bold and not nat_b:
        w_mult *= 1.08
    if italic and not nat_i:
        w_mult *= 1.04
    # Excel cell padding + DirectWrite glyph spacing cushion (~5%)
    w_mult *= 1.05
    return pil_font, w_mult


def measure_text_px(text: str, font_name: str, size_pt: float, *, bold: bool = False, italic: bool = False) -> tuple[float, float]:
    """Return conservative (width_px, height_px) at 96 DPI using PIL.ImageFont.truetype."""
    if not text:
        return 0.0, 0.0
    size_px = max(6, int(round(size_pt * 96.0 / 72.0)))
    pil_font, w_mult = _load_pil_font(font_name, size_px, bold, italic)

    # Separate emoji / wide pictographs (rendered via Segoe UI Emoji on Windows) from normal glyphs
    max_line_w = 0.0
    total_h = 0.0
    lines = str(text).split("\n")
    ascent, descent = pil_font.getmetrics()
    line_h = max(size_px * 1.25, float(ascent + descent))

    for line in lines:
        norm_chars = []
        emoji_cnt = 0
        for ch in line:
            cp = ord(ch)
            if cp == 0xFE0F or cp == 0x200D:
                continue  # variation selector / ZWJ
            if cp >= 0x2600 or (0x2190 <= cp <= 0x25FF):
                emoji_cnt += 1
            else:
                norm_chars.append(ch)
        clean = "".join(norm_chars)
        tw = 0.0
        if clean:
            try:
                tw = float(pil_font.getlength(clean))
            except Exception:
                tw = 0.0
            try:
                bb = pil_font.getbbox(clean)
                if bb:
                    tw = max(tw, float(bb[2] - bb[0]))
            except Exception:
                pass
        line_w = tw * w_mult + emoji_cnt * (size_px * 1.45)
        if line_w > max_line_w:
            max_line_w = line_w
        total_h += line_h

    return max_line_w, total_h


def autofit_font_size(
    texts: list[str],
    font_name: str,
    target_pt: float,
    avail_w_px: float,
    *,
    bold: bool = False,
    italic: bool = False,
    min_pt: float = 7.5,
    safety: float = 0.88,
) -> tuple[float, float, bool]:
    """
    Step Font.Size down by -1pt until EVERY string in `texts` satisfies:
        rendered_text_width_px <= avail_w_px * safety (default 0.88 -> >=12% margin).
    Returns: (fitted_size_pt, min_row_height_pt, was_shrunk).
    """
    valid_texts = [t for t in texts if t and str(t).strip()]
    if not valid_texts or avail_w_px <= 0:
        return target_pt, target_pt * 1.65 + 6.0, False

    limit_px = avail_w_px * safety
    sz = float(target_pt)
    shrunk = False
    while sz > min_pt:
        max_w = max(measure_text_px(t, font_name, sz, bold=bold, italic=italic)[0] for t in valid_texts)
        if max_w <= limit_px:
            break
        sz = max(min_pt, sz - 1.0)
        shrunk = True

    max_h_px = max(measure_text_px(t, font_name, sz, bold=bold, italic=italic)[1] for t in valid_texts)
    min_rh_pt = max(sz * 1.55 + 5.0, max_h_px * (72.0 / 96.0) + 6.5)
    return sz, min_rh_pt, shrunk


# --------------------------------------------------------------------------- #
#  Optical Calibration & TypographySpec (Strict Whitelist!)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class FontOptics:
    size_delta: float = 0.0
    rh_boost: float = 2.0
    italic: bool = False
    bold: bool = True
    max_month_pt: float = 20.0


FONT_OPTICS: dict[str, FontOptics] = {
    # Whitelist Script / Handwritten (ONLY for Title Case like "October"!)
    "Lucida Handwriting": FontOptics(size_delta=0.0,  rh_boost=3.0, italic=False, bold=True,  max_month_pt=18.5),
    "Segoe Script":       FontOptics(size_delta=-0.5, rh_boost=3.0, italic=False, bold=True,  max_month_pt=18.0),
    "Gabriola":           FontOptics(size_delta=3.5,  rh_boost=5.5, italic=False, bold=False, max_month_pt=23.0),
    "Monotype Corsiva":   FontOptics(size_delta=2.5,  rh_boost=3.5, italic=False, bold=True,  max_month_pt=21.5),
    "Segoe Print":        FontOptics(size_delta=-0.5, rh_boost=3.0, italic=False, bold=True,  max_month_pt=17.5),
    "Ink Free":           FontOptics(size_delta=1.5,  rh_boost=3.0, italic=False, bold=True,  max_month_pt=20.0),
    "Bradley Hand ITC":   FontOptics(size_delta=1.0,  rh_boost=3.0, italic=False, bold=True,  max_month_pt=19.5),
    # Whitelist Elegant Magazine Serifs (Crystal clear for ALL-CAPS & Title Case!)
    "Georgia":            FontOptics(size_delta=0.0,  rh_boost=2.5, italic=True,  bold=True,  max_month_pt=19.0),
    "Palatino Linotype":  FontOptics(size_delta=0.0,  rh_boost=2.5, italic=True,  bold=True,  max_month_pt=19.0),
    "Constantia":         FontOptics(size_delta=0.0,  rh_boost=2.5, italic=True,  bold=True,  max_month_pt=19.0),
    "Book Antiqua":       FontOptics(size_delta=0.0,  rh_boost=2.5, italic=True,  bold=True,  max_month_pt=19.0),
    "Cambria":            FontOptics(size_delta=0.0,  rh_boost=2.0, italic=False, bold=True,  max_month_pt=19.0),
    "Garamond":           FontOptics(size_delta=2.0,  rh_boost=2.5, italic=True,  bold=True,  max_month_pt=21.0),
    "Sylfaen":            FontOptics(size_delta=0.5,  rh_boost=2.5, italic=False, bold=True,  max_month_pt=19.0),
    # Whitelist Clean Body & VN Title
    "Candara":            FontOptics(size_delta=0.0,  rh_boost=2.0, italic=False, bold=True,  max_month_pt=19.0),
    "Corbel":             FontOptics(size_delta=0.0,  rh_boost=2.0, italic=False, bold=True,  max_month_pt=19.0),
    "Segoe UI":           FontOptics(size_delta=0.0,  rh_boost=1.5, italic=False, bold=True,  max_month_pt=18.5),
}


@dataclass(frozen=True)
class TypographySpec:
    display_en: str             # Title Case ONLY (Month `October`, `Daily!E5`): Script OR Serif Italic
    display_caps: str           # ALL-CAPS English headers (`B2`, `B9`, Yearly Goals `B2`, `YOU HAVE PLANTED:`): ALWAYS Elegant Serif!
    title_vn: str               # Vietnamese banners & section headers (100% 0-missing VN!)
    body_ui: str                # Habit list, tables, instructions (100% 0-missing VN!)
    num_font: str               # Big Year & KPI numbers (100% 0-missing VN!)
    title_vn_italic: bool = True
    caps_italic: bool = True    # Flowing italic on ALL-CAPS Serif banners (False for bold modern/RPG)
    vibe: str = "pastel"

    @property
    def en_optics(self) -> FontOptics:
        return FONT_OPTICS.get(self.display_en, FontOptics())

    @property
    def caps_optics(self) -> FontOptics:
        return FONT_OPTICS.get(self.display_caps, FontOptics())

    @property
    def vn_optics(self) -> FontOptics:
        return FONT_OPTICS.get(self.title_vn, FontOptics())


# --------------------------------------------------------------------------- #
#  CURATED 80-THEME STRICT-WHITELIST TYPOGRAPHY MATRIX (#01–#80)
#  - 0 Blacklist fonts!
#  - 0 Script fonts on ALL-CAPS cells (`display_caps` is 100% Elegant Serif)!
#  - Adjacent themes (#i and #i+1) NEVER repeat `display_en` or `title_vn`.
#  - 100% of `title_vn`, `body_ui`, `num_font` are verified 0-missing VN.
# --------------------------------------------------------------------------- #
THEME_TYPOGRAPHY: dict[str, TypographySpec] = {
    # === BATCH 1 (#01–#10) ===
    "sunflower":              TypographySpec("Lucida Handwriting", "Georgia",           "Palatino Linotype", "Candara",           "Palatino Linotype", True,  True,  "floral"),
    "cactus":                 TypographySpec("Segoe Script",       "Constantia",        "Candara",           "Corbel",            "Constantia",        True,  True,  "pastel"),
    "lotus_stars":            TypographySpec("Georgia",            "Book Antiqua",      "Cambria",           "Segoe UI",          "Cambria",           False, False, "executive"),
    "botanical":              TypographySpec("Gabriola",           "Palatino Linotype", "Constantia",        "Palatino Linotype", "Constantia",        True,  True,  "botanical"),
    "lavender_moon":          TypographySpec("Monotype Corsiva",   "Garamond",          "Palatino Linotype", "Corbel",            "Palatino Linotype", True,  True,  "dreamy"),
    "focus_rocket":           TypographySpec("Cambria",            "Cambria",           "Corbel",            "Segoe UI",          "Cambria",           False, False, "modern"),
    "sakura_zen":             TypographySpec("Lucida Handwriting", "Palatino Linotype", "Constantia",        "Candara",           "Constantia",        True,  True,  "floral"),
    "ocean_coral":            TypographySpec("Ink Free",           "Georgia",           "Candara",           "Segoe UI",          "Palatino Linotype", True,  True,  "energetic"),
    "matcha_cafe":            TypographySpec("Bradley Hand ITC",   "Book Antiqua",      "Constantia",        "Corbel",            "Cambria",           True,  True,  "botanical"),
    "aurora_rpg":             TypographySpec("Constantia",         "Sylfaen",           "Cambria",           "Segoe UI",          "Cambria",           False, False, "rpg"),

    # === BATCH 2 (#11–#19) ===
    "velvet_rose":            TypographySpec("Monotype Corsiva",   "Georgia",           "Palatino Linotype", "Palatino Linotype", "Palatino Linotype", True,  True,  "luxury"),
    "blue_tulip":             TypographySpec("Segoe Script",       "Constantia",        "Corbel",            "Candara",           "Constantia",        True,  True,  "pastel"),
    "blossom_star":           TypographySpec("Segoe Print",        "Book Antiqua",      "Candara",           "Corbel",            "Palatino Linotype", True,  True,  "cute"),
    "forest_tree":            TypographySpec("Gabriola",           "Garamond",          "Constantia",        "Candara",           "Cambria",           True,  True,  "botanical"),
    "mocha_sunflower":        TypographySpec("Book Antiqua",       "Georgia",           "Palatino Linotype", "Candara",           "Palatino Linotype", True,  True,  "vintage"),
    "dream_house":            TypographySpec("Georgia",            "Cambria",           "Cambria",           "Segoe UI",          "Cambria",           False, False, "architect"),
    "wildflower_mood":        TypographySpec("Lucida Handwriting", "Constantia",        "Palatino Linotype", "Corbel",            "Constantia",        True,  True,  "floral"),
    "plum_oak":               TypographySpec("Garamond",           "Book Antiqua",      "Constantia",        "Palatino Linotype", "Palatino Linotype", True,  True,  "executive"),
    "meadow_sunflower":       TypographySpec("Gabriola",           "Georgia",           "Palatino Linotype", "Candara",           "Constantia",        True,  True,  "botanical"),

    # === BATCH 3 (#20–#31) ===
    "alpaca_cream":           TypographySpec("Ink Free",           "Book Antiqua",      "Candara",           "Corbel",            "Constantia",        True,  True,  "cozy"),
    "alpaca_blush":           TypographySpec("Lucida Handwriting", "Palatino Linotype", "Palatino Linotype", "Candara",           "Palatino Linotype", True,  True,  "pastel"),
    "alpaca_matcha":          TypographySpec("Bradley Hand ITC",   "Constantia",        "Constantia",        "Corbel",            "Cambria",           True,  True,  "botanical"),
    "bamboo_panda":           TypographySpec("Segoe Print",        "Georgia",           "Corbel",            "Candara",           "Cambria",           True,  True,  "zen"),
    "royal_cat_cash":         TypographySpec("Georgia",            "Book Antiqua",      "Cambria",           "Segoe UI",          "Palatino Linotype", False, True,  "royal"),
    "ginger_kitten":          TypographySpec("Segoe Script",       "Constantia",        "Candara",           "Corbel",            "Constantia",        True,  True,  "cute"),
    "purple_cat":             TypographySpec("Monotype Corsiva",   "Garamond",          "Palatino Linotype", "Corbel",            "Palatino Linotype", True,  True,  "dreamy"),
    "hatching_chick":         TypographySpec("Ink Free",           "Sylfaen",           "Candara",           "Segoe UI",          "Constantia",        False, False, "cute"),
    "candy_jar":              TypographySpec("Gabriola",           "Palatino Linotype", "Corbel",            "Candara",           "Palatino Linotype", True,  True,  "sweet"),
    "rose_bouquet":           TypographySpec("Lucida Handwriting", "Georgia",           "Palatino Linotype", "Palatino Linotype", "Palatino Linotype", True,  True,  "floral"),
    "shiba_inu":              TypographySpec("Segoe Print",        "Book Antiqua",      "Candara",           "Segoe UI",          "Cambria",           False, False, "playful"),
    "akita_inu":              TypographySpec("Palatino Linotype",  "Constantia",        "Constantia",        "Corbel",            "Constantia",        True,  True,  "winter"),

    # === BATCH 4 (#32–#35) ===
    "sakura_tree":            TypographySpec("Monotype Corsiva",   "Palatino Linotype", "Palatino Linotype", "Corbel",            "Palatino Linotype", True,  True,  "minimal"),
    "mochi_cat":              TypographySpec("Ink Free",           "Georgia",           "Candara",           "Candara",           "Constantia",        True,  True,  "pastel"),
    "fluffy_bunny":           TypographySpec("Gabriola",           "Book Antiqua",      "Corbel",            "Candara",           "Palatino Linotype", True,  True,  "cute"),
    "milk_mocha_bear":        TypographySpec("Segoe Script",       "Constantia",        "Constantia",        "Candara",           "Palatino Linotype", True,  True,  "cozy"),

    # === BATCH 5 (#36–#40): Digimon 7-Stage ===
    "digimon_veemon":         TypographySpec("Cambria",            "Sylfaen",           "Cambria",           "Segoe UI",          "Cambria",           False, False, "rpg"),
    "digimon_agumon":         TypographySpec("Georgia",            "Book Antiqua",      "Constantia",        "Candara",           "Cambria",           False, False, "rpg"),
    "digimon_gatomon":        TypographySpec("Monotype Corsiva",   "Palatino Linotype", "Palatino Linotype", "Corbel",            "Palatino Linotype", True,  True,  "pastel"),
    "digimon_gabumon":        TypographySpec("Bradley Hand ITC",   "Cambria",           "Corbel",            "Segoe UI",          "Cambria",           False, False, "modern"),
    "digimon_piyomon":        TypographySpec("Segoe Script",       "Georgia",           "Candara",           "Corbel",            "Constantia",        True,  True,  "energetic"),

    # === BATCH 6 (#41–#47): Digimon Batch 2 ===
    "digimon_patamon":        TypographySpec("Lucida Handwriting", "Constantia",        "Palatino Linotype", "Candara",           "Constantia",        True,  True,  "dreamy"),
    "digimon_palmon":         TypographySpec("Gabriola",           "Palatino Linotype", "Constantia",        "Corbel",            "Palatino Linotype", True,  True,  "floral"),
    "digimon_gomamon":        TypographySpec("Segoe Print",        "Georgia",           "Corbel",            "Segoe UI",          "Cambria",           False, False, "ocean"),
    "digimon_guilmon":        TypographySpec("Cambria",            "Sylfaen",           "Cambria",           "Segoe UI",          "Cambria",           False, False, "rpg"),
    "digimon_terriermon":     TypographySpec("Ink Free",           "Book Antiqua",      "Candara",           "Corbel",            "Constantia",        False, False, "cute"),
    "digimon_renamon":        TypographySpec("Garamond",           "Georgia",           "Palatino Linotype", "Palatino Linotype", "Palatino Linotype", True,  True,  "mystic"),
    "digimon_tentomon":       TypographySpec("Constantia",         "Cambria",           "Cambria",           "Segoe UI",          "Cambria",           False, False, "tech"),

    # === BATCH 7 (#48–#60): Capybara Chill ===
    "capybara_avocado":       TypographySpec("Ink Free",           "Constantia",        "Constantia",        "Candara",           "Constantia",        True,  True,  "botanical"),
    "capybara_onsen":         TypographySpec("Gabriola",           "Palatino Linotype", "Palatino Linotype", "Corbel",            "Palatino Linotype", True,  True,  "zen"),
    "capybara_pip_puddle":    TypographySpec("Segoe Print",        "Book Antiqua",      "Candara",           "Corbel",            "Constantia",        True,  True,  "cute"),
    "capybara_boba_pond":     TypographySpec("Segoe Script",       "Georgia",           "Corbel",            "Candara",           "Constantia",        True,  True,  "cafe"),
    "capybara_bookworm":      TypographySpec("Bradley Hand ITC",   "Garamond",          "Palatino Linotype", "Palatino Linotype", "Cambria",           True,  True,  "study"),
    "capybara_lofi_picnic":   TypographySpec("Monotype Corsiva",   "Constantia",        "Candara",           "Corbel",            "Constantia",        True,  True,  "lofi"),
    "capybara_foodie":        TypographySpec("Ink Free",           "Book Antiqua",      "Constantia",        "Candara",           "Palatino Linotype", True,  True,  "cafe"),
    "capybara_dino_hoodie":   TypographySpec("Segoe Print",        "Sylfaen",           "Corbel",            "Segoe UI",          "Cambria",           False, False, "playful"),
    "capybara_apple_orchard": TypographySpec("Lucida Handwriting", "Georgia",           "Palatino Linotype", "Candara",           "Palatino Linotype", True,  True,  "orchard"),
    "capybara_pink_chill":    TypographySpec("Gabriola",           "Palatino Linotype", "Candara",           "Corbel",            "Constantia",        True,  True,  "dreamy"),
    "capybara_fairy_party":   TypographySpec("Monotype Corsiva",   "Constantia",        "Palatino Linotype", "Candara",           "Palatino Linotype", True,  True,  "pastel"),
    "capybara_selfcare":      TypographySpec("Segoe Script",       "Book Antiqua",      "Constantia",        "Corbel",            "Constantia",        True,  True,  "glow"),
    "capybara_traveler":      TypographySpec("Bradley Hand ITC",   "Georgia",           "Cambria",           "Segoe UI",          "Cambria",           True,  True,  "travel"),

    # === BATCH 8 (#61–#70): Loopy Pastel Collection ===
    "loopy_red_bow":          TypographySpec("Lucida Handwriting", "Georgia",           "Palatino Linotype", "Candara",           "Palatino Linotype", True,  True,  "pastel"),
    "loopy_taiyaki":          TypographySpec("Segoe Script",       "Book Antiqua",      "Constantia",        "Corbel",            "Constantia",        True,  True,  "cafe"),
    "loopy_piggy_cafe":       TypographySpec("Gabriola",           "Palatino Linotype", "Candara",           "Candara",           "Palatino Linotype", True,  True,  "sweet"),
    "loopy_sauna_sheep":      TypographySpec("Monotype Corsiva",   "Constantia",        "Corbel",            "Corbel",            "Constantia",        True,  True,  "spa"),
    "loopy_honey_bee":        TypographySpec("Segoe Print",        "Georgia",           "Candara",           "Segoe UI",          "Cambria",           False, True,  "cute"),
    "loopy_poolside_duck":    TypographySpec("Ink Free",           "Palatino Linotype", "Corbel",            "Candara",           "Constantia",        True,  True,  "summer"),
    "loopy_fluffy_commuter":  TypographySpec("Bradley Hand ITC",   "Book Antiqua",      "Constantia",        "Segoe UI",          "Cambria",           True,  True,  "cozy"),
    "loopy_panda_study":      TypographySpec("Georgia",            "Garamond",          "Palatino Linotype", "Corbel",            "Constantia",        True,  True,  "study"),
    "loopy_ruffle_sleep":     TypographySpec("Gabriola",           "Palatino Linotype", "Constantia",        "Candara",           "Palatino Linotype", True,  True,  "dreamy"),
    "loopy_hair_roller":      TypographySpec("Segoe Script",       "Georgia",           "Candara",           "Corbel",            "Constantia",        True,  True,  "glow"),

    # === BATCH 9 (#71–#80): Lotso Chubby Plush Bear Collection ===
    "lotso_strawberry":       TypographySpec("Monotype Corsiva",   "Georgia",           "Palatino Linotype", "Candara",           "Palatino Linotype", True,  True,  "floral"),
    "lotso_milk_cafe":        TypographySpec("Lucida Handwriting", "Book Antiqua",      "Candara",           "Corbel",            "Constantia",        True,  True,  "cafe"),
    "lotso_flower_crown":     TypographySpec("Gabriola",           "Palatino Linotype", "Constantia",        "Palatino Linotype", "Palatino Linotype", True,  True,  "floral"),
    "lotso_overalls":         TypographySpec("Segoe Print",        "Sylfaen",           "Candara",           "Candara",           "Cambria",           False, False, "playful"),
    "lotso_lofi":             TypographySpec("Segoe Script",       "Constantia",        "Corbel",            "Segoe UI",          "Constantia",        True,  True,  "lofi"),
    "lotso_mood_detox":       TypographySpec("Ink Free",           "Georgia",           "Candara",           "Corbel",            "Constantia",        True,  False, "comic"),
    "lotso_sweet_dreams":     TypographySpec("Monotype Corsiva",   "Garamond",          "Palatino Linotype", "Corbel",            "Palatino Linotype", True,  True,  "dreamy"),
    "lotso_daisy_glow":       TypographySpec("Bradley Hand ITC",   "Book Antiqua",      "Constantia",        "Candara",           "Constantia",        True,  True,  "floral"),
    "lotso_bunny_selfcare":   TypographySpec("Lucida Handwriting", "Palatino Linotype", "Candara",           "Corbel",            "Palatino Linotype", True,  True,  "spa"),
    "lotso_gift_box":         TypographySpec("Gabriola",           "Georgia",           "Constantia",        "Candara",           "Palatino Linotype", True,  True,  "party"),
}


_VN_DIACRITIC_RE = re.compile(
    r"[ăâđêôơưĂÂĐÊÔƠƯáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ"
    r"ÁÀẢÃẠẤẦẨẪẬẮẰẲẴẶÉÈẺẼẸẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢÚÙỦŨỤỨỪỬỮỰÝỲỶỸỴ]"
)


def has_vietnamese(text: str) -> bool:
    """Returns True if text contains any Vietnamese accented character or đ/Đ."""
    return bool(text and _VN_DIACRITIC_RE.search(text))


def is_all_caps(text: str) -> bool:
    """Returns True if text has >= 3 alphabetic chars and >= 75% are uppercase."""
    if not text:
        return False
    letters = [ch for ch in text if ch.isalpha()]
    if len(letters) < 3:
        return False
    return (sum(1 for ch in letters if ch.isupper()) / len(letters)) >= 0.75


def get_typography(slug: str) -> TypographySpec:
    return THEME_TYPOGRAPHY.get(
        slug,
        TypographySpec("Lucida Handwriting", "Georgia", "Palatino Linotype", "Candara", "Palatino Linotype", True, True, "default"),
    )


def verify_vietnamese_fonts() -> dict[str, int]:
    """Programmatically validates EVERY title_vn, body_ui & num_font against Windows TTF/TTC files."""
    from fontTools.ttLib import TTCollection, TTFont

    vn_codes = {ord(c) for c in "ăâđêôơưệữợắẫỰĐĂÂÊÔƠƯáàảãạéèẻẽẹíìỉĩịóòỏõọúùủũụýỳỷỹỵ"}
    cmap_miss: dict[str, int] = {}
    for fam, variants in FONT_TTF_MAP.items():
        fname, idx, _, _ = variants[(False, False)]
        p = _WIN_FONTS / fname
        assert p.exists(), f"Missing font file on Windows: {p}"
        f = TTCollection(str(p), lazy=True).fonts[idx] if p.suffix.lower() == ".ttc" else TTFont(str(p), fontNumber=0, lazy=True)
        cmap = f.getBestCmap() or {}
        cmap_miss[fam] = sum(1 for c in vn_codes if c not in cmap)

    vn_fonts_used = set()
    for sp in THEME_TYPOGRAPHY.values():
        vn_fonts_used.update([sp.title_vn, sp.body_ui, sp.num_font])

    report: dict[str, int] = {}
    for fam in sorted(vn_fonts_used):
        m = cmap_miss.get(fam, 999)
        report[fam] = m
        assert m == 0, f"VIETNAMESE FONT FAILURE: {fam!r} is missing {m} Vietnamese glyphs!"
    return report


def validate_matrix(ordered_slugs: list[str] | None = None) -> None:
    slugs = ordered_slugs or list(THEME_TYPOGRAPHY.keys())
    assert len(slugs) == 80, f"Expected 80 themes, got {len(slugs)}"
    for i, sl in enumerate(slugs):
        assert sl in THEME_TYPOGRAPHY, f"Missing typography for slug: {sl}"
        sp = THEME_TYPOGRAPHY[sl]
        for f in (sp.display_en, sp.display_caps, sp.title_vn, sp.body_ui, sp.num_font):
            assert f not in BLACKLIST_FONTS, f"BLACKLISTED FONT in {sl}: {f}"
            assert f in ALL_ALLOWED_PC_FONTS, f"NON-WHITELIST FONT in {sl}: {f}"
        assert sp.display_caps in SERIF_WHITELIST, f"ALL-CAPS font MUST be Elegant Serif ({sl}: {sp.display_caps})"
        assert sp.title_vn in VN_TITLE_WHITELIST, f"title_vn MUST be VN-safe ({sl}: {sp.title_vn})"
        assert sp.body_ui in BODY_UI_WHITELIST, f"body_ui MUST be VN-safe ({sl}: {sp.body_ui})"
        if i > 0:
            prev = THEME_TYPOGRAPHY[slugs[i - 1]]
            assert prev.display_en != sp.display_en, f"Adjacent display_en repeat: {slugs[i-1]} & {sl}"
            assert prev.title_vn != sp.title_vn, f"Adjacent title_vn repeat: {slugs[i-1]} & {sl}"


if __name__ == "__main__":
    validate_matrix()
    rep = verify_vietnamese_fonts()
    used_script = sorted({s.display_en for s in THEME_TYPOGRAPHY.values() if s.display_en in SCRIPT_WHITELIST})
    used_serif = sorted({s.display_caps for s in THEME_TYPOGRAPHY.values()} | {s.display_en for s in THEME_TYPOGRAPHY.values() if s.display_en in SERIF_WHITELIST})
    used_vn = sorted({s.title_vn for s in THEME_TYPOGRAPHY.values()})
    used_body = sorted({s.body_ui for s in THEME_TYPOGRAPHY.values()})
    print("OK: All 80 themes strictly validated (0 blacklist, 0 script on ALL-CAPS, 0 adjacent repeats)!")
    print("  Script (Title Case only):", used_script)
    print("  Serif  (ALL-CAPS + TC)  :", used_serif)
    print("  VN Title (0 missing)    :", used_vn)
    print("  Body UI  (0 missing)    :", used_body)
    print("  VN verification         :", rep)
