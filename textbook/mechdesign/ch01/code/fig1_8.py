"""图 1.8.1 凯悦酒店空中走廊的吊杆节点：原设计（一根通长吊杆）与实际施工（两根吊杆错开）。
程序给出节点处螺母的受力：每层走廊传给吊杆的载荷记为 P。"""
from matplotlib.patches import Rectangle

import _ch1 as H
from bookout import T, figure, out, style

P = 1.0
design = {"nut_4th": P, "rod_above_4th": 2 * P}      # 原设计：四楼箱梁下的螺母只托四楼走廊；二楼走廊的载荷沿通长吊杆直接上传
asbuilt = {"nut_4th": 2 * P, "rod_above_4th": 2 * P}  # 实际：二楼吊杆挂在四楼箱梁上，四楼箱梁下的螺母要托两层走廊

plt = style()
fig, axs = plt.subplots(1, 2, figsize=(6.6, 3.3))
for ax, case, title in ((axs[0], design, T("原设计：一根通长吊杆", "original: one continuous rod")),
                        (axs[1], asbuilt, T("实际施工：两根吊杆", "as built: two rods"))):
    ax.add_patch(Rectangle((-0.6, 2.0), 1.2, 0.35, fc=H.PALE["grey"], ec=H.INK))      # 四楼走廊箱梁
    ax.add_patch(Rectangle((-0.6, 0.0), 1.2, 0.35, fc=H.PALE["grey"], ec=H.INK))      # 二楼走廊箱梁
    ax.text(0.75, 2.17, T("四楼走廊", "4th-floor walkway"), fontsize=7.5, va="center")
    ax.text(0.75, 0.17, T("二楼走廊", "2nd-floor walkway"), fontsize=7.5, va="center")
    if case is design:
        ax.plot([0, 0], [-0.2, 3.3], color=H.INK, lw=2.4)
    else:
        ax.plot([-0.15, -0.15], [1.9, 3.3], color=H.INK, lw=2.4)
        ax.plot([0.15, 0.15], [-0.2, 2.45], color=H.INK, lw=2.4)
    xn = 0 if case is design else -0.15
    ax.add_patch(Rectangle((xn - 0.12, 1.88), 0.24, 0.12, fc="#c0392b", ec=H.INK))        # 四楼箱梁下的螺母（关键）
    xl = 0 if case is design else 0.15
    ax.add_patch(Rectangle((xl - 0.12, -0.12), 0.24, 0.12, fc=H.PALE["grey"], ec=H.INK))   # 二楼箱梁下的螺母
    if case is not design:
        ax.add_patch(Rectangle((xl - 0.12, 2.35), 0.24, 0.12, fc=H.PALE["grey"], ec=H.INK))  # 下吊杆挂在四楼箱梁上
    ax.annotate("", (xn + 0.02, 1.25), (xn + 0.02, 1.85), arrowprops=dict(arrowstyle="<-", color="#c0392b", lw=1.6))
    ax.text(xn - 0.2, 1.5, T("螺母托 {:g}P", "nut carries {:g}P").format(case["nut_4th"]), fontsize=8.5, color="#c0392b", ha="right")
    ax.text(0.05, 3.35, T("屋顶吊点", "roof hanger"), fontsize=7, ha="center", va="bottom", color=H.MUTED)
    ax.set_title(title, fontsize=9)
    ax.set_xlim(-1.8, 1.9)
    ax.set_ylim(-0.4, 3.7)
    ax.axis("off")
fig.tight_layout()
figure(fig, "fig1_8_1")
out(ratio=asbuilt["nut_4th"] / design["nut_4th"])
