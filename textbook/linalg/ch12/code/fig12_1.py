"""图 12.1.1：不同的范数与内积。(a) 平面上四种“单位圆”：1-范数（菱形）、2-范数（圆）、∞-范数（正方形）、W 内积的范数（斜椭圆），
只有圆和椭圆来自内积；(b) W = [[2, 1], [1, 2]] 下 u = (1, 0) 与 v = (−1, 2) 正交：v 沿椭圆 xᵀWx = 2 在 u 处的切线。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, arrow, axes_box, figure, plt

W = np.array([[2.0, 1], [1, 2]])
t = np.linspace(0, 2 * np.pi, 721)
C = np.vstack([np.cos(t), np.sin(t)])
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.0, 4.6))
axes_box(a1, 1.6)
a1.plot([1, 0, -1, 0, 1], [0, 1, 0, -1, 0], color=RED, lw=1.8, label=T("1-范数 |x₁| + |x₂| = 1", "1-norm |x₁| + |x₂| = 1"))
a1.plot(C[0], C[1], color=BLUE, lw=1.8, label=T("2-范数（点积）", "2-norm (dot product)"))
a1.plot([1, -1, -1, 1, 1], [1, 1, -1, -1, 1], color=GREEN, lw=1.8, label=T("∞-范数 max(|x₁|, |x₂|) = 1", "∞-norm max(|x₁|, |x₂|) = 1"))
E = np.linalg.inv(np.linalg.cholesky(W).T) @ C
a1.plot(E[0], E[1], color=ACC, lw=2.2, label=T("W 内积：xᵀWx = 1", "W inner product: xᵀWx = 1"))
a1.legend(loc="upper center", fontsize=9, frameon=False, bbox_to_anchor=(0.5, -0.06), ncol=2)
a1.set_title(T("(a) 四种“单位圆”", "(a) Four 'unit circles'"), fontsize=11)
axes_box(a2, 2.6)
E2 = np.sqrt(2) * E
a2.plot(E2[0], E2[1], color=ACC, lw=2.2)
u, v = np.array([1.0, 0]), np.array([-1.0, 2])
arrow(a2, u, RED, "u", offset=(0.05, -0.32))
arrow(a2, v, GREEN, "v", offset=(-0.3, 0.05))
a2.plot([u[0] - 0.6 * v[0], u[0] + 0.6 * v[0]], [u[1] - 0.6 * v[1], u[1] + 0.6 * v[1]], ls="--", color=GREEN, lw=1)
a2.text(-2.45, -2.3, T("u·v = −1，但 uᵀWv = 0", "u·v = −1, but uᵀWv = 0"), color=INK, fontsize=10)
a2.text(0.75, 1.8, "xᵀWx = 2", color=ACC, fontsize=10)
a2.set_title(T("(b) W 内积下 u 与 v 正交", "(b) u and v orthogonal under W"), fontsize=11)
figure(fig, "fig12_1_1")
