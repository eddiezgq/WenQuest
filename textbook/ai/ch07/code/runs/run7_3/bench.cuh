// bench.cuh：第 5 章起各程序共用的计时与测试数据（每个实测文件夹各放一份）。
#pragma once
#include <algorithm>
#include <vector>
#include "check.cuh"

// 计时：先运行一次（预热，并检查错误），再运行 reps 次，取中位数，单位毫秒（4.1 节）。launch 是启动核函数的函数对象；
// 事件记在流 s 上，被测的操作也必须发在这个流里（6.2.1 节）。
template <typename F>
float time_ms(F launch, int reps = 20, cudaStream_t s = 0) {
    cudaEvent_t t0, t1;
    CHECK(cudaEventCreate(&t0));
    CHECK(cudaEventCreate(&t1));
    launch();
    CHECK_LAUNCH();
    std::vector<float> ms(reps);
    for (float& m : ms) {
        CHECK(cudaEventRecord(t0, s));
        launch();
        CHECK(cudaEventRecord(t1, s));
        CHECK(cudaEventSynchronize(t1));
        CHECK(cudaEventElapsedTime(&m, t0, t1));
    }
    CHECK(cudaGetLastError());
    CHECK(cudaEventDestroy(t0));
    CHECK(cudaEventDestroy(t1));
    std::sort(ms.begin(), ms.end());
    return ms[reps / 2];
}

// 第 i 个伪随机数（splitmix64），与书中 Python 程序 _ch5.splitmix64 逐位相同；主机与设备上都能用
__host__ __device__ inline unsigned long long splitmix64(unsigned long long i) {
    unsigned long long z = i * 0x9E3779B97F4A7C15ull + 0x9E3779B97F4A7C15ull;
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBull;
    return z ^ (z >> 31);
}
