"""14.6 节：积分表与计算机代数——用 SymPy 求几类典型积分并求导验算；三个常见的“坑”：
带参数的幂函数（结果是分段的）、对数的绝对值、根式开方的符号假设。"""
import sympy as sp

from bookout import out

x = sp.symbols("x")
cases = [sp.exp(2 * x) * sp.sin(3 * x), x ** 2 * sp.log(x), 1 / (x ** 3 + 1), sp.sqrt(4 - x ** 2), 1 / (2 + sp.cos(x)), x / sp.sqrt(x ** 2 + 2 * x + 5)]
rows = []
tex = lambda e: sp.latex(e).replace("\\log", "\\ln").replace("\\operatorname{atan}", "\\arctan").replace("\\operatorname{asin}", "\\arcsin").replace("\\operatorname{asinh}", "\\operatorname{arsinh}")
for f in cases:
    F = sp.integrate(f, x)
    Fn, fn = sp.lambdify(x, F, "math"), sp.lambdify(x, f, "math")
    h = 1e-5                                                      # 在几个点上用中心差商数值验算 F' = f
    ok = all(abs((Fn(v + h) - Fn(v - h)) / (2 * h) - fn(v)) < 1e-6 for v in (0.3, 1.1, 1.7))
    rows.append(f"| ${tex(f)}$ | ${tex(F)}$ | {'是' if ok else '否'} |")
out(cas_tab="\n".join(rows))
n = sp.symbols("n")
out(power=tex(sp.integrate(x ** n, x)))
# 根式：x 为实数时 √(x²) = |x|，SymPy 默认不化简；声明 x 为正后化为 x
xp = sp.symbols("x", positive=True)
out(sq_gen=str(sp.simplify(sp.sqrt(x ** 2))), sq_pos=str(sp.simplify(sp.sqrt(xp ** 2))))
out(log_def=str(sp.integrate(1 / x, (x, -2, -1))))
