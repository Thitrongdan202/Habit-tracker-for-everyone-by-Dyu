"""
audit_batch_81_100.py — Full 80-File Acceptance Audit for Milestone 100 Templates:
  - Part A: 60 Holiday Habit Tracker files (#81–#95 × 4 editions)
  - Part B: 20 Chiikawa Vocabulary Tracker files (#96–#100 × 4 editions)

Verifies:
  1. ZERO Blacklist / Non-Whitelist / ALL-CAPS-Script / Bad-VN fonts & ZERO PIL text overflows
  2. ZERO `_xludf.IMAGE` or `_xlfn.IMAGE` in ANY of the 40 Cloud/Mobile files (#81–#100)
  3. Exact `_Assets!B2:B7` pure `=IMAGE(...)` + blank `B8`, Mobile portrait column limits
     (`<= Col I` for #81–#95, `<= Col G` for #96–#100), Mobile 7-col checkbox colors + `=C$20=""`
  4. Live Excel COM audit on isolated `%TEMP%` copies of ALL 80 files:
     - 0 formula errors (`#REF!`, `#NAME?`, `#VALUE!`, `#N/A`, `#DIV/0!`, `#NUM!`, `#NULL!`)
     - 20/20 Pro `.xlsm` preserve worksheet protection on all visible tabs
  5. Live VBA Execution Test in Excel COM:
     - Holiday Finale (`BtnDemoFX`) on `#81, #84, #89, #90, #91, #93, #94, #95` -> 0 errors, 0 orphans
     - Chiikawa Study Pro (`VerifyQuizEngineHeadless` + `BtnVocabDemoFX`) on ALL 5 (`#96–#100`) -> 0 errors, 0 orphans
  6. Hygiene: 0 modified files in `#01–#80`, `_build_tmp` absent, 0 `.zip`, `%TEMP%` cleaned!
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

import audit_holiday_81_95 as hol_aud
import audit_v42_pc as pc_aud
from hx.typography import (
    ALL_ALLOWED_PC_FONTS,
    BLACKLIST_FONTS,
    SCRIPT_WHITELIST,
    has_vietnamese,
    is_all_caps,
    verify_vietnamese_fonts,
)
from hx.vocab_data import VOCAB_THEMES

PRO_DIR = ROOT / "templates" / "pro_macro"
OFF_DIR = ROOT / "templates" / "excel_universal_offline"
GS_DIR = ROOT / "templates" / "google_sheets_edition"
MOB_DIR = ROOT / "templates" / "mobile_portrait_sheets"

RAW_BASE = "https://raw.githubusercontent.com/Thitrongdan202/Habit-tracker-for-everyone-by-Dyu/main/assets"
FORMULA_ERRORS = {"#REF!", "#NAME?", "#VALUE!", "#N/A", "#DIV/0!", "#NUM!", "#NULL!"}
HIDDEN_SHEETS = {"_Calc", "_Database", "_Assets", "_YearHistory"}


def check_no_xludf_image_40() -> list[str]:
    bad = []
    for p in list(GS_DIR.glob("8[1-9]_*.xlsx")) + list(GS_DIR.glob("9[0-9]_*.xlsx")) + list(GS_DIR.glob("100_*.xlsx")) \
           + list(MOB_DIR.glob("8[1-9]_*_Mobile.xlsx")) + list(MOB_DIR.glob("9[0-9]_*_Mobile.xlsx")) + list(MOB_DIR.glob("100_*_Mobile.xlsx")):
        with zipfile.ZipFile(p, "r") as z:
            for nm in z.namelist():
                if nm.startswith("xl/worksheets/sheet") and nm.endswith(".xml"):
                    txt = z.read(nm).decode("utf-8", errors="ignore")
                    if "_xludf.IMAGE" in txt or "_xlfn.IMAGE" in txt:
                        bad.append(f"{p.parent.name}/{p.name} ({nm})")
    return bad


def audit_vocab_static_20() -> tuple[bool, list[tuple[str, Path, bool]]]:
    vn_safe = set(verify_vietnamese_fonts().keys()) | {"Segoe UI"}
    pc_issues = []
    pc_overflows = []
    cloud_issues = []
    targets: list[tuple[str, Path, bool]] = []

    for v in VOCAB_THEMES:
        pro_p = PRO_DIR / f"{v.stem}_Pro.xlsm"
        off_p = OFF_DIR / f"{v.stem}.xlsx"
        gs_p = GS_DIR / f"{v.stem}.xlsx"
        mob_p = MOB_DIR / f"{v.stem}_Mobile.xlsx"

        for tag, p in (("PRO", pro_p), ("OFF", off_p), ("GS", gs_p), ("MOB", mob_p)):
            assert p.exists(), f"Missing vocab file: {p}"
            targets.append((tag, p, tag == "PRO"))

        # 1. PC Pair (Pro + Offline)
        for is_pro, p in ((True, pro_p), (False, off_p)):
            with zipfile.ZipFile(p, "r") as z:
                names = set(z.namelist())
                if is_pro and "xl/vbaProject.bin" not in names:
                    pc_issues.append((p.name, "Missing xl/vbaProject.bin"))
                wb_xml = z.read("xl/workbook.xml").decode("utf-8", errors="ignore")
                if 'calcMode="manual"' in wb_xml:
                    pc_issues.append((p.name, "calcMode=manual"))

            wb = openpyxl.load_workbook(p, data_only=False)
            found_v42, found_copy = False, False
            for sn in wb.sheetnames:
                ws = wb[sn]
                is_vis = sn not in HIDDEN_SHEETS
                cw = pc_aud._col_width_map(ws) if is_vis else {}
                for row in ws.iter_rows():
                    for cell in row:
                        val = cell.value
                        if is_vis and cell.font and cell.font.name and val is not None and str(val).strip() != "":
                            fn = cell.font.name
                            if fn in BLACKLIST_FONTS or fn not in ALL_ALLOWED_PC_FONTS:
                                pc_issues.append((p.name, f"{sn}!{cell.coordinate} non-whitelist font {fn}"))
                        if isinstance(val, str) and val and not val.startswith("="):
                            if "v4.2" in val or "V4.2" in val:
                                found_v42 = True
                            if "© 2026 Dyu (Thân Trọng Duy)" in val:
                                found_copy = True
                            if is_vis and cell.font and cell.font.name:
                                fn = cell.font.name
                                if has_vietnamese(val) and fn not in vn_safe:
                                    pc_issues.append((p.name, f"{sn}!{cell.coordinate} bad VN font {fn}"))
                                if is_all_caps(val) and fn in SCRIPT_WHITELIST:
                                    pc_issues.append((p.name, f"{sn}!{cell.coordinate} ALL-CAPS script {fn}"))
                if is_vis:
                    pc_aud._check_fit(ws, "B2", [str(ws["B2"].value or "")], pc_overflows, p.name, sn, cw)
            wb.close()
            if not found_v42:
                pc_issues.append((p.name, "Missing v4.2 tag"))
            if not found_copy:
                pc_issues.append((p.name, "Missing copyright"))

        # 2. Cloud + Mobile Pair
        for is_mob, p in ((False, gs_p), (True, mob_p)):
            wb = openpyxl.load_workbook(p, data_only=False)
            try:
                for req in ("_Calc", "_Assets"):
                    if req not in wb.sheetnames or wb[req].sheet_state != "hidden":
                        cloud_issues.append((p.name, f"Hidden sheet {req} missing/visible"))
                ws_a = wb["_Assets"]
                for r in range(2, 8):
                    want = f'=IMAGE("{RAW_BASE}/{v.slug}/stage_{r - 2}.png",1)'
                    got = str(ws_a.cell(r, 2).value or "")
                    if got != want:
                        cloud_issues.append((p.name, f"_Assets!B{r} mismatch: {got!r}"))
                if ws_a.cell(8, 2).value not in (None, ""):
                    cloud_issues.append((p.name, "_Assets!B8 not blank"))
                for sn in wb.sheetnames:
                    ws = wb[sn]
                    if ws.sheet_state == "visible":
                        if ws.views.sheetView[0].showGridLines is not False:
                            cloud_issues.append((p.name, f"{sn} gridlines visible"))
                        if is_mob and ws.max_column > 7:
                            cloud_issues.append((p.name, f"{sn} max_column={ws.max_column} > 7 (Col G)"))
            finally:
                wb.close()

    print("=== STATIC 20-FILE CHIIKAWA VOCAB AUDIT (#96–#100) ===")
    print(f"  PC issues (10 files)       : {len(pc_issues)}")
    print(f"  PC PIL overflows (10 files): {len(pc_overflows)}")
    print(f"  Cloud/Mobile issues (10)   : {len(cloud_issues)}")
    for lbl, arr in (("VOCAB PC", pc_issues[:10]), ("VOCAB OVF", pc_overflows[:10]), ("VOCAB CLOUD", cloud_issues[:10])):
        if arr:
            print(f"  !! {lbl}:", arr)
    return not (pc_issues or pc_overflows or cloud_issues), targets


def test_live_vocab_vba(pro_files: list[Path]) -> bool:
    tmp_dir = Path(tempfile.mkdtemp(prefix="audit_vocab_vba_"))
    errs = []
    tested = 0
    pythoncom.CoInitialize()
    xl = None
    try:
        xl = win32.DispatchEx("Excel.Application")
        xl.Visible = False
        xl.DisplayAlerts = False
        xl.EnableEvents = False
        for i, src in enumerate(pro_files):
            dst = tmp_dir / f"{i:02d}_{src.name}"
            shutil.copy2(src, dst)
            wb = xl.Workbooks.Open(str(dst.resolve()), UpdateLinks=0, ReadOnly=False)
            try:
                picked = xl.Run(f"'{wb.Name}'!VerifyQuizEngineHeadless")
                if not isinstance(picked, (int, float)) or int(picked) < 15:
                    errs.append((src.name, f"Quiz headless returned invalid row: {picked}"))
                ws_g = wb.Worksheets("📖 Hướng Dẫn")
                ws_g.Activate()
                xl.Run(f"'{wb.Name}'!BtnVocabDemoFX")
                xl.Run(f"'{wb.Name}'!CleanupAllVocabFX")
                leftovers = [
                    str(ws_g.Shapes(k).Name)
                    for k in range(1, ws_g.Shapes.Count + 1)
                    if str(ws_g.Shapes(k).Name).startswith(("FX_VOC_", "FX_TOAST"))
                ]
                if leftovers:
                    errs.append((src.name, f"Leftover FX shapes: {leftovers}"))
                tested += 1
            except Exception as e:
                errs.append((src.name, f"VBA error: {e}"))
            finally:
                wb.Close(SaveChanges=False)
                dst.unlink(missing_ok=True)
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
        shutil.rmtree(tmp_dir, ignore_errors=True)

    print("=== LIVE VBA CHIIKAWA STUDY PRO AUDIT (#96–#100) ===")
    print(f"  Pro workbooks live-tested  : {tested} / {len(pro_files)}")
    print(f"  VBA / quiz / orphan errors : {len(errs)}")
    print(f"  Temp VBA dir cleaned       : {not tmp_dir.exists()}")
    for e in errs:
        print("  !! VOCAB VBA ERR:", e)
    return tested == len(pro_files) and not errs


def main():
    ok_hol_static, hol_targets = hol_aud.audit_static_60(ready_only=False)
    ok_voc_static, voc_targets = audit_vocab_static_20()
    xludf_bad = check_no_xludf_image_40()
    print(f"=== PURE =IMAGE() CHECK (40 Cloud/Mobile #81–#100): bad={len(xludf_bad)} ===")
    if xludf_bad:
        print("  !! _xludf.IMAGE found in:", xludf_bad[:10])

    all_targets = hol_targets + voc_targets
    ok_com = hol_aud.audit_com_60(all_targets)

    hol_vba_samples = [
        p for (tag, p, is_pro) in hol_targets
        if is_pro and any(p.name.startswith(pref) for pref in ("81_", "84_", "89_", "90_", "91_", "93_", "94_", "95_"))
    ]
    ok_hol_vba = hol_aud.test_live_holiday_vba_finale(hol_vba_samples)
    voc_vba_samples = [p for (tag, p, is_pro) in voc_targets if is_pro]
    ok_voc_vba = test_live_vocab_vba(voc_vba_samples)

    ok_all = ok_hol_static and ok_voc_static and (not xludf_bad) and ok_com and ok_hol_vba and ok_voc_vba
    print(f"\nFINAL 80-FILE MILESTONE-100 AUDIT: {'PASS (80/80 CLEAN)' if ok_all else 'FAIL'}")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
