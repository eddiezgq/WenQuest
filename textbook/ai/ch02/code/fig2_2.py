"""2.2 节的示意图。

图 2.2.1：跑合试验台数据与最小二乘直线，竖线为残差。
图 2.2.2：（a）逻辑函数 σ(z)；（b）零件检验数据上逻辑回归给出的合格概率（等高线）与 p = 0.5 的分界线。
"""
import numpy as np

from _ch2 import PARTS, rig_data
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

# ---------------------------------------------------------------- 图 2.2.1
x, y = rig_data()
X = np.c_[x, np.ones(len(x))]
w = np.linalg.solve(X.T @ X, X.T @ y)
fig, ax = plt.subplots(figsize=(6.8, 4.0))
xx = np.linspace(0, 65, 2)
for xi, yi in zip(x, y):
    ax.plot([xi, xi], [yi, w[0] * xi + w[1]], color=C["x"], lw=0.8, alpha=0.7)
ax.plot(x, y, "o", color=C["z"], ms=5, label=T("试验记录（教学数据）", "test records (teaching data)"))
ax.plot(xx, w[0] * xx + w[1], color=C["accent"], lw=2, label=T(f"最小二乘直线 $\\hat y = {w[0]:.3f}x + {w[1]:.2f}$",
                                                              f"least squares $\\hat y = {w[0]:.3f}x + {w[1]:.2f}$"))
ax.plot([], [], color=C["x"], lw=0.8, label=T("残差 $y_i - \\hat y_i$", "residual $y_i - \\hat y_i$"))
ax.set_xlabel(T("负载转矩 $x$ / (N·m)", "load torque $x$ / (N·m)"))
ax.set_ylabel(T("30 分钟油温温升 $y$ / K", "oil temperature rise after 30 min $y$ / K"))
ax.set_xlim(0, 65)
ax.legend(fontsize=9, frameon=False, loc="upper left")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
figure(fig, "fig2_2_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 2.2.2
P = np.array(PARTS, dtype=float)
Z = np.c_[P[:, :2], np.ones(len(P))]
t = (P[:, 2] > 0).astype(float)
sig = lambda z: 1 / (1 + np.exp(-z))
v = np.zeros(3)
for _ in range(20000):
    v -= 0.5 * (Z.T @ (sig(Z @ v) - t) / len(t) + 0.01 * np.r_[v[:2], 0])
fig, axs = plt.subplots(1, 2, figsize=(10.2, 4.2), gridspec_kw={"width_ratios": [1, 1.2]})
ax = axs[0]
z = np.linspace(-8, 8, 300)
ax.plot(z, sig(z), color=C["z"], lw=2)
ax.axhline(0.5, color=C["muted"], lw=0.8, ls=":")
ax.axvline(0, color=C["muted"], lw=0.8, ls=":")
zl = np.linspace(-2, 2, 2)
ax.plot(zl, 0.5 + zl / 4, color=C["accent"], lw=1, ls="--")
ax.text(2.3, 0.72, T("$z = 0$ 处斜率 $1/4$", "slope $1/4$ at $z = 0$"), fontsize=9, color=C["accent"])
ax.set_ylim(-0.05, 1.05)
ax.set_xlabel("$z$")
ax.set_ylabel("$\\sigma(z) = 1/(1 + e^{-z})$")
ax.set_title(T("（a）逻辑函数", "(a) The logistic function"), fontsize=11)
ax = axs[1]
g1, g2 = np.meshgrid(np.linspace(-0.2, 3.4, 200), np.linspace(-0.2, 3.8, 200))
pp = sig(v[0] * g1 + v[1] * g2 + v[2])
cs = ax.contourf(g1, g2, pp, levels=np.linspace(0, 1, 11), cmap="RdBu", alpha=0.55)
ax.contour(g1, g2, pp, levels=[0.5], colors=[C["ink"]], linewidths=1.8)
for a, b, c in PARTS:
    ax.plot(a, b, "o" if c > 0 else "s", color=C["z"] if c > 0 else C["x"], mfc="white" if c > 0 else C["x"], ms=6, mew=1.5)
cb = fig.colorbar(cs, ax=ax, fraction=0.046, pad=0.03)
cb.set_label(T("合格概率 $p$", "probability of acceptance $p$"))
ax.set_aspect("equal")
ax.set_xlabel(T("$x_1$（10 μm）", "$x_1$ (10 μm)"))
ax.set_ylabel(T("$x_2$（10 μm）", "$x_2$ (10 μm)"))
ax.set_title(T("（b）零件检验数据上的逻辑回归", "(b) Logistic regression on the part data"), fontsize=11)
for a_ in axs:
    for s in ("top", "right"):
        a_.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig2_2_2")
plt.close(fig)
