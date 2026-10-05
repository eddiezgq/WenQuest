"""5.5 节的计算：

算例 5.5.1  一台极坐标型（R–θ）机器人：手臂以 ω = 1.0 rad/s 匀速转动，同时以 u = 0.20 m/s 匀速伸出，r = 0.30 m + ut。
            求 t = 1.0 s 时末端速度和加速度的径向、横向分量，指出 2ṙθ̇ 项（科里奥利项）的来历；用直角坐标数值求导核对
            （图 5.5.1）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d

r0, u, w = 0.30, 0.20, 1.0
rr = lambda t: r0 + u * t
pos = lambda t: rr(t) * np.array([math.cos(w * t), math.sin(w * t)])
t1 = 1.0
r1 = rr(t1)
vr, vth = u, r1 * w
ar, ath = -r1 * w * w, 2 * u * w
h = 1e-4
vnum = (pos(t1 + h) - pos(t1 - h)) / (2 * h)
anum = (pos(t1 + h) - 2 * pos(t1) + pos(t1 - h)) / h ** 2
er = np.array([math.cos(w * t1), math.sin(w * t1)]); eth = np.array([-math.sin(w * t1), math.cos(w * t1)])
assert abs(vnum @ er - vr) < 1e-7 and abs(vnum @ eth - vth) < 1e-7
assert abs(anum @ er - ar) < 1e-5 and abs(anum @ eth - ath) < 1e-5
out(r0=r0, u=u, w=w, t1=t1, r1=r1, vr=vr, vth=vth, vmag=math.hypot(vr, vth), ar=ar, ath=ath, amag=math.hypot(ar, ath),
    deg=math.degrees(w * t1), cor_ratio=abs(ath / ar))

plt = style()
fig, ax = plt.subplots(figsize=(5.2, 3.9))
tt = np.linspace(0, 2.5, 300)
P = np.array([pos(t) for t in tt])
ax.plot(P[:, 0], P[:, 1], color="#c3ccd1", lw=1.6)
ax.plot([0], [0], "s", color=d.MUTED, ms=9)
p = pos(t1)
ax.plot([0, p[0]], [0, p[1]], color=d.INK, lw=5, alpha=0.35, solid_capstyle="round")
ax.plot(*p, "o", color=d.INK, ms=5)
s = 0.5
d.arrow(ax, tuple(p), tuple(p + s * vr * er), d.VA, lw=1.6, ms=10); ax.text(*(p + s * vr * er + np.array([0.01, -0.03])), r"$v_r$", color=d.VA, fontsize=10)
d.arrow(ax, tuple(p), tuple(p + s * vth * eth), d.VA, lw=1.6, ms=10); ax.text(*(p + s * vth * eth + np.array([-0.07, 0.02])), r"$v_\theta$", color=d.VA, fontsize=10)
d.arrow(ax, tuple(p), tuple(p + s * (vr * er + vth * eth)), d.VA, lw=2.4); ax.text(*(p + s * (vr * er + vth * eth) + np.array([0.0, 0.02])), r"$\boldsymbol{v}$", color=d.VA, fontsize=12)
d.arrow(ax, tuple(p), tuple(p + s * ar * er), d.VR, lw=1.6, ms=10); ax.text(*(p + s * ar * er + np.array([0.02, -0.02])), r"$-r\dot\theta^2$", color=d.VR, fontsize=10)
d.arrow(ax, tuple(p), tuple(p + s * ath * eth), d.VR, lw=1.6, ms=10); ax.text(*(p + s * ath * eth + np.array([-0.02, -0.075])), r"$2\dot r\dot\theta$", color=d.VR, fontsize=10)
d.arrow(ax, tuple(p), tuple(p + s * (ar * er + ath * eth)), d.VR, lw=2.4); ax.text(*(p + s * (ar * er + ath * eth) + np.array([-0.06, 0.0])), r"$\boldsymbol{a}$", color=d.VR, fontsize=12)
ax.set_aspect("equal"); ax.set_xlim(-0.6, 0.55); ax.set_ylim(-0.15, 0.78); ax.set_xlabel("x / m"); ax.set_ylabel("y / m"); d.spines(ax)
ax.set_title(T("手臂边转边伸：末端走出螺线", "turning while extending: the tip traces a spiral"), fontsize=9)
figure(fig, "fig5_5_1")
