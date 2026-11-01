"""图 19.2.1：左：y′ = x − y 的方向场与几条积分曲线，等倾线 y = x − 1 本身是积分曲线；
右：带风扇负载的 RE 40 电机，上：f(ω) 与平衡点；下：从不同初值出发的转速曲线都趋于 ω*。"""
import numpy as np
from scipy.integrate import solve_ivp

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig = plt.figure(figsize=(11, 4.6))
a1 = fig.add_subplot(1, 2, 1)
X, Y = np.meshgrid(np.linspace(-1, 4, 21), np.linspace(-2, 4, 25))
S = X - Y
L = np.sqrt(1 + S * S)
a1.quiver(X, Y, 1 / L, S / L, angles="xy", color=MUTED, headwidth=0, headlength=0, headaxislength=0, pivot="mid", scale=40, width=0.003)
x = np.linspace(-1, 4, 300)
for C, col in ((-3, BLUE), (-1.5, BLUE), (1.5, GREEN), (4, GREEN), (8, GREEN)):
    a1.plot(x, x - 1 + C * np.exp(-x), color=col, lw=1.6)
a1.plot(x, x - 1, color=RED, lw=2.4, label=T("y = x − 1（等倾线 c = 1，也是积分曲线）", "y = x − 1 (isocline c = 1, also a solution)"))
a1.set_xlim(-1, 4)
a1.set_ylim(-2, 4)
a1.set_xlabel("x")
a1.set_ylabel("y")
a1.legend(fontsize=8.5, frameon=True, facecolor="white", edgecolor="white", framealpha=0.95, loc="upper left")
a1.set_title(T("y′ = x − y 的方向场与积分曲线", "Direction field and solutions of y′ = x − y"), fontsize=10)
R, k, J, V, cf = 1.13, 60.3e-3, 137e-7, 48.0, 3.3e-7
tau, wi = R * J / k ** 2, V / k
f = lambda w: (wi - w) / tau - cf / J * w * w
ws = (-k * k / R + np.sqrt((k * k / R) ** 2 + 4 * cf * k * k / R * wi)) / (2 * cf)
a2 = fig.add_subplot(2, 2, 2)
w = np.linspace(0, 950, 400)
a2.plot(w, f(w) / 1000, color=BLUE, lw=2)
a2.axhline(0, color=MUTED, lw=0.8)
a2.plot([ws], [0], "o", color=RED)
a2.annotate("", xy=(ws - 60, 8), xytext=(150, 8), arrowprops=dict(arrowstyle="->", color=GREEN, lw=1.5))
a2.annotate("", xy=(ws + 40, -8), xytext=(930, -8), arrowprops=dict(arrowstyle="->", color=GREEN, lw=1.5))
a2.text(ws, 25, "ω* ≈ 740", color=RED, fontsize=9, ha="center")
a2.set_xlabel("ω / (rad/s)", fontsize=9, labelpad=1)
a2.set_ylabel(T("f(ω) / (10³ rad/s²)", "f(ω) / (10³ rad/s²)"), fontsize=9)
a2.set_title(T("电机带风扇：f(ω) 的零点是稳态转速，f′(ω*) < 0，稳定", "Motor with fan: the zero of f is the steady speed; f′(ω*) < 0, stable"), fontsize=10)
for s_ in ("top", "right"):
    a2.spines[s_].set_visible(False)
a3 = fig.add_subplot(2, 2, 4)
for w0 in (0, 300, 900, 1100):
    s = solve_ivp(lambda t, y: f(y), (0, 0.02), [w0], max_step=1e-4)
    a3.plot(s.t * 1000, s.y[0], color=BLUE if w0 < ws else ACC, lw=1.5)
a3.axhline(ws, color=RED, ls="--", lw=1)
a3.set_xlabel(T("时间 t / ms", "time t / ms"))
a3.set_ylabel(T("ω / (rad/s)", "ω / (rad/s)"), fontsize=9)
clean(a3, zero=False)
fig.tight_layout()
figure(fig, "fig19_2_1")
