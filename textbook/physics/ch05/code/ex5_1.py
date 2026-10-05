"""5.1 节的计算：

算例 5.1.1  打磨机器人的工具沿“8”字形路径运动：r(t) = (x₀ + A sin ωt, y₀ + B sin 2ωt)，x₀ = 0.50 m、y₀ = 0.30 m、
            A = 0.15 m、B = 0.08 m、ω = 1.2 rad/s。求 t = 0.5 s 时的位置、速度和加速度矢量；比较 0.5～0.7 s 的平均速度
            与 t = 0.5 s 的瞬时速度；说明速度沿切线、加速度指向轨迹弯曲的内侧（图 5.1.1）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d

x0, y0, A, B, w = 0.50, 0.30, 0.15, 0.08, 1.2
r = lambda t: np.array([x0 + A * math.sin(w * t), y0 + B * math.sin(2 * w * t)])
v = lambda t: np.array([A * w * math.cos(w * t), 2 * B * w * math.cos(2 * w * t)])
a = lambda t: np.array([-A * w * w * math.sin(w * t), -4 * B * w * w * math.sin(2 * w * t)])
t1, dt = 0.5, 0.2
h = 1e-5
assert np.allclose((r(t1 + h) - r(t1 - h)) / (2 * h), v(t1), atol=1e-8)
assert np.allclose((v(t1 + h) - v(t1 - h)) / (2 * h), a(t1), atol=1e-7)
vavg = (r(t1 + dt) - r(t1)) / dt
R, V, Acc = r(t1), v(t1), a(t1)
ut = V / np.linalg.norm(V)
out(t1=t1, rx=R[0], ry=R[1], vx=V[0], vy=V[1], vmag=float(np.linalg.norm(V)), vdeg=math.degrees(math.atan2(V[1], V[0])),
    ax=Acc[0], ay=Acc[1], amag=float(np.linalg.norm(Acc)), vavx=vavg[0], vavy=vavg[1], vavmag=float(np.linalg.norm(vavg)),
    vavdeg=math.degrees(math.atan2(vavg[1], vavg[0])), at=float(Acc @ ut), an=float(abs(Acc[0] * ut[1] - Acc[1] * ut[0])),
    T8=2 * math.pi / w, dt=dt, vdeg_mid=math.degrees(math.atan2(v(t1 + dt / 2)[1], v(t1 + dt / 2)[0])), tmid=t1 + dt / 2)

plt = style()
fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.4), gridspec_kw={"width_ratios": [1, 1.25]})
tt = np.linspace(0, 2 * math.pi / w, 400)
P = np.array([r(t) for t in tt])
ax = axs[0]
ax.plot(P[:, 0], P[:, 1], color="#c3ccd1", lw=1.6)
ax.plot([0], [0], "s", color=d.MUTED, ms=8); ax.text(0.02, -0.04, T("机器人基座 O", "robot base O"), fontsize=8.5, color=d.MUTED)
d.arrow(ax, (0, 0), tuple(R), d.INK, lw=1.4, ms=10)
ax.text(R[0] * 0.5 - 0.02, R[1] * 0.5 + 0.03, r"$\boldsymbol{r}$", fontsize=12)
ax.plot(*R, "o", color=d.INK, ms=4)
ax.set_aspect("equal"); ax.set_xlim(-0.05, 0.75); ax.set_ylim(-0.08, 0.45); ax.set_xlabel("x / m"); ax.set_ylabel("y / m"); d.spines(ax)
ax.set_title(T("位置矢量从原点指向工具", "the position vector points from the origin to the tool"), fontsize=8.5)
ax = axs[1]
ax.plot(P[:, 0], P[:, 1], color="#c3ccd1", lw=1.6)
for tk, lab in ((t1, True), (2.2, False), (3.6, False), (4.6, False)):
    Rk, Vk, Ak = r(tk), v(tk), a(tk)
    d.arrow(ax, tuple(Rk), tuple(Rk + 0.5 * Vk), d.VA, lw=2.0)
    d.arrow(ax, tuple(Rk), tuple(Rk + 0.15 * Ak), d.VR, lw=2.0)
    ax.plot(*Rk, "o", color=d.INK, ms=4)
ax.text(*(R + 0.5 * V + np.array([0.005, 0.008])), r"$\boldsymbol{v}$", color=d.VA, fontsize=12)
ax.text(*(R + 0.15 * Acc + np.array([0.012, 0.0])), r"$\boldsymbol{a}$", color=d.VR, fontsize=12)
Q = r(t1 + dt)
ax.plot(*Q, "o", color=d.VB, ms=4); d.arrow(ax, tuple(R), tuple(Q), d.VB, lw=1.4, ms=9)
ax.text(Q[0] + 0.008, Q[1] - 0.02, r"$\Delta\boldsymbol{r}$", color=d.VB, fontsize=11)
ax.set_aspect("equal"); ax.set_xlim(0.30, 0.72); ax.set_ylim(0.18, 0.42); ax.set_xlabel("x / m"); d.spines(ax)
ax.set_title(T("放大：v 沿切线，a 指向弯曲的内侧", "zoom: v along the tangent, a towards the inside of the bend"), fontsize=8.5)
fig.tight_layout()
figure(fig, "fig5_1_1")
