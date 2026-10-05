// check.cuh：CUDA 调用的错误检查（4.4 节）。几乎每个 CUDA 程序都用它。
#pragma once
#include <cstdio>
#include <cstdlib>
#include <cuda_runtime.h>

// 每个 CUDA 运行时调用都返回 cudaError_t；出错时打印文件、行号和错误说明，然后退出
#define CHECK(call)                                                                  \
    do {                                                                             \
        cudaError_t err_ = (call);                                                   \
        if (err_ != cudaSuccess) {                                                   \
            std::fprintf(stderr, "CUDA 错误 %s:%d：%s（%s）\n", __FILE__, __LINE__,      \
                         cudaGetErrorString(err_), cudaGetErrorName(err_));          \
            std::exit(1);                                                            \
        }                                                                            \
    } while (0)

// 核函数的启动本身不返回错误：启动后立刻查一次（配置错误），需要时再同步查一次（执行中的错误）
#define CHECK_LAUNCH()                                                               \
    do {                                                                             \
        CHECK(cudaGetLastError());                                                   \
        CHECK(cudaDeviceSynchronize());                                              \
    } while (0)
