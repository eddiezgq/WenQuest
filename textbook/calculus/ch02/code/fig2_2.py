"""图 2.2.1：肩关节角 θ(t) 的图像与控制器的记录。"""
import numpy as np

from _fig import BLUE, INK, MUTED, RED, T, clean, figure, plt

th = lambda t: 90 * (10 * (t / 2) ** 3 - 15 * (t / 2) ** 4 + 6 * (t / 2) ** 5)
fig, ax = plt.subplots(figsize=(7.5, 4))
t = np.linspace(0, 2, 400)
ax.plot(t, th(t), color=INK, lw=2, label=T("公式 θ(t) 的图像", "graph of the formula θ(t)"))
tk = np.arange(0, 2.01, 0.25)
ax.plot(tk, th(tk), "o", color=RED, ms=6, label=T("控制器每 0.25 s 的记录", "controller log every 0.25 s"))
ax.plot(tk, th(tk), color=BLUE, lw=1, ls="--", label=T("记录之间的线性插值", "linear interpolation"))
ax.plot([1], [45], "s", color=MUTED)
ax.text(1.05, 40, T("中点 (1, 45)：曲线关于它对称", "midpoint (1, 45): centre of symmetry"), fontsize=10, color=MUTED)
ax.text(0.05, 80, T("“2 s 内由 0° 平稳转到 90°，\n起止时刻速度、加速度为零”", "'From 0° to 90° in 2 s, smoothly;\nzero speed and acceleration at both ends'"), fontsize=10)
ax.set_xlabel(T("t / s", "t / s"))
ax.set_ylabel(T("θ / (°)", "θ / (°)"))
ax.legend(loc="lower right", fontsize=9, frameon=False)
clean(ax)
fig.tight_layout()
figure(fig, "fig2_2_1")
