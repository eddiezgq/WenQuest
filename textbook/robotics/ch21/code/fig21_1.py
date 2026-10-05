"""21.1 节的示意图。

图 21.1.1：(a) X2 的俯视几何：旋翼编号、转向、坐标系 {b}、尺寸 l_x、l_y；(b) 侧视：旋翼、质心、IMU 的高度。
图 21.1.2：四种基本的推力组合：总推力、横滚力矩、俯仰力矩、偏航力矩（蓝色桨盘推力增大，红色减小）。
图 21.1.3：总推力为 f、偏航力矩为零时，(m_x, m_y) 的可达范围；f = m𝔤、2m𝔤、3.5m𝔤 三种情形（3m𝔤 与 m𝔤 的范围相同）。
"""
import math

import numpy as np
from matplotlib.patches import Circle

from _fig21 import C, ROTOR_R, arrow, frame2, top_view
from _uav import G, alloc, x2
from bookout import T, figure, style

plt = style()
P = x2()
r, sig, m, c, fmax = P["r"], P["sig"], P["m"], P["c"], P["fmax"]
lx, ly = P["lx"], P["ly"]
A, _ = alloc(P)
Ainv = np.linalg.inv(A)
W = m * G

# ---------------------------------------------------------------- 图 21.1.1
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.4, 5.0), gridspec_kw={"width_ratios": [1.1, 1.0]})
a1.set_aspect("equal")
a1.axis("off")
top_view(a1, r, sig)
frame2(a1, (0, 0), 0.1, dx=(-0.03, -0.055))
a1.plot(0, 0, "o", ms=5, color=C["ink"], zorder=7)
a1.text(-0.035, -0.035, "C", fontsize=11, zorder=7)
# 尺寸
a1.annotate("", xy=(lx, -0.36), xytext=(0, -0.36), arrowprops=dict(arrowstyle="<->", color=C["ink"], lw=0.9))
a1.plot([lx, lx], [-0.18 - ROTOR_R + 0.02, -0.37], color=C["muted"], lw=0.5, ls=":")
a1.plot([0, 0], [-0.05, -0.37], color=C["muted"], lw=0.5, ls=":")
a1.text(lx / 2, -0.385, f"$l_x$ = {lx:.2f} m", fontsize=10.5, ha="center", va="top")
a1.annotate("", xy=(0.37, ly), xytext=(0.37, 0), arrowprops=dict(arrowstyle="<->", color=C["ink"], lw=0.9))
a1.plot([0.14 + ROTOR_R - 0.02, 0.38], [ly, ly], color=C["muted"], lw=0.5, ls=":")
a1.text(0.385, ly / 2, f"$l_y$ = {ly:.2f} m", fontsize=10.5, va="center")
a1.plot([0, -lx], [0, ly], color=C["accent"], lw=1.0, ls="--", zorder=6)
a1.text(-0.11, 0.055, "$l$", color=C["accent"], fontsize=13)
a1.text(0.205, 0.015, T("机头", "nose"), fontsize=9.5, color=C["accent"])
a1.text(-0.47, -0.33, T("紫色箭头：旋翼转向（从上往下看）\n1、3 逆时针，2、4 顺时针",
                        "purple arrows: rotor spin seen from above\n1, 3 counter-clockwise; 2, 4 clockwise"),
        fontsize=9, color=C["purple"], va="top")
a1.set_xlim(-0.48, 0.5)
a1.set_ylim(-0.45, 0.36)
a1.set_title(T("(a) 俯视：$x_b$ 指向机头，$z_b$ 指向读者", "(a) top view: $x_b$ to the nose, $z_b$ towards the reader"), fontsize=11)

# (b) 侧视（从右侧看，x_b 向右，z_b 向上），高度为 MJCF 机体坐标系中的值
a2.set_aspect("equal")
a2.axis("off")
zc = P["com"][2]
for (x, z, nm, sub) in ((-lx, 0.05, "1, 2", "1"), (lx, 0.08, "3, 4", "3")):
    a2.plot([0, x], [0.02, z], color=C["dark"], lw=3, solid_capstyle="round", zorder=2)
    a2.plot([x - ROTOR_R, x + ROTOR_R], [z + 0.012, z + 0.012], color=C["dark"], lw=2.4, zorder=3)
    a2.plot([x, x], [z, z + 0.012], color=C["dark"], lw=1.4)
    arrow(a2, (x, z + 0.02), (x, z + 0.11), C["blue"], 1.8, 10)
    a2.text(x + 0.012, z + 0.1, f"$f_{sub}$", color=C["blue"], fontsize=12)
    a2.text(x + np.sign(x) * 0.07, z + 0.03, T(f"旋翼 {nm}", f"rotors {nm}"), fontsize=9, ha="center", color=C["muted"])
e = __import__("matplotlib").patches.Ellipse((0, 0.02), 0.32, 0.04, fc=C["body"], ec=C["dark"], lw=0.9, zorder=3)
a2.add_patch(e)
a2.plot(0, zc, "o", ms=8, mfc="white", mec=C["red"], mew=2, zorder=6)
a2.plot(0, 0.02, "s", ms=5, color=C["green"], zorder=6)
a2.plot([0, 0], [zc + 0.008, 0.125], color=C["red"], lw=0.6)
a2.text(0, 0.13, T("质心 C", "CoM C"), color=C["red"], fontsize=10, ha="center")
a2.text(0, -0.008, "IMU", color=C["green"], fontsize=9.5, va="top", ha="center")
a2.plot([-0.3, 0.3], [0, 0], color=C["muted"], lw=0.5, ls=":")
a2.text(-0.3, -0.035, T("点线：MJCF 机体坐标系原点的高度", "dotted: height of the MJCF body origin"), fontsize=8.5,
        color=C["muted"], va="top")
a2.annotate("", xy=(0.28, zc), xytext=(0.28, 0), arrowprops=dict(arrowstyle="<->", color=C["red"], lw=0.8))
a2.plot([0.02, 0.29], [zc, zc], color=C["red"], lw=0.5, ls=":")
a2.text(0.288, zc / 2, f"{zc:.3f} m", fontsize=9.5, color=C["red"], va="center")
arrow(a2, (-0.3, 0.17), (-0.22, 0.17), C["x"], 1.3, 9)
arrow(a2, (-0.3, 0.17), (-0.3, 0.25), C["z"], 1.3, 9)
a2.text(-0.215, 0.162, "$x_b$", color=C["x"], fontsize=11)
a2.text(-0.32, 0.255, "$z_b$", color=C["z"], fontsize=11)
a2.set_xlim(-0.34, 0.37)
a2.set_ylim(-0.08, 0.28)
a2.set_title(T("(b) 侧视：推力都平行于 $z_b$", "(b) side view: all thrusts parallel to $z_b$"), fontsize=11)
fig.tight_layout()
figure(fig, "fig21_1_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 21.1.2
modes = [((W, 0, 0, 0), T("(a) 总推力 $f$：四个一起增减", "(a) collective thrust $f$: all four together"), None),
         ((W, 0.4, 0, 0), T("(b) 横滚力矩 $m_x > 0$：左增右减", "(b) roll moment $m_x > 0$: left up, right down"), "x"),
         ((W, 0, 0.4, 0), T("(c) 俯仰力矩 $m_y > 0$：后增前减", "(c) pitch moment $m_y > 0$: rear up, front down"), "y"),
         ((W, 0, 0, 0.05), T("(d) 偏航力矩 $m_z > 0$：2、4 增，1、3 减", "(d) yaw moment $m_z > 0$: 2, 4 up; 1, 3 down"), "z")]
fig, axs = plt.subplots(2, 2, figsize=(10.4, 8.0))
for ax, (w, title, ax_m) in zip(axs.flat, modes):
    ax.set_aspect("equal")
    ax.axis("off")
    if ax_m is None:
        f = np.full(4, W / 4)
        top_view(ax, r, sig, thrust=np.array([1.0, 1.0, 1.0, 1.0]) * 0 + f, spin_arrows=False)
        for i, ri in enumerate(r):
            ax.add_patch(Circle((ri[0], ri[1]), ROTOR_R, fc=C["up"], alpha=0.35, ec=C["dark"], lw=0.8, zorder=3))
        ax.text(0, -0.39, T("$f_i$ 同增：上升；同减：下降", "all $f_i$ up: climb; all down: descend"), ha="center", fontsize=9.5,
                color=C["muted"])
    else:
        f = Ainv @ np.array(w)
        top_view(ax, r, sig, thrust=f, spin_arrows=(ax_m == "z"))
        if ax_m == "x":
            arrow(ax, (0, 0), (0.2, 0), C["purple"], 2.4, 14)
            arrow(ax, (0.12, 0), (0.2, 0), C["purple"], 2.4, 14)
            ax.text(0.2, 0.03, "$m_x$", color=C["purple"], fontsize=13)
            ax.text(0, -0.39, T("左侧抬起，机身向右倾（φ 增大）", "left side lifts: body rolls right (φ grows)"), ha="center",
                    fontsize=9.5, color=C["muted"])
        elif ax_m == "y":
            arrow(ax, (0, 0), (0, 0.2), C["purple"], 2.4, 14)
            arrow(ax, (0, 0.12), (0, 0.2), C["purple"], 2.4, 14)
            ax.text(0.03, 0.17, "$m_y$", color=C["purple"], fontsize=13)
            ax.text(0, -0.39, T("机尾抬起，机头向下（θ 增大）", "tail lifts: nose goes down (θ grows)"), ha="center", fontsize=9.5,
                    color=C["muted"])
        else:
            t = np.linspace(math.radians(-60), math.radians(200), 60)
            ax.plot(0.065 * np.cos(t), 0.065 * np.sin(t), color=C["purple"], lw=2.2, zorder=7)
            arrow(ax, (0.065 * math.cos(t[-3]), 0.065 * math.sin(t[-3])), (0.065 * math.cos(t[-1]), 0.065 * math.sin(t[-1])),
                  C["purple"], 2.2, 14, z=8)
            ax.text(0.06, 0.07, "$m_z$", color=C["purple"], fontsize=13, zorder=7)
            ax.text(0, -0.39, T("顺时针旋翼的反扭矩占上风，机身逆时针转（ψ 增大）",
                               "reaction of the clockwise rotors wins: body yaws counter-clockwise (ψ grows)"),
                    ha="center", fontsize=9.5, color=C["muted"])
        for i, ri in enumerate(r):
            d = f[i] - W / 4
            ax.text(ri[0], ri[1] - 0.06 * np.sign(ri[1]) - 0.005, f"{d:+.2f} N".replace("-", "−"), fontsize=9,
                    ha="center", va="center", color=C["up"] if d > 0 else C["down"], zorder=8)
    ax.set_xlim(-0.36, 0.36)
    ax.set_ylim(-0.42, 0.34)
    ax.set_title(title, fontsize=10.5)
fig.text(0.5, 0.015, T(r"悬停推力 $f = m\mathfrak{g}$ 不变；桨盘旁的数字为各旋翼推力相对悬停值 $m\mathfrak{g}/4$ 的改变量（示意的力矩：0.4 N·m、0.4 N·m、0.05 N·m）",
                       r"Collective thrust kept at $m\mathfrak{g}$; numbers: change of each rotor thrust from $m\mathfrak{g}/4$ (illustrative moments: 0.4, 0.4, 0.05 N·m)"),
         ha="center", fontsize=9, color=C["muted"])
fig.tight_layout(rect=(0, 0.03, 1, 1))
figure(fig, "fig21_1_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 21.1.3
fig, ax = plt.subplots(figsize=(6.6, 5.4))
cols = [C["blue"], C["green"], C["orange"]]
for F, col, nm in ((W, cols[0], r"$f = m\mathfrak{g}$"), (2 * W, cols[1], r"$f = 2m\mathfrak{g}$"), (3.5 * W, cols[2], r"$f = 3.5m\mathfrak{g}$")):
    # 0 ≤ f_i ≤ f_max 的交集（m_z = 0）：在 (m_x, m_y) 平面上逐点检查，再取边界
    ang = np.linspace(0, 2 * math.pi, 721)
    pts = []
    for a in ang:
        u = np.array([math.cos(a), math.sin(a)])
        smax = np.inf
        for i in range(4):
            g = Ainv[i, 1] * u[0] + Ainv[i, 2] * u[1]
            base = F / 4
            if g > 1e-12:
                smax = min(smax, (fmax - base) / g)
            elif g < -1e-12:
                smax = min(smax, (0 - base) / g)
        pts.append(smax * u)
    pts = np.array(pts)
    ax.fill(pts[:, 0], pts[:, 1], color=col, alpha=0.10)
    ax.plot(pts[:, 0], pts[:, 1], color=col, lw=1.6, label=nm)
ax.axhline(0, color=C["muted"], lw=0.6)
ax.axvline(0, color=C["muted"], lw=0.6)
ax.set_xlabel(T("横滚力矩 $m_x$ / (N·m)", "roll moment $m_x$ / (N·m)"))
ax.set_ylabel(T("俯仰力矩 $m_y$ / (N·m)", "pitch moment $m_y$ / (N·m)"))
ax.set_aspect("equal")
ax.legend(loc="upper right", fontsize=10, frameon=False)
ax.text(-4.9, -4.3, T("偏航力矩 $m_z = 0$；每个旋翼 $0 \\leq f_i \\leq 13$ N", "yaw moment $m_z = 0$; each rotor $0 \\leq f_i \\leq 13$ N"),
        fontsize=9, color=C["muted"])
ax.set_xlim(-5.2, 5.2)
ax.set_ylim(-4.6, 4.6)
ax.grid(alpha=0.25)
figure(fig, "fig21_1_3")
plt.close(fig)
