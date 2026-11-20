"""
hx.addons — Template-specific in-sheet dashboard blocks mounted onto the main tracker sheet.
"""
from __future__ import annotations

import random

from .core import Canvas, acell, cell, colname, rng, donut, place_chart, axis_font
from .tracker import (C_NAME, C_D0, C_D31, C_R0, CALC_WK_COL0, R_BAND0, R_BAND1, R_DONE, R_NOT,
                      R_PCT, R_DAY, R_EXTRA, TrackerRefs, day_col, week_days)


# --------------------------------------------------------------------------- #
#  Template 2 (Cactus): Color-coded Weekly Pastel Summary Strip + Side Stats
# --------------------------------------------------------------------------- #
def add_cactus_weekly_strip(wb, cv: Canvas, tr: TrackerRefs):
    t = cv.t
    r = R_EXTRA
    cv.row(r, 22)
    cv.row(r + 1, 28)
    cv.row(r + 2, 20)
    cv.row(r + 3, 20)

    cv.merge(r, C_NAME, r, C_NAME, "🌵  WEEKLY SUMMARY", bold=True, font_size=9.5, align="center",
             bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r + 1, C_NAME, r + 3, C_NAME,
             f'="Tổng hoàn thành: "&{tr.s["tdone"]}&" / "&{tr.s["tgoal"]}&CHAR(10)&'
             f'"Hiệu suất TB: "&TEXT({tr.s["avg"]},"0%")&CHAR(10)&'
             f'"Ngày 100%: "&{tr.s["perfect"]}&" ngày ✨"',
             font_size=9, align="center", text_wrap=True, bg_color=t.card, font_color=t.ink)
    cv.box(r, C_NAME, r + 3, C_NAME, t.line)

    rb = tr.calc_row_base
    for w in range(5):
        days = week_days(w)
        c1, c2 = day_col(days[0]), day_col(days[-1])
        hc = CALC_WK_COL0 + w
        pct_ref = f"{tr.calc_q}!{acell(rb + 2, hc)}"
        done_ref = f"{tr.calc_q}!{acell(rb + 0, hc)}"
        tot_ref = f"{tr.calc_q}!{acell(rb + 1, hc)}"
        cv.merge(r, c1, r, c2, f"WEEK {w + 1}  ({days[0]}–{days[-1]})", bold=True, font_size=8.5,
                 align="center", bg_color=t.week_head[w], font_color=t.week_on[w])
        cv.merge(r + 1, c1, r + 1, c2, f"={pct_ref}", bold=True, font_size=15, align="center",
                 num_format="0%", bg_color=t.card, font_color=t.ink, font_name=t.font_title)
        cv.merge(r + 2, c1, r + 2, c2, f'={done_ref}&" / "&{tot_ref}&" lượt"', font_size=8.5,
                 align="center", bg_color=t.week_tint[w], font_color=t.ink)
        cv.merge(r + 3, c1, r + 3, c2,
                 f'=IF({pct_ref}>=0.85,"🌸 Nở hoa!",IF({pct_ref}>=0.6,"🌵 Ổn định","🌱 Cố lên!"))',
                 font_size=8.5, bold=True, align="center", bg_color=t.card, font_color=t.muted)
        cv.box(r, c1, r + 3, c2, t.line)

    # Right side highlight card
    C_RE = tr.c_right_end
    cv.merge(r, C_R0, r, C_RE, "🌵  SIDE STATS • ĐIỂM NHẤN", bold=True, font_size=8.5, align="center",
             bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r + 1, C_R0, r + 1, C_R0 + 2, "Chuỗi cao nhất tháng:", font_size=9, align="left",
             indent=1, bg_color=t.card, font_color=t.muted)
    cv.merge(r + 1, C_R0 + 3, r + 1, C_RE, f'={tr.s["best"]}&" ngày 🔥"', bold=True, font_size=10,
             align="center", bg_color=t.card, font_color=t.ink)
    cv.merge(r + 2, C_R0, r + 2, C_R0 + 2, "Số ngày nở hoa (≥75%):", font_size=9, align="left",
             indent=1, bg_color=t.card, font_color=t.muted)
    cv.merge(r + 2, C_R0 + 3, r + 2, C_RE, f'={tr.s["grown"]}&" / "&{tr.s["dim"]}', bold=True,
             font_size=10, align="center", bg_color=t.card, font_color=t.primary_dark)
    cv.merge(r + 3, C_R0, r + 3, C_R0 + 2, "Chuỗi hiện tại tốt nhất:", font_size=9, align="left",
             indent=1, bg_color=t.card, font_color=t.muted)
    cv.merge(r + 3, C_R0 + 3, r + 3, C_RE, f'={tr.s["bestcur"]}&" ngày"', bold=True, font_size=10,
             align="center", bg_color=t.card, font_color=t.ink)
    cv.box(r, C_R0, r + 3, C_RE, t.line)


# --------------------------------------------------------------------------- #
#  Template 3 (Rainbow Executive): 5 Weekly Donut Charts + Weekly Habits + Notes
# --------------------------------------------------------------------------- #
def add_rainbow_bottom_blocks(wb, cv: Canvas, tr: TrackerRefs):
    t = cv.t
    q = tr.q
    C_RE = tr.c_right_end

    # ---- BLOCK 1: WEEKLY PROGRESS (5 DONUTS) + NOTES ----
    r0 = R_EXTRA
    for rr in range(r0, r0 + 5):
        cv.row(rr, 22)
    cv.row(r0 + 5, 19)
    cv.row(r0 + 6, 19)

    cv.merge(r0, C_NAME, r0 + 4, C_NAME, "WEEKLY PROGRESS\nTiến độ theo tuần", bold=True,
             font_size=10.5, align="center", text_wrap=True, bg_color=t.card, font_color=t.ink,
             font_name=t.font_title)
    cv.put(r0 + 5, C_NAME, "Habits Completed", align="right", indent=1, font_size=8.5, bold=True,
           bg_color=t.soft, font_color=t.ink)
    cv.put(r0 + 6, C_NAME, "Habits Incompleted", align="right", indent=1, font_size=8.5,
           bg_color=t.card, font_color=t.muted)

    # 5 Weekly Donuts spanning cols C_D0..C_D31 (6, 6, 6, 6, 7 cols -> super balanced!)
    rb = tr.calc_row_base
    spans = [(2, 7), (8, 13), (14, 19), (20, 25), (26, 32)]
    donut_colors = ["#77BBD9", "#7ECF9B", "#EB9BBF", "#F2BD6B", "#A9C96E"]
    for w, (c1, c2) in enumerate(spans):
        hc = CALC_WK_COL0 + w
        cv.merge(r0, c1, r0, c2, f"WEEK {w + 1}", bold=True, font_size=8.5, align="center",
                 bg_color=t.week_head[w], font_color=t.week_on[w])
        cv.merge(r0 + 1, c1, r0 + 4, c2, f"={tr.calc_q}!{acell(rb + 2, hc)}", bold=True, font_size=13, align="center",
                 num_format="0%", bg_color=t.card, font_color=donut_colors[w], font_name=t.font_title)
        dch = donut(wb, f"={tr.calc_q}!{rng(rb + 2, hc, rb + 3, hc)}", [donut_colors[w], t.donut_rest], hole=70)
        place_chart(cv, dch, r0 + 1, c1, r0 + 4, c2, pad_x=10, pad_y=2)
        cv.vline(c2, r0, r0 + 4, t.line, where="right")

    # Daily Completed / Incompleted rows directly aligned under days 1..31
    for k in range(1, 32):
        c = day_col(k)
        cv.put(r0 + 5, c, f"={cell(R_DONE, c)}", align="center", font_size=8, bold=True,
               bg_color=t.soft, font_color=t.ink)
        cv.put(r0 + 6, c, f"={cell(R_NOT, c)}", align="center", font_size=8,
               bg_color=t.card, font_color=t.muted)
    cv.grid(r0 + 5, C_D0, r0 + 6, C_D31, t.line)
    cv.box(r0, C_NAME, r0 + 6, C_D31, t.line)

    # NOTES card on the right (C_R0..C_RE)
    cv.merge(r0, C_R0, r0, C_RE, "📝  NOTES • GHI CHÚ THÁNG", bold=True, font_size=9, align="center",
             bg_color=t.primary, font_color=t.on_primary)
    sample_notes = [
        "• Sinh nhật mẹ ngày 18 — đặt hoa trước 2 ngày",
        "• Duy trì đi bộ 20 phút sau bữa tối",
        "• Hoàn thành cuốn Atomic Habits trước ngày 25",
        "• Chuẩn bị mục tiêu tháng sau vào Chủ nhật tuần 4",
        "",
        "",
    ]
    for i, note in enumerate(sample_notes):
        cv.merge(r0 + 1 + i, C_R0, r0 + 1 + i, C_RE, note, font_size=9, align="left", indent=1,
                 bg_color=t.card, font_color=t.ink)
        cv.hline(r0 + 1 + i, C_R0, C_RE, t.line)
    cv.box(r0, C_R0, r0 + 6, C_RE, t.line)

    # ---- BLOCK 2: WEEKLY HABITS CHECKLIST ----
    r1 = r0 + 8
    cv.row(r1 - 1, 12)
    cv.row(r1, 22)
    for i in range(1, 7):
        cv.row(r1 + i, 21)

    weekly_tasks = [
        [("Lập kế hoạch tuần", True), ("Chuẩn bị bữa ăn (Meal prep)", True),
         ("Dọn gọn góc làm việc", True), ("Review mục tiêu tuần", False), ("", False), ("", False)],
        [("Thử 1 công thức nấu ăn mới", True), ("Dọn tủ quần áo", True),
         ("Dành 2h sáng tạo cá nhân", False), ("Tổng kết chi tiêu", True), ("", False), ("", False)],
        [("Viết nhật ký biết ơn", True), ("Học kỹ năng mới 2h", True),
         ("Gọi điện cho gia đình", True), ("Đi bộ công viên cuối tuần", False), ("", False), ("", False)],
        [("Buổi tối không màn hình", True), ("Đặt mục tiêu tháng tới", True),
         ("Chăm sóc da chuyên sâu", False), ("Sao lưu tài liệu", True), ("", False), ("", False)],
        [("Tổng vệ sinh nhà cửa", True), ("Tổng kết tháng & tự thưởng", False),
         ("", False), ("", False), ("", False), ("", False)],
    ]
    # Collect ranges for live weekly habit completion counter
    chk_cols, txt_cols = [], []
    for w, (c1, c2) in enumerate(spans):
        cv.merge(r1, c1, r1, c2, f"WEEK {w + 1}", bold=True, font_size=8.5, align="center",
                 bg_color=t.week_head[w], font_color=t.week_on[w])
        chk_cols.append(c1)
        txt_cols.append(c1 + 1)
        for i, (task, done) in enumerate(weekly_tasks[w]):
            rr = r1 + 1 + i
            cv.checkbox(rr, c1, done, align="center", font_color=t.week_check[w], bg_color=t.card)
            cv.merge(rr, c1 + 1, rr, c2, task, font_size=9, align="left", indent=1, bg_color=t.card,
                     font_color=t.ink)
            cv.hline(rr, c1, c2, t.line)
        cv.vline(c2, r1, r1 + 6, t.line, where="right")

    done_terms = "+".join(
        f'COUNTIFS({rng(r1 + 1, tc, r1 + 6, tc)},"?*",{rng(r1 + 1, cc, r1 + 6, cc)},TRUE)'
        for cc, tc in zip(chk_cols, txt_cols)
    )
    tot_terms = "+".join(
        f'COUNTIF({rng(r1 + 1, tc, r1 + 6, tc)},"?*")'
        for tc in txt_cols
    )
    cv.put(r1, C_NAME, "WEEKLY HABITS", bold=True, font_size=9.5, align="center",
           bg_color=t.primary, font_color=t.on_primary)
    cv.put(r1 + 1, C_NAME, "COMPLETED", bold=True, font_size=8.5, align="center",
           bg_color=t.soft, font_color=t.muted)
    cv.merge(r1 + 2, C_NAME, r1 + 4, C_NAME, f"=IFERROR(({done_terms})/({tot_terms}),0)",
             bold=True, font_size=20, align="center", num_format="0%", bg_color=t.card,
             font_color=t.primary_dark, font_name=t.font_title)
    cv.merge(r1 + 5, C_NAME, r1 + 6, C_NAME, f'=({done_terms})&" / "&({tot_terms})&" việc tuần"',
             font_size=9, align="center", bg_color=t.card, font_color=t.muted)
    cv.box(r1, C_NAME, r1 + 6, C_D31, t.line)

    # Right summary card next to Weekly Habits: Quick Inspiration / Monthly Mantra
    cv.merge(r1, C_R0, r1, C_RE, "✨  MONTHLY FOCUS • TÂM ĐIỂM", bold=True, font_size=9,
             align="center", bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r1 + 1, C_R0, r1 + 3, C_RE,
             "\"Kỷ luật nhỏ mỗi ngày tạo nên kết quả lớn cuối tháng.\"\n— Consistency > Perfection —",
             italic=True, font_size=9.5, align="center", text_wrap=True, bg_color=t.soft,
             font_color=t.ink)
    cv.merge(r1 + 4, C_R0, r1 + 6, C_RE,
             f'="⭐ Tổng lọ sao đầy: "&{tr.s["grown"]}&" ngày"&CHAR(10)&'
             f'"🏆 Ngày hoàn hảo 100%: "&{tr.s["perfect"]}&" ngày"',
             bold=True, font_size=9.5, align="center", text_wrap=True, bg_color=t.card,
             font_color=t.primary_dark)
    cv.box(r1, C_R0, r1 + 6, C_RE, t.line)


# --------------------------------------------------------------------------- #
#  Template 5 (Lavender Wellness): Sleep + Mood + Energy Log & Correlation Chart
# --------------------------------------------------------------------------- #
def add_wellness_mood_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 55) -> dict:
    """Returns dict of key cell addresses on the main sheet for Gratitude & Review tab."""
    t = cv.t
    ws = cv.ws
    q = tr.q
    C_RE = tr.c_right_end

    r0 = R_EXTRA
    cv.row(r0, 23)
    for rr in range(r0 + 1, r0 + 5):
        cv.row(rr, 22)

    cv.put(r0, C_NAME, "🌙  WELLNESS & MOOD LOG", bold=True, font_size=9.5, align="left", indent=1,
           bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_D0, r0, C_D31, "THEO DÕI GIẤC NGỦ (GIỜ) • TÂM TRẠNG (1–5) • NĂNG LƯỢNG (1–5) • BÌNH AN (1–5)",
             bold=True, font_size=8.5, align="center", bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_R0, r0, C_RE, "💜  WELLNESS SUMMARY", bold=True, font_size=8.5, align="center",
             bg_color=t.primary, font_color=t.on_primary)

    r_sleep, r_mood, r_energy, r_calm = r0 + 1, r0 + 2, r0 + 3, r0 + 4
    rows_meta = [
        (r_sleep, "💤  Giờ ngủ (Sleep Hours)", "0.0"),
        (r_mood, "💜  Tâm trạng (Mood 1–5)", "0"),
        (r_energy, "⚡  Năng lượng (Energy 1–5)", "0"),
        (r_calm, "🧘  Thư thái (Calm 1–5)", "0"),
    ]
    for rr, lab, _ in rows_meta:
        cv.put(rr, C_NAME, lab, bold=True, font_size=9, align="left", indent=1, bg_color=t.soft,
               font_color=t.ink)

    rnd = random.Random(seed)
    for k in range(1, 32):
        c = day_col(k)
        if k > 22:
            # Leave Days 23..31 blank ready for the user to log
            for rr, _, nf in rows_meta:
                cv.put(rr, c, "", align="center", font_size=9, bg_color=t.card, num_format=nf)
            continue
        sl = round(rnd.choice([6.5, 7.0, 7.5, 7.5, 8.0, 8.0, 8.5, 6.0, 7.5, 8.0]), 1)
        md = min(5, max(2, int(round(sl - 3.6 + rnd.uniform(-0.5, 0.7)))))
        en = min(5, max(2, int(round(md + rnd.uniform(-0.6, 0.5)))))
        cm = min(5, max(2, int(round(md + rnd.uniform(-0.7, 0.7)))))
        cv.put(r_sleep, c, sl, align="center", font_size=8.5, bg_color=t.card, num_format="0.0", font_color=t.ink)
        cv.put(r_mood, c, md, align="center", font_size=9, bold=True, bg_color=t.card, num_format="0", font_color=t.ink)
        cv.put(r_energy, c, en, align="center", font_size=9, bold=True, bg_color=t.card, num_format="0", font_color=t.ink)
        cv.put(r_calm, c, cm, align="center", font_size=9, bg_color=t.card, num_format="0", font_color=t.ink)

    cv.grid(r_sleep, C_NAME, r_calm, C_D31, t.line)
    cv.box(r0, C_NAME, r_calm, C_D31, t.line)

    # Conditional heatmaps + dropdown validation
    sleep_rng = rng(r_sleep, C_D0, r_sleep, C_D31)
    mood_rng = rng(r_mood, C_D0, r_mood, C_D31)
    energy_rng = rng(r_energy, C_D0, r_energy, C_D31)
    calm_rng = rng(r_calm, C_D0, r_calm, C_D31)
    ws.conditional_format(sleep_rng, {"type": "3_color_scale", "min_type": "num", "min_value": 5,
                                      "mid_type": "num", "mid_value": 7.5, "max_type": "num", "max_value": 9,
                                      "min_color": "#FDE8EC", "mid_color": "#EFEAF9", "max_color": "#C8B6E2"})
    for rg in (mood_rng, energy_rng, calm_rng):
        ws.conditional_format(rg, {"type": "3_color_scale", "min_type": "num", "min_value": 1,
                                   "mid_type": "num", "mid_value": 3, "max_type": "num", "max_value": 5,
                                   "min_color": "#F9EFF4", "mid_color": "#E2D7F8", "max_color": "#A594F9"})
        ws.data_validation(rg, {"validate": "integer", "criteria": "between", "minimum": 1, "maximum": 5,
                                "input_title": "Thang điểm 1–5", "input_message": "1 = Rất thấp, 3 = Ổn định, 5 = Tuyệt vời"})

    # Right summary KPIs
    avg_sleep_addr = acell(r_sleep, C_R0 + 3)
    avg_mood_addr = acell(r_mood, C_R0 + 3)
    avg_energy_addr = acell(r_energy, C_R0 + 3)
    great_days_addr = acell(r_calm, C_R0 + 3)
    kpis = [
        (r_sleep, "Giấc ngủ trung bình:", f'=IFERROR(AVERAGE({sleep_rng}),0)', '0.0" h"'),
        (r_mood, "Tâm trạng TB (/5):", f'=IFERROR(AVERAGE({mood_rng}),0)', '0.0" ★"'),
        (r_energy, "Năng lượng TB (/5):", f'=IFERROR(AVERAGE({energy_rng}),0)', '0.0" ⚡"'),
        (r_calm, "Ngày tâm trạng tốt (≥4):", f'=COUNTIF({mood_rng},">=4")', '0" ngày"'),
    ]
    for rr, lab, form, nf in kpis:
        cv.merge(rr, C_R0, rr, C_R0 + 2, lab, font_size=9, align="left", indent=1,
                 bg_color=t.card, font_color=t.muted)
        cv.merge(rr, C_R0 + 3, rr, C_RE, form, bold=True, font_size=10, align="center",
                 bg_color=t.soft, font_color=t.primary_dark, num_format=nf)
        cv.hline(rr, C_R0, C_RE, t.line)
    cv.box(r0, C_R0, r_calm, C_RE, t.line)

    # Hidden normalized Mood% & Sleep% rows (cols C_D0..C_D31) in hidden rows? No — put in hidden cols?
    # Better: put normalized series in rows r_calm+2..r_calm+3? No, keep sheet super clean by writing
    # normalized Mood% (=Mood/5) & Sleep% (=MIN(1,Sleep/8)) in hidden cols 60..90 at rows r_mood & r_sleep!
    # Wait: cols 60..90 are ALREADY hidden! So row r_mood cols 60..90 = Mood/5, row r_sleep cols 60..90 = MIN(1,Sleep/8)!
    C_HID_NORM = 60
    cv.cols(C_HID_NORM, C_HID_NORM + 30, 5, hidden=True)
    for k in range(1, 32):
        c = day_col(k)
        hc = C_HID_NORM + k - 1
        cv.put(r_mood, hc, f'=IF({cell(r_mood, c)}="",0,IFERROR({cell(r_mood, c)}/5,0))')
        cv.put(r_sleep, hc, f'=IF({cell(r_sleep, c)}="",0,IFERROR(MIN(1,{cell(r_sleep, c)}/8),0))')

    # Correlation Chart below wellness table
    r_ch0 = r_calm + 2
    r_ch1 = r_ch0 + 8
    cv.row(r_ch0 - 1, 12)
    for rr in range(r_ch0, r_ch1 + 1):
        cv.row(rr, 20)

    corr = wb.add_chart({"type": "area"})
    day_row = rng(R_DAY, C_D0, R_DAY, C_D31)
    pct_row = rng(R_PCT, C_D0, R_PCT, C_D31)
    corr.add_series({
        "name": "Habit %",
        "categories": f"={q}!{day_row}",
        "values": f"={q}!{pct_row}",
        "fill": {"color": "#C8B6E2", "transparency": 55},
        "border": {"color": "#A594F9", "width": 1.25},
    })
    ln = wb.add_chart({"type": "line"})
    ln.add_series({
        "name": "Mood (Scaled /5)",
        "categories": f"={q}!{day_row}",
        "values": f"={q}!{rng(r_mood, C_HID_NORM, r_mood, C_HID_NORM + 30)}",
        "line": {"color": "#6E5BCB", "width": 2.0},
        "marker": {"type": "circle", "size": 4, "fill": {"color": "#6E5BCB"}, "border": {"color": "#FFFFFF"}},
    })
    ln.add_series({
        "name": "Sleep (vs 8h)",
        "categories": f"={q}!{day_row}",
        "values": f"={q}!{rng(r_sleep, C_HID_NORM, r_sleep, C_HID_NORM + 30)}",
        "line": {"color": "#E08AB5", "width": 1.75, "dash_type": "dash"},
        "marker": {"type": "none"},
    })
    corr.combine(ln)
    corr.show_hidden_data()
    corr.set_title({"name": "HABIT COMPLETION vs. MOOD & SLEEP CORRELATION",
                    "name_font": {"name": t.font, "size": 9.5, "bold": True, "color": t.ink}})
    corr.set_y_axis({"min": 0, "max": 1, "major_unit": 0.25, "num_format": "0%",
                     "num_font": axis_font(t), "line": {"none": True},
                     "major_gridlines": {"visible": True, "line": {"color": t.line, "dash_type": "dash"}}})
    corr.set_x_axis({"num_font": axis_font(t, 7.5), "line": {"color": t.line}, "position_axis": "on_tick"})
    corr.set_legend({"position": "top", "font": {"name": t.font, "size": 8.5, "color": t.ink}})
    corr.set_chartarea({"border": {"color": t.line, "width": 0.75}, "fill": {"color": t.card}})
    corr.set_plotarea({"layout": {"x": 0.045, "y": 0.22, "width": 0.935, "height": 0.64}})
    place_chart(cv, corr, r_ch0, C_NAME, r_ch1, C_D31)

    # Right Wellness Tip / Sleep Hygiene Card next to chart
    cv.merge(r_ch0, C_R0, r_ch0, C_RE, "🌙  WELLNESS INSIGHTS", bold=True, font_size=9,
             align="center", bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r_ch0 + 1, C_R0, r_ch0 + 3, C_RE,
             f'=IF({avg_sleep_addr}>=7.5,"✨ Giấc ngủ rất tốt! Bạn đang duy trì nền tảng năng lượng tuyệt vời.",'
             f'"🌙 Gợi ý: Hãy thử ngủ sớm hơn 30 phút để tăng mức năng lượng & hoàn thành thói quen!")',
             font_size=9, align="center", text_wrap=True, bg_color=t.soft, font_color=t.ink)
    cv.merge(r_ch0 + 4, C_R0, r_ch0 + 6, C_RE,
             f'=IF({avg_mood_addr}>=4,"💜 Tâm trạng trung bình rất tích cực! Ghi lại điều bạn biết ơn ở tab bên cạnh.",'
             f'"🪻 Dành 10 phút hít thở sâu hoặc đi bộ nhẹ để cân bằng cảm xúc nhé.")',
             font_size=9, align="center", text_wrap=True, bg_color=t.card, font_color=t.ink)
    cv.merge(r_ch0 + 7, C_R0, r_ch1, C_RE,
             f'="🌕 Đêm trăng tròn (≥75%): "&{tr.s["grown"]}&" / "&{tr.s["dim"]}&" ngày"',
             bold=True, font_size=9.5, align="center", bg_color=t.soft, font_color=t.primary_dark)
    cv.box(r_ch0, C_R0, r_ch1, C_RE, t.line)

    return {
        "avg_sleep": f"{q}!{avg_sleep_addr}",
        "avg_mood": f"{q}!{avg_mood_addr}",
        "avg_energy": f"{q}!{avg_energy_addr}",
        "great_days": f"{q}!{great_days_addr}",
    }


# --------------------------------------------------------------------------- #
#  Template 6 (Midnight Navy Focus): Gamified Top-Right Rank & XP Card
# --------------------------------------------------------------------------- #
def add_focus_rank_top_card(wb, cv: Canvas, tr: TrackerRefs, total_xp_addr: str):
    """High-contrast Deep Navy + Blush Gamification Rank Card in R_BAND0..R_BAND1."""
    t = cv.t
    C_RE = tr.c_right_end
    xp = total_xp_addr
    cv.box(R_BAND0, C_R0, R_BAND1, C_RE, t.primary, fill=t.card)
    cv.merge(R_BAND0, C_R0, R_BAND0, C_RE, "🏆  GAMIFICATION RANK & XP", bold=True, font_size=8.5,
             align="center", bg_color=t.primary, font_color=t.on_primary)

    # Left half: Total XP + Consistency %
    mid = C_R0 + 2
    cv.merge(R_BAND0 + 1, C_R0, R_BAND0 + 2, mid, f"={xp}", bold=True, font_size=18, align="center",
             num_format='#,##0" XP"', bg_color=t.card, font_color=t.primary, font_name=t.font_title)
    cv.merge(R_BAND0 + 3, C_R0, R_BAND0 + 3, mid,
             f'="Consistency: "&TEXT({tr.s["overall"]},"0%")', bold=True, font_size=8.5,
             align="center", bg_color=t.soft, font_color=t.ink)
    cv.merge(R_BAND0 + 4, C_R0, R_BAND1, mid,
             f'="🔥 Best Streak: "&{tr.s["best"]}&" ngày"&CHAR(10)&"🚀 Orbit Days: "&{tr.s["perfect"]}',
             font_size=8, align="center", text_wrap=True, bg_color=t.card, font_color=t.muted)

    # Right half: Rank Tier badge + Progress toward Master (3000 XP)
    cv.merge(R_BAND0 + 1, mid + 1, R_BAND0 + 1, C_RE, "CURRENT RANK TIER", bold=True, font_size=7.5,
             align="center", bg_color=t.card, font_color=t.muted)
    cv.merge(R_BAND0 + 2, mid + 1, R_BAND0 + 3, C_RE,
             f'=IF({xp}>=3000,"👑 MASTER",IF({xp}>=1800,"🔥 UNSTOPPABLE",IF({xp}>=800,"⚡ CONSISTENT","🌱 BEGINNER")))',
             bold=True, font_size=12, align="center", bg_color=t.soft, font_color=t.primary,
             font_name=t.font_title)
    cv.merge(R_BAND0 + 4, mid + 1, R_BAND0 + 4, C_RE,
             f'=IF({xp}>=3000,"Đã đạt đỉnh Master!",IF({xp}>=1800,"Còn "&(3000-{xp})&" XP → Master",'
             f'IF({xp}>=800,"Còn "&(1800-{xp})&" XP → Unstoppable","Còn "&(800-{xp})&" XP → Consistent")))',
             font_size=8, italic=True, align="center", bg_color=t.card, font_color=t.muted)
    cv.merge(R_BAND1, mid + 1, R_BAND1, C_RE, f"=MIN(1,{xp}/3000)", bold=True, font_size=8.5,
             align="center", num_format='0%" → Master"', bg_color=t.card, font_color=t.primary)
    cv.ws.conditional_format(rng(R_BAND1, mid + 1, R_BAND1, C_RE),
                             {"type": "data_bar", "bar_color": t.bar, "bar_solid": True,
                              "min_type": "num", "min_value": 0, "max_type": "num", "max_value": 1})


# --------------------------------------------------------------------------- #
#  Template 7 (Sakura Zen Study): Daily Focus Hours Log + Focus Hours Chart
# --------------------------------------------------------------------------- #
def add_sakura_study_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 77) -> dict:
    t = cv.t
    ws = cv.ws
    q = tr.q
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23)
    cv.row(r0 + 1, 24)
    cv.row(r0 + 2, 23)

    cv.put(r0, C_NAME, "🌸  DAILY FOCUS HOURS", bold=True, font_size=9.5, align="left", indent=1,
           bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_D0, r0, C_D31, "SỐ GIỜ HỌC TẬP / DEEP WORK MỖI NGÀY (NHẬP SỐ GIỜ TỪ 0 – 12)",
             bold=True, font_size=8.5, align="center", bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_R0, r0, C_RE, "📚  STUDY SUMMARY", bold=True, font_size=8.5, align="center",
             bg_color=t.primary, font_color=t.on_primary)

    r_hrs, r_pom = r0 + 1, r0 + 2
    cv.put(r_hrs, C_NAME, "⏱️  Giờ tập trung (Focus Hours)", bold=True, font_size=9, align="left",
           indent=1, bg_color=t.soft, font_color=t.ink)
    cv.put(r_pom, C_NAME, "🍅  Pomodoro (25m sessions)", bold=True, font_size=9, align="left",
           indent=1, bg_color=t.card, font_color=t.muted)

    rnd = random.Random(seed)
    for k in range(1, 32):
        c = day_col(k)
        if k > 22:
            cv.put(r_hrs, c, "", align="center", font_size=8.5, bg_color=t.card, num_format="0.0")
            cv.put(r_pom, c, f'=IF({cell(r_hrs, c)}="","",ROUND({cell(r_hrs, c)}*2,0))',
                   align="center", font_size=8.5, bg_color=t.card, font_color=t.muted)
            continue
        hrs = rnd.choice([2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 3.5, 4.0, 2.0, 5.5])
        cv.put(r_hrs, c, hrs, align="center", font_size=8.5, bold=True, bg_color=t.card,
               font_color=t.ink, num_format="0.0")
        cv.put(r_pom, c, f'=IF({cell(r_hrs, c)}="","",ROUND({cell(r_hrs, c)}*2,0))',
               align="center", font_size=8.5, bg_color=t.card, font_color=t.muted)

    hrs_rng = rng(r_hrs, C_D0, r_hrs, C_D31)
    cv.grid(r_hrs, C_NAME, r_pom, C_D31, t.line)
    cv.box(r0, C_NAME, r_pom, C_D31, t.line)
    ws.conditional_format(hrs_rng, {"type": "3_color_scale", "min_type": "num", "min_value": 0,
                                    "mid_type": "num", "mid_value": 3, "max_type": "num", "max_value": 6,
                                    "min_color": "#FFFBF7", "mid_color": "#FCE0E7", "max_color": "#E899AE"})

    tot_hrs_addr = acell(r_hrs, C_R0 + 3)
    avg_hrs_addr = acell(r_pom, C_R0 + 3)
    cv.merge(r_hrs, C_R0, r_hrs, C_R0 + 2, "Tổng giờ học tháng:", font_size=9, align="left", indent=1,
             bg_color=t.card, font_color=t.muted)
    cv.merge(r_hrs, C_R0 + 3, r_hrs, C_RE, f"=SUM({hrs_rng})", bold=True, font_size=11, align="center",
             num_format='0.0" h"', bg_color=t.soft, font_color=t.primary_dark)
    cv.merge(r_pom, C_R0, r_pom, C_R0 + 2, "Trung bình / ngày học:", font_size=9, align="left", indent=1,
             bg_color=t.card, font_color=t.muted)
    cv.merge(r_pom, C_R0 + 3, r_pom, C_RE, f"=IFERROR(AVERAGE({hrs_rng}),0)", bold=True, font_size=10,
             align="center", num_format='0.0" h/ngày"', bg_color=t.card, font_color=t.ink)
    cv.hline(r_hrs, C_R0, C_RE, t.line)
    cv.box(r0, C_R0, r_pom, C_RE, t.line)

    # Focus Hours Column Chart below
    r_ch0, r_ch1 = r_pom + 2, r_pom + 9
    cv.row(r_ch0 - 1, 10)
    for rr in range(r_ch0, r_ch1 + 1):
        cv.row(rr, 20)
    ch = wb.add_chart({"type": "column"})
    ch.add_series({
        "name": "Focus Hours",
        "categories": f"={q}!{rng(R_DAY, C_D0, R_DAY, C_D31)}",
        "values": f"={q}!{hrs_rng}",
        "fill": {"color": "#F2A4B8"},
        "border": {"none": True},
        "gap": 50,
    })
    ch.set_title({"name": "DAILY DEEP WORK & STUDY HOURS (GIỜ TẬP TRUNG MỖI NGÀY)",
                  "name_font": {"name": t.font, "size": 9.5, "bold": True, "color": t.ink}})
    ch.set_y_axis({"min": 0, "max": 8, "major_unit": 2, "num_format": '0"h"',
                   "num_font": axis_font(t), "line": {"none": True},
                   "major_gridlines": {"visible": True, "line": {"color": t.line, "dash_type": "dash"}}})
    ch.set_x_axis({"num_font": axis_font(t, 7.5), "line": {"color": t.line}})
    ch.set_legend({"none": True})
    ch.set_chartarea({"border": {"color": t.line, "width": 0.75}, "fill": {"color": t.card}})
    place_chart(cv, ch, r_ch0, C_NAME, r_ch1, C_D31)

    cv.merge(r_ch0, C_R0, r_ch0, C_RE, "🌸  ZEN STUDY NOTES", bold=True, font_size=9, align="center",
             bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r_ch0 + 1, C_R0, r_ch0 + 4, C_RE,
             "• Ưu tiên 2 phiên Deep Work 90 phút vào buổi sáng.\n• Tắt thông báo điện thoại khi học.\n• Ôn tập lại ghi chú mỗi tối Chủ nhật.",
             font_size=9, align="left", indent=1, text_wrap=True, bg_color=t.card, font_color=t.ink)
    cv.merge(r_ch0 + 5, C_R0, r_ch1, C_RE,
             f'="🌸 Ngày nở hoa: "&{tr.s["grown"]}&" ngày"&CHAR(10)&"🍅 Tổng Pomodoro: "&SUM({rng(r_pom, C_D0, r_pom, C_D31)})&" phiên"',
             bold=True, font_size=9.5, align="center", text_wrap=True, bg_color=t.soft, font_color=t.primary_dark)
    cv.box(r_ch0, C_R0, r_ch1, C_RE, t.line)
    return {"total_hrs": f"{q}!{tot_hrs_addr}", "avg_hrs": f"{q}!{avg_hrs_addr}"}


# --------------------------------------------------------------------------- #
#  Template 8 (Ocean Coral Fitness): Energy + Water Bar + 5 Weekly Donut Gauges
# --------------------------------------------------------------------------- #
def add_ocean_fitness_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 88) -> dict:
    t = cv.t
    ws = cv.ws
    q = tr.q
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23)
    cv.row(r0 + 1, 22)
    cv.row(r0 + 2, 22)

    cv.put(r0, C_NAME, "🪸  ENERGY & HYDRATION LOG", bold=True, font_size=9.5, align="left", indent=1,
           bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_D0, r0, C_D31, "NĂNG LƯỢNG MỖI NGÀY (1–5)  •  LƯỢNG NƯỚC UỐNG (LÍT)",
             bold=True, font_size=8.5, align="center", bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_R0, r0, C_RE, "💧  FITNESS VITALS", bold=True, font_size=8.5, align="center",
             bg_color=t.primary, font_color=t.on_primary)

    r_en, r_wat = r0 + 1, r0 + 2
    cv.put(r_en, C_NAME, "⚡  Năng lượng (Energy 1–5)", bold=True, font_size=9, align="left",
           indent=1, bg_color=t.soft, font_color=t.ink)
    cv.put(r_wat, C_NAME, "💧  Lượng nước (Water Liters)", bold=True, font_size=9, align="left",
           indent=1, bg_color=t.card, font_color=t.ink)

    rnd = random.Random(seed)
    for k in range(1, 32):
        c = day_col(k)
        if k > 22:
            cv.put(r_en, c, "", align="center", font_size=8.5, bg_color=t.card, num_format="0")
            cv.put(r_wat, c, "", align="center", font_size=8.5, bg_color=t.card, num_format="0.0")
            continue
        cv.put(r_en, c, rnd.choice([3, 4, 4, 5, 4, 5, 3, 5, 4]), align="center", font_size=9,
               bold=True, bg_color=t.card, font_color=t.ink, num_format="0")
        cv.put(r_wat, c, rnd.choice([1.8, 2.0, 2.2, 2.5, 2.5, 2.8, 2.0, 2.4, 3.0]), align="center",
               font_size=8.5, bg_color=t.card, font_color=t.ink, num_format="0.0")

    en_rng = rng(r_en, C_D0, r_en, C_D31)
    wat_rng = rng(r_wat, C_D0, r_wat, C_D31)
    cv.grid(r_en, C_NAME, r_wat, C_D31, t.line)
    cv.box(r0, C_NAME, r_wat, C_D31, t.line)
    ws.conditional_format(en_rng, {"type": "3_color_scale", "min_type": "num", "min_value": 1,
                                   "mid_type": "num", "mid_value": 3, "max_type": "num", "max_value": 5,
                                   "min_color": "#FDECE6", "mid_color": "#F8D5C4", "max_color": "#F4A582"})
    ws.conditional_format(wat_rng, {"type": "3_color_scale", "min_type": "num", "min_value": 1.0,
                                    "mid_type": "num", "mid_value": 2.0, "max_type": "num", "max_value": 3.0,
                                    "min_color": "#FFFFFF", "mid_color": "#D4F1EC", "max_color": "#64BFB8"})

    avg_en_addr = acell(r_en, C_R0 + 3)
    avg_wat_addr = acell(r_wat, C_R0 + 3)
    cv.merge(r_en, C_R0, r_en, C_R0 + 2, "Năng lượng TB (/5):", font_size=9, align="left", indent=1,
             bg_color=t.card, font_color=t.muted)
    cv.merge(r_en, C_R0 + 3, r_en, C_RE, f"=IFERROR(AVERAGE({en_rng}),0)", bold=True, font_size=10,
             align="center", num_format='0.0" ⚡"', bg_color="#FDF1EC", font_color="#C46B48")
    cv.merge(r_wat, C_R0, r_wat, C_R0 + 2, "Nước uống TB / ngày:", font_size=9, align="left", indent=1,
             bg_color=t.card, font_color=t.muted)
    cv.merge(r_wat, C_R0 + 3, r_wat, C_RE, f"=IFERROR(AVERAGE({wat_rng}),0)", bold=True, font_size=10,
             align="center", num_format='0.0" L"', bg_color=t.soft, font_color=t.primary)
    cv.hline(r_en, C_R0, C_RE, t.line)
    cv.box(r0, C_R0, r_wat, C_RE, t.line)

    # 5 Weekly Lagoon & Coral Donut Gauges right below
    rd = r_wat + 2
    cv.row(rd - 1, 10)
    for rr in range(rd, rd + 5):
        cv.row(rr, 22)
    cv.merge(rd, C_NAME, rd + 4, C_NAME, "🌊  WEEKLY FITNESS GAUGES\nTiến độ 5 tuần", bold=True,
             font_size=10.5, align="center", text_wrap=True, bg_color=t.card, font_color=t.primary,
             font_name=t.font_title)
    rb = tr.calc_row_base
    spans = [(2, 7), (8, 13), (14, 19), (20, 25), (26, 32)]
    dcols = ["#2E7D87", "#48A9A6", "#F4A582", "#3B9A9C", "#E88B68"]
    for w, (c1, c2) in enumerate(spans):
        hc = CALC_WK_COL0 + w
        cv.merge(rd, c1, rd, c2, f"WEEK {w + 1}", bold=True, font_size=8.5, align="center",
                 bg_color=t.week_head[w], font_color=t.week_on[w])
        cv.merge(rd + 1, c1, rd + 4, c2, f"={tr.calc_q}!{acell(rb + 2, hc)}", bold=True, font_size=13,
                 align="center", num_format="0%", bg_color=t.card, font_color=dcols[w], font_name=t.font_title)
        dch = donut(wb, f"={tr.calc_q}!{rng(rb + 2, hc, rb + 3, hc)}", [dcols[w], t.donut_rest], hole=70)
        place_chart(cv, dch, rd + 1, c1, rd + 4, c2, pad_x=10, pad_y=2)
        cv.vline(c2, rd, rd + 4, t.line, where="right")
    cv.box(rd, C_NAME, rd + 4, C_D31, t.line)

    cv.merge(rd, C_R0, rd, C_RE, "🪸  REEF MILESTONE", bold=True, font_size=9, align="center",
             bg_color=t.primary, font_color=t.on_primary)
    cv.merge(rd + 1, C_R0, rd + 4, C_RE,
             f'="🦪 Ngày rạn san hô tỏa sáng: "&{tr.s["grown"]}&" ngày"&CHAR(10)&'
             f'"🔥 Kỷ lục Streak: "&{tr.s["best"]}&" ngày"&CHAR(10)&'
             f'"💧 Tổng nước tháng: "&TEXT(SUM({wat_rng}),"0.0")&" Lít"',
             bold=True, font_size=9.5, align="center", text_wrap=True, bg_color=t.card, font_color=t.ink)
    cv.box(rd, C_R0, rd + 4, C_RE, t.line)
    return {"avg_energy": f"{q}!{avg_en_addr}", "avg_water": f"{q}!{avg_wat_addr}"}


# --------------------------------------------------------------------------- #
#  Template 9 (Matcha Cafe Routine): Morning vs Evening Ratio + Mood + Cozy Box
# --------------------------------------------------------------------------- #
def add_matcha_routine_block(wb, cv: Canvas, tr: TrackerRefs, morning_count: int = 5,
                             evening_count: int = 5, seed: int = 99) -> dict:
    from .tracker import R_H0, CALC_DONEN_COL, CALC_GOALN_COL
    t = cv.t
    ws = cv.ws
    q = tr.q
    cq = tr.calc_q
    C_RE = tr.c_right_end

    r0 = R_EXTRA
    cv.row(r0, 23)
    cv.row(r0 + 1, 24)
    cv.row(r0 + 2, 10)
    for rr in range(r0 + 3, r0 + 8):
        cv.row(rr, 22)

    # Daily Mood Check-in Row (1..5)
    cv.put(r0, C_NAME, "🍵  DAILY CAFE MOOD CHECK-IN", bold=True, font_size=9.5, align="left", indent=1,
           bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_D0, r0, C_D31, "TÂM TRẠNG & NĂNG LƯỢNG HẰNG NGÀY (THANG 1 – 5)",
             bold=True, font_size=8.5, align="center", bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_R0, r0, C_RE, "☕  MOOD AVG", bold=True, font_size=8.5, align="center",
             bg_color=t.primary, font_color=t.on_primary)

    r_mood = r0 + 1
    cv.put(r_mood, C_NAME, "✨  Tâm trạng trong ngày (1–5)", bold=True, font_size=9, align="left",
           indent=1, bg_color=t.soft, font_color=t.ink)
    rnd = random.Random(seed)
    for k in range(1, 32):
        c = day_col(k)
        val = "" if k > 22 else rnd.choice([3, 4, 4, 5, 4, 5, 4, 3, 5])
        cv.put(r_mood, c, val, align="center", font_size=9, bold=True, bg_color=t.card,
               font_color=t.ink, num_format="0")
    mood_rng = rng(r_mood, C_D0, r_mood, C_D31)
    cv.grid(r_mood, C_NAME, r_mood, C_D31, t.line)
    cv.box(r0, C_NAME, r_mood, C_D31, t.line)
    ws.conditional_format(mood_rng, {"type": "3_color_scale", "min_type": "num", "min_value": 1,
                                     "mid_type": "num", "mid_value": 3, "max_type": "num", "max_value": 5,
                                     "min_color": "#F7ECE1", "mid_color": "#E8D5BA", "max_color": "#A8C294"})
    cv.merge(r_mood, C_R0, r_mood, C_RE, f'=IFERROR(AVERAGE({mood_rng}),0)', bold=True, font_size=12,
             align="center", num_format='0.0" / 5 ☕"', bg_color=t.card, font_color=t.primary_dark)
    cv.box(r0, C_R0, r_mood, C_RE, t.line)

    # Bottom Split Cards: Morning Routine % | Evening Routine % | Cozy Weekly Reflection Box
    rc0 = r0 + 3
    rb = tr.calc_row_base
    m_done = f"{cq}!{rng(rb + R_H0, CALC_DONEN_COL, rb + R_H0 + morning_count - 1, CALC_DONEN_COL)}"
    m_goal = f"{cq}!{rng(rb + R_H0, CALC_GOALN_COL, rb + R_H0 + morning_count - 1, CALC_GOALN_COL)}"
    e_done = f"{cq}!{rng(rb + R_H0 + morning_count, CALC_DONEN_COL, rb + R_H0 + morning_count + evening_count - 1, CALC_DONEN_COL)}"
    e_goal = f"{cq}!{rng(rb + R_H0 + morning_count, CALC_GOALN_COL, rb + R_H0 + morning_count + evening_count - 1, CALC_GOALN_COL)}"

    m_pct_addr = acell(rc0 + 1, C_NAME)
    e_pct_addr = acell(rc0 + 1, C_D0)

    # Card 1: Morning Routine Ratio (Col B)
    cv.put(rc0, C_NAME, "☀️  MORNING ROUTINE (SÁNG)", bold=True, font_size=9.5, align="center",
           bg_color="#D4A373", font_color="#FFFFFF")
    cv.merge(rc0 + 1, C_NAME, rc0 + 3, C_NAME, f"=IFERROR(SUM({m_done})/SUM({m_goal}),0)", bold=True,
             font_size=22, align="center", num_format="0%", bg_color=t.card, font_color="#8A5E3B",
             font_name=t.font_title)
    cv.put(rc0 + 4, C_NAME, f'=SUM({m_done})&" / "&SUM({m_goal})&" lượt sáng hoàn thành"',
           font_size=8.8, align="center", bg_color="#F8EFE4", font_color=t.ink)
    cv.box(rc0, C_NAME, rc0 + 4, C_NAME, t.line)

    # Card 2: Evening Routine Ratio (Cols C..L)
    cv.merge(rc0, C_D0, rc0, C_D0 + 9, "🌙  EVENING ROUTINE (TỐI)", bold=True, font_size=9.5,
             align="center", bg_color="#5C4033", font_color="#FFFFFF")
    cv.merge(rc0 + 1, C_D0, rc0 + 3, C_D0 + 9, f"=IFERROR(SUM({e_done})/SUM({e_goal}),0)", bold=True,
             font_size=22, align="center", num_format="0%", bg_color=t.card, font_color="#5C4033",
             font_name=t.font_title)
    cv.merge(rc0 + 4, C_D0, rc0 + 4, C_D0 + 9, f'=SUM({e_done})&" / "&SUM({e_goal})&" lượt tối hoàn thành"',
             font_size=8.8, align="center", bg_color="#F3ECE7", font_color=t.ink)
    cv.box(rc0, C_D0, rc0 + 4, C_D0 + 9, t.line)

    # Card 3: Cozy Weekly Reflection Box (Cols M..AG + Right side!)
    cv.merge(rc0, C_D0 + 11, rc0, C_RE, "☕  COZY WEEKLY REFLECTION • GÓC NHÂM NHI & SUY NGẪM",
             bold=True, font_size=9.5, align="left", indent=1, bg_color=t.primary, font_color=t.on_primary)
    reflections = [
        "• Nghi thức buổi sáng yêu thích nhất tuần này: Pha ly matcha ấm & viết 3 mục tiêu trong yên tĩnh.",
        "• Điều giúp buổi tối nhẹ nhàng hơn: Tắt màn hình sớm 30 phút & đọc sách giấy dưới đèn vàng.",
        "• Phần thưởng nhỏ cho bản thân cuối tuần: Ghé quán cafe yên tĩnh yêu thích & nghỉ ngơi trọn vẹn.",
        "",
    ]
    for i, line in enumerate(reflections):
        cv.merge(rc0 + 1 + i, C_D0 + 11, rc0 + 1 + i, C_RE, line, font_size=9, align="left", indent=1,
                 bg_color=t.card, font_color=t.ink)
        cv.hline(rc0 + 1 + i, C_D0 + 11, C_RE, t.line)
    cv.box(rc0, C_D0 + 11, rc0 + 4, C_RE, t.line)

    return {"morning_pct": f"{q}!{m_pct_addr}", "evening_pct": f"{q}!{e_pct_addr}",
            "avg_mood": f"{q}!{acell(r_mood, C_R0)}"}


# --------------------------------------------------------------------------- #
#  Template 10 (Aurora Glow RPG): Hero Level, Rank & Combo XP Card
# --------------------------------------------------------------------------- #
def add_aurora_rpg_top_card(wb, cv: Canvas, tr: TrackerRefs, total_xp_addr: str):
    """Nordic Slate + Aurora Mint/Violet RPG Hero Level & Rank Card in R_BAND0..R_BAND1."""
    t = cv.t
    C_RE = tr.c_right_end
    xp = total_xp_addr
    mid = C_R0 + 3
    cv.box(R_BAND0, C_R0, R_BAND1, C_RE, t.primary, fill=t.card)
    cv.merge(R_BAND0, C_R0, R_BAND0, C_RE, "⚔️  RPG HERO STATUS & AURORA LEVEL", bold=True,
             font_size=8.5, align="center", bg_color=t.primary, font_color="#4FD1C5")

    # Left half: Character Level + Total XP (with Streak Combo Multiplier!)
    cv.merge(R_BAND0 + 1, C_R0, R_BAND0 + 2, mid,
             f'="LV. "&(1+INT({xp}/300))&"  •  "&TEXT({xp},"#,##0")&" XP"',
             bold=True, font_size=14, align="center", bg_color=t.card, font_color=t.primary,
             font_name=t.font_title)
    cv.merge(R_BAND0 + 3, C_R0, R_BAND0 + 3, mid,
             f'="Consistency: "&TEXT({tr.s["overall"]},"0%")&"  •  Best Combo: "&{tr.s["best"]}&"d"',
             bold=True, font_size=8.2, align="center", bg_color=t.soft, font_color=t.ink)
    cv.merge(R_BAND0 + 4, C_R0, R_BAND1, mid,
             f'="✨ Aurora Days (≥75%): "&{tr.s["grown"]}&"  •  Perfect 100%: "&{tr.s["perfect"]}',
             font_size=8.2, align="center", bg_color=t.card, font_color=t.muted)

    # Right half: Rank Badge (Novice -> Apprentice -> Warrior -> Master -> Legend)
    cv.merge(R_BAND0 + 1, mid + 1, R_BAND0 + 1, C_RE, "HERO RANK CLASS", bold=True, font_size=7.5,
             align="center", bg_color=t.card, font_color=t.muted)
    cv.merge(R_BAND0 + 2, mid + 1, R_BAND0 + 3, C_RE,
             f'=IF({xp}>=4500,"👑 LEGEND",IF({xp}>=3000,"🌌 MASTER",IF({xp}>=1800,"⚔️ WARRIOR",'
             f'IF({xp}>=800,"🛡️ APPRENTICE","🌱 NOVICE"))))',
             bold=True, font_size=12, align="center", bg_color="#EDE9FE", font_color="#5B3FA8",
             font_name=t.font_title)
    cv.merge(R_BAND0 + 4, mid + 1, R_BAND0 + 4, C_RE,
             f'=IF({xp}>=4500,"Đã đạt cảnh giới Legend!",'
             f'IF({xp}>=3000,"Còn "&(4500-{xp})&" XP → Legend",'
             f'IF({xp}>=1800,"Còn "&(3000-{xp})&" XP → Master",'
             f'IF({xp}>=800,"Còn "&(1800-{xp})&" XP → Warrior","Còn "&(800-{xp})&" XP → Apprentice"))))',
             font_size=7.8, italic=True, align="center", bg_color=t.card, font_color=t.muted)
    cv.merge(R_BAND1, mid + 1, R_BAND1, C_RE, f"=MIN(1,{xp}/4500)", bold=True, font_size=8.5,
             align="center", num_format='0%" → Legend"', bg_color=t.card, font_color=t.primary)
    cv.ws.conditional_format(rng(R_BAND1, mid + 1, R_BAND1, C_RE),
                             {"type": "data_bar", "bar_color": "#4FD1C5", "bar_solid": True,
                              "min_type": "num", "min_value": 0, "max_type": "num", "max_value": 1})
