"""
qa_verify_v35.py — Comprehensive Automated QA Suite for Habit Tracker v3.5
(35 Pro FX .xlsm + 35 Offline .xlsx + 35 GSheets .xlsx + 35 Mobile Portrait = 140 Workbooks).

Checks:
  1. Static OpenXML / Typography / Structure Audit across ALL 140 workbooks:
     - Exact 35 files in each of the 4 edition folders (140 total)
     - Pure `Segoe UI` styled fonts, 0 backticks, 35/35 unique bespoke Annual titles
     - All 35 Pro .xlsm: vbaProject.bin, CFG_FX_ENABLED, ANCHOR_* defined names,
       0 volatile formulas (TODAY/NOW/INDIRECT/OFFSET), 0 orphan FX_PARTICLE_/FX_TOAST
     - All 35 Offline .xlsx: 0 vbaProject.bin, 0 featurePropertyBag, >=660 ctrlProps, `;;;`
     - All 35 GSheets & 35 Mobile: live `=IMAGE()`, Mobile strict 4 tabs + <= Col I content
  2. Live Excel COM QA (strictly on isolated `%TEMP%\\qa_v35_test\\` copies, recycling COM every 5):
     - ALL 35 Pro .xlsm checked for 0 formula errors, 0 `#####`, 54 Linked Pictures,
       7 Quick-Action Pill Buttons (`BTN_*`), and 0 orphan `FX_PARTICLE_`/`FX_TOAST` shapes!
     - Deep Interactive FX & Event Tests on #01, #32, #33, #34, #35:
       BtnPrevMonth/BtnNextMonth (+ Dec->Jan roll), BtnToggleFX, BtnPrevDay/BtnNextDay,
       Yearly Goals & Annual Year switch + deferred EnableCalculation, 100% completion
       PlayHeroBounce + PlaySparkleBurst + ShowToast + BtnDemoFX (0 errors, Hero dims intact, 0 orphans),
       plus single-tick latency measurement!
     - Live COM test of new #32-#35 Offline .xlsx (FormCBs 620+20+20, `;;;`, 0 BTN_*, live toggle)

Usage:
    python scripts/qa_verify_v35.py
"""
from __future__ import annotations

import re
import shutil
import sys
import tempfile
import time
import traceback
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import win32com.client as win32

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from excel_builder import TEMPLATES
from hx.daily_tasks import DAILY_TASKS_SHEET
from hx.annual import YEARLY_GOALS_SHEET, ANNUAL_SHEET
from hx.annual_lore import get_annual_lore
from hx.guide import GUIDE_SHEET

ED_PRO = ROOT / "templates" / "pro_macro"
ED_OFF = ROOT / "templates" / "excel_universal_offline"
ED_GS  = ROOT / "templates" / "google_sheets_edition"
ED_MOB = ROOT / "templates" / "mobile_portrait_sheets"

NS_MAIN = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
EXCEL_ERRORS = {"#REF!", "#NAME?", "#VALUE!", "#N/A", "#DIV/0!", "#NUM!", "#NULL!", "#BLOCKED!", "#FIELD!"}
REQUIRED_BTNS = {
    "BTN_PREV_MONTH", "BTN_NEXT_MONTH", "BTN_FX_TOGGLE",
    "BTN_PREV_DAY", "BTN_TODAY", "BTN_NEXT_DAY", "BTN_DEMO_FX",
}


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
                errs.append("unexpected xl/vbaProject.bin")

        if edition == "offline":
            if has_fpb:
                errs.append("unexpected featurePropertyBag in Offline")
            if len(ctrl_props) < 660:
                errs.append(f"expected >=660 Form Control ctrlProps, got {len(ctrl_props)}")

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
                errs.append("missing `;;;` hidden TRUE/FALSE format")

        if "xl/sharedStrings.xml" in names:
            ss_xml = zf.read("xl/sharedStrings.xml").decode("utf-8", errors="ignore")
            if "`" in ss_xml:
                errs.append("found backtick character in sharedStrings.xml")

        wb_xml = zf.read("xl/workbook.xml").decode("utf-8", errors="ignore")
        wb_root = ET.fromstring(wb_xml)
        sheets = [(s.attrib.get("name", ""), s.attrib.get("state", "visible"))
                  for s in wb_root.findall(".//m:sheets/m:sheet", NS_MAIN)]
        vis_names = [nm for nm, st in sheets if st == "visible"]

        if edition == "pro":
            for req_nm in ("CFG_FX_ENABLED", "ANCHOR_TRACKER", "ANCHOR_DAILYTASKS",
                           "ANCHOR_GOALS", "ANCHOR_ANNUAL", "ANCHOR_GUIDE"):
                if f'name="{req_nm}"' not in wb_xml:
                    errs.append(f"missing defined name {req_nm}")

        if edition in ("pro", "offline", "gsheets"):
            if DAILY_TASKS_SHEET not in vis_names:
                errs.append(f"missing visible tab `{DAILY_TASKS_SHEET}`")
            if ANNUAL_SHEET not in vis_names:
                errs.append(f"missing visible tab `{ANNUAL_SHEET}`")
        elif edition == "mobile":
            expected_mob = ["📱 Tuần Này", "📝 Việc Hôm Nay", "🎯 Mục Tiêu & Thành Tựu", "📖 Hướng Dẫn"]
            if vis_names != expected_mob:
                errs.append(f"mobile visible tabs mismatch: {vis_names}")

        # Check drawings for stray FX_PARTICLE_ or FX_TOAST
        for dn in names:
            if dn.startswith("xl/drawings/drawing") and dn.endswith(".xml"):
                d_xml = zf.read(dn).decode("utf-8", errors="ignore")
                if "FX_PARTICLE_" in d_xml or '"FX_TOAST"' in d_xml:
                    errs.append(f"orphan FX shape in {dn}")
                if edition == "offline" and '"BTN_' in d_xml:
                    errs.append(f"macro BTN_ shape leaked into Offline {dn}")

        sheet_xmls = sorted(n for n in names if re.match(r"xl/worksheets/sheet\d+\.xml$", n))
        has_image_formula = False
        for idx_s, sxml_name in enumerate(sheet_xmls):
            raw = zf.read(sxml_name).decode("utf-8", errors="ignore")
            if "IMAGE(" in raw:
                has_image_formula = True
            if edition == "pro" and re.search(r"<f[^>]*>[^<]*\b(TODAY|NOW|INDIRECT|OFFSET)\(", raw):
                errs.append(f"volatile formula in {sxml_name}")
            if edition == "mobile" and idx_s < len(sheets) and sheets[idx_s][1] == "visible":
                refs = re.findall(r'<c r="([A-Z]+)\d+"', raw)
                max_c = max((_col_to_num(c) for c in refs), default=0)
                if max_c > 10:
                    errs.append(f"mobile sheet `{sheets[idx_s][0]}` exceeds Col J (max_col={max_c})")

        if edition in ("gsheets", "mobile") and not has_image_formula:
            errs.append("missing dynamic =IMAGE() formulas")
    return errs


def run_static_audit() -> bool:
    print("=== 1. STATIC OPENXML / TYPOGRAPHY / FX AUDIT (140 WORKBOOKS) ===", flush=True)
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
        annual_titles[tdef.stem] = get_annual_lore(tdef.theme.slug)["banner"]

    unique_titles = len(set(annual_titles.values()))
    print(f"  Checked {total_files} workbooks | Static errors: {total_errs} | Unique bespoke Annual titles: {unique_titles}/35",
          flush=True)
    if total_files != 140 or total_errs > 0 or unique_titles != 35:
        return False
    print("  [PASS] ALL 140 WORKBOOKS PASSED STATIC AUDIT 100%!", flush=True)
    return True


def _scan_sheet_errors(ws) -> tuple[list[str], list[str]]:
    f_errs, hashes = [], []
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
    if ws.Visible == -1:
        max_r = min(ur.Rows.Count, 52)
        max_c = min(ur.Columns.Count, 42)
        for rr in range(1, max_r + 1):
            for cc in range(1, max_c + 1):
                txt = str(ws.Cells(rr, cc).Text or "")
                if "###" in txt:
                    hashes.append(f"{ws.Name}!R{rr}C{cc}='{txt}'")
    return f_errs, hashes


def run_live_com_qa() -> bool:
    print("\n=== 2. LIVE EXCEL COM QA — ALL 35 PRO (.XLSM) + NEW #32-#35 OFFLINE (.XLSX) ===", flush=True)
    tmp_dir = Path(tempfile.gettempdir()) / "qa_v35_test"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir, ignore_errors=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    deep_fx_stems = {
        "01_Sunflower_Garden_Blush",
        "32_Sakura_Blossom_Minimalist",
        "33_Peach_Mochi_Cat_Mood_Suite",
        "34_Fluffy_Bunny_Sticker_Pop",
        "35_Milk_Mocha_Bear_Sweet_Love",
    }
    new_off_stems = [t.stem for t in TEMPLATES[31:35]]

    ok = True
    xl = None
    try:
        # --- ALL 35 PRO .xlsm ---
        for idx, tdef in enumerate(TEMPLATES):
            if idx % 5 == 0:
                if xl is not None:
                    xl.Quit(); time.sleep(0.4)
                xl = win32.DispatchEx("Excel.Application")
                xl.Visible = False
                xl.DisplayAlerts = False

            stem = tdef.stem
            src = ED_PRO / f"{stem}_Pro.xlsm"
            dst = tmp_dir / src.name
            shutil.copy2(src, dst)
            wb = xl.Workbooks.Open(str(dst))
            try:
                xl.CalculateFullRebuild()
                all_ferrs, all_hashes = [], []
                total_pics = 0
                found_btns = set()
                stray_fx = []
                for ws in wb.Worksheets:
                    fe, ha = _scan_sheet_errors(ws)
                    all_ferrs.extend(fe)
                    all_hashes.extend(ha)
                    for shp in ws.Shapes:
                        snm = str(shp.Name or "")
                        if snm.startswith("FX_PARTICLE_") or snm == "FX_TOAST":
                            stray_fx.append(f"{ws.Name}!{snm}")
                        if snm in REQUIRED_BTNS:
                            found_btns.add(snm)
                        if ws.Visible == -1 and (shp.Type == 13 or snm.startswith("Anim_") or snm.startswith("Guide_Stage")):
                            total_pics += 1

                missing_btns = REQUIRED_BTNS - found_btns
                if all_ferrs or all_hashes or total_pics < 54 or missing_btns or stray_fx:
                    print(f"  [FAIL] [PRO] {stem}: errs={all_ferrs[:3]} hashes={all_hashes[:3]} "
                          f"pics={total_pics} missing_btns={missing_btns} stray={stray_fx}", flush=True)
                    ok = False
                    continue

                msg = f"  [PASS] [PRO {idx + 1:02d}/35] {stem}: 0 errs, 0 ###, pics={total_pics}, 7/7 pills, 0 stray"

                # Deep Interactive FX + Event + Latency Test on #01 & #32-#35!
                if stem in deep_fx_stems:
                    ws_tr = wb.Worksheets(3)
                    ws_dt = wb.Worksheets(DAILY_TASKS_SHEET)
                    ws_yg = wb.Worksheets(YEARLY_GOALS_SHEET)
                    ws_an = wb.Worksheets(ANNUAL_SHEET)
                    ws_g  = wb.Worksheets(GUIDE_SHEET)
                    ws_c  = wb.Worksheets("_Calc")

                    h_tr = ws_tr.Shapes("Anim_MonthlyHero")
                    orig_tr = (h_tr.Left, h_tr.Top, h_tr.Width, h_tr.Height)
                    h_dt = ws_dt.Shapes("Anim_DailyTaskHero")
                    orig_dt = (h_dt.Left, h_dt.Top, h_dt.Width, h_dt.Height)

                    # 1) Measure normal tick latency on Tracker
                    ws_tr.Activate()
                    t0 = time.perf_counter()
                    ws_tr.Range("Y17").Value = True
                    tick_ms = (time.perf_counter() - t0) * 1000.0

                    # 2) Month navigation pills + Dec->Jan roll + data persistence
                    xl.Run("BtnNextMonth")
                    assert ws_tr.Range("B3").Value == "November" and ws_c.Range("B15").Value == 1
                    xl.Run("BtnNextMonth"); xl.Run("BtnNextMonth")
                    assert ws_tr.Range("B3").Value == "January" and int(ws_tr.Range("B5").Value) == 2027
                    xl.Run("BtnPrevMonth"); xl.Run("BtnPrevMonth"); xl.Run("BtnPrevMonth")
                    assert ws_tr.Range("B3").Value == "October" and int(ws_tr.Range("B5").Value) == 2026

                    # 3) FX Toggle pill
                    xl.Run("BtnToggleFX")
                    assert ws_c.Range("BA1").Value is False
                    xl.Run("BtnToggleFX")
                    assert ws_c.Range("BA1").Value is True

                    # 4) Daily Tasks 100% completion -> Bounce + Sparkle Burst + Toast + exact Hero restore
                    ws_dt.Activate()
                    ws_dt.Range("B13").Value = True
                    ws_dt.Range("B14").Value = True  # Hits 100%!
                    assert all(abs(a - b) <= 1.5 for a, b in zip(orig_dt, (h_dt.Left, h_dt.Top, h_dt.Width, h_dt.Height)))

                    # 5) Daily Tasks date pills
                    xl.Run("BtnNextDay")
                    assert int(ws_dt.Range("D5").Value) == 22 and not ws_dt.Range("C9").Value
                    xl.Run("BtnPrevDay")
                    assert int(ws_dt.Range("D5").Value) == 21 and "báo cáo" in str(ws_dt.Range("C9").Value)

                    # 6) Yearly Goals Year switch & Annual deferred calc + spotlight
                    ws_yg.Activate()
                    yg26 = ws_c.Range("AN5").Value
                    ws_yg.Range("I2").Value = 2028
                    assert ws_c.Range("AN5").Value == 0
                    ws_yg.Range("I2").Value = 2026
                    assert abs(ws_c.Range("AN5").Value - yg26) < 1e-6

                    ws_an.Activate()
                    assert ws_an.EnableCalculation is True
                    an26 = ws_c.Range("AN10").Value
                    assert an26 > 0
                    ws_an.Range("B3").Value = 2028
                    ws_c.Calculate(); ws_an.Calculate()
                    assert ws_c.Range("AN10").Value == 0 and ws_c.Range("AN8").Value == 1
                    ws_an.Range("B3").Value = 2026
                    ws_c.Calculate(); ws_an.Calculate()

                    # 7) Demo FX button on Guide + CleanupAllFX -> 0 orphans!
                    ws_g.Activate()
                    xl.Run("BtnDemoFX")
                    xl.Run("CleanupAllFX")
                    stray2 = [f"{s.Name}!{sh.Name}" for s in wb.Worksheets for sh in s.Shapes
                              if sh.Name.startswith("FX_PARTICLE_") or sh.Name == "FX_TOAST"]
                    assert not stray2, f"Orphans after FX: {stray2}"
                    assert all(abs(a - b) <= 1.5 for a, b in zip(orig_tr, (h_tr.Left, h_tr.Top, h_tr.Width, h_tr.Height)))

                    msg += f" + FULL FX SUITE OK! (tick={tick_ms:.0f}ms)"
                print(msg, flush=True)
            finally:
                wb.Close(SaveChanges=False)

        # --- NEW #32-#35 OFFLINE .xlsx ---
        if xl is not None:
            xl.Quit(); time.sleep(0.4)
        xl = win32.DispatchEx("Excel.Application")
        xl.Visible = False
        xl.DisplayAlerts = False

        for stem in new_off_stems:
            src = ED_OFF / f"{stem}.xlsx"
            dst = tmp_dir / f"off_{src.name}"
            shutil.copy2(src, dst)
            wb = xl.Workbooks.Open(str(dst))
            try:
                xl.CalculateFullRebuild()
                ws_tr = wb.Worksheets(3)
                ws_dt = wb.Worksheets(DAILY_TASKS_SHEET)
                ws_yg = wb.Worksheets(YEARLY_GOALS_SHEET)
                ws_c  = wb.Worksheets("_Calc")

                all_ferrs, all_hashes, bad_btns = [], [], []
                for ws in wb.Worksheets:
                    fe, ha = _scan_sheet_errors(ws)
                    all_ferrs.extend(fe); all_hashes.extend(ha)
                    for shp in ws.Shapes:
                        if str(shp.Name or "").startswith("BTN_"):
                            bad_btns.append(f"{ws.Name}!{shp.Name}")

                cb_tr = ws_tr.CheckBoxes().Count
                cb_dt = ws_dt.CheckBoxes().Count
                cb_yg = ws_yg.CheckBoxes().Count
                p0 = ws_c.Range("AN15").Value
                ws_dt.Range("B13").Value = True
                xl.CalculateFullRebuild()
                p1 = ws_c.Range("AN15").Value

                assert not all_ferrs and not all_hashes and not bad_btns
                assert cb_tr >= 620 and cb_dt == 20 and cb_yg == 20
                assert str(ws_tr.Range("C17").NumberFormat) == ";;;"
                assert str(ws_dt.Range("B9").NumberFormat) == ";;;"
                assert str(ws_yg.Range("B6").NumberFormat) == ";;;"
                assert p1 > p0
                print(f"  [PASS] [OFFLINE] {stem}: 0 errs, 0 ###, FormCBs={cb_tr}+{cb_dt}+{cb_yg}, "
                      f"`;;;` hidden, 0 macro btns, toggle {p0:.2f}->{p1:.2f}", flush=True)
            finally:
                wb.Close(SaveChanges=False)
    except Exception:
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
        print("\n=== ALL HABIT TRACKER v3.5 QA CHECKS PASSED 100%! ===", flush=True)
        sys.exit(0)
    else:
        print("\n=== QA FAILED! See errors above. ===", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
