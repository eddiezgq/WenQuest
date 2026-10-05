// hipcheck.h：HIP 调用的错误检查（与第 4 章的 check.cuh 对应，10.6 节）。
#pragma once
#include <cstdio>
#include <cstdlib>

#include <hip/hip_runtime.h>

// 主机侧怎样知道线程束（波前）有多少道：warpSize 是**设备侧**的内建变量，主机代码不能直接读它
// （HIP 的 hipDeviceProp_t 里也有一个 warpSize，但在某些实现上与设备侧看到的不一致）。
// 最稳妥的办法是让设备自己报：起一个线程把 warpSize 写回来。
__global__ void wq_warp_probe(int* out) {
    if (threadIdx.x == 0 && blockIdx.x == 0) *out = warpSize;
}

inline int warp_width() {
    int* d = nullptr;
    int h = 0;
    if (hipMalloc(&d, sizeof(int)) != hipSuccess) return 0;
    hipLaunchKernelGGL(wq_warp_probe, dim3(1), dim3(1), 0, 0, d);
    hipMemcpy(&h, d, sizeof(int), hipMemcpyDeviceToHost);
    hipFree(d);
    return h;
}

#define HIP_CHECK(call)                                                                \
    do {                                                                               \
        hipError_t err_ = (call);                                                      \
        if (err_ != hipSuccess) {                                                      \
            std::fprintf(stderr, "HIP 错误 %s:%d：%s\n", __FILE__, __LINE__,             \
                         hipGetErrorString(err_));                                     \
            std::exit(1);                                                              \
        }                                                                              \
    } while (0)
