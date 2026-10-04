"""Examples of Section 3.5.

Example 3.5.1: write one component of the projection tensor of Example 3.4.1, (P_a)_23 = r_2k r_3l (P_b)_kl, in index
           notation and list the non-zero terms; check it in three ways: term by term, matrix multiplication, numpy.einsum.
Theorem 3.5.1 (ε–δ identity): check all 81 index combinations one by one; check the vector triple product formula
           derived from it against direct computation.
Also checked: the index forms of the cross product, the cross-product matrix, the determinant and the scalar triple
product; ε unchanged under rotation and changing sign under mirror reflection; δ unchanged under rotation.
"""
import itertools
import math

import numpy as np

from _vec import d, rot_x, rot_z, skew
from bookout import out

# ---------------------------------------------------------------- Kronecker delta and Levi-Civita symbol
delta = np.eye(3)
eps = np.zeros((3, 3, 3))
for i, j, k in itertools.permutations(range(3)):
    eps[i, j, k] = np.linalg.det(np.eye(3)[[i, j, k]])          # even permutation +1, odd permutation −1
assert eps[0, 1, 2] == 1 and eps[1, 0, 2] == -1 and np.count_nonzero(eps) == 6

# ---------------------------------------------------------------- Example 3.5.1
R = rot_x(d(20))
P_b = np.diag([1.0, 1.0, 0.0])
i, j = 1, 2                                                      # indices start at 0 in the program: (2, 3) → (1, 2)
terms = [(k + 1, l + 1, R[i, k] * R[j, l] * P_b[k, l]) for k in range(3) for l in range(3)]
nonzero = [(k, l, v) for k, l, v in terms if abs(v) > 1e-15]
P23_sum = sum(v for _, _, v in terms)
P23_mat = (R @ P_b @ R.T)[i, j]
P_ein = np.einsum("ik,jl,kl->ij", R, R, P_b)
assert abs(P23_sum - P23_mat) < 1e-15 and np.allclose(P_ein, R @ P_b @ R.T)
assert len(nonzero) == 1 and nonzero[0][:2] == (2, 2)          # only the term k = l = 2 is left
n_mult = 9 * 9 * 2                                              # summing term by term by (3.5.3): 9 terms per entry, two multiplications per term

# ---------------------------------------------------------------- Theorem 3.5.1 ε–δ identity
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
    assert abs(np.einsum("ijk,i,j,k->", eps, a, b, c) - np.cross(a, b) @ c) < 1e-12        # scalar triple product
    # vector triple product: [a×(b×c)]_i = ε_ijk a_j ε_kmn b_m c_n = (δ_im δ_jn − δ_in δ_jm) a_j b_m c_n
    lhs = np.einsum("ijk,j,kmn,m,n->i", eps, a, eps, b, c)
    assert np.allclose(lhs, b * (a @ c) - c * (a @ b))

# ---------------------------------------------------------------- ε and δ under rotation and mirror reflection
Q = rot_z(d(37)) @ rot_x(d(-58))
assert np.allclose(np.einsum("il,jm,kn,lmn->ijk", Q, Q, Q, eps), eps)                    # rotation: unchanged
M = np.diag([1.0, 1.0, -1.0])
assert np.allclose(np.einsum("il,jm,kn,lmn->ijk", M, M, M, eps), -eps)                   # mirror reflection: sign changes
assert np.allclose(np.einsum("ik,jl,kl->ij", Q, Q, delta), delta)

out(
    P23=P23_sum, r22=R[1, 1], r32=R[2, 1], s20=math.sin(d(20)), c20=math.cos(d(20)),
    n_nonzero_cases=n_nonzero_cases, n_mult=n_mult,
)
