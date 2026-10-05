"""程序 8.6.1：Triton 的第一个程序——向量加法（8.6 节）。与第 4 章 CUDA 的向量加法对照：
CUDA 的核函数写的是“一个线程做什么”，Triton 的核函数写的是“一个程序实例处理一块数据（BLOCK 个元素）做什么”，
块内怎样分给线程、怎样合并访问、用不用向量化的读写，由 Triton 的编译器决定。"""
import torch
import triton
import triton.language as tl


@triton.jit
def add_kernel(x_ptr, y_ptr, z_ptr, n, BLOCK: tl.constexpr):
    pid = tl.program_id(0)                       # 第几个程序实例（相当于 CUDA 的 blockIdx.x）
    offs = pid * BLOCK + tl.arange(0, BLOCK)     # 这个实例负责的 BLOCK 个下标：一个向量，不是一个数
    mask = offs < n                              # 最后一块可能不满：越界的位置不读不写
    x = tl.load(x_ptr + offs, mask=mask)
    y = tl.load(y_ptr + offs, mask=mask)
    tl.store(z_ptr + offs, x + y, mask=mask)


def add(x, y, BLOCK=1024):
    z = torch.empty_like(x)
    n = x.numel()
    add_kernel[(triton.cdiv(n, BLOCK),)](x, y, z, n, BLOCK=BLOCK)   # 网格：几个程序实例
    return z
