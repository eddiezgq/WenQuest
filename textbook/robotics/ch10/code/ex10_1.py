"""算例 10.1.1：AGV 沿圆弧转弯，车间地面上静止的零件在 AGV 坐标系 {b} 中怎样运动。

地面坐标系 {s}：AGV 从原点出发，初始朝 +x，以 v = 0.5 m/s 沿半径 R0 = 2.0 m 的圆左转，圆心 C = (0, 2.0) m；
AGV 坐标系 {b}：原点在车体中心，x 朝前，y 朝左，随 AGV 运动。零件 P 在 {s} 中静止于 (2.0, 0.5) m。
按 p_b = R_sb^T (p_s − p_sb)（式 (5.1.3)）逐时刻换算，验证：在 {b} 中零件绕点 (0, R0) 作圆周运动，半径 |CP|，
速率 Ω|CP|；并用两种办法（数值求导、公式 ṗ_b = −Ω ẑ × p_b − (v, 0, 0)）求它在 {b} 中的速度，二者一致。
另给出同一参考系（地面）中两个坐标系对 P 的两组读数：直角坐标与极坐标。
"""
import math

import numpy as np

from _kin import d1, rotz, skew
from bookout import out

v, R0 = 0.5, 2.0                       # AGV 车速 m/s，转弯半径 m
Om = v / R0                            # 车体转动角速度 rad/s
C = np.array([0.0, R0, 0.0])           # 圆心，{s}
P = np.array([2.0, 0.5, 0.0])          # 零件，{s}


def agv(t):
    """AGV 在 {s} 中的位置 p_sb(t) 与姿态 R_sb(t)。"""
    psi = Om * t
    return C + R0 * np.array([math.sin(psi), -math.cos(psi), 0.0]), rotz(psi)


def p_b(t):
    o, R = agv(t)
    return R.T @ (P - o)                # 式 (5.1.3)


t1 = 6.0
pb1 = p_b(t1)
cb = np.array([0.0, R0, 0.0])          # 圆心在 {b} 中的位置（不随时间变化）
d = float(np.linalg.norm(P - C))
for t in np.linspace(0, 20, 81):       # 零件在 {b} 中始终距 (0, R0) 为 d
    assert abs(np.linalg.norm(p_b(t) - cb) - d) < 1e-12
    o, R = agv(t)
    assert abs(np.linalg.norm(R.T @ (C - o) - cb)) < 1e-12

vb_num = d1(p_b, t1, 1e-5)
vb_formula = -skew([0, 0, Om]) @ pb1 - np.array([v, 0, 0])
assert np.allclose(vb_num, vb_formula, atol=1e-9)
speed_b = float(np.linalg.norm(vb_formula))
assert abs(speed_b - Om * d) < 1e-12

# 同一参考系中的两个坐标系：直角坐标 (x, y) 与极坐标 (ρ, φ)
rho = math.hypot(P[0], P[1])
phi = math.atan2(P[1], P[0])
assert abs(rho * math.cos(phi) - P[0]) < 1e-12 and abs(rho * math.sin(phi) - P[1]) < 1e-12

o1, _ = agv(t1)
out(v=v, R0=R0, Om=Om, t1=t1, psi1_deg=math.degrees(Om * t1),
    ox1=o1[0], oy1=o1[1], pbx=pb1[0], pby=pb1[1], d=d, speed_b=speed_b,
    vbx=vb_formula[0], vby=vb_formula[1],
    rho=rho, phi_deg=math.degrees(phi), period=2 * math.pi / Om)
