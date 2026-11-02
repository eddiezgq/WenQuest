"""图 22.2.1：UR5e 上臂自由下摆 2 s，欧拉、休恩、RK4 的全程最大误差与函数求值次数（对数坐标）；RK4 的四个斜率示意。"""
import math

import numpy as np
from scipy.integrate import solve_ivp

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

m, d, I, g = 8.393, 0.2125, 0.5129, 9.81
c = m * g * d / I
f = lambda y: np.array([y[1], -c * math.cos(y[0])])
TT = 2.0
sol = solve_ivp(lambda t, y: f(y), (0, TT), [0.0, 0.0], method="DOP853", rtol=1e-13, atol=1e-14, dense_output=True)


def run(step, h):
    """全程（各步时刻）最大的角度误差。"""
    n = round(TT / h)
    y = np.zeros(2)
    ys = np.empty(n)
    for j in range(n):
        y = step(y, h)
        ys[j] = y[0]
    return float(np.max(np.abs(ys - sol.sol(np.arange(1, n + 1) * TT / n)[0])))


eu = lambda y, h: y + h * f(y)
def he(y, h):
    k1 = f(y); k2 = f(y + h * k1); return y + h / 2 * (k1 + k2)
def r4(y, h):
    k1 = f(y); k2 = f(y + h / 2 * k1); k3 = f(y + h / 2 * k2); k4 = f(y + h * k3)
    return y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.0))
for step, s, col, lab in ((eu, 1, RED, T("欧拉（1 阶）", "Euler (1st)")), (he, 2, GREEN, T("休恩（2 阶）", "Heun (2nd)")),
                          (r4, 4, BLUE, T("RK4（4 阶）", "RK4 (4th)"))):
    hs = TT / np.round(np.logspace(np.log10(100), np.log10(20000 if s == 1 else 4000), 9))
    hs = hs[hs <= 0.02]
    errs = [run(step, h) for h in hs]
    a1.loglog(s * TT / hs, errs, "o-", color=col, lw=2, ms=4, label=lab)
a1.axhline(1e-6, color=MUTED, ls="--", lw=1)
a1.text(130, 1.6e-6, T("目标 10⁻⁶ rad", "target 10⁻⁶ rad"), fontsize=9, color=MUTED)
a1.set_xlabel(T("函数 f 的求值次数", "evaluations of f")); a1.set_ylabel(T("0—2 s 内最大角度误差 / rad", "max angle error over 0–2 s / rad"))
a1.set_title(T("同样的计算量，高阶方法精确得多", "Same work, higher order is far more accurate"), fontsize=10)
a1.legend(fontsize=9, frameon=False); clean(a1, zero=False)
# 右：y′ = y 在 [0, h] 上一步 RK4 的四个斜率
h = 1.0
xs = np.linspace(0, 1.05, 100)
a2.plot(xs, np.exp(xs), color=INK, lw=2, label=T("准确解 eˣ", "exact eˣ"))
k1 = 1; k2 = 1 + h / 2 * k1; k3 = 1 + h / 2 * k2; k4 = 1 + h * k3
for x0, y0, k, lab, col in ((0, 1, k1, "k₁", RED), (0.5, 1 + 0.5 * k1, k2, "k₂", GREEN), (0.5, 1 + 0.5 * k2, k3, "k₃", ACC), (1, 1 + k3, k4, "k₄", BLUE)):
    a2.plot([x0 - 0.15, x0 + 0.15], [y0 - 0.15 * k, y0 + 0.15 * k], color=col, lw=2.5)
    a2.plot([x0], [y0], "o", color=col, ms=5)
    a2.text(x0 + 0.05, y0 - 0.22, f"{lab} = {k:.3g}", color=col, fontsize=9)
y1 = 1 + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
a2.plot([0, 1], [1, y1], ":", color=BLUE, lw=1.5)
a2.plot([1], [y1], "*", color=BLUE, ms=12)
a2.text(0.55, 2.75, T(f"RK4 一步：{y1:.4f}\n准确值 e = {math.e:.4f}", f"one RK4 step: {y1:.4f}\nexact e = {math.e:.4f}"), fontsize=9)
a2.set_xlabel("x"); a2.set_ylabel("y")
a2.set_title(T("RK4 的四个斜率（y′ = y，h = 1）", "The four RK4 slopes (y′ = y, h = 1)"), fontsize=10)
a2.legend(fontsize=9, frameon=False, loc="upper left"); clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig22_2_1")
