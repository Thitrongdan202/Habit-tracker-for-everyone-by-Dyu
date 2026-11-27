"""
apply_v42_typography_pc.py — Safe Excel COM batch upgrader for Release v4.2.

Applies the curated 80-theme 3-tier Typography system + v4.2 version & author copyright
across ALL 160 PC Excel workbooks:
  - templates/pro_macro/*.xlsm (80 files)
  - templates/excel_universal_offline/*.xlsx (80 files)

NEVER uses openpyxl.save() — preserves 100% of VBA Macros, Form Control Checkboxes,
bottom-left Toast, Linked Pictures, charts, and worksheet protection!
NEVER touches templates/google_sheets_edition/, templates/mobile_portrait_sheets/, or assets/.
"""
from __future__ import annotations

import argparse
import gc
import re
import shutil
import sys
import time
from pathlib import Path

import pythoncom
import win32com.client as win32

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from excel_builder import TEMPLATES
from hx.core import REPO_URL, cell as xl_cell
from hx.typography import TypographySpec, get_typography, has_vietnamese

PRO_DIR = ROOT / "templates" / "pro_macro"
OFF_DIR = ROOT / "templates" / "excel_universal_offline"

GUIDE_SHEET = "📖 Hướng Dẫn"
DAILY_SHEET = "📝 Nhiệm Vụ Ngày"
GOALS_SHEET = "🎯 Yearly Goals & Habits"
ANNUAL_SHEET = "🏆 Tổng Kết & Thành Tựu Năm"
HIDDEN_SHEETS = {"_Calc", "_Database", "_Assets", "_YearHistory"}

_VER_TOKEN_RE = re.compile(r"\b([vV])[234]\.\d+(\s+(?:Turbo|TURBO|Universal|UNIVERSAL))?\b")


def _norm_ver_text(txt: str, is_pro: bool) -> str:
    """Idempotently upgrade any legacy version string (v2.1..v4.1) in plain text to v4.2."""
    if not txt:
        return txt

    def _repl(m: re.Match) -> str:
        prefix = m.group(1)
        suffix = m.group(2) or ""
        if is_pro:
            if suffix.strip() == "TURBO" or prefix == "V":
                return "V4.2 TURBO"
            return "v4.2 Turbo"
        else:
            if suffix.strip() == "UNIVERSAL" or prefix == "V":
                return "V4.2 UNIVERSAL"
            return "v4.2 Universal"

    return _VER_TOKEN_RE.sub(_repl, txt)


def _safe_text(rng) -> str:
    try:
        v = rng.Text
        if v:
            return str(v)
    except Exception:
        pass
    try:
        v = rng.Value
        return "" if v is None else str(v)
    except Exception:
        return ""


def _is_formula(cell) -> bool:
    try:
        f = cell.Formula
        return isinstance(f, str) and f.startswith("=")
    except Exception:
        return False


def _set_font(rng, font_name: str, *, typo: TypographySpec, size: float | None = None,
              bold: bool | None = None, italic: bool | None = None, check_vn: bool = True):
    """Apply font safely: automatically prevents non-VN display_en from touching Vietnamese text."""
    final_font = font_name
    final_bold = bold
    final_italic = italic
    if check_vn and final_font == typo.display_en:
        txt = _safe_text(rng)
        if has_vietnamese(txt):
            final_font = typo.title_vn
            if final_bold is None or not final_bold:
                final_bold = True
            final_italic = typo.title_vn_italic
    f = rng.Font
    f.Name = final_font
    if size is not None:
        f.Size = float(size)
    if final_bold is not None:
        f.Bold = bool(final_bold)
    if final_italic is not None:
        f.Italic = bool(final_italic)


def _boost_row(ws, row_1: int, min_h: float):
    try:
        cur = float(ws.Rows(row_1).RowHeight or 0)
        if cur < min_h:
            ws.Rows(row_1).RowHeight = float(min_h)
    except Exception:
        pass


def _unprotect_if_needed(ws) -> bool:
    try:
        if bool(ws.ProtectContents):
            ws.Unprotect("")
            return True
    except Exception:
        pass
    return False


def _reprotect(ws, was_prot: bool):
    if not was_prot:
        return
    ws.Protect(
        Password="",
        DrawingObjects=False,
        Contents=True,
        Scenarios=False,
        UserInterfaceOnly=True,
        AllowFormattingCells=False,
    )


def _update_chart_titles(ws, title_font: str):
    try:
        for i in range(1, ws.ChartObjects().Count + 1):
            co = ws.ChartObjects(i)
            ch = co.Chart
            if ch.HasTitle:
                ch.ChartTitle.Font.Name = title_font
                ch.ChartTitle.Font.Bold = True
    except Exception:
        pass


def _upgrade_guide(ws, typo: TypographySpec, is_pro: bool):
    was_prot = _unprotect_if_needed(ws)
    try:
        ur = ws.UsedRange
        ur.Font.Name = typo.body_ui
        r0, c0 = ur.Row, ur.Column
        vals = ur.Value
        forms = ur.Formula
        if not isinstance(vals, tuple):
            vals = ((vals,),)
            forms = ((forms,),)

        ver_tag = "v4.2 Turbo" if is_pro else "v4.2 Universal"
        foot_txt = (
            f"💛  © 2026 Dyu (Thân Trọng Duy)  •  Habit Tracker Collection v4.2 Pro Turbo  •  {REPO_URL}"
            if is_pro else
            f"💛  © 2026 Dyu (Thân Trọng Duy)  •  Habit Tracker Collection v4.2 Universal  •  {REPO_URL}"
        )

        # B2 Hero Banner
        c_b2 = ws.Cells(2, 2)
        v2 = vals[2 - r0][2 - c0] if (2 >= r0 and 2 - r0 < len(vals) and 2 >= c0 and 2 - c0 < len(vals[0])) else c_b2.Value
        if isinstance(v2, str) and not v2.startswith("="):
            nv2 = _norm_ver_text(v2, is_pro)
            if nv2 != v2:
                c_b2.Value = nv2
        _set_font(c_b2.MergeArea, typo.title_vn, typo=typo, size=16.5, bold=True,
                  italic=typo.title_vn_italic, check_vn=False)
        _boost_row(ws, 2, 42)

        # B3 Tagline
        _set_font(ws.Cells(3, 2).MergeArea, typo.title_vn, typo=typo, size=10.5, bold=False,
                  italic=True, check_vn=False)
        _boost_row(ws, 3, 26)

        # B4 Mode Bar
        v4 = vals[4 - r0][2 - c0] if (4 >= r0 and 4 - r0 < len(vals) and 2 >= c0 and 2 - c0 < len(vals[0])) else ws.Cells(4, 2).Value
        if isinstance(v4, str) and not v4.startswith("="):
            nv4 = _norm_ver_text(v4, is_pro)
            if nv4 != v4:
                ws.Cells(4, 2).Value = nv4

        # Fast in-memory scan over bulk-read array (ZERO COM calls on empty/unchanged cells!)
        sec_prefixes = (
            "🗂️", "📌  1.", "⚡  2.", "🧩  3.", "🏆  4.", "🎨  5.", "⚡  5.",
            "📌 1.", "⚡ 2.", "🧩 3.", "🏆 4.", "🎨 5.", "⚡ 5.",
        )
        sec_full_cells = []
        sec_half_cells = []
        boost_28_rows = set()

        for ri, row_vals in enumerate(vals):
            r = r0 + ri
            if r < 5:
                continue
            row_forms = forms[ri]
            for ci, val in enumerate(row_vals):
                c = c0 + ci
                if c < 2 or c > 9:
                    continue
                if not isinstance(val, str) or not val.strip():
                    continue
                f_str = row_forms[ci]
                if isinstance(f_str, str) and f_str.startswith("="):
                    continue
                s = val.strip()

                # Footer detection
                if "Habit Tracker Collection" in s and ("github.com" in s or "by Dyu" in s or "©" in s):
                    cell = ws.Cells(r, c)
                    if val != foot_txt:
                        cell.Value = foot_txt
                    _set_font(cell.MergeArea, typo.title_vn, typo=typo, size=9.5, bold=False, italic=True, check_vn=False)
                    _boost_row(ws, r, 30)
                    continue

                # Upgrade any legacy version string in text cells
                if _VER_TOKEN_RE.search(s):
                    nv = _norm_ver_text(val, is_pro)
                    if nv != val:
                        ws.Cells(r, c).Value = nv
                    s = nv.strip()

                # Section header detection
                if any(s.startswith(p) for p in sec_prefixes):
                    addr = xl_cell(r - 1, c - 1)
                    if s.startswith(("🗂️", "🎨", "⚡  5.", "⚡ 5.")):
                        sec_full_cells.append(addr)
                    else:
                        sec_half_cells.append(addr)
                    boost_28_rows.add(r)

        if sec_full_cells:
            _set_font(ws.Range(",".join(sec_full_cells)), typo.title_vn, typo=typo, size=11.0, bold=True, check_vn=False)
        if sec_half_cells:
            _set_font(ws.Range(",".join(sec_half_cells)), typo.title_vn, typo=typo, size=10.5, bold=True, check_vn=False)
        for br in boost_28_rows:
            _boost_row(ws, br, 28)
    finally:
        _reprotect(ws, was_prot)


def _upgrade_tracker(ws, typo: TypographySpec):
    was_prot = _unprotect_if_needed(ws)
    try:
        ur = ws.UsedRange
        ur.Font.Name = typo.body_ui
        r0, c0 = ur.Row, ur.Column
        vals = ur.Value
        forms = ur.Formula
        if not isinstance(vals, tuple):
            vals = ((vals,),)
            forms = ((forms,),)
        en = typo.en_optics

        def _val_at(r1: int, c1: int):
            ri, ci = r1 - r0, c1 - c0
            if 0 <= ri < len(vals) and 0 <= ci < len(vals[ri]):
                return vals[ri][ci]
            return None

        def _form_at(r1: int, c1: int):
            ri, ci = r1 - r0, c1 - c0
            if 0 <= ri < len(forms) and 0 <= ci < len(forms[ri]):
                return forms[ri][ci]
            return None

        # B2: Top label tag
        t_b2 = str(_val_at(2, 2) or "")
        if has_vietnamese(t_b2):
            _set_font(ws.Cells(2, 2), typo.title_vn, typo=typo, size=9.5, bold=True, check_vn=False)
        else:
            _set_font(ws.Cells(2, 2), typo.display_en, typo=typo, size=min(11.5, 9.0 + en.size_delta * 0.4),
                      bold=en.bold, italic=en.italic, check_vn=False)
        _boost_row(ws, 2, 21 + en.rh_boost * 0.4)

        # B3: Month name (October)
        m_sz = min(en.max_month_pt, 17.5 + en.size_delta)
        _set_font(ws.Cells(3, 2), typo.display_en, typo=typo, size=m_sz, bold=en.bold, italic=en.italic, check_vn=False)
        _boost_row(ws, 3, 30 + en.rh_boost)

        # B5: Year (2026)
        _set_font(ws.Cells(5, 2), typo.num_font, typo=typo, size=14.0, bold=True, check_vn=False)
        _boost_row(ws, 5, 25)

        # B9: Garden / Theme Hero label
        t_b9 = str(_val_at(9, 2) or "")
        if has_vietnamese(t_b9):
            _set_font(ws.Cells(9, 2), typo.title_vn, typo=typo, size=12.0, bold=True,
                      italic=typo.title_vn_italic, check_vn=False)
        else:
            _set_font(ws.Cells(9, 2), typo.display_en, typo=typo, size=min(15.5, 11.5 + en.size_delta * 0.55),
                      bold=en.bold, italic=en.italic, check_vn=False)

        # Top-right KPI numbers grouped: AI3 (15.5), AL4+AL6 (12.5), AI10 (26.0)
        if _val_at(3, 35) is not None or _form_at(3, 35):
            _set_font(ws.Cells(3, 35), typo.num_font, typo=typo, size=15.5, bold=True, check_vn=False)
        al_addrs = []
        if _val_at(4, 38) is not None or _form_at(4, 38):
            al_addrs.append("AL4")
        if _val_at(6, 38) is not None or _form_at(6, 38):
            al_addrs.append("AL6")
        if al_addrs:
            _set_font(ws.Range(",".join(al_addrs)), typo.num_font, typo=typo, size=12.5, bold=True, check_vn=False)
        if _val_at(10, 35) is not None or _form_at(10, 35):
            _set_font(ws.Cells(10, 35), typo.num_font, typo=typo, size=26.0, bold=True, check_vn=False)

        # Fast in-memory scan for addon section headers (Rows 39+)
        vn_hdr_addrs = []
        en_hdr_addrs = []
        boost_rows_en = set()
        boost_rows_vn = set()

        for ri, row_vals in enumerate(vals):
            r = r0 + ri
            if r < 39:
                continue
            row_forms = forms[ri]
            for ci, val in enumerate(row_vals):
                c = c0 + ci
                if c < 2 or not isinstance(val, str):
                    continue
                f_str = row_forms[ci]
                if isinstance(f_str, str) and f_str.startswith("="):
                    continue
                s = val.strip()
                if len(s) < 5 or s.upper().startswith("WEEK "):
                    continue
                # Quick heuristic: addon banners are uppercase titles or emoji-prefixed headers
                letters = [ch for ch in s if ch.isalpha()]
                if not letters:
                    continue
                upper_ratio = sum(1 for ch in letters if ch.isupper()) / len(letters)
                if upper_ratio < 0.72:
                    continue
                cell = ws.Cells(r, c)
                ma = cell.MergeArea
                if ma.Row != r or ma.Column != c or ma.Columns.Count < 3:
                    continue
                try:
                    if not bool(cell.Font.Bold) or int(cell.Interior.Color or 16777215) == 16777215:
                        continue
                except Exception:
                    continue
                addr = xl_cell(r - 1, c - 1)
                if has_vietnamese(s):
                    vn_hdr_addrs.append(addr)
                    boost_rows_vn.add(r)
                elif len(s) <= 52:
                    en_hdr_addrs.append(addr)
                    boost_rows_en.add(r)

        if vn_hdr_addrs:
            _set_font(ws.Range(",".join(vn_hdr_addrs)), typo.title_vn, typo=typo, size=10.5, bold=True, check_vn=False)
        if en_hdr_addrs:
            _set_font(ws.Range(",".join(en_hdr_addrs)), typo.display_en, typo=typo,
                      size=min(13.5, 10.5 + en.size_delta * 0.4), bold=en.bold, italic=en.italic, check_vn=False)
        for br in boost_rows_vn:
            _boost_row(ws, br, 24)
        for br in boost_rows_en:
            _boost_row(ws, br, 24 + en.rh_boost * 0.5)

        _update_chart_titles(ws, typo.title_vn)
    finally:
        _reprotect(ws, was_prot)


def _upgrade_daily_tasks(ws, typo: TypographySpec):
    was_prot = _unprotect_if_needed(ws)
    try:
        ws.UsedRange.Font.Name = typo.body_ui
        en = typo.en_optics

        _set_font(ws.Range("B2"), typo.title_vn, typo=typo, size=15.5, bold=True,
                  italic=typo.title_vn_italic, check_vn=False)
        _boost_row(ws, 2, 34)

        _set_font(ws.Range("B5"), typo.title_vn, typo=typo, size=13.5, bold=True,
                  italic=typo.title_vn_italic, check_vn=False)
        _set_font(ws.Range("D5,F5"), typo.num_font, typo=typo, size=13.5, bold=True, check_vn=False)
        _set_font(ws.Range("E5"), typo.display_en, typo=typo, size=min(16.5, 13.0 + en.size_delta * 0.65),
                  bold=en.bold, italic=en.italic, check_vn=False)
        _boost_row(ws, 5, 30 + en.rh_boost)

        _set_font(ws.Range("H2,B30"), typo.title_vn, typo=typo, size=10.0, bold=True, check_vn=False)
        _set_font(ws.Range("H4"), typo.num_font, typo=typo, size=20.0, bold=True, check_vn=False)
        _set_font(ws.Range("H21,H27"), typo.title_vn, typo=typo, size=9.0, bold=True, check_vn=False)
        _boost_row(ws, 30, 26)
    finally:
        _reprotect(ws, was_prot)


def _upgrade_yearly_goals(ws, typo: TypographySpec):
    was_prot = _unprotect_if_needed(ws)
    try:
        ur = ws.UsedRange
        ur.Font.Name = typo.body_ui
        en = typo.en_optics

        _set_font(ws.Range("B2"), typo.display_en, typo=typo,
                  size=min(21.0, 16.0 + en.size_delta * 0.75), bold=en.bold, italic=en.italic, check_vn=False)
        _boost_row(ws, 2, 38 + en.rh_boost)

        _set_font(ws.Range("I2"), typo.num_font, typo=typo, size=15.0, bold=True, check_vn=False)
        _set_font(ws.Range("B4,D4"), typo.title_vn, typo=typo, size=10.5, bold=True, check_vn=False)
        _set_font(ws.Range("H4"), typo.title_vn, typo=typo, size=10.0, bold=True, check_vn=False)
        _boost_row(ws, 4, 28)

        # Single bulk read of H11:H20 to locate "YOU HAVE PLANTED:"
        col_h = ws.Range("H11:H20").Value
        for idx, row_t in enumerate(col_h):
            txt = str(row_t[0] or "") if isinstance(row_t, tuple) else str(row_t or "")
            if "PLANTED" in txt.upper():
                rp = 11 + idx
                _set_font(ws.Cells(rp, 8), typo.display_en, typo=typo,
                          size=min(13.5, 10.5 + en.size_delta * 0.5), bold=en.bold, italic=en.italic, check_vn=False)
                _boost_row(ws, rp, 26 + en.rh_boost * 0.4)
                _set_font(ws.Cells(rp + 1, 8), typo.num_font, typo=typo, size=28.0, bold=True, check_vn=False)
                break
    finally:
        _reprotect(ws, was_prot)


def _upgrade_annual(ws, typo: TypographySpec):
    was_prot = _unprotect_if_needed(ws)
    try:
        ws.UsedRange.Font.Name = typo.body_ui
        en = typo.en_optics

        _set_font(ws.Range("B3"), typo.num_font, typo=typo, size=16.5, bold=True, check_vn=False)
        _boost_row(ws, 2, 22)
        _boost_row(ws, 3, 32)
        _boost_row(ws, 4, 21)

        _set_font(ws.Range("D2"), typo.title_vn, typo=typo, size=16.5, bold=True,
                  italic=typo.title_vn_italic, check_vn=False)
        _set_font(ws.Range("D4"), typo.title_vn, typo=typo, size=10.0, bold=False, italic=True, check_vn=False)

        # 4 Big KPIs + Badge counter (L34): group same sizes!
        _set_font(ws.Range("B7,L34"), typo.num_font, typo=typo, size=26.0, bold=True, check_vn=False)
        _set_font(ws.Range("E7"), typo.num_font, typo=typo, size=18.0, bold=True, check_vn=False)
        _set_font(ws.Range("I7"), typo.num_font, typo=typo, size=22.0, bold=True, check_vn=False)
        _set_font(ws.Range("L7"), typo.num_font, typo=typo, size=24.0, bold=True, check_vn=False)

        # Section headers grouped
        _set_font(ws.Range("B13,B33"), typo.title_vn, typo=typo, size=10.5, bold=True, check_vn=False)
        _boost_row(ws, 13, 26)
        _boost_row(ws, 33, 28)

        t_l33 = str(ws.Cells(33, 12).Value or "")
        if has_vietnamese(t_l33):
            _set_font(ws.Range("B15,L33"), typo.title_vn, typo=typo, size=10.0, bold=True, check_vn=False)
        else:
            _set_font(ws.Range("B15"), typo.title_vn, typo=typo, size=10.0, bold=True, check_vn=False)
            _set_font(ws.Range("L33"), typo.display_en, typo=typo,
                      size=min(13.0, 10.0 + en.size_delta * 0.45), bold=en.bold, italic=en.italic, check_vn=False)

        _update_chart_titles(ws, typo.title_vn)
    finally:
        _reprotect(ws, was_prot)


def _upgrade_hidden(wb, is_pro: bool):
    # _Calc!BA16 (FX_MSG_DEMO)
    try:
        ws_c = wb.Worksheets("_Calc")
        c_ba16 = ws_c.Cells(16, 53)  # Col BA = 53
        if not _is_formula(c_ba16):
            v = str(c_ba16.Value or "")
            if v and ("v3." in v.lower() or "v4." in v.lower()):
                c_ba16.Value = "🎉 Hiệu ứng Pro v4.2 Turbo đang BẬT — Siêu tốc & sống động!"
    except Exception:
        pass

    # _Assets!C1
    try:
        ws_a = wb.Worksheets("_Assets")
        c_c1 = ws_a.Cells(1, 3)
        if not _is_formula(c_c1):
            v = str(c_c1.Value or "")
            if v:
                c_c1.Value = re.sub(r"\(v\d+\.\d+\)", "(v4.2)", v, flags=re.IGNORECASE)
    except Exception:
        pass


def _export_sheet_png(ws, rng_addr: str, out_png: Path):
    """Export a range from an Excel worksheet to PNG via CopyPicture + temporary ChartObject."""
    was_prot = _unprotect_if_needed(ws)
    co = None
    try:
        ws.Activate()
        time.sleep(0.2)
        rng = ws.Range(rng_addr)
        rng.CopyPicture(Appearance=1, Format=2)  # xlScreen, xlBitmap
        time.sleep(0.2)
        w = max(400, rng.Width)
        h = max(300, rng.Height)
        co = ws.ChartObjects().Add(0, 0, w, h)
        co.Activate()
        time.sleep(0.25)
        co.Chart.Paste()
        time.sleep(0.25)
        out_png.parent.mkdir(parents=True, exist_ok=True)
        co.Chart.Export(str(out_png.resolve()), "PNG")
    finally:
        if co is not None:
            try:
                co.Delete()
            except Exception:
                pass
        _reprotect(ws, was_prot)


def upgrade_workbook(xl, wb_path: Path, slug: str, is_pro: bool, preview_dir: Path | None = None,
                     tag: str = ""):
    typo = get_typography(slug)
    wb = xl.Workbooks.Open(str(wb_path.resolve()), UpdateLinks=0, ReadOnly=False)
    try:
        tracker_ws = None
        for i in range(1, wb.Worksheets.Count + 1):
            ws = wb.Worksheets(i)
            nm = ws.Name
            if nm == GUIDE_SHEET:
                _upgrade_guide(ws, typo, is_pro)
            elif nm == DAILY_SHEET:
                _upgrade_daily_tasks(ws, typo)
            elif nm == GOALS_SHEET:
                _upgrade_yearly_goals(ws, typo)
            elif nm == ANNUAL_SHEET:
                _upgrade_annual(ws, typo)
            elif nm not in HIDDEN_SHEETS:
                tracker_ws = ws
                _upgrade_tracker(ws, typo)

        _upgrade_hidden(wb, is_pro)
        wb.Save()

        if preview_dir is not None:
            xl.ScreenUpdating = True
            ed = "pro" if is_pro else "off"
            p_tag = tag or slug
            if tracker_ws is not None:
                _export_sheet_png(tracker_ws, "A1:AN38", preview_dir / f"{p_tag}_{ed}_01_tracker.png")
            ws_g = wb.Worksheets(GUIDE_SHEET)
            g_lr = ws_g.UsedRange.Row + ws_g.UsedRange.Rows.Count
            g_lc = "J" if ws_g.UsedRange.Columns.Count >= 9 else ("I" if ws_g.UsedRange.Columns.Count == 8 else "H")
            _export_sheet_png(ws_g, f"A1:{g_lc}{min(42, g_lr + 1)}", preview_dir / f"{p_tag}_{ed}_02_guide.png")
            _export_sheet_png(wb.Worksheets(DAILY_SHEET), "A1:I34", preview_dir / f"{p_tag}_{ed}_03_daily.png")
            _export_sheet_png(wb.Worksheets(GOALS_SHEET), "A1:J26", preview_dir / f"{p_tag}_{ed}_04_goals.png")
            _export_sheet_png(wb.Worksheets(ANNUAL_SHEET), "A1:O43", preview_dir / f"{p_tag}_{ed}_05_annual.png")
            xl.ScreenUpdating = False
    finally:
        wb.Close(SaveChanges=False)


def _open_excel():
    xl = win32.DispatchEx("Excel.Application")
    xl.Visible = False
    xl.DisplayAlerts = False
    xl.ScreenUpdating = False
    xl.EnableEvents = False
    xl.AskToUpdateLinks = False
    return xl


def _close_excel(xl):
    if xl is None:
        return
    try:
        xl.DisplayAlerts = False
        xl.Quit()
    except Exception:
        pass
    del xl
    gc.collect()
    time.sleep(1.5)


def collect_jobs(edition: str, start: int, end: int, only_ids: list[int] | None = None) -> list[tuple[int, str, bool, Path]]:
    jobs: list[tuple[int, str, bool, Path]] = []
    pro_map = {int(p.name[:2]): p for p in sorted(PRO_DIR.glob("[0-9][0-9]_*.xlsm"))}
    off_map = {int(p.name[:2]): p for p in sorted(OFF_DIR.glob("[0-9][0-9]_*.xlsx"))}
    assert len(pro_map) == 80, f"Expected 80 pro_macro files, got {len(pro_map)}"
    assert len(off_map) == 80, f"Expected 80 offline files, got {len(off_map)}"

    indices = only_ids if only_ids else list(range(start, end + 1))
    for idx in indices:
        slug = TEMPLATES[idx - 1].theme.slug
        if edition in ("pro", "both"):
            jobs.append((idx, slug, True, pro_map[idx]))
        if edition in ("offline", "both"):
            jobs.append((idx, slug, False, off_map[idx]))
    return jobs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--edition", choices=["pro", "offline", "both"], default="both")
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int, default=80)
    ap.add_argument("--ids", type=str, default="", help="Comma-separated 1-based theme IDs, e.g. 1,4,19,61,80")
    ap.add_argument("--recycle", type=int, default=8, help="Recycle EXCEL.EXE every N workbooks")
    ap.add_argument("--pilot-dir", type=str, default="", help="Copy targets into this temp dir instead of editing live files")
    ap.add_argument("--preview-out", type=str, default="", help="Export 5-sheet PNG previews into this directory")
    args = ap.parse_args()

    only_ids = [int(x.strip()) for x in args.ids.split(",") if x.strip()] if args.ids else None
    jobs = collect_jobs(args.edition, args.start, args.end, only_ids=only_ids)
    preview_dir = Path(args.preview_out) if args.preview_out else None
    pilot_dir = Path(args.pilot_dir) if args.pilot_dir else None
    if pilot_dir:
        pilot_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== v4.2 PC Typography & Version Upgrader: {len(jobs)} workbooks ===")
    t0 = time.time()
    pythoncom.CoInitialize()
    xl = None
    processed_since_recycle = 0
    ok = 0
    failed = []

    try:
        for i, (idx, slug, is_pro, src_path) in enumerate(jobs, 1):
            target = src_path
            if pilot_dir is not None:
                target = pilot_dir / src_path.name
                shutil.copy2(src_path, target)

            ed_lbl = "PRO" if is_pro else "OFF"
            t1 = time.time()
            last_err = None
            for attempt in range(2):
                if xl is None or processed_since_recycle >= args.recycle:
                    _close_excel(xl)
                    xl = _open_excel()
                    processed_since_recycle = 0
                try:
                    upgrade_workbook(xl, target, slug, is_pro, preview_dir=preview_dir, tag=f"{idx:02d}_{slug}")
                    last_err = None
                    break
                except Exception as exc:
                    last_err = exc
                    _close_excel(xl)
                    xl = None
                    processed_since_recycle = 0
                    if attempt == 0:
                        time.sleep(1.0)
            if last_err is None:
                ok += 1
                processed_since_recycle += 1
                ty = get_typography(slug)
                print(f"[{i:03d}/{len(jobs):03d}] OK #{idx:02d} {ed_lbl} {slug:<22} "
                      f"EN={ty.display_en} | VN={ty.title_vn} | UI={ty.body_ui} ({time.time() - t1:.1f}s)",
                      flush=True)
            else:
                failed.append((idx, ed_lbl, slug, str(last_err)))
                print(f"[{i:03d}/{len(jobs):03d}] FAIL #{idx:02d} {ed_lbl} {slug}: {last_err}", flush=True)
    finally:
        _close_excel(xl)
        pythoncom.CoUninitialize()

    elapsed = time.time() - t0
    print(f"=== DONE: {ok}/{len(jobs)} OK, {len(failed)} failed in {elapsed:.1f}s ===")
    if failed:
        for f in failed:
            print("  FAILED:", f)
        sys.exit(1)


if __name__ == "__main__":
    main()
