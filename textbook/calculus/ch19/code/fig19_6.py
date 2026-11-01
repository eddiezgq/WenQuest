"""图 19.6.1：左：欧拉法解 y′ = x − y、y(0) = 2（步长 0.5、0.25、0.1）与准确解；
右：欧拉法仿真 RE 40 空载启动（τ ≈ 4.26 ms），步长 1 ms、5 ms、10 ms。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.0))
x = np.linspace(0, 2, 300)
a1.plot(x, x - 1 + 3 * np.exp(-x), color=INK, lw=2.4, label=T("准确解", "exact"))
for h, col in ((0.5, RED), (0.25, ACC), (0.1, BLUE)):
    xs, ys = [0.0], [2.0]
    while xs[-1] < 2 - 1e-9:
        ys.append(ys[-1] + h * (xs[-1] - ys[-1]))
        xs.append(xs[-1] + h)
    a1.plot(xs, ys, "o-", color=col, lw=1.4, ms=3.5, label=f"h = {h:g}")
a1.set_xlabel("x")
a1.set_ylabel("y")
a1.set_title(T("欧拉折线：步长越小越接近准确解", "Euler polygons approach the exact solution"), fontsize=10)
a1.legend(fontsize=9, frameon=False)
clean(a1)
tau, wi = 1.13 * 137e-7 / 60.3e-3 ** 2 * 1000, 48 / 60.3e-3
t = np.linspace(0, 40, 400)
a2.plot(t, wi * (1 - np.exp(-t / tau)), color=INK, lw=2.4, label=T("准确解", "exact"))
for h, col in ((1.0, BLUE), (5.0, ACC), (10.0, RED)):
    ts, ws = [0.0], [0.0]
    while ts[-1] < 40 - 1e-9:
        ws.append(ws[-1] + h * (wi - ws[-1]) / tau)
        ts.append(ts[-1] + h)
    a2.plot(ts, ws, "o-", color=col, lw=1.4, ms=3.5, label=f"h = {h:g} ms")
a2.set_ylim(-1500, 3000)
a2.set_xlabel(T("时间 t / ms", "time t / ms"))
a2.set_ylabel(T("转速 / (rad/s)", "speed / (rad/s)"))
a2.set_title(T("电机启动（τ ≈ 4.26 ms）：h > 2τ 时欧拉法发散", "Motor start (τ ≈ 4.26 ms): Euler diverges for h > 2τ"), fontsize=10)
a2.legend(fontsize=9, frameon=True, facecolor="white", edgecolor="white", loc="lower right")
clean(a2)
fig.tight_layout()
figure(fig, "fig19_6_1")
