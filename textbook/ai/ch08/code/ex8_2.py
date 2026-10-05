"""算例 8.2.1、8.2.2：半精度训练中梯度的下溢与损失缩放。
（1）设一批梯度的绝对值按对数正态分布：log₁₀|g| ~ N(−6, 1.5²)（梯度大多很小，跨好几个数量级——这是混合精度训练的论文中
    实测的激活梯度直方图的大致形状，这里只作示意）。存成 FP16 时：多少变成 0（比最小次正规数的一半还小）、多少落进次正规数
    （有效位数不足）；乘以损失缩放因子 S = 2^k 再存，下溢与上溢（超过 65504）各多少。BF16 与 FP32 的指数范围相同，同样的梯度几乎不下溢。
（2）动态损失缩放（PyTorch GradScaler 的默认做法）：S 从 2¹⁶ 开始；某一步的梯度出现无穷或 NaN，就跳过这一步、S 减半；
    连续 2000 步正常，S 加倍。模拟 20 000 步，每步梯度的最大值随训练缓慢变化并偶有尖峰，数一数跳过了几步、S 稳定在多少。"""
import numpy as np

from _ch8 import FMTS
from bookout import out

rng = np.random.default_rng(82)
g = 10.0 ** rng.normal(-6, 1.5, 1_000_000)
f16, b16 = FMTS["FP16"], FMTS["BF16"]


def fractions(x, f):
    under = np.mean(x < f.min_sub / 2) * 100
    sub = np.mean((x >= f.min_sub / 2) & (x < f.min_normal)) * 100
    over = np.mean(x > f.max) * 100
    return under, sub, over


res = {}
for k in (0, 8, 16, 24):
    u, s, o = fractions(g * 2.0 ** k, f16)
    res[f"u{k}"], res[f"s{k}"], res[f"o{k}"] = u, s, o
ub, sb, ob = fractions(g, b16)

# （2）动态损失缩放
steps = 20000
gmax = 10.0 ** (-1.0 + 0.5 * np.sin(np.arange(steps) / 3000.0)) * np.where(rng.random(steps) < 0.002, 1e2, 1.0)   # 每步梯度绝对值的最大值
S, good, skipped, hist = 2.0 ** 16, 0, 0, []
for t in range(steps):
    if gmax[t] * S > f16.max:          # 缩放后的梯度溢出：跳过这一步，S 减半
        skipped += 1
        S /= 2
        good = 0
    else:
        good += 1
        if good == 2000:
            S *= 2
            good = 0
    hist.append(S)
out(**res, ub=ub, sb=sb, skipped=skipped, skipped_pct=100 * skipped / steps, S_end_log2=float(np.log2(hist[-1])),
    S_min_log2=float(np.log2(min(hist))), S_max_log2=float(np.log2(max(hist))))
