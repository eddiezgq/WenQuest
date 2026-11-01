"""11.6 节的计算：

算例 11.6.1  传送带受料：碎料从料斗以 20 kg/s 竖直落到以 1.5 m/s 匀速运行的水平传送带上。维持匀速，传送带要多加多大的力、
            多大的功率？料获得的动能每秒多少？其余的到哪里去了？
算例 11.6.2  火箭方程：喷气速度 u = 3000 m/s。质量比 m₀/m_f = 10 时的速度增量；单级入轨需要 Δv ≈ 9.4 km/s，
            质量比要多大；两级各取质量比 4 时的总速度增量（图 11.6.1）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d

q, v = 20.0, 1.5
F = q * v
P = F * v
out(q=q, v=v, F=F, P=P, Kdot=0.5 * q * v * v, heat=P - 0.5 * q * v * v)

u = 3000.0
dv10 = u * math.log(10)
R_orbit = math.exp(9400 / u)
dv2 = u * (math.log(4) + math.log(4))
out(u=u, dv10=dv10, R_orbit=R_orbit, dv2=dv2, dv_one16=u * math.log(16))

# 数值核对：每一小步喷出 dm，按动量守恒更新速度
m, vv, mf = 10.0, 0.0, 1.0
dm = 1e-5
while m > mf:
    vv += u * dm / m                                              # (m)v = (m − dm)(v + dv) + dm (v − u)  ⇒  m dv ≈ u dm
    m -= dm
assert abs(vv - dv10) < 1e-2 * dv10
out(dv10_num=vv)

plt = style()
fig, ax = plt.subplots(figsize=(4.8, 3.0))
R = np.linspace(1, 30, 400)
ax.plot(R, np.log(R), color=d.VA, lw=2)
ax.axhline(9400 / u, color=d.VR, lw=1, ls="--"); ax.text(2.0, 9400 / u + 0.12, T("单级入轨约需 Δv/u ≈ 3.1", "single stage to orbit: Δv/u ≈ 3.1"), fontsize=8.5, color=d.VR)
ax.plot(10, math.log(10), "o", color=d.VA); ax.text(10.6, math.log(10) - 0.25, T("质量比 10", "mass ratio 10"), fontsize=8.5)
ax.set_xlabel(T(r"质量比 $m_0/m_\mathrm{f}$", r"mass ratio $m_0/m_\mathrm{f}$")); ax.set_ylabel("Δv / u"); ax.set_xlim(1, 30); ax.set_ylim(0, 3.6); d.spines(ax)
figure(fig, "fig11_6_1")
