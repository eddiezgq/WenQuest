"""12.7 节的计算：

算例 12.7.1  实心球、实心圆柱、薄圆筒（圆环）和光滑滑块（不转）从 30° 的斜面顶端由静止释放，沿斜面走 2.0 m（滚动不滑）。
            加速度、所用时间、到底时平动动能与转动动能之比（图 12.7.1）。
算例 12.7.2  不打滑的条件：斜面倾角 θ 时，纯滚动需要的静摩擦因数至少多大？μ_s = 0.30 时，三种物体各能在多陡的斜面上纯滚动？
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d

th, L = math.radians(30.0), 2.0
shapes = [("ball", 2 / 5), ("cyl", 1 / 2), ("hoop", 1.0), ("block", 0.0)]
for tag, k in shapes:
    a = g * math.sin(th) / (1 + k)
    t = math.sqrt(2 * L / a)
    out(**{f"a_{tag}": a, f"t_{tag}": t, f"rot_{tag}": k / (1 + k), f"v_{tag}": a * t})
mu = 0.30
for tag, k in shapes[:3]:
    mu_min = math.tan(th) * k / (1 + k)
    th_max = math.degrees(math.atan(mu * (1 + k) / k))
    out(**{f"mumin_{tag}": mu_min, f"thmax_{tag}": th_max})
out(mu=mu)

plt = style()
fig, ax = plt.subplots(figsize=(4.8, 2.9))
cols = {"ball": d.VR, "cyl": d.VA, "hoop": d.VB, "block": d.MUTED}
names = {"ball": T("实心球", "solid sphere"), "cyl": T("实心圆柱", "solid cylinder"), "hoop": T("薄圆筒", "thin hoop"), "block": T("光滑滑块（不转）", "frictionless block")}
tt = np.linspace(0, 1.4, 200)
for tag, k in shapes:
    a = g * math.sin(th) / (1 + k)
    ax.plot(tt, np.minimum(0.5 * a * tt ** 2, L), color=cols[tag], lw=2, ls="--" if tag == "block" else "-", label=names[tag])
ax.axhline(L, color=d.MUTED, lw=0.6, ls=":")
ax.set_xlabel(T("时间 / s", "time / s")); ax.set_ylabel(T("沿斜面走过的距离 / m", "distance down the incline / m"))
ax.set_xlim(0, 1.4); ax.set_ylim(0, 2.2); ax.legend(frameon=False, fontsize=8, loc="upper left"); d.spines(ax)
figure(fig, "fig12_7_1")
