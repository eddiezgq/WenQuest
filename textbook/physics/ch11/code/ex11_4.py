"""11.4 节的计算：

算例 11.4.1  打台球的机器人：母球以 2.0 m/s 撞击静止的目标球（质量相同、弹性碰撞、不计旋转），目标球沿与原方向成 30° 的方向飞出。
            两球碰后的速度大小和方向；验证两者垂直（图 11.4.1（a））。
算例 11.4.2  路口两台 AGV 相撞后卡在一起：A 400 kg 向东 1.5 m/s，B 600 kg 向北 1.0 m/s。碰后共同速度的大小和方向，
            动能损失；碰后一起滑行，μ = 0.50，滑多远停下（图 11.4.1（b））。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d

# ---- 算例 11.4.1
v0, th2 = 2.0, math.radians(30.0)
v2 = v0 * math.cos(th2)
v1 = v0 * math.sin(th2)
th1 = math.radians(90.0) - th2
p_before = np.array([v0, 0.0])
p_after = v1 * np.array([math.cos(th1), math.sin(th1)]) + v2 * np.array([math.cos(th2), -math.sin(th2)])
assert np.allclose(p_before, p_after) and abs(v1 ** 2 + v2 ** 2 - v0 ** 2) < 1e-12
out(v0=v0, v1=v1, v2=v2, th1=math.degrees(th1), th2=30.0)

# ---- 算例 11.4.2
mA, vA, mB, vB, mu = 400.0, 1.5, 600.0, 1.0, 0.50
P = np.array([mA * vA, mB * vB])
V = P / (mA + mB)
Vmag, ang = float(np.linalg.norm(V)), math.degrees(math.atan2(V[1], V[0]))
K0 = 0.5 * mA * vA ** 2 + 0.5 * mB * vB ** 2
K1 = 0.5 * (mA + mB) * Vmag ** 2
s = Vmag ** 2 / (2 * mu * g)
out(mA=mA, vA=vA, mB=mB, vB=vB, px=P[0], py=P[1], Vx=V[0], Vy=V[1], V=Vmag, ang=ang, K0=K0, K1=K1, dK=K0 - K1, mu=mu, s=s)

plt = style()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 3.0))
d.arrow(a1, (-2.2, 0), (-0.2, 0), d.VA, label=T("母球 2.0 m/s", "cue ball 2.0 m/s"), off=(0, 0.25), fs=9)
a1.add_patch(plt.Circle((0.0, 0), 0.12, color=d.VA)); a1.add_patch(plt.Circle((0.24 * math.cos(-th2), 0.24 * math.sin(-th2)), 0.12, color=d.VR))
o1, o2 = np.array([0.0, 0.0]), np.array([0.24 * math.cos(-th2), 0.24 * math.sin(-th2)])
d.arrow(a1, o1, o1 + 1.6 * v1 * np.array([math.cos(th1), math.sin(th1)]), d.VA, label=f"{v1:.2f} m/s", off=(-0.35, 0.1), fs=9)
d.arrow(a1, o2, o2 + 1.6 * v2 * np.array([math.cos(th2), -math.sin(th2)]), d.VR, label=f"{v2:.2f} m/s", off=(0.45, 0.25), fs=9)
a1.plot([0, 2.2], [0, 0], color=d.MUTED, lw=0.6, ls=":")
a1.text(1.0, 0.55, "60°", fontsize=9, color=d.VA); a1.text(1.1, -0.42, "30°", fontsize=9, color=d.VR)
a1.set_aspect("equal"); a1.set_xlim(-2.4, 2.8); a1.set_ylim(-1.6, 2.0); d.clean(a1)
a1.set_title(T("(a) 等质量弹性斜碰：碰后互相垂直", "(a) equal masses, elastic: 90° apart"), fontsize=9.5)
d.arrow(a2, (0, 0), (P[0] / 1000 * 1.0, 0), d.VA, label=T("A 的动量", "A's momentum"), off=(0, -0.08), fs=9)
d.arrow(a2, (P[0] / 1000, 0), (P[0] / 1000, P[1] / 1000), d.VB, label=T("B 的动量", "B's momentum"), off=(0.22, 0), fs=9)
d.arrow(a2, (0, 0), (P[0] / 1000, P[1] / 1000), d.VR, label=T("碰后总动量", "total after"), off=(-0.2, 0.08), fs=9)
a2.text(0.12, 0.05, f"{ang:.0f}°", fontsize=9)
a2.set_aspect("equal"); a2.set_xlim(-0.1, 0.9); a2.set_ylim(-0.15, 0.75); d.clean(a2)
a2.set_title(T("(b) 动量矢量相加（单位 kN·s）", "(b) momenta add as vectors (kN·s)"), fontsize=9.5)
fig.tight_layout()
figure(fig, "fig11_4_1")
