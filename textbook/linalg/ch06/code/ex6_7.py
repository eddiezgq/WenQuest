"""6.7 节：范德蒙德行列式与几类特殊行列式——过 4 个时刻的关节角插值多项式（范德蒙德方程组）；
det V = ∏(x_j − x_i)；节点靠得很近时矩阵几乎奇异；三对角行列式的递推 D_n = 2D_{n−1} − D_{n−2}；分块三角矩阵。"""
import math

import numpy as np

from _num import sci
from bookout import out, tex, vec

t = np.array([0.0, 1.0, 2.0, 3.0])
th = np.array([0.0, 20.0, 60.0, 90.0])
V = np.vander(t, increasing=True)
c = np.linalg.solve(V, th)
prod = math.prod(t[j] - t[i] for i in range(4) for j in range(i + 1, 4))
out(V=tex(V, 0), detV=round(float(np.linalg.det(V))), prod=prod, c=vec(c, 3), at15=float(np.polyval(c[::-1], 1.5)))
# 节点靠近：t = 0, 1, 1.01, 3
t2 = np.array([0.0, 1.0, 1.01, 3.0])
V2 = np.vander(t2, increasing=True)
out(detV2=float(np.linalg.det(V2)), cond1=sci(np.linalg.cond(V), 1), cond2=sci(np.linalg.cond(V2), 1))
# 等距节点、阶数升高时条件数急剧增长
out(cond10=sci(np.linalg.cond(np.vander(np.linspace(0, 1, 10), increasing=True)), 1),
    cond20=sci(np.linalg.cond(np.vander(np.linspace(0, 1, 20), increasing=True)), 1))
# 三对角 (−1, 2, −1) 的行列式：D_n = n + 1
Ds = [round(float(np.linalg.det(2 * np.eye(n) - np.eye(n, k=1) - np.eye(n, k=-1)))) for n in range(1, 7)]
out(Ds=", ".join(map(str, Ds)))
# 分块上三角：det = det A₁₁ · det A₂₂
A11, A12, A22 = np.array([[2.0, 1], [5, 3]]), np.array([[7.0, 1], [2, 8]]), np.array([[3.0, 1], [1, 2]])
M = np.block([[A11, A12], [np.zeros((2, 2)), A22]])
out(blk=round(float(np.linalg.det(M))), blk2=round(float(np.linalg.det(A11) * np.linalg.det(A22))))
