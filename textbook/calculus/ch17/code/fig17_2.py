"""图 17.2.1：左：水箱侧壁上的压强随深度线性增加（三角形分布），合力作用在 2/3 水深处；
右：竖直的圆形观察窗，按深度切成水平窄条，每条受力 ρ g h · 宽度 · dh。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.3))
H = 0.25
y = np.linspace(0, H, 12)
a1.plot([0, 0], [0, -H], color=INK, lw=3)
for yy in y[1:]:
    p = yy / H
    a1.annotate("", (0, -yy), (p, -yy), arrowprops=dict(arrowstyle="->", color=BLUE, lw=1))
a1.plot([0, 1], [0, -H], color=BLUE, lw=1.5)
a1.annotate("", (0, -2 * H / 3), (1.3, -2 * H / 3), arrowprops=dict(arrowstyle="->", color=RED, lw=3))
a1.text(0.62, -2 * H / 3 + 0.012, T("合力 F，作用在 2H/3 处", "resultant F at depth 2H/3"), color=RED, fontsize=9)
a1.text(0.45, -0.06, T("压强 p = ρ g y", "pressure p = ρ g y"), color=BLUE, fontsize=9)
a1.axhline(0, color=BLUE, lw=0.8, ls="--")
a1.set_xlim(-0.2, 1.5)
a1.set_ylim(-0.29, 0.03)
a1.set_xticks([])
a1.set_ylabel(T("水面以下 / m", "below the surface / m"))
a1.set_title(T("矩形侧壁：压强三角形分布", "Rectangular wall: triangular pressure"), fontsize=10)
clean(a1, zero=False)
r = 1.0
t = np.linspace(0, 2 * np.pi, 200)
a2.fill(r * np.cos(t), r * np.sin(t), color=BLUE, alpha=0.12)
a2.plot(r * np.cos(t), r * np.sin(t), color=BLUE, lw=2)
s0, ds = 0.35, 0.12
w = np.sqrt(r * r - s0 * s0)
a2.add_patch(plt.Rectangle((-w, -s0 - ds / 2), 2 * w, ds, color=RED, alpha=0.5))
a2.annotate(T("深度 h_c + s 处的窄条（s 向下为正）：\n宽 2√(r² − s²)，高 ds", "strip at depth h_c + s (s downwards):\nwidth 2√(r² − s²), height ds"), (w, -s0), (0.3, -1.35), fontsize=9,
            arrowprops=dict(arrowstyle="->", color=INK))
a2.plot([0], [0], "o", color=INK)
a2.text(0.05, 0.06, T("中心深度 h_c", "centre at depth h_c"), fontsize=9)
a2.set_aspect("equal")
a2.set_xlim(-1.4, 1.9)
a2.set_ylim(-1.5, 1.3)
a2.axis("off")
a2.set_title(T("ROV 观察窗：F = ∫ρ g h · 宽度 dh = ρ g h_c A", "ROV window: F = ∫ρ g h · width dh = ρ g h_c A"), fontsize=10)
fig.tight_layout()
figure(fig, "fig17_2_1")
