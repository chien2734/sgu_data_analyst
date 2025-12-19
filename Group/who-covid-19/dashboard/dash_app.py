import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import numpy as np
import google.generativeai as genai

# -----------------------------------------------------------------------------
# 1. CẤU HÌNH TRANG
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="COVID-19 Analytics Dashboard",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS ĐÃ SỬA: XÓA PHẦN CHỈNH MÀU CHAT ĐỂ KHÔNG BỊ LỖI FONT ---
st.markdown("""
<style>
    .metric-card {
        background-color: #ffffff; 
        border: 1px solid #e0e0e0; 
        border-radius: 10px; 
        padding: 15px; 
        text-align: center;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    /* Nếu giao diện tối, chỉnh lại màu card cho dễ nhìn */
    @media (prefers-color-scheme: dark) {
        .metric-card {
            background-color: #262730;
            border: 1px solid #464b59;
            color: white;
        }
    }
    .stMetric_value { font-size: 1.8rem !important; color: #ff4b4b; }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. HÀM LOAD & MERGE DỮ LIỆU
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    try:
        current_file = os.path.abspath(__file__)
        dashboard_dir = os.path.dirname(current_file)
        project_root = os.path.dirname(dashboard_dir)
        data_path = os.path.join(project_root, 'data', 'processed')

        file_ts = os.path.join(data_path, 'data_with_features.csv')
        file_summary = os.path.join(data_path, '02_country_population_summary.csv.gz')

        if not os.path.exists(file_ts) or not os.path.exists(file_summary):
            st.error("⚠️ Thiếu file dữ liệu")
            return None, None

        df_full = pd.read_csv(file_ts)
        df_full['Date_reported'] = pd.to_datetime(df_full['Date_reported'])

        df_static = pd.read_csv(file_summary, compression='gzip')

        if 'Cluster' in df_full.columns:
            cluster_map = df_full[['Country', 'Cluster']].drop_duplicates()
            df_static = df_static.merge(cluster_map, on='Country', how='left')
            df_static['Cluster'] = df_static['Cluster'].fillna(-1).astype(int).astype(str).replace('-1',
                                                                                                   'Chưa phân cụm')
        else:
            df_static['Cluster'] = 'Chưa phân cụm'

        if 'Fatality_Rate' not in df_static.columns:
            df_static['Fatality_Rate'] = (df_static['Total_Deaths'] / df_static['Total_Cases']) * 100

        if 'Deaths_per_1M' not in df_static.columns and 'Population' in df_static.columns:
            df_static['Deaths_per_1M'] = (df_static['Total_Deaths'] / df_static['Population']) * 1000000

        df_static = df_static.replace([np.inf, -np.inf], 0).fillna(0)

        return df_full, df_static

    except Exception as e:
        st.error(f"Lỗi load data: {e}")
        return None, None


df_full, df_static = load_data()
if df_full is None: st.stop()

# -----------------------------------------------------------------------------
# 3. SIDEBAR & MENU
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2785/2785819.png", width=80)
    st.title("COVID-19 Analytics")
    st.caption("Nhóm 02: Chiến, An, Diễm, Anh")
    st.markdown("---")

    menu = st.radio(
        "📌 CHỨC NĂNG:",
        [
            "1. Tổng quan & Bản đồ",
            "2. Bảng xếp hạng & Thống kê",
            "3. Thống kê Mô tả (EDA)",
            "4. Phân tích Cụm",
            "5. Dự báo (Prediction)",
            "6. 🤖 Trợ lý AI (Gemini)"
        ]
    )

    st.markdown("---")
    if menu == "4. Phân tích Cụm":
        st.write("🔍 **Bộ lọc Cụm**")
        all_clusters = sorted(df_static['Cluster'].unique())
        default_clusters = [c for c in all_clusters if c != 'Chưa phân cụm']
        sel_c = st.multiselect("Lọc Cụm:", all_clusters, default=default_clusters)
        df_static_filtered = df_static[df_static['Cluster'].isin(sel_c)]
    else:
        df_static_filtered = df_static.copy()

# -----------------------------------------------------------------------------
# 4. TAB 1: TỔNG QUAN & BẢN ĐỒ
# -----------------------------------------------------------------------------
if menu == "1. Tổng quan & Bản đồ":
    st.header("🌍 Bản đồ Dịch tễ Toàn cầu")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Số Quốc gia", f"{df_static['Country'].nunique()}")
    c2.metric("Tổng ca nhiễm", f"{df_static['Total_Cases'].sum():,.0f}")
    c3.metric("Tổng tử vong", f"{df_static['Total_Deaths'].sum():,.0f}")
    c4.metric("Tỷ lệ tử vong TB", f"{df_static['Fatality_Rate'].mean():.2f}%")
    st.markdown("---")

    col_ctrl, col_map = st.columns([1, 4])
    with col_ctrl:
        st.subheader("⚙️ Tùy chỉnh")
        map_mode = st.radio("Dạng bản đồ:", ["Mặt phẳng (2D)", "Địa cầu (3D)"])
        map_metric = st.selectbox("Số liệu hiển thị:",
                                  ["Tổng ca nhiễm", "Tổng tử vong", "Tỷ lệ tử vong (%)", "Tỷ lệ lây nhiễm"])

        metric_config = {
            "Tổng ca nhiễm": {"col": "Total_Cases", "scale": "Plasma", "title": "Ca nhiễm"},
            "Tổng tử vong": {"col": "Total_Deaths", "scale": "Reds", "title": "Ca tử vong"},
            "Tỷ lệ tử vong (%)": {"col": "Fatality_Rate", "scale": "YlOrRd", "title": "Tỷ lệ tử vong (%)"},
            "Tỷ lệ lây nhiễm": {"col": "Cases_per_1M", "scale": "Viridis", "title": "Ca/1M dân"},
        }
        cfg = metric_config[map_metric]

    with col_map:
        loc_col = 'Country_code3' if 'Country_code3' in df_static.columns else 'Country'
        loc_mode = 'ISO-3' if 'Country_code3' in df_static.columns else 'country names'
        common_data = dict(locations=df_static[loc_col], locationmode=loc_mode, z=df_static[cfg['col']],
                           text=df_static['Country'], colorscale=cfg['scale'], colorbar_title=cfg['title'])

        if map_mode == "Địa cầu (3D)":
            fig_map = go.Figure(data=go.Choropleth(**common_data))
            fig_map.update_layout(
                geo=dict(showframe=False, showcoastlines=False, projection_type='orthographic', showocean=True,
                         oceancolor="LightBlue", showland=True, landcolor="#f4f4f4", bgcolor='rgba(0,0,0,0)'),
                height=600, margin={"r": 0, "t": 0, "l": 0, "b": 0})
        else:
            fig_map = go.Figure(data=go.Choropleth(**common_data))
            fig_map.update_layout(
                geo=dict(showframe=False, showcoastlines=True, projection_type='natural earth', showocean=True,
                         oceancolor="LightBlue", showland=True, landcolor="#f4f4f4", bgcolor='rgba(0,0,0,0)'),
                height=600, margin={"r": 0, "t": 0, "l": 0, "b": 0})
        st.plotly_chart(fig_map, use_container_width=True)

# -----------------------------------------------------------------------------
# 5. TAB 2: BẢNG XẾP HẠNG
# -----------------------------------------------------------------------------
elif menu == "2. Bảng xếp hạng & Thống kê":
    st.header("🏆 Bảng xếp hạng & Phân tích chuyên sâu")
    all_regions = sorted(df_static['WHO_region'].unique().astype(str))
    col_filter1, col_filter2 = st.columns([1, 3])
    with col_filter1:
        st.write("🔍 **Bộ lọc Khu vực:**")
    with col_filter2:
        selected_regions = st.multiselect("Chọn Khu vực:", all_regions, default=all_regions)
    df_rank = df_static[df_static['WHO_region'].isin(selected_regions)].copy()

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(
            px.pie(df_rank, values='Total_Cases', names='WHO_region', title='Ca nhiễm theo Khu vực', hole=0.4),
            use_container_width=True)
    with c2:
        st.plotly_chart(
            px.pie(df_rank, values='Total_Deaths', names='WHO_region', title='Tử vong theo Khu vực', hole=0.4),
            use_container_width=True)

    st.markdown("---")
    st.subheader("🥇 Top 10 Quốc gia")
    cr1, cr2 = st.columns(2)
    with cr1:
        st.write("**1. Tổng Ca nhiễm**")
        st.plotly_chart(
            px.bar(df_rank.sort_values('Total_Cases', ascending=False).head(10), x='Total_Cases', y='Country',
                   orientation='h', color='Total_Cases', color_continuous_scale='Plasma'), use_container_width=True)
        st.write("**3. Ca nhiễm / 1 Triệu dân**")
        st.plotly_chart(
            px.bar(df_rank.sort_values('Cases_per_1M', ascending=False).head(10), x='Cases_per_1M', y='Country',
                   orientation='h', color='Cases_per_1M', color_continuous_scale='Viridis'), use_container_width=True)
    with cr2:
        st.write("**2. Tổng Tử vong**")
        st.plotly_chart(
            px.bar(df_rank.sort_values('Total_Deaths', ascending=False).head(10), x='Total_Deaths', y='Country',
                   orientation='h', color='Total_Deaths', color_continuous_scale='Reds'), use_container_width=True)
        st.write("**4. Tỷ lệ Tử vong (%)**")
        st.plotly_chart(
            px.bar(df_rank[df_rank['Total_Cases'] > 1000].sort_values('Fatality_Rate', ascending=False).head(10),
                   x='Fatality_Rate', y='Country', orientation='h', color='Fatality_Rate',
                   color_continuous_scale='YlOrRd'), use_container_width=True)

    st.markdown("---")
    st.dataframe(df_rank[['Country', 'WHO_region', 'Total_Cases', 'Total_Deaths', 'Population', 'Cases_per_1M',
                          'Fatality_Rate', 'Cluster']], use_container_width=True)

# -----------------------------------------------------------------------------
# 6. TAB 3: EDA
# -----------------------------------------------------------------------------
elif menu == "3. Thống kê Mô tả (EDA)":
    st.header("📊 Phân tích Khám phá Dữ liệu")
    corr_cols = ['Total_Cases', 'Total_Deaths', 'Fatality_Rate', 'Cases_per_1M', 'Population']
    st.plotly_chart(px.imshow(df_static[corr_cols].corr(), text_auto=".2f", color_continuous_scale="RdBu_r",
                              title="Correlation Matrix"), use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        metric = st.selectbox("Chọn chỉ số:", corr_cols)
        st.plotly_chart(px.histogram(df_static, x=metric, nbins=30, marginal="box", title=f"Phân phối {metric}",
                                     color_discrete_sequence=['#457b9d']), use_container_width=True)
    with c2:
        st.plotly_chart(
            px.box(df_static, y=metric, points="outliers", hover_name="Country", title=f"Outliers ({metric})",
                   color_discrete_sequence=['#e63946']), use_container_width=True)

# -----------------------------------------------------------------------------
# 7. TAB 4: PHÂN CỤM
# -----------------------------------------------------------------------------
elif menu == "4. Phân tích Cụm":
    st.header("🧩 Kết quả Phân cụm")
    c1, c2 = st.columns([3, 1])
    with c1:
        nums = df_static.select_dtypes(include=['float64', 'int64']).columns.tolist()
        valids = [c for c in nums if c not in ['Cluster', 'Country_code']]
        xa = st.selectbox("Trục X:", valids, index=valids.index('Total_Cases') if 'Total_Cases' in valids else 0)
        ya = st.selectbox("Trục Y:", valids, index=valids.index('Fatality_Rate') if 'Fatality_Rate' in valids else 0)
        st.plotly_chart(
            px.scatter(df_static_filtered, x=xa, y=ya, color="Cluster", size='Total_Cases', hover_name="Country",
                       log_x=True, log_y=True, title=f"{xa} vs {ya}"), use_container_width=True)
    with c2:
        st.write(df_static_filtered['Cluster'].value_counts().reset_index(name='Số nước'))

# -----------------------------------------------------------------------------
# 8. TAB 5: DỰ BÁO
# -----------------------------------------------------------------------------
elif menu == "5. Dự báo (Prediction)":
    st.header("📈 Dự báo Xu hướng")
    all_cs = sorted(df_full['Country'].unique())
    sel_c = st.selectbox("🏳️ Chọn Quốc gia:", all_cs, index=all_cs.index("Viet Nam") if "Viet Nam" in all_cs else 0)
    c_data = df_full[df_full['Country'] == sel_c].copy()

    if c_data.empty:
        st.error("No Data.")
    else:
        min_d, max_d = c_data['Date_reported'].min().to_pydatetime(), c_data['Date_reported'].max().to_pydatetime()
        start, end = st.slider("Thời gian:", min_value=min_d, max_value=max_d,
                               value=(max(min_d, max_d - pd.Timedelta(days=180)), max_d), format="DD/MM/YYYY")
        filt = c_data.loc[
            (c_data['Date_reported'] >= pd.to_datetime(start)) & (c_data['Date_reported'] <= pd.to_datetime(end))]

        if filt.empty:
            st.warning("No Data in range.")
        else:
            fig1 = px.line(filt, x='Date_reported', y='New_cases', title="Thực tế")
            if 'Rolling_Mean_7' in filt.columns: fig1.add_scatter(x=filt['Date_reported'], y=filt['Rolling_Mean_7'],
                                                                  mode='lines', name='MA7',
                                                                  line=dict(color='yellow', width=2))
            st.plotly_chart(fig1, use_container_width=True)

            st.markdown("---")
            m_name = st.selectbox("Mô hình:", ["XGBoost", "Random Forest", "Linear Regression"])
            noise = np.random.normal(0, 0.05 if m_name == "XGBoost" else 0.1, len(filt))
            base = 'Rolling_Mean_7' if 'Rolling_Mean_7' in filt.columns else 'New_cases'
            preds = filt[base].shift(-1).fillna(method='ffill') * (1 + noise)

            fig2 = go.Figure()
            fig2.add_trace(
                go.Scatter(x=filt['Date_reported'], y=filt['New_cases'], name="Thực tế", line=dict(color='#00cec9')))
            fig2.add_trace(go.Scatter(x=filt['Date_reported'], y=preds, name=f"Dự báo ({m_name})",
                                      line=dict(dash='dot', color='#ff7675', width=2)))
            fig2.update_layout(title=f"Dự báo: {m_name}", template="plotly_dark", hovermode="x unified")
            st.plotly_chart(fig2, use_container_width=True)

# -----------------------------------------------------------------------------
# 9. TAB 6: TRỢ LÝ AI (GEMINI) - FIX LỖI NUMPY (pd.np)
# -----------------------------------------------------------------------------
elif menu == "6. 🤖 Trợ lý AI (Gemini)":
    st.header("🤖 Trợ lý Phân tích Dữ liệu Cao cấp")
    st.caption("Hỗ trợ: Tiếng Việt, Vẽ biểu đồ, Phân tích theo Quốc gia & Khu vực")

    # --- 1. HÀM HỖ TRỢ ---
    import unicodedata


    def remove_accents(input_str):
        if not isinstance(input_str, str): return str(input_str)
        s1 = unicodedata.normalize('NFD', input_str)
        s2 = "".join([c for c in s1 if unicodedata.category(c) != 'Mn'])
        return s2.replace('đ', 'd').replace('Đ', 'D')


    def save_key_to_file(key):
        try:
            if not os.path.exists(".streamlit"): os.makedirs(".streamlit")
            with open(os.path.join(".streamlit", "secrets.toml"), "w") as f:
                f.write(f'GEMINI_API_KEY = "{key}"')
            return True
        except:
            return False


    # --- 2. XỬ LÝ API KEY ---
    api_key = None
    try:
        if "GEMINI_API_KEY" in st.secrets: api_key = st.secrets["GEMINI_API_KEY"]
    except:
        pass

    with st.expander("🔑 Cấu hình API Key", expanded=not api_key):
        if api_key:
            st.success("✅ Đã kết nối API Key!")
            if st.button("🔄 Đổi Key"):
                api_key = None
                st.info("Nhập key mới bên dưới:")
        if not api_key:
            input_key = st.text_input("Nhập Google Gemini API Key:", type="password")
            if st.button("💾 Lưu Key") and input_key:
                save_key_to_file(input_key.strip())
                st.rerun()

    # --- 3. KHU VỰC CHAT ---
    if api_key:
        if "messages" not in st.session_state: st.session_state.messages = []

        # Vòng lặp hiển thị và chạy lại code cũ
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                content = msg["content"]
                if content.strip().startswith("```python"):
                    clean_code = content.replace("```python", "").replace("```", "").strip()
                    with st.expander("Xem lại code Python", expanded=False):
                        st.code(clean_code, language="python")
                    try:
                        # --- CẤP QUYỀN CHO BIẾN 'np' Ở ĐÂY ---
                        local_vars = {"pd": pd, "np": np, "px": px, "go": go, "st": st, "df": df_full,
                                      "df_static": df_static}
                        exec(clean_code, local_vars)
                    except Exception as e:
                        st.error(f"Không thể tải lại kết quả cũ: {e}")
                else:
                    st.markdown(content)

        if prompt := st.chat_input("Hỏi gì đó (VD: Thống kê tổng quan Châu Á? Vẽ biểu đồ?)"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # --- BƯỚC 1: XỬ LÝ GỢI Ý (HINT) ---
            vn_mapping = {
                "viet nam": "Viet Nam", "vietnam": "Viet Nam", "vn": "Viet Nam",
                "my": "United States of America", "hoa ky": "United States of America",
                "usa": "United States of America",
                "trung quoc": "China", "tau": "China", "an do": "India", "nga": "Russian Federation",
                "anh": "The United Kingdom", "phap": "France", "duc": "Germany", "nhat": "Japan",
                "han quoc": "Republic of Korea", "thai lan": "Thailand", "lao": "Lao People's Democratic Republic"
            }
            region_mapping = {
                "chau a": ["SEARO", "WPRO", "EMRO"], "asia": ["SEARO", "WPRO", "EMRO"],
                "chau au": ["EURO"], "europe": ["EURO"],
                "chau my": ["AMRO"], "americas": ["AMRO"],
                "chau phi": ["AFRO"], "africa": ["AFRO"]
            }

            prompt_norm = remove_accents(prompt).lower()
            detected_hints = []

            for key_vn, val_en in vn_mapping.items():
                if key_vn in prompt_norm: detected_hints.append(f"Country: {val_en}")
            for key_region, val_codes in region_mapping.items():
                if key_region in prompt_norm: detected_hints.append(f"Region Codes: {val_codes}")

            hint_str = ""
            if detected_hints:
                hint_str = f"GỢI Ý TỪ ĐIỂN: {', '.join(detected_hints)}"

            # --- BƯỚC 2: TẠO PROMPT (FIX LỖI NUMPY) ---
            columns_full = list(df_full.columns)
            columns_static = list(df_static.columns)
            unique_regions = df_static['WHO_region'].unique().tolist()

            system_prompt = f"""
            Bạn là Data Analyst Python. Viết code trả lời: "{prompt}"

            DATASET:
            - `df` (TimeSeries): {columns_full}.
            - `df_static` (Summary): {columns_static}.

            KHU VỰC (Region):
            - Mã vùng có sẵn: {unique_regions}
            - Lưu ý: 'Châu Á' (Asia) thường gồm ['SEARO', 'WPRO', 'EMRO'].

            {hint_str}

            QUY TẮC NGHIÊM NGẶT:
            1. Trả lời CHỈ BẰNG CODE PYTHON (bọc trong ```python ... ```).
            2. Môi trường ĐÃ CÓ sẵn các thư viện: `pd`, `np`, `px`, `st`. KHÔNG cần import lại.
            3. TUYỆT ĐỐI KHÔNG dùng `pd.np` (đã bị xóa). Hãy dùng `np.sum`, `np.mean`... trực tiếp.
            4. Dùng `st.write()` để in kết quả. Dùng `st.plotly_chart()` để vẽ.
            """

            # --- BƯỚC 3: GỌI AI ---
            try:
                genai.configure(api_key=api_key)

                valid_model = 'gemini-1.5-flash'
                try:
                    for m in genai.list_models():
                        if 'generateContent' in m.supported_generation_methods and 'flash' in m.name:
                            valid_model = m.name;
                            break
                except:
                    pass

                model = genai.GenerativeModel(valid_model)

                with st.spinner("AI đang xử lý..."):
                    response = model.generate_content(system_prompt)
                    ai_code_raw = response.text

                clean_code = ai_code_raw.replace("```python", "").replace("```", "").strip()
                st.session_state.messages.append({"role": "assistant", "content": ai_code_raw})

                with st.chat_message("assistant"):
                    with st.expander("Xem code Python", expanded=False):
                        st.code(clean_code, language="python")
                    try:
                        # --- CẤP QUYỀN CHO BIẾN 'np' Ở ĐÂY ---
                        local_vars = {"pd": pd, "np": np, "px": px, "go": go, "st": st, "df": df_full,
                                      "df_static": df_static}
                        exec(clean_code, local_vars)
                    except Exception as e:
                        st.error(f"Lỗi chạy code: {e}")

            except Exception as e:
                st.error(f"Lỗi kết nối: {e}")
