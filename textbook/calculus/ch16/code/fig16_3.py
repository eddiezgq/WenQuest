"""图 16.3.1：左：圆盘法——曲线 y = f(x) 下方的区域绕 x 轴旋转，垂直于轴的薄片是圆盘，体积元 π f(x)² dx；
右：柱壳法——区域绕 y 轴旋转，平行于轴的竖条扫出薄圆筒，体积元 2πx f(x) dx。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.4))
f = lambda x: 0.6 + 0.5 * np.sqrt(x)
x = np.linspace(0, 3, 300)
a1.plot(x, f(x), color=BLUE, lw=2)
a1.plot(x, -f(x), color=BLUE, lw=1, ls="--")
for x0 in (0, 3):
    a1.add_patch(plt.matplotlib.patches.Ellipse((x0, 0), 0.35 * f(x0), 2 * f(x0), fill=False, ec=BLUE, lw=1, ls="--"))
x0, dx = 1.8, 0.18
a1.add_patch(plt.matplotlib.patches.Ellipse((x0, 0), 0.35 * f(x0), 2 * f(x0), color=RED, alpha=0.35))
a1.add_patch(plt.matplotlib.patches.Ellipse((x0 + dx, 0), 0.35 * f(x0), 2 * f(x0), color=RED, alpha=0.55))
a1.fill_between(x, 0, f(x), color=BLUE, alpha=0.12)
a1.annotate(T("厚 dx 的圆盘\n半径 f(x)", "disk of thickness dx\nradius f(x)"), (x0 + dx, f(x0)), (2.2, 1.9), fontsize=9, arrowprops=dict(arrowstyle="->", color=INK))
a1.axhline(0, color=INK, lw=1)
a1.set_xlim(-0.3, 3.4)
a1.set_ylim(-1.8, 2.3)
a1.set_xlabel("x")
a1.set_title(T("圆盘法：绕 x 轴，dV = π f(x)² dx", "Disks: about the x-axis, dV = π f(x)² dx"), fontsize=10)
a1.set_aspect("equal")
clean(a1, zero=False)
g = lambda x: x * (2 - x)
x = np.linspace(0, 2, 300)
a2.fill_between(x, 0, g(x), color=GREEN, alpha=0.18)
a2.plot(x, g(x), color=GREEN, lw=2)
a2.plot(-x, g(x), color=GREEN, lw=1, ls="--")
xs, w = 1.3, 0.12
a2.add_patch(plt.Rectangle((xs, 0), w, g(xs), color=RED, alpha=0.55))
a2.add_patch(plt.Rectangle((-xs - w, 0), w, g(xs), color=RED, alpha=0.25))
for yy in (0, g(xs)):
    a2.add_patch(plt.matplotlib.patches.Ellipse((0, yy), 2 * xs + w, 0.35, fill=False, ec=RED, lw=1))
a2.annotate(T("半径 x、高 f(x)、厚 dx 的薄圆筒", "thin shell: radius x, height f(x), thickness dx"), (xs + w, g(xs) * 0.6), (1.3, 1.35), fontsize=9, arrowprops=dict(arrowstyle="->", color=INK))
a2.axvline(0, color=INK, lw=1)
a2.axhline(0, color=MUTED, lw=0.6)
a2.set_xlim(-2.3, 2.6)
a2.set_ylim(-0.4, 1.6)
a2.set_xlabel("x")
a2.set_title(T("柱壳法：绕 y 轴，dV = 2πx f(x) dx", "Shells: about the y-axis, dV = 2πx f(x) dx"), fontsize=10)
a2.set_aspect("equal")
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig16_3_1")
