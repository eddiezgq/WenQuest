"""23.3 节的计算：旋量形式的牛顿-欧拉方程。

(1) 定理的数值核对：随机生成一个由 400 个质点组成的“刚体”（固定种子），任取物体坐标系、运动旋量与加速度：
    - 按各质点的牛顿第二定律求合力与合力矩（质点的加速度由刚体运动学 ẍ = ... 算出）；
    - 按式 (23.3.11)（质心坐标系）与式 (23.3.14)（任意物体坐标系，G_a = Adᵀ G Ad）算出的力旋量；三者一致。
    - 引理 23.3.1：[ad_{Ad_T V}] = [Ad_T][ad_V][Ad_T]⁻¹；式 (23.3.13) 与分块形式 (23.3.15) 一致。
(2) 算例 23.3.1：UR5e 在零位，关节 1 以 θ̇₁ = 1.2 rad/s、θ̈₁ = 6 rad/s²（示意值）转动，法兰上是夹爪 + SH-301 毛坯（算例 23.2.2）。
    求法兰对负载的力旋量和六维力/力矩传感器的读数。三种算法：质心坐标系的牛顿-欧拉方程再用 Adᵀ 换到法兰；
    直接在法兰坐标系用 G_b；把负载分成许多小块，沿精确的运动用有限差分求各块的加速度，按牛顿第二定律求和。
(3) 算例 23.3.2：打磨电主轴的陀螺力矩（示意值：砂轮 Ø100 mm、0.6 kg，12000 r/min，手腕以 1 rad/s 转动主轴的轴线），
    式 (23.3.17)；MuJoCo 核对（实验 23.3 的机器人场景用同一个模型）。
(4) 算例 23.3.3：自行车轮陀螺（示意值）：进动角速度 Ω = m𝔤l/(I₃ω)，式 (23.3.18)；MuJoCo 核对；不转时直接倒下。
(5) 习题答案。
"""
import math

import numpy as np

from _ch23 import (G0, GRIP_BOX, GRIP_C, GRIP_M, UR_M, UR_S, ad, adjoint, box_inertia, cyl_inertia, exp6, exp_twist, G_com, G_frame,
                   inv, mj_load, ne_wrench, sh301_blank, skew, tf)
from bookout import out, tex

rng = np.random.default_rng(23)

# ---------------------------------------------------------------- (1) 定理的数值核对
N = 400
mk = rng.uniform(0.01, 0.1, N)
xk = rng.normal(size=(N, 3)) * [0.2, 0.1, 0.05] + [0.3, -0.1, 0.2]     # 各质点在物体坐标系 {a} 中的位置
m = mk.sum()
c = (mk[:, None] * xk).sum(0) / m
Ia_c = sum(mi * ((r @ r) * np.eye(3) - np.outer(r, r)) for mi, r in zip(mk, xk - c))   # 对质心，{a} 的方向
Ga = G_frame(Ia_c, m, np.eye(3), c)                                  # 式 (23.3.15)：{a} 中的空间惯量
Va = rng.normal(size=6)
Vda = rng.normal(size=6)
w, v = Va[:3], Va[3:]
wd, vd = Vda[:3], Vda[3:]
# 质点的加速度（在 {a} 中表示，{a} 随物体运动）：ẍ = v̇ + ω × v + ω̇ × x + ω × (ω × x)
acc = vd + np.cross(w, v) + np.cross(wd, xk) + np.cross(w, np.cross(w, xk))
F_pt = np.r_[(np.cross(xk, mk[:, None] * acc)).sum(0), (mk[:, None] * acc).sum(0)]
F_ne = ne_wrench(Ga, Va, Vda)
err_ne = float(np.abs(F_pt - F_ne).max() / np.abs(F_pt).max())
assert err_ne < 1e-12
# 质心坐标系 {c}（方向与 {a} 相同）：G_c = diag(I_c, m I)，再用 F_a = [Ad_{T_ca}]ᵀ F_c 换回
T_ca = tf(np.eye(3), -c)                                             # {a} 相对 {c} 的位姿
A = adjoint(T_ca)
Gc = G_com(Ia_c, m)
assert np.allclose(A.T @ Gc @ A, Ga, atol=1e-14)                     # 式 (23.3.13)
F_c = ne_wrench(Gc, A @ Va, A @ Vda)
assert np.allclose(A.T @ F_c, F_ne, atol=1e-12)
# 引理 23.3.1
Tr = exp_twist(rng.normal(size=6))
X = rng.normal(size=6)
assert np.allclose(ad(adjoint(Tr) @ X), adjoint(Tr) @ ad(X) @ np.linalg.inv(adjoint(Tr)), atol=1e-12)
# 任意姿态的质心坐标系（主轴）也一样
lam, Q = np.linalg.eigh(Ia_c)
if np.linalg.det(Q) < 0:
    Q[:, 2] *= -1
T_ac = tf(Q, c)
A2 = adjoint(inv(T_ac))
assert np.allclose(A2.T @ G_com(np.diag(lam), m) @ A2, Ga, atol=1e-13)
# G 对称正定
assert np.allclose(Ga, Ga.T) and np.linalg.eigvalsh(Ga).min() > 0

# ---------------------------------------------------------------- (2) 算例 23.3.1：法兰对负载的力旋量
m_b, r_b, L_b = sh301_blank()
gx, gz, gy = GRIP_BOX
I_g = box_inertia(GRIP_M, gx, gy, gz)
cb = cyl_inertia(m_b, r_b, L_b)
I_bl = np.diag([cb[0, 0], cb[2, 2], cb[0, 0]])                      # 毛坯轴线沿工具方向 y_b
c_g = np.array([0, GRIP_C, 0])
c_bl = np.array([0, 0.15 - 0.04 + L_b / 2, 0])
m_p = GRIP_M + m_b
c_p = (GRIP_M * c_g + m_b * c_bl) / m_p
I_pc = sum(mi * ((d @ d) * np.eye(3) - np.outer(d, d)) + Ii for mi, Ii, d in ((GRIP_M, I_g, c_g - c_p), (m_b, I_bl, c_bl - c_p)))
Gb = G_frame(I_pc, m_p, np.eye(3), c_p)                             # 法兰坐标系 {b} 中负载的空间惯量
dth, ddth = 1.2, 6.0
B1 = adjoint(inv(UR_M)) @ UR_S[0]                                    # 关节 1 的物体旋量轴（零位）
Vb, Vdb = B1 * dth, B1 * ddth
g_b = UR_M[:3, :3].T @ np.array([0, 0, -G0])                         # 重力加速度在 {b} 中的分量
F_grav = np.r_[np.cross(c_p, m_p * g_b), m_p * g_b]                 # 重力对 {b} 原点的力旋量
F_rob = ne_wrench(Gb, Vb, Vdb) - F_grav                             # 式 (23.3.16)：法兰对负载
F_static = -F_grav
F_dyn = F_rob - F_static
# 算法一：质心坐标系 {c}（方向与 {b} 相同）
A = adjoint(tf(np.eye(3), -c_p))
F_c = ne_wrench(G_com(I_pc, m_p), A @ Vb, A @ Vdb) - np.r_[np.zeros(3), m_p * g_b]
assert np.allclose(A.T @ F_c, F_rob, atol=1e-12)
# 算法三：分成小块，沿精确的运动 T_sb(t) = e^{[S1]θ₁(t)} M 用有限差分求加速度
pts, ms = [], []
n1 = 12
for i in range(n1):                                                  # 夹爪：12×12×12 个小方块
    for j in range(n1):
        for k in range(n1):
            pts.append([(i + 0.5) / n1 * gx - gx / 2, GRIP_C + (j + 0.5) / n1 * gy - gy / 2, (k + 0.5) / n1 * gz - gz / 2])
            ms.append(GRIP_M / n1 ** 3)
nr, nph, nz = 10, 24, 40                                            # 毛坯：柱坐标网格
for i in range(nr):
    r0, r1 = i * r_b / nr, (i + 1) * r_b / nr
    rm = math.sqrt((r0 * r0 + r1 * r1) / 2)
    for j in range(nph):
        p = (j + 0.5) * 2 * math.pi / nph
        for k in range(nz):
            pts.append([rm * math.cos(p), c_bl[1] + (k + 0.5) / nz * L_b - L_b / 2, rm * math.sin(p)])
            ms.append(m_b * (r1 * r1 - r0 * r0) / (r_b * r_b) / (nph * nz))
pts, ms = np.array(pts), np.array(ms)
cq = (ms[:, None] * pts).sum(0) / ms.sum()
Iq = sum(mi * ((d @ d) * np.eye(3) - np.outer(d, d)) for mi, d in zip(ms, pts - cq))
Gq = G_frame(Iq, ms.sum(), np.eye(3), cq)                            # 这些小块合起来的空间惯量


def world(t):
    th = dth * t + 0.5 * ddth * t * t
    T = exp6(UR_S[0], th) @ UR_M
    return (T[:3, :3] @ pts.T).T + T[:3, 3], T


h = 1e-4
P0, T0 = world(0.0)
acc_s = (world(h)[0] - 2 * P0 + world(-h)[0]) / h ** 2
f_s = ms[:, None] * (acc_s - np.array([0, 0, -G0]))                 # 法兰对每一小块（连同块间内力）的合力：m(a − g)
F_fd = np.r_[T0[:3, :3].T @ np.cross(P0 - T0[:3, 3], f_s).sum(0), T0[:3, :3].T @ f_s.sum(0)]
g_q = np.r_[np.cross(cq, ms.sum() * g_b), ms.sum() * g_b]
F_q = ne_wrench(Gq, Vb, Vdb) - g_q
err_fd = float(np.abs(F_fd - F_q).max())
assert err_fd < 1e-5                                                  # 有限差分的截断误差 O(h²)
err_disc = float(np.abs(F_q - F_rob).max() / np.abs(F_rob).max())    # 小块划分与连续体的差别
assert err_disc < 5e-3
sensor = -F_rob                                                     # 传感器读到的是负载对法兰的力旋量
# 运动引起的绕 z_b 的力矩分成两部分：水平力（作用在质心）对法兰中心的力矩 (r × f)_z，与使负载自身加速转动的 I_zz ω̇_z。
# ω 沿 z_b，z_b 是 I_pc 的主轴，陀螺项 ω × I ω 为零。
mz_arm = float(np.cross(c_p, F_dyn[3:])[2])
mz_rot = float(F_dyn[2] - mz_arm)
assert abs(mz_rot - I_pc[2, 2] * Vdb[2]) < 1e-12 and np.abs(np.cross(Vb[:3], I_pc @ Vb[:3])).max() < 1e-15
r_axis = math.hypot(*(T0[:3, :3] @ c_p + T0[:3, 3])[:2])            # 负载质心到关节 1 轴的距离

# ---------------------------------------------------------------- (3) 算例 23.3.2：打磨电主轴
m_r, r_r, h_r = 0.6, 0.05, 0.02
I3_r = 0.5 * m_r * r_r ** 2
n_sp = 12000.0
w_sp = n_sp * 2 * math.pi / 60
Om = 1.0
M_gyro = I3_r * w_sp * Om
xml = (f'<mujoco><option timestep="0.0002" integrator="RK4" gravity="0 0 -{G0}"/><worldbody>'
       f'<body name="wrist" pos="0 0 0.5"><joint name="turn" type="hinge" axis="0 0 1"/><site name="s"/>'
       f'<geom type="box" size="0.03 0.03 0.03" mass="0.5" contype="0" conaffinity="0"/>'
       f'<body name="rotor"><joint name="spin" type="hinge" axis="0 1 0"/>'
       f'<geom type="cylinder" size="{r_r} {h_r / 2}" quat="0.7071067811865476 0.7071067811865476 0 0" mass="{m_r}" contype="0" conaffinity="0"/>'
       f'</body></body></worldbody><sensor><torque site="s"/></sensor></mujoco>')
mj, mm, dd = mj_load(xml)
assert abs(mm.body_inertia[2][2] - I3_r) < 1e-15
dd.qvel[0], dd.qvel[1] = Om, w_sp
tq = []
for _ in range(5000):
    mj.mj_step(mm, dd)
    tq.append(dd.sensordata[:3].copy())
tq = np.array(tq)
M_gyro_mj = float(np.linalg.norm(tq, axis=1).mean())
assert abs(M_gyro_mj / M_gyro - 1) < 1e-9 and np.ptp(np.linalg.norm(tq, axis=1)) < 1e-9
assert abs(tq[-1][2]) < 1e-9 and abs(tq[-1][1]) < 1e-9               # 力矩垂直于两根轴（在手腕坐标系中沿 x）
# 实验 23.3 任务 2：砂轮反转，力矩沿支架 x 轴的分量变号
mj, mm, dd = mj_load(xml)
dd.qvel[0], dd.qvel[1] = Om, -w_sp
for _ in range(1000):
    mj.mj_step(mm, dd)
assert tq[-1][0] < 0 < dd.sensordata[0] and abs(np.linalg.norm(dd.sensordata[:3]) / M_gyro - 1) < 1e-9
M_wrist = 28.0                                                      # Menagerie 模型中手腕关节的力矩上限（forcerange）

# ---------------------------------------------------------------- (4) 算例 23.3.3：自行车轮陀螺
m_w, r_w, t_w, l_w = 1.0, 0.15, 0.02, 0.20
I3_w = 0.5 * m_w * r_w ** 2


def wheel(spin, T=4.0, dt=0.0005):
    Om0 = m_w * G0 * l_w / (I3_w * spin) if spin > 0 else 0.0
    xml = (f'<mujoco><option timestep="{dt}" integrator="RK4" gravity="0 0 -{G0}"/><worldbody>'
           f'<body name="axle" pos="0 0 1"><joint type="ball"/>'
           f'<geom type="capsule" fromto="0 0 0 {l_w} 0 0" size="0.006" mass="1e-6" contype="0" conaffinity="0"/>'
           f'<body name="wheel" pos="{l_w} 0 0"><joint type="hinge" axis="1 0 0"/>'
           f'<geom type="cylinder" size="{r_w} {t_w / 2}" quat="0.7071067811865476 0 0.7071067811865476 0" mass="{m_w}" contype="0" conaffinity="0"/>'
           f'</body></body></worldbody></mujoco>')
    mj, mm, dd = mj_load(xml)
    dd.qvel[2], dd.qvel[3] = Om0, spin                                # 球铰的角速度在轴的坐标系中；开始时轴沿 x、水平
    tt, az, el = [], [], []
    for _ in range(int(T / dt)):
        mj.mj_step(mm, dd)
        ax_ = dd.xmat[1].reshape(3, 3)[:, 0]
        tt.append(dd.time)
        az.append(math.atan2(ax_[1], ax_[0]))
        el.append(math.degrees(math.asin(max(-1.0, min(1.0, ax_[2])))))
    az = np.unwrap(np.array(az))
    return Om0, float(np.polyfit(tt, az, 1)[0]), float(min(el)), np.array(tt), np.array(el)


Om60, rate60, drop60, _, _ = wheel(60.0)
Om30, rate30, drop30, _, _ = wheel(30.0)
assert abs(rate60 / Om60 - 1) < 1e-4 and abs(rate30 / Om30 - 1) < 1e-4 and drop60 > -0.01
_, _, _, t0, el0 = wheel(0.0, T=1.0)
t_fall = float(t0[np.argmax(el0 < -60)])                             # 不转时轴落到水平线下 60° 的时刻
assert t_fall < 1.0

# ---------------------------------------------------------------- (5) 习题答案
F_rob0 = ne_wrench(Gb, Vb, np.zeros(6)) - F_grav                    # 23.3.6：θ̈₁ = 0
F_dyn0 = F_rob0 - F_static                                          # 只剩向心力与它对法兰中心的力矩（陀螺项为零）
assert abs(np.linalg.norm(F_dyn0[3:]) - m_p * dth ** 2 * r_axis) < 1e-12 and abs(F_dyn0[2] - np.cross(c_p, F_dyn0[3:])[2]) < 1e-12
w_ex5 = 0.5 * G0 * 0.05 / (0.5 * 0.5 * 0.04 ** 2 * (math.pi / 2))   # 23.3.5：1.0 s 进动 90°

out(err_ne=err_ne, N=N,
    m_p=m_p, c_p=c_p[1], dth=dth, ddth=ddth, B1=tex(B1, 3), Vb=tex(Vb, 4), Vdb=tex(Vdb, 3), g_b=tex(g_b, 2),
    F_rob=tex(F_rob, 3), F_static=tex(F_static, 3), F_dyn=tex(F_dyn, 3), sensor=tex(sensor, 3), err_fd=err_fd, err_disc=err_disc,
    n_parts=len(ms), r_axis=r_axis, f_cent=m_p * dth ** 2 * r_axis, f_tan=m_p * ddth * r_axis, F_rob0=tex(F_rob0, 3),
    I3_r=I3_r, w_sp=w_sp, M_gyro=M_gyro, M_gyro_mj=M_gyro_mj, L_sp=I3_r * w_sp, gyro_pct=M_gyro / M_wrist * 100,
    w_ex5=w_ex5, mz_dyn=F_dyn[2], mz_arm=mz_arm, mz_rot=mz_rot, Izz_p=I_pc[2, 2], mz0=F_dyn0[2], I3_w=I3_w, Om60=Om60, rate60=rate60, Om30=Om30, rate30=rate30, drop60=drop60, drop60_abs=abs(drop60), t_fall=t_fall, ratio60=60 / Om60)
