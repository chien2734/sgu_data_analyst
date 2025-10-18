# 📊 SGU Data Analyst Project

> Dự án phân tích dữ liệu sử dụng **Python** và **Jupyter Notebook**  (hoặc Colab Google)

---

## 🧠 Giới thiệu

Dự án **SGU Data Analyst** được xây dựng nhằm mục tiêu thực hành và củng cố kiến thức về **phân tích dữ liệu** (Data Analytics) thông qua các bài lab và bài tập lớn.  
Nhóm tiến hành phân tích các bộ dữ liệu thực tế bằng **Python**, kết hợp với các thư viện mạnh mẽ như:

- **NumPy**, **Pandas**: Xử lý và phân tích dữ liệu  
- **Matplotlib**, **Seaborn**: Trực quan hóa dữ liệu  
- **Scikit-learn**: Hỗ trợ mô hình hóa và đánh giá  
- **Jupyter Notebook**: Giao diện lập trình trực quan và dễ trình bày  

---

## 📂 Cấu trúc thư mục dự án
sgu_data_analyst/

  ├── BTL01_EDA/ # Bài tập lớn 1 – Phân tích khám phá dữ liệu (EDA)
  
  ├── lab2_DataAnalytics/ # Bài tập lab2 
  
  ├── lab3_BuiDucChien_3122410039/ # Bài tập lab03
  
  └── README.md # Tệp mô tả dự án


---

## 👥 Thành viên nhóm

| Họ và Tên | Vai Trò |
|------------|----------|
| **Bùi Đức Chiến** | Trưởng nhóm | 
| **Trần Khải An** | Thành viên | 
| **Từ Nhật Anh** | Thành viên |
| **Trần Thị Kiều Diễm** | Thành viên |

> Mỗi thành viên chịu trách nhiệm cho phần nội dung notebook riêng do nhóm trưởng phân công, sau đó gộp vào repo thông qua Git.

---

## ⚙️ Hướng dẫn cài đặt và chạy

### 1. Clone repository

```bash
git clone https://github.com/chien2734/sgu_data_analyst.git
cd sgu_data_analyst
```
### 2. Tạo môi trường ảo (tùy chọn)
``` bash
python -m venv venv
source venv/bin/activate       # Trên macOS / Linux
venv\Scripts\activate          # Trên Windows
```
### 3. Cài đặt thư viện cần thiết

### Mở Jupyter Notebook
```bash
jupyter notebook
```
Sau đó mở các file trong thư mục BTL01_EDA/ hoặc Lab2_DataAnalytics/ để xem chi tiết nội dung phân tích.

### 🧩 Nội dung chính

1. Khám phá dữ liệu (EDA)

* Kiểm tra thông tin tổng quan của dataset

* Xử lý dữ liệu thiếu, dữ liệu ngoại lệ

* Phân tích thống kê mô tả

* Vẽ biểu đồ (histogram, boxplot, heatmap, pairplot, …)

2. Trực quan hóa dữ liệu

* Sử dụng thư viện Seaborn và Matplotlib

* Biểu đồ tương quan giữa các biến

* Biểu đồ xu hướng theo thời gian

3. Kết quả và nhận xét

* Tổng hợp phát hiện từ quá trình EDA

* Đề xuất hướng phân tích hoặc mô hình hóa tiếp theo

### 💡 Cộng tác (Collaboration)

* Mỗi thành viên tạo branch riêng theo tên

| Họ và Tên | branch |
|------------|----------|
| **Bùi Đức Chiến** | chien | 
| **Trần Khải An** | an | 
| **Từ Nhật Anh** | anh |
| **Trần Thị Kiều Diễm** | diem |

* Thực hiện các thay đổi trong notebook cá nhân.

* Tạo pull request để hợp nhất (merge) vào nhánh main.

* Kiểm tra xung đột trước khi merge.
### 📜 License

Dự án được phát triển cho mục đích học tập và nghiên cứu cho môn Phân tích dữ liệu tại Trường Đại học Sài Gòn (SGU).
Mọi quyền thuộc về nhóm tác giả Bùi Đức Chiến, Trần Khải An, Từ Nhật Anh, Trần Thị Kiều Diễm.
