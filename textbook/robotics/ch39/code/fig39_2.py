"""39.2 节的示意图。

图 39.2.1：(a) 惠斯通电桥（schemdraw 画电路）；(b) 单臂、半桥、全桥的输出与应变的关系（5 V 激励，K = 2）。
图 39.2.2：三运放仪表放大器。
"""
import io

import matplotlib
import numpy as np
import schemdraw
import schemdraw.elements as elm

from _meas import V_EX, bridge_full, bridge_half, bridge_quarter
from bookout import COLORS as C, figure, style

plt = style()
schemdraw.config(fontsize=12, lw=1.4, font="Noto Sans CJK SC")


def schem_to_ax(d, ax):
    """把 schemdraw 图画进 matplotlib 的一个子图。"""
    d.draw(canvas=ax, show=False)
    ax.set_aspect("equal")
    ax.axis("off")


# ---------------------------------------------------------------- 图 39.2.1
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 3.9), gridspec_kw={"width_ratios": [1.0, 1.25]})
with schemdraw.Drawing(show=False) as d:
    d.config(unit=2.2)
    W, H = 5.0, 4.4                      # 电桥宽、高
    d.add(elm.SourceV().at((0, 0)).to((0, H)))
    d.add(elm.Label().at((-1.0, H / 2)).label("$V_{ex}$"))
    d.add(elm.Line().at((0, H)).to((W, H)))
    d.add(elm.Line().at((0, 0)).to((W, 0)))
    d.add(elm.Resistor().at((2, H)).to((2, H / 2)).label("$R_a$", loc="bot"))
    d.add(elm.Resistor().at((2, H / 2)).to((2, 0)).label("$R_b$", loc="bot"))
    d.add(elm.Resistor().at((W, H)).to((W, H / 2)).label("$R_c$", loc="top"))
    d.add(elm.Resistor().at((W, H / 2)).to((W, 0)).label("$R_d$", loc="top"))
    d.add(elm.Ground().at((0, 0)))
    d.add(elm.Dot().at((2, H / 2)).label("$V_m$", loc="left"))
    d.add(elm.Dot().at((W, H / 2)).label("$V_p$", loc="right"))
    d.add(elm.Gap().at((2, H / 2)).to((W, H / 2)).label(["−", "$V_o$", "+"]))
    schem_to_ax(d, a1)
a1.set_title("(a) 惠斯通电桥", fontsize=11)

eps = np.linspace(0, 1500e-6, 200)
a2.plot(eps * 1e6, bridge_full(eps) * 1e3, color=C["z"], lw=2, label="全桥 $V_{ex}K\\varepsilon$")
a2.plot(eps * 1e6, bridge_half(eps) * 1e3, color=C["y"], lw=2, label="半桥 $V_{ex}K\\varepsilon/2$")
a2.plot(eps * 1e6, bridge_quarter(eps) * 1e3, color=C["x"], lw=2, label="单臂电桥（精确）")
a2.plot(eps * 1e6, V_EX * 2 * eps / 4 * 1e3, color=C["x"], lw=1, ls="--", label="单臂电桥（线性近似）")
a2.set_xlabel("应变 ε / µε")
a2.set_ylabel("电桥输出 $V_o$ / mV")
a2.legend(fontsize=8.5, frameon=False)
for s in ("top", "right"):
    a2.spines[s].set_visible(False)
ins = a2.inset_axes([0.62, 0.12, 0.34, 0.3])
e2 = np.linspace(0, 1500e-6, 50)
ins.plot(e2 * 1e6, (V_EX * 2 * e2 / 4 - bridge_quarter(e2)) * 1e6, color=C["x"], lw=1.2)
ins.set_title("单臂：近似 − 精确 / µV", fontsize=7.5)
ins.tick_params(labelsize=7)
a2.set_title("(b) 三种接法的输出（5 V 激励，K = 2）", fontsize=11)
fig.tight_layout()
figure(fig, "fig39_2_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 39.2.2
fig, ax = plt.subplots(figsize=(8.4, 4.8))


def P(a):
    return (float(a[0]), float(a[1]))


with schemdraw.Drawing(show=False) as d:
    d.config(unit=1.6)
    o1 = d.add(elm.Opamp(leads=True).right().flip().at((0, 5.3)).anchor("out").label("$A_1$", loc="center", ofst=(-0.35, 0)))
    o2 = d.add(elm.Opamp(leads=True).right().at((0, 0.5)).anchor("out").label("$A_2$", loc="center", ofst=(-0.35, 0)))
    n1, n2, p1, p2, q1, q2 = P(o1.in1), P(o2.in1), P(o1.in2), P(o2.in2), P(o1.out), P(o2.out)
    d.add(elm.Line().at(p1).to((p1[0] - 1.2, p1[1])).label("$V_m$", loc="left"))
    d.add(elm.Line().at(p2).to((p2[0] - 1.2, p2[1])).label("$V_p$", loc="left"))
    xr = n1[0] - 0.4
    d.add(elm.Line().at(n1).to((xr, n1[1])))
    d.add(elm.Line().at(n2).to((xr, n2[1])))
    d.add(elm.Resistor().at((xr, n1[1])).to((xr, n2[1])).label("$R_g$", loc="bot"))
    y1, y2 = n1[1] - 0.7, n2[1] + 0.7
    d.add(elm.Line().at((xr, n1[1])).to((xr, y1)))
    d.add(elm.Resistor().at((xr, y1)).to((q1[0], y1)).label("R", loc="bot"))
    d.add(elm.Line().at((q1[0], y1)).to(q1))
    d.add(elm.Line().at((xr, n2[1])).to((xr, y2)))
    d.add(elm.Resistor().at((xr, y2)).to((q2[0], y2)).label("R"))
    d.add(elm.Line().at((q2[0], y2)).to(q2))
    o3 = d.add(elm.Opamp(leads=True).right().at((q1[0] + 5.2, (q1[1] + q2[1]) / 2)).anchor("out").label("$A_3$", loc="center", ofst=(-0.35, 0)))
    m3, p3, q3 = P(o3.in1), P(o3.in2), P(o3.out)
    xa = m3[0] - 0.8
    d.add(elm.Resistor().at(q1).to((xa, q1[1])).label("$R_1$"))
    d.add(elm.Line().at((xa, q1[1])).to((xa, m3[1])))
    d.add(elm.Line().at((xa, m3[1])).to(m3))
    d.add(elm.Resistor().at(q2).to((xa, q2[1])).label("$R_1$", loc="bot"))
    d.add(elm.Line().at((xa, q2[1])).to((xa, p3[1])))
    d.add(elm.Line().at((xa, p3[1])).to(p3))
    d.add(elm.Resistor().at((xa, q2[1])).to((xa, q2[1] - 1.6)).label("$R_1$", loc="bot"))
    d.add(elm.Ground().at((xa, q2[1] - 1.6)))
    d.add(elm.Line().at(m3).to((m3[0], m3[1] + 1.0)))
    d.add(elm.Resistor().at((m3[0], m3[1] + 1.0)).to((q3[0], m3[1] + 1.0)).label("$R_1$"))
    d.add(elm.Line().at((q3[0], m3[1] + 1.0)).to(q3))
    d.add(elm.Line().at(q3).to((q3[0] + 0.8, q3[1])).label("$V_{out}$", loc="right"))
    for q in ((xr, n1[1]), (xr, n2[1]), (xa, q2[1])):
        d.add(elm.Dot().at(q))
    schem_to_ax(d, ax)
ax.text(0.0, -0.06, "输入级：$V_{o2} - V_{o1} = (V_p - V_m)(1 + 2R/R_g)$，共模电压不被放大；差分级：输出两个输入之差", transform=ax.transAxes, fontsize=9)
figure(fig, "fig39_2_2")
plt.close(fig)
