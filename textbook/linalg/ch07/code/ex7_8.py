"""7.8 节：子空间的和与直和；维数公式 dim(U + W) = dim U + dim W − dim(U ∩ W)——ℝ³ 中两个平面；
ℝ⁴ 中两个二维子空间；2×2 矩阵空间 = 对称矩阵 ⊕ 反对称矩阵。"""
import numpy as np
import scipy.linalg as sla

from bookout import out, vec

r = np.linalg.matrix_rank
# ℝ³：平面 U（z = 0）与平面 W（x = 0）
U = np.array([[1.0, 0, 0], [0, 1, 0]]).T
W = np.array([[0.0, 1, 0], [0, 0, 1]]).T
out(dsum3=int(r(np.hstack([U, W]))), dint3=int(r(U) + r(W) - r(np.hstack([U, W]))))
# ℝ⁴：U = span{u1, u2}，W = span{w1, w2}
u1, u2 = np.array([1.0, 0, 1, 0]), np.array([0.0, 1, 0, 1])
w1, w2 = np.array([1.0, 1, 1, 1]), np.array([1.0, 0, 0, 0])
UW = np.column_stack([u1, u2, w1, w2])
dsum = int(r(UW))
out(dsum4=dsum, dint4=2 + 2 - dsum)
# 交：解 a u1 + b u2 = c w1 + d w2
N = sla.null_space(np.column_stack([u1, u2, -w1, -w2]))
v = N[0, 0] * u1 + N[1, 0] * u2
out(inter=vec(v / v[np.argmax(np.abs(v))], 0))
# 直和：2×2 矩阵 = 对称 ⊕ 反对称，交只有零矩阵
sym = [np.array([[1.0, 0], [0, 0]]), np.array([[0.0, 1], [1, 0]]), np.array([[0.0, 0], [0, 1]])]
skw = [np.array([[0.0, 1], [-1, 0]])]
out(dmat=int(r(np.array([m.ravel() for m in sym + skw]))))
