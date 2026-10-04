"""图 2.5.1–2.5.3：sin x 的平移与伸缩；标准运动规律的平移与伸缩；反函数与热敏电阻。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

# 图 2.5.1
fig, axs = plt.subplots(1, 4, figsize=(13, 3.2), sharey=True)
x = np.linspace(-0.5, 2 * np.pi + 0.5, 600)
steps = [(lambda x: np.sin(2 * x), T("① 横向压缩：sin 2x", "① squeeze: sin 2x")),
         (lambda x: np.sin(2 * (x - np.pi / 6)), T("② 右移 π/6：sin(2x − π/3)", "② right π/6: sin(2x − π/3)")),
         (lambda x: 3 * np.sin(2 * x - np.pi / 3), T("③ 纵向伸长：3 sin(2x − π/3)", "③ stretch: 3 sin(2x − π/3)")),
         (lambda x: 3 * np.sin(2 * x - np.pi / 3) + 1, T("④ 上移 1", "④ up 1"))]
prev = np.sin
for a, (f, name) in zip(axs, steps):
    a.plot(x, prev(x), color=MUTED, lw=1.2, ls="--")
    a.plot(x, f(x), color=BLUE, lw=2)
    a.set_title(name, fontsize=10)
    a.set_xticks([0, np.pi, 2 * np.pi])
    a.set_xticklabels(["0", "$\\pi$", "$2\\pi$"])
    clean(a)
    prev = f
axs[1].axvline(np.pi / 6, color=RED, lw=0.8, ls=":")
axs[1].text(np.pi / 6 + 0.1, -1.6, "$\\pi/6$", color=RED)
fig.tight_layout()
figure(fig, "fig2_5_1")

# 图 2.5.2
p = lambda s: 10 * s**3 - 15 * s**4 + 6 * s**5
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.8), gridspec_kw={"width_ratios": [1, 1.8]})
s = np.linspace(0, 1, 300)
a1.plot(s, p(s), color=INK, lw=2)
a1.set_xlabel("s")
a1.set_title(T("标准运动规律 p(s)", "Standard profile p(s)"), fontsize=10)
clean(a1)
t = np.linspace(0, 4, 800)
for th0, D, t0, T_, c in ((30, 90, 1.0, 1.5, RED), (0, 90, 0.0, 2.0, MUTED), (120, -60, 2.8, 1.0, BLUE)):
    tw = t[(t >= t0 - 0.3) & (t <= t0 + T_ + 0.3)]
    a2.plot(tw, th0 + D * p(np.clip((tw - t0) / T_, 0, 1)), color=c, lw=2)
a2.text(2.1, 55, T("30° → 120°，\nt = 1 s 起，1.5 s", "30° → 120°,\nfrom t = 1 s, 1.5 s"), color=RED, fontsize=9)
a2.text(0.1, 60, T("0° → 90°，2 s", "0° → 90°, 2 s"), color=MUTED, fontsize=9)
a2.text(3.0, 125, T("120° → 60°，2.8 s 起，1 s", "120° → 60°, from 2.8 s, 1 s"), color=BLUE, fontsize=9)
a2.set_xlabel("t / s")
a2.set_ylabel("θ / (°)")
a2.set_title(T("平移与伸缩后的关节运动", "Shifted and scaled joint motions"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig2_5_2")

# 图 2.5.3
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.3))
x = np.linspace(-2.5, 1.6, 300)
a1.plot(x, np.exp(x), color=RED, lw=2, label="$e^x$")
xl = np.linspace(0.08, 4.8, 300)
a1.plot(xl, np.log(xl), color=BLUE, lw=2, label="$\\ln x$")
xc = np.linspace(-1.6, 1.6, 300)
a1.plot(xc, xc**3, color=GREEN, lw=1.5, label="$x^3$")
a1.plot(xc**3, xc, color=ACC, lw=1.5, ls="--", label="$\\sqrt[3]{x}$")
a1.plot([-2.5, 4.8], [-2.5, 4.8], color=MUTED, lw=1, ls=":")
pt = (1.0, math.e)
a1.plot([pt[0], pt[1]], [pt[1], pt[0]], color=MUTED, lw=0.8, ls="--")
a1.plot(*pt, "o", color=RED, ms=5)
a1.plot(pt[1], pt[0], "o", color=BLUE, ms=5)
a1.text(0.2, 3.0, "$(1, e)$", color=RED)
a1.text(2.75, 0.6, "$(e, 1)$", color=BLUE)
a1.set_xlim(-2.5, 4.8)
a1.set_ylim(-2.5, 4.8)
a1.set_aspect("equal")
a1.legend(fontsize=9, frameon=False, loc="lower right")
a1.set_title(T("函数与反函数关于 y = x 对称", "A function and its inverse: mirror images in y = x"), fontsize=10)
clean(a1)
a1.axvline(0, color=MUTED, lw=0.6)
R0, T0, B = 10.0, 298.15, 3950.0
Tc = np.linspace(-20, 120, 300)
R = R0 * np.exp(B * (1 / (Tc + 273.15) - 1 / T0))
a2.plot(Tc, R, color=RED, lw=2, label=T("R(T)：温度 → 电阻", "R(T): temperature → resistance"))
a2.set_xlabel(T("温度 / °C", "temperature / °C"))
a2.set_ylabel(T("电阻 / kΩ", "resistance / kΩ"))
a2.plot([41.46, 41.46], [0, 5], color=BLUE, lw=1, ls="--")
a2.plot([-20, 41.46], [5, 5], color=BLUE, lw=1, ls="--")
a2.annotate(T("测得 5 kΩ → 约 41 °C", "read 5 kΩ → about 41 °C"), xy=(41.46, 5), xytext=(55, 25),
            arrowprops=dict(arrowstyle="->", color=BLUE), color=BLUE, fontsize=10)
a2.set_ylim(0, 100)
a2.legend(fontsize=9, frameon=False)
a2.set_title(T("NTC 热敏电阻：用反函数由电阻求温度", "NTC thermistor: temperature from resistance by the inverse"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig2_5_3")
