"""34.1 节的计算：

算例 34.1.1  方形线圈中的磁场在 0.1 s 内由 0 均匀增加到 0.5 T，感应电动势；
算例 34.1.2  一块钕铁硼磁铁沿轴线匀速穿过线圈：磁通量与感应电动势随时间的变化（图 34.1.2），
             解析式与数值求导核对；
图 34.1.1    磁铁的磁感线穿过线圈（磁偶极子的磁感线 r = C sin²θ）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import mu_0
import _draw as d

# ---- 算例 34.1.1
N1, side, B0, B1, dt = 100, 0.05, 0.0, 0.5, 0.1
A1 = side ** 2
emf1 = N1 * A1 * (B1 - B0) / dt

# ---- 算例 34.1.2：磁偶极子沿轴线穿过半径为 a 的圆线圈
Br = 1.3                                   # 钕铁硼（N42 级）的剩磁，T
D, Hm = 0.010, 0.010                       # 圆柱磁铁的直径与高度，m
Vm = math.pi * (D / 2) ** 2 * Hm
m = Br * Vm / mu_0                         # 磁矩，A·m²（均匀磁化：M = Br/μ0）
a, N, v = 0.010, 200, 0.5                  # 线圈半径 m、匝数、磁铁速度 m/s


def flux(z):
    """磁偶极子在轴线上距离 z 处，通过半径 a 的圆面的磁通量（精确式）。"""
    return mu_0 * m * a ** 2 / (2 * (a ** 2 + z ** 2) ** 1.5)


def emf(z, v):
    """ε = −N dΦ/dt，z = z(t) 为磁铁到线圈平面的有向距离，dz/dt = v。"""
    return N * 1.5 * mu_0 * m * a ** 2 * z * v / (a ** 2 + z ** 2) ** 2.5


t = np.linspace(-0.12, 0.12, 4801)          # 磁铁在 t = 0 时穿过线圈平面
z = v * t
Phi = flux(z)
eps = emf(z, v)
eps_num = -N * np.gradient(Phi, t)          # 数值求导核对
assert np.max(np.abs(eps_num - eps)) < 1e-3 * np.max(np.abs(eps))
z_peak = a / 2                              # dε/dz = 0 处
eps_peak = emf(-z_peak, v)                  # 磁铁靠近时（z < 0）的峰值
assert abs(abs(eps_peak) - np.max(np.abs(eps))) < 1e-3 * abs(eps_peak)
Phi_max = flux(0.0)

out(emf1=emf1, A1_cm2=A1 * 1e4, m=m, Vm_cm3=Vm * 1e6, a_cm=a * 100, N=N, v=v,
    Phi_max=Phi_max, NPhi_max=N * Phi_max, eps_peak=abs(eps_peak), z_peak_mm=z_peak * 1000,
    dt_pass_ms=2 * a / v * 1000)

plt = style()
# ---- 图 34.1.1：磁感线穿过线圈
fig, ax = plt.subplots(figsize=(6.2, 3.6))
for C in (0.25, 0.4, 0.6, 0.9, 1.4, 2.2, 3.5, 5.5, 9.0):
    th = np.linspace(0.02, math.pi - 0.02, 2000)
    r = C * np.sin(th) ** 2
    x, y = r * np.cos(th), r * np.sin(th)
    for s in (1, -1):
        ax.plot(x, s * y, color=d.FIELD, lw=1, alpha=0.75)
        if C <= 0.9:                     # 磁感线方向：磁铁外从 N 极（右）回到 S 极（左）
            ax.annotate("", xy=(-0.03, s * C), xytext=(0.03, s * C),
                        arrowprops=dict(arrowstyle="-|>", color=d.FIELD, lw=1, mutation_scale=10))
d.magnet(ax, 0, 0, w=0.36, h=0.14)
# 线圈（侧视为一个竖直的椭圆），在 x = 0.6 处；靠近轴线的磁感线从中穿过
from matplotlib.patches import Ellipse
ax.add_patch(Ellipse((0.6, 0), 0.1, 0.5, fc="none", ec=d.CURR, lw=3, zorder=4))
ax.text(0.6, 0.33, T("线圈", "coil"), ha="center", fontsize=10, color=d.CURR,
        bbox=dict(fc="white", ec="none", pad=1))
d.arrow(ax, 0.28, -0.62, 0.35, 0, d.INK, r"$\boldsymbol{v}$", off=(0.08, 0))
ax.text(1.55, 0.95, T("磁感线", "field lines"), fontsize=10, color=d.FIELD)
ax.set_xlim(-1.6, 1.9); ax.set_ylim(-1.05, 1.05)
d.clean(ax)
figure(fig, "fig34_1_1")

# ---- 图 34.1.2：Φ(t) 与 ε(t)
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(5.8, 4.2), sharex=True)
ax1.plot(t * 1000, N * Phi * 1e3, color=d.FIELD, lw=2)
ax1.set_ylabel(T("$N\\Phi$ / mWb", "$N\\Phi$ / mWb"))
ax2.plot(t * 1000, eps * 1000, color=d.CURR, lw=2)
ax2.axhline(0, color=d.MUTED, lw=0.8)
ax2.set_ylabel(T("$\\mathcal{E}$ / mV", "$\\mathcal{E}$ / mV"))
ax2.set_xlabel(T("时间 $t$ / ms（$t$ = 0 时磁铁穿过线圈平面）", "time $t$ / ms (magnet crosses the coil plane at $t$ = 0)"))
ax2.annotate(T("靠近：Φ 增大", "approaching: Φ grows"), (-20, eps_peak * 1000 * 0.92), fontsize=9, color=d.INK, ha="right")
ax2.annotate(T("离开：Φ 减小", "leaving: Φ falls"), (20, -eps_peak * 1000 * 0.92), fontsize=9, color=d.INK)
for ax in (ax1, ax2):
    d.spines(ax)
ax2.set_xlim(-120, 120)
fig.tight_layout()
figure(fig, "fig34_1_2")
