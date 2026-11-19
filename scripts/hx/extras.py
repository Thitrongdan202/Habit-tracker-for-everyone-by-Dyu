"""
hx.extras — Bespoke secondary dashboard, planner, budget, wellness & gamification sheets.
"""
from __future__ import annotations

from .core import (Canvas, Styles, acell, cell, colname, qs, rng, kpi_card, donut,
                   place_chart, axis_font, text_lines, MONTHS_EN)
from .tracker import (C_NAME, C_D0, C_D31, C_WK0, R_H0, R_H1, R_PCT, R_DONE, R_DAY,
                      N_HABITS, TrackerRefs, day_col)


def _finish_sheet(ws, cv: Canvas, tab_color: str, zoom: int = 90):
    ws.hide_gridlines(2)
    ws.set_zoom(zoom)
    ws.set_tab_color(tab_color)
    ws.set_landscape()
    ws.set_paper(9)
    ws.fit_to_pages(1, 0)
    ws.set_margins(0.3, 0.3, 0.4, 0.4)
    cv.flush()


# =========================================================================== #
#  1A. Template 1 — 🎯 Yearly Goals & Habits (Ref 2)
# =========================================================================== #
def build_yearly_goals_sheet(wb, styles: Styles, offline_sprites: bool = False):
    name = "🎯 Yearly Goals & Habits"
    t = styles.t
    ws = wb.add_worksheet(name)
    cv = Canvas(wb, ws, styles, name)

    # Cols: 0 gutter | 1 chk | 2 MY GOALS | 3 MONTHLY | 4 WEEKLY | 5 DAILY | 6 gap | 7..8 sidebar | 9 gutter
    cv.col(0, 2.5)
    cv.col(1, 4.8)
    cv.col(2, 24)
    cv.col(3, 30)
    cv.col(4, 30)
    cv.col(5, 30)
    cv.col(6, 2.2)
    cv.col(7, 17)
    cv.col(8, 17)
    cv.col(9, 2.5)

    cv.row(0, 12)
    cv.row(1, 32)
    cv.row(2, 10)
    cv.row(3, 24)
    cv.row(4, 22)

    cv.merge(1, 1, 1, 5, "🌻  YEARLY GOALS & HABITS PLANNER", font_name=t.font_title,
             font_size=15, bold=True, align="center", bg_color=t.primary, font_color=t.on_primary)
    cv.box(1, 1, 1, 5, t.line)

    cv.merge(3, 1, 4, 2, "MY GOALS • MỤC TIÊU NĂM", bold=True, font_size=10, align="center",
             bg_color=t.primary, font_color=t.on_primary)
    cv.merge(3, 3, 3, 5, "MY HABITS • KẾ HOẠCH HÀNH ĐỘNG", bold=True, font_size=10, align="center",
             bg_color=t.primary, font_color=t.on_primary)
    cv.put(4, 3, "MONTHLY HABITS (Hàng tháng)", bold=True, font_size=9, align="center", bg_color=t.soft, font_color=t.ink)
    cv.put(4, 4, "WEEKLY HABITS (Hàng tuần)", bold=True, font_size=9, align="center", bg_color=t.soft, font_color=t.ink)
    cv.put(4, 5, "DAILY HABITS (Hàng ngày)", bold=True, font_size=9, align="center", bg_color=t.soft, font_color=t.ink)

    rows = [
        (True, "Tăng cường sức khỏe thể chất", "Đánh giá lịch tập & chỉ số sức khỏe mỗi tháng",
         "Đi bộ / chạy bộ cuối tuần ít nhất 2 giờ", "Tập thể dục / yoga 30 phút mỗi sáng"),
        (True, "Chăm sóc sức khỏe tinh thần", "Chấm điểm mức độ stress & hạnh phúc (1–10)",
         "Xem 1 bộ phim truyền cảm hứng / gặp bạn bè", "Viết nhật ký cảm xúc & thiền 10 phút"),
        (True, "Tự do tài chính & Tiết kiệm", "Lập ngân sách tháng & tiết kiệm ≥ 3 triệu",
         "Kiểm tra tổng chi tiêu mỗi Chủ nhật", "Ghi chép chi tiêu hằng ngày, hạn chế mua bốc đồng"),
        (True, "Đọc sách & Mở rộng tri thức", "Hoàn thành ít nhất 1 cuốn sách mỗi tháng",
         "Đọc sách tối thiểu 5 ngày / tuần & tóm tắt", "Đọc sách 20 phút mỗi tối trước khi ngủ"),
        (True, "Uống đủ nước & Ăn lành mạnh", "Biến việc uống nước thành phản xạ tự nhiên",
         "Chuẩn bị rau xanh & meal prep ít nhất 5 bữa", "Uống đủ 2L nước & ăn 1 bữa nhiều rau xanh"),
        (True, "Hạn chế đồ ăn nhanh & đồ ngọt", "Giảm 70% đồ ăn chế biến sẵn so với tháng trước",
         "Tự nấu ăn ở nhà tối thiểu 5 buổi / tuần", "Ưu tiên thực phẩm tươi, thay trà sữa bằng nước lọc"),
        (True, "Ngủ đủ 8 tiếng & Dậy sớm", "Cảm thấy tỉnh táo, không uể oải mỗi sáng",
         "Đạt ít nhất 5 đêm ngủ đủ 7.5–8 tiếng", "Tắt màn hình trước 22h30, đi ngủ trước 23h00"),
        (True, "Không gian sống gọn gàng", "Tổng vệ sinh 1 khu vực lớn trong nhà mỗi tháng",
         "Giặt giũ, thay ga gối & sắp xếp bàn học", "Dành 10 phút dọn dẹp nhanh (rửa bát, gấp chăn)"),
        (True, "Nâng cao tiếng Anh / Chuyên môn", "Hoàn thành 1 khóa học mini / 1 dự án nhỏ",
         "Luyện nghe nói hoặc viết 3 buổi / tuần", "Học 30 phút mỗi ngày (từ vựng / kỹ năng)"),
        (False, "Viết nhật ký biết ơn", "Đọc lại nhật ký cuối tháng để nhìn thấy sự trưởng thành",
         "Viết ít nhất 4 lần / tuần về 3 điều biết ơn", "Ghi 3 dòng ngắn trước khi đi ngủ"),
    ]
    r0 = 5
    total_rows = 20
    for i in range(total_rows):
        rr = r0 + i
        if i < len(rows):
            chk, g, m, w, d = rows[i]
            max_l = max(text_lines(g, 23), text_lines(m, 29), text_lines(w, 29), text_lines(d, 29))
            cv.row(rr, max(24, max_l * 14 + 8))
        else:
            chk, g, m, w, d = False, "", "", "", ""
            cv.row(rr, 23)
        bg = t.card if i % 2 == 0 else t.page
        cv.checkbox(rr, 1, chk, align="center", font_color=t.week_check[0], bg_color=bg)
        cv.put(rr, 2, g, bold=bool(g), font_size=9.5, align="left", text_wrap=True, bg_color=bg, font_color=t.ink)
        cv.put(rr, 3, m, font_size=9, align="left", text_wrap=True, bg_color=bg, font_color=t.ink)
        cv.put(rr, 4, w, font_size=9, align="left", text_wrap=True, bg_color=bg, font_color=t.ink)
        cv.put(rr, 5, d, font_size=9, align="left", text_wrap=True, bg_color=bg, font_color=t.ink)

    cv.grid(3, 1, r0 + total_rows - 1, 5, t.line)
    cv.box(3, 1, r0 + total_rows - 1, 5, t.line)

    # Sidebar: INSTRUCTIONS card (rows 3..14, cols 7..8)
    cv.merge(3, 7, 3, 8, "📌  INSTRUCTIONS • HƯỚNG DẪN", bold=True, font_size=9.5, align="center",
             bg_color=t.primary, font_color=t.on_primary)
    inst = [
        "★  Trang này giúp bạn biến Mục tiêu năm thành các Thói quen cụ thể (Tháng → Tuần → Ngày).",
        "★  Bước 1: Viết 1 mục tiêu lớn ở cột MY GOALS.",
        "★  Bước 2: Chia nhỏ thành thói quen Hàng tháng, Hàng tuần và Hàng ngày tương ứng.",
        "★  Bước 3: Tick vào ô ☑ bên trái mỗi khi bạn bắt đầu triển khai hoặc hoàn thành mục tiêu đó để 'gieo' 1 bông hoa hướng dương!",
        "★  Mẹo: Copy các thói quen ở cột DAILY HABITS dán sang tab 🌻 Monthly Tracker để theo dõi mỗi ngày.",
    ]
    r_cur = 4
    for txt in inst:
        cv.merge(r_cur, 7, r_cur + 1, 8, txt, font_size=9, align="left", text_wrap=True,
                 bg_color=t.card, font_color=t.ink, indent=1)
        cv.hline(r_cur + 1, 7, 8, t.line)
        r_cur += 2
    cv.box(3, 7, r_cur - 1, 8, t.line)

    # Sidebar: YOU HAVE PLANTED counter card (rows 16..20, cols 7..8)
    rp = r_cur + 1
    cv.merge(rp, 7, rp, 8, "🌻  YOU HAVE PLANTED:", bold=True, font_size=10, align="center",
             bg_color=t.primary, font_color=t.on_primary)
    chk_rng = rng(r0, 1, r0 + total_rows - 1, 1)
    goal_rng = rng(r0, 2, r0 + total_rows - 1, 2)
    cv.merge(rp + 1, 7, rp + 3, 7, f'=COUNTIFS({goal_rng},"?*",{chk_rng},TRUE)', bold=True,
             font_size=28, align="center", bg_color=t.card, font_color=t.primary_dark,
             font_name=t.font_title)
    st5 = "=INDEX(_Sprites!$A$1:$A$6,6)" if offline_sprites else '=_xlfn.IMAGE(CFG_IMG_BASE&"stage_5.png")'
    cv.merge(rp + 1, 8, rp + 3, 8, st5, align="center", bg_color=t.card)
    cv.merge(rp + 4, 7, rp + 4, 8,
             f'="trên tổng "&COUNTIF({goal_rng},"?*")&" mục tiêu đã đặt"',
             font_size=9, italic=True, align="center", bg_color=t.soft, font_color=t.ink)
    cv.box(rp, 7, rp + 4, 8, t.line)

    _finish_sheet(ws, cv, t.primary)


# =========================================================================== #
#  1B. Template 1 — 📊 Annual Overview
# =========================================================================== #
def build_annual_overview_sheet(wb, styles: Styles, tr: TrackerRefs):
    name = "📊 Annual Overview"
    t = styles.t
    ws = wb.add_worksheet(name)
    cv = Canvas(wb, ws, styles, name)
    q = qs(name)

    cv.col(0, 2.5)
    widths = [15, 13, 14, 13, 13, 16, 2.2, 16, 16, 16, 16]
    for i, w in enumerate(widths, start=1):
        cv.col(i, w)
    cv.col(12, 2.5)

    cv.row(0, 12)
    cv.row(1, 32)
    cv.row(2, 10)
    cv.row(3, 20)
    cv.row(4, 34)
    cv.row(5, 12)
    cv.row(6, 24)
    cv.row(7, 22)

    cv.merge(1, 1, 1, 11, f"{t.emoji}  ANNUAL HABIT OVERVIEW — TỔNG KẾT NĂM",
             font_name=t.font_title, font_size=15, bold=True, align="center",
             bg_color=t.primary, font_color=t.on_primary)
    cv.box(1, 1, 1, 11, t.line)

    # 12-month table rows 8..19 (October = row 17 dynamically linked!)
    r0 = 8
    r1 = r0 + 11
    pct_r = rng(r0, 2, r1, 2)
    grn_r = rng(r0, 3, r1, 3)
    prf_r = rng(r0, 4, r1, 4)
    str_r = rng(r0, 5, r1, 5)

    kpi_card(cv, 3, 1, 2, "ANNUAL AVG COMPLETION", f'=IFERROR(AVERAGEIF({pct_r},">0"),0)',
             num_format="0.0%", value_color=t.primary_dark)
    kpi_card(cv, 3, 3, 4, "TOTAL FLOWERS GROWN", f"=SUM({grn_r})", num_format='#,##0" 🌻"',
             value_color=t.primary_dark)
    kpi_card(cv, 3, 5, 6, "PERFECT 100% DAYS", f"=SUM({prf_r})", num_format='#,##0" ngày"',
             value_color=t.ink)
    kpi_card(cv, 3, 8, 9, "LONGEST YEAR STREAK", f"=MAX({str_r})", num_format='0" ngày 🔥"',
             value_color=t.streak_hi)
    kpi_card(cv, 3, 10, 11, "ACTIVE HABITS", f"={tr.a('hc')}", num_format='0" thói quen"',
             value_color=t.ink)

    cv.merge(6, 1, 6, 6, "📅  MONTHLY PERFORMANCE LOG (Tháng 10 tự động liên kết!)",
             bold=True, font_size=9.5, align="left", indent=1, bg_color=t.primary, font_color=t.on_primary)
    hdrs = ["Tháng", "Hoàn thành %", "Hoa đã nở", "Ngày 100%", "Best Streak", "Đánh giá"]
    for i, h in enumerate(hdrs, start=1):
        cv.put(7, i, h, bold=True, font_size=9, align="center", bg_color=t.soft, font_color=t.ink)

    hist = [
        (0.74, 18, 9, 14), (0.78, 19, 10, 16), (0.81, 22, 12, 19), (0.76, 19, 8, 15),
        (0.84, 24, 14, 21), (0.80, 21, 11, 17), (0.86, 25, 15, 22), (0.83, 23, 13, 18),
        (0.88, 26, 16, 24), None, ("", "", "", ""), ("", "", "", ""),
    ]
    for idx, mname in enumerate(MONTHS_EN):
        rr = r0 + idx
        cv.row(rr, 22)
        bg = t.warn_fill if idx == 9 else (t.card if idx % 2 == 0 else t.page)
        cv.put(rr, 1, f"{mname}" + ("  ★" if idx == 9 else ""), bold=(idx == 9), font_size=9.5,
               align="left", indent=1, bg_color=bg, font_color=t.primary_dark if idx == 9 else t.ink)
        if idx == 9:
            cv.put(rr, 2, f"={tr.a('overall')}", bold=True, align="center", num_format="0.0%", bg_color=bg)
            cv.put(rr, 3, f"={tr.a('grown')}", bold=True, align="center", num_format="0", bg_color=bg)
            cv.put(rr, 4, f"={tr.a('perfect')}", bold=True, align="center", num_format="0", bg_color=bg)
            cv.put(rr, 5, f"={tr.a('best')}", bold=True, align="center", num_format="0", bg_color=bg)
        else:
            p, g, pf, st = hist[idx]
            cv.put(rr, 2, p, align="center", num_format="0.0%", bg_color=bg, font_color=t.ink)
            cv.put(rr, 3, g, align="center", num_format="0", bg_color=bg, font_color=t.ink)
            cv.put(rr, 4, pf, align="center", num_format="0", bg_color=bg, font_color=t.ink)
            cv.put(rr, 5, st, align="center", num_format="0", bg_color=bg, font_color=t.ink)
        pc = cell(rr, 2)
        cv.put(rr, 6, f'=IF({pc}="","⏳ Sắp tới",IF({pc}>=0.85,"🌻 Xuất sắc",IF({pc}>=0.7,"🌱 Ổn định","💪 Cố lên")))',
               align="center", font_size=9, bg_color=bg, font_color=t.ink)
    cv.grid(7, 1, r1, 6, t.line)
    cv.box(6, 1, r1, 6, t.line)
    ws.conditional_format(pct_r, {"type": "data_bar", "bar_color": t.bar, "bar_solid": True,
                                  "min_type": "num", "min_value": 0, "max_type": "num", "max_value": 1})

    # Column chart on right (rows 6..19, cols 8..11)
    ch = wb.add_chart({"type": "column"})
    ch.add_series({
        "name": "Monthly Completion %",
        "categories": f"={q}!{rng(r0, 1, r1, 1)}",
        "values": f"={q}!{pct_r}",
        "fill": {"color": t.primary},
        "border": {"none": True},
        "gap": 70,
    })
    ch.set_title({"name": "MONTHLY COMPLETION TREND (JAN – DEC)",
                  "name_font": {"name": t.font, "size": 10, "bold": True, "color": t.ink}})
    ch.set_y_axis({"min": 0, "max": 1, "major_unit": 0.2, "num_format": "0%",
                   "num_font": axis_font(t), "line": {"none": True},
                   "major_gridlines": {"visible": True, "line": {"color": t.line, "dash_type": "dash"}}})
    ch.set_x_axis({"num_font": axis_font(t, 8), "line": {"color": t.line}})
    ch.set_legend({"none": True})
    ch.set_chartarea({"border": {"color": t.line, "width": 0.75}, "fill": {"color": t.card}})
    place_chart(cv, ch, 6, 8, r1, 11)

    # Quarterly reflection cards below (rows 21..25)
    cv.row(20, 12)
    cv.row(21, 22)
    for rr in range(22, 26):
        cv.row(rr, 22)
    quarters = [
        (1, 2, "Q1  (Jan – Mar)", "Xây nền tảng kỷ luật buổi sáng & duy trì thói quen đọc sách."),
        (3, 5, "Q2  (Apr – Jun)", "Tăng cường thể lực, duy trì 16+ buổi tập mỗi tháng."),
        (6, 8, "Q3  (Jul – Sep)", "Cân bằng công việc, giấc ngủ 8 tiếng & tiết kiệm ổn định."),
        (9, 11, "Q4  (Oct – Dec)", "Bứt phá mục tiêu cuối năm & tổng kết hành trình 12 tháng."),
    ]
    for c1, c2, qt, note in quarters:
        cv.merge(21, c1, 21, c2, f"✨  {qt}", bold=True, font_size=9.5, align="center",
                 bg_color=t.primary, font_color=t.on_primary)
        cv.merge(22, c1, 25, c2, note, font_size=9, align="left", text_wrap=True,
                 bg_color=t.card, font_color=t.ink, indent=1)
        cv.box(21, c1, 25, c2, t.line)

    _finish_sheet(ws, cv, t.primary_dark)


# =========================================================================== #
#  2. Template 2 (Cactus) — 📝 Reflection & Notes
# =========================================================================== #
def build_reflection_notes_sheet(wb, styles: Styles, tr: TrackerRefs):
    name = "📝 Reflection & Notes"
    t = styles.t
    ws = wb.add_worksheet(name)
    cv = Canvas(wb, ws, styles, name)

    cv.col(0, 2.5)
    cv.col(1, 16)
    cv.col(2, 16)
    cv.col(3, 24)
    cv.col(4, 2.2)
    cv.col(5, 16)
    cv.col(6, 16)
    cv.col(7, 24)
    cv.col(8, 2.5)

    cv.row(0, 12)
    cv.row(1, 32)
    cv.row(2, 10)
    cv.row(3, 20)
    cv.row(4, 34)
    cv.row(5, 12)

    cv.merge(1, 1, 1, 7, "🌵  MONTHLY REFLECTION & WEEKLY CHECK-IN", font_name=t.font_title,
             font_size=15, bold=True, align="center", bg_color=t.primary, font_color=t.on_primary)
    cv.box(1, 1, 1, 7, t.line)

    kpi_card(cv, 3, 1, 1, "OVERALL %", f"={tr.a('overall')}", num_format="0.0%", value_color=t.primary_dark)
    kpi_card(cv, 3, 2, 3, "CACTI BLOOMED (≥75%)", f"={tr.a('grown')}", num_format='0" 🌵"', value_color=t.primary_dark)
    kpi_card(cv, 3, 5, 6, "PERFECT 100% DAYS", f"={tr.a('perfect')}", num_format='0" ngày"', value_color=t.ink)
    kpi_card(cv, 3, 7, 7, "LONGEST STREAK", f"={tr.a('best')}", num_format='0" ngày 🔥"', value_color=t.streak_hi)

    # 2x2 Reflection Cards
    cards = [
        (6, 1, 3, "🌟  THÀNH TỰU NỔI BẬT (MONTHLY WINS)", t.week_head[0], t.week_on[0], [
            "• Duy trì tập thể dục đều đặn 5 buổi/tuần mà không bỏ giữa chừng.",
            "• Giảm rõ rệt đồ ăn nhanh & tự nấu ăn tối 4 ngày/tuần.",
            "• Hoàn thành 100% mục tiêu uống 2L nước trong 3 tuần liên tiếp.",
            "",
        ]),
        (6, 5, 7, "🧱  THỬ THÁCH & ĐIỂM CẦN CẢI THIỆN (CHALLENGES)", t.week_head[1], t.week_on[1], [
            "• Tuần 3 công việc tăng ca nên giấc ngủ bị trễ sau 23h30.",
            "• Dễ quên viết nhật ký vào cuối tuần khi đi chơi về muộn.",
            "• Cần đặt nhắc nhở điện thoại lúc 22h15 để tắt màn hình.",
            "",
        ]),
        (12, 1, 3, "🌵  THÓI QUEN ĐÃ VÀO GUỒNG (HABITS THAT STUCK)", t.week_head[2], t.week_on[2], [
            "• Uống 1 cốc nước ấm ngay sau khi thức dậy — cực kỳ dễ duy trì!",
            "• Đọc 15–20 phút sách giấy trước giờ ngủ giúp ngủ sâu hơn hẳn.",
            "",
        ]),
        (12, 5, 7, "🎯  ĐIỀU CHỈNH CHO THÁNG TỚI (NEXT MONTH FOCUS)", t.week_head[3], t.week_on[3], [
            "• Thêm thói quen đi bộ 15 phút buổi chiều để giải tỏa căng thẳng.",
            "• Đặt mục tiêu tăng số ngày nở hoa lên tối thiểu 25/30 ngày!",
            "",
        ]),
    ]
    for r_s, c1, c2, title, hbg, hfg, lines in cards:
        cv.row(r_s, 23)
        cv.merge(r_s, c1, r_s, c2, title, bold=True, font_size=9.5, align="left", indent=1,
                 bg_color=hbg, font_color=hfg)
        for i in range(4):
            rr = r_s + 1 + i
            cv.row(rr, 24)
            txt = lines[i] if i < len(lines) else ""
            cv.merge(rr, c1, rr, c2, txt, font_size=9, align="left", indent=1, text_wrap=True,
                     bg_color=t.card, font_color=t.ink)
            cv.hline(rr, c1, c2, t.line)
        cv.box(r_s, c1, r_s + 4, c2, t.line)
    cv.row(11, 10)
    cv.row(17, 12)

    # Weekly Check-in Table (rows 18..24) linked directly to Week 1..5 %
    rw = 18
    cv.row(rw, 24)
    cv.row(rw + 1, 22)
    cv.merge(rw, 1, rw, 7, "🗓️  WEEKLY CHECK-IN • ĐÁNH GIÁ TỪNG TUẦN (Tự liên kết %)",
             bold=True, font_size=9.5, align="left", indent=1, bg_color=t.primary, font_color=t.on_primary)
    cv.put(rw + 1, 1, "Tuần", bold=True, font_size=9, align="center", bg_color=t.soft)
    cv.put(rw + 1, 2, "Hoàn thành %", bold=True, font_size=9, align="center", bg_color=t.soft)
    cv.put(rw + 1, 3, "Tâm điểm tuần (Weekly Focus)", bold=True, font_size=9, align="center", bg_color=t.soft)
    cv.merge(rw + 1, 5, rw + 1, 7, "Ghi chú & Bài học rút ra", bold=True, font_size=9, align="center", bg_color=t.soft)
    cv.put(rw + 1, 4, "", bg_color=t.soft)

    wk_notes = [
        ("Khởi động nhịp sinh học đều đặn", "Khởi đầu cực sung sức! Giữ vững giờ ngủ trước 23h."),
        ("Tối ưu buổi sáng năng suất", "Chuẩn bị quần áo tập từ tối hôm trước giúp không bỏ buổi nào."),
        ("Vượt qua tuần bận rộn", "Có 2 ngày bị tụt nhưng đã quay lại nhịp rất nhanh — không bỏ cuộc!"),
        ("Bứt phá kỷ lục streak", "Cảm nhận rõ sự thay đổi về năng lượng và tinh thần."),
        ("Tổng kết & ăn mừng thành quả", "Tự thưởng 1 buổi cafe thư giãn cuối tháng 🌵✨"),
    ]
    for w in range(5):
        rr = rw + 2 + w
        cv.row(rr, 25)
        cv.put(rr, 1, f"WEEK {w + 1}", bold=True, font_size=9.5, align="center",
               bg_color=t.week_head[w], font_color=t.week_on[w])
        cv.put(rr, 2, f"={tr.q}!{acell(3, C_WK0 + w)}", bold=True, font_size=10, align="center",
               num_format="0%", bg_color=t.week_tint[w], font_color=t.ink)
        cv.merge(rr, 3, rr, 4, wk_notes[w][0], font_size=9, align="left", indent=1,
                 bg_color=t.card, font_color=t.ink)
        cv.merge(rr, 5, rr, 7, wk_notes[w][1], font_size=9, align="left", indent=1, text_wrap=True,
                 bg_color=t.card, font_color=t.ink)
        cv.hline(rr, 1, 7, t.line)
    cv.box(rw, 1, rw + 6, 7, t.line)

    _finish_sheet(ws, cv, t.primary_dark)


# =========================================================================== #
#  3. Template 3 (Rainbow) — 📈 Analytics
# =========================================================================== #
def build_rainbow_analytics_sheet(wb, styles: Styles, tr: TrackerRefs):
    name = "📈 Analytics"
    t = styles.t
    ws = wb.add_worksheet(name)
    cv = Canvas(wb, ws, styles, name)
    q = qs(name)

    cv.col(0, 2.5)
    widths = [34, 10, 10, 12, 11, 11, 13, 2.2, 14, 14, 14, 14]
    for i, w in enumerate(widths, start=1):
        cv.col(i, w)
    cv.col(13, 2.5)
    # Hidden cols 20..50 for exact Day-of-Week computation (1=Mon..7=Sun)
    cv.cols(20, 50, 5, hidden=True)

    cv.row(0, 12)
    cv.row(1, 32)
    cv.row(2, 10)
    cv.row(3, 20)
    cv.row(4, 34)
    cv.row(5, 12)
    cv.row(6, 24)
    cv.row(7, 22)

    cv.merge(1, 1, 1, 12, "🌈  HABIT ANALYTICS & PERFORMANCE LEADERBOARD", font_name=t.font_title,
             font_size=15, bold=True, align="center", bg_color=t.primary, font_color=t.on_primary)
    cv.box(1, 1, 1, 12, t.line)

    # Hidden day-of-week helper (row 1: weekday 1..7, row 2: pct)
    for k in range(1, 32):
        hc = 20 + k - 1
        dc = f"{tr.q}!{acell(R_DAY, day_col(k))}"
        pc = f"{tr.q}!{acell(R_PCT, day_col(k))}"
        cv.put(1, hc, f'=IF({dc}="","",WEEKDAY(DATE({tr.a("y")},{tr.a("m")},{k}),2))')
        cv.put(2, hc, f'=IF({dc}="","",{pc})')
    wd_rng = rng(1, 20, 1, 50)
    wp_rng = rng(2, 20, 2, 50)

    # Habit leaderboard rows 8..27 (20 rows mirroring tracker)
    r0 = 8
    r1 = r0 + N_HABITS - 1
    rc = tr.right_cols
    pct_col = rng(r0, 4, r1, 4)

    kpi_card(cv, 3, 1, 2, "MONTHLY COMPLETION", f"={tr.a('overall')}", num_format="0.0%", value_color=t.primary_dark)
    kpi_card(cv, 3, 3, 4, "TOTAL CHECKS DONE", f"={tr.a('tdone')}", num_format="#,##0", value_color=t.ink)
    kpi_card(cv, 3, 5, 7, "TOP HABIT SCORE", f"=IFERROR(MAX({pct_col}),0)", num_format="0%", value_color=t.streak_hi)
    kpi_card(cv, 3, 9, 10, "STAR JARS FILLED", f"={tr.a('grown')}", num_format='0" ⭐"', value_color=t.primary_dark)
    kpi_card(cv, 3, 11, 12, "BEST STREAK", f"={tr.a('best')}", num_format='0" ngày 🔥"', value_color=t.streak_hi)

    cv.merge(6, 1, 6, 7, "🏆  HABIT-BY-HABIT LEADERBOARD (Tự động cập nhật từ Dashboard)",
             bold=True, font_size=9.5, align="left", indent=1, bg_color=t.primary, font_color=t.on_primary)
    for i, h in enumerate(["Thói quen", "Mục tiêu", "Đã làm", "Tỷ lệ %", "Streak HT", "Max Streak", "Xếp hạng"], start=1):
        cv.put(7, i, h, bold=True, font_size=8.5, align="center", bg_color=t.soft, font_color=t.ink)

    for i in range(N_HABITS):
        rr = r0 + i
        src_r = R_H0 + i
        cv.row(rr, 21)
        bg = t.card if i % 2 == 0 else t.page
        snm = f"{tr.q}!{cell(src_r, C_NAME)}"
        cv.put(rr, 1, f'=IF({snm}="","",{snm})', align="left", indent=1, font_size=9, bg_color=bg, font_color=t.ink)
        cv.put(rr, 2, f'=IF({snm}="","",{tr.q}!{cell(src_r, 92)})', align="center", font_size=9, bg_color=bg)
        cv.put(rr, 3, f'=IF({snm}="","",{tr.q}!{cell(src_r, 91)})', align="center", font_size=9, bg_color=bg)
        cv.put(rr, 4, f'=IF({snm}="","",{tr.q}!{cell(src_r, rc["progress"])})', align="center", bold=True,
               font_size=9, num_format="0%", bg_color=bg, font_color=t.primary_dark)
        cv.put(rr, 5, f'=IF({snm}="","",{tr.q}!{cell(src_r, rc["cur"])})', align="center", font_size=9, bg_color=bg)
        cv.put(rr, 6, f'=IF({snm}="","",{tr.q}!{cell(src_r, rc["long"])})', align="center", font_size=9, bg_color=bg)
        pc = cell(rr, 4)
        cv.put(rr, 7, f'=IF({snm}="","",IF({pc}>=0.9,"🥇 Xuất sắc",IF({pc}>=0.75,"⭐ Rất tốt",IF({pc}>=0.5,"🌱 Ổn định","⚡ Tập trung"))))',
               align="center", font_size=8.5, bg_color=bg, font_color=t.ink)
    cv.grid(7, 1, r1, 7, t.line)
    cv.box(6, 1, r1, 7, t.line)
    ws.conditional_format(pct_col, {"type": "data_bar", "bar_color": t.bar, "bar_solid": True,
                                    "min_type": "num", "min_value": 0, "max_type": "num", "max_value": 1})

    # Right top (rows 6..16, cols 9..12): Horizontal Bar Chart of top 10 habits
    hb = wb.add_chart({"type": "bar"})
    hb.add_series({
        "name": "Completion %",
        "categories": f"={q}!{rng(r0, 1, r0 + 9, 1)}",
        "values": f"={q}!{rng(r0, 4, r0 + 9, 4)}",
        "fill": {"color": "#77BBD9"},
        "border": {"none": True},
    })
    hb.set_title({"name": "HABIT COMPLETION RATE (%)",
                  "name_font": {"name": t.font, "size": 9.5, "bold": True, "color": t.ink}})
    hb.set_x_axis({"min": 0, "max": 1, "major_unit": 0.25, "num_format": "0%",
                   "num_font": axis_font(t), "major_gridlines": {"visible": True, "line": {"color": t.line, "dash_type": "dash"}}})
    hb.set_y_axis({"reverse": True, "num_font": axis_font(t, 8), "line": {"color": t.line}})
    hb.set_legend({"none": True})
    hb.set_chartarea({"border": {"color": t.line, "width": 0.75}, "fill": {"color": t.card}})
    place_chart(cv, hb, 6, 9, 16, 12)

    # Right bottom (rows 18..27, cols 9..12): Day-of-Week table + Column Chart
    rd0 = 18
    cv.merge(rd0, 9, rd0, 12, "📅  HIỆU SUẤT THEO THỨ TRONG TUẦN (MON–SUN)", bold=True, font_size=9,
             align="center", bg_color=t.primary, font_color=t.on_primary)
    # Put 7-day table in hidden cols 52..53 (or right above chart? Put table in rows 29..36 cols 1..7 + chart in 18..27 cols 9..12!)
    dow_labels = ["Thứ 2 (Mon)", "Thứ 3 (Tue)", "Thứ 4 (Wed)", "Thứ 5 (Thu)",
                  "Thứ 6 (Fri)", "Thứ 7 (Sat)", "Chủ nhật (Sun)"]
    r_dt = r1 + 2
    cv.row(r_dt - 1, 10)
    cv.row(r_dt, 23)
    cv.row(r_dt + 1, 21)
    cv.merge(r_dt, 1, r_dt, 7, "📅  DAY-OF-WEEK PERFORMANCE BREAKDOWN (Thứ nào bạn kỷ luật nhất?)",
             bold=True, font_size=9.5, align="left", indent=1, bg_color=t.primary, font_color=t.on_primary)
    for i, dl in enumerate(dow_labels, start=1):
        cv.put(r_dt + 1, i, dl, bold=True, font_size=8.5, align="center", bg_color=t.soft, font_color=t.ink)
    cv.row(r_dt + 2, 26)
    for i in range(1, 8):
        cv.put(r_dt + 2, i, f'=IFERROR(AVERAGEIF({wd_rng},{i},{wp_rng}),0)', bold=True, font_size=11,
               align="center", num_format="0%", bg_color=t.card, font_color=t.primary_dark)
    cv.grid(r_dt + 1, 1, r_dt + 2, 7, t.line)
    cv.box(r_dt, 1, r_dt + 2, 7, t.line)
    ws.conditional_format(rng(r_dt + 2, 1, r_dt + 2, 7),
                          {"type": "3_color_scale", "min_type": "num", "min_value": 0.4,
                           "mid_type": "num", "mid_value": 0.75, "max_type": "num", "max_value": 1.0,
                           "min_color": "#FAD3E4", "mid_color": "#FCE2B8", "max_color": "#C8EDD5"})

    dc_ch = wb.add_chart({"type": "column"})
    dow_cols = ["#77BBD9", "#7ECF9B", "#EB9BBF", "#F2BD6B", "#A9C96E", "#A594F9", "#E0A899"]
    dc_ch.add_series({
        "name": "Avg %",
        "categories": f"={q}!{rng(r_dt + 1, 1, r_dt + 1, 7)}",
        "values": f"={q}!{rng(r_dt + 2, 1, r_dt + 2, 7)}",
        "points": [{"fill": {"color": col}, "border": {"none": True}} for col in dow_cols],
        "gap": 55,
    })
    dc_ch.set_title({"name": "AVG COMPLETION BY DAY OF WEEK",
                     "name_font": {"name": t.font, "size": 9.5, "bold": True, "color": t.ink}})
    dc_ch.set_y_axis({"min": 0, "max": 1, "major_unit": 0.25, "num_format": "0%",
                      "num_font": axis_font(t), "line": {"none": True},
                      "major_gridlines": {"visible": True, "line": {"color": t.line, "dash_type": "dash"}}})
    dc_ch.set_x_axis({"num_font": axis_font(t, 7.5), "line": {"color": t.line}})
    dc_ch.set_legend({"none": True})
    dc_ch.set_chartarea({"border": {"color": t.line, "width": 0.75}, "fill": {"color": t.card}})
    place_chart(cv, dc_ch, 18, 9, r_dt + 2, 12)

    _finish_sheet(ws, cv, t.primary_dark)


# =========================================================================== #
#  4A. Template 4 (Sage Botanical) — 💰 Monthly Budget (Ref 5 Ultimate Budget!)
# =========================================================================== #
def build_monthly_budget_sheet(wb, styles: Styles) -> dict:
    name = "💰 Monthly Budget"
    t = styles.t
    ws = wb.add_worksheet(name)
    cv = Canvas(wb, ws, styles, name)
    q = qs(name)

    SAGE, SAND, CORAL, SKY = "#9FB8AD", "#E8D5B7", "#E0A899", "#B6C9DF"
    SAGE_L, SAND_L, CORAL_L, SKY_L = "#E9F0EC", "#F8F1E4", "#F8EAE6", "#EBF1F8"
    VND = '#,##0" ₫"'

    # Columns 0..13: 0 gutter | 1..3 left summaries | 4 gap | 5..8 middle charts | 9 gap | 10..12 right goals/bills | 13 gutter
    cv.col(0, 2.2)
    cv.col(1, 18)
    cv.col(2, 16.5)
    cv.col(3, 14)
    cv.col(4, 2.0)
    cv.col(5, 13)
    cv.col(6, 13)
    cv.col(7, 13)
    cv.col(8, 13)
    cv.col(9, 2.0)
    cv.col(10, 17)
    cv.col(11, 13.5)
    cv.col(12, 13.5)
    cv.col(13, 2.2)

    cv.row(0, 10)
    cv.row(1, 32)
    cv.row(2, 10)
    cv.row(3, 20)
    cv.row(4, 30)
    cv.row(5, 10)

    cv.merge(1, 1, 1, 12, "🌿  MONTHLY BUDGET PLANNER — QUẢN LÝ TÀI CHÍNH CÁ NHÂN",
             font_name=t.font_title, font_size=15, bold=True, align="center",
             bg_color=SAGE, font_color="#FFFFFF")
    cv.box(1, 1, 1, 12, t.line)

    # Transaction Log bounds (will be placed at rows 28..52)
    R_LOG_H = 27
    R_LOG0 = 28
    R_LOG1 = 52
    cat_rng = rng(R_LOG0, 2, R_LOG1, 2)
    amt_rng = rng(R_LOG0, 6, R_LOG1, 6)
    typ_rng = rng(R_LOG0, 8, R_LOG1, 8)

    # Cash Flow Summary cells (rows 8..11, col 2)
    cf_inc = acell(8, 2)
    cf_exp = acell(9, 2)
    cf_sav = acell(10, 2)
    cf_lft = acell(11, 2)

    # 4 Top KPI cards
    kpi_card(cv, 3, 1, 3, "TOTAL INCOME • TỔNG THU", f"={cf_inc}", num_format=VND,
             label_fill=SAGE_L, value_color="#3E6B58", value_size=16)
    kpi_card(cv, 3, 5, 6, "TOTAL EXPENSES • CHI TIÊU", f"={cf_exp}", num_format=VND,
             label_fill=CORAL_L, value_color="#A85D4C", value_size=16)
    kpi_card(cv, 3, 7, 8, "TOTAL SAVINGS • TIẾT KIỆM", f"={cf_sav}", num_format=VND,
             label_fill=SAND_L, value_color="#8C6A35", value_size=16)
    kpi_card(cv, 3, 10, 12, "LEFT TO SPEND • CÒN LẠI", f"={cf_lft}", num_format=VND,
             label_fill=SKY_L, value_color="#496588", value_size=16)

    # ---- LEFT COLUMN: CASH FLOW SUMMARY (rows 6..11) + BUDGET VS ACTUAL TABLE (rows 13..24) ----
    for r in range(6, 26):
        cv.row(r, 22)
    cv.row(12, 10)
    cv.row(25, 12)

    cv.merge(6, 1, 6, 3, "CASH FLOW SUMMARY", bold=True, font_size=9.5, align="center",
             bg_color=SAGE, font_color="#FFFFFF")
    cv.put(7, 1, "Hạng mục", bold=True, font_size=8.5, align="center", bg_color=SAGE_L)
    cv.put(7, 2, "Số tiền", bold=True, font_size=8.5, align="center", bg_color=SAGE_L)
    cv.put(7, 3, "% Thu nhập", bold=True, font_size=8.5, align="center", bg_color=SAGE_L)

    cf_rows = [
        (8, "Total Income", f'=SUMIF({typ_rng},"Income",{amt_rng})', f"=IFERROR({cf_inc}/{cf_inc},0)", t.card),
        (9, "Total Expenses", f'=SUMIF({typ_rng},"Expense",{amt_rng})', f"=IFERROR({cf_exp}/{cf_inc},0)", t.card),
        (10, "Total Savings", f'=SUMIF({typ_rng},"Savings",{amt_rng})', f"=IFERROR({cf_sav}/{cf_inc},0)", t.card),
        (11, "Left to Spend", f"=MAX(0,{cf_inc}-{cf_exp}-{cf_sav})", f"=IFERROR({cf_lft}/{cf_inc},0)", SAGE_L),
    ]
    for rr, lab, f1, f2, bg in cf_rows:
        cv.put(rr, 1, lab, bold=(rr == 11), font_size=9, align="left", indent=1, bg_color=bg)
        cv.put(rr, 2, f1, bold=True, font_size=9.5, align="right", num_format=VND, bg_color=bg)
        cv.put(rr, 3, f2, bold=(rr == 11), font_size=9, align="center", num_format="0.0%", bg_color=bg)
    cv.grid(7, 1, 11, 3, t.line)
    cv.box(6, 1, 11, 3, t.line)

    # Budget vs Actual Table (rows 13..21)
    cv.merge(13, 1, 13, 3, "BUDGET VS ACTUAL • NGÂN SÁCH", bold=True, font_size=9.5, align="center",
             bg_color=CORAL, font_color="#FFFFFF")
    cv.put(14, 1, "Nhóm chi", bold=True, font_size=8.5, align="center", bg_color=CORAL_L)
    cv.put(14, 2, "Dự kiến", bold=True, font_size=8.5, align="center", bg_color=CORAL_L)
    cv.put(14, 3, "Thực tế", bold=True, font_size=8.5, align="center", bg_color=CORAL_L)

    cats = [
        ("Bills & Rent", 5500000),
        ("Food & Groceries", 3500000),
        ("Transport & Daily", 1500000),
        ("Wants & Fun", 2000000),
        ("Self-Growth", 1500000),
        ("Savings", 6000000),
    ]
    r_b0 = 15
    for idx, (cat, bud) in enumerate(cats):
        rr = r_b0 + idx
        bg = t.card if idx % 2 == 0 else t.page
        cv.put(rr, 1, cat, font_size=9, align="left", indent=1, bg_color=bg)
        cv.put(rr, 2, bud, font_size=9, align="right", num_format=VND, bg_color=bg)
        cv.put(rr, 3, f'=SUMIF({cat_rng},{cell(rr, 1)},{amt_rng})', bold=True, font_size=9,
               align="right", num_format=VND, bg_color=bg)
    r_btot = r_b0 + len(cats)   # 21
    cv.put(r_btot, 1, "TOTAL", bold=True, font_size=9, align="left", indent=1, bg_color=CORAL_L)
    cv.put(r_btot, 2, f"=SUM({rng(r_b0, 2, r_btot - 1, 2)})", bold=True, font_size=9, align="right",
           num_format=VND, bg_color=CORAL_L)
    cv.put(r_btot, 3, f"=SUM({rng(r_b0, 3, r_btot - 1, 3)})", bold=True, font_size=9, align="right",
           num_format=VND, bg_color=CORAL_L)
    cv.grid(14, 1, r_btot, 3, t.line)
    cv.box(13, 1, r_btot, 3, t.line)

    # Budget health mini banner (rows 23..24, cols 1..3)
    cv.merge(23, 1, 23, 3, "SAVINGS RATE • TỶ LỆ TIẾT KIỆM", bold=True, font_size=8.5, align="center",
             bg_color=SAND_L, font_color=t.ink)
    sav_rate_addr = acell(24, 1)
    cv.merge(24, 1, 24, 3, f"=IFERROR({cf_sav}/{cf_inc},0)", bold=True, font_size=14, align="center",
             num_format='0.0%" thu nhập"', bg_color=t.card, font_color="#3E6B58", font_name=t.font_title)
    cv.box(23, 1, 24, 3, t.line)

    # ---- MIDDLE COLUMN: CASH FLOW DONUT (rows 6..14) + BUDGET VS ACTUAL BAR CHART (rows 15..24) ----
    # Donut over Expenses, Savings, Left to Spend (sums to 100% of Income!)
    dch = wb.add_chart({"type": "doughnut"})
    dch.add_series({
        "name": "Cash Flow",
        "categories": f"={q}!{rng(9, 1, 11, 1)}",
        "values": f"={q}!{rng(9, 2, 11, 2)}",
        "points": [
            {"fill": {"color": CORAL}, "border": {"color": "#FFFFFF", "width": 1.5}},
            {"fill": {"color": SAND}, "border": {"color": "#FFFFFF", "width": 1.5}},
            {"fill": {"color": SAGE}, "border": {"color": "#FFFFFF", "width": 1.5}},
        ],
        "data_labels": {"percentage": True, "font": {"name": t.font, "size": 8.5, "bold": True, "color": t.ink}},
    })
    dch.set_hole_size(58)
    dch.set_title({"name": "CASH FLOW OVERVIEW",
                   "name_font": {"name": t.font, "size": 9.5, "bold": True, "color": t.ink}})
    dch.set_legend({"position": "right", "font": {"name": t.font, "size": 8.5, "color": t.ink}})
    dch.set_chartarea({"border": {"color": t.line, "width": 0.75}, "fill": {"color": t.card}})
    place_chart(cv, dch, 6, 5, 14, 8)

    bch = wb.add_chart({"type": "column"})
    bch.add_series({
        "name": "Budget",
        "categories": f"={q}!{rng(r_b0, 1, r_btot - 1, 1)}",
        "values": f"={q}!{rng(r_b0, 2, r_btot - 1, 2)}",
        "fill": {"color": SAGE},
        "border": {"none": True},
    })
    bch.add_series({
        "name": "Actual",
        "categories": f"={q}!{rng(r_b0, 1, r_btot - 1, 1)}",
        "values": f"={q}!{rng(r_b0, 3, r_btot - 1, 3)}",
        "fill": {"color": CORAL},
        "border": {"none": True},
    })
    bch.set_title({"name": "BUDGET VS ACTUAL",
                   "name_font": {"name": t.font, "size": 9.5, "bold": True, "color": t.ink}})
    bch.set_y_axis({"num_format": "#,##0", "num_font": axis_font(t, 7.5), "line": {"none": True},
                    "major_gridlines": {"visible": True, "line": {"color": t.line, "dash_type": "dash"}}})
    bch.set_x_axis({"num_font": axis_font(t, 7.5), "line": {"color": t.line}})
    bch.set_legend({"position": "top", "font": {"name": t.font, "size": 8.5, "color": t.ink}})
    bch.set_chartarea({"border": {"color": t.line, "width": 0.75}, "fill": {"color": t.card}})
    place_chart(cv, bch, 15, 5, 24, 8)

    # ---- RIGHT COLUMN: SAVINGS GOALS (rows 6..14) + BILLS TRACKER (rows 16..24) ----
    cv.merge(6, 10, 6, 12, "SAVINGS GOALS • MỤC TIÊU TIẾT KIỆM", bold=True, font_size=9.5,
             align="center", bg_color=SAND, font_color=t.ink)
    cv.put(7, 10, "Mục tiêu", bold=True, font_size=8.5, align="center", bg_color=SAND_L)
    cv.put(7, 11, "Đã tích lũy", bold=True, font_size=8.5, align="center", bg_color=SAND_L)
    cv.put(7, 12, "Mục tiêu", bold=True, font_size=8.5, align="center", bg_color=SAND_L)
    goals = [
        ("Quỹ dự phòng", 18000000, 30000000),
        ("Du lịch cuối năm", 6500000, 12000000),
        ("Quỹ học tập", 4000000, 8000000),
        ("Đầu tư dài hạn", 12000000, 40000000),
        ("Nâng cấp thiết bị", 3500000, 10000000),
    ]
    for i, (gn, sv, tg) in enumerate(goals):
        rr = 8 + i
        bg = t.card if i % 2 == 0 else t.page
        cv.put(rr, 10, gn, font_size=9, align="left", indent=1, bg_color=bg)
        cv.put(rr, 11, sv, font_size=9, align="right", num_format=VND, bg_color=bg)
        cv.put(rr, 12, tg, font_size=9, align="right", num_format=VND, bg_color=bg)
    cv.put(13, 10, "OVERALL PROGRESS", bold=True, font_size=8.5, align="left", indent=1, bg_color=SAGE_L)
    goal_prog_addr = acell(13, 11)
    cv.merge(13, 11, 13, 12, f"=IFERROR(SUM({rng(8, 11, 12, 11)})/SUM({rng(8, 12, 12, 12)}),0)",
             bold=True, font_size=10, align="center", num_format="0.0%", bg_color=SAGE_L, font_color="#3E6B58")
    ws.conditional_format(rng(13, 11, 13, 12),
                          {"type": "data_bar", "bar_color": SAGE, "bar_solid": True,
                           "min_type": "num", "min_value": 0, "max_type": "num", "max_value": 1})
    cv.grid(7, 10, 13, 12, t.line)
    cv.box(6, 10, 13, 12, t.line)

    # Bills tracker (rows 15..24)
    cv.merge(15, 10, 15, 12, "BILLS TRACKER • HÓA ĐƠN ĐỊNH KỲ", bold=True, font_size=9.5,
             align="center", bg_color=CORAL, font_color="#FFFFFF")
    cv.put(16, 10, "Hóa đơn", bold=True, font_size=8.5, align="center", bg_color=CORAL_L)
    cv.put(16, 11, "Số tiền", bold=True, font_size=8.5, align="center", bg_color=CORAL_L)
    cv.put(16, 12, "Đã trả ☑", bold=True, font_size=8.5, align="center", bg_color=CORAL_L)
    bills = [
        ("Tiền thuê nhà", 4200000, True),
        ("Điện & Nước", 650000, True),
        ("Internet Wifi", 250000, True),
        ("Điện thoại / 4G", 150000, True),
        ("Phòng tập Gym", 450000, True),
        ("Cloud / Phần mềm", 120000, False),
        ("", "", False),
    ]
    for i, (bn, ba, paid) in enumerate(bills):
        rr = 17 + i
        bg = t.card if i % 2 == 0 else t.page
        cv.put(rr, 10, bn, font_size=9, align="left", indent=1, bg_color=bg)
        cv.put(rr, 11, ba, font_size=9, align="right", num_format=VND, bg_color=bg)
        cv.checkbox(rr, 12, paid, align="center", font_color=SAGE, bg_color=bg)
    cv.put(24, 10, "TOTAL BILLS", bold=True, font_size=8.5, align="left", indent=1, bg_color=CORAL_L)
    cv.put(24, 11, f"=SUM({rng(17, 11, 23, 11)})", bold=True, font_size=9, align="right",
           num_format=VND, bg_color=CORAL_L)
    cv.put(24, 12, f'=COUNTIFS({rng(17, 10, 23, 10)},"?*",{rng(17, 12, 23, 12)},TRUE)&"/"&COUNTIF({rng(17, 10, 23, 10)},"?*")',
           bold=True, font_size=9, align="center", bg_color=CORAL_L)
    cv.grid(16, 10, 24, 12, t.line)
    cv.box(15, 10, 24, 12, t.line)

    # ---- BOTTOM FULL-WIDTH: TRANSACTION LOG (rows 26..52) ----
    cv.row(26, 24)
    cv.row(R_LOG_H, 22)
    cv.merge(26, 1, 26, 12, "🧾  TRANSACTION LOG — NHẬT KÝ THU CHI (Nhập vào đây → mọi biểu đồ tự cập nhật!)",
             bold=True, font_size=9.5, align="left", indent=1, bg_color=SAGE, font_color="#FFFFFF")
    cv.put(R_LOG_H, 1, "Ngày", bold=True, font_size=8.5, align="center", bg_color=SAGE_L)
    cv.put(R_LOG_H, 2, "Danh mục (Category)", bold=True, font_size=8.5, align="center", bg_color=SAGE_L)
    cv.merge(R_LOG_H, 3, R_LOG_H, 5, "Mô tả (Description)", bold=True, font_size=8.5, align="center", bg_color=SAGE_L)
    cv.merge(R_LOG_H, 6, R_LOG_H, 7, "Số tiền (VNĐ)", bold=True, font_size=8.5, align="center", bg_color=SAGE_L)
    cv.put(R_LOG_H, 8, "Loại (Type)", bold=True, font_size=8.5, align="center", bg_color=SAGE_L)
    cv.merge(R_LOG_H, 9, R_LOG_H, 12, "Ghi chú (Notes)", bold=True, font_size=8.5, align="center", bg_color=SAGE_L)

    txs = [
        ("01/10/2026", "Salary", "Lương chính tháng 10", 18000000, "Income", "Chuyển khoản công ty"),
        ("02/10/2026", "Side Hustle", "Dự án freelance thiết kế", 4500000, "Income", "Khách hàng thanh toán đợt 2"),
        ("02/10/2026", "Bills & Rent", "Tiền thuê nhà + dịch vụ", 4200000, "Expense", "Thanh toán đầu tháng"),
        ("03/10/2026", "Savings", "Trích quỹ dự phòng", 4000000, "Savings", "Tự động tiết kiệm đầu tháng"),
        ("04/10/2026", "Food & Groceries", "Đi siêu thị tuần 1", 950000, "Expense", "Rau củ, thịt cá, trái cây"),
        ("05/10/2026", "Bills & Rent", "Điện, nước & Wifi", 900000, "Expense", "Hóa đơn tháng trước"),
        ("07/10/2026", "Self-Growth", "Mua sách & khóa học Excel", 750000, "Expense", "Đầu tư bản thân"),
        ("09/10/2026", "Transport & Daily", "Xăng xe & gửi xe", 420000, "Expense", "Di chuyển đi làm"),
        ("11/10/2026", "Food & Groceries", "Đi chợ & siêu thị tuần 2", 880000, "Expense", "Nấu ăn tại nhà"),
        ("14/10/2026", "Wants & Fun", "Cafe & ăn tối cùng bạn bè", 680000, "Expense", "Cuối tuần thư giãn"),
        ("15/10/2026", "Savings", "Quỹ du lịch cuối năm", 2000000, "Savings", "Đạt mục tiêu tiết kiệm tháng"),
        ("18/10/2026", "Food & Groceries", "Siêu thị tuần 3", 820000, "Expense", "Bổ sung thực phẩm lành mạnh"),
        ("20/10/2026", "Self-Growth", "Gia hạn thẻ Gym", 450000, "Expense", "Duy trì thói quen tập luyện"),
        ("23/10/2026", "Wants & Fun", "Xem phim & quà tặng", 550000, "Expense", "Giải trí hợp lý"),
    ]
    for i in range(R_LOG1 - R_LOG0 + 1):
        rr = R_LOG0 + i
        cv.row(rr, 21)
        bg = t.card if i % 2 == 0 else t.page
        dt, cat, desc, amt, tp, nt = txs[i] if i < len(txs) else ("", "", "", "", "", "")
        cv.put(rr, 1, dt, align="center", font_size=9, bg_color=bg, font_color=t.muted)
        cv.put(rr, 2, cat, align="left", indent=1, font_size=9, bg_color=bg, font_color=t.ink)
        cv.merge(rr, 3, rr, 5, desc, align="left", indent=1, font_size=9, bg_color=bg, font_color=t.ink)
        cv.merge(rr, 6, rr, 7, amt, align="right", font_size=9, bold=bool(amt), num_format=VND, bg_color=bg, font_color=t.ink)
        cv.put(rr, 8, tp, align="center", font_size=9, bold=bool(tp), bg_color=bg, font_color=t.ink)
        cv.merge(rr, 9, rr, 12, nt, align="left", indent=1, font_size=8.5, bg_color=bg, font_color=t.muted)
    cv.grid(R_LOG_H, 1, R_LOG1, 12, t.line)
    cv.box(26, 1, R_LOG1, 12, t.line)

    ws.data_validation(rng(R_LOG0, 2, R_LOG1, 2),
                       {"validate": "list", "source": ["Salary", "Side Hustle", "Bills & Rent",
                                                       "Food & Groceries", "Transport & Daily",
                                                       "Wants & Fun", "Self-Growth", "Savings"]})
    ws.data_validation(rng(R_LOG0, 8, R_LOG1, 8),
                       {"validate": "list", "source": ["Income", "Expense", "Savings"]})

    _finish_sheet(ws, cv, SAGE, zoom=85)
    return {
        "q": q, "income": f"{q}!{cf_inc}", "expenses": f"{q}!{cf_exp}",
        "savings": f"{q}!{cf_sav}", "left": f"{q}!{cf_lft}",
        "savings_rate": f"{q}!{sav_rate_addr}", "goal_progress": f"{q}!{goal_prog_addr}",
    }


# =========================================================================== #
#  4B. Template 4 (Sage Botanical) — 🔗 Life Overview
# =========================================================================== #
def build_life_overview_sheet(wb, styles: Styles, tr: TrackerRefs, b: dict):
    name = "🔗 Life Overview"
    t = styles.t
    ws = wb.add_worksheet(name)
    cv = Canvas(wb, ws, styles, name)
    q = qs(name)
    VND = '#,##0" ₫"'

    cv.col(0, 2.5)
    for c in range(1, 9):
        cv.col(c, 16)
    cv.col(9, 2.5)
    cv.cols(15, 20, 6, hidden=True)

    cv.row(0, 12)
    cv.row(1, 32)
    cv.row(2, 10)
    cv.row(3, 20)
    cv.row(4, 34)
    cv.row(5, 12)

    cv.merge(1, 1, 1, 8, "🔗  LIFE OVERVIEW — CÂN BẰNG THÓI QUEN & TÀI CHÍNH",
             font_name=t.font_title, font_size=15, bold=True, align="center",
             bg_color=t.primary, font_color=t.on_primary)
    cv.box(1, 1, 1, 8, t.line)

    # Hidden donut helper cells
    cv.put(1, 15, f"={tr.a('overall')}")
    cv.put(2, 15, f"=1-{tr.a('overall')}")
    cv.put(1, 16, f"={b['savings_rate']}")
    cv.put(2, 16, f"=MAX(0,1-{b['savings_rate']})")

    score_expr = f"IFERROR(AVERAGE({tr.a('overall')},MIN(1,{b['savings_rate']}/0.25)),0)"
    kpi_card(cv, 3, 1, 2, "🌿  HABIT COMPLETION %", f"={tr.a('overall')}", num_format="0.0%",
             label_fill="#E9F0EC", value_color="#3E6B58")
    kpi_card(cv, 3, 3, 4, "💰  SAVINGS RATE %", f"={b['savings_rate']}", num_format="0.0%",
             label_fill="#F8F1E4", value_color="#8C6A35")
    kpi_card(cv, 3, 5, 6, "✨  LIFE BALANCE SCORE", f"={score_expr}", num_format="0.0%",
             label_fill="#F8EAE6", value_color="#A85D4C")
    kpi_card(cv, 3, 7, 8, "🎯  SAVINGS GOALS PROGRESS", f"={b['goal_progress']}", num_format="0.0%",
             label_fill="#EBF1F8", value_color="#496588")

    # Side-by-side Donut Cards (rows 6..15)
    for r in range(6, 16):
        cv.row(r, 22)
    # Left Donut: Habit Consistency
    cv.merge(6, 1, 6, 4, "🌿  HABIT CONSISTENCY • KỶ LUẬT THÓI QUEN", bold=True, font_size=9.5,
             align="center", bg_color="#9FB8AD", font_color="#FFFFFF")
    cv.merge(7, 1, 14, 4, f"={tr.a('overall')}", bold=True, font_size=22, align="center",
             num_format="0%", bg_color=t.card, font_color="#3E6B58", font_name=t.font_title)
    cv.merge(15, 1, 15, 4,
             f'="Cây nở hoa: "&{tr.a("grown")}&" ngày  •  Best Streak: "&{tr.a("best")}&" ngày"',
             font_size=9, align="center", bg_color="#E9F0EC", font_color=t.ink)
    cv.box(6, 1, 15, 4, t.line)
    d1 = donut(wb, f"={q}!{rng(1, 15, 2, 15)}", ["#9FB8AD", "#E9F0EC"], hole=68)
    place_chart(cv, d1, 7, 1, 14, 4, pad_x=35, pad_y=6)

    # Right Donut: Savings Rate
    cv.merge(6, 5, 6, 8, "💰  SAVINGS RATE • TỶ LỆ TIẾT KIỆM (Mục tiêu ≥ 25%)", bold=True, font_size=9.5,
             align="center", bg_color="#E8D5B7", font_color=t.ink)
    cv.merge(7, 5, 14, 8, f"={b['savings_rate']}", bold=True, font_size=22, align="center",
             num_format="0.0%", bg_color=t.card, font_color="#8C6A35", font_name=t.font_title)
    cv.merge(15, 5, 15, 8,
             f'="Tiết kiệm: "&TEXT({b["savings"]},"#,##0")&" ₫  •  Còn lại: "&TEXT({b["left"]},"#,##0")&" ₫"',
             font_size=9, align="center", bg_color="#F8F1E4", font_color=t.ink)
    cv.box(6, 5, 15, 8, t.line)
    d2 = donut(wb, f"={q}!{rng(1, 16, 2, 16)}", ["#E0A899", "#F8F1E4"], hole=68)
    place_chart(cv, d2, 7, 5, 14, 8, pad_x=35, pad_y=6)

    # Bottom Executive Insights Card (rows 17..22)
    cv.row(16, 12)
    cv.row(17, 24)
    cv.merge(17, 1, 17, 8, "💡  EXECUTIVE LIFE BALANCE INSIGHTS (Tự động đánh giá)", bold=True,
             font_size=9.5, align="left", indent=1, bg_color=t.primary, font_color=t.on_primary)
    insights = [
        ("🌿  Đánh giá Thói quen:",
         f'=IF({tr.a("overall")}>=0.8,"Tuyệt vời! Bạn duy trì kỷ luật thói quen trên 80% — nền tảng vững chắc cho sức khỏe & hiệu suất.",'
         f'"Khá tốt! Hãy chọn 2 thói quen cốt lõi để tập trung nâng tỷ lệ lên trên 80% trong tuần tới.")'),
        ("💰  Đánh giá Tài chính:",
         f'=IF({b["savings_rate"]}>=0.25,"Xuất sắc! Tỷ lệ tiết kiệm đạt từ 25% thu nhập trở lên — tài chính cá nhân cực kỳ lành mạnh.",'
         f'"Bạn đang đi đúng hướng! Cắt giảm 10% nhóm Wants & Fun sẽ giúp đẩy tỷ lệ tiết kiệm vượt mốc 25%.")'),
        ("🔗  Sức khỏe Tổng thể:",
         f'=IF({score_expr}>=0.85,"🌟 TRẠNG THÁI THỊNH VƯỢNG: Cả kỷ luật cá nhân lẫn dòng tiền đều đạt chuẩn đỉnh cao!",'
         f'"🌱 TRẠNG THÁI TĂNG TRƯỞNG: Duy trì đều đặn mỗi ngày để nâng điểm Cân Bằng Cuộc Sống vượt 85%!")'),
    ]
    for i, (lab, form) in enumerate(insights):
        rr = 18 + i
        cv.row(rr, 28)
        bg = t.card if i % 2 == 0 else t.page
        cv.merge(rr, 1, rr, 2, f"  {lab}", bold=True, font_size=9.5, align="left", bg_color=bg, font_color=t.primary_dark)
        cv.merge(rr, 3, rr, 8, form, font_size=9.5, align="left", text_wrap=True, bg_color=bg, font_color=t.ink)
        cv.hline(rr, 1, 8, t.line)
    cv.box(17, 1, 20, 8, t.line)

    _finish_sheet(ws, cv, t.primary_dark)


# =========================================================================== #
#  5. Template 5 (Lavender Dream) — ✨ Gratitude & Review
# =========================================================================== #
def build_gratitude_sheet(wb, styles: Styles, tr: TrackerRefs, well: dict):
    name = "✨ Gratitude & Review"
    t = styles.t
    ws = wb.add_worksheet(name)
    cv = Canvas(wb, ws, styles, name)

    cv.col(0, 2.5)
    cv.col(1, 9.5)
    cv.col(2, 41)
    cv.col(3, 41)
    cv.col(4, 15.5)
    cv.col(5, 2.2)
    cv.col(6, 20)
    cv.col(7, 20)
    cv.col(8, 2.5)

    cv.row(0, 12)
    cv.row(1, 32)
    cv.row(2, 10)
    cv.row(3, 20)
    cv.row(4, 34)
    cv.row(5, 12)
    cv.row(6, 24)
    cv.row(7, 22)

    cv.merge(1, 1, 1, 7, "✨  GRATITUDE JOURNAL & MONTHLY WELLNESS REVIEW", font_name=t.font_title,
             font_size=15, bold=True, align="center", bg_color=t.primary, font_color=t.on_primary)
    cv.box(1, 1, 1, 7, t.line)

    kpi_card(cv, 3, 1, 2, "🌙  HABIT COMPLETION %", f"={tr.a('overall')}", num_format="0.0%", value_color=t.primary_dark)
    kpi_card(cv, 3, 3, 3, "💤  AVG SLEEP HOURS", f"={well['avg_sleep']}", num_format='0.0" h"', value_color=t.ink)
    kpi_card(cv, 3, 4, 4, "💜  AVG MOOD", f"={well['avg_mood']}", num_format='0.0" /5"', value_color=t.primary_dark)
    kpi_card(cv, 3, 6, 7, "⚡  AVG ENERGY & GREAT DAYS", f"={well['avg_energy']}", num_format='0.0" ⚡"', value_color=t.primary_dark)

    cv.merge(6, 1, 6, 4, "🪻  31-DAY GRATITUDE & DAILY HIGHLIGHT LOG", bold=True, font_size=9.5,
             align="left", indent=1, bg_color=t.primary, font_color=t.on_primary)
    cv.put(7, 1, "Ngày", bold=True, font_size=8.5, align="center", bg_color=t.soft)
    cv.put(7, 2, "Điều biết ơn hôm nay (Grateful For)", bold=True, font_size=8.5, align="center", bg_color=t.soft)
    cv.put(7, 3, "Khoảnh khắc đẹp nhất (Daily Highlight)", bold=True, font_size=8.5, align="center", bg_color=t.soft)
    cv.put(7, 4, "Self-care ☑", bold=True, font_size=8.5, align="center", bg_color=t.soft)

    samples = [
        ("Bữa sáng ấm áp và nắng nhẹ đầu tuần", "Hoàn thành xong danh sách việc ưu tiên trước 16h", True),
        ("Cơ thể khỏe mạnh sau buổi chạy bộ", "Nghe một podcast truyền cảm hứng trên đường về", True),
        ("Đồng nghiệp hỗ trợ nhiệt tình", "Tự nấu món súp rau củ rất ngon", True),
        ("Giấc ngủ sâu đủ 8 tiếng không mộng mị", "Đọc hết 2 chương sách yêu thích", True),
        ("Cuộc gọi hỏi thăm đầy yêu thương từ gia đình", "Đi dạo công viên ngắm hoàng hôn tím", True),
        ("Một buổi sáng cuối tuần thong thả", "Dọn gọn bàn làm việc & cắm bình hoa tươi", True),
        ("Thời tiết mát mẻ dễ chịu", "Thiền 15 phút thấy lòng bình an lạ thường", True),
        ("Một ly trà hoa cúc ấm vào buổi tối", "Giải quyết trơn tru task khó nhất tuần", True),
        ("Những người bạn luôn lắng nghe", "Cười thả ga trong buổi cafe chiều", True),
        ("Sự kiên trì của chính bản thân mình", "Chạm mốc chuỗi 10 ngày liên tiếp không bỏ cuộc!", True),
    ]
    for d in range(1, 32):
        rr = 7 + d
        cv.row(rr, 28 if d <= 20 else 23)
        bg = t.card if d % 2 == 1 else t.page
        g, hl, sc = samples[d - 1] if d <= len(samples) else ("", "", False)
        cv.put(rr, 1, f"Ngày {d}", bold=True, font_size=9, align="center", bg_color=t.soft, font_color=t.ink)
        cv.put(rr, 2, g, font_size=9, align="left", indent=1, bg_color=bg, font_color=t.ink)
        cv.put(rr, 3, hl, font_size=9, align="left", indent=1, bg_color=bg, font_color=t.ink)
        cv.checkbox(rr, 4, sc, align="center", font_color=t.primary_dark, bg_color=bg)
    cv.grid(7, 1, 38, 4, t.line)
    cv.box(6, 1, 38, 4, t.line)

    # Sidebar Monthly Wellness Review Cards (cols 6..7)
    side_cards = [
        (6, "💜  3 ĐIỀU TỰ HÀO NHẤT THÁNG", [
            "1. Kiên trì giữ thói quen đi ngủ sớm và đọc sách.",
            "2. Lắng nghe cảm xúc và cho phép bản thân nghỉ ngơi.",
            "3. Duy trì năng lượng tích cực ngay cả trong tuần bận rộn.",
            "",
        ]),
        (12, "🌙  BÀI HỌC TÂM ĐẮC", [
            "• Giấc ngủ đủ 7.5–8h ảnh hưởng trực tiếp đến 80% tâm trạng ngày hôm sau.",
            "• Chỉ cần làm 1 bước nhỏ (5 phút) cũng tốt hơn bỏ qua hoàn toàn.",
            "", "",
        ]),
        (18, "🪻  Ý ĐỊNH THÁNG TỚI (INTENTIONS)", [
            "• Sống chậm lại 10% — tận hưởng trọn vẹn từng bữa ăn.",
            "• Dành ít nhất 1 buổi chiều cuối tuần hoàn toàn rời xa màn hình.",
            "", "",
        ]),
    ]
    for rs, title, lines in side_cards:
        cv.merge(rs, 6, rs, 7, title, bold=True, font_size=9.5, align="center",
                 bg_color=t.primary, font_color=t.on_primary)
        for i, ln in enumerate(lines):
            cv.merge(rs + 1 + i, 6, rs + 1 + i, 7, ln, font_size=9, align="left", indent=1,
                     text_wrap=True, bg_color=t.card, font_color=t.ink)
            cv.hline(rs + 1 + i, 6, 7, t.line)
        cv.box(rs, 6, rs + len(lines), 7, t.line)

    # Live Self-care counter card
    cv.merge(24, 6, 24, 7, "✨  SELF-CARE DAYS COUNTER", bold=True, font_size=9.5, align="center",
             bg_color=t.primary, font_color=t.on_primary)
    cv.merge(25, 6, 27, 7, f"=COUNTIF({rng(8, 4, 38, 4)},TRUE)", bold=True, font_size=26,
             align="center", num_format='0" ngày"', bg_color=t.card, font_color=t.primary_dark,
             font_name=t.font_title)
    cv.merge(28, 6, 28, 7, "Bạn xứng đáng được yêu thương mỗi ngày 💜", italic=True, font_size=8.5,
             align="center", bg_color=t.soft, font_color=t.ink)
    cv.box(24, 6, 28, 7, t.line)

    _finish_sheet(ws, cv, t.primary_dark)


# =========================================================================== #
#  6. Template 6 (Midnight Navy Focus) — 🏆 Milestones & Gamification
# =========================================================================== #
def build_milestones_sheet(wb, styles: Styles, tr: TrackerRefs, total_xp_ref: str, xp_col: int):
    name = "🏆 Milestones"
    t = styles.t
    ws = wb.add_worksheet(name)
    cv = Canvas(wb, ws, styles, name)
    q = qs(name)

    NAVY, BLUSH, SLATE = "#2B3452", "#F2D7D9", "#5C6B9C"
    BLUSH_L = "#FAF1F2"

    cv.col(0, 2.5)
    cv.col(1, 27.5)
    cv.col(2, 33)
    cv.col(3, 12)
    cv.col(4, 15)
    cv.col(5, 2.2)
    cv.col(6, 19)
    cv.col(7, 16)
    cv.col(8, 16)
    cv.col(9, 2.5)

    cv.row(0, 12)
    cv.row(1, 34)
    cv.row(2, 10)
    cv.row(3, 20)
    cv.row(4, 34)
    cv.row(5, 12)
    cv.row(6, 24)
    cv.row(7, 22)

    cv.merge(1, 1, 1, 8, "🚀  FOCUS MILESTONES • BẢNG THÀNH TÍCH & HỆ THỐNG CẤP BẬC XP",
             font_name=t.font_title, font_size=15, bold=True, align="center",
             bg_color=NAVY, font_color="#FFFFFF")
    cv.box(1, 1, 1, 8, NAVY)

    r_m0 = 8
    r_m1 = 17
    stat_rng = rng(r_m0, 4, r_m1, 4)

    kpi_card(cv, 3, 1, 1, "TOTAL XP EARNED", f"={total_xp_ref}", num_format='#,##0" XP"',
             label_fill=BLUSH, value_color=NAVY)
    kpi_card(cv, 3, 2, 2, "CURRENT RANK TIER",
             f'=IF({total_xp_ref}>=3000,"👑 MASTER",IF({total_xp_ref}>=1800,"🔥 UNSTOPPABLE",'
             f'IF({total_xp_ref}>=800,"⚡ CONSISTENT","🌱 BEGINNER")))',
             num_format="@", label_fill=BLUSH, value_color=NAVY, value_size=16)
    kpi_card(cv, 3, 3, 4, "BADGES UNLOCKED", f'=COUNTIF({stat_rng},"🏆 UNLOCKED")&" / 10"',
             num_format="@", label_fill=BLUSH, value_color=NAVY)
    kpi_card(cv, 3, 6, 8, "MONTHLY CONSISTENCY", f"={tr.a('overall')}", num_format="0.0%",
             label_fill=BLUSH, value_color=NAVY)

    # Left: 10 Dynamic Achievement Badges (rows 6..17, cols 1..4)
    cv.merge(6, 1, 6, 4, "🏅  ACHIEVEMENT BADGES (Tự động mở khóa theo tiến độ thật!)",
             bold=True, font_size=9.5, align="left", indent=1, bg_color=NAVY, font_color="#FFFFFF")
    for c, h in [(1, "Huy hiệu (Badge)"), (2, "Điều kiện mở khóa"), (3, "Tiến độ"), (4, "Trạng thái")]:
        cv.put(7, c, h, bold=True, font_size=8.5, align="center", bg_color=BLUSH, font_color=NAVY)

    badges = [
        ("🚀  First Liftoff", "Hoàn thành ít nhất 1 ngày 100%", f"=MIN(1,{tr.a('perfect')}/1)"),
        ("🔥  7-Day Fire Streak", "Đạt chuỗi 7 ngày liên tiếp ở 1 thói quen", f"=MIN(1,{tr.a('best')}/7)"),
        ("🛡️  14-Day Iron Will", "Đạt chuỗi 14 ngày liên tiếp", f"=MIN(1,{tr.a('best')}/14)"),
        ("🧠  21-Day Habit Wired", "Đạt chuỗi 21 ngày liên tiếp", f"=MIN(1,{tr.a('best')}/21)"),
        ("👑  30-Day Legend", "Đạt chuỗi 30 ngày liên tiếp không đứt", f"=MIN(1,{tr.a('best')}/30)"),
        ("⚡  1,000 XP Club", "Tích lũy từ 1,000 XP trở lên", f"=MIN(1,{total_xp_ref}/1000)"),
        ("💎  2,500 XP Elite", "Tích lũy từ 2,500 XP trở lên", f"=MIN(1,{total_xp_ref}/2500)"),
        ("🎯  80% Consistency", "Tỷ lệ hoàn thành toàn tháng ≥ 80%", f"=MIN(1,{tr.a('overall')}/0.8)"),
        ("🌟  15+ Orbit Days", "Đạt ít nhất 15 ngày năng suất ≥ 75%", f"=MIN(1,{tr.a('grown')}/15)"),
        ("🏆  150+ Focus Checks", "Đạt tổng cộng ≥ 150 lượt hoàn thành", f"=MIN(1,{tr.a('tdone')}/150)"),
    ]
    for i, (bname, cond, pf) in enumerate(badges):
        rr = r_m0 + i
        cv.row(rr, 24)
        bg = t.card if i % 2 == 0 else BLUSH_L
        cv.put(rr, 1, bname, bold=True, font_size=9.5, align="left", indent=1, bg_color=bg, font_color=NAVY)
        cv.put(rr, 2, cond, font_size=9, align="left", indent=1, bg_color=bg, font_color=t.ink)
        cv.put(rr, 3, pf, bold=True, font_size=9, align="center", num_format="0%", bg_color=bg, font_color=NAVY)
        cv.put(rr, 4, f'=IF({cell(rr, 3)}>=1,"🏆 UNLOCKED","🔒 Locked")', bold=True, font_size=9,
               align="center", bg_color=bg, font_color=t.muted)
    cv.grid(7, 1, r_m1, 4, t.line)
    cv.box(6, 1, r_m1, 4, NAVY)
    ws.conditional_format(rng(r_m0, 3, r_m1, 3),
                          {"type": "data_bar", "bar_color": BLUSH, "bar_solid": True,
                           "min_type": "num", "min_value": 0, "max_type": "num", "max_value": 1})
    ws.conditional_format(stat_rng, {"type": "text", "criteria": "containing", "value": "UNLOCKED",
                                     "format": wb.add_format({"bg_color": "#E6F6EC", "font_color": "#236B43", "bold": True})})

    # Right Top: Rank Tier Ladder (rows 6..11, cols 6..8)
    cv.merge(6, 6, 6, 8, "🎖️  RANK TIER LADDER", bold=True, font_size=9.5, align="center",
             bg_color=NAVY, font_color="#FFFFFF")
    cv.put(7, 6, "Cấp bậc", bold=True, font_size=8.5, align="center", bg_color=BLUSH, font_color=NAVY)
    cv.put(7, 7, "Yêu cầu XP", bold=True, font_size=8.5, align="center", bg_color=BLUSH, font_color=NAVY)
    cv.put(7, 8, "Trạng thái", bold=True, font_size=8.5, align="center", bg_color=BLUSH, font_color=NAVY)
    ranks = [
        ("🌱  Beginner", "0 – 799 XP", f'=IF({total_xp_ref}>=800,"✅ Đã vượt qua","📍 Đang ở đây")'),
        ("⚡  Consistent", "800 – 1,799 XP", f'=IF({total_xp_ref}>=1800,"✅ Đã vượt qua",IF({total_xp_ref}>=800,"📍 Đang ở đây","🔒 Khóa"))'),
        ("🔥  Unstoppable", "1,800 – 2,999 XP", f'=IF({total_xp_ref}>=3000,"✅ Đã vượt qua",IF({total_xp_ref}>=1800,"📍 Đang ở đây","🔒 Khóa"))'),
        ("👑  Focus Master", "3,000+ XP", f'=IF({total_xp_ref}>=3000,"👑 ĐẠT ĐỈNH!","🔒 Khóa")'),
    ]
    for i, (rn, req, sf) in enumerate(ranks):
        rr = 8 + i
        bg = t.card if i % 2 == 0 else BLUSH_L
        cv.put(rr, 6, rn, bold=True, font_size=9.5, align="left", indent=1, bg_color=bg, font_color=NAVY)
        cv.put(rr, 7, req, font_size=9, align="center", bg_color=bg, font_color=t.muted)
        cv.put(rr, 8, sf, bold=True, font_size=9, align="center", bg_color=bg, font_color=NAVY)
    cv.grid(7, 6, 11, 8, t.line)
    cv.box(6, 6, 11, 8, NAVY)

    # Right Bottom: XP Contribution by Habit Column Chart (rows 13..22, cols 6..8)
    for rr in range(18, 23):
        cv.row(rr, 22)
    ch = wb.add_chart({"type": "bar"})
    ch.add_series({
        "name": "XP Earned",
        "categories": f"={tr.q}!{rng(R_H0, C_NAME, R_H0 + 7, C_NAME)}",
        "values": f"={tr.q}!{rng(R_H0, xp_col, R_H0 + 7, xp_col)}",
        "fill": {"color": SLATE},
        "border": {"none": True},
    })
    ch.set_title({"name": "XP EARNED BY HABIT",
                  "name_font": {"name": t.font, "size": 9.5, "bold": True, "color": NAVY}})
    ch.set_x_axis({"num_format": "#,##0", "num_font": axis_font(t),
                   "major_gridlines": {"visible": True, "line": {"color": t.line, "dash_type": "dash"}}})
    ch.set_y_axis({"reverse": True, "num_font": axis_font(t, 8), "line": {"color": t.line}})
    ch.set_legend({"none": True})
    ch.set_chartarea({"border": {"color": NAVY, "width": 0.75}, "fill": {"color": t.card}})
    place_chart(cv, ch, 13, 6, 22, 8)

    # Left bottom: Personal Reward Card (rows 19..22, cols 1..4)
    cv.row(18, 10)
    cv.merge(19, 1, 19, 4, "🎁  SELF-REWARD MILESTONES (Phần thưởng tự tặng khi lên hạng)",
             bold=True, font_size=9.5, align="left", indent=1, bg_color=NAVY, font_color="#FFFFFF")
    rewards = [
        ("⚡  Đạt Consistent (800 XP):", "Một buổi cafe đặc sản & 1 cuốn sách mới yêu thích"),
        ("🔥  Đạt Unstoppable (1,800 XP):", "Một bữa tối ngon miệng hoặc buổi massage thư giãn"),
        ("👑  Đạt Focus Master (3,000 XP):", "Món đồ công nghệ / du lịch ngắn cuối tuần bạn mong muốn!"),
    ]
    for i, (rl, rd) in enumerate(rewards):
        rr = 20 + i
        bg = t.card if i % 2 == 0 else BLUSH_L
        cv.put(rr, 1, rl, bold=True, font_size=9, align="left", indent=1, bg_color=bg, font_color=NAVY)
        cv.merge(rr, 2, rr, 4, rd, font_size=9, align="left", indent=1, bg_color=bg, font_color=t.ink)
        cv.hline(rr, 1, 4, t.line)
    cv.box(19, 1, 22, 4, NAVY)

    _finish_sheet(ws, cv, NAVY)
