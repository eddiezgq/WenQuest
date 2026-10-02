"""3.6 节的算例。

算例 3.6.1：UR5e 在零位（各关节角为 0）时，关节 1 以 60°/s 转动。法兰盘中心的速度 v = ω × r：
           分别以轴上两个不同的点为参考点计算；再用“转过一个小角度后的位置差 / 时间”数值求导核对。
           求示教降速 250 mm/s 所允许的关节 1 最大转速；求法兰盘中心的向心加速度。
算例 3.6.2：关节 2（水平轴，方向 −y，过点 (0, −0.138, 0.163) m）以 30°/s 转动，法兰盘中心的速度。
算例 3.6.3：地球自转：上海（北纬约 31.2°）地面一点随地球转动的速度。
另外验证：平面转动的速度公式；两个过同一点的角速度同时作用时，速度等于两者之和叉乘 r。
"""
import math

import numpy as np

from _vec import d, skew, unit
from bookout import out, vec


def rot_about(axis, point, t, p):
    """把点 p 绕过 point、方向为 axis 的直线转过 t（罗德里格斯公式，第 4 章 4.4 节）。"""
    w = unit(axis)
    K = skew(w)
    R = np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K
    return point + R @ (p - point)


# UR5e 零位时法兰盘中心的位置（与第 12 章算例 12.1.2 相同，机座坐标系 {s}，单位 m）
H1, W1, L1, W2, L2, W3, H2, W4 = 0.163, 0.138, 0.425, 0.131, 0.392, 0.127, 0.1, 0.1
p = np.array([-L1 - L2, -W1 + W2 - W3 - W4, H1 - H2])

# ---------------------------------------------------------------- 算例 3.6.1 关节 1
w1 = d(60)                                      # rad/s
axis1, q1 = np.array([0, 0, 1.0]), np.array([0, 0, H1])
omega1 = w1 * axis1
v1 = np.cross(omega1, p - q1)                   # 参考点取关节 1 轴上的 q1
v1b = np.cross(omega1, p - np.zeros(3))         # 参考点取轴上的原点
assert np.allclose(v1, v1b)                     # 式 (3.6.6)：与参考点在轴上的位置无关
assert np.allclose(v1, skew(omega1) @ (p - q1))  # 式 (3.6.5)
h = 1e-6                                        # s
v1_num = (rot_about(axis1, q1, w1 * h, p) - rot_about(axis1, q1, -w1 * h, p)) / (2 * h)
assert np.allclose(v1_num, v1, atol=1e-8)       # 数值求导核对
rho1 = math.hypot(p[0], p[1])                   # 到关节 1 轴的距离
assert abs(np.linalg.norm(v1) - w1 * rho1) < 1e-12
v_lim = 0.25                                    # m/s，手动降速模式的上限
w1_max = v_lim / rho1                           # rad/s
a1 = np.cross(omega1, np.cross(omega1, p - q1))  # 式 (3.6.8)
rperp = (p - q1) - ((p - q1) @ axis1) * axis1
assert np.allclose(a1, -w1 ** 2 * rperp)
# 数值求二阶导数核对
a1_num = (rot_about(axis1, q1, w1 * 1e-4, p) - 2 * p + rot_about(axis1, q1, -w1 * 1e-4, p)) / 1e-8
assert np.allclose(a1_num, a1, atol=1e-5)

# ---------------------------------------------------------------- 算例 3.6.2 关节 2
w2 = d(30)
axis2, q2 = np.array([0, -1.0, 0]), np.array([0, -W1, H1])
omega2 = w2 * axis2
v2 = np.cross(omega2, p - q2)
q2b = q2 + 0.3 * axis2                          # 轴上另一点
assert np.allclose(v2, np.cross(omega2, p - q2b))
v2_num = (rot_about(axis2, q2, w2 * h, p) - rot_about(axis2, q2, -w2 * h, p)) / (2 * h)
assert np.allclose(v2_num, v2, atol=1e-8)
rho2 = np.linalg.norm((p - q2) - ((p - q2) @ unit(axis2)) * unit(axis2))
assert abs(np.linalg.norm(v2) - w2 * rho2) < 1e-12

# ---------------------------------------------------------------- 两个角速度同时作用（过同一点的两根轴）
rng = np.random.default_rng(2)
for _ in range(50):
    wa, wb, r = rng.normal(size=(3, 3))
    assert np.allclose(np.cross(wa, r) + np.cross(wb, r), np.cross(wa + wb, r))

# ---------------------------------------------------------------- 平面转动的速度
x0, y0, th, thd = 0.2, 0.1, d(30), 0.8          # 4.1 节的角点，转角，角速度 rad/s
Rp = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])
dR = thd * np.array([[-math.sin(th), -math.cos(th)], [math.cos(th), -math.sin(th)]])
pp = Rp @ [x0, y0]
assert np.allclose(dR @ [x0, y0], thd * np.array([-pp[1], pp[0]]))   # 式 (3.6.2)

# ---------------------------------------------------------------- 算例 3.6.3 地球自转
wE = 7.292115e-5                                # rad/s，地球自转角速度（相对恒星）
RE = 6371.0e3                                   # m，地球平均半径
lat = d(31.2)
v_eq = wE * RE
v_sh = wE * RE * math.cos(lat)
T_sid = 2 * math.pi / wE                        # 恒星日，s

out(
    p=vec(p, 3), px=p[0], py=p[1], pz=p[2],
    w1=w1, v1=vec(v1, 4), v1x=v1[0], v1y=v1[1], v1_len=float(np.linalg.norm(v1)), rho1=rho1,
    v1_num_err=float(np.abs(v1_num - v1).max()),
    w1_max=w1_max, w1_max_deg=math.degrees(w1_max), a1=vec(a1, 4), a1_len=float(np.linalg.norm(a1)),
    w2=w2, r2=vec(p - q2, 3), v2=vec(v2, 4), v2x=v2[0], v2z=v2[2], v2_len=float(np.linalg.norm(v2)), rho2=rho2,
    wE=wE, v_eq=v_eq, v_sh=v_sh, T_sid_h=T_sid / 3600,
)
