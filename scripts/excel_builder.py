"""
excel_builder.py — Version 2.0 base workbook builder for all 6 Habit Tracker themes.

Creates the structural .xlsx workbooks (card layouts, universal formulas, `_Calc`,
`_Assets` placeholder, charts, conditional formatting, data validations) and writes
a JSON manifest for `excel_com_enhancer.py` to compile Tier A Offline `.xlsx` files.

Run standalone to build Tier A staging files in `_build_tmp/`:
    python scripts/excel_builder.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import xlsxwriter

from hx.core import Theme, Styles, Canvas, acell, colname, qs
from hx.guide import build_guide, GUIDE_SHEET
from hx.tracker import (Habit, TrackerSpec, build_tracker, CALC_SHEET, CALC_STAGE_ROW,
                        R_IMG, R_TOT, day_col)
from hx.addons import (add_cactus_weekly_strip, add_rainbow_bottom_blocks,
                       add_wellness_mood_block, add_focus_rank_top_card)
from hx.extras import (build_yearly_goals_sheet, build_annual_overview_sheet,
                       build_reflection_notes_sheet, build_rainbow_analytics_sheet,
                       build_monthly_budget_sheet, build_life_overview_sheet,
                       build_gratitude_sheet, build_milestones_sheet)

BUILD_TMP = ROOT / "_build_tmp"
ASSETS_SHEET = "_Assets"


def add_assets_placeholder(wb, styles: Styles):
    """Create the clean `_Assets` sheet whose B2:B7 cells hold the 6 sprites (B8 = blank).
    Users can right-click any tab -> Unhide -> `_Assets` and paste their own 6 icons into B2:B7!"""
    t = styles.t
    ws = wb.add_worksheet(ASSETS_SHEET)
    ws.hide_gridlines(2)
    ws.set_column(0, 0, 26)
    ws.set_column(1, 1, 12.2)   # ~68pt square cell matching RowHeight 68pt
    ws.set_column(2, 2, 46)
    hdr = wb.add_format({"font_name": t.font, "font_size": 10, "bold": True,
                         "bg_color": t.primary, "font_color": t.on_primary,
                         "align": "center", "valign": "vcenter"})
    lab = wb.add_format({"font_name": t.font, "font_size": 9.5, "bold": True,
                         "bg_color": t.soft, "font_color": t.ink,
                         "align": "center", "valign": "vcenter"})
    # Pure borderless white cells for B2:B8 so Linked Pictures have ZERO border artifacts!
    slot = wb.add_format({"bg_color": t.card})
    tip = wb.add_format({"font_name": t.font, "font_size": 9, "font_color": t.muted,
                         "bg_color": t.page, "valign": "vcenter", "text_wrap": True})

    ws.set_row(0, 26)
    ws.write(0, 0, "STAGE", hdr)
    ws.write(0, 1, "SPRITE (B2:B7)", hdr)
    ws.write(0, 2, "HƯỚNG DẪN TỰ ĐỔI ẢNH HOẠT ẢNH", hdr)

    stage_notes = [
        ("Stage 0 (0%)", "Chưa tick thói quen nào — Dán ảnh nền trống / chậu đất vào B2"),
        ("Stage 1 (1%–24%)", "Khởi động — Dán ảnh mầm nhỏ vào B3"),
        ("Stage 2 (25%–49%)", "Đang phát triển — Dán ảnh cây con vào B4"),
        ("Stage 3 (50%–74%)", "Ổn định — Dán ảnh đang lớn vào B5"),
        ("Stage 4 (75%–99%)", "Sắp hoàn thành — Dán ảnh nụ hoa / gần đỉnh vào B6"),
        ("Stage 5 (100% ✨)", "Hoàn hảo 100% — Dán ảnh nở hoa rực rỡ vào B7 (cũng là Hero Icon!)"),
        ("(Ô trống ngoài tháng)", "GIỮ NGUYÊN Ô TRẮNG B8 — dùng để ẩn ngày 29/30/31 ở tháng ngắn"),
    ]
    for i, (st, note) in enumerate(stage_notes):
        r = 1 + i
        ws.set_row(r, 68)
        ws.write(r, 0, st, lab)
        ws.write_blank(r, 1, None, slot)
        ws.write(r, 2, note, tip)
    return ws


def _day_anim_manifest(tracker_sheet: str) -> list[dict]:
    items = []
    for k in range(1, 32):
        items.append({
            "name": f"Anim_Day{k:02d}",
            "refers_to": f"=INDEX({ASSETS_SHEET}!$B$2:$B$8,{CALC_SHEET}!${colname(k)}${CALC_STAGE_ROW + 1})",
            "sheet": tracker_sheet,
            "r1": R_IMG, "c1": day_col(k), "r2": R_IMG, "c2": day_col(k),
        })
    return items


# =========================================================================== #
#  6 CURATED TEMPLATES
# =========================================================================== #
def build_sunflower(out_path: Path, universal: bool = True) -> dict:
    theme = Theme(
        slug="sunflower", name="SUNFLOWER GARDEN BLUSH", emoji="🌻",
        tagline_vi="Gieo từng thói quen nhỏ mỗi ngày — ngắm khu vườn hướng dương nở rộ suốt cả tháng.",
        font="Segoe UI", font_title="Segoe UI Semibold", font_month="Segoe Script",
        page="#FFFDFB", card="#FFFFFF", ink="#4A3B3B", muted="#968181", line="#EAD8D8",
        primary="#D8A7A7", primary_dark="#B57A7A", on_primary="#FFFFFF", soft="#F5E6E6",
        chart_fill="#E7C2C2", chart_line="#C48888",
        week_head=["#D29E9E", "#DBA9A9", "#E3B8B8", "#EBC8C8", "#F2DADA"],
        week_tint=["#F6E8E8", "#F8ECEC", "#FAF0F0", "#FBF4F4", "#FCF7F7"],
        week_check=["#C88E8E", "#CE9696", "#D4A0A0", "#DAA8A8", "#DFB2B2"],
        week_on=["#FFFFFF", "#FFFFFF", "#5B3F3F", "#5B3F3F", "#5B3F3F"],
        streak_lo="#F1FAF4", streak_mid="#9AD6B0", streak_hi="#4E9F76",
        bar="#D8A7A7", donut_rest="#F4E7E7",
        chart_title="DAILY PROGRESS • TIẾN ĐỘ HẰNG NGÀY",
    )
    habits = [
        Habit("Tiết kiệm mỗi ngày", goal=31, p=0.96),
        Habit("Tập thể dục 30 phút", goal=24, p=0.84),
        Habit("Đọc sách 20 phút mỗi ngày", goal=26, p=0.82),
        Habit("Uống đủ 2L nước", goal=31, p=0.90),
        Habit("Hạn chế đồ ăn nhanh", goal=25, p=0.78),
        Habit("Ngủ đủ 8 tiếng", goal=26, p=0.85),
        Habit("Dọn dẹp nhà cửa 10 phút", goal=30, p=0.93),
        Habit("Viết nhật ký cuối ngày", goal=22, p=0.80),
        Habit("Học tiếng Anh 30 phút", goal=25, p=0.76),
        Habit("Thiền định / hít thở 10 phút", goal=24, p=0.81),
    ]
    tracker_name = "🌻 Monthly Tracker"
    wb = xlsxwriter.Workbook(str(out_path))
    styles = Styles(wb, theme)
    g_info = build_guide(wb, styles, tracker_name, [
        ("🎯 Yearly Goals & Habits", "Lập mục tiêu năm & chia nhỏ thành thói quen Tháng / Tuần / Ngày + bộ đếm hoa đã gieo."),
        ("📊 Annual Overview", "Tổng kết tiến độ 12 tháng, biểu đồ xu hướng cả năm & ghi chú đánh giá theo Quý."),
    ], universal=universal)

    ws = wb.add_worksheet(tracker_name)
    cv = Canvas(wb, ws, styles, tracker_name, universal=universal)
    tr = build_tracker(wb, styles, cv, TrackerSpec(
        sheet=tracker_name, habits=habits, month="October", year=2026, seed=11,
        label_tag="SUNFLOWER GARDEN", garden_label="SUNFLOWER GARDEN",
        grown_label="THIS MONTH,\nYOU'VE GROWN:", universal=universal,
    ))
    cv.flush()
    yg_info = build_yearly_goals_sheet(wb, styles, universal=universal)
    build_annual_overview_sheet(wb, styles, tr)
    if universal:
        add_assets_placeholder(wb, styles)
    wb.close()

    r1, c1, r2, c2 = tr.hero_icon_box
    return {
        "stem": "01_Sunflower_Garden_Blush", "slug": theme.slug, "tracker_sheet": tracker_name,
        "day_anims": _day_anim_manifest(tracker_name),
        "static_pics": g_info["linked_pictures"] + yg_info["linked_pictures"] + [
            {"sheet": tracker_name, "r1": r1, "c1": c1, "r2": r2, "c2": c2, "formula": f"={ASSETS_SHEET}!$B$7"}
        ],
        "checkboxes": {tracker_name: cv.form_checkboxes, **yg_info["checkboxes"]},
        "captures": [
            {"sheet": GUIDE_SHEET, "range": f"A1:H{g_info['guide_last_row']}", "out": "01_sunflower_guide.png"},
            {"sheet": tracker_name, "range": "A1:AN38", "out": "01_sunflower_tracker.png"},
            {"sheet": "🎯 Yearly Goals & Habits", "range": "A1:J26", "out": "01_sunflower_yearly_goals.png"},
            {"sheet": "📊 Annual Overview", "range": "A1:M26", "out": "01_sunflower_annual.png"},
        ],
    }


def build_cactus(out_path: Path, universal: bool = True) -> dict:
    theme = Theme(
        slug="cactus", name="CACTUS BLOOM PASTEL WEEKS", emoji="🌵",
        tagline_vi="5 tuần rực rỡ sắc pastel — kiên trì từng ngày để chậu xương rồng của bạn nở hoa hồng xinh xắn!",
        font="Segoe UI", font_title="Segoe UI Semibold", font_month="Segoe UI Semibold",
        page="#FCFCFA", card="#FFFFFF", ink="#3E4346", muted="#8A9296", line="#E3E6E8",
        primary="#78B884", primary_dark="#4E945D", on_primary="#FFFFFF", soft="#EDF7EF",
        chart_fill="#C2E5C7", chart_line="#5CA372",
        week_head=["#F8D7E8", "#E2D7F8", "#D7EAF8", "#D7F8E5", "#FAF2CC"],
        week_tint=["#FDF0F7", "#F4F0FD", "#EFF7FD", "#EFFDF5", "#FDFBE9"],
        week_check=["#D87AA8", "#9378D8", "#65A6D8", "#5BB885", "#D6B442"],
        week_on=["#6D3B55", "#4B3B73", "#2F5675", "#2B6144", "#6B5A20"],
        streak_lo="#EFFAF2", streak_mid="#9ED9AE", streak_hi="#4E9F76",
        bar="#78B884", donut_rest="#E7F2E9", weekday_style="letter", chart_markers=True,
        chart_title="Daily Productivity • Năng suất hằng ngày",
    )
    habits = [
        Habit("Ngủ đủ 7.5 – 8 tiếng", goal=28, p=0.88),
        Habit("Lập kế hoạch 24h mỗi sáng", goal=30, p=0.92),
        Habit("Tập thể dục / đi bộ 30 phút", goal=24, p=0.83),
        Habit("Uống đủ 2L nước lọc", goal=31, p=0.94),
        Habit("Ăn sáng đầy đủ dinh dưỡng", goal=28, p=0.86),
        Habit("Tự nấu bữa trưa / bữa tối lành mạnh", goal=22, p=0.79),
        Habit("Không dùng điện thoại sau 22h30", goal=24, p=0.75),
        Habit("Đọc sách / nghe sách nói 20 phút", goal=26, p=0.84),
        Habit("Chăm sóc da sáng & tối", goal=31, p=0.95),
        Habit("Viết 3 dòng tổng kết cuối ngày", goal=25, p=0.81),
    ]
    tracker_name = "🌵 Monthly Tracker"
    wb = xlsxwriter.Workbook(str(out_path))
    styles = Styles(wb, theme)
    g_info = build_guide(wb, styles, tracker_name, [
        ("📝 Reflection & Notes", "Đánh giá thành tựu, thử thách, thói quen đã vào guồng & bảng check-in 5 tuần pastel."),
    ], universal=universal)

    ws = wb.add_worksheet(tracker_name)
    cv = Canvas(wb, ws, styles, tracker_name, universal=universal)
    tr = build_tracker(wb, styles, cv, TrackerSpec(
        sheet=tracker_name, habits=habits, month="October", year=2026, seed=22,
        label_tag="MONTHLY HABIT TRACKER", garden_label="CACTUS GARDEN",
        grown_label="THIS MONTH,\nYOU HAVE GROWN:",
        right_labels=("GOAL", "DAYS\nCOMPLETE", "% DONE", "CURRENT\nSTREAK", "LONGEST\nSTREAK"),
        universal=universal,
    ))
    add_cactus_weekly_strip(wb, cv, tr)
    cv.flush()
    build_reflection_notes_sheet(wb, styles, tr)
    if universal:
        add_assets_placeholder(wb, styles)
    wb.close()

    r1, c1, r2, c2 = tr.hero_icon_box
    return {
        "stem": "02_Cactus_Bloom_Pastel_Weeks", "slug": theme.slug, "tracker_sheet": tracker_name,
        "day_anims": _day_anim_manifest(tracker_name),
        "static_pics": g_info["linked_pictures"] + [
            {"sheet": tracker_name, "r1": r1, "c1": c1, "r2": r2, "c2": c2, "formula": f"={ASSETS_SHEET}!$B$7"}
        ],
        "checkboxes": {tracker_name: cv.form_checkboxes},
        "captures": [
            {"sheet": tracker_name, "range": "A1:AN43", "out": "02_cactus_tracker.png"},
            {"sheet": "📝 Reflection & Notes", "range": "A1:I26", "out": "02_cactus_reflection.png"},
        ],
    }


def build_rainbow(out_path: Path, universal: bool = True) -> dict:
    theme = Theme(
        slug="lotus_stars", name="RAINBOW EXECUTIVE DONUTS", emoji="🌈",
        tagline_vi="Dashboard đa sắc pastel với 5 biểu đồ Donut theo tuần, lọ sao phát sáng & danh sách thói quen tuần.",
        font="Segoe UI", font_title="Segoe UI Semibold", font_month="Segoe UI Semibold",
        page="#F8F8FC", card="#FFFFFF", ink="#3D3C4E", muted="#8A88A0", line="#E4E2F0",
        primary="#9E9AD1", primary_dark="#6E69A8", on_primary="#FFFFFF", soft="#EFEEF9",
        chart_fill="#D7D5EE", chart_line="#8985C2",
        week_head=["#C7E5F5", "#C8EDD5", "#FAD3E4", "#FCE2B8", "#D9E8B8"],
        week_tint=["#EEF8FD", "#EFFBF3", "#FEF2F7", "#FEF7EB", "#F4F9E9"],
        week_check=["#5BA7CE", "#5CC084", "#E07AA8", "#E6A646", "#8BB34D"],
        week_on=["#2A5670", "#2A6343", "#7A3656", "#785319", "#476022"],
        streak_lo="#F0F8FC", streak_mid="#A9D7EE", streak_hi="#5B9EC4",
        bar="#B3AFE0", donut_rest="#ECEBF6", weekday_style="letter", chart_title="DAILY PROGRESS",
    )
    habits = [
        Habit("Uống đủ 2.5L nước mỗi ngày", goal=31, p=0.93),
        Habit("Tập luyện thể thao 30 phút", goal=22, p=0.84),
        Habit("Ngủ đủ 8 tiếng mỗi đêm", goal=30, p=0.91),
        Habit("Ăn đủ rau xanh & trái cây", goal=26, p=0.86),
        Habit("Thiền định 15 phút", goal=28, p=0.82),
        Habit("Đọc 20 trang sách", goal=24, p=0.85),
        Habit("Deep Work tập trung 2 giờ", goal=25, p=0.88),
        Habit("Đi bộ thư giãn 15 phút", goal=24, p=0.77),
        Habit("1 giờ không mạng xã hội (Tech detox)", goal=24, p=0.80),
    ]
    tracker_name = "🌈 Habit Dashboard"
    wb = xlsxwriter.Workbook(str(out_path))
    styles = Styles(wb, theme)
    g_info = build_guide(wb, styles, tracker_name, [
        ("📈 Analytics", "Bảng xếp hạng từng thói quen (Leaderboard) & phân tích hiệu suất theo Thứ trong tuần (Mon–Sun)."),
    ], universal=universal)

    ws = wb.add_worksheet(tracker_name)
    cv = Canvas(wb, ws, styles, tracker_name, universal=universal)
    tr = build_tracker(wb, styles, cv, TrackerSpec(
        sheet=tracker_name, habits=habits, month="October", year=2026, seed=33,
        label_tag="HABIT TRACKER", garden_label="STAR JAR GARDEN",
        grown_label="FULL STAR JARS\nTHIS MONTH:", universal=universal,
    ))
    add_rainbow_bottom_blocks(wb, cv, tr)
    cv.flush()
    build_rainbow_analytics_sheet(wb, styles, tr)
    if universal:
        add_assets_placeholder(wb, styles)
    wb.close()

    r1, c1, r2, c2 = tr.hero_icon_box
    return {
        "stem": "03_Rainbow_Executive_Donuts", "slug": theme.slug, "tracker_sheet": tracker_name,
        "day_anims": _day_anim_manifest(tracker_name),
        "static_pics": g_info["linked_pictures"] + [
            {"sheet": tracker_name, "r1": r1, "c1": c1, "r2": r2, "c2": c2, "formula": f"={ASSETS_SHEET}!$B$7"}
        ],
        "checkboxes": {tracker_name: cv.form_checkboxes},
        "captures": [
            {"sheet": tracker_name, "range": "A1:AN54", "out": "03_rainbow_dashboard.png"},
            {"sheet": "📈 Analytics", "range": "A1:N32", "out": "03_rainbow_analytics.png"},
        ],
    }


def build_botanical(out_path: Path, universal: bool = True) -> dict:
    theme = Theme(
        slug="botanical", name="SAGE BOTANICAL HABIT & BUDGET", emoji="🌿",
        tagline_vi="Sống xanh & quản lý tài chính tinh gọn — kết hợp thói quen lành mạnh với dòng tiền cá nhân.",
        font="Segoe UI", font_title="Segoe UI Semibold", font_month="Georgia",
        page="#FAF9F6", card="#FFFFFF", ink="#3A4A42", muted="#82928A", line="#E3E6DF",
        primary="#9FB8AD", primary_dark="#638375", on_primary="#FFFFFF", soft="#EDF3F0",
        chart_fill="#C7D9D1", chart_line="#6E9484",
        week_head=["#9FB8AD", "#B5C9BF", "#E8D5B7", "#E0A899", "#A8BFA8"],
        week_tint=["#EFF5F2", "#F3F8F5", "#FAF5EC", "#FAF0ED", "#F1F6F1"],
        week_check=["#6C9282", "#7EA393", "#B99A6B", "#C87D6C", "#749674"],
        week_on=["#FFFFFF", "#3A4A42", "#4E4029", "#FFFFFF", "#FFFFFF"],
        streak_lo="#EFF6F2", streak_mid="#A5CBB9", streak_hi="#4E8A6E",
        bar="#9FB8AD", donut_rest="#EEF2EF", chart_title="DAILY HABIT FLOW",
    )
    habits = [
        Habit("Ghi chép thu chi cuối ngày", goal=31, p=0.95),
        Habit("Không mua sắm bốc đồng (No-spend)", goal=25, p=0.84),
        Habit("Tự nấu ăn / mang cơm đi làm", goal=24, p=0.82),
        Habit("Tiết kiệm tối thiểu 50k/ngày", goal=28, p=0.90),
        Habit("Tập thể dục / Yoga 30 phút", goal=24, p=0.83),
        Habit("Đọc sách tài chính / phát triển bản thân", goal=25, p=0.86),
        Habit("Uống đủ 2L nước & hạn chế trà sữa", goal=30, p=0.88),
        Habit("Ngủ sớm trước 23h00", goal=26, p=0.79),
        Habit("Chăm sóc cây xanh & dọn bàn gọn", goal=28, p=0.87),
    ]
    tracker_name = "🌿 Daily Habits"
    wb = xlsxwriter.Workbook(str(out_path))
    styles = Styles(wb, theme)
    g_info = build_guide(wb, styles, tracker_name, [
        ("💰 Monthly Budget", "Trình quản lý thu chi toàn diện (Cash Flow Donut, Budget vs Actual, Savings Goals, Bills & Transaction Log)."),
        ("🔗 Life Overview", "Dashboard tổng hợp kết nối Tỷ lệ Thói quen % + Tỷ lệ Tiết kiệm % thành điểm Cân bằng Cuộc sống!"),
    ], universal=universal)

    ws = wb.add_worksheet(tracker_name)
    cv = Canvas(wb, ws, styles, tracker_name, universal=universal)
    tr = build_tracker(wb, styles, cv, TrackerSpec(
        sheet=tracker_name, habits=habits, month="October", year=2026, seed=44,
        label_tag="BOTANICAL LIVING", garden_label="MONSTERA GARDEN",
        grown_label="PLANTS FLOURISHED\nTHIS MONTH:", universal=universal,
    ))
    cv.flush()
    b_refs = build_monthly_budget_sheet(wb, styles, universal=universal)
    build_life_overview_sheet(wb, styles, tr, b_refs)
    if universal:
        add_assets_placeholder(wb, styles)
    wb.close()

    r1, c1, r2, c2 = tr.hero_icon_box
    return {
        "stem": "04_Sage_Botanical_Habit_And_Budget", "slug": theme.slug, "tracker_sheet": tracker_name,
        "day_anims": _day_anim_manifest(tracker_name),
        "static_pics": g_info["linked_pictures"] + [
            {"sheet": tracker_name, "r1": r1, "c1": c1, "r2": r2, "c2": c2, "formula": f"={ASSETS_SHEET}!$B$7"}
        ],
        "checkboxes": {tracker_name: cv.form_checkboxes, **b_refs["checkboxes"]},
        "captures": [
            {"sheet": tracker_name, "range": "A1:AN38", "out": "04_botanical_habits.png"},
            {"sheet": "💰 Monthly Budget", "range": "A1:N46", "out": "04_botanical_budget.png"},
            {"sheet": "🔗 Life Overview", "range": "A1:J22", "out": "04_botanical_life_overview.png"},
        ],
    }


def build_lavender(out_path: Path, universal: bool = True) -> dict:
    theme = Theme(
        slug="lavender_moon", name="LAVENDER DREAM WELLNESS & MOOD", emoji="🌙",
        tagline_vi="Chăm sóc thân – tâm – trí nhẹ nhàng với chu kỳ mặt trăng, nhật ký giấc ngủ, tâm trạng & lòng biết ơn.",
        font="Segoe UI", font_title="Segoe UI Semibold", font_month="Segoe Script",
        page="#F9F7FD", card="#FFFFFF", ink="#2D2A32", muted="#8A8299", line="#E6DEF5",
        primary="#A594F9", primary_dark="#7663D9", on_primary="#FFFFFF", soft="#F3EFFB",
        chart_fill="#D7C8F5", chart_line="#8E7CE8",
        week_head=["#C8B6E2", "#B9A7EA", "#A594F9", "#C5B4EE", "#DACDF2"],
        week_tint=["#F6F2FB", "#F4F0FC", "#F1EEFE", "#F5F2FC", "#F8F5FD"],
        week_check=["#967CC4", "#8872D8", "#7663D9", "#947ED4", "#A993D8"],
        week_on=["#3B2E52", "#FFFFFF", "#FFFFFF", "#3B2E52", "#3B2E52"],
        streak_lo="#F4F0FC", streak_mid="#C2B1F2", streak_hi="#7B66DB",
        bar="#B5A4F5", donut_rest="#EFEAF9", chart_title="DAILY WELLNESS & HABIT FLOW",
    )
    habits = [
        Habit("Ngủ trước 23h & đủ 7.5–8 tiếng", goal=28, p=0.87),
        Habit("Thiền / hít thở chánh niệm 10 phút", goal=28, p=0.89),
        Habit("Uống đủ 2L nước & trà thảo mộc", goal=31, p=0.94),
        Habit("Vận động nhẹ / Yoga / giãn cơ", goal=24, p=0.83),
        Habit("Skincare & chăm sóc bản thân", goal=31, p=0.95),
        Habit("Đọc sách giấy 20 phút trước khi ngủ", goal=25, p=0.84),
        Habit("Viết 3 điều biết ơn mỗi tối", goal=28, p=0.90),
        Habit("Tắt điện thoại 30 phút trước khi ngủ", goal=24, p=0.76),
        Habit("Dành 15 phút ngoài trời / ánh nắng", goal=26, p=0.82),
    ]
    tracker_name = "🌙 Habit & Wellness"
    wb = xlsxwriter.Workbook(str(out_path))
    styles = Styles(wb, theme)
    g_info = build_guide(wb, styles, tracker_name, [
        ("✨ Gratitude & Review", "Nhật ký 31 ngày biết ơn, khoảnh khắc đẹp, bộ đếm Self-care & tổng kết sức khỏe tinh thần."),
    ], universal=universal)

    ws = wb.add_worksheet(tracker_name)
    cv = Canvas(wb, ws, styles, tracker_name, universal=universal)
    tr = build_tracker(wb, styles, cv, TrackerSpec(
        sheet=tracker_name, habits=habits, month="October", year=2026, seed=55,
        label_tag="WELLNESS & MOOD", garden_label="MOON & LAVENDER",
        grown_label="FULL MOONS\nTHIS MONTH:", universal=universal,
    ))
    well_refs = add_wellness_mood_block(wb, cv, tr, seed=55)
    cv.flush()
    gr_info = build_gratitude_sheet(wb, styles, tr, well_refs, universal=universal)
    if universal:
        add_assets_placeholder(wb, styles)
    wb.close()

    r1, c1, r2, c2 = tr.hero_icon_box
    return {
        "stem": "05_Lavender_Dream_Wellness_Mood", "slug": theme.slug, "tracker_sheet": tracker_name,
        "day_anims": _day_anim_manifest(tracker_name),
        "static_pics": g_info["linked_pictures"] + [
            {"sheet": tracker_name, "r1": r1, "c1": c1, "r2": r2, "c2": c2, "formula": f"={ASSETS_SHEET}!$B$7"}
        ],
        "checkboxes": {tracker_name: cv.form_checkboxes, **gr_info["checkboxes"]},
        "captures": [
            {"sheet": tracker_name, "range": "A1:AN54", "out": "05_lavender_wellness.png"},
            {"sheet": "✨ Gratitude & Review", "range": "A1:I31", "out": "05_lavender_gratitude.png"},
        ],
    }


def build_focus(out_path: Path, universal: bool = True) -> dict:
    theme = Theme(
        slug="focus_rocket", name="MIDNIGHT NAVY BLUSH FOCUS", emoji="🚀",
        tagline_vi="Phong cách tương phản Navy – Blush sắc nét dành cho Deep Work, Coding & Gym với hệ thống tích điểm XP & thăng hạng!",
        font="Segoe UI", font_title="Segoe UI Semibold", font_month="Segoe UI Semibold",
        page="#F7F8FB", card="#FFFFFF", ink="#2B3452", muted="#727D9E", line="#DDE1EE",
        primary="#2B3452", primary_dark="#1D243B", on_primary="#FFFFFF", soft="#F2D7D9",
        chart_fill="#F2D7D9", chart_line="#2B3452",
        week_head=["#2B3452", "#3B476E", "#4D5B87", "#5C6B9C", "#7180B0"],
        week_tint=["#FAF1F2", "#F7F3F7", "#F2F4FA", "#F5F6FB", "#F8F3F5"],
        week_check=["#2B3452", "#3B476E", "#4D5B87", "#5C6B9C", "#C47D88"],
        week_on=["#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF"],
        streak_lo="#FAF1F2", streak_mid="#E4B7BD", streak_hi="#2B3452",
        bar="#E5A9B0", donut_rest="#EEF0F7",
        chart_title="DAILY FOCUS VELOCITY • TỐC ĐỘ TẬP TRUNG",
    )
    habits = [
        Habit("Deep Work tập trung cao độ 2 giờ", goal=26, p=0.90, extra={"xp_day": 30}),
        Habit("Luyện Code / Học chuyên môn 1 giờ", goal=26, p=0.88, extra={"xp_day": 25}),
        Habit("Tập Gym / Chạy bộ 45 phút", goal=22, p=0.84, extra={"xp_day": 25}),
        Habit("Không mạng xã hội 2 giờ đầu sáng", goal=28, p=0.85, extra={"xp_day": 20}),
        Habit("Đọc sách kỹ năng / tài liệu 25 phút", goal=25, p=0.82, extra={"xp_day": 15}),
        Habit("Review mục tiêu & lập Todo ngày mai", goal=30, p=0.93, extra={"xp_day": 15}),
        Habit("Ngủ đủ 7.5 – 8 tiếng đúng giờ", goal=28, p=0.86, extra={"xp_day": 15}),
        Habit("Uống đủ 2.5L nước & ăn đủ Protein", goal=31, p=0.94, extra={"xp_day": 10}),
    ]
    extra_cols = [
        {"key": "xp_day", "label": "XP /\nDAY", "width": 6.8, "kind": "input", "fmt": "0", "blank": 15},
        {"key": "xp_tot", "label": "TOTAL\nXP", "width": 8.2, "kind": "formula",
         "formula": '=IF({nm}="","",{dn}*{xp_day})', "fmt": "#,##0",
         "total": "=SUM({col}{r1}:{col}{r2})"},
    ]
    tracker_name = "🚀 Focus Tracker"
    wb = xlsxwriter.Workbook(str(out_path))
    styles = Styles(wb, theme)
    g_info = build_guide(wb, styles, tracker_name, [
        ("🏆 Milestones", "Hệ thống thăng hạng XP (Beginner → Master), 10 Huy hiệu thành tích tự mở khóa & biểu đồ XP!"),
    ], universal=universal)

    ws = wb.add_worksheet(tracker_name)
    cv = Canvas(wb, ws, styles, tracker_name, universal=universal)
    tr = build_tracker(wb, styles, cv, TrackerSpec(
        sheet=tracker_name, habits=habits, month="October", year=2026, seed=66,
        label_tag="FOCUS TRACKER PRO", garden_label="LAUNCH PAD",
        grown_label="ORBIT DAYS\nTHIS MONTH:",
        top_right="custom", extra_cols=extra_cols, universal=universal,
    ))
    xp_col = tr.right_cols["xp_tot"]
    total_xp_local = acell(R_TOT, xp_col)
    add_focus_rank_top_card(wb, cv, tr, total_xp_local)
    cv.flush()
    build_milestones_sheet(wb, styles, tr, f"{tr.q}!{total_xp_local}", xp_col)
    if universal:
        add_assets_placeholder(wb, styles)
    wb.close()

    r1, c1, r2, c2 = tr.hero_icon_box
    return {
        "stem": "06_Midnight_Navy_Blush_Focus", "slug": theme.slug, "tracker_sheet": tracker_name,
        "day_anims": _day_anim_manifest(tracker_name),
        "static_pics": g_info["linked_pictures"] + [
            {"sheet": tracker_name, "r1": r1, "c1": c1, "r2": r2, "c2": c2, "formula": f"={ASSETS_SHEET}!$B$7"}
        ],
        "checkboxes": {tracker_name: cv.form_checkboxes},
        "captures": [
            {"sheet": tracker_name, "range": "A1:AP38", "out": "06_navy_focus_tracker.png"},
            {"sheet": "🏆 Milestones", "range": "A1:J24", "out": "06_navy_milestones.png"},
        ],
    }


BUILDERS = [
    ("01_Sunflower_Garden_Blush", build_sunflower),
    ("02_Cactus_Bloom_Pastel_Weeks", build_cactus),
    ("03_Rainbow_Executive_Donuts", build_rainbow),
    ("04_Sage_Botanical_Habit_And_Budget", build_botanical),
    ("05_Lavender_Dream_Wellness_Mood", build_lavender),
    ("06_Midnight_Navy_Blush_Focus", build_focus),
]


def build_all_base_tier_a() -> list[dict]:
    BUILD_TMP.mkdir(parents=True, exist_ok=True)
    manifests = []
    print("Building 6 Tier-A Universal Offline base workbooks into _build_tmp/...")
    for stem, fn in BUILDERS:
        out = BUILD_TMP / f"{stem}_base.xlsx"
        meta = fn(out, universal=True)
        meta["base_path"] = str(out)
        mpath = BUILD_TMP / f"{stem}.manifest.json"
        mpath.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        manifests.append(meta)
        cb_total = sum(len(v) for v in meta["checkboxes"].values())
        print(f"  ✓ {stem}_base.xlsx  (checkboxes={cb_total}, anims={len(meta['day_anims'])}, static_pics={len(meta['static_pics'])})")
    return manifests


if __name__ == "__main__":
    build_all_base_tier_a()
