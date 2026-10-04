"""3.2 节的计算：

算例 3.2.2  机械臂的一个关节以恒定角速度 ω = 1.5 rad/s 转动，连杆长 L = 0.40 m，末端的位置矢量
            r(t) = L(cos ωt, sin ωt)。对每个分量求导得速度 v(t) 和加速度 a(t)；核对 v 与 r 垂直、|v| = ωL、
            a = −ω² r（图 3.2.1）。再用中心差分数值求导，与公式比较。
算例 3.2.1  链式法则：关节从静止起步，转角 θ(t) = 0.5 t²（rad），连杆末端的高度 y = L sin θ。求 t = 1.0 s 时末端
            上升的速度 dy/dt = L cos θ · dθ/dt，并用数值求导核对。
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d

L, w = 0.40, 1.5
r = lambda t: L * np.array([math.cos(w * t), math.sin(w * t)])
v = lambda t: L * w * np.array([-math.sin(w * t), math.cos(w * t)])
a = lambda t: -L * w * w * np.array([math.cos(w * t), math.sin(w * t)])
t1 = 0.8
h = 1e-5
v_num = (r(t1 + h) - r(t1 - h)) / (2 * h)
a_num = (r(t1 + h) - 2 * r(t1) + r(t1 - h)) / h ** 2
assert np.allclose(v_num, v(t1), atol=1e-8) and np.allclose(a_num, a(t1), atol=1e-4)
assert abs(r(t1) @ v(t1)) < 1e-12
out(L=L, w=w, t1=t1, rx=r(t1)[0], ry=r(t1)[1], vx=v(t1)[0], vy=v(t1)[1], ax=a(t1)[0], ay=a(t1)[1],
    vmag=L * w, amag=L * w * w, vnx=v_num[0], vny=v_num[1], rdotv=float(r(t1) @ v(t1)), deg=math.degrees(w * t1))

# ---- 算例 3.2.1：链式法则
th = lambda t: 0.5 * t ** 2
y = lambda t: L * math.sin(th(t))
t2 = 1.0
dy = L * math.cos(th(t2)) * t2                                # dθ/dt = t
dy_num = (y(t2 + h) - y(t2 - h)) / (2 * h)
assert abs(dy - dy_num) < 1e-8
out(e_const=math.e, t2=t2, th2=th(t2), th2deg=math.degrees(th(t2)), dth=t2, dy=dy, dy_num=dy_num)

plt = style()
# ---- 图 3.2.1：匀速转动的末端：位置、速度、加速度
fig, ax = plt.subplots(figsize=(4.8, 4.2))
ph = np.linspace(0, 2 * math.pi, 200)
ax.plot(L * np.cos(ph), L * np.sin(ph), color="#d5dbde", lw=1)
ax.plot([0], [0], "s", color=d.MUTED, ms=10)
for tk in (0.25, t1, 2.6):
    p, vv, aa = r(tk), v(tk), a(tk)
    sv, sa = 0.25, 0.18
    d.arrow(ax, (0, 0), p, d.INK, lw=1.2, ms=10)
    d.arrow(ax, p, p + sv * vv, d.VA, lw=2.2)
    d.arrow(ax, p, p + sa * aa, d.VR, lw=2.2)
    ax.plot(*p, "o", color=d.INK, ms=4)
p = r(t1)
ax.text(*(p + 0.25 * v(t1) + np.array([0.0, 0.03])), r"$\boldsymbol{v}$", color=d.VA, fontsize=12)
ax.text(*(p + 0.18 * a(t1) * 0.55 + np.array([0.03, 0.0])), r"$\boldsymbol{a}$", color=d.VR, fontsize=12)
ax.text(*(p * 0.5 + np.array([-0.06, 0.02])), r"$\boldsymbol{r}$", color=d.INK, fontsize=12)
ax.text(0, -0.5, T("v 沿切线、与 r 垂直；a 指向圆心", "v is tangent, perpendicular to r; a points to the centre"), ha="center", fontsize=9, color=d.MUTED)
ax.set_xlim(-0.6, 0.6); ax.set_ylim(-0.56, 0.56); ax.set_aspect("equal"); ax.set_xlabel("x / m"); ax.set_ylabel("y / m"); d.spines(ax)
figure(fig, "fig3_2_1")
