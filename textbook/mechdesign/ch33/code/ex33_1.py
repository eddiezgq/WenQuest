"""33.1 节：轴的类型与材料。

图 33.1.1  心轴、传动轴、转轴：受什么载荷（弯矩图、转矩图示意）；
图 33.1.2  候选材料的疲劳极限与弹性模量（数字工厂材料库）：换合金钢能提高强度，几乎不能提高刚度；
算例 33.1.1  SH-301 用 45 钢调质还是 40Cr 调质：强度、刚度、价格的比较。
"""
import numpy as np

import _draw as D
from bookout import T, figure, out, style
import mdstd

# ---- 算例 33.1.1：材料库里的四种轴用材料
ids = ["45-QT", "40Cr-QT", "20CrMnTi-CQ", "QT500-7"]
mats = [mdstd.material(i) for i in ids]
m45, m40 = mats[0], mats[1]
gain_strength = m40["sigma_1"] / m45["sigma_1"]
gain_stiff = m40["E"] / m45["E"]
# 价格：数字工厂物料单价（factory/工厂设计.md，示意数值，美元/kg）：45 钢圆棒 1.60；40Cr 按 20CrMnTi 圆钢同价位 2.40 估
price_45, price_40 = 1.60, 2.40
price_ratio = price_40 / price_45

# ---- 图 33.1.1：三种轴
plt = style()
fig, axs = plt.subplots(3, 1, figsize=(6.4, 5.4))
cases = [
    (T("心轴：只受弯矩，不传转矩（如车辆的从动轴、滑轮轴）", "Axle: bending only, no torque (e.g. idler, pulley axle)"), True, False),
    (T("传动轴：只传转矩，基本不受弯矩（如汽车传动轴）", "Transmission shaft: torque only, little bending (e.g. propeller shaft)"), False, True),
    (T("转轴：既受弯矩又传转矩（减速器的轴，最常见）", "Rotating shaft: bending and torque (gearbox shafts — the common case)"), True, True),
]
z = np.linspace(0, 100, 201)
for ax, (title, bend, tors) in zip(axs, cases):
    lay = [(0, 100, 10)]
    D.shaft(ax, lay)
    D.support(ax, 8, -5, 3.5)
    D.support(ax, 92, -5, 3.5)
    if bend:
        D.force(ax, 50, 24, 0, -18, "F", size=10, off=(5, 9))
        Mz = np.where(z <= 50, (z - 8).clip(0) / 42, (92 - z).clip(0) / 42) * 12
        ax.fill_between(z, -16 + 0 * z, -16 - Mz, color=D.MOMENT, alpha=0.25, lw=0)
        ax.plot(z, -16 - Mz, color=D.MOMENT, lw=1.4)
        ax.text(102, -20, "M", color=D.MOMENT, fontsize=11)
    if tors:
        z0 = 50 if bend else 0
        Tz = np.where(z >= z0, 8, 0)
        ax.fill_between(z, -32, -32 - Tz, color=D.TORQUE, alpha=0.25, lw=0)
        ax.plot(z, -32 - Tz, color=D.TORQUE, lw=1.4)
        ax.text(102, -37, "T", color=D.TORQUE, fontsize=11)
        if bend:
            ax.text(50, -50, T("转矩从齿轮输入、联轴器输出", "torque in at the gear, out at the coupling"), fontsize=8, color=D.MUTED, ha="center")
    ax.set_title(title, fontsize=10, loc="left")
    ax.set_xlim(-6, 112)
    ax.set_ylim(-54, 28)
    ax.set_aspect("equal")
    ax.axis("off")
fig.tight_layout()
figure(fig, "fig33_1_1")

# ---- 图 33.1.2：强度与刚度
fig, ax = plt.subplots(figsize=(6.6, 3.4))
x = np.arange(len(mats))
s1 = [m["sigma_1"] for m in mats]
E = [m["E"] / 1000 for m in mats]
ax.bar(x - 0.2, s1, 0.38, color=D.MOMENT, label=T("疲劳极限 σ₋₁ / MPa", "Endurance limit σ₋₁ / MPa"))
ax2 = ax.twinx()
ax2.bar(x + 0.2, E, 0.38, color=D.GEAR, label=T("弹性模量 E / GPa", "Elastic modulus E / GPa"))
ax.set_xticks(x)
ax.set_xticklabels([T(m["name"].replace("（", "\n（").replace(" 球墨", "\n球墨"), m["id"]) for m in mats], fontsize=9)
ax.set_ylabel("σ₋₁ / MPa", color=D.MOMENT)
ax2.set_ylabel("E / GPa", color=D.GEAR)
ax.set_ylim(0, 700)
ax2.set_ylim(0, 300)
for xi, v in zip(x, s1):
    ax.text(xi - 0.2, v + 8, f"{v:.0f}", ha="center", fontsize=9, color=D.MOMENT)
for xi, v in zip(x, E):
    ax2.text(xi + 0.2, v + 3, f"{v:.0f}", ha="center", fontsize=9, color="#8a6a1e")
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, fontsize=8.5, loc="upper left", frameon=False, ncol=2)
for a in (ax, ax2):
    a.spines["top"].set_visible(False)
fig.tight_layout()
figure(fig, "fig33_1_2")

out(s1_45=m45["sigma_1"], s1_40=m40["sigma_1"], sb_45=m45["sigma_b"], sb_40=m40["sigma_b"], ss_45=m45["sigma_s"],
    ss_40=m40["sigma_s"], tau1_45=m45["tau_1"], tau1_40=m40["tau_1"], E_45=m45["E"] / 1000, E_40=m40["E"] / 1000,
    gain_strength=gain_strength, gain_stiff=gain_stiff, price_45=price_45, price_40=price_40, price_ratio=price_ratio,
    s1_qt=mats[3]["sigma_1"], E_qt=mats[3]["E"] / 1000, s1_cr=mats[2]["sigma_1"])
