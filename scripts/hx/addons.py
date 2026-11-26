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
    cv.unlock(r0 + 1, C_R0, r0 + 6, C_RE)
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
        cv.unlock(r1 + 1, c1, r1 + 6, c2)
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
    cv.unlock(r_sleep, C_D0, r_calm, C_D31)

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
    cv.unlock(r_hrs, C_D0, r_hrs, C_D31)
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
    cv.unlock(r_ch0 + 1, C_R0, r_ch0 + 4, C_RE)
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
    cv.unlock(r_en, C_D0, r_wat, C_D31)
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
    cv.unlock(r_mood, C_D0, r_mood, C_D31)
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
    cv.unlock(rc0 + 1, C_D0 + 11, rc0 + 4, C_RE)
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
    cv.unlock(r0 + 1, C_NAME, r0 + 5, c_mid)
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
    cv.unlock(r0 + 1, c_fail0, r0 + 5, C_D31)
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
    cv.unlock(r0 + 2, C_D0, r0 + 2, C_D31)
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
    cv.unlock(r0 + 2, C_NAME, r0 + 7, 15)

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
    cv.unlock(r0 + 2, c_m0, r0 + 7, c_m1)

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
    cv.unlock(r0 + 2, c_n0, r0 + 7, C_RE)


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
    cv.unlock(r0 + 2, C_NAME, r0 + 5, 24)

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
    cv.unlock(r0 + 2, 23, r0 + 5, C_R0 + 1)


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
    cv.unlock(r0 + 2, 17, r0 + 3, C_RE)
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
    cv.unlock(r0 + 1, 17, r0 + 1, C_RE)
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
    cv.unlock(r0 + 1, C_D0, r0 + 1, C_D31)
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
    cv.unlock(r_b + 1, C_NAME, r_b + 4, 10)

    cv.merge(r_b, 12, r_b, 24, "✨  ĐIỀU LÀM TỐT (WHAT WENT WELL)", bold=True, font_size=9,
             align="left", indent=1, bg_color="#FCD5B5", font_color=t.ink)
    cv.merge(r_b + 1, 12, r_b + 4, 24,
             "• Giữ được nhịp dậy sớm & uống đủ nước đều đặn.\n"
             "• Tâm trạng luôn tích cực nhờ viết nhật ký cảm xúc mỗi tối.\n"
             "• Hoàn thành sớm toàn bộ việc ưu tiên trong tuần!",
             font_size=9.2, align="left", indent=1, text_wrap=True, bg_color=t.card, font_color=t.ink)
    cv.box(r_b, 12, r_b + 4, 24, t.line)
    cv.unlock(r_b + 1, 12, r_b + 4, 24)

    cv.merge(r_b, 26, r_b, C_RE, "💡  ĐIỀU CẦN CẢI THIỆN (WHAT DIDN'T GO WELL)", bold=True, font_size=9,
             align="left", indent=1, bg_color="#F4A261", font_color="#FFFFFF")
    cv.merge(r_b + 1, 26, r_b + 4, C_RE,
             "• Vẫn còn lướt điện thoại khuya 2 tối cuối tuần.\n"
             "• Tuần tới cần đặt báo thức ngủ lúc 22h45 & chuẩn bị đồ từ tối hôm trước!",
             font_size=9.2, align="left", indent=1, text_wrap=True, bg_color=t.card, font_color=t.ink)
    cv.box(r_b, 26, r_b + 4, C_RE, t.line)
    cv.unlock(r_b + 1, 26, r_b + 4, C_RE)


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


# --------------------------------------------------------------------------- #
#  Templates 36..40 (DIGIMON 7-STAGE EVOLUTION COLLECTION): Crest Digivice Panel!
# --------------------------------------------------------------------------- #
def add_digimon_crest_panel(wb, cv: Canvas, tr: TrackerRefs, kind: str = "veemon"):
    """Bespoke 7-Stage Digivolution Breakdown + Crest Power Meter + Digivice Mission Log."""
    t = cv.t
    ws = cv.ws
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 24)
    cv.row(r0 + 1, 21)
    cv.row(r0 + 2, 23)
    cv.row(r0 + 3, 20)
    cv.row(r0 + 4, 24)
    cv.row(r0 + 5, 24)

    cfg = {
        "veemon": {
            "banner": "⚡  DIGIVICE D-3  •  CREST OF MIRACLES  •  THỐNG KÊ 7 CẤP TIẾN HÓA VEEMON → MAGNAMON",
            "right_hdr": "👑  MIRACLE CREST POWER",
            "stages": [
                ("🥚 Digi-Egg",    "0%",      "#F3F4F6", "#64748B"),
                ("💧 Chibomon",    "1–19%",   "#E0F2FE", "#0369A1"),
                ("🐾 DemiVeemon",  "20–39%",  "#DBEAFE", "#1D4ED8"),
                ("⚡ Veemon",      "40–59%",  "#BFDBFE", "#1E40AF"),
                ("🔥 Flamedramon", "60–79%",  "#FEE2E2", "#B91C1C"),
                ("🛡️ Paildramon",  "80–99%",  "#CCFBF1", "#0F766E"),
                ("👑 Magnamon",    "100% ✨", "#FEF3C7", "#B45309"),
            ],
            "mission_lbl": "⚡  NHIỆM VỤ DIGIVICE D-3 (GHI CHÚ THÁNG):",
            "mission_txt": "Kích hoạt Golden Armor Evolution! Hoàn thành đều đặn 8 thói quen cốt lõi để mở khóa Magnamon 100% mỗi ngày!",
            "crest_accent": "#D97706",
            "mega_name": "Magnamon",
            "ult_name": "Paildramon",
            "champ_name": "Flamedramon",
            "rookie_name": "Veemon",
        },
        "agumon": {
            "banner": "🔥  CREST OF COURAGE  •  LÒ RÈN DŨNG KHÍ  •  THỐNG KÊ 7 CẤP TIẾN HÓA AGUMON → WARGREYMON",
            "right_hdr": "🛡️  COURAGE FLAME METER",
            "stages": [
                ("🥚 Digi-Egg",    "0%",      "#FFF7ED", "#9A3412"),
                ("⚫ Botamon",     "1–19%",   "#F3F4F6", "#4B5563"),
                ("🩷 Koromon",     "20–39%",  "#FCE7F3", "#BE185D"),
                ("🦖 Agumon",      "40–59%",  "#FEF3C7", "#B45309"),
                ("🔥 Greymon",     "60–79%",  "#FFEDD5", "#C2410C"),
                ("⚙️ MetalGreymon","80–99%",  "#FEE2E2", "#991B1B"),
                ("⚔️ WarGreymon",  "100% ✨", "#FEF08A", "#854D0E"),
            ],
            "mission_lbl": "🔥  NHIỆM VỤ DŨNG KHÍ (COURAGE LOG):",
            "mission_txt": "Không lùi bước trước thói quen khó! Tích lũy chuỗi ngày rèn thể lực & học tập để hóa thân WarGreymon!",
            "crest_accent": "#EA580C",
            "mega_name": "WarGreymon",
            "ult_name": "MetalGreymon",
            "champ_name": "Greymon",
            "rookie_name": "Agumon",
        },
        "gatomon": {
            "banner": "✨  CREST OF LIGHT  •  VÒNG THÁNH ÁNH SÁNG  •  THỐNG KÊ 7 CẤP TIẾN HÓA GATOMON → LOVELYANGEMON",
            "right_hdr": "🌟  HOLY RING RADIANCE",
            "stages": [
                ("🥚 Digi-Egg",      "0%",      "#FDF4FF", "#86198F"),
                ("❄️ YukimiBotamon", "1–19%",   "#F0F9FF", "#0369A1"),
                ("🐱 Nyaromon",      "20–39%",  "#FEF9C3", "#A16207"),
                ("🐶 Salamon",       "40–59%",  "#FAF5FF", "#7E22CE"),
                ("🐾 Gatomon",       "60–79%",  "#F3E8FF", "#6B21A8"),
                ("🪽 Angewomon",     "80–99%",  "#FCE7F3", "#BE185D"),
                ("💖 LovelyAngemon", "100% ✨", "#FEF3C7", "#B45309"),
            ],
            "mission_lbl": "✨  NHẬT KÝ ÁNH SÁNG & BIẾT ƠN (CREST OF LIGHT):",
            "mission_txt": "Giữ tâm thế dịu dàng, chăm sóc bản thân và lan tỏa năng lượng tích cực để rực sáng cùng LovelyAngemon!",
            "crest_accent": "#EC4899",
            "mega_name": "LovelyAngemon",
            "ult_name": "Angewomon",
            "champ_name": "Gatomon",
            "rookie_name": "Salamon",
        },
        "gabumon": {
            "banner": "❄️  CREST OF FRIENDSHIP  •  SÓI BĂNG TRUNG THÀNH  •  THỐNG KÊ 7 CẤP GABUMON → METALGARURUMON",
            "right_hdr": "🐺  FRIENDSHIP BOND POWER",
            "stages": [
                ("🥚 Digi-Egg",       "0%",      "#F0F9FF", "#0369A1"),
                ("🔴 Punimon",        "1–19%",   "#FFE4E6", "#BE123C"),
                ("🦊 Tsunomon",       "20–39%",  "#FEF3C7", "#B45309"),
                ("🐾 Gabumon",        "40–59%",  "#E0F2FE", "#0284C7"),
                ("🐺 Garurumon",      "60–79%",  "#DBEAFE", "#1D4ED8"),
                ("⚡ WereGarurumon",  "80–99%",  "#E0E7FF", "#4338CA"),
                ("🚀 MetalGarurumon", "100% ✨", "#EDE9FE", "#6D28D9"),
            ],
            "mission_lbl": "❄️  CAM KẾT TRUNG THÀNH (FRIENDSHIP STREAK):",
            "mission_txt": "Giữ lời hứa với chính mình như Sói Băng trung thành — duy trì chuỗi không đứt quãng để đạt dạng MetalGarurumon!",
            "crest_accent": "#0284C7",
            "mega_name": "MetalGarurumon",
            "ult_name": "WereGarurumon",
            "champ_name": "Garurumon",
            "rookie_name": "Gabumon",
        },
        "piyomon": {
            "banner": "🔥  CREST OF LOVE  •  ĐÔI CÁNH PHƯỢNG HOÀNG  •  THỐNG KÊ 7 CẤP BIYOMON → PHOENIXMON",
            "right_hdr": "🕊️  PHOENIX LOVE FLAME",
            "stages": [
                ("🥚 Digi-Egg",   "0%",      "#FFF1F2", "#9F1239"),
                ("🌱 Nyokimon",   "1–19%",   "#ECFDF5", "#047857"),
                ("🌷 Yokomon",    "20–39%",  "#FCE7F3", "#BE185D"),
                ("🐦 Biyomon",    "40–59%",  "#FFE4E6", "#E11D48"),
                ("🔥 Birdramon",  "60–79%",  "#FFEDD5", "#C2410C"),
                ("🦅 Garudamon",  "80–99%",  "#FEE2E2", "#B91C1C"),
                ("👑 Phoenixmon", "100% ✨", "#FEF3C7", "#B45309"),
            ],
            "mission_lbl": "❤️  NHẬT KÝ YÊU THƯƠNG & PHẢN TƯ (CREST OF LOVE):",
            "mission_txt": "Mỗi ngày biết ơn và nỗ lực là một ngọn lửa ấm áp nâng đôi cánh rực rỡ hóa thân thành Phượng Hoàng Phoenixmon!",
            "crest_accent": "#E11D48",
            "mega_name": "Phoenixmon",
            "ult_name": "Garudamon",
            "champ_name": "Birdramon",
            "rookie_name": "Biyomon",
        },
        "patamon": {
            "banner": "🪽  CREST OF HOPE  •  MYTHICAL SKY  •  THỐNG KÊ 7 CẤP TIẾN HÓA PATAMON → GRIFFOMON",
            "right_hdr": "✨  MYTHICAL WING POWER",
            "stages": [
                ("🥚 Digi-Egg",       "0%",      "#FFFBEB", "#92400E"),
                ("☁️ Poyomon",        "1–19%",   "#F0F9FF", "#0369A1"),
                ("🐾 Tokomon",        "20–39%",  "#FEF3C7", "#B45309"),
                ("🪽 Patamon",        "40–59%",  "#FFEDD5", "#C2410C"),
                ("🦄 Unimon",         "60–79%",  "#DBEAFE", "#1D4ED8"),
                ("🦅 Hippogriffomon", "80–99%",  "#EDE9FE", "#6D28D9"),
                ("👑 Griffomon",      "100% ✨", "#FEF08A", "#92400E"),
            ],
            "mission_lbl": "🪽  NHẬT KÝ HY VỌNG & ĐÔI CÁNH (CREST OF HOPE):",
            "mission_txt": "Giữ niềm tin vững vàng mỗi ngày — sải rộng đôi cánh kỷ luật từ Patamon lên Thần Thú Bầu Trời Griffomon!",
            "crest_accent": "#F59E0B",
            "mega_name": "Griffomon",
            "ult_name": "Hippogriffomon",
            "champ_name": "Unimon",
            "rookie_name": "Patamon",
        },
        "palmon": {
            "banner": "🌹  CREST OF SINCERITY  •  BLOOMING ROSE GARDEN  •  THỐNG KÊ 7 CẤP PALMON → ROSEMON",
            "right_hdr": "🌸  BLOOMING ROSE POWER",
            "stages": [
                ("🥚 Digi-Egg", "0%",      "#F0FDF4", "#166534"),
                ("☁️ Yuramon",  "1–19%",   "#ECFDF5", "#047857"),
                ("🌱 Tanemon",  "20–39%",  "#DCFCE7", "#15803D"),
                ("🌺 Palmon",   "40–59%",  "#BBF7D0", "#166534"),
                ("🌵 Togemon",  "60–79%",  "#D1FAE5", "#065F46"),
                ("🧚 Lilimon",  "80–99%",  "#FCE7F3", "#BE185D"),
                ("🌹 Rosemon",  "100% ✨", "#FFE4E6", "#BE123C"),
            ],
            "mission_lbl": "🌹  NHẬT KÝ VƯỜN HOA & CHÂN THÀNH (CREST OF SINCERITY):",
            "mission_txt": "Chăm sóc bản thân chân thành mỗi ngày để từng mầm xanh nở rộ thành Nữ Hoàng Hoa Hồng Rosemon 100%!",
            "crest_accent": "#EC4899",
            "mega_name": "Rosemon",
            "ult_name": "Lilimon",
            "champ_name": "Togemon",
            "rookie_name": "Palmon",
        },
        "gomamon": {
            "banner": "🧊  CREST OF RELIABILITY  •  ARCTIC VIKING  •  8 CẤP TIẾN HÓA GOMAMON → ANCIENTMEGATHERIUM",
            "right_hdr": "🛡️  VIKING RELIABILITY",
            "stages": [
                ("🥚 Digi-Egg",    "0%",      "#ECFEFF", "#155E75"),
                ("💧 Pichimon",    "1–14%",   "#E0F2FE", "#0369A1"),
                ("🦭 Bukamon",     "15–29%",  "#F3E8FF", "#6B21A8"),
                ("🐾 Gomamon",     "30–49%",  "#CFFAFE", "#0E7490"),
                ("🦄 Ikkakumon",   "50–69%",  "#DBEAFE", "#1D4ED8"),
                ("🔨 Zudomon",     "70–84%",  "#FEF3C7", "#B45309"),
                ("⚔️ Vikemon",     "85–99%",  "#EDE9FE", "#5B21B6"),
                ("❄️ AncientMega", "100% ✨", "#A5F3FC", "#0F293A"),
            ],
            "mission_lbl": "🧊  CAM KẾT TIN CẬY VIKING (CREST OF RELIABILITY):",
            "mission_txt": "Nói là làm, giữ kỷ luật vững như băng hà — vượt qua mọi thử thách để mở khóa Cổ Thú Băng Hà 100%!",
            "crest_accent": "#06B6D4",
            "ultra_name": "AncientMegatherium",
            "mega_name": "Vikemon",
            "ult_name": "Zudomon",
            "champ_name": "Ikkakumon",
            "rookie_name": "Gomamon",
        },
        "guilmon": {
            "banner": "⚔️  ROYAL KNIGHT  •  DIGITAL HAZARD  •  8 CẤP TIẾN HÓA GUILMON → GALLANTMON CRIMSON",
            "right_hdr": "👑  ROYAL KNIGHT HONOR",
            "stages": [
                ("🥚 Digi-Egg",    "0%",      "#FEF2F2", "#991B1B"),
                ("🔥 Jyarimon",    "1–14%",   "#FFEDD5", "#C2410C"),
                ("🐾 Gigimon",     "15–29%",  "#FEE2E2", "#B91C1C"),
                ("🦖 Guilmon",     "30–49%",  "#FECACA", "#991B1B"),
                ("🔥 Growlmon",    "50–69%",  "#FCA5A5", "#7F1D1D"),
                ("⚙️ WarGrowlmon", "70–84%",  "#E2E8F0", "#334155"),
                ("🛡️ Gallantmon",  "85–99%",  "#FEF3C7", "#B45309"),
                ("👑 CrimsonMode", "100% ✨", "#FEE2E2", "#991B1B"),
            ],
            "mission_lbl": "⚔️  DANH DỰ HIỆP SĨ HOÀNG GIA (ROYAL KNIGHT LOG):",
            "mission_txt": "Rèn kỷ luật thép từng ngày để thức tỉnh Thánh Quang Đỏ Rực — Gallantmon Crimson Mode 100%!",
            "crest_accent": "#DC2626",
            "ultra_name": "Gallantmon Crimson",
            "mega_name": "Gallantmon",
            "ult_name": "WarGrowlmon",
            "champ_name": "Growlmon",
            "rookie_name": "Guilmon",
        },
        "terriermon": {
            "banner": "🌿  MOMENTAI ZEN  •  CHILL TO MECHA  •  THỐNG KÊ 7 CẤP TERRIERMON → MEGAGARGOMON",
            "right_hdr": "💚  MOMENTAI ZEN SCORE",
            "stages": [
                ("🥚 Digi-Egg",     "0%",      "#ECFDF5", "#065F46"),
                ("🌱 Zerimon",      "1–19%",   "#D1FAE5", "#047857"),
                ("🐾 Gummymon",     "20–39%",  "#A7F3D0", "#065F46"),
                ("🐰 Terriermon",   "40–59%",  "#DCFCE7", "#15803D"),
                ("🔫 Gargomon",     "60–79%",  "#E2E8F0", "#334155"),
                ("⚡ Rapidmon",     "80–99%",  "#BBF7D0", "#047857"),
                ("🤖 MegaGargomon", "100% ✨", "#A7F3D0", "#0F2E22"),
            ],
            "mission_lbl": "🌿  GHI CHÚ MOMENTAI (CỨ BÌNH TĨNH & ĐỀU ĐẶN):",
            "mission_txt": "Momentai! Không cần vội vàng, chỉ cần đều đặn mỗi ngày để nâng cấp thành Pháo Đài MegaGargomon 100%!",
            "crest_accent": "#059669",
            "mega_name": "MegaGargomon",
            "ult_name": "Rapidmon",
            "champ_name": "Gargomon",
            "rookie_name": "Terriermon",
        },
        "renamon": {
            "banner": "⛩️  MYSTIC SHRINE  •  KITSUNE SPIRIT  •  8 CẤP TIẾN HÓA RENAMON → KUZUHAMON MIKO",
            "right_hdr": "🔮  SPIRIT FOCUS • TÂM TĨNH",
            "stages": [
                ("🥚 Digi-Egg",     "0%",      "#FAF5FF", "#6B21A8"),
                ("🌕 Relemon",      "1–14%",   "#FEF9C3", "#A16207"),
                ("🦊 Viximon",      "15–29%",  "#FEF08A", "#854D0E"),
                ("🍃 Renamon",      "30–49%",  "#FEF3C7", "#B45309"),
                ("🔥 Youkomon",     "50–69%",  "#EDE9FE", "#5B21B6"),
                ("📜 Doumon",       "70–84%",  "#FFE4E6", "#BE123C"),
                ("⛩️ Kuzuhamon",    "85–99%",  "#DDD6FE", "#4C1D95"),
                ("🌸 KuzuhamonMiko","100% ✨", "#FCE7F3", "#9D174D"),
            ],
            "mission_lbl": "⛩️  TÂM TĨNH & PHẢN TƯ ĐỀN THỜ (MINDFULNESS REFLECTION):",
            "mission_txt": "Giữ tâm tĩnh lặng như Hồ Ly đền thờ — tập trung sâu và chánh niệm mỗi ngày để hóa thân Kuzuhamon Miko!",
            "crest_accent": "#7C3AED",
            "ultra_name": "Kuzuhamon Miko",
            "mega_name": "Kuzuhamon",
            "ult_name": "Doumon",
            "champ_name": "Youkomon",
            "rookie_name": "Renamon",
        },
        "tentomon": {
            "banner": "⚡  CREST OF KNOWLEDGE  •  CYBER LIGHTNING  •  7 CẤP TENTOMON → HERAKLEKABUTERIMON",
            "right_hdr": "💡  KNOWLEDGE VOLTAGE",
            "stages": [
                ("🥚 Digi-Egg",         "0%",      "#EEF2FF", "#3730A3"),
                ("🫧 Bubbmon",          "1–19%",   "#ECFDF5", "#047857"),
                ("🩷 Mochimon",         "20–39%",  "#FCE7F3", "#BE185D"),
                ("🐞 Tentomon",         "40–59%",  "#FEE2E2", "#B91C1C"),
                ("⚡ Kabuterimon",      "60–79%",  "#E0E7FF", "#4338CA"),
                ("🔥 MegaKabuterimon",  "80–99%",  "#FFEDD5", "#C2410C"),
                ("👑 HerakleKabuteri",  "100% ✨", "#FEF3C7", "#B45309"),
            ],
            "mission_lbl": "⚡  NHẬT KÝ TRI THỨC & SÁNG TẠO (CREST OF KNOWLEDGE):",
            "mission_txt": "Tích lũy tri thức và tò mò học hỏi mỗi ngày — nạp đầy điện áp để hóa thân HerakleKabuterimon 100%!",
            "crest_accent": "#4F46E5",
            "mega_name": "HerakleKabuterimon",
            "ult_name": "MegaKabuterimon",
            "champ_name": "Kabuterimon",
            "rookie_name": "Tentomon",
        },
    }[kind]

    cv.merge(r0, C_NAME, r0, C_D31, cfg["banner"], bold=True, font_size=9.4,
             align="left", indent=1, bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_R0, r0, C_RE, cfg["right_hdr"], bold=True, font_size=9,
             align="center", bg_color=t.primary_dark, font_color=t.on_primary)

    # Left 7-stage (4,4,4,5,5,5,5 = 32 cols) OR 8-stage (8 x 4 = 32 cols!) distribution across C_NAME..C_D31!
    is_8 = (len(cfg["stages"]) == 8)
    if is_8:
        stage_spans = [(1 + i * 4, 4 + i * 4) for i in range(8)]
    else:
        stage_spans = [
            (1, 4), (5, 8), (9, 12), (13, 17), (18, 22), (23, 27), (28, 32),
        ]
    stg_rng = f"{tr.calc_q}!{rng(tr.stage_row, 1, tr.stage_row, 31)}"
    for idx, ((c1, c2), (st_lbl, pct_lbl, bg_s, fg_s)) in enumerate(zip(stage_spans, cfg["stages"])):
        stg_num = idx + 1
        cv.merge(r0 + 1, c1, r0 + 1, c2, st_lbl, bold=True, font_size=(8.1 if is_8 else 8.6),
                 align="center", bg_color=bg_s, font_color=fg_s)
        cv.merge(r0 + 2, c1, r0 + 2, c2, f'=COUNTIF({stg_rng},{stg_num})&" ngày"',
                 bold=True, font_size=10.2, align="center", bg_color=t.card, font_color=fg_s,
                 font_name=t.font_title)
        cv.merge(r0 + 3, c1, r0 + 3, c2, pct_lbl, italic=True, font_size=7.8,
                 align="center", bg_color=t.page, font_color=t.muted)

    # Mission / Digivice Log strip (r0+4..r0+5)
    cv.merge(r0 + 4, C_NAME, r0 + 4, C_D31, cfg["mission_lbl"], bold=True, font_size=8.6,
             align="left", indent=1, bg_color=t.soft, font_color=t.primary_dark)
    cv.merge(r0 + 5, C_NAME, r0 + 5, C_D31, cfg["mission_txt"], font_size=9.2,
             align="left", indent=1, text_wrap=True, bg_color=t.card, font_color=t.ink)
    cv.unlock(r0 + 5, C_NAME, r0 + 5, C_D31)
    cv.grid(r0 + 1, C_NAME, r0 + 5, C_D31, t.line)
    cv.box(r0, C_NAME, r0 + 5, C_D31, t.line)

    # Right Crest Evolution Rank Card (C_R0..C_RE, r0+1..r0+5)
    ov = tr.s["overall"]
    if is_8:
        rank_f = (
            f'=IF({ov}>=0.999,"👑 ULTRA: {cfg["ultra_name"]}",'
            f'IF({ov}>=CFG_THR_3,"⚡ MEGA: {cfg["mega_name"]}",'
            f'IF({ov}>=CFG_THR_2,"🔥 ULTIMATE: {cfg["ult_name"]}",'
            f'IF({ov}>=CFG_THR_1,"🛡️ CHAMPION: {cfg["champ_name"]}",'
            f'IF({ov}>=CFG_THR_0,"✨ ROOKIE: {cfg["rookie_name"]}","🥚 DIGI-EGG / TRAINING")))))'
        )
        grown_txt = f'="👑 Ultra 100%: "&{tr.s["perfect"]}&" ngày  •  ⚡ ≥85%: "&{tr.s["grown"]}&"d"'
    else:
        rank_f = (
            f'=IF({ov}>=0.999,"👑 MEGA: {cfg["mega_name"]}",'
            f'IF({ov}>=CFG_THR_3,"⚡ ULTIMATE: {cfg["ult_name"]}",'
            f'IF({ov}>=CFG_THR_2,"🔥 CHAMPION: {cfg["champ_name"]}",'
            f'IF({ov}>=CFG_THR_1,"✨ ROOKIE: {cfg["rookie_name"]}","🥚 DIGI-EGG / TRAINING"))))'
        )
        grown_txt = f'="👑 Mega 100%: "&{tr.s["perfect"]}&" ngày   •   ⚡ ≥80%: "&{tr.s["grown"]}&"d"'
    cv.merge(r0 + 1, C_R0, r0 + 1, C_RE, "CURRENT FORM  •  CẤP HIỆN TẠI", bold=True, font_size=7.8,
             align="center", bg_color=t.soft, font_color=t.muted)
    cv.merge(r0 + 2, C_R0, r0 + 2, C_RE, rank_f, bold=True, font_size=9.4,
             align="center", bg_color=t.card, font_color=t.primary_dark, font_name=t.font_title)
    cv.merge(r0 + 3, C_R0, r0 + 3, C_RE, f"={ov}", bold=True, font_size=9.5,
             align="center", num_format="0%", bg_color=t.card, font_color=t.ink)
    ws.conditional_format(rng(r0 + 3, C_R0, r0 + 3, C_RE), {
        "type": "data_bar", "bar_color": cfg["crest_accent"], "bar_solid": True,
        "min_type": "num", "min_value": 0, "max_type": "num", "max_value": 1,
    })
    cv.merge(r0 + 4, C_R0, r0 + 4, C_RE, grown_txt,
             bold=True, font_size=8.4, align="center", bg_color=t.soft, font_color=t.ink)
    cv.merge(r0 + 5, C_R0, r0 + 5, C_RE,
             f'="🔥 Chuỗi kỷ lục: "&{tr.s["best"]}&" ngày liên tiếp"',
             bold=True, font_size=8.6, align="center", bg_color=t.card, font_color=cfg["crest_accent"])
    cv.grid(r0 + 1, C_R0, r0 + 5, C_RE, t.line)
    cv.box(r0, C_R0, r0 + 5, C_RE, t.line)


# =========================================================================== #
#  BATCH 7 — 13 BESPOKE CAPYBARA CHILL COLLECTION ADDONS (#48–#60, v3.9)
#  ANTI-CLONE DESIGN: Every single one of the 13 themes has its own distinct
#  dashboard structure, metrics, interactivity, and visual silhouette!
# =========================================================================== #

# 48. Avocado Zen: Hydration + Healthy Meal Score + Avocado Chill Rituals & Meal Note
def add_capybara_avocado_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 480):
    t, ws = cv.t, cv.ws
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23); cv.row(r0 + 1, 22); cv.row(r0 + 2, 22); cv.row(r0 + 3, 10)
    for rr in range(r0 + 4, r0 + 8):
        cv.row(rr, 22)

    cv.put(r0, C_NAME, "🥑  AVOCADO ZEN WELLNESS LOG", bold=True, font_size=9.3, align="left", indent=1,
           bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_D0, r0, C_D31, "NƯỚC UỐNG MỖI NGÀY (LÍT)  •  ĐIỂM BỮA ĂN LÀNH MẠNH (1–5)",
             bold=True, font_size=8.4, align="center", bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_R0, r0, C_RE, "🥑  ZEN BALANCE", bold=True, font_size=8.5, align="center",
             bg_color=t.primary_dark, font_color=t.on_primary)

    r_w, r_m = r0 + 1, r0 + 2
    cv.put(r_w, C_NAME, "💧  Nước lọc / Trà xanh (Lít)", bold=True, font_size=8.8, align="left", indent=1,
           bg_color=t.soft, font_color=t.ink)
    cv.put(r_m, C_NAME, "🥗  Bữa ăn lành mạnh (1–5)", bold=True, font_size=8.8, align="left", indent=1,
           bg_color=t.card, font_color=t.ink)

    rnd = random.Random(seed)
    for k in range(1, 32):
        c = day_col(k)
        if k > 22:
            cv.put(r_w, c, "", align="center", font_size=8.3, bg_color=t.card, num_format="0.0")
            cv.put(r_m, c, "", align="center", font_size=8.5, bg_color=t.card, num_format="0")
        else:
            cv.put(r_w, c, rnd.choice([1.8, 2.0, 2.2, 2.5, 2.5, 2.8, 2.0, 2.4]),
                   align="center", font_size=8.3, bg_color=t.card, font_color=t.ink, num_format="0.0")
            cv.put(r_m, c, rnd.choice([4, 4, 5, 4, 5, 3, 5, 4]),
                   align="center", font_size=8.8, bold=True, bg_color=t.card, font_color=t.ink, num_format="0")

    w_rng = rng(r_w, C_D0, r_w, C_D31)
    m_rng = rng(r_m, C_D0, r_m, C_D31)
    cv.unlock(r_w, C_D0, r_m, C_D31)
    cv.grid(r_w, C_NAME, r_m, C_D31, t.line)
    cv.box(r0, C_NAME, r_m, C_D31, t.line)
    ws.conditional_format(w_rng, {"type": "3_color_scale", "min_type": "num", "min_value": 1.0,
                                  "mid_type": "num", "mid_value": 2.0, "max_type": "num", "max_value": 3.0,
                                  "min_color": "#FFFDF7", "mid_color": "#ECFCCB", "max_color": "#A3E635"})
    ws.conditional_format(m_rng, {"type": "3_color_scale", "min_type": "num", "min_value": 1,
                                  "mid_type": "num", "mid_value": 3, "max_type": "num", "max_value": 5,
                                  "min_color": "#FEFCE8", "mid_color": "#D9F99D", "max_color": "#65A30D"})

    cv.merge(r_w, C_R0, r_w, C_R0 + 2, "Nước TB / ngày:", font_size=8.8, align="left", indent=1,
             bg_color=t.card, font_color=t.muted)
    cv.merge(r_w, C_R0 + 3, r_w, C_RE, f"=IFERROR(AVERAGE({w_rng}),0)", bold=True, font_size=10,
             align="center", num_format='0.0" L"', bg_color=t.soft, font_color=t.primary_dark)
    cv.merge(r_m, C_R0, r_m, C_R0 + 2, "Bữa lành mạnh TB:", font_size=8.8, align="left", indent=1,
             bg_color=t.card, font_color=t.muted)
    cv.merge(r_m, C_R0 + 3, r_m, C_RE, f"=IFERROR(AVERAGE({m_rng}),0)", bold=True, font_size=10,
             align="center", num_format='0.0" / 5"', bg_color=t.card, font_color="#854D0E")
    cv.hline(r_w, C_R0, C_RE, t.line)
    cv.box(r0, C_R0, r_m, C_RE, t.line)

    # Bottom 2-column Avocado Chill Rituals & Meal Quick Note + Avocado King Rank Card
    rb0 = r0 + 4
    c_mid = 16
    cv.merge(rb0, C_NAME, rb0, c_mid, "🥑  AVOCADO MEAL & HYDRATION QUICK NOTE", bold=True, font_size=9,
             align="left", indent=1, bg_color="#65A30D", font_color="#FFFFFF")
    notes_l = [
        "• Sáng: Bánh mì bơ nghiền trứng luộc + 1 ly nước ấm chanh tươi.",
        "• Trưa: Cơm gạo lứt, ức gà áp chảo, salad rau xanh dầu ô-liu.",
        "• Tối: Ăn nhẹ trước 19h30, uống trà hoa cúc thả lỏng trước khi ngủ.",
    ]
    for i, txt in enumerate(notes_l):
        cv.merge(rb0 + 1 + i, C_NAME, rb0 + 1 + i, c_mid, txt, font_size=9, align="left", indent=1,
                 bg_color=t.card, font_color=t.ink)
        cv.hline(rb0 + 1 + i, C_NAME, c_mid, t.line)
    cv.unlock(rb0 + 1, C_NAME, rb0 + 3, c_mid)
    cv.box(rb0, C_NAME, rb0 + 3, c_mid, t.line)

    cv.merge(rb0, c_mid + 2, rb0, C_D31, "🌿  CHILL CAPYBARA ZEN RITUALS", bold=True, font_size=9,
             align="left", indent=1, bg_color="#854D0E", font_color="#FFFFFF")
    notes_r = [
        "• Không vội vàng: Hít thở sâu 4-7-8 mỗi khi thấy căng thẳng.",
        "• Chăm chút từng bước nhỏ như Capybara nằm thuyền bơ bình thản.",
        "• Cuối tuần tự thưởng 1 ly sinh tố bơ hoặc đi dạo công viên xanh.",
    ]
    for i, txt in enumerate(notes_r):
        cv.merge(rb0 + 1 + i, c_mid + 2, rb0 + 1 + i, C_D31, txt, font_size=9, align="left", indent=1,
                 bg_color=t.card, font_color=t.ink)
        cv.hline(rb0 + 1 + i, c_mid + 2, C_D31, t.line)
    cv.unlock(rb0 + 1, c_mid + 2, rb0 + 3, C_D31)
    cv.box(rb0, c_mid + 2, rb0 + 3, C_D31, t.line)

    ov = tr.s["overall"]
    cv.merge(rb0, C_R0, rb0, C_RE, "👑  AVOCADO KING RANK", bold=True, font_size=8.8, align="center",
             bg_color=t.primary, font_color=t.on_primary)
    cv.merge(rb0 + 1, C_R0, rb0 + 2, C_RE,
             f'=IF({ov}>=0.999,"👑 Vua Bơ Tối Thượng!",IF({ov}>=0.75,"🥑 Áo Choàng Bơ Xanh",'
             f'IF({ov}>=0.5,"💚 Ôm Bơ Hạnh Phúc","🌱 Đang Nằm Thuyền Bơ")))',
             bold=True, font_size=10, align="center", bg_color=t.soft, font_color=t.primary_dark,
             font_name=t.font_title)
    cv.merge(rb0 + 3, C_R0, rb0 + 3, C_RE,
             f'="🥑 Ngày Bơ Chín: "&{tr.s["grown"]}&"d  •  🔥 Best: "&{tr.s["best"]}&"d"',
             bold=True, font_size=8.5, align="center", bg_color=t.card, font_color="#854D0E")
    cv.box(rb0, C_R0, rb0 + 3, C_RE, t.line)


# 49. Yuzu Onsen Spa: Evening Wind-Down Log + 5 Weekly Onsen Calm Donut Gauges
def add_capybara_onsen_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 490):
    t, ws = cv.t, cv.ws
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23); cv.row(r0 + 1, 22); cv.row(r0 + 2, 10)
    for rr in range(r0 + 3, r0 + 8):
        cv.row(rr, 22)

    cv.put(r0, C_NAME, "🍊  YUZU ONSEN CALM METER", bold=True, font_size=9.3, align="left", indent=1,
           bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_D0, r0, C_D31, "ĐỘ THƯ GIÃN & BÌNH AN BUỔI TỐI MỖI NGÀY (THANG 1 – 5)",
             bold=True, font_size=8.4, align="center", bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_R0, r0, C_RE, "♨️  SPA CALM AVG", bold=True, font_size=8.5, align="center",
             bg_color=t.primary_dark, font_color=t.on_primary)

    r_clm = r0 + 1
    cv.put(r_clm, C_NAME, "♨️  Độ thư giãn cuối ngày (1–5)", bold=True, font_size=8.8, align="left", indent=1,
           bg_color=t.soft, font_color=t.ink)
    rnd = random.Random(seed)
    for k in range(1, 32):
        c = day_col(k)
        val = "" if k > 22 else rnd.choice([4, 4, 5, 5, 3, 4, 5, 4])
        cv.put(r_clm, c, val, align="center", font_size=9, bold=True, bg_color=t.card,
               font_color=t.ink, num_format="0")
    clm_rng = rng(r_clm, C_D0, r_clm, C_D31)
    cv.unlock(r_clm, C_D0, r_clm, C_D31)
    cv.grid(r_clm, C_NAME, r_clm, C_D31, t.line)
    cv.box(r0, C_NAME, r_clm, C_D31, t.line)
    ws.conditional_format(clm_rng, {"type": "3_color_scale", "min_type": "num", "min_value": 1,
                                    "mid_type": "num", "mid_value": 3, "max_type": "num", "max_value": 5,
                                    "min_color": "#FFFBF2", "mid_color": "#FED7AA", "max_color": "#FB923C"})
    cv.merge(r_clm, C_R0, r_clm, C_RE, f"=IFERROR(AVERAGE({clm_rng}),0)", bold=True, font_size=11.5,
             align="center", num_format='0.0" / 5 🍊"', bg_color=t.soft, font_color=t.primary_dark)
    cv.box(r0, C_R0, r_clm, C_RE, t.line)

    # 5 Weekly Onsen Calm Donut Gauges + Evening Wind-Down Card!
    rd = r0 + 3
    cv.merge(rd, C_NAME, rd + 4, C_NAME, "♨️  ONSEN WEEKLY GAUGES\nNhịp thư giãn 5 tuần", bold=True,
             font_size=10, align="center", text_wrap=True, bg_color=t.card, font_color=t.primary_dark,
             font_name=t.font_title)
    rb = tr.calc_row_base
    spans = [(2, 7), (8, 13), (14, 19), (20, 25), (26, 32)]
    dcols = ["#F97316", "#EA580C", "#38BDF8", "#D97706", "#C2410C"]
    for w, (c1, c2) in enumerate(spans):
        hc = CALC_WK_COL0 + w
        cv.merge(rd, c1, rd, c2, f"WEEK {w + 1}", bold=True, font_size=8.4, align="center",
                 bg_color=t.week_head[w], font_color=t.week_on[w])
        cv.merge(rd + 1, c1, rd + 4, c2, f"={tr.calc_q}!{acell(rb + 2, hc)}", bold=True, font_size=13,
                 align="center", num_format="0%", bg_color=t.card, font_color=dcols[w], font_name=t.font_title)
        dch = donut(wb, f"={tr.calc_q}!{rng(rb + 2, hc, rb + 3, hc)}", [dcols[w], t.donut_rest], hole=70)
        place_chart(cv, dch, rd + 1, c1, rd + 4, c2, pad_x=10, pad_y=2)
        cv.vline(c2, rd, rd + 4, t.line, where="right")
    cv.box(rd, C_NAME, rd + 4, C_D31, t.line)

    cv.merge(rd, C_R0, rd, C_RE, "🌙  EVENING WIND-DOWN NOTE", bold=True, font_size=8.6, align="center",
             bg_color="#9A5B2C", font_color="#FFFFFF")
    cv.merge(rd + 1, C_R0, rd + 3, C_RE,
             "• Tắm nước ấm 10p + ngửi tinh dầu cam Yuzu.\n• Buông điện thoại 30p trước giờ đi ngủ.\n• Ghi 1 điều nhẹ lòng trong ngày.",
             font_size=8.7, align="left", indent=1, text_wrap=True, bg_color=t.card, font_color=t.ink)
    cv.unlock(rd + 1, C_R0, rd + 3, C_RE)
    cv.merge(rd + 4, C_R0, rd + 4, C_RE,
             f'="♨️ Ngày Suối Nóng: "&{tr.s["grown"]}&"d  •  ✨ 100%: "&{tr.s["perfect"]}&"d"',
             bold=True, font_size=8.5, align="center", bg_color=t.soft, font_color=t.primary_dark)
    cv.box(rd, C_R0, rd + 4, C_RE, t.line)


# 50. Pip & Puddle Besties: Dual-Tone Pink/Lavender Bestie Bond & 5-Week Milestone Strip
def add_capybara_pip_puddle_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 500):
    t, ws = cv.t, cv.ws
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23)
    for rr in range(r0 + 1, r0 + 7):
        cv.row(rr, 22)

    cv.merge(r0, C_NAME, r0, C_D31, "💕  PIP & PUDDLE BESTIE BOND  •  TIẾN ĐỘ GẮN KẾT 5 TUẦN (DUAL-TONE PINK & LAVENDER)",
             bold=True, font_size=9.2, align="left", indent=1, bg_color="#F472B6", font_color="#FFFFFF")
    cv.merge(r0, C_R0, r0, C_RE, "🎀  DUO BOND LEVEL", bold=True, font_size=8.8, align="center",
             bg_color="#7C3AED", font_color="#FFFFFF")

    rb = tr.calc_row_base
    spans = [(1, 6), (7, 13), (14, 19), (20, 26), (27, 32)]
    w_bgs = ["#FCE7F3", "#EDE9FE", "#FCE7F3", "#EDE9FE", "#FDF2F8"]
    w_fgs = ["#BE185D", "#6D28D9", "#BE185D", "#6D28D9", "#9D174D"]
    w_bars = ["#F472B6", "#A78BFA", "#EC4899", "#8B5CF6", "#DB2777"]
    for w, ((c1, c2), bg, fg, barc) in enumerate(zip(spans, w_bgs, w_fgs, w_bars)):
        hc = CALC_WK_COL0 + w
        pct_ref = f"{tr.calc_q}!{acell(rb + 2, hc)}"
        cv.merge(r0 + 1, c1, r0 + 1, c2, f"💖 WEEK {w + 1}", bold=True, font_size=8.6,
                 align="center", bg_color=bg, font_color=fg)
        cv.merge(r0 + 2, c1, r0 + 2, c2, f"={pct_ref}", bold=True, font_size=11,
                 align="center", num_format="0%", bg_color=t.card, font_color=fg, font_name=t.font_title)
        ws.conditional_format(rng(r0 + 2, c1, r0 + 2, c2), {
            "type": "data_bar", "bar_color": barc, "bar_solid": True,
            "min_type": "num", "min_value": 0, "max_type": "num", "max_value": 1,
        })
        cv.merge(r0 + 3, c1, r0 + 3, c2,
                 f'=IF({pct_ref}>=0.8,"💕 Besties Forever!",IF({pct_ref}>=0.5,"🧣 Chung Khăn Ấm","💤 Đang Ngủ Chung"))',
                 italic=True, font_size=8.0, align="center", bg_color=t.page, font_color=fg)

    # Bottom Shared Wins & Kindness Log (r0+4..r0+6)
    cv.merge(r0 + 4, C_NAME, r0 + 4, C_D31, "💌  BESTIE KINDNESS & SHARED WINS • GÓC CHIA SẺ NIỀM VUI CÙNG PIP & PUDDLE",
             bold=True, font_size=8.8, align="left", indent=1, bg_color="#EDE9FE", font_color="#5B21B6")
    cv.merge(r0 + 5, C_NAME, r0 + 5, C_D31,
             "• Điều ngọt ngào nhất tuần này: Gửi lời hỏi thăm / cảm ơn 1 người bạn thân thiết & cùng nhau giữ kỷ luật!",
             font_size=9.0, align="left", indent=1, bg_color=t.card, font_color=t.ink)
    cv.merge(r0 + 6, C_NAME, r0 + 6, C_D31,
             "• Phần thưởng chung của đôi bạn thân: Cùng đi uống trà sữa / ăn snack ngon khi cả tuần đạt ≥ 80%!",
             font_size=9.0, align="left", indent=1, bg_color=t.card, font_color=t.ink)
    cv.unlock(r0 + 5, C_NAME, r0 + 6, C_D31)
    cv.grid(r0 + 1, C_NAME, r0 + 6, C_D31, t.line)
    cv.box(r0, C_NAME, r0 + 6, C_D31, t.line)

    ov = tr.s["overall"]
    cv.merge(r0 + 1, C_R0, r0 + 1, C_RE, "PIP & PUDDLE STATUS", bold=True, font_size=7.8,
             align="center", bg_color="#FCE7F3", font_color="#BE185D")
    cv.merge(r0 + 2, C_R0, r0 + 3, C_RE,
             f'=IF({ov}>=0.999,"💖 Sending Love 100%!",IF({ov}>=0.75,"🧣 Besties Chung Khăn",'
             f'IF({ov}>=0.5,"🍪 Snack Attack Duo","💤 Nap Buddies")))',
             bold=True, font_size=10, align="center", bg_color=t.card, font_color="#7C3AED",
             font_name=t.font_title)
    cv.merge(r0 + 4, C_R0, r0 + 4, C_RE,
             f'="💕 Tổng tim tích lũy: "&{tr.s["tdone"]}&" lượt"',
             bold=True, font_size=8.8, align="center", bg_color="#F5F3FF", font_color="#6D28D9")
    cv.merge(r0 + 5, C_R0, r0 + 6, C_RE,
             f'="🎀 Ngày gắn kết ≥75%: "&{tr.s["grown"]}&"d"&CHAR(10)&"🔥 Chuỗi Bestie: "&{tr.s["best"]}&" ngày"',
             bold=True, font_size=8.6, align="center", text_wrap=True, bg_color=t.card, font_color="#BE185D")
    cv.grid(r0 + 1, C_R0, r0 + 6, C_RE, t.line)
    cv.box(r0, C_R0, r0 + 6, C_RE, t.line)


# 51. Boba Lily Pond: Weekly Boba Cups Earned Counter + Pond Balance Note
def add_capybara_boba_pond_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 510):
    t, ws = cv.t, cv.ws
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23)
    for rr in range(r0 + 1, r0 + 6):
        cv.row(rr, 22)

    cv.merge(r0, C_NAME, r0, C_D31, "🧋  BOBA LILY POND REWARD COUNTER  •  TÍCH LY TRÀ SỮA DÂU THEO TỪNG TUẦN (MỖI 2 NGÀY ≥75% = 1 LY!)",
             bold=True, font_size=9.0, align="left", indent=1, bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_R0, r0, C_RE, "🧋  TOTAL BOBA CUPS", bold=True, font_size=8.8, align="center",
             bg_color="#DB2777", font_color="#FFFFFF")

    stg_row = tr.stage_row
    wk_day_spans = [(1, 7), (8, 14), (15, 21), (22, 28), (29, 31)]
    col_spans = [(1, 6), (7, 13), (14, 19), (20, 26), (27, 32)]
    for w, ((d1, d2), (c1, c2)) in enumerate(zip(wk_day_spans, col_spans)):
        st_rng = f"{tr.calc_q}!{rng(stg_row, d1, stg_row, d2)}"
        cups_expr = f'INT(COUNTIF({st_rng},">=5")/2)'
        cv.merge(r0 + 1, c1, r0 + 1, c2, f"🪷 WEEK {w + 1} (Ngày {d1}–{d2})", bold=True, font_size=8.4,
                 align="center", bg_color=t.week_head[w], font_color=t.week_on[w])
        cv.merge(r0 + 2, c1, r0 + 2, c2, f'={cups_expr}&" ly 🧋"', bold=True, font_size=11.5,
                 align="center", bg_color=t.card, font_color="#DB2777", font_name=t.font_title)
        cv.merge(r0 + 3, c1, r0 + 3, c2, f'=COUNTIF({st_rng},">=5")&" ngày đạt ≥75%"', italic=True,
                 font_size=8.0, align="center", bg_color=t.soft, font_color=t.primary_dark)

    cv.merge(r0 + 4, C_NAME, r0 + 4, C_D31, "🪷  BOBA & HYDRATION BALANCE NOTE  •  GHI CHÚ THƯỞNG TRÀ SỮA LÀNH MẠNH",
             bold=True, font_size=8.6, align="left", indent=1, bg_color="#DCFCE7", font_color="#166534")
    cv.merge(r0 + 5, C_NAME, r0 + 5, C_D31,
             "• Quy tắc hồ sen: Uống đủ 2L nước lọc mỗi ngày & chỉ thưởng 1 ly trà sữa ít đường (30% đường) khi đạt đủ mốc tuần!",
             font_size=9.0, align="left", indent=1, bg_color=t.card, font_color=t.ink)
    cv.unlock(r0 + 5, C_NAME, r0 + 5, C_D31)
    cv.grid(r0 + 1, C_NAME, r0 + 5, C_D31, t.line)
    cv.box(r0, C_NAME, r0 + 5, C_D31, t.line)

    cv.merge(r0 + 1, C_R0, r0 + 2, C_RE, f'=INT({tr.s["grown"]}/2)&" LY 🧋"', bold=True, font_size=16,
             align="center", bg_color="#FCE7F3", font_color="#BE185D", font_name=t.font_title)
    cv.merge(r0 + 3, C_R0, r0 + 3, C_RE, f'="🪷 Ngày hồ sen ≥75%: "&{tr.s["grown"]}&" ngày"',
             bold=True, font_size=8.6, align="center", bg_color=t.soft, font_color=t.primary_dark)
    cv.merge(r0 + 4, C_R0, r0 + 5, C_RE,
             f'="✨ Ngày 100% Boba King: "&{tr.s["perfect"]}&"d"&CHAR(10)&"🔥 Best Streak: "&{tr.s["best"]}&"d"',
             bold=True, font_size=8.6, align="center", text_wrap=True, bg_color=t.card, font_color=t.ink)
    cv.grid(r0 + 1, C_R0, r0 + 5, C_RE, t.line)
    cv.box(r0, C_R0, r0 + 5, C_RE, t.line)


# 52. Bookworm Study: Daily Focus Hours + Pages Read + Study Focus Column Chart + Chapter Notes
def add_capybara_bookworm_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 520):
    t, ws, q = cv.t, cv.ws, tr.q
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23); cv.row(r0 + 1, 22); cv.row(r0 + 2, 22); cv.row(r0 + 3, 10)
    for rr in range(r0 + 4, r0 + 10):
        cv.row(rr, 20)

    cv.put(r0, C_NAME, "📚  CAPY & CHAPTERED STUDY LOG", bold=True, font_size=9.2, align="left", indent=1,
           bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_D0, r0, C_D31, "GIỜ TẬP TRUNG HỌC (HOURS)  •  SỐ TRANG SÁCH ĐỌC MỖI NGÀY (PAGES)",
             bold=True, font_size=8.4, align="center", bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_R0, r0, C_RE, "📖  STUDY TOTALS", bold=True, font_size=8.5, align="center",
             bg_color=t.primary_dark, font_color=t.on_primary)

    r_h, r_p = r0 + 1, r0 + 2
    cv.put(r_h, C_NAME, "⏱️  Giờ tập trung (Focus Hours)", bold=True, font_size=8.8, align="left", indent=1,
           bg_color=t.soft, font_color=t.ink)
    cv.put(r_p, C_NAME, "📖  Số trang sách đọc (Pages)", bold=True, font_size=8.8, align="left", indent=1,
           bg_color=t.card, font_color=t.ink)
    rnd = random.Random(seed)
    for k in range(1, 32):
        c = day_col(k)
        if k > 22:
            cv.put(r_h, c, "", align="center", font_size=8.3, bg_color=t.card, num_format="0.0")
            cv.put(r_p, c, "", align="center", font_size=8.3, bg_color=t.card, num_format="0")
        else:
            cv.put(r_h, c, rnd.choice([2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 3.0, 5.0]),
                   align="center", font_size=8.3, bold=True, bg_color=t.card, font_color=t.ink, num_format="0.0")
            cv.put(r_p, c, rnd.choice([12, 15, 20, 25, 30, 18, 22, 35]),
                   align="center", font_size=8.3, bg_color=t.card, font_color=t.ink, num_format="0")

    h_rng = rng(r_h, C_D0, r_h, C_D31)
    p_rng = rng(r_p, C_D0, r_p, C_D31)
    cv.unlock(r_h, C_D0, r_p, C_D31)
    cv.grid(r_h, C_NAME, r_p, C_D31, t.line)
    cv.box(r0, C_NAME, r_p, C_D31, t.line)
    ws.conditional_format(h_rng, {"type": "3_color_scale", "min_type": "num", "min_value": 0,
                                  "mid_type": "num", "mid_value": 3, "max_type": "num", "max_value": 6,
                                  "min_color": "#FFFDF5", "mid_color": "#FEF08A", "max_color": "#EAB308"})
    ws.conditional_format(p_rng, {"type": "3_color_scale", "min_type": "num", "min_value": 0,
                                  "mid_type": "num", "mid_value": 20, "max_type": "num", "max_value": 40,
                                  "min_color": "#FFFDF5", "mid_color": "#BAE6FD", "max_color": "#0284C7"})

    cv.merge(r_h, C_R0, r_h, C_R0 + 2, "Tổng giờ học:", font_size=8.8, align="left", indent=1, bg_color=t.card, font_color=t.muted)
    cv.merge(r_h, C_R0 + 3, r_h, C_RE, f"=SUM({h_rng})", bold=True, font_size=10.5, align="center",
             num_format='0.0" h"', bg_color=t.soft, font_color=t.primary_dark)
    cv.merge(r_p, C_R0, r_p, C_R0 + 2, "Tổng trang sách:", font_size=8.8, align="left", indent=1, bg_color=t.card, font_color=t.muted)
    cv.merge(r_p, C_R0 + 3, r_p, C_RE, f"=SUM({p_rng})", bold=True, font_size=10.5, align="center",
             num_format='#,##0" tr"', bg_color="#E0F2FE", font_color="#0369A1")
    cv.hline(r_h, C_R0, C_RE, t.line)
    cv.box(r0, C_R0, r_p, C_RE, t.line)

    # Focus Hours Column Chart + Bookworm Chapter Notes
    rc0, rc1 = r0 + 4, r0 + 9
    ch = wb.add_chart({"type": "column"})
    ch.add_series({
        "name": "Focus Hours",
        "categories": f"={q}!{rng(R_DAY, C_D0, R_DAY, C_D31)}",
        "values": f"={q}!{h_rng}",
        "fill": {"color": "#EAB308"},
        "border": {"none": True},
        "gap": 55,
    })
    ch.set_title({"name": "DAILY STUDY HOURS • GIỜ HỌC TẬP TRUNG MỖI NGÀY",
                  "name_font": {"name": t.font, "size": 9.2, "bold": True, "color": t.ink}})
    ch.set_y_axis({"min": 0, "max": 6, "major_unit": 2, "num_format": '0"h"',
                   "num_font": axis_font(t), "line": {"none": True},
                   "major_gridlines": {"visible": True, "line": {"color": t.line, "dash_type": "dash"}}})
    ch.set_x_axis({"num_font": axis_font(t, 7.5), "line": {"color": t.line}})
    ch.set_legend({"none": True})
    ch.set_chartarea({"border": {"color": t.line, "width": 0.75}, "fill": {"color": t.card}})
    place_chart(cv, ch, rc0, C_NAME, rc1, C_D31)

    cv.merge(rc0, C_R0, rc0, C_RE, "📚  CURRENT BOOK & NOTES", bold=True, font_size=8.6, align="center",
             bg_color="#0284C7", font_color="#FFFFFF")
    cv.merge(rc0 + 1, C_R0, rc0 + 3, C_RE,
             "• Sách đang đọc: Atomic Habits\n• Mục tiêu tháng: 500 trang + 80h học\n• Ghi chú: Tóm tắt 3 ý chính mỗi chương!",
             font_size=8.6, align="left", indent=1, text_wrap=True, bg_color=t.card, font_color=t.ink)
    cv.unlock(rc0 + 1, C_R0, rc0 + 3, C_RE)
    cv.merge(rc0 + 4, C_R0, rc1, C_RE,
             f'="📖 TB: "&TEXT(IFERROR(AVERAGE({p_rng}),0),"0")&" trang/ngày"&CHAR(10)&"🏆 Ngày Mọt Sách: "&{tr.s["grown"]}&"d"',
             bold=True, font_size=8.8, align="center", text_wrap=True, bg_color=t.soft, font_color=t.primary_dark)
    cv.box(rc0, C_R0, rc1, C_RE, t.line)


# 53. Lofi Picnic Beats: Deep Flow Minutes + Lofi Playlist & Picnic Vibe Board
def add_capybara_lofi_picnic_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 530):
    t, ws = cv.t, cv.ws
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23); cv.row(r0 + 1, 22); cv.row(r0 + 2, 10)
    for rr in range(r0 + 3, r0 + 7):
        cv.row(rr, 22)

    cv.put(r0, C_NAME, "🎧  LOFI DEEP FLOW MINUTES", bold=True, font_size=9.2, align="left", indent=1,
           bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_D0, r0, C_D31, "SỐ PHÚT DEEP WORK / HỌC CÙNG NHẠC LOFI MỖI NGÀY (PHÚT)",
             bold=True, font_size=8.4, align="center", bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_R0, r0, C_RE, "🎵  FLOW TOTAL", bold=True, font_size=8.5, align="center",
             bg_color="#DC2626", font_color="#FFFFFF")

    r_fl = r0 + 1
    cv.put(r_fl, C_NAME, "🎵  Phút tập trung Lofi (mins)", bold=True, font_size=8.8, align="left", indent=1,
           bg_color=t.soft, font_color=t.ink)
    rnd = random.Random(seed)
    for k in range(1, 32):
        c = day_col(k)
        val = "" if k > 22 else rnd.choice([45, 60, 90, 120, 75, 90, 60, 105])
        cv.put(r_fl, c, val, align="center", font_size=8.3, bold=True, bg_color=t.card,
               font_color=t.ink, num_format="0")
    fl_rng = rng(r_fl, C_D0, r_fl, C_D31)
    cv.unlock(r_fl, C_D0, r_fl, C_D31)
    cv.grid(r_fl, C_NAME, r_fl, C_D31, t.line)
    cv.box(r0, C_NAME, r_fl, C_D31, t.line)
    ws.conditional_format(fl_rng, {"type": "3_color_scale", "min_type": "num", "min_value": 0,
                                   "mid_type": "num", "mid_value": 60, "max_type": "num", "max_value": 120,
                                   "min_color": "#F0F7FF", "mid_color": "#BFDBFE", "max_color": "#3B82F6"})
    cv.merge(r_fl, C_R0, r_fl, C_RE, f"=SUM({fl_rng})/60", bold=True, font_size=11, align="center",
             num_format='0.0" giờ 🎧"', bg_color="#FEE2E2", font_color="#B91C1C")
    cv.box(r0, C_R0, r_fl, C_RE, t.line)

    rb0 = r0 + 3
    c_mid = 16
    cv.merge(rb0, C_NAME, rb0, c_mid, "📻  NOW PLAYING • PLAYLIST LOFI YÊU THÍCH", bold=True, font_size=9,
             align="left", indent=1, bg_color="#2563EB", font_color="#FFFFFF")
    tracks = [
        "♫  Track 01: Cozy Rainy Day Capybara Beats (Study & Chill 90 BPM)",
        "♫  Track 02: Sunday Gingham Picnic Acoustic Guitar & Birds",
        "♫  Track 03: Midnight Tea & Soft Piano Deep Focus Mix",
    ]
    for i, trk in enumerate(tracks):
        cv.merge(rb0 + 1 + i, C_NAME, rb0 + 1 + i, c_mid, trk, font_size=8.9, align="left", indent=1,
                 bg_color=t.card, font_color=t.ink)
        cv.hline(rb0 + 1 + i, C_NAME, c_mid, t.line)
    cv.unlock(rb0 + 1, C_NAME, rb0 + 3, c_mid)
    cv.box(rb0, C_NAME, rb0 + 3, c_mid, t.line)

    cv.merge(rb0, c_mid + 2, rb0, C_D31, "🧺  PICNIC VIBE & RECHARGE NOTES", bold=True, font_size=9,
             align="left", indent=1, bg_color="#EF4444", font_color="#FFFFFF")
    vibes = [
        "• Đeo tai nghe, tắt thông báo 45 phút để vào trạng thái Flow êm ái.",
        "• Nghỉ giữa giờ: Vươn vai, nhìn cây xanh & nhâm nhi trái cây tươi.",
        "• Cuối tuần trải khăn caro đọc sách ngoài công viên sạc lại năng lượng!",
    ]
    for i, vb in enumerate(vibes):
        cv.merge(rb0 + 1 + i, c_mid + 2, rb0 + 1 + i, C_D31, vb, font_size=8.9, align="left", indent=1,
                 bg_color=t.card, font_color=t.ink)
        cv.hline(rb0 + 1 + i, c_mid + 2, C_D31, t.line)
    cv.unlock(rb0 + 1, c_mid + 2, rb0 + 3, C_D31)
    cv.box(rb0, c_mid + 2, rb0 + 3, C_D31, t.line)

    cv.merge(rb0, C_R0, rb0, C_RE, "🎶  LOFI FLOW STATS", bold=True, font_size=8.8, align="center",
             bg_color=t.primary_dark, font_color="#FFFFFF")
    cv.merge(rb0 + 1, C_R0, rb0 + 2, C_RE,
             f'="🎧 TB: "&TEXT(IFERROR(AVERAGE({fl_rng}),0),"0")&" phút/ngày"',
             bold=True, font_size=10.5, align="center", bg_color=t.soft, font_color=t.primary_dark,
             font_name=t.font_title)
    cv.merge(rb0 + 3, C_R0, rb0 + 3, C_RE,
             f'="🧺 Ngày Chill: "&{tr.s["grown"]}&"d  •  🔥 Best: "&{tr.s["best"]}&"d"',
             bold=True, font_size=8.5, align="center", bg_color=t.card, font_color="#DC2626")
    cv.box(rb0, C_R0, rb0 + 3, C_RE, t.line)


# 54. Foodie Snack Club: 6-Tier Snack Reward Unlock Strip + Weekly Treat Menu
def add_capybara_foodie_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 540):
    t, ws = cv.t, cv.ws
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23)
    for rr in range(r0 + 1, r0 + 6):
        cv.row(rr, 22)

    cv.merge(r0, C_NAME, r0, C_D31, "🍔  FOODIE SNACK CLUB  •  THỐNG KÊ 6 MÓN ĂN MỞ KHÓA TRONG THÁNG",
             bold=True, font_size=9.2, align="left", indent=1, bg_color="#EF4444", font_color="#FFFFFF")
    cv.merge(r0, C_R0, r0, C_RE, "🍟  FOODIE RANK", bold=True, font_size=8.8, align="center",
             bg_color="#D97706", font_color="#FFFFFF")

    stg_rng = f"{tr.calc_q}!{rng(tr.stage_row, 1, tr.stage_row, 31)}"
    tiers = [
        ("🥛 Milk", "0%", "#FEF2F2", "#B91C1C"),
        ("🍓 Sip Milk", "1–24%", "#FFFBEB", "#B45309"),
        ("🍉 Melon", "25–49%", "#ECFDF5", "#047857"),
        ("🍿 Popcorn", "50–74%", "#FEF3C7", "#D97706"),
        ("🍕 Pizza", "75–99%", "#FFEDD5", "#C2410C"),
        ("🍔 Burger!", "100% ✨", "#FEE2E2", "#991B1B"),
    ]
    spans = [(1, 5), (6, 10), (11, 15), (16, 21), (22, 26), (27, 32)]
    for i, ((c1, c2), (lbl, pct, bg, fg)) in enumerate(zip(spans, tiers)):
        cv.merge(r0 + 1, c1, r0 + 1, c2, lbl, bold=True, font_size=8.8, align="center", bg_color=bg, font_color=fg)
        cv.merge(r0 + 2, c1, r0 + 2, c2, f'=COUNTIF({stg_rng},{i + 1})&" ngày"', bold=True, font_size=10.5,
                 align="center", bg_color=t.card, font_color=fg, font_name=t.font_title)
        cv.merge(r0 + 3, c1, r0 + 3, c2, pct, italic=True, font_size=7.8, align="center", bg_color=t.page, font_color=t.muted)

    cv.merge(r0 + 4, C_NAME, r0 + 4, C_D31, "🍕  WEEKLY TREAT REWARD MENU  •  PHẦN THƯỞNG MÓN NGON KHI ĐẠT MỤC TIÊU TUẦN",
             bold=True, font_size=8.6, align="left", indent=1, bg_color="#FEF3C7", font_color="#92400E")
    cv.merge(r0 + 5, C_NAME, r0 + 5, C_D31,
             "• Tuần ≥80%: Thưởng 1 bữa ăn yêu thích không áy náy!  • Mục tiêu tháng: Ăn đủ chất, nấu ở nhà ≥5 ngày/tuần & uống đủ nước.",
             font_size=9.0, align="left", indent=1, bg_color=t.card, font_color=t.ink)
    cv.unlock(r0 + 5, C_NAME, r0 + 5, C_D31)
    cv.grid(r0 + 1, C_NAME, r0 + 5, C_D31, t.line)
    cv.box(r0, C_NAME, r0 + 5, C_D31, t.line)

    ov = tr.s["overall"]
    cv.merge(r0 + 1, C_R0, r0 + 2, C_RE,
             f'=IF({ov}>=0.999,"👑 BURGER KING!",IF({ov}>=0.75,"🍕 PIZZA CHEF",'
             f'IF({ov}>=0.5,"🍿 POPCORN FAN","🍉 FRESH FOODIE")))',
             bold=True, font_size=10.5, align="center", bg_color="#FEF3C7", font_color="#B91C1C",
             font_name=t.font_title)
    cv.merge(r0 + 3, C_R0, r0 + 3, C_RE, f"={ov}", bold=True, font_size=9.5, align="center",
             num_format="0%", bg_color=t.card, font_color=t.ink)
    ws.conditional_format(rng(r0 + 3, C_R0, r0 + 3, C_RE), {
        "type": "data_bar", "bar_color": "#F59E0B", "bar_solid": True,
        "min_type": "num", "min_value": 0, "max_type": "num", "max_value": 1,
    })
    cv.merge(r0 + 4, C_R0, r0 + 5, C_RE,
             f'="🍔 Ngày 100%: "&{tr.s["perfect"]}&" ngày"&CHAR(10)&"🔥 Streak: "&{tr.s["best"]}&" ngày"',
             bold=True, font_size=8.6, align="center", text_wrap=True, bg_color=t.card, font_color="#B45309")
    cv.grid(r0 + 1, C_R0, r0 + 5, C_RE, t.line)
    cv.box(r0, C_R0, r0 + 5, C_RE, t.line)


# 55. Dino Hoodie Play: Daily Playful Joy Row + 5-Week Pastel Dino Progress Bars
def add_capybara_dino_hoodie_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 550):
    t, ws = cv.t, cv.ws
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23); cv.row(r0 + 1, 22); cv.row(r0 + 2, 10)
    for rr in range(r0 + 3, r0 + 7):
        cv.row(rr, 22)

    cv.put(r0, C_NAME, "🦕  DAILY JOY & PLAYFULNESS", bold=True, font_size=9.2, align="left", indent=1,
           bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_D0, r0, C_D31, "MỨC ĐỘ VUI VẺ & HỨNG KHỞI MỖI NGÀY CÙNG DINO HOODIE (1 – 5)",
             bold=True, font_size=8.4, align="center", bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_R0, r0, C_RE, "🐤  JOY SCORE", bold=True, font_size=8.5, align="center",
             bg_color="#EAB308", font_color="#422006")

    r_joy = r0 + 1
    cv.put(r_joy, C_NAME, "🌼  Điểm niềm vui trong ngày (1–5)", bold=True, font_size=8.8, align="left", indent=1,
           bg_color=t.soft, font_color=t.ink)
    rnd = random.Random(seed)
    for k in range(1, 32):
        c = day_col(k)
        val = "" if k > 22 else rnd.choice([4, 5, 4, 5, 3, 5, 4, 5])
        cv.put(r_joy, c, val, align="center", font_size=9, bold=True, bg_color=t.card, font_color=t.ink, num_format="0")
    j_rng = rng(r_joy, C_D0, r_joy, C_D31)
    cv.unlock(r_joy, C_D0, r_joy, C_D31)
    cv.grid(r_joy, C_NAME, r_joy, C_D31, t.line)
    cv.box(r0, C_NAME, r_joy, C_D31, t.line)
    ws.conditional_format(j_rng, {"type": "3_color_scale", "min_type": "num", "min_value": 1,
                                  "mid_type": "num", "mid_value": 3, "max_type": "num", "max_value": 5,
                                  "min_color": "#FEF9C3", "mid_color": "#BBF7D0", "max_color": "#22C55E"})
    cv.merge(r_joy, C_R0, r_joy, C_RE, f"=IFERROR(AVERAGE({j_rng}),0)", bold=True, font_size=11,
             align="center", num_format='0.0" / 5 🦕"', bg_color="#FEF9C3", font_color="#854D0E")
    cv.box(r0, C_R0, r_joy, C_RE, t.line)

    # 5-Week Playful Pastel Progress Bars!
    rb0 = r0 + 3
    rb = tr.calc_row_base
    cv.merge(rb0, C_NAME, rb0, C_D31, "🦖  PLAYFUL DINO WEEKLY BARS  •  THANH TIẾN ĐỘ PASTEL 5 TUẦN",
             bold=True, font_size=9, align="left", indent=1, bg_color="#16A34A", font_color="#FFFFFF")
    spans = [(1, 6), (7, 13), (14, 19), (20, 26), (27, 32)]
    p_cols = ["#4ADE80", "#FACC15", "#FB923C", "#34D399", "#A3E635"]
    p_bgs = ["#DCFCE7", "#FEF9C3", "#FFEDD5", "#D1FAE5", "#ECFCCB"]
    p_fgs = ["#166534", "#854D0E", "#9A3412", "#065F46", "#3F6212"]
    for w, ((c1, c2), bc, bg, fg) in enumerate(zip(spans, p_cols, p_bgs, p_fgs)):
        hc = CALC_WK_COL0 + w
        pct_ref = f"{tr.calc_q}!{acell(rb + 2, hc)}"
        cv.merge(rb0 + 1, c1, rb0 + 1, c2, f"🦖 WEEK {w + 1}", bold=True, font_size=8.5, align="center",
                 bg_color=bg, font_color=fg)
        cv.merge(rb0 + 2, c1, rb0 + 2, c2, f"={pct_ref}", bold=True, font_size=11, align="center",
                 num_format="0%", bg_color=t.card, font_color=fg, font_name=t.font_title)
        ws.conditional_format(rng(rb0 + 2, c1, rb0 + 2, c2), {
            "type": "data_bar", "bar_color": bc, "bar_solid": True,
            "min_type": "num", "min_value": 0, "max_type": "num", "max_value": 1,
        })
        cv.merge(rb0 + 3, c1, rb0 + 3, c2,
                 f'=IF({pct_ref}>=0.8,"🦖 Dino Siêu Quậy!",IF({pct_ref}>=0.5,"🦕 Khoác Áo Dino","🥚 Bé Dino Ngủ"))',
                 italic=True, font_size=8.0, align="center", bg_color=t.page, font_color=fg)
    cv.grid(rb0 + 1, C_NAME, rb0 + 3, C_D31, t.line)
    cv.box(rb0, C_NAME, rb0 + 3, C_D31, t.line)

    cv.merge(rb0, C_R0, rb0, C_RE, "🌼  DINO PLAYTIME NOTE", bold=True, font_size=8.6, align="center",
             bg_color="#FB923C", font_color="#FFFFFF")
    cv.merge(rb0 + 1, C_R0, rb0 + 2, C_RE,
             "• Mỗi ngày dành 20p cho sở thích cá nhân (vẽ, chơi game nhẹ, đi dạo)!",
             font_size=8.6, align="left", indent=1, text_wrap=True, bg_color=t.card, font_color=t.ink)
    cv.unlock(rb0 + 1, C_R0, rb0 + 2, C_RE)
    cv.merge(rb0 + 3, C_R0, rb0 + 3, C_RE,
             f'="🦖 Dino Days: "&{tr.s["grown"]}&"d  •  🔥 Best: "&{tr.s["best"]}&"d"',
             bold=True, font_size=8.5, align="center", bg_color=t.soft, font_color=t.primary_dark)
    cv.box(rb0, C_R0, rb0 + 3, C_RE, t.line)


# 56. Apple Orchard Sweet: Live Orchard Apple Harvest Counter + 3-Line Gratitude Box
def add_capybara_apple_orchard_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 560):
    t, ws = cv.t, cv.ws
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23)
    for rr in range(r0 + 1, r0 + 6):
        cv.row(rr, 22)

    # Left: Orchard Harvest Basket Breakdown (Col B..N)
    c_mid = 13
    cv.merge(r0, C_NAME, r0, c_mid, "🍎  APPLE ORCHARD HARVEST COUNTER  •  GIỎ TÁO THU HOẠCH THÁNG",
             bold=True, font_size=9.1, align="left", indent=1, bg_color="#E11D48", font_color="#FFFFFF")
    cv.merge(r0 + 1, C_NAME, r0 + 3, 5,
             f'="🍎 "&{tr.s["tdone"]}&CHAR(10)&"QUẢ TÁO ĐÃ HÁI"',
             bold=True, font_size=14, align="center", text_wrap=True, bg_color="#FFE4E6", font_color="#BE123C",
             font_name=t.font_title)
    cv.merge(r0 + 1, 6, r0 + 1, c_mid, f'="🌿 Giỏ Táo Đầy (ngày ≥75%):  "&{tr.s["grown"]}&" giỏ"',
             bold=True, font_size=9.2, align="left", indent=1, bg_color=t.card, font_color="#166534")
    cv.merge(r0 + 2, 6, r0 + 2, c_mid, f'="❤️ Ngày Ôm Táo 100%:  "&{tr.s["perfect"]}&" ngày trọn vẹn"',
             bold=True, font_size=9.2, align="left", indent=1, bg_color="#FFF6ED", font_color="#BE123C")
    cv.merge(r0 + 3, 6, r0 + 3, c_mid, f'="🎯 Tỷ lệ thu hoạch mục tiêu:  "&TEXT({tr.s["overall"]},"0%")',
             bold=True, font_size=9.2, align="left", indent=1, bg_color=t.card, font_color=t.ink)
    cv.merge(r0 + 4, C_NAME, r0 + 5, c_mid,
             f'=IF({tr.s["tdone"]}>=200,"🏆 Mùa Vụ Táo Đỏ Bội Thu (>200 quả)!",IF({tr.s["tdone"]}>=100,"🍎 Vườn Táo Đang Chín Đỏ (>100 quả)!","🌱 Bắt đầu hái những quả táo ngọt đầu tiên!"))',
             bold=True, font_size=9.3, align="center", bg_color="#DCFCE7", font_color="#166534")
    cv.grid(r0 + 1, C_NAME, r0 + 5, c_mid, t.line)
    cv.box(r0, C_NAME, r0 + 5, c_mid, "#E11D48")

    # Right-Mid: 3-Line Sweet Orchard Gratitude Box (Col P..AG)
    c_g0 = c_mid + 2
    cv.merge(r0, c_g0, r0, C_D31, "💌  SWEET ORCHARD GRATITUDE  •  3 ĐIỀU NGỌT NGÀO BIẾT ƠN THÁNG NÀY",
             bold=True, font_size=9.1, align="left", indent=1, bg_color="#16A34A", font_color="#FFFFFF")
    grats = [
        "1. Biết ơn cơ thể khỏe mạnh giúp mình hoàn thành đều đặn những thói quen nhỏ mỗi ngày.",
        "2. Biết ơn những bữa ăn ngon, trái cây ngọt lành & giấc ngủ trọn vẹn.",
        "3. Biết ơn bản thân đã kiên trì và dịu dàng với chính mình suốt cả tháng!",
        "",
        "",
    ]
    for i, g in enumerate(grats):
        cv.merge(r0 + 1 + i, c_g0, r0 + 1 + i, C_D31, g, font_size=9.0, align="left", indent=1,
                 bg_color=t.card, font_color=t.ink)
        cv.hline(r0 + 1 + i, c_g0, C_D31, t.line)
    cv.unlock(r0 + 1, c_g0, r0 + 5, C_D31)
    cv.box(r0, c_g0, r0 + 5, C_D31, "#16A34A")

    # Far Right: Sweet Apple Harvest Gauge Card
    cv.merge(r0, C_R0, r0, C_RE, "🍏  HARVEST GOAL", bold=True, font_size=8.8, align="center",
             bg_color=t.primary_dark, font_color="#FFFFFF")
    cv.merge(r0 + 1, C_R0, r0 + 2, C_RE, f"=MIN(1,{tr.s['tdone']}/220)", bold=True, font_size=14,
             align="center", num_format="0%", bg_color="#FFE4E6", font_color="#BE123C", font_name=t.font_title)
    ws.conditional_format(rng(r0 + 1, C_R0, r0 + 2, C_RE), {
        "type": "data_bar", "bar_color": "#E11D48", "bar_solid": True,
        "min_type": "num", "min_value": 0, "max_type": "num", "max_value": 1,
    })
    cv.merge(r0 + 3, C_R0, r0 + 3, C_RE, "Mốc vụ mùa: 220 táo", italic=True, font_size=8.2,
             align="center", bg_color=t.card, font_color=t.muted)
    cv.merge(r0 + 4, C_R0, r0 + 5, C_RE,
             f'="🔥 Chuỗi Vườn Táo:"&CHAR(10)&{tr.s["best"]}&" ngày liên tiếp"',
             bold=True, font_size=8.8, align="center", text_wrap=True, bg_color="#DCFCE7", font_color="#166534")
    cv.grid(r0 + 1, C_R0, r0 + 5, C_RE, t.line)
    cv.box(r0, C_R0, r0 + 5, C_RE, t.line)


# 57. Pink Cloud Chill: Intentionally Ultra-Clean Minimalist 4-Row Pink Cloud Chill Bar!
def add_capybara_pink_chill_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 570):
    t, ws = cv.t, cv.ws
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23); cv.row(r0 + 1, 24); cv.row(r0 + 2, 24)

    cv.merge(r0, C_NAME, r0, C_D31, "☁️  PINK CLOUD MINIMALIST CHILL BAR  •  NHỊP SỐNG CHẬM & ÊM ÁI TRÊN MÂY HỒNG",
             bold=True, font_size=9.2, align="left", indent=1, bg_color="#DB2777", font_color="#FFFFFF")
    cv.merge(r0, C_R0, r0, C_RE, "🌸  PEACE SCORE", bold=True, font_size=8.8, align="center",
             bg_color="#9D174D", font_color="#FFFFFF")

    ov = tr.s["overall"]
    cv.put(r0 + 1, C_NAME, "☁️  Mức độ êm ái tháng này:", bold=True, font_size=9.2, align="left", indent=1,
           bg_color="#FCE7F3", font_color="#9D174D")
    cv.merge(r0 + 1, C_D0, r0 + 1, C_D31, f"={ov}", bold=True, font_size=11, align="center",
             num_format='0%"  ☁️ Pink Cloud Chill Progress"', bg_color=t.card, font_color="#DB2777")
    ws.conditional_format(rng(r0 + 1, C_D0, r0 + 1, C_D31), {
        "type": "data_bar", "bar_color": "#F472B6", "bar_solid": True,
        "min_type": "num", "min_value": 0, "max_type": "num", "max_value": 1,
    })

    cv.put(r0 + 2, C_NAME, "🌸  Lời nhắn dịu dàng hôm nay:", bold=True, font_size=9.0, align="left", indent=1,
           bg_color=t.card, font_color=t.muted)
    cv.merge(r0 + 2, C_D0, r0 + 2, C_D31,
             "Không cần hoàn hảo ngay lập tức — cứ trôi nhẹ nhàng như Capybara trên mây hồng, mỗi ngày tốt hơn 1% là tuyệt vời rồi!",
             italic=True, font_size=9.2, align="left", indent=1, bg_color="#FFF7FB", font_color=t.ink)
    cv.unlock(r0 + 2, C_D0, r0 + 2, C_D31)
    cv.grid(r0 + 1, C_NAME, r0 + 2, C_D31, t.line)
    cv.box(r0, C_NAME, r0 + 2, C_D31, t.line)

    cv.merge(r0 + 1, C_R0, r0 + 2, C_RE,
             f'="☁️ "&{tr.s["grown"]}&" ngày êm dịu"&CHAR(10)&"🔥 Chuỗi: "&{tr.s["best"]}&" ngày"',
             bold=True, font_size=9.2, align="center", text_wrap=True, bg_color="#FCE7F3", font_color="#9D174D")
    cv.box(r0, C_R0, r0 + 2, C_RE, t.line)


# 58. Fairy Party Wish: 5 Interactive Star Wishes Tracker + Fairy Magic Progress Card
def add_capybara_fairy_party_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 580):
    t, ws = cv.t, cv.ws
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23)
    for rr in range(r0 + 1, r0 + 6):
        cv.row(rr, 22)

    cv.merge(r0, C_NAME, r0, C_D31, "🧚  FAIRY PARTY STAR WISHES  •  5 ĐIỀU ƯỚC NGÔI SAO THÁNG NÀY (TỰ ĐỘNG THẮP SÁNG KHI ĐẠT MỐC!)",
             bold=True, font_size=9.1, align="left", indent=1, bg_color="#9333EA", font_color="#FFFFFF")
    cv.merge(r0, C_R0, r0, C_RE, "✨  FAIRY MAGIC", bold=True, font_size=8.8, align="center",
             bg_color="#DB2777", font_color="#FFFFFF")

    wishes = [
        ("⭐ Điều ước 1: Hoàn thành tuần đầu tiên ≥ 75% đều đặn", f'=IF({tr.s["grown"]}>=5,"✨ ĐÃ THẮP SÁNG!","☆ Đang tích sao...")'),
        ("🌟 Điều ước 2: Chạm mốc chuỗi kỷ luật 7 ngày liên tiếp", f'=IF({tr.s["best"]}>=7,"✨ ĐÃ THẮP SÁNG!","☆ Còn "&MAX(0,7-{tr.s["best"]})&" ngày")'),
        ("💖 Điều ước 3: Có ít nhất 5 ngày hoàn hảo 100% Fairy Wish", f'=IF({tr.s["perfect"]}>=5,"✨ ĐÃ THẮP SÁNG!","☆ Còn "&MAX(0,5-{tr.s["perfect"]})&" ngày")'),
        ("🎁 Điều ước 4: Tích lũy ≥ 150 lượt tick thói quen trong tháng", f'=IF({tr.s["tdone"]}>=150,"✨ ĐÃ THẮP SÁNG!","☆ Còn "&MAX(0,150-{tr.s["tdone"]})&" lượt")'),
        ("👑 Điều ước 5: Đạt hiệu suất tổng tháng ≥ 80% Tiệc Tiên!", f'=IF({tr.s["overall"]}>=0.8,"✨ ĐÃ THẮP SÁNG!","☆ Đạt "&TEXT({tr.s["overall"]},"0%")&"/80%")'),
    ]
    c_stat0 = 23
    for i, (wtxt, wf) in enumerate(wishes):
        rr = r0 + 1 + i
        bg = "#FAF5FF" if i % 2 == 0 else "#FFFFFF"
        cv.merge(rr, C_NAME, rr, c_stat0 - 1, wtxt, font_size=9.0, align="left", indent=1,
                 bg_color=bg, font_color=t.ink)
        cv.merge(rr, c_stat0, rr, C_D31, wf, bold=True, font_size=8.8, align="center",
                 bg_color="#FEF9C3" if i % 2 == 0 else "#FCE7F3", font_color="#7E22CE")
        ws.conditional_format(rng(rr, c_stat0, rr, C_D31), {
            "type": "text", "criteria": "containing", "value": "ĐÃ THẮP SÁNG",
            "format": wb.add_format({"bg_color": "#DCFCE7", "font_color": "#15803D", "bold": True}),
        })
    cv.unlock(r0 + 1, C_NAME, r0 + 5, c_stat0 - 1)
    cv.grid(r0 + 1, C_NAME, r0 + 5, C_D31, t.line)
    cv.box(r0, C_NAME, r0 + 5, C_D31, "#9333EA")

    st_col_rng = rng(r0 + 1, c_stat0, r0 + 5, c_stat0)
    cv.merge(r0 + 1, C_R0, r0 + 2, C_RE,
             f'=COUNTIF({st_col_rng},"*ĐÃ THẮP SÁNG*")&" / 5 ⭐"',
             bold=True, font_size=15, align="center", bg_color="#FAF5FF", font_color="#7E22CE",
             font_name=t.font_title)
    cv.merge(r0 + 3, C_R0, r0 + 3, C_RE, f'=COUNTIF({st_col_rng},"*ĐÃ THẮP SÁNG*")/5',
             bold=True, font_size=9.2, align="center", num_format="0%", bg_color=t.card, font_color="#DB2777")
    ws.conditional_format(rng(r0 + 3, C_R0, r0 + 3, C_RE), {
        "type": "data_bar", "bar_color": "#EAB308", "bar_solid": True,
        "min_type": "num", "min_value": 0, "max_type": "num", "max_value": 1,
    })
    cv.merge(r0 + 4, C_R0, r0 + 5, C_RE,
             f'="🧚 Ngày Tiên 100%: "&{tr.s["perfect"]}&"d"&CHAR(10)&"🔥 Best: "&{tr.s["best"]}&"d"',
             bold=True, font_size=8.6, align="center", text_wrap=True, bg_color="#FCE7F3", font_color="#9D174D")
    cv.grid(r0 + 1, C_R0, r0 + 5, C_RE, t.line)
    cv.box(r0, C_R0, r0 + 5, C_RE, t.line)


# 59. SelfCare GlowUp: Morning / Afternoon / Evening 3-Card Glow Grouping + Affirmation Journal
def add_capybara_selfcare_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 590):
    from .tracker import R_H0, CALC_DONEN_COL, CALC_GOALN_COL
    t, ws, cq = cv.t, cv.ws, tr.calc_q
    C_RE = tr.c_right_end
    rb = tr.calc_row_base
    r0 = R_EXTRA
    cv.row(r0, 23)
    for rr in range(r0 + 1, r0 + 6):
        cv.row(rr, 22)

    # 3 Live Routine Grouping Cards: Morning (habits 0..2), Afternoon (3..5), Evening (6..8)
    groups = [
        ("☀️  MORNING GLOW (SÁNG)", 0, 2, (1, 10), "#F43F5E", "#FFF1F2", "#BE123C"),
        ("🌤️  AFTERNOON CARE (CHIỀU)", 3, 5, (12, 21), "#D97706", "#FFFBEB", "#B45309"),
        ("🌙  EVENING WIND-DOWN (TỐI)", 6, 8, (23, 32), "#9333EA", "#FAF5FF", "#6B21A8"),
    ]
    for title, h_a, h_b, (c1, c2), hdr_bg, card_bg, fg in groups:
        d_rng = f"{cq}!{rng(rb + R_H0 + h_a, CALC_DONEN_COL, rb + R_H0 + h_b, CALC_DONEN_COL)}"
        g_rng = f"{cq}!{rng(rb + R_H0 + h_a, CALC_GOALN_COL, rb + R_H0 + h_b, CALC_GOALN_COL)}"
        cv.merge(r0, c1, r0, c2, title, bold=True, font_size=8.8, align="center",
                 bg_color=hdr_bg, font_color="#FFFFFF")
        cv.merge(r0 + 1, c1, r0 + 2, c2, f"=IFERROR(SUM({d_rng})/SUM({g_rng}),0)", bold=True, font_size=18,
                 align="center", num_format="0%", bg_color=t.card, font_color=fg, font_name=t.font_title)
        cv.merge(r0 + 3, c1, r0 + 3, c2, f'=SUM({d_rng})&" / "&SUM({g_rng})&" lượt hoàn thành"',
                 bold=True, font_size=8.5, align="center", bg_color=card_bg, font_color=fg)
        cv.box(r0, c1, r0 + 3, c2, hdr_bg)

    # Bottom Affirmation Strip across C_NAME..C_D31
    cv.merge(r0 + 4, C_NAME, r0 + 4, C_D31, "🪞  DAILY SELF-CARE AFFIRMATION  •  LỜI KHẲNG ĐỊNH YÊU THƯƠNG BẢN THÂN",
             bold=True, font_size=8.6, align="left", indent=1, bg_color="#FFE4E6", font_color="#BE123C")
    cv.merge(r0 + 5, C_NAME, r0 + 5, C_D31,
             "• Mình xứng đáng được chăm sóc dịu dàng từ bên trong lẫn bên ngoài — ngủ đủ, uống đủ nước và mỉm cười trước gương mỗi sáng!",
             italic=True, font_size=9.0, align="left", indent=1, bg_color=t.card, font_color=t.ink)
    cv.unlock(r0 + 5, C_NAME, r0 + 5, C_D31)
    cv.box(r0 + 4, C_NAME, r0 + 5, C_D31, t.line)

    # Right GlowUp Score Card
    cv.merge(r0, C_R0, r0, C_RE, "✨  GLOW-UP METER", bold=True, font_size=8.8, align="center",
             bg_color=t.primary, font_color="#FFFFFF")
    cv.merge(r0 + 1, C_R0, r0 + 2, C_RE,
             f'=IF({tr.s["overall"]}>=0.85,"✨ Radiant Glow!",IF({tr.s["overall"]}>=0.6,"🕶️ Stylish Self-Care","🪞 Starting Fresh"))',
             bold=True, font_size=10.5, align="center", bg_color="#FFF1F2", font_color="#BE123C",
             font_name=t.font_title)
    cv.merge(r0 + 3, C_R0, r0 + 3, C_RE, f'="✨ Ngày tỏa sáng: "&{tr.s["grown"]}&" ngày"',
             bold=True, font_size=8.6, align="center", bg_color=t.card, font_color=t.ink)
    cv.merge(r0 + 4, C_R0, r0 + 5, C_RE,
             f'="💖 Ngày 100%: "&{tr.s["perfect"]}&"d"&CHAR(10)&"🔥 Best: "&{tr.s["best"]}&"d"',
             bold=True, font_size=8.6, align="center", text_wrap=True, bg_color="#FEF3C7", font_color="#B45309")
    cv.grid(r0 + 1, C_R0, r0 + 5, C_RE, t.line)
    cv.box(r0, C_R0, r0 + 5, C_RE, t.line)


# 60. Snapshot Traveler: Polaroid Memory Highlight Diary + Travel Stamp Counter
def add_capybara_traveler_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 600):
    t, ws = cv.t, cv.ws
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23)
    for rr in range(r0 + 1, r0 + 6):
        cv.row(rr, 22)

    cv.merge(r0, C_NAME, r0, C_D31, "📸  SNAPSHOT TRAVELER MEMORY DIARY  •  NHẬT KÝ KHOẢNH KHẮC & KỶ NIỆM ĐÁNG NHỚ TRONG THÁNG",
             bold=True, font_size=9.1, align="left", indent=1, bg_color="#0D9488", font_color="#FFFFFF")
    cv.merge(r0, C_R0, r0, C_RE, "🛂  PASSPORT STAMPS", bold=True, font_size=8.6, align="center",
             bg_color="#EA580C", font_color="#FFFFFF")

    # Polaroid Diary Table Header + 4 Editable Memory Rows
    cv.put(r0 + 1, C_NAME, "📅  TUẦN / NGÀY", bold=True, font_size=8.5, align="center",
           bg_color="#CCFBF1", font_color="#115E59")
    cv.merge(r0 + 1, C_D0, r0 + 1, 14, "📍  ĐỊA ĐIỂM / TRẢI NGHIỆM MỚI", bold=True, font_size=8.5,
             align="center", bg_color="#CCFBF1", font_color="#115E59")
    cv.merge(r0 + 1, 15, r0 + 1, C_D31, "🎞️  KHOẢNH KHẮC ĐÁNG NHỚ (POLAROID CAPTION)", bold=True, font_size=8.5,
             align="center", bg_color="#FFEDD5", font_color="#9A3412")

    memories = [
        ("Tuần 1 • Khởi hành", "Quán cafe yên tĩnh góc phố mới", "Chụp 1 bức ảnh nắng sớm & viết kế hoạch tháng mới thật hào hứng!"),
        ("Tuần 2 • Khám phá", "Đi bộ công viên / cung đường mới", "Ngắm hoàng hôn cam rực rỡ & nghe podcast du lịch nhẹ nhàng."),
        ("Tuần 3 • Kết nối", "Gặp gỡ bạn thân & thưởng trà chiều", "Lưu lại tấm ảnh kỷ niệm hai chiếc mũ pastel cùng nụ cười thật tươi!"),
        ("Tuần 4 • Nhìn lại", "Góc bàn học ấm áp cuối tháng", "Tổng kết hành trình, đóng dấu hộ chiếu kỷ luật & chuẩn bị chuyến đi mới!"),
    ]
    for i, (dt_s, loc_s, cap_s) in enumerate(memories):
        rr = r0 + 2 + i
        bg = "#FFFFFF" if i % 2 == 0 else "#FAF7F2"
        cv.put(rr, C_NAME, dt_s, bold=True, font_size=8.7, align="left", indent=1, bg_color=bg, font_color="#0F766E")
        cv.merge(rr, C_D0, rr, 14, loc_s, font_size=8.8, align="left", indent=1, bg_color=bg, font_color=t.ink)
        cv.merge(rr, 15, rr, C_D31, cap_s, font_size=8.8, align="left", indent=1, bg_color=bg, font_color=t.ink)
    cv.unlock(r0 + 2, C_NAME, r0 + 5, C_D31)
    cv.grid(r0 + 1, C_NAME, r0 + 5, C_D31, t.line)
    cv.box(r0, C_NAME, r0 + 5, C_D31, "#0D9488")

    # Right Passport Stamp Counter Card
    cv.merge(r0 + 1, C_R0, r0 + 2, C_RE, f'="🛂 "&{tr.s["grown"]}&" DẤU"', bold=True, font_size=15,
             align="center", bg_color="#CCFBF1", font_color="#115E59", font_name=t.font_title)
    cv.merge(r0 + 3, C_R0, r0 + 3, C_RE, f"=MIN(1,{tr.s['grown']}/20)", bold=True, font_size=9.2,
             align="center", num_format='0%" (Mốc 20 dấu)"', bg_color=t.card, font_color="#0F766E")
    ws.conditional_format(rng(r0 + 3, C_R0, r0 + 3, C_RE), {
        "type": "data_bar", "bar_color": "#0D9488", "bar_solid": True,
        "min_type": "num", "min_value": 0, "max_type": "num", "max_value": 1,
    })
    cv.merge(r0 + 4, C_R0, r0 + 5, C_RE,
             f'="📸 Snapshot 100%: "&{tr.s["perfect"]}&" tấm"&CHAR(10)&"🔥 Best: "&{tr.s["best"]}&" ngày"',
             bold=True, font_size=8.6, align="center", text_wrap=True, bg_color="#FFEDD5", font_color="#9A3412")
    cv.grid(r0 + 1, C_R0, r0 + 5, C_RE, t.line)
    cv.box(r0, C_R0, r0 + 5, C_RE, t.line)


# =========================================================================== #
#  LOOPY PASTEL COLLECTION (#61–#70) — 10 BESPOKE SIGNATURE ADDON BLOCKS!
#  Strictly placed at R_EXTRA (row 39+) so ZERO onEdit(e) coordinates shift!
# =========================================================================== #

# 61. Loopy Red Bow Glow-Up: Daily Glow-Up Mood + Self-Love Rituals + Red Bow Rank Card
def add_loopy_red_bow_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 610):
    t, ws = cv.t, cv.ws
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23); cv.row(r0 + 1, 22); cv.row(r0 + 2, 10)
    for rr in range(r0 + 3, r0 + 7):
        cv.row(rr, 22)

    cv.put(r0, C_NAME, "🎀  RED BOW GLOW-UP ENERGY", bold=True, font_size=9.2, align="left", indent=1,
           bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_D0, r0, C_D31, "MỨC ĐỘ TỰ TIN & NĂNG LƯỢNG GLOW-UP MỖI NGÀY (THANG 1 – 5)",
             bold=True, font_size=8.6, align="center", bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_R0, r0, C_RE, "🌼  GLOW AVG", bold=True, font_size=8.8, align="center",
             bg_color=t.primary_dark, font_color=t.on_primary)

    r_gl = r0 + 1
    cv.put(r_gl, C_NAME, "✨  Điểm rạng rỡ hôm nay (1–5)", bold=True, font_size=9.0, align="left", indent=1,
           bg_color=t.soft, font_color=t.ink)
    rnd = random.Random(seed)
    for k in range(1, 32):
        c = day_col(k)
        val = "" if k > 22 else rnd.choice([4, 5, 4, 5, 3, 5, 4, 5])
        cv.put(r_gl, c, val, align="center", font_size=9.0, bold=True, bg_color=t.card,
               font_color=t.ink, num_format="0")
    gl_rng = rng(r_gl, C_D0, r_gl, C_D31)
    cv.unlock(r_gl, C_D0, r_gl, C_D31)
    cv.grid(r_gl, C_NAME, r_gl, C_D31, t.line)
    cv.box(r0, C_NAME, r_gl, C_D31, t.line)
    ws.conditional_format(gl_rng, {"type": "3_color_scale", "min_type": "num", "min_value": 1,
                                   "mid_type": "num", "mid_value": 3, "max_type": "num", "max_value": 5,
                                   "min_color": "#FFF8EA", "mid_color": "#FBCFE8", "max_color": "#D85A68"})
    cv.merge(r_gl, C_R0, r_gl, C_RE, f"=IFERROR(AVERAGE({gl_rng}),0)", bold=True, font_size=11.0,
             align="center", num_format='0.0" / 5 🎀"', bg_color=t.soft, font_color=t.primary_dark)
    cv.box(r0, C_R0, r_gl, C_RE, t.line)

    rb0 = r0 + 3
    c_mid = 16
    cv.merge(rb0, C_NAME, rb0, c_mid, "🎀  MORNING & EVENING GLOW-UP CHECKLIST", bold=True, font_size=9.0,
             align="left", indent=1, bg_color="#D85A68", font_color="#FFFFFF")
    notes_l = [
        "• Sáng: Hít thở sâu 3 nhịp, skincare gọn gàng & tự khen mình trước gương!",
        "• Trưa: Uống đủ nước, nghỉ mắt 10 phút & giữ dáng ngồi thật xinh.",
        "• Tối: Ghi 1 niềm vui nhỏ nở rộ như bông hoa vàng trên tay Loopy.",
    ]
    for i, txt in enumerate(notes_l):
        cv.merge(rb0 + 1 + i, C_NAME, rb0 + 1 + i, c_mid, txt, font_size=9.0, align="left", indent=1,
                 bg_color=t.card, font_color=t.ink)
        cv.hline(rb0 + 1 + i, C_NAME, c_mid, t.line)
    cv.unlock(rb0 + 1, C_NAME, rb0 + 3, c_mid)
    cv.box(rb0, C_NAME, rb0 + 3, c_mid, t.line)

    cv.merge(rb0, c_mid + 2, rb0, C_D31, "🌼  LOOPY SELF-LOVE NOTES", bold=True, font_size=9.0,
             align="left", indent=1, bg_color="#6E99B5", font_color="#FFFFFF")
    notes_r = [
        "• Không sao nếu có ngày lỡ quên việc!! Hít thở rồi thắt nơ đỏ làm lại!",
        "• Tập trung từng bước nhỏ — hoa vàng sẽ nở vào đúng ngày 100%.",
        "• Tự thưởng một buổi chiều thư giãn khi hoàn thành tốt mục tiêu tuần.",
    ]
    for i, txt in enumerate(notes_r):
        cv.merge(rb0 + 1 + i, c_mid + 2, rb0 + 1 + i, C_D31, txt, font_size=9.0, align="left", indent=1,
                 bg_color=t.card, font_color=t.ink)
        cv.hline(rb0 + 1 + i, c_mid + 2, C_D31, t.line)
    cv.unlock(rb0 + 1, c_mid + 2, rb0 + 3, C_D31)
    cv.box(rb0, c_mid + 2, rb0 + 3, C_D31, t.line)

    ov = tr.s["overall"]
    cv.merge(rb0, C_R0, rb0, C_RE, "👑  RED BOW RANK", bold=True, font_size=8.8, align="center",
             bg_color=t.primary_dark, font_color=t.on_primary)
    cv.merge(rb0 + 1, C_R0, rb0 + 2, C_RE,
             f'=IF({ov}>=0.9,"🎀 Hoàn Thành 100%!",IF({ov}>=0.7,"📋 Gần Kín Bảng",'
             f'IF({ov}>=0.4,"🎀 Thắt Nơ Cầm Bút","❗ Ôm Má Bình Tĩnh")))',
             bold=True, font_size=10.0, align="center", bg_color=t.soft, font_color=t.primary_dark)
    cv.merge(rb0 + 3, C_R0, rb0 + 3, C_RE,
             f'="🎀 Ngày Glow: "&{tr.s["grown"]}&"d  •  🔥 Best: "&{tr.s["best"]}&"d"',
             bold=True, font_size=8.8, align="center", bg_color=t.card, font_color=t.primary_dark)
    cv.box(rb0, C_R0, rb0 + 3, C_RE, t.line)


# 62. Loopy Taiyaki Street Snack: Weekly Taiyaki & Dango Treat Counter + Healthy Balance Note
def add_loopy_taiyaki_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 620):
    t, ws = cv.t, cv.ws
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23)
    for rr in range(r0 + 1, r0 + 6):
        cv.row(rr, 22)

    cv.merge(r0, C_NAME, r0, C_D31, "🐟  TAIYAKI & DANGO REWARD COUNTER  •  TÍCH BÁNH CÁ NÓNG THEO TUẦN (MỖI 2 NGÀY ≥75% = 1 PHẦN!)",
             bold=True, font_size=9.0, align="left", indent=1, bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_R0, r0, C_RE, "🍡  TOTAL TREATS", bold=True, font_size=8.8, align="center",
             bg_color="#6E9E82", font_color="#FFFFFF")

    stg_row = tr.stage_row
    wk_day_spans = [(1, 7), (8, 14), (15, 21), (22, 28), (29, 31)]
    col_spans = [(1, 6), (7, 13), (14, 19), (20, 26), (27, 32)]
    for w, ((d1, d2), (c1, c2)) in enumerate(zip(wk_day_spans, col_spans)):
        st_rng = f"{tr.calc_q}!{rng(stg_row, d1, stg_row, d2)}"
        cv.merge(r0 + 1, c1, r0 + 1, c2, f"🐟 WEEK {w + 1} (Ngày {d1}–{d2})", bold=True, font_size=8.6,
                 align="center", bg_color=t.week_head[w], font_color=t.week_on[w])
        cv.merge(r0 + 2, c1, r0 + 2, c2, f'=INT(COUNTIF({st_rng},">=5")/2)&" phần 🐟"', bold=True, font_size=11.0,
                 align="center", bg_color=t.card, font_color=t.primary_dark)
        cv.merge(r0 + 3, c1, r0 + 3, c2, f'=COUNTIF({st_rng},">=5")&" ngày đạt ≥75%"', italic=True,
                 font_size=8.5, align="center", bg_color=t.soft, font_color=t.ink)

    cv.merge(r0 + 4, C_NAME, r0 + 4, C_D31, "🍡  STREET SNACK SMART REWARD NOTE  •  QUY TẮC TỰ THƯỞNG BÁNH NGỌT LÀNH MẠNH",
             bold=True, font_size=8.8, align="left", indent=1, bg_color="#E6F2EC", font_color="#2D5A42")
    cv.merge(r0 + 5, C_NAME, r0 + 5, C_D31,
             "• Ăn đủ bữa chính giàu rau xanh & tự thưởng 1 chiếc bánh Taiyaki nóng hoặc xiên Dango cuối tuần khi hoàn thành KPI!",
             font_size=9.0, align="left", indent=1, bg_color=t.card, font_color=t.ink)
    cv.unlock(r0 + 5, C_NAME, r0 + 5, C_D31)
    cv.grid(r0 + 1, C_NAME, r0 + 5, C_D31, t.line)
    cv.box(r0, C_NAME, r0 + 5, C_D31, t.line)

    cv.merge(r0 + 1, C_R0, r0 + 2, C_RE, f'=INT({tr.s["grown"]}/2)&" PHẦN 🐟"', bold=True, font_size=15.0,
             align="center", bg_color=t.soft, font_color=t.primary_dark)
    cv.merge(r0 + 3, C_R0, r0 + 3, C_RE, f'="🍡 Ngày bánh nóng: "&{tr.s["grown"]}&" ngày"',
             bold=True, font_size=8.8, align="center", bg_color="#E6F2EC", font_color="#2D5A42")
    cv.merge(r0 + 4, C_R0, r0 + 5, C_RE,
             f'="✨ Ngày 100%: "&{tr.s["perfect"]}&"d"&CHAR(10)&"🔥 Best: "&{tr.s["best"]}&"d"',
             bold=True, font_size=8.8, align="center", text_wrap=True, bg_color=t.card, font_color=t.ink)
    cv.grid(r0 + 1, C_R0, r0 + 5, C_RE, t.line)
    cv.box(r0, C_R0, r0 + 5, C_RE, t.line)


# 63. Loopy Piggy Dessert Cafe: 6-Stage Dessert Menu Unlock Strip + Sweet Self-Care Menu
def add_loopy_piggy_cafe_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 630):
    t, ws = cv.t, cv.ws
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23)
    for rr in range(r0 + 1, r0 + 6):
        cv.row(rr, 22)

    cv.merge(r0, C_NAME, r0, C_D31, "🧁  PIGGY DESSERT CAFE MENU  •  THỐNG KÊ 6 MÓN TRÁNG MIỆNG MỞ KHÓA TRONG THÁNG",
             bold=True, font_size=9.2, align="left", indent=1, bg_color=t.primary, font_color="#FFFFFF")
    cv.merge(r0, C_R0, r0, C_RE, "🍒  CAFE RANK", bold=True, font_size=8.8, align="center",
             bg_color="#5EA9C7", font_color="#FFFFFF")

    stg_rng = f"{tr.calc_q}!{rng(tr.stage_row, 1, tr.stage_row, 31)}"
    tiers = [
        ("🧀 Phô Mai", "0%", "#FFFBEB", "#B45309"),
        ("🐷 Mũ Heo", "1–24%", "#FCE7F3", "#BE185D"),
        ("🍦 Kem 1 Viên", "25–49%", "#FFFDF0", "#A16207"),
        ("🍨 Kem 2 Viên", "50–74%", "#E0F2FE", "#0369A1"),
        ("🍰 Bánh Cherry", "75–99%", "#FFE4E6", "#BE123C"),
        ("👑 Tiệc Cafe!", "100% ✨", "#FCE7F3", "#9D174D"),
    ]
    spans = [(1, 5), (6, 10), (11, 15), (16, 21), (22, 26), (27, 32)]
    for i, ((c1, c2), (lbl, pct, bg, fg)) in enumerate(zip(spans, tiers)):
        cv.merge(r0 + 1, c1, r0 + 1, c2, lbl, bold=True, font_size=8.8, align="center", bg_color=bg, font_color=fg)
        cv.merge(r0 + 2, c1, r0 + 2, c2, f'=COUNTIF({stg_rng},{i + 1})&" ngày"', bold=True, font_size=10.5,
                 align="center", bg_color=t.card, font_color=fg)
        cv.merge(r0 + 3, c1, r0 + 3, c2, pct, italic=True, font_size=8.2, align="center", bg_color=t.page, font_color=t.muted)

    cv.merge(r0 + 4, C_NAME, r0 + 4, C_D31, "🍨  WEEKLY CAFE SELF-CARE TREAT  •  GÓC TỰ THƯỞNG NGỌT NGÀO CUỐI TUẦN",
             bold=True, font_size=8.8, align="left", indent=1, bg_color="#E6F5FA", font_color="#1D5E78")
    cv.merge(r0 + 5, C_NAME, r0 + 5, C_D31,
             "• Mục tiêu tuần ≥80%: Hẹn quán cafe xinh, thưởng thức 1 món bánh dâu cherry yêu thích & chụp ảnh kỷ niệm!",
             font_size=9.0, align="left", indent=1, bg_color=t.card, font_color=t.ink)
    cv.unlock(r0 + 5, C_NAME, r0 + 5, C_D31)
    cv.grid(r0 + 1, C_NAME, r0 + 5, C_D31, t.line)
    cv.box(r0, C_NAME, r0 + 5, C_D31, t.line)

    ov = tr.s["overall"]
    cv.merge(r0 + 1, C_R0, r0 + 2, C_RE,
             f'=IF({ov}>=0.9,"👑 Tiệc Cafe 5 Sao!",IF({ov}>=0.7,"🍒 Bánh Cherry",'
             f'IF({ov}>=0.45,"🍨 Kem 2 Viên","🐷 Mũ Heo Xinh")))',
             bold=True, font_size=10.0, align="center", bg_color=t.soft, font_color=t.primary_dark)
    cv.merge(r0 + 3, C_R0, r0 + 3, C_RE, f"={ov}", bold=True, font_size=9.5, align="center",
             num_format="0%", bg_color=t.card, font_color=t.ink)
    ws.conditional_format(rng(r0 + 3, C_R0, r0 + 3, C_RE), {
        "type": "data_bar", "bar_color": "#F28FB0", "bar_solid": True,
        "min_type": "num", "min_value": 0, "max_type": "num", "max_value": 1,
    })
    cv.merge(r0 + 4, C_R0, r0 + 5, C_RE,
             f'="🍒 Ngày 100%: "&{tr.s["perfect"]}&"d"&CHAR(10)&"🔥 Streak: "&{tr.s["best"]}&"d"',
             bold=True, font_size=8.8, align="center", text_wrap=True, bg_color="#E6F5FA", font_color="#1D5E78")
    cv.grid(r0 + 1, C_R0, r0 + 5, C_RE, t.line)
    cv.box(r0, C_R0, r0 + 5, C_RE, t.line)


# 64. Loopy Sauna Sheep Detox: Daily Detox Calm Meter (1–5) + 5 Weekly Sauna Donut Gauges
def add_loopy_sauna_sheep_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 640):
    t, ws = cv.t, cv.ws
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23); cv.row(r0 + 1, 22); cv.row(r0 + 2, 10)
    for rr in range(r0 + 3, r0 + 8):
        cv.row(rr, 22)

    cv.put(r0, C_NAME, "🐑  SAUNA DETOX CALM METER", bold=True, font_size=9.2, align="left", indent=1,
           bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_D0, r0, C_D31, "MỨC ĐỘ THƯ GIÃN & GIẢI TỎA CĂNG THẲNG MỖI TỐI (THANG 1 – 5)",
             bold=True, font_size=8.6, align="center", bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_R0, r0, C_RE, "♨️  DETOX AVG", bold=True, font_size=8.8, align="center",
             bg_color="#5B8EB8", font_color="#FFFFFF")

    r_clm = r0 + 1
    cv.put(r_clm, C_NAME, "♨️  Độ nhẹ lòng cuối ngày (1–5)", bold=True, font_size=9.0, align="left", indent=1,
           bg_color=t.soft, font_color=t.ink)
    rnd = random.Random(seed)
    for k in range(1, 32):
        c = day_col(k)
        val = "" if k > 22 else rnd.choice([4, 4, 5, 5, 3, 4, 5, 5])
        cv.put(r_clm, c, val, align="center", font_size=9.0, bold=True, bg_color=t.card,
               font_color=t.ink, num_format="0")
    clm_rng = rng(r_clm, C_D0, r_clm, C_D31)
    cv.unlock(r_clm, C_D0, r_clm, C_D31)
    cv.grid(r_clm, C_NAME, r_clm, C_D31, t.line)
    cv.box(r0, C_NAME, r_clm, C_D31, t.line)
    ws.conditional_format(clm_rng, {"type": "3_color_scale", "min_type": "num", "min_value": 1,
                                    "mid_type": "num", "mid_value": 3, "max_type": "num", "max_value": 5,
                                    "min_color": "#FDF6E9", "mid_color": "#DBEAFE", "max_color": "#60A5FA"})
    cv.merge(r_clm, C_R0, r_clm, C_RE, f"=IFERROR(AVERAGE({clm_rng}),0)", bold=True, font_size=11.0,
             align="center", num_format='0.0" / 5 🐑"', bg_color="#EAF3FB", font_color="#2B5C8A")
    cv.box(r0, C_R0, r_clm, C_RE, t.line)

    rd = r0 + 3
    cv.merge(rd, C_NAME, rd + 4, C_NAME, "🐑  YANGMEORI WEEKLY\nNhịp Detox 5 Tuần", bold=True,
             font_size=10.0, align="center", text_wrap=True, bg_color=t.card, font_color=t.primary_dark)
    rb = tr.calc_row_base
    spans = [(2, 7), (8, 13), (14, 19), (20, 25), (26, 32)]
    dcols = ["#C99368", "#6B9EC8", "#D87A90", "#A6734B", "#5B8EB8"]
    for w, (c1, c2) in enumerate(spans):
        hc = CALC_WK_COL0 + w
        cv.merge(rd, c1, rd, c2, f"WEEK {w + 1}", bold=True, font_size=8.6, align="center",
                 bg_color=t.week_head[w], font_color=t.week_on[w])
        cv.merge(rd + 1, c1, rd + 4, c2, f"={tr.calc_q}!{acell(rb + 2, hc)}", bold=True, font_size=12.5,
                 align="center", num_format="0%", bg_color=t.card, font_color=dcols[w])
        dch = donut(wb, f"={tr.calc_q}!{rng(rb + 2, hc, rb + 3, hc)}", [dcols[w], t.donut_rest], hole=70)
        place_chart(cv, dch, rd + 1, c1, rd + 4, c2, pad_x=10, pad_y=2)
        cv.vline(c2, rd, rd + 4, t.line, where="right")
    cv.box(rd, C_NAME, rd + 4, C_D31, t.line)

    cv.merge(rd, C_R0, rd, C_RE, "♨️  WA~ DETOX RITUAL", bold=True, font_size=8.8, align="center",
             bg_color=t.primary_dark, font_color="#FFFFFF")
    cv.merge(rd + 1, C_R0, rd + 3, C_RE,
             "• Tháo kính, tắm ấm 10p & đắp mặt nạ thư giãn.\n• Uống trà lúa mạch ấm, rời xa màn hình.\n• Thở nhẹ một cái thật đã: WA~!",
             font_size=8.8, align="left", indent=1, text_wrap=True, bg_color=t.card, font_color=t.ink)
    cv.unlock(rd + 1, C_R0, rd + 3, C_RE)
    cv.merge(rd + 4, C_R0, rd + 4, C_RE,
             f'="🐑 Ngày Detox: "&{tr.s["grown"]}&"d  •  ✨ 100%: "&{tr.s["perfect"]}&"d"',
             bold=True, font_size=8.8, align="center", bg_color=t.soft, font_color=t.primary_dark)
    cv.box(rd, C_R0, rd + 4, C_RE, t.line)


# 65. Loopy Honey Bee KPI: Daily Deep Work Hours + KPI Focus Column Chart + Team Cheer Card
def add_loopy_honey_bee_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 650):
    t, ws, q = cv.t, cv.ws, tr.q
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23); cv.row(r0 + 1, 22); cv.row(r0 + 2, 10)
    for rr in range(r0 + 3, r0 + 9):
        cv.row(rr, 20)

    cv.put(r0, C_NAME, "🐝  HONEY BEE KPI HOURS", bold=True, font_size=9.2, align="left", indent=1,
           bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_D0, r0, C_D31, "SỐ GIỜ LÀM VIỆC TẬP TRUNG ĐẠT KPI MỖI NGÀY (DEEP WORK HOURS)",
             bold=True, font_size=8.6, align="center", bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_R0, r0, C_RE, "🍯  TOTAL HOURS", bold=True, font_size=8.8, align="center",
             bg_color="#7A5C52", font_color="#FFFFFF")

    r_h = r0 + 1
    cv.put(r_h, C_NAME, "⏱️  Giờ tập trung KPI (h)", bold=True, font_size=9.0, align="left", indent=1,
           bg_color=t.soft, font_color=t.ink)
    rnd = random.Random(seed)
    for k in range(1, 32):
        c = day_col(k)
        val = "" if k > 22 else rnd.choice([3.0, 3.5, 4.0, 4.5, 5.0, 4.0, 5.5, 6.0])
        cv.put(r_h, c, val, align="center", font_size=8.8, bold=True, bg_color=t.card,
               font_color=t.ink, num_format="0.0")
    h_rng = rng(r_h, C_D0, r_h, C_D31)
    cv.unlock(r_h, C_D0, r_h, C_D31)
    cv.grid(r_h, C_NAME, r_h, C_D31, t.line)
    cv.box(r0, C_NAME, r_h, C_D31, t.line)
    ws.conditional_format(h_rng, {"type": "3_color_scale", "min_type": "num", "min_value": 0,
                                  "mid_type": "num", "mid_value": 3.5, "max_type": "num", "max_value": 6.5,
                                  "min_color": "#FFFDF2", "mid_color": "#FEF08A", "max_color": "#EAB844"})
    cv.merge(r_h, C_R0, r_h, C_RE, f"=SUM({h_rng})", bold=True, font_size=11.0, align="center",
             num_format='0.0" giờ 🍯"', bg_color=t.soft, font_color="#7A5C52")
    cv.box(r0, C_R0, r_h, C_RE, t.line)

    rc0, rc1 = r0 + 3, r0 + 8
    ch = wb.add_chart({"type": "column"})
    ch.add_series({
        "name": "KPI Hours",
        "categories": f"={q}!{rng(R_DAY, C_D0, R_DAY, C_D31)}",
        "values": f"={q}!{h_rng}",
        "fill": {"color": "#EAB844"},
        "border": {"none": True},
        "gap": 55,
    })
    ch.set_title({"name": "DAILY HONEY BEE KPI HOURS • GIỜ TẬP TRUNG HIỆU SUẤT MỖI NGÀY",
                  "name_font": {"name": t.font, "size": 9.2, "bold": True, "color": t.ink}})
    ch.set_y_axis({"min": 0, "max": 7, "major_unit": 2, "num_format": '0"h"',
                   "num_font": axis_font(t), "line": {"none": True},
                   "major_gridlines": {"visible": True, "line": {"color": t.line, "dash_type": "dash"}}})
    ch.set_x_axis({"num_font": axis_font(t, 8.0), "line": {"color": t.line}})
    ch.set_legend({"none": True})
    ch.set_chartarea({"border": {"color": t.line, "width": 0.75}, "fill": {"color": t.card}})
    place_chart(cv, ch, rc0, C_NAME, rc1, C_D31)

    cv.merge(rc0, C_R0, rc0, C_RE, "🧸  PASTEL BEAR CHEER", bold=True, font_size=8.8, align="center",
             bg_color="#7A5C52", font_color="#FFFFFF")
    cv.merge(rc0 + 1, C_R0, rc0 + 3, C_RE,
             "• Chia việc thành 3 block Pomodoro 50 phút.\n• Giải quyết đầu việc khó nhất trước 11h.\n• Cả hội bạn gấu pastel đang cổ vũ bạn!",
             font_size=8.8, align="left", indent=1, text_wrap=True, bg_color=t.card, font_color=t.ink)
    cv.unlock(rc0 + 1, C_R0, rc0 + 3, C_RE)
    cv.merge(rc0 + 4, C_R0, rc1, C_RE,
             f'="🍯 TB: "&TEXT(IFERROR(AVERAGE({h_rng}),0),"0.0")&" h/ngày"&CHAR(10)&"🐝 Ngày KPI: "&{tr.s["grown"]}&"d"',
             bold=True, font_size=8.8, align="center", text_wrap=True, bg_color=t.soft, font_color="#7A5C52")
    cv.box(rc0, C_R0, rc1, C_RE, t.line)


# 66. Loopy Poolside Duck Chill: Daily Hydration Glasses + 5-Week Aqua Chill Progress Bars
def add_loopy_poolside_duck_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 660):
    t, ws = cv.t, cv.ws
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23); cv.row(r0 + 1, 22); cv.row(r0 + 2, 10)
    for rr in range(r0 + 3, r0 + 7):
        cv.row(rr, 22)

    cv.put(r0, C_NAME, "💧  POOLSIDE HYDRATION LOG", bold=True, font_size=9.2, align="left", indent=1,
           bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_D0, r0, C_D31, "SỐ LY NƯỚC MÁT UỐNG MỖI NGÀY CÙNG LOOPY PHAO VỊT (MỤC TIÊU 8 LY)",
             bold=True, font_size=8.6, align="center", bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_R0, r0, C_RE, "💧  AVG CUPS", bold=True, font_size=8.8, align="center",
             bg_color="#D99B16", font_color="#FFFFFF")

    r_w = r0 + 1
    cv.put(r_w, C_NAME, "🥤  Số ly nước lọc (ly/ngày)", bold=True, font_size=9.0, align="left", indent=1,
           bg_color=t.soft, font_color=t.ink)
    rnd = random.Random(seed)
    for k in range(1, 32):
        c = day_col(k)
        val = "" if k > 22 else rnd.choice([6, 7, 8, 8, 9, 7, 8, 8])
        cv.put(r_w, c, val, align="center", font_size=9.0, bold=True, bg_color=t.card,
               font_color=t.ink, num_format="0")
    w_rng = rng(r_w, C_D0, r_w, C_D31)
    cv.unlock(r_w, C_D0, r_w, C_D31)
    cv.grid(r_w, C_NAME, r_w, C_D31, t.line)
    cv.box(r0, C_NAME, r_w, C_D31, t.line)
    ws.conditional_format(w_rng, {"type": "3_color_scale", "min_type": "num", "min_value": 4,
                                  "mid_type": "num", "mid_value": 7, "max_type": "num", "max_value": 10,
                                  "min_color": "#F2FBFF", "mid_color": "#BAE6FD", "max_color": "#38BDF8"})
    cv.merge(r_w, C_R0, r_w, C_RE, f"=IFERROR(AVERAGE({w_rng}),0)", bold=True, font_size=11.0,
             align="center", num_format='0.0" ly 💧"', bg_color="#FEF9C3", font_color="#854D0E")
    cv.box(r0, C_R0, r_w, C_RE, t.line)

    rb0 = r0 + 3
    rb = tr.calc_row_base
    cv.merge(rb0, C_NAME, rb0, C_D31, "🐥  POOLSIDE WEEKLY CHILL BARS  •  THANH TIẾN ĐỘ HỒ XANH 5 TUẦN",
             bold=True, font_size=9.0, align="left", indent=1, bg_color="#2A8EB5", font_color="#FFFFFF")
    spans = [(1, 6), (7, 13), (14, 19), (20, 26), (27, 32)]
    p_cols = ["#6EC6E6", "#F7CF52", "#38BDF8", "#F59E0B", "#0EA5E9"]
    p_bgs = ["#E0F2FE", "#FEF9C3", "#E0F2FE", "#FEF3C7", "#E0F2FE"]
    p_fgs = ["#075985", "#854D0E", "#0369A1", "#92400E", "#0C4A6E"]
    for w, ((c1, c2), bc, bg, fg) in enumerate(zip(spans, p_cols, p_bgs, p_fgs)):
        hc = CALC_WK_COL0 + w
        pct_ref = f"{tr.calc_q}!{acell(rb + 2, hc)}"
        cv.merge(rb0 + 1, c1, rb0 + 1, c2, f"🐥 WEEK {w + 1}", bold=True, font_size=8.6, align="center",
                 bg_color=bg, font_color=fg)
        cv.merge(rb0 + 2, c1, rb0 + 2, c2, f"={pct_ref}", bold=True, font_size=11.0, align="center",
                 num_format="0%", bg_color=t.card, font_color=fg)
        ws.conditional_format(rng(rb0 + 2, c1, rb0 + 2, c2), {
            "type": "data_bar", "bar_color": bc, "bar_solid": True,
            "min_type": "num", "min_value": 0, "max_type": "num", "max_value": 1,
        })
        cv.merge(rb0 + 3, c1, rb0 + 3, c2,
                 f'=IF({pct_ref}>=0.8,"🌊 Nổi Chill Hết Nấc!",IF({pct_ref}>=0.5,"🛟 Phao Sọc Xinh","🐥 Ôm Phao Vịt"))',
                 italic=True, font_size=8.3, align="center", bg_color=t.page, font_color=fg)
    cv.grid(rb0 + 1, C_NAME, rb0 + 3, C_D31, t.line)
    cv.box(rb0, C_NAME, rb0 + 3, C_D31, t.line)

    cv.merge(rb0, C_R0, rb0, C_RE, "☀️  SUMMER CHILL NOTE", bold=True, font_size=8.8, align="center",
             bg_color="#F59E0B", font_color="#FFFFFF")
    cv.merge(rb0 + 1, C_R0, rb0 + 2, C_RE,
             "• Giữ cơ thể mát mẻ, giãn cơ nhẹ & nghỉ giải lao đầy nắng!",
             font_size=8.8, align="left", indent=1, text_wrap=True, bg_color=t.card, font_color=t.ink)
    cv.unlock(rb0 + 1, C_R0, rb0 + 2, C_RE)
    cv.merge(rb0 + 3, C_R0, rb0 + 3, C_RE,
             f'="🐥 Pool Days: "&{tr.s["grown"]}&"d  •  🔥 Best: "&{tr.s["best"]}&"d"',
             bold=True, font_size=8.8, align="center", bg_color=t.soft, font_color=t.primary_dark)
    cv.box(rb0, C_R0, rb0 + 3, C_RE, t.line)


# 67. Loopy Fluffy Commuter Diary: 4-Week Commuter Workday Diary & On-Time Clock-Out Counter
def add_loopy_fluffy_commuter_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 670):
    t, ws = cv.t, cv.ws
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23)
    for rr in range(r0 + 1, r0 + 6):
        cv.row(rr, 22)

    cv.merge(r0, C_NAME, r0, C_D31, "🎒  FLUFFY COMMUTER WORKDAY DIARY  •  NHẬT KÝ ĐI LÀM & GHI CHÚ TAN LÀM ĐÚNG GIỜ",
             bold=True, font_size=9.1, align="left", indent=1, bg_color=t.primary, font_color="#FFFFFF")
    cv.merge(r0, C_R0, r0, C_RE, "🌟  ON-TIME BADGE", bold=True, font_size=8.8, align="center",
             bg_color="#C98A2C", font_color="#FFFFFF")

    cv.put(r0 + 1, C_NAME, "📅  TUẦN LÀM VIỆC", bold=True, font_size=8.8, align="center",
           bg_color="#FDE7A9", font_color="#5C4033")
    cv.merge(r0 + 1, C_D0, r0 + 1, 14, "💼  TRỌNG TÂM TUẦN (TOP PRIORITY)", bold=True, font_size=8.8,
             align="center", bg_color="#FDE7A9", font_color="#5C4033")
    cv.merge(r0 + 1, 15, r0 + 1, C_D31, "⭐  NIỀM VUI TAN LÀM / GHI CHÚ NHANH", bold=True, font_size=8.8,
             align="center", bg_color="#F3EAE4", font_color="#5C4033")

    rows = [
        ("Tuần 1 • Khởi động", "Hoàn thiện kế hoạch tháng & dọn gọn hộp thư", "Đội mũ bông đi làm đúng giờ, ghé mua 1 ly cafe ấm!"),
        ("Tuần 2 • Tăng tốc", "Xử lý xong báo cáo / dự án cốt lõi đúng hạn", "Tan làm 17h30 đi dạo ngắm hoàng hôn cực chill."),
        ("Tuần 3 • Giữ nhịp", "Duy trì Deep Work buổi sáng, không mang việc về nhà", "Tự nấu bữa tối ấm cúng & nghe podcast yêu thích."),
        ("Tuần 4 • Tổng kết", "Rà soát KPI, đóng gói gọn gàng & chuẩn bị tháng mới", "Thưởng cho mình 1 buổi cuối tuần ngủ nướng thả ga!"),
    ]
    for i, (wk_s, pri_s, joy_s) in enumerate(rows):
        rr = r0 + 2 + i
        bg = "#FFFFFF" if i % 2 == 0 else "#FFFBF2"
        cv.put(rr, C_NAME, wk_s, bold=True, font_size=8.8, align="left", indent=1, bg_color=bg, font_color="#5C4033")
        cv.merge(rr, C_D0, rr, 14, pri_s, font_size=8.8, align="left", indent=1, bg_color=bg, font_color=t.ink)
        cv.merge(rr, 15, rr, C_D31, joy_s, font_size=8.8, align="left", indent=1, bg_color=bg, font_color=t.ink)
    cv.unlock(r0 + 2, C_NAME, r0 + 5, C_D31)
    cv.grid(r0 + 1, C_NAME, r0 + 5, C_D31, t.line)
    cv.box(r0, C_NAME, r0 + 5, C_D31, t.primary)

    cv.merge(r0 + 1, C_R0, r0 + 2, C_RE, f'="🌟 "&{tr.s["grown"]}&" NGÀY"', bold=True, font_size=15.0,
             align="center", bg_color="#FEF3C7", font_color="#8B5A12")
    cv.merge(r0 + 3, C_R0, r0 + 3, C_RE, f"=MIN(1,{tr.s['grown']}/22)", bold=True, font_size=9.2,
             align="center", num_format='0%" (Mốc 22 ngày)"', bg_color=t.card, font_color=t.primary_dark)
    ws.conditional_format(rng(r0 + 3, C_R0, r0 + 3, C_RE), {
        "type": "data_bar", "bar_color": "#D99B38", "bar_solid": True,
        "min_type": "num", "min_value": 0, "max_type": "num", "max_value": 1,
    })
    cv.merge(r0 + 4, C_R0, r0 + 5, C_RE,
             f'="💼 Ngày 100%: "&{tr.s["perfect"]}&"d"&CHAR(10)&"🔥 Best: "&{tr.s["best"]}&"d"',
             bold=True, font_size=8.8, align="center", text_wrap=True, bg_color=t.soft, font_color=t.ink)
    cv.grid(r0 + 1, C_R0, r0 + 5, C_RE, t.line)
    cv.box(r0, C_R0, r0 + 5, C_RE, t.line)


# 68. Loopy Panda Zen Study: Daily Study Minutes + Pages Read + Zen Study Milestone Card
def add_loopy_panda_study_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 680):
    t, ws = cv.t, cv.ws
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23); cv.row(r0 + 1, 22); cv.row(r0 + 2, 22); cv.row(r0 + 3, 10)
    for rr in range(r0 + 4, r0 + 7):
        cv.row(rr, 22)

    cv.put(r0, C_NAME, "🐼  PANDA ZEN STUDY LOG", bold=True, font_size=9.2, align="left", indent=1,
           bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_D0, r0, C_D31, "PHÚT TỰ HỌC SÂU (MINS)  •  SỐ TRANG SÁCH / TÀI LIỆU ĐỌC MỖI NGÀY (PAGES)",
             bold=True, font_size=8.6, align="center", bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_R0, r0, C_RE, "🎋  STUDY TOTALS", bold=True, font_size=8.8, align="center",
             bg_color="#3E7A5B", font_color="#FFFFFF")

    r_m, r_p = r0 + 1, r0 + 2
    cv.put(r_m, C_NAME, "⏱️  Phút tập trung học (mins)", bold=True, font_size=9.0, align="left", indent=1,
           bg_color=t.soft, font_color=t.ink)
    cv.put(r_p, C_NAME, "📖  Số trang đọc mỗi ngày", bold=True, font_size=9.0, align="left", indent=1,
           bg_color=t.card, font_color=t.ink)
    rnd = random.Random(seed)
    for k in range(1, 32):
        c = day_col(k)
        if k > 22:
            cv.put(r_m, c, "", align="center", font_size=8.8, bg_color=t.card, num_format="0")
            cv.put(r_p, c, "", align="center", font_size=8.8, bg_color=t.card, num_format="0")
        else:
            cv.put(r_m, c, rnd.choice([45, 60, 75, 90, 60, 90, 120, 75]),
                   align="center", font_size=8.8, bold=True, bg_color=t.card, font_color=t.ink, num_format="0")
            cv.put(r_p, c, rnd.choice([10, 15, 20, 25, 18, 22, 30, 16]),
                   align="center", font_size=8.8, bg_color=t.card, font_color=t.ink, num_format="0")

    m_rng = rng(r_m, C_D0, r_m, C_D31)
    p_rng = rng(r_p, C_D0, r_p, C_D31)
    cv.unlock(r_m, C_D0, r_p, C_D31)
    cv.grid(r_m, C_NAME, r_p, C_D31, t.line)
    cv.box(r0, C_NAME, r_p, C_D31, t.line)
    ws.conditional_format(m_rng, {"type": "3_color_scale", "min_type": "num", "min_value": 0,
                                  "mid_type": "num", "mid_value": 60, "max_type": "num", "max_value": 120,
                                  "min_color": "#F7FBF9", "mid_color": "#B8DEC9", "max_color": "#3E7A5B"})
    ws.conditional_format(p_rng, {"type": "3_color_scale", "min_type": "num", "min_value": 0,
                                  "mid_type": "num", "mid_value": 15, "max_type": "num", "max_value": 30,
                                  "min_color": "#F7FBF9", "mid_color": "#CBD5E1", "max_color": "#4E545C"})

    cv.merge(r_m, C_R0, r_m, C_R0 + 2, "Tổng giờ học:", font_size=8.8, align="left", indent=1, bg_color=t.card, font_color=t.muted)
    cv.merge(r_m, C_R0 + 3, r_m, C_RE, f"=SUM({m_rng})/60", bold=True, font_size=10.5, align="center",
             num_format='0.0" h"', bg_color="#E6F5EC", font_color="#2D5A42")
    cv.merge(r_p, C_R0, r_p, C_R0 + 2, "Tổng trang:", font_size=8.8, align="left", indent=1, bg_color=t.card, font_color=t.muted)
    cv.merge(r_p, C_R0 + 3, r_p, C_RE, f"=SUM({p_rng})", bold=True, font_size=10.5, align="center",
             num_format='#,##0" tr"', bg_color=t.soft, font_color=t.ink)
    cv.hline(r_m, C_R0, C_RE, t.line)
    cv.box(r0, C_R0, r_p, C_RE, t.line)

    rb0 = r0 + 4
    cv.merge(rb0, C_NAME, rb0, C_D31, "🎋  PANDA ZEN FOCUS NOTES  •  MỤC TIÊU ÔN TẬP & GHI CHÚ TRI THỨC THÁNG NÀY",
             bold=True, font_size=9.0, align="left", indent=1, bg_color="#3E7A5B", font_color="#FFFFFF")
    cv.merge(rb0 + 1, C_NAME, rb0 + 1, C_D31,
             "• Môn / Kỹ năng trọng tâm: Ôn ngoại ngữ 30p sáng + tóm tắt 3 ý chính mỗi chương sách đang đọc.",
             font_size=9.0, align="left", indent=1, bg_color=t.card, font_color=t.ink)
    cv.merge(rb0 + 2, C_NAME, rb0 + 2, C_D31,
             "• Không gian Zen: Tắt thông báo điện thoại, đặt 1 ly trà xanh mát & bật nhạc không lời nhẹ nhàng.",
             font_size=9.0, align="left", indent=1, bg_color=t.card, font_color=t.ink)
    cv.unlock(rb0 + 1, C_NAME, rb0 + 2, C_D31)
    cv.grid(rb0 + 1, C_NAME, rb0 + 2, C_D31, t.line)
    cv.box(rb0, C_NAME, rb0 + 2, C_D31, t.line)

    cv.merge(rb0, C_R0, rb0, C_RE, "🐼  ZEN SCHOLAR RANK", bold=True, font_size=8.8, align="center",
             bg_color=t.primary, font_color="#FFFFFF")
    cv.merge(rb0 + 1, C_R0, rb0 + 2, C_RE,
             f'="🎋 Ngày Zen: "&{tr.s["grown"]}&" ngày"&CHAR(10)&"🔥 Best Streak: "&{tr.s["best"]}&"d"',
             bold=True, font_size=9.0, align="center", text_wrap=True, bg_color="#E6F5EC", font_color="#2D5A42")
    cv.box(rb0, C_R0, rb0 + 2, C_RE, t.line)


# 69. Loopy Ruffle Sleep Routine: Daily Sleep Hours + 3-Part Bedtime Routine Cards
def add_loopy_ruffle_sleep_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 690):
    t, ws = cv.t, cv.ws
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23); cv.row(r0 + 1, 22); cv.row(r0 + 2, 10)
    for rr in range(r0 + 3, r0 + 7):
        cv.row(rr, 22)

    cv.put(r0, C_NAME, "🛏️  RUFFLE SLEEP HOURS LOG", bold=True, font_size=9.2, align="left", indent=1,
           bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_D0, r0, C_D31, "SỐ GIỜ NGỦ MỖI ĐÊM CÙNG LOOPY GỐI BÈO (MỤC TIÊU 7.5 – 8.5 GIỜ)",
             bold=True, font_size=8.6, align="center", bg_color=t.primary, font_color=t.on_primary)
    cv.merge(r0, C_R0, r0, C_RE, "💤  AVG SLEEP", bold=True, font_size=8.8, align="center",
             bg_color="#7C6BA8", font_color="#FFFFFF")

    r_sl = r0 + 1
    cv.put(r_sl, C_NAME, "🌙  Giờ ngủ chất lượng (giờ)", bold=True, font_size=9.0, align="left", indent=1,
           bg_color=t.soft, font_color=t.ink)
    rnd = random.Random(seed)
    for k in range(1, 32):
        c = day_col(k)
        val = "" if k > 22 else rnd.choice([7.0, 7.5, 8.0, 8.0, 8.5, 7.5, 8.0, 7.5])
        cv.put(r_sl, c, val, align="center", font_size=8.8, bold=True, bg_color=t.card,
               font_color=t.ink, num_format="0.0")
    sl_rng = rng(r_sl, C_D0, r_sl, C_D31)
    cv.unlock(r_sl, C_D0, r_sl, C_D31)
    cv.grid(r_sl, C_NAME, r_sl, C_D31, t.line)
    cv.box(r0, C_NAME, r_sl, C_D31, t.line)
    ws.conditional_format(sl_rng, {"type": "3_color_scale", "min_type": "num", "min_value": 5.5,
                                   "mid_type": "num", "mid_value": 7.5, "max_type": "num", "max_value": 9.0,
                                   "min_color": "#FDFBE9", "mid_color": "#EAE4F7", "max_color": "#E892AC"})
    cv.merge(r_sl, C_R0, r_sl, C_RE, f"=IFERROR(AVERAGE({sl_rng}),0)", bold=True, font_size=11.0,
             align="center", num_format='0.0" giờ 💤"', bg_color="#EAE4F7", font_color="#5B468A")
    cv.box(r0, C_R0, r_sl, C_RE, t.line)

    # 3 Cozy Bedtime Wind-Down Cards
    rb0 = r0 + 3
    cards = [
        ("🎀  21:30 • KÉO RÈM NƠ HỒNG", (1, 10), "#E892AC", "#FFF2F6",
         "• Cất điện thoại ra xa giường.\n• Bật đèn vàng dịu & xịt thơm gối."),
        ("🫧  22:00 • THƯ GIÃN TỰA GỐI", (12, 21), "#8B74B8", "#F4F0FC",
         "• Dưỡng da tối & giãn cơ nhẹ 5p.\n• Đọc 5 trang sách nhẹ nhàng."),
        ("💤  22:30 • GIẤC MƠ HOA ZZZ", (23, 32), "#C96A88", "#FFF5F8",
         "• Hít thở sâu 4-7-8 thả lỏng vai.\n• Ngủ đủ 8 tiếng đón sáng tươi tắn!"),
    ]
    for title, (c1, c2), h_bg, c_bg, body in cards:
        cv.merge(rb0, c1, rb0, c2, title, bold=True, font_size=8.8, align="center",
                 bg_color=h_bg, font_color="#FFFFFF")
        cv.merge(rb0 + 1, c1, rb0 + 3, c2, body, font_size=8.8, align="left", indent=1,
                 text_wrap=True, bg_color=c_bg, font_color=t.ink)
        cv.unlock(rb0 + 1, c1, rb0 + 3, c2)
        cv.box(rb0, c1, rb0 + 3, c2, h_bg)

    cv.merge(rb0, C_R0, rb0, C_RE, "🌙  SLEEP SCORE", bold=True, font_size=8.8, align="center",
             bg_color=t.primary_dark, font_color="#FFFFFF")
    cv.merge(rb0 + 1, C_R0, rb0 + 2, C_RE,
             f'=IF(IFERROR(AVERAGE({sl_rng}),0)>=7.8,"💤 Giấc Mơ Hoa!",IF(IFERROR(AVERAGE({sl_rng}),0)>=7.0,"🫧 Ngủ Đủ Giấc","🎀 Đi Ngủ Sớm Nhé"))',
             bold=True, font_size=10.0, align="center", bg_color=t.soft, font_color=t.primary_dark)
    cv.merge(rb0 + 3, C_R0, rb0 + 3, C_RE,
             f'="🌙 Đêm Ngon: "&{tr.s["grown"]}&"d  •  🔥 Best: "&{tr.s["best"]}&"d"',
             bold=True, font_size=8.6, align="center", bg_color=t.card, font_color=t.ink)
    cv.box(rb0, C_R0, rb0 + 3, C_RE, t.line)


# 70. Loopy Hair Roller GRWM: Daily GRWM Glow Score + 3-Step Hair & Skincare Routine Cards
def add_loopy_hair_roller_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 700):
    t, ws = cv.t, cv.ws
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23); cv.row(r0 + 1, 22); cv.row(r0 + 2, 10)
    for rr in range(r0 + 3, r0 + 7):
        cv.row(rr, 22)

    cv.put(r0, C_NAME, "💇‍♀️  HAIR ROLLER GRWM GLOW", bold=True, font_size=9.2, align="left", indent=1,
           bg_color=t.primary, font_color="#FFFFFF")
    cv.merge(r0, C_D0, r0, C_D31, "CHỈ SỐ CHỈN CHU & RẠNG RỠ GRWM MỖI NGÀY CÙNG LOOPY LÔ CUỐN MÁI (1 – 5)",
             bold=True, font_size=9.0, align="center", bg_color=t.primary, font_color="#FFFFFF")
    cv.merge(r0, C_R0, r0, C_RE, "🪞  GRWM AVG", bold=True, font_size=9.0, align="center",
             bg_color="#4A3B42", font_color="#FFFFFF")

    r_gr = r0 + 1
    cv.put(r_gr, C_NAME, "✨  Độ chỉn chu sáng (1–5)", bold=True, font_size=9.0, align="left", indent=1,
           bg_color=t.soft, font_color=t.ink)
    rnd = random.Random(seed)
    for k in range(1, 32):
        c = day_col(k)
        val = "" if k > 22 else rnd.choice([4, 5, 4, 5, 3, 5, 4, 5])
        cv.put(r_gr, c, val, align="center", font_size=9.0, bold=True, bg_color=t.card,
               font_color=t.ink, num_format="0")
    gr_rng = rng(r_gr, C_D0, r_gr, C_D31)
    cv.unlock(r_gr, C_D0, r_gr, C_D31)
    cv.grid(r_gr, C_NAME, r_gr, C_D31, t.line)
    cv.box(r0, C_NAME, r_gr, C_D31, t.line)
    ws.conditional_format(gr_rng, {"type": "3_color_scale", "min_type": "num", "min_value": 1,
                                   "mid_type": "num", "mid_value": 3, "max_type": "num", "max_value": 5,
                                   "min_color": "#FFF7FA", "mid_color": "#F7B4C9", "max_color": "#D96B8D"})
    cv.merge(r_gr, C_R0, r_gr, C_RE, f"=IFERROR(AVERAGE({gr_rng}),0)", bold=True, font_size=11.0,
             align="center", num_format='0.0" / 5 🪞"', bg_color="#FDEAF1", font_color="#A84264")
    cv.box(r0, C_R0, r_gr, C_RE, t.line)

    rb0 = r0 + 3
    cards = [
        ("💇‍♀️  BƯỚC 1 • CUỐN LÔ & TRÀ ẤM", (1, 10), "#D96B8D", "#FFF5F8",
         "• Cuốn lô mái bồng, rửa mặt sạch.\n• Nhấp 1 ngụm trà ấm tỉnh hồn ngay!"),
        ("🌸  BƯỚC 2 • SKINCARE & MÁ HỒNG", (12, 21), "#4A3B42", "#F7F2F4",
         "• Dưỡng ẩm, chống nắng đủ lượng.\n• Chấm nhẹ má hồng & dưỡng môi xinh."),
        ("🪞  BƯỚC 3 • THÁO LÔ TỎA SÁNG", (23, 32), "#C45175", "#FFF5F9",
         "• Tháo lô mái bồng, kẹp nơ hồng.\n• Soi gương mỉm cười tự tin ra cửa!"),
    ]
    for title, (c1, c2), h_bg, c_bg, body in cards:
        cv.merge(rb0, c1, rb0, c2, title, bold=True, font_size=9.0, align="center",
                 bg_color=h_bg, font_color="#FFFFFF")
        cv.merge(rb0 + 1, c1, rb0 + 3, c2, body, font_size=9.0, align="left", indent=1,
                 text_wrap=True, bg_color=c_bg, font_color=t.ink)
        cv.unlock(rb0 + 1, c1, rb0 + 3, c2)
        cv.box(rb0, c1, rb0 + 3, c2, h_bg)

    ov = tr.s["overall"]
    cv.merge(rb0, C_R0, rb0, C_RE, "👑  GRWM RANK", bold=True, font_size=9.0, align="center",
             bg_color=t.primary_dark, font_color="#FFFFFF")
    cv.merge(rb0 + 1, C_R0, rb0 + 2, C_RE,
             f'=IF({ov}>=0.9,"✨ Xinh Lung Linh!",IF({ov}>=0.7,"🪞 Mái Bồng Soi Gương",'
             f'IF({ov}>=0.45,"🌸 Chấm Má Hồng","💇‍♀️ Cuốn Lô Bắt Đầu")))',
             bold=True, font_size=9.8, align="center", bg_color=t.soft, font_color=t.primary_dark)
    cv.merge(rb0 + 3, C_R0, rb0 + 3, C_RE,
             f'="🪞 Ngày GRWM: "&{tr.s["grown"]}&"d • 🔥 "&{tr.s["best"]}&"d"',
             bold=True, font_size=9.0, align="center", bg_color=t.card, font_color=t.ink)
    cv.box(rb0, C_R0, rb0 + 3, C_RE, t.line)


# =========================================================================== #
#  LOTSO STRAWBERRY BEAR COLLECTION (#71–#80) — 10 BESPOKE ADDON BLOCKS!
#  Strictly placed at R_EXTRA (row 39+) so ZERO onEdit(e) coordinates shift!
# =========================================================================== #

# 71. Lotso Strawberry Harvest: Live Strawberry Basket Counter + 3-Line Sweet Harvest Note
def add_lotso_strawberry_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 710):
    t, ws = cv.t, cv.ws
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23)
    for rr in range(r0 + 1, r0 + 6):
        cv.row(rr, 22)

    c_mid = 13
    cv.merge(r0, C_NAME, r0, c_mid, "🍓  STRAWBERRY HARVEST BASKET  •  GIỎ DÂU TÂY THU HOẠCH THÁNG",
             bold=True, font_size=9.1, align="left", indent=1, bg_color=t.primary, font_color="#FFFFFF")
    cv.merge(r0 + 1, C_NAME, r0 + 3, 5,
             f'="🍓 "&{tr.s["tdone"]}&CHAR(10)&"QUẢ DÂU ĐÃ HÁI"',
             bold=True, font_size=13.5, align="center", text_wrap=True, bg_color=t.soft, font_color=t.primary_dark)
    cv.merge(r0 + 1, 6, r0 + 1, c_mid, f'="🌿 Ngày hái dâu chín (≥75%):  "&{tr.s["grown"]}&" ngày"',
             bold=True, font_size=9.1, align="left", indent=1, bg_color=t.card, font_color="#2D6A42")
    cv.merge(r0 + 2, 6, r0 + 2, c_mid, f'="😍 Ngày mắt tim 100%:  "&{tr.s["perfect"]}&" ngày rực rỡ"',
             bold=True, font_size=9.1, align="left", indent=1, bg_color="#FFF5F8", font_color=t.primary_dark)
    cv.merge(r0 + 3, 6, r0 + 3, c_mid, f'="🎯 Tỷ lệ chín mọng tháng:  "&TEXT({tr.s["overall"]},"0%")',
             bold=True, font_size=9.1, align="left", indent=1, bg_color=t.card, font_color=t.ink)
    cv.merge(r0 + 4, C_NAME, r0 + 5, c_mid,
             f'=IF({tr.s["tdone"]}>=180,"🍓 Vụ mùa dâu chín mọng tuyệt đỉnh!",IF({tr.s["tdone"]}>=90,"🌿 Vườn dâu đang chín đỏ rất đều!","🐾 Hết quay lưng lì lợm, bắt đầu hái dâu thôi!"))',
             bold=True, font_size=9.1, align="center", bg_color="#EBF7EC", font_color="#2D6A42")
    cv.grid(r0 + 1, C_NAME, r0 + 5, c_mid, t.line)
    cv.box(r0, C_NAME, r0 + 5, c_mid, t.primary)

    c_g0 = c_mid + 2
    cv.merge(r0, c_g0, r0, C_D31, "💌  LOTSO SWEET HARVEST NOTES  •  GHI CHÚ THÀNH QUẢ NGỌT NGÀO",
             bold=True, font_size=9.1, align="left", indent=1, bg_color="#5B9E65", font_color="#FFFFFF")
    notes = [
        "1. Khi thấy lười như Lotso quay lưng (0%): làm 1 thói quen nhỏ nhất trong 2 phút!",
        "2. Mỗi dấu tick là một quả dâu chín đỏ — tích đều cuối tuần sẽ có giỏ dâu đầy ắp.",
        "3. Tự thưởng sinh tố dâu / trà trái cây mát lạnh khi tuần đạt ≥ 80%!",
        "",
        "",
    ]
    for i, g in enumerate(notes):
        cv.merge(r0 + 1 + i, c_g0, r0 + 1 + i, C_D31, g, font_size=9.0, align="left", indent=1,
                 bg_color=t.card, font_color=t.ink)
        cv.hline(r0 + 1 + i, c_g0, C_D31, t.line)
    cv.unlock(r0 + 1, c_g0, r0 + 5, C_D31)
    cv.box(r0, c_g0, r0 + 5, C_D31, "#5B9E65")

    cv.merge(r0, C_R0, r0, C_RE, "🍓  HARVEST GOAL", bold=True, font_size=9.0, align="center",
             bg_color=t.primary_dark, font_color="#FFFFFF")
    cv.merge(r0 + 1, C_R0, r0 + 2, C_RE, f"=MIN(1,{tr.s['tdone']}/200)", bold=True, font_size=14.0,
             align="center", num_format="0%", bg_color=t.soft, font_color=t.primary_dark)
    ws.conditional_format(rng(r0 + 1, C_R0, r0 + 2, C_RE), {
        "type": "data_bar", "bar_color": "#E56B8C", "bar_solid": True,
        "min_type": "num", "min_value": 0, "max_type": "num", "max_value": 1,
    })
    cv.merge(r0 + 3, C_R0, r0 + 3, C_RE, "Mốc vụ mùa: 200 dâu", italic=True, font_size=9.0,
             align="center", bg_color=t.card, font_color=t.muted)
    cv.merge(r0 + 4, C_R0, r0 + 5, C_RE,
             f'="🔥 Chuỗi Hái Dâu:"&CHAR(10)&{tr.s["best"]}&" ngày liên tiếp"',
             bold=True, font_size=9.0, align="center", text_wrap=True, bg_color="#EBF7EC", font_color="#2D6A42")
    cv.grid(r0 + 1, C_R0, r0 + 5, C_RE, t.line)
    cv.box(r0, C_R0, r0 + 5, C_RE, t.line)


# 72. Lotso Strawberry Milk Cafe: Daily Hydration & Milk Treat Log + Cafe Menu Reward Bar
def add_lotso_milk_cafe_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 720):
    t, ws = cv.t, cv.ws
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23); cv.row(r0 + 1, 22); cv.row(r0 + 2, 10)
    for rr in range(r0 + 3, r0 + 6):
        cv.row(rr, 22)

    cv.put(r0, C_NAME, "🥛  STRAWBERRY MILK & WATER", bold=True, font_size=9.2, align="left", indent=1,
           bg_color=t.primary, font_color="#FFFFFF")
    cv.merge(r0, C_D0, r0, C_D31, "SỐ LY NƯỚC LỌC & SỮA DÂU TƯƠI BỔ SUNG MỖI NGÀY (MỤC TIÊU 8 LY)",
             bold=True, font_size=9.0, align="center", bg_color=t.primary, font_color="#FFFFFF")
    cv.merge(r0, C_R0, r0, C_RE, "🍓  AVG CUPS", bold=True, font_size=9.0, align="center",
             bg_color="#53966F", font_color="#FFFFFF")

    r_w = r0 + 1
    cv.put(r_w, C_NAME, "🥤  Số ly nước / sữa (ly)", bold=True, font_size=9.0, align="left", indent=1,
           bg_color=t.soft, font_color=t.ink)
    rnd = random.Random(seed)
    for k in range(1, 32):
        c = day_col(k)
        val = "" if k > 22 else rnd.choice([6, 7, 8, 8, 9, 7, 8, 8])
        cv.put(r_w, c, val, align="center", font_size=9.0, bold=True, bg_color=t.card, font_color=t.ink, num_format="0")
    w_rng = rng(r_w, C_D0, r_w, C_D31)
    cv.unlock(r_w, C_D0, r_w, C_D31)
    cv.grid(r_w, C_NAME, r_w, C_D31, t.line)
    cv.box(r0, C_NAME, r_w, C_D31, t.line)
    ws.conditional_format(w_rng, {"type": "3_color_scale", "min_type": "num", "min_value": 4,
                                  "mid_type": "num", "mid_value": 7, "max_type": "num", "max_value": 10,
                                  "min_color": "#FFF8F5", "mid_color": "#F7B2C4", "max_color": "#D65076"})
    cv.merge(r_w, C_R0, r_w, C_RE, f"=IFERROR(AVERAGE({w_rng}),0)", bold=True, font_size=11.0, align="center",
             num_format='0.0" ly 🥛"', bg_color="#E8F6EE", font_color="#2D6A4A")
    cv.box(r0, C_R0, r_w, C_RE, t.line)

    rb0 = r0 + 3
    ov = tr.s["overall"]
    cv.merge(rb0, C_NAME, rb0, C_D31, "🍰  STRAWBERRY MILK CAFE MENU  •  QUY TẮC PHA CHẾ & TỰ THƯỞNG CUỐI TUẦN",
             bold=True, font_size=9.0, align="left", indent=1, bg_color="#53966F", font_color="#FFFFFF")
    cv.merge(rb0 + 1, C_NAME, rb0 + 1, C_D31,
             "• Sáng: Đeo tạp dề dâu tây, uống 1 ly nước ấm + bữa sáng đủ chất để tỉnh táo làm việc.",
             font_size=9.0, align="left", indent=1, bg_color=t.card, font_color=t.ink)
    cv.merge(rb0 + 2, C_NAME, rb0 + 2, C_D31,
             "• Cuối tuần ≥80%: Tự pha 1 ly sữa dâu kem tươi + lát bánh Shortcake ăn mừng kỷ luật!",
             font_size=9.0, align="left", indent=1, bg_color=t.card, font_color=t.ink)
    cv.unlock(rb0 + 1, C_NAME, rb0 + 2, C_D31)
    cv.grid(rb0 + 1, C_NAME, rb0 + 2, C_D31, t.line)
    cv.box(rb0, C_NAME, rb0 + 2, C_D31, t.line)

    cv.merge(rb0, C_R0, rb0, C_RE, "🍰  CAFE RANK", bold=True, font_size=9.0, align="center",
             bg_color=t.primary, font_color="#FFFFFF")
    cv.merge(rb0 + 1, C_R0, rb0 + 1, C_RE,
             f'=IF({ov}>=0.85,"🍰 Tiệc Shortcake!",IF({ov}>=0.6,"🥛 Sữa Dâu Kem Tươi","🍓 Đeo Tạp Dề Mở Quán"))',
             bold=True, font_size=9.5, align="center", bg_color=t.soft, font_color=t.primary_dark)
    cv.merge(rb0 + 2, C_R0, rb0 + 2, C_RE,
             f'="🍓 Ngày Cafe: "&{tr.s["grown"]}&"d • 🔥 "&{tr.s["best"]}&"d"',
             bold=True, font_size=9.0, align="center", bg_color=t.card, font_color=t.ink)
    cv.box(rb0, C_R0, rb0 + 2, C_RE, t.line)


# 73. Lotso Berry Flower Crown: 6-Stage Crown Weaving Counter + Garden Affirmation
def add_lotso_flower_crown_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 730):
    t, ws = cv.t, cv.ws
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23)
    for rr in range(r0 + 1, r0 + 6):
        cv.row(rr, 22)

    cv.merge(r0, C_NAME, r0, C_D31, "👑  BERRY FLOWER CROWN WEAVER  •  THỐNG KÊ 6 BƯỚC KẾT VƯƠNG MIỆN HOA DÂU TRONG THÁNG",
             bold=True, font_size=9.1, align="left", indent=1, bg_color=t.primary, font_color="#FFFFFF")
    cv.merge(r0, C_R0, r0, C_RE, "🌼  CROWN RANK", bold=True, font_size=9.0, align="center",
             bg_color="#539662", font_color="#FFFFFF")

    stg_rng = f"{tr.calc_q}!{rng(tr.stage_row, 1, tr.stage_row, 31)}"
    tiers = [
        ("🌱 Đầu Trơn", "0%", "#FFF9F5", "#9C4A5E"),
        ("🌼 Cài Cúc", "1–24%", "#FEF9C3", "#854D0E"),
        ("🌿 Nửa Vòng", "25–49%", "#E8F5EB", "#2D6A42"),
        ("👑 Vương Miện", "50–74%", "#FCE7EE", "#B82E50"),
        ("🍓 Chùm Dâu", "75–99%", "#FFE4EC", "#9E1F42"),
        ("✨ Rạng Rỡ!", "100% ✨", "#FCE7F3", "#9D174D"),
    ]
    spans = [(1, 5), (6, 10), (11, 15), (16, 21), (22, 26), (27, 32)]
    for i, ((c1, c2), (lbl, pct, bg, fg)) in enumerate(zip(spans, tiers)):
        cv.merge(r0 + 1, c1, r0 + 1, c2, lbl, bold=True, font_size=9.0, align="center", bg_color=bg, font_color=fg)
        cv.merge(r0 + 2, c1, r0 + 2, c2, f'=COUNTIF({stg_rng},{i + 1})&" ngày"', bold=True, font_size=10.5,
                 align="center", bg_color=t.card, font_color=fg)
        cv.merge(r0 + 3, c1, r0 + 3, c2, pct, italic=True, font_size=9.0, align="center", bg_color=t.page, font_color=t.muted)

    cv.merge(r0 + 4, C_NAME, r0 + 4, C_D31, "🌸  GARDEN BLOOMING AFFIRMATION  •  LỜI NHẮN KHU VƯỜN HOA DÂU",
             bold=True, font_size=9.0, align="left", indent=1, bg_color="#E8F5EB", font_color="#2D6A42")
    cv.merge(r0 + 5, C_NAME, r0 + 5, C_D31,
             "• Mỗi thói quen đều đặn là một bông cúc trắng & quả dâu đỏ — kiên trì từng ngày sẽ kết trọn chiếc vương miện rực rỡ!",
             font_size=9.0, align="left", indent=1, bg_color=t.card, font_color=t.ink)
    cv.unlock(r0 + 5, C_NAME, r0 + 5, C_D31)
    cv.grid(r0 + 1, C_NAME, r0 + 5, C_D31, t.line)
    cv.box(r0, C_NAME, r0 + 5, C_D31, t.line)

    ov = tr.s["overall"]
    cv.merge(r0 + 1, C_R0, r0 + 2, C_RE,
             f'=IF({ov}>=0.9,"👑 Hoàng Tử Vườn Dâu!",IF({ov}>=0.7,"🍓 Chùm Dâu Chín",'
             f'IF({ov}>=0.45,"🌿 Kết Nửa Vòng Hoa","🌼 Cài Bông Cúc Đầu")))',
             bold=True, font_size=10.0, align="center", bg_color=t.soft, font_color=t.primary_dark)
    cv.merge(r0 + 3, C_R0, r0 + 3, C_RE, f"={ov}", bold=True, font_size=9.5, align="center",
             num_format="0%", bg_color=t.card, font_color=t.ink)
    ws.conditional_format(rng(r0 + 3, C_R0, r0 + 3, C_RE), {
        "type": "data_bar", "bar_color": "#D94A6B", "bar_solid": True,
        "min_type": "num", "min_value": 0, "max_type": "num", "max_value": 1,
    })
    cv.merge(r0 + 4, C_R0, r0 + 5, C_RE,
             f'="👑 Ngày 100%: "&{tr.s["perfect"]}&"d"&CHAR(10)&"🔥 Best: "&{tr.s["best"]}&"d"',
             bold=True, font_size=9.0, align="center", text_wrap=True, bg_color="#E8F5EB", font_color="#2D6A42")
    cv.grid(r0 + 1, C_R0, r0 + 5, C_RE, t.line)
    cv.box(r0, C_R0, r0 + 5, C_RE, t.line)


# 74. Lotso Overalls Toy Workshop: 4-Week Workshop Project Sprint Log + Rocket Counter
def add_lotso_overalls_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 740):
    t, ws = cv.t, cv.ws
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23)
    for rr in range(r0 + 1, r0 + 6):
        cv.row(rr, 22)

    cv.merge(r0, C_NAME, r0, C_D31, "🚀  TOY WORKSHOP SPRINT JOURNAL  •  SỔ TAY DỰ ÁN & BẢNG STICKER TUẦN",
             bold=True, font_size=9.1, align="left", indent=1, bg_color=t.primary, font_color="#FFFFFF")
    cv.merge(r0, C_R0, r0, C_RE, "🚀  ROCKET BOOST", bold=True, font_size=9.0, align="center",
             bg_color="#E3657B", font_color="#FFFFFF")

    cv.put(r0 + 1, C_NAME, "📅  CHẶNG XƯỞNG", bold=True, font_size=9.0, align="center", bg_color="#EBF5EC", font_color="#2E5E33")
    cv.merge(r0 + 1, C_D0, r0 + 1, 14, "🛠️  MỤC TIÊU SÁNG TẠO / DỰ ÁN", bold=True, font_size=9.0,
             align="center", bg_color="#EBF5EC", font_color="#2E5E33")
    cv.merge(r0 + 1, 15, r0 + 1, C_D31, "🎉  THÀNH QUẢ & STICKER ĐÃ DÁN", bold=True, font_size=9.0,
             align="center", bg_color="#FDECEF", font_color="#9E2A42")

    sprints = [
        ("Tuần 1 • Khởi ca", "Lên bản vẽ kế hoạch & dọn bàn gọn gàng", "Mặc quần yếm cài cúc, chào Hi! tràn năng lượng."),
        ("Tuần 2 • Chế tác", "Hoàn thiện phần lõi của dự án / bài học", "Dán thêm sticker dâu tây handmade lên sổ tay!"),
        ("Tuần 3 • Tăng tốc", "Bứt phá hoàn tất các hạng mục tồn đọng", "Phóng tên lửa vàng – cam vượt tiến độ tuần!"),
        ("Tuần 4 • Ăn mừng", "Đóng gói sản phẩm & nhìn lại bài học hay", "Vẫy tay ăn mừng cùng bạn heo hồng cực vui!"),
    ]
    for i, (w_s, p_s, r_s) in enumerate(sprints):
        rr = r0 + 2 + i
        bg = "#FFFFFF" if i % 2 == 0 else "#FFFBF0"
        cv.put(rr, C_NAME, w_s, bold=True, font_size=9.0, align="left", indent=1, bg_color=bg, font_color="#2E5E33")
        cv.merge(rr, C_D0, rr, 14, p_s, font_size=9.0, align="left", indent=1, bg_color=bg, font_color=t.ink)
        cv.merge(rr, 15, rr, C_D31, r_s, font_size=9.0, align="left", indent=1, bg_color=bg, font_color=t.ink)
    cv.unlock(r0 + 2, C_NAME, r0 + 5, C_D31)
    cv.grid(r0 + 1, C_NAME, r0 + 5, C_D31, t.line)
    cv.box(r0, C_NAME, r0 + 5, C_D31, t.primary)

    cv.merge(r0 + 1, C_R0, r0 + 2, C_RE, f'="🚀 "&{tr.s["grown"]}&" LẦN"', bold=True, font_size=14.5,
             align="center", bg_color="#FDECEF", font_color="#B82E4C")
    cv.merge(r0 + 3, C_R0, r0 + 3, C_RE, f"=MIN(1,{tr.s['grown']}/20)", bold=True, font_size=9.2,
             align="center", num_format='0%" (Mốc 20 ngày)"', bg_color=t.card, font_color="#2E5E33")
    ws.conditional_format(rng(r0 + 3, C_R0, r0 + 3, C_RE), {
        "type": "data_bar", "bar_color": "#6D9F71", "bar_solid": True,
        "min_type": "num", "min_value": 0, "max_type": "num", "max_value": 1,
    })
    cv.merge(r0 + 4, C_R0, r0 + 5, C_RE,
             f'="🛠️ Ngày 100%: "&{tr.s["perfect"]}&"d"&CHAR(10)&"🔥 Best: "&{tr.s["best"]}&"d"',
             bold=True, font_size=9.0, align="center", text_wrap=True, bg_color="#EBF5EC", font_color="#2E5E33")
    cv.grid(r0 + 1, C_R0, r0 + 5, C_RE, t.line)
    cv.box(r0, C_R0, r0 + 5, C_RE, t.line)


# 75. Lotso LoFi Earphones Flow: Daily Flow Minutes + Lo-Fi Playlist & Soundwave Stats
def add_lotso_lofi_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 750):
    t, ws = cv.t, cv.ws
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23); cv.row(r0 + 1, 22); cv.row(r0 + 2, 10)
    for rr in range(r0 + 3, r0 + 7):
        cv.row(rr, 22)

    cv.put(r0, C_NAME, "🎧  LO-FI FLOW MINUTES", bold=True, font_size=9.2, align="left", indent=1,
           bg_color=t.primary, font_color="#FFFFFF")
    cv.merge(r0, C_D0, r0, C_D31, "SỐ PHÚT TẬP TRUNG SÂU CÙNG NHẠC LO-FI MỖI NGÀY (MINUTES)",
             bold=True, font_size=9.0, align="center", bg_color=t.primary, font_color="#FFFFFF")
    cv.merge(r0, C_R0, r0, C_RE, "🎵  TOTAL FLOW", bold=True, font_size=9.0, align="center",
             bg_color="#6B3A2E", font_color="#FFFFFF")

    r_fl = r0 + 1
    cv.put(r_fl, C_NAME, "🎶  Phút Deep Flow (mins)", bold=True, font_size=9.0, align="left", indent=1,
           bg_color=t.soft, font_color=t.ink)
    rnd = random.Random(seed)
    for k in range(1, 32):
        c = day_col(k)
        val = "" if k > 22 else rnd.choice([45, 60, 75, 90, 120, 60, 90, 105])
        cv.put(r_fl, c, val, align="center", font_size=9.0, bold=True, bg_color=t.card, font_color=t.ink, num_format="0")
    fl_rng = rng(r_fl, C_D0, r_fl, C_D31)
    cv.unlock(r_fl, C_D0, r_fl, C_D31)
    cv.grid(r_fl, C_NAME, r_fl, C_D31, t.line)
    cv.box(r0, C_NAME, r_fl, C_D31, t.line)
    ws.conditional_format(fl_rng, {"type": "3_color_scale", "min_type": "num", "min_value": 0,
                                   "mid_type": "num", "mid_value": 60, "max_type": "num", "max_value": 120,
                                   "min_color": "#FFF4F2", "mid_color": "#F5C2D0", "max_color": "#C84B6E"})
    cv.merge(r_fl, C_R0, r_fl, C_RE, f"=SUM({fl_rng})/60", bold=True, font_size=11.0, align="center",
             num_format='0.0" giờ 🎧"', bg_color="#F5EBE8", font_color="#6B3A2E")
    cv.box(r0, C_R0, r_fl, C_RE, t.line)

    rb0 = r0 + 3
    c_mid = 16
    cv.merge(rb0, C_NAME, rb0, c_mid, "📻  LOTSO LO-FI PLAYLIST  •  NHẠC TẬP TRUNG YÊU THÍCH", bold=True, font_size=9.0,
             align="left", indent=1, bg_color="#C84B6E", font_color="#FFFFFF")
    tracks = [
        "♫  Track 01: Warm Berry Coffee Shop Lo-Fi Beats (90 BPM Focus)",
        "♫  Track 02: Rainy Afternoon Vinyl & Soft Guitar Study Mix",
        "♫  Track 03: Midnight Strawberry Piano Deep Flow Session",
    ]
    for i, trk in enumerate(tracks):
        cv.merge(rb0 + 1 + i, C_NAME, rb0 + 1 + i, c_mid, trk, font_size=9.0, align="left", indent=1,
                 bg_color=t.card, font_color=t.ink)
        cv.hline(rb0 + 1 + i, C_NAME, c_mid, t.line)
    cv.unlock(rb0 + 1, C_NAME, rb0 + 3, c_mid)
    cv.box(rb0, C_NAME, rb0 + 3, c_mid, t.line)

    cv.merge(rb0, c_mid + 2, rb0, C_D31, "🌊  DEEP FLOW RULES  •  BÍ QUYẾT VÀO GUỒNG", bold=True, font_size=9.0,
             align="left", indent=1, bg_color="#6B3A2E", font_color="#FFFFFF")
    rules = [
        "• Đeo tai nghe dây nâu, bật chế độ Không Làm Phiền (DND) 45 phút.",
        "• Mở duy nhất 1 tab công việc chính — gạt hết xao nhãng sang một bên.",
        "• Kết thúc phiên nhạc: vươn vai, uống nước ấm & ghi lại tiến độ!",
    ]
    for i, rl in enumerate(rules):
        cv.merge(rb0 + 1 + i, c_mid + 2, rb0 + 1 + i, C_D31, rl, font_size=9.0, align="left", indent=1,
                 bg_color=t.card, font_color=t.ink)
        cv.hline(rb0 + 1 + i, c_mid + 2, C_D31, t.line)
    cv.unlock(rb0 + 1, c_mid + 2, rb0 + 3, C_D31)
    cv.box(rb0, c_mid + 2, rb0 + 3, C_D31, t.line)

    cv.merge(rb0, C_R0, rb0, C_RE, "🎶  FLOW METER", bold=True, font_size=9.0, align="center",
             bg_color=t.primary_dark, font_color="#FFFFFF")
    cv.merge(rb0 + 1, C_R0, rb0 + 2, C_RE,
             f'="🎧 TB: "&TEXT(IFERROR(AVERAGE({fl_rng}),0),"0")&" phút/ngày"',
             bold=True, font_size=10.0, align="center", bg_color=t.soft, font_color=t.primary_dark)
    cv.merge(rb0 + 3, C_R0, rb0 + 3, C_RE,
             f'="🎵 Ngày Flow: "&{tr.s["grown"]}&"d • 🔥 "&{tr.s["best"]}&"d"',
             bold=True, font_size=9.0, align="center", bg_color=t.card, font_color="#6B3A2E")
    cv.box(rb0, C_R0, rb0 + 3, C_RE, t.line)


# 76. Lotso Mood Detox Comic: Daily Stress-to-Joy Meter (1–5) + 5 Weekly Mood Detox Donut Gauges
def add_lotso_mood_detox_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 760):
    t, ws = cv.t, cv.ws
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23); cv.row(r0 + 1, 22); cv.row(r0 + 2, 10)
    for rr in range(r0 + 3, r0 + 8):
        cv.row(rr, 22)

    cv.put(r0, C_NAME, "⚡  MOOD DETOX METER", bold=True, font_size=9.2, align="left", indent=1,
           bg_color=t.primary, font_color="#FFFFFF")
    cv.merge(r0, C_D0, r0, C_D31, "CHỈ SỐ GIẢI TỎA STRESS & TÂM TRẠNG TÍCH CỰC MỖI NGÀY (1 = TIA SÉT → 5 = MƯA TIM)",
             bold=True, font_size=9.0, align="center", bg_color=t.primary, font_color="#FFFFFF")
    cv.merge(r0, C_R0, r0, C_RE, "💖  MOOD AVG", bold=True, font_size=9.0, align="center",
             bg_color="#D9A026", font_color="#FFFFFF")

    r_m = r0 + 1
    cv.put(r_m, C_NAME, "💗  Tâm trạng cuối ngày (1–5)", bold=True, font_size=9.0, align="left", indent=1,
           bg_color=t.soft, font_color=t.ink)
    rnd = random.Random(seed)
    for k in range(1, 32):
        c = day_col(k)
        val = "" if k > 22 else rnd.choice([4, 4, 5, 5, 3, 4, 5, 5])
        cv.put(r_m, c, val, align="center", font_size=9.0, bold=True, bg_color=t.card, font_color=t.ink, num_format="0")
    m_rng = rng(r_m, C_D0, r_m, C_D31)
    cv.unlock(r_m, C_D0, r_m, C_D31)
    cv.grid(r_m, C_NAME, r_m, C_D31, t.line)
    cv.box(r0, C_NAME, r_m, C_D31, t.line)
    ws.conditional_format(m_rng, {"type": "3_color_scale", "min_type": "num", "min_value": 1,
                                  "mid_type": "num", "mid_value": 3, "max_type": "num", "max_value": 5,
                                  "min_color": "#FEF3C7", "mid_color": "#FBCFE8", "max_color": "#B8456A"})
    cv.merge(r_m, C_R0, r_m, C_RE, f"=IFERROR(AVERAGE({m_rng}),0)", bold=True, font_size=11.0,
             align="center", num_format='0.0" / 5 💖"', bg_color="#FEF9C3", font_color="#854D0E")
    cv.box(r0, C_R0, r_m, C_RE, t.line)

    rd = r0 + 3
    cv.merge(rd, C_NAME, rd + 4, C_NAME, "💖  MOOD DETOX GAUGES\nNhịp cân bằng 5 tuần", bold=True,
             font_size=10.0, align="center", text_wrap=True, bg_color=t.card, font_color=t.primary_dark)
    rb = tr.calc_row_base
    spans = [(2, 7), (8, 13), (14, 19), (20, 25), (26, 32)]
    dcols = ["#B8456A", "#E5B03A", "#A8649E", "#D95D82", "#9C3456"]
    for w, (c1, c2) in enumerate(spans):
        hc = CALC_WK_COL0 + w
        cv.merge(rd, c1, rd, c2, f"WEEK {w + 1}", bold=True, font_size=9.0, align="center",
                 bg_color=t.week_head[w], font_color=t.week_on[w])
        cv.merge(rd + 1, c1, rd + 4, c2, f"={tr.calc_q}!{acell(rb + 2, hc)}", bold=True, font_size=12.5,
                 align="center", num_format="0%", bg_color=t.card, font_color=dcols[w])
        dch = donut(wb, f"={tr.calc_q}!{rng(rb + 2, hc, rb + 3, hc)}", [dcols[w], t.donut_rest], hole=70)
        place_chart(cv, dch, rd + 1, c1, rd + 4, c2, pad_x=10, pad_y=2)
        cv.vline(c2, rd, rd + 4, t.line, where="right")
    cv.box(rd, C_NAME, rd + 4, C_D31, t.line)

    cv.merge(rd, C_R0, rd, C_RE, "🎈  ANTI-STRESS TIP", bold=True, font_size=9.0, align="center",
             bg_color=t.primary_dark, font_color="#FFFFFF")
    cv.merge(rd + 1, C_R0, rd + 3, C_RE,
             "• Bực bội? Dừng 60 giây, uống ngụm nước mát.\n• Chia việc lớn thành 1 bước siêu nhỏ.\n• Ôm bóng tim & khen mình đã cố gắng!",
             font_size=9.0, align="left", indent=1, text_wrap=True, bg_color=t.card, font_color=t.ink)
    cv.unlock(rd + 1, C_R0, rd + 3, C_RE)
    cv.merge(rd + 4, C_R0, rd + 4, C_RE,
             f'="💖 Ngày An: "&{tr.s["grown"]}&"d • ✨ "&{tr.s["perfect"]}&"d"',
             bold=True, font_size=9.0, align="center", bg_color=t.soft, font_color=t.primary_dark)
    cv.box(rd, C_R0, rd + 4, C_RE, t.line)


# 77. Lotso Floral Sweet Dreams: Evening Sleep Hours + 3-Part Sweet Dreams Cloud Routine
def add_lotso_sweet_dreams_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 770):
    t, ws = cv.t, cv.ws
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23); cv.row(r0 + 1, 22); cv.row(r0 + 2, 10)
    for rr in range(r0 + 3, r0 + 7):
        cv.row(rr, 22)

    cv.put(r0, C_NAME, "🐑  SWEET DREAMS SLEEP LOG", bold=True, font_size=9.2, align="left", indent=1,
           bg_color=t.primary, font_color="#FFFFFF")
    cv.merge(r0, C_D0, r0, C_D31, "SỐ GIỜ NGỦ ÊM ÁI CÙNG MÂY CỪU TÍM MỖI ĐÊM (MỤC TIÊU 7.5 – 8.5 GIỜ)",
             bold=True, font_size=9.0, align="center", bg_color=t.primary, font_color="#FFFFFF")
    cv.merge(r0, C_R0, r0, C_RE, "☁️  AVG SLEEP", bold=True, font_size=9.0, align="center",
             bg_color="#8A6BB8", font_color="#FFFFFF")

    r_sl = r0 + 1
    cv.put(r_sl, C_NAME, "🌙  Giờ ngủ mỗi đêm (h)", bold=True, font_size=9.0, align="left", indent=1,
           bg_color=t.soft, font_color=t.ink)
    rnd = random.Random(seed)
    for k in range(1, 32):
        c = day_col(k)
        val = "" if k > 22 else rnd.choice([7.5, 8.0, 8.0, 8.5, 7.0, 7.5, 8.0, 8.0])
        cv.put(r_sl, c, val, align="center", font_size=9.0, bold=True, bg_color=t.card, font_color=t.ink, num_format="0.0")
    sl_rng = rng(r_sl, C_D0, r_sl, C_D31)
    cv.unlock(r_sl, C_D0, r_sl, C_D31)
    cv.grid(r_sl, C_NAME, r_sl, C_D31, t.line)
    cv.box(r0, C_NAME, r_sl, C_D31, t.line)
    ws.conditional_format(sl_rng, {"type": "3_color_scale", "min_type": "num", "min_value": 5.5,
                                   "mid_type": "num", "mid_value": 7.5, "max_type": "num", "max_value": 9.0,
                                   "min_color": "#FFF7FB", "mid_color": "#E6DAF7", "max_color": "#C25674"})
    cv.merge(r_sl, C_R0, r_sl, C_RE, f"=IFERROR(AVERAGE({sl_rng}),0)", bold=True, font_size=11.0,
             align="center", num_format='0.0" giờ 🐑"', bg_color="#F1EAF9", font_color="#5E408C")
    cv.box(r0, C_R0, r_sl, C_RE, t.line)

    rb0 = r0 + 3
    cards = [
        ("🌹  21:30 • TỔNG KẾT BÓ HOA", (1, 10), "#C25674", "#FFF5F9",
         "• Tick gọn các thói quen hôm nay.\n• Ghi 1 bông hoa biết ơn dịu dàng."),
        ("☁️  22:00 • ĐÁM MÂY THƯ GIÃN", (12, 21), "#9374C4", "#F5F0FC",
         "• Hạ ánh sáng đèn, rời màn hình.\n• Uống trà hoa cúc ấm nhẹ lòng."),
        ("🐑  22:30 • ĐẾM CỪU TÍM NGỦ", (23, 32), "#A64561", "#FFF4F8",
         "• Hít sâu thở chậm thả lỏng vai.\n• Ngủ sâu 8 tiếng mơ đẹp êm ái!"),
    ]
    for title, (c1, c2), h_bg, c_bg, body in cards:
        cv.merge(rb0, c1, rb0, c2, title, bold=True, font_size=9.0, align="center", bg_color=h_bg, font_color="#FFFFFF")
        cv.merge(rb0 + 1, c1, rb0 + 3, c2, body, font_size=9.0, align="left", indent=1, text_wrap=True, bg_color=c_bg, font_color=t.ink)
        cv.unlock(rb0 + 1, c1, rb0 + 3, c2)
        cv.box(rb0, c1, rb0 + 3, c2, h_bg)

    cv.merge(rb0, C_R0, rb0, C_RE, "🐑  DREAM SCORE", bold=True, font_size=9.0, align="center",
             bg_color=t.primary_dark, font_color="#FFFFFF")
    cv.merge(rb0 + 1, C_R0, rb0 + 2, C_RE,
             f'=IF(IFERROR(AVERAGE({sl_rng}),0)>=7.8,"🐑 Mơ Cừu Bồng Bềnh!",IF(IFERROR(AVERAGE({sl_rng}),0)>=7.0,"🌹 Ngủ Đủ Giấc","☁️ Ngủ Sớm Hơn Nhé"))',
             bold=True, font_size=9.5, align="center", bg_color=t.soft, font_color=t.primary_dark)
    cv.merge(rb0 + 3, C_R0, rb0 + 3, C_RE,
             f'="🌙 Đêm Đẹp: "&{tr.s["grown"]}&"d • 🔥 "&{tr.s["best"]}&"d"',
             bold=True, font_size=9.0, align="center", bg_color=t.card, font_color=t.ink)
    cv.box(rb0, C_R0, rb0 + 3, C_RE, t.line)


# 78. Lotso Daisy Cheek Glow: Daily Joy Score + 5-Week Sunny Daisy Progress Bars
def add_lotso_daisy_glow_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 780):
    t, ws = cv.t, cv.ws
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23); cv.row(r0 + 1, 22); cv.row(r0 + 2, 10)
    for rr in range(r0 + 3, r0 + 7):
        cv.row(rr, 22)

    cv.put(r0, C_NAME, "🌼  DAISY CHEEK GLOW SCORE", bold=True, font_size=9.2, align="left", indent=1,
           bg_color=t.primary, font_color="#FFFFFF")
    cv.merge(r0, C_D0, r0, C_D31, "ĐỘ TƯƠI TẮN & NIỀM VUI NHẸ NHÀNG MỖI NGÀY CÙNG LOTSO HOA CÚC (1 – 5)",
             bold=True, font_size=9.0, align="center", bg_color=t.primary, font_color="#FFFFFF")
    cv.merge(r0, C_R0, r0, C_RE, "☀️  GLOW AVG", bold=True, font_size=9.0, align="center",
             bg_color="#D9A31E", font_color="#FFFFFF")

    r_gl = r0 + 1
    cv.put(r_gl, C_NAME, "🌼  Điểm tươi tắn ngày (1–5)", bold=True, font_size=9.0, align="left", indent=1,
           bg_color=t.soft, font_color=t.ink)
    rnd = random.Random(seed)
    for k in range(1, 32):
        c = day_col(k)
        val = "" if k > 22 else rnd.choice([4, 5, 4, 5, 3, 5, 4, 5])
        cv.put(r_gl, c, val, align="center", font_size=9.0, bold=True, bg_color=t.card, font_color=t.ink, num_format="0")
    j_rng = rng(r_gl, C_D0, r_gl, C_D31)
    cv.unlock(r_gl, C_D0, r_gl, C_D31)
    cv.grid(r_gl, C_NAME, r_gl, C_D31, t.line)
    cv.box(r0, C_NAME, r_gl, C_D31, t.line)
    ws.conditional_format(j_rng, {"type": "3_color_scale", "min_type": "num", "min_value": 1,
                                  "mid_type": "num", "mid_value": 3, "max_type": "num", "max_value": 5,
                                  "min_color": "#FFF9F2", "mid_color": "#FEF08A", "max_color": "#F6CE55"})
    cv.merge(r_gl, C_R0, r_gl, C_RE, f"=IFERROR(AVERAGE({j_rng}),0)", bold=True, font_size=11.0,
             align="center", num_format='0.0" / 5 🌼"', bg_color="#FEF9C3", font_color="#854D0E")
    cv.box(r0, C_R0, r_gl, C_RE, t.line)

    rb0 = r0 + 3
    rb = tr.calc_row_base
    cv.merge(rb0, C_NAME, rb0, C_D31, "🌼  SUNNY DAISY WEEKLY PROGRESS  •  THANH TIẾN ĐỘ HOA CÚC 5 TUẦN",
             bold=True, font_size=9.0, align="left", indent=1, bg_color="#96394F", font_color="#FFFFFF")
    spans = [(1, 6), (7, 13), (14, 19), (20, 26), (27, 32)]
    p_cols = ["#B94E66", "#F6CE55", "#D67086", "#EAB308", "#A33E55"]
    p_bgs = ["#FCECEF", "#FEF9C3", "#FCECEF", "#FEF3C7", "#FCECEF"]
    p_fgs = ["#8C2D42", "#854D0E", "#8C2D42", "#92400E", "#752235"]
    for w, ((c1, c2), bc, bg, fg) in enumerate(zip(spans, p_cols, p_bgs, p_fgs)):
        hc = CALC_WK_COL0 + w
        pct_ref = f"{tr.calc_q}!{acell(rb + 2, hc)}"
        cv.merge(rb0 + 1, c1, rb0 + 1, c2, f"🌼 WEEK {w + 1}", bold=True, font_size=9.0, align="center", bg_color=bg, font_color=fg)
        cv.merge(rb0 + 2, c1, rb0 + 2, c2, f"={pct_ref}", bold=True, font_size=11.0, align="center",
                 num_format="0%", bg_color=t.card, font_color=fg)
        ws.conditional_format(rng(rb0 + 2, c1, rb0 + 2, c2), {
            "type": "data_bar", "bar_color": bc, "bar_solid": True,
            "min_type": "num", "min_value": 0, "max_type": "num", "max_value": 1,
        })
        cv.merge(rb0 + 3, c1, rb0 + 3, c2,
                 f'=IF({pct_ref}>=0.8,"🌼 Rạng Rỡ Nháy Mắt!",IF({pct_ref}>=0.5,"✨ Cài Cúc Lên Tai","🌼 Nhặt Hoa Cúc"))',
                 italic=True, font_size=9.0, align="center", bg_color=t.page, font_color=fg)
    cv.grid(rb0 + 1, C_NAME, rb0 + 3, C_D31, t.line)
    cv.box(rb0, C_NAME, rb0 + 3, C_D31, t.line)

    cv.merge(rb0, C_R0, rb0, C_RE, "☀️  DAISY SMILE NOTE", bold=True, font_size=9.0, align="center",
             bg_color="#D9A31E", font_color="#FFFFFF")
    cv.merge(rb0 + 1, C_R0, rb0 + 2, C_RE,
             "• Thả lỏng đôi vai, mỉm cười chữ U thật hiền mỗi sáng!",
             font_size=9.0, align="left", indent=1, text_wrap=True, bg_color=t.card, font_color=t.ink)
    cv.unlock(rb0 + 1, C_R0, rb0 + 2, C_RE)
    cv.merge(rb0 + 3, C_R0, rb0 + 3, C_RE,
             f'="🌼 Glow Days: "&{tr.s["grown"]}&"d • 🔥 "&{tr.s["best"]}&"d"',
             bold=True, font_size=9.0, align="center", bg_color=t.soft, font_color=t.primary_dark)
    cv.box(rb0, C_R0, rb0 + 3, C_RE, t.line)


# 79. Lotso Bunny Headband Selfcare: 3 Live Routine Grouping Cards (Morning / Day / Spa Night)
def add_lotso_bunny_selfcare_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 790):
    from .tracker import R_H0, CALC_DONEN_COL, CALC_GOALN_COL
    t, cq = cv.t, tr.calc_q
    C_RE = tr.c_right_end
    rb = tr.calc_row_base
    r0 = R_EXTRA
    cv.row(r0, 23)
    for rr in range(r0 + 1, r0 + 6):
        cv.row(rr, 22)

    groups = [
        ("☀️  MORNING FRESH (SÁNG)", 0, 2, (1, 10), "#EB7B9B", "#FFF2F6", "#A63759"),
        ("🍓  DAYTIME CARE (BAN NGÀY)", 3, 5, (12, 21), "#A8649E", "#F8F0F7", "#733A6B"),
        ("🐰  NIGHT SPA ROUTINE (TỐI)", 6, 8, (23, 32), "#8B529E", "#F5EEF9", "#5B2E6B"),
    ]
    for title, h_a, h_b, (c1, c2), hdr_bg, card_bg, fg in groups:
        d_rng = f"{cq}!{rng(rb + R_H0 + h_a, CALC_DONEN_COL, rb + R_H0 + h_b, CALC_DONEN_COL)}"
        g_rng = f"{cq}!{rng(rb + R_H0 + h_a, CALC_GOALN_COL, rb + R_H0 + h_b, CALC_GOALN_COL)}"
        cv.merge(r0, c1, r0, c2, title, bold=True, font_size=9.0, align="center", bg_color=hdr_bg, font_color="#FFFFFF")
        cv.merge(r0 + 1, c1, r0 + 2, c2, f"=IFERROR(SUM({d_rng})/SUM({g_rng}),0)", bold=True, font_size=17.0,
                 align="center", num_format="0%", bg_color=t.card, font_color=fg)
        cv.merge(r0 + 3, c1, r0 + 3, c2, f'=SUM({d_rng})&" / "&SUM({g_rng})&" bước hoàn thành"',
                 bold=True, font_size=9.0, align="center", bg_color=card_bg, font_color=fg)
        cv.box(r0, c1, r0 + 3, c2, hdr_bg)

    cv.merge(r0 + 4, C_NAME, r0 + 4, C_D31, "🐰  BUNNY HEADBAND SPA PROMISE  •  LỜI HỨA CHĂM SÓC BẢN THÂN",
             bold=True, font_size=9.0, align="left", indent=1, bg_color="#F3E5F5", font_color="#6A326E")
    cv.merge(r0 + 5, C_NAME, r0 + 5, C_D31,
             "• Đặt điện thoại xuống đúng giờ, đeo bờm tai thỏ tím & dành trọn 15 phút skincare thư giãn yêu chiều bản thân!",
             italic=True, font_size=9.0, align="left", indent=1, bg_color=t.card, font_color=t.ink)
    cv.unlock(r0 + 5, C_NAME, r0 + 5, C_D31)
    cv.box(r0 + 4, C_NAME, r0 + 5, C_D31, t.line)

    cv.merge(r0, C_R0, r0, C_RE, "🐰  SPA GLOW RANK", bold=True, font_size=9.0, align="center",
             bg_color=t.primary, font_color="#FFFFFF")
    cv.merge(r0 + 1, C_R0, r0 + 2, C_RE,
             f'=IF({tr.s["overall"]}>=0.85,"🐰 Rạng Ngời Self-Care!",IF({tr.s["overall"]}>=0.6,"🧴 Đắp Mặt Nạ Dâu","🎀 Đeo Bờm Bắt Đầu"))',
             bold=True, font_size=9.8, align="center", bg_color=t.soft, font_color=t.primary_dark)
    cv.merge(r0 + 3, C_R0, r0 + 3, C_RE, f'="🐰 Ngày Spa: "&{tr.s["grown"]}&" ngày"',
             bold=True, font_size=9.0, align="center", bg_color=t.card, font_color=t.ink)
    cv.merge(r0 + 4, C_R0, r0 + 5, C_RE,
             f'="💖 Ngày 100%: "&{tr.s["perfect"]}&"d"&CHAR(10)&"🔥 Best: "&{tr.s["best"]}&"d"',
             bold=True, font_size=9.0, align="center", text_wrap=True, bg_color="#FFF2F6", font_color="#A63759")
    cv.grid(r0 + 1, C_R0, r0 + 5, C_RE, t.line)
    cv.box(r0, C_R0, r0 + 5, C_RE, t.line)


# 80. Lotso Berry Gift Box Party: 5-Week Gift Box Unlocks + Celebration Wish Board
def add_lotso_gift_box_block(wb, cv: Canvas, tr: TrackerRefs, seed: int = 800):
    t, ws = cv.t, cv.ws
    C_RE = tr.c_right_end
    r0 = R_EXTRA
    cv.row(r0, 23)
    for rr in range(r0 + 1, r0 + 7):
        cv.row(rr, 22)

    cv.merge(r0, C_NAME, r0, C_D31, "🎁  BERRY GIFT BOX PARTY UNLOCKS  •  MỞ KHÓA 5 HỘP QUÀ PHẦN THƯỞNG TUẦN",
             bold=True, font_size=9.2, align="left", indent=1, bg_color=t.primary, font_color="#FFFFFF")
    cv.merge(r0, C_R0, r0, C_RE, "🎉  PARTY LEVEL", bold=True, font_size=9.0, align="center",
             bg_color="#942449", font_color="#FFFFFF")

    rb = tr.calc_row_base
    spans = [(1, 6), (7, 13), (14, 19), (20, 26), (27, 32)]
    w_bgs = ["#FCE7EF", "#FEF5D6", "#FCE7EF", "#FEF5D6", "#FCE7EF"]
    w_fgs = ["#C43E67", "#8A6208", "#C43E67", "#8A6208", "#942449"]
    w_bars = ["#C43E67", "#F5CB69", "#E05A84", "#EAB948", "#A82E54"]
    for w, ((c1, c2), bg, fg, barc) in enumerate(zip(spans, w_bgs, w_fgs, w_bars)):
        hc = CALC_WK_COL0 + w
        pct_ref = f"{tr.calc_q}!{acell(rb + 2, hc)}"
        cv.merge(r0 + 1, c1, r0 + 1, c2, f"🎁 WEEK {w + 1}", bold=True, font_size=9.0, align="center", bg_color=bg, font_color=fg)
        cv.merge(r0 + 2, c1, r0 + 2, c2, f"={pct_ref}", bold=True, font_size=11.0, align="center", num_format="0%",
                 bg_color=t.card, font_color=fg)
        ws.conditional_format(rng(r0 + 2, c1, r0 + 2, c2), {
            "type": "data_bar", "bar_color": barc, "bar_solid": True,
            "min_type": "num", "min_value": 0, "max_type": "num", "max_value": 1,
        })
        cv.merge(r0 + 3, c1, r0 + 3, c2,
                 f'=IF({pct_ref}>=0.8,"🥳 Tung Confetti Quà!",IF({pct_ref}>=0.5,"🧁 Mở Hộp Cupcake","🎁 Hộp Quà Đang Chờ"))',
                 italic=True, font_size=9.0, align="center", bg_color=t.page, font_color=fg)

    cv.merge(r0 + 4, C_NAME, r0 + 4, C_D31, "🧁  CELEBRATION WISH & REWARD BOARD  •  BẢNG ĐIỀU ƯỚC & PHẦN THƯỞNG KỶ LUẬT",
             bold=True, font_size=9.0, align="left", indent=1, bg_color="#FEF5D6", font_color="#785206")
    cv.merge(r0 + 5, C_NAME, r0 + 5, C_D31,
             "• Điều ước tháng này: Duy trì đều đặn thói quen nhỏ để tự tin mở trọn 5 hộp quà tuần cùng Lotso!",
             font_size=9.0, align="left", indent=1, bg_color=t.card, font_color=t.ink)
    cv.merge(r0 + 6, C_NAME, r0 + 6, C_D31,
             "• Phần thưởng Tiệc 100%: Thưởng 1 chiếc bánh Cupcake / món quà nhỏ mơ ước khi tổng tháng đạt ≥ 80%!",
             font_size=9.0, align="left", indent=1, bg_color=t.card, font_color=t.ink)
    cv.unlock(r0 + 5, C_NAME, r0 + 6, C_D31)
    cv.grid(r0 + 1, C_NAME, r0 + 6, C_D31, t.line)
    cv.box(r0, C_NAME, r0 + 6, C_D31, t.line)

    ov = tr.s["overall"]
    cv.merge(r0 + 1, C_R0, r0 + 2, C_RE,
             f'=IF({ov}>=0.9,"🥳 CONFETTI PARTY!",IF({ov}>=0.7,"🧁 ÔM CUPCAKE ƯỚC",'
             f'IF({ov}>=0.45,"🎉 ĐỘI MŨ TIỆC","🎁 LẤP LÓ HỘP QUÀ")))',
             bold=True, font_size=9.8, align="center", bg_color=t.soft, font_color=t.primary_dark)
    cv.merge(r0 + 3, C_R0, r0 + 4, C_RE,
             f'="🎁 Tổng lượt tick: "&{tr.s["tdone"]}&CHAR(10)&"🎉 Ngày tiệc ≥75%: "&{tr.s["grown"]}&"d"',
             bold=True, font_size=9.0, align="center", text_wrap=True, bg_color=t.card, font_color=t.ink)
    cv.merge(r0 + 5, C_R0, r0 + 6, C_RE,
             f'="✨ Ngày 100%: "&{tr.s["perfect"]}&"d"&CHAR(10)&"🔥 Best Streak: "&{tr.s["best"]}&"d"',
             bold=True, font_size=9.0, align="center", text_wrap=True, bg_color="#FEF5D6", font_color="#785206")
    cv.grid(r0 + 1, C_R0, r0 + 6, C_RE, t.line)
    cv.box(r0, C_R0, r0 + 6, C_RE, t.line)





