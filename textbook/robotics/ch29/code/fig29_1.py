"""29.1 节的示意图。

图 29.1.1：(a) 正动力学的乘法次数随关节数 n 的变化：铰接体算法与“递推 + 复合刚体算法 + 楚列斯基分解”；
          (b) 叠放料箱的 PGS 达到 0.1% 精度所需的迭代次数随料箱数 N 的变化，等重与顶上重 10 倍，虚线为 2.8N²；
          (c) 每步只迭代 10 次时 10 个料箱顶上那一个的下沉量随时间的变化：冷启动与热启动。
"""
import math

import numpy as np

from _ch29 import Count, aba_counted, crba_counted, pgs, random_chain, stack_delassus
from bookout import COLORS as C, T, figure, style

plt = style()
rng = np.random.default_rng(29)
fig, axs = plt.subplots(1, 3, figsize=(13.2, 3.9))

# (a)
ns = [1, 2, 3, 6, 9, 12, 16, 20, 25, 30, 40, 50]
A_, B_ = [], []
for n in ns:
    ch = random_chain(n, rng)
    th, thd, tau = rng.uniform(-3, 3, n), rng.uniform(-1, 1, n), rng.uniform(-5, 5, n)
    Count.reset()
    aba_counted(ch, th, thd, tau)
    A_.append(Count.mul)
    Count.reset()
    crba_counted(ch, th, thd, tau)
    B_.append(Count.mul)
ax = axs[0]
ax.plot(ns, np.array(A_) / 1000, "o-", color=C["z"], ms=4, lw=1.6, label=T("铰接体算法", "articulated-body algorithm"))
ax.plot(ns, np.array(B_) / 1000, "s-", color=C["x"], ms=4, lw=1.6, label=T("递推 + 复合刚体 + 楚列斯基", "RNEA + CRBA + Cholesky"))
ax.axvline(6, color=C["muted"], lw=0.8, ls=":")
ax.text(7, max(B_) / 1000 * 0.45, T("WQ-CR5\nn = 6", "WQ-CR5\nn = 6"), fontsize=8.5, color=C["muted"])
ax.set_xlabel(T("关节数 n", "number of joints n"))
ax.set_ylabel(T("乘法次数 / 千次", "multiplications / thousand"))
ax.set_title(T("(a) 正动力学的运算量", "(a) cost of forward dynamics"), fontsize=11)
ax.legend(fontsize=8.5, frameon=False, loc="upper left")
ax.grid(alpha=0.25)

# (b)
H, G0, MB = 0.002, 9.81, 8.0


def lcp(N, top=MB):
    ms = np.full(N, MB)
    ms[-1] = top
    J, A = stack_delassus(ms)
    return ms, J, A, J @ np.full(N, -H * G0)


def iters(N, top=MB):
    ms, J, A, b = lcp(N, top)
    lam = np.linalg.solve(A, -b)
    _, hist = pgs(A, b, iters=20000)
    return next(i + 1 for i, x in enumerate(hist) if np.abs(x - lam).max() < 1e-3 * lam.max())


Ns = [2, 4, 6, 8, 10, 14, 20]
ax = axs[1]
ax.plot(Ns, [iters(N) for N in Ns], "o-", color=C["z"], ms=4, lw=1.6, label=T("等重", "equal masses"))
ax.plot(Ns, [iters(N, 10 * MB) for N in Ns], "s-", color=C["accent"], ms=4, lw=1.6, label=T("顶上重 10 倍", "top box 10× heavier"))
xx = np.linspace(2, 20, 100)
ax.plot(xx, math.log(1e3) * 4 / math.pi ** 2 * xx ** 2, color=C["muted"], lw=1, ls="--", label=r"$2.8N^2$")
ax.set_xlabel(T("料箱层数 N", "number of boxes N"))
ax.set_ylabel(T("迭代次数", "iterations"))
ax.set_title(T("(b) PGS 达到 0.1% 精度", "(b) PGS to 0.1% accuracy"), fontsize=11)
ax.legend(fontsize=8.5, frameon=False, loc="upper left")
ax.grid(alpha=0.25)

# (c)
ax = axs[2]
for warm, col, lab in ((False, C["x"], T("冷启动", "cold start")), (True, C["z"], T("热启动", "warm start"))):
    ms, J, A, _ = lcp(10)
    v, x, lam = np.zeros(10), np.zeros(10), np.zeros(10)
    ts, ys = [], []
    for k in range(500):
        b = J @ (v - H * G0)
        lam, _ = pgs(A, b, lam0=lam if warm else None, iters=10)
        v = v - H * G0 + J.T @ lam / ms
        x = x + H * v
        ts.append((k + 1) * H)
        ys.append(-x[-1] * 1000)
    ax.plot(ts, ys, color=col, lw=1.8, label=lab)
ax.set_xlabel("t / s")
ax.set_ylabel(T("顶上料箱的下沉 / mm", "sinking of the top box / mm"))
ax.set_title(T("(c) 10 层，每步迭代 10 次", "(c) 10 boxes, 10 iterations per step"), fontsize=11)
ax.legend(fontsize=8.5, frameon=False, loc="upper left")
ax.grid(alpha=0.25)
fig.tight_layout()
figure(fig, "fig29_1_1")
