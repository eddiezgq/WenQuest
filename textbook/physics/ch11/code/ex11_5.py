"""11.5 节的计算：

算例 11.5.1  移动机械臂的质心与倾翻：底盘 120 kg，质心在两轮之间正中（x = 0，高 0.30 m），支撑区 −0.40 m ≤ x ≤ 0.40 m；
            机械臂 25 kg，质心在 x = 0.50 m、高 0.90 m；末端负载 10 kg，在 x = 1.00 m、高 1.00 m。
            整体质心在哪里？静止时会不会倾翻？末端负载最多多重（只看静止）（图 11.5.1）。
算例 11.5.2  空间机器人：基座 400 kg；机械臂末端抓着 10 kg 的部件，从基座前方 1.0 m 移到后方 1.0 m（相对基座）。
            基座相对太空移动多少（机械臂自身质量计入基座）？
"""
import numpy as np

from bookout import T, figure, out, style
import _draw as d

parts = [("base", 120.0, 0.0, 0.30), ("arm", 25.0, 0.50, 0.90), ("load", 10.0, 1.00, 1.00)]
M = sum(p[1] for p in parts)
xc = sum(p[1] * p[2] for p in parts) / M
yc = sum(p[1] * p[3] for p in parts) / M
edge = 0.40
m_max = (edge * (parts[0][1] + parts[1][1]) - parts[1][1] * parts[1][2]) / (parts[2][2] - edge)   # 质心到达支撑区边缘
out(M=M, xc=xc, yc=yc, edge=edge, m_max=m_max, margin=edge - xc)

Mb, mp, dx = 400.0, 10.0, -2.0
dxb = -mp * dx / (Mb + mp)
out(Mb=Mb, mp=mp, dxb=dxb * 1000, dxp=-(dx + dxb))           # dxp：部件向后移动的距离（正值）

plt = style()
fig, ax = plt.subplots(figsize=(4.8, 3.0))
ax.add_patch(plt.Rectangle((-0.5, 0.12), 1.0, 0.36, fc="#d9dee3", ec=d.INK, lw=1.2))
for x in (-0.40, 0.40):
    ax.add_patch(plt.Circle((x, 0.10), 0.10, color=d.INK))
ax.plot([0.0, 0.0, 1.0], [0.48, 1.05, 1.0], color=d.VA, lw=5, solid_capstyle="round")
ax.add_patch(plt.Rectangle((0.95, 0.88), 0.12, 0.12, fc="#e8d9a8", ec=d.INK))
for name, m, x, y in parts:
    ax.plot(x, y, "o", color=d.MUTED, ms=5)
ax.plot(xc, yc, "X", color=d.VR, ms=10)
ax.text(xc + 0.08, yc - 0.12, T("整体质心", "overall CoM"), fontsize=9, color=d.VR)
ax.plot([xc, xc], [yc, 0], color=d.VR, lw=1, ls="--")
ax.plot([-0.40, 0.40], [-0.02, -0.02], color=d.VB, lw=4)
ax.text(-0.2, -0.13, T("支撑区", "support region"), fontsize=9, color=d.VB)
ax.axhline(0, color=d.MUTED, lw=0.8)
ax.set_aspect("equal"); ax.set_xlim(-0.7, 1.3); ax.set_ylim(-0.2, 1.2); d.clean(ax)
figure(fig, "fig11_5_1")

# ---- 图 11.5.2：实验室系与质心系中的同一次弹性碰撞（m₁ = 1 kg 以 2.0 m/s 撞静止的 m₂ = 3 kg），配动画 11.5.1
m1, m2, v1 = 1.0, 3.0, 2.0
vc = m1 * v1 / (m1 + m2)
v1a, v2a = (m1 - m2) / (m1 + m2) * v1, 2 * m1 / (m1 + m2) * v1
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 2.4))
for ax, title, (ub1, ub2, ua1, ua2) in ((a1, T("(a) 实验室系", "(a) lab frame"), (v1, 0.0, v1a, v2a)),
                                         (a2, T("(b) 质心系", "(b) centre-of-mass frame"), (v1 - vc, -vc, v1a - vc, v2a - vc))):
    for y, (u1, u2), tag in ((1.0, (ub1, ub2), T("碰前", "before")), (0.0, (ua1, ua2), T("碰后", "after"))):
        ax.add_patch(plt.Circle((-0.6, y), 0.16, color=d.VA)); ax.add_patch(plt.Circle((0.6, y), 0.24, color=d.VR))
        for x0, u, c in ((-0.6, u1, d.VA), (0.6, u2, d.VR)):
            if abs(u) > 1e-9:
                d.arrow(ax, (x0, y + 0.38), (x0 + 0.45 * u, y + 0.38), c, lw=1.8, ms=10)
                ax.text(x0 + 0.225 * u, y + 0.55, f"{u:+.1f}", fontsize=8.5, ha="center", color=c)
        ax.text(-1.95, y, tag, fontsize=9, va="center")
    ax.set_title(title, fontsize=9.5); ax.set_xlim(-2.1, 1.9); ax.set_ylim(-0.4, 1.8); ax.set_aspect("equal"); d.clean(ax)
fig.text(0.5, 0.01, T("箭头上的数字为速度（m/s）；质心系中两球总动量为零，碰后各自反向", "numbers are velocities (m/s); in the CM frame the total momentum is zero and each velocity reverses"), ha="center", fontsize=8.5)
figure(fig, "fig11_5_2")
