"""23.4 节的计算：动量与能量；自由刚体转动的稳定性（网球拍定理）。

(1) 定理 23.4.1、23.4.2 的数值核对：任取一个刚体的运动 T(t) = exp([A]t + [B]t²)（固定种子），用有限差分求 V_b、V̇_b；
    空间动量 P_s = [Ad_{T_bs}]ᵀ G_b V_b 对时间的导数等于力旋量 F_s；动能对时间的导数等于功率 F_bᵀV_b；
    动能在任意两个物体坐标系中相同，并满足柯尼希定理 (23.4.5)。
(2) 算例 23.4.1：花样滑冰运动员收臂（示意值），角动量守恒：转速与动能的变化（兑现 10.3 节的说法）。
(3) 算例 23.4.2：空间站机械臂松开的工具箱 0.40 × 0.24 × 0.10 m、6 kg（示意值），以 ω₀ = 8 rad/s 主要绕某根主轴转动，
    另两轴各有 1% 的扰动。本章自己的 RK4 积分欧拉方程，与 MuJoCo（自由刚体，RK4，步长 1 ms）逐步比较；
    绕最大、最小惯量轴 10 s 内角速度不低于 ω₀ 的 99.99%；绕中间轴：增长率 λ（式 (23.4.13)）、第一次翻转的时刻、
    相邻两次翻转的间隔，并与雅可比椭圆函数精确解的半周期 2K(k)/ν 核对；能量与 |L| 守恒。
(4) 实验 23.4 的阈值：扰动 ε = 0.1% 时第一次翻转的时刻（RK4 与 MuJoCo 一致，< 10 s），比 ε = 1% 推迟约 ln 10/λ；
    手机（0.16 × 0.075 × 0.008 m、0.2 kg，示意值）以 12 rad/s 绕中间轴转动的增长率。
(5) 习题答案。
"""
import math

import numpy as np
from scipy.special import ellipk

from _ch23 import G_frame, ad, adjoint, box_inertia, exp_twist, free_spin, inv, mj_load, ne_wrench, sign_changes, skew
from bookout import out

rng = np.random.default_rng(234)

# ---------------------------------------------------------------- (1) 定理的数值核对
m = 2.5
Ic = np.diag([0.02, 0.05, 0.06])
Rq, _ = np.linalg.qr(rng.normal(size=(3, 3)))
if np.linalg.det(Rq) < 0:
    Rq[:, 0] *= -1
r = np.array([0.1, -0.05, 0.2])
Gb = G_frame(Ic, m, Rq, r)                                           # 物体坐标系 {b} 不在质心
A_, B_ = rng.normal(size=6), rng.normal(size=6) * 0.5


def T_of(t):
    return exp_twist(A_ * t + B_ * t * t)


def vee(X):
    return np.array([X[2, 1], X[0, 2], X[1, 0], X[0, 3], X[1, 3], X[2, 3]])


def Vb_of(t, h=1e-5):
    T = T_of(t)
    return vee(inv(T) @ (T_of(t + h) - T_of(t - h)) / (2 * h))


t0, h = 0.7, 1e-4
V = Vb_of(t0)
Vd = (Vb_of(t0 + h) - Vb_of(t0 - h)) / (2 * h)
Fb = ne_wrench(Gb, V, Vd)
Fs = adjoint(inv(T_of(t0))).T @ Fb                                   # 式 (6.6.4)：F_s = [Ad_{T_bs}]ᵀ F_b


def Ps(t):
    return adjoint(inv(T_of(t))).T @ Gb @ Vb_of(t)


dPs = (Ps(t0 + h) - Ps(t0 - h)) / (2 * h)
err_P = float(np.abs(dPs - Fs).max() / np.abs(Fs).max())
assert err_P < 1e-5


def K(t):
    v = Vb_of(t)
    return 0.5 * v @ Gb @ v


dK = (K(t0 + h) - K(t0 - h)) / (2 * h)
err_K = abs(dK - Fb @ V) / abs(Fb @ V)
assert err_K < 1e-5
assert abs(V @ ad(V).T @ Gb @ V) < 1e-12                             # 证明中的关键一步：[ad_V]V = 0
# 动能与坐标系无关，并满足柯尼希定理：质心坐标系中 ½ m|v_c|² + ½ ωᵀ I_c ω
T_cb = inv(np.vstack([np.c_[Rq, r], [0, 0, 0, 1]]))                   # {b} 相对质心坐标系 {c} 的位姿
Vc = adjoint(T_cb) @ V
K_c = 0.5 * m * Vc[3:] @ Vc[3:] + 0.5 * Vc[:3] @ Ic @ Vc[:3]
assert abs(K_c - K(t0)) < 1e-10

# ---------------------------------------------------------------- (2) 算例 23.4.1：花样滑冰（示意值）
m_body, r_body = 48.0, 0.13                                          # 躯干、头、腿合成一个竖直圆柱
m_arm, l_arm, d_sh = 3.5, 0.65, 0.20                                 # 每条手臂（连手）、臂长、肩到转轴的距离
I_body = 0.5 * m_body * r_body ** 2
I_out = I_body + 2 * m_arm * (l_arm ** 2 / 12 + (d_sh + l_arm / 2) ** 2)     # 两臂水平伸直（平行轴定理）
I_in = I_body + 2 * m_arm * d_sh ** 2                               # 两臂收拢贴在身体两侧（细杆绕自身的竖直轴不计）
n_out = 1.5                                                         # 伸臂时 1.5 r/s
n_in = n_out * I_out / I_in
I_half = I_body + 2 * m_arm * 0.30 ** 2                              # 习题 23.4.3：手臂收到一半（看作质点）
n_half = n_out * I_out / I_half
K_out = 0.5 * I_out * (2 * math.pi * n_out) ** 2
K_in = 0.5 * I_in * (2 * math.pi * n_in) ** 2

# ---------------------------------------------------------------- (3) 算例 23.4.2：工具箱
a, b, c, M = 0.40, 0.24, 0.10, 6.0
I = np.diag(box_inertia(M, a, b, c))
I1, I2, I3 = I
w0, eps = 8.0, 0.01
lam = w0 * math.sqrt((I3 - I2) * (I2 - I1) / (I1 * I3))
nu1 = w0 * math.sqrt((I2 - I1) * (I3 - I1) / (I2 * I3))
nu3 = w0 * math.sqrt((I3 - I1) * (I3 - I2) / (I1 * I2))


def mj_box(w, a=a, b=b, c=c, M=M, T=12.0):
    xml = (f'<mujoco><option timestep="0.001" integrator="RK4" gravity="0 0 0"/><worldbody>'
           f'<body pos="0 0 0.8"><freejoint/><geom type="box" size="{a / 2} {b / 2} {c / 2}" mass="{M}"/></body></worldbody></mujoco>')
    mj, mm, dd = mj_load(xml)
    dd.qvel[3:6] = w                                                 # 自由刚体：角速度在物体坐标系中的分量
    W = np.zeros((int(round(T / 0.001)) + 1, 3))
    W[0] = w
    for k in range(1, len(W)):
        mj.mj_step(mm, dd)
        W[k] = dd.qvel[3:6]
    return np.arange(len(W)) * 0.001, W, mm.body_inertia[1].copy()


res = {}
for k in range(3):
    w = np.full(3, eps * w0)
    w[k] = w0
    t, Wm, Imj = mj_box(w)
    assert np.allclose(Imj, I, rtol=1e-12)
    _, Wr = free_spin(I, w, 12.0)
    diff = float(np.abs(Wm - Wr).max())
    assert diff < 1e-7
    kin = 0.5 * (I * Wm ** 2).sum(1)
    L2 = ((I * Wm) ** 2).sum(1)
    drift = float(max(np.abs(kin / kin[0] - 1).max(), np.abs(L2 / L2[0] - 1).max()))
    assert drift < 1e-9
    res[k] = dict(t=t, W=Wm, diff=diff, drift=drift, minr=float((np.abs(Wm[:10001, k]) / w0).min()), flips=sign_changes(t, Wm[:, k]))
assert res[0]["minr"] > 0.9999 and res[2]["minr"] > 0.9999 and len(res[0]["flips"]) == 0 and len(res[2]["flips"]) == 0
fl = res[1]["flips"]
t_flip1 = float(fl[0])
dt_flip = float(np.mean(np.diff(fl)))
# 椭圆函数精确解（I₁ < I₂ < I₃，L² > 2E I₂ 时 ω₂ ∝ sn，半周期 2K(k)/ν）
w = np.array([eps * w0, w0, eps * w0])
E2 = (I * w * w).sum()
L2 = ((I * w) ** 2).sum()
assert L2 > E2 * I2
nu = math.sqrt((I3 - I2) * (L2 - E2 * I1) / (I1 * I2 * I3))
k2 = (I2 - I1) * (E2 * I3 - L2) / ((I3 - I2) * (L2 - E2 * I1))
half = 2 * ellipk(k2) / nu
assert abs(dt_flip - half) < 1e-6
diff_all = max(res[k]["diff"] for k in range(3))
drift_all = max(res[k]["drift"] for k in range(3))
# 线性化在开始的一段时间内准确：ω₁、ω₃ 按 e^{λt} 增长
W1 = res[1]["W"]
i05 = int(0.5 / 0.001)
# 线性解：δ₁ = A cosh λt + B sinh λt 的组合，取 t = 0.5 s 比较数值解与线性解
d1, d3 = eps * w0, eps * w0
s1 = (I3 - I2) * w0 / I1 * d3 / lam                                  # δ̇₁(0)/λ，由 I₁δ̇₁ = (I₂ − I₃)ω₀δ₃ 的符号
lin1 = d1 * math.cosh(lam * 0.5) - s1 * math.sinh(lam * 0.5)
lin_err = abs(W1[i05, 0] - lin1) / abs(lin1)
assert lin_err < 0.05

# ---------------------------------------------------------------- (4) 实验 23.4 的阈值
# 任务“扰动 ε ≤ 0.2% 仍在 10 s 内翻转”：演示取 ε = 0.1%；扰动缩小 10 倍，第一次翻转约推迟 ln 10 / λ
tt, We = free_spin(I, np.array([1e-3 * w0, w0, 1e-3 * w0]), 12.0)
t_flip_e3 = float(sign_changes(tt, We[:, 1])[0])
assert t_flip_e3 < 10.0
_, Wd, _ = mj_box(np.array([1e-3 * w0, w0, 1e-3 * w0]), T=4.0)
t_flip_e3_mj = float(sign_changes(np.arange(len(Wd)) * 0.001, Wd[:, 1])[0])
assert abs(t_flip_e3_mj - t_flip_e3) < 1e-6
delay = t_flip_e3 - t_flip1
Ip = np.diag(box_inertia(0.2, 0.16, 0.075, 0.008))
lam_phone = 12.0 * math.sqrt((Ip[2] - Ip[1]) * (Ip[1] - Ip[0]) / (Ip[0] * Ip[2]))

# ---------------------------------------------------------------- (5) 习题答案

out(err_P=err_P, err_K=err_K,
    I_body=I_body, I_out=I_out, I_in=I_in, n_out=n_out, n_in=n_in, n_half=n_half, K_out=K_out, K_in=K_in, W_mus=K_in - K_out, ratio_I=I_out / I_in,
    I1=I1, I2=I2, I3=I3, w0=w0, lam=lam, nu1=nu1, nu3=nu3, t_flip1=t_flip1, dt_flip=dt_flip, half=half, k2=k2,
    diff_all=diff_all, drift_all=drift_all, minr0=res[0]["minr"] * 100, minr2=res[2]["minr"] * 100, lin_err=lin_err * 100,
    e_fold=1 / lam, lam_phone=lam_phone, t_flip_e3=t_flip_e3, delay=delay, ln10_lam=math.log(10) / lam)
