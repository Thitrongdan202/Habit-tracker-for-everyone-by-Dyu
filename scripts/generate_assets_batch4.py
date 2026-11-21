"""
generate_assets_batch4.py
=========================
Generates 4 brand-new adorable high-DPI (300x300px, 4x supersampled) transparent PNG
6-stage sprite sets (24 PNGs) for Habit Tracker v3.5 Templates 32..35 + contact sheet:

  32. sakura_tree      (Seed -> Sprout -> Branch -> Leafy Green Tree -> Budding -> Full Blooming Sakura Tree!)
  33. mochi_cat        (Closed Orange Box -> Peeking Ears -> Paws on Box -> Climbing Out -> Sitting -> Radiant Mochi Cat!)
  34. fluffy_bunny     (Curled Sleepy Baby Bunny -> Peeking -> Sitting -> Perked -> Smiling -> Cherry-Ribbon Bunny!)
  35. milk_mocha_bear  (Heart Sprout & Can -> Sleepy Milk -> Mocha Bear -> Together -> Watering Pot -> Hugging Bears!)

Output:
  assets/<slug>/stage_0.png .. stage_5.png  (24 PNGs)
  previews/assets_contact_sheet_batch4.png
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


def _heart_pts(cx: float, cy: float, r: float):
    pts = []
    for k in range(32):
        t = 2 * math.pi * k / 32.0
        x = 16 * (math.sin(t) ** 3)
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((cx + x * r / 16.0, cy + y * r / 16.0))
    return pts


def _sakura_blossom(sp: Sprite, cx: float, cy: float, r: float, petal="#FCE7F3", center="#EC4899"):
    sp.group([PG(round_petal_pts((cx, cy), -90 + k * 72, r, r * 0.72), petal) for k in range(5)],
             "#D87A9E", ow=2.2)
    sp.detail([C(cx, cy, r * 0.28, center)])


# ==========================================================================
#  32. SAKURA TREE (Minimalist Pink Cherry Blossom Tree Growth)
# ==========================================================================
def sakura_tree(stage: int) -> Sprite:
    sp = Sprite()
    bark = "#6B4F4B"
    bark_dk = "#4A3330"
    leaf_g = "#6FB85E"
    leaf_lt = "#9AD684"
    leaf_dk = "#4C8C42"
    pink1 = "#FAD2E1"
    pink2 = "#F4A5C2"
    pink3 = "#FCE7F3"
    ink = "#4A3236"

    if stage == 5:
        sp.glow(128, 124, 108, "#FCE7F3", alpha=145, power=1.6)
    sp.detail([E((128 - (38 + stage * 8), BOTTOM - 10, 128 + (38 + stage * 8), BOTTOM + 4), with_alpha(ink, 35))])

    if stage == 0:
        # Plump brown cherry seed resting gently
        sp.group([
            E((102, BOTTOM - 42, 154, BOTTOM - 4), bark),
        ], ink, ow=5.8)
        sp.detail([
            E((110, BOTTOM - 35, 134, BOTTOM - 21), with_alpha("#FFFFFF", 95)),
            ARC((112, BOTTOM - 36, 146, BOTTOM - 10), 215, 325, 3.0, bark_dk),
        ])
    elif stage == 1:
        # Sprouting seed + fresh curly green stem & twin leaves
        sp.group([E((96, BOTTOM - 36, 138, BOTTOM - 4), bark)], ink, ow=5.2)
        stem = quad((122, BOTTOM - 26), (144, BOTTOM - 64), (132, BOTTOM - 104), 16)
        sp.group([
            LN(stem, 8.0, leaf_dk),
            PG(leaf_pts((132, BOTTOM - 100), -138, 42, 24), leaf_g),
            PG(leaf_pts((132, BOTTOM - 100), -36, 44, 24), leaf_lt),
        ], ink, ow=4.8)
        sp.detail([
            LN(stem, 4.0, leaf_g),
            LN([(130, BOTTOM - 99), (110, BOTTOM - 115)], 2.2, leaf_dk),
            LN([(134, BOTTOM - 99), (154, BOTTOM - 111)], 2.2, leaf_dk),
        ])
    elif stage == 2:
        # Graceful bare young sapling with forks & baby leaf clusters
        trunk = [(117, BOTTOM - 4), (122, BOTTOM - 56), (124, BOTTOM - 102),
                 (132, BOTTOM - 102), (134, BOTTOM - 56), (140, BOTTOM - 4)]
        b_l = quad((125, BOTTOM - 74), (105, BOTTOM - 104), (88, BOTTOM - 124), 12)
        b_r = quad((131, BOTTOM - 82), (151, BOTTOM - 106), (168, BOTTOM - 122), 12)
        b_t = quad((128, BOTTOM - 98), (130, BOTTOM - 128), (128, BOTTOM - 148), 10)
        sp.group([PG(trunk, bark), LN(b_l, 8.0, bark), LN(b_r, 7.5, bark), LN(b_t, 6.5, bark)], ink, ow=4.8)
        tips = [(86, BOTTOM - 126, -140), (170, BOTTOM - 124, -40), (128, BOTTOM - 150, -90),
                (104, BOTTOM - 108, -160), (152, BOTTOM - 110, -25)]
        sp.group([PG(leaf_pts((x, y), ang, 30, 18), leaf_g if i % 2 == 0 else leaf_lt)
                  for i, (x, y, ang) in enumerate(tips)], ink, ow=4.0)
        sp.detail([LN([(127, BOTTOM - 12), (128, BOTTOM - 94)], 2.8, bark_dk)])
    elif stage == 3:
        # Full leafy green tree
        trunk = [(112, BOTTOM - 4), (120, BOTTOM - 52), (121, BOTTOM - 112),
                 (135, BOTTOM - 112), (136, BOTTOM - 52), (144, BOTTOM - 4)]
        sp.group([
            PG(trunk, bark),
            LN([(123, BOTTOM - 88), (96, BOTTOM - 122)], 9.0, bark),
            LN([(133, BOTTOM - 90), (160, BOTTOM - 122)], 9.0, bark),
        ], ink, ow=4.8)
        puffs = [
            (128, 108, 46, leaf_g), (88, 122, 34, leaf_dk), (168, 122, 34, leaf_dk),
            (100, 86, 33, leaf_g), (156, 86, 33, leaf_g), (128, 72, 37, leaf_lt),
            (110, 122, 30, leaf_lt), (148, 122, 30, leaf_g),
        ]
        sp.group([C(x, y, r, col) for x, y, r, col in puffs], ink, ow=5.0)
        sp.detail([
            C(122, 66, 15, with_alpha("#D9F99D", 145)),
            C(98, 88, 13, with_alpha("#D9F99D", 115)),
            LN([(125, BOTTOM - 14), (126, BOTTOM - 98)], 3.0, bark_dk),
        ])
    elif stage == 4:
        # Budding pink-green cherry blossom tree
        trunk = [(110, BOTTOM - 4), (118, BOTTOM - 54), (120, BOTTOM - 114),
                 (136, BOTTOM - 114), (138, BOTTOM - 54), (146, BOTTOM - 4)]
        sp.group([
            PG(trunk, bark),
            LN([(122, BOTTOM - 90), (94, BOTTOM - 126)], 9.5, bark),
            LN([(134, BOTTOM - 92), (162, BOTTOM - 126)], 9.5, bark),
        ], ink, ow=4.8)
        puffs = [
            (128, 106, 48, leaf_g), (86, 122, 35, leaf_dk), (170, 122, 35, leaf_dk),
            (98, 84, 34, pink1), (158, 84, 34, pink1), (128, 70, 38, pink2),
            (108, 120, 30, leaf_lt), (150, 120, 30, pink1),
        ]
        sp.group([C(x, y, r, col) for x, y, r, col in puffs], ink, ow=5.0)
        for bx, by in [(98, 84), (128, 66), (158, 86), (114, 108), (144, 112), (86, 116)]:
            _sakura_blossom(sp, bx, by, 10.5)
        sp.detail([LN([(126, BOTTOM - 14), (127, BOTTOM - 100)], 3.0, bark_dk)])
    else:
        # Stage 5: FULL BLOOMING PINK CHERRY BLOSSOM TREE + falling petals & sparkles!
        trunk = [(106, BOTTOM - 4), (117, BOTTOM - 56), (119, BOTTOM - 116),
                 (137, BOTTOM - 116), (139, BOTTOM - 56), (150, BOTTOM - 4)]
        sp.group([
            PG(trunk, bark),
            LN([(121, BOTTOM - 92), (88, BOTTOM - 130)], 10.0, bark),
            LN([(135, BOTTOM - 94), (168, BOTTOM - 130)], 10.0, bark),
            LN([(128, BOTTOM - 108), (128, BOTTOM - 142)], 8.0, bark),
        ], ink, ow=4.8)
        puffs = [
            (128, 104, 54, pink1), (78, 118, 38, pink2), (178, 118, 38, pink2),
            (92, 78, 38, pink1), (164, 78, 38, pink1), (128, 60, 42, pink3),
            (106, 122, 33, pink2), (152, 122, 33, pink2), (128, 92, 35, pink3),
        ]
        sp.group([C(x, y, r, col) for x, y, r, col in puffs], ink, ow=5.2)
        sp.detail([
            C(124, 54, 18, with_alpha("#FFFFFF", 160)),
            LN([(124, BOTTOM - 12), (126, BOTTOM - 104)], 3.2, bark_dk),
            LN([(133, BOTTOM - 16), (132, BOTTOM - 88)], 2.4, bark_dk),
        ])
        for bx, by, br in [
            (94, 76, 11), (128, 56, 13), (162, 78, 11), (78, 114, 10),
            (112, 98, 11), (144, 98, 11), (178, 114, 10), (128, 120, 10),
        ]:
            _sakura_blossom(sp, bx, by, br)
        # Falling petals
        sp.detail([PG(leaf_pts((px, py), ang, 15, 9), "#F4A5C2")
                   for px, py, ang in [(48, 162, 25), (210, 152, -30), (62, 198, 55), (196, 194, -50)]])
        corner_sparkles(sp, [(42, 54, 10), (214, 56, 10), (212, 174, 8)])
    return sp


# ==========================================================================
#  33. PEACH MOCHI CAT IN ORANGE CARDBOARD BOX
# ==========================================================================
def mochi_cat(stage: int) -> Sprite:
    sp = Sprite()
    box_main = "#F6B067"
    box_top = "#F49A48"
    box_dk = "#DA7D32"
    cat_white = "#FFFFFF"
    cat_cream = "#FFF9F5"
    ear_pink = "#F9C6CE"
    ol_cat = "#B87E88"
    ol_box = "#B46224"
    face_ink = "#623D42"

    if stage == 5:
        sp.glow(128, 128, 104, "#FCD5B5", alpha=145, power=1.6)
    sp.detail([E((128 - (56 + stage * 4), BOTTOM - 10, 128 + (56 + stage * 4), BOTTOM + 4), with_alpha(ol_box, 35))])

    def _draw_box(bx1, by1, bx2, by2, open_flap=False):
        sp.group([RR((bx1, by1, bx2, by2), 6, box_main)], ol_box, ow=4.8)
        if open_flap:
            flap = [(bx1 - 10, by1 + 2), (bx1 + 5, by1 - 22), (bx2 - 5, by1 - 22), (bx2 + 10, by1 + 2)]
            sp.group([PG(flap, box_top)], ol_box, ow=4.8)
        else:
            lid = [(bx1 - 9, by1 + 13), (bx1 + 2, by1 - 10), (bx2 - 2, by1 - 10), (bx2 + 9, by1 + 13)]
            sp.group([PG(lid, box_top)], ol_box, ow=4.8)
        det = [LN([(bx1 + 7, by1 + 9), (bx2 - 7, by1 + 9)], 2.4, with_alpha("#FFFFFF", 90))]
        for k in range(3):
            sx = bx2 - 12 - k * 8
            det.append(RR((sx - 2.6, by2 - 16, sx + 2.6, by2 - 5), 2, box_dk))
        sp.detail(det)

    def _ears(cx, cy, sc):
        le = round_poly([(cx - 30 * sc, cy - 10 * sc), (cx - 26 * sc, cy - 42 * sc), (cx - 7 * sc, cy - 23 * sc)], 4.5 * sc)
        re = round_poly([(cx + 7 * sc, cy - 23 * sc), (cx + 26 * sc, cy - 42 * sc), (cx + 30 * sc, cy - 10 * sc)], 4.5 * sc)
        li = round_poly([(cx - 25 * sc, cy - 14 * sc), (cx - 23 * sc, cy - 34 * sc), (cx - 11 * sc, cy - 22 * sc)], 2.8 * sc)
        ri = round_poly([(cx + 11 * sc, cy - 22 * sc), (cx + 23 * sc, cy - 34 * sc), (cx + 25 * sc, cy - 14 * sc)], 2.8 * sc)
        return [PG(le, cat_white), PG(re, cat_white)], [PG(li, ear_pink), PG(ri, ear_pink)]

    def _face(cx, cy, sc, happy=True):
        det = [
            E((cx - 24 * sc, cy + 3 * sc, cx - 11 * sc, cy + 12 * sc), with_alpha("#F9A8B8", 185)),
            E((cx + 11 * sc, cy + 3 * sc, cx + 24 * sc, cy + 12 * sc), with_alpha("#F9A8B8", 185)),
            E((cx - 4.0 * sc, cy + 1 * sc, cx + 4.0 * sc, cy + 6.5 * sc), "#B87A7A"),
            ARC((cx - 8.5 * sc, cy + 3 * sc, cx, cy + 13 * sc), 10, 175, 2.5 * sc, face_ink),
            ARC((cx, cy + 3 * sc, cx + 8.5 * sc, cy + 13 * sc), 5, 170, 2.5 * sc, face_ink),
            LN([(cx - 31 * sc, cy + 3 * sc), (cx - 16 * sc, cy + 5 * sc)], 2.2 * sc, ol_cat),
            LN([(cx - 30 * sc, cy + 10 * sc), (cx - 16 * sc, cy + 9 * sc)], 2.2 * sc, ol_cat),
            LN([(cx + 16 * sc, cy + 5 * sc), (cx + 31 * sc, cy + 3 * sc)], 2.2 * sc, ol_cat),
            LN([(cx + 16 * sc, cy + 9 * sc), (cx + 30 * sc, cy + 10 * sc)], 2.2 * sc, ol_cat),
            C(cx - 4.5 * sc, cy - 20 * sc, 2.0 * sc, "#E6B8B8"),
            C(cx + 3.8 * sc, cy - 22 * sc, 1.8 * sc, "#E6B8B8"),
        ]
        if happy:
            det.extend([
                ARC((cx - 21 * sc, cy - 11 * sc, cx - 6 * sc, cy + 3 * sc), 200, 340, 3.4 * sc, face_ink),
                ARC((cx + 6 * sc, cy - 11 * sc, cx + 21 * sc, cy + 3 * sc), 200, 340, 3.4 * sc, face_ink),
            ])
        else:
            det.extend([
                C(cx - 14 * sc, cy - 4 * sc, 4.3 * sc, face_ink),
                C(cx + 14 * sc, cy - 4 * sc, 4.3 * sc, face_ink),
                C(cx - 15.5 * sc, cy - 5.5 * sc, 1.6 * sc, "#FFFFFF"),
                C(cx + 12.5 * sc, cy - 5.5 * sc, 1.6 * sc, "#FFFFFF"),
            ])
        sp.detail(det)

    if stage == 0:
        _draw_box(70, BOTTOM - 86, 186, BOTTOM - 6, open_flap=False)
    elif stage == 1:
        eo, ei = _ears(128, BOTTOM - 94, 0.92)
        sp.group(eo + [E((96, BOTTOM - 118, 160, BOTTOM - 70), cat_white)], ol_cat, ow=4.8)
        sp.detail(ei)
        _draw_box(68, BOTTOM - 82, 188, BOTTOM - 6, open_flap=True)
    elif stage == 2:
        eo, ei = _ears(128, BOTTOM - 128, 0.98)
        sp.group(eo + [E((88, BOTTOM - 156, 168, BOTTOM - 88), cat_white)], ol_cat, ow=4.8)
        sp.detail(ei)
        _draw_box(66, BOTTOM - 86, 190, BOTTOM - 6, open_flap=True)
        sp.group([
            E((94, BOTTOM - 94, 114, BOTTOM - 70), cat_white),
            E((142, BOTTOM - 94, 162, BOTTOM - 70), cat_white),
        ], ol_cat, ow=4.5)
        _face(128, BOTTOM - 126, 0.94, happy=True)
    elif stage == 3:
        tail = quad((164, BOTTOM - 78), (198, BOTTOM - 92), (192, BOTTOM - 122), 14)
        sp.group([LN(tail, 16, cat_white)], ol_cat, ow=4.8)
        eo, ei = _ears(124, BOTTOM - 136, 1.02)
        sp.group(eo + [E((82, BOTTOM - 166, 166, BOTTOM - 80), cat_white)], ol_cat, ow=4.8)
        sp.detail(ei)
        _draw_box(64, BOTTOM - 88, 188, BOTTOM - 6, open_flap=True)
        sp.group([
            E((90, BOTTOM - 96, 112, BOTTOM - 72), cat_white),
            E((138, BOTTOM - 96, 160, BOTTOM - 72), cat_white),
        ], ol_cat, ow=4.5)
        _face(124, BOTTOM - 134, 0.96, happy=True)
    elif stage == 4:
        tail = quad((88, BOTTOM - 34), (56, BOTTOM - 52), (62, BOTTOM - 92), 14)
        sp.group([LN(tail, 18, cat_white)], ol_cat, ow=5.0)
        eo, ei = _ears(132, BOTTOM - 136, 1.12)
        sp.group(eo + [
            E((82, BOTTOM - 108, 182, BOTTOM - 6), cat_cream),
            E((80, BOTTOM - 180, 184, BOTTOM - 88), cat_white),
            RR((104, BOTTOM - 52, 124, BOTTOM - 6), 9, cat_white),
            RR((140, BOTTOM - 52, 160, BOTTOM - 6), 9, cat_white),
        ], ol_cat, ow=5.0)
        sp.detail(ei)
        _face(132, BOTTOM - 134, 1.08, happy=False)
    else:
        tail = quad((82, BOTTOM - 34), (48, BOTTOM - 54), (54, BOTTOM - 100), 14)
        sp.group([LN(tail, 20, cat_white)], ol_cat, ow=5.2)
        eo, ei = _ears(132, BOTTOM - 144, 1.20)
        sp.group(eo + [
            E((78, BOTTOM - 112, 186, BOTTOM - 6), cat_cream),
            E((74, BOTTOM - 192, 190, BOTTOM - 90), cat_white),
            RR((102, BOTTOM - 54, 124, BOTTOM - 6), 10, cat_white),
            RR((140, BOTTOM - 54, 162, BOTTOM - 6), 10, cat_white),
        ], ol_cat, ow=5.4)
        sp.detail(ei)
        sp.group([
            RR((104, BOTTOM - 98, 160, BOTTOM - 85), 5, "#F4A261"),
            C(132, BOTTOM - 82, 8.5, "#FBBF24"),
        ], ol_box, ow=3.6)
        _face(132, BOTTOM - 140, 1.16, happy=True)
        corner_sparkles(sp, [(48, 60, 11), (210, 56, 11), (208, 152, 9)])
    return sp


# ==========================================================================
#  34. FLUFFY BUNNY STICKER POP (Notedii-Style Kawaii White Bunny)
# ==========================================================================
def fluffy_bunny(stage: int) -> Sprite:
    sp = Sprite()
    ink = "#2B2626"
    fur = "#FFFFFF"
    ear_p = "#F9C6D0"
    blush = (247, 178, 196, 185)
    ribbon = "#F48FA2"
    cherry = "#E11D48"

    if stage == 5:
        sp.glow(128, 128, 106, "#F9C6D0", alpha=145, power=1.6)
    sp.detail([E((128 - (42 + stage * 5), BOTTOM - 10, 128 + (42 + stage * 5), BOTTOM + 4), with_alpha(ink, 35))])

    def _ear_poly(x0, y0, w, h, ang_deg):
        ang = math.radians(ang_deg)
        pts = []
        for k in range(28):
            t = 2 * math.pi * k / 28.0
            lx, ly = math.cos(t) * w, math.sin(t) * h
            pts.append((x0 + lx * math.cos(ang) - ly * math.sin(ang),
                        y0 + lx * math.sin(ang) + ly * math.cos(ang)))
        return pts

    def _tall_ears(cx, cy, sc, spread=15.0, tilt=0.0):
        lo = _ear_poly(cx - spread * sc, cy - 42 * sc, 11.5 * sc, 31 * sc, -12 + tilt)
        ro = _ear_poly(cx + spread * sc, cy - 42 * sc, 11.5 * sc, 31 * sc, 12 + tilt)
        li = _ear_poly(cx - spread * sc, cy - 41 * sc, 6.2 * sc, 22 * sc, -12 + tilt)
        ri = _ear_poly(cx + spread * sc, cy - 41 * sc, 6.2 * sc, 22 * sc, 12 + tilt)
        return [PG(lo, fur), PG(ro, fur)], [PG(li, ear_p), PG(ri, ear_p)]

    def _face(cx, cy, sc, mood="cute"):
        det = [
            E((cx - 24 * sc, cy + 3 * sc, cx - 12 * sc, cy + 11 * sc), blush),
            E((cx + 12 * sc, cy + 3 * sc, cx + 24 * sc, cy + 11 * sc), blush),
        ]
        if mood == "sleep":
            det.extend([
                ARC((cx - 16 * sc, cy - 4 * sc, cx - 5 * sc, cy + 5 * sc), 15, 165, 2.8 * sc, ink),
                ARC((cx + 5 * sc, cy - 4 * sc, cx + 16 * sc, cy + 5 * sc), 15, 165, 2.8 * sc, ink),
                ARC((cx - 5 * sc, cy + 3 * sc, cx + 5 * sc, cy + 9 * sc), 20, 160, 2.2 * sc, ink),
            ])
        elif mood == "happy":
            det.extend([
                ARC((cx - 18 * sc, cy - 7 * sc, cx - 7 * sc, cy + 4 * sc), 200, 340, 3.2 * sc, ink),
                ARC((cx + 7 * sc, cy - 7 * sc, cx + 18 * sc, cy + 4 * sc), 200, 340, 3.2 * sc, ink),
                ARC((cx - 6.5 * sc, cy + 2 * sc, cx, cy + 10 * sc), 15, 175, 2.4 * sc, ink),
                ARC((cx, cy + 2 * sc, cx + 6.5 * sc, cy + 10 * sc), 5, 165, 2.4 * sc, ink),
            ])
        else:
            det.extend([
                E((cx - 18 * sc, cy - 7 * sc, cx - 9 * sc, cy + 4 * sc), ink),
                E((cx + 9 * sc, cy - 7 * sc, cx + 18 * sc, cy + 4 * sc), ink),
                C(cx - 15 * sc, cy - 3.5 * sc, 2.0 * sc, "#FFFFFF"),
                C(cx + 12 * sc, cy - 3.5 * sc, 2.0 * sc, "#FFFFFF"),
                ARC((cx - 6 * sc, cy + 2 * sc, cx, cy + 9 * sc), 15, 175, 2.4 * sc, ink),
                ARC((cx, cy + 2 * sc, cx + 6 * sc, cy + 9 * sc), 5, 165, 2.4 * sc, ink),
            ])
        sp.detail(det)

    if stage == 0:
        sp.group([
            C(86, BOTTOM - 24, 12, fur),
            E((90, BOTTOM - 58, 172, BOTTOM - 8), fur),
            E((98, BOTTOM - 74, 142, BOTTOM - 48), fur),
            E((104, BOTTOM - 68, 144, BOTTOM - 42), fur),
        ], ink, ow=5.2)
        sp.detail([E((108, BOTTOM - 63, 136, BOTTOM - 48), ear_p)])
        _face(144, BOTTOM - 32, 0.70, mood="sleep")
    elif stage == 1:
        eo, ei = _tall_ears(128, BOTTOM - 66, 0.74, spread=15, tilt=12)
        sp.group([C(160, BOTTOM - 20, 12, fur)] + eo + [
            E((96, BOTTOM - 54, 160, BOTTOM - 6), fur),
            E((96, BOTTOM - 96, 162, BOTTOM - 38), fur),
        ], ink, ow=5.2)
        sp.detail(ei)
        _face(128, BOTTOM - 66, 0.78, mood="cute")
    elif stage == 2:
        eo, ei = _tall_ears(128, BOTTOM - 90, 0.86, spread=15, tilt=5)
        sp.group([C(166, BOTTOM - 24, 14, fur)] + eo + [
            E((92, BOTTOM - 70, 164, BOTTOM - 6), fur),
            E((88, BOTTOM - 124, 168, BOTTOM - 54), fur),
            E((106, BOTTOM - 28, 126, BOTTOM - 6), fur),
            E((130, BOTTOM - 28, 150, BOTTOM - 6), fur),
        ], ink, ow=5.2)
        sp.detail(ei)
        _face(128, BOTTOM - 88, 0.90, mood="cute")
    elif stage == 3:
        eo, ei = _tall_ears(128, BOTTOM - 108, 0.96, spread=16, tilt=0)
        sp.group([C(172, BOTTOM - 26, 15, fur)] + eo + [
            E((88, BOTTOM - 84, 168, BOTTOM - 6), fur),
            E((82, BOTTOM - 146, 174, BOTTOM - 66), fur),
            E((104, BOTTOM - 30, 126, BOTTOM - 6), fur),
            E((130, BOTTOM - 30, 152, BOTTOM - 6), fur),
        ], ink, ow=5.4)
        sp.detail(ei)
        _face(128, BOTTOM - 106, 0.98, mood="cute")
    elif stage == 4:
        eo, ei = _tall_ears(128, BOTTOM - 122, 1.04, spread=17, tilt=-3)
        sp.group([C(176, BOTTOM - 28, 16, fur)] + eo + [
            E((84, BOTTOM - 94, 172, BOTTOM - 6), fur),
            E((78, BOTTOM - 160, 178, BOTTOM - 74), fur),
            E((74, BOTTOM - 76, 98, BOTTOM - 52), fur),
            E((158, BOTTOM - 76, 182, BOTTOM - 52), fur),
            E((102, BOTTOM - 32, 126, BOTTOM - 6), fur),
            E((130, BOTTOM - 32, 154, BOTTOM - 6), fur),
        ], ink, ow=5.5)
        sp.detail(ei)
        _face(128, BOTTOM - 118, 1.04, mood="happy")
    else:
        eo, ei = _tall_ears(128, BOTTOM - 130, 1.10, spread=18, tilt=0)
        sp.group([C(180, BOTTOM - 30, 16, fur)] + eo + [
            E((82, BOTTOM - 100, 174, BOTTOM - 6), fur),
            E((74, BOTTOM - 172, 182, BOTTOM - 80), fur),
            E((100, BOTTOM - 34, 126, BOTTOM - 6), fur),
            E((130, BOTTOM - 34, 156, BOTTOM - 6), fur),
        ], ink, ow=5.6)
        sp.detail(ei)
        # Signature pink ribbon collar + twin red cherry charm!
        sp.detail([
            ARC((96, BOTTOM - 98, 160, BOTTOM - 72), 15, 165, 5.2, ribbon),
            LN([(120, BOTTOM - 76), (114, BOTTOM - 63)], 2.6, "#16A34A"),
            LN([(120, BOTTOM - 76), (126, BOTTOM - 63)], 2.6, "#16A34A"),
            C(113, BOTTOM - 61, 5.5, cherry),
            C(127, BOTTOM - 61, 5.5, cherry),
            C(111, BOTTOM - 63, 1.8, "#FFFFFF"),
            C(125, BOTTOM - 63, 1.8, "#FFFFFF"),
        ])
        _face(128, BOTTOM - 126, 1.10, mood="cute")
        corner_sparkles(sp, [(46, 58, 11), (212, 54, 11), (212, 154, 9), (44, 154, 9)])
    return sp


# ==========================================================================
#  35. MILK & MOCHA BEAR SWEET LOVE (Berry Pink & Cocoa Chibi Bears)
# ==========================================================================
def milk_mocha_bear(stage: int) -> Sprite:
    sp = Sprite()
    ink = "#5C3B30"
    mocha = "#C6947C"
    mocha_in = "#E7C5B3"
    milk = "#FFFDFD"
    milk_ear = "#F4A5BA"
    heart_p = "#E86A92"
    heart_lt = "#FBCFE8"
    can_p = "#F48FB1"
    pot_c = "#D98A6C"

    if stage == 5:
        sp.glow(128, 128, 108, "#F9A8C9", alpha=145, power=1.6)
    sp.detail([E((128 - (50 + stage * 7), BOTTOM - 10, 128 + (50 + stage * 7), BOTTOM + 4), with_alpha(ink, 35))])

    def _draw_bear(cx, cy, sc, body_col, ear_in, happy=True, hold_heart=False):
        r_ear = 13.5 * sc
        sp.group([
            C(cx - 26 * sc, cy - 27 * sc, r_ear, body_col),
            C(cx + 26 * sc, cy - 27 * sc, r_ear, body_col),
            E((cx - 29 * sc, cy + 4 * sc, cx + 29 * sc, cy + 51 * sc), body_col),
            E((cx - 35 * sc, cy - 31 * sc, cx + 35 * sc, cy + 25 * sc), body_col),
            E((cx - 22 * sc, cy + 38 * sc, cx - 3 * sc, cy + 53 * sc), body_col),
            E((cx + 3 * sc, cy + 38 * sc, cx + 22 * sc, cy + 53 * sc), body_col),
        ], ink, ow=4.6)
        det = [
            C(cx - 26 * sc, cy - 27 * sc, 7 * sc, ear_in),
            C(cx + 26 * sc, cy - 27 * sc, 7 * sc, ear_in),
            E((cx - 26 * sc, cy + 1 * sc, cx - 14 * sc, cy + 9 * sc), with_alpha("#F48FB1", 190)),
            E((cx + 14 * sc, cy + 1 * sc, cx + 26 * sc, cy + 9 * sc), with_alpha("#F48FB1", 190)),
            E((cx - 4.2 * sc, cy - 1 * sc, cx + 4.2 * sc, cy + 5 * sc), ink),
        ]
        if happy:
            det.extend([
                ARC((cx - 20 * sc, cy - 11 * sc, cx - 7 * sc, cy + 1 * sc), 200, 340, 3.0 * sc, ink),
                ARC((cx + 7 * sc, cy - 11 * sc, cx + 20 * sc, cy + 1 * sc), 200, 340, 3.0 * sc, ink),
                E((cx - 5.5 * sc, cy + 5.5 * sc, cx + 5.5 * sc, cy + 14.5 * sc), "#F472B6"),
            ])
        else:
            det.extend([
                C(cx - 14 * sc, cy - 4.5 * sc, 4.3 * sc, ink),
                C(cx + 14 * sc, cy - 4.5 * sc, 4.3 * sc, ink),
                C(cx - 15.5 * sc, cy - 6.0 * sc, 1.6 * sc, "#FFFFFF"),
                C(cx + 12.5 * sc, cy - 6.0 * sc, 1.6 * sc, "#FFFFFF"),
                ARC((cx - 5.5 * sc, cy + 3.5 * sc, cx, cy + 10 * sc), 15, 175, 2.2 * sc, ink),
                ARC((cx, cy + 3.5 * sc, cx + 5.5 * sc, cy + 10 * sc), 5, 165, 2.2 * sc, ink),
            ])
        sp.detail(det)
        if hold_heart:
            sp.group([
                PG(_heart_pts(cx, cy + 30 * sc, 13.5 * sc), heart_p),
                E((cx - 24 * sc, cy + 22 * sc, cx - 7 * sc, cy + 36 * sc), body_col),
                E((cx + 7 * sc, cy + 22 * sc, cx + 24 * sc, cy + 36 * sc), body_col),
            ], ink, ow=3.8)

    if stage == 0:
        # Tiny pink watering can & sprout
        sp.group([
            RR((86, BOTTOM - 58, 144, BOTTOM - 8), 12, can_p),
            LN([(142, BOTTOM - 34), (172, BOTTOM - 56)], 10, can_p),
            ARC((68, BOTTOM - 52, 96, BOTTOM - 18), 90, 270, 7.0, can_p),
        ], ink, ow=4.6)
        sp.detail([PG(_heart_pts(115, BOTTOM - 33, 11), "#FFFFFF")])
        sp.group([
            LN([(180, BOTTOM - 10), (180, BOTTOM - 36)], 5.0, "#59A96A"),
            PG(leaf_pts((180, BOTTOM - 32), -140, 24, 14), "#81C784"),
            PG(leaf_pts((180, BOTTOM - 32), -40, 24, 14), "#A5D6A7"),
        ], ink, ow=3.8)
    elif stage == 1:
        _draw_bear(128, BOTTOM - 58, 0.90, milk, milk_ear, happy=False, hold_heart=True)
    elif stage == 2:
        _draw_bear(128, BOTTOM - 64, 1.00, mocha, mocha_in, happy=True, hold_heart=True)
        sp.detail([PG(_heart_pts(174, BOTTOM - 110, 10), heart_p)])
    elif stage == 3:
        _draw_bear(92, BOTTOM - 58, 0.88, mocha, mocha_in, happy=True, hold_heart=True)
        _draw_bear(164, BOTTOM - 58, 0.88, milk, milk_ear, happy=True, hold_heart=True)
        sp.detail([PG(_heart_pts(128, BOTTOM - 116, 12), heart_p)])
    elif stage == 4:
        _draw_bear(84, BOTTOM - 60, 0.84, mocha, mocha_in, happy=False, hold_heart=False)
        _draw_bear(174, BOTTOM - 60, 0.84, milk, milk_ear, happy=True, hold_heart=False)
        sp.group([
            PG([(115, BOTTOM - 38), (141, BOTTOM - 38), (137, BOTTOM - 8), (119, BOTTOM - 8)], pot_c),
            RR((111, BOTTOM - 44, 145, BOTTOM - 34), 4, "#C57455"),
            LN([(128, BOTTOM - 44), (128, BOTTOM - 72)], 5.0, "#4E9F68"),
            PG(leaf_pts((128, BOTTOM - 54), -140, 22, 13), "#74C684"),
            PG(leaf_pts((128, BOTTOM - 54), -40, 22, 13), "#74C684"),
        ], ink, ow=3.8)
        _sakura_blossom(sp, 128, BOTTOM - 78, 15, "#F9A8D4", "#FBBF24")
        sp.group([RR((102, BOTTOM - 62, 120, BOTTOM - 45), 5, can_p)], ink, ow=3.2)
    else:
        _draw_bear(94, BOTTOM - 68, 0.98, mocha, mocha_in, happy=True, hold_heart=False)
        _draw_bear(162, BOTTOM - 68, 0.98, milk, milk_ear, happy=True, hold_heart=False)
        sp.group([PG(_heart_pts(128, BOTTOM - 42, 22), heart_p)], ink, ow=4.2)
        sp.detail([
            PG(_heart_pts(128, BOTTOM - 134, 16), "#E86A92"),
            PG(_heart_pts(80, BOTTOM - 144, 10), heart_lt),
            PG(_heart_pts(178, BOTTOM - 142, 11), "#F9A8C9"),
        ])
        corner_sparkles(sp, [(42, 62, 11), (214, 60, 11), (212, 152, 8)])
    return sp


BATCH4_THEMES = {
    "sakura_tree": sakura_tree,
    "mochi_cat": mochi_cat,
    "fluffy_bunny": fluffy_bunny,
    "milk_mocha_bear": milk_mocha_bear,
}


def main():
    only = sys.argv[1:] or None
    results = {}
    for slug, fn in BATCH4_THEMES.items():
        if only and slug not in only:
            continue
        ims = []
        for stage in range(6):
            out = ASSETS_DIR / slug / f"stage_{stage}.png"
            ims.append(fn(stage).save(out))
            print(f"  {out.relative_to(ROOT)}  {out.stat().st_size / 1024:.1f} KB", flush=True)
        results[slug] = ims
    if not only:
        sheet_path = PREVIEW_DIR / "assets_contact_sheet_batch4.png"
        build_contact_sheet(results, sheet_path)
        print(f"Contact sheet: {sheet_path.relative_to(ROOT)}", flush=True)


if __name__ == "__main__":
    main()
