"""15.2 节的计算：

算例 15.2.1  不考虑地球自转、把地球看成均匀球：地面的 g = GM/R²。再算赤道上自转所需的向心加速度 ω²R，它占 g 的多少？
算例 15.2.2  正常重力公式（WGS 84 的索米利亚纳公式）给出海平面上 g 随纬度 φ 的变化（图 15.2.1）：
            g(φ) = g_e (1 + k sin²φ)/√(1 − e² sin²φ)，g_e = 9.780 325 335 9 m/s²，k = 0.001 931 852 652 41，e² = 0.006 694 379 990 13。
            求赤道、两极、哈尔滨（45.8°N）、北京（39.9°N）、广州（23.1°N）的 g。高度每升高 1 m，g 约减小 3.086×10⁻⁶ m/s²（自由空气梯度）。
算例 15.2.3  称重传感器在北京用砝码标定，搬到广州去称 50.000 kg 的物体，读数是多少？在北京 2000 m 高的山上呢？
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import GM_earth, R_earth, R_earth_mean, omega_earth
import _draw as d

g0 = GM_earth / R_earth_mean ** 2
ac = omega_earth ** 2 * R_earth
out(g0=g0, ac=ac, ac_frac=ac / 9.78, GM_e14=GM_earth / 1e14)

ge, kk, e2 = 9.7803253359, 0.00193185265241, 0.00669437999013
gphi = lambda phi: ge * (1 + kk * math.sin(math.radians(phi)) ** 2) / math.sqrt(1 - e2 * math.sin(math.radians(phi)) ** 2)
grad = 3.086e-6
out(ge=ge, kk=kk, e2=e2, grad_e6=grad * 1e6)
for name, phi in (("eq", 0.0), ("pole", 90.0), ("hrb", 45.8), ("bj", 39.9), ("gz", 23.1)):
    out(**{f"g_{name}": gphi(phi)})
out(pole_eq=gphi(90) - gphi(0), pole_eq_pct=(gphi(90) - gphi(0)) / gphi(0) * 100)

m = 50.000
out(m50=m)
read_gz = m * gphi(23.1) / gphi(39.9)
read_mt = m * (gphi(39.9) - grad * 2000) / gphi(39.9)
out(read_gz=read_gz, err_gz_g=abs(read_gz - m) * 1000, read_mt=read_mt, err_mt_g=abs(read_mt - m) * 1000, dg_2000=grad * 2000)

plt = style()
fig, ax = plt.subplots(figsize=(4.8, 2.9))
ph = np.linspace(0, 90, 181)
ax.plot(ph, [gphi(p) for p in ph], color=d.VA, lw=2)
for name, phi in ((T("广州", "Guangzhou"), 23.1), (T("北京", "Beijing"), 39.9), (T("哈尔滨", "Harbin"), 45.8)):
    ax.plot(phi, gphi(phi), "o", color=d.VR, ms=5); ax.text(phi + 1.5, gphi(phi) - 0.0012, name, fontsize=8.5)
ax.set_xlabel(T("纬度 φ / (°)", "latitude φ / (°)")); ax.set_ylabel(T("海平面上的 g / (m/s²)", "sea-level g / (m/s²)"))
ax.set_xlim(0, 90); d.spines(ax)
figure(fig, "fig15_2_1")
