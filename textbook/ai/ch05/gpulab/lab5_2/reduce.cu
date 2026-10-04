// 程序 5.2.1：归约的五个版本（5.2 节）。对 n = 2^25 个单精度数求和。
//   v1 交错寻址：tid % (2s) == 0 的线程工作——同一线程束内一半、四分之三……的线程空转（线程束分化）
//   v2 交错寻址、连续的线程工作：k = 2·s·tid——不再分化，但共享内存跨步 2s 访问，有存储体冲突
//   v3 顺序寻址：前 s 个线程加上后 s 个——没有分化，也没有冲突
//   v4 网格跨步：只启动“SM 数 × 每个 SM 能同时驻留的线程块数”个线程块（A10 上 72 × 6），每个线程先在寄存器里加许多个数，再做 v3 的树形归约
//   v5 线程束洗牌：v4 的基础上，线程束内用 __shfl_down_sync 求和，每个线程束只写一次共享内存
//   参照：CUB 的 cub::DeviceReduce::Sum。
// v1–v3 每个线程先读一个数，得到 ⌈n/256⌉ 个部分和；v4、v5 得到“SM 数 × 每个 SM 的线程块数”个部分和。部分和都再用 v5 的核函数
// （一个线程块）加起来，计时包括这两次启动。另用全 1 的输入（n = 2^24 − 3，不是 256 的倍数）检查每个版本的和精确等于 n。
// 编译：nvcc -O3 -arch=native -o reduce reduce.cu；运行：./reduce [每个 SM 的线程块数，默认按占用率算出能同时驻留的个数]
#include <cmath>
#include <cstdlib>
#include <cstdio>
#include <cub/cub.cuh>
#include "bench.cuh"

constexpr int B = 256;                       // 每个线程块的线程数

__global__ void v1(const float* x, float* part, int n) {
    __shared__ float sm[B];
    int tid = threadIdx.x, i = blockIdx.x * B + tid;
    sm[tid] = i < n ? x[i] : 0.0f;
    __syncthreads();
    for (int s = 1; s < B; s *= 2) {
        if (tid % (2 * s) == 0) sm[tid] += sm[tid + s];
        __syncthreads();
    }
    if (tid == 0) part[blockIdx.x] = sm[0];
}

__global__ void v2(const float* x, float* part, int n) {
    __shared__ float sm[B];
    int tid = threadIdx.x, i = blockIdx.x * B + tid;
    sm[tid] = i < n ? x[i] : 0.0f;
    __syncthreads();
    for (int s = 1; s < B; s *= 2) {
        int k = 2 * s * tid;
        if (k < B) sm[k] += sm[k + s];
        __syncthreads();
    }
    if (tid == 0) part[blockIdx.x] = sm[0];
}

__device__ __forceinline__ float block_tree(float v, float* sm) {        // v3 的树形归约（共享内存 sm 有 B 个数）
    int tid = threadIdx.x;
    sm[tid] = v;
    __syncthreads();
    for (int s = B / 2; s > 0; s >>= 1) {
        if (tid < s) sm[tid] += sm[tid + s];
        __syncthreads();
    }
    return sm[0];
}

__global__ void v3(const float* x, float* part, int n) {
    __shared__ float sm[B];
    int i = blockIdx.x * B + threadIdx.x;
    float s = block_tree(i < n ? x[i] : 0.0f, sm);
    if (threadIdx.x == 0) part[blockIdx.x] = s;
}

__device__ __forceinline__ float grid_sum(const float* x, int n) {     // 网格跨步：每个线程先在寄存器里累加
    float s = 0.0f;
    for (int i = blockIdx.x * B + threadIdx.x; i < n; i += gridDim.x * B) s += x[i];
    return s;
}

__global__ void v4(const float* x, float* part, int n) {
    __shared__ float sm[B];
    float s = block_tree(grid_sum(x, n), sm);
    if (threadIdx.x == 0) part[blockIdx.x] = s;
}

__device__ __forceinline__ float warp_sum(float v) {                   // 线程束内：5 次洗牌，0 号线程得到 32 个数的和
    for (int off = 16; off > 0; off >>= 1) v += __shfl_down_sync(0xffffffffu, v, off);
    return v;
}

__global__ void v5(const float* x, float* part, int n) {
    __shared__ float sm[B / 32];
    int lane = threadIdx.x % 32, warp = threadIdx.x / 32;
    float s = warp_sum(grid_sum(x, n));
    if (lane == 0) sm[warp] = s;
    __syncthreads();
    if (warp == 0) {
        s = warp_sum(lane < B / 32 ? sm[lane] : 0.0f);
        if (lane == 0) part[blockIdx.x] = s;
    }
}

int main(int argc, char** argv) {
    const int n = 1 << 25;
    std::vector<float> hx(n);
    double ref = 0.0;
    for (int i = 0; i < n; i++) ref += hx[i] = float(splitmix64(i) % 1000) / 1000.0f;
    int sms, fit;
    CHECK(cudaDeviceGetAttribute(&sms, cudaDevAttrMultiProcessorCount, 0));
    CHECK(cudaOccupancyMaxActiveBlocksPerMultiprocessor(&fit, v5, B, 0));      // 每个 SM 能同时驻留几个线程块
    const int per_sm = argc > 1 ? std::atoi(argv[1]) : fit;
    const int gmany = (n + B - 1) / B, gfew = std::min(std::max(sms * per_sm, 1), gmany);
    float *x, *part, *sum;
    CHECK(cudaMalloc(&x, size_t(n) * 4));
    CHECK(cudaMalloc(&part, size_t(gmany) * 4));
    CHECK(cudaMalloc(&sum, 4));
    CHECK(cudaMemcpy(x, hx.data(), size_t(n) * 4, cudaMemcpyHostToDevice));
    size_t tmp_bytes = 0;
    CHECK(cub::DeviceReduce::Sum(nullptr, tmp_bytes, x, sum, n));
    void* tmp;
    CHECK(cudaMalloc(&tmp, tmp_bytes));

    using K = void (*)(const float*, float*, int);
    K ks[5] = {v1, v2, v3, v4, v5};
    float ms[6];
    bool ok = true;
    double rel[6];
    for (int v = 0; v < 6; v++) {
        int g = v < 3 ? gmany : gfew;
        auto launch = [&] {
            if (v < 5) {
                ks[v]<<<g, B>>>(x, part, n);
                v5<<<1, B>>>(part, sum, g);
            } else {
                cub::DeviceReduce::Sum(tmp, tmp_bytes, x, sum, n);
            }
        };
        CHECK(cudaMemset(sum, 0xFF, 4));
        ms[v] = time_ms(launch);
        float h;
        CHECK(cudaMemcpy(&h, sum, 4, cudaMemcpyDeviceToHost));
        rel[v] = std::fabs(h - ref) / ref;
        ok = ok && rel[v] < 1e-4;
    }
    // 精确性检查：全 1 的输入，长度不是 256 的倍数；2^24 以内的整数单精度精确表示，每个版本的和都应当恰好是 n1
    const int n1 = (1 << 24) - 3;
    std::vector<float> ones(n1, 1.0f);
    CHECK(cudaMemcpy(x, ones.data(), size_t(n1) * 4, cudaMemcpyHostToDevice));
    for (int v = 0; v < 6; v++) {
        int g = v < 3 ? (n1 + B - 1) / B : std::min(gfew, (n1 + B - 1) / B);
        if (v < 5) {
            ks[v]<<<g, B>>>(x, part, n1);
            v5<<<1, B>>>(part, sum, g);
        } else {
            CHECK(cub::DeviceReduce::Sum(tmp, tmp_bytes, x, sum, n1));
        }
        CHECK_LAUNCH();
        float h;
        CHECK(cudaMemcpy(&h, sum, 4, cudaMemcpyDeviceToHost));
        if (h != float(n1)) {
            std::fprintf(stderr, "版本 %d：全 1 输入的和是 %.0f，应为 %d\n", v + 1, h, n1);
            ok = false;
        }
    }
    const double gb = double(n) * 4 / 1e9;
    std::printf("{\"n\": %d, \"sms\": %d, \"per_sm\": %d, \"fit\": %d", n, sms, per_sm, fit);
    const char* names[6] = {"v1", "v2", "v3", "v4", "v5", "cub"};
    for (int v = 0; v < 6; v++) std::printf(", \"%s_us\": %.1f, \"%s_GBs\": %.1f", names[v], ms[v] * 1e3, names[v], gb / (ms[v] * 1e-3));
    std::printf(", \"max_rel_err\": %.2e, \"correct\": %s}\n", *std::max_element(rel, rel + 6), ok ? "true" : "false");
    CHECK(cudaFree(x));
    CHECK(cudaFree(part));
    CHECK(cudaFree(sum));
    CHECK(cudaFree(tmp));
    return 0;
}
