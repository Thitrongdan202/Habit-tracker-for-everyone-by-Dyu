"""
hx.core — shared building blocks for the Habit Tracker collection.

Design idea
-----------
xlsxwriter needs one complete Format per cell, but a "card UI" spreadsheet is
built in layers (page background -> card fill -> card border -> content).
`Canvas` buffers every cell as a dict of style properties, lets us paint layers
on top of each other, and only writes to the worksheet in `flush()`.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from xlsxwriter.utility import xl_rowcol_to_cell, xl_col_to_name

REPO_RAW = "https://raw.githubusercontent.com/Thitrongdan202/Habit-tracker-for-everyone-by-Dyu/main/assets/"
REPO_URL = "https://github.com/Thitrongdan202/Habit-tracker-for-everyone-by-Dyu"

MONTHS_EN = ["January", "February", "March", "April", "May", "June", "July",
             "August", "September", "October", "November", "December"]
MONTH_ARRAY = "{" + ",".join(f'"{m}"' for m in MONTHS_EN) + "}"

CHECK_ALT = "✓"          # legacy alternative to a TRUE checkbox


# --------------------------------------------------------------------------- #
#  Theme
# --------------------------------------------------------------------------- #
@dataclass
class Theme:
    slug: str                    # asset folder name
    name: str                    # e.g. "SUNFLOWER GARDEN"
    emoji: str
    tagline_vi: str
    # typography — strictly unified ONE clean font family (`Segoe UI`) across 100% of cells & charts!
    font: str = "Segoe UI"
    font_title: str = "Segoe UI"
    font_month: str = "Segoe UI"
    # palette
    page: str = "#FFFDFB"        # sheet background (gutters)
    card: str = "#FFFFFF"        # card background
    ink: str = "#4A3F3F"         # main text
    muted: str = "#9C8C8C"       # secondary text
    line: str = "#EADADA"        # card borders / hairlines
    primary: str = "#D8A7A7"     # strong header fill
    primary_dark: str = "#B97F7F"
    on_primary: str = "#FFFFFF"  # text on primary
    soft: str = "#F5E6E6"        # light fill
    chart_fill: str = "#E9C9C9"
    chart_line: str = "#C98F8F"
    week_head: list = field(default_factory=lambda: ["#D8A7A7"] * 5)
    week_tint: list = field(default_factory=lambda: ["#F5E6E6"] * 5)
    week_check: list = field(default_factory=lambda: ["#C98F8F"] * 5)
    week_on: list = field(default_factory=lambda: ["#FFFFFF"] * 5)   # text on week_head
    streak_lo: str = "#F1FAF4"
    streak_mid: str = "#A8DAB9"
    streak_hi: str = "#4E9F76"
    bar: str = "#D8A7A7"
    donut_rest: str = "#F1E4E4"
    weekday_style: str = "short"          # "short" -> Mon, "letter" -> M
    chart_markers: bool = False
    chart_title: str = "DAILY PROGRESS"
    chart_kind: str = "area"              # "area" | "line" | "column"
    pct_traffic_light: bool = False       # True -> Emerald/Amber/Coral traffic-light % row
    check_fill_override: str | None = None  # Optional override fill for checked cells (e.g. Gold Star)
    hero_header_bg: str | None = None     # Optional accent banner bg on Grown Hero card
    hero_header_fg: str | None = None     # Optional accent banner fg on Grown Hero card
    warn_fill: str = "#FFF6DD"
    warn_line: str = "#F1D88A"

    @property
    def img_base(self) -> str:
        return REPO_RAW + self.slug + "/"


# --------------------------------------------------------------------------- #
#  Unit helpers (xlsxwriter default font Calibri 11 => max digit width 7px)
# --------------------------------------------------------------------------- #
def col_px(width: float) -> int:
    if width <= 0:
        return 0
    if width < 1:
        return int(width * 12 + 0.5)
    return int(width * 7 + 0.5) + 5


def row_px(height_pt: float) -> int:
    return int(round(height_pt * 4 / 3))


def cell(r: int, c: int, row_abs=False, col_abs=False) -> str:
    return xl_rowcol_to_cell(r, c, row_abs, col_abs)


def acell(r: int, c: int) -> str:
    return xl_rowcol_to_cell(r, c, True, True)


def rng(r1, c1, r2, c2, absolute=True) -> str:
    return f"{xl_rowcol_to_cell(r1, c1, absolute, absolute)}:{xl_rowcol_to_cell(r2, c2, absolute, absolute)}"


def colname(c: int) -> str:
    return xl_col_to_name(c)


def qs(sheet: str) -> str:
    """Quote a sheet name for formulas."""
    return "'" + sheet.replace("'", "''") + "'"


def checked_pastel_bg(head_hex: str, tint_hex: str) -> str:
    """Return a crisp, joyful pastel fill for checked (TRUE) checkbox cells:
    boosts contrast slightly over ultra-pale `tint_hex` while keeping dark themes readable."""
    def _rgb(h: str):
        h = h.lstrip("#")
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r, g, b = _rgb(head_hex)
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
    # Light/pastel headers (Cactus, Rainbow, Sunflower, Sakura): richer pastel blend (~58% head)
    # Dark headers (Navy, Aurora, Ocean): gentle soft blend (~22% head) so dark checkbox stays super sharp
    alpha = 0.58 if lum > 0.72 else (0.36 if lum > 0.45 else 0.18)
    mr = int(round(r * alpha + 255 * (1 - alpha)))
    mg = int(round(g * alpha + 255 * (1 - alpha)))
    mb = int(round(b * alpha + 255 * (1 - alpha)))
    return f"#{mr:02X}{mg:02X}{mb:02X}"


def text_lines(text: str, width_chars: float, factor: float = 1.0) -> int:
    """Estimate wrapped line count for Segoe UI 10 in a cell `width_chars` wide."""
    usable = max(8.0, width_chars * 1.18 * factor)
    lines = 0
    for para in str(text).split("\n"):
        lines += max(1, math.ceil(len(para) / usable))
    return lines


# --------------------------------------------------------------------------- #
#  Format cache
# --------------------------------------------------------------------------- #
class Styles:
    def __init__(self, wb, theme: Theme):
        self.wb = wb
        self.t = theme
        self._cache: dict = {}

    def base(self) -> dict:
        return {"font_name": self.t.font, "font_size": 10, "font_color": self.t.ink,
                "valign": "vcenter", "bg_color": self.t.page}

    def get(self, props: dict):
        p = self.base()
        p.update({k: v for k, v in props.items() if v is not None})
        # drop "pattern" when no bg
        key = tuple(sorted((k, str(v)) for k, v in p.items()))
        if key not in self._cache:
            self._cache[key] = self.wb.add_format(p)
        return self._cache[key]


# --------------------------------------------------------------------------- #
#  Canvas
# --------------------------------------------------------------------------- #
class Canvas:
    """Buffered, layer-friendly worksheet writer."""

    def __init__(self, wb, ws, styles: Styles, name: str, universal: bool = False, gsheets: bool = False):
        self.wb, self.ws, self.S, self.name = wb, ws, styles, name
        self.universal = universal
        self.gsheets = gsheets
        self.t = styles.t
        self.cells: dict[tuple[int, int], dict[str, Any]] = {}
        self.merges: list[tuple[int, int, int, int]] = []
        self.widths: dict[int, float] = {}
        self.heights: dict[int, float] = {}
        self.hidden_cols: set[int] = set()
        self.form_checkboxes: list[tuple[int, int]] = []
        self.unlock_ranges: list[tuple[int, int, int, int]] = []
        self.max_col = 0
        self.max_row = 0

    def unlock(self, r1: int, c1: int, r2: int | None = None, c2: int | None = None):
        """Register 0-based (r1, c1, r2, c2) user-editable range to unlock under sheet protection."""
        self.unlock_ranges.append((r1, c1, r1 if r2 is None else r2, c1 if c2 is None else c2))

    # ---- geometry -------------------------------------------------------
    def col(self, c: int, width: float, hidden=False):
        self.widths[c] = width
        if hidden:
            self.hidden_cols.add(c)

    def cols(self, c1: int, c2: int, width: float, hidden=False):
        for c in range(c1, c2 + 1):
            self.col(c, width, hidden)

    def row(self, r: int, height: float):
        self.heights[r] = height

    def px_x(self, c: int) -> int:
        return sum(col_px(self.widths.get(i, 8.43)) for i in range(c) if i not in self.hidden_cols)

    def px_w(self, c1: int, c2: int) -> int:
        return sum(col_px(self.widths.get(i, 8.43)) for i in range(c1, c2 + 1) if i not in self.hidden_cols)

    def px_h(self, r1: int, r2: int) -> int:
        return sum(row_px(self.heights.get(i, 15)) for i in range(r1, r2 + 1))

    # ---- painting -------------------------------------------------------
    def _cell(self, r, c):
        self.max_col = max(self.max_col, c)
        self.max_row = max(self.max_row, r)
        return self.cells.setdefault((r, c), {"props": {}, "kind": None, "value": None})

    def style(self, r1, c1, r2, c2, **props):
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                self._cell(r, c)["props"].update(props)

    def fill(self, r1, c1, r2, c2, color):
        self.style(r1, c1, r2, c2, bg_color=color)

    def box(self, r1, c1, r2, c2, color=None, weight=1, fill=None):
        """Card: optional fill + outer border."""
        color = color or self.t.line
        if fill:
            self.fill(r1, c1, r2, c2, fill)
        for c in range(c1, c2 + 1):
            self._cell(r1, c)["props"].update(top=weight, top_color=color)
            self._cell(r2, c)["props"].update(bottom=weight, bottom_color=color)
        for r in range(r1, r2 + 1):
            self._cell(r, c1)["props"].update(left=weight, left_color=color)
            self._cell(r, c2)["props"].update(right=weight, right_color=color)

    def hline(self, r, c1, c2, color=None, weight=1, where="bottom"):
        color = color or self.t.line
        for c in range(c1, c2 + 1):
            self._cell(r, c)["props"].update({where: weight, f"{where}_color": color})

    def vline(self, c, r1, r2, color=None, weight=1, where="right"):
        color = color or self.t.line
        for r in range(r1, r2 + 1):
            self._cell(r, c)["props"].update({where: weight, f"{where}_color": color})

    def grid(self, r1, c1, r2, c2, color=None, weight=1):
        """Hairline inner grid (bottom + right of every cell)."""
        color = color or self.t.line
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                self._cell(r, c)["props"].update(bottom=weight, bottom_color=color,
                                                 right=weight, right_color=color)

    # ---- content --------------------------------------------------------
    def put(self, r, c, value, **props):
        d = self._cell(r, c)
        d["props"].update(props)
        if isinstance(value, str) and value.startswith("="):
            d["kind"], d["value"] = "formula", value
        else:
            d["kind"], d["value"] = "value", value
        return d

    def merge(self, r1, c1, r2, c2, value=None, **props):
        if (r1, c1) != (r2, c2):
            self.merges.append((r1, c1, r2, c2))
        self.style(r1, c1, r2, c2)  # touch cells
        if value is not None:
            self.put(r1, c1, value, **props)
        else:
            self._cell(r1, c1)["props"].update(props)
        # share fill/font props to all cells of the merge
        if props:
            for r in range(r1, r2 + 1):
                for c in range(c1, c2 + 1):
                    if (r, c) != (r1, c1):
                        self._cell(r, c)["props"].update(
                            {k: v for k, v in props.items()
                             if k not in ("top", "bottom", "left", "right", "top_color",
                                          "bottom_color", "left_color", "right_color")})
        return (r1, c1, r2, c2)

    def checkbox(self, r, c, value: bool, **props):
        d = self._cell(r, c)
        d["props"].update(props)
        if self.gsheets:
            # Google Sheets Edition: clean centered, softly styled boolean cells ready for 1-click Insert -> Checkbox or Apps Script!
            d["props"].setdefault("align", "center")
            d["props"]["font_size"] = 7.5
            d["props"]["font_color"] = self.t.muted
            d["kind"], d["value"] = "value", bool(value)
        else:
            # Pro .xlsm & Universal Offline .xlsx: Excel Native Cell Checkboxes with theme/week pastel colors!
            d["props"].setdefault("align", "center")
            d["props"].setdefault("font_size", 11.5)
            d["kind"], d["value"] = "checkbox", bool(value)

    def blank_row_fill(self, r, c1, c2, color):
        self.fill(r, c1, r, c2, color)

    # ---- flush ----------------------------------------------------------
    def _merge_format(self, r1, c1, r2, c2):
        tl = dict(self.cells.get((r1, c1), {}).get("props", {}))
        for side, (rr, cc) in {"top": (r1, c1), "left": (r1, c1),
                               "bottom": (r2, c1), "right": (r1, c2)}.items():
            p = self.cells.get((rr, cc), {}).get("props", {})
            tl.pop(side, None)
            tl.pop(side + "_color", None)
            if side in p:
                tl[side] = p[side]
                tl[side + "_color"] = p.get(side + "_color")
        return tl

    def flush(self):
        ws, S = self.ws, self.S
        page_fmt = S.get({})
        last_col = max(self.max_col + 2, 60)
        for c in range(0, last_col + 1):
            w = self.widths.get(c, 8.43)
            opts = {"hidden": True} if c in self.hidden_cols else {}
            ws.set_column(c, c, w, page_fmt, opts)
        for r, h in self.heights.items():
            ws.set_row(r, h)

        merged_cells = set()
        for (r1, c1, r2, c2) in self.merges:
            props = self._merge_format(r1, c1, r2, c2)
            fmt = S.get(props)
            d = self.cells.get((r1, c1), {})
            kind, value = d.get("kind"), d.get("value")
            data = "" if value is None else value
            ws.merge_range(r1, c1, r2, c2, "", fmt)
            if kind == "formula":
                ws.write_formula(r1, c1, value, fmt)
            elif value is not None and value != "":
                ws.write(r1, c1, data, fmt)
            for r in range(r1, r2 + 1):
                for c in range(c1, c2 + 1):
                    merged_cells.add((r, c))

        for (r, c), d in self.cells.items():
            if (r, c) in merged_cells:
                continue
            fmt = S.get(d["props"])
            kind, value = d["kind"], d["value"]
            if kind == "formula":
                ws.write_formula(r, c, value, fmt)
            elif kind == "checkbox":
                ws.insert_checkbox(r, c, value, fmt)
            elif kind == "value" and value is not None and value != "":
                ws.write(r, c, value, fmt)
            else:
                ws.write_blank(r, c, None, fmt)

        ws.ignore_errors({k: f"A1:{colname(last_col + 40)}{self.max_row + 60}" for k in (
            "number_stored_as_text", "eval_error", "formula_differs", "formula_range",
            "formula_unlocked", "empty_cell_reference", "list_data_validation")})


# --------------------------------------------------------------------------- #
#  Small UI widgets
# --------------------------------------------------------------------------- #
def section_header(cv: Canvas, r, c1, c2, text, fill=None, color=None, size=10, height=24,
                   align="center", font=None):
    t = cv.t
    cv.row(r, height)
    cv.merge(r, c1, r, c2, text, bold=True, font_size=size, align=align,
             bg_color=fill or t.primary, font_color=color or t.on_primary,
             font_name=font or t.font, indent=1 if align == "left" else None)


def kpi_card(cv: Canvas, r, c1, c2, label, formula, num_format="0", fill=None, label_fill=None,
             value_color=None, value_size=20, label_color=None, rows=2):
    """Label strip on top + big value merged below (rows-1 rows)."""
    t = cv.t
    cv.merge(r, c1, r, c2, label, bold=True, font_size=8.5, align="center",
             bg_color=label_fill or t.soft, font_color=label_color or t.ink)
    cv.merge(r + 1, c1, r + rows - 1, c2, formula, bold=True, font_size=value_size, align="center",
             bg_color=fill or t.card, font_color=value_color or t.ink, num_format=num_format,
             font_name=t.font_title)
    cv.box(r, c1, r + rows - 1, c2, t.line)


def donut(wb, values_ref: str, colors: list, hole=68, name="Donut"):
    ch = wb.add_chart({"type": "doughnut"})
    ch.add_series({
        "name": name,
        "values": values_ref,
        "points": [{"fill": {"color": col}, "border": {"none": True}} for col in colors],
    })
    ch.set_hole_size(hole)
    ch.set_rotation(0)
    ch.set_title({"none": True})
    ch.set_legend({"none": True})
    ch.show_hidden_data()
    ch.set_chartarea({"border": {"none": True}, "fill": {"none": True}})
    ch.set_plotarea({"layout": {"x": 0.06, "y": 0.06, "width": 0.88, "height": 0.88},
                     "border": {"none": True}, "fill": {"none": True}})
    return ch


def place_chart(cv: Canvas, chart, r1, c1, r2, c2, pad_x=0, pad_y=0):
    """Size a chart to exactly cover a cell block (minus padding)."""
    w = cv.px_w(c1, c2) - 2 * pad_x
    h = cv.px_h(r1, r2) - 2 * pad_y
    chart.set_size({"width": max(w, 20), "height": max(h, 20)})
    cv.ws.insert_chart(r1, c1, chart, {"x_offset": pad_x, "y_offset": pad_y, "object_position": 1})


def axis_font(theme: Theme, size=8, color=None):
    return {"name": theme.font, "size": size, "color": color or theme.muted}
