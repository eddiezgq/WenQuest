"""程序 7.7.1：融合的“加偏置 + GELU”自定义 CUDA 算子（7.7 节）。
y = GELU(x + b)，GELU 用 tanh 近似（与 2.9 节、PyTorch 的 F.gelu(approximate="tanh") 相同）；x 的最后一维长 f，b 长 f。
- CUDA 源程序：前向、反向各一个核函数，按 x 的元素逐个计算；用 AT_DISPATCH_FLOATING_TYPES 为 float 与 double 各生成一份
  （double 用来做梯度检查）；核函数发在 PyTorch 当前的流上。
- torch.utils.cpp_extension.load_inline 在第一次导入时调用 nvcc 编译（约一分钟），以后用缓存。
- BiasGelu 是一个 torch.autograd.Function：前向保存 x 与 b，反向用第二个核函数算 dx，偏置的梯度是 dx 按最后一维以外的各维求和。"""
import torch
from torch.utils.cpp_extension import load_inline

CUDA_SRC = r"""
#include <ATen/cuda/CUDAContext.h>
#include <torch/extension.h>

template <typename T> __device__ __forceinline__ T gelu_parts(T t, T* d) {
    const T c = 0.7978845608028654, a = 0.044715;              // √(2/π)
    T u = tanh(c * (t + a * t * t * t));
    *d = T(0.5) * (T(1) + u) + T(0.5) * t * (T(1) - u * u) * c * (T(1) + T(3) * a * t * t);   // GELU 的导数
    return T(0.5) * t * (T(1) + u);
}

template <typename T> __global__ void fwd_kernel(const T* x, const T* b, T* y, int64_t n, int64_t f) {
    for (int64_t i = blockIdx.x * (int64_t)blockDim.x + threadIdx.x; i < n; i += (int64_t)gridDim.x * blockDim.x) {
        T d;
        y[i] = gelu_parts(x[i] + b[i % f], &d);
    }
}

template <typename T> __global__ void bwd_kernel(const T* dy, const T* x, const T* b, T* dx, int64_t n, int64_t f) {
    for (int64_t i = blockIdx.x * (int64_t)blockDim.x + threadIdx.x; i < n; i += (int64_t)gridDim.x * blockDim.x) {
        T d;
        gelu_parts(x[i] + b[i % f], &d);
        dx[i] = dy[i] * d;
    }
}

static void check(const torch::Tensor& t) {
    TORCH_CHECK(t.is_cuda(), "要在 GPU 上");
    TORCH_CHECK(t.is_contiguous(), "要连续存放");
}

static int blocks(int64_t n) { return (int)std::min<int64_t>((n + 255) / 256, 65535); }

torch::Tensor forward(torch::Tensor x, torch::Tensor b) {
    check(x); check(b);
    TORCH_CHECK(b.dim() == 1 && x.size(-1) == b.size(0), "b 的长度要等于 x 的最后一维");
    auto y = torch::empty_like(x);
    int64_t n = x.numel(), f = b.size(0);
    auto stream = at::cuda::getCurrentCUDAStream();
    AT_DISPATCH_FLOATING_TYPES(x.scalar_type(), "bias_gelu_fwd", [&] {
        fwd_kernel<scalar_t><<<blocks(n), 256, 0, stream>>>(x.data_ptr<scalar_t>(), b.data_ptr<scalar_t>(), y.data_ptr<scalar_t>(), n, f);
    });
    C10_CUDA_KERNEL_LAUNCH_CHECK();
    return y;
}

torch::Tensor backward(torch::Tensor dy, torch::Tensor x, torch::Tensor b) {
    check(dy); check(x); check(b);
    auto dx = torch::empty_like(x);
    int64_t n = x.numel(), f = b.size(0);
    auto stream = at::cuda::getCurrentCUDAStream();
    AT_DISPATCH_FLOATING_TYPES(x.scalar_type(), "bias_gelu_bwd", [&] {
        bwd_kernel<scalar_t><<<blocks(n), 256, 0, stream>>>(dy.data_ptr<scalar_t>(), x.data_ptr<scalar_t>(), b.data_ptr<scalar_t>(),
                                                            dx.data_ptr<scalar_t>(), n, f);
    });
    C10_CUDA_KERNEL_LAUNCH_CHECK();
    return dx;
}
"""
CPP_SRC = "torch::Tensor forward(torch::Tensor x, torch::Tensor b);\ntorch::Tensor backward(torch::Tensor dy, torch::Tensor x, torch::Tensor b);"

ext = load_inline(name="wq_bias_gelu", cpp_sources=CPP_SRC, cuda_sources=CUDA_SRC, functions=["forward", "backward"],
                  extra_cuda_cflags=["-O3"], verbose=False)


class BiasGelu(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, b):
        x, b = x.contiguous(), b.contiguous()
        ctx.save_for_backward(x, b)
        return ext.forward(x, b)

    @staticmethod
    def backward(ctx, dy):
        x, b = ctx.saved_tensors
        dx = ext.backward(dy.contiguous(), x, b)
        return dx, dx.sum(dim=tuple(range(dx.dim() - 1)))


def bias_gelu(x, b):
    return BiasGelu.apply(x, b)
