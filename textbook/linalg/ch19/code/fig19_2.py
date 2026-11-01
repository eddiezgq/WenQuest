"""图 19.2.1：主成分是投影方差最大的方向。(a) 标准化后的噪声与振动：主成分方向 v₁、v₂ 与 2 倍标准差的椭圆，
一条 30° 的直线和各点到它的垂线（残差）；(b) 投影方差与残差平方和（除以 N − 1）随直线角度的变化，两者之和恒为 2。
图 19.2.2：六项检测的主成分。(a) 特征值（碎石图）与累计方差解释比；(b) 前三个主成分的载荷。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, arrow, figure, plt
from _num import fix_sign
from _qc import N_I, SHORT, SHORT_EN, X_I

Xc = X_I - X_I.mean(axis=0)
Z = Xc / Xc.std(axis=0, ddof=1)
Z2 = Z[:, [2, 4]]
R2 = Z2.T @ Z2 / (N_I - 1)
w2, V2 = np.linalg.eigh(R2)
w2, V2 = w2[::-1], fix_sign(V2[:, ::-1])

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.8))
a1.scatter(Z2[:, 0], Z2[:, 1], s=9, color=BLUE, alpha=0.55, lw=0, zorder=2)
th = np.radians(30)
u = np.array([np.cos(th), np.sin(th)])
a1.plot([-3.5 * u[0], 3.5 * u[0]], [-3.5 * u[1], 3.5 * u[1]], color=ACC, lw=1.4, zorder=3)
for z in Z2[::4]:
    q = (z @ u) * u
    a1.plot([z[0], q[0]], [z[1], q[1]], color=ACC, lw=0.6, alpha=0.7, zorder=3)
t = np.linspace(0, 2 * np.pi, 200)
E = V2 @ np.vstack([2 * np.sqrt(w2[0]) * np.cos(t), 2 * np.sqrt(w2[1]) * np.sin(t)])
a1.plot(E[0], E[1], color=MUTED, lw=1, ls="--")
arrow(a1, 2 * np.sqrt(w2[0]) * V2[:, 0], RED, "v₁", offset=(0.1, -0.05), lw=2.4)
arrow(a1, 2.2 * np.sqrt(w2[1]) * V2[:, 1], GREEN, "v₂", offset=(0.1, -0.2), lw=2.4)
a1.text(2.4, 1.0, T("30° 的直线", "line at 30°"), color=ACC, fontsize=9.5)
a1.set_aspect("equal")
a1.set_xlim(-3.6, 3.6)
a1.set_ylim(-3.2, 3.4)
a1.set_xlabel(T("噪声（标准化）", "noise (standardized)"))
a1.set_ylabel(T("振动（标准化）", "vibration (standardized)"))
a1.set_title(T("(a) 主成分方向与一条试探的直线", "(a) Principal directions and a trial line"), fontsize=11)
for s in ("top", "right"):
    a1.spines[s].set_visible(False)
deg = np.linspace(0, 180, 361)
U = np.vstack([np.cos(np.radians(deg)), np.sin(np.radians(deg))])
var = np.einsum("ik,ij,jk->k", U, R2, U)
a2.plot(deg, var, color=RED, lw=2, label=T("投影方差 uᵀRu", "projected variance uᵀRu"))
a2.plot(deg, 2 - var, color=GREEN, lw=2, label=T("残差平方和 /(N − 1)", "residual sum of squares /(N − 1)"))
a2.axhline(2, color=MUTED, lw=0.8, ls=":")
a2.text(2, 1.9, T("两者之和 = tr R = 2", "sum = tr R = 2"), color=MUTED, fontsize=9)
a2.axvline(45, color=RED, lw=0.8, ls="--")
a2.axvline(135, color=GREEN, lw=0.8, ls="--")
a2.text(47, w2[0] + 0.04, T(f"45°：方差最大 λ₁ = {w2[0]:.2f}", f"45°: largest variance λ₁ = {w2[0]:.2f}"), color=RED, fontsize=9.5)
a2.text(133, w2[1] + 0.1, T(f"135°：方差最小 λ₂ = {w2[1]:.2f}", f"135°: smallest variance λ₂ = {w2[1]:.2f}"), color=RED, fontsize=9.5, ha="right")
a2.set_xlim(0, 180)
a2.set_ylim(0, 2.55)
a2.set_xticks([0, 30, 45, 90, 135, 180])
a2.set_xlabel(T("直线与横轴的夹角 / (°)", "angle of the line / (°)"))
a2.legend(frameon=False, fontsize=9, loc="upper center", ncol=2)
a2.set_title(T("(b) 投影方差最大 ⇔ 残差最小", "(b) Largest projected variance ⇔ smallest residual"), fontsize=11)
for s in ("top", "right"):
    a2.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig19_2_1")

# 图 19.2.2
R = Z.T @ Z / (N_I - 1)
w, V = np.linalg.eigh(R)
w, V = w[::-1], fix_sign(V[:, ::-1])
fig, (b1, b2) = plt.subplots(1, 2, figsize=(11.0, 4.2))
k = np.arange(1, 7)
b1.bar(k, w, color=BLUE, width=0.6)
for i in range(6):
    b1.text(k[i], w[i] + 0.05, f"{w[i]:.2f}", ha="center", fontsize=9)
b1.axhline(1, color=MUTED, lw=0.8, ls=":")
b1.set_xlabel(T("主成分序号 i", "component i"))
b1.set_ylabel(T("特征值 λᵢ", "eigenvalue λᵢ"))
bt = b1.twinx()
bt.plot(k, 100 * np.cumsum(w) / 6, "o-", color=RED, lw=1.6)
bt.set_ylim(0, 105)
bt.set_ylabel(T("累计方差解释比 / %", "cumulative explained variance / %"), color=RED)
bt.axhline(85, color=RED, lw=0.6, ls=":")
b1.set_title(T("(a) 碎石图", "(a) Scree plot"), fontsize=11)
names = T(SHORT, SHORT_EN)
x = np.arange(6)
for j, col in enumerate((RED, GREEN, BLUE)):
    b2.bar(x + (j - 1) * 0.26, V[:, j], width=0.26, color=col, label=f"v{'₁₂₃'[j]}（{100 * w[j] / 6:.0f}%）" if T("z", "e") == "z" else f"v{'₁₂₃'[j]} ({100 * w[j] / 6:.0f}%)")
b2.axhline(0, color=INK, lw=0.6)
b2.set_xticks(x)
b2.set_xticklabels(names)
b2.set_ylabel(T("载荷", "loading"))
b2.legend(frameon=False, fontsize=9, ncol=3, loc="lower left")
b2.set_ylim(-0.8, 0.85)
b2.set_title(T("(b) 前三个主成分的载荷", "(b) Loadings of the first three components"), fontsize=11)
for a in (b1, b2):
    for s in ("top",):
        a.spines[s].set_visible(False)
b2.spines["right"].set_visible(False)
fig.tight_layout()
figure(fig, "fig19_2_2")
