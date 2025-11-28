import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import scipy.stats as stats
import community.community_louvain as community_louvain # Thư viện python-louvain
from networkx.algorithms.community import greedy_modularity_communities
import seaborn as sns
import numpy as np

# ==============================================================================
# PHẦN 2: PHÂN TÍCH TỔNG QUAN MẠNG
# ==============================================================================
print(">>> ĐANG TẢI DỮ LIỆU...")
df = pd.read_csv("youtube_network_data.csv")

# 1. Tiền xử lý và tạo đồ thị
# Mạng đồng hiện là mạng Vô hướng (Undirected) và Có trọng số (Weighted)
G = nx.from_pandas_edgelist(df, 'Source', 'Target', edge_attr='Weight')

# Loại bỏ các vòng lặp (self-loops) nếu có (A nối với A)
G.remove_edges_from(nx.selfloop_edges(G))

print(f"--- THÔNG TIN CƠ BẢN ---")
print(f"Kiểu đồ thị: Vô hướng, Có trọng số, Đồng nhất (Homogeneous - Nút đều là Tag)")
print(f"Số nút: {G.number_of_nodes()}")
print(f"Số cạnh: {G.number_of_edges()}")

# Mật độ mạng (Density)
density = nx.density(G)
print(f"- Mật độ mạng: {density:.6f}")

# Lấy thành phần liên thông lớn nhất (Giant Component) để tính đường kính
# (Vì nếu mạng bị đứt đoạn, đường kính = vô cùng, code sẽ lỗi)
largest_cc_nodes = max(nx.connected_components(G), key=len)
G_sub = G.subgraph(largest_cc_nodes).copy()
print(f"Số nút trong thành phần liên thông lớn nhất: {G_sub.number_of_nodes()}")

# Đường kính & Bán kính (Chạy trên G_sub)
# Lưu ý: Mạng > 2000 nút tính cái này hơi lâu, kiên nhẫn nhé
if G_sub.number_of_nodes() > 1:
    print("Đang tính đường kính (có thể mất vài giây)...")
    diameter = nx.diameter(G_sub)
    radius = nx.radius(G_sub)
    avg_path_len = nx.average_shortest_path_length(G_sub)
    print(f"Đường kính (Diameter): {diameter}")
    print(f"Bán kính (Radius): {radius}")
    print(f"Độ dài đường đi trung bình: {avg_path_len:.4f}")
else:
    print("Mạng quá rời rạc.")

# Hệ số phân cụm
avg_clustering = nx.average_clustering(G)
print(f"Hệ số phân cụm toàn cục (Average Clustering): {avg_clustering:.4f}")

# --- VẼ BIỂU ĐỒ PHẦN 2 ---

# 1. Histogram Hệ số phân cụm cục bộ
clustering_coeffs = list(nx.clustering(G).values())
plt.figure(figsize=(10, 5))
plt.hist(clustering_coeffs, bins=30, color='skyblue', edgecolor='black')
plt.title("Phân phối Hệ số phân cụm (Clustering Coefficient Distribution)")
plt.xlabel("Hệ số phân cụm")
plt.ylabel("Số lượng nút")
plt.savefig("dist_clustering.png")
plt.close()

# 2. Phân phối bậc và Hồi quy (Power Law check)
degrees = [d for n, d in G.degree()]
degree_counts = pd.Series(degrees).value_counts().sort_index()
x_deg = degree_counts.index.values
y_count = degree_counts.values

# Chuyển sang Log-Log để hồi quy tuyến tính
x_log = np.log10(x_deg)
y_log = np.log10(y_count)

# Hồi quy tuyến tính
slope, intercept, r_value, p_value, std_err = stats.linregress(x_log, y_log)

plt.figure(figsize=(10, 6))
plt.scatter(x_log, y_log, label='Dữ liệu thực tế', alpha=0.6)
plt.plot(x_log, slope*x_log + intercept, color='red', label=f'Hồi quy (Slope={slope:.2f}, R2={r_value**2:.2f})')
plt.title("Phân phối bậc (Log-Log Scale) - Kiểm định Power Law")
plt.xlabel("Log10(Degree)")
plt.ylabel("Log10(Count)")
plt.legend()
plt.grid(True)
plt.savefig("dist_degree_regression.png")
plt.close()
print(f"Đánh giá phân phối bậc: Hệ số góc (Slope) = {slope:.2f}. (Nếu gần -2 đến -3 là mạng phi quy mô).")


# ==============================================================================
# PHẦN 3: PHÂN TÍCH CẤU TRÚC (CENTRALITY)
# ==============================================================================
print("\n--- PHÂN TÍCH CENTRALITY ---")

# Tính toán các chỉ số
deg_cent = nx.degree_centrality(G)
bet_cent = nx.betweenness_centrality(G) # Nặng!
eig_cent = nx.eigenvector_centrality(G, max_iter=1000)
pagerank = nx.pagerank(G) # PageRank dùng tốt cho cả mạng vô hướng

df_cent = pd.DataFrame({
    'Degree': deg_cent,
    'Betweenness': bet_cent,
    'Eigenvector': eig_cent,
    'PageRank': pagerank
})

# Top 5 của mỗi loại để mô tả
print("Top nodes by Degree (Phổ biến):", df_cent['Degree'].nlargest(5).index.tolist())
print("Top nodes by Betweenness (Cầu nối):", df_cent['Betweenness'].nlargest(5).index.tolist())
print("Top nodes by PageRank (Uy tín):", df_cent['PageRank'].nlargest(5).index.tolist())

# Tương quan giữa các độ đo
corr_matrix = df_cent.corr()
print("\nMa trận tương quan (Correlation Matrix):")
print(corr_matrix)

# Vẽ Heatmap tương quan
plt.figure(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')
plt.title("Tương quan giữa các chỉ số trung tâm")
plt.savefig("centrality_correlation.png")
plt.close()

# Phân tích tính tương đương cấu trúc - Đơn giản hóa
# Tìm 2 nút có bộ hàng xóm giống nhau nhất (Jaccard Similarity)
top_nodes = df_cent['Degree'].nlargest(20).index.tolist()
print("\nKiểm tra tính tương đồng cấu trúc (Top 20 nodes):")
sim_results = []
for i in range(len(top_nodes)):
    for j in range(i + 1, len(top_nodes)):
        u, v = top_nodes[i], top_nodes[j]
        preds = nx.jaccard_coefficient(G, [(u, v)])
        for u, v, p in preds:
            if p > 0.5: # Ngưỡng tương đồng
                sim_results.append((u, v, p))

sim_results.sort(key=lambda x: x[2], reverse=True)
if sim_results:
    print(f"Cặp nút có cấu trúc tương đồng nhất: {sim_results[0][0]} và {sim_results[0][1]} (Score: {sim_results[0][2]:.2f})")
else:
    print("Không tìm thấy cặp nút có độ tương đồng cao trong top nodes.")


# ==============================================================================
# PHẦN 4: PHÂN TÍCH CỘNG ĐỒNG
# ==============================================================================
print("\n--- PHÂN TÍCH CỘNG ĐỒNG ---")

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

# 1. K-Core Decomposition (Tìm lõi mạng)
# Loại bỏ dần các nút bậc thấp để tìm lõi cứng nhất
k_core_graph = nx.k_core(G)
print(f"K-Core lớn nhất (Max Core): {max(nx.core_number(G).values())}")
print(f"Số nút trong lõi K-Core cứng nhất: {k_core_graph.number_of_nodes()}")

# 2. So sánh thuật toán phát hiện cộng đồng
# Thuật toán A: Louvain (Dựa trên Modularity)
part_louvain = community_louvain.best_partition(G, weight='Weight')
mod_louvain = community_louvain.modularity(part_louvain, G)
num_com_louvain = len(set(part_louvain.values()))


communities = {}
for node, com_id in part_louvain.items():
    communities.setdefault(com_id, []).append(node)

sorted_coms = sorted(communities.items(), key=lambda x: len(x[1]), reverse=True)
print("\nCác chủ đề (Cộng đồng) chính tìm được:")
for i in range(min(3, len(sorted_coms))):
    com_id, nodes = sorted_coms[i]
    print(f"  + Cộng đồng {i+1} ({len(nodes)} nút): {', '.join(nodes[:5])}...")

# Thuật toán B: Greedy Modularity (Của NetworkX)
part_greedy = list(greedy_modularity_communities(G, weight='Weight'))
mod_greedy = nx.community.modularity(G, part_greedy)
num_com_greedy = len(part_greedy)

print(f"\nSo sánh thuật toán:")
print(f"1. Louvain: Modularity = {mod_louvain:.4f} | Số cộng đồng = {num_com_louvain}")
print(f"2. Greedy Modularity: Modularity = {mod_greedy:.4f} | Số cộng đồng = {num_com_greedy}")

if mod_louvain > mod_greedy:
    print("=> Kết luận: Thuật toán Louvain phân chia tốt hơn (Modularity cao hơn).")
else:
    print("=> Kết luận: Thuật toán Greedy phân chia tốt hơn.")

# Xuất file cho Gephi 
# Thêm thuộc tính cộng đồng vào node để Gephi tô màu
nx.set_node_attributes(G, part_louvain, 'Louvain_Community')
nx.set_node_attributes(G, dict(G.degree()), 'Degree_Attr')

nx.write_gexf(G, "youtube_network_final.gexf")
print("\n>>> Đã xuất file 'youtube_network_final.gexf'.")