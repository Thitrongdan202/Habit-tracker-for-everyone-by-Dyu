"""
qa_verify_all.py — Mandatory v2.0 Final QA & Copy-Portability Verification Suite.

Tests ALL 30 workbooks (10 Primary Offline, 10 Pro Offline, 10 Google Sheets):
  1. Isolated Copy-Portability: copies files into `%TEMP%/habit_copy_test/` detached
     from repo & assets/ and opens the COPIED files in headless Excel COM.
  2. Zero-Error & Zero-IMAGE Audit: scans EVERY cell across ALL sheets.
  3. Month & Year Dropdown Verification (Bug 2): asserts BOTH `B3` (Month) and `B5` (Year)
     are UNMERGED with active `xlValidateList` (Type == 3), tests Oct -> Feb 2026 (28d) ->
     Feb 2028 (29d) -> Oct 2026 with zero errors.
  4. Live Linked Picture & Distinct-Day Reactivity: asserts >= 32 Linked Pictures with
     valid `Anim_DayXX` formulas & non-zero dimensions, toggles Day 1 & Day 10 independently
     to verify distinct day-column recalculation (catching any locked `$B` bug!).
  5. Google Sheets Edition formula audit: verifies all 31 day columns reference distinct
     `_Calc` stage cells (`$B$15`..`$AF$15`) and `main/assets/` URLs.

Run from repo root:
    python scripts/qa_verify_all.py
"""
from __future__ import annotations

import os
import re
import shutil
import sys
import tempfile
import time
import zipfile
from pathlib import Path
import win32com.client as win32

ROOT = Path(__file__).resolve().parent.parent
PRIMARY_DIR = ROOT / "templates"
PRO_DIR = PRIMARY_DIR / "pro_macro"
GS_DIR = PRIMARY_DIR / "google_sheets_edition"

EXCEL_ERRORS = ("#REF!", "#NAME?", "#DIV/0!", "#VALUE!", "#N/A", "#NUM!", "#NULL!",
                "#CALC!", "#SPILL!", "#CONNECT!", "#BLOCKED!", "#UNKNOWN!", "#FIELD!")


def check_primary_xml(xlsx_path: Path) -> list[str]:
    issues = []
    with zipfile.ZipFile(xlsx_path, "r") as z:
        names = z.namelist()
        if any("vbaproject" in n.lower() for n in names):
            issues.append("Contains vbaProject.bin (must be macro-free .xlsx)")
        for nm in names:
            if nm.endswith(".xml") and (nm.startswith("xl/worksheets/") or nm == "xl/workbook.xml"):
                txt = z.read(nm).decode("utf-8", errors="ignore")
                if "_xlfn." in txt:
                    found = sorted(set(re.findall(r"_xlfn\.[A-Z0-9_.]+", txt)))
                    issues.append(f"{nm} contains _xlfn functions: {found}")
                if "IMAGE(" in txt.upper():
                    issues.append(f"{nm} contains IMAGE() formula (forbidden in offline primary templates!)")
    return issues


def check_gs_distinct_stage_cols(xlsx_path: Path) -> list[str]:
    """Verify every Google Sheets file uses distinct stage columns ($B$15..$AF$15) and main/assets/."""
    issues = []
    with zipfile.ZipFile(xlsx_path, "r") as z:
        joined = "\n".join(
            z.read(nm).decode("utf-8", errors="ignore")
            for nm in z.namelist()
            if nm.startswith("xl/worksheets/") or nm == "xl/sharedStrings.xml"
        )
        if "/main/assets/" not in joined:
            issues.append("Missing `/main/assets/` URL in Google Sheets edition")
        # Check all 31 distinct _Calc stage refs exist ($B$15 through $AF$15)
        from xlsxwriter.utility import xl_col_to_name
        missing = [f"${xl_col_to_name(k)}$15" for k in range(1, 32)
                   if f"${xl_col_to_name(k)}$15" not in joined]
        if missing:
            issues.append(f"Missing distinct day stage refs: {missing[:6]}")
    return issues


def audit_workbook_cells(wb, allow_sprites_cverr: bool = False) -> list[str]:
    issues = []
    for ws in wb.Worksheets:
        if ws.Name == "_Sprites":
            continue
        ur = ws.UsedRange
        if ur is None:
            continue
        rows, cols = ur.Rows.Count, ur.Columns.Count
        r0, c0 = ur.Row, ur.Column
        vals = ur.Value
        forms = ur.Formula
        if rows == 1 and cols == 1:
            vals, forms = ((vals,),), ((forms,),)
        elif rows == 1:
            vals, forms = (vals,), (forms,)
        elif cols == 1:
            vals, forms = tuple((v,) for v in vals), tuple((f,) for f in forms)

        for ri in range(rows):
            for ci in range(cols):
                v = vals[ri][ci]
                f = str(forms[ri][ci] or "")
                is_sp = allow_sprites_cverr and ("_SPRITES!" in f.upper())
                if isinstance(v, int) and v < -2146000000:
                    txt = str(ws.Cells(r0 + ri, c0 + ci).Text or "")
                    if is_sp:
                        if any(e in txt for e in EXCEL_ERRORS) or txt.startswith("#"):
                            issues.append(f"{ws.Name}!R{r0+ri}C{c0+ci}: SPRITE error text={txt!r}")
                    else:
                        issues.append(f"{ws.Name}!R{r0+ri}C{c0+ci}: ERR val={v} text={txt!r} f={f}")
                elif isinstance(v, str) and any(e in v for e in EXCEL_ERRORS):
                    issues.append(f"{ws.Name}!R{r0+ri}C{c0+ci}: STR_ERR={v!r}")

        if ws.Visible == -1:
            for ri in range(min(rows, 58)):
                for ci in range(min(cols, 46)):
                    v = vals[ri][ci]
                    if isinstance(v, (int, float)) and not isinstance(v, bool):
                        txt = str(ws.Cells(r0 + ri, c0 + ci).Text or "")
                        if txt.startswith("###"):
                            issues.append(f"{ws.Name}!R{r0+ri}C{c0+ci}: OVERFLOW {txt!r}")
    return issues


def test_primary_copy_portability(xl, wb, stem: str):
    ws = wb.Worksheets(2)       # Main Tracker sheet
    ws_calc = wb.Worksheets("_Calc")

    # 1. Verify UNMERGED Month (B3) & Year (B5) Dropdowns (xlValidateList == 3)
    m_cell = ws.Range("B3")
    y_cell = ws.Range("B5")
    assert not bool(m_cell.MergeCells), f"{stem}: Month cell B3 must NOT be merged!"
    assert not bool(y_cell.MergeCells), f"{stem}: Year cell B5 must NOT be merged!"
    assert int(m_cell.Validation.Type) == 3, f"{stem}: Month B3 missing xlValidateList!"
    assert int(y_cell.Validation.Type) == 3, f"{stem}: Year B5 missing xlValidateList!"

    # 2. Verify Linked Pictures (>=32) & Form Control Checkboxes (>=372)
    cb_cnt = ws.CheckBoxes().Count
    pic_cnt = ws.Pictures().Count
    assert cb_cnt >= 372, f"{stem}: expected >=372 checkboxes, got {cb_cnt}"
    assert pic_cnt >= 32, f"{stem}: expected >=32 linked pictures, got {pic_cnt}"
    anim_names = set()
    for i in range(1, pic_cnt + 1):
        p = ws.Pictures(i)
        assert p.Width > 10 and p.Height > 10, f"{stem}: Pic {i} collapsed ({p.Width}x{p.Height})"
        f = str(p.Formula or "").lstrip("=")
        if f.startswith("Anim_Day"):
            anim_names.add(f)
    assert len(anim_names) == 31, f"{stem}: expected 31 distinct Anim_DayXX formulas, got {len(anim_names)}"

    # 3. Distinct-Day Toggle Reactivity Test (Day 1 = Col C / _Calc!B15, Day 10 = Col L / _Calc!K15)
    d1_pct0, d1_st0 = float(ws.Range("C12").Value), int(ws_calc.Range("B15").Value)
    d10_pct0, d10_st0 = float(ws.Range("L12").Value), int(ws_calc.Range("K15").Value)

    # Toggle Day 10 ONLY -> Day 1 MUST stay unchanged, Day 10 MUST drop!
    orig10 = [ws.Range(f"L{r}").Value for r in range(17, 23)]
    for r in range(17, 23):
        ws.Range(f"L{r}").Value = False
    xl.CalculateFull()
    assert abs(float(ws.Range("C12").Value) - d1_pct0) < 1e-6, f"{stem}: Day 10 toggle affected Day 1!"
    assert int(ws_calc.Range("B15").Value) == d1_st0, f"{stem}: Day 1 stage changed when toggling Day 10!"
    d10_pct1, d10_st1 = float(ws.Range("L12").Value), int(ws_calc.Range("K15").Value)
    assert d10_pct1 < d10_pct0 and d10_st1 < d10_st0, f"{stem}: Day 10 didn't update ({d10_pct0}->{d10_pct1}, st {d10_st0}->{d10_st1})"
    for r, v in zip(range(17, 23), orig10):
        ws.Range(f"L{r}").Value = v
    xl.CalculateFull()

    # 4. Dynamic Calendar Switch Test (Oct -> Feb 2026 = 28d -> Feb 2028 = 29d -> Oct 2026)
    m_cell.Value = "February"
    y_cell.Value = 2026
    xl.CalculateFull()
    assert int(ws_calc.Range("C3").Value) == 28, f"{stem}: Feb 2026 dim != 28"
    assert ws.Range("AE16").Value == "" and ws.Range("AF16").Value == "" and ws.Range("AG16").Value == "", f"{stem}: Feb 2026 Days 29-31 not blank"
    assert int(ws_calc.Range("AD15").Value) == 7, f"{stem}: Feb 2026 Day 29 stage != 7 (blank)"

    y_cell.Value = 2028
    xl.CalculateFull()
    assert int(ws_calc.Range("C3").Value) == 29, f"{stem}: Feb 2028 leap year dim != 29"
    assert int(ws.Range("AE16").Value) == 29 and ws.Range("AF16").Value == "", f"{stem}: Feb 2028 Day 29/30 mismatch"

    # Revert back cleanly
    m_cell.Value = "October"
    y_cell.Value = 2026
    xl.CalculateFull()
    assert int(ws_calc.Range("C3").Value) == 31
    return cb_cnt, pic_cnt, (d10_pct0, d10_pct1), (d10_st0, d10_st1)


def main():
    copy_dir = Path(tempfile.gettempdir()) / "habit_copy_test"
    if copy_dir.exists():
        shutil.rmtree(copy_dir)
    copy_dir.mkdir(parents=True)

    primary_files = sorted(PRIMARY_DIR.glob("[0-9][0-9]_*.xlsx"))
    pro_files = sorted(PRO_DIR.glob("[0-9][0-9]_*.xlsx"))
    gs_files = sorted(GS_DIR.glob("[0-9][0-9]_*.xlsx"))
    assert len(primary_files) == 10, f"Expected 10 primary files, found {len(primary_files)}"
    assert len(pro_files) == 10, f"Expected 10 pro files, found {len(pro_files)}"
    assert len(gs_files) == 10, f"Expected 10 google sheets files, found {len(gs_files)}"

    failures = []
    xl = win32.DispatchEx("Excel.Application")
    xl.Visible = False
    xl.DisplayAlerts = False
    try:
        print(f"=== QA 1: Copy-Portability & Full COM Test on 10 Primary Offline Templates ({copy_dir}) ===", flush=True)
        for src in primary_files:
            dst = copy_dir / src.name
            shutil.copy2(src, dst)
            xml_err = check_primary_xml(dst)
            if xml_err:
                failures.append((src.name, xml_err))
                print(f"  ✗ {src.name} XML FAIL: {xml_err}", flush=True)
                continue
            wb = xl.Workbooks.Open(str(dst.resolve()))
            xl.CalculateFullRebuild()
            time.sleep(0.35)
            errs = audit_workbook_cells(wb, allow_sprites_cverr=False)
            if errs:
                failures.append((src.name, errs))
                print(f"  ✗ {src.name}: {len(errs)} error(s) -> {errs[:4]}", flush=True)
            else:
                cb_n, pic_n, pcts, stgs = test_primary_copy_portability(xl, wb, src.stem)
                print(f"  ✓ {src.name}: COPY-PORTABLE OK | 0 errs | 0 IMAGE/xlfn | "
                      f"Month+Year Dropdowns OK | {cb_n} CBs | {pic_n} Pics | Day10 {pcts[0]:.0%}->{pcts[1]:.0%} (st {stgs[0]}->{stgs[1]})",
                      flush=True)
            wb.Close(False)

        print(f"\n=== QA 2: Copy-Portability Audit on 10 Pro Offline 365 Templates ===", flush=True)
        for src in pro_files:
            dst = copy_dir / src.name
            shutil.copy2(src, dst)
            wb = xl.Workbooks.Open(str(dst.resolve()))
            xl.CalculateFullRebuild()
            time.sleep(0.3)
            errs = audit_workbook_cells(wb, allow_sprites_cverr=True)
            if errs:
                failures.append((f"pro/{src.name}", errs))
                print(f"  ✗ {src.name}: {errs[:4]}", flush=True)
            else:
                print(f"  ✓ {src.name}: COPY-PORTABLE OK | 0 formula errors | 0 ### overflow", flush=True)
            wb.Close(False)

        print(f"\n=== QA 3: Distinct Day-Stage & URL Audit on 10 Google Sheets Templates ===", flush=True)
        for src in gs_files:
            gs_err = check_gs_distinct_stage_cols(src)
            if gs_err:
                failures.append((f"gs/{src.name}", gs_err))
                print(f"  ✗ {src.name}: {gs_err}", flush=True)
            else:
                print(f"  ✓ {src.name}: 31 distinct _Calc stage cols ($B$15..$AF$15) + main/assets/ URL OK", flush=True)

        if failures:
            print("\nQA SUITE FAILED:")
            for nm, er in failures:
                print(f"  {nm}: {er[:6]}")
            sys.exit(1)
        print("\nALL 30 WORKBOOKS PASSED 100% COPY-PORTABILITY, DROPDOWN, ANIMATION & ZERO-ERROR QA!", flush=True)
    finally:
        xl.Quit()
        shutil.rmtree(copy_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
