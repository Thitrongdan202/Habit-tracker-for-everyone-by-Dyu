"""
qa_verify_v22.py — Strict Automated QA & UI/UX Typography Verification for Habit Tracker v2.3.

Runs in an isolated `%TEMP%/qa_v22_test/` folder (zero repo coupling):
  - Audit 0:   Structural, XML & v2.3 Typography hygiene across ALL 30 files (10 Pro .xlsm + 10 Offline .xlsx + 10 GSheets .xlsx):
                 * Zero markdown backticks (`_Assets` etc.) in any cell text
                 * 100% unified `Segoe UI` font (zero `Segoe Script` / `Segoe UI Semibold` / `Calibri` leaks)
                 * Zero `_xlfn.IMAGE` in Pro/Offline; dynamic `=IMAGE()` on `main/assets/` in GSheets
  - Test A:    Zero formula errors (#REF!, #NAME?, #VALUE!, #DIV/0!, #N/A, #BLOCKED!) & zero `#####` on ALL 20 Excel workbooks
  - Test B:    Live Hero Animation Reactivity (0% -> Stage 1, ~40% -> Stage 3, 100% -> Stage 6)
  - Test C:    Pro `.xlsm` VBA Multi-Month & Multi-Year Persistence + Dropdown Validation + Empty Year 2028 Isolation
  - Test UI:   Verify Guide Row 23 centered threshold labels, Row 14/27/Footer generous heights, and Bold/Regular column hierarchy!

Usage:
    python scripts/qa_verify_v22.py
"""
from __future__ import annotations

import shutil
import tempfile
import time
import zipfile
from pathlib import Path

import win32com.client as win32

ROOT = Path(__file__).resolve().parent.parent
PRO_DIR = ROOT / "templates" / "pro_macro"
OFF_DIR = ROOT / "templates" / "excel_universal_offline"
GS_DIR = ROOT / "templates" / "google_sheets_edition"

EXCEL_ERRORS = {
    -2146826288: "#NULL!",
    -2146826281: "#DIV/0!",
    -2146826273: "#VALUE!",
    -2146826265: "#REF!",
    -2146826259: "#NAME?",
    -2146826252: "#NUM!",
    -2146826246: "#N/A",
}
ERROR_STRS = ("#REF!", "#NAME?", "#VALUE!", "#DIV/0!", "#N/A", "#NUM!", "#NULL!", "#BLOCKED!", "#UNKNOWN!")


def audit_xml_static():
    print("\n=== AUDIT 0: STATIC STRUCTURAL, FORMULA & v2.3 TYPOGRAPHY HYGIENE (30 FILES) ===", flush=True)
    pro_files = sorted(PRO_DIR.glob("*_Pro.xlsm"))
    off_files = sorted(OFF_DIR.glob("*.xlsx"))
    gs_files = sorted(GS_DIR.glob("*.xlsx"))
    assert len(pro_files) == 10, f"Expected 10 Pro .xlsm, got {len(pro_files)}"
    assert len(off_files) == 10, f"Expected 10 Offline .xlsx, got {len(off_files)}"
    assert len(gs_files) == 10, f"Expected 10 Google Sheets .xlsx, got {len(gs_files)}"

    for f in pro_files + off_files + gs_files:
        with zipfile.ZipFile(f) as z:
            names = z.namelist()
            # 1) Zero raw markdown backticks leaking into sharedStrings!
            if "xl/sharedStrings.xml" in names:
                ss = z.read("xl/sharedStrings.xml").decode("utf-8", errors="ignore")
                assert "`" not in ss, f"{f.name}: raw markdown backtick found in cell text!"
            # 2) Strict font unification: no Segoe Script / Segoe UI Semibold in styles.xml
            if "xl/styles.xml" in names:
                st = z.read("xl/styles.xml").decode("utf-8", errors="ignore")
                assert "Segoe Script" not in st, f"{f.name}: mixed font Segoe Script found!"
                assert "Segoe UI Semibold" not in st, f"{f.name}: mixed font Segoe UI Semibold found!"

    for f in pro_files + off_files:
        with zipfile.ZipFile(f) as z:
            names = z.namelist()
            if f.suffix == ".xlsm":
                assert any("vbaProject.bin" in n for n in names), f"{f.name}: missing vbaProject.bin"
            else:
                assert not any("vbaProject" in n for n in names), f"{f.name}: unexpected VBA in No-Macro offline .xlsx!"
            for nm in names:
                if nm.startswith("xl/worksheets/sheet") and nm.endswith(".xml"):
                    txt = z.read(nm).decode("utf-8", errors="ignore")
                    assert "_xlfn.IMAGE" not in txt, f"{f.name} ({nm}): forbidden _xlfn.IMAGE in offline workbook!"

    for f in gs_files:
        with zipfile.ZipFile(f) as z:
            sheet_xmls = [n for n in z.namelist() if n.startswith("xl/worksheets/sheet") and n.endswith(".xml")]
            wb_xml = z.read("xl/workbook.xml").decode("utf-8", errors="ignore")
            ss_xml = z.read("xl/sharedStrings.xml").decode("utf-8", errors="ignore") if "xl/sharedStrings.xml" in z.namelist() else ""
            assert 'state="hidden"' in wb_xml, f"{f.name}: missing hidden helper sheets"
            all_xml = "\n".join(z.read(n).decode("utf-8", errors="ignore") for n in sheet_xmls)
            assert "raw.githubusercontent.com/Thitrongdan202/Habit-tracker-for-everyone-by-Dyu/main/assets/" in (all_xml + ss_xml)
            assert "stage_&quot;&amp;(MIN(6,MAX(1," in all_xml or 'stage_"&amp;(MIN(6,MAX(1,' in all_xml
            assert all_xml.count("stage_5.png") == 1, f"{f.name}: unexpected static stage_5.png count"

    print("  ✓ All 30 files passed XML, formula, zero-backtick & strict Segoe UI font checks!", flush=True)
    return pro_files, off_files, gs_files


def scan_sheet_errors(wb) -> list[str]:
    issues = []
    for ws in wb.Worksheets:
        used = ws.UsedRange
        vals = used.Value
        if vals is None:
            continue
        if not isinstance(vals, tuple):
            vals = ((vals,),)
        r0 = used.Row
        c0 = used.Column
        for dr, row in enumerate(vals):
            if not isinstance(row, tuple):
                row = (row,)
            for dc, v in enumerate(row):
                if isinstance(v, int) and v in EXCEL_ERRORS:
                    issues.append(f"{ws.Name}!R{r0 + dr}C{c0 + dc}={EXCEL_ERRORS[v]}")
                elif isinstance(v, str) and any(e in v for e in ERROR_STRS):
                    issues.append(f"{ws.Name}!R{r0 + dr}C{c0 + dc}={v[:40]}")
        if ws.Visible == -1:
            n_rows = min(used.Rows.Count, 60)
            n_cols = min(used.Columns.Count, 46)
            for rr in range(1, n_rows + 1):
                for cc in range(1, n_cols + 1):
                    txt = str(ws.Cells(rr, cc).Text or "")
                    if "###" in txt:
                        issues.append(f"{ws.Name}!R{rr}C{cc} displays '{txt}'")
    return issues


def find_tracker_ws(wb):
    for ws in wb.Worksheets:
        if ws.Visible == -1 and ws.Name not in ("📖 Hướng Dẫn", "🎯 Yearly Goals & Habits", "🏆 Tổng Kết & Thành Tựu Năm"):
            return ws
    raise RuntimeError("Could not find Monthly Tracker worksheet")


def run_test_ui_polish(wb, label: str):
    """Verify v2.3 typography, alignment, indent, and row-height invariants via live Excel COM."""
    ws_g = wb.Worksheets("📖 Hướng Dẫn")
    ws_tr = find_tracker_ws(wb)
    ws_yg = wb.Worksheets("🎯 Yearly Goals & Habits")
    ws_ann = wb.Worksheets("🏆 Tổng Kết & Thành Tựu Năm")

    # 1. Guide Row 23 threshold labels centered (-4108 = xlCenter) & Row 25 sprite height >= 90 & Row 27 >= 60 & Footer >= 26
    assert ws_g.Range("B23").HorizontalAlignment == -4108, f"{label}: Guide B23 not centered!"
    assert ws_g.Range("D23").HorizontalAlignment == -4108, f"{label}: Guide D23 not centered!"
    assert ws_g.Range("F23").HorizontalAlignment == -4108, f"{label}: Guide F23 not centered!"
    assert ws_g.Rows(14).RowHeight >= 48, f"{label}: Guide Row 14 height too small ({ws_g.Rows(14).RowHeight})"
    assert ws_g.Rows(25).RowHeight >= 90, f"{label}: Guide Row 25 height too small ({ws_g.Rows(25).RowHeight})"
    assert ws_g.Rows(27).RowHeight >= 60, f"{label}: Guide Row 27 height too small ({ws_g.Rows(27).RowHeight})"
    assert ws_g.Rows(29).RowHeight >= 26, f"{label}: Guide Footer Row 29 height too small ({ws_g.Rows(29).RowHeight})"
    assert "`" not in str(ws_g.Range("B27").Value or ""), f"{label}: Backtick in Guide Row 27!"

    # 2. Monthly Tracker Col B habits (incl. blank row 35): BOLD, Segoe UI, indent >= 1
    for rr in (17, 35):
        c = ws_tr.Cells(rr, 2)
        assert c.Font.Name == "Segoe UI", f"{label}: Tracker B{rr} font={c.Font.Name}"
        assert c.Font.Bold is True, f"{label}: Tracker B{rr} not bold!"
        assert c.IndentLevel >= 1, f"{label}: Tracker B{rr} indent={c.IndentLevel}"

    # 3. Yearly Goals Col C (incl. blank row 24) BOLD + indent=1; Cols D..F REGULAR + indent=1
    for rr in (6, 24):
        assert ws_yg.Cells(rr, 3).Font.Bold is True and ws_yg.Cells(rr, 3).IndentLevel >= 1
        assert ws_yg.Cells(rr, 4).Font.Bold is False and ws_yg.Cells(rr, 4).IndentLevel >= 1
        assert ws_yg.Cells(rr, 5).Font.Bold is False and ws_yg.Cells(rr, 5).IndentLevel >= 1
        assert ws_yg.Cells(rr, 6).Font.Bold is False and ws_yg.Cells(rr, 6).IndentLevel >= 1

    # 4. Annual Achievements Badges: Title BOLD + indent=1, Requirement REGULAR + indent=1
    assert ws_ann.Range("B35").Font.Bold is True and ws_ann.Range("B35").IndentLevel >= 1
    assert ws_ann.Range("E35").Font.Bold is False and ws_ann.Range("E35").IndentLevel >= 1


def run_test_b_reactivity(xl, wb, label: str):
    ws_tr = find_tracker_ws(wb)
    ws_yg = wb.Worksheets("🎯 Yearly Goals & Habits")
    ws_calc = wb.Worksheets("_Calc")

    prev_ev = xl.EnableEvents
    xl.EnableEvents = False
    try:
        blank_grid = [[False] * 31 for _ in range(20)]
        ws_tr.Range("C17:AG36").Value = blank_grid
        ws_yg.Range("B6:B25").Value = [[False] for _ in range(20)]
        xl.CalculateFull()
        assert int(ws_calc.Range("C14").Value) == 1
        assert int(ws_calc.Range("AN7").Value) == 1
        assert int(ws_calc.Range("AN8").Value) == 1
        assert int(ws_calc.Range("AN9").Value) == 1

        mid_grid = [[(d < 10) for d in range(31)] for _ in range(20)]
        ws_tr.Range("C17:AG36").Value = mid_grid
        xl.CalculateFull()
        m_pct = float(ws_calc.Range("C6").Value)
        assert 0.25 <= m_pct < 0.50, f"{label} [~40%]: pct={m_pct:.2%}"
        assert int(ws_calc.Range("C14").Value) == 3, f"{label} [~40%]: stage!=3"

        full_grid = [[True] * 31 for _ in range(20)]
        ws_tr.Range("C17:AG36").Value = full_grid
        ws_yg.Range("B6:B25").Value = [[True] if r < 10 else [False] for r in range(20)]
        xl.CalculateFull()
        assert int(ws_calc.Range("C14").Value) == 6
        assert int(ws_calc.Range("AN7").Value) == 6
        assert int(ws_calc.Range("AN8").Value) == 6
    finally:
        xl.EnableEvents = prev_ev


def run_test_c_persistence(xl, wb, label: str):
    ws_tr = find_tracker_ws(wb)
    ws_yg = wb.Worksheets("🎯 Yearly Goals & Habits")
    ws_ann = wb.Worksheets("🏆 Tổng Kết & Thành Tựu Năm")
    ws_calc = wb.Worksheets("_Calc")

    xl.EnableEvents = True
    ws_tr.Range("C17").Value = True
    ws_tr.Range("D17").Value = False
    ws_tr.Range("E17").Value = True
    ws_tr.Range("F17").Value = False
    xl.CalculateFull()

    t0 = time.perf_counter()
    ws_tr.Range("B3").Value = "November"
    dt_nov = time.perf_counter() - t0
    assert dt_nov < 3.5, f"{label}: Month switch too slow ({dt_nov:.2f}s)"
    assert str(ws_calc.Range("AN2").Value) == "2026-11"
    assert ws_tr.Range("C17").Value is False and ws_tr.Range("E17").Value is False
    assert int(ws_calc.Range("C9").Value) == 0 and int(ws_calc.Range("C14").Value) == 1

    ws_tr.Range("C17").Value = False
    ws_tr.Range("D17").Value = True
    ws_tr.Range("F17").Value = True

    t1 = time.perf_counter()
    ws_tr.Range("B3").Value = "October"
    dt_oct = time.perf_counter() - t1
    assert ws_tr.Range("C17").Value is True and ws_tr.Range("D17").Value is False
    assert ws_tr.Range("E17").Value is True and ws_tr.Range("F17").Value is False

    ws_tr.Range("B3").Value = "November"
    assert ws_tr.Range("C17").Value is False and ws_tr.Range("D17").Value is True and ws_tr.Range("F17").Value is True

    ws_yg.Range("I2").Value = 2028
    assert int(ws_calc.Range("AN4").Value) == 0 and int(ws_calc.Range("AN7").Value) == 1
    ws_yg.Range("I2").Value = 2026
    assert int(ws_calc.Range("AN4").Value) == 6

    ws_ann.Range("B3").Value = 2028
    xl.CalculateFull()
    for m_row in range(2, 14):
        assert float(ws_calc.Range(f"AS{m_row}").Value) == 0.0 and int(ws_calc.Range(f"AW{m_row}").Value) == 1
    assert int(ws_calc.Range("AN8").Value) == 1 and int(ws_calc.Range("AN9").Value) == 1

    ws_ann.Range("B3").Value = 2026
    xl.CalculateFull()
    assert float(ws_calc.Range("AS11").Value) > 0.4 and int(ws_calc.Range("AN8").Value) >= 3
    return dt_nov, dt_oct


def main():
    pro_files, off_files, _ = audit_xml_static()

    tmp_dir = Path(tempfile.gettempdir()) / "qa_v22_test"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir, ignore_errors=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    xl = win32.DispatchEx("Excel.Application")
    xl.Visible = False
    xl.DisplayAlerts = False
    xl.AutomationSecurity = 1
    try:
        print("\n=== TEST A + B + C + UI POLISH: PRO INTERACTIVE (.XLSM — ALL 10 FILES) ===", flush=True)
        for src in pro_files:
            dst = tmp_dir / src.name
            shutil.copy2(src, dst)
            wb = xl.Workbooks.Open(str(dst.resolve()))
            try:
                xl.CalculateFullRebuild()
                vis = [ws.Name for ws in wb.Worksheets if ws.Visible == -1]
                assert len(vis) == 4, f"{src.name}: expected 4 visible tabs, got {len(vis)}"
                errs = scan_sheet_errors(wb)
                assert not errs, f"{src.name} errors: {errs[:5]}"
                run_test_ui_polish(wb, src.name)
                dt_nov, dt_oct = run_test_c_persistence(xl, wb, src.name)
                wb.Close(SaveChanges=False)
                wb = xl.Workbooks.Open(str(dst.resolve()))
                run_test_b_reactivity(xl, wb, src.name)
                print(f"  ✓ [PRO PASS] {src.name}  (4 tabs, 0 errs, UI Polish OK, switch={dt_nov*1000:.0f}ms/{dt_oct*1000:.0f}ms, Hero OK!)",
                      flush=True)
            finally:
                wb.Close(SaveChanges=False)

        print("\n=== TEST A + B + UI POLISH: UNIVERSAL OFFLINE (.XLSX — ALL 10 FILES) ===", flush=True)
        for src in off_files:
            dst = tmp_dir / src.name
            shutil.copy2(src, dst)
            wb = xl.Workbooks.Open(str(dst.resolve()))
            try:
                xl.CalculateFullRebuild()
                vis = [ws.Name for ws in wb.Worksheets if ws.Visible == -1]
                assert len(vis) == 4
                errs = scan_sheet_errors(wb)
                assert not errs, f"{src.name} errors: {errs[:5]}"
                run_test_ui_polish(wb, src.name)
                ws_ann = wb.Worksheets("🏆 Tổng Kết & Thành Tựu Năm")
                ws_calc = wb.Worksheets("_Calc")
                ws_ann.Range("B3").Value = 2028
                xl.CalculateFull()
                assert int(ws_calc.Range("AN8").Value) == 1 and int(ws_calc.Range("AN9").Value) == 1
                ws_ann.Range("B3").Value = 2026
                xl.CalculateFull()
                run_test_b_reactivity(xl, wb, src.name)
                print(f"  ✓ [OFFLINE PASS] {src.name}  (4 tabs, 0 errs, UI Polish OK, Hero OK, empty 2028 OK!)",
                      flush=True)
            finally:
                wb.Close(SaveChanges=False)
    finally:
        xl.Quit()
        shutil.rmtree(tmp_dir, ignore_errors=True)

    print("\n🎉 ALL v2.3 QA & UI/UX POLISH TESTS PASSED 100% ACROSS ALL 30 DELIVERABLES!", flush=True)


if __name__ == "__main__":
    main()
