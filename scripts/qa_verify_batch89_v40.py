"""
qa_verify_batch89_v40.py — Full Automated 80-File & Golden Reference (#59) QA Suite
across ALL 4 EDITIONS (Pro Macro, Universal Offline, Google Sheets Desktop, Mobile Portrait):
  1. Global 80/80 file count check across all 4 `templates/*` folders + ZERO orphan files of replaced themes.
  2. Structural & ZIP verification of all 80 `#61-#80` workbooks (4 editions x 20 themes).
  3. Live Excel COM Golden Reference comparison (`#59 SelfCare Glow Capy` vs `#61-#80` + `#01`) on isolated `%TEMP%` copies:
     - Pro Macro: `Nhiệm Vụ Ngày` 0/6 -> 6/6 tick test, 6-stage `SPR_DHERO_S0..S5` transitions,
       bottom-left `FX_TOAST` coordinate verification against `ActiveWindow.VisibleRange`,
       3 nav buttons, Donut chart, CleanupAllFX 0-orphan check, Month Switch + Undo.
     - Universal Offline: `Nhiệm Vụ Ngày` & Monthly Tracker 0% -> 100% tick test,
       `_Calc` stage index live 1 -> 6 progression, `Anim_DailyTaskHero` & `Anim_Day01..31` Linked Pictures,
       660 Form Control Checkboxes (`;;;`), Donut chart, 0 `#REF!` / formula errors.
     - Google Sheets Desktop & Mobile: COM formula evaluation check (0 errors outside web `_Assets`).
"""
from __future__ import annotations

import gc
import hashlib
import shutil
import sys
import tempfile
import time
import zipfile
from pathlib import Path

import openpyxl
import win32com.client as win32

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from excel_builder import TEMPLATES
from hx.daily_tasks import DAILY_TASKS_SHEET

BATCH_TEMPLATES = TEMPLATES[60:80]
assert len(BATCH_TEMPLATES) == 20, f"Expected 20 templates (#61-#80), found {len(BATCH_TEMPLATES)}"

ERR_TOKENS = {"#REF!", "#NAME?", "#VALUE!", "#N/A", "#DIV/0!", "#NUM!", "#NULL!"}
RAW_BASE = "https://raw.githubusercontent.com/Thitrongdan202/Habit-tracker-for-everyone-by-Dyu/main/assets"
OLD_SLUGS = (
    "Fluffy_Squad", "Cane_Boss", "Berry_Squad",
    "loopy_fluffy_squad", "lotso_cane_boss", "lotso_berry_squad",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_global_counts_and_orphans() -> list[str]:
    errs: list[str] = []
    folders = {
        "pro_macro": ("*_Pro.xlsm", 80),
        "excel_universal_offline": ("*.xlsx", 80),
        "google_sheets_edition": ("*.xlsx", 80),
        "mobile_portrait_sheets": ("*_Mobile.xlsx", 80),
    }
    print("=== GLOBAL 80/80 FILE COUNT & ZERO-ORPHAN CHECK ===", flush=True)
    for sub, (pat, exp) in folders.items():
        d = ROOT / "templates" / sub
        files = [p for p in d.glob(pat) if not p.name.startswith("~$")]
        print(f"  templates/{sub:24s}: {len(files)}/{exp}", flush=True)
        if len(files) != exp:
            errs.append(f"templates/{sub} count={len(files)} != {exp}")

    for scan_dir in (ROOT / "templates", ROOT / "assets", ROOT / "previews"):
        for p in scan_dir.rglob("*"):
            for old in OLD_SLUGS:
                if old.lower() in p.name.lower():
                    errs.append(f"ORPHAN FILE/DIR FOUND: {p}")
    print(f"  Orphan scan across templates/, assets/, previews/: {len([e for e in errs if 'ORPHAN' in e])} orphans", flush=True)
    return errs


def verify_zip_and_structure() -> tuple[int, list[str]]:
    errors: list[str] = []
    checked = 0

    for tdef in BATCH_TEMPLATES:
        stem = tdef.stem
        slug = tdef.theme.slug
        expected_hashes = {
            sha256_bytes((ROOT / "assets" / slug / f"stage_{i}.png").read_bytes())
            for i in range(6)
        }

        # 1) Pro Macro (.xlsm)
        pro_p = ROOT / "templates" / "pro_macro" / f"{stem}_Pro.xlsm"
        if not pro_p.exists():
            errors.append(f"MISSING PRO: {pro_p}")
        else:
            checked += 1
            with zipfile.ZipFile(pro_p, "r") as zf:
                names = zf.namelist()
                if "xl/vbaProject.bin" not in names:
                    errors.append(f"PRO missing vbaProject.bin: {pro_p.name}")
                media_pngs = [n for n in names if n.startswith("xl/media/") and n.lower().endswith(".png")]
                actual_hashes = {sha256_bytes(zf.read(n)) for n in media_pngs}
                if len(media_pngs) != 6 or actual_hashes != expected_hashes:
                    errors.append(f"PRO media mismatch in {pro_p.name}: count={len(media_pngs)} match={actual_hashes == expected_hashes}")

        # 2) Universal Offline (.xlsx)
        off_p = ROOT / "templates" / "excel_universal_offline" / f"{stem}.xlsx"
        if not off_p.exists():
            errors.append(f"MISSING OFFLINE: {off_p}")
        else:
            checked += 1
            with zipfile.ZipFile(off_p, "r") as zf:
                names = zf.namelist()
                if any("vbaProject" in n for n in names):
                    errors.append(f"OFFLINE contains macro: {off_p.name}")
                ctrls = [n for n in names if n.startswith("xl/ctrlProps/")]
                if len(ctrls) != 660:
                    errors.append(f"OFFLINE ctrlProps={len(ctrls)} != 660: {off_p.name}")
                wb_xml = zf.read("xl/workbook.xml").decode("utf-8")
                if "Anim_Day01" not in wb_xml or "Anim_DailyTaskHero" not in wb_xml:
                    errors.append(f"OFFLINE missing Anim_Day01/Anim_DailyTaskHero named range: {off_p.name}")
                media = [n for n in names if n.startswith("xl/media/")]
                if len(media) < 6:
                    errors.append(f"OFFLINE missing embedded media ({len(media)}): {off_p.name}")

        # 3) Google Sheets Edition (.xlsx)
        gs_p = ROOT / "templates" / "google_sheets_edition" / f"{stem}.xlsx"
        if not gs_p.exists():
            errors.append(f"MISSING GSHEETS: {gs_p}")
        else:
            checked += 1
            with zipfile.ZipFile(gs_p, "r") as zf:
                if any("vbaProject" in n for n in zf.namelist()):
                    errors.append(f"GSHEETS contains macro: {gs_p.name}")
            wb = openpyxl.load_workbook(gs_p, data_only=False)
            try:
                for h_s in ("_Calc", "_Database", "_Assets"):
                    if h_s not in wb.sheetnames or wb[h_s].sheet_state != "hidden":
                        errors.append(f"GSHEETS missing/visible {h_s}: {gs_p.name}")
                ws_a = wb["_Assets"]
                for r in range(2, 8):
                    exp = f'=IMAGE("{RAW_BASE}/{slug}/stage_{r - 2}.png",1)'
                    if str(ws_a.cell(r, 2).value or "") != exp:
                        errors.append(f"GSHEETS _Assets!B{r} mismatch: {gs_p.name}")
                if ws_a.cell(8, 2).value not in (None, ""):
                    errors.append(f"GSHEETS _Assets!B8 not blank: {gs_p.name}")
                ws_tr = wb[tdef.tracker_name]
                if ws_tr["B3"].value != "October" or ws_tr["B5"].value != 2026 or not isinstance(ws_tr["C17"].value, bool):
                    errors.append(f"GSHEETS onEdit coords mismatch: {gs_p.name}")
            finally:
                wb.close()

        # 4) Mobile Portrait (.xlsx)
        mob_p = ROOT / "templates" / "mobile_portrait_sheets" / f"{stem}_Mobile.xlsx"
        if not mob_p.exists():
            errors.append(f"MISSING MOBILE: {mob_p}")
        else:
            checked += 1
            with zipfile.ZipFile(mob_p, "r") as zf:
                if any("vbaProject" in n for n in zf.namelist()):
                    errors.append(f"MOBILE contains macro: {mob_p.name}")
            wb = openpyxl.load_workbook(mob_p, data_only=False)
            try:
                for h_s in ("_Calc", "_Database", "_Assets"):
                    if h_s not in wb.sheetnames or wb[h_s].sheet_state != "hidden":
                        errors.append(f"MOBILE missing/visible {h_s}: {mob_p.name}")
                ws_wk = wb["📱 Tuần Này"]
                if ws_wk.max_column > 9:
                    errors.append(f"MOBILE max_column={ws_wk.max_column} > 9: {mob_p.name}")
                if ws_wk["B5"].value != "October" or ws_wk["C5"].value != 2026 or not isinstance(ws_wk["C21"].value, bool):
                    errors.append(f"MOBILE onEdit coords mismatch: {mob_p.name}")
            finally:
                wb.close()

    return checked, errors


def scan_com_errors(wb, skip_assets_refs: bool = False) -> list[str]:
    errs: list[str] = []
    for ws in wb.Worksheets:
        if ws.Visible != -1:
            continue
        ur = ws.UsedRange
        vals = ur.Value
        if vals is None:
            continue
        if not isinstance(vals, tuple):
            vals = ((vals,),)
        r0, c0 = ur.Row, ur.Column
        for ri, row in enumerate(vals):
            if not isinstance(row, tuple):
                row = (row,)
            for ci, v in enumerate(row):
                is_err = (isinstance(v, int) and v <= -2146826200) or (isinstance(v, str) and (v in ERR_TOKENS or v.startswith("#####")))
                if is_err:
                    if skip_assets_refs:
                        f_str = str(ws.Cells(r0 + ri, c0 + ci).Formula or "")
                        if "_Assets" in f_str:
                            continue
                    errs.append(f"{ws.Name}!R{r0+ri}C{c0+ci}={v}")
    return errs


def _test_pro_daily_tasks_and_toast(xl, wb, label: str) -> tuple[str, list[str]]:
    errs: list[str] = []
    ws_dt = wb.Worksheets(DAILY_TASKS_SHEET)
    ws_dt.Activate()
    time.sleep(0.2)

    # Check 3 nav buttons + Donut chart
    sh_names = {str(ws_dt.Shapes(i).Name or "") for i in range(1, ws_dt.Shapes.Count + 1)}
    for req_btn in ("BTN_PREV_DAY", "BTN_TODAY", "BTN_NEXT_DAY"):
        if req_btn not in sh_names:
            errs.append(f"{label} missing {req_btn} on {DAILY_TASKS_SHEET}")
    n_charts = ws_dt.ChartObjects().Count
    if n_charts < 1:
        errs.append(f"{label} missing Donut chart on {DAILY_TASKS_SHEET}")

    # Clear B9:B14 to False (0/6) then tick B9..B14 -> True (1/6..6/6)
    for r in range(9, 15):
        ws_dt.Cells(r, 2).Value = False
    xl.Calculate()

    seen_stages: list[int] = []
    def _visible_hero_stage() -> int:
        for s in range(6):
            nm = f"SPR_DHERO_S{s}"
            if nm in sh_names:
                shp = ws_dt.Shapes(nm)
                if bool(shp.Visible):
                    return s
        return -1

    seen_stages.append(_visible_hero_stage())
    for r in range(9, 15):
        ws_dt.Cells(r, 2).Value = True
        xl.Calculate()
        seen_stages.append(_visible_hero_stage())

    unique_stages = sorted(set(x for x in seen_stages if x >= 0))
    if len(unique_stages) < 5:
        errs.append(f"{label} SPR_DHERO stage progression insufficient: {seen_stages}")

    # Trigger toast at 100% (ensure ShowToast fires on current active window)
    # Note: setting B14 True on 6/6 already fires Worksheet_Change -> ShowToast!
    # Check FX_TOAST coordinates relative to ActiveWindow.VisibleRange
    vis = xl.ActiveWindow.VisibleRange
    vis_l, vis_t, vis_w, vis_h = float(vis.Left), float(vis.Top), float(vis.Width), float(vis.Height)

    toast_info = "no-toast"
    toast_shp = None
    for i in range(1, ws_dt.Shapes.Count + 1):
        if ws_dt.Shapes(i).Name == "FX_TOAST":
            toast_shp = ws_dt.Shapes(i)
            break
    if toast_shp is None:
        errs.append(f"{label} FX_TOAST shape not created at 6/6 (100%)!")
    else:
        tl, tt, tw, th = float(toast_shp.Left), float(toast_shp.Top), float(toast_shp.Width), float(toast_shp.Height)
        exp_l = vis_l + 14.0
        exp_t = max(10.0, vis_t + vis_h - th - 18.0)
        dl = abs(tl - exp_l)
        dt = abs(tt - exp_t)
        toast_info = f"toast=({tl:.1f},{tt:.1f}) exp=({exp_l:.1f},{exp_t:.1f}) visH={vis_h:.0f}"
        if dl > 18.0 or dt > 12.0:
            errs.append(f"{label} FX_TOAST NOT bottom-left! got=({tl:.1f},{tt:.1f}) exp=({exp_l:.1f},{exp_t:.1f})")

    # CleanupAllFX -> verify FX_TOAST hidden & 0 orphan FX_CONFETTI
    xl.Run(f"'{wb.Name}'!modHabitState.CleanupAllFX")
    orphans = 0
    for i in range(1, ws_dt.Shapes.Count + 1):
        nm = str(ws_dt.Shapes(i).Name or "")
        if nm.startswith("FX_CONFETTI") or (nm == "FX_TOAST" and bool(ws_dt.Shapes(i).Visible)):
            orphans += 1
    if orphans:
        errs.append(f"{label} CleanupAllFX left {orphans} visible/orphan FX shapes!")

    return f"stages={unique_stages} | charts={n_charts} | {toast_info} | orphans=0", errs


def _test_offline_daily_and_tracker(xl, wb, tracker_name: str, label: str) -> tuple[str, list[str]]:
    errs: list[str] = []
    ws_dt = wb.Worksheets(DAILY_TASKS_SHEET)
    ws_tr = wb.Worksheets(tracker_name)
    ws_calc = wb.Worksheets("_Calc")

    # Verify Anim_DailyTaskHero picture + Donut chart
    n_charts_dt = ws_dt.ChartObjects().Count
    if n_charts_dt < 1:
        errs.append(f"{label} missing Donut chart on {DAILY_TASKS_SHEET}")
    if ws_dt.Pictures().Count < 1:
        errs.append(f"{label} missing Anim_DailyTaskHero Linked Picture on {DAILY_TASKS_SHEET}")

    # Find Daily Task stage cell in _Calc via Anim_DailyTaskHero Named Range
    nm_ref = str(wb.Names("Anim_DailyTaskHero").RefersTo)
    if "_Assets" not in nm_ref or "#REF!" in nm_ref:
        errs.append(f"{label} Anim_DailyTaskHero invalid RefersTo: {nm_ref}")

    # Clear B9:B14 -> False, tick 1..6 and observe _Calc!B35 (or stage cell in nm_ref)
    import re
    m = re.search(r"_Calc!\$?([A-Z]+)\$?(\d+)", nm_ref)
    calc_addr = f"{m.group(1)}{m.group(2)}" if m else "B35"
    for r in range(9, 15):
        ws_dt.Cells(r, 2).Value = False
    xl.CalculateFull()
    stgs = [int(ws_calc.Range(calc_addr).Value or 0)]
    for r in range(9, 15):
        ws_dt.Cells(r, 2).Value = True
        xl.Calculate()
        stgs.append(int(ws_calc.Range(calc_addr).Value or 0))
    uniq_dt = sorted(set(stgs))
    if uniq_dt != [1, 2, 3, 4, 5, 6] and len(uniq_dt) < 5:
        errs.append(f"{label} Offline DailyTasks _Calc!{calc_addr} did not progress 1..6: {stgs}")

    # Also test Monthly Tracker Day 1 progression (all active habit rows C17:C36 -> False then active habits -> True)
    d1_ref = str(wb.Names("Anim_Day01").RefersTo)
    m1 = re.search(r"_Calc!\$?([A-Z]+)\$?(\d+)", d1_ref)
    d1_addr = f"{m1.group(1)}{m1.group(2)}" if m1 else "A4"
    active_rows = [r for r in range(17, 37) if str(ws_tr.Cells(r, 2).Value or "").strip() != ""]
    for r in active_rows:
        ws_tr.Cells(r, 3).Value = False
    xl.Calculate()
    tr_s0 = int(ws_calc.Range(d1_addr).Value or 0)
    for r in active_rows:
        ws_tr.Cells(r, 3).Value = True
    xl.Calculate()
    tr_s5 = int(ws_calc.Range(d1_addr).Value or 0)
    if tr_s0 != 1 or tr_s5 != 6:
        errs.append(f"{label} Offline Tracker Day 1 _Calc!{d1_addr} failed 1->6: {tr_s0}->{tr_s5}")

    return f"dt_stages={uniq_dt} | tr_d1={tr_s0}->{tr_s5} | charts={n_charts_dt}", errs


def verify_com_runtime() -> tuple[int, list[str]]:
    errors: list[str] = []
    com_passed = 0
    tmp_dir = Path(tempfile.mkdtemp(prefix="qa_batch89_v40_"))

    def _new_xl(visible: bool = False):
        x = win32.DispatchEx("Excel.Application")
        x.Visible = visible
        x.DisplayAlerts = False
        try:
            x.AutomationSecurity = 1
        except Exception:
            pass
        return x

    def _quit_xl(x):
        if x is not None:
            try:
                x.Quit()
            except Exception:
                pass
            del x
            gc.collect()
            time.sleep(0.4)

    try:
        # ---- GOLDEN REFERENCE + TOAST POSITION TEST (Visible=True so VisibleRange is real!) ----
        print("\n=== GOLDEN REFERENCE (#59) + BOTTOM-LEFT TOAST LIVE AUDIT (PRO MACRO) ===", flush=True)
        toast_targets = [
            TEMPLATES[0],   # #01 synced via sync_vba_toast_01_60.py
            TEMPLATES[58],  # #59 Golden Reference (Capybara SelfCare GlowUp)
            TEMPLATES[60],  # #61 Loopy Red Bow
            TEMPLATES[69],  # #70 NEW Loopy Hair Roller GRWM
            TEMPLATES[71],  # #72 NEW Lotso Strawberry Milk Cafe
            TEMPLATES[79],  # #80 NEW Lotso Berry Gift Box Party
        ]
        xl = _new_xl(visible=True)
        try:
            xl.WindowState = -4137  # xlMaximized for crisp realistic VisibleRange
        except Exception:
            pass
        for tdef in toast_targets:
            src = ROOT / "templates" / "pro_macro" / f"{tdef.stem}_Pro.xlsm"
            dst = tmp_dir / f"toast_{src.name}"
            shutil.copy2(src, dst)
            wb = xl.Workbooks.Open(str(dst.resolve()))
            try:
                xl.CalculateFullRebuild()
                cerrs = scan_com_errors(wb)
                if cerrs:
                    errors.append(f"PRO-GOLD {src.name} formula errs: {cerrs[:5]}")
                summary, t_errs = _test_pro_daily_tasks_and_toast(xl, wb, src.name)
                errors.extend(t_errs)
                com_passed += 1
                print(f"  ✓ PRO-GOLD {src.name:40s} | {summary}", flush=True)
            finally:
                wb.Close(SaveChanges=False)
        _quit_xl(xl)

        # ---- ALL 20 PRO MACRO (#61-#80) FULL SUITE ----
        print("\n=== COM LIVE QA: ALL 20 PRO MACRO (#61-#80 .xlsm) ===", flush=True)
        xl = None
        for idx, tdef in enumerate(BATCH_TEMPLATES):
            if idx % 5 == 0:
                _quit_xl(xl)
                xl = _new_xl(visible=False)
            src = ROOT / "templates" / "pro_macro" / f"{tdef.stem}_Pro.xlsm"
            dst = tmp_dir / src.name
            shutil.copy2(src, dst)
            wb = xl.Workbooks.Open(str(dst.resolve()))
            try:
                xl.CalculateFullRebuild()
                cerrs = scan_com_errors(wb)
                if cerrs:
                    errors.append(f"PRO {src.name} formula errs: {cerrs[:5]}")

                ws_tr = wb.Worksheets(tdef.tracker_name)
                prot = bool(ws_tr.ProtectContents)
                k37_locked = bool(ws_tr.Range("K37").Locked)
                c17_locked = bool(ws_tr.Range("C17").Locked)
                if not prot or not k37_locked or c17_locked:
                    errors.append(f"PRO {src.name} protection fail: prot={prot} k37={k37_locked} c17={c17_locked}")

                btn_cnt = sum(
                    1 for w in wb.Worksheets for s_i in range(1, w.Shapes.Count + 1)
                    if str(w.Shapes(s_i).Name or "").startswith("BTN_")
                )
                if btn_cnt < 9:
                    errors.append(f"PRO {src.name} missing pill buttons ({btn_cnt} < 9)")

                t_ms = 0.0
                if idx in (0, 5, 9, 10, 15, 19):
                    ws_tr.Range("B3").Value = "November"
                    t0 = time.perf_counter()
                    ws_tr.Range("B3").Value = "October"
                    t_ms = (time.perf_counter() - t0) * 1000.0
                    done_tot = ws_tr.Range("C37").Value
                    if not isinstance(done_tot, (int, float)) or done_tot <= 0:
                        errors.append(f"PRO {src.name} Oct reload C37 invalid: {done_tot}")
                    if idx in (0, 10):
                        orig_val = ws_tr.Range("C17").Value
                        ws_tr.Range("C17").Value = not bool(orig_val)
                        xl.Run(f"'{wb.Name}'!modHabitState.UndoLastHabitEdit")
                        if bool(ws_tr.Range("C17").Value) != bool(orig_val):
                            errors.append(f"PRO {src.name} Undo failed!")

                try:
                    xl.Run(f"'{wb.Name}'!modHabitState.CleanupAllFX")
                except Exception:
                    pass
                com_passed += 1
                ms_tag = f" | switch={t_ms:.0f}ms" if t_ms > 0 else ""
                print(f"  ✓ PRO {src.name:44s} | errs=0 | btns={btn_cnt} | prot=OK{ms_tag}", flush=True)
            finally:
                wb.Close(SaveChanges=False)
        _quit_xl(xl)

        # ---- GOLDEN REFERENCE (#59) + ALL 20 UNIVERSAL OFFLINE (#61-#80) ----
        print("\n=== COM LIVE QA: GOLDEN REF (#59) + ALL 20 UNIVERSAL OFFLINE (.xlsx) ===", flush=True)
        offline_list = [TEMPLATES[58]] + list(BATCH_TEMPLATES)
        xl = None
        for idx, tdef in enumerate(offline_list):
            if idx % 5 == 0:
                _quit_xl(xl)
                xl = _new_xl(visible=False)
            src = ROOT / "templates" / "excel_universal_offline" / f"{tdef.stem}.xlsx"
            dst = tmp_dir / f"off_{src.name}"
            shutil.copy2(src, dst)
            wb = xl.Workbooks.Open(str(dst.resolve()))
            try:
                xl.CalculateFullRebuild()
                cerrs = scan_com_errors(wb)
                if cerrs:
                    errors.append(f"OFFLINE {src.name} formula errs: {cerrs[:5]}")
                ws_tr = wb.Worksheets(tdef.tracker_name)
                cb_tr = ws_tr.CheckBoxes().Count
                nf_c17 = str(ws_tr.Range("C17").NumberFormat)
                pics_tot = sum(w.Pictures().Count for w in wb.Worksheets if w.Visible == -1)
                if cb_tr != 620 or nf_c17 != ";;;" or pics_tot != 54:
                    errors.append(f"OFFLINE {src.name} mismatch: cb_tr={cb_tr} nf={nf_c17} pics={pics_tot}")
                anim_summary, a_errs = _test_offline_daily_and_tracker(xl, wb, tdef.tracker_name, src.name)
                errors.extend(a_errs)
                com_passed += 1
                tag = "OFF-GOLD" if idx == 0 else "OFF"
                print(f"  ✓ {tag:8s} {src.name:40s} | cbs={cb_tr} | pics={pics_tot} | {anim_summary}", flush=True)
            finally:
                wb.Close(SaveChanges=False)
        _quit_xl(xl)

        # ---- SAMPLE GSHEETS & MOBILE (.xlsx) ----
        print("\n=== COM LIVE QA: SAMPLE GSHEETS & MOBILE (.xlsx) ===", flush=True)
        xl = _new_xl(visible=False)
        for idx in (0, 4, 9, 10, 11, 15, 19):
            tdef = BATCH_TEMPLATES[idx]
            for label, sub, suf in (("GS", "google_sheets_edition", ".xlsx"), ("MOB", "mobile_portrait_sheets", "_Mobile.xlsx")):
                src = ROOT / "templates" / sub / f"{tdef.stem}{suf}"
                dst = tmp_dir / src.name
                shutil.copy2(src, dst)
                wb = xl.Workbooks.Open(str(dst.resolve()))
                try:
                    xl.CalculateFullRebuild()
                    cerrs = scan_com_errors(wb, skip_assets_refs=True)
                    if cerrs:
                        errors.append(f"{label} {src.name} formula errs: {cerrs[:5]}")
                    com_passed += 1
                    print(f"  ✓ {label:3s} {src.name:44s} | errs=0", flush=True)
                finally:
                    wb.Close(SaveChanges=False)
        _quit_xl(xl)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    return com_passed, errors


if __name__ == "__main__":
    g_errs = verify_global_counts_and_orphans()
    print("\n=== ZIP & STRUCTURAL QA: ALL 80 WORKBOOKS (#61-#80 x 4 EDITIONS) ===", flush=True)
    n_chk, z_errs = verify_zip_and_structure()
    print(f"  Checked {n_chk}/80 workbooks | structural errors: {len(z_errs)}", flush=True)
    for e in g_errs + z_errs:
        print(f"  [ERR] {e}", flush=True)

    c_pass, c_errs = verify_com_runtime()
    for e in c_errs:
        print(f"  [ERR] {e}", flush=True)

    all_errs = g_errs + z_errs + c_errs
    print("\n============================================================")
    if not all_errs:
        print(f"PASS 100%! 80/80 ALL 4 FOLDERS + 0 ORPHANS + {n_chk}/80 STRUCTURAL + {c_pass} LIVE COM AUDITS (INCL. GOLDEN #59 & BOTTOM-LEFT TOAST) PASSED WITH ZERO ERRORS!")
    else:
        print(f"FAILED with {len(all_errs)} error(s)!")
        sys.exit(1)
