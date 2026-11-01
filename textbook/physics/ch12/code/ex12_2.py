"""12.2 节的计算：

算例 12.2.1  同样两个 1.0 kg 的小球装在一根轻杆上绕杆中点转动：两球离轴各 0.10 m，或各 0.40 m。转动惯量各多少？
            用 0.50 N·m 的力矩从静止加速，转到 1 圈各要多久（图 12.2.1）？
算例 12.2.2  飞轮储能：钢制实心圆盘 50 kg、半径 0.30 m，以 3000 r/min 转动，储存多少能量？转速降到一半时放出多少？
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d

m, tau = 1.0, 0.50
res = {}
for tag, r in (("near", 0.10), ("far", 0.40)):
    J = 2 * m * r * r
    al = tau / J
    t1 = math.sqrt(2 * 2 * math.pi / al)
    res[tag] = (J, al, t1)
    out(**{f"r_{tag}": r, f"J_{tag}": J, f"al_{tag}": al, f"t1_{tag}": t1})
out(ratio_J=res["far"][0] / res["near"][0], ratio_t=res["far"][2] / res["near"][2])

M, R, n = 50.0, 0.30, 3000.0
J = 0.5 * M * R * R
w = n * 2 * math.pi / 60
E = 0.5 * J * w * w
out(Mf=M, Rf=R, Jf=J, wf=w, Ef_kJ=E / 1e3, Ef_Wh=E / 3600, Erel_kJ=0.75 * E / 1e3, v_rim=w * R)

plt = style()
fig, ax = plt.subplots(figsize=(4.8, 2.9))
tt = np.linspace(0, 4.5, 300)
for tag, col, lab in (("near", d.VA, T("球离轴 0.10 m", "balls 0.10 m from axis")), ("far", d.VR, T("球离轴 0.40 m", "balls 0.40 m from axis"))):
    J, al, t1 = res[tag]
    ax.plot(tt, np.minimum(0.5 * al * tt ** 2 / (2 * math.pi), 3), color=col, lw=2, label=lab)
    ax.plot(t1, 1, "o", color=col)
ax.axhline(1, color=d.MUTED, lw=0.6, ls=":")
ax.set_xlabel(T("时间 / s", "time / s")); ax.set_ylabel(T("转过的圈数", "turns completed")); ax.set_ylim(0, 3); ax.set_xlim(0, 4.5)
ax.legend(frameon=False, fontsize=8.5); d.spines(ax)
figure(fig, "fig12_2_1")
