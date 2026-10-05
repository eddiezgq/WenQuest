// 程序 6.3.1：GPU 之间的点对点带宽（6.3 节）。对每一对 GPU (i, j)：打开点对点访问，把 i 上的 256 MiB 复制到 j，测带宽；
// 另测 0 与 1 两个方向同时复制的双向带宽，以及不用点对点、经主机内存中转（GPU 0 → 锁页内存 → GPU 1）的带宽。
// 注意：某一对 GPU 不允许点对点时，cudaMemcpyPeerAsync 会自动经主机中转，测到的就不是点对点带宽（输出 all_peer 标明）。
// 编译：nvcc -O3 -o p2p p2p.cu
#include <algorithm>
#include <chrono>
#include <cstdio>
#include <vector>
#include "check.cuh"

constexpr size_t BYTES = size_t(256) << 20;

template <typename F>
static double median_ms(F fn, int reps = 5) {
    fn();
    std::vector<double> v(reps);
    for (double& x : v) {
        auto a = std::chrono::steady_clock::now();
        fn();
        x = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - a).count();
    }
    std::sort(v.begin(), v.end());
    return v[reps / 2];
}

int main() {
    int n;
    CHECK(cudaGetDeviceCount(&n));
    std::vector<void*> buf(n), buf2(n);
    std::vector<cudaStream_t> st(n);
    bool all_peer = true;
    for (int i = 0; i < n; i++) {
        CHECK(cudaSetDevice(i));
        CHECK(cudaMalloc(&buf[i], BYTES));
        CHECK(cudaMalloc(&buf2[i], BYTES));
        CHECK(cudaMemset(buf[i], i + 1, BYTES));
        CHECK(cudaStreamCreate(&st[i]));
        for (int j = 0; j < n; j++) {
            if (j == i) continue;
            int can;
            CHECK(cudaDeviceCanAccessPeer(&can, i, j));
            if (can) CHECK(cudaDeviceEnablePeerAccess(j, 0));   // 打开以后，i 上的核函数也能直接读写 j 的显存
            all_peer = all_peer && can;
        }
    }
    double gmin = 1e30, gmax = 0, g01 = 0, sum = 0;
    bool pair_ok = true;
    int pairs = 0;
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++) {
            if (i == j) continue;
            CHECK(cudaSetDevice(i));
            double ms = median_ms([&] {
                CHECK(cudaMemcpyPeerAsync(buf2[j], j, buf[i], i, BYTES, st[i]));
                CHECK(cudaStreamSynchronize(st[i]));
            });
            unsigned char edge[2];                                // 核对：收到的首尾两个字节都是 i 的数据（i + 1）
            CHECK(cudaMemcpy(edge, buf2[j], 1, cudaMemcpyDeviceToHost));
            CHECK(cudaMemcpy(edge + 1, (char*)buf2[j] + BYTES - 1, 1, cudaMemcpyDeviceToHost));
            pair_ok = pair_ok && edge[0] == i + 1 && edge[1] == i + 1;
            double gbs = BYTES / 1e9 / (ms * 1e-3);
            gmin = std::min(gmin, gbs), gmax = std::max(gmax, gbs), sum += gbs, pairs++;
            if (i == 0 && j == 1) g01 = gbs;
        }
    double bidir = 0, staged = 0;
    if (n >= 2) {
        double ms = median_ms([&] {                             // 0→1 与 1→0 同时进行
            CHECK(cudaSetDevice(0));
            CHECK(cudaMemcpyPeerAsync(buf2[1], 1, buf[0], 0, BYTES, st[0]));
            CHECK(cudaSetDevice(1));
            CHECK(cudaMemcpyPeerAsync(buf2[0], 0, buf[1], 1, BYTES, st[1]));
            CHECK(cudaStreamSynchronize(st[1]));
            CHECK(cudaSetDevice(0));
            CHECK(cudaStreamSynchronize(st[0]));
        });
        bidir = 2 * BYTES / 1e9 / (ms * 1e-3);
        void* host;
        CHECK(cudaMallocHost(&host, BYTES));
        ms = median_ms([&] {                                    // 经主机中转
            CHECK(cudaSetDevice(0));
            CHECK(cudaMemcpy(host, buf[0], BYTES, cudaMemcpyDeviceToHost));
            CHECK(cudaSetDevice(1));
            CHECK(cudaMemcpy(buf2[1], host, BYTES, cudaMemcpyHostToDevice));
        });
        staged = BYTES / 1e9 / (ms * 1e-3);
        CHECK(cudaFreeHost(host));
    }
    // 核对：GPU 1 上收到的是 GPU 0 的数据（每个字节都是 1）
    std::vector<unsigned char> h(4096);
    CHECK(cudaSetDevice(1));
    CHECK(cudaMemcpy(h.data(), buf2[1], h.size(), cudaMemcpyDeviceToHost));
    bool ok = n >= 2 && pair_ok && std::all_of(h.begin(), h.end(), [](unsigned char c) { return c == 1; });
    std::printf("{\"n_gpus\": %d, \"all_peer\": %d, \"p2p_01_GBs\": %.1f, \"p2p_min_GBs\": %.1f, \"p2p_max_GBs\": %.1f, "
                "\"p2p_mean_GBs\": %.1f, \"bidir_01_GBs\": %.1f, \"staged_GBs\": %.1f, \"correct\": %s}\n",
                n, int(all_peer), g01, gmin, gmax, pairs ? sum / pairs : 0.0, bidir, staged, ok ? "true" : "false");
    return 0;
}
