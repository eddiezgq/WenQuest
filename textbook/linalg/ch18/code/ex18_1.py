"""算例 18.1.1 与 18.1.4 节：2×2 矩阵 A 把单位圆变成椭圆；UR5e 肩、肘两关节的速度椭圆。"""
import math

import numpy as np

from _arm import planar2, svd_fixed, ur5e_links
from bookout import out, tex, vec

# 算例 18.1.1：A = [[3, 0], [4, 5]]
A = np.array([[3.0, 0.0], [4.0, 5.0]])
f = lambda phi: np.linalg.norm(A @ np.array([math.cos(phi), math.sin(phi)])) ** 2     # ‖Ax‖² = 25 + 20 sin 2φ
phis = np.linspace(0, 2 * math.pi, 3601)
vals = np.array([f(p) for p in phis])
assert np.allclose(vals, 25 + 20 * np.sin(2 * phis))
U, s, V = svd_fixed(A)
v1, v2, u1, u2 = V[:, 0], V[:, 1], U[:, 0], U[:, 1]
assert abs(np.dot(A @ v1, A @ v2)) < 1e-12
out(len_e1=np.linalg.norm(A @ [1, 0]), len_e2=np.linalg.norm(A @ [0, 1]),
    len_d=np.linalg.norm(A @ (np.array([1, 1]) / math.sqrt(2))),
    s1=s[0], s2=s[1], s1sq=s[0] ** 2, s2sq=s[1] ** 2, max_deg=math.degrees(phis[np.argmax(vals)]), min_deg=math.degrees(phis[np.argmin(vals[:1801])]),
    v1=vec(v1), v2=vec(v2), u1=vec(u1), u2=vec(u2), Av1=tex(A @ v1), Av2=tex(A @ v2), det=np.linalg.det(A), prod=s[0] * s[1],
    sqrt2_inv=1 / math.sqrt(2), sqrt10_inv=1 / math.sqrt(10))

# 18.1.4 节：UR5e 肩关节 θ1 = 30°、肘关节 θ2 = 60°，上臂与前臂长度取自零件库关节表
l1, l2 = ur5e_links()
t1, t2 = math.radians(30), math.radians(60)
p, J = planar2(t1, t2, l1, l2)
Uj, sj, Vj = svd_fixed(J)
out(l1=l1, l2=l2, J=tex(J, 4), px=p[0], py=p[1],
    js1=sj[0], js2=sj[1], ratio=sj[0] / sj[1],
    ju1=vec(Uj[:, 0], 4), ju2=vec(Uj[:, 1], 4), jv1=vec(Vj[:, 0], 4), jv2=vec(Vj[:, 1], 4),
    ju1_deg=math.degrees(math.atan2(Uj[1, 0], Uj[0, 0])), ju2_deg=math.degrees(math.atan2(Uj[1, 1], Uj[0, 1])),
    jdet=np.linalg.det(J), jdet_formula=l1 * l2 * math.sin(t2),
    # 对照：只转一个关节（1 rad/s）时末端的速度大小
    only1=np.linalg.norm(J[:, 0]), only2=np.linalg.norm(J[:, 1]))
