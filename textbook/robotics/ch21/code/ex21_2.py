"""21.2 节的计算：姿态与位置的耦合。

算例 21.2.1  X2 在同一高度上以 2 m/s² 向前加速：倾角、总推力、每个旋翼的推力、加速度计读数；
             保持高度时的最大水平加速度（全推力；倾角限制 30°，示意值）。
算例 21.2.2  给定加速度 (1.5, −1.0, 0.8) m/s² 与偏航角 60°（示意值）：由定理 21.2.1 的构造法和欧拉角公式两种方法求姿态，
             核对由 R 反求的 ZYX 偏航角就是给定的 ψ；比较偏航角为 0 时的姿态。
算例 21.2.3  协调转弯：车速 4 m/s、半径 5 m 的水平圆周（示意值）。倾角、推力、物体角速度（式 (21.2.7) 与差商两种方法），
             IMU 不在质心时加速度计的读数。
算例 21.2.4  加速度在 0.2 s 内由 0 线性增大到 2 m/s²（加加速度 10 m/s³）：俯仰角速度由式 (21.2.10) 与 θ = atan(a/𝔤) 求导两种方法；
             积分角速度得到终了的俯仰角。
"""
import math

import numpy as np

from _uav import EZ, G, Wmat, attitude, eul, eul_of, flat, logso3, rotz, skew, x2
from bookout import out, tex, vec

P = x2()
m, fmax4 = P["m"], 4 * P["fmax"]
W = m * G

# ---------------------------------------------------------------- 算例 21.2.1
a1 = 2.0
t1 = np.array([a1, 0, 0]) + G * EZ
f1 = m * np.linalg.norm(t1)
R1, th1, ph1 = attitude(t1 / np.linalg.norm(t1), 0.0)
assert abs(th1 - math.atan2(a1, G)) < 1e-14 and abs(ph1) < 1e-14
th1_deg = math.degrees(th1)
f1_ratio = (f1 / W - 1) * 100
f1_rotor = f1 / 4
spec1 = R1.T @ t1                                       # 比力在 {b} 中的分量
assert np.allclose(spec1[:2], 0, atol=1e-14) and abs(spec1[2] - f1 / m) < 1e-12
# 保持高度时的最大水平加速度
tilt_full = math.acos(W / fmax4)
a_full = G * math.tan(tilt_full)
assert abs(m * math.hypot(a_full, G) - fmax4) < 1e-9
tilt_lim = math.radians(30)
a_lim = G * math.tan(tilt_lim)
f_lim = W / math.cos(tilt_lim)

# ---------------------------------------------------------------- 算例 21.2.2
a2 = np.array([1.5, -1.0, 0.8])
psi2 = math.radians(60)
t2 = a2 + G * EZ
f2 = m * np.linalg.norm(t2)
zb2 = t2 / np.linalg.norm(t2)
R2, th2, ph2 = attitude(zb2, psi2)                    # attitude() 内部已核对构造法与欧拉角公式一致
ps_back, th_back, ph_back = eul_of(R2)
assert abs(ps_back - psi2) < 1e-12 and abs(th_back - th2) < 1e-12 and abs(ph_back - ph2) < 1e-12
assert np.allclose(R2[:, 2], zb2) and np.allclose(R2.T @ R2, np.eye(3)) and abs(np.linalg.det(R2) - 1) < 1e-12
tilt2 = math.degrees(math.acos(zb2[2]))
R2b, th2b, ph2b = attitude(zb2, 0.0)
assert np.allclose(R2b[:, 2], zb2)
# 两个姿态只差绕 z_b 的转动：R2b^T R2 = Rot(ẑ, α)
D = R2b.T @ R2
assert abs(D[2, 2] - 1) < 1e-12
yaw_rel = math.degrees(math.atan2(D[1, 0], D[0, 0]))

# ---------------------------------------------------------------- 算例 21.2.3：协调转弯（逆时针，绕 {s} 原点）
v3, rho3 = 4.0, 5.0
Om = v3 / rho3
ac = v3 ** 2 / rho3
t3 = 1.3                                                  # 任取一个时刻


def circle(t, r=rho3, w=Om, h=2.0):
    """水平圆周 p(t) 及其 1～4 阶导数。"""
    c, s = math.cos(w * t), math.sin(w * t)
    p = np.array([r * c, r * s, h])
    d1 = np.array([-r * w * s, r * w * c, 0])
    d2 = np.array([-r * w * w * c, -r * w * w * s, 0])
    d3 = np.array([r * w ** 3 * s, -r * w ** 3 * c, 0])
    d4 = np.array([r * w ** 4 * c, r * w ** 4 * s, 0])
    return [p, d1, d2, d3, d4]


psi3 = Om * t3 + math.pi / 2                               # 机头沿速度方向
F3 = flat(circle(t3), psi3, Om, 0.0, m)
ph3, th3 = F3["phi"], F3["th"]
assert abs(th3) < 1e-12 and abs(ph3 + math.atan2(ac, G)) < 1e-12            # 向左压坡度：φ < 0
w3 = F3["w"]
assert np.allclose(w3, Om * np.array([0, math.sin(ph3), math.cos(ph3)]), atol=1e-12)
assert np.allclose(w3, Wmat(ph3, th3) @ np.array([0, 0, Om]), atol=1e-12)
assert np.allclose(F3["dw"], 0, atol=1e-12)
# 差商核对：ω_b ≈ log(R(t)^T R(t+h))/h
h = 1e-6
Rp = flat(circle(t3 + h), psi3 + Om * h, Om, 0.0, m)["R"]
Rm = flat(circle(t3 - h), psi3 - Om * h, Om, 0.0, m)["R"]
assert np.allclose(logso3(Rm.T @ Rp) / (2 * h), w3, atol=1e-7)
f3 = F3["f"]
lap = 2 * math.pi / Om
# IMU 在质心下方 r_imu：加速度计读数 = R^T t + ω̇ × r + ω × (ω × r)
r_imu = P["imu"]
spec_com = F3["R"].T @ (circle(t3)[2] + G * EZ)
spec_imu = spec_com + np.cross(F3["dw"], r_imu) + np.cross(w3, np.cross(w3, r_imu))
lever = spec_imu - spec_com

# ---------------------------------------------------------------- 算例 21.2.4：加速度线性增大
j4, T4 = 10.0, 0.2


def ramp(t):
    a = j4 * t
    return [np.zeros(3), np.array([0.5 * j4 * t * t, 0, 0]), np.array([a, 0, 0]), np.array([j4, 0, 0]), np.zeros(3)]


wy0 = flat(ramp(0.0), 0.0, 0.0, 0.0, m)["w"][1]
assert abs(wy0 - j4 / G) < 1e-12
tm = 0.1
wym = flat(ramp(tm), 0.0, 0.0, 0.0, m)["w"][1]
am = j4 * tm
assert abs(wym - j4 * G / (G * G + am * am)) < 1e-12              # d/dt atan(a/𝔤)
# 积分俯仰角速度（辛普森法）得到终了的俯仰角，与 atan(2/𝔤) 核对
n = 200
ts = np.linspace(0, T4, n + 1)
ys = np.array([flat(ramp(t), 0.0, 0.0, 0.0, m)["w"][1] for t in ts])
th_int = T4 / n / 3 * (ys[0] + ys[-1] + 4 * ys[1:-1:2].sum() + 2 * ys[2:-1:2].sum())
assert abs(th_int - math.atan2(j4 * T4, G)) < 1e-10
peaks = {Tr: (2.0 / Tr) / G for Tr in (0.2, 0.1, 0.05)}             # 起始时刻的俯仰角速度 = 加加速度/𝔤

out(a1=a1, th1_deg=th1_deg, f1=f1, f1_ratio=f1_ratio, f1_rotor=f1_rotor, spec1=spec1[2], W=W,
    tilt_full_deg=math.degrees(tilt_full), a_full=a_full, a_lim=a_lim, f_lim=f_lim, fmax4=fmax4,
    f2=f2, zb2=vec(zb2, 4), th2_deg=math.degrees(th2), ph2_deg=math.degrees(ph2), tilt2=tilt2,
    R2=tex(R2, 4), th2b_deg=math.degrees(th2b), ph2b_deg=math.degrees(ph2b), yaw_rel=yaw_rel,
    t2z=t2[2], t2n=np.linalg.norm(t2),
    v3=v3, rho3=rho3, Om=Om, ac=ac, ph3_deg=math.degrees(ph3), bank3_deg=abs(math.degrees(ph3)), f3=f3, lap=lap,
    w3x=w3[0], w3y=w3[1], w3z=w3[2], spec_com=spec_com[2], lever_x=lever[0], lever_y=lever[1], lever_z=lever[2],
    lever_n=np.linalg.norm(lever), r_imu=-r_imu[2],
    j4=j4, T4=T4, wy0=wy0, wy0_deg=math.degrees(wy0), wym=wym, th_int_deg=math.degrees(th_int),
    pk02=peaks[0.2], pk01=peaks[0.1], pk005=peaks[0.05], pk005_deg=math.degrees(peaks[0.05]))
