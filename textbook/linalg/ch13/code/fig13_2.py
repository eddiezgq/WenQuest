"""图 13.2.1：旋转的转轴是特征值 1 的特征向量。R = [[0, 0, 1], [1, 0, 0], [0, 1, 0]] 把 e₁ → e₂ → e₃ → e₁，
是绕 (1, 1, 1) 转 120°：三个坐标轴的端点在垂直于转轴的平面上转圈，转轴上的点不动，Rv = v。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, arrow3, figure, plt, view3

P, _ = view3(30, 20)
fig, ax = plt.subplots(figsize=(5.6, 5.0))
ax.set_aspect("equal"); ax.axis("off")
e = np.eye(3)
for i, (c, n) in enumerate(zip((RED, GREEN, BLUE), ("e₁", "e₂", "e₃"))):
    arrow3(ax, P, (0, 0, 0), e[i], c, n, lw=2.2)
k = np.ones(3) / np.sqrt(3)
arrow3(ax, P, (0, 0, 0), 1.6 * k, INK, T("转轴 (1, 1, 1)：Rv = v", "axis (1, 1, 1): Rv = v"), lw=2.6, size=11, off=(0.05, 0.05))
c0 = np.ones(3) / 3                             # 三个端点所在圆的圆心
u = (e[0] - c0) / np.linalg.norm(e[0] - c0); w = np.cross(k, u)
r = np.linalg.norm(e[0] - c0)
t = np.linspace(0, 2 * np.pi, 200)
circ = np.array([P(c0 + r * (np.cos(a) * u + np.sin(a) * w)) for a in t])
ax.plot(circ[:, 0], circ[:, 1], color=ACC, lw=1.2, ls="--")
for a0 in (0, 120, 240):
    a = np.radians(a0 + 60); b = np.radians(a0 + 75)
    p1, p2 = P(c0 + r * (np.cos(a) * u + np.sin(a) * w)), P(c0 + r * (np.cos(b) * u + np.sin(b) * w))
    ax.annotate("", xy=p2, xytext=p1, arrowprops=dict(arrowstyle="-|>", color=ACC, lw=1.5, mutation_scale=12))
ax.text(*(P(c0) + np.array([0.25, -0.55])), T("e₁ → e₂ → e₃ → e₁，每次转 120°", "e₁ → e₂ → e₃ → e₁, 120° each"), color=ACC, fontsize=10)
pts = np.array([P(x) for x in (np.zeros(3), *e, 1.7 * k)] + list(circ))
lo, hi = pts.min(0), pts.max(0)
ax.set_xlim(lo[0] - 0.3, hi[0] + 1.2); ax.set_ylim(lo[1] - 0.7, hi[1] + 0.3)
figure(fig, "fig13_2_1")
