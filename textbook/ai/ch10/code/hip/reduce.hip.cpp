// 程序 10.6.2：第 5 章的归约移到 HIP——这一个要动手改（10.6 节）。
// code/runs/run5_2/reduce.cu 的 v5 版用 __shfl_down_sync(0xffffffffu, v, off) 做线程束内归约，循环从 off = 16 开始：
// 这两处都把“线程束 32 道”写进了代码。HIPIFY 只会把名字换成 __shfl_down（HIP 的洗牌不带掩码参数），
// 循环的起点仍是 16——在 64 道的波前上，每个波前只求出低 32 道与高 32 道各自的和，结果约为正确值的一半（算例 10.2.1）。
// 可移植的写法：循环起点取 warpSize / 2，暂存部分和的共享内存按 blockDim.x / warpSize 算。
// 下面两个核函数都在：wrong_v5 是照搬的错版（本程序验证它确实算错），portable 是改好的版本。
// 编译（ROCm）：hipcc -O3 -o reduce reduce.hip.cpp
// 编译（CPU，核对正确性）：g++ -std=c++17 -O2 -I<HIP-CPU>/include reduce.hip.cpp -o reduce -ltbb -lpthread
#include <cstdio>
#include <vector>

#include <hip/hip_runtime.h>

#include "hipcheck.h"

constexpr int B = 256;                      // 每个线程块的线程数
constexpr int MIN_WARP = 16;                // 我们愿意支持的最小波前宽度（32 与 64 都比它大）
constexpr int MAX_WAVES = B / MIN_WARP;     // 共享内存按最小宽度开，任何宽度都够用

// 照搬 CUDA 的写法：循环写死 16（= 32 / 2）
__global__ void wrong_v5(const float* x, float* out, int n) {
    __shared__ float sm[MAX_WAVES];
    float v = 0.0f;
    for (int i = blockIdx.x * blockDim.x + threadIdx.x; i < n; i += blockDim.x * gridDim.x) v += x[i];
    for (int off = 16; off > 0; off >>= 1) v += __shfl_down(v, off);          // ← 在 64 道上只归约了一半
    int lane = threadIdx.x % warpSize, wave = threadIdx.x / warpSize;
    if (lane == 0) sm[wave] = v;
    __syncthreads();
    if (threadIdx.x == 0) {
        float s = 0.0f;
        for (int i = 0; i < int((blockDim.x + warpSize - 1) / warpSize); i++) s += sm[i];
        out[blockIdx.x] = s;
    }
}

// 可移植的写法：起点由 warpSize 决定
__global__ void portable(const float* x, float* out, int n) {
    __shared__ float sm[MAX_WAVES];
    float v = 0.0f;
    for (int i = blockIdx.x * blockDim.x + threadIdx.x; i < n; i += blockDim.x * gridDim.x) v += x[i];
    for (int off = warpSize / 2; off > 0; off >>= 1) v += __shfl_down(v, off);
    int lane = threadIdx.x % warpSize, wave = threadIdx.x / warpSize;
    if (lane == 0) sm[wave] = v;
    __syncthreads();
    if (threadIdx.x == 0) {
        float s = 0.0f;
        for (int i = 0; i < int((blockDim.x + warpSize - 1) / warpSize); i++) s += sm[i];   // 线程数不是宽度的整数倍时也不丢
        out[blockIdx.x] = s;
    }
}

int main() {
    const int n = 1 << 20, G = 64;
    std::vector<float> hx(n, 1.0f), hp(G), hw(G);           // 全 1：和就是 n，错在哪里一目了然（算例 5.2.1 的检查法）
    float *x, *o;
    HIP_CHECK(hipMalloc(&x, n * sizeof(float)));
    HIP_CHECK(hipMalloc(&o, G * sizeof(float)));
    HIP_CHECK(hipMemcpy(x, hx.data(), n * sizeof(float), hipMemcpyHostToDevice));
    hipLaunchKernelGGL(portable, dim3(G), dim3(B), 0, 0, x, o, n);
    HIP_CHECK(hipGetLastError());
    HIP_CHECK(hipMemcpy(hp.data(), o, G * sizeof(float), hipMemcpyDeviceToHost));
    hipLaunchKernelGGL(wrong_v5, dim3(G), dim3(B), 0, 0, x, o, n);
    HIP_CHECK(hipGetLastError());
    HIP_CHECK(hipMemcpy(hw.data(), o, G * sizeof(float), hipMemcpyDeviceToHost));
    double sp = 0.0, sw = 0.0;
    for (int i = 0; i < G; i++) {
        sp += hp[i];
        sw += hw[i];
    }
    const int w = warp_width();
    const bool ok = sp == double(n);                        // 可移植版：精确等于 n
    const bool bug = sw < sp;                               // 错版：在 64 道上偏小（在 32 道上两者相同）
    const bool as_expected = (w == 64) ? bug : (sw == sp);  // 教学点本身也要被检查，不能悄悄失效
    std::printf("{\"n\": %d, \"warp\": %d, \"portable\": %.0f, \"wrong\": %.0f, \"ratio\": %.3f, \"correct\": %s}\n",
                n, w, sp, sw, sw / sp, (ok && as_expected) ? "true" : "false");
    HIP_CHECK(hipFree(x));
    HIP_CHECK(hipFree(o));
    if (!as_expected) std::fprintf(stderr, "错版在 %d 道上的表现与预期不符（宽度 64 时应偏小、32 时应相同）\n", w);
    return (ok && as_expected) ? 0 : 1;
}
