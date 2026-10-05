"""8.1 节：列空间与零空间——由简化行阶梯形读出主元列（列空间的基）和特殊解（零空间的基）；验证 A N = 0。"""
import numpy as np

from _a import A
from _elim import rref, tex_frac
from bookout import out, tex, vec

R, piv = rref(A.tolist())
rows = " \\\\ ".join(" & ".join(tex_frac(x) for x in r) for r in R)
out(A=tex(A, 0), R=f"\\begin{{pmatrix}} {rows} \\end{{pmatrix}}", piv="、".join(str(p + 1) for p in piv))
# 特殊解：每个自由变量取 1，其余自由变量取 0
n = A.shape[1]
free = [j for j in range(n) if j not in piv]
S = []
for f in free:
    x = np.zeros(n)
    x[f] = 1
    for i, p in enumerate(piv):
        x[p] = -float(R[i][f])
    S.append(x)
N = np.column_stack(S)
out(free="、".join(str(f + 1) for f in free), s1=vec(S[0], 0), s2=vec(S[1], 0), AN=float(np.abs(A @ N).max()))
out(c1=vec(A[:, 0], 0), c3=vec(A[:, 2], 0))
# b = (1, 3, 4) 在列空间中；(1, 3, 5) 不在
for name, b in (("bin", np.array([1.0, 3, 4])), ("bout", np.array([1.0, 3, 5]))):
    x, *_ = np.linalg.lstsq(A, b, rcond=None)
    out(**{name: vec(b, 0), name + "_res": float(np.linalg.norm(A @ x - b))})
