"""3.1 节的算例。

算例 3.1.1：夹爪到零件的位移矢量 d，在机器人基座坐标系 {a} 中的分量为 (0.30, 0.20, 0) m；相机坐标系 {b}
           相对 {a} 绕竖直轴转过 30°。按“投影”的几何办法求 d 在 {b} 中的分量，并验证两个坐标系量出的长度相同。
           另用 3.3 节的变换矩阵复算一次，两种办法必须一致。
算例 3.1.2：零件到夹具的位移 e 在 {a} 中为 (−0.10, 0.25, 0) m。求夹爪到夹具的位移 d + e；
           再演示把 {b} 中的 d 与 {a} 中的 e 直接相加的错误结果，给出误差。
"""
import math

import numpy as np

from _vec import d, rot_z
from bookout import out

# ---------------------------------------------------------------- 算例 3.1.1
d_a = np.array([0.30, 0.20, 0.0])          # m，{a} 中的分量
beta = d(30)                               # {b} 相对 {a} 绕 z 轴转过的角度，rad

L_a = math.sqrt(d_a @ d_a)                 # 式 (3.1.4)：由 {a} 中的分量求长度
phi_a = math.atan2(d_a[1], d_a[0])         # d 与 x_a 轴的夹角
phi_b = phi_a - beta                       # d 与 x_b 轴的夹角：从 x_b 量起，少转了 β
d_b = np.array([L_a * math.cos(phi_b), L_a * math.sin(phi_b), 0.0])   # 投影到 {b} 的两根轴上

# 第二种办法（3.3 节）：d_b = R_abᵀ d_a，R_ab 的列是 {b} 的三根轴在 {a} 中的分量
R_ab = rot_z(beta)
assert np.allclose(R_ab.T @ d_a, d_b)
L_b = math.sqrt(d_b @ d_b)
assert abs(L_a - L_b) < 1e-12                                   # 长度是不变量
# 第三种办法：分量 = 矢量与各轴单位矢量的点积（3.2 节）
xb, yb = R_ab[:, 0], R_ab[:, 1]
assert abs(d_a @ xb - d_b[0]) < 1e-12 and abs(d_a @ yb - d_b[1]) < 1e-12

# ---------------------------------------------------------------- 算例 3.1.2
e_a = np.array([-0.10, 0.25, 0.0])
s_a = d_a + e_a                            # 正确：同一坐标系中的分量相加
wrong = d_b + e_a                          # 错误：{b} 中的分量与 {a} 中的分量相加
err = np.linalg.norm(wrong - s_a)
# 正确的做法也可以全在 {b} 中做：e_b = R_abᵀ e_a，d_b + e_b 再换回 {a}
assert np.allclose(R_ab @ (d_b + R_ab.T @ e_a), s_a)

out(
    L=L_a, phi_a_deg=math.degrees(phi_a), phi_b_deg=math.degrees(phi_b),
    db1=d_b[0], db2=d_b[1], L_b=L_b, c30=math.cos(beta),
    s1=s_a[0], s2=s_a[1], s_len=float(np.linalg.norm(s_a)),
    w1=wrong[0], w2=wrong[1], w_len=float(np.linalg.norm(wrong)), err=err, err_mm=err * 1000,
)
