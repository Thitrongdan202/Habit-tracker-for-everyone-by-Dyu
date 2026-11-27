"""
hx.typography — v4.2 Bespoke 3-Tier Typography Matrix for ALL 80 Habit Tracker PC Themes (#01–#80).

Every theme has its own artistic identity built from 3 harmonious tiers:
  - Tier 1 (`display_en`): Expressive script / calligraphy / playful / editorial display font
                           for English titles, Month (`October`), Year/Garden banners & EN addons.
  - Tier 2 (`title_vn`):   100% Vietnamese-verified (0 missing glyphs via fontTools) expressive
                           serif / calligraphic humanist font for Vietnamese banners, taglines
                           and section headers across all 5 sheets.
  - Tier 3 (`body_ui`):    100% Vietnamese-verified clean, comfortable body font matched to each
                           theme's aesthetic (Pastel/Cute, Botanical/Zen/Vintage, Modern/RPG).
  - Companion (`num_font`):100% Vietnamese-verified crisp editorial serif/humanist font for
                           large Year (`2026`) & KPI numbers (`143`, `22 ngày`, `6 / 10`, `3 / 8`).

Strict guarantees:
  1. 100% built-in Windows / Microsoft Office fonts — zero broken fonts when opened on any Windows PC.
  2. ZERO missing Vietnamese diacritics on every `title_vn`, `num_font`, and `body_ui` cell.
  3. Adjacent themes (#i and #i+1) NEVER repeat `display_en` or `title_vn`.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path


# --------------------------------------------------------------------------- #
#  Optical Font Calibration Metrics (size delta, row-height boost, slant/bold)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class FontOptics:
    size_delta: float = 0.0      # Size adjustment relative to baseline Segoe UI
    rh_boost: float = 2.0        # Extra row height (pt) for tall ascenders/descenders
    italic: bool = False         # Apply Excel Italic (False if font is natively cursive!)
    bold: bool = True            # Apply Excel Bold (False for thin/ornate scripts that smear)
    max_month_pt: float = 22.0   # Safety cap for Month cell (B3) so "September" never clips


FONT_OPTICS: dict[str, FontOptics] = {
    # Flowing Romantic Calligraphy & Cursive (natively italic -> italic=False!)
    "Lucida Handwriting":    FontOptics(size_delta=0.0,  rh_boost=3.0, italic=False, bold=True,  max_month_pt=19.0),
    "Segoe Script":          FontOptics(size_delta=-0.5, rh_boost=3.0, italic=False, bold=True,  max_month_pt=18.5),
    "Gabriola":              FontOptics(size_delta=4.0,  rh_boost=6.0, italic=False, bold=False, max_month_pt=24.0),
    "Monotype Corsiva":      FontOptics(size_delta=3.0,  rh_boost=4.0, italic=False, bold=True,  max_month_pt=22.0),
    "French Script MT":      FontOptics(size_delta=6.0,  rh_boost=6.0, italic=False, bold=False, max_month_pt=26.0),
    "Vivaldi":               FontOptics(size_delta=3.5,  rh_boost=5.0, italic=False, bold=False, max_month_pt=23.0),
    "Freestyle Script":      FontOptics(size_delta=4.5,  rh_boost=4.5, italic=False, bold=False, max_month_pt=24.0),
    "Brush Script MT":       FontOptics(size_delta=3.0,  rh_boost=4.0, italic=False, bold=False, max_month_pt=22.0),
    "Script MT Bold":        FontOptics(size_delta=1.5,  rh_boost=3.5, italic=False, bold=False, max_month_pt=20.5),
    "Lucida Calligraphy":    FontOptics(size_delta=0.0,  rh_boost=3.5, italic=False, bold=True,  max_month_pt=18.5),
    "Harlow Solid Italic":   FontOptics(size_delta=1.5,  rh_boost=4.0, italic=False, bold=False, max_month_pt=20.0),
    "Pristina":              FontOptics(size_delta=3.0,  rh_boost=4.0, italic=False, bold=True,  max_month_pt=22.0),
    "Bradley Hand ITC":      FontOptics(size_delta=1.5,  rh_boost=3.0, italic=False, bold=True,  max_month_pt=20.0),
    "Ink Free":              FontOptics(size_delta=2.0,  rh_boost=3.5, italic=False, bold=True,  max_month_pt=20.5),
    "Segoe Print":           FontOptics(size_delta=-0.5, rh_boost=3.0, italic=False, bold=True,  max_month_pt=18.0),
    "Kristen ITC":           FontOptics(size_delta=-0.5, rh_boost=3.0, italic=False, bold=True,  max_month_pt=18.0),
    "Mistral":               FontOptics(size_delta=3.5,  rh_boost=4.0, italic=False, bold=False, max_month_pt=22.5),
    "Forte":                 FontOptics(size_delta=1.5,  rh_boost=3.5, italic=False, bold=False, max_month_pt=20.5),
    "Rage Italic":           FontOptics(size_delta=4.0,  rh_boost=4.5, italic=False, bold=False, max_month_pt=23.5),
    "Viner Hand ITC":        FontOptics(size_delta=1.5,  rh_boost=3.5, italic=False, bold=True,  max_month_pt=20.0),
    # Editorial / Luxury Serifs & Modern Display
    "Palatino Linotype":     FontOptics(size_delta=0.5,  rh_boost=2.5, italic=True,  bold=True,  max_month_pt=20.0),
    "Book Antiqua":          FontOptics(size_delta=0.5,  rh_boost=2.5, italic=True,  bold=True,  max_month_pt=20.0),
    "Garamond":              FontOptics(size_delta=2.5,  rh_boost=3.0, italic=True,  bold=True,  max_month_pt=22.0),
    "Baskerville Old Face":  FontOptics(size_delta=1.5,  rh_boost=3.0, italic=False, bold=True,  max_month_pt=21.0),
    "Bodoni MT":             FontOptics(size_delta=1.0,  rh_boost=2.5, italic=True,  bold=True,  max_month_pt=20.5),
    "Constantia":            FontOptics(size_delta=0.5,  rh_boost=2.5, italic=True,  bold=True,  max_month_pt=20.0),
    "Century Gothic":        FontOptics(size_delta=-0.5, rh_boost=2.0, italic=False, bold=True,  max_month_pt=18.5),
    # 100% Vietnamese-certified Title & Body fonts
    "Sitka Text":            FontOptics(size_delta=0.5,  rh_boost=2.5, italic=False, bold=True,  max_month_pt=20.0),
    "Cambria":               FontOptics(size_delta=0.5,  rh_boost=2.0, italic=False, bold=True,  max_month_pt=20.0),
    "Candara":               FontOptics(size_delta=0.5,  rh_boost=2.0, italic=False, bold=True,  max_month_pt=20.0),
    "Corbel":                FontOptics(size_delta=0.5,  rh_boost=2.0, italic=False, bold=True,  max_month_pt=20.0),
    "Times New Roman":       FontOptics(size_delta=1.0,  rh_boost=2.0, italic=True,  bold=True,  max_month_pt=20.5),
    "Segoe UI":              FontOptics(size_delta=0.0,  rh_boost=1.5, italic=False, bold=True,  max_month_pt=19.0),
    "Calibri":               FontOptics(size_delta=0.5,  rh_boost=1.5, italic=False, bold=True,  max_month_pt=19.5),
    "Verdana":               FontOptics(size_delta=-0.5, rh_boost=2.0, italic=False, bold=True,  max_month_pt=18.0),
}


@dataclass(frozen=True)
class TypographySpec:
    display_en: str             # Tier 1: English display / Month / EN headers
    title_vn: str               # Tier 2: Vietnamese banners / taglines / section headers (100% VN!)
    body_ui: str                # Tier 3: Clean comfortable body text (100% VN!)
    num_font: str               # Crisp editorial companion for Year & big KPI numbers (100% VN!)
    title_vn_italic: bool = True  # Flowing italic elegance on Vietnamese main banners
    vibe: str = "pastel"        # Style family tag

    @property
    def en_optics(self) -> FontOptics:
        return FONT_OPTICS.get(self.display_en, FontOptics())

    @property
    def vn_optics(self) -> FontOptics:
        return FONT_OPTICS.get(self.title_vn, FontOptics())


# --------------------------------------------------------------------------- #
#  CURATED 80-THEME TYPOGRAPHY MATRIX (#01–#80)
#  - Every theme has a distinct personality matching its colors & artwork.
#  - Adjacent themes (#i and #i+1) NEVER share `display_en` or `title_vn`.
#  - 100% of `title_vn`, `body_ui`, `num_font` are verified 0-missing Vietnamese.
# --------------------------------------------------------------------------- #
THEME_TYPOGRAPHY: dict[str, TypographySpec] = {
    # === BATCH 1 (#01–#10): Signature Floral, Botanical, Executive, Wellness, RPG ===
    "sunflower":              TypographySpec("Lucida Handwriting",   "Palatino Linotype", "Candara",           "Palatino Linotype", True,  "floral"),
    "cactus":                 TypographySpec("Segoe Script",         "Candara",           "Corbel",            "Constantia",        True,  "pastel"),
    "lotus_stars":            TypographySpec("Baskerville Old Face", "Cambria",           "Segoe UI",          "Cambria",           False, "executive"),
    "botanical":              TypographySpec("Gabriola",             "Constantia",        "Palatino Linotype", "Constantia",        True,  "botanical"),
    "lavender_moon":          TypographySpec("French Script MT",     "Sitka Text",        "Corbel",            "Palatino Linotype", True,  "dreamy"),
    "focus_rocket":           TypographySpec("Century Gothic",       "Cambria",           "Segoe UI",          "Cambria",           False, "modern"),
    "sakura_zen":             TypographySpec("Monotype Corsiva",     "Palatino Linotype", "Candara",           "Constantia",        True,  "floral"),
    "ocean_coral":            TypographySpec("Freestyle Script",     "Candara",           "Segoe UI",          "Sitka Text",        True,  "energetic"),
    "matcha_cafe":            TypographySpec("Mistral",              "Constantia",        "Corbel",            "Cambria",           True,  "botanical"),
    "aurora_rpg":             TypographySpec("Forte",                "Cambria",           "Calibri",           "Cambria",           False, "rpg"),

    # === BATCH 2 (#11–#19): Rose, Tulip, Blossom, Forest, Architect, Meadow ===
    "velvet_rose":            TypographySpec("Vivaldi",              "Times New Roman",   "Palatino Linotype", "Palatino Linotype", True,  "luxury"),
    "blue_tulip":             TypographySpec("Pristina",             "Corbel",            "Candara",           "Constantia",        True,  "pastel"),
    "blossom_star":           TypographySpec("Script MT Bold",       "Candara",           "Calibri",           "Sitka Text",        True,  "cute"),
    "forest_tree":            TypographySpec("Viner Hand ITC",       "Constantia",        "Sitka Text",        "Cambria",           True,  "botanical"),
    "mocha_sunflower":        TypographySpec("Book Antiqua",         "Palatino Linotype", "Candara",           "Palatino Linotype", True,  "vintage"),
    "dream_house":            TypographySpec("Bodoni MT",            "Cambria",           "Segoe UI",          "Cambria",           False, "architect"),
    "wildflower_mood":        TypographySpec("Lucida Calligraphy",   "Sitka Text",        "Corbel",            "Constantia",        True,  "floral"),
    "plum_oak":               TypographySpec("Garamond",             "Constantia",        "Cambria",           "Palatino Linotype", True,  "executive"),
    "meadow_sunflower":       TypographySpec("Gabriola",             "Palatino Linotype", "Candara",           "Constantia",        True,  "botanical"),

    # === BATCH 3 (#20–#31): Alpaca, Panda, Cats, Chick, Candy, Rose, Shiba, Akita ===
    "alpaca_cream":           TypographySpec("Ink Free",             "Candara",           "Corbel",            "Constantia",        True,  "cozy"),
    "alpaca_blush":           TypographySpec("Lucida Handwriting",   "Palatino Linotype", "Candara",           "Palatino Linotype", True,  "pastel"),
    "alpaca_matcha":          TypographySpec("Bradley Hand ITC",     "Constantia",        "Corbel",            "Sitka Text",        True,  "botanical"),
    "bamboo_panda":           TypographySpec("Mistral",              "Sitka Text",        "Candara",           "Cambria",           True,  "zen"),
    "royal_cat_cash":         TypographySpec("Vivaldi",              "Cambria",           "Segoe UI",          "Palatino Linotype", False, "royal"),
    "ginger_kitten":          TypographySpec("Segoe Print",          "Candara",           "Calibri",           "Constantia",        True,  "cute"),
    "purple_cat":             TypographySpec("Pristina",             "Palatino Linotype", "Corbel",            "Sitka Text",        True,  "dreamy"),
    "hatching_chick":         TypographySpec("Kristen ITC",          "Candara",           "Segoe UI",          "Constantia",        False, "cute"),
    "candy_jar":              TypographySpec("Harlow Solid Italic",  "Corbel",            "Candara",           "Palatino Linotype", True,  "sweet"),
    "rose_bouquet":           TypographySpec("French Script MT",     "Times New Roman",   "Palatino Linotype", "Palatino Linotype", True,  "floral"),
    "shiba_inu":              TypographySpec("Brush Script MT",      "Candara",           "Segoe UI",          "Cambria",           False, "playful"),
    "akita_inu":              TypographySpec("Lucida Calligraphy",   "Sitka Text",        "Corbel",            "Constantia",        True,  "winter"),

    # === BATCH 4 (#32–#35): Sakura Minimal, Mochi Cat, Bunny, Milk & Mocha ===
    "sakura_tree":            TypographySpec("Monotype Corsiva",     "Palatino Linotype", "Corbel",            "Palatino Linotype", True,  "minimal"),
    "mochi_cat":              TypographySpec("Script MT Bold",       "Candara",           "Calibri",           "Constantia",        True,  "pastel"),
    "fluffy_bunny":           TypographySpec("Freestyle Script",     "Corbel",            "Candara",           "Sitka Text",        True,  "cute"),
    "milk_mocha_bear":        TypographySpec("Segoe Script",         "Constantia",        "Candara",           "Palatino Linotype", True,  "cozy"),

    # === BATCH 5 (#36–#40): Digimon 7-Stage Collection ===
    "digimon_veemon":         TypographySpec("Forte",                "Cambria",           "Segoe UI",          "Cambria",           False, "rpg"),
    "digimon_agumon":         TypographySpec("Rage Italic",          "Constantia",        "Calibri",           "Cambria",           False, "rpg"),
    "digimon_gatomon":        TypographySpec("Lucida Calligraphy",   "Palatino Linotype", "Corbel",            "Palatino Linotype", True,  "pastel"),
    "digimon_gabumon":        TypographySpec("Bradley Hand ITC",     "Sitka Text",        "Segoe UI",          "Cambria",           False, "modern"),
    "digimon_piyomon":        TypographySpec("Brush Script MT",      "Candara",           "Calibri",           "Constantia",        True,  "energetic"),

    # === BATCH 6 (#41–#47): Digimon Batch 2 (7 & 8 Stage Ultra) ===
    "digimon_patamon":        TypographySpec("Pristina",             "Palatino Linotype", "Candara",           "Constantia",        True,  "dreamy"),
    "digimon_palmon":         TypographySpec("Gabriola",             "Constantia",        "Corbel",            "Palatino Linotype", True,  "floral"),
    "digimon_gomamon":        TypographySpec("Segoe Script",         "Corbel",            "Segoe UI",          "Cambria",           False, "ocean"),
    "digimon_guilmon":        TypographySpec("Forte",                "Cambria",           "Calibri",           "Cambria",           False, "rpg"),
    "digimon_terriermon":     TypographySpec("Kristen ITC",          "Candara",           "Corbel",            "Constantia",        False, "cute"),
    "digimon_renamon":        TypographySpec("Vivaldi",              "Sitka Text",        "Palatino Linotype", "Palatino Linotype", True,  "mystic"),
    "digimon_tentomon":       TypographySpec("Century Gothic",       "Cambria",           "Segoe UI",          "Cambria",           False, "tech"),

    # === BATCH 7 (#48–#60): Capybara Chill Collection (13 Bespoke Themes) ===
    "capybara_avocado":       TypographySpec("Ink Free",             "Constantia",        "Candara",           "Constantia",        True,  "botanical"),
    "capybara_onsen":         TypographySpec("Gabriola",             "Palatino Linotype", "Corbel",            "Palatino Linotype", True,  "zen"),
    "capybara_pip_puddle":    TypographySpec("Segoe Print",          "Candara",           "Calibri",           "Sitka Text",        True,  "cute"),
    "capybara_boba_pond":     TypographySpec("Script MT Bold",       "Corbel",            "Candara",           "Constantia",        True,  "cafe"),
    "capybara_bookworm":      TypographySpec("Bradley Hand ITC",     "Sitka Text",        "Palatino Linotype", "Cambria",           True,  "study"),
    "capybara_lofi_picnic":   TypographySpec("Freestyle Script",     "Candara",           "Corbel",            "Constantia",        True,  "lofi"),
    "capybara_foodie":        TypographySpec("Brush Script MT",      "Constantia",        "Candara",           "Sitka Text",        True,  "cafe"),
    "capybara_dino_hoodie":   TypographySpec("Kristen ITC",          "Corbel",            "Segoe UI",          "Cambria",           False, "playful"),
    "capybara_apple_orchard": TypographySpec("Lucida Handwriting",   "Palatino Linotype", "Candara",           "Palatino Linotype", True,  "orchard"),
    "capybara_pink_chill":    TypographySpec("Pristina",             "Candara",           "Corbel",            "Constantia",        True,  "dreamy"),
    "capybara_fairy_party":   TypographySpec("French Script MT",     "Sitka Text",        "Candara",           "Palatino Linotype", True,  "pastel"),
    "capybara_selfcare":      TypographySpec("Monotype Corsiva",     "Palatino Linotype", "Corbel",            "Constantia",        True,  "glow"),
    "capybara_traveler":      TypographySpec("Mistral",              "Constantia",        "Segoe UI",          "Cambria",           True,  "travel"),

    # === BATCH 8 (#61–#70): Loopy Pastel Collection (10 Distinct Scripts!) ===
    "loopy_red_bow":          TypographySpec("Script MT Bold",       "Palatino Linotype", "Candara",           "Palatino Linotype", True,  "pastel"),
    "loopy_taiyaki":          TypographySpec("Brush Script MT",      "Constantia",        "Corbel",            "Constantia",        True,  "cafe"),
    "loopy_piggy_cafe":       TypographySpec("Lucida Handwriting",   "Candara",           "Calibri",           "Palatino Linotype", True,  "sweet"),
    "loopy_sauna_sheep":      TypographySpec("Pristina",             "Sitka Text",        "Corbel",            "Constantia",        True,  "spa"),
    "loopy_honey_bee":        TypographySpec("Segoe Print",          "Candara",           "Segoe UI",          "Cambria",           False, "cute"),
    "loopy_poolside_duck":    TypographySpec("Freestyle Script",     "Corbel",            "Candara",           "Sitka Text",        True,  "summer"),
    "loopy_fluffy_commuter":  TypographySpec("Ink Free",             "Constantia",        "Segoe UI",          "Cambria",           True,  "cozy"),
    "loopy_panda_study":      TypographySpec("Bradley Hand ITC",     "Sitka Text",        "Corbel",            "Constantia",        True,  "study"),
    "loopy_ruffle_sleep":     TypographySpec("French Script MT",     "Palatino Linotype", "Candara",           "Palatino Linotype", True,  "dreamy"),
    "loopy_hair_roller":      TypographySpec("Harlow Solid Italic",  "Candara",           "Corbel",            "Constantia",        True,  "glow"),

    # === BATCH 9 (#71–#80): Lotso Chubby Plush Bear Collection (10 Distinct Scripts!) ===
    "lotso_strawberry":       TypographySpec("Monotype Corsiva",     "Palatino Linotype", "Candara",           "Palatino Linotype", True,  "floral"),
    "lotso_milk_cafe":        TypographySpec("Lucida Calligraphy",   "Candara",           "Corbel",            "Constantia",        True,  "cafe"),
    "lotso_flower_crown":     TypographySpec("Gabriola",             "Sitka Text",        "Palatino Linotype", "Palatino Linotype", True,  "floral"),
    "lotso_overalls":         TypographySpec("Kristen ITC",          "Constantia",        "Candara",           "Cambria",           False, "playful"),
    "lotso_lofi":             TypographySpec("Segoe Script",         "Corbel",            "Segoe UI",          "Sitka Text",        True,  "lofi"),
    "lotso_mood_detox":       TypographySpec("Forte",                "Candara",           "Calibri",           "Constantia",        True,  "comic"),
    "lotso_sweet_dreams":     TypographySpec("Vivaldi",              "Palatino Linotype", "Corbel",            "Palatino Linotype", True,  "dreamy"),
    "lotso_daisy_glow":       TypographySpec("Pristina",             "Sitka Text",        "Candara",           "Constantia",        True,  "floral"),
    "lotso_bunny_selfcare":   TypographySpec("French Script MT",     "Candara",           "Corbel",            "Palatino Linotype", True,  "spa"),
    "lotso_gift_box":         TypographySpec("Harlow Solid Italic",  "Constantia",        "Candara",           "Palatino Linotype", True,  "party"),
}


_VN_DIACRITIC_RE = re.compile(
    r"[ăâđêôơưĂÂĐÊÔƠƯáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ"
    r"ÁÀẢÃẠẤẦẨẪẬẮẰẲẴẶÉÈẺẼẸẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢÚÙỦŨỤỨỪỬỮỰÝỲỶỸỴ]"
)


def has_vietnamese(text: str) -> bool:
    """Returns True if text contains any Vietnamese accented character or đ/Đ."""
    return bool(text and _VN_DIACRITIC_RE.search(text))


def get_typography(slug: str) -> TypographySpec:
    return THEME_TYPOGRAPHY.get(
        slug,
        TypographySpec("Lucida Handwriting", "Palatino Linotype", "Candara", "Palatino Linotype", True, "default"),
    )


def verify_vietnamese_fonts() -> dict[str, int]:
    """Programmatically validates EVERY title_vn, body_ui & num_font against Windows TTF/TTC files."""
    from fontTools.ttLib import TTCollection, TTFont

    vn_codes = {ord(c) for c in "ăâđêôơưệữợắẫỰĐĂÂÊÔƠƯáàảãạéèẻẽẹíìỉĩịóòỏõọúùủũụýỳỷỹỵ"}
    font_dirs = [
        Path(r"C:\Windows\Fonts"),
        Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "Windows" / "Fonts",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "FontCache" / "4" / "CloudFonts",
    ]
    cmap_miss: dict[str, int] = {}
    for d in font_dirs:
        if not d.exists():
            continue
        for p in d.rglob("*"):
            if p.suffix.lower() not in (".ttf", ".otf", ".ttc"):
                continue
            try:
                fonts = TTCollection(str(p)).fonts if p.suffix.lower() == ".ttc" else [TTFont(str(p), fontNumber=0)]
                for f in fonts:
                    fam = f["name"].getBestFamilyName()
                    if not fam:
                        continue
                    cmap = f.getBestCmap() or {}
                    miss = sum(1 for c in vn_codes if c not in cmap)
                    if fam not in cmap_miss or miss < cmap_miss[fam]:
                        cmap_miss[fam] = miss
            except Exception:
                pass

    vn_fonts_used = set()
    en_fonts_used = set()
    for sp in THEME_TYPOGRAPHY.values():
        vn_fonts_used.update([sp.title_vn, sp.body_ui, sp.num_font])
        en_fonts_used.add(sp.display_en)

    # Sitka Text is registered via SitkaVF.ttf whose BestFamilyName is "Sitka"
    def lookup_miss(fam: str) -> int:
        if fam in cmap_miss:
            return cmap_miss[fam]
        if fam.startswith("Sitka") and "Sitka" in cmap_miss:
            return cmap_miss["Sitka"]
        return 999

    report: dict[str, int] = {}
    for fam in sorted(vn_fonts_used):
        m = lookup_miss(fam)
        report[fam] = m
        assert m == 0, f"VIETNAMESE FONT FAILURE: {fam!r} is missing {m} Vietnamese glyphs!"

    for fam in sorted(en_fonts_used):
        m = lookup_miss(fam)
        assert m < 999, f"MISSING DISPLAY FONT ON WINDOWS: {fam!r} not installed!"

    return report


def validate_matrix(ordered_slugs: list[str] | None = None) -> None:
    slugs = ordered_slugs or list(THEME_TYPOGRAPHY.keys())
    assert len(slugs) == 80, f"Expected 80 themes, got {len(slugs)}"
    for i, sl in enumerate(slugs):
        assert sl in THEME_TYPOGRAPHY, f"Missing typography for slug: {sl}"
        if i > 0:
            prev = THEME_TYPOGRAPHY[slugs[i - 1]]
            cur = THEME_TYPOGRAPHY[sl]
            assert prev.display_en != cur.display_en, f"Adjacent display_en repeat: {slugs[i-1]} & {sl} ({cur.display_en})"
            assert prev.title_vn != cur.title_vn, f"Adjacent title_vn repeat: {slugs[i-1]} & {sl} ({cur.title_vn})"


if __name__ == "__main__":
    validate_matrix()
    rep = verify_vietnamese_fonts()
    print(f"OK: All 80 themes validated (0 adjacent repeats)!")
    print(f"OK: All {len(rep)} VN-tier fonts verified 0 missing Vietnamese glyphs: {list(rep.keys())}")
    print(f"OK: {len({s.display_en for s in THEME_TYPOGRAPHY.values()})} distinct English display fonts across 80 themes!")
