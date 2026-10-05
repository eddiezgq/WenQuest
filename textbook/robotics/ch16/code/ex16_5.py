"""16.5 节：静力学 τ = Jᵀ F。

(1) 定理 16.5.1 的核对：UR5e 在 θ* 处，任取一个力旋量，三种写法 J_sᵀ F_s、J_bᵀ F_b、J_gᵀ F_g 给出同一组关节力矩；
    再用零件库模型（与指数积无关）按虚功原理 τ_i = f · ∂p/∂θ_i 的差商核对一个作用在法兰盘中心的纯力。
(2) 算例 16.5.1：θ* 处法兰盘向下压 50 N：各关节力矩及其与力矩上限（150、150、150、28、28、28 N·m）之比；
    只看关节力矩上限，竖直向下最多能压多大的力，哪个关节先到上限；力椭球的半轴 1/σ_i 与方向（与速度椭球相同）；
    竖直、径向的力传递比与速度传递比之积 ≤ 1，沿主轴等于 1（定理 16.5.2）。
(3) 算例 16.5.2：Panda（七轴）在 ready 姿态，手上受外力；七个关节力矩传感器的读数含噪声，
    用最小二乘 F̂ = (Jᵀ)⁺ τ 估计外力：误差的上界 ‖δτ‖/σ_min 与蒙特卡罗结果；七维中多出的一维（Jᵀ 值域的正交补）
    上的残差：力作用在手上时只有噪声，力作用在第 4 个连杆上（碰撞）时残差远大于噪声，可以用来检测碰撞。
(4) 算例 16.5.3：关节柔度引起的末端变形：C = J K⁻¹ Jᵀ；θ* 处向下压 50 N 时法兰盘中心的位移与转角，
    与把 δθ = K⁻¹ Jᵀ F 代回零件库模型的结果核对。
"""
import math

import numpy as np

from _jac import (PANDA_READY, TAU_MAX, TH_STAR, adjoint, ellipsoid, force_ratio, inv, jacobian_body, jacobian_space,
                  body_screws, panda_screws, skew, svals, trans_ratio, ur_fk, ur_jb, ur_jg, ur_js, ur_jv, ur_model,
                  ur_radial_point)
from bookout import T, out, vec

rng = np.random.default_rng(165)
deg = np.degrees

# ---------------------------------------------------------------- (1) 三种写法一致；虚功原理核对
Tq = ur_fk(TH_STAR)
R, p = Tq[:3, :3], Tq[:3, 3]
Js, Jb, Jg = ur_js(TH_STAR), ur_jb(TH_STAR), ur_jg(TH_STAR)
e_pair = 0.0
for _ in range(200):
    Fs = rng.normal(size=6) * np.r_[np.full(3, 5.0), np.full(3, 50.0)]
    Fb = adjoint(Tq).T @ Fs                                       # 式 (6.6.4)：F_b = [Ad_T]ᵀ F_s
    m_p = Fs[:3] - np.cross(p, Fs[3:])                            # 对法兰盘中心的力矩
    Fg = np.r_[m_p, Fs[3:]]
    t1, t2, t3 = Js.T @ Fs, Jb.T @ Fb, Jg.T @ Fg
    e_pair = max(e_pair, float(np.abs(t1 - t2).max()), float(np.abs(t1 - t3).max()))
assert e_pair < 1e-11
# 虚功原理：作用在法兰盘中心的恒力 f，τ_i = f · ∂p/∂θ_i（零件库模型的差商）
mdl = ur_model()
f = np.array([0.0, 0.0, -50.0])
h = 1e-6
tau_vw = np.zeros(6)
for i in range(6):
    d = np.zeros(6)
    d[i] = h
    tau_vw[i] = f @ (mdl.fk(TH_STAR + d)[:3, 3] - mdl.fk(TH_STAR - d)[:3, 3]) / (2 * h)
Jv = ur_jv(TH_STAR)
tau = Jv.T @ f
e_vw = float(np.abs(tau - tau_vw).max())
assert e_vw < 1e-7

# ---------------------------------------------------------------- (2) 算例 16.5.1
ratio = np.abs(tau) / TAU_MAX
per_N = Jv.T @ np.array([0, 0, -1.0])                             # 每牛顿向下的力所需的关节力矩
lim = TAU_MAX / np.maximum(np.abs(per_N), 1e-12)
F_down = float(lim.min())
j_down = int(np.argmin(lim)) + 1
assert j_down == 2
sv, U = ellipsoid(Jv)
for k in range(3):
    U[:, k] *= np.sign(U[np.argmax(np.abs(U[:, k])), k])
fax = 1 / sv                                                      # 力椭球的半轴（N 每 N·m），从小到大
er = ur_radial_point(1.0) - ur_radial_point(0.0)
er /= np.linalg.norm(er)
ez = np.array([0, 0, 1.0])
b_z, b_r = force_ratio(Jv, ez), force_ratio(Jv, er)
a_z, a_r = trans_ratio(Jv, ez), trans_ratio(Jv, er)
assert a_z * b_z < 1 and a_r * b_r < 1
for k in range(3):                                                 # 沿主轴：α β = 1
    assert abs(trans_ratio(Jv, U[:, k]) * force_ratio(Jv, U[:, k]) - 1) < 1e-12
worst_ab = 0.0
for _ in range(5000):                                              # 定理 16.5.2：α(u) β(u) ≤ 1
    u = rng.normal(size=3)
    worst_ab = max(worst_ab, trans_ratio(Jv, u) * force_ratio(Jv, u))
assert worst_ab <= 1 + 1e-12
# 按关节力矩上限（长方体）沿径向、竖直方向能平衡的最大力
def fmax(u):
    return float((TAU_MAX / np.maximum(np.abs(Jv.T @ u), 1e-12)).min())


F_rad, F_up = fmax(er), fmax(ez)

# ---------------------------------------------------------------- (3) 算例 16.5.2：Panda 估计外力
S, M, W, Q, pa = panda_screws()
B = body_screws(S, M)
q = PANDA_READY
Jp = jacobian_body(B, q)                                           # 6×7
sp = svals(Jp)
F_true = np.array([0, 0, 0, 10.0, 0, -5.0])                        # 手上：沿 x_b 10 N、沿 z_b −5 N 的纯力（作用在 {b} 原点）
tau_p = Jp.T @ F_true
sig = 0.05                                                         # 每个关节力矩传感器的噪声标准差（示意值），N·m
P = np.linalg.pinv(Jp.T)                                           # (Jᵀ)⁺ = (J Jᵀ)⁻¹ J
assert np.allclose(P, np.linalg.solve(Jp @ Jp.T, Jp), atol=1e-12)
assert np.allclose(P @ tau_p, F_true, atol=1e-12)
ef, em, worst_ratio = [], [], 0.0
N_MC = 20000
for _ in range(N_MC):
    d = rng.normal(0, sig, 7)
    E = P @ d
    ef.append(np.linalg.norm(E[3:]))
    em.append(np.linalg.norm(E[:3]))
    worst_ratio = max(worst_ratio, np.linalg.norm(E) * sp[-1] / np.linalg.norm(d))
assert worst_ratio <= 1 + 1e-12                                   # ‖δF‖ ≤ ‖δτ‖ / σ_min
rms_f, rms_m = float(np.sqrt(np.mean(np.square(ef)))), float(np.sqrt(np.mean(np.square(em))))
# 理论值：协方差 σ² (J Jᵀ)⁻¹，各分块的迹
Cov = sig ** 2 * np.linalg.inv(Jp @ Jp.T)
th_f, th_m = math.sqrt(np.trace(Cov[3:, 3:])), math.sqrt(np.trace(Cov[:3, :3]))
assert abs(rms_f / th_f - 1) < 0.03 and abs(rms_m / th_m - 1) < 0.03
# 多出的一维：Jᵀ 值域的正交补，即 J 的零空间（自运动方向）n；残差 r = nᵀ τ
nvec = np.linalg.svd(Jp)[2][-1]
assert np.abs(Jp @ nvec).max() < 1e-12
res_hand = float(abs(nvec @ tau_p))
# 碰撞：力作用在第 4 个连杆上（关节 4 的轴上一点再向外 0.1 m），只有关节 1～4 受力
E4 = np.eye(4)
for Si, ti in zip(S[:4], q[:4]):
    from _jac import exp6
    E4 = E4 @ exp6(Si, ti)
c0 = Q[3] + 0.0                                                    # 零位时关节 4 的轴上一点
c = E4[:3, :3] @ c0 + E4[:3, 3]
fc = np.array([0, 15.0, 0])                                        # 有人从侧面推了一下肘部：沿 y_s 15 N
Fc_s = np.r_[np.cross(c, fc), fc]
Jsp = jacobian_space(S, q)
tau_c = np.r_[Jsp[:, :4].T @ Fc_s, np.zeros(3)]                    # 关节 5～7 不受力
nvec = nvec * np.sign(nvec @ tau_c)                                # 正负号任取，取碰撞时残差为正
res_coll = float(nvec @ tau_c)
F_wrong = P @ tau_c                                                # 误当作手上的外力时的“估计”
res_noise = sig                                                    # 残差中噪声的标准差 = σ（n 是单位矢量）
assert res_hand < 1e-12 and res_coll > 20 * res_noise

# ---------------------------------------------------------------- (4) 算例 16.5.3：关节柔度
K = np.diag([2.0e4, 2.0e4, 2.0e4, 5.0e3, 5.0e3, 5.0e3])           # 关节刚度（示意值），N·m/rad
Fg = np.r_[0, 0, 0, f]
C = Jg @ np.linalg.inv(K) @ Jg.T                                   # 柔度矩阵（式 (16.5.9)）
dx = C @ Fg
dth = np.linalg.solve(K, Jg.T @ Fg)
T2 = mdl.fk(TH_STAR + dth)
T1 = mdl.fk(TH_STAR)
dp_model = T2[:3, 3] - T1[:3, 3]
from _jac import logR
dw_model = logR(T2[:3, :3] @ T1[:3, :3].T)
e_lin = float(max(np.abs(dp_model - dx[3:]).max(), np.abs(dw_model - dx[:3]).max()))
assert e_lin < 1e-3 * np.abs(dx).max()                              # 二阶小量
Cv = C[3:, 3:]
kv_s = svals(Cv)

# 平面 2R 臂（图 16.5.1）：速度椭圆与力椭圆
from _jac import jac_2r
s90 = svals(jac_2r(np.radians([30, 90])))
s30 = svals(jac_2r(np.radians([30, 30])))
out(s90=", ".join(f"{x:.4f}" for x in s90), f90=", ".join(f"{1 / x:.3f}" for x in s90[::-1]),
    s30=", ".join(f"{x:.4f}" for x in s30), f30=", ".join(f"{1 / x:.3f}" for x in s30[::-1]), f30a=1 / s30[1])
out(e_pair=e_pair, e_vw=e_vw, tau=vec(tau, 2), ratio=", ".join(f"{x:.3f}" for x in ratio), F_down=F_down, j_down=j_down,
    fax=", ".join(f"{x:.3f}" for x in fax), u1=vec(U[:, 0], 4), u3=vec(U[:, 2], 4), b_z=b_z, b_r=b_r, a_z=a_z, a_r=a_r,
    ab_z=a_z * b_z, ab_r=a_r * b_r, worst_ab=worst_ab, F_rad=F_rad, F_up=F_up,
    sp=", ".join(f"{x:.4f}" for x in sp), tau_p=vec(tau_p, 3), rms_f=rms_f, rms_m=rms_m, th_f=th_f, th_m=th_m,
    bound=sig * math.sqrt(7) / sp[-1], worst_ratio=worst_ratio, nvec=vec(nvec, 3), res_coll=res_coll, F_wrong=vec(F_wrong, 2),
    c=vec(c, 3), dx_p=vec(dx[3:] * 1000, 3), dx_w=vec(deg(dx[:3]), 4), dpn=float(np.linalg.norm(dx[3:]) * 1000),
    dth=vec(deg(dth), 4), e_lin=e_lin, kc=", ".join(f"{x * 1e6:.2f}" for x in kv_s), ncv=float(abs(dx[5]) * 1000))
