"""8.1 节的计算：

算例 8.1.1  网球发球机器人：网球 m = 58 g，直径 6.7 cm，C_d = 0.55，空气密度 1.20 kg/m³。出球点高 1.0 m，
            以 25 m/s、仰角 10° 射出。把牛顿第二定律写成四个一阶方程（x, y, v_x, v_y），用很小的步长数值求解，
            求落地点与飞行时间，与不计空气阻力的结果比较（图 8.1.1）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d
from _ode import run

from _ball import m, D, Cd, k, v0, th, y0, S0, f, landing as land3


def landing(h):
    t, Y = run(f, S0, h, int(5 / h), "rk4")
    i = np.argmax(Y[:, 1] < 0)
    a = Y[i - 1, 1] / (Y[i - 1, 1] - Y[i, 1])                 # 两步之间线性插值求 y = 0
    return t, Y, i, Y[i - 1, 0] + a * (Y[i, 0] - Y[i - 1, 0]), t[i - 1] + a * h, Y[i - 1, 2:] + a * (Y[i, 2:] - Y[i - 1, 2:])


t, Y, i, X_lin, Tf, vl = landing(1e-4)
X = land3(1e-4)                                               # 落地点用三次插值（与 _ball.py 相同）
vy0 = v0 * math.sin(th)
T0 = (vy0 + math.sqrt(vy0 ** 2 + 2 * g * y0)) / g
X0 = v0 * math.cos(th) * T0
out(m_g=1000 * m, D_cm=100 * D, Cd=Cd, k=k, v0=v0, th=10.0, y0=y0, a_drag0=k * v0 ** 2, a_drag0_g=k * v0 ** 2 / g,
    X=X, Tf=Tf, v_land=float(np.hypot(*vl)), X0=X0, T0=T0, short_pct=100 * (1 - X / X0), vt=math.sqrt(g / k))

plt = style()
fig, ax = plt.subplots(figsize=(5.4, 2.8))
tt = np.linspace(0, T0, 200)
ax.plot(v0 * math.cos(th) * tt, y0 + vy0 * tt - g * tt ** 2 / 2, color=d.MUTED, lw=1.4, ls="--", label=T("不计空气阻力", "no drag"))
ax.plot(Y[:i + 1, 0], Y[:i + 1, 1], color=d.VR, lw=2, label=T("二次方阻力（数值解）", "quadratic drag (numerical)"))
ax.axhline(0, color=d.INK, lw=0.8)
ax.set_xlabel("x / m"); ax.set_ylabel("y / m"); ax.set_ylim(-0.2, 3.2); ax.legend(frameon=False, fontsize=8.5); d.spines(ax)
figure(fig, "fig8_1_1")
