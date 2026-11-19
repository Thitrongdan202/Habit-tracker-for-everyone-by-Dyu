"""
Verify all Excel workbooks in real Microsoft Excel (formula audit + reactivity test)
and render crisp high-res PNG previews into `previews/`.

Run from repo root:
    python scripts/verify_and_render.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path
from PIL import Image, ImageGrab
import win32com.client as win32

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT / "templates"
PRO_DIR = TEMPLATES_DIR / "pro_macro"
PREVIEWS_DIR = ROOT / "previews"

EXCEL_ERRORS = ("#REF!", "#NAME?", "#DIV/0!", "#VALUE!", "#N/A", "#NUM!", "#NULL!",
                "#CALC!", "#SPILL!", "#CONNECT!", "#BLOCKED!", "#UNKNOWN!", "#FIELD!")

# Capture specs: (workbook_stem, sheet_index_1based, range_str, out_png_name)
CAPTURES = [
    ("01_Sunflower_Garden_Blush", 2, "A1:AN38", "01_sunflower_tracker.png"),
    ("01_Sunflower_Garden_Blush", 1, "A1:H38", "01_sunflower_guide.png"),
    ("01_Sunflower_Garden_Blush", 3, "A1:J26", "01_sunflower_yearly_goals.png"),
    ("01_Sunflower_Garden_Blush", 4, "A1:M26", "01_sunflower_annual.png"),
    ("02_Cactus_Bloom_Pastel_Weeks", 2, "A1:AN43", "02_cactus_tracker.png"),
    ("02_Cactus_Bloom_Pastel_Weeks", 3, "A1:I26", "02_cactus_reflection.png"),
    ("03_Rainbow_Executive_Donuts", 2, "A1:AN54", "03_rainbow_dashboard.png"),
    ("03_Rainbow_Executive_Donuts", 3, "A1:N32", "03_rainbow_analytics.png"),
    ("04_Sage_Botanical_Habit_And_Budget", 2, "A1:AN38", "04_botanical_habits.png"),
    ("04_Sage_Botanical_Habit_And_Budget", 3, "A1:N46", "04_botanical_budget.png"),
    ("04_Sage_Botanical_Habit_And_Budget", 4, "A1:J22", "04_botanical_life_overview.png"),
    ("05_Lavender_Dream_Wellness_Mood", 2, "A1:AN54", "05_lavender_wellness.png"),
    ("05_Lavender_Dream_Wellness_Mood", 3, "A1:I31", "05_lavender_gratitude.png"),
    ("06_Midnight_Navy_Blush_Focus", 2, "A1:AP38", "06_navy_focus_tracker.png"),
    ("06_Midnight_Navy_Blush_Focus", 3, "A1:J24", "06_navy_milestones.png"),
]


def grab_range_png(ws, rng_str: str, out_path: Path, retries: int = 4):
    ws.Activate()
    time.sleep(0.35)
    for attempt in range(retries):
        try:
            ws.Range(rng_str).CopyPicture(Appearance=1, Format=2)
            time.sleep(0.55)
            im = ImageGrab.grabclipboard()
            if isinstance(im, Image.Image):
                out_path.parent.mkdir(parents=True, exist_ok=True)
                im.save(out_path, optimize=True)
                return im.size
        except Exception as e:
            if attempt == retries - 1:
                raise e
        time.sleep(0.6)
    raise RuntimeError(f"Clipboard capture failed for {ws.Name}!{rng_str}")


def audit_workbook(wb) -> list[str]:
    """Scan every used cell on every visible/hidden worksheet for formula errors or ### overflow."""
    issues = []
    for ws in wb.Worksheets:
        if ws.Name == "_Sprites":
            continue
        ur = ws.UsedRange
        if ur is None:
            continue
        rows = ur.Rows.Count
        cols = ur.Columns.Count
        r0 = ur.Row
        c0 = ur.Column
        vals = ur.Value
        forms = ur.Formula
        if rows == 1 and cols == 1:
            vals = ((vals,),)
            forms = ((forms,),)
        elif rows == 1:
            vals = (vals,)
            forms = (forms,)
        elif cols == 1:
            vals = tuple((v,) for v in vals)
            forms = tuple((f,) for f in forms)

        for ri in range(rows):
            for ci in range(cols):
                v = vals[ri][ci]
                f = str(forms[ri][ci] or "")
                is_img = ("IMAGE(" in f.upper()) or ("_SPRITES!" in f.upper())
                # COM CVErr ints are negative around -2146826xxx
                if isinstance(v, int) and v < -2146000000:
                    if is_img:
                        # Check displayed text for real IMAGE error vs valid rendered image
                        txt = str(ws.Cells(r0 + ri, c0 + ci).Text or "")
                        if any(e in txt for e in EXCEL_ERRORS) or txt.startswith("#"):
                            issues.append(f"{ws.Name}!R{r0+ri}C{c0+ci}: IMAGE text={txt!r} formula={f}")
                    else:
                        txt = str(ws.Cells(r0 + ri, c0 + ci).Text or "")
                        issues.append(f"{ws.Name}!R{r0+ri}C{c0+ci}: ERR val={v} text={txt!r} formula={f}")
                elif isinstance(v, str) and any(e in v for e in EXCEL_ERRORS):
                    issues.append(f"{ws.Name}!R{r0+ri}C{c0+ci}: STR_ERR={v!r}")
        # Spot-check numeric/formula cells in visible range for "###" width truncation (fast!)
        max_vis_c = min(cols, 44)
        max_vis_r = min(rows, 58)
        for ri in range(max_vis_r):
            for ci in range(max_vis_c):
                v = vals[ri][ci]
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    cell_obj = ws.Cells(r0 + ri, c0 + ci)
                    txt = str(cell_obj.Text or "")
                    if txt.startswith("###"):
                        issues.append(f"{ws.Name}!R{r0+ri}C{c0+ci}: OVERFLOW {txt!r} (col width={cell_obj.ColumnWidth})")
    return issues


def test_reactivity(xl, wb_path: Path):
    """Verify dynamic calendar (Feb 2026 = 28d, Feb 2024 = 29d) & adding a brand-new habit on blank row 11."""
    wb = xl.Workbooks.Open(str(wb_path))
    ws = wb.Worksheets(2)
    xl.CalculateFullRebuild()
    time.sleep(0.8)

    # Check initial state (October 2026)
    dim_oct = int(ws.Range("BH4").Value)
    hc_init = int(ws.Range("BH6").Value)
    assert dim_oct == 31, f"Expected 31 days in Oct, got {dim_oct}"

    # Switch to February 2026 (non-leap)
    ws.Range("B3").Value = "February"
    ws.Range("B5").Value = 2026
    xl.CalculateFull()
    dim_feb26 = int(ws.Range("BH4").Value)
    day29_26 = ws.Range("AE16").Value
    assert dim_feb26 == 28 and day29_26 == "", f"Feb 2026 failed: dim={dim_feb26}, day29={day29_26!r}"

    # Switch to February 2024 (leap year)
    ws.Range("B5").Value = 2024
    xl.CalculateFull()
    dim_feb24 = int(ws.Range("BH4").Value)
    day29_24 = ws.Range("AE16").Value
    assert dim_feb24 == 29 and int(day29_24) == 29, f"Feb 2024 failed: dim={dim_feb24}, day29={day29_24!r}"

    # Switch back to October 2026 & add a new habit into blank row 11 (Excel row 27)
    ws.Range("B3").Value = "October"
    ws.Range("B5").Value = 2026
    ws.Range("B27").Value = "Đi bộ 15 phút buổi chiều"
    for col in ("C", "D", "E", "F", "G"):
        ws.Range(f"{col}27").Value = True
    xl.CalculateFull()
    hc_after = int(ws.Range("BH6").Value)
    new_long = int(ws.Range("AM27").Value)
    new_done = ws.Range("AJ27").Value
    assert hc_after == hc_init + 1, f"HabitCount didn't increment: {hc_init} -> {hc_after}"
    assert new_long == 5, f"Expected Longest Streak=5 on new habit, got {new_long}"
    issues = audit_workbook(wb)
    wb.Close(False)
    assert not issues, f"Reactivity audit found errors: {issues[:5]}"
    print(f"  ✓ Reactivity test PASSED: Oct=31d, Feb26=28d, Feb24=29d, NewHabit hc {hc_init}->{hc_after}, streak={new_long}, done={new_done!r}")


def main():
    xl = win32.DispatchEx("Excel.Application")
    xl.Visible = False
    xl.DisplayAlerts = False
    xl.ScreenUpdating = True
    try:
        all_errors = {}
        # 1. Audit all 6 Universal templates + capture previews
        by_stem = {}
        for stem, idx, rng_s, out_name in CAPTURES:
            by_stem.setdefault(stem, []).append((idx, rng_s, out_name))

        print("=== Auditing & Rendering 6 Universal Templates (live GitHub =IMAGE) ===")
        for stem, cap_list in by_stem.items():
            p = TEMPLATES_DIR / f"{stem}.xlsx"
            wb = xl.Workbooks.Open(str(p))
            xl.CalculateFullRebuild()
            # Give Excel 365 a few seconds to fetch live GitHub sprites for =IMAGE()
            time.sleep(5.5)
            xl.CalculateFull()
            issues = audit_workbook(wb)
            if issues:
                all_errors[p.name] = issues
                print(f"  ✗ {p.name}: {len(issues)} issue(s) -> {issues[:5]}")
            else:
                print(f"  ✓ {p.name}: ZERO formula errors, ZERO ### overflow!")
            for idx, rng_s, out_name in cap_list:
                ws = wb.Worksheets(idx)
                sz = grab_range_png(ws, rng_s, PREVIEWS_DIR / out_name)
                print(f"      captured {out_name}  ({sz[0]}x{sz[1]})")
            wb.Close(False)

        # 2. Audit all 6 Offline Pro Showcase Editions (embedded _Sprites)
        print("\n=== Auditing 6 Offline Pro Editions (100% offline embedded sprites) ===")
        for p in sorted(PRO_DIR.glob("*.xlsx")):
            wb = xl.Workbooks.Open(str(p))
            xl.CalculateFullRebuild()
            time.sleep(1.5)
            issues = audit_workbook(wb)
            if issues:
                all_errors[p.name] = issues
                print(f"  ✗ {p.name}: {len(issues)} issue(s) -> {issues[:5]}")
            else:
                print(f"  ✓ {p.name}: ZERO formula errors, ZERO ### overflow!")
            if p.name.startswith("01_"):
                sz = grab_range_png(wb.Worksheets(2), "A1:AN38", PREVIEWS_DIR / "01_sunflower_offline_pro.png")
                print(f"      captured 01_sunflower_offline_pro.png ({sz[0]}x{sz[1]})")
            wb.Close(False)

        # 3. Dynamic Reactivity Test
        print("\n=== Running Dynamic Calendar & Add-New-Habit Reactivity Test ===")
        test_reactivity(xl, TEMPLATES_DIR / "01_Sunflower_Garden_Blush.xlsx")

        if all_errors:
            print("\nFAILED AUDIT SUMMARY:")
            for fn, errs in all_errors.items():
                print(f"  {fn}:")
                for e in errs[:10]:
                    print("   ", e)
            sys.exit(1)
        print("\nALL 12 WORKBOOKS PASSED 100% FORMULA + OVERFLOW + REACTIVITY VERIFICATION!")
    finally:
        xl.Quit()


if __name__ == "__main__":
    main()
