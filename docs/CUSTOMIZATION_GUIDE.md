# 🎨 Hướng Dẫn Tùy Biến Nâng Cao (Customization Guide)

Tài liệu này giúp bạn cá nhân hóa trọn bộ **6 Excel Habit Tracker Templates** theo phong cách riêng mà vẫn giữ nguyên 100% độ chính xác của công thức, biểu đồ và hoạt ảnh tăng trưởng.

---

## 1. Cách thêm / sửa / xóa thói quen mà KHÔNG hỏng công thức

Mỗi bảng theo dõi đã được thiết kế sẵn **20 dòng thói quen** (8–10 dòng mẫu gợi ý + 10–12 dòng trống đã gắn sẵn checkbox, công thức tính `GOAL`, `DONE`, `PROGRESS`, `CURRENT STREAK`, `LONGEST STREAK` và dải công thức ẩn `BI:CM`).

- **Thêm thói quen mới:** Chỉ cần gõ tên vào bất kỳ ô trống nào trong cột `B` (từ `B17` đến `B36`) và nhập mục tiêu số ngày ở cột `GOAL` (hoặc bỏ trống nếu muốn mục tiêu là cả tháng).
- **Xóa thói quen mẫu:** Chọn tên thói quen cần xóa → nhấn phím **`Delete`** (tuyệt đối không bấm *Delete Row* để tránh ảnh hưởng vùng công thức).
- **Cần nhiều hơn 20 thói quen:**
  1. Chuột phải vào tiêu đề dòng **35** (dòng thói quen thứ 19) → chọn **Copy**.
  2. Chuột phải vào tiêu đề dòng **36** → chọn **Insert Copied Cells**.
  3. Excel sẽ tự động mở rộng phạm vi `SUM`, `COUNTIFS`, định dạng có điều kiện và kéo theo cả dải công thức tính streak ẩn ở cột `BI:CM`!

---

## 2. Cách thay đổi Tháng / Năm & Nhân bản sang tháng mới

### Đổi tháng động
- Tại thẻ tiêu đề góc trên bên trái (`B3` cho Tháng, `B5` cho Năm), bấm mũi tên chọn tháng mới (`January` – `December`) và năm (`2024` – `2040`).
- Lịch tự động tính chuẩn số ngày (28 / 29 năm nhuận / 30 / 31) và cập nhật thứ (`Mon` – `Sun`). Các ngày thừa (vd: ngày 29–31 của tháng 2) tự động ẩn màu nền và ẩn icon hoạt ảnh!

### Nhân bản sang tháng sau
1. Chuột phải vào tab Tracker chính ở thanh dưới (vd: `🌻 Monthly Tracker`) → **Move or Copy...**
2. Tick chọn **☑ Create a copy** → **OK**.
3. Đổi tên tab mới (vd: `🌻 Tháng 11`).
4. Chọn Tháng mới ở ô `B3`.
5. Quét vùng checkbox `C17:AG36` → nhấn **`Delete`** (hoặc chạy macro `ResetCurrentMonth`) để làm mới hoàn toàn!

---

## 3. Tự thay bộ ảnh hoạt ảnh 6 giai đoạn (Custom Animation)

Toàn bộ công thức ảnh trên bảng Tracker đều đọc trực tiếp từ **4 ô cấu hình màu vàng** trên tab **`📖 Hướng Dẫn`**:

| Tên vùng (Named Range) | Giá trị mặc định | Ý nghĩa |
|---|---|---|
| `CFG_IMG_BASE` | `https://raw.githubusercontent.com/Thitrongdan202/Habit-tracker-for-everyone-by-Dyu/main/assets/<theme>/` | Đường dẫn thư mục gốc chứa 6 file PNG |
| `CFG_THR_1` | `25%` | Ngưỡng chuyển từ Stage 1 → Stage 2 |
| `CFG_THR_2` | `50%` | Ngưỡng chuyển từ Stage 2 → Stage 3 |
| `CFG_THR_3` | `75%` | Ngưỡng chuyển từ Stage 3 → Stage 4 & tính vào bộ đếm **Monthly Grown** |

### Tự tạo bộ icon riêng của bạn (vd: Mèo con, Trà sữa, Cây anh đào, Pixel Art...)
1. Chuẩn bị 6 ảnh PNG nền trong suốt kích thước `256×256px` đặt tên chính xác:
   `stage_0.png`, `stage_1.png`, `stage_2.png`, `stage_3.png`, `stage_4.png`, `stage_5.png`
2. Tải lên một thư mục GitHub public (hoặc bất kỳ CDN/host nào trả về link ảnh trực tiếp).
3. Mở tab **`📖 Hướng Dẫn`** → dán đường dẫn thư mục gốc (kết thúc bằng dấu `/`) vào ô vàng **`CFG_IMG_BASE`**.
4. Nhấn `Enter` — toàn bộ 31 ngày + dải xem trước sẽ tự động thay áo mới ngay lập tức!

> **Mẹo đổi giữa 6 bộ ảnh có sẵn trong repo:** Chỉ cần đổi tên thư mục cuối trong `CFG_IMG_BASE` thành một trong 6 tên sau:
> `sunflower` · `cactus` · `lotus_stars` · `botanical` · `lavender_moon` · `focus_rocket`

---

## 4. Tương thích nền tảng & Xử lý sự cố thường gặp

| Tình huống | Nguyên nhân | Cách xử lý nhanh |
|---|---|---|
| Ô ảnh hiện `#BLOCKED!` trên Excel 365 | Excel mặc định chặn tải ảnh từ Internet lần đầu | Bấm thanh cảnh báo màu vàng phía trên **Enable Content / Trust** → hoặc mở bản Offline trong `templates/pro_macro/` |
| Ô ảnh hiện `#NAME?` | Bạn đang dùng Excel 2016/2019/2021 (chưa có hàm `=IMAGE`) | Tải file lên **Google Sheets** (miễn phí, chạy mượt 100%) hoặc cài VBA trong `vba_scripts/` |
| Ô checkbox hiện chữ `TRUE` / `FALSE` | Phiên bản Excel chưa hỗ trợ Native Checkbox | Gõ `TRUE` hoặc `✓` để đánh dấu hoàn thành — mọi công thức, streak & biểu đồ vẫn hoạt động 100%! |
| Muốn chỉnh lại bảng màu / font chữ | Sở thích cá nhân | Bạn có thể chỉnh sửa trực tiếp trong `scripts/build_all.py` rồi chạy `python scripts/build_all.py` để sinh lại toàn bộ bộ template! |
