"""30.2 节的示意图。

图 30.2.1：(a) 工具竖直朝下时，偏置腕（WQ-CR5）与球形腕（肩高、大臂相同，小臂加长 d5 使臂展相同）在手臂平面里能到达的区域；
          (b) 四种构型的评分（算例 30.2.3：每一段是“权重 × 打分”，总长是加权总分）。
"""
import math

import numpy as np

from _ch30 import cr_dh
from bookout import COLORS as C, T, figure, style

plt = style()
dh = cr_dh()
a2, a3 = abs(dh[1]["a"]), abs(dh[2]["a"])
d1, d4, d5, d6 = dh[0]["d"], dh[3]["d"], dh[4]["d"], dh[5]["d"]
TOOL = 0.15


def off(r, z):
    if r < d4:
        return False
    rp = math.sqrt(r * r - d4 * d4)
    h = z + TOOL + d6 - d1
    return any(abs(a2 - a3) <= math.hypot(x, h) <= a2 + a3 for x in (rp - d5, rp + d5))


def sph(r, z):
    h = z + TOOL + d6 - d1
    return abs(a2 - a3 - d5) <= math.hypot(r, h) <= a2 + a3 + d5


fig, axs = plt.subplots(1, 2, figsize=(11.8, 4.4), gridspec_kw={"width_ratios": [1, 1.3]})
ax = axs[0]
rs = np.linspace(0, 1.0, 251)
zs = np.linspace(-0.8, 1.0, 361)
A = np.array([[off(r, z) for r in rs] for z in zs], float)
B = np.array([[sph(r, z) for r in rs] for z in zs], float)
ax.contourf(rs, zs, B, levels=[0.5, 1.5], colors=[C["muted"]], alpha=0.18)
ax.contour(rs, zs, B, levels=[0.5], colors=[C["muted"]], linewidths=1, linestyles="--")
ax.contourf(rs, zs, A, levels=[0.5, 1.5], colors=[C["z"]], alpha=0.22)
ax.contour(rs, zs, A, levels=[0.5], colors=[C["z"]], linewidths=1.2)
ax.plot([], [], color=C["z"], lw=1.2, label=T("偏置腕（WQ-CR5）", "offset wrist (WQ-CR5)"))
ax.plot([], [], color=C["muted"], lw=1, ls="--", label=T("球形腕（臂展相同）", "spherical wrist (same reach)"))
ax.axhline(0, color=C["ink"], lw=0.6)
ax.annotate(T("半径 d4 = 0.12 m 的圆柱\n工具朝下时够不着", "a cylinder of radius d4 = 0.12 m\nis out of reach with the tool down"),
            xy=(0.06, 0.2), xytext=(0.2, 0.75), fontsize=8, arrowprops=dict(arrowstyle="->", color=C["accent"]), color=C["accent"])
ax.set_aspect("equal")
ax.set_xlim(0, 1.0)
ax.set_ylim(-0.8, 1.0)
ax.set_xlabel(T("离 J1 轴的距离 r / m", "distance from J1's axis r / m"))
ax.set_ylabel(T("TCP 高度 z / m", "TCP height z / m"))
ax.legend(fontsize=8, frameon=False, loc="lower left")
ax.set_title(T("(a) 工具朝下时的工作空间（手臂平面）", "(a) tool-down workspace in the arm plane"), fontsize=11)

ax = axs[1]
crit = [T("与人同场", "working beside people"), T("模组化", "modularity"), T("工作空间", "workspace"), T("逆解与编程", "inverse kinematics, programming"),
        T("成本", "cost"), T("刚度与精度", "stiffness, accuracy")]
w = np.array([0.25, 0.20, 0.20, 0.15, 0.10, 0.10])
names = [T("偏置腕六轴", "6-axis, offset wrist"), T("球形腕六轴", "6-axis, spherical wrist"), T("七轴", "7-axis"), "SCARA"]
S = np.array([[5, 5, 4, 4, 4, 3], [3, 2, 5, 5, 4, 4], [5, 4, 4, 2, 2, 3], [2, 3, 1, 5, 5, 5]], float)
cols = ["#1f77b4", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#b8860b"]
left = np.zeros(4)
for k in range(6):
    seg = w[k] * S[:, k]
    ax.barh(range(4), seg, left=left, color=cols[k], alpha=0.8, label=f"{crit[k]}（{w[k]:.2f}）" if T("中", "") else f"{crit[k]} ({w[k]:.2f})")
    left += seg
for i, v in enumerate(left):
    ax.text(v + 0.05, i, f"{v:.2f}", va="center", fontsize=9)
ax.set_yticks(range(4), names)
ax.invert_yaxis()
ax.set_xlim(0, 5.4)
ax.set_xlabel(T("加权总分（满分 5）", "weighted score (out of 5)"))
ax.legend(fontsize=7.5, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=3)
ax.set_title(T("(b) 四种构型的评分", "(b) scoring the four configurations"), fontsize=11)
fig.tight_layout()
figure(fig, "fig30_2_1")
