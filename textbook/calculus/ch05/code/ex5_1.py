"""5.1 节：连续——AGV 原地转向时，航向角读数取主值 (−π, π]，转过 ±π 时读数跳变；
用相邻读数的差商估计角速度，跳变处得到一个荒谬的值。连续函数 sin x、x·sin(1/x) 的数值核对。"""
import math

import numpy as np

from bookout import out

w, T = 0.5, 0.02                       # 转速 0.5 rad/s（逆时针），采样周期 20 ms
t = np.arange(0, 12, T)
theta = 2.5 + w * t                    # 真实航向（连续）
read = np.arctan2(np.sin(theta), np.cos(theta))      # 传感器给出的主值 (−π, π]
rate = np.diff(read) / T
k = int(np.argmin(rate))
out(w=w, T_ms=T * 1000, t_jump=t[k + 1], read_before=read[k], read_after=read[k + 1],
    rate_jump=rate[k], rate_normal=float(np.median(rate)), jump=read[k + 1] - read[k])
rows = []
for i in range(k - 2, k + 4):
    r = "—" if i == k - 2 else f"{(read[i] - read[i - 1]) / T:.2f}"
    rows.append(f"| {t[i]:.2f} | {theta[i]:.4f} | {read[i]:.4f} | {r} |")
out(jump_tab="\n".join(rows))

# |sin x − sin a| ≤ |x − a|：在 [−10, 10] 上随机抽点核对
rng = np.random.default_rng(5)
x, a = rng.uniform(-10, 10, 10**6), rng.uniform(-10, 10, 10**6)
out(sin_lip=float(np.max(np.abs(np.sin(x) - np.sin(a)) / np.abs(x - a))))

# x·sin(1/x) 在 0 处：|f(x)| ≤ |x|
for e in (1e-1, 1e-3, 1e-6):
    xs = np.linspace(-e, e, 100001)
    xs = xs[xs != 0]
    out(**{f"xs_{-int(math.log10(e))}": float(np.max(np.abs(xs * np.sin(1 / xs))))})
