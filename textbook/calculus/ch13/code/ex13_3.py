"""13.3 节：原函数与不定积分——同一个函数的三个“不同”的原函数只差常数；
用 SymPy 求不定积分并求导验算；原函数不是初等函数的例子（e^{−x²}、sin x / x、1/ln x）。"""
import math

import sympy as sp

from bookout import out

# ∫ sin x cos x dx：sin²x/2、−cos²x/2、−cos 2x/4，两两之差为常数
F1 = lambda x: math.sin(x) ** 2 / 2
F2 = lambda x: -math.cos(x) ** 2 / 2
F3 = lambda x: -math.cos(2 * x) / 4
xs = [0.0, 0.7, 1.9, 3.1]
out(d12=[round(F1(x) - F2(x), 12) for x in xs], d13=[round(F1(x) - F3(x), 12) for x in xs])

x = sp.symbols("x")
items = [x ** 3 - 2 * x + 1, 1 / x, sp.exp(-x) * sp.cos(x), 1 / (1 + x ** 2), sp.exp(-x ** 2), sp.sin(x) / x, 1 / sp.log(x)]
rows = []
for f in items:
    F = sp.integrate(f, x)
    ok = sp.simplify(sp.diff(F, x) - f) == 0
    tex = lambda e: sp.latex(e).replace("\\log", "\\ln").replace("\\operatorname{atan}", "\\arctan")
    rows.append(f"| ${tex(f)}$ | ${tex(F)}$ | {'是' if ok else '否'} |")
out(sym_tab="\n".join(rows))
