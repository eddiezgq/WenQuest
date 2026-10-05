"""17.2 节的示意图。

图 17.2.1：Panda 的手固定在 ready 姿态时的自运动（算例 17.2.1）。(a) 沿限位以内的弧取的几个形态与肘点走过的整条闭曲线；
           (b) 七个关节角在各自限位区间中的位置随弧长 s 的变化（0 为下限，1 为上限），以及可操作度 w。
图 17.2.2：平面 3R 臂的末端沿圆周运动，关节速度取伪逆解（算例 17.2.2）。(a) 开始时与转 10 圈以后的形态；
           (b) 每圈结束时三个关节角相对起点的变化：只用伪逆时越积越多，加上零空间项以后很快收敛到不变。
数据与 ex17_2.py 相同（重算一遍）。
"""
import math

import numpy as np

from _fig17 import C, GOLD2, arm_pts, axes3d, base_mark, draw_arm, draw_chain, equal3d, floor3d, plane, rerun, spines
from _red import PA_HI, PA_LO, PL, manip, pa_fk, pa_js, pa_points
from bookout import T, figure, style

plt = style()
E = rerun("ex17_2.py")
P, Pi, arc, n_pts, h = E["P"], E["Pi"], E["arc"], E["n_pts"], E["h"]

# ---------------------------------------------------------------- 图 17.2.1
fig = plt.figure(figsize=(12.4, 5.0))
ax = axes3d(plt, fig, pos=121, elev=16, azim=-28)
floor3d(ax, (-0.45, 0.55), (-0.5, 0.5))
cmap = plt.get_cmap("viridis")
pick = [arc[int(round(x))] for x in np.linspace(0, len(arc) - 1, 5)]
allp = []
ax.plot([0, 0], [0, 0], [0, 0.333], color="#9aa6ad", lw=7, solid_capstyle="butt")
for j, k in enumerate(pick):
    Pk = pa_points(P[k])[1:]
    draw_chain(ax, Pk, cmap(0.1 + 0.8 * j / 4), lw=3.0, alpha=0.85, js=8)
    allp.append(Pk)
Pr = pa_points(P[0])[1:]
draw_chain(ax, Pr, C["x"], lw=5, js=14)
EL = np.array([pa_points(q)[3] for q in P])
ax.plot(*EL.T, color=C["muted"], lw=1.0, ls="--")
ELa = np.array([pa_points(P[k])[3] for k in arc])
ax.plot(*ELa.T, color=C["accent"], lw=2.2)
Tb = pa_fk(P[0])
o = Tb[:3, 3]
for k, col in ((0, C["x"]), (1, C["y"]), (2, C["z"])):
    ax.quiver(*o, *(0.1 * Tb[:3, k]), color=col, lw=1.6, arrow_length_ratio=0.25)
ax.text(*(Pr[2] + np.array([0.0, -0.16, 0.10])), "ready", color=C["x"], fontsize=10, weight="bold")
equal3d(ax, np.vstack(allp + [EL, np.array([[-0.3, -0.35, 0], [0.45, 0.35, 0]])]), pad=0.0, zoom=1.25)
ax.text2D(0.02, 0.06, T("红：ready；彩色：限位以内的其他形态\n金色实线：肘点在限位以内走过的弧；虚线：超出限位的部分\n手（{b}，坐标轴）始终不动",
                         "red: ready; colours: other configurations within the limits\ngold: the elbow's arc within the limits; dashed: beyond the limits\nthe hand ({b}, axes) never moves"),
          transform=ax.transAxes, fontsize=8.5, color=C["muted"])
ax.set_title(T("(a) 手不动，肘部绕肩腕连线摆动", "(a) Hand still, elbow swinging about the shoulder–wrist line"), fontsize=10.5, loc="left")

ax = fig.add_subplot(122)
s = np.arange(n_pts) * h
s = np.where(s > s[-1] / 2, s - s[-1] - h, s)                     # 以 ready 为原点，两侧各半圈
order = np.argsort(s)
cols = [C["x"], C["y"], C["z"], C["accent"], "#8c564b", "#7f7f7f", "#9467bd"]
ax.axhspan(0, 1, color="#eef4fb", zorder=0)
Pc = P.copy()
Pc[s < 0] -= 2 * math.pi * np.array(E["net"])                     # 后半圈减去一圈的净转数，使曲线在 ready 两侧连续
Pc = Pc - 2 * math.pi * np.round((Pc[0] - Pi[0]) / (2 * math.pi))
for j in range(7):
    y = (Pc[:, j] - PA_LO[j]) / (PA_HI[j] - PA_LO[j])
    ax.plot(s[order], y[order], color=cols[j], lw=1.6, label="θ" + "₁₂₃₄₅₆₇"[j])
ax.axvline(0, color=C["ink"], lw=0.8)
s_arc = s[arc]
for v in (s_arc.min(), s_arc.max()):
    ax.axvline(v, color=C["muted"], lw=0.9, ls="--")
ax.text(0.08, 1.6, "ready", fontsize=9)
ax.text(s_arc.max() + 0.08, 1.6, T("关节 2 到下限", "joint 2 at its lower limit"), fontsize=8.5, color=C["muted"])
ax.text(s_arc.min() - 0.08, 1.6, T("关节 2 到下限", "joint 2 at its lower limit"), fontsize=8.5, color=C["muted"], ha="right")
ax.set_ylim(-0.7, 1.75)
ax.set_xlabel(T("沿自运动的弧长 s / rad", "arc length along the self-motion s / rad"))
ax.set_ylabel(T("(θ − 下限) / (上限 − 下限)", "(θ − lower) / (upper − lower)"))
spines(ax)
ax.legend(fontsize=8, ncol=4, frameon=False, loc="lower left")
ax2 = ax.twinx()
w = np.array([manip(pa_js(q)) for q in P])
ax2.plot(s[order], w[order], color=C["ink"], lw=1.4, ls=":")
ax2.set_ylabel(T("可操作度 w（点线）", "manipulability w (dotted)"))
ax2.set_ylim(0, 0.13)
ax.set_title(T("(b) 关节角在限位区间中的位置；阴影带内为允许", "(b) Joint angles within their limits; inside the band is allowed"), fontsize=10.5, loc="left")
fig.tight_layout()
figure(fig, "fig17_2_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 17.2.2
fig, axs = plt.subplots(1, 2, figsize=(11.6, 4.3), gridspec_kw={"width_ratios": [1, 1.15]})
ax = axs[0]
plane(ax, (-0.1, 0.85), (-0.42, 0.52))
base_mark(ax)
t = np.linspace(0, 2 * math.pi, 200)
CC, RR = E["CC"], E["RR"]
ax.plot(CC[0] + RR * np.cos(t), CC[1] + RR * np.sin(t), color=C["muted"], lw=1.0, ls="--")
draw_arm(ax, arm_pts(E["th0"], PL), C["z"], lw=5, alpha=0.95)
draw_arm(ax, arm_pts(E["ends"][10], PL), GOLD2, lw=5, alpha=0.9)
ax.annotate("", xy=CC + RR * np.array([math.cos(1.2), math.sin(1.2)]), xytext=CC + RR * np.array([math.cos(0.8), math.sin(0.8)]),
            arrowprops=dict(arrowstyle="-|>", color=C["muted"], lw=1.2))
ax.text(-0.08, 0.47, T("(a) 末端沿圆周走 10 圈，回到同一点", "(a) The tip goes round the circle 10 times, back to the same point"), fontsize=10)
ax.text(-0.08, 0.41, T("蓝：开始时；金：10 圈以后（只用伪逆）", "blue: at the start; gold: after 10 rounds (pseudoinverse only)"), fontsize=8.8, color=C["muted"])
ax = axs[1]
k = np.arange(11)
d = np.degrees(E["ends"] - E["th0"])
dk = np.degrees(E["ends_k"] - E["th0"])
for j, col in enumerate((C["x"], C["y"], C["z"])):
    ax.plot(k, d[:, j], "o-", color=col, ms=3.5, lw=1.5, label=T(f"θ{'₁₂₃'[j]}：只用伪逆", f"θ{'₁₂₃'[j]}: pseudoinverse only"))
    ax.plot(k, dk[:, j], "s--", color=col, ms=3, lw=1.2, alpha=0.7, label=T(f"θ{'₁₂₃'[j]}：加零空间项", f"θ{'₁₂₃'[j]}: with null-space term"))
ax.axhline(0, color=C["muted"], lw=0.8)
ax.set_xlabel(T("圈数", "rounds"))
ax.set_ylabel(T("每圈结束时 θ 相对起点的变化 / (°)", "change of θ at the end of each round / (°)"))
spines(ax)
ax.legend(fontsize=8, ncol=2, frameon=False, loc="upper left")
ax.set_title(T("(b) 关节角一圈一圈地漂移", "(b) The joint angles drift round after round"), fontsize=10.5, loc="left")
fig.tight_layout()
figure(fig, "fig17_2_2")
plt.close(fig)
