// 程序 4.7.1：矩阵转置的四个版本（4.6、4.7 节）。B = Aᵀ，A 为 n×n 的单精度矩阵，行主序。
//   copy      ：B = A，读写都合并访问——带宽的上限（参照）
//   naive     ：按行读 A（合并），按列写 B（跨步 n，不合并）
//   tiled     ：32×32 的块先读进共享内存，再按行写出——读写都合并，但按列读共享内存有 32 路存储体冲突
//   padded    ：同上，共享内存每行多留 1 个字（33 列），消除存储体冲突
// n 须为 TILE（32）的倍数，且 n² < 2³¹（下标用 int）。编译：nvcc -O3 -arch=native -o transpose transpose.cu
#include <algorithm>
#include <cstdio>
#include <vector>
#include "check.cuh"

constexpr int TILE = 32, ROWS = 8;          // 每个线程块 32×8 个线程，每个线程搬 4 个元素

__global__ void copy(const float* a, float* b, int n) {
    int x = blockIdx.x * TILE + threadIdx.x, y = blockIdx.y * TILE + threadIdx.y;
    for (int j = 0; j < TILE; j += ROWS) b[(y + j) * n + x] = a[(y + j) * n + x];
}

__global__ void naive(const float* a, float* b, int n) {
    int x = blockIdx.x * TILE + threadIdx.x, y = blockIdx.y * TILE + threadIdx.y;
    for (int j = 0; j < TILE; j += ROWS) b[x * n + (y + j)] = a[(y + j) * n + x];   // 写：相邻线程相隔 n 个元素
}

template <int PAD>
__global__ void tiled(const float* a, float* b, int n) {
    __shared__ float t[TILE][TILE + PAD];
    int x = blockIdx.x * TILE + threadIdx.x, y = blockIdx.y * TILE + threadIdx.y;
    for (int j = 0; j < TILE; j += ROWS) t[threadIdx.y + j][threadIdx.x] = a[(y + j) * n + x];   // 按行读，合并
    __syncthreads();                                                                         // 整块读完再写
    x = blockIdx.y * TILE + threadIdx.x;                                                     // 转置后的块位置
    y = blockIdx.x * TILE + threadIdx.y;
    for (int j = 0; j < TILE; j += ROWS) b[(y + j) * n + x] = t[threadIdx.x][threadIdx.y + j];   // 按列读共享内存，按行写，合并
}

template <typename K>
static float time_ms(K kernel, const float* a, float* b, int n) {
    dim3 grid(n / TILE, n / TILE), block(TILE, ROWS);
    cudaEvent_t t0, t1;
    CHECK(cudaEventCreate(&t0));
    CHECK(cudaEventCreate(&t1));
    kernel<<<grid, block>>>(a, b, n);
    CHECK_LAUNCH();
    std::vector<float> ms(20);
    for (float& m : ms) {
        CHECK(cudaEventRecord(t0));
        kernel<<<grid, block>>>(a, b, n);
        CHECK(cudaEventRecord(t1));
        CHECK(cudaEventSynchronize(t1));
        CHECK(cudaEventElapsedTime(&m, t0, t1));
    }
    CHECK(cudaGetLastError());
    CHECK(cudaEventDestroy(t0));
    CHECK(cudaEventDestroy(t1));
    std::sort(ms.begin(), ms.end());
    return ms[ms.size() / 2];
}

static bool transposed(const std::vector<float>& a, const std::vector<float>& b, int n, bool copy = false) {
    for (int i = 0; i < n; i += 97)                      // 抽样核对（每隔 97 行、89 列）
        for (int j = 0; j < n; j += 89)
            if (b[size_t(j) * n + i] != a[copy ? size_t(j) * n + i : size_t(i) * n + j]) return false;
    return true;
}

// 每个版本运行前把 b 填成全 1 的位模式（NaN），免得上一个版本留下的正确结果蒙混过关
template <typename K>
static bool run_check(K kernel, float* ms, const float* a, float* b, int n, size_t bytes,
                      const std::vector<float>& ha, std::vector<float>& hb, bool copy = false) {
    CHECK(cudaMemset(b, 0xFF, bytes));
    *ms = time_ms(kernel, a, b, n);
    CHECK(cudaMemcpy(hb.data(), b, bytes, cudaMemcpyDeviceToHost));
    return transposed(ha, hb, n, copy);
}

int main() {
    const int n = 8192;                                  // 256 MiB 的矩阵
    const size_t bytes = size_t(n) * n * sizeof(float);
    std::vector<float> ha(size_t(n) * n), hb(size_t(n) * n);
    for (size_t i = 0; i < ha.size(); i++) ha[i] = float(i % 65521);
    float *a, *b;
    CHECK(cudaMalloc(&a, bytes));
    CHECK(cudaMalloc(&b, bytes));
    CHECK(cudaMemcpy(a, ha.data(), bytes, cudaMemcpyHostToDevice));
    const double gb = 2.0 * bytes / 1e9;                  // 读一遍、写一遍
    float tc, tn, tt, tp;
    bool okc = run_check(copy, &tc, a, b, n, bytes, ha, hb, true);
    bool okn = run_check(naive, &tn, a, b, n, bytes, ha, hb);
    bool okt = run_check(tiled<0>, &tt, a, b, n, bytes, ha, hb);
    bool okp = run_check(tiled<1>, &tp, a, b, n, bytes, ha, hb);
    std::printf("{\"n\": %d, \"copy_GBs\": %.1f, \"naive_GBs\": %.1f, \"tiled_GBs\": %.1f, \"padded_GBs\": %.1f, \"correct\": %s}\n",
                n, gb / (tc * 1e-3), gb / (tn * 1e-3), gb / (tt * 1e-3), gb / (tp * 1e-3), okc && okn && okt && okp ? "true" : "false");
    CHECK(cudaFree(a));
    CHECK(cudaFree(b));
    return 0;
}
