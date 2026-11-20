"""
build_mobile_templates.py — Builds ALL 10 Mobile Portrait Habit Tracker templates
into `templates/mobile_portrait_sheets/01..10_*_Mobile.xlsx`.

Pipeline:
  1. Generate all 10 mobile portrait `.xlsx` workbooks via `hx.mobile.build_mobile_workbook`
     (strictly 8-col portrait `B:I`, 3 tabs `📱 Tuần Này`, `🎯 Mục Tiêu & Thành Tựu`, `📖 Hướng Dẫn`,
     native theme-colored Excel checkboxes + dynamic `=IMAGE(...)` pointing to `main/assets/`).
  2. Post-process via Excel COM (`CellControl.SetCheckbox()` if supported, force `CalculateFullRebuild`,
     strictly preserving all `=IMAGE(...)` formulas!).
  3. Capture crisp portrait preview PNGs into `previews/mobile_*.png` using temporary render copies
     (overlaying local `assets/<slug>/stage_X.png` strictly on the temp render copy so headless Excel's
     Linked Data Types block never shows `#BLOCKED!` in README screenshots, while keeping the real
     deliverable `.xlsx` 100% pure `=IMAGE(...)`!).

Usage:
    python scripts/build_mobile_templates.py [short_key ...]
"""
from __future__ import annotations

import shutil
import sys
import tempfile
import time
from pathlib import Path

from PIL import Image, ImageGrab
import win32com.client as win32

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from excel_builder import TEMPLATES
from hx.mobile import (build_mobile_workbook, MOBILE_WEEK_SHEET, MOBILE_GOALS_SHEET,
                       MOBILE_GUIDE_SHEET, MOBILE_CALC_SHEET)

OUT_DIR = ROOT / "templates" / "mobile_portrait_sheets"
ASSETS_DIR = ROOT / "assets"
PREVIEWS_DIR = ROOT / "previews"

PREVIEW_KEYS = {"01_sunflower", "02_cactus", "07_sakura", "10_aurora",
                "11_velvet_rose", "16_dream_house", "18_plum_oak"}


def _grab_png(ws, rng_str: str, out_path: Path, retries: int = 5):
    ws.Activate()
    ws.Range("A1").Select()
    time.sleep(0.20)
    for attempt in range(retries):
        try:
            ws.Range(rng_str).CopyPicture(Appearance=1, Format=2)
            time.sleep(0.30)
            im = ImageGrab.grabclipboard()
            if isinstance(im, Image.Image):
                out_path.parent.mkdir(parents=True, exist_ok=True)
                im.save(out_path, optimize=True)
                return im.size
        except Exception as e:
            if attempt == retries - 1:
                raise e
        time.sleep(0.35)
    raise RuntimeError(f"Clipboard grab failed for {ws.Name}!{rng_str}")


def _overlay_sprite(ws, cell_rng, img_path: Path, align_bottom: bool = False):
    pad_x = 3.0 if align_bottom else 5.0
    pad_y = 3.0 if align_bottom else 5.0
    side = max(12.0, min(cell_rng.Width - 2 * pad_x, cell_rng.Height - 2 * pad_y))
    left = cell_rng.Left + (cell_rng.Width - side) / 2.0
    if align_bottom:
        top = cell_rng.Top + cell_rng.Height - side - 2.0
    else:
        top = cell_rng.Top + (cell_rng.Height - side) / 2.0
    shp = ws.Shapes.AddPicture(
        Filename=str(img_path.resolve()), LinkToFile=False, SaveWithDocument=True,
        Left=left, Top=top, Width=side, Height=side,
    )
    shp.Line.Visible = False
    return shp


def _capture_mobile_previews(xl, meta: dict):
    """Render crisp portrait PNGs from an isolated temp copy with local sprites overlaid for preview."""
    short_key = meta["short_key"]
    slug = meta["slug"]
    src = Path(meta["out_path"])
    tmp_render = Path(tempfile.gettempdir()) / f"render_{short_key}_mobile.xlsx"
    shutil.copy2(src, tmp_render)

    wb = xl.Workbooks.Open(str(tmp_render.resolve()))
    try:
        xl.CalculateFullRebuild()
        ws_calc = wb.Worksheets(MOBILE_CALC_SHEET)
        ws_wk = wb.Worksheets(MOBILE_WEEK_SHEET)
        ws_go = wb.Worksheets(MOBILE_GOALS_SHEET)
        ws_gd = wb.Worksheets(MOBILE_GUIDE_SHEET)

        # 1) Tab 1: Replace =IMAGE() display with exact computed stage sprite on temp copy ONLY
        hero_stg = max(1, min(6, int(ws_calc.Range("E12").Value or 1)))
        ws_wk.Range("F9").Value = ""
        _overlay_sprite(ws_wk, ws_wk.Range("F9:I12"), ASSETS_DIR / slug / f"stage_{hero_stg - 1}.png")

        for dow in range(7):
            c_xl = 3 + dow
            day_val = ws_wk.Cells(20, c_xl).Value
            ws_wk.Cells(15, c_xl).Value = ""
            if day_val is not None and str(day_val).strip() != "":
                stg = max(1, min(6, int(ws_calc.Cells(1, 7 + dow).Value or 1)))
                _overlay_sprite(ws_wk, ws_wk.Cells(15, c_xl),
                                ASSETS_DIR / slug / f"stage_{stg - 1}.png", align_bottom=True)

        # Stitch full mobile portrait view (or top+bottom cleanly)
        sz_top = _grab_png(ws_wk, meta["week_capture_top"], PREVIEWS_DIR / f"mobile_{short_key}.png")
        print(f"      [PNG] mobile_{short_key}.png ({sz_top[0]}x{sz_top[1]})", flush=True)

        if short_key == "01_sunflower":
            # Also capture lower half (Progress Bars + Chart + Quick Notes), Goals tab, and Guide tab!
            sz_bot = _grab_png(ws_wk, meta["week_capture_bottom"], PREVIEWS_DIR / "mobile_01_sunflower_bottom.png")
            print(f"      [PNG] mobile_01_sunflower_bottom.png ({sz_bot[0]}x{sz_bot[1]})", flush=True)

            yg_stg = max(1, min(6, int(ws_calc.Range("E19").Value or 1)))
            ws_go.Range("F4").Value = ""
            _overlay_sprite(ws_go, ws_go.Range("F4:I7"), ASSETS_DIR / slug / f"stage_{yg_stg - 1}.png")

            ach_stg = max(1, min(6, int(ws_calc.Range("E27").Value or 1)))
            ws_go.Range("G39").Value = ""
            _overlay_sprite(ws_go, ws_go.Range("G39:I40"), ASSETS_DIR / slug / f"stage_{ach_stg - 1}.png")
            sz_go = _grab_png(ws_go, meta["goals_capture"], PREVIEWS_DIR / "mobile_01_goals.png")
            print(f"      [PNG] mobile_01_goals.png ({sz_go[0]}x{sz_go[1]})", flush=True)

            # Guide 2x3 stage sprites
            # Find the 2 sprite rows dynamically (rows where col B contains =IMAGE)
            for rr in range(1, 35):
                f_txt = str(ws_gd.Cells(rr, 2).Formula or "")
                if "IMAGE(" in f_txt:
                    for bi in range(3):
                        c1 = 2 + bi * 2
                        f2 = str(ws_gd.Cells(rr, c1).Formula or "")
                        for s_i in range(6):
                            if f"stage_{s_i}.png" in f2:
                                ws_gd.Cells(rr, c1).Value = ""
                                _overlay_sprite(ws_gd, ws_gd.Range(ws_gd.Cells(rr, c1), ws_gd.Cells(rr, c1 + 1)),
                                                ASSETS_DIR / slug / f"stage_{s_i}.png")
                                break
            sz_gd = _grab_png(ws_gd, meta["guide_capture"], PREVIEWS_DIR / "mobile_01_guide.png")
            print(f"      [PNG] mobile_01_guide.png ({sz_gd[0]}x{sz_gd[1]})", flush=True)
    finally:
        wb.Close(SaveChanges=False)
        tmp_render.unlink(missing_ok=True)


def main():
    only = sys.argv[1:] or None
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    metas = []
    print("Building Mobile Portrait `.xlsx` templates...", flush=True)
    for tdef in TEMPLATES:
        if only and tdef.stem not in only and tdef.short_key not in only:
            continue
        out_path = OUT_DIR / f"{tdef.stem}_Mobile.xlsx"
        meta = build_mobile_workbook(tdef, out_path)
        metas.append(meta)
        print(f"  [MOBILE base] {out_path.name} ({out_path.stat().st_size:,} B)", flush=True)

    print("\nRunning Excel COM post-build (CellControl.SetCheckbox + formula cache + previews)...", flush=True)
    xl = win32.DispatchEx("Excel.Application")
    xl.Visible = False
    xl.DisplayAlerts = False
    try:
        for meta in metas:
            t0 = time.perf_counter()
            p = Path(meta["out_path"]).resolve()
            wb = xl.Workbooks.Open(str(p))
            try:
                ws_wk = wb.Worksheets(MOBILE_WEEK_SHEET)
                ws_go = wb.Worksheets(MOBILE_GOALS_SHEET)
                # Ensure Excel native CellControl checkboxes are registered cleanly (preserving colors & values!)
                try:
                    ws_wk.Range("C21:I35").CellControl.SetCheckbox()
                    ws_go.Range("B11:B22").CellControl.SetCheckbox()
                except Exception:
                    # Already created natively by xlsxwriter.insert_checkbox()
                    pass

                # Ensure gridlines off on all 3 visible tabs & land on `📱 Tuần Này`!
                for nm in (MOBILE_GUIDE_SHEET, MOBILE_GOALS_SHEET, MOBILE_WEEK_SHEET):
                    ws = wb.Worksheets(nm)
                    for _att in range(6):
                        try:
                            ws.Activate()
                            xl.ActiveWindow.DisplayGridlines = False
                            ws.Range("A1").Select()
                            break
                        except Exception:
                            time.sleep(0.25)

                for _att in range(6):
                    try:
                        xl.CalculateFullRebuild()
                        wb.Save()
                        break
                    except Exception:
                        time.sleep(0.25)
            finally:
                wb.Close(SaveChanges=False)

            if meta["short_key"] in PREVIEW_KEYS:
                _capture_mobile_previews(xl, meta)

            dt = time.perf_counter() - t0
            print(f"  ✓ [MOBILE] {p.name} ({p.stat().st_size:,} B, {dt:.1f}s)", flush=True)
    finally:
        xl.Quit()


if __name__ == "__main__":
    main()
