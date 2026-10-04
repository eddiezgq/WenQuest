"""3.6 节的计算：

算例 3.6.1  小角度近似 sin θ ≈ θ、cos θ ≈ 1 − θ²/2、tan θ ≈ θ：误差多大？由泰勒展开的下一项估计 sin θ 的相对误差 ≈ θ²/6，
            求误差为 1% 时的 θ，并与精确计算比较（图 3.6.1）。
算例 3.6.2  (1 + x)ⁿ ≈ 1 + nx：GPS 卫星以 v ≈ 3.87 km/s 运行，相对论因子 γ = (1 − v²/c²)^(−1/2)。直接用计算机算 γ − 1 会丢掉
            有效数字；用 γ − 1 ≈ v²/(2c²) 既简单又准确。由此估计卫星钟每天慢多少（第 42 章，与 6.7 节的 7 μs 对照）。
算例 3.6.3  估一估：激光雷达的角度误差 0.1°，30 m 外的物体横向偏差约多少？弧长 ≈ rθ。
"""
import math

import numpy as np
from scipy.optimize import brentq

from bookout import T, figure, out, style
from constants import c
import _draw as d

# ---- 算例 3.6.1
rel = lambda th: (th - math.sin(th)) / math.sin(th)
th1 = brentq(lambda th: rel(th) - 0.01, 1e-3, 1.0)
th1_est = math.sqrt(6 * 0.01)
cos_err = lambda th: abs((1 - th * th / 2) - math.cos(th)) / math.cos(th)
tan_rel = lambda th: (math.tan(th) - th) / math.tan(th)
th10 = math.radians(10)
out(th1=math.degrees(th1), th1_est=math.degrees(th1_est), r10=100 * rel(th10), r10_est=100 * th10 ** 2 / 6,
    cos10=100 * cos_err(th10), tan10=100 * tan_rel(th10), r30=100 * rel(math.radians(30)))

# ---- 算例 3.6.2
v = 3.87e3
beta2 = (v / c) ** 2
g_direct = 1 / math.sqrt(1 - beta2) - 1                       # 双精度直接计算
g_taylor = beta2 / 2 + 3 * beta2 ** 2 / 8
from decimal import Decimal, getcontext
getcontext().prec = 40
b2 = Decimal(v) ** 2 / Decimal(c) ** 2
g_exact = float(1 / (1 - b2).sqrt() - 1)
day = 86400.0
out(v_kms=v / 1000, gm1=g_taylor, slow_us=g_taylor * day * 1e6, rel_direct=abs(g_direct - g_exact) / g_exact,
    rel_taylor=abs(beta2 / 2 - g_exact) / g_exact)

# ---- 算例 3.6.3
r, dth = 30.0, math.radians(0.1)
out(lat_cm=100 * r * dth, chord_diff=r * (2 * math.sin(dth / 2)) - r * dth)

plt = style()
# ---- 图 3.6.1：sin 的泰勒多项式与小角度近似的误差
fig, axs = plt.subplots(1, 2, figsize=(7.4, 3.0))
ax = axs[0]
x = np.linspace(0, math.pi, 300)
ax.plot(x, np.sin(x), color=d.INK, lw=2.2, label=r"$\sin\theta$")
ax.plot(x, x, color=d.VA, lw=1.4, label=r"$\theta$")
ax.plot(x, x - x ** 3 / 6, color=d.VB, lw=1.4, label=r"$\theta-\theta^3/6$")
ax.plot(x, x - x ** 3 / 6 + x ** 5 / 120, color=d.VR, lw=1.4, ls="--", label=r"$\theta-\theta^3/6+\theta^5/120$")
ax.set_ylim(-0.3, 1.6); ax.set_xlabel(T("θ / rad", "θ / rad")); ax.legend(frameon=False, fontsize=8); d.spines(ax)
ax = axs[1]
deg = np.linspace(0.5, 40, 200)
rad = np.radians(deg)
ax.plot(deg, 100 * (rad - np.sin(rad)) / np.sin(rad), color=d.VA, lw=1.8, label=r"$\sin\theta\approx\theta$")
ax.plot(deg, 100 * np.abs(1 - rad ** 2 / 2 - np.cos(rad)) / np.cos(rad), color=d.VB, lw=1.8, label=r"$\cos\theta\approx1-\theta^2/2$")
ax.plot(deg, 100 * (np.tan(rad) - rad) / np.tan(rad), color=d.VR, lw=1.8, label=r"$\tan\theta\approx\theta$")
ax.axhline(1, color=d.MUTED, lw=0.8, ls=":"); ax.text(1, 1.2, "1%", color=d.MUTED, fontsize=9)
ax.set_xlabel(T("θ / (°)", "θ / (°)")); ax.set_ylabel(T("相对误差 / %", "relative error / %")); ax.set_ylim(0, 10)
ax.legend(frameon=False, fontsize=8); d.spines(ax)
fig.tight_layout()
figure(fig, "fig3_6_1")
