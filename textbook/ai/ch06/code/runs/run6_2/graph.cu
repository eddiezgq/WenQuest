// 程序 6.2.1：启动开销与 CUDA 图（6.2 节）。一个只有 1024 个数的小核函数（每个数加 1），连续启动 N = 1000 次：
//   stream   ：在一个流里逐个启动，测两个事件之间平均每个核函数占的时间——它是“GPU 执行一个核函数的时间”与“主机发出一次启动的间隔”
//              中较大的一个；另外测主机连续发出 200 次启动、平均每次花的时间（200 次，免得排满驱动的启动队列而被阻塞）
//   graph    ：把这 1000 次启动捕获成一个 CUDA 图，一次提交
//   roundtrip：启动一次就同步一次（主机等 GPU 做完），一个来回的时间
// 需要 CUDA 12 及以上（cudaGraphInstantiate 的三参数形式）。编译：nvcc -O3 -arch=native -o graph graph.cu
#include <chrono>
#include <cstdio>
#include "bench.cuh"

constexpr int N = 1000, LEN = 1024;

__global__ void add1(float* x) { x[threadIdx.x + blockIdx.x * blockDim.x] += 1.0f; }

int main() {
    float* x;
    CHECK(cudaMalloc(&x, LEN * sizeof(float)));
    CHECK(cudaMemset(x, 0, LEN * sizeof(float)));
    cudaStream_t s;
    CHECK(cudaStreamCreate(&s));
    long launches = 0;
    auto many = [&] {
        for (int i = 0; i < N; i++) add1<<<LEN / 256, 256, 0, s>>>(x);
        launches += N;
    };
    // GPU 上的时间：事件记在同一个流里
    auto gpu_ms = [&](auto fn) {
        cudaEvent_t a, b;
        CHECK(cudaEventCreate(&a));
        CHECK(cudaEventCreate(&b));
        fn();                                                    // 预热
        CHECK(cudaStreamSynchronize(s));
        std::vector<float> v(7);
        for (float& m : v) {
            CHECK(cudaEventRecord(a, s));
            fn();
            CHECK(cudaEventRecord(b, s));
            CHECK(cudaEventSynchronize(b));
            CHECK(cudaEventElapsedTime(&m, a, b));
        }
        CHECK(cudaEventDestroy(a));
        CHECK(cudaEventDestroy(b));
        std::sort(v.begin(), v.end());
        return v[3];
    };
    float t_stream = gpu_ms(many);
    // 主机每次启动花的时间（只算发出命令，不等 GPU）
    const int NE = 200;
    auto h0 = std::chrono::steady_clock::now();
    for (int i = 0; i < NE; i++) add1<<<LEN / 256, 256, 0, s>>>(x);
    double enqueue_us = std::chrono::duration<double, std::micro>(std::chrono::steady_clock::now() - h0).count() / NE;
    launches += NE;
    CHECK(cudaStreamSynchronize(s));
    // CUDA 图：捕获 N 次启动
    cudaGraph_t g;
    cudaGraphExec_t ge;
    CHECK(cudaStreamBeginCapture(s, cudaStreamCaptureModeGlobal));
    for (int i = 0; i < N; i++) add1<<<LEN / 256, 256, 0, s>>>(x);
    CHECK(cudaStreamEndCapture(s, &g));
    CHECK(cudaGraphInstantiate(&ge, g, 0));
    float t_graph = gpu_ms([&] { CHECK(cudaGraphLaunch(ge, s)); launches += N; });
    // 一个来回：启动后马上同步
    auto r0 = std::chrono::steady_clock::now();
    for (int i = 0; i < N; i++) {
        add1<<<LEN / 256, 256, 0, s>>>(x);
        CHECK(cudaStreamSynchronize(s));
    }
    launches += N;
    double roundtrip_us = std::chrono::duration<double, std::micro>(std::chrono::steady_clock::now() - r0).count() / N;
    CHECK(cudaGetLastError());
    std::vector<float> hx(LEN);
    CHECK(cudaMemcpy(hx.data(), x, LEN * sizeof(float), cudaMemcpyDeviceToHost));
    bool ok = true;
    for (float v : hx) ok = ok && v == float(launches);         // 每次启动每个数加 1，总数精确（小于 2^24）
    std::printf("{\"n\": %d, \"stream_us\": %.2f, \"graph_us\": %.2f, \"enqueue_us\": %.2f, \"roundtrip_us\": %.2f, \"correct\": %s}\n",
                N, t_stream * 1e3 / N, t_graph * 1e3 / N, enqueue_us, roundtrip_us, ok ? "true" : "false");
    CHECK(cudaGraphExecDestroy(ge));
    CHECK(cudaGraphDestroy(g));
    CHECK(cudaStreamDestroy(s));
    CHECK(cudaFree(x));
    return 0;
}
