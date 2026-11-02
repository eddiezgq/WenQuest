"""图 23.4.1：(a) 示教轨迹的 5 次多项式拟合：不加约束时起点、终点的位置和速度都有偏差；加上等式约束后两端严格满足，中间的拟合几乎不变；
(b) 四种回炉料配铜合金：不加约束的最小二乘要用负的料 B；加上“用量非负、总质量 100 kg”后只用料 C、D。"""
import numpy as np
from scipy.linalg import qr

from _fig import BLUE, GREEN, INK, MUTED, RED, T, figure, plt

rng = np.random.default_rng(23041)
t = np.linspace(0, 2, 30)
s = t - 1.0
q0, q1 = 0.2, 1.4
q_true = q0 + (q1 - q0) * (10 * (t / 2) ** 3 - 15 * (t / 2) ** 4 + 6 * (t / 2) ** 5) + 0.03 * np.sin(2 * np.pi * t / 2)
y = q_true + rng.normal(0, 0.01, t.size)
A = np.vander(s, 6, increasing=True)


def row(sv, der):
    return np.array([0 if k < der else np.prod(range(k - der + 1, k + 1)) * sv ** (k - der) for k in range(6)], dtype=float)


Cm = np.vstack([row(-1, 0), row(1, 0), row(-1, 1), row(1, 1)])
d = np.array([q0, q1, 0.0, 0.0])
K = np.block([[A.T @ A, Cm.T], [Cm, np.zeros((4, 4))]])
xc = np.linalg.solve(K, np.concatenate([A.T @ y, d]))[:6]
xf = np.linalg.lstsq(A, y, rcond=None)[0]
tt = np.linspace(0, 2, 400)
Vt = np.vander(tt - 1, 6, increasing=True)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.4), gridspec_kw={"width_ratios": [1.4, 1]})
a1.plot(t, y, "o", color=MUTED, ms=4, label=T("示教采样（带噪声）", "taught samples (noisy)"))
a1.plot(tt, Vt @ xf, color=BLUE, lw=1.4, ls="--", label=T("不加约束", "unconstrained"))
a1.plot(tt, Vt @ xc, color=RED, lw=1.8, label=T("两端位置、速度约束", "end position & velocity constrained"))
a1.plot([0, 2], [q0, q1], "s", color=INK, ms=8, label=T("给定的起点、终点", "required end points"))
ins = a1.inset_axes([0.62, 0.1, 0.35, 0.35])
m = tt > 1.8
ins.plot(tt[m], (Vt @ xf)[m], color=BLUE, ls="--")
ins.plot(tt[m], (Vt @ xc)[m], color=RED)
ins.plot([2], [q1], "s", color=INK)
ins.set_title(T("终点附近", "near the end"), fontsize=8)
ins.tick_params(labelsize=7)
a1.set_xlabel(T("时间 / s", "time / s"))
a1.set_ylabel(T("关节角 / rad", "joint angle / rad"))
a1.legend(frameon=False, fontsize=8.5, loc="upper left")
a1.set_title(T("(a) 带端点约束的轨迹拟合", "(a) Trajectory fit with end-point constraints"), fontsize=10)
M = np.array([[0.80, 0.60, 0.70, 0.90], [0.15, 0.35, 0.10, 0.02], [0.04, 0.04, 0.18, 0.03], [0.01, 0.01, 0.02, 0.05]])
tg = 100 * np.array([0.88, 0.03, 0.07, 0.02])
x_ls = np.linalg.solve(M, tg)
best = None
import itertools
for r in range(1, 5):
    for S in itertools.combinations(range(4), r):
        Ms = M[:, S]
        k = len(S)
        Kk = np.block([[Ms.T @ Ms, np.ones((k, 1))], [np.ones((1, k)), np.zeros((1, 1))]])
        xs = np.linalg.solve(Kk, np.concatenate([Ms.T @ tg, [100.0]]))[:k]
        if np.all(xs >= -1e-12):
            x = np.zeros(4); x[list(S)] = xs
            rr = np.linalg.norm(M @ x - tg)
            if best is None or rr < best[0]:
                best = (rr, x)
xs = np.arange(4)
a2.bar(xs - 0.2, x_ls, width=0.38, color=BLUE, label=T("不加约束", "unconstrained"))
a2.bar(xs + 0.2, best[1], width=0.38, color=RED, label=T("非负、总质量 100 kg", "nonnegative, total 100 kg"))
a2.axhline(0, color=INK, lw=0.8)
a2.set_xticks(xs)
a2.set_xticklabels([T("料 A", "A"), T("料 B", "B"), T("料 C", "C"), T("料 D", "D")])
a2.set_ylabel(T("用量 / kg", "mass / kg"))
a2.legend(frameon=False, fontsize=8.5)
a2.set_title(T("(b) 配料：非负约束", "(b) Batching with nonnegativity"), fontsize=10)
for a in (a1, a2):
    for sp in ("top", "right"):
        a.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig23_4_1")
