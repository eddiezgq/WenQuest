"""6.2 节：三条性质决定行列式——det I = 1；交换两行变号；对每一行是线性的。由此推出：两行相等则为零；
倍加不变；有零行则为零；三角矩阵为对角元之积。逐条数值验证。"""
import numpy as np

from bookout import out, tex

d = np.linalg.det
rng = np.random.default_rng(62)
A = rng.integers(-3, 4, (3, 3)).astype(float)
out(A=tex(A, 0), dA=round(float(d(A))))
S = A[[1, 0, 2]]
out(swap=round(float(d(S))))
# 对第 1 行线性：第 1 行乘 5；第 1 行换成两个向量之和
A5 = A.copy()
A5[0] *= 5
u, w = np.array([1.0, 0, 2]), np.array([0.0, 3, -1])
Au, Aw, Auw = A.copy(), A.copy(), A.copy()
Au[0], Aw[0], Auw[0] = u, w, u + w
out(scale=round(float(d(A5))), add_lhs=round(float(d(Auw))), add_rhs=round(float(d(Au) + d(Aw))))
# 推论：倍加不变；两行相等为零；三角矩阵
Ar = A.copy()
Ar[2] += 4 * Ar[0]
Aeq = A.copy()
Aeq[2] = Aeq[0]
U = np.array([[2.0, 7, -1], [0, -3, 5], [0, 0, 4]])
out(rowadd=round(float(d(Ar))), equal=round(float(d(Aeq))), U=tex(U, 0), dU=round(float(d(U))))
# 数乘整个矩阵：det(cA) = cⁿ det A，不是 c det A
out(d2A=round(float(d(2 * A))))
