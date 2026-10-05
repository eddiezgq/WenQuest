"""Fig. 1.8.1  Hanger-rod connection of the Hyatt Regency skywalks: original design (one continuous rod) and as built
(two offset rods). The program gives the force on the nut at the connection; the load each walkway passes to the rod is P."""
from matplotlib.patches import Rectangle

import _ch1 as H
from bookout import T, figure, out, style

P = 1.0
design = {"nut_4th": P, "rod_above_4th": 2 * P}      # original: the nut under the 4th-floor box beam carries only the 4th-floor walkway; the 2nd-floor load goes straight up the continuous rod
asbuilt = {"nut_4th": 2 * P, "rod_above_4th": 2 * P}  # as built: the 2nd-floor rod hangs from the 4th-floor box beam, so the nut under that beam carries both walkways

plt = style()
fig, axs = plt.subplots(1, 2, figsize=(6.6, 3.3))
for ax, case, title in ((axs[0], design, T("原设计：一根通长吊杆", "original: one continuous rod")),
                        (axs[1], asbuilt, T("实际施工：两根吊杆", "as built: two rods"))):
    ax.add_patch(Rectangle((-0.6, 2.0), 1.2, 0.35, fc=H.PALE["gray"], ec=H.INK))      # 4th-floor walkway box beam
    ax.add_patch(Rectangle((-0.6, 0.0), 1.2, 0.35, fc=H.PALE["gray"], ec=H.INK))      # 2nd-floor walkway box beam
    ax.text(0.75, 2.17, T("四楼走廊", "4th-floor walkway"), fontsize=7.5, va="center")
    ax.text(0.75, 0.17, T("二楼走廊", "2nd-floor walkway"), fontsize=7.5, va="center")
    if case is design:
        ax.plot([0, 0], [-0.2, 3.3], color=H.INK, lw=2.4)
    else:
        ax.plot([-0.15, -0.15], [1.9, 3.3], color=H.INK, lw=2.4)
        ax.plot([0.15, 0.15], [-0.2, 2.45], color=H.INK, lw=2.4)
    xn = 0 if case is design else -0.15
    ax.add_patch(Rectangle((xn - 0.12, 1.88), 0.24, 0.12, fc="#c0392b", ec=H.INK))        # nut under the 4th-floor box beam (the critical one)
    xl = 0 if case is design else 0.15
    ax.add_patch(Rectangle((xl - 0.12, -0.12), 0.24, 0.12, fc=H.PALE["gray"], ec=H.INK))   # nut under the 2nd-floor box beam
    if case is not design:
        ax.add_patch(Rectangle((xl - 0.12, 2.35), 0.24, 0.12, fc=H.PALE["gray"], ec=H.INK))  # lower rod hung from the 4th-floor box beam
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
