"""15.4 节的计算：

算例 15.4.1  八大行星的轨道半长轴 a（天文单位）和公转周期 T（年）（常用值），检验开普勒第三定律 T² ∝ a³（图 15.4.1）。
算例 15.4.2  由地球绕太阳的公转（a = 1 AU，T = 365.256 d）求太阳的质量；由月球绕地球（a = 3.844×10⁸ m，T = 27.32 d）求地球的质量。
算例 15.4.3  哈雷彗星：近日点 0.586 AU，远日点 35.1 AU。周期多少年？近日点、远日点的速率之比是多少？
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import G, AU, GM_sun, d_moon
import _draw as d

planets = [("水星", "Mercury", 0.387, 0.241), ("金星", "Venus", 0.723, 0.615), ("地球", "Earth", 1.000, 1.000),
           ("火星", "Mars", 1.524, 1.881), ("木星", "Jupiter", 5.203, 11.86), ("土星", "Saturn", 9.537, 29.46),
           ("天王星", "Uranus", 19.19, 84.01), ("海王星", "Neptune", 30.07, 164.8)]
ratios = [Tp ** 2 / a ** 3 for _, _, a, Tp in planets]
out(rmin=min(ratios), rmax=max(ratios), r_jup=ratios[4], r_nep=ratios[7])
assert max(abs(x - 1) for x in ratios) < 0.01

yr = 365.256 * 86400
out(yr_d=365.256, dmoon_e8=d_moon / 1e8, Tmoon_d=27.32)
Ms = 4 * math.pi ** 2 * AU ** 3 / (G * yr ** 2)
Me = 4 * math.pi ** 2 * d_moon ** 3 / (G * (27.32 * 86400) ** 2)
out(Ms_e30=Ms / 1e30, Me_e24=Me / 1e24, GMs_err=abs(G * Ms - GM_sun) / GM_sun)

rp, ra = 0.586, 35.1
a = (rp + ra) / 2
out(a_h=a, T_h=a ** 1.5, e_h=(ra - rp) / (ra + rp), vratio=ra / rp)

plt = style()
fig, ax = plt.subplots(figsize=(4.8, 3.0))
aa = np.array([p[2] for p in planets]); TT = np.array([p[3] for p in planets])
ax.loglog(aa, TT, "o", color=d.DATA, ms=5)
xs = np.logspace(-0.6, 1.6, 50); ax.loglog(xs, xs ** 1.5, color=d.FIT, lw=1.2, label=r"$T = a^{3/2}$")
for zh, en, a_, T_ in planets:
    ax.text(a_ * 1.12, T_ * 0.72, T(zh, en), fontsize=7.5)
ax.set_xlabel(T("半长轴 a / AU", "semi-major axis a / AU")); ax.set_ylabel(T("周期 T / 年", "period T / yr"))
ax.legend(frameon=False, fontsize=9, loc="upper left"); d.spines(ax)
figure(fig, "fig15_4_1")
