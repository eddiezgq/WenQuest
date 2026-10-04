"""4.7 节：用计算机求极限的陷阱——机器精度与浮点数的间隔；(1 − cos x)/x² 与 (eˣ − 1)/x 的相消及其改写；
求根公式的相消；差速 AGV 里程计 Δy 的相消；“爱国者”导弹的计时误差。"""
import math
from fractions import Fraction

import numpy as np

from bookout import out


def sci(v):
    if v == 0:
        return "0"
    m, e = f"{v:.2e}".split("e")
    return f"${m}\\times 10^{{{int(e)}}}$"


eps = np.finfo(float).eps
out(eps=eps, sp1=float(np.spacing(1.0)), sp1e8=float(np.spacing(1e8)), sp1e16=float(np.spacing(1e16)),
    one_plus=1.0 + eps / 2 == 1.0, big=1e16 + 1 == 1e16)

# (1 − cos x)/x² 的两种算法与 (eˣ − 1)/x 的两种算法，真值用高阶泰勒多项式（x ≤ 0.1 时误差远小于 1e−16）
true_c = lambda x: 0.5 - x * x / 24 + x**4 / 720 - x**6 / 40320 + x**8 / 3628800
true_e = lambda x: sum(x**k / math.factorial(k + 1) for k in range(12))
rows = []
for k in (1, 2, 4, 6, 7, 8, 9):
    x = 10.0**-k
    d = (1 - math.cos(x)) / x**2
    g = 2 * math.sin(x / 2) ** 2 / x**2
    de = (math.exp(x) - 1) / x
    ge = math.expm1(x) / x
    rows.append(f"| $10^{{-{k}}}$ | {d:.10f} | {sci(abs(d - true_c(x)) / true_c(x))} | {g:.10f} | {sci(abs(de - true_e(x)) / true_e(x))} | {sci(abs(ge - true_e(x)) / true_e(x))} |")
out(cancel_tab="\n".join(rows))
# 相对误差约为 ε/x² 的规律：x = 1e−4 时
x = 1e-4
out(err4=abs((1 - math.cos(x)) / x**2 - true_c(x)) / true_c(x), pred4=eps / x**2)

# 求根公式：x² + 2bx + c = 0，b = 1e8，c = 1（射线与碰撞球求交时常见）。小根 −b + √(b² − c)
b, c = 1e8, 1.0
naive = -b + math.sqrt(b * b - c)
stable = -c / (b + math.sqrt(b * b - c))
out(q_naive=naive, q_stable=stable, q_true=-0.5e-8)

# 差速 AGV：v = 1 m/s，T = 0.02 s，Δy = (v/ω)(1 − cos ωT)，改写为 (v/ω)·2 sin²(ωT/2)
v, T = 1.0, 0.02
rows = []
for w in (1e-2, 1e-4, 1e-6, 1e-7):
    naive = v / w * (1 - math.cos(w * T))
    good = v / w * 2 * math.sin(w * T / 2) ** 2
    true = v * w * T * T / 2 * (1 - (w * T) ** 2 / 12)
    rows.append(f"| $10^{{{round(math.log10(w))}}}$ | {sci(naive)} | {sci(good)} | {sci(abs(naive - true) / true)} |")
out(odo_tab="\n".join(rows))

# “爱国者”导弹：0.1 s 在 24 位定点寄存器中截断（小数点后 23 位），每次计时的误差
tick = Fraction(1, 10)
stored = Fraction(math.floor(tick * 2**23), 2**23)
per = float(tick - stored)
ticks = 100 * 3600 * 10
out(pat_per=per, pat_err=per * ticks, pat_dist=per * ticks * 1676)

# 计算器的例子：√(10¹⁰ + 1) − 10⁵
out(calc_sqrt=f"{math.sqrt(1e10 + 1):.6f}", calc_true=1 / (math.sqrt(1e10 + 1) + 1e5))
