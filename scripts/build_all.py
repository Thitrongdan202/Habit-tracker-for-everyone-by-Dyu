"""
Master generator for the 6-template Habit Tracker Excel Collection (plus Offline Pro editions).

Run from the repository root:
    python scripts/build_all.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import xlsxwriter

from hx.core import Theme, Styles, Canvas, acell, qs
from hx.guide import build_guide
from hx.tracker import (Habit, TrackerSpec, build_tracker, attach_offline_sprites_sheet, R_TOT)
from hx.addons import (add_cactus_weekly_strip, add_rainbow_bottom_blocks,
                       add_wellness_mood_block, add_focus_rank_top_card)
from hx.extras import (build_yearly_goals_sheet, build_annual_overview_sheet,
                       build_reflection_notes_sheet, build_rainbow_analytics_sheet,
                       build_monthly_budget_sheet, build_life_overview_sheet,
                       build_gratitude_sheet, build_milestones_sheet)

ASSETS_DIR = ROOT / "assets"
TEMPLATES_DIR = ROOT / "templates"
PRO_DIR = TEMPLATES_DIR / "pro_macro"


# =========================================================================== #
#  1. SUNFLOWER GARDEN BLUSH (Ref 1 & 2)
# =========================================================================== #
def make_sunflower(path: Path, offline: bool = False):
    theme = Theme(
        slug="sunflower",
        name="SUNFLOWER GARDEN BLUSH",
        emoji="🌻",
        tagline_vi="Gieo từng thói quen nhỏ mỗi ngày — ngắm khu vườn hướng dương nở rộ suốt cả tháng.",
        font="Segoe UI",
        font_title="Segoe UI Semibold",
        font_month="Segoe Script",
        page="#FFFDFB",
        card="#FFFFFF",
        ink="#4A3B3B",
        muted="#968181",
        line="#EAD8D8",
        primary="#D8A7A7",
        primary_dark="#B57A7A",
        on_primary="#FFFFFF",
        soft="#F5E6E6",
        chart_fill="#E7C2C2",
        chart_line="#C48888",
        # Reference 1 dusty-rose gradient across Weeks 1–5!
        week_head=["#D29E9E", "#DBA9A9", "#E3B8B8", "#EBC8C8", "#F2DADA"],
        week_tint=["#F6E8E8", "#F8ECEC", "#FAF0F0", "#FBF4F4", "#FCF7F7"],
        week_check=["#C88E8E", "#CE9696", "#D4A0A0", "#DAA8A8", "#DFB2B2"],
        week_on=["#FFFFFF", "#FFFFFF", "#5B3F3F", "#5B3F3F", "#5B3F3F"],
        streak_lo="#F1FAF4",
        streak_mid="#9AD6B0",
        streak_hi="#4E9F76",
        bar="#D8A7A7",
        donut_rest="#F4E7E7",
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
    wb = xlsxwriter.Workbook(str(path))
    styles = Styles(wb, theme)
    build_guide(wb, styles, "🌻 Monthly Tracker", [
        ("🎯 Yearly Goals & Habits", "Lập mục tiêu năm & chia nhỏ thành thói quen Tháng / Tuần / Ngày + bộ đếm hoa đã gieo."),
        ("📊 Annual Overview", "Tổng kết tiến độ 12 tháng, biểu đồ xu hướng cả năm & ghi chú đánh giá theo Quý."),
    ], offline_sprites=offline)

    ws = wb.add_worksheet("🌻 Monthly Tracker")
    cv = Canvas(wb, ws, styles, "🌻 Monthly Tracker")
    tr = build_tracker(wb, cv, TrackerSpec(
        sheet="🌻 Monthly Tracker", habits=habits, month="October", year=2026, seed=11,
        label_tag="SUNFLOWER GARDEN", garden_label="SUNFLOWER GARDEN",
        grown_label="THIS MONTH,\nYOU'VE GROWN:", offline_sprites=offline,
    ))
    cv.flush()
    build_yearly_goals_sheet(wb, styles, offline_sprites=offline)
    build_annual_overview_sheet(wb, styles, tr)
    if offline:
        attach_offline_sprites_sheet(wb, theme.slug, ASSETS_DIR)
    wb.close()


# =========================================================================== #
#  2. CACTUS BLOOM PASTEL WEEKS (Ref: Cactus Video)
# =========================================================================== #
def make_cactus(path: Path, offline: bool = False):
    theme = Theme(
        slug="cactus",
        name="CACTUS BLOOM PASTEL WEEKS",
        emoji="🌵",
        tagline_vi="5 tuần rực rỡ sắc pastel — kiên trì từng ngày để chậu xương rồng của bạn nở hoa hồng xinh xắn!",
        font="Segoe UI",
        font_title="Segoe UI Semibold",
        font_month="Segoe UI Semibold",
        page="#FCFCFA",
        card="#FFFFFF",
        ink="#3E4346",
        muted="#8A9296",
        line="#E3E6E8",
        primary="#78B884",
        primary_dark="#4E945D",
        on_primary="#FFFFFF",
        soft="#EDF7EF",
        chart_fill="#C2E5C7",
        chart_line="#5CA372",
        # Exact 5 color-coded pastel weeks from spec!
        week_head=["#F8D7E8", "#E2D7F8", "#D7EAF8", "#D7F8E5", "#FAF2CC"],
        week_tint=["#FDF0F7", "#F4F0FD", "#EFF7FD", "#EFFDF5", "#FDFBE9"],
        week_check=["#D87AA8", "#9378D8", "#65A6D8", "#5BB885", "#D6B442"],
        week_on=["#6D3B55", "#4B3B73", "#2F5675", "#2B6144", "#6B5A20"],
        streak_lo="#EFFAF2",
        streak_mid="#9ED9AE",
        streak_hi="#4E9F76",
        bar="#78B884",
        donut_rest="#E7F2E9",
        weekday_style="letter",
        chart_markers=True,
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
    wb = xlsxwriter.Workbook(str(path))
    styles = Styles(wb, theme)
    build_guide(wb, styles, "🌵 Monthly Tracker", [
        ("📝 Reflection & Notes", "Đánh giá thành tựu, thử thách, thói quen đã vào guồng & bảng check-in 5 tuần pastel."),
    ], offline_sprites=offline)

    ws = wb.add_worksheet("🌵 Monthly Tracker")
    cv = Canvas(wb, ws, styles, "🌵 Monthly Tracker")
    tr = build_tracker(wb, cv, TrackerSpec(
        sheet="🌵 Monthly Tracker", habits=habits, month="October", year=2026, seed=22,
        label_tag="MONTHLY HABIT TRACKER", garden_label="CACTUS GARDEN",
        grown_label="THIS MONTH,\nYOU HAVE GROWN:",
        right_labels=("GOAL", "DAYS\nCOMPLETE", "% DONE", "CURRENT\nSTREAK", "LONGEST\nSTREAK"),
        offline_sprites=offline,
    ))
    add_cactus_weekly_strip(wb, cv, tr)
    cv.flush()
    build_reflection_notes_sheet(wb, styles, tr)
    if offline:
        attach_offline_sprites_sheet(wb, theme.slug, ASSETS_DIR)
    wb.close()


# =========================================================================== #
#  3. RAINBOW EXECUTIVE DONUTS (Ref 3)
# =========================================================================== #
def make_rainbow(path: Path, offline: bool = False):
    theme = Theme(
        slug="lotus_stars",
        name="RAINBOW EXECUTIVE DONUTS",
        emoji="🌈",
        tagline_vi="Dashboard đa sắc pastel với 5 biểu đồ Donut theo tuần, lọ sao phát sáng & danh sách thói quen tuần.",
        font="Segoe UI",
        font_title="Segoe UI Semibold",
        font_month="Segoe UI Semibold",
        page="#F8F8FC",
        card="#FFFFFF",
        ink="#3D3C4E",
        muted="#8A88A0",
        line="#E4E2F0",
        primary="#9E9AD1",
        primary_dark="#6E69A8",
        on_primary="#FFFFFF",
        soft="#EFEEF9",
        chart_fill="#D7D5EE",
        chart_line="#8985C2",
        # Ref 3 Pastel Rainbow: Ice Blue, Sage Mint, Rose Pink, Peach Apricot, Soft Olive!
        week_head=["#C7E5F5", "#C8EDD5", "#FAD3E4", "#FCE2B8", "#D9E8B8"],
        week_tint=["#EEF8FD", "#EFFBF3", "#FEF2F7", "#FEF7EB", "#F4F9E9"],
        week_check=["#5BA7CE", "#5CC084", "#E07AA8", "#E6A646", "#8BB34D"],
        week_on=["#2A5670", "#2A6343", "#7A3656", "#785319", "#476022"],
        streak_lo="#F0F8FC",
        streak_mid="#A9D7EE",
        streak_hi="#5B9EC4",
        bar="#B3AFE0",
        donut_rest="#ECEBF6",
        weekday_style="letter",
        chart_title="DAILY PROGRESS",
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
    wb = xlsxwriter.Workbook(str(path))
    styles = Styles(wb, theme)
    build_guide(wb, styles, "🌈 Habit Dashboard", [
        ("📈 Analytics", "Bảng xếp hạng từng thói quen (Leaderboard) & phân tích hiệu suất theo Thứ trong tuần (Mon–Sun)."),
    ], offline_sprites=offline)

    ws = wb.add_worksheet("🌈 Habit Dashboard")
    cv = Canvas(wb, ws, styles, "🌈 Habit Dashboard")
    tr = build_tracker(wb, cv, TrackerSpec(
        sheet="🌈 Habit Dashboard", habits=habits, month="October", year=2026, seed=33,
        label_tag="HABIT TRACKER", garden_label="STAR JAR GARDEN",
        grown_label="FULL STAR JARS\nTHIS MONTH:", offline_sprites=offline,
    ))
    add_rainbow_bottom_blocks(wb, cv, tr)
    cv.flush()
    build_rainbow_analytics_sheet(wb, styles, tr)
    if offline:
        attach_offline_sprites_sheet(wb, theme.slug, ASSETS_DIR)
    wb.close()


# =========================================================================== #
#  4. SAGE BOTANICAL HABIT & BUDGET (Ref 5)
# =========================================================================== #
def make_botanical(path: Path, offline: bool = False):
    theme = Theme(
        slug="botanical",
        name="SAGE BOTANICAL HABIT & BUDGET",
        emoji="🌿",
        tagline_vi="Sống xanh & quản lý tài chính tinh gọn — kết hợp thói quen lành mạnh với dòng tiền cá nhân.",
        font="Segoe UI",
        font_title="Segoe UI Semibold",
        font_month="Georgia",
        page="#FAF9F6",
        card="#FFFFFF",
        ink="#3A4A42",
        muted="#82928A",
        line="#E3E6DF",
        primary="#9FB8AD",
        primary_dark="#638375",
        on_primary="#FFFFFF",
        soft="#EDF3F0",
        chart_fill="#C7D9D1",
        chart_line="#6E9484",
        week_head=["#9FB8AD", "#B5C9BF", "#E8D5B7", "#E0A899", "#A8BFA8"],
        week_tint=["#EFF5F2", "#F3F8F5", "#FAF5EC", "#FAF0ED", "#F1F6F1"],
        week_check=["#6C9282", "#7EA393", "#B99A6B", "#C87D6C", "#749674"],
        week_on=["#FFFFFF", "#3A4A42", "#4E4029", "#FFFFFF", "#FFFFFF"],
        streak_lo="#EFF6F2",
        streak_mid="#A5CBB9",
        streak_hi="#4E8A6E",
        bar="#9FB8AD",
        donut_rest="#EEF2EF",
        chart_title="DAILY HABIT FLOW",
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
    wb = xlsxwriter.Workbook(str(path))
    styles = Styles(wb, theme)
    build_guide(wb, styles, "🌿 Daily Habits", [
        ("💰 Monthly Budget", "Trình quản lý thu chi toàn diện (Cash Flow Donut, Budget vs Actual, Savings Goals, Bills & Transaction Log)."),
        ("🔗 Life Overview", "Dashboard tổng hợp kết nối Tỷ lệ Thói quen % + Tỷ lệ Tiết kiệm % thành điểm Cân bằng Cuộc sống!"),
    ], offline_sprites=offline)

    ws = wb.add_worksheet("🌿 Daily Habits")
    cv = Canvas(wb, ws, styles, "🌿 Daily Habits")
    tr = build_tracker(wb, cv, TrackerSpec(
        sheet="🌿 Daily Habits", habits=habits, month="October", year=2026, seed=44,
        label_tag="BOTANICAL LIVING", garden_label="MONSTERA GARDEN",
        grown_label="PLANTS FLOURISHED\nTHIS MONTH:", offline_sprites=offline,
    ))
    cv.flush()
    b_refs = build_monthly_budget_sheet(wb, styles)
    build_life_overview_sheet(wb, styles, tr, b_refs)
    if offline:
        attach_offline_sprites_sheet(wb, theme.slug, ASSETS_DIR)
    wb.close()


# =========================================================================== #
#  5. LAVENDER DREAM WELLNESS & MOOD
# =========================================================================== #
def make_lavender(path: Path, offline: bool = False):
    theme = Theme(
        slug="lavender_moon",
        name="LAVENDER DREAM WELLNESS & MOOD",
        emoji="🌙",
        tagline_vi="Chăm sóc thân – tâm – trí nhẹ nhàng với chu kỳ mặt trăng, nhật ký giấc ngủ, tâm trạng & lòng biết ơn.",
        font="Segoe UI",
        font_title="Segoe UI Semibold",
        font_month="Segoe Script",
        page="#F9F7FD",
        card="#FFFFFF",
        ink="#2D2A32",
        muted="#8A8299",
        line="#E6DEF5",
        primary="#A594F9",
        primary_dark="#7663D9",
        on_primary="#FFFFFF",
        soft="#F3EFFB",
        chart_fill="#D7C8F5",
        chart_line="#8E7CE8",
        week_head=["#C8B6E2", "#B9A7EA", "#A594F9", "#C5B4EE", "#DACDF2"],
        week_tint=["#F6F2FB", "#F4F0FC", "#F1EEFE", "#F5F2FC", "#F8F5FD"],
        week_check=["#967CC4", "#8872D8", "#7663D9", "#947ED4", "#A993D8"],
        week_on=["#3B2E52", "#FFFFFF", "#FFFFFF", "#3B2E52", "#3B2E52"],
        streak_lo="#F4F0FC",
        streak_mid="#C2B1F2",
        streak_hi="#7B66DB",
        bar="#B5A4F5",
        donut_rest="#EFEAF9",
        chart_title="DAILY WELLNESS & HABIT FLOW",
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
    wb = xlsxwriter.Workbook(str(path))
    styles = Styles(wb, theme)
    build_guide(wb, styles, "🌙 Habit & Wellness", [
        ("✨ Gratitude & Review", "Nhật ký 31 ngày biết ơn, khoảnh khắc đẹp, bộ đếm Self-care & tổng kết sức khỏe tinh thần."),
    ], offline_sprites=offline)

    ws = wb.add_worksheet("🌙 Habit & Wellness")
    cv = Canvas(wb, ws, styles, "🌙 Habit & Wellness")
    tr = build_tracker(wb, cv, TrackerSpec(
        sheet="🌙 Habit & Wellness", habits=habits, month="October", year=2026, seed=55,
        label_tag="WELLNESS & MOOD", garden_label="MOON & LAVENDER",
        grown_label="FULL MOONS\nTHIS MONTH:", offline_sprites=offline,
    ))
    well_refs = add_wellness_mood_block(wb, cv, tr, seed=55)
    cv.flush()
    build_gratitude_sheet(wb, styles, tr, well_refs)
    if offline:
        attach_offline_sprites_sheet(wb, theme.slug, ASSETS_DIR)
    wb.close()


# =========================================================================== #
#  6. MIDNIGHT NAVY BLUSH FOCUS (Ref 4)
# =========================================================================== #
def make_focus(path: Path, offline: bool = False):
    theme = Theme(
        slug="focus_rocket",
        name="MIDNIGHT NAVY BLUSH FOCUS",
        emoji="🚀",
        tagline_vi="Phong cách tương phản Navy – Blush sắc nét dành cho Deep Work, Coding & Gym với hệ thống tích điểm XP & thăng hạng!",
        font="Segoe UI",
        font_title="Segoe UI Semibold",
        font_month="Segoe UI Semibold",
        page="#F7F8FB",
        card="#FFFFFF",
        ink="#2B3452",
        muted="#727D9E",
        line="#DDE1EE",
        primary="#2B3452",
        primary_dark="#1D243B",
        on_primary="#FFFFFF",
        soft="#F2D7D9",
        chart_fill="#F2D7D9",
        chart_line="#2B3452",
        week_head=["#2B3452", "#3B476E", "#4D5B87", "#5C6B9C", "#7180B0"],
        week_tint=["#FAF1F2", "#F7F3F7", "#F2F4FA", "#F5F6FB", "#F8F3F5"],
        week_check=["#2B3452", "#3B476E", "#4D5B87", "#5C6B9C", "#C47D88"],
        week_on=["#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF"],
        streak_lo="#FAF1F2",
        streak_mid="#E4B7BD",
        streak_hi="#2B3452",
        bar="#E5A9B0",
        donut_rest="#EEF0F7",
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
    wb = xlsxwriter.Workbook(str(path))
    styles = Styles(wb, theme)
    build_guide(wb, styles, "🚀 Focus Tracker", [
        ("🏆 Milestones", "Hệ thống thăng hạng XP (Beginner → Master), 10 Huy hiệu thành tích tự mở khóa & biểu đồ XP!"),
    ], offline_sprites=offline)

    ws = wb.add_worksheet("🚀 Focus Tracker")
    cv = Canvas(wb, ws, styles, "🚀 Focus Tracker")
    tr = build_tracker(wb, cv, TrackerSpec(
        sheet="🚀 Focus Tracker", habits=habits, month="October", year=2026, seed=66,
        label_tag="FOCUS TRACKER PRO", garden_label="LAUNCH PAD",
        grown_label="ORBIT DAYS\nTHIS MONTH:",
        top_right="custom", extra_cols=extra_cols, offline_sprites=offline,
    ))
    xp_col = tr.right_cols["xp_tot"]
    total_xp_local = acell(R_TOT, xp_col)
    add_focus_rank_top_card(wb, cv, tr, total_xp_local)
    cv.flush()
    build_milestones_sheet(wb, styles, tr, f"{tr.q}!{total_xp_local}", xp_col)
    if offline:
        attach_offline_sprites_sheet(wb, theme.slug, ASSETS_DIR)
    wb.close()


BUILDERS = [
    ("01_Sunflower_Garden_Blush", make_sunflower),
    ("02_Cactus_Bloom_Pastel_Weeks", make_cactus),
    ("03_Rainbow_Executive_Donuts", make_rainbow),
    ("04_Sage_Botanical_Habit_And_Budget", make_botanical),
    ("05_Lavender_Dream_Wellness_Mood", make_lavender),
    ("06_Midnight_Navy_Blush_Focus", make_focus),
]


def main():
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    PRO_DIR.mkdir(parents=True, exist_ok=True)
    print("Building 6 Universal Excel 365 / Google Sheets templates...")
    for stem, fn in BUILDERS:
        out = TEMPLATES_DIR / f"{stem}.xlsx"
        fn(out, offline=False)
        print(f"  ✓ {out.relative_to(ROOT)}  ({out.stat().st_size / 1024:.1f} KB)")
    print("Building 6 Offline Pro Showcase Editions (embedded sprites, zero-internet)...")
    for stem, fn in BUILDERS:
        out = PRO_DIR / f"{stem}_Offline_Pro.xlsx"
        fn(out, offline=True)
        print(f"  ✓ {out.relative_to(ROOT)}  ({out.stat().st_size / 1024:.1f} KB)")
    print("All 12 workbooks built successfully!")


if __name__ == "__main__":
    main()
