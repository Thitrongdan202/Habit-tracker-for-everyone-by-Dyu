# 🛠️ Hướng Dẫn Sử Dụng Bộ Macro VBA (Dành Cho Excel Bản Cũ & Offline Pro)

> **Lưu ý nhanh cho phiên bản 2.0 Final:**
> Toàn bộ **10 mẫu chính trong [`templates/`](../templates/)** ĐÃ hoạt động **100% Offline trên mọi phiên bản Excel (2016 / 2019 / 2021 / 365 • Windows & Mac)** bằng Linked Pictures & Form Control Checkboxes — **KHÔNG cần cài VBA hay Macro**!
> Ngoài ra, người dùng Excel 365 có thêm 10 bản ảnh nhúng trực tiếp vào ô trong [`templates/pro_macro/`](../templates/pro_macro/).

Bộ script VBA trong thư mục này dành cho người dùng **Excel 2016 / 2019 / 2021** (chưa có hàm `=IMAGE()` và Checkbox gốc) hoặc muốn thêm tính năng **nhấn đúp để tick nhanh, thông báo ăn mừng chuỗi 7/14/21/30 ngày, nút Reset tháng mới & xuất PDF 1 trang**.

## Cách cài đặt trong 3 bước (30 giây)

1. Mở file template `.xlsx` bất kỳ → nhấn **`Alt + F11`** để mở cửa sổ **VBA Editor**.
2. Chọn **`File → Import File...`** → chọn file **`HabitTrackerPro.bas`** trong thư mục `vba_scripts/`.
3. *(Tùy chọn — bật sự kiện tự động đổi ảnh & chúc mừng)*:
   - Nhấn đúp vào tên sheet Tracker chính (vd: `🌻 Monthly Tracker`) ở cây thư mục bên trái.
   - Copy nội dung từ **`SheetTrackerEvents.cls`** (từ dòng `Option Explicit` trở xuống) dán vào cửa sổ code của sheet đó.
4. Nhấn **`Ctrl + S`** → chọn lưu định dạng **`Excel Macro-Enabled Workbook (*.xlsm)`**.

## Các Macro đi kèm (`Alt + F8` để chạy)

| Tên Macro | Chức năng |
|---|---|
| `SetupOfflineSprites` | Chọn thư mục ảnh `assets/<theme>/` để nhúng 6 ảnh PNG vào sheet ẩn `_SpritesVBA` (chạy 100% offline trên Excel cũ) |
| `RefreshAllOfflineStages` | Cập nhật lại toàn bộ 31 biểu tượng hoạt ảnh theo `% COMPLETED` hiện tại |
| `ResetCurrentMonth` | Đặt lại sạch sẽ toàn bộ vùng checkbox `C17:AG36` cho tháng mới mà **không làm hỏng công thức** |
| `ExportDashboardPDF` | Xuất bảng dashboard hiện tại ra file PDF 1 trang ngang sắc nét |
