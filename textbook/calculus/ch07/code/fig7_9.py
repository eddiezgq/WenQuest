"""图 7.9.1：云台相机跟踪 AGV 的几何关系，以及所需的转动角速度。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

d, v, lim = 2.0, 1.5, 0.5
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.4, 3.9), gridspec_kw={"width_ratios": [1, 1.3]})
a1.plot([-3.5, 3.5], [0, 0], color=MUTED, lw=6, alpha=0.3)
a1.text(-3.4, 0.15, T("AGV 路线", "AGV route"), color=MUTED)
xa = 1.5
a1.add_patch(plt.Rectangle((xa - 0.35, -0.18), 0.7, 0.36, fc=BLUE, ec=INK))
a1.annotate("", xy=(xa + 1.1, 0), xytext=(xa + 0.4, 0), arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=2))
a1.text(xa + 0.6, 0.2, "$v$", color=BLUE, fontsize=12)
a1.plot([0], [-d], "s", color=INK, ms=9)
a1.text(0.15, -d - 0.1, T("相机", "camera"))
a1.plot([0, 0], [-d, 0], color=MUTED, ls="--")
a1.plot([0, xa], [-d, 0], color=RED, lw=1.5)
a1.text(-0.35, -d / 2, "$d$", fontsize=12)
a1.text(xa / 2, 0.12, "$x$", fontsize=12)
a1.text(0.12, -d + 0.55, r"$\theta$", color=RED, fontsize=12)
a1.set_aspect("equal")
a1.set_xlim(-3.5, 3.5)
a1.set_ylim(-2.5, 0.8)
a1.axis("off")
x = np.linspace(-6, 6, 400)
w = v * d / (d**2 + x**2)
a2.plot(x, w, color=INK, lw=2)
a2.axhline(lim, color=RED, ls="--", lw=1.2)
xs = math.sqrt(v * d / lim - d**2)
a2.fill_between(x, lim, w, where=w > lim, color=RED, alpha=0.15)
a2.text(2.0, lim + 0.03, T("云台限速 0.5 rad/s", "pan limit 0.5 rad/s"), color=RED)
a2.set_xlabel(T("AGV 位置 x / m", "AGV position x / m"))
a2.set_ylabel(T("dθ/dt / (rad/s)", "dθ/dt / (rad/s)"))
a2.set_title(T("经过相机正前方时需要转得最快", "The camera must turn fastest as the AGV passes closest"), fontsize=11)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig7_9_1")
