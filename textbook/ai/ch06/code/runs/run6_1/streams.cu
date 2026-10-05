// 程序 6.1.1：用三个流让传输与计算重叠（6.1 节）。检测相机的 12 帧 3840×2160 彩色图像（锁页内存）依次：上传 → 处理 → 灰度结果传回。
//   处理：灰度化，再做 iters 轮乘加（代替更复杂的处理，例如第 11 章的缺陷检测网络）；iters 在运行时调到使处理时间与上传时间相当
//         （输出中的 k_over_h 是两者之比，应接近 1）。
//   serial ：只用一个流，每帧三步依次完成
//   streams：三个流，第 f 帧放进第 f % 3 个流（各有自己的显存缓冲区），不同帧的上传、处理、传回可以同时进行
// 另外分别测出一帧的上传、处理、传回各要多久，以及 GPU 有几个复制引擎（asyncEngineCount）。
// 编译：nvcc -O3 -arch=native -o streams streams.cu
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <chrono>
#include <cstring>
#include "bench.cuh"

constexpr int W = 3840, H = 2160, PX = W * H, F = 12, NS = 3;

__global__ void process(const uint8_t* rgb, uint8_t* out, int n, int iters) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n) return;
    float v = fmaf(0.114f, float(rgb[3 * i + 2]), fmaf(0.587f, float(rgb[3 * i + 1]), 0.299f * float(rgb[3 * i])));
    for (int k = 0; k < iters; k++) v = fmaf(v, 0.999f, 0.1f);          // 有依赖的乘加链，编译器不能省掉
    out[i] = uint8_t(fminf(v + 0.5f, 255.0f));
}

static uint8_t ref_px(const uint8_t* rgb, int iters) {               // 与核函数逐位相同的主机计算
    float v = std::fmaf(0.114f, float(rgb[2]), std::fmaf(0.587f, float(rgb[1]), 0.299f * float(rgb[0])));
    for (int k = 0; k < iters; k++) v = std::fmaf(v, 0.999f, 0.1f);
    return uint8_t(std::fmin(v + 0.5f, 255.0f));
}

int main() {
    const size_t rgb_b = size_t(PX) * 3, gray_b = PX;
    uint8_t *h_rgb, *h_out, *h_out2;
    CHECK(cudaMallocHost(&h_rgb, rgb_b * F));                         // 锁页内存：异步传输的前提（4.3 节）
    CHECK(cudaMallocHost(&h_out, gray_b * F));
    CHECK(cudaMallocHost(&h_out2, gray_b * F));
    for (int f = 0; f < F; f++)
        for (int r = 0; r < H; r++)
            for (int c = 0; c < W; c++) {
                uint8_t* p = h_rgb + rgb_b * f + (size_t(r) * W + c) * 3;
                int cc = (c + 37 * f) % W;                            // 每帧平移一点，模拟连续的画面
                bool spot = (r - 1000) * (r - 1000) + (cc - 2000) * (cc - 2000) < 60 * 60;
                p[0] = spot ? 20 : 120 + cc % 100;
                p[1] = spot ? 25 : 130 + r % 80;
                p[2] = spot ? 30 : 140;
            }
    uint8_t *d_rgb[NS], *d_out[NS];
    cudaStream_t st[NS];
    for (int s = 0; s < NS; s++) {
        CHECK(cudaMalloc(&d_rgb[s], rgb_b));
        CHECK(cudaMalloc(&d_out[s], gray_b));
        CHECK(cudaStreamCreate(&st[s]));
    }
    const int bs = 256, gs = (PX + bs - 1) / bs;
    int engines;
    CHECK(cudaDeviceGetAttribute(&engines, cudaDevAttrAsyncEngineCount, 0));

    // 一帧三步各要多久（事件与操作都在 st[0] 里）；按上传时间调处理的计算量。处理时间 = 固定部分（读写显存）+ 每轮乘加的时间 × iters，
    // 用 iters = 0 与 1024 两点定出这条直线，再解出使处理时间等于上传时间的 iters
    float t_h = time_ms([&] { CHECK(cudaMemcpyAsync(d_rgb[0], h_rgb, rgb_b, cudaMemcpyHostToDevice, st[0])); }, 10, st[0]);
    float t_d = time_ms([&] { CHECK(cudaMemcpyAsync(h_out, d_out[0], gray_b, cudaMemcpyDeviceToHost, st[0])); }, 10, st[0]);
    float t0 = time_ms([&] { process<<<gs, bs, 0, st[0]>>>(d_rgb[0], d_out[0], PX, 0); }, 10, st[0]);
    float t1 = time_ms([&] { process<<<gs, bs, 0, st[0]>>>(d_rgb[0], d_out[0], PX, 1024); }, 10, st[0]);
    const double per_iter = std::fmax((t1 - t0) / 1024.0, 1e-9);
    const int iters = int(std::fmin(100000.0, std::fmax(0.0, std::round((t_h - t0) / per_iter))));
    float t_k = time_ms([&] { process<<<gs, bs, 0, st[0]>>>(d_rgb[0], d_out[0], PX, iters); }, 10, st[0]);

    auto serial = [&] {
        for (int f = 0; f < F; f++) {
            CHECK(cudaMemcpyAsync(d_rgb[0], h_rgb + rgb_b * f, rgb_b, cudaMemcpyHostToDevice, st[0]));
            process<<<gs, bs, 0, st[0]>>>(d_rgb[0], d_out[0], PX, iters);
            CHECK(cudaMemcpyAsync(h_out + gray_b * f, d_out[0], gray_b, cudaMemcpyDeviceToHost, st[0]));
        }
        CHECK(cudaStreamSynchronize(st[0]));
    };
    auto streams = [&] {
        for (int f = 0; f < F; f++) {
            int s = f % NS;                                             // 同一个流里的三步仍按顺序；不同流之间可以重叠
            CHECK(cudaMemcpyAsync(d_rgb[s], h_rgb + rgb_b * f, rgb_b, cudaMemcpyHostToDevice, st[s]));
            process<<<gs, bs, 0, st[s]>>>(d_rgb[s], d_out[s], PX, iters);
            CHECK(cudaMemcpyAsync(h_out2 + gray_b * f, d_out[s], gray_b, cudaMemcpyDeviceToHost, st[s]));
        }
        for (int s = 0; s < NS; s++) CHECK(cudaStreamSynchronize(st[s]));
    };
    // 整段计时用主机的时钟，包括最后的同步（涉及多个流时，这样最直接）；先跑一遍预热
    auto wall = [&](auto fn) {
        fn();
        CHECK(cudaGetLastError());
        std::vector<double> v(5);
        for (double& x : v) {
            auto a = std::chrono::steady_clock::now();
            fn();
            x = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - a).count();
        }
        std::sort(v.begin(), v.end());
        return v[2];
    };
    double t_serial = wall(serial), t_streams = wall(streams);
    CHECK(cudaGetLastError());

    bool ok = std::memcmp(h_out, h_out2, gray_b * F) == 0;           // 两种做法结果相同
    for (int f = 0; f < F && ok; f++)
        for (int i = 0; i < PX; i += 9973)                              // 抽样与主机核对
            ok = ok && h_out[gray_b * f + i] == ref_px(h_rgb + rgb_b * f + size_t(i) * 3, iters);
    std::printf("{\"frames\": %d, \"engines\": %d, \"iters\": %d, \"h2d_ms\": %.3f, \"kern_ms\": %.3f, \"d2h_ms\": %.3f, "
                "\"serial_ms\": %.2f, \"streams_ms\": %.2f, \"speedup\": %.2f, \"h2d_GBs\": %.1f, \"k_over_h\": %.2f, \"correct\": %s}\n",
                F, engines, iters, t_h, t_k, t_d, t_serial, t_streams, t_serial / t_streams, rgb_b / 1e9 / (t_h * 1e-3), t_k / t_h,
                ok ? "true" : "false");
    for (int s = 0; s < NS; s++) {
        CHECK(cudaFree(d_rgb[s]));
        CHECK(cudaFree(d_out[s]));
        CHECK(cudaStreamDestroy(st[s]));
    }
    CHECK(cudaFreeHost(h_rgb));
    CHECK(cudaFreeHost(h_out));
    CHECK(cudaFreeHost(h_out2));
    return 0;
}
