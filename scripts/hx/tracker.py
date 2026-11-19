"""
hx.tracker — Version 2.1 unified monthly habit-tracker engine.

Supports 3 clean editions from one single codebase:
  1. Pro Interactive (`.xlsm`, single tracker tab + hidden `_Database` + VBA persistence)
     - 100% offline Linked Pictures (`_Assets!B2:B8`) + Form Control Checkboxes
     - Dynamic 6-stage Monthly Hero (`Anim_MonthlyHero`) + 31 Daily Animations (`Anim_Day01..31`)
  2. Universal Offline No-Macro (`.xlsx`, 12 independent tabs `T01..T12` + `_YearHistory`)
     - 100% offline Linked Pictures + Form Control Checkboxes, ZERO macros, ZERO volatile formulas
     - Each month tab `m` uses a clean 40-row stride on shared hidden `_Calc` (`rb = (m - 1) * 40`)
  3. Google Sheets Edition (`.xlsx`, 12 independent tabs `T01..T12` + `_YearHistory`)
     - Dynamic `=_xlfn.IMAGE(CFG_IMG_BASE&"stage_"&(<stage>-1)&".png")` for every daily & hero sprite
     - Clean centered softly-tinted boolean cells ready for 1-click Insert->Checkbox / Apps Script
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field

from .core import (Canvas, Styles, Theme, MONTHS_EN, CHECK_ALT, acell, cell, colname,
                   qs, rng, donut, place_chart, axis_font)

# ---- fixed geometry (0-based) --------------------------------------------- #
C_NAME = 1
C_D0 = 2                       # Day 1 (Col C)
C_D31 = C_D0 + 30              # Day 31 (Col AG)
C_GAP = 33                     # Col AH
C_R0 = 34                      # Col AI (first right-side stat col)
N_HABITS = 20
N_FORM_ROWS = 12               # Pro single-tab Form Control Checkbox rows (12 x 31 = 372)
N_FORM_ROWS_12M = 10           # 12-Month Offline Form Control Checkbox rows (10 x 31 = 310/tab)

R_BAND0, R_BAND1 = 1, 6
R_IMG = 8                      # Excel row 9 (Linked Picture / IMAGE row)
R_DONE, R_NOT, R_PCT = 9, 10, 11   # Excel rows 10, 11, 12
R_WEEK, R_WD, R_DAY = 13, 14, 15   # Excel rows 14, 15, 16
R_H0 = 16                      # Excel row 17 (first habit row)
R_H1 = R_H0 + N_HABITS - 1     # Excel row 36 (20th habit row)
R_TOT = R_H1 + 1               # Excel row 37 (totals row)
R_EXTRA = R_TOT + 2            # Excel row 39 (first extra dashboard block row)

# ---- _Calc hidden sheet coordinates (0-based, 100% NON-OVERLAPPING!) ------- #
CALC_SHEET = "_Calc"
CALC_STRIDE = 40               # Row stride per monthly tracker block on _Calc
CALC_KPI_COL = 2               # Col C: rows rb+0..rb+12 = KPIs; rb+13 = HeroStageIdx!
CALC_HERO_ROW_OFF = 13         # Row rb+13, Col C -> Monthly Hero Stage Index (1..6)
CALC_DONUT_COL = 4             # Col E: rows rb+0..rb+1 -> Overall Donut
CALC_WK_COL0 = 6               # Cols G..K: rows rb+0..rb+4 -> Week 1..5 helpers
CALC_STAGE_ROW = 14            # Row rb+14, cols B..AF (1..31) -> Day 1..31 Stage Index (1..7)
CALC_RUN_ROW0 = 16             # Rows rb+16..rb+35, cols B..AF (1..31) -> Streak runs
CALC_DONEN_COL = 32            # Col AG (32) -> numeric done per habit
CALC_GOALN_COL = 33            # Col AH (33) -> effective goal per habit

# Global shared columns on _Calc (Cols AJ..AY = 35..50, NEVER touched by month blocks A..AH!)
CALC_MONTH_COL = 35            # AJ1:AJ12 -> January..December (locale-safe dropdown source!)
CALC_YEAR_COL = 36             # AK1:AK17 -> 2024..2040 (locale-safe dropdown source!)
CALC_CHK_COL = 37              # AL1      -> "✓" (locale-safe dropdown source!)
CALC_STATE_LBL_COL = 38        # AM1:AM12 -> Global state & hero stage labels
CALC_STATE_VAL_COL = 39        # AN1:AN12 -> Global state & hero stage values:
#   AN1 (row 0): ActiveTrackingYear (2026)
#   AN2 (row 1): LastLoadedKey ("2026-10") — Pro VBA
#   AN3 (row 2): LastGoalYear (2026)       — Pro VBA
#   AN4 (row 3): YearlyGoalsDone (live)
#   AN5 (row 4): YearlyGoalsTotal (live)
#   AN6 (row 5): YearlyGoalsPct (live)
#   AN7 (row 6): YearlyGoalsStageIdx (1..6 -> Anim_YearlyGoals)
#   AN8 (row 7): AnnualHeroStageIdx  (1..6 -> Anim_AnnualHero)
#   AN9 (row 8): AchBadgesStageIdx   (1..6 -> Anim_AchBadges)
#   AN10(row 9): AnnualDonutDone
#   AN11(row10): AnnualDonutRest

CALC_ANN_COL0 = 40             # AO..AW (40..48), rows 1..12 -> 12-Month Annual summary engine
#   AO(40): MonthNum (1..12)
#   AP(41): MonthKey ("YYYY-MM")
#   AQ(42): Completed
#   AR(43): TotalGoal
#   AS(44): OverallPct
#   AT(45): GrownDays (>=75%)
#   AU(46): PerfectDays (100%)
#   AV(47): BestStreak
#   AW(48): MonthlyStageIdx (1..6 -> Anim_AnnualM01..M12)
CALC_ANN_YG_LBL_COL = 49       # AX1:AX3 -> Annual selected-year YearlyGoals labels
CALC_ANN_YG_VAL_COL = 50       # AY1:AY3 -> Annual selected-year GoalsDone, GoalsTotal, GoalsPct

WEEKDAYS_SHORT = '"Mon","Tue","Wed","Thu","Fri","Sat","Sun"'
WEEKDAYS_LETTER = '"M","T","W","T","F","S","S"'


def day_col(k: int) -> int:          # k = 1..31
    return C_D0 + k - 1


def week_days(w: int):               # w = 0..4
    a = 7 * w + 1
    return list(range(a, min(a + 6, 31) + 1))


def stage6_formula(pct_ref: str) -> str:
    """Consistent 6-stage formula (returns 1..6 for stage_0..stage_5):
    0% -> 1, 1-24% -> 2, 25-49% -> 3, 50-74% -> 4, 75-99% -> 5, 100% -> 6."""
    return (f"=1+({pct_ref}>0)+({pct_ref}>=CFG_THR_1)+({pct_ref}>=CFG_THR_2)"
            f"+({pct_ref}>=CFG_THR_3)+({pct_ref}>=0.999)")


def init_calc_sheet(wb, active_year: int = 2026, last_loaded_key: str = "2026-10",
                    last_goal_year: int = 2026):
    """Create the shared hidden `_Calc` sheet with non-overlapping lookups & state cells."""
    ws_calc = wb.add_worksheet(CALC_SHEET)
    ws_calc.hide_gridlines(2)
    for idx, m in enumerate(MONTHS_EN):
        ws_calc.write(idx, CALC_MONTH_COL, m)
    for idx, yr in enumerate(range(2024, 2041)):
        ws_calc.write(idx, CALC_YEAR_COL, yr)
    ws_calc.write(0, CALC_CHK_COL, CHECK_ALT)

    state_init = [
        ("ActiveTrackingYear", active_year),
        ("LastLoadedKey", last_loaded_key),
        ("LastGoalYear", last_goal_year),
        ("YearlyGoalsDone", 0),
        ("YearlyGoalsTotal", 0),
        ("YearlyGoalsPct", 0),
        ("YearlyGoalsStageIdx", 1),
        ("AnnualHeroStageIdx", 1),
        ("AchBadgesStageIdx", 1),
        ("AnnualDonutDone", 0),
        ("AnnualDonutRest", 1),
    ]
    for r_idx, (lbl, val) in enumerate(state_init):
        ws_calc.write(r_idx, CALC_STATE_LBL_COL, lbl)
        ws_calc.write(r_idx, CALC_STATE_VAL_COL, val)
    return ws_calc


def month_lookup_ref() -> str:
    return f"{qs(CALC_SHEET)}!{rng(0, CALC_MONTH_COL, 11, CALC_MONTH_COL)}"


def year_lookup_ref() -> str:
    return f"{qs(CALC_SHEET)}!{rng(0, CALC_YEAR_COL, 16, CALC_YEAR_COL)}"


def chk_lookup_ref() -> str:
    return f"{qs(CALC_SHEET)}!{acell(0, CALC_CHK_COL)}"


@dataclass
class Habit:
    name: str
    goal: int | None = None
    p: float = 0.85
    extra: dict = field(default_factory=dict)


@dataclass
class TrackerSpec:
    sheet: str
    habits: list
    month: str = "October"
    year: int = 2026
    seed: int = 7
    label_tag: str = "HABIT TRACKER"
    garden_label: str = "YOUR GARDEN"
    grown_label: str = "THIS MONTH,\nYOU'VE GROWN:"
    habits_label: str = "DAILY HABITS"
    right_labels: tuple = ("GOAL", "DONE", "PROGRESS", "CURRENT\nSTREAK", "LONGEST\nSTREAK")
    right_widths: tuple = (6.4, 8.8, 10.8, 8.8, 8.8)
    extra_cols: list = field(default_factory=list)
    top_right: str = "donut"           # "donut" | "custom"
    day_width: float = 5.6
    name_width: float = 35
    img_row_height: float = 58
    habit_row_height: float = 23
    universal: bool = True             # True = Offline/Pro Linked Pictures + Form Checkboxes
    gsheets: bool = False              # True = Google Sheets =IMAGE() + clean styled boolean cells
    pro_mode: bool = False             # True = Pro .xlsm with VBA auto-save
    calc_slot: int = 0                 # 0 for unified 4-tab layout
    fixed_month: int | None = None     # None = editable Month/Year dropdown
    sample_mode: str = "oct"           # "oct" | "sep" | "empty"
    form_rows: int = N_FORM_ROWS       # Form Control checkbox rows when universal=True


@dataclass
class TrackerRefs:
    sheet: str
    q: str
    calc_q: str
    calc_row_base: int
    stage_row: int
    hero_stage_cell: str               # e.g. '_Calc'!$C$14
    month_cell: str
    year_cell: str
    s: dict                            # KPI name -> fully-qualified `_Calc!$C$N` ref
    c_right_end: int
    right_cols: dict
    hero_icon_box: tuple               # (r1, c1, r2, c2) for Monthly Hero Linked Picture
    ticks_2d: list = field(default_factory=list)

    def a(self, key):
        return self.s[key]


def _done_test(ref: str) -> str:
    return f'OR({ref}=TRUE,{ref}="{CHECK_ALT}")'


def build_tracker(wb, styles: Styles, cv: Canvas, spec: TrackerSpec, ws_calc=None) -> TrackerRefs:
    t = cv.t
    ws = cv.ws
    q = qs(spec.sheet)
    cq = qs(CALC_SHEET)
    rb = spec.calc_slot * CALC_STRIDE

    if ws_calc is None:
        ws_calc = init_calc_sheet(wb, active_year=spec.year,
                                  last_loaded_key=f"{spec.year}-{MONTHS_EN.index(spec.month) + 1:02d}",
                                  last_goal_year=spec.year)

    n_right = len(spec.right_labels) + len(spec.extra_cols)
    C_RE = C_R0 + n_right - 1
    rc = {"goal": C_R0, "done": C_R0 + 1, "progress": C_R0 + 2, "cur": C_R0 + 3, "long": C_R0 + 4}
    for i, ec in enumerate(spec.extra_cols):
        rc[ec["key"]] = C_R0 + 5 + i

    # ------------------------------------------------------------------ geometry
    cv.col(0, 2.4)
    cv.col(C_NAME, spec.name_width)
    cv.cols(C_D0, C_D31, spec.day_width)
    cv.col(C_GAP, 1.6)
    for i, w in enumerate(spec.right_widths):
        cv.col(C_R0 + i, w)
    for i, ec in enumerate(spec.extra_cols):
        cv.col(C_R0 + 5 + i, ec.get("width", 9))
    cv.col(C_RE + 1, 2.4)

    cv.row(0, 10)
    cv.row(R_BAND0, 19)
    cv.row(R_BAND0 + 1, 30)        # Dedicated UNMERGED Month cell (B3)
    cv.row(R_BAND0 + 2, 15)        # Helper cue label (B4)
    cv.row(R_BAND0 + 3, 24)        # Dedicated UNMERGED Year cell (B5)
    cv.row(R_BAND0 + 4, 18)        # Dynamic Tháng/Năm/Ngày summary (B6)
    cv.row(R_BAND0 + 5, 16)        # Auto-calendar / tip cue (B7)
    cv.row(7, 9)
    cv.row(R_IMG, spec.img_row_height)
    for r in (R_DONE, R_NOT, R_PCT):
        cv.row(r, 19)
    cv.row(12, 12)
    cv.row(R_WEEK, 22)
    cv.row(R_WD, 17)
    cv.row(R_DAY, 18)
    for r in range(R_H0, R_H1 + 1):
        cv.row(r, spec.habit_row_height)
    cv.row(R_TOT, 23)
    cv.row(R_TOT + 1, 14)

    # ------------------------------------------------------------------ _Calc block for this sheet
    month_lookup_rng = month_lookup_ref()
    year_lookup_rng = year_lookup_ref()
    chk_lookup_rng = chk_lookup_ref()

    kpi_keys = ["m", "y", "dim", "ref", "hc", "overall", "grown", "perfect",
                "tdone", "tgoal", "best", "avg", "bestcur"]
    kpi_labels = ["MonthNum", "Year", "DaysInMonth", "LastActiveDay", "HabitCount",
                  "Overall%", "GrownDays", "PerfectDays", "TotalDone", "TotalGoal",
                  "BestStreak", "AvgDaily%", "BestCurrent"]
    S = {}
    for idx, (k, lab) in enumerate(zip(kpi_keys, kpi_labels)):
        ws_calc.write(rb + idx, CALC_KPI_COL - 1, f"{spec.sheet}:{lab}")
        S[k] = f"{cq}!{acell(rb + idx, CALC_KPI_COL)}"

    month_cell = acell(R_BAND0 + 1, C_NAME)       # $B$3
    year_cell = acell(R_BAND0 + 3, C_NAME)        # $B$5
    q_names = f"{q}!{rng(R_H0, C_NAME, R_H1, C_NAME)}"
    q_pct_row = f"{q}!{rng(R_PCT, C_D0, R_PCT, C_D31)}"
    q_done_row = f"{q}!{rng(R_DONE, C_D0, R_DONE, C_D31)}"
    q_day_row = f"{q}!{rng(R_DAY, C_D0, R_DAY, C_D31)}"

    def set_kpi(key, formula):
        idx = kpi_keys.index(key)
        ws_calc.write_formula(rb + idx, CALC_KPI_COL, formula)

    if spec.fixed_month is not None:
        ws_calc.write_number(rb + 0, CALC_KPI_COL, spec.fixed_month)
    else:
        set_kpi("m", f"=IFERROR(MATCH({q}!{month_cell},{month_lookup_rng},0),1)")
    set_kpi("y", f"=IFERROR(--{q}!{year_cell},YEAR(TODAY()))")
    set_kpi("dim", f"=DAY(EOMONTH(DATE({S['y']},{S['m']},1),0))")
    set_kpi("ref", f"=IFERROR(LOOKUP(2,1/({q_done_row}>0),{q_day_row}),0)")
    set_kpi("hc", f'=COUNTIF({q_names},"?*")')
    set_kpi("tdone", f"=SUM({rng(rb + R_H0, CALC_DONEN_COL, rb + R_H1, CALC_DONEN_COL)})")
    set_kpi("tgoal", f"=SUM({rng(rb + R_H0, CALC_GOALN_COL, rb + R_H1, CALC_GOALN_COL)})")
    set_kpi("overall", f"=IFERROR(MIN(1,{S['tdone']}/{S['tgoal']}),0)")
    set_kpi("grown", f'=COUNTIF({q_pct_row},">="&CFG_THR_3)')
    set_kpi("perfect", f'=COUNTIF({q_pct_row},">=1")')
    set_kpi("best", f"=MAX(0,{q}!{rng(R_H0, rc['long'], R_H1, rc['long'])})")
    set_kpi("avg", f'=IFERROR(SUMIFS({q_pct_row},{q_day_row},"<="&{S["ref"]})/{S["ref"]},0)')
    set_kpi("bestcur", f"=MAX(0,{q}!{rng(R_H0, rc['cur'], R_H1, rc['cur'])})")

    # DYNAMIC Monthly Hero Stage Index (FIX 2: driven by real Overall Monthly %!)
    hero_stage_row = rb + CALC_HERO_ROW_OFF
    ws_calc.write(hero_stage_row, CALC_KPI_COL - 1, f"{spec.sheet}:HeroStageIdx")
    ws_calc.write_formula(hero_stage_row, CALC_KPI_COL, stage6_formula(S["overall"]))
    hero_stage_cell = f"{cq}!{acell(hero_stage_row, CALC_KPI_COL)}"

    # Daily Stage index row on _Calc (rb + 14, cols B..AF = Day 1..31) -> values 1..7
    stage_row = rb + CALC_STAGE_ROW
    ws_calc.write(stage_row, 0, f"{spec.sheet}:StageIdx(1-7)")
    for k in range(1, 32):
        c_tr = day_col(k)
        c_ca = k  # Col B (1) .. Col AF (31)
        dc = f"{q}!{acell(R_DAY, c_tr)}"
        pc = f"{q}!{acell(R_PCT, c_tr)}"
        ws_calc.write_formula(
            stage_row, c_ca,
            f'=IF({dc}="",7,1+({pc}>0)+({pc}>=CFG_THR_1)+({pc}>=CFG_THR_2)+({pc}>=CFG_THR_3)+({pc}>=0.999))'
        )

    # Overall Donut data on _Calc!E{rb+1}:E{rb+2}
    ws_calc.write_formula(rb + 0, CALC_DONUT_COL, f"={S['overall']}")
    ws_calc.write_formula(rb + 1, CALC_DONUT_COL, f"=1-{S['overall']}")

    # Weekly helpers on _Calc!G..K (rows rb+0..rb+4)
    for w in range(5):
        days = week_days(w)
        c1, c2 = day_col(days[0]), day_col(days[-1])
        hc = CALC_WK_COL0 + w
        ws_calc.write_formula(rb + 0, hc, f"=SUM({q}!{rng(R_DONE, c1, R_DONE, c2)})")
        ws_calc.write_formula(rb + 1, hc, f'={S["hc"]}*COUNT({q}!{rng(R_DAY, c1, R_DAY, c2)})')
        ws_calc.write_formula(rb + 2, hc, f"=IFERROR({cell(rb + 0, hc)}/{cell(rb + 1, hc)},0)")
        ws_calc.write_formula(rb + 3, hc, f"=1-{cell(rb + 2, hc)}")
        ws_calc.write_formula(rb + 4, hc, f"={cell(rb + 1, hc)}-{cell(rb + 0, hc)}")

    # ------------------------------------------------------------------ title card
    cv.box(R_BAND0, C_NAME, R_BAND1, C_NAME, t.line, fill=t.card)
    cv.put(R_BAND0, C_NAME, f"{t.emoji}  {spec.label_tag}", bold=True, font_size=8.5, align="center",
           font_color=t.primary_dark, bg_color=t.card)

    month_name_disp = MONTHS_EN[spec.fixed_month - 1] if spec.fixed_month else spec.month
    cv.put(R_BAND0 + 1, C_NAME, month_name_disp, font_name=t.font_title, font_size=16, bold=True,
           align="center", bg_color=t.soft, font_color=t.ink,
           top=1, top_color=t.primary, bottom=1, bottom_color=t.primary,
           left=1, left_color=t.primary, right=1, right_color=t.primary)

    if spec.fixed_month is not None:
        cv.put(R_BAND0 + 2, C_NAME, f"Tab Tháng {spec.fixed_month:02d} độc lập  •  Năm theo dõi:",
               italic=True, font_size=7.6, align="center", bg_color=t.card, font_color=t.muted)
        cv.put(R_BAND0 + 3, C_NAME, f"={cq}!{acell(0, CALC_STATE_VAL_COL)}", font_name=t.font_title,
               font_size=13.5, bold=True, align="center", bg_color=t.soft, font_color=t.ink,
               num_format="0", top=1, top_color=t.primary, bottom=1, bottom_color=t.primary,
               left=1, left_color=t.primary, right=1, right_color=t.primary)
        cv.put(R_BAND0 + 4, C_NAME, f'="Tháng "&{S["m"]}&"/"&{S["y"]}&"  •  "&{S["dim"]}&" ngày"',
               font_size=8.8, bold=True, align="center", bg_color=t.card, font_color=t.primary_dark)
        cue_txt = ("💡 GSheets: Chọn C17:AG36 → Chèn → Hộp kiểm"
                   if spec.gsheets else "✓ Dữ liệu lưu riêng từng tab T01–T12 (0ms)")
        cv.put(R_BAND0 + 5, C_NAME, cue_txt, italic=True, font_size=7.5,
               align="center", bg_color=t.card, font_color=t.muted)
    else:
        cv.put(R_BAND0 + 2, C_NAME, "▲ Tháng (Month)   •   ▼ Năm (Year)", italic=True, font_size=7.8,
               align="center", bg_color=t.card, font_color=t.muted)
        cv.put(R_BAND0 + 3, C_NAME, spec.year, font_name=t.font_title, font_size=13.5, bold=True,
               align="center", bg_color=t.soft, font_color=t.ink, num_format="0",
               top=1, top_color=t.primary, bottom=1, bottom_color=t.primary,
               left=1, left_color=t.primary, right=1, right_color=t.primary)
        cv.put(R_BAND0 + 4, C_NAME, f'="Tháng "&{S["m"]}&"/"&{S["y"]}&"  •  "&{S["dim"]}&" ngày"',
               font_size=8.8, bold=True, align="center", bg_color=t.card, font_color=t.primary_dark)
        cue_txt = (
            "⚡ Tự lưu & tải dữ liệu theo từng Tháng/Năm" if spec.pro_mode else (
                "💡 GSheets: Chạy Script 1-Click bật Checkbox & lưu 12 tháng" if spec.gsheets
                else "✓ Đổi Tháng/Năm động • Bản Offline không Macro"
            )
        )
        cv.put(R_BAND0 + 5, C_NAME, cue_txt, italic=True, font_size=7.4,
               align="center", bg_color=t.card, font_color=t.muted)
        ws.data_validation(month_cell, {"validate": "list", "source": f"={month_lookup_rng}",
                                        "input_title": "Chọn Tháng (Month)",
                                        "input_message": "Chọn tháng (January–December) → tự lưu tháng cũ & tải tháng mới!"})
        ws.data_validation(year_cell, {"validate": "list", "source": f"={year_lookup_rng}",
                                       "input_title": "Chọn Năm (Year)",
                                       "input_message": "Chọn năm (2024–2040) → tự lưu & tách biệt hoàn toàn từng năm!"})

    # ------------------------------------------------------------------ daily progress chart
    day_row = rng(R_DAY, C_D0, R_DAY, C_D31)
    pct_row = rng(R_PCT, C_D0, R_PCT, C_D31)
    ch = wb.add_chart({"type": "area"})
    ch.add_series({
        "name": "% Completed",
        "categories": f"={q}!{day_row}",
        "values": f"={q}!{pct_row}",
        "fill": {"color": t.chart_fill, "transparency": 45},
        "border": {"none": True},
    })
    ln = wb.add_chart({"type": "line"})
    line_series = {"name": "Trend", "categories": f"={q}!{day_row}", "values": f"={q}!{pct_row}",
                   "line": {"color": t.chart_line, "width": 1.75}}
    if t.chart_markers:
        line_series["marker"] = {"type": "circle", "size": 5, "fill": {"color": t.chart_line},
                                 "border": {"color": "#FFFFFF", "width": 0.75}}
    else:
        line_series["marker"] = {"type": "none"}
    ln.add_series(line_series)
    ch.combine(ln)
    ch.set_title({"name": t.chart_title, "name_font": {"name": t.font, "size": 9, "bold": True,
                                                       "color": t.ink}, "overlay": False})
    ch.set_y_axis({"min": 0, "max": 1, "major_unit": 0.25, "num_format": "0%",
                   "num_font": axis_font(t), "line": {"none": True},
                   "major_gridlines": {"visible": True, "line": {"color": t.line, "width": 0.5,
                                                                  "dash_type": "dash"}}})
    ch.set_x_axis({"num_font": axis_font(t, 7.5), "line": {"color": t.line},
                   "major_tick_mark": "none", "minor_tick_mark": "none", "position_axis": "on_tick"})
    ch.set_legend({"none": True})
    ch.set_chartarea({"border": {"color": t.line, "width": 0.75}, "fill": {"color": t.card}})
    ch.set_plotarea({"layout": {"x": 0.045, "y": 0.2, "width": 0.94, "height": 0.62}})
    place_chart(cv, ch, R_BAND0, C_D0, R_BAND1, C_D31)

    # ------------------------------------------------------------------ top-right card
    if spec.top_right == "donut":
        cv.box(R_BAND0, C_R0, R_BAND1, C_RE, t.line, fill=t.card)
        cv.merge(R_BAND0, C_R0, R_BAND0, C_RE, "MONTHLY PROGRESS", bold=True, font_size=8.5,
                 align="center", bg_color=t.soft, font_color=t.ink)
        cd1 = C_R0 + 2
        cv.merge(R_BAND0 + 1, C_R0, R_BAND1, cd1, f"={S['overall']}", bold=True, font_size=15,
                 align="center", num_format="0%", bg_color=t.card, font_name=t.font_title,
                 font_color=t.primary_dark)
        d = donut(wb, f"={cq}!{rng(rb + 0, CALC_DONUT_COL, rb + 1, CALC_DONUT_COL)}",
                  [t.primary, t.donut_rest], hole=70)
        place_chart(cv, d, R_BAND0 + 1, C_R0, R_BAND1, cd1, pad_y=2)
        kc = C_R0 + 3
        stats = [("CHECKS", f'={S["tdone"]}&" / "&{S["tgoal"]}'),
                 ("PERFECT DAYS", f"={S['perfect']}"),
                 ("BEST STREAK", f'="🔥 "&{S["best"]}&" ngày liên tiếp"')]
        for i, (lab, f) in enumerate(stats):
            if i < 2:
                rr = R_BAND0 + 1 + i * 2
                cv.merge(rr, kc, rr, C_RE, lab, font_size=7.5, bold=True, align="center",
                         font_color=t.muted, bg_color=t.card)
                cv.merge(rr + 1, kc, rr + 1, C_RE, f, font_size=12, bold=True, align="center",
                         font_color=t.ink, bg_color=t.card, font_name=t.font_title)
            else:
                cv.merge(R_BAND0 + 5, kc, R_BAND0 + 5, C_RE, f, font_size=8,
                         align="center", font_color=t.primary_dark, bg_color=t.card, bold=True)

    # ------------------------------------------------------------------ growth row
    cv.box(R_IMG, C_NAME, R_PCT, C_NAME, t.line, fill=t.card)
    cv.put(R_IMG, C_NAME, f"{t.emoji}  {spec.garden_label}", bold=True, font_size=11, align="center",
           bg_color=t.card, font_color=t.primary_dark, font_name=t.font_title)
    for r, lab in ((R_DONE, "COMPLETED  ✓"), (R_NOT, "NOT COMPLETED"), (R_PCT, "% COMPLETED")):
        cv.put(r, C_NAME, lab, align="right", font_size=8.5, bold=True, font_color=t.ink,
               bg_color=t.card, indent=1, top=1 if r == R_DONE else None, top_color=t.line)
    cv.hline(R_IMG, C_D0, C_D31, t.line, where="bottom")

    names_local = rng(R_H0, C_NAME, R_H1, C_NAME)
    for k in range(1, 32):
        c = day_col(k)
        w = (k - 1) // 7
        dc = cell(R_DAY, c, row_abs=True)
        if spec.universal:
            cv.put(R_IMG, c, "", bg_color=t.card, align="center")
        else:
            st_ref = f"{cq}!{acell(stage_row, k)}"
            cv.put(R_IMG, c, f'=IF({dc}="","",_xlfn.IMAGE(CFG_IMG_BASE&"stage_"&(MIN(6,MAX(1,{st_ref}))-1)&".png"))',
                   bg_color=t.card, align="center")
        col_rng = f"{colname(c)}${R_H0 + 1}:{colname(c)}${R_H1 + 1}"
        cv.put(R_DONE, c, f'=IF({dc}="","",COUNTIFS({names_local},"?*",{col_rng},TRUE)+'
                          f'COUNTIFS({names_local},"?*",{col_rng},"{CHECK_ALT}"))',
               align="center", font_size=9, bold=True, bg_color=t.week_tint[w], font_color=t.ink)
        cv.put(R_NOT, c, f'=IF({dc}="","",{S["hc"]}-{cell(R_DONE, c)})', align="center", font_size=9,
               bg_color=t.card, font_color=t.muted)
        cv.put(R_PCT, c, f'=IF({dc}="","",IFERROR({cell(R_DONE, c)}/{S["hc"]},0))', align="center",
               font_size=7.5, num_format="0%", bg_color=t.card, font_color=t.ink)
    cv.grid(R_DONE, C_D0, R_PCT, C_D31, t.line)
    cv.box(R_IMG, C_D0, R_PCT, C_D31, t.line)

    # ------------------------------------------------------------------ DYNAMIC grown hero card (FIX 2!)
    cv.box(R_IMG, C_R0, R_PCT, C_RE, t.line, fill=t.card)
    split = C_R0 + 2
    cv.merge(R_IMG, C_R0, R_IMG, split, spec.grown_label, bold=True, font_size=8.5, align="center",
             text_wrap=True, bg_color=t.card, font_color=t.ink)
    hero_box = (R_IMG, split + 1, R_IMG, C_RE)
    if spec.universal:
        # COM pastes DYNAMIC Linked Picture bound to Anim_MonthlyHero / Anim_Mnn_Hero here!
        cv.merge(*hero_box, "", align="center", bg_color=t.card)
    else:
        cv.merge(*hero_box,
                 f'=_xlfn.IMAGE(CFG_IMG_BASE&"stage_"&(MIN(6,MAX(1,{hero_stage_cell}))-1)&".png")',
                 align="center", bg_color=t.card)
    cv.merge(R_DONE, C_R0, R_PCT, split, f"={S['grown']}", bold=True, font_size=26, align="center",
             bg_color=t.card, font_color=t.primary_dark, font_name=t.font_title)
    cv.merge(R_DONE, split + 1, R_PCT, C_RE,
             '="ngày ≥"&TEXT(CFG_THR_3,"0%")&CHAR(10)&"Tháng: "&TEXT(' + S["overall"] + ',"0%")',
             font_size=8.2, bold=True, align="center", text_wrap=True, bg_color=t.card, font_color=t.muted)

    # ------------------------------------------------------------------ week band / headers
    cv.merge(R_WEEK, C_NAME, R_WD, C_NAME, f"{spec.habits_label}", bold=True, font_size=11,
             align="left", indent=1, bg_color=t.primary, font_color=t.on_primary, font_name=t.font_title)
    cv.put(R_DAY, C_NAME, f'="Thói quen: "&{S["hc"]}&"   •   Ngày: "&{S["dim"]}', font_size=8.5,
           align="left", indent=1, bg_color=t.soft, font_color=t.ink)
    wd_list = WEEKDAYS_LETTER if t.weekday_style == "letter" else WEEKDAYS_SHORT
    for w in range(5):
        days = week_days(w)
        c1, c2 = day_col(days[0]), day_col(days[-1])
        cv.merge(R_WEEK, c1, R_WEEK, c2, f"WEEK {w + 1}", bold=True, font_size=9, align="center",
                 bg_color=t.week_head[w], font_color=t.week_on[w])
        for k in days:
            c = day_col(k)
            cv.put(R_WD, c, f'=IF({k}<={S["dim"]},CHOOSE(WEEKDAY(DATE({S["y"]},{S["m"]},{k}),2),{wd_list}),"")',
                   align="center", font_size=7.5, bg_color=t.week_tint[w], font_color=t.ink)
            cv.put(R_DAY, c, f'=IF({k}<={S["dim"]},{k},"")', align="center", font_size=8.5, bold=True,
                   bg_color=t.week_tint[w], font_color=t.ink)
        cv.vline(c2, R_WEEK, R_TOT, t.line, where="right")

    all_right = list(spec.right_labels) + [ec["label"] for ec in spec.extra_cols]
    for i, lab in enumerate(all_right):
        c = C_R0 + i
        cv.merge(R_WEEK, c, R_DAY, c, lab, bold=True, font_size=7.5, align="center", text_wrap=True,
                 bg_color=t.primary, font_color=t.on_primary)
    for c in range(C_R0, C_RE + 1):
        cv.vline(c, R_WEEK, R_DAY, t.card, where="right")

    # ------------------------------------------------------------------ habit rows
    rnd = random.Random(spec.seed + (100 if spec.sample_mode == "sep" else 0))
    if spec.sample_mode == "oct":
        tick_grid = _sample_matrix_v2(rnd, spec.habits, mode="oct")
    elif spec.sample_mode == "sep":
        tick_grid = _sample_matrix_v2(rnd, spec.habits, mode="sep")
    else:
        tick_grid = [[False] * 31 for _ in range(len(spec.habits))]

    full_ticks_20 = [tick_grid[i] if i < len(tick_grid) else [False] * 31 for i in range(N_HABITS)]

    for i in range(N_HABITS):
        r = R_H0 + i
        h = spec.habits[i] if i < len(spec.habits) else None
        X = r + 1
        r_calc = rb + r
        X_calc = r_calc + 1
        cv.put(r, C_NAME, h.name if h else "", align="left", indent=1, bg_color=t.card,
               font_color=t.ink, font_size=9.5)
        ticks = full_ticks_20[i]
        for k in range(1, 32):
            c = day_col(k)
            w = (k - 1) // 7
            if spec.universal and i >= spec.form_rows:
                cv.put(r, c, "", align="center", font_size=11, bold=True,
                       font_color=t.week_check[w], bg_color=t.card)
            else:
                cv.checkbox(r, c, ticks[k - 1], align="center",
                            font_color=t.week_check[w], bg_color=t.card)

        # Running streak matrix on _Calc (cols B..AF = 1..31, row = r_calc)
        for k in range(1, 32):
            tr_ref = f"{q}!{cell(r, day_col(k))}"
            prev = "0" if k == 1 else cell(r_calc, k - 1)
            ws_calc.write_formula(r_calc, k, f'=IF(AND({k}<={S["dim"]},{_done_test(tr_ref)}),{prev}+1,0)')

        run_calc = f"{cq}!$B{X_calc}:$AF{X_calc}"
        nm_q = f"{q}!${colname(C_NAME)}{X}"
        goal_q = f"{q}!${colname(rc['goal'])}{X}"
        ws_calc.write_formula(r_calc, CALC_DONEN_COL, f'=IF({nm_q}="",0,COUNTIF($B{X_calc}:$AF{X_calc},">0"))')
        ws_calc.write_formula(r_calc, CALC_GOALN_COL, f'=IF({nm_q}="",0,IF({goal_q}="",{S["dim"]},MIN({goal_q},{S["dim"]})))')

        nm = f"${colname(C_NAME)}{X}"
        dn = f"{cq}!$AG{X_calc}"
        gn = f"{cq}!$AH{X_calc}"
        cv.put(r, rc["goal"], h.goal if (h and h.goal) else "", align="center", font_color=t.muted,
               bg_color=t.card, font_size=9, num_format="0")
        cv.put(r, rc["done"], f'=IF({nm}="","",{dn}&" / "&{gn})', align="center", font_size=9,
               bg_color=t.card, font_color=t.ink)
        cv.put(r, rc["progress"], f'=IF({nm}="","",IFERROR(MIN(1,{dn}/{gn}),0))', align="center",
               font_size=8.5, num_format="0%", bg_color=t.card, font_color=t.ink, bold=True)
        ref_day = S["ref"]
        idx_f = lambda off: f"INDEX({run_calc},{ref_day}{off})"
        cv.put(r, rc["cur"], f'=IF({nm}="","",IFERROR(IF({ref_day}=0,0,IF({idx_f("")}>0,{idx_f("")},'
                             f'IF({ref_day}>1,{idx_f("-1")},0))),0))',
               align="center", font_size=10, bold=True, bg_color=t.card, font_color=t.ink, num_format="0")
        cv.put(r, rc["long"], f'=IF({nm}="","",MAX({run_calc}))', align="center", font_size=10, bold=True,
               bg_color=t.card, font_color=t.ink, num_format="0")
        for ec in spec.extra_cols:
            c = rc[ec["key"]]
            if ec["kind"] == "input":
                cv.put(r, c, h.extra.get(ec["key"], "") if h else ec.get("blank", ""), align="center",
                       font_size=9, bg_color=t.card, font_color=t.muted, num_format=ec.get("fmt", "General"))
            else:
                f = ec["formula"].format(r=X, nm=nm, dn=dn, gn=gn,
                                         **{k2: f"${colname(v)}{X}" for k2, v in rc.items()})
                cv.put(r, c, f, align="center", font_size=9.5, bold=True, bg_color=t.card, font_color=t.ink,
                       num_format=ec.get("fmt", "General"))

    cv.grid(R_H0, C_NAME, R_H1, C_D31, t.line)
    cv.grid(R_H0, C_R0, R_H1, C_RE, t.line)
    for k in (7, 14, 21, 28):
        cv.vline(day_col(k), R_H0, R_H1, t.week_head[(k - 1) // 7], where="right")

    if spec.universal:
        cv.hline(R_H0 + spec.form_rows - 1, C_NAME, C_D31, t.primary, where="bottom")
        exp_rng = rng(R_H0 + spec.form_rows, C_D0, R_H1, C_D31)
        ws.data_validation(exp_rng, {"validate": "list", "source": f"={chk_lookup_rng}",
                                     "input_title": f"Dòng mở rộng nhanh ({spec.form_rows + 1}–20)",
                                     "input_message": "Chọn ✓ để đánh dấu hoàn thành!"})

    # totals row
    cv.put(R_TOT, C_NAME, "TOTAL  •  TỔNG KẾT", bold=True, font_size=9, align="left", indent=1,
           bg_color=t.soft, font_color=t.ink)
    for k in range(1, 32):
        c = day_col(k)
        cv.put(R_TOT, c, f'=IF({cell(R_DAY, c, row_abs=True)}="","",{cell(R_DONE, c)})', align="center",
               font_size=8, bg_color=t.soft, font_color=t.muted)
    cv.put(R_TOT, rc["goal"], f"={S['tgoal']}", align="center", bold=True, font_size=9, bg_color=t.soft)
    cv.put(R_TOT, rc["done"], f'={S["tdone"]}&" / "&{S["tgoal"]}', align="center", bold=True, font_size=9,
           bg_color=t.soft)
    cv.put(R_TOT, rc["progress"], f"={S['overall']}", align="center", bold=True, font_size=9,
           bg_color=t.soft, num_format="0%")
    cv.put(R_TOT, rc["cur"], f"={S['bestcur']}", align="center", bold=True, font_size=9, bg_color=t.soft)
    cv.put(R_TOT, rc["long"], f"={S['best']}", align="center", bold=True, font_size=9, bg_color=t.soft)
    for ec in spec.extra_cols:
        if ec.get("total"):
            cv.put(R_TOT, rc[ec["key"]], ec["total"].format(r1=R_H0 + 1, r2=R_H1 + 1,
                                                            col=colname(rc[ec["key"]])),
                   align="center", bold=True, font_size=9, bg_color=t.soft, num_format=ec.get("fmt", "General"))
        else:
            cv.put(R_TOT, rc[ec["key"]], "", bg_color=t.soft)
    cv.hline(R_TOT, C_NAME, C_D31, t.primary, where="top")
    cv.hline(R_TOT, C_R0, C_RE, t.primary, where="top")
    cv.box(R_WEEK, C_NAME, R_TOT, C_D31, t.line)
    cv.box(R_WEEK, C_R0, R_TOT, C_RE, t.line)

    # ------------------------------------------------------------------ conditional formats
    body = rng(R_H0, C_D0, R_H1, C_D31, absolute=False)
    day_hdr = f"{colname(C_D0)}${R_DAY + 1}"
    ws.conditional_format(body, {"type": "formula", "criteria": f'={day_hdr}=""',
                                 "format": wb.add_format({"bg_color": t.page, "font_color": t.page}),
                                 "stop_if_true": True})
    for w in range(5):
        days = week_days(w)
        a = rng(R_H0, day_col(days[0]), R_H1, day_col(days[-1]), absolute=False)
        tl = cell(R_H0, day_col(days[0]))
        cf_props = {"bg_color": t.week_tint[w]}
        if spec.gsheets:
            cf_props["font_color"] = t.week_check[w]
            cf_props["bold"] = True
        ws.conditional_format(a, {"type": "formula", "criteria": f'=OR({tl}=TRUE,{tl}="{CHECK_ALT}")',
                                  "format": wb.add_format(cf_props)})
    for r in (R_WD, R_DAY, R_DONE, R_NOT, R_PCT, R_TOT):
        ws.conditional_format(rng(r, C_D0, r, C_D31, absolute=False),
                              {"type": "formula", "criteria": f'={colname(C_D0)}${R_DAY + 1}=""',
                               "format": wb.add_format({"bg_color": t.page}), "stop_if_true": True})
    ws.conditional_format(pct_row, {"type": "3_color_scale", "min_type": "num", "min_value": 0,
                                    "mid_type": "num", "mid_value": 0.5, "max_type": "num", "max_value": 1,
                                    "min_color": "#FFFFFF", "mid_color": t.week_tint[0], "max_color": t.bar})
    prog = rng(R_H0, rc["progress"], R_H1, rc["progress"])
    ws.conditional_format(prog, {"type": "data_bar", "bar_color": t.bar, "bar_solid": True,
                                 "min_type": "num", "min_value": 0, "max_type": "num", "max_value": 1,
                                 "bar_border_color": t.bar})
    streak = rng(R_H0, rc["cur"], R_H1, rc["long"])
    ws.conditional_format(streak, {"type": "3_color_scale", "min_type": "num", "min_value": 0,
                                   "mid_type": "num", "mid_value": 10, "max_type": "num", "max_value": 25,
                                   "min_color": t.streak_lo, "mid_color": t.streak_mid,
                                   "max_color": t.streak_hi})
    ws.conditional_format(streak, {"type": "cell", "criteria": ">=", "value": 16,
                                   "format": wb.add_format({"font_color": "#FFFFFF", "bold": True})})
    ws.data_validation(rng(R_H0, rc["goal"], R_H1, rc["goal"]),
                       {"validate": "integer", "criteria": "between", "minimum": 0, "maximum": 31,
                        "input_title": "Mục tiêu (ngày)", "input_message": "Số ngày muốn hoàn thành trong tháng. Bỏ trống = cả tháng.",
                        "error_title": "Mục tiêu không hợp lệ", "error_message": "Nhập số từ 0 đến 31."})
    ws.data_validation(rng(R_H0, C_NAME, R_H1, C_NAME),
                       {"validate": "any", "input_title": "Tên thói quen",
                        "input_message": "Gõ tên thói quen mới — công thức, checkbox & streak đã được nối sẵn!"})

    ws.hide_gridlines(2)
    ws.set_zoom(85)
    ws.freeze_panes(0, 2)
    ws.set_tab_color(t.primary)
    ws.set_landscape()
    ws.set_paper(9)
    ws.fit_to_pages(1, 0)
    ws.set_margins(0.3, 0.3, 0.4, 0.4)

    return TrackerRefs(sheet=spec.sheet, q=q, calc_q=cq, calc_row_base=rb, stage_row=stage_row,
                       hero_stage_cell=hero_stage_cell, month_cell=month_cell, year_cell=year_cell,
                       s=S, c_right_end=C_RE, right_cols=rc, hero_icon_box=hero_box,
                       ticks_2d=full_ticks_20)


def _sample_matrix_v2(rnd: random.Random, habits: list, mode: str = "oct"):
    """Pre-populate varied, inspiring habit data showcasing all 6 growth stages."""
    n = len(habits)
    if n == 0:
        return []
    if mode == "sep":
        # 26 active days in September (30 days total), ~74% monthly completion -> distinct from Oct!
        wave = [
            0.88, 1.00, 0.75, 0.88, 1.00, 0.62, 0.50,
            1.00, 1.00, 0.88, 0.75, 0.88, 1.00, 1.00,
            0.75, 0.88, 1.00, 0.62, 0.88, 1.00, 1.00,
            0.88, 0.75, 0.88, 1.00, 0.88, 0.0, 0.0, 0.0, 0.0, 0.0,
        ]
    else:
        # 22 active days in October (~65% monthly completion -> Monthly Hero shows living Stage 3/4, NOT frozen Stage 5!)
        wave22 = [
            1.00, 1.00, 0.88, 0.75, 0.62, 0.38, 0.75,
            0.88, 1.00, 1.00, 0.88, 1.00, 0.75, 0.88,
            1.00, 0.50, 0.18, 0.62, 0.88, 1.00, 1.00,
            1.00,
        ]
        shift = rnd.randint(0, 3)
        wave = wave22[:2] + wave22[2 + shift:20] + wave22[2:2 + shift] + wave22[20:]
        wave = wave + [0.0] * (31 - len(wave))

    order = sorted(range(n), key=lambda i: (-habits[i].p, rnd.random()))
    grid = [[False] * 31 for _ in range(n)]
    for d, ratio in enumerate(wave):
        if ratio <= 0:
            k = 0
        elif ratio >= 0.99:
            k = n
        else:
            k = max(1, min(n - 1, int(round(ratio * n))))
        scored = sorted(
            range(n),
            key=lambda i: (habits[i].p + rnd.uniform(-0.18, 0.18) + (0.18 if i == order[0] else 0)),
            reverse=True,
        )
        for idx in scored[:k]:
            grid[idx][d] = True
    return grid


def compute_month_summary_py(habits: list[Habit], ticks_20: list[list[bool]], year: int, month: int) -> dict:
    """Compute exact summary metrics matching Excel formulas (used to pre-seed _Database & _YearHistory)."""
    import calendar
    dim = calendar.monthrange(year, month)[1]
    n_active = len(habits)
    total_done = 0
    total_goal = 0
    best_streak = 0
    for i, h in enumerate(habits):
        row = ticks_20[i]
        eff_goal = min(h.goal, dim) if h.goal else dim
        total_goal += eff_goal
        run = 0
        for d in range(dim):
            if row[d]:
                total_done += 1
                run += 1
                if run > best_streak:
                    best_streak = run
            else:
                run = 0
    grown_days = 0
    perfect_days = 0
    if n_active > 0:
        for d in range(dim):
            done_d = sum(1 for i in range(n_active) if ticks_20[i][d])
            pct_d = done_d / n_active
            if pct_d >= 0.75:
                grown_days += 1
            if pct_d >= 0.999:
                perfect_days += 1
    overall = min(1.0, total_done / total_goal) if total_goal > 0 else 0.0
    return {
        "key": f"{year:04d}-{month:02d}",
        "year": year, "month": month,
        "completed": total_done, "total_goal": total_goal,
        "overall": overall, "grown_days": grown_days,
        "perfect_days": perfect_days, "best_streak": best_streak,
    }
