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

    is_7 = (t.num_stages == 7)
    is_8 = (t.num_stages == 8)
    is_digi = (t.num_stages >= 7)
    last_c = 8 if is_8 else (7 if is_7 else 6)  # 6 cols (B:G), 7 cols (B:H), or 8 cols (B:I for 2x4 8-stage!)
    col_w = 17.5 if is_8 else (19.2 if is_7 else 22.0)

    cv.col(0, 3.0)
    for c in range(1, last_c + 1):
        cv.col(c, col_w)
    cv.col(last_c + 1, 3.0)
    cv.row(0, 12)

    # ------------------------------------------------------------------ HERO BANNER (Rows 2..4)
    cv.row(1, 38)
    cv.row(2, 24)
    cv.row(3, 24)
    is_capy = t.slug.startswith("capybara_")
    if is_capy:
        ver_tag = "v3.9 Turbo" if edition == "pro_xlsm" else "v3.9"
    elif is_digi:
        ver_tag = "v3.8 Turbo" if edition == "pro_xlsm" else "v3.8"
    else:
        ver_tag = "v3.6 Turbo" if edition == "pro_xlsm" else "v3.5"
    cv.merge(1, 1, 1, last_c, f"{t.emoji}  {t.name}  —  HƯỚNG DẪN SỬ DỤNG ({ver_tag})",
             font_name=t.font_title, font_size=15.5, bold=True, align="center",
             bg_color=t.primary, font_color=t.on_primary)
    cv.merge(2, 1, 2, last_c, t.tagline_vi, font_size=10, italic=True, align="center",
             bg_color=t.soft, font_color=t.ink)

    if edition == "pro_xlsm":
        mode_txt = (
            f"⚡ BẢN PRO INTERACTIVE {ver_tag.upper()} (.XLSM)  •  Đổi Tháng/Ngày < 150ms + Hiệu ứng Pro & Ctrl+Z Undo  •  Tự lưu Đa Ngày/Tháng/Năm  •  100% Offline"
        )
    elif edition == "offline":
        mode_txt = f"✨ BẢN EXCEL OFFLINE KHÔNG MACRO ({ver_tag} .XLSX)  •  Gọn nhẹ 5 tab  •  Chạy mọi Excel 2016–365 Win/Mac  •  0 cảnh báo bảo mật"
    else:
        mode_txt = f"☁️ BẢN GOOGLE SHEETS EDITION ({ver_tag})  •  Font Be Vietnam Pro sắc nét  •  Cache _Assets + INDEX siêu mượt  •  Script 1-Click!"

    cv.merge(3, 1, 3, last_c, mode_txt, font_size=9, bold=True, align="center",
             bg_color=t.card, font_color=t.primary_dark)
    cv.box(1, 1, 3, last_c, t.line)
    r = 4

    # Google Sheets crisp 1-line 3-second tip banner right under hero!
    if gsheets:
        cv.row(r, 10)
        r += 1
        cv.row(r, 46)
        cv.merge(
            r, 1, r, last_c,
            "💡 Mẹo mở trên Google Sheets (3 giây): Chọn vùng ô TRUE/FALSE → Chèn (Insert) → Hộp kiểm (Checkbox) "
            "— HOẶC vào Tiện ích mở rộng (Extensions) → Apps Script → dán file google_sheets_1click_setup.gs và chạy setupHabitTracker() để bật Checkbox & tự động lưu 12 tháng vào _Database!",
            font_size=9.5, bold=False, align="left", indent=1, text_wrap=True,
            bg_color=t.warn_fill, font_color=t.ink,
        )
        cv.box(r, 1, r, last_c, t.warn_line)
        r += 1

    cv.row(r, 12)
    r += 1

    # ------------------------------------------------------------------ TAB MAP (5 CLEAN TABS)
    cv.row(r, 26)
    cv.merge(r, 1, r, last_c, f"🗂️  CẤU TRÚC 5 SHEET GỌN ĐẸP TRONG FILE ({ver_tag})", bold=True, font_size=10.5,
             align="left", indent=1, bg_color=t.primary, font_color=t.on_primary)

    if edition == "pro_xlsm":
        tracker_desc = "Bảng theo dõi 31 ngày siêu gọn: đổi dropdown Tháng (B3) / Năm (B5) tự lưu tháng cũ & tải tháng mới vào _Database!"
    elif edition == "offline":
        tracker_desc = f"Bảng theo dõi 31 ngày không Macro siêu nhẹ: lịch động, hoạt ảnh {t.num_stages} giai đoạn offline & Streak Heatmap!"
    else:
        tracker_desc = "Bảng theo dõi 31 ngày Google Sheets: kết hợp script 1-click để bật Checkbox & tự lưu/nạp 12 tháng trong _Database!"

    tab_rows = [
        (GUIDE_SHEET, f"Trang chào mừng, hướng dẫn nhanh & bảng tùy chỉnh ngưỡng tiến hóa {t.num_stages} giai đoạn."),
        (tracker_sheet, tracker_desc),
    ] + extra_tabs

    for idx, (tname, desc) in enumerate(tab_rows):
        rr = r + 1 + idx
        d_lines = text_lines(desc, 78, factor=0.80)
        cv.row(rr, max(32, d_lines * 16 + 14))
        bg = t.card if idx % 2 == 0 else t.page
        cv.merge(rr, 1, rr, 2, tname, bold=True, font_size=10, align="left", indent=1,
                 bg_color=bg, font_color=t.primary_dark)
        cv.merge(rr, 3, rr, last_c, desc, bold=False, font_size=10, align="left", indent=1, text_wrap=True,
                 bg_color=bg, font_color=t.ink)
        cv.hline(rr, 1, last_c, t.line)
    cv.box(r, 1, r + len(tab_rows), last_c, t.line)
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
            "⚡  Gọn đúng 5 tab đẹp mắt (kèm tab 📝 Nhiệm Vụ Ngày cho việc phát sinh!) nhờ sheet ẩn _Database lưu riêng dữ liệu 12 tháng & từng ngày.",
            "🧹  Reset nhanh trên Google Sheets: chọn vùng Checkbox C17:AG36 → nhấn Space (hoặc Delete) để bỏ tick sạch sẽ.",
            "✨  Hoạt ảnh =IMAGE() động 6 giai đoạn tự cập nhật cho cả 31 ngày, Monthly Hero, Nhiệm Vụ Ngày, Yearly Goals & Thành Tựu Năm!",
        ]

    split_c = 4 if is_8 else 3
    end1 = info_card(r, 1, split_c, "📌  1. CÁCH SỬ DỤNG & TICK HẰNG NGÀY", sec1)
    end2 = info_card(r, split_c + 1, last_c, "⚡  2. DỮ LIỆU MẪU, RESET & SANG THÁNG MỚI", sec2)
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

    end3 = info_card(r, 1, split_c, "🧩  3. TÙY BIẾN THÓI QUEN & MỤC TIÊU NĂM", sec3)
    end4 = info_card(r, split_c + 1, last_c, "🏆  4. LỊCH ĐỘNG, ĐA THÁNG/NĂM & THÀNH TỰU", sec4)
    r = max(end3, end4) + 1
    cv.row(r - 1, 12)

    # ------------------------------------------------------------------ SEC 5: CUSTOM ANIMATION & THRESHOLDS
    r_cfg = r
    cv.row(r_cfg, 26)
    sec5_title = (
        "⚡  5. HOẠT ẢNH TIẾN HÓA 8 GIAI ĐOẠN (ULTRA DIGIVOLUTION 0% → 100%) & TÙY CHỈNH NGƯỠNG"
        if is_8 else (
            "⚡  5. HOẠT ẢNH TIẾN HÓA 7 GIAI ĐOẠN (DIGIVOLUTION 0% → 100%) & TÙY CHỈNH NGƯỠNG"
            if is_7 else
            "🎨  5. HOẠT ẢNH 6 GIAI ĐOẠN (LIVE GROWTH ANIMATION) & TÙY CHỈNH NGƯỠNG"
        )
    )
    cv.merge(r_cfg, 1, r_cfg, last_c, sec5_title,
             bold=True, font_size=10.5, align="left", indent=1, bg_color=t.primary, font_color=t.on_primary)

    cur_r = r_cfg + 1
    # Threshold bar — 3 thresholds (6-stage), 4 thresholds (7-stage), or 5 thresholds (8-stage Ultra!)
    r_thr = cur_r
    guide_sprite_slots = []
    if is_8:
        cv.row(r_thr, 26)
        cv.row(r_thr + 1, 26)
        # Row 1 (3 thresholds across B:I -> 2+1, 2+1, 1+1? Better: clean 2-col pairs across 8 cols -> 3 pairs + final!)
        # Actually: Row 1: Stage 2 (15%) [1..2, 3] | Stage 3 (30%) [4..5, 6] | Stage 4 (50%) [7, 8] -> clean!
        cv.merge(r_thr, 1, r_thr, 2, "Ngưỡng Stage 2 (Baby II):", bold=True, font_size=9.0, align="center", bg_color=t.soft, font_color=t.ink)
        cv.put(r_thr, 3, 0.15, bold=True, font_size=10, align="center", num_format="0%", bg_color=t.warn_fill, font_color=t.primary_dark)
        cv.merge(r_thr, 4, r_thr, 5, "Ngưỡng Stage 3 (Rookie):", bold=True, font_size=9.0, align="center", bg_color=t.soft, font_color=t.ink)
        cv.put(r_thr, 6, 0.30, bold=True, font_size=10, align="center", num_format="0%", bg_color=t.warn_fill, font_color=t.primary_dark)
        cv.put(r_thr, 7, "Stage 4 (Champion):", bold=True, font_size=8.8, align="center", bg_color=t.soft, font_color=t.ink)
        cv.put(r_thr, 8, 0.50, bold=True, font_size=10, align="center", num_format="0%", bg_color=t.warn_fill, font_color=t.primary_dark)
        # Row 2: Stage 5 (70%) [1..2, 3] | Stage 6 Mega / Grown (85%) [4..5, 6] | Stage 7 Ultra/Burst [7..8]
        cv.merge(r_thr + 1, 1, r_thr + 1, 2, "Ngưỡng Stage 5 (Ultimate):", bold=True, font_size=9.0, align="center", bg_color=t.soft, font_color=t.ink)
        cv.put(r_thr + 1, 3, 0.70, bold=True, font_size=10, align="center", num_format="0%", bg_color=t.warn_fill, font_color=t.primary_dark)
        cv.merge(r_thr + 1, 4, r_thr + 1, 5, "Ngưỡng Stage 6 • Đạt (Mega):", bold=True, font_size=9.0, align="center", bg_color=t.soft, font_color=t.ink)
        cv.put(r_thr + 1, 6, 0.85, bold=True, font_size=10, align="center", num_format="0%", bg_color=t.warn_fill, font_color=t.primary_dark)
        cv.merge(r_thr + 1, 7, r_thr + 1, 8, "Stage 7 Ultra / Burst: 100% ✨", bold=True, font_size=9.0, align="center", bg_color=t.primary, font_color=t.on_primary)

        wb.define_name("CFG_THR_M1", f"={q}!{acell(r_thr, 3)}")
        wb.define_name("CFG_THR_0", f"={q}!{acell(r_thr, 6)}")
        wb.define_name("CFG_THR_1", f"={q}!{acell(r_thr, 8)}")
        wb.define_name("CFG_THR_2", f"={q}!{acell(r_thr + 1, 3)}")
        wb.define_name("CFG_THR_3", f"={q}!{acell(r_thr + 1, 6)}")
        cv.grid(r_thr, 1, r_thr + 1, last_c, t.line)

        # Clean 2-Row x 4-Card Evolution Gallery (ZERO squished text or sprites!)
        snames = t.stage_names or ["Digi-Egg", "Baby I", "Baby II", "Rookie", "Champion", "Ultimate", "Mega", "Ultra"]
        pct_subs = [
            "0% (Chờ nở)",
            "1% – 14% (Baby I)",
            "15% – 29% (Baby II)",
            "30% – 49% (Rookie)",
            "50% – 69% (Champion)",
            "70% – 84% (Ultimate)",
            "85% – 99% (Mega • Đạt)",
            "100% ULTRA / BURST ✨",
        ]
        r_cur = r_thr + 2
        for row_grp in (range(0, 4), range(4, 8)):
            r_sh, r_si, r_sd = r_cur, r_cur + 1, r_cur + 2
            cv.row(r_sh, 26)
            cv.row(r_si, 94)
            cv.row(r_sd, 24)
            for pos, idx in enumerate(row_grp):
                c1, c2 = 1 + pos * 2, 2 + pos * 2
                is_final = (idx == 7)
                cv.merge(r_sh, c1, r_sh, c2, f"S{idx} • {snames[idx]}", bold=True, font_size=9.4, align="center",
                         bg_color=(t.primary if is_final else t.soft),
                         font_color=(t.on_primary if is_final else t.ink))
                if universal:
                    cv.merge(r_si, c1, r_si, c2, "", align="center", bg_color=t.card)
                    guide_sprite_slots.append({"name": f"Guide_Stage{idx}", "sheet": GUIDE_SHEET,
                                               "r1": r_si, "c1": c1, "r2": r_si, "c2": c2,
                                               "formula": f"=_Assets!$B${2 + idx}"})
                else:
                    cv.merge(r_si, c1, r_si, c2, f"=_Assets!$B${2 + idx}",
                             align="center", bg_color=t.card)
                cv.merge(r_sd, c1, r_sd, c2, pct_subs[idx], bold=is_final, font_size=8.8, align="center",
                         bg_color=(t.soft if is_final else t.card),
                         font_color=(t.primary_dark if is_final else t.muted))
            r_cur += 3
        r_sdesc = r_cur - 1
        cv.grid(r_thr + 2, 1, r_sdesc, last_c, t.line)
    else:
        if is_7:
            cv.row(r_thr, 26)
            cv.row(r_thr + 1, 26)
            cv.merge(r_thr, 1, r_thr, 2, "Ngưỡng Stage 2 (Baby II):", bold=True, font_size=9.2, align="center", bg_color=t.soft, font_color=t.ink)
            cv.put(r_thr, 3, 0.20, bold=True, font_size=10, align="center", num_format="0%", bg_color=t.warn_fill, font_color=t.primary_dark)
            cv.merge(r_thr, 4, r_thr, 6, "Ngưỡng Stage 3 (Rookie):", bold=True, font_size=9.2, align="center", bg_color=t.soft, font_color=t.ink)
            cv.put(r_thr, 7, 0.40, bold=True, font_size=10, align="center", num_format="0%", bg_color=t.warn_fill, font_color=t.primary_dark)
            cv.merge(r_thr + 1, 1, r_thr + 1, 2, "Ngưỡng Stage 4 (Champion):", bold=True, font_size=9.2, align="center", bg_color=t.soft, font_color=t.ink)
            cv.put(r_thr + 1, 3, 0.60, bold=True, font_size=10, align="center", num_format="0%", bg_color=t.warn_fill, font_color=t.primary_dark)
            cv.merge(r_thr + 1, 4, r_thr + 1, 6, "Ngưỡng Stage 5 • Đạt (Ultimate):", bold=True, font_size=9.2, align="center", bg_color=t.soft, font_color=t.ink)
            cv.put(r_thr + 1, 7, 0.80, bold=True, font_size=10, align="center", num_format="0%", bg_color=t.warn_fill, font_color=t.primary_dark)
            wb.define_name("CFG_THR_0", f"={q}!{acell(r_thr, 3)}")
            wb.define_name("CFG_THR_1", f"={q}!{acell(r_thr, 7)}")
            wb.define_name("CFG_THR_2", f"={q}!{acell(r_thr + 1, 3)}")
            wb.define_name("CFG_THR_3", f"={q}!{acell(r_thr + 1, 7)}")
            cv.grid(r_thr, 1, r_thr + 1, last_c, t.line)
            r_shead = r_thr + 2
        else:
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
            r_shead = r_thr + 1

        # Stage headers, airy 94pt sprite row, descriptions (6 stages OR 7 Digimon stages!)
        r_simg = r_shead + 1
        r_sdesc = r_shead + 2
        cv.row(r_shead, 26 if is_7 else 24)
        cv.row(r_simg, 96 if is_7 else 94)
        cv.row(r_sdesc, 34 if is_7 else 24)
        if is_7:
            snames = t.stage_names or ["Digi-Egg", "Baby I", "Baby II", "Rookie", "Champion", "Ultimate", "Mega"]
            pct_subs = [
                "0%\n(Chờ nở)",
                "1% – 19%\n(Baby I)",
                "20% – 39%\n(Baby II)",
                "40% – 59%\n(Rookie)",
                "60% – 79%\n(Champion)",
                "80% – 99%\n(Ultimate)",
                "100% MEGA ✨\n(Tối thượng!)",
            ]
            stage_meta = [(f"S{i} • {snames[i]}", pct_subs[i]) for i in range(7)]
        else:
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
            is_mega = is_7 and (idx == 6)
            cv.put(r_shead, c, st_title, bold=True, font_size=(8.8 if is_7 else 9.5), align="center",
                   bg_color=(t.primary if is_mega else t.soft),
                   font_color=(t.on_primary if is_mega else t.ink))
            if universal:
                cv.put(r_simg, c, "", align="center", bg_color=t.card)
                guide_sprite_slots.append({"name": f"Guide_Stage{idx}", "sheet": GUIDE_SHEET,
                                           "r1": r_simg, "c1": c, "r2": r_simg, "c2": c,
                                           "formula": f"=_Assets!$B${2 + idx}"})
            else:
                cv.put(r_simg, c, f"=_Assets!$B${2 + idx}", align="center", bg_color=t.card)
            cv.put(r_sdesc, c, st_sub, bold=is_mega, font_size=8.6, align="center", text_wrap=True,
                   bg_color=(t.soft if is_mega else t.card),
                   font_color=(t.primary_dark if is_mega else t.muted))
        cv.grid(r_shead, 1, r_sdesc, last_c, t.line)

    # Tip Box — ZERO markdown backticks, generous height + indent=1!
    r_tip = r_sdesc + 1
    slot_range_txt = f"B2:B{1 + t.num_stages} (Stage 0 → Stage {t.max_stage_idx})"
    if edition == "pro_xlsm":
        tip_txt = (
            f"✨  CÁCH TỰ ĐỔI BỘ ẢNH HOẠT ẢNH RIÊNG (KHÔNG CẦN LINK / KHÔNG CẦN MẠNG):  "
            f"1) Chuột phải tên tab bất kỳ → chọn Unhide → chọn _Assets → OK.  "
            f"2) Thay {t.num_stages} ảnh trong ô {slot_range_txt} bằng ảnh PNG/sticker của bạn.  "
            f"3) Bấm nút 🔄 Đồng bộ {t.num_stages} ảnh mới (SyncSpritesFromAssets) ngay trên _Assets rồi ẩn lại → toàn bộ 31 ngày, Hero & 12 tháng cập nhật ngay lập tức!"
        )
    elif universal:
        tip_txt = (
            f"✨  CÁCH TỰ ĐỔI BỘ ẢNH HOẠT ẢNH RIÊNG (KHÔNG CẦN LINK / KHÔNG CẦN MẠNG):  "
            f"1) Chuột phải tên tab bất kỳ → chọn Unhide → chọn _Assets → OK.  "
            f"2) Thay {t.num_stages} ảnh trong ô {slot_range_txt} bằng ảnh PNG/sticker của bạn.  "
            f"3) Ẩn lại _Assets → toàn bộ 31 ngày, Monthly Hero, Yearly Goals & 12 tháng Tổng Kết Năm tự động đổi theo ảnh của bạn!"
        )
    else:
        tip_txt = (
            f"💡  Muốn tự thay bộ icon riêng trên Google Sheets? Mở sheet ẩn _Assets (Xem → Trang tính ẩn → _Assets) "
            f"và sửa trực tiếp {t.num_stages} công thức =IMAGE(...) trong ô {slot_range_txt} — toàn bộ 31 ngày, Hero & 12 tháng tự đồng bộ siêu tốc nhờ bộ nhớ đệm INDEX!"
        )
    tip_lines = text_lines(tip_txt, 118, factor=0.76)
    cv.row(r_tip, max(64, tip_lines * 16 + 20))
    cv.merge(r_tip, 1, r_tip, last_c, tip_txt, bold=False, font_size=9.5, align="left", text_wrap=True,
             bg_color=t.warn_fill, font_color=t.ink, indent=1)
    cv.box(r_cfg, 1, r_tip, last_c, t.line)

    # Footer row — generous 28pt height, centered, NEVER clipped!
    r_foot = r_tip + 2
    cv.row(r_foot - 1, 10)
    cv.row(r_foot, 28)
    cv.row(r_foot + 1, 12)
    foot_ver = (
        f"{ver_tag} by Dyu  •  Sub-150ms Native Sprite Engine & Pro FX + Ctrl+Z Undo"
        if edition == "pro_xlsm" else
        f"{ver_tag} by Dyu  •  Unified 5-Tab Habit Tracker Collection"
    )
    cv.merge(r_foot, 1, r_foot, last_c,
             f"💛  Habit Tracker Collection {foot_ver}  •  {REPO_URL}",
             bold=False, font_size=9, italic=True, align="center", bg_color=t.page, font_color=t.muted)

    wb.define_name("ANCHOR_GUIDE", f"={q}!$B$2")

    ws.hide_gridlines(2)
    ws.set_zoom(90)
    ws.set_tab_color(t.primary_dark)
    ws.set_landscape()
    ws.set_paper(9)
    ws.fit_to_pages(1, 0)
    ws.set_margins(0.35, 0.35, 0.4, 0.4)
    cv.flush()

    # Return 1-based last row & last col including gutter so PNG capture NEVER clips!
    return {
        "linked_pictures": guide_sprite_slots,
        "guide_last_row": r_foot + 2,
        "guide_last_col": "J" if is_8 else ("I" if is_7 else "H"),
    }
