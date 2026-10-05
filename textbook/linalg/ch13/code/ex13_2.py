"""13.2 节：特征多项式；求特征值与特征向量。
A = [[4, −5], [2, −3]]：det(A − λI) = λ² − λ − 2，λ = 2, −1；特征向量由 N(A − λI) 求出。
3×3：B = [[2, 0, 0], [1, 3, 0], [−1, 1, 3]]（下三角，特征值就是对角元）；特征空间的维数。
机器人：旋转矩阵 R = [[0, 0, 1], [1, 0, 0], [0, 1, 0]] 的特征多项式 −(λ³ − 1)，实特征值只有 1，转轴 N(R − I) = span{(1, 1, 1)}。
numpy.linalg.eig 的结果与手算比较（特征向量差一个倍数）。"""
import numpy as np

from _elim import rref
from _frac import fmat
from _num import sci
from bookout import out, vec

A = np.array([[4.0, -5], [2, -3]])
c = np.poly(A)                     # λ² − tr λ + det
w, V = np.linalg.eig(A)
idx = np.argsort(-w.real); w, V = w[idx].real, V[:, idx].real
out(charA=", ".join(f"{x:.0f}" for x in c), lamA=", ".join(f"{x:.0f}" for x in w),
    vA1=vec(V[:, 0] / V[1, 0] * 2, 0), vA2=vec(V[:, 1] / V[0, 1], 0), Vnp=vec(V[:, 0], 4),
    chkA=sci(max(np.abs(A @ V[:, j] - w[j] * V[:, j]).max() for j in range(2)) + 1e-30, 0))
B = np.array([[2.0, 0, 0], [1, 3, 0], [-1, 1, 3]])
wB = np.sort(np.linalg.eigvals(B).real)
for lam in (2.0, 3.0):
    Ns = B - lam * np.eye(3)
    out(**{f"rankB{int(lam)}": int(np.linalg.matrix_rank(Ns)), f"dimB{int(lam)}": int(3 - np.linalg.matrix_rank(Ns))})
out(lamB=", ".join(f"{x:.0f}" for x in wB))
R = np.array([[0.0, 0, 1], [1, 0, 0], [0, 1, 0]])
wR = np.linalg.eigvals(R)
Rr, _ = rref(R - np.eye(3))
out(RmI=fmat(R - np.eye(3)), RmI_rref=fmat(np.array(Rr, dtype=float)))
for lam in (2.0, 3.0):
    Rb, _ = rref(B - lam * np.eye(3))
    out(**{f"Bm{int(lam)}": fmat(B - lam * np.eye(3)), f"Bm{int(lam)}_rref": fmat(np.array(Rb, dtype=float))})
out(charR=", ".join(f"{x:.0f}" for x in np.poly(R)), rankRI=int(np.linalg.matrix_rank(R - np.eye(3))),
    lamR=", ".join(f"{z.real:.4f}{z.imag:+.4f}i" for z in sorted(wR, key=lambda z: z.imag)))
