"""1.6 节：Python 的第一课——数组、差分、累加；SymPy 的极限、导数、积分。"""
import numpy as np
import sympy as sp

from bookout import out

t = np.linspace(0, 2, 5)                 # 0, 0.5, 1, 1.5, 2
x = 0.25 * t**2
out(t=", ".join(f"{v:g}" for v in t), x=", ".join(f"{v:g}" for v in x),
    dx=", ".join(f"{v:g}" for v in np.diff(x)), v=", ".join(f"{v:g}" for v in np.diff(x) / np.diff(t)))
# 浮点数：0.1 + 0.2 不等于 0.3
out(f01=repr(0.1 + 0.2), eq=str(0.1 + 0.2 == 0.3), close=str(bool(np.isclose(0.1 + 0.2, 0.3))))
# SymPy
ts = sp.symbols("t")
lim = sp.limit(sp.sin(ts) / ts, ts, 0)
d = sp.diff(sp.Rational(1, 4) * ts**2, ts)
I = sp.integrate(ts**2, (ts, 0, 1))
out(lim=str(lim), deriv=sp.latex(d), integral=str(I))
import math
out(sin30=repr(math.sin(math.pi / 6)))
