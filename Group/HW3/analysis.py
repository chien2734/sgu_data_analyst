import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import community.community_louvain as community_louvain # Thư viện python-louvain
import numpy as np

# 1. ĐỌC DỮ LIỆU
print(">>> Đang đọc dữ liệu...")
df = pd.read_csv("youtube_network_data.csv")
# Tạo đồ thị vô hướng (Undirected) từ DataFrame
G = nx.from_pandas_edgelist(df, 'Source', 'Target', edge_attr='Weight')

print("------------------------------------------------")
print("PHẦN 2: PHÂN TÍCH TỔNG QUAN MẠNG")
# Số lượng nút và cạnh
num_nodes = G.number_of_nodes()
num_edges = G.number_of_edges()
print(f"- Số nút (Nodes): {num_nodes}")
print(f"- Số cạnh (Edges): {num_edges}")

# Mật độ mạng (Density)
density = nx.density(G)
print(f"- Mật độ mạng: {density:.6f}")

# Hệ số phân cụm trung bình (Average Clustering Coefficient)
avg_clustering = nx.average_clustering(G)
print(f"- Hệ số phân cụm trung bình: {avg_clustering:.6f}")

# --- Xử lý thành phần liên thông (Connected Components) ---
# Vì đồ thị thực tế thường bị ngắt quãng, ta chỉ tính đường kính trên cụm lớn nhất
largest_cc = max(nx.connected_components(G), key=len)
S = G.subgraph(largest_cc).copy()
print(f"- Số nút trong thành phần liên thông lớn nhất: {S.number_of_nodes()}")

# Đường kính và Bán kính (Chạy trên cụm lớn nhất)
if S.number_of_nodes() > 1:
    diameter = nx.diameter(S)
    radius = nx.radius(S)
    avg_path = nx.average_shortest_path_length(S)
    print(f"- Đường kính (Diameter): {diameter}")
    print(f"- Bán kính (Radius): {radius}")
    print(f"- Độ dài đường đi trung bình: {avg_path:.4f}")
else:
    print("- Mạng quá rời rạc, không tính được đường kính/bán kính.")

print("\n------------------------------------------------")
print("PHẦN 3: PHÂN TÍCH CẤU TRÚC (CENTRALITY)")

# 1. Degree Centrality (Ai kết nối nhiều nhất?)
degree_dict = dict(G.degree(weight='Weight'))
sorted_degree = sorted(degree_dict.items(), key=lambda item: item[1], reverse=True)
print("\nTop 5 Hashtag phổ biến nhất (Degree):")
for node, val in sorted_degree[:5]:
    print(f"  + {node}: {val}")

# 2. Betweenness Centrality (Cầu nối thông tin)
# Lưu ý: Tính cái này khá lâu với mạng lớn, ta giới hạn k nếu cần
print("\nĐang tính Betweenness (có thể mất chút thời gian)...")
betweenness = nx.betweenness_centrality(G, weight='Weight')
sorted_bet = sorted(betweenness.items(), key=lambda item: item[1], reverse=True)
print("Top 5 Hashtag cầu nối (Betweenness):")
for node, val in sorted_bet[:5]:
    print(f"  + {node}: {val:.4f}")

# 3. PageRank (Độ uy tín)
pagerank = nx.pagerank(G, weight='Weight')
sorted_pr = sorted(pagerank.items(), key=lambda item: item[1], reverse=True)
print("\nTop 5 Hashtag uy tín (PageRank):")
for node, val in sorted_pr[:5]:
    print(f"  + {node}: {val:.4f}")

print("\n------------------------------------------------")
print("PHẦN 4: PHÂN TÍCH CỘNG ĐỒNG & VẼ BIỂU ĐỒ")

# 1. Phân phối bậc (Degree Distribution Histogram)
degrees = [d for n, d in G.degree()]
plt.figure(figsize=(10, 6))
plt.hist(degrees, bins=50, color='skyblue', edgecolor='black')
plt.title("Phân phối bậc của các nút (Degree Distribution)")
plt.xlabel("Bậc (Degree)")
plt.ylabel("Số lượng nút")
plt.yscale('log') # Dùng thang log để nhìn rõ hơn nếu chênh lệch lớn
plt.grid(axis='y', alpha=0.75)
plt.savefig("degree_distribution.png")
print("- Đã lưu biểu đồ phân phối bậc: degree_distribution.png")

# 2. Phát hiện cộng đồng (Louvain Algorithm)
partition = community_louvain.best_partition(G, weight='Weight')
# Tính chỉ số Modularity
modularity = community_louvain.modularity(partition, G)
print(f"- Chỉ số Modularity (Tính mô-đun): {modularity:.4f}")
print(f"- Số lượng cộng đồng tìm thấy: {len(set(partition.values()))}")

# In thử vài cộng đồng lớn
communities = {}
for node, com_id in partition.items():
    communities.setdefault(com_id, []).append(node)

sorted_coms = sorted(communities.items(), key=lambda x: len(x[1]), reverse=True)
print("\nCác chủ đề (Cộng đồng) chính tìm được:")
for i in range(min(3, len(sorted_coms))):
    com_id, nodes = sorted_coms[i]
    print(f"  + Cộng đồng {i+1} ({len(nodes)} nút): {', '.join(nodes[:5])}...")

print("\n HOÀN TẤT PHÂN TÍCH!")