"""2.2 节：两连杆平面臂的末端位置是两个连杆向量之和；线性组合与求组合系数。"""
import math

import numpy as np

from bookout import out, tex, vec
from _arm import ur5e_links

l1, l2 = ur5e_links()                      # UR5e 上臂、前臂长度（零件库关节表）
t1, t2 = math.radians(30), math.radians(45)   # 肩关节角、肘关节相对角
r1 = l1 * np.array([math.cos(t1), math.sin(t1)])
r2 = l2 * np.array([math.cos(t1 + t2), math.sin(t1 + t2)])
p = r1 + r2
out(l1=l1, l2=l2, r1=vec(r1, 4), r2=vec(r2, 4), p=vec(p, 4), p_len=float(np.linalg.norm(p)))
# 交换加的次序：先走前臂向量再走上臂向量，终点相同（平行四边形的另一条路）
out(same=bool(np.allclose(r1 + r2, r2 + r1)))
# 数乘：把前臂加长一半
out(r2x15=vec(1.5 * r2, 4))
# 线性组合：b = c1 u + c2 w，手算得 c1 = 2, c2 = 3
u, w, b = np.array([2.0, 1.0]), np.array([1.0, 3.0]), np.array([7.0, 11.0])
c = np.linalg.solve(np.c_[u, w], b)
out(c=vec(c, 0), check=vec(c[0] * u + c[1] * w, 0))
# 标准基：v = 4 e1 − 2 e2 + 5 e3
v = np.array([4.0, -2.0, 5.0])
E3 = np.eye(3)
out(v=vec(v, 0), v_from_e=vec(4 * E3[0] - 2 * E3[1] + 5 * E3[2], 0))
# 平行的两个向量只能组合出一条直线：(1, 2) 与 (−2, −4) 凑不出 (1, 0)
P = np.c_[[1.0, 2.0], [-2.0, -4.0]]
out(det_par=float(np.linalg.det(P)))
