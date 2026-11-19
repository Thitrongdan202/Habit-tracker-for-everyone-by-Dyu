"""
hx.guide — Beautiful, self-contained `📖 Hướng Dẫn` first tab for every workbook.

Defines the workbook-level Named Ranges used by the tracker formulas:
  - ImgBase : base URL ending with `/` where stage_0.png .. stage_5.png live
  - Thr1    : 25% (stage 2 threshold)
  - Thr2    : 50% (stage 3 threshold)
  - Thr3    : 75% (stage 4 + Monthly Grown Counter threshold)
"""
from __future__ import annotations

from .core import Canvas, Theme, Styles, acell, qs, text_lines, REPO_URL

GUIDE_SHEET = "📖 Hướng Dẫn"


def build_guide(wb, styles: Styles, tracker_sheet: str, extra_tabs: list[tuple[str, str]],
                offline_sprites: bool = False) -> Canvas:
    t: Theme = styles.t
    ws = wb.add_worksheet(GUIDE_SHEET)
    cv = Canvas(wb, ws, styles, GUIDE_SHEET)
    q = qs(GUIDE_SHEET)

    # Columns A..H: A gutter | B..G content cards (6 equal cols -> great for 6 stages!) | H gutter
    cv.col(0, 3.0)
    for c in range(1, 7):
        cv.col(c, 21.5)
    cv.col(7, 3.0)

    cv.row(0, 12)

    # ------------------------------------------------------------------ HERO BANNER
    cv.row(1, 34)
    cv.row(2, 22)
    cv.row(3, 20)
    cv.merge(1, 1, 1, 6, f"{t.emoji}  {t.name}  —  HƯỚNG DẪN SỬ DỤNG",
             font_name=t.font_title, font_size=18, bold=True, align="center",
             bg_color=t.primary, font_color=t.on_primary)
    cv.merge(2, 1, 2, 6, t.tagline_vi, font_size=10.5, italic=True, align="center",
             bg_color=t.soft, font_color=t.ink)
    mode_txt = ("⚡ Phiên bản OFFLINE PRO (ảnh nhúng sẵn — hoạt động không cần Internet trên Excel 365)"
                if offline_sprites else
                "✨ Tương thích Excel 365 & Google Sheets  •  Tự động cập nhật lịch, hoạt ảnh tăng trưởng, streak & biểu đồ")
    cv.merge(3, 1, 3, 6, mode_txt, font_size=9, align="center", bg_color=t.card, font_color=t.muted)
    cv.box(1, 1, 3, 6, t.line)

    cv.row(4, 12)

    # ------------------------------------------------------------------ TAB MAP CARD
    r = 5
    cv.row(r, 24)
    cv.merge(r, 1, r, 6, "🗂️  CẤU TRÚC CÁC SHEET TRONG TEMPLATE", bold=True, font_size=10,
             align="left", indent=1, bg_color=t.primary, font_color=t.on_primary)
    tab_rows = [
        (GUIDE_SHEET, "Trang hướng dẫn & bảng cấu hình ảnh hoạt ảnh / ngưỡng phần trăm (bạn đang ở đây)."),
        (tracker_sheet, "Bảng theo dõi thói quen hằng ngày (31 ngày) với hoạt ảnh 6 giai đoạn, biểu đồ & chuỗi streak."),
    ] + extra_tabs
    for idx, (tname, desc) in enumerate(tab_rows):
        rr = r + 1 + idx
        cv.row(rr, 22)
        bg = t.card if idx % 2 == 0 else t.page
        cv.merge(rr, 1, rr, 2, f"  {tname}", bold=True, font_size=9.5, align="left",
                 bg_color=bg, font_color=t.primary_dark)
        cv.merge(rr, 3, rr, 6, desc, font_size=9.5, align="left", text_wrap=True,
                 bg_color=bg, font_color=t.ink)
        cv.hline(rr, 1, 6, t.line)
    cv.box(r, 1, r + len(tab_rows), 6, t.line)

    r = r + len(tab_rows) + 2
    cv.row(r - 1, 12)

    # ------------------------------------------------------------------ 2-COLUMN CARDS (SEC 1 & SEC 2)
    def info_card(start_r: int, c1: int, c2: int, title: str, bullets: list[str]) -> int:
        cv.row(start_r, 24)
        cv.merge(start_r, c1, start_r, c2, title, bold=True, font_size=10, align="left", indent=1,
                 bg_color=t.primary, font_color=t.on_primary)
        span_w = sum(cv.widths.get(c, 19.5) for c in range(c1, c2 + 1)) - 2
        cur = start_r + 1
        for b in bullets:
            lines = text_lines(b, span_w, factor=0.92)
            h = max(24, lines * 15 + 8)
            cv.row(cur, max(cv.heights.get(cur, 0), h))
            cv.merge(cur, c1, cur, c2, b, font_size=9.5, align="left", text_wrap=True,
                     bg_color=t.card, font_color=t.ink, indent=1)
            cv.hline(cur, c1, c2, t.line)
            cur += 1
        cv.box(start_r, c1, cur - 1, c2, t.line)
        return cur

    sec1 = [
        "1️⃣  Mở tab theo dõi chính và nhấn vào ô checkbox (☑ / ☐) ở ngày tương ứng mỗi khi hoàn thành một thói quen.",
        "2️⃣  Nếu dùng Excel phiên bản cũ không có Checkbox: bạn chỉ cần gõ chữ TRUE hoặc ký hiệu ✓ (copy sẵn: ✓) vào ô ngày — công thức vẫn tự động tính chính xác 100%!",
        "3️⃣  Quan sát thanh % Completed tăng lên: biểu tượng phía trên mỗi ngày sẽ tự động chuyển qua 6 giai đoạn phát triển, đồng thời Biểu đồ tiến độ & Streak Heatmap cập nhật ngay lập tức.",
        "4️⃣  Cột GOAL (Mục tiêu): nhập số ngày bạn muốn đạt trong tháng cho từng thói quen (ví dụ 20 ngày). Bỏ trống = mặc định cả tháng.",
    ]
    sec2 = [
        "✅  20 DÒNG NỐI SẴN CÔNG THỨC: Bảng đã chuẩn bị sẵn 20 dòng thói quen (8–10 dòng mẫu gợi ý + 10–12 dòng trống đã gắn sẵn checkbox, thanh tiến độ & công thức streak).",
        "✏️  Thêm thói quen mới siêu nhanh: Chỉ cần gõ tên thói quen vào dòng trống bất kỳ (dòng 11–20) rồi tick! Mọi biểu đồ, tổng ngày & streak tự động tính thêm mà KHÔNG làm hỏng công thức.",
        "🧹  Xóa/sửa mẫu gợi ý: Chọn cột tên thói quen hoặc vùng checkbox rồi nhấn phím Delete (KHÔNG xóa nguyên hàng/cột).",
        "➕  Cần hơn 20 thói quen? Chuột phải vào số thứ tự dòng thứ 19 → Copy → chuột phải dòng 20 → Insert Copied Cells. Toàn bộ công thức ẩn (cột BI:CM) sẽ tự nhân bản theo!",
    ]

    end1 = info_card(r, 1, 3, "📌  1. CÁCH SỬ DỤNG HẰNG NGÀY", sec1)
    # Spacer look via double-card border between col 3 and 4
    end2 = info_card(r, 4, 6, "🧩  2. THÊM THÓI QUEN MỚI KHÔNG HỎNG CÔNG THỨC", sec2)
    r = max(end1, end2) + 1
    cv.row(r - 1, 12)

    # ------------------------------------------------------------------ SEC 3 (MONTH/YEAR & DUPLICATE)
    sec3 = [
        "📅  Đổi Tháng & Năm động: Tại góc trên bên trái bảng Tracker, nhấn mũi tên dropdown để chọn Tháng (January–December) và Năm (2024–2040). Toàn bộ số ngày (28/29/30/31) và thứ trong tuần (Mon–Sun) sẽ tự tính lại, ngày thừa (như ngày 31 của tháng 4) tự ẩn sạch sẽ!",
        "📑  Nhân bản sang tháng mới: Chuột phải vào tên tab Tracker ở thanh dưới → chọn Move or Copy → tick ☑ Create a copy → OK. Đổi tên tab (vd: Tháng 11), chọn lại Tháng mới trong dropdown, rồi quét chọn vùng checkbox (C17:AG36) bấm Space/Delete để reset sạch cho tháng mới.",
    ]
    r = info_card(r, 1, 6, "🗓️  3. ĐỔI THÁNG / NĂM & NHÂN BẢN SANG THÁNG MỚI", sec3) + 1
    cv.row(r - 1, 12)

    # ------------------------------------------------------------------ SEC 4: LIVE ANIMATION CONFIG & 6-STAGE PREVIEW
    r_cfg = r
    cv.row(r_cfg, 24)
    cv.merge(r_cfg, 1, r_cfg, 6, "🎨  4. TÙY CHỈNH ẢNH HOẠT ẢNH & NGƯỠNG TĂNG TRƯỞNG (LIVE CONFIG)",
             bold=True, font_size=10, align="left", indent=1, bg_color=t.primary, font_color=t.on_primary)

    # Row: CFG_IMG_BASE editable cell
    r_url = r_cfg + 1
    cv.row(r_url, 26)
    cv.merge(r_url, 1, r_url, 2, "  🔗  Đường dẫn ảnh (CFG_IMG_BASE):", bold=True, font_size=9.5,
             align="left", bg_color=t.soft, font_color=t.ink)
    cv.merge(r_url, 3, r_url, 6, t.img_base, font_size=8.5, align="left",
             bg_color=t.warn_fill, font_color=t.ink, indent=1)
    img_base_ref = f"{q}!{acell(r_url, 3)}"
    wb.define_name("CFG_IMG_BASE", f"={img_base_ref}")

    # Row: Editable thresholds CFG_THR_1, CFG_THR_2, CFG_THR_3
    r_thr = r_cfg + 2
    cv.row(r_thr, 24)
    cv.put(r_thr, 1, "Ngưỡng Stage 2:", bold=True, font_size=9, align="right", bg_color=t.soft)
    cv.put(r_thr, 2, 0.25, bold=True, font_size=10, align="center", num_format="0%",
           bg_color=t.warn_fill, font_color=t.primary_dark)
    cv.put(r_thr, 3, "Ngưỡng Stage 3:", bold=True, font_size=9, align="right", bg_color=t.soft)
    cv.put(r_thr, 4, 0.50, bold=True, font_size=10, align="center", num_format="0%",
           bg_color=t.warn_fill, font_color=t.primary_dark)
    cv.put(r_thr, 5, "Ngưỡng Đạt (Grown):", bold=True, font_size=9, align="right", bg_color=t.soft)
    cv.put(r_thr, 6, 0.75, bold=True, font_size=10, align="center", num_format="0%",
           bg_color=t.warn_fill, font_color=t.primary_dark)
    wb.define_name("CFG_THR_1", f"={q}!{acell(r_thr, 2)}")
    wb.define_name("CFG_THR_2", f"={q}!{acell(r_thr, 4)}")
    wb.define_name("CFG_THR_3", f"={q}!{acell(r_thr, 6)}")
    cv.hline(r_url, 1, 6, t.line)
    cv.hline(r_thr, 1, 6, t.line)

    # Row: Live 6-stage sprite preview strip!
    r_shead = r_cfg + 3
    r_simg = r_cfg + 4
    r_sdesc = r_cfg + 5
    cv.row(r_shead, 20)
    cv.row(r_simg, 76)
    cv.row(r_sdesc, 22)
    stage_meta = [
        ("Stage 0", "0% (Chưa bắt đầu)"),
        ("Stage 1", "1% – 24% (Khởi động)"),
        ("Stage 2", "25% – 49% (Đang lớn)"),
        ("Stage 3", "50% – 74% (Ổn định)"),
        ("Stage 4", "75% – 99% (Sắp trọn vẹn)"),
        ("Stage 5", "100% (Hoàn hảo ✨)"),
    ]
    for idx, (st_title, st_sub) in enumerate(stage_meta):
        c = 1 + idx
        cv.put(r_shead, c, st_title, bold=True, font_size=9, align="center",
               bg_color=t.soft, font_color=t.ink)
        if offline_sprites:
            f_img = f"=INDEX(_Sprites!$A$1:$A$6,{idx + 1})"
        else:
            f_img = f'=_xlfn.IMAGE(CFG_IMG_BASE&"stage_{idx}.png")'
        cv.put(r_simg, c, f_img, align="center", bg_color=t.card)
        cv.put(r_sdesc, c, st_sub, font_size=8.5, align="center", bg_color=t.card, font_color=t.muted)
    cv.grid(r_shead, 1, r_sdesc, 6, t.line)

    r_tip = r_cfg + 6
    tip_txt = ("💡  Muốn tự thay bộ icon riêng? Tạo 6 file PNG đặt tên stage_0.png → stage_5.png (nền trong suốt 256×256px), "
               "tải lên GitHub / Imgur / Google Drive public, sau đó dán link thư mục gốc vào ô vàng CFG_IMG_BASE ở trên. "
               "Hoặc sửa 3 ô ngưỡng vàng (25% / 50% / 75%) để điều chỉnh độ khó tăng trưởng!")
    cv.row(r_tip, max(36, text_lines(tip_txt, 114) * 15 + 8))
    cv.merge(r_tip, 1, r_tip, 6, tip_txt, font_size=9, italic=True, align="left", text_wrap=True,
             bg_color=t.warn_fill, font_color=t.ink, indent=1)
    cv.box(r_cfg, 1, r_tip, 6, t.line)

    r = r_tip + 2
    cv.row(r - 1, 12)

    # ------------------------------------------------------------------ SEC 5: COMPATIBILITY TABLE
    cv.row(r, 24)
    cv.merge(r, 1, r, 6, "⚙️  5. TƯƠNG THÍCH EXCEL 365 • EXCEL CŨ • GOOGLE SHEETS & XỬ LÝ SỰ CỐ",
             bold=True, font_size=10, align="left", indent=1, bg_color=t.primary, font_color=t.on_primary)
    r_th = r + 1
    cv.row(r_th, 22)
    cv.put(r_th, 1, "Nền tảng", bold=True, font_size=9, align="center", bg_color=t.soft)
    cv.put(r_th, 2, "Checkbox & Biểu đồ", bold=True, font_size=9, align="center", bg_color=t.soft)
    cv.put(r_th, 3, "Hoạt ảnh =IMAGE()", bold=True, font_size=9, align="center", bg_color=t.soft)
    cv.merge(r_th, 4, r_th, 6, "Ghi chú & Cách bật nhanh", bold=True, font_size=9, align="center", bg_color=t.soft)

    compat = [
        ("Microsoft Excel 365\n(Desktop & Web)", "✅ Hỗ trợ đầy đủ\n(Click tick mượt)", "✅ Hiển thị trực tiếp",
         "Nếu thấy thông báo vàng 'Security Warning: External Data / Connected Images' ở thanh trên → bấm Enable Content / Trust to show images. Hoặc dùng bản Offline Pro trong thư mục pro_macro/ để không cần Internet!"),
        ("Google Sheets\n(Miễn phí 100%)", "✅ Tự động chuyển\nthành ô Checkbox", "✅ Hiển thị siêu mượt",
         "Mở Google Drive → Tải file .xlsx lên → Mở bằng Google Trang tính (Google Sheets) → Tệp → Lưu dưới dạng Google Trang tính. Toàn bộ hàm =IMAGE(), lịch động, biểu đồ & heatmap chạy mượt!"),
        ("Excel 2016 / 2019 / 2021\n(Bản cũ không có 365)", "⚡ Nhập ✓ hoặc TRUE\nthay cho Checkbox", "⚠️ Không có hàm IMAGE\n(Dùng VBA đi kèm)",
         "Excel bản cũ hiển thị TRUE/FALSE thay cho ô tick và chưa hỗ trợ hàm IMAGE(). Bạn có thể nhập ✓/TRUE (mọi biểu đồ, streak & data bar vẫn chạy tốt!) hoặc import file VBA trong thư mục vba_scripts/ để bật click-toggle & đổi ảnh offline."),
    ]
    for i, (plat, chk, img_s, note) in enumerate(compat):
        rr = r_th + 1 + i
        lines = text_lines(note, 56, factor=0.92)
        cv.row(rr, max(44, lines * 14 + 12))
        bg = t.card if i % 2 == 0 else t.page
        cv.put(rr, 1, plat, bold=True, font_size=9, align="center", text_wrap=True, bg_color=bg, font_color=t.ink)
        cv.put(rr, 2, chk, font_size=9, align="center", text_wrap=True, bg_color=bg, font_color=t.ink)
        cv.put(rr, 3, img_s, font_size=9, align="center", text_wrap=True, bg_color=bg, font_color=t.ink)
        cv.merge(rr, 4, rr, 6, note, font_size=9, align="left", text_wrap=True, bg_color=bg, font_color=t.ink, indent=1)
        cv.hline(rr, 1, 6, t.line)
    cv.grid(r_th, 1, r_th + len(compat), 6, t.line)
    cv.box(r, 1, r_th + len(compat), 6, t.line)

    # Footer
    r_foot = r_th + len(compat) + 2
    cv.row(r_foot - 1, 10)
    cv.row(r_foot, 22)
    cv.merge(r_foot, 1, r_foot, 6,
             f"💛  Habit Tracker Collection by Dyu  •  Mã nguồn & bộ ảnh mở tại: {REPO_URL}",
             font_size=8.5, italic=True, align="center", bg_color=t.page, font_color=t.muted)

    ws.hide_gridlines(2)
    ws.set_zoom(90)
    ws.set_tab_color(t.primary_dark)
    ws.set_landscape()
    ws.set_paper(9)
    ws.fit_to_pages(1, 0)
    ws.set_margins(0.35, 0.35, 0.4, 0.4)

    cv.flush()
    return cv
