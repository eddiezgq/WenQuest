"""4.1 节：导线的电阻与电容。

算例 4.1.1  电机控制芯片里横跨芯片的时钟线长 3 mm。比较 SKY130 局部互连层（li1）和五层金属各取最小线宽时，
            整条线的电阻、电容和 RC 乘积；电容分“单独一条线”和“两侧都有最小间距的邻线”两种情况。
算例 4.1.2  met1 线宽加倍、加到 4 倍时，电阻、电容和 RC 怎样变化。
图 4.1.1    (a) SKY130 金属层的高度与厚度（按比例）；(b) 各层最小线宽时每毫米的电阻和电容。
"""
import numpy as np

from bookout import T, figure, out, style
from mos import P, WIRES, wire_c, wire_cc, wire_r
import _draw as d

L = P["problems"]["p41"]["L_um"]
layers = ["li1", "met1", "met2", "met3", "met4", "met5"]
rows = {}
for l in layers:
    q = WIRES[l]
    w = q["wmin"]
    R = wire_r(l, w) * L
    C = wire_c(l, w) * L
    Cn = wire_c(l, w, q["smin"]) * L
    rows[l] = (R, C, Cn)
    out(**{f"{l}_w": w, f"{l}_s": q["smin"], f"{l}_rsq": q["Rsq"], f"{l}_R": R, f"{l}_Rk": R / 1e3, f"{l}_C": C * 1e15,
           f"{l}_Cn": Cn * 1e15, f"{l}_RC": R * C * 1e12, f"{l}_RCn": R * Cn * 1e12, f"{l}_t": q["t"],
           f"{l}_carea": q["Carea"], f"{l}_cfr": q["Cfringe"]})
out(L_mm=L / 1000, rc_ratio_li_m1=rows["li1"][0] * rows["li1"][1] / (rows["met1"][0] * rows["met1"][1]),
    rc_ratio_m1_m5=rows["met1"][0] * rows["met1"][1] / (rows["met5"][0] * rows["met5"][1]))
# 面积电容与边缘电容所占比例（met1 最小线宽）
q1 = WIRES["met1"]
area_part = q1["Carea"] * q1["wmin"]
out(m1_area_aF=area_part, m1_fringe_aF=2 * q1["Cfringe"], m1_fringe_pct=2 * q1["Cfringe"] / (area_part + 2 * q1["Cfringe"]) * 100,
    m1_cc_aF=wire_cc("met1", q1["smin"]) * 1e18, m1_cn_pct=(rows["met1"][2] / rows["met1"][1] - 1) * 100)

# 算例 4.1.2：met1 加宽
w0 = q1["wmin"]
for k in (1, 2, 4):
    R = wire_r("met1", k * w0) * L
    C = wire_c("met1", k * w0) * L
    out(**{f"w{k}_R": R, f"w{k}_C": C * 1e15, f"w{k}_RC": R * C * 1e12})

# 图 4.1.1
plt = style()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.2, 3.8), gridspec_kw={"width_ratios": [0.8, 1.3]})
cols = {"li1": "#8e6c8a", "met1": d.NMOS, "met2": "#3a9bd5", "met3": d.MEAN, "met4": "#5fb37f", "met5": d.LOAD}
for i, l in enumerate(layers):
    q = WIRES[l]
    a1.add_patch(__import__("matplotlib").patches.Rectangle((0.15 + 0.12 * (i % 2), q["z"]), 0.6, q["t"], color=cols[l], alpha=0.85))
    a1.text(0.95, q["z"] + q["t"] / 2, f"{l}  t = {q['t']:.2f} μm", va="center", fontsize=8.5)
a1.add_patch(__import__("matplotlib").patches.Rectangle((0.1, -0.2), 0.8, 0.2, color=d.MUTED, alpha=0.6))
a1.text(0.5, -0.1, T("衬底", "substrate"), ha="center", va="center", fontsize=8.5, color="white")
a1.set_xlim(0, 2.0); a1.set_ylim(-0.3, 6.9)
a1.set_ylabel(T("离衬底的高度 / μm", "height above substrate / μm"))
a1.set_xticks([])
for k in ("top", "right", "bottom"):
    a1.spines[k].set_visible(False)
a1.set_title(T("(a) 金属层的高度与厚度", "(a) layer heights and thicknesses"), fontsize=10)
x = np.arange(len(layers))
r_mm = [wire_r(l, WIRES[l]["wmin"]) * 1000 for l in layers]
c_mm = [wire_c(l, WIRES[l]["wmin"]) * 1000 * 1e15 for l in layers]
a2.bar(x - 0.2, r_mm, 0.4, color=d.PMOS, label=T("电阻 Ω/mm", "resistance Ω/mm"))
a2.set_yscale("log")
a2.set_ylabel(T("电阻 / (Ω/mm)", "resistance / (Ω/mm)"), color=d.PMOS)
a3 = a2.twinx()
a3.bar(x + 0.2, c_mm, 0.4, color=d.NMOS, label=T("电容 fF/mm", "capacitance fF/mm"))
a3.set_ylabel(T("电容 / (fF/mm)", "capacitance / (fF/mm)"), color=d.NMOS)
a3.set_ylim(0, max(c_mm) * 1.4)
a2.set_xticks(x, layers)
a2.set_title(T("(b) 最小线宽时每毫米的电阻（红，对数）与电容（蓝）", "(b) per-mm resistance (red, log) and capacitance (blue) at minimum width"), fontsize=10)
for k in ("top",):
    a2.spines[k].set_visible(False); a3.spines[k].set_visible(False)
figure(fig, "fig4_1_1")
