# 🌸 Habit Tracker Collection for Everyone — by Dyu (v2.1)

> **Bộ sưu tập 10 mẫu Excel & Google Sheets Habit Tracker thẩm mỹ chuẩn Digital Planner** — **Thống nhất gọn đúng 4 tab đẹp mắt (`📖 Hướng Dẫn`, `Monthly Tracker`, `🎯 Yearly Goals & Habits`, `🏆 Tổng Kết & Thành Tựu Năm`) trên cả 3 phiên bản!**
> **Hoạt ảnh động 6 giai đoạn theo % thực tế • Lưu dữ liệu đa Tháng & đa Năm siêu mượt (<100ms) • Hệ thống 8 Huy hiệu Thành Tựu Năm tự mở khóa • 100% Offline trên Excel 2016–365!**

![Version 2.1](https://img.shields.io/badge/Version-2.1_Unified_4--Tab-B57A7A?style=for-the-badge)
![Pro Interactive](https://img.shields.io/badge/Pro_Interactive-.XLSM_Auto--Save-217346?style=for-the-badge&logo=microsoftexcel&logoColor=white)
![Zero Macro Offline](https://img.shields.io/badge/Offline_No--Macro-.XLSX_Excel_2016--365-4E9F76?style=for-the-badge)
![Google Sheets](https://img.shields.io/badge/Google_Sheets-4--Tab_+_1--Click_Script-34A853?style=for-the-badge&logo=googlesheets&logoColor=white)

---

## ⚡ Cài Đặt & Tải Nhanh Bằng 1 Dòng Lệnh (Interactive Installer)

Chạy **1 dòng lệnh duy nhất** — trình cài đặt sẽ cho bạn chọn **Phiên bản** (`[1] Pro .xlsm`, `[2] Excel Offline Không Macro .xlsx`, `[3] Google Sheets + Script 1-Click`) và chọn **Mẫu yêu thích** (`1`, `1,3,7`, `1-5`, hoặc `A` tải toàn bộ 10 mẫu) vào thư mục `template/`:

### 🪟 Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/Thitrongdan202/Habit-tracker-for-everyone-by-Dyu/main/install.ps1 | iex
```

### 🍎 macOS / 🐧 Linux (Terminal)
```bash
curl -fsSL https://raw.githubusercontent.com/Thitrongdan202/Habit-tracker-for-everyone-by-Dyu/main/install.sh | bash
```

> **Người dùng cuối KHÔNG cần cài Python!** Tải xong chỉ cần nhấp đúp mở file bằng Microsoft Excel hoặc tải lên Google Sheets và bắt đầu tick ngay.

---

## 🧭 Chọn Đúng Phiên Bản Phù Hợp Với Bạn (3 Thư Mục Gọn Sạch)

| Phiên bản | Thư mục | Số tab hiển thị | Điểm nổi bật | Phù hợp với |
|---|---|---|---|---|
| **⚡ Pro Interactive (`.xlsm`)** *(Khuyên dùng)* | [`templates/pro_macro/`](templates/pro_macro/) | **4 tab** | Đổi Tháng (`B3`) & Năm (`B5`) hoặc Năm Mục Tiêu (`I2`) **tự lưu & tải dữ liệu đa tháng/năm (<100ms)** vào sheet ẩn `_Database` (không dính tick!). 100% Offline! | Excel Desktop (Windows & Mac) dùng lâu dài nhiều tháng/năm |
| **✨ Excel Offline Không Macro (`.xlsx`)** | [`templates/excel_universal_offline/`](templates/excel_universal_offline/) | **4 tab** | **KHÔNG Macro / không cảnh báo bảo mật**, chạy cực nhẹ trên mọi Excel 2016–365 Win/Mac, 100% hoạt ảnh offline & Thành Tựu Năm! Sang tháng mới chỉ cần nhân bản tab/file trong 2 giây. | Máy công ty chặn Macro hoặc thích mở phát chạy luôn không bấm Enable Content |
| **☁️ Google Sheets Edition (`.xlsx` + `.gs`)** | [`templates/google_sheets_edition/`](templates/google_sheets_edition/) | **4 tab** | Gọn 4 tab + `_Database` + hoạt ảnh `=IMAGE()` động 6 giai đoạn. Dán [`google_sheets_1click_setup.gs`](scripts/google_sheets_1click_setup.gs) chạy 1 lần → **bật Checkbox Pastel & tự lưu/nạp 12 tháng qua `onEdit(e)`**! | Dùng Cloud trên trình duyệt, điện thoại & iPad |

---

## ✨ Điểm Đột Phá Của Phiên Bản 2.1

1. **🔄 Lưu Dữ Liệu Đa Tháng & Đa Năm Thật Sự (Zero Sticking Ticks!):**
   - Trong bản **Pro (`.xlsm`)** (và bản **Google Sheets** sau khi chạy Script 1-Click), toàn bộ vùng tick `C17:AG36`, tên thói quen & mục tiêu năm được tự động lưu vào sheet ẩn `_Database` theo khóa `YYYY-MM` và `YYYY` bằng mảng 2D trong bộ nhớ (`ScreenUpdating = False`, `Calculation = xlCalculationManual` → chuyển tháng mượt `<100ms`).
   - Đổi từ `October 2026` → `November 2026` mở ra bảng **trắng tinh 100%** (tuyệt đối không dính tick tháng cũ); quay lại `October 2026` khôi phục nguyên vẹn từng ô tick!
2. **🌱 Hoạt Ảnh Động 6 Giai Đoạn Cho MỌI Biểu Tượng Hero (Không Bao Giờ Đứng Im!):**
   - **0%** → `stage_0` (chậu trống) · **1–24%** → `stage_1` · **25–49%** → `stage_2` · **50–74%** → `stage_3` · **75–99%** → `stage_4` · **100%** → `stage_5` (nở rộ!).
   - Áp dụng đồng bộ cho **tất cả 4 khu vực** trên cả 10 mẫu:
     1. **31 biểu tượng từng ngày** (`Anim_Day01`..`Anim_Day31`)
     2. **Biểu tượng Monthly Hero** (`Anim_MonthlyHero` ở thẻ *THIS MONTH, YOU'VE GROWN*)
     3. **Biểu tượng Yearly Goals Hero** (`Anim_YearlyGoals` ở thẻ *YOU HAVE PLANTED* — `0/10` mục tiêu hiển thị chậu trống!)
     4. **Biểu tượng Annual Hero + 12 mini-icon tháng (`T01`–`T12`) + Biểu tượng Huy hiệu** (`Anim_AnnualHero`, `Anim_AnnualM01..M12`, `Anim_AchBadges`)!
3. **🏆 Tab Mới `🏆 Tổng Kết & Thành Tựu Năm` + `🎯 Yearly Goals & Habits` Trên Đủ 10 Mẫu:**
   - Đồng bộ tuyệt đối bảng màu, font chữ và bộ sprite riêng của **từng chủ đề** (Sunflower Blush, Cactus Pastel, Rainbow, Sage Botanical, Lavender Moon, Midnight Navy, Sakura Zen, Ocean Coral, Matcha Cafe, Aurora RPG).
   - Chọn Năm (`2024–2040`) — năm chưa có dữ liệu (vd: `2028`) hiển thị **0%, biểu đồ trống, `0/8` huy hiệu & chậu trống `stage_0`** (tuyệt đối không rò rỉ dữ liệu năm khác!).
   - **4 thẻ Executive KPI** + **Khu vườn 12 tháng động** + **Biểu đồ xu hướng năm** + **8 Huy hiệu kỷ luật tự mở khóa** (*Khởi Hành, Tuần Lễ Vàng 7d, Chiến Binh 21d, Huyền Thoại 30d, Tháng Rực Rỡ ≥80%, Vườn Hoa Trăm Ngày, Chinh Phục Mục Tiêu ≥50%, Bậc Thầy Cả Năm*).
4. **☁️ Sửa Triệt Để Lỗi `TRUE/FALSE` Trên Google Sheets:**
   - Định dạng sẵn ô gọn đẹp + hướng dẫn 3 giây `Insert → Checkbox` ngay trong file, kèm Script 1-Click [`scripts/google_sheets_1click_setup.gs`](scripts/google_sheets_1click_setup.gs) (xem chi tiết tại [`docs/GOOGLE_SHEETS_GUIDE.md`](docs/GOOGLE_SHEETS_GUIDE.md)).

---

## 📋 Bảng Tải Trực Tiếp 10 Mẫu Template (Đủ 3 Phiên Bản)

| # | Tên Mẫu & Chủ Đề | ⚡ Pro Interactive *(Khuyên dùng)* | ✨ Excel Offline *(Không Macro)* | ☁️ Google Sheets *(4 Tab)* |
|---|---|---|---|---|
| **01** | 🌻 **Sunflower Garden Blush** | [Tải `_Pro.xlsm`](templates/pro_macro/01_Sunflower_Garden_Blush_Pro.xlsm) | [Tải `.xlsx`](templates/excel_universal_offline/01_Sunflower_Garden_Blush.xlsx) | [Google Sheets](templates/google_sheets_edition/01_Sunflower_Garden_Blush.xlsx) |
| **02** | 🌵 **Cactus Bloom Pastel Weeks** | [Tải `_Pro.xlsm`](templates/pro_macro/02_Cactus_Bloom_Pastel_Weeks_Pro.xlsm) | [Tải `.xlsx`](templates/excel_universal_offline/02_Cactus_Bloom_Pastel_Weeks.xlsx) | [Google Sheets](templates/google_sheets_edition/02_Cactus_Bloom_Pastel_Weeks.xlsx) |
| **03** | 🌈 **Rainbow Executive Donuts** | [Tải `_Pro.xlsm`](templates/pro_macro/03_Rainbow_Executive_Donuts_Pro.xlsm) | [Tải `.xlsx`](templates/excel_universal_offline/03_Rainbow_Executive_Donuts.xlsx) | [Google Sheets](templates/google_sheets_edition/03_Rainbow_Executive_Donuts.xlsx) |
| **04** | 🌿 **Sage Botanical Habit & Living** | [Tải `_Pro.xlsm`](templates/pro_macro/04_Sage_Botanical_Habit_And_Budget_Pro.xlsm) | [Tải `.xlsx`](templates/excel_universal_offline/04_Sage_Botanical_Habit_And_Budget.xlsx) | [Google Sheets](templates/google_sheets_edition/04_Sage_Botanical_Habit_And_Budget.xlsx) |
| **05** | 🌙 **Lavender Dream Wellness & Mood** | [Tải `_Pro.xlsm`](templates/pro_macro/05_Lavender_Dream_Wellness_Mood_Pro.xlsm) | [Tải `.xlsx`](templates/excel_universal_offline/05_Lavender_Dream_Wellness_Mood.xlsx) | [Google Sheets](templates/google_sheets_edition/05_Lavender_Dream_Wellness_Mood.xlsx) |
| **06** | 🚀 **Midnight Navy Blush Focus XP** | [Tải `_Pro.xlsm`](templates/pro_macro/06_Midnight_Navy_Blush_Focus_Pro.xlsm) | [Tải `.xlsx`](templates/excel_universal_offline/06_Midnight_Navy_Blush_Focus.xlsx) | [Google Sheets](templates/google_sheets_edition/06_Midnight_Navy_Blush_Focus.xlsx) |
| **07** | 🌸 **Sakura Zen Study Planner** | [Tải `_Pro.xlsm`](templates/pro_macro/07_Sakura_Zen_Study_Planner_Pro.xlsm) | [Tải `.xlsx`](templates/excel_universal_offline/07_Sakura_Zen_Study_Planner.xlsx) | [Google Sheets](templates/google_sheets_edition/07_Sakura_Zen_Study_Planner.xlsx) |
| **08** | 🪸 **Ocean Coral Fitness & Energy** | [Tải `_Pro.xlsm`](templates/pro_macro/08_Ocean_Coral_Fitness_Energy_Pro.xlsm) | [Tải `.xlsx`](templates/excel_universal_offline/08_Ocean_Coral_Fitness_Energy.xlsx) | [Google Sheets](templates/google_sheets_edition/08_Ocean_Coral_Fitness_Energy.xlsx) |
| **09** | 🍵 **Matcha Cafe Daily Routine** | [Tải `_Pro.xlsm`](templates/pro_macro/09_Matcha_Cafe_Daily_Routine_Pro.xlsm) | [Tải `.xlsx`](templates/excel_universal_offline/09_Matcha_Cafe_Daily_Routine.xlsx) | [Google Sheets](templates/google_sheets_edition/09_Matcha_Cafe_Daily_Routine.xlsx) |
| **10** | 🌌 **Aurora Glow RPG Quest Tracker** | [Tải `_Pro.xlsm`](templates/pro_macro/10_Aurora_Glow_RPG_Quest_Tracker_Pro.xlsm) | [Tải `.xlsx`](templates/excel_universal_offline/10_Aurora_Glow_RPG_Quest_Tracker.xlsx) | [Google Sheets](templates/google_sheets_edition/10_Aurora_Glow_RPG_Quest_Tracker.xlsx) |

---

## 🎨 Bộ Sưu Tập Ảnh Chụp Thực Tế Từ Microsoft Excel (v2.1)

### 1. 🌻 Sunflower Garden Blush
- **4 tab gọn đẹp:** `📖 Hướng Dẫn` · `🌻 Monthly Tracker` · `🎯 Yearly Goals & Habits` · `🏆 Tổng Kết & Thành Tựu Năm`

![Sunflower Monthly Tracker](previews/01_sunflower_tracker.png)
![Sunflower Annual Achievements](previews/01_sunflower_annual_achievements.png)

<details>
<summary>📸 Xem thêm: Trang Hướng Dẫn & Yearly Goals (Sunflower)</summary>

![Sunflower Guide](previews/01_sunflower_guide.png)
![Sunflower Yearly Goals](previews/01_sunflower_yearly_goals.png)

</details>

---

### 2. 🌵 Cactus Bloom Pastel Weeks
![Cactus Monthly Tracker](previews/02_cactus_tracker.png)
<details>
<summary>📸 Xem thêm: Yearly Goals & Tổng Kết Thành Tựu Năm (Cactus)</summary>

![Cactus Yearly Goals](previews/02_cactus_yearly_goals.png)
![Cactus Annual Achievements](previews/02_cactus_annual_achievements.png)

</details>

---

### 3. 🌈 Rainbow Executive Donuts
![Rainbow Habit Dashboard](previews/03_rainbow_tracker.png)
<details>
<summary>📸 Xem thêm: Yearly Goals & Tổng Kết Thành Tựu Năm (Rainbow)</summary>

![Rainbow Yearly Goals](previews/03_rainbow_yearly_goals.png)
![Rainbow Annual Achievements](previews/03_rainbow_annual_achievements.png)

</details>

---

### 4. 🌿 Sage Botanical Living
![Sage Botanical Tracker](previews/04_botanical_tracker.png)
<details>
<summary>📸 Xem thêm: Yearly Goals & Tổng Kết Thành Tựu Năm (Botanical)</summary>

![Botanical Yearly Goals](previews/04_botanical_yearly_goals.png)
![Botanical Annual Achievements](previews/04_botanical_annual_achievements.png)

</details>

---

### 5. 🌙 Lavender Dream Wellness & Mood
![Lavender Wellness Tracker](previews/05_lavender_tracker.png)
<details>
<summary>📸 Xem thêm: Yearly Goals & Tổng Kết Thành Tựu Năm (Lavender)</summary>

![Lavender Yearly Goals](previews/05_lavender_yearly_goals.png)
![Lavender Annual Achievements](previews/05_lavender_annual_achievements.png)

</details>

---

### 6. 🚀 Midnight Navy Blush Focus XP
![Midnight Navy Focus Tracker](previews/06_navy_tracker.png)
<details>
<summary>📸 Xem thêm: Yearly Goals & Tổng Kết Thành Tựu Năm (Midnight Navy)</summary>

![Midnight Navy Yearly Goals](previews/06_navy_yearly_goals.png)
![Midnight Navy Annual Achievements](previews/06_navy_annual_achievements.png)

</details>

---

### 7. 🌸 Sakura Zen Study Planner
![Sakura Zen Study Tracker](previews/07_sakura_tracker.png)
<details>
<summary>📸 Xem thêm: Yearly Goals & Tổng Kết Thành Tựu Năm (Sakura Zen)</summary>

![Sakura Yearly Goals](previews/07_sakura_yearly_goals.png)
![Sakura Annual Achievements](previews/07_sakura_annual_achievements.png)

</details>

---

### 8. 🪸 Ocean Coral Fitness & Energy
![Ocean Coral Fitness Tracker](previews/08_ocean_tracker.png)
<details>
<summary>📸 Xem thêm: Yearly Goals & Tổng Kết Thành Tựu Năm (Ocean Coral)</summary>

![Ocean Yearly Goals](previews/08_ocean_yearly_goals.png)
![Ocean Annual Achievements](previews/08_ocean_annual_achievements.png)

</details>

---

### 9. 🍵 Matcha Cafe Daily Routine
![Matcha Cafe Daily Routine](previews/09_matcha_tracker.png)
<details>
<summary>📸 Xem thêm: Yearly Goals & Tổng Kết Thành Tựu Năm (Matcha Cafe)</summary>

![Matcha Yearly Goals](previews/09_matcha_yearly_goals.png)
![Matcha Annual Achievements](previews/09_matcha_annual_achievements.png)

</details>

---

### 10. 🌌 Aurora Glow RPG Quest Tracker
![Aurora Glow RPG Tracker](previews/10_aurora_tracker.png)
<details>
<summary>📸 Xem thêm: Yearly Goals & Tổng Kết Thành Tựu Năm (Aurora RPG)</summary>

![Aurora Yearly Goals](previews/10_aurora_yearly_goals.png)
![Aurora Annual Achievements](previews/10_aurora_annual_achievements.png)

</details>

---

## ☁️ Kích Hoạt Google Sheets Trong 10 Giây (1-Click Setup)

1. Tải mẫu từ [`templates/google_sheets_edition/`](templates/google_sheets_edition/) lên Google Drive → **Mở bằng Google Sheets** → **Tệp → Lưu dưới dạng Google Trang tính**.
2. Chọn **Tiện ích mở rộng (Extensions) → Apps Script** → dán toàn bộ code trong [`scripts/google_sheets_1click_setup.gs`](scripts/google_sheets_1click_setup.gs) → **Lưu (`Ctrl+S`)** → bấm **Run `setupHabitTracker`**.
3. Toàn bộ ô `TRUE/FALSE` lập tức trở thành **Checkbox màu Pastel** + tự động lưu/nạp dữ liệu 12 tháng vào `_Database` mỗi khi đổi Tháng (`B3`) hoặc Năm (`B5`)!

Xem hướng dẫn chi tiết tại [`docs/GOOGLE_SHEETS_GUIDE.md`](docs/GOOGLE_SHEETS_GUIDE.md) và hướng dẫn tự đổi ảnh hoạt ảnh tại [`docs/CUSTOMIZATION_GUIDE.md`](docs/CUSTOMIZATION_GUIDE.md).

---

## 🎭 Bộ 60 Ảnh Hoạt Ảnh 6 Giai Đoạn (`assets/`)

![60 Sprites Contact Sheet](previews/assets_contact_sheet.png)

---

## 🛠️ Dành Cho Developer (Build & QA Từ Mã Nguồn)

```powershell
# Build bản Google Sheets (10 file — 2 giây)
python scripts/excel_builder.py gsheets

# Compile 10 bản Pro Interactive (.xlsm) & 10 bản Offline Không Macro (.xlsx) qua Excel COM
python scripts/excel_com_enhancer.py pro
python scripts/excel_com_enhancer.py offline

# Chạy bộ QA tự động v2.1 trên bản copy cô lập trong %TEMP%\qa_v21_test\
python scripts/qa_verify_v21.py
```

---

💛 **Created with care by Dyu** · *Chúc bạn gieo từng thói quen nhỏ và gặt hái cả khu vườn kỷ luật rực rỡ!*
