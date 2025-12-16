# 📂 Thư mục `data/`

Thư mục `data/` lưu trữ toàn bộ dữ liệu sử dụng trong dự án **Phân tích và Dự báo xu hướng dịch tễ COVID-19 bằng kỹ thuật Phân cụm và Mô hình học máy**.

Dữ liệu tại đây được chia thành hai nhóm chính: **Raw** (Thô) và **Processed** (Đã xử lý).

---

## 📌 1. `raw/` – Dữ liệu gốc (chưa xử lý)
Thư mục `raw/` chứa dữ liệu nguyên bản được tải trực tiếp từ nguồn, dùng để đối chiếu khi cần thiết.

- **Nguồn:** Tổ chức Y tế Thế giới (WHO)
- **Dataset:** *WHO COVID-19 Global Daily Data*
- **File chính:** `who-covid-19-global-daily-data.csv`

### ✅ Đặc điểm:
- Giữ nguyên bản, không chỉnh sửa, không xóa dòng.
- Dùng làm mốc so sánh để đảm bảo tính minh bạch.

---

## 📌 2. `processed/` – Dữ liệu sau tiền xử lý (QUAN TRỌNG)
Thư mục này chứa **3 file dữ liệu chính** đã qua làm sạch, xử lý missing value, nội suy và tạo đặc trưng (Feature Engineering). 

> **⚠️ Lưu ý:** Các file được nén định dạng `.gz` để tối ưu dung lượng. Thư viện `pandas` đọc trực tiếp được (không cần giải nén).

### 📄 File 1: `01_clean_daily_timeseries.csv.gz`
- **Mô tả:** Dữ liệu chuỗi thời gian hàng ngày của **tất cả các quốc gia** có trong dataset.
- **Xử lý:** Đã xử lý số âm, nội suy tuyến tính (linear interpolation) cho dữ liệu thiếu.
- **Mục đích:** Dùng cho Phân tích khám phá chung (EDA) toàn cầu.

### 📄 File 2: `02_country_population_summary.csv.gz`
- **Mô tả:** Dữ liệu tổng hợp tĩnh theo từng quốc gia (mỗi dòng là 1 nước).
- **Các cột quan trọng:** `Total_Cases`, `Total_Deaths`, `Fatality_Rate`, `Cases_per_1M`, `Population`.
- **Mục đích:** Dùng làm đầu vào cho thuật toán **Phân cụm (K-Means)** để gom nhóm các nước.

### 📄 File 3: `03_4_country_population_summary.csv.gz`
- **Mô tả:** Dữ liệu chuỗi thời gian chi tiết chỉ của **4 quốc gia trọng điểm**: Việt Nam, Trung Quốc, Ấn Độ, Hoa Kỳ.
- **Xử lý:** Đã lọc riêng, sắp xếp theo thời gian chuẩn.
- **Mục đích:** Dùng làm đầu vào huấn luyện các mô hình dự báo (**Linear Regression, Random Forest, XGBoost**).

---

## 📌 3. Hướng dẫn Load dữ liệu (Python)

```python
import pandas as pd

# 1. Load dữ liệu toàn cầu (Cho EDA)
df_all = pd.read_csv("data/processed/01_clean_daily_timeseries.csv.gz")

# 2. Load dữ liệu để chạy Phân cụm (Clustering)
df_cluster = pd.read_csv("data/processed/02_country_population_summary.csv.gz")

# 3. Load dữ liệu để chạy Mô hình dự báo (Modeling)
df_model = pd.read_csv("data/processed/03_4_country_population_summary.csv.gz")

