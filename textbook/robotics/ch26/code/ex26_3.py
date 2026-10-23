"""26.3 节的计算：最小二乘辨识。

(1) 算例 26.3.1：在 MuJoCo 里做辨识实验。“真实的”UR5e = 书中模型 + 法兰上的夹爪和毛坯（3.8 kg，算例 23.2.2）
    + 关节摩擦（库仑、黏性，示意值）。控制器只知道不带负载、不带摩擦的名义模型：τ = RNEA_名义(θ_d) + PD。
    跟踪 26.2 节优化的激励轨迹两个周期（20 s），500 Hz 记录关节角和电机力矩，加上测量噪声（示意值）。
(2) 数据处理（26.3.3 节）：零相位低通滤波（8 Hz）、中心差分求 θ̇、θ̈，力矩同样滤波，每 5 个点取一个。
(3) 最小二乘：用 QR 分解求基参数（不形成 WᵀW，2.5 节）；残差、参数的标准差 σ̂²(WᵀW)⁻¹；与真值比较；
    按各关节噪声大小加权的最小二乘。
(4) 验证（26.3.4 节）：同一台“真实”机器人做第 22 章的上下料动作（不是辨识用的轨迹），用辨识的模型预测电机力矩，
    与实测比较；名义模型（无负载、无摩擦）的预测误差作对照。
(5) 算例 26.3.2 负载辨识（26.3.5 节）：手臂和摩擦已知，只辨识负载的十个参数（写在连杆 6 坐标系中），求质量、质心。
(6) 习题答案。
"""
import numpy as np
import scipy.linalg as sla

from _ch26 import (EXC_TF, FC_TRUE, FV_TRUE, SIGMA_TAU, base_from_full, cell_move, exc_experiment, full_names, full_pi,
                   full_regressor, lowpass_derivatives, payload_parts, quintic, regressor, run_experiment, ur_base_set, ur_chain,
                   FLANGE_Y, pi_from_G, G_frame)
from bookout import out

W0, ind, dep, K, rank = ur_base_set()
names = full_names(6)
pl = payload_parts()
m_p, c_p, I_pc = pl
ch_true = ur_chain(payload=pl)
ch_nom = ur_chain()
pi_true = full_pi(ch_true, FC_TRUE, FV_TRUE)
pb_true = base_from_full(pi_true, ind, dep, K)
# ---------------------------------------------------------------- (1)、(2) 实验与数据处理（_ch26.exc_experiment）
T_EXP = 2 * EXC_TF
DEC = 5
E = exc_experiment(payload=pl, seed=263, dec=DEC)
track = float(np.degrees(E["track"]))
n_raw = E["n_raw"]
Qf, Qd, Qdd, TAUf = E["Qf"], E["Qd"], E["Qdd"], E["TAUf"]
N = len(Qf)
Wm = E["W"][:, ind]
y = E["y"]
cond_m = float(np.linalg.cond(Wm))

# ---------------------------------------------------------------- (3) 最小二乘（QR）
Qr, Rr = sla.qr(Wm, mode="economic")
pb = sla.solve_triangular(Rr, Qr.T @ y)
res = y - Wm @ pb
dof = len(y) - len(pb)
s2 = float(res @ res / dof)
cov = s2 * np.linalg.inv(Rr.T @ Rr)
std = np.sqrt(np.diag(cov))
rms_res = float(np.sqrt(np.mean(res ** 2)))
err_rel = float(np.linalg.norm(pb - pb_true) / np.linalg.norm(pb_true))
# 加权：每行除以该关节的噪声标准差
w = np.tile(1 / SIGMA_TAU, N)
pbw = np.linalg.lstsq(Wm * w[:, None], y * w, rcond=None)[0]
err_rel_w = float(np.linalg.norm(pbw - pb_true) / np.linalg.norm(pb_true))
# 表 26.3.1：选出的基参数（以独立列的名字称呼）
SHOW = ["J_r1", "mc_z^2", "J_r2", "mc_z^3", "I_yy^3", "mc_z^5", "J_r4", "f_c1", "f_c2", "f_v2", "f_c6", "f_v6"]
tab = {}
for k, nm in enumerate(SHOW):
    j = list(ind).index(names.index(nm))
    key = nm.replace("^", "").replace("_", "")
    tab[f"t_{key}"] = pb_true[j]
    tab[f"e_{key}"] = pb[j]
    tab[f"s_{key}"] = std[j]
# 估计误差在 3 倍标准差以内的比例
z = np.abs(pb - pb_true) / std
frac3 = float(np.mean(z < 3) * 100)
# 名义模型（不带负载）的基参数与真值相差多少：mc_z^2 等
pb_nom = base_from_full(full_pi(ch_nom, np.zeros(6), np.zeros(6)), ind, dep, K)

# ---------------------------------------------------------------- (4) 验证：上下料动作
thA, thB, T_move = cell_move()


def traj_v(t):
    if t <= T_move:
        return quintic(thA, thB, T_move, t)
    return quintic(thB, thA, T_move, t - T_move)


tv, Qv, TAUv, _, _ = run_experiment(traj_v, 2 * T_move + 0.5, payload=pl, model=ch_nom, seed=264)
tv1, Qvf, Qvd, Qvdd, TAUvf = lowpass_derivatives(tv, Qv, TAUv)
P_id = np.array([full_regressor(ch_nom, Qvf[k], Qvd[k], Qvdd[k])[:, ind] @ pb for k in range(len(tv1))])
P_nom = np.array([ch_nom.rnea(Qvf[k], Qvd[k], Qvdd[k]) for k in range(len(tv1))])
rms_id = np.sqrt(np.mean((P_id - TAUvf) ** 2, axis=0))
rms_nom = np.sqrt(np.mean((P_nom - TAUvf) ** 2, axis=0))
pk_meas = np.abs(TAUvf).max(0)

# ---------------------------------------------------------------- (5) 负载辨识
# 手臂用书中模型（“真实”机器人的手臂就是它，相当于手臂已辨识得完全准确），摩擦用 (3) 辨识出的值：
# τ − τ_手臂 − 摩擦 = Y_6 π_负载（回归矩阵中连杆 6 的十列）。对照：完全不计摩擦。
fc_id = np.array([pb[list(ind).index(names.index(f"f_c{i}"))] for i in range(1, 7)])
fv_id = np.array([pb[list(ind).index(names.index(f"f_v{i}"))] for i in range(1, 7)])


def payload_id(fc, fv):
    Yl, yl = [], []
    for k in range(N):
        Y = regressor(ch_nom, Qf[k], Qd[k], Qdd[k])
        Yl.append(Y[:, 50:60])
        yl.append(TAUf[k] - ch_nom.rnea(Qf[k], Qd[k], Qdd[k]) - fc * np.sign(Qd[k]) - fv * Qd[k])
    Yl, yl = np.vstack(Yl), np.concatenate(yl)
    p = np.linalg.lstsq(Yl, yl, rcond=None)[0]
    m = p[0]
    c = p[1:4] / m - np.array([0, FLANGE_Y, 0])                   # 质心在法兰坐标系中
    return m, c, abs(m - m_p) / m_p * 100, float(np.linalg.norm(c - c_p) * 1000), float(np.linalg.cond(Yl))


m_hat, c_hat, err_m, err_c_mm, cond_pl = payload_id(fc_id, fv_id)
_, _, err_m_nf, err_c_nf, _ = payload_id(np.zeros(6), np.zeros(6))

# ---------------------------------------------------------------- (6) 摩擦参数的偏差（26.4 节解释）；滤波后的噪声
dfc = (fc_id - FC_TRUE) / FC_TRUE * 100
dfv = (fv_id - FV_TRUE) / FV_TRUE * 100
zf = np.array([abs(pb[list(ind).index(names.index(nm))] - pb_true[list(ind).index(names.index(nm))]) /
               std[list(ind).index(names.index(nm))] for nm in [f"f_{t}{i}" for t in "cv" for i in range(1, 7)]]).reshape(2, 6)
z13_lo, z13_hi = float(zf[:, :3].min()), float(zf[:, :3].max())
z46_lo, z46_hi = float(zf[:, 3:].min()), float(zf[:, 3:].max())
rng_n = np.random.default_rng(265)
tn = np.arange(n_raw) * (EXC_TF * 2 / n_raw)
_, _, _, _, NF = lowpass_derivatives(tn, np.zeros((n_raw, 6)), rng_n.normal(0, 1, (n_raw, 6)) * SIGMA_TAU)
rms_noise_raw = float(np.sqrt(np.mean(SIGMA_TAU ** 2)))
rms_noise_f = float(np.sqrt(np.mean(NF ** 2)))
NFd = NF[::DEC]
rho_dec = float(np.mean([np.corrcoef(NFd[:-1, i], NFd[1:, i])[0, 1] for i in range(6)]))

out(T_EXP=T_EXP, track=track, n_raw=n_raw, N=N, DEC=DEC, n_rows=len(y), n_base=len(ind), cond_m=cond_m, rms_res=rms_res,
    err_rel=err_rel * 100, err_rel_w=err_rel_w * 100, frac3=frac3, s2=s2,
    rms_id2=rms_id[1], rms_nom2=rms_nom[1], rms_id4=rms_id[3], rms_nom4=rms_nom[3], rms_id1=rms_id[0], rms_nom1=rms_nom[0],
    pk2=pk_meas[1], m_hat=m_hat, m_p=m_p, cy_hat=c_hat[1] * 1000, cy_true=c_p[1] * 1000, cx_hat=c_hat[0] * 1000,
    cz_hat=c_hat[2] * 1000, err_m=err_m, err_c_mm=err_c_mm, cond_pl=cond_pl, err_m_nf=err_m_nf, err_c_nf=err_c_nf,
    dfc_lo=float(-dfc.max()), dfc_hi=float(-dfc.min()), dfv_lo=float(dfv.min()), dfv_hi=float(dfv.max()),
    z13_lo=z13_lo, z13_hi=z13_hi, z46_lo=z46_lo, z46_hi=z46_hi, rms_noise_raw=rms_noise_raw, rms_noise_f=rms_noise_f, rho_dec=rho_dec,
    mcz2_nom=pb_nom[list(ind).index(names.index("mc_z^2"))], Jr1_nom=pb_nom[list(ind).index(names.index("J_r1"))], **tab)
