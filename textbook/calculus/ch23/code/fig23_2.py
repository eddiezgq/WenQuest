"""图 23.2.1：左：调和级数的部分和与 ln n + γ，矩形面积说明 Hₙ > ln(n + 1)；右：8 块砖的最大悬挑 H₈/2。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
x = np.linspace(1, 10.5, 300)
for k in range(1, 10):
    a1.add_patch(plt.Rectangle((k, 0), 1, 1 / k, facecolor=BLUE, alpha=0.18, edgecolor=BLUE, lw=0.8))
a1.plot(x, 1 / x, color=RED, lw=2, label="y = 1/x")
a1.text(5.5, 0.6, T("矩形面积之和 Hₙ\n> 曲线下面积 ln(n + 1)", "rectangles Hₙ\n> area under curve ln(n + 1)"), fontsize=9)
a1.set_xlabel("x"); a1.set_ylabel("y")
a1.set_title(T("Hₙ = 1 + 1/2 + … + 1/n 与 ∫ dx/x 的比较", "Hₙ = 1 + 1/2 + … + 1/n versus ∫ dx/x"), fontsize=10)
a1.legend(fontsize=9, frameon=False); clean(a1)
# 砖块：自上而下第 k 块相对下一块伸出 1/(2k)
n = 8
L, Hb = 1.0, 0.18
offs = [0.0]
for k in range(1, n + 1):
    offs.append(offs[-1] + 1 / (2 * k))
top = offs[-1]
for k in range(1, n + 1):
    right = top - offs[k - 1]                      # 从上往下数第 k 块的右端
    y = (n - k) * Hb
    a2.add_patch(plt.Rectangle((right - L, y), L, Hb * 0.95, facecolor=ACC if k % 2 else BLUE, alpha=0.6, edgecolor=INK, lw=0.8))
edge = top - offs[-1]
a2.add_patch(plt.Rectangle((edge - 1.5, -0.25), 1.5, 0.25, facecolor=MUTED, alpha=0.4))
a2.text(edge - 0.75, -0.17, T("桌面", "table"), ha="center", fontsize=9)
a2.axvline(edge, color=INK, lw=1, ls=":")
a2.annotate("", xy=(top, n * Hb + 0.12), xytext=(edge, n * Hb + 0.12), arrowprops=dict(arrowstyle="<->", color=RED, lw=1.5))
a2.text((top + edge) / 2, n * Hb + 0.18, T(f"悬挑 H₈/2 ≈ {offs[-1]:.2f} 块长", f"overhang H₈/2 ≈ {offs[-1]:.2f} lengths"), color=RED, ha="center", fontsize=9)
a2.set_xlim(edge - 1.7, top + 0.3); a2.set_ylim(-0.3, n * Hb + 0.45); a2.set_aspect("equal")
a2.axis("off")
a2.set_title(T("8 块砖叠出来，最上面一块已完全伸出桌边", "With 8 bricks the top one lies entirely beyond the edge"), fontsize=10)
fig.tight_layout()
figure(fig, "fig23_2_1")
