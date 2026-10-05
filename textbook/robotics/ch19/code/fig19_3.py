"""19.3 节的示意图。

图 19.3.1：瑞典轮接地点的速度分解：主轮转动贡献 rθ̇ e，接地辊子自由滚动贡献沿 s 的任意速度；两者之和在辊子轴线 a 上的投影
           等于 rθ̇ cos γ。(a) 麦克纳姆轮 γ = −45°；(b) 全向轮 γ = 0。
图 19.3.2：四轮麦克纳姆 AGV 的四种运动：前进、向左侧移、斜行、原地逆时针转。箭头为各轮的转速（向前为正），蓝色为车体的运动。
图 19.3.3：(a)(b) 车轮推力的作用线（沿辊子轴线）：正确安装时离车体中心远，左右装反时几乎都过中心；
           (c) 轮速限制下水平速度的可行范围（ω = 0）：麦克纳姆底盘是一个正方形，差速底盘只是一条线段。
"""
import math

import numpy as np

from _fig19 import C, arrow, rect, wheel
from _mob import swedish_row
from bookout import T, figure, style

plt = style()
O = (0.0, 0.0, 0.0)

# ---------------------------------------------------------------- 图 19.3.1
fig, axs = plt.subplots(1, 2, figsize=(10.0, 4.4))
for ax, gm, ttl in ((axs[0], -math.pi / 4, T("(a) 麦克纳姆轮，γ = −45°", "(a) mecanum wheel, γ = −45°")),
                    (axs[1], 0.0, T("(b) 全向轮，γ = 0", "(b) omni wheel, γ = 0"))):
    ax.set_aspect("equal")
    ax.axis("off")
    wheel(ax, O, 0, 0, 0.0, r=0.32, width=0.16, rollers=7, gamma=gm, fc="#7b868c")
    e = np.array([1.0, 0.0])
    a = np.array([math.cos(gm), math.sin(gm)])
    s = np.array([-a[1], a[0]])
    rth = 0.55
    u = 0.42 if gm else 0.35
    vP = rth * e + u * s
    arrow(ax, (0, 0), rth * e, C["green"], 2.0)
    ax.text(rth + 0.02 if gm else 0.12, -0.07 if gm else -0.14, r"$r\dot\theta\,e$", color=C["green"], fontsize=13)
    arrow(ax, rth * e, vP, C["blue"], 1.6, ls="--")
    ax.text(*(rth * e + 0.55 * u * s + np.array([0.04, 0.0])), T("辊子自由滚动 $u\\,s$", "roller rolls freely $u\\,s$"), color=C["blue"], fontsize=10)
    arrow(ax, (0, 0), vP, C["ink"], 2.2)
    ax.text(*(vP + np.array([0.03, 0.02])), "$v_P$", fontsize=13)
    ax.plot(*np.array([-0.75 * a, 0.95 * a]).T, color=C["purple"], lw=1.0, ls="--")
    ax.text(*(0.95 * a + np.array([0.02, -0.08 if gm else 0.03])), T("辊子轴线 $a$", "roller axis $a$"), color=C["purple"], fontsize=10)
    proj = (vP @ a) * a
    ax.plot([vP[0], proj[0]], [vP[1], proj[1]], color=C["muted"], lw=0.8, ls=":")
    ax.plot(*proj, "o", color=C["purple"], ms=4)
    if gm:                                                       # 标注放在轴线左下方，不与虚线相交
        ax.text(proj[0] - 0.06, proj[1] - 0.06, r"$a\cdot v_P = r\dot\theta\cos\gamma$", color=C["purple"], fontsize=11, ha="right", va="top")
    else:
        ax.text(*(proj + np.array([0.02, -0.3])), r"$a\cdot v_P = r\dot\theta\cos\gamma$", color=C["purple"], fontsize=11)
    ax.set_xlim(-0.8, 1.15)
    ax.set_ylim(-0.85, 0.75)
    ax.set_title(ttl, fontsize=10.5)
figure(fig, "fig19_3_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 19.3.2
r, l, w = 0.075, 0.25, 0.20
g = math.pi / 4
wh = [("FL", l, w, -g), ("FR", l, -w, g), ("RL", -l, w, g), ("RR", -l, -w, -g)]
H = np.array([swedish_row(x, y, 0.0, gm, r) for _, x, y, gm in wh])
cases = [(np.array([0.0, 0.5, 0.0]), T("(a) 前进", "(a) forward") + r" $v_x$ = 0.5 m/s"),
         (np.array([0.0, 0.0, 0.3]), T("(b) 向左侧移", "(b) sideways left") + r" $v_y$ = 0.3 m/s"),
         (np.array([0.0, 0.3, 0.3]), T("(c) 斜行", "(c) diagonal") + r" $v_x = v_y$ = 0.3 m/s"),
         (np.array([1.0, 0.0, 0.0]), T("(d) 原地逆时针转", "(d) spin anticlockwise") + r" $\omega$ = 1 rad/s")]
fig, axs = plt.subplots(1, 4, figsize=(12.0, 4.0))
for ax, (V, ttl) in zip(axs, cases):
    ax.set_aspect("equal")
    ax.axis("off")
    rect(ax, O, 0, 0, 0, 2 * l + 0.12, 2 * w + 0.02, C["body"], C["dark"], 0.8, 1)
    th = H @ V
    for (nm, x, y, gm), t in zip(wh, th):
        wheel(ax, O, x, y + (0.03 if y > 0 else -0.03), 0.0, r=r, width=0.05, rollers=4, gamma=gm, fc="#7b868c")
        yy = y + (0.1 if y > 0 else -0.1)
        if abs(t) > 1e-9:
            arrow(ax, (x, yy), (x + 0.018 * t, yy), C["red"], 1.8, 9)
        ax.text(x - 0.06, yy + (0.05 if y > 0 else -0.08), f"{t:.1f}".replace("-", "−"), color=C["red"], fontsize=9)
    if abs(V[0]) > 0:
        tt = np.linspace(-0.3, 1.9, 40)
        ax.plot(0.12 * np.cos(tt), 0.12 * np.sin(tt), color=C["blue"], lw=2.0)
        arrow(ax, (0.12 * math.cos(1.8), 0.12 * math.sin(1.8)), (0.12 * math.cos(1.95), 0.12 * math.sin(1.95)), C["blue"], 2.0, 12)
    else:
        arrow(ax, (0, 0), (0.42 * V[1], 0.42 * V[2]), C["blue"], 2.6, 14)
    ax.set_xlim(-0.42, 0.42)
    ax.set_ylim(-0.42, 0.42)
    ax.set_title(ttl, fontsize=9.5)
fig.text(0.1, 0.03, T("红色数字与箭头：车轮转速", "red: wheel speeds") + r" $\dot\theta$ / (rad/s)" + T("，向前为正；蓝色：车体的运动；车轮上的白线：接地辊子的轴线方向",
                      ", forward positive; blue: the body's motion; white strokes: axes of the rollers touching the floor"),
         fontsize=9)
figure(fig, "fig19_3_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 19.3.3
fig, axs = plt.subplots(1, 3, figsize=(12.6, 4.3))
for ax, sgn, ttl in ((axs[0], 1, T("(a) 正确安装：作用线离中心 (l + w)/√2", "(a) correct: lines (l + w)/√2 from the centre")),
                     (axs[1], -1, T("(b) 左右装反：作用线离中心 (l − w)/√2", "(b) swapped: lines (l − w)/√2 from the centre"))):
    ax.set_aspect("equal")
    ax.axis("off")
    rect(ax, O, 0, 0, 0, 2 * l + 0.12, 2 * w + 0.02, C["body"], C["dark"], 0.8, 1)
    for nm, x, y, gm in wh:
        gm2 = sgn * gm
        wheel(ax, O, x, y + (0.03 if y > 0 else -0.03), 0.0, r=r, width=0.05, rollers=4, gamma=gm2, fc="#7b868c")
        a = np.array([math.cos(gm2), math.sin(gm2)])
        p = np.array([x, y])
        ax.plot(*np.array([p - 0.6 * a, p + 0.6 * a]).T, color=C["purple"], lw=1.0, ls="--")
    ax.plot(0, 0, "+", color=C["ink"], ms=10)
    c = (l + w) / math.sqrt(2) if sgn > 0 else (l - w) / math.sqrt(2)
    circ = np.linspace(0, 2 * math.pi, 100)
    ax.plot(c * np.cos(circ), c * np.sin(circ), color=C["accent"], lw=1.2)
    ax.set_xlim(-0.5, 0.5)
    ax.set_ylim(-0.56, 0.48)
    ax.set_title(ttl, fontsize=9.5)
axs[0].text(-0.5, -0.53, T("紫虚线：各轮推力的作用线（沿辊子轴线）；橙圆：它们离中心的距离",
                            "purple: lines of the wheel forces (along roller axes); orange: their distance from the centre"), fontsize=8.5)
ax = axs[2]
ax.set_aspect("equal")
sq = np.array([[1.5, 0], [0, 1.5], [-1.5, 0], [0, -1.5], [1.5, 0]])
ax.fill(sq[:, 0], sq[:, 1], color=C["blue"], alpha=0.12)
ax.plot(sq[:, 0], sq[:, 1], color=C["blue"], lw=1.4, label=T("麦克纳姆", "mecanum") + r" ($r\,\omega_{\max}$ = 1.5 m/s)")
ax.plot([-1.0, 1.0], [0, 0], color=C["red"], lw=3, label=T("差速 AGV（1.0 m/s）", "differential AGV (1.0 m/s)"))
ax.plot([0, 0.75], [0, 0.75], color=C["muted"], lw=0.8, ls=":")
ax.plot(0.75, 0.75, "o", color=C["blue"], ms=4)
ax.text(0.8, 0.8, T("斜行 1.06 m/s", "diagonal 1.06 m/s"), fontsize=9)
ax.axhline(0, color=C["muted"], lw=0.5)
ax.axvline(0, color=C["muted"], lw=0.5)
ax.set_xlabel(r"$v_x$ / (m/s)")
ax.set_ylabel(r"$v_y$ / (m/s)")
ax.set_xlim(-1.8, 1.8)
ax.set_ylim(-1.8, 1.8)
ax.legend(fontsize=8, loc="lower left", frameon=False)
ax.set_title(T("(c) ω = 0 时水平速度的可行范围", "(c) feasible velocities with ω = 0"), fontsize=9.5)
fig.subplots_adjust(wspace=0.15)
figure(fig, "fig19_3_3")
plt.close(fig)
