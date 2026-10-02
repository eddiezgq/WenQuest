"""50.4 节：基准不重合的代价（算例 50.4.1）。

键槽在磨削之前铣：铣键槽时以精车后的 Ø40.3h8 外圆为基准控制槽底尺寸 H，而图纸的 d − t = 35₋₀.₂ 是从磨削后的 Ø40k6 外圆量起的。
封闭环 A₀ = d − t = H − R₁ + R₂，R₁ 是精车后的半径（减环），R₂ 是磨削后的半径（增环）。用极值法（第 51 章）解出 H。
"""
from bookout import out

A0, ES0, EI0 = 35.0, 0.0, -0.2                 # GB/T 1095：b = 12（d > 38~44）t = 5.0⁺⁰·²，图纸标 d − t = 35₋₀.₂
R1, ES1, EI1 = 40.3 / 2, 0.0, -0.039 / 2       # 精车 Ø40.3h8 的半径
R2, ES2, EI2 = 40.0 / 2, 0.018 / 2, 0.002 / 2  # 磨削 Ø40k6 的半径
H = A0 + R1 - R2
ES_H = ES0 + EI1 - ES2
EI_H = EI0 + ES1 - EI2
T_H = ES_H - EI_H
# 区间核对
Hmax, Hmin = H + ES_H, H + EI_H
assert abs((Hmax - (R1 + EI1) + (R2 + ES2)) - (A0 + ES0)) < 1e-12
assert abs((Hmin - (R1 + ES1) + (R2 + EI2)) - (A0 + EI0)) < 1e-12
out(A0=A0, H=H, ES_H=ES_H, EI_H=EI_H, T_H=T_H, T0=ES0 - EI0, shrink_pct=100 * (1 - T_H / (ES0 - EI0)), Hmax=Hmax, Hmin=Hmin,
    T1=ES1 - EI1, T2=ES2 - EI2, R1=R1, EI1=EI1, R2=R2, ES2=ES2, EI2=EI2)

# ---- 图 50.4.1：（a）粗车以外圆为粗基准，夹一端、钻中心孔；（b）精车、磨削以两端中心孔为精基准；（c）键槽尺寸的尺寸链
from matplotlib.patches import Polygon, Rectangle

import _mfg as M
from bookout import T, figure, style

plt = style()
fig, axs = plt.subplots(1, 3, figsize=(7.4, 2.4), gridspec_kw={"width_ratios": [1.1, 1.1, 0.9]})
for k, ax in enumerate(axs[:2]):
    ax.add_patch(Rectangle((0, -10), 60, 20, fc=M.STEEL, ec=M.INK, lw=1))
    ax.plot([-8, 68], [0, 0], color=M.MUTED, lw=0.7, ls=(0, (6, 2, 1, 2)))
    if k == 0:
        for s in (1, -1):        # 三爪卡盘的卡爪夹在外圆上
            ax.add_patch(Rectangle((-2, s * 10 if s > 0 else -16), 14, 6, fc="#d98c3a", ec=M.INK, lw=0.8))
        ax.add_patch(Polygon([[60, -2], [54, 0], [60, 2]], fc="white", ec=M.INK, lw=0.8))
        ax.text(30, -22, T("(a) 粗基准：毛坯外圆", "(a) rough datum: bar OD"), ha="center", fontsize=9)
    else:
        for x0, s in ((0, 1), (60, -1)):
            ax.add_patch(Polygon([[x0, -2.5], [x0 + s * 5, 0], [x0, 2.5]], fc="white", ec=M.INK, lw=0.8))
            ax.add_patch(Polygon([[x0 - s * 9, -3], [x0 + s * 3.5, 0], [x0 - s * 9, 3]], fc="#3a7dc9", ec=M.INK, lw=0.8))
        ax.text(30, -22, T("(b) 精基准：两端中心孔", "(b) finish datum: centre holes"), ha="center", fontsize=9)
    ax.set_xlim(-14, 74); ax.set_ylim(-26, 18); ax.set_aspect("equal"); ax.axis("off")
ax = axs[2]
ax.add_patch(plt.Circle((0, 0), 23.0, fc="#e6eef7", ec="#3a7dc9", lw=1, ls="--"))       # 精车外圆（磨量夸大画出）
ax.add_patch(plt.Circle((0, 0), 20.0, fc=M.STEEL, ec=M.INK, lw=1))
ax.add_patch(Rectangle((-6, 15), 12, 5.2, fc="white", ec=M.INK, lw=0.8))
ax.annotate("", (8, 15), (8, -23.0), arrowprops=dict(arrowstyle="<->", color="#3a7dc9", lw=0.8))
ax.text(9, -4, "H", color="#3a7dc9", fontsize=10)
ax.annotate("", (-8, 15), (-8, -20.0), arrowprops=dict(arrowstyle="<->", color=M.INK, lw=0.8))
ax.text(-16.5, -4, "d−t₁", color=M.INK, fontsize=9)
ax.text(0, -31, T("(c) 铣槽时量 H，图纸要 d−t₁\n（虚线为精车外圆，磨量夸大）", "(c) milled to H, drawing gives d−t₁\n(dashed: turned OD, allowance exaggerated)"), ha="center", fontsize=8.5, va="top")
ax.set_xlim(-27, 27); ax.set_ylim(-40, 25); ax.set_aspect("equal"); ax.axis("off")
figure(fig, "fig50_4_1")
