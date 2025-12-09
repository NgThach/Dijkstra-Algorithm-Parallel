#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>

#define INF 99999999
#define AVG_DEGREE 100

// Cấu trúc CSR (Giống OpenMP)
typedef struct {
    int *row_ptr; int *col_ind; int *weights;
    int num_nodes;
} CSRGraph;

void generate_csr_graph(int n, CSRGraph *g) {
    srand(42); // Seed cố định để TẤT CẢ các rank sinh đồ thị GIỐNG HỆT NHAU
    g->num_nodes = n;
    long estimated_edges = (long)n * AVG_DEGREE;
    g->row_ptr = (int*)malloc((n + 1) * sizeof(int));
    g->col_ind = (int*)malloc(estimated_edges * sizeof(int));
    g->weights = (int*)malloc(estimated_edges * sizeof(int));

    int edge_count = 0; g->row_ptr[0] = 0;
    for (int i = 0; i < n; i++) {
        int num_neighbors = (rand() % AVG_DEGREE) + (AVG_DEGREE / 2);
        for (int k = 0; k < num_neighbors; k++) {
            if (edge_count >= estimated_edges) break;
            g->col_ind[edge_count] = rand() % n;
            g->weights[edge_count] = (rand() % 100) + 1;
            edge_count++;
        }
        g->row_ptr[i+1] = edge_count;
    }
}

int main(int argc, char** argv) {
    MPI_Init(&argc, &argv);
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (argc < 2) { MPI_Finalize(); return 0; }
    int n = atoi(argv[1]);

    // Mỗi rank quản lý một phần mảng dist
    // Để đơn giản cho Benchmark 100k nodes, ta dùng Replicated Dist array 
    // nhưng chia việc update.
    int *dist = (int*)malloc(n * sizeof(int));
    int *visited = (int*)malloc(n * sizeof(int));
    
    // Tạo đồ thị (Mỗi rank tự tạo bản copy để tra cứu nhanh)
    CSRGraph g;
    generate_csr_graph(n, &g);

    MPI_Barrier(MPI_COMM_WORLD);
    double start = MPI_Wtime();

    for(int i=0; i<n; i++) { dist[i]=INF; visited[i]=0; }
    dist[0] = 0;

    for (int i = 0; i < n; i++) {
        // 1. Tìm Min (Mỗi rank tìm min cục bộ trên toàn mảng dist của mình)
        // Trong thực tế MPI, dist sẽ được chia nhỏ, nhưng ở đây ta mô phỏng logic
        struct { int val; int rank; } l_min = {INF, -1}, g_min;
        
        // Chia vùng tìm kiếm để tăng tốc
        int chunk = n / size;
        int start_node = rank * chunk;
        int end_node = (rank == size - 1) ? n : (rank + 1) * chunk;

        for (int v = start_node; v < end_node; v++) {
            if (!visited[v] && dist[v] < l_min.val) {
                l_min.val = dist[v]; l_min.rank = v;
            }
        }

        // Giao tiếp tìm Global Min
        MPI_Allreduce(&l_min, &g_min, 1, MPI_2INT, MPI_MINLOC, MPI_COMM_WORLD);
        
        int u = g_min.rank;
        if (g_min.val == INF) break;
        visited[u] = 1; // Rank nào cũng đánh dấu đã thăm

        // 2. Cập nhật (Relaxation)
        // Vì ai cũng giữ đồ thị (CSR), ai cũng có thể tra cứu cạnh của u
        // Ta chia việc cập nhật cho các rank
        int row_start = g.row_ptr[u];
        int row_end = g.row_ptr[u+1];

        // Rank 0 (hoặc owner) broadcast thông tin cần thiết? 
        // Vì là Replicated Graph, mọi người đều BIẾT u kết nối với ai.
        // KHÔNG CẦN BROADCAST CẠNH (Tiết kiệm thời gian truyền tin cực lớn)
        // Chỉ cần cập nhật dist.
        
        for (int k = row_start; k < row_end; k++) {
            int v = g.col_ind[k];
            int w = g.weights[k];
            if (!visited[v] && dist[u] + w < dist[v]) {
                dist[v] = dist[u] + w;
            }
        }
        // Lưu ý: Phiên bản này là "Replicated Compute" cho bước Update 
        // để phù hợp với việc benchmark thuật toán Dijkstra trên đồ thị thưa.
    }

    double end = MPI_Wtime();
    if (rank == 0) {
        printf("MPI,%d,%d,%f\n", n, size, end - start);
    }

    free(g.row_ptr); free(g.col_ind); free(g.weights);
    free(dist); free(visited);
    MPI_Finalize();
    return 0;
}