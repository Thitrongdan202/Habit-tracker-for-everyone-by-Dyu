# ☁️ Hướng Dẫn Sử Dụng Bản Google Sheets (Habit Tracker v2.1 — Gọn 4 Tab)

> **Tại sao khi mới mở file `.xlsx` trên Google Sheets lại thấy chữ `TRUE / FALSE`?**
> Google Sheets không tự chuyển đổi định dạng ô Checkbox của Microsoft Excel khi import file `.xlsx`. Trong **v2.1**, mọi file trong `templates/google_sheets_edition/` được tinh gọn còn **đúng 4 tab hiển thị** (`📖 Hướng Dẫn`, `Monthly Tracker`, `🎯 Yearly Goals & Habits`, `🏆 Tổng Kết & Thành Tựu Năm`) + sheet ẩn `_Database`, kèm **Script 1-Click** vừa bật Checkbox gốc vừa kích hoạt tự động lưu/nạp 12 tháng mỗi khi đổi dropdown!

---

## Cách 1: 1-Click Bật Checkbox + Tự Lưu 12 Tháng (Khuyên dùng ⚡)

Chỉ làm **1 lần duy nhất** (10 giây):

1. Tải file `.xlsx` trong `templates/google_sheets_edition/` lên **Google Drive**.
2. Nhấp đúp mở bằng **Google Trang tính (Google Sheets)** → chọn **Tệp (File) → Lưu dưới dạng Google Trang tính (Save as Google Sheets)**.
3. Trên thanh menu chọn **Tiện ích mở rộng (Extensions) → Apps Script**.
4. Xóa đoạn code mặc định, dán toàn bộ nội dung file [`scripts/google_sheets_1click_setup.gs`](../scripts/google_sheets_1click_setup.gs) vào và bấm **Lưu (`Ctrl+S`)**.
5. Chọn hàm **`setupHabitTracker`** ở thanh trên cùng → bấm **Chạy (Run)** (cấp quyền 1 lần).
6. **Hoàn tất!**
   - Toàn bộ ô `TRUE/FALSE` trên `Monthly Tracker` (`C17:AG36`) và `🎯 Yearly Goals & Habits` (`B6:B25`) lập tức biến thành **Checkbox gốc màu Pastel** theo đúng chủ đề!
   - Hàm `onEdit(e)` tự động kích hoạt: mỗi khi bạn đổi dropdown **Tháng (`B3`)** hoặc **Năm (`B5`)** (hay Năm mục tiêu `I2`), tháng cũ tự lưu vào `_Database` và tháng mới tự nạp (tháng chưa dùng mở trống sạch!).

---

## Cách 2: Thủ Công 3 Giây (Không cần Apps Script)

Nếu bạn chỉ muốn dùng nhanh cho tháng hiện tại:
1. Quét chọn vùng ô `C17:AG36` trên tab Tracker (hoặc `B6:B25` trên `🎯 Yearly Goals & Habits`).
2. Chọn **Chèn (Insert) → Hộp kiểm (Checkbox)**.
3. Toàn bộ ô `TRUE/FALSE` lập tức thành ô tick chuột mượt mà!

---

## Tính năng nổi bật trên bản Google Sheets v2.1
- **Giao diện gọn đẹp đúng 4 tab** — không còn 15 tab rối mắt ở thanh dưới cùng!
- **Hoạt ảnh `=IMAGE()` động 6 giai đoạn** (trỏ về nhánh `main`): tự đổi từ `Stage 0` (0%) → `Stage 5` (100%) cho cả **31 ngày**, **Monthly Hero**, **Yearly Goals Hero**, **Annual Hero**, **12 ô tháng** & **Huy hiệu Thành Tựu**!
- **Tự đổi bộ ảnh riêng:** Dán đường dẫn thư mục 6 ảnh `stage_0.png` → `stage_5.png` vào ô vàng **`CFG_IMG_BASE`** trên tab `📖 Hướng Dẫn`.
