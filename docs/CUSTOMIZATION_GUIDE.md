# 🎨 Hướng Dẫn Tùy Biến Nâng Cao — Version 2.0 (Universal Offline Excel Edition)

---

## 1. Reset dữ liệu mẫu trong 5 giây
1. Mở tab Tracker chính (vd: `🌻 Monthly Tracker`).
2. Quét chọn toàn bộ vùng ô tick từ **`C17:AG36`** (hoặc bấm `Ctrl + G` → gõ `C17:AG36` → `Enter`).
3. Nhấn phím **`Delete`** (trên Mac: `fn + Backspace`).
4. Toàn bộ ô Checkbox lập tức trở về trạng thái chưa tick, biểu tượng hoạt ảnh về Stage 0, còn **100% công thức, màu sắc & biểu đồ được giữ nguyên vẹn**!

---

## 2. Tự đổi bộ ảnh hoạt ảnh 6 giai đoạn (Custom Animation)

### ⭐ Trên bản Excel Offline Mọi Máy (`templates/excel_universal_offline/`) — KHÔNG cần link, KHÔNG cần Internet!
1. Chuột phải vào tên bất kỳ tab nào ở thanh dưới cùng → chọn **Unhide (Hiện trang tính)** → chọn sheet **`_Assets`** → bấm **OK**.
2. Bạn sẽ thấy 6 ô trắng **`B2:B7`** tương ứng với **Stage 0 → Stage 5** (ô `B8` để trắng để ẩn ngày thừa cuối tháng — giữ nguyên `B8`!).
3. Xóa 6 hình mẫu cũ và dùng **Insert → Pictures** dán 6 ảnh PNG/sticker bất kỳ của riêng bạn vào đúng giữa 6 ô **`B2` → `B7`**.
4. Chuột phải vào tab **`_Assets`** → **Hide** để ẩn lại.
5. Quay lại tab Tracker: **toàn bộ 31 ngày + Hero icon + 6 ô xem trước trên trang Hướng Dẫn đã tự động đổi sang bộ ảnh mới của bạn!**

### ☁️ Trên bản Google Sheets & Excel 365 (`templates/google_sheets_and_excel365/`)
1. Chuẩn bị 6 file PNG đặt tên `stage_0.png` .. `stage_5.png` trên thư mục GitHub/CDN public.
2. Mở tab **`📖 Hướng Dẫn`** → dán đường dẫn thư mục gốc (kết thúc bằng `/`) vào ô màu vàng **`CFG_IMG_BASE`**.

---

## 3. Điều chỉnh ngưỡng tăng trưởng (%)
Trên tab **`📖 Hướng Dẫn`**, bạn có thể sửa trực tiếp 3 ô ngưỡng màu vàng:
- **`CFG_THR_1`** (mặc định `25%`): Ngưỡng lên Stage 2
- **`CFG_THR_2`** (mặc định `50%`): Ngưỡng lên Stage 3
- **`CFG_THR_3`** (mặc định `75%`): Ngưỡng lên Stage 4 & tính vào bộ đếm **THIS MONTH YOU'VE GROWN**

---

## 4. Thêm thói quen mới mà KHÔNG hỏng công thức
- **Dòng 1–12 (`B17:B28`):** Đã gắn sẵn 372 Form Control Checkboxes — chỉ cần sửa/gõ tên thói quen ở cột `B`.
- **Dòng 13–20 (`B29:B36`):** Đã nối sẵn công thức `GOAL`, `DONE`, `PROGRESS`, `CURRENT STREAK`, `LONGEST STREAK` (trên sheet ẩn `_Calc`) kèm dropdown chọn **`✓`** — chỉ cần gõ tên thói quen và dùng ngay!
- Để xóa thói quen không dùng: chọn ô tên trong cột `B` → bấm **`Delete`** (không bấm *Delete Row*).

---

## 5. Đổi Tháng / Năm & Nhân bản sang tháng mới
1. Nhấn trực tiếp vào 2 ô pill màu riêng biệt ở góc trên bên trái bảng Tracker: **Tháng (`B3`)** và **Năm (`B5`)** → chọn từ danh sách thả xuống (tương thích mọi cài đặt ngôn ngữ/vùng miền trên Windows & Mac). Toàn bộ số ngày (28 / 29 năm nhuận / 30 / 31) và thứ (`Mon–Sun`) tự nhảy chuẩn xác!
2. Để tạo tháng mới: Chuột phải vào tab Tracker → **Move or Copy...** → tick **☑ Create a copy** → đổi tên tab → đổi Tháng ở `B3` → reset vùng `C17:AG36` bằng phím `Delete`.
