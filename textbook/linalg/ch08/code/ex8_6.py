"""8.6 节：秩的性质与秩不等式——rank(AB) ≤ min(rank A, rank B)；rank(A + B) ≤ rank A + rank B；
西尔维斯特不等式 rank A + rank B − n ≤ rank(AB)；rank(AᵀA) = rank A；用随机低秩矩阵逐条验证。"""
import numpy as np

from bookout import out

rk = np.linalg.matrix_rank
rng = np.random.default_rng(86)


def lowrank(m, n, r):
    return rng.standard_normal((m, r)) @ rng.standard_normal((r, n))


A, B = lowrank(6, 5, 3), lowrank(5, 7, 4)
out(rA=int(rk(A)), rB=int(rk(B)), rAB=int(rk(A @ B)), syl=int(rk(A) + rk(B) - 5))
C, D = lowrank(6, 5, 2), lowrank(6, 5, 2)
out(rC=int(rk(C)), rD=int(rk(D)), rCD=int(rk(C + D)))
out(rATA=int(rk(A.T @ A)), rAAT=int(rk(A @ A.T)))
# 乘可逆矩阵不改变秩
P = rng.standard_normal((6, 6))
out(rPA=int(rk(P @ A)))
