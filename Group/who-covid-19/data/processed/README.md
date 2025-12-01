# 📂 Dữ liệu Dự báo Dịch tễ COVID-19 (Đã xử lý)

Thư mục này chứa dữ liệu đã qua các bước tiền xử lý, làm sạch và chuẩn hóa từ nguồn **WHO** và **World Bank**. Dữ liệu sẵn sàng để sử dụng cho các tác vụ Thống kê mô tả, EDA và Huấn luyện mô hình Machine Learning.

## 1. Danh sách File dữ liệu

Chúng ta có 2 file dữ liệu chính (được nén định dạng `.gz` để tối ưu dung lượng):

| Tên File | Loại dữ liệu | Số dòng (ước tính) | Mục đích sử dụng chính |
| :--- | :--- | :--- | :--- |
| **`01_clean_daily_timeseries.csv.gz`** | Chuỗi thời gian (Daily) | ~500,000 | **EDA (Biểu đồ theo thời gian)** & **Modeling (Dự báo)** |
| **`02_country_population_summary.csv.gz`** | Tổng hợp theo Quốc gia | ~230 | **Thống kê mô tả (So sánh các nước)** |

> **⚠️ Lưu ý quan trọng: KHÔNG CẦN GIẢI NÉN** thủ công. Thư viện `pandas` trong Python có thể đọc trực tiếp file `.gz`.

---

## 2. Chi tiết từng File

### 📄 File 1: `01_clean_daily_timeseries.csv.gz`
Chứa dữ liệu diễn biến dịch bệnh theo từng ngày của từng quốc gia. Dữ liệu đã được **nội suy (interpolation)** để lấp đầy giá trị thiếu và loại bỏ các giá trị âm vô lý.

**Các cột quan trọng:**
* `Date_reported`: Ngày ghi nhận.
* `Country`: Tên quốc gia.
* `New_cases`, `New_deaths`: Số ca nhiễm/tử vong mới trong ngày.
* `Cumulative_cases`: Tổng số ca tích lũy.
* **`New_cases_MA7`**: Trung bình trượt 7 ngày của số ca nhiễm (Dùng để vẽ biểu đồ mượt hơn, giảm nhiễu).
* **`Growth_Rate`**: Tốc độ tăng trưởng (%) so với ngày hôm trước (Dùng để xem tốc độ lây lan).

**👉 Dành cho:**
* **EDA:** Vẽ biểu đồ đường (Line plot) xem xu hướng dịch bệnh tăng giảm theo thời gian.
* **Modeling:** Dùng làm đầu vào để tạo thêm các biến trễ (Lag features) và chạy mô hình dự báo.

---

### 📄 File 2: `02_country_population_summary.csv.gz`
Chứa số liệu tổng kết tĩnh (tính đến ngày mới nhất) của mỗi quốc gia, đã được ghép với dữ liệu **Dân số (Population)**. Đã loại bỏ các thực thể không phải quốc gia (như tàu du lịch).

**Các cột quan trọng:**
* `Total_Cases`, `Total_Deaths`: Tổng số ca nhiễm và tử vong.
* `Population`: Dân số quốc gia.
* **`Cases_per_1M`**: Số ca nhiễm trên 1 triệu dân (Dùng để so sánh mức độ lây nhiễm giữa nước lớn và nước nhỏ).
* **`Fatality_Rate`**: Tỷ lệ tử vong (%).

**👉 Dành cho:**
* **Thống kê:** Vẽ biểu đồ cột (Bar chart) so sánh Top 10 nước, bản đồ nhiệt (Heatmap) hoặc so sánh tỷ lệ tử vong giữa các khu vực (WHO Region).

---

## 3. Hướng dẫn sử dụng (Code Python)

Dưới đây là đoạn code mẫu để các bạn load dữ liệu vào Colab/Jupyter Notebook:

```python
import pandas as pd

# 1. Đọc file Chuỗi thời gian (Cho EDA & Modeling)
# Pandas tự động nhận diện đuôi .gz để giải nén
df_daily = pd.read_csv("01_clean_daily_timeseries.csv.gz")

# Convert lại cột ngày tháng (để chắc chắn)
df_daily['Date_reported'] = pd.to_datetime(df_daily['Date_reported'])

print("Dữ liệu Daily:", df_daily.shape)
display(df_daily.head())

# ---------------------------------------------------------

# 2. Đọc file Tổng hợp Quốc gia (Cho Thống kê mô tả)
df_summary = pd.read_csv("02_country_population_summary.csv.gz")

print("Dữ liệu Summary:", df_summary.shape)
display(df_summary.head())
