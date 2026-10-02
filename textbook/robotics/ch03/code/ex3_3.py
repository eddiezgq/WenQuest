"""3.3 节的算例。

算例 3.3.1：绕竖直轴转 30° 的相机，用方向余弦矩阵复算算例 3.1.1。
算例 3.3.2：俯视传送带的相机。相机坐标系 {b} 的三根轴在机座坐标系 {a} 中的分量已知（光轴 z_b 向下并偏 20°），
           由此写出方向余弦矩阵 R_ab，检查它的正交性与行列式；相机测得零件相对相机的位移 d_b，求 d_a，并反算回去。
算例 3.3.3：同一个相机经支架安装：支架 {c} 相对 {a} 绕 z 轴转 −90°，相机 {b} 相对支架绕 x 轴转 160°。
           验证 R_ab = R_ac R_cb。
另外：验证 R 保持点积、叉积（定理 3.3.3、3.3.4），左手系时叉积反号。
"""
import math

import numpy as np

from _vec import d, is_rotation, rot_x, rot_z
from bookout import out, tex, vec

c20, s20 = math.cos(d(20)), math.sin(d(20))
xb = np.array([0.0, -1.0, 0.0])
yb = np.array([-c20, 0.0, s20])
zb = np.array([-s20, 0.0, -c20])
R_ab = np.column_stack([xb, yb, zb])             # 第 j 列 = {b} 的第 j 根轴在 {a} 中的分量

# 方向余弦：r_ij = (轴 i of {a})·(轴 j of {b}) = cos(夹角)
A_axes = np.eye(3)
DC = np.array([[A_axes[:, i] @ R_ab[:, j] for j in range(3)] for i in range(3)])
assert np.allclose(DC, R_ab)
ang = np.degrees(np.arccos(np.clip(R_ab, -1, 1)))   # 九个夹角，度

assert np.allclose(R_ab.T @ R_ab, np.eye(3))        # 定理 3.3.2：正交
det = float(np.linalg.det(R_ab))
mixed = float(np.cross(xb, yb) @ zb)                # 式 (3.2.12)：行列式 = 混合积
assert abs(det - 1) < 1e-12 and abs(mixed - 1) < 1e-12

d_b = np.array([0.12, -0.05, 0.60])                 # 相机测得的位移，m
d_a = R_ab @ d_b                                    # 式 (3.3.3)
# 第二种算法：逐轴展开 d = d1 x_b + d2 y_b + d3 z_b
assert np.allclose(d_a, d_b[0] * xb + d_b[1] * yb + d_b[2] * zb)
back = R_ab.T @ d_a                                 # 式 (3.3.4)
assert np.allclose(back, d_b)
assert abs(np.linalg.norm(d_a) - np.linalg.norm(d_b)) < 1e-12

# ---------------------------------------------------------------- 算例 3.3.3 经支架安装
R_ac = rot_z(d(-90))
R_cb = rot_x(d(160))
assert np.allclose(R_ac @ R_cb, R_ab)               # 式 (3.3.6)
assert is_rotation(R_ac) and is_rotation(R_cb)

# ---------------------------------------------------------------- 算例 3.3.1：复算算例 3.1.1
R30 = rot_z(d(30))
d1_a = np.array([0.30, 0.20, 0.0])
d1_b = R30.T @ d1_a
Lp, ph = math.hypot(0.30, 0.20), math.atan2(0.20, 0.30) - d(30)       # 3.1 节的投影法
assert np.allclose(d1_b, [Lp * math.cos(ph), Lp * math.sin(ph), 0.0])

# ---------------------------------------------------------------- 保持点积与叉积
rng = np.random.default_rng(7)
for _ in range(200):
    u, v = rng.normal(size=(2, 3))
    assert abs((R_ab @ u) @ (R_ab @ v) - u @ v) < 1e-12                       # 定理 3.3.3
    assert np.allclose(np.cross(R_ab @ u, R_ab @ v), R_ab @ np.cross(u, v))   # 定理 3.3.4
    M = np.diag([1.0, 1.0, -1.0])                                             # 镜像反射，det = −1
    assert np.allclose(np.cross(M @ u, M @ v), -(M @ np.cross(u, v)))

out(
    c20=c20, s20=s20, R_ab=tex(R_ab, 4), R_abT=tex(R_ab.T, 4),
    d_a=tex(d_a, 4), d_a_vec=vec(d_a, 4), da1=d_a[0], da2=d_a[1], da3=d_a[2],
    L=float(np.linalg.norm(d_b)), depth=-d_a[2],
    ang11=ang[0, 0], ang13=ang[0, 2], ang33=ang[2, 2], ang31=ang[2, 0], ang21=ang[1, 0], ang32=ang[2, 1],
    R_ac=tex(R_ac, 4), R_cb=tex(R_cb, 4), c160=math.cos(d(160)), s160=math.sin(d(160)),
)
