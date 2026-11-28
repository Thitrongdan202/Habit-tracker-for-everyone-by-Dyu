"""
update_offline_holiday_sprites.py — Fast (~6-10s/file) Excel COM updater for existing
`templates/excel_universal_offline/81..95_*.xlsx` workbooks:
  1. Replaces all 6 embedded sprites (`ASSET_S0..ASSET_S5`) on hidden `_Assets!B2:B7`
     with the newly generated AI kawaii chibi `assets/<slug>/stage_0..5.png` files.
  2. Clears any old `DECOR_*` shapes and mounts the exclusive Holiday corner overlays
     (`add_holiday_decor_overlays`) on all 5 visible tabs.
  3. Runs `xl.CalculateFullRebuild()` so all 54 existing Linked Pictures automatically
     refresh to display the new AI sprites, then saves cleanly!
"""
from __future__ import annotations

import gc
import sys
import time
from pathlib import Path

import pythoncom
import win32com.client as win32

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from excel_builder import TEMPLATES
from excel_com_enhancer import ASSETS_DIR, OFFLINE_OUT_DIR, add_holiday_decor_overlays
from hx.annual import ASSETS_SHEET
from hx.guide import GUIDE_SHEET


def main():
    only = set(sys.argv[1:])
    targets = [t for t in TEMPLATES if (not only or t.short_key in only or t.stem in only)]
    print(f"Fast-updating {len(targets)} Offline .xlsx workbooks (AI sprites + Holiday Decor)...", flush=True)

    pythoncom.CoInitialize()
    xl = None
    try:
        for idx, tdef in enumerate(targets):
            if xl is None or (idx % 5 == 0):
                if xl is not None:
                    try:
                        xl.Quit()
                    except Exception:
                        pass
                    del xl
                    gc.collect()
                    time.sleep(1.0)
                xl = win32.DispatchEx("Excel.Application")
                xl.Visible = False
                xl.DisplayAlerts = False
                xl.EnableEvents = False
                try:
                    xl.EnableAnimations = False
                except Exception:
                    pass

            t0 = time.perf_counter()
            slug = tdef.theme.slug
            p = (OFFLINE_OUT_DIR / f"{tdef.stem}.xlsx").resolve()
            assert p.exists(), f"Missing offline file: {p}"
            wb = xl.Workbooks.Open(str(p), UpdateLinks=0, ReadOnly=False)
            try:
                xl.ScreenUpdating = False
                xl.Calculation = -4135  # xlCalculationManual

                # 1. Replace ASSET_S0..ASSET_S5 on `_Assets!B2:B7`
                ws_a = wb.Worksheets(ASSETS_SHEET)
                ws_a.Visible = -1
                for i_s in range(ws_a.Shapes.Count, 0, -1):
                    nm = str(ws_a.Shapes(i_s).Name or "")
                    if nm.startswith("ASSET_S") or nm.startswith("Picture"):
                        ws_a.Shapes(i_s).Delete()
                for k in range(tdef.theme.num_stages):
                    cell_obj = ws_a.Cells(2 + k, 2)
                    pad = 2.5
                    side = min(cell_obj.Width, cell_obj.Height) - 2 * pad
                    left = cell_obj.Left + (cell_obj.Width - side) / 2.0
                    top = cell_obj.Top + (cell_obj.Height - side) / 2.0
                    img_p = (ASSETS_DIR / slug / f"stage_{k}.png").resolve()
                    shp = ws_a.Shapes.AddPicture(
                        Filename=str(img_p), LinkToFile=False, SaveWithDocument=True,
                        Left=left, Top=top, Width=side, Height=side,
                    )
                    shp.Name = f"ASSET_S{k}"
                    shp.Placement = 1
                    shp.Line.Visible = False
                ws_a.Visible = 0

                # 2. Remove any old DECOR_* shapes across visible sheets
                for ws in wb.Worksheets:
                    for i_s in range(ws.Shapes.Count, 0, -1):
                        if str(ws.Shapes(i_s).Name or "").startswith("DECOR_"):
                            ws.Shapes(i_s).Delete()

                # 3. Recalculate so all 54 Linked Pictures refresh to the new AI sprites
                xl.Calculation = -4105  # xlCalculationAutomatic
                xl.CalculateFullRebuild()

                # 4. Mount Holiday Corner Decorations AFTER CalculateFullRebuild (instant!)
                d_cnt = add_holiday_decor_overlays(wb, {"slug": slug, "tracker_sheet": tdef.tracker_name})

                ws_g = wb.Worksheets(GUIDE_SHEET)
                ws_g.Activate()
                ws_g.Range("A1").Select()
                xl.ScreenUpdating = True
                wb.Save()
                dt = time.perf_counter() - t0
                print(f"  ✓ [offline fast] {p.name} ({p.stat().st_size:,} B, decor={d_cnt}, {dt:.1f}s)", flush=True)
            finally:
                wb.Close(SaveChanges=False)
    finally:
        if xl is not None:
            try:
                xl.Quit()
            except Exception:
                pass
            del xl
            gc.collect()
            time.sleep(1.0)
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    main()
