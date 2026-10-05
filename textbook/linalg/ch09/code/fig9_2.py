"""图 9.2.1：求导的核是常数。左：p(x) = x³/3 − x 加上不同的常数 c；右：它们的导数都是 x² − 1。
D 把一整条“上下平移”的曲线族压成同一个像，丢掉的正好是核（常数）的那一维。"""
import numpy as np

from _fig import BLUE, INK, MUTED, RED, T, figure, plt

x = np.linspace(-2.2, 2.2, 300)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.0, 3.4))
fig.subplots_adjust(wspace=0.45)
cols = plt.cm.viridis(np.linspace(0.1, 0.85, 5))
for c, col in zip([-2, -1, 0, 1, 2], cols):
    a1.plot(x, x ** 3 / 3 - x + c, color=col, lw=1.8)
    a1.text(1.0, c - 0.67 + 0.12, f"c = {c}", color=col, fontsize=9, ha="center", va="bottom")
a1.set_title(T("p(x) + c：一整族多项式", "p(x) + c: a whole family"), fontsize=12, color=INK)
a2.plot(x, x ** 2 - 1, color=RED, lw=2.4)
a2.set_title(T("导数都是 x² − 1", "every derivative is x² − 1"), fontsize=12, color=INK)
for a in (a1, a2):
    a.axhline(0, color=MUTED, lw=0.6)
    a.axvline(0, color=MUTED, lw=0.6)
    a.set_xlim(-2.2, 2.2)
    a.set_ylim(-4, 4)
    a.set_xlabel("x")
    for s in ("top", "right"):
        a.spines[s].set_visible(False)
fig.text(0.5, 0.5, "D →", ha="center", va="center", fontsize=16, color=BLUE)
figure(fig, "fig9_2_1")
