"""1.1 节的示意图。

图 1.1.1：感知—决策—执行回路：机器人通过传感器读取环境与自身的状态，控制器按程序作出决策，驱动器使机构运动并改变环境。
图 1.1.2：AGV 的停车距离随速度变化（式 (1.1.4)），标出算例 1.1.1 的点。
"""
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from bookout import COLORS, T, figure, style
from _ch1 import AGV_SPEED as v, STOP_A as a, STOP_TC, STOP_TP, stop_distance as stop_formula

t_d = STOP_TC + STOP_TP
d = stop_formula(v, t_d, a)

plt = style()
C = COLORS


def box(ax, x, y, w, h, title, sub, color):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
                                fc=color, ec=C["ink"], lw=1.0, alpha=0.9))
    ax.text(x, y + 0.11, title, ha="center", va="center", fontsize=12, weight="bold", color=C["ink"])
    ax.text(x, y - 0.13, sub, ha="center", va="center", fontsize=8.5, color=C["ink"])


def arrow(ax, p, q, text="", off=(0, 0), rad=0.0, color=None):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=14, lw=1.4, color=color or C["ink"],
                                 connectionstyle=f"arc3,rad={rad}"))
    if text:
        ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], text, ha="center", va="center", fontsize=9,
                color=C["muted"])


# ---------------------------------------------------------------- 图 1.1.1
fig, ax = plt.subplots(figsize=(7.2, 4.2))
ax.set_xlim(0, 7.2)
ax.set_ylim(0, 4.2)
ax.axis("off")
box(ax, 1.3, 3.0, 1.9, 0.75, T("感知", "Sense"), T("编码器、激光雷达、相机", "encoders, lidar, camera"), "#dbe9f6")
box(ax, 3.6, 3.0, 1.9, 0.75, T("决策", "Decide"), T("控制器中的程序", "program in the controller"), "#f3e2b3")
box(ax, 5.9, 3.0, 1.9, 0.75, T("执行", "Act"), T("驱动器带动机构", "actuators drive the links"), "#dcefdc")
box(ax, 3.6, 0.9, 5.3, 0.8, T("环境与机器人自身的状态 x", "Environment and the robot's own state x"),
    T("工件位置、障碍物、关节角、车速……", "part positions, obstacles, joint angles, speed ..."), "#eceff1")
arrow(ax, (2.27, 3.0), (2.63, 3.0))
arrow(ax, (4.57, 3.0), (4.93, 3.0))
ax.text(2.45, 3.32, "y", ha="center", fontsize=12, style="italic")
ax.text(4.75, 3.32, "u", ha="center", fontsize=12, style="italic")
arrow(ax, (5.9, 2.6), (5.9, 1.33))
ax.text(6.0, 1.95, T("运动改变\n状态", "motion changes\nthe state"), ha="left", va="center", fontsize=9, color=C["muted"])
arrow(ax, (1.3, 1.33), (1.3, 2.6))
ax.text(1.2, 1.95, T("测量", "measure"), ha="right", va="center", fontsize=9, color=C["muted"])
ax.text(3.6, 3.85, T("一个控制周期：读 → 算 → 动，周而复始", "One control cycle: read → compute → move, again and again"),
        ha="center", fontsize=10, color=C["ink"])
ax.text(3.6, 2.15, T("y = h(x)　　u = π(y)　　x 随 u 变化", "y = h(x)    u = π(y)    x changes with u"), ha="center",
        fontsize=10, color=C["accent"])
figure(fig, "fig1_1_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 1.1.2
fig, ax = plt.subplots(figsize=(6.0, 3.8))
vs = np.linspace(0, 2.0, 200)
for td, aa, ls, col in ((t_d, a, "-", C["accent"]), (t_d, 2 * a, "--", C["z"]), (3 * t_d, a, ":", C["x"])):
    ax.plot(vs, stop_formula(vs, td, aa), ls, color=col, lw=1.6,
            label=T(f"反应时间 {td:.1f} s，减速度 {aa:.1f} m/s²", f"reaction {td:.1f} s, deceleration {aa:.1f} m/s²"))
ax.plot([v], [d], "o", color=C["ink"], ms=5, zorder=5)
ax.annotate(T(f"算例 1.1.1：{v:.1f} m/s 时 {d:.1f} m", f"Example 1.1.1: {d:.1f} m at {v:.1f} m/s"), xy=(v, d),
            xytext=(1.08, 0.45), fontsize=9, arrowprops=dict(arrowstyle="-", color=C["muted"], lw=0.8))
ax.set_xlabel(T("车速 v（m/s）", "speed v (m/s)"))
ax.set_ylabel(T("停车距离 d（m）", "stopping distance d (m)"))
ax.set_xlim(0, 2.0)
ax.set_ylim(0, 4.6)
ax.grid(alpha=0.3)
ax.legend(fontsize=8.5, loc="upper left", bbox_to_anchor=(0.0, 0.86), frameon=False)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
figure(fig, "fig1_1_2")
plt.close(fig)
