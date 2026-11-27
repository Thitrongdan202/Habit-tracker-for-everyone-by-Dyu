#!/usr/bin/env bash
# ============================================================================
#  Habit Tracker Collection v4.2 — Interactive Zero-Install Downloader (macOS/Linux)
#  Run in 1 line:
#    curl -fsSL https://raw.githubusercontent.com/Thitrongdan202/Habit-tracker-for-everyone-by-Dyu/main/install.sh | bash
# ============================================================================
set -euo pipefail

REPO_RAW="https://raw.githubusercontent.com/Thitrongdan202/Habit-tracker-for-everyone-by-Dyu/main"

if [ -t 1 ]; then
  C_RESET=$'\033[0m'; C_BOLD=$'\033[1m'; C_CYAN=$'\033[36m'
  C_GREEN=$'\033[32m'; C_YELLOW=$'\033[33m'; C_MAGENTA=$'\033[35m'; C_RED=$'\033[31m'; C_DIM=$'\033[2m'
else
  C_RESET=""; C_BOLD=""; C_CYAN=""; C_GREEN=""; C_YELLOW=""; C_MAGENTA=""; C_RED=""; C_DIM=""
fi

STEMS=(
  ""
  "01_Sunflower_Garden_Blush"
  "02_Cactus_Bloom_Pastel_Weeks"
  "03_Rainbow_Executive_Donuts"
  "04_Sage_Botanical_Habit_And_Budget"
  "05_Lavender_Dream_Wellness_Mood"
  "06_Midnight_Navy_Blush_Focus"
  "07_Sakura_Zen_Study_Planner"
  "08_Ocean_Coral_Fitness_Energy"
  "09_Matcha_Cafe_Daily_Routine"
  "10_Aurora_Glow_RPG_Quest_Tracker"
  "11_Velvet_Rose_Garden"
  "12_Blue_Tulip_Mint_Breeze"
  "13_Buttercream_Blossom_Bars"
  "14_Emerald_Forest_Gold_Stars"
  "15_Mocha_Rose_Terracotta_Sunflower"
  "16_Dream_Home_Architect_Builder"
  "17_Wildflower_Bloom_Daily_Mood"
  "18_Plum_Oak_Master_Suite"
  "19_Meadow_Emerald_Sunflower"
  "20_Cream_Alpaca_Cozy_Budget"
  "21_Blush_Alpaca_Flower_Crown"
  "22_Matcha_Alpaca_Meadow"
  "23_Bamboo_Panda_Zen_Garden"
  "24_Royal_Cat_Saving_Cash"
  "25_Ginger_Kitten_Basket_Routine"
  "26_Pastel_Purple_Royal_Cat"
  "27_Hatching_Chick_Icon_Studio"
  "28_Cotton_Candy_Jar_Sweet"
  "29_Watercolor_Rose_Bouquet"
  "30_Shiba_Inu_Happy_Bork"
  "31_Akita_Inu_Snow_Loyal"
  "32_Sakura_Blossom_Minimalist"
  "33_Peach_Mochi_Cat_Mood_Suite"
  "34_Fluffy_Bunny_Sticker_Pop"
  "35_Milk_Mocha_Bear_Sweet_Love"
  "36_Digimon_Veemon_Miracle"
  "37_Digimon_Agumon_Courage"
  "38_Digimon_Gatomon_Light"
  "39_Digimon_Gabumon_Friendship"
  "40_Digimon_Piyomon_Love"
  "41_Digimon_Patamon_Mythical"
  "42_Digimon_Palmon_Rose"
  "43_Digimon_Gomamon_Arctic"
  "44_Digimon_Guilmon_Crimson"
  "45_Digimon_Terriermon_Mint"
  "46_Digimon_Renamon_Kuzuhamon"
  "47_Digimon_Tentomon_Electro"
  "48_Capybara_Avocado_Zen"
  "49_Capybara_Yuzu_Onsen_Spa"
  "50_Capybara_Pip_Puddle_Besties"
  "51_Capybara_Boba_Lily_Pond"
  "52_Capybara_Bookworm_Study"
  "53_Capybara_Lofi_Picnic_Beats"
  "54_Capybara_Foodie_Snack_Club"
  "55_Capybara_Dino_Hoodie_Play"
  "56_Capybara_Apple_Orchard_Sweet"
  "57_Capybara_Pink_Cloud_Chill"
  "58_Capybara_Fairy_Party_Wish"
  "59_Capybara_SelfCare_GlowUp"
  "60_Capybara_Snapshot_Traveler"
  "61_Loopy_Red_Bow_Glow_Up"
  "62_Loopy_Taiyaki_Street_Snack"
  "63_Loopy_Piggy_Dessert_Cafe"
  "64_Loopy_Sauna_Sheep_Detox"
  "65_Loopy_Honey_Bee_KPI"
  "66_Loopy_Poolside_Duck_Chill"
  "67_Loopy_Fluffy_Commuter_Diary"
  "68_Loopy_Panda_Zen_Study"
  "69_Loopy_Ruffle_Sleep_Routine"
  "70_Loopy_Hair_Roller_GRWM"
  "71_Lotso_Strawberry_Harvest"
  "72_Lotso_Strawberry_Milk_Cafe"
  "73_Lotso_Berry_Flower_Crown"
  "74_Lotso_Overalls_Toy_Workshop"
  "75_Lotso_LoFi_Earphones_Flow"
  "76_Lotso_Mood_Detox_Comic"
  "77_Lotso_Floral_Sweet_Dreams"
  "78_Lotso_Daisy_Cheek_Glow"
  "79_Lotso_Bunny_Headband_Selfcare"
  "80_Lotso_Berry_Gift_Box_Party"
)

TITLES=(
  ""
  "Vườn Hướng Dương Pastel (Sunflower Garden)"
  "Xương Rồng Nở Hoa — 5 Tuần Pastel"
  "Cầu Vồng Dashboard & 5 Biểu Đồ Tròn"
  "Lá Xanh Thói Quen & Ngân Sách Cá Nhân"
  "Oải Hương Chăm Sóc Giấc Ngủ & Tâm Trạng"
  "Navy Tập Trung Deep Work & Điểm XP"
  "Hoa Anh Đào Học Tập & Giờ Focus"
  "San Hô Đại Dương Tập Luyện & Năng Lượng"
  "Matcha Cafe Lịch Trình Sáng / Tối"
  "Cực Quang RPG Thăng Cấp Thói Quen"
  "Vườn Hồng Nhung Tím Lavender (Velvet Rose)"
  "Tulip Xanh Lam — Dải Màu Mint Chanh"
  "Kem Bơ Biểu Đồ Cột Caramel & Hoa Nở"
  "Rừng Ngọc Bích & Sao Vàng (Gold Stars)"
  "Hướng Dương Mocha & Hồng Đất Terracotta"
  "Xây Ngôi Nhà Mơ Ước (6 Cấp Độ Kiến Trúc)"
  "Hoa Dại 5 Cánh & Tâm Trạng Mỗi Ngày"
  "Cây Sồi Tím Mận & Bảng Tuần/Tháng Toàn Diện"
  "Hướng Dương Đồng Cỏ Xanh Ngọc Lục Bảo"
  "Alpaca Kem Cozy Cafe (Khăn Len, Mũ Nồi & Latte)"
  "Alpaca Hồng Vườn Cổ Tích (Giỏ Hoa & Vòng Hoa)"
  "Alpaca Matcha Picnic (Yên Thêu & Mũ Cói)"
  "Gấu Trúc Mochi Tròn Xoe (Onigiri & Khăn Đỏ)"
  "Mèo Hoàng Gia Tiết Kiệm & Vương Quốc Mèo"
  "Mèo Cam Giỏ Mây & Bảng Xếp Hạng Thói Quen"
  "Mèo Ánh Sao Lavender (Trăng Khuyết & Mũ Nồi Sao)"
  "Gà Con Nở Trứng 6 Giai Đoạn (Studio)"
  "Hũ Kẹo Bông Gòn Pastel Hồng-Xanh"
  "Bó Hoa Hồng Màu Nước & Chánh Niệm"
  "Cún Shiba Inu Khăn Đỏ Karakusa & Xương Vàng"
  "Cún Akita Tuyết Trắng & Chuông Shimenawa"
  "Cây Hoa Anh Đào Tối Giản (Minimalist)"
  "Mèo Mochi Quýt Mikan + 6 Cảm Xúc & To-Do"
  "Thỏ Bông Sticker Pop 5 Màu Pastel"
  "Gấu Milk & Mocha + 5+1 Biểu Đồ Donut"
  "Digimon Veemon → Magnamon (7 Cấp Tiến Hóa)"
  "Digimon Agumon → WarGreymon (7 Cấp Tiến Hóa)"
  "Digimon Gatomon → LovelyAngemon (7 Cấp Tiến Hóa)"
  "Digimon Gabumon → MetalGarurumon (7 Cấp Tiến Hóa)"
  "Digimon Piyomon → Phoenixmon (7 Cấp Tiến Hóa)"
  "Digimon Patamon → Griffomon (7 Cấp Thần Thoại)"
  "Digimon Palmon → Rosemon (7 Cấp Tiên Hoa)"
  "Digimon Gomamon → AncientMegatheriummon (8 Cấp)"
  "Digimon Guilmon → Gallantmon Crimson (8 Cấp)"
  "Digimon Terriermon → MegaGargomon (7 Cấp)"
  "Digimon Renamon → Kuzuhamon Miko (8 Cấp)"
  "Digimon Tentomon → HerakleKabuterimon (7 Cấp)"
  "Capybara Bơ Xanh Vẽ Tay (Nước & Bữa Bơ Zen)"
  "Capybara Suối Nóng Yuzu (5 Donut & Thư Giãn Tối)"
  "Đôi Bạn Pip & Puddle (Hồng-Tím Bestie Bond)"
  "Capybara Hồ Sen Trà Sữa (Đếm Ly Boba Tuần)"
  "Capy & Chaptered (Giờ Học & Trang Sách)"
  "Capybara Lofi Picnic (Đếm Phút Flow & Playlist)"
  "Capybara Foodie Club (6 Mốc Mở Khóa Món Ngon)"
  "Capybara Áo Dino Xanh (Điểm Vui & 5 Thanh Pastel)"
  "Capybara Vườn Táo Đỏ (Đếm Táo & Biết Ơn)"
  "Capybara Mây Hồng Tối Giản (Minimalist Chill)"
  "Capybara Tiệc Tiên (5 Điều Ước Sao Tự Thắp Sáng)"
  "Capybara Self-Care GlowUp (3 Thẻ Sáng-Chiều-Tối)"
  "Capybara Lữ Hành (Nhật Ký Polaroid & Dấu Hộ Chiếu)"
  "Loopy Nơ Đỏ Glow-Up (Checklist 0→100% & Tự Tin)"
  "Loopy Mũ Bánh Cá Taiyaki & Xiên Dango 3 Màu"
  "Loopy Mũ Heo Tiệm Bánh Kem Cherry & Phô Mai"
  "Loopy Khăn Cừu Yangmeori Sauna (5 Donut Detox)"
  "Loopy Ong Chăm Chỉ KPI (Deep Work & Hũ Mật)"
  "Loopy Hồ Bơi Phao Vịt Vàng (Nước & 5 Thanh Hè)"
  "Loopy Mũ Bông Nhật Ký Đi Làm & Tan Làm Đúng Giờ"
  "Loopy Mũ Gấu Trúc Học Tập Zen (Phút & Trang Sách)"
  "Loopy Rèm Bèo Nơ Hồng (Giấc Ngủ Ngon 8 Tiếng)"
  "Loopy Cuốn Lô Mái GRWM (Trà Ấm & Soi Gương)"
  "Gấu Dâu Lotso Thu Hoạch Dâu Tây (Giỏ Dâu & Mắt Tim)"
  "Lotso Quán Sữa Dâu Kem Tươi & Bánh Shortcake"
  "Lotso Kết Vương Miện Hoa Cúc & Chùm Dâu Đỏ"
  "Lotso Quần Yếm Xưởng Đồ Chơi (Sticker & Tên Lửa)"
  "Lotso Tai Nghe Lo-Fi (Phút Deep Flow & Playlist)"
  "Lotso Giải Độc Stress Tia Sét → Mưa Tim (5 Donut)"
  "Lotso Hái Hoa Đỏ & Giấc Mơ Cừu Tím Pastel"
  "Lotso Hoa Cúc Trắng Cài Tai & Áp Má Nháy Mắt"
  "Lotso Bờm Tai Thỏ Spa Self-Care (Sáng-Ngày-Tối)"
  "Lotso Tiệc Hộp Quà Hồng, Cupcake & Confetti 100%"
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

validate_zip() {
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
  local rel="$1" dest="$2" check_zip="$3"
  local url="${REPO_RAW}/${rel}"
  mkdir -p "$(dirname "$dest")"
  if curl -fsSL "$url" -o "$dest"; then
    if [ "$check_zip" = "1" ] && ! validate_zip "$dest"; then
      rm -f "$dest"
      printf "  %s[LOI] File khong hop le: %s%s\n" "$C_RED" "$(basename "$dest")" "$C_RESET"
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

read_input() {
  local prompt="$1" out=""
  printf "%s" "$prompt"
  if [ -r /dev/tty ]; then
    read -r out </dev/tty
  else
    read -r out
  fi
  REPLY="$out"
}

OUT_DIR="$(resolve_out_dir)"
mkdir -p "$OUT_DIR"

printf "\n%s========================================================================%s\n" "$C_MAGENTA" "$C_RESET"
printf "%s   HABIT TRACKER COLLECTION v4.2 — BY DYU (80 THEMES × 4 EDITIONS)%s\n" "$C_YELLOW" "$C_RESET"
printf "%s   Turbo 6/7/8-Stage Native Sprite Engine • FX Suite • Ctrl+Z Undo%s\n" "$C_CYAN" "$C_RESET"
printf "%s========================================================================%s\n" "$C_MAGENTA" "$C_RESET"
printf "  %sThư mục lưu file:%s %s\n\n" "$C_GREEN" "$C_RESET" "$OUT_DIR"

printf "  %sBƯỚC 1 — CHỌN PHIÊN BẢN PHÙ HỢP (THEO THỨ TỰ ƯU TIÊN):%s\n" "$C_BOLD" "$C_RESET"
printf "  %s----------------------------------------------------------------------%s\n" "$C_DIM" "$C_RESET"
printf "  %s[1] Pro Interactive (.xlsm)  [⭐ KHUYÊN DÙNG SỐ 1 — EXCEL 365 TURBO v4.2]%s\n" "$C_GREEN" "$C_RESET"
printf "      %s-> Siêu tốc ~25–54ms + Full FX Nảy/Pháo hoa/Toast góc trái dưới + Ctrl+Z Undo%s\n" "$C_DIM" "$C_RESET"
printf "         %s+ Khóa bảo vệ công thức + Tự lưu Đa Ngày/Tháng/Năm (100%% Offline)!%s\n" "$C_DIM" "$C_RESET"
printf "  %s[2] Excel Universal Offline (.xlsx)  [Excel 2016/2019/2021/365]%s\n" "$C_CYAN" "$C_RESET"
printf "      %s-> Không Macro, 0 lỗi TRUE/FALSE trên Excel cũ, đủ hoạt ảnh offline!%s\n" "$C_DIM" "$C_RESET"
printf "  %s[3] Google Sheets Desktop (.xlsx + .gs)  [Beta — Đang thử nghiệm]%s\n" "$C_YELLOW" "$C_RESET"
printf "      %s-> Dùng online qua Google Drive (còn một số lỗi nhỏ / trễ 1–2s)!%s\n" "$C_DIM" "$C_RESET"
printf "  %s[4] Mobile Portrait (.xlsx + .gs)  [Early Beta — Còn thô sơ & còn lỗi]%s\n" "$C_MAGENTA" "$C_RESET"
printf "      %s-> Khổ dọc 8 cột đang thử nghiệm (chỉ mở bằng App Google Sheets)!%s\n" "$C_DIM" "$C_RESET"
printf "  %s[0] Thoát%s\n\n" "$C_DIM" "$C_RESET"

ED_CHOICE=""
if [ -n "${HABIT_EDITION:-}" ]; then
  ED_CHOICE="$HABIT_EDITION"
  printf "  > Chọn phiên bản (auto): %s\n" "$ED_CHOICE"
else
  read_input "  > Nhập phiên bản (1, 2, 3, 4/M — mặc định [1] Pro #1): "
  ED_CHOICE="${REPLY:-1}"
fi

ED_CHOICE="$(printf "%s" "$ED_CHOICE" | tr '[:lower:]' '[:upper:]')"
case "$ED_CHOICE" in
  0|Q|EXIT)
    printf "  %sTạm biệt! Chúc bạn xây dựng thói quen thành công!%s\n" "$C_CYAN" "$C_RESET"
    exit 0
    ;;
  M|MOBILE) ED_CHOICE="4" ;;
  1|2|3|4) ;;
  *) ED_CHOICE="1" ;;
esac

printf "\n  %sBƯỚC 2 — CHỌN MẪU THÓI QUEN (80 CHỦ ĐỀ LOTSO, LOOPY, CAPYBARA, DIGIMON & HOA LÁ):%s\n" "$C_BOLD" "$C_RESET"
printf "  %s----------------------------------------------------------------------%s\n" "$C_DIM" "$C_RESET"
printf "  %s--- 🍓 [v4.1] 10 BỘ GẤU DÂU LOTSO PASTEL COLLECTION (#71–#80) ---%s\n" "$C_MAGENTA" "$C_RESET"
for i in 71 72 73 74 75 76 77 78 79 80; do
  printf "  [%-2d] %-38s — %s\n" "$i" "${STEMS[$i]}" "${TITLES[$i]}"
done
printf "  %s--- 🎀 [v4.1] 10 BỘ HẢI LY LOOPY PASTEL COLLECTION (#61–#70) ---%s\n" "$C_YELLOW" "$C_RESET"
for i in 61 62 63 64 65 66 67 68 69 70; do
  printf "  [%-2d] %-38s — %s\n" "$i" "${STEMS[$i]}" "${TITLES[$i]}"
done
printf "  %s--- 🥑 13 BỘ CAPYBARA CHILL COLLECTION ĐỘC BẢN (#48–#60) ---%s\n" "$C_GREEN" "$C_RESET"
for i in 48 49 50 51 52 53 54 55 56 57 58 59 60; do
  printf "  [%-2d] %-38s — %s\n" "$i" "${STEMS[$i]}" "${TITLES[$i]}"
done
printf "  %s--- ⚡ 12 BỘ DIGIMON 7 & 8 CẤP TIẾN HÓA (#36–#47) ---%s\n" "$C_CYAN" "$C_RESET"
for i in 36 37 38 39 40 41 42 43 44 45 46 47; do
  printf "  [%-2d] %-38s — %s\n" "$i" "${STEMS[$i]}" "${TITLES[$i]}"
done
printf "  %s--- THÚ CƯNG SIÊU CUTE (Mochi Cat, Bunny, Milk & Mocha, Shiba, Akita, Alpaca...) ---%s\n" "$C_YELLOW" "$C_RESET"
for i in 21 22 23 25 26 27 30 31 33 34 35; do
  printf "  [%-2d] %-38s — %s\n" "$i" "${STEMS[$i]}" "${TITLES[$i]}"
done
printf "  %s--- HOA & THIÊN NHIÊN (Sakura Minimalist, Hướng Dương, Xương Rồng, Hồng Nhung...) ---%s\n" "$C_GREEN" "$C_RESET"
for i in 1 2 11 12 13 14 15 17 18 19 29 32; do
  printf "  [%-2d] %-38s — %s\n" "$i" "${STEMS[$i]}" "${TITLES[$i]}"
done
printf "  %s--- PHONG CÁCH & MỤC TIÊU (Dream Home, Candy Jar, Rainbow, Aurora RPG, Matcha...) ---%s\n" "$C_CYAN" "$C_RESET"
for i in 3 5 8 9 10 16 28; do
  printf "  [%-2d] %-38s — %s\n" "$i" "${STEMS[$i]}" "${TITLES[$i]}"
done
printf "  %s--- TÀI CHÍNH & TẬP TRUNG (Royal Cat Cash, Alpaca Budget, Sage Budget, Deep Work...) ---%s\n" "$C_MAGENTA" "$C_RESET"
for i in 4 6 7 20 24; do
  printf "  [%-2d] %-38s — %s\n" "$i" "${STEMS[$i]}" "${TITLES[$i]}"
done
printf "  %s----------------------------------------------------------------------%s\n" "$C_DIM" "$C_RESET"
printf "  %s[A]%s  Tải TOÀN BỘ 80 mẫu (Download All 80)\n" "$C_GREEN" "$C_RESET"
printf "  %s[0]%s  Thoát\n\n" "$C_DIM" "$C_RESET"
printf "  %sGợi ý: Nhập 1 số (vd: 71), nhiều số (vd: 61,70,78), dải (vd: 61-80), hoặc A%s\n" "$C_YELLOW" "$C_RESET"

CHOICE=""
if [ -n "${HABIT_CHOICE:-}" ]; then
  CHOICE="$HABIT_CHOICE"
  printf "  > Chọn mẫu (auto): %s\n" "$CHOICE"
else
  read_input "  > Nhập lựa chọn của bạn: "
  CHOICE="$REPLY"
fi

SEL_IDS=()
DO_ALL=0
CLEAN="${CHOICE//,/ }"
for tok in $CLEAN; do
  up="$(printf "%s" "$tok" | tr '[:lower:]' '[:upper:]')"
  case "$up" in
    0|Q|EXIT)
      printf "  %sTạm biệt! Chúc bạn xây dựng thói quen thành công!%s\n" "$C_CYAN" "$C_RESET"
      exit 0
      ;;
    A|ALL) DO_ALL=1 ;;
    *-*)
      a="${up%%-*}"; b="${up##*-}"
      if [[ "$a" =~ ^[0-9]+$ ]] && [[ "$b" =~ ^[0-9]+$ ]]; then
        [ "$a" -gt "$b" ] && { t="$a"; a="$b"; b="$t"; }
        for ((n=a; n<=b; n++)); do
          [ "$n" -ge 1 ] && [ "$n" -le 80 ] && SEL_IDS+=("$n")
        done
      fi
      ;;
    *)
      if [[ "$up" =~ ^[0-9]+$ ]] && [ "$up" -ge 1 ] && [ "$up" -le 80 ]; then
        SEL_IDS+=("$up")
      fi
      ;;
  esac
done

if [ "$DO_ALL" -eq 1 ]; then
  SEL_IDS=(1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80)
fi

UNIQUE_IDS=()
for id in "${SEL_IDS[@]:-}"; do
  [ -z "$id" ] && continue
  seen=0
  for u in "${UNIQUE_IDS[@]:-}"; do
    [ "$u" = "$id" ] && { seen=1; break; }
  done
  [ "$seen" -eq 0 ] && UNIQUE_IDS+=("$id")
done

if [ "${#UNIQUE_IDS[@]}" -eq 0 ]; then
  printf "  %sKhông có mẫu nào được chọn. Vui lòng chạy lại!%s\n" "$C_YELLOW" "$C_RESET"
  exit 0
fi

QUEUE_REL=()
QUEUE_DST=()
QUEUE_CHK=()
SUB_DIR=""
HINT=""

if [ "$ED_CHOICE" = "1" ]; then
  SUB_DIR="${OUT_DIR}/pro_macro"
  for id in "${UNIQUE_IDS[@]}"; do
    fn="${STEMS[$id]}_Pro.xlsm"
    QUEUE_REL+=("templates/pro_macro/${fn}")
    QUEUE_DST+=("${SUB_DIR}/${fn}")
    QUEUE_CHK+=("1")
  done
  HINT="Mở file .xlsm -> bấm 'Enable Content' 1 lần -> bấm 'Thử Hiệu Ứng Pro' trên tab Hướng Dẫn!"
elif [ "$ED_CHOICE" = "2" ]; then
  SUB_DIR="${OUT_DIR}/excel_universal_offline"
  for id in "${UNIQUE_IDS[@]}"; do
    fn="${STEMS[$id]}.xlsx"
    QUEUE_REL+=("templates/excel_universal_offline/${fn}")
    QUEUE_DST+=("${SUB_DIR}/${fn}")
    QUEUE_CHK+=("1")
  done
  HINT="Nhấp đúp file .xlsx -> dùng ngay 100% Offline, không Macro, chạy mọi Excel 2016–365!"
elif [ "$ED_CHOICE" = "3" ]; then
  SUB_DIR="${OUT_DIR}/google_sheets_edition"
  for id in "${UNIQUE_IDS[@]}"; do
    fn="${STEMS[$id]}.xlsx"
    QUEUE_REL+=("templates/google_sheets_edition/${fn}")
    QUEUE_DST+=("${SUB_DIR}/${fn}")
    QUEUE_CHK+=("1")
  done
  QUEUE_REL+=("scripts/google_sheets_1click_setup.gs" "docs/GOOGLE_SHEETS_GUIDE.md")
  QUEUE_DST+=("${SUB_DIR}/google_sheets_1click_setup.gs" "${SUB_DIR}/GOOGLE_SHEETS_GUIDE.md")
  QUEUE_CHK+=("0" "0")
  HINT="Tải file lên Google Sheets -> dán google_sheets_1click_setup.gs vào Apps Script -> Run setupHabitTracker()!"
else
  SUB_DIR="${OUT_DIR}/mobile_portrait_sheets"
  for id in "${UNIQUE_IDS[@]}"; do
    fn="${STEMS[$id]}_Mobile.xlsx"
    QUEUE_REL+=("templates/mobile_portrait_sheets/${fn}")
    QUEUE_DST+=("${SUB_DIR}/${fn}")
    QUEUE_CHK+=("1")
  done
  QUEUE_REL+=("scripts/google_sheets_1click_setup.gs" "docs/GOOGLE_SHEETS_GUIDE.md")
  QUEUE_DST+=("${SUB_DIR}/google_sheets_1click_setup.gs" "${SUB_DIR}/GOOGLE_SHEETS_GUIDE.md")
  QUEUE_CHK+=("0" "0")
  HINT="Tải *_Mobile.xlsx lên Google Drive -> mở bằng App Google Sheets trên điện thoại & dán .gs 1 lần!"
fi

TOTAL="${#QUEUE_REL[@]}"
printf "\n  %sĐang tải %d tệp về: %s ...%s\n" "$C_CYAN" "$TOTAL" "$SUB_DIR" "$C_RESET"
OK=0
for ((idx=0; idx<TOTAL; idx++)); do
  printf "  %s[%d/%d]%s " "$C_DIM" "$((idx+1))" "$TOTAL" "$C_RESET"
  if download_asset "${QUEUE_REL[$idx]}" "${QUEUE_DST[$idx]}" "${QUEUE_CHK[$idx]}"; then
    OK=$((OK + 1))
  fi
done

printf "\n%s========================================================================%s\n" "$C_MAGENTA" "$C_RESET"
printf "  %sHOÀN TẤT: Đã tải thành công %d / %d tệp!%s\n" "$C_GREEN" "$OK" "$TOTAL" "$C_RESET"
printf "  Thư mục:   %s\n" "$SUB_DIR"
printf "  %sCách dùng: %s%s\n" "$C_YELLOW" "$HINT" "$C_RESET"
printf "%s========================================================================%s\n" "$C_MAGENTA" "$C_RESET"

if [ "${HABIT_NO_OPEN:-0}" != "1" ]; then
  read_input "  Mở thư mục lưu file ngay bây giờ? (Y/n): "
  OPEN_ANS="$REPLY"
  if [ -z "$OPEN_ANS" ] || [[ "$OPEN_ANS" =~ ^[Yy]$ ]]; then
    if command -v open >/dev/null 2>&1; then
      open "$SUB_DIR"
    elif command -v xdg-open >/dev/null 2>&1; then
      xdg-open "$SUB_DIR" >/dev/null 2>&1 &
    fi
  fi
fi
