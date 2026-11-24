"""
convert_offline_v30.py — Ultra-Fast Hybrid OpenXML + Excel COM Universal Form Control Converter (v3.0)
Converts `templates/excel_universal_offline/*.xlsx` from Excel-365 CellControls to 100% Universal
Excel 2016-365 Form Control Checkboxes + `;;;` hidden TRUE/FALSE across ALL 3 checkbox tabs:
  - Monthly Tracker (`ws Index 3`): `C17:AG36` (620) + addon checkboxes (`03_Rainbow` +30, `18_Plum_Oak` +36)
  - Daily One-Off Tasks (`📝 Nhiệm Vụ Ngày`): `B9:B28` (20)
  - Yearly Goals & Habits (`🎯 Yearly Goals & Habits`): `B6:B25` (20)
Verifies all 54 offline Linked Pictures remain intact and recycles EXCEL.EXE COM every 5 files!

Usage:
    python scripts/convert_offline_v30.py [file1.xlsx file2.xlsx ...]
    python scripts/convert_offline_v30.py --start 20 --end 31
"""
from __future__ import annotations

import gc
import re
import sys
import time
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import win32com.client as win32
from xlsxwriter.utility import xl_rowcol_to_cell

ROOT = Path(__file__).resolve().parent.parent
OFFLINE_DIR = ROOT / "templates" / "excel_universal_offline"
GUIDE_SHEET = "📖 Hướng Dẫn"
DAILY_TASKS_SHEET = "📝 Nhiệm Vụ Ngày"
YEARLY_GOALS_SHEET = "🎯 Yearly Goals & Habits"

SHAPETYPE_T201 = (
    '<v:shapetype id="_x0000_t201" coordsize="21600,21600" o:spt="201"\r\n'
    '  path="m,l,21600r21600,l21600,xe">\r\n'
    '  <v:stroke joinstyle="miter"/>\r\n'
    '  <v:path shadowok="f" o:extrusionok="f" strokeok="f" fillok="f" o:connecttype="rect"/>\r\n'
    '  <o:lock v:ext="edit" shapetype="t"/>\r\n'
    ' </v:shapetype>'
)

CTRL_REL_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/ctrlProp"
CTRL_CONTENT_TYPE = "application/vnd.ms-excel.controlproperties+xml"


def _read_sheet_specs_com(ws, coords: list[tuple[int, int]]) -> list[dict]:
    rows = sorted({r for r, _ in coords})
    cols = sorted({c for _, c in coords})
    row_geom = {r: (float(ws.Rows(r + 1).Top), float(ws.Rows(r + 1).Height)) for r in rows}
    col_geom = {c: (float(ws.Columns(c + 1).Left), float(ws.Columns(c + 1).Width)) for c in cols}

    r_min, r_max = rows[0], rows[-1]
    c_min, c_max = cols[0], cols[-1]
    raw_vals = ws.Range(ws.Cells(r_min + 1, c_min + 1), ws.Cells(r_max + 1, c_max + 1)).Value

    def _is_true(r: int, c: int) -> bool:
        if r_min == r_max and c_min == c_max:
            v = raw_vals
        elif r_min == r_max:
            v = raw_vals[0][c - c_min]
        elif c_min == c_max:
            v = raw_vals[r - r_min][0]
        else:
            v = raw_vals[r - r_min][c - c_min]
        return v is True

    cb_w, cb_h = 13.5, 13.5
    items = []
    for (r, c) in coords:
        c_left, c_w = col_geom[c]
        r_top, r_h = row_geom[r]
        dx1_pt = max(0.5, (c_w - 11.5) / 2.0)
        dy1_pt = max(0.5, (r_h - 13.0) / 2.0)
        dx2_pt = min(c_w - 0.5, dx1_pt + cb_w)
        dy2_pt = min(r_h - 0.5, dy1_pt + cb_h)
        items.append({
            "r": r, "c": c,
            "addr": xl_rowcol_to_cell(r, c, True, True),
            "checked": _is_true(r, c),
            "left_pt": c_left + dx1_pt, "top_pt": r_top + dy1_pt,
            "w_pt": dx2_pt - dx1_pt, "h_pt": dy2_pt - dy1_pt,
            "dx1_pt": dx1_pt, "dy1_pt": dy1_pt, "dx2_pt": dx2_pt, "dy2_pt": dy2_pt,
        })
    return items


def _step1_strip_controls_and_collect(xl, path: Path) -> dict[str, list[dict]]:
    wb = xl.Workbooks.Open(str(path.resolve()))
    try:
        xl.ScreenUpdating = False
        xl.EnableEvents = False
        xl.Calculation = -4135  # xlCalculationManual

        ws_tr = wb.Worksheets(3)
        ws_dt = wb.Worksheets(DAILY_TASKS_SHEET)
        ws_yg = wb.Worksheets(YEARLY_GOALS_SHEET)

        for ws in (ws_tr, ws_dt, ws_yg):
            if ws.CheckBoxes().Count > 0:
                ws.CheckBoxes().Delete()

        # 1. Monthly Tracker: C17:AG36 + template addons
        tr_rng = ws_tr.Range("C17:AG36")
        tr_rng.RemoveControls()
        tr_rng.NumberFormat = ";;;"
        tr_coords = [(r, c) for r in range(16, 36) for c in range(2, 33)]

        if "03_Rainbow" in path.name:
            for col_letter, col_idx in (("C", 2), ("I", 8), ("O", 14), ("U", 20), ("AA", 26)):
                r_extra = ws_tr.Range(f"{col_letter}48:{col_letter}53")
                r_extra.RemoveControls()
                r_extra.NumberFormat = ";;;"
                for r in range(47, 53):
                    tr_coords.append((r, col_idx))

        if "18_Plum_Oak" in path.name:
            for col_letter, col_idx in (("G", 6), ("I", 8), ("K", 10), ("M", 12), ("O", 14), ("AC", 28)):
                r_extra = ws_tr.Range(f"{col_letter}41:{col_letter}46")
                r_extra.RemoveControls()
                r_extra.NumberFormat = ";;;"
                for r in range(40, 46):
                    tr_coords.append((r, col_idx))

        # 2. Daily One-Off Tasks: B9:B28 (0-based rows 8..27, col 1 -> 20 cells)
        dt_rng = ws_dt.Range("B9:B28")
        dt_rng.RemoveControls()
        dt_rng.NumberFormat = ";;;"
        dt_coords = [(r, 1) for r in range(8, 28)]

        # 3. Yearly Goals & Habits: B6:B25 (0-based rows 5..24, col 1 -> 20 cells)
        yg_rng = ws_yg.Range("B6:B25")
        yg_rng.RemoveControls()
        yg_rng.NumberFormat = ";;;"
        yg_coords = [(r, 1) for r in range(5, 25)]

        specs = {
            ws_tr.Name: _read_sheet_specs_com(ws_tr, tr_coords),
            ws_dt.Name: _read_sheet_specs_com(ws_dt, dt_coords),
            ws_yg.Name: _read_sheet_specs_com(ws_yg, yg_coords),
        }

        xl.Calculation = -4105
        xl.ScreenUpdating = True
        xl.EnableEvents = True
        wb.Save()
        return specs
    finally:
        xl.EnableEvents = True
        wb.Close(SaveChanges=False)


def _find_sheet_paths(z: zipfile.ZipFile) -> dict[str, str]:
    wb_root = ET.fromstring(z.read("xl/workbook.xml"))
    rels_root = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    r_map = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels_root}
    ns_s = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    ns_r = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    out = {}
    for sh in wb_root.findall(f".//{{{ns_s}}}sheet"):
        name = sh.attrib["name"]
        rid = sh.attrib[f"{{{ns_r}}}id"]
        target = r_map[rid].lstrip("/")
        if not target.startswith("xl/"):
            target = "xl/" + target
        out[name] = target
    return out


def _step2_inject_form_checkboxes_ooxml(path: Path, specs_by_sheet: dict[str, list[dict]]) -> int:
    tmp_zip = path.with_suffix(".tmp.xlsx")
    with zipfile.ZipFile(path, "r") as zin:
        files = {name: zin.read(name) for name in zin.namelist()}
        sheet_paths = _find_sheet_paths(zin)

    for k in [n for n in list(files.keys()) if n.startswith("xl/ctrlProps/")]:
        del files[k]
    ct_xml = files["[Content_Types].xml"].decode("utf-8")
    ct_xml = re.sub(r'<Override[^>]*PartName="/xl/ctrlProps/[^"]*"[^>]*/>', "", ct_xml)

    ctrl_prop_idx = 0
    total_injected = 0

    for sheet_name, items in specs_by_sheet.items():
        sh_path = sheet_paths[sheet_name]
        sh_file = sh_path.split("/")[-1]
        rels_path = f"xl/worksheets/_rels/{sh_file}.rels"

        sh_xml = files[sh_path].decode("utf-8")
        rels_xml = files[rels_path].decode("utf-8")

        m_vml = re.search(r'<Relationship[^>]*Type="[^"]*/vmlDrawing"[^>]*Target="([^"]+)"', rels_xml)
        if not m_vml:
            raise RuntimeError(f"No vmlDrawing relationship found for {sheet_name} ({rels_path})")
        vml_path = "xl/" + m_vml.group(1).replace("../", "")
        vml_xml = files[vml_path].decode("utf-8")

        rels_xml = re.sub(r'<Relationship[^>]*Type="[^"]*/ctrlProp"[^>]*/>', "", rels_xml)
        sh_xml = re.sub(
            r'<mc:AlternateContent[^>]*><mc:Choice Requires="x14"><controls>.*?</controls></mc:Choice></mc:AlternateContent>',
            "",
            sh_xml,
            flags=re.S,
        )
        sh_xml = re.sub(r"<controls>.*?</controls>", "", sh_xml, flags=re.S)

        existing_rids = [int(x) for x in re.findall(r'Id="rId(\d+)"', rels_xml)]
        next_rid = (max(existing_rids) if existing_rids else 0) + 1
        existing_sids = [int(x) for x in re.findall(r'_x0000_s(\d+)', vml_xml)]
        next_sid = max(existing_sids, default=1024) + 50

        vml_shapes = []
        if 'id="_x0000_t201"' not in vml_xml:
            vml_shapes.append(SHAPETYPE_T201)

        ctrl_entries = []
        new_rels = []
        new_ct_overrides = []
        px_per_pt = 96.0 / 72.0

        for idx_local, it in enumerate(items, start=1):
            ctrl_prop_idx += 1
            sid = next_sid
            next_sid += 1
            rid = f"rId{next_rid}"
            next_rid += 1

            r, c = it["r"], it["c"]
            addr = it["addr"]
            checked = it["checked"]

            x1_emu = int(round(it["dx1_pt"] * 12700))
            y1_emu = int(round(it["dy1_pt"] * 12700))
            x2_emu = int(round(it["dx2_pt"] * 12700))
            y2_emu = int(round(it["dy2_pt"] * 12700))
            x1_px = int(round(it["dx1_pt"] * px_per_pt))
            y1_px = int(round(it["dy1_pt"] * px_per_pt))
            x2_px = int(round(it["dx2_pt"] * px_per_pt))
            y2_px = int(round(it["dy2_pt"] * px_per_pt))

            chk_attr = ' checked="Checked"' if checked else ""
            cp_xml = (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n'
                f'<formControlPr xmlns="http://schemas.microsoft.com/office/spreadsheetml/2009/9/main"'
                f' objectType="CheckBox"{chk_attr} fmlaLink="{addr}" lockText="1" noThreeD="1"/>'
            )
            files[f"xl/ctrlProps/ctrlProp{ctrl_prop_idx}.xml"] = cp_xml.encode("utf-8")

            new_ct_overrides.append(
                f'<Override PartName="/xl/ctrlProps/ctrlProp{ctrl_prop_idx}.xml" ContentType="{CTRL_CONTENT_TYPE}"/>'
            )
            new_rels.append(
                f'<Relationship Id="{rid}" Type="{CTRL_REL_TYPE}" Target="../ctrlProps/ctrlProp{ctrl_prop_idx}.xml"/>'
            )
            ctrl_entries.append(
                f'<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006">'
                f'<mc:Choice Requires="x14">'
                f'<control shapeId="{sid}" r:id="{rid}" name="Check Box {ctrl_prop_idx}">'
                f'<controlPr defaultSize="0" autoFill="0" autoLine="0" autoPict="0">'
                f'<anchor moveWithCells="1">'
                f'<from><xdr:col>{c}</xdr:col><xdr:colOff>{x1_emu}</xdr:colOff>'
                f'<xdr:row>{r}</xdr:row><xdr:rowOff>{y1_emu}</xdr:rowOff></from>'
                f'<to><xdr:col>{c}</xdr:col><xdr:colOff>{x2_emu}</xdr:colOff>'
                f'<xdr:row>{r}</xdr:row><xdr:rowOff>{y2_emu}</xdr:rowOff></to>'
                f'</anchor></controlPr></control>'
                f'</mc:Choice></mc:AlternateContent>'
            )
            chk_vml = "\r\n   <x:Checked>1</x:Checked>" if checked else ""
            vml_shapes.append(
                f'<v:shape id="_x0000_s{sid}" type="#_x0000_t201" style=\'position:absolute;\r\n'
                f'  margin-left:{it["left_pt"]:.1f}pt;margin-top:{it["top_pt"]:.1f}pt;'
                f'width:{it["w_pt"]:.1f}pt;height:{it["h_pt"]:.1f}pt;z-index:{100 + idx_local};\r\n'
                f'  mso-wrap-style:tight\' filled="f" fillcolor="windowText [64]" stroked="f"\r\n'
                f'  strokecolor="window [65]" strokeweight="3e-5mm" o:insetmode="auto">\r\n'
                f'  <v:fill color2="window [65]"/>\r\n'
                f'  <v:path shadowok="t" strokeok="t" fillok="t"/>\r\n'
                f'  <o:lock v:ext="edit" rotation="t"/>\r\n'
                f'  <v:textbox style=\'mso-direction-alt:auto\' o:singleclick="f">\r\n'
                f'   <div style=\'text-align:left;direction:ltr\'></div>\r\n'
                f'  </v:textbox>\r\n'
                f'  <x:ClientData ObjectType="Checkbox">\r\n'
                f'   <x:SizeWithCells/>\r\n'
                f'   <x:Anchor>\r\n'
                f'    {c}, {x1_px}, {r}, {y1_px}, {c}, {x2_px}, {r}, {y2_px}</x:Anchor>\r\n'
                f'   <x:AutoFill>False</x:AutoFill>\r\n'
                f'   <x:AutoLine>False</x:AutoLine>\r\n'
                f'   <x:TextVAlign>Center</x:TextVAlign>{chk_vml}\r\n'
                f'   <x:FmlaLink>{addr}</x:FmlaLink>\r\n'
                f'   <x:NoThreeD/>\r\n'
                f'  </x:ClientData>\r\n'
                f' </v:shape>'
            )
            total_injected += 1

        vml_xml = vml_xml.replace("</xml>", "".join(vml_shapes) + "</xml>", 1)
        files[vml_path] = vml_xml.encode("utf-8")

        rels_xml = rels_xml.replace("</Relationships>", "".join(new_rels) + "</Relationships>", 1)
        files[rels_path] = rels_xml.encode("utf-8")

        controls_block = (
            '<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006">'
            '<mc:Choice Requires="x14"><controls>'
            + "".join(ctrl_entries)
            + "</controls></mc:Choice></mc:AlternateContent>"
        )
        m_ld = re.search(r"<legacyDrawing[^/>]*/>", sh_xml)
        if not m_ld:
            raise RuntimeError(f"No <legacyDrawing/> found in {sh_path}")
        sh_xml = sh_xml[: m_ld.end()] + controls_block + sh_xml[m_ld.end() :]
        files[sh_path] = sh_xml.encode("utf-8")

        ct_xml = ct_xml.replace("</Types>", "".join(new_ct_overrides) + "</Types>", 1)

    files["[Content_Types].xml"] = ct_xml.encode("utf-8")
    with zipfile.ZipFile(tmp_zip, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for name, data in files.items():
            zout.writestr(name, data)
    tmp_zip.replace(path)
    return total_injected


def _step3_validate_and_finalize_com(xl, path: Path, exp_tr: int, exp_dt: int, exp_yg: int) -> dict:
    wb = xl.Workbooks.Open(str(path.resolve()))
    try:
        xl.ScreenUpdating = False
        xl.EnableEvents = False
        ws_tr = wb.Worksheets(3)
        ws_dt = wb.Worksheets(DAILY_TASKS_SHEET)
        ws_yg = wb.Worksheets(YEARLY_GOALS_SHEET)

        tr_cbs = ws_tr.CheckBoxes().Count
        dt_cbs = ws_dt.CheckBoxes().Count
        yg_cbs = ws_yg.CheckBoxes().Count
        pic_total = sum(ws.Pictures().Count for ws in wb.Worksheets if ws.Visible == -1)

        if tr_cbs != exp_tr or dt_cbs != exp_dt or yg_cbs != exp_yg:
            raise RuntimeError(
                f"{path.name}: checkbox mismatch! got tr={tr_cbs}/{exp_tr}, dt={dt_cbs}/{exp_dt}, yg={yg_cbs}/{exp_yg}"
            )
        if pic_total not in (54, 55, 56):
            raise RuntimeError(f"{path.name}: linked picture mismatch! got {pic_total} (exp 54, 55, or 56)")

        xl.Calculation = -4105
        xl.ScreenUpdating = True
        xl.CalculateFullRebuild()
        time.sleep(0.2)

        wb.Worksheets(GUIDE_SHEET).Activate()
        wb.Worksheets(GUIDE_SHEET).Range("A1").Select()
        xl.EnableEvents = True
        wb.Save()
        return {"tr_cbs": tr_cbs, "dt_cbs": dt_cbs, "yg_cbs": yg_cbs, "pics": pic_total}
    finally:
        xl.EnableEvents = True
        wb.Close(SaveChanges=False)


def convert_workbook(xl, path: Path) -> dict:
    t0 = time.perf_counter()
    specs = _step1_strip_controls_and_collect(xl, path)
    _step2_inject_form_checkboxes_ooxml(path, specs)
    keys = list(specs.keys())
    res = _step3_validate_and_finalize_com(
        xl, path, len(specs[keys[0]]), len(specs[DAILY_TASKS_SHEET]), len(specs[YEARLY_GOALS_SHEET])
    )
    dt = time.perf_counter() - t0
    return {
        "file": path.name, **res,
        "size": path.stat().st_size, "sec": dt,
    }


def main():
    args = sys.argv[1:]
    start_idx, end_idx, raw_paths = None, None, []
    i = 0
    while i < len(args):
        if args[i] == "--start" and i + 1 < len(args):
            start_idx = int(args[i + 1]); i += 2
        elif args[i] == "--end" and i + 1 < len(args):
            end_idx = int(args[i + 1]); i += 2
        else:
            raw_paths.append(Path(args[i])); i += 1

    if start_idx is not None or end_idx is not None:
        all_off = sorted(OFFLINE_DIR.glob("*.xlsx"))
        targets = all_off[(start_idx or 1) - 1 : (end_idx or len(all_off))]
    elif raw_paths:
        targets = raw_paths
    else:
        targets = sorted(OFFLINE_DIR.glob("*.xlsx"))

    print(f"Converting {len(targets)} Offline .xlsx file(s) to v3.0 Universal Form Checkboxes (recycling COM every 5)...", flush=True)
    for chunk_i in range(0, len(targets), 5):
        chunk = targets[chunk_i : chunk_i + 5]
        xl = win32.DispatchEx("Excel.Application")
        xl.Visible = False
        xl.DisplayAlerts = False
        try:
            try:
                xl.EnableAnimations = False
            except Exception:
                pass
            for p in chunk:
                info = convert_workbook(xl, p)
                print(
                    f"  OK {info['file']}: cbs={info['tr_cbs']}+{info['dt_cbs']}+{info['yg_cbs']}, "
                    f"pics={info['pics']}, {info['size']:,} B ({info['sec']:.1f}s)",
                    flush=True,
                )
        finally:
            xl.Quit()
            del xl
            gc.collect()
            time.sleep(0.4)


if __name__ == "__main__":
    main()
