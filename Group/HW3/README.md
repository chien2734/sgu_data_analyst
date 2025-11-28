# PHÂN TÍCH MẠNG XÃ HỘI: MẠNG ĐỒNG HIỆN HASHTAG YOUTUBE

## 📌 Giới thiệu (Overview)
Dự án này thực hiện thu thập và phân tích mạng xã hội (Social Network Analysis - SNA) dựa trên dữ liệu từ YouTube. Cụ thể, đề tài tập trung vào việc xây dựng **mạng đồng hiện (Co-occurrence Network)** của các từ khóa (Hashtags) trong chủ đề **Trí tuệ nhân tạo**.

Mục tiêu là tìm ra các chủ đề trung tâm, xu hướng nội dung và các cộng đồng (nhóm chủ đề) có liên quan chặt chẽ với nhau trên nền tảng YouTube.

## 📂 Cấu trúc dự án

    ├── chart/                                  # Chứa các biểu đồ trực quan hóa xuất ra từ Python
    │   ├── centrality_correlation_updated.png  # Ma trận tương quan giữa các chỉ số trung tâm (Heatmap)
    │   ├── centrality_top10_all_5_metrics.png  # Biểu đồ thanh so sánh Top 10 nút quan trọng
    │   ├── community_k_core_decomposition.png  # Biểu đồ phân rã K-Core (Sự bền vững của mạng)
    │   ├── community_network_layout_preview.png# Hình ảnh xem trước bố cục mạng phân chia cộng đồng
    │   ├── dist_clustering.png                 # Phân phối hệ số phân cụm
    │   └── dist_degree_regression.png          # Phân phối bậc và đường hồi quy (Kiểm định Power Law)
    │
    ├── data/                                   # Chứa dữ liệu thô và đã xử lý
    │   └── youtube_network_data.csv            # Dữ liệu cạnh (Edge List) thu thập từ API
    │
    ├── gephi/                                  # Các file dành riêng cho phần mềm Gephi
    │   └── youtube_network_community.gexf      # File đồ thị đã tích hợp thông tin cộng đồng & K-core
    │
    ├── src/                                    # Mã nguồn (Source Code)
    │   ├── analysis.py                         # Code phân tích mạng, tính chỉ số và vẽ biểu đồ
    │   └── data_collection.py                  # Code thu thập dữ liệu từ YouTube API
    │
    └── README.md                               # Tài liệu báo cáo và hướng dẫn sử dụng

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