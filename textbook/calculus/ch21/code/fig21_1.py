"""图 21.1.1：RE 40 启动，二阶模型（计入电感）与一阶模型的转速、电流；(i, ω) 状态平面上的轨线。"""
import numpy as np
from scipy.integrate import solve_ivp

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

V, R, L, k, J = 48.0, 1.13, 0.33e-3, 60.3e-3, 137e-7
tau = R * J / k ** 2
t = np.linspace(0, 0.02, 2001)
s = solve_ivp(lambda t, y: [(V - R * y[0] - k * y[1]) / L, k * y[0] / J], (0, 0.02), [0, 0], t_eval=t, rtol=1e-10, atol=1e-10)
fig, (a1, a3) = plt.subplots(1, 2, figsize=(11, 4.0))
a1.plot(t * 1000, s.y[1], color=BLUE, lw=2, label=T("转速 ω（二阶模型）", "speed ω (2nd order)"))
a1.plot(t * 1000, V / k * (1 - np.exp(-t / tau)), color=BLUE, ls="--", lw=1.2, label=T("转速（一阶模型）", "speed (1st order)"))
a1.set_xlabel(T("时间 t / ms", "time t / ms"))
a1.set_ylabel(T("转速 / (rad/s)", "speed / (rad/s)"), color=BLUE)
b = a1.twinx()
b.plot(t * 1000, s.y[0], color=RED, lw=2, label=T("电流 i（二阶）", "current i (2nd)"))
b.plot(t * 1000, V / R * np.exp(-t / tau), color=RED, ls="--", lw=1.2)
b.set_ylabel(T("电流 / A", "current / A"), color=RED)
b.spines["top"].set_visible(False)
a1.set_title(T("RE 40 启动：电感使电流不能突变", "RE 40 start: inductance stops the current jumping"), fontsize=10)
a1.legend(fontsize=9, frameon=False, loc="center right")
clean(a1)
a3.plot(s.y[0], s.y[1], color=INK, lw=2)
for j in (5, 30, 100, 300, 1000):
    a3.annotate("", xy=(s.y[0][j + 5], s.y[1][j + 5]), xytext=(s.y[0][j], s.y[1][j]), arrowprops=dict(arrowstyle="->", color=RED, lw=1.5))
a3.plot([0], [0], "o", color=GREEN)
a3.plot([0], [V / k], "s", color=RED)
a3.text(1, V / k - 60, T("稳态 (0, V/k)", "steady state (0, V/k)"), fontsize=9, color=RED)
a3.set_xlabel(T("电流 i / A", "current i / A"))
a3.set_ylabel(T("转速 ω / (rad/s)", "speed ω / (rad/s)"))
a3.set_title(T("状态平面上的轨线", "Trajectory in the state plane"), fontsize=10)
clean(a3, zero=False)
fig.tight_layout()
figure(fig, "fig21_1_1")
