"""15.6 节的计算：

算例 15.6.1  月球和太阳在地球表面产生的潮汐加速度（最大值 2GMR/d³），两者之比；与 g 比较。
            图 15.6.1：月球在 +x 方向时，地球表面各处的潮汐加速度（引力减去地心处的引力）。
算例 15.6.2  GPS 卫星的时钟（轨道半径 26 560 km）：广义相对论（引力势不同）使它每天比地面的钟快多少？
            狭义相对论（运动）使它慢多少？合起来每天差多少微秒？相当于测距误差多少？
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import G, GM_earth, M_moon, M_sun, d_moon, AU, R_earth_mean, c, g_n
import _draw as d

R = R_earth_mean
am = 2 * G * M_moon * R / d_moon ** 3
asun = 2 * G * M_sun * R / AU ** 3
out(am_e6=am * 1e6, am_e7=am * 1e7, as_e7=asun * 1e7, ratio=asun / am, am_g=am / g_n * 1e7)

rg = 26560e3
gr = GM_earth / c ** 2 * (1 / R - 1 / rg)
v = math.sqrt(GM_earth / rg)
sr = v ** 2 / (2 * c ** 2)
day = 86400
out(gr_us=gr * day * 1e6, sr_us=sr * day * 1e6, net_us=(gr - sr) * day * 1e6, v_gps=v / 1000, range_km=(gr - sr) * day * c / 1000)

plt = style()
fig, ax = plt.subplots(figsize=(4.4, 3.4))
th = np.linspace(0, 2 * np.pi, 400)
ax.fill(np.cos(th), np.sin(th), color="#dfe8ef", lw=0); ax.plot(np.cos(th), np.sin(th), color=d.MUTED, lw=1)
# 潮汐加速度 ∝ (2x, −y)（x、y 以 R 为单位），箭头长度只示意方向和相对大小
for t_ in np.linspace(0, 2 * np.pi, 24, endpoint=False):
    x, y = math.cos(t_), math.sin(t_)
    ax.annotate("", xy=(x + 0.22 * 2 * x, y - 0.22 * y), xytext=(x, y), arrowprops=dict(arrowstyle="->", color=d.VR, lw=1.3))
tt = np.linspace(0, 2 * np.pi, 400); eps = 0.12
ax.plot((1 + eps * (3 * np.cos(tt) ** 2 - 1) / 2) * np.cos(tt) * 1.18, (1 + eps * (3 * np.cos(tt) ** 2 - 1) / 2) * np.sin(tt) * 1.18,
        color=d.VA, lw=1, ls="--")
ax.annotate("", xy=(2.25, 0), xytext=(1.85, 0), arrowprops=dict(arrowstyle="->", color=d.INK))
ax.text(1.8, 0.12, T("月球方向", "towards the Moon"), fontsize=8.5)
ax.text(-1.95, -1.6, T("虚线：海水的两个隆起（夸大）", "dashed: the two tidal bulges (exaggerated)"), fontsize=7.5, color=d.VA)
ax.set_aspect("equal"); ax.set_xlim(-2.0, 2.4); ax.set_ylim(-1.7, 1.7); ax.axis("off")
figure(fig, "fig15_6_1")
