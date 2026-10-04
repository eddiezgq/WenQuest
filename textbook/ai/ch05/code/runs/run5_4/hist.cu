// 程序 5.4.1：256 个箱的直方图，三种写法 × 三种输入（5.4 节）。
//   global：每个元素对全局内存做一次 atomicAdd（程序 4.8 节的写法）
//   shared：每个线程块先在共享内存里统计（私有化），最后把 256 个箱加到全局
//   warpagg：在 shared 的基础上，线程束内先用 __match_any_sync 找出落进同一个箱的线程，由其中编号最小的一个代表大家做一次原子加法
//   输入：rand 均匀随机的字节；cam 检测相机的灰度图（4 帧，与程序 4.2.1 的测试图相同）；const 全部是 128（争用最严重）
// 编译：nvcc -O3 -arch=native -o hist hist.cu
#include <cstdint>
#include <cstdio>
#include <cstring>
#include "bench.cuh"

constexpr int W = 3840, H = 2160, FRAMES = 4, N = W * H * FRAMES, BS = 256;

__global__ void h_global(const uint8_t* d, int n, unsigned* bins) {
    for (int i = blockIdx.x * blockDim.x + threadIdx.x; i < n; i += gridDim.x * blockDim.x) atomicAdd(&bins[d[i]], 1u);
}

__global__ void h_shared(const uint8_t* d, int n, unsigned* bins) {
    __shared__ unsigned s[256];
    for (int k = threadIdx.x; k < 256; k += blockDim.x) s[k] = 0;
    __syncthreads();
    for (int i = blockIdx.x * blockDim.x + threadIdx.x; i < n; i += gridDim.x * blockDim.x) atomicAdd(&s[d[i]], 1u);
    __syncthreads();
    for (int k = threadIdx.x; k < 256; k += blockDim.x)
        if (s[k]) atomicAdd(&bins[k], s[k]);
}

__global__ void h_warpagg(const uint8_t* d, int n, unsigned* bins) {
    __shared__ unsigned s[256];
    for (int k = threadIdx.x; k < 256; k += blockDim.x) s[k] = 0;
    __syncthreads();
    const int lane = threadIdx.x % 32;
    // 循环的边界按线程束对齐，保证 __match_any_sync 时整个线程束都在
    for (int base = blockIdx.x * blockDim.x + threadIdx.x - lane; base < n; base += gridDim.x * blockDim.x) {
        int i = base + lane;
        unsigned key = i < n ? d[i] : 0xFFFFFFFFu;                   // 越界的线程用一个不可能的箱号
        unsigned peers = __match_any_sync(0xFFFFFFFFu, key);         // 与我落进同一个箱的线程（32 位掩码）
        if (key != 0xFFFFFFFFu && lane == __ffs(peers) - 1) atomicAdd(&s[key], unsigned(__popc(peers)));
    }
    __syncthreads();
    for (int k = threadIdx.x; k < 256; k += blockDim.x)
        if (s[k]) atomicAdd(&bins[k], s[k]);
}

static uint8_t gray_px(int r, int c) {             // 与程序 4.2.1 相同的测试图与灰度公式
    bool spot = (r - 1000) * (r - 1000) + (c - 2000) * (c - 2000) < 60 * 60;
    float R = spot ? 20 : 120 + c % 100, G = spot ? 25 : 130 + r % 80, B = spot ? 30 : 140;
    return uint8_t(0.299f * R + 0.587f * G + 0.114f * B + 0.5f);
}

int main() {
    std::vector<uint8_t> h(N);
    const char* in_names[3] = {"rand", "cam", "const"};
    const char* k_names[3] = {"global", "shared", "warpagg"};
    using K = void (*)(const uint8_t*, int, unsigned*);
    K ks[3] = {h_global, h_shared, h_warpagg};
    int sms, fit;
    CHECK(cudaDeviceGetAttribute(&sms, cudaDevAttrMultiProcessorCount, 0));
    CHECK(cudaOccupancyMaxActiveBlocksPerMultiprocessor(&fit, h_warpagg, BS, 0));
    const int grid = sms * fit;                       // 网格跨步：线程块数取一波能同时驻留的个数
    uint8_t* d;
    unsigned* bins;
    CHECK(cudaMalloc(&d, N));
    CHECK(cudaMalloc(&bins, 256 * 4));
    bool ok = true;
    std::printf("{\"n\": %d", N);
    for (int in = 0; in < 3; in++) {
        for (int i = 0; i < N; i++) {
            int f = i % (W * H);
            h[i] = in == 0 ? uint8_t(splitmix64(i) % 256) : in == 1 ? gray_px(f / W, f % W) : 128;
        }
        unsigned ref[256] = {0}, got[256];
        for (int i = 0; i < N; i++) ref[h[i]]++;
        CHECK(cudaMemcpy(d, h.data(), N, cudaMemcpyHostToDevice));
        for (int k = 0; k < 3; k++) {
            float ms = time_ms([&] {
                CHECK(cudaMemsetAsync(bins, 0, 256 * 4));
                ks[k]<<<grid, BS>>>(d, N, bins);
            });
            CHECK(cudaMemcpy(got, bins, sizeof got, cudaMemcpyDeviceToHost));
            ok = ok && std::memcmp(got, ref, sizeof ref) == 0;
            std::printf(", \"%s_%s_us\": %.1f, \"%s_%s_GBs\": %.1f", in_names[in], k_names[k], ms * 1e3, in_names[in], k_names[k],
                        N / 1e9 / (ms * 1e-3));
        }
    }
    std::printf(", \"correct\": %s}\n", ok ? "true" : "false");
    CHECK(cudaFree(d));
    CHECK(cudaFree(bins));
    return 0;
}
