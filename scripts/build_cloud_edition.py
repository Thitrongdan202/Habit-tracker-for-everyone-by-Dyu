"""
build_cloud_edition.py — Tier B Cloud & Google Sheets / Excel 365 generator (branch: version2).

Generates lightweight `.xlsx` workbooks in `templates/google_sheets_and_excel365/`
using `=IMAGE("https://raw.githubusercontent.com/Thitrongdan202/Habit-tracker-for-everyone-by-Dyu/version2/assets/...")`
and native cell checkboxes.

Run from repo root:
    python scripts/build_cloud_edition.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from excel_builder import BUILDERS

CLOUD_DIR = ROOT / "templates" / "google_sheets_and_excel365"


def main():
    CLOUD_DIR.mkdir(parents=True, exist_ok=True)
    print("Building 6 Tier-B Cloud & Google Sheets / Excel 365 templates (branch: version2)...")
    for stem, fn in BUILDERS:
        out = CLOUD_DIR / f"{stem}.xlsx"
        fn(out, universal=False)
        print(f"  ✓ {out.relative_to(ROOT)}  ({out.stat().st_size / 1024:.1f} KB)")
    print("All 6 Tier-B Cloud workbooks built successfully!")


if __name__ == "__main__":
    main()
