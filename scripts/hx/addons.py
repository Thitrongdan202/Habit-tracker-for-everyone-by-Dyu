"""
hx.addons — Template-specific in-sheet dashboard blocks mounted onto the main tracker sheet.
"""
from __future__ import annotations

import random

from .core import Canvas, acell, cell, colname, rng, donut, place_chart, axis_font
from .tracker import (C_NAME, C_D0, C_D31, C_R0, CALC_WK_COL0, CALC_DONUT_COL, R_BAND0, R_BAND1, R_DONE, R_NOT,
                      R_PCT, R_DAY, R_EXTRA, TrackerRefs, day_col, week_days, mood_lookup_ref,
                      mood6_lookup_ref, MOOD6_OPTIONS, MOOD6_LABELS)


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


# --------------------------------------------------------------------------- #
#  Template 16 (Dream Home Architect): Success Notes + Failure / Lessons Notes
# --------------------------------------------------------------------------- #
def add_dream_house_notes_block(wb, cv: Canvas, tr: TrackerRefs):
    """Side-by-side Emerald Success Notes + Coral Failure/Lessons Notes + Architect Milestone Card."""
    t = cv.t
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 24)
    for rr in range(r0 + 1, r0 + 6):
        cv.row(rr, 22)

    # Left half: SUCCESS NOTES (Emerald Green #0D9468) — Col B .. Col Q (1..16)
    c_mid = 16
    cv.merge(r0, C_NAME, r0, c_mid, "🏆  SUCCESS NOTES  •  ĐIỂM SÁNG & THÀNH CÔNG TRONG THÁNG",
             bold=True, font_size=9.5, align="left", indent=1, bg_color="#0D9468", font_color="#FFFFFF")
    success_lines = [
        "✓  Duy trì tập thể dục buổi sáng đều đặn 5 buổi/tuần — tinh thần tỉnh táo hẳn lên!",
        "✓  Hoàn thành kỷ luật tắt điện thoại trước 22h30 giúp ngủ sâu hơn mỗi đêm.",
        "✓  Kiểm soát chi tiêu tốt hơn nhờ ghi chép đều đặn cuối ngày.",
        "",
        "",
    ]
    for i, txt in enumerate(success_lines):
        cv.merge(r0 + 1 + i, C_NAME, r0 + 1 + i, c_mid, txt, font_size=9.5, align="left", indent=1,
                 bg_color="#FFFFFF", font_color=t.ink)
        cv.hline(r0 + 1 + i, C_NAME, c_mid, "#D1FAE5")
    cv.box(r0, C_NAME, r0 + 5, c_mid, "#0D9468")

    # Middle half: FAILURE / LESSONS NOTES (Coral Red #E63956) — Col S .. Col AG (18..32)
    c_fail0 = c_mid + 2
    cv.merge(r0, c_fail0, r0, C_D31, "💡  FAILURE / LESSONS NOTES  •  BÀI HỌC & ĐIỀU CẦN CẢI THIỆN",
             bold=True, font_size=9.5, align="left", indent=1, bg_color="#E63956", font_color="#FFFFFF")
    fail_lines = [
        "•  Giữa tuần hơi lơ là đọc sách vì thức khuya làm việc → đặt báo thức 21h30.",
        "•  Hạn chế đồ ăn nhanh vào cuối tuần còn khó → chuẩn bị sẵn đồ ăn nhẹ lành mạnh.",
        "•  Chủ nhật nên lên kế hoạch tuần sớm hơn để tránh quá tải sáng thứ Hai.",
        "",
        "",
    ]
    for i, txt in enumerate(fail_lines):
        cv.merge(r0 + 1 + i, c_fail0, r0 + 1 + i, C_D31, txt, font_size=9.5, align="left", indent=1,
                 bg_color="#FFFFFF", font_color=t.ink)
        cv.hline(r0 + 1 + i, c_fail0, C_D31, "#FFE4E6")
    cv.box(r0, c_fail0, r0 + 5, C_D31, "#E63956")

    # Right summary card: DREAM HOME ARCHITECT STATUS (C_R0..C_RE)
    cv.merge(r0, C_R0, r0, C_RE, "🏡  ARCHITECT MILESTONE", bold=True, font_size=9, align="center",
             bg_color="#F5B800", font_color="#1E293B")
    cv.merge(r0 + 1, C_R0, r0 + 2, C_RE,
             f'=IF({tr.s["overall"]}>=0.99,"🏛️ LUXURY VILLA",'
             f'IF({tr.s["overall"]}>=0.75,"🏡 2-STORY HOUSE",'
             f'IF({tr.s["overall"]}>=0.5,"🏠 COZY COTTAGE",'
             f'IF({tr.s["overall"]}>=0.25,"🛖 WOODEN HUT",'
             f'IF({tr.s["overall"]}>0,"⛺ CAMPING TENT","🔥 CAMPFIRE")))))',
             bold=True, font_size=12, align="center", bg_color="#FFFFFF", font_color="#0D9468",
             font_name=t.font_title)
    cv.merge(r0 + 3, C_R0, r0 + 3, C_RE,
             f'="Tiến độ xây nhà: "&TEXT({tr.s["overall"]},"0%")',
             bold=True, font_size=9, align="center", bg_color="#ECFDF5", font_color="#065F46")
    cv.merge(r0 + 4, C_R0, r0 + 5, C_RE,
             f'="🏗️ Hoàn thành: "&{tr.s["tdone"]}&" / "&{tr.s["tgoal"]}&" lượt"&CHAR(10)&'
             f'"🔥 Chuỗi bền nhất: "&{tr.s["best"]}&" ngày"',
             font_size=8.8, align="center", text_wrap=True, bg_color="#FFFFFF", font_color=t.ink)
    cv.box(r0, C_R0, r0 + 5, C_RE, "#F5B800")


# --------------------------------------------------------------------------- #
#  Template 17 (Wildflower Bloom): Daily Mood Emoji Check-in Row + Mood Counter
# --------------------------------------------------------------------------- #
def add_wildflower_mood_row(wb, cv: Canvas, tr: TrackerRefs, seed: int = 171):
    """Dedicated Daily Mood Emoji dropdown row (😊 / 😐 / 😢) directly beneath habit grid."""
    t = cv.t
    ws = cv.ws
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23)
    cv.row(r0 + 1, 20)
    cv.row(r0 + 2, 28)

    cv.merge(r0, C_NAME, r0, C_D31,
             "🌸  DAILY MOOD CHECK-IN  •  TÂM TRẠNG MỖI NGÀY   (Chọn ô ngày bên dưới:  😊 Vui vẻ  •  😐 Bình thường  •  😢 Mệt mỏi)",
             bold=True, font_size=9.5, align="left", indent=1, bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_R0, r0, C_RE, "💛  MOOD SUMMARY", bold=True, font_size=9, align="center",
             bg_color=t.primary, font_color=t.on_primary)

    cv.put(r0 + 1, C_NAME, "Ngày trong tháng (Day 1–31)", bold=True, font_size=8.5, align="left",
           indent=1, bg_color=t.soft, font_color=t.muted)
    cv.put(r0 + 2, C_NAME, "Tâm trạng hôm nay (Click chọn)", bold=True, font_size=9.5,
           align="left", indent=1, bg_color=t.card, font_color=t.ink)

    rnd = random.Random(seed)
    mood_pool = ["😊", "😊", "😊", "😊", "😐", "😐", "😢"]
    for k in range(1, 32):
        c = day_col(k)
        w = (k - 1) // 7
        dc = cell(R_DAY, c, row_abs=True)
        cv.put(r0 + 1, c, f'=IF({dc}="","",{k})', align="center", font_size=8, bold=True,
               bg_color=t.week_tint[w], font_color=t.ink)
        val = rnd.choice(mood_pool) if k <= 22 else ""
        cv.put(r0 + 2, c, val, align="center", font_size=13, bg_color=t.card, font_color=t.ink)

    mood_rng = rng(r0 + 2, C_D0, r0 + 2, C_D31)
    ws.data_validation(mood_rng, {
        "validate": "list",
        "source": f"={mood_lookup_ref()}",
        "input_title": "Chọn Tâm Trạng (Daily Mood)",
        "input_message": "😊 = Vui vẻ  |  😐 = Bình thường  |  😢 = Mệt mỏi",
    })
    # Subtle pastel highlight per mood emoji
    tl = cell(r0 + 2, C_D0)
    ws.conditional_format(mood_rng, {"type": "formula", "criteria": f'={tl}="😊"',
                                     "format": wb.add_format({"bg_color": "#DCFCE7"})})
    ws.conditional_format(mood_rng, {"type": "formula", "criteria": f'={tl}="😐"',
                                     "format": wb.add_format({"bg_color": "#FEF3C7"})})
    ws.conditional_format(mood_rng, {"type": "formula", "criteria": f'={tl}="😢"',
                                     "format": wb.add_format({"bg_color": "#FFE4E6"})})

    cv.grid(r0 + 1, C_NAME, r0 + 2, C_D31, t.line)
    cv.box(r0, C_NAME, r0 + 2, C_D31, t.line)

    # Right Mood Counter Card (3 auto COUNTIF pills side-by-side!)
    cv.merge(r0 + 1, C_R0, r0 + 1, C_R0 + 1, "😊 Vui vẻ", bold=True, font_size=8.5, align="center",
             bg_color="#DCFCE7", font_color="#166534")
    cv.merge(r0 + 1, C_R0 + 2, r0 + 1, C_R0 + 3, "😐 Bình thường", bold=True, font_size=8.5, align="center",
             bg_color="#FEF3C7", font_color="#92400E")
    cv.put(r0 + 1, C_RE, "😢 Mệt mỏi", bold=True, font_size=8, align="center",
           bg_color="#FFE4E6", font_color="#9F1239")

    cv.merge(r0 + 2, C_R0, r0 + 2, C_R0 + 1, f'=COUNTIF({mood_rng},"😊")&" ngày"', bold=True,
             font_size=10.5, align="center", bg_color=t.card, font_color="#166534")
    cv.merge(r0 + 2, C_R0 + 2, r0 + 2, C_R0 + 3, f'=COUNTIF({mood_rng},"😐")&" ngày"', bold=True,
             font_size=10.5, align="center", bg_color=t.card, font_color="#92400E")
    cv.put(r0 + 2, C_RE, f'=COUNTIF({mood_rng},"😢")&" d"', bold=True,
           font_size=10.5, align="center", bg_color=t.card, font_color="#9F1239")
    cv.grid(r0 + 1, C_R0, r0 + 2, C_RE, t.line)
    cv.box(r0, C_R0, r0 + 2, C_RE, t.line)


# --------------------------------------------------------------------------- #
#  Template 18 (Plum Oak Master Suite): Weekly Habits + Monthly Habits + Notes
# --------------------------------------------------------------------------- #
def add_plum_oak_master_panels(wb, cv: Canvas, tr: TrackerRefs):
    """Compact side-by-side Weekly Habits (5-week grid) + Monthly Habits + Notes below tracker."""
    t = cv.t
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23)
    cv.row(r0 + 1, 20)
    for i in range(6):
        cv.row(r0 + 2 + i, 22)

    # Banner across full width
    cv.merge(r0, C_NAME, r0, C_RE,
             "🌳  WEEKLY & MONTHLY HABITS MASTER SUITE  •  THÓI QUEN TUẦN, THÁNG & GHI CHÚ",
             bold=True, font_size=9.5, align="center", bg_color=t.primary, font_color=t.on_primary)

    # Panel 1 (Left, Col B..P = 1..15): WEEKLY HABITS (task + 5 week checkboxes W1..W5!)
    cv.merge(r0 + 1, C_NAME, r0 + 1, 5, "WEEKLY HABITS • THÓI QUEN TUẦN", bold=True, font_size=8.5,
             align="left", indent=1, bg_color="#B8D4F5", font_color="#1E3A5F")
    w_chk_cols = [6, 8, 10, 12, 14]
    for w_idx, wc in enumerate(w_chk_cols):
        cv.merge(r0 + 1, wc, r0 + 1, wc + 1, f"W{w_idx + 1}", bold=True, font_size=8.5, align="center",
                 bg_color=t.week_head[w_idx], font_color=t.week_on[w_idx])

    weekly_rows = [
        ("Dọn dẹp nhà cửa & bàn làm việc", [True, True, True, True, False]),
        ("Chuẩn bị thực đơn & Meal Prep", [True, True, False, True, False]),
        ("Đi bộ công viên / thiên nhiên 1h", [True, False, True, True, False]),
        ("Tổng kết tài chính cá nhân", [True, True, True, False, False]),
        ("Gọi điện / gặp gỡ gia đình", [True, True, True, True, False]),
        ("", [False, False, False, False, False]),
    ]
    for i, (task, states) in enumerate(weekly_rows):
        rr = r0 + 2 + i
        cv.merge(rr, C_NAME, rr, 5, task, bold=bool(task), font_size=9, align="left", indent=1,
                 bg_color=t.card, font_color=t.ink)
        for w_idx, wc in enumerate(w_chk_cols):
            # Place checkbox in unmerged left cell `wc`, visual padding in `wc+1`
            cv.checkbox(rr, wc, states[w_idx], align="center", font_color=t.week_check[w_idx], bg_color=t.card)
            cv.put(rr, wc + 1, "", bg_color=t.card)
    cv.grid(r0 + 1, C_NAME, r0 + 7, 15, t.line)
    cv.box(r0 + 1, C_NAME, r0 + 7, 15, t.line)

    # Panel 2 (Middle, Col R..AC = 17..28): MONTHLY HABITS (task + DONE checkbox!)
    c_m0, c_m1 = 17, 28
    cv.merge(r0 + 1, c_m0, r0 + 1, c_m1 - 1, "MONTHLY HABITS • MỤC TIÊU THÁNG", bold=True, font_size=8.5,
             align="left", indent=1, bg_color="#C9E4C5", font_color="#1E4620")
    cv.put(r0 + 1, c_m1, "DONE", bold=True, font_size=8, align="center",
           bg_color="#C9E4C5", font_color="#1E4620")
    monthly_rows = [
        ("Hoàn thành ít nhất 1 cuốn sách phát triển bản thân", True),
        ("Dọn gọn tủ đồ & tối giản không gian sống", True),
        ("Lập ngân sách & trích quỹ tiết kiệm đầu tháng", True),
        ("Chăm sóc sức khỏe / khám định kỳ", False),
        ("Sao lưu ảnh & tài liệu quan trọng", True),
        ("", False),
    ]
    for i, (task, done) in enumerate(monthly_rows):
        rr = r0 + 2 + i
        cv.merge(rr, c_m0, rr, c_m1 - 1, task, bold=bool(task), font_size=9, align="left", indent=1,
                 bg_color=t.card, font_color=t.ink)
        cv.checkbox(rr, c_m1, done, align="center", font_color=t.primary, bg_color=t.card)
    cv.grid(r0 + 1, c_m0, r0 + 7, c_m1, t.line)
    cv.box(r0 + 1, c_m0, r0 + 7, c_m1, t.line)

    # Panel 3 (Right, Col AE..C_RE = 30..C_RE): MONTHLY NOTES & REFLECTION
    c_n0 = 30
    cv.merge(r0 + 1, c_n0, r0 + 1, C_RE, "📝  NOTES • GHI CHÚ & TỔNG KẾT THÁNG", bold=True, font_size=8.5,
             align="left", indent=1, bg_color="#A66E8A", font_color="#FFFFFF")
    notes = [
        "• Giữ vững chuỗi thói quen sáng để cây Sồi ra hoa đỏ cuối tháng!",
        "• Chủ nhật cuối tháng tổng kết ngân sách & kế hoạch tháng mới.",
        "• Dành 1 buổi cuối tuần nghỉ ngơi trọn vẹn không mạng xã hội.",
        "",
        "",
        "",
    ]
    for i, txt in enumerate(notes):
        rr = r0 + 2 + i
        cv.merge(rr, c_n0, rr, C_RE, txt, font_size=9, align="left", indent=1,
                 bg_color=t.card, font_color=t.ink)
        cv.hline(rr, c_n0, C_RE, t.line)
    cv.box(r0 + 1, c_n0, r0 + 7, C_RE, t.line)


# --------------------------------------------------------------------------- #
#  Templates 20, 21, 22 (Alpaca Bundle): Cozy Budget / Self-Care / Savings Goals
# --------------------------------------------------------------------------- #
def add_alpaca_mini_panel(wb, cv: Canvas, tr: TrackerRefs, kind: str = "budget"):
    """Compact Alpaca Bundle addon below tracker (Budget #4, Self-Care #5, Savings Goals #6)."""
    t = cv.t
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23)
    cv.row(r0 + 1, 20)
    for i in range(4):
        cv.row(r0 + 2 + i, 22)

    if kind == "budget":
        hdr = "🦙  COZY MINI-BUDGET & SAVINGS  •  NGÂN SÁCH & TIẾT KIỆM THÁNG"
        rows = [
            ("Thu nhập (Income)",       25000000, 26500000),
            ("Chi tiêu thiết yếu",      11000000, 10200000),
            ("Chi tiêu cá nhân / Ăn uống", 5500000, 4800000),
            ("Tiết kiệm & Đầu tư",       8500000, 11500000),
        ]
    elif kind == "selfcare":
        hdr = "🌸  SELF-CARE & SPENDING MOOD  •  CHĂM SÓC BẢN THÂN & CHI TIÊU NHẸ NHÀNG"
        rows = [
            ("Quỹ chăm sóc da & sức khỏe", 2000000, 1650000),
            ("Sách, khóa học & phát triển", 1500000, 1200000),
            ("Cafe, thư giãn & gặp bạn bè", 1800000, 1450000),
            ("Quỹ tự thưởng cuối tháng",    2500000, 2500000),
        ]
    else:
        hdr = "🍵  MONTHLY SAVINGS GOALS  •  MỤC TIÊU QUỸ TIẾT KIỆM THÁNG"
        rows = [
            ("Quỹ dự phòng khẩn cấp",      5000000, 5000000),
            ("Quỹ du lịch / nghỉ dưỡng",   3000000, 2400000),
            ("Quỹ học tập & nâng cấp kỹ năng", 2000000, 1800000),
            ("Quỹ đầu tư dài hạn",         4000000, 3600000),
        ]

    cv.merge(r0, C_NAME, r0, C_D31, hdr, bold=True, font_size=9.5, align="left", indent=1,
             bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_R0, r0, C_RE, f"{t.emoji}  TỔNG KẾT TÀI CHÍNH", bold=True, font_size=9,
             align="center", bg_color=t.primary, font_color=t.on_primary)

    cv.merge(r0 + 1, C_NAME, r0 + 1, 10, "HẠNG MỤC (CATEGORY)", bold=True, font_size=8.5,
             align="left", indent=1, bg_color=t.soft, font_color=t.ink)
    cv.merge(r0 + 1, 11, r0 + 1, 17, "MỤC TIÊU (PLANNED)", bold=True, font_size=8.5,
             align="center", bg_color=t.soft, font_color=t.ink)
    cv.merge(r0 + 1, 18, r0 + 1, 24, "THỰC TẾ (ACTUAL)", bold=True, font_size=8.5,
             align="center", bg_color=t.soft, font_color=t.ink)
    cv.merge(r0 + 1, 25, r0 + 1, C_D31, "TIẾN ĐỘ (%)", bold=True, font_size=8.5,
             align="center", bg_color=t.soft, font_color=t.ink)

    for i, (cat, plan, act) in enumerate(rows):
        rr = r0 + 2 + i
        bg = t.card if i % 2 == 0 else t.page
        cv.merge(rr, C_NAME, rr, 10, cat, bold=True, font_size=9.5, align="left", indent=1,
                 bg_color=bg, font_color=t.ink)
        cv.merge(rr, 11, rr, 17, plan, font_size=9.5, align="center", num_format="#,##0",
                 bg_color=bg, font_color=t.muted)
        cv.merge(rr, 18, rr, 24, act, bold=True, font_size=9.5, align="center", num_format="#,##0",
                 bg_color=bg, font_color=t.ink)
        cv.merge(rr, 25, rr, C_D31, f"=IFERROR(MIN(1.5,S{rr + 1}/L{rr + 1}),0)", bold=True,
                 font_size=9, align="center", num_format="0%", bg_color=bg, font_color=t.primary_dark)

    cv.ws.conditional_format(rng(r0 + 2, 25, r0 + 5, C_D31), {
        "type": "data_bar", "bar_color": t.bar, "bar_solid": True,
        "min_type": "num", "min_value": 0, "max_type": "num", "max_value": 1,
    })
    cv.grid(r0 + 1, C_NAME, r0 + 5, C_D31, t.line)
    cv.box(r0, C_NAME, r0 + 5, C_D31, t.line)

    # Right summary card
    cv.merge(r0 + 1, C_R0, r0 + 1, C_RE, "TỔNG THỰC TẾ", bold=True, font_size=8, align="center",
             bg_color=t.soft, font_color=t.muted)
    cv.merge(r0 + 2, C_R0, r0 + 3, C_RE, f"=SUM(S{r0 + 3}:S{r0 + 6})", bold=True, font_size=14,
             align="center", num_format='#,##0" đ"', bg_color=t.card, font_color=t.primary_dark,
             font_name=t.font_title)
    cv.merge(r0 + 4, C_R0, r0 + 5, C_RE,
             f'="Đạt "&TEXT(IFERROR(SUM(S{r0 + 3}:S{r0 + 6})/SUM(L{r0 + 3}:L{r0 + 6}),0),"0%")&" kế hoạch"&CHAR(10)&'
             f'"{t.emoji} Kỷ luật tháng: "&TEXT({tr.s["overall"]},"0%")',
             bold=True, font_size=8.8, align="center", text_wrap=True, bg_color=t.soft, font_color=t.ink)
    cv.box(r0, C_R0, r0 + 5, C_RE, t.line)


# --------------------------------------------------------------------------- #
#  Template 24 (Royal Cat Saving Cash): Cat Kingdom Counters + Cash Flow Panel
# --------------------------------------------------------------------------- #
def add_royal_cat_cash_panel(wb, cv: Canvas, tr: TrackerRefs):
    """Playful Cat Kingdom Counters (Box / Mature / Royal Cats) + Expected vs Actual Cash Flow."""
    t = cv.t
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23)
    cv.row(r0 + 1, 20)
    for i in range(4):
        cv.row(r0 + 2 + i, 22)

    pct_rng = f"{rng(R_PCT, C_D0, R_PCT, C_D31)}"
    # Left Card: Cat Kingdom Counters (Col B..N = 1..13)
    cv.merge(r0, C_NAME, r0, 13, "👑  CAT KINGDOM STATUS  •  VƯƠNG QUỐC MÈO THÁNG NÀY",
             bold=True, font_size=9.5, align="left", indent=1, bg_color=t.primary, font_color=t.on_primary)
    cat_tiers = [
        ("👑  Mèo Hoàng Gia (100% hoàn hảo)",     f'=COUNTIF({pct_rng},">=0.999")&" chú mèo 👑"', "#FEF3C7", "#92400E"),
        ("🐱  Mèo Trưởng Thành (50% – 99%)",      f'=COUNTIFS({pct_rng},">=0.5",{pct_rng},"<0.999")&" chú mèo 🐱"', "#ECFDF5", "#065F46"),
        ("📦  Mèo Hộp Giấy (< 50% / chưa tick)",  f'=COUNTIFS({pct_rng},">0",{pct_rng},"<0.5")&" chú mèo 📦"', "#F3EFE9", "#5C4033"),
        ("✨  Tỉ lệ lên ngôi Hoàng Gia",           f'=TEXT(IFERROR(COUNTIF({pct_rng},">=0.999")/COUNTIF({pct_rng},">0"),0),"0%")', t.soft, t.primary_dark),
    ]
    cv.merge(r0 + 1, C_NAME, r0 + 1, 8, "CẤP BẬC MÈO", bold=True, font_size=8.5, align="left", indent=1, bg_color=t.soft, font_color=t.ink)
    cv.merge(r0 + 1, 9, r0 + 1, 13, "SỐ LƯỢNG", bold=True, font_size=8.5, align="center", bg_color=t.soft, font_color=t.ink)
    for i, (lbl, fml, bg, fg) in enumerate(cat_tiers):
        rr = r0 + 2 + i
        cv.merge(rr, C_NAME, rr, 8, lbl, bold=True, font_size=9.2, align="left", indent=1, bg_color=t.card, font_color=t.ink)
        cv.merge(rr, 9, rr, 13, fml, bold=True, font_size=9.5, align="center", bg_color=bg, font_color=fg)
    cv.grid(r0 + 1, C_NAME, r0 + 5, 13, t.line)
    cv.box(r0, C_NAME, r0 + 5, 13, t.line)

    # Right Card: Expected vs Actual Cash Flow Summary (Col P..C_RE = 15..C_RE)
    cv.merge(r0, 15, r0, C_RE, "💰  SAVING CASH SUMMARY  •  DỰ KIẾN VS THỰC TẾ",
             bold=True, font_size=9.5, align="left", indent=1, bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0 + 1, 15, r0 + 1, 22, "DANH MỤC DÒNG TIỀN", bold=True, font_size=8.5, align="left", indent=1, bg_color=t.soft, font_color=t.ink)
    cv.merge(r0 + 1, 23, r0 + 1, 28, "DỰ KIẾN", bold=True, font_size=8.5, align="center", bg_color=t.soft, font_color=t.ink)
    cv.merge(r0 + 1, 29, r0 + 1, C_R0 + 1, "THỰC TẾ", bold=True, font_size=8.5, align="center", bg_color=t.soft, font_color=t.ink)
    cv.merge(r0 + 1, C_R0 + 2, r0 + 1, C_RE, "CHÊNH LỆCH", bold=True, font_size=8.5, align="center", bg_color=t.soft, font_color=t.ink)
    cash_rows = [
        ("💵 Thu nhập (Income)",   28000000, 29500000),
        ("🛍️ Chi tiêu (Expenses)", 10000000,  8900000),
        ("🧾 Hóa đơn (Bills)",      5500000,  5300000),
        ("🏦 Tiết kiệm (Savings)", 12500000, 15300000),
    ]
    for i, (lbl, exp_v, act_v) in enumerate(cash_rows):
        rr = r0 + 2 + i
        bg = t.card if i % 2 == 0 else t.page
        cv.merge(rr, 15, rr, 22, lbl, bold=True, font_size=9.2, align="left", indent=1, bg_color=bg, font_color=t.ink)
        cv.merge(rr, 23, rr, 28, exp_v, font_size=9.2, align="center", num_format="#,##0", bg_color=bg, font_color=t.muted)
        cv.merge(rr, 29, rr, C_R0 + 1, act_v, bold=True, font_size=9.2, align="center", num_format="#,##0", bg_color=bg, font_color=t.ink)
        cv.merge(rr, C_R0 + 2, rr, C_RE, f"={cell(rr, 29)}-{cell(rr, 23)}", bold=True, font_size=9.2, align="center",
                 num_format="+#,##0;-#,##0;0", bg_color=bg, font_color=t.primary_dark)
    cv.grid(r0 + 1, 15, r0 + 5, C_RE, t.line)
    cv.box(r0, 15, r0 + 5, C_RE, t.line)


# --------------------------------------------------------------------------- #
#  Templates 25 (Ginger Kitten) & 28 (Candy Jar): Top Habits Rank & Highlights
# --------------------------------------------------------------------------- #
def add_top_habits_rank_panel(wb, cv: Canvas, tr: TrackerRefs, kind: str = "ginger"):
    """Compact Top-5 Habit Rank Leaderboard + Motivational Card below the main tracker."""
    t = cv.t
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23)
    cv.row(r0 + 1, 20)
    for i in range(4):
        cv.row(r0 + 2 + i, 22)

    title_l = ("🐱  TOP HABITS LEADERBOARD  •  XẾP HẠNG THÓI QUEN XUẤT SẮC"
               if kind == "ginger" else
               "🍬  HABITS RANK  •  BẢNG XẾP HẠNG THÓI QUEN NGỌT NGÀO")
    cv.merge(r0, C_NAME, r0, C_D31, title_l, bold=True, font_size=9.5, align="left", indent=1,
             bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_R0, r0, C_RE,
             ("🐾  ROUTINE SUMMARY" if kind == "ginger" else "🍭  CANDY JAR BONUS"),
             bold=True, font_size=9, align="center", bg_color=t.primary, font_color=t.on_primary)

    # Top 4 habits dynamically pulled via LARGE on Progress column (col 36 = AK? No, rc["progress"]!)
    prog_col = colname(tr.right_cols["progress"])
    done_col = colname(tr.right_cols["done"])
    cv.merge(r0 + 1, C_NAME, r0 + 1, 14, "HẠNG & THÓI QUEN DẪN ĐẦU", bold=True, font_size=8.5,
             align="left", indent=1, bg_color=t.soft, font_color=t.ink)
    cv.merge(r0 + 1, 15, r0 + 1, 23, "TỈ LỆ HOÀN THÀNH", bold=True, font_size=8.5,
             align="center", bg_color=t.soft, font_color=t.ink)
    cv.merge(r0 + 1, 24, r0 + 1, C_D31, "SỐ NGÀY ĐẠT", bold=True, font_size=8.5,
             align="center", bg_color=t.soft, font_color=t.ink)

    medals = ["🥇 #1", "🥈 #2", "🥉 #3", "⭐ #4"]
    p_rng = f"${prog_col}$17:${prog_col}$36"
    for i, med in enumerate(medals):
        rr = r0 + 2 + i
        k_rank = i + 1
        bg = t.card if i % 2 == 0 else t.page
        cv.merge(rr, C_NAME, rr, 14,
                 f'=IFERROR("{med}  "&INDEX($B$17:$B$36,MATCH(LARGE({p_rng},{k_rank}),{p_rng},0)),"{med}  —")',
                 bold=True, font_size=9.5, align="left", indent=1, bg_color=bg, font_color=t.ink)
        cv.merge(rr, 15, rr, 23, f"=IFERROR(LARGE({p_rng},{k_rank}),0)", bold=True, font_size=9.5,
                 align="center", num_format="0%", bg_color=bg, font_color=t.primary_dark)
        cv.merge(rr, 24, rr, C_D31,
                 f'=IFERROR(INDEX(${done_col}$17:${done_col}$36,MATCH(LARGE({p_rng},{k_rank}),{p_rng},0)),"—")',
                 font_size=9.2, align="center", bg_color=bg, font_color=t.ink)
    cv.grid(r0 + 1, C_NAME, r0 + 5, C_D31, t.line)
    cv.box(r0, C_NAME, r0 + 5, C_D31, t.line)

    # Right Celebration Card
    big_txt = (f'="YAY! "&{tr.s["grown"]}&" CANDY JARS!"' if kind != "ginger"
               else f'="🐾 "&{tr.s["grown"]}&" NGÀY MÈO VUI!"')
    cv.merge(r0 + 1, C_R0, r0 + 3, C_RE, big_txt, bold=True, font_size=13, align="center",
             bg_color=t.card, font_color=t.primary_dark, font_name=t.font_title)
    cv.merge(r0 + 4, C_R0, r0 + 5, C_RE,
             f'="Hiệu suất: "&TEXT({tr.s["overall"]},"0%")&"  •  Hoàn hảo: "&{tr.s["perfect"]}&"d"',
             bold=True, font_size=8.8, align="center", bg_color=t.soft, font_color=t.ink)
    cv.box(r0, C_R0, r0 + 5, C_RE, t.line)


# --------------------------------------------------------------------------- #
#  Templates 30 (Shiba Inu) & 31 (Akita Inu): Good Boy Points & Loyalty Focus
# --------------------------------------------------------------------------- #
def add_dog_companion_panel(wb, cv: Canvas, tr: TrackerRefs, kind: str = "shiba"):
    """Bespoke gamified Shiba Inu 'Good Boy Points' or Akita Inu 'Loyalty & Zen Focus' card."""
    t = cv.t
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 24)
    cv.row(r0 + 1, 22)
    cv.row(r0 + 2, 24)
    cv.row(r0 + 3, 22)

    pts_expr = f'({tr.s["tdone"]}*10+{tr.s["perfect"]}*50+{tr.s["best"]}*15)'
    if kind == "shiba":
        hdr = "🐕  SHIBA INU GOOD BOY POINTS  •  ĐIỂM CÚN NGOAN & PHẦN THƯỞNG"
        rank_f = (f'=IF({pts_expr}>=2500,"👑 SHIBA HOÀNG ĐẾ",'
                  f'IF({pts_expr}>=1500,"🧣 CHIẾN BINH KHĂN ĐỎ",'
                  f'IF({pts_expr}>=600,"🐕 CÚN NGOAN VẪY ĐUÔI","🐾 SHIBA TẬP SỰ")))')
        note_lbl = "🦴  PHẦN THƯỞNG TỰ THƯỞNG KHI ĐẠT MỤC TIÊU THÁNG"
        note_val = "• Đạt 1.500 điểm Cún Ngoan: Thưởng 1 buổi xem phim / ăn món ngon yêu thích! 🍜"
    else:
        hdr = "❄️  AKITA INU LOYALTY & ZEN FOCUS  •  CHỈ SỐ TRUNG THÀNH & TĨNH TÂM"
        rank_f = (f'=IF({pts_expr}>=2500,"⛩️ ĐẠI SƯ AKITA",'
                  f'IF({pts_expr}>=1500,"🔔 CHUÔNG VÀNG TRUNG THÀNH",'
                  f'IF({pts_expr}>=600,"❄️ CÚN TUYẾT KIÊN ĐỊNH","🐾 ĐỆM TATAMI KHỞI ĐẦU")))')
        note_lbl = "🌸  GHI CHÚ TĨNH TÂM & BIẾT ƠN TRONG THÁNG"
        note_val = "• Giữ nhịp sống điềm tĩnh, trung thành với lời hứa nhỏ với chính mình mỗi ngày. ❄️"

    cv.merge(r0, C_NAME, r0, C_RE, hdr, bold=True, font_size=9.5, align="left", indent=1,
             bg_color=t.primary, font_color=t.on_primary)

    # KPI 1: Points (Cols B..H = 1..7)
    cv.merge(r0 + 1, C_NAME, r0 + 1, 7, ("🦴 ĐIỂM CÚN NGOAN" if kind == "shiba" else "🔔 ĐIỂM TRUNG THÀNH"),
             bold=True, font_size=8.5, align="center", bg_color=t.soft, font_color=t.muted)
    cv.merge(r0 + 2, C_NAME, r0 + 3, 7, f'={pts_expr}', bold=True, font_size=18, align="center",
             num_format='#,##0" pts"', bg_color=t.card, font_color=t.primary_dark, font_name=t.font_title)

    # KPI 2: Rank (Cols I..Q = 8..16)
    cv.merge(r0 + 1, 8, r0 + 1, 16, "DANH HIỆU HIỆN TẠI", bold=True, font_size=8.5, align="center",
             bg_color=t.soft, font_color=t.muted)
    cv.merge(r0 + 2, 8, r0 + 3, 16, rank_f, bold=True, font_size=12, align="center",
             bg_color=t.card, font_color=t.ink, font_name=t.font_title)

    # KPI 3: Reflection / Reward Note (Cols R..C_RE = 17..C_RE)
    cv.merge(r0 + 1, 17, r0 + 1, C_RE, note_lbl, bold=True, font_size=8.5, align="left", indent=1,
             bg_color=t.soft, font_color=t.ink)
    cv.merge(r0 + 2, 17, r0 + 3, C_RE, note_val, font_size=9.5, align="left", indent=1, text_wrap=True,
             bg_color=t.card, font_color=t.ink)
    cv.grid(r0 + 1, C_NAME, r0 + 3, C_RE, t.line)
    cv.box(r0, C_NAME, r0 + 3, C_RE, t.line)


# --------------------------------------------------------------------------- #
#  Template 32 (Sakura Blossom Minimalist): Start Date & Blossom Summary Bar
# --------------------------------------------------------------------------- #
def add_sakura_minimalist_bar(wb, cv: Canvas, tr: TrackerRefs):
    """Ultra-clean minimalist Sakura Start Date & Blossom Reflection Strip."""
    t = cv.t
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 22)
    cv.row(r0 + 1, 28)

    cv.merge(r0, C_NAME, r0, 7, "🌸  NGÀY BẮT ĐẦU (START DATE)", bold=True, font_size=8.5,
             align="center", bg_color=t.soft, font_color=t.primary_dark)
    cv.merge(r0 + 1, C_NAME, r0 + 1, 7,
             f'=TEXT(DATE({tr.s["y"]},{tr.s["m"]},1),"dd/mm/yyyy")',
             bold=True, font_size=12, align="center", bg_color=t.card, font_color=t.ink, font_name=t.font_title)

    cv.merge(r0, 8, r0, 16, "🌳  CÂY ANH ĐÀO ĐÃ NỞ (≥ 75%)", bold=True, font_size=8.5,
             align="center", bg_color=t.soft, font_color=t.primary_dark)
    cv.merge(r0 + 1, 8, r0 + 1, 16,
             f'={tr.s["grown"]}&" cây anh đào  •  "&{tr.s["perfect"]}&" ngày 100% ✨"',
             bold=True, font_size=10.5, align="center", bg_color=t.card, font_color=t.primary_dark)

    cv.merge(r0, 17, r0, C_RE, "🕊️  GHI CHÚ TỐI GIẢN & CHÁNH NIỆM THÁNG NÀY", bold=True, font_size=8.5,
             align="left", indent=1, bg_color=t.soft, font_color=t.primary_dark)
    cv.merge(r0 + 1, 17, r0 + 1, C_RE,
             "• Ít nhưng tinh — tập trung hoàn thành trọn vẹn từng thói quen cốt lõi để mỗi ngày đều nở hoa anh đào.",
             font_size=9.2, align="left", indent=1, text_wrap=True, bg_color=t.card, font_color=t.ink)
    cv.grid(r0, C_NAME, r0 + 1, C_RE, t.line)
    cv.box(r0, C_NAME, r0 + 1, C_RE, t.line)


# --------------------------------------------------------------------------- #
#  Template 33 (Peach Mochi Cat Mood Suite): 6-Mood Tracker + Daily To-Do + Reflection
# --------------------------------------------------------------------------- #
def add_mochi_cat_mood_suite(wb, cv: Canvas, tr: TrackerRefs, seed: int = 330):
    """Honors Peach Mochi Cat ref: 31-day 6-Mood Tracker + 6 Mood Counters + Quick To-Do + Reflection!"""
    t = cv.t
    ws = cv.ws
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 24)        # Banner
    cv.row(r0 + 1, 24)    # 31-day 6-mood dropdown strip
    cv.row(r0 + 2, 22)    # 6-Mood Counter labels
    cv.row(r0 + 3, 24)    # 6-Mood Counter values
    cv.row(r0 + 4, 10)    # Spacer
    cv.row(r0 + 5, 24)    # Bottom 3-Card Headers (Quick To-Do | What Went Well | What Didn't Go Well)
    for rr in range(r0 + 6, r0 + 10):
        cv.row(rr, 22)

    # Row 1: MOOD TRACKER Banner + 31-day Mood Selector Strip
    cv.merge(r0, C_NAME, r0, C_RE, "🐱  MOOD TRACKER  •  NHẬT KÝ 6 CẢM XÚC HẰNG NGÀY (CHỌN TỪ DROPDOWN)",
             bold=True, font_size=9.5, align="left", indent=1, bg_color=t.primary, font_color=t.on_primary)
    cv.put(r0 + 1, C_NAME, "💛  Tâm trạng hôm nay", bold=True, font_size=9.2, align="left", indent=1,
           bg_color=t.soft, font_color=t.ink)

    rnd = random.Random(seed)
    pool = [MOOD6_OPTIONS[0], MOOD6_OPTIONS[1], MOOD6_OPTIONS[1], MOOD6_OPTIONS[2],
            MOOD6_OPTIONS[0], MOOD6_OPTIONS[1], MOOD6_OPTIONS[3], MOOD6_OPTIONS[2], MOOD6_OPTIONS[4]]
    for k in range(1, 32):
        c = day_col(k)
        val = rnd.choice(pool) if k <= 22 else ""
        cv.put(r0 + 1, c, val, align="center", font_size=11, bg_color=t.card, font_color=t.ink)

    mood_strip_rng = rng(r0 + 1, C_D0, r0 + 1, C_D31)
    ws.data_validation(mood_strip_rng, {
        "validate": "list", "source": f"={mood6_lookup_ref()}",
        "input_title": "Chọn Tâm Trạng (6 Mức)",
        "input_message": "❤️ Yêu đời / 😊 Vui vẻ / 🙂 Ổn áp / 😕 Chưa ổn / 😢 Buồn / 😠 Bực bội",
    })
    cv.merge(r0 + 1, C_R0, r0 + 1, C_RE,
             f'=COUNTIF({mood_strip_rng},"?*")&" / "&{tr.s["dim"]}&" ngày ghi tâm trạng"',
             bold=True, font_size=8.8, align="center", bg_color=t.soft, font_color=t.primary_dark)

    # Row 2 & 3: 6 Pastel Mood Counters neatly distributed across Cols B..C_RE
    cv.merge(r0 + 2, C_NAME, r0 + 3, C_NAME, "📊  TỔNG KẾT 6 CẢM XÚC", bold=True, font_size=9,
             align="center", bg_color=t.soft, font_color=t.ink)
    mood_spans = [
        (2, 6,   MOOD6_OPTIONS[0], MOOD6_LABELS[0], "#FFE4E6", "#BE123C"),
        (7, 11,  MOOD6_OPTIONS[1], MOOD6_LABELS[1], "#FEF3C7", "#92400E"),
        (12, 16, MOOD6_OPTIONS[2], MOOD6_LABELS[2], "#DCFCE7", "#166534"),
        (17, 22, MOOD6_OPTIONS[3], MOOD6_LABELS[3], "#E0F2FE", "#075985"),
        (23, 28, MOOD6_OPTIONS[4], MOOD6_LABELS[4], "#EDE9FE", "#5B21B6"),
        (29, C_RE, MOOD6_OPTIONS[5], MOOD6_LABELS[5], "#FEE2E2", "#991B1B"),
    ]
    for c1, c2, opt, lbl_m, m_bg, m_fg in mood_spans:
        cv.merge(r0 + 2, c1, r0 + 2, c2, lbl_m, bold=True, font_size=8.8, align="center",
                 bg_color=m_bg, font_color=m_fg)
        cv.merge(r0 + 3, c1, r0 + 3, c2, f'=COUNTIF({mood_strip_rng},"{opt}")&" ngày"',
                 bold=True, font_size=10, align="center", bg_color=t.card, font_color=m_fg)
    cv.grid(r0 + 1, C_NAME, r0 + 3, C_RE, t.line)
    cv.box(r0, C_NAME, r0 + 3, C_RE, t.line)

    # Row 5..9: Side-by-side Quick Daily To-Do | What Went Well | What Didn't Go Well
    r_b = r0 + 5
    cv.merge(r_b, C_NAME, r_b, 10, "📝  QUICK DAILY TO-DO (VIỆC CẦN LÀM NHANH)", bold=True, font_size=9,
             align="left", indent=1, bg_color="#CBE8C8", font_color="#2D4A2B")
    todos = [
        "☑  Quay video chia sẻ góc học tập mới",
        "☑  Viết bài tổng kết mục tiêu tuần này",
        "☐  Thăm gia đình & ăn tối cuối tuần",
        "☐  Dọn bàn làm việc & tưới cây nhỏ",
    ]
    for idx_td, td in enumerate(todos):
        cv.merge(r_b + 1 + idx_td, C_NAME, r_b + 1 + idx_td, 10, td, font_size=9.2, align="left", indent=1,
                 bg_color=t.card if idx_td % 2 == 0 else t.page, font_color=t.ink)
    cv.grid(r_b + 1, C_NAME, r_b + 4, 10, t.line)
    cv.box(r_b, C_NAME, r_b + 4, 10, t.line)

    cv.merge(r_b, 12, r_b, 24, "✨  ĐIỀU LÀM TỐT (WHAT WENT WELL)", bold=True, font_size=9,
             align="left", indent=1, bg_color="#FCD5B5", font_color=t.ink)
    cv.merge(r_b + 1, 12, r_b + 4, 24,
             "• Giữ được nhịp dậy sớm & uống đủ nước đều đặn.\n"
             "• Tâm trạng luôn tích cực nhờ viết nhật ký cảm xúc mỗi tối.\n"
             "• Hoàn thành sớm toàn bộ việc ưu tiên trong tuần!",
             font_size=9.2, align="left", indent=1, text_wrap=True, bg_color=t.card, font_color=t.ink)
    cv.box(r_b, 12, r_b + 4, 24, t.line)

    cv.merge(r_b, 26, r_b, C_RE, "💡  ĐIỀU CẦN CẢI THIỆN (WHAT DIDN'T GO WELL)", bold=True, font_size=9,
             align="left", indent=1, bg_color="#F4A261", font_color="#FFFFFF")
    cv.merge(r_b + 1, 26, r_b + 4, C_RE,
             "• Vẫn còn lướt điện thoại khuya 2 tối cuối tuần.\n"
             "• Tuần tới cần đặt báo thức ngủ lúc 22h45 & chuẩn bị đồ từ tối hôm trước!",
             font_size=9.2, align="left", indent=1, text_wrap=True, bg_color=t.card, font_color=t.ink)
    cv.box(r_b, 26, r_b + 4, C_RE, t.line)


# --------------------------------------------------------------------------- #
#  Template 34 (Fluffy Bunny Sticker Pop): 5-Color Pastel Bars + Progress Ring
# --------------------------------------------------------------------------- #
def add_bunny_sticker_pop_panel(wb, cv: Canvas, tr: TrackerRefs):
    """Notedii-inspired 5-Color Pastel Progress Bars (Coral/Pink/Lavender/Sky/Mint) + Bunny Ring!"""
    t = cv.t
    ws = cv.ws
    C_RE = tr.c_right_end
    rb = tr.calc_row_base
    r0 = R_EXTRA
    cv.row(r0, 24)
    for i in range(5):
        cv.row(r0 + 1 + i, 24)

    cv.merge(r0, C_NAME, r0, C_D31, "🐰  BUNNY PASTEL PROGRESS BARS  •  5 DẢI TIẾN ĐỘ TUẦN (CORAL • PINK • LAVENDER • SKY • MINT)",
             bold=True, font_size=9.5, align="left", indent=1, bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_R0, r0, C_RE, "🎀  BUNNY PROGRESS RING", bold=True, font_size=9,
             align="center", bg_color=t.primary, font_color=t.on_primary)

    bar_colors = [
        ("WEEK 1  •  Coral Peach",   "#F4A4A4", "#FFF1F1"),
        ("WEEK 2  •  Pastel Pink",   "#F9C6D0", "#FFF5F7"),
        ("WEEK 3  •  Soft Lavender", "#C4B5FD", "#F5F3FF"),
        ("WEEK 4  •  Baby Sky",      "#7DD3FC", "#F0F9FF"),
        ("WEEK 5  •  Fresh Mint",    "#6EE7B7", "#ECFDF5"),
    ]
    for w, (lbl, b_col, tint_col) in enumerate(bar_colors):
        rr = r0 + 1 + w
        hc = CALC_WK_COL0 + w
        pct_ref = f"{tr.calc_q}!{acell(rb + 2, hc)}"
        done_ref = f"{tr.calc_q}!{acell(rb + 0, hc)}"
        tot_ref = f"{tr.calc_q}!{acell(rb + 1, hc)}"
        cv.merge(rr, C_NAME, rr, 6, f"🐇  {lbl}", bold=True, font_size=9.2, align="left", indent=1,
                 bg_color=tint_col, font_color=t.ink)
        cv.merge(rr, 7, rr, 27, f"={pct_ref}", bold=True, font_size=9.5, align="center",
                 num_format="0%", bg_color=t.card, font_color=t.ink)
        ws.conditional_format(rng(rr, 7, rr, 27), {
            "type": "data_bar", "bar_color": b_col, "bar_solid": True,
            "min_type": "num", "min_value": 0, "max_type": "num", "max_value": 1,
        })
        cv.merge(rr, 28, rr, C_D31, f'={done_ref}&" / "&{tot_ref}&" ✓"', bold=True, font_size=8.8,
                 align="center", bg_color=tint_col, font_color=t.ink)
    cv.grid(r0 + 1, C_NAME, r0 + 5, C_D31, t.line)
    cv.box(r0, C_NAME, r0 + 5, C_D31, t.line)

    # Right Bunny Progress Ring Donut Card
    cv.merge(r0 + 1, C_R0, r0 + 4, C_RE, f"={tr.s['overall']}", bold=True, font_size=16,
             align="center", num_format="0%", bg_color=t.card, font_color="#C25D6A", font_name=t.font_title)
    d_b = donut(wb, f"={tr.calc_q}!{rng(rb + 0, CALC_DONUT_COL, rb + 1, CALC_DONUT_COL)}",
                ["#F4A4A4", "#FCE7EB"], hole=68, name="BunnyProgressRing")
    place_chart(cv, d_b, r0 + 1, C_R0, r0 + 4, C_RE, pad_x=10, pad_y=2)
    cv.merge(r0 + 5, C_R0, r0 + 5, C_RE,
             f'="🍒 "&{tr.s["grown"]}&" ngày Thỏ Nơ Cherry!"',
             bold=True, font_size=8.8, align="center", bg_color=t.soft, font_color=t.ink)
    cv.box(r0, C_R0, r0 + 5, C_RE, t.line)


# --------------------------------------------------------------------------- #
#  Template 35 (Milk & Mocha Bear Sweet Love): 5 Weekly Donuts + 1 Monthly Donut!
# --------------------------------------------------------------------------- #
def add_milk_mocha_donuts_panel(wb, cv: Canvas, tr: TrackerRefs):
    """Honors Milk & Mocha Bear ref: Weekly Done/Incomplete rows + 5 Weekly Donuts + 1 Monthly Donut!"""
    t = cv.t
    C_RE = tr.c_right_end
    rb = tr.calc_row_base
    r0 = R_EXTRA
    cv.row(r0, 24)        # Banner
    cv.row(r0 + 1, 20)    # Weekly Completed
    cv.row(r0 + 2, 20)    # Weekly Incomplete
    for rr in range(r0 + 3, r0 + 10):
        cv.row(rr, 22)    # 7 tall rows for crisp 5 Weekly + 1 Monthly Donuts!
    cv.row(r0 + 10, 22)   # Percentage % per Week footer row

    cv.merge(r0, C_NAME, r0, C_D31, "🐻  PROGRESS PER WEEK  •  5 BIỂU ĐỒ TRÒN TIẾN ĐỘ TUẦN (MILK & MOCHA)",
             bold=True, font_size=9.5, align="left", indent=1, bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_R0, r0, C_RE, "💖  TOTAL MONTHLY PROGRESS", bold=True, font_size=9,
             align="center", bg_color="#6D1D3A", font_color="#FFFFFF")

    cv.put(r0 + 1, C_NAME, "Weekly Habits Completed ✓", bold=True, font_size=8.8, align="left", indent=1,
           bg_color=t.soft, font_color=t.ink)
    cv.put(r0 + 2, C_NAME, "Weekly Habits Incomplete", font_size=8.6, align="left", indent=1,
           bg_color=t.card, font_color=t.muted)
    cv.merge(r0 + 3, C_NAME, r0 + 9, C_NAME,
             f'="🐻 Milk & Mocha"&CHAR(10)&"Tổng tháng: "&{tr.s["tdone"]}&" / "&{tr.s["tgoal"]}&CHAR(10)&'
             f'"💖 Ngày 100%: "&{tr.s["perfect"]}&"d"&CHAR(10)&"🔥 Best Streak: "&{tr.s["best"]}&"d"',
             bold=True, font_size=9.2, align="center", text_wrap=True, bg_color=t.card, font_color=t.primary_dark)
    cv.put(r0 + 10, C_NAME, "Percentage % per Week", bold=True, font_size=8.8, align="left", indent=1,
           bg_color=t.soft, font_color=t.primary_dark)

    wk_donut_cols = ["#E86A92", "#A78BFA", "#F47272", "#6DBE7A", "#EC4899"]
    wk_rest_cols  = ["#FCE7F3", "#EDE9FE", "#FEE2E2", "#DCFCE7", "#FCE7F3"]
    for w in range(5):
        days = week_days(w)
        c1, c2 = day_col(days[0]), day_col(days[-1])
        hc = CALC_WK_COL0 + w
        done_ref = f"{tr.calc_q}!{acell(rb + 0, hc)}"
        rem_ref  = f"{tr.calc_q}!{acell(rb + 4, hc)}"
        pct_ref  = f"{tr.calc_q}!{acell(rb + 2, hc)}"

        cv.merge(r0 + 1, c1, r0 + 1, c2, f"={done_ref}", bold=True, font_size=9.5, align="center",
                 bg_color=t.week_tint[w], font_color=t.ink)
        cv.merge(r0 + 2, c1, r0 + 2, c2, f"={rem_ref}", font_size=9, align="center",
                 bg_color=t.card, font_color=t.muted)
        cv.merge(r0 + 3, c1, r0 + 9, c2, "", align="center", bg_color=t.card)
        d_w = donut(wb, f"={tr.calc_q}!{rng(rb + 2, hc, rb + 3, hc)}",
                    [wk_donut_cols[w], wk_rest_cols[w]], hole=62, name=f"Week{w + 1}Donut")
        place_chart(cv, d_w, r0 + 3, c1, r0 + 9, c2, pad_x=4, pad_y=4)
        cv.merge(r0 + 10, c1, r0 + 10, c2, f"={pct_ref}", bold=True, font_size=10, align="center",
                 num_format="0.0%", bg_color=t.week_tint[w], font_color=t.ink)

    cv.grid(r0 + 1, C_NAME, r0 + 10, C_D31, t.line)
    cv.box(r0, C_NAME, r0 + 10, C_D31, t.line)

    # Right Total Monthly Progress Donut Card (matching Milk & Mocha ref #4!)
    cv.merge(r0 + 1, C_R0, r0 + 1, C_RE, f'="Completed: "&{tr.s["tdone"]}', bold=True, font_size=8.8,
             align="center", bg_color=t.soft, font_color=t.ink)
    cv.merge(r0 + 2, C_R0, r0 + 2, C_RE, f'="Remaining: "&({tr.s["tgoal"]}-{tr.s["tdone"]})', font_size=8.5,
             align="center", bg_color=t.card, font_color=t.muted)
    cv.merge(r0 + 3, C_R0, r0 + 9, C_RE, "", align="center", bg_color=t.card)
    d_m = donut(wb, f"={tr.calc_q}!{rng(rb + 0, CALC_DONUT_COL, rb + 1, CALC_DONUT_COL)}",
                ["#E86A92", "#FCE7F3"], hole=60, name="TotalMonthlyDonut")
    place_chart(cv, d_m, r0 + 3, C_R0, r0 + 9, C_RE, pad_x=10, pad_y=4)
    cv.merge(r0 + 10, C_R0, r0 + 10, C_RE, f"={tr.s['overall']}", bold=True, font_size=11, align="center",
             num_format="0.0%", bg_color=t.soft, font_color="#6D1D3A", font_name=t.font_title)
    cv.grid(r0 + 1, C_R0, r0 + 10, C_RE, t.line)
    cv.box(r0, C_R0, r0 + 10, C_RE, t.line)

