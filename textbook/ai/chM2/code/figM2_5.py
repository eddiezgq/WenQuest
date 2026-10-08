"""M2.5 节的示意图。

图 M2.5.1：（a）条件数 κ = 20 的二次损失上，三种学习率的轨迹：太小（慢）、最优（之字形但收敛）、超过上限（发散）——
取 20 而不是 100 只为画面看得清，道理一样；
（b）同一个问题，梯度下降与带动量的梯度下降：误差随步数的下降（对数坐标）。
"""
import numpy as np

from _chM2 import gd, quad
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
KAP = 100.0                                                  # (b) 用 κ = 100
KAP_A = 20.0                                                 # (a) 用 κ = 20：轨迹看得清
loss, grad, lam = quad([1.0, KAP])
loss_a, grad_a, _ = quad([1.0, KAP_A])
th0 = [1.0, 1.0]
eta_opt = 2 / (1 + KAP)
eta_opt_a = 2 / (1 + KAP_A)

fig, (a, b) = plt.subplots(1, 2, figsize=(11.0, 4.0))
g1, g2 = np.meshgrid(np.linspace(-1.2, 1.2, 240), np.linspace(-1.2, 1.2, 240))
Z = 0.5 * (g1 ** 2 + KAP_A * g2 ** 2)
a.contour(g1, g2, Z, levels=np.logspace(-2, 1.8, 14), colors=C["muted"], linewidths=0.6)
for eta, steps, col, name in ((0.02, 40, C["z"], T("太小：$\\eta=0.02$", "too small")),
                              (eta_opt_a, 40, C["y"], T(f"最优：$\\eta={eta_opt_a:.3f}$", "optimal")),
                              (0.102, 8, C["x"], T("超过上限：$\\eta=0.102$", "above the bound"))):
    tr = gd(grad_a, th0, eta, steps=steps)
    a.plot(tr[:, 0], tr[:, 1], "o-", color=col, lw=1.3, ms=3, label=name)
a.set_xlim(-1.3, 1.3)
a.set_ylim(-1.3, 1.3)
a.set_xlabel("$\\theta_1$")
a.set_ylabel("$\\theta_2$")
a.set_title(T("(a) 三种学习率的轨迹（$\\kappa = 20$）", "(a) Three learning rates ($\\kappa = 20$)"), fontsize=10)
a.legend(fontsize=8, loc="upper right")
a.grid(alpha=0.2, lw=0.5)

beta = ((np.sqrt(KAP) - 1) / (np.sqrt(KAP) + 1)) ** 2
eta_m = 4 / (1 + np.sqrt(KAP)) ** 2
for tr, col, name in ((gd(grad, th0, eta_opt, steps=400), C["y"], T("梯度下降（最优学习率）", "gradient descent")),
                      (gd(grad, th0, eta_m, steps=400, beta=beta), C["z"], T("加动量", "with momentum"))):
    e = np.linalg.norm(tr, axis=1)
    b.semilogy(np.arange(len(e)), np.maximum(e, 1e-16), color=col, lw=1.8, label=name)
b.set_xlabel(T("步数", "step"))
b.set_ylabel(T("到最低点的距离", "distance to the minimum"))
b.set_title(T("(b) 动量把步数从 $\\kappa$ 降到 $\\sqrt{\\kappa}$ 的量级",
              "(b) Momentum: from $\\kappa$ to $\\sqrt{\\kappa}$ steps"), fontsize=10)
b.set_ylim(1e-12, 3)
b.legend(fontsize=9)
b.grid(alpha=0.25, lw=0.5, which="both")
fig.tight_layout()
figure(fig, "figM2_5_1")
