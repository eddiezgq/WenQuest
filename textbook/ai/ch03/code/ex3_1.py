"""算例 3.1.1～3.1.3：检测工位相机的数据并行；归约求和的工作量与跨度；浮点加法的顺序改变结果。

式 (3.1.1)：工作量 W、跨度 S 的计算，在 p 个处理器上 max(W/p, S) ≤ T_p ≤ W/p + S（布伦特定理）。
树形归约：n 个数求和，W = n − 1 次加法，S = ⌈log₂ n⌉ 层。
"""
import math

import numpy as np

from bookout import out

# 算例 3.1.1：数字工厂检测工位的相机，3840 × 2160 像素，每秒 60 帧；每个像素做一次 3×3 滤波（9 次乘加 = 18 FLOP）
# 再与阈值比较（1 FLOP）。像素之间互不依赖：数据并行。
W_px, H_px, fps = 3840, 2160, 60
px = W_px * H_px
flop_px = 9 * 2 + 1
rate = px * fps * flop_px
budget_ms = 1000 / fps

# 算例 3.1.2：归约求和
n = 2 ** 20
W = n - 1
S = math.ceil(math.log2(n))
bounds = {}
for p in (1, 128, 16896, 2 ** 20):
    bounds[p] = (max(W / p, S), W / p + S)
speedup_h100 = W / bounds[16896][1]                     # 用上界估计的加速比


def tree_sum(x):
    """逐层两两相加，每层所有加法互相独立（可以并行），共 ⌈log₂ n⌉ 层。"""
    x = x.copy()
    levels = 0
    while len(x) > 1:
        if len(x) % 2:
            x = np.append(x, x.dtype.type(0))
        x = x[0::2] + x[1::2]
        levels += 1
    return x[0], levels


# 算例 3.1.3：单精度下顺序相加与树形相加 2^20 个 0.1
v = np.full(n, 0.1, dtype=np.float32)
exact = float(np.float64(np.float32(0.1)) * n)             # 每个数实际存的是 float32(0.1)
seq = np.float32(0)
for chunk in np.split(v, 64):                              # 逐个相加（分块只为省时间，块内仍逐个累加）
    for a in chunk:
        seq = np.float32(seq + a)
tree, levels = tree_sum(v)
assert levels == S
err_seq = abs(float(seq) - exact)
err_tree = abs(float(tree) - exact)

out(W_px=W_px, H_px=H_px, fps=fps, px_M=px / 1e6, flop_px=flop_px, rate_G=rate / 1e9, budget_ms=budget_ms,
    n=n, n_e="2^{20}", W=W, S=S, b1_lo=bounds[1][0], b128_lo=bounds[128][0], b128_hi=bounds[128][1],
    bh_lo=bounds[16896][0], bh_hi=bounds[16896][1], bn_lo=bounds[2 ** 20][0], bn_hi=bounds[2 ** 20][1], speedup_h100=speedup_h100,
    exact=exact, seq=float(seq), tree=float(tree), err_seq=err_seq, err_tree=err_tree)
