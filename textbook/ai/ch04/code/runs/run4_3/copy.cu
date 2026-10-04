// 程序 4.3.2：主机与设备之间的传输带宽——可分页内存与锁页内存，主机到设备与设备到主机（4.3 节）。
// 编译：nvcc -O3 -arch=native -o copy copy.cu
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include "check.cuh"

// 把 bytes 字节从 src 拷到 dst，重复 10 次取中位数，返回 GB/s
static double rate(void* dst, const void* src, size_t bytes, cudaMemcpyKind kind) {
    cudaEvent_t t0, t1;
    CHECK(cudaEventCreate(&t0));
    CHECK(cudaEventCreate(&t1));
    CHECK(cudaMemcpy(dst, src, bytes, kind));                    // 预热
    std::vector<float> ms(10);
    for (float& m : ms) {
        CHECK(cudaEventRecord(t0));
        CHECK(cudaMemcpy(dst, src, bytes, kind));
        CHECK(cudaEventRecord(t1));
        CHECK(cudaEventSynchronize(t1));
        CHECK(cudaEventElapsedTime(&m, t0, t1));
    }
    std::sort(ms.begin(), ms.end());
    CHECK(cudaEventDestroy(t0));
    CHECK(cudaEventDestroy(t1));
    return bytes / (ms[ms.size() / 2] * 1e-3) / 1e9;
}

int main() {
    const size_t bytes = size_t(256) << 20;                       // 256 MiB
    void* pageable = std::malloc(bytes);                         // 普通的（可分页）主机内存
    void* pinned;
    CHECK(cudaMallocHost(&pinned, bytes));                       // 锁页内存：GPU 可以直接用 DMA 读写
    void* dev;
    CHECK(cudaMalloc(&dev, bytes));
    std::fill((char*)pageable, (char*)pageable + bytes, 1);
    std::fill((char*)pinned, (char*)pinned + bytes, 1);
    int d;
    cudaDeviceProp prop;
    CHECK(cudaGetDevice(&d));
    CHECK(cudaGetDeviceProperties(&prop, d));
    std::printf("{\"h2d_pageable\": %.1f, \"h2d_pinned\": %.1f, \"d2h_pageable\": %.1f, \"d2h_pinned\": %.1f, \"device\": \"%s\"}\n",
                rate(dev, pageable, bytes, cudaMemcpyHostToDevice), rate(dev, pinned, bytes, cudaMemcpyHostToDevice),
                rate(pageable, dev, bytes, cudaMemcpyDeviceToHost), rate(pinned, dev, bytes, cudaMemcpyDeviceToHost),
                prop.name);
    CHECK(cudaFree(dev));
    CHECK(cudaFreeHost(pinned));
    std::free(pageable);
    return 0;
}
