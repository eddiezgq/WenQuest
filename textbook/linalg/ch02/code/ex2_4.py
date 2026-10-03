"""2.4 节：向一条直线投影——AGV 偏离通道中心线的距离；斜面输送带上零件重力的分解。"""
import math

import numpy as np

from bookout import out, vec

# 通道中心线：从 A = (2, 1) 出发，方向 a = (4, 3)。激光定位测得 AGV 在 Q = (5.0, 4.1)
A = np.array([2.0, 1.0])
a = np.array([4.0, 3.0])
Q = np.array([5.0, 4.1])
b = Q - A
p = (a @ b) / (a @ a) * a
e = b - p
out(b=vec(b, 1), ab=float(a @ b), aa=float(a @ a), xhat=float((a @ b) / (a @ a)), p=vec(p, 3), e=vec(e, 3),
    e_len=float(np.linalg.norm(e)), ea=float(e @ a), along=float(a @ b / np.linalg.norm(a)), foot=vec(A + p, 3))
# 投影矩阵 P = a aᵀ / (aᵀa)
P = np.outer(a, a) / (a @ a)
out(P25=vec(P @ b, 3), PP=bool(np.allclose(P @ P, P)))
# 斜面输送带：倾角 20°，零件 2 kg；重力沿带面向下的分量与压向带面的分量
g = 9.80665
th = math.radians(20)
G = np.array([0.0, -2 * g])
t = np.array([math.cos(th), math.sin(th)])        # 沿带面向上的单位向量
G_t = (G @ t) * t
G_n = G - G_t
out(G=vec(G, 3), Gt=float(G @ t), Gt_vec=vec(G_t, 3), Gn=vec(G_n, 3), Gn_len=float(np.linalg.norm(G_n)),
    mu_need=float(abs(G @ t) / np.linalg.norm(G_n)))
