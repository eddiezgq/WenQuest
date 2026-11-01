"""图 18.4.1：左：康托尔集的构造，每一步去掉每段中间的三分之一，剩下 2ᵏ 段、总长 (2/3)ᵏ；
右：弹跳的球（恢复系数 0.8）的高度：弹跳时刻越来越密，在 t∞ 处聚集，无穷多次弹跳在有限时间内完成。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.0))
segs = [(0.0, 1.0)]
for k in range(6):
    for a, b in segs:
        a1.plot([a, b], [-k, -k], color=BLUE, lw=6, solid_capstyle="butt")
    a1.text(1.03, -k, T(f"k = {k}：{2 ** k} 段，总长 {(2 / 3) ** k:.3f}", f"k = {k}: {2 ** k} pieces, length {(2 / 3) ** k:.3f}"), va="center", fontsize=9)
    segs = [s for a, b in segs for s in ((a, a + (b - a) / 3), (b - (b - a) / 3, b))]
a1.set_xlim(-0.02, 1.6)
a1.set_ylim(-5.6, 0.6)
a1.axis("off")
a1.set_title(T("康托尔集：不可数，测度却为零", "Cantor set: uncountable, yet of measure zero"), fontsize=10)
g, h0, e = 9.81, 0.5, 0.8
t0 = math.sqrt(2 * h0 / g)
v1 = math.sqrt(2 * g * h0)
ts = np.linspace(0, t0, 50)
a2.plot(ts, h0 - 0.5 * g * ts ** 2, color=BLUE, lw=1.5)
tc = t0
for k in range(1, 40):
    vk = v1 * e ** k
    dur = 2 * vk / g
    tt = np.linspace(0, dur, 40)
    a2.plot(tc + tt, vk * tt - 0.5 * g * tt ** 2, color=BLUE, lw=1.5)
    tc += dur
a2.axvline(tc, color=RED, ls="--", lw=1)
a2.text(tc - 0.05, 0.42, T(f"t∞ ≈ {tc:.2f} s", f"t∞ ≈ {tc:.2f} s"), color=RED, ha="right", fontsize=9)
a2.set_xlabel("t / s")
a2.set_ylabel(T("高度 / m", "height / m"))
a2.set_title(T("芝诺现象：弹跳时刻在 t∞ 处聚集", "Zeno behaviour: bounce times accumulate at t∞"), fontsize=10)
clean(a2)
fig.tight_layout()
figure(fig, "fig18_4_1")
