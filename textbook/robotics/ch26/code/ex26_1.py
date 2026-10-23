"""26.1 节的计算：正定性、反对称性、线性参数化。

(1) 回归矩阵：连杆力旋量 𝒢𝒱̇ − [ad_𝒱]ᵀ𝒢𝒱 = Ψ(𝒱, 𝒱̇)π_i（式 (26.1.3)），由它递推出 Y(θ, θ̇, θ̈)（式 (26.1.5)）；
    随机状态下 Yπ 与牛顿-欧拉递推 + 摩擦逐项比较；与 MuJoCo 的逆动力学比较。
(2) 基参数（26.1.4 节）：书中 UR5e 的 13 × 6 = 78 个参数（每个连杆十个惯性参数、转子惯量、库仑摩擦、黏性摩擦），
    300 个随机状态叠成 1800 × 78 的矩阵，带列主元的 QR 分解求秩、恒为零的列、基参数；举例：J_r1 与 I_zz^1 只以和的形式出现。
(3) 算例 26.1.1：用广义动量检测碰撞（反对称性的应用，26.1.2 节）。UR5e 走第 22 章的上下料动作（带夹爪 + 毛坯），
    MuJoCo 中 t = 0.70～0.80 s 在 TCP 处加 40 N 的水平力（模拟撞到人）；观测器用测得的 θ、θ̇、τ，
    ṙ = K_O(τ_ext − r)，r 与真实的 Jᵀℱ_ext 比较；碰撞前 r 的大小（模型无误差时）。
(4) 物理一致性（26.1.5 节）：书中模型每个连杆的伪惯量矩阵正定；把某个连杆的质心放到很远处（参数仍能拟合同一组基参数）时出现负特征值。
(5) 习题答案。
"""
import math

import numpy as np

from _ch26 import (NOCONTACT, chain_pi, collision_demo, full_names, full_pi, full_regressor, mj_load, mjcf_text, ur_base_set,
                   ur_chain, FC_TRUE, FV_TRUE)
from bookout import out

rng = np.random.default_rng(261)
ch = ur_chain()
n = ch.n

# ---------------------------------------------------------------- (1) 回归矩阵
pi = full_pi(ch, FC_TRUE, FV_TRUE)
err_Y = 0.0
for _ in range(50):
    q, qd, qdd = rng.uniform(-3, 3, (3, 6))
    tau = ch.rnea(q, qd, qdd) + FC_TRUE * np.sign(qd) + FV_TRUE * qd
    err_Y = max(err_Y, float(np.abs(full_regressor(ch, q, qd, qdd) @ pi - tau).max()))
assert err_Y < 1e-10
mj, m, d = mj_load(mjcf_text(option=NOCONTACT))
err_mj = 0.0
for _ in range(20):
    q, qd, qdd = rng.uniform(-3, 3, (3, 6))
    d.qpos[:], d.qvel[:], d.qacc[:] = q, qd, qdd
    mj.mj_inverse(m, d)
    Y = full_regressor(ch, q, qd, qdd)
    err_mj = max(err_mj, float(np.abs(Y[:, :66] @ pi[:66] - d.qfrc_inverse).max()))
assert err_mj < 1e-10
n_par = len(pi)

# ---------------------------------------------------------------- (2) 基参数
W, ind, dep, K, rank = ur_base_set()
names = full_names(n)
zero = [names[j] for j in dep if np.abs(W[:, j]).max() < 1e-9]
n_zero = len(zero)
n_dep = len(dep) - n_zero
n_inert_base = sum(1 for j in ind if j < 66)            # 惯性参数（含转子）中的基参数个数
n_fric = sum(1 for j in ind if j >= 66)
assert n_fric == 12
# 例：J_r1 与 I_zz^1 只以和出现：两列相同
i_Jr1, i_Izz1 = names.index("J_r1"), names.index("I_zz^1")
same = float(np.abs(W[:, i_Jr1] - W[:, i_Izz1]).max())
assert same < 1e-12
# 关节 2、3 的转子惯量：J_r2 与 I_zz 类参数并组的例子不必列出；数一数连杆 1 的零列
zero1 = sum(1 for z in zero if z.endswith("^1"))
# 条件数：随机状态下基参数列的条件数
cond_rand = float(np.linalg.cond(W[:, ind]))

# ---------------------------------------------------------------- (3) 算例 26.1.1：广义动量观测器（_ch26.collision_demo）
KO, F_EXT, T0C, T1C = 50.0, 40.0, 0.70, 0.80
t_hist, R_hist, R_nom, E_hist = collision_demo(KO, F_EXT, T0C, T1C)
pre = (t_hist < T0C) & (t_hist > 0.05)
r_pre = float(np.abs(R_hist[pre]).max())
r_pre_nom = float(np.abs(R_nom[pre]).max())
k_hit = int(np.searchsorted(t_hist, T1C - 1e-9)) - 1
r_end = R_hist[k_hit]
e_hit = E_hist[k_hit]
j_big = int(np.argmax(np.abs(e_hit)))
ratio_hit = float(r_end[j_big] / e_hit[j_big])
thr = 1.0                                          # 阈值 1 N·m（示意）
over = np.nonzero((np.abs(R_hist) > thr).any(axis=1) & (t_hist >= T0C))[0]
t_det = float(t_hist[over[0]] - T0C)

# ---------------------------------------------------------------- (4) 物理一致性：伪惯量矩阵
def pseudo(p):
    m, mc = p[0], p[1:4]
    I = np.array([[p[4], p[5], p[6]], [p[5], p[7], p[8]], [p[6], p[8], p[9]]])
    S = 0.5 * np.trace(I) * np.eye(3) - I
    return np.block([[S, mc[:, None]], [mc[None, :], np.array([[m]])]])


pis = chain_pi(ch).reshape(6, 10)
min_eig = min(float(np.linalg.eigvalsh(pseudo(p)).min()) for p in pis)
assert min_eig > 0
# 把连杆 3 的质量减半、质心外移使 m c 不变（m c 不变，惯量不变）：它对运动方程的贡献中 m 只与 m c、I 组合出现吗？
p_bad = pis[2].copy()
p_bad[0] = pis[2][0] * 0.05                         # 质量改成 5%，m c 与 I 不变
eig_bad = float(np.linalg.eigvalsh(pseudo(p_bad)).min())

out(n_par=n_par, err_Y=err_Y, err_mj=err_mj, rank=rank, n_zero=n_zero, n_dep=n_dep, n_inert_base=n_inert_base, n_fric=n_fric,
    zero1=zero1, cond_rand=cond_rand, KO=KO, F_EXT=F_EXT, T0C=T0C, T1C=T1C, r_pre=r_pre, ratio_hit=ratio_hit,
    j_big=j_big + 1, e_big=float(e_hit[j_big]), r_big=float(r_end[j_big]), thr=thr, t_det_ms=t_det * 1000, r_pre_nom=r_pre_nom,
    min_eig=min_eig, eig_bad=eig_bad, m3=pis[2][0])
