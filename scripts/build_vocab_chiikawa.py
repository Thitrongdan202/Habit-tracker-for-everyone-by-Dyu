"""
build_vocab_chiikawa.py — Full 4-Edition Compiler for Chiikawa Vocabulary Trackers (#96–#100):
  1. `templates/pro_macro/96..100_*_Pro.xlsm`
       - Native pre-placed Chiikawa Sprite Stacks (`SPR_VHERO_S0..S5`, `SPR_PHERO_S0..S5`,
         `SPR_SHERO_S0..S5`, `Guide_Stage0..5`) + SHA-256 media dedup (6 unique PNGs!)
       - Native Excel 365 Checkboxes (`CellControl.SetCheckbox()`) on all checkbox ranges
       - Injects `vba_scripts/modVocabPro.bas` + `ThisWorkbook` + Tab 1/Tab 2 event handlers
       - Mounts sleek Pro Pill Buttons (`🎲 Dò Bài Ngẫu Nhiên`, `✨ FX: BẬT`, `🎉 Thử Hiệu Ứng Chiikawa`)
       - Worksheet protection (`UserInterfaceOnly=True`)
  2. `templates/excel_universal_offline/96..100_*.xlsx`
       - 100% macro-free offline `.xlsx` with embedded `_Assets!B2:B7` + Dynamic Linked Pictures
         (`Anim_VocabHero`, `Anim_PracHero`, `Anim_StatsHero`, `Guide_Stage0..5`) + native Checkboxes
  3. `templates/google_sheets_edition/96..100_*.xlsx`
       - Pure `xlsxwriter` output, `Be Vietnam Pro`, pure `=IMAGE(...)` (ZERO `_xludf.IMAGE`!)
  4. `templates/mobile_portrait_sheets/96..100_*_Mobile.xlsx`
       - Strictly portrait `<= Col G`, Excel COM `SetCheckbox()` + OOXML post-pass stripping
         any `_xludf.` from `_xludf.IMAGE(` back to pure `IMAGE(`!

Zero `_build_tmp/` left behind — uses isolated `%TEMP%` workspace cleaned in `finally`.
"""
from __future__ import annotations

import gc
import os
import re
import shutil
import sys
import tempfile
import time
import zipfile
from pathlib import Path

import pythoncom
import win32com.client as win32

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from hx.vocab_data import VOCAB_THEMES, VocabThemeDef
from hx.vocab_builder import (
    ASSETS_SHEET, CALC_SHEET, GUIDE_SHEET, MOB_MAIN_SHEET, MOB_PRAC_SHEET,
    PRACTICE_SHEET, STATS_SHEET, VOCAB_SHEET,
    build_vocab_desktop_workbook, build_vocab_mobile_workbook,
)
from excel_com_enhancer import _add_pill_button, _hex_to_bgr, deduplicate_xlsm_media

ASSETS_DIR = ROOT / "assets"
VBA_VOCAB_PATH = ROOT / "vba_scripts" / "modVocabPro.bas"
PRO_DIR = ROOT / "templates" / "pro_macro"
OFF_DIR = ROOT / "templates" / "excel_universal_offline"
GS_DIR = ROOT / "templates" / "google_sheets_edition"
MOB_DIR = ROOT / "templates" / "mobile_portrait_sheets"

WB_EVENT_VBA = (
    "Option Explicit\r\n"
    "Private Sub Workbook_Open()\r\n"
    "    modVocabPro.InitVocabWorkbook\r\n"
    "End Sub\r\n"
    "Private Sub Workbook_BeforeClose(Cancel As Boolean)\r\n"
    "    modVocabPro.CleanupAllVocabFX\r\n"
    "End Sub\r\n"
)

VOCAB_WS_EVENT_VBA = (
    "Option Explicit\r\n"
    "Private Sub Worksheet_Change(ByVal Target As Range)\r\n"
    "    If Not Intersect(Target, Me.Range(\"C15:N114\")) Is Nothing Then\r\n"
    "        modVocabPro.HandleVocabEdit Me, Target\r\n"
    "    End If\r\n"
    "End Sub\r\n"
)

PRAC_WS_EVENT_VBA = (
    "Option Explicit\r\n"
    "Private Sub Worksheet_Change(ByVal Target As Range)\r\n"
    "    If Not Intersect(Target, Me.Range(\"B10:B14\")) Is Nothing Then\r\n"
    "        modVocabPro.HandlePracticeEdit Me, Target\r\n"
    "    End If\r\n"
    "End Sub\r\n"
)


def strip_xludf_image_xml(xlsx_path: Path) -> int:
    """Cleanly replace any Excel-rewritten `_xludf.IMAGE(` or `_xlfn.IMAGE(` back to pure `IMAGE(`
    in worksheet XML so Google Sheets & Excel both evaluate `=IMAGE(...)` with ZERO errors!"""
    changed = 0
    with zipfile.ZipFile(xlsx_path, "r") as zin:
        infos = zin.infolist()
        blobs = {info.filename: zin.read(info.filename) for info in infos}

    tmp = xlsx_path.with_suffix(".clean.tmp")
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zout:
        for info in infos:
            data = blobs[info.filename]
            if info.filename.startswith("xl/worksheets/sheet") and info.filename.endswith(".xml"):
                txt = data.decode("utf-8", errors="ignore")
                new_txt, n1 = re.subn(r"_xludf\.IMAGE\(", "IMAGE(", txt)
                new_txt, n2 = re.subn(r"_xlfn\.IMAGE\(", "IMAGE(", new_txt)
                if n1 or n2:
                    changed += (n1 + n2)
                    data = new_txt.encode("utf-8")
            zout.writestr(info, data)
    tmp.replace(xlsx_path)
    return changed


def _place_sprite_stack(ws, dst_rng, img_paths: list[str], prefix: str, initial_stage1to6: int):
    pad = 5.0
    side = max(16.0, min(dst_rng.Width - 2 * pad, dst_rng.Height - 2 * pad))
    left = dst_rng.Left + (dst_rng.Width - side) / 2.0
    top = dst_rng.Top + (dst_rng.Height - side) / 2.0
    for k in range(6):
        shp = ws.Shapes.AddPicture(
            Filename=img_paths[k], LinkToFile=False, SaveWithDocument=True,
            Left=left, Top=top, Width=side, Height=side,
        )
        shp.Name = f"{prefix}{k}"
        shp.Line.Visible = 0
        shp.LockAspectRatio = -1
        shp.Placement = 1
        shp.Visible = -1 if (k == initial_stage1to6 - 1) else 0


def _compile_pc_vocab(xl, v: VocabThemeDef, meta: dict, is_pro: bool):
    t0 = time.perf_counter()
    base_p = Path(meta["base_path"]).resolve()
    out_p = (PRO_DIR / f"{v.stem}_Pro.xlsm") if is_pro else (OFF_DIR / f"{v.stem}.xlsx")
    out_p.parent.mkdir(parents=True, exist_ok=True)
    if out_p.exists():
        out_p.unlink()

    img_paths = [str((ASSETS_DIR / v.slug / f"stage_{k}.png").resolve()) for k in range(6)]
    wb = xl.Workbooks.Open(str(base_p))
    try:
        xl.ScreenUpdating = False
        xl.EnableEvents = False
        xl.Calculation = -4135

        # 1. Embed 6 sprites in `_Assets!B2:B7`
        ws_a = wb.Worksheets(ASSETS_SHEET)
        ws_a.Visible = -1
        for k in range(6):
            c_obj = ws_a.Cells(2 + k, 2)
            side = min(c_obj.Width, c_obj.Height) - 5.0
            shp = ws_a.Shapes.AddPicture(
                Filename=img_paths[k], LinkToFile=False, SaveWithDocument=True,
                Left=c_obj.Left + (c_obj.Width - side) / 2.0,
                Top=c_obj.Top + (c_obj.Height - side) / 2.0,
                Width=side, Height=side,
            )
            shp.Name = f"ASSET_S{k}"
            shp.Line.Visible = 0
            shp.Placement = 1

        # 2. Native Excel 365 Checkboxes on Tab 1 & Tab 2
        ws_v = wb.Worksheets(VOCAB_SHEET)
        ws_p = wb.Worksheets(PRACTICE_SHEET)
        ws_s = wb.Worksheets(STATS_SHEET)
        ws_g = wb.Worksheets(GUIDE_SHEET)
        ws_c = wb.Worksheets(CALC_SHEET)

        for r_str in meta["checkbox_ranges_vocab"]:
            try:
                ws_v.Range(r_str).CellControl.SetCheckbox()
            except Exception:
                pass
        for r_str in meta["checkbox_ranges_practice"]:
            try:
                ws_p.Range(r_str).CellControl.SetCheckbox()
            except Exception:
                pass

        # Calculate stages first so sprites show live stage immediately!
        xl.Calculation = -4105
        xl.CalculateFullRebuild()
        st_hero = max(1, min(6, int(round(float(ws_c.Range("C6").Value2 or 1)))))
        st_prac = max(1, min(6, int(round(float(ws_c.Range("C7").Value2 or 1)))))

        # 3. Place Dynamic Sprites (Pro: Native Sprite Stacks; Offline: Dynamic Linked Pictures!)
        hc1, hc2 = meta["hero_c1"] + 1, meta["hero_c2"] + 1
        v_hero_rng = ws_v.Range(ws_v.Cells(6, hc1), ws_v.Cells(9, hc2))
        p_hero_rng = ws_p.Range("H5:H14")
        s_hero_rng = ws_s.Range("H5:H11")

        if is_pro:
            _place_sprite_stack(ws_v, v_hero_rng, img_paths, "SPR_VHERO_S", st_hero)
            _place_sprite_stack(ws_p, p_hero_rng, img_paths, "SPR_PHERO_S", st_prac)
            _place_sprite_stack(ws_s, s_hero_rng, img_paths, "SPR_SHERO_S", st_hero)
            for k in range(6):
                gdst = ws_g.Cells(17, 2 + k)
                side = min(gdst.Width, gdst.Height) - 8.0
                shp = ws_g.Shapes.AddPicture(
                    Filename=img_paths[k], LinkToFile=False, SaveWithDocument=True,
                    Left=gdst.Left + (gdst.Width - side) / 2.0,
                    Top=gdst.Top + (gdst.Height - side) / 2.0,
                    Width=side, Height=side,
                )
                shp.Name = f"Guide_Stage{k}"
                shp.Line.Visible = 0
                shp.Placement = 1
        else:
            # Offline dynamic Linked Pictures (0 macros, updates live as you tick!)
            wb.Names.Add(Name="Anim_VocabHero", RefersTo=f"=INDEX({ASSETS_SHEET}!$B$2:$B$7,{CALC_SHEET}!$C$6)")
            wb.Names.Add(Name="Anim_PracHero", RefersTo=f"=INDEX({ASSETS_SHEET}!$B$2:$B$7,{CALC_SHEET}!$C$7)")
            wb.Names.Add(Name="Anim_StatsHero", RefersTo=f"=INDEX({ASSETS_SHEET}!$B$2:$B$7,{CALC_SHEET}!$C$6)")
            src_cell = ws_a.Range("B2")
            for dst_ws, dst_r, fml, snm in (
                (ws_v, v_hero_rng, "=Anim_VocabHero", "Anim_VocabHero"),
                (ws_p, p_hero_rng, "=Anim_PracHero", "Anim_PracHero"),
                (ws_s, s_hero_rng, "=Anim_StatsHero", "Anim_StatsHero"),
            ):
                dst_ws.Activate()
                src_cell.Copy()
                time.sleep(0.05)
                pic = dst_ws.Pictures().Paste(Link=True)
                pic.Formula = fml
                pic.Name = snm
                pic.ShapeRange.Line.Visible = False
                pic.ShapeRange.LockAspectRatio = -1
                sc = min((dst_r.Width - 8.0) / pic.Width, (dst_r.Height - 8.0) / pic.Height)
                pic.Width = pic.Width * sc
                pic.Left = dst_r.Left + (dst_r.Width - pic.Width) / 2.0
                pic.Top = dst_r.Top + (dst_r.Height - pic.Height) / 2.0
                pic.Placement = 1
            for k in range(6):
                gdst = ws_g.Cells(17, 2 + k)
                side = min(gdst.Width, gdst.Height) - 8.0
                shp = ws_g.Shapes.AddPicture(
                    Filename=img_paths[k], LinkToFile=False, SaveWithDocument=True,
                    Left=gdst.Left + (gdst.Width - side) / 2.0,
                    Top=gdst.Top + (gdst.Height - side) / 2.0,
                    Width=side, Height=side,
                )
                shp.Name = f"Guide_Stage{k}"
                shp.Line.Visible = 0
                shp.Placement = 1
            xl.CutCopyMode = False

        # 4. Inject VBA + Pro Quick-Action Pill Buttons + Protection (Pro `.xlsm` ONLY)
        if is_pro:
            vbp = wb.VBProject
            vbp.VBComponents.Import(str(VBA_VOCAB_PATH.resolve()))

            for comp_name, code_str in (
                (wb.CodeName, WB_EVENT_VBA),
                (ws_v.CodeName, VOCAB_WS_EVENT_VBA),
                (ws_p.CodeName, PRAC_WS_EVENT_VBA),
            ):
                cm = vbp.VBComponents(comp_name).CodeModule
                if cm.CountOfLines > 0:
                    cm.DeleteLines(1, cm.CountOfLines)
                cm.AddFromString(code_str)

            bgr_pri = _hex_to_bgr(v.primary)
            bgr_dk = _hex_to_bgr(v.primary_dark)
            bgr_sft = _hex_to_bgr(v.soft)
            bgr_ink = _hex_to_bgr(v.ink)
            bgr_onp = _hex_to_bgr(v.on_primary)
            bgr_wht = _hex_to_bgr("#FFFFFF")

            # Tab 1 Pro Button Tray (Row 11, tray_c1..last_col)
            tray_rng = ws_v.Range(ws_v.Cells(11, meta["tray_c1"] + 1), ws_v.Cells(11, meta["last_col"] + 1))
            bh = min(21.0, max(16.0, tray_rng.Height - 5.0))
            bt = tray_rng.Top + (tray_rng.Height - bh) / 2.0
            gap = 5.0
            bw = min(150.0, (tray_rng.Width - 10.0 - 2 * gap) / 3.0)
            bx0 = tray_rng.Left + tray_rng.Width - (3 * bw + 2 * gap) - 5.0
            _add_pill_button(ws_v, "BTN_VOCAB_QUIZ", "🎲 Dò Bài Ngẫu Nhiên", bx0, bt, bw, bh,
                             bgr_pri, bgr_dk, bgr_onp, "BtnVocabQuiz", font_size=8.2)
            _add_pill_button(ws_v, "BTN_FX_TOGGLE", "✨ FX: BẬT", bx0 + bw + gap, bt, bw * 0.72, bh,
                             bgr_sft, bgr_pri, bgr_ink, "BtnVocabToggleFX", font_size=8.0)
            _add_pill_button(ws_v, "BTN_DEMO_FX", f"🎉 Hiệu Ứng {v.char_name}", bx0 + bw * 1.72 + 2 * gap, bt, bw * 1.12, bh,
                             bgr_wht, bgr_pri, bgr_dk, "BtnVocabDemoFX", font_size=8.0)

            # Tab 4 Guide CTA Pill Button on Section 5 bar (`B16:G16`)
            sec5 = ws_g.Range("B16:G16")
            gw = 162.0
            gh = min(21.0, sec5.Height - 5.0)
            _add_pill_button(ws_g, "BTN_GUIDE_DEMO", f"🎉 Thử Hiệu Ứng {v.char_name}",
                             sec5.Left + sec5.Width - gw - 6.0, sec5.Top + (sec5.Height - gh) / 2.0,
                             gw, gh, bgr_wht, bgr_sft, bgr_dk, "BtnVocabDemoFX", font_size=8.2)

            # Protect visible sheets while unlocking ALL user-editable vocab cells!
            ws_v.Cells.Locked = True
            ws_v.Range("B11").MergeArea.Locked = False
            if v.mode == "flashcard":
                ws_v.Range("E11").MergeArea.Locked = False
            if v.mode == "media":
                ws_v.Range("B8").MergeArea.Locked = False
            if v.mode == "exam":
                ws_v.Range("B8").MergeArea.Locked = False
            # Unlock data body C15:<last_col>114 excluding formula columns!
            body_r = ws_v.Range(ws_v.Cells(15, 3), ws_v.Cells(114, meta["last_col"] + 1))
            body_r.Locked = False
            try:
                body_r.SpecialCells(-4123).Locked = True
            except Exception:
                pass

            ws_p.Cells.Locked = True
            ws_p.Range("B5:E5").Locked = False
            ws_p.Range("B10:B14").Locked = False

            ws_s.Cells.Locked = True
            ws_g.Cells.Locked = True

            for wsp in (ws_v, ws_p, ws_s, ws_g):
                wsp.Protect(Password="", DrawingObjects=False, Contents=True,
                            Scenarios=False, UserInterfaceOnly=True, AllowFormattingCells=False)

        # Hide internal sheets cleanly
        ws_a.Visible = 0
        ws_c.Visible = 0
        for ws in (ws_g, ws_s, ws_p, ws_v):
            ws.Activate()
            xl.ActiveWindow.DisplayGridlines = False
            ws.Range("A1").Select()

        xl.CalculateFullRebuild()
        xl.ScreenUpdating = True
        xl.EnableEvents = True
        wb.SaveAs(str(out_p.resolve()), FileFormat=(52 if is_pro else 51))
    finally:
        xl.EnableEvents = True
        wb.Close(SaveChanges=False)

    extra = ""
    if is_pro:
        raw_m, uniq_m = deduplicate_xlsm_media(out_p, v.slug, n_stages=6)
        extra = f", media={uniq_m}/{raw_m}"
    dt = time.perf_counter() - t0
    tag = "VOCAB PRO" if is_pro else "VOCAB OFF"
    print(f"  ✓ [{tag}] {out_p.name} ({out_p.stat().st_size:,} B{extra}, {dt:.1f}s)", flush=True)


def main():
    tmp_dir = Path(tempfile.mkdtemp(prefix="vocab_chiikawa_build_"))
    pythoncom.CoInitialize()
    xl = None
    try:
        # 1. Google Sheets Edition (pure xlsxwriter -> ZERO _xludf.IMAGE!)
        print("=== 1) Building 5 Google Sheets Chiikawa Vocabulary Trackers (#96–#100) ===", flush=True)
        GS_DIR.mkdir(parents=True, exist_ok=True)
        for v in VOCAB_THEMES:
            p = GS_DIR / f"{v.stem}.xlsx"
            build_vocab_desktop_workbook(v, p, edition="gsheets")
            print(f"  ✓ [VOCAB GS] {p.name} ({p.stat().st_size:,} B)", flush=True)

        # 2. Build Base PC workbooks in %TEMP% & compile via Excel COM (5 Pro + 5 Offline)
        print("\n=== 2) Compiling 5 Pro (.xlsm) + 5 Offline (.xlsx) Chiikawa Vocabulary Trackers ===", flush=True)
        xl = win32.DispatchEx("Excel.Application")
        xl.Visible = False
        xl.DisplayAlerts = False
        try:
            xl.EnableAnimations = False
        except Exception:
            pass

        for v in VOCAB_THEMES:
            m_pro = build_vocab_desktop_workbook(v, tmp_dir / f"{v.stem}_pro_base.xlsx", edition="pro_xlsm")
            _compile_pc_vocab(xl, v, m_pro, is_pro=True)
            m_off = build_vocab_desktop_workbook(v, tmp_dir / f"{v.stem}_off_base.xlsx", edition="offline")
            _compile_pc_vocab(xl, v, m_off, is_pro=False)

        # 3. Mobile Portrait Edition (5 _Mobile.xlsx, strictly <= Col G, native checkboxes + strip _xludf.IMAGE!)
        print("\n=== 3) Building 5 Mobile Portrait Chiikawa Vocabulary Trackers (<= Col G) ===", flush=True)
        MOB_DIR.mkdir(parents=True, exist_ok=True)
        for v in VOCAB_THEMES:
            p_mob = (MOB_DIR / f"{v.stem}_Mobile.xlsx").resolve()
            m_mob = build_vocab_mobile_workbook(v, p_mob)
            wb = xl.Workbooks.Open(str(p_mob))
            try:
                ws_m = wb.Worksheets(MOB_MAIN_SHEET)
                ws_p = wb.Worksheets(MOB_PRAC_SHEET)
                for rr in m_mob["mob_chk_ranges"]:
                    try:
                        ws_m.Range(rr).CellControl.SetCheckbox()
                    except Exception:
                        pass
                for rr in m_mob["mob_prac_ranges"]:
                    try:
                        ws_p.Range(rr).CellControl.SetCheckbox()
                    except Exception:
                        pass
                for ws in wb.Worksheets:
                    if ws.Visible == -1:
                        ws.Activate()
                        xl.ActiveWindow.DisplayGridlines = False
                        ws.Range("A1").Select()
                ws_m.Activate()
                xl.CalculateFullRebuild()
                wb.Save()
            finally:
                wb.Close(SaveChanges=False)
            stripped = strip_xludf_image_xml(p_mob)
            print(f"  ✓ [VOCAB MOB] {p_mob.name} ({p_mob.stat().st_size:,} B, stripped_xludf={stripped})", flush=True)

        # 4. Also strip any `_xludf.IMAGE(` from Holiday Mobile #81-#95 so 100% of #81-#100 Mobile/GS are pure =IMAGE()!
        print("\n=== 4) Ensuring pure =IMAGE() (zero _xludf.IMAGE) across ALL #81-#95 Mobile files ===", flush=True)
        for mp in sorted(MOB_DIR.glob("8[1-9]_*_Mobile.xlsx")) + sorted(MOB_DIR.glob("9[0-5]_*_Mobile.xlsx")):
            n = strip_xludf_image_xml(mp)
            if n:
                print(f"  [CLEANED] {mp.name}: stripped {n} _xludf.IMAGE prefixes -> pure IMAGE()", flush=True)

    finally:
        if xl is not None:
            try:
                xl.Quit()
            except Exception:
                pass
            del xl
            gc.collect()
            time.sleep(1.0)
        pythoncom.CoUninitialize()
        shutil.rmtree(tmp_dir, ignore_errors=True)
    print("\n=== ALL 20 CHIIKAWA VOCABULARY TRACKERS BUILT CLEANLY! ===")


if __name__ == "__main__":
    main()
