"""图 16.5.1：左：旋转曲面面积的推导——一小段弧绕轴旋转扫出一条窄带，近似为圆台的侧面 2π f(x) ds；
右：服务机器人外壳（圆柱 + 半椭球顶），由轮廓线绕竖直轴旋转而成。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig = plt.figure(figsize=(11, 4.6))
a1 = fig.add_subplot(1, 2, 1)
f = lambda x: 0.5 + 0.35 * np.sin(1.4 * x) + 0.3 * x
x = np.linspace(0, 2.4, 300)
a1.plot(x, f(x), color=BLUE, lw=2)
a1.plot(x, -f(x), color=BLUE, lw=1, ls="--")
x0, dx = 1.2, 0.25
for xx in (x0, x0 + dx):
    a1.add_patch(plt.matplotlib.patches.Ellipse((xx, 0), 0.3 * f(xx), 2 * f(xx), fill=False, ec=RED, lw=1.4))
a1.fill_between([x0, x0 + dx], [f(x0), f(x0 + dx)], [-f(x0), -f(x0 + dx)], color=RED, alpha=0.18)
a1.plot([x0, x0 + dx], [f(x0), f(x0 + dx)], color=RED, lw=3)
a1.annotate(T("弧长 ds，半径 f(x)\n窄带面积 ≈ 2π f(x) ds", "arc ds at radius f(x)\nband area ≈ 2π f(x) ds"), (x0 + dx / 2, (f(x0) + f(x0 + dx)) / 2), (0.1, 1.75), fontsize=9,
            arrowprops=dict(arrowstyle="->", color=INK))
a1.axhline(0, color=INK, lw=1)
a1.set_xlim(-0.2, 2.6)
a1.set_ylim(-1.7, 2.3)
a1.set_aspect("equal")
a1.set_xlabel("x")
a1.set_title(T("一小段弧旋转扫出的窄带近似为圆台侧面", "A short arc sweeps a band ≈ a frustum's side"), fontsize=10)
clean(a1, zero=False)
ax = fig.add_subplot(1, 2, 2, projection="3d")
R, H, c = 150.0, 400.0, 100.0
t = np.linspace(0, np.pi / 2, 30)
prof_r = np.concatenate([np.full(20, R), R * np.cos(t)])
prof_z = np.concatenate([np.linspace(0, H, 20), H + c * np.sin(t)])
th = np.linspace(0, 2 * np.pi, 60)
TH, PR = np.meshgrid(th, prof_r)
_, PZ = np.meshgrid(th, prof_z)
ax.plot_surface(PR * np.cos(TH), PR * np.sin(TH), PZ, color=BLUE, alpha=0.35, linewidth=0.2, edgecolor=BLUE)
ax.plot(prof_r, np.zeros_like(prof_r), prof_z, color=RED, lw=2.5)
ax.plot([0, 0], [0, 0], [0, H + c + 60], color=INK, lw=1, ls="--")
ax.set_box_aspect((1, 1, 1.6))
ax.set_axis_off()
ax.view_init(elev=15, azim=-60)
ax.set_title(T("外壳：红色轮廓线绕竖直轴旋转（R = 150 mm，H = 400 mm，顶高 100 mm）",
               "Housing: the red profile revolved about the vertical axis"), fontsize=10)
fig.tight_layout()
figure(fig, "fig16_5_1")
