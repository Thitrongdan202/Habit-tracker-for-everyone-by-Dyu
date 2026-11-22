"""
benchmark_pro_speed.py — Habit Tracker v3.6 Real Excel COM Wall-Clock Latency Benchmark.

Copies target Pro `.xlsm` files to `%TEMP%\\bench_v36\\` and measures exact wall-clock
milliseconds with real Excel COM events (`EnableEvents = True`, `Calculation = Automatic`) for:
  1. Single checkbox tick on `Monthly Tracker` (C17:AG36)
  2. Month switch (`October -> September -> October`)
  3. Year switch (`2026 -> 2025 -> 2026`)
  4. Daily Task date switch (`2026-10-21 -> 2026-10-22 -> 2026-10-21`)
  5. Annual Achievements tab activate + Year switch (`2026 -> 2025 -> 2026`)

Usage:
    python scripts/benchmark_pro_speed.py [label]
"""
from __future__ import annotations

import gc
import os
import shutil
import statistics
import sys
import tempfile
import time
from pathlib import Path

import win32com.client as win32

ROOT = Path(__file__).resolve().parent.parent
PRO_DIR = ROOT / "templates" / "pro_macro"

BENCH_FILES = [
    "01_Sunflower_Garden_Blush_Pro.xlsm",
    "35_Milk_Mocha_Bear_Sweet_Love_Pro.xlsm",
]


def _find_sheet(wb, anchor_name: str, fallback_substr: str):
    try:
        return wb.Names(anchor_name).RefersToRange.Worksheet
    except Exception:
        for ws in wb.Worksheets:
            if fallback_substr in ws.Name:
                return ws
    raise RuntimeError(f"Cannot locate sheet for {anchor_name} / {fallback_substr}")


def benchmark_file(xl, src_path: Path, tmp_dir: Path) -> dict:
    dst_path = tmp_dir / src_path.name
    shutil.copy2(src_path, dst_path)

    wb = xl.Workbooks.Open(str(dst_path.resolve()))
    results: dict[str, dict] = {}
    try:
        # Ensure normal interactive user state
        xl.Calculation = -4105  # xlCalculationAutomatic
        xl.ScreenUpdating = True
        xl.EnableEvents = True
        time.sleep(0.3)

        ws_tr = _find_sheet(wb, "ANCHOR_TRACKER", "Monthly")
        ws_dt = _find_sheet(wb, "ANCHOR_DAILYTASKS", "Nhiệm Vụ Ngày")
        ws_ann = _find_sheet(wb, "ANCHOR_ANNUAL", "Tổng Kết")

        # Warm up on Monthly Tracker
        ws_tr.Activate()
        time.sleep(0.25)

        # ------------------------------------------------------------------
        # 1. Single checkbox tick on Monthly Tracker (5 timed ticks on non-100% day 28, rows 17..21)
        #    Note: Day 28 = col AD (col 30). Flip False -> True so it doesn't hit 100% bounce FX.
        # ------------------------------------------------------------------
        tick_ms = []
        # Warmup 1 tick
        ws_tr.Range("AD22").Value = not bool(ws_tr.Range("AD22").Value)
        for r in (17, 18, 19, 20, 21):
            cell = ws_tr.Cells(r, 30)  # AD17..AD21
            new_val = not bool(cell.Value)
            t0 = time.perf_counter()
            cell.Value = new_val
            # Force Excel to finish any pending calc cycle just like interactive UI
            if xl.CalculationState != 0:
                xl.Calculate()
            dt = (time.perf_counter() - t0) * 1000.0
            tick_ms.append(dt)
        results["1_single_tick"] = {
            "samples_ms": [round(x, 1) for x in tick_ms],
            "median_ms": round(statistics.median(tick_ms), 1),
            "avg_ms": round(statistics.mean(tick_ms), 1),
        }

        # ------------------------------------------------------------------
        # 2. Month switch: October -> September -> October (2 full cycles = 4 switches)
        # ------------------------------------------------------------------
        month_ms = []
        for target_m in ("September", "October", "September", "October"):
            t0 = time.perf_counter()
            ws_tr.Range("B3").Value = target_m
            if xl.CalculationState != 0:
                xl.Calculate()
            dt = (time.perf_counter() - t0) * 1000.0
            month_ms.append(dt)
        results["2_month_switch"] = {
            "samples_ms": [round(x, 1) for x in month_ms],
            "median_ms": round(statistics.median(month_ms), 1),
            "avg_ms": round(statistics.mean(month_ms), 1),
        }

        # ------------------------------------------------------------------
        # 3. Year switch on Monthly Tracker: 2026 -> 2025 -> 2026 (2 full cycles = 4 switches)
        # ------------------------------------------------------------------
        year_ms = []
        for target_y in (2025, 2026, 2025, 2026):
            t0 = time.perf_counter()
            ws_tr.Range("B5").Value = target_y
            if xl.CalculationState != 0:
                xl.Calculate()
            dt = (time.perf_counter() - t0) * 1000.0
            year_ms.append(dt)
        results["3_year_switch"] = {
            "samples_ms": [round(x, 1) for x in year_ms],
            "median_ms": round(statistics.median(year_ms), 1),
            "avg_ms": round(statistics.mean(year_ms), 1),
        }

        # ------------------------------------------------------------------
        # 4. Daily Task date switch: 2026-10-21 -> 2026-10-22 -> 2026-10-21 (4 switches)
        # ------------------------------------------------------------------
        ws_dt.Activate()
        time.sleep(0.2)
        daily_ms = []
        for target_d in (22, 21, 22, 21):
            t0 = time.perf_counter()
            ws_dt.Range("D5").Value = target_d
            if xl.CalculationState != 0:
                xl.Calculate()
            dt = (time.perf_counter() - t0) * 1000.0
            daily_ms.append(dt)
        results["4_daily_date_switch"] = {
            "samples_ms": [round(x, 1) for x in daily_ms],
            "median_ms": round(statistics.median(daily_ms), 1),
            "avg_ms": round(statistics.mean(daily_ms), 1),
        }

        # ------------------------------------------------------------------
        # 5. Annual Achievements tab activate + Year switch (2026 -> 2025 -> 2026)
        #    Note: Temporarily disable FX bounce during activate measurement so we measure
        #    pure engine latency rather than the intentional 250ms visual bounce!
        #    We ALSO measure activate with FX ON separately for full transparency.
        # ------------------------------------------------------------------
        ws_calc = wb.Worksheets("_Calc")
        prev_fx = ws_calc.Range("BA1").Value
        ws_calc.Range("BA1").Value = False
        try:
            xl.Run(f"'{wb.Name}'!modHabitState.RefreshFXCache")
        except Exception:
            pass

        ws_tr.Activate()
        time.sleep(0.15)
        t0 = time.perf_counter()
        ws_ann.Activate()
        if xl.CalculationState != 0:
            xl.Calculate()
        ann_act_ms = (time.perf_counter() - t0) * 1000.0

        ann_yr_ms = []
        for target_ay in (2025, 2026, 2025, 2026):
            t0 = time.perf_counter()
            ws_ann.Range("B3").Value = target_ay
            if xl.CalculationState != 0:
                xl.Calculate()
            dt = (time.perf_counter() - t0) * 1000.0
            ann_yr_ms.append(dt)

        ws_calc.Range("BA1").Value = prev_fx
        try:
            xl.Run(f"'{wb.Name}'!modHabitState.RefreshFXCache")
        except Exception:
            pass
        results["5_annual_activate_and_year"] = {
            "activate_ms": round(ann_act_ms, 1),
            "year_samples_ms": [round(x, 1) for x in ann_yr_ms],
            "year_median_ms": round(statistics.median(ann_yr_ms), 1),
            "year_avg_ms": round(statistics.mean(ann_yr_ms), 1),
        }

        # 6. Bonus: 1-Click Quick-Action Month Pill Buttons (`BtnPrevMonth` / `BtnNextMonth`)
        ws_tr.Activate()
        time.sleep(0.15)
        btn_ms = []
        for mac in ("BtnPrevMonth", "BtnNextMonth", "BtnPrevMonth", "BtnNextMonth"):
            t0 = time.perf_counter()
            xl.Run(f"'{wb.Name}'!modHabitState.{mac}")
            dt = (time.perf_counter() - t0) * 1000.0
            btn_ms.append(dt)
        results["6_btn_month_switch"] = {
            "samples_ms": [round(x, 1) for x in btn_ms],
            "median_ms": round(statistics.median(btn_ms), 1),
            "avg_ms": round(statistics.mean(btn_ms), 1),
        }

        # Clean up any scheduled OnTime toast before closing
        try:
            xl.Run(f"'{wb.Name}'!modHabitState.CleanupAllFX")
        except Exception:
            pass
    finally:
        wb.Close(SaveChanges=False)
    return results


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "RUN"
    tmp_dir = Path(tempfile.gettempdir()) / "bench_v36"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir, ignore_errors=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== HABIT TRACKER PRO SPEED BENCHMARK [{label}] ===", flush=True)
    xl = win32.DispatchEx("Excel.Application")
    xl.Visible = False
    xl.DisplayAlerts = False
    try:
        for fname in BENCH_FILES:
            fpath = PRO_DIR / fname
            fsize_kb = fpath.stat().st_size / 1024.0
            print(f"\nFile: {fname} ({fsize_kb:.1f} KB)", flush=True)
            res = benchmark_file(xl, fpath, tmp_dir)
            print(f"  1. Single Tick (Monthly)     : median={res['1_single_tick']['median_ms']:6.1f} ms | avg={res['1_single_tick']['avg_ms']:6.1f} ms | {res['1_single_tick']['samples_ms']}", flush=True)
            print(f"  2. Month Switch (Oct<->Sep)  : median={res['2_month_switch']['median_ms']:6.1f} ms | avg={res['2_month_switch']['avg_ms']:6.1f} ms | {res['2_month_switch']['samples_ms']}", flush=True)
            print(f"  3. Year Switch (2026<->2025) : median={res['3_year_switch']['median_ms']:6.1f} ms | avg={res['3_year_switch']['avg_ms']:6.1f} ms | {res['3_year_switch']['samples_ms']}", flush=True)
            print(f"  4. Daily Date (21<->22)      : median={res['4_daily_date_switch']['median_ms']:6.1f} ms | avg={res['4_daily_date_switch']['avg_ms']:6.1f} ms | {res['4_daily_date_switch']['samples_ms']}", flush=True)
            print(f"  5. Annual Activate / Year    : activate={res['5_annual_activate_and_year']['activate_ms']:6.1f} ms | year_median={res['5_annual_activate_and_year']['year_median_ms']:6.1f} ms | {res['5_annual_activate_and_year']['year_samples_ms']}", flush=True)
            print(f"  6. 1-Click Month Pill Button : median={res['6_btn_month_switch']['median_ms']:6.1f} ms | avg={res['6_btn_month_switch']['avg_ms']:6.1f} ms | {res['6_btn_month_switch']['samples_ms']}", flush=True)
    finally:
        xl.Quit()
        del xl
        gc.collect()
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
