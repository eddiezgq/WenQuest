"""34.5 节的计算：

算例 34.5.1  电机铁心的涡流损耗：0.5 mm 与 0.35 mm 硅钢片的比较（薄片近似 P_V = π² f² B² d²/(6ρ)，
             片厚不超过透入深度时误差不到 1%），以及损耗随片厚的变化（图 34.5.1）；
算例 34.5.2  感应淬火的透入深度 δ = √(2ρ/(ω μ))：频率越高，加热层越薄（图 34.5.2）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import mu_0
import _draw as d

f, Bm = 50.0, 1.5               # 频率 Hz、磁感应强度幅值 T
rho_si = 4.7e-7                 # 硅钢（约 3% 硅）的电阻率，Ω·m
dens = 7650.0                   # 硅钢的密度，kg/m³


def loss(dthick, rho=rho_si):
    """薄片的经典涡流损耗，W/m³（片厚 d 不超过透入深度时误差不到 1%）。"""
    return math.pi ** 2 * f ** 2 * Bm ** 2 * dthick ** 2 / (6 * rho)


P05 = loss(0.5e-3)
P035 = loss(0.35e-3)
ratio = P05 / P035
mur_si = 4000.0                 # 硅钢的相对磁导率（取典型值）
d_si = math.sqrt(2 * rho_si / (2 * math.pi * f * mu_0 * mur_si))       # 50 Hz 时的透入深度

# 感应淬火：钢在居里点以下 μr 约 100，以上 μr = 1；电阻率取 2×10⁻⁷ Ω·m（冷态）与 1.1×10⁻⁶ Ω·m（热态）
def delta(fr, rho, mur):
    return math.sqrt(2 * rho / (2 * math.pi * fr * mu_0 * mur))


d_cold_10k = delta(1e4, 2e-7, 100)
d_hot_10k = delta(1e4, 1.1e-6, 1)
d_hot_200k = delta(2e5, 1.1e-6, 1)
d_hot_1k = delta(1e3, 1.1e-6, 1)

out(P05=P05, P05_kg=P05 / dens, P035_kg=P035 / dens, ratio=ratio, d_si_mm=d_si * 1000,
    d_cold_10k_mm=d_cold_10k * 1000, d_hot_10k_mm=d_hot_10k * 1000, d_hot_200k_mm=d_hot_200k * 1000, d_hot_1k_mm=d_hot_1k * 1000)

plt = style()
fig, ax = plt.subplots(figsize=(5.4, 3.0))
dd = np.linspace(0.1, 0.7, 200)
ax.plot(dd, [loss(x * 1e-3) / dens for x in dd], color=d.CURR, lw=2)
ax.plot([0.5], [P05 / dens], "o", color=d.FORCE)
ax.plot([0.35], [P035 / dens], "o", color=d.FIELD)
ax.annotate(T("常用 0.5 mm 硅钢片", "usual 0.5 mm laminations"), (0.5, P05 / dens), xytext=(0.15, 1.1), fontsize=9,
            arrowprops=dict(arrowstyle="->", color=d.MUTED))
ax.set_xlabel(T("片厚 $d$ / mm", "lamination thickness $d$ / mm"))
ax.set_ylabel(T("涡流损耗 / (W/kg)", "eddy loss / (W/kg)"))
ax.set_xlim(0, 0.7); ax.set_ylim(0, 1.4); d.spines(ax)
ax.text(0.36, 0.2, r"$P_V=\pi^2 f^2 B_\mathrm{m}^2 d^2/(6\rho)$", fontsize=10, color=d.INK)
figure(fig, "fig34_5_1")

fig, ax = plt.subplots(figsize=(5.4, 3.0))
ff = np.logspace(2, 6, 200)
ax.loglog(ff, [delta(x, 1.1e-6, 1) * 1000 for x in ff], color=d.FORCE, lw=2, label=T("热态（居里点以上）", "hot (above Curie point)"))
ax.loglog(ff, [delta(x, 2e-7, 100) * 1000 for x in ff], color=d.FIELD, lw=2, ls="--", label=T("冷态", "cold"))
ax.set_xlabel(T("频率 $f$ / Hz", "frequency $f$ / Hz")); ax.set_ylabel(T("透入深度 $\\delta$ / mm", "penetration depth $\\delta$ / mm"))
ax.legend(frameon=False); d.spines(ax)
figure(fig, "fig34_5_2")
