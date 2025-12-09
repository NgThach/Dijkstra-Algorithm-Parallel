#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
#include <limits.h>

#define INF 99999999
#define AVG_DEGREE 100 // Trung bình mỗi node kết nối với 100 node khác

// Cấu trúc đồ thị nén (CSR)
typedef struct {
    int *row_ptr;
    int *col_ind;
    int *weights;
    int num_nodes;
    int num_edges;
} CSRGraph;

void generate_csr_graph(int n, CSRGraph *g) {
    g->num_nodes = n;
    long estimated_edges = (long)n * AVG_DEGREE;
    
    g->row_ptr = (int*)malloc((n + 1) * sizeof(int));
    g->col_ind = (int*)malloc(estimated_edges * sizeof(int));
    g->weights = (int*)malloc(estimated_edges * sizeof(int));

    if (!g->row_ptr || !g->col_ind || !g->weights) {
        printf("ERROR: Khong du RAM (Malloc failed)\n");
        exit(1);
    }

    int edge_count = 0;
    g->row_ptr[0] = 0;

    // Sinh ngẫu nhiên (Tuần tự để đảm bảo cấu trúc CSR)
    for (int i = 0; i < n; i++) {
        int num_neighbors = (rand() % AVG_DEGREE) + (AVG_DEGREE / 2); // 50-150 cạnh
        for (int k = 0; k < num_neighbors; k++) {
            if (edge_count >= estimated_edges) break;
            g->col_ind[edge_count] = rand() % n;
            g->weights[edge_count] = (rand() % 100) + 1;
            edge_count++;
        }
        g->row_ptr[i+1] = edge_count;
    }
    g->num_edges = edge_count;
}

void dijkstra(CSRGraph *g, int src) {
    int n = g->num_nodes;
    int *dist = (int*)malloc(n * sizeof(int));
    int *visited = (int*)malloc(n * sizeof(int));

    #pragma omp parallel for
    for(int i=0; i<n; i++) { dist[i]=INF; visited[i]=0; }
    dist[src] = 0;

    for (int count = 0; count < n; count++) {
        int u = -1;
        int min_val = INF;
        
        // Giai đoạn 1: Tìm Min (OpenMP cực hiệu quả ở đây với đồ thị lớn)
        #pragma omp parallel
        {
            int u_local = -1; int min_local = INF;
            #pragma omp for nowait
            for (int i = 0; i < n; i++) {
                if (!visited[i] && dist[i] < min_local) {
                    min_local = dist[i]; u_local = i;
                }
            }
            #pragma omp critical
            {
                if (min_local < min_val) { min_val = min_local; u = u_local; }
            }
        }
        
        if (u == -1 || dist[u] == INF) break;
        visited[u] = 1;

        // Giai đoạn 2: Cập nhật (Dựa trên CSR)
        int start = g->row_ptr[u];
        int end = g->row_ptr[u+1];

        // Với đồ thị thưa, vòng lặp này ngắn (khoảng 100 lần), chạy tuần tự nhanh hơn tạo thread
        for (int i = start; i < end; i++) {
            int v = g->col_ind[i];
            int w = g->weights[i];
            if (!visited[v] && dist[u] + w < dist[v]) {
                dist[v] = dist[u] + w;
            }
        }
    }
    free(dist); free(visited);
}

int main() {
    // Cấu hình test
    int nodes[] = {100, 1000, 10000, 50000, 100000}; 
    int num_tests = 5;
    int max_threads = 10; 

    // Header được in bởi run.sh, ở đây chỉ in dữ liệu
    for (int t = 0; t < num_tests; t++) {
        int n = nodes[t];
        CSRGraph g;
        generate_csr_graph(n, &g);

        for (int p = 1; p <= max_threads; p++) {
            omp_set_num_threads(p);
            double start = omp_get_wtime();
            dijkstra(&g, 0);
            double end = omp_get_wtime();
            printf("OpenMP,%d,%d,%f\n", n, p, end - start);
        }
        
        free(g.row_ptr); free(g.col_ind); free(g.weights);
    }
    return 0;
}