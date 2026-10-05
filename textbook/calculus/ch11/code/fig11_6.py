"""图 11.6.1：左：带噪声的阶跃响应数据与拟合曲线（τ 的最小二乘估计）；右：黄金分割法、梯度下降（三种步长）与牛顿法的误差随迭代次数的变化。"""
import math
import random

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

random.seed(116)
ts = [0.01 * i for i in range(41)]
ys = [1 - math.exp(-t / 0.08) + random.gauss(0, 0.01) for t in ts]
S = lambda tau: sum((y - (1 - math.exp(-t / tau))) ** 2 for t, y in zip(ts, ys))
dS = lambda tau: sum(-2 * (y - (1 - math.exp(-t / tau))) * (-math.exp(-t / tau) * t / tau ** 2) for t, y in zip(ts, ys))
h = 1e-7
ddS = lambda tau: (dS(tau + h) - dS(tau - h)) / (2 * h)
tau = 0.15
for _ in range(30):
    tau -= dS(tau) / ddS(tau)
ts_ = tau
c2 = ddS(ts_)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
a1.plot(ts, ys, "o", color=BLUE, ms=3.5, label=T("测量数据", "data"))
tt = np.linspace(0, 0.4, 300)
a1.plot(tt, 1 - np.exp(-tt / ts_), color=RED, lw=2, label=T(f"拟合 τ = {ts_:.4f} s", f"fit τ = {ts_:.4f} s"))
a1.set_xlabel("t / s")
a1.set_ylabel(T("归一化转速", "normalized speed"))
a1.legend(fontsize=9, frameon=False, loc="lower right")
a1.set_title(T("最小二乘拟合电机的时间常数", "Least-squares fit of the time constant"), fontsize=10)
clean(a1, zero=False)
# 黄金分割
g = (math.sqrt(5) - 1) / 2
a, b = 0.02, 0.30
c, d = b - g * (b - a), a + g * (b - a)
fc, fd = S(c), S(d)
eg = []
for _ in range(40):
    if fc < fd:
        b, d, fd = d, c, fc
        c = b - g * (b - a)
        fc = S(c)
    else:
        a, c, fc = c, d, fd
        d = a + g * (b - a)
        fd = S(d)
    eg.append(max(abs((a + b) / 2 - ts_), 1e-17))
a2.semilogy(range(1, 41), eg, "o-", color=GREEN, ms=3, lw=1, label=T("黄金分割", "golden section"))
for eta, c_, lab in ((0.5 / c2, BLUE, T("梯度下降 η = 0.5/S″", "gradient, η = 0.5/S″")), (1.9 / c2, ACC, T("梯度下降 η = 1.9/S″", "gradient, η = 1.9/S″")),
                     (2.2 / c2, MUTED, T("梯度下降 η = 2.2/S″（不收敛）", "gradient, η = 2.2/S″ (no convergence)"))):
    tau, e = 0.15, []
    for _ in range(40):
        tau -= eta * dS(tau)
        e.append(max(abs(tau - ts_), 1e-17))
    a2.semilogy(range(1, 41), e, "o-", color=c_, ms=3, lw=1, label=lab)
tau, e = 0.15, []
for _ in range(8):
    tau -= dS(tau) / ddS(tau)
    e.append(max(abs(tau - ts_), 1e-17))
a2.semilogy(range(1, 9), e, "o-", color=RED, ms=4, lw=1.4, label=T("牛顿法", "Newton"))
a2.set_xlabel(T("迭代次数", "iteration"))
a2.set_ylabel("|τₖ − τ*|")
a2.set_ylim(1e-17, 1)
a2.legend(fontsize=8, frameon=False, loc="upper right")
a2.set_title(T("牛顿法最快，步长过大的梯度下降来回振荡", "Newton fastest; a large gradient step oscillates"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig11_6_1")
