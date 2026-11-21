"""
build_mobile_templates.py — Builds Mobile Portrait Habit Tracker templates (v3.0, 01..31)
into `templates/mobile_portrait_sheets/01..31_*_Mobile.xlsx`.

Pipeline:
  1. Generate mobile portrait `.xlsx` workbooks via `hx.mobile.build_mobile_workbook`
     (strictly 8-col portrait `B:I`, 4 visible tabs `📱 Tuần Này`, `📝 Việc Hôm Nay`,
     `🎯 Mục Tiêu & Thành Tựu`, `📖 Hướng Dẫn`, native theme-colored Excel checkboxes +
     dynamic `=IMAGE(...)` pointing to `main/assets/`).
  2. Post-process via Excel COM with retry guards & COM recycling every 5 workbooks
     (`CellControl.SetCheckbox()`, `CalculateFullRebuild`, strictly preserving `=IMAGE(...)`!).
  3. Capture crisp portrait preview PNGs into `previews/mobile_*.png` using temporary render copies.

Usage:
    python scripts/build_mobile_templates.py [--start N] [--end M] [short_key ...]
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
from hx.mobile import (build_mobile_workbook, MOBILE_WEEK_SHEET, MOBILE_TASKS_SHEET,
                       MOBILE_GOALS_SHEET, MOBILE_GUIDE_SHEET, MOBILE_CALC_SHEET)

OUT_DIR = ROOT / "templates" / "mobile_portrait_sheets"
ASSETS_DIR = ROOT / "assets"
PREVIEWS_DIR = ROOT / "previews"

PREVIEW_KEYS = {"01_sunflower", "02_cactus", "07_sakura", "10_aurora",
                "11_velvet_rose", "16_dream_house", "18_plum_oak",
                "20_alpaca_cream", "24_royal_cat_cash", "30_shiba_inu", "31_akita_inu",
                "32_sakura_min", "33_mochi_cat", "34_fluffy_bunny", "35_milk_mocha"}


def _com_retry(fn, retries: int = 12, delay: float = 0.25):
    for attempt in range(retries):
        try:
            return fn()
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(delay)


def _new_excel():
    xl = win32.DispatchEx("Excel.Application")
    xl.Visible = False
    xl.DisplayAlerts = False
    return xl


def _quit_excel(xl):
    if xl is None:
        return
    try:
        xl.Quit()
    except Exception:
        pass
    time.sleep(0.4)


def _grab_png(ws, rng_str: str, out_path: Path, retries: int = 6):
    _com_retry(lambda: ws.Activate())
    _com_retry(lambda: ws.Range("A1").Select())
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
    w = _com_retry(lambda: cell_rng.Width)
    h = _com_retry(lambda: cell_rng.Height)
    l0 = _com_retry(lambda: cell_rng.Left)
    t0 = _com_retry(lambda: cell_rng.Top)
    side = max(12.0, min(w - 2 * pad_x, h - 2 * pad_y))
    left = l0 + (w - side) / 2.0
    if align_bottom:
        top = t0 + h - side - 2.0
    else:
        top = t0 + (h - side) / 2.0
    shp = _com_retry(lambda: ws.Shapes.AddPicture(
        Filename=str(img_path.resolve()), LinkToFile=False, SaveWithDocument=True,
        Left=left, Top=top, Width=side, Height=side,
    ))
    _com_retry(lambda: setattr(shp.Line, "Visible", False))
    return shp


def _capture_mobile_previews(xl, meta: dict):
    """Render crisp portrait PNGs from an isolated temp copy with local sprites overlaid for preview."""
    short_key = meta["short_key"]
    slug = meta["slug"]
    src = Path(meta["out_path"])
    tmp_render = Path(tempfile.gettempdir()) / f"render_{short_key}_mobile.xlsx"
    shutil.copy2(src, tmp_render)

    wb = _com_retry(lambda: xl.Workbooks.Open(str(tmp_render.resolve())))
    try:
        _com_retry(lambda: xl.CalculateFullRebuild())
        time.sleep(0.35)
        ws_calc = wb.Worksheets(MOBILE_CALC_SHEET)
        ws_wk = wb.Worksheets(MOBILE_WEEK_SHEET)
        ws_dt = wb.Worksheets(MOBILE_TASKS_SHEET)
        ws_go = wb.Worksheets(MOBILE_GOALS_SHEET)
        ws_gd = wb.Worksheets(MOBILE_GUIDE_SHEET)

        # 1) Tab 1: Replace =IMAGE() display with exact computed stage sprite on temp copy ONLY
        hero_stg = max(1, min(6, int(_com_retry(lambda: ws_calc.Range("E12").Value) or 1)))
        _com_retry(lambda: setattr(ws_wk.Range("F9"), "Value", ""))
        _overlay_sprite(ws_wk, ws_wk.Range("F9:I12"), ASSETS_DIR / slug / f"stage_{hero_stg - 1}.png")

        for dow in range(7):
            c_xl = 3 + dow
            day_val = _com_retry(lambda c=c_xl: ws_wk.Cells(20, c).Value)
            _com_retry(lambda c=c_xl: setattr(ws_wk.Cells(15, c), "Value", ""))
            if day_val is not None and str(day_val).strip() != "":
                stg = max(1, min(6, int(_com_retry(lambda d=dow: ws_calc.Cells(1, 7 + d).Value) or 1)))
                _overlay_sprite(ws_wk, ws_wk.Cells(15, c_xl),
                                ASSETS_DIR / slug / f"stage_{stg - 1}.png", align_bottom=True)

        sz_top = _grab_png(ws_wk, meta["week_capture_top"], PREVIEWS_DIR / f"mobile_{short_key}.png")
        print(f"      [PNG] mobile_{short_key}.png ({sz_top[0]}x{sz_top[1]})", flush=True)

        # Capture Mobile Daily Tasks tab on flagship templates
        if short_key in ("01_sunflower", "30_shiba_inu"):
            dt_stg = max(1, min(6, int(_com_retry(lambda: ws_calc.Range("E33").Value) or 1)))
            _com_retry(lambda: setattr(ws_dt.Range("F9"), "Value", ""))
            _overlay_sprite(ws_dt, ws_dt.Range("F9:I12"), ASSETS_DIR / slug / f"stage_{dt_stg - 1}.png")
            out_dt = PREVIEWS_DIR / f"mobile_{short_key}_daily.png"
            sz_dt = _grab_png(ws_dt, meta["tasks_capture"], out_dt)
            print(f"      [PNG] {out_dt.name} ({sz_dt[0]}x{sz_dt[1]})", flush=True)

        if short_key == "01_sunflower":
            sz_bot = _grab_png(ws_wk, meta["week_capture_bottom"], PREVIEWS_DIR / "mobile_01_sunflower_bottom.png")
            print(f"      [PNG] mobile_01_sunflower_bottom.png ({sz_bot[0]}x{sz_bot[1]})", flush=True)

            yg_stg = max(1, min(6, int(_com_retry(lambda: ws_calc.Range("E19").Value) or 1)))
            _com_retry(lambda: setattr(ws_go.Range("F4"), "Value", ""))
            _overlay_sprite(ws_go, ws_go.Range("F4:I7"), ASSETS_DIR / slug / f"stage_{yg_stg - 1}.png")

            ach_stg = max(1, min(6, int(_com_retry(lambda: ws_calc.Range("E27").Value) or 1)))
            _com_retry(lambda: setattr(ws_go.Range("G39"), "Value", ""))
            _overlay_sprite(ws_go, ws_go.Range("G39:I40"), ASSETS_DIR / slug / f"stage_{ach_stg - 1}.png")
            sz_go = _grab_png(ws_go, meta["goals_capture"], PREVIEWS_DIR / "mobile_01_goals.png")
            print(f"      [PNG] mobile_01_goals.png ({sz_go[0]}x{sz_go[1]})", flush=True)

            for rr in range(1, 38):
                f_txt = str(_com_retry(lambda r=rr: ws_gd.Cells(r, 2).Formula) or "")
                if "IMAGE(" in f_txt:
                    for bi in range(3):
                        c1 = 2 + bi * 2
                        f2 = str(_com_retry(lambda r=rr, c=c1: ws_gd.Cells(r, c).Formula) or "")
                        for s_i in range(6):
                            if f"stage_{s_i}.png" in f2:
                                _com_retry(lambda r=rr, c=c1: setattr(ws_gd.Cells(r, c), "Value", ""))
                                _overlay_sprite(ws_gd, ws_gd.Range(ws_gd.Cells(rr, c1), ws_gd.Cells(rr, c1 + 1)),
                                                ASSETS_DIR / slug / f"stage_{s_i}.png")
                                break
            sz_gd = _grab_png(ws_gd, meta["guide_capture"], PREVIEWS_DIR / "mobile_01_guide.png")
            print(f"      [PNG] mobile_01_guide.png ({sz_gd[0]}x{sz_gd[1]})", flush=True)
    finally:
        _com_retry(lambda: wb.Close(SaveChanges=False))
        tmp_render.unlink(missing_ok=True)


def _select_templates(args: list[str]):
    start_idx = 1
    end_idx = len(TEMPLATES)
    only: list[str] = []
    i = 0
    while i < len(args):
        if args[i] == "--start" and i + 1 < len(args):
            start_idx = int(args[i + 1])
            i += 2
        elif args[i] == "--end" and i + 1 < len(args):
            end_idx = int(args[i + 1])
            i += 2
        else:
            only.append(args[i])
            i += 1
    selected = []
    for pos, tdef in enumerate(TEMPLATES, start=1):
        if only:
            if tdef.stem in only or tdef.short_key in only:
                selected.append(tdef)
        elif start_idx <= pos <= end_idx:
            selected.append(tdef)
    return selected


def main():
    selected = _select_templates(sys.argv[1:])
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    metas = []
    print(f"Building Mobile Portrait `.xlsx` templates ({len(selected)} file(s))...", flush=True)
    for tdef in selected:
        out_path = OUT_DIR / f"{tdef.stem}_Mobile.xlsx"
        meta = build_mobile_workbook(tdef, out_path)
        metas.append(meta)
        print(f"  [MOBILE base] {out_path.name} ({out_path.stat().st_size:,} B)", flush=True)

    print("\nRunning Excel COM post-build (CellControl.SetCheckbox + formula cache + previews, recycling COM every 5)...",
          flush=True)
    xl = None
    try:
        for idx, meta in enumerate(metas):
            if idx % 5 == 0:
                _quit_excel(xl)
                xl = _new_excel()
            t0 = time.perf_counter()
            p = Path(meta["out_path"]).resolve()
            wb = _com_retry(lambda: xl.Workbooks.Open(str(p)))
            try:
                ws_wk = wb.Worksheets(MOBILE_WEEK_SHEET)
                ws_dt = wb.Worksheets(MOBILE_TASKS_SHEET)
                ws_go = wb.Worksheets(MOBILE_GOALS_SHEET)
                try:
                    _com_retry(lambda: ws_wk.Range("C21:I35").CellControl.SetCheckbox())
                    _com_retry(lambda: ws_dt.Range("B16:B30").CellControl.SetCheckbox())
                    _com_retry(lambda: ws_go.Range("B11:B22").CellControl.SetCheckbox())
                except Exception:
                    pass

                for nm in (MOBILE_GUIDE_SHEET, MOBILE_GOALS_SHEET, MOBILE_TASKS_SHEET, MOBILE_WEEK_SHEET):
                    ws = wb.Worksheets(nm)
                    def _prep(s=ws):
                        s.Activate()
                        xl.ActiveWindow.DisplayGridlines = False
                        s.Range("A1").Select()
                    _com_retry(_prep)

                _com_retry(lambda: xl.CalculateFullRebuild())
                _com_retry(lambda: wb.Save())
            finally:
                _com_retry(lambda: wb.Close(SaveChanges=False))

            if meta["short_key"] in PREVIEW_KEYS:
                _capture_mobile_previews(xl, meta)

            dt = time.perf_counter() - t0
            print(f"  ✓ [MOBILE] {p.name} ({p.stat().st_size:,} B, {dt:.1f}s)", flush=True)
    finally:
        _quit_excel(xl)


if __name__ == "__main__":
    main()
