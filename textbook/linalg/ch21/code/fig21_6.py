"""图 21.6.1：(a) AGV 横向控制在随机扰动下的稳态：2 万步仿真的 (横向偏差, 航向偏差)（点）与离散李雅普诺夫方程
P = FPFᵀ + Q 的解给出的 1σ、2σ、3σ 椭圆；(b) 6 × 6 网格的二维拉普拉斯矩阵 L₂ = I ⊗ L₁ + L₁ ⊗ I 的非零元分布（36 阶）。"""
import math

import numpy as np

from _fig import BLUE, INK, MUTED, RED, T, figure, plt

rng = np.random.default_rng(21061)
dt, v, k1, k2 = 0.05, 1.0, 4.0, 3.0
F = np.array([[1.0, v * dt], [-k1 * dt, 1 - k2 * dt]])
sig = np.array([0.002, math.radians(0.3)])
Q = np.diag(sig ** 2)
P = np.linalg.solve(np.eye(4) - np.kron(F, F), Q.reshape(-1, order="F")).reshape(2, 2, order="F")
z = np.zeros(2)
Z = []
for k in range(20000):
    z = F @ z + sig * rng.standard_normal(2)
    Z.append(z)
Z = np.array(Z[1000:])
S = np.diag([1000, 180 / math.pi])                    # 换成 mm 与度
Zs = Z @ S
Ps = S @ P @ S
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 4.8), gridspec_kw={"width_ratios": [1.3, 1]})
a1.plot(Zs[::4, 0], Zs[::4, 1], ".", color=MUTED, ms=1.5, alpha=0.5, rasterized=True)
lam, U = np.linalg.eigh(Ps)
u = np.linspace(0, 2 * math.pi, 361)
for kk in (1, 2, 3):
    E = U @ np.diag(kk * np.sqrt(lam)) @ np.vstack([np.cos(u), np.sin(u)])
    a1.plot(E[0], E[1], color=RED, lw=1.6 if kk == 1 else 1.0)
    frac = np.mean(np.einsum("ij,jk,ik->i", Zs, np.linalg.inv(Ps), Zs) <= kk ** 2)
    a1.text(E[0, 30], E[1, 30], T(f"{kk}σ：{frac:.1%}", f"{kk}σ: {frac:.1%}"), color=RED, fontsize=9)
a1.set_xlabel(T("横向偏差 e / mm", "lateral error e / mm"))
a1.set_ylabel(T("航向偏差 φ / (°)", "heading error φ / (°)"))
a1.set_title(T("(a) 仿真（点）与 P = FPFᵀ + Q 的椭圆\n（百分数为落在椭圆内的点所占比例）", "(a) Simulation (dots) and ellipses from P = FPFᵀ + Q \n(percentages: share of points inside)"), fontsize=9.5)
for sp in ("top", "right"):
    a1.spines[sp].set_visible(False)
n = 6
L1 = 2 * np.eye(n) - np.eye(n, k=1) - np.eye(n, k=-1)
L2 = np.kron(np.eye(n), L1) + np.kron(L1, np.eye(n))
a2.spy(L2, markersize=5, color=BLUE)
for k in range(1, n):
    a2.axhline(k * n - 0.5, color=MUTED, lw=0.5)
    a2.axvline(k * n - 0.5, color=MUTED, lw=0.5)
a2.set_title(T(f"(b) L₂ = I ⊗ L₁ + L₁ ⊗ I 的非零元（{n}×{n} 网格，{np.count_nonzero(L2)} 个）",
               f"(b) Nonzeros of L₂ = I ⊗ L₁ + L₁ ⊗ I ({n}×{n} grid, {np.count_nonzero(L2)})"), fontsize=9.5)
a2.tick_params(labelsize=8)
fig.tight_layout()
figure(fig, "fig21_6_1")
