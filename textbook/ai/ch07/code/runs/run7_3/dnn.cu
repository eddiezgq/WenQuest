// 程序 7.3.1：cuDNN 的各种卷积算法（7.3 节）。卷积层与算例 5.5.1 相同：B = 32，C = K = 64，56×56，3×3，步长 1，补零 1 圈。
// 三种设置：单精度 NCHW 不用张量核心（CUDNN_FMA_MATH）；单精度 NCHW 允许 TF32 张量核心（CUDNN_DEFAULT_MATH，PyTorch 的默认）；
// 半精度 NHWC 用张量核心（CUDNN_TENSOR_OP_MATH）。每种设置把 cuDNN 的 8 种前向算法逐个试：不支持的记“—”；
// 支持的记耗时（中位数）、工作区大小、与参考结果的最大误差。
// 测试数据取 −1、0、1，卷积结果是绝对值不超过 576 的整数：按矩阵乘法做的算法应与参考结果逐位相同，
// 维诺格拉德、快速傅里叶变换的变换中有分数，会有舍入误差（只要求相对于结果的最大绝对值很小）。参考结果由一个直接按定义写的核函数（单精度）算出。
// 另测：cudnnFindConvolutionForwardAlgorithm 选出的最快算法（PyTorch 设 cudnn.benchmark = True 时就这样选）；
// 把输入在两种布局之间转换一次（NHWC → NCHW，cudnnTransformTensor）要多久。
#include <cmath>
#include <cstdio>
#include <string>
#include <vector>
#include <cuda_fp16.h>
#include <cudnn.h>
#include "bench.cuh"

#define CHECK_DNN(call)                                                                            \
    do {                                                                                           \
        cudnnStatus_t s_ = (call);                                                                 \
        if (s_ != CUDNN_STATUS_SUCCESS) {                                                          \
            std::fprintf(stderr, "cuDNN 错误 %s:%d：%s\n", __FILE__, __LINE__, cudnnGetErrorString(s_)); \
            std::exit(1);                                                                          \
        }                                                                                          \
    } while (0)

const int N = 32, C = 64, K = 64, H = 56, W = 56, R = 3, S = 3;
const char* NAMES[] = {"IMPLICIT_GEMM", "IMPLICIT_PRECOMP_GEMM", "GEMM", "DIRECT", "FFT", "FFT_TILING", "WINOGRAD", "WINOGRAD_NONFUSED"};

static float tern(unsigned long long i) { return float(int(splitmix64(i) % 3) - 1); }      // −1、0、1

// 参考：按定义逐项相加（NCHW，单精度；数据是小整数，结果精确）
__global__ void conv_ref(const float* x, const float* w, float* y) {
    int q = blockIdx.x * blockDim.x + threadIdx.x, p = blockIdx.y, nk = blockIdx.z;
    int n = nk / K, k = nk % K;
    if (q >= W) return;
    float s = 0;
    for (int c = 0; c < C; c++)
        for (int r = 0; r < R; r++)
            for (int t = 0; t < S; t++) {
                int ih = p + r - 1, iw = q + t - 1;
                if (ih >= 0 && ih < H && iw >= 0 && iw < W) s += w[((k * C + c) * R + r) * S + t] * x[((n * C + c) * H + ih) * W + iw];
            }
    y[((n * K + k) * H + p) * W + q] = s;
}

std::string fmt(const char* f, double v) {
    char buf[64];
    std::snprintf(buf, sizeof buf, f, v);
    return buf;
}

int main() {
    cudnnHandle_t dnn;
    CHECK_DNN(cudnnCreate(&dnn));
    size_t nx = (size_t)N * C * H * W, nw = (size_t)K * C * R * S, ny = (size_t)N * K * H * W;
    std::vector<float> x(nx), w(nw), ref(ny);
    for (size_t i = 0; i < nx; i++) x[i] = tern(i);
    for (size_t i = 0; i < nw; i++) w[i] = tern(77000000 + i);
    float *dx, *dw, *dy, *dref;
    CHECK(cudaMalloc(&dx, nx * 4));
    CHECK(cudaMalloc(&dw, nw * 4));
    CHECK(cudaMalloc(&dy, ny * 4));
    CHECK(cudaMalloc(&dref, ny * 4));
    CHECK(cudaMemcpy(dx, x.data(), nx * 4, cudaMemcpyHostToDevice));
    CHECK(cudaMemcpy(dw, w.data(), nw * 4, cudaMemcpyHostToDevice));
    conv_ref<<<dim3((W + 63) / 64, H, N * K), 64>>>(dx, dw, dref);
    CHECK_LAUNCH();
    CHECK(cudaMemcpy(ref.data(), dref, ny * 4, cudaMemcpyDeviceToHost));
    double refmax = 0;
    for (float v : ref) refmax = std::fmax(refmax, std::fabs(v));

    // 半精度 NHWC 的数据（整数在半精度里精确）；卷积核按 KRSC 存放
    std::vector<__half> xh(nx), wh(nw);
    for (int n = 0; n < N; n++)
        for (int c = 0; c < C; c++)
            for (int h = 0; h < H; h++)
                for (int v = 0; v < W; v++) xh[((size_t)(n * H + h) * W + v) * C + c] = __float2half(x[((size_t)(n * C + c) * H + h) * W + v]);
    for (int k = 0; k < K; k++)
        for (int c = 0; c < C; c++)
            for (int r = 0; r < R; r++)
                for (int t = 0; t < S; t++) wh[((k * R + r) * S + t) * C + c] = __float2half(w[((k * C + c) * R + r) * S + t]);
    __half *dxh, *dwh, *dyh, *dxh_nchw;
    CHECK(cudaMalloc(&dxh, nx * 2));
    CHECK(cudaMalloc(&dwh, nw * 2));
    CHECK(cudaMalloc(&dyh, ny * 2));
    CHECK(cudaMalloc(&dxh_nchw, nx * 2));
    CHECK(cudaMemcpy(dxh, xh.data(), nx * 2, cudaMemcpyHostToDevice));
    CHECK(cudaMemcpy(dwh, wh.data(), nw * 2, cudaMemcpyHostToDevice));

    struct Setting { const char* key; cudnnDataType_t type; cudnnTensorFormat_t fmt; cudnnMathType_t math; void *x, *w, *y; };
    Setting sets[] = {{"fp32", CUDNN_DATA_FLOAT, CUDNN_TENSOR_NCHW, CUDNN_FMA_MATH, dx, dw, dy},
                      {"tf32", CUDNN_DATA_FLOAT, CUDNN_TENSOR_NCHW, CUDNN_DEFAULT_MATH, dx, dw, dy},
                      {"fp16", CUDNN_DATA_HALF, CUDNN_TENSOR_NHWC, CUDNN_TENSOR_OP_MATH, dxh, dwh, dyh}};
    const float one = 1.0f, zero = 0.0f;
    std::string json = "{";
    bool all_ok = true;
    double flop = 2.0 * N * K * H * W * C * R * S;
    for (auto& st : sets) {
        cudnnTensorDescriptor_t xd, yd;
        cudnnFilterDescriptor_t wd;
        cudnnConvolutionDescriptor_t cd;
        CHECK_DNN(cudnnCreateTensorDescriptor(&xd));
        CHECK_DNN(cudnnCreateTensorDescriptor(&yd));
        CHECK_DNN(cudnnCreateFilterDescriptor(&wd));
        CHECK_DNN(cudnnCreateConvolutionDescriptor(&cd));
        CHECK_DNN(cudnnSetTensor4dDescriptor(xd, st.fmt, st.type, N, C, H, W));
        CHECK_DNN(cudnnSetTensor4dDescriptor(yd, st.fmt, st.type, N, K, H, W));
        CHECK_DNN(cudnnSetFilter4dDescriptor(wd, st.type, st.fmt, K, C, R, S));
        CHECK_DNN(cudnnSetConvolution2dDescriptor(cd, 1, 1, 1, 1, 1, 1, CUDNN_CROSS_CORRELATION, CUDNN_DATA_FLOAT));
        CHECK_DNN(cudnnSetConvolutionMathType(cd, st.math));
        double best = 1e30;
        std::string best_name = "—";
        for (int a = 0; a < 8; a++) {
            auto algo = (cudnnConvolutionFwdAlgo_t)a;
            std::string k = std::string(st.key) + "_" + NAMES[a];
            size_t ws_bytes = 0;
            void* ws = nullptr;
            bool ok = cudnnGetConvolutionForwardWorkspaceSize(dnn, xd, wd, cd, yd, algo, &ws_bytes) == CUDNN_STATUS_SUCCESS;
            if (ok && ws_bytes) ok = cudaMalloc(&ws, ws_bytes) == cudaSuccess;
            if (ok) ok = cudnnConvolutionForward(dnn, &one, xd, st.x, wd, st.w, cd, algo, ws, ws_bytes, &zero, yd, st.y) == CUDNN_STATUS_SUCCESS;
            if (ok) ok = cudaDeviceSynchronize() == cudaSuccess;
            if (!ok) {
                cudaGetLastError();
                if (ws) cudaFree(ws);
                json += "\"" + k + "_us\": \"—\", \"" + k + "_ws\": \"—\", \"" + k + "_err\": \"—\", ";
                continue;
            }
            float ms = time_ms([&] { cudnnConvolutionForward(dnn, &one, xd, st.x, wd, st.w, cd, algo, ws, ws_bytes, &zero, yd, st.y); });
            double err = 0;
            if (st.type == CUDNN_DATA_FLOAT) {
                std::vector<float> y(ny);
                CHECK(cudaMemcpy(y.data(), st.y, ny * 4, cudaMemcpyDeviceToHost));
                for (size_t i = 0; i < ny; i++) err = std::fmax(err, std::fabs(y[i] - ref[i]));
            } else {
                std::vector<__half> y(ny);
                CHECK(cudaMemcpy(y.data(), st.y, ny * 2, cudaMemcpyDeviceToHost));
                for (int n = 0; n < N; n++)
                    for (int kk = 0; kk < K; kk++)
                        for (int h = 0; h < H; h++)
                            for (int v = 0; v < W; v++)
                                err = std::fmax(err, std::fabs(__half2float(y[((size_t)(n * H + h) * W + v) * K + kk]) -
                                                               ref[((size_t)(n * K + kk) * H + h) * W + v]));
            }
            // 核对：按矩阵乘法做的与直接卷积（前 4 种）应与参考逐位相同；变换类算法有舍入误差，只要求相对于结果的最大绝对值很小
            // （单精度 1e-3；TF32 与半精度的尾数只有 10 位，放宽到 3e-2）
            double tol = (st.math == CUDNN_FMA_MATH ? 1e-3 : 3e-2) * refmax;
            all_ok = all_ok && (a < 4 ? err == 0 : err <= tol);
            if (ws) CHECK(cudaFree(ws));
            if (ms < best) best = ms, best_name = NAMES[a];
            json += "\"" + k + "_us\": \"" + fmt("%.0f", ms * 1e3) + "\", \"" + k + "_ws\": \"" + fmt("%.0f", ws_bytes / 1e6) +
                    "\", \"" + k + "_err\": \"" + (err == 0 ? std::string("0") : fmt("%.0e", err)) + "\", ";
        }
        // cuDNN 自己试一遍，挑出最快的（cudnn.benchmark = True 时 PyTorch 这样选）
        cudnnConvolutionFwdAlgoPerf_t perf[8];
        int got = 0;
        CHECK_DNN(cudnnFindConvolutionForwardAlgorithm(dnn, xd, wd, cd, yd, 8, &got, perf));
        json += std::string("\"") + st.key + "_find\": \"" + NAMES[perf[0].algo] + "\", \"" + st.key + "_best\": \"" + best_name +
                "\", \"" + st.key + "_best_us\": " + fmt("%.1f", best * 1e3) + ", \"" + st.key + "_best_TFs\": " + fmt("%.1f", flop / best / 1e9) + ", ";
    }
    // 输入从 NHWC 转成 NCHW（半精度；反方向的代价相同）
    cudnnTensorDescriptor_t a, b;
    CHECK_DNN(cudnnCreateTensorDescriptor(&a));
    CHECK_DNN(cudnnCreateTensorDescriptor(&b));
    CHECK_DNN(cudnnSetTensor4dDescriptor(a, CUDNN_TENSOR_NHWC, CUDNN_DATA_HALF, N, C, H, W));
    CHECK_DNN(cudnnSetTensor4dDescriptor(b, CUDNN_TENSOR_NCHW, CUDNN_DATA_HALF, N, C, H, W));
    size_t v = cudnnGetVersion();                           // 9.x：主版本 × 10000 + 次版本 × 100 + 补丁号；8.x：主版本 × 1000 + …
    size_t major = v >= 10000 ? v / 10000 : v / 1000, minor = v >= 10000 ? v / 100 % 100 : v / 100 % 10;
    float tr_ms = time_ms([&] { cudnnTransformTensor(dnn, &one, a, dxh, &zero, b, dxh_nchw); });
    json += "\"transform_us\": " + fmt("%.1f", tr_ms * 1e3) + ", \"transform_GBs\": " + fmt("%.0f", 2.0 * nx * 2 / tr_ms / 1e6) +
            ", \"cudnn\": \"" + std::to_string(major) + "." + std::to_string(minor) + "." + std::to_string(v % 100) + "\", \"correct\": " + (all_ok ? "true" : "false") + "}";
    std::printf("%s\n", json.c_str());
    return 0;
}
