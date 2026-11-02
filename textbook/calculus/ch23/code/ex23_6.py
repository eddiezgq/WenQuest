"""23.6 节：级数求和的数值方法与加速。
(1) 莱布尼茨级数求 π：直接求和、相邻部分和取平均（反复平均）、艾特肯 Δ² 加速（反复使用）的误差；
(2) 梅钦公式 π = 16 arctan(1/5) − 4 arctan(1/239)：几项就够；
(3) Σ1/k² 加上余项的积分修正（欧拉–麦克劳林）：S_n + 1/n − 1/(2n²) + 1/(6n³)；
(4) 单精度下卡亨补偿求和。"""
import math

import numpy as np

from bookout import T, out


def leib(n):
    """4 × 前 n 项部分和，n = 1, 2, …"""
    S, out_ = 0.0, []
    for k in range(n):
        S += (-1) ** k / (2 * k + 1)
        out_.append(4 * S)
    return out_


def aitken(s):
    return [s[i + 2] - (s[i + 2] - s[i + 1]) ** 2 / ((s[i + 2] - s[i + 1]) - (s[i + 1] - s[i])) for i in range(len(s) - 2)]


def averages(s, times):
    for _ in range(times):
        s = [(s[i] + s[i + 1]) / 2 for i in range(len(s) - 1)]
    return s


n = 10
s = leib(n)
rows = []
rows.append(f"| {T('直接求和', 'plain partial sum')} | {abs(s[-1] - math.pi):.1e} |")
rows.append(f"| {T('相邻两个平均一次', 'average of neighbours, once')} | {abs(averages(s, 1)[-1] - math.pi):.1e} |")
rows.append(f"| {T('反复平均 9 次', 'averaged 9 times')} | {abs(averages(s, 9)[-1] - math.pi):.1e} |")
a = s
for j in range(4):
    a = aitken(a)
    rows.append(f"| {T(f'艾特肯加速 {j + 1} 次', f'Aitken, {j + 1} time(s)')} | {abs(a[-1] - math.pi):.1e} |")
out(pi_tab="\n".join(rows), pi_n=n)
# 直接求和要达到艾特肯 4 次的精度需要多少项（误差约 1/n）
out(pi_need=1 / abs(a[-1] - math.pi))
# 梅钦公式


def atan_series(x, m):
    return sum((-1) ** k * x ** (2 * k + 1) / (2 * k + 1) for k in range(m))


rows = []
for m in (1, 2, 4, 6, 8, 10):
    v = 16 * atan_series(1 / 5, m) - 4 * atan_series(1 / 239, m)
    rows.append(f"| {m} | {v:.15f} | {abs(v - math.pi):.1e} |")
out(ma_tab="\n".join(rows))
# Σ1/k² 的余项修正
z2 = math.pi ** 2 / 6
rows = []
for n in (10, 100, 1000):
    S = math.fsum(1 / k ** 2 for k in range(1, n + 1))
    c1 = S + 1 / n
    c2 = c1 - 1 / (2 * n * n)
    c3 = c2 + 1 / (6 * n ** 3)
    rows.append(f"| {n} | {abs(S - z2):.1e} | {abs(c1 - z2):.1e} | {abs(c2 - z2):.1e} | {abs(c3 - z2):.1e} |")
out(em_tab="\n".join(rows))
# 卡亨求和（单精度，Σ_{k=1}^{10⁶} 1/k² 从大到小）
k = np.arange(1, 10 ** 6 + 1, dtype=np.float64)
t32 = (1.0 / k ** 2).astype(np.float32)
s32 = np.float32(0); c = np.float32(0)
for v in t32:
    y = np.float32(v - c)
    t = np.float32(s32 + y)
    c = np.float32(np.float32(t - s32) - y)
    s32 = t
exact = math.fsum(1.0 / k ** 2)
out(kh_sum=float(s32), kh_err=abs(float(s32) - exact))
