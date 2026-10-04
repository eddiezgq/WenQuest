"""图 6.1.1：有理数挤向 √2——数轴上分母不超过 12 的有理数，以及 √2 的渐近分数的误差 ≈ 0.354/q²。"""
import math
from fractions import Fraction

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

r2 = math.sqrt(2)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.8), gridspec_kw={"width_ratios": [1.3, 1]})
fr = sorted({Fraction(p, q) for q in range(1, 13) for p in range(q, 2 * q + 1)})
for f in fr:
    a1.plot([float(f)] * 2, [0, 1 / f.denominator], color=BLUE, lw=1.2)
a1.axvline(r2, color=RED, lw=1.2, ls="--")
a1.text(r2 + 0.005, 0.9, "$\\sqrt{2}$", color=RED)
for f in (Fraction(7, 5), Fraction(17, 12), Fraction(3, 2), Fraction(4, 3)):
    a1.text(float(f), 1 / f.denominator + 0.03, f"{f.numerator}/{f.denominator}", ha="center", fontsize=9)
a1.set_xlim(1.3, 1.55)
a1.set_ylim(0, 1.0)
a1.set_xlabel(T("有理数 p/q（竖线高度 1/q）", "rationals p/q (bar height 1/q)"))
a1.set_yticks([])
a1.set_title(T("分母越大，有理数越密，但永远落不到 √2 上", "Larger denominators fill in, yet never land on √2"), fontsize=10)
clean(a1, zero=False)
h0, h1, k0, k1, y = 0, 1, 1, 0, r2
qs, es = [], []
for _ in range(12):
    a = math.floor(y)
    h0, h1 = h1, a * h1 + h0
    k0, k1 = k1, a * k1 + k0
    qs.append(k1)
    es.append(abs(h1 / k1 - r2))
    y = 1 / (y - a)
q = np.array(qs[1:], float)
a2.loglog(q, es[1:], "o", color=BLUE, label=T("渐近分数的误差", "error of convergents"))
a2.loglog(q, 0.3536 / q ** 2, color=RED, lw=1, label="$1/(2\\sqrt{2}\\,q^2)$")
a2.set_xlabel(T("分母 q", "denominator q"))
a2.set_ylabel(T("|p/q − √2|", "|p/q − √2|"))
a2.legend(fontsize=9, frameon=False)
a2.set_title(T("最佳逼近：误差约与 1/q² 成正比", "Best approximations: error ∝ 1/q²"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig6_1_1")
