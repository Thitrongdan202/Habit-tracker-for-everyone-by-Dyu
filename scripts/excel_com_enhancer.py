"""
excel_com_enhancer.py — Version 2.1 High-Speed Excel COM Compiler for:
  1. Pro Interactive Edition (`pro_xlsm`) -> `templates/pro_macro/01..10_*_Pro.xlsm` (FileFormat=52)
     - Embeds 6 high-DPI sprites in `_Assets!B2:B7`
     - Creates dynamic Named Ranges (`Anim_Day01..31`, `Anim_MonthlyHero`, `Anim_YearlyGoals`,
       `Anim_AnnualHero`, `Anim_AnnualM01..M12`, `Anim_AchBadges`) + Linked Pictures
     - Adds crisp Form Control Checkboxes (batched geometry cache for 5x speed)
     - Injects `vba_scripts/modHabitState.bas` + Monthly Tracker & Yearly Goals `Worksheet_Change` handlers
  2. Universal Offline No-Macro Edition (`offline_12m`) -> `templates/excel_universal_offline/01..10_*.xlsx` (FileFormat=51)
     - Same 100% offline Linked Pictures + Form Checkboxes across all 12 independent tabs `T01..T12`
       + `Yearly Goals` + `Annual Achievements` — ZERO macros, ZERO security popups!

Usage:
    python scripts/excel_com_enhancer.py pro [short_key ...]
    python scripts/excel_com_enhancer.py offline [short_key ...]
    python scripts/excel_com_enhancer.py all [short_key ...]
"""
from __future__ import annotations

import sys
import time
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageGrab
import win32com.client as win32
from xlsxwriter.utility import xl_rowcol_to_cell

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from excel_builder import (build_base_pro, build_base_offline, build_all_gsheets)
from hx.tracker import CALC_SHEET
from hx.guide import GUIDE_SHEET
from hx.annual import ASSETS_SHEET, DATABASE_SHEET, HISTORY_SHEET, YEARLY_GOALS_SHEET
from hx.daily_tasks import DAILY_TASKS_SHEET

ASSETS_DIR = ROOT / "assets"
PRO_OUT_DIR = ROOT / "templates" / "pro_macro"
OFFLINE_OUT_DIR = ROOT / "templates" / "excel_universal_offline"
PREVIEWS_DIR = ROOT / "previews"
VBA_MOD_PATH = ROOT / "vba_scripts" / "modHabitState.bas"

THISWORKBOOK_EVENT_VBA = (
    "Option Explicit\r\n"
    "Private Sub Workbook_Open()\r\n"
    "    modHabitState.InitWorkbookFastMode\r\n"
    "End Sub\r\n"
    "Private Sub Workbook_BeforeClose(Cancel As Boolean)\r\n"
    "    modHabitState.CleanupAllFX\r\n"
    "End Sub\r\n"
    "Private Sub Workbook_SheetActivate(ByVal Sh As Object)\r\n"
    "    modHabitState.HandleSheetActivate Sh\r\n"
    "End Sub\r\n"
)

TRACKER_EVENT_VBA = (
    "Option Explicit\r\n"
    "Private Sub Worksheet_Change(ByVal Target As Range)\r\n"
    "    If Not Intersect(Target, Me.Range(\"B3,B5\")) Is Nothing Then\r\n"
    "        modHabitState.HandleMonthlySwitch Me\r\n"
    "    ElseIf Not Intersect(Target, Me.Range(\"C17:AG36\")) Is Nothing Then\r\n"
    "        modHabitState.HandleTrackerTick Me, Target\r\n"
    "    End If\r\n"
    "End Sub\r\n"
)

YEARLY_GOALS_EVENT_VBA = (
    "Option Explicit\r\n"
    "Private Sub Worksheet_Change(ByVal Target As Range)\r\n"
    "    If Not Intersect(Target, Me.Range(\"I2\")) Is Nothing Then\r\n"
    "        modHabitState.HandleYearlyGoalsSwitch Me\r\n"
    "    ElseIf Not Intersect(Target, Me.Range(\"B6:B25\")) Is Nothing Then\r\n"
    "        modHabitState.HandleYearlyGoalTick Me, Target\r\n"
    "    End If\r\n"
    "End Sub\r\n"
)

DAILY_TASKS_EVENT_VBA = (
    "Option Explicit\r\n"
    "Private Sub Worksheet_Change(ByVal Target As Range)\r\n"
    "    If Not Intersect(Target, Me.Range(\"D5:F5\")) Is Nothing Then\r\n"
    "        modHabitState.HandleDailyTasksSwitch Me\r\n"
    "    ElseIf Not Intersect(Target, Me.Range(\"B9:B28\")) Is Nothing Then\r\n"
    "        modHabitState.HandleDailyTaskTick Me, Target\r\n"
    "    End If\r\n"
    "End Sub\r\n"
)


def _hex_to_bgr(hex_str: str, fallback: int = 0x7A7AB5) -> int:
    """Convert '#RRGGBB' to Excel COM little-endian BGR integer (R + G*256 + B*65536)."""
    try:
        s = hex_str.strip().lstrip("#")
        if len(s) != 6:
            return fallback
        r, g, b = int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
        return r + (g << 8) + (b << 16)
    except Exception:
        return fallback


def _add_pill_button(ws, name: str, text: str, left: float, top: float, width: float, height: float,
                     fill_bgr: int, border_bgr: int, font_bgr: int, on_action: str, font_size: float = 8.0):
    """Create a sleek rounded-rectangle Quick-Action Pastel Pill Button bound to a Pure-ASCII VBA macro."""
    shp = ws.Shapes.AddShape(5, left, top, width, height)  # msoShapeRoundedRectangle = 5
    shp.Name = name
    try:
        shp.Adjustments[1] = 0.42
    except Exception:
        pass
    shp.Fill.Solid()
    shp.Fill.ForeColor.RGB = fill_bgr
    shp.Line.Visible = -1  # msoTrue
    shp.Line.ForeColor.RGB = border_bgr
    shp.Line.Weight = 0.85
    tf2 = shp.TextFrame2
    tf2.WordWrap = 0
    tf2.VerticalAnchor = 3  # msoAnchorMiddle
    tf2.MarginLeft = 2
    tf2.MarginRight = 2
    tf2.MarginTop = 1
    tf2.MarginBottom = 1
    tr = tf2.TextRange
    tr.Text = text
    tr.ParagraphFormat.Alignment = 2  # msoAlignCenter
    tr.Font.Name = "Segoe UI"
    tr.Font.Size = font_size
    tr.Font.Bold = -1
    tr.Font.Fill.ForeColor.RGB = font_bgr
    shp.OnAction = on_action
    shp.Placement = 1  # xlMoveAndSize
    return shp


def add_pro_pill_buttons(wb, meta: dict):
    """Effect 4: Add sleek Quick-Action Pastel Pill Buttons cleanly on Pro `.xlsm` (ZERO overlaps!)."""
    bgr_pri = _hex_to_bgr(meta.get("theme_primary", "#B57A7A"))
    bgr_dk  = _hex_to_bgr(meta.get("theme_primary_dark", "#8B5454"))
    bgr_sft = _hex_to_bgr(meta.get("theme_soft", "#F7EAE6"))
    bgr_ink = _hex_to_bgr(meta.get("theme_ink", "#3B2F2F"))
    bgr_onp = _hex_to_bgr(meta.get("theme_on_primary", "#FFFFFF"))
    bgr_wht = _hex_to_bgr("#FFFFFF")

    # 1. Monthly Tracker (`B7` cell tray): [◀ Tháng] [Tháng ▶] [✨ FX: BẬT]
    ws_tr = wb.Worksheets(meta["tracker_sheet"])
    b7 = ws_tr.Range("B7")
    pad_x = 3.0
    gap = 3.0
    bh = min(19.0, max(15.0, b7.Height - 5.0))
    bt = b7.Top + (b7.Height - bh) / 2.0
    avail_w = b7.Width - 2 * pad_x - 2 * gap
    w_nav = avail_w * 0.305
    w_fx  = avail_w - 2 * w_nav
    x0 = b7.Left + pad_x
    _add_pill_button(ws_tr, "BTN_PREV_MONTH", "◀ Tháng", x0, bt, w_nav, bh,
                     bgr_sft, bgr_pri, bgr_ink, "BtnPrevMonth", font_size=7.6)
    _add_pill_button(ws_tr, "BTN_NEXT_MONTH", "Tháng ▶", x0 + w_nav + gap, bt, w_nav, bh,
                     bgr_sft, bgr_pri, bgr_ink, "BtnNextMonth", font_size=7.6)
    _add_pill_button(ws_tr, "BTN_FX_TOGGLE", "✨ FX: BẬT", x0 + 2 * (w_nav + gap), bt, w_fx, bh,
                     bgr_pri, bgr_dk, bgr_onp, "BtnToggleFX", font_size=7.6)

    # 2. Daily One-Off Tasks (`D6:F6` cell tray): [◀ Hôm qua] [📅 Hôm nay] [Ngày mai ▶]
    ws_dt = wb.Worksheets(DAILY_TASKS_SHEET)
    tray = ws_dt.Range("D6:F6")
    d_pad = 6.0
    d_gap = 6.0
    dh = min(21.0, max(16.0, tray.Height - 6.0))
    dt_top = tray.Top + (tray.Height - dh) / 2.0
    dw = (tray.Width - 2 * d_pad - 2 * d_gap) / 3.0
    dx0 = tray.Left + d_pad
    _add_pill_button(ws_dt, "BTN_PREV_DAY", "◀ Hôm qua", dx0, dt_top, dw, dh,
                     bgr_sft, bgr_pri, bgr_ink, "BtnPrevDay", font_size=8.2)
    _add_pill_button(ws_dt, "BTN_TODAY", "📅 Hôm nay", dx0 + dw + d_gap, dt_top, dw, dh,
                     bgr_pri, bgr_dk, bgr_onp, "BtnToday", font_size=8.2)
    _add_pill_button(ws_dt, "BTN_NEXT_DAY", "Ngày mai ▶", dx0 + 2 * (dw + d_gap), dt_top, dw, dh,
                     bgr_sft, bgr_pri, bgr_ink, "BtnNextDay", font_size=8.2)

    # 3. Guide (Section 5 left-aligned header bar, right CTA pill directly above Guide_Stage5 — ZERO overlap!)
    ws_g = wb.Worksheets(GUIDE_SHEET)
    r_sec5 = 23
    for rr_g in range(18, 34):
        if "5. HOẠT ẢNH" in str(ws_g.Cells(rr_g, 2).Value or ""):
            r_sec5 = rr_g
            break
    sec5_bar = ws_g.Range(ws_g.Cells(r_sec5, 2), ws_g.Cells(r_sec5, 7))
    gw = 148.0
    gh = min(21.0, max(17.0, sec5_bar.Height - 4.0))
    gl = sec5_bar.Left + sec5_bar.Width - gw - 6.0
    gt = sec5_bar.Top + (sec5_bar.Height - gh) / 2.0
    _add_pill_button(ws_g, "BTN_DEMO_FX", "🎉 Thử Hiệu Ứng Pro", gl, gt, gw, gh,
                     bgr_wht, bgr_sft, bgr_dk, "BtnDemoFX", font_size=8.2)


def paste_linked_picture_fast(xl, src_cell, dst_ws, left: float, top: float, width: float, height: float,
                              formula: str, align_bottom: bool = False, need_copy: bool = True,
                              shape_name: str | None = None):
    """Paste Linked Picture onto `dst_ws`, bind `formula`, name deterministically & position cleanly."""
    for attempt in range(6):
        try:
            if need_copy or attempt > 0:
                src_cell.Copy()
                time.sleep(0.025)
            pic = dst_ws.Pictures().Paste(Link=True)
            pic.Formula = formula
            if shape_name:
                pic.Name = shape_name
            pic.ShapeRange.Line.Visible = False
            pic.ShapeRange.LockAspectRatio = -1  # msoTrue
            pad_x = 1.5 if align_bottom else 4.5
            pad_y = 2.5 if align_bottom else 4.5
            max_w = max(8.0, width - 2 * pad_x)
            max_h = max(8.0, height - 2 * pad_y)
            scale = min(max_w / pic.Width, max_h / pic.Height)
            pic.Width = pic.Width * scale
            pic.Left = left + (width - pic.Width) / 2.0
            if align_bottom:
                pic.Top = top + height - pic.Height - 2.0
            else:
                pic.Top = top + (height - pic.Height) / 2.0
            pic.Placement = 1  # xlMoveAndSize
            return pic
        except Exception as e:
            if attempt == 5:
                raise RuntimeError(f"Failed pasting linked picture {formula}: {e}") from e
            time.sleep(0.15 * (attempt + 1))


def add_checkboxes_fast(ws, coords: list[tuple[int, int]]) -> int:
    """Add Form Control Checkboxes using cached row/col geometry & bulk boolean read (5x faster!)."""
    if not coords:
        return 0
    rows = sorted({r for r, _ in coords})
    cols = sorted({c for _, c in coords})
    row_geom = {}
    for r in rows:
        ro = ws.Rows(r + 1)
        row_geom[r] = (ro.Top, ro.Height)
    col_geom = {}
    for c in cols:
        co = ws.Columns(c + 1)
        col_geom[c] = (co.Left, co.Width)

    # Bulk-read bounding box values in ONE COM call
    r_min, r_max = rows[0], rows[-1]
    c_min, c_max = cols[0], cols[-1]
    raw_vals = ws.Range(ws.Cells(r_min + 1, c_min + 1), ws.Cells(r_max + 1, c_max + 1)).Value

    def _is_true(r: int, c: int) -> bool:
        if r_min == r_max and c_min == c_max:
            v = raw_vals
        elif r_min == r_max:
            v = raw_vals[0][c - c_min]
        elif c_min == c_max:
            v = raw_vals[r - r_min][0]
        else:
            v = raw_vals[r - r_min][c - c_min]
        return v is True

    cbs = ws.CheckBoxes()
    cb_w, cb_h = 13.5, 13.5
    count = 0
    for (r, c) in coords:
        c_left, c_width = col_geom[c]
        r_top, r_height = row_geom[r]
        left = c_left + (c_width - 11.5) / 2.0
        top = r_top + (r_height - 13.0) / 2.0
        cb = cbs.Add(left, top, cb_w, cb_h)
        cb.Caption = ""
        cb.LinkedCell = xl_rowcol_to_cell(r, c, True, True)
        cb.Value = 1 if _is_true(r, c) else -4146
        cb.Display3DShading = False
        cb.Placement = 1
        count += 1
    return count


def grab_range_png(ws, rng_str: str, out_path: Path, retries: int = 5):
    ws.Activate()
    time.sleep(0.18)
    for attempt in range(retries):
        try:
            ws.Range(rng_str).CopyPicture(Appearance=1, Format=2)
            time.sleep(0.28)
            im = ImageGrab.grabclipboard()
            if isinstance(im, Image.Image):
                out_path.parent.mkdir(parents=True, exist_ok=True)
                im.save(out_path, optimize=True)
                return im.size
        except Exception as e:
            if attempt == retries - 1:
                raise e
        time.sleep(0.35)
    raise RuntimeError(f"Clipboard grab failed for {ws.Name}!{rng_str}")


def enhance_one(xl, meta: dict, capture_previews: bool = True):
    t0 = time.perf_counter()
    edition = meta["edition"]
    stem = meta["stem"]
    slug = meta["slug"]
    base_path = Path(meta["base_path"])

    if edition == "pro_xlsm":
        PRO_OUT_DIR.mkdir(parents=True, exist_ok=True)
        final_path = PRO_OUT_DIR / f"{stem}_Pro.xlsm"
        file_format = 52  # xlOpenXMLWorkbookMacroEnabled
    else:
        OFFLINE_OUT_DIR.mkdir(parents=True, exist_ok=True)
        final_path = OFFLINE_OUT_DIR / f"{stem}.xlsx"
        file_format = 51  # xlOpenXMLWorkbook

    if final_path.exists():
        final_path.unlink()

    wb = xl.Workbooks.Open(str(base_path.resolve()))
    try:
        xl.ScreenUpdating = False
        xl.EnableEvents = False
        xl.Calculation = -4135  # xlCalculationManual

        # 1. Populate `_Assets!B2:B7` with 300x300px high-DPI PNG sprites
        ws_a = wb.Worksheets(ASSETS_SHEET)
        ws_a.Visible = -1
        ws_a.Activate()
        xl.ActiveWindow.DisplayGridlines = False
        for idx in range(6):
            cell_obj = ws_a.Cells(2 + idx, 2)
            pad = 2.5
            side = min(cell_obj.Width, cell_obj.Height) - 2 * pad
            left = cell_obj.Left + (cell_obj.Width - side) / 2.0
            top = cell_obj.Top + (cell_obj.Height - side) / 2.0
            img_path = (ASSETS_DIR / slug / f"stage_{idx}.png").resolve()
            shp = ws_a.Shapes.AddPicture(
                Filename=str(img_path), LinkToFile=False, SaveWithDocument=True,
                Left=left, Top=top, Width=side, Height=side
            )
            shp.Placement = 1
            shp.Line.Visible = False

        hidden_names = {ASSETS_SHEET, CALC_SHEET, DATABASE_SHEET, HISTORY_SHEET}
        for ws in wb.Worksheets:
            if ws.Name not in hidden_names:
                ws.Activate()
                xl.ActiveWindow.DisplayGridlines = False

        # 2. Add Form Control Checkboxes (cached geometry + bulk bool read!)
        cb_count = 0
        for sheet_name, coords in meta["checkboxes"].items():
            if not coords:
                continue
            ws = wb.Worksheets(sheet_name)
            ws.Activate()
            cb_count += add_checkboxes_fast(ws, coords)

        # 3. Register ALL dynamic Named Ranges first
        for item in meta["dyn_anims"]:
            wb.Names.Add(Name=item["name"], RefersTo=item["refers_to"])

        # 4. Paste ALL Linked Pictures grouped by sheet (minimal activations + deterministic Hero names!)
        pic_groups = defaultdict(list)
        for item in meta["dyn_anims"]:
            pic_groups[item["sheet"]].append({
                "name": item.get("name"),
                "r1": item["r1"], "c1": item["c1"], "r2": item["r2"], "c2": item["c2"],
                "formula": f"={item['name']}",
                "align_bottom": item.get("align_bottom", False),
            })
        for sp in meta["static_pics"]:
            pic_groups[sp["sheet"]].append({
                "name": sp.get("name"),
                "r1": sp["r1"], "c1": sp["c1"], "r2": sp["r2"], "c2": sp["c2"],
                "formula": sp["formula"],
                "align_bottom": False,
            })

        src_anchor = ws_a.Range("B2")
        pic_count = 0
        for sheet_name, items in pic_groups.items():
            ws_dst = wb.Worksheets(sheet_name)
            ws_dst.Activate()
            src_anchor.Copy()
            time.sleep(0.03)
            for idx_p, it in enumerate(items):
                dst = ws_dst.Range(ws_dst.Cells(it["r1"] + 1, it["c1"] + 1),
                                   ws_dst.Cells(it["r2"] + 1, it["c2"] + 1))
                paste_linked_picture_fast(
                    xl, src_anchor, ws_dst,
                    dst.Left, dst.Top, dst.Width, dst.Height,
                    it["formula"], align_bottom=it["align_bottom"],
                    need_copy=(idx_p == 0),
                    shape_name=it.get("name"),
                )
                pic_count += 1
            xl.CutCopyMode = False

        # 5. Inject v3.5 Ultra-Smooth FX VBA Engine & Quick-Action Pastel Pill Buttons into Pro `.xlsm`
        if edition == "pro_xlsm":
            vbp = wb.VBProject
            vbp.VBComponents.Import(str(VBA_MOD_PATH.resolve()))

            # Inject ThisWorkbook lifecycle events (Workbook_Open, BeforeClose, SheetActivate)
            cm_wb = vbp.VBComponents(wb.CodeName).CodeModule
            if cm_wb.CountOfLines > 0:
                cm_wb.DeleteLines(1, cm_wb.CountOfLines)
            cm_wb.AddFromString(THISWORKBOOK_EVENT_VBA)

            ws_tr = wb.Worksheets(meta["tracker_sheet"])
            cm_tr = vbp.VBComponents(ws_tr.CodeName).CodeModule
            if cm_tr.CountOfLines > 0:
                cm_tr.DeleteLines(1, cm_tr.CountOfLines)
            cm_tr.AddFromString(TRACKER_EVENT_VBA)

            ws_yg = wb.Worksheets(YEARLY_GOALS_SHEET)
            cm_yg = vbp.VBComponents(ws_yg.CodeName).CodeModule
            if cm_yg.CountOfLines > 0:
                cm_yg.DeleteLines(1, cm_yg.CountOfLines)
            cm_yg.AddFromString(YEARLY_GOALS_EVENT_VBA)

            ws_dt = wb.Worksheets(DAILY_TASKS_SHEET)
            cm_dt = vbp.VBComponents(ws_dt.CodeName).CodeModule
            if cm_dt.CountOfLines > 0:
                cm_dt.DeleteLines(1, cm_dt.CountOfLines)
            cm_dt.AddFromString(DAILY_TASKS_EVENT_VBA)

            # Mount Effect 4: Sleek Quick-Action Pastel Pill Buttons (Tracker, Daily Tasks, Guide)
            add_pro_pill_buttons(wb, meta)

        # Disable Page Breaks on every worksheet for zero-lag scrolling & ticking!
        for ws in wb.Worksheets:
            try:
                ws.DisplayPageBreaks = False
            except Exception:
                pass

        # 6. Restore calculation & force full rebuild
        xl.Calculation = -4105  # xlCalculationAutomatic
        xl.ScreenUpdating = True
        xl.CalculateFullRebuild()
        time.sleep(0.4)

        # Hide internal sheets cleanly (`xlSheetHidden = 0`)
        for hname in hidden_names:
            try:
                wb.Worksheets(hname).Visible = 0
            except Exception:
                pass

        for ws in wb.Worksheets:
            if ws.Visible == -1:
                ws.Activate()
                ws.Range("A1").Select()
        wb.Worksheets(GUIDE_SHEET).Activate()
        wb.Worksheets(GUIDE_SHEET).Range("A1").Select()

        xl.EnableEvents = True
        wb.SaveAs(str(final_path.resolve()), FileFormat=file_format)

        # 7. Capture fresh visual previews
        if capture_previews:
            for cap in meta.get("captures", []):
                ws_c = wb.Worksheets(cap["sheet"])
                ws_c.Activate()
                ws_c.Range("A1").Select()
                sz = grab_range_png(ws_c, cap["range"], PREVIEWS_DIR / cap["out"])
                print(f"      [PNG] {cap['out']} ({sz[0]}x{sz[1]})", flush=True)

        wb.Worksheets(GUIDE_SHEET).Activate()
        wb.Save()
        dt = time.perf_counter() - t0
        print(f"  ✓ [{edition}] {final_path.name} ({final_path.stat().st_size:,} B, cbs={cb_count}, pics={pic_count}, {dt:.1f}s)",
              flush=True)
    finally:
        xl.EnableEvents = True
        wb.Close(SaveChanges=False)


def derive_offline_from_pro(xl, only: list[str] | None = None):
    """Ultra-fast (~2s/file) derivation of 100% macro-free Universal Offline `.xlsx` from compiled Pro `.xlsm`:
    Updates the Guide & tracker cue text to the No-Macro Offline copy and saves with FileFormat=51 (.xlsx),
    which natively strips vbaProject.bin while keeping all 392 Form Checkboxes & 53 Dynamic Linked Pictures intact!"""
    from excel_builder import TEMPLATES
    OFFLINE_OUT_DIR.mkdir(parents=True, exist_ok=True)
    xl.DisplayAlerts = False
    xl.EnableEvents = False
    for tdef in TEMPLATES:
        if only and tdef.stem not in only and tdef.short_key not in only:
            continue
        t0 = time.perf_counter()
        pro_path = PRO_OUT_DIR / f"{tdef.stem}_Pro.xlsm"
        off_path = OFFLINE_OUT_DIR / f"{tdef.stem}.xlsx"
        if off_path.exists():
            off_path.unlink()
        wb = xl.Workbooks.Open(str(pro_path.resolve()))
        try:
            # Update `📖 Hướng Dẫn` edition copy cleanly to Offline No-Macro version (v3.0: 5-tab layout!)
            ws_g = wb.Worksheets(GUIDE_SHEET)
            ws_g.Range("B4").Value = (
                "✨ BẢN EXCEL OFFLINE KHÔNG MACRO (.XLSX)  •  Gọn nhẹ 5 tab  •  "
                "Chạy mọi Excel 2016–365 Win/Mac  •  Không cảnh báo bảo mật"
            )
            ws_g.Range("D8").Value = (
                "Bảng theo dõi 31 ngày không Macro siêu nhẹ: lịch động, hoạt ảnh 6 giai đoạn offline & Streak Heatmap!"
            )
            # Dynamically locate Section 1 & Section 3 header rows (handles bonus tabs cleanly!)
            r_s1, r_s3 = 13, 18
            for rr_scan in range(8, 28):
                val_scan = str(ws_g.Cells(rr_scan, 2).Value or "")
                if "1. CÁCH SỬ DỤNG" in val_scan:
                    r_s1 = rr_scan
                elif "3. TÙY BIẾN" in val_scan:
                    r_s3 = rr_scan
            ws_g.Cells(r_s1 + 1, 2).Value = (
                "1️⃣  Mở tab Tracker chính và click thẳng vào ô Checkbox (☑ / ☐) — KHÔNG Macro, "
                "KHÔNG cảnh báo bảo mật, KHÔNG cần Internet, mở cực nhanh trên mọi Excel 2016–365!"
            )
            ws_g.Cells(r_s1 + 1, 5).Value = (
                "⚡  File điền sẵn ~22 ngày mẫu sinh động. Muốn reset về 0%: chọn vùng C17:AG36 → nhấn Delete "
                "(Mac: fn + Backspace) → toàn bộ ô tick về trống & cây về Stage 0!"
            )
            ws_g.Cells(r_s1 + 2, 5).Value = (
                "📑  Sang tháng mới trong 2 giây (bản Không Macro): chuột phải tab Tracker → Move or Copy → "
                "tick ☑ Create a copy (hoặc nhân bản file cho tháng mới), chọn tháng ở B3 & xóa vùng tick."
            )
            ws_g.Cells(r_s1 + 3, 5).Value = (
                "💡  Mẹo: Nếu muốn lưu tự động nhiều Tháng & nhiều Năm ngay trên 1 trang duy nhất, "
                "hãy dùng bản Pro (.xlsm) trong thư mục pro_macro/!"
            )
            ws_g.Cells(r_s3 + 1, 5).Value = (
                "📅  Đổi Tháng (B3) & Năm (B5) tự nhảy lịch (28/29/30/31 ngày + thứ Mon–Sun), ẩn gọn ngày thừa cuối tháng!"
            )
            ws_g.Cells(r_s3 + 2, 5).Value = (
                "🏆  Tổng Kết & Thành Tựu Năm: Đồng bộ live tiến độ tháng hiện tại & Yearly Goals, tự mở khóa 8 Huy hiệu kỷ luật "
                "& hiển thị 0% / Stage 0 khi chọn năm trống (vd: 2028)!"
            )
            ws_g.Cells(r_s3 + 3, 5).Value = (
                "⚡  Cần lưu lịch sử tự động 12 tháng × nhiều năm trên 1 tab? Chuyển sang dùng bản Pro (.xlsm) đã đi kèm sẵn!"
            )
            # Ensure generous vertical padding on Offline instruction rows (zero clipping!)
            for r_inst in (r_s1 + 1, r_s1 + 2, r_s1 + 3, r_s3 + 1, r_s3 + 2, r_s3 + 3):
                if ws_g.Rows(r_inst).RowHeight < 66:
                    ws_g.Rows(r_inst).RowHeight = 66
            # Strip all Pro macro Quick-Action Pill Buttons (`BTN_*`) & any FX shapes cleanly!
            for ws_clean in wb.Worksheets:
                try:
                    for idx_sh in range(ws_clean.Shapes.Count, 0, -1):
                        snm = str(ws_clean.Shapes(idx_sh).Name or "")
                        if snm.startswith("BTN_") or snm.startswith("FX_"):
                            ws_clean.Shapes(idx_sh).Delete()
                except Exception:
                    pass
            # Update tracker cue line B7 & Daily Tasks cue line B6:F6
            ws_tr = wb.Worksheets(tdef.tracker_name)
            ws_tr.Range("B7").Value = "📌 Bản Không Macro • Dùng bản Pro (.xlsm) để tự lưu nhiều tháng/năm"
            try:
                ws_dt = wb.Worksheets(DAILY_TASKS_SHEET)
                ws_dt.Range("B6:F6").UnMerge()
                ws_dt.Range("B6:F6").Merge()
                ws_dt.Range("B6").HorizontalAlignment = -4108  # xlCenter
                ws_dt.Range("B6").Value = (
                    "📌  Bản Không Macro (Excel 2016–365) • Tick xong việc để xem hoạt ảnh lớn dần "
                    "— Dùng bản Pro (.xlsm) để tự lưu nhiều ngày!"
                )
            except Exception:
                pass

            ws_g.Activate()
            ws_g.Range("A1").Select()
            wb.SaveAs(str(off_path.resolve()), FileFormat=51)  # Pure macro-free .xlsx!
            dt = time.perf_counter() - t0
            print(f"  ✓ [offline .xlsx] {off_path.name} ({off_path.stat().st_size:,} B, {dt:.1f}s)", flush=True)
        finally:
            wb.Close(SaveChanges=False)


def main():
    import gc
    args = sys.argv[1:]
    mode = args[0] if args else "all"
    rest = args[1:]
    start_idx = None
    end_idx = None
    only = []
    i = 0
    while i < len(rest):
        if rest[i] == "--start" and i + 1 < len(rest):
            start_idx = int(rest[i + 1]); i += 2
        elif rest[i] == "--end" and i + 1 < len(rest):
            end_idx = int(rest[i + 1]); i += 2
        else:
            only.append(rest[i]); i += 1

    if start_idx is not None or end_idx is not None:
        from excel_builder import TEMPLATES
        lo = (start_idx or 1) - 1
        hi = end_idx or len(TEMPLATES)
        only = [t.short_key for t in TEMPLATES[lo:hi]]
    only = only or None

    def _new_excel():
        xl_app = win32.DispatchEx("Excel.Application")
        xl_app.Visible = False
        xl_app.DisplayAlerts = False
        try:
            xl_app.EnableAnimations = False
        except Exception:
            pass
        return xl_app

    if mode == "derive-offline":
        print(f"\nDeriving pure macro-free Offline .xlsx files from Pro .xlsm (only={only})...", flush=True)
        xl = _new_excel()
        try:
            derive_offline_from_pro(xl, only)
        finally:
            xl.Quit()
        return

    pro_manifests = build_base_pro(only) if mode in ("all", "pro") else []
    off_manifests = build_base_offline(only) if mode in ("all", "offline") else []
    if mode in ("all", "gsheets"):
        build_all_gsheets(only)

    all_jobs = [(m, True) for m in pro_manifests] + [(m, False) for m in off_manifests]
    if not all_jobs:
        return

    # Anti-hang batch protocol: recycle EXCEL.EXE COM cleanly every 5 templates!
    print(f"\nStarting Excel COM compilation ({len(all_jobs)} workbook(s), recycling COM every 5)...", flush=True)
    for chunk_i in range(0, len(all_jobs), 5):
        chunk = all_jobs[chunk_i:chunk_i + 5]
        xl = _new_excel()
        try:
            for meta, cap_prev in chunk:
                enhance_one(xl, meta, capture_previews=cap_prev)
        finally:
            xl.Quit()
            del xl
            gc.collect()
            time.sleep(0.5)


if __name__ == "__main__":
    main()
