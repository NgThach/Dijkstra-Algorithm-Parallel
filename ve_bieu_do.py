import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

try:
    df = pd.read_csv('ket_qua_full.csv')
except:
    print("Error reading CSV")
    exit()

# Tắt giảm độ bão hòa màu của seaborn
sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 11})

# Tự định nghĩa bộ màu đậm - high contrast
colors_bold = ['#000000', '#1f77b4', '#d62728', '#2ca02c', '#9467bd']
colors_method = ['#d62728', '#1f77b4']  # MPI - OpenMP

# ============================ 1. Biểu đồ thời gian ============================
plt.figure(figsize=(12, 6))
subset = df[df['Nodes'] == df['Nodes'].max()]

sns.lineplot(
    data=subset,
    x='Threads',
    y='Time',
    hue='Method',
    marker='o',
    linewidth=2.8,
    palette=colors_method
)

plt.title(f'Thoi gian thuc thi (N={df["Nodes"].max()})', fontsize=14, fontweight='bold')
plt.ylabel('Thoi gian (s)')
plt.xticks(range(1, 11))
plt.savefig('bieu_do_thoi_gian.png')

# ============================ 2. Speedup OpenMP ============================
plt.figure(figsize=(12, 6))

omp_df = df[df['Method'] == 'OpenMP'].copy()
omp_df['Speedup'] = 0.0

for n in omp_df['Nodes'].unique():
    base = omp_df[(omp_df['Nodes'] == n) & (omp_df['Threads'] == 1)]['Time'].values[0]
    omp_df.loc[omp_df['Nodes'] == n, 'Speedup'] = base / omp_df.loc[omp_df['Nodes'] == n, 'Time']

sns.lineplot(
    data=omp_df,
    x='Threads',
    y='Speedup',
    hue='Nodes',
    palette=colors_bold,
    marker='o',
    linewidth=2.8
)

plt.plot([1, 10], [1, 10], 'k--', label='Ideal', linewidth=1.8)
plt.title('Speedup OpenMP', fontsize=14, fontweight='bold')
plt.ylabel('Speedup (x)')
plt.xticks(range(1, 11))
plt.savefig('bieu_do_speedup_omp.png')

# ============================ 3. Speedup MPI ============================
plt.figure(figsize=(12, 6))

mpi_df = df[df['Method'] == 'MPI'].copy()
mpi_df['Speedup'] = 0.0

for n in mpi_df['Nodes'].unique():
    base = mpi_df[(mpi_df['Nodes'] == n) & (mpi_df['Threads'] == 1)]['Time'].values[0]
    mpi_df.loc[mpi_df['Nodes'] == n, 'Speedup'] = base / mpi_df.loc[mpi_df['Nodes'] == n, 'Time']

sns.lineplot(
    data=mpi_df,
    x='Threads',
    y='Speedup',
    hue='Nodes',
    palette=colors_bold,
    marker='o',
    linewidth=2.8
)

plt.plot([1, 10], [1, 10], 'k--', label='Ideal', linewidth=1.8)
plt.title('Speedup MPI (Apple M4)', fontsize=14, fontweight='bold')
plt.xticks(range(1, 11))
plt.ylabel("Speedup (x)")
plt.savefig('bieu_do_speedup_mpi.png')
