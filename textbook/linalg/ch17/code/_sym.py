"""本章共用：把 SymPy 的矩阵、多项式写成 LaTeX（整数与分数精确显示）。以下划线开头，构建时不单独运行。"""
import sympy as sp


def stex(M):
    """SymPy 矩阵或表达式 → LaTeX（pmatrix）。"""
    s = sp.latex(M, mat_delim="(", mat_str="matrix")
    return s.replace(r"\left(\begin{matrix}", r"\begin{pmatrix}").replace(r"\end{matrix}\right)", r"\end{pmatrix}")


def ptex(p, x=sp.Symbol("lambda")):
    """多项式因式分解后的 LaTeX，例如 (λ − 2)^3 (λ + 1)。"""
    return sp.latex(sp.factor(p))
