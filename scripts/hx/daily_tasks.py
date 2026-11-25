"""
hx.daily_tasks — Pillar 1 (v3.0): `📝 Nhiệm Vụ Ngày` (Daily One-Off Tasks Planner)
with interactive Date Picker (Day/Month/Year), 20 pre-wired rows (6 realistic sample tasks
for default date 21/10/2026 + 14 blank expansion rows), Priority pill Conditional Formatting,
Live Daily Hero Growth Animation (`Anim_DailyTaskHero`), Priority Breakdown, and
Quick Daily Highlight Note persisted per date (`YYYY-MM-DD`) in `_Database`!
"""
from __future__ import annotations

from .core import (Canvas, Styles, acell, cell, colname, donut, place_chart, qs, rng,
                   checked_pastel_bg)
from .tracker import (CALC_SHEET, CALC_STATE_VAL_COL, CALC_CHK_COL,
                      month_lookup_ref, year_lookup_ref, stage6_formula)

DAILY_TASKS_SHEET = "📝 Nhiệm Vụ Ngày"
ASSETS_SHEET = "_Assets"

DEFAULT_TASK_DAY = 21
DEFAULT_TASK_MONTH = "October"
DEFAULT_TASK_MONTH_NUM = 10
DEFAULT_TASK_YEAR = 2026
DEFAULT_TASK_KEY = "2026-10-21"

TASK_CATEGORIES = ["Công việc", "Học tập", "Cá nhân", "Sức khỏe"]
TASK_PRIORITIES = ["🔴 Cao", "🟡 Trung bình", "🟢 Thấp"]

DEFAULT_DAILY_TASKS = [
    (True,  "Gửi báo cáo tiến độ tuần cho quản lý",       "Công việc", "🔴 Cao",        "Đính kèm file số liệu & biểu đồ cập nhật"),
    (True,  "Đóng tiền điện, nước & Internet tháng 10",   "Cá nhân",   "🔴 Cao",        "Thanh toán qua app ngân hàng trước 17h"),
    (True,  "Ôn tập 30 từ vựng chuyên ngành & làm quiz",  "Học tập",   "🟡 Trung bình", "Ghi chú lại 5 mẫu câu hay áp dụng ngay"),
    (True,  "Đặt lịch khám nha khoa định kỳ cuối tuần",   "Sức khỏe",  "🟡 Trung bình", "Gọi phòng khám chọn khung 9h sáng Thứ Bảy"),
    (False, "Mua quà sinh nhật & viết thiệp tặng bạn",    "Cá nhân",   "🟡 Trung bình", "Ghé tiệm sách hoặc đặt giao nhanh buổi tối"),
    (False, "Dọn gọn thư mục Downloads & sao lưu Drive",  "Công việc", "🟢 Thấp",       "Sắp xếp theo tháng, xóa file tạm nặng máy"),
]
DEFAULT_DAILY_HIGHLIGHT = (
    "Hôm nay xử lý gọn các đầu việc quan trọng trước 16h — dành buổi tối thư giãn & nạp lại năng lượng!"
)

# _Calc lookup ranges for Daily Tasks (placed cleanly in Col AL = 37, rows 5..45)
def day_num_lookup_ref() -> str:
    return f"{qs(CALC_SHEET)}!{rng(5, CALC_CHK_COL, 35, CALC_CHK_COL)}"    # _Calc!$AL$6:$AL$36


def task_cat_lookup_ref() -> str:
    return f"{qs(CALC_SHEET)}!{rng(37, CALC_CHK_COL, 40, CALC_CHK_COL)}"   # _Calc!$AL$38:$AL$41


def task_prio_lookup_ref() -> str:
    return f"{qs(CALC_SHEET)}!{rng(42, CALC_CHK_COL, 44, CALC_CHK_COL)}"   # _Calc!$AL$43:$AL$45


def build_daily_tasks_sheet(
    wb,
    styles: Styles,
    ws_calc,
    *,
    universal: bool = True,
    gsheets: bool = False,
    pro_mode: bool = False,
) -> dict:
    """Build the unified themed `📝 Nhiệm Vụ Ngày` sheet for ALL 31 templates."""
    name = DAILY_TASKS_SHEET
    t = styles.t
    ws = wb.add_worksheet(name)
    cv = Canvas(wb, ws, styles, name, universal=universal, gsheets=gsheets)
    q = qs(name)
    cq = qs(CALC_SHEET)

    # Geometry: Col A(2.2) | B(6.2 chk) | C(42.0 task) | D(17.5 cat) | E(17.0 prio) | F(31.0 note) | G(2.2 gap) | H(31.0 sidebar) | I(2.2)
    cv.col(0, 2.2)
    cv.col(1, 6.2)
    cv.col(2, 42.0)
    cv.col(3, 17.5)
    cv.col(4, 17.0)
    cv.col(5, 31.0)
    cv.col(6, 2.2)
    cv.col(7, 31.0)
    cv.col(8, 2.2)

    cv.row(0, 10)
    cv.row(1, 30)   # Banner
    cv.row(2, 8)    # Spacer
    cv.row(3, 20)   # Date Picker labels
    cv.row(4, 30)   # Date Picker dropdown values (D5, E5, F5) + Formatted Weekday (B5:C5)
    cv.row(5, 19)   # Cue line
    cv.row(6, 10)   # Spacer
    cv.row(7, 26)   # Table Header (Row 8)

    # Wire live Daily Tasks formulas onto _Calc!AN12:AN18 (rows 11..17, col AN = 39)
    # Row 11 (AN12): LastTaskDateKey ("2026-10-21") — already initialized in init_calc_sheet
    dt_done_ref = f"{cq}!{acell(12, CALC_STATE_VAL_COL)}"     # _Calc!$AN$13
    dt_tot_ref = f"{cq}!{acell(13, CALC_STATE_VAL_COL)}"      # _Calc!$AN$14
    dt_pct_ref = f"{cq}!{acell(14, CALC_STATE_VAL_COL)}"      # _Calc!$AN$15
    dt_stage_ref = f"{cq}!{acell(15, CALC_STATE_VAL_COL)}"    # _Calc!$AN$16

    r0 = 8        # 0-based row 8 -> Excel Row 9
    n_rows = 20   # Excel Rows 9..28
    chk_rng_q = f"{q}!{rng(r0, 1, r0 + n_rows - 1, 1)}"
    task_rng_q = f"{q}!{rng(r0, 2, r0 + n_rows - 1, 2)}"
    prio_rng_q = f"{q}!{rng(r0, 4, r0 + n_rows - 1, 4)}"

    ws_calc.write_formula(12, CALC_STATE_VAL_COL, f'=COUNTIFS({task_rng_q},"?*",{chk_rng_q},TRUE)')
    ws_calc.write_formula(13, CALC_STATE_VAL_COL, f'=COUNTIF({task_rng_q},"?*")')
    ws_calc.write_formula(14, CALC_STATE_VAL_COL, f"=IFERROR({acell(12, CALC_STATE_VAL_COL)}/{acell(13, CALC_STATE_VAL_COL)},0)")
    ws_calc.write_formula(15, CALC_STATE_VAL_COL, stage6_formula(acell(14, CALC_STATE_VAL_COL), t.num_stages))
    ws_calc.write_formula(16, CALC_STATE_VAL_COL, f"={acell(14, CALC_STATE_VAL_COL)}")
    ws_calc.write_formula(17, CALC_STATE_VAL_COL, f"=1-{acell(14, CALC_STATE_VAL_COL)}")

    # ------------------------------------------------------------------ TOP BANNER & DATE PICKER
    cv.merge(1, 1, 1, 5, f"{t.emoji}  NHIỆM VỤ TRONG NGÀY  •  DAILY ONE-OFF TASKS",
             font_name=t.font_title, font_size=14.5, bold=True, align="center",
             bg_color=t.primary, font_color=t.on_primary)
    cv.box(1, 1, 1, 5, t.line)

    # Date Picker Card (Rows 4..6, Cols B..F)
    cv.merge(3, 1, 3, 2, "📆  NGÀY ĐANG XEM (TỰ ĐỘNG THEO LỊCH)", bold=True, font_size=8.5,
             align="center", bg_color=t.soft, font_color=t.ink)
    cv.put(3, 3, "NGÀY (DAY)", bold=True, font_size=8.5, align="center", bg_color=t.soft, font_color=t.ink)
    cv.put(3, 4, "THÁNG (MONTH)", bold=True, font_size=8.5, align="center", bg_color=t.soft, font_color=t.ink)
    cv.put(3, 5, "NĂM (YEAR)", bold=True, font_size=8.5, align="center", bg_color=t.soft, font_color=t.ink)

    # Safe date expression clamping D5 to last day of selected month/year
    m_expr = f"IFERROR(MATCH($E$5,{month_lookup_ref()},0),1)"
    d_safe = f"MIN(IFERROR(--$D$5,1),DAY(EOMONTH(DATE($F$5,{m_expr},1),0)))"
    dt_expr = f"DATE($F$5,{m_expr},{d_safe})"
    wd_formula = (
        f'=CHOOSE(WEEKDAY({dt_expr},2),"Thứ Hai","Thứ Ba","Thứ Tư","Thứ Năm","Thứ Sáu","Thứ Bảy","Chủ Nhật")'
        f'&", "&TEXT({dt_expr},"dd/mm/yyyy")'
    )
    cv.merge(4, 1, 4, 2, wd_formula, font_name=t.font_title, font_size=13, bold=True, align="center",
             bg_color=t.card, font_color=t.primary_dark)
    cv.put(4, 3, DEFAULT_TASK_DAY, font_name=t.font_title, font_size=13, bold=True, align="center",
           num_format="0", bg_color=t.soft, font_color=t.ink,
           top=1, top_color=t.primary, bottom=1, bottom_color=t.primary,
           left=1, left_color=t.primary, right=1, right_color=t.primary)
    cv.put(4, 4, DEFAULT_TASK_MONTH, font_name=t.font_title, font_size=12.5, bold=True, align="center",
           bg_color=t.soft, font_color=t.ink,
           top=1, top_color=t.primary, bottom=1, bottom_color=t.primary,
           left=1, left_color=t.primary, right=1, right_color=t.primary)
    cv.put(4, 5, DEFAULT_TASK_YEAR, font_name=t.font_title, font_size=13, bold=True, align="center",
           num_format="0", bg_color=t.soft, font_color=t.ink,
           top=1, top_color=t.primary, bottom=1, bottom_color=t.primary,
           left=1, left_color=t.primary, right=1, right_color=t.primary)

    if pro_mode:
        cv.row(5, 28)
        cv.merge(5, 1, 5, 2, "⚡  Chuyển ngày nhanh & tự lưu vào _Database:", italic=True,
                 font_size=8.6, align="right", bg_color=t.card, font_color=t.muted)
        cv.merge(5, 3, 5, 5, "", align="center", bg_color=t.card)
    else:
        cue_txt = (
            "💡  Google Sheets: Chạy setupHabitTracker() 1 lần để bật Checkbox & tự lưu nhiệm vụ theo từng ngày!"
            if gsheets else
            "📌  Bản Không Macro (Excel 2016–365) • Tick xong việc để xem hoạt ảnh lớn dần — Dùng bản Pro (.xlsm) để tự lưu nhiều ngày!"
        )
        cv.merge(5, 1, 5, 5, cue_txt, italic=True, font_size=8.5, align="center", bg_color=t.card, font_color=t.muted)
    cv.grid(3, 1, 4, 5, t.line)
    cv.box(3, 1, 5, 5, t.line)

    # Date Picker Data Validations
    ws.data_validation("D5", {"validate": "list", "source": f"={day_num_lookup_ref()}",
                              "input_title": "Chọn Ngày (1–31)",
                              "input_message": "Chọn ngày cần lập danh sách nhiệm vụ đột xuất!"})
    ws.data_validation("E5", {"validate": "list", "source": f"={month_lookup_ref()}",
                              "input_title": "Chọn Tháng (Month)",
                              "input_message": "Chọn tháng (January–December)"})
    ws.data_validation("F5", {"validate": "list", "source": f"={year_lookup_ref()}",
                              "input_title": "Chọn Năm (Year)",
                              "input_message": "Chọn năm (2024–2040)"})

    # ------------------------------------------------------------------ 20-ROW DAILY TASKS TABLE
    hdrs = [
        (1, "✓", "center"),
        (2, "TÊN NHIỆM VỤ  •  VIỆC ĐỘT XUẤT TRONG NGÀY", "left"),
        (3, "PHÂN LOẠI", "center"),
        (4, "ĐỘ ƯU TIÊN", "center"),
        (5, "GHI CHÚ CHI TIẾT", "left"),
    ]
    for c_i, lab, al in hdrs:
        cv.put(7, c_i, lab, bold=True, font_size=9.5, align=al,
               indent=(1 if al == "left" else None),
               bg_color=t.primary, font_color=t.on_primary)

    for i in range(n_rows):
        rr = r0 + i
        cv.row(rr, 28 if i < len(DEFAULT_DAILY_TASKS) else 25)
        bg = t.card if i % 2 == 0 else t.page
        if i < len(DEFAULT_DAILY_TASKS):
            done, task_nm, cat, prio, note = DEFAULT_DAILY_TASKS[i]
        else:
            done, task_nm, cat, prio, note = False, "", "", "", ""
        cv.checkbox(rr, 1, done, align="center", font_size=12, font_color=t.primary_dark, bg_color=bg)
        # Col C (Task Name): ALWAYS BOLD 10pt + indent=1 (including blank user-input rows!)
        cv.put(rr, 2, task_nm, bold=True, font_size=10, align="left", indent=1, text_wrap=True,
               bg_color=bg, font_color=t.ink)
        # Col D (Category): Centered regular 9.5pt
        cv.put(rr, 3, cat, bold=False, font_size=9.5, align="center", bg_color=bg, font_color=t.ink)
        # Col E (Priority): Centered bold 9pt (styled with pastel pills via CF)
        cv.put(rr, 4, prio, bold=True, font_size=9, align="center", bg_color=bg, font_color=t.ink)
        # Col F (Notes): ALWAYS REGULAR 9.5pt + indent=1
        cv.put(rr, 5, note, bold=False, font_size=9.5, align="left", indent=1, text_wrap=True,
               bg_color=bg, font_color=t.muted)

    cv.grid(7, 1, r0 + n_rows - 1, 5, t.line)
    cv.box(7, 1, r0 + n_rows - 1, 5, t.line)

    # Dropdowns for Category (D9:D28) & Priority (E9:E28)
    cat_rng = rng(r0, 3, r0 + n_rows - 1, 3)
    prio_rng = rng(r0, 4, r0 + n_rows - 1, 4)
    ws.data_validation(cat_rng, {"validate": "list", "source": f"={task_cat_lookup_ref()}",
                                 "input_title": "Phân loại nhiệm vụ",
                                 "input_message": "Chọn nhóm: Công việc / Học tập / Cá nhân / Sức khỏe"})
    ws.data_validation(prio_rng, {"validate": "list", "source": f"={task_prio_lookup_ref()}",
                                  "input_title": "Độ ưu tiên",
                                  "input_message": "Chọn mức ưu tiên: 🔴 Cao / 🟡 Trung bình / 🟢 Thấp"})

    # Conditional Formatting:
    # 1) Checked checkbox cell pastel highlight (B9:B28)
    chk_rng_rel = rng(r0, 1, r0 + n_rows - 1, 1, absolute=False)
    ws.conditional_format(chk_rng_rel, {
        "type": "formula", "criteria": f"=B{r0 + 1}=TRUE",
        "format": wb.add_format({"bg_color": checked_pastel_bg(t.primary, t.soft),
                                 "font_color": t.primary_dark, "bold": True}),
    })
    # 2) Checked task name strikethrough & soft muted tint (C9:C28)
    task_rng_rel = rng(r0, 2, r0 + n_rows - 1, 2, absolute=False)
    ws.conditional_format(task_rng_rel, {
        "type": "formula", "criteria": f"=$B{r0 + 1}=TRUE",
        "format": wb.add_format({"font_strikeout": True, "font_color": t.muted, "bg_color": t.soft}),
    })
    # 3) Priority soft pill Conditional Formatting (E9:E28)
    prio_rel = rng(r0, 4, r0 + n_rows - 1, 4, absolute=False)
    ws.conditional_format(prio_rel, {
        "type": "formula", "criteria": f'=E{r0 + 1}="🔴 Cao"',
        "format": wb.add_format({"bg_color": "#FEE2E2", "font_color": "#991B1B", "bold": True}),
    })
    ws.conditional_format(prio_rel, {
        "type": "formula", "criteria": f'=E{r0 + 1}="🟡 Trung bình"',
        "format": wb.add_format({"bg_color": "#FEF3C7", "font_color": "#92400E", "bold": True}),
    })
    ws.conditional_format(prio_rel, {
        "type": "formula", "criteria": f'=E{r0 + 1}="🟢 Thấp"',
        "format": wb.add_format({"bg_color": "#DCFCE7", "font_color": "#166534", "bold": True}),
    })

    # ------------------------------------------------------------------ QUICK DAILY HIGHLIGHT NOTE (Rows 30..33)
    r_note0 = r0 + n_rows + 1  # 0-based 29 -> Excel Row 30
    cv.row(r_note0 - 1, 10)
    cv.row(r_note0, 24)
    cv.row(r_note0 + 1, 24)
    cv.row(r_note0 + 2, 24)
    cv.row(r_note0 + 3, 24)
    cv.row(r_note0 + 4, 10)

    cv.merge(r_note0, 1, r_note0, 5, "✨  ĐIỂM SÁNG & GHI CHÚ TRONG NGÀY  •  HIGHLIGHT OF THE DAY",
             bold=True, font_size=9.5, align="left", indent=1, bg_color=t.primary, font_color=t.on_primary)
    # Merged editable cell anchored at B31 (0-based row 30, col 1)!
    cv.merge(r_note0 + 1, 1, r_note0 + 3, 5, DEFAULT_DAILY_HIGHLIGHT, bold=False, font_size=10,
             align="left", indent=1, text_wrap=True, bg_color=t.card, font_color=t.ink)
    cv.box(r_note0, 1, r_note0 + 3, 5, t.line)

    # ------------------------------------------------------------------ RIGHT SIDEBAR (COL H = 7): LIVE HERO + DONUT + PRIORITY
    # Card 1 (Rows 2..19, Col H): DAILY HERO GROWTH ANIMATION & PROGRESS
    cv.put(1, 7, f"{t.emoji}  TIẾN ĐỘ NHIỆM VỤ NGÀY", bold=True, font_size=10.5, align="center",
           bg_color=t.primary, font_color=t.on_primary)

    # Donut chart in rows 3..7 (0-based 2..6? Wait: row 2 is 8pt spacer, let's use rows 3..7 = 0-based 3..7!)
    cv.merge(3, 7, 7, 7, f"={dt_pct_ref}", font_name=t.font_title, font_size=20, bold=True,
             align="center", num_format="0%", bg_color=t.card, font_color=t.primary_dark)
    d_dt = donut(wb, f"={cq}!{rng(16, CALC_STATE_VAL_COL, 17, CALC_STATE_VAL_COL)}",
                 [t.primary, t.donut_rest], hole=68, name="DailyTasksDonut")
    place_chart(cv, d_dt, 3, 7, 7, 7, pad_x=12, pad_y=3)

    cv.put(8, 7, f'="✓ Hoàn thành: "&{dt_done_ref}&" / "&{dt_tot_ref}&" việc"',
           bold=True, font_size=10, align="center", bg_color=t.soft, font_color=t.ink)

    # Large Dynamic 6-Stage Growth Sprite box: rows 10..17 (0-based 9..16)
    hero_box = (9, 7, 16, 7)
    dyn_anims = []
    if universal:
        cv.merge(*hero_box, "", align="center", bg_color=t.card)
        dyn_anims.append({
            "name": "Anim_DailyTaskHero",
            "refers_to": f"=INDEX({ASSETS_SHEET}!{t.assets_range},{dt_stage_ref})",
            "sheet": name, "r1": 9, "c1": 7, "r2": 16, "c2": 7,
            "align_bottom": False,
        })
    else:
        cv.merge(*hero_box,
                 f"=INDEX(_Assets!{t.assets_range},{dt_stage_ref})",
                 align="center", bg_color=t.card)

    cv.merge(17, 7, 18, 7,
             f'=IF({dt_tot_ref}=0,"🌱 Gõ nhiệm vụ để bắt đầu ngày mới!",'
             f'IF({dt_pct_ref}>=0.999,"🎉 Xuất sắc! Đã hoàn thành 100% việc hôm nay!",'
             f'IF({dt_pct_ref}>=0.75,"✨ Tuyệt vời! Sắp chạm đích 100% rồi!",'
             f'IF({dt_pct_ref}>=0.5,"🔥 Đã đi quá nửa chặng đường!","💪 Cố lên, hoàn thành từng việc một!"))))',
             bold=True, font_size=9.2, align="center", text_wrap=True, bg_color=t.soft, font_color=t.ink)
    ws.conditional_format("H18:H19", {
        "type": "formula", "criteria": f"=AND({dt_tot_ref}>0,{dt_pct_ref}>=0.999)",
        "format": wb.add_format({"bg_color": "#DCFCE7", "font_color": "#166534", "bold": True}),
        "stop_if_true": True,
    })
    ws.conditional_format("H18:H19", {
        "type": "formula", "criteria": f"=AND({dt_tot_ref}>0,{dt_pct_ref}>=0.75)",
        "format": wb.add_format({"bg_color": "#FEF3C7", "font_color": "#92400E", "bold": True}),
        "stop_if_true": True,
    })
    ws.conditional_format("H18:H19", {
        "type": "formula", "criteria": f"={dt_tot_ref}=0",
        "format": wb.add_format({"bg_color": t.card, "font_color": t.muted, "bold": False}),
    })
    cv.box(1, 7, 18, 7, t.line)

    # Card 2 (Rows 21..26, Col H): PRIORITY BREAKDOWN LIVE KPI
    cv.put(20, 7, "🎯  PHÂN BỔ ĐỘ ƯU TIÊN HÔM NAY", bold=True, font_size=9.5, align="center",
           bg_color=t.primary, font_color=t.on_primary)
    prio_stats = [
        (21, "🔴 Cao",        "#FEE2E2", "#991B1B"),
        (22, "🟡 Trung bình", "#FEF3C7", "#92400E"),
        (23, "🟢 Thấp",       "#DCFCE7", "#166534"),
    ]
    for rr_p, p_lbl, p_bg, p_fg in prio_stats:
        cv.put(
            rr_p, 7,
            f'="{p_lbl}:  "&COUNTIFS({task_rng_q},"?*",{prio_rng_q},"{p_lbl}",{chk_rng_q},TRUE)&" / "&'
            f'COUNTIFS({task_rng_q},"?*",{prio_rng_q},"{p_lbl}")&" xong"',
            bold=True, font_size=9.5, align="left", indent=1, bg_color=p_bg, font_color=p_fg,
        )
        cv.hline(rr_p, 7, 7, t.line)
    cv.put(24, 7, f'="⏳ Còn lại chưa xong: "&({dt_tot_ref}-{dt_done_ref})&" việc"',
           bold=True, font_size=9.5, align="center", bg_color=t.card, font_color=t.primary_dark)
    cv.box(20, 7, 24, 7, t.line)

    # Card 3 (Rows 27..33, Col H): QUICK GUIDE CARD
    cv.put(26, 7, "💡  MẸO DÙNG NHIỆM VỤ NGÀY", bold=True, font_size=9.5, align="center",
           bg_color=t.primary, font_color=t.on_primary)
    tips = [
        "★  Dùng cho việc đột xuất, deadline, lịch hẹn không lặp lại hằng ngày.",
        "★  Chỉ các dòng có tên việc mới tính vào % — dòng trống không làm giảm %!",
        "★  Tick xong việc → tên tự gạch ngang & hoạt ảnh bên trên lớn dần tới 100%!",
    ]
    cv.merge(27, 7, 28, 7, tips[0], font_size=9, align="left", indent=1, text_wrap=True, bg_color=t.card, font_color=t.ink)
    cv.hline(28, 7, 7, t.line)
    cv.merge(29, 7, 30, 7, tips[1], font_size=9, align="left", indent=1, text_wrap=True, bg_color=t.card, font_color=t.ink)
    cv.hline(30, 7, 7, t.line)
    cv.merge(31, 7, 32, 7, tips[2], font_size=9, align="left", indent=1, text_wrap=True, bg_color=t.card, font_color=t.ink)
    cv.box(26, 7, 32, 7, t.line)

    # Define Pure-ASCII Named Anchor for VBA (`ANCHOR_DAILYTASKS`)
    wb.define_name("ANCHOR_DAILYTASKS", f"={q}!$D$5")

    cv.flush()
    ws.hide_gridlines(2)
    ws.set_zoom(90)
    ws.set_tab_color(t.primary)
    ws.set_landscape()
    ws.set_paper(9)
    ws.fit_to_pages(1, 1)
    ws.set_margins(0.3, 0.3, 0.4, 0.4)

    return {
        "sheet": name,
        "checkboxes": {name: cv.form_checkboxes},
        "dyn_anims": dyn_anims,
        "capture_range": "A1:I34",
    }
