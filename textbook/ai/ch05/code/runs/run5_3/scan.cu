// 程序 5.3.1：前缀和（包含式扫描）的三段式实现与 CUB（5.3 节）。对 n = 2^24 个 32 位无符号整数。
//   scan_blocks：每个线程块扫描 1024 个数——线程束内用 __shfl_up_sync 扫描，32 个线程束的和放进共享内存再由 0 号线程束扫描，
//                再加回各线程束；每块把自己的总和写进 sums
//   scan（主机函数）：对 sums 递归地做同样的扫描（2^24 → 16384 → 16 → 1），再用 add_offsets 把前面各块的总和加回来
//   参照：cub::DeviceScan::InclusiveSum（单遍扫描，带“退耦回看”）
// 编译：nvcc -O3 -arch=native -o scan scan.cu
#include <cstdio>
#include <cub/cub.cuh>
#include "bench.cuh"

constexpr int B = 1024;                      // 每个线程块 1024 个线程、32 个线程束
constexpr unsigned FULL = 0xffffffffu;

__device__ __forceinline__ unsigned warp_scan(unsigned v, int lane) {
    for (int d = 1; d < 32; d <<= 1) {
        unsigned t = __shfl_up_sync(FULL, v, d);       // 取 lane − d 号线程的值
        if (lane >= d) v += t;
    }
    return v;
}

__global__ void scan_blocks(const unsigned* x, unsigned* y, unsigned* sums, int n) {
    __shared__ unsigned ws[B / 32];
    int i = blockIdx.x * B + threadIdx.x, lane = threadIdx.x % 32, warp = threadIdx.x / 32;
    unsigned v = warp_scan(i < n ? x[i] : 0u, lane);   // 每个线程只读写自己的 i，所以 x 与 y 可以是同一个数组
    if (lane == 31) ws[warp] = v;                      // 本线程束的和
    __syncthreads();
    if (warp == 0) ws[lane] = warp_scan(ws[lane], lane);
    __syncthreads();
    if (warp > 0) v += ws[warp - 1];                   // 加上前面各线程束的和
    if (i < n) y[i] = v;
    if (sums != nullptr && threadIdx.x == B - 1) sums[blockIdx.x] = v;
}

__global__ void add_offsets(unsigned* y, const unsigned* sums, int n) {
    int i = blockIdx.x * B + threadIdx.x;
    if (blockIdx.x > 0 && i < n) y[i] += sums[blockIdx.x - 1];
}

// y = x 的包含式前缀和；tmp 是存放各级块和的工作区（至少 n/1023 + 64 个数）
static void scan(const unsigned* x, unsigned* y, int n, unsigned* tmp) {
    int nb = (n + B - 1) / B;
    if (nb == 1) {
        scan_blocks<<<1, B>>>(x, y, nullptr, n);
        return;
    }
    scan_blocks<<<nb, B>>>(x, y, tmp, n);
    scan(tmp, tmp, nb, tmp + nb);                      // 就地扫描各块的和
    add_offsets<<<nb, B>>>(y, tmp, n);
}

int main() {
    const int n = 1 << 24;
    const size_t bytes = size_t(n) * 4;
    std::vector<unsigned> hx(n), hy(n), ref(n);
    unsigned run = 0;
    for (int i = 0; i < n; i++) {
        hx[i] = unsigned(splitmix64(i) % 4);
        ref[i] = run += hx[i];
    }
    unsigned *x, *y, *tmp;
    CHECK(cudaMalloc(&x, bytes));
    CHECK(cudaMalloc(&y, bytes));
    CHECK(cudaMalloc(&tmp, (n / 1023 + 64) * sizeof(unsigned)));
    CHECK(cudaMemcpy(x, hx.data(), bytes, cudaMemcpyHostToDevice));
    size_t cub_bytes = 0;
    CHECK(cub::DeviceScan::InclusiveSum(nullptr, cub_bytes, x, y, n));
    void* cub_tmp;
    CHECK(cudaMalloc(&cub_tmp, cub_bytes));

    CHECK(cudaMemset(y, 0xFF, bytes));
    float t_ours = time_ms([&] { scan(x, y, n, tmp); });
    CHECK(cudaMemcpy(hy.data(), y, bytes, cudaMemcpyDeviceToHost));
    bool ok = hy == ref;
    CHECK(cudaMemset(y, 0xFF, bytes));
    float t_cub = time_ms([&] { cub::DeviceScan::InclusiveSum(cub_tmp, cub_bytes, x, y, n); });
    CHECK(cudaMemcpy(hy.data(), y, bytes, cudaMemcpyDeviceToHost));
    ok = ok && hy == ref;
    const double gb = 2.0 * bytes / 1e9;              // 有效带宽：输入读一遍、输出写一遍
    std::printf("{\"n\": %d, \"ours_us\": %.1f, \"ours_GBs\": %.1f, \"cub_us\": %.1f, \"cub_GBs\": %.1f, \"correct\": %s}\n",
                n, t_ours * 1e3, gb / (t_ours * 1e-3), t_cub * 1e3, gb / (t_cub * 1e-3), ok ? "true" : "false");
    CHECK(cudaFree(x));
    CHECK(cudaFree(y));
    CHECK(cudaFree(tmp));
    CHECK(cudaFree(cub_tmp));
    return 0;
}
