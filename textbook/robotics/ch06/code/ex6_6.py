"""6.6 节的算例。

算例 6.6.1：UR5e 在零位，抓着 5 kg 的负载，负载质心在法兰盘中心沿 ŷ_b 方向 0.05 m 处。
            机器人对负载施加的力旋量 F_s（托住负载）；零位时各关节需要的静力矩 τ_i = S_iᵀ F_s（式 (6.6.6)）。
            独立核对：虚功原理——τ_i 等于负载重力势能 m𝔤 z_c(θ) 对 θ_i 的偏导数（数值求导）。
算例 6.6.2：法兰盘上的六维力传感器的读数 F_b = [Ad_{T_sb}]ᵀ F_s（式 (6.6.4)）；与直接按 f_b = Rᵀf、m_b = r_b × f_b 计算比较。
            功率不变：关节 2 以 30°/s 转动时，F_sᵀV_s = F_bᵀV_b = τ₂θ̇₂。
算例 6.6.3：力旋量的中心轴与节距（潘索）：两个不共面的力合成的力旋量。
另：互易积的几何公式 (6.6.11) 与定义 (6.6.10) 对随机的旋量一致；转动关节的旋量轴与过其轴线的任何力互易。
"""
import math

import numpy as np

from _screw import UR_AXES, UR_M, UR_S, adjoint, exp6, inv, pose, screw_from_axis, ur_fk
from bookout import out, tex, vec

g = 9.81
m = 5.0
rb = np.array([0, 0.05, 0])                       # 负载质心在 {b} 中的位置 (m)
c = (UR_M @ np.r_[rb, 1])[:3]                     # 零位时负载质心在 {s} 中的位置
f_up = np.array([0, 0, m * g])                    # 机器人托住负载的力
F = np.r_[np.cross(c, f_up), f_up]                # 力旋量 F_s = (m_s, f_s)，力矩对 {s} 原点
tau = np.array([S @ F for S in UR_S])


def zc(th):
    return (ur_fk(th) @ np.r_[rb, 1])[2]


h = 1e-6
tau_vw = np.array([m * g * (zc(np.eye(6)[i] * h) - zc(-np.eye(6)[i] * h)) / (2 * h) for i in range(6)])
assert np.allclose(tau, tau_vw, atol=1e-6)
# 按几何：τ_i = ω_i · ((c − q_i) × f)
for (w, q), t in zip(UR_AXES, tau):
    assert abs(w @ np.cross(c - q, f_up) - t) < 1e-12

# ---------------------------------------------------------------- 算例 6.6.2
Fg_s = -F                                          # 负载作用在法兰盘上的力旋量（传感器测得的就是它）
Fb = adjoint(UR_M).T @ Fg_s
R = UR_M[:3, :3]
fb = R.T @ Fg_s[3:]
mb = np.cross(rb, fb)
assert np.allclose(Fb, np.r_[mb, fb])
# 功率不变
rate = math.radians(30)
Vs = UR_S[1] * rate
Vb = adjoint(inv(UR_M)) @ Vs
P_s, P_b = F @ Vs, (adjoint(UR_M).T @ F) @ Vb
assert abs(P_s - P_b) < 1e-12 and abs(P_s - tau[1] * rate) < 1e-12

# ---------------------------------------------------------------- 算例 6.6.3 中心轴
# 两个力：f1 = (0, 0, −10) N 作用在 (0.2, 0, 0) m；f2 = (0, 10, 0) N 作用在 (0, 0, 0.3) m
P1, f1 = np.array([0.2, 0, 0]), np.array([0, 0, -10.0])
P2, f2 = np.array([0, 0, 0.3]), np.array([0, 10.0, 0])
fR = f1 + f2
mR = np.cross(P1, f1) + np.cross(P2, f2)
hw = float(mR @ fR / (fR @ fR))                    # 节距 (m)
qw = np.cross(fR, mR) / (fR @ fR)                  # 中心轴上离原点最近的点
assert np.allclose(np.r_[mR, fR], np.r_[np.cross(qw, fR) + hw * fR, fR])     # 式 (6.6.7)
# 中心轴上，力矩与力平行且最小
mq = mR - np.cross(qw, fR)
assert np.allclose(np.cross(mq, fR), 0) and np.linalg.norm(mq) <= np.linalg.norm(mR) + 1e-12
m_central = float(np.linalg.norm(mq))

# ---------------------------------------------------------------- 互易积的几何公式
rng = np.random.default_rng(66)


def recip(S1, S2):
    return S1[:3] @ S2[3:] + S2[:3] @ S1[3:]


for _ in range(50):
    s1, s2 = (x / np.linalg.norm(x) for x in rng.normal(size=(2, 3)))
    q1, q2 = rng.normal(size=(2, 3))
    h1, h2 = rng.normal(size=2)
    A, B = screw_from_axis(q1, s1, h1), screw_from_axis(q2, s2, h2)
    n = np.cross(s1, s2)
    sa = np.linalg.norm(n)
    n /= sa
    ca = s1 @ s2
    # 公垂线上的有向距离 d：从轴 1 到轴 2 沿 n 量
    dd = (q2 - q1) @ n
    assert abs(recip(A, B) - ((h1 + h2) * ca - dd * sa)) < 1e-10
# 关节 2 的旋量轴与一个过关节 2 轴线的力互易：该力不产生关节 2 的力矩
w2, q2_ = UR_AXES[1]
fx = np.array([0.3, 0.0, -1.0])
Fx = np.r_[np.cross(q2_, fx), fx]
assert abs(UR_S[1] @ Fx) < 1e-12

out(c=vec(c, 3), F=vec(F, 3), tau=vec(tau, 2), tau2=tau[1], tau3=tau[2], tau4=tau[3], mg=m * g,
    Fb=vec(Fb, 3), fb=vec(fb, 2), mb=vec(mb, 4), Vs=vec(Vs, 4), Vb=vec(Vb, 4), P=P_s, rate=rate,
    fR=vec(fR, 1), mR=vec(mR, 1), hw=hw, qw=vec(qw, 4), m_central=m_central, AdMT=tex(adjoint(UR_M).T, 3))
