# ☁️ Hướng Dẫn Sử Dụng Google Sheets — Desktop & Điện Thoại Khổ Dọc (v4.3 — 100 Templates)

> **1 Script duy nhất (`google_sheets_1click_setup.gs` v4.3 Turbo) tự nhận diện cả 4 bố cục Cloud cho trọn bộ 100 mẫu (`#01`–`#95` Habit Tracker & Lễ Hội Giáng Sinh/Năm Mới + `#96`–`#100` Chiikawa Vocabulary Tracker!):**
> - **Bản Desktop Habit (`#01`–`#95`, `templates/google_sheets_edition/`):** Gọn 5 tab (`📖 Hướng Dẫn`, `Monthly Tracker`, `📝 Nhiệm Vụ Ngày`, `🎯 Yearly Goals & Habits`, `🏆 Tổng Kết & Thành Tựu Năm`), lịch tháng 31 ngày + lưu tự động O(1) từng Ngày & 12 Tháng vào `_Database`.
> - **Bản Desktop Chiikawa Vocabulary (`#96`–`#100`, `templates/google_sheets_edition/`):** Gọn 4 tab (`📚 Kho Từ Vựng`, `🎯 Luyện Tập & Lịch Ôn`, `📊 Thống Kê & Thành Tựu`, `📖 Hướng Dẫn`), tự bật Checkbox Pastel cho công tắc `🙈 Ẩn Nghĩa` / `🙈 Ẩn Từ`, cột SRS/Thuộc bài & Checklist 5 bước!
> - **Bản Điện Thoại Khổ Dọc (`#01`–`#100`, `templates/mobile_portrait_sheets/`):** Khổ dọc vừa khít iPhone/Android **0 cuộn ngang** (`<= Cột I` cho Habit & `<= Cột G` cho Chiikawa Vocabulary), ô tick lớn dễ bấm bằng ngón cái!

---

## 📱 Hướng Dẫn Nhanh Cho Điện Thoại (iOS & Android) — Mở 1 Chạm Như App!

### Bước 1: Cài đặt 1 lần (10 giây trên máy tính hoặc trình duyệt)
1. Tải file `*_Mobile.xlsx` từ [`templates/mobile_portrait_sheets/`](../templates/mobile_portrait_sheets/) lên **Google Drive**.
2. Mở bằng **Google Trang tính (Google Sheets)** → chọn **Tệp (File) → Lưu dưới dạng Google Trang tính (Save as Google Sheets)**.
3. Chọn **Tiện ích mở rộng (Extensions) → Apps Script** → xóa code cũ → dán toàn bộ nội dung [`scripts/google_sheets_1click_setup.gs`](../scripts/google_sheets_1click_setup.gs) → nhấn **Lưu (`Ctrl+S`)**.
4. Chọn hàm **`setupHabitTracker`** → nhấn **Chạy (Run)** (cấp quyền 1 lần duy nhất).
5. **Xong!** Toàn bộ vùng tick biến thành **Checkbox Pastel cỡ lớn (`14pt`)** và `onEdit(e)` tự động lưu/nạp dữ liệu mỗi khi bạn đổi **Tháng (`B5`)**, **Năm (`C5`)**, **Tuần (`F5`)** hoặc **Năm Mục Tiêu (`E3`)**!

### Bước 2: Ghim ra Màn hình chính điện thoại (Pin to Home Screen)
- **🤖 Android (Samsung / Xiaomi / Pixel):**
  1. Mở ứng dụng **Google Trang tính (Google Sheets)** → tìm file Habit Tracker Mobile của bạn.
  2. Nhấn dấu ba chấm (`...`) bên cạnh tên file → chọn **Thêm vào màn hình chính (Add to Home Screen)**.
  3. Từ giờ chỉ cần chạm icon ngoài màn hình chính là mở thẳng tab **`📱 Tuần Này`** theo chiều dọc!
- **🍎 iPhone / iPad (iOS):**
  1. Trong app **Google Trang tính**, nhấn `...` → **Sao chép đường liên kết (Copy link)**.
  2. Mở ứng dụng **Phím tắt (Shortcuts)** của Apple → bấm **`+`** → chọn **Mở URL (Open URLs)** → dán link Google Sheets vừa copy.
  3. Nhấn nút Chia sẻ (Share) → **Thêm vào Màn hình chính (Add to Home Screen)**, đặt tên *Habit Tracker* & chọn icon yêu thích!

---

## 💻 Cách Thủ Công 3 Giây (Không Cần Apps Script)

Nếu không muốn dùng Apps Script:
- **Bản Mobile Portrait:** Chọn vùng ô `C21:I35` trên `📱 Tuần Này`, `B16:B30` trên `📝 Việc Hôm Nay`, và `B11:B22` trên `🎯 Mục Tiêu & Thành Tựu` → menu **Chèn (Insert) → Hộp kiểm (Checkbox)**.
- **Bản Desktop:** Chọn vùng ô `C17:AG36` trên `Monthly Tracker`, `B9:B28` trên `📝 Nhiệm Vụ Ngày`, và `B6:B25` trên `🎯 Yearly Goals & Habits` → **Chèn (Insert) → Hộp kiểm (Checkbox)**.

---

## ✨ Mẹo Hay
- **Hoạt ảnh `=IMAGE()` động 6, 7 hoặc 8 giai đoạn:** Cả 7 icon ngày, Weekly Hero, Yearly Goals Hero & Huy hiệu tự biến đổi từ `Stage 0` (0%) → `Stage 5 / 6 / 7 Ultra ✨` (100%) theo đúng tiến độ thực tế.
- **Đổi bộ ảnh riêng:** Vào tab `📖 Hướng Dẫn`, dán URL thư mục chứa 6 (`stage_0..5.png`), 7 (`stage_0..6.png`), hoặc 8 (`stage_0..7.png`) ảnh vào ô vàng **`CFG_IMG_BASE`**.
