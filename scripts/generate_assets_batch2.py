"""
generate_assets_batch2.py
=========================

Generates the 9 brand-new high-DPI (300x300px, 4x supersampled) kawaii/vector
growth-stage sprite sets for Templates 11..19 + contact sheet for visual QA:

  11. velvet_rose       (Crimson Velvet Rose in ribbed slate-blue pot)
  12. blue_tulip        (Royal Blue Tulip in terracotta pot)
  13. blossom_star      (Magenta-Gold Blossom from dark soil & falling seeds)
  14. forest_tree       (Emerald Forest Tree on tan soil mound)
  15. mocha_sunflower   (Earthy Golden Sunflower grounded in espresso soil)
  16. dream_house       (Campfire -> Tent -> Hut -> Cottage -> 2-Story -> Modern Villa!)
  17. wildflower_mood   (Pink 5-Petal Cosmos/Wildflower Cluster)
  18. plum_oak          (Grand Forest Oak Tree with red meadow flowers at roots)
  19. meadow_sunflower  (Fresh Spring Lime & Vivid Green Meadow Sunflower)

Output:
  assets/<slug>/stage_0.png .. stage_5.png   (54 PNGs, 300x300 RGBA transparent)
  previews/assets_contact_sheet_batch2.png
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from generate_assets import (
    ASSETS_DIR, PREVIEW_DIR, BOTTOM, Sprite,
    E, C, RR, PG, LN, ARC,
    mix, with_alpha, quad, round_poly, leaf_pts, round_petal_pts, along,
    star_pts, tapered_body, classic_pot, stem_leaves_group, corner_sparkles,
    build_contact_sheet,
)

BATCH2_SLUGS = [
    "velvet_rose",
    "blue_tulip",
    "blossom_star",
    "forest_tree",
    "mocha_sunflower",
    "dream_house",
    "wildflower_mood",
    "plum_oak",
    "meadow_sunflower",
]


def _soil_mound(sp: Sprite, fill="#6B3E26", ol="#422416", hi="#8B5A3C",
                cx=128.0, top_y=214.0, hw=58.0, pebbles=True):
    """Lush organic soil mound resting cleanly on BOTTOM."""
    pts = [
        (cx - hw, BOTTOM),
        (cx - hw * 0.85, top_y + 12),
        (cx - hw * 0.45, top_y + 2),
        (cx, top_y),
        (cx + hw * 0.45, top_y + 2),
        (cx + hw * 0.85, top_y + 12),
        (cx + hw, BOTTOM),
    ]
    m = sp.group([PG(round_poly(pts, 12), fill)], ol, ow=6.0)
    sp.detail([
        E((cx - hw * 0.55, top_y + 4, cx + hw * 0.15, top_y + 13), with_alpha(hi, 175)),
        PG([(cx + hw * 0.15, top_y - 2), (cx + hw + 6, top_y - 2),
            (cx + hw + 6, BOTTOM + 6), (cx + hw * 0.05, BOTTOM + 6)],
           with_alpha(ol, 75)),
    ], clip=m)
    if pebbles:
        sp.detail([
            C(cx - hw * 0.42, BOTTOM - 7, 3.2, with_alpha(ol, 160)),
            C(cx + hw * 0.35, BOTTOM - 6, 3.8, with_alpha(ol, 160)),
            C(cx - hw * 0.08, BOTTOM - 9, 2.8, with_alpha(hi, 190)),
        ], clip=m)


def _slate_ribbed_pot(sp: Sprite, plant_fn=None, cx=128.0):
    """Ribbed slate-blue pot (#4A6572) matching Ref 11 (Plant a Rose)."""
    body = "#526E7C"
    body_ol = "#2F434D"
    rim = "#648292"
    soil = "#6E4735"
    soil_ol = "#3F261B"
    body_top = 184.0
    top_hw, bot_hw = 40.0, 29.0
    body_pts = tapered_body(cx, body_top, BOTTOM, top_hw, bot_hw, r_top=4, r_bot=10)
    m = sp.group([PG(body_pts, body)], body_ol, ow=6.0)
    # Subtle vertical ribs + shading
    sp.detail([
        PG([(cx + 12, body_top), (cx + 50, body_top), (cx + 50, BOTTOM + 4), (cx + 9, BOTTOM + 4)],
           mix(body, body_ol, 0.32)),
        LN([(cx - 18, body_top + 6), (cx - 13, BOTTOM - 5)], 2.6, with_alpha("#94B3C2", 140)),
        LN([(cx, body_top + 6), (cx, BOTTOM - 5)], 2.6, with_alpha("#94B3C2", 110)),
        LN([(cx + 16, body_top + 6), (cx + 12, BOTTOM - 5)], 2.6, with_alpha(body_ol, 120)),
    ], clip=m)
    sp.group([E((cx - 36, 173, cx + 36, 191), soil)], soil_ol, ow=5.0)
    if plant_fn:
        plant_fn(sp)
    rim_box = (cx - 46, 175, cx + 46, 191)
    mr = sp.group([RR(rim_box, 6, rim)], body_ol, ow=6.0)
    sp.detail([
        RR((cx - 39, 178, cx - 8, 182), 2, with_alpha("#FFFFFF", 115)),
        RR((cx + 16, 173, cx + 48, 193), 0, mix(rim, body_ol, 0.28)),
    ], clip=mr)


# --------------------------------------------------------------------------
# Theme 11: velvet_rose (Crimson Velvet Rose in ribbed slate pot)
# --------------------------------------------------------------------------
def velvet_rose(stage: int) -> Sprite:
    sp = Sprite()
    stem_c, leaf_c, leaf_d, green_ol = "#4E8E3E", "#65AE4F", "#3D732F", "#2B5322"
    rose_dark, rose_mid, rose_hi, rose_ol = "#9F1239", "#DC2655", "#FB7185", "#6B0F28"

    if stage == 5:
        sp.glow(128, 72, 90, "#F472B6", alpha=115, power=1.7)
        sp.rays(128, 72, 95, "#F9A8D4", n=10, alpha=85)

    def _plant(s):
        if stage == 0:
            # Plump rose seed nestled on soil
            s.group([E((119, 169, 137, 181), "#C48A5A")], "#6E4526", ow=4.5)
            s.detail([E((122, 171, 130, 175), with_alpha("#FFF2DF", 150))])
        elif stage == 1:
            stem_leaves_group(
                s, [(128, 180), (128, 152)], 6.5,
                [((128, 155), -142, 24, 13), ((128, 155), -38, 24, 13)],
                stem_c, leaf_c, green_ol, vein=leaf_d,
            )
        elif stage == 2:
            stem_leaves_group(
                s, [(128, 180), (126, 148), (129, 118)], 7.0,
                [((127, 154), -148, 30, 17), ((127, 152), -32, 30, 17),
                 ((128, 126), -142, 26, 15), ((129, 122), -36, 26, 15)],
                stem_c, leaf_c, green_ol, vein=leaf_d,
            )
        elif stage == 3:
            # Taller rose stem with thorns + 5 lush leaves
            stem_pts = [(128, 180), (125, 145), (130, 112), (127, 84)]
            thorns = [
                PG([(125, 160), (116, 155), (126, 152)], stem_c),
                PG([(130, 132), (139, 127), (129, 124)], stem_c),
            ]
            parts = [LN(stem_pts, 7.5, stem_c)] + thorns
            leaves = [
                ((126, 150), -150, 36, 20), ((128, 145), -30, 36, 20),
                ((129, 118), -145, 34, 19), ((129, 114), -34, 34, 19),
                ((127, 88), -92, 26, 15),
            ]
            for (b, a, ln, wd) in leaves:
                parts.append(PG(leaf_pts(b, a, ln, wd), leaf_c))
            s.group(parts, green_ol)
            s.detail([LN([along(b, a, ln * 0.2), along(b, a, ln * 0.72)], 2.4, leaf_d) for (b, a, ln, _) in leaves])
        elif stage == 4:
            # Tall leafy stem + tight crimson rosebud wrapped in sepals
            stem_pts = [(128, 180), (125, 146), (131, 114), (128, 86)]
            parts = [
                LN(stem_pts, 7.5, stem_c),
                PG([(125, 160), (116, 155), (126, 152)], stem_c),
                PG([(131, 132), (140, 127), (130, 124)], stem_c),
            ]
            leaves = [
                ((126, 150), -150, 38, 21), ((128, 144), -28, 38, 21),
                ((130, 118), -146, 36, 20), ((130, 114), -32, 36, 20),
            ]
            for (b, a, ln, wd) in leaves:
                parts.append(PG(leaf_pts(b, a, ln, wd), leaf_c))
            s.group(parts, green_ol)
            s.detail([LN([along(b, a, ln * 0.2), along(b, a, ln * 0.72)], 2.4, leaf_d) for (b, a, ln, _) in leaves])
            # Crimson rosebud
            bud = PG(round_poly([(128, 42), (146, 62), (143, 86), (113, 86), (110, 62)], 12), rose_mid)
            m = s.group([bud], rose_ol, ow=6.0)
            s.detail([
                PG([(128, 44), (144, 62), (140, 86), (128, 86)], rose_dark),
                PG(leaf_pts((120, 72), -85, 22, 10), with_alpha(rose_hi, 175)),
            ], clip=m)
            # Green calyx sepals hugging bud base
            s.group([
                PG(leaf_pts((128, 90), -122, 24, 11), leaf_c),
                PG(leaf_pts((128, 90), -58, 24, 11), leaf_c),
                PG(leaf_pts((128, 90), -90, 19, 10), stem_c),
            ], green_ol, ow=4.5)
        elif stage == 5:
            # Tall leafy stem + full layered Velvet Crimson Rose!
            stem_pts = [(128, 180), (126, 146), (130, 118), (128, 96)]
            parts = [
                LN(stem_pts, 8.0, stem_c),
                PG([(126, 162), (117, 157), (127, 154)], stem_c),
                PG([(130, 134), (139, 129), (129, 126)], stem_c),
            ]
            leaves = [
                ((127, 152), -150, 42, 22), ((128, 148), -28, 42, 22),
                ((129, 122), -145, 38, 21), ((129, 118), -34, 38, 21),
            ]
            for (b, a, ln, wd) in leaves:
                parts.append(PG(leaf_pts(b, a, ln, wd), leaf_c))
            s.group(parts, green_ol)
            s.detail([LN([along(b, a, ln * 0.2), along(b, a, ln * 0.72)], 2.5, leaf_d) for (b, a, ln, _) in leaves])
            # Outer lush crimson rose petals
            cy = 68.0
            outer = []
            for i in range(7):
                ang = -90 + i * (360 / 7)
                outer.append(PG(round_petal_pts((128, cy), ang, 42, 34), rose_dark if i % 2 else rose_mid))
            s.group(outer, rose_ol, ow=6.5)
            # Mid rosette petals
            mid = []
            for i in range(5):
                ang = -60 + i * 72
                mid.append(PG(round_petal_pts((128, cy - 2), ang, 30, 26), rose_mid if i % 2 == 0 else rose_hi))
            s.group(mid, rose_ol, ow=4.5)
            # Inner velvety spiral core
            s.group([C(128, cy - 2, 16, rose_dark)], rose_ol, ow=3.8)
            s.detail([
                ARC((115, cy - 15, 141, cy + 11), 20, 250, 3.6, rose_hi),
                ARC((120, cy - 10, 136, cy + 6), 140, 360, 3.0, "#FFE4E6"),
            ])

    _slate_ribbed_pot(sp, plant_fn=_plant)
    if stage == 5:
        corner_sparkles(sp, [(56, 46, 13), (202, 48, 12), (194, 112, 9)])
    return sp


# --------------------------------------------------------------------------
# Theme 12: blue_tulip (Royal Blue Tulip in terracotta pot — Ref Mint-to-Lemon)
# --------------------------------------------------------------------------
def blue_tulip(stage: int) -> Sprite:
    sp = Sprite()
    pot = dict(body="#C98365", body_ol="#8E5238", rim="#D99374", rim_ol="#8E5238",
               soil="#7B4F3B", soil_ol="#4E3024")
    stem_c, leaf_c, leaf_d, green_ol = "#2CA58D", "#38C299", "#1E806C", "#186455"
    tulip_c, tulip_d, tulip_hi, tulip_ol = "#3B5BDB", "#2741A8", "#749BFF", "#1C2E78"

    if stage == 5:
        sp.glow(128, 76, 86, "#93C5FD", alpha=130, power=1.7)

    def _plant(s):
        if stage == 0:
            return
        elif stage == 1:
            # Cute twin oval baby leaves
            s.group([
                LN([(128, 178), (128, 152)], 6.5, stem_c),
                PG(leaf_pts((128, 158), -138, 34, 20, sharp=0.65), leaf_c),
                PG(leaf_pts((128, 158), -42, 34, 20, sharp=0.65), leaf_c),
            ], green_ol)
        elif stage == 2:
            # Lush sweeping tulip foliage
            s.group([
                LN([(128, 178), (128, 128)], 7.5, stem_c),
                PG(leaf_pts((128, 166), -132, 56, 26, sharp=0.62), leaf_c),
                PG(leaf_pts((128, 166), -48, 56, 26, sharp=0.62), leaf_c),
                PG(leaf_pts((128, 162), -90, 44, 18, sharp=0.7), stem_c),
            ], green_ol)
        elif stage == 3:
            # Foliage + emerging indigo tulip bud
            s.group([
                LN([(128, 178), (128, 114)], 7.5, stem_c),
                PG(leaf_pts((128, 168), -135, 62, 28, sharp=0.6), leaf_c),
                PG(leaf_pts((128, 168), -45, 62, 28, sharp=0.6), leaf_c),
            ], green_ol)
            m = s.group([E((114, 88, 142, 122), tulip_c)], tulip_ol, ow=5.5)
            s.detail([E((119, 93, 128, 108), with_alpha(tulip_hi, 170))], clip=m)
        elif stage == 4:
            # Half-opened royal blue tulip rising taller
            s.group([
                LN([(128, 178), (128, 98)], 8.0, stem_c),
                PG(leaf_pts((128, 168), -136, 68, 29, sharp=0.6), leaf_c),
                PG(leaf_pts((128, 168), -44, 68, 29, sharp=0.6), leaf_c),
            ], green_ol)
            # 2-petal cup
            m = s.group([
                PG(round_petal_pts((128, 108), -106, 46, 28), tulip_c),
                PG(round_petal_pts((128, 108), -74, 46, 28), tulip_d),
                PG(round_petal_pts((128, 108), -90, 48, 24), tulip_c),
            ], tulip_ol, ow=6.0)
            s.detail([E((118, 70, 127, 94), with_alpha(tulip_hi, 175))], clip=m)
        elif stage == 5:
            # Full radiant Royal Blue Tulip (3-scallop crown + broad leaves!)
            s.group([
                LN([(128, 178), (128, 92)], 8.5, stem_c),
                PG(leaf_pts((128, 170), -138, 76, 32, sharp=0.58), leaf_c),
                PG(leaf_pts((128, 170), -42, 76, 32, sharp=0.58), leaf_c),
            ], green_ol)
            s.detail([
                LN([(124, 162), (96, 130)], 2.8, leaf_d),
                LN([(132, 162), (160, 130)], 2.8, leaf_d),
            ])
            # Iconic 3-petal tulip silhouette
            m = s.group([
                PG(round_petal_pts((128, 106), -90, 62, 38), tulip_d),
                PG(round_petal_pts((122, 106), -114, 58, 34), tulip_c),
                PG(round_petal_pts((134, 106), -66, 58, 34), tulip_c),
            ], tulip_ol, ow=6.5)
            s.detail([
                PG(round_petal_pts((122, 100), -105, 42, 15), with_alpha(tulip_hi, 155)),
                E((124, 56, 133, 76), with_alpha("#DBEAFE", 140)),
            ], clip=m)

    classic_pot(
        sp, **pot,
        rim_box=(82, 172, 174, 190), body_top=184, top_hw=41, bot_hw=31,
        soil_box=(91, 167, 165, 184), plant=_plant,
    )
    if stage == 5:
        corner_sparkles(sp, [(58, 48, 12), (200, 48, 13), (196, 114, 9)])
    return sp


# --------------------------------------------------------------------------
# Theme 13: blossom_star (Magenta-Gold Blossom from dark soil & falling seeds)
# --------------------------------------------------------------------------
def blossom_star(stage: int) -> Sprite:
    sp = Sprite()
    stem_c, leaf_c, leaf_d, green_ol = "#46A049", "#6BD15E", "#2D7A36", "#1F5726"
    pink_c, pink_hi, pink_ol = "#EC4899", "#FBCFE8", "#9D174D"
    gold_c, gold_ol = "#F59E0B", "#B45309"

    if stage == 5:
        sp.glow(128, 78, 92, "#FDE68A", alpha=145, power=1.7)
        sp.rays(128, 78, 96, "#FBBF24", n=10, alpha=95)

    if stage == 0:
        # Falling seeds dropping into rich dark soil!
        seeds = [(116, 146, -28), (138, 164, 24), (122, 182, -16), (144, 194, 32)]
        for (sx, sy, ang) in seeds:
            sp.group([PG(leaf_pts((sx, sy), ang, 16, 9, sharp=0.7), "#D97757")], "#7C2D12", ow=3.5)
    elif stage == 1:
        # Curled tiny sprout emerging
        pts = quad((128, 222), (122, 184), (144, 178), n=12)
        sp.group([LN(pts, 7.0, stem_c), PG(leaf_pts((142, 178), -20, 22, 14), leaf_c)], green_ol)
    elif stage == 2:
        stem_leaves_group(
            sp, [(128, 222), (126, 180), (129, 152)], 8.0,
            [((128, 162), -140, 38, 22), ((129, 156), -40, 38, 22)],
            stem_c, leaf_c, green_ol, vein=leaf_d,
        )
    elif stage == 3:
        stem_leaves_group(
            sp, [(128, 222), (124, 172), (130, 124)], 8.5,
            [((125, 174), -148, 44, 25), ((127, 166), -32, 44, 25),
             ((129, 130), -136, 38, 22), ((130, 126), -44, 38, 22)],
            stem_c, leaf_c, green_ol, vein=leaf_d,
        )
    elif stage == 4:
        stem_leaves_group(
            sp, [(128, 222), (124, 168), (130, 114)], 9.0,
            [((125, 176), -148, 48, 26), ((127, 166), -30, 48, 26),
             ((129, 132), -142, 40, 23), ((130, 126), -38, 40, 23)],
            stem_c, leaf_c, green_ol, vein=leaf_d,
        )
        # Plump magenta bud with golden tip
        m = sp.group([E((110, 74, 146, 116), pink_c)], pink_ol, ow=6.0)
        s_star = PG(star_pts(128, 92, 12, inner=0.48), "#FDE047")
        sp.detail([E((116, 80, 127, 96), with_alpha(pink_hi, 170)), s_star], clip=m)
    elif stage == 5:
        stem_leaves_group(
            sp, [(128, 222), (124, 168), (130, 118)], 9.5,
            [((125, 178), -148, 52, 28), ((127, 168), -30, 52, 28),
             ((129, 136), -142, 42, 24), ((130, 132), -36, 42, 24)],
            stem_c, leaf_c, green_ol, vein=leaf_d,
        )
        cy = 82.0
        petals = [PG(round_petal_pts((128, cy), -90 + i * 60, 48, 34), pink_c if i % 2 == 0 else "#F472B6")
                  for i in range(6)]
        sp.group(petals, pink_ol, ow=6.5)
        for i in range(6):
            sp.detail([PG(round_petal_pts((128, cy), -90 + i * 60, 32, 13), with_alpha(pink_hi, 140))])
        # Golden star center
        sp.group([C(128, cy, 19, gold_c)], gold_ol, ow=5.0)
        sp.group([PG(star_pts(128, cy, 13, inner=0.48), "#FEF08A")], gold_ol, ow=2.5)
        corner_sparkles(sp, [(54, 48, 14), (204, 48, 13), (200, 120, 10)])

    _soil_mound(sp, fill="#4E3830", ol="#2B1C17", hi="#75554A", hw=58.0, top_y=215.0)
    return sp


# --------------------------------------------------------------------------
# Theme 14: forest_tree (Emerald Forest Tree on sandy-tan mound — Ref Gold Stars)
# --------------------------------------------------------------------------
def forest_tree(stage: int) -> Sprite:
    sp = Sprite()
    mound_f, mound_ol, mound_hi = "#C99B6D", "#8B623B", "#E2BC94"
    trunk_c, trunk_ol = "#2F7D61", "#1B523F"
    canopy_c, canopy_hi, canopy_d, canopy_ol = "#34D399", "#6EE7B7", "#10B981", "#157355"

    if stage == 5:
        sp.glow(128, 108, 98, "#A7F3D0", alpha=130, power=1.7)

    if stage == 1:
        stem_leaves_group(
            sp, [(128, 218), (128, 178)], 6.5,
            [((128, 182), -140, 26, 16), ((128, 182), -40, 26, 16)],
            trunk_c, canopy_c, canopy_ol,
        )
    elif stage == 2:
        stem_leaves_group(
            sp, [(128, 218), (128, 144)], 7.0,
            [((128, 174), -145, 30, 18), ((128, 174), -35, 30, 18),
             ((128, 148), -136, 26, 16), ((128, 148), -44, 26, 16)],
            trunk_c, canopy_c, canopy_ol,
        )
    elif stage == 3:
        # Young slender oval emerald tree
        sp.group([LN([(128, 218), (128, 152)], 9.0, trunk_c)], trunk_ol, ow=5.5)
        m = sp.group([E((90, 96, 166, 186), canopy_c)], canopy_ol, ow=6.5)
        sp.detail([
            E((98, 108, 126, 158), with_alpha(canopy_hi, 145)),
            PG([(134, 92), (174, 92), (174, 190), (134, 190)], with_alpha(canopy_d, 125)),
            LN([(128, 186), (128, 128)], 5.0, trunk_c),
            LN([(128, 158), (112, 142)], 3.8, trunk_c),
            LN([(128, 148), (144, 134)], 3.8, trunk_c),
        ], clip=m)
    elif stage == 4:
        # Tall rounded emerald tree
        sp.group([LN([(128, 218), (128, 158)], 10.5, trunk_c)], trunk_ol, ow=5.5)
        m = sp.group([
            E((76, 62, 180, 186), canopy_c),
            C(128, 86, 36, canopy_c),
        ], canopy_ol, ow=6.5)
        sp.detail([
            E((86, 76, 124, 146), with_alpha(canopy_hi, 145)),
            PG([(136, 54), (186, 54), (186, 192), (136, 192)], with_alpha(canopy_d, 130)),
            LN([(128, 188), (128, 108)], 5.5, trunk_c),
            LN([(128, 154), (104, 132)], 4.2, trunk_c),
            LN([(128, 138), (150, 118)], 4.2, trunk_c),
        ], clip=m)
    elif stage == 5:
        # Majestic lush Emerald Forest Tree + Golden Star accents!
        sp.group([LN([(128, 218), (128, 160)], 12.0, trunk_c)], trunk_ol, ow=6.0)
        m = sp.group([
            C(128, 72, 42, canopy_c),
            C(94, 112, 38, canopy_c),
            C(162, 112, 38, canopy_c),
            C(98, 148, 36, canopy_c),
            C(158, 148, 36, canopy_c),
            E((82, 74, 174, 184), canopy_c),
        ], canopy_ol, ow=7.0)
        sp.detail([
            C(104, 86, 26, with_alpha(canopy_hi, 145)),
            PG([(138, 28), (206, 28), (206, 190), (138, 190)], with_alpha(canopy_d, 125)),
            LN([(128, 188), (128, 96)], 6.0, trunk_c),
            LN([(128, 156), (98, 130)], 4.5, trunk_c),
            LN([(128, 140), (156, 116)], 4.5, trunk_c),
            LN([(128, 120), (108, 100)], 3.8, trunk_c),
        ], clip=m)
        # Golden star sparkles matching the Gold Stars theme!
        for (sx, sy, sr) in [(54, 52, 14), (202, 50, 15), (196, 146, 10)]:
            sp.group([PG(star_pts(sx, sy, sr, inner=0.46), "#FBBF24")], "#B45309", ow=3.0)

    _soil_mound(sp, fill=mound_f, ol=mound_ol, hi=mound_hi, hw=60.0, top_y=212.0, pebbles=False)
    return sp


# --------------------------------------------------------------------------
# Theme 15: mocha_sunflower (Earthy Golden Sunflower grounded in espresso soil)
# --------------------------------------------------------------------------
def mocha_sunflower(stage: int) -> Sprite:
    sp = Sprite()
    stem_c, leaf_c, leaf_d, green_ol = "#65A30D", "#84CC16", "#4D7C0F", "#365314"
    pet1, pet2, pet_ol = "#FACC15", "#F59E0B", "#B45309"
    ctr, ctr_ol = "#784212", "#451A03"

    if stage == 5:
        sp.glow(128, 80, 94, "#FEF08A", alpha=130, power=1.7)

    if stage == 1:
        # Single curved vibrant green shoot
        sp.group([
            LN([(128, 220), (128, 178)], 7.0, stem_c),
            PG(leaf_pts((128, 184), -62, 30, 17), leaf_c),
        ], green_ol)
    elif stage == 2:
        stem_leaves_group(
            sp, [(128, 220), (128, 162)], 7.5,
            [((128, 172), -142, 38, 22), ((128, 172), -38, 38, 22)],
            stem_c, leaf_c, green_ol, vein=leaf_d,
        )
    elif stage == 3:
        stem_leaves_group(
            sp, [(128, 220), (126, 168), (129, 126)], 8.5,
            [((127, 178), -148, 48, 26), ((127, 172), -32, 48, 26),
             ((129, 134), -65, 36, 20)],
            stem_c, leaf_c, green_ol, vein=leaf_d,
        )
    elif stage == 4:
        stem_leaves_group(
            sp, [(128, 220), (126, 158), (129, 102)], 9.0,
            [((127, 180), -148, 52, 28), ((127, 174), -32, 52, 28),
             ((128, 138), -144, 46, 25), ((129, 132), -36, 46, 25)],
            stem_c, leaf_c, green_ol, vein=leaf_d,
        )
        # Golden bud emerging from green calyx
        sp.group([C(129, 88, 20, pet1)], pet_ol, ow=5.0)
        sp.group([
            PG(leaf_pts((129, 108), -122, 24, 12), leaf_c),
            PG(leaf_pts((129, 108), -58, 24, 12), leaf_c),
        ], green_ol, ow=4.5)
    elif stage == 5:
        stem_leaves_group(
            sp, [(128, 220), (127, 168), (128, 118)], 9.5,
            [((127, 186), -150, 56, 30), ((128, 180), -30, 56, 30),
             ((128, 146), -144, 48, 26), ((128, 140), -36, 48, 26)],
            stem_c, leaf_c, green_ol, vein=leaf_d,
        )
        cy = 78.0
        back = [PG(leaf_pts((128, cy), i * 22.5 + 11.25, 56, 22, sharp=0.65), pet2) for i in range(16)]
        front = [PG(leaf_pts((128, cy), i * 22.5, 54, 21, sharp=0.65), pet1) for i in range(16)]
        sp.group(back + front, pet_ol, ow=5.5)
        m = sp.group([C(128, cy, 27, ctr)], ctr_ol, ow=5.5)
        # Textured mocha seed dots
        dots = []
        for r_d, cnt in ((10, 6), (18, 10)):
            for i in range(cnt):
                a = math.radians(i * 360 / cnt)
                dots.append(C(128 + r_d * math.cos(a), cy + r_d * math.sin(a), 2.3, "#9C5B2B"))
        sp.detail(dots, clip=m)
        corner_sparkles(sp, [(48, 42, 12), (208, 44, 12)])

    _soil_mound(sp, fill="#6E3E26", ol="#3D1F10", hi="#91583A", hw=64.0, top_y=214.0)
    return sp


# --------------------------------------------------------------------------
# Theme 16: dream_house (Campfire -> Tent -> Hut -> Cottage -> 2-Story -> Luxury Villa!)
# --------------------------------------------------------------------------
def dream_house(stage: int) -> Sprite:
    sp = Sprite()
    slate, slate_d, slate_ol = "#475569", "#334155", "#1E293B"
    em, em_d, em_ol = "#10B981", "#047857", "#064E3B"
    cream, blush, wood, wood_ol = "#FFFDF9", "#E5A9B4", "#A16244", "#5C331D"

    if stage == 5:
        sp.glow(128, 134, 108, "#A7F3D0", alpha=110, power=1.7)

    # Clean grassy ground strip shared across all 6 stages
    sp.group([RR((26, 224, 230, BOTTOM), 8, "#6EE7B7")], em_ol, ow=5.5)

    if stage == 0:
        # Empty plot + warm glowing Campfire!
        sp.glow(128, 186, 56, "#FBBF24", alpha=130, power=1.7)
        sp.group([
            LN([(92, 222), (164, 206)], 11, wood),
            LN([(164, 222), (92, 206)], 11, "#854D32"),
        ], wood_ol, ow=5.5)
        # Layered campfire flames
        sp.group([
            PG(round_poly([(128, 140), (154, 184), (144, 212), (112, 212), (102, 184)], 14), "#F97316"),
            PG(round_poly([(128, 160), (144, 192), (138, 210), (118, 210), (112, 192)], 10), "#FACC15"),
        ], "#B91C1C", ow=5.5)
        sp.detail([E((121, 184, 135, 206), "#FEF9C3")])

    elif stage == 1:
        # Cozy A-frame Camping Tent + tiny campfire on the left!
        tent = [(134, 130), (204, 224), (66, 224)]
        m = sp.group([PG(round_poly(tent, 6), "#B47B56")], wood_ol, ow=6.5)
        sp.detail([
            PG([(134, 130), (206, 224), (144, 224)], "#9A6240"),
            PG([(134, 164), (156, 224), (112, 224)], "#3E2723"),
        ], clip=m)
        # Tiny warm campfire on left
        sp.group([PG(round_poly([(56, 190), (68, 212), (62, 222), (50, 222), (44, 212)], 6), "#F97316")], "#B91C1C", ow=4.0)
        sp.detail([C(56, 212, 5, "#FDE047")])

    elif stage == 2:
        # Rustic Wooden Hut (thatched roof + plaster walls + wooden door)
        sp.group([RR((74, 146, 182, 224), 5, "#F5EFE6")], wood_ol, ow=6.0)
        # Wooden door & window
        sp.group([RR((114, 180, 142, 224), 8, wood)], wood_ol, ow=4.5)
        sp.group([RR((152, 174, 172, 196), 3, "#93C5FD")], wood_ol, ow=4.0)
        # Thatched gable roof
        roof = [(128, 102), (198, 152), (58, 152)]
        m = sp.group([PG(round_poly(roof, 10), "#9A6B49")], wood_ol, ow=6.5)
        sp.detail([PG([(128, 102), (198, 152), (132, 152)], "#7F5436")], clip=m)

    elif stage == 3:
        # Cozy Pastel Cottage (blush pitched roof, white walls, chimney, green door!)
        sp.group([RR((164, 98, 182, 142), 3, "#C88A94")], slate_ol, ow=5.0)
        sp.group([RR((56, 140, 200, 224), 5, cream)], slate_ol, ow=6.0)
        # Pastel blush roof
        roof = [(128, 92), (214, 144), (42, 144)]
        m = sp.group([PG(round_poly(roof, 8), "#D89AA6")], slate_ol, ow=6.5)
        sp.detail([PG([(128, 92), (214, 144), (134, 144)], "#BF7E8C")], clip=m)
        # Door + twin windows
        sp.group([RR((114, 178, 142, 224), 4, em)], em_ol, ow=4.5)
        sp.group([RR((72, 166, 98, 194), 3, "#BAE6FD"), RR((158, 166, 184, 194), 3, "#BAE6FD")], slate_ol, ow=4.0)
        sp.detail([
            LN([(85, 166), (85, 194)], 2.4, cream), LN([(72, 180), (98, 180)], 2.4, cream),
            LN([(171, 166), (171, 194)], 2.4, cream), LN([(158, 180), (184, 180)], 2.4, cream),
        ])

    elif stage == 4:
        # 2-Story Family House with attached garage!
        # Attached garage right
        sp.group([RR((164, 162, 220, 224), 4, "#F3EDE2")], slate_ol, ow=5.5)
        sp.group([RR((174, 182, 212, 224), 3, "#E2E8F0")], slate_ol, ow=4.0)
        sp.detail([LN([(176, 194), (210, 194)], 2.2, "#94A3B8"), LN([(176, 208), (210, 208)], 2.2, "#94A3B8")])
        # Main 2-story house body
        sp.group([RR((44, 114, 174, 224), 5, "#FEF3C7")], slate_ol, ow=6.0)
        # Pitched slate roof
        roof = [(109, 68), (186, 118), (32, 118)]
        m = sp.group([PG(round_poly(roof, 7), slate)], slate_ol, ow=6.5)
        sp.detail([PG([(109, 68), (186, 118), (114, 118)], slate_d)], clip=m)
        # Garage roof
        sp.group([PG(round_poly([(164, 146), (226, 164), (164, 164)], 4), slate)], slate_ol, ow=5.0)
        # Upper windows + lower door & window
        sp.group([
            RR((62, 130, 92, 156), 3, "#BAE6FD"),
            RR((126, 130, 156, 156), 3, "#BAE6FD"),
            RR((62, 178, 92, 204), 3, "#BAE6FD"),
        ], slate_ol, ow=4.0)
        sp.group([RR((124, 178, 152, 224), 4, em)], em_ol, ow=4.5)

    elif stage == 5:
        # Sleek Modern Luxury Villa (Multi-level Slate + Blush Accent + Mint Glass!)
        # Top-right penthouse volume
        sp.group([RR((114, 72, 208, 134), 4, slate)], slate_ol, ow=6.0)
        sp.group([RR((128, 86, 194, 122), 3, "#A7F3D0")], slate_ol, ow=4.0)
        # Cantilevered mid blush architectural deck
        sp.group([RR((38, 118, 164, 170), 4, blush)], slate_ol, ow=6.0)
        sp.group([RR((52, 130, 118, 160), 3, "#6EE7B7")], slate_ol, ow=4.0)
        # Ground floor crisp white + slate villa base
        sp.group([RR((48, 168, 218, 224), 4, cream)], slate_ol, ow=6.0)
        sp.group([RR((150, 142, 218, 224), 4, "#E2E8F0")], slate_ol, ow=5.5)
        # Floor-to-ceiling glass + architectural red/emerald entrance
        sp.group([
            RR((60, 178, 112, 224), 3, "#34D399"),
            RR((122, 180, 146, 224), 3, "#E63956"),
            RR((162, 158, 206, 224), 3, "#99F6E4"),
        ], slate_ol, ow=4.0)
        # Sleek overhanging flat roof slabs
        sp.group([
            RR((104, 62, 218, 76), 4, slate_d),
            RR((30, 110, 172, 122), 4, slate_d),
        ], slate_ol, ow=5.0)
        # Luxury garden hedges
        sp.group([C(42, 216, 13, em), C(220, 216, 13, em)], em_ol, ow=4.5)
        corner_sparkles(sp, [(46, 54, 13), (222, 48, 14), (218, 108, 9)])

    return sp


# --------------------------------------------------------------------------
# Theme 17: wildflower_mood (Pink 5-Petal Cosmos/Wildflower Cluster)
# --------------------------------------------------------------------------
def _draw_cosmos(sp: Sprite, cx: float, cy: float, r_pet: float,
                 pet_c="#F28B9C", pet_hi="#FBCFE8", pet_ol="#9D2C47"):
    petals = [PG(round_petal_pts((cx, cy), -90 + i * 72, r_pet, r_pet * 0.72), pet_c) for i in range(5)]
    sp.group(petals, pet_ol, ow=5.2)
    for i in range(5):
        sp.detail([PG(round_petal_pts((cx, cy), -90 + i * 72, r_pet * 0.65, r_pet * 0.28),
                      with_alpha(pet_hi, 140))])
    sp.group([C(cx, cy, r_pet * 0.34, "#FBBF24")], "#B45309", ow=3.8)
    sp.detail([C(cx - r_pet * 0.08, cy - r_pet * 0.08, r_pet * 0.12, "#FEF08A")])


def wildflower_mood(stage: int) -> Sprite:
    sp = Sprite()
    stem_c, leaf_c, leaf_d, green_ol = "#4E9454", "#6BBF6D", "#35703A", "#245228"

    if stage == 5:
        sp.glow(128, 86, 96, "#FBCFE8", alpha=130, power=1.7)

    if stage == 1:
        stem_leaves_group(
            sp, [(128, 218), (128, 182)], 6.0,
            [((128, 188), -138, 22, 13), ((128, 188), -42, 22, 13)],
            stem_c, leaf_c, green_ol,
        )
        sp.group([C(128, 176, 7.5, "#F28B9C")], "#9D2C47", ow=3.5)
    elif stage == 2:
        stem_leaves_group(
            sp, [(128, 218), (126, 172), (129, 142)], 7.0,
            [((127, 178), -146, 34, 18), ((128, 174), -34, 34, 18),
             ((129, 152), -138, 26, 15), ((129, 150), -42, 26, 15)],
            stem_c, leaf_c, green_ol, vein=leaf_d,
        )
        sp.group([E((119, 120, 139, 145), "#F28B9C")], "#9D2C47", ow=4.5)
    elif stage == 3:
        # Single blooming 5-petal Pink Cosmos
        stem_leaves_group(
            sp, [(128, 218), (126, 166), (128, 114)], 7.5,
            [((127, 182), -148, 38, 20), ((127, 176), -32, 38, 20),
             ((128, 148), -142, 32, 17), ((128, 144), -38, 32, 17)],
            stem_c, leaf_c, green_ol, vein=leaf_d,
        )
        _draw_cosmos(sp, 128, 96, 36)
    elif stage == 4:
        # Double pink wildflower blossoms
        stem_leaves_group(
            sp, [(128, 218), (126, 164), (104, 108)], 7.5,
            [((127, 184), -150, 38, 20), ((127, 176), -28, 38, 20),
             ((116, 146), -146, 30, 16)],
            stem_c, leaf_c, green_ol, vein=leaf_d,
        )
        stem_leaves_group(
            sp, [(128, 218), (134, 156), (156, 116)], 7.0,
            [((142, 148), -34, 28, 15)],
            stem_c, leaf_c, green_ol,
        )
        _draw_cosmos(sp, 102, 96, 34)
        _draw_cosmos(sp, 158, 108, 30)
    elif stage == 5:
        # Lush 3-Flower Pink Wildflower Cluster!
        sp.group([
            LN([(128, 218), (128, 154), (128, 86)], 8.0, stem_c),
            LN([(128, 218), (106, 166), (82, 116)], 7.0, stem_c),
            LN([(128, 218), (150, 166), (174, 116)], 7.0, stem_c),
            PG(leaf_pts((114, 186), -152, 42, 21), leaf_c),
            PG(leaf_pts((142, 186), -28, 42, 21), leaf_c),
            PG(leaf_pts((128, 156), -142, 34, 18), leaf_c),
            PG(leaf_pts((128, 156), -38, 34, 18), leaf_c),
        ], green_ol)
        _draw_cosmos(sp, 80, 108, 31)
        _draw_cosmos(sp, 176, 108, 31)
        _draw_cosmos(sp, 128, 72, 39)
        corner_sparkles(sp, [(50, 46, 12), (206, 46, 12)])

    _soil_mound(sp, fill="#5C3A2E", ol="#382018", hi="#7E5546", hw=60.0, top_y=215.0)
    return sp


# --------------------------------------------------------------------------
# Theme 18: plum_oak (Grand Forest Oak Tree + Red Meadow Flowers at Roots)
# --------------------------------------------------------------------------
def plum_oak(stage: int) -> Sprite:
    sp = Sprite()
    bark, bark_d, bark_ol = "#8D5B3C", "#6E442A", "#4A2C1A"
    leaf_d, leaf_m, leaf_l, leaf_ol = "#4D7C0F", "#65A30D", "#A3E635", "#2D4C08"

    if stage == 5:
        sp.glow(128, 96, 102, "#D9F99D", alpha=125, power=1.7)

    if stage == 0:
        # Acorn resting on soil
        sp.group([E((116, 198, 140, 218), "#B47B49")], bark_ol, ow=4.5)
        sp.group([RR((113, 193, 143, 204), 5, bark_d)], bark_ol, ow=4.0)
    elif stage == 1:
        stem_leaves_group(
            sp, [(128, 220), (128, 180)], 6.5,
            [((128, 184), -142, 28, 15), ((128, 184), -38, 28, 15)],
            leaf_d, leaf_m, leaf_ol,
        )
    elif stage == 2:
        stem_leaves_group(
            sp, [(128, 220), (126, 176), (130, 140)], 7.5,
            [((127, 182), -148, 32, 17), ((127, 176), -32, 32, 17),
             ((129, 148), -140, 30, 16), ((130, 144), -40, 30, 16)],
            bark, leaf_m, leaf_ol,
        )
    elif stage == 3:
        # Small sapling oak tree
        sp.group([
            LN([(128, 220), (128, 134)], 11.0, bark),
            LN([(128, 156), (104, 134)], 6.5, bark),
            LN([(128, 148), (152, 128)], 6.5, bark),
        ], bark_ol, ow=5.5)
        m = sp.group([
            C(128, 102, 36, leaf_m),
            C(98, 120, 28, leaf_m),
            C(158, 120, 28, leaf_m),
        ], leaf_ol, ow=6.5)
        sp.detail([C(116, 92, 20, with_alpha(leaf_l, 165)),
                   C(150, 124, 24, with_alpha(leaf_d, 145))], clip=m)
    elif stage == 4:
        # Fuller tall oak tree
        trunk = [(118, 222), (122, 136), (134, 136), (138, 222)]
        sp.group([PG(trunk, bark), LN([(128, 154), (96, 128)], 8.0, bark),
                  LN([(128, 144), (160, 122)], 8.0, bark)], bark_ol, ow=5.5)
        m = sp.group([
            C(128, 72, 38, leaf_m),
            C(94, 102, 34, leaf_m),
            C(162, 102, 34, leaf_m),
            C(96, 132, 30, leaf_m),
            C(160, 132, 30, leaf_m),
            C(128, 114, 42, leaf_m),
        ], leaf_ol, ow=6.5)
        sp.detail([
            C(116, 66, 22, with_alpha(leaf_l, 175)),
            C(96, 98, 18, with_alpha(leaf_l, 155)),
            C(158, 126, 28, with_alpha(leaf_d, 145)),
        ], clip=m)
    elif stage == 5:
        # Grand Forest Oak Tree + Red Meadow Flowers at the roots!
        trunk = [(112, 224), (120, 134), (136, 134), (144, 224)]
        m_tr = sp.group([
            PG(trunk, bark),
            LN([(128, 152), (90, 124)], 9.5, bark),
            LN([(128, 144), (166, 118)], 9.5, bark),
        ], bark_ol, ow=6.0)
        sp.detail([PG([(130, 134), (148, 134), (148, 226), (132, 226)], bark_d)], clip=m_tr)

        m = sp.group([
            C(128, 60, 42, leaf_m),
            C(86, 86, 36, leaf_m),
            C(170, 86, 36, leaf_m),
            C(78, 122, 34, leaf_m),
            C(178, 122, 34, leaf_m),
            C(112, 134, 34, leaf_m),
            C(146, 134, 34, leaf_m),
            C(128, 104, 48, leaf_m),
        ], leaf_ol, ow=7.0)
        sp.detail([
            C(118, 52, 26, with_alpha(leaf_l, 180)),
            C(88, 84, 20, with_alpha(leaf_l, 160)),
            C(164, 124, 34, with_alpha(leaf_d, 150)),
            C(138, 140, 26, with_alpha(leaf_d, 140)),
        ], clip=m)
        corner_sparkles(sp, [(46, 42, 13), (210, 42, 13)])

    _soil_mound(sp, fill="#6D442B", ol="#3F2415", hi="#8E5F41", hw=64.0, top_y=216.0)

    if stage == 5:
        # Iconic Red Meadow Flowers & grass tufts blooming at the oak roots!
        tufts = []
        for fx in (74, 96, 160, 182):
            tufts.append(LN([(fx, 224), (fx, 206)], 4.0, leaf_m))
        sp.group(tufts, leaf_ol, ow=3.0)
        for fx, fy in ((74, 202), (96, 206), (160, 206), (182, 202)):
            sp.group([
                PG(round_petal_pts((fx, fy + 6), -106, 14, 9), "#DC2626"),
                PG(round_petal_pts((fx, fy + 6), -74, 14, 9), "#EF4444"),
            ], "#7F1D1D", ow=3.0)

    return sp


# --------------------------------------------------------------------------
# Theme 19: meadow_sunflower (Fresh Spring Lime & Vivid Green Sunflower)
# --------------------------------------------------------------------------
def meadow_sunflower(stage: int) -> Sprite:
    sp = Sprite()
    stem_c, leaf_c, leaf_d, green_ol = "#22C55E", "#86EFAC", "#16A34A", "#14532D"
    leaf_vivid = "#4ADE80"
    pet1, pet2, pet_ol = "#FDE047", "#EAB308", "#A16207"
    ctr, ctr_ol = "#5C3317", "#3A1D0B"

    if stage == 5:
        sp.glow(128, 72, 92, "#FEF08A", alpha=140, power=1.7)
        sp.rays(128, 72, 96, "#DCFCE7", n=12, alpha=95)

    if stage == 1:
        stem_leaves_group(
            sp, [(128, 220), (128, 178)], 7.0,
            [((128, 182), -140, 30, 17), ((128, 182), -40, 30, 17)],
            stem_c, leaf_vivid, green_ol, vein=leaf_d,
        )
    elif stage == 2:
        stem_leaves_group(
            sp, [(128, 220), (128, 146)], 7.5,
            [((128, 182), -146, 36, 20), ((128, 182), -34, 36, 20),
             ((128, 152), -140, 32, 18), ((128, 152), -40, 32, 18)],
            stem_c, leaf_vivid, green_ol, vein=leaf_d,
        )
    elif stage == 3:
        # 3-tier crisp spring leafy stem
        stem_leaves_group(
            sp, [(128, 220), (128, 108)], 8.0,
            [((128, 188), -148, 42, 22), ((128, 188), -32, 42, 22),
             ((128, 154), -144, 38, 20), ((128, 154), -36, 38, 20),
             ((128, 122), -138, 32, 18), ((128, 122), -42, 32, 18)],
            stem_c, leaf_vivid, green_ol, vein=leaf_d,
        )
    elif stage == 4:
        # Multi-tier leafy stem + bright yellow-green sunflower bud opening up!
        stem_leaves_group(
            sp, [(128, 220), (128, 100)], 8.5,
            [((128, 190), -148, 44, 23), ((128, 190), -32, 44, 23),
             ((128, 156), -144, 40, 21), ((128, 156), -36, 40, 21),
             ((128, 124), -140, 34, 18), ((128, 124), -40, 34, 18)],
            stem_c, leaf_vivid, green_ol, vein=leaf_d,
        )
        # Yellow-green opening bud
        sp.group([
            PG(leaf_pts((128, 86), -110, 28, 15), pet1),
            PG(leaf_pts((128, 86), -90, 30, 16), pet2),
            PG(leaf_pts((128, 86), -70, 28, 15), pet1),
        ], pet_ol, ow=4.5)
        sp.group([C(128, 92, 18, "#84CC16")], green_ol, ow=5.0)
    elif stage == 5:
        stem_leaves_group(
            sp, [(128, 220), (128, 112)], 9.0,
            [((128, 190), -148, 46, 24), ((128, 190), -32, 46, 24),
             ((128, 158), -144, 42, 22), ((128, 158), -36, 42, 22),
             ((128, 128), -138, 36, 19), ((128, 128), -42, 36, 19)],
            stem_c, leaf_vivid, green_ol, vein=leaf_d,
        )
        cy = 72.0
        back = [PG(leaf_pts((128, cy), i * 24 + 12, 52, 20, sharp=0.65), pet2) for i in range(15)]
        front = [PG(leaf_pts((128, cy), i * 24, 50, 19, sharp=0.65), pet1) for i in range(15)]
        sp.group(back + front, pet_ol, ow=5.5)
        m = sp.group([C(128, cy, 24, ctr)], ctr_ol, ow=5.5)
        sp.detail([C(121, cy - 6, 7, with_alpha("#9A5B30", 170))], clip=m)
        corner_sparkles(sp, [(50, 42, 13), (206, 42, 13)])

    _soil_mound(sp, fill="#5D3A29", ol="#3A2116", hi="#7E523C", hw=58.0, top_y=215.0)
    return sp


BATCH2_THEMES = {
    "velvet_rose": velvet_rose,
    "blue_tulip": blue_tulip,
    "blossom_star": blossom_star,
    "forest_tree": forest_tree,
    "mocha_sunflower": mocha_sunflower,
    "dream_house": dream_house,
    "wildflower_mood": wildflower_mood,
    "plum_oak": plum_oak,
    "meadow_sunflower": meadow_sunflower,
}


def main():
    only = sys.argv[1:] or None
    results = {}
    for slug, fn in BATCH2_THEMES.items():
        if only and slug not in only:
            continue
        ims = []
        for stage in range(6):
            out = ASSETS_DIR / slug / f"stage_{stage}.png"
            ims.append(fn(stage).save(out))
            print(f"  {out.relative_to(ROOT)}  {out.stat().st_size / 1024:.1f} KB", flush=True)
        results[slug] = ims
    if not only:
        sheet_path = PREVIEW_DIR / "assets_contact_sheet_batch2.png"
        build_contact_sheet(results, sheet_path)
        print(f"Contact sheet: {sheet_path.relative_to(ROOT)}", flush=True)


if __name__ == "__main__":
    main()
