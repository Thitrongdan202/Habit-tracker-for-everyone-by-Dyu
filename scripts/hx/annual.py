"""
hx.annual — Version 2.1 unified Yearly Goals, Annual Achievements, _Database & _YearHistory builders.

Harmonizes strictly with EACH template's `Theme` (colors, fonts, emoji, sprites) and wires
ALL dynamic 6-stage hero & monthly growth animations cleanly across all 3 editions:
  - `Anim_YearlyGoals` -> `_Calc!$AN$7`
  - `Anim_AnnualHero`  -> `_Calc!$AN$8`
  - `Anim_AchBadges`   -> `_Calc!$AN$9`
  - `Anim_AnnualM01..M12` -> `_Calc!$AW$2:$AW$13`
"""
from __future__ import annotations

from .core import (Canvas, Styles, acell, cell, colname, qs, rng, donut,
                   place_chart, axis_font, text_lines, MONTHS_EN, checked_pastel_bg)
from .tracker import (CALC_SHEET, CALC_STATE_VAL_COL, CALC_ANN_COL0, CALC_ANN_YG_LBL_COL,
                      CALC_ANN_YG_VAL_COL, N_HABITS, Habit, TrackerRefs,
                      stage6_formula, year_lookup_ref, compute_month_summary_py)
from .annual_lore import get_annual_lore
from .daily_tasks import DEFAULT_DAILY_TASKS, DEFAULT_DAILY_HIGHLIGHT, DEFAULT_TASK_KEY

YEARLY_GOALS_SHEET = "🎯 Yearly Goals & Habits"
ANNUAL_SHEET = "🏆 Tổng Kết & Thành Tựu Năm"
DATABASE_SHEET = "_Database"
HISTORY_SHEET = "_YearHistory"
ASSETS_SHEET = "_Assets"

DEFAULT_YEARLY_GOALS = [
    (True,  "Tăng cường sức khỏe thể chất", "Đánh giá lịch tập & chỉ số sức khỏe mỗi tháng",
     "Đi bộ / chạy bộ cuối tuần ít nhất 2 giờ", "Tập thể dục / yoga 30 phút mỗi sáng"),
    (True,  "Chăm sóc sức khỏe tinh thần", "Chấm điểm mức độ stress & hạnh phúc (1–10)",
     "Xem 1 bộ phim truyền cảm hứng / gặp bạn bè", "Viết nhật ký cảm xúc & thiền 10 phút"),
    (True,  "Tự do tài chính & Tiết kiệm", "Lập ngân sách tháng & tiết kiệm ≥ 3 triệu",
     "Kiểm tra tổng chi tiêu mỗi Chủ nhật", "Ghi chép chi tiêu hằng ngày, hạn chế mua bốc đồng"),
    (True,  "Đọc sách & Mở rộng tri thức", "Hoàn thành ít nhất 1 cuốn sách mỗi tháng",
     "Đọc sách tối thiểu 5 ngày / tuần & tóm tắt", "Đọc sách 20 phút mỗi tối trước khi ngủ"),
    (True,  "Uống đủ nước & Ăn lành mạnh", "Biến việc uống nước thành phản xạ tự nhiên",
     "Chuẩn bị rau xanh & meal prep ít nhất 5 bữa", "Uống đủ 2L nước & ăn 1 bữa nhiều rau xanh"),
    (True,  "Ngủ đủ 8 tiếng & Dậy sớm", "Cảm thấy tỉnh táo, không uể oải mỗi sáng",
     "Đạt ít nhất 5 đêm ngủ đủ 7.5–8 tiếng", "Tắt màn hình trước 22h30, đi ngủ trước 23h00"),
    (False, "Hạn chế đồ ăn nhanh & đồ ngọt", "Giảm 70% đồ ăn chế biến sẵn so với tháng trước",
     "Tự nấu ăn ở nhà tối thiểu 5 buổi / tuần", "Ưu tiên thực phẩm tươi, thay trà sữa bằng nước lọc"),
    (False, "Không gian sống gọn gàng", "Tổng vệ sinh 1 khu vực lớn trong nhà mỗi tháng",
     "Giặt giũ, thay ga gối & sắp xếp bàn học", "Dành 10 phút dọn dẹp nhanh (rửa bát, gấp chăn)"),
    (False, "Nâng cao tiếng Anh / Chuyên môn", "Hoàn thành 1 khóa học mini / 1 dự án nhỏ",
     "Luyện nghe nói hoặc viết 3 buổi / tuần", "Học 30 phút mỗi ngày (từ vựng / kỹ năng)"),
    (False, "Viết nhật ký biết ơn", "Đọc lại nhật ký cuối tháng để nhìn thấy sự trưởng thành",
     "Viết ít nhất 4 lần / tuần về 3 điều biết ơn", "Ghi 3 dòng ngắn trước khi đi ngủ"),
]


def _finish_sheet(ws, cv: Canvas, tab_color: str, zoom: int = 88):
    ws.hide_gridlines(2)
    ws.set_zoom(zoom)
    ws.set_tab_color(tab_color)
    ws.set_landscape()
    ws.set_paper(9)
    ws.fit_to_pages(1, 0)
    ws.set_margins(0.3, 0.3, 0.4, 0.4)
    cv.flush()


# =========================================================================== #
#  1. 🎯 Yearly Goals & Habits (Themed for ALL 10 Templates + Year Dropdown + Dynamic Hero!)
# =========================================================================== #
def build_yearly_goals_v21(wb, styles: Styles, ws_calc, year: int = 2026,
                           universal: bool = True, gsheets: bool = False,
                           pro_mode: bool = False) -> dict:
    name = YEARLY_GOALS_SHEET
    t = styles.t
    ws = wb.add_worksheet(name)
    cv = Canvas(wb, ws, styles, name, universal=universal, gsheets=gsheets)
    q = qs(name)
    cq = qs(CALC_SHEET)

    # Cols: 0 gutter | 1 chk | 2 MY GOALS | 3 MONTHLY | 4 WEEKLY | 5 DAILY | 6 gap | 7..8 sidebar | 9 gutter
    cv.col(0, 2.4)
    cv.col(1, 5.2)
    cv.col(2, 31)
    cv.col(3, 31)
    cv.col(4, 31)
    cv.col(5, 31)
    cv.col(6, 2.2)
    cv.col(7, 19)
    cv.col(8, 19)
    cv.col(9, 2.4)

    cv.row(0, 10)
    cv.row(1, 36)   # Title banner + Year selector pill (I2)
    cv.row(2, 10)
    cv.row(3, 26)
    cv.row(4, 24)

    cv.merge(1, 1, 1, 5, f"{t.emoji}  YEARLY GOALS & HABITS PLANNER", font_name=t.font_title,
             font_size=15, bold=True, align="center", bg_color=t.primary, font_color=t.on_primary)
    cv.box(1, 1, 1, 5, t.line)

    # Unmerged Year dropdown pill in H2:I2 (I2 = row 1, col 8 = Excel $I$2!)
    cv.put(1, 7, "📅  NĂM (YEAR):", bold=True, font_size=10, align="center",
           bg_color=t.primary, font_color=t.on_primary)
    cv.put(1, 8, year, font_name=t.font_title, font_size=14, bold=True, align="center",
           num_format="0", bg_color=t.soft, font_color=t.ink,
           top=1, top_color=t.primary_dark, bottom=1, bottom_color=t.primary_dark,
           left=1, left_color=t.primary_dark, right=1, right_color=t.primary_dark)
    cv.box(1, 7, 1, 8, t.line)
    ws.data_validation(acell(1, 8), {
        "validate": "list", "source": f"={year_lookup_ref()}",
        "input_title": "Chọn Năm Mục Tiêu (2024–2040)",
        "input_message": ("Chọn năm → Pro tự lưu mục tiêu năm cũ & tải mục tiêu năm mới!"
                          if pro_mode else "Chọn năm mục tiêu để đồng bộ với tab 🏆 Tổng Kết & Thành Tựu Năm!"),
    })

    cv.merge(3, 1, 4, 2, "MY GOALS • MỤC TIÊU NĂM", bold=True, font_size=10, align="center",
             bg_color=t.primary, font_color=t.on_primary)
    cv.merge(3, 3, 3, 5, "MY HABITS • KẾ HOẠCH HÀNH ĐỘNG", bold=True, font_size=10, align="center",
             bg_color=t.primary, font_color=t.on_primary)
    cv.put(4, 3, "MONTHLY HABITS (Hàng tháng)", bold=True, font_size=9.5, align="center", bg_color=t.soft, font_color=t.ink)
    cv.put(4, 4, "WEEKLY HABITS (Hàng tuần)", bold=True, font_size=9.5, align="center", bg_color=t.soft, font_color=t.ink)
    cv.put(4, 5, "DAILY HABITS (Hàng ngày)", bold=True, font_size=9.5, align="center", bg_color=t.soft, font_color=t.ink)

    r0 = 5
    total_rows = 20
    for i in range(total_rows):
        rr = r0 + i
        if i < len(DEFAULT_YEARLY_GOALS):
            chk, g, m, w, d = DEFAULT_YEARLY_GOALS[i]
            max_l = max(text_lines(g, 28, factor=0.88), text_lines(m, 28, factor=0.88),
                        text_lines(w, 28, factor=0.88), text_lines(d, 28, factor=0.88))
            cv.row(rr, max(38, max_l * 15 + 14))
        else:
            chk, g, m, w, d = False, "", "", "", ""
            cv.row(rr, 26)
        bg = t.card if i % 2 == 0 else t.page
        cv.checkbox(rr, 1, chk, align="center", font_size=12, font_color=t.primary_dark, bg_color=bg)
        # Col C (MY GOALS): ALWAYS BOLD 10pt + indent=1 (including blank user-input expansion rows!)
        cv.put(rr, 2, g, bold=True, font_size=10, align="left", indent=1, text_wrap=True, bg_color=bg, font_color=t.ink)
        # Cols D, E, F (Habits): ALWAYS REGULAR 9.5pt + indent=1 (including blank rows!)
        cv.put(rr, 3, m, bold=False, font_size=9.5, align="left", indent=1, text_wrap=True, bg_color=bg, font_color=t.ink)
        cv.put(rr, 4, w, bold=False, font_size=9.5, align="left", indent=1, text_wrap=True, bg_color=bg, font_color=t.ink)
        cv.put(rr, 5, d, bold=False, font_size=9.5, align="left", indent=1, text_wrap=True, bg_color=bg, font_color=t.ink)

    cv.grid(3, 1, r0 + total_rows - 1, 5, t.line)
    cv.box(3, 1, r0 + total_rows - 1, 5, t.line)

    # Conditional highlight on checked goal rows
    chk_col_rng = rng(r0, 1, r0 + total_rows - 1, 1, absolute=False)
    ws.conditional_format(chk_col_rng, {
        "type": "formula", "criteria": f"=B{r0 + 1}=TRUE",
        "format": wb.add_format({"bg_color": checked_pastel_bg(t.primary, t.soft),
                                 "font_color": t.primary_dark, "bold": True}),
    })

    # Wire LIVE YearlyGoals stats + 6-Stage Hero index onto _Calc!AN4:AN7
    chk_rng_q = f"{q}!{rng(r0, 1, r0 + total_rows - 1, 1)}"
    goal_rng_q = f"{q}!{rng(r0, 2, r0 + total_rows - 1, 2)}"
    yg_done_ref = f"{cq}!{acell(3, CALC_STATE_VAL_COL)}"     # _Calc!$AN$4
    yg_tot_ref = f"{cq}!{acell(4, CALC_STATE_VAL_COL)}"      # _Calc!$AN$5
    yg_pct_ref = f"{cq}!{acell(5, CALC_STATE_VAL_COL)}"      # _Calc!$AN$6
    yg_stage_ref = f"{cq}!{acell(6, CALC_STATE_VAL_COL)}"    # _Calc!$AN$7

    ws_calc.write_formula(3, CALC_STATE_VAL_COL, f'=COUNTIFS({goal_rng_q},"?*",{chk_rng_q},TRUE)')
    ws_calc.write_formula(4, CALC_STATE_VAL_COL, f'=COUNTIF({goal_rng_q},"?*")')
    ws_calc.write_formula(5, CALC_STATE_VAL_COL, f"=IFERROR({acell(3, CALC_STATE_VAL_COL)}/{acell(4, CALC_STATE_VAL_COL)},0)")
    ws_calc.write_formula(6, CALC_STATE_VAL_COL, stage6_formula(acell(5, CALC_STATE_VAL_COL)))

    # Sidebar: INSTRUCTIONS card (rows 3..13, cols 7..8)
    cv.merge(3, 7, 3, 8, "📌  INSTRUCTIONS • HƯỚNG DẪN", bold=True, font_size=9.5, align="center",
             bg_color=t.primary, font_color=t.on_primary)
    inst = [
        "★  Biến Mục tiêu năm thành các Thói quen cụ thể (Tháng → Tuần → Ngày) để duy trì bền vững.",
        "★  Chọn Năm ở ô góc trên bên phải (2024–2040) để theo dõi mục tiêu riêng cho từng năm.",
        "★  Tick vào ô ☑ bên trái mỗi khi đạt mục tiêu — biểu tượng hoạt ảnh bên dưới sẽ TỰ LỚN DẦN từ 0% (chậu trống) → 100% (nở rộ)!",
        "★  Số mục tiêu hoàn thành tự động đồng bộ sang tab 🏆 Tổng Kết & Thành Tựu Năm & mở khóa huy hiệu 🎯 Goal Crusher!",
    ]
    if gsheets:
        inst.append("💡  Google Sheets: Chọn B6:B25 → Chèn (Insert) → Hộp kiểm (Checkbox) hoặc chạy setupHabitTracker().")
    r_cur = 4
    for txt in inst:
        cv.merge(r_cur, 7, r_cur + 1, 8, txt, bold=False, font_size=9.5, align="left", text_wrap=True,
                 bg_color=t.card, font_color=t.ink, indent=1)
        cv.hline(r_cur + 1, 7, 8, t.line)
        r_cur += 2
    cv.box(3, 7, r_cur - 1, 8, t.line)

    # Sidebar: DYNAMIC `YOU HAVE PLANTED:` hero card
    rp = r_cur + 1
    cv.merge(rp, 7, rp, 8, f"{t.emoji}  YOU HAVE PLANTED:", bold=True, font_size=10, align="center",
             bg_color=t.primary, font_color=t.on_primary)
    cv.merge(rp + 1, 7, rp + 3, 7, f"={yg_done_ref}", bold=True,
             font_size=28, align="center", bg_color=t.card, font_color=t.primary_dark,
             font_name=t.font_title)
    dyn_anims = []
    if universal:
        cv.merge(rp + 1, 8, rp + 3, 8, "", align="center", bg_color=t.card)
        dyn_anims.append({
            "name": "Anim_YearlyGoals",
            "refers_to": f"=INDEX({ASSETS_SHEET}!$B$2:$B$8,{yg_stage_ref})",
            "sheet": name, "r1": rp + 1, "c1": 8, "r2": rp + 3, "c2": 8,
            "align_bottom": False,
        })
    else:
        cv.merge(rp + 1, 8, rp + 3, 8,
                 f'=_xlfn.IMAGE(CFG_IMG_BASE&"stage_"&(MIN(6,MAX(1,{yg_stage_ref}))-1)&".png")',
                 align="center", bg_color=t.card)
    cv.merge(rp + 4, 7, rp + 4, 8,
             f'="trên "&{yg_tot_ref}&" mục tiêu  •  "&TEXT({yg_pct_ref},"0%")',
             font_size=9, bold=True, align="center", bg_color=t.soft, font_color=t.ink)
    cv.box(rp, 7, rp + 4, 8, t.line)

    _finish_sheet(ws, cv, t.primary, zoom=88)
    return {
        "checkboxes": {name: cv.form_checkboxes},
        "dyn_anims": dyn_anims,
        "year_cell": f"{q}!$I$2",
        "last_row": max(r0 + total_rows, rp + 5),
    }


# =========================================================================== #
#  2. 🏆 Tổng Kết & Thành Tựu Năm (Annual Summary & Gamified Achievements — ALL 10 Templates!)
# =========================================================================== #
def build_annual_achievements_sheet(
    wb, styles: Styles, ws_calc, mode: str,
    pro_tr: TrackerRefs | None = None,
    month_refs: list[TrackerRefs] | None = None,
    year: int = 2026,
    universal: bool = True, gsheets: bool = False,
) -> dict:
    """
    Build the flagship `🏆 Tổng Kết & Thành Tựu Năm` sheet harmonized to `styles.t`.
      - mode == "pro_xlsm": reads live active month from `pro_tr` + saved months from `_Database`
      - mode in ("offline_12m", "gsheets"): reads live `T01..T12` when Year == ActiveYear, else `_YearHistory`
    """
    name = ANNUAL_SHEET
    t = styles.t
    ws = wb.add_worksheet(name)
    cv = Canvas(wb, ws, styles, name, universal=universal, gsheets=gsheets)
    q = qs(name)
    cq = qs(CALC_SHEET)
    yg_q = qs(YEARLY_GOALS_SHEET)
    # Pure-ASCII Named Anchors for VBA (zero Vietnamese/emoji sheet names in VBA!)
    wb.define_name("ANCHOR_GOALS", f"={yg_q}!$I$2")
    wb.define_name("ANCHOR_ANNUAL", f"={q}!$B$3")

    # 15 columns (0..14): A gutter | B label (21) | C..N = 12 months T1..T12 (9.5 each) | O gutter
    cv.col(0, 2.2)
    cv.col(1, 21.5)
    for m_col in range(2, 14):
        cv.col(m_col, 9.6)
    cv.col(14, 2.2)

    sel_y_local = "$B$3"
    sel_y_q = f"{q}!$B$3"

    # ---- Populate `_Calc!AO..AY` 12-month dynamic aggregation engine (ZERO volatile formulas!) ----
    ann_headers = ["MonthNum", "MonthKey", "Completed", "TotalGoal", "OverallPct",
                   "GrownDays", "PerfectDays", "BestStreak", "MonthlyStageIdx"]
    for off, hdr in enumerate(ann_headers):
        ws_calc.write(0, CALC_ANN_COL0 + off, hdr)

    db_q = qs(DATABASE_SHEET)
    hist_q = qs(HISTORY_SHEET)
    active_yr_ref = acell(0, CALC_STATE_VAL_COL)  # $AN$1

    for m in range(1, 13):
        rm = m  # 0-based row 1..12 -> Excel rows 2..13
        c_m = CALC_ANN_COL0
        c_key = CALC_ANN_COL0 + 1
        c_done = CALC_ANN_COL0 + 2
        c_goal = CALC_ANN_COL0 + 3
        c_pct = CALC_ANN_COL0 + 4
        c_grn = CALC_ANN_COL0 + 5
        c_prf = CALC_ANN_COL0 + 6
        c_str = CALC_ANN_COL0 + 7
        c_stg = CALC_ANN_COL0 + 8

        key_ref = acell(rm, c_key)
        ws_calc.write_number(rm, c_m, m)
        ws_calc.write_formula(rm, c_key, f'={sel_y_q}&"-"&TEXT({acell(rm, c_m)},"00")')

        if mode == "pro_xlsm" or True:
            # All 3 unified 4-tab editions (Pro .xlsm, Offline .xlsx, Google Sheets) share the exact same
            # single Monthly Tracker + hidden `_Database` architecture!
            assert pro_tr is not None
            is_live = f"AND({sel_y_q}={pro_tr.s['y']},{m}={pro_tr.s['m']})"
            db_keys = f"{db_q}!$AK$2:$AK$300"
            ws_calc.write_formula(rm, c_done, f"=IF({is_live},{pro_tr.s['tdone']},IFERROR(INDEX({db_q}!$AN$2:$AN$300,MATCH({key_ref},{db_keys},0)),0))")
            ws_calc.write_formula(rm, c_goal, f"=IF({is_live},{pro_tr.s['tgoal']},IFERROR(INDEX({db_q}!$AO$2:$AO$300,MATCH({key_ref},{db_keys},0)),0))")
            ws_calc.write_formula(rm, c_pct,  f"=IFERROR(MIN(1,{acell(rm, c_done)}/{acell(rm, c_goal)}),0)")
            ws_calc.write_formula(rm, c_grn,  f"=IF({is_live},{pro_tr.s['grown']},IFERROR(INDEX({db_q}!$AQ$2:$AQ$300,MATCH({key_ref},{db_keys},0)),0))")
            ws_calc.write_formula(rm, c_prf,  f"=IF({is_live},{pro_tr.s['perfect']},IFERROR(INDEX({db_q}!$AR$2:$AR$300,MATCH({key_ref},{db_keys},0)),0))")
            ws_calc.write_formula(rm, c_str,  f"=IF({is_live},{pro_tr.s['best']},IFERROR(INDEX({db_q}!$AS$2:$AS$300,MATCH({key_ref},{db_keys},0)),0))")

        ws_calc.write_formula(rm, c_stg, stage6_formula(acell(rm, c_pct)))

    # Selected-year Yearly Goals lookup on _Calc!AX1:AY3
    ws_calc.write(0, CALC_ANN_YG_LBL_COL, "AnnualYGDone")
    ws_calc.write(1, CALC_ANN_YG_LBL_COL, "AnnualYGTotal")
    ws_calc.write(2, CALC_ANN_YG_LBL_COL, "AnnualYGPct")
    yg_yr_ref = f"{yg_q}!$I$2"
    ws_calc.write_formula(0, CALC_ANN_YG_VAL_COL,
                          f"=IF({sel_y_q}={yg_yr_ref},{acell(3, CALC_STATE_VAL_COL)},IFERROR(INDEX({db_q}!$BD$2:$BD$60,MATCH({sel_y_q},{db_q}!$BC$2:$BC$60,0)),0))")
    ws_calc.write_formula(1, CALC_ANN_YG_VAL_COL,
                          f"=IF({sel_y_q}={yg_yr_ref},{acell(4, CALC_STATE_VAL_COL)},IFERROR(INDEX({db_q}!$BE$2:$BE$60,MATCH({sel_y_q},{db_q}!$BC$2:$BC$60,0)),0))")
    ws_calc.write_formula(2, CALC_ANN_YG_VAL_COL,
                          f"=IFERROR({acell(0, CALC_ANN_YG_VAL_COL)}/{acell(1, CALC_ANN_YG_VAL_COL)},0)")

    # Annual Overall % (active months completed / active months goals -> 0% when empty, 100% when all active months 100%!)
    done_col_rng = rng(1, CALC_ANN_COL0 + 2, 12, CALC_ANN_COL0 + 2)
    goal_col_rng = rng(1, CALC_ANN_COL0 + 3, 12, CALC_ANN_COL0 + 3)
    grn_col_rng = rng(1, CALC_ANN_COL0 + 5, 12, CALC_ANN_COL0 + 5)
    prf_col_rng = rng(1, CALC_ANN_COL0 + 6, 12, CALC_ANN_COL0 + 6)
    str_col_rng = rng(1, CALC_ANN_COL0 + 7, 12, CALC_ANN_COL0 + 7)
    pct_col_rng = rng(1, CALC_ANN_COL0 + 4, 12, CALC_ANN_COL0 + 4)

    ann_overall_calc = acell(9, CALC_STATE_VAL_COL)      # $AN$10
    ann_hero_stg_calc = acell(7, CALC_STATE_VAL_COL)     # $AN$8
    ach_stg_calc = acell(8, CALC_STATE_VAL_COL)          # $AN$9

    ws_calc.write_formula(9, CALC_STATE_VAL_COL,
                          f'=IFERROR(MIN(1,SUM({done_col_rng})/SUMIF({done_col_rng},">0",{goal_col_rng})),0)')
    ws_calc.write_formula(10, CALC_STATE_VAL_COL, f"=1-{ann_overall_calc}")
    ws_calc.write_formula(7, CALC_STATE_VAL_COL, stage6_formula(ann_overall_calc))
    # AchBadgesStageIdx: reads the 8 badge progress cells on Annual sheet (H35:H42 -> 0-based rows 34..41, col 7)
    ws_calc.write_formula(8, CALC_STATE_VAL_COL,
                          stage6_formula(f'(COUNTIF({q}!$H$35:$H$42,">=1")/8)'))

    ann_done_q = f"{cq}!{done_col_rng}"
    ann_goal_q = f"{cq}!{goal_col_rng}"
    ann_grn_q = f"{cq}!{grn_col_rng}"
    ann_prf_q = f"{cq}!{prf_col_rng}"
    ann_str_q = f"{cq}!{str_col_rng}"
    ann_pct_q = f"{cq}!{pct_col_rng}"
    ann_overall_q = f"{cq}!{ann_overall_calc}"
    ann_hero_stg_q = f"{cq}!{ann_hero_stg_calc}"
    ach_stg_q = f"{cq}!{ach_stg_calc}"
    ann_yg_done_q = f"{cq}!{acell(0, CALC_ANN_YG_VAL_COL)}"
    ann_yg_tot_q = f"{cq}!{acell(1, CALC_ANN_YG_VAL_COL)}"
    ann_yg_pct_q = f"{cq}!{acell(2, CALC_ANN_YG_VAL_COL)}"

    # ================================================================== ROW 1..4: HEADER & YEAR PICKER
    cv.row(0, 10)
    cv.row(1, 20)
    cv.row(2, 30)   # B3 = UNMERGED Year Dropdown!
    cv.row(3, 18)
    cv.row(4, 10)

    # Left Year Selector Card (B2:C4)
    cv.merge(1, 1, 1, 2, "📅  CHỌN NĂM • YEAR", bold=True, font_size=8.5, align="center",
             bg_color=t.primary, font_color=t.on_primary)
    cv.put(2, 1, year, font_name=t.font_title, font_size=16, bold=True, align="center",
           num_format="0", bg_color=t.soft, font_color=t.ink,
           top=1, top_color=t.primary_dark, bottom=1, bottom_color=t.primary_dark,
           left=1, left_color=t.primary_dark, right=1, right_color=t.primary_dark)
    cv.put(2, 2, f'=IF(SUM({ann_done_q})>0,"● Có dữ liệu","○ Chưa có")', bold=True, font_size=8.5,
           align="center", bg_color=t.card, font_color=t.primary_dark)
    cv.merge(3, 1, 3, 2, "▼ Nhấn ô năm (2024–2040)", italic=True, font_size=7.8, align="center",
             bg_color=t.card, font_color=t.muted)
    cv.box(1, 1, 3, 2, t.line)
    ws.data_validation(sel_y_local, {
        "validate": "list", "source": f"={year_lookup_ref()}",
        "input_title": "Chọn Năm Tổng Kết (2024–2040)",
        "input_message": "Chọn năm muốn xem tổng kết 12 tháng & huy hiệu. Năm chưa có dữ liệu sẽ hiển thị 0% sạch sẽ!",
    })

    # Bespoke per-theme Annual Achievements lore (31 unique handcrafted themes!)
    lore = get_annual_lore(t.slug)

    # Right Title Banner (D2:N4)
    cv.merge(1, 3, 2, 13, lore["banner"],
             font_name=t.font_title, font_size=15.5, bold=True, align="center",
             bg_color=t.primary, font_color=t.on_primary)
    cv.merge(3, 3, 3, 13,
             f'="Năm "&{sel_y_local}&"  •  {lore["subtitle"]}"',
             font_size=9.5, italic=True, align="center", bg_color=t.soft, font_color=t.ink)
    cv.box(1, 3, 3, 13, t.line)

    # ================================================================== ROW 6..11: 4 EXECUTIVE KPI CARDS
    cv.row(5, 22)
    for rr in range(6, 10):
        cv.row(rr, 22)
    cv.row(10, 20)
    cv.row(11, 10)

    # Card 1 (B6:D11): Bespoke Theme Total Completed Counter
    cv.merge(5, 1, 5, 3, lore["kpi1"], bold=True, font_size=8.8, align="center",
             bg_color=t.soft, font_color=t.ink)
    cv.merge(6, 1, 9, 3, f"=SUM({ann_done_q})", bold=True, font_size=26, align="center",
             num_format="#,##0", bg_color=t.card, font_color=t.primary_dark, font_name=t.font_title)
    cv.merge(10, 1, 10, 3,
             f'="{t.emoji} "&SUM({ann_grn_q})&" {lore["kpi1_unit"]}"&TEXT(CFG_THR_3,"0%")',
             font_size=8.5, bold=True, align="center", bg_color=t.card, font_color=t.muted)
    cv.box(5, 1, 10, 3, t.line)

    # Card 2 (E6:H11): Annual Completion % + Donut + LIVE Annual Hero Animation!
    cv.merge(5, 4, 5, 7, "🌟  TIẾN ĐỘ TRUNG BÌNH CẢ NĂM", bold=True, font_size=8.8, align="center",
             bg_color=t.soft, font_color=t.ink)
    cv.merge(6, 4, 9, 5, f"={ann_overall_q}", bold=True, font_size=18, align="center",
             num_format="0%", bg_color=t.card, font_color=t.primary_dark, font_name=t.font_title)
    d_ann = donut(wb, f"={cq}!{rng(9, CALC_STATE_VAL_COL, 10, CALC_STATE_VAL_COL)}",
                  [t.primary, t.donut_rest], hole=70)
    place_chart(cv, d_ann, 6, 4, 9, 5, pad_x=4, pad_y=2)

    dyn_anims = []
    hero_ann_box = (6, 6, 9, 7)
    if universal:
        cv.merge(*hero_ann_box, "", align="center", bg_color=t.card)
        dyn_anims.append({
            "name": "Anim_AnnualHero",
            "refers_to": f"=INDEX({ASSETS_SHEET}!$B$2:$B$8,{ann_hero_stg_q})",
            "sheet": name, "r1": 6, "c1": 6, "r2": 9, "c2": 7,
            "align_bottom": False,
        })
    else:
        cv.merge(*hero_ann_box,
                 f'=_xlfn.IMAGE(CFG_IMG_BASE&"stage_"&(MIN(6,MAX(1,{ann_hero_stg_q}))-1)&".png")',
                 align="center", bg_color=t.card)
    cv.merge(10, 4, 10, 7, f'="Biểu tượng tăng trưởng theo % năm "&{sel_y_local}',
             font_size=8.3, italic=True, align="center", bg_color=t.card, font_color=t.muted)
    cv.box(5, 4, 10, 7, t.line)

    # Card 3 (I6:K11): Best Streak & Perfect 100% Days
    cv.merge(5, 8, 5, 10, "🔥  CHUỖI & NGÀY HOÀN HẢO", bold=True, font_size=8.8, align="center",
             bg_color=t.soft, font_color=t.ink)
    cv.merge(6, 8, 7, 10, f"=MAX(0,{ann_str_q})", bold=True, font_size=22, align="center",
             num_format='0" ngày"', bg_color=t.card, font_color=t.primary_dark, font_name=t.font_title)
    cv.merge(8, 8, 9, 10, f'="✨ "&SUM({ann_prf_q})&" ngày hoàn hảo 100%"', bold=True, font_size=9.5,
             align="center", bg_color=t.card, font_color=t.ink)
    cv.merge(10, 8, 10, 10, f'="Tháng cao nhất: "&TEXT(MAX(0,{ann_pct_q}),"0%")',
             font_size=8.3, align="center", bg_color=t.card, font_color=t.muted)
    cv.box(5, 8, 10, 10, t.line)

    # Card 4 (L6:N11): Yearly Goals Achieved (linked to selected Year!)
    cv.merge(5, 11, 5, 13, "🎯  MỤC TIÊU NĂM ĐÃ ĐẠT", bold=True, font_size=8.8, align="center",
             bg_color=t.soft, font_color=t.ink)
    cv.merge(6, 11, 8, 13, f'={ann_yg_done_q}&" / "&{ann_yg_tot_q}', bold=True, font_size=24,
             align="center", bg_color=t.card, font_color=t.primary_dark, font_name=t.font_title)
    cv.merge(9, 11, 9, 13, f"={ann_yg_pct_q}", bold=True, font_size=11, align="center",
             num_format="0%", bg_color=t.card, font_color=t.ink)
    cv.merge(10, 11, 10, 13, f'="Đồng bộ Yearly Goals năm "&{sel_y_local}',
             font_size=8.2, italic=True, align="center", bg_color=t.card, font_color=t.muted)
    cv.box(5, 11, 10, 13, t.line)

    # ================================================================== ROW 13..20: 12-MONTH GARDEN & TABLE
    r_g = 12
    cv.row(r_g, 24)        # Row 13: section header
    cv.row(r_g + 1, 22)    # Row 14: T1..T12 labels
    cv.row(r_g + 2, 66)    # Row 15: 12 LIVE MONTHLY SPRITES!
    for rr in range(r_g + 3, r_g + 8):
        cv.row(rr, 20)
    cv.row(r_g + 8, 10)    # Row 21: gutter

    cv.merge(r_g, 1, r_g, 13, lore["garden"],
             bold=True, font_size=10, align="left", indent=1, bg_color=t.primary, font_color=t.on_primary)
    cv.put(r_g + 1, 1, "THÁNG (MONTH)", bold=True, font_size=8.8, align="center", bg_color=t.soft, font_color=t.ink)
    cv.put(r_g + 2, 1, f"{t.emoji}  TĂNG TRƯỞNG", bold=True, font_size=9.5, align="center",
           bg_color=t.card, font_color=t.primary_dark, font_name=t.font_title)
    row_labels = [
        ("Hoàn thành (Completed)", "0"),
        ("Mục tiêu (Total Goal)", "0"),
        ("Tỉ lệ % (% Completed)", "0%"),
        ("Ngày 100% (Perfect)", "0"),
        ("Chuỗi dài nhất (Streak)", "0"),
    ]
    for idx, (lab, _) in enumerate(row_labels):
        rr = r_g + 3 + idx
        bg = t.soft if idx == 2 else (t.card if idx % 2 == 0 else t.page)
        cv.put(rr, 1, lab, bold=(idx == 2), font_size=8.8, align="right", indent=1,
               bg_color=bg, font_color=t.ink)

    for m in range(1, 13):
        c = 1 + m  # Col C (2) .. Col N (13)
        rm = m     # _Calc row 1..12
        cv.put(r_g + 1, c, f"T{m:02d}", bold=True, font_size=9.5, align="center",
               bg_color=t.week_head[(m - 1) % 5], font_color=t.week_on[(m - 1) % 5])

        m_stg_q = f"{cq}!{acell(rm, CALC_ANN_COL0 + 8)}"
        if universal:
            cv.put(r_g + 2, c, "", align="center", bg_color=t.card)
            dyn_anims.append({
                "name": f"Anim_AnnualM{m:02d}",
                "refers_to": f"=INDEX({ASSETS_SHEET}!$B$2:$B$8,{m_stg_q})",
                "sheet": name, "r1": r_g + 2, "c1": c, "r2": r_g + 2, "c2": c,
                "align_bottom": True,
            })
        else:
            cv.put(r_g + 2, c,
                   f'=_xlfn.IMAGE(CFG_IMG_BASE&"stage_"&(MIN(6,MAX(1,{m_stg_q}))-1)&".png")',
                   align="center", bg_color=t.card)

        cv.put(r_g + 3, c, f"={cq}!{acell(rm, CALC_ANN_COL0 + 2)}", align="center", font_size=9,
               bold=True, num_format="#,##0", bg_color=t.card, font_color=t.ink)
        cv.put(r_g + 4, c, f"={cq}!{acell(rm, CALC_ANN_COL0 + 3)}", align="center", font_size=8.8,
               num_format="#,##0", bg_color=t.page, font_color=t.muted)
        cv.put(r_g + 5, c, f"={cq}!{acell(rm, CALC_ANN_COL0 + 4)}", align="center", font_size=9.2,
               bold=True, num_format="0%", bg_color=t.soft, font_color=t.ink)
        cv.put(r_g + 6, c, f"={cq}!{acell(rm, CALC_ANN_COL0 + 6)}", align="center", font_size=8.8,
               num_format="0", bg_color=t.page, font_color=t.ink)
        cv.put(r_g + 7, c, f"={cq}!{acell(rm, CALC_ANN_COL0 + 7)}", align="center", font_size=9,
               bold=True, num_format="0", bg_color=t.card, font_color=t.primary_dark)

    cv.grid(r_g + 1, 1, r_g + 7, 13, t.line)
    cv.box(r_g, 1, r_g + 7, 13, t.line)

    pct_row_ann = rng(r_g + 5, 2, r_g + 5, 13)
    ws.conditional_format(pct_row_ann, {
        "type": "3_color_scale",
        "min_type": "num", "min_value": 0, "mid_type": "num", "mid_value": 0.5, "max_type": "num", "max_value": 1,
        "min_color": "#FFFFFF", "mid_color": t.week_tint[0], "max_color": t.bar,
    })

    # ================================================================== ROW 22..31: 12-MONTH TREND CHART
    r_ch0 = 21
    for rr in range(r_ch0, r_ch0 + 10):
        cv.row(rr, 20)
    cv.row(r_ch0 + 10, 12)  # Row 32: gutter

    cv.box(r_ch0, 1, r_ch0 + 9, 13, t.line, fill=t.card)
    c_style = lore["chart_style"]
    if c_style == "area":
        ch_yr = wb.add_chart({"type": "area"})
        ch_yr.add_series({
            "name": "% Hoàn thành tháng",
            "categories": f"={q}!{rng(r_g + 1, 2, r_g + 1, 13)}",
            "values": f"={q}!{pct_row_ann}",
            "fill": {"color": t.chart_fill, "transparency": 35},
            "border": {"none": True},
        })
        ch_ln = wb.add_chart({"type": "line"})
        ch_ln.add_series({
            "name": "Xu hướng",
            "categories": f"={q}!{rng(r_g + 1, 2, r_g + 1, 13)}",
            "values": f"={q}!{pct_row_ann}",
            "line": {"color": t.chart_line, "width": 2.2},
            "marker": {"type": "circle", "size": 6, "fill": {"color": t.primary_dark},
                       "border": {"color": "#FFFFFF", "width": 1.0}},
            "data_labels": {"value": True, "num_format": "0%", "position": "above",
                            "font": {"name": t.font, "size": 8, "color": t.ink}},
        })
        ch_yr.combine(ch_ln)
    elif c_style == "column":
        ch_yr = wb.add_chart({"type": "column"})
        ch_yr.add_series({
            "name": "% Hoàn thành tháng",
            "categories": f"={q}!{rng(r_g + 1, 2, r_g + 1, 13)}",
            "values": f"={q}!{pct_row_ann}",
            "fill": {"color": t.primary},
            "border": {"none": True},
            "gap": 55,
            "data_labels": {"value": True, "num_format": "0%", "font": {"name": t.font, "size": 8, "color": t.ink}},
        })
    else:
        ch_yr = wb.add_chart({"type": "column"})
        ch_yr.add_series({
            "name": "% Hoàn thành tháng",
            "categories": f"={q}!{rng(r_g + 1, 2, r_g + 1, 13)}",
            "values": f"={q}!{pct_row_ann}",
            "fill": {"color": t.chart_fill},
            "border": {"color": t.chart_line, "width": 1.0},
            "data_labels": {"value": True, "num_format": "0%", "font": {"name": t.font, "size": 8, "color": t.ink}},
        })
        ch_ln = wb.add_chart({"type": "line"})
        ch_ln.add_series({
            "name": "Xu hướng",
            "categories": f"={q}!{rng(r_g + 1, 2, r_g + 1, 13)}",
            "values": f"={q}!{pct_row_ann}",
            "line": {"color": t.chart_line, "width": 2.0},
            "marker": {"type": "circle", "size": 6, "fill": {"color": t.primary_dark},
                       "border": {"color": "#FFFFFF", "width": 1.0}},
        })
        ch_yr.combine(ch_ln)
    ch_yr.set_title({"name": lore["chart_title"],
                     "name_font": {"name": t.font, "size": 10, "bold": True, "color": t.ink}})
    ch_yr.set_y_axis({"min": 0, "max": 1, "major_unit": 0.25, "num_format": "0%",
                      "num_font": axis_font(t), "line": {"none": True},
                      "major_gridlines": {"visible": True, "line": {"color": t.line, "dash_type": "dash"}}})
    ch_yr.set_x_axis({"num_font": axis_font(t, 8.5), "line": {"color": t.line}})
    ch_yr.set_legend({"none": True})
    ch_yr.set_chartarea({"border": {"none": True}, "fill": {"color": t.card}})
    ch_yr.set_plotarea({"layout": {"x": 0.06, "y": 0.18, "width": 0.91, "height": 0.68}})
    place_chart(cv, ch_yr, r_ch0, 1, r_ch0 + 9, 13, pad_x=4, pad_y=4)

    # ================================================================== ROW 33..42: 8 DYNAMIC ACHIEVEMENTS WALL + LIVE COUNTER!
    r_b0 = 32  # Excel row 33
    cv.row(r_b0, 26)
    cv.row(r_b0 + 1, 24)
    for rr in range(r_b0 + 2, r_b0 + 10):
        cv.row(rr, 34)
    cv.row(r_b0 + 10, 12)

    cv.merge(r_b0, 1, r_b0, 10, lore["wall"],
             bold=True, font_size=10, align="left", indent=1, bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r_b0 + 1, 1, r_b0 + 1, 3, "HUY HIỆU (BADGE)", bold=True, font_size=8.8, align="center",
             bg_color=t.soft, font_color=t.ink)
    cv.merge(r_b0 + 1, 4, r_b0 + 1, 6, "ĐIỀU KIỆN MỞ KHÓA (REQUIREMENT)", bold=True, font_size=8.8, align="center",
             bg_color=t.soft, font_color=t.ink)
    cv.merge(r_b0 + 1, 7, r_b0 + 1, 8, "TIẾN ĐỘ (PROGRESS)", bold=True, font_size=8.8, align="center",
             bg_color=t.soft, font_color=t.ink)
    cv.merge(r_b0 + 1, 9, r_b0 + 1, 10, "TRẠNG THÁI (STATUS)", bold=True, font_size=8.8, align="center",
             bg_color=t.soft, font_color=t.ink)

    badge_formulas = [
        f"=MIN(1,SUM({ann_grn_q})/1)",
        f"=MIN(1,MAX(0,{ann_str_q})/7)",
        f"=MIN(1,MAX(0,{ann_str_q})/21)",
        f"=MIN(1,MAX(0,{ann_str_q})/30)",
        f"=MIN(1,MAX(0,{ann_pct_q})/0.8)",
        f"=MIN(1,SUM({ann_grn_q})/100)",
        f"=MIN(1,{ann_yg_pct_q}/0.5)",
        f"=MIN(1,MAX({ann_overall_q}/0.8,SUM({ann_grn_q})/250))",
    ]
    badges = [(bn, br, bf) for (bn, br), bf in zip(lore["badges"], badge_formulas)]

    r_b_first = r_b0 + 2   # 0-based 34 -> Excel row 35 (matches _Calc!$AN$9 formula $H$35:$H$42!)
    r_b_last = r_b_first + len(badges) - 1  # Excel row 42
    for idx, (b_name, b_req, b_prog_f) in enumerate(badges):
        rr = r_b_first + idx
        bg = t.card if idx % 2 == 0 else t.page
        cv.merge(rr, 1, rr, 3, b_name, bold=True, font_size=10, align="left", indent=1,
                 bg_color=bg, font_color=t.ink)
        cv.merge(rr, 4, rr, 6, b_req, bold=False, font_size=9.5, align="left", indent=1, text_wrap=True,
                 bg_color=bg, font_color=t.muted)
        cv.merge(rr, 7, rr, 8, b_prog_f, bold=True, font_size=9.5, align="center",
                 num_format="0%", bg_color=bg, font_color=t.ink)
        cv.merge(rr, 9, rr, 10, f'=IF($H{rr + 1}>=1,"🏆 ĐÃ MỞ KHÓA","🔒 Chưa mở")',
                 bold=True, font_size=9, align="center", bg_color="#F3F4F6", font_color="#8A929A")
    cv.grid(r_b0 + 1, 1, r_b_last, 10, t.line)
    cv.box(r_b0, 1, r_b_last, 10, t.line)

    # Progress Data Bars on H35:I42 + Conditional Highlight on J35:K42 when unlocked!
    ws.conditional_format(rng(r_b_first, 7, r_b_last, 8), {
        "type": "data_bar", "bar_color": t.bar, "bar_solid": True,
        "min_type": "num", "min_value": 0, "max_type": "num", "max_value": 1,
        "bar_border_color": t.bar,
    })
    ws.conditional_format(rng(r_b_first, 9, r_b_last, 10, absolute=False), {
        "type": "formula", "criteria": f"=$H{r_b_first + 1}>=1",
        "format": wb.add_format({"bg_color": t.primary, "font_color": t.on_primary, "bold": True}),
    })

    # Right Achievements Counter Card (L33:N42 -> cols 11..13, rows 32..41)
    cv.merge(r_b0, 11, r_b0, 13, lore["counter"], bold=True, font_size=9.5, align="center",
             bg_color=t.primary, font_color=t.on_primary)
    unlocked_expr = f'COUNTIF($H${r_b_first + 1}:$H${r_b_last + 1},">=1")'
    cv.merge(r_b0 + 1, 11, r_b0 + 3, 13, f'={unlocked_expr}&" / 8"', bold=True, font_size=26,
             align="center", bg_color=t.card, font_color=t.primary_dark, font_name=t.font_title)

    ach_icon_box = (r_b0 + 4, 11, r_b0 + 7, 13)
    if universal:
        cv.merge(*ach_icon_box, "", align="center", bg_color=t.card)
        dyn_anims.append({
            "name": "Anim_AchBadges",
            "refers_to": f"=INDEX({ASSETS_SHEET}!$B$2:$B$8,{ach_stg_q})",
            "sheet": name, "r1": r_b0 + 4, "c1": 11, "r2": r_b0 + 7, "c2": 13,
            "align_bottom": False,
        })
    else:
        cv.merge(*ach_icon_box,
                 f'=_xlfn.IMAGE(CFG_IMG_BASE&"stage_"&(MIN(6,MAX(1,{ach_stg_q}))-1)&".png")',
                 align="center", bg_color=t.card)

    r0_msg, r1_msg, r2_msg, r3_msg = lore["ranks"]
    cv.merge(r_b0 + 8, 11, r_b0 + 9, 13,
             f'=IF({unlocked_expr}=0,"{r0_msg}",'
             f'IF({unlocked_expr}<=3,"{r1_msg}",'
             f'IF({unlocked_expr}<=6,"{r2_msg}","{r3_msg}")))',
             bold=True, font_size=9.2, align="center", text_wrap=True,
             bg_color=t.soft, font_color=t.ink)
    cv.box(r_b0, 11, r_b0 + 9, 13, t.line)

    _finish_sheet(ws, cv, t.primary_dark, zoom=82)
    return {
        "dyn_anims": dyn_anims,
        "year_cell": sel_y_q,
        "capture_range": f"A1:O{r_b_last + 2}",
    }


# =========================================================================== #
#  3. Hidden `_Database` Sheet (Pro `.xlsm` Multi-Month / Multi-Year Persistence!)
# =========================================================================== #
def build_database_sheet(wb, styles: Styles, habits: list[Habit],
                         seed_months: list[tuple[int, int, list[list[bool]]]],
                         seed_goal_year: int = 2026):
    """
    Create hidden `_Database` sheet with 4 clean structured tables:
      - MonthlyRaw (Cols A:AI, 35 cols): Key, RowIdx(1..20), HabitName, Goal, D01..D31
      - MonthlySummary (Cols AK:AS, 9 cols): Key, Year, Month, Completed, TotalGoal, OverallPct, GrownDays, PerfectDays, BestStreak
      - YearlyGoalsRaw (Cols AU:BA, 7 cols): YearKey, RowIdx(1..20), Done, GoalText, MonthlyHabit, WeeklyHabit, DailyHabit
      - YearlyGoalsSummary (Cols BC:BE, 3 cols): YearKey, GoalsDone, GoalsTotal
    """
    ws = wb.add_worksheet(DATABASE_SHEET)
    ws.hide_gridlines(2)
    t = styles.t
    hdr = wb.add_format({"font_name": t.font, "font_size": 9, "bold": True,
                         "bg_color": t.primary, "font_color": t.on_primary, "align": "center"})

    # Table 1 headers: A1:AI1 (cols 0..34)
    raw_hdrs = ["Key", "RowIdx", "HabitName", "Goal"] + [f"D{d:02d}" for d in range(1, 32)]
    for c, h in enumerate(raw_hdrs):
        ws.write(0, c, h, hdr)

    # Table 2 headers: AK1:AS1 (cols 36..44)
    sum_hdrs = ["Key", "Year", "Month", "Completed", "TotalGoal", "OverallPct",
                "GrownDays", "PerfectDays", "BestStreak"]
    for off, h in enumerate(sum_hdrs):
        ws.write(0, 36 + off, h, hdr)

    # Table 3 headers: AU1:BA1 (cols 46..52)
    yg_raw_hdrs = ["YearKey", "RowIdx", "Done", "GoalText", "MonthlyHabit", "WeeklyHabit", "DailyHabit"]
    for off, h in enumerate(yg_raw_hdrs):
        ws.write(0, 46 + off, h, hdr)

    # Table 4 headers: BC1:BE1 (cols 54..56)
    yg_sum_hdrs = ["YearKey", "GoalsDone", "GoalsTotal"]
    for off, h in enumerate(yg_sum_hdrs):
        ws.write(0, 54 + off, h, hdr)

    # Table 5 headers: BG1:BN1 (cols 58..65) — Daily One-Off Tasks by YYYY-MM-DD (v3.0!)
    dt_hdrs = ["DateKey", "RowIdx", "Done", "TaskName", "Category", "Priority", "Notes", "DailyHighlight"]
    for off, h in enumerate(dt_hdrs):
        ws.write(0, 58 + off, h, hdr)

    # Pre-seed MonthlyRaw & MonthlySummary
    raw_r = 1
    sum_r = 1
    for yr, mo, ticks_20 in seed_months:
        key = f"{yr:04d}-{mo:02d}"
        for i in range(N_HABITS):
            h = habits[i] if i < len(habits) else None
            ws.write(raw_r, 0, key)
            ws.write_number(raw_r, 1, i + 1)
            ws.write(raw_r, 2, h.name if h else "")
            if h and h.goal:
                ws.write_number(raw_r, 3, h.goal)
            else:
                ws.write(raw_r, 3, "")
            row_ticks = ticks_20[i] if i < len(ticks_20) else [False] * 31
            for d in range(31):
                ws.write_boolean(raw_r, 4 + d, bool(row_ticks[d]))
            raw_r += 1

        s = compute_month_summary_py(habits, ticks_20, yr, mo)
        ws.write(sum_r, 36, s["key"])
        ws.write_number(sum_r, 37, s["year"])
        ws.write_number(sum_r, 38, s["month"])
        ws.write_number(sum_r, 39, s["completed"])
        ws.write_number(sum_r, 40, s["total_goal"])
        ws.write_number(sum_r, 41, s["overall"])
        ws.write_number(sum_r, 42, s["grown_days"])
        ws.write_number(sum_r, 43, s["perfect_days"])
        ws.write_number(sum_r, 44, s["best_streak"])
        sum_r += 1

    # Pre-seed YearlyGoalsRaw & YearlyGoalsSummary for `seed_goal_year`
    goals_done = 0
    goals_tot = 0
    for i in range(20):
        rr = 1 + i
        ws.write_number(rr, 46, seed_goal_year)
        ws.write_number(rr, 47, i + 1)
        if i < len(DEFAULT_YEARLY_GOALS):
            chk, g, m, w, d = DEFAULT_YEARLY_GOALS[i]
            goals_tot += 1
            if chk:
                goals_done += 1
            ws.write_boolean(rr, 48, chk)
            ws.write(rr, 49, g)
            ws.write(rr, 50, m)
            ws.write(rr, 51, w)
            ws.write(rr, 52, d)
        else:
            ws.write_boolean(rr, 48, False)
            ws.write(rr, 49, "")
            ws.write(rr, 50, "")
            ws.write(rr, 51, "")
            ws.write(rr, 52, "")
    ws.write_number(1, 54, seed_goal_year)
    ws.write_number(1, 55, goals_done)
    ws.write_number(1, 56, goals_tot)

    # Pre-seed Table 5 (DailyTasksRaw, BG2:BN21) ONLY for default demo date 2026-10-21!
    for i in range(20):
        rr = 1 + i
        ws.write(rr, 58, DEFAULT_TASK_KEY)
        ws.write_number(rr, 59, i + 1)
        if i < len(DEFAULT_DAILY_TASKS):
            done, t_nm, cat, prio, note = DEFAULT_DAILY_TASKS[i]
            ws.write_boolean(rr, 60, done)
            ws.write(rr, 61, t_nm)
            ws.write(rr, 62, cat)
            ws.write(rr, 63, prio)
            ws.write(rr, 64, note)
        else:
            ws.write_boolean(rr, 60, False)
            ws.write(rr, 61, "")
            ws.write(rr, 62, "")
            ws.write(rr, 63, "")
            ws.write(rr, 64, "")
        ws.write(rr, 65, DEFAULT_DAILY_HIGHLIGHT if i == 0 else "")

    ws.hide()
    return ws


# =========================================================================== #
#  4. Hidden `_YearHistory` Sheet (Offline 12-Month `.xlsx` & Google Sheets Archive!)
# =========================================================================== #
def build_year_history_sheet(wb, styles: Styles):
    """
    Create clean hidden `_YearHistory` archive table for multi-year viewing in No-Macro editions.
    - Cols A:I -> Past years' monthly archive (`Key`, `Year`, `Month`, `Completed`, `TotalGoal`, `OverallPct`, `GrownDays`, `PerfectDays`, `BestStreak`)
    - Cols K:M -> Past years' YearlyGoals archive (`YearKey`, `GoalsDone`, `GoalsTotal`)
    Empty by default so any unstarted year (e.g., 2027, 2028) cleanly displays 0% & stage_0!
    """
    ws = wb.add_worksheet(HISTORY_SHEET)
    ws.hide_gridlines(2)
    t = styles.t
    hdr = wb.add_format({"font_name": t.font, "font_size": 9, "bold": True,
                         "bg_color": t.primary, "font_color": t.on_primary, "align": "center"})

    m_hdrs = ["Key (YYYY-MM)", "Year", "Month", "Completed", "TotalGoal", "OverallPct",
              "GrownDays", "PerfectDays", "BestStreak"]
    for c, h in enumerate(m_hdrs):
        ws.write(0, c, h, hdr)

    g_hdrs = ["YearKey", "GoalsDone", "GoalsTotal"]
    for off, h in enumerate(g_hdrs):
        ws.write(0, 10 + off, h, hdr)

    ws.set_column(0, 12, 14)
    ws.hide()
    return ws
