"""26.4 节的计算：摩擦模型。

(1) 算例 26.4.1：恒速试验。在 MuJoCo 中让“真实”UR5e 的关节 1（轴竖直，不受重力）以 ±0.05～1.5 rad/s 的恒定速度转动，
    其余关节由 PD 保持不动；稳定后取 1.5 s 的平均力矩。正、负速度两边各拟合一条直线 τ = ±f_c + f_v θ̇，得到 f_c、f_v，
    与模型中设的值（frictionloss、damping，示意值）比较。关节 6 同样做一遍。
(2) 斯特里贝克曲线（示意）：τ_f(θ̇) = [f_c + (f_s − f_c) e^{−(θ̇/v_s)²}] sign θ̇ + f_v θ̇（式 (26.4.2)），参数为示意值，只用于图 26.4.1。
(3) 算例 26.4.2：26.3 节的辨识中摩擦参数的偏差从何而来。速度换向时库仑摩擦力矩跳变，低通滤波把跳变抹平，
    而 sign θ̇ 照样跳变，两者在换向附近对不上。去掉 |θ̇_i| < 0.05 rad/s 的行（只去掉该关节的那一行）重新辨识，比较误差。
(4) 摩擦在力矩中的份额：第 22 章上下料动作（带夹爪 + 毛坯）中，各关节摩擦力矩的均方根与总力矩的均方根之比。
(5) 习题答案。
"""
import mujoco
import numpy as np

from _ch26 import (EXC_Q0, FC_TRUE, FV_TRUE, KD, KP, base_from_full, cell_move, exc_experiment, friction_mjcf, full_pi,
                   payload_parts, quintic, ur_base_set, ur_chain, full_names)
from bookout import out

ch = ur_chain()

# ---------------------------------------------------------------- (1) 恒速试验
SPEEDS = [0.05, 0.1, 0.2, 0.5, 1.0, 1.5]


def constant_speed(j, w, T=3.0, dt=0.001):
    m = mujoco.MjModel.from_xml_string(friction_mjcf())
    d = mujoco.MjData(m)
    m.jnt_limited[:] = 0
    d.qpos[:] = EXC_Q0
    d.qvel[j] = w
    taus = []
    for k in range(int(T / dt)):
        t = k * dt
        qdes = EXC_Q0.copy()
        qdes[j] += w * t
        qdd = np.zeros(6)
        qdd[j] = w
        tau = ch.rnea(qdes, qdd, np.zeros(6)) + KP * (qdes - d.qpos) + KD * (qdd - d.qvel)
        d.qfrc_applied[:] = tau
        mujoco.mj_step(m, d)
        if t >= 1.5:
            taus.append(tau[j] - ch.rnea(d.qpos, d.qvel, np.zeros(6))[j])   # 减去模型中的重力、速度项（关节 1 为零）
    return float(np.mean(taus))


def fit(j):
    w = np.array(SPEEDS + [-s for s in SPEEDS])
    tau = np.array([constant_speed(j, x) for x in w])
    A = np.column_stack([np.sign(w), w])
    (fc, fv), *_ = np.linalg.lstsq(A, tau, rcond=None)
    return w, tau, fc, fv


w1, tau1, fc1, fv1 = fit(0)
w6, tau6, fc6, fv6 = fit(5)
err_fc1 = abs(fc1 - FC_TRUE[0])
err_fv1 = abs(fv1 - FV_TRUE[0])
assert err_fc1 < 0.01 and err_fv1 < 0.01 and abs(fc6 - FC_TRUE[5]) < 0.01 and abs(fv6 - FV_TRUE[5]) < 0.01
tau_slow = tau1[0]                                    # +0.05 rad/s 时

# ---------------------------------------------------------------- (2) 斯特里贝克曲线（示意值）
FS_S, FC_S, VS_S, FV_S = 3.0, 2.0, 0.1, 1.5          # 静摩擦、库仑摩擦、斯特里贝克速度、黏性系数（示意值）
tau_slow_st = FC_S + (FS_S - FC_S) * np.exp(-(0.05 / VS_S) ** 2) + FV_S * 0.05   # 习题 26.4.1：0.05 rad/s 处的斯特里贝克模型

# ---------------------------------------------------------------- (3) 算例 26.4.2：去掉低速的行
W0, ind, dep, K, rank = ur_base_set()
names = full_names(6)
pl = payload_parts()
pb_true = base_from_full(full_pi(ur_chain(payload=pl), FC_TRUE, FV_TRUE), ind, dep, K)
E = exc_experiment(payload=pl, seed=263)
Wm, y, Qd = E["W"][:, ind], E["y"], E["Qd"]
VTH = 0.05


def solve(mask):
    pb = np.linalg.lstsq(Wm[mask], y[mask], rcond=None)[0]
    return pb, float(np.linalg.norm(pb - pb_true) / np.linalg.norm(pb_true))


pb_all, e_all = solve(np.ones(len(y), bool))
keep = (np.abs(Qd) > VTH).reshape(-1)
pb_k, e_k = solve(keep)
frac_keep = float(keep.mean() * 100)
nb = [names[j] for j in ind]
fc_all = np.array([pb_all[nb.index(f"f_c{i}")] for i in range(1, 7)])
fv_all = np.array([pb_all[nb.index(f"f_v{i}")] for i in range(1, 7)])
fc_k = np.array([pb_k[nb.index(f"f_c{i}")] for i in range(1, 7)])
fv_k = np.array([pb_k[nb.index(f"f_v{i}")] for i in range(1, 7)])
dfc_all = float(np.abs(fc_all - FC_TRUE).max())
dfc_k = float(np.abs(fc_k - FC_TRUE).max())
# 换向的次数：两个周期中各关节速度过零的次数
n_rev = int(sum(np.sum(np.diff(np.sign(Qd[:, i])) != 0) for i in range(6)))

# ---------------------------------------------------------------- (4) 摩擦的份额
thA, thB, T_move = cell_move()
chp = ur_chain(payload=pl)
ts = np.linspace(0, T_move, 600)
TT = np.array([chp.rnea(*quintic(thA, thB, T_move, t)) for t in ts])
FF = np.array([FC_TRUE * np.sign(quintic(thA, thB, T_move, t)[1]) + FV_TRUE * quintic(thA, thB, T_move, t)[1] for t in ts[1:-1]])
share = np.sqrt(np.mean(FF ** 2, axis=0)) / np.sqrt(np.mean((TT[1:-1] + FF) ** 2, axis=0)) * 100

out(n_speeds=len(SPEEDS) * 2, fc1=fc1, fv1=fv1, fc6=fc6, fv6=fv6, fc1_true=FC_TRUE[0], fv1_true=FV_TRUE[0], fc6_true=FC_TRUE[5],
    fv6_true=FV_TRUE[5], err_fc1=err_fc1, tau_slow=tau_slow, tau_slow_st=tau_slow_st, FS_S=FS_S, FC_S=FC_S, VS_S=VS_S, FV_S=FV_S,
    e_all=e_all * 100, e_k=e_k * 100, VTH=VTH, frac_keep=frac_keep, dfc_all=dfc_all, dfc_k=dfc_k,
    fc2_all=fc_all[1], fv2_all=fv_all[1], fc2_k=fc_k[1], fv2_k=fv_k[1], n_rev=n_rev,
    share1=share[0], share2=share[1], share4=share[3], share6=share[5])
