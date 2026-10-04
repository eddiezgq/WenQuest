"""4.1 节：矩阵乘向量——按列（列的线性组合）与按行（行与向量的点积）两种算法；线性映射的矩阵由基向量的像确定。"""
import math

import numpy as np

from bookout import out, tex, vec

A = np.array([[1.0, 2.0, 0.0], [3.0, -1.0, 4.0]])
x = np.array([2.0, 1.0, -1.0])
cols = [x[j] * A[:, j] for j in range(3)]
out(A=tex(A, 0), x=vec(x, 0), Ax=vec(A @ x, 0), c1=vec(cols[0], 0), c2=vec(cols[1], 0), c3=vec(cols[2], 0),
    r1=float(A[0] @ x), r2=float(A[1] @ x))
# 线性：A(c u + d w) = c A u + d A w
rng = np.random.default_rng(41)
u, w = rng.standard_normal(3), rng.standard_normal(3)
out(lin=bool(np.allclose(A @ (2 * u - 3 * w), 2 * (A @ u) - 3 * (A @ w))))
# 由基向量的像写出矩阵：绕原点转 θ = 30°；关于直线 y = x 的反射；向 x 轴投影
t = math.radians(30)
R = np.column_stack([[math.cos(t), math.sin(t)], [-math.sin(t), math.cos(t)]])
F = np.column_stack([[0.0, 1.0], [1.0, 0.0]])
P = np.column_stack([[1.0, 0.0], [0.0, 0.0]])
out(R=tex(R, 4), F=tex(F, 0), P=tex(P, 0), Rp=vec(R @ np.array([0.2, 0.1]), 4))
# 相机：针孔模型把相机坐标系中的点 (X, Y, Z) 化为齐次像素坐标 K (X, Y, Z)ᵀ，再除以第三个分量
K = np.array([[800.0, 0.0, 320.0], [0.0, 800.0, 240.0], [0.0, 0.0, 1.0]])
Pc = np.array([0.1, -0.05, 1.6])
q = K @ Pc
out(K=tex(K, 0), Pc=vec(Pc, 2), q=vec(q, 1), uv=vec(q[:2] / q[2], 1))
