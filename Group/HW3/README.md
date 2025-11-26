# PHÂN TÍCH MẠNG XÃ HỘI: MẠNG ĐỒNG HIỆN HASHTAG YOUTUBE

## 📌 Giới thiệu (Overview)
Dự án này thực hiện thu thập và phân tích mạng xã hội (Social Network Analysis - SNA) dựa trên dữ liệu từ YouTube. Cụ thể, đề tài tập trung vào việc xây dựng **mạng đồng hiện (Co-occurrence Network)** của các từ khóa (Hashtags) trong chủ đề **Trí tuệ nhân tạo**.

Mục tiêu là tìm ra các chủ đề trung tâm, xu hướng nội dung và các cộng đồng (nhóm chủ đề) có liên quan chặt chẽ với nhau trên nền tảng YouTube.

## 📂 Cấu trúc dự án
    cập nhật sau

## 🛠 Công nghệ sử dụng
* Ngôn ngữ: Python 3.x

* Thu thập dữ liệu: google-api-python-client (YouTube Data API v3)

* Xử lý dữ liệu: pandas, numpy

* Phân tích mạng: networkx

* Phát hiện cộng đồng: python-louvain

* Trực quan hóa: matplotlib (biểu đồ thống kê), Gephi (vẽ đồ thị mạng lưới).

## 🚀 Hướng dẫn cài đặt & Chạy
### 1. Cài đặt thư viện
Chạy lệnh sau để cài đặt các gói phụ thuộc:
`pip install google-api-python-client pandas networkx matplotlib python-louvain scipy`

### 2.Phân tích dữ liệu
Chạy file phân tích để tính toán các chỉ số mạng:
`python analysis.py`

*Kết quả*: Chương trình sẽ in ra màn hình các thông số:

* Đường kính, Bán kính, Mật độ mạng.

* Top Node theo Degree Centrality, Betweenness Centrality, PageRank.

* Chỉ số Modularity và danh sách các cộng đồng.

* Tự động lưu biểu đồ degree_distribution.png.

### 3. Trực quan hóa với Gephi
1. Mở phần mềm Gephi.

2. Import file youtube_network_data.csv (Chế độ: Undirected Graph).

3. Sử dụng Layout: Force Atlas 2.

4. Tô màu node theo Modularity Class (Cộng đồng).

5. Kích thước node theo Degree (Độ phổ biến).