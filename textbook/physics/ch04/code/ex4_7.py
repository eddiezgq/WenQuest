"""4.7 节的计算：

算例 4.7.1  AGV 从一个站点开到 6.0 m 外的另一个站点，最大速度 1.2 m/s、最大加速度 0.50 m/s²。比较梯形速度曲线与
            S 形速度曲线（加加速度不超过 1.0 m/s³）的运动时间、速度、加速度和加加速度（图 4.7.1）。
算例 4.7.2  只移动 0.80 m：达不到最大速度，梯形变成三角形，峰值速度 √(aL)，时间 2√(L/a)。
算例 4.7.3  龙门机器人吊着货物移动 3.0 m（最大速度 0.80 m/s、最大加速度 0.50 m/s²），绳长 1.2 m。小车按梯形或
            S 形速度曲线运动，货物像单摆一样摆动。比较停车后残余摆动的幅度，并改变加速度上升时间 a/j（图 4.7.2）：
            加速越柔和，残余摆动越小，代价是运动时间变长（1.1 节的防摆问题）。距离只有 3 m，j_m 较小时加速度还没升到
            a_m 就要开始回落，实际上升时间小于名义值 a_m/j_m，程序一并输出实际的峰值加速度。
"""
import math

import numpy as np
from scipy.integrate import solve_ivp

from bookout import T, figure, out, style
from constants import g
import _draw as d
from _kin import trapezoid, scurve

# ---- 算例 4.7.1
L, vm, am, jm = 6.0, 1.2, 0.50, 1.0
Ptr, Psc = trapezoid(L, vm, am), scurve(L, vm, am, jm)
assert abs(Psc["xend"] - L) < 1e-5
out(L=L, vm=vm, am=am, jm=jm, T_tr=Ptr["T"], T_sc=Psc["T"], dT=Psc["T"] - Ptr["T"], aj=am / jm, ta_tr=Ptr["ta"], tc_tr=Ptr["tc"],
    xa_tr=0.5 * am * Ptr["ta"] ** 2)

# ---- 算例 4.7.2
Ls = 0.80
Pshort = trapezoid(Ls, vm, am)
assert abs(Pshort["vp"] - math.sqrt(am * Ls)) < 1e-12 and abs(Pshort["T"] - 2 * math.sqrt(Ls / am)) < 1e-12
out(Ls=Ls, vp_short=Pshort["vp"], T_short=Pshort["T"], Lmin=vm ** 2 / am)

# ---- 算例 4.7.3：吊挂货物的残余摆动
Lr, Lg, vg, ag = 1.2, 3.0, 0.80, 0.50
w0 = math.sqrt(g / Lr); T0 = 2 * math.pi / w0


def residual(prof):
    """小车按 prof 运动，返回停车后货物摆动的幅度（水平方向，mm）。"""
    acc = prof["a"]
    f = lambda t, y: [y[1], -(g / Lr) * math.sin(y[0]) - float(acc(t)) / Lr * math.cos(y[0])]
    sol = solve_ivp(f, (0, prof["T"]), [0, 0], max_step=0.002, rtol=1e-9, atol=1e-12)
    th, om = sol.y[0, -1], sol.y[1, -1]
    return 1000 * Lr * math.hypot(th, om / w0)


r_tr = residual(trapezoid(Lg, vg, ag))
tjs = np.linspace(0.05, 3.0, 60)
r_sc = np.array([residual(scurve(Lg, vg, ag, ag / tj, n=6001)) for tj in tjs])
Pg = trapezoid(Lg, vg, ag)
S1, S2 = scurve(Lg, vg, ag, ag / 1.0, n=6001), scurve(Lg, vg, ag, ag / 2.0, n=6001)
r1, r2 = residual(S1), residual(S2)
T_s = np.array([scurve(Lg, vg, ag, ag / tj, n=2001)["T"] for tj in tjs])
out(Lr=Lr, T0=T0, r_tr=r_tr, r1=r1, r2=r2, ap2=S2["ap"], tj2=S2["tj"], ap1=S1["ap"], T_g_tr=Pg["T"], T_g1=S1["T"], T_g2=S2["T"], ta_g=Pg["ta"], p1=100 * r1 / r_tr, p2=100 * r2 / r_tr)

plt = style()
# ---- 图 4.7.1
fig, axs = plt.subplots(3, 1, figsize=(6.0, 5.4), sharex=True)
tt = np.linspace(0, Psc["T"] + 0.3, 3000)
for ax, key, lab in ((axs[0], "v", "v / (m/s)"), (axs[1], "a", r"a / (m/s$^2$)")):
    ax.plot(tt, Ptr[key](tt) * (tt <= Ptr["T"]), color=d.VA, lw=2, label=T("梯形", "trapezoidal"))
    ax.plot(tt, Psc[key](tt) * (tt <= Psc["T"]), color=d.VR, lw=2, label=T("S 形", "S-curve"))
    ax.set_ylabel(lab); d.spines(ax)
axs[0].legend(frameon=False, fontsize=8.5, loc="center right")
ax = axs[2]
ax.plot(tt, Psc["j"](tt) * (tt <= Psc["T"]), color=d.VR, lw=2)
for tk in (0, Ptr["ta"], Ptr["ta"] + Ptr["tc"], Ptr["T"]):
    ax.annotate("", xy=(tk, 2.6 if tk in (0, Ptr["T"]) else -2.6), xytext=(tk, 0), arrowprops=dict(arrowstyle="->", color=d.VA, lw=1.4))
ax.text(Ptr["ta"] + 0.15, 1.6, T("梯形：加速度跳变，加加速度瞬间无穷大", "trapezoidal: jumps in a, infinite jerk"), color=d.VA, fontsize=8)
ax.set_ylim(-3, 3); ax.set_ylabel(r"j / (m/s$^3$)"); ax.set_xlabel("t / s"); d.spines(ax)
fig.tight_layout()
figure(fig, "fig4_7_1")

# ---- 图 4.7.2
fig, ax = plt.subplots(figsize=(5.0, 3.1))
ax.plot(tjs, r_sc, color=d.VR, lw=2, label=T("S 形", "S-curve"))
ax.axhline(r_tr, color=d.VA, lw=1.5, ls="--", label=T("梯形（上升时间为 0）", "trapezoidal (zero rise time)"))
ax2 = ax.twinx()
ax2.plot(tjs, T_s, color=d.MUTED, lw=1.2, ls=":")
ax2.set_ylabel(T("运动时间 / s（点线）", "move time / s (dotted)"), color=d.MUTED); ax2.tick_params(axis="y", colors=d.MUTED)
ax2.spines["top"].set_visible(False)
ax.set_xlabel(T("名义上升时间 a_m/j_m / s", "nominal rise time a_m/j_m / s")); ax.set_ylabel(T("残余摆幅 / mm", "residual swing / mm"))
ax.set_ylim(0, r_tr * 1.15); ax.legend(frameon=False, fontsize=8.5); d.spines(ax)
figure(fig, "fig4_7_2")
