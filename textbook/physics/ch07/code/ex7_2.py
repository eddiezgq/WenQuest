"""7.2 节的计算：

算例 7.2.1  洁净车间里的粉尘：直径 10 μm、密度 2.0×10³ kg/m³ 的颗粒在静止空气中沉降。用斯托克斯阻力 F = 6πηrv 求终端速度，
            核对雷诺数很小；它从 2 m 高处落到地面要多久？
算例 7.2.2  巡检无人机（质量 1.2 kg）在 60 m 高空失去动力，翻滚下落时有效的 C_dA ≈ 0.040 m²；带应急降落伞时
            C_dA ≈ 1.3 m²（伞面积约 1.0 m²，C_d ≈ 1.3）。按二次方阻力求两种情况的终端速度、下落时间和落地速度，
            与无空气阻力比较（图 7.2.1）。二次方阻力的解析解：v = v_t tanh(gt/v_t)，y = (v_t²/g) ln cosh(gt/v_t)。
估一估      乒乓球（2.7 g，直径 40 mm，C_d = 0.47）的终端速度；AGV（迎风 C_dA ≈ 0.50 m²）以 2.0 m/s 行驶时的空气阻力，
            与滚动阻力（算例 7.1.3，约 74 N）比较。
"""
import math

import numpy as np
from scipy.optimize import brentq

from bookout import T, figure, out, style
from constants import g
import _draw as d

rho_air, eta = 1.20, 1.8e-5                 # 空气密度 kg/m³，空气的黏度 Pa·s（20 °C）

# ---- 算例 7.2.1
r, rho_p, h1 = 5e-6, 2.0e3, 2.0
vt1 = 2 * r * r * (rho_p - rho_air) * g / (9 * eta)
Re1 = rho_air * vt1 * 2 * r / eta
tau1 = (rho_p * 4 / 3 * math.pi * r ** 3) / (6 * math.pi * eta * r)
out(d_um=2e6 * r, vt1_mm=1000 * vt1, Re1=Re1, tau1_ms=1000 * tau1, t_fall_min=h1 / vt1 / 60)

# ---- 算例 7.2.2
m, H = 1.2, 60.0
cases = {"tumble": 0.040, "chute": 1.3}
res = {}
for k, CdA in cases.items():
    vt = math.sqrt(2 * m * g / (rho_air * CdA))
    T_ = brentq(lambda t: vt ** 2 / g * math.log(math.cosh(g * t / vt)) - H, 1e-6, 200)
    res[k] = (vt, T_, vt * math.tanh(g * T_ / vt))
t0 = math.sqrt(2 * H / g)
out(m=m, H=H, vt_tumble=res["tumble"][0], T_tumble=res["tumble"][1], v_tumble=res["tumble"][2],
    vt_chute=res["chute"][0], T_chute=res["chute"][1], v_chute=res["chute"][2], T_vac=t0, v_vac=g * t0,
    Re_chute=rho_air * res["chute"][0] * 1.13 / eta, t95_chute=res["chute"][0] / g * math.atanh(0.95))

# ---- 估一估
mpp, dpp = 2.7e-3, 0.040
App = math.pi * dpp ** 2 / 4
vt_pp = math.sqrt(2 * mpp * g / (rho_air * 0.47 * App))
out(vt_pp=vt_pp, Re_pp=rho_air * vt_pp * dpp / eta, F_agv=0.5 * rho_air * 0.50 * 2.0 ** 2)

plt = style()
fig, ax = plt.subplots(figsize=(5.0, 3.2))
tt = np.linspace(0, 20, 600)
ax.plot(tt[tt <= t0], g * tt[tt <= t0], color=d.MUTED, lw=1.2, ls="--", label=T("无空气阻力", "no drag"))
for k, col, name in (("tumble", d.VR, T("失去动力翻滚下落", "tumbling")), ("chute", d.VA, T("打开降落伞", "parachute"))):
    vt, T_, vland = res[k]
    q = tt[tt <= T_]
    ax.plot(q, vt * np.tanh(g * q / vt), color=col, lw=2, label=name)
    ax.plot(T_, vland, "o", color=col)
    ax.axhline(vt, color=col, lw=0.8, ls=":")
ax.text(12, res["tumble"][0] + 1.0, T("终端速度", "terminal speed"), color=d.VR, fontsize=8.5)
ax.set_xlabel("t / s"); ax.set_ylabel(T("下落速度 / (m/s)", "falling speed / (m/s)")); ax.set_ylim(0, 40); ax.legend(frameon=False, fontsize=8.5)
ax.text(8.5, 7, T("圆点：落地（60 m）", "dots: reaching the ground (60 m)"), fontsize=8, color=d.MUTED); d.spines(ax)
figure(fig, "fig7_2_1")
