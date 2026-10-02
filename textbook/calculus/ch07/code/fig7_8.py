"""图 7.8.1：三种运动规律的角度、角速度、角加速度、加加速度；图 7.8.2：用编码器读数的二阶差商估计角加速度。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt
from _traj import cubic, quintic, trapezoid

T2, D, ta = 2.0, math.pi / 2, 0.5
t = np.linspace(-0.2, T2 + 0.2, 2401)
profiles = [(T("三次多项式", "cubic"), cubic(t, T2, D)), (T("五次多项式", "quintic"), quintic(t, T2, D)),
            (T("梯形速度", "trapezoidal"), trapezoid(t, T2, D, ta))]
names = [T("θ / (°)", "θ / (°)"), T("ω / (rad/s)", "ω / (rad/s)"), T("α / (rad/s²)", "α / (rad/s²)"), T("j / (rad/s³)", "j / (rad/s³)")]
fig, axs = plt.subplots(4, 3, figsize=(10.5, 8.0), sharex=True)
for c, (title, vals) in enumerate(profiles):
    axs[0, c].set_title(title, fontsize=12)
    for r in range(4):
        y = np.degrees(vals[0]) if r == 0 else vals[r]
        axs[r, c].plot(t, y, color=(INK, BLUE, GREEN, RED)[r], lw=1.8)
        clean(axs[r, c])
        if c == 0:
            axs[r, c].set_ylabel(names[r])
    axs[3, c].set_xlabel(T("t / s", "t / s"))
# 冲激：用竖直箭头表示
for c, pts in ((0, [(0, 1), (T2, 1)]), (2, [(0, 1), (ta, -1), (T2 - ta, -1), (T2, 1)])):
    for x0, sgn in pts:
        axs[3, c].annotate("", xy=(x0, sgn * 9), xytext=(x0, 0), arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.6))
    axs[3, c].set_ylim(-12, 12)
axs[3, 1].set_ylim(-12, 12)
axs[3, 0].text(0.25, 6, T("箭头：冲激（无穷大）", "arrows: impulses (infinite)"), color=RED, fontsize=9)
fig.tight_layout()
figure(fig, "fig7_8_1")

q = 2 * math.pi / 2**17
Ts = 0.001
tk = np.arange(0, T2 + Ts / 2, Ts)
thk = np.round(quintic(tk, T2, D)[0] / q) * q
fig, ax = plt.subplots(figsize=(7.0, 4.2))
for k, c, lw, al in ((1, "#c8ced3", 0.6, 1.0), (5, BLUE, 0.6, 0.55), (20, GREEN, 2.0, 1.0)):
    h = k * Ts
    est = (thk[2 * k:] - 2 * thk[k:-k] + thk[:-2 * k]) / h**2
    ax.plot(tk[k:-k], est, color=c, lw=lw, alpha=al, label=T(f"h = {k} ms", f"h = {k} ms"))
ax.plot(tk, quintic(tk, T2, D)[2], color=RED, lw=1.4, ls="--", label=T("真值", "exact"), zorder=5)
ax.set_ylim(-8, 8)
ax.set_xlabel(T("时间 t / s", "time t / s"))
ax.set_ylabel(T("角加速度 / (rad/s²)", "angular acceleration / (rad/s²)"))
ax.legend(frameon=False, ncol=4, fontsize=9, loc="upper right")
clean(ax)
ax.set_title(T("步长太小，量化误差被放大；步长适中，估计贴近真值", "Too small a step magnifies quantization; a moderate step tracks the truth"), fontsize=11)
fig.tight_layout()
figure(fig, "fig7_8_2")
