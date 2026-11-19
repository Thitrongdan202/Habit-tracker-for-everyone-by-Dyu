"""
excel_com_enhancer.py — Version 2.0 Tier-A Universal Offline `.xlsx` COM Compiler.

Opens each base workbook built by `excel_builder.py` in headless Microsoft Excel:
  1. Inserts 6 crisp 300x300px sprites cleanly centered inside `_Assets!B2:B7`
  2. Creates 31 Workbook-level Named Ranges (`Anim_Day01`..`Anim_Day31`) bound to
     `=INDEX(_Assets!$B$2:$B$8, _Calc!$B$15)` .. `$AF$15`
  3. Pastes 31 borderless Linked Pictures in the animation row + Hero & Guide Linked Pictures
  4. Adds centered, flat Form Control Checkboxes linked to `;;;`-hidden boolean cells
  5. Hides `_Assets` and `_Calc` (`xlSheetHidden`), forces full calculation, saves pure `.xlsx`
     (FileFormat=51, ZERO VBA, ZERO macros, ZERO internet required!)
  6. Captures crisp high-res PNG screenshots into `previews/`

Run from repo root:
    python scripts/excel_com_enhancer.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from PIL import Image, ImageGrab
import win32com.client as win32

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from excel_builder import build_all_base_tier_a, BUILD_TMP, ASSETS_SHEET
from hx.tracker import CALC_SHEET
from hx.guide import GUIDE_SHEET

ASSETS_DIR = ROOT / "assets"
OFFLINE_DIR = ROOT / "templates" / "excel_universal_offline"
PREVIEWS_DIR = ROOT / "previews"


def paste_linked_picture(xl, src_cell, dst_ws, dst_range, formula: str, align_bottom: bool = False):
    """Copy `src_cell`, paste as Linked Picture on `dst_ws`, bind `formula`, size & align cleanly."""
    for attempt in range(6):
        try:
            src_cell.Copy()
            time.sleep(0.03)
            pic = dst_ws.Pictures().Paste(Link=True)
            xl.CutCopyMode = False
            pic.Formula = formula
            pic.ShapeRange.Line.Visible = False
            pic.ShapeRange.LockAspectRatio = -1  # msoTrue
            pad_x = 1.5 if align_bottom else 5.0
            pad_y = 3.0 if align_bottom else 5.0
            max_w = max(8.0, dst_range.Width - 2 * pad_x)
            max_h = max(8.0, dst_range.Height - 2 * pad_y)
            scale = min(max_w / pic.Width, max_h / pic.Height)
            pic.Width = pic.Width * scale
            pic.Left = dst_range.Left + (dst_range.Width - pic.Width) / 2.0
            if align_bottom:
                pic.Top = dst_range.Top + dst_range.Height - pic.Height - 2.0
            else:
                pic.Top = dst_range.Top + (dst_range.Height - pic.Height) / 2.0
            pic.Placement = 1  # xlMoveAndSize
            return pic
        except Exception as e:
            if attempt == 5:
                raise RuntimeError(f"Failed pasting linked picture {formula}: {e}") from e
            time.sleep(0.18 * (attempt + 1))


def grab_range_png(ws, rng_str: str, out_path: Path, retries: int = 5):
    ws.Activate()
    time.sleep(0.35)
    for attempt in range(retries):
        try:
            ws.Range(rng_str).CopyPicture(Appearance=1, Format=2)
            time.sleep(0.55)
            im = ImageGrab.grabclipboard()
            if isinstance(im, Image.Image):
                out_path.parent.mkdir(parents=True, exist_ok=True)
                im.save(out_path, optimize=True)
                return im.size
        except Exception as e:
            if attempt == retries - 1:
                raise e
        time.sleep(0.5)
    raise RuntimeError(f"Clipboard grab failed for {ws.Name}!{rng_str}")


def enhance_one(xl, meta: dict):
    stem = meta["stem"]
    slug = meta["slug"]
    base_path = Path(meta["base_path"])
    final_path = OFFLINE_DIR / f"{stem}.xlsx"
    if final_path.exists():
        final_path.unlink()

    wb = xl.Workbooks.Open(str(base_path.resolve()))
    try:
        xl.ScreenUpdating = False
        xl.Calculation = -4135  # xlCalculationManual

        # 1. Populate `_Assets!B2:B7` with 300x300px high-DPI PNGs
        ws_a = wb.Worksheets(ASSETS_SHEET)
        ws_a.Visible = -1  # xlSheetVisible while building
        ws_a.Activate()
        xl.ActiveWindow.DisplayGridlines = False
        for idx in range(6):
            cell_obj = ws_a.Cells(2 + idx, 2)
            pad = 2.5
            side = min(cell_obj.Width, cell_obj.Height) - 2 * pad
            left = cell_obj.Left + (cell_obj.Width - side) / 2.0
            top = cell_obj.Top + (cell_obj.Height - side) / 2.0
            img_path = (ASSETS_DIR / slug / f"stage_{idx}.png").resolve()
            shp = ws_a.Shapes.AddPicture(
                Filename=str(img_path), LinkToFile=False, SaveWithDocument=True,
                Left=left, Top=top, Width=side, Height=side
            )
            shp.Placement = 1  # xlMoveAndSize
            shp.Line.Visible = False

        # Ensure gridlines off on every visible sheet
        for ws in wb.Worksheets:
            if ws.Name not in (ASSETS_SHEET, CALC_SHEET):
                ws.Activate()
                xl.ActiveWindow.DisplayGridlines = False

        # 2. Add crisp Form Control Checkboxes linked to `;;;`-hidden boolean cells
        cb_count = 0
        for sheet_name, coords in meta["checkboxes"].items():
            if not coords:
                continue
            ws = wb.Worksheets(sheet_name)
            ws.Activate()
            cbs = ws.CheckBoxes()
            for (r, c) in coords:
                cell_obj = ws.Cells(r + 1, c + 1)
                was_checked = (cell_obj.Value is True)
                # Center the 11.5pt square checkbox cleanly inside the cell
                cb_w, cb_h = 13.5, 13.5
                left = cell_obj.Left + (cell_obj.Width - 11.5) / 2.0
                top = cell_obj.Top + (cell_obj.Height - 13.0) / 2.0
                cb = cbs.Add(left, top, cb_w, cb_h)
                cb.Characters.Text = ""
                cb.LinkedCell = cell_obj.Address
                cb.Value = 1 if was_checked else -4146  # xlOn=1, xlOff=-4146
                cb.Display3DShading = False
                cb.Placement = 1  # xlMoveAndSize
                cb_count += 1

        # 3. Create 31 Workbook-level Named Ranges (`Anim_Day01`..`Anim_Day31`) + paste Linked Pictures
        src_anchor = ws_a.Range("B2")
        ws_tr = wb.Worksheets(meta["tracker_sheet"])
        ws_tr.Activate()
        for item in meta["day_anims"]:
            wb.Names.Add(Name=item["name"], RefersTo=item["refers_to"])
            dst = ws_tr.Range(ws_tr.Cells(item["r1"] + 1, item["c1"] + 1),
                              ws_tr.Cells(item["r2"] + 1, item["c2"] + 1))
            paste_linked_picture(xl, src_anchor, ws_tr, dst, f"={item['name']}", align_bottom=True)

        # 4. Paste static Linked Pictures (Hero Grown icon, 6 Guide Stage Previews, Yearly Goals icon)
        for sp in meta["static_pics"]:
            ws_s = wb.Worksheets(sp["sheet"])
            ws_s.Activate()
            dst = ws_s.Range(ws_s.Cells(sp["r1"] + 1, sp["c1"] + 1),
                             ws_s.Cells(sp["r2"] + 1, sp["c2"] + 1))
            paste_linked_picture(xl, src_anchor, ws_s, dst, sp["formula"], align_bottom=False)

        # 5. Force full recalculation while restoring automatic calc + ScreenUpdating
        xl.Calculation = -4105  # xlCalculationAutomatic
        xl.ScreenUpdating = True
        xl.CalculateFullRebuild()
        time.sleep(0.5)

        # Hide `_Assets` & `_Calc` cleanly (xlSheetHidden = 0 so users can Unhide `_Assets` to customize icons!)
        ws_a.Visible = 0
        wb.Worksheets(CALC_SHEET).Visible = 0

        # Select clean cell A1 on every visible tab & land on Welcome Screen (`📖 Hướng Dẫn`)
        for ws in wb.Worksheets:
            if ws.Visible == -1:
                ws.Activate()
                ws.Range("A1").Select()
        wb.Worksheets(GUIDE_SHEET).Activate()

        # Save as pure `.xlsx` (FileFormat=51 — ZERO VBA / ZERO macro popups!)
        OFFLINE_DIR.mkdir(parents=True, exist_ok=True)
        wb.SaveAs(str(final_path.resolve()), FileFormat=51)
        print(f"  ✓ Compiled {final_path.name}  ({final_path.stat().st_size / 1024:.1f} KB, "
              f"checkboxes={cb_count}, linked_pics={len(meta['day_anims']) + len(meta['static_pics'])})",
              flush=True)

        # 6. Export crisp high-res PNG previews directly from the compiled offline `.xlsx`
        for cap in meta["captures"]:
            ws_c = wb.Worksheets(cap["sheet"])
            sz = grab_range_png(ws_c, cap["range"], PREVIEWS_DIR / cap["out"])
            print(f"      preview: {cap['out']}  ({sz[0]}x{sz[1]})", flush=True)
    finally:
        xl.CutCopyMode = False
        wb.Close(False)


def main():
    manifests = build_all_base_tier_a()
    print("\nCompiling 6 Tier-A Universal Offline `.xlsx` files via Excel COM...", flush=True)
    xl = win32.DispatchEx("Excel.Application")
    xl.Visible = False
    xl.DisplayAlerts = False
    try:
        for meta in manifests:
            enhance_one(xl, meta)
    finally:
        xl.Quit()
    print("\nAll 6 Tier-A Universal Offline workbooks compiled & screenshotted!", flush=True)


if __name__ == "__main__":
    main()
