"""图 4.5.1：单位圆中的三角形 OAB、扇形 OAB、三角形 OAD；cos x < sin x / x < 1。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.4), gridspec_kw={"width_ratios": [1, 1.3]})
x0 = 0.75
t = np.linspace(0, math.pi / 2, 200)
a1.plot(np.cos(t), np.sin(t), color=MUTED, lw=1)
a1.fill([0, 1, 1], [0, 0, math.tan(x0)], color=RED, alpha=0.10)
tt = np.linspace(0, x0, 100)
a1.fill(np.r_[0, np.cos(tt)], np.r_[0, np.sin(tt)], color=ACC, alpha=0.30, hatch="///", ec=ACC, lw=0)
a1.fill([0, 1, math.cos(x0)], [0, 0, math.sin(x0)], color=BLUE, alpha=0.20)
a1.plot([0, 1, 1, 0], [0, 0, math.tan(x0), 0], color=RED, lw=1.2)
a1.plot([0, math.cos(x0)], [0, math.sin(x0)], color=INK, lw=1)
a1.plot([math.cos(x0), math.cos(x0)], [0, math.sin(x0)], color=BLUE, lw=1.5)
for p, s, off in (((0, 0), "O", (-0.08, -0.06)), ((1, 0), "A", (0.03, -0.06)), ((math.cos(x0), math.sin(x0)), "B", (-0.09, 0.03)),
                  ((1, math.tan(x0)), "D", (0.03, 0))):
    a1.text(p[0] + off[0], p[1] + off[1], s)
a1.text(0.22, 0.06, "$x$")
a1.text(1.03, 0.4, r"$\tan x$", color=RED)
a1.text(math.cos(x0) - 0.2, 0.25, r"$\sin x$", color=BLUE)
a1.set_aspect("equal")
a1.set_xlim(-0.15, 1.35)
a1.set_ylim(-0.15, 1.05)
a1.axis("off")
a1.set_title(T("三角形 OAB < 扇形 OAB < 三角形 OAD", "triangle OAB < sector OAB < triangle OAD"), fontsize=10)
x = np.linspace(-2.5, 2.5, 801)
x = x[np.abs(x) > 1e-9]
a2.plot(x, np.sin(x) / x, color=RED, lw=2, label=r"$\sin x / x$")
a2.plot(x, np.cos(x), color=BLUE, lw=1.5, label=r"$\cos x$")
a2.axhline(1, color=GREEN, lw=1.5, label="$1$")
a2.plot([0], [1], "o", mfc="white", mec=RED, ms=6, zorder=5)
a2.set_ylim(-0.9, 1.3)
a2.legend(fontsize=9, frameon=False, loc="lower center")
a2.set_title(T("夹逼：cos x < sin x / x < 1", "Squeeze: cos x < sin x / x < 1"), fontsize=10)
clean(a2)
fig.tight_layout()
figure(fig, "fig4_5_1")
