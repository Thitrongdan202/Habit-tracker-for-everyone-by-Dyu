"""
generate_assets_batch3.py
=========================

Generates 12 brand-new adorable, high-DPI (300x300px, 4x supersampled) chibi/kawaii
6-stage transparent PNG sprite sets (72 PNGs) for Templates 20..31 + contact sheet:

  20. alpaca_cream      (Fluffy Latte Cream Alpaca)
  21. alpaca_blush      (Pastel Lavender-Pink Alpaca w/ Pink Flower Crown)
  22. alpaca_matcha     (Fresh Matcha-Mint Alpaca w/ Embroidered Green Saddle)
  23. bamboo_panda      (Chibi Bamboo Panda: basket -> hugging bamboo stalks)
  24. royal_cat_cash    (White Cat: under cardboard box -> Royal Crown Cat)
  25. ginger_kitten     (Ginger Tabby Kitten: curled in basket -> waving happy cat)
  26. purple_cat        (Pastel Slate-Grey Cat: closed box -> Royal Crown Cat)
  27. hatching_chick    (Smooth Egg -> Cracked -> Peeking -> Bouncing Fluffy Chick)
  28. candy_jar         (Empty Pink Glass Jar -> Overflowing Sweets & Swirl Lollipops)
  29. rose_bouquet      (Closed Green Bud -> Full-Bloom Watercolor Pink Rose Bouquet)
  30. shiba_inu         (Paw Bed -> Sleepy Pup -> Bandana Shiba -> Crowned Shiba Inu!)
  31. akita_inu         (Tatami Cushion -> Snowball Pup -> Braided-Collar Akita Inu!)

Output:
  assets/<slug>/stage_0.png .. stage_5.png   (72 PNGs, 300x300 RGBA transparent)
  previews/assets_contact_sheet_batch3.png
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
    star_pts, corner_sparkles, build_contact_sheet,
)

BATCH3_SLUGS = [
    "alpaca_cream", "alpaca_blush", "alpaca_matcha", "bamboo_panda",
    "royal_cat_cash", "ginger_kitten", "purple_cat", "hatching_chick",
    "candy_jar", "rose_bouquet", "shiba_inu", "akita_inu",
]


# --------------------------------------------------------------------------
# Shared kawaii facial & accessory helpers
# --------------------------------------------------------------------------
def _kawaii_eyes(sp: Sprite, cx: float, cy: float, dx: float = 14.0, r: float = 5.6,
                 eye_col="#2D2220", blush_col=(244, 143, 177, 175),
                 blush_dx: float | None = None, smile: str = "cat"):
    """Big sparkling chibi eyes + rosy blush + cute mouth."""
    bdx = blush_dx if blush_dx is not None else dx + 9.0
    parts = [
        # Rosy blush ovals
        E((cx - bdx - 7.5, cy + r * 0.45, cx - bdx + 7.5, cy + r * 1.6), blush_col),
        E((cx + bdx - 7.5, cy + r * 0.45, cx + bdx + 7.5, cy + r * 1.6), blush_col),
        # Glossy eyes
        C(cx - dx, cy, r, eye_col),
        C(cx + dx, cy, r, eye_col),
        C(cx - dx - r * 0.28, cy - r * 0.28, r * 0.38, "#FFFFFF"),
        C(cx + dx - r * 0.28, cy - r * 0.28, r * 0.38, "#FFFFFF"),
        C(cx - dx + r * 0.25, cy + r * 0.28, r * 0.18, with_alpha("#FFFFFF", 180)),
        C(cx + dx + r * 0.25, cy + r * 0.28, r * 0.18, with_alpha("#FFFFFF", 180)),
    ]
    if smile == "cat":
        # Tiny pink nose + :3 mouth
        parts.extend([
            PG([(cx - 3.2, cy + r * 0.2), (cx + 3.2, cy + r * 0.2), (cx, cy + r * 0.85)], "#F48FB1"),
            ARC((cx - 7.5, cy + r * 0.4, cx, cy + r * 1.55), 10, 170, 2.3, eye_col),
            ARC((cx, cy + r * 0.4, cx + 7.5, cy + r * 1.55), 10, 170, 2.3, eye_col),
        ])
    elif smile == "dog":
        # Cute dark button nose + joyful open puppy smile
        parts.extend([
            E((cx - 4.4, cy + r * 0.05, cx + 4.4, cy + r * 0.85), eye_col),
            ARC((cx - 8.0, cy + r * 0.45, cx, cy + r * 1.65), 15, 170, 2.4, eye_col),
            ARC((cx, cy + r * 0.45, cx + 8.0, cy + r * 1.65), 10, 165, 2.4, eye_col),
        ])
    elif smile == "happy_open":
        parts.extend([
            E((cx - 4.4, cy + r * 0.0, cx + 4.4, cy + r * 0.8), eye_col),
            E((cx - 6.0, cy + r * 0.9, cx + 6.0, cy + r * 2.15), "#F472B6"),
            ARC((cx - 8.0, cy + r * 0.4, cx, cy + r * 1.55), 15, 170, 2.4, eye_col),
            ARC((cx, cy + r * 0.4, cx + 8.0, cy + r * 1.55), 10, 165, 2.4, eye_col),
        ])
    elif smile == "tiny":
        parts.append(ARC((cx - 6.0, cy + r * 0.2, cx + 6.0, cy + r * 1.4), 20, 160, 2.4, eye_col))
    sp.detail(parts)


def _sleepy_eyes(sp: Sprite, cx: float, cy: float, dx: float = 12.0, eye_col="#4A3428"):
    sp.detail([
        E((cx - dx - 10, cy + 2, cx - dx + 2, cy + 9), (244, 143, 177, 160)),
        E((cx + dx - 2, cy + 2, cx + dx + 10, cy + 9), (244, 143, 177, 160)),
        ARC((cx - dx - 6, cy - 3, cx - dx + 6, cy + 5), 15, 165, 2.8, eye_col),
        ARC((cx + dx - 6, cy - 3, cx + dx + 6, cy + 5), 15, 165, 2.8, eye_col),
        ARC((cx - 4, cy + 4, cx + 4, cy + 10), 20, 160, 2.2, eye_col),
    ])


def _golden_crown(sp: Sprite, cx: float, bottom_y: float, scale: float = 1.0):
    """Sparkling 3-point Royal Golden Crown."""
    w = 24.0 * scale
    h = 22.0 * scale
    pts = [
        (cx - w, bottom_y),
        (cx - w * 1.12, bottom_y - h * 0.85),
        (cx - w * 0.48, bottom_y - h * 0.42),
        (cx, bottom_y - h * 1.05),
        (cx + w * 0.48, bottom_y - h * 0.42),
        (cx + w * 1.12, bottom_y - h * 0.85),
        (cx + w, bottom_y),
    ]
    m = sp.group([PG(round_poly(pts, 3.0 * scale), "#FACC15")], "#B45309", ow=4.2 * scale)
    sp.detail([
        RR((cx - w - 4, bottom_y - 5.5 * scale, cx + w + 4, bottom_y + 2), 2, "#F59E0B"),
        C(cx, bottom_y - h * 0.35, 3.6 * scale, "#EF4444"),
        C(cx - w * 0.62, bottom_y - h * 0.32, 2.6 * scale, "#38BDF8"),
        C(cx + w * 0.62, bottom_y - h * 0.32, 2.6 * scale, "#38BDF8"),
    ], clip=m)


def _heart(sp: Sprite, cx: float, cy: float, r: float, fill="#F472B6", ol="#BE185D"):
    pts = [
        (cx, cy + r * 0.95),
        (cx - r * 1.05, cy - r * 0.05),
        (cx - r * 0.62, cy - r * 0.85),
        (cx, cy - r * 0.35),
        (cx + r * 0.62, cy - r * 0.85),
        (cx + r * 1.05, cy - r * 0.05),
    ]
    sp.group([PG(round_poly(pts, r * 0.35), fill)], ol, ow=3.2)


# --------------------------------------------------------------------------
# Themes 20, 21, 22: Three Distinct Adorable Alpacas!
# --------------------------------------------------------------------------
def _draw_alpaca(stage: int, *, wool: str, shade: str, ol: str, ear_in: str,
                 hoof: str, glow: str, variant: str) -> Sprite:
    """Shared chibi fluffy Alpaca engine with 3 totally distinct personalities:
      - variant='cream'  (20): Warm fluffy latte alpaca + sparkles
      - variant='blush'  (21): Pastel periwinkle/pink alpaca + Pink Flower Crown & blush tail!
      - variant='matcha' (22): Mint matcha alpaca + leaf sprout & ornate embroidered green saddle!
    """
    sp = Sprite()
    if stage == 5:
        sp.glow(128, 128, 104, glow, alpha=130, power=1.7)

    # Scale & posture grow smoothly across stages 0 -> 5!
    if stage == 0:
        # Stage 0: Tiny curled sleeping baby alpaca fluffball on soft shadow
        sp.detail([E((82, BOTTOM - 14, 174, BOTTOM + 2), with_alpha(ol, 35))])
        m = sp.group([
            E((86, 178, 170, 232), wool),
            C(104, 186, 20, wool), C(128, 178, 22, wool), C(152, 188, 19, wool),
            PG(round_poly([(94, 166), (104, 146), (112, 168)], 4), wool),
            PG(round_poly([(124, 164), (132, 146), (138, 168)], 4), wool),
        ], ol, ow=5.8)
        sp.detail([E((116, 198, 174, 236), with_alpha(shade, 140))], clip=m)
        sp.detail([E((96, 182, 134, 214), "#FFFDFB")])
        _sleepy_eyes(sp, 115, 196, dx=9.5, eye_col=ol)
        return sp

    # Growth geometry for stages 1..5
    # (scale, body_cx, body_cy, head_cx, head_cy, standing)
    cfgs = {
        1: (0.58, 132, 206, 116, 176, False),
        2: (0.72, 134, 196, 112, 152, False),
        3: (0.84, 136, 176, 108, 118, True),
        4: (0.94, 138, 168, 106, 102, True),
        5: (1.04, 140, 162, 104, 88, True),
    }
    sc, bcx, bcy, hcx, hcy, standing = cfgs[stage]
    sp.detail([E((bcx - 58 * sc, BOTTOM - 14, bcx + 58 * sc, BOTTOM + 2), with_alpha(ol, 35))])

    # Legs (under body)
    leg_parts = []
    if standing:
        leg_xs = [bcx - 30 * sc, bcx - 10 * sc, bcx + 14 * sc, bcx + 32 * sc]
        for lx in leg_xs:
            leg_parts.append(RR((lx - 9 * sc, bcy + 14 * sc, lx + 9 * sc, BOTTOM - 1), 6 * sc, wool))
        ml = sp.group(leg_parts, ol, ow=5.5)
        for lx in leg_xs:
            sp.detail([RR((lx - 9 * sc, BOTTOM - 13 * sc, lx + 9 * sc, BOTTOM + 1), 3 * sc, hoof)], clip=ml)
    else:
        # Cute tucked sitting feet
        leg_parts = [
            E((bcx - 34 * sc, BOTTOM - 22 * sc, bcx - 8 * sc, BOTTOM), wool),
            E((bcx + 8 * sc, BOTTOM - 22 * sc, bcx + 34 * sc, BOTTOM), wool),
        ]
        ml = sp.group(leg_parts, ol, ow=5.2)
        sp.detail([
            E((bcx - 32 * sc, BOTTOM - 12 * sc, bcx - 14 * sc, BOTTOM), hoof),
            E((bcx + 14 * sc, BOTTOM - 12 * sc, bcx + 32 * sc, BOTTOM), hoof),
        ], clip=ml)

    # Fluffy cloud body + neck + head + ears + tail puff (single plush sticker silhouette!)
    tail_col = "#F9A8D4" if (variant == "blush" and stage >= 3) else wool
    ear_l = [(hcx - 18 * sc, hcy - 18 * sc), (hcx - 24 * sc, hcy - 46 * sc), (hcx - 4 * sc, hcy - 26 * sc)]
    ear_r = [(hcx + 4 * sc, hcy - 26 * sc), (hcx + 22 * sc, hcy - 46 * sc), (hcx + 18 * sc, hcy - 18 * sc)]
    body_parts = [
        # Tail puff on right
        C(bcx + 48 * sc, bcy - 6 * sc, 15 * sc, tail_col),
        # Main fluffy wool body puffs
        E((bcx - 46 * sc, bcy - 26 * sc, bcx + 48 * sc, bcy + 30 * sc), wool),
        C(bcx - 28 * sc, bcy - 12 * sc, 22 * sc, wool),
        C(bcx + 4 * sc, bcy - 18 * sc, 24 * sc, wool),
        C(bcx + 32 * sc, bcy - 8 * sc, 21 * sc, wool),
        C(bcx - 18 * sc, bcy + 14 * sc, 20 * sc, wool),
        C(bcx + 18 * sc, bcy + 14 * sc, 20 * sc, wool),
        # Thick woolly neck connecting body & head
        LN([(hcx + 2 * sc, hcy + 12 * sc), (bcx - 22 * sc, bcy - 4 * sc)], 34 * sc, wool),
        C(hcx - 10 * sc, (hcy + bcy) * 0.5, 19 * sc, wool),
        # Ears
        PG(round_poly(ear_l, 5 * sc), wool),
        PG(round_poly(ear_r, 5 * sc), wool),
        # Fluffy head & top wool curls!
        C(hcx, hcy, 30 * sc, wool),
        C(hcx - 14 * sc, hcy - 22 * sc, 13 * sc, wool),
        C(hcx, hcy - 26 * sc, 14 * sc, wool),
        C(hcx + 14 * sc, hcy - 22 * sc, 13 * sc, wool),
        C(hcx - 24 * sc, hcy - 4 * sc, 13 * sc, wool),
        C(hcx + 24 * sc, hcy - 4 * sc, 13 * sc, wool),
    ]
    mb = sp.group(body_parts, ol, ow=6.0)
    # Soft pastel shading on back/belly
    sp.detail([
        E((bcx - 6 * sc, bcy - 18 * sc, bcx + 62 * sc, bcy + 40 * sc), with_alpha(shade, 145)),
        PG(round_poly([(hcx - 16 * sc, hcy - 21 * sc), (hcx - 20 * sc, hcy - 38 * sc), (hcx - 8 * sc, hcy - 25 * sc)], 2.5 * sc), ear_in),
        PG(round_poly([(hcx + 8 * sc, hcy - 25 * sc), (hcx + 18 * sc, hcy - 38 * sc), (hcx + 15 * sc, hcy - 21 * sc)], 2.5 * sc), ear_in),
    ], clip=mb)

    # Variant-specific signature accessories!
    if variant == "matcha" and stage >= 4:
        # Ornate embroidered green & gold Peruvian-style saddle on back!
        sad = RR((bcx - 10 * sc, bcy - 26 * sc, bcx + 36 * sc, bcy + 14 * sc), 10 * sc, "#4E9F58")
        ms = sp.group([sad], "#1B4332", ow=4.0)
        sp.detail([
            RR((bcx - 6 * sc, bcy - 22 * sc, bcx + 32 * sc, bcy + 8 * sc), 7 * sc, "#FFFBEB"),
            RR((bcx - 2 * sc, bcy - 18 * sc, bcx + 28 * sc, bcy + 4 * sc), 5 * sc, "#6BBF74"),
        ], clip=ms)
        if stage == 5:
            # Cute gold tassels along saddle edge
            for tx in (bcx - 2 * sc, bcx + 12 * sc, bcx + 26 * sc):
                sp.group([C(tx, bcy + 14 * sc, 4.2 * sc, "#FACC15")], "#92400E", ow=2.2)

    if variant == "matcha" and stage in (2, 3):
        # Cute little green matcha leaf sprout on head!
        sp.group([
            PG(leaf_pts((hcx + 2 * sc, hcy - 34 * sc), -130, 18 * sc, 10 * sc), "#4ADE80"),
            PG(leaf_pts((hcx + 2 * sc, hcy - 34 * sc), -50, 18 * sc, 10 * sc), "#22C55E"),
        ], "#14532D", ow=3.0)

    # Soft face oval + sparkling chibi eyes
    sp.detail([E((hcx - 21 * sc, hcy - 12 * sc, hcx + 21 * sc, hcy + 18 * sc), "#FFFDFB")])
    _kawaii_eyes(sp, hcx, hcy + 1 * sc, dx=10.5 * sc, r=4.6 * sc, eye_col=ol,
                 blush_dx=16.5 * sc, smile="cat")

    if variant == "blush" and stage >= 3:
        # Pink Flower Crown progression (1 flower at stage 3 -> 2 at stage 4 -> full 3-flower crown at stage 5!)
        spots = [(hcx, hcy - 31 * sc)] if stage == 3 else (
            [(hcx - 11 * sc, hcy - 29 * sc), (hcx + 11 * sc, hcy - 29 * sc)] if stage == 4 else
            [(hcx - 15 * sc, hcy - 28 * sc), (hcx, hcy - 33 * sc), (hcx + 15 * sc, hcy - 28 * sc)]
        )
        for fx, fy in spots:
            petals = [PG(round_petal_pts((fx, fy), -90 + i * 72, 10 * sc, 8 * sc), "#F472B6") for i in range(5)]
            sp.group(petals, "#9D174D", ow=2.6)
            sp.group([C(fx, fy, 3.6 * sc, "#FEF08A")], "#B45309", ow=1.8)

    if stage == 4 and variant == "cream":
        _heart(sp, hcx + 42 * sc, hcy - 18 * sc, 10, "#F59E0B", "#92400E")
    if stage == 5:
        corner_sparkles(sp, [(46, 46, 13), (208, 52, 12), (204, 124, 9)])
    return sp


def alpaca_cream(stage: int) -> Sprite:
    return _draw_alpaca(stage, wool="#FFF8EE", shade="#E8D5BE", ol="#5C4033",
                        ear_in="#F5C6AA", hoof="#A67C52", glow="#FDE68A", variant="cream")


def alpaca_blush(stage: int) -> Sprite:
    return _draw_alpaca(stage, wool="#FBF6FF", shade="#DDD6FE", ol="#4C1D42",
                        ear_in="#F9A8D4", hoof="#A78BFA", glow="#FBCFE8", variant="blush")


def alpaca_matcha(stage: int) -> Sprite:
    return _draw_alpaca(stage, wool="#DDF5DE", shade="#A7D7A9", ol="#234E2A",
                        ear_in="#F9C6D0", hoof="#6BBF74", glow="#BBF7D0", variant="matcha")


# --------------------------------------------------------------------------
# Theme 23: bamboo_panda (Chibi Bamboo Panda)
# --------------------------------------------------------------------------
def _draw_panda_head(sp: Sprite, cx: float, cy: float, sc: float, happy: bool = False):
    dark = "#232326"
    # Round black ears + plump white head
    sp.group([
        C(cx - 28 * sc, cy - 26 * sc, 13 * sc, dark),
        C(cx + 28 * sc, cy - 26 * sc, 13 * sc, dark),
        E((cx - 38 * sc, cy - 30 * sc, cx + 38 * sc, cy + 30 * sc), "#FFFFFF"),
    ], dark, ow=5.8)
    # Tilted iconic black eye patches
    sp.detail([
        E((cx - 26 * sc, cy - 12 * sc, cx - 6 * sc, cy + 12 * sc), dark),
        E((cx + 6 * sc, cy - 12 * sc, cx + 26 * sc, cy + 12 * sc), dark),
        # Glossy sparkling eyes inside patches
        C(cx - 15 * sc, cy - 1 * sc, 5.2 * sc, "#111111"),
        C(cx + 15 * sc, cy - 1 * sc, 5.2 * sc, "#111111"),
        C(cx - 17 * sc, cy - 3.2 * sc, 2.7 * sc, "#FFFFFF"),
        C(cx + 13 * sc, cy - 3.2 * sc, 2.7 * sc, "#FFFFFF"),
        C(cx - 13 * sc, cy + 2.5 * sc, 1.3 * sc, "#FFFFFF"),
        C(cx + 17 * sc, cy + 2.5 * sc, 1.3 * sc, "#FFFFFF"),
        # Rosy pink cheeks
        E((cx - 31 * sc, cy + 7 * sc, cx - 18 * sc, cy + 16 * sc), (249, 168, 212, 185)),
        E((cx + 18 * sc, cy + 7 * sc, cx + 31 * sc, cy + 16 * sc), (249, 168, 212, 185)),
        # Tiny nose + smile
        E((cx - 4.5 * sc, cy + 4 * sc, cx + 4.5 * sc, cy + 10 * sc), dark),
        ARC((cx - 8 * sc, cy + 7 * sc, cx, cy + 16 * sc), 15, 170, 2.4 * sc, dark),
        ARC((cx, cy + 7 * sc, cx + 8 * sc, cy + 16 * sc), 10, 165, 2.4 * sc, dark),
    ])
    if happy:
        sp.detail([E((cx - 4.5 * sc, cy + 12 * sc, cx + 4.5 * sc, cy + 19 * sc), "#F472B6")])


def bamboo_panda(stage: int) -> Sprite:
    sp = Sprite()
    dark = "#232326"
    bam, bam_d, bam_ol = "#8EDB48", "#5EA822", "#2F5E10"

    if stage == 5:
        sp.glow(128, 126, 102, "#D9F99D", alpha=130, power=1.7)

    if stage == 0:
        # Tiny peeking baby panda head behind a bamboo leaf
        _draw_panda_head(sp, 128, 198, 0.72)
        sp.group([
            PG(leaf_pts((100, 232), -140, 38, 17), bam),
            PG(leaf_pts((156, 232), -40, 38, 17), bam),
            RR((74, 224, 182, BOTTOM), 7, "#A3E635"),
        ], bam_ol, ow=4.8)
    elif stage == 1:
        # Baby panda peeking adorably out of a woven bamboo basket!
        _draw_panda_head(sp, 128, 152, 0.88)
        # Cute little paws on basket rim
        sp.group([C(96, 182, 11, dark), C(160, 182, 11, dark)], dark, ow=4.0)
        # Woven warm wooden bamboo basket
        b_pts = [(70, 184), (186, 184), (170, BOTTOM), (86, BOTTOM)]
        mb = sp.group([PG(round_poly(b_pts, 10), "#D9A066")], "#784421", ow=6.0)
        sp.detail([
            LN([(74, 200), (182, 200)], 3.0, "#A46B39"),
            LN([(80, 218), (176, 218)], 3.0, "#A46B39"),
            LN([(104, 184), (108, BOTTOM)], 2.6, "#A46B39"),
            LN([(128, 184), (128, BOTTOM)], 2.6, "#A46B39"),
            LN([(152, 184), (148, BOTTOM)], 2.6, "#A46B39"),
        ], clip=mb)
        sp.group([RR((64, 178, 192, 192), 6, "#E6B47E")], "#784421", ow=5.2)
    elif stage == 2:
        # Cute chubby sitting panda
        sp.group([
            E((82, 158, 174, 232), "#FFFFFF"),
            E((76, 172, 106, 206), dark),
            E((150, 172, 180, 206), dark),
            C(96, 224, 17, dark), C(160, 224, 17, dark),
        ], dark, ow=5.8)
        sp.detail([C(96, 224, 7, "#F9A8D4"), C(160, 224, 7, "#F9A8D4")])
        _draw_panda_head(sp, 128, 128, 0.96)
    elif stage == 3:
        # Standing curious plump panda
        sp.group([
            RR((92, 204, 118, BOTTOM), 9, dark),
            RR((138, 204, 164, BOTTOM), 9, dark),
            E((78, 134, 178, 218), "#FFFFFF"),
            RR((76, 138, 180, 168), 14, dark),
            E((64, 152, 92, 190), dark),
            E((164, 152, 192, 190), dark),
        ], dark, ow=6.0)
        _draw_panda_head(sp, 128, 104, 1.04)
    elif stage == 4:
        # Happy panda holding a bamboo shoot!
        sp.group([
            E((76, 144, 180, 234), "#FFFFFF"),
            RR((74, 148, 182, 176), 14, dark),
            C(94, 224, 18, dark), C(162, 224, 18, dark),
        ], dark, ow=6.0)
        sp.detail([C(94, 224, 7.5, "#F9A8D4"), C(162, 224, 7.5, "#F9A8D4")])
        # Bamboo shoot held in paws
        sp.group([
            LN([(156, 226), (178, 118)], 12, bam),
            PG(leaf_pts((174, 136), -25, 28, 13), bam_d),
            PG(leaf_pts((170, 154), -145, 24, 11), bam),
        ], bam_ol, ow=4.5)
        sp.group([E((76, 168, 110, 194), dark), E((142, 166, 176, 194), dark)], dark, ow=4.5)
        _draw_panda_head(sp, 124, 108, 1.06, happy=True)
    elif stage == 5:
        # Joyful Big Panda hugging a lush bundle of segmented Bamboo Stalks!
        # Lush bamboo stalks behind/beside panda
        sp.group([
            LN([(66, BOTTOM - 4), (48, 66)], 16, bam),
            LN([(86, BOTTOM - 4), (72, 76)], 14, "#A3E635"),
            PG(leaf_pts((52, 82), -145, 34, 15), bam_d),
            PG(leaf_pts((74, 92), -30, 32, 14), bam),
            PG(leaf_pts((62, 122), -150, 30, 13), bam),
        ], bam_ol, ow=5.2)
        for seg_y in (110, 150, 190):
            sp.detail([LN([(44, seg_y), (88, seg_y)], 3.0, bam_ol)])
        # Plump panda body hugging bamboo
        sp.group([
            E((84, 134, 196, 232), "#FFFFFF"),
            RR((84, 140, 196, 172), 14, dark),
            C(106, 222, 19, dark), C(174, 222, 19, dark),
            E((62, 158, 108, 188), dark),
            E((168, 164, 204, 194), dark),
        ], dark, ow=6.0)
        sp.detail([C(106, 222, 8, "#F9A8D4"), C(174, 222, 8, "#F9A8D4")])
        _draw_panda_head(sp, 140, 98, 1.12, happy=True)
        corner_sparkles(sp, [(196, 44, 13), (210, 104, 10), (46, 46, 11)])
    return sp


# --------------------------------------------------------------------------
# Themes 24 & 26: Royal White Cat (24) & Pastel Purple Slate-Grey Cat (26)
# --------------------------------------------------------------------------
def _draw_royal_cat(stage: int, *, fur: str, shade: str, ol: str,
                    glow: str, box_stage0: str, stripes: bool = False) -> Sprite:
    sp = Sprite()
    if stage == 5:
        sp.glow(128, 118, 102, glow, alpha=130, power=1.7)

    box_c, box_d, box_ol = "#C8A98E", "#A68468", "#5C4033"

    def _cat_head(s_unused, cx, cy, sc, crown=False):
        ear_l = [(cx - 30 * sc, cy - 10 * sc), (cx - 28 * sc, cy - 42 * sc), (cx - 6 * sc, cy - 26 * sc)]
        ear_r = [(cx + 6 * sc, cy - 26 * sc), (cx + 28 * sc, cy - 42 * sc), (cx + 30 * sc, cy - 10 * sc)]
        mh = sp.group([
            PG(round_poly(ear_l, 4 * sc), fur),
            PG(round_poly(ear_r, 4 * sc), fur),
            E((cx - 38 * sc, cy - 28 * sc, cx + 38 * sc, cy + 28 * sc), fur),
        ], ol, ow=5.6)
        sp.detail([
            PG(round_poly([(cx - 25 * sc, cy - 15 * sc), (cx - 23 * sc, cy - 33 * sc), (cx - 11 * sc, cy - 23 * sc)], 2 * sc), "#F9B8C6"),
            PG(round_poly([(cx + 11 * sc, cy - 23 * sc), (cx + 23 * sc, cy - 33 * sc), (cx + 25 * sc, cy - 15 * sc)], 2 * sc), "#F9B8C6"),
        ], clip=mh)
        if stripes:
            sp.detail([
                LN([(cx - 8 * sc, cy - 28 * sc), (cx - 6 * sc, cy - 16 * sc)], 3.2 * sc, shade),
                LN([(cx, cy - 30 * sc), (cx, cy - 15 * sc)], 3.4 * sc, shade),
                LN([(cx + 8 * sc, cy - 28 * sc), (cx + 6 * sc, cy - 16 * sc)], 3.2 * sc, shade),
                E((cx - 18 * sc, cy + 1 * sc, cx + 18 * sc, cy + 24 * sc), "#FFFFFF"),
            ], clip=mh)
        _kawaii_eyes(sp, cx, cy + 2 * sc, dx=14 * sc, r=4.8 * sc, eye_col=ol, blush_dx=22 * sc, smile="cat")
        # Whiskers
        sp.detail([
            LN([(cx - 34 * sc, cy + 2 * sc), (cx - 46 * sc, cy)], 2.2 * sc, ol),
            LN([(cx - 34 * sc, cy + 8 * sc), (cx - 46 * sc, cy + 10 * sc)], 2.2 * sc, ol),
            LN([(cx + 34 * sc, cy + 2 * sc), (cx + 46 * sc, cy)], 2.2 * sc, ol),
            LN([(cx + 34 * sc, cy + 8 * sc), (cx + 46 * sc, cy + 10 * sc)], 2.2 * sc, ol),
        ])
        if crown:
            _golden_crown(sp, cx, cy - 25 * sc, scale=sc * 0.95)

    if stage == 0:
        if box_stage0 == "under_box":
            # Funny white cat hiding UNDER an upside-down cardboard box (Ref 24!)
            sp.group([E((80, 174, 176, 232), fur)], ol, ow=5.6)
            _kawaii_eyes(sp, 128, 206, dx=13, r=4.4, eye_col=ol, blush_dx=21, smile="cat")
            # Tilted cardboard box resting on head!
            box_pts = [(54, 176), (82, 124), (176, 124), (202, 186), (172, 194), (84, 190)]
            mb = sp.group([PG(round_poly(box_pts, 6), box_c)], box_ol, ow=6.0)
            sp.detail([
                PG([(82, 124), (176, 124), (176, 188), (82, 188)], box_d),
                RR((116, 172, 140, 180), 3, box_ol),
            ], clip=mb)
        else:
            # Closed kraft cardboard box with cute cat sticker on front (Ref 26!)
            mb = sp.group([RR((64, 142, 192, BOTTOM), 8, box_c)], box_ol, ow=6.0)
            sp.detail([
                LN([(64, 166), (192, 166)], 3.5, box_ol),
                RR((116, 142, 140, 166), 2, "#E8D5BE"),
            ], clip=mb)
            sp.group([C(128, 202, 18, "#FFFDFB")], box_ol, ow=3.2)
            _kawaii_eyes(sp, 128, 202, dx=6.5, r=2.3, eye_col=ol, blush_dx=10, smile="cat")
    elif stage == 1:
        # Cute kitten peeking out of open cardboard box!
        _cat_head(sp, 128, 148, 0.86)
        sp.group([RR((70, 166, 186, BOTTOM), 6, box_c)], box_ol, ow=5.8)
        # Open side flaps
        sp.group([
            PG(round_poly([(70, 166), (48, 150), (62, 142), (82, 166)], 4), box_d),
            PG(round_poly([(186, 166), (208, 150), (194, 142), (174, 166)], 4), box_d),
        ], box_ol, ow=5.0)
        sp.group([C(100, 168, 9, fur), C(156, 168, 9, fur)], ol, ow=4.0)
    elif stage == 2:
        # Cute sitting kitten with curled tail
        sp.group([
            LN([(160, 224), (190, 218), (196, 196)], 11, fur),
            E((88, 156, 168, BOTTOM), fur),
            E((96, 214, 122, BOTTOM), fur), E((134, 214, 160, BOTTOM), fur),
        ], ol, ow=5.8)
        _cat_head(sp, 124, 134, 0.92)
    elif stage == 3:
        # Happy mature chubby sitting cat
        sp.group([
            LN([(164, 222), (198, 212), (204, 180)], 13, fur),
            E((80, 144, 176, BOTTOM), fur),
            E((92, 212, 122, BOTTOM), fur), E((134, 212, 164, BOTTOM), fur),
        ], ol, ow=6.0)
        _cat_head(sp, 126, 116, 1.02)
    elif stage == 4:
        # Proud tall sitting cat with heart/sparkle
        sp.group([
            LN([(166, 220), (204, 206), (208, 168)], 14, fur),
            E((76, 136, 180, BOTTOM), fur),
            E((90, 210, 122, BOTTOM), fur), E((134, 210, 166, BOTTOM), fur),
        ], ol, ow=6.0)
        _cat_head(sp, 126, 104, 1.06)
        _heart(sp, 192, 80, 11, "#F472B6", "#9D174D")
    elif stage == 5:
        # Royal Cat wearing Sparkling Golden Crown!
        sp.group([
            LN([(168, 220), (208, 202), (212, 162)], 14, fur),
            E((76, 138, 180, BOTTOM), fur),
            E((90, 210, 122, BOTTOM), fur), E((134, 210, 166, BOTTOM), fur),
        ], ol, ow=6.0)
        _cat_head(sp, 126, 108, 1.08, crown=True)
        corner_sparkles(sp, [(50, 50, 13), (206, 52, 13), (204, 124, 9)])
    return sp


def royal_cat_cash(stage: int) -> Sprite:
    return _draw_royal_cat(stage, fur="#FFFFFF", shade="#E5DDD3", ol="#4A3B32",
                           glow="#FDE68A", box_stage0="under_box", stripes=False)


def purple_cat(stage: int) -> Sprite:
    return _draw_royal_cat(stage, fur="#8D92A1", shade="#646978", ol="#3B3D47",
                           glow="#DDD6FE", box_stage0="closed_box", stripes=True)


# --------------------------------------------------------------------------
# Theme 25: ginger_kitten (Cozy Ginger Kitten in Basket -> Waving Happy Cat)
# --------------------------------------------------------------------------
def ginger_kitten(stage: int) -> Sprite:
    sp = Sprite()
    fur, belly, stripe, ol = "#F4B886", "#FFF3E4", "#C87A45", "#5C3A21"
    if stage == 5:
        sp.glow(128, 120, 102, "#FDE68A", alpha=130, power=1.7)

    def _ginger_head(s_unused, cx, cy, sc, sleepy=False):
        ear_l = [(cx - 28 * sc, cy - 10 * sc), (cx - 26 * sc, cy - 40 * sc), (cx - 6 * sc, cy - 24 * sc)]
        ear_r = [(cx + 6 * sc, cy - 24 * sc), (cx + 26 * sc, cy - 40 * sc), (cx + 28 * sc, cy - 10 * sc)]
        mh = sp.group([
            PG(round_poly(ear_l, 4 * sc), fur),
            PG(round_poly(ear_r, 4 * sc), fur),
            E((cx - 38 * sc, cy - 28 * sc, cx + 38 * sc, cy + 28 * sc), fur),
        ], ol, ow=5.6)
        sp.detail([
            PG(round_poly([(cx - 23 * sc, cy - 15 * sc), (cx - 21 * sc, cy - 32 * sc), (cx - 10 * sc, cy - 22 * sc)], 2 * sc), "#F7C6B9"),
            PG(round_poly([(cx + 10 * sc, cy - 22 * sc), (cx + 21 * sc, cy - 32 * sc), (cx + 23 * sc, cy - 15 * sc)], 2 * sc), "#F7C6B9"),
            LN([(cx - 8 * sc, cy - 28 * sc), (cx - 6 * sc, cy - 15 * sc)], 3.2 * sc, stripe),
            LN([(cx, cy - 30 * sc), (cx, cy - 14 * sc)], 3.4 * sc, stripe),
            LN([(cx + 8 * sc, cy - 28 * sc), (cx + 6 * sc, cy - 15 * sc)], 3.2 * sc, stripe),
            E((cx - 18 * sc, cy + 2 * sc, cx + 18 * sc, cy + 24 * sc), belly),
        ], clip=mh)
        if sleepy:
            _sleepy_eyes(sp, cx, cy + 4 * sc, dx=12 * sc, eye_col=ol)
        else:
            _kawaii_eyes(sp, cx, cy + 2 * sc, dx=13.5 * sc, r=4.6 * sc, eye_col=ol, blush_dx=21 * sc, smile="cat")

    def _basket():
        b_pts = [(56, 186), (200, 186), (182, BOTTOM), (74, BOTTOM)]
        mb = sp.group([PG(round_poly(b_pts, 14), "#D9A46B")], "#784821", ow=5.8)
        sp.detail([
            LN([(62, 204), (194, 204)], 3.0, "#A66E38"),
            LN([(70, 222), (186, 222)], 3.0, "#A66E38"),
        ], clip=mb)
        sp.group([RR((50, 178, 206, 192), 7, "#E8BA84")], "#784821", ow=5.2)

    if stage == 0:
        # Sleepy ginger kitten curled snugly in woven basket
        sp.group([E((76, 148, 180, 202), fur)], ol, ow=5.5)
        _ginger_head(sp, 114, 162, 0.82, sleepy=True)
        _basket()
    elif stage == 1:
        # Awake ginger kitten peeking from basket
        _ginger_head(sp, 128, 148, 0.90)
        sp.group([C(96, 178, 10, belly), C(160, 178, 10, belly)], ol, ow=4.0)
        _basket()
    elif stage == 2:
        # Sitting ginger cat
        sp.group([
            LN([(162, 222), (194, 212), (200, 184)], 12, fur),
            E((84, 152, 172, BOTTOM), fur),
            E((104, 166, 152, 222), belly),
            E((94, 214, 120, BOTTOM), belly), E((136, 214, 162, BOTTOM), belly),
        ], ol, ow=5.8)
        _ginger_head(sp, 126, 124, 0.96)
    elif stage == 3:
        # Playful stretching / pouncing kitten
        sp.group([
            LN([(176, 188), (204, 162), (198, 140)], 12, fur),
            E((86, 164, 186, 222), fur),
            E((64, 210, 106, BOTTOM), belly),
            E((148, 208, 182, BOTTOM), belly),
        ], ol, ow=5.8)
        _ginger_head(sp, 104, 142, 0.96)
    elif stage == 4:
        # Happy standing ginger cat waving one paw
        sp.group([
            LN([(164, 214), (202, 198), (206, 166)], 13, fur),
            RR((98, 206, 122, BOTTOM), 9, belly),
            RR((134, 206, 158, BOTTOM), 9, belly),
            E((82, 134, 174, 220), fur),
            E((102, 150, 154, 210), belly),
            LN([(162, 156), (194, 132)], 16, fur),
            LN([(92, 162), (76, 184)], 15, fur),
        ], ol, ow=5.8)
        _ginger_head(sp, 128, 102, 1.04)
    elif stage == 5:
        # Joyful standing Happy Ginger Cat waving BOTH paws!
        sp.group([
            LN([(166, 210), (206, 194), (210, 158)], 14, fur),
            RR((96, 204, 122, BOTTOM), 10, belly),
            RR((134, 204, 160, BOTTOM), 10, belly),
            E((80, 130, 176, 220), fur),
            E((102, 146, 154, 210), belly),
            LN([(90, 152), (58, 122)], 17, fur),
            LN([(166, 152), (198, 122)], 17, fur),
        ], ol, ow=6.0)
        _ginger_head(sp, 128, 96, 1.08)
        corner_sparkles(sp, [(48, 48, 13), (208, 48, 13), (128, 30, 10)])
    return sp


# --------------------------------------------------------------------------
# Theme 27: hatching_chick (Egg -> Cracked -> Peeking -> Bouncing Yellow Chick!)
# --------------------------------------------------------------------------
def hatching_chick(stage: int) -> Sprite:
    sp = Sprite()
    egg, egg_s, egg_ol = "#FFFDF5", "#F3E8D2", "#5C4B3B"
    ch, ch_s, ch_ol = "#FACC15", "#EAB308", "#78490E"
    beak, beak_ol = "#F97316", "#9A3412"

    if stage == 5:
        sp.glow(128, 126, 104, "#FEF08A", alpha=145, power=1.7)

    egg_pts = [
        (128, 84), (164, 104), (180, 162), (168, 218), (128, BOTTOM),
        (88, 218), (76, 162), (92, 104),
    ]

    if stage == 0:
        m = sp.group([PG(round_poly(egg_pts, 32), egg)], egg_ol, ow=6.5)
        sp.detail([
            E((94, 114, 114, 152), with_alpha("#FFFFFF", 210)),
            PG([(142, 80), (190, 80), (190, 244), (138, 244)], with_alpha(egg_s, 145)),
        ], clip=m)
    elif stage == 1:
        m = sp.group([PG(round_poly(egg_pts, 32), egg)], egg_ol, ow=6.5)
        sp.detail([PG([(142, 80), (190, 80), (190, 244), (138, 244)], with_alpha(egg_s, 140))], clip=m)
        # Zig-zag crack across middle!
        sp.detail([LN([(82, 158), (102, 144), (118, 162), (138, 142), (154, 160), (174, 146)], 5.0, egg_ol)])
    elif stage == 2:
        # Cracked egg with cute chick eyes & beak peeking out!
        m = sp.group([PG(round_poly(egg_pts, 32), egg)], egg_ol, ow=6.5)
        sp.detail([E((90, 122, 166, 174), ch)], clip=m)
        _kawaii_eyes(sp, 128, 146, dx=14, r=4.6, eye_col="#3B2314", blush_dx=23, smile="none")
        sp.group([PG([(122, 152), (134, 152), (128, 163)], beak)], beak_ol, ow=2.6)
        # Lower jagged shell rim
        shell_bot = [(76, 164), (98, 152), (116, 170), (134, 152), (154, 170), (180, 156), (170, 222), (128, BOTTOM), (86, 222)]
        sp.group([PG(shell_bot, egg)], egg_ol, ow=5.5)
    elif stage == 3:
        # Half-hatched happy yellow chick sitting inside lower shell!
        sp.group([
            C(128, 128, 46, ch),
            PG(leaf_pts((128, 84), -108, 20, 10), ch),
            PG(leaf_pts((128, 84), -72, 18, 9), ch),
        ], ch_ol, ow=6.0)
        _kawaii_eyes(sp, 128, 124, dx=16, r=5.2, eye_col="#3B2314", blush_dx=26, smile="none")
        sp.group([PG([(120, 130), (136, 130), (128, 143)], beak)], beak_ol, ow=3.0)
        shell_bot = [(72, 158), (94, 142), (112, 164), (130, 142), (150, 164), (172, 144), (184, 162), (170, 224), (128, BOTTOM), (86, 224)]
        sp.group([PG(shell_bot, egg)], egg_ol, ow=5.8)
    elif stage == 4:
        # Chick stepping out wearing tiny eggshell cap on head!
        sp.group([
            LN([(110, 212), (110, BOTTOM - 4)], 7, beak),
            LN([(146, 212), (146, BOTTOM - 4)], 7, beak),
            LN([(98, BOTTOM - 4), (120, BOTTOM - 4)], 6, beak),
            LN([(136, BOTTOM - 4), (158, BOTTOM - 4)], 6, beak),
        ], beak_ol, ow=3.5)
        sp.group([
            E((72, 102, 184, 218), ch),
            E((56, 148, 86, 184), ch_s),
            E((170, 148, 200, 184), ch_s),
        ], ch_ol, ow=6.2)
        _kawaii_eyes(sp, 128, 146, dx=18, r=5.6, eye_col="#3B2314", blush_dx=29, smile="none")
        sp.group([PG([(120, 152), (136, 152), (128, 166)], beak)], beak_ol, ow=3.2)
        # Cute eggshell hat on top!
        hat = [(88, 114), (104, 72), (128, 62), (152, 72), (168, 114), (148, 104), (128, 118), (108, 104)]
        sp.group([PG(hat, egg)], egg_ol, ow=5.2)
    elif stage == 5:
        # Bouncing Fully Hatched Fluffy Sunny Yellow Chick!
        sp.group([
            LN([(108, 206), (104, BOTTOM - 4)], 7.5, beak),
            LN([(148, 206), (152, BOTTOM - 4)], 7.5, beak),
            LN([(92, BOTTOM - 4), (116, BOTTOM - 4)], 6.5, beak),
            LN([(140, BOTTOM - 4), (164, BOTTOM - 4)], 6.5, beak),
        ], beak_ol, ow=3.8)
        m = sp.group([
            E((66, 86, 190, 212), ch),
            PG(leaf_pts((128, 90), -114, 26, 13), ch),
            PG(leaf_pts((128, 90), -90, 30, 14), ch),
            PG(leaf_pts((128, 90), -66, 24, 12), ch),
            # Happy flapping wings!
            PG(leaf_pts((74, 142), -155, 38, 22), ch),
            PG(leaf_pts((182, 142), -25, 38, 22), ch),
        ], ch_ol, ow=6.5)
        sp.detail([E((96, 164, 160, 206), with_alpha("#FEF08A", 180))], clip=m)
        _kawaii_eyes(sp, 128, 136, dx=19, r=6.0, eye_col="#3B2314", blush_dx=31, smile="none")
        sp.group([PG([(118, 142), (138, 142), (128, 158)], beak)], beak_ol, ow=3.4)
        corner_sparkles(sp, [(46, 54, 13), (210, 54, 14), (206, 124, 9)])
    return sp


# --------------------------------------------------------------------------
# Theme 28: candy_jar (Cotton Candy Pastel Glass Jar -> Overflowing Sweets!)
# --------------------------------------------------------------------------
def _wrapped_candy(sp: Sprite, cx: float, cy: float, ang: float, fill: str, ol: str):
    a = math.radians(ang)
    dx, dy = math.cos(a) * 14, math.sin(a) * 14
    sp.group([
        PG([(cx - dx, cy - dy), (cx - dx - dy * 0.55, cy - dy + dx * 0.55),
            (cx - dx * 1.65, cy - dy * 1.65)], fill),
        PG([(cx + dx, cy + dy), (cx + dx + dy * 0.55, cy + dy - dx * 0.55),
            (cx + dx * 1.65, cy + dy * 1.65)], fill),
        C(cx, cy, 11, fill),
    ], ol, ow=3.0)
    sp.detail([C(cx - 3, cy - 3, 3.2, with_alpha("#FFFFFF", 160))])


def _lollipop(sp: Sprite, cx: float, cy: float, r: float, fill: str, swirl: str, ol: str, stick_bot: float):
    sp.group([LN([(cx, cy + r * 0.6), (cx, stick_bot)], 4.5, "#FFFFFF")], "#94A3B8", ow=2.0)
    m = sp.group([C(cx, cy, r, fill)], ol, ow=3.8)
    sp.detail([
        ARC((cx - r * 0.65, cy - r * 0.65, cx + r * 0.65, cy + r * 0.65), 0, 270, 3.6, swirl),
        ARC((cx - r * 0.3, cy - r * 0.3, cx + r * 0.3, cy + r * 0.3), 120, 360, 3.0, "#FFFFFF"),
    ], clip=m)


def candy_jar(stage: int) -> Sprite:
    sp = Sprite()
    jar_ol, rim_c = "#EC4899", "#F472B6"
    if stage == 5:
        sp.glow(128, 120, 108, "#FBCFE8", alpha=140, power=1.7)

    # Glass jar body background
    sp.group([
        RR((68, 94, 188, BOTTOM), 24, "#FFFDFE"),
        RR((84, 76, 172, 98), 8, "#FFFDFE"),
    ], jar_ol, ow=5.8)

    # Fill candies progressively inside jar!
    if stage >= 1:
        _wrapped_candy(sp, 96, 214, -18, "#F9A8D4", "#BE185D")
        _wrapped_candy(sp, 128, 218, 12, "#93C5FD", "#2563EB")
        _wrapped_candy(sp, 160, 212, -10, "#DDD6FE", "#7C3AED")
    if stage >= 2:
        _lollipop(sp, 108, 166, 15, "#60A5FA", "#DBEAFE", "#2563EB", 216)
        _lollipop(sp, 148, 164, 15, "#F472B6", "#FCE7F3", "#BE185D", 216)
        _wrapped_candy(sp, 110, 194, 20, "#FBCFE8", "#DB2777")
        _wrapped_candy(sp, 148, 194, -22, "#BAE6FD", "#0284C7")
    if stage >= 3:
        _wrapped_candy(sp, 92, 174, -25, "#FDE68A", "#D97706")
        _wrapped_candy(sp, 128, 176, 8, "#C4B5FD", "#6D28D9")
        _wrapped_candy(sp, 164, 174, 18, "#F9A8D4", "#BE185D")
    if stage >= 4:
        _lollipop(sp, 94, 134, 16, "#EC4899", "#FBCFE8", "#9D174D", 190)
        _lollipop(sp, 162, 134, 16, "#38BDF8", "#E0F2FE", "#0369A1", 190)
        _wrapped_candy(sp, 128, 152, -12, "#F9A8D4", "#BE185D")
    if stage >= 5:
        # Overflowing giant pastel swirl lollipops popping right above the jar rim!
        _lollipop(sp, 128, 72, 24, "#F472B6", "#93C5FD", "#9D174D", 162)
        _lollipop(sp, 86, 98, 18, "#38BDF8", "#FBCFE8", "#0284C7", 172)
        _lollipop(sp, 170, 98, 18, "#C084FC", "#FEF08A", "#7E22CE", 172)
        _wrapped_candy(sp, 114, 128, 15, "#FDE047", "#CA8A04")
        _wrapped_candy(sp, 144, 126, -18, "#93C5FD", "#1D4ED8")

    # Jar rim & glossy glass specular highlight on top
    sp.group([RR((78, 74, 178, 90), 7, with_alpha("#FBCFE8", 215))], jar_ol, ow=4.8)
    sp.detail([
        RR((78, 108, 90, 212), 6, with_alpha("#FFFFFF", 135)),
        RR((84, 78, 126, 84), 3, with_alpha("#FFFFFF", 165)),
    ])
    if stage == 5:
        corner_sparkles(sp, [(46, 50, 13), (210, 50, 13), (206, 136, 9)])
    return sp


# --------------------------------------------------------------------------
# Theme 29: rose_bouquet (Watercolor Romantic Blush Pink Rose)
# --------------------------------------------------------------------------
def rose_bouquet(stage: int) -> Sprite:
    sp = Sprite()
    stem_c, leaf_c, green_ol = "#6E8F64", "#89AB7E", "#425C3B"
    p_pale, p_mid, p_deep, p_ol = "#FCE7F0", "#E8A6BD", "#C66D8B", "#7A374E"

    if stage == 5:
        sp.glow(128, 90, 100, "#F8D7E3", alpha=145, power=1.7)

    # Graceful botanical stem & leaves
    stem_top = {0: 158, 1: 142, 2: 126, 3: 112, 4: 102, 5: 106}[stage]
    leaves = []
    if stage >= 1:
        leaves.append(((128, 198), -146, 34, 17))
    if stage >= 2:
        leaves.append(((128, 188), -34, 34, 17))
    if stage >= 3:
        leaves.extend([((128, 160), -142, 38, 19), ((128, 154), -38, 38, 19)])
    sp.group([LN([(128, BOTTOM - 4), (126, (BOTTOM + stem_top) * 0.5), (128, stem_top)], 7.5, stem_c)]
             + [PG(leaf_pts(b, a, ln, wd), leaf_c) for (b, a, ln, wd) in leaves], green_ol, ow=5.2)

    if stage == 0:
        # Closed botanical green sepal bud
        sp.group([PG(leaf_pts((128, 166), -90, 48, 28, sharp=0.65), leaf_c)], green_ol, ow=5.2)
    elif stage == 1:
        # Bud showing first blush pink tip!
        sp.group([PG(leaf_pts((128, 148), -90, 52, 30, sharp=0.65), p_mid)], p_ol, ow=5.2)
        sp.group([
            PG(leaf_pts((128, 152), -112, 32, 14), leaf_c),
            PG(leaf_pts((128, 152), -68, 32, 14), leaf_c),
        ], green_ol, ow=4.0)
    elif stage == 2:
        # Half-opened spiral pink rose
        cy = 108.0
        sp.group([
            PG(round_petal_pts((128, cy + 16), -114, 46, 28), p_pale),
            PG(round_petal_pts((128, cy + 16), -66, 46, 28), p_mid),
            PG(round_petal_pts((128, cy + 16), -90, 50, 30), p_mid),
        ], p_ol, ow=5.2)
        sp.detail([ARC((116, cy - 22, 140, cy + 2), 10, 260, 3.2, p_deep)])
    elif stage == 3:
        # Blooming lush blush rose
        cy = 96.0
        outer = [PG(round_petal_pts((128, cy), -90 + i * 60, 40, 32), p_pale if i % 2 else p_mid) for i in range(6)]
        sp.group(outer, p_ol, ow=5.5)
        sp.group([C(128, cy, 18, p_mid)], p_ol, ow=3.8)
        sp.detail([ARC((114, cy - 14, 142, cy + 14), 20, 270, 3.4, p_deep)])
    elif stage == 4:
        # Full romantic layered rose
        cy = 88.0
        outer = [PG(round_petal_pts((128, cy), -90 + i * (360 / 7), 48, 38), p_pale if i % 2 else p_mid) for i in range(7)]
        sp.group(outer, p_ol, ow=5.8)
        mid = [PG(round_petal_pts((128, cy), -50 + i * 72, 32, 26), p_mid if i % 2 == 0 else p_deep) for i in range(5)]
        sp.group(mid, p_ol, ow=4.0)
        sp.detail([ARC((114, cy - 14, 142, cy + 14), 0, 270, 3.5, "#FFF0F6")])
    elif stage == 5:
        # Lush Full-Bloom Watercolor Pink Rose Bouquet (center + 2 side buds!)
        sp.group([
            LN([(128, 174), (84, 120)], 6.0, stem_c),
            LN([(128, 174), (172, 120)], 6.0, stem_c),
            PG(leaf_pts((86, 126), -145, 34, 18), leaf_c),
            PG(leaf_pts((170, 126), -35, 34, 18), leaf_c),
        ], green_ol, ow=4.8)
        # Side mini roses
        for sx, sy in ((80, 110), (176, 110)):
            sp.group([PG(round_petal_pts((sx, sy), -90 + i * 72, 24, 19), p_mid if i % 2 else p_pale) for i in range(5)], p_ol, ow=4.2)
            sp.group([C(sx, sy, 10, p_deep)], p_ol, ow=2.8)
        # Hero centerpiece romantic blush rose
        cy = 76.0
        sp.group([PG(round_petal_pts((128, cy), -90 + i * (360 / 7), 50, 40), p_pale if i % 2 else p_mid) for i in range(7)], p_ol, ow=6.0)
        sp.group([PG(round_petal_pts((128, cy - 2), -60 + i * 72, 33, 27), p_mid if i % 2 == 0 else p_deep) for i in range(5)], p_ol, ow=4.0)
        sp.group([C(128, cy - 2, 15, p_deep)], p_ol, ow=3.2)
        sp.detail([
            ARC((116, cy - 14, 140, cy + 10), 20, 260, 3.2, p_pale),
            ARC((121, cy - 9, 135, cy + 5), 140, 360, 2.8, "#FFFFFF"),
        ])
        corner_sparkles(sp, [(48, 44, 12), (208, 44, 12)])
    return sp


# --------------------------------------------------------------------------
# Theme 30: shiba_inu (Super-Cute Chibi Shiba Inu w/ Red Japanese Bandana!)
# --------------------------------------------------------------------------
def _draw_shiba_head(sp: Sprite, cx: float, cy: float, sc: float,
                     tilt_deg: float = 0.0, sleepy: bool = False,
                     open_mouth: bool = False, crown: bool = False):
    coat, cream, ol = "#E89B54", "#FFF8EE", "#4A2C1A"
    # Iconic pointed Shiba ears
    ear_l = [(cx - 32 * sc, cy - 8 * sc), (cx - 30 * sc, cy - 46 * sc), (cx - 8 * sc, cy - 26 * sc)]
    ear_r = [(cx + 8 * sc, cy - 26 * sc), (cx + 30 * sc, cy - 46 * sc), (cx + 32 * sc, cy - 8 * sc)]
    mh = sp.group([
        PG(round_poly(ear_l, 5 * sc), coat),
        PG(round_poly(ear_r, 5 * sc), coat),
        E((cx - 42 * sc, cy - 30 * sc, cx + 42 * sc, cy + 32 * sc), coat),
    ], ol, ow=5.8)
    # Signature Shiba cream urajiro cheeks/muzzle + cream eyebrow dots + ear cream!
    sp.detail([
        PG(round_poly([(cx - 26 * sc, cy - 14 * sc), (cx - 25 * sc, cy - 36 * sc), (cx - 12 * sc, cy - 22 * sc)], 2.5 * sc), cream),
        PG(round_poly([(cx + 12 * sc, cy - 22 * sc), (cx + 25 * sc, cy - 36 * sc), (cx + 26 * sc, cy - 14 * sc)], 2.5 * sc), cream),
        # Plush white cheeks & muzzle
        E((cx - 38 * sc, cy - 2 * sc, cx - 2 * sc, cy + 34 * sc), cream),
        E((cx + 2 * sc, cy - 2 * sc, cx + 38 * sc, cy + 34 * sc), cream),
        E((cx - 20 * sc, cy - 4 * sc, cx + 20 * sc, cy + 32 * sc), cream),
        # Cute little cream Shiba eyebrow dots (maro!)
        E((cx - 18 * sc, cy - 18 * sc, cx - 9 * sc, cy - 11 * sc), cream),
        E((cx + 9 * sc, cy - 18 * sc, cx + 18 * sc, cy - 11 * sc), cream),
    ], clip=mh)
    if sleepy:
        _sleepy_eyes(sp, cx, cy + 2 * sc, dx=14 * sc, eye_col=ol)
    else:
        _kawaii_eyes(sp, cx, cy + 1 * sc, dx=15 * sc, r=5.0 * sc, eye_col=ol,
                     blush_dx=24 * sc, smile=("happy_open" if open_mouth else "dog"))
    if crown:
        _golden_crown(sp, cx, cy - 26 * sc, scale=sc * 0.92)


def shiba_inu(stage: int) -> Sprite:
    sp = Sprite()
    coat, cream, ol = "#E89B54", "#FFF8EE", "#4A2C1A"
    bandana, band_ol = "#D94F4F", "#881337"

    if stage == 5:
        sp.glow(128, 120, 108, "#FDE68A", alpha=140, power=1.7)

    if stage == 0:
        # Cozy plush red Japanese paw-print dog bed
        mb = sp.group([E((42, 168, 214, BOTTOM), bandana)], band_ol, ow=6.0)
        sp.detail([E((64, 180, 192, 224), "#FEF3C7")], clip=mb)
        # Cute paw print on cushion
        sp.detail([
            E((116, 198, 140, 216), "#E89B54"),
            C(112, 192, 4.5, "#E89B54"), C(123, 188, 4.5, "#E89B54"),
            C(134, 188, 4.5, "#E89B54"), C(144, 192, 4.5, "#E89B54"),
        ])
    elif stage == 1:
        # Tiny sleepy Shiba pup curled peacefully on red dog bed!
        mb = sp.group([E((46, 174, 210, BOTTOM), bandana)], band_ol, ow=5.8)
        sp.detail([E((66, 184, 190, 224), "#FEF3C7")], clip=mb)
        sp.group([E((80, 152, 178, 214), coat), C(164, 178, 15, coat)], ol, ow=5.5)
        _draw_shiba_head(sp, 114, 168, 0.80, sleepy=True)
    elif stage == 2:
        # Curious sitting baby Shiba
        sp.group([
            C(164, 196, 16, coat),
            E((86, 150, 170, BOTTOM), coat),
            E((102, 164, 154, 224), cream),
            E((94, 214, 120, BOTTOM), cream), E((136, 214, 162, BOTTOM), cream),
        ], ol, ow=5.8)
        _draw_shiba_head(sp, 126, 124, 0.94)
    elif stage == 3:
        # Happy Shiba puppy wagging curly donut tail + Red Japanese Bandana!
        sp.group([
            C(176, 186, 19, coat), C(176, 186, 8, cream),
            E((80, 144, 176, BOTTOM), coat),
            E((98, 158, 158, 224), cream),
            E((92, 212, 120, BOTTOM), cream), E((136, 212, 164, BOTTOM), cream),
        ], ol, ow=6.0)
        # Red bandana scarf around neck!
        sp.group([PG(round_poly([(94, 148), (162, 148), (128, 182)], 6), bandana)], band_ol, ow=4.5)
        sp.detail([C(128, 162, 3.5, "#FEF08A"), C(116, 155, 2.5, "#FEF08A"), C(140, 155, 2.5, "#FEF08A")])
        _draw_shiba_head(sp, 128, 112, 1.02)
    elif stage == 4:
        # Energetic leaping happy Shiba with red bandana & hearts!
        sp.group([
            C(182, 174, 20, coat), C(182, 174, 8, cream),
            E((78, 138, 178, 222), coat),
            E((98, 154, 158, 214), cream),
            LN([(92, 164), (62, 140)], 16, coat),
            LN([(164, 164), (194, 140)], 16, coat),
            RR((94, 206, 120, BOTTOM - 2), 9, cream),
            RR((136, 206, 162, BOTTOM - 2), 9, cream),
        ], ol, ow=6.0)
        sp.group([PG(round_poly([(92, 144), (164, 144), (128, 180)], 6), bandana)], band_ol, ow=4.5)
        _draw_shiba_head(sp, 128, 102, 1.06, open_mouth=True)
        _heart(sp, 58, 72, 11, "#F472B6", "#9D174D")
        _heart(sp, 200, 68, 12, "#F472B6", "#9D174D")
    elif stage == 5:
        # Radiant Smiling Fluffy Shiba Inu w/ Red Japanese Bandana + Golden Crown + Sakura!
        sp.group([
            C(184, 180, 22, coat), C(184, 180, 9, cream),
            E((76, 136, 180, BOTTOM), coat),
            E((98, 152, 158, 224), cream),
            LN([(86, 158), (56, 132)], 17, coat),
            LN([(170, 158), (200, 132)], 17, coat),
            E((90, 212, 122, BOTTOM), cream), E((134, 212, 166, BOTTOM), cream),
        ], ol, ow=6.2)
        sp.group([PG(round_poly([(90, 142), (166, 142), (128, 182)], 7), bandana)], band_ol, ow=4.8)
        sp.detail([
            C(128, 160, 4.0, "#FEF08A"), C(114, 152, 3.0, "#FEF08A"), C(142, 152, 3.0, "#FEF08A"),
        ])
        _draw_shiba_head(sp, 128, 104, 1.08, open_mouth=True, crown=True)
        # Floating sakura petals & golden sparkles!
        sp.group([PG(leaf_pts((48, 84), -35, 18, 11), "#FBCFE8")], "#DB2777", ow=2.6)
        sp.group([PG(leaf_pts((208, 92), -145, 18, 11), "#FBCFE8")], "#DB2777", ow=2.6)
        corner_sparkles(sp, [(52, 46, 13), (206, 46, 13)])
    return sp


# --------------------------------------------------------------------------
# Theme 31: akita_inu (Super-Cute Fluffy Winter Chibi Akita Inu!)
# --------------------------------------------------------------------------
def _draw_akita_head(sp: Sprite, cx: float, cy: float, sc: float, open_mouth: bool = False):
    """Distinctly FLUFFIER, wider plush-cheeked Akita Inu head in warm pale apricot + snow white!"""
    coat, white, ol = "#E6B88A", "#FFFFFF", "#2C3545"
    # Slightly thicker rounded forward-leaning Akita ears
    ear_l = [(cx - 32 * sc, cy - 10 * sc), (cx - 32 * sc, cy - 42 * sc), (cx - 8 * sc, cy - 26 * sc)]
    ear_r = [(cx + 8 * sc, cy - 26 * sc), (cx + 32 * sc, cy - 42 * sc), (cx + 32 * sc, cy - 10 * sc)]
    mh = sp.group([
        PG(round_poly(ear_l, 7 * sc), coat),
        PG(round_poly(ear_r, 7 * sc), coat),
        # Extra-wide fluffy Akita cheeks!
        E((cx - 46 * sc, cy - 28 * sc, cx + 46 * sc, cy + 32 * sc), coat),
        C(cx - 34 * sc, cy + 12 * sc, 20 * sc, white),
        C(cx + 34 * sc, cy + 12 * sc, 20 * sc, white),
    ], ol, ow=5.8)
    sp.detail([
        PG(round_poly([(cx - 26 * sc, cy - 15 * sc), (cx - 26 * sc, cy - 33 * sc), (cx - 13 * sc, cy - 23 * sc)], 3 * sc), "#F6D5C8"),
        PG(round_poly([(cx + 13 * sc, cy - 23 * sc), (cx + 26 * sc, cy - 33 * sc), (cx + 26 * sc, cy - 15 * sc)], 3 * sc), "#F6D5C8"),
        # Wide snow-white plush cheeks & muzzle mask
        E((cx - 46 * sc, cy - 2 * sc, cx + 46 * sc, cy + 36 * sc), white),
        E((cx - 22 * sc, cy - 8 * sc, cx + 22 * sc, cy + 34 * sc), white),
        # Soft forehead widow's peak in apricot
        PG([(cx - 14 * sc, cy - 26 * sc), (cx + 14 * sc, cy - 26 * sc), (cx, cy - 6 * sc)], coat),
    ], clip=mh)
    _kawaii_eyes(sp, cx, cy + 1 * sc, dx=15.5 * sc, r=5.0 * sc, eye_col=ol,
                 blush_dx=26 * sc, smile=("happy_open" if open_mouth else "dog"))


def akita_inu(stage: int) -> Sprite:
    sp = Sprite()
    coat, white, ol = "#E6B88A", "#FFFFFF", "#2C3545"
    indigo, ind_ol = "#3B5998", "#1E3A5F"
    gold, gold_ol = "#F59E0B", "#92400E"

    if stage == 5:
        sp.glow(128, 118, 108, "#CFE3F5", alpha=145, power=1.7)

    if stage == 0:
        # Cozy Japanese Indigo-bordered Tatami Cushion (Zabuton) w/ paw print & tassels!
        mc = sp.group([RR((44, 174, 212, BOTTOM), 16, "#DCECD8")], ind_ol, ow=6.0)
        sp.detail([
            RR((44, 174, 212, 190), 4, indigo),
            RR((44, BOTTOM - 16, 212, BOTTOM), 4, indigo),
        ], clip=mc)
        # Cute corner red tassels & center paw print
        sp.group([C(46, 206, 7, "#DC2626"), C(210, 206, 7, "#DC2626")], "#7F1D1D", ow=3.0)
        sp.detail([
            E((116, 200, 140, 218), indigo),
            C(112, 195, 4.2, indigo), C(123, 191, 4.2, indigo),
            C(134, 191, 4.2, indigo), C(144, 195, 4.2, indigo),
        ])
    elif stage == 1:
        # Fluffy snowball Akita pup peeking over tatami cushion!
        _draw_akita_head(sp, 128, 152, 0.84)
        sp.group([C(96, 178, 11, white), C(160, 178, 11, white)], ol, ow=4.2)
        mc = sp.group([RR((50, 180, 206, BOTTOM), 14, "#DCECD8")], ind_ol, ow=5.8)
        sp.detail([RR((50, 180, 206, 194), 4, indigo)], clip=mc)
    elif stage == 2:
        # Plump sitting baby Akita with extra-fluffy chest
        sp.group([
            C(170, 194, 18, white),
            E((82, 148, 174, BOTTOM), coat),
            E((96, 158, 160, 226), white),
            E((92, 214, 120, BOTTOM), white), E((136, 214, 164, BOTTOM), white),
        ], ol, ow=5.8)
        _draw_akita_head(sp, 128, 122, 0.94)
    elif stage == 3:
        # Loyal smiling fluffy Akita wearing Indigo & Gold collar w/ bell!
        sp.group([
            C(178, 182, 21, white), C(178, 182, 11, coat),
            E((76, 142, 180, BOTTOM), coat),
            E((92, 154, 164, 226), white),
            E((90, 212, 120, BOTTOM), white), E((136, 212, 166, BOTTOM), white),
        ], ol, ow=6.0)
        sp.group([RR((92, 144, 164, 158), 7, indigo)], ind_ol, ow=4.2)
        sp.group([C(128, 164, 9.5, gold)], gold_ol, ow=3.2)
        sp.detail([LN([(122, 164), (134, 164)], 2.4, gold_ol)])
        _draw_akita_head(sp, 128, 110, 1.02)
    elif stage == 4:
        # Proud standing fluffy Akita w/ falling winter snow & cherry petals!
        sp.group([
            C(186, 174, 23, white), C(186, 174, 11, coat),
            E((74, 134, 182, 224), coat),
            E((90, 148, 166, 216), white),
            RR((92, 206, 120, BOTTOM), 9, white),
            RR((136, 206, 164, BOTTOM), 9, white),
        ], ol, ow=6.0)
        sp.group([RR((90, 140, 166, 155), 7, indigo)], ind_ol, ow=4.2)
        sp.group([C(128, 160, 10, gold)], gold_ol, ow=3.2)
        _draw_akita_head(sp, 128, 102, 1.06)
        # Soft falling winter snowflakes!
        for (sx, sy, sr) in [(54, 62, 8), (204, 68, 9), (56, 134, 6)]:
            sp.group([C(sx, sy, sr, "#E0F2FE")], "#60A5FA", ow=2.5)
    elif stage == 5:
        # Majestic Fluffy Smiling Akita Inu w/ Red-and-Gold Braided Collar (Shimenawa) + Bell + Winter Blossoms!
        sp.group([
            C(190, 174, 26, white), C(190, 174, 13, coat),
            E((70, 132, 186, BOTTOM), coat),
            E((86, 144, 170, 226), white),
            C(94, 162, 18, white), C(162, 162, 18, white),
            E((88, 212, 122, BOTTOM), white), E((134, 212, 168, BOTTOM), white),
        ], ol, ow=6.2)
        # Signature Red-and-Gold Braided Japanese Collar (Shimenawa beads) + Golden Bell!
        beads = []
        for i, bx in enumerate(range(92, 165, 14)):
            beads.append(C(bx, 146 + (4 if i in (2, 3) else 0), 9.5, "#DC2626" if i % 2 == 0 else "#F59E0B"))
        sp.group(beads, "#7F1D1D", ow=3.8)
        sp.group([C(128, 164, 12, "#FACC15")], gold_ol, ow=3.6)
        sp.detail([C(125, 160, 3.2, "#FEF9C3"), LN([(121, 166), (135, 166)], 2.6, gold_ol)])
        _draw_akita_head(sp, 128, 100, 1.10, open_mouth=True)
        # Sparkling winter blossoms & snowflakes!
        for (sx, sy) in ((50, 58), (206, 56)):
            sp.group([PG(round_petal_pts((sx, sy), -90 + i * 72, 12, 9), "#FBCFE8") for i in range(5)], "#DB2777", ow=2.6)
            sp.detail([C(sx, sy, 3.5, "#FEF08A")])
        corner_sparkles(sp, [(44, 118, 10), (212, 114, 11), (128, 28, 11)])
    return sp


BATCH3_THEMES = {
    "alpaca_cream": alpaca_cream,
    "alpaca_blush": alpaca_blush,
    "alpaca_matcha": alpaca_matcha,
    "bamboo_panda": bamboo_panda,
    "royal_cat_cash": royal_cat_cash,
    "ginger_kitten": ginger_kitten,
    "purple_cat": purple_cat,
    "hatching_chick": hatching_chick,
    "candy_jar": candy_jar,
    "rose_bouquet": rose_bouquet,
    "shiba_inu": shiba_inu,
    "akita_inu": akita_inu,
}


def main():
    only = sys.argv[1:] or None
    results = {}
    for slug, fn in BATCH3_THEMES.items():
        if only and slug not in only:
            continue
        ims = []
        for stage in range(6):
            out = ASSETS_DIR / slug / f"stage_{stage}.png"
            ims.append(fn(stage).save(out))
            print(f"  {out.relative_to(ROOT)}  {out.stat().st_size / 1024:.1f} KB", flush=True)
        results[slug] = ims
    if not only:
        sheet_path = PREVIEW_DIR / "assets_contact_sheet_batch3.png"
        build_contact_sheet(results, sheet_path)
        print(f"Contact sheet: {sheet_path.relative_to(ROOT)}", flush=True)


if __name__ == "__main__":
    main()
