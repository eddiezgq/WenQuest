// 程序 5.1.1：映射的融合与 3×3 模板计算（5.1 节）。
//   映射：小型 Transformer 前馈网络第一层的输出 x（32×256×1536 个单精度数）加偏置 b、再过 GELU。
//         unfused：两个核函数（先加偏置写回显存，再读出来过 GELU）；fused：一个核函数。
//   模板：3840×2160 的灰度图（单精度）做 3×3 加权平均，越界时取最近的边界像素；权重放在常量内存。
//         naive：每个线程从全局内存读 9 个数（相邻线程读的数大量重复，靠缓存）；
//         tiled：16×16 的线程块先把 18×18 的输入块（含一圈晕圈）读进共享内存，再从共享内存读 9 个数。
// 编译：nvcc -O3 -arch=native -o stencil stencil.cu
#include <cmath>
#include <cstdio>
#include <vector>
#include "bench.cuh"

constexpr int W = 3840, H = 2160, T = 16;
constexpr int NB = 1536, NF = 32 * 256 * NB;
__constant__ float wts[9];

__device__ __forceinline__ float gelu(float v) {        // GELU 的 tanh 近似，与程序 2.9.1 相同（2.9 节）
    return 0.5f * v * (1.0f + tanhf(0.7978845608f * (v + 0.044715f * v * v * v)));
}
__global__ void add_bias(const float* x, const float* b, float* t, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) t[i] = x[i] + b[i % NB];
}
__global__ void gelu_k(const float* t, float* y, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) y[i] = gelu(t[i]);
}
__global__ void bias_gelu(const float* x, const float* b, float* y, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) y[i] = gelu(x[i] + b[i % NB]);
}

__device__ __forceinline__ int clampi(int v, int hi) { return v < 0 ? 0 : (v > hi ? hi : v); }

__global__ void naive(const float* in, float* out) {
    int x = blockIdx.x * blockDim.x + threadIdx.x, y = blockIdx.y * blockDim.y + threadIdx.y;
    if (x >= W || y >= H) return;
    float s = 0.0f;
    for (int dy = -1; dy <= 1; dy++)
        for (int dx = -1; dx <= 1; dx++)
            s += wts[(dy + 1) * 3 + dx + 1] * in[clampi(y + dy, H - 1) * W + clampi(x + dx, W - 1)];
    out[y * W + x] = s;
}

__global__ void tiled(const float* in, float* out) {
    __shared__ float t[T + 2][T + 2];
    int x0 = blockIdx.x * T - 1, y0 = blockIdx.y * T - 1;          // 输入块左上角（含晕圈）
    for (int i = threadIdx.y; i < T + 2; i += T)                    // 256 个线程读 18×18 = 324 个数
        for (int j = threadIdx.x; j < T + 2; j += T)
            t[i][j] = in[clampi(y0 + i, H - 1) * W + clampi(x0 + j, W - 1)];
    __syncthreads();
    int x = blockIdx.x * T + threadIdx.x, y = blockIdx.y * T + threadIdx.y;
    if (x >= W || y >= H) return;
    float s = 0.0f;
    for (int dy = 0; dy < 3; dy++)
        for (int dx = 0; dx < 3; dx++) s += wts[dy * 3 + dx] * t[threadIdx.y + dy][threadIdx.x + dx];
    out[y * W + x] = s;
}

int main() {
    // ---- 映射的融合
    std::vector<float> hx(NF), hb(NB), h1(NF), h2(NF);
    for (int i = 0; i < NF; i++) hx[i] = float(int(splitmix64(i) % 2001) - 1000) / 250.0f;   // −4 到 4
    for (int i = 0; i < NB; i++) hb[i] = float(int(splitmix64(NF + i) % 201) - 100) / 100.0f;
    float *x, *b, *t, *y;
    CHECK(cudaMalloc(&x, NF * 4));
    CHECK(cudaMalloc(&b, NB * 4));
    CHECK(cudaMalloc(&t, NF * 4));
    CHECK(cudaMalloc(&y, NF * 4));
    CHECK(cudaMemcpy(x, hx.data(), NF * 4, cudaMemcpyHostToDevice));
    CHECK(cudaMemcpy(b, hb.data(), NB * 4, cudaMemcpyHostToDevice));
    const int bs = 256, gs = (NF + bs - 1) / bs;
    float t_unf = time_ms([&] { add_bias<<<gs, bs>>>(x, b, t, NF); gelu_k<<<gs, bs>>>(t, y, NF); });
    CHECK(cudaMemcpy(h1.data(), y, NF * 4, cudaMemcpyDeviceToHost));
    CHECK(cudaMemset(y, 0xFF, NF * 4));
    float t_fus = time_ms([&] { bias_gelu<<<gs, bs>>>(x, b, y, NF); });
    CHECK(cudaMemcpy(h2.data(), y, NF * 4, cudaMemcpyDeviceToHost));
    bool ok_map = h1 == h2;                                       // 同样的运算，结果应逐位相同
    for (int i = 0; i < NF && ok_map; i += 4099) {                // 抽样与主机核对
        float v = hx[i] + hb[i % NB];
        float r = 0.5f * v * (1.0f + std::tanh(0.7978845608f * (v + 0.044715f * v * v * v)));
        ok_map = std::fabs(h2[i] - r) <= 1e-5f * (1.0f + std::fabs(r));
    }
    CHECK(cudaFree(x));
    CHECK(cudaFree(b));
    CHECK(cudaFree(t));
    CHECK(cudaFree(y));

    // ---- 模板计算
    const float hw[9] = {1 / 16.f, 2 / 16.f, 1 / 16.f, 2 / 16.f, 4 / 16.f, 2 / 16.f, 1 / 16.f, 2 / 16.f, 1 / 16.f};
    CHECK(cudaMemcpyToSymbol(wts, hw, sizeof hw));
    const size_t px = size_t(W) * H, bytes = px * 4;
    std::vector<float> hin(px), hout(px), ref(px);
    for (size_t i = 0; i < px; i++) hin[i] = float(splitmix64(i + (1ull << 32)) % 256);
    for (int r = 0; r < H; r++)
        for (int c = 0; c < W; c++) {
            float s = 0.0f;
            for (int dy = -1; dy <= 1; dy++)
                for (int dx = -1; dx <= 1; dx++)
                    s += hw[(dy + 1) * 3 + dx + 1] * hin[size_t(std::min(std::max(r + dy, 0), H - 1)) * W + std::min(std::max(c + dx, 0), W - 1)];
            ref[size_t(r) * W + c] = s;
        }
    float *in, *out;
    CHECK(cudaMalloc(&in, bytes));
    CHECK(cudaMalloc(&out, bytes));
    CHECK(cudaMemcpy(in, hin.data(), bytes, cudaMemcpyHostToDevice));
    dim3 blk(T, T), grd(W / T, H / T);
    auto check = [&] {
        CHECK(cudaMemcpy(hout.data(), out, bytes, cudaMemcpyDeviceToHost));
        for (size_t i = 0; i < px; i++)
            if (hout[i] != ref[i]) return false;       // 权重是 k/16、输入是整数：结果在单精度中精确，与加法顺序无关
        return true;
    };
    CHECK(cudaMemset(out, 0xFF, bytes));
    float t_nv = time_ms([&] { naive<<<grd, blk>>>(in, out); });
    bool ok_nv = check();
    CHECK(cudaMemset(out, 0xFF, bytes));
    float t_tl = time_ms([&] { tiled<<<grd, blk>>>(in, out); });
    bool ok_tl = check();
    CHECK(cudaFree(in));
    CHECK(cudaFree(out));
    const double gb = 2.0 * bytes / 1e9;                         // 有效带宽：每个像素读一次、写一次
    std::printf("{\"unfused_us\": %.1f, \"fused_us\": %.1f, \"naive_us\": %.1f, \"tiled_us\": %.1f, \"naive_GBs\": %.1f, "
                "\"tiled_GBs\": %.1f, \"correct\": %s}\n", t_unf * 1e3, t_fus * 1e3, t_nv * 1e3, t_tl * 1e3, gb / (t_nv * 1e-3),
                gb / (t_tl * 1e-3), ok_map && ok_nv && ok_tl ? "true" : "false");
    return 0;
}
