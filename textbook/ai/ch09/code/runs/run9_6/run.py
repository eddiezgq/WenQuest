"""程序 9.6.2：FlashAttention 与标准注意力的速度与显存（9.6 节）。A10，半精度，因果注意力，头维 d_h = 64、6 个头，
每批共 8192 个词元：T = 256（B = 32，小型 Transformer 的训练批）、T = 1024（B = 8）、T = 4096（B = 2）。
三种做法各做一次前向加反向：标准写法（矩阵乘法、缩放、掩码、softmax、矩阵乘法，与第 7 章 model.py 相同）；
PyTorch 的 scaled_dot_product_attention 指定数学后端（等价于标准写法）与 FlashAttention 后端。
记录耗时（中位数）与显存峰值，并与标准写法的输出核对。结果写进 out.json（第 14 轮附 4.4 节）。"""
import json
import math

import torch
from torch.nn import functional as F

dev, dt = "cuda", torch.float16
torch.manual_seed(0)
try:
    from torch.nn.attention import SDPBackend, sdpa_kernel
    BACK = {"math": lambda: sdpa_kernel(SDPBackend.MATH), "flash": lambda: sdpa_kernel(SDPBackend.FLASH_ATTENTION)}
except ImportError:                                         # 较老的 PyTorch
    BACK = {"math": lambda: torch.backends.cuda.sdp_kernel(enable_flash=False, enable_math=True, enable_mem_efficient=False),
            "flash": lambda: torch.backends.cuda.sdp_kernel(enable_flash=True, enable_math=False, enable_mem_efficient=False)}


MASK = {}                                                   # 掩码事先建好，不计入耗时


def eager(q, k, v):
    T = q.shape[-2]
    s = (q @ k.transpose(-2, -1)) * (1 / math.sqrt(q.shape[-1]))
    s = s.masked_fill(MASK[T], float("-inf"))
    return s.softmax(-1) @ v


def sdpa(name):
    def f(q, k, v):
        with BACK[name]():
            return F.scaled_dot_product_attention(q, k, v, is_causal=True)
    return f


def measure(fn, q, k, v, g, reps=20):
    def step():
        q.grad = k.grad = v.grad = None
        fn(q, k, v).backward(g)
    for _ in range(3):
        step()
    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()
    base = torch.cuda.memory_allocated()
    e0, e1 = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
    ts = []
    for _ in range(reps):
        e0.record()
        step()
        e1.record()
        e1.synchronize()
        ts.append(e0.elapsed_time(e1))
    return sorted(ts)[reps // 2], (torch.cuda.max_memory_allocated() - base) / 1e6


out = {"torch": torch.__version__}
for T, B in ((256, 32), (1024, 8), (4096, 2)):
    q, k, v = (torch.randn(B, 6, T, 64, device=dev, dtype=dt, requires_grad=True) for _ in range(3))
    g = torch.randn(B, 6, T, 64, device=dev, dtype=dt)
    MASK[T] = torch.triu(torch.ones(T, T, dtype=torch.bool, device=dev), 1)
    with torch.no_grad():
        ref = eager(q, k, v).float()
        for name in ("math", "flash"):
            out[f"err_{name}_{T}"] = (sdpa(name)(q, k, v).float() - ref).abs().max().item()
    for name, fn in (("eager", eager), ("math", sdpa("math")), ("flash", sdpa("flash"))):
        out[f"{name}_{T}_ms"], out[f"{name}_{T}_MB"] = measure(fn, q, k, v, g)
    out[f"speed_{T}"] = out[f"eager_{T}_ms"] / out[f"flash_{T}_ms"]
    del q, k, v, g, ref, MASK[T]
    torch.cuda.empty_cache()
json.dump(out, open("out.json", "w"))                      # 先写结果，核对不过时也留下数据便于查看
print(out)
assert all(out[f"err_{n}_{T}"] < 2e-2 for n in ("math", "flash") for T in (256, 1024, 4096)), "与标准写法的差别过大"
