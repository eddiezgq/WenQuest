// 程序 4.2.1：把检测相机的一帧彩色图像（3840×2160，RGB 各 8 位）变成灰度并按阈值分出“可能是缺陷”的像素（4.2 节）。
// 二维的线程块与网格：每个线程处理一个像素。编译：nvcc -O3 -arch=native -o gray gray.cu
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <vector>
#include "check.cuh"

// 灰度 Y = 0.299 R + 0.587 G + 0.114 B（ITU-R BT.601）；结果 ≤ thr 的像素记为 1（暗斑，可能是缺陷）
__global__ void gray(const uint8_t* rgb, uint8_t* y, uint8_t* mask, int w, int h, int thr) {
    int col = blockIdx.x * blockDim.x + threadIdx.x;      // 式 (4.2.3)
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    if (col >= w || row >= h) return;
    int p = row * w + col;                                // 行主序：第 row 行第 col 列
    float v = 0.299f * rgb[3 * p] + 0.587f * rgb[3 * p + 1] + 0.114f * rgb[3 * p + 2];
    uint8_t g = uint8_t(v + 0.5f);
    y[p] = g;
    mask[p] = g <= thr;
}

int main() {
    const int w = 3840, h = 2160, thr = 40;
    const size_t px = size_t(w) * h;
    std::vector<uint8_t> rgb(3 * px), hy(px), hm(px);
    for (size_t p = 0; p < px; p++) {                     // 一张合成的测试图：渐变底色，加一块暗斑
        int r = int(p / w), c = int(p % w);
        bool spot = (r - 1000) * (r - 1000) + (c - 2000) * (c - 2000) < 60 * 60;
        rgb[3 * p] = spot ? 20 : 120 + c % 100;
        rgb[3 * p + 1] = spot ? 25 : 130 + r % 80;
        rgb[3 * p + 2] = spot ? 30 : 140;
    }
    uint8_t *drgb, *dy, *dm;
    CHECK(cudaMalloc(&drgb, 3 * px));
    CHECK(cudaMalloc(&dy, px));
    CHECK(cudaMalloc(&dm, px));
    CHECK(cudaMemcpy(drgb, rgb.data(), 3 * px, cudaMemcpyHostToDevice));
    dim3 block(16, 16);                                   // 每块 256 个线程，排成 16×16
    dim3 grid((w + block.x - 1) / block.x, (h + block.y - 1) / block.y);
    gray<<<grid, block>>>(drgb, dy, dm, w, h, thr);
    CHECK_LAUNCH();
    cudaEvent_t t0, t1;
    CHECK(cudaEventCreate(&t0));
    CHECK(cudaEventCreate(&t1));
    std::vector<float> ms(20);
    for (float& m : ms) {
        CHECK(cudaEventRecord(t0));
        gray<<<grid, block>>>(drgb, dy, dm, w, h, thr);
        CHECK(cudaEventRecord(t1));
        CHECK(cudaEventSynchronize(t1));
        CHECK(cudaEventElapsedTime(&m, t0, t1));
    }
    CHECK(cudaGetLastError());
    CHECK(cudaEventDestroy(t0));
    CHECK(cudaEventDestroy(t1));
    std::sort(ms.begin(), ms.end());
    const float t = ms[ms.size() / 2];
    CHECK(cudaMemcpy(hm.data(), dm, px, cudaMemcpyDeviceToHost));
    CHECK(cudaMemcpy(hy.data(), dy, px, cudaMemcpyDeviceToHost));
    size_t dark = 0, diff = 0;
    for (size_t p = 0; p < px; p++) {                     // 与主机上同一公式算出的灰度逐像素比较（4.4.4 节）
        float v = 0.299f * rgb[3 * p] + 0.587f * rgb[3 * p + 1] + 0.114f * rgb[3 * p + 2];
        diff += hy[p] != uint8_t(v + 0.5f);
        dark += hm[p];
    }
    std::printf("{\"gray_ms\": %.4f, \"gray_GBs\": %.1f, \"gray_dark\": %zu, \"gray_diff\": %zu, \"gray_blocks\": %u}\n",
                t, 5.0 * px / (t * 1e-3) / 1e9, dark, diff, grid.x * grid.y);
    CHECK(cudaFree(drgb));
    CHECK(cudaFree(dy));
    CHECK(cudaFree(dm));
    return 0;
}
