"""
hx.guide — Version 2.3 `📖 Hướng Dẫn` welcome screen & live animation config tab.

Strict UI/UX polish:
  - Unified `Segoe UI` font across 100% of cells (zero mixed fonts, zero markdown backticks)
  - Consistent Bold (headers & key column) vs. Regular (descriptions & instructions) hierarchy
  - `indent=1` horizontal padding on all left-aligned text cells & `valign="vcenter"` everywhere
  - Centered threshold bar (Row 23), generous dynamic row heights (zero clipping on Row 14/27/Footer)
  - Airy 94pt sprite preview row (Row 25) with centered Stage 0..5 icons
"""
from __future__ import annotations

from .core import Canvas, Theme, Styles, acell, qs, text_lines, REPO_URL

GUIDE_SHEET = "📖 Hướng Dẫn"


def build_guide(wb, styles: Styles, tracker_sheet: str, extra_tabs: list[tuple[str, str]],
                edition: str = "offline") -> dict:
    """Returns manifest info for COM Linked Pictures (6 stage previews in `pro_xlsm` / `offline`)."""
    t: Theme = styles.t
    universal = edition in ("pro_xlsm", "offline")
    gsheets = (edition == "gsheets")
    ws = wb.add_worksheet(GUIDE_SHEET)
    cv = Canvas(wb, ws, styles, GUIDE_SHEET, universal=universal, gsheets=gsheets)
    q = qs(GUIDE_SHEET)

    cv.col(0, 3.0)
    for c in range(1, 7):
        cv.col(c, 22.0)
    cv.col(7, 3.0)
    cv.row(0, 12)

    # ------------------------------------------------------------------ HERO BANNER (Rows 2..4)
    cv.row(1, 38)
    cv.row(2, 24)
    cv.row(3, 24)
    cv.merge(1, 1, 1, 6, f"{t.emoji}  {t.name}  —  HƯỚNG DẪN SỬ DỤNG (v2.3)",
             font_name=t.font_title, font_size=15.5, bold=True, align="center",
             bg_color=t.primary, font_color=t.on_primary)
    cv.merge(2, 1, 2, 6, t.tagline_vi, font_size=10, italic=True, align="center",
             bg_color=t.soft, font_color=t.ink)

    if edition == "pro_xlsm":
        mode_txt = "⚡ BẢN PRO INTERACTIVE (.XLSM)  •  Gọn 4 tab  •  Tự lưu & chuyển Tháng / Năm siêu mượt  •  100% Offline"
    elif edition == "offline":
        mode_txt = "✨ BẢN EXCEL OFFLINE KHÔNG MACRO (.XLSX)  •  Gọn nhẹ 4 tab  •  Chạy mọi Excel 2016–365 Win/Mac  •  0 cảnh báo bảo mật"
    else:
        mode_txt = "☁️ BẢN GOOGLE SHEETS EDITION  •  Gọn 4 tab + _Database  •  Hoạt ảnh =IMAGE() động  •  Kèm Script 1-Click Checkbox!"

    cv.merge(3, 1, 3, 6, mode_txt, font_size=9, bold=True, align="center",
             bg_color=t.card, font_color=t.primary_dark)
    cv.box(1, 1, 3, 6, t.line)
    r = 4

    # Google Sheets crisp 1-line 3-second tip banner right under hero!
    if gsheets:
        cv.row(r, 10)
        r += 1
        cv.row(r, 46)
        cv.merge(
            r, 1, r, 6,
            "💡 Mẹo mở trên Google Sheets (3 giây): Chọn vùng ô TRUE/FALSE → Chèn (Insert) → Hộp kiểm (Checkbox) "
            "— HOẶC vào Tiện ích mở rộng (Extensions) → Apps Script → dán file google_sheets_1click_setup.gs và chạy setupHabitTracker() để bật Checkbox & tự động lưu 12 tháng vào _Database!",
            font_size=9.5, bold=False, align="left", indent=1, text_wrap=True,
            bg_color=t.warn_fill, font_color=t.ink,
        )
        cv.box(r, 1, r, 6, t.warn_line)
        r += 1

    cv.row(r, 12)
    r += 1

    # ------------------------------------------------------------------ TAB MAP (4 CLEAN TABS, Rows 6..10)
    cv.row(r, 26)
    cv.merge(r, 1, r, 6, "🗂️  CẤU TRÚC 4 SHEET GỌN ĐẸP TRONG FILE (v2.3)", bold=True, font_size=10.5,
             align="left", indent=1, bg_color=t.primary, font_color=t.on_primary)

    if edition == "pro_xlsm":
        tracker_desc = "Bảng theo dõi 31 ngày siêu gọn: đổi dropdown Tháng (B3) / Năm (B5) tự lưu tháng cũ & tải tháng mới vào _Database!"
    elif edition == "offline":
        tracker_desc = "Bảng theo dõi 31 ngày không Macro siêu nhẹ: lịch động, hoạt ảnh 6 giai đoạn offline & Streak Heatmap!"
    else:
        tracker_desc = "Bảng theo dõi 31 ngày Google Sheets: kết hợp script 1-click để bật Checkbox & tự lưu/nạp 12 tháng trong _Database!"

    tab_rows = [
        (GUIDE_SHEET, "Trang chào mừng, hướng dẫn nhanh & bảng tùy chỉnh ngưỡng tăng trưởng 6 giai đoạn."),
        (tracker_sheet, tracker_desc),
    ] + extra_tabs

    for idx, (tname, desc) in enumerate(tab_rows):
        rr = r + 1 + idx
        d_lines = text_lines(desc, 78, factor=0.80)
        cv.row(rr, max(32, d_lines * 16 + 14))
        bg = t.card if idx % 2 == 0 else t.page
        cv.merge(rr, 1, rr, 2, tname, bold=True, font_size=10, align="left", indent=1,
                 bg_color=bg, font_color=t.primary_dark)
        cv.merge(rr, 3, rr, 6, desc, bold=False, font_size=10, align="left", indent=1, text_wrap=True,
                 bg_color=bg, font_color=t.ink)
        cv.hline(rr, 1, 6, t.line)
    cv.box(r, 1, r + len(tab_rows), 6, t.line)
    r = r + len(tab_rows) + 2
    cv.row(r - 1, 12)

    def info_card(start_r: int, c1: int, c2: int, title: str, bullets: list[str]) -> int:
        cv.row(start_r, 26)
        cv.merge(start_r, c1, start_r, c2, title, bold=True, font_size=10, align="left", indent=1,
                 bg_color=t.primary, font_color=t.on_primary)
        span_w = sum(cv.widths.get(c, 22.0) for c in range(c1, c2 + 1)) - 4
        cur = start_r + 1
        for b in bullets:
            lines = text_lines(b, span_w, factor=0.76)
            h = max(48, lines * 16 + 18)
            cv.row(cur, max(cv.heights.get(cur, 0), h))
            cv.merge(cur, c1, cur, c2, b, bold=False, font_size=9.8, align="left", text_wrap=True,
                     bg_color=t.card, font_color=t.ink, indent=1)
            cv.hline(cur, c1, c2, t.line)
            cur += 1
        cv.box(start_r, c1, cur - 1, c2, t.line)
        return cur

    # ------------------------------------------------------------------ 2-COL CARDS (SEC 1 & SEC 2, Rows 12..15)
    if edition == "pro_xlsm":
        sec1 = [
            "1️⃣  Mở file lần đầu: bấm Enable Content (Bật Macro) màu vàng 1 lần để kích hoạt bộ máy tự lưu dữ liệu Tháng/Năm siêu mượt.",
            "2️⃣  Click thẳng vào ô Checkbox (☑ / ☐): hoạt ảnh từng ngày, Monthly Hero, Yearly Goals & Thành Tựu Năm tự lớn lên theo % thực tế (0% = chậu trống → 100% = nở rộ!).",
            "3️⃣  Cột GOAL: nhập số ngày mục tiêu mỗi tháng (vd: 24 ngày). Bỏ trống = tính cả tháng.",
        ]
        sec2 = [
            "⚡  File điền sẵn dữ liệu mẫu tháng 10/2026 để bạn trải nghiệm ngay hiệu ứng hoạt ảnh & Thành Tựu Năm.",
            "🧹  Bắt đầu tháng mới trống 100%? Chỉ cần đổi dropdown Tháng (B3) sang November hoặc Năm (B5) sang 2027 — dữ liệu tháng cũ TỰ LƯU vào _Database & tháng mới mở TRỐNG SẠCH!",
            "🧹  Hoặc reset tháng hiện tại: chọn vùng C17:AG36 → nhấn phím Delete (Mac: fn + Backspace).",
        ]
    elif edition == "offline":
        sec1 = [
            "1️⃣  Mở tab Tracker chính và click thẳng vào ô Checkbox (☑ / ☐) — KHÔNG Macro, KHÔNG cảnh báo bảo mật, KHÔNG cần Internet, mở cực nhanh trên mọi Excel 2016–365!",
            "2️⃣  Hoạt ảnh động 100% theo % thực tế: 31 biểu tượng ngày, Monthly Hero, Yearly Goals & Tổng Kết Năm đều tự đổi từ Stage 0 (0%) → Stage 5 (100%)!",
            "3️⃣  Cột GOAL: nhập số ngày mục tiêu trong tháng. Bỏ trống = mặc định tính đủ số ngày của tháng.",
        ]
        sec2 = [
            "⚡  File điền sẵn ~22 ngày mẫu sinh động. Muốn reset về 0%: chọn vùng C17:AG36 → nhấn Delete (Mac: fn + Backspace) → toàn bộ ô tick về trống & cây về Stage 0!",
            "📑  Sang tháng mới trong 2 giây (bản Không Macro): chuột phải tab Tracker → Move or Copy → tick ☑ Create a copy (hoặc nhân bản file cho tháng mới), chọn tháng ở B3 & xóa vùng tick.",
            "💡  Mẹo: Nếu muốn lưu tự động nhiều Tháng & nhiều Năm ngay trên 1 trang duy nhất, hãy dùng bản Pro (.xlsm) trong thư mục pro_macro/!",
        ]
    else:
        sec1 = [
            "1️⃣  Tải file lên Google Drive → Mở bằng Google Sheets → Tệp → Lưu dưới dạng Google Trang tính.",
            "2️⃣  Bật Checkbox + Lưu 12 Tháng trong 1 giây: Tiện ích mở rộng → Apps Script → dán file google_sheets_1click_setup.gs → Run setupHabitTracker()!",
            "3️⃣  Hoặc làm nhanh không cần Script (3 giây): chọn C17:AG36 → Chèn (Insert) → Hộp kiểm (Checkbox).",
        ]
        sec2 = [
            "⚡  Gọn đúng 4 tab đẹp mắt (không còn 15 tab rối mắt!) nhờ sheet ẩn _Database lưu riêng dữ liệu 12 tháng trong năm.",
            "🧹  Reset nhanh trên Google Sheets: chọn vùng Checkbox C17:AG36 → nhấn Space (hoặc Delete) để bỏ tick sạch sẽ.",
            "✨  Hoạt ảnh =IMAGE() động 6 giai đoạn tự cập nhật cho cả 31 ngày, Monthly Hero, Yearly Goals & Thành Tựu Năm!",
        ]

    end1 = info_card(r, 1, 3, "📌  1. CÁCH SỬ DỤNG & TICK HẰNG NGÀY", sec1)
    end2 = info_card(r, 4, 6, "⚡  2. DỮ LIỆU MẪU, RESET & SANG THÁNG MỚI", sec2)
    r = max(end1, end2) + 1
    cv.row(r - 1, 12)

    # ------------------------------------------------------------------ 2-COL CARDS (SEC 3 & SEC 4, Rows 17..20)
    sec3 = [
        "✏️  Sửa tên thói quen: Gõ đè trực tiếp lên cột tên thói quen (B17:B36) — mọi biểu đồ, hoạt ảnh & chuỗi streak tự cập nhật!",
        "➕  Thêm thói quen: Toàn bộ 20 dòng (B17:B36) đã gắn sẵn ô Checkbox màu pastel đặc trưng của chủ đề + công thức Streak & biểu đồ tự động!",
        "🎯  Mục tiêu Năm: Mở tab 🎯 Yearly Goals & Habits, chọn Năm (ô I2) & tick mục tiêu đạt được — biểu tượng YOU HAVE PLANTED tự lớn từ 0% → 100%!",
    ]
    if edition == "pro_xlsm":
        sec4 = [
            "⚡  Đổi Tháng (B3) & Năm (B5) siêu mượt: Dữ liệu tháng cũ TỰ LƯU vào _Database, tháng chưa dùng mở TRỐNG 100%, quay lại tháng cũ giữ nguyên vẹn từng ô tick!",
            "🏆  Tổng Kết & Thành Tựu Năm: Mở tab 🏆 Tổng Kết & Thành Tựu Năm, chọn Năm (ô B3) → xem ngay 4 thẻ KPI, khu vườn 12 tháng động & 8 Huy hiệu kỷ luật!",
            "🗓️  Chọn năm chưa có dữ liệu (vd: 2028) → hiển thị 0% / Stage 0 trống sạch, không rò rỉ dữ liệu năm khác.",
        ]
    elif edition == "offline":
        sec4 = [
            "📅  Đổi Tháng (B3) & Năm (B5) tự nhảy lịch (28/29/30/31 ngày + thứ Mon–Sun), ẩn gọn ngày thừa cuối tháng!",
            "🏆  Tổng Kết & Thành Tựu Năm: Đồng bộ live tiến độ tháng hiện tại & Yearly Goals, tự mở khóa 8 Huy hiệu kỷ luật & hiển thị 0% / Stage 0 khi chọn năm trống (vd: 2028)!",
            "⚡  Cần lưu lịch sử tự động 12 tháng × nhiều năm trên 1 tab? Chuyển sang dùng bản Pro (.xlsm) đã đi kèm sẵn!",
        ]
    else:
        sec4 = [
            "⚡  Khi đã chạy 1-click Script (google_sheets_1click_setup.gs), mỗi khi đổi dropdown Tháng (B3) trên Google Sheets, hàm onEdit(e) TỰ ĐỘNG lưu tháng cũ & nạp tháng mới từ _Database!",
            "🏆  Tổng Kết & Thành Tựu Năm: Tự tổng hợp 12 tháng trong năm đang chọn + đồng bộ Yearly Goals + mở khóa 8 Huy hiệu kỷ luật!",
            "🗓️  Chọn năm chưa có dữ liệu (vd: 2028) ở ô B3 tab Tổng Kết → toàn bộ biểu đồ, 12 ô tháng & huy hiệu hiển thị 0% / Stage 0 sạch sẽ!",
        ]

    end3 = info_card(r, 1, 3, "🧩  3. TÙY BIẾN THÓI QUEN & MỤC TIÊU NĂM", sec3)
    end4 = info_card(r, 4, 6, "🏆  4. LỊCH ĐỘNG, ĐA THÁNG/NĂM & THÀNH TỰU", sec4)
    r = max(end3, end4) + 1
    cv.row(r - 1, 12)

    # ------------------------------------------------------------------ SEC 5: CUSTOM ANIMATION & THRESHOLDS (Rows 22..27)
    r_cfg = r
    cv.row(r_cfg, 26)
    cv.merge(r_cfg, 1, r_cfg, 6,
             "🎨  5. HOẠT ẢNH 6 GIAI ĐOẠN (LIVE GROWTH ANIMATION) & TÙY CHỈNH NGƯỠNG",
             bold=True, font_size=10.5, align="left", indent=1, bg_color=t.primary, font_color=t.on_primary)

    cur_r = r_cfg + 1
    if gsheets:
        cv.row(cur_r, 28)
        cv.merge(cur_r, 1, cur_r, 2, "🔗  Đường dẫn ảnh (CFG_IMG_BASE):", bold=True, font_size=9.5,
                 align="left", indent=1, bg_color=t.soft, font_color=t.ink)
        cv.merge(cur_r, 3, cur_r, 6, t.img_base, bold=False, font_size=8.8, align="left",
                 bg_color=t.warn_fill, font_color=t.ink, indent=1)
        wb.define_name("CFG_IMG_BASE", f"={q}!{acell(cur_r, 3)}")
        cv.hline(cur_r, 1, 6, t.line)
        cur_r += 1

    # Row 23 Threshold bar — SYMMETRICALLY CENTERED!
    r_thr = cur_r
    cv.row(r_thr, 28)
    cv.put(r_thr, 1, "Ngưỡng Stage 2:", bold=True, font_size=9.5, align="center", bg_color=t.soft, font_color=t.ink)
    cv.put(r_thr, 2, 0.25, bold=True, font_size=10, align="center", num_format="0%",
           bg_color=t.warn_fill, font_color=t.primary_dark)
    cv.put(r_thr, 3, "Ngưỡng Stage 3:", bold=True, font_size=9.5, align="center", bg_color=t.soft, font_color=t.ink)
    cv.put(r_thr, 4, 0.50, bold=True, font_size=10, align="center", num_format="0%",
           bg_color=t.warn_fill, font_color=t.primary_dark)
    cv.put(r_thr, 5, "Ngưỡng Đạt (Grown):", bold=True, font_size=9.5, align="center", bg_color=t.soft, font_color=t.ink)
    cv.put(r_thr, 6, 0.75, bold=True, font_size=10, align="center", num_format="0%",
           bg_color=t.warn_fill, font_color=t.primary_dark)
    wb.define_name("CFG_THR_1", f"={q}!{acell(r_thr, 2)}")
    wb.define_name("CFG_THR_2", f"={q}!{acell(r_thr, 4)}")
    wb.define_name("CFG_THR_3", f"={q}!{acell(r_thr, 6)}")
    cv.hline(r_thr, 1, 6, t.line)

    # Rows 24..26: Stage 0..5 headers, airy 94pt sprite row, descriptions
    r_shead = r_thr + 1
    r_simg = r_thr + 2
    r_sdesc = r_thr + 3
    cv.row(r_shead, 24)
    cv.row(r_simg, 94)
    cv.row(r_sdesc, 24)
    stage_meta = [
        ("Stage 0", "0% (Chưa bắt đầu)"),
        ("Stage 1", "1% – 24% (Khởi động)"),
        ("Stage 2", "25% – 49% (Đang lớn)"),
        ("Stage 3", "50% – 74% (Ổn định)"),
        ("Stage 4", "75% – 99% (Sắp trọn vẹn)"),
        ("Stage 5", "100% (Hoàn hảo ✨)"),
    ]
    guide_sprite_slots = []
    for idx, (st_title, st_sub) in enumerate(stage_meta):
        c = 1 + idx
        cv.put(r_shead, c, st_title, bold=True, font_size=9.5, align="center",
               bg_color=t.soft, font_color=t.ink)
        if universal:
            cv.put(r_simg, c, "", align="center", bg_color=t.card)
            guide_sprite_slots.append({"sheet": GUIDE_SHEET, "r1": r_simg, "c1": c,
                                       "r2": r_simg, "c2": c, "formula": f"=_Assets!$B${2 + idx}"})
        else:
            cv.put(r_simg, c, f'=_xlfn.IMAGE(CFG_IMG_BASE&"stage_{idx}.png")', align="center", bg_color=t.card)
        cv.put(r_sdesc, c, st_sub, bold=False, font_size=8.8, align="center", bg_color=t.card, font_color=t.muted)
    cv.grid(r_shead, 1, r_sdesc, 6, t.line)

    # Row 27 Yellow Tip Box — ZERO markdown backticks, generous height + indent=1!
    r_tip = r_sdesc + 1
    if universal:
        tip_txt = (
            "✨  CÁCH TỰ ĐỔI BỘ ẢNH HOẠT ẢNH RIÊNG (KHÔNG CẦN LINK / KHÔNG CẦN MẠNG):  "
            "1) Chuột phải tên tab bất kỳ → chọn Unhide → chọn _Assets → OK.  "
            "2) Thay 6 ảnh trong ô B2:B7 (Stage 0 → Stage 5) bằng ảnh PNG/sticker của bạn.  "
            "3) Ẩn lại _Assets → toàn bộ 31 ngày, Monthly Hero, Yearly Goals & 12 tháng Tổng Kết Năm tự động đổi theo ảnh của bạn!"
        )
    else:
        tip_txt = (
            "💡  Muốn tự thay bộ icon riêng trên Google Sheets? Tạo 6 file PNG (stage_0.png → stage_5.png), "
            "tải lên GitHub public rồi dán URL thư mục gốc vào ô vàng CFG_IMG_BASE ở trên. "
            "Hoặc sửa 3 ô ngưỡng vàng (25% / 50% / 75%) để điều chỉnh tốc độ tăng trưởng!"
        )
    tip_lines = text_lines(tip_txt, 118, factor=0.76)
    cv.row(r_tip, max(64, tip_lines * 16 + 20))
    cv.merge(r_tip, 1, r_tip, 6, tip_txt, bold=False, font_size=9.5, align="left", text_wrap=True,
             bg_color=t.warn_fill, font_color=t.ink, indent=1)
    cv.box(r_cfg, 1, r_tip, 6, t.line)

    # Footer row — generous 28pt height, centered, NEVER clipped!
    r_foot = r_tip + 2
    cv.row(r_foot - 1, 10)
    cv.row(r_foot, 28)
    cv.row(r_foot + 1, 12)
    cv.merge(r_foot, 1, r_foot, 6,
             f"💛  Habit Tracker Collection v2.3 by Dyu  •  Unified 4-Tab Edition  •  {REPO_URL}",
             bold=False, font_size=9, italic=True, align="center", bg_color=t.page, font_color=t.muted)

    ws.hide_gridlines(2)
    ws.set_zoom(90)
    ws.set_tab_color(t.primary_dark)
    ws.set_landscape()
    ws.set_paper(9)
    ws.fit_to_pages(1, 0)
    ws.set_margins(0.35, 0.35, 0.4, 0.4)
    cv.flush()

    # Return 1-based last row including bottom gutter so PNG capture NEVER clips the footer!
    return {"linked_pictures": guide_sprite_slots, "guide_last_row": r_foot + 2}
