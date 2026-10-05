// 程序 10.6.3：第 5 章的分块矩阵乘法移到 HIP（10.6 节）。来自 code/runs/run5_7/gemm.cu 的 tiled 版（程序 5.7.1），
// 32×32 的共享内存分块。这个核函数里没有线程束级指令、没有写死的 32 道假设（32×32 的线程块在 32 道上是 32 个线程束、
// 在 64 道上是 16 个波前，都排得下），HIPIFY 转换后不用改一个字——算例 10.4.1 里“一处要人改的地方都没有”的那一类。
// 寄存器分块与张量核心的版本就不同了：前者要按 64 道重排线程与数据（习题 10.6.3），后者的 WMMA 要换成 rocWMMA（10.2 节）。
// 编译（ROCm）：hipcc -O3 -o gemm gemm.hip.cpp
// 编译（CPU，核对正确性）：g++ -std=c++17 -O2 -I<HIP-CPU>/include gemm.hip.cpp -o gemm -ltbb -lpthread
#include <cstdio>
#include <vector>

#include <hip/hip_runtime.h>

#include "hipcheck.h"

constexpr int T = 32;

__global__ void tiled(int M, int N, int K, const float* A, const float* B, float* C) {
    __shared__ float As[T][T], Bs[T][T];
    int tx = threadIdx.x, ty = threadIdx.y;
    int row = blockIdx.y * T + ty, col = blockIdx.x * T + tx;
    float s = 0.0f;
    for (int k0 = 0; k0 < K; k0 += T) {
        As[ty][tx] = A[row * K + k0 + tx];
        Bs[ty][tx] = B[(k0 + ty) * N + col];
        __syncthreads();
        for (int k = 0; k < T; k++) s += As[ty][k] * Bs[k][tx];
        __syncthreads();
    }
    C[row * N + col] = s;
}

int main() {
    const int n = 256;                                  // CPU 上核对用小矩阵；GPU 上实测用 4096（run5_7）
    std::vector<float> hA(n * n), hB(n * n), hC(n * n), ref(n * n);
    for (int i = 0; i < n * n; i++) {                   // −2 到 2 的整数：结果精确，可逐个比较（程序 5.7.1 的做法）
        hA[i] = float((i * 7919ll) % 5 - 2);        // 用 64 位中间值，避免乘法溢出
        hB[i] = float((i * 104729ll) % 5 - 2);
    }
    for (int r = 0; r < n; r++)
        for (int c = 0; c < n; c++) {
            float s = 0.0f;
            for (int k = 0; k < n; k++) s += hA[r * n + k] * hB[k * n + c];
            ref[r * n + c] = s;
        }
    float *A, *B, *C;
    HIP_CHECK(hipMalloc(&A, hA.size() * 4));
    HIP_CHECK(hipMalloc(&B, hB.size() * 4));
    HIP_CHECK(hipMalloc(&C, hC.size() * 4));
    HIP_CHECK(hipMemcpy(A, hA.data(), hA.size() * 4, hipMemcpyHostToDevice));
    HIP_CHECK(hipMemcpy(B, hB.data(), hB.size() * 4, hipMemcpyHostToDevice));
    hipLaunchKernelGGL(tiled, dim3(n / T, n / T), dim3(T, T), 0, 0, n, n, n, A, B, C);
    HIP_CHECK(hipGetLastError());
    HIP_CHECK(hipMemcpy(hC.data(), C, hC.size() * 4, hipMemcpyDeviceToHost));
    bool ok = true;
    for (int i = 0; i < n * n; i++) ok = ok && hC[i] == ref[i];
    const int w = warp_width();
    std::printf("{\"n\": %d, \"warp\": %d, \"waves_per_block\": %d, \"correct\": %s}\n",
                n, w, w ? T * T / w : 0, ok ? "true" : "false");
    HIP_CHECK(hipFree(A));
    HIP_CHECK(hipFree(B));
    HIP_CHECK(hipFree(C));
    return ok ? 0 : 1;
}
