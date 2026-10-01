"""4.8 节的示意图。

图 4.8.1：姿态累积更新时偏离正交的程度（与程序 4.8.1 同样的模拟）。
图 4.8.2：正交化的几何意义（示意图：曲线代表 SO(3)，点 M 在曲线外）。
"""
import math

import numpy as np

from _rot import C, rot_axis, skew
from bookout import figure, style

plt = style()


def svd_project(M):
    U, _, Vt = np.linalg.svd(M)
    return U @ np.diag([1, 1, np.sign(np.linalg.det(U @ Vt))]) @ Vt


# ---------------------------------------------------------------- 图 4.8.1
w = np.array([0.3, -0.5, 0.8])
dt, steps = 0.001, 20000
R1, R2, R3 = np.eye(3), np.eye(3), np.eye(3)
E = rot_axis(w, np.linalg.norm(w) * dt)
ts, a, b, c = [], [], [], []
for k in range(1, steps + 1):
    R1 = R1 @ (np.eye(3) + skew(w) * dt)
    R2 = R2 @ E
    R3 = R3 @ (np.eye(3) + skew(w) * dt)
    if k % 100 == 0:
        R3 = svd_project(R3)
    if k % 100 == 50:
        ts.append(k * dt)
        a.append(np.abs(R1.T @ R1 - np.eye(3)).max())
        b.append(np.abs(R2.T @ R2 - np.eye(3)).max())
        c.append(np.abs(R3.T @ R3 - np.eye(3)).max())
fig, ax = plt.subplots(figsize=(5.8, 3.3))
ax.semilogy(ts, a, color=C["x"], lw=1.8, label="一阶近似更新，式 (4.8.6)")
ax.semilogy(ts, np.maximum(b, 1e-17), color=C["z"], lw=1.8, label="罗德里格斯公式精确更新")
ax.semilogy(ts, np.maximum(c, 1e-17), color=C["accent"], lw=1.8, label="一阶更新 + 每 0.1 s 正交化")
ax.set_xlabel("时间（s），每 1 ms 更新一次")
ax.set_ylabel(r"$R^{\mathsf{T}}R$ 偏离 $I$ 的最大值")
ax.legend(fontsize=8.5, frameon=False, loc="center right")
ax.grid(True, lw=0.3, alpha=0.5)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
figure(fig, "fig4_8_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 4.8.2
fig, ax = plt.subplots(figsize=(5.0, 3.0))
x = np.linspace(-1.6, 1.6, 200)
y = -0.35 * x ** 2
ax.plot(x, y, color=C["z"], lw=2.2)
ax.text(1.35, -0.75, "SO(3)", color=C["z"], fontsize=12)
M = np.array([0.35, 0.42])
# 曲线上离 M 最近的点
k = int(np.argmin((x - M[0]) ** 2 + (y - M[1]) ** 2))
S = np.array([x[k], y[k]])
G = np.array([0.95, -0.35 * 0.95 ** 2])
ax.plot(*np.array([M, S]).T, color=C["accent"], lw=1.4)
ax.plot(*np.array([M, G]).T, color=C["muted"], lw=1.2, ls="--")
for p, label, col, dx, dy in ((M, "M（带误差）", C["ink"], 0.06, 0.03), (S, "奇异值分解法", C["accent"], -0.95, -0.2),
                              (G, "格拉姆-施密特法", C["muted"], 0.08, 0.06)):
    ax.plot(*p, "o", color=col, ms=6)
    ax.text(p[0] + dx, p[1] + dy, label, fontsize=10, color=col)
ax.set_xlim(-1.7, 1.9)
ax.set_ylim(-1.0, 0.65)
ax.set_aspect("equal")
ax.axis("off")
figure(fig, "fig4_8_2")
plt.close(fig)
