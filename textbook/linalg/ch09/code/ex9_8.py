"""9.8 节：商空间。ℝ³ 模去直线 U = span{(1, 1, 1)}：x 与 y 同属一个陪集当且仅当 x − y ∈ U；映射 x ↦ (x1 − x3, x2 − x3) 的核恰为 U，
给出 ℝ³/U ≅ ℝ²。第一同构定理 V/ker T ≅ im T：节点电位模去常数 ≅ 支路电压（8.7 节）；关节速度模去自运动 ≅ 末端速度。"""
import numpy as np
import scipy.linalg as sla

from bookout import out, tex, vec

q = lambda x: np.array([x[0] - x[2], x[1] - x[2]])
x = np.array([3.0, 1.0, 2.0])
y = x + 2.5 * np.ones(3)
z = np.array([3.0, 1.0, 0.0])
out(x=vec(x, 0), y=vec(y, 1), z=vec(z, 0), qx=vec(q(x), 0), qy=vec(q(y), 0), qz=vec(q(z), 0))
# 8.7 节的关联矩阵：电位 u 与 u + c·1 给出相同的支路电压
M = np.array([[-1, 1, 0, 0], [-1, 0, 1, 0], [0, -1, 1, 0], [0, -1, 0, 1], [0, 0, -1, 1]], dtype=float)
u = np.array([24.0, 23.5, 23.0, 22.0])
out(Mu=vec(M @ u, 1), Mu2=vec(M @ (u - 22), 1), u2=vec(u - 22, 1), dimq=4 - sla.null_space(M).shape[1], rM=int(np.linalg.matrix_rank(M)))
# 8.3 节的三连杆臂：同一陪集中的关节速度给出相同的末端速度
L = 0.3
th = np.radians([30, 45, -60])
c = np.cumsum(th)
J = np.array([[-L * np.sin(c[i:]).sum() for i in range(3)], [L * np.cos(c[i:]).sum() for i in range(3)]])
n = sla.null_space(J)[:, 0]
qd = np.array([0.2, -0.1, 0.3])
out(Jqd=vec(J @ qd, 4), Jqd2=vec(J @ (qd + 0.7 * n), 4))
