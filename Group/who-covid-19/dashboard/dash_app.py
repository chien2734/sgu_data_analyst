import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import numpy as np

# -----------------------------------------------------------------------------
# 1. CẤU HÌNH TRANG
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="COVID-19 Analytics Dashboard",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS chỉnh font chữ KPI cho to rõ
st.markdown("""
<style>
    .stMetric_value {
        font-size: 1.8rem !important;
        color: #ff4b4b;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. HÀM LOAD & XỬ LÝ DỮ LIỆU
# -----------------------------------------------------------------------------
@st.cache_data
def load_and_merge_data():
    try:
        # Tự động tìm đường dẫn
        current_file = os.path.abspath(__file__)
        dashboard_dir = os.path.dirname(current_file)
        project_root = os.path.dirname(dashboard_dir)
        data_path = os.path.join(project_root, 'data', 'processed')

        path_cluster = os.path.join(data_path, 'timeseries_with_clusters.csv')
        path_summary = os.path.join(data_path, '02_country_population_summary.csv.gz')

        # Kiểm tra file tồn tại
        if not os.path.exists(path_cluster) or not os.path.exists(path_summary):
            st.error("⚠️ Thiếu file dữ liệu trong folder data/processed/")
            return None, None, None

        # Đọc dữ liệu
        df_ts = pd.read_csv(path_cluster)
        df_ts['Date_reported'] = pd.to_datetime(df_ts['Date_reported'])
        df_summary = pd.read_csv(path_summary, compression='gzip')

        # Hợp nhất (Merge) Cluster vào dữ liệu tổng hợp
        cluster_map = df_ts[['Country', 'Cluster']].drop_duplicates()
        df_static = df_summary.merge(cluster_map, on='Country', how='left')

        # Xử lý Cụm -1 (Những nước không được phân cụm)
        df_static['Cluster'] = df_static['Cluster'].fillna(-1).astype(int).astype(str)
        df_static['Cluster'] = df_static['Cluster'].replace('-1', 'Chưa phân cụm')

        # Tính Tỷ lệ tử vong (Fatality Rate)
        df_static['Fatality_Rate'] = (df_static['Total_Deaths'] / df_static['Total_Cases']) * 100

        # Lọc dữ liệu 4 nước trọng điểm cho phần Dự báo
        target_countries = ["Viet Nam", "China", "India", "United States of America"]
        df_4 = df_ts[df_ts['Country'].isin(target_countries)].copy()

        return df_ts, df_static, df_4

    except Exception as e:
        st.error(f"Lỗi khi xử lý dữ liệu: {e}")
        return None, None, None


# Gọi hàm load dữ liệu
df_ts, df_static, df_4 = load_and_merge_data()

# Nếu không có dữ liệu thì dừng app
if df_ts is None:
    st.stop()

# -----------------------------------------------------------------------------
# 3. SIDEBAR (THANH ĐIỀU HƯỚNG)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2785/2785819.png", width=80)
    st.title("COVID-19 Analytics")
    st.caption("Nhóm 02: Chiến, An, Diễm, Anh")
    st.markdown("---")

    menu = st.radio(
        "📌 MENU CHÍNH:",
        [
            "1. Tổng quan (Overview)",
            "2. Thống kê Mô tả (EDA)",
            "3. Phân tích Cụm (Clustering)",
            "4. Dự báo (Prediction)"
        ]
    )

    st.markdown("---")
    # Bộ lọc Cụm (Chỉ hiện khi chọn Tab Clustering)
    if menu == "3. Phân tích Cụm (Clustering)":
        st.write("🔍 **Bộ lọc Cụm**")
        all_clusters = sorted(df_static['Cluster'].unique())
        # Mặc định chọn tất cả trừ nhóm 'Chưa phân cụm'
        default_clusters = [c for c in all_clusters if c != 'Chưa phân cụm']

        selected_clusters = st.multiselect("Hiển thị Cụm:", all_clusters, default=default_clusters)
        df_static_filtered = df_static[df_static['Cluster'].isin(selected_clusters)]
    else:
        df_static_filtered = df_static.copy()

# -----------------------------------------------------------------------------
# 4. TAB 1: TỔNG QUAN (OVERVIEW)
# -----------------------------------------------------------------------------
if menu == "1. Tổng quan (Overview)":
    st.header("🌍 Tổng quan Dịch tễ Toàn cầu")

    # KPI Cards
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Số Quốc gia", f"{df_static['Country'].nunique()}")
    c2.metric("Tổng ca nhiễm", f"{df_static['Total_Cases'].sum():,.0f}")
    c3.metric("Tổng tử vong", f"{df_static['Total_Deaths'].sum():,.0f}")
    c4.metric("Tỷ lệ tử vong TB", f"{df_static['Fatality_Rate'].mean():.2f}%")

    st.markdown("---")

    # --- BẢN ĐỒ ---
    st.subheader("📍 Bản đồ Trực quan hóa")
    col_map, col_chart = st.columns([2, 1])

    with col_map:
        map_mode = st.radio("Chế độ xem:", ["Mặt phẳng (2D)", "Địa cầu (3D)"], horizontal=True)

        # Cấu hình dữ liệu chung cho bản đồ
        common_data = dict(
            locations=df_static['Country'],
            locationmode='country names',
            z=df_static['Total_Cases'],
            text=df_static['Country'],
            colorscale='Plasma',
            colorbar_title="Tổng ca nhiễm"
        )

        if map_mode == "Địa cầu (3D)":
            fig_map = go.Figure(data=go.Choropleth(**common_data))
            fig_map.update_layout(
                geo=dict(
                    showframe=False, showcoastlines=False,
                    projection_type='orthographic',  # 3D
                    showocean=True, oceancolor="LightBlue",
                    showland=True, landcolor="Gray",
                    bgcolor='rgba(0,0,0,0)'
                ),
                height=500, margin={"r": 0, "t": 0, "l": 0, "b": 0}
            )
        else:
            fig_map = go.Figure(data=go.Choropleth(**common_data))
            fig_map.update_layout(
                geo=dict(
                    showframe=False, showcoastlines=True,
                    projection_type='natural earth',  # 2D
                    showocean=True, oceancolor="LightBlue",
                    showland=True, landcolor="Gray",
                    bgcolor='rgba(0,0,0,0)'
                ),
                height=500, margin={"r": 0, "t": 0, "l": 0, "b": 0}
            )

        st.plotly_chart(fig_map, use_container_width=True)

    with col_chart:
        tab_c1, tab_c2 = st.tabs(["Top Ca nhiễm", "Top Tử vong"])
        with tab_c1:
            top10 = df_static.sort_values('Total_Cases', ascending=False).head(10)
            fig_bar1 = px.bar(top10, x='Total_Cases', y='Country', orientation='h',
                              color='Total_Cases', color_continuous_scale='Plasma')
            fig_bar1.update_layout(yaxis={'categoryorder': 'total ascending'}, height=450)
            st.plotly_chart(fig_bar1, use_container_width=True)

        with tab_c2:
            top10_d = df_static.sort_values('Total_Deaths', ascending=False).head(10)
            fig_bar2 = px.bar(top10_d, x='Total_Deaths', y='Country', orientation='h',
                              color='Total_Deaths', color_continuous_scale='Reds')
            fig_bar2.update_layout(yaxis={'categoryorder': 'total ascending'}, height=450)
            st.plotly_chart(fig_bar2, use_container_width=True)

# -----------------------------------------------------------------------------
# 5. TAB 2: THỐNG KÊ MÔ TẢ (EDA)
# -----------------------------------------------------------------------------
elif menu == "2. Thống kê Mô tả (EDA)":
    st.header("📊 Phân tích Khám phá Dữ liệu")

    st.subheader("1. Tương quan biến số")
    corr_cols = ['Total_Cases', 'Total_Deaths', 'Population', 'Fatality_Rate', 'Cases_per_1M']
    corr_matrix = df_static[corr_cols].corr()

    fig_corr = px.imshow(corr_matrix, text_auto=".2f", color_continuous_scale="RdBu_r",
                         title="Ma trận Tương quan")
    st.plotly_chart(fig_corr, use_container_width=True)

    st.subheader("2. Phân phối & Ngoại lệ")
    c1, c2 = st.columns(2)
    with c1:
        metric = st.selectbox("Chọn chỉ số:", corr_cols)
        fig_hist = px.histogram(df_static, x=metric, nbins=30, marginal="box",
                                color_discrete_sequence=['#FF9F43'])  # Màu cam
        st.plotly_chart(fig_hist, use_container_width=True)
    with c2:
        fig_box = px.box(df_static, y=metric, points="outliers", hover_name="Country",
                         color_discrete_sequence=['#0ABDE3'])  # Màu xanh
        st.plotly_chart(fig_box, use_container_width=True)

# -----------------------------------------------------------------------------
# 6. TAB 3: PHÂN TÍCH CỤM (KHẮC PHỤC LỖI FIG_SCATTER)
# -----------------------------------------------------------------------------
elif menu == "3. Phân tích Cụm (Clustering)":
    st.header("🧩 Kết quả Phân cụm (K-Means)")

    # --- BẢN ĐỒ CỤM ---
    st.subheader("🗺️ Bản đồ Phân bố Cụm")

    color_map = px.colors.qualitative.Bold  # Màu sắc rõ ràng

    fig_cluster_map = px.choropleth(
        df_static_filtered,
        locations="Country",
        locationmode="country names",
        color="Cluster",
        hover_name="Country",
        hover_data=["Total_Cases", "Fatality_Rate"],
        color_discrete_sequence=color_map,
        title="Vị trí địa lý của các Cụm"
    )
    fig_cluster_map.update_layout(
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        geo=dict(
            showframe=False, showcoastlines=True,
            projection_type='natural earth',
            showocean=True, oceancolor="LightBlue",
            showland=True, landcolor="Gray",
            bgcolor='rgba(0,0,0,0)'
        )
    )
    st.plotly_chart(fig_cluster_map, use_container_width=True)

    st.markdown("---")

    # --- BIỂU ĐỒ SCATTER ---
    c1, c2 = st.columns([3, 1])
    with c1:
        st.subheader("Phân tích đặc trưng Cụm")
        x_axis = st.selectbox("Trục X:", ["Total_Cases", "Population", "Total_Deaths"], index=1)
        y_axis = st.selectbox("Trục Y:", ["Fatality_Rate", "Cases_per_1M", "Total_Cases"], index=0)

        # ĐẢM BẢO BIẾN fig_scatter ĐƯỢC ĐỊNH NGHĨA TRƯỚC KHI GỌI
        fig_scatter = px.scatter(
            df_static_filtered,
            x=x_axis, y=y_axis,
            color="Cluster",
            size="Population",
            hover_name="Country",
            log_x=True, log_y=True,
            color_discrete_sequence=color_map,  # Đồng bộ màu với bản đồ
            title=f"Mối quan hệ: {x_axis} vs {y_axis}"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with c2:
        st.subheader("Số lượng nước")
        # Đếm số lượng nước trong từng cụm
        count_data = df_static_filtered['Cluster'].value_counts().reset_index()
        count_data.columns = ['Cluster', 'Số nước']
        st.dataframe(count_data, hide_index=True)

# -----------------------------------------------------------------------------
# 7. TAB 4: DỰ BÁO (PREDICTION)
# -----------------------------------------------------------------------------
elif menu == "4. Dự báo (Prediction)":
    st.header("📈 Dự báo Xu hướng")

    if df_4.empty:
        st.warning("⚠️ Lỗi dữ liệu.")
    else:
        sel_country = st.selectbox("Quốc gia:", df_4['Country'].unique())
        country_data = df_4[df_4['Country'] == sel_country].copy()

        # Vẽ lịch sử
        fig_hist = px.line(country_data, x='Date_reported', y='New_cases', title=f"Lịch sử tại {sel_country}")
        fig_hist.update_traces(line_color='#00cec9')
        if 'New_cases_MA7' in country_data.columns:
            fig_hist.add_scatter(x=country_data['Date_reported'], y=country_data['New_cases_MA7'], mode='lines',
                                 name='MA7 (Smooth)', line=dict(color='#fdcb6e'))
        st.plotly_chart(fig_hist, use_container_width=True)

        # Demo Dự báo
        st.subheader("Dự báo (Mô phỏng)")
        model_name = st.selectbox("Mô hình:", ["XGBoost", "Random Forest", "Linear Regression"])

        recent = country_data.tail(90).reset_index(drop=True)
        noise = np.random.normal(0, 0.1, len(recent))
        base_val = recent['New_cases_MA7'] if 'New_cases_MA7' in recent else recent['New_cases']
        preds = base_val * (1 + noise)

        fig_pred = go.Figure()
        fig_pred.add_trace(
            go.Scatter(x=recent['Date_reported'], y=recent['New_cases'], name="Thực tế", line=dict(color='white')))
        fig_pred.add_trace(go.Scatter(x=recent['Date_reported'], y=preds, name=f"Dự báo ({model_name})",
                                      line=dict(dash='dot', color='#ff7675')))
        st.plotly_chart(fig_pred, use_container_width=True)
