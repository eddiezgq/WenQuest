"""图 14.2.1：关节正弦摆动 θ = A sin Ωt（A = 0.5 rad，1 Hz，J = 0.5 kg·m²，b = 0.2 N·m·s/rad）两个周期内的功率：
惯性部分正负交替、平均为零；摩擦部分始终为正，平均值 bA²Ω²/2（虚线）。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

J, b, A, W = 0.5, 0.2, 0.5, 2 * np.pi
t = np.linspace(0, 2, 1000)
om = A * W * np.cos(W * t)
al = -A * W * W * np.sin(W * t)
Pi = J * al * om
Pf = b * om ** 2
fig, ax = plt.subplots(figsize=(9, 4.4))
ax.plot(t, Pi, color=BLUE, lw=1.8, label=T("惯性部分 Jαω", "inertial Jαω"))
ax.plot(t, Pf, color=RED, lw=1.8, label=T("摩擦部分 bω²", "friction bω²"))
ax.plot(t, Pi + Pf, color=INK, lw=1.2, ls=":", label=T("合计", "total"))
ax.axhline(b * A * A * W * W / 2, color=RED, lw=1, ls="--")
ax.set_xlabel("t / s")
ax.set_ylabel("P / W")
ax.legend(fontsize=9, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=3)
ax.set_title(T("峰值功率十几瓦，平均功率不到 1 瓦", "Peak power above 15 W, average under 1 W"), fontsize=10)
clean(ax)
fig.tight_layout()
figure(fig, "fig14_2_1")
