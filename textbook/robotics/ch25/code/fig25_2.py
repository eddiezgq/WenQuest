"""25.2 节的示意图。

图 25.2.1：连杆 i 的受力：关节 i 传来的 ℱ_i，关节 i+1 处被下一个连杆反作用的 −[Ad_{T_{i+1,i}}]ᵀℱ_{i+1}，合力旋量等于 𝒢_i𝒱̇_i − [ad_{𝒱_i}]ᵀ𝒢_i𝒱_i；
          关节 i 处的 ℱ_i 分成绕轴力矩（电机）、弯曲力矩、轴向力、径向力（轴承与减速器）。
图 25.2.2：算例 25.2.2：上下料动作中关节 2 传给大臂的力：(a) 绕轴力矩（关节力矩）与弯曲力矩；(b) 轴向力与径向力；
          实线为实际动作，虚线为同样的姿态但动作极慢（只有重力）。
"""
import math

import numpy as np

from _ch25 import cell_move, payload_parts, quintic, split_wrench, ur_chain
from bookout import COLORS as C, T, figure, style

plt = style()


def arrow(ax, p, q, color, lw=1.6, ms=13):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=ms, shrinkA=0, shrinkB=0))


def curl(ax, c, r, a0, a1, color, lw=1.4):
    t = np.linspace(a0, a1, 40)
    ax.plot(c[0] + r * np.cos(t), c[1] + r * np.sin(t), color=color, lw=lw)
    p = np.array([c[0] + r * math.cos(t[-2]), c[1] + r * math.sin(t[-2])])
    q = np.array([c[0] + r * math.cos(t[-1]), c[1] + r * math.sin(t[-1])])
    arrow(ax, p, q, color, lw=lw, ms=11)


# ---------------------------------------------------------------- 图 25.2.1
fig, axs = plt.subplots(1, 2, figsize=(11.0, 4.4), gridspec_kw=dict(width_ratios=[1.35, 1]))
ax = axs[0]
ax.set_aspect("equal")
ax.axis("off")
P0, P1 = np.array([0.0, 0.0]), np.array([3.2, 1.3])
u = (P1 - P0) / np.linalg.norm(P1 - P0)
nrm = np.array([-u[1], u[0]])
w = 0.28
pts = np.array([P0 + nrm * w, P1 + nrm * w, P1 - nrm * w, P0 - nrm * w])
ax.add_patch(plt.Polygon(pts, closed=True, fc="#dbe9f6", ec=C["ink"], lw=1.1, zorder=2))
for P in (P0, P1):
    ax.add_patch(plt.Circle(P, 0.2, fc="white", ec=C["ink"], lw=1.2, zorder=3))
ax.text(*(0.5 * (P0 + P1) + nrm * 0.05), T("连杆 i", "link i"), ha="center", va="center", fontsize=11, zorder=4)
ax.text(*(P0 + np.array([0.3, -0.62])), T("关节 i", "joint i"), fontsize=10, color=C["muted"])
ax.text(*(P1 + np.array([-0.2, 0.42])), T("关节 i+1", "joint i+1"), fontsize=10, color=C["muted"])
# 关节 i 处：ℱ_i（来自连杆 i−1）
arrow(ax, P0 + np.array([-1.0, -0.6]), P0 + np.array([-0.18, -0.1]), C["x"])
curl(ax, P0, 0.45, math.radians(140), math.radians(260), C["x"])
ax.text(-1.55, -0.95, r"$\mathcal{F}_i$" + T("（来自连杆 i−1）", " (from link i−1)"), fontsize=11, color=C["x"])
# 关节 i+1 处：−Adᵀℱ_{i+1}
arrow(ax, P1 + np.array([0.15, 0.08]), P1 + np.array([1.0, 0.65]), C["z"])
curl(ax, P1, 0.45, math.radians(-40), math.radians(60), C["z"])
ax.text(P1[0] - 0.6, P1[1] + 1.05, r"$-[\mathrm{Ad}_{T_{i+1,i}}]^{\mathrm{T}}\mathcal{F}_{i+1}$", fontsize=11, color=C["z"])
ax.text(P1[0] + 0.2, P1[1] - 0.95, T("（连杆 i+1 的反作用）", "(reaction of link i+1)"), fontsize=10, color=C["z"])
ax.text(-1.4, 2.65, T("两者之和 = ", "their sum = ") + r"$\mathcal{G}_i\dot{\mathcal{V}}_i - [\mathrm{ad}_{\mathcal{V}_i}]^{\mathrm{T}}\mathcal{G}_i\mathcal{V}_i$"
        + T("（重力已算进 $\\dot{\\mathcal{V}}_0$）", " (gravity is in $\\dot{\\mathcal{V}}_0$)"), fontsize=11, color=C["ink"])
ax.set_xlim(-1.8, 5.0)
ax.set_ylim(-1.3, 3.0)
ax.set_title(T("(a) 连杆 i 的受力", "(a) forces on link i"), fontsize=11)
# (b) 关节处的分解
ax = axs[1]
ax.set_aspect("equal")
ax.axis("off")
# 画一个圆柱形关节（轴竖直）
ax.add_patch(plt.Rectangle((-0.6, -0.9), 1.2, 1.8, fc="#eef2f4", ec=C["ink"], lw=1.1))
ax.plot([0, 0], [-1.5, 1.7], color=C["muted"], lw=1.0, ls="-.")
ax.text(0.08, 1.6, T("关节轴 ω", "axis ω"), fontsize=10, color=C["muted"])
curl(ax, np.array([0, 1.15]), 0.38, math.radians(200), math.radians(340), C["x"], lw=1.8)
ax.text(-1.95, 1.3, T("绕轴力矩 = 关节力矩\n（电机）", "moment about the axis\n= joint torque (motor)"), fontsize=10, color=C["x"])
arrow(ax, np.array([0, -0.9]), np.array([0, -1.45]), C["z"], lw=1.8)
ax.text(0.12, -1.45, T("轴向力", "axial force"), fontsize=10, color=C["z"])
arrow(ax, np.array([0.6, 0.0]), np.array([1.35, 0.0]), C["z"], lw=1.8)
ax.text(1.0, 0.12, T("径向力", "radial force"), fontsize=10, color=C["z"])
curl(ax, np.array([0.0, 0.0]), 1.1, math.radians(-60), math.radians(-15), C["accent"], lw=1.8)
ax.text(1.0, -1.1, T("弯曲（倾覆）力矩", "tilting moment"), fontsize=10, color=C["accent"])
ax.text(-1.95, -2.05, T("后三者由轴承、减速器承受", "the last three are taken by the bearings and the gearbox"), fontsize=10, color=C["ink"])
ax.set_xlim(-2.0, 2.6)
ax.set_ylim(-2.3, 2.1)
ax.set_title(T("(b) 关节处力旋量的四个部分", "(b) the four parts of the wrench at a joint"), fontsize=11)
fig.tight_layout()
figure(fig, "fig25_2_1")

# ---------------------------------------------------------------- 图 25.2.2
thA, thB, T_move = cell_move()
ch = ur_chain(payload=payload_parts())
Z = np.zeros(6)
ts = np.linspace(0, T_move, 400)
dyn, st = [], []
for t in ts:
    q, qd, qdd = quintic(thA, thB, T_move, t)
    _, Fd, _ = ch.rnea(q, qd, qdd, full=True)
    _, Fs, _ = ch.rnea(q, Z, Z, full=True)
    dyn.append(split_wrench(Fd[1], ch.A[1][:3]))
    st.append(split_wrench(Fs[1], ch.A[1][:3]))
dyn, st = np.array(dyn), np.array(st)
fig, axs = plt.subplots(1, 2, figsize=(11.0, 3.8))
ax = axs[0]
ax.plot(ts, np.abs(dyn[:, 0]), color=C["x"], lw=1.8, label=T("绕轴力矩 |τ₂|", "about the axis |τ₂|"))
ax.plot(ts, np.abs(st[:, 0]), color=C["x"], lw=1.2, ls="--")
ax.plot(ts, dyn[:, 1], color=C["accent"], lw=1.8, label=T("弯曲力矩", "tilting moment"))
ax.plot(ts, st[:, 1], color=C["accent"], lw=1.2, ls="--")
ax.set_xlabel(T("时间 t / s", "time t / s"))
ax.set_ylabel(T("力矩 / (N·m)", "moment / (N·m)"))
ax.set_title(T("(a) 关节 2 的力矩（虚线：只有重力）", "(a) moments at joint 2 (dashed: gravity only)"), fontsize=11)
ax.legend(fontsize=9, frameon=False)
ax.grid(alpha=0.25)
ax.set_xlim(0, T_move)
ax = axs[1]
ax.plot(ts, np.abs(dyn[:, 2]), color=C["z"], lw=1.8, label=T("轴向力", "axial force"))
ax.plot(ts, np.abs(st[:, 2]), color=C["z"], lw=1.2, ls="--")
ax.plot(ts, dyn[:, 3], color=C["y"], lw=1.8, label=T("径向力", "radial force"))
ax.plot(ts, st[:, 3], color=C["y"], lw=1.2, ls="--")
ax.set_xlabel(T("时间 t / s", "time t / s"))
ax.set_ylabel(T("力 / N", "force / N"))
ax.set_title(T("(b) 关节 2 的力（虚线：只有重力）", "(b) forces at joint 2 (dashed: gravity only)"), fontsize=11)
ax.legend(fontsize=9, frameon=False)
ax.grid(alpha=0.25)
ax.set_xlim(0, T_move)
fig.tight_layout()
figure(fig, "fig25_2_2")
