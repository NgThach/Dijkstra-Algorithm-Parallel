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

# Cấu hình giao diện chung
sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 12})

# Hàm vẽ biểu đồ cột đa năng
def ve_bieu_do_cot(n_val, filename):
    plt.figure(figsize=(14, 7))
    
    # Lọc dữ liệu tại số Node này
    subset = df[df['Nodes'] == n_val].copy()
    
    if subset.empty:
        print(f"Không có dữ liệu cho N={n_val}")
        return

    # Vẽ biểu đồ cột nhóm
    ax = sns.barplot(data=subset, x='Threads', y='Time', hue='Method', 
                     palette="muted", edgecolor="black", linewidth=1)

    # Tiêu đề thông minh: Cảnh báo nếu N nhỏ
    if n_val <= 1000:
        msg = "(Lưu ý: Overhead cao -> Càng nhiều luồng càng chậm!)"
    else:
        msg = "(Thấp hơn là Tốt hơn)"

    plt.title(f'So sánh Thời gian chạy tại N={n_val} {msg}', 
              fontsize=16, fontweight='bold', pad=20)
    plt.ylabel('Thời gian (Giây)', fontsize=13)
    plt.xlabel('Số luồng (Threads/Processes)', fontsize=13)
    
    # Đặt Legend ở góc trên trái để tránh che mất cột dữ liệu (thường cao bên phải ở N nhỏ)
    plt.legend(title='Phương pháp', loc='upper left')
    
    # --- THÊM NHÃN SỐ LIỆU ---
    for container in ax.containers:
        # Nếu N nhỏ (chạy cực nhanh), hiển thị 4 số lẻ để thấy sự khác biệt
        # Nếu N lớn, chỉ cần 2 số lẻ cho gọn
        fmt_str = '%.4f' if n_val <= 1000 else '%.2f'
        
        # Xoay chữ 90 độ nếu N nhỏ (để số không bị đè lên nhau vì cột thấp)
        rot = 90 if n_val <= 1000 else 0
        
        ax.bar_label(container, fmt=fmt_str, padding=3, fontsize=10, rotation=rot)

    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    print(f"Đã vẽ xong: {filename}")

# --- THỰC HIỆN VẼ ---

# 1. Vòng lặp vẽ TẤT CẢ các mức Node
ds_node = [100, 1000, 10000, 50000, 100000]

print("--- Đang vẽ biểu đồ cột ---")
for n in ds_node:
    ve_bieu_do_cot(n, f'bieu_do_cot_{n}.png')

# 2. Vẽ biểu đồ Speedup tại N=100,000 (như cũ)
print("--- Đang vẽ biểu đồ Speedup ---")
plt.figure(figsize=(14, 7))
subset_100k = df[df['Nodes'] == 100000].copy()
subset_100k['Speedup'] = 0.0

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
print("HOÀN TẤT! Đã vẽ xong tất cả biểu đồ.")