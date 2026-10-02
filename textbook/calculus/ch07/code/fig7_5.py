"""图 7.5.1：电机—减速器—上臂，变化率逐级相乘。"""
from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

fig, ax = plt.subplots(figsize=(10, 2.8))
boxes = [(0.2, T("电机", "motor"), r"$\theta_m$"), (3.3, T("减速器", "reducer"), r"$\theta=\theta_m/N$"), (6.4, T("上臂", "upper arm"), r"$y=l_1\sin\theta$")]
for x, name, var in boxes:
    ax.add_patch(plt.Rectangle((x, 0.4), 2.2, 1.2, fc="#eef3f8", ec=INK, lw=1.2))
    ax.text(x + 1.1, 1.22, name, ha="center", fontsize=12)
    ax.text(x + 1.1, 0.72, var, ha="center", fontsize=12)
for x0, lab in ((2.4, r"$\dfrac{d\theta}{d\theta_m}=\dfrac{1}{N}$"), (5.5, r"$\dfrac{dy}{d\theta}=l_1\cos\theta$")):
    ax.annotate("", xy=(x0 + 0.9, 1.0), xytext=(x0, 1.0), arrowprops=dict(arrowstyle="-|>", color=RED, lw=2, mutation_scale=16))
    ax.text(x0 + 0.45, 1.75, lab, ha="center", color=RED, fontsize=12)
ax.annotate("", xy=(9.6, 1.0), xytext=(8.6, 1.0), arrowprops=dict(arrowstyle="-|>", color=RED, lw=2, mutation_scale=16))
ax.text(9.65, 0.92, r"$\dfrac{dy}{dt}$", color=RED, fontsize=13)
ax.text(5.0, -0.25, r"$\dfrac{dy}{dt}=\dfrac{dy}{d\theta}\cdot\dfrac{d\theta}{d\theta_m}\cdot\dfrac{d\theta_m}{dt}$", ha="center", fontsize=14, color=INK)
ax.text(0.0, 1.0, r"$\dfrac{d\theta_m}{dt}$", color=BLUE, fontsize=13, ha="right")
ax.set_xlim(-0.9, 10.5)
ax.set_ylim(-0.7, 2.3)
ax.axis("off")
fig.tight_layout()
figure(fig, "fig7_5_1")
