"""
hx.vocab_builder — Complete 4-Edition Chiikawa Vocabulary Tracker Builder (#96–#100):
  1. Desktop editions (`pro_xlsm`, `offline`, `gsheets`):
       - Tab 1: `📚 Kho Từ Vựng` (Bespoke per-theme schema, Dashboard KPIs, dynamic Chiikawa
         Mascot S0..S5, 1-click Quiz Mode CF toggles, 100 ready rows with 15 domain sample words)
       - Tab 2: `🎯 Luyện Tập & Lịch Ôn` (Daily goals, 5-step Active Study Checklist, dynamic
         Top-15 Priority/Urgent Review table via universal IF/COUNTIF/INDEX/MATCH, cheering Mascot)
       - Tab 3: `📊 Thống Kê & Thành Tựu` (Mastery Doughnut Chart, Theme-specific Breakdown Bar
         Chart, 5 Vocabulary Milestones 50→1000 words with data bars, Trophy Mascot)
       - Tab 4: `📖 Hướng Dẫn` (Theme-specific study guide, Quiz & Multi-Lang tips, 6-Stage Gallery)
       - Hidden `_Calc` & `_Assets` (`B2:B7` + blank `B8` + optional GIF URL in `C9`)
  2. Mobile Portrait edition (`mobile_portrait_sheets`, strictly `<= Col G`):
       - Tab 1: `📚 Học Từ Hôm Nay` (Mascot + KPI + big `🙈 Ẩn Nghĩa` toggle + 50 thumb-friendly rows)
       - Tab 2: `🎯 Luyện Tập & Tiến Độ` (5-step Checklist + Mastery Stats + 5 Milestones + Mascot)
       - Tab 3: `📖 Hướng Dẫn` (Compact mobile guide + 2x3 6-Stage Chiikawa Gallery)
       - Hidden `_Calc` & `_Assets`

100% universal Excel + Google Sheets formulas (ZERO `#NAME?`, ZERO non-GSheets functions!).
"""
from __future__ import annotations

import datetime
from pathlib import Path

import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell

from .core import REPO_URL, qs
from .vocab_data import VocabThemeDef

VOCAB_SHEET = "📚 Kho Từ Vựng"
PRACTICE_SHEET = "🎯 Luyện Tập & Lịch Ôn"
STATS_SHEET = "📊 Thống Kê & Thành Tựu"
GUIDE_SHEET = "📖 Hướng Dẫn"
CALC_SHEET = "_Calc"
ASSETS_SHEET = "_Assets"

MOB_MAIN_SHEET = "📚 Học Từ Hôm Nay"
MOB_PRAC_SHEET = "🎯 Luyện Tập & Tiến Độ"
MOB_GUIDE_SHEET = "📖 Hướng Dẫn"

RAW_ASSETS_BASE = "https://raw.githubusercontent.com/Thitrongdan202/Habit-tracker-for-everyone-by-Dyu/main/assets"
N_ROWS = 100
R_DATA0 = 14  # 0-based row 14 -> Excel Row 15
R_DATA1 = R_DATA0 + N_ROWS - 1  # Excel Row 114


def _stage6(pct_ref: str) -> str:
    return f"=1+({pct_ref}>0)+({pct_ref}>=0.2)+({pct_ref}>=0.4)+({pct_ref}>=0.6)+({pct_ref}>=0.999)"


def _fmt(wb, font: str, size: float = 10, bold: bool = False, italic: bool = False,
         bg: str | None = None, fg: str = "#333333", align: str = "left", valign: str = "vcenter",
         wrap: bool = True, border: int = 0, border_color: str = "#E5E7EB",
         num_format: str | None = None, indent: int = 0):
    d = {
        "font_name": font, "font_size": size, "bold": bold, "italic": italic,
        "font_color": fg, "align": align, "valign": valign, "text_wrap": wrap,
    }
    if bg:
        d["bg_color"] = bg
    if border:
        d["border"] = border
        d["border_color"] = border_color
    if num_format:
        d["num_format"] = num_format
    if indent and align in ("left", "right"):
        d["indent"] = indent
    return wb.add_format(d)


def _add_assets_sheet(wb, v: VocabThemeDef, gsheets: bool, ui_font: str):
    ws = wb.add_worksheet(ASSETS_SHEET)
    ws.hide_gridlines(2)
    ws.set_column(0, 0, 26)
    ws.set_column(1, 1, 14)
    ws.set_column(2, 2, 68)
    f_hdr = _fmt(wb, ui_font, 10, True, bg=v.primary, fg=v.on_primary, align="center")
    f_lab = _fmt(wb, ui_font, 10, True, bg=v.soft, fg=v.ink, align="center")
    f_slot = _fmt(wb, ui_font, 10, bg=v.card, fg=v.ink, align="center")
    f_tip = _fmt(wb, ui_font, 9.5, bg=v.page, fg=v.muted)

    ws.set_row(0, 26)
    ws.write(0, 0, "STAGE", f_hdr)
    ws.write(0, 1, "SPRITE CACHE (B2:B7)", f_hdr)
    ws.write(0, 2, "CHIIKAWA VOCABULARY SPRITES (500x500 RGBA)", f_hdr)

    for i in range(6):
        r = 1 + i
        url = f"{RAW_ASSETS_BASE}/{v.slug}/stage_{i}.png"
        ws.set_row(r, 68)
        ws.write(r, 0, f"Stage {i} ({v.stage_names[i]})", f_lab)
        if gsheets:
            ws.write_formula(r, 1, f'=IMAGE("{url}",1)', f_slot)
        else:
            ws.write(r, 1, "", f_slot)
        ws.write(r, 2, url, f_tip)

    # Row 8 (0-based 7): strictly blank hide slot!
    ws.set_row(7, 26)
    ws.write(7, 0, "(Blank / Hide)", f_lab)
    ws.write(7, 1, "", f_slot)
    ws.write(7, 2, "GIỮ NGUYÊN Ô TRỐNG (B8)", f_tip)

    # Row 9 (0-based 8): Optional Animated GIF URL reference
    ws.set_row(8, 26)
    ws.write(8, 0, "Optional S5 GIF", f_lab)
    ws.write(8, 1, "", f_slot)
    ws.write(8, 2, f"Tùy chọn thay B7 bằng ảnh GIF động: {RAW_ASSETS_BASE}/previews/vocab/{v.num:02d}_{v.slug}_fx.gif", f_tip)
    ws.hide()
    return ws


def _mode_schema(mode: str) -> dict:
    """Return column metadata & VBA quiz indices for each distinct Vocabulary mode."""
    if mode == "srs":
        return {
            "last_col": 13,  # Col N (0-based 13)
            "cols": [
                ("STT", 5.5), ("Từ vựng (Word)", 18.0), ("Phiên âm (IPA)", 18.0),
                ("Nghĩa tiếng Việt", 25.0), ("Ví dụ áp dụng", 34.0), ("Ngày học", 11.5),
                ("L1\n+1d", 5.8), ("L2\n+3d", 5.8), ("L3\n+7d", 5.8), ("L4\n+14d", 5.8), ("L5\n+30d", 5.8),
                ("Ngày ôn tiếp", 12.5), ("Trạng thái SRS", 19.0),
            ],
            "c_word": 3, "c_pron": 4, "c_mean": 5, "c_hint": 6, "c_mast": 12, "mode_code": 1,
            "mean_letter": "E", "mast_letter": "L", "extra_letter": "N",
            "breakdown_title": "📊 PHÂN BỐ TIẾN ĐỘ 5 MỐC SRS (L1 → L5)",
            "breakdown_cats": [("L1 (+1 ngày)", "H"), ("L2 (+3 ngày)", "I"), ("L3 (+7 ngày)", "J"),
                               ("L4 (+14 ngày)", "K"), ("L5 (Thuộc 100%)", "L")],
        }
    if mode == "ielts":
        return {
            "last_col": 11,  # Col L (0-based 11)
            "cols": [
                ("STT", 5.5), ("Từ học thuật", 17.5), ("Phiên âm (IPA)", 17.5),
                ("Band / Level", 11.5), ("Chủ đề thi", 13.0), ("Nghĩa tiếng Việt", 23.0),
                ("Collocation ăn điểm", 26.0), ("Từ đồng nghĩa (Synonyms)", 24.0),
                ("Câu mẫu Writing", 32.0), ("Trạng thái", 12.0), ("Thuần thục", 9.5),
            ],
            "c_word": 3, "c_pron": 4, "c_mean": 7, "c_hint": 8, "c_mast": 12, "mode_code": 2,
            "mean_letter": "G", "mast_letter": "L", "extra_letter": "H",
            "breakdown_title": "📊 THỐNG KÊ TỪ HỌC THUẬT THEO CHỦ ĐỀ THI IELTS",
            "breakdown_cats": [("Education", "F"), ("Environment", "F"), ("Technology", "F"),
                               ("Work", "F"), ("Society", "F"), ("Health", "F")],
        }
    if mode == "flashcard":
        return {
            "last_col": 9,   # Col J (0-based 9)
            "cols": [
                ("Card", 6.0), ("Phrasal Verb / Idiom", 23.0), ("Phát âm / Stress", 19.0),
                ("Phân loại", 13.5), ("Nghĩa & Sắc thái", 27.0), ("Câu hội thoại áp dụng (Speaking)", 38.0),
                ("Độ tự tin (1–5⭐)", 14.5), ("Đã nói", 8.5), ("Trạng thái", 14.0),
            ],
            "c_word": 3, "c_pron": 4, "c_mean": 6, "c_hint": 7, "c_mast": 9, "mode_code": 3,
            "mean_letter": "F", "mast_letter": "I", "extra_letter": "G",
            "breakdown_title": "📊 MỨC ĐỘ TỰ TIN PHẢN XẠ SPEAKING (⭐ 1 → 5 SAO)",
            "breakdown_cats": [("⭐", "H"), ("⭐⭐", "H"), ("⭐⭐⭐", "H"), ("⭐⭐⭐⭐", "H"), ("⭐⭐⭐⭐⭐", "H")],
        }
    if mode == "media":
        return {
            "last_col": 10,  # Col K (0-based 10)
            "cols": [
                ("STT", 5.5), ("Từ / Cụm biểu đạt", 21.0), ("IPA / Pinyin / Furigana", 21.0),
                ("Nghĩa tiếng Việt", 26.0), ("Nguồn trích dẫn", 23.0), ("Thể loại Media", 14.0),
                ("Sắc thái", 13.5), ("Câu trích dẫn gốc (Quote)", 34.0), ("Thuộc", 8.0), ("Trạng thái", 12.5),
            ],
            "c_word": 3, "c_pron": 4, "c_mean": 5, "c_hint": 9, "c_mast": 10, "mode_code": 2,
            "mean_letter": "E", "mast_letter": "J", "extra_letter": "F",
            "breakdown_title": "📊 BỘ SƯU TẬP TỪ VỰNG THEO NGUỒN MEDIA",
            "breakdown_cats": [("Phim", "G"), ("Bài hát", "G"), ("Podcast", "G"), ("Sách/Truyện", "G")],
        }
    # mode == "exam" (#100 Shisa Matcha Bookshop)
    return {
        "last_col": 10,  # Col K (0-based 10)
        "cols": [
            ("STT", 5.5), ("Từ chính", 15.5), ("Phiên âm (IPA)", 16.5),
            ("Cặp từ dễ nhầm (Bẫy thi)", 26.0), ("Nghĩa phân biệt rõ", 25.0),
            ("Mẹo nhớ nhanh (Mnemonic)", 31.0), ("Số lần\nquên", 8.5),
            ("Cảnh báo cứu gấp", 15.5), ("Hết nhầm", 9.0), ("Ví dụ tránh bẫy thi", 30.0),
        ],
        "c_word": 3, "c_pron": 4, "c_mean": 6, "c_hint": 7, "c_mast": 10, "mode_code": 4,
        "mean_letter": "F", "mast_letter": "J", "extra_letter": "E",
        "breakdown_title": "📊 PHÂN LOẠI ĐỘ NGUY HIỂM 'NGÂN HÀNG TỪ HAY QUÊN'",
        "breakdown_cats": [("🚨 CỨU GẤP!", "I"), ("🍵 Cần ôn", "I"), ("✅ Đã xử lý", "I")],
    }


def build_vocab_desktop_workbook(v: VocabThemeDef, out_path: Path, edition: str = "pro_xlsm") -> dict:
    """Build 4-tab Desktop Chiikawa Vocabulary Tracker (pro_xlsm / offline / gsheets)."""
    universal = edition in ("pro_xlsm", "offline")
    gsheets = (edition == "gsheets")
    pro_mode = (edition == "pro_xlsm")
    ui_font = "Segoe UI" if universal else "Be Vietnam Pro"
    title_font = v.font_caps if universal else "Be Vietnam Pro"
    disp_font = v.font_display if universal else "Be Vietnam Pro"
    num_font = v.font_num if universal else "Be Vietnam Pro"
    ver_tag = "v4.3 Turbo" if pro_mode else ("v4.3 Universal" if universal else "v4.3 Cloud")

    sch = _mode_schema(v.mode)
    last_c = sch["last_col"]  # 0-based inclusive col index (cols 1..last_c)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    wb = xlsxwriter.Workbook(str(out_path))
    wb.formats[0].set_font_name(ui_font)
    wb.formats[0].set_font_size(10)

    ws_v = wb.add_worksheet(VOCAB_SHEET)
    ws_p = wb.add_worksheet(PRACTICE_SHEET)
    ws_s = wb.add_worksheet(STATS_SHEET)
    ws_g = wb.add_worksheet(GUIDE_SHEET)
    ws_c = wb.add_worksheet(CALC_SHEET)
    _add_assets_sheet(wb, v, gsheets=gsheets, ui_font=ui_font)

    vq, pq, sq, gq, cq = qs(VOCAB_SHEET), qs(PRACTICE_SHEET), qs(STATS_SHEET), qs(GUIDE_SHEET), qs(CALC_SHEET)

    # Pure-ASCII anchors for VBA (ZERO Vietnamese tab-name hardcoding!)
    wb.define_name("ANCHOR_VOCAB", f"={vq}!$B$2")
    wb.define_name("ANCHOR_PRACTICE", f"={pq}!$B$2")
    wb.define_name("ANCHOR_STATS", f"={sq}!$B$2")
    wb.define_name("ANCHOR_GUIDE", f"={gq}!$B$2")

    # =========================================================================
    #  HIDDEN `_Calc` SHEET (Universal KPIs, Rank Helpers, Lookups & VBA Config)
    # =========================================================================
    ws_c.hide_gridlines(2)
    r_s = R_DATA0 + 1  # 15
    r_e = R_DATA1 + 1  # 114
    w_rng = f"{vq}!$C${r_s}:$C${r_e}"
    m_rng = f"{vq}!${sch['mast_letter']}${r_s}:${sch['mast_letter']}${r_e}"

    ws_c.write(0, 1, "KPI")
    ws_c.write(0, 2, "Value")
    ws_c.write(1, 1, "TotalWords")
    ws_c.write_formula(1, 2, f'=COUNTIF({w_rng},"?*")')                                  # C2
    ws_c.write(2, 1, "MasteredWords")
    ws_c.write_formula(2, 2, f'=COUNTIFS({w_rng},"?*",{m_rng},TRUE)')                    # C3
    ws_c.write(3, 1, "UrgentWords")
    if v.mode == "srs":
        ws_c.write_formula(3, 2, f'=COUNTIF({vq}!$N${r_s}:$N${r_e},"🔴 Hôm nay phải ôn!")')  # C4
    elif v.mode == "ielts":
        ws_c.write_formula(3, 2, f'=COUNTIFS({w_rng},"?*",{vq}!$E${r_s}:$E${r_e},"C*")')
    elif v.mode == "flashcard":
        ws_c.write_formula(3, 2, f'=COUNTIF({vq}!$H${r_s}:$H${r_e},"⭐⭐⭐⭐⭐")')
    elif v.mode == "media":
        ws_c.write_formula(3, 2, f'=COUNTIF({vq}!$G${r_s}:$G${r_e},"Phim")+COUNTIF({vq}!$G${r_s}:$G${r_e},"Bài hát")')
    else:
        ws_c.write_formula(3, 2, f'=COUNTIF({vq}!$I${r_s}:$I${r_e},"🚨 CỨU GẤP!")')
    ws_c.write(4, 1, "MasteryPct")
    ws_c.write_formula(4, 2, "=IFERROR(MIN(1,C3/C2),0)")                                 # C5
    ws_c.write(5, 1, "HeroStageIdx")
    ws_c.write_formula(5, 2, _stage6("C5"))                                              # C6 (1..6)
    ws_c.write(6, 1, "PracticeStageIdx")
    ws_c.write_formula(6, 2, _stage6("C8"))                                              # C7 (1..6)
    ws_c.write(7, 1, "PracticePct")
    ws_c.write_formula(7, 2, f"=IFERROR(COUNTIF({pq}!$B$10:$B$14,TRUE)/5,0)")            # C8
    ws_c.write(8, 1, "LearningWords")
    ws_c.write_formula(8, 2, "=MAX(0,C2-C3)")                                            # C9
    ws_c.write(9, 1, "NewWords")
    if v.mode == "srs":
        ws_c.write_formula(9, 2, f'=COUNTIFS({w_rng},"?*",{vq}!$H${r_s}:$H${r_e},FALSE,{m_rng},FALSE)')  # C10
    elif v.mode == "ielts":
        ws_c.write_formula(9, 2, f'=COUNTIF({vq}!$K${r_s}:$K${r_e},"Mới học")')
    elif v.mode == "flashcard":
        ws_c.write_formula(9, 2, f'=COUNTIF({vq}!$J${r_s}:$J${r_e},"🌱 Mới học")')
    elif v.mode == "media":
        ws_c.write_formula(9, 2, f'=COUNTIF({vq}!$K${r_s}:$K${r_e},"Mới học")')
    else:
        ws_c.write_formula(9, 2, f'=COUNTIFS({w_rng},"?*",{vq}!$H${r_s}:$H${r_e},">=2",{m_rng},FALSE)')
    ws_c.write(10, 1, "InProgressWords")
    ws_c.write_formula(10, 2, "=MAX(0,C2-C3-C10)")                                       # C11

    # Lookup lists on Col E (4)
    for i_b, b_txt in enumerate(("B1", "B2", "C1 (7.0+)", "C2 (8.0+)")):
        ws_c.write(1 + i_b, 4, b_txt)                                                    # E2:E5
    for i_t, t_txt in enumerate(("Education", "Environment", "Technology", "Work", "Society", "Health")):
        ws_c.write(6 + i_t, 4, t_txt)                                                    # E7:E12
    for i_s, s_txt in enumerate(("Mới học", "Đang ôn", "Đã thuộc")):
        ws_c.write(13 + i_s, 4, s_txt)                                                   # E14:E16
    for i_k, k_txt in enumerate(("Phrasal Verb", "Idiom", "Speaking Filler")):
        ws_c.write(17 + i_k, 4, k_txt)                                                   # E18:E20
    for i_st, st_txt in enumerate(("⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐")):
        ws_c.write(21 + i_st, 4, st_txt)                                                 # E22:E26
    for i_m, m_txt in enumerate(("Phim", "Bài hát", "Podcast", "Sách/Truyện")):
        ws_c.write(27 + i_m, 4, m_txt)                                                   # E28:E31
    for i_n, n_txt in enumerate(("Thân mật", "Trang trọng", "Slang / GenZ", "Lãng mạn")):
        ws_c.write(32 + i_n, 4, n_txt)                                                   # E33:E36
    for i_l, l_txt in enumerate(("🇬🇧 Tiếng Anh", "🇨🇳 Tiếng Trung", "🇯🇵 Tiếng Nhật", "🇰🇷 Tiếng Hàn")):
        ws_c.write(37 + i_l, 4, l_txt)                                                   # E38:E41

    # Universal Priority-Rank Helper (`H2:I101`) — ZERO array CSE, 100% Excel + GSheets safe!
    ws_c.write(0, 7, "UrgentFlag")
    ws_c.write(0, 8, "PriorityRank")
    for idx_r in range(N_ROWS):
        xr = r_s + idx_r
        cr = 2 + idx_r  # Excel row 2..101 on _Calc
        w_c = f"{vq}!C{xr}"
        m_c = f"{vq}!{sch['mast_letter']}{xr}"
        if v.mode == "srs":
            uf = f'=IF(AND({w_c}<>"",{m_c}<>TRUE),IF({vq}!M{xr}<=TODAY(),2,1),0)'
        elif v.mode == "ielts":
            uf = f'=IF(AND({w_c}<>"",{m_c}<>TRUE),IF(OR({vq}!E{xr}="C2 (8.0+)",{vq}!E{xr}="C1 (7.0+)"),2,1),0)'
        elif v.mode == "flashcard":
            uf = f'=IF(AND({w_c}<>"",{m_c}<>TRUE),IF(OR({vq}!H{xr}="⭐",{vq}!H{xr}="⭐⭐"),2,1),0)'
        elif v.mode == "media":
            uf = f'=IF(AND({w_c}<>"",{m_c}<>TRUE),1,0)'
        else:
            uf = f'=IF(AND({w_c}<>"",{m_c}<>TRUE),IF({vq}!H{xr}>=2,2,1),0)'
        ws_c.write_formula(1 + idx_r, 7, uf)
        rk = f"=IF(H{cr}=2,COUNTIF($H$2:H{cr},2),IF(H{cr}=1,COUNTIF($H$2:$H$101,2)+COUNTIF($H$2:H{cr},1),0))"
        ws_c.write_formula(1 + idx_r, 8, rk)

    # VBA Config & Pure-Vietnamese Messages (`Z1:AA25` -> cols 25 & 26)
    vba_cfg = [
        ("CFG_FX_ENABLED", True),                      # AA1
        ("CFG_THEME_PRIMARY", v.primary),              # AA2
        ("CFG_THEME_DARK", v.primary_dark),            # AA3
        ("CFG_THEME_SOFT", v.soft),                    # AA4
        ("CFG_CHAR_NAME", v.char_name),                # AA5
        ("QUIZ_START_ROW", r_s),                       # AA6
        ("QUIZ_END_ROW", r_e),                         # AA7
        ("QUIZ_WORD_COL", sch["c_word"]),              # AA8
        ("QUIZ_PRON_COL", sch["c_pron"]),              # AA9
        ("QUIZ_MEAN_COL", sch["c_mean"]),              # AA10
        ("QUIZ_HINT_COL", sch["c_hint"]),              # AA11
        ("QUIZ_MAST_COL", sch["c_mast"]),              # AA12
        ("QUIZ_MODE_CODE", sch["mode_code"]),          # AA13
        ("MSG_PERFECT", v.toast_perfect),              # AA14
        ("MSG_PRACTICE", v.toast_practice),            # AA15
        ("QUIZ_TITLE", f"🎲 Dò Bài Flashcard • {v.char_name}"), # AA16
        ("QUIZ_ASK", "Bạn đã nhớ nghĩa của từ này chưa? Bấm OK để mở đáp án!"), # AA17
        ("QUIZ_CONFIRM", "Bạn có nhớ đúng từ này không?\n• YES = Đã nhớ (+1 bậc / Đánh dấu thuộc)\n• NO = Chưa nhớ (Cần ôn lại)"), # AA18
        ("QUIZ_OK_TOAST", f"✨ Tuyệt vời! {v.char_name} đã cập nhật tiến độ thuộc bài cho bạn!"), # AA19
        ("QUIZ_EMPTY", "ℹ️ Kho từ vựng đang trống — hãy thêm từ mới ở cột C trước nhé!"), # AA20
        ("QUIZ_RETRY_TOAST", f"🌷 Không sao đâu! {v.char_name} đã đánh dấu từ này để bạn ôn lại nhé!"), # AA21
        ("LBL_FX_ON", "✨ FX: BẬT"),                    # AA22
        ("LBL_FX_OFF", "💤 FX: TẮT"),                   # AA23
        ("MSG_FX_ON", "✨ Đã BẬT hiệu ứng Chiikawa!"),  # AA24
        ("MSG_FX_OFF", "💤 Đã TẮT hiệu ứng để siêu mượt!"), # AA25
    ]
    for ri, (k, val) in enumerate(vba_cfg):
        ws_c.write(ri, 25, k)
        if isinstance(val, bool):
            ws_c.write_boolean(ri, 26, val)
        elif isinstance(val, (int, float)):
            ws_c.write_number(ri, 26, val)
        else:
            ws_c.write(ri, 26, val)
    ws_c.hide()

    # =========================================================================
    #  TAB 1: `📚 Kho Từ Vựng`
    # =========================================================================
    ws_v.hide_gridlines(2)
    ws_v.set_tab_color(v.primary)
    ws_v.set_zoom(88)
    ws_v.set_column(0, 0, 2.2)
    for ci, (_, w_col) in enumerate(sch["cols"], start=1):
        ws_v.set_column(ci, ci, w_col)
    ws_v.set_column(last_c + 1, last_c + 1, 2.2)

    ws_v.set_row(0, 10)
    ws_v.set_row(1, 38)   # Banner
    ws_v.set_row(2, 22)   # Subtitle
    ws_v.set_row(3, 8)    # Spacer
    ws_v.set_row(4, 20)   # KPI labels
    ws_v.set_row(5, 30)   # KPI numbers
    ws_v.set_row(6, 20)   # Sub-info / Exam date / Language pill
    ws_v.set_row(7, 26)   # Sub-info value
    ws_v.set_row(8, 22)   # Motivation pill
    ws_v.set_row(9, 10)   # Spacer
    ws_v.set_row(10, 28)  # Row 11: Quiz Mode Toggle + Pro Pill Buttons Bar!
    ws_v.set_row(11, 8)   # Spacer
    ws_v.set_row(12, 10)  # Spacer
    ws_v.set_row(13, 30)  # Row 14: Table Header

    vn_ban_font = ui_font if gsheets else (
        "Cambria" if v.mode in ("srs", "ielts")
        else ("Candara" if v.mode in ("flashcard", "media") else "Palatino Linotype")
    )
    f_ban = _fmt(wb, title_font, 15.5, True, bg=v.primary, fg=v.on_primary, align="center", border=1, border_color=v.primary_dark)
    f_ban_vn = _fmt(wb, vn_ban_font, 13.5, True, bg=v.primary, fg=v.on_primary, align="center", border=1, border_color=v.primary_dark)
    f_sub = _fmt(wb, ui_font, 10, False, True, bg=v.soft, fg=v.ink, align="center", border=1, border_color=v.line)
    f_klab = _fmt(wb, ui_font, 8.5, True, bg=v.soft, fg=v.muted, align="center", border=1, border_color=v.line)
    f_kval = _fmt(wb, num_font, 16, True, bg=v.card, fg=v.primary_dark, align="center", border=1, border_color=v.line)
    f_kpct = _fmt(wb, num_font, 16, True, bg=v.card, fg=v.primary_dark, align="center", border=1, border_color=v.line, num_format="0%")
    f_kwarn = _fmt(wb, num_font, 16, True, bg=v.warn_fill, fg=v.warn_ink, align="center", border=1, border_color=v.line)
    f_pill = _fmt(wb, ui_font, 9.5, True, bg=v.soft, fg=v.primary_dark, align="center", border=1, border_color=v.primary)
    f_input = _fmt(wb, ui_font, 10.5, True, bg=v.card, fg=v.primary_dark, align="center", border=1, border_color=v.primary)
    f_date_in = _fmt(wb, num_font, 11, True, bg=v.card, fg=v.primary_dark, align="center", border=1, border_color=v.primary, num_format="dd/mm/yyyy")
    f_hero_box = _fmt(wb, ui_font, 9.5, True, bg=v.card, fg=v.primary_dark, align="center", border=1, border_color=v.primary)

    ws_v.merge_range(1, 1, 1, last_c, f"{v.emoji}  {v.title_en}  ({ver_tag})", f_ban)
    ws_v.merge_range(2, 1, 2, last_c, v.subtitle_vi, f_sub)

    # Right Hero Mascot Box spans last 2 columns (last_c-1 .. last_c), rows 4..8 (Excel rows 5..9)
    hero_c1 = last_c - 1
    hero_c2 = last_c
    kpi_end = hero_c1 - 1

    # Split KPI band `1..kpi_end` cleanly into 4 KPI cards!
    span = kpi_end
    w1 = max(2, span // 4)
    c_b1 = (1, min(kpi_end, w1))
    c_b2 = (c_b1[1] + 1, min(kpi_end, c_b1[1] + w1))
    c_b3 = (c_b2[1] + 1, min(kpi_end, c_b2[1] + w1))
    c_b4 = (c_b3[1] + 1, kpi_end)

    k3_lbl = {
        "srs": "🔴 CẦN ÔN HÔM NAY",
        "ielts": "🎓 TỪ BAND C1–C2",
        "flashcard": "⭐ TỰ TIN 5 SAO",
        "media": "🎬 TỪ PHIM & NHẠC",
        "exam": "🚨 TỪ CẦN CỨU GẤP",
    }[v.mode]

    def _mput(ws_t, r1, c1, r2, c2, val, fm):
        if r1 == r2 and c1 == c2:
            if isinstance(val, str) and val.startswith("="):
                ws_t.write_formula(r1, c1, val, fm)
            else:
                ws_t.write(r1, c1, val, fm)
        else:
            ws_t.merge_range(r1, c1, r2, c2, val, fm)

    _mput(ws_v, 4, c_b1[0], 4, c_b1[1], "📚 TỔNG SỐ TỪ", f_klab)
    _mput(ws_v, 5, c_b1[0], 5, c_b1[1], f"={cq}!$C$2", f_kval)
    _mput(ws_v, 4, c_b2[0], 4, c_b2[1], "✅ ĐÃ THUỘC 100%", f_klab)
    _mput(ws_v, 5, c_b2[0], 5, c_b2[1], f"={cq}!$C$3", f_kval)
    _mput(ws_v, 4, c_b3[0], 4, c_b3[1], k3_lbl, f_klab)
    _mput(ws_v, 5, c_b3[0], 5, c_b3[1], f"={cq}!$C$4", f_kwarn if v.mode in ("srs", "exam") else f_kval)
    _mput(ws_v, 4, c_b4[0], 4, c_b4[1], "📈 TỈ LỆ THUỘC BÀI", f_klab)
    _mput(ws_v, 5, c_b4[0], 5, c_b4[1], f"={cq}!$C$5", f_kpct)

    # Row 6..7: Theme-specific interactive feature bar!
    if v.mode == "srs":
        ws_v.merge_range(6, 1, 6, c_b2[1], "🍓 MỤC TIÊU ÔN TẬP HÔM NAY", f_klab)
        ws_v.merge_range(7, 1, 7, c_b2[1], f'="Còn "&{cq}!$C$4&" từ cần ôn hôm nay  •  Đã thuộc "&{cq}!$C$3&" / "&{cq}!$C$2&" từ"', f_input)
        ws_v.merge_range(6, c_b3[0], 6, kpi_end, "📅 NGÀY HÔM NAY (AUTO TODAY)", f_klab)
        ws_v.merge_range(7, c_b3[0], 7, kpi_end, "=TODAY()", f_date_in)
    elif v.mode == "ielts":
        ws_v.merge_range(6, 1, 6, kpi_end, "📘 THỐNG KÊ NHANH THEO CHỦ ĐỀ THI IELTS", f_klab)
        ws_v.merge_range(
            7, 1, 7, kpi_end,
            f'="Edu: "&COUNTIF($F$15:$F$114,"Education")&"  •  Env: "&COUNTIF($F$15:$F$114,"Environment")'
            f'&"  •  Tech: "&COUNTIF($F$15:$F$114,"Technology")&"  •  Work: "&COUNTIF($F$15:$F$114,"Work")'
            f'&"  •  Soc: "&COUNTIF($F$15:$F$114,"Society")&"  •  Health: "&COUNTIF($F$15:$F$114,"Health")',
            f_input,
        )
    elif v.mode == "flashcard":
        ws_v.merge_range(6, 1, 6, c_b2[1], "🗣️ PHÂN LOẠI THẺ SPEAKING", f_klab)
        ws_v.merge_range(7, 1, 7, c_b2[1], '="Idioms: "&COUNTIF($E$15:$E$114,"Idiom")&"  •  Phrasal Verbs: "&COUNTIF($E$15:$E$114,"Phrasal Verb")', f_input)
        ws_v.merge_range(6, c_b3[0], 6, kpi_end, "💡 MẸO DÒ BÀI 2 CHIỀU", f_klab)
        ws_v.merge_range(7, c_b3[0], 7, kpi_end, "Bật 🙈 Ẩn Nghĩa (B11) hoặc 🙈 Ẩn Từ (E11) ngay bên dưới!", f_input)
    elif v.mode == "media":
        ws_v.merge_range(6, 1, 6, c_b2[1], "🌐 NGÔN NGỮ ĐANG HỌC (CHỌN DROPDOWN)", f_klab)
        ws_v.merge_range(7, 1, 7, c_b2[1], "🇬🇧 Tiếng Anh", f_input)
        ws_v.data_validation(7, 1, 7, 1, {"validate": "list", "source": f"={cq}!$E$38:$E$41"})
        ws_v.merge_range(6, c_b3[0], 6, kpi_end, "🎬 BỘ SƯU TẬP MEDIA", f_klab)
        ws_v.merge_range(
            7, c_b3[0], 7, kpi_end,
            '="🎬 "&COUNTIF($G$15:$G$114,"Phim")&"  •  🎵 "&COUNTIF($G$15:$G$114,"Bài hát")'
            '&"  •  🎧 "&COUNTIF($G$15:$G$114,"Podcast")&"  •  📖 "&COUNTIF($G$15:$G$114,"Sách/Truyện")',
            f_input,
        )
    else:  # exam (#100 Shisa)
        ws_v.merge_range(6, 1, 6, c_b2[1], "📅 NGÀY THI MỤC TIÊU (NHẬP NGÀY THI CỦA BẠN)", f_klab)
        ws_v.write_datetime(7, 1, datetime.date(2026, 12, 28), f_date_in)
        if c_b2[1] > 1:
            ws_v.merge_range(7, 2, 7, c_b2[1], '="🎯 Còn "&MAX(0,B8-TODAY())&" ngày tới kỳ thi!"', f_kwarn)
        ws_v.merge_range(6, c_b3[0], 6, kpi_end, "🚨 TÌNH TRẠNG NGÂN HÀNG TỪ HAY QUÊN", f_klab)
        ws_v.merge_range(7, c_b3[0], 7, kpi_end, f'="🚨 Cần cứu gấp: "&{cq}!$C$4&" từ  •  ✅ Đã hết nhầm: "&{cq}!$C$3&" từ"', f_input)

    # Row 8: Live Motivation Banner
    ws_v.merge_range(
        8, 1, 8, kpi_end,
        f'=IF({cq}!$C$5>=0.999,"🌟 100% XUẤT SẮC! {v.char_name} cổ vũ bạn hết mình!",'
        f'IF({cq}!$C$5>=0.6,"✨ Phong độ tuyệt vời ("&TEXT({cq}!$C$5,"0%")&") — Cố thêm chút nữa đạt 100%!",'
        f'IF({cq}!$C$5>=0.2,"🌱 Đang tiến bộ đều đặn ("&TEXT({cq}!$C$5,"0%")&") cùng {v.char_name}!",'
        f'"🎀 Bắt đầu học vài từ mới ngay hôm nay nhé!")))',
        f_pill,
    )

    # Right Hero Card (`hero_c1..hero_c2`, rows 4..8)
    ws_v.merge_range(4, hero_c1, 4, hero_c2, f"{v.emoji} {v.char_name.upper()} MASCOT", f_klab)
    if gsheets:
        ws_v.merge_range(5, hero_c1, 8, hero_c2, f"=INDEX({ASSETS_SHEET}!$B$2:$B$7,{cq}!$C$6)", f_hero_box)
    else:
        ws_v.merge_range(5, hero_c1, 8, hero_c2, "", f_hero_box)

    # Row 10 (Excel Row 11): Quiz Mode Toggle(s) + Pro Quick-Action Bar!
    f_chk_tog = _fmt(wb, ui_font, 11, True, bg=v.soft, fg=v.primary_dark, align="center", border=1, border_color=v.primary)
    f_tog_lbl = _fmt(wb, ui_font, 9.5, True, bg=v.soft, fg=v.ink, align="left", indent=1, border=1, border_color=v.primary)
    ws_v.write_boolean(10, 1, False, f_chk_tog)  # B11 = 🙈 Ẩn Nghĩa
    if v.mode == "flashcard":
        ws_v.merge_range(10, 2, 10, 3, "🙈 Ẩn Nghĩa (Dò Anh → Việt)", f_tog_lbl)
        ws_v.write_boolean(10, 4, False, f_chk_tog)  # E11 = 🙈 Ẩn Từ
        ws_v.merge_range(10, 5, 10, 6, "🙈 Ẩn Từ (Dò Việt → Anh)", f_tog_lbl)
        tray_c1 = 7
    else:
        ws_v.merge_range(10, 2, 10, 4, "🙈 Chế độ Dò Bài — Tích ô B11 để Ẩn cột Nghĩa!", f_tog_lbl)
        tray_c1 = 5

    f_tray = _fmt(wb, ui_font, 9, True, bg=v.card, fg=v.muted, align="center", border=1, border_color=v.line)
    if pro_mode:
        ws_v.merge_range(10, tray_c1, 10, last_c, "", f_tray)  # Hosts VBA Pill Buttons!
    else:
        cue = ("☁️ Bản Google Sheets: Chọn ô TRUE/FALSE → Chèn → Hộp kiểm để tick siêu mượt!"
               if gsheets else "✨ Bản Excel Offline Không Macro — Dò bài mượt ngay không cần mạng!")
        ws_v.merge_range(10, tray_c1, 10, last_c, cue, f_tray)

    # Row 13 (Excel Row 14): Table Header
    f_th = _fmt(wb, ui_font, 9.5, True, bg=v.primary, fg=v.on_primary, align="center", border=1, border_color=v.primary_dark)
    for ci, (cname, _) in enumerate(sch["cols"], start=1):
        ws_v.write(13, ci, cname, f_th)

    # Table Body Formats (alternating soft pastel rows!)
    f_idx_a = _fmt(wb, num_font, 9.5, True, bg=v.card, fg=v.muted, align="center", border=1, border_color=v.line)
    f_idx_b = _fmt(wb, num_font, 9.5, True, bg=v.page, fg=v.muted, align="center", border=1, border_color=v.line)
    f_w_a = _fmt(wb, ui_font, 10.5, True, bg=v.card, fg=v.primary_dark, align="left", indent=1, border=1, border_color=v.line)
    f_w_b = _fmt(wb, ui_font, 10.5, True, bg=v.page, fg=v.primary_dark, align="left", indent=1, border=1, border_color=v.line)
    f_txt_a = _fmt(wb, ui_font, 9.5, False, bg=v.card, fg=v.ink, align="left", indent=1, border=1, border_color=v.line)
    f_txt_b = _fmt(wb, ui_font, 9.5, False, bg=v.page, fg=v.ink, align="left", indent=1, border=1, border_color=v.line)
    f_ipa_a = _fmt(wb, ui_font, 9.2, False, True, bg=v.card, fg=v.muted, align="center", border=1, border_color=v.line)
    f_ipa_b = _fmt(wb, ui_font, 9.2, False, True, bg=v.page, fg=v.muted, align="center", border=1, border_color=v.line)
    f_ctr_a = _fmt(wb, ui_font, 9.5, True, bg=v.card, fg=v.ink, align="center", border=1, border_color=v.line)
    f_ctr_b = _fmt(wb, ui_font, 9.5, True, bg=v.page, fg=v.ink, align="center", border=1, border_color=v.line)
    f_dt_a = _fmt(wb, num_font, 9.5, False, bg=v.card, fg=v.ink, align="center", border=1, border_color=v.line, num_format="dd/mm/yy")
    f_dt_b = _fmt(wb, num_font, 9.5, False, bg=v.page, fg=v.ink, align="center", border=1, border_color=v.line, num_format="dd/mm/yy")
    f_chk_a = _fmt(wb, ui_font, 10, True, bg=v.card, fg=v.primary_dark, align="center", border=1, border_color=v.line)
    f_chk_b = _fmt(wb, ui_font, 10, True, bg=v.page, fg=v.primary_dark, align="center", border=1, border_color=v.line)
    f_num_a = _fmt(wb, num_font, 10, True, bg=v.card, fg=v.ink, align="center", border=1, border_color=v.line, num_format="0")
    f_num_b = _fmt(wb, num_font, 10, True, bg=v.page, fg=v.ink, align="center", border=1, border_color=v.line, num_format="0")

    today = datetime.date(2026, 11, 28)
    row_h = 34 if v.mode == "flashcard" else 28
    checkbox_ranges_v: list[str] = ["B11"]
    if v.mode == "flashcard":
        checkbox_ranges_v.append("E11")

    for i in range(N_ROWS):
        r = R_DATA0 + i
        xr = r + 1
        ws_v.set_row(r, row_h)
        even = (i % 2 == 0)
        fi, fw, ft, fipa, fc, fdt, fck, fn = (
            (f_idx_a, f_w_a, f_txt_a, f_ipa_a, f_ctr_a, f_dt_a, f_chk_a, f_num_a)
            if even else
            (f_idx_b, f_w_b, f_txt_b, f_ipa_b, f_ctr_b, f_dt_b, f_chk_b, f_num_b)
        )
        ws_v.write_number(r, 1, i + 1, fi)
        has_s = i < len(v.samples)
        smp = v.samples[i] if has_s else None

        if v.mode == "srs":
            ws_v.write(r, 2, smp[0] if has_s else "", fw)
            ws_v.write(r, 3, smp[1] if has_s else "", fipa)
            ws_v.write(r, 4, smp[2] if has_s else "", ft)
            ws_v.write(r, 5, smp[3] if has_s else "", ft)
            if has_s:
                ws_v.write_datetime(r, 6, today - datetime.timedelta(days=smp[4]), fdt)
            else:
                ws_v.write(r, 6, "", fdt)
            for k in range(5):
                ws_v.write_boolean(r, 7 + k, bool(smp[5 + k]) if has_s else False, fck)
            ws_v.write_formula(
                r, 12,
                f'=IF(C{xr}="","",IF(L{xr}=TRUE,"Đã thuộc!",IF(K{xr}=TRUE,G{xr}+30,IF(J{xr}=TRUE,G{xr}+14,IF(I{xr}=TRUE,G{xr}+7,IF(H{xr}=TRUE,G{xr}+3,G{xr}+1))))))',
                fdt,
            )
            ws_v.write_formula(
                r, 13,
                f'=IF(C{xr}="","",IF(L{xr}=TRUE,"🌸 Đã thuộc",IF(M{xr}<=TODAY(),"🔴 Hôm nay phải ôn!","🌷 Đang ôn")))',
                fc,
            )
        elif v.mode == "ielts":
            ws_v.write(r, 2, smp[0] if has_s else "", fw)
            ws_v.write(r, 3, smp[1] if has_s else "", fipa)
            ws_v.write(r, 4, smp[2] if has_s else "", fc)
            ws_v.write(r, 5, smp[3] if has_s else "", fc)
            ws_v.write(r, 6, smp[4] if has_s else "", ft)
            ws_v.write(r, 7, smp[5] if has_s else "", ft)
            ws_v.write(r, 8, smp[6] if has_s else "", ft)
            ws_v.write(r, 9, smp[7] if has_s else "", ft)
            ws_v.write(r, 10, smp[8] if has_s else "", fc)
            ws_v.write_boolean(r, 11, bool(smp[9]) if has_s else False, fck)
        elif v.mode == "flashcard":
            ws_v.write(r, 2, smp[0] if has_s else "", fw)
            ws_v.write(r, 3, smp[1] if has_s else "", fipa)
            ws_v.write(r, 4, smp[2] if has_s else "", fc)
            ws_v.write(r, 5, smp[3] if has_s else "", ft)
            ws_v.write(r, 6, smp[4] if has_s else "", ft)
            ws_v.write(r, 7, smp[5] if has_s else "", fc)
            ws_v.write_boolean(r, 8, bool(smp[6]) if has_s else False, fck)
            ws_v.write_formula(
                r, 9,
                f'=IF(C{xr}="","",IF(OR(I{xr}=TRUE,H{xr}="⭐⭐⭐⭐⭐"),"🍯 Đã thuộc",IF(H{xr}="⭐","🌱 Mới học","🐝 Đang ôn")))',
                fc,
            )
        elif v.mode == "media":
            ws_v.write(r, 2, smp[0] if has_s else "", fw)
            ws_v.write(r, 3, smp[1] if has_s else "", fipa)
            ws_v.write(r, 4, smp[2] if has_s else "", ft)
            ws_v.write(r, 5, smp[3] if has_s else "", ft)
            ws_v.write(r, 6, smp[4] if has_s else "", fc)
            ws_v.write(r, 7, smp[5] if has_s else "", fc)
            ws_v.write(r, 8, smp[6] if has_s else "", ft)
            ws_v.write_boolean(r, 9, bool(smp[7]) if has_s else False, fck)
            ws_v.write(r, 10, smp[8] if has_s else "", fc)
        else:  # exam
            ws_v.write(r, 2, smp[0] if has_s else "", fw)
            ws_v.write(r, 3, smp[1] if has_s else "", fipa)
            ws_v.write(r, 4, smp[2] if has_s else "", ft)
            ws_v.write(r, 5, smp[3] if has_s else "", ft)
            ws_v.write(r, 6, smp[4] if has_s else "", ft)
            if has_s:
                ws_v.write_number(r, 7, int(smp[5]), fn)
            else:
                ws_v.write(r, 7, "", fn)
            ws_v.write_formula(
                r, 8,
                f'=IF(C{xr}="","",IF(J{xr}=TRUE,"✅ Đã xử lý",IF(H{xr}>=2,"🚨 CỨU GẤP!","🍵 Cần ôn")))',
                fc,
            )
            ws_v.write_boolean(r, 9, bool(smp[6]) if has_s else False, fck)
            ws_v.write(r, 10, smp[7] if has_s else "", ft)

    # Dropdowns & Checkbox Ranges on Tab 1
    if v.mode == "srs":
        checkbox_ranges_v.append(f"H{r_s}:L{r_e}")
    elif v.mode == "ielts":
        checkbox_ranges_v.append(f"L{r_s}:L{r_e}")
        ws_v.data_validation(f"E{r_s}:E{r_e}", {"validate": "list", "source": f"={cq}!$E$2:$E$5"})
        ws_v.data_validation(f"F{r_s}:F{r_e}", {"validate": "list", "source": f"={cq}!$E$7:$E$12"})
        ws_v.data_validation(f"K{r_s}:K{r_e}", {"validate": "list", "source": f"={cq}!$E$14:$E$16"})
    elif v.mode == "flashcard":
        checkbox_ranges_v.append(f"I{r_s}:I{r_e}")
        ws_v.data_validation(f"E{r_s}:E{r_e}", {"validate": "list", "source": f"={cq}!$E$18:$E$20"})
        ws_v.data_validation(f"H{r_s}:H{r_e}", {"validate": "list", "source": f"={cq}!$E$22:$E$26"})
    elif v.mode == "media":
        checkbox_ranges_v.append(f"J{r_s}:J{r_e}")
        ws_v.data_validation(f"G{r_s}:G{r_e}", {"validate": "list", "source": f"={cq}!$E$28:$E$31"})
        ws_v.data_validation(f"H{r_s}:H{r_e}", {"validate": "list", "source": f"={cq}!$E$33:$E$36"})
        ws_v.data_validation(f"K{r_s}:K{r_e}", {"validate": "list", "source": f"={cq}!$E$14:$E$16"})
    else:
        checkbox_ranges_v.append(f"J{r_s}:J{r_e}")

    # Conditional Formatting on Tab 1: Quiz Mode Masking + Urgent Highlight + Checked Pastel!
    f_mask = wb.add_format({"bg_color": v.soft, "font_color": v.soft})
    ml = sch["mean_letter"]
    ws_v.conditional_format(f"{ml}{r_s}:{ml}{r_e}", {"type": "formula", "criteria": "=$B$11=TRUE", "format": f_mask, "stop_if_true": True})
    if v.mode == "flashcard":
        ws_v.conditional_format(f"C{r_s}:D{r_e}", {"type": "formula", "criteria": "=$E$11=TRUE", "format": f_mask, "stop_if_true": True})

    f_red = wb.add_format({"bg_color": v.warn_fill, "font_color": v.warn_ink, "bold": True})
    f_ok = wb.add_format({"bg_color": "#DCFCE7", "font_color": "#166534", "bold": True})
    if v.mode == "srs":
        ws_v.conditional_format(f"N{r_s}:N{r_e}", {"type": "cell", "criteria": "==", "value": '"🔴 Hôm nay phải ôn!"', "format": f_red})
        ws_v.conditional_format(f"N{r_s}:N{r_e}", {"type": "cell", "criteria": "==", "value": '"🌸 Đã thuộc"', "format": f_ok})
        ws_v.conditional_format(f"H{r_s}:L{r_e}", {"type": "cell", "criteria": "==", "value": True, "format": wb.add_format({"bg_color": v.soft, "font_color": v.primary_dark, "bold": True})})
    elif v.mode == "exam":
        ws_v.conditional_format(f"I{r_s}:I{r_e}", {"type": "cell", "criteria": "==", "value": '"🚨 CỨU GẤP!"', "format": f_red})
        ws_v.conditional_format(f"I{r_s}:I{r_e}", {"type": "cell", "criteria": "==", "value": '"✅ Đã xử lý"', "format": f_ok})
        ws_v.conditional_format(f"J{r_s}:J{r_e}", {"type": "cell", "criteria": "==", "value": True, "format": wb.add_format({"bg_color": v.soft, "font_color": v.primary_dark, "bold": True})})
    else:
        ml_c = sch["mast_letter"]
        ws_v.conditional_format(f"{ml_c}{r_s}:{ml_c}{r_e}", {"type": "cell", "criteria": "==", "value": True, "format": wb.add_format({"bg_color": v.soft, "font_color": v.primary_dark, "bold": True})})

    # =========================================================================
    #  TAB 2: `🎯 Luyện Tập & Lịch Ôn`
    # =========================================================================
    ws_p.hide_gridlines(2)
    ws_p.set_tab_color(v.primary_dark)
    ws_p.set_zoom(92)
    p_widths = [2.2, 6.5, 22.0, 20.0, 26.0, 30.0, 2.2, 26.0, 2.2]
    for ci, cw in enumerate(p_widths):
        ws_p.set_column(ci, ci, cw)
    ws_p.set_row(0, 10)
    ws_p.set_row(1, 36)
    ws_p.set_row(2, 10)
    ws_p.set_row(3, 22)
    ws_p.set_row(4, 30)
    ws_p.set_row(5, 10)
    ws_p.set_row(6, 26)
    ws_p.set_row(7, 8)
    ws_p.set_row(8, 26)

    ws_p.merge_range(1, 1, 1, 7, f"🎯  LUYỆN TẬP HẰNG NGÀY & LỊCH ÔN GẤP  •  {v.char_name.upper()}", f_ban_vn)
    ws_p.merge_range(3, 1, 3, 2, "🎯 MỤC TIÊU TỪ MỚI / NGÀY", f_klab)
    ws_p.merge_range(4, 1, 4, 2, 10, f_kval)
    ws_p.merge_range(3, 3, 3, 4, "🔄 MỤC TIÊU TỪ ÔN / NGÀY", f_klab)
    ws_p.merge_range(4, 3, 4, 4, 15, f_kval)
    ws_p.write(3, 5, "✨ TIẾN ĐỘ 5 BƯỚC HỌC", f_klab)
    ws_p.write_formula(4, 5, f"={cq}!$C$8", f_kpct)

    # Sidebar Mascot on Tab 2 (`H4:H14`)
    ws_p.write(3, 7, f"{v.emoji} {v.char_name} CỔ VŨ!", f_klab)
    if gsheets:
        ws_p.merge_range(4, 7, 13, 7, f"=INDEX({ASSETS_SHEET}!$B$2:$B$7,{cq}!$C$7)", f_hero_box)
    else:
        ws_p.merge_range(4, 7, 13, 7, "", f_hero_box)

    # 5-Step Active Study Checklist (Rows 9..13 -> Excel Rows 10..14)
    ws_p.merge_range(8, 1, 8, 5, "🌸  CHECKLIST 5 BƯỚC HỌC TỪ CHỦ ĐỘNG HÔM NAY", f_th)
    for si, stxt in enumerate(v.practice_steps):
        rr = 9 + si
        ws_p.set_row(rr, 28)
        ws_p.write_boolean(rr, 1, si < 2, f_chk_a if si % 2 == 0 else f_chk_b)
        ws_p.merge_range(rr, 2, rr, 5, stxt, f_txt_a if si % 2 == 0 else f_txt_b)
    ws_p.conditional_format("B10:B14", {"type": "cell", "criteria": "==", "value": True, "format": wb.add_format({"bg_color": v.soft, "font_color": v.primary_dark, "bold": True})})

    # Dynamic Top-15 Urgent Review Table (Rows 17..32 -> Excel 18..33)
    ws_p.set_row(14, 12)
    ws_p.set_row(15, 28)
    ws_p.set_row(16, 26)
    urg_hdr = "🚨  NGÂN HÀNG 'TỪ HAY QUÊN' CẦN CỨU GẤP (TOP 15 TỰ ĐỘNG)" if v.mode == "exam" else "🔥  DANH SÁCH TỪ ƯU TIÊN CẦN ÔN GẤP HÔM NAY (TOP 15 TỰ ĐỘNG)"
    ws_p.merge_range(15, 1, 15, 7, urg_hdr, f_th)
    ws_p.write(16, 1, "#", f_klab)
    ws_p.write(16, 2, "Từ vựng ưu tiên", f_klab)
    ws_p.write(16, 3, "Phiên âm", f_klab)
    ws_p.write(16, 4, "Nghĩa tiếng Việt", f_klab)
    ws_p.merge_range(16, 5, 16, 7, "Gợi ý / Collocation / Mẹo nhớ / Trạng thái", f_klab)

    m_col_l = sch["mean_letter"]
    x_col_l = sch["extra_letter"]
    for k in range(1, 16):
        rr = 16 + k
        ws_p.set_row(rr, 25)
        even = (k % 2 == 0)
        ws_p.write_number(rr, 1, k, f_idx_a if even else f_idx_b)
        ws_p.write_formula(rr, 2, f'=IFERROR(INDEX({vq}!$C${r_s}:$C${r_e},MATCH({k},{cq}!$I$2:$I$101,0)),"")', f_w_a if even else f_w_b)
        ws_p.write_formula(rr, 3, f'=IFERROR(INDEX({vq}!$D${r_s}:$D${r_e},MATCH({k},{cq}!$I$2:$I$101,0)),"")', f_ipa_a if even else f_ipa_b)
        ws_p.write_formula(rr, 4, f'=IFERROR(INDEX({vq}!${m_col_l}${r_s}:${m_col_l}${r_e},MATCH({k},{cq}!$I$2:$I$101,0)),"")', f_txt_a if even else f_txt_b)
        ws_p.merge_range(rr, 5, rr, 7, f'=IFERROR(INDEX({vq}!${x_col_l}${r_s}:${x_col_l}${r_e},MATCH({k},{cq}!$I$2:$I$101,0)),"")', f_txt_a if even else f_txt_b)

    # =========================================================================
    #  TAB 3: `📊 Thống Kê & Thành Tựu`
    # =========================================================================
    ws_s.hide_gridlines(2)
    ws_s.set_tab_color(v.primary)
    ws_s.set_zoom(92)
    for ci, cw in enumerate([2.2, 24.0, 14.0, 16.0, 2.2, 24.0, 14.0, 24.0, 2.2]):
        ws_s.set_column(ci, ci, cw)
    ws_s.set_row(0, 10)
    ws_s.set_row(1, 36)
    ws_s.set_row(2, 10)
    ws_s.set_row(3, 26)

    ws_s.merge_range(1, 1, 1, 7, f"📊  THỐNG KÊ TIẾN ĐỘ & CỘT MỐC THÀNH TỰU  •  {v.char_name.upper()}", f_ban_vn)

    # Left Block: Mastery Status Table (Rows 4..7 -> Excel 5..8)
    ws_s.merge_range(3, 1, 3, 3, "📈 TRẠNG THÁI THUỘC TỪ VỰNG", f_th)
    status_rows = [
        ("🌸 Đã thuộc 100%", f"={cq}!$C$3"),
        ("🌷 Đang ôn tập",   f"={cq}!$C$11"),
        ("🌱 Mới học / Cần cứu", f"={cq}!$C$10"),
    ]
    for si, (slbl, sform) in enumerate(status_rows):
        rr = 4 + si
        ws_s.set_row(rr, 26)
        ws_s.write(rr, 1, slbl, f_txt_a if si % 2 == 0 else f_txt_b)
        ws_s.write_formula(rr, 2, sform, f_num_a if si % 2 == 0 else f_num_b)
        ws_s.write_formula(rr, 3, f"=IFERROR(C{rr + 1}/{cq}!$C$2,0)", f_kpct)

    # Native Doughnut Chart of Mastery Status (Rows 8..16, Cols B..D)
    ch_d = wb.add_chart({"type": "doughnut"})
    ch_d.add_series({
        "name": "Trạng thái từ vựng",
        "categories": f"={sq}!$B$5:$B$7",
        "values": f"={sq}!$C$5:$C$7",
        "points": [
            {"fill": {"color": v.primary}},
            {"fill": {"color": v.accent_alt}},
            {"fill": {"color": v.soft}},
        ],
        "data_labels": {"percentage": True, "font": {"name": ui_font, "size": 9, "bold": True, "color": v.ink}},
    })
    ch_d.set_title({"name": "Tỉ lệ Thuộc Bài", "name_font": {"name": ui_font, "size": 10.5, "bold": True, "color": v.ink}})
    ch_d.set_legend({"position": "bottom", "font": {"name": ui_font, "size": 9, "color": v.ink}})
    ch_d.set_chartarea({"border": {"color": v.line}, "fill": {"color": v.card}})
    ch_d.set_hole_size(58)
    ws_s.insert_chart("B9", ch_d, {"x_scale": 0.92, "y_scale": 0.88})

    # Right Block: Theme-Specific Breakdown Table (Rows 4..9, Cols F..G) + Trophy Mascot (Col H)
    ws_s.merge_range(3, 5, 3, 6, sch["breakdown_title"], f_th)
    ws_s.write(3, 7, f"🏆 {v.char_name} TROPHY", f_th)
    if gsheets:
        ws_s.merge_range(4, 7, 10, 7, f"=INDEX({ASSETS_SHEET}!$B$2:$B$7,{cq}!$C$6)", f_hero_box)
    else:
        ws_s.merge_range(4, 7, 10, 7, "", f_hero_box)

    for bi, (cat_lbl, col_l) in enumerate(sch["breakdown_cats"]):
        rr = 4 + bi
        ws_s.set_row(rr, 25)
        ws_s.write(rr, 5, cat_lbl, f_txt_a if bi % 2 == 0 else f_txt_b)
        if v.mode == "srs":
            ws_s.write_formula(rr, 6, f'=COUNTIFS({w_rng},"?*",{vq}!${col_l}${r_s}:${col_l}${r_e},TRUE)', f_num_a if bi % 2 == 0 else f_num_b)
        else:
            ws_s.write_formula(rr, 6, f'=COUNTIF({vq}!${col_l}${r_s}:${col_l}${r_e},"{cat_lbl}")', f_num_a if bi % 2 == 0 else f_num_b)

    # Bar chart for Theme Breakdown (below table)
    ch_b = wb.add_chart({"type": "column"})
    end_br = 4 + len(sch["breakdown_cats"])
    ch_b.add_series({
        "name": "Số từ",
        "categories": f"={sq}!$F$5:$F${end_br}",
        "values": f"={sq}!$G$5:$G${end_br}",
        "fill": {"color": v.primary},
        "data_labels": {"value": True, "font": {"name": ui_font, "size": 9, "bold": True, "color": v.ink}},
    })
    ch_b.set_title({"name": "Phân bố chuyên sâu", "name_font": {"name": ui_font, "size": 10.5, "bold": True, "color": v.ink}})
    ch_b.set_legend({"none": True})
    ch_b.set_chartarea({"border": {"color": v.line}, "fill": {"color": v.card}})
    ws_s.insert_chart("F12", ch_b, {"x_scale": 0.92, "y_scale": 0.78})

    # Milestones Wall: 50 → 100 → 300 → 500 → 1000 words (Rows 23..29 -> Excel 24..30)
    for rr_sp in range(10, 23):
        ws_s.set_row(rr_sp, 22)
    ws_s.set_row(23, 28)
    ws_s.set_row(24, 24)
    ws_s.merge_range(23, 1, 23, 7, "🏆  HỆ THỐNG CỘT MỐC THÀNH TỰU TỪ VỰNG (50 → 100 → 300 → 500 → 1,000 TỪ)", f_th)
    ws_s.write(24, 1, "Cột mốc danh hiệu", f_klab)
    ws_s.write(24, 2, "Mục tiêu", f_klab)
    ws_s.write(24, 3, "Đã thuộc", f_klab)
    ws_s.merge_range(24, 5, 24, 6, "Tiến độ hoàn thành", f_klab)
    ws_s.write(24, 7, "Trạng thái mở khóa", f_klab)

    milestones = [
        ("🌱 Mầm Non Từ Vựng",   50),
        ("🌸 Chiến Binh Chăm Chỉ", 100),
        ("⭐ Học Giả Kiên Trì",  300),
        ("💎 Bậc Thầy Ngoại Ngữ", 500),
        ("👑 Huyền Thoại 1000 Từ", 1000),
    ]
    for mi, (mname, mgoal) in enumerate(milestones):
        rr = 25 + mi
        xr = rr + 1
        ws_s.set_row(rr, 28)
        even = (mi % 2 == 0)
        ws_s.write(rr, 1, mname, f_w_a if even else f_w_b)
        ws_s.write_number(rr, 2, mgoal, f_num_a if even else f_num_b)
        ws_s.write_formula(rr, 3, f"={cq}!$C$3", f_num_a if even else f_num_b)
        ws_s.merge_range(rr, 5, rr, 6, f"=MIN(1,D{xr}/C{xr})", f_kpct)
        ws_s.write_formula(rr, 7, f'=IF(D{xr}>=C{xr},"🏆 ĐÃ MỞ KHÓA!","🌱 Còn "&(C{xr}-D{xr})&" từ")', f_ctr_a if even else f_ctr_b)
    ws_s.conditional_format("F26:G30", {"type": "data_bar", "bar_color": v.primary, "bar_solid": True, "min_type": "num", "min_value": 0, "max_type": "num", "max_value": 1})
    ws_s.conditional_format("H26:H30", {"type": "cell", "criteria": "==", "value": '"🏆 ĐÃ MỞ KHÓA!"', "format": f_ok})

    # =========================================================================
    #  TAB 4: `📖 Hướng Dẫn`
    # =========================================================================
    ws_g.hide_gridlines(2)
    ws_g.set_tab_color(v.primary_dark)
    ws_g.set_zoom(92)
    ws_g.set_column(0, 0, 2.5)
    for ci in range(1, 7):
        ws_g.set_column(ci, ci, 22.0)
    ws_g.set_column(7, 7, 2.5)

    ws_g.set_row(0, 10)
    ws_g.set_row(1, 40)
    ws_g.set_row(2, 24)
    ws_g.set_row(3, 24)
    ws_g.set_row(4, 10)

    ws_g.merge_range(1, 1, 1, 6, f"{v.emoji}  {v.char_name.upper()} VOCAB  —  HƯỚNG DẪN SỬ DỤNG ({ver_tag})", f_ban_vn)
    ws_g.merge_range(2, 1, 2, 6, v.subtitle_vi, f_sub)
    ed_desc = (
        f"⚡ BẢN PRO INTERACTIVE ({ver_tag.upper()} .XLSM) • Nút Dò Bài Flashcard Pop-up + Hiệu ứng Chiikawa Pastel!"
        if pro_mode else (
            f"✨ BẢN EXCEL OFFLINE KHÔNG MACRO ({ver_tag} .XLSX) • Chạy mọi Excel 2016–365 không cần Internet!"
            if universal else f"☁️ BẢN GOOGLE SHEETS ({ver_tag}) • Font Be Vietnam Pro sắc nét • Công thức chuẩn 100% không lỗi!"
        )
    )
    ws_g.merge_range(3, 1, 3, 6, ed_desc, f_pill)

    # Guide Card 1: Method-Specific Instructions
    ws_g.set_row(5, 28)
    ws_g.merge_range(5, 1, 5, 6, v.guide_method_title, f_th)
    for bi, btxt in enumerate(v.guide_method_bullets):
        ws_g.set_row(6 + bi, 38)
        ws_g.merge_range(6 + bi, 1, 6 + bi, 6, btxt, f_txt_a if bi % 2 == 0 else f_txt_b)

    # Guide Card 2: Quiz Mode & Multi-Language Usage
    ws_g.set_row(9, 10)
    ws_g.set_row(10, 28)
    ws_g.merge_range(10, 1, 10, 6, "🙈  CÁCH BẬT CHẾ ĐỘ DÒ BÀI & DÙNG ĐA NGÔN NGỮ (ANH • TRUNG • NHẬT • HÀN)", f_th)
    tips = [
        "🙈 Chế độ Dò Bài (Không cần Macro): Tích ô B11 ở tab 📚 Kho Từ Vựng để tự động Ẩn toàn bộ cột Nghĩa — tự kiểm tra trí nhớ xong bỏ tích để hiện lại đáp án ngay lập tức!",
        "🌐 Dùng cho mọi ngoại ngữ: Cột Phiên âm dùng linh hoạt cho IPA (Tiếng Anh), Pinyin (Tiếng Trung), Furigana (Tiếng Nhật) hoặc Romaji (Tiếng Hàn).",
        "🎲 Đặc quyền Bản Pro (.xlsm): Bấm nút 'Dò Bài Ngẫu Nhiên' trên tab 📚 Kho Từ Vựng để mở Flashcard Pop-up tự chấm điểm & cộng tiến độ trực tiếp vào bảng!",
    ]
    for ti, ttxt in enumerate(tips):
        ws_g.set_row(11 + ti, 36)
        ws_g.merge_range(11 + ti, 1, 11 + ti, 6, ttxt, f_txt_a if ti % 2 == 0 else f_txt_b)

    # Section 5: 6-Stage Chiikawa Gallery (Row 16 header, Row 17 sprites, Row 18 labels)
    ws_g.set_row(14, 10)
    ws_g.set_row(15, 28)
    ws_g.set_row(16, 94)
    ws_g.set_row(17, 26)
    ws_g.merge_range(15, 1, 15, 6, f"5. HOẠT ẢNH TIẾN HÓA 6 GIAI ĐOẠN CỦA {v.char_name.upper()} (0% → 100%)", f_th)
    pct_lbls = ("0%", "20%", "40%", "60%", "80%", "100% MAX")
    for k in range(6):
        if gsheets:
            ws_g.write_formula(16, 1 + k, f"=INDEX({ASSETS_SHEET}!$B$2:$B$7,{k + 1})", f_hero_box)
        else:
            ws_g.write(16, 1 + k, "", f_hero_box)
        ws_g.write(17, 1 + k, f"{v.stage_names[k]}\n({pct_lbls[k]})", f_klab)

    # Copyright Footer
    ws_g.set_row(18, 10)
    ws_g.set_row(19, 26)
    ws_g.merge_range(19, 1, 19, 6, f"© 2026 Dyu (Thân Trọng Duy)  •  Chiikawa Vocabulary Tracker {ver_tag}  •  Mốc 100 Template", f_sub)

    wb.close()
    return {
        "edition": edition,
        "num": v.num,
        "stem": v.stem,
        "slug": v.slug,
        "char_name": v.char_name,
        "theme_primary": v.primary,
        "theme_primary_dark": v.primary_dark,
        "theme_soft": v.soft,
        "theme_ink": v.ink,
        "theme_on_primary": v.on_primary,
        "last_col": last_c,
        "hero_c1": hero_c1,
        "hero_c2": hero_c2,
        "tray_c1": tray_c1,
        "checkbox_ranges_vocab": checkbox_ranges_v,
        "checkbox_ranges_practice": ["B10:B14"],
        "base_path": str(out_path),
    }


def build_vocab_mobile_workbook(v: VocabThemeDef, out_path: Path) -> dict:
    """Build strictly Portrait `<= Col G` Mobile Vocabulary Tracker (`templates/mobile_portrait_sheets/`)."""
    ui_font = "Be Vietnam Pro"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    wb = xlsxwriter.Workbook(str(out_path))
    wb.formats[0].set_font_name(ui_font)
    wb.formats[0].set_font_size(10)

    ws_m = wb.add_worksheet(MOB_MAIN_SHEET)
    ws_p = wb.add_worksheet(MOB_PRAC_SHEET)
    ws_g = wb.add_worksheet(MOB_GUIDE_SHEET)
    ws_c = wb.add_worksheet(CALC_SHEET)
    _add_assets_sheet(wb, v, gsheets=True, ui_font=ui_font)

    mq, pq, cq = qs(MOB_MAIN_SHEET), qs(MOB_PRAC_SHEET), qs(CALC_SHEET)
    N_MOB = 50
    R0, R1 = 15, 15 + N_MOB - 1  # Excel rows 15..64

    # Hidden `_Calc`
    ws_c.hide_gridlines(2)
    ws_c.write(1, 2, f'=COUNTIF({mq}!$C${R0}:$C${R1},"?*")')                        # C2 Total
    ws_c.write_formula(2, 2, f'=COUNTIFS({mq}!$C${R0}:$C${R1},"?*",{mq}!$B${R0}:$B${R1},TRUE)')  # C3 Mastered
    ws_c.write_formula(4, 2, "=IFERROR(MIN(1,C3/C2),0)")                            # C5 Pct
    ws_c.write_formula(5, 2, _stage6("C5"))                                         # C6 HeroStage
    ws_c.write_formula(6, 2, _stage6("C8"))                                         # C7 PracticeStage
    ws_c.write_formula(7, 2, f"=IFERROR(COUNTIF({pq}!$B$6:$B$10,TRUE)/5,0)")        # C8 PracticePct
    ws_c.hide()

    f_ban = _fmt(wb, ui_font, 14, True, bg=v.primary, fg=v.on_primary, align="center", border=1, border_color=v.primary_dark)
    f_sub = _fmt(wb, ui_font, 9.5, False, True, bg=v.soft, fg=v.ink, align="center", border=1, border_color=v.line)
    f_klab = _fmt(wb, ui_font, 9, True, bg=v.soft, fg=v.muted, align="center", border=1, border_color=v.line)
    f_kval = _fmt(wb, ui_font, 18, True, bg=v.card, fg=v.primary_dark, align="center", border=1, border_color=v.line)
    f_kpct = _fmt(wb, ui_font, 20, True, bg=v.card, fg=v.primary_dark, align="center", border=1, border_color=v.line, num_format="0%")
    f_hero = _fmt(wb, ui_font, 9, True, bg=v.card, fg=v.primary_dark, align="center", border=1, border_color=v.primary)
    f_th = _fmt(wb, ui_font, 9.5, True, bg=v.primary, fg=v.on_primary, align="center", border=1, border_color=v.primary_dark)
    f_chk_a = _fmt(wb, ui_font, 11, True, bg=v.card, fg=v.primary_dark, align="center", border=1, border_color=v.line)
    f_chk_b = _fmt(wb, ui_font, 11, True, bg=v.page, fg=v.primary_dark, align="center", border=1, border_color=v.line)
    f_w_a = _fmt(wb, ui_font, 10.5, True, bg=v.card, fg=v.primary_dark, align="left", indent=1, border=1, border_color=v.line)
    f_w_b = _fmt(wb, ui_font, 10.5, True, bg=v.page, fg=v.primary_dark, align="left", indent=1, border=1, border_color=v.line)
    f_txt_a = _fmt(wb, ui_font, 9.8, False, bg=v.card, fg=v.ink, align="left", indent=1, border=1, border_color=v.line)
    f_txt_b = _fmt(wb, ui_font, 9.8, False, bg=v.page, fg=v.ink, align="left", indent=1, border=1, border_color=v.line)
    f_tag_a = _fmt(wb, ui_font, 9, True, bg=v.card, fg=v.muted, align="center", border=1, border_color=v.line)
    f_tag_b = _fmt(wb, ui_font, 9, True, bg=v.page, fg=v.muted, align="center", border=1, border_color=v.line)
    f_tog = _fmt(wb, ui_font, 11, True, bg=v.soft, fg=v.primary_dark, align="center", border=1, border_color=v.primary)

    # ---- TAB 1: `📚 Học Từ Hôm Nay` (Cols B..G -> max_col = 7!) ----
    ws_m.hide_gridlines(2)
    ws_m.set_tab_color(v.primary)
    ws_m.set_portrait()
    ws_m.fit_to_pages(1, 0)
    for ci, cw in enumerate([1.5, 6.2, 16.5, 13.5, 16.0, 12.5, 11.5]):  # A..G (7 cols total!)
        ws_m.set_column(ci, ci, cw)
    ws_m.set_row(0, 8)
    ws_m.set_row(1, 34)
    ws_m.set_row(2, 24)
    ws_m.set_row(3, 8)
    for rr in range(4, 9):
        ws_m.set_row(rr, 26)
    ws_m.set_row(9, 8)
    ws_m.set_row(10, 34)  # Row 11: Big thumb-friendly Quiz Mode switch!
    ws_m.set_row(11, 8)
    ws_m.set_row(12, 8)
    ws_m.set_row(13, 28)

    ws_m.merge_range(1, 1, 1, 6, f"{v.emoji}  {v.char_name.upper()} VOCAB • MOBILE", f_ban)
    ws_m.merge_range(2, 1, 2, 6, v.subtitle_vi, f_sub)
    ws_m.merge_range(4, 1, 4, 3, "📈 TIẾN ĐỘ THUỘC BÀI", f_klab)
    ws_m.merge_range(5, 1, 6, 3, f"={cq}!$C$5", f_kpct)
    ws_m.merge_range(7, 1, 8, 3, f'="✅ Đã thuộc: "&{cq}!$C$3&" / "&{cq}!$C$2&" từ"', f_sub)
    ws_m.merge_range(4, 4, 8, 6, f"=INDEX({ASSETS_SHEET}!$B$2:$B$7,{cq}!$C$6)", f_hero)

    # Row 11: Big Quiz Switch
    ws_m.write_boolean(10, 1, False, f_tog)  # B11 = 🙈 Ẩn Nghĩa
    if v.mode == "flashcard":
        ws_m.merge_range(10, 2, 10, 3, "🙈 Ẩn Nghĩa", f_sub)
        ws_m.write_boolean(10, 4, False, f_tog)  # E11 = 🙈 Ẩn Từ
        ws_m.merge_range(10, 5, 10, 6, "🙈 Ẩn Từ", f_sub)
    else:
        ws_m.merge_range(10, 2, 10, 6, "🙈 Tích B11 để ẨN NGHĨA dò bài nhanh 1 tay!", f_sub)

    ws_m.write(13, 1, "✓", f_th)
    ws_m.write(13, 2, "Từ vựng", f_th)
    ws_m.write(13, 3, "Phiên âm", f_th)
    ws_m.merge_range(13, 4, 13, 5, "Nghĩa tiếng Việt", f_th)
    ws_m.write(13, 6, "Ghi chú", f_th)

    for i in range(N_MOB):
        r = 14 + i
        ws_m.set_row(r, 36)  # Generous 36pt thumb-friendly tap row!
        even = (i % 2 == 0)
        has_s = i < len(v.samples)
        smp = v.samples[i] if has_s else None
        if has_s:
            if v.mode == "srs":
                done, w, ipa, mean, tag = bool(smp[9]), smp[0], smp[1], smp[2], ("L5 🌸" if smp[9] else "SRS")
            elif v.mode == "ielts":
                done, w, ipa, mean, tag = bool(smp[9]), smp[0], smp[1], smp[4], smp[2]
            elif v.mode == "flashcard":
                done, w, ipa, mean, tag = bool(smp[6]), smp[0], smp[1], smp[3], smp[5]
            elif v.mode == "media":
                done, w, ipa, mean, tag = bool(smp[7]), smp[0], smp[1], smp[2], smp[4]
            else:
                done, w, ipa, mean, tag = bool(smp[6]), smp[0], smp[1], smp[3], (f"Quên {smp[5]}x" if smp[5] >= 2 else "OK")
        else:
            done, w, ipa, mean, tag = False, "", "", "", ""
        ws_m.write_boolean(r, 1, done, f_chk_a if even else f_chk_b)
        ws_m.write(r, 2, w, f_w_a if even else f_w_b)
        ws_m.write(r, 3, ipa, f_tag_a if even else f_tag_b)
        ws_m.merge_range(r, 4, r, 5, mean, f_txt_a if even else f_txt_b)
        ws_m.write(r, 6, tag, f_tag_a if even else f_tag_b)

    f_mask = wb.add_format({"bg_color": v.soft, "font_color": v.soft})
    ws_m.conditional_format(f"E{R0}:F{R1}", {"type": "formula", "criteria": "=$B$11=TRUE", "format": f_mask, "stop_if_true": True})
    if v.mode == "flashcard":
        ws_m.conditional_format(f"C{R0}:D{R1}", {"type": "formula", "criteria": "=$E$11=TRUE", "format": f_mask, "stop_if_true": True})
    ws_m.conditional_format(f"B{R0}:B{R1}", {"type": "cell", "criteria": "==", "value": True, "format": wb.add_format({"bg_color": v.soft, "font_color": v.primary_dark, "bold": True})})

    # ---- TAB 2: `🎯 Luyện Tập & Tiến Độ` (Cols B..G) ----
    ws_p.hide_gridlines(2)
    ws_p.set_tab_color(v.primary_dark)
    ws_p.set_portrait()
    ws_p.fit_to_pages(1, 0)
    for ci, cw in enumerate([1.5, 6.2, 16.5, 13.5, 16.0, 12.5, 11.5]):
        ws_p.set_column(ci, ci, cw)
    ws_p.set_row(0, 8)
    ws_p.set_row(1, 34)
    ws_p.set_row(2, 8)
    ws_p.set_row(3, 26)
    ws_p.set_row(4, 26)
    ws_p.merge_range(1, 1, 1, 6, f"🎯  LUYỆN TẬP 5 BƯỚC & THÀNH TỰU", f_ban)
    ws_p.merge_range(3, 1, 3, 6, "🌸 CHECKLIST HỌC CHỦ ĐỘNG HÔM NAY", f_th)
    ws_p.merge_range(4, 1, 4, 6, f'="Tiến độ hôm nay: "&TEXT({cq}!$C$8,"0%")', f_sub)
    for si, stxt in enumerate(v.practice_steps):
        rr = 5 + si
        ws_p.set_row(rr, 36)
        ws_p.write_boolean(rr, 1, si < 2, f_chk_a if si % 2 == 0 else f_chk_b)
        ws_p.merge_range(rr, 2, rr, 6, stxt, f_txt_a if si % 2 == 0 else f_txt_b)
    ws_p.conditional_format("B6:B10", {"type": "cell", "criteria": "==", "value": True, "format": wb.add_format({"bg_color": v.soft, "font_color": v.primary_dark, "bold": True})})

    ws_p.set_row(11, 28)
    ws_p.merge_range(11, 1, 11, 6, f"{v.emoji} {v.char_name.upper()} CỔ VŨ & CỘT MỐC", f_th)
    for rr in range(12, 17):
        ws_p.set_row(rr, 28)
    ws_p.merge_range(12, 1, 16, 3, f"=INDEX({ASSETS_SHEET}!$B$2:$B$7,{cq}!$C$7)", f_hero)
    for mi, (mn, mg) in enumerate((("🌱 50 từ", 50), ("🌸 100 từ", 100), ("⭐ 300 từ", 300), ("💎 500 từ", 500), ("👑 1000 từ", 1000))):
        ws_p.write(12 + mi, 4, mn, f_w_a if mi % 2 == 0 else f_w_b)
        ws_p.merge_range(12 + mi, 5, 12 + mi, 6, f'=IF({cq}!$C$3>={mg},"🏆 XONG!",{cq}!$C$3&" / {mg}")', f_tag_a if mi % 2 == 0 else f_tag_b)

    # ---- TAB 3: `📖 Hướng Dẫn` (Cols B..G) ----
    ws_g.hide_gridlines(2)
    ws_g.set_tab_color(v.primary)
    ws_g.set_portrait()
    ws_g.fit_to_pages(1, 0)
    for ci, cw in enumerate([1.5, 13.0, 13.0, 13.0, 13.0, 13.0, 13.0]):
        ws_g.set_column(ci, ci, cw)
    ws_g.set_row(0, 8)
    ws_g.set_row(1, 34)
    ws_g.set_row(2, 26)
    ws_g.merge_range(1, 1, 1, 6, f"{v.emoji}  HƯỚNG DẪN MOBILE • {v.char_name.upper()}", f_ban)
    ws_g.merge_range(2, 1, 2, 6, v.subtitle_vi, f_sub)
    for bi, btxt in enumerate(v.guide_method_bullets):
        ws_g.set_row(4 + bi, 44)
        ws_g.merge_range(4 + bi, 1, 4 + bi, 6, btxt, f_txt_a if bi % 2 == 0 else f_txt_b)
    ws_g.set_row(8, 26)
    ws_g.merge_range(8, 1, 8, 6, f"🌟 6 GIAI ĐOẠN {v.char_name.upper()} (0% → 100%)", f_th)
    for r_row in range(2):
        r_im = 9 + r_row * 2
        r_lb = r_im + 1
        ws_g.set_row(r_im, 74)
        ws_g.set_row(r_lb, 24)
        for c_blk in range(3):
            k = r_row * 3 + c_blk
            c1 = 1 + c_blk * 2
            ws_g.merge_range(r_im, c1, r_im, c1 + 1, f"=INDEX({ASSETS_SHEET}!$B$2:$B$7,{k + 1})", f_hero)
            ws_g.merge_range(r_lb, c1, r_lb, c1 + 1, v.stage_names[k], f_klab)
    ws_g.set_row(14, 24)
    ws_g.merge_range(14, 1, 14, 6, "© 2026 Dyu (Thân Trọng Duy) • Chiikawa Vocab Mobile v4.3", f_sub)

    wb.close()
    return {
        "num": v.num,
        "stem": v.stem,
        "slug": v.slug,
        "out_path": str(out_path),
        "mob_chk_ranges": [f"B{R0}:B{R1}", "B11"] + (["E11"] if v.mode == "flashcard" else []),
        "mob_prac_ranges": ["B6:B10"],
    }
