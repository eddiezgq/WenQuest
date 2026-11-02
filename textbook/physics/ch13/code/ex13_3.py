"""13.3 节的计算：

算例 13.3.1  转椅：人和转椅绕竖直轴的转动惯量 1.2 kg·m²，两手各握 2.5 kg 的哑铃（看成质点），平伸时离轴 0.80 m，
            以 0.50 r/s 转动。把哑铃收到离轴 0.15 m。转速、动能怎样变？（图 13.3.1，转轴摩擦不计）
算例 13.3.2  离合器：电机转子（J₁ = 0.020 kg·m²，300 rad/s）通过摩擦离合器与静止的负载盘（J₂ = 0.060 kg·m²）接合。
            接合后共同的角速度多大？损失了多少动能？
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d

J0, md, ro, ri, n0 = 1.2, 2.5, 0.80, 0.15, 0.50
Jc = lambda r: J0 + 2 * md * r * r
Jo, Ji = Jc(ro), Jc(ri)
n1 = n0 * Jo / Ji
Ko = 0.5 * Jo * (2 * math.pi * n0) ** 2
Ki = 0.5 * Ji * (2 * math.pi * n1) ** 2
out(J0=J0, md=md, ro=ro, ri=ri, n0=n0, Jo=Jo, Ji=Ji, n1=n1, Ko=Ko, Ki=Ki, Wc=Ki - Ko, ratioK=Ki / Ko, Lc=Jo * 2 * math.pi * n0)

J1, w1, J2 = 0.020, 300.0, 0.060
wc = J1 * w1 / (J1 + J2)
Kb, Ka = 0.5 * J1 * w1 ** 2, 0.5 * (J1 + J2) * wc ** 2
out(J1=J1, w1=w1, J2=J2, wc=wc, Kb=Kb, Ka=Ka, dK=Kb - Ka, frac=(Kb - Ka) / Kb)

plt = style()
fig, ax = plt.subplots(figsize=(4.8, 2.9))
r = np.linspace(0.10, 0.85, 200)
ax.plot(r, n0 * Jo / Jc(r), color=d.VA, lw=2, label=T("转速 / (r/s)", "spin rate / (r/s)"))
ax.plot(r, 0.5 * Jo ** 2 * (2 * math.pi * n0) ** 2 / Jc(r) / Ko, color=d.VR, lw=2, ls="--", label=T("动能 / 平伸时的动能", "KE / KE arms out"))
ax.plot([ro, ri], [n0, n1], "o", color=d.VA, ms=5)
ax.set_xlabel(T("哑铃离轴的距离 r / m", "dumbbell distance from axis r / m")); ax.set_ylabel(T("转速；动能之比", "spin rate; KE ratio"))
ax.set_xlim(0.1, 0.85); ax.set_ylim(0, 3.6); ax.legend(frameon=False, fontsize=8.5); d.spines(ax)
figure(fig, "fig13_3_1")

