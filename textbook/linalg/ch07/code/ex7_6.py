"""7.6 节：基与维数——平面 x + y + z = 0 的一组基；ℝ³ 中四个向量必相关；
3 阶对称矩阵空间维数为 6；齐次方程组解空间的维数 = 未知数个数 − 主元个数。"""
import numpy as np
import scipy.linalg as sla

from bookout import out, vec

B = sla.null_space(np.array([[1.0, 1, 1]]))
out(planedim=B.shape[1])
b1, b2 = np.array([1.0, -1, 0]), np.array([1.0, 0, -1])
out(b1=vec(b1, 0), b2=vec(b2, 0), indep=int(np.linalg.matrix_rank(np.column_stack([b1, b2]))))
rng = np.random.default_rng(76)
F = rng.standard_normal((3, 4))
out(rank4=int(np.linalg.matrix_rank(F)), nullF=sla.null_space(F).shape[1])
# 3 阶对称矩阵的一组基：E_ii 与 E_ij + E_ji
basis = []
for i in range(3):
    for j in range(i, 3):
        E = np.zeros((3, 3))
        E[i, j] = E[j, i] = 1
        basis.append(E.ravel())
out(symdim=int(np.linalg.matrix_rank(np.array(basis))))
# 齐次方程组：3 个方程、5 个未知数，秩 2
A = np.array([[1.0, 2, 0, 1, 1], [0, 0, 1, 2, 0], [1, 2, 1, 3, 1]])
out(rA=int(np.linalg.matrix_rank(A)), nA=sla.null_space(A).shape[1])
