"""7.2 节的示意图。

图 7.2.1：欧拉法的几何意义：沿切线走一步；局部截断误差与全局误差（电机起动，h = 10 ms）。
图 7.2.2：连杆单摆积分 2 s 的误差与步长（双对数坐标），斜率就是方法的阶。
图 7.2.3：欧拉法仿真电机起动：h = 5 ms、30 ms、45 ms。
图 7.2.4：长时间仿真中的能量误差：(a) 欧拉法 10 s；(b) RK4、辛欧拉法、施特默-韦莱法 1000 s。
图 7.2.5：相空间中一小片初始状态经过 2 s 后的样子：欧拉法使面积变大，辛欧拉法保持面积。
图 7.2.6：陀螺仪积分：(a) 姿态误差与步长；(b) 正交性误差随时间增长。
"""
import math

import numpy as np
from scipy.integrate import solve_ivp

from _ode import (angle_between, cone_R, euler, lie_integrate, lie_step, orth, link_params, motor_first_order, pend_energy, pend_f, rk4, run, run_pend, symp_euler,
                  verlet)
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
box = dict(fc="white", ec="none", pad=1.0, alpha=0.9)
PURPLE = "#8e44ad"


def clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


tau, K = motor_first_order()
w_inf = K * 12.0
f_m = lambda t, x: np.array([(w_inf - x[0]) / tau])
w_ex = lambda t: w_inf * (1 - np.exp(-t / tau))

# ---------------------------------------------------------------- 图 7.2.1
fig, ax = plt.subplots(figsize=(5.8, 3.8))
h = 0.01
ts = np.linspace(0, 0.06, 300)
ax.plot(ts * 1e3, w_ex(ts), color=C["ink"], lw=1.6, label=T("精确解", "exact solution"))
xs = run(euler, f_m, [0.0], 0.06, h, keep=True)[:, 0]
tk = np.arange(len(xs)) * h
ax.plot(tk * 1e3, xs, "o-", color=C["x"], lw=1.3, ms=4, label=T("欧拉法 h = 10 ms", "Euler, h = 10 ms"))
# 第一步：从精确解出发沿切线走一步，与精确解的差是局部截断误差
ax.annotate("", xy=(h * 1e3, w_ex(h)), xytext=(h * 1e3, xs[1]),
            arrowprops=dict(arrowstyle="<->", color=C["z"], lw=1.1, shrinkA=0, shrinkB=0))
ax.text(h * 1e3 + 1.2, (w_ex(h) + xs[1]) / 2, T("局部截断误差", "local truncation error"), color=C["z"], fontsize=9.5, va="center",
        bbox=box)
# 从第 3 步的“数值解”出发的那条精确解曲线
k = 3
t3 = tk[k]
tt = np.linspace(t3, 0.06, 100)
w_from = w_inf + (xs[k] - w_inf) * np.exp(-(tt - t3) / tau)
ax.plot(tt * 1e3, w_from, color=C["muted"], lw=0.9, ls="--")
ax.annotate(T("从 $\\omega_3$ 出发的精确解", "exact solution through $\\omega_3$"), xy=(52, w_from[-12]), xytext=(36, 268),
            color=C["muted"], fontsize=9, arrowprops=dict(arrowstyle="-", color=C["muted"], lw=0.7))
ax.annotate("", xy=(0.04 * 1e3, w_ex(0.04)), xytext=(0.04 * 1e3, xs[4]),
            arrowprops=dict(arrowstyle="<->", color=PURPLE, lw=1.1, shrinkA=0, shrinkB=0))
ax.annotate(T("全局误差 $e_4$", "global error $e_4$"), xy=(40, (w_ex(0.04) + xs[4]) / 2), xytext=(43, 165),
            color=PURPLE, fontsize=9.5, bbox=box, arrowprops=dict(arrowstyle="-", color=PURPLE, lw=0.7))
for i in range(1, 4):
    ax.text(tk[i] * 1e3 - 1.0, xs[i] + 8, f"$\\omega_{i}$", color=C["x"], fontsize=10, ha="right")
ax.set_xlabel(T("时间 t / ms", "time t / ms"))
ax.set_ylabel(T("转速 ω / (rad/s)", "speed ω / (rad/s)"))
ax.set_xlim(0, 62)
ax.set_ylim(0, 300)
ax.legend(loc="lower right", frameon=False, fontsize=9.5)
clean(ax)
figure(fig, "fig7_2_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 7.2.2
Jo, lc, wn2 = link_params()
x0 = np.array([math.pi / 2, 0.0])
ref = solve_ivp(pend_f(wn2), (0, 2.0), x0, method="DOP853", rtol=1e-13, atol=1e-13).y[:, -1]
hs = np.array([0.04, 0.02, 0.01, 0.005, 0.0025, 0.00125])
fig, ax = plt.subplots(figsize=(5.8, 4.0))
style_m = {"euler": (C["x"], "o", T("欧拉法", "Euler")), "symp": ("#e67e22", "v", T("辛欧拉法", "symplectic Euler")),
           "midpoint": (C["y"], "s", T("中点法", "midpoint")), "verlet": (PURPLE, "D", T("施特默-韦莱法", "Störmer–Verlet")),
           "rk4": (C["z"], "^", T("经典 RK4", "classical RK4"))}
for meth, (col, mk, lab) in style_m.items():
    es = [np.linalg.norm(run_pend(meth, wn2, x0, 2.0, h)[-1] - ref) for h in hs]
    ax.loglog(hs, es, marker=mk, color=col, lw=1.2, ms=4.5, label=lab)
for p, y0, lab in ((1, 0.6, "1"), (2, 2e-3, "2"), (4, 1e-8, "4")):
    hh = np.array([0.0025, 0.02])
    ax.loglog(hh, y0 * (hh / 0.0025) ** p, color=C["muted"], lw=0.8, ls=":")
    ax.text(0.021, y0 * (0.02 / 0.0025) ** p, T(f"斜率 {lab}", f"slope {lab}"), fontsize=9, color=C["muted"], va="center")
ax.set_xlabel(T("步长 h / s", "step size h / s"))
ax.set_ylabel(T("t = 2 s 时的误差", "error at t = 2 s"))
ax.grid(True, which="major", lw=0.3, alpha=0.5)
ax.legend(loc="lower right", frameon=False, fontsize=9)
ax.set_xlim(1e-3, 0.06)
clean(ax)
figure(fig, "fig7_2_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 7.2.3
fig, ax = plt.subplots(figsize=(5.8, 3.6))
ts = np.linspace(0, 0.32, 400)
ax.plot(ts * 1e3, w_ex(ts), color=C["ink"], lw=1.8, label=T("精确解", "exact solution"))
for h, col, mk in ((0.005, C["y"], "."), (0.030, C["z"], "o"), (0.045, C["x"], "s")):
    xs = run(euler, f_m, [0.0], 0.315 if h == 0.045 else 0.3, h, keep=True)[:, 0]
    tk = np.arange(len(xs)) * h
    ax.plot(tk * 1e3, xs, marker=mk, color=col, lw=1.0, ms=4, label=f"h = {h * 1e3:.0f} ms")
ax.axhline(w_inf, color=C["muted"], lw=0.6, ls="--")
ax.set_ylim(-250, 650)
ax.set_xlim(0, 320)
ax.set_xlabel(T("时间 t / ms", "time t / ms"))
ax.set_ylabel(T("转速 ω / (rad/s)", "speed ω / (rad/s)"))
ax.text(250, 570, T("h > 2τ：发散", "h > 2τ: diverges"), color=C["x"], fontsize=10, bbox=box)
ax.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0), frameon=False, fontsize=9)
clean(ax)
figure(fig, "fig7_2_3")
plt.close(fig)

# ---------------------------------------------------------------- 图 7.2.4
E0 = float(pend_energy(x0, wn2))
fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(12.0, 3.9), gridspec_kw=dict(width_ratios=[1, 1.3, 1.3], wspace=0.35))
xs = run_pend("euler", wn2, x0, 10.0, 0.02)
tt = np.arange(len(xs)) * 0.02
a1.plot(tt, pend_energy(xs, wn2) / E0, color=C["x"], lw=1.3)
a1.axhline(1, color=C["ink"], lw=0.8, ls="--")
a1.axhline(2, color=C["muted"], lw=0.6, ls=":")
a1.text(0.3, 2.08, T("高于此线：连杆越过顶点", "above: the link goes over the top"), fontsize=8.5, color=C["muted"])
a1.set_xlabel(T("时间 t / s", "time t / s"))
a1.set_ylabel(T("能量 E / E(0)", "energy E / E(0)"))
a1.set_title(T("(a) 欧拉法，h = 0.02 s", "(a) Euler, h = 0.02 s"), fontsize=10.5)
clean(a1)


def band(ax, t, y, col, lab, width=10.0):
    """快速振荡的曲线画成包络带：每 width 秒取最大值和最小值。"""
    n = int(round(width / (t[1] - t[0])))
    m = len(y) // n
    tb = t[:m * n].reshape(m, n).mean(axis=1)
    lo, hi = y[:m * n].reshape(m, n).min(axis=1), y[:m * n].reshape(m, n).max(axis=1)
    ax.fill_between(tb, lo, hi, color=col, alpha=0.3, lw=0, label=lab)
    ax.plot(tb, lo, color=col, lw=0.6)
    ax.plot(tb, hi, color=col, lw=0.6)


runs = {}
for meth, h in (("symp", 0.02), ("verlet", 0.02), ("rk4", 0.08), ("rk4", 0.02)):
    xs = run_pend(meth, wn2, x0, 1000.0, h)
    runs[(meth, h)] = (np.arange(len(xs)) * h, (pend_energy(xs, wn2) - E0) / E0 * 100)
band(a2, *runs[("symp", 0.02)], "#e67e22", T("辛欧拉法 h = 0.02 s（振荡的包络）", "symplectic Euler, h = 0.02 s (envelope)"))
a2.plot(*runs[("rk4", 0.08)], color=C["z"], lw=1.4, label=T("RK4 h = 0.08 s", "RK4, h = 0.08 s"))
a2.axhline(0, color=C["ink"], lw=0.6)
a2.set_ylim(-60, 10)
a2.set_xlabel(T("时间 t / s", "time t / s"))
a2.set_ylabel(T("能量的相对误差 / %", "relative energy error / %"))
a2.set_title(T("(b) 1000 s：辛欧拉法与 RK4", "(b) 1000 s: symplectic Euler and RK4"), fontsize=10.5)
a2.legend(loc="lower left", frameon=False, fontsize=8.5)
clean(a2)
band(a3, *runs[("verlet", 0.02)], PURPLE, T("施特默-韦莱法 h = 0.02 s（包络）", "Störmer–Verlet, h = 0.02 s (envelope)"))
a3.plot(*runs[("rk4", 0.02)], color=C["y"], lw=1.4, label=T("RK4 h = 0.02 s", "RK4, h = 0.02 s"))
a3.axhline(0, color=C["ink"], lw=0.6)
a3.set_ylim(-0.4, 0.1)
a3.set_xlabel(T("时间 t / s", "time t / s"))
a3.set_title(T("(c) 放大纵轴：韦莱法与 h = 0.02 s 的 RK4", "(c) enlarged: Verlet and RK4 with h = 0.02 s"), fontsize=10.5)
a3.legend(loc="lower left", frameon=False, fontsize=8.5)
clean(a3)
figure(fig, "fig7_2_4")
plt.close(fig)

# ---------------------------------------------------------------- 图 7.2.5
fig, axs = plt.subplots(1, 3, figsize=(10.0, 3.6), sharex=True, sharey=True)
ang = np.linspace(0, 2 * math.pi, 200)
c0 = np.array([0.6, 0.0])
disk = np.column_stack([c0[0] + 0.25 * np.cos(ang), c0[1] + 1.5 * np.sin(ang)])
h = 0.05
nstep = int(round(2.0 / h))


def area(P):
    x, y = P[:, 0], P[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


A0 = area(disk)
f = pend_f(wn2)
maps = (("euler", T("(a) 欧拉法", "(a) Euler"), C["x"]), ("symp", T("(b) 辛欧拉法", "(b) symplectic Euler"), "#e67e22"),
        ("exact", T("(c) 精确的流", "(c) the exact flow"), C["z"]))
thc = np.linspace(-math.pi, math.pi, 400)
omc = np.linspace(-11, 11, 400)
THc, OMc = np.meshgrid(thc, omc)
Ec = 0.5 * OMc ** 2 + wn2 * (1 - np.cos(THc))
for ax, (kind, title, col) in zip(axs, maps):
    ax.contour(THc, OMc, Ec, levels=np.linspace(0.2, 1.6, 6) * wn2, colors=[C["muted"]], linewidths=0.4, alpha=0.6)
    P = disk.copy()
    if kind == "exact":
        P = np.array([solve_ivp(f, (0, 2.0), p, method="DOP853", rtol=1e-11, atol=1e-11).y[:, -1] for p in P])
    else:
        for _ in range(nstep):
            P = np.array([euler(f, 0, p, h) if kind == "euler" else symp_euler(wn2, p, h) for p in P])
    ax.fill(disk[:, 0], disk[:, 1], color=C["muted"], alpha=0.35, lw=0)
    ax.fill(P[:, 0], P[:, 1], color=col, alpha=0.45, lw=0)
    ax.plot(P[:, 0], P[:, 1], color=col, lw=0.8)
    ax.set_title(title, fontsize=10.5)
    ax.text(-3.0, -10.4, T(f"面积之比 {area(P) / A0:.2f}", f"area ratio {area(P) / A0:.2f}"), fontsize=9.5, color=col, bbox=box)
    ax.set_xlabel(r"$\theta$ / rad")
    clean(ax)
axs[0].set_ylabel(r"$\dot\theta$ / (rad/s)")
axs[0].text(0.95, 2.0, T("出发时", "start"), fontsize=9, color=C["ink"])
axs[0].set_xlim(-3.2, 3.2)
axs[0].set_ylim(-11, 11)
figure(fig, "fig7_2_5")
plt.close(fig)

# ---------------------------------------------------------------- 图 7.2.6
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.0, 3.9), gridspec_kw=dict(wspace=0.3))
names = {"euler": (T("欧拉法（矩阵元素）", "Euler (matrix entries)"), C["x"], "o"),
         "lie": (T("李-欧拉法", "Lie–Euler"), "#e67e22", "v"),
         "mid": (T("李-中点法", "Lie midpoint"), C["y"], "s"),
         "rk4": (T("RK4（矩阵元素）", "RK4 (matrix entries)"), C["z"], "^"),
         "mag4": (T("四阶马格努斯法", "4th-order Magnus"), PURPLE, "D")}
hs = [0.04, 0.02, 0.01, 0.005, 0.0025]
for m_, (lab, col, mk) in names.items():
    es = [math.degrees(angle_between(lie_integrate(m_, 2.0, h), cone_R(2.0))) for h in hs]
    a1.loglog(hs, es, marker=mk, color=col, lw=1.2, ms=4.5, label=lab)
a1.set_xlabel(T("步长 h / s", "step size h / s"))
a1.set_ylabel(T("t = 2 s 时的姿态误差 / (°)", "attitude error at t = 2 s / (°)"))
a1.set_title(T("(a) 误差与步长", "(a) error versus step size"), fontsize=10.5)
a1.grid(True, which="major", lw=0.3, alpha=0.5)
a1.legend(loc="lower right", frameon=False, fontsize=8.5)
clean(a1)
h = 0.01
for m_ in ("euler", "rk4", "lie", "mag4"):
    lab, col, mk = names[m_]
    R = cone_R(0.0)
    tt, oo = [], []
    n = int(round(100.0 / h))
    for k in range(n):
        R = lie_step(m_, R, k * h, h)
        if (k + 1) % 50 == 0:
            tt.append((k + 1) * h)
            oo.append(max(orth(R), 1e-16))
        if m_ == "euler" and (k + 1) * h >= 20:
            break
    a2.semilogy(tt, oo, color=col, lw=1.3, label=lab)
a2.set_xlabel(T("时间 t / s", "time t / s"))
a2.set_ylabel(r"$\Vert R^{\rm T}R - I\Vert$")
a2.set_title(T("(b) 离开 SO(3) 的程度，h = 0.01 s", "(b) how far R leaves SO(3), h = 0.01 s"), fontsize=10.5)
a2.set_ylim(1e-16, 1e3)
a2.legend(loc="center right", frameon=False, fontsize=8.5)
clean(a2)
figure(fig, "fig7_2_6")
plt.close(fig)
