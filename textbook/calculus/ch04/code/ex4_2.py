"""4.2 节：用极限运算法则求极限——几个算例的 SymPy 核对与数值核对；“直接代入”失败时的三种代数变形。"""
import math

import sympy as sp

from bookout import out

x, h = sp.symbols("x h")
cases = {
    "a": ((x**3 - 8) / (x - 2), 2),
    "b": ((sp.sqrt(x + 4) - 2) / x, 0),
    "c": ((1 / x - sp.Rational(1, 3)) / (x - 3), 3),
    "d": ((x**2 + 3 * x - 1) / (2 * x + 5), 1),
    "e": (x**2 * sp.sin(1 / x), 0),
}
for k, (f, a) in cases.items():
    out(**{f"lim_{k}": sp.latex(sp.limit(f, x, a))})
# 有理化在数值计算中的好处：x = 1e−12 时 (√(x + 4) − 2)/x 的两种算法
xv = 1e-12
out(direct=(math.sqrt(xv + 4) - 2) / xv, rational=1 / (math.sqrt(xv + 4) + 2))
# AGV：v̄(h) = 1 + 0.25 h
vbar = sp.simplify((sp.Rational(1, 4) * (2 + h) ** 2 - 1) / h)
out(vbar=sp.latex(vbar), vbar_lim=sp.latex(sp.limit(vbar, h, 0)))
