"""
hx.guide — Version 2.0 `📖 Hướng Dẫn` welcome screen & live animation config tab.

Covers all 5 mandatory Vietnamese guide blocks:
  1. Cách tick hằng ngày (click Checkbox trực tiếp — không cài gì, không Macro, không mạng)
  2. Cách reset dữ liệu mẫu trong 5 giây
  3. Cách tự thêm / sửa tên thói quen mà không hỏng công thức
  4. Cách đổi Tháng / Năm động (28/29/30/31 ngày + thứ tự nhảy)
  5. Cách tự đổi bộ ảnh hoạt ảnh (Tier A: Unhide `_Assets` -> dán 6 ảnh vào B2:B7; Tier B: `CFG_IMG_BASE`)
"""
from __future__ import annotations

from .core import Canvas, Theme, Styles, acell, qs, text_lines, REPO_URL

GUIDE_SHEET = "📖 Hướng Dẫn"


def build_guide(wb, styles: Styles, tracker_sheet: str, extra_tabs: list[tuple[str, str]],
                universal: bool = True, pro_365_offline: bool = False) -> dict:
    """Returns manifest info for Tier A COM Linked Pictures (6 stage previews)."""
    t: Theme = styles.t
    ws = wb.add_worksheet(GUIDE_SHEET)
    cv = Canvas(wb, ws, styles, GUIDE_SHEET, universal=universal)
    q = qs(GUIDE_SHEET)

    cv.col(0, 3.0)
    for c in range(1, 7):
        cv.col(c, 21.5)
    cv.col(7, 3.0)
    cv.row(0, 12)

    # ------------------------------------------------------------------ HERO BANNER
    cv.row(1, 34)
    cv.row(2, 22)
    cv.row(3, 21)
    cv.merge(1, 1, 1, 6, f"{t.emoji}  {t.name}  —  HƯỚNG DẪN SỬ DỤNG (v2.0)",
             font_name=t.font_title, font_size=18, bold=True, align="center",
             bg_color=t.primary, font_color=t.on_primary)
    cv.merge(2, 1, 2, 6, t.tagline_vi, font_size=10.5, italic=True, align="center",
             bg_color=t.soft, font_color=t.ink)
    mode_txt = (
        "✨ BẢN EXCEL OFFLINE MỌI MÁY (Excel 2016 / 2019 / 2021 / 365 • Windows & Mac)  •  KHÔNG MACRO  •  KHÔNG CẦN MẠNG  •  MỞ LÀ DÙNG NGAY"
        if universal else (
            "⚡ BẢN EXCEL 365 PRO OFFLINE (Ảnh nhúng trực tiếp vào ô — tốc độ 0ms, không cần Internet!)"
            if pro_365_offline else
            "☁️ BẢN GOOGLE SHEETS & EXCEL 365 CLOUD  •  Ảnh trực tuyến nhẹ gọn  •  Checkbox gốc & Lịch động"
        )
    )
    cv.merge(3, 1, 3, 6, mode_txt, font_size=8.8, bold=True, align="center",
             bg_color=t.card, font_color=t.primary_dark)
    cv.box(1, 1, 3, 6, t.line)
    cv.row(4, 12)

    # ------------------------------------------------------------------ TAB MAP
    r = 5
    cv.row(r, 24)
    cv.merge(r, 1, r, 6, "🗂️  CẤU TRÚC CÁC SHEET TRONG FILE", bold=True, font_size=10,
             align="left", indent=1, bg_color=t.primary, font_color=t.on_primary)
    tab_rows = [
        (GUIDE_SHEET, "Trang chào mừng, hướng dẫn sử dụng nhanh & bảng tùy chỉnh ngưỡng tăng trưởng."),
        (tracker_sheet, "Bảng theo dõi 31 ngày với ô tick Checkbox, hoạt ảnh 6 giai đoạn, biểu đồ & chuỗi Streak."),
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

    # Helper for crisp callout cards
    def info_card(start_r: int, c1: int, c2: int, title: str, bullets: list[str]) -> int:
        cv.row(start_r, 24)
        cv.merge(start_r, c1, start_r, c2, title, bold=True, font_size=9.8, align="left", indent=1,
                 bg_color=t.primary, font_color=t.on_primary)
        span_w = sum(cv.widths.get(c, 21.5) for c in range(c1, c2 + 1)) - 2
        cur = start_r + 1
        for b in bullets:
            lines = text_lines(b, span_w, factor=0.92)
            h = max(25, lines * 15 + 9)
            cv.row(cur, max(cv.heights.get(cur, 0), h))
            cv.merge(cur, c1, cur, c2, b, font_size=9.5, align="left", text_wrap=True,
                     bg_color=t.card, font_color=t.ink, indent=1)
            cv.hline(cur, c1, c2, t.line)
            cur += 1
        cv.box(start_r, c1, cur - 1, c2, t.line)
        return cur

    # ------------------------------------------------------------------ 2-COL CARDS (SEC 1 & SEC 2)
    sec1 = [
        "1️⃣  Mở tab Tracker chính và click thẳng vào ô vuông Checkbox (☑ / ☐) ở ngày tương ứng — KHÔNG cần gõ chữ, KHÔNG cần cài thêm gì, KHÔNG cần Internet!",
        "2️⃣  Mỗi khi bạn tick, ô ngày sẽ tự tô màu pastel dịu mắt, thanh % Completed tăng lên, biểu tượng phía trên cột ngày tự lớn lên theo 6 giai đoạn, và Biểu đồ + Streak Heatmap cập nhật ngay lập tức.",
        "3️⃣  Cột GOAL (Mục tiêu): nhập số ngày bạn muốn đạt trong tháng (vd: 20 ngày). Bỏ trống = mặc định tính cả tháng.",
    ]
    sec2 = [
        "⚡  File đã điền sẵn ~22 ngày dữ liệu mẫu để bạn xem ngay hiệu ứng hoạt ảnh & biểu đồ. Khi muốn bắt đầu tháng của riêng mình:",
        "🧹  Bước 1: Mở tab Tracker chính → kéo chuột chọn toàn bộ vùng ô tick từ C17 đến AG36 (hoặc nhấn Ctrl+G → gõ C17:AG36 → Enter).",
        "🧹  Bước 2: Nhấn phím Delete (trên Mac nhấn fn + Backspace) — toàn bộ ô vuông Checkbox lập tức bỏ tick sạch sẽ, giữ nguyên 100% công thức, màu sắc & hoạt ảnh!",
    ]
    end1 = info_card(r, 1, 3, "📌  1. CÁCH TICK HẰNG NGÀY (MỞ LÀ DÙNG)", sec1)
    end2 = info_card(r, 4, 6, "⚡  2. RESET DỮ LIỆU MẪU TRONG 5 GIÂY", sec2)
    r = max(end1, end2) + 1
    cv.row(r - 1, 12)

    # ------------------------------------------------------------------ 2-COL CARDS (SEC 3 & SEC 4)
    sec3 = [
        "✏️  Sửa tên thói quen: Gõ đè trực tiếp lên cột tên thói quen (B17:B28) — mọi biểu đồ & chuỗi streak giữ nguyên 100%!",
        "➕  Thêm thói quen (12 dòng Checkbox sẵn + 8 dòng mở rộng nhanh): Dòng 1–12 đã gắn sẵn ô Checkbox bấm 1 chạm; dòng 13–20 (B29:B36) đã nối sẵn công thức Streak + dropdown chọn ✓ (chỉ cần gõ tên thói quen là dùng ngay!).",
        "🚫  Lưu ý nhỏ: Để xóa thói quen không dùng, chỉ chọn ô tên rồi bấm Delete — KHÔNG bấm Delete Row để tránh ảnh hưởng dải liên kết.",
    ]
    sec4 = [
        "📅  Đổi Tháng & Năm động: Tại thẻ góc trên bên trái bảng Tracker (ô B3 & B5), nhấn mũi tên dropdown chọn Tháng (January–December) và Năm (2024–2040).",
        "✨  Toàn bộ số ngày (28 / 29 năm nhuận / 30 / 31) và thứ (Mon–Sun) tự động nhảy chuẩn xác! Ngày thừa cuối tháng (vd: ngày 29–31 tháng 2) tự động ẩn icon hoạt ảnh sạch sẽ.",
        "📑  Tạo thêm tháng mới: Chuột phải vào tab Tracker → Move or Copy → tick ☑ Create a copy → đổi tên tab → chọn tháng mới & reset vùng C17:AG36 trong 5 giây!",
    ]
    end3 = info_card(r, 1, 3, "🧩  3. THÊM / SỬA THÓI QUEN KHÔNG HỎNG CÔNG THỨC", sec3)
    end4 = info_card(r, 4, 6, "🗓️  4. ĐỔI THÁNG / NĂM & NHÂN BẢN SANG THÁNG MỚI", sec4)
    r = max(end3, end4) + 1
    cv.row(r - 1, 12)

    # ------------------------------------------------------------------ SEC 5: CUSTOM ANIMATION & THRESHOLDS
    r_cfg = r
    cv.row(r_cfg, 24)
    cv.merge(r_cfg, 1, r_cfg, 6,
             "🎨  5. TÙY CHỈNH ẢNH HOẠT ẢNH (CUSTOM ANIMATION) & NGƯỠNG TĂNG TRƯỞNG",
             bold=True, font_size=10, align="left", indent=1, bg_color=t.primary, font_color=t.on_primary)

    cur_r = r_cfg + 1
    if (not universal) and (not pro_365_offline):
        cv.row(cur_r, 26)
        cv.merge(cur_r, 1, cur_r, 2, "  🔗  Đường dẫn ảnh (CFG_IMG_BASE):", bold=True, font_size=9.5,
                 align="left", bg_color=t.soft, font_color=t.ink)
        cv.merge(cur_r, 3, cur_r, 6, t.img_base, font_size=8.5, align="left",
                 bg_color=t.warn_fill, font_color=t.ink, indent=1)
        wb.define_name("CFG_IMG_BASE", f"={q}!{acell(cur_r, 3)}")
        cv.hline(cur_r, 1, 6, t.line)
        cur_r += 1

    # Editable thresholds row (CFG_THR_1, CFG_THR_2, CFG_THR_3)
    r_thr = cur_r
    cv.row(r_thr, 25)
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
    cv.hline(r_thr, 1, 6, t.line)

    # 6-stage sprite preview strip
    r_shead = r_thr + 1
    r_simg = r_thr + 2
    r_sdesc = r_thr + 3
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
    guide_sprite_slots = []
    for idx, (st_title, st_sub) in enumerate(stage_meta):
        c = 1 + idx
        cv.put(r_shead, c, st_title, bold=True, font_size=9, align="center",
               bg_color=t.soft, font_color=t.ink)
        if universal:
            cv.put(r_simg, c, "", align="center", bg_color=t.card)
            guide_sprite_slots.append({"sheet": GUIDE_SHEET, "r1": r_simg, "c1": c,
                                       "r2": r_simg, "c2": c, "formula": f"=_Assets!$B${2 + idx}"})
        elif pro_365_offline:
            cv.put(r_simg, c, f"=INDEX(_Sprites!$A$1:$A$6,{idx + 1})", align="center", bg_color=t.card)
        else:
            cv.put(r_simg, c, f'=_xlfn.IMAGE(CFG_IMG_BASE&"stage_{idx}.png")', align="center", bg_color=t.card)
        cv.put(r_sdesc, c, st_sub, font_size=8.5, align="center", bg_color=t.card, font_color=t.muted)
    cv.grid(r_shead, 1, r_sdesc, 6, t.line)

    r_tip = r_sdesc + 1
    if universal:
        tip_txt = (
            "✨  CÁCH TỰ ĐỔI BỘ ẢNH HOẠT ẢNH RIÊNG (KHÔNG CẦN LINK / KHÔNG CẦN MẠNG):  "
            "1) Chuột phải vào tên bất kỳ tab nào ở thanh dưới cùng → chọn Unhide (Hiện trang tính) → chọn sheet `_Assets` → OK.  "
            "2) Xóa 6 ảnh cũ trong các ô B2 đến B7 (tương ứng Stage 0 → Stage 5) rồi Insert Picture / dán 6 ảnh PNG/sticker của riêng bạn vào đúng giữa các ô B2:B7.  "
            "3) Chuột phải vào tab `_Assets` → Hide để ẩn lại. Toàn bộ 31 ngày + Hero icon sẽ TỰ ĐỘNG biến thành bộ ảnh của bạn ngay lập tức!"
        )
    else:
        tip_txt = (
            "💡  Muốn tự thay bộ icon riêng trên Google Sheets / Excel 365? Tạo 6 file PNG (stage_0.png → stage_5.png), "
            "tải lên GitHub / Imgur public rồi dán đường dẫn thư mục gốc vào ô vàng CFG_IMG_BASE ở trên. "
            "Hoặc sửa 3 ô ngưỡng vàng (25% / 50% / 75%) để điều chỉnh tốc độ tăng trưởng!"
        )
    cv.row(r_tip, max(44, text_lines(tip_txt, 124) * 15 + 12))
    cv.merge(r_tip, 1, r_tip, 6, tip_txt, font_size=9.2, align="left", text_wrap=True,
             bg_color=t.warn_fill, font_color=t.ink, indent=1)
    cv.box(r_cfg, 1, r_tip, 6, t.line)

    # Footer
    r_foot = r_tip + 2
    cv.row(r_foot - 1, 10)
    cv.row(r_foot, 22)
    cv.merge(r_foot, 1, r_foot, 6,
             f"💛  Habit Tracker Collection v2.0 by Dyu  •  Zero-Install Universal Excel Edition  •  {REPO_URL}",
             font_size=8.5, italic=True, align="center", bg_color=t.page, font_color=t.muted)

    ws.hide_gridlines(2)
    ws.set_zoom(90)
    ws.set_tab_color(t.primary_dark)
    ws.set_landscape()
    ws.set_paper(9)
    ws.fit_to_pages(1, 0)
    ws.set_margins(0.35, 0.35, 0.4, 0.4)
    cv.flush()

    return {"linked_pictures": guide_sprite_slots, "guide_last_row": r_foot + 1}
