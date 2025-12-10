import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys

# 1. Đọc dữ liệu
try:
    df = pd.read_csv('ket_qua_full.csv')
except:
    print("Lỗi: Không tìm thấy file ket_qua_full.csv")
    sys.exit()

# Cấu hình giao diện đẹp, font chữ lớn
sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 12, 'lines.linewidth': 2.5, 'lines.markersize': 8})
custom_palette = sns.color_palette("tab10")

# ==============================================================================
# BIỂU ĐỒ A: LINE CHART - SO SÁNH TUẦN TỰ VS SONG SONG (TẠI N LỚN NHẤT)
# Mục đích: Xem đường song song "chui" xuống dưới đường tuần tự khi nào?
# ==============================================================================
def ve_bieu_do_line_baseline(n_val, filename):
    plt.figure(figsize=(12, 7))
    
    # Lấy dữ liệu của N này
    subset = df[df['Nodes'] == n_val].copy()
    if subset.empty: return

    # 1. Vẽ các đường Song song (OpenMP và MPI)
    sns.lineplot(data=subset, x='Threads', y='Time', hue='Method', style='Method',
                 markers=True, dashes=False, palette=custom_palette)

    # 2. Lấy thời gian Tuần tự (Lấy OpenMP tại Threads=1 làm chuẩn)
    try:
        tuan_tu_time = subset[(subset['Method'] == 'OpenMP') & (subset['Threads'] == 1)]['Time'].values[0]
        
        # 3. Vẽ đường Tuần tự (Đường nằm ngang màu đỏ nét đứt)
        plt.axhline(y=tuan_tu_time, color='r', linestyle='--', linewidth=2, label=f'Tuần tự (1 Core): {tuan_tu_time:.2f}s')
        
        # Thêm chú thích ngay trên đường kẻ
        plt.text(1.5, tuan_tu_time, 'Baseline (Tuần tự)', color='red', 
                 verticalalignment='bottom', fontweight='bold')
    except:
        pass

    plt.title(f'So sánh Thời gian: Tuần tự vs Song song (N={n_val})', fontsize=14, fontweight='bold')
    plt.ylabel('Thời gian thực thi (Giây)')
    plt.xlabel('Số luồng (Cores/Processes)')
    plt.xticks(range(1, 11))
    plt.legend(title='Phương pháp')
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    print(f"Đã vẽ: {filename}")

# ==============================================================================
# BIỂU ĐỒ B: BAR CHART - SO SÁNH TRỰC DIỆN (SPEEDUP THỰC TẾ)
# Mục đích: Thấy rõ Song song nhanh gấp mấy lần Tuần tự ở từng mức dữ liệu
# ==============================================================================
def ve_bieu_do_cot_so_sanh():
    plt.figure(figsize=(12, 7))
    
    # Tạo DataFrame mới để so sánh
    # Lấy thời gian chạy 1 luồng (Tuần tự) và thời gian chạy nhanh nhất (Best Parallel)
    compare_data = []
    
    for n in df['Nodes'].unique():
        # Lấy thời gian tuần tự (OpenMP 1 thread)
        try:
            t_seq = df[(df['Method'] == 'OpenMP') & (df['Nodes'] == n) & (df['Threads'] == 1)]['Time'].values[0]
            compare_data.append({'Nodes': n, 'Type': 'Tuần tự (1 Core)', 'Time': t_seq})
            
            # Lấy thời gian song song tốt nhất (Min time của OpenMP hoặc MPI)
            t_par_omp = df[(df['Method'] == 'OpenMP') & (df['Nodes'] == n)]['Time'].min()
            t_par_mpi = df[(df['Method'] == 'MPI') & (df['Nodes'] == n)]['Time'].min()
            
            # Chọn cái nào nhanh hơn giữa OpenMP và MPI để đại diện cho "Song song"
            t_best = min(t_par_omp, t_par_mpi)
            compare_data.append({'Nodes': n, 'Type': 'Song song (Best)', 'Time': t_best})
        except:
            continue
            
    df_compare = pd.DataFrame(compare_data)
    
    # Vẽ biểu đồ cột
    ax = sns.barplot(data=df_compare, x='Nodes', y='Time', hue='Type', palette=['#ff9999', '#66b3ff'], edgecolor='black')
    
    plt.title('Đối đầu trực tiếp: Tuần tự vs Song song tối ưu', fontsize=14, fontweight='bold')
    plt.ylabel('Thời gian (Giây) - Thấp hơn là tốt hơn')
    plt.xlabel('Kích thước đồ thị (Số đỉnh)')
    
    # Ghi số liệu lên đầu cột
    for p in ax.patches:
        if p.get_height() > 0:
            ax.annotate(f'{p.get_height():.2f}s', 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha='center', va='center', xytext=(0, 5), 
                        textcoords='offset points', fontsize=9, fontweight='bold')

    plt.tight_layout()
    plt.savefig('bieu_do_so_sanh_cot.png', dpi=300)
    print("Đã vẽ: bieu_do_so_sanh_cot.png")

# --- CHẠY CÁC HÀM VẼ ---

# 1. Vẽ Line Chart cho tập dữ liệu lớn nhất (thường là 100k)
max_n = df['Nodes'].max()
ve_bieu_do_line_baseline(max_n, 'bieu_do_line_so_sanh.png')

# 2. Vẽ Bar Chart tổng hợp
ve_bieu_do_cot_so_sanh()