"""
hx.tracker — the monthly habit-tracker engine shared by all 6 templates.

Layout (0-based rows / cols)
----------------------------
cols: 0 gutter | 1 habit names | 2..32 day 1..31 | 33 gap | 34.. right stats | ... | 57+ hidden helpers
rows: 1-6 header band (title card, DAILY PROGRESS chart, MONTHLY PROGRESS card)
      8 growth-animation row (=IMAGE per day), 9-11 completed / not completed / %,
      13-15 week band + weekday + day number, 16-35 twenty habit rows, 36 totals.
Every habit row carries its own hidden run-length helper (cols 60-90) so that
"Insert copied row" keeps streak formulas intact.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field

from .core import (Canvas, Theme, MONTH_ARRAY, MONTHS_EN, CHECK_ALT, acell, cell, colname, rng,
                   donut, place_chart, axis_font)

# ---- fixed geometry ------------------------------------------------------- #
C_NAME = 1
C_D0 = 2                       # day 1
C_D31 = C_D0 + 30              # day 31 (col 32 = AG)
C_GAP = 33
C_R0 = 34                      # first right-side stat column
N_HABITS = 20

R_BAND0, R_BAND1 = 1, 6
R_IMG = 8
R_DONE, R_NOT, R_PCT = 9, 10, 11
R_WEEK, R_WD, R_DAY = 13, 14, 15
R_H0 = 16
R_H1 = R_H0 + N_HABITS - 1     # 35
R_TOT = R_H1 + 1               # 36
R_EXTRA = R_TOT + 2            # 38 first free row for template extras

# hidden helper zone
C_HLAB, C_HVAL = 58, 59
C_RUN0 = 60                    # run-length day 1 .. day 31 => 60..90
C_DONEN = 91                   # numeric done count per habit
C_GOALN = 92                   # effective goal per habit
C_DON = 93                     # overall donut data
C_WK0 = 94                     # weekly helper cols 94..98
C_HID0, C_HID1 = 57, 110

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
    p: float = 0.85                  # sample completion probability
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
    garden_sub: str = "Mỗi ngày hoàn thành = một bông hoa"
    grown_label: str = "THIS MONTH,\nYOU'VE GROWN"
    habits_label: str = "DAILY HABITS"
    right_labels: tuple = ("GOAL", "DONE", "PROGRESS", "CURRENT\nSTREAK", "LONGEST\nSTREAK")
    right_widths: tuple = (6.2, 8.6, 10.5, 8.6, 8.6)
    extra_cols: list = field(default_factory=list)   # [{label,width,kind:'input'|'formula',fmt,...}]
    top_right: str = "donut"           # "donut" | "custom"
    day_width: float = 5.3
    name_width: float = 35
    img_row_height: float = 68
    habit_row_height: float = 23
    offline_sprites: bool = False      # True -> use =INDEX(_Sprites!$A$1:$A$6, stage+1)


@dataclass
class TrackerRefs:
    sheet: str
    q: str                              # quoted sheet name
    month_cell: str
    year_cell: str
    s: dict                             # settings name -> absolute address
    c_right_end: int
    right_cols: dict                    # 'goal','done','progress','cur','long', extra...

    def a(self, key):                   # sheet-qualified settings ref
        return f"{self.q}!{self.s[key]}"

    def col_range(self, c, r1=R_H0, r2=R_H1):
        return f"{self.q}!{rng(r1, c, r2, c)}"

    def row_range(self, r, c1=C_D0, c2=C_D31):
        return f"{self.q}!{rng(r, c1, r, c2)}"


def _done_test(ref: str) -> str:
    return f'OR({ref}=TRUE,{ref}="{CHECK_ALT}")'


def build_tracker(wb, cv: Canvas, spec: TrackerSpec) -> TrackerRefs:
    t = cv.t
    ws = cv.ws
    q = "'" + spec.sheet.replace("'", "''") + "'"

    n_right = len(spec.right_labels) + len(spec.extra_cols)
    C_RE = C_R0 + n_right - 1                # last right stat column
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
    for c in range(C_RE + 2, C_HID0):
        cv.col(c, 8.43)
    cv.cols(C_HID0, C_HID1, 6, hidden=True)

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

    # ------------------------------------------------------------------ settings (hidden)
    S = {}
    labels = ["MonthNum", "Year", "DaysInMonth", "RefDay", "HabitCount", "Overall%", "GrownDays",
              "PerfectDays", "TotalDone", "TotalGoal", "BestStreak", "AvgDaily%", "BestCurrent"]
    for i, lab in enumerate(labels):
        cv.put(1 + i, C_HLAB, lab, font_color="#999999")
    keys = ["m", "y", "dim", "ref", "hc", "overall", "grown", "perfect", "tdone", "tgoal", "best",
            "avg", "bestcur"]
    for i, k in enumerate(keys):
        S[k] = acell(1 + i, C_HVAL)

    month_cell = acell(R_BAND0 + 1, C_NAME)       # B3
    year_cell = acell(R_BAND0 + 3, C_NAME)        # B5
    names = rng(R_H0, C_NAME, R_H1, C_NAME)
    pct_row = rng(R_PCT, C_D0, R_PCT, C_D31)
    done_row = rng(R_DONE, C_D0, R_DONE, C_D31)
    day_row = rng(R_DAY, C_D0, R_DAY, C_D31)
    hv = lambda k, f: cv.put(int(S[k].split("$")[2]) - 1, C_HVAL, f)
    hv("m", f"=IFERROR(MATCH({month_cell},{MONTH_ARRAY},0),1)")
    hv("y", f"=IFERROR(--{year_cell},YEAR(TODAY()))")
    hv("dim", f"=DAY(EOMONTH(DATE({S['y']},{S['m']},1),0))")
    hv("ref", f"=IF(DATE({S['y']},{S['m']},1)>TODAY(),0,IF(AND(YEAR(TODAY())={S['y']},"
              f"MONTH(TODAY())={S['m']}),DAY(TODAY()),{S['dim']}))")
    hv("hc", f'=COUNTIF({names},"?*")')
    hv("tdone", f"=SUM({rng(R_H0, C_DONEN, R_H1, C_DONEN)})")
    hv("tgoal", f"=SUM({rng(R_H0, C_GOALN, R_H1, C_GOALN)})")
    hv("overall", f"=IFERROR(MIN(1,{S['tdone']}/{S['tgoal']}),0)")
    hv("grown", f'=COUNTIF({pct_row},">="&CFG_THR_3)')
    hv("perfect", f'=COUNTIF({pct_row},">=1")')
    hv("best", f"=MAX(0,{rng(R_H0, rc['long'], R_H1, rc['long'])})")
    hv("avg", f'=IFERROR(SUMIFS({pct_row},{day_row},"<="&{S["ref"]})/{S["ref"]},0)')
    hv("bestcur", f"=MAX(0,{rng(R_H0, rc['cur'], R_H1, rc['cur'])})")

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
        cv.put(R_BAND0, C_DON, f"={S['overall']}")
        cv.put(R_BAND0 + 1, C_DON, f"=1-{S['overall']}")
        cd1 = C_R0 + 2
        cv.merge(R_BAND0 + 1, C_R0, R_BAND1, cd1, f"={S['overall']}", bold=True, font_size=15,
                 align="center", num_format="0%", bg_color=t.card, font_name=t.font_title,
                 font_color=t.primary_dark)
        d = donut(wb, f"={q}!{rng(R_BAND0, C_DON, R_BAND0 + 1, C_DON)}", [t.primary, t.donut_rest], hole=70)
        place_chart(cv, d, R_BAND0 + 1, C_R0, R_BAND1, cd1, pad_y=2)
        kc = C_R0 + 3
        stats = [("CHECKS", f'={S["tdone"]}&" / "&{S["tgoal"]}'),
                 ("PERFECT DAYS", f"={S['perfect']}"),
                 ("BEST STREAK", f'={S["best"]}&" ngày"')]
        for i, (lab, f) in enumerate(stats):
            rr = R_BAND0 + 1 + i * 2 if i < 2 else R_BAND0 + 5
            if i < 2:
                cv.merge(rr, kc, rr, C_RE, lab, font_size=7.5, bold=True, align="center",
                         font_color=t.muted, bg_color=t.card)
                cv.merge(rr + 1, kc, rr + 1, C_RE, f, font_size=12, bold=True, align="center",
                         font_color=t.ink, bg_color=t.card, font_name=t.font_title)
            else:
                cv.merge(rr, kc, rr, C_RE, f'="🔥 "&{S["best"]}&" ngày liên tiếp"', font_size=8,
                         align="center", font_color=t.primary_dark, bg_color=t.card, bold=True)

    # ------------------------------------------------------------------ growth row
    cv.box(R_IMG, C_NAME, R_PCT, C_NAME, t.line, fill=t.card)
    cv.put(R_IMG, C_NAME, f"{t.emoji}  {spec.garden_label}", bold=True, font_size=11, align="center",
           bg_color=t.card, font_color=t.primary_dark, font_name=t.font_title)
    for r, lab in ((R_DONE, "COMPLETED  ✓"), (R_NOT, "NOT COMPLETED"), (R_PCT, "% COMPLETED")):
        cv.put(r, C_NAME, lab, align="right", font_size=8.5, bold=True, font_color=t.ink,
               bg_color=t.card, indent=1, top=1 if r == R_DONE else None, top_color=t.line)
    cv.hline(R_IMG, C_D0, C_D31, t.line, where="bottom")

    for k in range(1, 32):
        c = day_col(k)
        w = (k - 1) // 7
        dc = cell(R_DAY, c, row_abs=True)
        pc = cell(R_PCT, c)
        stage = f"(({pc}>0)+({pc}>=CFG_THR_1)+({pc}>=CFG_THR_2)+({pc}>=CFG_THR_3)+({pc}>=1))"
        if spec.offline_sprites:
            img_formula = f'=IF({dc}="","",INDEX(_Sprites!$A$1:$A$6,{stage}+1))'
        else:
            img_formula = f'=IF({dc}="","",_xlfn.IMAGE(CFG_IMG_BASE&"stage_"&{stage}&".png"))'
        cv.put(R_IMG, c, img_formula, bg_color=t.card, align="center")
        col_rng = rng(R_H0, c, R_H1, c, absolute=False).replace(str(R_H0 + 1), f"${R_H0 + 1}").replace(
            str(R_H1 + 1), f"${R_H1 + 1}")
        cv.put(R_DONE, c, f'=IF({dc}="","",COUNTIFS({names},"?*",{col_rng},TRUE)+'
                          f'COUNTIFS({names},"?*",{col_rng},"{CHECK_ALT}"))',
               align="center", font_size=9, bold=True, bg_color=t.week_tint[w], font_color=t.ink)
        cv.put(R_NOT, c, f'=IF({dc}="","",{S["hc"]}-{cell(R_DONE, c)})', align="center", font_size=9,
               bg_color=t.card, font_color=t.muted)
        cv.put(R_PCT, c, f'=IF({dc}="","",IFERROR({cell(R_DONE, c)}/{S["hc"]},0))', align="center",
               font_size=7.5, num_format="0%", bg_color=t.card, font_color=t.ink)
    cv.grid(R_DONE, C_D0, R_PCT, C_D31, t.line)
    cv.box(R_IMG, C_D0, R_PCT, C_D31, t.line)

    # ------------------------------------------------------------------ grown card (mid right)
    cv.box(R_IMG, C_R0, R_PCT, C_RE, t.line, fill=t.card)
    split = C_R0 + 2
    cv.merge(R_IMG, C_R0, R_IMG, split, spec.grown_label, bold=True, font_size=8.5, align="center",
             text_wrap=True, bg_color=t.card, font_color=t.ink)
    stage5_f = "=INDEX(_Sprites!$A$1:$A$6,6)" if spec.offline_sprites else '=_xlfn.IMAGE(CFG_IMG_BASE&"stage_5.png")'
    cv.merge(R_IMG, split + 1, R_IMG, C_RE, stage5_f, align="center", bg_color=t.card)
    cv.merge(R_DONE, C_R0, R_PCT, split, f"={S['grown']}", bold=True, font_size=26, align="center",
             bg_color=t.card, font_color=t.primary_dark, font_name=t.font_title)
    cv.merge(R_DONE, split + 1, R_PCT, C_RE, '="ngày đạt ≥ "&TEXT(CFG_THR_3,"0%")&CHAR(10)&"(trên "&' + S["dim"] + '&" ngày)"',
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
        fill = t.primary
        cv.merge(R_WEEK, c, R_DAY, c, lab, bold=True, font_size=7.5, align="center", text_wrap=True,
                 bg_color=fill, font_color=t.on_primary)
    cv.vline(C_RE, R_WEEK, R_DAY, t.card, where="right")
    for c in range(C_R0, C_RE):
        cv.vline(c, R_WEEK, R_DAY, t.card, where="right")

    # ------------------------------------------------------------------ habit rows
    rnd = random.Random(spec.seed)
    tick_grid = _sample_matrix(rnd, spec.habits)
    for i in range(N_HABITS):
        r = R_H0 + i
        h = spec.habits[i] if i < len(spec.habits) else None
        X = r + 1                                  # excel row number
        cv.put(r, C_NAME, h.name if h else "", align="left", indent=1, bg_color=t.card,
               font_color=t.ink, font_size=9.5)
        ticks = tick_grid[i] if i < len(tick_grid) else [False] * 31
        for k in range(1, 32):
            c = day_col(k)
            w = (k - 1) // 7
            cv.checkbox(r, c, ticks[k - 1], align="center", font_color=t.week_check[w], bg_color=t.card)
        # hidden run-length helper
        for k in range(1, 32):
            c = day_col(k)
            ref = cell(r, c)
            prev = "0" if k == 1 else cell(r, C_RUN0 + k - 2)
            cv.put(r, C_RUN0 + k - 1, f'=IF(AND({k}<={S["dim"]},{_done_test(ref)}),{prev}+1,0)')
        run = rng(r, C_RUN0, r, C_RUN0 + 30, absolute=False).replace(colname(C_RUN0), "$" + colname(C_RUN0)) \
            .replace(colname(C_RUN0 + 30), "$" + colname(C_RUN0 + 30))
        nm = f"${colname(C_NAME)}{X}"
        goal = f"${colname(rc['goal'])}{X}"
        dn = f"${colname(C_DONEN)}{X}"
        gn = f"${colname(C_GOALN)}{X}"
        cv.put(r, C_DONEN, f'=IF({nm}="",0,COUNTIF({run},">0"))')
        cv.put(r, C_GOALN, f'=IF({nm}="",0,IF({goal}="",{S["dim"]},MIN({goal},{S["dim"]})))')
        cv.put(r, rc["goal"], h.goal if (h and h.goal) else "", align="center", font_color=t.muted,
               bg_color=t.card, font_size=9, num_format="0")
        cv.put(r, rc["done"], f'=IF({nm}="","",{dn}&" / "&{gn})', align="center", font_size=9,
               bg_color=t.card, font_color=t.ink)
        cv.put(r, rc["progress"], f'=IF({nm}="","",IFERROR(MIN(1,{dn}/{gn}),0))', align="center",
               font_size=8.5, num_format="0%", bg_color=t.card, font_color=t.ink, bold=True)
        R = acell(1, 1)  # unused placeholder to keep linters calm
        ref_day = S["ref"]
        idx = lambda off: f"INDEX({run},{ref_day}{off})"
        cv.put(r, rc["cur"], f'=IF({nm}="","",IFERROR(IF({ref_day}=0,0,IF({idx("")}>0,{idx("")},'
                             f'IF({ref_day}>1,{idx("-1")},0))),0))',
               align="center", font_size=10, bold=True, bg_color=t.card, font_color=t.ink, num_format="0")
        cv.put(r, rc["long"], f'=IF({nm}="","",MAX({run}))', align="center", font_size=10, bold=True,
               bg_color=t.card, font_color=t.ink, num_format="0")
        for ec in spec.extra_cols:
            c = rc[ec["key"]]
            if ec["kind"] == "input":
                cv.put(r, c, h.extra.get(ec["key"], "") if h else ec.get("blank", ""), align="center",
                       font_size=9, bg_color=t.card, font_color=t.muted, num_format=ec.get("fmt", "General"))
            else:
                f = ec["formula"].format(r=X, nm=nm, dn=dn, gn=gn, **{k2: f"${colname(v)}{X}" for k2, v in rc.items()})
                cv.put(r, c, f, align="center", font_size=9.5, bold=True, bg_color=t.card, font_color=t.ink,
                       num_format=ec.get("fmt", "General"))
    cv.grid(R_H0, C_NAME, R_H1, C_D31, t.line)
    cv.grid(R_H0, C_R0, R_H1, C_RE, t.line)
    for k in (7, 14, 21, 28):
        cv.vline(day_col(k), R_H0, R_H1, t.week_head[(k - 1) // 7], where="right")

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

    # ------------------------------------------------------------------ weekly helpers
    for w in range(5):
        days = week_days(w)
        c1, c2 = day_col(days[0]), day_col(days[-1])
        hc = C_WK0 + w
        cv.put(1, hc, f"=SUM({rng(R_DONE, c1, R_DONE, c2)})")
        cv.put(2, hc, f'={S["hc"]}*COUNT({rng(R_DAY, c1, R_DAY, c2)})')
        cv.put(3, hc, f"=IFERROR({cell(1, hc)}/{cell(2, hc)},0)")
        cv.put(4, hc, f"=1-{cell(3, hc)}")
        cv.put(5, hc, f"={cell(2, hc)}-{cell(1, hc)}")

    # ------------------------------------------------------------------ conditional formats
    body = rng(R_H0, C_D0, R_H1, C_D31, absolute=False)
    top_left = cell(R_H0, C_D0)
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
    # out-of-month headers / stats -> blank look
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
                                   "mid_type": "num", "mid_value": 12, "max_type": "num", "max_value": 31,
                                   "min_color": t.streak_lo, "mid_color": t.streak_mid,
                                   "max_color": t.streak_hi})
    ws.conditional_format(streak, {"type": "cell", "criteria": ">=", "value": 18,
                                   "format": wb.add_format({"font_color": "#FFFFFF", "bold": True})})
    ws.data_validation(rng(R_H0, rc["goal"], R_H1, rc["goal"]),
                       {"validate": "integer", "criteria": "between", "minimum": 0, "maximum": 31,
                        "input_title": "Mục tiêu (ngày)", "input_message": "Số ngày muốn hoàn thành trong tháng. Bỏ trống = cả tháng.",
                        "error_title": "Mục tiêu không hợp lệ", "error_message": "Nhập số từ 0 đến 31."})
    ws.data_validation(rng(R_H0, C_NAME, R_H1, C_NAME),
                       {"validate": "any", "input_title": "Tên thói quen",
                        "input_message": "Gõ tên thói quen mới — công thức, checkbox & streak đã được nối sẵn!"})

    # sheet options
    ws.hide_gridlines(2)
    ws.set_zoom(85)
    ws.freeze_panes(0, 2)
    ws.set_tab_color(t.primary)
    ws.set_landscape()
    ws.set_paper(9)
    ws.fit_to_pages(1, 0)
    ws.set_margins(0.3, 0.3, 0.4, 0.4)

    return TrackerRefs(sheet=spec.sheet, q=q, month_cell=month_cell, year_cell=year_cell, s=S,
                       c_right_end=C_RE, right_cols=rc)


def _sample_matrix(rnd: random.Random, habits: list):
    """Generate a realistic, inspiring 31-day habit grid showcasing all 6 growth stages.

    Most days are strong (75%-100% -> stages 4 & 5) with a few natural dip days
    (stages 1-3) and Day 31 left empty (stage 0) so users see every growth sprite
    in action and the Daily Progress area chart forms a graceful organic wave.
    """
    n = len(habits)
    if n == 0:
        return []
    # Target daily completion ratios across 31 days (varied slightly per seed)
    base_wave = [
        1.00, 1.00, 0.88, 0.75, 0.62, 0.50, 0.75,   # Week 1: strong start + mid dip
        0.88, 1.00, 1.00, 0.88, 1.00, 0.75, 0.88,   # Week 2: peak momentum
        1.00, 0.88, 0.38, 0.20, 0.62, 0.88, 1.00,   # Week 3: busy-week dip (stages 1-3!) -> bounce back
        1.00, 0.88, 0.88, 0.75, 1.00, 0.88, 1.00,   # Week 4: consistent mastery
        0.88, 1.00, 0.00,                           # Week 5: Day 31 ready to tick (stage 0!)
    ]
    # Rotate middle weeks subtly based on seed so the 6 templates look distinct
    shift = rnd.randint(0, 4)
    wave = base_wave[:2] + base_wave[2 + shift:28] + base_wave[2:2 + shift] + base_wave[28:]

    # Rank habits by their affinity p so high-affinity habits get long streaks (20-30 days)
    order = sorted(range(n), key=lambda i: (-habits[i].p, rnd.random()))
    grid = [[False] * 31 for _ in range(n)]
    for d, ratio in enumerate(wave):
        if ratio <= 0:
            k = 0
        elif ratio >= 0.99:
            k = n
        else:
            k = max(1, min(n - 1, int(round(ratio * n))))
        # Pick top habits with slight jitter so streaks look organic yet impressive
        scored = sorted(
            range(n),
            key=lambda i: (habits[i].p + rnd.uniform(-0.18, 0.18) + (0.15 if i == order[0] else 0)),
            reverse=True,
        )
        for idx in scored[:k]:
            grid[idx][d] = True
    return grid


def attach_offline_sprites_sheet(wb, slug: str, assets_root):
    """Embed the 6 theme PNGs inside a hidden `_Sprites` sheet for 100% offline Excel 365 swapping."""
    import os
    sp = wb.add_worksheet("_Sprites")
    sp.set_column(0, 0, 14)
    for i in range(6):
        sp.set_row(i, 64)
        img_path = os.path.join(str(assets_root), slug, f"stage_{i}.png")
        sp.embed_image(i, 0, img_path)
    sp.hide()
    return sp
