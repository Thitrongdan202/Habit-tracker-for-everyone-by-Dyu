"""
sync_vba_toast_01_60.py — Fast, safe VBA-only module swap for templates/pro_macro/01..60_*_Pro.xlsm.
Replaces ONLY the `modHabitState` standard module with the latest `vba_scripts/modHabitState.bas`
(bottom-left toast positioning + gentle slide animation) without touching any sheet, formula,
sprite, chart, or workbook layout!
"""
from __future__ import annotations

import gc
import sys
import time
from pathlib import Path
import win32com.client as win32

ROOT = Path(__file__).resolve().parent.parent
PRO_DIR = ROOT / "templates" / "pro_macro"
BAS_PATH = ROOT / "vba_scripts" / "modHabitState.bas"


def open_excel():
    xl = win32.DispatchEx("Excel.Application")
    xl.Visible = False
    xl.DisplayAlerts = False
    xl.ScreenUpdating = False
    xl.EnableEvents = False
    try:
        xl.AskToUpdateLinks = False
    except Exception:
        pass
    return xl


def close_excel(xl):
    if xl is None:
        return
    try:
        xl.DisplayAlerts = False
        xl.Quit()
    except Exception:
        pass
    del xl
    gc.collect()
    time.sleep(0.4)


def main():
    assert BAS_PATH.exists(), f"Missing {BAS_PATH}"
    bas_text = BAS_PATH.read_text(encoding="ascii")
    assert "visR.Left + 14!" in bas_text and "visR.Height - tH - 18!" in bas_text, (
        "modHabitState.bas does not contain expected bottom-left toast coordinates!"
    )

    files = sorted(
        p for p in PRO_DIR.glob("*_Pro.xlsm")
        if p.name[:2].isdigit() and 1 <= int(p.name[:2]) <= 60
    )
    print(f"Found {len(files)} Pro Macro workbooks (#01-#60) to sync modHabitState.bas.")
    assert len(files) == 60, f"Expected 60 files (#01-#60), found {len(files)}"

    xl = None
    ok = 0
    t0 = time.time()
    try:
        for idx, fpath in enumerate(files, 1):
            if xl is None or (idx - 1) % 10 == 0:
                close_excel(xl)
                xl = open_excel()
            wb = xl.Workbooks.Open(str(fpath.resolve()), UpdateLinks=0, ReadOnly=False)
            try:
                vbp = wb.VBProject
                # Remove old modHabitState module (and any duplicates)
                to_rm = [c for c in vbp.VBComponents if c.Name.startswith("modHabitState")]
                for comp in to_rm:
                    vbp.VBComponents.Remove(comp)
                imported = vbp.VBComponents.Import(str(BAS_PATH.resolve()))
                # Verify bottom-left toast marker is present inside CodeModule
                cm = imported.CodeModule
                code_str = cm.Lines(1, cm.CountOfLines)
                if "visR.Left + 14!" not in code_str or "visR.Height - tH - 18!" not in code_str:
                    raise RuntimeError(f"Imported modHabitState missing bottom-left marker in {fpath.name}")
                wb.Save()
                ok += 1
                if idx % 10 == 0 or idx in (1, 59, 60):
                    print(f"  [{idx:02d}/60] Synced {fpath.name} ({time.time() - t0:.1f}s)")
            finally:
                wb.Close(SaveChanges=False)
                del wb
    finally:
        close_excel(xl)

    print(f"DONE: {ok}/60 Pro Macro workbooks (#01-#60) synced with bottom-left toast in {time.time() - t0:.1f}s.")
    if ok != 60:
        sys.exit(1)


if __name__ == "__main__":
    main()
