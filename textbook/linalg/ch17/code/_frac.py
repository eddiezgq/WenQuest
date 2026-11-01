"""本章共用：把有理数向量、矩阵写成带分数的 LaTeX。以下划线开头，构建时不单独运行。"""
from fractions import Fraction

import numpy as np

from _elim import tex_frac


def fr(x, den=1000):
    return Fraction(float(x)).limit_denominator(den)


def fvec(v, den=1000):
    """(a, b, …)^T，分量写成分数。"""
    return "(" + ",\\ ".join(tex_frac(fr(x, den)) for x in v) + ")^{\\mathsf T}"


def fmat(M, den=1000):
    M = np.atleast_2d(np.asarray(M, dtype=float))
    rows = " \\\\ ".join(" & ".join(tex_frac(fr(x, den)) for x in r) for r in M)
    return f"\\begin{{pmatrix}} {rows} \\end{{pmatrix}}"
