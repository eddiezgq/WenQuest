"""4.3 节：运算律——结合律、分配律成立，交换律不成立；AB = O 而 A、B 都不是零矩阵；消去律失效；矩阵的幂。"""
import math

import numpy as np

from bookout import out, tex

t = math.radians(30)
R = np.array([[math.cos(t), -math.sin(t)], [math.sin(t), math.cos(t)]])
S = np.array([[1.0, 1.0], [0.0, 1.0]])
out(R=tex(R, 4), S=tex(S, 0), RS=tex(R @ S, 4), SR=tex(S @ R, 4), comm=bool(np.allclose(R @ S, S @ R)))
# 结合律（随机矩阵检验）与运算量的差别：(AB)C 与 A(BC)
rng = np.random.default_rng(43)
A, B, C = rng.standard_normal((2, 3)), rng.standard_normal((3, 4)), rng.standard_normal((4, 5))
out(assoc=bool(np.allclose((A @ B) @ C, A @ (B @ C))))
# 乘向量链：(A B) x 与 A (B x) 的乘法次数，A、B 为 1000×1000
n = 1000
out(cost_left=f"{n ** 3 + n ** 2:.2e}", cost_right=f"{2 * n ** 2:.1e}")
# AB = O
P = np.array([[1.0, 2.0], [2.0, 4.0]])
Q = np.array([[2.0, -4.0], [-1.0, 2.0]])
out(P=tex(P, 0), Q=tex(Q, 0), PQ=tex(P @ Q, 0), QP=tex(Q @ P, 0))
# 消去律失效：PB = PC 而 B ≠ C
Bm = np.array([[1.0, 0.0], [0.0, 1.0]])
Cm = Bm + Q
out(cancel=bool(np.allclose(P @ Bm, P @ Cm)), Cm=tex(Cm, 0))
# 幂：转 30° 的矩阵的 12 次幂是单位矩阵；剪切的 n 次幂
out(R12=tex(np.round(np.linalg.matrix_power(R, 12), 12) + 0.0, 0), S5=tex(np.linalg.matrix_power(S, 5), 0))
# 与对角矩阵可交换：任何矩阵都与 cI 可交换；对角矩阵之间可交换
D1, D2 = np.diag([2.0, 3.0]), np.diag([-1.0, 5.0])
out(diagcomm=bool(np.allclose(D1 @ D2, D2 @ D1)))
