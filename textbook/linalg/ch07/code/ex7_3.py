"""7.3 节：子空间的判别——过原点的平面是子空间，不过原点的不是；齐次方程组的解集是子空间；
对称矩阵、满足 p(1) = 0 的多项式构成子空间；非齐次方程组的解集不是。"""
import numpy as np
import scipy.linalg as sla

from bookout import out, tex, vec

# 平面 x + y + z = 0：两个点之和、数乘仍在平面上
u, w = np.array([1.0, -1, 0]), np.array([2.0, 1, -3])
out(sumuw=vec(u + w, 0), on_plane=float((u + w).sum()), cu=float((-2.5 * u).sum()))
# 平面 x + y + z = 1：两个点之和不在平面上
a, b = np.array([1.0, 0, 0]), np.array([0.0, 1, 0])
out(shift=float((a + b).sum()))
# 齐次方程组 Ax = 0 的解集（零空间）：一组基
A = np.array([[1.0, 2, 1, 1], [2, 4, 0, 2]])
N = sla.null_space(A)
out(A=tex(A, 0), nulldim=N.shape[1], resid=float(np.abs(A @ N).max()))
# 满足 p(1) = 0 的多项式：(t − 1) 与 (t² − 1) 的组合在 1 处仍为 0
p1, p2 = np.poly1d([1, -1]), np.poly1d([1, 0, -1])
out(p_at1=float((3 * p1 - 2 * p2)(1)))
