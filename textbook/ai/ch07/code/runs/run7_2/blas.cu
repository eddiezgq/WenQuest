// 程序 7.2.1：cuBLAS 与 cuBLASLt（7.2 节）。三件事：
// （1）列主序约定：行主序的 C = A·B（M×K 乘 K×N），交给 cuBLAS 算 Cᵀ = Bᵀ·Aᵀ——B 在前、A 在后、M 与 N 对调，不搬数据；
//      测试数据取 −2—2 的整数，乘加的结果是精确的整数，与主机逐位相同。
// （2）注意力分数：B·h = 192 个 256×64 乘 64×256 的矩阵乘法，逐个调用 cublasSgemm 与一次 cublasSgemmStridedBatched 比较。
// （3）cuBLASLt 的尾处理：前馈网络第一层 Y = GELU(X·W + b)，X 为 8192×384、W 为 384×1536（半精度，单精度累加）。
//      一次带 GELU_BIAS 尾处理的矩阵乘法，与“矩阵乘法 + 另一个核函数加偏置、过 GELU”比较。
// 输出一行 JSON：各项耗时（中位数，μs）与核对结果。
#include <cmath>
#include <cstdio>
#include <vector>
#include <cublasLt.h>
#include <cublas_v2.h>
#include <cuda_fp16.h>
#include "bench.cuh"

#define CHECK_BLAS(call)                                                                      \
    do {                                                                                      \
        cublasStatus_t s_ = (call);                                                           \
        if (s_ != CUBLAS_STATUS_SUCCESS) {                                                    \
            std::fprintf(stderr, "cuBLAS 错误 %s:%d：%d\n", __FILE__, __LINE__, (int)s_);       \
            std::exit(1);                                                                     \
        }                                                                                     \
    } while (0)

static float small_int(unsigned long long i) { return float(int(splitmix64(i) % 5) - 2); }      // −2—2
static float uniform(unsigned long long i) { return float(splitmix64(i) >> 11) * 0x1.0p-53f * 2.0f - 1.0f; }   // [−1, 1)

// 加偏置、过 GELU（tanh 近似，与 2.9 节相同），原地改写 Y（行主序，每行 n 个数）
__global__ void bias_gelu(__half* y, const __half* b, long long total, int n) {
    long long i = blockIdx.x * (long long)blockDim.x + threadIdx.x;
    if (i >= total) return;
    float x = __half2float(y[i]) + __half2float(b[i % n]);
    float u = tanhf(0.7978845608f * (x + 0.044715f * x * x * x));
    y[i] = __float2half(0.5f * x * (1.0f + u));
}

int main() {
    cublasHandle_t h;
    CHECK_BLAS(cublasCreate(&h));
    const float one = 1.0f, zero = 0.0f;

    // ---------------------------------------------------------------- （1）列主序约定
    const int M = 300, N = 200, K = 100;
    std::vector<float> A(M * K), B(K * N), C(M * N), ref(M * N, 0.0f);
    for (int i = 0; i < M * K; i++) A[i] = small_int(i);
    for (int i = 0; i < K * N; i++) B[i] = small_int(1000000 + i);
    for (int i = 0; i < M; i++)
        for (int k = 0; k < K; k++)
            for (int j = 0; j < N; j++) ref[i * N + j] += A[i * K + k] * B[k * N + j];
    float *dA, *dB, *dC;
    CHECK(cudaMalloc(&dA, A.size() * 4));
    CHECK(cudaMalloc(&dB, B.size() * 4));
    CHECK(cudaMalloc(&dC, C.size() * 4));
    CHECK(cudaMemcpy(dA, A.data(), A.size() * 4, cudaMemcpyHostToDevice));
    CHECK(cudaMemcpy(dB, B.data(), B.size() * 4, cudaMemcpyHostToDevice));
    // 列主序下：B 的缓冲区是 Bᵀ（N×K，ld = N），A 的缓冲区是 Aᵀ（K×M，ld = K），结果 Cᵀ（N×M，ld = N）就是行主序的 C
    CHECK_BLAS(cublasSgemm(h, CUBLAS_OP_N, CUBLAS_OP_N, N, M, K, &one, dB, N, dA, K, &zero, dC, N));
    CHECK(cudaMemcpy(C.data(), dC, C.size() * 4, cudaMemcpyDeviceToHost));
    bool ok_swap = C == ref;
    // 不对调、直接把行主序的缓冲区交给 cuBLAS：得到的不是 A·B
    CHECK_BLAS(cublasSgemm(h, CUBLAS_OP_N, CUBLAS_OP_N, M, N, K, &one, dA, M, dB, K, &zero, dC, M));
    CHECK(cudaMemcpy(C.data(), dC, C.size() * 4, cudaMemcpyDeviceToHost));
    bool naive_wrong = C != ref;

    // ---------------------------------------------------------------- （2）批量矩阵乘法
    const int nb = 192, T = 256, dh = 64;
    std::vector<float> Q((size_t)nb * T * dh), Kh((size_t)nb * T * dh);
    for (size_t i = 0; i < Q.size(); i++) Q[i] = small_int(2000000 + i), Kh[i] = small_int(90000000 + i);
    float *dQ, *dK, *dS1, *dS2;
    CHECK(cudaMalloc(&dQ, Q.size() * 4));
    CHECK(cudaMalloc(&dK, Kh.size() * 4));
    CHECK(cudaMalloc(&dS1, (size_t)nb * T * T * 4));
    CHECK(cudaMalloc(&dS2, (size_t)nb * T * T * 4));
    CHECK(cudaMemcpy(dQ, Q.data(), Q.size() * 4, cudaMemcpyHostToDevice));
    CHECK(cudaMemcpy(dK, Kh.data(), Kh.size() * 4, cudaMemcpyHostToDevice));
    // 每批：行主序 S = Q·Kᵀ（T×T）⇔ 列主序 Sᵀ = K·Qᵀ。K 的缓冲区按列主序是 Kᵀ（dh×T），要转置（OP_T）；Q 的缓冲区是 Qᵀ，不转置
    auto loop = [&] {
        for (int i = 0; i < nb; i++)
            CHECK_BLAS(cublasSgemm(h, CUBLAS_OP_T, CUBLAS_OP_N, T, T, dh, &one, dK + (size_t)i * T * dh, dh,
                                   dQ + (size_t)i * T * dh, dh, &zero, dS1 + (size_t)i * T * T, T));
    };
    auto batched = [&] {
        CHECK_BLAS(cublasSgemmStridedBatched(h, CUBLAS_OP_T, CUBLAS_OP_N, T, T, dh, &one, dK, dh, (long long)T * dh,
                                             dQ, dh, (long long)T * dh, &zero, dS2, T, (long long)T * T, nb));
    };
    float loop_ms = time_ms(loop), batched_ms = time_ms(batched);
    std::vector<float> S1((size_t)nb * T * T), S2(S1.size());
    CHECK(cudaMemcpy(S1.data(), dS1, S1.size() * 4, cudaMemcpyDeviceToHost));
    CHECK(cudaMemcpy(S2.data(), dS2, S2.size() * 4, cudaMemcpyDeviceToHost));
    bool ok_batched = S1 == S2;
    for (int bi : {0, 77, nb - 1})                          // 三批与主机逐位核对
        for (int r = 0; r < T; r++)
            for (int c = 0; c < T; c++) {
                float s = 0;
                for (int k = 0; k < dh; k++) s += Q[((size_t)bi * T + r) * dh + k] * Kh[((size_t)bi * T + c) * dh + k];
                ok_batched = ok_batched && S2[((size_t)bi * T + r) * T + c] == s;
            }

    // ---------------------------------------------------------------- （3）cuBLASLt 的尾处理
    const int n = 8192, d = 384, f = 1536;
    std::vector<__half> X((size_t)n * d), W((size_t)d * f), bias(f);
    for (size_t i = 0; i < X.size(); i++) X[i] = __float2half(uniform(3000000000ull + i));
    for (size_t i = 0; i < W.size(); i++) W[i] = __float2half(uniform(4000000000ull + i) * 0.1f);
    for (int i = 0; i < f; i++) bias[i] = __float2half(uniform(5000000000ull + i) * 0.5f);
    __half *dX, *dW, *db, *dY1, *dY2;
    CHECK(cudaMalloc(&dX, X.size() * 2));
    CHECK(cudaMalloc(&dW, W.size() * 2));
    CHECK(cudaMalloc(&db, f * 2));
    CHECK(cudaMalloc(&dY1, (size_t)n * f * 2));
    CHECK(cudaMalloc(&dY2, (size_t)n * f * 2));
    CHECK(cudaMemcpy(dX, X.data(), X.size() * 2, cudaMemcpyHostToDevice));
    CHECK(cudaMemcpy(dW, W.data(), W.size() * 2, cudaMemcpyHostToDevice));
    CHECK(cudaMemcpy(db, bias.data(), f * 2, cudaMemcpyHostToDevice));
    size_t ws_bytes = 32 << 20;
    void* ws;
    CHECK(cudaMalloc(&ws, ws_bytes));
    cublasLtHandle_t lt;
    CHECK_BLAS(cublasLtCreate(&lt));
    // 列主序：D（f×n，ld = f）= W 的缓冲区（f×d，ld = f）× X 的缓冲区（d×n，ld = d）；偏置按 D 的行加，长度 f
    cublasLtMatrixLayout_t La, Lb, Ld;
    CHECK_BLAS(cublasLtMatrixLayoutCreate(&La, CUDA_R_16F, f, d, f));
    CHECK_BLAS(cublasLtMatrixLayoutCreate(&Lb, CUDA_R_16F, d, n, d));
    CHECK_BLAS(cublasLtMatrixLayoutCreate(&Ld, CUDA_R_16F, f, n, f));
    cublasLtMatmulPreference_t pref;
    CHECK_BLAS(cublasLtMatmulPreferenceCreate(&pref));
    CHECK_BLAS(cublasLtMatmulPreferenceSetAttribute(pref, CUBLASLT_MATMUL_PREF_MAX_WORKSPACE_BYTES, &ws_bytes, sizeof(ws_bytes)));
    auto make = [&](cublasLtEpilogue_t epi, cublasLtMatmulDesc_t& desc, cublasLtMatmulHeuristicResult_t& heur) {
        CHECK_BLAS(cublasLtMatmulDescCreate(&desc, CUBLAS_COMPUTE_32F, CUDA_R_32F));
        CHECK_BLAS(cublasLtMatmulDescSetAttribute(desc, CUBLASLT_MATMUL_DESC_EPILOGUE, &epi, sizeof(epi)));
        if (epi != CUBLASLT_EPILOGUE_DEFAULT)
            CHECK_BLAS(cublasLtMatmulDescSetAttribute(desc, CUBLASLT_MATMUL_DESC_BIAS_POINTER, &db, sizeof(db)));
        int found = 0;
        CHECK_BLAS(cublasLtMatmulAlgoGetHeuristic(lt, desc, La, Lb, Ld, Ld, pref, 1, &heur, &found));
        if (!found) { std::fprintf(stderr, "cuBLASLt 找不到可用的算法\n"); std::exit(1); }
    };
    cublasLtMatmulDesc_t dFused, dPlain;
    cublasLtMatmulHeuristicResult_t hFused, hPlain;
    make(CUBLASLT_EPILOGUE_GELU_BIAS, dFused, hFused);
    make(CUBLASLT_EPILOGUE_DEFAULT, dPlain, hPlain);
    auto fused = [&] {
        CHECK_BLAS(cublasLtMatmul(lt, dFused, &one, dW, La, dX, Lb, &zero, dY1, Ld, dY1, Ld, &hFused.algo, ws, ws_bytes, 0));
    };
    auto plain = [&] {
        CHECK_BLAS(cublasLtMatmul(lt, dPlain, &one, dW, La, dX, Lb, &zero, dY2, Ld, dY2, Ld, &hPlain.algo, ws, ws_bytes, 0));
    };
    long long total = (long long)n * f;
    auto epi = [&] { bias_gelu<<<(total + 255) / 256, 256>>>(dY2, db, total, f); };
    auto unfused = [&] { plain(); epi(); };
    float fused_ms = time_ms(fused), plain_ms = time_ms(plain), epi_ms = time_ms(epi), unfused_ms = time_ms(unfused);
    fused();
    unfused();
    CHECK_LAUNCH();
    std::vector<__half> Y1((size_t)n * f), Y2(Y1.size());
    CHECK(cudaMemcpy(Y1.data(), dY1, Y1.size() * 2, cudaMemcpyDeviceToHost));
    CHECK(cudaMemcpy(Y2.data(), dY2, Y2.size() * 2, cudaMemcpyDeviceToHost));
    double max_diff = 0, max_y = 0;
    for (size_t i = 0; i < Y1.size(); i++) {
        max_diff = std::fmax(max_diff, std::fabs(__half2float(Y1[i]) - __half2float(Y2[i])));
        max_y = std::fmax(max_y, std::fabs(__half2float(Y2[i])));
    }
    // 两种做法只差在 GELU 的写法与中间结果的舍入（融合时 GELU 作用在单精度的累加结果上，不融合时先舍入成半精度）
    bool ok_epi = max_diff <= 0.01 * max_y;
    double flop = 2.0 * n * d * f;
    std::printf("{\"correct\": %s, \"ok_swap\": %s, \"naive_wrong\": %s, \"ok_batched\": %s, \"ok_epi\": %s, "
                "\"loop_us\": %.2f, \"batched_us\": %.2f, \"batch_speedup\": %.2f, "
                "\"fused_us\": %.2f, \"plain_us\": %.2f, \"epi_us\": %.2f, \"unfused_us\": %.2f, \"epi_saving_pct\": %.1f, "
                "\"plain_TFs\": %.1f, \"epi_GBs\": %.0f, \"max_diff\": %.5f, \"max_y\": %.3f}\n",
                ok_swap && naive_wrong && ok_batched && ok_epi ? "true" : "false", ok_swap ? "true" : "false",
                naive_wrong ? "true" : "false", ok_batched ? "true" : "false", ok_epi ? "true" : "false",
                loop_ms * 1e3, batched_ms * 1e3, loop_ms / batched_ms, fused_ms * 1e3, plain_ms * 1e3, epi_ms * 1e3,
                unfused_ms * 1e3, 100.0 * (unfused_ms - fused_ms) / unfused_ms, flop / plain_ms / 1e9,
                2.0 * total * 2 / epi_ms / 1e6, max_diff, max_y);
    return 0;
}
