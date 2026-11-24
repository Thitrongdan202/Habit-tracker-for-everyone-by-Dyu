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

import hashlib
import os
import re
import sys
import time
import zipfile
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
from hx.annual import ANNUAL_SHEET, ASSETS_SHEET, DATABASE_SHEET, HISTORY_SHEET, YEARLY_GOALS_SHEET
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
    "Private Sub Workbook_BeforeSave(ByVal SaveAsUI As Boolean, Cancel As Boolean)\r\n"
    "    modHabitState.FlushAllDirty\r\n"
    "End Sub\r\n"
    "Private Sub Workbook_BeforeClose(Cancel As Boolean)\r\n"
    "    modHabitState.FlushAllDirty\r\n"
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
    "    ElseIf Not Intersect(Target, Me.Range(\"B17:B36,AI17:AI36\")) Is Nothing Then\r\n"
    "        modHabitState.HandleTrackerMetaEdit Me\r\n"
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
    "    ElseIf Not Intersect(Target, Me.Range(\"C6:F25\")) Is Nothing Then\r\n"
    "        modHabitState.HandleGoalsMetaEdit Me\r\n"
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
    "    ElseIf Not Intersect(Target, Me.Range(\"C9:F28,B31\")) Is Nothing Then\r\n"
    "        modHabitState.HandleDailyMetaEdit Me\r\n"
    "    End If\r\n"
    "End Sub\r\n"
)

ANNUAL_EVENT_VBA = (
    "Option Explicit\r\n"
    "Private Sub Worksheet_Change(ByVal Target As Range)\r\n"
    "    If Not Intersect(Target, Me.Range(\"B3\")) Is Nothing Then\r\n"
    "        modHabitState.HandleAnnualYearSwitch Me\r\n"
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

    # 1. Monthly Tracker (`B7` cell tray): [◀ Tháng] [Tháng ▶] [✨ FX: BẬT] [↩ Undo]
    ws_tr = wb.Worksheets(meta["tracker_sheet"])
    b7 = ws_tr.Range("B7")
    pad_x = 2.0
    gap = 2.0
    bh = min(19.0, max(15.0, b7.Height - 5.0))
    bt = b7.Top + (b7.Height - bh) / 2.0
    avail_w = b7.Width - 2 * pad_x - 3 * gap
    w_nav  = avail_w * 0.242
    w_fx   = avail_w * 0.282
    w_undo = avail_w - 2 * w_nav - w_fx
    x0 = b7.Left + pad_x
    _add_pill_button(ws_tr, "BTN_PREV_MONTH", "◀ Tháng", x0, bt, w_nav, bh,
                     bgr_sft, bgr_pri, bgr_ink, "BtnPrevMonth", font_size=7.0)
    _add_pill_button(ws_tr, "BTN_NEXT_MONTH", "Tháng ▶", x0 + w_nav + gap, bt, w_nav, bh,
                     bgr_sft, bgr_pri, bgr_ink, "BtnNextMonth", font_size=7.0)
    _add_pill_button(ws_tr, "BTN_FX_TOGGLE", "✨ FX: BẬT", x0 + 2 * (w_nav + gap), bt, w_fx, bh,
                     bgr_pri, bgr_dk, bgr_onp, "BtnToggleFX", font_size=7.0)
    _add_pill_button(ws_tr, "BTN_UNDO", "↩ Undo", x0 + 2 * (w_nav + gap) + w_fx + gap, bt, w_undo, bh,
                     bgr_wht, bgr_pri, bgr_dk, "UndoLastHabitEdit", font_size=7.0)

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

    # 3. Guide (Section 5 left-aligned header bar, right CTA pill directly above last stage — ZERO overlap!)
    n_stages = int(meta.get("num_stages", 6))
    ws_g = wb.Worksheets(GUIDE_SHEET)
    r_sec5 = 23
    for rr_g in range(18, 36):
        val_g = str(ws_g.Cells(rr_g, 2).Value or "")
        if "5. HOẠT ẢNH" in val_g:
            r_sec5 = rr_g
            break
    last_g_col = 1 + n_stages  # Col G (7) for 6-stage, Col H (8) for 7-stage, Col I (9) for 8-stage!
    sec5_bar = ws_g.Range(ws_g.Cells(r_sec5, 2), ws_g.Cells(r_sec5, last_g_col))
    gw = 148.0
    gh = min(21.0, max(17.0, sec5_bar.Height - 4.0))
    gl = sec5_bar.Left + sec5_bar.Width - gw - 6.0
    gt = sec5_bar.Top + (sec5_bar.Height - gh) / 2.0
    _add_pill_button(ws_g, "BTN_DEMO_FX", "🎉 Thử Hiệu Ứng Pro", gl, gt, gw, gh,
                     bgr_wht, bgr_sft, bgr_dk, "BtnDemoFX", font_size=8.2)

    # 4. `_Assets` 1-Click Custom Sprite Sync button (`D2:F2` right beside B2:B7/B8 & C2)
    ws_a = wb.Worksheets(ASSETS_SHEET)
    d2 = ws_a.Range("D2")
    _add_pill_button(ws_a, "BTN_SYNC_ASSETS", f"🔄 Đồng bộ {n_stages} ảnh mới (SyncSprites)",
                     d2.Left + 8.0, d2.Top + 12.0, 224.0, 32.0,
                     bgr_pri, bgr_dk, bgr_onp, "SyncSpritesFromAssets", font_size=9.0)


def _map_anim_to_stack_info(anim_name: str) -> tuple[str, str, bool]:
    """Map legacy `Anim_*` manifest names to v3.6 Pure-ASCII Sprite Stack prefix & `_Calc` stage cell."""
    if anim_name.startswith("Anim_Day"):
        d_num = int(anim_name[8:10])
        col_let = xl_rowcol_to_cell(14, d_num, False, False)  # row 15 (0-based 14), col 1..31 -> B15..AF15
        return f"SPR_D{d_num:02d}_S", col_let, True
    if anim_name == "Anim_MonthlyHero":
        return "SPR_MHERO_S", "C14", False
    if anim_name == "Anim_DailyTaskHero":
        return "SPR_DHERO_S", "AN16", False
    if anim_name == "Anim_YearlyGoals":
        return "SPR_GHERO_S", "AN7", False
    if anim_name == "Anim_AnnualHero":
        return "SPR_AHERO_S", "AN8", False
    if anim_name == "Anim_AchBadges":
        return "SPR_BHERO_S", "AN9", False
    if anim_name.startswith("Anim_AnnualM"):
        m_num = int(anim_name[12:14])
        return f"SPR_AM{m_num:02d}_S", f"AW{1 + m_num}", False
    raise ValueError(f"Unmapped dynamic animation slot: {anim_name}")


def add_pro_native_sprite_stacks(wb, meta: dict, slug: str) -> tuple[int, list[dict]]:
    """v3.6/v3.7 Turbo: Place crisp Native Pre-Placed PNG Sprite Stacks (`SPR_*_S0..S<N-1>` + `Guide_Stage0..<N-1>`).
    Supports both 6-stage (#01-#35) and 7-stage Digimon (#36-#40) seamlessly!"""
    n_stages = int(meta.get("num_stages", 6))
    img_paths = [str((ASSETS_DIR / slug / f"stage_{k}.png").resolve()) for k in range(n_stages)]
    pic_count = 0
    stack_slots: list[dict] = []

    # 1. Dynamic sprite stacks grouped by worksheet
    dyn_groups = defaultdict(list)
    for item in meta["dyn_anims"]:
        dyn_groups[item["sheet"]].append(item)

    for sheet_name, items in dyn_groups.items():
        ws_dst = wb.Worksheets(sheet_name)
        ws_dst.Activate()
        for it in items:
            prefix, calc_cell, allow_hide = _map_anim_to_stack_info(it["name"])
            dst = ws_dst.Range(ws_dst.Cells(it["r1"] + 1, it["c1"] + 1),
                               ws_dst.Cells(it["r2"] + 1, it["c2"] + 1))
            align_bottom = it.get("align_bottom", False)
            pad_x = 1.5 if align_bottom else 4.5
            pad_y = 2.5 if align_bottom else 4.5
            max_w = max(8.0, dst.Width - 2.0 * pad_x)
            max_h = max(8.0, dst.Height - 2.0 * pad_y)
            side = min(max_w, max_h)
            left = dst.Left + (dst.Width - side) / 2.0
            top = (dst.Top + dst.Height - side - 2.0) if align_bottom else (dst.Top + (dst.Height - side) / 2.0)

            for k in range(n_stages):
                shp = ws_dst.Shapes.AddPicture(
                    Filename=img_paths[k], LinkToFile=False, SaveWithDocument=True,
                    Left=left, Top=top, Width=side, Height=side,
                )
                shp.Name = f"{prefix}{k}"
                shp.Line.Visible = 0
                shp.LockAspectRatio = -1
                shp.Placement = 1
                shp.Visible = -1 if k == 0 else 0
                pic_count += 1

            stack_slots.append({
                "sheet": sheet_name,
                "prefix": prefix,
                "calc_cell": calc_cell,
                "allow_hide": allow_hide,
            })

    # 2. Static Guide Stage 0..5 previews (`Guide_Stage0`..`Guide_Stage5`, native PNGs!)
    for sp in meta["static_pics"]:
        ws_dst = wb.Worksheets(sp["sheet"])
        nm = sp.get("name", "")
        st_idx = int(nm[-1]) if nm and nm[-1].isdigit() else 0
        dst = ws_dst.Range(ws_dst.Cells(sp["r1"] + 1, sp["c1"] + 1),
                           ws_dst.Cells(sp["r2"] + 1, sp["c2"] + 1))
        pad = 4.5
        side = min(max(8.0, dst.Width - 2.0 * pad), max(8.0, dst.Height - 2.0 * pad))
        left = dst.Left + (dst.Width - side) / 2.0
        top = dst.Top + (dst.Height - side) / 2.0
        shp = ws_dst.Shapes.AddPicture(
            Filename=img_paths[st_idx], LinkToFile=False, SaveWithDocument=True,
            Left=left, Top=top, Width=side, Height=side,
        )
        shp.Name = nm
        shp.Line.Visible = 0
        shp.LockAspectRatio = -1
        shp.Placement = 1
        shp.Visible = -1
        pic_count += 1

    return pic_count, stack_slots


def clamp_pro_top_chart(wb, meta: dict):
    """Ensure the top Daily Productivity chart on Monthly Tracker ends cleanly ABOVE Row 8
    so it NEVER overlaps down into Row 8 or the habit checkbox grid!"""
    ws_tr = wb.Worksheets(meta["tracker_sheet"])
    row2_top = float(ws_tr.Rows(2).Top)
    row8_top = float(ws_tr.Rows(8).Top)
    col35_left = float(ws_tr.Columns(35).Left)
    max_bottom = row8_top - 2.5
    for co in ws_tr.ChartObjects():
        if float(co.Top) < row8_top and float(co.Left) < col35_left:
            new_top = row2_top + 1.5
            new_h = max(40.0, max_bottom - new_top)
            co.Top = new_top
            co.Height = new_h
            co.Placement = 1  # xlMoveAndSize


def apply_pro_sheet_protection(wb, meta: dict):
    """Unlock ONLY legitimate user-editable cells across the 5 visible Pro tabs, lock ALL
    headers/KPIs/formulas/TOTAL row 37, and protect with `UserInterfaceOnly=True` (no password)!"""
    # 1. Monthly Tracker
    ws_tr = wb.Worksheets(meta["tracker_sheet"])
    ws_tr.Cells.Locked = True
    for (r1, c1, r2, c2) in meta.get("tracker_unlock_ranges", []):
        rng_obj = ws_tr.Range(ws_tr.Cells(r1 + 1, c1 + 1), ws_tr.Cells(r2 + 1, c2 + 1))
        rng_obj.Locked = False
        # Belt-and-suspenders: never unlock any formula cell inside an unlocked addon block!
        try:
            f_cells = rng_obj.SpecialCells(-4123)  # xlCellTypeFormulas
            f_cells.Locked = True
        except Exception:
            pass
    # Belt-and-suspenders: guarantee TOTAL row 37 is 100% locked!
    ws_tr.Rows(37).Locked = True

    # 2. Daily One-Off Tasks
    ws_dt = wb.Worksheets(DAILY_TASKS_SHEET)
    ws_dt.Cells.Locked = True
    ws_dt.Range("D5:F5").Locked = False
    ws_dt.Range("B9:F28").Locked = False
    ws_dt.Range("B31:F35").Locked = False

    # 3. Yearly Goals & Habits
    ws_yg = wb.Worksheets(YEARLY_GOALS_SHEET)
    ws_yg.Cells.Locked = True
    ws_yg.Range("I2").Locked = False
    ws_yg.Range("B6:F25").Locked = False

    # 4. Annual Achievements — ONLY Year dropdown B3 unlocked!
    ws_ann = wb.Worksheets(ANNUAL_SHEET)
    ws_ann.Cells.Locked = True
    ws_ann.Range("B3").Locked = False

    # 5. Guide — ONLY the threshold config cells unlocked!
    ws_g = wb.Worksheets(GUIDE_SHEET)
    ws_g.Cells.Locked = True
    for thr_nm in ("CFG_THR_M1", "CFG_THR_0", "CFG_THR_1", "CFG_THR_2", "CFG_THR_3"):
        try:
            wb.Names(thr_nm).RefersToRange.Locked = False
        except Exception:
            pass

    for ws_p in (ws_g, ws_tr, ws_dt, ws_yg, ws_ann):
        ws_p.Protect(
            Password="",
            DrawingObjects=False,
            Contents=True,
            Scenarios=False,
            UserInterfaceOnly=True,
            AllowFormattingCells=False,
        )


def sync_initial_pro_sprite_visibility(wb, stack_slots: list[dict], n_stages: int = 6):
    """Set initial `.Visible` on every `SPR_*_S0..S<N-1>` stack to match live `_Calc` stage indices."""
    ws_calc = wb.Worksheets(CALC_SHEET)
    hide_slot = n_stages + 1
    by_sheet = defaultdict(list)
    for slot in stack_slots:
        by_sheet[slot["sheet"]].append(slot)
    for sheet_name, slots in by_sheet.items():
        ws = wb.Worksheets(sheet_name)
        for slot in slots:
            raw = ws_calc.Range(slot["calc_cell"]).Value2
            try:
                st = int(round(float(raw)))
            except Exception:
                st = 1
            st = max(1, min(hide_slot if slot.get("allow_hide") else n_stages, st))
            prefix = slot["prefix"]
            for k in range(n_stages):
                want = -1 if (k == st - 1 and st <= n_stages) else 0
                ws.Shapes(f"{prefix}{k}").Visible = want


def deduplicate_xlsm_media(xlsm_path: Path, slug: str, n_stages: int = 6) -> tuple[int, int]:
    """Post-COM OOXML Sprite-Aware Media Deduplication:
    Maps every `SPR_*_S<k>`, `Guide_Stage<k>`, and `ASSET_S<k>` shape across ALL drawings
    directly to the N canonical high-DPI `xl/media/image1.png..imageN.png` (`stage_0..N-1.png`),
    eliminating 100% of Excel's per-size re-encoded duplicates!"""
    import xml.etree.ElementTree as ET

    stage_bytes = [(ASSETS_DIR / slug / f"stage_{k}.png").read_bytes() for k in range(n_stages)]

    with zipfile.ZipFile(xlsm_path, "r") as zin:
        infos = zin.infolist()
        blobs = {info.filename: zin.read(info.filename) for info in infos}

    raw_media = sorted(n for n in blobs if n.startswith("xl/media/"))

    # Inspect each drawing XML -> map (rels_path, rId) -> stage index (0..5)
    rels_rid_to_stage: dict[str, dict[str, int]] = {}
    referenced_other_media: set[str] = set()

    for fname, data in blobs.items():
        if not (fname.startswith("xl/drawings/drawing") and fname.endswith(".xml")):
            continue
        rels_name = f"xl/drawings/_rels/{os.path.basename(fname)}.rels"
        rid_map: dict[str, int] = {}
        try:
            root = ET.fromstring(data)
            for pic in root.iter():
                if not pic.tag.endswith("}pic"):
                    continue
                shp_name = ""
                rid = ""
                for elem in pic.iter():
                    if elem.tag.endswith("}cNvPr") and not shp_name:
                        shp_name = elem.attrib.get("name", "")
                    elif elem.tag.endswith("}blip") and not rid:
                        for ak, av in elem.attrib.items():
                            if ak.endswith("}embed"):
                                rid = av
                                break
                if rid and shp_name:
                    m_st = re.search(r"(?:_S|Guide_Stage|ASSET_S)([0-7])$", shp_name)
                    if m_st and int(m_st.group(1)) < n_stages:
                        rid_map[rid] = int(m_st.group(1))
        except Exception:
            pass
        if rid_map:
            rels_rid_to_stage[rels_name] = rid_map

    # Rewrite drawing `.rels` files to point sprite rIds -> `../media/image1.png..image6.png`
    rel_tag_pat = re.compile(r'(<Relationship\b[^>]*>)')
    id_pat = re.compile(r'\bId="([^"]+)"')
    tgt_pat = re.compile(r'\bTarget="([^"]+)"')

    updated_blobs: dict[str, bytes] = {}
    for fname, data in blobs.items():
        if fname.endswith(".rels") and b"media/" in data:
            txt = data.decode("utf-8")
            rid_map = rels_rid_to_stage.get(fname, {})

            def _fix_rel(m: re.Match) -> str:
                tag = m.group(1)
                im = id_pat.search(tag)
                tm = tgt_pat.search(tag)
                if not im or not tm:
                    return tag
                rid = im.group(1)
                tgt = tm.group(1)
                if rid in rid_map:
                    canon_tgt = f"../media/image{rid_map[rid] + 1}.png"
                    return tgt_pat.sub(f'Target="{canon_tgt}"', tag, count=1)
                if "media/" in tgt:
                    referenced_other_media.add("xl/media/" + os.path.basename(tgt))
                return tag

            new_txt = rel_tag_pat.sub(_fix_rel, txt)
            updated_blobs[fname] = new_txt.encode("utf-8")

    canon_media = {f"xl/media/image{k + 1}.png": stage_bytes[k] for k in range(n_stages)}

    tmp_path = xlsm_path.with_suffix(".dedup.tmp")
    with zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zout:
        written_media: set[str] = set()
        for info in infos:
            fname = info.filename
            if fname.startswith("xl/media/"):
                if fname in canon_media:
                    zout.writestr(fname, canon_media[fname])
                    written_media.add(fname)
                elif fname in referenced_other_media:
                    zout.writestr(info, blobs[fname])
                    written_media.add(fname)
                continue
            zout.writestr(info, updated_blobs.get(fname, blobs[fname]))
        for cname, cbytes in canon_media.items():
            if cname not in written_media:
                zout.writestr(cname, cbytes)
                written_media.add(cname)

    tmp_path.replace(xlsm_path)
    return len(raw_media), len(written_media)


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

        # 1. Populate `_Assets!B2:B<1+N>` with 300x300px high-DPI PNG sprites
        n_stages = int(meta.get("num_stages", 6))
        ws_a = wb.Worksheets(ASSETS_SHEET)
        ws_a.Visible = -1
        ws_a.Activate()
        xl.ActiveWindow.DisplayGridlines = False
        for idx in range(n_stages):
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
            shp.Name = f"ASSET_S{idx}"
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

        # 3 & 4. Dynamic Visuals:
        #   - pro_xlsm (v3.6 Turbo): Native Pre-Placed Sprite Stacks (ZERO Camera Linked Pictures!)
        #   - offline: Legacy Linked Pictures (kept intact for offline no-macro builds)
        stack_slots: list[dict] = []
        if edition == "pro_xlsm":
            pic_count, stack_slots = add_pro_native_sprite_stacks(wb, meta, slug)
        else:
            for item in meta["dyn_anims"]:
                wb.Names.Add(Name=item["name"], RefersTo=item["refers_to"])

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

        # 5. Inject v3.6 Turbo VBA Engine & Quick-Action Pastel Pill Buttons into Pro `.xlsm`
        if edition == "pro_xlsm":
            vbp = wb.VBProject
            vbp.VBComponents.Import(str(VBA_MOD_PATH.resolve()))

            # Inject ThisWorkbook lifecycle events (Open, BeforeSave, BeforeClose, SheetActivate)
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

            ws_ann = wb.Worksheets(ANNUAL_SHEET)
            cm_ann = vbp.VBComponents(ws_ann.CodeName).CodeModule
            if cm_ann.CountOfLines > 0:
                cm_ann.DeleteLines(1, cm_ann.CountOfLines)
            cm_ann.AddFromString(ANNUAL_EVENT_VBA)

            # Mount Quick-Action Pastel Pill Buttons (Tracker, Daily Tasks, Guide, _Assets)
            add_pro_pill_buttons(wb, meta)

        # Disable Page Breaks on every worksheet for zero-lag scrolling & ticking!
        for ws in wb.Worksheets:
            try:
                ws.DisplayPageBreaks = False
            except Exception:
                pass

        # 6. Restore calculation & force full rebuild, then sync initial native sprite visibility!
        xl.Calculation = -4105  # xlCalculationAutomatic
        xl.CalculateFullRebuild()
        if edition == "pro_xlsm":
            if stack_slots:
                sync_initial_pro_sprite_visibility(wb, stack_slots, n_stages=n_stages)
            clamp_pro_top_chart(wb, meta)
            apply_pro_sheet_protection(wb, meta)
        xl.ScreenUpdating = True
        time.sleep(0.25)

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
    finally:
        xl.EnableEvents = True
        wb.Close(SaveChanges=False)

    # 8. Post-COM OOXML SHA-256 Media Deduplication -> ONLY N unique PNGs inside `xl/media/`!
    media_info = ""
    if edition == "pro_xlsm":
        raw_m, uniq_m = deduplicate_xlsm_media(final_path, slug, n_stages=n_stages)
        media_info = f", media={uniq_m}/{raw_m}"
    dt = time.perf_counter() - t0
    print(f"  ✓ [{edition}] {final_path.name} ({final_path.stat().st_size:,} B, cbs={cb_count}, pics={pic_count}{media_info}, {dt:.1f}s)",
          flush=True)


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
