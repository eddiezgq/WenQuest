"""13.4 节：对角化 A = XΛX⁻¹。
A = [[3, 1], [0, 2]]：X 的列是特征向量 (1, 0)、(−1, 1)，Λ = diag(3, 2)，验证 AX = XΛ 与 A = XΛX⁻¹；A¹⁰ = XΛ¹⁰X⁻¹。
机器人：柔顺腕的刚度矩阵 K = [[4, 1], [1, 4]] kN/m 对称，特征向量互相垂直，K = QΛQᵀ。在主轴坐标下 F 与位移的各分量互不耦合：
沿 x 推 10 N，先分解到两个主轴上，各自除以主刚度，再合成，得到与直接解方程相同的位移。
不能对角化的例子：剪切 [[1, 1], [0, 1]] 只有一个特征方向。"""
import numpy as np

from _frac import fmat, fvec
from _num import sci
from bookout import out, tex, vec

A = np.array([[3.0, 1], [0, 2]])
X = np.array([[1.0, -1], [0, 1]])
L = np.diag([3.0, 2])
Xi = np.linalg.inv(X)
out(X=fmat(X), Xi=fmat(Xi), L=fmat(L), AX=fmat(A @ X), XL=fmat(X @ L), back=fmat(X @ L @ Xi))
A10 = X @ np.diag([3.0 ** 10, 2.0 ** 10]) @ Xi
out(A10=tex(A10, 0), A10chk=float(np.abs(A10 - np.linalg.matrix_power(A, 10)).max()), p310=3 ** 10, p210=2 ** 10, d10=3 ** 10 - 2 ** 10)
# 刚度矩阵
K = np.array([[4.0, 1], [1, 4]])
lam, Q = np.linalg.eigh(K)
Q = Q * np.sign(Q[0])
F = np.array([10.0, 0])
f = Q.T @ F                       # 主轴坐标中的力
dq = f / lam                      # 主轴坐标中的位移
d = Q @ dq
out(Q=r"\tfrac1{\sqrt2}\begin{pmatrix}1 & 1\\ -1 & 1\end{pmatrix}", Qchk=float(np.abs(Q - np.array([[1, 1], [-1, 1]]) / np.sqrt(2)).max()),
    lamK=", ".join(f"{x:.0f}" for x in lam), fq=vec(f * np.sqrt(2), 0), dqs=fvec(dq * np.sqrt(2)), d=fvec(d), dsolve=fvec(np.linalg.solve(K, F)),
    QtQ=sci(float(np.abs(Q.T @ Q - np.eye(2)).max()) + 1e-30, 0))
# 剪切
S = np.array([[1.0, 1], [0, 1]])
w, V = np.linalg.eig(S)
out(Seig=", ".join(f"{x:.0f}" for x in w), Srank=int(np.linalg.matrix_rank(S - np.eye(2))), Vdet=sci(abs(float(np.linalg.det(V))) + 1e-30, 0))
