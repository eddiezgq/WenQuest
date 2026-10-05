"""图 14.2.1：两连杆臂末端的柔度椭圆（姿态 (0°, 90°)，关节刚度 2000、1000 N·m/rad）。沿各个方向施加 10 N 的力，
末端位移的端点组成椭圆 d = C F；椭圆的主轴是刚度矩阵的特征向量（互相垂直），长轴方向最软（5764 N/m），短轴方向最硬（24097 N/m）。
竖直向下推 10 N，位移 (0.6, −0.8) mm 偏向软的方向。"""
import numpy as np

from _arm2 import compliance, points
from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

q1, q2 = 0.0, np.radians(90)
C = compliance(q1, q2, 2000.0, 1000.0) * 1e3 * 10          # mm，对 10 N 的力
w, V = np.linalg.eigh(C)
P = points(q1, q2) * 1000                                   # mm
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 4.6), gridspec_kw={"width_ratios": [1, 1.2]})
a1.plot(P[:, 0], P[:, 1], "-", color=INK, lw=5, solid_capstyle="round")
a1.plot(P[:2, 0], P[:2, 1], "o", color="white", mec=INK, ms=9, mew=2)
a1.plot([-40, 40], [-8, -8], color=INK, lw=3)
t = np.linspace(0, 2 * np.pi, 300)
sc = 50                                                     # 位移放大 50 倍画在臂上
E = C @ np.vstack([np.cos(t), np.sin(t)])
a1.plot(P[2, 0] + sc * E[0], P[2, 1] + sc * E[1], color=ACC, lw=2)
a1.set_aspect("equal"); a1.axis("off")
a1.set_xlim(-60, 520); a1.set_ylim(-60, 400)
a1.set_title(T("(a) 姿态 (0°, 90°) 与末端柔度椭圆（放大 50 倍）", "(a) Pose (0°, 90°) and tip compliance ellipse (×50)"), fontsize=11)
ax = a2
ax.set_aspect("equal")
ax.plot(E[0], E[1], color=ACC, lw=2)
for j, c, lab in ((0, RED, T("硬", "stiff")), (1, GREEN, T("软", "soft"))):
    v = V[:, j] * w[j]
    ax.annotate("", xy=v, xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=c, lw=2, mutation_scale=12))
    ax.annotate("", xy=-v, xytext=(0, 0), arrowprops=dict(arrowstyle="-", color=c, lw=1, ls="--"))
    ax.text(v[0] * 1.1 + (-0.25 if j == 0 else 0), v[1] * 1.1 + 0.03, lab, color=c, fontsize=11)
F = np.array([0, -10.0]); d = C @ F / 10
ax.annotate("", xy=(0, -0.5), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.6, mutation_scale=12))
ax.text(0.03, -0.5, T("力 10 N", "force 10 N"), color=BLUE, fontsize=10)
ax.annotate("", xy=d, xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=INK, lw=2, mutation_scale=12))
ax.text(d[0] + 0.05, d[1], T("位移 (0.6, −0.8) mm", "deflection (0.6, −0.8) mm"), color=INK, fontsize=10)
ax.axhline(0, color=MUTED, lw=0.6); ax.axvline(0, color=MUTED, lw=0.6)
ax.set_xlim(-1.9, 1.9); ax.set_ylim(-1.3, 1.3)
ax.set_xlabel("mm"); ax.set_ylabel("mm")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.set_title(T("(b) 10 N 的力产生的位移：主轴互相垂直", "(b) Deflection under 10 N: perpendicular principal axes"), fontsize=11)
fig.tight_layout()
figure(fig, "fig14_2_1")
