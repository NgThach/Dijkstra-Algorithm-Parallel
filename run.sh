#!/bin/bash

# --- CẤU HÌNH ---
OUTPUT_FILE="ket_qua_full.csv"
# Danh sách Node cho MPI (OpenMP đã tự loop trong code C)
# Chạy đến 100,000 node!
MPI_NODES="100 1000 10000 50000 100000"

# --- BƯỚC 1: BIÊN DỊCH ---
echo "--- 1. DANG BIEN DICH ---"

# OpenMP (Dùng file CSR mới)
if gcc -Xpreprocessor -fopenmp -I/opt/homebrew/opt/libomp/include -L/opt/homebrew/opt/libomp/lib -lomp bench_omp.c -o exe_omp; then
    echo "   - OpenMP (CSR): OK"
else
    echo "   - OpenMP: FAILED. Check libomp"
    exit 1
fi

# MPI (Dùng file CSR mới)
if mpicc bench_mpi.c -o exe_mpi; then
    echo "   - MPI (CSR): OK"
else
    echo "   - MPI: FAILED. Check open-mpi"
    exit 1
fi

# --- BƯỚC 2: CHẠY BENCHMARK ---
echo "--- 2. DANG CHAY BENCHMARK ---"
echo "Method,Nodes,Threads,Time" > $OUTPUT_FILE

echo ">>> Running OpenMP (100 - 100,000 nodes)..."
./exe_omp >> $OUTPUT_FILE

echo ">>> Running MPI (100 - 100,000 nodes)..."
for n in $MPI_NODES
do
    # Chạy loop từ 1 đến 10 processes
    for p in {1..10}
    do
        # In ra màn hình để biết đang chạy đến đâu
        echo "    - MPI: Nodes=$n, Procs=$p"
        # Mpirun với n tham số
        mpirun -np $p ./exe_mpi $n | grep "MPI," >> $OUTPUT_FILE
    done
done

echo "   - Da luu ket qua vao $OUTPUT_FILE"

# --- BƯỚC 3: VẼ BIỂU ĐỒ ---
echo "--- 3. DANG VE BIEU DO ---"

# Tạo script Python tại chỗ để đảm bảo khớp dữ liệu
cat << 'PY_EOF' > ve_bieu_do.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

try:
    df = pd.read_csv('ket_qua_full.csv')
except:
    print("Error reading CSV")
    exit()

sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 11})

# 1. Biểu đồ Thời gian
plt.figure(figsize=(12, 6))
# Lọc lấy OpenMP và MPI tại max node để so sánh
subset = df[df['Nodes'] == df['Nodes'].max()]
sns.lineplot(data=subset, x='Threads', y='Time', hue='Method', marker='o', linewidth=2.5)
plt.title(f'Thoi gian thuc thi (N={df["Nodes"].max()})', fontsize=14, fontweight='bold')
plt.ylabel('Thoi gian (s)')
plt.xticks(range(1, 11))
plt.savefig('bieu_do_thoi_gian.png')

# 2. Biểu đồ Speedup OpenMP
plt.figure(figsize=(12, 6))
omp_df = df[df['Method'] == 'OpenMP'].copy()
omp_df['Speedup'] = 0.0
for n in omp_df['Nodes'].unique():
    base = omp_df[(omp_df['Nodes'] == n) & (omp_df['Threads'] == 1)]['Time'].values[0]
    omp_df.loc[omp_df['Nodes'] == n, 'Speedup'] = base / omp_df.loc[omp_df['Nodes'] == n, 'Time']

sns.lineplot(data=omp_df, x='Threads', y='Speedup', hue='Nodes', marker='o', palette='viridis')
plt.plot([1, 10], [1, 10], 'k--', alpha=0.5, label='Ideal')
plt.title('Speedup OpenMP (Apple M4)', fontsize=14, fontweight='bold')
plt.ylabel('Speedup (x)')
plt.xticks(range(1, 11))
plt.savefig('bieu_do_speedup_omp.png')

# 3. Biểu đồ Speedup MPI
plt.figure(figsize=(12, 6))
mpi_df = df[df['Method'] == 'MPI'].copy()
mpi_df['Speedup'] = 0.0
for n in mpi_df['Nodes'].unique():
    try:
        base = mpi_df[(mpi_df['Nodes'] == n) & (mpi_df['Threads'] == 1)]['Time'].values[0]
        mpi_df.loc[mpi_df['Nodes'] == n, 'Speedup'] = base / mpi_df.loc[mpi_df['Nodes'] == n, 'Time']
    except: pass

sns.lineplot(data=mpi_df, x='Threads', y='Speedup', hue='Nodes', marker='o', palette='magma')
plt.title('Speedup MPI (Apple M4)', fontsize=14, fontweight='bold')
plt.xticks(range(1, 11))
plt.savefig('bieu_do_speedup_mpi.png')
PY_EOF

# Chạy Python
python3 ve_bieu_do.py

echo "HOAN TAT! Kiem tra 3 file anh .png"
