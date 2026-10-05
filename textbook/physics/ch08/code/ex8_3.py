"""8.3 节的计算：

算例 8.3.1  同一个弹簧振子（m = 1.0 kg，k = 100 N/m，x₀ = 0.10 m），步长 h = 0.02 s（ωh = 0.2），走 5 个周期。
            比较欧拉法和半隐式欧拉法的能量与相平面轨迹（图 8.3.1）。
算例 8.3.2  机械臂断电后像单摆一样自由摆动：摆长 L = 0.50 m（看作质点在杆端），由 60° 释放，不计摩擦。
            步长 0.01 s 仿真 30 s，三种算法（欧拉法、半隐式欧拉法、RK4）最后的最大摆角各是多少？
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d
from _ode import run, semi_implicit

# ---- 算例 8.3.1
mS, kS, A = 1.0, 100.0, 0.10
w = math.sqrt(kS / mS); Tp = 2 * math.pi / w; h = 0.02
n = int(round(5 * Tp / h))
fS = lambda t, y: np.array([y[1], -kS / mS * y[0]])
tE, YE = run(fS, np.array([A, 0.0]), h, n, "euler")
tS, XS, VS = semi_implicit(lambda t, x, v: -kS / mS * x, [A], [0.0], h, n)
E0 = 0.5 * kS * A * A
EE = (0.5 * kS * YE[:, 0] ** 2 + 0.5 * mS * YE[:, 1] ** 2) / E0
ES = (0.5 * kS * XS[:, 0] ** 2 + 0.5 * mS * VS[:, 0] ** 2) / E0
out(h3=h, wh3=w * h, EE5=EE[-1], ES_min=ES.min(), ES_max=ES.max(), ES_dev_pct=100 * max(ES.max() - 1, 1 - ES.min()))

# ---- 算例 8.3.2
L, th0, hp, Tend = 0.50, math.radians(60.0), 0.01, 30.0
np_ = int(round(Tend / hp))
fp = lambda t, y: np.array([y[1], -g / L * math.sin(y[0])])
res = {}
for meth in ("euler", "rk4"):
    _, Y = run(fp, np.array([th0, 0.0]), hp, np_, meth)
    res[meth] = math.degrees(np.abs(Y[-int(2 / hp):, 0]).max())
    if meth == "euler":
        res["t_over"] = hp * int(np.argmax(np.abs(Y[:, 0]) > math.pi))       # 欧拉法的“摆”第一次越过最高点
_, Xp, Vp = semi_implicit(lambda t, x, v: -g / L * np.sin(x), [th0], [0.0], hp, np_)
res["semi"] = math.degrees(np.abs(Xp[-int(2 / hp):, 0]).max())
out(L=L, hp=hp, Tend=Tend, amp_euler=res["euler"], amp_semi=res["semi"], amp_rk4=res["rk4"], t_over=res["t_over"])

plt = style()
fig, axs = plt.subplots(1, 2, figsize=(6.4, 3.0))
ax = axs[0]
ax.plot(tE / Tp, EE, color=d.VR, lw=1.6, label=T("欧拉法", "Euler"))
ax.plot(tS / Tp, ES, color=d.VA, lw=1.6, label=T("半隐式欧拉法", "semi-implicit Euler"))
ax.axhline(1, color=d.MUTED, lw=0.8, ls="--"); ax.set_yscale("log")
ax.set_xlabel(T("周期数 t/T", "periods t/T")); ax.set_ylabel(T("能量 E/E₀", "energy E/E₀")); ax.legend(frameon=False, fontsize=8); d.spines(ax)
ax = axs[1]
q = np.linspace(0, 2 * math.pi, 200)
ax.plot(A * np.cos(q), A * w * np.sin(q), color=d.MUTED, lw=1.2, ls="--")
n15 = int(round(1.5 * Tp / h))
ax.plot(YE[:n15, 0], YE[:n15, 1], color=d.VR, lw=1.2)
ax.plot(XS[:, 0], VS[:, 0], color=d.VA, lw=1.2)
ax.set_xlabel("x / m"); ax.set_ylabel("v / (m/s)"); ax.set_aspect(1 / w); d.spines(ax)
ax.set_xlim(-0.2, 0.2); ax.set_ylim(-2.0, 2.0)
ax.set_title(T("相平面（虚线：精确解；红：欧拉法前 1.5 个周期）", "phase plane (dashed: exact; red: Euler, first 1.5 periods)"), fontsize=8.5)
fig.tight_layout()
figure(fig, "fig8_3_1")
