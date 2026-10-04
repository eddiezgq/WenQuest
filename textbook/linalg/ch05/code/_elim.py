"""本章共用（取自第 3 章）：用分数精确地做消元；化为简化行阶梯形。以下划线开头，构建时不单独运行。"""
from fractions import Fraction


def F(M):
    return [[Fraction(x) for x in row] for row in M]


def fstr(x):
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def tex_frac(x):
    x = Fraction(x)
    if x.denominator == 1:
        return str(x.numerator)
    s = "-" if x < 0 else ""
    return f"{s}\\tfrac{{{abs(x.numerator)}}}{{{x.denominator}}}"


def tex_aug(M, ncoef=None, env="pmatrix"):
    """增广矩阵写成 LaTeX，系数与右端之间画竖线（ncoef = 系数列数）。"""
    n = len(M[0])
    k = ncoef if ncoef is not None else n - 1
    spec = "c" * k + "|" + "c" * (n - k)
    rows = " \\\\ ".join(" & ".join(tex_frac(x) for x in r) for r in M)
    return f"\\left(\\begin{{array}}{{{spec}}} {rows} \\end{{array}}\\right)"


def forward(M):
    """不交换行的前向消元（主元为零时交换到下方第一个非零行）。返回各步（说明，矩阵）与乘数。"""
    A = F(M)
    m, n = len(A), len(A[0])
    steps, mult, r = [], {}, 0
    for c in range(n - 1):
        if r >= m:
            break
        p = next((i for i in range(r, m) if A[i][c] != 0), None)
        if p is None:
            continue
        if p != r:
            A[r], A[p] = A[p], A[r]
            steps.append((f"交换第 {r + 1}、{p + 1} 行", [row[:] for row in A]))
        for i in range(r + 1, m):
            if A[i][c] != 0:
                l = A[i][c] / A[r][c]
                mult[(i + 1, r + 1)] = l
                A[i] = [a - l * b for a, b in zip(A[i], A[r])]
                steps.append((f"第 {i + 1} 行减去第 {r + 1} 行的 {fstr(l)} 倍", [row[:] for row in A]))
        r += 1
    return A, steps, mult


def rref(M, ncols=None):
    """化为简化行阶梯形。ncols：只在前 ncols 列找主元（增广矩阵传系数列数）。返回 (R, 主元列)。"""
    A = F(M)
    m, n = len(A), len(A[0])
    nc = n if ncols is None else ncols
    piv, r = [], 0
    for c in range(nc):
        p = next((i for i in range(r, m) if A[i][c] != 0), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        A[r] = [x / A[r][c] for x in A[r]]
        for i in range(m):
            if i != r and A[i][c] != 0:
                l = A[i][c]
                A[i] = [a - l * b for a, b in zip(A[i], A[r])]
        piv.append(c)
        r += 1
        if r == m:
            break
    return A, piv


def count_ops(n):
    """对 n×n 方程组（带一个右端列）做不选主元的高斯消元和回代，逐次数出乘除法与加减法。"""
    mul = add = 0
    for k in range(n - 1):                 # 消去第 k 列
        for i in range(k + 1, n):
            mul += 1                       # 乘数 l = a_ik / a_kk
            mul += (n - k - 1) + 1         # 第 k+1 … n 列和右端各一次乘法
            add += (n - k - 1) + 1         # 同样多次减法
    for i in range(n - 1, -1, -1):         # 回代
        mul += (n - 1 - i) + 1             # 乘法 + 一次除法
        add += (n - 1 - i)
    return mul, add
