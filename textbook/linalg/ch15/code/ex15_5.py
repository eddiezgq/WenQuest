"""15.5 节：乔列斯基分解 A = RᵀR（R 上三角、对角元为正）。
(1) 逐行手算的算法（与 numpy.linalg.cholesky 比较），A = [[4, 2, −2], [2, 10, 2], [−2, 2, 6]]，R = [[2, 1, −1], [0, 3, 1], [0, 0, 2]]；
(2) 正定性检验：对不定矩阵，算法在第几步遇到负数而失败；
(3) 乘法次数约 n³/6（加减同样多，合计 n³/3 次运算），是 LU 的一半；逐次数出来；
(4) QR 与乔列斯基：AᵀA 的乔列斯基因子就是 A = QR 中的 R（对角元取正，11.3 节）；
(5) 按协方差 Σ = [[4, 2], [2, 3]] cm² 生成 AGV 定位误差样本：x = Rᵀz，z 为标准正态（14.5 节）；
(6) 把 Kx = λMx 化为标准特征值问题：M = RᵀR，y = Rx，(R⁻ᵀKR⁻¹)y = λy（三质量链末端加 0.5 kg 负载，习题 14.4.7）。"""
import numpy as np
import scipy.linalg as sl

from _num import sci
from bookout import out, tex, vec


def chol(A):
    """返回 (R, ok, 失败的行号)。r_kk = √(a_kk − Σ_{i<k} r_ik²)，r_kj = (a_kj − Σ_{i<k} r_ik r_ij)/r_kk。"""
    n = len(A)
    R = np.zeros((n, n))
    for kk in range(n):
        s = A[kk, kk] - R[:kk, kk] @ R[:kk, kk]
        if s <= 0:
            return R, False, kk + 1, s
        R[kk, kk] = np.sqrt(s)
        for j in range(kk + 1, n):
            R[kk, j] = (A[kk, j] - R[:kk, kk] @ R[:kk, j]) / R[kk, kk]
    return R, True, None, None


A = np.array([[4.0, 2, -2], [2, 10, 2], [-2, 2, 6]])
R, ok, _, _ = chol(A)
out(A=tex(A), R=tex(R), ok=ok, same_np=bool(np.allclose(R, np.linalg.cholesky(A).T)), detA=int(round(np.linalg.det(A))),
    detR2=int(round(np.prod(np.diag(R)) ** 2)))
# (2) 不定矩阵
B = np.array([[4.0, 2, -2], [2, 10, 2], [-2, 2, 1]])
_, okB, row, s = chol(B)
out(B=tex(B), okB=okB, rowB=row, sB=float(s), lamB=vec(np.linalg.eigvalsh(B), 2))


# (3) 运算次数
def count(n):
    mul = 0
    for kk in range(n):
        mul += kk + 1                   # r_kk：kk 次乘法 + 1 次开方（开方计入）
        mul += (n - kk - 1) * (kk + 1)  # r_kj：kk 次乘法 + 1 次除法
    return mul


out(cnt="、".join(str(count(n)) for n in (10, 100, 1000)), ratio1000=float(count(1000) / (1000 ** 3 / 6)))
# (4) QR 与乔列斯基
rng = np.random.default_rng(155)
G = rng.normal(size=(8, 3))
Qg, Rg = np.linalg.qr(G)
Rg = np.sign(np.diag(Rg))[:, None] * Rg
out(qr_chol=sci(float(np.abs(Rg - np.linalg.cholesky(G.T @ G).T).max()) + 1e-17, 0))
# (5) 按协方差生成样本
S = np.array([[4.0, 2], [2, 3]])
Rs = np.linalg.cholesky(S).T
Z = rng.normal(size=(200000, 2))
Xs = Z @ Rs                          # 每一行 x = Rᵀz
out(Rs=tex(Rs, 3), Rs_exact=bool(np.allclose(Rs, [[2, 1], [0, np.sqrt(2)]])), Shat=tex(np.cov(Xs.T), 2))
# (6) 广义特征值问题
K = 1e4 * np.array([[2.0, -1, 0], [-1, 2, -1], [0, -1, 1]])
M = np.diag([1.0, 1.0, 1.5])
Rm = np.linalg.cholesky(M).T
Ri = np.linalg.inv(Rm)
Cm = Ri.T @ K @ Ri
lam_c = np.linalg.eigvalsh(Cm)
lam_g = sl.eigh(K, M, eigvals_only=True)
f_before = float(np.sqrt(np.linalg.eigvalsh(K)[0]) / (2 * np.pi))
out(Cm=tex(Cm, 0), sym=bool(np.allclose(Cm, Cm.T)), lam_c=vec(lam_c, 1), err_g=sci(float(np.abs(lam_c - lam_g).max()) + 1e-17, 0), f_before=f_before,
    f=vec(np.sqrt(lam_c) / (2 * np.pi), 2))
