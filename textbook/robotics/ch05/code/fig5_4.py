"""5.4 节的示意图。

图 5.4.1：UR5e 工作站的坐标系树。根为工作台 {w}；边上注明这条变换从哪里来（安装与标定、关节编码器、视觉测量）。
         高亮从相机 {c} 到工具 {t} 的唯一路径：向上走一步（乘逆），向下走十步。
图 5.4.2：UR5e 在关节角 θ_A = (0°, −90°, 90°, −90°, −90°, 0°) 时各连杆坐标系的位置与方向（模型关节表逐边相乘）。
"""
import numpy as np
from matplotlib.patches import FancyBboxPatch

from _fig5 import AX, C, axes3d, box3d, frame3
from _frames import DEG, T, T_bt, ur_edges_from_table
from bookout import T as TT, figure, style

plt = style()

# ---------------------------------------------------------------- 图 5.4.1
fig, ax = plt.subplots(figsize=(7.6, 8.4))
ax.axis("off")
ax.set_xlim(-0.2, 10.2)
ax.set_ylim(-0.6, 10.0)
dy = 0.9
nodes = {"w": (5.0, 9.4, TT("{w} 工作台", "{w} worktable")),
         "s": (2.6, 8.3, TT("{s} 机器人基座", "{s} robot base")),
         "c": (7.4, 8.3, TT("{c} 相机", "{c} camera")),
         "o": (7.4, 6.9, TT("{o} 齿轮坯", "{o} gear blank")),
         "g": (7.4, 5.5, TT("{g} 抓取点", "{g} grasp")),
         "base": (2.6, 8.3 - dy, TT("基座连杆", "base link"))}
chain = ["base"] + [f"L{i}" for i in range(1, 7)] + ["b", "t"]
for k, n in enumerate(chain[1:], 1):
    lab = TT(f"连杆 {k}", f"link {k}") if n.startswith("L") else (TT("{b} 法兰", "{b} flange") if n == "b" else TT("{t} 工具", "{t} tool"))
    nodes[n] = (2.6, 8.3 - (k + 1) * dy, lab)
path = {("c", "w"), ("w", "s"), ("s", "base")} | {(chain[i], chain[i + 1]) for i in range(len(chain) - 1)}
on_path = {"c", "w", "s", "t", "b", "base"} | {f"L{i}" for i in range(1, 7)}


def box(n):
    x, y, lab = nodes[n]
    hl = n in on_path
    ax.add_patch(FancyBboxPatch((x - 1.05, y - 0.25), 2.1, 0.5, boxstyle="round,pad=0.03",
                                facecolor="#fdf3d8" if hl else "#eef1f3", edgecolor=C["accent"] if hl else "#9aa6ad", lw=1.2))
    ax.text(x, y, lab, ha="center", va="center", fontsize=9.5)


def edge(p, c, label, color="#5b6b75", ls="-"):
    x0, y0, _ = nodes[p]
    x1, y1, _ = nodes[c]
    ax.annotate("", xy=(x1, y1 + 0.27), xytext=(x0, y0 - 0.27),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.2, linestyle=ls, mutation_scale=10))
    if label:
        side = 1.15 if abs(x0 - x1) < 1e-9 else 0.15
        ax.text((x0 + x1) / 2 + side, (y0 + y1) / 2 + (0 if abs(x0 - x1) < 1e-9 else 0.18), label, fontsize=8.5,
                color=color, va="center", ha="left" if abs(x0 - x1) < 1e-9 or x1 > x0 else "right")


for n in nodes:
    box(n)
edge("w", "s", TT("安装：$T_{ws}$", "mounting: $T_{ws}$"))
edge("w", "c", TT("标定：$T_{wc}$", "calibration: $T_{wc}$"))
edge("c", "o", TT("视觉测量：$T_{co}$", "vision: $T_{co}$"), ls="--")
edge("o", "g", TT("抓取设计：$T_{og}$", "grasp design: $T_{og}$"))
edge("s", "base", TT("固定：绕 z 转 180°", "fixed: 180° about z"))
for i in range(1, len(chain)):
    p, c = chain[i - 1], chain[i]
    lab = (TT(f"关节 {i}：$\\theta_{i}$", f"joint {i}: $\\theta_{i}$") if c.startswith("L")
           else (TT("固定：法兰偏置", "fixed: flange offset") if c == "b" else TT("工具设置：$T_{bt}$", "tool data: $T_{bt}$")))
    edge(p, c, lab)
# 路径：c → w（向上，乘逆），w → … → t（向下）
ax.annotate("", xy=(6.15, 9.55), xytext=(8.6, 8.6),
            arrowprops=dict(arrowstyle="-|>", color="#d62728", lw=2.2, mutation_scale=14))
ax.text(7.5, 9.45, TT("向上：乘 $T_{wc}^{-1}$", "up: multiply by $T_{wc}^{-1}$"), fontsize=9.5, color="#d62728")
ax.annotate("", xy=(1.25, nodes["t"][1]), xytext=(1.25, 9.0),
            arrowprops=dict(arrowstyle="-|>", color="#d62728", lw=2.2, mutation_scale=14))
ax.text(1.05, 5.0, TT("向下：依次乘各条边的 $T$", "down: multiply the edges' $T$ in turn"), fontsize=9.5, color="#d62728",
        rotation=90, ha="right", va="center")
ax.text(5.9, 3.6, TT("从 {c} 到 {t} 的唯一路径（高亮）：", "The unique path from {c} to {t} (highlighted):"), fontsize=9.5)
ax.text(5.9, 3.1, r"$T_{ct}=T_{wc}^{-1}\,T_{ws}\,T_{s,\mathrm{base}}\cdots T_{bt}$", fontsize=11)
ax.text(5.9, 2.4, TT("实线：固定或由关节角决定", "solid: fixed or set by a joint angle"), fontsize=9, color=C["muted"])
ax.text(5.9, 2.0, TT("虚线：由测量得到，随时更新", "dashed: measured, updated as it changes"), fontsize=9, color=C["muted"])
figure(fig, "fig5_4_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 5.4.2
thA = np.array([0, -90, 90, -90, -90, 0]) * DEG
M = np.eye(4)
frames, pts = [], [M[:3, 3].copy()]
for child, parent, Tm in ur_edges_from_table(thA):
    M = M @ Tm
    frames.append((child, M.copy()))
    pts.append(M[:3, 3].copy())
tip = M @ T_bt()
fig, ax = axes3d(plt, size=(6.6, 5.4), elev=18, azim=-128)
P = np.array(pts)
ax.plot(*P.T, color="#9aa6ad", lw=6, solid_capstyle="round", alpha=0.8)
ax.plot(*np.c_[M[:3, 3], tip[:3, 3]], color="#5b6b75", lw=3)
frame3(ax, np.eye(4), 0.12, "{s}", off=(0.0, 0.06, -0.05))
names = {"shoulder_link": "1", "upper_arm_link": "2", "forearm_link": "3", "wrist_1_link": "4", "wrist_2_link": "5",
         "wrist_3_link": "6", "b": "{b}"}
offs = {"shoulder_link": (0.06, 0.0, -0.03), "upper_arm_link": (0.0, -0.07, 0.04), "forearm_link": (0.0, -0.07, 0.03),
        "wrist_1_link": (0.03, 0.04, 0.05), "wrist_2_link": (0.0, -0.08, 0.03), "wrist_3_link": (-0.06, 0.03, 0.04),
        "b": (0.05, -0.02, -0.06)}
for child, F in frames:
    if child in names:
        frame3(ax, F, 0.07, names[child], fs=10, off=offs[child], lw=1.3, color=C["accent"])
frame3(ax, tip, 0.06, "{t}", fs=10, off=(0.05, 0.0, -0.04), lw=1.3)
box3d(ax, (-0.6, -0.25, 0.0), (0.12, 0.12, 0.66), zoom=1.0)
ax.text2D(0.02, 0.02, TT("金色数字：连杆坐标系 1–6；每个坐标系由上一个乘一条边得到",
                         "Gold numbers: link frames 1–6; each is the previous one times one edge"), transform=ax.transAxes, fontsize=9)
figure(fig, "fig5_4_2")
plt.close(fig)
