"""5.3 节的计算：

图 5.3.1    匀速圆周运动中 Δv 的方向：Δt 越小，Δv 越接近指向圆心，大小 |Δv| ≈ vωΔt，由此得 a = v²/R = ω²R。
算例 5.3.1  SCARA 机器人的第一关节按梯形角速度曲线转过 90°（最大角速度 3.0 rad/s，最大角加速度 10 rad/s²），
            末端到转轴的距离 R = 0.40 m。求末端的最大速率、加速与减速段的切向加速度、匀速段的向心加速度，
            以及合加速度的最大值（图 5.3.2）。
生活中的例子  洗衣机脱水：1400 r/min，滚筒半径 0.25 m，求衣物的向心加速度（g 的多少倍）。
            地球自转：赤道处与北纬 30° 处的向心加速度。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d
from _kin import trapezoid

# ---- 算例 5.3.1
R, wm, am, ang = 0.40, 3.0, 10.0, math.pi / 2
P = trapezoid(ang, wm, am)
tt = np.linspace(0, P["T"], 4001)
w, al = P["v"](tt), P["a"](tt)
vt = w * R; at = al * R; an = w ** 2 * R; atot = np.hypot(at, an)
k = int(np.argmax(atot))
out(R=R, wm=wm, am=am, Tm=P["T"], ta=P["ta"], tc=P["tc"], vmax=wm * R, at_max=am * R, an_max=wm ** 2 * R, atot_max=float(atot.max()),
    t_atot=float(tt[k]), an_g=wm ** 2 * R / g)

# ---- 生活中的例子
n_rpm, Rd = 1400, 0.25
wd = 2 * math.pi * n_rpm / 60
day = 86164.0                                     # 恒星日，s
Re = 6.371e6
we = 2 * math.pi / day
out(wd=wd, vd=wd * Rd, ad=wd ** 2 * Rd, ad_g=wd ** 2 * Rd / g, ae0=we ** 2 * Re, ae30=we ** 2 * Re * math.cos(math.radians(30)),
    ve0=we * Re, we=we)

plt = style()
# ---- 图 5.3.1：Δv 指向圆心
fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.3))
ax = axs[0]
Rc, th0, dth = 1.0, math.radians(60), math.radians(40)
ph = np.linspace(0, 2 * math.pi, 300)
ax.plot(Rc * np.cos(ph), Rc * np.sin(ph), color="#d5dbde", lw=1)
p1 = np.array([math.cos(th0), math.sin(th0)]); p2 = np.array([math.cos(th0 + dth), math.sin(th0 + dth)])
v1 = 0.6 * np.array([-math.sin(th0), math.cos(th0)]); v2 = 0.6 * np.array([-math.sin(th0 + dth), math.cos(th0 + dth)])
for p, vv, lab in ((p1, v1, r"$\boldsymbol{v}_1$"), (p2, v2, r"$\boldsymbol{v}_2$")):
    d.arrow(ax, (0, 0), tuple(p), d.MUTED, lw=1, ms=8); d.arrow(ax, tuple(p), tuple(p + vv), d.VA, lw=2)
    ax.text(*(p + vv * 1.12), lab, color=d.VA, fontsize=11, ha="center")
ax.plot([0], [0], "o", color=d.INK, ms=4); ax.text(0.04, -0.12, "O", fontsize=10)
ax.text(0.15, 0.55, r"$\Delta\theta$", fontsize=11, color=d.MUTED)
ax.set_aspect("equal"); ax.set_xlim(-1.5, 1.2); ax.set_ylim(-0.4, 1.6); ax.axis("off")
ax.text(-0.15, -0.28, T("同一个速率，方向转过 Δθ", "same speed, direction turned by Δθ"), fontsize=9, ha="center")
ax = axs[1]
o = np.array([0.0, 0.0])
d.arrow(ax, tuple(o), tuple(v1), d.VA, lw=2); d.arrow(ax, tuple(o), tuple(v2), d.VA, lw=2)
d.arrow(ax, tuple(v1), tuple(v2), d.VR, lw=2.4)
ax.text(*(v1 * 0.55 + np.array([0.05, -0.02])), r"$\boldsymbol{v}_1$", color=d.VA, fontsize=11)
ax.text(*(v2 * 0.55 + np.array([-0.1, 0.02])), r"$\boldsymbol{v}_2$", color=d.VA, fontsize=11)
mid = (v1 + v2) / 2
ax.text(*(mid + np.array([-0.16, 0.0])), r"$\Delta\boldsymbol{v}$", color=d.VR, fontsize=12)
dirc = -(p1 + p2) / 2; dirc /= np.linalg.norm(dirc)
d.arrow(ax, tuple(mid), tuple(mid + 0.25 * dirc), d.MUTED, lw=1, ms=8)
ax.text(*(mid + 0.32 * dirc), T("指向圆心", "to the centre"), fontsize=8.5, color=d.MUTED, ha="center")
ax.set_aspect("equal"); ax.set_xlim(-0.8, 0.3); ax.set_ylim(-0.65, 0.6); ax.axis("off")
ax.text(-0.25, -0.55, T("两个速度的起点放在一起：Δv 指向圆心", "common start: Δv points to the centre"), fontsize=9, ha="center")
figure(fig, "fig5_3_1")

# ---- 图 5.3.2：SCARA 末端的加速度
fig, axs = plt.subplots(2, 1, figsize=(6.0, 4.2), sharex=True)
ax = axs[0]
ax.plot(tt, vt, color=d.VA, lw=2); ax.set_ylabel(T("末端速率 / (m/s)", "tip speed / (m/s)")); d.spines(ax)
ax = axs[1]
ax.plot(tt, at, color=d.VB, lw=2, label=T("切向 αR", "tangential αR"))
ax.plot(tt, an, color=d.VR, lw=2, label=T("法向（向心）ω²R", "normal (centripetal) ω²R"))
ax.plot(tt, atot, color=d.INK, lw=1.4, ls="--", label=T("合加速度的大小", "magnitude"))
ax.axhline(0, color=d.MUTED, lw=0.8)
ax.set_xlabel("t / s"); ax.set_ylabel(r"a / (m/s$^2$)"); ax.set_ylim(-5, 7.5); ax.legend(frameon=False, fontsize=8.5, ncol=3, loc="upper center"); d.spines(ax)
fig.tight_layout()
figure(fig, "fig5_3_2")
