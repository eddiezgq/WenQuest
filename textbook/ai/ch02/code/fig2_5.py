"""2.5 节的示意图。

图 2.5.2：“月牙”数据：（a）逻辑回归的线性分界；（b）两层网络（16 个 ReLU）学到的弯曲分界。
图 2.5.1：算例 2.5.1 的计算图：黑字为前向计算的值，红字为反向传播得到的梯度 ∂L/∂(节点)。
"""
import math

import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from _ch2 import moons
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

# ---------------------------------------------------------------- 图 2.5.1（与程序 2.5.2 相同的训练）
X, y = moons(200, seed=7)
n, d, m = 200, 2, 16
rng = np.random.default_rng(3)
P = {"W1": rng.normal(0, np.sqrt(2 / d), (d, m)), "b1": np.zeros(m), "W2": rng.normal(0, np.sqrt(2 / m), (m, 1)),
     "b2": np.zeros(1)}


def fwd(P, A):
    Z1 = A @ P["W1"] + P["b1"]
    H = np.maximum(Z1, 0)
    return Z1, H, (H @ P["W2"] + P["b2"]).ravel()


for _ in range(5000):
    Z1, H, z = fwd(P, X)
    dz = (1 / (1 + np.exp(-z)) - y)[:, None] / n
    dZ1 = (dz @ P["W2"].T) * (Z1 > 0)
    for k, gk in (("W2", H.T @ dz), ("b2", dz.sum(0)), ("W1", X.T @ dZ1), ("b1", dZ1.sum(0))):
        P[k] -= 0.5 * gk
Z = np.c_[X, np.ones(n)]
w = np.zeros(3)
for _ in range(5000):
    w -= 0.5 * Z.T @ (1 / (1 + np.exp(-Z @ w)) - y) / n
g1, g2 = np.meshgrid(np.linspace(-1.5, 2.5, 300), np.linspace(-1.1, 1.6, 220))
G = np.c_[g1.ravel(), g2.ravel()]
fig, axs = plt.subplots(1, 2, figsize=(10.4, 3.9))
for ax, zz, title in ((axs[0], np.c_[G, np.ones(len(G))] @ w, T("（a）逻辑回归：分界只能是直线", "(a) Logistic regression: a straight boundary")),
                      (axs[1], fwd(P, G)[2], T("（b）两层网络：分界可以弯曲", "(b) Two-layer network: a curved boundary"))):
    ax.contourf(g1, g2, (zz > 0).reshape(g1.shape), levels=[-0.5, 0.5, 1.5], colors=["#fbe9e7", "#dbe7f3"], alpha=0.8)
    ax.contour(g1, g2, zz.reshape(g1.shape), levels=[0], colors=[C["ink"]], linewidths=1.5)
    ax.plot(X[y == 0, 0], X[y == 0, 1], "s", color=C["x"], ms=3.5)
    ax.plot(X[y == 1, 0], X[y == 1, 1], "o", color=C["z"], ms=3.5, mfc="white")
    ax.set_title(title, fontsize=11)
    ax.set_aspect("equal")
    ax.set_xlabel("$x_1$")
    ax.set_ylabel("$x_2$")
fig.tight_layout()
figure(fig, "fig2_5_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 2.5.2
xv, wv, bv, yv = 1.5, 0.8, -0.3, 1.0
zv = wv * xv + bv
pv = 1 / (1 + math.exp(-zv))
Lv = (pv - yv) ** 2
dLdp = 2 * (pv - yv)
dLdz = dLdp * pv * (1 - pv)
nodes = {  # 名称: (x, y, 值, 梯度)
    "w": (0.6, 3.0, wv, dLdz * xv), "x": (0.6, 1.8, xv, dLdz * wv), "b": (0.6, 0.6, bv, dLdz),
    "u": (2.5, 2.4, wv * xv, dLdz), "z": (4.2, 1.5, zv, dLdz), "p": (6.0, 1.5, pv, dLdp), "L": (7.9, 1.5, Lv, 1.0)}
ops = {"u": "×", "z": "+", "p": "σ", "L": "(·−y)²"}
fig, ax = plt.subplots(figsize=(10.0, 3.8))
ax.set_xlim(0, 9)
ax.set_ylim(0, 4.15)
ax.axis("off")
edges = [("w", "u"), ("x", "u"), ("u", "z"), ("b", "z"), ("z", "p"), ("p", "L")]
for a, b in edges:
    (xa, ya, *_), (xb, yb, *_) = nodes[a], nodes[b]
    ax.add_patch(FancyArrowPatch((xa + 0.45, ya), (xb - 0.45, yb), arrowstyle="-|>", mutation_scale=12, lw=1.2, color=C["ink"]))
    ax.add_patch(FancyArrowPatch((xb - 0.45, yb - 0.12), (xa + 0.45, ya - 0.12), arrowstyle="-|>", mutation_scale=10, lw=1.0,
                                 color=C["x"], ls="--", alpha=0.7))
for k, (xx, yy, v, gr) in nodes.items():
    fc = "#eef3f8" if k in ("w", "x", "b") else "#fdf3dc"
    ax.add_patch(FancyBboxPatch((xx - 0.42, yy - 0.3), 0.84, 0.6, boxstyle="round,pad=0.02,rounding_size=0.1", fc=fc, ec=C["ink"], lw=1.1))
    lab = {"u": "$wx$", "L": "$L$"}.get(k, f"${k}$")
    ax.text(xx, yy + 0.08, lab, ha="center", va="center", fontsize=11)
    ax.text(xx, yy + 0.47, f"{v:.4f}", ha="center", fontsize=9, color=C["ink"])
    ax.text(xx, yy - 0.5, f"{gr:.4f}", ha="center", fontsize=9, color=C["x"])
    if k in ops:
        ax.text(xx - 0.36, yy - 0.2, ops[k], fontsize=8, color=C["muted"])
ax.text(0.1, 4.0, T("黑字：前向计算的值（从左到右）    红字：反向得到的 $\\partial L/\\partial(\\cdot)$（从右到左）",
                    "black: forward values (left to right)    red: $\\partial L/\\partial(\\cdot)$ from the backward pass (right to left)"),
        fontsize=9.5, color=C["ink"])
ax.text(6.95, 0.55, T(f"$y = {yv:g}$", f"$y = {yv:g}$"), fontsize=10, color=C["muted"])
figure(fig, "fig2_5_1")
plt.close(fig)
