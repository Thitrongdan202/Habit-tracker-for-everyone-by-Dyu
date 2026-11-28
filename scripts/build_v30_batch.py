"""
build_v30_batch.py — Unified 4-edition batch builder for Habit & Vocabulary Tracker v4.3 (Templates 01..100).

Runs all 4 editions cleanly with Excel COM recycling every 4-5 templates:
  1. pro     : templates/pro_macro/*_Pro.xlsm (Native Colored Checkboxes + Pure-ASCII VBA + Native Sprites)
  2. offline : templates/excel_universal_offline/*.xlsx (Form Control Checkboxes + `;;;` + Linked Pictures, 0 VBA)
  3. gsheets : templates/google_sheets_edition/*.xlsx (Desktop Cloud + dynamic `=IMAGE()` + SetCheckbox)
  4. mobile  : templates/mobile_portrait_sheets/*_Mobile.xlsx (Portrait + dynamic `=IMAGE()`)
  - Templates #01..#95 (Habit & Holiday): built via `excel_com_enhancer.py` / `build_mobile_templates.py`
  - Templates #96..#100 (Chiikawa Vocabulary): automatically delegated to `scripts/build_vocab_chiikawa.py`

Usage:
    python scripts/build_v30_batch.py --start 81 --end 100
    python scripts/build_v30_batch.py --start 81 --end 95 --editions gsheets,mobile
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

import win32com.client as win32

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from excel_builder import TEMPLATES, build_template
from hx.daily_tasks import DAILY_TASKS_SHEET
from hx.annual import YEARLY_GOALS_SHEET
from hx.guide import GUIDE_SHEET

GSHEETS_DIR = ROOT / "templates" / "google_sheets_edition"


def _com_retry(fn, retries: int = 12, delay: float = 0.25):
    for attempt in range(retries):
        try:
            return fn()
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(delay)


def _run_step(cmd: list[str], label: str):
    print(f"\n=== [{label}] {' '.join(cmd)} ===", flush=True)
    res = subprocess.run(cmd, cwd=str(ROOT))
    if res.returncode != 0:
        raise SystemExit(f"Step failed ({label}) with exit code {res.returncode}")


def build_gsheets_range(start_idx: int, end_idx: int):
    GSHEETS_DIR.mkdir(parents=True, exist_ok=True)
    selected = TEMPLATES[start_idx - 1:end_idx]
    built = []
    print(f"\n=== [gsheets base] Building {len(selected)} Google Sheets .xlsx files ===", flush=True)
    for tdef in selected:
        out_p = GSHEETS_DIR / f"{tdef.stem}.xlsx"
        build_template(tdef, out_p, edition="gsheets")
        built.append((tdef, out_p))
        print(f"  [GSHEETS base] {out_p.name} ({out_p.stat().st_size:,} B)", flush=True)

    print(f"  Post-processing {len(built)} Google Sheets .xlsx via COM (SetCheckbox + calc, recycling every 5)...",
          flush=True)
    xl = None
    try:
        for idx, (tdef, p) in enumerate(built):
            if idx % 5 == 0:
                if xl is not None:
                    try:
                        xl.Quit()
                    except Exception:
                        pass
                    time.sleep(0.4)
                xl = win32.DispatchEx("Excel.Application")
                xl.Visible = False
                xl.DisplayAlerts = False

            t0 = time.perf_counter()
            wb = _com_retry(lambda path=p: xl.Workbooks.Open(str(path.resolve())))
            try:
                ws_tr = wb.Worksheets(tdef.tracker_name)
                ws_dt = wb.Worksheets(DAILY_TASKS_SHEET)
                ws_yg = wb.Worksheets(YEARLY_GOALS_SHEET)
                try:
                    _com_retry(lambda: ws_tr.Range("C17:AG36").CellControl.SetCheckbox())
                    _com_retry(lambda: ws_dt.Range("B9:B28").CellControl.SetCheckbox())
                    _com_retry(lambda: ws_yg.Range("B6:B25").CellControl.SetCheckbox())
                    if tdef.short_key == "03_rainbow":
                        _com_retry(lambda: ws_tr.Range("D42:M43").CellControl.SetCheckbox())
                    elif tdef.short_key == "18_plum_oak":
                        _com_retry(lambda: ws_tr.Range("D42:G43").CellControl.SetCheckbox())
                except Exception:
                    pass
                ws_g = wb.Worksheets(GUIDE_SHEET)
                _com_retry(lambda: ws_g.Activate())
                _com_retry(lambda: ws_g.Range("A1").Select())
                _com_retry(lambda: xl.CalculateFullRebuild())
                _com_retry(lambda: wb.Save())
            finally:
                _com_retry(lambda: wb.Close(SaveChanges=False))
            dt = time.perf_counter() - t0
            print(f"  ✓ [GSHEETS] {p.name} ({p.stat().st_size:,} B, {dt:.1f}s)", flush=True)
    finally:
        if xl is not None:
            try:
                xl.Quit()
            except Exception:
                pass


def main():
    args = sys.argv[1:]
    start_idx = 1
    end_idx = len(TEMPLATES)
    editions = ["pro", "offline", "gsheets", "mobile"]
    i = 0
    while i < len(args):
        if args[i] == "--start" and i + 1 < len(args):
            start_idx = int(args[i + 1]); i += 2
        elif args[i] == "--end" and i + 1 < len(args):
            end_idx = int(args[i + 1]); i += 2
        elif args[i] == "--editions" and i + 1 < len(args):
            editions = [e.strip() for e in args[i + 1].split(",") if e.strip()]; i += 2
        else:
            i += 1

    py = sys.executable
    t_all = time.perf_counter()
    habit_end = min(end_idx, len(TEMPLATES))
    if start_idx <= habit_end:
        if "pro" in editions:
            _run_step([py, "scripts/excel_com_enhancer.py", "pro",
                       "--start", str(start_idx), "--end", str(habit_end)], "PRO .xlsm")
        if "offline" in editions:
            _run_step([py, "scripts/excel_com_enhancer.py", "derive-offline",
                       "--start", str(start_idx), "--end", str(habit_end)], "OFFLINE derive")
            _run_step([py, "scripts/convert_offline_v30.py",
                       "--start", str(start_idx), "--end", str(habit_end)], "OFFLINE Form Checkboxes")
        if "gsheets" in editions:
            build_gsheets_range(start_idx, habit_end)
        if "mobile" in editions:
            _run_step([py, "scripts/build_mobile_templates.py",
                       "--start", str(start_idx), "--end", str(habit_end)], "MOBILE Portrait")
    if end_idx >= 96:
        _run_step([py, "scripts/build_vocab_chiikawa.py"], "CHIIKAWA VOCAB (#96-#100, 4 Editions)")

    print(f"\nALL REQUESTED EDITIONS ({','.join(editions)}) FOR TEMPLATES {start_idx}..{end_idx} "
          f"DONE in {time.perf_counter() - t_all:.1f}s!", flush=True)


if __name__ == "__main__":
    main()
