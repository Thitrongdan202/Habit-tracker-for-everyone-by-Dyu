"""
hx.tracker — Version 2.0 universal monthly habit-tracker engine.

Architecture
------------
- Tier A (universal=True): 100% Excel 2016 / 2019 / 2021 / 365 compatible:
    * Zero `_xlfn.` functions (no IMAGE, XLOOKUP, LET, LAMBDA, SCAN)
    * Clean hidden `_Calc` sheet holds Month lookup, KPIs, Stage Index (1..7),
      20x31 running-streak matrix, and Donut chart helpers
    * Rows 1..12 x 31 days (372 cells): pure boolean cells formatted `;;;`
      ready for Form Control Checkboxes added by `excel_com_enhancer.py`
    * Rows 13..20 x 31 days (8 expansion rows): pre-wired `"✓"` dropdown cells
    * Row 9 (`C9:AG9`) + Hero Grown slot: clean card canvas ready for 31+1
      Excel Native Linked Pictures bound to `=INDEX(_Assets!$B$2:$B$8, _Calc!...)`
- Tier B (universal=False): Cloud / Google Sheets / Excel 365 lightweight edition
    * Uses `=_xlfn.IMAGE(CFG_IMG_BASE&"stage_"&...)` pointing to branch `version2`
    * Uses native cell checkboxes across all 20 rows
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
N_FORM_ROWS = 12               # Tier A Form Control Checkbox rows (12 x 31 = 372)

R_BAND0, R_BAND1 = 1, 6
R_IMG = 8                      # Excel row 9 (Linked Picture / IMAGE row)
R_DONE, R_NOT, R_PCT = 9, 10, 11   # Excel rows 10, 11, 12
R_WEEK, R_WD, R_DAY = 13, 14, 15   # Excel rows 14, 15, 16
R_H0 = 16                      # Excel row 17 (first habit row)
R_H1 = R_H0 + N_HABITS - 1     # Excel row 36 (20th habit row)
R_TOT = R_H1 + 1               # Excel row 37 (totals row)
R_EXTRA = R_TOT + 2            # Excel row 39 (first extra dashboard block row)

# ---- _Calc hidden sheet coordinates (0-based) ----------------------------- #
CALC_SHEET = "_Calc"
CALC_MONTH_COL = 0             # A1:A12 -> January..December
CALC_KPI_COL = 2               # C1:C13 -> KPIs
CALC_DONUT_COL = 4             # E1:E2  -> Overall Donut
CALC_WK_COL0 = 6               # G1:K5  -> Week 1..5 helpers
CALC_STAGE_ROW = 14            # Excel row 15, cols B..AF (1..31) -> Stage Index 1..7
CALC_RUN_ROW0 = 16             # Excel rows 17..36, cols B..AF (1..31) -> Streak runs
CALC_DONEN_COL = 32            # Col AG (32) -> numeric done per habit
CALC_GOALN_COL = 33            # Col AH (33) -> effective goal per habit

WEEKDAYS_SHORT = '"Mon","Tue","Wed","Thu","Fri","Sat","Sun"'
WEEKDAYS_LETTER = '"M","T","W","T","F","S","S"'


def day_col(k: int) -> int:          # k = 1..31
    return C_D0 + k - 1


def week_days(w: int):               # w = 0..4
    a = 7 * w + 1
    return list(range(a, min(a + 6, 31) + 1))


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
    universal: bool = True             # True = Tier A Offline, False = Tier B Cloud


@dataclass
class TrackerRefs:
    sheet: str
    q: str
    calc_q: str
    month_cell: str
    year_cell: str
    s: dict                             # KPI name -> fully-qualified `_Calc!$C$N` ref
    c_right_end: int
    right_cols: dict
    hero_icon_box: tuple                # (r1, c1, r2, c2) for Hero Grown Linked Picture

    def a(self, key):
        return self.s[key]


def _done_test(ref: str) -> str:
    return f'OR({ref}=TRUE,{ref}="{CHECK_ALT}")'


def build_tracker(wb, styles: Styles, cv: Canvas, spec: TrackerSpec) -> TrackerRefs:
    t = cv.t
    ws = cv.ws
    q = qs(spec.sheet)
    cq = qs(CALC_SHEET)

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
    for r in range(R_BAND0, R_BAND1 + 1):
        cv.row(r, 21)
    cv.row(R_BAND0, 19)
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

    # ------------------------------------------------------------------ _Calc sheet setup
    ws_calc = wb.add_worksheet(CALC_SHEET)
    ws_calc.hide_gridlines(2)
    for idx, m in enumerate(MONTHS_EN):
        ws_calc.write(idx, CALC_MONTH_COL, m)
    month_lookup_rng = f"{cq}!{rng(0, CALC_MONTH_COL, 11, CALC_MONTH_COL)}"

    kpi_keys = ["m", "y", "dim", "ref", "hc", "overall", "grown", "perfect",
                "tdone", "tgoal", "best", "avg", "bestcur"]
    kpi_labels = ["MonthNum", "Year", "DaysInMonth", "LastActiveDay", "HabitCount",
                  "Overall%", "GrownDays", "PerfectDays", "TotalDone", "TotalGoal",
                  "BestStreak", "AvgDaily%", "BestCurrent"]
    S = {}
    for idx, (k, lab) in enumerate(zip(kpi_keys, kpi_labels)):
        ws_calc.write(idx, CALC_KPI_COL - 1, lab)
        S[k] = f"{cq}!{acell(idx, CALC_KPI_COL)}"

    month_cell = acell(R_BAND0 + 1, C_NAME)       # $B$3
    year_cell = acell(R_BAND0 + 3, C_NAME)        # $B$5
    q_names = f"{q}!{rng(R_H0, C_NAME, R_H1, C_NAME)}"
    q_pct_row = f"{q}!{rng(R_PCT, C_D0, R_PCT, C_D31)}"
    q_done_row = f"{q}!{rng(R_DONE, C_D0, R_DONE, C_D31)}"
    q_day_row = f"{q}!{rng(R_DAY, C_D0, R_DAY, C_D31)}"

    def set_kpi(key, formula):
        idx = kpi_keys.index(key)
        ws_calc.write_formula(idx, CALC_KPI_COL, formula)

    set_kpi("m", f"=IFERROR(MATCH({q}!{month_cell},{month_lookup_rng},0),1)")
    set_kpi("y", f"=IFERROR(--{q}!{year_cell},YEAR(TODAY()))")
    set_kpi("dim", f"=DAY(EOMONTH(DATE({S['y']},{S['m']},1),0))")
    # LastActiveDay: last day with any completed habit (100% Excel 2007–365 universal!)
    set_kpi("ref", f"=IFERROR(LOOKUP(2,1/({q_done_row}>0),{q_day_row}),0)")
    set_kpi("hc", f'=COUNTIF({q_names},"?*")')
    set_kpi("tdone", f"=SUM({rng(R_H0, CALC_DONEN_COL, R_H1, CALC_DONEN_COL)})")
    set_kpi("tgoal", f"=SUM({rng(R_H0, CALC_GOALN_COL, R_H1, CALC_GOALN_COL)})")
    set_kpi("overall", f"=IFERROR(MIN(1,{S['tdone']}/{S['tgoal']}),0)")
    set_kpi("grown", f'=COUNTIF({q_pct_row},">="&CFG_THR_3)')
    set_kpi("perfect", f'=COUNTIF({q_pct_row},">=1")')
    set_kpi("best", f"=MAX(0,{q}!{rng(R_H0, rc['long'], R_H1, rc['long'])})")
    set_kpi("avg", f'=IFERROR(SUMIFS({q_pct_row},{q_day_row},"<="&{S["ref"]})/{S["ref"]},0)')
    set_kpi("bestcur", f"=MAX(0,{q}!{rng(R_H0, rc['cur'], R_H1, rc['cur'])})")

    # Stage index row on _Calc (Excel row 15, cols B..AF = Day 1..31) -> values 1..7
    ws_calc.write(CALC_STAGE_ROW, 0, "StageIdx(1-7)")
    for k in range(1, 32):
        c_tr = day_col(k)
        c_ca = k  # Col B (1) .. Col AF (31)
        dc = f"{q}!{acell(R_DAY, c_tr)}"
        pc = f"{q}!{acell(R_PCT, c_tr)}"
        ws_calc.write_formula(
            CALC_STAGE_ROW, c_ca,
            f'=IF({dc}="",7,1+({pc}>0)+({pc}>=CFG_THR_1)+({pc}>=CFG_THR_2)+({pc}>=CFG_THR_3)+({pc}>=1))'
        )

    # Overall Donut data on _Calc!E1:E2
    ws_calc.write_formula(0, CALC_DONUT_COL, f"={S['overall']}")
    ws_calc.write_formula(1, CALC_DONUT_COL, f"=1-{S['overall']}")

    # Weekly helpers on _Calc!G1:K5
    for w in range(5):
        days = week_days(w)
        c1, c2 = day_col(days[0]), day_col(days[-1])
        hc = CALC_WK_COL0 + w
        ws_calc.write_formula(0, hc, f"=SUM({q}!{rng(R_DONE, c1, R_DONE, c2)})")
        ws_calc.write_formula(1, hc, f'={S["hc"]}*COUNT({q}!{rng(R_DAY, c1, R_DAY, c2)})')
        ws_calc.write_formula(2, hc, f"=IFERROR({cell(0, hc)}/{cell(1, hc)},0)")
        ws_calc.write_formula(3, hc, f"=1-{cell(2, hc)}")
        ws_calc.write_formula(4, hc, f"={cell(1, hc)}-{cell(0, hc)}")

    # ------------------------------------------------------------------ title card
    cv.box(R_BAND0, C_NAME, R_BAND1, C_NAME, t.line, fill=t.card)
    cv.put(R_BAND0, C_NAME, f"{t.emoji}  {spec.label_tag}", bold=True, font_size=8.5, align="center",
           font_color=t.primary_dark, bg_color=t.card)
    cv.merge(R_BAND0 + 1, C_NAME, R_BAND0 + 2, C_NAME, spec.month, font_name=t.font_month,
             font_size=22, align="center", bg_color=t.card, font_color=t.ink, bold=t.font_month != "Segoe Script")
    cv.put(R_BAND0 + 3, C_NAME, spec.year, font_name=t.font_title, font_size=15, align="center",
           bg_color=t.card, font_color=t.ink, num_format="0", bold=True)
    cv.put(R_BAND0 + 4, C_NAME, f'="Tháng "&{S["m"]}&"/"&{S["y"]}&"  •  "&{S["dim"]}&" ngày"',
           font_size=9, align="center", bg_color=t.card, font_color=t.muted)
    cv.put(R_BAND0 + 5, C_NAME, "▼ chọn Tháng & Năm ở ô phía trên", italic=True, font_size=8,
           align="center", bg_color=t.card, font_color=t.muted)
    ws.data_validation(month_cell, {"validate": "list", "source": MONTHS_EN,
                                    "input_title": "Chọn tháng", "input_message": "Chọn tháng để lịch tự cập nhật"})
    ws.data_validation(year_cell, {"validate": "list", "source": [str(y) for y in range(2024, 2041)],
                                   "input_title": "Chọn năm", "input_message": "Chọn năm (2024–2040)"})

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
        d = donut(wb, f"={cq}!{rng(0, CALC_DONUT_COL, 1, CALC_DONUT_COL)}",
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
            # Tier A: pure white card cell — COM pastes Linked Picture bound to Anim_DayNN here!
            cv.put(R_IMG, c, "", bg_color=t.card, align="center")
        else:
            st_ref = f"{cq}!{acell(CALC_STAGE_ROW, k)}"
            cv.put(R_IMG, c, f'=IF({dc}="","",_xlfn.IMAGE(CFG_IMG_BASE&"stage_"&({st_ref}-1)&".png"))',
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

    # ------------------------------------------------------------------ grown hero card (mid right)
    cv.box(R_IMG, C_R0, R_PCT, C_RE, t.line, fill=t.card)
    split = C_R0 + 2
    cv.merge(R_IMG, C_R0, R_IMG, split, spec.grown_label, bold=True, font_size=8.5, align="center",
             text_wrap=True, bg_color=t.card, font_color=t.ink)
    hero_box = (R_IMG, split + 1, R_IMG, C_RE)
    if spec.universal:
        cv.merge(*hero_box, "", align="center", bg_color=t.card)
    else:
        cv.merge(*hero_box, '=_xlfn.IMAGE(CFG_IMG_BASE&"stage_5.png")', align="center", bg_color=t.card)
    cv.merge(R_DONE, C_R0, R_PCT, split, f"={S['grown']}", bold=True, font_size=26, align="center",
             bg_color=t.card, font_color=t.primary_dark, font_name=t.font_title)
    cv.merge(R_DONE, split + 1, R_PCT, C_RE,
             '="ngày đạt ≥ "&TEXT(CFG_THR_3,"0%")&CHAR(10)&"(trên "&' + S["dim"] + '&" ngày)"',
             font_size=8, align="center", text_wrap=True, bg_color=t.card, font_color=t.muted)

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
    rnd = random.Random(spec.seed)
    tick_grid = _sample_matrix_v2(rnd, spec.habits, active_days=22)
    for i in range(N_HABITS):
        r = R_H0 + i
        h = spec.habits[i] if i < len(spec.habits) else None
        X = r + 1
        cv.put(r, C_NAME, h.name if h else "", align="left", indent=1, bg_color=t.card,
               font_color=t.ink, font_size=9.5)
        ticks = tick_grid[i] if i < len(tick_grid) else [False] * 31
        for k in range(1, 32):
            c = day_col(k)
            w = (k - 1) // 7
            if spec.universal and i >= N_FORM_ROWS:
                # Rows 13..20 in Tier A: fast expansion rows with "✓" dropdown
                cv.put(r, c, "", align="center", font_size=11, bold=True,
                       font_color=t.week_check[w], bg_color=t.card)
            else:
                cv.checkbox(r, c, ticks[k - 1], align="center",
                            font_color=t.week_check[w], bg_color=t.card)

        # Running streak matrix on _Calc (cols B..AF = 1..31, row = r)
        for k in range(1, 32):
            tr_ref = f"{q}!{cell(r, day_col(k))}"
            prev = "0" if k == 1 else cell(r, k - 1)
            ws_calc.write_formula(r, k, f'=IF(AND({k}<={S["dim"]},{_done_test(tr_ref)}),{prev}+1,0)')

        run_calc = f"{cq}!$B{X}:$AF{X}"
        nm_q = f"{q}!${colname(C_NAME)}{X}"
        goal_q = f"{q}!${colname(rc['goal'])}{X}"
        ws_calc.write_formula(r, CALC_DONEN_COL, f'=IF({nm_q}="",0,COUNTIF($B{X}:$AF{X},">0"))')
        ws_calc.write_formula(r, CALC_GOALN_COL, f'=IF({nm_q}="",0,IF({goal_q}="",{S["dim"]},MIN({goal_q},{S["dim"]})))')

        nm = f"${colname(C_NAME)}{X}"
        dn = f"{cq}!$AG{X}"
        gn = f"{cq}!$AH{X}"
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

    # Subtle separator line between 12 checkbox rows and 8 quick-expand rows in Tier A
    if spec.universal:
        cv.hline(R_H0 + N_FORM_ROWS - 1, C_NAME, C_D31, t.primary, where="bottom")
        exp_rng = rng(R_H0 + N_FORM_ROWS, C_D0, R_H1, C_D31)
        ws.data_validation(exp_rng, {"validate": "list", "source": [CHECK_ALT],
                                     "input_title": "Dòng mở rộng nhanh (13–20)",
                                     "input_message": "Chọn ✓ để đánh dấu hoàn thành, hoặc copy 1 dòng Checkbox phía trên xuống!"})

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
        ws.conditional_format(a, {"type": "formula", "criteria": f'=OR({tl}=TRUE,{tl}="{CHECK_ALT}")',
                                  "format": wb.add_format({"bg_color": t.week_tint[w]})})
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

    ws_calc.hide()
    ws.hide_gridlines(2)
    ws.set_zoom(85)
    ws.freeze_panes(0, 2)
    ws.set_tab_color(t.primary)
    ws.set_landscape()
    ws.set_paper(9)
    ws.fit_to_pages(1, 0)
    ws.set_margins(0.3, 0.3, 0.4, 0.4)

    return TrackerRefs(sheet=spec.sheet, q=q, calc_q=cq, month_cell=month_cell, year_cell=year_cell,
                       s=S, c_right_end=C_RE, right_cols=rc, hero_icon_box=hero_box)


def _sample_matrix_v2(rnd: random.Random, habits: list, active_days: int = 22):
    """Pre-populate ~22 days of varied, inspiring habit data showcasing all 6 growth stages;
    Days 23..31 remain empty (stage 0) so the user can continue ticking right away!"""
    n = len(habits)
    if n == 0:
        return []
    # 22 active days with organic ups/downs covering stages 1..5 + 9 upcoming days (stage 0)
    wave22 = [
        1.00, 1.00, 0.88, 0.75, 0.62, 0.38, 0.75,   # Week 1: strong start + mid dip (stage 2)
        0.88, 1.00, 1.00, 0.88, 1.00, 0.75, 0.88,   # Week 2: full bloom momentum
        1.00, 0.50, 0.18, 0.62, 0.88, 1.00, 1.00,   # Week 3: realistic busy day (stage 1!) -> comeback
        1.00,                                        # Day 22: glowing bloom today!
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
