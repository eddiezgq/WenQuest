"""11.1 节：关节即旋量。

(1) 表 11.1.1：七种关节（R、P、H、C、U、S、E）各自允许的运动旋量张成的子空间。秩就是关节的自由度 f；
    与之“功率为零”的力旋量（约束力旋量）张成的子空间维数为 6 − f（定理 11.1.1），用两种方法核对：
    奇异值分解求零空间；逐一验证 ℱᵀ𝒱 = 0 并用互易积 (6.6.10) 复核。
(2) 算例 11.1.1：滚珠丝杠花键轴。导程 20 mm 的丝杠，节距 h = 导程 / 2π；花键螺母带轴转 90° 而丝杠螺母不动时，
    轴沿自身轴线移动 hθ。用螺旋关节的旋量轴 (11.1.2) 的矩阵指数计算，与“先转后移”的几何算法及级数定义核对。
(3) 理想（无摩擦）螺旋副的约束力旋量：轴向力 F 必伴随扭矩 hF，算出 50 N 轴向力对应的扭矩。
"""
import math

import numpy as np

from _ch11 import exp6, expm_series, bracket, null_space, rot, screw_helical, screw_prismatic, screw_revolute
from bookout import T, out

z = np.array([0, 0, 1.0])
x = np.array([1.0, 0, 0])
y = np.array([0, 1.0, 0])
o = np.zeros(3)

# ---------------------------------------------------------------- (1) 七种关节：允许的运动旋量
h_demo = 0.02 / (2 * math.pi)        # 螺旋关节取导程 20 mm
joints = [
    ("R", T("转动关节", "revolute"), [screw_revolute(z, o)]),
    ("P", T("移动关节", "prismatic"), [screw_prismatic(z)]),
    ("H", T("螺旋副", "helical"), [screw_helical(z, o, h_demo)]),
    ("C", T("圆柱副", "cylindrical"), [screw_revolute(z, o), screw_prismatic(z)]),
    ("U", T("万向节", "universal"), [screw_revolute(x, o), screw_revolute(y, o)]),
    ("S", T("球关节", "spherical"), [screw_revolute(x, o), screw_revolute(y, o), screw_revolute(z, o)]),
    ("E", T("平面副", "planar"), [screw_revolute(z, o), screw_prismatic(x), screw_prismatic(y)]),
]

f_of = {}
for sym, name, twists in joints:
    V = np.column_stack(twists)                  # 6 × k，列为允许的运动旋量
    f = np.linalg.matrix_rank(V)
    W, rankVt = null_space(V.T)                  # 满足 Vᵀℱ = 0 的力旋量 ℱ = (m, f)：约束力旋量
    c = W.shape[1]
    assert f == rankVt and f + c == 6            # 定理 11.1.1：f + c = 6
    for Fw in W.T:                               # 功率 ℱᵀ𝒱 = m·ω + f·v = 0，式 (6.6.3)
        for Vt in V.T:
            assert abs(Fw @ Vt) < 1e-12
            # 互易积 (6.6.10)：把力旋量写成 (f, m)（方向在前、矩在后）后，与 𝒱 的互易积就是功率
            s1, v1, s2, v2 = Vt[:3], Vt[3:], Fw[3:], Fw[:3]
            assert abs(s1 @ v2 + s2 @ v1 - Fw @ Vt) < 1e-12
    f_of[sym] = (f, c)

# 各关节的约束力旋量的物理意义（转动关节：过轴的三个力 + 垂直于轴的两个力矩）
W_R, _ = null_space(np.column_stack(joints[0][2]).T)
# W_R 张成的空间应与 {力 x、y、z（作用线过原点），力矩 x、y} 张成的空间相同
basis_R = np.array([[0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0]], float).T
assert np.linalg.matrix_rank(np.column_stack([W_R, basis_R])) == 5

# 表 11.1.1 印在书上的 f、c（手写的整数）必须与计算一致
book = {"R": (1, 5), "P": (1, 5), "H": (1, 5), "C": (2, 4), "U": (2, 4), "S": (3, 3), "E": (3, 3)}
assert f_of == book, f_of

# ---------------------------------------------------------------- (2) 算例 11.1.1：滚珠丝杠花键轴
lead = 0.020                                     # 导程 (m/r)
h = lead / (2 * math.pi)                         # 节距 (m/rad)，6.1 节：导程 = 2πh
q_axis = np.array([0.6, 0.0, 0.0])               # 轴线位置：取零件库 SCARA 第 3、4 轴的水平位置
w_axis = np.array([0, 0, -1.0])                  # 方向：竖直向下（与 SCARA 关节 3 的正方向一致）
S_H = screw_helical(w_axis, q_axis, h)
th = math.radians(90)
E = exp6(S_H, th)
assert np.allclose(E, expm_series(bracket(S_H) * th), atol=1e-12)
# 几何算法（定理 6.4.2）：绕过 q 的轴转 θ，再沿轴移动 hθ
Rg = rot(w_axis, th)
pt = np.array([0.62, 0.0, 0.2])                  # 轴上一个随轴运动的点（离轴 0.02 m 的花键键齿）
p_geo = q_axis + Rg @ (pt - q_axis) + h * th * w_axis
p_exp = (E @ np.r_[pt, 1.0])[:3]
assert np.allclose(p_geo, p_exp, atol=1e-12)
dz = h * th                                      # 沿轴移动的距离
# 丝杠螺母补偿：轴相对丝杠螺母的螺旋运动 = 花键转角 − 丝杠螺母转角；补偿后二者相同，轴不升降
comp_deg = 90.0

# ---------------------------------------------------------------- (3) 理想螺旋副的约束力旋量
W_H, _ = null_space(S_H.reshape(6, 1).T)
F_axial = 50.0                                   # 轴向力 (N)
# 在 W_H 中找“沿轴的力 F + 沿轴的力矩 m”这一个：m·ω + f·v = 0 ⇒ m_ax = −h F_ax（沿 ω 方向计）
m_ax = -h * F_axial
Fw = np.r_[m_ax * w_axis + np.cross(q_axis, F_axial * w_axis), F_axial * w_axis]
assert abs(Fw @ S_H) < 1e-12
tau_needed = h * F_axial                         # 不让轴转所需的扭矩 (N·m)

out(h=h, h_mm=h * 1000, dz_mm=dz * 1000, comp_deg=comp_deg,
    tau=tau_needed, p_geo=p_geo.tolist(), z_end=p_exp[2])
