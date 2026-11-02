"""22.2 节：乔列斯基分解与对称不定分解。(1) 乔列斯基分解是最便宜的正定判别：成功即正定，失败即不正定；
(2) 带主元的乔列斯基分解：六个传感器读数的协方差矩阵（真实秩 3）——对角元依次减小，读出数值秩；
(3) 冗余机械臂的加权最小范数解：KKT 方程组 [[W, Jᵀ], [J, O]]，对称但不定；不选主元的 LDLᵀ 遇到零主元失败（约束放在前面时），
邦奇–考夫曼分解用 2 阶主元块；由 D 的惯性数出正、负特征值的个数（西尔维斯特惯性定理）；
(4) 小主元 [[ε, 1], [1, 0]]：1 阶主元的 LDLᵀ 增长 1/ε，2 阶主元块没有增长。"""
import math

import numpy as np
from scipy.linalg import cho_factor, ldl

from _num import sci
from bookout import out, tex, vec

rng = np.random.default_rng(22021)
# (1) 正定判别
K = np.array([[4.0, -2.0, 0.0], [-2.0, 5.0, -3.0], [0.0, -3.0, 3.0]])     # 弹簧 2、2、3 串联，一端固定
K2 = K.copy()
K2[2, 2] = 1.0
ok = []
for M in (K, K2):
    try:
        np.linalg.cholesky(M)
        ok.append(True)
    except np.linalg.LinAlgError:
        ok.append(False)
out(K=tex(K, 0), ok1=ok[0], ok2=ok[1], ev1=vec(np.linalg.eigvalsh(K), 3), ev2=vec(np.linalg.eigvalsh(K2), 3), RK=tex(np.linalg.cholesky(K).T, 3))
# 乔列斯基分解中对 K2 的第 3 个主元：5 − 4 = 1，3 − 9/(5 − 1) ... 手算对照
d3 = K2[2, 2] - (K2[2, 1] ** 2) / (K2[1, 1] - K2[1, 0] ** 2 / K2[0, 0])
out(d3=float(d3))


# (2) 带主元的乔列斯基分解（每步取剩余对角元中最大的作主元）
def pivoted_cholesky(A, tol=0.0):
    A = A.copy()
    n = len(A)
    perm = list(range(n))
    R = np.zeros((n, n))
    diag = []
    for k in range(n):
        j = k + int(np.argmax(np.diag(A)[k:]))
        diag.append(float(A[j, j]))
        if A[j, j] <= tol:
            return R[:k], perm, diag
        A[[k, j]] = A[[j, k]]
        A[:, [k, j]] = A[:, [j, k]]
        R[:, [k, j]] = R[:, [j, k]]
        perm[k], perm[j] = perm[j], perm[k]
        R[k, k] = math.sqrt(A[k, k])
        R[k, k + 1:] = A[k, k + 1:] / R[k, k]
        A[k + 1:, k + 1:] -= np.outer(R[k, k + 1:], R[k, k + 1:])
    return R, perm, diag


F = rng.standard_normal((6, 3))                         # 6 个传感器、3 个独立的误差源
Sig = F @ F.T + 1e-10 * np.eye(6)                       # 加上很小的独立噪声：数值上秩 3
R, perm, diag = pivoted_cholesky(Sig, tol=1e-8 * np.max(np.diag(Sig)))
out(pc_diag=", ".join(sci(x, 1) for x in diag), pc_rank=len(R), sig_ev=", ".join(sci(x, 1) for x in sorted(np.linalg.eigvalsh(Sig))[::-1]))
# 仓库地面 200 个测点（20 m × 10 m）的高斯核矩阵，核长度 3 m（与图 22.2.1 相同的随机数）
pts = rng.random((200, 2)) * [20.0, 10.0]
D2 = ((pts[:, None, :] - pts[None, :, :]) ** 2).sum(-1)
Kg = np.exp(-D2 / (2 * 3.0 ** 2)) + 1e-12 * np.eye(200)
Rg, _, dg = pivoted_cholesky(Kg, tol=1e-8 * np.max(np.diag(Kg)))
out(gp_rank=len(Rg))
try:
    np.linalg.cholesky(F @ F.T - 1e-12 * np.eye(6))
    plain = "ok"
except np.linalg.LinAlgError:
    plain = "fail"
assert plain == "fail"

# (3) 冗余机械臂：min ½ q̇ᵀ W q̇，约束 J q̇ = v（末端速度）
Lk = np.array([0.40, 0.35, 0.25])
q = np.radians([30.0, 60.0, -30.0])
c = np.cumsum(q)
J = np.array([[-np.sum(Lk[j:] * np.sin(c[j:])) for j in range(3)], [np.sum(Lk[j:] * np.cos(c[j:])) for j in range(3)]])
W = np.diag([4.0, 2.0, 1.0])                            # 肩关节最“贵”，腕关节最便宜
v = np.array([0.10, 0.05])
Kkt = np.block([[W, J.T], [J, np.zeros((2, 2))]])
rhs = np.concatenate([np.zeros(3), v])
sol = np.linalg.solve(Kkt, rhs)
qd = sol[:3]
Wi = np.linalg.inv(W)
qd2 = Wi @ J.T @ np.linalg.solve(J @ Wi @ J.T, v)      # 加权伪逆的公式
assert np.allclose(qd, qd2) and np.allclose(J @ qd, v)
ev = np.linalg.eigvalsh(Kkt)
out(J=tex(J, 3), Kkt=tex(Kkt, 3), qd=vec(qd, 4), lam=vec(sol[3:], 4), npos=int(np.sum(ev > 0)), nneg=int(np.sum(ev < 0)))
# 不选主元的 LDLᵀ：W 在前时主元为 4、2、1、负、负；约束放在前面时第一个主元为 0
def ldl_nopivot(A):
    A = A.copy()
    n = len(A)
    d = []
    for k in range(n):
        if A[k, k] == 0:
            return d, False
        d.append(float(A[k, k]))
        l = A[k + 1:, k] / A[k, k]
        A[k + 1:, k + 1:] -= np.outer(l, A[k, k + 1:])
    return d, True


d_good, ok_good = ldl_nopivot(Kkt)
perm2 = [3, 4, 0, 1, 2]
d_bad, ok_bad = ldl_nopivot(Kkt[np.ix_(perm2, perm2)])
out(d_good=", ".join(f"{x:.4g}" for x in d_good), ok_bad=ok_bad, nd_bad=len(d_bad))
Lb, Db, pb = ldl(Kkt[np.ix_(perm2, perm2)], lower=True)      # 邦奇–考夫曼
blocks = []
i = 0
while i < 5:
    if i < 4 and Db[i + 1, i] != 0:
        blocks.append(Db[i:i + 2, i:i + 2]); i += 2
    else:
        blocks.append(Db[i:i + 1, i:i + 1]); i += 1
inertia = [0, 0]
for B in blocks:
    e = np.linalg.eigvalsh(B)
    inertia[0] += int(np.sum(e > 0)); inertia[1] += int(np.sum(e < 0))
assert inertia == [3, 2]
out(bk_perm=", ".join(str(i + 1) for i in pb), nblocks=len(blocks), n2=sum(1 for B in blocks if B.shape[0] == 2), bk_pos=inertia[0], bk_neg=inertia[1],
    bk_err=sci(float(np.linalg.norm(Lb @ Db @ Lb.T - Kkt[np.ix_(perm2, perm2)])), 1))

# (4) 小主元：A = [[ε, 1], [1, 0]]
for e_ in (1e-8,):
    Ae = np.array([[e_, 1.0], [1.0, 0.0]])
    d1, _ = ldl_nopivot(Ae)
    out(eps_d=", ".join(sci(x, 0) for x in d1), eps_growth=sci(max(abs(x) for x in d1) / 1.0, 0))
    Le, De, pe = ldl(Ae, lower=True)
    out(eps_bk2=bool(De[1, 0] != 0), eps_De=tex(De, 0))

# 运算量（n = 1000）
n = 1000
out(fl_chol=sci(n ** 3 / 3, 1), fl_lu=sci(2 * n ** 3 / 3, 1))
