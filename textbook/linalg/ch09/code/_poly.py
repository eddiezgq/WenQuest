"""本章共用：多项式用系数向量 (a0, a1, …, an) 表示（p(x) = a0 + a1 x + … + an xⁿ）；求导、积分、在点上取值。以下划线开头，构建时不单独运行。"""
import numpy as np


def D(p):
    """求导：(a0, a1, …, an) → (a1, 2a2, …, n an, 0)，结果仍在 P_n 中。"""
    p = np.asarray(p, dtype=float)
    return np.r_[p[1:] * np.arange(1, len(p)), 0.0]


def I(p):
    """从 0 积分：(a0, …, an) → (0, a0, a1/2, …, an/(n + 1))，结果在 P_{n+1} 中。"""
    p = np.asarray(p, dtype=float)
    return np.r_[0.0, p / np.arange(1, len(p) + 1)]


def ev(p, x):
    return float(np.polynomial.polynomial.polyval(x, p))


def matrix(T, n_in, n_out=None):
    """线性映射 T 在标准基 1, x, x², … 下的矩阵：第 j 列是 T(x^j) 的系数。"""
    cols = []
    for j in range(n_in):
        e = np.zeros(n_in)
        e[j] = 1
        cols.append(np.asarray(T(e), dtype=float))
    return np.column_stack(cols)


def ptex(p, var="x"):
    """系数向量写成多项式的 LaTeX，如 2 - x + 3x^{2}。"""
    from fractions import Fraction
    from _elim import tex_frac
    terms = []
    for k, a in enumerate(p):
        if abs(a) < 1e-12:
            continue
        mag = tex_frac(Fraction(abs(float(a))).limit_denominator(1000))
        mon = "" if k == 0 else (var if k == 1 else f"{var}^{{{k}}}")
        coef = mag if (k == 0 or mag != "1") else ""
        s = coef + mon
        terms.append(("-" if a < 0 else "+", s))
    if not terms:
        return "0"
    out = ("-" if terms[0][0] == "-" else "") + terms[0][1]
    for sg, s in terms[1:]:
        out += f" {sg} {s}"
    return out


def ftex(M):
    """有理数矩阵写成 LaTeX（分数用 \\tfrac）。"""
    from fractions import Fraction
    from _elim import tex_frac
    M = np.atleast_2d(np.asarray(M, dtype=float))
    rows = " \\\\ ".join(" & ".join(tex_frac(Fraction(float(x)).limit_denominator(1000)) for x in r) for r in M)
    return f"\\begin{{pmatrix}} {rows} \\end{{pmatrix}}"
