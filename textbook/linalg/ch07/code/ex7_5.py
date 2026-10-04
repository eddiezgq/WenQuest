"""7.5 节：线性相关与线性无关——用消元判断；六次试验记录（_rec.py）：秩为 3，主元列 1、2、3 是一个极大无关组；
记录 4、5、6 用前三条表示的系数；极大无关组不唯一。"""
import numpy as np

from _elim import rref, tex_frac
from _rec import RECORDS
from bookout import out, tex, vec

# 三个向量：消元看主元
V = np.array([[1, 0, 1], [0, 1, 1], [1, 1, 2]], float)
R, piv = rref(V.tolist())
out(piv3="、".join(str(p + 1) for p in piv))
# 六条记录排成 5×6 矩阵（每列一条记录）
M = RECORDS.T
R, piv = rref(M.tolist())
out(M=tex(M, 0), rankM=len(piv), piv="、".join(str(p + 1) for p in piv))
rows = " \\\\ ".join(" & ".join(tex_frac(x) for x in r) for r in R)
out(R=f"\\begin{{pmatrix}} {rows} \\end{{pmatrix}}")
# 非主元列的系数就在简化行阶梯形中
for j in (3, 4, 5):
    out(**{f"c{j + 1}": vec(np.array([float(R[i][j]) for i in range(3)]), 0)})
# 另一个极大无关组：记录 2、3、4
out(r234=int(np.linalg.matrix_rank(M[:, [1, 2, 3]])), r124=int(np.linalg.matrix_rank(M[:, [0, 1, 3]])))
