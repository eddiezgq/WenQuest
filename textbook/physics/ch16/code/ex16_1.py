"""16.1 节的计算：

算例 16.1.1  液压举升机：小活塞直径 20 mm，大活塞直径 200 mm，大活塞上的平台连同汽车共 1800 kg。油的压强多大？
            压小活塞要用多大的力？小活塞压下 100 mm，汽车升高多少？（不计活塞重量、摩擦和油的压缩）
算例 16.1.2  气动夹爪：双作用气缸缸径 16 mm、活塞杆直径 6 mm，气源表压 0.50 MPa。夹紧（推出）和张开（缩回）的理论力各多大？
            表压从 0.2 MPa 调到 0.7 MPa，夹紧力怎样变化（图 16.1.1）？
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d

g = 9.81
d1, d2, M = 0.020, 0.200, 1800.0
A1, A2 = math.pi * d1 ** 2 / 4, math.pi * d2 ** 2 / 4
p = M * g / A2
F1 = p * A1
out(p_MPa=p / 1e6, F1=F1, ratio=A2 / A1, lift_mm=100 * A1 / A2, W=M * g)

D, dr, pg = 0.016, 0.006, 0.50e6
Ap, Ar = math.pi * D ** 2 / 4, math.pi * (D ** 2 - dr ** 2) / 4
out(F_push=pg * Ap, F_pull=pg * Ar, Ap_mm2=Ap * 1e6, Ar_mm2=Ar * 1e6)

plt = style()
fig, ax = plt.subplots(figsize=(4.8, 2.9))
pp = np.linspace(0.2, 0.7, 50)
ax.plot(pp, pp * 1e6 * Ap, color=d.VR, lw=2, label=T("推出（夹紧）", "extend (clamp)"))
ax.plot(pp, pp * 1e6 * Ar, color=d.VA, lw=2, ls="--", label=T("缩回（张开）", "retract (open)"))
ax.set_xlabel(T("气源表压 / MPa", "supply gauge pressure / MPa")); ax.set_ylabel(T("理论输出力 / N", "theoretical force / N"))
ax.legend(frameon=False, fontsize=8.5); d.spines(ax)
figure(fig, "fig16_1_1")
