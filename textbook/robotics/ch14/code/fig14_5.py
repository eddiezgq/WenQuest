"""14.5 节的示意图。

图 14.5.1：UR5e 到达算例 14.5.1 的目标位姿的 8 组解（编号、标签与表 14.5.1 相同）。8 种形态的法兰盘都在同一处、朝向相同。
图 14.5.2：求 θ1 的几何（俯视）：关节 2、3、4 所在的平面离基座轴线恒为 d4，所以这个平面与半径 d4 的圆相切；
           腕点 p_w 要落在这个平面内，过 p_w 作圆的两条切线，得到 θ1 的两个解。
"""
import math

import numpy as np

from _fig14 import BLUE2, C, axes3d, draw_chain, equal3d, label3d, plane, ur_chain
from _ik import D4, W4, ur_fk, ur_ik, ur_ordered
from bookout import T, figure, style

plt = style()
ths = np.radians([30, -60, 90, -120, -90, 45])
Td = ur_fk(ths)
sols = ur_ik(Td)
ordered = ur_ordered(sols)                         # 与表 14.5.1 相同的次序和标签

# ---------------------------------------------------------------- 图 14.5.1
fig = plt.figure(figsize=(10.4, 5.6))
pts_all = np.vstack([ur_chain(s) for s, _ in ordered])
for k, (s, lab) in enumerate(ordered):
    _, ax = axes3d(plt, fig=fig, pos=241 + k, elev=16, azim=-50)
    P = ur_chain(s)
    draw_chain(ax, P, C["z"] if lab[0] == "A" else C["accent"], lw=4, js=10)
    ax.plot([0, 0], [0, 0], [-0.05, 0.0], color=C["muted"], lw=6)
    xs = np.array([-0.45, 0.45])
    X, Y = np.meshgrid(xs, xs)
    ax.plot_surface(X, Y, np.zeros_like(X), color="#eef1f3", alpha=0.5, linewidth=0, shade=False)
    f = Td[:3, 3]
    n = Td[:3, 1]
    ax.quiver(*f, *(0.12 * n), color=C["x"], lw=1.4, arrow_length_ratio=0.3)
    up = lab[1] == "up"
    txt = f"{k + 1}  {T('肩', 'sh.')} {lab[0]} · {T('肘', 'elb.')} {T('上', 'up') if up else T('下', 'down')} · {T('腕', 'wr.')} {T('不翻', 'no flip') if lab[2] else T('翻', 'flip')}"
    ax.set_title(txt, fontsize=9, pad=-4)
    equal3d(ax, pts_all, pad=0.02, zoom=1.35)
figure(fig, "fig14_5_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 14.5.2
fig, ax = plt.subplots(figsize=(6.2, 5.0))
plane(ax, (-0.95, 0.4), (-0.8, 0.35))
pw = Td[:3, 3] - W4 * Td[:3, 1]
t = np.linspace(0, 2 * math.pi, 200)
ax.fill(D4 * np.cos(t), D4 * np.sin(t), color="#eef4fb", zorder=0)
ax.plot(D4 * np.cos(t), D4 * np.sin(t), color=BLUE2, lw=1.4)
ax.plot(0, 0, "+", color=C["ink"], ms=10)
ax.annotate("", xy=(0.3, 0), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=C["x"], lw=1.2))
ax.annotate("", xy=(0, 0.3), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=C["y"], lw=1.2))
ax.text(0.31, -0.03, "x", color=C["x"], fontsize=11)
ax.text(0.015, 0.3, "y", color=C["y"], fontsize=11)
ax.plot(pw[0], pw[1], "o", color=C["x"], ms=7, zorder=8)
ax.text(pw[0] - 0.16, pw[1] + 0.01, r"$p_w$", fontsize=12, color=C["x"])
for sg, col, name in ((1, C["z"], "A"), (-1, C["accent"], "B")):
    t1 = [s[0] for s, l in sols if l[0] == sg][0]
    # 关节 2 的轴方向（俯视）ω2(θ1) = Rot(z, θ1)(0, −1, 0)；平面内的点满足 ω2ᵀ p = d4
    w2 = np.array([math.sin(t1), -math.cos(t1)])
    foot = D4 * w2                                       # 切点
    d = np.array([-w2[1], w2[0]])                        # 平面的水平方向
    a, b = foot - 0.95 * d, foot + 0.95 * d
    ax.plot([a[0], b[0]], [a[1], b[1]], color=col, lw=2.0)
    ax.plot([0, foot[0]], [0, foot[1]], color=col, lw=1.0, ls="--")
    ax.plot(*foot, "o", color=col, ms=4)
    xl = -0.88 if sg > 0 else -0.25
    tip = foot + (xl - foot[0]) / d[0] * d
    ax.text(*(tip + np.array([0.0 if sg > 0 else 0.03, 0.04 if sg > 0 else 0.0])), T(f"解 {name}", f"solution {name}"), fontsize=10, color=col)
    ax.annotate("", xy=foot + 0.12 * w2, xytext=foot, arrowprops=dict(arrowstyle="-|>", color=col, lw=1.0))
ax.text(0.03, -0.17, r"$d_4$", fontsize=11, color=BLUE2)
ax.text(-0.93, 0.28, T("俯视：手臂平面与半径 $d_4$ 的圆相切，并经过 $p_w$", "top view: the arm plane touches the circle of radius $d_4$ and passes through $p_w$"), fontsize=9.5, color=C["ink"])
figure(fig, "fig14_5_2")
plt.close(fig)
