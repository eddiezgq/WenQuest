"""1.1 节的计算：

算例 1.1.1  龙门搬运机器人吊着工件，绳长 1.5 m：按单摆模型（质点、轻绳、小摆角、无空气阻力）估算摆动周期；
            摆角为 10°、30°、60° 时，小摆角近似的误差各有多大（精确周期用完全椭圆积分计算，图 1.1.1）。
"""
import math

import numpy as np
from scipy.integrate import quad
from scipy.special import ellipk

from bookout import T, figure, out, style
from constants import g
import _draw as d

L = 1.5
T0 = 2 * math.pi * math.sqrt(L / g)                    # 小摆角近似


def T_exact(theta0_deg):
    k = math.sin(math.radians(theta0_deg) / 2)
    return 4 * math.sqrt(L / g) * ellipk(k * k)        # scipy 的 ellipk 以 m = k² 为参数


# 用数值积分 T = 4√(L/g) ∫₀^{π/2} dφ/√(1 − k² sin²φ) 核对
k30 = math.sin(math.radians(30) / 2)
assert abs(T_exact(30) - 4 * math.sqrt(L / g) * quad(lambda p: 1 / math.sqrt(1 - k30 ** 2 * math.sin(p) ** 2), 0, math.pi / 2)[0]) < 1e-12
err = {a: 100 * (T_exact(a) / T0 - 1) for a in (10, 30, 60)}

from scipy.optimize import brentq
ang = lambda pct: brentq(lambda a: 100 * (T_exact(a) / T0 - 1) - pct, 1, 120)   # 误差恰为 pct% 的摆角
out(L=L, T0=T0, T10=T_exact(10), T30=T_exact(30), T60=T_exact(60), e10=err[10], e30=err[30], e60=err[60],
    a1=ang(1), a10=ang(10))

plt = style()
fig, ax = plt.subplots(figsize=(5.0, 3.0))
th = np.linspace(0.5, 90, 300)
ax.plot(th, [100 * (T_exact(a) / T0 - 1) for a in th], color=d.FIT, lw=2)
for a in (10, 30, 60):
    ax.plot([a], [err[a]], "o", color=d.INK)
    ax.annotate(f"{err[a]:.2g}%", (a, err[a]), xytext=(a - 9, err[a] + 1.8), fontsize=9)
ax.axhline(1, color=d.MUTED, ls=":", lw=1)
ax.text(72, 1.4, T("误差 1%", "1% error"), fontsize=9, color=d.MUTED)
ax.set_xlabel(T("摆角 $\\theta_0$ / (°)", "amplitude $\\theta_0$ / (°)"))
ax.set_ylabel(T("小摆角近似的误差 / %", "error of the small-angle formula / %"))
ax.set_xlim(0, 90); ax.set_ylim(0, 19); d.spines(ax)
# 小图：0–40° 放大，带网格，便于读出 0.5%、1% 对应的摆角（习题 1.1.2）
ins = ax.inset_axes([0.08, 0.42, 0.42, 0.52])
ti = np.linspace(0.5, 40, 200)
ins.plot(ti, [100 * (T_exact(a) / T0 - 1) for a in ti], color=d.FIT, lw=1.6)
ins.set_xlim(0, 40); ins.set_ylim(0, 3); ins.set_xticks(range(0, 41, 10)); ins.set_yticks([0, 0.5, 1, 1.5, 2, 2.5, 3])
ins.set_xticks(range(0, 41, 5), minor=True); ins.grid(True, which="both", lw=0.4, color="#cccccc")
ins.tick_params(labelsize=7); ins.set_title(T("0–40° 放大", "zoom: 0–40°"), fontsize=8)
figure(fig, "fig1_1_1")
