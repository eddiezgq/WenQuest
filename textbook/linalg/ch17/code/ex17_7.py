"""17.7 节：舒尔分解——数值计算为什么用它而不用若尔当形。
(1) 若尔当形不连续：n 阶若尔当块 J_n(0) 的左下角加 ε，特征值变为 ε^{1/n} 乘 n 次单位根（模都是 ε^{1/n}）；
(2) 浮点数中的“重特征值”：17.4 节的整数矩阵 A（特征值 2 有 3 阶块）用 numpy.linalg.eig 求特征值：元素只差 10⁻¹⁵ 时特征值误差约 (10⁻¹⁵)^{1/3}，
    特征向量矩阵的条件数巨大；而舒尔分解 A = QTQᵀ 的残差和 Q 的正交性都在舍入误差的量级（后向稳定）；
(3) 算函数：scipy.linalg.expm 对亏损的 A 照样准确（与 SymPy 的精确 e^A 比较），而 numpy 给出的“特征向量矩阵”秩不足，无法对角化；
(4) 无差拍控制的灵敏度（17.2 节的位置轴）：质量误差 δ 使二重特征值 0 变为约 ±√δ 量级。"""
import numpy as np
import scipy.linalg as sl
import sympy as sp

from _num import sci
from bookout import out

rows = []
for n in (2, 4, 8):
    for e in (1e-4, 1e-8, 1e-16):
        Jn = np.diag(np.ones(n - 1), 1)
        Jn[n - 1, 0] = e
        ev = np.linalg.eigvals(Jn)
        rows.append((n, e, float(np.abs(ev).max()), e ** (1 / n)))
fmt_ = lambda x: (f"{x:.3g}" if x >= 1e-3 else sci(x, 0))
out(**{f"r_{n}_{int(-np.log10(e))}": fmt_(m) for n, e, m, _ in rows})
out(**{f"p_{n}_{int(-np.log10(e))}": p for n, e, _, p in rows})
# (2) 17.4 节的矩阵


def jb(l, k):
    return sp.Matrix(k, k, lambda i, j: l if i == j else (1 if j == i + 1 else 0))


J = sp.diag(jb(2, 3), jb(2, 1), jb(-1, 2))
P = sp.Matrix([[1, 0, -1, 0, 0, 0], [0, 1, 0, 1, 0, 0], [-1, 0, 1, 0, 0, 1], [0, 0, 0, 1, 0, -1], [1, 0, 0, 0, 1, 0], [-1, 0, 0, -1, 0, 1]])
As = P * J * P.inv()
A = np.array(As.tolist(), float)
w, V = np.linalg.eig(A)
out(condV=sci(float(np.linalg.cond(V)), 0), eig_exact=sci(float(max(min(abs(z - 2), abs(z + 1)) for z in w)) + 1e-30, 0))
# 元素只差 10⁻¹⁵ 的矩阵（相当于舍入误差）：特征值的误差约 (10⁻¹⁵)^{1/3}
rng = np.random.default_rng(177)
errs = []
for _ in range(20):
    E = rng.uniform(-1, 1, (6, 6)) * 1e-15
    wp = np.linalg.eigvals(A + E)
    errs.append(max(abs(z - 2) for z in wp if abs(z - 2) < 0.5))
out(pert_err=sci(float(np.median(errs)), 0), pert13=sci(1e-15 ** (1 / 3), 0))
T, Q = sl.schur(A)
out(schur_res=sci(float(np.abs(Q @ T @ Q.T - A).max()) + 1e-18, 0), schur_orth=sci(float(np.abs(Q.T @ Q - np.eye(6)).max()) + 1e-18, 0),
    T_lower=sci(float(np.abs(np.tril(T, -1)).max()) + 1e-30, 0), Tdiag=", ".join(f"{x:.6f}" for x in np.sort(np.diag(T))))
# (3) 函数
eA = np.array(sp.simplify(As.exp()).evalf(30).tolist(), float)
out(expm_err=sci(float(np.abs(sl.expm(A) - eA).max() / np.abs(eA).max()), 0),
    rank_V=int(np.linalg.matrix_rank(V)))
# (4) 无差拍
T_, m = 0.01, 1.0
Ad = np.array([[1, T_], [0, 1]]); Bd = np.array([[T_ * T_ / 2], [T_]])
K = np.array([[1 / T_ ** 2, 1.5 / T_]])
for name, d in (("1", 0.01), ("5", 0.05)):
    ev = np.linalg.eigvals(Ad - Bd / (1 + d) @ K)
    out(**{f"db_{name}": float(np.abs(ev).max())})
