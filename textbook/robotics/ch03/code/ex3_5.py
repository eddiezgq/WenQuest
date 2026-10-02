"""3.5 节的算例。

算例 3.5.1：用指标记号写出算例 3.4.1 中投影张量的一个分量 (P_a)_23 = r_2k r_3l (P_b)_kl，列出非零项；
           与矩阵乘法、numpy.einsum 三种算法核对。
算例 3.5.2：逐一检验 ε–δ 恒等式的全部 81 种指标组合；由它推出的二重叉积公式与直接计算核对。
另外验证：叉积、叉积矩阵、行列式、混合积的指标形式；ε 在转动下不变，在镜像下变号；δ 在转动下不变。
"""
import itertools
import math

import numpy as np

from _vec import d, rot_x, rot_z, skew
from bookout import out

# ---------------------------------------------------------------- 克罗内克符号与列维-奇维塔符号
delta = np.eye(3)
eps = np.zeros((3, 3, 3))
for i, j, k in itertools.permutations(range(3)):
    eps[i, j, k] = np.linalg.det(np.eye(3)[[i, j, k]])          # 偶排列 +1，奇排列 −1
assert eps[0, 1, 2] == 1 and eps[1, 0, 2] == -1 and np.count_nonzero(eps) == 6

# ---------------------------------------------------------------- 算例 3.5.1
R = rot_x(d(20))
P_b = np.diag([1.0, 1.0, 0.0])
i, j = 1, 2                                                      # 程序中下标从 0 起：(2, 3) → (1, 2)
terms = [(k + 1, l + 1, R[i, k] * R[j, l] * P_b[k, l]) for k in range(3) for l in range(3)]
nonzero = [(k, l, v) for k, l, v in terms if abs(v) > 1e-15]
P23_sum = sum(v for _, _, v in terms)
P23_mat = (R @ P_b @ R.T)[i, j]
P_ein = np.einsum("ik,jl,kl->ij", R, R, P_b)
assert abs(P23_sum - P23_mat) < 1e-15 and np.allclose(P_ein, R @ P_b @ R.T)
assert len(nonzero) == 1 and nonzero[0][:2] == (2, 2)          # 只剩 k = l = 2 一项
n_mult = 9 * 9 * 2                                              # 按 (3.5.3) 逐项求和：每个元素 9 项，每项两次乘法

# ---------------------------------------------------------------- 算例 3.5.2 ε–δ 恒等式
bad = 0
for jj, kk, mm, nn in itertools.product(range(3), repeat=4):
    lhs = sum(eps[ii, jj, kk] * eps[ii, mm, nn] for ii in range(3))
    rhs = delta[jj, mm] * delta[kk, nn] - delta[jj, nn] * delta[kk, mm]
    bad += lhs != rhs
assert bad == 0
lhs_all = np.einsum("ijk,imn->jkmn", eps, eps)
rhs_all = np.einsum("jm,kn->jkmn", delta, delta) - np.einsum("jn,km->jkmn", delta, delta)
assert np.array_equal(lhs_all, rhs_all)
n_nonzero_cases = int(np.count_nonzero(lhs_all))

rng = np.random.default_rng(5)
for _ in range(100):
    a, b, c = rng.normal(size=(3, 3))
    A = rng.normal(size=(3, 3))
    assert np.allclose(np.einsum("ijk,j,k->i", eps, a, b), np.cross(a, b))                 # (a×b)_i = ε_ijk a_j b_k
    assert np.allclose(-np.einsum("ijk,k->ij", eps, a), skew(a))                           # [a]_ij = −ε_ijk a_k
    assert abs(np.einsum("ijk,i,j,k->", eps, A[:, 0], A[:, 1], A[:, 2]) - np.linalg.det(A)) < 1e-9   # det A
    assert abs(np.einsum("ijk,i,j,k->", eps, a, b, c) - np.cross(a, b) @ c) < 1e-12        # 混合积
    # 二重叉积：[a×(b×c)]_i = ε_ijk a_j ε_kmn b_m c_n = (δ_im δ_jn − δ_in δ_jm) a_j b_m c_n
    lhs = np.einsum("ijk,j,kmn,m,n->i", eps, a, eps, b, c)
    assert np.allclose(lhs, b * (a @ c) - c * (a @ b))

# ---------------------------------------------------------------- ε、δ 在转动和镜像下
Q = rot_z(d(37)) @ rot_x(d(-58))
assert np.allclose(np.einsum("il,jm,kn,lmn->ijk", Q, Q, Q, eps), eps)                    # 转动：不变
M = np.diag([1.0, 1.0, -1.0])
assert np.allclose(np.einsum("il,jm,kn,lmn->ijk", M, M, M, eps), -eps)                   # 镜像：变号
assert np.allclose(np.einsum("ik,jl,kl->ij", Q, Q, delta), delta)

out(
    P23=P23_sum, r22=R[1, 1], r32=R[2, 1], s20=math.sin(d(20)), c20=math.cos(d(20)),
    n_nonzero_cases=n_nonzero_cases, n_mult=n_mult,
)
