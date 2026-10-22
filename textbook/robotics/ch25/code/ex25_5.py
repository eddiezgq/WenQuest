"""25.5 节的计算：UR5e 的关节力矩。

(1) 算例 25.5.1（兑现 1.6 节）：手臂水平伸直静止，θ = (0, 0, 0, −90°, 0, 0)。关节 2 的力矩：手臂自重的部分、各连杆的贡献，
    法兰处 5 kg 负载（质点）的部分；与力矩上限 150 N·m 比较。
(2) 算例 25.5.2：第 22 章上下料动作（A → B，五次多项式，T = 最短时间），法兰上装夹爪 + 毛坯（3.8 kg，算例 23.2.2）。
    六个关节的力矩曲线（图 25.5.1 的数据）、峰值与上限之比、均方根值；峰值时刻的三项分解。
(3) 算例 25.5.3：负载加重（夹爪 + 毛坯按质量等比放大，质心不变）、动作加快：每个关节的力矩峰值达到上限时的负载；
    哪个关节先超限；负载上限随动作时间 T 的变化（图 25.5.2 (a) 的数据）。
(4) 只看静止的力矩上限：负载（质点）的重心沿工具方向离法兰 r 时，最不利姿态下能举的最大质量（图 25.5.2 (b)），哪个关节起限制作用。
    最不利姿态在 θ₁ = 0、θ₂～θ₆ 随机取 4000 组中找（θ₁ 不影响重力力矩）。
(5) 习题答案。
"""
import numpy as np

from _ch25 import G0, TAU_MAX, cell_move, payload_parts, quintic, ur_chain
from bookout import out, tex

thA, thB, T_move = cell_move()
Z = np.zeros(6)
ch0 = ur_chain()
NAMES = ["关节 1", "关节 2", "关节 3", "关节 4", "关节 5", "关节 6"]


def point_payload(m, r=0.0):
    return (m, np.array([0, r, 0.0]), np.zeros((3, 3)))


# ---------------------------------------------------------------- (1) 算例 25.5.1：水平伸直
Q_H = np.array([0, 0, 0, -np.pi / 2, 0, 0])
tau_arm = ch0.rnea(Q_H, Z, Z)
tau_5 = ur_chain(payload=point_payload(5.0)).rnea(Q_H, Z, Z)
arm2 = abs(tau_arm[1])
load2 = abs(tau_5[1]) - arm2
tot2 = abs(tau_5[1])
lever5 = load2 / (5.0 * G0)
# 各连杆对关节 2 力矩的贡献：只留连杆 j 的质量
contrib = []
for j in range(6):
    c = ur_chain()
    for k in range(6):
        if k != j:
            c.G[k] = np.zeros((6, 6))
    contrib.append(abs(c.rnea(Q_H, Z, Z)[1]))
contrib = np.array(contrib)
assert abs(contrib[1:].sum() - arm2) < 1e-9 and contrib[0] < 1e-12
share_up = contrib[1] / arm2 * 100                            # 大臂
share_fa = contrib[2] / arm2 * 100                            # 小臂
share_wr = contrib[3:].sum() / arm2 * 100                     # 手腕三个连杆

# ---------------------------------------------------------------- (2) 算例 25.5.2：上下料动作
pl = payload_parts()
m_p, c_p, I_pc = pl
ch = ur_chain(payload=pl)
ts = np.linspace(0, T_move, 1319)
taus = np.array([ch.rnea(*quintic(thA, thB, T_move, t)) for t in ts])
pk = np.abs(taus).max(0)
k_pk = np.abs(taus).argmax(0)
rms = np.sqrt((taus ** 2).mean(0))
util = pk / TAU_MAX
j_util = int(np.argmax(util)) + 1
order = np.argsort(-util)
# 关节 2 峰值时刻的分解
k2 = k_pk[1]
q2, qd2, qdd2 = quintic(thA, thB, T_move, ts[k2])
g2 = ch.rnea(q2, Z, Z)[1]
i2 = ch.rnea(q2, Z, qdd2, Vd0=np.zeros(6))[1]
c2 = ch.rnea(q2, qd2, Z, Vd0=np.zeros(6))[1]
# 关节 4 峰值时刻的分解
k4 = k_pk[3]
q4, qd4, qdd4 = quintic(thA, thB, T_move, ts[k4])
g4 = ch.rnea(q4, Z, Z)[3]
i4 = ch.rnea(q4, Z, qdd4, Vd0=np.zeros(6))[3]
c4 = ch.rnea(q4, qd4, Z, Vd0=np.zeros(6))[3]

# ---------------------------------------------------------------- (3) 算例 25.5.3：负载加重、动作加快
# 运动方程对惯性参数是线性的（定理 24.3.4）：负载按质量等比放大 k 倍时 τ(t) = τ_手臂(t) + k τ_负载(t)。
# 每个动作时间只要算两遍递推，任意 k 的力矩曲线都由它们线性组合得到。
ch_arm = ur_chain()


def split_curves(T, N=800):
    tt = np.linspace(0, T, N)
    a = np.array([ch_arm.rnea(*quintic(thA, thB, T, t)) for t in tt])
    b = np.array([ch.rnea(*quintic(thA, thB, T, t)) for t in tt]) - a
    return a, b


KS = np.linspace(0, 20, 20001)                              # 负载 = k × 3.8 kg，k 从 0 到 20（0～76 kg）


def payload_limits(T):
    a, b = split_curves(T)
    lim = np.full(6, np.inf)
    for j in range(6):
        P = np.abs(a[:, j][None, :] + KS[:, None] * b[:, j][None, :]).max(1)
        over = np.nonzero(P > TAU_MAX[j])[0]
        if len(over):
            i = over[0]
            lim[j] = (KS[i - 1] + (TAU_MAX[j] - P[i - 1]) / (P[i] - P[i - 1]) * (KS[i] - KS[i - 1])) * m_p
    return lim


lim_T = payload_limits(T_move)
T_v = 15 / 8 * float(np.abs(thB - thA).max()) / np.pi            # 关节 1 的峰值速度达到 180 °/s 的动作时间
assert abs(np.abs(split_curves(T_move)[0] + split_curves(T_move)[1]).max(0)[1] - pk[1]) < 0.05 * pk[1]
j_first = int(np.argmin(lim_T)) + 1
m_first = float(lim_T.min())
TS = [0.6, 0.8, 1.0, T_move, 1.6, 2.0]
lim_all = {T: payload_limits(T) for T in TS}
m_first_06 = float(lim_all[0.6].min())
j_first_06 = int(np.argmin(lim_all[0.6])) + 1
m_first_2 = float(lim_all[2.0].min())
j_first_2 = int(np.argmin(lim_all[2.0])) + 1

# ---------------------------------------------------------------- (4) 静止时的负载曲线
# 质点负载的重力力矩对质量是线性的，对重心偏移 r 也是线性的（质点位置 p = p_f + r y_f，雅可比对 r 线性）：两个 r 算两遍就够。
rng = np.random.default_rng(255)
Q = np.c_[np.zeros(4000), rng.uniform(-np.pi, np.pi, (4000, 5))]
TA = np.array([ch0.rnea(q, Z, Z) for q in Q])
c_0 = ur_chain(payload=point_payload(1.0, 0.0))
c_1 = ur_chain(payload=point_payload(1.0, 1.0))
P0 = np.array([c_0.rnea(q, Z, Z) for q in Q]) - TA
P1 = np.array([c_1.rnea(q, Z, Z) for q in Q]) - TA
qt = Q[17]
assert np.abs(ur_chain(payload=point_payload(1.0, 0.3)).rnea(qt, Z, Z) - TA[17] - (P0[17] + 0.3 * (P1[17] - P0[17]))).max() < 1e-10
RS = np.round(np.linspace(0, 0.5, 11), 3)
m_static, j_static = [], []
for r in RS:
    TP = P0 + r * (P1 - P0)                                  # 1 kg 负载产生的力矩
    with np.errstate(divide="ignore", invalid="ignore"):
        MM = np.where(np.abs(TP) > 1e-12, (TAU_MAX - np.abs(TA)) / np.abs(TP), np.inf)
    i, j = np.unravel_index(np.argmin(MM), MM.shape)
    m_static.append(float(MM[i, j]))
    j_static.append(int(j) + 1)
m_static = np.array(m_static)
ms0, js0 = m_static[0], j_static[0]
i3 = list(RS).index(0.3)
ms3, js3 = m_static[i3], j_static[i3]
i5 = list(RS).index(0.5)
ms5, js5 = m_static[i5], j_static[i5]
r_switch = float(RS[next(k for k, j in enumerate(j_static) if j != js0)])

# ---------------------------------------------------------------- 实验 25.5 的阈值
# (a) 5 kg（夹爪 + 毛坯按质量放大）时，各关节都不超限的最短动作时间（二分）


def pk_ratio(m, T, r=0.0, N=400):
    pl_ = (m, c_p + np.array([0, r, 0]), I_pc * (m / m_p))
    c = ur_chain(payload=pl_)
    tt = np.linspace(0, T, N)
    return (np.abs(np.array([c.rnea(*quintic(thA, thB, T, t)) for t in tt])).max(0) / TAU_MAX)


lo, hi = 0.4, T_move
for _ in range(22):
    mid = 0.5 * (lo + hi)
    if pk_ratio(5.0, mid).max() > 1:
        lo = mid
    else:
        hi = mid
T_lim5 = hi
j_lim5 = int(np.argmax(pk_ratio(5.0, T_lim5 * 0.999))) + 1
# (b) 5 kg、T = 最短时间：负载重心沿工具方向再外移 r，哪个关节先超限、r 多大
lo, hi = 0.0, 1.0
for _ in range(22):
    mid = 0.5 * (lo + hi)
    if pk_ratio(5.0, T_move, mid).max() > 1:
        hi = mid
    else:
        lo = mid
r_lim5 = lo
j_r5 = int(np.argmax(pk_ratio(5.0, T_move, hi))) + 1

# ---------------------------------------------------------------- (5) 习题答案
# 习题 25.5.2：动作时间加倍（T = 2T_min），关节 2、4 力矩峰值
a2, b2 = split_curves(2 * T_move)
pk2x = np.abs(a2 + b2).max(0)

out(arm2=arm2, load2=load2, tot2=tot2, lever5=lever5, share_up=share_up, share_fa=share_fa, share_wr=share_wr,
    T_move=T_move, m_p=m_p,
    pk=tex(pk.reshape(1, -1), 1), util=tex((util * 100).reshape(1, -1), 0), rms=tex(rms.reshape(1, -1), 1),
    pk2=pk[1], pk4=pk[3], util2=util[1] * 100, util4=util[3] * 100, j_util=j_util, rms2=rms[1],
    t_pk2=ts[k2], g2=abs(g2), i2=abs(i2), c2=abs(c2), t_pk4=ts[k4], g4=abs(g4), i4=abs(i4), c4=abs(c4),
    lim2=lim_T[1], lim4=lim_T[3], lim5=lim_T[4], lim3=lim_T[2],
    j_first=j_first, m_first=m_first, m_first_06=m_first_06, j_first_06=j_first_06, m_first_2=m_first_2, j_first_2=j_first_2,
    ms0=ms0, js0=js0, r_switch=r_switch, ms3=ms3, js3=js3, ms5=ms5, js5=js5,
    pk2x=pk2x[1], pk2x4=pk2x[3], T_lim5=T_lim5, T_v=T_v, j_lim5=j_lim5, r_lim5=r_lim5, j_r5=j_r5)
