// 程序 10.6.1：第 4 章的向量加法移到 HIP（10.6 节）。由 hipify-perl 从 code/runs/run4_1/vadd.cu 转换而来，
// 转换只改了名字：cudaMalloc → hipMalloc、cudaMemcpy → hipMemcpy、cuda_runtime.h → hip/hip_runtime.h……
// 核函数一个字没改。本书的 HIP 程序一律用 hipLaunchKernelGGL(核函数, 网格, 线程块, 共享内存, 流, 参数...)
// 而不是 <<<>>>：两种写法在 ROCm 上等价，但只有前者能用 AMD 开源的 HIP-CPU 在没有显卡的机器上编译运行（10.6.3 节）。
// 编译（ROCm）：hipcc -O3 -o vadd vadd.hip.cpp
// 编译（CPU，核对正确性）：g++ -std=c++17 -O2 -I<HIP-CPU>/include vadd.hip.cpp -o vadd -ltbb -lpthread
#include <cstdio>
#include <vector>

#include <hip/hip_runtime.h>

#include "hipcheck.h"

__global__ void vadd(const float* a, const float* b, float* c, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) c[i] = a[i] + b[i];
}

int main() {
    const int n = 1 << 20, B = 256;
    std::vector<float> ha(n), hb(n), hc(n);
    for (int i = 0; i < n; i++) {
        ha[i] = float(i % 1000);
        hb[i] = float((i * 7) % 1000);
    }
    float *a, *b, *c;
    HIP_CHECK(hipMalloc(&a, n * sizeof(float)));
    HIP_CHECK(hipMalloc(&b, n * sizeof(float)));
    HIP_CHECK(hipMalloc(&c, n * sizeof(float)));
    HIP_CHECK(hipMemcpy(a, ha.data(), n * sizeof(float), hipMemcpyHostToDevice));
    HIP_CHECK(hipMemcpy(b, hb.data(), n * sizeof(float), hipMemcpyHostToDevice));
    hipLaunchKernelGGL(vadd, dim3((n + B - 1) / B), dim3(B), 0, 0, a, b, c, n);
    HIP_CHECK(hipGetLastError());
    HIP_CHECK(hipMemcpy(hc.data(), c, n * sizeof(float), hipMemcpyDeviceToHost));
    bool ok = true;
    for (int i = 0; i < n; i++) ok = ok && hc[i] == ha[i] + hb[i];
    std::printf("{\"n\": %d, \"warp\": %d, \"correct\": %s}\n", n, warp_width(), ok ? "true" : "false");
    HIP_CHECK(hipFree(a));
    HIP_CHECK(hipFree(b));
    HIP_CHECK(hipFree(c));
    return ok ? 0 : 1;
}
