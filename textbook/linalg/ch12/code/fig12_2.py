"""图 12.2.1：三相电流与复数空间矢量。(a) 伺服电机的三相电流 i_a、i_b、i_c（幅值 2 A，50 Hz，互差 120°）；
(b) 克拉克变换（功率不变形式，正交矩阵）后的 i_α + i·i_β 是复平面上匀速旋转、长度不变的空间矢量，长度 √(3/2)·2 A。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, axes_box, figure, plt

I0, f = 2.0, 50.0
t = np.linspace(0, 0.02, 401)
th = 2 * np.pi * f * t
sh = np.array([0, 2 * np.pi / 3, -2 * np.pi / 3])
i3 = I0 * np.cos(th[:, None] - sh)
s3 = np.sqrt(3)
C = np.sqrt(2 / 3) * np.array([[1, -0.5, -0.5], [0, s3 / 2, -s3 / 2]])
ab = i3 @ C.T
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 4.2), gridspec_kw={"width_ratios": [1.5, 1]})
for k, (c, n) in enumerate(zip((RED, GREEN, BLUE), ("i_a", "i_b", "i_c"))):
    a1.plot(t * 1000, i3[:, k], color=c, lw=1.8, label=f"${n}$")
a1.axhline(0, color=MUTED, lw=0.6)
for tk in (2.0, 7.0, 12.0):
    a1.axvline(tk, color=ACC, lw=0.8, ls=":")
a1.set_xlabel(T("时间 / ms", "time / ms")); a1.set_ylabel(T("电流 / A", "current / A"))
a1.set_xlim(0, 20); a1.set_ylim(-2.6, 2.6)
a1.legend(loc="upper right", frameon=False, ncol=3, fontsize=10)
for s in ("top", "right"):
    a1.spines[s].set_visible(False)
a1.set_title(T("(a) 三相电流", "(a) Three phase currents"), fontsize=11)
axes_box(a2, 3.2)
r = np.sqrt(1.5) * I0
a2.plot(r * np.cos(th), r * np.sin(th), color=MUTED, lw=1, ls="--")
for tk in (2.0, 7.0, 12.0):
    k = int(round(tk / 20 * 400))
    a2.annotate("", xy=(ab[k, 0], ab[k, 1]), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=ACC, lw=2, mutation_scale=13))
    a2.text(ab[k, 0] * 1.13 - 0.25, ab[k, 1] * 1.13, f"{tk:.0f} ms", color=ACC, fontsize=9)
a2.set_xlabel("Re  $i_\\alpha$"); a2.set_ylabel("Im  $i_\\beta$")
a2.set_title(T("(b) 空间矢量 $i_\\alpha + \\mathrm{i}\\, i_\\beta$", "(b) Space vector $i_\\alpha + \\mathrm{i}\\, i_\\beta$"), fontsize=11)
a2.text(-3.1, -3.0, T("长度恒为 √1.5 × 2 A", "constant length √1.5 × 2 A"), fontsize=9, color=INK)
fig.tight_layout()
figure(fig, "fig12_2_1")
