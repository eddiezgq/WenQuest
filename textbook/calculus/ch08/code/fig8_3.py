"""图 8.3.1：误差传播——编码器误差 ±0.001 rad（均匀分布）时两节连杆末端误差的蒙特卡罗点云、最坏情况界与均方根；测高的相对误差随仰角的变化。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt
from _traj import ur5e_links

l1, l2 = ur5e_links()
t1, t2 = math.radians(30), math.radians(60)
d0 = 1e-3
rng = np.random.default_rng(83)
e1, e2 = rng.uniform(-d0, d0, 5000), rng.uniform(-d0, d0, 5000)
fk = lambda a, b: np.stack([l1 * np.cos(a) + l2 * np.cos(a + b), l1 * np.sin(a) + l2 * np.sin(a + b)])
dp = (fk(t1 + e1, t2 + e2) - fk(np.array(t1), np.array(t2))[:, None]) * 1000
r = math.sqrt(l1 ** 2 + l2 ** 2 + 2 * l1 * l2 * math.cos(t2))
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.4))
a1.plot(dp[0], dp[1], ".", color=BLUE, ms=1.5, alpha=0.5)
c = np.linspace(0, 2 * math.pi, 200)
W = (r + l2) * d0 * 1000
S = d0 * math.sqrt((r * r + l2 * l2) / 3) * 1000
a1.plot(W * np.cos(c), W * np.sin(c), color=RED, lw=1.5, label=T("最坏情况界 (r + l₂)δ", "worst case (r + l₂)δ"))
a1.plot(S * np.cos(c), S * np.sin(c), color=GREEN, lw=1.5, ls="--", label=T("均方根", "RMS"))
a1.set_aspect("equal")
a1.set_xlabel("Δx / mm")
a1.set_ylabel("Δy / mm")
a1.legend(fontsize=8.5, frameon=False, loc="upper right")
a1.set_title(T("末端误差：点云是平行四边形，大部分远离最坏情况", "End error: a parallelogram cloud, mostly far from the worst case"), fontsize=9.5)
clean(a1, zero=False)
al = np.linspace(5, 85, 200)
da = math.radians(0.5)
a2.plot(al, 2 * da / np.sin(2 * np.radians(al)) * 100, color=INK, lw=2)
a2.plot([45], [2 * da * 100], "o", color=RED)
a2.set_ylim(0, 8)
a2.set_xlabel(T("仰角 α / (°)", "elevation α / (°)"))
a2.set_ylabel(T("高度的相对误差 / %", "relative error of height / %"))
a2.set_title(T("h = d·tan α，角度误差 ±0.5°：45° 时最准", "h = d·tan α, ±0.5° error: best at 45°"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig8_3_1")
