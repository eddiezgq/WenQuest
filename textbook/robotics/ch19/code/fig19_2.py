"""19.2 节的示意图。

图 19.2.1：差速驱动的几何：两轮速度、车体中心的速度 v、角速度 ω、瞬心与转弯半径 R；车上各点的速度沿车轴线性分布。
图 19.2.2：(a) 轮速限制下 (v, ω) 的可行范围（菱形）与几种运动；(b) 两轮匀速转 2 s：精确的圆弧与欧拉法（步长 0.1 s）。
图 19.2.3：数字工厂的真实路线（ht-01 → cnc-l01-b）：(a) 车间平面上的折线与圆弧过渡；(b) 车速与两轮转速随时间的变化。
"""
import math

import numpy as np

from _fig19 import C, arrow, rect, wheel
from _mob import diff_cart, exp_se2, factory, profile, q_of, round_corners, seg_len, seg_point, step_euler, to_book
from bookout import T, figure, style

plt = style()
P = diff_cart()
r, b, wmax = P["r"], P["b"], P["wmax"]
O = (0.0, 0.0, 0.0)

# ---------------------------------------------------------------- 图 19.2.1
fig, ax = plt.subplots(figsize=(6.4, 6.2))
ax.set_aspect("equal")
ax.axis("off")
rect(ax, O, -0.02, 0, 0, P["length"], P["width"], C["body"], C["dark"], 0.8, 1)
for y in (b / 2, -b / 2):
    wheel(ax, O, 0, y, 0.0, r=r, width=0.03)
wheel(ax, O, -0.14, 0, 0.0, r=0.025, width=0.018, fc="#8a959b")
R = 0.45                                   # 示意：瞬心在左侧 0.45 m
k = 0.55                                   # 速度箭头的比例（1 m/s 画成 0.55 m）
om = 0.6
vR, vL, vC = om * (R + b / 2), om * (R - b / 2), om * R
ax.plot([0, 0], [-b / 2 - 0.05, R + 0.06], color=C["red"], lw=0.9, ls="--", zorder=2)
for y, vv, nm in ((-b / 2, vR, r"$r\omega_R$"), (b / 2, vL, r"$r\omega_L$"), (0, vC, "$v$")):
    arrow(ax, (0, y), (k * vv, y), C["green"] if y else C["blue"], 2.0)
    ax.text(k * vv + 0.012, y - 0.012, nm, color=C["green"] if y else C["blue"], fontsize=13)
ax.plot([0, k * vR], [R, -b / 2], color=C["muted"], lw=0.8, ls=":")
ax.plot([k * vR, 0], [-b / 2, -b / 2], color=C["muted"], lw=0.5)
ax.plot(0, R, "o", ms=8, mfc="white", mec=C["accent"], mew=2, zorder=6)
ax.text(0.02, R + 0.015, T("瞬心", "ICR"), color=C["accent"], fontsize=12)
ax.annotate("", xy=(-0.05, R), xytext=(-0.05, 0), arrowprops=dict(arrowstyle="<->", color=C["accent"], lw=1.0))
ax.text(-0.11, R / 2, "$R$", color=C["accent"], fontsize=13)
ax.annotate("", xy=(-0.2, b / 2), xytext=(-0.2, -b / 2), arrowprops=dict(arrowstyle="<->", color=C["ink"], lw=0.9))
ax.text(-0.235, -0.01, "$b$", fontsize=13)
t = np.linspace(-0.6, 0.6, 30)
ax.plot(0.07 * np.cos(t) + 0.0, 0.07 * np.sin(t), color=C["purple"], lw=1.2)
arrow(ax, (0.07 * math.cos(0.6), 0.07 * math.sin(0.6)), (0.07 * math.cos(0.75), 0.07 * math.sin(0.75)), C["purple"], 1.2, 9)
ax.text(0.075, 0.05, r"$\omega$", color=C["purple"], fontsize=13)
arrow(ax, (0.0, 0.0), (0.0, 0.0), C["ink"])
ax.plot(0, 0, "o", color=C["ink"], ms=3, zorder=6)
ax.text(-0.04, -0.035, "O", fontsize=11)
arrow(ax, (-0.28, -0.32), (-0.18, -0.32), C["x"], 1.2, 9)
arrow(ax, (-0.28, -0.32), (-0.28, -0.22), C["y"], 1.2, 9)
ax.text(-0.175, -0.335, "$x_b$", color=C["x"], fontsize=11)
ax.text(-0.305, -0.21, "$y_b$", color=C["y"], fontsize=11)
ax.text(-0.3, -0.4, T("车上各点的速度沿车轴线性分布，延长线交于瞬心", "speeds along the axle grow linearly; their tips line up with the ICR"),
        fontsize=9.5, color=C["muted"])
ax.text(0.3, -0.16, T("右轮", "right"), fontsize=9.5, color=C["muted"])
ax.text(0.3, 0.1, T("左轮", "left"), fontsize=9.5, color=C["muted"])
ax.set_xlim(-0.33, 0.55)
ax.set_ylim(-0.43, R + 0.1)
figure(fig, "fig19_2_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 19.2.2
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.6))
vm, omm = r * wmax, 2 * r * wmax / b
dia = np.array([[vm, 0], [0, omm], [-vm, 0], [0, -omm], [vm, 0]])
a1.fill(dia[:, 0], dia[:, 1], color=C["blue"], alpha=0.10)
a1.plot(dia[:, 0], dia[:, 1], color=C["blue"], lw=1.4)
a1.axhline(0, color=C["muted"], lw=0.6)
a1.axvline(0, color=C["muted"], lw=0.6)
rho = 0.5
vv = np.linspace(0, vm, 10)
a1.plot(vv, vv / rho, color=C["accent"], lw=1.0, ls="--")
a1.text(0.75, 2.25, T("ω = v/ρ，ρ = 0.5 m", "ω = v/ρ, ρ = 0.5 m"), color=C["accent"], fontsize=9)
v_wh = vm / (1 + b / (2 * rho))
marks = [((vm, 0), (0.55, -1.6), T("直行最快", "fastest straight")),
         ((0, omm), (0.08, 7.9), T("原地转最快", "fastest spin")),
         ((0.5, 1.0), (-0.98, 3.0), T("拐角，横向加速度限制", "corner, lateral-acceleration limit")),
         ((v_wh, v_wh / rho), (0.42, 4.4), T("拐角，轮速限制", "corner, wheel limit")),
         ((0.5, 0.5), (-0.98, 1.0), T("算例 19.2.1", "Example 19.2.1"))]
for (x, y), (tx, ty), s in marks:
    a1.plot(x, y, "o", color=C["red"], ms=5, zorder=5)
    a1.annotate(s, xy=(x, y), xytext=(tx, ty), fontsize=9, arrowprops=dict(arrowstyle="-", color=C["muted"], lw=0.6))
a1.set_xlabel(T("车速 v / (m/s)", "speed v / (m/s)"))
a1.set_ylabel(T("角速度 ω / (rad/s)", "turn rate ω / (rad/s)"))
a1.text(-0.95, -6.9, r"$|v| + \frac{b}{2}|\omega| \leq r\,\omega_{\max}$", fontsize=13, color=C["blue"])
a1.set_xlim(-1.1, 1.25)
a1.set_ylim(-8.4, 8.6)
a1.set_title(T("(a) 轮速限制下的可行范围", "(a) what the wheel-speed limit allows"), fontsize=10.5)
# (b)
a2.set_aspect("equal")
for (wR, wL), col in (((11.3, 8.7), C["blue"]), ((12.0, 4.0), C["purple"]), ((10.0, 10.0), C["green"]), ((6.0, 12.0), C["red"])):
    V = np.array([r * (wR - wL) / b, r * (wR + wL) / 2, 0.0])
    ts = np.linspace(0, 2, 200)
    pp = np.array([q_of(exp_se2(V, t))[:2] for t in ts])
    a2.plot(pp[:, 0], pp[:, 1], color=col, lw=1.6)
    lab = r"$\omega_R$ = %g, $\omega_L$ = %g" % (wR, wL)
    end = pp[-1]
    a2.plot(*end, "o", color=col, ms=4)
    off = {C["blue"]: (0.04, 0.04), C["purple"]: (-0.05, 0.08), C["green"]: (0.03, -0.1), C["red"]: (0.05, -0.05)}[col]
    a2.text(end[0] + off[0], end[1] + off[1], lab, color=col, fontsize=9)
qe = np.zeros(3)
E = [qe[:2].copy()]
V2 = np.array([0.5, 0.5, 0.0])
for _ in range(20):
    qe = step_euler(qe, V2, 0.1)
    E.append(qe[:2].copy())
E = np.array(E)
a2.plot(E[:, 0], E[:, 1], "o-", color=C["orange"], ms=2.5, lw=0.8)
a2.text(E[-1, 0] + 0.04, E[-1, 1] - 0.12, T("欧拉法，步长 0.1 s", "Euler, step 0.1 s"), color=C["orange"], fontsize=9)
a2.plot(0, 0, "s", color=C["ink"], ms=5)
a2.text(-0.32, 0.06, T("起点，车头朝 +x", "start, heading +x"), fontsize=9)
a2.set_xlim(-0.35, 2.0)
a2.set_ylim(-0.95, 1.0)
a2.set_xlabel("x / m")
a2.set_ylabel("y / m")
a2.set_title(T("(b) 两轮匀速转动 2 s：车体中心走圆弧", "(b) constant wheel speeds for 2 s: the centre runs on an arc"), fontsize=10.5)
fig.subplots_adjust(wspace=0.28)
figure(fig, "fig19_2_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 19.2.3
lay = factory()
W_f, D_f = lay.FLOOR
path_f = lay.route(lay.dock("ht-01"), lay.dock("cnc-l01-b"))
path = to_book(path_f, D_f)
segs = round_corners(path, 0.5)
pr = profile(segs, r * wmax, 0.5, 0.5)
fig = plt.figure(figsize=(11.0, 4.8))
a1 = fig.add_axes([0.03, 0.08, 0.47, 0.86])
a2 = fig.add_axes([0.57, 0.14, 0.41, 0.78])
a1.set_aspect("equal")
for y in lay.AISLES:
    a1.fill([4, 30, 30, 4], [D_f - y - 1, D_f - y - 1, D_f - y + 1, D_f - y + 1], color="#e6eaed", lw=0)
a1.fill([lay.CROSS_X - 1, lay.CROSS_X + 1, lay.CROSS_X + 1, lay.CROSS_X - 1],
        [D_f - lay.AISLES[1] - 1, D_f - lay.AISLES[1] - 1, D_f - lay.AISLES[0] + 1, D_f - lay.AISLES[0] + 1], color="#e6eaed", lw=0)
names = {"saw-01": T("带锯床", "saw"), "cnc-l01-a": T("数控车床 A", "lathe A"), "cnc-l01-b": T("数控车床 B", "lathe B"),
         "ht-01": T("热处理炉", "furnace"), "vmc-01": T("立式加工中心", "VMC"), "hmc-01": T("卧式加工中心", "HMC"),
         "hob-01": T("滚齿机", "hobber"), "key-01": T("键槽铣床", "keyway"), "grd-01": T("外圆磨床", "grinder")}
for u, (x, y, w, d) in lay.LAYOUT.items():
    if not (3 < x < 30):
        continue
    yb = D_f - y
    hl = u in ("ht-01", "cnc-l01-b")
    a1.fill([x - w / 2, x + w / 2, x + w / 2, x - w / 2], [yb - d / 2, yb - d / 2, yb + d / 2, yb + d / 2],
            color="#f3e2b3" if hl else "#cfd6db", ec=C["dark"], lw=0.6)
    if u in names:
        a1.text(x, yb, names[u], ha="center", va="center", fontsize=8)
pa = np.array(path)
a1.plot(pa[:, 0], pa[:, 1], color=C["muted"], lw=1.0, ls="--")
a1.plot(pr["xy"][:, 0], pr["xy"][:, 1], color=C["blue"], lw=1.8)
a1.plot(*pa[0], "o", color=C["green"], ms=6)
a1.plot(*pa[-1], "s", color=C["red"], ms=6)
a1.text(pa[0][0] + 0.4, pa[0][1] - 0.3, T("起点", "start"), color=C["green"], fontsize=9)
a1.text(pa[-1][0] + 0.4, pa[-1][1] - 0.3, T("终点", "goal"), color=C["red"], fontsize=9)
a1.text(8, 15.5, T("虚线：工厂仿真的折线\n实线：拐角用 ρ = 0.5 m 圆弧过渡", "dashed: the plant model's polyline\nsolid: corners rounded, ρ = 0.5 m"),
        fontsize=8.5, color=C["ink"])
a1.set_xlim(4, 30)
a1.set_ylim(4.3, 24.5)
a1.set_xlabel("x / m")
a1.set_ylabel("y / m")
a1.set_title(T("(a) 车间平面（y 轴向上）", "(a) workshop plan (y up)"), fontsize=10.5)
tt = np.r_[0.0, pr["t"], pr["T"]]
v = np.r_[0.0, pr["v"], 0.0]
kap = np.r_[0.0, pr["kap"], 0.0]
wR = (v + v * kap * b / 2) / r
wL = (v - v * kap * b / 2) / r
a2.plot(tt, wR, color=C["red"], lw=1.2, label=T("右轮", "right") + r" $\omega_R$")
a2.plot(tt, wL, color=C["green"], lw=1.2, label=T("左轮", "left") + r" $\omega_L$")
a2.set_ylabel(T("轮速 / (rad/s)", "wheel speed / (rad/s)"))
a2.set_xlabel(T("时间 t / s", "time t / s"))
a2.axhline(wmax, color=C["muted"], lw=0.7, ls=":")
a2.text(1, wmax + 0.4, T("轮速上限 20 rad/s", "wheel limit 20 rad/s"), fontsize=8.5, color=C["muted"])
a3 = a2.twinx()
a3.plot(tt, v, color=C["blue"], lw=1.6, label=T("车速 v", "speed v"))
a3.set_ylabel(T("车速 v / (m/s)", "speed v / (m/s)"), color=C["blue"])
a3.set_ylim(0, 1.6)
a2.set_ylim(0, 24)
h1, l1 = a2.get_legend_handles_labels()
h2, l2 = a3.get_legend_handles_labels()
a2.legend(h1 + h2, l1 + l2, loc="lower center", fontsize=8.5, ncol=3, frameon=False)
a2.set_title(T("(b) 速度曲线与两轮转速", "(b) speed profile and wheel speeds"), fontsize=10.5)
figure(fig, "fig19_2_3")
plt.close(fig)
