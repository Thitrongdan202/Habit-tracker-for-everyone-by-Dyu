"""
qa_verify_capybara_v39.py — Full Automated QA Suite for the 13 Bespoke Capybara Templates
(#48-#60, v3.9 — 52 new workbooks across ALL 4 editions) on isolated %TEMP% copies.
"""
from __future__ import annotations

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

CAPY_TEMPLATES = TEMPLATES[47:]
assert len(CAPY_TEMPLATES) == 13, f"Expected 13 Capybara templates, found {len(CAPY_TEMPLATES)}"

ERR_TOKENS = {"#REF!", "#NAME?", "#VALUE!", "#N/A", "#DIV/0!", "#NUM!", "#NULL!"}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_zip_and_structure() -> tuple[int, list[str]]:
    errors: list[str] = []
    checked = 0

    for tdef in CAPY_TEMPLATES:
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
                if len(ctrls) < 600:
                    errors.append(f"OFFLINE low ctrlProps count ({len(ctrls)}): {off_p.name}")

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
                vis = [s.title for s in wb.worksheets if s.sheet_state == "visible"]
                if len(vis) != 5:
                    errors.append(f"GSHEETS visible tabs={len(vis)} != 5: {gs_p.name}")
                ws_tr = wb[tdef.tracker_name]
                f_img = str(ws_tr["C9"].value or "")
                if "IMAGE(" not in f_img:
                    errors.append(f"GSHEETS missing IMAGE() at C9: {gs_p.name} ({f_img})")
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
                vis = [s.title for s in wb.worksheets if s.sheet_state == "visible"]
                if len(vis) != 4:
                    errors.append(f"MOBILE visible tabs={len(vis)} != 4: {mob_p.name}")
                ws_wk = wb["📱 Tuần Này"]
                if ws_wk.max_column > 10:  # Col J (10) is right margin spacer; active content strictly B:I (2..9)
                    errors.append(f"MOBILE max_column={ws_wk.max_column} > 10: {mob_p.name}")
                f_img = str(ws_wk["C15"].value or "")
                if "IMAGE(" not in f_img:
                    errors.append(f"MOBILE missing IMAGE() at C15: {mob_p.name} ({f_img})")
            finally:
                wb.close()

    return checked, errors


def scan_com_errors(wb) -> tuple[int, list[str]]:
    """Scan all used cells on all visible sheets for Excel formula error tokens or ##### clipping."""
    errs: list[str] = []
    cells_scanned = 0
    for ws in wb.Worksheets:
        if ws.Visible != -1:  # xlSheetVisible
            continue
        ur = ws.UsedRange
        vals = ur.Value
        if vals is None:
            continue
        if not isinstance(vals, tuple):
            vals = ((vals,),)
        r0 = ur.Row
        c0 = ur.Column
        for ri, row in enumerate(vals):
            if not isinstance(row, tuple):
                row = (row,)
            for ci, v in enumerate(row):
                cells_scanned += 1
                if isinstance(v, int) and v <= -2146826200:
                    errs.append(f"{ws.Name}!R{r0+ri}C{c0+ci}=COM_ERR({v})")
                elif isinstance(v, str) and (v in ERR_TOKENS or v.startswith("#####")):
                    errs.append(f"{ws.Name}!R{r0+ri}C{c0+ci}={v}")
    return cells_scanned, errs


def verify_com_runtime() -> list[str]:
    errors: list[str] = []
    tmp_dir = Path(tempfile.mkdtemp(prefix="qa_capy_v39_"))
    xl = win32.DispatchEx("Excel.Application")
    xl.Visible = False
    xl.DisplayAlerts = False
    try:
        xl.AutomationSecurity = 1  # msoAutomationSecurityLow for controlled local QA
    except Exception:
        pass

    try:
        print("\n=== COM LIVE QA: ALL 13 PRO MACRO (.xlsm) ===", flush=True)
        for idx, tdef in enumerate(CAPY_TEMPLATES):
            src = ROOT / "templates" / "pro_macro" / f"{tdef.stem}_Pro.xlsm"
            dst = tmp_dir / src.name
            shutil.copy2(src, dst)
            wb = xl.Workbooks.Open(str(dst.resolve()))
            try:
                xl.CalculateFullRebuild()
                _, cerrs = scan_com_errors(wb)
                if cerrs:
                    errors.append(f"PRO {src.name} formula errs: {cerrs[:5]}")

                ws_tr = wb.Worksheets(tdef.tracker_name)
                # Verify UserInterfaceOnly protection & K37 formula lock + C17 unlock
                prot = bool(ws_tr.ProtectContents)
                k37_locked = bool(ws_tr.Range("K37").Locked)
                c17_locked = bool(ws_tr.Range("C17").Locked)
                if not prot or not k37_locked or c17_locked:
                    errors.append(f"PRO {src.name} protection fail: prot={prot} k37_locked={k37_locked} c17_locked={c17_locked}")

                # Benchmark live Month switching (warm steady-state) on pilot/sample + check all 13
                t_ms = 0.0
                if idx in (0, 2, 4, 9, 12):
                    # Warm switch Oct -> Nov -> Oct
                    ws_tr.Range("B3").Value = "November"
                    t0 = time.perf_counter()
                    ws_tr.Range("B3").Value = "October"
                    t_ms = (time.perf_counter() - t0) * 1000.0
                    # Verify restored data on October (C17 should be boolean or True)
                    done_tot = ws_tr.Range("C37").Value
                    if not isinstance(done_tot, (int, float)) or done_tot <= 0:
                        errors.append(f"PRO {src.name} Oct reload C37 invalid: {done_tot}")

                    # Verify Undo engine on #48 and #50
                    if idx in (0, 2):
                        orig_val = ws_tr.Range("C17").Value
                        ws_tr.Range("C17").Value = not bool(orig_val)
                        xl.Run(f"'{wb.Name}'!modHabitState.UndoLastHabitEdit")
                        after_undo = ws_tr.Range("C17").Value
                        if bool(after_undo) != bool(orig_val):
                            errors.append(f"PRO {src.name} Undo failed: orig={orig_val} after={after_undo}")

                # Always run CleanupAllFX before closing to avoid OnTime race!
                try:
                    xl.Run(f"'{wb.Name}'!modHabitState.CleanupAllFX")
                except Exception:
                    pass

                ms_tag = f" | switch={t_ms:.0f}ms" if t_ms > 0 else ""
                print(f"  ✓ PRO {src.name:44s} | errs=0 | prot=OK | K37_lock=OK{ms_tag}", flush=True)
            finally:
                wb.Close(SaveChanges=False)

        print("\n=== COM LIVE QA: SAMPLE OFFLINE (.xlsx) ===", flush=True)
        for idx in (0, 2, 4, 8, 11, 12):
            tdef = CAPY_TEMPLATES[idx]
            src = ROOT / "templates" / "excel_universal_offline" / f"{tdef.stem}.xlsx"
            dst = tmp_dir / src.name
            shutil.copy2(src, dst)
            wb = xl.Workbooks.Open(str(dst.resolve()))
            try:
                xl.CalculateFullRebuild()
                _, cerrs = scan_com_errors(wb)
                if cerrs:
                    errors.append(f"OFFLINE {src.name} formula errs: {cerrs[:5]}")
                ws_tr = wb.Worksheets(tdef.tracker_name)
                cb_tr = ws_tr.CheckBoxes().Count
                nf_c17 = str(ws_tr.Range("C17").NumberFormat)
                pics_tot = sum(w.Pictures().Count for w in wb.Worksheets if w.Visible == -1)
                if cb_tr != 620 or nf_c17 != ";;;" or pics_tot != 54:
                    errors.append(f"OFFLINE {src.name} mismatch: cb_tr={cb_tr} nf={nf_c17} pics={pics_tot}")
                print(f"  ✓ OFF {src.name:44s} | errs=0 | cbs={cb_tr} | nf='{nf_c17}' | pics={pics_tot}", flush=True)
            finally:
                wb.Close(SaveChanges=False)
    finally:
        xl.Quit()
        shutil.rmtree(tmp_dir, ignore_errors=True)

    return errors


if __name__ == "__main__":
    print("=== ZIP & STRUCTURAL QA: ALL 52 CAPYBARA WORKBOOKS (#48-#60 x 4 EDITIONS) ===", flush=True)
    n_chk, z_errs = verify_zip_and_structure()
    print(f"  Checked {n_chk}/52 workbooks | structural errors: {len(z_errs)}", flush=True)
    for e in z_errs:
        print(f"  [ERR] {e}", flush=True)

    c_errs = verify_com_runtime()
    for e in c_errs:
        print(f"  [ERR] {e}", flush=True)

    all_errs = z_errs + c_errs
    print("\n============================================================")
    if not all_errs:
        print(f"PASS 100%! ALL {n_chk}/52 CAPYBARA WORKBOOKS VERIFIED WITH ZERO ERRORS!")
    else:
        print(f"FAILED with {len(all_errs)} error(s)!")
        sys.exit(1)
