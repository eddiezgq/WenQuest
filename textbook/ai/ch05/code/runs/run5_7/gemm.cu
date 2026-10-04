// 程序 5.7.1：矩阵乘法 C = AB 从朴素版到张量核心版（5.7—5.11 节）。A 为 M×K、B 为 K×N、C 为 M×N，行主序。
//   naive_rowx ：朴素版，threadIdx.x 对应行（读 A 跨步 K，不合并）——反面的例子
//   naive      ：朴素版，threadIdx.x 对应列（读 B 合并，读 A 广播）                         5.7 节
//   tiled      ：32×32 的共享内存分块                                                      5.8 节
//   regtile    ：线程块 128×128、沿 K 每步 8，每个线程算 8×8 个（寄存器分块）               5.9 节
//   vec        ：regtile + float4 向量化读写，线程负责的 8 列分成相隔 64 的两组（无存储体冲突） 5.9 节
//   dbuf       ：vec + 双缓冲（读下一块与计算这一块重叠）                                    5.9 节
//   wmma       ：半精度输入、单精度累加，张量核心（WMMA 接口），线程块 128×128、每个线程束 32×64 5.10 节
//   cuBLAS     ：cublasSgemm（单精度）、同一调用打开 TF32 张量核心、cublasGemmEx（半精度输入，单精度累加） 5.11 节
// 测试数据是 −2 到 2 的整数，各版本（含 TF32、半精度）的结果都是精确的整数，可以逐个比较：先用 CPU 抽样核对 cuBLAS 单精度，
// 再要求其余各版本与它完全相同。n 须为 128 的倍数。
// 编译：nvcc -O3 -arch=native -o gemm gemm.cu -lcublas；运行：./gemm [n，默认 4096]
#include <cstdio>
#include <cstdlib>
#include <cublas_v2.h>
#include <cuda_fp16.h>
#include <mma.h>
#include "bench.cuh"

using namespace nvcuda;

// ---------- 5.7 朴素版：一个线程算 C 的一个元素
__global__ void naive_rowx(int M, int N, int K, const float* A, const float* B, float* C) {
    int row = blockIdx.x * blockDim.x + threadIdx.x, col = blockIdx.y * blockDim.y + threadIdx.y;   // x → 行：反面的例子
    float s = 0.0f;
    for (int k = 0; k < K; k++) s += A[row * K + k] * B[k * N + col];
    C[row * N + col] = s;
}

__global__ void naive(int M, int N, int K, const float* A, const float* B, float* C) {
    int row = blockIdx.y * blockDim.y + threadIdx.y, col = blockIdx.x * blockDim.x + threadIdx.x;   // x → 列
    float s = 0.0f;
    for (int k = 0; k < K; k++) s += A[row * K + k] * B[k * N + col];
    C[row * N + col] = s;
}

// ---------- 5.8 共享内存分块：线程块 32×32 个线程算 C 的 32×32 块
constexpr int T = 32;
__global__ void tiled(int M, int N, int K, const float* A, const float* B, float* C) {
    __shared__ float As[T][T], Bs[T][T];
    int tx = threadIdx.x, ty = threadIdx.y;
    int row = blockIdx.y * T + ty, col = blockIdx.x * T + tx;
    float s = 0.0f;
    for (int k0 = 0; k0 < K; k0 += T) {
        As[ty][tx] = A[row * K + k0 + tx];          // 读合并：相邻线程读同一行中相邻的数
        Bs[ty][tx] = B[(k0 + ty) * N + col];
        __syncthreads();
        for (int k = 0; k < T; k++) s += As[ty][k] * Bs[k][tx];   // As[ty][k]：同一线程束广播；Bs[k][tx]：连续，无冲突
        __syncthreads();                             // 下一轮覆盖共享内存之前，大家都要算完
    }
    C[row * N + col] = s;
}

// ---------- 5.9 寄存器分块：线程块 128×128，沿 K 每步 8；256 个线程排成 16×16，每个线程算 8×8 个
constexpr int BM = 128, BN = 128, BK = 8, TM = 8, TN = 8, NT = 256;
// __launch_bounds__(NT, 2)：要求编译器把每个线程的寄存器控制在 65536 / (256 × 2) = 128 个以内，保证每个 SM 能驻留 2 个线程块

__global__ void __launch_bounds__(NT, 2) regtile(int M, int N, int K, const float* A, const float* B, float* C) {
    __shared__ float As[BK][BM];                      // A 的块转置存放：As[k][m]，内层循环读一行 8 个连续的数
    __shared__ float Bs[BK][BN];
    const int tid = threadIdx.x, trow = tid / 16, tcol = tid % 16;
    const float* Ab = A + size_t(blockIdx.y) * BM * K;
    const float* Bb = B + blockIdx.x * BN;
    float acc[TM][TN] = {}, ra[TM], rb[TN];
    for (int k0 = 0; k0 < K; k0 += BK) {
        for (int i = 0; i < BM * BK / NT; i++) {      // A 的 128×8 块：每个线程读 4 个
            int e = tid + i * NT, m = e / BK, k = e % BK;
            As[k][m] = Ab[size_t(m) * K + k0 + k];
        }
        for (int i = 0; i < BK * BN / NT; i++) {      // B 的 8×128 块：每个线程读 4 个，读合并
            int e = tid + i * NT, k = e / BN, n = e % BN;
            Bs[k][n] = Bb[size_t(k0 + k) * N + n];
        }
        __syncthreads();
        for (int k = 0; k < BK; k++) {
            for (int i = 0; i < TM; i++) ra[i] = As[k][trow * TM + i];
            for (int j = 0; j < TN; j++) rb[j] = Bs[k][tcol * TN + j];
            for (int i = 0; i < TM; i++)
                for (int j = 0; j < TN; j++) acc[i][j] += ra[i] * rb[j];   // 外积：读 16 个数，做 64 次乘加
        }
        __syncthreads();
    }
    for (int i = 0; i < TM; i++)
        for (int j = 0; j < TN; j++)
            C[size_t(blockIdx.y * BM + trow * TM + i) * N + blockIdx.x * BN + tcol * TN + j] = acc[i][j];
}

// vec 与 dbuf 共用：把 A、B 的第 k0 步的块用 float4 读进寄存器，再存进共享内存
struct Frag {
    float4 a, b;
};
__device__ __forceinline__ Frag load_tiles(const float* Ab, const float* Bb, int N, int K, int k0, int tid) {
    Frag f;
    f.a = *reinterpret_cast<const float4*>(Ab + size_t(tid / 2) * K + k0 + (tid % 2) * 4);    // A：128 行 × 2 个 float4
    f.b = *reinterpret_cast<const float4*>(Bb + size_t(k0 + tid / 32) * N + (tid % 32) * 4);  // B：8 行 × 32 个 float4
    return f;
}
__device__ __forceinline__ void store_tiles(const Frag& f, float (*As)[BM], float (*Bs)[BN], int tid) {
    int m = tid / 2, kq = (tid % 2) * 4;
    As[kq + 0][m] = f.a.x;                            // A 转置存放
    As[kq + 1][m] = f.a.y;
    As[kq + 2][m] = f.a.z;
    As[kq + 3][m] = f.a.w;
    *reinterpret_cast<float4*>(&Bs[tid / 32][(tid % 32) * 4]) = f.b;
}
// 计算一步：线程负责的 8 行是 trow*4 + {0..3} 与 64 + trow*4 + {0..3}，8 列同理——每次读 float4，四分之一线程束内地址连续，无冲突
__device__ __forceinline__ void compute_step(const float (*As)[BM], const float (*Bs)[BN], float (*acc)[TN], int trow, int tcol) {
    for (int k = 0; k < BK; k++) {
        float4 a0 = *reinterpret_cast<const float4*>(&As[k][trow * 4]), a1 = *reinterpret_cast<const float4*>(&As[k][64 + trow * 4]);
        float4 b0 = *reinterpret_cast<const float4*>(&Bs[k][tcol * 4]), b1 = *reinterpret_cast<const float4*>(&Bs[k][64 + tcol * 4]);
        float ra[8] = {a0.x, a0.y, a0.z, a0.w, a1.x, a1.y, a1.z, a1.w}, rb[8] = {b0.x, b0.y, b0.z, b0.w, b1.x, b1.y, b1.z, b1.w};
        for (int i = 0; i < 8; i++)
            for (int j = 0; j < 8; j++) acc[i][j] += ra[i] * rb[j];
    }
}
__device__ __forceinline__ void store_c(float* C, int N, float (*acc)[TN], int trow, int tcol) {
    float* Cb = C + size_t(blockIdx.y) * BM * N + blockIdx.x * BN;
    for (int i = 0; i < 8; i++) {
        int r = (i < 4 ? 0 : 64) + trow * 4 + i % 4;
        *reinterpret_cast<float4*>(Cb + size_t(r) * N + tcol * 4) = make_float4(acc[i][0], acc[i][1], acc[i][2], acc[i][3]);
        *reinterpret_cast<float4*>(Cb + size_t(r) * N + 64 + tcol * 4) = make_float4(acc[i][4], acc[i][5], acc[i][6], acc[i][7]);
    }
}

__global__ void __launch_bounds__(NT, 2) vec(int M, int N, int K, const float* A, const float* B, float* C) {
    __shared__ __align__(16) float As[BK][BM];
    __shared__ __align__(16) float Bs[BK][BN];
    const int tid = threadIdx.x, trow = tid / 16, tcol = tid % 16;
    const float* Ab = A + size_t(blockIdx.y) * BM * K;
    const float* Bb = B + blockIdx.x * BN;
    float acc[TM][TN] = {};
    for (int k0 = 0; k0 < K; k0 += BK) {
        store_tiles(load_tiles(Ab, Bb, N, K, k0, tid), As, Bs, tid);
        __syncthreads();
        compute_step(As, Bs, acc, trow, tcol);
        __syncthreads();
    }
    store_c(C, N, acc, trow, tcol);
}

__global__ void __launch_bounds__(NT, 2) dbuf(int M, int N, int K, const float* A, const float* B, float* C) {
    __shared__ __align__(16) float As[2][BK][BM];     // 两份：计算一份的同时往另一份里装下一步的数据
    __shared__ __align__(16) float Bs[2][BK][BN];
    const int tid = threadIdx.x, trow = tid / 16, tcol = tid % 16;
    const float* Ab = A + size_t(blockIdx.y) * BM * K;
    const float* Bb = B + blockIdx.x * BN;
    float acc[TM][TN] = {};
    const int steps = K / BK;
    store_tiles(load_tiles(Ab, Bb, N, K, 0, tid), As[0], Bs[0], tid);
    __syncthreads();
    for (int t = 0; t < steps; t++) {
        const int cur = t & 1;
        Frag next;
        if (t + 1 < steps) next = load_tiles(Ab, Bb, N, K, (t + 1) * BK, tid);   // 先发出下一步的读（不等它到）
        compute_step(As[cur], Bs[cur], acc, trow, tcol);                         // 读在路上时做这一步的计算
        if (t + 1 < steps) store_tiles(next, As[cur ^ 1], Bs[cur ^ 1], tid);    // 另一份上一轮已用完（上一轮末尾同步过）
        __syncthreads();                                                         // 每步只同步一次
    }
    store_c(C, N, acc, trow, tcol);
}

// ---------- 5.10 张量核心（WMMA）：半精度输入、单精度累加。线程块 128×128、沿 K 每步 32；8 个线程束排成 4×2，每个算 32×64
constexpr int WBK = 32, LDA = WBK + 8, LDB = BN + 8;   // 每行多留 8 个半精度数（16 字节），减少存储体冲突
__global__ void __launch_bounds__(NT) wmma_gemm(int M, int N, int K, const half* A, const half* B, float* C) {
    __shared__ __align__(32) half As[BM][LDA];
    __shared__ __align__(32) half Bs[WBK][LDB];
    const int tid = threadIdx.x, warp = tid / 32, wm = warp / 2, wn = warp % 2;
    const half* Ab = A + size_t(blockIdx.y) * BM * K;
    const half* Bb = B + blockIdx.x * BN;
    wmma::fragment<wmma::matrix_a, 16, 16, 16, half, wmma::row_major> fa[2];
    wmma::fragment<wmma::matrix_b, 16, 16, 16, half, wmma::row_major> fb[4];
    wmma::fragment<wmma::accumulator, 16, 16, 16, float> fc[2][4];
    for (int i = 0; i < 2; i++)
        for (int j = 0; j < 4; j++) wmma::fill_fragment(fc[i][j], 0.0f);
    for (int k0 = 0; k0 < K; k0 += WBK) {
        for (int i = 0; i < 2; i++) {                 // A 的 128×32 块与 B 的 32×128 块：各 512 个 16 字节，每个线程搬 2 个
            int e = tid + i * NT;
            *reinterpret_cast<uint4*>(&As[e / 4][(e % 4) * 8]) = *reinterpret_cast<const uint4*>(Ab + size_t(e / 4) * K + k0 + (e % 4) * 8);
            *reinterpret_cast<uint4*>(&Bs[e / 16][(e % 16) * 8]) = *reinterpret_cast<const uint4*>(Bb + size_t(k0 + e / 16) * N + (e % 16) * 8);
        }
        __syncthreads();
        for (int kk = 0; kk < WBK; kk += 16) {
            for (int i = 0; i < 2; i++) wmma::load_matrix_sync(fa[i], &As[wm * 32 + i * 16][kk], LDA);
            for (int j = 0; j < 4; j++) wmma::load_matrix_sync(fb[j], &Bs[kk][wn * 64 + j * 16], LDB);
            for (int i = 0; i < 2; i++)
                for (int j = 0; j < 4; j++) wmma::mma_sync(fc[i][j], fa[i], fb[j], fc[i][j]);   // 16×16×16 的乘加，整个线程束一起做
        }
        __syncthreads();
    }
    for (int i = 0; i < 2; i++)
        for (int j = 0; j < 4; j++)
            wmma::store_matrix_sync(C + size_t(blockIdx.y * BM + wm * 32 + i * 16) * N + blockIdx.x * BN + wn * 64 + j * 16, fc[i][j], N,
                                    wmma::mem_row_major);
}

#define CHECK_BLAS(call)                                                                     \
    do {                                                                                     \
        cublasStatus_t st_ = (call);                                                         \
        if (st_ != CUBLAS_STATUS_SUCCESS) {                                                  \
            std::fprintf(stderr, "cuBLAS 错误 %s:%d：%d\n", __FILE__, __LINE__, int(st_));     \
            std::exit(1);                                                                    \
        }                                                                                    \
    } while (0)

int main(int argc, char** argv) {
    const int n = argc > 1 ? std::atoi(argv[1]) : 4096, M = n, N = n, K = n;
    if (n <= 0 || n % 128) {
        std::fprintf(stderr, "n 须为 128 的倍数\n");
        return 1;
    }
    const size_t mn = size_t(M) * N;
    std::vector<float> hA(size_t(M) * K), hB(size_t(K) * N), ref(mn), got(mn);
    std::vector<half> hAh(hA.size()), hBh(hB.size());
    for (size_t i = 0; i < hA.size(); i++) hAh[i] = __float2half(hA[i] = float(int(splitmix64(i) % 5) - 2));
    for (size_t i = 0; i < hB.size(); i++) hBh[i] = __float2half(hB[i] = float(int(splitmix64(i + (1ull << 40)) % 5) - 2));
    float *A, *B, *Cm;
    half *Ah, *Bh;
    CHECK(cudaMalloc(&A, hA.size() * 4));
    CHECK(cudaMalloc(&B, hB.size() * 4));
    CHECK(cudaMalloc(&Cm, mn * 4));
    CHECK(cudaMalloc(&Ah, hA.size() * 2));
    CHECK(cudaMalloc(&Bh, hB.size() * 2));
    CHECK(cudaMemcpy(A, hA.data(), hA.size() * 4, cudaMemcpyHostToDevice));
    CHECK(cudaMemcpy(B, hB.data(), hB.size() * 4, cudaMemcpyHostToDevice));
    CHECK(cudaMemcpy(Ah, hAh.data(), hA.size() * 2, cudaMemcpyHostToDevice));
    CHECK(cudaMemcpy(Bh, hBh.data(), hB.size() * 2, cudaMemcpyHostToDevice));
    cublasHandle_t h;
    CHECK_BLAS(cublasCreate(&h));
    const float one = 1.0f, zero = 0.0f;
    const double flop = 2.0 * M * N * K;

    // 参照：cuBLAS 单精度（行主序的 C = AB 等于列主序的 Cᵀ = BᵀAᵀ）；CPU 抽样核对
    auto sgemm = [&] { CHECK_BLAS(cublasSgemm(h, CUBLAS_OP_N, CUBLAS_OP_N, N, M, K, &one, B, N, A, K, &zero, Cm, N)); };
    CHECK_BLAS(cublasSetMathMode(h, CUBLAS_DEFAULT_MATH));
    float t_sgemm = time_ms(sgemm, 10);
    CHECK(cudaMemcpy(ref.data(), Cm, mn * 4, cudaMemcpyDeviceToHost));
    bool ok = true;
    for (int s = 0; s < 4096; s++) {
        size_t idx = splitmix64(s + (5ull << 40)) % mn;
        int r = int(idx / N), c = int(idx % N);
        double acc = 0.0;
        for (int k = 0; k < K; k++) acc += double(hA[size_t(r) * K + k]) * hB[size_t(k) * N + c];
        ok = ok && acc == ref[idx];
    }
    std::printf("{\"n\": %d", n);
    auto report = [&](const char* name, float ms) {
        CHECK(cudaMemcpy(got.data(), Cm, mn * 4, cudaMemcpyDeviceToHost));
        bool same = true;
        for (size_t i = 0; i < mn && same; i++) same = got[i] == ref[i];
        ok = ok && same;
        std::printf(", \"%s_ms\": %.3f, \"%s_GFs\": %.1f", name, ms, name, flop / (ms * 1e-3) / 1e9);
        if (!same) std::fprintf(stderr, "%s 的结果与 cuBLAS 不同\n", name);
    };
    report("cublas", t_sgemm);
    CHECK_BLAS(cublasSetMathMode(h, CUBLAS_TF32_TENSOR_OP_MATH));
    CHECK(cudaMemset(Cm, 0xFF, mn * 4));
    report("cublas_tf32", time_ms(sgemm, 10));
    CHECK_BLAS(cublasSetMathMode(h, CUBLAS_DEFAULT_MATH));
    CHECK(cudaMemset(Cm, 0xFF, mn * 4));
    report("cublas_h", time_ms([&] {
        CHECK_BLAS(cublasGemmEx(h, CUBLAS_OP_N, CUBLAS_OP_N, N, M, K, &one, Bh, CUDA_R_16F, N, Ah, CUDA_R_16F, K, &zero, Cm, CUDA_R_32F, N,
                                CUBLAS_COMPUTE_32F, CUBLAS_GEMM_DEFAULT));
    }, 10));

    const dim3 b2(32, 8), g_rowx(M / 32, N / 8), g_col(N / 32, M / 8), b32(T, T), g32(N / T, M / T), g128(N / BN, M / BM);
    auto run = [&](const char* name, int reps, auto launch) {
        CHECK(cudaMemset(Cm, 0xFF, mn * 4));
        report(name, time_ms(launch, reps));
    };
    run("naive_rowx", 3, [&] { naive_rowx<<<g_rowx, b2>>>(M, N, K, A, B, Cm); });
    run("naive", 3, [&] { naive<<<g_col, b2>>>(M, N, K, A, B, Cm); });
    run("tiled", 10, [&] { tiled<<<g32, b32>>>(M, N, K, A, B, Cm); });
    run("regtile", 10, [&] { regtile<<<g128, NT>>>(M, N, K, A, B, Cm); });
    run("vec", 10, [&] { vec<<<g128, NT>>>(M, N, K, A, B, Cm); });
    run("dbuf", 10, [&] { dbuf<<<g128, NT>>>(M, N, K, A, B, Cm); });
    run("wmma", 10, [&] { wmma_gemm<<<g128, NT>>>(M, N, K, Ah, Bh, Cm); });
    // 每个线程实际用了几个寄存器、有没有溢出到本地内存（5.9 节）
    auto regs = [&](const char* name, const void* f) {
        cudaFuncAttributes a;
        CHECK(cudaFuncGetAttributes(&a, f));
        std::printf(", \"%s_regs\": %d, \"%s_spill\": %zu", name, a.numRegs, name, a.localSizeBytes);
    };
    regs("regtile", (const void*)regtile);
    regs("vec", (const void*)vec);
    regs("dbuf", (const void*)dbuf);
    regs("wmma", (const void*)wmma_gemm);
    std::printf(", \"correct\": %s}\n", ok ? "true" : "false");
    CHECK_BLAS(cublasDestroy(h));
    CHECK(cudaFree(A));
    CHECK(cudaFree(B));
    CHECK(cudaFree(Cm));
    CHECK(cudaFree(Ah));
    CHECK(cudaFree(Bh));
    return 0;
}
