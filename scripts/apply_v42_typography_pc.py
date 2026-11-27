"""
apply_v42_typography_pc.py — Strict-Whitelist Typography + PIL Pixel Auto-Fit COM Upgrader (160 PC Files).

Applies ONLY Whitelist readable fonts across ALL 160 PC Excel workbooks:
  - templates/pro_macro/*.xlsm (80 files)
  - templates/excel_universal_offline/*.xlsx (80 files)

Strict guarantees:
  1. ZERO Blacklist fonts (Vivaldi, French Script MT, Freestyle Script, Harlow Solid Italic, etc.).
  2. ZERO Script fonts on ALL-CAPS text (ALL-CAPS English titles ALWAYS use Elegant Serif).
  3. Mathematical PIL.ImageFont.truetype Auto-Fit on EVERY title, theme name, Month (incl. September),
     Weekday (incl. longest VN weekday), Year, KPI & banner cell across all 5 sheets:
       rendered_text_width_px <= available_cell_width_px * 0.88
     Steps Font.Size down by -1pt until 100% satisfied & keeps WrapText=False on single-line titles.
  4. Direct Excel COM edits ONLY (NEVER openpyxl.save()), preserves 100% VBA, protection, charts,
     checkboxes, animations, and calcMode=auto.
  5. NEVER creates _build_tmp/, NEVER touches Google Sheets / Mobile / assets.
"""
from __future__ import annotations

import argparse
import gc
import json
import re
import sys
import time
from pathlib import Path

import pythoncom
import win32com.client as win32

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from excel_builder import TEMPLATES
from hx.core import REPO_URL, cell as xl_cell
from hx.typography import (
    SCRIPT_WHITELIST,
    TypographySpec,
    autofit_font_size,
    get_typography,
    has_vietnamese,
    is_all_caps,
)

PRO_DIR = ROOT / "templates" / "pro_macro"
OFF_DIR = ROOT / "templates" / "excel_universal_offline"

GUIDE_SHEET = "📖 Hướng Dẫn"
DAILY_SHEET = "📝 Nhiệm Vụ Ngày"
GOALS_SHEET = "🎯 Yearly Goals & Habits"
ANNUAL_SHEET = "🏆 Tổng Kết & Thành Tựu Năm"
HIDDEN_SHEETS = {"_Calc", "_Database", "_Assets", "_YearHistory"}

_VER_TOKEN_RE = re.compile(r"\b([vV])[234]\.\d+(\s+(?:Turbo|TURBO|Universal|UNIVERSAL))?\b")


def _norm_ver_text(txt: str, is_pro: bool) -> str:
    if not txt:
        return txt

    def _repl(m: re.Match) -> str:
        prefix = m.group(1)
        suffix = m.group(2) or ""
        if is_pro:
            if suffix.strip() == "TURBO" or prefix == "V":
                return "V4.2 TURBO"
            return "v4.2 Turbo"
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


def _boost_row(ws, row_1: int, min_h: float):
    try:
        cur = float(ws.Rows(row_1).RowHeight or 0)
        if cur + 0.25 < min_h:
            ws.Rows(row_1).RowHeight = round(float(min_h), 1)
    except Exception:
        pass


def _apply_fitted_cell(
    ws,
    cell_rng,
    texts: list[str],
    font_name: str,
    target_pt: float,
    *,
    typo: TypographySpec,
    bold: bool = True,
    italic: bool = False,
    min_pt: float = 7.0,
    safety: float = 0.84,
    single_line: bool = True,
    force_min_rh: float | None = None,
    stats: dict | None = None,
) -> float:
    """
    Mathematically auto-fit cell font via PIL.ImageFont.truetype against exact Excel MergeArea.Width,
    enforcing:
      - ZERO Vietnamese text in non-VN font
      - ZERO ALL-CAPS text in Script font
      - rendered_text_width_px <= available_cell_width_px * 0.88
      - Writes ONLY properties that actually changed (fast on Offline!)
    """
    joined = " ".join(t for t in texts if t)
    final_font = font_name
    final_bold = bool(bold)
    final_italic = bool(italic)

    # Hard guard 1: Vietnamese text NEVER gets non-VN font
    if has_vietnamese(joined) and final_font not in (typo.title_vn, typo.body_ui, typo.num_font):
        final_font = typo.title_vn
        final_bold = True
        final_italic = typo.title_vn_italic if italic else False

    # Hard guard 2: ALL-CAPS text NEVER gets a Script font
    if is_all_caps(joined) and final_font in SCRIPT_WHITELIST:
        final_font = typo.title_vn if has_vietnamese(joined) else typo.display_caps
        final_bold = True
        final_italic = typo.caps_italic if not has_vietnamese(joined) else False

    ma = cell_rng.MergeArea
    avail_w_px = float(ma.Width) * (96.0 / 72.0)

    fitted_pt, min_rh_pt, shrunk = autofit_font_size(
        texts,
        final_font,
        target_pt,
        avail_w_px,
        bold=final_bold,
        italic=final_italic,
        min_pt=min_pt,
        safety=safety,
    )

    if stats is not None:
        stats["checked_cells"] += 1
        if shrunk:
            stats["shrunk_cells"] += 1

    # Write ONLY changed properties to minimize Excel COM Linked-Picture repaints
    f = cell_rng.Font
    if str(f.Name or "") != final_font:
        f.Name = final_font
    if abs(float(f.Size or 0) - fitted_pt) > 0.05:
        f.Size = float(fitted_pt)
    if bool(f.Bold) != final_bold:
        f.Bold = final_bold
    if bool(f.Italic) != final_italic:
        f.Italic = final_italic

    if single_line:
        try:
            if bool(cell_rng.WrapText):
                cell_rng.WrapText = False
        except Exception:
            pass

    if ma.Rows.Count == 1:
        need_rh = max(min_rh_pt, force_min_rh or 0.0)
        _boost_row(ws, ma.Row, need_rh)
    elif force_min_rh is not None:
        # Ensure multi-row merge has adequate total height
        if float(ma.Height) < force_min_rh:
            extra = (force_min_rh - float(ma.Height)) / ma.Rows.Count
            for rr in range(ma.Row, ma.Row + ma.Rows.Count):
                _boost_row(ws, rr, float(ws.Rows(rr).RowHeight or 0) + extra)

    return fitted_pt


def _ensure_body_font(ws, sample_cell, target_body: str):
    """Apply UsedRange.Font.Name = target_body ONLY if body font currently differs."""
    try:
        cur = str(sample_cell.Font.Name or "")
    except Exception:
        cur = ""
    if cur != target_body:
        ws.UsedRange.Font.Name = target_body


def _update_chart_titles(ws, title_font: str):
    try:
        for i in range(1, ws.ChartObjects().Count + 1):
            ch = ws.ChartObjects(i).Chart
            if ch.HasTitle:
                if str(ch.ChartTitle.Font.Name or "") != title_font:
                    ch.ChartTitle.Font.Name = title_font
                if not bool(ch.ChartTitle.Font.Bold):
                    ch.ChartTitle.Font.Bold = True
    except Exception:
        pass


def _upgrade_guide(ws, typo: TypographySpec, is_pro: bool, stats: dict):
    was_prot = _unprotect_if_needed(ws)
    try:
        _ensure_body_font(ws, ws.Cells(14, 2), typo.body_ui)
        ur = ws.UsedRange
        r0, c0 = ur.Row, ur.Column
        vals = ur.Value
        forms = ur.Formula
        if not isinstance(vals, tuple):
            vals = ((vals,),)
            forms = ((forms,),)

        foot_txt = (
            f"💛  © 2026 Dyu (Thân Trọng Duy)  •  Habit Tracker Collection v4.2 Pro Turbo  •  {REPO_URL}"
            if is_pro else
            f"💛  © 2026 Dyu (Thân Trọng Duy)  •  Habit Tracker Collection v4.2 Universal  •  {REPO_URL}"
        )

        # B2 Hero Banner
        c_b2 = ws.Cells(2, 2)
        v2 = str(vals[2 - r0][2 - c0] or "") if (2 >= r0 and 2 - r0 < len(vals) and 2 >= c0 and 2 - c0 < len(vals[0])) else _safe_text(c_b2)
        if v2 and not v2.startswith("="):
            nv2 = _norm_ver_text(v2, is_pro)
            if nv2 != v2:
                c_b2.Value = nv2
                v2 = nv2
        _apply_fitted_cell(ws, c_b2, [v2], typo.title_vn, 16.0, typo=typo,
                           bold=True, italic=typo.title_vn_italic, force_min_rh=40.0, stats=stats)

        # B3 Tagline
        c_b3 = ws.Cells(3, 2)
        v3 = str(vals[3 - r0][2 - c0] or "") if (3 >= r0 and 3 - r0 < len(vals) and 2 >= c0 and 2 - c0 < len(vals[0])) else _safe_text(c_b3)
        _apply_fitted_cell(ws, c_b3, [v3], typo.title_vn, 10.5, typo=typo,
                           bold=False, italic=True, force_min_rh=26.0, stats=stats)

        # B4 Mode Bar
        v4 = vals[4 - r0][2 - c0] if (4 >= r0 and 4 - r0 < len(vals) and 2 >= c0 and 2 - c0 < len(vals[0])) else ws.Cells(4, 2).Value
        if isinstance(v4, str) and not v4.startswith("="):
            nv4 = _norm_ver_text(v4, is_pro)
            if nv4 != v4:
                ws.Cells(4, 2).Value = nv4

        # Section headers & footer scan
        sec_prefixes = (
            "🗂️", "📌  1.", "⚡  2.", "🧩  3.", "🏆  4.", "🎨  5.", "⚡  5.",
            "📌 1.", "⚡ 2.", "🧩 3.", "🏆 4.", "🎨 5.", "⚡ 5.",
        )
        for ri, row_vals in enumerate(vals):
            r = r0 + ri
            if r < 5:
                continue
            row_forms = forms[ri]
            for ci, val in enumerate(row_vals):
                c = c0 + ci
                if c < 2 or c > 9 or not isinstance(val, str) or not val.strip():
                    continue
                f_str = row_forms[ci]
                if isinstance(f_str, str) and f_str.startswith("="):
                    continue
                s = val.strip()

                if "Habit Tracker Collection" in s and ("github.com" in s or "by Dyu" in s or "©" in s):
                    cell = ws.Cells(r, c)
                    if val != foot_txt:
                        cell.Value = foot_txt
                    _apply_fitted_cell(ws, cell, [foot_txt], typo.title_vn, 9.5, typo=typo,
                                       bold=False, italic=True, force_min_rh=28.0, stats=stats)
                    continue

                if _VER_TOKEN_RE.search(s):
                    nv = _norm_ver_text(val, is_pro)
                    if nv != val:
                        ws.Cells(r, c).Value = nv
                    s = nv.strip()

                if any(s.startswith(p) for p in sec_prefixes):
                    cell = ws.Cells(r, c)
                    tgt = 11.0 if s.startswith(("🗂️", "🎨", "⚡  5.", "⚡ 5.")) else 10.5
                    _apply_fitted_cell(ws, cell, [s], typo.title_vn, tgt, typo=typo,
                                       bold=True, italic=False, force_min_rh=27.0, stats=stats)
    finally:
        _reprotect(ws, was_prot)


def _upgrade_tracker(ws, typo: TypographySpec, stats: dict):
    was_prot = _unprotect_if_needed(ws)
    try:
        _ensure_body_font(ws, ws.Cells(17, 2), typo.body_ui)
        ur = ws.UsedRange
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

        # B2: Top tag (ALL-CAPS -> ALWAYS Elegant Serif display_caps, NEVER Script!)
        t_b2 = str(_val_at(2, 2) or "")
        if has_vietnamese(t_b2):
            _apply_fitted_cell(ws, ws.Cells(2, 2), [t_b2], typo.title_vn, 9.5, typo=typo,
                               bold=True, italic=False, min_pt=7.0, force_min_rh=20.0, stats=stats)
        else:
            _apply_fitted_cell(ws, ws.Cells(2, 2), [t_b2], typo.display_caps, 9.5, typo=typo,
                               bold=True, italic=typo.caps_italic, min_pt=7.0, force_min_rh=20.0, stats=stats)

        # B3: Month name (Title Case "October" — fitted against BOTH current & longest "September"!)
        t_b3 = str(_val_at(3, 2) or "October")
        m_tgt = min(en.max_month_pt, 17.5 + en.size_delta)
        _apply_fitted_cell(ws, ws.Cells(3, 2), [t_b3, "September"], typo.display_en, m_tgt, typo=typo,
                           bold=en.bold, italic=en.italic, min_pt=10.0, force_min_rh=30.0 + en.rh_boost, stats=stats)

        # B5: Year ("2026")
        _apply_fitted_cell(ws, ws.Cells(5, 2), [str(_val_at(5, 2) or "2026")], typo.num_font, 14.0, typo=typo,
                           bold=True, italic=False, min_pt=10.0, force_min_rh=25.0, stats=stats)

        # B9: Theme / Garden title (ALL-CAPS -> ALWAYS Elegant Serif display_caps, auto-fitted into Col B!)
        t_b9 = str(_val_at(9, 2) or "")
        if has_vietnamese(t_b9):
            _apply_fitted_cell(ws, ws.Cells(9, 2), [t_b9], typo.title_vn, 11.5, typo=typo,
                               bold=True, italic=typo.title_vn_italic, min_pt=7.5, stats=stats)
        else:
            _apply_fitted_cell(ws, ws.Cells(9, 2), [t_b9], typo.display_caps, 11.5, typo=typo,
                               bold=True, italic=typo.caps_italic, min_pt=7.5, stats=stats)

        # Top-right KPI numbers: AI3, AL4, AL6, AI10
        if _val_at(3, 35) is not None or _form_at(3, 35):
            _apply_fitted_cell(ws, ws.Cells(3, 35), ["100%"], typo.num_font, 15.0, typo=typo,
                               bold=True, italic=False, min_pt=10.0, stats=stats)
        if _val_at(4, 38) is not None or _form_at(4, 38):
            _apply_fitted_cell(ws, ws.Cells(4, 38), [str(_val_at(4, 38) or "264 / 264"), "264 / 264"],
                               typo.num_font, 12.0, typo=typo, bold=True, italic=False, min_pt=8.5, stats=stats)
        if _val_at(6, 38) is not None or _form_at(6, 38):
            _apply_fitted_cell(ws, ws.Cells(6, 38), ["31"], typo.num_font, 12.0, typo=typo,
                               bold=True, italic=False, min_pt=8.5, stats=stats)
        if _val_at(10, 35) is not None or _form_at(10, 35):
            _apply_fitted_cell(ws, ws.Cells(10, 35), ["31"], typo.num_font, 26.0, typo=typo,
                               bold=True, italic=False, min_pt=14.0, stats=stats)

        # Addon section headers (Rows 39+): ALL-CAPS EN -> display_caps Serif, VN -> title_vn, auto-fitted!
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
                if not is_all_caps(s):
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
                if has_vietnamese(s):
                    _apply_fitted_cell(ws, cell, [s], typo.title_vn, 10.5, typo=typo,
                                       bold=True, italic=False, min_pt=7.5, force_min_rh=24.0, stats=stats)
                elif len(s) <= 56:
                    _apply_fitted_cell(ws, cell, [s], typo.display_caps, 10.5, typo=typo,
                                       bold=True, italic=typo.caps_italic, min_pt=7.5, force_min_rh=24.0, stats=stats)

        _update_chart_titles(ws, typo.title_vn)
    finally:
        _reprotect(ws, was_prot)


def _upgrade_daily_tasks(ws, typo: TypographySpec, stats: dict):
    was_prot = _unprotect_if_needed(ws)
    try:
        _ensure_body_font(ws, ws.Cells(9, 3), typo.body_ui)
        en = typo.en_optics

        _apply_fitted_cell(ws, ws.Cells(2, 2), [_safe_text(ws.Cells(2, 2))], typo.title_vn, 15.5, typo=typo,
                           bold=True, italic=typo.title_vn_italic, force_min_rh=34.0, stats=stats)
        _apply_fitted_cell(
            ws, ws.Cells(5, 2),
            [_safe_text(ws.Cells(5, 2)), "Chủ Nhật, 28/09/2026", "Thứ Năm, 28/09/2026"],
            typo.title_vn, 13.5, typo=typo, bold=True, italic=typo.title_vn_italic,
            force_min_rh=30.0 + en.rh_boost, stats=stats,
        )
        _apply_fitted_cell(ws, ws.Cells(5, 4), ["31"], typo.num_font, 13.5, typo=typo,
                           bold=True, italic=False, stats=stats)
        _apply_fitted_cell(ws, ws.Cells(5, 5), [_safe_text(ws.Cells(5, 5)), "September"], typo.display_en,
                           min(16.0, 13.0 + en.size_delta * 0.65), typo=typo,
                           bold=en.bold, italic=en.italic, min_pt=9.0, force_min_rh=30.0 + en.rh_boost, stats=stats)
        _apply_fitted_cell(ws, ws.Cells(5, 6), ["2026"], typo.num_font, 13.5, typo=typo,
                           bold=True, italic=False, stats=stats)

        _apply_fitted_cell(ws, ws.Cells(2, 8), [_safe_text(ws.Cells(2, 8))], typo.title_vn, 10.0, typo=typo,
                           bold=True, italic=False, min_pt=7.5, stats=stats)
        _apply_fitted_cell(ws, ws.Cells(4, 8), ["100%"], typo.num_font, 20.0, typo=typo,
                           bold=True, italic=False, min_pt=12.0, stats=stats)
        _apply_fitted_cell(ws, ws.Cells(21, 8), [_safe_text(ws.Cells(21, 8))], typo.title_vn, 9.0, typo=typo,
                           bold=True, italic=False, min_pt=7.0, stats=stats)
        _apply_fitted_cell(ws, ws.Cells(27, 8), [_safe_text(ws.Cells(27, 8))], typo.title_vn, 9.0, typo=typo,
                           bold=True, italic=False, min_pt=7.0, stats=stats)
        _apply_fitted_cell(ws, ws.Cells(30, 2), [_safe_text(ws.Cells(30, 2))], typo.title_vn, 10.0, typo=typo,
                           bold=True, italic=False, force_min_rh=26.0, stats=stats)
    finally:
        _reprotect(ws, was_prot)


def _upgrade_yearly_goals(ws, typo: TypographySpec, stats: dict):
    was_prot = _unprotect_if_needed(ws)
    try:
        _ensure_body_font(ws, ws.Cells(6, 3), typo.body_ui)

        # B2 ("YEARLY GOALS & HABITS PLANNER" -> ALL-CAPS Elegant Serif!)
        _apply_fitted_cell(ws, ws.Cells(2, 2), [_safe_text(ws.Cells(2, 2))], typo.display_caps, 16.5, typo=typo,
                           bold=True, italic=typo.caps_italic, force_min_rh=38.0, stats=stats)
        _apply_fitted_cell(ws, ws.Cells(2, 9), ["2026"], typo.num_font, 15.0, typo=typo,
                           bold=True, italic=False, stats=stats)

        _apply_fitted_cell(ws, ws.Cells(4, 2), [_safe_text(ws.Cells(4, 2))], typo.title_vn, 10.5, typo=typo,
                           bold=True, italic=False, force_min_rh=28.0, stats=stats)
        _apply_fitted_cell(ws, ws.Cells(4, 4), [_safe_text(ws.Cells(4, 4))], typo.title_vn, 10.5, typo=typo,
                           bold=True, italic=False, force_min_rh=28.0, stats=stats)
        _apply_fitted_cell(ws, ws.Cells(4, 8), [_safe_text(ws.Cells(4, 8))], typo.title_vn, 10.0, typo=typo,
                           bold=True, italic=False, force_min_rh=28.0, stats=stats)

        col_h = ws.Range("H11:H20").Value
        for idx, row_t in enumerate(col_h):
            txt = str(row_t[0] or "") if isinstance(row_t, tuple) else str(row_t or "")
            if "PLANTED" in txt.upper():
                rp = 11 + idx
                _apply_fitted_cell(ws, ws.Cells(rp, 8), [txt], typo.display_caps, 10.5, typo=typo,
                                   bold=True, italic=typo.caps_italic, min_pt=7.5, force_min_rh=26.0, stats=stats)
                _apply_fitted_cell(ws, ws.Cells(rp + 1, 8), ["20"], typo.num_font, 28.0, typo=typo,
                                   bold=True, italic=False, min_pt=16.0, stats=stats)
                break
    finally:
        _reprotect(ws, was_prot)


def _upgrade_annual(ws, typo: TypographySpec, stats: dict):
    was_prot = _unprotect_if_needed(ws)
    try:
        _ensure_body_font(ws, ws.Cells(16, 2), typo.body_ui)

        _apply_fitted_cell(ws, ws.Cells(3, 2), ["2026"], typo.num_font, 16.5, typo=typo,
                           bold=True, italic=False, force_min_rh=32.0, stats=stats)
        _boost_row(ws, 2, 22)
        _boost_row(ws, 4, 21)

        _apply_fitted_cell(ws, ws.Cells(2, 4), [_safe_text(ws.Cells(2, 4))], typo.title_vn, 16.0, typo=typo,
                           bold=True, italic=typo.title_vn_italic, min_pt=9.5, stats=stats)
        _apply_fitted_cell(ws, ws.Cells(4, 4), [_safe_text(ws.Cells(4, 4))], typo.title_vn, 10.0, typo=typo,
                           bold=False, italic=True, min_pt=7.5, force_min_rh=21.0, stats=stats)

        _apply_fitted_cell(ws, ws.Cells(7, 2), ["9,999"], typo.num_font, 26.0, typo=typo, bold=True, italic=False, stats=stats)
        _apply_fitted_cell(ws, ws.Cells(7, 5), ["100%"], typo.num_font, 18.0, typo=typo, bold=True, italic=False, stats=stats)
        _apply_fitted_cell(ws, ws.Cells(7, 9), ["31 ngày"], typo.num_font, 22.0, typo=typo, bold=True, italic=False, stats=stats)
        _apply_fitted_cell(ws, ws.Cells(7, 12), ["20 / 20"], typo.num_font, 24.0, typo=typo, bold=True, italic=False, stats=stats)
        _apply_fitted_cell(ws, ws.Cells(34, 12), ["8 / 8"], typo.num_font, 26.0, typo=typo, bold=True, italic=False, stats=stats)

        _apply_fitted_cell(ws, ws.Cells(13, 2), [_safe_text(ws.Cells(13, 2))], typo.title_vn, 10.5, typo=typo,
                           bold=True, italic=False, force_min_rh=26.0, stats=stats)
        _apply_fitted_cell(ws, ws.Cells(15, 2), [_safe_text(ws.Cells(15, 2))], typo.title_vn, 10.0, typo=typo,
                           bold=True, italic=False, min_pt=7.5, stats=stats)
        _apply_fitted_cell(ws, ws.Cells(33, 2), [_safe_text(ws.Cells(33, 2))], typo.title_vn, 10.5, typo=typo,
                           bold=True, italic=False, force_min_rh=28.0, stats=stats)

        t_l33 = _safe_text(ws.Cells(33, 12))
        if has_vietnamese(t_l33):
            _apply_fitted_cell(ws, ws.Cells(33, 12), [t_l33], typo.title_vn, 10.0, typo=typo,
                               bold=True, italic=False, min_pt=7.5, stats=stats)
        else:
            _apply_fitted_cell(ws, ws.Cells(33, 12), [t_l33], typo.display_caps, 10.0, typo=typo,
                               bold=True, italic=typo.caps_italic, min_pt=7.5, stats=stats)

        _update_chart_titles(ws, typo.title_vn)
    finally:
        _reprotect(ws, was_prot)


def _upgrade_hidden(wb):
    try:
        ws_c = wb.Worksheets("_Calc")
        c_ba16 = ws_c.Cells(16, 53)
        v = str(c_ba16.Value or "")
        if v and not v.startswith("=") and ("v3." in v.lower() or "v4.0" in v.lower() or "v4.1" in v.lower()):
            c_ba16.Value = "🎉 Hiệu ứng Pro v4.2 Turbo đang BẬT — Siêu tốc & sống động!"
    except Exception:
        pass
    try:
        ws_a = wb.Worksheets("_Assets")
        c_c1 = ws_a.Cells(1, 3)
        v = str(c_c1.Value or "")
        if v and not v.startswith("="):
            nv = re.sub(r"\(v\d+\.\d+\)", "(v4.2)", v, flags=re.IGNORECASE)
            if nv != v:
                c_c1.Value = nv
    except Exception:
        pass


def upgrade_workbook(xl, wb_path: Path, slug: str, is_pro: bool, stats: dict):
    typo = get_typography(slug)
    wb = xl.Workbooks.Open(str(wb_path.resolve()), UpdateLinks=0, ReadOnly=False)
    try:
        for i in range(1, wb.Worksheets.Count + 1):
            ws = wb.Worksheets(i)
            nm = ws.Name
            if nm == GUIDE_SHEET:
                _upgrade_guide(ws, typo, is_pro, stats)
            elif nm == DAILY_SHEET:
                _upgrade_daily_tasks(ws, typo, stats)
            elif nm == GOALS_SHEET:
                _upgrade_yearly_goals(ws, typo, stats)
            elif nm == ANNUAL_SHEET:
                _upgrade_annual(ws, typo, stats)
            elif nm not in HIDDEN_SHEETS:
                _upgrade_tracker(ws, typo, stats)
        _upgrade_hidden(wb)
        wb.Save()
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


def collect_jobs(edition: str, start: int, end: int, only_ids: list[int] | None = None):
    jobs = []
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
    ap.add_argument("--ids", type=str, default="")
    ap.add_argument("--recycle", type=int, default=14)
    args = ap.parse_args()

    only_ids = [int(x.strip()) for x in args.ids.split(",") if x.strip()] if args.ids else None
    jobs = collect_jobs(args.edition, args.start, args.end, only_ids=only_ids)

    print(f"=== Whitelist Typography + PIL Auto-Fit COM Fixer: {len(jobs)} workbooks ===")
    t0 = time.time()
    pythoncom.CoInitialize()
    xl = None
    processed = 0
    ok = 0
    failed = []
    total_stats = {"checked_cells": 0, "shrunk_cells": 0}

    try:
        for i, (idx, slug, is_pro, target) in enumerate(jobs, 1):
            ed_lbl = "PRO" if is_pro else "OFF"
            t1 = time.time()
            last_err = None
            wb_stats = {"checked_cells": 0, "shrunk_cells": 0}
            for attempt in range(2):
                if xl is None or processed >= args.recycle:
                    _close_excel(xl)
                    xl = _open_excel()
                    processed = 0
                try:
                    wb_stats = {"checked_cells": 0, "shrunk_cells": 0}
                    upgrade_workbook(xl, target, slug, is_pro, wb_stats)
                    last_err = None
                    break
                except Exception as exc:
                    last_err = exc
                    _close_excel(xl)
                    xl = None
                    processed = 0
                    if attempt == 0:
                        time.sleep(1.0)
            if last_err is None:
                ok += 1
                processed += 1
                total_stats["checked_cells"] += wb_stats["checked_cells"]
                total_stats["shrunk_cells"] += wb_stats["shrunk_cells"]
                ty = get_typography(slug)
                print(
                    f"[{i:03d}/{len(jobs):03d}] OK #{idx:02d} {ed_lbl} {slug:<22} "
                    f"Month={ty.display_en:<18} Caps={ty.display_caps:<17} "
                    f"fit={wb_stats['shrunk_cells']}/{wb_stats['checked_cells']} ({time.time() - t1:.1f}s)",
                    flush=True,
                )
            else:
                failed.append((idx, ed_lbl, slug, str(last_err)))
                print(f"[{i:03d}/{len(jobs):03d}] FAIL #{idx:02d} {ed_lbl} {slug}: {last_err}", flush=True)
    finally:
        _close_excel(xl)
        pythoncom.CoUninitialize()

    print(
        f"=== DONE: {ok}/{len(jobs)} OK, {len(failed)} failed in {time.time() - t0:.1f}s | "
        f"AUTO-FIT: {total_stats['shrunk_cells']} / {total_stats['checked_cells']} cells shrunk ==="
    )
    if failed:
        for f in failed:
            print("  FAILED:", f)
        sys.exit(1)


if __name__ == "__main__":
    main()
