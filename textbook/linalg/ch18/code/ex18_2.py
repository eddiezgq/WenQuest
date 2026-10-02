"""算例 18.2.1：A = [[3, 2, 2], [2, 3, −2]] 的奇异值分解（手算步骤逐一核对），以及 2×2 矩阵的“转—伸缩—转”。"""
import math

import numpy as np

from _arm import svd_fixed
from bookout import out, tex

A = np.array([[3.0, 2.0, 2.0], [2.0, 3.0, -2.0]])
AAt = A @ A.T
AtA = A.T @ A
lam = np.linalg.eigvalsh(AAt)[::-1]
U, s, V = svd_fixed(A)
# 手算：u1 = (1, 1)/√2，u2 = (1, −1)/√2；v_i = Aᵀu_i/σ_i；v3 ⟂ v1, v2
u1h, u2h = np.array([1, 1]) / math.sqrt(2), np.array([1, -1]) / math.sqrt(2)
v1h, v2h = A.T @ u1h / 5, A.T @ u2h / 3
v3h = np.cross(v1h, v2h)
v3h = v3h / np.linalg.norm(v3h)
if v3h[np.argmax(np.abs(v3h))] < 0:
    v3h = -v3h
assert np.allclose(np.c_[v1h, v2h, v3h], V) and np.allclose(np.c_[u1h, u2h], U)
assert np.allclose(v1h, [1 / math.sqrt(2), 1 / math.sqrt(2), 0]) and np.allclose(v2h * 3 * math.sqrt(2), [1, -1, 4])
assert np.allclose(v3h * 3, [2, -2, -1])
Sigma = np.zeros((2, 3))
Sigma[0, 0], Sigma[1, 1] = s
err = np.abs(U @ Sigma @ V.T - A).max()
outer = 5 * np.outer(u1h, v1h) + 3 * np.outer(u2h, v2h)
eigAtA = np.sort(np.linalg.eigvalsh(AtA))[::-1]
out(AAt=tex(AAt, 0), AtA=tex(AtA, 0), lam1=round(lam[0]), lam2=round(lam[1]), s1=s[0], s2=s[1],
    U=tex(U, 4), V=tex(V, 4), err_rec=err, err_outer=np.abs(outer - A).max(),
    eigAtA=", ".join(f"{x:.0f}" if abs(x) > 1e-9 else "0" for x in eigAtA),
    Av3_max=np.abs(A @ v3h).max())

# 2×2 例子 A = [[3, 0], [4, 5]] 的三个因子（图 18.2.1）
B = np.array([[3.0, 0.0], [4.0, 5.0]])
Ub, sb, Vb = svd_fixed(B)
ang = lambda Q: math.degrees(math.atan2(Q[1, 0], Q[0, 0]))
out(BU=tex(Ub, 4), BV=tex(Vb, 4), detU=np.linalg.det(Ub), detV=np.linalg.det(Vb),
    angU=ang(Ub), angVt=ang(Vb.T), cond_sq=(np.linalg.cond(B.T @ B)), cond=np.linalg.cond(B))

# 选另一组符号，使 U、V 都是旋转（det A > 0 时总能做到）：A = R(α) Σ R(−β)
Ur, Vr = Ub.copy(), Vb.copy()
Ur[:, 1] *= -1
Vr[:, 1] *= -1
assert np.allclose(Ur @ np.diag(sb) @ Vr.T, B) and np.linalg.det(Ur) > 0 and np.linalg.det(Vr) > 0
out(BUr=tex(Ur, 4), BVr=tex(Vr, 4), alpha=ang(Ur), beta=ang(Vr))
