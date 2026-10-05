# GPU 实验 8.7 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 8.7　用 Triton 写融合的 softmax
# %%
import sys; sys.path.insert(0, "..")
import math
import torch
import wqgpu
env = wqgpu.check(("gpu", "torch", "triton"))
# %% [markdown]
# ## 1. 第一个 Triton 程序：向量加法
# 打开 `add.py`：核函数写的是“一个程序实例处理 BLOCK 个元素”。
# %%
import add
x, y = torch.randn(1 << 26, device="cuda"), torch.randn(1 << 26, device="cuda")
assert torch.equal(add.add(x, y), x + y)
for B in (256, 1024, 4096):
    t = wqgpu.bench(lambda: add.add(x, y, BLOCK=B), sync=torch.cuda.synchronize) * 1e6
    print(f"BLOCK = {B}：{t:.0f} μs，{3 * x.numel() * 4 / t / 1e3:.0f} GB/s")
t_add = wqgpu.bench(lambda: add.add(x, y), sync=torch.cuda.synchronize) * 1e6
# %% [markdown]
# ## 2. 融合的“缩放 + 因果掩码 + softmax”（任务 1）
# `kernels.py` 中的 `attn_softmax_kernel`：每个程序实例处理注意力分数的一行。与急切执行的三个运算比较。
# %%
import kernels
T, bh = 256, 192
s = torch.randn(bh * T, T, device="cuda")
mask = torch.triu(torch.ones(T, T, dtype=torch.bool, device="cuda"), 1)          # 只有 T × T，按头广播
scale = 1 / math.sqrt(64)
attn = lambda s: (s.view(-1, T, T) * scale).masked_fill(mask, float("-inf")).softmax(dim=-1).view(s.shape)
eager = lambda: attn(s)
assert torch.allclose(kernels.attn_softmax(s, T, scale), eager(), rtol=1e-4, atol=1e-6)
t_eager = wqgpu.bench(eager, sync=torch.cuda.synchronize) * 1e6
t_tri = wqgpu.bench(lambda: kernels.attn_softmax(s, T, scale), sync=torch.cuda.synchronize) * 1e6
comp = torch.compile(attn, dynamic=False)
t_comp = wqgpu.bench(lambda: comp(s), sync=torch.cuda.synchronize) * 1e6
nbytes = 2 * s.numel() * 4
print(f"急切执行 {t_eager:.0f} μs，Triton {t_tri:.0f} μs（{nbytes / t_tri / 1e3:.0f} GB/s），torch.compile {t_comp:.0f} μs")
# %% [markdown]
# ## 3. 改一改（任务 2）
# 试几个 `num_warps`（2、4、8），以及更长的行（T = 1024、4096）：什么时候整行放不进寄存器、速度明显下降？
# %%
for w in (2, 4, 8):
    t = wqgpu.bench(lambda: kernels.attn_softmax(s, T, scale, num_warps=w), sync=torch.cuda.synchronize) * 1e6
    print(f"num_warps = {w}：{t:.0f} μs")
for T2 in (1024, 4096):
    s2 = torch.randn(48 * T2 if T2 == 1024 else 4 * T2, T2, device="cuda")
    t = wqgpu.bench(lambda: kernels.attn_softmax(s2, T2, scale), sync=torch.cuda.synchronize) * 1e6
    print(f"T = {T2}：{t:.0f} μs，{2 * s2.numel() * 4 / t / 1e3:.0f} GB/s")
# %% [markdown]
# ## 4. 自己写一个：融合的“加偏置 + GELU”（任务 3）
# 仿照 `add.py`，写一个核函数：y = GELU(x + b)（tanh 近似），x 形状 (8192, 1536)，b 长 1536。与 GPU 实验 7.7 的 CUDA 版本比较。
# 提示：`tl.math` 里没有 tanh 时，可用 tanh(u) = 2·sigmoid(2u) − 1。
# %%
# 在这里写你的核函数
# %% [markdown]
# ## 5. 回传结果
# %%
wqgpu.submit(add_us=t_add, eager_us=t_eager, triton_us=t_tri, compile_us=t_comp, triton_GBs=nbytes / t_tri / 1e3)
