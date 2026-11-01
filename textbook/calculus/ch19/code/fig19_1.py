"""图 19.1.1：左：RE 40 电机由 (19.1.1) 得到的转速曲线（τ = RJ/k²），t = τ 处 63.2%；
右：排水方程 h′ = −c√h 的几条解曲线：不同时刻流空，此后都与 h = 0 重合。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.0))
R, k, J, V = 1.13, 60.3e-3, 137e-7, 48.0
tau, w_inf = R * J / k ** 2, V / k
t = np.linspace(0, 25e-3, 400)
a1.plot(t * 1000, w_inf * (1 - np.exp(-t / tau)), color=BLUE, lw=2, label=T("ω(t) = ω∞(1 − e^(−t/τ))", "ω(t) = ω∞(1 − e^(−t/τ))"))
a1.plot([0, tau * 1000], [0, w_inf], color=MUTED, ls="--", lw=1)
a1.axhline(w_inf, color=MUTED, ls=":", lw=1)
a1.plot([tau * 1000], [w_inf * (1 - np.exp(-1))], "o", color=RED)
a1.annotate(T("t = τ ≈ 4.26 ms，63.2%", "t = τ ≈ 4.26 ms, 63.2%"), (tau * 1000, w_inf * 0.632), xytext=(8, 380), fontsize=9, color=RED,
            arrowprops=dict(arrowstyle="->", color=RED, lw=0.8))
a1.set_xlabel(T("时间 t / ms", "time t / ms"))
a1.set_ylabel(T("转速 ω / (rad/s)", "speed ω / (rad/s)"))
a1.set_title(T("maxon RE 40（48 V）空载启动", "maxon RE 40 (48 V), no-load start"), fontsize=10)
a1.legend(fontsize=9, frameon=False, loc="lower right")
clean(a1)
c = 0.6 * np.pi * 4e-3 ** 2 / 4 * np.sqrt(2 * 9.81) / 0.03
for t1, col in ((0, RED), (-150, ACC), (-300, GREEN), (-450, BLUE)):
    tt = np.linspace(-900, 200, 600)
    h = np.where(tt < t1, c * c / 4 * (t1 - tt) ** 2, 0.0)
    a2.plot(tt, h * 100, color=col, lw=2 if t1 == 0 else 1.5)
a2.axvline(0, color=INK, lw=0.8, ls="--")
a2.text(10, 22, T("现在：h = 0", "now: h = 0"), fontsize=9)
a2.set_ylim(-1, 26)
a2.set_xlabel(T("时间 t / s", "time t / s"))
a2.set_ylabel(T("水深 h / cm", "depth h / cm"))
a2.set_title(T("h′ = −c√h：流空的时刻无法由“现在是空的”确定", "h′ = −c√h: 'empty now' does not tell when it emptied"), fontsize=10)
clean(a2)
fig.tight_layout()
figure(fig, "fig19_1_1")
