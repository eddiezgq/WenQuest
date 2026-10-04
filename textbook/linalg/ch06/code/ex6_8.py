"""6.8 节：应用——三角形面积与四面体体积；极坐标的雅可比行列式 r；两连杆臂（UR5e 上臂、前臂长度）的
雅可比行列式 det J = l₁ l₂ sin θ₂，伸直或折叠时为零（奇异位形）。"""
import math

import numpy as np

from _arm import planar2, ur5e_links
from bookout import out, vec

# 三角形面积：顶点 (1, 1)、(5, 2)、(2, 4)
P = np.array([[1.0, 1], [5, 2], [2, 4]])
M = np.column_stack([P, np.ones(3)])
out(tri=0.5 * abs(np.linalg.det(M)), tri2=0.5 * abs(np.linalg.det(np.array([P[1] - P[0], P[2] - P[0]]).T)))
# 四面体体积：顶点 O、(1,0,0)、(0,2,0)、(0,0,3)
Q = np.array([[1.0, 0, 0], [0, 2, 0], [0, 0, 3]])
out(tet=abs(np.linalg.det(Q)) / 6)
# 极坐标：x = r cos φ，y = r sin φ 的雅可比行列式
r, ph = 2.0, math.radians(30)
J = np.array([[math.cos(ph), -r * math.sin(ph)], [math.sin(ph), r * math.cos(ph)]])
out(polar=float(np.linalg.det(J)))
# 两连杆臂：UR5e 的上臂与前臂
l1, l2 = ur5e_links()
out(l1=l1, l2=l2, dmax=l1 * l2)
for deg in (90, 45, 10, 0):
    _, Jq = planar2(math.radians(30), math.radians(deg), l1, l2)
    out(**{f"dJ{deg}": float(np.linalg.det(Jq))})
# 伸直时 J 的两列平行：末端只能沿垂直于手臂的方向运动
_, J0 = planar2(math.radians(30), 0.0, l1, l2)
out(J0c1=vec(J0[:, 0], 4), J0c2=vec(J0[:, 1], 4))
# 面积换算：关节角在 1°×1° 的小方块内变化，末端扫过的面积 ≈ |det J|·(π/180)²
_, J45 = planar2(math.radians(30), math.radians(45), l1, l2)
out(darea=abs(np.linalg.det(J45)) * (math.pi / 180) ** 2 * 1e6)
