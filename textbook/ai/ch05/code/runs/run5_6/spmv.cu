// 程序 5.6.1：稀疏矩阵与向量相乘 y = Ax（5.6 节）。两个矩阵：
//   lap：2048×2048 网格上的二维拉普拉斯矩阵（五点差分，零件热分析），每行至多 5 个非零元；
//   pl ：幂律矩阵，2^20 行，第 i 行长度 min(4096, 1 + ⌊4u^(−0.8)⌋)（u 由 splitmix64 生成，与程序 5.6.2 同一规则），列号随机。
// 三种核函数：
//   csr_scalar：CSR 格式，一个线程算一行
//   csr_vector：CSR 格式，一个线程束算一行（32 个线程跨步 32 读这一行，最后洗牌求和）
//   ell       ：ELL 格式（每行补到同样长，按列主序存放），一个线程算一行——只用于拉普拉斯矩阵
// 有效带宽按 CSR 至少要搬运的字节计：val、col 各 4 字节/非零元，行指针，读 x、写 y 各一遍。
// 编译：nvcc -O3 -arch=native -o spmv spmv.cu
#include <cmath>
#include <cstdio>
#include "bench.cuh"

__global__ void csr_scalar(int N, const int* ptr, const int* col, const float* val, const float* x, float* y) {
    int r = blockIdx.x * blockDim.x + threadIdx.x;
    if (r >= N) return;
    float s = 0.0f;
    for (int k = ptr[r]; k < ptr[r + 1]; k++) s += val[k] * x[col[k]];
    y[r] = s;
}

__global__ void csr_vector(int N, const int* ptr, const int* col, const float* val, const float* x, float* y) {
    int r = (blockIdx.x * blockDim.x + threadIdx.x) / 32, lane = threadIdx.x % 32;
    if (r >= N) return;                                  // 同一线程束的 r 相同，整个线程束一起返回
    float s = 0.0f;
    for (int k = ptr[r] + lane; k < ptr[r + 1]; k += 32) s += val[k] * x[col[k]];
    for (int off = 16; off > 0; off >>= 1) s += __shfl_down_sync(0xffffffffu, s, off);
    if (lane == 0) y[r] = s;
}

__global__ void ell(int N, int width, const int* col, const float* val, const float* x, float* y) {
    int r = blockIdx.x * blockDim.x + threadIdx.x;
    if (r >= N) return;
    float s = 0.0f;
    for (int k = 0; k < width; k++) s += val[size_t(k) * N + r] * x[col[size_t(k) * N + r]];   // 相邻线程读相邻地址
    y[r] = s;
}

struct Csr {
    int N;
    std::vector<int> ptr, col;
    std::vector<float> val;
};

static Csr laplacian(int n) {
    Csr a{n * n, {0}, {}, {}};
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++) {
            const int di[5] = {-1, 0, 0, 0, 1}, dj[5] = {0, -1, 0, 1, 0};
            for (int t = 0; t < 5; t++) {
                int ii = i + di[t], jj = j + dj[t];
                if (ii < 0 || ii >= n || jj < 0 || jj >= n) continue;
                a.col.push_back(ii * n + jj);
                a.val.push_back(t == 2 ? 4.0f : -1.0f);
            }
            a.ptr.push_back(int(a.col.size()));
        }
    return a;
}

static double uniform(unsigned long long i) { return (double(splitmix64(i) >> 11) + 1.0) / 9007199254740992.0; }

static Csr powerlaw(int N) {
    Csr a{N, {0}, {}, {}};
    for (int i = 0; i < N; i++) {
        int len = int(std::fmin(4096.0, 1.0 + std::floor(4.0 * std::pow(uniform(i + (7ull << 40)), -0.8))));
        for (int t = 0; t < len; t++) {
            unsigned long long h = splitmix64(a.col.size() + (9ull << 40));
            a.col.push_back(int(h % N));
            a.val.push_back(float(h >> 40 & 1023) / 1024.0f - 0.5f);
        }
        a.ptr.push_back(int(a.col.size()));
    }
    return a;
}

template <typename T>
static T* dev(const std::vector<T>& h) {
    T* d;
    CHECK(cudaMalloc(&d, h.size() * sizeof(T)));
    CHECK(cudaMemcpy(d, h.data(), h.size() * sizeof(T), cudaMemcpyHostToDevice));
    return d;
}

int main() {
    bool ok = true;
    std::printf("{");
    const char* mats[2] = {"lap", "pl"};
    for (int m = 0; m < 2; m++) {
        Csr a = m == 0 ? laplacian(2048) : powerlaw(1 << 20);
        const int N = a.N;
        const size_t nnz = a.col.size();
        std::vector<float> hx(N), hy(N);
        for (int i = 0; i < N; i++) hx[i] = float(splitmix64(i + (3ull << 40)) % 1000) / 1000.0f;
        std::vector<double> ref(N);
        for (int r = 0; r < N; r++)
            for (int k = a.ptr[r]; k < a.ptr[r + 1]; k++) ref[r] += double(a.val[k]) * hx[a.col[k]];
        int *ptr = dev(a.ptr), *col = dev(a.col);
        float *val = dev(a.val), *x = dev(hx), *y;
        CHECK(cudaMalloc(&y, N * sizeof(float)));
        const double gb = (nnz * 8.0 + (N + 1) * 4.0 + 2.0 * N * 4) / 1e9;
        auto check = [&] {
            CHECK(cudaMemcpy(hy.data(), y, N * sizeof(float), cudaMemcpyDeviceToHost));
            for (int r = 0; r < N; r++)
                if (std::fabs(hy[r] - ref[r]) > 1e-3 * (1.0 + std::fabs(ref[r]))) return false;
            return true;
        };
        const int bs = 256;
        CHECK(cudaMemset(y, 0xFF, N * sizeof(float)));
        float t_s = time_ms([&] { csr_scalar<<<(N + bs - 1) / bs, bs>>>(N, ptr, col, val, x, y); });
        ok = ok && check();
        CHECK(cudaMemset(y, 0xFF, N * sizeof(float)));
        float t_v = time_ms([&] { csr_vector<<<int((size_t(N) * 32 + bs - 1) / bs), bs>>>(N, ptr, col, val, x, y); });
        ok = ok && check();
        std::printf("%s\"%s_nnz\": %zu, \"%s_scalar_us\": %.1f, \"%s_scalar_GBs\": %.1f, \"%s_vector_us\": %.1f, \"%s_vector_GBs\": %.1f",
                    m ? ", " : "", mats[m], nnz, mats[m], t_s * 1e3, mats[m], gb / (t_s * 1e-3), mats[m], t_v * 1e3, mats[m], gb / (t_v * 1e-3));
        if (m == 0) {                                     // 拉普拉斯矩阵的 ELL 格式：宽 5，补的位置列号取本行、值取 0
            const int width = 5;
            std::vector<int> ec(size_t(width) * N);
            std::vector<float> ev(size_t(width) * N, 0.0f);
            for (int r = 0; r < N; r++)
                for (int k = 0; k < width; k++) {
                    int src = a.ptr[r] + k;
                    bool in = src < a.ptr[r + 1];
                    ec[size_t(k) * N + r] = in ? a.col[src] : r;
                    ev[size_t(k) * N + r] = in ? a.val[src] : 0.0f;
                }
            int* ecol = dev(ec);
            float* eval = dev(ev);
            CHECK(cudaMemset(y, 0xFF, N * sizeof(float)));
            float t_e = time_ms([&] { ell<<<(N + bs - 1) / bs, bs>>>(N, width, ecol, eval, x, y); });
            ok = ok && check();
            std::printf(", \"lap_ell_us\": %.1f, \"lap_ell_GBs\": %.1f", t_e * 1e3, gb / (t_e * 1e-3));
            CHECK(cudaFree(ecol));
            CHECK(cudaFree(eval));
        }
        CHECK(cudaFree(ptr));
        CHECK(cudaFree(col));
        CHECK(cudaFree(val));
        CHECK(cudaFree(x));
        CHECK(cudaFree(y));
    }
    std::printf(", \"correct\": %s}\n", ok ? "true" : "false");
    return 0;
}
