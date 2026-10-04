"""3.1 节的计算：

算例 3.1.1  AGV 从静止起步，加速度 0.50 m/s²，位置 x(t) = 0.25 t²（m，t 的单位为 s）。求 t = 2 s 前后不同时间间隔内的
            平均速度，看它们怎样逼近瞬时速度 1.00 m/s（表 3.1.1、图 3.1.1：割线变成切线）。
算例 3.1.2  编码器读数有分辨率：AGV 车轮编码器换算到车身位移，每个脉冲 0.1 mm，位置读数被量化到 0.1 mm。
            用前向差分 [x(t+h) − x(t)]/h 和中心差分 [x(t+h) − x(t−h)]/(2h) 估计 t = 2 s 的速度，看误差怎样随 h 变化：
            h 太大，割线与切线差得远（截断误差）；h 太小，量化误差被放大（舍入误差）。找出最好的 h（图 3.1.2）。
            为了让截断误差看得见，这里改用一段非匀加速的运动 x(t) = 0.25 t² + 0.02 t³。
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d

# ---- 算例 3.1.1
x = lambda t: 0.25 * t ** 2
t0 = 2.0
rows = []
for dt in (1.0, 0.5, 0.1, 0.01, 0.001):
    vbar = (x(t0 + dt) - x(t0)) / dt
    rows.append((dt, x(t0 + dt) - x(t0), vbar))
v_exact = 0.5 * t0
assert abs(rows[-1][2] - v_exact) < 1e-3
out(table="；".join(f"Δt = {r[0]:g} s 时，Δx = {r[1]:.6g} m，平均速度 {r[2]:.4f} m/s" for r in rows),
    v1=rows[0][2], v2=rows[1][2], v3=rows[2][2], v4=rows[3][2], v5=rows[4][2], v_exact=v_exact)

# ---- 算例 3.1.2：数值求导的两种误差
q = 1e-4                                                     # 位置分辨率 0.1 mm
xf = lambda t: 0.25 * t ** 2 + 0.02 * t ** 3
vtrue = 0.5 * t0 + 0.06 * t0 ** 2
quant = lambda v: np.round(v / q) * q
hs = np.logspace(-4, 0, 41)
# 量化误差的大小取决于读数恰好落在刻度的什么位置，带有偶然性：在 t0 附近取 400 个起点求均方根误差
rng = np.random.default_rng(31)
ts = t0 + rng.uniform(0, 0.01, 400)
vt = 0.5 * ts + 0.06 * ts ** 2
err_f = np.array([np.sqrt(np.mean(((quant(xf(ts + h)) - quant(xf(ts))) / h - vt) ** 2)) for h in hs])
err_c = np.array([np.sqrt(np.mean(((quant(xf(ts + h)) - quant(xf(ts - h))) / (2 * h) - vt) ** 2)) for h in hs])
# 理论估计：前向差分截断误差 ≈ |x''| h / 2，中心差分 ≈ |x'''| h² / 6；舍入误差 ≈ q / h（前向）、q / (2h)（中心）
x2 = 0.5 + 0.12 * t0
x3 = 0.12
h_f = math.sqrt(2 * q / x2)                                  # 让 x'' h / 2 与 q / h 相等
h_c = (6 * q / (2 * x3)) ** (1 / 3)
emin_f, emin_c = x2 * h_f / 2 + q / h_f, x3 * h_c ** 2 / 6 + q / (2 * h_c)
ib = int(np.argmin(err_f)); ic = int(np.argmin(err_c))
out(q_mm=q * 1000, vtrue=vtrue, x2=x2, h_f=h_f, h_c=h_c, emin_f=emin_f, emin_c=emin_c,
    e_f_big=float(err_f[-1]), e_c_big=float(err_c[-1]), e_f_small=float(err_f[0]),
    hbest_f=float(hs[ib]), ebest_f=float(err_f[ib]), hbest_c=float(hs[ic]), ebest_c=float(err_c[ic]))

plt = style()
# ---- 图 3.1.1：割线变成切线
fig, axs = plt.subplots(1, 2, figsize=(7.4, 3.1), gridspec_kw={"width_ratios": [1.15, 1]})
ax = axs[0]
tt = np.linspace(0, 3.2, 200)
ax.plot(tt, x(tt), color=d.INK, lw=2)
cols = ["#9fb8d9", "#6f97c9", d.VA]
for c, dt in zip(cols, (1.0, 0.5, 0.1)):   # 与表 3.1.1 的 Δt 相同
    k = (x(t0 + dt) - x(t0)) / dt
    ax.plot([0.6, 3.2], [x(t0) + k * (0.6 - t0), x(t0) + k * (3.2 - t0)], color=c, lw=1.2)
    ax.plot([t0 + dt], [x(t0 + dt)], "o", color=c, ms=4)
ax.plot([0.6, 3.2], [x(t0) + v_exact * (0.6 - t0), x(t0) + v_exact * (3.2 - t0)], color=d.VR, lw=2, ls="--")
ax.plot([t0], [x(t0)], "o", color=d.VR, ms=6)
ax.text(2.55, 0.55, T("切线：斜率 = 瞬时速度", "tangent: slope = instantaneous velocity"), color=d.VR, fontsize=8.5, ha="center")
ax.text(1.0, 2.2, T("割线：斜率 = 平均速度", "secants: slope = average velocity"), color=d.VA, fontsize=8.5)
ax.set_xlim(0, 3.2); ax.set_ylim(0, 2.6); ax.set_xlabel("t / s"); ax.set_ylabel("x / m"); d.spines(ax)
ax = axs[1]
dts = np.array([1.0, 0.5, 0.1, 0.01, 0.001])                # 与表 3.1.1 相同
ax.plot(dts, [(x(t0 + h) - x(t0)) / h for h in dts], "o-", color=d.VA)
ax.axhline(v_exact, color=d.VR, ls="--", lw=1.2)
ax.text(0.5, v_exact + 0.01, T("瞬时速度 1.00 m/s", "instantaneous 1.00 m/s"), color=d.VR, fontsize=8.5, ha="left", va="bottom")
ax.set_xscale("log"); ax.invert_xaxis(); ax.set_xlabel(T("时间间隔 Δt / s", "interval Δt / s")); ax.set_ylabel(T("平均速度 / (m/s)", "average velocity / (m/s)"))
d.spines(ax)
fig.tight_layout()
figure(fig, "fig3_1_1")

# ---- 图 3.1.2：数值求导的误差随步长的变化
fig, ax = plt.subplots(figsize=(5.2, 3.4))
ax.loglog(hs, err_f, "o", ms=3, color=d.VA, label=T("前向差分", "forward difference"))
ax.loglog(hs, err_c, "s", ms=3, color=d.VB, label=T("中心差分", "central difference"))
ax.loglog(hs, x2 * hs / 2 + q / (math.sqrt(6) * hs), color=d.VA, lw=1, alpha=0.7, ls="--")
ax.loglog(hs, x3 * hs ** 2 / 6 + q / (2 * math.sqrt(6) * hs), color=d.VB, lw=1, alpha=0.7, ls="--")
ax.text(2e-4, 1.2, T("h 小：量化误差被放大", "small h: quantisation amplified"), fontsize=8.5, color=d.MUTED)
ax.text(0.06, 2e-5, T("h 大：割线偏离切线", "large h: secant leaves tangent"), fontsize=8.5, color=d.MUTED)
ax.set_xlabel(T("步长 h / s", "step h / s")); ax.set_ylabel(T("速度误差 / (m/s)", "velocity error / (m/s)"))
ax.set_ylim(1e-5, 5); ax.legend(fontsize=8.5, frameon=False, loc="upper center"); d.spines(ax)
figure(fig, "fig3_1_2")
