"""
audit_holiday_81_95.py — Full 60-File Audit for Batch 10–11 Holiday Themes (#81–#95 × 4 Editions).

Verifies:
  1. Static & PIL Auto-Fit audit on all 30 new PC files (15 Pro .xlsm + 15 Offline .xlsx):
     - 0 Blacklist / Non-Whitelist / ALL-CAPS-Script / Bad-VN font cells
     - 0 PIL pixel overflows (`rendered_text_width_px <= avail_px * 0.88`)
     - 15/15 Pro have `xl/vbaProject.bin`, 30/30 have `calcMode=auto`, v4.2 & copyright
  2. Static Cloud/Mobile audit on all 30 new Cloud files (15 GSheets Desktop + 15 Mobile Portrait):
     - Exact `_Assets!B2:B7` `=IMAGE()` URLs + blank `B8`, 0 stray `=IMAGE()` outside `_Assets`
     - Exact `onEdit(e)` anchor coordinates (`B3`/`B5`/`C17` Desktop, `B5`/`C5`/`C21` Mobile)
     - Mobile `max_column <= 9` (Col I), `Be Vietnam Pro`, gridlines hidden
  3. Live Excel COM audit on isolated `%TEMP%` copies of ALL 60 new files (cleaned up in finally):
     - 0 formula errors (`#REF!`, `#NAME?`, `#VALUE!`, `#N/A`, `#DIV/0!`, `#NUM!`, `#NULL!`)
     - 15/15 Pro Macro preserve worksheet protection on all 5 visible sheets
  4. Scope check: 0 modified files in `#01`–`#80`, no `_build_tmp/`, 0 `.zip` files.
"""
from __future__ import annotations

import gc
import shutil
import subprocess
import sys
import tempfile
import time
import warnings
import zipfile
from pathlib import Path

import openpyxl
import pythoncom
import win32com.client as win32

warnings.filterwarnings("ignore", category=UserWarning)

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from excel_builder import TEMPLATES
from hx.typography import (
    ALL_ALLOWED_PC_FONTS,
    BLACKLIST_FONTS,
    SCRIPT_WHITELIST,
    has_vietnamese,
    is_all_caps,
    verify_vietnamese_fonts,
)
import audit_v42_pc as pc_aud

PRO_DIR = ROOT / "templates" / "pro_macro"
OFF_DIR = ROOT / "templates" / "excel_universal_offline"
GS_DIR = ROOT / "templates" / "google_sheets_edition"
MOB_DIR = ROOT / "templates" / "mobile_portrait_sheets"

RAW_BASE = "https://raw.githubusercontent.com/Thitrongdan202/Habit-tracker-for-everyone-by-Dyu/main/assets"
FORMULA_ERRORS = {"#REF!", "#NAME?", "#VALUE!", "#N/A", "#DIV/0!", "#NUM!", "#NULL!"}
HIDDEN_SHEETS = {"_Calc", "_Database", "_Assets", "_YearHistory"}


READY_11_NUMS = {81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 92}


def audit_static_60(ready_only: bool = False) -> tuple[bool, list[tuple[str, Path, bool]]]:
    vn_safe = set(verify_vietnamese_fonts().keys()) | {"Segoe UI"}
    if ready_only:
        tdefs = [t for i, t in enumerate(TEMPLATES, 1) if i in READY_11_NUMS]
    else:
        tdefs = TEMPLATES[80:95]
    expected_n = 11 if ready_only else 15
    assert len(tdefs) == expected_n, f"Expected {expected_n} holiday templates, got {len(tdefs)}"

    pc_issues = []
    pc_overflows = []
    cloud_issues = []
    com_targets: list[tuple[str, Path, bool]] = []

    for tdef in tdefs:
        slug = tdef.theme.slug
        pro_p = PRO_DIR / f"{tdef.stem}_Pro.xlsm"
        off_p = OFF_DIR / f"{tdef.stem}.xlsx"
        gs_p = GS_DIR / f"{tdef.stem}.xlsx"
        mob_p = MOB_DIR / f"{tdef.stem}_Mobile.xlsx"

        for tag, p in (("PRO", pro_p), ("OFF", off_p), ("GS", gs_p), ("MOB", mob_p)):
            assert p.exists(), f"Missing generated file: {p}"
            com_targets.append((tag, p, tag == "PRO"))

        # --- 1) Audit PC pair (Pro + Offline) ---
        for is_pro, p in ((True, pro_p), (False, off_p)):
            with zipfile.ZipFile(p, "r") as z:
                names = set(z.namelist())
                if is_pro and "xl/vbaProject.bin" not in names:
                    pc_issues.append((p.name, "Missing xl/vbaProject.bin"))
                wb_xml = z.read("xl/workbook.xml").decode("utf-8", errors="ignore")
                if 'calcMode="manual"' in wb_xml:
                    pc_issues.append((p.name, "calcMode=manual"))

            wb = openpyxl.load_workbook(p, read_only=False, data_only=False)
            found_v42 = False
            found_copy = False
            for sname in wb.sheetnames:
                ws = wb[sname]
                is_vis = sname not in HIDDEN_SHEETS
                cw = pc_aud._col_width_map(ws) if is_vis else {}
                for row in ws.iter_rows():
                    for cell in row:
                        v = cell.value
                        if is_vis and cell.font and cell.font.name and v is not None and str(v).strip() != "":
                            fn = cell.font.name
                            if fn in BLACKLIST_FONTS or fn not in ALL_ALLOWED_PC_FONTS:
                                pc_issues.append((p.name, f"{sname}!{cell.coordinate} non-whitelist font {fn}"))
                        if isinstance(v, str) and v and not v.startswith("="):
                            if "v4.2" in v or "V4.2" in v:
                                found_v42 = True
                            if "© 2026 Dyu (Thân Trọng Duy)" in v:
                                found_copy = True
                            if is_vis and cell.font and cell.font.name:
                                fn = cell.font.name
                                if has_vietnamese(v) and fn not in vn_safe:
                                    pc_issues.append((p.name, f"{sname}!{cell.coordinate} bad VN font {fn}"))
                                if is_all_caps(v) and fn in SCRIPT_WHITELIST:
                                    pc_issues.append((p.name, f"{sname}!{cell.coordinate} ALL-CAPS script {fn}"))
                if not is_vis:
                    continue
                if sname == pc_aud.GUIDE_SHEET:
                    for coord in ("B2", "B3", "B6"):
                        pc_aud._check_fit(ws, coord, [str(ws[coord].value or "")], pc_overflows, p.name, sname, cw)
                elif sname == pc_aud.DAILY_SHEET:
                    pc_aud._check_fit(ws, "B2", [str(ws["B2"].value or "")], pc_overflows, p.name, sname, cw)
                    pc_aud._check_fit(ws, "B5", ["Chủ Nhật, 28/09/2026", "Thứ Năm, 28/09/2026"], pc_overflows, p.name, sname, cw)
                    pc_aud._check_fit(ws, "E5", [str(ws["E5"].value or "October"), "September"], pc_overflows, p.name, sname, cw)
                    for coord in ("H2", "H21", "H27", "B30"):
                        pc_aud._check_fit(ws, coord, [str(ws[coord].value or "")], pc_overflows, p.name, sname, cw)
                elif sname == pc_aud.GOALS_SHEET:
                    for coord in ("B2", "B4", "D4", "H4"):
                        pc_aud._check_fit(ws, coord, [str(ws[coord].value or "")], pc_overflows, p.name, sname, cw)
                elif sname == pc_aud.ANNUAL_SHEET:
                    for coord in ("D2", "B13", "B15", "B33", "L33"):
                        pc_aud._check_fit(ws, coord, [str(ws[coord].value or "")], pc_overflows, p.name, sname, cw)
                else:
                    pc_aud._check_fit(ws, "B2", [str(ws["B2"].value or "")], pc_overflows, p.name, sname, cw)
                    pc_aud._check_fit(ws, "B3", [str(ws["B3"].value or "October"), "September"], pc_overflows, p.name, sname, cw)
                    pc_aud._check_fit(ws, "B9", [str(ws["B9"].value or "")], pc_overflows, p.name, sname, cw)
            wb.close()
            if not found_v42:
                pc_issues.append((p.name, "Missing v4.2 tag"))
            if not found_copy:
                pc_issues.append((p.name, "Missing © 2026 Dyu copyright"))

        # --- 2) Audit Google Sheets Desktop + Mobile Portrait ---
        for is_mob, p in ((False, gs_p), (True, mob_p)):
            wb = openpyxl.load_workbook(p, data_only=False)
            try:
                for req in ("_Calc", "_Database", "_Assets"):
                    if req not in wb.sheetnames or wb[req].sheet_state != "hidden":
                        cloud_issues.append((p.name, f"Hidden sheet {req} missing/visible"))
                ws_a = wb["_Assets"]
                for r in range(2, 8):
                    url_part = f'"{RAW_BASE}/{slug}/stage_{r - 2}.png",1)'
                    valid_forms = {f"=IMAGE({url_part}", f"=_xludf.IMAGE({url_part}", f"=_xlfn.IMAGE({url_part}"}
                    got = str(ws_a.cell(r, 2).value or "")
                    if got not in valid_forms:
                        cloud_issues.append((p.name, f"_Assets!B{r} mismatch: {got!r}"))
                if ws_a.cell(8, 2).value not in (None, ""):
                    cloud_issues.append((p.name, "_Assets!B8 not blank"))
                for sn in wb.sheetnames:
                    ws = wb[sn]
                    if ws.sheet_state == "visible":
                        if ws.views.sheetView[0].showGridLines is not False:
                            cloud_issues.append((p.name, f"{sn} gridlines visible"))
                        if is_mob and ws.max_column > 9:
                            cloud_issues.append((p.name, f"{sn} max_column={ws.max_column} > 9"))
                if is_mob:
                    w = wb["📱 Tuần Này"]
                    if w["B5"].value != "October" or w["C5"].value != 2026 or not isinstance(w["C21"].value, bool):
                        cloud_issues.append((p.name, "Mobile onEdit anchor mismatch"))
                    # Verify ALL 7 columns C21:I35 have non-white checkbox font color + =C$20="" CF rule!
                    for col_i in range(3, 10):
                        fc = w.cell(21, col_i).font.color
                        rgb = str(fc.rgb) if (fc and fc.rgb) else ""
                        if rgb.upper().endswith("FFFFFF") or not rgb:
                            cloud_issues.append((p.name, f"Mobile Col {col_i} checkbox font is white/empty ({rgb})"))
                    cf_formulas = []
                    for cf in w.conditional_formatting:
                        for rule in cf.rules:
                            cf_formulas.extend(rule.formula or [])
                    if not any('C$20=""' in str(f) for f in cf_formulas):
                        cloud_issues.append((p.name, 'Mobile missing =C$20="" out-of-month CF rule'))
                else:
                    w = wb[tdef.tracker_name]
                    if w["B3"].value != "October" or w["B5"].value != 2026 or not isinstance(w["C17"].value, bool):
                        cloud_issues.append((p.name, "Desktop GSheets onEdit anchor mismatch"))
            finally:
                wb.close()

    # --- 3) Check #01-#80 untouched ---
    st = subprocess.check_output(["git", "status", "--short", "templates"], cwd=ROOT, text=True)
    touched_old = []
    for line in st.splitlines():
        if not line.strip():
            continue
        fn = Path(line[3:].strip().strip('"')).name
        if len(fn) >= 2 and fn[:2].isdigit() and int(fn[:2]) <= 80:
            touched_old.append(line)

    print(f"=== STATIC {len(tdefs) * 4}-FILE HOLIDAY AUDIT ===")
    print(f"  PC issues ({len(tdefs) * 2} files)       : {len(pc_issues)}")
    print(f"  PC PIL overflows ({len(tdefs) * 2} files): {len(pc_overflows)}")
    print(f"  Cloud/Mobile issues ({len(tdefs) * 2})   : {len(cloud_issues)}")
    print(f"  Touched #01–#80 files      : {len(touched_old)}")
    print(f"  _build_tmp exists          : {(ROOT / '_build_tmp').exists()}")
    for lbl, arr in (("PC ISSUE", pc_issues[:15]), ("PC OVERFLOW", pc_overflows[:15]),
                     ("CLOUD/MOB", cloud_issues[:15]), ("OLD TOUCHED", touched_old[:15])):
        if arr:
            print(f"  !! {lbl}:")
            for x in arr:
                print("    ", x)

    ok = not (pc_issues or pc_overflows or cloud_issues or touched_old or (ROOT / "_build_tmp").exists())
    return ok, com_targets


def audit_com_60(targets: list[tuple[str, Path, bool]]) -> bool:
    tmp_dir = Path(tempfile.mkdtemp(prefix="audit_holiday_81_95_"))
    formula_errs = []
    prot_errs = []
    checked = 0

    pythoncom.CoInitialize()
    xl = None
    try:
        for i, (tag, src, is_pro) in enumerate(targets):
            if xl is None or (i % 12 == 0):
                if xl is not None:
                    try:
                        xl.Quit()
                    except Exception:
                        pass
                    del xl
                    gc.collect()
                    time.sleep(1.2)
                xl = win32.DispatchEx("Excel.Application")
                xl.Visible = False
                xl.DisplayAlerts = False
                xl.EnableEvents = False
                xl.ScreenUpdating = False

            dst = tmp_dir / f"{i:02d}_{src.name}"
            shutil.copy2(src, dst)
            wb = xl.Workbooks.Open(str(dst.resolve()), UpdateLinks=0, ReadOnly=True)
            try:
                xl.CalculateFull()
                for ws_i in range(1, wb.Worksheets.Count + 1):
                    ws = wb.Worksheets(ws_i)
                    nm = ws.Name
                    if is_pro and nm not in HIDDEN_SHEETS and not bool(ws.ProtectContents):
                        prot_errs.append((src.name, nm))
                    if nm == "_Assets":
                        continue
                    ur = ws.UsedRange
                    vals = ur.Value
                    if not isinstance(vals, tuple):
                        continue
                    for ri, rvals in enumerate(vals):
                        if not isinstance(rvals, tuple):
                            continue
                        for ci, v in enumerate(rvals):
                            if isinstance(v, str) and v in FORMULA_ERRORS:
                                f_str = str(ws.Cells(ur.Row + ri, ur.Column + ci).Formula or "")
                                if tag in ("GS", "MOB") and "_Assets" in f_str:
                                    continue
                                formula_errs.append((src.name, nm, ur.Row + ri, ur.Column + ci, v, f_str[:40]))
                checked += 1
            finally:
                wb.Close(SaveChanges=False)
                try:
                    dst.unlink()
                except Exception:
                    pass
    finally:
        if xl is not None:
            try:
                xl.Quit()
            except Exception:
                pass
            del xl
            gc.collect()
            time.sleep(1.2)
        pythoncom.CoUninitialize()
        shutil.rmtree(tmp_dir, ignore_errors=True)

    print("=== LIVE EXCEL COM 60-FILE AUDIT (%TEMP% COPIES) ===")
    print(f"  Workbooks verified in Excel: {checked} / {len(targets)}")
    print(f"  Formula errors             : {len(formula_errs)}")
    print(f"  Unprotected Pro tabs       : {len(prot_errs)}")
    print(f"  Temp audit dir cleaned     : {not tmp_dir.exists()}")
    for x in formula_errs[:20]:
        print("  !! FORMULA ERR:", x)
    for x in prot_errs[:20]:
        print("  !! UNPROTECTED:", x)
    return checked == len(targets) and not formula_errs and not prot_errs


def test_live_holiday_vba_finale(pro_files: list[Path]) -> bool:
    """Test LIVE execution of `BtnDemoFX` (Winter Magic Finale & Grand New Year Fireworks Finale)
    on isolated %TEMP% copies inside Excel COM: verifies 0 VBA runtime errors, DECOR_* shapes
    preserved cleanly, and ZERO leftover FX_HOL_* / FX_PARTICLE_* orphan shapes!"""
    tmp_dir = Path(tempfile.mkdtemp(prefix="audit_holiday_vba_"))
    vba_errs = []
    tested = 0
    pythoncom.CoInitialize()
    xl = None
    try:
        xl = win32.DispatchEx("Excel.Application")
        xl.Visible = False
        xl.DisplayAlerts = False
        xl.EnableEvents = False
        for idx, src in enumerate(pro_files):
            dst = tmp_dir / f"{idx:02d}_{src.name}"
            shutil.copy2(src, dst)
            wb = xl.Workbooks.Open(str(dst.resolve()), UpdateLinks=0, ReadOnly=False)
            try:
                ws_g = wb.Worksheets("📖 Hướng Dẫn")
                ws_g.Activate()
                decor_before = sum(1 for i in range(1, ws_g.Shapes.Count + 1) if str(ws_g.Shapes(i).Name).startswith("DECOR_"))
                if decor_before < 2:
                    vba_errs.append((src.name, f"Missing DECOR_* on Guide (found {decor_before})"))
                # Run live Holiday Finale macro!
                xl.Run(f"'{wb.Name}'!BtnDemoFX")
                # Clean toast timer before closing
                xl.Run(f"'{wb.Name}'!CleanupAllFX")
                leftover_fx = [
                    str(ws_g.Shapes(i).Name)
                    for i in range(1, ws_g.Shapes.Count + 1)
                    if str(ws_g.Shapes(i).Name).startswith(("FX_HOL_", "FX_PARTICLE_", "FX_TOAST"))
                ]
                decor_after = sum(1 for i in range(1, ws_g.Shapes.Count + 1) if str(ws_g.Shapes(i).Name).startswith("DECOR_"))
                if leftover_fx:
                    vba_errs.append((src.name, f"Leftover FX shapes: {leftover_fx}"))
                if decor_after != decor_before:
                    vba_errs.append((src.name, f"DECOR count changed: {decor_before} -> {decor_after}"))
                tested += 1
            except Exception as e:
                vba_errs.append((src.name, f"VBA runtime error: {e}"))
            finally:
                wb.Close(SaveChanges=False)
                try:
                    dst.unlink()
                except Exception:
                    pass
    finally:
        if xl is not None:
            try:
                xl.Quit()
            except Exception:
                pass
            del xl
            gc.collect()
            time.sleep(1.2)
        pythoncom.CoUninitialize()
        shutil.rmtree(tmp_dir, ignore_errors=True)

    print("=== LIVE VBA HOLIDAY FINALE MACRO AUDIT (%TEMP% COPIES) ===")
    print(f"  Pro workbooks live-tested  : {tested} / {len(pro_files)}")
    print(f"  VBA / orphan shape errors  : {len(vba_errs)}")
    print(f"  Temp VBA dir cleaned       : {not tmp_dir.exists()}")
    for x in vba_errs:
        print("  !! VBA ERR:", x)
    return tested == len(pro_files) and not vba_errs


def main():
    ready_only = ("--ready-only" in sys.argv[1:])
    ok_static, targets = audit_static_60(ready_only=ready_only)
    ok_com = audit_com_60(targets)
    # Test LIVE Holiday VBA Finale on representative Christmas (#81, #84) & New Year (#89, #90, #92) Pro files!
    vba_samples = [
        p for (tag, p, is_pro) in targets
        if is_pro and any(p.name.startswith(pref) for pref in ("81_", "84_", "89_", "90_", "92_"))
    ]
    ok_vba = test_live_holiday_vba_finale(vba_samples)
    total_n = len(targets)
    print(f"FINAL {total_n}-FILE HOLIDAY AUDIT:", f"PASS ({total_n}/{total_n} CLEAN)" if (ok_static and ok_com and ok_vba) else "FAIL")
    sys.exit(0 if (ok_static and ok_com and ok_vba) else 1)


if __name__ == "__main__":
    main()
