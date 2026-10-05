"""图 10.6.1：加权最小二乘。(a) 相机跟踪远去的 AGV：测量误差（误差棒为 ±σ_i）随距离增大，普通最小二乘与加权最小二乘拟合的直线；
(b) 重复 2000 次测量，两种方法得到的速度估计值的分布：加权的更集中。"""
import numpy as np

from _fig import BLUE, INK, MUTED, RED, T, figure, plt

rng = np.random.default_rng(606)
t = np.arange(12) * 0.5
x_true = 2.0 + 0.8 * t
sig = 0.005 * x_true ** 2
A = np.column_stack([np.ones_like(t), t])
W = np.diag(1 / sig ** 2)
x = x_true + rng.normal(size=t.size) * sig
co = np.linalg.solve(A.T @ A, A.T @ x)
cw = np.linalg.solve(A.T @ W @ A, A.T @ W @ x)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 3.9))
a1.errorbar(t, x, yerr=sig, fmt="o", color=INK, ms=4, capsize=3, lw=1)
tt = np.linspace(0, 5.5, 2)
a1.plot(tt, co[0] + co[1] * tt, color=BLUE, lw=2, label=T("普通最小二乘", "ordinary least squares"))
a1.plot(tt, cw[0] + cw[1] * tt, color=RED, lw=2, ls="--", label=T("加权最小二乘", "weighted least squares"))
a1.set_xlabel(T("时间 t / s", "time t / s")); a1.set_ylabel(T("位置 x / m", "position x / m"))
a1.legend(frameon=False, fontsize=10)
a1.set_title(T("(a) 误差随距离增大的测量", "(a) errors grow with distance"), fontsize=11)
eo, ew = [], []
for _ in range(2000):
    xm = x_true + rng.normal(size=t.size) * sig
    eo.append(np.linalg.solve(A.T @ A, A.T @ xm)[1])
    ew.append(np.linalg.solve(A.T @ W @ A, A.T @ W @ xm)[1])
bins = np.linspace(0.70, 0.90, 41)
a2.hist(eo, bins=bins, color=BLUE, alpha=0.5, label=T("普通", "ordinary"))
a2.hist(ew, bins=bins, color=RED, alpha=0.5, label=T("加权", "weighted"))
a2.axvline(0.8, color=INK, lw=1)
a2.set_xlabel(T("速度估计值 / (m/s)", "estimated speed / (m/s)")); a2.set_ylabel(T("次数", "count"))
a2.legend(frameon=False, fontsize=10)
a2.set_title(T("(b) 2000 次重复：加权估计更集中", "(b) 2000 repeats: the weighted estimate is tighter"), fontsize=11)
for a in (a1, a2):
    for s in ("top", "right"):
        a.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig10_6_1")
