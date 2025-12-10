import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import numpy as np

# 1. Đọc dữ liệu
try:
    df = pd.read_csv('ket_qua_full.csv')
except:
    print("Lỗi: Không tìm thấy file ket_qua_full.csv")
    sys.exit()

# Cấu hình giao diện
sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 12})

# Hàm vẽ biểu đồ cột cho một mức Node cụ thể
def ve_bieu_do_cot(n_val, filename):
    plt.figure(figsize=(14, 7))
    
    # Lọc dữ liệu tại số Node này
    subset = df[df['Nodes'] == n_val].copy()
    
    if subset.empty:
        return

    # Vẽ biểu đồ cột nhóm (Grouped Bar Chart)
    # x = Số luồng, y = Thời gian, hue = Phương pháp (để so sánh màu)
    ax = sns.barplot(data=subset, x='Threads', y='Time', hue='Method', 
                     palette="muted", edgecolor="black", linewidth=1)

    plt.title(f'So sánh Thời gian chạy tại N={n_val} (Thấp hơn là Tốt hơn)', 
              fontsize=16, fontweight='bold', pad=20)
    plt.ylabel('Thời gian (Giây)', fontsize=13)
    plt.xlabel('Số luồng (Threads/Processes)', fontsize=13)
    plt.legend(title='Phương pháp', loc='upper right')
    
    # --- THÊM NHÃN SỐ LIỆU LÊN ĐẦU CỘT ---
    # Đoạn này giúp hiện số giây cụ thể trên đầu mỗi cột
    for container in ax.containers:
        ax.bar_label(container, fmt='%.2f', padding=3, fontsize=10)

    # Thêm lưới ngang để dễ gióng
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    print(f"Đã vẽ xong: {filename}")

# --- THỰC HIỆN VẼ ---

# 1. Vẽ cho trường hợp lớn nhất (N=100,000) - Quan trọng nhất
ve_bieu_do_cot(100000, 'bieu_do_cot_100k.png')

# 2. Vẽ cho trường hợp trung bình (N=50,000)
ve_bieu_do_cot(50000, 'bieu_do_cot_50k.png')

# 3. Vẽ biểu đồ so sánh Hiệu quả (Speedup) dạng cột tại N=100,000
plt.figure(figsize=(14, 7))
subset_100k = df[df['Nodes'] == 100000].copy()
subset_100k['Speedup'] = 0.0

# Tính Speedup
for method in ['OpenMP', 'MPI']:
    try:
        base = subset_100k[(subset_100k['Method'] == method) & (subset_100k['Threads'] == 1)]['Time'].values[0]
        subset_100k.loc[subset_100k['Method'] == method, 'Speedup'] = base / subset_100k['Time']
    except: pass

ax2 = sns.barplot(data=subset_100k, x='Threads', y='Speedup', hue='Method',
                  palette="viridis", edgecolor="black", linewidth=1)

plt.title('So sánh Tốc độ tăng tốc (Speedup) tại N=100,000', fontsize=16, fontweight='bold', pad=20)
plt.ylabel('Speedup (Lần)', fontsize=13)
plt.xlabel('Số luồng', fontsize=13)
plt.axhline(y=1, color='red', linestyle='--', label='Mức cơ sở (1x)')
plt.legend()

for container in ax2.containers:
    ax2.bar_label(container, fmt='%.1fx', padding=3, fontsize=10)

plt.tight_layout()
plt.savefig('bieu_do_cot_speedup.png', dpi=300)
print("Đã vẽ xong: bieu_do_cot_speedup.png")