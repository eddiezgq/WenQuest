"""1.1 从一台减速器说起：WQR-105 的层次（机器—部件—零件）、传动比与各轴的转速、功率、转矩（算例 1.1.1，图 1.1.1、1.1.2）。
数据：数字工厂的齿数、BOM（factory/factory/data.py）与参数配置器的标准工况（4 kW、1450 r/min、KA 1.25）。"""
import numpy as np

import _ch1 as H
from bookout import T, figure, out, style

F, C = H.F, H.C
P_IN = 4.0                                    # kW：参数配置器的默认输入功率
KA = 1.25                                     # 参数配置器默认工况系数（中等冲击）
ETA_G, ETA_B = 0.97, 0.99                     # 一对齿轮、一对轴承（与配置器 ETA 同一组数）
assert abs(ETA_G ** 2 * ETA_B ** 3 - C.ETA) < 1e-12

z1, z2 = F.GEARS["SH-101"]["z"], F.GEARS["GR-202"]["z"]
z3, z4 = F.GEARS["GR-203"]["z"], F.GEARS["GR-302"]["z"]
i1, i2 = z2 / z1, z4 / z3
i = i1 * i2
n = [F.INPUT_SPEED_RPM, F.INPUT_SPEED_RPM / i1, F.INPUT_SPEED_RPM / i]
P = [P_IN * ETA_B]                            # 各轴传出的功率：每根轴一对轴承，每级一对齿轮
P.append(P[0] * ETA_G * ETA_B)
P.append(P[1] * ETA_G * ETA_B)
Tq = [9550 * p / k for p, k in zip(P, n)]
T_out_ka = Tq[2] * KA

# ---- BOM：层次与零件数
tree = H.bom_tree()
n_make = sum(1 for lvl, c, q in tree if H.kind(c) == "make")
n_buy_lines = sum(1 for lvl, c, q in tree if H.kind(c) == "buy")
n_pieces = sum(q for lvl, c, q in tree if H.kind(c) in ("make", "buy") and F.ITEMS[c][2] == "Nos")
n_sub = sum(1 for lvl, c, q in tree if H.kind(c) == "sub")

# ---------------------------------------------------------------- 图 1.1.1：机器—部件—零件
plt = style()
fig, ax = plt.subplots(figsize=(6.8, 3.6))
subs = [c for c, _ in F.BOMS["WQR-105"][1] if H.kind(c) == "sub"]
H.box(ax, 2.6, 3.3, 2.6, 0.5, T("机器：WQR-105 减速器", "Machine: WQR-105 reducer"), H.PALE["blue"], 9, True)
xs = np.linspace(0.0, 6.0, len(subs))
for x, s in zip(xs, subs):
    nm = F.ITEMS[s][0].split(" ")[0]
    H.box(ax, x, 2.2, 1.75, 0.5, f"{s}\n{T(nm, F.ITEMS[s][0].split(' ', 1)[1])}", H.PALE["green"], 7.5)
    H.arrow(ax, (3.9, 3.3), (x + 0.875, 2.7), H.MUTED)
    kids = [c for c, _ in F.BOMS[s][1]]
    for k, c in enumerate(kids):
        col = H.PALE["orange"] if H.kind(c) == "make" else H.PALE["grey"]
        H.box(ax, x + 0.1, 1.6 - 0.36 * k, 1.55, 0.29, c, col, 7)
others = [c for c, _ in F.BOMS["WQR-105"][1] if H.kind(c) != "sub"]
ax.text(7.95, 2.45, T("另有总装件 {} 种\n（端盖、油封、螺钉、\n润滑油……）", "plus {} final-assembly\nitems (caps, seals,\nscrews, oil …)").format(len(others)),
        fontsize=7.5, va="center", color=H.MUTED)
H.box(ax, 0.0, -0.95, 1.0, 0.3, T("自制零件", "made part"), H.PALE["orange"], 7)
H.box(ax, 1.2, -0.95, 1.0, 0.3, T("外购件", "bought part"), H.PALE["grey"], 7)
ax.set_xlim(-0.2, 9.6)
ax.set_ylim(-1.05, 3.9)
ax.axis("off")
fig.tight_layout()
figure(fig, "fig1_1_1")

# ---------------------------------------------------------------- 图 1.1.2：动力从电机到输出轴
fig, axs = plt.subplots(1, 3, figsize=(6.8, 2.6))
names = [T("输入轴", "input"), T("中间轴", "intermediate"), T("输出轴", "output")]
for ax, vals, lab, col, fmt in ((axs[0], n, T("转速 / (r/min)", "speed / (r/min)"), "#2c6fbb", "{:.0f}"),
                                (axs[1], P, T("功率 / kW（纵轴不从 0 起）", "power / kW (axis not from 0)"), "#b8860b", "{:.2f}"),
                                (axs[2], Tq, T("转矩 / (N·m)", "torque / (N·m)"), "#8e44ad", "{:.1f}")):
    ax.bar(range(3), vals, color=col, width=0.6)
    ax.set_xticks(range(3))
    ax.set_xticklabels(names, fontsize=8)
    ax.set_title(lab, fontsize=9)
    for k, v in enumerate(vals):
        ax.text(k, v, fmt.format(v), ha="center", va="bottom", fontsize=7.5)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
axs[1].set_ylim(P[2] * 0.9, P_IN * 1.01)
fig.tight_layout()
figure(fig, "fig1_1_2")

out(z1=z1, z2=z2, z3=z3, z4=z4, i1=i1, i2=i2, i=i, n1=n[0], n2=n[1], n3=n[2], P_in=P_IN, P1=P[0], P2=P[1], P3=P[2],
    eta=C.ETA, T1=Tq[0], T2=Tq[1], T3=Tq[2], KA=KA, T3ka=T_out_ka, T_rated=C.T_RATED, loss_w=(P_IN - P[2]) * 1000,
    n_make=n_make, n_buy=n_buy_lines, n_pieces=n_pieces, n_sub=n_sub, n_items=len(F.ITEMS), a1=C.A1, a2=C.A2,
    m1=F.GEARS["SH-101"]["m"], m2=F.GEARS["GR-302"]["m"], n_others=len(others))
