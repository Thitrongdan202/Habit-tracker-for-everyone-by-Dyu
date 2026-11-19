"""
build_cloud_edition.py — Builds:
  1. Google Sheets Edition (10 files) -> `templates/google_sheets_edition/01..10_*.xlsx`
     Uses `=IMAGE("https://raw.githubusercontent.com/Thitrongdan202/Habit-tracker-for-everyone-by-Dyu/main/assets/<slug>/stage_...")`
     with every day column referencing its own `_Calc` stage cell.
  2. Pro Excel 365 Offline Edition (10 files) -> `templates/pro_macro/01..10_*_Pro.xlsx`
     Uses 100% offline embedded `_Sprites` + native colored Excel 365 checkboxes (copy-anywhere, 0ms!).

Run from repo root:
    python scripts/build_cloud_edition.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from excel_builder import BUILDERS

GS_DIR = ROOT / "templates" / "google_sheets_edition"
PRO_DIR = ROOT / "templates" / "pro_macro"


def main():
    GS_DIR.mkdir(parents=True, exist_ok=True)
    PRO_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Building {len(BUILDERS)} Google Sheets Edition templates (main/assets URLs)...", flush=True)
    for stem, fn in BUILDERS:
        out = GS_DIR / f"{stem}.xlsx"
        fn(out, universal=False, pro_365_offline=False)
        print(f"  ✓ {out.relative_to(ROOT)}  ({out.stat().st_size / 1024:.1f} KB)", flush=True)

    print(f"\nBuilding {len(BUILDERS)} Pro Excel 365 Offline templates (embedded sprites, copy-anywhere)...", flush=True)
    for stem, fn in BUILDERS:
        out = PRO_DIR / f"{stem}_Pro.xlsx"
        fn(out, universal=False, pro_365_offline=True)
        print(f"  ✓ {out.relative_to(ROOT)}  ({out.stat().st_size / 1024:.1f} KB)", flush=True)

    print("\nAll Google Sheets & Pro Offline workbooks built successfully!", flush=True)


if __name__ == "__main__":
    main()
