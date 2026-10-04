"""4.2 节：矩阵乘法——由复合映射定义；四种算法（行乘列、列的组合、行的组合、列乘行之和）给出同一个结果；
AGV 车轮：车体速度 → 轮速 → 电机转速，两步合成一步。"""
import numpy as np

from bookout import out, tex, vec

A = np.array([[1.0, 2.0, 0.0], [0.0, 1.0, -1.0]])
B = np.array([[2.0, 1.0], [0.0, 3.0], [1.0, -1.0]])
C = A @ B
out(A=tex(A, 0), B=tex(B, 0), C=tex(C, 0))
# 1) 行乘列
c_rc = np.array([[A[i] @ B[:, j] for j in range(2)] for i in range(2)])
# 2) 列：AB 的第 j 列 = A 乘 B 的第 j 列
c_col = np.column_stack([A @ B[:, j] for j in range(2)])
# 3) 行：AB 的第 i 行 = A 的第 i 行乘 B
c_row = np.vstack([A[i] @ B for i in range(2)])
# 4) 列乘行之和
outer = [np.outer(A[:, k], B[k]) for k in range(3)]
c_out = sum(outer)
out(same=bool(np.allclose(c_rc, C) and np.allclose(c_col, C) and np.allclose(c_row, C) and np.allclose(c_out, C)),
    o1=tex(outer[0], 0), o2=tex(outer[1], 0), o3=tex(outer[2], 0), Ab1=vec(A @ B[:, 0], 0), a1B=vec(A[0] @ B, 0))
# AGV：车体速度 (v, ω) → 轮速 = Ainv (v, ω)；电机经减速比 15 的减速器带轮子：电机转速 = 15 × 轮速
r, b = 0.075, 0.40
Ainv = np.array([[1 / r, -b / (2 * r)], [1 / r, b / (2 * r)]])
G = 15.0 * np.eye(2)
M = G @ Ainv
vw = np.array([0.5, 0.5])
out(Ainv=tex(Ainv, 4), M=tex(M, 1), motor=vec(M @ vw, 1), motor2=vec(G @ (Ainv @ vw), 1), rpm=vec(M @ vw * 60 / (2 * np.pi), 0))
# 运算量：m×n 乘 n×p 要 mnp 次乘法
out(cost=2 * 3 * 2)
