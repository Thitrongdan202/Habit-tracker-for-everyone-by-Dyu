# ⚡ Habit Tracker Collection for Everyone — by Dyu (v3.7 — 40 Themes × 4 Editions)

> **Bộ sưu tập 40 mẫu Habit Tracker thẩm mỹ chuẩn Digital Planner — Đủ 4 phiên bản cho Máy tính & Điện thoại (160 file hoàn chỉnh + 245 ảnh hoạt ảnh: 35 chủ đề 6 giai đoạn & 5 chủ đề Digimon 7 giai đoạn tiến hóa)!**
> **MỚI v3.7 — BỘ SƯU TẬP DIGIMON 7 CẤP TIẾN HÓA (`#36`–`#40`):** Bổ sung **5 mẫu Digimon chuẩn canon** (*Veemon → Magnamon*, *Agumon → WarGreymon*, *Gatomon → LovelyAngemon*, *Gabumon → MetalGarurumon*, *Piyomon → Phoenixmon*) mở rộng động cơ **Turbo Native Sprite Engine** lên **7 giai đoạn tiến hóa (`0% → 1–19% → 20–39% → 40–59% → 60–79% → 80–99% → 100% Mega ✨`)** trên đủ 4 phiên bản! Đổi Tháng chỉ **~29–54 ms**, đổi Ngày **~4–5 ms**, đầy đủ **FX Suite, `Ctrl+Z` / `↩ Undo` & khóa bảo vệ công thức (`UserInterfaceOnly`)**!

![Version 3.7](https://img.shields.io/badge/Version-3.7_40_Themes_x_4_Editions-1D6FE2?style=for-the-badge)
![Pro #1 Recommended](https://img.shields.io/badge/⭐_RECOMMENDED_%231-Pro_Interactive_.XLSM_Turbo_v3.7-217346?style=for-the-badge&logo=microsoftexcel&logoColor=white)
![Zero Macro Offline](https://img.shields.io/badge/Offline_No--Macro-.XLSX_Excel_2016--365-4E9F76?style=for-the-badge)
![Google Sheets](https://img.shields.io/badge/Google_Sheets-1--Click_Script_v3.7-34A853?style=for-the-badge&logo=googlesheets&logoColor=white)
![Mobile Portrait](https://img.shields.io/badge/Mobile_Portrait-iOS_%26_Android_0_Scroll-9E9AD1?style=for-the-badge)

---

## ⚡ KHUYÊN DÙNG SỐ 1: Phiên Bản `Pro Interactive (.xlsm)` — Turbo Engine & FX Suite v3.7

Nếu bạn dùng **Microsoft Excel trên Windows hoặc macOS**, hãy chọn ngay **`[1] Pro Interactive (.xlsm)`** trong [`templates/pro_macro/`](templates/pro_macro/) để trải nghiệm tốc độ mượt như **App Desktop gốc** hoàn toàn 100% Offline:

- **🚀 Động cơ v3.7 Turbo Performance Engine (Hỗ trợ cả 6 giai đoạn & 7 giai đoạn Digimon — Nhanh gấp 20×–80×!):**
  - **Native Pre-Placed Sprite Stacks + Nén Đúng 6 hoặc 7 PNG (`xl/media/`):** Bỏ hoàn toàn Camera-Tool Linked Pictures gây giật lag GDI; thay bằng cụm ảnh PNG gốc siêu nét + bộ đệm so sánh thay đổi (`Stage-Diff Cache`) & tham chiếu Shape O(1)!
  - **Chỉ mục `_Database` O(1) thuần VBA (`Collection`, tương thích cả Windows & macOS Excel) + `.Value2` + Lazy-Flush:** Tick ô Checkbox **KHÔNG ghi `_Database`** (tự động flush khi đổi Tháng/Ngày/Năm, mở tab Tổng Kết Năm, hoặc Lưu/Đóng file!).
  - **🛡️ Hoàn tác `Ctrl+Z` Thực Thụ & Khóa Bảo Vệ Công Thức (`UserInterfaceOnly:=True`):** Giữ snapshot trước mỗi thao tác tick/kéo-fill để bấm **`Ctrl+Z`** hoặc nút **`↩ Undo`** khôi phục tức thì cả dữ liệu lẫn sprite; đồng thời khóa an toàn dòng `TOTAL • TỔNG KẾT` (Row 37) & toàn bộ ô công thức để kéo thả checkbox không bao giờ ghi đè hỏng công thức!
  - **Giữ nguyên tính năng tự đổi ảnh trong `_Assets`:** Chỉ cần dán 6 ảnh mới vào `_Assets!B2:B7` (hoặc 7 ảnh vào `_Assets!B2:B8` cho Digimon) rồi bấm nút **`🔄 Đồng bộ 6/7 ảnh mới (SyncSprites)`** 1 chạm!
- **🎉 Giữ nguyên 100% Bộ Hiệu Ứng Sống Động Pro (Bật/Tắt 1 chạm ngay trên sheet!):**
  1. **Hero Mascot Bounce (`PlayHeroBounce`):** Linh vật / Digimon nảy nhẹ đầy hứng khởi mỗi khi đạt **100% Ngày**, hoàn thành **100% Nhiệm Vụ Ngày**, hoặc tick xong **Mục Tiêu Năm**!
  2. **Pastel Sparkle / Heart / Star Burst (`PlaySparkleBurst`):** Pháo hoa sao & trái tim phối đúng màu chủ đề bùng nổ quanh Hero khi chạm mốc **100% Perfect Day** hoặc chuỗi **7 / 14 / 21 / 30 ngày** (tự dọn 100% hình thừa — 0 rác!).
  3. **Floating Toast Banner (`ShowToast`):** Thông báo tiếng Việt góc trên-phải tái sử dụng O(1) & tự ẩn sau 2 giây (tuyệt đối không bật `MsgBox` chắn tay!).
  4. **Nút Quick-Action Pastel 1 Chạm:** **`◀ Tháng` · `Tháng ▶` · `✨ FX: BẬT/TẮT` · `↩ Undo`** ngay góc trái bảng Tracker, **`◀ Hôm qua` · `📅 Hôm nay` · `Ngày mai ▶`** trên `📝 Nhiệm Vụ Ngày`, nút **`🎉 Thử Hiệu Ứng Pro`** trên `📖 Hướng Dẫn`, và **`🔄 Đồng bộ ảnh mới`** trên `_Assets`!

### 📊 Benchmark Tốc Độ Thực Tế Excel COM (`Linked Pictures cũ` vs `v3.7 Turbo`)

Đo thực tế trên Microsoft Excel (`EnableEvents = True`, `Calculation = Automatic`):

| Thao tác thực tế | Linked Pictures cũ | `01_Sunflower` **Turbo** | `36_Digimon_Veemon` **v3.7 (7-Stage)** | Tăng tốc |
|---|---:|---:|---:|---:|
| **1. Tick 1 ô Checkbox (`Monthly Tracker`)** | 347.3 ms | **42.7 ms** | **< 40 ms** | **~8–10× nhanh hơn** |
| **2a. Đổi Tháng bằng Dropdown (`B3`)** | 4,137.1 ms | **141.6 ms** | **29 – 54 ms** | **~75–140× nhanh hơn!** |
| **2b. Đổi Tháng bằng Nút 1 chạm (`◀ / ▶`)** | 4,137.1 ms | **51.3 ms** | **21 – 41 ms** | **~80–190× nhanh hơn!** |
| **3. Đổi Ngày `📝 Nhiệm Vụ Ngày` (`21 ↔ 22`)** | 2,918.2 ms | **46.5 ms** | **4 – 5 ms** | **~60–580× nhanh hơn!** |
| **4. Đổi Năm `🏆 Tổng Kết Năm` (`2026 ↔ 2027`)** | 317.2 ms | **74.9 ms** | **13 – 15 ms** | **~21× nhanh hơn!** |
| **Số ảnh nén trong `xl/media/`** | 54 bản sao | **6 PNG duy nhất** | **7 PNG duy nhất** | **Siêu gọn nhẹ!** |

---

## ⚡ Cài Đặt & Tải Nhanh Bằng 1 Dòng Lệnh (Interactive Installer v3.7)

Chạy **1 dòng lệnh duy nhất** — trình cài đặt dẫn bạn chọn đúng phiên bản theo thứ tự ưu tiên (`[1] Pro #1`, `[2] Excel Offline`, `[3] Google Sheets Desktop`, `[4] Mobile Portrait`) và chọn **40 mẫu phân nhóm sẵn** (`36`, `36-40`, `32,33,35,36`, hoặc `A` tải toàn bộ **40 mẫu**) vào thư mục `template/`:

### 🪟 Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/Thitrongdan202/Habit-tracker-for-everyone-by-Dyu/main/install.ps1 | iex
```

### 🍎 macOS / 🐧 Linux (Terminal)
```bash
curl -fsSL https://raw.githubusercontent.com/Thitrongdan202/Habit-tracker-for-everyone-by-Dyu/main/install.sh | bash
```

> **Người dùng cuối KHÔNG cần cài Python!** Tải xong chỉ cần nhấp đúp mở file bằng Microsoft Excel (bấm **Enable Content** 1 lần cho bản Pro) hoặc tải lên Google Sheets và bắt đầu tick ngay!

---

## 🧭 Chọn Đúng Phiên Bản Phù Hợp (Theo Thứ Tự Ưu Tiên — 160 File)

| Thứ tự | Phiên bản | Thư mục | Số tab | Điểm nổi bật | Phù hợp với |
|---|---|---|---|---|---|
| **#1 ⭐** | **⚡ Pro Interactive (`.xlsm`)** *(Khuyên dùng #1)* | [`templates/pro_macro/`](templates/pro_macro/) | **5 tab** | **Turbo Engine & FX Suite v3.7** (Native Sprite Stacks 6/7 PNG siêu tốc ~29–54ms + Bounce + Sparkle Burst + Toast + `Ctrl+Z` / `↩ Undo` + Khóa bảo vệ dòng công thức + O(1) Lazy-Flush `_Database`) — 100% Offline! | **Excel Desktop (Windows & Mac)** — trải nghiệm đẹp, nhanh và mượt nhất! |
| **#2** | **✨ Excel Universal Offline (`.xlsx`)** | [`templates/excel_universal_offline/`](templates/excel_universal_offline/) | **5 tab** | **KHÔNG Macro / 0 cảnh báo bảo mật**, dùng **Form Control Checkboxes** ẩn sạch `TRUE/FALSE` (`;;;`), chạy mọi đời **Excel 2016–365 Win/Mac** + đủ 54–55 hoạt ảnh offline! | Máy công ty chặn Macro hoặc dùng Excel 2016/2019/2021 không cần VBA |
| **#3** | **☁️ Google Sheets Desktop (`.xlsx` + `.gs`)** | [`templates/google_sheets_edition/`](templates/google_sheets_edition/) | **5 tab** | Gọn 5 tab + `_Database` + hoạt ảnh `=IMAGE()` động 6/7 giai đoạn. Chạy [`google_sheets_1click_setup.gs`](scripts/google_sheets_1click_setup.gs) 1 lần → **Checkbox Pastel & tự lưu từng Ngày + 12 Tháng** trên Cloud! | Dùng online trên trình duyệt & đồng bộ Google Drive |
| **#4** | **📱 Mobile Portrait (`.xlsx` + `.gs`)** | [`templates/mobile_portrait_sheets/`](templates/mobile_portrait_sheets/) | **4 tab** | **Khổ dọc 8 cột `B:I` riêng cho iPhone/Android (0 cuộn ngang!)**, gồm tab **`📝 Việc Hôm Nay`**, ô tick lớn `38pt` dễ chạm ngón cái & tự lưu từng Tuần/Ngày! | Check-in thói quen & việc đột xuất 1 chạm ngay trên điện thoại |

---

## ⚡ MỚI v3.7 — Bộ Sưu Tập Digimon 7-Stage Evolution (`#36` – `#40`)

Mỗi ngày tick thói quen sẽ tiến hóa nhân vật Digimon chuẩn canon qua **7 giai đoạn đầy đủ**: `0% Digi-Egg` → `1–19% Baby I` → `20–39% Baby II` → `40–59% Rookie` → `60–79% Champion / Armor` → `80–99% Ultimate` → **`100% Mega ✨`** — kèm bảng **Crest Digivice Breakdown** thống kê số ngày đạt từng dạng & thẻ **Current Form Power Meter**!

### 36. ⚡ Digimon Veemon Miracle — `Digi-Egg → Chibomon → DemiVeemon → Veemon → Flamedramon → Paildramon → Magnamon`
![Digimon Veemon Miracle Tracker](previews/36_digimon_veemon_tracker.png)
<details>
<summary>📸 Xem thêm: Hướng Dẫn Tiến Hóa 7 Giai Đoạn, Đại Sảnh Kỳ Tích Veemon, Nhiệm Vụ Ngày & Yearly Goals</summary>

![Veemon 7-Stage Guide](previews/36_digimon_veemon_guide.png)
![Veemon Annual Achievements](previews/36_digimon_veemon_annual_achievements.png)
![Veemon Daily Tasks](previews/36_digimon_veemon_daily_tasks.png)
![Veemon Yearly Goals](previews/36_digimon_veemon_yearly_goals.png)

</details>

### 37. 🔥 Digimon Agumon Courage — `Digi-Egg → Botamon → Koromon → Agumon → Greymon → MetalGreymon → WarGreymon`
![Digimon Agumon Courage Tracker](previews/37_digimon_agumon_tracker.png)
<details>
<summary>📸 Xem thêm: Đại Sảnh Dũng Khí Agumon & Nhiệm Vụ Ngày</summary>

![Agumon Annual Achievements](previews/37_digimon_agumon_annual_achievements.png)
![Agumon Daily Tasks](previews/37_digimon_agumon_daily_tasks.png)

</details>

### 38. ✨ Digimon Gatomon Light — `Digi-Egg → YukimiBotamon → Nyaromon → Salamon → Gatomon → Angewomon → LovelyAngemon`
![Digimon Gatomon Light Tracker](previews/38_digimon_gatomon_tracker.png)

### 39. ❄️ Digimon Gabumon Friendship — `Digi-Egg → Punimon → Tsunomon → Gabumon → Garurumon → WereGarurumon → MetalGarurumon`
![Digimon Gabumon Friendship Tracker](previews/39_digimon_gabumon_tracker.png)

### 40. ❤️ Digimon Piyomon Love — `Digi-Egg → Nyokimon → Yokomon → Biyomon → Birdramon → Garudamon → Phoenixmon`
![Digimon Piyomon Love Tracker](previews/40_digimon_piyomon_tracker.png)

<details>
<summary>📱 Xem 5 Màn Hình Điện Thoại Khổ Dọc Digimon (`#36`–`#40` — 0 Cuộn Ngang!)</summary>

<table>
  <tr>
    <td align="center"><img src="previews/mobile_36_digimon_veemon.png" width="165" alt="Mobile Veemon"/><br/><sub><b>⚡ Veemon Miracle</b></sub></td>
    <td align="center"><img src="previews/mobile_37_digimon_agumon.png" width="165" alt="Mobile Agumon"/><br/><sub><b>🔥 Agumon Courage</b></sub></td>
    <td align="center"><img src="previews/mobile_38_digimon_gatomon.png" width="165" alt="Mobile Gatomon"/><br/><sub><b>✨ Gatomon Light</b></sub></td>
    <td align="center"><img src="previews/mobile_39_digimon_gabumon.png" width="165" alt="Mobile Gabumon"/><br/><sub><b>❄️ Gabumon Friend</b></sub></td>
    <td align="center"><img src="previews/mobile_40_digimon_piyomon.png" width="165" alt="Mobile Piyomon"/><br/><sub><b>❤️ Piyomon Love</b></sub></td>
  </tr>
</table>

</details>

---

## 🎀 Showcase 4 Mẫu Signature (`#32` – `#35`)

### 35. 🐻 Milk & Mocha Bear Sweet Love — 5 Biểu Đồ Tròn Tuần + 1 Tổng Tháng
![Milk & Mocha Bear Sweet Love](previews/35_milk_mocha_tracker.png)
<details>
<summary>📸 Xem thêm: Nhiệm Vụ Ngày (Nút ◀ Hôm qua / Hôm nay / Ngày mai ▶), Yearly Goals & Đại Sảnh Milk & Mocha</summary>

![Milk & Mocha Daily Tasks](previews/35_milk_mocha_daily_tasks.png)
![Milk & Mocha Yearly Goals](previews/35_milk_mocha_yearly_goals.png)
![Milk & Mocha Annual Achievements](previews/35_milk_mocha_annual_achievements.png)

</details>

### 33. 🐱 Peach Mochi Cat & Mood Suite — Hộp Cam + Nhật Ký 6 Cảm Xúc + Quick To-Do
![Peach Mochi Cat Mood Suite](previews/33_mochi_cat_tracker.png)
<details>
<summary>📸 Xem thêm: Nhiệm Vụ Ngày & Đại Sảnh Mèo Mochi</summary>

![Mochi Cat Daily Tasks](previews/33_mochi_cat_daily_tasks.png)
![Mochi Cat Annual Achievements](previews/33_mochi_cat_annual_achievements.png)

</details>

### 34. 🐰 Fluffy Bunny Sticker Pop — 5 Dải Màu Pastel & Bunny Progress Ring
![Fluffy Bunny Sticker Pop](previews/34_fluffy_bunny_tracker.png)
<details>
<summary>📸 Xem thêm: Đại Sảnh Thỏ Bông Sticker Pop</summary>

![Fluffy Bunny Annual Achievements](previews/34_fluffy_bunny_annual_achievements.png)

</details>

### 32. 🌸 Sakura Blossom Minimalist — Cây Hoa Anh Đào Tối Giản Tinh Khôi
![Sakura Blossom Minimalist](previews/32_sakura_min_tracker.png)
<details>
<summary>📸 Xem thêm: Đại Sảnh Rừng Anh Đào Tối Giản</summary>

![Sakura Minimalist Annual Achievements](previews/32_sakura_min_annual_achievements.png)

</details>

---

## 📱 Xem Nhanh Bản Điện Thoại Khổ Dọc (Mobile Portrait — 0 Cuộn Ngang!)

<table>
  <tr>
    <td align="center"><img src="previews/mobile_35_milk_mocha.png" width="205" alt="Mobile Milk & Mocha"/><br/><sub><b>🐻 Milk & Mocha Portrait</b></sub></td>
    <td align="center"><img src="previews/mobile_33_mochi_cat.png" width="205" alt="Mobile Mochi Cat"/><br/><sub><b>🐱 Mochi Cat Portrait</b></sub></td>
    <td align="center"><img src="previews/mobile_34_fluffy_bunny.png" width="205" alt="Mobile Fluffy Bunny"/><br/><sub><b>🐰 Fluffy Bunny Portrait</b></sub></td>
    <td align="center"><img src="previews/mobile_32_sakura_min.png" width="205" alt="Mobile Sakura Min"/><br/><sub><b>🌸 Sakura Min Portrait</b></sub></td>
  </tr>
</table>

<details>
<summary>📸 Xem thêm màn hình Mobile Portrait (Shiba, Akita, Alpaca, Royal Cat, Sunflower, Daily Tasks)</summary>

<table>
  <tr>
    <td align="center"><img src="previews/mobile_30_shiba_inu.png" width="205" alt="Mobile Shiba"/><br/><sub><b>🐕 Shiba Inu</b></sub></td>
    <td align="center"><img src="previews/mobile_30_shiba_inu_daily.png" width="205" alt="Mobile Shiba Daily"/><br/><sub><b>📝 Việc Hôm Nay</b></sub></td>
    <td align="center"><img src="previews/mobile_20_alpaca_cream.png" width="205" alt="Mobile Alpaca"/><br/><sub><b>🦙 Cream Alpaca</b></sub></td>
    <td align="center"><img src="previews/mobile_24_royal_cat_cash.png" width="205" alt="Mobile Royal Cat"/><br/><sub><b>👑 Royal Cat Cash</b></sub></td>
  </tr>
</table>

</details>

---

## 📋 Bảng Tải Trực Tiếp Toàn Bộ 40 Mẫu Template (Đủ 4 Phiên Bản — 160 Tệp)

| # | Tên Mẫu & Chủ Đề | ⚡ Pro #1 (Turbo v3.7) | ✨ Excel Offline | ☁️ GSheets Desktop | 📱 Mobile Portrait |
|---|---|---|---|---|---|
| **01** | 🌻 **Sunflower Garden Blush** | [`_Pro.xlsm`](templates/pro_macro/01_Sunflower_Garden_Blush_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/01_Sunflower_Garden_Blush.xlsx) | [Desktop](templates/google_sheets_edition/01_Sunflower_Garden_Blush.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/01_Sunflower_Garden_Blush_Mobile.xlsx) |
| **02** | 🌵 **Cactus Bloom Pastel Weeks** | [`_Pro.xlsm`](templates/pro_macro/02_Cactus_Bloom_Pastel_Weeks_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/02_Cactus_Bloom_Pastel_Weeks.xlsx) | [Desktop](templates/google_sheets_edition/02_Cactus_Bloom_Pastel_Weeks.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/02_Cactus_Bloom_Pastel_Weeks_Mobile.xlsx) |
| **03** | 🌈 **Rainbow Executive Donuts** | [`_Pro.xlsm`](templates/pro_macro/03_Rainbow_Executive_Donuts_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/03_Rainbow_Executive_Donuts.xlsx) | [Desktop](templates/google_sheets_edition/03_Rainbow_Executive_Donuts.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/03_Rainbow_Executive_Donuts_Mobile.xlsx) |
| **04** | 🌿 **Sage Botanical Habit & Budget** | [`_Pro.xlsm`](templates/pro_macro/04_Sage_Botanical_Habit_And_Budget_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/04_Sage_Botanical_Habit_And_Budget.xlsx) | [Desktop](templates/google_sheets_edition/04_Sage_Botanical_Habit_And_Budget.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/04_Sage_Botanical_Habit_And_Budget_Mobile.xlsx) |
| **05** | 🌙 **Lavender Dream Wellness & Mood** | [`_Pro.xlsm`](templates/pro_macro/05_Lavender_Dream_Wellness_Mood_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/05_Lavender_Dream_Wellness_Mood.xlsx) | [Desktop](templates/google_sheets_edition/05_Lavender_Dream_Wellness_Mood.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/05_Lavender_Dream_Wellness_Mood_Mobile.xlsx) |
| **06** | 🚀 **Midnight Navy Blush Focus XP** | [`_Pro.xlsm`](templates/pro_macro/06_Midnight_Navy_Blush_Focus_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/06_Midnight_Navy_Blush_Focus.xlsx) | [Desktop](templates/google_sheets_edition/06_Midnight_Navy_Blush_Focus.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/06_Midnight_Navy_Blush_Focus_Mobile.xlsx) |
| **07** | 🌸 **Sakura Zen Study Planner** | [`_Pro.xlsm`](templates/pro_macro/07_Sakura_Zen_Study_Planner_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/07_Sakura_Zen_Study_Planner.xlsx) | [Desktop](templates/google_sheets_edition/07_Sakura_Zen_Study_Planner.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/07_Sakura_Zen_Study_Planner_Mobile.xlsx) |
| **08** | 🪸 **Ocean Coral Fitness & Energy** | [`_Pro.xlsm`](templates/pro_macro/08_Ocean_Coral_Fitness_Energy_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/08_Ocean_Coral_Fitness_Energy.xlsx) | [Desktop](templates/google_sheets_edition/08_Ocean_Coral_Fitness_Energy.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/08_Ocean_Coral_Fitness_Energy_Mobile.xlsx) |
| **09** | 🍵 **Matcha Cafe Daily Routine** | [`_Pro.xlsm`](templates/pro_macro/09_Matcha_Cafe_Daily_Routine_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/09_Matcha_Cafe_Daily_Routine.xlsx) | [Desktop](templates/google_sheets_edition/09_Matcha_Cafe_Daily_Routine.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/09_Matcha_Cafe_Daily_Routine_Mobile.xlsx) |
| **10** | 🌌 **Aurora Glow RPG Quest Tracker** | [`_Pro.xlsm`](templates/pro_macro/10_Aurora_Glow_RPG_Quest_Tracker_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/10_Aurora_Glow_RPG_Quest_Tracker.xlsx) | [Desktop](templates/google_sheets_edition/10_Aurora_Glow_RPG_Quest_Tracker.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/10_Aurora_Glow_RPG_Quest_Tracker_Mobile.xlsx) |
| **11** | 🌹 **Velvet Rose Garden** | [`_Pro.xlsm`](templates/pro_macro/11_Velvet_Rose_Garden_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/11_Velvet_Rose_Garden.xlsx) | [Desktop](templates/google_sheets_edition/11_Velvet_Rose_Garden.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/11_Velvet_Rose_Garden_Mobile.xlsx) |
| **12** | 🌷 **Blue Tulip Mint Breeze** | [`_Pro.xlsm`](templates/pro_macro/12_Blue_Tulip_Mint_Breeze_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/12_Blue_Tulip_Mint_Breeze.xlsx) | [Desktop](templates/google_sheets_edition/12_Blue_Tulip_Mint_Breeze.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/12_Blue_Tulip_Mint_Breeze_Mobile.xlsx) |
| **13** | 🌸 **Buttercream Blossom Bars** | [`_Pro.xlsm`](templates/pro_macro/13_Buttercream_Blossom_Bars_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/13_Buttercream_Blossom_Bars.xlsx) | [Desktop](templates/google_sheets_edition/13_Buttercream_Blossom_Bars.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/13_Buttercream_Blossom_Bars_Mobile.xlsx) |
| **14** | 🌳 **Emerald Forest Gold Stars** | [`_Pro.xlsm`](templates/pro_macro/14_Emerald_Forest_Gold_Stars_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/14_Emerald_Forest_Gold_Stars.xlsx) | [Desktop](templates/google_sheets_edition/14_Emerald_Forest_Gold_Stars.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/14_Emerald_Forest_Gold_Stars_Mobile.xlsx) |
| **15** | 🌻 **Mocha Rose Terracotta Sunflower** | [`_Pro.xlsm`](templates/pro_macro/15_Mocha_Rose_Terracotta_Sunflower_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/15_Mocha_Rose_Terracotta_Sunflower.xlsx) | [Desktop](templates/google_sheets_edition/15_Mocha_Rose_Terracotta_Sunflower.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/15_Mocha_Rose_Terracotta_Sunflower_Mobile.xlsx) |
| **16** | 🏡 **Dream Home Architect Builder** | [`_Pro.xlsm`](templates/pro_macro/16_Dream_Home_Architect_Builder_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/16_Dream_Home_Architect_Builder.xlsx) | [Desktop](templates/google_sheets_edition/16_Dream_Home_Architect_Builder.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/16_Dream_Home_Architect_Builder_Mobile.xlsx) |
| **17** | 🌺 **Wildflower Bloom & Daily Mood** | [`_Pro.xlsm`](templates/pro_macro/17_Wildflower_Bloom_Daily_Mood_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/17_Wildflower_Bloom_Daily_Mood.xlsx) | [Desktop](templates/google_sheets_edition/17_Wildflower_Bloom_Daily_Mood.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/17_Wildflower_Bloom_Daily_Mood_Mobile.xlsx) |
| **18** | 🌳 **Plum Oak Master Suite** | [`_Pro.xlsm`](templates/pro_macro/18_Plum_Oak_Master_Suite_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/18_Plum_Oak_Master_Suite.xlsx) | [Desktop](templates/google_sheets_edition/18_Plum_Oak_Master_Suite.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/18_Plum_Oak_Master_Suite_Mobile.xlsx) |
| **19** | 🌻 **Meadow Emerald Sunflower** | [`_Pro.xlsm`](templates/pro_macro/19_Meadow_Emerald_Sunflower_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/19_Meadow_Emerald_Sunflower.xlsx) | [Desktop](templates/google_sheets_edition/19_Meadow_Emerald_Sunflower.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/19_Meadow_Emerald_Sunflower_Mobile.xlsx) |
| **20** | 🦙 **Cream Alpaca Cozy Budget** *(Cozy Cafe: Khăn Len, Mũ Nồi & Latte)* | [`_Pro.xlsm`](templates/pro_macro/20_Cream_Alpaca_Cozy_Budget_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/20_Cream_Alpaca_Cozy_Budget.xlsx) | [Desktop](templates/google_sheets_edition/20_Cream_Alpaca_Cozy_Budget.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/20_Cream_Alpaca_Cozy_Budget_Mobile.xlsx) |
| **21** | 🌸 **Blush Alpaca Flower Crown** *(Vườn Cổ Tích: Giỏ Hoa & Vòng Hoa Hồng)* | [`_Pro.xlsm`](templates/pro_macro/21_Blush_Alpaca_Flower_Crown_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/21_Blush_Alpaca_Flower_Crown.xlsx) | [Desktop](templates/google_sheets_edition/21_Blush_Alpaca_Flower_Crown.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/21_Blush_Alpaca_Flower_Crown_Mobile.xlsx) |
| **22** | 🍵 **Matcha Alpaca Meadow** *(Picnic Thám Hiểm: Khăn Caro, Yên Thêu & Mũ Cói)* | [`_Pro.xlsm`](templates/pro_macro/22_Matcha_Alpaca_Meadow_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/22_Matcha_Alpaca_Meadow.xlsx) | [Desktop](templates/google_sheets_edition/22_Matcha_Alpaca_Meadow.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/22_Matcha_Alpaca_Meadow_Mobile.xlsx) |
| **23** | 🐼 **Bamboo Panda Zen Garden** *(Gấu Trúc Mochi Tròn Xoe: Onigiri & Khăn Đỏ)* | [`_Pro.xlsm`](templates/pro_macro/23_Bamboo_Panda_Zen_Garden_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/23_Bamboo_Panda_Zen_Garden.xlsx) | [Desktop](templates/google_sheets_edition/23_Bamboo_Panda_Zen_Garden.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/23_Bamboo_Panda_Zen_Garden_Mobile.xlsx) |
| **24** | 👑 **Royal Cat Saving Cash** | [`_Pro.xlsm`](templates/pro_macro/24_Royal_Cat_Saving_Cash_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/24_Royal_Cat_Saving_Cash.xlsx) | [Desktop](templates/google_sheets_edition/24_Royal_Cat_Saving_Cash.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/24_Royal_Cat_Saving_Cash_Mobile.xlsx) |
| **25** | 🐱 **Ginger Kitten Basket Routine** | [`_Pro.xlsm`](templates/pro_macro/25_Ginger_Kitten_Basket_Routine_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/25_Ginger_Kitten_Basket_Routine.xlsx) | [Desktop](templates/google_sheets_edition/25_Ginger_Kitten_Basket_Routine.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/25_Ginger_Kitten_Basket_Routine_Mobile.xlsx) |
| **26** | 🌙 **Pastel Purple Starlight Cat** *(Trăng Khuyết & Mũ Nồi Sao)* | [`_Pro.xlsm`](templates/pro_macro/26_Pastel_Purple_Royal_Cat_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/26_Pastel_Purple_Royal_Cat.xlsx) | [Desktop](templates/google_sheets_edition/26_Pastel_Purple_Royal_Cat.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/26_Pastel_Purple_Royal_Cat_Mobile.xlsx) |
| **27** | 🐣 **Hatching Chick Icon Studio** | [`_Pro.xlsm`](templates/pro_macro/27_Hatching_Chick_Icon_Studio_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/27_Hatching_Chick_Icon_Studio.xlsx) | [Desktop](templates/google_sheets_edition/27_Hatching_Chick_Icon_Studio.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/27_Hatching_Chick_Icon_Studio_Mobile.xlsx) |
| **28** | 🍬 **Cotton Candy Jar Sweet** | [`_Pro.xlsm`](templates/pro_macro/28_Cotton_Candy_Jar_Sweet_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/28_Cotton_Candy_Jar_Sweet.xlsx) | [Desktop](templates/google_sheets_edition/28_Cotton_Candy_Jar_Sweet.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/28_Cotton_Candy_Jar_Sweet_Mobile.xlsx) |
| **29** | 🌹 **Watercolor Rose Bouquet** | [`_Pro.xlsm`](templates/pro_macro/29_Watercolor_Rose_Bouquet_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/29_Watercolor_Rose_Bouquet.xlsx) | [Desktop](templates/google_sheets_edition/29_Watercolor_Rose_Bouquet.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/29_Watercolor_Rose_Bouquet_Mobile.xlsx) |
| **30** | 🐕 **Shiba Inu Happy Bork** *(Khăn Đỏ Karakusa & Xương Vàng)* | [`_Pro.xlsm`](templates/pro_macro/30_Shiba_Inu_Happy_Bork_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/30_Shiba_Inu_Happy_Bork.xlsx) | [Desktop](templates/google_sheets_edition/30_Shiba_Inu_Happy_Bork.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/30_Shiba_Inu_Happy_Bork_Mobile.xlsx) |
| **31** | ❄️ **Akita Inu Snow Loyal** *(Tuyết Trắng & Vòng Chuông Shimenawa)* | [`_Pro.xlsm`](templates/pro_macro/31_Akita_Inu_Snow_Loyal_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/31_Akita_Inu_Snow_Loyal.xlsx) | [Desktop](templates/google_sheets_edition/31_Akita_Inu_Snow_Loyal.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/31_Akita_Inu_Snow_Loyal_Mobile.xlsx) |
| **32** | 🌸 **Sakura Blossom Minimalist** *(Signature)* | [`_Pro.xlsm`](templates/pro_macro/32_Sakura_Blossom_Minimalist_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/32_Sakura_Blossom_Minimalist.xlsx) | [Desktop](templates/google_sheets_edition/32_Sakura_Blossom_Minimalist.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/32_Sakura_Blossom_Minimalist_Mobile.xlsx) |
| **33** | 🐱 **Peach Mochi Cat Mood Suite** *(Bánh Nếp, Quýt Mikan & Taiyaki)* | [`_Pro.xlsm`](templates/pro_macro/33_Peach_Mochi_Cat_Mood_Suite_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/33_Peach_Mochi_Cat_Mood_Suite.xlsx) | [Desktop](templates/google_sheets_edition/33_Peach_Mochi_Cat_Mood_Suite.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/33_Peach_Mochi_Cat_Mood_Suite_Mobile.xlsx) |
| **34** | 🐰 **Fluffy Bunny Sticker Pop** *(Signature)* | [`_Pro.xlsm`](templates/pro_macro/34_Fluffy_Bunny_Sticker_Pop_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/34_Fluffy_Bunny_Sticker_Pop.xlsx) | [Desktop](templates/google_sheets_edition/34_Fluffy_Bunny_Sticker_Pop.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/34_Fluffy_Bunny_Sticker_Pop_Mobile.xlsx) |
| **35** | 🐻 **Milk & Mocha Bear Sweet Love** *(Signature)* | [`_Pro.xlsm`](templates/pro_macro/35_Milk_Mocha_Bear_Sweet_Love_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/35_Milk_Mocha_Bear_Sweet_Love.xlsx) | [Desktop](templates/google_sheets_edition/35_Milk_Mocha_Bear_Sweet_Love.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/35_Milk_Mocha_Bear_Sweet_Love_Mobile.xlsx) |
| **36** | ⚡ **Digimon Veemon Miracle** *(7-Stage: Veemon → Magnamon)* | [`_Pro.xlsm`](templates/pro_macro/36_Digimon_Veemon_Miracle_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/36_Digimon_Veemon_Miracle.xlsx) | [Desktop](templates/google_sheets_edition/36_Digimon_Veemon_Miracle.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/36_Digimon_Veemon_Miracle_Mobile.xlsx) |
| **37** | 🔥 **Digimon Agumon Courage** *(7-Stage: Agumon → WarGreymon)* | [`_Pro.xlsm`](templates/pro_macro/37_Digimon_Agumon_Courage_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/37_Digimon_Agumon_Courage.xlsx) | [Desktop](templates/google_sheets_edition/37_Digimon_Agumon_Courage.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/37_Digimon_Agumon_Courage_Mobile.xlsx) |
| **38** | ✨ **Digimon Gatomon Light** *(7-Stage: Gatomon → LovelyAngemon)* | [`_Pro.xlsm`](templates/pro_macro/38_Digimon_Gatomon_Light_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/38_Digimon_Gatomon_Light.xlsx) | [Desktop](templates/google_sheets_edition/38_Digimon_Gatomon_Light.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/38_Digimon_Gatomon_Light_Mobile.xlsx) |
| **39** | ❄️ **Digimon Gabumon Friendship** *(7-Stage: Gabumon → MetalGarurumon)* | [`_Pro.xlsm`](templates/pro_macro/39_Digimon_Gabumon_Friendship_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/39_Digimon_Gabumon_Friendship.xlsx) | [Desktop](templates/google_sheets_edition/39_Digimon_Gabumon_Friendship.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/39_Digimon_Gabumon_Friendship_Mobile.xlsx) |
| **40** | ❤️ **Digimon Piyomon Love** *(7-Stage: Biyomon → Phoenixmon)* | [`_Pro.xlsm`](templates/pro_macro/40_Digimon_Piyomon_Love_Pro.xlsm) | [`.xlsx`](templates/excel_universal_offline/40_Digimon_Piyomon_Love.xlsx) | [Desktop](templates/google_sheets_edition/40_Digimon_Piyomon_Love.xlsx) | [📱 Mobile](templates/mobile_portrait_sheets/40_Digimon_Piyomon_Love_Mobile.xlsx) |

---

## 🎨 Giao Diện Pro v3.7 Thực Tế (`01_Sunflower` + Bộ Sưu Tập `#01`–`#31`)

![Sunflower Pro v3.7 Tracker](previews/01_sunflower_tracker.png)
![Sunflower Pro v3.7 Guide](previews/01_sunflower_guide.png)

<details>
<summary>🌻 Mở rộng xem ảnh chụp 31 mẫu cổ điển & linh vật (#02 – #31)</summary>

| Mẫu | Preview |
|---|---|
| **02. 🌵 Cactus Bloom Pastel Weeks** | ![Cactus](previews/02_cactus_tracker.png) |
| **03. 🌈 Rainbow Executive Donuts** | ![Rainbow](previews/03_rainbow_tracker.png) |
| **04. 🌿 Sage Botanical Living** | ![Botanical](previews/04_botanical_tracker.png) |
| **05. 🌙 Lavender Dream Wellness** | ![Lavender](previews/05_lavender_tracker.png) |
| **06. 🚀 Midnight Navy Focus XP** | ![Navy](previews/06_navy_tracker.png) |
| **07. 🌸 Sakura Zen Study Planner** | ![Sakura](previews/07_sakura_tracker.png) |
| **08. 🪸 Ocean Coral Fitness** | ![Ocean](previews/08_ocean_tracker.png) |
| **09. 🍵 Matcha Cafe Routine** | ![Matcha](previews/09_matcha_tracker.png) |
| **10. 🌌 Aurora Glow RPG Quest** | ![Aurora](previews/10_aurora_tracker.png) |
| **11. 🌹 Velvet Rose Garden** | ![Velvet Rose](previews/11_velvet_rose_tracker.png) |
| **12. 🌷 Blue Tulip Mint Breeze** | ![Blue Tulip](previews/12_blue_tulip_tracker.png) |
| **13. 🌸 Buttercream Blossom Bars** | ![Buttercream](previews/13_buttercream_blossom_tracker.png) |
| **14. 🌳 Emerald Forest Gold Stars** | ![Emerald Forest](previews/14_emerald_forest_tracker.png) |
| **15. 🌻 Mocha Rose Terracotta** | ![Mocha Sunflower](previews/15_mocha_sunflower_tracker.png) |
| **16. 🏡 Dream Home Architect** | ![Dream Home](previews/16_dream_house_tracker.png) |
| **17. 🌺 Wildflower Bloom & Mood** | ![Wildflower](previews/17_wildflower_mood_tracker.png) |
| **18. 🌳 Plum Oak Master Suite** | ![Plum Oak](previews/18_plum_oak_tracker.png) |
| **19. 🌻 Meadow Emerald Sunflower** | ![Meadow Sunflower](previews/19_meadow_sunflower_tracker.png) |
| **20. 🦙 Cream Alpaca Cozy Cafe & Budget** | ![Cream Alpaca](previews/20_alpaca_cream_tracker.png) |
| **21. 🌸 Blush Alpaca Fairy Flower Crown** | ![Blush Alpaca](previews/21_alpaca_blush_tracker.png) |
| **22. 🍵 Matcha Alpaca Picnic Explorer** | ![Matcha Alpaca](previews/22_alpaca_matcha_tracker.png) |
| **23. 🐼 Bamboo Panda Round Zen Garden** | ![Bamboo Panda](previews/23_bamboo_panda_tracker.png) |
| **24. 👑 Royal Cat Saving Cash** | ![Royal Cat](previews/24_royal_cat_cash_tracker.png) |
| **25. 🐱 Ginger Kitten Basket** | ![Ginger Kitten](previews/25_ginger_kitten_tracker.png) |
| **26. 🌙 Pastel Purple Starlight Cat** | ![Starlight Lavender Cat](previews/26_purple_cat_tracker.png) |
| **27. 🐣 Hatching Chick Studio** | ![Hatching Chick](previews/27_hatching_chick_tracker.png) |
| **28. 🍬 Cotton Candy Jar Sweet** | ![Candy Jar](previews/28_candy_jar_tracker.png) |
| **29. 🌹 Watercolor Rose Bouquet** | ![Rose Bouquet](previews/29_rose_bouquet_tracker.png) |
| **30. 🐕 Shiba Inu Happy Bork** | ![Shiba Inu](previews/30_shiba_inu_tracker.png) |
| **31. ❄️ Akita Inu Snow Loyal** | ![Akita Inu](previews/31_akita_inu_tracker.png) |

</details>

---

## 🎭 Bộ 245 Ảnh Hoạt Ảnh 6 & 7 Giai Đoạn (`assets/` — 40 Chủ Đề, v3.7)

### ⚡ Batch 5 (Mới v3.7 — Bộ 5 Chủ Đề Digimon 7 Cấp Tiến Hóa `#36`–`#40` — 35 Sprites Chuẩn Canon)
![35 Digimon 7-Stage Evolution Sprites Contact Sheet](previews/assets_contact_sheet_digimon.png)

### Bộ 4 Alpaca & Gấu Trúc Mochi Vẽ Lại Độc Bản (`#20`, `#21`, `#22`, `#23` — 24 Sprites)
![24 Overhauled Alpaca & Panda Sprites](previews/assets_contact_sheet_alpaca_panda_fix.png)

### Bộ 6 Thú Cưng Vẽ Lại Chuẩn Kawaii Vector Bézier (`#24`, `#25`, `#26`, `#30`, `#31`, `#33` — 36 Sprites)
![36 Overhauled Pet Sprites Contact Sheet](previews/assets_contact_sheet_pets_overhaul.png)

### Batch 4 (Chủ đề `#32`–`#35` — 24 Sprites Signature)
![24 Sprites Contact Sheet Batch 4](previews/assets_contact_sheet_batch4.png)

<details>
<summary>🎨 Xem Batch 1 (#01–#10), Batch 2 (#11–#19) & Batch 3 (#20–#31) Sprites</summary>

![72 Sprites Contact Sheet Batch 3](previews/assets_contact_sheet_batch3.png)
![60 Sprites Contact Sheet Batch 1](previews/assets_contact_sheet.png)
![54 Sprites Contact Sheet Batch 2](previews/assets_contact_sheet_batch2.png)

</details>

---

## ☁️ Kích Hoạt Google Sheets Trong 10 Giây (1-Click Setup v3.7)

1. Tải mẫu từ [`templates/google_sheets_edition/`](templates/google_sheets_edition/) hoặc [`templates/mobile_portrait_sheets/`](templates/mobile_portrait_sheets/) lên Google Drive → **Mở bằng Google Sheets** → **Tệp → Lưu dưới dạng Google Trang tính**.
2. Chọn **Tiện ích mở rộng (Extensions) → Apps Script** → dán toàn bộ code trong [`scripts/google_sheets_1click_setup.gs`](scripts/google_sheets_1click_setup.gs) → **Lưu (`Ctrl+S`)** → bấm **Run `setupHabitTracker`**.

Xem thêm hướng dẫn tại [`docs/GOOGLE_SHEETS_GUIDE.md`](docs/GOOGLE_SHEETS_GUIDE.md) và [`docs/CUSTOMIZATION_GUIDE.md`](docs/CUSTOMIZATION_GUIDE.md).

---

## 🛠️ Dành Cho Developer (Build & QA v3.7)

```powershell
# Trích xuất bộ 35 sprite Digimon chuẩn canon & xuất contact sheet:
python scripts/extract_digimon_assets.py

# Build Pro Interactive (.xlsm) theo lô với Turbo Engine v3.7 (tự recycle Excel COM mỗi 5 file):
python scripts/excel_com_enhancer.py pro 36_Digimon_Veemon_Miracle 37_Digimon_Agumon_Courage 38_Digimon_Gatomon_Light 39_Digimon_Gabumon_Friendship 40_Digimon_Piyomon_Love

# Build Mobile Portrait (.xlsx) hỗ trợ 6 & 7 giai đoạn:
python scripts/build_mobile_templates.py 36_digimon_veemon 37_digimon_agumon 38_digimon_gatomon 39_digimon_gabumon 40_digimon_piyomon
```

---

💛 **Created with care by Dyu** · *Chúc bạn gieo từng thói quen nhỏ, tận hưởng niềm vui pháo hoa mỗi ngày 100% và gặt hái cả khu vườn kỷ luật rực rỡ!*
