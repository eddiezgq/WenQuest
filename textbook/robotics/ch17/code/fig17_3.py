"""17.3 节的示意图。

图 17.3.1：避限位（算例 17.3.1）。Panda 在 4 s 内把手向后、向右、向下移动并绕竖直轴转 80°：(a) 关节 2 与关节 4 的角度，
           只用伪逆时关节 2 越过下限 −101°；(b) 式 (15.4.6) 的 H 随时间的变化。
图 17.3.3：避障（算例 17.3.3）。(a) 平面 3R 臂末端固定，圆形障碍物从上方压向肘部：只用伪逆时手臂不动、被压到；加上避障的
           次要任务后，肘部让开；(b) Panda 的手固定在 ready 姿态，球形障碍物从后方移向肘部：手臂到障碍物表面的距离。
图 17.3.2：提高可操作度（算例 17.3.2）。(a) 沿 17.2 节那条自运动闭曲线的可操作度，以及两次梯度上升的起点和终点；
           (b) 梯度上升过程中 w 随时间的变化。
数据与 ex17_3.py 相同（重算一遍）。
"""
import math

import numpy as np

from _fig17 import C, GOLD2, arm_pts, base_mark, draw_arm, plane, rerun, spines
from _red import PA_HI, PA_LO, PL, manip, pa_js
from bookout import T, figure, style

plt = style()
E = rerun("ex17_3.py")

# ---------------------------------------------------------------- 图 17.3.1
R0, R1 = E["R0"], E["R1"]
fig, axs = plt.subplots(1, 2, figsize=(11.6, 4.0))
ax = axs[0]
t = R0[:, 0]
ax.plot(t, np.degrees(R0[:, 2]), color=C["x"], lw=2, label=T("θ₂：只用伪逆", "θ₂: pseudoinverse only"))
ax.plot(t, np.degrees(R1[:, 2]), color=C["z"], lw=2, label=T("θ₂：加避限位项", "θ₂: with limit avoidance"))
ax.plot(t, np.degrees(R0[:, 4]), color=C["x"], lw=1.4, ls="--", label=T("θ₄：只用伪逆", "θ₄: pseudoinverse only"))
ax.plot(t, np.degrees(R1[:, 4]), color=C["z"], lw=1.4, ls="--", label=T("θ₄：加避限位项", "θ₄: with limit avoidance"))
for v, lab in ((PA_LO[1], T("关节 2 下限 −101°", "joint 2 lower limit −101°")), (PA_LO[3], T("关节 4 下限 −176°", "joint 4 lower limit −176°"))):
    ax.axhline(math.degrees(v), color=C["muted"], lw=1.0, ls=":")
    ax.text(0.05, math.degrees(v) + 2.5, lab, fontsize=8.5, color=C["muted"])
ax.set_ylim(-190, -30)
ax.set_xlabel(T("时间 t / s", "time t / s"))
ax.set_ylabel(T("关节角 / (°)", "joint angle / (°)"))
spines(ax)
ax.legend(fontsize=8.2, frameon=False, loc="upper right", ncol=2)
ax.set_title(T("(a) 关节 2 与关节 4", "(a) Joints 2 and 4"), fontsize=10.5, loc="left")
ax = axs[1]
ax.plot(t, R0[:, 8], color=C["x"], lw=2, label=T("只用伪逆", "pseudoinverse only"))
ax.plot(t, R1[:, 8], color=C["z"], lw=2, label=T("加避限位项（k = 5）", "with limit avoidance (k = 5)"))
ax.set_xlabel(T("时间 t / s", "time t / s"))
ax.set_ylabel(T("H(θ)（式 (15.4.6)）", "H(θ) (Eq. (15.4.6))"))
spines(ax)
ax.legend(fontsize=9, frameon=False, loc="upper left")
ax.set_title(T("(b) 离限位中点的程度 H", "(b) Distance from the mid-range, H"), fontsize=10.5, loc="left")
fig.tight_layout()
figure(fig, "fig17_3_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 17.3.2
fig, axs = plt.subplots(1, 2, figsize=(11.8, 4.5), gridspec_kw={"width_ratios": [1, 1.1]})
ax = axs[0]
plane(ax, (-0.08, 0.80), (-0.08, 1.0))
base_mark(ax)
PL0, PL1 = E["PL0"], E["PL1"]
import matplotlib.patches as mp
for k, a in ((0, 0.25), (len(PL0) // 3, 0.45), (2 * len(PL0) // 3, 0.7), (len(PL0) - 1, 1.0)):
    c = PL1[k, 5:7]
    ax.add_patch(mp.Circle(c, E["PRAD"], facecolor=C["x"], alpha=0.12 + 0.3 * a, edgecolor=C["x"], lw=0.8, zorder=1))
draw_arm(ax, arm_pts(PL0[-1, 2:5], PL), C["muted"], lw=5, alpha=0.6, ls="-")
draw_arm(ax, arm_pts(PL1[-1, 2:5], PL), C["z"], lw=5)
EL = np.array([arm_pts(r[2:5], PL)[1] for r in PL1])
ax.plot(*EL.T, color=C["accent"], lw=1.6)
ax.annotate("", xy=E["PC1"] + np.array([0, 0.07]), xytext=E["PC0"] + np.array([0, -0.06]),
            arrowprops=dict(arrowstyle="-|>", color=C["x"], lw=1.2))
ax.plot(*E["PT"], "o", color=C["ink"], ms=5)
ax.text(E["PT"][0] - 0.02, E["PT"][1] - 0.08, T("末端固定", "tip fixed"), fontsize=9)
ax.text(E["PC0"][0] + 0.03, E["PC0"][1] - 0.22, T("障碍物下压", "obstacle\ncoming down"), fontsize=9, color=C["x"])
ax.text(-0.07, 0.96, T("(a) 平面 3R 臂", "(a) Planar 3R arm"), fontsize=10.5)
ax.text(0.33, 0.86, T("灰：只用伪逆（不动，被压到）\n蓝：加避障项，金线为肘点的路径", "grey: pseudoinverse only (stays, gets hit)\nblue: with avoidance; gold: path of the elbow"),
        fontsize=8.6, color=C["muted"], va="top")
ax = axs[1]
O0, O1 = E["O0"], E["O1"]
ax.plot(O0[:, 0], O0[:, 1] * 100, color=C["x"], lw=2, label=T("只用伪逆", "pseudoinverse only"))
ax.plot(O1[:, 0], O1[:, 1] * 100, color=C["z"], lw=2, label=T("加避障项", "with obstacle avoidance"))
ax.axhline(0, color=C["ink"], lw=0.8)
ax.axhline(E["D_ACT"] * 100, color=C["muted"], lw=0.9, ls="--")
ax.text(0.05, E["D_ACT"] * 100 + 0.6, T("开始避让的距离 0.12 m", "avoidance starts at 0.12 m"), fontsize=8.5, color=C["muted"])
ax.text(2.6, -3.2, T("负值：已经撞上", "negative: collision"), fontsize=8.5, color=C["x"])
ax.set_xlabel(T("时间 t / s", "time t / s"))
ax.set_ylabel(T("手臂到障碍物表面的距离 / cm", "distance from the arm to the obstacle / cm"))
spines(ax)
ax.legend(fontsize=9, frameon=False, loc="upper right")
ax.set_title(T("(b) Panda：手固定在 ready 姿态，障碍物从后方移向肘部", "(b) Panda, hand fixed at ready, obstacle approaching the elbow from behind"), fontsize=10, loc="left")
fig.tight_layout()
figure(fig, "fig17_3_3")
plt.close(fig)

# ---------------------------------------------------------------- 图 17.3.3
P, s_of = E["P"], E["s_of"]
w = np.array([manip(pa_js(q)) for q in P])
o = np.argsort(s_of)
fig, axs = plt.subplots(1, 2, figsize=(11.6, 3.9))
ax = axs[0]
ax.plot(s_of[o], w[o], color=C["ink"], lw=1.8)
for k_, k2, col, lab, dx, dy, ha in ((E["k_a"], 0, C["z"], T("从 s = −1 出发", "start at s = −1"), -0.1, -0.0035, "center"),
                                     (E["k_b"], E["k_stop"], GOLD2, T("从 s = −3 出发", "start at s = −3"), -0.2, -0.0012, "right")):
    ax.plot(s_of[k_], w[k_], "o", color=col, ms=7, mfc="white", mew=2)
    ax.annotate("", xy=(s_of[k2], w[k2] + 0.0006), xytext=(s_of[k_], w[k_] + 0.0006),
                arrowprops=dict(arrowstyle="-|>", color=col, lw=1.6, connectionstyle="arc3,rad=-0.35"))
    ax.plot(s_of[k2], w[k2], "*", color=col, ms=11)
    ax.text(s_of[k_] + dx, w[k_] + dy, lab, fontsize=8.8, color=col, ha=ha)
ax.text(0.1, w[0] + 0.0012, T("ready：全局最大", "ready: global maximum"), fontsize=8.8)
ax.text(E["s_stop"] - 0.2, w[E["k_stop"]] + 0.0025, T("局部最大", "local maximum"), fontsize=8.8, color=GOLD2, ha="center")
ax.set_xlabel(T("沿自运动的弧长 s / rad", "arc length along the self-motion s / rad"))
ax.set_ylabel(T("可操作度 w", "manipulability w"))
ax.set_ylim(0.045, 0.086)
spines(ax)
ax.set_title(T("(a) 梯度上升只能爬到最近的山顶", "(a) Gradient ascent climbs only to the nearest peak"), fontsize=10.5, loc="left")
ax = axs[1]
ax.plot(E["Ha"][:, 0], E["Ha"][:, 1], color=C["z"], lw=2, label=T("从 s = −1 出发", "start at s = −1"))
ax.plot(E["Hb"][:, 0], E["Hb"][:, 1], color=GOLD2, lw=2, label=T("从 s = −3 出发", "start at s = −3"))
ax.axhline(E["w_ready"], color=C["muted"], lw=0.9, ls="--")
ax.set_xlabel(T("时间 t / s", "time t / s"))
ax.set_ylabel(T("可操作度 w", "manipulability w"))
spines(ax)
ax.legend(fontsize=9, frameon=False, loc="lower right")
ax.set_title(T("(b) 零空间里的梯度上升（k = 50），手始终不动", "(b) Gradient ascent in the null space (k = 50), hand still"), fontsize=10.5, loc="left")
fig.tight_layout()
figure(fig, "fig17_3_2")
plt.close(fig)
