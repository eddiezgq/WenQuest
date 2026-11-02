"""13.5 节的计算：

算例 13.5.1  手机看成均匀长方体：长 a = 0.150 m、宽 b = 0.075 m、厚 c = 0.008 m，质量 0.20 kg。求绕三条对称轴（主轴）的转动惯量；
            绕沿长宽对角线方向的轴以 ω 转动时，角动量与角速度的夹角多大？
算例 13.5.2  装歪的转子：均匀圆盘 1.0 kg、半径 0.10 m，装在轴上时盘面与轴的垂直面歪了 1.0°，以 300 rad/s 转动。
            角动量偏离转轴多少？要维持这样的转动，轴承要对转子施加多大的力矩？两个轴承相距 0.10 m，各受多大的旋转力？
算例 13.5.3  中间轴不稳定：手机绕三条主轴之一以 6.0 rad/s 抛起，加上很小的扰动（另外两个分量各 0.01 rad/s）。
            用欧拉方程数值积分，绕最大、最小转动惯量的轴转动是稳定的，绕中间的轴会反复翻转（图 13.5.1）。
"""
import math

import numpy as np
from scipy.integrate import solve_ivp

from bookout import T, figure, out, style
import _draw as d

m, a, b, c = 0.20, 0.150, 0.075, 0.008
Ix, Iy, Iz = m * (b * b + c * c) / 12, m * (a * a + c * c) / 12, m * (a * a + b * b) / 12   # x 沿长边，y 沿宽边，z 沿厚度
I = np.diag([Ix, Iy, Iz])
u = np.array([a, b, 0.0]); u /= np.linalg.norm(u)
Lv = I @ u
ang = math.degrees(math.acos(float(Lv @ u) / np.linalg.norm(Lv)))
out(Ix_e5=Ix * 1e5, Iy_e5=Iy * 1e5, Iz_e5=Iz * 1e5, ang=ang, Iu_e5=float(u @ I @ u) * 1e5)

M, R, eps, w = 1.0, 0.10, math.radians(1.0), 300.0
I3, I1 = 0.5 * M * R * R, 0.25 * M * R * R
# 圆盘主轴坐标：对称轴与转轴夹角 eps；ω 沿转轴
wp, wa = w * math.cos(eps), w * math.sin(eps)                   # ω 在对称轴上的分量、在盘面内的分量
Lp, La = I3 * wp, I1 * wa
off = math.degrees(math.atan2(La, Lp)) - math.degrees(eps)      # L 与转轴的夹角（L 比对称轴更靠近转轴还是更远）
L_perp = abs(Lp * math.sin(eps) - La * math.cos(eps))           # L 垂直于转轴的分量
torque = w * L_perp                                             # 这个分量随转子以 ω 转圈：dL/dt = ω × L
out(I3=I3, I1=I1, w=w, L_perp=L_perp, off=abs(off), torque=torque, Fb=torque / 0.10, rpm=w * 60 / (2 * math.pi))
assert abs(torque - w * w * (I3 - I1) * math.sin(eps) * math.cos(eps)) < 1e-9


def euler(t, y):
    w1, w2, w3 = y
    return [(Iy - Iz) * w2 * w3 / Ix, (Iz - Ix) * w3 * w1 / Iy, (Ix - Iy) * w1 * w2 / Iz]


tt = np.linspace(0, 6.0, 3001)
runs = {}
for k, w0 in (("x", [6.0, 0.01, 0.01]), ("y", [0.01, 6.0, 0.01]), ("z", [0.01, 0.01, 6.0])):
    s = solve_ivp(euler, (0, 6.0), w0, t_eval=tt, rtol=1e-10, atol=1e-12)
    runs[k] = s.y
flips = int(np.sum(np.diff(np.sign(runs["y"][1])) != 0))
out(dev_x=float(np.abs(runs["x"][1:]).max()), dev_z=float(np.abs(runs["z"][:2]).max()), flips=flips)
assert flips >= 2 and np.abs(runs["x"][1:]).max() < 0.1

plt = style()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 2.8), sharey=True)
for ax, k, ttl in ((a1, "z", T("(a) 绕最大主轴（厚度方向）", "(a) about the largest axis")), (a2, "y", T("(b) 绕中间主轴（宽度方向）", "(b) about the middle axis"))):
    W = runs[k]
    for j, (lab, col) in enumerate(((r"$\omega_x$", d.VB), (r"$\omega_y$", d.VR), (r"$\omega_z$", d.VA))):
        ax.plot(tt, W[j], color=col, lw=1.6, label=lab)
    ax.axhline(0, color=d.MUTED, lw=0.6); ax.set_xlabel(T("时间 / s", "time / s")); ax.set_title(ttl, fontsize=9.5); d.spines(ax)
a1.set_ylabel(T("角速度分量 / (rad/s)", "angular velocity components / (rad/s)")); a2.legend(frameon=False, fontsize=8.5, loc="center", bbox_to_anchor=(0.62, 0.72))
fig.tight_layout()
figure(fig, "fig13_5_1")
