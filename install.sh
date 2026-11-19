#!/usr/bin/env bash
# ============================================================================
#  Habit Tracker Collection v2.0 — Interactive Zero-Install Downloader (macOS/Linux)
#  Run in 1 line:
#    curl -fsSL https://raw.githubusercontent.com/Thitrongdan202/Habit-tracker-for-everyone-by-Dyu/main/install.sh | bash
# ============================================================================
set -euo pipefail

REPO_RAW="https://raw.githubusercontent.com/Thitrongdan202/Habit-tracker-for-everyone-by-Dyu/main"

# Colors (fallback gracefully if not a tty)
if [ -t 1 ]; then
  C_RESET=$'\033[0m'; C_BOLD=$'\033[1m'; C_CYAN=$'\033[36m'
  C_GREEN=$'\033[32m'; C_YELLOW=$'\033[33m'; C_MAGENTA=$'\033[35m'; C_RED=$'\033[31m'; C_DIM=$'\033[2m'
else
  C_RESET=""; C_BOLD=""; C_CYAN=""; C_GREEN=""; C_YELLOW=""; C_MAGENTA=""; C_RED=""; C_DIM=""
fi

FILES=(
  ""
  "01_Sunflower_Garden_Blush.xlsx"
  "02_Cactus_Bloom_Pastel_Weeks.xlsx"
  "03_Rainbow_Executive_Donuts.xlsx"
  "04_Sage_Botanical_Habit_And_Budget.xlsx"
  "05_Lavender_Dream_Wellness_Mood.xlsx"
  "06_Midnight_Navy_Blush_Focus.xlsx"
  "07_Sakura_Zen_Study_Planner.xlsx"
  "08_Ocean_Coral_Fitness_Energy.xlsx"
  "09_Matcha_Cafe_Daily_Routine.xlsx"
  "10_Aurora_Glow_RPG_Quest_Tracker.xlsx"
)

TITLES=(
  ""
  "Vườn Hướng Dương Pastel (Sunflower Garden)"
  "Xương Rồng Nở Hoa — 5 Tuần Pastel"
  "Cầu Vồng Dashboard & 5 Biểu Đồ Tròn"
  "Lá Xanh Thói Quen + Ngân Sách Cá Nhân"
  "Oải Hương Chăm Sóc Giấc Ngủ & Tâm Trạng"
  "Navy Tập Trung Deep Work & Điểm XP"
  "Hoa Anh Đào Học Tập & Giờ Focus"
  "San Hô Đại Dương Tập Luyện & Năng Lượng"
  "Matcha Cafe Lịch Trình Sáng / Tối"
  "Cực Quang RPG Thăng Cấp Thói Quen"
)

resolve_out_dir() {
  if [ -n "${HABIT_OUT_DIR:-}" ]; then
    printf "%s" "$HABIT_OUT_DIR"
    return
  fi
  local cwd
  cwd="$(pwd)"
  case "$cwd" in
    "/"|"/System"*|"/usr"*|"/bin"|"/sbin"|"/etc"|"/var"*|"/Library"*)
      printf "%s/Desktop/template" "$HOME"
      ;;
    *)
      printf "%s/template" "$cwd"
      ;;
  esac
}

validate_xlsx() {
  local f="$1"
  [ -f "$f" ] || return 1
  local sz
  sz=$(wc -c < "$f" | tr -d '[:space:]')
  [ "${sz:-0}" -ge 10240 ] || return 1
  local magic
  magic=$(head -c 2 "$f" 2>/dev/null || true)
  [ "$magic" = "PK" ] || return 1
  return 0
}

download_asset() {
  local rel="$1" dest="$2" check_xlsx="$3"
  local url="${REPO_RAW}/${rel}"
  mkdir -p "$(dirname "$dest")"
  if curl -fsSL "$url" -o "$dest"; then
    if [ "$check_xlsx" = "1" ] && ! validate_xlsx "$dest"; then
      rm -f "$dest"
      printf "  %s[LOI] File khong hop le (.xlsx): %s%s\n" "$C_RED" "$(basename "$dest")" "$C_RESET"
      return 1
    fi
    local sz_kb
    sz_kb=$(( $(wc -c < "$dest" | tr -d '[:space:]') / 1024 ))
    printf "  %s[OK] %s  (%s KB)%s\n" "$C_GREEN" "$(basename "$dest")" "$sz_kb" "$C_RESET"
    return 0
  else
    printf "  %s[LOI] Khong tai duoc: %s%s\n" "$C_RED" "$rel" "$C_RESET"
    return 1
  fi
}

OUT_DIR="$(resolve_out_dir)"
mkdir -p "$OUT_DIR"

printf "\n%s========================================================================%s\n" "$C_MAGENTA" "$C_RESET"
printf "%s   HABIT TRACKER COLLECTION v2.0 — BY DYU (100%% OFFLINE EXCEL .XLSX)%s\n" "$C_YELLOW" "$C_RESET"
printf "%s   Khong Python • Khong Macro • Khong Internet • Excel 2016 - 365%s\n" "$C_CYAN" "$C_RESET"
printf "%s========================================================================%s\n" "$C_MAGENTA" "$C_RESET"
printf "  %sThu muc luu file:%s %s\n\n" "$C_GREEN" "$C_RESET" "$OUT_DIR"
printf "  %sDANH SACH 10 MAU EXCEL OFFLINE (Mo la dung ngay tren moi may):%s\n" "$C_BOLD" "$C_RESET"
printf "  %s----------------------------------------------------------------------%s\n" "$C_DIM" "$C_RESET"
for i in 1 2 3 4 5 6 7 8 9 10; do
  printf "  [%-2d] %-42s — %s\n" "$i" "${FILES[$i]}" "${TITLES[$i]}"
done
printf "  %s----------------------------------------------------------------------%s\n" "$C_DIM" "$C_RESET"
printf "  %s[A]%s  Tai TOAN BO 10 mau Excel Offline (Download All)\n" "$C_GREEN" "$C_RESET"
printf "  %s[P]%s  Tai them ban Pro Offline Excel 365 + VBA Scripts (Optional)\n" "$C_CYAN" "$C_RESET"
printf "  %s[G]%s  Tai them ban Google Sheets Edition (Optional)\n" "$C_CYAN" "$C_RESET"
printf "  %s[0]%s  Thoat\n\n" "$C_DIM" "$C_RESET"
printf "  %sGoi y: Nhap 1 so (vd: 1), nhieu so (vd: 1,3,7), dai (vd: 1-5), hoac A%s\n" "$C_YELLOW" "$C_RESET"

CHOICE=""
if [ -n "${HABIT_CHOICE:-}" ]; then
  CHOICE="$HABIT_CHOICE"
  printf "  > Chon mau (auto): %s\n" "$CHOICE"
else
  printf "  > Nhap lua chon cua ban: "
  if [ -r /dev/tty ]; then
    read -r CHOICE </dev/tty
  else
    read -r CHOICE
  fi
fi

# Parse selection (numbers, comma/space lists, ranges a-b, A, P, G, 0)
SEL_IDS=()
DO_ALL=0; DO_PRO=0; DO_GS=0
CLEAN="${CHOICE//,/ }"
for tok in $CLEAN; do
  up="$(printf "%s" "$tok" | tr '[:lower:]' '[:upper:]')"
  case "$up" in
    0|Q|EXIT)
      printf "  %sTam biet! Chuc ban xay dung thoi quen thanh cong!%s\n" "$C_CYAN" "$C_RESET"
      exit 0
      ;;
    A|ALL) DO_ALL=1 ;;
    P|PRO) DO_PRO=1 ;;
    G|GSHEETS) DO_GS=1 ;;
    *-*)
      a="${up%%-*}"; b="${up##*-}"
      if [[ "$a" =~ ^[0-9]+$ ]] && [[ "$b" =~ ^[0-9]+$ ]]; then
        [ "$a" -gt "$b" ] && { t="$a"; a="$b"; b="$t"; }
        for ((n=a; n<=b; n++)); do
          [ "$n" -ge 1 ] && [ "$n" -le 10 ] && SEL_IDS+=("$n")
        done
      fi
      ;;
    *)
      if [[ "$up" =~ ^[0-9]+$ ]] && [ "$up" -ge 1 ] && [ "$up" -le 10 ]; then
        SEL_IDS+=("$up")
      fi
      ;;
  esac
done

if [ "$DO_ALL" -eq 1 ]; then
  SEL_IDS=(1 2 3 4 5 6 7 8 9 10)
fi

# Deduplicate SEL_IDS cleanly
UNIQUE_IDS=()
for id in "${SEL_IDS[@]:-}"; do
  [ -z "$id" ] && continue
  seen=0
  for u in "${UNIQUE_IDS[@]:-}"; do
    [ "$u" = "$id" ] && { seen=1; break; }
  done
  [ "$seen" -eq 0 ] && UNIQUE_IDS+=("$id")
done

QUEUE_REL=()
QUEUE_DST=()
QUEUE_CHK=()

for id in "${UNIQUE_IDS[@]:-}"; do
  [ -z "$id" ] && continue
  QUEUE_REL+=("templates/${FILES[$id]}")
  QUEUE_DST+=("${OUT_DIR}/${FILES[$id]}")
  QUEUE_CHK+=("1")
done

if [ "$DO_PRO" -eq 1 ]; then
  for i in 1 2 3 4 5 6 7 8 9 10; do
    pf="${FILES[$i]%.xlsx}_Pro.xlsx"
    QUEUE_REL+=("templates/pro_macro/${pf}")
    QUEUE_DST+=("${OUT_DIR}/pro_excel365_offline/${pf}")
    QUEUE_CHK+=("1")
  done
  for vf in HabitTrackerPro.bas SheetTrackerEvents.cls README_VBA.md; do
    QUEUE_REL+=("vba_scripts/${vf}")
    QUEUE_DST+=("${OUT_DIR}/vba_scripts/${vf}")
    QUEUE_CHK+=("0")
  done
fi

if [ "$DO_GS" -eq 1 ]; then
  for i in 1 2 3 4 5 6 7 8 9 10; do
    QUEUE_REL+=("templates/google_sheets_edition/${FILES[$i]}")
    QUEUE_DST+=("${OUT_DIR}/google_sheets_edition/${FILES[$i]}")
    QUEUE_CHK+=("1")
  done
fi

TOTAL="${#QUEUE_REL[@]}"
if [ "$TOTAL" -eq 0 ]; then
  printf "  %sKhong co lua chon hop le nao duoc chon. Vui long chay lai!%s\n" "$C_YELLOW" "$C_RESET"
  exit 0
fi

printf "\n  %sDang tai %d tep ve: %s ...%s\n" "$C_CYAN" "$TOTAL" "$OUT_DIR" "$C_RESET"
OK=0
for ((idx=0; idx<TOTAL; idx++)); do
  printf "  %s[%d/%d]%s " "$C_DIM" "$((idx+1))" "$TOTAL" "$C_RESET"
  if download_asset "${QUEUE_REL[$idx]}" "${QUEUE_DST[$idx]}" "${QUEUE_CHK[$idx]}"; then
    OK=$((OK + 1))
  fi
done

printf "\n%s========================================================================%s\n" "$C_MAGENTA" "$C_RESET"
printf "  %sHOAN TAT: Da tai thanh cong %d / %d tep!%s\n" "$C_GREEN" "$OK" "$TOTAL" "$C_RESET"
printf "  Thu muc:  %s\n" "$OUT_DIR"
printf "  %sCach dung: Nhan dup vao file .xlsx -> xem tab 'Huong Dan' -> tick ngay!%s\n" "$C_YELLOW" "$C_RESET"
printf "%s========================================================================%s\n" "$C_MAGENTA" "$C_RESET"

if [ "${HABIT_NO_OPEN:-0}" != "1" ]; then
  printf "  Mo thu muc 'template' ngay bay gio? (Y/n): "
  OPEN_ANS=""
  if [ -r /dev/tty ]; then
    read -r OPEN_ANS </dev/tty
  fi
  if [ -z "$OPEN_ANS" ] || [[ "$OPEN_ANS" =~ ^[Yy]$ ]]; then
    if command -v open >/dev/null 2>&1; then
      open "$OUT_DIR"
    elif command -v xdg-open >/dev/null 2>&1; then
      xdg-open "$OUT_DIR" >/dev/null 2>&1 &
    fi
  fi
fi
