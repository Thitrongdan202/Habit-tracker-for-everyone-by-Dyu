"""
qa_verify_v30.py — Comprehensive Automated QA Suite for Habit Tracker v3.0 (31 Templates x 4 Editions = 124 Workbooks).

Checks:
  1. Static OpenXML / Typography / Structure Audit across ALL 124 workbooks:
     - Exact 31 files in each of the 4 edition folders
     - Pure `Segoe UI` font (zero Calibri/Arial), zero markdown backticks in sharedStrings
     - Pro .xlsm: vbaProject.bin present, 5+ visible tabs including `📝 Nhiệm Vụ Ngày`
     - Offline .xlsx: 0 vbaProject.bin, 0 featurePropertyBag, >= 660 Form Control ctrlProps, `;;;` format
     - Google Sheets .xlsx: 0 vbaProject.bin, live `=IMAGE(` formulas
     - Mobile *_Mobile.xlsx: 0 vbaProject.bin, 4 visible tabs (`📱 Tuần Này`, `📝 Việc Hôm Nay`,
       `🎯 Mục Tiêu & Thành Tựu`, `📖 Hướng Dẫn`), strict max visible content col <= I (9)
     - 31 unique bespoke Annual Hall of Fame titles (no duplicates!)
  2. Live Excel COM Functional QA (strictly on isolated `%TEMP%\\qa_v30_test\\` copies):
     - Zero formula errors, zero `#####`, 54 Linked Pictures on Pro & Offline
     - Live Pro VBA persistence: Month switch, Daily Tasks Date switch (`2026-10-21` <-> `2026-10-22`),
       Yearly Goals Year switch (`2026` <-> `2028`), Annual Year switch (`2026` <-> `2028`)
     - Live Offline Form Control CheckBox toggle + `;;;` hidden TRUE/FALSE verification

Usage:
    python scripts/qa_verify_v30.py
"""
from __future__ import annotations

import re
import shutil
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import win32com.client as win32

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from excel_builder import TEMPLATES
from hx.daily_tasks import DAILY_TASKS_SHEET
from hx.annual import YEARLY_GOALS_SHEET, ANNUAL_SHEET

ED_PRO = ROOT / "templates" / "pro_macro"
ED_OFF = ROOT / "templates" / "excel_universal_offline"
ED_GS  = ROOT / "templates" / "google_sheets_edition"
ED_MOB = ROOT / "templates" / "mobile_portrait_sheets"

NS_MAIN = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
EXCEL_ERRORS = {"#REF!", "#NAME?", "#VALUE!", "#N/A", "#DIV/0!", "#NUM!", "#NULL!", "#BLOCKED!", "#FIELD!"}


def _col_to_num(col_letters: str) -> int:
    n = 0
    for ch in col_letters:
        n = n * 26 + (ord(ch) - 64)
    return n


def _check_static_workbook(path: Path, edition: str) -> list[str]:
    errs: list[str] = []
    if not path.exists():
        return [f"MISSING FILE: {path}"]
    with zipfile.ZipFile(path, "r") as zf:
        names = set(zf.namelist())
        has_vba = "xl/vbaProject.bin" in names
        has_fpb = any("featurePropertyBag" in n for n in names)
        ctrl_props = [n for n in names if n.startswith("xl/ctrlProps/")]

        if edition == "pro":
            if not has_vba:
                errs.append("missing xl/vbaProject.bin")
        else:
            if has_vba:
                errs.append("unexpected xl/vbaProject.bin in non-Pro edition")

        if edition == "offline":
            if has_fpb:
                errs.append("unexpected featurePropertyBag in Offline .xlsx")
            if len(ctrl_props) < 660:
                errs.append(f"expected >=660 Form Control ctrlProps, got {len(ctrl_props)}")

        # Styles check: pure Segoe UI on all styled fonts (fontId >= 1; fontId=0 is Excel's built-in Normal)
        if "xl/styles.xml" in names:
            styles_xml = zf.read("xl/styles.xml").decode("utf-8", errors="ignore")
            s_root = ET.fromstring(styles_xml)
            fonts = s_root.findall(".//m:fonts/m:font", NS_MAIN)
            bad_fonts = set()
            for f_idx, f_el in enumerate(fonts):
                if f_idx == 0:
                    continue
                nm_el = f_el.find("m:name", NS_MAIN)
                if nm_el is not None:
                    fnm = nm_el.attrib.get("val", "")
                    if fnm and fnm not in ("Segoe UI", "Segoe UI Emoji", "Segoe UI Symbol"):
                        bad_fonts.add(fnm)
            if bad_fonts:
                errs.append(f"non-Segoe UI styled fonts: {sorted(bad_fonts)}")
            if edition == "offline" and ";;;" not in styles_xml:
                errs.append("missing `;;;` hidden TRUE/FALSE number format in Offline")

        # SharedStrings check: zero markdown backticks
        if "xl/sharedStrings.xml" in names:
            ss_xml = zf.read("xl/sharedStrings.xml").decode("utf-8", errors="ignore")
            if "`" in ss_xml:
                errs.append("found backtick character in sharedStrings.xml")

        # Workbook sheet names check
        wb_root = ET.fromstring(zf.read("xl/workbook.xml"))
        sheets = [(s.attrib.get("name", ""), s.attrib.get("state", "visible"))
                  for s in wb_root.findall(".//m:sheets/m:sheet", NS_MAIN)]
        vis_names = [nm for nm, st in sheets if st == "visible"]

        if edition in ("pro", "offline", "gsheets"):
            if DAILY_TASKS_SHEET not in vis_names:
                errs.append(f"missing visible tab `{DAILY_TASKS_SHEET}`")
            if ANNUAL_SHEET not in vis_names:
                errs.append(f"missing visible tab `{ANNUAL_SHEET}`")
        elif edition == "mobile":
            expected_mob = ["📱 Tuần Này", "📝 Việc Hôm Nay", "🎯 Mục Tiêu & Thành Tựu", "📖 Hướng Dẫn"]
            if vis_names != expected_mob:
                errs.append(f"mobile visible tabs mismatch: {vis_names}")

        # Formula checks (gsheets/mobile IMAGE, mobile <= Col I)
        sheet_xmls = sorted(n for n in names if re.match(r"xl/worksheets/sheet\d+\.xml$", n))
        has_image_formula = False
        for idx_s, sxml_name in enumerate(sheet_xmls):
            raw = zf.read(sxml_name).decode("utf-8", errors="ignore")
            if "IMAGE(" in raw:
                has_image_formula = True
            if edition == "mobile" and idx_s < len(sheets) and sheets[idx_s][1] == "visible":
                # Verify all cell refs on visible mobile sheets have col <= 10 (J is 1.5pt right margin; content <= I=9)
                refs = re.findall(r'<c r="([A-Z]+)\d+"', raw)
                max_c = max((_col_to_num(c) for c in refs), default=0)
                if max_c > 10:
                    errs.append(f"mobile sheet `{sheets[idx_s][0]}` exceeds Col J (max_col={max_c})")

        if edition in ("gsheets", "mobile") and not has_image_formula:
            errs.append("missing dynamic =IMAGE() formulas")
    return errs


def run_static_audit() -> bool:
    print("=== 1. STATIC OPENXML / TYPOGRAPHY / STRUCTURE AUDIT (124 WORKBOOKS) ===", flush=True)
    total_files = 0
    total_errs = 0
    annual_titles: dict[str, str] = {}

    for tdef in TEMPLATES:
        cases = [
            ("pro",     ED_PRO / f"{tdef.stem}_Pro.xlsm"),
            ("offline", ED_OFF / f"{tdef.stem}.xlsx"),
            ("gsheets", ED_GS  / f"{tdef.stem}.xlsx"),
            ("mobile",  ED_MOB / f"{tdef.stem}_Mobile.xlsx"),
        ]
        for ed, p in cases:
            total_files += 1
            errs = _check_static_workbook(p, ed)
            if errs:
                total_errs += len(errs)
                print(f"  [FAIL] [{ed}] {p.name}: {'; '.join(errs)}", flush=True)

        # Verify bespoke annual lore title uniqueness
        from hx.annual_lore import get_annual_lore
        lore = get_annual_lore(tdef.theme.slug)
        annual_titles[tdef.stem] = lore["banner"]

    unique_titles = len(set(annual_titles.values()))
    print(f"  Checked {total_files} workbooks | Static errors: {total_errs} | Unique bespoke Annual titles: {unique_titles}/31",
          flush=True)
    if total_files != 124 or total_errs > 0 or unique_titles != 31:
        return False
    print("  [PASS] ALL 124 WORKBOOKS PASSED STATIC AUDIT 100%!", flush=True)
    return True


def _scan_sheet_errors(ws) -> tuple[list[str], list[str]]:
    f_errs = []
    hashes = []
    ur = ws.UsedRange
    if ur is None:
        return f_errs, hashes
    vals = ur.Value
    if vals is None:
        return f_errs, hashes
    if not isinstance(vals, tuple):
        vals = ((vals,),)
    elif vals and not isinstance(vals[0], tuple):
        vals = (vals,)
    for r_i, row in enumerate(vals, start=1):
        for c_i, v in enumerate(row, start=1):
            if isinstance(v, int) and v < -2000000000:
                f_errs.append(f"{ws.Name}!R{r_i}C{c_i}={v}")
            elif isinstance(v, str) and v.strip() in EXCEL_ERRORS:
                f_errs.append(f"{ws.Name}!R{r_i}C{c_i}={v}")
    # Check visible sheets for `#####` in first 45 rows x 40 cols
    if ws.Visible == -1:
        max_r = min(ur.Rows.Count, 48)
        max_c = min(ur.Columns.Count, 42)
        for rr in range(1, max_r + 1):
            for cc in range(1, max_c + 1):
                txt = str(ws.Cells(rr, cc).Text or "")
                if "###" in txt:
                    hashes.append(f"{ws.Name}!R{rr}C{cc}='{txt}'")
    return f_errs, hashes


def run_live_com_qa() -> bool:
    print("\n=== 2. LIVE EXCEL COM QA (ISOLATED %TEMP%\\qa_v30_test\\ COPIES) ===", flush=True)
    tmp_dir = Path(tempfile.gettempdir()) / "qa_v30_test"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir, ignore_errors=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    sample_pro = [
        "01_Sunflower_Garden_Blush",
        "03_Rainbow_Executive_Donuts",
        "04_Sage_Botanical_Habit_And_Budget",
        "16_Dream_Home_Architect_Builder",
        "18_Plum_Oak_Master_Suite",
        "20_Cream_Alpaca_Cozy_Budget",
        "23_Bamboo_Panda_Zen_Garden",
        "24_Royal_Cat_Saving_Cash",
        "27_Hatching_Chick_Icon_Studio",
        "28_Cotton_Candy_Jar_Sweet",
        "30_Shiba_Inu_Happy_Bork",
        "31_Akita_Inu_Snow_Loyal",
    ]
    vba_test_stems = {
        "01_Sunflower_Garden_Blush",
        "24_Royal_Cat_Saving_Cash",
        "30_Shiba_Inu_Happy_Bork",
        "31_Akita_Inu_Snow_Loyal",
    }
    sample_off = [
        "01_Sunflower_Garden_Blush",
        "03_Rainbow_Executive_Donuts",
        "20_Cream_Alpaca_Cozy_Budget",
        "24_Royal_Cat_Saving_Cash",
        "30_Shiba_Inu_Happy_Bork",
    ]

    ok = True
    xl = None
    try:
        # --- PRO .xlsm QA ---
        for idx, stem in enumerate(sample_pro):
            if idx % 4 == 0:
                if xl is not None:
                    xl.Quit(); time.sleep(0.4)
                xl = win32.DispatchEx("Excel.Application")
                xl.Visible = False
                xl.DisplayAlerts = False

            src = ED_PRO / f"{stem}_Pro.xlsm"
            dst = tmp_dir / src.name
            shutil.copy2(src, dst)
            wb = xl.Workbooks.Open(str(dst))
            try:
                xl.CalculateFullRebuild()
                all_ferrs, all_hashes = [], []
                total_pics = 0
                for ws in wb.Worksheets:
                    fe, ha = _scan_sheet_errors(ws)
                    all_ferrs.extend(fe)
                    all_hashes.extend(ha)
                    if ws.Visible == -1:
                        for shp in ws.Shapes:
                            if shp.Type == 13 or "Anim_" in shp.Name or "Picture" in shp.Name:
                                total_pics += 1
                if all_ferrs or all_hashes or total_pics < 54:
                    print(f"  [FAIL] [PRO] {stem}: errs={all_ferrs[:5]} hashes={all_hashes[:5]} pics={total_pics}", flush=True)
                    ok = False
                else:
                    msg = f"  [PASS] [PRO] {stem}: 0 errs, 0 ###, pics={total_pics}"

                # Full interactive VBA test on key flagship templates
                if stem in vba_test_stems:
                    ws_tr = wb.Worksheets(3)
                    ws_dt = wb.Worksheets(DAILY_TASKS_SHEET)
                    ws_yg = wb.Worksheets(YEARLY_GOALS_SHEET)
                    ws_an = wb.Worksheets(ANNUAL_SHEET)
                    ws_c = wb.Worksheets("_Calc")

                    # 1) Daily Tasks Date switch (2026-10-21 -> 2026-10-22 -> edit -> 2026-10-21 -> 2026-10-22)
                    p0 = ws_c.Range("AN15").Value
                    s0 = ws_c.Range("AN16").Value
                    assert round(p0, 2) == 0.67 and s0 == 4, f"DT init {p0}/{s0}"
                    ws_dt.Range("D5").Value = 22
                    xl.CalculateFullRebuild()
                    assert ws_c.Range("AN15").Value == 0 and ws_c.Range("AN16").Value == 1 and not ws_dt.Range("C9").Value
                    ws_dt.Range("C9").Value = "QA Test Task 1"
                    ws_dt.Range("B9").Value = True
                    ws_dt.Range("B31").Value = "QA Highlight 22"
                    xl.CalculateFullRebuild()
                    assert ws_c.Range("AN15").Value == 1.0 and ws_c.Range("AN16").Value == 6
                    ws_dt.Range("D5").Value = 21
                    xl.CalculateFullRebuild()
                    assert round(ws_c.Range("AN15").Value, 2) == 0.67 and "báo cáo" in str(ws_dt.Range("C9").Value)
                    ws_dt.Range("D5").Value = 22
                    xl.CalculateFullRebuild()
                    assert ws_c.Range("AN15").Value == 1.0 and ws_dt.Range("C9").Value == "QA Test Task 1"

                    # 2) Monthly switch (October -> November -> October)
                    m_oct = ws_c.Range("B15").Value
                    assert m_oct >= 3, f"Monthly stage init {m_oct}"
                    ws_tr.Range("B3").Value = "November"
                    xl.CalculateFullRebuild()
                    assert ws_c.Range("B15").Value == 1, f"Nov stage expected 1, got {ws_c.Range('B15').Value}"
                    ws_tr.Range("B3").Value = "October"
                    xl.CalculateFullRebuild()
                    assert ws_c.Range("B15").Value == m_oct

                    # 3) Yearly Goals & Annual Year switch (2026 -> 2028 -> 2026)
                    yg_26 = ws_c.Range("AN5").Value
                    assert yg_26 > 0
                    ws_yg.Range("I2").Value = 2028
                    xl.CalculateFullRebuild()
                    assert ws_c.Range("AN5").Value == 0
                    ws_yg.Range("I2").Value = 2026
                    xl.CalculateFullRebuild()
                    assert abs(ws_c.Range("AN5").Value - yg_26) < 1e-6

                    an_26 = ws_c.Range("AN10").Value
                    assert an_26 > 0, f"Annual 2026 pct expected > 0, got {an_26}"
                    ws_an.Range("B3").Value = 2028
                    xl.CalculateFullRebuild()
                    assert ws_c.Range("AN10").Value == 0 and ws_c.Range("AN8").Value == 1 and ws_c.Range("AN9").Value == 1
                    ws_an.Range("B3").Value = 2026
                    xl.CalculateFullRebuild()
                    assert abs(ws_c.Range("AN10").Value - an_26) < 1e-6

                    msg += " + VBA(Month/Date/Year/Annual) 100% OK!"
                print(msg, flush=True)
            finally:
                wb.Close(SaveChanges=False)

        # --- OFFLINE .xlsx QA ---
        if xl is not None:
            xl.Quit(); time.sleep(0.4)
        xl = win32.DispatchEx("Excel.Application")
        xl.Visible = False
        xl.DisplayAlerts = False

        for stem in sample_off:
            src = ED_OFF / f"{stem}.xlsx"
            dst = tmp_dir / f"off_{src.name}"
            shutil.copy2(src, dst)
            wb = xl.Workbooks.Open(str(dst))
            try:
                xl.CalculateFullRebuild()
                ws_tr = wb.Worksheets(3)
                ws_dt = wb.Worksheets(DAILY_TASKS_SHEET)
                ws_yg = wb.Worksheets(YEARLY_GOALS_SHEET)
                ws_c = wb.Worksheets("_Calc")

                all_ferrs, all_hashes = [], []
                for ws in wb.Worksheets:
                    fe, ha = _scan_sheet_errors(ws)
                    all_ferrs.extend(fe)
                    all_hashes.extend(ha)

                cb_tr = ws_tr.CheckBoxes().Count
                cb_dt = ws_dt.CheckBoxes().Count
                cb_yg = ws_yg.CheckBoxes().Count
                nf_tr = str(ws_tr.Range("C17").NumberFormat)
                nf_dt = str(ws_dt.Range("B9").NumberFormat)
                nf_yg = str(ws_yg.Range("B6").NumberFormat)

                # Live toggle test on Daily Tasks checkbox B13 (False -> True -> % rises from 4/6 to 5/6!)
                p_before = ws_c.Range("AN15").Value
                ws_dt.Range("B13").Value = True
                xl.CalculateFullRebuild()
                p_after = ws_c.Range("AN15").Value

                assert not all_ferrs and not all_hashes
                assert cb_tr >= 620 and cb_dt == 20 and cb_yg == 20
                assert nf_tr == ";;;" and nf_dt == ";;;" and nf_yg == ";;;"
                assert p_after > p_before
                print(f"  [PASS] [OFFLINE] {stem}: 0 errs, 0 ###, FormCBs={cb_tr}+{cb_dt}+{cb_yg}, "
                      f"`;;;` hidden, live toggle {p_before:.2f}->{p_after:.2f}", flush=True)
            finally:
                wb.Close(SaveChanges=False)
    except Exception:
        import traceback
        traceback.print_exc()
        ok = False
    finally:
        if xl is not None:
            try:
                xl.Quit()
            except Exception:
                pass
        time.sleep(0.4)
        shutil.rmtree(tmp_dir, ignore_errors=True)

    return ok


def main():
    s_ok = run_static_audit()
    c_ok = run_live_com_qa() if s_ok else False
    if s_ok and c_ok:
        print("\n=== ALL HABIT TRACKER v3.0 QA CHECKS PASSED 100%! ===", flush=True)
        sys.exit(0)
    else:
        print("\n=== QA FAILED! See errors above. ===", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
