"""5.4 节的计算：

算例 5.4.1  曲率半径 ρ = v³/|v × a|：算例 5.2.1 中零件的抛物线轨迹，最高点和落进箱口时的曲率半径；最高点处 ρ = v_x²/g。
            画出这两点的曲率圆（图 5.4.1）。
算例 5.4.2  AGV 转弯：弯道半径 1.20 m。货物不打滑要求合加速度不超过 1.50 m/s²（第 7 章由摩擦得到）。匀速过弯的最大速率多大？
            若在弯道中以 1.00 m/s² 的减速度刹车，最大速率又是多少？在“加速度圆”上标出两种情况（图 5.4.2）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d

# ---- 算例 5.4.1（数据同算例 5.2.1）
h0, X, th = 1.00, 1.60, math.radians(30)
dy = 0.40 - h0
v0 = math.sqrt(g * X * X / (2 * math.cos(th) ** 2 * (X * math.tan(th) - dy)))
vx, vy0 = v0 * math.cos(th), v0 * math.sin(th)


def rho_at(t):
    v = np.array([vx, vy0 - g * t]); a = np.array([0.0, -g])
    return np.linalg.norm(v) ** 3 / abs(v[0] * a[1] - v[1] * a[0])
tH, tf = vy0 / g, X / vx
rhoH, rhof, rho0 = rho_at(tH), rho_at(tf), rho_at(0)
assert abs(rhoH - vx ** 2 / g) < 1e-12
out(v0=v0, vx=vx, rhoH=rhoH, rho0=rho0, rhof=rhof, an_f=g * vx / math.hypot(vx, vy0 - g * tf), at_f=g * (g * tf - vy0) / math.hypot(vx, vy0 - g * tf))

# ---- 算例 5.4.2
Rc, alim, abrake = 1.20, 1.50, 1.00
v_const = math.sqrt(alim * Rc)
an_allow = math.sqrt(alim ** 2 - abrake ** 2)
v_brake = math.sqrt(an_allow * Rc)
out(Rc=Rc, alim=alim, abrake=abrake, v_const=v_const, an_allow=an_allow, v_brake=v_brake, drop=100 * (1 - v_brake / v_const))

plt = style()
fig, ax = plt.subplots(figsize=(5.6, 3.3))
tt = np.linspace(0, tf, 300)
xs, ys = vx * tt, h0 + vy0 * tt - 0.5 * g * tt ** 2
ax.plot(xs, ys, color=d.INK, lw=2)
for t, col, name in ((tH, d.VA, T("最高点", "top")), (tf, d.VR, T("箱口", "bin mouth"))):
    p = np.array([vx * t, h0 + vy0 * t - 0.5 * g * t * t]); v = np.array([vx, vy0 - g * t])
    nrm = np.array([v[1], -v[0]]) / np.linalg.norm(v)            # 指向弯曲内侧（向下弯）
    if nrm[1] > 0: nrm = -nrm
    c = p + rho_at(t) * nrm
    ph = np.linspace(0, 2 * math.pi, 300)
    ax.plot(c[0] + rho_at(t) * np.cos(ph), c[1] + rho_at(t) * np.sin(ph), color=col, lw=1, ls="--")
    ax.plot(*p, "o", color=col, ms=5); d.arrow(ax, tuple(p), tuple(c), col, lw=1, ms=8)
    ax.text(p[0] + 0.03, p[1] + 0.05, name + f"  ρ = {rho_at(t):.2f} m", color=col, fontsize=8.5)
ax.set_aspect("equal"); ax.set_xlim(-0.3, 2.3); ax.set_ylim(-0.2, 1.5); ax.set_xlabel("x / m"); ax.set_ylabel("y / m"); d.spines(ax)
figure(fig, "fig5_4_1")

fig, ax = plt.subplots(figsize=(4.0, 3.6))
ph = np.linspace(0, 2 * math.pi, 300)
ax.fill(alim * np.cos(ph), alim * np.sin(ph), color=d.VA, alpha=0.08)
ax.plot(alim * np.cos(ph), alim * np.sin(ph), color=d.VA, lw=1.5)
ax.axhline(0, color=d.MUTED, lw=0.8); ax.axvline(0, color=d.MUTED, lw=0.8)
d.arrow(ax, (0, 0), (0, alim), d.VR, lw=2); ax.text(0.08, alim * 0.55, T("匀速过弯", "constant speed"), color=d.VR, fontsize=8.5)
d.arrow(ax, (0, 0), (-abrake, an_allow), d.VB, lw=2); ax.text(-abrake - 0.05, an_allow + 0.12, T("边刹车边过弯", "braking in the bend"), color=d.VB, fontsize=8.5, ha="center")
ax.plot([-abrake, -abrake], [0, an_allow], color=d.VB, lw=0.8, ls=":"); ax.plot([-abrake, 0], [an_allow, an_allow], color=d.VB, lw=0.8, ls=":")
ax.set_xlabel(T(r"切向加速度 $a_\mathrm{t}$ / (m/s²)", r"tangential $a_\mathrm{t}$ / (m/s²)")); ax.set_ylabel(T(r"法向加速度 $a_\mathrm{n}$ / (m/s²)", r"normal $a_\mathrm{n}$ / (m/s²)"))
ax.set_aspect("equal"); ax.set_xlim(-1.9, 1.9); ax.set_ylim(-0.4, 1.9); d.spines(ax)
ax.set_title(T("加速度圆：合加速度不超过 1.5 m/s²", "acceleration circle: |a| ≤ 1.5 m/s²"), fontsize=9)
figure(fig, "fig5_4_2")
