"""7.4 节：张成——判断 b 是否在 a₁、a₂、a₃ 张成的空间中（解方程组）；三个向量只张成一个平面；
两连杆臂雅可比矩阵的两列张成 ℝ²，伸直时只张成一条直线。"""
import math

import numpy as np

from _arm import planar2, ur5e_links
from bookout import out, tex, vec

a1, a2, a3 = np.array([1.0, 0, 1]), np.array([0.0, 1, 1]), np.array([1.0, 1, 2])
A = np.column_stack([a1, a2, a3])
out(A=tex(A, 0), rank=int(np.linalg.matrix_rank(A)))
b_in, b_out = np.array([2.0, 3, 5]), np.array([1.0, 1, 1])
x, *_ = np.linalg.lstsq(A, b_in, rcond=None)
out(b_in=vec(b_in, 0), resid_in=float(np.linalg.norm(A @ x - b_in)))
x2, *_ = np.linalg.lstsq(A, b_out, rcond=None)
out(b_out=vec(b_out, 0), resid_out=float(np.linalg.norm(A @ x2 - b_out)))
# 平面方程：法向量 n = a₁ × a₂
n = np.cross(a1, a2)
out(n=vec(n, 0), nb=float(n @ b_in), nb2=float(n @ b_out))
l1, l2 = ur5e_links()
_, J = planar2(math.radians(30), math.radians(60), l1, l2)
_, J0 = planar2(math.radians(30), 0.0, l1, l2)
out(rJ=int(np.linalg.matrix_rank(J)), rJ0=int(np.linalg.matrix_rank(J0, tol=1e-9)))
