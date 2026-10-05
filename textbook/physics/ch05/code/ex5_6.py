"""5.6 节的计算：

算例 5.6.1  传送带以 u = 0.30 m/s 向 +x 运动。机器人抓取带上的零件时，夹爪相对传送带竖直下降 0.15 m（相对速度 0.30 m/s），
            再竖直提起。在传送带参考系和地面参考系中，夹爪的速度和轨迹各是什么样（图 5.6.1）？
算例 5.6.2  巡检无人机相对空气的速度（空速）为 8.0 m/s，风从西向东吹，风速 4.0 m/s。它要飞到正北 1.2 km 处：机头应偏向
            哪个方向？对地速度多大？用多长时间？若机头朝正北，会偏到哪里（图 5.6.2）？
生活中的例子  雨滴竖直下落，速度 6.0 m/s；汽车以 54 km/h 行驶，车里的人看到雨滴与竖直方向的夹角。
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d

# ---- 算例 5.6.1
u, hd, vd = 0.30, 0.15, 0.30
td = hd / vd
vg = np.array([u, -vd])
out(u=u, hd=hd, vd=vd, td=td, vg=float(np.linalg.norm(vg)), vgdeg=math.degrees(math.atan2(vd, u)), dx=u * 2 * td)

# ---- 算例 5.6.2
va, wind, D = 8.0, 4.0, 1200.0
phi = math.degrees(math.asin(wind / va))          # 机头偏向西的角度
vground = math.sqrt(va ** 2 - wind ** 2)
t_fly = D / vground
t_north = D / va
drift = wind * t_north
out(va=va, wind=wind, D_km=D / 1000, phi=phi, vground=vground, t_fly=t_fly, t_north=t_north, drift=drift,
    vg_north=math.hypot(va, wind), ang_north=math.degrees(math.atan2(wind, va)))

# ---- 雨
vr, vc = 6.0, 54 / 3.6
out(vrain=vr, vcar=vc, rain_deg=math.degrees(math.atan2(vc, vr)), rain_rel=math.hypot(vc, vr))

plt = style()
fig, axs = plt.subplots(1, 2, figsize=(7.4, 2.9))
tt = np.linspace(0, 2 * td, 100)
xb = np.zeros_like(tt)                                          # 传送带系：竖直下降、提起
yb = np.where(tt < td, hd - vd * tt, vd * (tt - td))
for ax, xs, title in ((axs[0], xb, T("传送带参考系：竖直上下", "belt frame: straight down and up")),
                      (axs[1], xb + u * tt, T("地面参考系：斜下、斜上", "ground frame: slanting down and up"))):
    ax.plot(xs, yb, color=d.VR, lw=2)
    ax.axhline(0, color=d.MUTED, lw=3)
    for k in (25, 75):                                          # 下降和提起各画一个速度箭头
        d.arrow(ax, (xs[k], yb[k]), (xs[k] + 0.1 * (xs[k + 1] - xs[k]) / (tt[1] - tt[0]), yb[k] + 0.1 * (yb[k + 1] - yb[k]) / (tt[1] - tt[0])), d.VA, lw=1.8, ms=10)
    ax.set_aspect("equal"); ax.set_xlim(-0.08, 0.36); ax.set_ylim(-0.04, 0.2); ax.set_xlabel("x / m"); d.spines(ax)
    ax.set_title(title, fontsize=9)
axs[0].set_ylabel(T("夹爪高度 / m", "gripper height / m"))
axs[1].text(0.2, 0.012, T("传送带 →", "belt →"), fontsize=8.5, color=d.MUTED)
fig.tight_layout()
figure(fig, "fig5_6_1")

fig, ax = plt.subplots(figsize=(4.4, 3.4))
o = np.array([0.0, 0.0])
air = np.array([-wind, vground])
d.arrow(ax, tuple(o), tuple(air), d.VA, lw=2.2); ax.text(-wind / 2 - 2.6, vground / 2, T("相对空气\n8.0 m/s", "airspeed\n8.0 m/s"), color=d.VA, fontsize=8.5)
d.arrow(ax, tuple(air), (0, vground), d.VB, lw=2.2); ax.text(-wind / 2, vground + 0.3, T("风 4.0 m/s", "wind 4.0 m/s"), color=d.VB, fontsize=8.5, ha="center")
d.arrow(ax, tuple(o), (0, vground), d.VR, lw=2.4); ax.text(0.2, vground / 2, T(f"对地\n{vground:.2f} m/s", f"ground\n{vground:.2f} m/s"), color=d.VR, fontsize=8.5)
ax.text(-0.95, 1.5, f"{phi:.0f}°", fontsize=9, color=d.MUTED)
d.arrow(ax, (3.2, 5.6), (3.2, 7.0), d.INK, lw=1.2, ms=9); ax.text(3.2, 7.2, T("北", "N"), fontsize=10, ha="center")
d.arrow(ax, (3.2, 5.6), (4.4, 5.6), d.INK, lw=1.2, ms=9); ax.text(4.6, 5.5, T("东", "E"), fontsize=10)
ax.set_aspect("equal"); ax.set_xlim(-5, 4.8); ax.set_ylim(-0.5, 8.2); ax.axis("off")
figure(fig, "fig5_6_2")
