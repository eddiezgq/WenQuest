"""图 17.1.1：不能对角化的矩阵。(a) u' = Ju，J = [[−1, 1], [0, −1]]（二重特征值 −1，只有一个特征向量 e₁）：
所有轨线最后都沿 e₁ 方向进入原点（退化结点）；对照的对角矩阵 −I 的轨线是直线；
(b) S 形加减速（程序 17.1.1）：加加速度 j = ±50 m/s³ 各 0.1 s，加速度、速度、位移是 t 的一、二、三次多项式。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.3))
for th in np.linspace(0, 2 * math.pi, 17)[:-1]:
    p0 = 1.8 * np.array([math.cos(th), math.sin(th)])
    ts = np.linspace(0, 8, 400)
    P = np.array([math.exp(-t) * np.array([p0[0] + t * p0[1], p0[1]]) for t in ts])
    a1.plot(P[:, 0], P[:, 1], color=BLUE, lw=1.3)
    a1.plot([p0[0], 0], [p0[1], 0], color=MUTED, lw=0.7, ls=":")
a1.axhline(0, color=ACC, lw=2)
a1.text(1.25, 0.08, T("唯一的特征方向 e₁", "the only eigendirection e₁"), color=ACC, fontsize=9)
a1.set_xlim(-2.3, 2.3); a1.set_ylim(-2, 2); a1.set_aspect("equal")
a1.set_xticks([]); a1.set_yticks([])
a1.set_title(T("(a) J = [[−1, 1], [0, −1]]：轨线都贴着 e₁ 进入原点\n（虚线：对角矩阵 −I 的直线轨线）", "(a) J = [[−1, 1], [0, −1]]: paths enter along e₁\n(dotted: straight paths of −I)"), fontsize=10)
t1 = np.linspace(0, 0.1, 50); t2 = np.linspace(0.1, 0.2, 50)
j = np.r_[np.full(50, 50.0), np.full(50, -50.0)]
tt = np.r_[t1, t2]
a = np.r_[50 * t1, 5 - 50 * (t2 - 0.1)]
v = np.r_[25 * t1 ** 2, 0.25 + 5 * (t2 - 0.1) - 25 * (t2 - 0.1) ** 2]
s = np.r_[50 * t1 ** 3 / 6, 50 * 0.1 ** 3 / 6 + 0.25 * (t2 - 0.1) + 2.5 * (t2 - 0.1) ** 2 - 50 * (t2 - 0.1) ** 3 / 6]
for y, col, lab, sc in ((j, MUTED, T("加加速度 j / (100 m/s³)", "jerk j / (100 m/s³)"), 0.01), (a, RED, T("加速度 a / (10 m/s²)", "acceleration a / (10 m/s²)"), 0.1),
                        (v, GREEN, T("速度 v / (m/s)", "velocity v / (m/s)"), 1.0), (s, BLUE, T("位移 s / (10 cm)", "position s / (10 cm)"), 10.0)):
    a2.plot(tt, y * sc, color=col, lw=2, label=lab)
a2.axhline(0, color=MUTED, lw=0.6)
a2.set_xlabel(T("t / s", "t / s")); a2.legend(frameon=False, fontsize=8.5, loc="lower left")
for sp_ in ("top", "right"):
    a2.spines[sp_].set_visible(False)
a2.set_title(T("(b) S 形加减速：e^(Nt) 给出多项式", "(b) S-curve: e^(Nt) gives polynomials"), fontsize=11)
fig.tight_layout()
figure(fig, "fig17_1_1")
