# FinDash 🇻🇳 - Bảng điều khiển Tài chính VN-INDEX 30

Đây là một bảng điều khiển (dashboard) tài chính được xây dựng bằng Streamlit, chuyên biệt cho thị trường Việt Nam. Ứng dụng này cho phép người dùng phân tích chi tiết các mã cổ phiếu trong rổ VN30.

Dự án này được xây dựng dựa trên logic của file `findash_app.py` (một dashboard mẫu cho thị trường Mỹ) và file `findash_demo.ipynb` (một notebook thử nghiệm). Toàn bộ các hàm lấy dữ liệu cho thị trường Mỹ (như `yahoo_fin`) đã được thay thế bằng các hàm của thư viện `vnstock` (phiên bản 3.x) để đảm bảo tương thích với dữ liệu Việt Nam.

## Tính năng

Ứng dụng được chia thành 7 tab chức năng chính:

1.  **Tab 1: Tổng quan (Summary):**
    * Hiển thị thông tin cơ bản của doanh nghiệp (Ngành nghề, Vốn hóa, v.v.) được lấy từ `Vnstock().stock(...).company.overview()`.
    * Biểu đồ giá 5 năm (dạng `area`) của cổ phiếu được chọn, lấy từ `Vnstock().stock(...).quote.history()`.

2.  **Tab 2: Biểu đồ Kỹ thuật (Chart):**
    * Biểu đồ giá tương tác với các tùy chọn phạm vi ngày và tần suất (`1D`, `1W`, `1M`).
    * Lựa chọn hiển thị dạng **Đường (Line)** hoặc **Nến (Candle)**.
    * Tự động tính toán và vẽ đường **SMA 50** (Trung bình động 50 kỳ).
    * Hiển thị **Khối lượng (Volume)** trên một trục Y thứ hai.

3.  **Tab 3: Thống kê (Statistics):**
    * Hiển thị các chỉ số tài chính quan trọng (P/E, ROA, ROE,...) theo Hàng năm hoặc Hàng quý, lấy từ hàm `Vnstock().stock(...).finance.ratio()`.
    * *(Lưu ý: Chức năng định dạng số lớn (thêm dấu ngắt) đã bị tạm hoãn để fix sau.)*

4.  **Tab 4: Báo cáo Tài chính (Financials):**
    * Cho phép người dùng xem chi tiết 3 báo cáo tài chính chính:
        * Báo cáo Kết quả Kinh doanh (`.income_statement`).
        * Bảng Cân đối Kế toán (`.balance_sheet`).
        * Báo cáo Lưu chuyển Tiền tệ (`.cash_flow`).
    * Tùy chọn xem theo Hàng năm hoặc Hàng quý.

5.  **Tab 5: Phân tích (Analysis):**
    * *Lưu ý: Chức năng này được điều chỉnh từ file `findash_demo.ipynb`.*
    * Thực hiện "cào" (scrape) dữ liệu trực tiếp từ trang `finance.yahoo.com/analysis` của mã được chọn.
    * *(Hạn chế: Yahoo Finance gần như không có dữ liệu này cho các mã cổ phiếu Việt Nam).*
    * Chức năng này hiện tại vẫn chưa hoàn chỉnh. Hiện tại chỉ hiển thị các cố phiểu đang có.

6.  **Tab 6: Mô phỏng Monte Carlo:**
    * Chạy mô phỏng Monte Carlo (dựa trên logic của `findash_app.py`) để dự đoán kịch bản giá trong 30-90 ngày tới.
    * Tính toán độ biến động (`volatility`) dựa trên 90 ngày giao dịch gần nhất (lấy bằng `vnstock`).
    * Hiển thị biểu đồ phân bổ và tính toán **Value at Risk (VaR) 95%**.
    * Đã điều chỉnh để hiển thị đúng đơn vị **VND** (nhân 1000).

7.  **Tab 7: Xu hướng Portfolio:**
    * Cho phép người dùng chọn nhiều mã cổ phiếu trong rổ VN30.
    * **Chuẩn hóa (Normalize)** giá của tất cả cổ phiếu về mốc `1.0` tại thời điểm 5 năm trước.
    * Vẽ biểu đồ đường so sánh hiệu suất tăng trưởng của các cổ phiếu đó một cách công bằng.

## Hướng dẫn Cài đặt & Khởi chạy

### 1. Yêu cầu Bắt buộc
* **Python 3.10 trở lên:** Thư viện `vnstock` v3.x (và các thư viện phụ trợ như `vnai`) yêu cầu Python 3.10+. Dự án này **sẽ thất bại** nếu chạy trên Python 3.9 hoặc cũ hơn.

### 2. Thiết lập thư viện
     Cài đặt tất cả các thư viện cần thiết vào môi trường này:
    ```bash
    pip install streamlit pandas numpy plotly matplotlib requests 
    pip install git+https://github.com/thinh-vu/vnstock
    ```
    *(Lưu ý: `vnstock` sẽ tự động cài `vnai` và `vnstock_ezchart` làm phụ thuộc).*
