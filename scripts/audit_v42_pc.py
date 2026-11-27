"""
audit_v42_pc.py — Comprehensive Release v4.2 Audit across all 160 PC workbooks.

Checks:
  1. Static XML + openpyxl read-only scan across ALL 160 PC files:
     - 0 leftover legacy version strings (v2.1..v4.1) on visible & hidden sheets
     - 160/160 copyright `© 2026 Dyu (Thân Trọng Duy)` & `v4.2`
     - 0 Vietnamese text cells assigned a non-VN-certified font
     - 160/160 automatic calculation mode (never stuck in `calcMode="manual"`)
     - 80/80 Pro Macro `.xlsm` preserve `xl/vbaProject.bin`
  2. Strict Git scope check: 0 changed files in Google Sheets, Mobile, assets, previews.
  3. Optional `--com-spotcheck` on 5 representative themes (#01, #04, #19, #61, #80)
     across BOTH Pro Macro & Universal Offline (on temp copies):
     - 0 Excel formula error cells (`#REF!`, `#NAME?`, `#VALUE!`, `#N/A`, `#DIV/0!`)
     - Worksheet protection intact on Pro Macro
     - Exports 5-sheet PNG previews into `_build_tmp/v42_spotcheck_png/` for visual QA.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import warnings
import zipfile
from pathlib import Path

import openpyxl

warnings.filterwarnings("ignore", category=UserWarning)

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from excel_builder import TEMPLATES
from hx.typography import THEME_TYPOGRAPHY, has_vietnamese, verify_vietnamese_fonts

PRO_DIR = ROOT / "templates" / "pro_macro"
OFF_DIR = ROOT / "templates" / "excel_universal_offline"

LEGACY_VER_RE = re.compile(r"\b[vV](?:2\.1|3\.\d+|4\.[01])\b")
FORMULA_ERRORS = {"#REF!", "#NAME?", "#VALUE!", "#N/A", "#DIV/0!", "#NUM!", "#NULL!"}
VISIBLE_HIDDEN = {"_Calc", "_Database", "_Assets", "_YearHistory"}


def run_static_audit() -> bool:
    vn_report = verify_vietnamese_fonts()
    vn_safe_fonts = set(vn_report.keys()) | {"Be Vietnam Pro", "Arial", "Tahoma", "Verdana", "Segoe UI Symbol", "Segoe UI Emoji"}

    pro_files = sorted(PRO_DIR.glob("[0-9][0-9]_*.xlsm"))
    off_files = sorted(OFF_DIR.glob("[0-9][0-9]_*.xlsx"))
    assert len(pro_files) == 80, f"Expected 80 pro_macro files, got {len(pro_files)}"
    assert len(off_files) == 80, f"Expected 80 offline files, got {len(off_files)}"

    legacy_hits = []
    missing_v42 = []
    missing_copy = []
    bad_vn_font = []
    manual_calc = []
    missing_vba = []

    all_files = [(True, p) for p in pro_files] + [(False, p) for p in off_files]
    for is_pro, p in all_files:
        # Zip XML checks: vbaProject.bin & calcMode
        with zipfile.ZipFile(p, "r") as z:
            names = set(z.namelist())
            if is_pro and "xl/vbaProject.bin" not in names:
                missing_vba.append(p.name)
            wb_xml = z.read("xl/workbook.xml").decode("utf-8", errors="ignore")
            if 'calcMode="manual"' in wb_xml:
                manual_calc.append(p.name)

        wb = openpyxl.load_workbook(p, read_only=False, data_only=False)
        found_v42 = False
        found_copy = False
        for sname in wb.sheetnames:
            ws = wb[sname]
            is_visible = sname not in VISIBLE_HIDDEN
            for row in ws.iter_rows():
                for cell in row:
                    val = cell.value
                    if not isinstance(val, str) or not val:
                        continue
                    if not val.startswith("="):
                        if LEGACY_VER_RE.search(val):
                            legacy_hits.append((p.name, sname, cell.coordinate, val[:100]))
                        if "v4.2" in val or "V4.2" in val:
                            found_v42 = True
                        if "© 2026 Dyu (Thân Trọng Duy)" in val:
                            found_copy = True
                        if is_visible and has_vietnamese(val):
                            fname = cell.font.name if cell.font else None
                            if fname and fname not in vn_safe_fonts:
                                bad_vn_font.append((p.name, sname, cell.coordinate, fname, val[:60]))
        wb.close()

        if not found_v42:
            missing_v42.append(p.name)
        if not found_copy:
            missing_copy.append(p.name)

    # Git scope check
    out = subprocess.check_output(
        ["git", "status", "--short",
         "templates/google_sheets_edition", "templates/mobile_portrait_sheets", "assets", "previews"],
        cwd=ROOT, text=True,
    ).strip()
    untouched_violations = [line for line in out.splitlines() if line.strip()]

    print("=== STATIC 160-FILE AUDIT SUMMARY ===")
    print(f"  Files audited        : {len(all_files)} (80 Pro + 80 Offline)")
    print(f"  Legacy version hits  : {len(legacy_hits)}")
    print(f"  Missing v4.2 tag     : {len(missing_v42)}")
    print(f"  Missing copyright    : {len(missing_copy)}")
    print(f"  Bad VN font cells    : {len(bad_vn_font)}")
    print(f"  Manual calcMode      : {len(manual_calc)}")
    print(f"  Missing VBA binary   : {len(missing_vba)}")
    print(f"  Out-of-scope changes : {len(untouched_violations)}")

    for label, items in [
        ("LEGACY VERSION", legacy_hits[:20]),
        ("MISSING v4.2", missing_v42[:20]),
        ("MISSING COPYRIGHT", missing_copy[:20]),
        ("BAD VN FONT", bad_vn_font[:20]),
        ("MANUAL CALC", manual_calc[:20]),
        ("MISSING VBA", missing_vba[:20]),
        ("OUT-OF-SCOPE GIT", untouched_violations[:20]),
    ]:
        if items:
            print(f"  !! {label}:")
            for it in items:
                print("    ", it)

    ok = not (legacy_hits or missing_v42 or missing_copy or bad_vn_font or manual_calc or missing_vba or untouched_violations)
    print("RESULT:", "PASS (100% CLEAN)" if ok else "FAIL")
    return ok


def run_com_spotcheck(ids: list[int]) -> bool:
    import pythoncom
    import apply_v42_typography_pc as u

    tmp_copy = ROOT / "_build_tmp" / "v42_spotcheck_copy"
    png_out = ROOT / "_build_tmp" / "v42_spotcheck_png"
    tmp_copy.mkdir(parents=True, exist_ok=True)
    png_out.mkdir(parents=True, exist_ok=True)

    pro_map = {int(p.name[:2]): p for p in sorted(PRO_DIR.glob("[0-9][0-9]_*.xlsm"))}
    off_map = {int(p.name[:2]): p for p in sorted(OFF_DIR.glob("[0-9][0-9]_*.xlsx"))}

    pythoncom.CoInitialize()
    xl = u._open_excel()
    formula_errs = []
    prot_errs = []

    try:
        for idx in ids:
            slug = TEMPLATES[idx - 1].theme.slug
            for is_pro, src in ((True, pro_map[idx]), (False, off_map[idx])):
                ed = "pro" if is_pro else "off"
                dst = tmp_copy / src.name
                shutil.copy2(src, dst)
                wb = xl.Workbooks.Open(str(dst.resolve()), UpdateLinks=0, ReadOnly=False)
                try:
                    xl.CalculateFull()
                    tracker_ws = None
                    for i in range(1, wb.Worksheets.Count + 1):
                        ws = wb.Worksheets(i)
                        nm = ws.Name
                        if nm not in VISIBLE_HIDDEN:
                            if is_pro and not bool(ws.ProtectContents):
                                prot_errs.append((src.name, nm))
                            if nm not in (u.GUIDE_SHEET, u.DAILY_SHEET, u.GOALS_SHEET, u.ANNUAL_SHEET):
                                tracker_ws = ws
                        # Check formula errors in UsedRange
                        ur = ws.UsedRange
                        vals = ur.Value
                        if isinstance(vals, tuple):
                            for ri, rvals in enumerate(vals):
                                if not isinstance(rvals, tuple):
                                    continue
                                for ci, v in enumerate(rvals):
                                    if isinstance(v, str) and v in FORMULA_ERRORS:
                                        formula_errs.append((src.name, nm, ur.Row + ri, ur.Column + ci, v))

                    # Export crisp PNGs for visual inspection (all 5 sheets on Pro, Tracker + Guide on Offline)
                    xl.ScreenUpdating = True
                    p_tag = f"{idx:02d}_{slug}"
                    if tracker_ws is not None:
                        u._export_sheet_png(tracker_ws, "A1:AN38", png_out / f"{p_tag}_{ed}_01_tracker.png")
                    ws_g = wb.Worksheets(u.GUIDE_SHEET)
                    g_lr = ws_g.UsedRange.Row + ws_g.UsedRange.Rows.Count
                    g_lc = "J" if ws_g.UsedRange.Columns.Count >= 9 else ("I" if ws_g.UsedRange.Columns.Count == 8 else "H")
                    u._export_sheet_png(ws_g, f"A1:{g_lc}{min(42, g_lr + 1)}", png_out / f"{p_tag}_{ed}_02_guide.png")
                    if is_pro:
                        u._export_sheet_png(wb.Worksheets(u.DAILY_SHEET), "A1:I34", png_out / f"{p_tag}_{ed}_03_daily.png")
                        u._export_sheet_png(wb.Worksheets(u.GOALS_SHEET), "A1:J26", png_out / f"{p_tag}_{ed}_04_goals.png")
                        u._export_sheet_png(wb.Worksheets(u.ANNUAL_SHEET), "A1:O43", png_out / f"{p_tag}_{ed}_05_annual.png")
                    xl.ScreenUpdating = False
                    print(f"  SPOTCHECK OK: #{idx:02d} {ed.upper()} ({slug})", flush=True)
                finally:
                    wb.Close(SaveChanges=False)
    finally:
        u._close_excel(xl)
        pythoncom.CoUninitialize()

    print("=== LIVE EXCEL COM SPOT-CHECK SUMMARY ===")
    print(f"  Themes checked       : {ids} (both Pro & Offline = {len(ids)*2} workbooks)")
    print(f"  Formula errors       : {len(formula_errs)}")
    print(f"  Unprotected Pro tabs : {len(prot_errs)}")
    for it in formula_errs[:20]:
        print("  !! FORMULA ERR:", it)
    for it in prot_errs[:20]:
        print("  !! UNPROTECTED PRO:", it)
    return not (formula_errs or prot_errs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--com-spotcheck", action="store_true")
    ap.add_argument("--ids", type=str, default="1,4,19,61,80")
    args = ap.parse_args()

    ok1 = run_static_audit()
    ok2 = True
    if args.com_spotcheck:
        ids = [int(x.strip()) for x in args.ids.split(",") if x.strip()]
        ok2 = run_com_spotcheck(ids)
    sys.exit(0 if (ok1 and ok2) else 1)


if __name__ == "__main__":
    main()
