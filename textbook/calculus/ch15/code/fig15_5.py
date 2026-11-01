"""图 15.5.1：左：∫₁^T x^{−p} dx 随 T 的增长，p = 2 趋于 1、p = 1 无限增长（对数）；右：关节阻尼制动时，耗散的能量随时间累积，
趋于初始动能 1 J，约 5.8 s 时达到 99%。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
Tt = np.logspace(0, 4, 300)
a1.semilogx(Tt, np.log(Tt), color=RED, lw=2, label=T("p = 1：ln T，无界", "p = 1: ln T, unbounded"))
a1.semilogx(Tt, 1 - 1 / Tt, color=BLUE, lw=2, label=T("p = 2：1 − 1/T → 1", "p = 2: 1 − 1/T → 1"))
a1.axhline(1, color=BLUE, lw=0.8, ls="--")
a1.set_xlabel("T")
a1.set_ylabel(r"$\int_1^T x^{-p}\,dx$")
a1.legend(fontsize=9, frameon=False)
a1.set_title(T("尾巴下降得够快，面积才有限", "Finite area needs a fast-decaying tail"), fontsize=10)
clean(a1, zero=False)
J, b, w0 = 0.5, 0.2, 2.0
tau = J / b
t = np.linspace(0, 15, 400)
E = 0.5 * J * w0 * w0 * (1 - np.exp(-2 * t / tau))
a2.plot(t, E, color=GREEN, lw=2)
a2.axhline(1.0, color=MUTED, lw=0.8, ls="--")
a2.axvline(tau / 2 * np.log(100), color=RED, lw=0.8, ls="--")
a2.set_xlabel("t / s")
a2.set_ylabel(T("耗散能量 / J", "energy dissipated / J"))
a2.set_title(T(r"$b\int_0^t\omega^2\,d\tau$ → 初始动能", r"$b\int_0^t\omega^2\,d\tau$ → initial kinetic energy"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig15_5_1")
