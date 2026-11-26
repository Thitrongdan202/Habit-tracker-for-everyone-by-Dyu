"""
render_loopy_previews_and_audit.py — Audits all 20 new Loopy workbooks (#61–#70 Desktop & Mobile)
and renders crisp Desktop + Mobile preview PNGs using isolated %TEMP% Excel COM copies
(NEVER modifying the actual `.xlsx` workbooks!).
"""
from __future__ import annotations

import shutil
import sys
import tempfile
import time
from pathlib import Path

import openpyxl
from PIL import Image, ImageGrab
import win32com.client as win32

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from excel_builder import TEMPLATES
from hx.tracker import CALC_SHEET, R_IMG, day_col
from hx.mobile import MOBILE_WEEK_SHEET, MOBILE_CALC_SHEET

GSHEETS_DIR = ROOT / "templates" / "google_sheets_edition"
MOBILE_DIR = ROOT / "templates" / "mobile_portrait_sheets"
ASSETS_DIR = ROOT / "assets"
PREVIEWS_DIR = ROOT / "previews"

LOOPY_KEYS = {
    "61_loopy_red_bow", "62_loopy_taiyaki", "63_loopy_piggy_cafe",
    "64_loopy_sauna_sheep", "65_loopy_honey_bee", "66_loopy_poolside_duck",
    "67_loopy_fluffy_commuter", "68_loopy_panda_study", "69_loopy_ruffle_sleep",
    "70_loopy_hair_roller",
}
RAW_BASE = "https://raw.githubusercontent.com/Thitrongdan202/Habit-tracker-for-everyone-by-Dyu/main/assets"


def audit_workbook(path: Path, slug: str, is_mobile: bool, tracker_name: str) -> list[str]:
    errs: list[str] = []
    wb = openpyxl.load_workbook(path, data_only=False)
    try:
        # 1) Hidden sheets present
        for req in ("_Calc", "_Database", "_Assets"):
            if req not in wb.sheetnames:
                errs.append(f"Missing sheet {req}")
            elif wb[req].sheet_state != "hidden":
                errs.append(f"Sheet {req} not hidden ({wb[req].sheet_state})")

        # 2) _Assets has ONLY 6 unique =IMAGE(...) pointing to main/assets/<slug>/stage_0..5.png
        ws_a = wb["_Assets"]
        img_urls = []
        for r in range(2, 8):
            val = str(ws_a.cell(r, 2).value or "")
            expected = f'=IMAGE("{RAW_BASE}/{slug}/stage_{r - 2}.png",1)'
            if val != expected:
                errs.append(f"_Assets!B{r} mismatch: {val!r} != {expected!r}")
            else:
                img_urls.append(val)
        if len(set(img_urls)) != 6:
            errs.append(f"Expected 6 unique IMAGE URLs in _Assets, got {len(set(img_urls))}")
        if ws_a.cell(8, 2).value not in (None, ""):
            errs.append(f"_Assets!B8 should be blank, got {ws_a.cell(8, 2).value!r}")

        # 3) Check visible sheets: gridlines off, font Be Vietnam Pro, no stray =IMAGE formulas, max_col on mobile
        stray_images = 0
        bad_fonts: set[str] = set()
        min_sz = 999.0
        for name in wb.sheetnames:
            ws = wb[name]
            if ws.sheet_state == "visible":
                if ws.views.sheetView[0].showGridLines is not False:
                    errs.append(f"{name}: showGridLines is not False")
                if is_mobile and ws.max_column > 9:
                    errs.append(f"{name}: Mobile max_column={ws.max_column} > 9 (col I)")
            for row in ws.iter_rows():
                for cell in row:
                    v = cell.value
                    if name != "_Assets" and isinstance(v, str) and v.lstrip().startswith("=") and "IMAGE(" in v.upper():
                        stray_images += 1
                    if ws.sheet_state == "visible" and v not in (None, ""):
                        fn = cell.font.name if cell.font else None
                        fs = cell.font.size if cell.font else None
                        if fn and fn != "Be Vietnam Pro":
                            bad_fonts.add(fn)
                        if fs is not None and fs < min_sz:
                            min_sz = fs
        if stray_images:
            errs.append(f"Found {stray_images} stray =IMAGE() formulas outside _Assets")
        if bad_fonts:
            errs.append(f"Non-Be-Vietnam-Pro fonts found: {sorted(bad_fonts)}")
        min_allowed = 10.0 if is_mobile else 9.0
        if min_sz < min_allowed:
            errs.append(f"Min font size {min_sz} < {min_allowed}")

        # 4) Verify critical onEdit(e) coordinate anchors
        if is_mobile:
            if MOBILE_WEEK_SHEET not in wb.sheetnames:
                errs.append(f"Missing {MOBILE_WEEK_SHEET}")
            else:
                w = wb[MOBILE_WEEK_SHEET]
                if w["B5"].value != "October":
                    errs.append(f"Mobile B5 month != 'October' ({w['B5'].value!r})")
                if w["C5"].value != 2026:
                    errs.append(f"Mobile C5 year != 2026 ({w['C5'].value!r})")
                if not isinstance(w["C21"].value, bool):
                    errs.append(f"Mobile C21 not bool ({w['C21'].value!r})")
        else:
            tr_ws = wb[tracker_name]
            if tr_ws["B3"].value != "October":
                errs.append(f"Desktop B3 month != 'October' ({tr_ws['B3'].value!r})")
            if tr_ws["B5"].value != 2026:
                errs.append(f"Desktop B5 year != 2026 ({tr_ws['B5'].value!r})")
            if not isinstance(tr_ws["C17"].value, bool):
                errs.append(f"Desktop C17 not bool ({tr_ws['C17'].value!r})")
            if "📝 Nhiệm Vụ Ngày" not in wb.sheetnames:
                errs.append("Missing 📝 Nhiệm Vụ Ngày")
            if "🎯 Yearly Goals & Habits" not in wb.sheetnames:
                errs.append("Missing 🎯 Yearly Goals & Habits")
    finally:
        wb.close()
    return errs


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


def _overlay_sprite(ws, cell_rng, img_path: Path, align_bottom: bool = False):
    pad_x = 2.0 if align_bottom else 5.0
    pad_y = 2.0 if align_bottom else 5.0
    w = _com_retry(lambda: cell_rng.Width)
    h = _com_retry(lambda: cell_rng.Height)
    l0 = _com_retry(lambda: cell_rng.Left)
    t0 = _com_retry(lambda: cell_rng.Top)
    side = max(12.0, min(w - 2 * pad_x, h - 2 * pad_y))
    left = l0 + (w - side) / 2.0
    top = (t0 + h - side - 2.0) if align_bottom else (t0 + (h - side) / 2.0)
    shp = _com_retry(lambda: ws.Shapes.AddPicture(
        Filename=str(img_path.resolve()), LinkToFile=False, SaveWithDocument=True,
        Left=left, Top=top, Width=side, Height=side,
    ))
    _com_retry(lambda: setattr(shp.Line, "Visible", False))
    return shp


def _grab_png(ws, rng_str: str, out_path: Path, retries: int = 6):
    _com_retry(lambda: ws.Activate())
    _com_retry(lambda: ws.Range("A1").Select())
    time.sleep(0.20)
    for attempt in range(retries):
        try:
            ws.Range(rng_str).CopyPicture(Appearance=1, Format=2)
            time.sleep(0.32)
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


def _check_formula_errors_com(wb) -> list[str]:
    bad_vals = {"#REF!", "#NAME?", "#VALUE!", "#DIV/0!", "#N/A", "#NUM!", "#NULL!"}
    found = []
    for ws in wb.Worksheets:
        if ws.Name == "_Assets":
            continue  # Excel desktop does not evaluate web =IMAGE() offline without M365 web fetch
        used = ws.UsedRange
        vals = used.Value
        if vals is None:
            continue
        if not isinstance(vals, tuple):
            vals = ((vals,),)
        for r_i, row in enumerate(vals, start=1):
            if not isinstance(row, tuple):
                row = (row,)
            for c_i, v in enumerate(row, start=1):
                # Ignore #VALUE!/#NAME? solely on INDEX(_Assets!...) display cells if Excel COM returns error for web IMAGE
                if isinstance(v, str) and v in bad_vals:
                    f_str = str(ws.Cells(used.Row + r_i - 1, used.Column + c_i - 1).Formula or "")
                    if "_Assets" not in f_str:
                        found.append(f"{ws.Name}!R{used.Row + r_i - 1}C{used.Column + c_i - 1}={v} ({f_str[:40]})")
    return found


def render_desktop_preview(xl, tdef):
    import re
    src = GSHEETS_DIR / f"{tdef.stem}.xlsx"
    tmp_p = Path(tempfile.gettempdir()) / f"render_{tdef.short_key}_desk.xlsx"
    shutil.copy2(src, tmp_p)
    wb = _com_retry(lambda: xl.Workbooks.Open(str(tmp_p.resolve())))
    try:
        _com_retry(lambda: xl.CalculateFullRebuild())
        time.sleep(0.35)
        ferrs = _check_formula_errors_com(wb)
        ws_tr = wb.Worksheets(tdef.tracker_name)
        ws_calc = wb.Worksheets(CALC_SHEET)

        # Find every cell referencing INDEX(_Assets!...) on the tracker (31 daily cells + Hero box)
        # and overlay the exact computed stage PNG on the %TEMP% copy ONLY!
        seen_areas: set[str] = set()
        for rr in range(1, 20):
            for cc in range(1, 42):
                f_txt = str(_com_retry(lambda r=rr, c=cc: ws_tr.Cells(r, c).Formula) or "")
                if "INDEX(_Assets!" in f_txt:
                    ma = _com_retry(lambda r=rr, c=cc: ws_tr.Cells(r, c).MergeArea)
                    addr_key = _com_retry(lambda m=ma: m.Address)
                    if addr_key in seen_areas:
                        continue
                    seen_areas.add(addr_key)
                    is_daily = (rr == R_IMG + 1 and 3 <= cc <= 33)
                    m = re.search(r"_Calc!\$?([A-Z]+)\$?(\d+)", f_txt)
                    stg = 1
                    if m:
                        raw_v = _com_retry(lambda a=f"{m.group(1)}{m.group(2)}": ws_calc.Range(a).Value)
                        if isinstance(raw_v, (int, float)):
                            stg = int(raw_v)
                    _com_retry(lambda r=rr, c=cc: setattr(ws_tr.Cells(r, c), "Value", ""))
                    if 1 <= stg <= 6:
                        _overlay_sprite(
                            ws_tr, ma,
                            ASSETS_DIR / tdef.theme.slug / f"stage_{stg - 1}.png",
                            align_bottom=is_daily,
                        )

        _com_retry(lambda: ws_tr.Activate())
        _com_retry(lambda: setattr(xl.ActiveWindow, "DisplayGridlines", False))
        out_p = PREVIEWS_DIR / f"{tdef.short_key}_tracker.png"
        sz = _grab_png(ws_tr, tdef.tracker_capture_range, out_p)
        return sz, ferrs
    finally:
        _com_retry(lambda: wb.Close(SaveChanges=False))
        tmp_p.unlink(missing_ok=True)


def render_mobile_preview(xl, tdef):
    src = MOBILE_DIR / f"{tdef.stem}_Mobile.xlsx"
    tmp_p = Path(tempfile.gettempdir()) / f"render_{tdef.short_key}_mob.xlsx"
    shutil.copy2(src, tmp_p)
    wb = _com_retry(lambda: xl.Workbooks.Open(str(tmp_p.resolve())))
    try:
        _com_retry(lambda: xl.CalculateFullRebuild())
        time.sleep(0.35)
        ferrs = _check_formula_errors_com(wb)
        ws_wk = wb.Worksheets(MOBILE_WEEK_SHEET)
        ws_calc = wb.Worksheets(MOBILE_CALC_SHEET)

        hero_stg = max(1, min(6, int(_com_retry(lambda: ws_calc.Range("E12").Value) or 1)))
        _com_retry(lambda: setattr(ws_wk.Range("F9"), "Value", ""))
        _overlay_sprite(ws_wk, ws_wk.Range("F9:I12"), ASSETS_DIR / tdef.theme.slug / f"stage_{hero_stg - 1}.png")

        for dow in range(7):
            c_xl = 3 + dow
            day_val = _com_retry(lambda c=c_xl: ws_wk.Cells(20, c).Value)
            _com_retry(lambda c=c_xl: setattr(ws_wk.Cells(15, c), "Value", ""))
            if day_val is not None and str(day_val).strip() != "":
                stg = max(1, min(6, int(_com_retry(lambda d=dow: ws_calc.Cells(1, 7 + d).Value) or 1)))
                _overlay_sprite(ws_wk, ws_wk.Cells(15, c_xl),
                                ASSETS_DIR / tdef.theme.slug / f"stage_{stg - 1}.png", align_bottom=True)

        _com_retry(lambda: ws_wk.Activate())
        _com_retry(lambda: setattr(xl.ActiveWindow, "DisplayGridlines", False))
        out_p = PREVIEWS_DIR / f"mobile_{tdef.short_key}.png"
        sz = _grab_png(ws_wk, "A1:J36", out_p)
        return sz, ferrs
    finally:
        _com_retry(lambda: wb.Close(SaveChanges=False))
        tmp_p.unlink(missing_ok=True)


def main():
    loopy_tdefs = [t for t in TEMPLATES if t.short_key in LOOPY_KEYS]
    assert len(loopy_tdefs) == 10, f"Expected 10 Loopy templates, got {len(loopy_tdefs)}"

    print("=== STEP 1: OPENPYXL STRUCTURAL AUDIT (20 WORKBOOKS) ===", flush=True)
    total_errs = 0
    for tdef in loopy_tdefs:
        dp = GSHEETS_DIR / f"{tdef.stem}.xlsx"
        mp = MOBILE_DIR / f"{tdef.stem}_Mobile.xlsx"
        d_errs = audit_workbook(dp, tdef.theme.slug, is_mobile=False, tracker_name=tdef.tracker_name)
        m_errs = audit_workbook(mp, tdef.theme.slug, is_mobile=True, tracker_name=tdef.tracker_name)
        total_errs += len(d_errs) + len(m_errs)
        print(f"  [{tdef.short_key}] Desktop: {'OK' if not d_errs else d_errs} | Mobile: {'OK' if not m_errs else m_errs}", flush=True)
    if total_errs:
        raise SystemExit(f"Audit failed with {total_errs} errors!")
    print("ALL 20 WORKBOOKS PASSED STRUCTURAL AUDIT (0 ERRORS)!\n", flush=True)

    print("=== STEP 2: ISOLATED %TEMP% EXCEL COM FORMULA CHECK + 20 PREVIEW PNGS ===", flush=True)
    xl = None
    try:
        for idx, tdef in enumerate(loopy_tdefs):
            if idx % 5 == 0:
                _quit_excel(xl)
                xl = _new_excel()
            d_sz, d_ferrs = render_desktop_preview(xl, tdef)
            m_sz, m_ferrs = render_mobile_preview(xl, tdef)
            print(f"  ✓ [{tdef.short_key}] Desktop {d_sz[0]}x{d_sz[1]} (errs={len(d_ferrs)}) | Mobile {m_sz[0]}x{m_sz[1]} (errs={len(m_ferrs)})", flush=True)
            if d_ferrs:
                print(f"      Desktop formula errs: {d_ferrs[:5]}", flush=True)
            if m_ferrs:
                print(f"      Mobile formula errs: {m_ferrs[:5]}", flush=True)
    finally:
        _quit_excel(xl)
    print("ALL 20 PREVIEWS RENDERED CLEANLY!", flush=True)


if __name__ == "__main__":
    main()
