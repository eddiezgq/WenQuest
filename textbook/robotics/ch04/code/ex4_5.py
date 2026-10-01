"""4.5 节的算例。

算例 4.5.1：由旋转矩阵求 ZYX 欧拉角（偏航 ψ、俯仰 θ、横滚 φ），再合成回去核对。
算例 4.5.2：万向节锁——俯仰接近 90° 时，姿态的微小变化使横滚和偏航大幅跳变；俯仰恰为 90° 时只能确定 ψ − φ。
"""
import math

import numpy as np

from _rot import is_rotation, rot_axis, rot_x, rot_y, rot_z
from bookout import out, tex

d, deg = math.radians, math.degrees


def wrap(a):
    """角度化到 (−180°, 180°]。"""
    a = (a + 180.0) % 360.0 - 180.0
    return 180.0 if a == -180.0 else a


def zyx(psi, th, phi):
    """式 (4.5.3)：R = Rot(z,ψ) Rot(y,θ) Rot(x,φ)。"""
    return rot_z(psi) @ rot_y(th) @ rot_x(phi)


def zyx_angles(R):
    """式 (4.5.4)：取 cos θ ≥ 0 的一组解。"""
    th = math.atan2(-R[2, 0], math.hypot(R[0, 0], R[1, 0]))
    psi = math.atan2(R[1, 0], R[0, 0])
    phi = math.atan2(R[2, 1], R[2, 2])
    return psi, th, phi


# 定理 4.5.1：绕固定轴 x→y→z 与绕自身轴 z→y→x 相同
a, b, c = d(20), d(-35), d(50)
fixed = rot_z(c) @ rot_y(b) @ rot_x(a)           # 绕固定轴依次 x(a), y(b), z(c)：左乘
body = np.eye(3)
for M in (rot_z(c), rot_y(b), rot_x(a)):          # 绕自身轴依次 z(c), y(b), x(a)：右乘
    body = body @ M
assert np.allclose(fixed, body)

# 算例 4.5.1：算例 4.2.3 中“绕固定轴”的结果 Rot(x,45°) Rot(z,30°)
R = rot_x(d(45)) @ rot_z(d(30))
psi, th, phi = zyx_angles(R)
assert is_rotation(R) and np.allclose(zyx(psi, th, phi), R)
# 另一组解：θ' = π − θ，ψ' = ψ + π，φ' = φ + π
assert np.allclose(zyx(psi + math.pi, math.pi - th, phi + math.pi), R)

# 算例 4.5.2：俯仰 89.9°，再绕固定 x 轴转 0.1°
R0 = zyx(d(10), d(89.9), d(20))
R1 = rot_axis([1, 0, 0], d(0.1)) @ R0
a0, a1 = zyx_angles(R0), zyx_angles(R1)
change = float(np.degrees(np.arccos(np.clip((np.trace(R0.T @ R1) - 1) / 2, -1, 1))))
jump_psi, jump_phi = deg(a1[0] - a0[0]), deg(a1[2] - a0[2])
assert abs(change - 0.1) < 1e-9 and abs(jump_psi) > 10 * change

# 俯仰恰为 90°：只有 ψ − φ 被确定
L1, L2 = zyx(d(40), d(90), d(10)), zyx(d(70), d(90), d(40))
assert np.allclose(L1, L2)

# 图 4.5.2 的数据：俯仰从 80° 扫到 89.99°，同样的 0.1° 扰动引起的偏航跳变
pitches = list(np.linspace(80, 89.99, 120))
jumps = []
for p in pitches:
    A0 = zyx(d(10), d(p), d(20))
    A1 = rot_axis([1, 0, 0], d(0.1)) @ A0
    jumps.append(abs(deg(zyx_angles(A1)[0] - zyx_angles(A0)[0])))

out(R=tex(R), psi=deg(psi), th=deg(th), phi=deg(phi), psi2=wrap(deg(psi + math.pi)), th2=wrap(deg(math.pi - th)), phi2=wrap(deg(phi + math.pi)),
    r31=R[2, 0], r21=R[1, 0], r11=R[0, 0], r32=R[2, 1], r33=R[2, 2],
    psi0=deg(a0[0]), phi0=deg(a0[2]), psi1=deg(a1[0]), phi1=deg(a1[2]), jump_psi=jump_psi, jump_phi=jump_phi,
    L=tex(L1), _pitches=pitches, _jumps=jumps)
