"""图 1.2.1 设计的全过程：七个阶段、阶段评审，以及每个阶段在数字工厂里用的系统；红线是工程更改的回路。"""
import _ch1 as H
from bookout import T, figure, style

plt = style()
fig, ax = plt.subplots(figsize=(6.9, 3.3))
stages = [
    (T("需求", "Needs"), T("客户订单\n参数配置器", "orders\nconfigurator"), H.PALE["blue"]),
    (T("方案", "Concept"), T("方案比较\n草图、计算", "options\nsketches, sums"), H.PALE["blue"]),
    (T("详细设计", "Detail design"), T("CAD、计算书\n零件库", "CAD, calc sheet\nparts library"), H.PALE["green"]),
    (T("验证", "Verification"), T("CAE：有限元\n疲劳、动力学", "CAE: FE,\nfatigue, dynamics"), H.PALE["orange"]),
    (T("发布", "Release"), T("PLM 审批\nERP 物料与 BOM", "PLM approval\nERP items, BOM"), H.PALE["purple"]),
    (T("制造", "Manufacture"), T("MES 工单、数控程序\nQMS 检验", "MES orders, CNC\nQMS inspection"), H.PALE["teal"]),
    (T("服务", "Service"), T("现场数据\n维修、备件", "field data\nrepair, spares"), H.PALE["teal"]),
]
w, gap = 0.86, 0.14
for k, (name, sys_, col) in enumerate(stages):
    x = k * (w + gap)
    H.box(ax, x, 1.6, w, 0.55, name, col, 8.5, True)
    ax.text(x + w / 2, 1.25, sys_, ha="center", va="top", fontsize=7, color=H.MUTED)
    if k < len(stages) - 1:
        H.arrow(ax, (x + w, 1.875), (x + w + gap, 1.875))
        ax.plot([x + w + gap / 2] * 2, [2.25, 2.45], color=H.INK, lw=0.8)
        ax.plot(x + w + gap / 2, 2.5, marker="D", ms=4, color=H.INK)
ax.text(3.5, 2.75, T("◆ 阶段评审（设计评审）：通过才进入下一阶段", "◆ gate (design review): pass to go on"), ha="center", fontsize=7.5)
COLOR = "#c0392b"
H.arrow(ax, (6 * (w + gap) + w / 2, 0.8), (2 * (w + gap) + w / 2, 0.8), color=COLOR, lw=0.9, rad=-0.15)
ax.text(4.1, 0.05, T("工程更改：评审、检验或现场发现的问题回到详细设计（如 SH-301 A 版 → B 版）",
                     "engineering change: problems found in review, inspection or service go back to detail design (e.g. SH-301 A → B)"),
        ha="center", fontsize=7.5, color=COLOR)
ax.set_xlim(-0.1, 7 * (w + gap))
ax.set_ylim(-0.2, 3.0)
ax.axis("off")
fig.tight_layout()
figure(fig, "fig1_2_1")
