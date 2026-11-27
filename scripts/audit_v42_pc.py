"""
audit_v42_pc.py — Mathematical 160-File Whitelist + PIL Overflow Auditor (ZERO temp files, ZERO _build_tmp).

Independently inspects ALL 160 PC workbooks (`80 pro_macro/*.xlsm` + `80 excel_universal_offline/*.xlsx`):
  1. 0 cells using ANY Blacklist font (or outside strict Whitelist)
  2. 0 ALL-CAPS text cells using ANY Script font
  3. 0 Vietnamese text cells using a non-VN-certified font
  4. Mathematical PIL.ImageFont.truetype width audit on EVERY title, theme name, Month (incl. September),
     Weekday (incl. longest VN weekday), Year, KPI & banner cell across ALL 5 sheets:
       rendered_text_width_px <= available_cell_width_px * 0.88
     Asserts 0 / 160 files with ANY overflow!
  5. 0 legacy version strings (v2.1..v4.1), 160/160 copyright + v4.2, 160/160 calcMode=auto, 80/80 VBA binary.
  6. 0 files modified in Google Sheets, Mobile, assets; 0 _build_tmp/ directory; 0 zip files.
"""
from __future__ import annotations

import re
import subprocess
import sys
import warnings
import zipfile
from pathlib import Path

import openpyxl
from openpyxl.utils import column_index_from_string, get_column_letter

warnings.filterwarnings("ignore", category=UserWarning)

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from hx.typography import (
    ALL_ALLOWED_PC_FONTS,
    BLACKLIST_FONTS,
    SCRIPT_WHITELIST,
    has_vietnamese,
    is_all_caps,
    measure_text_px,
    verify_vietnamese_fonts,
)

PRO_DIR = ROOT / "templates" / "pro_macro"
OFF_DIR = ROOT / "templates" / "excel_universal_offline"

GUIDE_SHEET = "📖 Hướng Dẫn"
DAILY_SHEET = "📝 Nhiệm Vụ Ngày"
GOALS_SHEET = "🎯 Yearly Goals & Habits"
ANNUAL_SHEET = "🏆 Tổng Kết & Thành Tựu Năm"
HIDDEN_SHEETS = {"_Calc", "_Database", "_Assets", "_YearHistory"}

LEGACY_VER_RE = re.compile(r"\b[vV](?:2\.1|3\.\d+|4\.[01])\b")


def _excel_col_px(width_chars: float | None) -> float:
    w = 8.43 if (width_chars is None or width_chars <= 0) else float(width_chars)
    if w < 1.0:
        return w * 12.0
    return w * 7.0 + 5.0


def _col_width_map(ws) -> dict[int, float]:
    """Expand openpyxl grouped column_dimensions (min..max) into exact 1-based col -> width map."""
    cmap: dict[int, float] = {}
    for key, dim in ws.column_dimensions.items():
        if dim.width is None or dim.width <= 0:
            continue
        c1 = dim.min or column_index_from_string(key)
        c2 = dim.max or c1
        for c in range(c1, c2 + 1):
            cmap[c] = float(dim.width)
    return cmap


def _merge_width_px(ws, row_1: int, col_1: int, col_w_map: dict[int, float]) -> tuple[float, int]:
    """Return exact Excel pixel width & row span of the cell or its containing merged range."""
    c_start, c_end, r_span = col_1, col_1, 1
    for m in ws.merged_cells.ranges:
        if m.min_row <= row_1 <= m.max_row and m.min_col <= col_1 <= m.max_col:
            c_start, c_end = m.min_col, m.max_col
            r_span = m.max_row - m.min_row + 1
            break
    total_px = 0.0
    for c in range(c_start, c_end + 1):
        total_px += _excel_col_px(col_w_map.get(c))
    return total_px, r_span


def _check_fit(ws, coord: str, test_texts: list[str], overflows: list, fname: str, sname: str, col_w_map: dict[int, float]):
    cell = ws[coord]
    f = cell.font
    if not f or not f.name or not f.size:
        return
    avail_px, _ = _merge_width_px(ws, cell.row, cell.column, col_w_map)
    limit_px = avail_px * 0.88
    for txt in test_texts:
        if not txt or str(txt).startswith("="):
            continue
        w_px, _ = measure_text_px(str(txt), f.name, float(f.size), bold=bool(f.bold), italic=bool(f.italic))
        if w_px > limit_px:
            overflows.append((fname, sname, coord, f.name, float(f.size), round(w_px, 1), round(limit_px, 1), str(txt)[:45]))
            break


def run_audit() -> bool:
    vn_report = verify_vietnamese_fonts()
    vn_safe_fonts = set(vn_report.keys()) | {"Segoe UI", "Arial", "Tahoma", "Verdana", "Be Vietnam Pro"}

    pro_files = sorted(PRO_DIR.glob("[0-9][0-9]_*.xlsm"))
    off_files = sorted(OFF_DIR.glob("[0-9][0-9]_*.xlsx"))
    assert len(pro_files) == 80, f"Expected 80 pro_macro files, got {len(pro_files)}"
    assert len(off_files) == 80, f"Expected 80 offline files, got {len(off_files)}"

    blacklist_hits = []
    non_whitelist_hits = []
    allcaps_script_hits = []
    bad_vn_font_hits = []
    overflow_hits = []
    legacy_hits = []
    missing_v42 = []
    missing_copy = []
    manual_calc = []
    missing_vba = []
    fonts_used = set()
    files_with_overflow = set()

    all_files = [(True, p) for p in pro_files] + [(False, p) for p in off_files]
    for is_pro, p in all_files:
        with zipfile.ZipFile(p, "r") as z:
            names = set(z.namelist())
            if is_pro and "xl/vbaProject.bin" not in names:
                missing_vba.append(p.name)
            wb_xml = z.read("xl/workbook.xml").decode("utf-8", errors="ignore")
            if 'calcMode="manual"' in wb_xml:
                manual_calc.append(p.name)

        wb = openpyxl.load_workbook(p, read_only=False, data_only=False)
        found_v42 = False
        found_copy = False
        for sname in wb.sheetnames:
            ws = wb[sname]
            is_vis = sname not in HIDDEN_SHEETS
            for row in ws.iter_rows():
                for cell in row:
                    val = cell.value
                    if is_vis and cell.font and cell.font.name:
                        fn = cell.font.name
                        if val is not None and str(val).strip() != "":
                            fonts_used.add(fn)
                            if fn in BLACKLIST_FONTS:
                                blacklist_hits.append((p.name, sname, cell.coordinate, fn, str(val)[:40]))
                            elif fn not in ALL_ALLOWED_PC_FONTS:
                                non_whitelist_hits.append((p.name, sname, cell.coordinate, fn, str(val)[:40]))

                    if not isinstance(val, str) or not val:
                        continue
                    if not val.startswith("="):
                        if LEGACY_VER_RE.search(val):
                            legacy_hits.append((p.name, sname, cell.coordinate, val[:80]))
                        if "v4.2" in val or "V4.2" in val:
                            found_v42 = True
                        if "© 2026 Dyu (Thân Trọng Duy)" in val:
                            found_copy = True
                        if is_vis and cell.font and cell.font.name:
                            fn = cell.font.name
                            if has_vietnamese(val) and fn not in vn_safe_fonts:
                                bad_vn_font_hits.append((p.name, sname, cell.coordinate, fn, val[:50]))
                            if is_all_caps(val) and fn in SCRIPT_WHITELIST:
                                allcaps_script_hits.append((p.name, sname, cell.coordinate, fn, val[:50]))

            # Mathematical PIL overflow checks on key display/title/month/KPI cells of every visible sheet
            if not is_vis:
                continue
            cw = _col_width_map(ws)
            before_n = len(overflow_hits)
            if sname == GUIDE_SHEET:
                _check_fit(ws, "B2", [str(ws["B2"].value or "")], overflow_hits, p.name, sname, cw)
                _check_fit(ws, "B3", [str(ws["B3"].value or "")], overflow_hits, p.name, sname, cw)
                _check_fit(ws, "B6", [str(ws["B6"].value or "")], overflow_hits, p.name, sname, cw)
            elif sname == DAILY_SHEET:
                _check_fit(ws, "B2", [str(ws["B2"].value or "")], overflow_hits, p.name, sname, cw)
                _check_fit(ws, "B5", ["Chủ Nhật, 28/09/2026", "Thứ Năm, 28/09/2026"], overflow_hits, p.name, sname, cw)
                _check_fit(ws, "D5", ["31"], overflow_hits, p.name, sname, cw)
                _check_fit(ws, "E5", [str(ws["E5"].value or "October"), "September"], overflow_hits, p.name, sname, cw)
                _check_fit(ws, "F5", ["2026"], overflow_hits, p.name, sname, cw)
                _check_fit(ws, "H2", [str(ws["H2"].value or "")], overflow_hits, p.name, sname, cw)
                _check_fit(ws, "H21", [str(ws["H21"].value or "")], overflow_hits, p.name, sname, cw)
                _check_fit(ws, "H27", [str(ws["H27"].value or "")], overflow_hits, p.name, sname, cw)
                _check_fit(ws, "B30", [str(ws["B30"].value or "")], overflow_hits, p.name, sname, cw)
            elif sname == GOALS_SHEET:
                _check_fit(ws, "B2", [str(ws["B2"].value or "")], overflow_hits, p.name, sname, cw)
                _check_fit(ws, "I2", ["2026"], overflow_hits, p.name, sname, cw)
                _check_fit(ws, "B4", [str(ws["B4"].value or "")], overflow_hits, p.name, sname, cw)
                _check_fit(ws, "D4", [str(ws["D4"].value or "")], overflow_hits, p.name, sname, cw)
                _check_fit(ws, "H4", [str(ws["H4"].value or "")], overflow_hits, p.name, sname, cw)
                for rr in range(11, 20):
                    v = str(ws.cell(rr, 8).value or "")
                    if "PLANTED" in v.upper():
                        _check_fit(ws, f"H{rr}", [v], overflow_hits, p.name, sname, cw)
                        break
            elif sname == ANNUAL_SHEET:
                _check_fit(ws, "B3", ["2026"], overflow_hits, p.name, sname, cw)
                _check_fit(ws, "D2", [str(ws["D2"].value or "")], overflow_hits, p.name, sname, cw)
                _check_fit(ws, "B13", [str(ws["B13"].value or "")], overflow_hits, p.name, sname, cw)
                _check_fit(ws, "B15", [str(ws["B15"].value or "")], overflow_hits, p.name, sname, cw)
                _check_fit(ws, "B33", [str(ws["B33"].value or "")], overflow_hits, p.name, sname, cw)
                _check_fit(ws, "L33", [str(ws["L33"].value or "")], overflow_hits, p.name, sname, cw)
            else:
                # Monthly Tracker sheet
                _check_fit(ws, "B2", [str(ws["B2"].value or "")], overflow_hits, p.name, sname, cw)
                _check_fit(ws, "B3", [str(ws["B3"].value or "October"), "September"], overflow_hits, p.name, sname, cw)
                _check_fit(ws, "B5", ["2026"], overflow_hits, p.name, sname, cw)
                _check_fit(ws, "B9", [str(ws["B9"].value or "")], overflow_hits, p.name, sname, cw)
                _check_fit(ws, "AI3", ["100%"], overflow_hits, p.name, sname, cw)
                if ws["AL4"].value is not None:
                    _check_fit(ws, "AL4", ["264 / 264"], overflow_hits, p.name, sname, cw)
                _check_fit(ws, "AI10", ["31"], overflow_hits, p.name, sname, cw)

            if len(overflow_hits) > before_n:
                files_with_overflow.add(p.name)
        wb.close()

        if not found_v42:
            missing_v42.append(p.name)
        if not found_copy:
            missing_copy.append(p.name)

    # Git scope & disk hygiene checks
    out = subprocess.check_output(
        ["git", "status", "--short",
         "templates/google_sheets_edition", "templates/mobile_portrait_sheets", "assets"],
        cwd=ROOT, text=True,
    ).strip()
    untouched_violations = [line for line in out.splitlines() if line.strip()]
    has_build_tmp = (ROOT / "_build_tmp").exists()
    zips_in_repo = list(ROOT.glob("*.zip"))

    print("=== STRICT 160-FILE WHITELIST + PIL AUTO-FIT AUDIT ===")
    print(f"  Files audited              : {len(all_files)} (80 Pro + 80 Offline)")
    print(f"  Distinct fonts used        : {sorted(fonts_used)}")
    print(f"  Blacklist font hits        : {len(blacklist_hits)}")
    print(f"  Non-whitelist font hits    : {len(non_whitelist_hits)}")
    print(f"  ALL-CAPS + Script hits     : {len(allcaps_script_hits)}")
    print(f"  Bad VN font hits           : {len(bad_vn_font_hits)}")
    print(f"  PIL overflow hits          : {len(overflow_hits)} (across {len(files_with_overflow)} / 160 files)")
    print(f"  Legacy version hits        : {len(legacy_hits)}")
    print(f"  Missing v4.2 / copyright   : {len(missing_v42)} / {len(missing_copy)}")
    print(f"  Manual calcMode / No VBA   : {len(manual_calc)} / {len(missing_vba)}")
    print(f"  Out-of-scope git changes   : {len(untouched_violations)}")
    print(f"  _build_tmp exists / zips   : {has_build_tmp} / {len(zips_in_repo)}")

    for lbl, items in [
        ("BLACKLIST", blacklist_hits[:15]),
        ("NON-WHITELIST", non_whitelist_hits[:15]),
        ("ALLCAPS-SCRIPT", allcaps_script_hits[:15]),
        ("BAD-VN-FONT", bad_vn_font_hits[:15]),
        ("OVERFLOW", overflow_hits[:25]),
        ("LEGACY-VER", legacy_hits[:15]),
        ("OUT-OF-SCOPE", untouched_violations[:15]),
    ]:
        if items:
            print(f"  !! {lbl}:")
            for it in items:
                print("    ", it)

    ok = not (
        blacklist_hits or non_whitelist_hits or allcaps_script_hits or bad_vn_font_hits
        or overflow_hits or legacy_hits or missing_v42 or missing_copy or manual_calc
        or missing_vba or untouched_violations or has_build_tmp or zips_in_repo
    )
    print("RESULT:", "PASS (100% CLEAN — 0 BLACKLIST, 0 ALL-CAPS SCRIPT, 0/160 OVERFLOW)" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    sys.exit(0 if run_audit() else 1)
