"""图 3.7.1：AGV 电机驱动电路（直流稳态的简化模型）与四个节点。图 3.7.2：三角形桁架与杆力。图 3.7.3：车间 AGV 路网的四个路口。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle


def resistor(ax, p, q, label, off=(0.12, 0)):
    p, q = np.array(p, float), np.array(q, float)
    d = q - p
    L = np.linalg.norm(d)
    u = d / L
    n = np.array([-u[1], u[0]])
    a, b = p + 0.3 * d, p + 0.7 * d
    ax.plot(*zip(p, a), color=INK, lw=1.5)
    ax.plot(*zip(b, q), color=INK, lw=1.5)
    zz = [a + t * (b - a) + (0.06 if k % 2 else -0.06) * n * (0 < k < 7) for k, t in enumerate(np.linspace(0, 1, 8))]
    ax.plot(*zip(*zz), color=INK, lw=1.5)
    m = (a + b) / 2
    ax.text(m[0] + off[0], m[1] + off[1], label, fontsize=9.5, va="center")


fig, ax = plt.subplots(figsize=(8.6, 4.4))
N = {1: (2.2, 3.0), 2: (4.4, 3.0), 3: (4.4, 0.9), 4: (6.4, 0.9)}
# 电池与内阻
ax.add_patch(Circle((0.4, 1.95), 0.32, fill=False, color=INK, lw=1.5))
ax.text(0.4, 1.95, "24 V", ha="center", va="center", fontsize=9)
ax.text(0.55, 2.3, "+", fontsize=11)
ax.text(0.55, 1.45, "−", fontsize=11)
ax.plot([0.4, 0.4], [2.27, 3.0], color=INK, lw=1.5)
ax.plot([0.4, 0.4], [1.63, 0.0], color=INK, lw=1.5)
resistor(ax, (0.4, 3.0), N[1], T("rb 0.2 Ω", "rb 0.2 Ω"), (-0.45, 0.22))
resistor(ax, N[1], (2.2, 0.0), T("控制板 48 Ω", "controller 48 Ω"), (0.12, 0))
resistor(ax, N[1], N[2], T("上管 0.05 Ω", "high side 0.05 Ω"), (-0.45, 0.22))
# 电机：电枢电阻 + 反电动势
resistor(ax, N[2], (4.4, 2.0), T("电枢 1.2 Ω", "armature 1.2 Ω"), (0.12, 0))
ax.add_patch(Circle((4.4, 1.55), 0.28, fill=False, color=INK, lw=1.5))
ax.text(4.4, 1.55, "Em", ha="center", va="center", fontsize=9)
ax.plot([4.4, 4.4], [2.0, 1.83], color=INK, lw=1.5)
ax.plot([4.4, 4.4], [1.27, N[3][1]], color=INK, lw=1.5)
ax.text(4.75, 1.75, "+", fontsize=11)
ax.text(4.75, 1.25, "−", fontsize=11)
resistor(ax, N[3], N[4], T("下管 0.05 Ω", "low side 0.05 Ω"), (-0.45, -0.25))
resistor(ax, N[4], (6.4, 0.0), T("采样 0.1 Ω", "sense 0.1 Ω"), (0.12, 0))
ax.plot([0.4, 6.4], [0.0, 0.0], color=INK, lw=1.5)
ax.plot([2.2, 2.2], [3.0, 3.0], color=INK)
for k, (x, y) in N.items():
    ax.plot(x, y, "o", color=RED, ms=7, zorder=5)
    ax.text(x + 0.08, y + 0.15, f"{k}", color=RED, fontsize=12, fontweight="bold")
for x in np.linspace(3.0, 4.0, 3):
    pass
ax.plot([3.2, 3.6], [-0.15, -0.15], color=INK, lw=1.5)
ax.plot([3.3, 3.5], [-0.25, -0.25], color=INK, lw=1.5)
ax.plot([3.4, 3.4], [0, -0.15], color=INK, lw=1.5)
ax.text(3.65, -0.25, T("地（0 V）", "ground (0 V)"), fontsize=9, color=MUTED)
ax.set_xlim(-0.2, 7.6)
ax.set_ylim(-0.5, 3.5)
ax.set_aspect("equal")
ax.axis("off")
fig.tight_layout()
figure(fig, "fig3_7_1")

A, B, C = np.array([0.0, 0]), np.array([2.0, 0]), np.array([1.0, 1.5])
f = {"AB": 433.3, "AC": -420.6, "BC": -781.2}
fig, ax = plt.subplots(figsize=(6.4, 4.2))
for (p, q), key in (((A, B), "AB"), ((A, C), "AC"), ((B, C), "BC")):
    col = BLUE if f[key] > 0 else RED
    ax.plot(*zip(p, q), color=col, lw=5, solid_capstyle="round")
    m = (p + q) / 2
    ax.text(m[0] + (-0.45 if key == "AC" else 0.1 if key == "BC" else -0.25), m[1] + (-0.2 if key == "AB" else 0.0),
            f"{key}: {f[key]:+.0f} N", color=col, fontsize=10)
for P, name in ((A, "A"), (B, "B"), (C, "C")):
    ax.add_patch(Circle(P, 0.05, color="white", ec=INK, zorder=5))
    ax.text(P[0] - 0.15, P[1] + 0.1, name, fontsize=12)
ax.add_patch(FancyArrowPatch(C, C + np.array([0.0, -0.6]), arrowstyle="-|>", mutation_scale=15, color=INK, lw=2))
ax.add_patch(FancyArrowPatch(C, C + np.array([0.3, 0.0]), arrowstyle="-|>", mutation_scale=15, color=INK, lw=2))
ax.text(C[0] + 0.05, C[1] - 0.75, "1000 N", fontsize=10)
ax.text(C[0] + 0.32, C[1] + 0.05, "200 N", fontsize=10)
ax.plot([A[0] - 0.15, A[0], A[0] + 0.15, A[0] - 0.15], [-0.25, 0, -0.25, -0.25], color=INK)
ax.add_patch(Circle((B[0], -0.13), 0.1, fill=False, ec=INK))
ax.plot([-0.4, 2.4], [-0.25, -0.25], color=MUTED, lw=1)
ax.text(-0.4, 1.7, T("蓝：拉；红：压", "blue: tension; red: compression"), fontsize=9, color=MUTED)
ax.set_xlim(-0.6, 2.6)
ax.set_ylim(-0.5, 1.9)
ax.set_aspect("equal")
ax.axis("off")
fig.tight_layout()
figure(fig, "fig3_7_2")

fig, ax = plt.subplots(figsize=(5.8, 4.6))
P = {1: (0, 2), 2: (3, 2), 3: (3, 0), 4: (0, 0)}
for a, b, name in ((1, 2, "f₁₂"), (2, 3, "f₂₃"), (3, 4, "f₃₄"), (4, 1, "f₄₁")):
    p, q = np.array(P[a], float), np.array(P[b], float)
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=16, color=BLUE, lw=2, shrinkA=14, shrinkB=14))
    m = (p + q) / 2
    ax.text(m[0] + (0.15 if a in (2, 4) else 0), m[1] + (0.15 if a in (1, 3) else 0), name, color=BLUE, fontsize=12, ha="center")
ext = {1: ((-0.9, 2.6), T("进 300", "in 300")), 2: ((3.9, 2.6), T("出 200", "out 200")), 3: ((3.9, -0.6), T("进 100", "in 100")), 4: ((-0.9, -0.6), T("出 200", "out 200"))}
for k, ((x, y), txt) in ext.items():
    p = np.array(P[k], float)
    src, dst = ((np.array([x, y]), p) if "进" in txt or "in" in txt else (p, np.array([x, y])))
    ax.add_patch(FancyArrowPatch(src, dst, arrowstyle="-|>", mutation_scale=14, color=ACC, lw=1.6, shrinkA=10, shrinkB=10))
    ax.text(x, y + (0.15 if y > 1 else -0.3), txt, color=ACC, fontsize=10, ha="center")
for k, (x, y) in P.items():
    ax.add_patch(Circle((x, y), 0.22, color="white", ec=INK, zorder=4))
    ax.text(x, y, str(k), ha="center", va="center", fontsize=12, zorder=5)
ax.set_xlim(-1.4, 4.4)
ax.set_ylim(-1.1, 3.1)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title(T("车间 AGV 路网（辆/小时）", "Workshop AGV network (vehicles/hour)"), fontsize=11)
fig.tight_layout()
figure(fig, "fig3_7_3")
