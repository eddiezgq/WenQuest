// 程序 6.4.1：用 NCCL 做全归约（6.4 节）。一个进程管 p 块 GPU（p = 2、4、8），每块 GPU 有一个长 count 的单精度数组，
// 全归约后每块 GPU 上都是 p 个数组之和。消息从 8 KiB 到 1 GiB，测耗时，算出算法带宽与总线带宽：
//   算法带宽 algbw = 消息字节数 / 耗时；总线带宽 busbw = algbw × 2(p − 1)/p（与 nccl-tests 的定义相同，可与链路带宽直接比较）。
// 编译：nvcc -O3 -arch=native -o allreduce allreduce.cu -lnccl
#include <algorithm>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <nccl.h>
#include "check.cuh"

#define CHECK_NCCL(call)                                                              \
    do {                                                                              \
        ncclResult_t r_ = (call);                                                     \
        if (r_ != ncclSuccess) {                                                      \
            std::fprintf(stderr, "NCCL 错误 %s:%d：%s\n", __FILE__, __LINE__, ncclGetErrorString(r_)); \
            std::exit(1);                                                             \
        }                                                                             \
    } while (0)

__global__ void fill(float* x, size_t n, float v) {
    for (size_t i = blockIdx.x * size_t(blockDim.x) + threadIdx.x; i < n; i += size_t(gridDim.x) * blockDim.x) x[i] = v;
}

int main() {
    int n;
    CHECK(cudaGetDeviceCount(&n));
    const int NSZ = 5;
    const size_t sizes[NSZ] = {size_t(8) << 10, size_t(64) << 10, size_t(1) << 20, size_t(64) << 20, size_t(1) << 30};
    const char* labels[NSZ] = {"8K", "64K", "1M", "64M", "1G"};
    const size_t maxc = sizes[NSZ - 1] / sizeof(float);
    bool ok = true;
    std::printf("{\"n_gpus\": %d", n);
    for (int p = 2; p <= n && p <= 8; p *= 2) {
        std::vector<int> devs(p);
        std::vector<ncclComm_t> comms(p);
        std::vector<float*> send(p), recv(p);
        std::vector<cudaStream_t> st(p);
        for (int r = 0; r < p; r++) {
            devs[r] = r;
            CHECK(cudaSetDevice(r));
            CHECK(cudaMalloc(&send[r], maxc * sizeof(float)));
            CHECK(cudaMalloc(&recv[r], maxc * sizeof(float)));
            CHECK(cudaStreamCreate(&st[r]));
            fill<<<1024, 256, 0, st[r]>>>(send[r], maxc, float(r + 1));   // 第 r 块 GPU 上全是 r + 1
            CHECK(cudaGetLastError());
        }
        CHECK_NCCL(ncclCommInitAll(comms.data(), p, devs.data()));
        // 连续发出 times 次全归约，最后才同步一次（与 nccl-tests 相同），免得每次同步的主机开销计入小消息的耗时
        auto allreduce = [&](size_t count, int times) {
            for (int t = 0; t < times; t++) {
                CHECK_NCCL(ncclGroupStart());                               // 一个进程管多块 GPU 时，把各块的调用包成一组
                for (int r = 0; r < p; r++) CHECK_NCCL(ncclAllReduce(send[r], recv[r], count, ncclFloat, ncclSum, comms[r], st[r]));
                CHECK_NCCL(ncclGroupEnd());
            }
            for (int r = 0; r < p; r++) {
                CHECK(cudaSetDevice(r));
                CHECK(cudaStreamSynchronize(st[r]));
            }
        };
        for (int k = 0; k < NSZ; k++) {
            const size_t count = sizes[k] / sizeof(float);
            const int times = k < 3 ? 100 : k < 4 ? 20 : 5;
            allreduce(count, 3);                                            // 预热（第一次要建立通信通道）
            std::vector<double> v(5);
            for (double& x : v) {
                auto a = std::chrono::steady_clock::now();
                allreduce(count, times);
                x = std::chrono::duration<double, std::micro>(std::chrono::steady_clock::now() - a).count() / times;
            }
            std::sort(v.begin(), v.end());
            const double us = v[2], algbw = sizes[k] / 1e3 / us;           // GB/s
            std::printf(", \"p%d_%s_us\": %.1f, \"p%d_%s_busbw\": %.1f", p, labels[k], us, p, labels[k], algbw * 2.0 * (p - 1) / p);
            float h[8];
            CHECK(cudaSetDevice(p - 1));
            CHECK(cudaMemcpy(h, recv[p - 1] + count - 4, 4 * sizeof(float), cudaMemcpyDeviceToHost));   // 最后一块 GPU 的末尾
            CHECK(cudaSetDevice(0));
            CHECK(cudaMemcpy(h + 4, recv[0], 4 * sizeof(float), cudaMemcpyDeviceToHost));               // 0 号 GPU 的开头
            for (float x : h) ok = ok && x == float(p * (p + 1) / 2);         // 1 + 2 + … + p
        }
        for (int r = 0; r < p; r++) {
            CHECK_NCCL(ncclCommDestroy(comms[r]));
            CHECK(cudaSetDevice(r));
            CHECK(cudaFree(send[r]));
            CHECK(cudaFree(recv[r]));
            CHECK(cudaStreamDestroy(st[r]));
        }
    }
    std::printf(", \"correct\": %s}\n", ok ? "true" : "false");
    return 0;
}
