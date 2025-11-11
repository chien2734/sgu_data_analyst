# vn30_dashboard.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from vnstock import Vnstock, Listing, Finance, Trading, Screener, Quote
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import requests 
import bs4
import yfinance as yf
#==============================================================================
# CẤU HÌNH BAN ĐẦU
#==============================================================================
st.set_page_config(layout="wide")

@st.cache_data(ttl=3600) 
def get_vn30_tickers_vnstock():
    """
    Dùng hàm Listing(source='VCI') để lấy danh sách VN30.
    """
    try:
        # SỬA LỖI: Dùng nguồn 'VCI' như bạn đã xác nhận
        listing = Listing(source='VCI') 
        vn30_series = listing.symbols_by_group('VN30')
        tickers = vn30_series.tolist()
        if not tickers:
             raise Exception("vnstock trả về danh sách VN30 rỗng")
        return ['-'] + sorted(tickers)
    except Exception as e:
        st.error(f"Không thể tải danh sách VN30 tự động từ vnstock: {e}. Sử dụng danh sách dự phòng.")
        return [
            '-', 'ACB', 'BCM', 'BID', 'BVH', 'CTG', 'FPT', 'GAS', 'GVR', 'HDB', 'HPG', 
            'MBB', 'MSN', 'MWG', 'PLX', 'POW', 'SAB', 'SSI', 'STB', 'TCB', 'TPB', 
            'VCB', 'VHM', 'VIB', 'VIC', 'VJC', 'VNM', 'VPB', 'VRE', 'SHB'
        ]

VN30_TICKERS = get_vn30_tickers_vnstock()

#==============================================================================
# Tab 1: Tổng quan (Summary) - ĐÃ HOÀN THIỆN
#==============================================================================
def tab1():
    st.title(f"Tổng quan - {ticker}")

    # --- LẤY DỮ LIỆU THÔNG TIN CÔNG TY ---
    @st.cache_data(ttl=3600) 
    def get_summary_data(ticker_symbol):
        try:
            stock = Vnstock().stock(symbol=ticker_symbol, source='VCI')
            overview = stock.company.overview()
            overview_df = overview.T
            if overview_df.empty:
                return pd.DataFrame()
            overview_df.columns = ['Giá trị']
            return overview_df
        except Exception:
            return pd.DataFrame()

    if ticker != '-':
        summary_df = get_summary_data(ticker)
        
        if not summary_df.empty:
            st.subheader("Thông tin cơ bản doanh nghiệp")
            st.dataframe(summary_df, use_container_width=True)
        else:
            st.warning(f"Không tìm thấy dữ liệu tổng quan cho mã {ticker}.")

    # --- LẤY DỮ LIỆU BIỂU ĐỒ GIÁ ---
    @st.cache_data(ttl=600) 
    def get_stock_data(ticker_symbol):
        end_date = datetime.today().strftime('%Y-%m-%d')
        start_date = (datetime.today() - timedelta(days=5*365)).strftime('%Y-%m-%d')
        try:
            stock = Vnstock().stock(symbol=ticker_symbol, source='VCI') # Dùng VCI cho đồng bộ
            stockdata = stock.quote.history(start=start_date, end=end_date, interval='1D')
            stockdata = stockdata.reset_index().rename(columns={"time": "date"})

            # vnstock trả về đơn vị ngàn đồng, ta nhân 1000 để ra VND
            price_cols = ['open', 'high', 'low', 'close']
            for col in price_cols:
                if col in stockdata.columns:
                    stockdata[col] = stockdata[col] * 1000
            return stockdata
        except Exception as e:
            st.error(f"Lỗi khi tải dữ liệu giá: {e}")
            return pd.DataFrame()
        
    if ticker != '-':
            st.subheader("Biểu đồ giá (5 Năm)")
            chartdata = get_stock_data(ticker) 
                       
            if not chartdata.empty:
                fig = px.area(chartdata, x='date', y='close', title=f"Biểu đồ giá Đóng cửa của {ticker}")
                
                fig.update_xaxes(title_text='Thời điểm')
                fig.update_yaxes(title_text='Giá (VND)')
                
                fig.update_xaxes(
                    rangeselector=dict(
                        buttons=list([
                            dict(count=1, label="1Th", step="month", stepmode="backward"),
                            dict(count=3, label="3Th", step="month", stepmode="backward"),
                            dict(count=6, label="6Th", step="month", stepmode="backward"),
                            dict(count=1, label="YTD", step="year", stepmode="todate"),
                            dict(count=1, label="1N", step="year", stepmode="backward"),
                            dict(count=3, label="3N", step="year", stepmode="backward"),
                            dict(label="Tất cả", step="all")
                        ])
                    )
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(f"Không thể tải được dữ liệu biểu đồ giá cho mã {ticker}.")

#==============================================================================
# Tab 2: Biểu đồ Kỹ thuật (Chart) - ĐÃ HOÀN THIỆN
#==============================================================================
def tab2():
    st.title(f"Biểu đồ kỹ thuật - {ticker}")
    
    # --- TÙY CHỌN ĐẦU VÀO ---
    c1, c2, c3, c4 = st.columns((1,1,1,1))
    
    with c1:
        start_date = st.date_input("Ngày bắt đầu", datetime.today().date() - timedelta(days=365))
    with c2:
        end_date = st.date_input("Ngày kết thúc", datetime.today().date())        
    with c3: 
        # vnstock hỗ trợ '1D', '1W', '1M'
        inter = st.selectbox("Chọn Tần suất", ['1D', '1W', '1M'], key="tab2_interval") 
    with c4:
        plot_type = st.selectbox("Chọn loại biểu đồ", ['Đường (Line)', 'Nến (Candle)'], key="tab2_plot")

    # --- HÀM LẤY DỮ LIỆU ---
    @st.cache_data            
    def get_chart_data(ticker_symbol, start_date, end_date, interval):
        try:
            # Chuyển đổi định dạng ngày tháng
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
            
            # Khởi tạo đối tượng stock
            stock = Vnstock().stock(symbol=ticker_symbol, source='VCI')
            # Lấy dữ liệu
            chartdata = stock.quote.history(start=start_str, end=end_str, interval=interval)
            
            if chartdata.empty:
                return pd.DataFrame()
            
            # Nhân 1000 vào tất cả các cột giá
            price_cols = ['open', 'high', 'low', 'close']
            for col in price_cols:
                if col in chartdata.columns:
                    chartdata[col] = chartdata[col] * 1000
            
            # Tính SMA 50
            chartdata['SMA_50'] = chartdata['close'].rolling(50).mean()
            
            # Reset index để có cột 'time' (hoặc 'date')
            chartdata = chartdata.reset_index().rename(columns={"time": "date"})
            
            return chartdata
        except Exception as e:
            st.error(f"Lỗi tải dữ liệu biểu đồ: {e}")
            return pd.DataFrame()
    
    if ticker != '-':
        chartdata = get_chart_data(ticker, start_date, end_date, inter) 
        
        if not chartdata.empty:
            # --- VẼ BIỂU ĐỒ ---
            # Sử dụng subplots để có 2 trục y (Giá và Khối lượng)
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Thêm Biểu đồ Nến hoặc Đường
            if plot_type == 'Đường (Line)':
                fig.add_trace(go.Scatter(x=chartdata['date'], y=chartdata['close'], mode='lines', 
                                         name = 'Giá đóng cửa'), secondary_y = False)
            else:
                fig.add_trace(go.Candlestick(x = chartdata['date'], open = chartdata['open'], 
                                             high = chartdata['high'], low = chartdata['low'], 
                                             close = chartdata['close'], name = 'Giá (Nến)'), 
                                             secondary_y = False)
          
            # Thêm đường SMA 50
            fig.add_trace(go.Scatter(x=chartdata['date'], y=chartdata['SMA_50'], mode='lines', 
                                     name = 'SMA 50', line=dict(color='orange', dash='dash')), 
                                     secondary_y = False)
            
            # Thêm Biểu đồ Khối lượng (Volume) vào trục y thứ 2
            fig.add_trace(go.Bar(x = chartdata['date'], y = chartdata['volume'], name = 'Khối lượng'), secondary_y = True)

            fig.update_layout(
                title=f"Biểu đồ Kỹ thuật {ticker} ({inter})",
                yaxis_title="Giá (VND)",
                xaxis_title="Ngày",
                legend_title="Chú thích",
                xaxis_rangeslider_visible=False # Ẩn thanh trượt mặc định khi dùng nến
            )
            # Ẩn nhãn của trục y thứ 2 (khối lượng) và điều chỉnh
            fig.update_yaxes(range=[0, chartdata['volume'].max()*3], showticklabels=False, secondary_y=True)
        
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Không có dữ liệu cho khoảng thời gian/tần suất đã chọn.")

#==============================================================================
# Tab 3: Thống kê (Statistics) - ĐÃ HOÀN THIỆN
#==============================================================================
def tab3():
    st.title(f"Thống kê chỉ số tài chính - {ticker}")
    
    # Thêm lựa chọn Hàng năm/Hàng quý
    period = st.radio("Chọn kỳ báo cáo", ('Hàng năm', 'Hàng quý'), horizontal=True, key="tab3_period")
    
    # Ánh xạ sang giá trị của vnstock
    period_key = 'year' if period == 'Hàng năm' else 'quarter'

    @st.cache_data(ttl=3600) # Cache 1 giờ
    def get_financial_ratios(ticker_symbol, period_key):
        """
        Tải các chỉ số tài chính (P/E, ROA, ROE, v.v.)
        Sử dụng cú pháp vnstock v3.x (theo tài liệu 8.8)
        """
        try:
            # Khởi tạo đối tượng stock
            stock = Vnstock().stock(symbol=ticker_symbol, source='VCI')
            
            # Lấy dữ liệu chỉ số, 'vi' = Tiếng Việt
            # Dữ liệu trả về có các chỉ số là Index
            ratios = stock.finance.ratio(period=period_key, lang='vi')
            
            if isinstance(ratios, pd.DataFrame):
                ratios.index.name = 'Chỉ tiêu'
            
            return ratios
        except Exception as e:
            st.error(f"Lỗi khi tải chỉ số tài chính: {e}")
            return pd.DataFrame()

    if ticker != '-':
        ratios_df = get_financial_ratios(ticker, period_key)
    
    if ratios_df is not None and not ratios_df.empty:
        st.subheader(f"Các chỉ số tài chính {period} của {ticker}")
        
        # sẽ tự động hiển thị cùng với các cột dữ liệu.
        st.dataframe(ratios_df, use_container_width=True)
        
    else:
        st.warning(f"Không có dữ liệu chỉ số tài chính cho mã {ticker}. (Nguồn VCI có thể không hỗ trợ mã này).")

#==============================================================================
# Tab 4: Báo cáo Tài chính (Financials) - ĐÃ HOÀN THIỆN
#==============================================================================
def tab4():
    st.title(f"Báo cáo tài chính - {ticker}")
    
    # Tạo 2 cột cho 2 bộ lọc
    c1, c2 = st.columns(2)
    with c1:
        statement = st.selectbox("Chọn báo cáo", 
                                ['Báo cáo kết quả kinh doanh', 
                                'Bảng cân đối kế toán', 
                                'Báo cáo lưu chuyển tiền tệ'])
    with c2:
        # Thêm key="tab4_period" để tránh xung đột với radio button của Tab 3
        period = st.selectbox("Chọn kỳ báo cáo", ['Hàng năm', 'Hàng quý'], key="tab4_period")
    
    # Ánh xạ lựa chọn
    statement_map = {
        'Báo cáo kết quả kinh doanh': 'incomestatement',
        'Bảng cân đối kế toán': 'balancesheet',
        'Báo cáo lưu chuyển tiền tệ': 'cashflow'
    }
    period_key = 'year' if period == 'Hàng năm' else 'quarter'

    @st.cache_data(ttl=3600) # Cache 1 giờ
    def get_financial_statement(ticker_symbol, report_type, period):
        """
        Tải báo cáo tài chính theo cú pháp vnstock v3.x
        """
        try:
            stock = Vnstock().stock(symbol=ticker_symbol, source='VCI')
            
            if report_type == 'incomestatement':
                data = stock.finance.income_statement(period=period, lang='vi')
            elif report_type == 'balancesheet':
                data = stock.finance.balance_sheet(period=period, lang='vi')
            elif report_type == 'cashflow':
                data = stock.finance.cash_flow(period=period, lang='vi')
            else:
                data = pd.DataFrame()
            
            # Đặt tên cho Index (Chỉ tiêu)
            if isinstance(data, pd.DataFrame) and not data.empty:
                data.index.name = 'Chỉ tiêu'
                
            return data
        except Exception as e:
            st.error(f"Lỗi khi tải báo cáo tài chính: {e}")
            return pd.DataFrame()
        
    if ticker != '-':
        report_type_key = statement_map[statement]
        
        data_df = get_financial_statement(ticker, report_type_key, period_key)
        
        if not data_df.empty:
            st.subheader(f"{statement} - {period}")
            
            st.dataframe(data_df, use_container_width=True)
        else:
            st.warning("Không có dữ liệu báo cáo tài chính cho lựa chọn này.")
                
#==============================================================================
# Tab 5: Phân tích (Analysis) - ĐÃ HOÀN THIỆN
#==============================================================================
def tab5():
    st.title(f"Phân tích mã {ticker}")
    st.write(f"Các phân tích của yfinance cho mã {ticker}.")
    st.warning("Lưu ý: yfinance có thể không có dữ liệu phân tích cho các mã Việt Nam.")

    @st.cache_data(ttl=600) # Cache 10 phút
    def get_analysis_data_yfinance(ticker_symbol):
        """
        Sử dụng các thuộc tính (attributes) của yfinance Ticker
        mà bạn đã cung cấp (ví dụ: .earnings_estimate)
        """
        data_package = {}
        try:
            # SỬA LỖI: Phải dùng đuôi .VN
            if not ticker_symbol.endswith(".VN"):
                ticker_symbol_vn = f"{ticker_symbol}.VN"
            else:
                ticker_symbol_vn = ticker_symbol
                
            # Tạo đối tượng Ticker
            stock = yf.Ticker(ticker_symbol_vn)
            
            # Lấy tất cả dữ liệu analysis mà bạn đã liệt kê
            data_package["recommendations"] = stock.recommendations
            data_package["earnings_estimate"] = stock.earnings_estimate
            data_package["revenue_estimate"] = stock.revenue_estimate
            data_package["earnings_history"] = stock.earnings_history
            data_package["eps_trend"] = stock.eps_trend
            data_package["eps_revisions"] = stock.eps_revisions
            data_package["growth_estimates"] = stock.growth_estimates
            
            return data_package
        
        except Exception as e:
            st.error(f"Lỗi khi tải dữ liệu yfinance: {e}")
            return None

    if ticker != '-':
        with st.spinner(f"Đang tải dữ liệu phân tích từ yfinance cho {ticker}..."):
            analysis_data = get_analysis_data_yfinance(ticker)
        
        if analysis_data:
            
            # 1. Khuyến nghị (Recommendations)
            st.subheader("Khuyến nghị của các chuyên gia phân tích")
            recs_df = analysis_data.get("recommendations")
            if recs_df is not None and not recs_df.empty:
                st.dataframe(recs_df.sort_index(ascending=False), use_container_width=True)
            else:
                st.warning(f"Không tìm thấy dữ liệu 'Recommendations' cho {ticker}.")

            # 2. Ước tính Thu nhập (Earnings Estimate)
            st.subheader("Ước tính thu nhập (Earnings Estimate)")
            earn_est_df = analysis_data.get("earnings_estimate")
            if earn_est_df is not None and not earn_est_df.empty:
                st.dataframe(earn_est_df, use_container_width=True)
            else:
                st.warning(f"Không tìm thấy dữ liệu 'Earnings Estimate' cho {ticker}.")

            # 3. Ước tính Doanh thu (Revenue Estimate)
            st.subheader("Ước tính doanh thu (Revenue Estimate)")
            rev_est_df = analysis_data.get("revenue_estimate")
            if rev_est_df is not None and not rev_est_df.empty:
                st.dataframe(rev_est_df, use_container_width=True)
            else:
                st.warning(f"Không tìm thấy dữ liệu 'Revenue Estimate' cho {ticker}.")

            # 4. Lịch sử Thu nhập (Earnings History)
            st.subheader("Lịch sử thu nhập (Earnings History)")
            earn_hist_df = analysis_data.get("earnings_history")
            if earn_hist_df is not None and not earn_hist_df.empty:
                st.dataframe(earn_hist_df, use_container_width=True)
            else:
                st.warning(f"Không tìm thấy dữ liệu 'Earnings History' cho {ticker}.")

            # 5. Xu hướng EPS (EPS Trend)
            st.subheader("Xu hướng EPS (EPS Trend)")
            eps_trend_df = analysis_data.get("eps_trend")
            if eps_trend_df is not None and not eps_trend_df.empty:
                st.dataframe(eps_trend_df, use_container_width=True)
            else:
                st.warning(f"Không tìm thấy dữ liệu 'EPS Trend' cho {ticker}.")
                
            # 6. Điều chỉnh EPS (EPS Revisions)
            st.subheader("Điều chỉnh EPS (EPS Revisions)")
            eps_rev_df = analysis_data.get("eps_revisions")
            if eps_rev_df is not None and not eps_rev_df.empty:
                st.dataframe(eps_rev_df, use_container_width=True)
            else:
                st.warning(f"Không tìm thấy dữ liệu 'EPS Revisions' cho {ticker}.")

            # 7. Ước tính Tăng trưởng (Growth Estimates)
            st.subheader("Ước tính tăng trưởng (Growth Estimates)")
            growth_est_df = analysis_data.get("growth_estimates")
            if growth_est_df is not None and not growth_est_df.empty:
                st.dataframe(growth_est_df, use_container_width=True)
            else:
                st.warning(f"Không tìm thấy dữ liệu 'Growth Estimates' cho {ticker}.")
                
        else:
            st.warning(f"Không thể tải bất kỳ dữ liệu phân tích nào cho {ticker}.")

#==============================================================================
# Tab 6: Mô phỏng Monte Carlo - ĐÃ HOÀN THIỆN
#==============================================================================
def tab6():
     st.title(f"Mô phỏng Monte Carlo - {ticker}")
     st.write("Mô phỏng này dự đoán các kịch bản giá cổ phiếu trong tương lai dựa trên biến động lịch sử (sử dụng 90 ngày gần nhất).")
     
     #Dropdown for selecting simulation and horizon
     c1, c2 = st.columns(2)
     with c1:
        simulations = st.selectbox("Số lần Mô phỏng (n)", [200, 500, 1000])
     with c2:
        time_horizon = st.selectbox("Số ngày Dự đoán (t)", [30, 60, 90])
     
     @st.cache_data(ttl=600) # Cache 10 phút
     def monte_carlo_simulation(ticker_symbol, time_horizon, simulations):
         
         end_date = datetime.now().date()
         start_date = (end_date - timedelta(days=90)).strftime('%Y-%m-%d')
         end_date_str = end_date.strftime('%Y-%m-%d')
         
         try:
             stock = Vnstock().stock(symbol=ticker_symbol, source='VCI')
             stock_price = stock.quote.history(start=start_date, end=end_date_str, interval='1D')

             if stock_price.empty:
                 st.error("Không đủ dữ liệu giá gần đây để chạy mô phỏng.")
                 return None, None
         except Exception as e:
             st.error(f"Lỗi tải dữ liệu giá cho Monte Carlo: {e}")
             return None, None

         close_price = stock_price['close']
     
         daily_return = close_price.pct_change()
         daily_volatility = np.std(daily_return) 
     
         simulation_df = pd.DataFrame()
         last_price = close_price.iloc[-1] # Đây là giá gốc (đơn vị ngàn đồng)
     
         for i in range(simulations):        
                next_price = []
                temp_last_price = last_price
    
                for x in range(time_horizon):
                      future_return = np.random.normal(0, daily_volatility)
                      future_price = temp_last_price * (1 + future_return)
                      next_price.append(future_price)
                      temp_last_price = future_price
    
                simulation_df[f'Sim {i+1}'] = next_price
                
         return simulation_df, last_price
          
     if ticker != '-':
        if st.button("Chạy Mô phỏng"):
            with st.spinner("Đang chạy mô phỏng... Vui lòng chờ..."):
                mc_df, last_price = monte_carlo_simulation(ticker, time_horizon, simulations)
            
            if mc_df is not None:
                fig, ax = plt.subplots(figsize=(15, 10))
                
                # SỬA LỖI ĐƠN VỊ: Nhân 1000 cho dữ liệu vẽ biểu đồ
                ax.plot(mc_df * 1000) 
                plt.title(f'Mô phỏng Monte Carlo cho {ticker} trong {time_horizon} ngày')
                plt.xlabel('Ngày')
                plt.ylabel('Giá (VND)')
                
                plt.axhline(y=last_price * 1000, color='red', linestyle='--')
                plt.legend([f'Giá Hiện tại: {last_price * 1000:,.0f} VND'])
                                
                st.pyplot(fig)
                
                # --- Phân tích Value at Risk (VaR) ---
                st.subheader('Phân tích Rủi ro (Value at Risk - VaR)')
                ending_prices = mc_df.iloc[-1, :] # Lấy giá gốc (đơn vị ngàn đồng)
                
                fig_hist, ax_hist = plt.subplots(figsize=(15, 10))
                
                ax_hist.hist(ending_prices * 1000, bins=50, density=True)
                
                # Tính toán VaR 95%
                future_price_95ci = np.percentile(ending_prices, 5) 
                VaR = last_price - future_price_95ci 
                
                plt.axvline(future_price_95ci * 1000, color='red', linestyle='--', linewidth=2)
                plt.legend([f'Giá trị phân vị 5% (5th Percentile): {future_price_95ci * 1000:,.0f} VND'])
                plt.title('Phân bổ giá vào ngày cuối cùng')
                plt.xlabel('Giá (VND)')
                plt.ylabel('Tần suất')
                st.pyplot(fig_hist)
                
                # Hiển thị VaR bằng st.metric
                st.subheader(f"Value at Risk (VaR) trong {time_horizon} ngày")
                
                st.metric(label=f"VaR (Độ tin cậy 95%)", 
                          value=f"{VaR * 1000:,.0f} VND",
                          help=f"Dựa trên 95% độ tin cậy, mức lỗ tối đa dự kiến cho cổ phiếu này trong {time_horizon} ngày tới là {VaR * 1000:,.0f} VND, nếu giá hiện tại là {last_price * 1000:,.0f} VND.")
                
#==============================================================================
# Tab 7: Xu hướng Portfolio - ĐÃ HOÀN THIỆN
#==============================================================================
def tab7():
    st.title("So sánh hiệu suất Portfolio (5 Năm)")
    st.write("Tab này so sánh sự tăng trưởng của các cổ phiếu VN30 trong 5 năm qua. Tất cả các cổ phiếu đều được chuẩn hóa về mốc '1.0' tại thời điểm bắt đầu để so sánh hiệu suất tăng trưởng một cách công bằng.")
    
    # Lấy danh sách VN30 (đã có ở global) và bỏ dấu '-'
    vn30_list = [t for t in VN30_TICKERS if t != '-']
    
    # Cho phép người dùng chọn nhiều mã
    selected_tickers = st.multiselect("Chọn các mã để so sánh", options=vn30_list) 
    
    @st.cache_data(ttl=3600) # Cache 1 giờ
    def get_portfolio_data(tickers):
        """
        Tải dữ liệu 5 năm cho nhiều mã và CHUẨN HÓA chúng.
        """
        # DataFrame để chứa kết quả đã chuẩn hóa
        normalized_df = pd.DataFrame()
        
        end_date = datetime.today().strftime('%Y-%m-%d')
        start_date = (datetime.today() - timedelta(days=5*365)).strftime('%Y-%m-%d')
        
        with st.spinner("Đang tải dữ liệu 5 năm..."):
            for ticker_symbol in tickers:
                try:
                    # 1. Tải dữ liệu
                    stock = Vnstock().stock(symbol=ticker_symbol, source='VCI')
                    data = stock.quote.history(start=start_date, end=end_date, interval='1D')['close']
                    
                    if not data.empty:
                        # 2. CHUẨN HÓA: Chia tất cả giá cho giá đầu tiên
                        normalized_data = data / data.iloc[0]
                        
                        # 3. Thêm vào DataFrame
                        normalized_df[ticker_symbol] = normalized_data
                    else:
                        st.warning(f"Không tìm thấy dữ liệu 5 năm cho {ticker_symbol}")
                
                except Exception as e:
                    st.error(f"Lỗi khi tải dữ liệu cho {ticker_symbol}: {e}")
        
        return normalized_df

    if not selected_tickers:
        st.warning("Vui lòng chọn ít nhất một mã cổ phiếu.")
    else:
        portfolio_df = get_portfolio_data(selected_tickers)
                  
        if not portfolio_df.empty:
            st.subheader("Biểu đồ tăng trưởng chuẩn hóa (5 Năm)")
            
            # 4. VẼ BIỂU ĐỒ (Dùng px.line như file mẫu)
            # Plotly tự động nhận index (là ngày tháng) làm trục X
            fig = px.line(portfolio_df, title="Hiệu suất Portfolio (Chuẩn hóa)")
            
            # Cập nhật tên trục
            fig.update_layout(yaxis_title="Tăng trưởng (1.0 = Mốc 5 năm trước)",
                              xaxis_title="Ngày",
                              legend_title="Cổ phiếu")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Không có dữ liệu để vẽ biểu đồ.")

#==============================================================================
# Hàm RUN chính của ứng dụng
#==============================================================================
def run():
    
    st.sidebar.title("Bảng điều khiển FinDash 🇻🇳")
    
    global ticker
    ticker = st.sidebar.selectbox("Chọn cổ phiếu VN-30", VN30_TICKERS)
    
    select_tab = st.sidebar.radio("Chọn chức năng", 
                                  ['Tổng quan', 'Biểu đồ kỹ thuật', 'Thống kê', 
                                   'Báo cáo tài chính', 'Phân tích', 
                                   'Mô phỏng Monte Carlo', "Xu hướng Portfolio"])
    
    if select_tab == 'Tổng quan':
        if ticker == '-':
            st.warning("Vui lòng chọn một mã cổ phiếu từ thanh bên trái.")
        else:
            tab1()
    elif select_tab == 'Biểu đồ kỹ thuật':
        if ticker == '-':
            st.warning("Vui lòng chọn một mã cổ phiếu từ thanh bên trái.")
        else:
            tab2()
    elif select_tab == 'Thống kê':
        if ticker == '-':
            st.warning("Vui lòng chọn một mã cổ phiếu từ thanh bên trái.")
        else:
            tab3()
    elif select_tab == 'Báo cáo tài chính':
        if ticker == '-':
            st.warning("Vui lòng chọn một mã cổ phiếu từ thanh bên trái.")
        else:
            tab4()
    elif select_tab == 'Phân tích':
        if ticker == '-':
            st.warning("Vui lòng chọn một mã cổ phiếu từ thanh bên trái.")
        else:
            tab5()
    elif select_tab == 'Mô phỏng Monte Carlo':
        if ticker == '-':
            st.warning("Vui lòng chọn một mã cổ phiếu từ thanh bên trái.")
        else:
            tab6()
    else:
        if ticker == '-':
            st.warning("Vui lòng chọn một mã cổ phiếu từ thanh bên trái.")
        if select_tab == "Xu hướng Portfolio":
            tab7()
       
if __name__ == "__main__":
    run()