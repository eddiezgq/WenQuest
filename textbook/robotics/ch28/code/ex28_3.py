"""28.3 节的计算：四旋翼动力学。X2 的数据取自网页版 x2.xml（MuJoCo Menagerie skydio_x2）。

(1) 算例 28.3.1：动量理论。旋翼半径取模型中旋翼碰撞椭球的半径 0.13 m；悬停时每个旋翼的诱导速度、理想功率；
    取悬停效率（品质因数）0.6（示意值），由模型的反扭矩系数 c = Q/T 估计悬停转速与推力系数 k_f。
(2) 算例 28.3.2：X2 对质心的惯量张量（机体坐标轴），主轴方向；悬停时（总推力 m𝔤）绕三个轴的最大力矩与角加速度，
    惯量积引起的耦合。
(3) 算例 28.3.3：“8”字形轨迹（算例 21.4.1）上 t = 1.3 s 处：由 ω_b、ω̇_b 按欧拉方程求力矩，陀螺项的大小，四个旋翼的推力；
    在 MuJoCo 中（关掉空气阻力）把这一状态和推力放进去，加速度与平坦映射给出的一致。整个周期内推力的范围。
(4) 算例 28.3.4：MuJoCo 的空气阻力（与惯量相同的等效长方体）。10 m/s、5 m/s 平飞的配平：俯仰角与总推力；
    逆风 5 m/s 悬停；倾角限 30° 时的最高平飞速度；在 MuJoCo 中核对配平状态的加速度为零。
"""
import math

import mujoco
import numpy as np

from _ch28 import G, RHO_AIR, R2quat, fig8, flat, mj_load, mjcf_text, roty, x2_alloc, x2_params, x2_state
from bookout import out

P = x2_params()
m, J = P["m"], P["J"]
A, A6 = x2_alloc(P)
W = m * G
out(m=m, W=W, com_z_mm=P["com"][2] * 1000, c=P["c"], fmax=P["fmax"], R_rot=P["R_rot"], hover=P["hover"],
    lx=abs(P["r"][0][0]), ly=abs(P["r"][0][1]))

# ---------------------------------------------------------------- (1) 动量理论
A_disk = math.pi * P["R_rot"] ** 2
T_h = W / 4
v_i = math.sqrt(T_h / (2 * RHO_AIR * A_disk))
P_id = T_h * v_i
FM = 0.6
P_act = P_id / FM
Omega = v_i / (FM * P["c"])                      # c = Q/T，QΩ = Tv_i/FM
k_f = T_h / Omega ** 2
k_m = P["c"] * k_f
v_i_max = math.sqrt(P["fmax"] / (2 * RHO_AIR * A_disk))
out(A_disk=A_disk, T_h=T_h, v_i=v_i, P_id=P_id, P_id4=4 * P_id, FM=FM, P_act4=4 * P_act, Omega=Omega, rpm=Omega * 60 / (2 * math.pi),
    k_f=k_f, k_m=k_m, disk_load=T_h / A_disk, v_i_max=v_i_max)
# 功率与推力的 3/2 次方成正比：总质量增加 20% 时悬停功率增加的比例
out(p_up20=(1.2 ** 1.5 - 1) * 100)

# ---------------------------------------------------------------- (2) 惯量与最大角加速度
Jxx, Jyy, Jzz, Jxz = J[0, 0], J[1, 1], J[2, 2], J[0, 2]
ang_p = 0.5 * math.degrees(math.atan2(2 * Jxz, Jzz - Jxx))       # 主轴在 x-z 平面内转过的角
out(Jxx=Jxx, Jyy=Jyy, Jzz=Jzz, Jxz=Jxz, ang_p=abs(ang_p), I1=P["principal"][0], I2=P["principal"][1], I3=P["principal"][2])
ly, lx = abs(P["r"][0][1]), abs(P["r"][0][0])
tx = 2 * (W / 2) * ly                            # 一侧两个旋翼各 m𝔤/2，另一侧为零
ty = 2 * (W / 2) * lx
tz = 2 * (W / 2) * P["c"]
# 用分配矩阵核对：f = m𝔤 时三个方向的力矩上限
for tau, k in ((np.array([W, tx, 0, 0]), 1), (np.array([W, 0, ty, 0]), 2), (np.array([W, 0, 0, tz]), 3)):
    fi = np.linalg.solve(A, tau)
    assert fi.min() > -1e-9 and fi.max() < W / 2 + 1e-9
ax = np.linalg.solve(J, [tx, 0, 0])
ay = np.linalg.solve(J, [0, ty, 0])
az = np.linalg.solve(J, [0, 0, tz])
out(tx=tx, ty=ty, tz=tz, ax=ax[0], ay=ay[1], az=az[2], ax_z=ax[2], ax_z_ratio=abs(ax[2] / ax[0]) * 100)
# 横滚 90° 所需的最短时间（先最大加速、再最大减速，bang-bang）
t90 = 2 * math.sqrt((math.pi / 2) / ax[0])
out(t90_ms=t90 * 1000)

# ---------------------------------------------------------------- (3) 平坦轨迹上的力矩与推力
t1, kpsi = 1.3, 0.3
F1 = flat(fig8(t1), kpsi * t1, kpsi, 0.0, m)
w1, dw1 = F1["w"], F1["dw"]
gyro1 = np.cross(w1, J @ w1)
tau1 = J @ dw1 + gyro1
f1 = np.linalg.solve(A, np.r_[F1["f"], tau1])
out(t1=t1, w1x=w1[0], w1y=w1[1], w1z=w1[2], dw1x=dw1[0], dw1y=dw1[1], dw1z=dw1[2], tau1x=tau1[0], tau1y=tau1[1], tau1z=tau1[2],
    gyro1=np.linalg.norm(gyro1), gyro1_rel=np.linalg.norm(gyro1) / np.linalg.norm(tau1) * 100,
    f1_1=f1[0], f1_2=f1[1], f1_3=f1[2], f1_4=f1[3], ftot1=F1["f"])
# MuJoCo 核对（关掉空气阻力）
mm, d = mj_load(mjcf_text("x2"))
mm.opt.density, mm.opt.viscosity = 0.0, 0.0
pc, vc, ac = fig8(t1)[0:3]
d.qpos[:], d.qvel[:] = x2_state(P, pc, vc, F1["R"], w1)
d.ctrl[:] = f1
mujoco.mj_forward(mm, d)
acc_c = d.qacc[:3] + F1["R"] @ (np.cross(d.qacc[3:6], P["com"]) + np.cross(w1, np.cross(w1, P["com"])))
err_dw = float(np.abs(d.qacc[3:6] - dw1).max())
err_a = float(np.abs(acc_c - ac).max())
assert err_dw < 1e-10 and err_a < 1e-10
out(err_dw=err_dw, err_a=err_a)
# 整个周期
ts = np.linspace(0, 2 * math.pi / 0.8, 2001)
fis, taus, gys = [], [], []
for t in ts:
    Ft = flat(fig8(t), kpsi * t, kpsi, 0.0, m)
    g_ = np.cross(Ft["w"], J @ Ft["w"])
    ta = J @ Ft["dw"] + g_
    fis.append(np.linalg.solve(A, np.r_[Ft["f"], ta]))
    taus.append(ta)
    gys.append(g_)
fis, taus, gys = np.array(fis), np.array(taus), np.array(gys)
out(f8_lo=fis.min(), f8_hi=fis.max(), tau8=np.linalg.norm(taus, axis=1).max(), gy8=np.linalg.norm(gys, axis=1).max(),
    f8_spread=(fis.max(axis=1) - fis.min(axis=1)).max())

# ---------------------------------------------------------------- (4) 空气阻力与配平
mm.opt.density, mm.opt.viscosity = RHO_AIR, 1.8e-5
Ix, Iy, Iz = P["principal"]
box = np.sqrt(np.array([Iy + Iz - Ix, Ix + Iz - Iy, Ix + Iy - Iz]) * 6 / m)   # 等效长方体（主轴坐标系）的边长
out(box1=box[0], box2=box[1], box3=box[2])


def mj_drag(v_air, R):
    """MuJoCo 中相对空气以 v_air（{s} 中）运动、姿态为 R 时空气对 X2 的力（{s} 中，作用在质心）。"""
    d.qpos[:] = np.r_[0, 0, 5, R2quat(R)]
    d.qvel[:] = np.r_[v_air, 0, 0, 0]
    d.ctrl[:] = 0
    mujoco.mj_forward(mm, d)
    return d.qfrc_passive[:3].copy()


def box_drag(v_air):
    """MuJoCo 的“惯量”空气模型（与 x2.xml 相同的 <option density viscosity>）：把机体换成质量、惯量都相同的长方体，
    在主轴坐标系中每个方向的阻力为 −½ρ(另两边之积)|v_i|v_i，再加黏性阻力 −3πμ(三边平均)v。v_air 为机体坐标系中的分量。"""
    v = P["Rp"].T @ v_air
    quad = -0.5 * RHO_AIR * np.array([box[1] * box[2], box[0] * box[2], box[0] * box[1]]) * np.abs(v) * v
    visc = -3 * math.pi * 1.8e-5 * box.mean() * v
    return P["Rp"] @ (quad + visc)


D10 = -mj_drag(np.array([10.0, 0, 0]), np.eye(3))[0]
Fb = box_drag(np.array([10.0, 0, 0]))
assert abs(-Fb[0] - D10) < 1e-9
out(D10=D10, A_eq=D10 / (0.5 * RHO_AIR * 100))


def trim(v):
    """水平匀速飞行（{s} 中沿 +x，速度 v）的配平：机身绕 y 轴转 θ（低头为正），推力 f 沿 z_b。不动点迭代。"""
    th = 0.0
    for _ in range(100):
        Fd = mj_drag(np.array([v, 0, 0]), roty(th))
        th_new = math.atan2(-Fd[0], W - Fd[2])
        if abs(th_new - th) < 1e-14:
            break
        th = th_new
    Fd = mj_drag(np.array([v, 0, 0]), roty(th))
    f = math.hypot(-Fd[0], W - Fd[2])
    return th, f, Fd


th10, f10, Fd10 = trim(10.0)
th5, f5, _ = trim(5.0)
# MuJoCo 核对：配平状态下加速度为零（四个旋翼推力相同，阻力过质心，不产生力矩）
d.qpos[:] = np.r_[0, 0, 5, R2quat(roty(th10))]
d.qvel[:] = np.r_[10.0, 0, 0, 0, 0, 0]
d.ctrl[:] = f10 / 4
mujoco.mj_forward(mm, d)
acc_o = d.qacc[:3]
err_trim = float(np.abs(acc_o).max() + np.abs(d.qacc[3:6]).max())
assert err_trim < 1e-9
# 逆风悬停：风速 5 m/s 从机头吹来（wind = (−5, 0, 0)），机身相对空气的速度为 +5 m/s，与平飞 5 m/s 相同
mm.opt.wind[:] = [-5.0, 0, 0]
d.qpos[:] = np.r_[0, 0, 5, R2quat(roty(th5))]
d.qvel[:] = 0
d.ctrl[:] = f5 / 4
mujoco.mj_forward(mm, d)
err_wind = float(np.abs(d.qacc).max())
assert err_wind < 1e-9
mm.opt.wind[:] = 0
# 倾角限 30° 时的最高平飞速度
lo, hi = 1.0, 60.0
for _ in range(60):
    mid = (lo + hi) / 2
    if trim(mid)[0] < math.radians(30):
        lo = mid
    else:
        hi = mid
v30 = lo
out(th10=math.degrees(th10), f10=f10, th5=math.degrees(th5), f5=f5, err_trim=err_trim, v30=v30, v30_kmh=v30 * 3.6,
    lift10=Fd10[2])
# 不计阻力时 10 m/s 平飞：机身是平的（21.2 节）

# ---------------------------------------------------------------- (5) 旋翼的陀螺力矩（转动惯量为示意值）
J_ROT = 5e-5                                       # 一个旋翼（桨叶连同电机转子）的转动惯量，kg·m²（示意值）
Om_h = math.sqrt(T_h / k_f)                        # 悬停转速（= Omega）
# 偏航力矩最大时：一对旋翼各 m𝔤/2，另一对为零
Om_y = math.sqrt(W / 2 / k_f)
sum_sig_Om = 2 * Om_y
gyro_rot = J_ROT * sum_sig_Om * 2.0                # 横滚角速度 2 rad/s 时
out(J_rot=J_ROT, Om_y=Om_y, gyro_rot=gyro_rot, gyro_rot_rel=gyro_rot / tx * 100, h_rot=J_ROT * Om_h)

# ---------------------------------------------------------------- 习题
# 28.3.1 载 0.3 kg 的相机：悬停诱导速度与理想功率
W2 = (m + 0.3) * G
out(m_cam=0.3, P_id_cam=4 * (W2 / 4) * math.sqrt(W2 / 4 / (2 * RHO_AIR * A_disk)), rpm_cam=math.sqrt(W2 / 4 / k_f) * 60 / (2 * math.pi))
# 28.3.3 只绕 y_b 的最大角加速度（f = m𝔤）时，俯仰 30° 的最短时间
out(t30_ms=2 * math.sqrt(math.radians(30) / ay[1]) * 1000)
# 28.3.4 逆风 8 m/s 悬停的倾角
mm.opt.wind[:] = 0
out(th8=math.degrees(trim(8.0)[0]))
