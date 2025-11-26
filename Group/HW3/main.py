import googleapiclient.discovery
import pandas as pd
import itertools

# --- CẤU HÌNH ---
API_KEY = "AIzaSyCb7W_6lHeJNu9zuoxXzKYp4SZrufY3jxY"  # <--- Thay API Key của bạn vào đây
SEARCH_QUERY = "Trí tuệ nhân tạo"  # Chủ đề bạn muốn quét (đổi thành gì cũng được)
MAX_VIDEOS = 200 # Số lượng video muốn quét (Càng nhiều thì mạng càng lớn)

def get_youtube_tags(api_key, query, max_results):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    
    video_data = []
    video_ids = []
    
    print(f"Đang tìm kiếm video về: {query}...")
    
    # 1. Tìm kiếm video lấy ID
    request = youtube.search().list(
        q=query,
        part="id",
        type="video",
        maxResults=50 # Max mỗi lần request là 50
    )
    
    while request and len(video_ids) < max_results:
        response = request.execute()
        for item in response['items']:
            video_ids.append(item['id']['videoId'])
        
        # Lấy trang tiếp theo nếu chưa đủ số lượng
        request = youtube.search().list_next(request, response)

    print(f"Đã tìm thấy {len(video_ids)} video. Đang lấy chi tiết tags...")

    # 2. Lấy chi tiết từng video (bao gồm Tags)
    # API chỉ cho phép lấy 50 ID một lần, nên phải chia nhỏ
    all_tags_connections = []
    
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i:i+50]
        ids_str = ",".join(chunk)
        
        video_response = youtube.videos().list(
            part="snippet",
            id=ids_str
        ).execute()

        for item in video_response['items']:
            # Kiểm tra xem video có tags không
            if 'tags' in item['snippet']:
                tags = item['snippet']['tags']
                # Chuẩn hóa: chuyển về chữ thường để tránh trùng lặp (ví dụ: AI và ai)
                tags = [tag.lower().strip() for tag in tags]
                
                # Nếu video có từ 2 tags trở lên mới tạo thành cạnh được
                if len(tags) > 1:
                    # Tạo các cặp kết nối (Edges)
                    # Ví dụ: tags = [A, B, C] -> (A,B), (A,C), (B,C)
                    connections = list(itertools.combinations(tags, 2))
                    all_tags_connections.extend(connections)

    return all_tags_connections

# --- CHẠY CHƯƠNG TRÌNH ---
try:
    # Lấy dữ liệu cạnh (Source, Target)
    edges = get_youtube_tags(API_KEY, SEARCH_QUERY, MAX_VIDEOS)
    
    # Tạo DataFrame
    df = pd.DataFrame(edges, columns=['Source', 'Target'])
    
    # Tính toán trọng số (Weight): Số lần 2 tag cùng xuất hiện
    df_weighted = df.groupby(['Source', 'Target']).size().reset_index(name='Weight')
    
    # Lọc bỏ các cạnh quá yếu (xuất hiện ít hơn 2 lần) để đồ thị đỡ rối (Tùy chọn)
    # df_weighted = df_weighted[df_weighted['Weight'] > 1] 

    print("------------------------------------------------")
    print(f"Tổng số cặp cạnh thu được: {len(df_weighted)}")
    print("Mẫu dữ liệu:")
    print(df_weighted.head())
    
    # Lưu ra file CSV
    filename = "youtube_network_data.csv"
    df_weighted.to_csv(filename, index=False)
    print(f"\nĐã lưu dữ liệu thành công vào file: {filename}")
    print("Bạn hãy dùng file này cho Giai đoạn 2 (Phân tích) và Gephi.")

except Exception as e:
    print(f"Có lỗi xảy ra: {e}")
    print("Lưu ý: Kiểm tra lại API Key hoặc kết nối mạng.")