"""4.5 节的计算：

算例 4.5.1  机械臂的夹爪在离箱底 1.20 m 处松开，一个零件自由下落。求落地时间和落地速度（不计空气阻力）。
算例 4.5.2  频闪照片测 g：频闪灯每秒闪 30 次，相机长时间曝光，一张照片上留下下落小球的一串像。从旁边的刻度尺读出
            每个像的位置（读数到 1 mm，误差在 ±1 mm 以内），用最小二乘拟合 y = y₀ + v₀t + ½gt²，求 g 及其不确定度
            （图 4.5.1）。第一个像不是从静止开始的，所以要拟合三个参数。
算例 4.5.3  什么时候可以不计空气阻力：直径 20 mm 的钢球与乒乓球（直径 40 mm、质量 2.7 g）从 1.20 m 高处落下，
            按二次方阻力 F = ½ρC_dAv²（C_d = 0.47）数值计算，比较落地时间与落地速度；终端速度 v_t = √(2mg/(ρC_dA))
            （图 4.5.2）。
"""
import math

import numpy as np
from scipy.integrate import solve_ivp

from bookout import T, figure, out, style
from constants import g
import _draw as d

# ---- 算例 4.5.1
H = 1.20
tf = math.sqrt(2 * H / g); vf = g * tf
assert abs(vf - math.sqrt(2 * g * H)) < 1e-12
out(H=H, tf=tf, vf=vf, v30=math.sqrt(2 * g * 30), v30k=3.6 * math.sqrt(2 * g * 30))

# ---- 算例 4.5.2：频闪照片（模拟数据，带种子，结果可复现）
rng = np.random.default_rng(45)
f, n = 30.0, 12
t = np.arange(n) / f
t_rel = 0.071                                           # 第一次闪光时小球已下落 0.071 s（学生不知道）
y_true = 0.5 * g * (t + t_rel) ** 2 - 0.5 * g * t_rel ** 2   # 以第一个像为原点，向下为正，m
y_read = np.round((y_true + rng.uniform(-0.0005, 0.0005, n)) * 1000) / 1000   # 读数误差 ±0.5 mm，再修约到 1 mm：总误差在 ±1 mm 以内
A = np.vstack([np.ones(n), t, 0.5 * t ** 2]).T
coef, res, *_ = np.linalg.lstsq(A, y_read, rcond=None)
r = y_read - A @ coef
s = math.sqrt(r @ r / (n - 3))
cov = s ** 2 * np.linalg.inv(A.T @ A)
g_fit, u_g = coef[2], math.sqrt(cov[2, 2])
out(f=f, n=n, y_list="、".join(f"{v * 1000:.0f}" for v in y_read), v0_fit=coef[1], g_fit=g_fit, u_g=u_g, U_g=2 * u_g,
    rel_g=100 * (g_fit - g) / g, s_mm=1000 * s, ylast_mm=1000 * y_read[-1])

# ---- 算例 4.5.3：空气阻力
rho, Cd = 1.20, 0.47
balls = {"steel": (7850 * math.pi / 6 * 0.020 ** 3, 0.020), "pp": (0.0027, 0.040)}


def fall(m, dia):
    k = 0.5 * rho * Cd * math.pi * dia ** 2 / 4 / m
    ev = lambda tt, y: y[0] - H; ev.terminal = True
    sol = solve_ivp(lambda tt, y: [y[1], g - k * y[1] * abs(y[1])], (0, 5), [0, 0], events=ev, max_step=1e-3, rtol=1e-10, atol=1e-12)
    return sol.t_events[0][0], sol.y_events[0][0][1], math.sqrt(g / k), sol
res = {k: fall(*v) for k, v in balls.items()}
out(m_steel_g=1000 * balls["steel"][0], vt_steel=res["steel"][2], vt_pp=res["pp"][2],
    t_steel=res["steel"][0], t_pp=res["pp"][0], v_steel=res["steel"][1], v_pp=res["pp"][1],
    dt_steel_pct=100 * (res["steel"][0] - tf) / tf, dt_pp_pct=100 * (res["pp"][0] - tf) / tf,
    dv_pp_pct=100 * (vf - res["pp"][1]) / vf)

plt = style()
# ---- 图 4.5.1：频闪照片与拟合
fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.6), gridspec_kw={"width_ratios": [0.7, 1.3]})
ax = axs[0]
for yv in y_read:
    ax.add_patch(plt.Circle((2, -yv * 100), 1.4, color=d.INK))
for k in range(0, 101, 5):
    ax.plot([6, 9 if k % 10 == 0 else 7.5], [-k, -k], color=d.MUTED, lw=0.8)
    if k % 20 == 0:
        ax.text(10, -k, f"{k}", fontsize=7, va="center", color=d.MUTED)
ax.plot([6, 6], [0, -100], color=d.MUTED, lw=0.8); ax.text(9, 4, "cm", fontsize=7.5, color=d.MUTED)
ax.set_xlim(-4, 16); ax.set_ylim(-102, 8); ax.set_aspect("equal"); ax.axis("off")
ax.set_title(T("频闪照片（示意）", "strobe photo (sketch)"), fontsize=9)
ax = axs[1]
ax.plot(t, y_read * 100, "o", color=d.VA, ms=5, label=T("读数", "readings"))
tt = np.linspace(0, t[-1], 200)
ax.plot(tt, (coef[0] + coef[1] * tt + 0.5 * coef[2] * tt ** 2) * 100, color=d.VR, lw=1.5, label=T("拟合", "fit"))
ax.set_xlabel("t / s"); ax.set_ylabel(T("下落距离 y / cm", "drop y / cm")); ax.legend(frameon=False, fontsize=8.5); d.spines(ax)
ax.text(0.02, 70, f"g = ({g_fit:.2f} ± {2 * u_g:.2f}) m/s²", fontsize=9, color=d.VR)
fig.tight_layout()
figure(fig, "fig4_5_1")

# ---- 图 4.5.2：空气阻力
fig, ax = plt.subplots(figsize=(4.8, 3.1))
tt = np.linspace(0, 1.6, 300)
ax.plot(tt, g * tt, color=d.MUTED, lw=1, ls="--", label=T("无空气阻力", "no drag"))
for key, col, name in (("steel", d.INK, T("钢球 d = 20 mm", "steel ball, d = 20 mm")), ("pp", d.VR, T("乒乓球", "table-tennis ball"))):
    m, dia = balls[key]
    k = 0.5 * rho * Cd * math.pi * dia ** 2 / 4 / m
    sol = solve_ivp(lambda q, y: [y[1], g - k * y[1] * abs(y[1])], (0, 1.6), [0, 0], t_eval=tt, rtol=1e-9)
    ax.plot(tt, sol.y[1], color=col, lw=2, label=name)
    ax.plot(res[key][0], res[key][1], "o", color=col, ms=5)
ax.axhline(res["pp"][2], color=d.VR, lw=0.8, ls=":"); ax.text(0.02, res["pp"][2] + 0.3, T("乒乓球的终端速度", "terminal speed (table-tennis)"), fontsize=8, color=d.VR)
ax.set_xlabel("t / s"); ax.set_ylabel("v / (m/s)"); ax.set_ylim(0, 16); ax.legend(frameon=False, fontsize=8, loc="upper left", bbox_to_anchor=(0, 0.88)); d.spines(ax)
ax.text(0.75, 2.0, T("圆点：从 1.2 m 高处落地", "dots: landing from 1.2 m"), fontsize=8, color=d.MUTED)
figure(fig, "fig4_5_2")
