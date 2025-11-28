import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import scipy.stats as stats
import community.community_louvain as community_louvain # Thư viện python-louvain
from networkx.algorithms.community import greedy_modularity_communities
import seaborn as sns
import numpy as np

# PHẦN 2: PHÂN TÍCH TỔNG QUAN MẠNG

print(">>> ĐANG TẢI DỮ LIỆU...")
df = pd.read_csv("youtube_network_data.csv")

# 1. Tiền xử lý và tạo đồ thị
# Mạng đồng hiện là mạng Vô hướng (Undirected) và Có trọng số (Weighted)
G = nx.from_pandas_edgelist(df, 'Source', 'Target', edge_attr='Weight')

# Loại bỏ các vòng lặp  nếu có 
G.remove_edges_from(nx.selfloop_edges(G))

print(f"--- THÔNG TIN CƠ BẢN ---")
print(f"Kiểu đồ thị: Vô hướng, Có trọng số, Đồng nhất (Homogeneous - Nút đều là Tag)")
print(f"Số nút: {G.number_of_nodes()}")
print(f"Số cạnh: {G.number_of_edges()}")

# Mật độ mạng (Density)
density = nx.density(G)
print(f"- Mật độ mạng: {density:.6f}")

# Lấy thành phần liên thông lớn nhất để tính đường kính
largest_cc_nodes = max(nx.connected_components(G), key=len)
G_sub = G.subgraph(largest_cc_nodes).copy()
print(f"Số nút trong thành phần liên thông lớn nhất: {G_sub.number_of_nodes()}")

# Đường kính & Bán kính & Độ dài đường đi trung bình
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

# Bậc trung bình
degrees = [d for n, d in G.degree()]
plt.figure(figsize=(10, 6))
plt.hist(degrees, bins=50, color='skyblue', edgecolor='black')
plt.title("Phân phối bậc của các nút (Degree Distribution)")
plt.xlabel("Bậc (Degree)")
plt.ylabel("Số lượng nút")
plt.yscale('log') 
plt.grid(axis='y', alpha=0.75)
plt.savefig("degree_distribution.png")
plt.close()

# Hệ số phân cụm
avg_clustering = nx.average_clustering(G)
print(f"Hệ số phân cụm toàn cục (Average Clustering): {avg_clustering:.4f}")

# --- VẼ BIỂU ĐỒ ---
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


# PHẦN 3: PHÂN TÍCH CẤU TRÚC (CENTRALITY)
print("\n--- PHÂN TÍCH CẤU TRÚC ---")
# 1. TÍNH TOÁN CÁC CHỈ SỐ
print("Đang tính Degree...")
deg_cent = nx.degree_centrality(G)

print("Đang tính Closeness...")
clo_cent = nx.closeness_centrality(G)

print("Đang tính Betweenness...")
bet_cent = nx.betweenness_centrality(G)

print("Đang tính Eigenvector...")
eig_cent = nx.eigenvector_centrality(G, max_iter=1000)

print("Đang tính PageRank...")
pagerank = nx.pagerank(G)

df_cent = pd.DataFrame({
    'Degree': deg_cent,
    'Closeness': clo_cent, 
    'Betweenness': bet_cent,
    'Eigenvector': eig_cent,
    'PageRank': pagerank
})

# 3. IN KẾT QUẢ TOP 5
print("-" * 30)
print("Top nodes by Degree (Phổ biến):", df_cent['Degree'].nlargest(5).index.tolist())
print("Top nodes by Closeness (Lan truyền nhanh):", df_cent['Closeness'].nlargest(5).index.tolist()) 
print("Top nodes by Betweenness (Cầu nối):", df_cent['Betweenness'].nlargest(5).index.tolist())
print("Top nodes by PageRank (Uy tín):", df_cent['PageRank'].nlargest(5).index.tolist())

# 4. TƯƠNG QUAN GIỮA CÁC ĐỘ ĐO
corr_matrix = df_cent.corr()
print("\nMa trận tương quan (Correlation Matrix):")
print(corr_matrix)

# Vẽ Heatmap tương quan
plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f")
plt.title("Tương quan giữa 5 chỉ số trung tâm")
plt.savefig("centrality_correlation.png")
plt.close()

# 5. TRỰC QUAN HÓA TOP 10 (BAR CHART) 
print("\n>>> ĐANG VẼ BIỂU ĐỒ SO SÁNH...")
sns.set_theme(style="whitegrid")

fig, axes = plt.subplots(3, 2, figsize=(15, 18))
fig.suptitle('Top 10 Hashtag quan trọng theo 5 chỉ số Centrality', fontsize=16)

metrics = ['Degree', 'Closeness', 'Betweenness', 'Eigenvector', 'PageRank']
colors = ['#3498db', '#f1c40f', '#e74c3c', '#2ecc71', '#9b59b6'] 

for i, metric in enumerate(metrics):
    row, col = i // 2, i % 2
    # Lấy dữ liệu top 10
    top_10 = df_cent[metric].nlargest(10).sort_values(ascending=True)
    # Vẽ
    axes[row, col].barh(top_10.index, top_10.values, color=colors[i], alpha=0.8)
    axes[row, col].set_title(f'Top 10 theo {metric}', fontsize=12, fontweight='bold')
    axes[row, col].set_xlabel('Giá trị')

# Ẩn biểu đồ thứ 6 
if len(metrics) % 2 != 0:
    fig.delaxes(axes[2, 1])

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig("centrality_top10_all_5_metrics.png")
plt.close()

# Phân tích tính tương đương cấu trúc , Tìm 2 nút có bộ hàng xóm giống nhau nhất (Jaccard Similarity)
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

# PHẦN 4: PHÂN TÍCH CỘNG ĐỒNG
print("\n--- PHÂN TÍCH CỘNG ĐỒNG ---")
# TÌM KIẾM NHÓM VÀ MÔ HÌNH HÓA DÙNG K-CORE
print("\n>>> 1. PHÂN TÍCH K-CORE (LÕI MẠNG)")
# Tính chỉ số Core cho từng nút
core_numbers = nx.core_number(G)
max_k = max(core_numbers.values())
print(f"- Chỉ số K-Core lớn nhất (Max Core): {max_k}")

# Lấy đồ thị con ứng với K-Core lớn nhất
k_core_graph = nx.k_core(G)
print(f"- Số nút trong lõi K-Core cứng nhất (k={max_k}): {k_core_graph.number_of_nodes()}")

# Mô hình hóa sự phân rã của mạng theo K (K-Core Decomposition Plot)
k_values = range(1, max_k + 2)
core_sizes = []
for k in k_values:
    count = sum(1 for c in core_numbers.values() if c >= k)
    core_sizes.append(count)

plt.figure(figsize=(10, 6))
plt.plot(k_values, core_sizes, marker='o', color='purple', linestyle='-')
plt.title("Mô hình hóa K-Core: Sự phân rã của mạng theo cấp độ lõi")
plt.xlabel("Bậc K (K-Shell)")
plt.ylabel("Số lượng nút còn lại")
plt.grid(True)
plt.savefig("community_k_core_decomposition.png")
plt.close()

# SO SÁNH THUẬT TOÁN PHÁT HIỆN CỘNG ĐỒNG
print("\n>>> 2. SO SÁNH THUẬT TOÁN CỘNG ĐỒNG (LOUVAIN vs GREEDY)")

# --- THUẬT TOÁN A: LOUVAIN (Heuristic, tối ưu Modularity) ---
part_louvain = community_louvain.best_partition(G, weight='Weight')
mod_louvain = community_louvain.modularity(part_louvain, G)
num_com_louvain = len(set(part_louvain.values()))

# --- THUẬT TOÁN B: GREEDY MODULARITY (Phân cấp, gộp dần) ---
part_greedy_sets = list(greedy_modularity_communities(G, weight='Weight'))
# Chuyển đổi định dạng output của Greedy sang dạng dict {node: community_id} để so sánh
part_greedy = {}
for i, comm_set in enumerate(part_greedy_sets):
    for node in comm_set:
        part_greedy[node] = i
mod_greedy = nx.community.modularity(G, part_greedy_sets)
num_com_greedy = len(part_greedy_sets)

# Bảng so sánh chỉ số chất lượng
print(f"\n{'-'*60}")
print(f"{'Thuật toán':<20} | {'Modularity (Q)':<15} | {'Số cộng đồng':<15}")
print(f"{'-'*60}")
print(f"{'Louvain':<20} | {mod_louvain:<15.4f} | {num_com_louvain:<15}")
print(f"{'Greedy Modularity':<20} | {mod_greedy:<15.4f} | {num_com_greedy:<15}")
print(f"{'-'*60}")

if mod_louvain > mod_greedy:
    best_algo = "Louvain"
    best_partition = part_louvain
    print("=> KẾT LUẬN: Thuật toán Louvain tốt hơn về mặt cấu trúc (Modularity cao hơn).")
else:
    best_algo = "Greedy"
    best_partition = part_greedy
    print("=> KẾT LUẬN: Thuật toán Greedy tốt hơn về mặt cấu trúc.")

print(f"\n>>> DIỄN GIẢI CÁC CỘNG ĐỒNG CHÍNH (THEO {best_algo.upper()})")
# Gom nhóm các node theo cộng đồng
communities = {}
for node, com_id in best_partition.items():
    communities.setdefault(com_id, []).append(node)

# Sắp xếp các cộng đồng theo kích thước (số lượng node)
sorted_coms = sorted(communities.items(), key=lambda x: len(x[1]), reverse=True)
# In ra 5 cộng đồng lớn nhất và tự động gán nhãn dựa trên Hubs
for i in range(min(5, len(sorted_coms))):
    com_id, nodes = sorted_coms[i]
    top_nodes = sorted(nodes, key=lambda x: G.degree[x], reverse=True)[:5]
    print(f"  + Cộng đồng {i+1} (Size: {len(nodes)}): {', '.join(top_nodes)}")
    print(f"    -> Dự đoán chủ đề: Nhóm xoay quanh '{top_nodes[0]}'")


# KẾT QUẢ HIỂN THỊ TRÊN BỐ CỤC MẠNG (VISUALIZATION)
print("\n>>> 3. TRỰC QUAN HÓA BỐ CỤC MẠNG THEO CỘNG ĐỒNG")
# Thêm thuộc tính vào đồ thị để xuất Gephi 
nx.set_node_attributes(G, best_partition, 'Community_Best')
nx.set_node_attributes(G, core_numbers, 'K_Core_Level') # Thêm K-Core để lọc trong Gephi
nx.set_node_attributes(G, dict(G.degree()), 'Degree')

# Xuất file Gephi
output_gephi = "youtube_network_community.gexf"
nx.write_gexf(G, output_gephi)
print(f"- Đã xuất file '{output_gephi}' chứa thông tin cộng đồng và K-Core.")

# Vẽ nhanh bằng Matplotlib (Preview bố cục)
print("- Đang vẽ bố cục mạng (có thể mất thời gian)...")
plt.figure(figsize=(15, 15))
pos = nx.spring_layout(G, seed=42, k=0.15) # Spring layout mô phỏng lực đàn hồi

# Tô màu theo cộng đồng
cmap = plt.get_cmap('tab20')
# Lấy danh sách màu cho từng node dựa trên community id
node_colors = [best_partition.get(node) for node in G.nodes()]
nx.draw_networkx_nodes(G, pos, node_size=30, cmap=cmap, node_color=node_colors, alpha=0.8)
nx.draw_networkx_edges(G, pos, alpha=0.1) # Cạnh mờ để đỡ rối

# Gắn nhãn cho một số nút quan trọng (Top Degree) để dễ nhìn
top_degree_nodes = sorted(G.nodes(), key=lambda x: G.degree[x], reverse=True)[:15]
nx.draw_networkx_labels(G, pos, labels={n: n for n in top_degree_nodes}, 
                        font_size=10, font_color='black', font_weight='bold')

plt.title(f"Bố cục mạng phân chia theo thuật toán {best_algo} (Top 15 Labels)", fontsize=15)
plt.axis('off')
plt.savefig("community_network_layout_preview.png")
plt.close()
print(">>> HOÀN TẤT PHÂN TÍCH CỘNG ĐỒNG!")