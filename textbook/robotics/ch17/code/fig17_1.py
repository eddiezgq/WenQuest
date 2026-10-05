"""17.1 节的示意图。

图 17.1.1：平面 3R 臂（0.425、0.392、0.1 m）只管末端位置时的自运动流形（算例 17.1.1）。
           (a) 目标 A = (0.5, 0.3) m：θ2 > 0、θ2 < 0 两族形态，末端都在 A；(b) 目标 B = (0.75, 0.10) m：一族形态，两支连成一条；
           (c) 两个目标的自运动流形在 (θ1, θ2) 平面上的投影：A 是两条闭曲线，B 是一条。
图 17.1.2：UR5e 弯头焊枪的五维任务（算例 17.1.2）：沿自运动，焊枪绕自身轴线转过 ψ 时 (a) 六个关节角；(b) θ3 与 det J_s。
数据与 ex17_1.py 相同（重算一遍）。
"""
import math

import numpy as np

from _fig17 import C, GOLD2, arm_pts, base_mark, broken, draw_arm, plane, rerun, spines
from _red import jacobian_space, UR_S
from bookout import T, figure, style

plt = style()
E = rerun("ex17_1.py")
L = E["L"]

# ---------------------------------------------------------------- 图 17.1.1
fig = plt.figure(figsize=(12.6, 4.6))
gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 1.05], wspace=0.12)


def fan(ax, arr, color, k, alpha=0.85, lw=4):
    idx = np.linspace(0, len(arr) - 1, k, endpoint=False).astype(int)
    for i in idx:
        draw_arm(ax, arm_pts(arr[i, 1:], L), color, lw=lw, alpha=alpha, jr=0.013)


ax = fig.add_subplot(gs[0])
plane(ax, (-0.12, 0.80), (-0.34, 0.80))
base_mark(ax)
fan(ax, E["A_up"], C["z"], 7)
fan(ax, E["A_dn"], GOLD2, 7)
ax.plot(*E["PA_"], "o", color=C["x"], ms=7, zorder=9)
ax.text(E["PA_"][0] + 0.10, E["PA_"][1] - 0.02, "A", color=C["x"], fontsize=13, weight="bold")
ax.text(-0.11, 0.75, T("(a) 目标 A：d = 0.583 m", "(a) Target A: d = 0.583 m"), fontsize=10.5)
ax.text(-0.11, 0.69, T("θ₂ > 0（蓝）、θ₂ < 0（金）两族，互不相连", "θ₂ > 0 (blue), θ₂ < 0 (gold): two separate families"), fontsize=8.8, color=C["muted"])

ax = fig.add_subplot(gs[1])
plane(ax, (-0.12, 0.95), (-0.44, 0.80))
base_mark(ax)
cmap = plt.get_cmap("viridis")
both = np.vstack([E["B_up"], E["B_dn"][::-1]])
for j, i in enumerate(np.linspace(0, len(both) - 1, 12, endpoint=False).astype(int)):
    draw_arm(ax, arm_pts(both[i, 1:], L), cmap(j / 12 * 0.9), lw=4, alpha=0.9, jr=0.013)
ax.plot(*E["PB_"], "o", color=C["x"], ms=7, zorder=9)
ax.text(E["PB_"][0] + 0.07, E["PB_"][1] + 0.05, "B", color=C["x"], fontsize=13, weight="bold")
t = np.linspace(-0.55, 0.75, 100)
ax.plot((L[0] + L[1]) * np.cos(t), (L[0] + L[1]) * np.sin(t), color=C["muted"], lw=0.8, ls="--")
ax.text(0.0, -0.43, T("腕点能到的外圆 |w| = L₁ + L₂", "outer reach of the wrist |w| = L₁ + L₂"), fontsize=8.5, color=C["muted"])
ax.text(-0.11, 0.75, T("(b) 目标 B：d = 0.757 m", "(b) Target B: d = 0.757 m"), fontsize=10.5)
ax.text(-0.11, 0.69, T("一族：θ₂ > 0 与 θ₂ < 0 两支在 θ₂ = 0 处相接", "one family: the θ₂ > 0 and θ₂ < 0 branches meet at θ₂ = 0"), fontsize=8.8, color=C["muted"])

ax = fig.add_subplot(gs[2])
for arr, col, lab in ((E["A_up"], C["z"], T("A，θ₂ > 0", "A, θ₂ > 0")), (E["A_dn"], GOLD2, T("A，θ₂ < 0", "A, θ₂ < 0"))):
    ax.plot(*broken(np.degrees(arr[:, 1]), np.degrees(arr[:, 2]), 180), color=col, lw=2, label=lab)
Bt1 = np.degrees(both[:, 1])
ax.plot(*broken(Bt1, np.degrees(both[:, 2]), 180), color=cmap(0.45), lw=2.4, ls="-", label=T("B（一条闭曲线）", "B (one closed curve)"))
ax.axhline(0, color=C["muted"], lw=0.8)
ax.set_xlabel("θ₁ / (°)")
ax.set_ylabel("θ₂ / (°)")
ax.set_xlim(-180, 180)
ax.set_xticks(range(-180, 181, 90))
ax.set_ylim(-185, 185)
spines(ax)
ax.legend(fontsize=8.5, frameon=False, loc="lower left")
ax.set_title(T("(c) 自运动流形在 (θ₁, θ₂) 平面上的投影", "(c) Self-motion manifolds projected on (θ₁, θ₂)"), fontsize=10.5, loc="left")
figure(fig, "fig17_1_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 17.1.2
fwd, bwd = E["fwd"], E["bwd"]
allr = np.vstack([np.r_[E["psi_lo"], E["q_lo"]], bwd[::-1], fwd[1:], np.r_[E["psi_hi"], E["q_hi"]]])
psi = np.degrees(allr[:, 0])
fig, axs = plt.subplots(1, 2, figsize=(11.6, 4.0))
ax = axs[0]
cols = [C["x"], C["y"], C["z"], C["accent"], "#8c564b", "#7f7f7f"]
for k in range(6):
    ax.plot(psi, np.degrees(allr[:, k + 1]), color=cols[k], lw=1.8, label="θ" + "₁₂₃₄₅₆"[k])
for v in (E["psi_lo"], E["psi_hi"]):
    ax.axvline(math.degrees(v), color=C["muted"], lw=0.8, ls="--")
ax.set_xlabel(T("焊枪绕自身轴线转过的角 ψ / (°)", "rotation of the torch about its own axis ψ / (°)"))
ax.set_ylabel(T("关节角 / (°)", "joint angle / (°)"))
spines(ax)
ax.legend(fontsize=8.5, ncol=3, frameon=False, loc="upper left")
ax.set_title(T("(a) 枪尖和轴线不动，焊枪绕轴线转动时的关节角", "(a) Joint angles while the torch turns about its axis, tip and axis fixed"), fontsize=10, loc="left")
ax = axs[1]
dets = [np.linalg.det(jacobian_space(UR_S, r[1:])) for r in allr]
ax.plot(psi, np.degrees(allr[:, 3]), color=C["z"], lw=2, label="θ₃ / (°)")
ax2 = ax.twinx()
ax2.plot(psi, np.array(dets) * 1000, color=C["accent"], lw=2, ls="--", label=r"$\det J_s$")
ax2.set_ylabel(r"$\det J_s$" + " × 1000 / m³", color=C["accent"])
ax.set_ylabel("θ₃ / (°)", color=C["z"])
ax.set_xlabel(T("ψ / (°)", "ψ / (°)"))
ax.axhline(0, color=C["muted"], lw=0.8)
ax2.axhline(0, color=C["accent"], lw=0.6, ls=":")
for v in (E["psi_lo"], E["psi_hi"]):
    ax.axvline(math.degrees(v), color=C["muted"], lw=0.8, ls="--")
ax.text(math.degrees(E["psi_lo"]) + 18, 91, T("← 肘部伸直，ψ 到头", "← elbow straight, ψ turns back"), fontsize=8.5, color=C["muted"])
ax.text(math.degrees(E["psi_hi"]) - 3, 91, T("肘部伸直，ψ 到头 →", "elbow straight, ψ turns back →"), fontsize=8.5, color=C["muted"], ha="right")
ax.set_ylim(-5, 100)
spines(ax)
ax.set_title(T("(b) 两端 ", "(b) At both ends ") + r"$\theta_3 \to 0,\ \det J_s \to 0$", fontsize=10, loc="left")
fig.tight_layout()
figure(fig, "fig17_1_2")
plt.close(fig)
