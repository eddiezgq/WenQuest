"""15.4 节：正定矩阵的五种判据。
(1) A = [[2, −1, 0], [−1, 2, −1], [0, −1, 2]]：特征值、主元、顺序主子式、乔列斯基因子、随机向量上的 xᵀAx，五种判据结论一致；
(2) 对角元都正不够：[[1, 2], [2, 1]] 的 det < 0，x = (1, −1) 时 xᵀAx < 0；
(3) 机器人：腱驱动手指的两个关节由 3 根腱拉动，腱的伸长 Δs = RΔq（R 为 3×2 力臂矩阵，m），腱刚度 k_i（N/m），
    关节刚度 K_q = Rᵀ diag(k) R（N·m/rad）。K_q 正定 ⇔ 拉紧的腱对应的 R 的行张成 R²（列满秩）。
    依次让腱 2、腱 1 和腱 2 一起松弛（k_i = 0），看 K_q 何时失去正定。"""
import numpy as np

from _frac import fmat
from bookout import out, tex, vec

A = np.array([[2.0, -1, 0], [-1, 2, -1], [0, -1, 2]])
lam = np.linalg.eigvalsh(A)
U = A.copy()
piv = []
for kk in range(3):                      # 不交换行的消元
    piv.append(U[kk, kk])
    for i in range(kk + 1, 3):
        U[i] -= U[i, kk] / U[kk, kk] * U[kk]
minors = [np.linalg.det(A[:j, :j]) for j in (1, 2, 3)]
R = np.linalg.cholesky(A).T
rng = np.random.default_rng(154)
X = rng.normal(size=(100000, 3))
qmin = float(min(np.einsum("ij,jk,ik->i", X, A, X) / np.einsum("ij,ij->i", X, X)))
out(lam=vec(lam, 3), piv=fmat(np.array(piv)[None, :]).replace("pmatrix", "matrix"), minors=", ".join(str(int(round(v))) for v in minors),
    R=tex(R, 3), RtR=float(np.abs(R.T @ R - A).max()), qmin=qmin, lam1=float(lam[0]))
# (2) 对角元为正的不定矩阵
B = np.array([[1.0, 2], [2, 1]])
x = np.array([1.0, -1])
out(detB=int(round(np.linalg.det(B))), qB=int(x @ B @ x), lamB=vec(np.linalg.eigvalsh(B), 0))
# (3) 腱驱动手指
Rm = np.array([[10.0, 8], [9, -8], [-12, 3]]) * 1e-3          # 力臂 mm → m
kt = np.array([5e4, 4e4, 6e4])


def Kq(k):
    return Rm.T @ np.diag(k) @ Rm


cases = {"all": kt, "slack2": kt * [1, 0, 1], "only3": kt * [0, 0, 1]}
for name, k in cases.items():
    Kc = Kq(k)
    l = np.linalg.eigvalsh(Kc)
    try:
        np.linalg.cholesky(Kc)
        chol = True
    except np.linalg.LinAlgError:
        chol = False
    out(**{f"K_{name}": tex(Kc, 2), f"lam_{name}": vec(l, 2), f"det_{name}": float(np.linalg.det(Kc)), f"chol_{name}": chol,
           f"rank_{name}": int(np.linalg.matrix_rank(Rm[k > 0])), f"lmin_{name}": float(l[0])})
# 只剩腱 3：哪个方向没有刚度
w, V = np.linalg.eigh(Kq(cases["only3"]))
v0 = V[:, 0] * np.sign(V[1, 0])
out(null3=vec(v0 * np.sqrt(17), 0), null3_ok=bool(np.allclose(v0 * np.sqrt(17), [1, 4])))
