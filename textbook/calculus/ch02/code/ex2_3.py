"""2.3 节：函数的性质——四足机器人膝关节的步态（示意模型）的周期、取值范围与单调区间；
sin 2t + sin 3t 的周期；f(x) = x/(1 + x²) 的界；偶部与奇部的分解。"""
import math

import numpy as np

from bookout import out

# 四足机器人小跑步态中膝关节角的示意模型（单位：度），步态周期 Tg = 0.5 s
Tg = 0.5
knee = lambda t: -90 + 20 * np.sin(2 * np.pi * t / Tg) + 6 * np.sin(4 * np.pi * t / Tg + 0.6)
t = np.linspace(0, 3 * Tg, 30001)
y = knee(t)
assert np.allclose(knee(t + Tg), y)                 # 周期 Tg
# 一个周期内的最大、最小值与单调区间（由采样的差分符号判断）
t1 = np.linspace(0, Tg, 50001)
y1 = knee(t1)
i_max, i_min = int(y1.argmax()), int(y1.argmin())
out(Tg=Tg, kmax=float(y1.max()), kmin=float(y1.min()), t_max=float(t1[i_max]), t_min=float(t1[i_min]),
    amp=float(y1.max() - y1.min()))
sgn = np.sign(np.diff(y1))
changes = np.nonzero(np.diff(sgn))[0]
out(n_turns=int(changes.size))                      # 一个周期内单调性改变的次数

# 算例 2.3.2：sin 2t + sin 3t 以 2π 为周期，且没有更小的正周期（在 (0, 2π) 上逐个检查候选值）
g = lambda t: np.sin(2 * t) + np.sin(3 * t)
ts = np.linspace(0, 2 * np.pi, 2001)
assert np.allclose(g(ts + 2 * np.pi), g(ts))
# 更小的候选周期 π、2π/3 都不行：例如 T = π 时 g(t + π) = sin 2t − sin 3t
for c in (np.pi, 2 * np.pi / 3, np.pi / 2):
    assert not np.allclose(g(ts + c), g(ts))
out(g_val=float(g(np.pi / 2 + np.pi)), g_val0=float(g(np.pi / 2)))

# 算例 2.3.3：x/(1 + x²) 的界是 1/2，在 x = ±1 处取到
xs = np.linspace(-50, 50, 200001)
f = xs / (1 + xs**2)
assert abs(float(f.max()) - 0.5) < 1e-8 and abs(float(f.min()) + 0.5) < 1e-8
out(fmax=float(f.max()), x_at=float(xs[f.argmax()]))

# 定理 2.3.2：f = 偶部 + 奇部，以 f(x) = eˣ 为例
ex = np.exp(xs[:1000])
ev, od = (np.exp(xs[:1000]) + np.exp(-xs[:1000])) / 2, (np.exp(xs[:1000]) - np.exp(-xs[:1000])) / 2
assert np.allclose(ev + od, ex)
out(decomp_ok=1)
