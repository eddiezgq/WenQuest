"""6.1 节的计算：

算例 6.1.1  推杆与导流板同时作用在零件上，求合力（矢量相加，图 6.1.1）；
算例 6.1.2  氢原子中电子与质子之间的电力与引力之比（常数取自 conventions/constants.py）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import G, a_0, e, epsilon_0, m_e, m_p
import _draw as d

# ---- 算例 6.1.2：电力与引力
r = a_0                                            # 电子到质子的距离取玻尔半径，m
F_e = e ** 2 / (4 * math.pi * epsilon_0 * r ** 2)  # 库仑力，N（第 26 章）
F_g = G * m_e * m_p / r ** 2                       # 万有引力，N（第 15 章）
ratio = F_e / F_g
assert abs(ratio / (e ** 2 / (4 * math.pi * epsilon_0 * G * m_e * m_p)) - 1) < 1e-12   # 比值与距离无关

# ---- 算例 6.1.1：两个力的合力
F1 = np.array([30.0, 0.0])                                        # 推杆，N，沿 x
F2 = 20.0 * np.array([math.cos(math.radians(120)), math.sin(math.radians(120))])   # 导流板，N，与 x 轴成 120°
F = F1 + F2
mag = float(np.linalg.norm(F))
ang = math.degrees(math.atan2(F[1], F[0]))
# 余弦定理核对：|F|² = F1² + F2² + 2 F1 F2 cos120°
assert abs(mag ** 2 - (30 ** 2 + 20 ** 2 + 2 * 30 * 20 * math.cos(math.radians(120)))) < 1e-9

out(r_pm=r * 1e12, F_e=F_e, F_g=F_g, ratio=ratio, ratio_exp=math.floor(math.log10(ratio)),
    F2x=F2[0], F2y=F2[1], Fx=F[0], Fy=F[1], F=mag, ang=ang)

# ---- 图 6.1.1：平行四边形法则
plt = style()
fig, ax = plt.subplots(figsize=(5.2, 3.4))
s = 0.06                                          # 1 N 画成 0.06 个单位
ax.add_patch(plt.Rectangle((-0.35, -0.25), 0.5, 0.5, fc=d.CRATE, ec=d.INK, lw=1.2, zorder=3))
d.arrow(ax, 0, 0, F1[0] * s, 0, d.FORCE, r"$\boldsymbol{F}_1$", off=(0.12, -0.12))
d.arrow(ax, 0, 0, F2[0] * s, F2[1] * s, d.FORCE, r"$\boldsymbol{F}_2$", off=(-0.15, 0.08))
ax.plot([F1[0] * s, F[0] * s], [0, F[1] * s], color=d.MUTED, ls="--", lw=1)
ax.plot([F2[0] * s, F[0] * s], [F2[1] * s, F[1] * s], color=d.MUTED, ls="--", lw=1)
d.arrow(ax, 0, 0, F[0] * s, F[1] * s, "#1d6fb8", r"$\boldsymbol{F}=\boldsymbol{F}_1+\boldsymbol{F}_2$", off=(0.55, 0.12), lw=2.8)
ax.add_patch(plt.matplotlib.patches.Arc((0, 0), 0.9, 0.9, theta1=0, theta2=120, color=d.MUTED, lw=1))
ax.text(0.18, 0.5, "120°", fontsize=10, color=d.MUTED)
ax.text(-0.1, -0.45, T("零件", "part"), ha="center", fontsize=10, color=d.INK)
ax.set_xlim(-1.0, 2.4); ax.set_ylim(-0.6, 1.4)
d.clean(ax)
figure(fig, "fig6_1_1")
