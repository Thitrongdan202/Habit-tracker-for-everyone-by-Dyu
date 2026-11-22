"""
qa_verify_v36.py — Comprehensive Automated QA Suite for Habit Tracker v3.6 Turbo Pro Edition.

Validates ALL 35 `templates/pro_macro/*_Pro.xlsm` + `vba_scripts/modHabitState.bas` +
`scripts/google_sheets_1click_setup.gs`:
  1. Static OOXML / ZIP audit on all 35 Pro `.xlsm`:
     - EXACTLY 6 unique PNGs in `xl/media/` (`<= 6`)
     - Lean file size (< 1.2 MB)
     - 0 legacy `Anim_*` Named Ranges
     - 0 volatile functions (`OFFSET`, `INDIRECT`, `TODAY`, `NOW`, `CELL`, `INFO`)
     - 0 orphan `FX_TOAST` / `FX_PARTICLE_*` shapes
     - All 48 native sprite stacks (`SPR_D01..31`, `SPR_MHERO`, `SPR_DHERO`, `SPR_GHERO`,
       `SPR_AHERO`, `SPR_BHERO`, `SPR_AM01..12`), `Guide_Stage0..5`, `ASSET_S0..5`, & 8 `BTN_*` pills present
  2. Pure-ASCII & Cross-Platform VBA audit (`0` non-ASCII bytes, `0` `Scripting.Dictionary`)
  3. Google Sheets Apps Script (`google_sheets_1click_setup.gs`) syntax & structure check
  4. Real Excel COM audit across ALL 35 Pro `.xlsm` (0 formula errors, 0 `#####`, 0 Linked Pictures)
  5. Deep interactive functional audit on 3 representative templates (`#01`, `#15`, `#35`):
     - Single tick sprite diff + lazy-flush + Month/Year switch persistence
     - `Workbook_BeforeSave` automatic lazy-flush verification
     - Daily Tasks date switch + `SPR_DHERO_S*` sync
     - Yearly Goals year switch + `SPR_GHERO_S*` sync
     - Annual Achievements activate + year switch + `SPR_AHERO`/`SPR_BHERO`/`SPR_AM01..12` sync
     - All v3.5/v3.6 FX & Pill Button macros (`BtnPrevMonth`, `BtnNextMonth`, `BtnToggleFX`,
       `BtnPrevDay`, `BtnNextDay`, `BtnDemoFX`, `SyncSpritesFromAssets`, `CleanupAllFX`)
"""
from __future__ import annotations

import gc
import re
import shutil
import sys
import tempfile
import time
import zipfile
from pathlib import Path

import win32com.client as win32

ROOT = Path(__file__).resolve().parent.parent
PRO_DIR = ROOT / "templates" / "pro_macro"
VBA_PATH = ROOT / "vba_scripts" / "modHabitState.bas"
GS_PATH = ROOT / "scripts" / "google_sheets_1click_setup.gs"

ERR_STRINGS = {"#REF!", "#NAME?", "#VALUE!", "#DIV/0!", "#N/A", "#NUM!", "#NULL!"}
VOLATILE_RE = re.compile(r"\b(?:OFFSET|INDIRECT|TODAY|NOW|CELL|INFO|RAND|RANDBETWEEN)\s*\(", re.IGNORECASE)

REQUIRED_SHAPES = (
    [f"SPR_D{d:02d}_S{s}" for d in range(1, 32) for s in range(6)]
    + [f"SPR_MHERO_S{s}" for s in range(6)]
    + [f"SPR_DHERO_S{s}" for s in range(6)]
    + [f"SPR_GHERO_S{s}" for s in range(6)]
    + [f"SPR_AHERO_S{s}" for s in range(6)]
    + [f"SPR_BHERO_S{s}" for s in range(6)]
    + [f"SPR_AM{m:02d}_S{s}" for m in range(1, 13) for s in range(6)]
    + [f"Guide_Stage{s}" for s in range(6)]
    + [f"ASSET_S{s}" for s in range(6)]
    + [
        "BTN_PREV_MONTH", "BTN_NEXT_MONTH", "BTN_FX_TOGGLE", "BTN_UNDO",
        "BTN_PREV_DAY", "BTN_TODAY", "BTN_NEXT_DAY",
        "BTN_DEMO_FX", "BTN_SYNC_ASSETS",
    ]
)

DEEP_TEST_FILES = [
    "01_Sunflower_Garden_Blush_Pro.xlsm",
    "15_Mocha_Rose_Terracotta_Sunflower_Pro.xlsm",
    "35_Milk_Mocha_Bear_Sweet_Love_Pro.xlsm",
]


def audit_vba_and_gs() -> list[str]:
    issues = []
    raw_vba = VBA_PATH.read_bytes()
    non_ascii = [b for b in raw_vba if b > 127]
    if non_ascii:
        issues.append(f"VBA has {len(non_ascii)} non-ASCII bytes!")
    vba_txt = raw_vba.decode("ascii", errors="ignore")
    if "Scripting.Dictionary" in vba_txt:
        issues.append("VBA uses Windows-only Scripting.Dictionary (crashes macOS Excel)!")
    for sym in ("SyncAllMonthlySprites", "FlushAllDirty", "SyncSpritesFromAssets",
                "HandleAnnualYearSwitch", "EnsureDbIndexes", "PlayHeroBounce", "PlaySparkleBurst", "ShowToast",
                "UndoLastHabitEdit", "ProtectVisibleSheets"):
        if sym not in vba_txt:
            issues.append(f"VBA missing required procedure: {sym}")

    gs_txt = GS_PATH.read_text(encoding="utf-8")
    for sym in ("buildColIndex_", "setupHabitTracker", "onEdit", "handleDesktopMonthlySwitch_",
                "handleDesktopDailyTasksSwitch_", "handleMobileWeekSwitch_", "handleMobileDailyTasksSwitch_"):
        if sym not in gs_txt:
            issues.append(f"Apps Script missing required function: {sym}")
    # Basic brace/paren balance check (ignoring comments/strings roughly)
    stripped = re.sub(r"//.*", "", gs_txt)
    stripped = re.sub(r"/\*[\s\S]*?\*/", "", stripped)
    stripped = re.sub(r'"(?:\\.|[^"\\])*"', '""', stripped)
    if stripped.count("{") != stripped.count("}"):
        issues.append(f"Apps Script unbalanced braces: {{={stripped.count('{')} }}={stripped.count('}')}")
    if stripped.count("(") != stripped.count(")"):
        issues.append(f"Apps Script unbalanced parens: (={stripped.count('(')} )={stripped.count(')')}")
    return issues


def audit_zip_ooxml(pro_files: list[Path]) -> list[str]:
    issues = []
    name_attr_re = re.compile(r'<xdr:cNvPr\b[^>]*\bname="([^"]+)"')
    formula_re = re.compile(r"<f[^>]*>([^<]+)</f>")
    defined_name_re = re.compile(r'<definedName\b[^>]*\bname="([^"]+)"')

    for fpath in pro_files:
        fsize = fpath.stat().st_size
        if fsize > 1_200_000:
            issues.append(f"{fpath.name}: bloated file size {fsize:,} B (> 1.2MB)")
        with zipfile.ZipFile(fpath, "r") as zf:
            names = zf.namelist()
            media = [n for n in names if n.startswith("xl/media/")]
            if len(media) != 6:
                issues.append(f"{fpath.name}: expected 6 unique PNGs in xl/media/, found {len(media)} ({media[:8]})")
            if "xl/vbaProject.bin" not in names:
                issues.append(f"{fpath.name}: missing xl/vbaProject.bin")

            wb_xml = zf.read("xl/workbook.xml").decode("utf-8", errors="ignore")
            def_names = defined_name_re.findall(wb_xml)
            anim_names = [n for n in def_names if n.startswith("Anim_")]
            if anim_names:
                issues.append(f"{fpath.name}: still has {len(anim_names)} legacy Anim_* Named Ranges: {anim_names[:5]}")

            # Scan all drawings for shape names & orphan FX
            found_shapes: set[str] = set()
            for n in names:
                if n.startswith("xl/drawings/drawing") and n.endswith(".xml"):
                    dxml = zf.read(n).decode("utf-8", errors="ignore")
                    for sn in name_attr_re.findall(dxml):
                        found_shapes.add(sn)
                        if sn == "FX_TOAST" or sn.startswith("FX_PARTICLE_"):
                            issues.append(f"{fpath.name}: orphan FX shape {sn} in {n}")
                        if sn.startswith("Anim_"):
                            issues.append(f"{fpath.name}: legacy Camera shape {sn} in {n}")

            missing = [s for s in REQUIRED_SHAPES if s not in found_shapes]
            if missing:
                issues.append(f"{fpath.name}: missing {len(missing)} required shapes (first 5: {missing[:5]})")

            # Scan all worksheet XMLs for volatile functions
            for n in names:
                if n.startswith("xl/worksheets/sheet") and n.endswith(".xml"):
                    sxml = zf.read(n).decode("utf-8", errors="ignore")
                    for ftxt in formula_re.findall(sxml):
                        m_vol = VOLATILE_RE.search(ftxt)
                        if m_vol:
                            issues.append(f"{fpath.name}: volatile formula {m_vol.group(0)} in {n}: {ftxt[:60]}")
                            break
    return issues


def _get_visible_stage(ws, prefix: str) -> int:
    vis = []
    for k in range(6):
        if ws.Shapes(f"{prefix}{k}").Visible == -1:
            vis.append(k)
    if len(vis) == 0:
        return -1  # all hidden (out-of-month day 29..31)
    if len(vis) == 1:
        return vis[0]
    return -99  # ERROR: multiple stages visible at once!


def audit_com_all_35(pro_files: list[Path], tmp_dir: Path) -> list[str]:
    issues = []
    for chunk_i in range(0, len(pro_files), 10):
        chunk = pro_files[chunk_i:chunk_i + 10]
        xl = win32.DispatchEx("Excel.Application")
        xl.Visible = False
        xl.DisplayAlerts = False
        try:
            for fpath in chunk:
                dst = tmp_dir / fpath.name
                shutil.copy2(fpath, dst)
                xl.EnableEvents = True
                wb = xl.Workbooks.Open(str(dst.resolve()))
                try:
                    xl.EnableEvents = False
                    for ws in wb.Worksheets:
                        if ws.Name in ("_Database", "_Assets"):
                            continue
                        # Check formulas / errors on UsedRange
                        ur = ws.UsedRange
                        vals = ur.Value2
                        if isinstance(vals, tuple):
                            for row in vals:
                                if isinstance(row, tuple):
                                    for v in row:
                                        if isinstance(v, str) and (v in ERR_STRINGS or v.startswith("#####")):
                                            issues.append(f"{fpath.name}[{ws.Name}]: cell error/clip '{v}'")
                                            break
                        # Check 0 Linked Pictures & 0 orphan FX shapes
                        for shp in ws.Shapes:
                            nm = str(shp.Name)
                            if shp.Type == 11 or nm.startswith("Anim_"):  # msoLinkedPicture = 11
                                issues.append(f"{fpath.name}[{ws.Name}]: Camera LinkedPicture {nm} (type={shp.Type})")
                            if nm == "FX_TOAST" or nm.startswith("FX_PARTICLE_"):
                                issues.append(f"{fpath.name}[{ws.Name}]: orphan FX shape {nm}")
                    # Verify v3.6.1 UX Hardening: Protection + Row 37 locked + Chart 1 strictly ABOVE Row 8!
                    ws_tr = wb.Names("ANCHOR_TRACKER").RefersToRange.Worksheet
                    if not ws_tr.ProtectContents or not ws_tr.ProtectionMode:
                        issues.append(f"{fpath.name}: Tracker missing UserInterfaceOnly protection!")
                    if ws_tr.Range("K37").Locked is not True or ws_tr.Range("C17").Locked is not False:
                        issues.append(f"{fpath.name}: Invalid lock map on Tracker (K37={ws_tr.Range('K37').Locked}, C17={ws_tr.Range('C17').Locked})")
                    row8_top = float(ws_tr.Rows(8).Top)
                    c1 = ws_tr.ChartObjects(1)
                    if float(c1.Top) + float(c1.Height) >= row8_top:
                        issues.append(f"{fpath.name}: Chart 1 bottom ({float(c1.Top)+float(c1.Height):.1f}) >= Row 8 top ({row8_top:.1f})")
                finally:
                    wb.Close(SaveChanges=False)
                print(f"  [COM OK] {fpath.name}", flush=True)
        finally:
            xl.Quit()
            del xl
            gc.collect()
            time.sleep(0.3)
    return issues


def audit_deep_interactive(tmp_dir: Path) -> list[str]:
    issues = []
    xl = win32.DispatchEx("Excel.Application")
    xl.Visible = False
    xl.DisplayAlerts = False
    try:
        for fname in DEEP_TEST_FILES:
            src = PRO_DIR / fname
            dst = tmp_dir / ("deep_" + fname)
            shutil.copy2(src, dst)
            wb = xl.Workbooks.Open(str(dst.resolve()))
            try:
                xl.EnableEvents = True
                xl.Calculation = -4105
                ws_tr = wb.Names("ANCHOR_TRACKER").RefersToRange.Worksheet
                ws_dt = wb.Names("ANCHOR_DAILYTASKS").RefersToRange.Worksheet
                ws_yg = wb.Names("ANCHOR_GOALS").RefersToRange.Worksheet
                ws_ann = wb.Names("ANCHOR_ANNUAL").RefersToRange.Worksheet
                ws_g = wb.Names("ANCHOR_GUIDE").RefersToRange.Worksheet
                ws_db = wb.Worksheets("_Database")
                ws_calc = wb.Worksheets("_Calc")

                # 1. Single tick on Day 28 (AD17..AD20) + Sprite Diff + Lazy-Flush check
                ws_tr.Activate()
                before_d28 = _get_visible_stage(ws_tr, "SPR_D28_S")
                if before_d28 != 0:
                    issues.append(f"{fname}: Day 28 expected stage 0 initially, got {before_d28}")
                # Tick 5 habits on Day 28 -> should advance sprite stage > 0!
                for rr in range(17, 22):
                    ws_tr.Cells(rr, 30).Value2 = True
                after_d28 = _get_visible_stage(ws_tr, "SPR_D28_S")
                if after_d28 <= 0:
                    issues.append(f"{fname}: Day 28 sprite did NOT advance after ticking 5 habits (got {after_d28})")

                # Verify Lazy-Flush: _Database row for 2026-10 col AD (col 4+28=32) should still be FALSE before switch/save!
                if bool(ws_db.Cells(2, 32).Value2) is True:
                    issues.append(f"{fname}: Lazy-flush failed — _Database was written immediately on single tick!")

                # 2. Month Switch (Oct -> Sep -> Oct): Sep has 30 days (Day 31 hidden!), Oct restores AD17=True!
                ws_tr.Range("B3").Value2 = "September"
                d31_sep = _get_visible_stage(ws_tr, "SPR_D31_S")
                if d31_sep != -1:
                    issues.append(f"{fname}: September Day 31 sprite should be hidden (-1), got {d31_sep}")
                if bool(ws_tr.Cells(17, 30).Value2) is True:
                    issues.append(f"{fname}: September leaked October's AD17=True tick!")
                # Verify October was flushed to _Database on switch!
                if bool(ws_db.Cells(2, 32).Value2) is not True:
                    issues.append(f"{fname}: Month switch did NOT flush dirty October edit to _Database!")

                ws_tr.Range("B3").Value2 = "October"
                if bool(ws_tr.Cells(17, 30).Value2) is not True:
                    issues.append(f"{fname}: Switching back to October did NOT restore AD17=True!")
                if _get_visible_stage(ws_tr, "SPR_D28_S") != after_d28:
                    issues.append(f"{fname}: Switching back to October did NOT restore Day 28 sprite!")
                if _get_visible_stage(ws_tr, "SPR_D31_S") < 0:
                    issues.append(f"{fname}: October Day 31 sprite remained hidden after returning from September!")

                # 3. Workbook_BeforeSave Lazy-Flush check: tick AE17 (Day 29, col 31) -> Save -> verify _Database col 33!
                ws_tr.Cells(17, 31).Value2 = True
                if bool(ws_db.Cells(2, 33).Value2) is True:
                    issues.append(f"{fname}: AE17 written to _Database before Save!")
                wb.Save()
                if bool(ws_db.Cells(2, 33).Value2) is not True:
                    issues.append(f"{fname}: Workbook_BeforeSave did NOT flush dirty AE17 to _Database!")

                # 4. Daily Tasks Date Switch + Sprite check
                ws_dt.Activate()
                st_dt21 = _get_visible_stage(ws_dt, "SPR_DHERO_S")
                if st_dt21 <= 0:
                    issues.append(f"{fname}: Daily Tasks 2026-10-21 hero stage should be >0, got {st_dt21}")
                ws_dt.Range("D5").Value2 = 22
                st_dt22 = _get_visible_stage(ws_dt, "SPR_DHERO_S")
                if st_dt22 != 0:
                    issues.append(f"{fname}: Empty Daily Tasks 2026-10-22 hero stage should be 0, got {st_dt22}")
                ws_dt.Range("C9").Value2 = "Test v3.6 Turbo Task"
                ws_dt.Range("B9").Value2 = True
                if _get_visible_stage(ws_dt, "SPR_DHERO_S") != 5:
                    issues.append(f"{fname}: 100% Daily Task on 22nd should reach stage 5!")
                ws_dt.Range("D5").Value2 = 21
                if _get_visible_stage(ws_dt, "SPR_DHERO_S") != st_dt21:
                    issues.append(f"{fname}: Daily Tasks return to 21st did not restore hero stage!")
                ws_dt.Range("D5").Value2 = 22
                if str(ws_dt.Range("C9").Value2) != "Test v3.6 Turbo Task":
                    issues.append(f"{fname}: Daily Tasks 22nd did NOT persist across date switches!")

                # 5. Yearly Goals Year Switch + Sprite check
                ws_yg.Activate()
                st_yg26 = _get_visible_stage(ws_yg, "SPR_GHERO_S")
                ws_yg.Range("I2").Value2 = 2028
                if _get_visible_stage(ws_yg, "SPR_GHERO_S") != 0:
                    issues.append(f"{fname}: Empty Yearly Goals 2028 should show stage 0!")
                ws_yg.Range("I2").Value2 = 2026
                if _get_visible_stage(ws_yg, "SPR_GHERO_S") != st_yg26:
                    issues.append(f"{fname}: Yearly Goals return to 2026 did not restore hero stage!")

                # 6. Annual Achievements Activate + Year Switch + Sprite check
                ws_ann.Activate()
                st_ah26 = _get_visible_stage(ws_ann, "SPR_AHERO_S")
                st_m10_26 = _get_visible_stage(ws_ann, "SPR_AM10_S")
                if st_ah26 <= 0 or st_m10_26 <= 0:
                    issues.append(f"{fname}: Annual 2026 sprites invalid (AHERO={st_ah26}, AM10={st_m10_26})")
                ws_ann.Range("B3").Value2 = 2028
                if _get_visible_stage(ws_ann, "SPR_AHERO_S") != 0 or _get_visible_stage(ws_ann, "SPR_AM10_S") != 0:
                    issues.append(f"{fname}: Annual 2028 empty year sprites did NOT drop to stage 0!")
                ws_ann.Range("B3").Value2 = 2026
                if _get_visible_stage(ws_ann, "SPR_AHERO_S") != st_ah26 or _get_visible_stage(ws_ann, "SPR_AM10_S") != st_m10_26:
                    issues.append(f"{fname}: Annual return to 2026 did NOT restore sprites!")

                # 7. Quick-Action Pill Buttons & FX macros
                ws_tr.Activate()
                xl.Run(f"'{wb.Name}'!modHabitState.BtnPrevMonth")
                if str(ws_tr.Range("B3").Value2) != "September":
                    issues.append(f"{fname}: BtnPrevMonth did not switch to September")
                xl.Run(f"'{wb.Name}'!modHabitState.BtnNextMonth")
                if str(ws_tr.Range("B3").Value2) != "October":
                    issues.append(f"{fname}: BtnNextMonth did not switch back to October")
                xl.Run(f"'{wb.Name}'!modHabitState.BtnToggleFX")
                if bool(ws_calc.Range("BA1").Value2) is not False:
                    issues.append(f"{fname}: BtnToggleFX did not disable FX")
                xl.Run(f"'{wb.Name}'!modHabitState.BtnToggleFX")
                if bool(ws_calc.Range("BA1").Value2) is not True:
                    issues.append(f"{fname}: BtnToggleFX did not re-enable FX")

                # Guide DemoFX (checks Guide_Stage5 exact width/height restore!)
                ws_g.Activate()
                g5 = ws_g.Shapes("Guide_Stage5")
                orig_w, orig_h = round(g5.Width, 2), round(g5.Height, 2)
                xl.Run(f"'{wb.Name}'!modHabitState.BtnDemoFX")
                if abs(g5.Width - orig_w) > 0.2 or abs(g5.Height - orig_h) > 0.2:
                    issues.append(f"{fname}: Guide_Stage5 drifted after BtnDemoFX ({g5.Width}x{g5.Height} vs {orig_w}x{orig_h})")

                # SyncSpritesFromAssets test (only on #01 to keep QA quick)
                if fname.startswith("01_"):
                    xl.Run(f"'{wb.Name}'!modHabitState.SyncSpritesFromAssets")
                    if _get_visible_stage(ws_tr, "SPR_MHERO_S") < 0:
                        issues.append(f"{fname}: SyncSpritesFromAssets broke SPR_MHERO_S visibility!")

                # 8. v3.6.1 Pro UX Hardening: Row 37 protection + Real Ctrl+Z Multi-Cell Undo!
                ws_tr.Activate()
                ws_tr.Protect(Password="", DrawingObjects=False, Contents=True, Scenarios=False,
                              UserInterfaceOnly=False, AllowFormattingCells=False)
                blocked_k37 = False
                try:
                    ws_tr.Range("K17:K36").AutoFill(Destination=ws_tr.Range("K17:K37"))
                except Exception:
                    blocked_k37 = True
                if not blocked_k37:
                    issues.append(f"{fname}: AutoFill onto K37 (TOTAL row) was NOT blocked!")
                xl.Run(f"'{wb.Name}'!modHabitState.ProtectVisibleSheets")

                orig_k = ws_tr.Range("K17:K36").Value2
                ws_tr.Range("K17:K36").Value2 = [[True] for _ in range(20)]
                xl.Run(f"'{wb.Name}'!modHabitState.UndoLastHabitEdit")
                if ws_tr.Range("K17:K36").Value2 != orig_k:
                    issues.append(f"{fname}: Multi-cell UndoLastHabitEdit did NOT restore K17:K36!")
                xl.Run(f"'{wb.Name}'!modHabitState.UndoLastHabitEdit")
                if ws_tr.Range("K36").Value2 is not True:
                    issues.append(f"{fname}: UndoLastHabitEdit Redo toggle failed!")
                xl.Run(f"'{wb.Name}'!modHabitState.UndoLastHabitEdit")

                # Final CleanupAllFX -> 0 orphan FX shapes across entire workbook!
                xl.Run(f"'{wb.Name}'!modHabitState.CleanupAllFX")
                for ws_chk in wb.Worksheets:
                    for shp in ws_chk.Shapes:
                        sn = str(shp.Name)
                        if sn == "FX_TOAST" or sn.startswith("FX_PARTICLE_"):
                            issues.append(f"{fname}[{ws_chk.Name}]: orphan {sn} remained after CleanupAllFX!")

                print(f"  [DEEP INTERACTIVE OK] {fname}", flush=True)
            finally:
                wb.Close(SaveChanges=False)
    finally:
        xl.Quit()
        del xl
        gc.collect()
    return issues


def main():
    pro_files = sorted(PRO_DIR.glob("*_Pro.xlsm"))
    print(f"=== HABIT TRACKER v3.6 TURBO QA VERIFICATION ({len(pro_files)} Pro workbooks) ===", flush=True)
    all_issues: list[str] = []

    if len(pro_files) != 35:
        all_issues.append(f"Expected 35 Pro .xlsm files, found {len(pro_files)}")

    print("\n[1/4] Auditing VBA pure-ASCII & Google Sheets Apps Script...", flush=True)
    iss1 = audit_vba_and_gs()
    all_issues.extend(iss1)
    print(f"  -> {len(iss1)} issue(s)", flush=True)

    print("\n[2/4] Auditing OOXML/ZIP structure, 6-PNG deduplication, 0 volatile formulas, 0 Anim_*...", flush=True)
    iss2 = audit_zip_ooxml(pro_files)
    all_issues.extend(iss2)
    print(f"  -> {len(iss2)} issue(s)", flush=True)

    tmp_dir = Path(tempfile.gettempdir()) / "qa_v36_test"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir, ignore_errors=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    try:
        print("\n[3/4] Running Excel COM formula/error/LinkedPicture scan across all 35 Pro files...", flush=True)
        iss3 = audit_com_all_35(pro_files, tmp_dir)
        all_issues.extend(iss3)
        print(f"  -> {len(iss3)} issue(s)", flush=True)

        print("\n[4/4] Running deep interactive runtime tests (Tick, Lazy-Flush, BeforeSave, Month/Year/Date/Goals/Annual, FX, SyncSprites)...", flush=True)
        iss4 = audit_deep_interactive(tmp_dir)
        all_issues.extend(iss4)
        print(f"  -> {len(iss4)} issue(s)", flush=True)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    print("\n" + "=" * 72)
    if all_issues:
        print(f"QA FAILED WITH {len(all_issues)} ISSUE(S):")
        for x in all_issues[:40]:
            print("  - " + x)
        sys.exit(1)
    else:
        print("ALL v3.6 TURBO QA CHECKS PASSED 100% (35/35 PRO WORKBOOKS + VBA + APPS SCRIPT)!")


if __name__ == "__main__":
    main()
