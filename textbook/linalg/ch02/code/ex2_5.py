"""2.5 节：叉积与混合积——负载对肩关节的力矩 r × F；三个探测点确定的平面的法向量与面积；四面体体积。"""
import math

import numpy as np

from bookout import out, vec
from _arm import ur5e_links

g = 9.80665
l1, l2 = ur5e_links()
r = np.array([l1 + l2, 0.0, 0.0])          # 手臂水平伸向 x 方向：肩关节到腕心
F = np.array([0.0, 0.0, -2 * g])          # 2 kg 负载的重力
tau = np.cross(r, F)
out(r=vec(r, 3), F=vec(F, 3), tau=vec(tau, 3), tau_len=float(np.linalg.norm(tau)))
# 手算的例子
u, v = np.array([1.0, 2.0, 3.0]), np.array([4.0, 5.0, 6.0])
uxv = np.cross(u, v)
out(uxv=vec(uxv, 0), d1=float(uxv @ u), d2=float(uxv @ v), lag=float(np.linalg.norm(uxv) ** 2), lag2=float((u @ u) * (v @ v) - (u @ v) ** 2))
# 叉积不满足结合律：e1 × (e1 × e2) 与 (e1 × e1) × e2
e1, e2, e3 = np.eye(3)
out(left=vec(np.cross(e1, np.cross(e1, e2)), 0), right=vec(np.cross(np.cross(e1, e1), e2), 0))
# 测头在零件上表面测得三个点（单位 mm）
P1, P2, P3 = np.array([400.0, 100.0, 50.0]), np.array([600.0, 120.0, 52.0]), np.array([450.0, 300.0, 49.0])
n = np.cross(P2 - P1, P3 - P1)
out(P1=vec(P1, 0), P2=vec(P2, 0), P3=vec(P3, 0), u12=vec(P2 - P1, 0), u13=vec(P3 - P1, 0), n=vec(n, 0),
    area=float(np.linalg.norm(n) / 2), nunit=vec(n / np.linalg.norm(n), 4), nlen=float(np.linalg.norm(n)),
    tilt=float(np.degrees(np.arccos(n[2] / np.linalg.norm(n)))))
# 混合积：平行六面体体积
a, b, c = np.array([2.0, 0, 0]), np.array([1.0, 3, 0]), np.array([1.0, 1, 4])
out(triple=float(a @ np.cross(b, c)), detabc=float(np.linalg.det(np.c_[a, b, c])), tetra=float(a @ np.cross(b, c) / 6))
# 用叉积求夹角：arctan2(‖u × v‖, u·v)，夹角很小时比 arccos 准确
p, q = np.array([1.0, 0, 0]), np.array([1.0, 1e-8, 0])
out(ang_acos=float(np.arccos(np.clip(p @ q / (np.linalg.norm(p) * np.linalg.norm(q)), -1, 1))), ang_atan=float(math.atan2(np.linalg.norm(np.cross(p, q)), p @ q)))
