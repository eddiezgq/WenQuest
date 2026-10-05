"""7.5 节的计算：

算例 7.5.1  气垫冰球台做成转台，以 ω = 1.0 rad/s 逆时针转动。冰球从中心以 v = 0.50 m/s 沿直线滑出（地面上看）。
            在转台上看它的轨迹是什么样？刚滑出时科里奥利加速度多大？（图 7.5.1）
算例 7.5.2  SCARA 机器人一边以 ω = 2.0 rad/s 转动，一边让末端沿径向以 0.50 m/s 伸出，夹着 0.80 kg 的零件，末端离轴 0.40 m。
            夹爪除了提供向心力，还要在切向推零件多大的力？
算例 7.5.3  地球上的 AGV：纬度 30°，速度 2.0 m/s，地球自转引起的水平科里奥利加速度多大？傅科摆的摆动面转一圈要多久？
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d

# ---- 算例 7.5.1
w1, v1, Rt = 1.0, 0.50, 0.80
t_end = Rt / v1
out(w1=w1, v1=v1, Rt=Rt, t_end=t_end, ac1=2 * w1 * v1, turn_deg=math.degrees(w1 * t_end))

# ---- 算例 7.5.2
w2, vr2, m2, r2 = 2.0, 0.50, 0.80, 0.40
out(w2=w2, vr2=vr2, m2=m2, r2=r2, Fcor=2 * m2 * w2 * vr2, Fcen=m2 * w2 ** 2 * r2)

# ---- 算例 7.5.3
wE = 2 * math.pi / 86164.0
phi, v3 = math.radians(30.0), 2.0
acor = 2 * wE * v3 * math.sin(phi)
TF = 86164.0 / math.sin(phi) / 3600
out(acor=acor, acor_g=acor / 9.81, TF=TF)

# ---- 图 7.5.1：地面上看与转台上看
t = np.linspace(0, t_end, 321)            # 步长 0.005 s
xg, yg = v1 * t, 0 * t
xr, yr = v1 * t * np.cos(w1 * t), -v1 * t * np.sin(w1 * t)   # 转到随台转动的坐标中
plt = style()
fig, axs = plt.subplots(1, 2, figsize=(6.2, 3.1))
for ax, (x, y), ttl in ((axs[0], (xg, yg), T("地面上看：直线", "seen from the ground: a straight line")),
                        (axs[1], (xr, yr), T("转台上看：向右弯", "seen on the turntable: bends to the right"))):
    ax.add_patch(plt.Circle((0, 0), Rt, fill=False, color=d.MUTED, lw=1.2))
    ax.plot(x, y, color=d.VR, lw=2)
    for k in range(0, 321, 40):
        ax.plot(x[k], y[k], "o", color=d.VR, ms=3.5)
    ax.plot(x[-1], y[-1], "o", color=d.VR, ms=6)
    ax.plot(0, 0, "+", color=d.INK, ms=8)
    ax.set_aspect("equal"); ax.set_xlim(-0.9, 0.9); ax.set_ylim(-0.9, 0.9); ax.axis("off")
    ax.set_title(ttl, fontsize=9.5)
ang = np.radians(np.linspace(20, 65, 40))
for ax in axs[:1]:                         # 右图的参考系随台转动，台子在其中不动，不画转向
    ax.plot(0.88 * np.cos(ang[:-1]), 0.88 * np.sin(ang[:-1]), color=d.VA, lw=1.4)
    ax.annotate("", xy=(0.88 * np.cos(ang[-1]), 0.88 * np.sin(ang[-1])), xytext=(0.88 * np.cos(ang[-3]), 0.88 * np.sin(ang[-3])),
                arrowprops=dict(arrowstyle="-|>", color=d.VA, lw=1.4, mutation_scale=12))
    ax.text(0.70, 0.70, r"$\omega$", color=d.VA, fontsize=12)
fig.text(0.5, 0.02, T("蓝色箭头：转台的转向（右图的参考系随台转动）。圆点间隔 0.2 s；冰球从中心出发", "blue arrow: sense of rotation (the right panel turns with the table). Dots every 0.2 s; the puck starts at the centre"),
         ha="center", fontsize=8.5, color=d.MUTED)
figure(fig, "fig7_5_1")
