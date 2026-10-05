"""13.4 节：基本积分表——逐条求导验算表 13.4.1；用积分表算几个定积分并与数值积分比较；
正弦的平方的平均值 1/2（交流电的有效值）；AGV 匀加速段的牵引能量。"""
import math

import sympy as sp

from bookout import out

x, a = sp.symbols("x a", positive=True)
table = [
    (x ** a, x ** (a + 1) / (a + 1)),
    (1 / x, sp.log(x)),
    (sp.exp(x), sp.exp(x)),
    (a ** x, a ** x / sp.log(a)),
    (sp.sin(x), -sp.cos(x)),
    (sp.cos(x), sp.sin(x)),
    (1 / sp.cos(x) ** 2, sp.tan(x)),
    (1 / sp.sin(x) ** 2, -sp.cot(x)),
    (1 / (1 + x ** 2), sp.atan(x)),
    (1 / sp.sqrt(1 - x ** 2), sp.asin(x)),
    (sp.sinh(x), sp.cosh(x)),
    (sp.cosh(x), sp.sinh(x)),
]
ok = sum(1 for f, F in table if sp.simplify(sp.diff(F, x) - f) == 0)
out(n_table=len(table), n_ok=ok)


def mid(f, a, b, n=200000):
    h = (b - a) / n
    return sum(f(a + (k + 0.5) * h) for k in range(n)) * h


out(sin2_mean=mid(lambda t: math.sin(t) ** 2, 0, 2 * math.pi) / (2 * math.pi),
    asin_half=mid(lambda t: 1 / math.sqrt(1 - t * t), 0, 0.5), pi6=math.pi / 6,
    sec2=mid(lambda t: 1 / math.cos(t) ** 2, 0, math.pi / 4),
    e1=mid(lambda t: (t ** 0.5 + 1 / t), 1, 4), e1x=2 / 3 * (8 - 1) + math.log(4))
