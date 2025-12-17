import streamlit as st
import pandas as pd
import plotly.express as px
import os

# -----------------------------------------------------------------------------
# 1. CẤU HÌNH TRANG & CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="COVID-19 Analytics Dashboard",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
    .stMetric_value {
        font-size: 2rem !important;
        color: #ff4b4b;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. HÀM LOAD DỮ LIỆU (ĐÃ SỬA ĐƯỜNG DẪN)
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    try:
        # --- ĐOẠN SỬA QUAN TRỌNG ---
        # File của bạn: .../who-covid-19/dashboard/dash_app.py
        current_file = os.path.abspath(__file__)

        # Đi ngược 1 cấp -> vào folder 'dashboard'
        dashboard_dir = os.path.dirname(current_file)

        # Đi ngược thêm 1 cấp nữa -> vào folder gốc 'who-covid-19' (Nơi chứa data)
        project_root = os.path.dirname(dashboard_dir)

        # Tạo đường dẫn đến data
        data_path = os.path.join(project_root, 'data', 'processed')
        # ---------------------------

        # 1. Load Daily Data
        df_daily = pd.read_csv(os.path.join(data_path, '01_clean_daily_timeseries.csv.gz'), compression='gzip')
        df_daily['Date_reported'] = pd.to_datetime(df_daily['Date_reported'])

        # 2. Load Summary Data
        df_summary = pd.read_csv(os.path.join(data_path, '02_country_population_summary.csv.gz'), compression='gzip')

        # 3. Load 4 Countries Data
        df_4 = pd.read_csv(os.path.join(data_path, '03_4_country_population_summary.csv.gz'), compression='gzip')
        df_4['Date_reported'] = pd.to_datetime(df_4['Date_reported'])

        return df_daily, df_summary, df_4

    except FileNotFoundError:
        return None, None, None


# Load dữ liệu
df_daily, df_summary, df_4 = load_data()

# Kiểm tra nếu không tìm thấy file thì báo lỗi chi tiết để debug
if df_daily is None:
    st.error(f"⚠️ VẪN LỖI ĐƯỜNG DẪN! Code đang tìm file tại: {os.path.dirname(os.path.abspath(__file__))}")
    st.warning(
        "Hãy đảm bảo bạn đã chạy file '01_data_preprocessing.ipynb' để tạo ra 3 file .gz trong thư mục data/processed/")
    st.stop()

# -----------------------------------------------------------------------------
# 3. SIDEBAR - THANH ĐIỀU HƯỚNG
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2785/2785819.png", width=100)
    st.title("COVID-19 Analytics")
    st.info("Nhóm 02: Chiến, An, Diễm, Anh")

    st.markdown("---")
    menu = st.radio(
        "📌 CHỌN CHỨC NĂNG:",
        ["1. Tổng quan (Overview)", "2. Phân cụm (Clustering)", "3. Dự báo (Prediction)"]
    )
    st.markdown("---")
    st.caption("Dữ liệu nguồn: WHO Global Data")

# -----------------------------------------------------------------------------
# 4. TAB 1: TỔNG QUAN (OVERVIEW)
# -----------------------------------------------------------------------------
if menu == "1. Tổng quan (Overview)":
    st.header("🌍 Tổng quan Tình hình Dịch tễ Toàn cầu")

    # --- KPI CARDS ---
    col1, col2, col3, col4 = st.columns(4)

    total_cases = df_summary['Total_Cases'].sum()
    total_deaths = df_summary['Total_Deaths'].sum()
    avg_fatality = df_summary['Fatality_Rate'].mean()
    n_countries = df_summary['Country'].nunique()

    col1.metric("Số Quốc gia", f"{n_countries}")
    col2.metric("Tổng Ca nhiễm", f"{total_cases:,.0f}")
    col3.metric("Tổng Tử vong", f"{total_deaths:,.0f}")
    col4.metric("Tỷ lệ Tử vong TB", f"{avg_fatality:.2f}%")

    st.markdown("---")

    # --- BIỂU ĐỒ 1: BẢN ĐỒ NHIỆT ---
    st.subheader("📍 Bản đồ mức độ lây nhiễm")
    fig_map = px.choropleth(
        df_summary,
        locations="Country",
        locationmode="country names",
        color="Total_Cases",
        hover_name="Country",
        color_continuous_scale="Reds",
        title="Phân bố Tổng số ca nhiễm trên thế giới"
    )
    fig_map.update_layout(height=500, margin={"r": 0, "t": 30, "l": 0, "b": 0})
    st.plotly_chart(fig_map, use_container_width=True)

    # --- BIỂU ĐỒ 2 & 3: XU HƯỚNG & TOP 10 ---
    c1, c2 = st.columns([2, 1])

    with c1:
        st.subheader("📈 Xu hướng Ca nhiễm mới (Toàn cầu)")
        global_trend = df_daily.groupby('Date_reported')['New_cases'].sum().reset_index()
        global_trend['MA7'] = global_trend['New_cases'].rolling(window=7).mean()

        fig_trend = px.line(global_trend, x='Date_reported', y='New_cases', title='Diễn biến dịch theo ngày')
        fig_trend.add_scatter(x=global_trend['Date_reported'], y=global_trend['MA7'], mode='lines',
                              name='Trung bình 7 ngày')
        st.plotly_chart(fig_trend, use_container_width=True)

    with c2:
        st.subheader("🏆 Top 10 Quốc gia")
        top_10 = df_summary.sort_values('Total_Cases', ascending=False).head(10)
        fig_bar = px.bar(top_10, x='Total_Cases', y='Country', orientation='h', title='Top 10 Ca nhiễm cao nhất')
        fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)

# -----------------------------------------------------------------------------
# 5. TAB 2: PHÂN CỤM (CLUSTERING)
# -----------------------------------------------------------------------------
elif menu == "2. Phân cụm (Clustering)":
    st.header("🧩 Phân nhóm Quốc gia (K-Means Clustering)")
    st.markdown("Mục tiêu: Gom nhóm các quốc gia có đặc điểm dịch tễ tương đồng.")

    if 'Cluster' in df_summary.columns:
        color_col = 'Cluster'
        st.success("✅ Đã cập nhật dữ liệu Phân cụm!")
    else:
        color_col = 'WHO_region'
        st.warning("⚠️ Đang hiển thị màu theo Khu vực (Demo). Chờ cập nhật kết quả 'Cluster'.")

    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("Biểu đồ Phân tán (Scatter Plot)")
        x_axis = st.selectbox("Chọn trục X:", ["Total_Cases", "Population", "Total_Deaths"], index=0)
        y_axis = st.selectbox("Chọn trục Y:", ["Fatality_Rate", "Deaths_per_1M", "Cases_per_1M"], index=0)

        fig_scatter = px.scatter(
            df_summary,
            x=x_axis, y=y_axis, size="Population", color=color_col,
            hover_name="Country", log_x=True,
            title=f"Tương quan giữa {x_axis} và {y_axis}"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col2:
        st.subheader("Chi tiết Nhóm")
        st.write(df_summary[color_col].value_counts())

# -----------------------------------------------------------------------------
# 6. TAB 3: DỰ BÁO (PREDICTION)
# -----------------------------------------------------------------------------
elif menu == "3. Dự báo (Prediction)":
    st.header("🤖 Mô hình Dự báo Máy học")

    col_sel, col_kpi = st.columns([1, 3])
    with col_sel:
        selected_country = st.selectbox("🏳️ Chọn Quốc gia:", df_4['Country'].unique())

    country_data = df_4[df_4['Country'] == selected_country]

    st.subheader(f"Diễn biến thực tế tại {selected_country}")
    fig_pred = px.line(country_data, x='Date_reported', y='New_cases', title="Dữ liệu lịch sử")
    fig_pred.add_scatter(x=country_data['Date_reported'], y=country_data['New_cases_MA7'], mode='lines',
                         name='MA7 (Smooth)')
    st.plotly_chart(fig_pred, use_container_width=True)

    st.markdown("---")
    st.info("⚠️ Khu vực này sẽ hiển thị kết quả dự báo khi tích hợp file từ folder results/")
