"""图 17.3.1：左：变截面连杆（截面积从根部到末端减为一半），质心在 4L/9 处，而不是 L/2；
右：装满物料的 AGV 料斗，物料的质心在斗内 0.65 倍高度处，整车质心升高，侧翻极限 a = g·(b/2)/h。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
L = 0.5
x = np.linspace(0, L, 200)
hw = 0.04 * (1 - x / (2 * L))
a1.fill_between(x, -hw, hw, color=BLUE, alpha=0.35)
a1.plot(x, hw, color=BLUE)
a1.plot(x, -hw, color=BLUE)
a1.plot([4 * L / 9], [0], "o", color=RED, ms=9)
a1.text(4 * L / 9, 0.055, T("质心 4L/9", "centre of mass 4L/9"), color=RED, ha="center", fontsize=10)
a1.axvline(L / 2, color=MUTED, ls="--", lw=1)
a1.text(L / 2 + 0.005, -0.065, "L/2", color=MUTED, fontsize=9)
a1.set_xlim(-0.02, 0.53)
a1.set_ylim(-0.08, 0.08)
a1.set_xlabel("x / m")
a1.set_yticks([])
a1.set_title(T("变截面连杆：x̄ = ∫xλ dx / ∫λ dx", "Tapered link: x̄ = ∫xλ dx / ∫λ dx"), fontsize=10)
clean(a1, zero=False)
# AGV + 料斗
a2.add_patch(plt.Rectangle((-0.45, 0.08), 0.9, 0.3, color=MUTED, alpha=0.5))
for xw in (-0.3, 0.3):
    a2.add_patch(plt.Circle((xw, 0.08), 0.08, color=INK))
a2.fill([-0.1, 0.1, 0.3, -0.3], [0.45, 0.45, 0.95, 0.95], color=ACC, alpha=0.5)
a2.plot([-0.1, 0.1, 0.3, -0.3, -0.1], [0.45, 0.45, 0.95, 0.95, 0.45], color=INK)
a2.plot([0], [0.45 + 0.327], "s", color=ACC, ms=8, mec=INK)
a2.text(0.33, 0.78, T("物料质心", "load centre"), fontsize=9)
a2.plot([0], [0.22], "s", color=MUTED, ms=8, mec=INK)
a2.text(0.08, 0.2, T("车体质心", "chassis centre"), fontsize=9)
a2.plot([0], [0.558], "o", color=RED, ms=10)
a2.text(-0.62, 0.56, T("整车质心 h", "overall centre h"), color=RED, fontsize=9)
a2.plot([0.3, 0], [0, 0.558], color=RED, ls="--", lw=1)
a2.annotate("", (-0.3, -0.06), (0.3, -0.06), arrowprops=dict(arrowstyle="<->", color=INK))
a2.text(0, -0.12, T("轮距 B", "track B"), ha="center", fontsize=9)
a2.set_aspect("equal")
a2.set_xlim(-0.8, 0.8)
a2.set_ylim(-0.18, 1.05)
a2.axis("off")
a2.set_title(T("装满后质心升高：侧翻极限 a = g·(B/2)/h", "A full hopper raises the centre: tip-over limit a = g·(B/2)/h"), fontsize=10)
fig.tight_layout()
figure(fig, "fig17_3_1")
