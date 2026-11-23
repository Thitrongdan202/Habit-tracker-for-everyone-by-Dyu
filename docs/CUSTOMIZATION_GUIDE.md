# 🎨 Hướng Dẫn Tùy Biến Nâng Cao — Habit Tracker Collection (v3.7)

---

## 1. Reset dữ liệu mẫu trong 5 giây
1. Mở tab Tracker chính (vd: `🌻 Monthly Tracker`).
2. Quét chọn toàn bộ vùng ô tick từ **`C17:AG36`** (hoặc bấm `Ctrl + G` → gõ `C17:AG36` → `Enter`).
3. Nhấn phím **`Delete`** (trên Mac: `fn + Backspace`).
4. Toàn bộ ô Checkbox lập tức trở về trạng thái chưa tick, biểu tượng hoạt ảnh về Stage 0, còn **100% công thức, màu sắc & biểu đồ được giữ nguyên vẹn**!
   - Trên bản **Pro Interactive (`.xlsm` v3.7)**: Nếu lỡ tay xóa hoặc kéo-fill nhầm, bấm ngay **`Ctrl + Z`** hoặc nút **`↩ Undo`** ở góc trái trên để khôi phục lập tức! Dòng công thức `TOTAL • TỔNG KẾT` (Row 37) được khóa bảo vệ tự động (`UserInterfaceOnly:=True`) nên không bao giờ bị ghi đè.

---

## 2. Tự đổi bộ ảnh hoạt ảnh 6 hoặc 7 giai đoạn (Custom Animation)

### ⭐ Trên bản Pro Interactive (`.xlsm` v3.7 Turbo — `templates/pro_macro/`)
1. Chuột phải vào bất kỳ tên tab nào ở thanh dưới cùng → chọn **Unhide (Hiện trang tính)** → chọn sheet **`_Assets`** → bấm **OK**.
2. Dán **6 ảnh PNG** vào **`B2:B7`** (cho các mẫu `#01`–`#35`, Stage 0 → Stage 5) hoặc **7 ảnh PNG** vào **`B2:B8`** (cho 5 mẫu Digimon `#36`–`#40`, Stage 0 → Stage 6).
3. Bấm nút **`🔄 Đồng bộ 6/7 ảnh mới (SyncSprites)`** ngay trên sheet `_Assets` → toàn bộ 31 ngày, Hero icon, Daily Tasks, Yearly Goals & 12 tháng Tổng Kết tự động cập nhật sang bộ ảnh mới chỉ trong 1 giây!
4. Chuột phải tab **`_Assets`** → **Hide** để ẩn lại.

### ✨ Trên bản Excel Universal Offline (`.xlsx` — `templates/excel_universal_offline/`) — KHÔNG Macro, KHÔNG cần Internet!
1. Chuột phải vào tên bất kỳ tab nào → **Unhide** → chọn sheet **`_Assets`** → bấm **OK**.
2. Thay 6 ảnh mẫu trong **`B2:B7`** (giữ trắng `B8`) — hoặc 7 ảnh trong **`B2:B8`** (giữ trắng `B9` đối với bộ Digimon `#36`–`#40`)!
3. Ẩn lại sheet **`_Assets`** → toàn bộ 54–55 Linked Pictures (31 ngày + Hero + Yearly + Annual) tự động hiển thị bộ ảnh mới của bạn!

### ☁️ Trên bản Google Sheets Desktop & Mobile Portrait (`templates/google_sheets_edition/` & `templates/mobile_portrait_sheets/`)
1. Chuẩn bị 6 file PNG (`stage_0.png` .. `stage_5.png`) — hoặc 7 file PNG (`stage_0.png` .. `stage_6.png` cho Digimon `#36`–`#40`) trên thư mục GitHub/CDN public.
2. Mở tab **`📖 Hướng Dẫn`** → dán đường dẫn thư mục gốc (kết thúc bằng `/`) vào ô màu vàng **`CFG_IMG_BASE`**.

---

## 3. Điều chỉnh ngưỡng tăng trưởng (%)
Trên tab **`📖 Hướng Dẫn`**, bạn có thể sửa trực tiếp các ô ngưỡng màu vàng:
- **Bộ 6 giai đoạn (`#01`–`#35`):** `CFG_THR_1` (`25%`), `CFG_THR_2` (`50%`), `CFG_THR_3` (`75%` — tính vào bộ đếm **THIS MONTH YOU'VE GROWN**).
- **Bộ Digimon 7 giai đoạn (`#36`–`#40`):** `CFG_THR_0` (`20%` Baby II), `CFG_THR_1` (`40%` Rookie), `CFG_THR_2` (`60%` Champion/Armor), `CFG_THR_3` (`80%` Ultimate — và `100%` mở khóa dạng **Mega ✨**!).

---

## 4. Thêm thói quen mới mà KHÔNG hỏng công thức
- Toàn bộ **20 dòng thói quen (`B17:B36`)** đã gắn sẵn 620 ô Checkbox (Excel Native Checkbox trên Pro `.xlsm` / Form Control Checkbox ẩn `;;;` trên Offline `.xlsx`) và nối sẵn công thức `GOAL`, `DONE`, `PROGRESS`, `CURRENT STREAK`, `LONGEST STREAK`!
- Chỉ cần gõ trực tiếp tên thói quen mới vào cột **`B`** (`B17:B36`) và nhập mục tiêu ở cột **`AI`** (`AI17:AI36`).
- Để xóa thói quen không dùng: chọn ô tên trong cột `B` → bấm **`Delete`** (không bấm *Delete Row*).

---

## 5. Đổi Tháng / Năm & Lưu Lịch Sử Đa Tháng
- **Bản Pro Interactive (`.xlsm` v3.7):** Nhấn nút **`◀ Tháng` / `Tháng ▶`** hoặc chọn dropdown **Tháng (`B3`)** / **Năm (`B5`)** — dữ liệu tháng cũ tự động lưu vào `_Database` và tháng mới mở ra siêu tốc (~31–54 ms)! Tương tự với **`📝 Nhiệm Vụ Ngày`** (nút `◀ Hôm qua` · `📅 Hôm nay` · `Ngày mai ▶`) và **`🎯 Yearly Goals & Habits`** (`I2`).
- **Bản Excel Universal Offline (`.xlsx`):** Đổi Tháng (`B3`) & Năm (`B5`) để tự nhảy lịch 28/29/30/31 ngày. Để sang tháng mới mà vẫn giữ dữ liệu cũ: chuột phải tab Tracker → **Move or Copy...** → tick **☑ Create a copy** → đổi Tháng ở `B3` → reset vùng `C17:AG36` bằng phím `Delete`.
