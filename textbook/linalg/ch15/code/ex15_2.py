"""15.2 节：化二次型为标准形。
算例 15.2.1  f = 2x₁² + 5x₂² + 5x₃² + 4x₁x₂ − 4x₁x₃ − 8x₂x₃：
  正交变换法：A = QΛQᵀ，x = Qy，f = λ₁y₁² + λ₂y₂² + λ₃y₃²（λ = 1, 1, 10，重特征值的特征向量要在特征子空间里正交化）；
  配方法：逐个变量配平方，等价于不交换行的 LDLᵀ 分解（D 的对角元 = 主元 2, 3, 5/3）。
  两种标准形系数不同，但正、负、零的个数相同；系数之积 = det A。
算例 15.2.2  f = 2x₁x₂ + 2x₁x₃ − 6x₂x₃（没有平方项）：先作 x₁ = y₁ + y₂、x₂ = y₁ − y₂、x₃ = y₃ 造出平方项，再配方。"""
from fractions import Fraction

import numpy as np

from _elim import F, tex_frac
from _frac import fmat
from _num import fix_sign
from bookout import out, tex, vec

A = np.array([[2.0, 2, -2], [2, 5, -4], [-2, -4, 5]])
lam, Q = np.linalg.eigh(A)
Q = fix_sign(Q)
out(lam=", ".join(str(int(round(v))) for v in lam), Q=tex(Q, 3), orth=float(np.abs(Q.T @ Q - np.eye(3)).max()),
    diag=float(np.abs(Q.T @ A @ Q - np.diag(lam)).max()))
# 属于 λ = 1 的特征子空间：x₁ + 2x₂ − 2x₃ = 0（A − I 的秩为 1）
out(rankAI=int(np.linalg.matrix_rank(A - np.eye(3))))
# 正交化前的两个特征向量 (−2, 1, 0)、(2, 0, 1)：互不垂直
a1, a2 = np.array([-2.0, 1, 0]), np.array([2.0, 0, 1])
out(dot12=int(a1 @ a2), check1=bool(np.allclose(A @ a1, a1) and np.allclose(A @ a2, a2)))
b2 = a2 - (a2 @ a1) / (a1 @ a1) * a1          # 施密特正交化
out(b2_is=bool(np.allclose(b2, [0.4, 0.8, 1.0])), b2dot=float(b2 @ a1))
# 单位化后与 λ = 10 的特征向量 (1, 2, −2)/3 拼成正交矩阵 Q
Q = np.column_stack([a1 / np.linalg.norm(a1), b2 / np.linalg.norm(b2), np.array([1.0, 2, -2]) / 3])
out(Q_orth=float(np.abs(Q.T @ Q - np.eye(3)).max()), Q_diag=tex(Q.T @ A @ Q, 3), Q_err=float(np.abs(Q.T @ A @ Q - np.diag([1, 1, 10])).max()))


def ldl(M):
    """不交换行的 LDLᵀ（用分数精确计算）：返回 L、主元 d。配方法的每一步就是消去一列。"""
    M = F(M)
    n = len(M)
    L = [[Fraction(int(i == j)) for j in range(n)] for i in range(n)]
    d = []
    for k in range(n):
        p = M[k][k]
        d.append(p)
        for i in range(k + 1, n):
            L[i][k] = M[i][k] / p
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                M[i][j] -= L[i][k] * p * L[j][k]
    return L, d


Lf, d = ldl(A.astype(int).tolist())
Lm = np.array([[float(x) for x in r] for r in Lf])
out(L=fmat(Lm), d=", ".join(tex_frac(x) for x in d), LDL=float(np.abs(Lm @ np.diag([float(x) for x in d]) @ Lm.T - A).max()),
    prod_d=tex_frac(d[0] * d[1] * d[2]), detA=int(round(np.linalg.det(A))), prod_lam=int(round(np.prod(lam))))
# 配方后的新变量 y = Lᵀx，x = L⁻ᵀy
Linv_T = np.linalg.inv(Lm.T)
out(Lt=fmat(Lm.T), C=fmat(Linv_T))
rng = np.random.default_rng(152)
X = rng.normal(size=(1000, 3))
f = lambda x: x @ A @ x
out(err_ldl=float(max(abs(f(x) - sum(float(d[i]) * (Lm.T @ x)[i] ** 2 for i in range(3))) for x in X)))
# 算例 15.2.2：没有平方项
B = np.array([[0.0, 1, 1], [1, 0, -3], [1, -3, 0]])
C1 = np.array([[1.0, 1, 0], [1, -1, 0], [0, 0, 1]])
B1 = C1.T @ B @ C1
L2, d2 = ldl(B1.astype(int).tolist())
L2m = np.array([[float(x) for x in r] for r in L2])
C2 = C1 @ np.linalg.inv(L2m.T)
out(B=tex(B), B1=tex(B1), d2=", ".join(tex_frac(x) for x in d2), C2=fmat(C2),
    CBC=fmat(C2.T @ B @ C2), detC2=fmat(np.atleast_2d(np.linalg.det(C2))).replace("\\begin{pmatrix} ", "").replace(" \\end{pmatrix}", ""),
    lamB=vec(np.linalg.eigvalsh(B), 3),
    sgnB=" ".join("+" if v > 0 else "−" for v in np.linalg.eigvalsh(B)))
# 配方的力学意义：腕部刚度 K_q = [[120, 30], [30, 60]]（15.1 节）。
# U = ½[k₁₁(Δq₁ + (k₁₂/k₁₁)Δq₂)² + (k₂₂ − k₁₂²/k₁₁)Δq₂²]：第二个系数是放松关节 1（不加力矩、让它自己找平衡）时关节 2 的刚度
Kq = np.array([[120.0, 30], [30, 60]])
d2 = Kq[1, 1] - Kq[0, 1] ** 2 / Kq[0, 0]
# 检验：关节 2 转 Δq₂，关节 1 取使 U 最小的值，此时关节 2 的力矩 / Δq₂
dq2 = 0.01
dq1 = -Kq[0, 1] / Kq[0, 0] * dq2
tau = Kq @ np.array([dq1, dq2])
out(Kd2=float(d2), Kdq1_ratio=float(dq1 / dq2), Ktau1=float(abs(tau[0])), Kstiff2=float(tau[1] / dq2))
