"""算例 10.3.1、10.3.2：柱面坐标（极坐标）下的速度、加速度。

算例 10.3.1：零件库 SCARA（l1 = 0.35 m，l2 = 0.25 m）。某一时刻 θ1 = 30°、θ2 = 90°，θ̇1 = 1.0 rad/s、θ̇2 = −1.5 rad/s，
  两个关节的角加速度为零；丝杠以 0.1 m/s 下降。由式 (10.3.11)～(10.3.13) 求末端的柱面坐标 (ρ, φ, z) 及其导数，
  按式 (10.3.8)、(10.3.9) 求速度、加速度的径向、横向、竖直分量。
  核对：由正运动学写出直角坐标 x(t)、y(t)，数值求二阶导数，再投影到 e_ρ、e_φ 上，结果一致。
算例 10.3.2：柱面坐标机器人的手臂以 ρ̇ = 0.2 m/s 匀速伸出，同时以 φ̇ = 1.0 rad/s 匀速转动，ρ = 0.5 m 时的加速度；
  与直角坐标数值求导核对；手爪连同零件 2 kg 所需的横向力。
"""
import math

import numpy as np

from _kin import cyl_basis, d1, d2
from bookout import out

l1, l2 = 0.35, 0.25
th1, th2 = math.radians(30), math.radians(90)
w1, w2 = 1.0, -1.5                     # θ̇1、θ̇2，rad/s
zdot = -0.1                            # 丝杠下降，m/s


def joints(t):
    return th1 + w1 * t, th2 + w2 * t


def xyz(t):                            # SCARA 正运动学（12.3 节）
    q1, q2 = joints(t)
    return np.array([l1 * math.cos(q1) + l2 * math.cos(q1 + q2), l1 * math.sin(q1) + l2 * math.sin(q1 + q2), 0.242 + zdot * t])


# 式 (10.3.11)–(10.3.13)：ρ、φ 及其导数（解析）
rho = math.sqrt(l1 ** 2 + l2 ** 2 + 2 * l1 * l2 * math.cos(th2))
beta = math.atan2(l2 * math.sin(th2), l1 + l2 * math.cos(th2))
phi = th1 + beta
rhod = -l1 * l2 * math.sin(th2) * w2 / rho
rhodd = (-l1 * l2 * math.cos(th2) * w2 ** 2 - rhod ** 2) / rho          # θ̈2 = 0
dbeta = (l2 ** 2 + l1 * l2 * math.cos(th2)) / rho ** 2                   # dβ/dθ2
phid = w1 + dbeta * w2
d2beta = -l1 * l2 * math.sin(th2) * (l1 ** 2 - l2 ** 2) / rho ** 4        # d²β/dθ2²
phidd = d2beta * w2 ** 2                                                  # θ̈1 = θ̈2 = 0

# 与数值求导核对 ρ(t)、φ(t)
rho_t = lambda t: math.hypot(*xyz(t)[:2])
phi_t = lambda t: math.atan2(xyz(t)[1], xyz(t)[0])
assert abs(rho_t(0) - rho) < 1e-12 and abs(phi_t(0) - phi) < 1e-12
assert abs(d1(rho_t, 0, 1e-5) - rhod) < 1e-8 and abs(d2(rho_t, 0, 1e-4) - rhodd) < 1e-5
assert abs(d1(phi_t, 0, 1e-5) - phid) < 1e-8 and abs(d2(phi_t, 0, 1e-4) - phidd) < 1e-5

# 式 (10.3.8)、(10.3.9)
v_rho, v_phi, v_z = rhod, rho * phid, zdot
a_rho = rhodd - rho * phid ** 2
a_phi = rho * phidd + 2 * rhod * phid
a_cent, a_cor, a_ang = -rho * phid ** 2, 2 * rhod * phid, rho * phidd

# 核对：直角坐标数值求导后投影到局部基
er, ep, ez = cyl_basis(phi)
v_num, a_num = d1(xyz, 0, 1e-5), d2(xyz, 0, 1e-4)
assert np.allclose([v_num @ er, v_num @ ep, v_num @ ez], [v_rho, v_phi, v_z], atol=1e-8)
assert np.allclose([a_num @ er, a_num @ ep, a_num @ ez], [a_rho, a_phi, 0.0], atol=1e-5)
a_xy = a_rho * er + a_phi * ep
speed = math.sqrt(v_rho ** 2 + v_phi ** 2 + v_z ** 2)
assert abs(speed - np.linalg.norm(v_num)) < 1e-8

# ---------------------------------------------------------------- 算例 10.3.2
rd2, pd2, r2 = 0.2, 1.0, 0.5
a2_rho, a2_phi = -r2 * pd2 ** 2, 2 * rd2 * pd2
m = 2.0
xy2 = lambda t: np.array([(r2 + rd2 * t) * math.cos(pd2 * t), (r2 + rd2 * t) * math.sin(pd2 * t)])
an = d2(xy2, 0, 1e-4)
assert np.allclose(an, [a2_rho, a2_phi], atol=1e-6)        # t = 0 时 e_ρ = x̂、e_φ = ŷ

out(l1=l1, l2=l2, rho=rho, phi_deg=math.degrees(phi), beta_deg=math.degrees(beta), rhod=rhod, rhodd=rhodd,
    dbeta=dbeta, phid=phid, phidd=phidd, v_rho=v_rho, v_phi=v_phi, v_z=v_z, speed=speed,
    a_rho=a_rho, a_phi=a_phi, a_cent=a_cent, a_cor=a_cor, a_ang=a_ang, rhodd_term=rhodd,
    a_mag=float(math.hypot(a_rho, a_phi)), ax=a_xy[0], ay=a_xy[1], vx=v_num[0], vy=v_num[1],
    rd2=rd2, pd2=pd2, r2=r2, a2_rho=a2_rho, a2_phi=a2_phi, a2_mag=math.hypot(a2_rho, a2_phi),
    m=m, F_side=m * a2_phi)
