"""图 17.6.1：水平关节按五次多项式 1 s 内转 90°：左：机械功率 τω（正：电机做功；负：制动，可回收），
右：电机电流与铜损功率 i²R。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

J, b, kt, N, R, D = 0.6, 0.4, 0.08, 50, 0.6, math.pi / 2
t = np.linspace(0, 1, 400)
w = D * 30 * t ** 2 * (1 - t) ** 2
a = D * 60 * t * (1 - t) * (1 - 2 * t)
tau = J * a + b * w
P = tau * w
i = tau / (kt * N)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.0))
a1.plot(t, P, color=INK, lw=2)
a1.fill_between(t, 0, P, where=P >= 0, color=RED, alpha=0.3, label=T("电机输出：约 3.38 J", "motor output: about 3.38 J"))
a1.fill_between(t, 0, P, where=P < 0, color=GREEN, alpha=0.3, label=T("制动（可回收）：约 1.97 J", "braking (recoverable): about 1.97 J"))
a1.set_xlabel("t / s")
a1.set_ylabel(T("机械功率 τω / W", "mechanical power τω / W"))
a1.legend(fontsize=9, frameon=False)
a1.set_title(T("能量 = 功率对时间的积分", "Energy = ∫ power dt"), fontsize=10)
clean(a1)
a2.plot(t, i, color=BLUE, lw=2, label=T("电流 i / A", "current i / A"))
a2.plot(t, i ** 2 * R, color=ACC, lw=2, label=T("铜损 i²R / W", "copper loss i²R / W"))
a2.set_xlabel("t / s")
a2.legend(fontsize=9, frameon=False)
a2.set_title(T("铜损与电流的平方成正比：看均方根，不看平均", "Copper loss ∝ i²: use RMS, not the mean"), fontsize=10)
clean(a2)
fig.tight_layout()
figure(fig, "fig17_6_1")
