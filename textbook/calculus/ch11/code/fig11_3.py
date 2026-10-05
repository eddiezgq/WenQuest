"""图 11.3.1：上：同一次关节运动（90°，速度 180°/s，加速度 400°/s²）的梯形速度曲线与 S 形曲线（加加速度 4000°/s³）的角速度、
角加速度、角加加速度；下：AGV 沿“直行—换道—直行”路径的速度规划，曲率限制的速度上限与前向、后向扫描的结果。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt
from _motion import scurve, trapezoid
from _path import A_LAT, curvature, lane

fig = plt.figure(figsize=(11, 7.4))
gs = fig.add_gridspec(2, 3, height_ratios=[1, 1.05])
D, V, A, J = 90.0, 180.0, 400.0, 4000.0
tt, _, wt, at, _ = trapezoid(D, V, A)
ts, _, ws, as_, js = scurve(D, V, A, J)
ax = [fig.add_subplot(gs[0, k]) for k in range(3)]
ax[0].plot(tt, wt, color=BLUE, lw=2, label=T("梯形", "trapezoid"))
ax[0].plot(ts, ws, color=RED, lw=2, label=T("S 形", "S-curve"))
ax[0].set_ylabel("ω / (°/s)")
ax[0].legend(fontsize=9, frameon=False)
ax[1].plot(tt, at, color=BLUE, lw=2)
ax[1].plot(ts, as_, color=RED, lw=2)
ax[1].set_ylabel("α / (°/s²)")
ax[2].plot(ts, js, color=RED, lw=2)
for x0 in (0, V / A, D / V, D / V + V / A):
    ax[2].annotate("", xy=(x0, 5500 if x0 in (0, D / V + V / A) else -5500), xytext=(x0, 0), arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.4))
ax[2].set_ylim(-6500, 6500)
ax[2].set_ylabel("j / (°/s³)")
ax[2].set_title(T("梯形：加加速度是冲激（箭头）", "Trapezoid: impulsive jerk (arrows)"), fontsize=10)
for a_ in ax:
    a_.set_xlabel("t / s")
    clean(a_)
b = fig.add_subplot(gs[1, :])
y, yp, ypp = lane("quintic", 1.0, 4.0)
yy = lambda x: 0.0 if x <= 0 else (1.0 if x >= 4 else y(x))
N = 3200
xs = np.linspace(-6, 10, N + 1)
ds = np.hypot(np.diff(xs), np.diff([yy(v) for v in xs]))
s = np.concatenate([[0], np.cumsum(ds)])
kap = np.array([curvature(yp, ypp, v) if 0 < v < 4 else 0.0 for v in xs])
vlim = np.minimum(2.0, np.sqrt(A_LAT / np.maximum(kap, 1e-12)))
v = vlim.copy()
v[0] = 0
for k in range(N):
    v[k + 1] = min(v[k + 1], math.sqrt(v[k] ** 2 + 2 * 0.5 * ds[k]))
v[N] = 0
for k in range(N - 1, -1, -1):
    v[k] = min(v[k], math.sqrt(v[k + 1] ** 2 + 2 * 0.5 * ds[k]))
b.plot(s, vlim, color=MUTED, lw=1.2, ls="--", label=T("上限：限速 2 m/s 与 √(a/κ)", "cap: 2 m/s and √(a/κ)"))
b.plot(s, v, color=INK, lw=2, label=T("规划的速度", "planned speed"))
b.axvspan(s[np.searchsorted(xs, 0)], s[np.searchsorted(xs, 4)], color=GREEN, alpha=0.08, lw=0)
b.set_xlabel(T("路程 s / m", "distance along path s / m"))
b.set_ylabel("v / (m/s)")
b.set_ylim(0, 2.3)
b.set_title(T("AGV 速度规划：直行加速、换道段（绿）按曲率减速、终点前减速停车", "AGV speed plan: accelerate, slow for the lane change (green), stop"), fontsize=10)
b.legend(fontsize=9, frameon=False, loc="lower center")
clean(b, zero=False)
fig.tight_layout()
figure(fig, "fig11_3_1")
