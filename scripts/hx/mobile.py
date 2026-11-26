"""
hx.mobile — Mobile Portrait Habit Tracker Engine (4th Edition: `templates/mobile_portrait_sheets/`).

Engineered strictly for smartphone portrait screens (iOS & Android, zero horizontal scroll):
  - Max visible column: Col `I` (8-column portrait stack `B:I` with thin gutters `A` & `J`)
  - 3 clean mobile tabs (Daily Tracker FIRST so opening the file lands straight on check-in!):
      1. `📱 Tuần Này`            (Vertical 7-card stack: Header/Selectors, Weekly Hero, 7-Day Garden,
                                   15 thumb-friendly 38pt habit rows, Per-Habit Progress Bars,
                                   Compact Portrait Chart, Quick Reflection Notes)
      2. `🎯 Mục Tiêu & Thành Tựu` (Vertical Year Selector + Live Yearly Hero + 12 thumb-friendly Goals
                                   + 2x2 Annual KPI Grid + 6 Core Achievements Wall)
      3. `📖 Hướng Dẫn`           (Single-column mobile-readable guide + 2x3 Stage 0..5 showcase + thresholds)
  - 2 hidden sheets: `_Calc` (non-overlapping lookups, calendar, KPIs, stage indices) & `_Database`
    (keyed by `YYYY-MM-W#` for weeks & `YYYY` for Yearly Goals, compatible with `google_sheets_1click_setup.gs`!)
  - All `=IMAGE(...)` URLs point to `main/assets/<slug>/stage_X.png` and react dynamically 0%..100%.
  - Strict `Segoe UI` typography, Bold/Regular hierarchy, `indent=1` padding, zero clipping.
"""
from __future__ import annotations

import calendar
import datetime
import random
from dataclasses import replace
from pathlib import Path

import xlsxwriter

from .core import (Canvas, Styles, Theme, MONTHS_EN, CHECK_ALT, acell, cell, colname,
                   qs, rng, place_chart, axis_font, text_lines, checked_pastel_bg, REPO_URL)
from .tracker import Habit
from .daily_tasks import (DEFAULT_DAILY_TASKS, DEFAULT_DAILY_HIGHLIGHT, DEFAULT_TASK_DAY,
                          DEFAULT_TASK_MONTH, DEFAULT_TASK_YEAR, DEFAULT_TASK_KEY, TASK_PRIORITIES)

MOBILE_WEEK_SHEET = "📱 Tuần Này"
MOBILE_TASKS_SHEET = "📝 Việc Hôm Nay"
MOBILE_GOALS_SHEET = "🎯 Mục Tiêu & Thành Tựu"
MOBILE_GUIDE_SHEET = "📖 Hướng Dẫn"
MOBILE_CALC_SHEET = "_Calc"
MOBILE_DB_SHEET = "_Database"
MOBILE_ASSETS_SHEET = "_Assets"

WEEKS_VI = ["Tuần 1", "Tuần 2", "Tuần 3", "Tuần 4", "Tuần 5"]
DAYS_VI = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]

N_MOB_HABITS = 15   # 8 realistic Vietnamese sample habits + 7 blank expansion rows
N_MOB_GOALS = 12    # 8 realistic Vietnamese sample goals + 4 blank expansion rows

MOBILE_GOALS_SAMPLE = [
    (True,  "Duy trì tập thể dục tối thiểu 4 buổi / tuần"),
    (True,  "Đọc trọn vẹn 12 cuốn sách hay trong năm"),
    (True,  "Uống đủ 2L nước & ăn lành mạnh mỗi ngày"),
    (True,  "Ngủ trước 23h00 & đủ 7.5 – 8 tiếng mỗi đêm"),
    (False, "Tiết kiệm đều đặn ít nhất 20% thu nhập tháng"),
    (False, "Học ngoại ngữ / kỹ năng mới 30 phút mỗi ngày"),
    (False, "Viết nhật ký biết ơn & giảm thời gian lướt mạng"),
    (False, "Duy trì không gian sống tối giản & gọn gàng"),
]


def _stage6(pct_ref: str, num_stages: int = 6) -> str:
    if num_stages == 8:
        return (f"=1+({pct_ref}>0)+({pct_ref}>=CFG_THR_M1)+({pct_ref}>=CFG_THR_0)"
                f"+({pct_ref}>=CFG_THR_1)+({pct_ref}>=CFG_THR_2)+({pct_ref}>=CFG_THR_3)+({pct_ref}>=0.999)")
    if num_stages == 7:
        return (f"=1+({pct_ref}>0)+({pct_ref}>=CFG_THR_0)+({pct_ref}>=CFG_THR_1)"
                f"+({pct_ref}>=CFG_THR_2)+({pct_ref}>=CFG_THR_3)+({pct_ref}>=0.999)")
    return (f"=1+({pct_ref}>0)+({pct_ref}>=CFG_THR_1)+({pct_ref}>=CFG_THR_2)"
            f"+({pct_ref}>=CFG_THR_3)+({pct_ref}>=0.999)")


def _img_formula(stage_ref: str, blank_guard: str | None = None, assets_range: str = "$B$2:$B$8") -> str:
    """Zero-lag cached sprite lookup referencing hidden `_Assets` (only 6-8 unique =IMAGE() calls!)."""
    core = f"INDEX(_Assets!{assets_range},{stage_ref})"
    if blank_guard:
        return f'=IF({blank_guard}="","",{core})'
    return f"={core}"


def _add_mobile_assets_sheet(wb, styles: Styles):
    """Hidden `_Assets` sprite cache for Mobile Portrait Google Sheets:
    holds ONLY the 6-8 unique `=IMAGE("https://.../stage_X.png", 1)` formulas in B2:B(1+N)
    plus an empty hide slot at B(2+N) so all mobile sprites render instantly via `=INDEX(_Assets!...)`."""
    t = styles.t
    ws = wb.add_worksheet(MOBILE_ASSETS_SHEET)
    ws.hide_gridlines(2)
    ws.set_column(0, 0, 26)
    ws.set_column(1, 1, 14)
    ws.set_column(2, 2, 62)
    hdr = wb.add_format({"font_name": t.font, "font_size": 10, "bold": True,
                         "bg_color": t.primary, "font_color": t.on_primary,
                         "align": "center", "valign": "vcenter"})
    lab = wb.add_format({"font_name": t.font, "font_size": 10, "bold": True,
                         "bg_color": t.soft, "font_color": t.ink,
                         "align": "center", "valign": "vcenter"})
    slot = wb.add_format({"font_name": t.font, "font_size": 10, "bg_color": t.card,
                          "align": "center", "valign": "vcenter"})
    tip = wb.add_format({"font_name": t.font, "font_size": 10, "font_color": t.muted,
                         "bg_color": t.page, "valign": "vcenter", "text_wrap": True})

    ws.set_row(0, 26)
    ws.write(0, 0, "STAGE", hdr)
    ws.write(0, 1, f"SPRITE CACHE (B2:B{1 + t.num_stages})", hdr)
    ws.write(0, 2, "MOBILE GOOGLE SHEETS IMAGE CACHE (6-8 URLs -> INDEX LOOKUP)", hdr)

    names = t.stage_names or [f"Stage {i}" for i in range(t.num_stages)]
    for i in range(t.num_stages):
        r = 1 + i
        url = f"{t.img_base}stage_{i}.png"
        ws.set_row(r, 68)
        ws.write(r, 0, f"Stage {i} ({names[i]})", lab)
        ws.write_formula(r, 1, f'=IMAGE("{url}",1)', slot)
        ws.write(r, 2, url, tip)

    r_blank = 1 + t.num_stages
    ws.set_row(r_blank, 28)
    ws.write(r_blank, 0, "(Blank / Hide Day)", lab)
    ws.write(r_blank, 1, "", slot)
    ws.write(r_blank, 2, "GIỮ NGUYÊN Ô TRỐNG — dùng để ẩn ngày ngoài tháng", tip)

    ws.hide()
    return ws


def _sample_week_ticks(habits: list[Habit], year: int, month: int, week_num: int, seed: int) -> list[list[bool]]:
    """Generate realistic demo ticks ONLY for active calendar days of `(year, month, week_num)`
    so out-of-month days are False and active days showcase rich stages 1..5 (~72% weekly)."""
    first = datetime.date(year, month, 1)
    first_wd = first.weekday()  # 0=Mon .. 6=Sun
    mon_w1 = first - datetime.timedelta(days=first_wd)
    active_cols = []
    for dow in range(7):
        dt = mon_w1 + datetime.timedelta(days=(week_num - 1) * 7 + dow)
        if dt.month == month:
            active_cols.append(dow)

    n = min(8, len(habits))
    rnd = random.Random(seed + 77)
    # Varied target completion ratios across active days so sprites visibly show multiple stages!
    wave = [1.00, 0.75, 0.50, 0.88, 1.00, 0.38, 0.88]
    grid = [[False] * 7 for _ in range(N_MOB_HABITS)]
    for idx_a, dow in enumerate(active_cols):
        ratio = wave[idx_a % len(wave)]
        k = n if ratio >= 0.99 else max(1, min(n - 1, int(round(ratio * n))))
        order = sorted(range(n), key=lambda i: habits[i].p + rnd.uniform(-0.20, 0.20), reverse=True)
        for hi in order[:k]:
            grid[hi][dow] = True
    return grid


def _compute_week_summary(habits: list[Habit], ticks_15: list[list[bool]], year: int, month: int, week_num: int) -> dict:
    first = datetime.date(year, month, 1)
    mon_w1 = first - datetime.timedelta(days=first.weekday())
    active_cols = [dow for dow in range(7)
                   if (mon_w1 + datetime.timedelta(days=(week_num - 1) * 7 + dow)).month == month]
    n_active = min(8, len(habits))
    completed = 0
    best_streak = 0
    for hi in range(n_active):
        run = 0
        for dow in active_cols:
            if ticks_15[hi][dow]:
                completed += 1
                run += 1
                best_streak = max(best_streak, run)
            else:
                run = 0
    target = n_active * len(active_cols)
    grown = 0
    perfect = 0
    if n_active > 0:
        for dow in active_cols:
            d_cnt = sum(1 for hi in range(n_active) if ticks_15[hi][dow])
            pct = d_cnt / n_active
            if pct >= 0.75 - 1e-6:
                grown += 1
            if pct >= 0.999:
                perfect += 1
    return {
        "key": f"{year:04d}-{month:02d}-W{week_num}",
        "year": year, "month": month, "week": week_num,
        "completed": completed, "target": target,
        "grown": grown, "perfect": perfect, "best_streak": best_streak,
    }


def _finish_mobile_sheet(ws, cv: Canvas, tab_color: str, zoom: int = 100):
    ws.hide_gridlines(2)
    ws.set_zoom(zoom)
    ws.set_tab_color(tab_color)
    ws.set_portrait()
    ws.set_paper(9)
    ws.fit_to_pages(1, 0)
    ws.set_margins(0.2, 0.2, 0.25, 0.25)
    cv.flush()


def build_mobile_workbook(tdef, out_path: Path) -> dict:
    """
    Build one complete Mobile Portrait `.xlsx` workbook for `tdef` (TemplateDef from excel_builder.py).
    Strictly fits within columns `B:I` on all 4 visible tabs, optimized for Google Sheets Mobile:
      - Unified `Be Vietnam Pro` typography (min 10pt body/labels/checkboxes, 11-16pt bold headers)
      - Hidden `_Assets` image cache (6-8 unique `=IMAGE(...,1)`) + instant `=INDEX(_Assets!...)`
      - Fast native `cellIs == TRUE` conditional formatting on checkbox grids
    """
    t: Theme = replace(
        tdef.theme,
        font="Be Vietnam Pro",
        font_title="Be Vietnam Pro",
        font_month="Be Vietnam Pro",
    )
    habits: list[Habit] = list(tdef.habits[:8])
    year, month_idx, week_num = 2026, 10, 1
    month_name = MONTHS_EN[month_idx - 1]
    week_label = WEEKS_VI[week_num - 1]
    week_key = f"{year:04d}-{month_idx:02d}-W{week_num}"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    wb = xlsxwriter.Workbook(str(out_path))
    wb.formats[0].set_font_name("Be Vietnam Pro")
    wb.formats[0].set_font_size(10)
    styles = Styles(wb, t, gsheets=True)

    # Create tabs in MOBILE-FIRST ORDER: 1. Week -> 2. Daily Tasks -> 3. Goals & Achievements -> 4. Guide -> hidden helpers
    ws_wk = wb.add_worksheet(MOBILE_WEEK_SHEET)
    ws_dt = wb.add_worksheet(MOBILE_TASKS_SHEET)
    ws_go = wb.add_worksheet(MOBILE_GOALS_SHEET)
    ws_gd = wb.add_worksheet(MOBILE_GUIDE_SHEET)
    ws_calc = wb.add_worksheet(MOBILE_CALC_SHEET)
    ws_db = wb.add_worksheet(MOBILE_DB_SHEET)

    wq = qs(MOBILE_WEEK_SHEET)
    tq = qs(MOBILE_TASKS_SHEET)
    gq = qs(MOBILE_GOALS_SHEET)
    dq = qs(MOBILE_GUIDE_SHEET)
    cq = qs(MOBILE_CALC_SHEET)
    dbq = qs(MOBILE_DB_SHEET)

    # =========================================================================
    #  HIDDEN `_Calc` SHEET (Non-overlapping lookups, calendar, KPIs & stages!)
    # =========================================================================
    # Col A (0): Months A1:A12
    # Col B (1): Years B1:B17 (2024..2040)
    # Col C (2): Weeks C1:C5 ("Tuần 1".."Tuần 5")
    # Col D (3): Labels | Col E (4): Weekly KPIs & State (E1..E25)
    #   E1: MonthNum (1..12)
    #   E2: Year (2024..2040)
    #   E3: WeekNum (1..5)
    #   E4: ActiveHabitCount
    #   E5: ActiveDaysInWeek
    #   E6: WeeklyDone
    #   E7: WeeklyTarget
    #   E8: WeeklyPct
    #   E9: WeeklyBestStreak
    #   E10: WeeklyPerfectDays
    #   E11: WeeklyGrownDays
    #   E12: WeeklyHeroStageIdx (1..6)
    #   E13: ActiveWeekKey ("2026-10-W1")
    #   E14: LastLoadedWeekKey ("2026-10-W1" — Google Sheets onEdit state!)
    #   E15: LastGoalYear (2026 — Google Sheets onEdit state!)
    #   E16: GoalsDone (live)
    #   E17: GoalsTotal (live)
    #   E18: GoalsPct (live)
    #   E19: GoalsHeroStageIdx (1..6)
    #   E20: AnnTotalDone (Selected Year on Tab 2)
    #   E21: AnnTotalTarget
    #   E22: AnnOverallPct
    #   E23: AnnBestStreak
    #   E24: AnnPerfectDays
    #   E25: AnnGrownDays
    #   E26: AnnMaxWeekPct
    #   E27: AnnBadgesStageIdx (1..6)
    #   E28: MonW1Date (serial date of Monday of Week 1 of Month/Year)
    # Cols G..M (6..12):
    #   Row 0 (Excel 1): Day 1..7 Stage Index (1..7)
    #   Rows 2..16 (Excel 3..17): 15x7 running streak matrix for active week
    #   Col N (13), rows 2..16: per-habit max streak in active week
    ws_calc.hide_gridlines(2)
    for idx, m in enumerate(MONTHS_EN):
        ws_calc.write(idx, 0, m)
    for idx, yr in enumerate(range(2024, 2041)):
        ws_calc.write(idx, 1, yr)
    for idx, wk in enumerate(WEEKS_VI):
        ws_calc.write(idx, 2, wk)
    # Mobile Daily Tasks lookups: Days 1..31 in Col R (17), Priorities in Col S (18)
    # (Cols P & Q are reserved for YearStreakHelper & YearWeekPctHelper!)
    for d_num in range(1, 32):
        ws_calc.write_number(d_num - 1, 17, d_num)
    for idx_p, p_lbl in enumerate(TASK_PRIORITIES):
        ws_calc.write(idx_p, 18, p_lbl)

    month_src = f"={cq}!$A$1:$A$12"
    year_src = f"={cq}!$B$1:$B$17"
    week_src = f"={cq}!$C$1:$C$5"
    day_src = f"={cq}!$R$1:$R$31"
    prio_src = f"={cq}!$S$1:$S$3"

    # Helper refs on _Calc Col E (col idx 4)
    E = lambda r1: f"{cq}!$E${r1}"
    calc_labels = [
        "MonthNum", "Year", "WeekNum", "ActiveHabitCount", "ActiveDaysInWeek",
        "WeeklyDone", "WeeklyTarget", "WeeklyPct", "WeeklyBestStreak", "WeeklyPerfectDays",
        "WeeklyGrownDays", "WeeklyHeroStageIdx", "ActiveWeekKey", "LastLoadedWeekKey",
        "LastGoalYear", "GoalsDone", "GoalsTotal", "GoalsPct", "GoalsHeroStageIdx",
        "AnnTotalDone", "AnnTotalTarget", "AnnOverallPct", "AnnBestStreak",
        "AnnPerfectDays", "AnnGrownDays", "AnnMaxWeekPct", "AnnBadgesStageIdx", "MonW1Date",
        "LastTaskDateKey", "MobTasksDone", "MobTasksTotal", "MobTasksPct", "MobTasksStageIdx",
    ]
    for i, lab in enumerate(calc_labels):
        ws_calc.write(i, 3, lab)

    # Row coordinates on Tab 1 (`📱 Tuần Này`)
    R_DAY_HDR = 19   # Excel row 20 (day numbers 1..31 or "")
    R_H0 = 20        # Excel row 21 (1st habit row)
    R_H1 = R_H0 + N_MOB_HABITS - 1  # Excel row 35 (15th habit row)
    R_DONE = 15      # Excel row 16 (daily done counts)
    R_PCT = 16       # Excel row 17 (daily %)

    ws_calc.write_formula(0, 4, f"=IFERROR(MATCH({wq}!$B$5,$A$1:$A$12,0),1)")
    ws_calc.write_formula(1, 4, f"=IFERROR(--{wq}!$C$5,2026)")
    ws_calc.write_formula(2, 4, f"=IFERROR(MATCH({wq}!$F$5,$C$1:$C$5,0),1)")
    ws_calc.write_formula(3, 4, f'=COUNTIF({wq}!$B${R_H0 + 1}:$B${R_H1 + 1},"?*")')
    ws_calc.write_formula(4, 4, f"=COUNT({wq}!$C${R_DAY_HDR + 1}:$I${R_DAY_HDR + 1})")
    ws_calc.write_formula(5, 4, f"=SUM({wq}!$C${R_DONE + 1}:$I${R_DONE + 1})")
    ws_calc.write_formula(6, 4, "=$E$4*$E$5")
    ws_calc.write_formula(7, 4, "=IFERROR(MIN(1,$E$6/$E$7),0)")
    ws_calc.write_formula(8, 4, "=MAX(0,$N$3:$N$17)")
    ws_calc.write_formula(9, 4, f'=COUNTIF({wq}!$C${R_PCT + 1}:$I${R_PCT + 1},">=0.999")')
    ws_calc.write_formula(10, 4, f'=COUNTIF({wq}!$C${R_PCT + 1}:$I${R_PCT + 1},">="&CFG_THR_3)')
    ws_calc.write_formula(11, 4, _stage6("$E$8", t.num_stages))
    ws_calc.write_formula(12, 4, '=TEXT($E$2,"0000")&"-"&TEXT($E$1,"00")&"-W"&$E$3')
    ws_calc.write(13, 4, week_key)  # LastLoadedWeekKey (updated by Apps Script onEdit)
    ws_calc.write(14, 4, year)      # LastGoalYear (updated by Apps Script onEdit)

    # Tab 2 (`🎯 Mục Tiêu & Thành Tựu`) live Yearly Goals rows: Excel rows 11..22 (0-based 10..21)
    R_G0 = 10
    R_G1 = R_G0 + N_MOB_GOALS - 1  # Excel row 22
    ws_calc.write_formula(15, 4, f'=COUNTIFS({gq}!$C${R_G0 + 1}:$C${R_G1 + 1},"?*",{gq}!$B${R_G0 + 1}:$B${R_G1 + 1},TRUE)')
    ws_calc.write_formula(16, 4, f'=COUNTIF({gq}!$C${R_G0 + 1}:$C${R_G1 + 1},"?*")')
    ws_calc.write_formula(17, 4, "=IFERROR($E$16/$E$17,0)")
    ws_calc.write_formula(18, 4, _stage6("$E$18", t.num_stages))

    # Annual metrics for Selected Year on Tab 2 (`$E$3`): combines live active week (if same year) + other saved weeks in `_Database`!
    sel_y_g = f"{gq}!$E$3"
    ws_calc.write_formula(
        19, 4,
        f'=IF({sel_y_g}=$E$2,$E$6,0)+SUMIFS({dbq}!$Q$2:$Q$400,{dbq}!$N$2:$N$400,{sel_y_g},{dbq}!$M$2:$M$400,"<>"&$E$13)'
    )
    ws_calc.write_formula(
        20, 4,
        f'=IF({sel_y_g}=$E$2,$E$7,0)+SUMIFS({dbq}!$R$2:$R$400,{dbq}!$N$2:$N$400,{sel_y_g},{dbq}!$M$2:$M$400,"<>"&$E$13)'
    )
    ws_calc.write_formula(21, 4, "=IFERROR(MIN(1,$E$20/$E$21),0)")
    # Annual BestStreak across live active week + saved weeks in `_Database` (universal MAXIFS-free via helper col O!)
    # Col O (14), rows 1..100? Even simpler & 100% Excel 2016 + GSheets safe without array CSE:
    # Use helper range `_Calc!P2:P80` = IF(_Database!N2=sel_y, IF(_Database!M2<>E13, _Database!U2, 0), 0)!
    ws_calc.write(0, 15, "YearStreakHelper")
    ws_calc.write(0, 16, "YearWeekPctHelper")
    for hr in range(1, 65):
        xr = hr + 1
        ws_calc.write_formula(
            hr, 15,
            f'=IF(AND({dbq}!$N${xr}={sel_y_g},{dbq}!$M${xr}<>$E$13),{dbq}!$U${xr},0)'
        )
        ws_calc.write_formula(
            hr, 16,
            f'=IF(AND({dbq}!$N${xr}={sel_y_g},{dbq}!$M${xr}<>$E$13),IFERROR({dbq}!$Q${xr}/{dbq}!$R${xr},0),0)'
        )
    ws_calc.write_formula(22, 4, f"=MAX(IF({sel_y_g}=$E$2,$E$9,0),MAX($P$2:$P$65))")
    ws_calc.write_formula(
        23, 4,
        f'=IF({sel_y_g}=$E$2,$E$10,0)+SUMIFS({dbq}!$T$2:$T$400,{dbq}!$N$2:$N$400,{sel_y_g},{dbq}!$M$2:$M$400,"<>"&$E$13)'
    )
    ws_calc.write_formula(
        24, 4,
        f'=IF({sel_y_g}=$E$2,$E$11,0)+SUMIFS({dbq}!$S$2:$S$400,{dbq}!$N$2:$N$400,{sel_y_g},{dbq}!$M$2:$M$400,"<>"&$E$13)'
    )
    ws_calc.write_formula(25, 4, f"=MAX(IF({sel_y_g}=$E$2,$E$8,0),MAX($Q$2:$Q$65))")
    # Badges stage index (reads 6 badge progress cells on Tab 2: F32:F37 -> 0-based rows 31..36)
    ws_calc.write_formula(26, 4, _stage6(f'(COUNTIF({gq}!$F$32:$F$37,">=1")/6)', t.num_stages))
    # Monday of Week 1 of (Year, Month)
    ws_calc.write_formula(27, 4, "=DATE($E$2,$E$1,1)-WEEKDAY(DATE($E$2,$E$1,1),2)+1")

    # 7-Day Stage Index row on `_Calc!G1:M1` (row 0, cols 6..12)
    for dow in range(7):
        col_wk = 2 + dow  # Col C (2) .. Col I (8)
        dc = f"{wq}!{acell(R_DAY_HDR, col_wk)}"
        pc = f"{wq}!{acell(R_PCT, col_wk)}"
        st_expr = _stage6(pc, t.num_stages)[1:]
        ws_calc.write_formula(
            0, 6 + dow,
            f'=IF({dc}="",{t.hide_stage_val},{st_expr})'
        )

    # 15x7 running streak matrix on `_Calc!G3:M17` + row max in `N3:N17`
    for hi in range(N_MOB_HABITS):
        rc_s = 2 + hi
        r_hab = R_H0 + hi
        for dow in range(7):
            c_wk = 2 + dow
            tr_ref = f"{wq}!{cell(r_hab, c_wk)}"
            dc_ref = f"{wq}!{acell(R_DAY_HDR, c_wk)}"
            nm_ref = f"{wq}!{acell(r_hab, 1)}"
            prev = "0" if dow == 0 else cell(rc_s, 6 + dow - 1)
            ws_calc.write_formula(
                rc_s, 6 + dow,
                f'=IF(AND({nm_ref}<>"",{dc_ref}<>"",{tr_ref}=TRUE),{prev}+1,0)'
            )
        ws_calc.write_formula(rc_s, 13, f"=MAX({rng(rc_s, 6, rc_s, 12, absolute=False)})")

    # =========================================================================
    #  TAB 1: `📱 Tuần Này` (Strict 8-Column Portrait Stack B:I!)
    # =========================================================================
    cv1 = Canvas(wb, ws_wk, styles, MOBILE_WEEK_SHEET, universal=False, gsheets=True)
    cv1.col(0, 1.5)
    cv1.col(1, 25.0)
    for c in range(2, 9):
        cv1.col(c, 6.4)
    cv1.col(9, 1.5)

    cv1.row(0, 8)
    # ---- CARD 1: Header & Selectors (Rows 2..6 -> idx 1..5) ----
    cv1.row(1, 36)
    cv1.row(2, 24)
    cv1.row(3, 22)
    cv1.row(4, 34)
    cv1.row(5, 24)
    cv1.row(6, 10)

    cv1.merge(1, 1, 1, 8, f"{t.emoji}  {t.name}", font_name=t.font_title, font_size=15,
              bold=True, align="center", bg_color=t.primary, font_color=t.on_primary)
    cv1.merge(2, 1, 2, 8, "📱  MOBILE PORTRAIT TRACKER  •  Khổ dọc tối ưu cho điện thoại",
              font_size=10, italic=True, align="center", bg_color=t.soft, font_color=t.ink)

    cv1.put(3, 1, "📅 THÁNG (MONTH)", bold=True, font_size=10, align="center", bg_color=t.soft, font_color=t.ink)
    cv1.merge(3, 2, 3, 4, "🗓️ NĂM (YEAR)", bold=True, font_size=10, align="center", bg_color=t.soft, font_color=t.ink)
    cv1.merge(3, 5, 3, 8, "📆 TUẦN (WEEK)", bold=True, font_size=10, align="center", bg_color=t.soft, font_color=t.ink)

    pill = dict(font_size=13, bold=True, align="center", bg_color=t.card, font_color=t.primary_dark,
                top=1, top_color=t.primary, bottom=1, bottom_color=t.primary,
                left=1, left_color=t.primary, right=1, right_color=t.primary)
    cv1.put(4, 1, month_name, **pill)
    cv1.merge(4, 2, 4, 4, year, num_format="0", **pill)
    cv1.merge(4, 5, 4, 8, week_label, **pill)

    ws_wk.data_validation("$B$5", {"validate": "list", "source": month_src,
                                   "input_title": "Chọn Tháng", "input_message": "Chọn tháng (January–December)"})
    ws_wk.data_validation("$C$5", {"validate": "list", "source": year_src,
                                   "input_title": "Chọn Năm", "input_message": "Chọn năm (2024–2040)"})
    ws_wk.data_validation("$F$5", {"validate": "list", "source": week_src,
                                   "input_title": "Chọn Tuần", "input_message": "Chọn Tuần 1 đến Tuần 5"})

    cv1.merge(5, 1, 5, 8,
              f'="Tháng "&{E(1)}&"/"&{E(2)}&"  •  "&$F$5&"  •  "&{E(5)}&" ngày trong tháng"',
              font_size=10, align="center", bg_color=t.card, font_color=t.muted)
    cv1.box(1, 1, 5, 8, t.line)

    # ---- CARD 2: Weekly Hero Progress Card (Rows 8..12 -> idx 7..11) ----
    cv1.row(7, 28)
    cv1.row(8, 28)
    cv1.row(9, 28)
    cv1.row(10, 24)
    cv1.row(11, 24)
    cv1.row(12, 10)

    cv1.merge(7, 1, 7, 8, f"{t.emoji}  TIẾN ĐỘ TUẦN NÀY • WEEKLY HERO", bold=True, font_size=11,
              align="center", bg_color=t.primary, font_color=t.on_primary)
    cv1.merge(8, 1, 9, 4, f"={E(8)}", bold=True, font_size=28, align="center",
              num_format="0%", bg_color=t.card, font_color=t.primary_dark)
    cv1.merge(10, 1, 10, 4, f'="✓ Hoàn thành: "&{E(6)}&" / "&{E(7)}&" lượt"',
              bold=True, font_size=10, align="center", bg_color=t.card, font_color=t.ink)
    cv1.merge(11, 1, 11, 4, f'="🔥 Chuỗi tuần: "&{E(9)}&"d  •  ✨ "&{E(10)}&" ngày 100%"',
              bold=False, font_size=10, align="center", bg_color=t.soft, font_color=t.ink)
    # Right side: Large Dynamic Weekly Hero Sprite via cached _Assets!
    cv1.merge(8, 5, 11, 8, _img_formula(E(12), assets_range=t.assets_range), align="center", bg_color=t.card)
    cv1.vline(4, 8, 11, t.line, where="right")
    cv1.box(7, 1, 11, 8, t.line)

    # ---- CARD 3: 7-Day Mini Growth Garden (Rows 14..17 -> idx 13..16) ----
    cv1.row(13, 28)
    cv1.row(14, 66)   # 7 live cached sprites
    cv1.row(15, 24)   # Completed counts
    cv1.row(16, 24)   # Daily %
    cv1.row(17, 10)

    cv1.merge(13, 1, 13, 8, "🌱  KHU VƯỜN 7 NGÀY TRONG TUẦN", bold=True, font_size=11,
              align="center", bg_color=t.primary, font_color=t.on_primary)
    cv1.put(14, 1, f"{t.emoji}  TĂNG TRƯỞNG", bold=True, font_size=11, align="center",
            bg_color=t.card, font_color=t.primary_dark)
    cv1.put(15, 1, "HOÀN THÀNH  ✓", bold=True, font_size=10, align="right", indent=1,
            bg_color=t.card, font_color=t.ink, top=1, top_color=t.line)
    cv1.put(16, 1, "% TRONG NGÀY", bold=False, font_size=10, align="right", indent=1,
            bg_color=t.card, font_color=t.muted)

    names_rng = f"$B${R_H0 + 1}:$B${R_H1 + 1}"
    for dow in range(7):
        c = 2 + dow
        col_l = colname(c)
        dc = f"{col_l}${R_DAY_HDR + 1}"
        st_ref = f"{cq}!{acell(0, 6 + dow)}"
        cv1.put(14, c, _img_formula(st_ref, blank_guard=dc, assets_range=t.assets_range), align="center", bg_color=t.card)
        col_body = f"{col_l}${R_H0 + 1}:{col_l}${R_H1 + 1}"
        cv1.put(15, c,
                f'=IF({dc}="","",COUNTIFS({names_rng},"?*",{col_body},TRUE))',
                bold=True, font_size=10, align="center", bg_color=t.week_tint[dow % 5], font_color=t.ink)
        cv1.put(16, c, f'=IF({dc}="","",IFERROR({cell(15, c)}/{E(4)},0))',
                bold=False, font_size=10, num_format="0%", align="center", bg_color=t.card, font_color=t.ink)
    cv1.grid(15, 2, 16, 8, t.line)
    cv1.hline(14, 2, 8, t.line, where="bottom")
    cv1.box(13, 1, 16, 8, t.line)

    # ---- CARD 4: Thumb-Friendly Habit Checklist (Rows 19..36 -> idx 18..35) ----
    cv1.row(18, 28)
    cv1.row(19, 25)
    cv1.merge(18, 1, 18, 1, "THÓI QUEN • HABITS", bold=True, font_size=11,
              align="left", indent=1, bg_color=t.primary, font_color=t.on_primary)
    cv1.put(19, 1, f'="Thói quen: "&{E(4)}&"  •  Chạm ô để tick"', bold=False, font_size=10,
            align="left", indent=1, bg_color=t.soft, font_color=t.ink)

    for dow in range(7):
        c = 2 + dow
        w_idx = dow % 5
        cv1.put(18, c, DAYS_VI[dow], bold=True, font_size=11, align="center",
                bg_color=t.week_head[w_idx], font_color=t.week_on[w_idx])
        # Real Mon-Sun calendar date inside selected month, else cleanly blank ""!
        dt_expr = f"({E(28)}+({E(3)}-1)*7+{dow})"
        cv1.put(19, c, f'=IF(MONTH({dt_expr})={E(1)},DAY({dt_expr}),"")',
                bold=False, font_size=10, align="center", bg_color=t.soft, font_color=t.ink)

    ticks_15 = _sample_week_ticks(habits, year, month_idx, week_num, tdef.seed)
    for hi in range(N_MOB_HABITS):
        r = R_H0 + hi
        cv1.row(r, 38)   # Generous 38pt thumb-friendly tap target!
        h = habits[hi] if hi < len(habits) else None
        bg_row = t.card if hi % 2 == 0 else t.page
        cv1.put(r, 1, h.name if h else "", bold=True, font_size=10, align="left", indent=1,
                text_wrap=True, bg_color=bg_row, font_color=t.ink)
        for dow in range(7):
            c = 2 + dow
            cv1.checkbox(r, c, ticks_15[hi][dow], align="center", font_size=10,
                         font_color=t.week_check[dow % 5], bg_color=bg_row)

    # Totals row (Row 36 -> idx 35)
    r_tot = R_H1 + 1
    cv1.row(r_tot, 28)
    cv1.put(r_tot, 1, "TỔNG HOÀN THÀNH NGÀY", bold=True, font_size=10, align="left", indent=1,
            bg_color=t.soft, font_color=t.ink)
    for dow in range(7):
        c = 2 + dow
        dc = f"{colname(c)}${R_DAY_HDR + 1}"
        cv1.put(r_tot, c, f'=IF({dc}="","",{cell(15, c)})', bold=True, font_size=10,
                align="center", bg_color=t.soft, font_color=t.primary_dark)

    cv1.grid(18, 1, r_tot, 8, t.line)
    cv1.hline(r_tot, 1, 8, t.primary, where="top")
    cv1.box(18, 1, r_tot, 8, t.line)

    # Lightweight Conditional Formatting on Tab 1: mask out-of-month + fast native `cell == TRUE`!
    body_rng = rng(R_H0, 2, R_H1, 8, absolute=False)
    ws_wk.conditional_format(body_rng, {
        "type": "formula", "criteria": f'=C${R_DAY_HDR + 1}=""',
        "format": wb.add_format({"bg_color": t.page, "font_color": t.page}),
        "stop_if_true": True,
    })
    for dow in range(7):
        c = 2 + dow
        col_rng = rng(R_H0, c, R_H1, c, absolute=False)
        chk_bg = checked_pastel_bg(t.week_head[dow % 5], t.week_tint[dow % 5])
        ws_wk.conditional_format(col_rng, {
            "type": "cell", "criteria": "==", "value": True,
            "format": wb.add_format({"bg_color": chk_bg, "font_color": t.week_check[dow % 5], "bold": True}),
        })
    ws_wk.conditional_format(rng(16, 2, 16, 8), {
        "type": "3_color_scale", "min_type": "num", "min_value": 0,
        "mid_type": "num", "mid_value": 0.5, "max_type": "num", "max_value": 1,
        "min_color": "#FFFFFF", "mid_color": t.week_tint[0], "max_color": t.bar,
    })

    # ---- CARD 5: Per-Habit Weekly Progress Bars (Stacked BELOW inside B:I!) ----
    r_p0 = r_tot + 2
    cv1.row(r_tot + 1, 10)
    cv1.row(r_p0, 28)
    cv1.row(r_p0 + 1, 24)
    cv1.merge(r_p0, 1, r_p0, 8, "📊  TIẾN ĐỘ TỪNG THÓI QUEN TRONG TUẦN", bold=True, font_size=11,
              align="center", bg_color=t.primary, font_color=t.on_primary)
    cv1.put(r_p0 + 1, 1, "THÓI QUEN", bold=True, font_size=10, align="left", indent=1,
            bg_color=t.soft, font_color=t.ink)
    cv1.merge(r_p0 + 1, 2, r_p0 + 1, 4, "HOÀN THÀNH", bold=True, font_size=10, align="center",
              bg_color=t.soft, font_color=t.ink)
    cv1.merge(r_p0 + 1, 5, r_p0 + 1, 8, "TIẾN ĐỘ (%)", bold=True, font_size=10, align="center",
              bg_color=t.soft, font_color=t.ink)

    r_pf = r_p0 + 2
    for hi in range(N_MOB_HABITS):
        rr = r_pf + hi
        h_xl = R_H0 + hi + 1
        cv1.row(rr, 32)
        bg_row = t.card if hi % 2 == 0 else t.page
        nm_ref = f"$B${h_xl}"
        done_expr = f'COUNTIFS($C${h_xl}:$I${h_xl},TRUE,$C${R_DAY_HDR + 1}:$I${R_DAY_HDR + 1},">0")'
        cv1.put(rr, 1, f'=IF({nm_ref}="","",{nm_ref})', bold=True, font_size=10, align="left", indent=1,
                text_wrap=True, bg_color=bg_row, font_color=t.ink)
        cv1.merge(rr, 2, rr, 4, f'=IF({nm_ref}="","",{done_expr}&" / "&{E(5)})',
                  bold=False, font_size=10, align="center", bg_color=bg_row, font_color=t.muted)
        cv1.merge(rr, 5, rr, 8, f'=IF({nm_ref}="","",IFERROR({done_expr}/{E(5)},0))',
                  bold=True, font_size=10, num_format="0%", align="center", bg_color=bg_row, font_color=t.ink)
    r_pl = r_pf + N_MOB_HABITS - 1
    cv1.grid(r_p0 + 1, 1, r_pl, 8, t.line)
    cv1.box(r_p0, 1, r_pl, 8, t.line)
    ws_wk.conditional_format(rng(r_pf, 5, r_pl, 8), {
        "type": "data_bar", "bar_color": t.bar, "bar_solid": True,
        "min_type": "num", "min_value": 0, "max_type": "num", "max_value": 1,
        "bar_border_color": t.bar,
    })

    # ---- CARD 6: Compact Portrait Productivity Chart (Inside B:I!) ----
    r_ch0 = r_pl + 2
    cv1.row(r_pl + 1, 10)
    for rr in range(r_ch0, r_ch0 + 10):
        cv1.row(rr, 22)
    cv1.box(r_ch0, 1, r_ch0 + 9, 8, t.line, fill=t.card)

    ch = wb.add_chart({"type": "column"})
    ch.add_series({
        "name": "% Hoàn thành",
        "categories": f"={wq}!$C$19:$I$19",
        "values": f"={wq}!$C$17:$I$17",
        "fill": {"color": t.chart_fill},
        "border": {"color": t.chart_line, "width": 1.0},
        "data_labels": {"value": True, "num_format": "0%", "font": {"name": t.font, "size": 10, "color": t.ink}},
    })
    ch_ln = wb.add_chart({"type": "line"})
    ch_ln.add_series({
        "name": "Xu hướng",
        "categories": f"={wq}!$C$19:$I$19",
        "values": f"={wq}!$C$17:$I$17",
        "line": {"color": t.chart_line, "width": 2.0},
        "marker": {"type": "circle", "size": 5, "fill": {"color": t.primary_dark},
                   "border": {"color": "#FFFFFF", "width": 1.0}},
    })
    ch.combine(ch_ln)
    ch.set_title({"name": "📈  NĂNG SUẤT 7 NGÀY TRONG TUẦN (T2 – CN)",
                  "name_font": {"name": t.font, "size": 11, "bold": True, "color": t.ink}})
    ch.set_y_axis({"min": 0, "max": 1, "major_unit": 0.25, "num_format": "0%",
                   "num_font": axis_font(t, 10), "line": {"none": True},
                   "major_gridlines": {"visible": True, "line": {"color": t.line, "dash_type": "dash"}}})
    ch.set_x_axis({"num_font": axis_font(t, 10), "line": {"color": t.line}})
    ch.set_legend({"none": True})
    ch.set_chartarea({"border": {"none": True}, "fill": {"color": t.card}})
    ch.set_plotarea({"layout": {"x": 0.11, "y": 0.20, "width": 0.85, "height": 0.66}})
    place_chart(cv1, ch, r_ch0, 1, r_ch0 + 9, 8, pad_x=4, pad_y=4)

    # ---- CARD 7: Quick Reflection Card (Inside B:I!) ----
    r_nt0 = r_ch0 + 11
    cv1.row(r_ch0 + 10, 10)
    cv1.row(r_nt0, 28)
    cv1.merge(r_nt0, 1, r_nt0, 8, "📝  GHI CHÚ NHANH TUẦN NÀY • QUICK REFLECTION",
              bold=True, font_size=11, align="center", bg_color=t.primary, font_color=t.on_primary)
    reflections = [
        "✨  Điều làm tốt nhất tuần này: Duy trì đều nhịp buổi sáng & uống đủ nước.",
        "🌱  Điều cần cải thiện tuần tới: Đi ngủ sớm hơn trước 23h00.",
        "🎁  Phần thưởng nhỏ cho bản thân: Một ly đồ uống yêu thích vào cuối tuần!",
    ]
    for idx_n, txt in enumerate(reflections):
        rr = r_nt0 + 1 + idx_n
        cv1.row(rr, 40)
        cv1.merge(rr, 1, rr, 8, txt, bold=False, font_size=10, align="left", indent=1,
                  text_wrap=True, bg_color=t.card if idx_n % 2 == 0 else t.page, font_color=t.ink)
        cv1.hline(rr, 1, 8, t.line)
    cv1.box(r_nt0, 1, r_nt0 + 3, 8, t.line)
    cv1.row(r_nt0 + 4, 10)

    _finish_mobile_sheet(ws_wk, cv1, t.primary, zoom=100)

    # =========================================================================
    #  TAB 2 (v3.0 NEW!): `📝 Việc Hôm Nay` — Mobile Portrait Daily One-Off Tasks (B:I!)
    # =========================================================================
    N_MOB_TASKS = 15
    ws_calc.write(28, 4, DEFAULT_TASK_KEY)  # E29: LastTaskDateKey
    ws_calc.write_formula(29, 4, f'=COUNTIFS({tq}!$C$16:$C$30,"?*",{tq}!$B$16:$B$30,TRUE)')  # E30: Done
    ws_calc.write_formula(30, 4, f'=COUNTIF({tq}!$C$16:$C$30,"?*")')                        # E31: Total
    ws_calc.write_formula(31, 4, f"=IFERROR({E(30)}/{E(31)},0)")                            # E32: Pct
    ws_calc.write_formula(32, 4, _stage6(E(32), t.num_stages))                                # E33: StageIdx (1..6/7)

    cvt = Canvas(wb, ws_dt, styles, MOBILE_TASKS_SHEET, universal=False, gsheets=True)
    cvt.col(0, 1.5)
    cvt.col(1, 6.4)     # Col B: Checkbox + Day picker
    cvt.col(2, 10.2)    # Col C..F: Task Name (merged 4 cols = ~35 width!)
    cvt.col(3, 8.2)
    cvt.col(4, 8.2)
    cvt.col(5, 8.2)
    cvt.col(6, 6.4)     # Col G..I: Priority pill (merged 3 cols = ~19.2 width!)
    cvt.col(7, 6.4)
    cvt.col(8, 6.4)
    cvt.col(9, 1.5)

    cvt.row(0, 8)
    cvt.row(1, 36)
    cvt.row(2, 22)
    cvt.row(3, 22)
    cvt.row(4, 34)
    cvt.row(5, 24)
    cvt.row(6, 10)

    cvt.merge(1, 1, 1, 8, f"{t.emoji}  VIỆC HÔM NAY  •  DAILY TASKS", font_name=t.font_title,
              font_size=15, bold=True, align="center", bg_color=t.primary, font_color=t.on_primary)
    cvt.merge(2, 1, 2, 8, "📝  Nhiệm vụ đột xuất theo ngày  •  0 cuộn ngang", italic=True,
              font_size=10, align="center", bg_color=t.soft, font_color=t.ink)
    cvt.put(3, 1, "NGÀY", bold=True, font_size=10, align="center", bg_color=t.card, font_color=t.muted)
    cvt.merge(3, 2, 3, 5, "THÁNG (MONTH)", bold=True, font_size=10, align="center", bg_color=t.card, font_color=t.muted)
    cvt.merge(3, 6, 3, 8, "NĂM (YEAR)", bold=True, font_size=10, align="center", bg_color=t.card, font_color=t.muted)

    cvt.put(4, 1, DEFAULT_TASK_DAY, font_name=t.font_title, font_size=13, bold=True, align="center",
            num_format="0", bg_color=t.card, font_color=t.primary_dark)
    cvt.merge(4, 2, 4, 5, DEFAULT_TASK_MONTH, font_name=t.font_title, font_size=13, bold=True,
              align="center", bg_color=t.card, font_color=t.primary_dark)
    cvt.merge(4, 6, 4, 8, DEFAULT_TASK_YEAR, font_name=t.font_title, font_size=13, bold=True,
              align="center", num_format="0", bg_color=t.card, font_color=t.primary_dark)

    m_mob = f"IFERROR(MATCH($C$5,{cq}!$A$1:$A$12,0),1)"
    d_mob = f"MIN(IFERROR(--$B$5,1),DAY(EOMONTH(DATE($G$5,{m_mob},1),0)))"
    dt_mob = f"DATE($G$5,{m_mob},{d_mob})"
    cvt.merge(5, 1, 5, 8,
              f'=CHOOSE(WEEKDAY({dt_mob},2),"Thứ Hai","Thứ Ba","Thứ Tư","Thứ Năm","Thứ Sáu","Thứ Bảy","Chủ Nhật")'
              f'&", "&TEXT({dt_mob},"dd/mm/yyyy")',
              bold=True, font_size=10, align="center", bg_color=t.card, font_color=t.muted)
    cvt.grid(3, 1, 4, 8, t.line)
    cvt.box(1, 1, 5, 8, t.line)

    ws_dt.data_validation("B5", {"validate": "list", "source": day_src})
    ws_dt.data_validation("C5", {"validate": "list", "source": month_src})
    ws_dt.data_validation("G5", {"validate": "list", "source": year_src})

    # Card 2: Daily Hero Card (Rows 8..13 -> 0-based 7..12)
    cvt.row(7, 28)
    for rr in range(8, 12):
        cvt.row(rr, 28)
    cvt.row(12, 10)
    cvt.merge(7, 1, 7, 8, f"{t.emoji}  TIẾN ĐỘ NHIỆM VỤ HÔM NAY", bold=True, font_size=11,
              align="center", bg_color=t.primary, font_color=t.on_primary)
    cvt.merge(8, 1, 9, 4, f"={E(32)}", font_name=t.font_title, font_size=26, bold=True,
              align="center", num_format="0%", bg_color=t.card, font_color=t.primary_dark)
    cvt.merge(10, 1, 10, 4, f'="✓ "&{E(30)}&" / "&{E(31)}&" việc xong"', bold=True, font_size=10,
              align="center", bg_color=t.card, font_color=t.ink)
    cvt.merge(11, 1, 11, 4, f'="⏳ Còn "&({E(31)}-{E(30)})&" việc"', font_size=10, bold=True,
              align="center", bg_color=t.soft, font_color=t.ink)
    cvt.merge(8, 5, 11, 8, _img_formula(E(33), assets_range=t.assets_range), align="center", bg_color=t.card)
    cvt.vline(4, 8, 11, t.line, where="right")
    cvt.box(7, 1, 11, 8, t.line)

    # Card 3: 15 Thumb-Friendly 38pt Task Rows (Header row 14 -> 0-based 13, Rows 16..30 -> 0-based 15..29)
    cvt.row(13, 28)
    cvt.row(14, 22)
    cvt.put(13, 1, "✓", bold=True, font_size=11, align="center", bg_color=t.primary, font_color=t.on_primary)
    cvt.merge(13, 2, 13, 5, "TÊN NHIỆM VỤ HÔM NAY", bold=True, font_size=11, align="left", indent=1,
              bg_color=t.primary, font_color=t.on_primary)
    cvt.merge(13, 6, 13, 8, "ƯU TIÊN", bold=True, font_size=11, align="center",
              bg_color=t.primary, font_color=t.on_primary)
    cvt.merge(14, 1, 14, 8, "Chạm ô vuông bên trái để tick hoàn thành • Chọn mức ưu tiên bên phải",
              italic=True, font_size=10, align="center", bg_color=t.soft, font_color=t.muted)

    for i in range(N_MOB_TASKS):
        rr = 15 + i  # Excel rows 16..30
        cvt.row(rr, 38)
        bg = t.card if i % 2 == 0 else t.page
        if i < len(DEFAULT_DAILY_TASKS):
            done, t_nm, _cat, prio, _note = DEFAULT_DAILY_TASKS[i]
        else:
            done, t_nm, prio = False, "", ""
        cvt.checkbox(rr, 1, done, align="center", font_size=10, font_color=t.primary_dark, bg_color=bg)
        cvt.merge(rr, 2, rr, 5, t_nm, bold=True, font_size=10, align="left", indent=1, text_wrap=True,
                  bg_color=bg, font_color=t.ink)
        cvt.merge(rr, 6, rr, 8, prio, bold=True, font_size=10, align="center", bg_color=bg, font_color=t.ink)

    cvt.grid(15, 1, 15 + N_MOB_TASKS - 1, 8, t.line)
    cvt.box(13, 1, 15 + N_MOB_TASKS - 1, 8, t.line)
    ws_dt.data_validation("G16:G30", {"validate": "list", "source": prio_src})
    ws_dt.conditional_format("B16:B30", {
        "type": "cell", "criteria": "==", "value": True,
        "format": wb.add_format({"bg_color": checked_pastel_bg(t.primary, t.soft), "font_color": t.primary_dark, "bold": True}),
    })
    ws_dt.conditional_format("C16:F30", {
        "type": "formula", "criteria": "=$B16=TRUE",
        "format": wb.add_format({"font_strikeout": True, "font_color": t.muted, "bg_color": t.soft}),
    })
    ws_dt.conditional_format("G16:I30", {"type": "formula", "criteria": '=$G16="🔴 Cao"',
                                         "format": wb.add_format({"bg_color": "#FEE2E2", "font_color": "#991B1B", "bold": True})})
    ws_dt.conditional_format("G16:I30", {"type": "formula", "criteria": '=$G16="🟡 Trung bình"',
                                         "format": wb.add_format({"bg_color": "#FEF3C7", "font_color": "#92400E", "bold": True})})
    ws_dt.conditional_format("G16:I30", {"type": "formula", "criteria": '=$G16="🟢 Thấp"',
                                         "format": wb.add_format({"bg_color": "#DCFCE7", "font_color": "#166534", "bold": True})})

    # Card 4: Quick Daily Highlight Note (Rows 32..35 -> 0-based 31..34)
    cvt.row(30, 10)
    cvt.row(31, 28)
    for rr in range(32, 35):
        cvt.row(rr, 25)
    cvt.row(35, 10)
    cvt.merge(31, 1, 31, 8, "✨  ĐIỂM SÁNG & GHI CHÚ HÔM NAY", bold=True, font_size=11, align="left",
              indent=1, bg_color=t.primary, font_color=t.on_primary)
    cvt.merge(32, 1, 34, 8, DEFAULT_DAILY_HIGHLIGHT, bold=False, font_size=10, align="left", indent=1,
              text_wrap=True, bg_color=t.card, font_color=t.ink)
    cvt.box(31, 1, 34, 8, t.line)
    _finish_mobile_sheet(ws_dt, cvt, t.primary, zoom=100)

    # =========================================================================
    #  TAB 3: `🎯 Mục Tiêu & Thành Tựu` (Vertical Portrait inside B:I!)
    # =========================================================================
    cv2 = Canvas(wb, ws_go, styles, MOBILE_GOALS_SHEET, universal=False, gsheets=True)
    cv2.col(0, 1.5)
    cv2.col(1, 6.4)     # Checkbox col B (thumb-friendly!)
    cv2.col(2, 20.0)    # Goal / Badge col C
    for c in range(3, 9):
        cv2.col(c, 7.2)  # Cols D..I
    cv2.col(9, 1.5)

    cv2.row(0, 8)
    # Card 1: Header + Year Dropdown + Live Yearly Hero Sprite (Rows 2..8 -> idx 1..7)
    cv2.row(1, 36)
    cv2.row(2, 32)
    cv2.row(3, 24)
    cv2.row(4, 28)
    cv2.row(5, 24)
    cv2.row(6, 24)
    cv2.row(7, 10)

    cv2.merge(1, 1, 1, 8, f"{t.emoji}  MỤC TIÊU & THÀNH TỰU NĂM", font_size=15,
              bold=True, align="center", bg_color=t.primary, font_color=t.on_primary)
    cv2.merge(2, 1, 2, 3, "📅  CHỌN NĂM (YEAR):", bold=True, font_size=11, align="center",
              bg_color=t.soft, font_color=t.ink)
    cv2.merge(2, 4, 2, 8, year, bold=True, font_size=14, align="center", num_format="0",
              bg_color=t.card, font_color=t.primary_dark,
              top=1, top_color=t.primary, bottom=1, bottom_color=t.primary,
              left=1, left_color=t.primary, right=1, right_color=t.primary)
    ws_go.data_validation("$E$3", {"validate": "list", "source": year_src,
                                   "input_title": "Chọn Năm", "input_message": "Chọn năm (2024–2040)"})

    cv2.merge(3, 1, 4, 4, f'={E(16)}&" / "&{E(17)}', bold=True, font_size=26, align="center",
              bg_color=t.card, font_color=t.primary_dark)
    cv2.merge(5, 1, 5, 4, f'="Tiến độ mục tiêu: "&TEXT({E(18)},"0%")', bold=True, font_size=10,
              align="center", bg_color=t.card, font_color=t.ink)
    cv2.merge(6, 1, 6, 4, f'="Mục tiêu đã đạt năm "&$E$3', bold=False, font_size=10, italic=True,
              align="center", bg_color=t.soft, font_color=t.muted)
    # Right side: Live Yearly Hero Sprite via cached _Assets!
    cv2.merge(3, 5, 6, 8, _img_formula(E(19), assets_range=t.assets_range), align="center", bg_color=t.card)
    cv2.vline(4, 3, 6, t.line, where="right")
    cv2.box(1, 1, 6, 8, t.line)

    # Card 2: Vertical Goals Checklist (12 thumb-friendly 38pt rows, Rows 9..22 -> idx 8..21)
    cv2.row(8, 28)
    cv2.row(9, 24)
    cv2.merge(8, 1, 8, 8, "🎯  DANH SÁCH MỤC TIÊU NĂM (CHẠM Ô ĐỂ TICK)", bold=True, font_size=11,
              align="center", bg_color=t.primary, font_color=t.on_primary)
    cv2.put(9, 1, "☑", bold=True, font_size=10, align="center", bg_color=t.soft, font_color=t.ink)
    cv2.merge(9, 2, 9, 6, "MỤC TIÊU QUAN TRỌNG", bold=True, font_size=10, align="left", indent=1,
              bg_color=t.soft, font_color=t.ink)
    cv2.merge(9, 7, 9, 8, "TRẠNG THÁI", bold=True, font_size=10, align="center",
              bg_color=t.soft, font_color=t.ink)

    for gi in range(N_MOB_GOALS):
        rr = R_G0 + gi
        cv2.row(rr, 38)
        chk, gtxt = MOBILE_GOALS_SAMPLE[gi] if gi < len(MOBILE_GOALS_SAMPLE) else (False, "")
        bg_row = t.card if gi % 2 == 0 else t.page
        cv2.checkbox(rr, 1, chk, align="center", font_size=10, font_color=t.primary_dark, bg_color=bg_row)
        cv2.merge(rr, 2, rr, 6, gtxt, bold=True, font_size=10, align="left", indent=1,
                  text_wrap=True, bg_color=bg_row, font_color=t.ink)
        cv2.merge(rr, 7, rr, 8, f'=IF($C{rr + 1}="","",IF($B{rr + 1}=TRUE,"✓ Đạt","○ Đang làm"))',
                  bold=True, font_size=10, align="center", bg_color=bg_row, font_color=t.muted)
    cv2.grid(9, 1, R_G1, 8, t.line)
    cv2.box(8, 1, R_G1, 8, t.line)
    ws_go.conditional_format(rng(R_G0, 1, R_G1, 1, absolute=False), {
        "type": "cell", "criteria": "==", "value": True,
        "format": wb.add_format({"bg_color": checked_pastel_bg(t.primary, t.soft), "font_color": t.primary_dark, "bold": True}),
    })
    ws_go.conditional_format(rng(R_G0, 7, R_G1, 8, absolute=False), {
        "type": "formula", "criteria": f'=AND($C{R_G0 + 1}<>"",$B{R_G0 + 1}=TRUE)',
        "format": wb.add_format({"bg_color": t.primary, "font_color": t.on_primary, "bold": True}),
    })

    # Card 3: Annual KPI 2x2 Grid (Rows 24..29 -> idx 23..28)
    r_k0 = R_G1 + 2
    cv2.row(R_G1 + 1, 10)
    cv2.row(r_k0, 28)
    cv2.row(r_k0 + 1, 22)
    cv2.row(r_k0 + 2, 30)
    cv2.row(r_k0 + 3, 22)
    cv2.row(r_k0 + 4, 30)
    cv2.row(r_k0 + 5, 10)

    cv2.merge(r_k0, 1, r_k0, 8, f'="📊  TỔNG KẾT NĂM "&$E$3&"  •  ANNUAL OVERVIEW"', bold=True,
              font_size=11, align="center", bg_color=t.primary, font_color=t.on_primary)
    cv2.merge(r_k0 + 1, 1, r_k0 + 1, 4, "✅ TỔNG LƯỢT HOÀN THÀNH", bold=True, font_size=10, align="center",
              bg_color=t.soft, font_color=t.ink)
    cv2.merge(r_k0 + 1, 5, r_k0 + 1, 8, "🌟 TỈ LỆ TRUNG BÌNH NĂM", bold=True, font_size=10, align="center",
              bg_color=t.soft, font_color=t.ink)
    cv2.merge(r_k0 + 2, 1, r_k0 + 2, 4, f"={E(20)}", bold=True, font_size=20, align="center",
              num_format="#,##0", bg_color=t.card, font_color=t.primary_dark)
    cv2.merge(r_k0 + 2, 5, r_k0 + 2, 8, f"={E(22)}", bold=True, font_size=20, align="center",
              num_format="0%", bg_color=t.card, font_color=t.primary_dark)

    cv2.merge(r_k0 + 3, 1, r_k0 + 3, 4, "🔥 CHUỖI DÀI NHẤT NĂM", bold=True, font_size=10, align="center",
              bg_color=t.soft, font_color=t.ink)
    cv2.merge(r_k0 + 3, 5, r_k0 + 3, 8, "✨ NGÀY HOÀN HẢO 100%", bold=True, font_size=10, align="center",
              bg_color=t.soft, font_color=t.ink)
    cv2.merge(r_k0 + 4, 1, r_k0 + 4, 4, f"={E(23)}", bold=True, font_size=18, align="center",
              num_format='0" ngày"', bg_color=t.card, font_color=t.ink)
    cv2.merge(r_k0 + 4, 5, r_k0 + 4, 8, f"={E(24)}", bold=True, font_size=18, align="center",
              num_format='0" ngày"', bg_color=t.card, font_color=t.ink)
    cv2.grid(r_k0 + 1, 1, r_k0 + 4, 8, t.line)
    cv2.box(r_k0, 1, r_k0 + 4, 8, t.line)

    # Card 4: 6 Core Achievements Wall + Live Counter (Rows 30..40 -> idx 29..39)
    r_a0 = r_k0 + 6  # idx 29 -> Excel row 30
    cv2.row(r_a0, 28)
    cv2.row(r_a0 + 1, 24)
    cv2.merge(r_a0, 1, r_a0, 8, "🏆  6 HUY HIỆU THÀNH TỰU CỐT LÕI", bold=True, font_size=11,
              align="center", bg_color=t.primary, font_color=t.on_primary)
    cv2.merge(r_a0 + 1, 1, r_a0 + 1, 4, "HUY HIỆU", bold=True, font_size=10, align="left", indent=1,
              bg_color=t.soft, font_color=t.ink)
    cv2.merge(r_a0 + 1, 5, r_a0 + 1, 6, "TIẾN ĐỘ", bold=True, font_size=10, align="center",
              bg_color=t.soft, font_color=t.ink)
    cv2.merge(r_a0 + 1, 7, r_a0 + 1, 8, "TRẠNG THÁI", bold=True, font_size=10, align="center",
              bg_color=t.soft, font_color=t.ink)

    mob_badges = [
        ("🌱 Khởi Hành (≥1 ngày ≥75%)",   f"=MIN(1,{E(25)}/1)"),
        ("🔥 Tuần Lễ Vàng (Chuỗi 7d)",     f"=MIN(1,{E(23)}/7)"),
        ("⚡ Kỷ Luật Bền Bỉ (≥15 ngày)",   f"=MIN(1,{E(25)}/15)"),
        ("🌟 Tuần Rực Rỡ (≥85% / tuần)",   f"=MIN(1,{E(26)}/0.85)"),
        ("🎯 Chinh Phục Mục Tiêu (≥50%)",  f"=MIN(1,{E(18)}/0.5)"),
        ("🏆 Bậc Thầy Cả Năm (≥80%)",      f"=MIN(1,{E(22)}/0.8)"),
    ]
    r_af = r_a0 + 2  # idx 31 -> Excel row 32 (matches _Calc!E27 `$F$32:$F$37`!)
    r_al = r_af + len(mob_badges) - 1  # Excel row 37
    for idx_b, (b_lbl, b_f) in enumerate(mob_badges):
        rr = r_af + idx_b
        cv2.row(rr, 36)
        bg_row = t.card if idx_b % 2 == 0 else t.page
        cv2.merge(rr, 1, rr, 4, b_lbl, bold=True, font_size=10, align="left", indent=1,
                  text_wrap=True, bg_color=bg_row, font_color=t.ink)
        cv2.merge(rr, 5, rr, 6, b_f, bold=True, font_size=10, num_format="0%", align="center",
                  bg_color=bg_row, font_color=t.ink)
        cv2.merge(rr, 7, rr, 8, f'=IF($F{rr + 1}>=1,"🏆 ĐÃ MỞ","🔒 Chưa mở")',
                  bold=True, font_size=10, align="center", bg_color="#F3F4F6", font_color="#8A929A")
    cv2.grid(r_a0 + 1, 1, r_al, 8, t.line)
    cv2.box(r_a0, 1, r_al, 8, t.line)
    ws_go.conditional_format(rng(r_af, 5, r_al, 6), {
        "type": "data_bar", "bar_color": t.bar, "bar_solid": True,
        "min_type": "num", "min_value": 0, "max_type": "num", "max_value": 1,
        "bar_border_color": t.bar,
    })
    ws_go.conditional_format(rng(r_af, 7, r_al, 8, absolute=False), {
        "type": "formula", "criteria": f"=$F{r_af + 1}>=1",
        "format": wb.add_format({"bg_color": t.primary, "font_color": t.on_primary, "bold": True}),
    })

    # Live Badge Counter Strip right below badges (Rows 39..41 -> idx 38..40)
    r_bc = r_al + 2
    cv2.row(r_al + 1, 10)
    cv2.row(r_bc, 34)
    cv2.row(r_bc + 1, 34)
    cv2.row(r_bc + 2, 10)
    unlocked_e = f'COUNTIF($F${r_af + 1}:$F${r_al + 1},">=1")'
    cv2.merge(r_bc, 1, r_bc, 5, f'="🏆 ĐÃ MỞ KHÓA: "&{unlocked_e}&" / 6 HUY HIỆU"',
              bold=True, font_size=12, align="center", bg_color=t.soft, font_color=t.primary_dark)
    cv2.merge(r_bc + 1, 1, r_bc + 1, 5,
              f'=IF({unlocked_e}=0,"🌱 Hãy tick thói quen để bắt đầu!",IF({unlocked_e}<=3,"✨ Khởi đầu tuyệt vời!","👑 Phong độ đỉnh cao!"))',
              bold=False, font_size=10, align="center", bg_color=t.card, font_color=t.ink)
    cv2.merge(r_bc, 6, r_bc + 1, 8, _img_formula(E(27), assets_range=t.assets_range), align="center", bg_color=t.card)
    cv2.vline(5, r_bc, r_bc + 1, t.line, where="right")
    cv2.box(r_bc, 1, r_bc + 1, 8, t.line)

    _finish_mobile_sheet(ws_go, cv2, t.primary_dark, zoom=100)

    # =========================================================================
    #  TAB 4: `📖 Hướng Dẫn` (Single-Column Mobile-Readable Portrait Guide in B:G!)
    # =========================================================================
    cv3 = Canvas(wb, ws_gd, styles, MOBILE_GUIDE_SHEET, universal=False, gsheets=True)
    cv3.col(0, 1.5)
    for c in range(1, 7):
        cv3.col(c, 11.5)  # 6 equal cols B:G = 69 chars -> exact 2x3 stage grid & mobile portrait width!
    cv3.col(7, 1.5)

    cv3.row(0, 8)
    cv3.row(1, 38)
    cv3.row(2, 26)
    cv3.row(3, 10)
    cv3.merge(1, 1, 1, 6, f"{t.emoji}  HƯỚNG DẪN BẢN ĐIỆN THOẠI", font_size=15, bold=True,
              align="center", bg_color=t.primary, font_color=t.on_primary)
    cv3.merge(2, 1, 2, 6, f"{t.name}  •  Be Vietnam Pro • Cache _Assets Siêu Mượt",
              font_size=10, italic=True, align="center", bg_color=t.soft, font_color=t.ink)
    cv3.box(1, 1, 2, 6, t.line)

    def mob_card(start_r: int, title: str, lines_list: list[str]) -> int:
        cv3.row(start_r, 28)
        cv3.merge(start_r, 1, start_r, 6, title, bold=True, font_size=11, align="left", indent=1,
                  bg_color=t.primary, font_color=t.on_primary)
        cur = start_r + 1
        for txt in lines_list:
            est = text_lines(txt, 58, factor=0.76)
            cv3.row(cur, max(46, est * 17 + 16))
            cv3.merge(cur, 1, cur, 6, txt, bold=False, font_size=10, align="left", indent=1,
                      text_wrap=True, bg_color=t.card, font_color=t.ink)
            cv3.hline(cur, 1, 6, t.line)
            cur += 1
        cv3.box(start_r, 1, cur - 1, 6, t.line)
        cv3.row(cur, 10)
        return cur + 1

    rg = 4
    rg = mob_card(rg, "📱  1. MỞ TRÊN ĐIỆN THOẠI (iOS / ANDROID) & GHIM MÀN HÌNH CHÍNH", [
        "1️⃣  Tải file lên Google Drive → Mở bằng ứng dụng Google Trang tính (Google Sheets) → Lưu dưới dạng Google Trang tính (hoặc dùng link /copy 1 chạm!).",
        "2️⃣  Nhấn nút dấu ba chấm (...) góc trên bên phải → chọn Thêm vào màn hình chính (Add to Home Screen) trên Android hoặc dùng Phím tắt (Shortcuts) trên iPhone để mở 1 chạm như App!",
        "3️⃣  Giữ điện thoại theo chiều DỌC (Portrait) — toàn bộ 7 ngày T2–CN, hoạt ảnh, biểu đồ & ghi chú vừa khít 100% màn hình, không cần xoay ngang!",
    ])
    rg = mob_card(rg, "⚡  2. BẬT CHECKBOX & TỰ LƯU TUẦN / THÁNG (1-CLICK SCRIPT)", [
        "☑️  Cách nhanh nhất (1 giây trên máy tính, dùng mãi trên điện thoại): Mở file trên trình duyệt → Tiện ích mở rộng (Extensions) → Apps Script → dán file google_sheets_1click_setup.gs → Run setupHabitTracker()!",
        "✨  Sau khi chạy 1 lần: toàn bộ ô TRUE/FALSE biến thành Checkbox màu Pastel VÀ tự động kích hoạt onEdit(e) 0ms — đổi Tuần 1 → Tuần 2 → Tuần 3 hoặc đổi Tháng tự lưu tuần cũ & nạp tuần mới vào _Database!",
        "🖐️  Cách thủ công không cần Script (3 giây): Chọn vùng ô C21:I35 trên tab Tuần Này → menu Chèn (Insert) → Hộp kiểm (Checkbox).",
    ])

    # Card 3: Stage Showcase + Editable Thresholds (6, 7, or 8 stages — cached via _Assets!)
    cv3.row(rg, 28)
    is_7 = (t.num_stages == 7)
    is_8 = (t.num_stages == 8)
    is_digi = (t.num_stages >= 7)
    cv3.merge(rg, 1, rg, 6,
              "⚡  3. TIẾN HÓA 8 GIAI ĐOẠN (ULTRA DIGIVOLUTION)" if is_8 else (
                  "⚡  3. TIẾN HÓA 7 GIAI ĐOẠN (DIGIVOLUTION) & NGƯỠNG" if is_7 else
                  "🎨  3. HOẠT ẢNH 6 GIAI ĐOẠN (2×3) & NGƯỠNG TĂNG TRƯỞNG"
              ),
              bold=True, font_size=11, align="left", indent=1, bg_color=t.primary, font_color=t.on_primary)

    # Clean tip row explaining hidden _Assets sprite cache (zero tiny raw URL wrapping!)
    r_url = rg + 1
    cv3.row(r_url, 40)
    cv3.merge(r_url, 1, r_url, 6,
              f"💡 Muốn tự đổi ảnh? Mở sheet ẩn _Assets (Xem → Trang tính ẩn) & sửa {t.num_stages} ô =IMAGE() tại B2:B{1 + t.num_stages} — toàn bộ app tự đồng bộ siêu tốc!",
              bold=False, font_size=10, align="left", indent=1, text_wrap=True,
              bg_color=t.warn_fill, font_color=t.ink)

    # Centered Threshold bar
    r_th = r_url + 1
    if is_8:
        for dr in range(3):
            cv3.row(r_th + dr, 26)
        cv3.merge(r_th, 1, r_th, 2, "S2 (Baby II):", bold=True, font_size=10, align="center", bg_color=t.soft, font_color=t.ink)
        cv3.put(r_th, 3, 0.15, bold=True, font_size=10, align="center", num_format="0%", bg_color=t.warn_fill, font_color=t.primary_dark)
        cv3.merge(r_th, 4, r_th, 5, "S3 (Rookie):", bold=True, font_size=10, align="center", bg_color=t.soft, font_color=t.ink)
        cv3.put(r_th, 6, 0.30, bold=True, font_size=10, align="center", num_format="0%", bg_color=t.warn_fill, font_color=t.primary_dark)
        cv3.merge(r_th + 1, 1, r_th + 1, 2, "S4 (Champ):", bold=True, font_size=10, align="center", bg_color=t.soft, font_color=t.ink)
        cv3.put(r_th + 1, 3, 0.50, bold=True, font_size=10, align="center", num_format="0%", bg_color=t.warn_fill, font_color=t.primary_dark)
        cv3.merge(r_th + 1, 4, r_th + 1, 5, "S5 (Ultim):", bold=True, font_size=10, align="center", bg_color=t.soft, font_color=t.ink)
        cv3.put(r_th + 1, 6, 0.70, bold=True, font_size=10, align="center", num_format="0%", bg_color=t.warn_fill, font_color=t.primary_dark)
        cv3.merge(r_th + 2, 1, r_th + 2, 2, "S6 • Đạt:", bold=True, font_size=10, align="center", bg_color=t.soft, font_color=t.ink)
        cv3.put(r_th + 2, 3, 0.85, bold=True, font_size=10, align="center", num_format="0%", bg_color=t.warn_fill, font_color=t.primary_dark)
        cv3.merge(r_th + 2, 4, r_th + 2, 6, "S7 Ultra: 100% ✨", bold=True, font_size=10, align="center", bg_color=t.primary, font_color=t.on_primary)
        wb.define_name("CFG_THR_M1", f"={dq}!{acell(r_th, 3)}")
        wb.define_name("CFG_THR_0", f"={dq}!{acell(r_th, 6)}")
        wb.define_name("CFG_THR_1", f"={dq}!{acell(r_th + 1, 3)}")
        wb.define_name("CFG_THR_2", f"={dq}!{acell(r_th + 1, 6)}")
        wb.define_name("CFG_THR_3", f"={dq}!{acell(r_th + 2, 3)}")
        snames = t.stage_names or ["Digi-Egg", "Baby I", "Baby II", "Rookie", "Champion", "Ultimate", "Mega", "Ultra"]
        stages_2x3 = [
            [(0, f"S0 • {snames[0]} (0%)"), (1, f"S1 • {snames[1]} (1–14%)"), (2, f"S2 • {snames[2]} (15–29%)")],
            [(3, f"S3 • {snames[3]} (30–49%)"), (4, f"S4 • {snames[4]} (50–69%)"), (5, f"S5 • {snames[5]} (70–84%)")],
        ]
        r_cur = r_th + 3
    elif is_7:
        cv3.row(r_th, 26)
        cv3.row(r_th + 1, 26)
        cv3.merge(r_th, 1, r_th, 2, "Stage 2 (Baby II):", bold=True, font_size=10, align="center", bg_color=t.soft, font_color=t.ink)
        cv3.put(r_th, 3, 0.20, bold=True, font_size=10, align="center", num_format="0%", bg_color=t.warn_fill, font_color=t.primary_dark)
        cv3.merge(r_th, 4, r_th, 5, "Stage 3 (Rookie):", bold=True, font_size=10, align="center", bg_color=t.soft, font_color=t.ink)
        cv3.put(r_th, 6, 0.40, bold=True, font_size=10, align="center", num_format="0%", bg_color=t.warn_fill, font_color=t.primary_dark)
        cv3.merge(r_th + 1, 1, r_th + 1, 2, "Stage 4 (Champ):", bold=True, font_size=10, align="center", bg_color=t.soft, font_color=t.ink)
        cv3.put(r_th + 1, 3, 0.60, bold=True, font_size=10, align="center", num_format="0%", bg_color=t.warn_fill, font_color=t.primary_dark)
        cv3.merge(r_th + 1, 4, r_th + 1, 5, "Stage 5 • Đạt:", bold=True, font_size=10, align="center", bg_color=t.soft, font_color=t.ink)
        cv3.put(r_th + 1, 6, 0.80, bold=True, font_size=10, align="center", num_format="0%", bg_color=t.warn_fill, font_color=t.primary_dark)
        wb.define_name("CFG_THR_0", f"={dq}!{acell(r_th, 3)}")
        wb.define_name("CFG_THR_1", f"={dq}!{acell(r_th, 6)}")
        wb.define_name("CFG_THR_2", f"={dq}!{acell(r_th + 1, 3)}")
        wb.define_name("CFG_THR_3", f"={dq}!{acell(r_th + 1, 6)}")
        snames = t.stage_names or ["Digi-Egg", "Baby I", "Baby II", "Rookie", "Champion", "Ultimate", "Mega"]
        stages_2x3 = [
            [(0, f"S0 • {snames[0]} (0%)"), (1, f"S1 • {snames[1]} (1–19%)"), (2, f"S2 • {snames[2]} (20–39%)")],
            [(3, f"S3 • {snames[3]} (40–59%)"), (4, f"S4 • {snames[4]} (60–79%)"), (5, f"S5 • {snames[5]} (80–99%)")],
        ]
        r_cur = r_th + 2
    else:
        cv3.row(r_th, 28)
        cv3.put(r_th, 1, "Stage 2:", bold=True, font_size=10, align="center", bg_color=t.soft, font_color=t.ink)
        cv3.put(r_th, 2, 0.25, bold=True, font_size=10, align="center", num_format="0%", bg_color=t.warn_fill, font_color=t.primary_dark)
        cv3.put(r_th, 3, "Stage 3:", bold=True, font_size=10, align="center", bg_color=t.soft, font_color=t.ink)
        cv3.put(r_th, 4, 0.50, bold=True, font_size=10, align="center", num_format="0%", bg_color=t.warn_fill, font_color=t.primary_dark)
        cv3.put(r_th, 5, "Đạt:", bold=True, font_size=10, align="center", bg_color=t.soft, font_color=t.ink)
        cv3.put(r_th, 6, 0.75, bold=True, font_size=10, align="center", num_format="0%", bg_color=t.warn_fill, font_color=t.primary_dark)
        wb.define_name("CFG_THR_1", f"={dq}!{acell(r_th, 2)}")
        wb.define_name("CFG_THR_2", f"={dq}!{acell(r_th, 4)}")
        wb.define_name("CFG_THR_3", f"={dq}!{acell(r_th, 6)}")
        stages_2x3 = [
            [(0, "Stage 0 • 0%"), (1, "Stage 1 • 1–24%"), (2, "Stage 2 • 25–49%")],
            [(3, "Stage 3 • 50–74%"), (4, "Stage 4 • 75–99%"), (5, "Stage 5 • 100% ✨")],
        ]
        r_cur = r_th + 1
    for grp in stages_2x3:
        cv3.row(r_cur, 28 if is_digi else 24)
        cv3.row(r_cur + 1, 86)
        for bi, (s_idx, s_lbl) in enumerate(grp):
            c1, c2 = 1 + bi * 2, 2 + bi * 2
            cv3.merge(r_cur, c1, r_cur, c2, s_lbl, bold=True, font_size=10, align="center",
                      text_wrap=True, bg_color=t.soft, font_color=t.ink)
            cv3.merge(r_cur + 1, c1, r_cur + 1, c2,
                      f"=_Assets!$B${2 + s_idx}",
                      align="center", bg_color=t.card)
        r_cur += 2
    if is_8:
        snames = t.stage_names or ["Digi-Egg", "Baby I", "Baby II", "Rookie", "Champion", "Ultimate", "Mega", "Ultra"]
        cv3.row(r_cur, 28)
        cv3.row(r_cur + 1, 96)
        cv3.merge(r_cur, 1, r_cur, 3, f"🔥 S6 MEGA • {snames[6]} (85–99%)",
                  bold=True, font_size=10, align="center", text_wrap=True, bg_color=t.soft, font_color=t.primary_dark)
        cv3.merge(r_cur + 1, 1, r_cur + 1, 3, "=_Assets!$B$8",
                  align="center", bg_color=t.card)
        cv3.merge(r_cur, 4, r_cur, 6, f"👑 S7 ULTRA • {snames[7]} (100% ✨)",
                  bold=True, font_size=10, align="center", text_wrap=True, bg_color=t.primary, font_color=t.on_primary)
        cv3.merge(r_cur + 1, 4, r_cur + 1, 6, "=_Assets!$B$9",
                  align="center", bg_color=t.card)
        r_cur += 2
    elif is_7:
        snames = t.stage_names or ["Digi-Egg", "Baby I", "Baby II", "Rookie", "Champion", "Ultimate", "Mega"]
        cv3.row(r_cur, 28)
        cv3.row(r_cur + 1, 96)
        cv3.merge(r_cur, 1, r_cur, 6, f"⚡ Stage 6 MEGA • {snames[6]} (100% Tối Thượng ✨)",
                  bold=True, font_size=11, align="center", bg_color=t.primary, font_color=t.on_primary)
        cv3.merge(r_cur + 1, 1, r_cur + 1, 6, "=_Assets!$B$8",
                  align="center", bg_color=t.card)
        r_cur += 2
    cv3.grid(r_url, 1, r_cur - 1, 6, t.line)
    cv3.box(rg, 1, r_cur - 1, 6, t.line)

    # Footer
    cv3.row(r_cur, 10)
    cv3.row(r_cur + 1, 28)
    cv3.row(r_cur + 2, 10)
    cv3.merge(r_cur + 1, 1, r_cur + 1, 6,
              "💛  Habit Tracker Mobile Portrait v4.0 by Dyu  •  github.com/Thitrongdan202",
              bold=False, font_size=10, italic=True, align="center", text_wrap=True,
              bg_color=t.page, font_color=t.muted)

    _finish_mobile_sheet(ws_gd, cv3, t.primary, zoom=100)

    # =========================================================================
    #  HIDDEN `_Database` SHEET (WeeklyRaw + WeeklySummary + YearlyGoals!)
    # =========================================================================
    ws_db.hide_gridlines(2)
    hdr_f = wb.add_format({"font_name": t.font, "font_size": 10, "bold": True,
                           "bg_color": t.primary, "font_color": t.on_primary, "align": "center"})

    # Table 1: WeeklyRaw A:J (10 cols: WeekKey, RowIdx, HabitName, T2..CN)
    for c, h in enumerate(["WeekKey", "RowIdx", "HabitName"] + DAYS_VI):
        ws_db.write(0, c, h, hdr_f)
    for hi in range(N_MOB_HABITS):
        rr = 1 + hi
        h = habits[hi] if hi < len(habits) else None
        ws_db.write(rr, 0, week_key)
        ws_db.write_number(rr, 1, hi + 1)
        ws_db.write(rr, 2, h.name if h else "")
        for dow in range(7):
            ws_db.write_boolean(rr, 3 + dow, bool(ticks_15[hi][dow]))

    # Table 2: WeeklySummary M:U (cols 12..20)
    for off, h in enumerate(["WeekKey", "Year", "Month", "WeekNum", "Completed", "Target",
                             "GrownDays", "PerfectDays", "BestStreak"]):
        ws_db.write(0, 12 + off, h, hdr_f)
    ws_sum = _compute_week_summary(habits, ticks_15, year, month_idx, week_num)
    ws_db.write(1, 12, ws_sum["key"])
    ws_db.write_number(1, 13, ws_sum["year"])
    ws_db.write_number(1, 14, ws_sum["month"])
    ws_db.write_number(1, 15, ws_sum["week"])
    ws_db.write_number(1, 16, ws_sum["completed"])
    ws_db.write_number(1, 17, ws_sum["target"])
    ws_db.write_number(1, 18, ws_sum["grown"])
    ws_db.write_number(1, 19, ws_sum["perfect"])
    ws_db.write_number(1, 20, ws_sum["best_streak"])

    # Table 3: YearlyGoalsRaw W:Z (cols 22..25)
    for off, h in enumerate(["YearKey", "RowIdx", "Done", "GoalText"]):
        ws_db.write(0, 22 + off, h, hdr_f)
    g_done = 0
    g_tot = 0
    for gi in range(N_MOB_GOALS):
        rr = 1 + gi
        ws_db.write_number(rr, 22, year)
        ws_db.write_number(rr, 23, gi + 1)
        if gi < len(MOBILE_GOALS_SAMPLE):
            chk, gtxt = MOBILE_GOALS_SAMPLE[gi]
            g_tot += 1
            if chk:
                g_done += 1
            ws_db.write_boolean(rr, 24, chk)
            ws_db.write(rr, 25, gtxt)
        else:
            ws_db.write_boolean(rr, 24, False)
            ws_db.write(rr, 25, "")

    # Table 4: YearlyGoalsSummary AB:AD (cols 27..29)
    for off, h in enumerate(["YearKey", "GoalsDone", "GoalsTotal"]):
        ws_db.write(0, 27 + off, h, hdr_f)
    ws_db.write_number(1, 27, year)
    ws_db.write_number(1, 28, g_done)
    ws_db.write_number(1, 29, g_tot)

    # Table 5: DailyTasksRaw AF:AK (cols 31..36) — seeded ONLY for 2026-10-21!
    for off, h in enumerate(["DateKey", "RowIdx", "Done", "TaskName", "Priority", "DailyHighlight"]):
        ws_db.write(0, 31 + off, h, hdr_f)
    for ti in range(15):
        rr = 1 + ti
        ws_db.write(rr, 31, DEFAULT_TASK_KEY)
        ws_db.write_number(rr, 32, ti + 1)
        if ti < len(DEFAULT_DAILY_TASKS):
            done, t_nm, _cat, prio, _note = DEFAULT_DAILY_TASKS[ti]
            ws_db.write_boolean(rr, 33, done)
            ws_db.write(rr, 34, t_nm)
            ws_db.write(rr, 35, prio)
        else:
            ws_db.write_boolean(rr, 33, False)
            ws_db.write(rr, 34, "")
            ws_db.write(rr, 35, "")
        ws_db.write(rr, 36, DEFAULT_DAILY_HIGHLIGHT if ti == 0 else "")

    ws_calc.hide()
    ws_db.hide()
    _add_mobile_assets_sheet(wb, styles)
    ws_wk.activate()
    wb.close()

    return {
        "stem": tdef.stem,
        "short_key": tdef.short_key,
        "slug": t.slug,
        "num_stages": t.num_stages,
        "out_path": str(out_path),
        "week_sheet": MOBILE_WEEK_SHEET,
        "tasks_sheet": MOBILE_TASKS_SHEET,
        "goals_sheet": MOBILE_GOALS_SHEET,
        "guide_sheet": MOBILE_GUIDE_SHEET,
        "week_capture_top": "A1:J37",
        "week_capture_bottom": f"A38:J{r_nt0 + 5}",
        "tasks_capture": "A1:J36",
        "goals_capture": f"A1:J{r_bc + 3}",
        "guide_capture": f"A1:H{r_cur + 3}",
    }
