"""图 14.3.1：卧式圆柱水箱。左：截面，液位 h 以下的水是一个弓形；右：水量占比随液位占比的变化，
两端变化慢、中间变化快，与 45° 直线（按液位线性换算）的偏差。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

r = 1.0
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.4))
th = np.linspace(0, 2 * np.pi, 400)
a1.plot(r * np.cos(th), r * np.sin(th), color=INK, lw=2)
h = 0.6
y = np.linspace(-r, h - r, 200)
a1.fill_betweenx(y, -np.sqrt(r * r - y * y), np.sqrt(r * r - y * y), color=BLUE, alpha=0.35)
a1.axhline(h - r, color=BLUE, lw=1)
yy = -0.6
a1.plot([-np.sqrt(r * r - yy * yy), np.sqrt(r * r - yy * yy)], [yy, yy], color=RED, lw=2)
a1.text(0.05, yy + 0.05, r"$2\sqrt{r^2 - y^2}$", color=RED, fontsize=12)
a1.annotate("", xy=(1.15, h - r), xytext=(1.15, -r), arrowprops=dict(arrowstyle="<->", color=MUTED))
a1.text(1.2, (h - 2 * r) / 2, "h", fontsize=12)
a1.set_aspect("equal")
a1.set_xlim(-1.4, 1.5)
a1.axis("off")
a1.set_title(T("截面：水是液位以下的弓形", "Cross-section: water fills a circular segment"), fontsize=10)
hh = np.linspace(0, 2, 300)
frac = (np.arccos(1 - hh) - (1 - hh) * np.sqrt(np.maximum(2 * hh - hh * hh, 0))) / np.pi
a2.plot(hh / 2, frac, color=BLUE, lw=2)
a2.plot([0, 1], [0, 1], color=MUTED, lw=0.8, ls="--")
a2.set_xlabel(T("液位 h/(2r)", "level h/(2r)"))
a2.set_ylabel(T("水量占比 V/V满", "volume fraction V/V_full"))
a2.set_title(T("液位与水量不成正比", "Level and volume are not proportional"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig14_3_1")
