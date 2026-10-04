// 程序 4.1.1：向量加法 c = a + b。第一个核函数：每个线程算一个元素（4.1、4.2 节）。
// 编译：nvcc -O3 -arch=native -o vadd vadd.cu        运行：./vadd [n]
// 输出一行 JSON：核函数耗时（20 次的中位数）、有效带宽、与 CPU 结果的最大误差
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include "check.cuh"

__global__ void vadd(const float* a, const float* b, float* c, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;   // 式 (4.2.1)：这个线程负责的元素
    if (i < n) c[i] = a[i] + b[i];                   // 最后一个线程块可能有多余的线程，越界的不做
}

int main(int argc, char** argv) {
    const int n = argc > 1 ? std::atoi(argv[1]) : (1 << 26);   // 默认 2^26 个，每个数组 256 MiB
    const size_t bytes = size_t(n) * sizeof(float);
    std::vector<float> ha(n), hb(n), hc(n);
    for (int i = 0; i < n; i++) { ha[i] = float(i % 1000) * 0.5f; hb[i] = float(i % 7) - 3.0f; }

    float *da, *db, *dc;                                             // 设备（显存）上的三个数组
    CHECK(cudaMalloc(&da, bytes));
    CHECK(cudaMalloc(&db, bytes));
    CHECK(cudaMalloc(&dc, bytes));
    CHECK(cudaMemcpy(da, ha.data(), bytes, cudaMemcpyHostToDevice));
    CHECK(cudaMemcpy(db, hb.data(), bytes, cudaMemcpyHostToDevice));

    const int block = 256;
    const int grid = (n + block - 1) / block;                        // 式 (4.2.2)：向上取整
    cudaEvent_t t0, t1;
    CHECK(cudaEventCreate(&t0));
    CHECK(cudaEventCreate(&t1));
    vadd<<<grid, block>>>(da, db, dc, n);                            // 预热一次
    CHECK_LAUNCH();
    std::vector<float> ms(20);
    for (float& m : ms) {
        CHECK(cudaEventRecord(t0));
        vadd<<<grid, block>>>(da, db, dc, n);
        CHECK(cudaEventRecord(t1));
        CHECK(cudaEventSynchronize(t1));
        CHECK(cudaEventElapsedTime(&m, t0, t1));
    }
    CHECK(cudaGetLastError());
    std::sort(ms.begin(), ms.end());
    const float t = ms[ms.size() / 2];

    CHECK(cudaMemcpy(hc.data(), dc, bytes, cudaMemcpyDeviceToHost));
    float err = 0.0f;
    for (int i = 0; i < n; i++) err = std::max(err, std::abs(hc[i] - (ha[i] + hb[i])));
    std::printf("{\"vadd_n\": %d, \"vadd_ms\": %.4f, \"vadd_GBs\": %.1f, \"vadd_err\": %g}\n",
                n, t, 3.0 * bytes / (t * 1e-3) / 1e9, err);
    CHECK(cudaFree(da));
    CHECK(cudaFree(db));
    CHECK(cudaFree(dc));
    return 0;
}
