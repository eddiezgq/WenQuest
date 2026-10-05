"""程序 8.7.2：用 Triton 写的两个融合核函数（8.7 节）。
- 注意力的“缩放 + 因果掩码 + softmax”：输入是注意力分数 S（形状 (B·h·T, T)，第 r 行是某个头里第 r mod T 个位置对各位置的分数），
  每个程序实例处理一行：整行读进来（BLOCK 取不小于行长的 2 的幂，越界与被掩掉的位置当作 −∞），乘以缩放因子，
  减去最大值、取指数、求和、相除，一次读、一次写。PyTorch 急切执行要三个核函数（缩放、掩码、softmax），各读写一遍。
- “残差加法 + 层归一化”：s = x + r，y = LN(s)·γ + β；每个程序实例处理一行，一次读 x 与 r，写 s（下一层的残差流）与 y。
  急切执行要两个核函数（加法、层归一化）。
开发时可设环境变量 TRITON_INTERPRET=1，在 CPU 上逐个程序实例解释执行，与 PyTorch 的结果核对。"""
import torch
import triton
import triton.language as tl


@triton.jit
def attn_softmax_kernel(s_ptr, p_ptr, stride, n, T, scale, BLOCK: tl.constexpr):
    row = tl.program_id(0)                               # 第几个程序实例 = 第几行
    pos = row % T                                        # 这一行是第几个位置：只能看它自己和之前的位置
    cols = tl.arange(0, BLOCK)                           # 这一行的各列：一个块，Triton 自己把它分给线程
    keep = (cols < n) & (cols <= pos)
    x = tl.load(s_ptr + row * stride + cols, mask=cols < n, other=0.0).to(tl.float32) * scale   # 在 FP32 中计算
    x = tl.where(keep, x, -float("inf"))
    x = x - tl.max(x, axis=0)
    e = tl.exp(x)
    tl.store(p_ptr + row * stride + cols, e / tl.sum(e, axis=0), mask=cols < n)


def attn_softmax(s, T, scale, num_warps=None):
    rows, n = s.shape
    p = torch.empty_like(s)
    BLOCK = triton.next_power_of_2(n)
    attn_softmax_kernel[(rows,)](s, p, s.stride(0), n, T, scale, BLOCK=BLOCK, num_warps=num_warps or (4 if BLOCK <= 2048 else 8))
    return p


@triton.jit
def add_layernorm_kernel(x_ptr, r_ptr, s_ptr, y_ptr, w_ptr, b_ptr, stride, n, eps, BLOCK: tl.constexpr):
    row = tl.program_id(0)
    cols = tl.arange(0, BLOCK)
    mask = cols < n
    s = (tl.load(x_ptr + row * stride + cols, mask=mask, other=0.0).to(tl.float32)
         + tl.load(r_ptr + row * stride + cols, mask=mask, other=0.0).to(tl.float32))     # 归约在 FP32 中做
    tl.store(s_ptr + row * stride + cols, s, mask=mask)
    mean = tl.sum(s, axis=0) / n
    d = tl.where(mask, s - mean, 0.0)
    rstd = 1 / tl.sqrt(tl.sum(d * d, axis=0) / n + eps)
    w = tl.load(w_ptr + cols, mask=mask)
    b = tl.load(b_ptr + cols, mask=mask)
    tl.store(y_ptr + row * stride + cols, d * rstd * w + b, mask=mask)


def add_layernorm(x, r, w, b, eps=1e-5):
    rows, n = x.shape
    s, y = torch.empty_like(x), torch.empty_like(x)
    BLOCK = triton.next_power_of_2(n)
    add_layernorm_kernel[(rows,)](x, r, s, y, w, b, x.stride(0), n, eps, BLOCK=BLOCK, num_warps=4 if BLOCK <= 1024 else 8)
    return s, y
