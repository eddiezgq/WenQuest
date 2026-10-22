"""25.2 节的计算：反向递推力旋量。

(1) 算例 25.2.1：与算例 25.1.1 同一时刻（第 22 章上下料动作 t = 0.40 s），法兰上装夹爪 + 毛坯（算例 23.2.2），
    牛顿-欧拉递推（算法 25.2.1）求六个关节力矩；与 MuJoCo 的逆动力学 mj_inverse 比较；与第 24 章的 M = ΣJᵀ𝒢J、
    克里斯托费尔符号、g = ∂U/∂θ（数值微分）比较。用同一个递推分出惯性项、速度项、重力项（25.2.4 节）。
(2) 算例 25.2.2：同一时刻各关节传给连杆的力旋量 ℱ_i，分成绕轴力矩、弯曲力矩、轴向力、径向力；与 MuJoCo 的 cfrc_int 比较。
    整个动作中关节 2、关节 1 的弯曲力矩与径向力的最大值，以及若动作极慢（只有重力）时的对应值。
(3) 法兰受外力（25.2.6 节）：静止在卡盘前的位姿 θ_B、不计重力时，法兰向外推 50 N（沿工具方向），递推得到的力矩等于 J_fᵀℱ（式 (16.5.1) 的静力学）。
(4) 生活中的例子：伸直手臂端一盆水（示意值），手腕、肘、肩的力矩由外向内累加。
(5) 习题答案。
"""
import numpy as np

from _ch25 import (G0, adjoint, cell_move, christoffel, dM, gravity, inv, mass_matrix, mj_joint_wrenches, parse_links, mjcf_text,
                   payload_parts, potential, quintic, split_wrench, ur_chain, ur_mj)
from bookout import out, tex

thA, thB, T_move = cell_move()
pl = payload_parts()
m_p, c_p, I_pc = pl
ch = ur_chain(payload=pl)
mj, m, d = ur_mj(payload=pl)
n = ch.n
t1 = 0.40
q, qd, qdd = quintic(thA, thB, T_move, t1)
Z = np.zeros(n)

# ---------------------------------------------------------------- (1) 算例 25.2.1
tau, Fs, _ = ch.rnea(q, qd, qdd, full=True)
d.qpos[:], d.qvel[:], d.qacc[:] = q, qd, qdd
mj.mj_inverse(m, d)
tau_mj = np.array(d.qfrc_inverse)
err_mj = float(np.abs(tau - tau_mj).max())
assert err_mj < 1e-9
# 三项分解：同一个递推，把不需要的输入置零
tau_g = ch.rnea(q, Z, Z)                                  # 重力项 g(θ)
tau_c = ch.rnea(q, qd, Z, Vd0=np.zeros(6))                # 速度项 c(θ, θ̇)
tau_i = ch.rnea(q, Z, qdd, Vd0=np.zeros(6))               # 惯性项 M(θ)θ̈（含转子）
assert np.abs(tau_g + tau_c + tau_i - tau).max() < 1e-10
# 第 24 章的写法：M = ΣJᵀ𝒢J，克里斯托费尔符号，g = ∂U/∂θ（中心差分）
links = parse_links(mjcf_text())
G_pl = ch.G[-1] - links[-1].G                             # 负载在连杆 6 坐标系中的空间惯量
extraM = (links[-1].name, G_pl)
c_pl_6 = ch.Mf[:3, 3] + c_p
Mfun = lambda th: mass_matrix(links, th, extraM)          # noqa: E731
Ufun = lambda th: potential(links, th, (links[-1].name, m_p, c_pl_6))   # noqa: E731
M24 = Mfun(q) + np.diag(ch.arm)
C24 = christoffel(dM(Mfun, q)) @ qd
g24 = gravity(Ufun, q)
tau24 = M24 @ qdd + C24 @ qd + g24
err_24 = float(np.abs(tau24 - tau).max())
assert err_24 < 1e-5
share_g = np.abs(tau_g) / (np.abs(tau_g) + np.abs(tau_c) + np.abs(tau_i))

# ---------------------------------------------------------------- (2) 算例 25.2.2：关节里的力
Fmj = mj_joint_wrenches(mj, m, d, ch.names, q, qd, qdd)
err_F = max(float(np.abs(a - b).max()) for a, b in zip(Fs, Fmj))
assert err_F < 1e-9
parts = [split_wrench(F, ch.A[i][:3]) for i, F in enumerate(Fs)]
for i, (ma, mb, fa, fr) in enumerate(parts):
    assert abs(ma + ch.arm[i] * qdd[i] - tau[i]) < 1e-10      # 绕轴力矩 + 转子惯性力矩 = 关节力矩
tab = {}
for i, (ma, mb, fa, fr) in enumerate(parts):
    tab[f"tq{i + 1}"] = tau[i]
    tab[f"mb{i + 1}"] = mb
    tab[f"fa{i + 1}"] = fa
    tab[f"fr{i + 1}"] = fr
# 整个动作
ts = np.linspace(0, T_move, 1319)
pk = np.zeros((n, 2))
pk_static = np.zeros((n, 2))
for t in ts:
    qq, qqd, qqdd = quintic(thA, thB, T_move, t)
    _, Fd, _ = ch.rnea(qq, qqd, qqdd, full=True)
    _, Fst, _ = ch.rnea(qq, Z, Z, full=True)
    for i in range(n):
        _, mb, _, fr = split_wrench(Fd[i], ch.A[i][:3])
        _, mbs, _, frs = split_wrench(Fst[i], ch.A[i][:3])
        pk[i] = np.maximum(pk[i], (mb, fr))
        pk_static[i] = np.maximum(pk_static[i], (mbs, frs))
# 整台手臂加负载的重力
m_arm = sum(L.m for L in links[1:])
W_total = (m_arm + m_p) * G0
W_moving = (m_arm - links[1].m + m_p) * G0               # 关节 2 以外（连杆 2～6 加负载）的重力

# ---------------------------------------------------------------- (3) 法兰受外力
F_push = 50.0
Ftip = np.array([0, 0, 0, 0, F_push, 0])                 # 写在 {f} 中：法兰沿工具方向（+y_f）向外推
tau_push = ch.rnea(thB, Z, Z, Vd0=np.zeros(6), Ftip=Ftip)
Jf = adjoint(inv(ch.Mf)) @ ch.jacobians(thB)[-1]
err_static = float(np.abs(tau_push - Jf.T @ Ftip).max())
assert err_static < 1e-12

# ---------------------------------------------------------------- (4) 生活中的例子：端一盆水（示意值）
# 手臂水平伸直：上臂 0.30 m、2.0 kg，前臂 0.27 m、1.3 kg，手 0.5 kg（质心距腕 0.08 m）；水盆 5 kg 在手心（距腕 0.08 m）
L_up, m_up, L_fa, m_fa, m_hand, c_hand, m_bowl = 0.30, 2.0, 0.27, 1.3, 0.5, 0.08, 5.0
M_wrist = (m_hand + m_bowl) * G0 * c_hand
M_elbow = M_wrist + (m_hand + m_bowl) * G0 * L_fa + m_fa * G0 * L_fa / 2
M_shoulder = M_elbow + (m_hand + m_bowl + m_fa) * G0 * L_up + m_up * G0 * L_up / 2
r_sh_wr = M_shoulder / M_wrist

# ---------------------------------------------------------------- (5) 习题答案
# 习题 25.2.3：在 θ_B 法兰向外推 50 N 时，关节 2 的力矩（静止、不计重力）
tau_push2 = tau_push[1]

out(t1=t1, tau=tex(tau.reshape(1, -1), 2), err_mj=err_mj, err_24=err_24,
    tg=tex(tau_g.reshape(1, -1), 2), tc=tex(tau_c.reshape(1, -1), 2), ti=tex(tau_i.reshape(1, -1), 2),
    share_g2=share_g[1] * 100, share_g3=share_g[2] * 100, tau2=tau[1], tau4=tau[3],
    err_F=err_F, **tab,
    mb2_pk=pk[1, 0], fr2_pk=pk[1, 1], mb2_st=pk_static[1, 0], fr2_st=pk_static[1, 1],
    mb1_pk=pk[0, 0], fr1_pk=pk[0, 1], mb1_st=pk_static[0, 0], fr1_st=pk_static[0, 1],
    dyn_mb2=(pk[1, 0] / pk_static[1, 0] - 1) * 100,
    W_total=W_total, W_moving=W_moving, m_arm=m_arm,
    F_push=F_push, err_static=err_static, tau_push2=tau_push2, tau_push=tex(tau_push.reshape(1, -1), 2),
    M_wrist=M_wrist, M_elbow=M_elbow, M_shoulder=M_shoulder, r_sh_wr=r_sh_wr)
