

## 📂 Cấu trúc thư mục đồ án
Group/who-covid-19/
      
      ├── data/
      │   ├── raw/                # Dữ liệu gốc WHO (không chỉnh sửa)
      │   │   └── who-covid19-global-daily-data.csv
      │   ├── processed/          # Dữ liệu sau tiền xử lý
      │   │   └── vn_processed.csv
      │   └── README.md           # Mô tả nguồn dữ liệu
      
      ├── notebooks/              # Các file Jupyter Notebook
      │   ├── 01_data_preprocessing.ipynb
      │   ├── 02_EDA_analysis.ipynb
      │   ├── 03_ml_models.ipynb
      │   └── 04_visualization_dashboard.ipynb
      
      ├── src/                    # Code Python chính của project
      │   ├── preprocessing.py
      │   ├── models.py
      │   ├── evaluation.py
      │   └── utils.py
      
      ├── dashboard/
      │   ├── powerbi/            # Nếu dùng Power BI
      │   ├── tableau/            # Nếu dùng Tableau
      │   └── dash_app/           # Nếu dùng Dash/Streamlit
      
      ├── results/
      │   ├── predictions/        # Output dự báo
      │   ├── model_metrics/      # Bảng đánh giá
      │   └── charts/             # Hình biểu đồ
      
      ├── requirements.txt        # Các thư viện Python
      ├── README.md               # Giới thiệu repo
      └── .gitignore              # Ignore file


