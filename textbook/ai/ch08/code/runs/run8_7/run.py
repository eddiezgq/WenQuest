"""程序 8.7.3：Triton 融合核函数与 PyTorch 急切执行、torch.compile 的比较（8.7 节）。单精度，A10。
- 注意力的“缩放 + 因果掩码 + softmax”：小型 Transformer 训练时 B·h·T = 49 152 行、每行 T = 256 个分数；另测 T = 1024
  （B·h = 48，共 49 152 行）。急切执行是三个运算 (S * scale).masked_fill(mask, −∞).softmax(−1)，掩码只有 T × T，按头广播。
- “残差加法 + 层归一化”：8192 行 × 384（小型 Transformer 的残差流）；另测 8192 行 × 4096。急切执行是 x + r 与 layer_norm 两个运算。
另测程序 8.6.1 的向量加法（2²⁶ 个数）与 PyTorch 的加法。
每种做法先与急切执行的结果核对，再取 50 次的中位数；按融合后“只读写一遍”的字节数算出达到的显存带宽（急切执行实际搬得更多）。
结果写进 out.json（第 14 轮附 4.4 节）。"""
import json
import math

import torch
from torch.nn import functional as F

import prep

prep.python_headers()                                       # Triton 编译它的启动代码要 Python.h
import add  # noqa: E402
import kernels  # noqa: E402

dev = "cuda"
torch.manual_seed(0)


def timeit(fn, reps=50):
    for _ in range(5):
        fn()
    e0, e1 = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
    ts = []
    for _ in range(reps):
        e0.record()
        fn()
        e1.record()
        e1.synchronize()
        ts.append(e0.elapsed_time(e1) * 1e3)
    ts.sort()
    return ts[len(ts) // 2]


def eager_attn(s, mask, scale):
    """s：(B·h·T, T)；mask：(T, T)，按头广播（与 model.py 相同），不展开成整个 s 那么大。"""
    T = mask.shape[0]
    return (s.view(-1, T, T) * scale).masked_fill(mask, float("-inf")).softmax(dim=-1).view(s.shape)


def eager_add_ln(x, r, w, b):
    s = x + r
    return s, F.layer_norm(s, (s.shape[-1],), w, b)


def compiled(f):
    return torch.compile(f, dynamic=False)                  # 每种形状各编译一份，不用动态形状的版本
out = {"torch": torch.__version__}
scale = 1 / math.sqrt(64)
for tag, (bh, T) in {"a256": (192, 256), "a1k": (48, 1024)}.items():
    s = torch.randn(bh * T, T, device=dev)
    mask = torch.triu(torch.ones(T, T, dtype=torch.bool, device=dev), 1)
    torch._dynamo.reset()
    c_attn = compiled(eager_attn)
    ref = eager_attn(s, mask, scale)
    assert torch.allclose(kernels.attn_softmax(s, T, scale), ref, rtol=1e-4, atol=1e-6)   # GPU 上的 exp 与除法是近似指令
    assert torch.allclose(c_attn(s, mask, scale), ref, rtol=1e-4, atol=1e-6)
    nbytes = 2 * s.numel() * 4
    for k, fn in (("eager", lambda: eager_attn(s, mask, scale)), ("triton", lambda: kernels.attn_softmax(s, T, scale)),
                  ("compile", lambda: c_attn(s, mask, scale))):
        t = timeit(fn)
        out[f"{tag}_{k}_us"], out[f"{tag}_{k}_GBs"] = t, nbytes / t / 1e3
for tag, (rows, n) in {"ln384": (8192, 384), "ln4k": (8192, 4096)}.items():
    x, r = torch.randn(rows, n, device=dev), torch.randn(rows, n, device=dev)
    w, b = torch.randn(n, device=dev), torch.randn(n, device=dev)
    torch._dynamo.reset()
    c_add_ln = compiled(eager_add_ln)
    s_ref, y_ref = eager_add_ln(x, r, w, b)
    s_t, y_t = kernels.add_layernorm(x, r, w, b)
    s_c, y_c = c_add_ln(x, r, w, b)
    assert torch.equal(s_t, s_ref) and (y_t - y_ref).abs().max().item() < 1e-4 and (y_c - y_ref).abs().max().item() < 1e-4
    nbytes = 4 * x.numel() * 4                              # 读 x、r，写 s、y
    for k, fn in (("eager", lambda: eager_add_ln(x, r, w, b)), ("triton", lambda: kernels.add_layernorm(x, r, w, b)),
                  ("compile", lambda: c_add_ln(x, r, w, b))):
        t = timeit(fn)
        out[f"{tag}_{k}_us"], out[f"{tag}_{k}_GBs"] = t, nbytes / t / 1e3
# 程序 8.6.1 的向量加法：2²⁶ 个单精度数，读两个数组写一个
x, y = torch.randn(1 << 26, device=dev), torch.randn(1 << 26, device=dev)
assert torch.equal(add.add(x, y), x + y)
for k, fn in (("torch", lambda: x + y), ("triton", lambda: add.add(x, y))):
    t = timeit(fn)
    out[f"add_{k}_us"], out[f"add_{k}_GBs"] = t, 3 * x.numel() * 4 / t / 1e3
out["correct"] = True
json.dump(out, open("out.json", "w"))
print(out)
