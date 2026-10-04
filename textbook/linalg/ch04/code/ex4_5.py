"""4.5 节：转置与对称矩阵——(AB)ᵀ = BᵀAᵀ；点积写成 xᵀy；AᵀA 对称；叉积矩阵 [a]× 反对称；电路节点矩阵 G 对称。"""
import numpy as np

from bookout import out, tex, vec

A = np.array([[1.0, 2.0, 0.0], [3.0, -1.0, 4.0]])
B = np.array([[2.0, 1.0], [0.0, 3.0], [1.0, -1.0]])
out(A=tex(A, 0), AT=tex(A.T, 0), ABT=tex((A @ B).T, 0), BTAT=tex(B.T @ A.T, 0), ok=bool(np.allclose((A @ B).T, B.T @ A.T)))
x, y = np.array([2.0, 1.0, -1.0]), np.array([1.0, 0.0, 2.0])
out(xty=float(x @ y), xyt=tex(np.outer(x, y), 0))
# Ax·y = x·Aᵀy
u, w = np.array([1.0, 2.0, 3.0]), np.array([2.0, -1.0])
out(lhs=float((A @ u) @ w), rhs=float(u @ (A.T @ w)))
# AᵀA 与 AAᵀ 都对称
out(ATA=tex(A.T @ A, 0), AAT=tex(A @ A.T, 0))
# 叉积矩阵
a = np.array([1.0, 2.0, 3.0])
ax = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
v = np.array([4.0, 5.0, 6.0])
out(ax=tex(ax, 0), axv=vec(ax @ v, 0), cross=vec(np.cross(a, v), 0), skew=bool(np.allclose(ax.T, -ax)))
# 任何方阵 = 对称部分 + 反对称部分
M = np.array([[1.0, 4.0], [2.0, 3.0]])
out(M=tex(M, 0), Msym=tex((M + M.T) / 2, 0), Mskw=tex((M - M.T) / 2, 0))
