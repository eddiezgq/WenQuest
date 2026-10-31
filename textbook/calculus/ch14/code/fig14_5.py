"""图 14.5.1：转速有波动的关节 ω = ω₀(1 + ε cos θ)。左：转角随时间的变化（ε = 0、0.3、0.5），波动越大，转一圈越慢；
右：转一圈的时间随 ε 的变化 T = T₀/√(1 − ε²)。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

w0 = 2 * np.pi
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
th = np.linspace(0, 2 * np.pi, 2000)
for eps, c in ((0.0, INK), (0.3, BLUE), (0.5, RED)):
    dt = 1 / (w0 * (1 + eps * np.cos(th)))
    t = np.concatenate([[0], np.cumsum((dt[1:] + dt[:-1]) / 2 * np.diff(th))])
    a1.plot(t, np.degrees(th), color=c, lw=2, label=f"ε = {eps:g}")
a1.set_xlabel("t / s")
a1.set_ylabel(T("转角 / (°)", "angle / (°)"))
a1.legend(fontsize=9, frameon=False)
a1.set_title(T("快的地方走得快，慢的地方耽误得更多", "Slow stretches cost more time than fast ones save"), fontsize=10)
clean(a1, zero=False)
e = np.linspace(0, 0.8, 200)
a2.plot(e, 1 / np.sqrt(1 - e * e), color=BLUE, lw=2)
a2.set_xlabel("ε")
a2.set_ylabel("T / T₀")
a2.set_title(T("T = T₀/√(1 − ε²)", "T = T₀/√(1 − ε²)"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig14_5_1")
