"""
excel_builder.py — Version 2.1 unified workbook builder for ALL 10 Habit Tracker templates
across ALL 3 editions:

  1. `pro_xlsm`:    Base staged in `_build_tmp/pro/` -> COM-compiled with `modHabitState.bas` +
                    Linked Pictures + Form Checkboxes into `templates/pro_macro/01..10_*_Pro.xlsm`
  2. `offline_12m`: Base staged in `_build_tmp/offline/` -> COM-compiled (12 tabs T01..T12,
                    ZERO macros, Linked Pictures + Form Checkboxes) into
                    `templates/excel_universal_offline/01..10_*.xlsx`
  3. `gsheets`:     Directly compiled (12 tabs T01..T12, dynamic `=IMAGE()` on `main`,
                    clean styled boolean grids + 1-click setup tip) into
                    `templates/google_sheets_edition/01..10_*.xlsx`
"""
from __future__ import annotations

import json
import random
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import xlsxwriter

from hx.core import Theme, Styles, Canvas, acell, colname, MONTHS_EN
from hx.guide import build_guide, GUIDE_SHEET
from hx.tracker import (Habit, TrackerSpec, TrackerRefs, build_tracker, init_calc_sheet,
                        _sample_matrix_v2, CALC_SHEET, R_IMG, R_TOT, day_col,
                        N_FORM_ROWS, N_FORM_ROWS_12M)
from hx.annual import (build_yearly_goals_v21, build_annual_achievements_sheet,
                       build_database_sheet, build_year_history_sheet,
                       YEARLY_GOALS_SHEET, ANNUAL_SHEET, ASSETS_SHEET)
from hx.addons import (add_cactus_weekly_strip, add_rainbow_bottom_blocks,
                       add_wellness_mood_block, add_focus_rank_top_card,
                       add_sakura_study_block, add_ocean_fitness_block,
                       add_matcha_routine_block, add_aurora_rpg_top_card,
                       add_dream_house_notes_block, add_wildflower_mood_row,
                       add_plum_oak_master_panels, add_alpaca_mini_panel,
                       add_royal_cat_cash_panel, add_top_habits_rank_panel,
                       add_dog_companion_panel)
from hx.daily_tasks import build_daily_tasks_sheet, DAILY_TASKS_SHEET
from hx.extras import (build_reflection_notes_sheet, build_rainbow_analytics_sheet,
                       build_monthly_budget_sheet, build_life_overview_sheet,
                       build_gratitude_sheet, build_milestones_sheet,
                       build_sakura_course_sheet, build_ocean_hall_of_fame_sheet,
                       build_matcha_weekly_review_sheet, build_aurora_character_sheet)

BUILD_TMP = ROOT / "_build_tmp"
GSHEETS_DIR = ROOT / "templates" / "google_sheets_edition"


def add_assets_placeholder(wb, styles: Styles):
    """Hidden `_Assets` sheet holding 6 uniform pure-white sprite slots `B2:B7` (`B8` = blank)."""
    t = styles.t
    ws = wb.add_worksheet(ASSETS_SHEET)
    ws.hide_gridlines(2)
    ws.set_column(0, 0, 26)
    ws.set_column(1, 1, 12.2)
    ws.set_column(2, 2, 52)
    hdr = wb.add_format({"font_name": t.font, "font_size": 10, "bold": True,
                         "bg_color": t.primary, "font_color": t.on_primary,
                         "align": "center", "valign": "vcenter"})
    lab = wb.add_format({"font_name": t.font, "font_size": 9.5, "bold": True,
                         "bg_color": t.soft, "font_color": t.ink,
                         "align": "center", "valign": "vcenter"})
    slot = wb.add_format({"bg_color": t.card})
    tip = wb.add_format({"font_name": t.font, "font_size": 9, "font_color": t.muted,
                         "bg_color": t.page, "valign": "vcenter", "text_wrap": True})

    ws.set_row(0, 26)
    ws.write(0, 0, "STAGE", hdr)
    ws.write(0, 1, "SPRITE (B2:B7)", hdr)
    ws.write(0, 2, "HƯỚNG DẪN TỰ ĐỔI ẢNH HOẠT ẢNH (v2.1)", hdr)

    stage_notes = [
        ("Stage 0 (0%)", "Chưa tick thói quen nào — Dán ảnh nền trống vào B2"),
        ("Stage 1 (1%–24%)", "Khởi động — Dán ảnh giai đoạn 1 vào B3"),
        ("Stage 2 (25%–49%)", "Đang phát triển — Dán ảnh giai đoạn 2 vào B4"),
        ("Stage 3 (50%–74%)", "Ổn định — Dán ảnh giai đoạn 3 vào B5"),
        ("Stage 4 (75%–99%)", "Sắp hoàn thành — Dán ảnh giai đoạn 4 vào B6"),
        ("Stage 5 (100% ✨)", "Hoàn hảo 100% — Dán ảnh đỉnh cao vào B7"),
        ("(Ô trống ngoài tháng)", "GIỮ NGUYÊN Ô TRẮNG B8 — dùng để ẩn ngày 29/30/31 ở tháng ngắn"),
    ]
    for i, (st, note) in enumerate(stage_notes):
        r = 1 + i
        ws.set_row(r, 68)
        ws.write(r, 0, st, lab)
        ws.write_blank(r, 1, None, slot)
        ws.write(r, 2, note, tip)
    return ws


@dataclass
class TemplateDef:
    stem: str
    short_key: str
    theme: Theme
    tracker_name: str
    habits: list[Habit]
    seed: int
    label_tag: str
    garden_label: str
    grown_label: str
    right_labels: tuple = ("GOAL", "DONE", "PROGRESS", "CURRENT\nSTREAK", "LONGEST\nSTREAK")
    top_right: str = "donut"
    extra_cols: list = field(default_factory=list)
    bonus_tab_docs: list = field(default_factory=list)
    tracker_capture_range: str = "A1:AN38"
    addon_fn: Callable | None = None
    extra_fn: Callable | None = None
    extra_captures: list = field(default_factory=list)


# ---- Template-specific addon & extra sheet callbacks ----------------------- #
def _addon_cactus(wb, cv, tr, seed):
    add_cactus_weekly_strip(wb, cv, tr)
    return None

def _addon_dream_house(wb, cv, tr, seed):
    add_dream_house_notes_block(wb, cv, tr)
    return None

def _addon_wildflower(wb, cv, tr, seed):
    add_wildflower_mood_row(wb, cv, tr, seed)
    return None

def _addon_plum_oak(wb, cv, tr, seed):
    add_plum_oak_master_panels(wb, cv, tr)
    return None

def _addon_alpaca_budget(wb, cv, tr, seed):
    add_alpaca_mini_panel(wb, cv, tr, kind="budget")
    return None

def _addon_alpaca_selfcare(wb, cv, tr, seed):
    add_alpaca_mini_panel(wb, cv, tr, kind="selfcare")
    return None

def _addon_alpaca_savings(wb, cv, tr, seed):
    add_alpaca_mini_panel(wb, cv, tr, kind="savings")
    return None

def _addon_royal_cat_cash(wb, cv, tr, seed):
    add_royal_cat_cash_panel(wb, cv, tr)
    return None

def _addon_ginger_rank(wb, cv, tr, seed):
    add_top_habits_rank_panel(wb, cv, tr, kind="ginger")
    return None

def _addon_candy_rank(wb, cv, tr, seed):
    add_top_habits_rank_panel(wb, cv, tr, kind="candy")
    return None

def _addon_shiba(wb, cv, tr, seed):
    add_dog_companion_panel(wb, cv, tr, kind="shiba")
    return None

def _addon_akita(wb, cv, tr, seed):
    add_dog_companion_panel(wb, cv, tr, kind="akita")
    return None

def _extra_cactus(wb, styles, tr, addon_ref, universal, gsheets):
    build_reflection_notes_sheet(wb, styles, tr)
    return {}

def _addon_rainbow(wb, cv, tr, seed):
    add_rainbow_bottom_blocks(wb, cv, tr)
    return None

def _extra_rainbow(wb, styles, tr, addon_ref, universal, gsheets):
    build_rainbow_analytics_sheet(wb, styles, tr)
    return {}

def _extra_botanical(wb, styles, tr, addon_ref, universal, gsheets):
    b_refs = build_monthly_budget_sheet(wb, styles, universal=universal, gsheets=gsheets)
    build_life_overview_sheet(wb, styles, tr, b_refs)
    return b_refs.get("checkboxes", {})

def _addon_lavender(wb, cv, tr, seed):
    return add_wellness_mood_block(wb, cv, tr, seed=seed)

def _extra_lavender(wb, styles, tr, addon_ref, universal, gsheets):
    gr = build_gratitude_sheet(wb, styles, tr, addon_ref, universal=universal, gsheets=gsheets)
    return gr.get("checkboxes", {})

def _addon_focus(wb, cv, tr, seed):
    xp_col = tr.right_cols["xp_tot"]
    total_xp_local = acell(R_TOT, xp_col)
    add_focus_rank_top_card(wb, cv, tr, total_xp_local)
    return {"total_xp_ref": f"{tr.q}!{total_xp_local}", "xp_col": xp_col}

def _extra_focus(wb, styles, tr, addon_ref, universal, gsheets):
    build_milestones_sheet(wb, styles, tr, addon_ref["total_xp_ref"], addon_ref["xp_col"])
    return {}

def _addon_sakura(wb, cv, tr, seed):
    return add_sakura_study_block(wb, cv, tr, seed=seed)

def _extra_sakura(wb, styles, tr, addon_ref, universal, gsheets):
    build_sakura_course_sheet(wb, styles, tr, addon_ref)
    return {}

def _addon_ocean(wb, cv, tr, seed):
    return add_ocean_fitness_block(wb, cv, tr, seed=seed)

def _extra_ocean(wb, styles, tr, addon_ref, universal, gsheets):
    build_ocean_hall_of_fame_sheet(wb, styles, tr, addon_ref)
    return {}

def _addon_matcha(wb, cv, tr, seed):
    return add_matcha_routine_block(wb, cv, tr, morning_count=5, evening_count=5, seed=seed)

def _extra_matcha(wb, styles, tr, addon_ref, universal, gsheets):
    build_matcha_weekly_review_sheet(wb, styles, tr, addon_ref)
    return {}

def _addon_aurora(wb, cv, tr, seed):
    xp_col = tr.right_cols["xp_tot"]
    skill_col = tr.right_cols["skill"]
    total_xp_local = acell(R_TOT, xp_col)
    add_aurora_rpg_top_card(wb, cv, tr, total_xp_local)
    return {"total_xp_ref": f"{tr.q}!{total_xp_local}", "skill_col": skill_col, "xp_col": xp_col}

def _extra_aurora(wb, styles, tr, addon_ref, universal, gsheets):
    build_aurora_character_sheet(wb, styles, tr, addon_ref["total_xp_ref"],
                                 addon_ref["skill_col"], addon_ref["xp_col"])
    return {}


# =========================================================================== #
#  ALL 10 TEMPLATE DEFINITIONS
# =========================================================================== #
TEMPLATES: list[TemplateDef] = [
    TemplateDef(
        stem="01_Sunflower_Garden_Blush", short_key="01_sunflower",
        theme=Theme(
            slug="sunflower", name="SUNFLOWER GARDEN BLUSH", emoji="🌻",
            tagline_vi="Gieo từng thói quen nhỏ mỗi ngày — ngắm khu vườn hướng dương nở rộ suốt cả tháng.",
            page="#FFFDFB", card="#FFFFFF", ink="#4A3B3B", muted="#968181", line="#EAD8D8",
            primary="#D8A7A7", primary_dark="#B57A7A", on_primary="#FFFFFF", soft="#F5E6E6",
            chart_fill="#E7C2C2", chart_line="#C48888",
            week_head=["#D29E9E", "#DBA9A9", "#E3B8B8", "#EBC8C8", "#F2DADA"],
            week_tint=["#F6E8E8", "#F8ECEC", "#FAF0F0", "#FBF4F4", "#FCF7F7"],
            week_check=["#C88E8E", "#CE9696", "#D4A0A0", "#DAA8A8", "#DFB2B2"],
            week_on=["#FFFFFF", "#FFFFFF", "#5B3F3F", "#5B3F3F", "#5B3F3F"],
            streak_lo="#F1FAF4", streak_mid="#9AD6B0", streak_hi="#4E9F76",
            bar="#D8A7A7", donut_rest="#F4E7E7", chart_title="DAILY PROGRESS • TIẾN ĐỘ HẰNG NGÀY",
        ),
        tracker_name="🌻 Monthly Tracker",
        habits=[
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
        ],
        seed=11, label_tag="SUNFLOWER GARDEN", garden_label="SUNFLOWER GARDEN",
        grown_label="THIS MONTH,\nYOU'VE GROWN:", tracker_capture_range="A1:AN38",
    ),
    TemplateDef(
        stem="02_Cactus_Bloom_Pastel_Weeks", short_key="02_cactus",
        theme=Theme(
            slug="cactus", name="CACTUS BLOOM PASTEL WEEKS", emoji="🌵",
            tagline_vi="5 tuần rực rỡ sắc pastel — kiên trì từng ngày để chậu xương rồng của bạn nở hoa hồng xinh xắn!",
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
        ),
        tracker_name="🌵 Monthly Tracker",
        habits=[
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
        ],
        seed=22, label_tag="MONTHLY HABIT TRACKER", garden_label="CACTUS GARDEN",
        grown_label="THIS MONTH,\nYOU HAVE GROWN:",
        right_labels=("GOAL", "DAYS\nCOMPLETE", "% DONE", "CURRENT\nSTREAK", "LONGEST\nSTREAK"),
        bonus_tab_docs=[("📝 Reflection & Notes", "Đánh giá thành tựu, thử thách, thói quen đã vào guồng & bảng check-in 5 tuần pastel.")],
        tracker_capture_range="A1:AN43", addon_fn=_addon_cactus, extra_fn=_extra_cactus,
        extra_captures=[{"sheet": "📝 Reflection & Notes", "range": "A1:I26", "out": "02_cactus_reflection.png"}],
    ),
    TemplateDef(
        stem="03_Rainbow_Executive_Donuts", short_key="03_rainbow",
        theme=Theme(
            slug="lotus_stars", name="RAINBOW EXECUTIVE DONUTS", emoji="🌈",
            tagline_vi="Dashboard đa sắc pastel với 5 biểu đồ Donut theo tuần, lọ sao phát sáng & danh sách thói quen tuần.",
            page="#F8F8FC", card="#FFFFFF", ink="#3D3C4E", muted="#8A88A0", line="#E4E2F0",
            primary="#9E9AD1", primary_dark="#6E69A8", on_primary="#FFFFFF", soft="#EFEEF9",
            chart_fill="#D7D5EE", chart_line="#8985C2",
            week_head=["#C7E5F5", "#C8EDD5", "#FAD3E4", "#FCE2B8", "#D9E8B8"],
            week_tint=["#EEF8FD", "#EFFBF3", "#FEF2F7", "#FEF7EB", "#F4F9E9"],
            week_check=["#5BA7CE", "#5CC084", "#E07AA8", "#E6A646", "#8BB34D"],
            week_on=["#2A5670", "#2A6343", "#7A3656", "#785319", "#476022"],
            streak_lo="#F0F8FC", streak_mid="#A9D7EE", streak_hi="#5B9EC4",
            bar="#B3AFE0", donut_rest="#ECEBF6", weekday_style="letter", chart_title="DAILY PROGRESS",
        ),
        tracker_name="🌈 Habit Dashboard",
        habits=[
            Habit("Uống đủ 2.5L nước mỗi ngày", goal=31, p=0.93),
            Habit("Tập luyện thể thao 30 phút", goal=22, p=0.84),
            Habit("Ngủ đủ 8 tiếng mỗi đêm", goal=30, p=0.91),
            Habit("Ăn đủ rau xanh & trái cây", goal=26, p=0.86),
            Habit("Thiền định 15 phút", goal=28, p=0.82),
            Habit("Đọc 20 trang sách", goal=24, p=0.85),
            Habit("Deep Work tập trung 2 giờ", goal=25, p=0.88),
            Habit("Đi bộ thư giãn 15 phút", goal=24, p=0.77),
            Habit("1 giờ không mạng xã hội (Tech detox)", goal=24, p=0.80),
        ],
        seed=33, label_tag="HABIT TRACKER", garden_label="STAR JAR GARDEN",
        grown_label="FULL STAR JARS\nTHIS MONTH:",
        bonus_tab_docs=[("📈 Analytics", "Bảng xếp hạng từng thói quen (Leaderboard) & phân tích hiệu suất theo Thứ trong tuần (Mon–Sun).")],
        tracker_capture_range="A1:AN54", addon_fn=_addon_rainbow, extra_fn=_extra_rainbow,
        extra_captures=[{"sheet": "📈 Analytics", "range": "A1:N32", "out": "03_rainbow_analytics.png"}],
    ),
    TemplateDef(
        stem="04_Sage_Botanical_Habit_And_Budget", short_key="04_botanical",
        theme=Theme(
            slug="botanical", name="SAGE BOTANICAL HABIT & BUDGET", emoji="🌿",
            tagline_vi="Sống xanh & quản lý tài chính tinh gọn — kết hợp thói quen lành mạnh với dòng tiền cá nhân.",
            page="#FAF9F6", card="#FFFFFF", ink="#3A4A42", muted="#82928A", line="#E3E6DF",
            primary="#9FB8AD", primary_dark="#638375", on_primary="#FFFFFF", soft="#EDF3F0",
            chart_fill="#C7D9D1", chart_line="#6E9484",
            week_head=["#9FB8AD", "#B5C9BF", "#E8D5B7", "#E0A899", "#A8BFA8"],
            week_tint=["#EFF5F2", "#F3F8F5", "#FAF5EC", "#FAF0ED", "#F1F6F1"],
            week_check=["#6C9282", "#7EA393", "#B99A6B", "#C87D6C", "#749674"],
            week_on=["#FFFFFF", "#3A4A42", "#4E4029", "#FFFFFF", "#FFFFFF"],
            streak_lo="#EFF6F2", streak_mid="#A5CBB9", streak_hi="#4E8A6E",
            bar="#9FB8AD", donut_rest="#EEF2EF", chart_title="DAILY HABIT FLOW",
        ),
        tracker_name="🌿 Daily Habits",
        habits=[
            Habit("Ghi chép thu chi cuối ngày", goal=31, p=0.95),
            Habit("Không mua sắm bốc đồng (No-spend)", goal=25, p=0.84),
            Habit("Tự nấu ăn / mang cơm đi làm", goal=24, p=0.82),
            Habit("Tiết kiệm tối thiểu 50k/ngày", goal=28, p=0.90),
            Habit("Tập thể dục / Yoga 30 phút", goal=24, p=0.83),
            Habit("Đọc sách tài chính / phát triển bản thân", goal=25, p=0.86),
            Habit("Uống đủ 2L nước & hạn chế trà sữa", goal=30, p=0.88),
            Habit("Ngủ sớm trước 23h00", goal=26, p=0.79),
            Habit("Chăm sóc cây xanh & dọn bàn gọn", goal=28, p=0.87),
        ],
        seed=44, label_tag="BOTANICAL LIVING", garden_label="MONSTERA GARDEN",
        grown_label="PLANTS FLOURISHED\nTHIS MONTH:",
        bonus_tab_docs=[
            ("💰 Monthly Budget", "Trình quản lý thu chi toàn diện (Cash Flow Donut, Budget vs Actual, Savings Goals, Bills & Transaction Log)."),
            ("🔗 Life Overview", "Dashboard tổng hợp kết nối Tỷ lệ Thói quen % + Tỷ lệ Tiết kiệm % thành điểm Cân bằng Cuộc sống!"),
        ],
        tracker_capture_range="A1:AN38", extra_fn=_extra_botanical,
        extra_captures=[
            {"sheet": "💰 Monthly Budget", "range": "A1:N46", "out": "04_botanical_budget.png"},
            {"sheet": "🔗 Life Overview", "range": "A1:J22", "out": "04_botanical_life_overview.png"},
        ],
    ),
    TemplateDef(
        stem="05_Lavender_Dream_Wellness_Mood", short_key="05_lavender",
        theme=Theme(
            slug="lavender_moon", name="LAVENDER DREAM WELLNESS & MOOD", emoji="🌙",
            tagline_vi="Chăm sóc thân – tâm – trí nhẹ nhàng với chu kỳ mặt trăng, nhật ký giấc ngủ, tâm trạng & lòng biết ơn.",
            page="#F9F7FD", card="#FFFFFF", ink="#2D2A32", muted="#8A8299", line="#E6DEF5",
            primary="#A594F9", primary_dark="#7663D9", on_primary="#FFFFFF", soft="#F3EFFB",
            chart_fill="#D7C8F5", chart_line="#8E7CE8",
            week_head=["#C8B6E2", "#B9A7EA", "#A594F9", "#C5B4EE", "#DACDF2"],
            week_tint=["#F6F2FB", "#F4F0FC", "#F1EEFE", "#F5F2FC", "#F8F5FD"],
            week_check=["#967CC4", "#8872D8", "#7663D9", "#947ED4", "#A993D8"],
            week_on=["#3B2E52", "#FFFFFF", "#FFFFFF", "#3B2E52", "#3B2E52"],
            streak_lo="#F4F0FC", streak_mid="#C2B1F2", streak_hi="#7B66DB",
            bar="#B5A4F5", donut_rest="#EFEAF9", chart_title="DAILY WELLNESS & HABIT FLOW",
        ),
        tracker_name="🌙 Habit & Wellness",
        habits=[
            Habit("Ngủ trước 23h & đủ 7.5–8 tiếng", goal=28, p=0.87),
            Habit("Thiền / hít thở chánh niệm 10 phút", goal=28, p=0.89),
            Habit("Uống đủ 2L nước & trà thảo mộc", goal=31, p=0.94),
            Habit("Vận động nhẹ / Yoga / giãn cơ", goal=24, p=0.83),
            Habit("Skincare & chăm sóc bản thân", goal=31, p=0.95),
            Habit("Đọc sách giấy 20 phút trước khi ngủ", goal=25, p=0.84),
            Habit("Viết 3 điều biết ơn mỗi tối", goal=28, p=0.90),
            Habit("Tắt điện thoại 30 phút trước khi ngủ", goal=24, p=0.76),
            Habit("Dành 15 phút ngoài trời / ánh nắng", goal=26, p=0.82),
        ],
        seed=55, label_tag="WELLNESS & MOOD", garden_label="MOON & LAVENDER",
        grown_label="FULL MOONS\nTHIS MONTH:",
        bonus_tab_docs=[("✨ Gratitude & Review", "Nhật ký 31 ngày biết ơn, khoảnh khắc đẹp, bộ đếm Self-care & tổng kết sức khỏe tinh thần.")],
        tracker_capture_range="A1:AN54", addon_fn=_addon_lavender, extra_fn=_extra_lavender,
        extra_captures=[{"sheet": "✨ Gratitude & Review", "range": "A1:I31", "out": "05_lavender_gratitude.png"}],
    ),
    TemplateDef(
        stem="06_Midnight_Navy_Blush_Focus", short_key="06_navy",
        theme=Theme(
            slug="focus_rocket", name="MIDNIGHT NAVY BLUSH FOCUS", emoji="🚀",
            tagline_vi="Phong cách tương phản Navy – Blush sắc nét dành cho Deep Work, Coding & Gym với hệ thống tích điểm XP & thăng hạng!",
            page="#F7F8FB", card="#FFFFFF", ink="#2B3452", muted="#727D9E", line="#DDE1EE",
            primary="#2B3452", primary_dark="#1D243B", on_primary="#FFFFFF", soft="#F2D7D9",
            chart_fill="#F2D7D9", chart_line="#2B3452",
            week_head=["#2B3452", "#3B476E", "#4D5B87", "#5C6B9C", "#7180B0"],
            week_tint=["#FAF1F2", "#F7F3F7", "#F2F4FA", "#F5F6FB", "#F8F3F5"],
            week_check=["#2B3452", "#3B476E", "#4D5B87", "#5C6B9C", "#C47D88"],
            week_on=["#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF"],
            streak_lo="#FAF1F2", streak_mid="#E4B7BD", streak_hi="#2B3452",
            bar="#E5A9B0", donut_rest="#EEF0F7", chart_title="DAILY FOCUS VELOCITY • TỐC ĐỘ TẬP TRUNG",
        ),
        tracker_name="🚀 Focus Tracker",
        habits=[
            Habit("Deep Work tập trung cao độ 2 giờ", goal=26, p=0.90, extra={"xp_day": 30}),
            Habit("Luyện Code / Học chuyên môn 1 giờ", goal=26, p=0.88, extra={"xp_day": 25}),
            Habit("Tập Gym / Chạy bộ 45 phút", goal=22, p=0.84, extra={"xp_day": 25}),
            Habit("Không mạng xã hội 2 giờ đầu sáng", goal=28, p=0.85, extra={"xp_day": 20}),
            Habit("Đọc sách kỹ năng / tài liệu 25 phút", goal=25, p=0.82, extra={"xp_day": 15}),
            Habit("Review mục tiêu & lập Todo ngày mai", goal=30, p=0.93, extra={"xp_day": 15}),
            Habit("Ngủ đủ 7.5 – 8 tiếng đúng giờ", goal=28, p=0.86, extra={"xp_day": 15}),
            Habit("Uống đủ 2.5L nước & ăn đủ Protein", goal=31, p=0.94, extra={"xp_day": 10}),
        ],
        seed=66, label_tag="FOCUS TRACKER PRO", garden_label="LAUNCH PAD",
        grown_label="ORBIT DAYS\nTHIS MONTH:", top_right="custom",
        extra_cols=[
            {"key": "xp_day", "label": "XP /\nDAY", "width": 6.8, "kind": "input", "fmt": "0", "blank": 15},
            {"key": "xp_tot", "label": "TOTAL\nXP", "width": 8.2, "kind": "formula",
             "formula": '=IF({nm}="","",{dn}*{xp_day})', "fmt": "#,##0", "total": "=SUM({col}{r1}:{col}{r2})"},
        ],
        bonus_tab_docs=[("🏆 Milestones", "Hệ thống thăng hạng XP (Beginner → Master), 10 Huy hiệu thành tích tự mở khóa & biểu đồ XP!")],
        tracker_capture_range="A1:AP38", addon_fn=_addon_focus, extra_fn=_extra_focus,
        extra_captures=[{"sheet": "🏆 Milestones", "range": "A1:J24", "out": "06_navy_milestones.png"}],
    ),
    TemplateDef(
        stem="07_Sakura_Zen_Study_Planner", short_key="07_sakura",
        theme=Theme(
            slug="sakura_zen", name="SAKURA ZEN STUDY PLANNER", emoji="🌸",
            tagline_vi="Phong cách Washi Nhật Bản dịu mắt — theo dõi thói quen học tập, giờ Deep Work & tiến độ khóa học / sách.",
            page="#FFFBF7", card="#FFFFFF", ink="#3D3535", muted="#958486", line="#EFE0E3",
            primary="#D47D95", primary_dark="#B35C75", on_primary="#FFFFFF", soft="#FCEBF0",
            chart_fill="#F7C5D0", chart_line="#C96F88",
            week_head=["#E69EB2", "#F0B6C6", "#F7C5D0", "#A8C69F", "#C3D9BC"],
            week_tint=["#FDF2F5", "#FEF5F7", "#FFF7F9", "#F3F8F1", "#F6FAF4"],
            week_check=["#C96F88", "#D47D95", "#DF8EA4", "#6E9B63", "#7FA874"],
            week_on=["#FFFFFF", "#59343E", "#59343E", "#FFFFFF", "#3B5235"],
            streak_lo="#F4F9F2", streak_mid="#BBD6B3", streak_hi="#6E9B63",
            bar="#F2A4B8", donut_rest="#FAECEF", chart_title="DAILY STUDY CONSISTENCY • NHỊP ĐỘ HỌC TẬP",
        ),
        tracker_name="🌸 Study & Habits",
        habits=[
            Habit("Deep Work học tập trung 2 giờ", goal=26, p=0.92),
            Habit("Ôn tập Flashcards / Anki 20 phút", goal=30, p=0.94),
            Habit("Đọc sách chuyên ngành 25 trang", goal=25, p=0.85),
            Habit("Ghi chép tóm tắt bài học (Active Recall)", goal=24, p=0.83),
            Habit("Luyện nghe / nói ngoại ngữ 30 phút", goal=28, p=0.88),
            Habit("Làm bài tập thực hành / dự án nhỏ", goal=22, p=0.80),
            Habit("Không lướt mạng xã hội trong giờ học", goal=28, p=0.86),
            Habit("Dọn bàn học gọn gàng cuối ngày", goal=30, p=0.90),
            Habit("Ngủ đủ giấc để củng cố trí nhớ", goal=28, p=0.87),
        ],
        seed=77, label_tag="SAKURA ZEN STUDY", garden_label="SAKURA BLOSSOM",
        grown_label="SAKURA BLOOMS\nTHIS MONTH:",
        bonus_tab_docs=[("📚 Course & Reading", "Theo dõi tiến độ sách đang đọc & khóa học Online với thanh Data Bar Sakura & biểu đồ Donut.")],
        tracker_capture_range="A1:AN52", addon_fn=_addon_sakura, extra_fn=_extra_sakura,
        extra_captures=[{"sheet": "📚 Course & Reading", "range": "A1:J22", "out": "07_sakura_courses.png"}],
    ),
    TemplateDef(
        stem="08_Ocean_Coral_Fitness_Energy", short_key="08_ocean",
        theme=Theme(
            slug="ocean_coral", name="OCEAN CORAL FITNESS & ENERGY", emoji="🪸",
            tagline_vi="Sức sống đại dương — theo dõi tập luyện, dinh dưỡng, lượng nước, mức năng lượng & bảng vinh danh Streak!",
            page="#F5FBFB", card="#FFFFFF", ink="#1E3A40", muted="#6E8F94", line="#D5ECEA",
            primary="#2E7D87", primary_dark="#1E5B63", on_primary="#FFFFFF", soft="#D4F1EC",
            chart_fill="#9CDFD6", chart_line="#2E7D87",
            week_head=["#2E7D87", "#48A9A6", "#F4A582", "#5BC0BE", "#E89372"],
            week_tint=["#EAF7F6", "#EDF9F8", "#FEF3EE", "#EEFAF9", "#FDF1EC"],
            week_check=["#2E7D87", "#3A9491", "#D97C56", "#42A3A1", "#D4724E"],
            week_on=["#FFFFFF", "#FFFFFF", "#5C2C1B", "#FFFFFF", "#FFFFFF"],
            streak_lo="#EAF7F6", streak_mid="#8FD8CC", streak_hi="#2E7D87",
            bar="#F4A582", donut_rest="#E4F4F2", weekday_style="letter", chart_markers=True,
            chart_title="DAILY FITNESS & ENERGY FLOW • PHONG ĐỘ THỂ CHẤT",
        ),
        tracker_name="🪸 Fitness & Energy",
        habits=[
            Habit("Tập Gym / Cardio / Chạy bộ 45 phút", goal=24, p=0.88),
            Habit("Đạt mục tiêu 8,000 – 10,000 bước chân", goal=28, p=0.91),
            Habit("Uống đủ 2.5L nước lọc & điện giải", goal=31, p=0.95),
            Habit("Ăn đủ Protein & rau xanh mỗi bữa", goal=28, p=0.87),
            Habit("Giãn cơ / Mobility 15 phút sau tập", goal=24, p=0.82),
            Habit("Không đường tinh luyện & nước ngọt", goal=25, p=0.80),
            Habit("Ngủ phục hồi đủ 7.5 – 8 tiếng", goal=28, p=0.86),
            Habit("Tắm nắng / hít thở không khí buổi sáng", goal=26, p=0.84),
            Habit("Theo dõi cân nặng / năng lượng cơ thể", goal=30, p=0.92),
        ],
        seed=88, label_tag="OCEAN FITNESS PRO", garden_label="CORAL REEF",
        grown_label="PEARL REEF DAYS\nTHIS MONTH:",
        bonus_tab_docs=[("🏅 Streak Hall of Fame", "Bảng vinh danh kỷ lục Streak với Huy chương Vàng / Bạc / Đồng & biểu đồ so sánh.")],
        tracker_capture_range="A1:AN49", addon_fn=_addon_ocean, extra_fn=_extra_ocean,
        extra_captures=[{"sheet": "🏅 Streak Hall of Fame", "range": "A1:K29", "out": "08_ocean_hall_of_fame.png"}],
    ),
    TemplateDef(
        stem="09_Matcha_Cafe_Daily_Routine", short_key="09_matcha",
        theme=Theme(
            slug="matcha_cafe", name="MATCHA CAFE DAILY ROUTINE", emoji="🍵",
            tagline_vi="Nhâm nhi nhịp sống chậm rãi — tách biệt rõ Thói quen Sáng & Tối cùng góc ghi chú ấm áp phong cách Cafe.",
            page="#F6F1E7", card="#FFFFFF", ink="#4A352A", muted="#8F7A6E", line="#E6DAC9",
            primary="#8FA97B", primary_dark="#647E52", on_primary="#FFFFFF", soft="#EDF2E8",
            chart_fill="#C9D9BA", chart_line="#6D8A5A",
            week_head=["#8FA97B", "#A5BC93", "#D4A373", "#8FA97B", "#B88D63"],
            week_tint=["#F1F5EC", "#F4F8F0", "#FAF3EA", "#F1F5EC", "#F8F1E8"],
            week_check=["#6C8959", "#7E9A6B", "#B88652", "#6C8959", "#8E623C"],
            week_on=["#FFFFFF", "#3A4A30", "#FFFFFF", "#FFFFFF", "#FFFFFF"],
            streak_lo="#F1F6EC", streak_mid="#B5CCA3", streak_hi="#5F7E4C",
            bar="#8FA97B", donut_rest="#EFECE4", chart_title="DAILY ROUTINE HARMONY • NHỊP SỐNG SÁNG & TỐI",
        ),
        tracker_name="🍵 Daily Routine",
        habits=[
            Habit("☀️ [Sáng] Dậy đúng giờ & gấp chăn gọn", goal=30, p=0.93),
            Habit("☀️ [Sáng] Uống 1 ly nước ấm / pha trà", goal=31, p=0.95),
            Habit("☀️ [Sáng] Giãn cơ / đi bộ đón nắng 15p", goal=25, p=0.84),
            Habit("☀️ [Sáng] Ăn sáng lành mạnh & đủ chất", goal=28, p=0.88),
            Habit("☀️ [Sáng] Viết 3 việc quan trọng nhất ngày", goal=30, p=0.90),
            Habit("🌙 [Tối] Dọn bàn làm việc & chuẩn bị đồ", goal=28, p=0.87),
            Habit("🌙 [Tối] Skincare & thư giãn cơ thể", goal=31, p=0.94),
            Habit("🌙 [Tối] Tắt điện thoại 30p trước giờ ngủ", goal=24, p=0.77),
            Habit("🌙 [Tối] Đọc sách giấy 20 phút đèn vàng", goal=26, p=0.85),
            Habit("🌙 [Tối] Viết nhật ký & ngủ trước 23h", goal=26, p=0.82),
        ],
        seed=99, label_tag="MATCHA CAFE ROUTINE", garden_label="MATCHA BREW",
        grown_label="MATCHA CUPS\nBREWED:",
        bonus_tab_docs=[("☕ Cozy Weekly Review", "So sánh tỷ lệ Thói quen Sáng vs Tối & sổ ghi chép Cozy Reflection 5 tuần.")],
        tracker_capture_range="A1:AN48", addon_fn=_addon_matcha, extra_fn=_extra_matcha,
        extra_captures=[{"sheet": "☕ Cozy Weekly Review", "range": "A1:F24", "out": "09_matcha_cozy_review.png"}],
    ),
    TemplateDef(
        stem="10_Aurora_Glow_RPG_Quest_Tracker", short_key="10_aurora",
        theme=Theme(
            slug="aurora_rpg", name="AURORA GLOW RPG QUEST TRACKER", emoji="🌌",
            tagline_vi="Biến cuộc sống thành tựa game nhập vai — mỗi thói quen cộng XP, chuỗi ngày nhân Combo x1.2 / x1.5 & nâng cấp chỉ số!",
            page="#F0F4F8", card="#FFFFFF", ink="#242B3D", muted="#6B7894", line="#D8E0EC",
            primary="#242B3D", primary_dark="#161B28", on_primary="#FFFFFF", soft="#E6FFFA",
            chart_fill="#9F7AEA", chart_line="#4FD1C5",
            week_head=["#242B3D", "#2E3B55", "#433878", "#2B5B66", "#5B3FA8"],
            week_tint=["#EEF6FA", "#EFF7F8", "#F4F0FD", "#EBFBF9", "#F5F0FE"],
            week_check=["#242B3D", "#2E7D87", "#7C5BD6", "#2B9E96", "#6D46C9"],
            week_on=["#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF"],
            streak_lo="#E6FFFA", streak_mid="#81E6D9", streak_hi="#2C7A7B",
            bar="#4FD1C5", donut_rest="#E8EDF5", chart_title="DAILY QUEST VELOCITY • TỐC ĐỘ CÀY XP",
        ),
        tracker_name="🌌 RPG Quest Tracker",
        habits=[
            Habit("Tập luyện thể lực / Gym 45 phút", goal=24, p=0.87, extra={"skill": "Health", "xp_day": 30}),
            Habit("Ngủ đủ 8 tiếng & Uống 2.5L nước", goal=30, p=0.93, extra={"skill": "Health", "xp_day": 20}),
            Habit("Đọc sách / Học kỹ năng mới 30 phút", goal=26, p=0.86, extra={"skill": "Mind", "xp_day": 25}),
            Habit("Thiền / Viết nhật ký chiến lược", goal=26, p=0.84, extra={"skill": "Mind", "xp_day": 20}),
            Habit("Deep Work dự án trọng tâm 2 giờ", goal=26, p=0.91, extra={"skill": "Career", "xp_day": 35}),
            Habit("Luyện chuyên môn / Networking 1 giờ", goal=22, p=0.82, extra={"skill": "Career", "xp_day": 25}),
            Habit("Ghi chép thu chi & Không tiêu hoang", goal=30, p=0.94, extra={"skill": "Finance", "xp_day": 20}),
            Habit("Tiết kiệm / Nghiên cứu đầu tư", goal=25, p=0.85, extra={"skill": "Finance", "xp_day": 25}),
        ],
        seed=101, label_tag="AURORA RPG QUEST", garden_label="AURORA CRYSTAL",
        grown_label="AURORA NIGHTS\nTHIS MONTH:", top_right="custom",
        extra_cols=[
            {"key": "skill", "label": "SKILL\nCLASS", "width": 8.4, "kind": "input", "fmt": "@", "blank": "Mind"},
            {"key": "xp_day", "label": "BASE\nXP", "width": 6.4, "kind": "input", "fmt": "0", "blank": 20},
            {"key": "combo", "label": "COMBO\nMULT", "width": 6.8, "kind": "formula",
             "formula": '=IF({nm}="","",IF({long}>=14,1.5,IF({long}>=7,1.2,1)))', "fmt": '0.0"x"'},
            {"key": "xp_tot", "label": "TOTAL\nXP", "width": 8.5, "kind": "formula",
             "formula": '=IF({nm}="","",ROUND({dn}*{xp_day}*{combo},0))', "fmt": "#,##0",
             "total": "=SUM({col}{r1}:{col}{r2})"},
        ],
        bonus_tab_docs=[("⚔️ Character Sheet", "Hồ sơ nhân vật RPG: Level, Rank Class, biểu đồ 4 nhánh kỹ năng (Health/Mind/Career/Finance) & 10 Quests!")],
        tracker_capture_range="A1:AR38", addon_fn=_addon_aurora, extra_fn=_extra_aurora,
        extra_captures=[{"sheet": "⚔️ Character Sheet", "range": "A1:J24", "out": "10_aurora_character_sheet.png"}],
    ),
    # ----------------------------------------------------------------------- #
    #  BATCH 2 — TEMPLATES 11..19 (v2.4 EXPANSION)
    # ----------------------------------------------------------------------- #
    TemplateDef(
        stem="11_Velvet_Rose_Garden", short_key="11_velvet_rose",
        theme=Theme(
            slug="velvet_rose", name="VELVET ROSE GARDEN", emoji="🌹",
            tagline_vi="Trồng một đóa hồng nhung mỗi ngày khi đạt mục tiêu — sắc tím lavender dịu mắt & dấu tick hồng berry đầy cảm hứng!",
            page="#F7F2FF", card="#FFFFFF", ink="#3B1D5E", muted="#7E6B98", line="#E3D7F5",
            primary="#5B21B6", primary_dark="#4C1D95", on_primary="#FFFFFF", soft="#EDE9FE",
            chart_fill="#DDD6FE", chart_line="#C84B93",
            week_head=["#5B21B6", "#6D28D9", "#7C3AED", "#8B5CF6", "#A78BFA"],
            week_tint=["#F5F0FF", "#F3EDFF", "#F6F0FF", "#F5F3FF", "#FAF5FF"],
            week_check=["#C84B93", "#C84B93", "#BE3E87", "#C84B93", "#A83279"],
            week_on=["#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF"],
            streak_lo="#FDF2F8", streak_mid="#F9A8D4", streak_hi="#C84B93",
            bar="#C84B93", donut_rest="#EDE9FE", chart_title="DAILY PROGRESS • TIẾN ĐỘ TRỒNG HỒNG NHUNG",
        ),
        tracker_name="🌹 Velvet Rose Tracker",
        habits=[
            Habit("Thức dậy sớm trước 6h30 & dọn giường", goal=28, p=0.90),
            Habit("Uống đủ 2L nước lọc mỗi ngày", goal=30, p=0.93),
            Habit("Tập thể dục / Yoga 30 phút buổi sáng", goal=24, p=0.84),
            Habit("Đọc sách 20 trang phát triển bản thân", goal=26, p=0.86),
            Habit("Không dùng mạng xã hội 1 giờ đầu ngày", goal=26, p=0.81),
            Habit("Ăn rau xanh & thực phẩm lành mạnh", goal=28, p=0.88),
            Habit("Viết 3 điều biết ơn & suy ngẫm tối", goal=26, p=0.85),
            Habit("Chăm sóc da & ngủ đủ 8 tiếng trước 23h", goal=28, p=0.87),
        ],
        seed=111, label_tag="PLANT A VELVET ROSE", garden_label="VELVET ROSE GARDEN",
        grown_label="VELVET ROSES\nBLOOMED:", tracker_capture_range="A1:AN38",
    ),
    TemplateDef(
        stem="12_Blue_Tulip_Mint_Breeze", short_key="12_blue_tulip",
        theme=Theme(
            slug="blue_tulip", name="BLUE TULIP MINT BREEZE", emoji="🌷",
            tagline_vi="Dải màu chuyển mượt Mint → Chanh nhạt thanh mát cùng hoa Tulip xanh lam tối giản, nhẹ nhàng & thư thái!",
            page="#F4FBF8", card="#FFFFFF", ink="#1E3A3A", muted="#6A8985", line="#D9EFE7",
            primary="#2CA58D", primary_dark="#1E7B68", on_primary="#FFFFFF", soft="#E6F7F2",
            chart_fill="#9EE0D2", chart_line="#2CA58D", chart_kind="line", chart_markers=True,
            week_head=["#9EE0D2", "#A8E6B8", "#C8EE9F", "#EDF5A3", "#FAF6C8"],
            week_tint=["#EEFBF8", "#F0FBF3", "#F5FCEB", "#FCFEEF", "#FEFEF5"],
            week_check=["#1D8A76", "#239B56", "#5D9E24", "#A69B12", "#B58900"],
            week_on=["#134E4A", "#14532D", "#365314", "#422006", "#422006"],
            streak_lo="#FEF9C3", streak_mid="#FDE68A", streak_hi="#0891B2",
            bar="#2CA58D", donut_rest="#E6F7F2", weekday_style="letter",
            chart_title="DAILY PRODUCTIVITY • HIỆU SUẤT MỖI NGÀY",
        ),
        tracker_name="🌷 Blue Tulip Tracker",
        habits=[
            Habit("Thiền tĩnh tâm 10 phút buổi sáng", goal=28, p=0.88),
            Habit("Tập vận động nhẹ / Đi bộ 30 phút", goal=26, p=0.85),
            Habit("Đọc sách 20 phút không xao nhãng", goal=26, p=0.84),
            Habit("Uống 2.5L nước lọc & trà thảo mộc", goal=30, p=0.92),
            Habit("Ăn sáng lành mạnh đầy đủ dinh dưỡng", goal=28, p=0.87),
            Habit("Hoàn thành 3 việc quan trọng nhất ngày", goal=28, p=0.90),
            Habit("Chăm sóc bản thân & thư giãn mắt", goal=26, p=0.82),
            Habit("Ngủ trước 23h00 & không điện thoại", goal=26, p=0.83),
        ],
        seed=122, label_tag="BLUE TULIP BREEZE", garden_label="BLUE TULIP GARDEN",
        grown_label="BLUE TULIPS\nYOU'VE PLANTED:", tracker_capture_range="A1:AN38",
    ),
    TemplateDef(
        stem="13_Buttercream_Blossom_Bars", short_key="13_buttercream_blossom",
        theme=Theme(
            slug="blossom_star", name="BUTTERCREAM BLOSSOM BARS", emoji="🌸",
            tagline_vi="Phong cách kem bơ ấm áp với biểu đồ cột Caramel nổi bật, biểu đồ tròn Mint/Hồng & huy hiệu sao vàng YOU HAVE GOT ⭐!",
            page="#FFFBEB", card="#FFFFFF", ink="#4A3728", muted="#9A7E65", line="#EFE1C6",
            primary="#C8A27A", primary_dark="#9A7148", on_primary="#FFFFFF", soft="#FEF3C7",
            chart_fill="#E7CBA9", chart_line="#C8A27A", chart_kind="column",
            week_head=["#99E6C9", "#93E2EC", "#F7A899", "#F9C6D0", "#D8F3DC"],
            week_tint=["#F0FDF8", "#F0FBFE", "#FFF4F2", "#FFF5F8", "#F4FCF6"],
            week_check=["#C8A27A", "#B5895A", "#D97757", "#C86B85", "#8B6F4E"],
            week_on=["#1B4332", "#164E63", "#6B271D", "#6B213A", "#1B4332"],
            streak_lo="#FFFBEB", streak_mid="#FDE68A", streak_hi="#D97706",
            bar="#C8A27A", donut_rest="#F9C6D0",
            hero_header_bg="#F59E0B", hero_header_fg="#FFFFFF",
            chart_title="DAILY PRODUCTIVITY CHART • BIỂU ĐỒ CỘT NĂNG SUẤT",
        ),
        tracker_name="🌸 Blossom Bars Tracker",
        habits=[
            Habit("Dậy sớm đón nắng & uống 1 ly nước ấm", goal=28, p=0.90),
            Habit("Đi bộ ngoài trời / hít thở khí trời 20p", goal=25, p=0.84),
            Habit("Ăn nhiều rau xanh & trái cây tươi", goal=28, p=0.87),
            Habit("Thiền định / hít thở sâu 15 phút", goal=26, p=0.83),
            Habit("Đọc sách giấy ít nhất 20 phút", goal=26, p=0.85),
            Habit("Viết nhật ký & tổng kết mục tiêu ngày", goal=28, p=0.88),
            Habit("Hạn chế đồ ngọt & trà sữa", goal=24, p=0.79),
            Habit("Đi bộ đạt mục tiêu 8.000–10.000 bước", goal=25, p=0.82),
        ],
        seed=133, label_tag="ULTIMATE BUTTERCREAM", garden_label="BLOSSOM GARDEN",
        grown_label="⭐  YOU HAVE GOT\nBLOOMING DAYS:", tracker_capture_range="A1:AN38",
    ),
    TemplateDef(
        stem="14_Emerald_Forest_Gold_Stars", short_key="14_emerald_forest",
        theme=Theme(
            slug="forest_tree", name="EMERALD FOREST GOLD STARS", emoji="🌳",
            tagline_vi="Gieo mầm rừng xanh Ngọc Bích — mỗi thói quen hoàn thành tỏa sáng sắc vàng Sao Kim lấp lánh trên nền Mint tươi mát!",
            page="#F7FEFA", card="#FFFFFF", ink="#134E4A", muted="#648B82", line="#D5F2E5",
            primary="#10B981", primary_dark="#047857", on_primary="#FFFFFF", soft="#ECFDF5",
            chart_fill="#A7F3D0", chart_line="#10B981", chart_kind="line", chart_markers=True,
            week_head=["#86D9B8", "#9BE3A8", "#BCEB9D", "#DCF29E", "#F4F7B2"],
            week_tint=["#EEFCF6", "#F1FCF3", "#F6FDEF", "#FBFEF1", "#FEFEF4"],
            week_check=["#D97706", "#D97706", "#D97706", "#D97706", "#D97706"],
            week_on=["#064E3B", "#14532D", "#365314", "#3F6212", "#422006"],
            check_fill_override="#FEF3C7",
            streak_lo="#FEF9C3", streak_mid="#FDE68A", streak_hi="#0284C7",
            bar="#34D399", donut_rest="#D1FAE5",
            chart_title="DAILY PRODUCTIVITY • TRỒNG RỪNG SAO VÀNG",
        ),
        tracker_name="🌳 Forest Stars Tracker",
        habits=[
            Habit("Thiền định & tĩnh tâm 15 phút", goal=28, p=0.89),
            Habit("Tập thể dục buổi sáng 30 phút", goal=25, p=0.86),
            Habit("Đọc sách / Học kiến thức mới 25 phút", goal=26, p=0.85),
            Habit("Uống đủ 2.5L nước lọc mỗi ngày", goal=30, p=0.93),
            Habit("Deep Work tập trung 2 giờ", goal=26, p=0.88),
            Habit("Ăn lành mạnh, hạn chế đồ chế biến", goal=26, p=0.84),
            Habit("Ghi lại 1 bài học hoặc thành tựu nhỏ", goal=28, p=0.87),
            Habit("Đi ngủ đúng giờ trước 23h00", goal=28, p=0.85),
        ],
        seed=144, label_tag="PLANT FOREST TREES", garden_label="EMERALD FOREST",
        grown_label="🌳  TREES YOU'VE\nPLANTED:", tracker_capture_range="A1:AN38",
    ),
    TemplateDef(
        stem="15_Mocha_Rose_Terracotta_Sunflower", short_key="15_mocha_sunflower",
        theme=Theme(
            slug="mocha_sunflower", name="MOCHA ROSE TERRACOTTA SUNFLOWER", emoji="🌻",
            tagline_vi="Tông nâu Mocha Espresso phối Hồng đất Terracotta sang trọng, thanh % Đèn giao thông (Xanh/Vàng/Đỏ) & Hướng dương mọc từ đất!",
            page="#FAF6F3", card="#FFFFFF", ink="#2D1F1D", muted="#856A64", line="#E6D7D1",
            primary="#8C6258", primary_dark="#5C3D36", on_primary="#FFFFFF", soft="#F3E7E3",
            chart_fill="#DFB9B6", chart_line="#8C6258", pct_traffic_light=True,
            week_head=["#8C6258", "#A67668", "#B98B7C", "#C99A96", "#D6B2AD"],
            week_tint=["#F8F1EE", "#FAF3F0", "#FAF4F2", "#FBF5F4", "#FCF7F6"],
            week_check=["#2D1F1D", "#3F2A26", "#5C3D36", "#734B43", "#8C6258"],
            week_on=["#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#2D1F1D"],
            streak_lo="#FAF6F3", streak_mid="#D8B4A8", streak_hi="#8C6258",
            bar="#C99A96", donut_rest="#EFE3DF",
            chart_title="DAILY COMPLETION CURVE • ĐƯỜNG CONG KỶ LUẬT",
        ),
        tracker_name="🌻 Mocha Sunflower",
        habits=[
            Habit("Thức dậy 6h30–7h00 & gấp gọn chăn gối", goal=30, p=0.92),
            Habit("Không chạm điện thoại 1 giờ đầu sáng", goal=26, p=0.82),
            Habit("Dưỡng ẩm & thoa kem chống nắng", goal=30, p=0.94),
            Habit("Tập Gym / Cardio 40 phút", goal=24, p=0.84),
            Habit("Đọc tối thiểu 10–15 trang sách", goal=28, p=0.88),
            Habit("Uống đủ 2L nước lọc tinh khiết", goal=30, p=0.91),
            Habit("Thiền định & hít thở chánh niệm 10 phút", goal=26, p=0.85),
            Habit("Viết nhật ký & danh sách biết ơn", goal=28, p=0.87),
            Habit("Dọn gọn nhà cửa 10 phút trước khi ngủ", goal=28, p=0.89),
            Habit("Tắt đèn đi ngủ trước 23h00", goal=28, p=0.86),
        ],
        seed=155, label_tag="MOCHA TERRACOTTA", garden_label="SUNFLOWER FIELD",
        grown_label="🌻  SUNFLOWERS\nHARVESTED:", tracker_capture_range="A1:AN38",
    ),
    TemplateDef(
        stem="16_Dream_Home_Architect_Builder", short_key="16_dream_house",
        theme=Theme(
            slug="dream_house", name="DREAM HOME ARCHITECT BUILDER", emoji="🏡",
            tagline_vi="Xây ngôi nhà mơ ước qua từng ngày kỷ luật: Lửa trại → Lều → Nhà gỗ → Cottage → Nhà 2 tầng → Biệt thự Hiện đại + Sổ Thành Công & Bài Học!",
            page="#F4F6F8", card="#FFFFFF", ink="#1E293B", muted="#64748B", line="#DCE3EC",
            primary="#3B4C59", primary_dark="#1E293B", on_primary="#FFFFFF", soft="#ECFDF5",
            chart_fill="#6EE7B7", chart_line="#0D9468", chart_kind="column",
            week_head=["#3B4C59", "#334155", "#2F4858", "#3B596A", "#475569"],
            week_tint=["#F1F5F9", "#F0FDF9", "#F1F5F9", "#F0FDF9", "#F8FAFC"],
            week_check=["#0D9468", "#0D9468", "#059669", "#0D9468", "#047857"],
            week_on=["#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF"],
            streak_lo="#ECFDF5", streak_mid="#6EE7B7", streak_hi="#0D9468",
            bar="#0D9468", donut_rest="#E2E8F0",
            hero_header_bg="#F5B800", hero_header_fg="#1E293B",
            chart_title="DAILY BUILD PROGRESS • TIẾN ĐỘ XÂY DỰNG MỖI NGÀY",
        ),
        tracker_name="🏡 Dream Home Builder",
        habits=[
            Habit("Thiền định & hoạch định mục tiêu sáng", goal=28, p=0.89),
            Habit("Tập thể dục rèn thể lực 35 phút", goal=25, p=0.86),
            Habit("Uống đủ 2.5L nước lọc mỗi ngày", goal=30, p=0.93),
            Habit("Hạn chế đồ ăn nhanh & nước có ga", goal=26, p=0.82),
            Habit("Gọi điện / ăn tối cùng gia đình", goal=26, p=0.87),
            Habit("Ghi chép hóa đơn & ngân sách ngày", goal=30, p=0.92),
            Habit("Deep Work sự nghiệp 2 giờ", goal=26, p=0.88),
            Habit("Đọc sách / Học kỹ năng mới 20 phút", goal=26, p=0.85),
        ],
        seed=166, label_tag="BUILD A DREAM HOME", garden_label="ARCHITECTURE STAGE",
        grown_label="🏡  HOMES BUILT\nTHIS MONTH:",
        tracker_capture_range="A1:AN45", addon_fn=_addon_dream_house,
    ),
    TemplateDef(
        stem="17_Wildflower_Bloom_Daily_Mood", short_key="17_wildflower_mood",
        theme=Theme(
            slug="wildflower_mood", name="WILDFLOWER BLOOM & DAILY MOOD", emoji="🌺",
            tagline_vi="Khu vườn hoa dại 5 cánh hồng rực rỡ kết hợp thanh ghi nhận Tâm Trạng hàng ngày (😊 / 😐 / 😢) & thống kê cảm xúc tự động!",
            page="#F6F8FE", card="#FFFFFF", ink="#2E3A59", muted="#718096", line="#DCE4F5",
            primary="#5C7CFA", primary_dark="#3B5BDB", on_primary="#FFFFFF", soft="#E8EEFF",
            chart_fill="#C9DAF8", chart_line="#C94C64",
            week_head=["#F4CCCC", "#D9EAD3", "#C9DAF8", "#FFF2CC", "#EAD1DC"],
            week_tint=["#FFF5F5", "#F4FAF1", "#F2F6FE", "#FFFDF2", "#FBF4F8"],
            week_check=["#C94C64", "#388E3C", "#3B5BDB", "#D97706", "#9D2C47"],
            week_on=["#7F1D1D", "#1B5E20", "#1E3A8A", "#78350F", "#701A3E"],
            streak_lo="#F4FAF1", streak_mid="#A5D6A7", streak_hi="#4CAF50",
            bar="#C94C64", donut_rest="#E8EEFF",
            chart_title="DAILY WILDFLOWER GROWTH • TIẾN ĐỘ NỞ HOA",
        ),
        tracker_name="🌺 Wildflower & Mood",
        habits=[
            Habit("Viết 3 ưu tiên quan trọng nhất hôm nay", goal=28, p=0.91),
            Habit("Không uống cà phê sau 14h00", goal=26, p=0.83),
            Habit("Không dùng điện thoại 30p sau dậy", goal=26, p=0.82),
            Habit("Uống đủ 8 cốc nước lọc mỗi ngày", goal=30, p=0.92),
            Habit("Giãn cơ / Yoga tối thiểu 10 phút", goal=28, p=0.87),
            Habit("Ngủ đủ 8 tiếng phục hồi năng lượng", goal=28, p=0.88),
            Habit("Tiết kiệm tối thiểu 100k / ghi chi tiêu", goal=28, p=0.89),
            Habit("Thiền 15–30 phút cân bằng cảm xúc", goal=25, p=0.84),
            Habit("Viết nhật ký cảm xúc cuối ngày", goal=26, p=0.86),
        ],
        seed=177, label_tag="WILDFLOWER & MOOD", garden_label="WILDFLOWER MEADOW",
        grown_label="🌺  WILDFLOWERS\nBLOOMED:",
        tracker_capture_range="A1:AN42", addon_fn=_addon_wildflower,
    ),
    TemplateDef(
        stem="18_Plum_Oak_Master_Suite", short_key="18_plum_oak",
        theme=Theme(
            slug="plum_oak", name="PLUM OAK MASTER SUITE", emoji="🌳",
            tagline_vi="Bộ quản trị thói quen toàn diện tông Tím Mận Hoàng Gia & 5 tuần Cầu Vồng Pastel + cây Sồi ra hoa đỏ & bảng Thói quen Tuần/Tháng/Ghi chú!",
            page="#FAF7FA", card="#FFFFFF", ink="#3A1D36", muted="#85657F", line="#E6D8E4",
            primary="#4A2545", primary_dark="#33172F", on_primary="#FFFFFF", soft="#F3E8F1",
            chart_fill="#DFC5F2", chart_line="#A66E8A",
            week_head=["#B8D4F5", "#C9E4C5", "#F4B6B6", "#F8D5A8", "#DFC5F2"],
            week_tint=["#F2F7FD", "#F4FAF3", "#FDF4F4", "#FEF8F0", "#F8F3FC"],
            week_check=["#2563EB", "#2E7D32", "#C62828", "#D97706", "#7E22CE"],
            week_on=["#1E3A5F", "#1B4332", "#7F1D1D", "#78350F", "#4A2545"],
            streak_lo="#FAF5FA", streak_mid="#D4A6C1", streak_hi="#4A2545",
            bar="#A66E8A", donut_rest="#EFE5ED",
            chart_title="DAILY OAK GROWTH • TIẾN ĐỘ CÂY SỒI MỖI NGÀY",
        ),
        tracker_name="🌳 Plum Oak Suite",
        habits=[
            Habit("Thức dậy 6h30 & mở cửa đón ánh sáng", goal=28, p=0.90),
            Habit("Đi bộ / Tập thể dục 30 phút", goal=25, p=0.86),
            Habit("Yoga giãn cơ 20 phút buổi sáng", goal=24, p=0.83),
            Habit("Uống đủ nước & bổ sung vitamin", goal=30, p=0.93),
            Habit("Chăm sóc da sáng & tối đều đặn", goal=28, p=0.89),
            Habit("Luyện kỹ năng / Ngoại ngữ 30 phút", goal=26, p=0.85),
            Habit("Viết nhật ký sáng (Morning Journal)", goal=26, p=0.84),
            Habit("Đọc sách 20 trang trước khi ngủ", goal=26, p=0.86),
            Habit("Chuẩn bị đồ & kế hoạch ngày mai", goal=28, p=0.88),
        ],
        seed=188, label_tag="PLUM OAK MASTER SUITE", garden_label="ROYAL OAK GROVE",
        grown_label="🌳  OAK TREES\nGROWN:",
        tracker_capture_range="A1:AN47", addon_fn=_addon_plum_oak,
    ),
    TemplateDef(
        stem="19_Meadow_Emerald_Sunflower", short_key="19_meadow_sunflower",
        theme=Theme(
            slug="meadow_sunflower", name="MEADOW EMERALD SUNFLOWER", emoji="🌻",
            tagline_vi="Thiết kế xanh lá mạ & ngọc lục bảo tươi mới, tối giản, dễ đọc tuyệt đối — gieo hoa Hướng dương đồng cỏ căng tràn năng lượng!",
            page="#F4FDF4", card="#FFFFFF", ink="#14532D", muted="#5B866B", line="#D2F0D8",
            primary="#16A34A", primary_dark="#15803D", on_primary="#FFFFFF", soft="#DCFCE7",
            chart_fill="#BBF7D0", chart_line="#16A34A",
            week_head=["#16A34A", "#22C55E", "#15803D", "#16A34A", "#4ADE80"],
            week_tint=["#F0FDF4", "#F2FEF6", "#ECFDF3", "#F0FDF4", "#F5FEF7"],
            week_check=["#16A34A", "#16A34A", "#15803D", "#16A34A", "#15803D"],
            week_on=["#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#14532D"],
            streak_lo="#F0FDF4", streak_mid="#86EFAC", streak_hi="#15803D",
            bar="#16A34A", donut_rest="#DCFCE7",
            chart_title="DAILY SUNFLOWER PROGRESS • NĂNG LƯỢNG ĐỒNG CỎ",
        ),
        tracker_name="🌻 Meadow Sunflower",
        habits=[
            Habit("Dậy sớm & uống 500ml nước ấm chanh", goal=30, p=0.92),
            Habit("Vận động / Chạy bộ ngoài trời 30 phút", goal=25, p=0.86),
            Habit("Ăn rau xanh & bữa ăn tươi lành mạnh", goal=28, p=0.89),
            Habit("Đọc sách 20 phút mở rộng tư duy", goal=26, p=0.85),
            Habit("Deep Work không mạng xã hội", goal=26, p=0.88),
            Habit("Tiết kiệm & ghi chép chi tiêu hằng ngày", goal=30, p=0.91),
            Habit("Dọn gọn không gian sống 10 phút", goal=28, p=0.87),
            Habit("Viết nhật ký biết ơn & ngủ đủ 8 tiếng", goal=28, p=0.88),
        ],
        seed=199, label_tag="MEADOW SUNFLOWER", garden_label="MEADOW SUNFLOWER",
        grown_label="🌻  SUNFLOWERS\nBLOOMED:", tracker_capture_range="A1:AN38",
    ),
    # ----------------------------------------------------------------------- #
    #  BATCH 3 — TEMPLATES 20..31 (v3.0 MEGA EXPANSION!)
    # ----------------------------------------------------------------------- #
    TemplateDef(
        stem="20_Cream_Alpaca_Cozy_Budget", short_key="20_alpaca_cream",
        theme=Theme(
            slug="alpaca_cream", name="CREAM ALPACA COZY BUDGET", emoji="🦙",
            tagline_vi="Chú Alpaca kem bông mềm ấm áp kết hợp bảng Ngân Sách & Tiết Kiệm tháng gọn gàng — rèn thói quen & quản lý ví tiền!",
            page="#FAF6F0", card="#FFFFFF", ink="#3E2C23", muted="#8C7362", line="#E6D8C8",
            primary="#A67C52", primary_dark="#7A5635", on_primary="#FFFFFF", soft="#F3E9DC",
            chart_fill="#DFC7AE", chart_line="#A67C52",
            week_head=["#C8A98E", "#B89578", "#A67C52", "#C4A484", "#D8C1A8"],
            week_tint=["#FAF4EC", "#F8F0E6", "#F7EDE1", "#FAF3EA", "#FCF8F2"],
            week_check=["#8B5E34", "#7A5635", "#6B4423", "#8B5E34", "#9A6B42"],
            week_on=["#3E2C23", "#FFFFFF", "#FFFFFF", "#3E2C23", "#3E2C23"],
            streak_lo="#FAF6F0", streak_mid="#DFC7AE", streak_hi="#A67C52",
            bar="#C8A98E", donut_rest="#EFE4D7",
            chart_title="COZY ALPACA PROGRESS • TIẾN ĐỘ THÓI QUEN MỖI NGÀY",
        ),
        tracker_name="🦙 Cream Alpaca",
        habits=[
            Habit("Thức dậy sớm & uống ly nước ấm", goal=28, p=0.90),
            Habit("Ghi chép thu chi hằng ngày", goal=30, p=0.93),
            Habit("Không mua sắm bốc đồng online", goal=26, p=0.84),
            Habit("Tự nấu ăn / mang cơm trưa", goal=24, p=0.82),
            Habit("Tập vận động / đi bộ 30 phút", goal=26, p=0.86),
            Habit("Đọc sách tài chính / kỹ năng 20p", goal=26, p=0.85),
            Habit("Dọn gọn bàn làm việc cuối ngày", goal=28, p=0.88),
            Habit("Ngủ đủ 8 tiếng trước 23h00", goal=28, p=0.87),
        ],
        seed=201, label_tag="COZY ALPACA & BUDGET", garden_label="ALPACA MEADOW",
        grown_label="🦙  FLUFFY ALPACAS\nGROWN:", tracker_capture_range="A1:AN45",
        addon_fn=_addon_alpaca_budget,
    ),
    TemplateDef(
        stem="21_Blush_Alpaca_Flower_Crown", short_key="21_alpaca_blush",
        theme=Theme(
            slug="alpaca_blush", name="BLUSH ALPACA FLOWER CROWN", emoji="🦙",
            tagline_vi="Chú Alpaca kẹo bông hồng tím đội Vương Miện Hoa kết hợp góc Self-Care & Chi tiêu nhẹ nhàng đầy mộng mơ!",
            page="#FDF2F8", card="#FFFFFF", ink="#4C1D42", muted="#956B8B", line="#F2D4E6",
            primary="#DB6DA3", primary_dark="#A63F74", on_primary="#FFFFFF", soft="#FCE7F3",
            chart_fill="#F9A8D4", chart_line="#C084FC",
            week_head=["#F9A8D4", "#DDD6FE", "#FBCFE8", "#C4B5FD", "#F5D0FE"],
            week_tint=["#FFF4F9", "#F7F4FF", "#FFF6FA", "#F5F2FF", "#FDF4FF"],
            week_check=["#C03A7C", "#7C3AED", "#DB2777", "#6D28D9", "#A21CAF"],
            week_on=["#4C1D42", "#3B1D5E", "#4C1D42", "#3B1D5E", "#4C1D42"],
            streak_lo="#FDF2F8", streak_mid="#F9A8D4", streak_hi="#C084FC",
            bar="#F472B6", donut_rest="#F5E1EE",
            chart_title="BLUSH ALPACA PROGRESS • TIẾN ĐỘ MỖI NGÀY",
        ),
        tracker_name="🦙 Blush Alpaca",
        habits=[
            Habit("Chăm sóc da sáng & kem chống nắng", goal=30, p=0.94),
            Habit("Uống đủ 2L nước & trà hoa", goal=30, p=0.91),
            Habit("Pilates / Yoga giãn cơ 25 phút", goal=24, p=0.84),
            Habit("Viết nhật ký cảm xúc & biết ơn", goal=28, p=0.88),
            Habit("Đọc sách nhẹ nhàng 20 phút tối", goal=26, p=0.85),
            Habit("Ăn rau xanh & trái cây tươi", goal=28, p=0.87),
            Habit("Hạn chế màn hình trước khi ngủ", goal=26, p=0.81),
            Habit("Ngủ sớm làm đẹp trước 23h00", goal=28, p=0.86),
        ],
        seed=211, label_tag="FLOWER CROWN ALPACA", garden_label="FLOWER CROWN",
        grown_label="🌸  FLOWER ALPACAS\nGROWN:", tracker_capture_range="A1:AN45",
        addon_fn=_addon_alpaca_selfcare,
    ),
    TemplateDef(
        stem="22_Matcha_Alpaca_Meadow", short_key="22_alpaca_matcha",
        theme=Theme(
            slug="alpaca_matcha", name="MATCHA ALPACA MEADOW", emoji="🦙",
            tagline_vi="Chú Alpaca xanh Matcha đeo yên thêu rực rỡ cùng thẻ Mục Tiêu Quỹ Tiết Kiệm Tháng tươi mát & bình yên!",
            page="#F3FAF4", card="#FFFFFF", ink="#234E2A", muted="#638768", line="#D4ECD7",
            primary="#6BBF74", primary_dark="#3E8E49", on_primary="#FFFFFF", soft="#E4F5E6",
            chart_fill="#A7D7A9", chart_line="#4E9F58",
            week_head=["#A7D7A9", "#8FD498", "#B5E2B7", "#99D99F", "#C5EBC7"],
            week_tint=["#F1FAF2", "#EDF8EE", "#F3FBF4", "#EFF9F0", "#F6FCF6"],
            week_check=["#2E7D32", "#1B5E20", "#388E3C", "#2E7D32", "#43A047"],
            week_on=["#1B4332", "#1B4332", "#1B4332", "#1B4332", "#1B4332"],
            streak_lo="#F0FDF4", streak_mid="#A7D7A9", streak_hi="#2E7D32",
            bar="#6BBF74", donut_rest="#E2F2E4",
            chart_title="MATCHA MEADOW PROGRESS • TIẾN ĐỘ XANH MỖI NGÀY",
        ),
        tracker_name="🦙 Matcha Alpaca",
        habits=[
            Habit("Dậy sớm đón khí trời & pha trà", goal=28, p=0.90),
            Habit("Đi bộ / chạy bộ ngoài trời 30p", goal=25, p=0.86),
            Habit("Uống đủ 2.5L nước lọc mỗi ngày", goal=30, p=0.92),
            Habit("Tự chuẩn bị bữa ăn healthy", goal=26, p=0.84),
            Habit("Tập trung Deep Work 2 giờ", goal=26, p=0.88),
            Habit("Đọc sách / nghe podcast học tập", goal=26, p=0.85),
            Habit("Ghi chi tiêu & trích quỹ tiết kiệm", goal=28, p=0.89),
            Habit("Thiền 10 phút & ngủ đủ 8 tiếng", goal=28, p=0.87),
        ],
        seed=222, label_tag="MATCHA ALPACA MEADOW", garden_label="MATCHA MEADOW",
        grown_label="🍵  MATCHA ALPACAS\nGROWN:", tracker_capture_range="A1:AN45",
        addon_fn=_addon_alpaca_savings,
    ),
    TemplateDef(
        stem="23_Bamboo_Panda_Zen_Garden", short_key="23_bamboo_panda",
        theme=Theme(
            slug="bamboo_panda", name="BAMBOO PANDA ZEN GARDEN", emoji="🐼",
            tagline_vi="Gấu Trúc dễ thương ôm trúc xanh cùng thanh tiến độ tre trúc tối giản, sạch sẽ & đầy cảm hứng Zen!",
            page="#F9FBF7", card="#FFFFFF", ink="#222222", muted="#6E7A6B", line="#D9E8CD",
            primary="#6AB824", primary_dark="#468212", on_primary="#FFFFFF", soft="#EAF8DC",
            chart_fill="#B8E986", chart_line="#6AB824", chart_kind="column",
            week_head=["#B8E986", "#9EE067", "#C6EF9C", "#A8E475", "#D4F4B4"],
            week_tint=["#F4FCEB", "#F1FBE7", "#F6FDEF", "#F2FBE9", "#F8FEF3"],
            week_check=["#222222", "#222222", "#222222", "#222222", "#222222"],
            week_on=["#1F3A09", "#1F3A09", "#1F3A09", "#1F3A09", "#1F3A09"],
            streak_lo="#F4FCEB", streak_mid="#B8E986", streak_hi="#468212",
            bar="#7ED321", donut_rest="#E8F5DA",
            chart_title="BAMBOO ZEN PROGRESS • TIẾN ĐỘ RỪNG TRÚC",
        ),
        tracker_name="🐼 Bamboo Panda",
        habits=[
            Habit("Thức dậy trước 6h30 & dọn giường", goal=28, p=0.90),
            Habit("Uống đủ 2L nước lọc mỗi ngày", goal=30, p=0.93),
            Habit("Thiền tĩnh tâm 15 phút (Zen)", goal=26, p=0.86),
            Habit("Ăn uống cân bằng, nhiều rau xanh", goal=28, p=0.87),
            Habit("Đọc sách tối thiểu 15–20 phút", goal=26, p=0.85),
            Habit("Tập vận động nhẹ 30 phút", goal=25, p=0.84),
            Habit("Lập kế hoạch ngày mai trước ngủ", goal=28, p=0.88),
            Habit("Ngủ đủ giấc 7.5–8 tiếng", goal=28, p=0.89),
        ],
        seed=233, label_tag="BAMBOO PANDA ZEN", garden_label="PANDA BAMBOO",
        grown_label="🐼  HAPPY PANDAS\nGROWN:", tracker_capture_range="A1:AN38",
    ),
    TemplateDef(
        stem="24_Royal_Cat_Saving_Cash", short_key="24_royal_cat_cash",
        theme=Theme(
            slug="royal_cat_cash", name="ROYAL CAT SAVING CASH", emoji="👑",
            tagline_vi="Nuôi Mèo Hộp Giấy lên ngôi Mèo Hoàng Gia đội vương miện — kết hợp bảng Dòng Tiền Dự Kiến vs Thực Tế & Bộ đếm Vương Quốc Mèo!",
            page="#F6F3EC", card="#FFFFFF", ink="#4A3B32", muted="#8C7B70", line="#E3D9CD",
            primary="#8D7360", primary_dark="#5E4B3E", on_primary="#FFFFFF", soft="#EFE8DF",
            chart_fill="#D8C3B0", chart_line="#8D7360",
            week_head=["#D8C3B0", "#D9DFD3", "#CBB39E", "#CBD5C4", "#DFCEBF"],
            week_tint=["#FAF6F1", "#F5F7F3", "#F8F3ED", "#F3F6F1", "#FBF8F4"],
            week_check=["#5E4B3E", "#4A6150", "#5E4B3E", "#4A6150", "#70594A"],
            week_on=["#3D2F27", "#2F3E32", "#3D2F27", "#2F3E32", "#3D2F27"],
            streak_lo="#F6F3EC", streak_mid="#D8C3B0", streak_hi="#6E5747",
            bar="#BFA38A", donut_rest="#EAE2D8",
            chart_title="CAT KINGDOM & CASH DISCIPLINE • KỶ LUẬT MỖI NGÀY",
        ),
        tracker_name="👑 Royal Cat & Cash",
        habits=[
            Habit("Ghi lại 100% khoản chi trong ngày", goal=30, p=0.94),
            Habit("Ngày không chi tiêu lãng phí", goal=24, p=0.82),
            Habit("Tự pha cà phê / nấu ăn tại nhà", goal=26, p=0.85),
            Habit("Trích quỹ tiết kiệm / đầu tư nhỏ", goal=28, p=0.88),
            Habit("Tập thể dục rèn sức khỏe 30p", goal=25, p=0.84),
            Habit("Đọc sách tài chính cá nhân 20p", goal=26, p=0.86),
            Habit("Hoàn thành 3 việc tạo thu nhập", goal=26, p=0.89),
            Habit("Ngủ sớm & kiểm tra mục tiêu ngày", goal=28, p=0.87),
        ],
        seed=244, label_tag="RAISING CATS & CASH", garden_label="ROYAL CAT KINGDOM",
        grown_label="👑  ROYAL CATS\nRAISED:", tracker_capture_range="A1:AN45",
        addon_fn=_addon_royal_cat_cash,
    ),
    TemplateDef(
        stem="25_Ginger_Kitten_Basket_Routine", short_key="25_ginger_kitten",
        theme=Theme(
            slug="ginger_kitten", name="GINGER KITTEN BASKET ROUTINE", emoji="🐱",
            tagline_vi="Chú Mèo Cam siêu đáng yêu chia nhịp Sáng · Chiều · Tối trên nền Mint Sage & Đào Kem + Bảng Xếp Hạng Top Thói Quen!",
            page="#F6FBF8", card="#FFFFFF", ink="#4A3525", muted="#8C7564", line="#D8E9DF",
            primary="#E59866", primary_dark="#C06C3A", on_primary="#FFFFFF", soft="#FFF3E4",
            chart_fill="#C9E4D6", chart_line="#E59866",
            week_head=["#C9E4D6", "#F7C6B9", "#C9E4D6", "#F7C6B9", "#FFE6B3"],
            week_tint=["#F1FAF5", "#FFF5F2", "#F1FAF5", "#FFF5F2", "#FFFBF0"],
            week_check=["#3D8B68", "#D46B50", "#3D8B68", "#D46B50", "#C07A28"],
            week_on=["#1B4332", "#6B271D", "#1B4332", "#6B271D", "#5C3A09"],
            streak_lo="#FFF8DC", streak_mid="#F7C6B9", streak_hi="#E59866",
            bar="#E59866", donut_rest="#E8F3EC",
            chart_title="GINGER KITTEN ROUTINE • LỊCH TRÌNH SÁNG-CHIỀU-TỐI",
        ),
        tracker_name="🐱 Ginger Kitten",
        habits=[
            Habit("☀️ [Sáng] Dậy sớm & dọn gọn giường", goal=28, p=0.91),
            Habit("☀️ [Sáng] Uống nước ấm & vận động 20p", goal=26, p=0.87),
            Habit("☀️ [Sáng] Ăn sáng đầy đủ dinh dưỡng", goal=28, p=0.89),
            Habit("🌤️ [Chiều] Tập trung Deep Work 2 giờ", goal=26, p=0.88),
            Habit("🌤️ [Chiều] Uống đủ 2L nước & giãn cơ", goal=30, p=0.92),
            Habit("🌤️ [Chiều] Đi bộ nhẹ / nghỉ mắt 15p", goal=26, p=0.83),
            Habit("🌙 [Tối] Đọc sách giấy 20 phút", goal=26, p=0.85),
            Habit("🌙 [Tối] Skincare & viết nhật ký tối", goal=28, p=0.88),
            Habit("🌙 [Tối] Tắt điện thoại & ngủ 23h", goal=28, p=0.84),
        ],
        seed=255, label_tag="SOPHIA GINGER CAT", garden_label="GINGER CAT BASKET",
        grown_label="🐱  HAPPY KITTENS\nGROWN:", tracker_capture_range="A1:AN45",
        addon_fn=_addon_ginger_rank,
    ),
    TemplateDef(
        stem="26_Pastel_Purple_Royal_Cat", short_key="26_purple_cat",
        theme=Theme(
            slug="purple_cat", name="PASTEL PURPLE ROYAL CAT", emoji="🐱",
            tagline_vi="Phong cách Tím Lavender & Hồng Phấn siêu thẩm mỹ cùng Mèo Xám Hoàng Gia & tab Nhiệm Vụ Ngày nổi bật!",
            page="#F4F0F9", card="#FFFFFF", ink="#3B324A", muted="#827894", line="#E3D9EE",
            primary="#9D84C7", primary_dark="#6E529E", on_primary="#FFFFFF", soft="#EDE6F7",
            chart_fill="#D2C1E8", chart_line="#9D84C7",
            week_head=["#D2C1E8", "#F2D2DC", "#D2C1E8", "#F2D2DC", "#DFD3F0"],
            week_tint=["#F7F3FC", "#FDF4F7", "#F7F3FC", "#FDF4F7", "#F8F5FD"],
            week_check=["#6E529E", "#B85C7E", "#6E529E", "#B85C7E", "#6B6E7B"],
            week_on=["#3B285C", "#5E253B", "#3B285C", "#5E253B", "#3B285C"],
            streak_lo="#F4F0F9", streak_mid="#D2C1E8", streak_hi="#6E529E",
            bar="#B298DC", donut_rest="#EAE2F3",
            chart_title="AESTHETIC PURPLE CAT • BIỂU ĐỒ KỶ LUẬT MỖI NGÀY",
        ),
        tracker_name="🐱 Purple Royal Cat",
        habits=[
            Habit("Thức dậy nhẹ nhàng & uống nước", goal=30, p=0.92),
            Habit("Viết 3 mục tiêu quan trọng nhất", goal=28, p=0.90),
            Habit("Tập thể dục / đi bộ 30 phút", goal=25, p=0.85),
            Habit("Ăn rau xanh & ít đồ ngọt", goal=26, p=0.84),
            Habit("Đọc sách / học kỹ năng 25 phút", goal=26, p=0.86),
            Habit("Dọn gọn phòng 10 phút mỗi ngày", goal=28, p=0.88),
            Habit("Chăm sóc da & thư giãn buổi tối", goal=28, p=0.90),
            Habit("Ngủ đủ 8 tiếng trước 23h00", goal=28, p=0.85),
        ],
        seed=266, label_tag="PASTEL PURPLE CAT", garden_label="ROYAL GREY CATS",
        grown_label="👑  ROYAL GREY CATS\nRAISED:", tracker_capture_range="A1:AN38",
    ),
    TemplateDef(
        stem="27_Hatching_Chick_Icon_Studio", short_key="27_hatching_chick",
        theme=Theme(
            slug="hatching_chick", name="HATCHING CHICK ICON STUDIO", emoji="🐣",
            tagline_vi="Ấp nở chú Gà Con Vàng siêu cưng qua 6 cấp độ từ trứng tròn đến gà bông tung cánh — phối Tím Periwinkle & Cam Đào rực rỡ!",
            page="#FCF8F2", card="#FFFFFF", ink="#3B2E4A", muted="#857894", line="#EAE0D5",
            primary="#7C5CD6", primary_dark="#5B3DB5", on_primary="#FFFFFF", soft="#EFEAFF",
            chart_fill="#FAD6B8", chart_line="#EA7B30", chart_kind="column",
            week_head=["#D4C5F9", "#FAD6B8", "#D4C5F9", "#FAD6B8", "#FEF08A"],
            week_tint=["#F6F2FF", "#FFF7F0", "#F6F2FF", "#FFF7F0", "#FFFDF0"],
            week_check=["#6D48D4", "#D96B27", "#6D48D4", "#D96B27", "#CA8A04"],
            week_on=["#3B1E78", "#7C2D12", "#3B1E78", "#7C2D12", "#713F12"],
            streak_lo="#FFFBEB", streak_mid="#FDE047", streak_hi="#7C5CD6",
            bar="#F59E0B", donut_rest="#EFE8FA",
            hero_header_bg="#FACC15", hero_header_fg="#3B2E4A",
            chart_title="HATCHING CHICK STUDIO • TIẾN ĐỘ ẤP TRỨNG MỖI NGÀY",
        ),
        tracker_name="🐣 Hatching Chick",
        habits=[
            Habit("Uống đủ 8 ly nước lọc mỗi ngày", goal=30, p=0.93),
            Habit("Giãn cơ / vận động buổi sáng 15p", goal=28, p=0.89),
            Habit("Đọc sách ít nhất 15–20 phút", goal=26, p=0.86),
            Habit("Không điện thoại sau 21h30", goal=26, p=0.81),
            Habit("Uống vitamin & ăn sáng đủ chất", goal=30, p=0.91),
            Habit("Viết nhật ký & 3 điều biết ơn", goal=28, p=0.87),
            Habit("Tập thể dục / đi bộ 30 phút", goal=24, p=0.84),
            Habit("Thiền / hít thở thư giãn 10 phút", goal=26, p=0.85),
            Habit("Dọn bếp & chọn đồ cho ngày mai", goal=28, p=0.88),
        ],
        seed=277, label_tag="CHOOSE YOUR STAGE: CHICK", garden_label="HATCHING STUDIO",
        grown_label="🐣  FLUFFY CHICKS\nHATCHED:", tracker_capture_range="A1:AN38",
    ),
    TemplateDef(
        stem="28_Cotton_Candy_Jar_Sweet", short_key="28_candy_jar",
        theme=Theme(
            slug="candy_jar", name="COTTON CANDY JAR SWEET", emoji="🍬",
            tagline_vi="Lấp đầy hũ thủy tinh bằng kẹo ngọt & kẹo mút xoắn sắc Hồng Kẹo Bông + Xanh Bầu Trời — kèm Bảng Xếp Hạng Thói Quen!",
            page="#FFFDFE", card="#FFFFFF", ink="#3B3054", muted="#877C9E", line="#F2D9E9",
            primary="#EC4899", primary_dark="#BE185D", on_primary="#FFFFFF", soft="#FCE7F3",
            chart_fill="#BAE6FD", chart_line="#3B82F6",
            week_head=["#FBCFE8", "#BAE6FD", "#FBCFE8", "#BAE6FD", "#DDD6FE"],
            week_tint=["#FFF5FA", "#F2FAFF", "#FFF5FA", "#F2FAFF", "#F7F4FF"],
            week_check=["#EC4899", "#2563EB", "#EC4899", "#2563EB", "#7C3AED"],
            week_on=["#831843", "#1E3A8A", "#831843", "#1E3A8A", "#4C1D95"],
            streak_lo="#F0F9FF", streak_mid="#BAE6FD", streak_hi="#EC4899",
            bar="#60A5FA", donut_rest="#FCE7F3",
            hero_header_bg="#FBCFE8", hero_header_fg="#831843",
            chart_title="SWEET CANDY JAR WAVE • SÓNG KẸO NGỌT MỖI NGÀY",
        ),
        tracker_name="🍬 Cotton Candy Jar",
        habits=[
            Habit("Uống đủ 8 ly nước lọc tươi mát", goal=30, p=0.92),
            Habit("Tập thể dục 30 phút tràn năng lượng", goal=25, p=0.86),
            Habit("Đọc sách 20 phút mở mang kiến thức", goal=26, p=0.87),
            Habit("Thức dậy sớm trước 6h30", goal=28, p=0.85),
            Habit("Luyện ngoại ngữ / kỹ năng mới 20p", goal=26, p=0.84),
            Habit("Hạn chế lướt mạng xã hội vô bổ", goal=26, p=0.82),
            Habit("Lên thực đơn lành mạnh trong ngày", goal=28, p=0.88),
            Habit("Viết nhật ký & gấp gọn chăn gối", goal=30, p=0.91),
        ],
        seed=288, label_tag="FILL YOUR CANDY JAR", garden_label="CANDY JAR SHELF",
        grown_label="🍬  YAY! CANDY JARS\nFILLED:", tracker_capture_range="A1:AN45",
        addon_fn=_addon_candy_rank,
    ),
    TemplateDef(
        stem="29_Watercolor_Rose_Bouquet", short_key="29_rose_bouquet",
        theme=Theme(
            slug="rose_bouquet", name="WATERCOLOR ROSE BOUQUET", emoji="💐",
            tagline_vi="Bó hoa hồng phấn màu nước lãng mạn trên nền trắng ngà tinh khôi — theo dõi kích thước Bó Hoa Tháng Này nở rộ từng ngày!",
            page="#FFFDFD", card="#FFFFFF", ink="#592B3B", muted="#9C7683", line="#F2DCE4",
            primary="#D47E9B", primary_dark="#A64D6B", on_primary="#FFFFFF", soft="#FBEBF0",
            chart_fill="#F8D7E3", chart_line="#D47E9B",
            week_head=["#E29BB3", "#E9AEC2", "#DF92AD", "#EBB6C8", "#F1C8D6"],
            week_tint=["#FDF5F8", "#FEF7F9", "#FDF4F7", "#FEF8FA", "#FFF9FB"],
            week_check=["#A64D6B", "#B55B7A", "#9E4362", "#B55B7A", "#6E8F64"],
            week_on=["#FFFFFF", "#FFFFFF", "#FFFFFF", "#592B3B", "#592B3B"],
            streak_lo="#FDF5F8", streak_mid="#F2C0D2", streak_hi="#A64D6B",
            bar="#E29BB3", donut_rest="#F6E5EB",
            chart_title="MONTHLY BOUQUET WAVE • LÀN SÓNG HOA HỒNG",
        ),
        tracker_name="💐 Rose Bouquet",
        habits=[
            Habit("Rửa mặt sạch & skincare sáng tối", goal=30, p=0.94),
            Habit("Ngủ đủ 8 tiếng dưỡng nhan", goal=28, p=0.88),
            Habit("Dọn gọn giường ngủ mỗi sáng", goal=30, p=0.92),
            Habit("Đọc sách văn học / kỹ năng 20p", goal=26, p=0.86),
            Habit("Dành 15 phút chăm sóc tinh thần", goal=28, p=0.87),
            Habit("Uống vitamin & 2L nước mỗi ngày", goal=30, p=0.91),
            Habit("Đi bộ thư giãn hít thở khí trời", goal=25, p=0.84),
            Habit("Viết 3 điều dịu dàng đáng nhớ", goal=28, p=0.88),
        ],
        seed=299, label_tag="MONTHLY BOUQUET SIZE", garden_label="ROSE BOUQUET",
        grown_label="💐  MONTHLY BOUQUET\nSIZE (FLOWERS):", tracker_capture_range="A1:AN38",
    ),
    TemplateDef(
        stem="30_Shiba_Inu_Happy_Bork", short_key="30_shiba_inu",
        theme=Theme(
            slug="shiba_inu", name="SHIBA INU HAPPY BORK", emoji="🐕",
            tagline_vi="Chú cún Shiba Inu đeo khăn đỏ Nhật Bản siêu dễ thương — tích điểm Cún Ngoan (Good Boy Points) & mở khóa Shiba Vương Miện!",
            page="#FFF9F0", card="#FFFFFF", ink="#3B281E", muted="#8E7260", line="#F0DFCA",
            primary="#E89B54", primary_dark="#C06E26", on_primary="#FFFFFF", soft="#FEF0DF",
            chart_fill="#F7C99B", chart_line="#D94F4F",
            week_head=["#E89B54", "#EEAD6E", "#D94F4F", "#E89B54", "#F4BE82"],
            week_tint=["#FFF6EB", "#FFF8EF", "#FFF3F3", "#FFF6EB", "#FFF9F0"],
            week_check=["#D94F4F", "#C06E26", "#D94F4F", "#C06E26", "#B45309"],
            week_on=["#FFFFFF", "#3B281E", "#FFFFFF", "#FFFFFF", "#3B281E"],
            streak_lo="#FFF9F0", streak_mid="#F9D5D3", streak_hi="#D94F4F",
            bar="#E89B54", donut_rest="#F5E5D5",
            hero_header_bg="#D94F4F", hero_header_fg="#FFFFFF",
            chart_title="GOOD BOY VELOCITY • NĂNG LƯỢNG CÚN SHIBA MỖI NGÀY",
        ),
        tracker_name="🐕 Shiba Inu Tracker",
        habits=[
            Habit("Dậy sớm tràn năng lượng trước 6h30", goal=28, p=0.90),
            Habit("Đi dạo / Chạy bộ ngoài trời 30p", goal=26, p=0.87),
            Habit("Uống đủ 2.5L nước lọc mỗi ngày", goal=30, p=0.93),
            Habit("Ăn đủ chất & hạn chế đồ chiên rán", goal=28, p=0.86),
            Habit("Tập trung Deep Work 2 giờ không lười", goal=26, p=0.89),
            Habit("Đọc sách / học kỹ năng mới 20p", goal=26, p=0.85),
            Habit("Ghi chi tiêu & giữ vững ngân sách", goal=28, p=0.88),
            Habit("Tắt điện thoại sớm & ngủ 23h00", goal=28, p=0.86),
        ],
        seed=301, label_tag="SHIBA INU GOOD BOY", garden_label="SHIBA INU PARK",
        grown_label="🦴  GOOD BOY DAYS\nTHIS MONTH:", tracker_capture_range="A1:AN43",
        addon_fn=_addon_shiba,
    ),
    TemplateDef(
        stem="31_Akita_Inu_Snow_Loyal", short_key="31_akita_inu",
        theme=Theme(
            slug="akita_inu", name="AKITA INU SNOW LOYAL", emoji="❄️",
            tagline_vi="Chú Akita Inu bông tuyết trung thành phong cách Nhật Bản mùa đông (Xanh Chàm Indigo & Kem Mơ) — tĩnh tâm, kiên định & bền bỉ!",
            page="#F7FAFC", card="#FFFFFF", ink="#1E293B", muted="#64748B", line="#D8E5F2",
            primary="#3B5998", primary_dark="#263C6B", on_primary="#FFFFFF", soft="#EBF3FB",
            chart_fill="#CFE3F5", chart_line="#3B5998",
            week_head=["#3B5998", "#4F72B3", "#4F8A6E", "#3B5998", "#C89564"],
            week_tint=["#F1F6FC", "#F3F8FD", "#F1FAF5", "#F1F6FC", "#FDF8F2"],
            week_check=["#3B5998", "#2B4C8C", "#3D7A5E", "#3B5998", "#B4743B"],
            week_on=["#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF"],
            streak_lo="#F0F7FF", streak_mid="#93C5FD", streak_hi="#3B5998",
            bar="#4F8A6E", donut_rest="#E2ECF6",
            chart_title="AKITA WINTER LOYALTY • NHỊP KỶ LUẬT TRUNG THÀNH",
        ),
        tracker_name="❄️ Akita Inu Zen",
        habits=[
            Habit("Thiền sáng / hít thở tĩnh tâm 10p", goal=28, p=0.89),
            Habit("Tập thể dục bền bỉ 35 phút", goal=25, p=0.86),
            Habit("Uống đủ 2.5L nước & trà ấm", goal=30, p=0.92),
            Habit("Deep Work tập trung hoàn toàn 2h", goal=26, p=0.90),
            Habit("Đọc sách / nghiên cứu chuyên sâu 25p", goal=26, p=0.87),
            Habit("Ăn lành mạnh & nấu ăn tại nhà", goal=26, p=0.84),
            Habit("Dọn tối giản không gian sống 10p", goal=28, p=0.88),
            Habit("Viết nhật ký biết ơn & ngủ đủ 8h", goal=28, p=0.88),
        ],
        seed=311, label_tag="AKITA SNOW LOYALTY", garden_label="AKITA SNOW VILLAGE",
        grown_label="❄️  LOYAL AKITA DAYS\nTHIS MONTH:", tracker_capture_range="A1:AN43",
        addon_fn=_addon_akita,
    ),
]


def _month_dyn_anims(sheet_name: str, tr: TrackerRefs, prefix: str | None = None) -> list[dict]:
    """Manifest of 31 dynamic Daily Linked Pictures + 1 dynamic Monthly Hero Linked Picture."""
    items = []
    for k in range(1, 32):
        nm = f"Anim_{prefix}_D{k:02d}" if prefix else f"Anim_Day{k:02d}"
        items.append({
            "name": nm,
            "refers_to": f"=INDEX({ASSETS_SHEET}!$B$2:$B$8,{CALC_SHEET}!${colname(k)}${tr.stage_row + 1})",
            "sheet": sheet_name, "r1": R_IMG, "c1": day_col(k), "r2": R_IMG, "c2": day_col(k),
            "align_bottom": True,
        })
    r1, c1, r2, c2 = tr.hero_icon_box
    hero_nm = f"Anim_{prefix}_Hero" if prefix else "Anim_MonthlyHero"
    items.append({
        "name": hero_nm,
        "refers_to": f"=INDEX({ASSETS_SHEET}!$B$2:$B$8,{tr.hero_stage_cell})",
        "sheet": sheet_name, "r1": r1, "c1": c1, "r2": r2, "c2": c2,
        "align_bottom": False,
    })
    return items


# =========================================================================== #
#  MASTER BUILDER — UNIFIED 4-VISIBLE-TAB ARCHITECTURE FOR ALL 3 EDITIONS!
# =========================================================================== #
def build_template(tdef: TemplateDef, out_path: Path, edition: str = "pro_xlsm") -> dict:
    """
    Unified 4 visible tabs across ALL 3 editions & ALL 10 templates:
      1. `📖 Hướng Dẫn`
      2. `<Template Monthly Tracker>` (with each template's signature in-sheet addon block!)
      3. `🎯 Yearly Goals & Habits` (themed, Year dropdown I2, live dynamic Anim_YearlyGoals)
      4. `🏆 Tổng Kết & Thành Tựu Năm` (themed, Year dropdown B3, 4 KPIs, 12-Month Garden, 8 Badges)
    Hidden sheets:
      - `pro_xlsm`: `_Calc`, `_Database`, `_Assets` (+ VBA `modHabitState.bas`)
      - `offline`:  `_Calc`, `_Database`, `_Assets` (pure `.xlsx`, ZERO macros!)
      - `gsheets`:  `_Calc`, `_Database` (`=IMAGE()` on `main` + 1-click Apps Script `onEdit`)
    """
    universal = edition in ("pro_xlsm", "offline")
    gsheets = (edition == "gsheets")
    pro_mode = (edition == "pro_xlsm")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    wb = xlsxwriter.Workbook(str(out_path))
    styles = Styles(wb, tdef.theme)

    extra_tab_docs = [
        (DAILY_TASKS_SHEET, "Quản lý nhiệm vụ đột xuất theo từng ngày (Ngày/Tháng/Năm), nhóm ưu tiên & hoạt ảnh lớn dần 0% → 100%!"),
        (YEARLY_GOALS_SHEET, "Lập mục tiêu năm (2024–2040), chia nhỏ Tháng/Tuần/Ngày & bộ đếm hoạt ảnh động 6 giai đoạn."),
        (ANNUAL_SHEET, "Tổng kết 12 tháng thiết kế riêng theo chủ đề, 4 thẻ KPI, khu vườn 12 biểu tượng & 8 Huy hiệu kỷ luật!"),
    ]
    g_info = build_guide(wb, styles, tdef.tracker_name, extra_tab_docs, edition=edition)

    ws_calc = init_calc_sheet(wb, active_year=2026, last_loaded_key="2026-10", last_goal_year=2026)

    dyn_anims: list[dict] = []
    static_pics: list[dict] = list(g_info["linked_pictures"])
    checkboxes: dict[str, list] = {}

    # Tab 2: Monthly Tracker (single ultra-clean tab with template's signature addon block!)
    ws_tr = wb.add_worksheet(tdef.tracker_name)
    cv = Canvas(wb, ws_tr, styles, tdef.tracker_name, universal=universal, gsheets=gsheets)
    tr = build_tracker(wb, styles, cv, TrackerSpec(
        sheet=tdef.tracker_name, habits=tdef.habits, month="October", year=2026, seed=tdef.seed,
        label_tag=tdef.label_tag, garden_label=tdef.garden_label, grown_label=tdef.grown_label,
        right_labels=tdef.right_labels, top_right=tdef.top_right, extra_cols=tdef.extra_cols,
        universal=universal, gsheets=gsheets, pro_mode=pro_mode, calc_slot=0, fixed_month=None,
        sample_mode="oct", form_rows=N_FORM_ROWS,
    ), ws_calc=ws_calc)
    if tdef.addon_fn:
        tdef.addon_fn(wb, cv, tr, tdef.seed)
    cv.flush()
    if universal:
        checkboxes[tdef.tracker_name] = cv.form_checkboxes
        dyn_anims.extend(_month_dyn_anims(tdef.tracker_name, tr, prefix=None))

    # Tab 3 (v3.0 NEW!): Daily One-Off Tasks (`📝 Nhiệm Vụ Ngày`) right next to Monthly Tracker!
    dt_info = build_daily_tasks_sheet(
        wb, styles, ws_calc, universal=universal, gsheets=gsheets, pro_mode=pro_mode
    )
    if universal:
        checkboxes.update(dt_info["checkboxes"])
        dyn_anims.extend(dt_info["dyn_anims"])

    # Tab 4: Yearly Goals & Habits (themed + Year dropdown + Dynamic Anim_YearlyGoals!)
    yg_info = build_yearly_goals_v21(wb, styles, ws_calc, year=2026, universal=universal,
                                     gsheets=gsheets, pro_mode=pro_mode)
    if universal:
        checkboxes.update(yg_info["checkboxes"])
        dyn_anims.extend(yg_info["dyn_anims"])

    # Tab 5: Bespoke Theme-Specific Annual Summary & Achievements (reads live active month + _Database!)
    ann_info = build_annual_achievements_sheet(
        wb, styles, ws_calc, mode=edition, pro_tr=tr, year=2026, universal=universal, gsheets=gsheets
    )
    if universal:
        dyn_anims.extend(ann_info["dyn_anims"])

    # Hidden `_Database` pre-seeded with `2026-10` + `2026` Yearly Goals + `2026-10-21` Daily Tasks
    build_database_sheet(wb, styles, tdef.habits,
                         seed_months=[(2026, 10, tr.ticks_2d)],
                         seed_goal_year=2026)

    ws_calc.hide()
    if universal:
        add_assets_placeholder(wb, styles)
    wb.close()

    captures = [
        {"sheet": tdef.tracker_name, "range": tdef.tracker_capture_range, "out": f"{tdef.short_key}_tracker.png"},
        {"sheet": ANNUAL_SHEET, "range": ann_info["capture_range"], "out": f"{tdef.short_key}_annual_achievements.png"},
    ]
    if tdef.short_key in ("01_sunflower", "20_alpaca_cream", "24_royal_cat_cash", "26_purple_cat", "30_shiba_inu", "31_akita_inu"):
        captures.append({"sheet": DAILY_TASKS_SHEET, "range": dt_info["capture_range"], "out": f"{tdef.short_key}_daily_tasks.png"})
    if tdef.short_key in ("01_sunflower", "20_alpaca_cream", "30_shiba_inu"):
        captures.append({"sheet": YEARLY_GOALS_SHEET, "range": "A1:J26", "out": f"{tdef.short_key}_yearly_goals.png"})

    return {
        "edition": edition,
        "stem": tdef.stem,
        "short_key": tdef.short_key,
        "slug": tdef.theme.slug,
        "tracker_sheet": tdef.tracker_name,
        "daily_tasks_sheet": DAILY_TASKS_SHEET,
        "yearly_goals_sheet": YEARLY_GOALS_SHEET,
        "annual_sheet": ANNUAL_SHEET,
        "dyn_anims": dyn_anims,
        "static_pics": static_pics,
        "checkboxes": checkboxes,
        "captures": captures,
        "base_path": str(out_path),
    }


def build_base_pro(only: list[str] | None = None) -> list[dict]:
    tmp = BUILD_TMP / "pro"
    tmp.mkdir(parents=True, exist_ok=True)
    manifests = []
    for tdef in TEMPLATES:
        if only and tdef.stem not in only and tdef.short_key not in only:
            continue
        out = tmp / f"{tdef.stem}_Pro_base.xlsx"
        meta = build_template(tdef, out, edition="pro_xlsm")
        (tmp / f"{tdef.stem}.manifest.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        manifests.append(meta)
        cb_n = sum(len(v) for v in meta["checkboxes"].values())
        print(f"  [PRO base] {tdef.stem}  cbs={cb_n}, dyn_anims={len(meta['dyn_anims'])}, static={len(meta['static_pics'])}", flush=True)
    return manifests


def build_base_offline(only: list[str] | None = None) -> list[dict]:
    tmp = BUILD_TMP / "offline"
    tmp.mkdir(parents=True, exist_ok=True)
    manifests = []
    for tdef in TEMPLATES:
        if only and tdef.stem not in only and tdef.short_key not in only:
            continue
        out = tmp / f"{tdef.stem}_offline_base.xlsx"
        meta = build_template(tdef, out, edition="offline")
        (tmp / f"{tdef.stem}.manifest.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        manifests.append(meta)
        cb_n = sum(len(v) for v in meta["checkboxes"].values())
        print(f"  [OFFLINE base] {tdef.stem}  cbs={cb_n}, dyn_anims={len(meta['dyn_anims'])}, static={len(meta['static_pics'])}", flush=True)
    return manifests


def build_all_gsheets(only: list[str] | None = None) -> list[Path]:
    GSHEETS_DIR.mkdir(parents=True, exist_ok=True)
    paths = []
    for tdef in TEMPLATES:
        if only and tdef.stem not in only and tdef.short_key not in only:
            continue
        out = GSHEETS_DIR / f"{tdef.stem}.xlsx"
        build_template(tdef, out, edition="gsheets")
        paths.append(out)
        print(f"  [GSHEETS] {out.name} ({out.stat().st_size:,} bytes)", flush=True)
    return paths


if __name__ == "__main__":
    args = sys.argv[1:]
    mode = args[0] if args else "all"
    only = args[1:] or None
    if mode in ("all", "pro"):
        build_base_pro(only)
    if mode in ("all", "offline"):
        build_base_offline(only)
    if mode in ("all", "gsheets"):
        build_all_gsheets(only)
