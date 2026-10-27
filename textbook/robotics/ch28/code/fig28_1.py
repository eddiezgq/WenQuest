"""28.1 节的示意图。

图 28.1.1：(a) 刷子模型（Fiala）的侧向力与侧偏角：AGV 后轴，干、湿两种地面，虚线为线性的 C α；
          (b) 侧滑与侧翻的极限侧向加速度随质心高度的变化：μ𝔤（干、湿）与 𝔤w/(2h)，标出满载 AGV 的 h = 0.65 m 与 h* = w/(2μ)；
          (c) MuJoCo 中 AGV 沿 R = 3 m 的圆匀速行驶：内侧两轮的法向力之和与侧向加速度，直线为 m𝔤/2 − m a_y h/w。
图 28.1.2：轿车（生活例子）的动力学自行车模型。(a) 以 R = 100 m 稳态转弯所需的转向角随车速的变化：运动学值 L/R、
          不足转向的轿车、质心后移后过度转向的同一辆车；(b) 100 km/h 时转向角突加 1° 的横摆角速度响应，虚线为运动学模型的值。
"""
import math

import numpy as np

from _ch28 import AGV, CAR, G, MU_DRY, MU_WET, agv_circle, axle_loads, bicycle_rhs, bicycle_steady, fiala, understeer_K
from bookout import COLORS as C, T, figure, style

plt = style()
P = AGV
fig, axs = plt.subplots(1, 3, figsize=(13.2, 3.9))
# (a)
ax = axs[0]
Fzf, Fzr = axle_loads(P)
al = np.radians(np.linspace(0, 15, 300))
for mu, col, lab in ((MU_DRY, C["z"], T("干地面 μ = 0.7", "dry, μ = 0.7")), (MU_WET, C["x"], T("湿地面 μ = 0.4", "wet, μ = 0.4"))):
    ax.plot(np.degrees(al), [fiala(a, P["Cr"], mu, Fzr) for a in al], color=col, lw=1.8, label=lab)
    ax.axhline(mu * Fzr, color=col, lw=0.8, ls=":")
ax.plot(np.degrees(al), P["Cr"] * np.tan(al), color=C["muted"], lw=1.2, ls="--", label=T("线性 Cα", "linear Cα"))
ax.set_ylim(0, 3500)
ax.set_xlabel(T("侧偏角 α / (°)", "slip angle α / (°)"))
ax.set_ylabel(T("后轴侧向力 / N", "rear-axle lateral force / N"))
ax.set_title(T("(a) 轮胎侧向力（刷子模型）", "(a) tyre lateral force (brush model)"), fontsize=11)
ax.legend(fontsize=8.5, frameon=False, loc="lower right")
ax.grid(alpha=0.25)
# (b)
ax = axs[1]
hh = np.linspace(0.2, 1.4, 200)
ax.plot(hh, G * P["w"] / (2 * hh), color=C["accent"], lw=1.8, label=T(r"侧翻 $\mathfrak{g}w/(2h)$", r"rollover $\mathfrak{g}w/(2h)$"))
ax.axhline(MU_DRY * G, color=C["z"], lw=1.6, label=T(r"侧滑（干）$\mu\mathfrak{g}$", r"skid (dry) $\mu\mathfrak{g}$"))
ax.axhline(MU_WET * G, color=C["x"], lw=1.6, label=T(r"侧滑（湿）$\mu\mathfrak{g}$", r"skid (wet) $\mu\mathfrak{g}$"))
ax.axvline(P["h"], color=C["ink"], lw=1, ls="--")
ax.text(P["h"] + 0.02, 11.2, T("满载 AGV\nh = 0.65 m", "loaded AGV\nh = 0.65 m"), fontsize=8.5)
hs = P["w"] / (2 * MU_DRY)
ax.plot([hs], [MU_DRY * G], "o", color=C["z"], ms=5)
ax.annotate("h*", (hs, MU_DRY * G), xytext=(hs - 0.17, MU_DRY * G + 2.0), fontsize=9, arrowprops=dict(arrowstyle="-", lw=0.6))
ax.set_ylim(0, 14)
ax.set_xlabel(T("质心高度 h / m", "height of the centre of mass h / m"))
ax.set_ylabel(T("极限侧向加速度 / (m/s²)", "limiting lateral acceleration / (m/s²)"))
ax.set_title(T("(b) 先侧滑还是先侧翻", "(b) skid first or roll over first"), fontsize=11)
ax.legend(fontsize=8.5, frameon=False, loc="upper right")
ax.grid(alpha=0.25)
# (c)
ax = axs[2]
vs = [1.0, 2.0, 2.5, 3.0, 3.5, 4.0, 4.3]
pts = [agv_circle(MU_DRY, lambda t, v=v: v, R=3.0, T=6.0) for v in vs]
ay = np.array([p[2] for p in pts])
inn = np.array([p[3] for p in pts])
hc = float(np.mean([p[5] for p in pts]))
xa = np.linspace(0, G * P["w"] / (2 * hc), 50)
ax.plot(xa, P["m"] * G / 2 - P["m"] * xa * hc / P["w"], color=C["muted"], lw=1.4, label=T("公式", "formula"))
ax.plot(ay, inn, "o", color=C["z"], ms=6, label=T("MuJoCo", "MuJoCo"))
ax.set_xlabel(T("侧向加速度 a_y / (m/s²)", "lateral acceleration a_y / (m/s²)"))
ax.set_ylabel(T("内侧两轮的法向力 / N", "normal force on the inner wheels / N"))
ax.set_title(T("(c) 载荷转移（R = 3 m，干地面）", "(c) load transfer (R = 3 m, dry)"), fontsize=11)
ax.legend(fontsize=8.5, frameon=False)
ax.grid(alpha=0.25)
ax.set_ylim(0, 4200)
fig.tight_layout()
figure(fig, "fig28_1_1")

# ---------------------------------------------------------------- 图 28.1.2
fig, axs = plt.subplots(1, 2, figsize=(10.4, 3.9))
ax = axs[0]
Cc = CAR
C2 = dict(Cc, a=1.6, b=1.1)
R = 100.0
v = np.linspace(0, 45, 300)
ax.plot(v * 3.6, np.degrees(np.full_like(v, Cc["L"] / R)), color=C["muted"], lw=1.4, ls="--", label=T("运动学 L/R", "kinematic L/R"))
ax.plot(v * 3.6, np.degrees(Cc["L"] / R + understeer_K(Cc) * v * v / R), color=C["z"], lw=1.8, label=T("不足转向（K > 0）", "understeer (K > 0)"))
ax.plot(v * 3.6, np.degrees(C2["L"] / R + understeer_K(C2) * v * v / R), color=C["x"], lw=1.8, label=T("质心后移：过度转向（K < 0）", "CG moved back: oversteer (K < 0)"))
ax.axhline(0, color=C["ink"], lw=0.6)
ax.set_xlabel(T("车速 / (km/h)", "speed / (km/h)"))
ax.set_ylabel(T("所需转向角 δ / (°)", "required steering angle δ / (°)"))
ax.set_title(T("(a) R = 100 m 的稳态转弯", "(a) steady turn, R = 100 m"), fontsize=11)
ax.legend(fontsize=8.5, frameon=False, loc="upper left")
ax.grid(alpha=0.25)
ax = axs[1]
v4 = 100 / 3.6
d1 = math.radians(1.0)
for P_, col, lab in ((Cc, C["z"], T("不足转向的轿车", "understeering car")), (C2, C["x"], T("质心后移", "CG moved back"))):
    x = np.zeros(2)
    ts, rs = [0.0], [0.0]
    dt = 1e-3
    f = lambda x_, P_=P_: bicycle_rhs(P_, x_, d1, v4)[0]  # noqa: E731
    for i in range(3000):
        k1 = f(x)
        k2 = f(x + dt / 2 * k1)
        k3 = f(x + dt / 2 * k2)
        k4 = f(x + dt * k3)
        x = x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        ts.append((i + 1) * dt)
        rs.append(x[1])
    ax.plot(ts, np.degrees(rs), color=col, lw=1.8, label=lab)
ax.axhline(math.degrees(v4 * math.tan(d1) / Cc["L"]), color=C["muted"], lw=1.4, ls="--", label=T("运动学 v tanδ/L", "kinematic v tanδ/L"))
ax.set_xlabel(T("时间 / s", "time / s"))
ax.set_ylabel(T("横摆角速度 r / (°/s)", "yaw rate r / (°/s)"))
ax.set_title(T("(b) 100 km/h 时转向角突加 1°", "(b) 1° step steer at 100 km/h"), fontsize=11)
ax.legend(fontsize=8.5, frameon=False, loc="lower right")
ax.grid(alpha=0.25)
fig.tight_layout()
figure(fig, "fig28_1_2")
