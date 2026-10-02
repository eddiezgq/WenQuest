"""1.3 节的示意图。

图 1.3.1：机器人的两种分类：按用途（ISO 8373），按机械结构与移动方式；叶子上标出零件库中的模型。
图 1.3.2：两种结构的工作空间：SCARA 的俯视图（由关节限位算出），UR5e 的侧视图（法兰中心的随机样本）。
"""
import math

import numpy as np
from matplotlib.patches import FancyBboxPatch

from _ch1 import entry, fk_point
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS


def node(ax, x, y, text, fc="#eef2f5", w=1.7, h=0.42, fs=9.2, bold=False):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc,
                                ec=C["ink"], lw=0.8))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, weight="bold" if bold else "normal", color=C["ink"])


def link(ax, p, q):
    ym = (p[1] + q[1]) / 2
    ax.plot([p[0], p[0], q[0], q[0]], [p[1], ym, ym, q[1]], color=C["muted"], lw=0.9, zorder=0)


# ---------------------------------------------------------------- 图 1.3.1
fig, (axa, axb) = plt.subplots(2, 1, figsize=(10.2, 6.6), gridspec_kw={"height_ratios": [1, 1.55]})
for ax in (axa, axb):
    ax.axis("off")
# (a) 按用途
axa.set_xlim(0, 10.45)
axa.set_ylim(0, 2.6)
node(axa, 5.1, 2.2, T("机器人（按用途）", "Robots (by use)"), "#f3e2b3", w=2.6, bold=True)
use = [(1.7, T("工业机器人", "industrial robot"), T("UR5e、Panda、SCARA、Delta", "UR5e, Panda, SCARA, Delta")),
       (5.1, T("服务机器人", "service robot"), T("个人用：扫地机器人\n专业用：物流、清洁、巡检", "personal: robot vacuum\nprofessional: logistics, cleaning, inspection")),
       (8.5, T("医疗机器人", "medical robot"), T("手术、康复", "surgery, rehabilitation"))]
for x, name, ex in use:
    link(axa, (5.1, 2.0), (x, 1.37))
    node(axa, x, 1.15, name, "#dbe9f6", w=2.3)
    axa.text(x, 0.55, ex, ha="center", va="center", fontsize=8.4, color=C["muted"], linespacing=1.4)
axa.text(0.0, 2.45, "(a)", fontsize=10)
# (b) 按结构与移动方式
axb.set_xlim(0, 10.45)
axb.set_ylim(0, 4.1)
axb.text(0.0, 3.95, "(b)", fontsize=10)
node(axb, 5.1, 3.65, T("机器人（按结构与移动方式）", "Robots (by structure and mobility)"), "#f3e2b3", w=3.6, bold=True)
mid = [(2.3, T("固定基座的操作臂", "fixed-base manipulators")), (7.9, T("移动机器人", "mobile robots"))]
for x, t in mid:
    link(axb, (5.1, 3.44), (x, 2.98))
    node(axb, x, 2.78, t, "#dbe9f6", w=2.8)
leaves_l = [(0.75, T("串联关节型", "articulated"), "UR5e\nPanda"), (2.3, "SCARA", T("问渠\nSCARA", "WenQuest\nSCARA")),
            (3.85, T("并联", "parallel"), "Delta")]
leaves_r = [(5.55, T("轮式", "wheeled"), T("差速小车\n(AGV)", "diff-drive\ncart (AGV)")), (6.95, T("足式", "legged"), "Go2"),
            (8.35, T("仿人", "humanoid"), "G1"), (9.75, T("空中", "aerial"), T("四旋翼\nX2", "quadrotor\nX2"))]
for x, t, ex in leaves_l:
    link(axb, (2.3, 2.57), (x, 1.92))
    node(axb, x, 1.72, t, "#dcefdc", w=1.4, fs=8.8)
    axb.text(x, 0.95, ex, ha="center", va="center", fontsize=8.4, color=C["muted"], linespacing=1.3)
for x, t, ex in leaves_r:
    link(axb, (7.9, 2.57), (x, 1.92))
    node(axb, x, 1.72, t, "#dcefdc", w=1.22, fs=8.8)
    axb.text(x, 0.95, ex, ha="center", va="center", fontsize=8.4, color=C["muted"], linespacing=1.3)
axb.text(5.1, 0.15, T("还有水下机器人、移动操作机器人（移动底盘 + 机械臂）等，零件库中暂无模型",
                      "There are also underwater robots and mobile manipulators (mobile base + arm); not yet in the library"),
         ha="center", fontsize=8.6, color=C["muted"])
fig.subplots_adjust(hspace=0.05)
figure(fig, "fig1_3_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 1.3.2
sc = entry("B-SCA-WQ4")
J = {j["name"]: j for j in sc["robot"]["joints"]}
a1, a2 = J["J2"]["origin"]["xyz"][0], J["J3"]["origin"]["xyz"][0]
l1, l2 = J["J1"]["limit"]["upper"], J["J2"]["limit"]["upper"]
rng = np.random.default_rng(132)
t1 = rng.uniform(-l1, l1, 60000)
t2 = rng.uniform(-l2, l2, 60000)
px = a1 * np.cos(t1) + a2 * np.cos(t1 + t2)
py = a1 * np.sin(t1) + a2 * np.sin(t1 + t2)

ur = entry("B-ARM-UR5E")
names = [j["name"] for j in ur["robot"]["joints"]]
pts = np.array([fk_point(ur, dict(zip(names, rng.uniform(-math.pi, math.pi, 6))), "wrist_3_link", (0, 0.1, 0))
                for _ in range(6000)])
rh = np.hypot(pts[:, 0], pts[:, 1]) * np.sign(pts[:, 0] + 1e-12)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 4.4))
ax1.plot(px, py, ".", ms=0.6, color=C["z"], alpha=0.35)
th = np.linspace(0, 2 * np.pi, 300)
ax1.plot((a1 + a2) * np.cos(th), (a1 + a2) * np.sin(th), "--", color=C["muted"], lw=0.8)
ax1.plot([0, a1 * math.cos(0.5), a1 * math.cos(0.5) + a2 * math.cos(0.5 - 1.2)],
         [0, a1 * math.sin(0.5), a1 * math.sin(0.5) + a2 * math.sin(0.5 - 1.2)], "-o", color=C["ink"], lw=2.2, ms=4)
ax1.set_aspect("equal")
ax1.set_title(T("SCARA 俯视：末端能到达的水平区域", "SCARA, top view: reachable area"), fontsize=10)
ax1.set_xlabel("x (m)")
ax1.set_ylabel("y (m)")
ax1.text(-0.62, -0.68, T("虚线：半径 a₁ + a₂ = 0.6 m；缺口来自关节 1 的限位 ±140°",
                         "dashed: radius a₁ + a₂ = 0.6 m; the gap comes from the ±140° limit of joint 1"), fontsize=7.6,
         color=C["muted"])
ax1.set_xlim(-0.68, 0.68)
ax1.set_ylim(-0.72, 0.66)
ax2.plot(rh, pts[:, 2], ".", ms=0.8, color=C["accent"], alpha=0.35)
sh_z = fk_point(ur, {}, "upper_arm_link")[2]                  # 肩关节轴的高度
ax2.plot(0.85 * np.cos(th), sh_z + 0.85 * np.sin(th), "--", color=C["muted"], lw=0.8)
ax2.text(-1.02, -0.95, T("虚线：以肩部为中心、半径 0.85 m（厂家工作半径）",
                         "dashed: radius 0.85 m about the shoulder (datasheet reach)"), fontsize=7.6, color=C["muted"])
ax2.plot([0], [sh_z], "o", color=C["ink"], ms=4)
ax2.text(0.05, 0.19, T("肩部", "shoulder"), fontsize=8.5)
ax2.plot([-0.25, 0.25], [0, 0], color=C["ink"], lw=3)
ax2.set_aspect("equal")
ax2.set_title(T("UR5e 侧视：法兰中心的随机样本（未计碰撞）", "UR5e, side view: flange-centre samples (collisions ignored)"), fontsize=10)
ax2.set_xlabel(T("离基座轴线的水平距离（m，带方向）", "signed horizontal distance from the base axis (m)"))
ax2.set_ylabel("z (m)")
ax2.set_ylim(-1.0, 1.15)
for ax in (ax1, ax2):
    ax.grid(alpha=0.25)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig1_3_2")
plt.close(fig)
