"""15.5 节的计算：

算例 15.5.1  牛顿大炮：在 200 km 高的“山顶”上（不计空气阻力和地球自转）水平发射炮弹，初速度 6.0、7.0、7.79（圆轨道速度）、9.0、10.5、11.5 km/s
            时的轨道（图 15.5.1）。数值积分（速度韦尔莱法）：v = √(GM/r₀) 时为圆，√(2GM/r₀) 以上时逃逸。
算例 15.5.2  空间站轨道（高 400 km）的速率和周期；地球静止轨道的半径和高度（周期取一个恒星日 86 164 s）；
            GPS 卫星（周期半个恒星日）的轨道高度。
算例 15.5.3  霍曼转移：卫星从 400 km 的圆轨道经过一条椭圆轨道转到地球静止轨道，两次点火各要多大的速度增量（图 15.5.2）？
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import GM_earth, R_earth_mean
import _draw as d

GM, R = GM_earth, R_earth_mean
v1 = math.sqrt(GM / R); v2 = math.sqrt(2 * GM / R)
out(v1=v1 / 1000, v2=v2 / 1000)


H0 = 200e3
r0 = R + H0
vc0, ve0 = math.sqrt(GM / r0), math.sqrt(2 * GM / r0)
out(vc0=vc0 / 1000, ve0=ve0 / 1000)


def shoot(v0, tmax=60000.0, dt=2.0):
    x, y, vx, vy = 0.0, r0, v0, 0.0
    pts = [(x, y)]
    ax, ay = -GM * x / r0 ** 3, -GM * y / r0 ** 3
    t, ang, prev = 0.0, 0.0, math.atan2(x, y)
    while t < tmax:
        vx += 0.5 * dt * ax; vy += 0.5 * dt * ay
        x += dt * vx; y += dt * vy
        r3 = (x * x + y * y) ** 1.5; ax, ay = -GM * x / r3, -GM * y / r3
        vx += 0.5 * dt * ax; vy += 0.5 * dt * ay
        t += dt; pts.append((x, y))
        cur = math.atan2(x, y); dphi = (cur - prev + math.pi) % (2 * math.pi) - math.pi; ang += dphi; prev = cur
        if math.hypot(x, y) < R: break                              # 落地
        if math.hypot(x, y) > 6 * R or ang >= 2 * math.pi: break    # 飞远了，或绕了一圈
    return np.array(pts), t, ang


speeds = [6.0, 7.0, round(vc0 / 1000, 2), 9.0, 10.5, 11.5]
paths = {v: shoot(v * 1000) for v in speeds}
P6, t6, a6 = paths[6.0]
P7, t7, a7 = paths[7.0]
Pc, tc, ac_ = paths[speeds[2]]
assert abs(np.hypot(Pc[:, 0], Pc[:, 1]).max() - r0) / r0 < 1e-3          # 圆轨道：半径不变
out(t6_min=t6 / 60, range6_km=a6 * R / 1000, t7_min=t7 / 60, range7_km=a7 * R / 1000, Tc_min=tc / 60)

h = 400e3; r = R + h
vs = math.sqrt(GM / r); Ts = 2 * math.pi * r / vs
Tsid = 86164.0
rg = (GM * Tsid ** 2 / (4 * math.pi ** 2)) ** (1 / 3)
rgps = (GM * (Tsid / 2) ** 2 / (4 * math.pi ** 2)) ** (1 / 3)
out(vs=vs / 1000, Ts_min=Ts / 60, rg_km=rg / 1000, hg_km=(rg - R) / 1000, vg=math.sqrt(GM / rg) / 1000, hgps_km=(rgps - R) / 1000)

a = (r + rg) / 2
vp = math.sqrt(GM * (2 / r - 1 / a)); va = math.sqrt(GM * (2 / rg - 1 / a))
dv1 = vp - vs; dv2 = math.sqrt(GM / rg) - va
Tt = math.pi * math.sqrt(a ** 3 / GM)
out(dv1=dv1 / 1000, dv2=dv2 / 1000, dv=(dv1 + dv2) / 1000, Tt_h=Tt / 3600, vp=vp / 1000, va=va / 1000)

plt = style()
fig, ax = plt.subplots(figsize=(4.6, 4.0))
th = np.linspace(0, 2 * np.pi, 400)
ax.fill(R * np.cos(th) / 1e6, R * np.sin(th) / 1e6, color="#dfe8ef", lw=0)
ax.plot(R * np.cos(th) / 1e6, R * np.sin(th) / 1e6, color=d.MUTED, lw=1)
cols = [d.MUTED, d.VB, d.VA, d.VR, "#8e44ad", d.INK]
for v, c in zip(speeds, cols):
    P = paths[v][0]
    ax.plot(P[::5, 0] / 1e6, P[::5, 1] / 1e6, color=c, lw=1.6, label=f"{v:g} km/s")
ax.plot(0, r0 / 1e6, "o", color=d.INK, ms=4)
ax.set_aspect("equal"); ax.set_xlim(-22, 40); ax.set_ylim(-26, 26)
ins = ax.inset_axes([0.6, 0.66, 0.38, 0.3])                        # 放大：6、7 km/s 很快落地
ins.fill(R * np.cos(th) / 1e6, R * np.sin(th) / 1e6, color="#dfe8ef", lw=0)
for v, c in zip(speeds[:3], cols[:3]):
    P = paths[v][0]; ins.plot(P[:, 0] / 1e6, P[:, 1] / 1e6, color=c, lw=1.6)
ins.set_xlim(-0.2, 3.6); ins.set_ylim(4.8, 6.8); ins.set_xticks([]); ins.set_yticks([])
ins.set_title(T("开头放大", "close-up"), fontsize=7)
ax.set_xlabel("x / 1000 km"); ax.set_ylabel("y / 1000 km")
ax.legend(frameon=False, fontsize=7.5, loc="lower left", title=T("水平发射速度", "horizontal launch speed"), title_fontsize=7.5); d.spines(ax)
figure(fig, "fig15_5_1")

fig, ax = plt.subplots(figsize=(4.4, 4.0))
ax.fill(R * np.cos(th) / 1e6, R * np.sin(th) / 1e6, color="#dfe8ef", lw=0)
ax.plot(r * np.cos(th) / 1e6, r * np.sin(th) / 1e6, color=d.VA, lw=1.4, label=T("400 km 圆轨道", "400 km circular orbit"))
ax.plot(rg * np.cos(th) / 1e6, rg * np.sin(th) / 1e6, color=d.VR, lw=1.4, label=T("静止轨道", "geostationary orbit"))
e = (rg - r) / (rg + r); tt = np.linspace(0, np.pi, 200)
rr_ = a * (1 - e ** 2) / (1 + e * np.cos(tt))
ax.plot(rr_ * np.cos(tt) / 1e6, rr_ * np.sin(tt) / 1e6, color=d.VB, lw=1.6, ls="--", label=T("转移轨道", "transfer orbit"))
ax.plot(r / 1e6, 0, "o", color=d.VB, ms=5); ax.text(r / 1e6 + 1.5, -2.5, "Δv₁", fontsize=9, color=d.VB)
ax.plot(-rg / 1e6, 0, "o", color=d.VB, ms=5); ax.text(-rg / 1e6 + 1.5, -2.5, "Δv₂", fontsize=9, color=d.VB)
ax.set_aspect("equal"); ax.set_xlim(-46, 46); ax.set_ylim(-46, 46)
ax.set_xlabel("x / 1000 km"); ax.set_ylabel("y / 1000 km"); ax.legend(frameon=False, fontsize=7.5, loc="lower right"); d.spines(ax)
figure(fig, "fig15_5_2")
