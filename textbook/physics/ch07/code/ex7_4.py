"""7.4 节的计算：

算例 7.4.1  加速 AGV 车厢里挂着一个小吊牌。车以 a = 1.5 m/s² 加速时，吊牌偏离竖直多少度？反过来，读得偏角 5.0°，加速度多大？
电梯（正文说明）：质量 70 kg 的人站在体重秤上。电梯以 1.2 m/s² 向上加速、匀速、以 1.2 m/s² 向上减速时，秤的读数（视重）。
算例 7.4.2  转台：零件放在转台上离轴 r = 0.15 m 处，μ_s = 0.40。转速超过多少零件开始滑动？在转台上看，是什么力
            “把它甩出去”？（图 7.4.1）
生活中的例子  地球自转使“重力”不等于引力：赤道上离心加速度 ω²R 多大？使重力加速度小百分之几？纬度 30° 处铅垂线偏离指向地心
            的方向多少？
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g, R_earth
import _draw as d

# ---- 算例 7.4.1
a1 = 1.5
th1 = math.degrees(math.atan(a1 / g))
th_meas = 5.0
a_meas = g * math.tan(math.radians(th_meas))
out(a1=a1, th1=th1, th_meas=th_meas, a_meas=a_meas)

# ---- 电梯
m2, a2 = 70.0, 1.2
out(m2=m2, a2=a2, W=m2 * g, N_up=m2 * (g + a2), N_dn=m2 * (g - a2), up_pct=100 * a2 / g)

# ---- 算例 7.4.2
r3, mu3 = 0.15, 0.40
w3 = math.sqrt(mu3 * g / r3)
out(r3=r3, mu3=mu3, w3=w3, rpm3=w3 * 60 / (2 * math.pi))

# ---- 地球自转
wE = 2 * math.pi / 86164.0          # 恒星日
a_cf = wE ** 2 * R_earth
phi = math.radians(30.0)
dev = a_cf * math.sin(phi) * math.cos(phi) / g      # 小角近似，rad
out(wE=wE, a_cf=a_cf, cf_pct=100 * a_cf / g, dev_deg=math.degrees(dev), dev_arcmin=60 * math.degrees(dev))

plt = style()
fig, ax = plt.subplots(figsize=(5.0, 3.2))
rs = np.linspace(0.03, 0.40, 300)
for mu, col in ((0.25, d.MUTED), (0.40, d.VA), (0.60, d.VR)):
    ax.plot(rs, np.sqrt(mu * g / rs) * 60 / (2 * math.pi), color=col, lw=2, label=rf"$\mu_\mathrm{{s}}$ = {mu:.2f}")
ax.plot([r3], [w3 * 60 / (2 * math.pi)], "o", color=d.INK, ms=5)
ax.annotate(T("算例 7.4.2", "Example 7.4.2"), (r3, w3 * 60 / (2 * math.pi)), xytext=(r3 + 0.05, 95), fontsize=8.5,
            arrowprops=dict(arrowstyle="-", color=d.INK, lw=0.6))
ax.set_xlabel(T("零件离转轴的距离 r / m", "distance from the axis r / m"))
ax.set_ylabel(T("开始滑动的转速 / (r/min)", "speed at which it slides / (rev/min)"))
ax.set_ylim(0, 140); ax.legend(frameon=False, fontsize=8.5); d.spines(ax)
figure(fig, "fig7_4_1")
