"""11.3 节：A = QR。11.2 节的三个向量作为 A 的列：Q 的列是格拉姆–施密特得到的标准正交向量，R 是上三角，r_ij = q_iᵀa_j；
|det A| = |r11 r22 r33|；5×3 矩阵的简化 QR（Q 为 5×3）与完全 QR（Q 为 5×5）；numpy 的 qr 可能给出负的对角元，调整符号后与格拉姆–施密特一致。"""
import numpy as np

from _gs import cgs
from _num import sci
from bookout import out, tex

A = np.array([[1.0, -1, 0], [2, 0, -2], [3, -3, 3]]).T
Q, R = cgs(A)
out(A=tex(A, 0), Q=tex(Q, 4), R=tex(R, 4), QR=float(np.abs(Q @ R - A).max()), r11sq=float(R[0, 0] ** 2), r22sq=float(R[1, 1] ** 2),
    r33sq=float(R[2, 2] ** 2), detA=float(np.linalg.det(A)), prodr=float(np.prod(np.diag(R))))
Qn, Rn = np.linalg.qr(A)
s = np.sign(np.diag(Rn))
out(Rn=tex(Rn, 4), signs=", ".join("+" if x > 0 else "−" for x in s), fixed=sci(float(np.abs(Rn * s[:, None] - R).max()) + 1e-18, 0))
rng = np.random.default_rng(3)
M = rng.normal(size=(5, 3))
Qr, Rr = np.linalg.qr(M)                    # 简化
Qf, Rf = np.linalg.qr(M, mode="complete")   # 完全
out(red=f"{Qr.shape[0]}×{Qr.shape[1]}，R 为 {Rr.shape[0]}×{Rr.shape[1]}", full=f"{Qf.shape[0]}×{Qf.shape[1]}，R 为 {Rf.shape[0]}×{Rf.shape[1]}",
    Rf_low=float(np.abs(Rf[3:]).max()), fullorth=float(np.abs(Qf.T @ Qf - np.eye(5)).max()))
# AᵀA = RᵀR：正规方程的系数矩阵就是 RᵀR
out(AtA=tex(A.T @ A, 0), RtR=float(np.abs(R.T @ R - A.T @ A).max()))
