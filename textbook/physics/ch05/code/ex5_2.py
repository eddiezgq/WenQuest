"""5.2 节的计算：

图 5.2.1    频闪式对比：水平抛出、同时自由落下、地面上以同样水平速度运动的“影子”（配动画 5.2.1）。
算例 5.2.1  分拣机器人把零件抛进料箱：出手点高 1.00 m，料箱口的中心在水平距离 1.60 m、高 0.40 m 处。出手角 θ = 30° 时，
            出手速度要多大？飞行多长时间、最高到多高、落进箱口时速度多大、方向如何（图 5.2.2）？
算例 5.2.2  同一个目标，出手角不同，所需的出手速度也不同；求所需速度最小的出手角，并与“同一高度时 45° 射程最远”比较。
算例 5.2.3  容差：出手速度有 ±2% 的误差、出手角有 ±1° 的误差时，零件落在箱口高度的水平位置散布多大？箱口宽 0.30 m，够不够？
            比较 θ = 30° 与所需速度最小的出手角（图 5.2.3）。
生活中的例子  罚球：出手点高 2.10 m，篮筐高 3.05 m，水平距离 4.20 m，求所需速度最小的出手角与速度。
"""
import math

import numpy as np
from scipy.optimize import minimize_scalar

from bookout import T, figure, out, style
from constants import g
import _draw as d

h0, X, Y = 1.00, 1.60, 0.40                      # 出手点高度；目标的水平距离与高度
dy = Y - h0


def v_needed(th, X=X, dy=dy):
    """以角 th（弧度）出手、经过 (X, dy) 所需的速度；不可能时返回 nan。"""
    den = 2 * math.cos(th) ** 2 * (X * math.tan(th) - dy)
    return math.sqrt(g * X * X / den) if den > 0 else float("nan")


th1 = math.radians(30)
v1 = v_needed(th1)
vx, vy0 = v1 * math.cos(th1), v1 * math.sin(th1)
tf = X / vx
vyf = vy0 - g * tf
H = h0 + vy0 ** 2 / (2 * g)
out(h0=h0, X=X, Y=Y, th1=30, v1=v1, vx=vx, vy0=vy0, tf=tf, H=H, vf=math.hypot(vx, vyf), angf=math.degrees(math.atan2(-vyf, vx)),
    tH=vy0 / g)

# ---- 算例 5.2.2：所需速度最小的出手角
res = minimize_scalar(lambda th: v_needed(th), bounds=(math.radians(1), math.radians(89)), method="bounded", options={"xatol": 1e-10})
thm, vmin = res.x, res.fun
th_formula = 0.5 * (math.pi / 2 + math.atan2(dy, X))   # 理论：θ = 45° + β/2，β 为目标的仰角
assert abs(thm - th_formula) < 1e-5
out(thm=math.degrees(thm), vmin=vmin, beta=math.degrees(math.atan2(dy, X)))

# ---- 算例 5.2.3：容差（落点在箱口高度处的水平位置）
def land_x(v, th):
    """以 (v, th) 出手，下落到 dy 时的水平距离。"""
    a, b, c = -0.5 * g, v * math.sin(th), -dy
    t = (-b - math.sqrt(b * b - 4 * a * c)) / (2 * a)
    return v * math.cos(th) * t


def spread(th, v):
    xs = [land_x(v * (1 + s1 * 0.02), th + s2 * math.radians(1)) for s1 in (-1, 0, 1) for s2 in (-1, 0, 1)]
    return min(xs), max(xs), land_x(v * 1.02, th) - land_x(v * 0.98, th), land_x(v, th + math.radians(1)) - land_x(v, th - math.radians(1))
lo1, hi1, dv1, dth1 = spread(th1, v1)
lom, him, dvm, dthm = spread(thm, vmin)
out(sp1=hi1 - lo1, sp_v1=dv1, sp_th1=dth1, spm=him - lom, sp_vm=dvm, sp_thm=dthm, box=0.30,
    sp_v20=spread(math.radians(20), v_needed(math.radians(20)))[2], sp_v45=spread(math.radians(45), v_needed(math.radians(45)))[2])

# ---- 罚球
Xb, dyb = 4.20, 3.05 - 2.10
resb = minimize_scalar(lambda th: v_needed(th, Xb, dyb), bounds=(math.radians(20), math.radians(85)), method="bounded", options={"xatol": 1e-10})
out(thb=math.degrees(resb.x), vb=resb.fun, vb45=v_needed(math.radians(45), Xb, dyb), vb60=v_needed(math.radians(60), Xb, dyb))

plt = style()
# ---- 图 5.2.1：频闪式对比——水平抛出、同时自由落下、地面上的影子
fig, ax = plt.subplots(figsize=(5.4, 3.2))
Hs, Vs, n = 1.20, 1.5, 8
tf_s = math.sqrt(2 * Hs / g)
for k in range(n + 1):
    t = tf_s * k / n
    ax.plot(Vs * t, Hs - 0.5 * g * t * t, "o", color=d.VA, ms=7)
    ax.plot(-0.25, Hs - 0.5 * g * t * t, "o", color="#f0a35e", ms=7)
    ax.plot(Vs * t, 0.0, "o", color=d.VB, ms=6)
    ax.plot([-0.25, Vs * t], [Hs - 0.5 * g * t * t] * 2, color="#d5dbde", lw=0.8, zorder=0)
    ax.plot([Vs * t, Vs * t], [0, Hs - 0.5 * g * t * t], color="#d5dbde", lw=0.8, zorder=0)
ax.axhline(0, color=d.MUTED, lw=1.5, zorder=0)
ax.set_title(T("蓝：水平抛出　橙：同时自由落下\n绿：地面上以同样水平速度运动的影子（每隔相同时间一个像）", "blue: thrown   orange: dropped\ngreen: shadow at the same horizontal speed (equal time steps)"), fontsize=8.5)
ax.set_xlim(-0.45, 0.95); ax.set_ylim(-0.08, 1.38); ax.set_aspect("equal"); ax.set_xlabel("x / m"); ax.set_ylabel("y / m"); d.spines(ax)
figure(fig, "fig5_2_1")

# ---- 图 5.2.2：抛进料箱
fig, ax = plt.subplots(figsize=(5.6, 3.3))
for th, col, lw in ((math.radians(20), d.MUTED, 1.4), (th1, d.VA, 2.2), (thm, d.VR, 2.2), (math.radians(60), d.VB, 1.4)):
    v0 = v_needed(th)
    tt = np.linspace(0, X / (v0 * math.cos(th)), 200)
    ax.plot(v0 * math.cos(th) * tt, h0 + v0 * math.sin(th) * tt - 0.5 * g * tt ** 2, color=col, lw=lw,
            label=f"θ = {math.degrees(th):.0f}°, v₀ = {v0:.2f} m/s")
ax.add_patch(plt.Rectangle((X - 0.15, 0), 0.30, Y, fc="#e6eaec", ec=d.MUTED))
ax.text(X, Y / 2, T("料箱", "bin"), ha="center", va="center", fontsize=9)
ax.plot([0], [h0], "o", color=d.INK, ms=6); ax.text(0.03, h0 - 0.12, T("出手点", "release"), fontsize=9)
d.arrow(ax, (0, h0), (0.3 * math.cos(th1), h0 + 0.3 * math.sin(th1)), d.VA, lw=1.4, ms=10)
ax.set_xlim(0, 1.9); ax.set_ylim(0, 1.6); ax.set_aspect("equal"); ax.set_xlabel("x / m"); ax.set_ylabel("y / m")
ax.legend(frameon=False, fontsize=8, loc="upper right"); d.spines(ax)
figure(fig, "fig5_2_2")

# ---- 图 5.2.3：所需速度与出手角；容差
fig, axs = plt.subplots(1, 2, figsize=(7.4, 3.0))
ax = axs[0]
ths = np.radians(np.linspace(5, 85, 400))
ax.plot(np.degrees(ths), [v_needed(t) for t in ths], color=d.INK, lw=2)
ax.plot(math.degrees(thm), vmin, "o", color=d.VR, label=T(f"所需速度最小：{math.degrees(thm):.0f}°", f"least speed: {math.degrees(thm):.0f}°")); ax.plot(30, v1, "o", color=d.VA, label="30°")
ax.legend(frameon=False, fontsize=8.5, loc="upper center")
ax.set_xlabel(T("出手角 θ / (°)", "launch angle θ / (°)")); ax.set_ylabel(T("所需出手速度 / (m/s)", "required speed / (m/s)")); ax.set_ylim(2.5, 7); d.spines(ax)
ax = axs[1]
das = np.linspace(-3, 3, 121)
for th, v0, col, name in ((th1, v1, d.VA, "θ = 30°"), (thm, vmin, d.VR, f"θ = {math.degrees(thm):.0f}°")):
    ax.plot(das, [100 * (land_x(v0, th + math.radians(a)) - X) for a in das], color=col, lw=2, label=name)
ax.axhline(0, color=d.MUTED, lw=0.8)
ax.set_xlabel(T("出手角的误差 / (°)", "launch-angle error / (°)")); ax.set_ylabel(T("落点偏离 / cm", "landing offset / cm"))
ax.legend(frameon=False, fontsize=8.5); d.spines(ax)
fig.tight_layout()
figure(fig, "fig5_2_3")
