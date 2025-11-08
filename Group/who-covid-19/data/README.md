# 📁 Thư mục `data/`  
Thư mục `data/` lưu trữ toàn bộ dữ liệu sử dụng trong dự án **Dự báo xu hướng dịch tễ COVID-19 bằng mô hình học máy từ dữ liệu WHO**.

Dữ liệu tại đây được chia thành hai nhóm chính:

---

## 📌 1. `raw/` – Dữ liệu gốc (chưa xử lý)
Thư mục `raw/` chứa dữ liệu nguyên bản được tải trực tiếp từ nguồn:

- **Tổ chức Y tế Thế giới (WHO)**  
- Dataset: *WHO COVID-19 Global Daily Data*  
- File chính:
  - `who-covid-19-global-daily-data.csv`

### ✅ Đặc điểm:
- Không chỉnh sửa bất kỳ giá trị nào.
- Dùng làm dữ liệu gốc để tái lập quy trình phân tích.
- Giúp đảm bảo tính minh bạch và khả năng kiểm chứng.

---

## 📌 2. `processed/` – Dữ liệu sau tiền xử lý
Thư mục `processed/` chứa các file được tạo ra sau khi:
- Làm sạch dữ liệu  
- Lọc theo quốc gia  
- Tạo các biến đặc trưng (lag features, rolling mean…)  
- Chuẩn hóa (nếu có)

### Ví dụ các file trong thư mục:
- `vietnam_processed.csv`
- `usa_processed.csv`
- `india_processed.csv`

### ✅ Mục đích:
- Là dữ liệu đầu vào cho mô hình học máy.
- Giảm chi phí xử lý cho các notebook/model sau này.
- Giúp nhóm làm việc nhất quán (mọi người dùng chung processed data).

---

## 📌 3. Lưu ý khi làm việc với dữ liệu

### ✅ Dữ liệu gốc **không được chỉnh sửa**  
Nếu cần thay đổi, hãy tạo file mới trong `processed/`.

### ✅ Dung lượng lớn  
Nếu file nặng, hãy **không commit vào GitHub**, mà lưu trên:
- Google Drive  
---

## 📌 4. Nguồn dữ liệu (Citation)

Nguồn dữ liệu được lấy từ:  
**World Health Organization (WHO)**  
Dataset: *WHO COVID-19 Global Data Repository*  
Link tải: https://covid19.who.int/data (tùy phiên bản)

Nếu sử dụng trong báo cáo, hãy trích dẫn:

> World Health Organization. WHO Coronavirus (COVID-19) Dashboard – Global Data. Available at: https://covid19.who.int/ (Accessed YYYY).

---

## 📌 5. Cấu trúc thư mục

