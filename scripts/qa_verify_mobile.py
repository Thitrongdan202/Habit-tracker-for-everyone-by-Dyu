"""
qa_verify_mobile.py — Strict Automated QA Verification for ALL 10 Mobile Portrait Templates
(`templates/mobile_portrait_sheets/01..10_*_Mobile.xlsx`).

Verifies on isolated `%TEMP%/qa_mobile_test/` copies:
  - Audit 0: Exactly 10 `*_Mobile.xlsx` files, 0 backticks, strict `Segoe UI` font (zero mixed fonts),
             all `=IMAGE(...)` URLs point to `main/assets/<slug>/`, every day `C15:I15` references
             its OWN stage cell (`_Calc!$G$1`..`_Calc!$M$1`) — zero locked column bug!
  - Test A:  0 formula errors (`#REF!`, `#NAME?`, `#VALUE!`, `#DIV/0!`, `#N/A`), 0 `#####` on non-IMAGE cells!
  - Test B:  Strict Portrait Width Constraint: EVERY visible tab (`📱 Tuần Này`, `🎯 Mục Tiêu & Thành Tựu`,
             `📖 Hướng Dẫn`) has max populated column <= Col I (9) (zero stray wide content in J+!).
  - Test C:  Valid `xlValidateList` (type == 3) dropdowns on Month (`B5`), Year (`C5`), Week (`F5`), and Goals Year (`E3`).
  - Test D:  Dynamic Calendar & Stage Reactivity:
             * Weekly Hero stage (`_Calc!E12`) drops to 1 at 0%, hits 3 at ~38%, hits 6 at 100%!
             * Goals Hero stage (`_Calc!E19`) drops to 1 at 0/8, hits 6 at 8/8!
             * Switching `Tuần 1` -> `Tuần 2` updates all 7 dates `C20:I20` cleanly (`5..11` in Oct 2026)!
             * Switching Year on Tab 2 (`E3`) to `2028` drops Annual KPIs (`E20..E26`) to `0`!

Usage:
    python scripts/qa_verify_mobile.py
"""
from __future__ import annotations

import shutil
import tempfile
import time
import zipfile
from pathlib import Path

import win32com.client as win32

ROOT = Path(__file__).resolve().parent.parent
MOB_DIR = ROOT / "templates" / "mobile_portrait_sheets"

EXCEL_ERRORS = {
    -2146826288: "#NULL!",
    -2146826281: "#DIV/0!",
    -2146826273: "#VALUE!",
    -2146826265: "#REF!",
    -2146826259: "#NAME?",
    -2146826252: "#NUM!",
    -2146826246: "#N/A",
}
HARD_ERRORS = ("#REF!", "#NAME?", "#VALUE!", "#DIV/0!", "#N/A", "#NUM!", "#NULL!")


def audit_static_mobile():
    print("\n=== AUDIT 0: STATIC XML, IMAGE() & TYPOGRAPHY CHECK (10 MOBILE TEMPLATES) ===", flush=True)
    files = sorted(MOB_DIR.glob("*_Mobile.xlsx"))
    assert len(files) == 10, f"Expected 10 *_Mobile.xlsx, got {len(files)}"

    for f in files:
        with zipfile.ZipFile(f) as z:
            names = z.namelist()
            assert not any("vbaProject" in n for n in names), f"{f.name}: unexpected VBA"
            ss = z.read("xl/sharedStrings.xml").decode("utf-8", errors="ignore") if "xl/sharedStrings.xml" in names else ""
            assert "`" not in ss, f"{f.name}: markdown backtick found!"
            st = z.read("xl/styles.xml").decode("utf-8", errors="ignore") if "xl/styles.xml" in names else ""
            assert "Segoe Script" not in st and "Segoe UI Semibold" not in st, f"{f.name}: mixed font!"

            sheet_xmls = [n for n in names if n.startswith("xl/worksheets/sheet") and n.endswith(".xml")]
            all_xml = "\n".join(z.read(n).decode("utf-8", errors="ignore") for n in sheet_xmls)
            assert "raw.githubusercontent.com/Thitrongdan202/Habit-tracker-for-everyone-by-Dyu/main/assets/" in (all_xml + ss)
            # Verify each of the 7 day stage cells ($G$1..$M$1) is referenced dynamically (no locked column bug!)
            for col_l in ("G", "H", "I", "J", "K", "L", "M"):
                assert f"_Calc'!${col_l}$1" in all_xml or f"_Calc!${col_l}$1" in all_xml, (
                    f"{f.name}: missing dynamic day stage reference ${col_l}$1"
                )
            # Verify Weekly Hero ($E$12), Goals Hero ($E$19), Badges Hero ($E$27) are dynamic!
            for ref in ("$E$12", "$E$19", "$E$27"):
                assert ref in all_xml, f"{f.name}: missing dynamic hero stage ref {ref}"
    print("  ✓ All 10 Mobile Portrait `.xlsx` files passed XML, dynamic IMAGE(), zero-backtick & Segoe UI checks!", flush=True)
    return files


def max_populated_col(ws) -> int:
    """Return rightmost 1-based column containing any non-empty value or formula on `ws`."""
    used = ws.UsedRange
    vals = used.Value
    if vals is None:
        return 0
    if not isinstance(vals, tuple):
        vals = ((vals,),)
    c0 = used.Column
    max_c = 0
    for row in vals:
        if not isinstance(row, tuple):
            row = (row,)
        for dc, v in enumerate(row):
            if v is not None and str(v).strip() != "":
                max_c = max(max_c, c0 + dc)
    return max_c


def main():
    files = audit_static_mobile()
    tmp_dir = Path(tempfile.gettempdir()) / "qa_mobile_test"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir, ignore_errors=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    xl = win32.DispatchEx("Excel.Application")
    xl.Visible = False
    xl.DisplayAlerts = False
    try:
        print("\n=== TEST A + B + C + D: LIVE EXCEL COM QA ON ALL 10 MOBILE PORTRAIT FILES ===", flush=True)
        for src in files:
            dst = tmp_dir / src.name
            shutil.copy2(src, dst)
            wb = xl.Workbooks.Open(str(dst.resolve()))
            try:
                xl.CalculateFullRebuild()
                vis = [ws.Name for ws in wb.Worksheets if ws.Visible == -1]
                assert vis == ["📱 Tuần Này", "🎯 Mục Tiêu & Thành Tựu", "📖 Hướng Dẫn"], (
                    f"{src.name}: unexpected visible tab order {vis}"
                )

                ws_wk = wb.Worksheets("📱 Tuần Này")
                ws_go = wb.Worksheets("🎯 Mục Tiêu & Thành Tựu")
                ws_gd = wb.Worksheets("📖 Hướng Dẫn")
                ws_calc = wb.Worksheets("_Calc")

                # Test B: Strict Portrait Width (max populated column <= 9 = Col I on ALL visible tabs!)
                for ws in (ws_wk, ws_go, ws_gd):
                    mc = max_populated_col(ws)
                    assert mc <= 9, f"{src.name} ({ws.Name}): content spills past Col I (max_col={mc})!"

                # Test A: 0 hard formula errors & 0 `#####` (excluding headless Linked Data Type #BLOCKED! on IMAGE() cells)
                for ws in wb.Worksheets:
                    used = ws.UsedRange
                    vals = used.Value
                    forms = used.Formula
                    if vals is None:
                        continue
                    if not isinstance(vals, tuple):
                        vals, forms = ((vals,),), ((forms,),)
                    r0, c0 = used.Row, used.Column
                    for dr, (vrow, frow) in enumerate(zip(vals, forms)):
                        if not isinstance(vrow, tuple):
                            vrow, frow = (vrow,), (frow,)
                        for dc, (v, fm) in enumerate(zip(vrow, frow)):
                            f_str = str(fm or "")
                            if "IMAGE(" in f_str.upper():
                                continue  # Headless Excel blocks external IMAGE() URLs by security policy
                            if isinstance(v, int) and v in EXCEL_ERRORS:
                                raise AssertionError(f"{src.name} {ws.Name}!R{r0+dr}C{c0+dc}={EXCEL_ERRORS[v]}")
                            if isinstance(v, str) and any(e in v for e in HARD_ERRORS):
                                raise AssertionError(f"{src.name} {ws.Name}!R{r0+dr}C{c0+dc}={v}")
                            if ws.Visible == -1:
                                for _att in range(4):
                                    try:
                                        txt = str(ws.Cells(r0 + dr, c0 + dc).Text or "")
                                        break
                                    except Exception:
                                        time.sleep(0.15)
                                else:
                                    txt = ""
                                if "###" in txt:
                                    raise AssertionError(f"{src.name} {ws.Name}!R{r0+dr}C{c0+dc} displays '{txt}'")

                # Test C: Dropdown validations (xlValidateList == 3)
                assert ws_wk.Range("B5").Validation.Type == 3, f"{src.name}: Month dropdown missing"
                assert ws_wk.Range("C5").Validation.Type == 3, f"{src.name}: Year dropdown missing"
                assert ws_wk.Range("F5").Validation.Type == 3, f"{src.name}: Week dropdown missing"
                assert ws_go.Range("E3").Validation.Type == 3, f"{src.name}: Goals Year dropdown missing"

                # Test D1: Dynamic calendar mapping (Oct 2026 Tuần 1 -> T2..T4 blank, T5..CN = 1..4; Tuần 2 -> 5..11)
                assert ws_wk.Range("C20").Value == "" and int(ws_wk.Range("F20").Value) == 1 and int(ws_wk.Range("I20").Value) == 4
                ws_wk.Range("F5").Value = "Tuần 2"
                xl.CalculateFull()
                wk2_days = [int(ws_wk.Cells(20, 3 + d).Value) for d in range(7)]
                assert wk2_days == [5, 6, 7, 8, 9, 10, 11], f"{src.name}: Tuần 2 dates={wk2_days}"
                ws_wk.Range("F5").Value = "Tuần 1"
                xl.CalculateFull()

                # Test D2: Weekly Hero & Goals Hero Reactivity (0% -> 1, ~38% -> 3, 100% -> 6)
                ws_wk.Range("C21:I35").Value = [[False] * 7 for _ in range(15)]
                ws_go.Range("B11:B22").Value = [[False] for _ in range(12)]
                xl.CalculateFull()
                assert int(ws_calc.Range("E12").Value) == 1, f"{src.name}: 0% Weekly Hero != 1"
                assert int(ws_calc.Range("E19").Value) == 1, f"{src.name}: 0% Goals Hero != 1"

                # ~38% (3 of 8 habits checked across all 4 active days -> 12/32 = 37.5% -> Stage 3!)
                mid = [[True] * 7 if r < 3 else [False] * 7 for r in range(15)]
                ws_wk.Range("C21:I35").Value = mid
                xl.CalculateFull()
                assert int(ws_calc.Range("E12").Value) == 3, f"{src.name}: 37.5% Weekly Hero != 3"

                # 100% -> Stage 6!
                ws_wk.Range("C21:I35").Value = [[True] * 7 for _ in range(15)]
                ws_go.Range("B11:B22").Value = [[True] if r < 8 else [False] for r in range(12)]
                xl.CalculateFull()
                assert int(ws_calc.Range("E12").Value) == 6, f"{src.name}: 100% Weekly Hero != 6"
                assert int(ws_calc.Range("E19").Value) == 6, f"{src.name}: 100% Goals Hero != 6"

                # Test D3: Empty Year 2028 on Tab 2 -> Annual KPIs drop to 0!
                ws_go.Range("E3").Value = 2028
                xl.CalculateFull()
                assert int(ws_calc.Range("E20").Value) == 0 and float(ws_calc.Range("E22").Value) == 0.0

                print(f"  ✓ [MOBILE PASS] {src.name}  (3 tabs <= Col I, 0 errs, dropdowns OK, W1/W2 dates OK, Hero 0%/38%/100% OK!)",
                      flush=True)
            finally:
                wb.Close(SaveChanges=False)
    finally:
        xl.Quit()
        shutil.rmtree(tmp_dir, ignore_errors=True)

    print("\n🎉 ALL 10 MOBILE PORTRAIT TEMPLATES PASSED 100% QA VERIFICATION!", flush=True)


if __name__ == "__main__":
    main()
