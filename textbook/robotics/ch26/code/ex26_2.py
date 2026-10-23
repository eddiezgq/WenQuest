"""26.2 节的计算：激励轨迹设计。

(1) 有限项傅里叶级数（式 (26.2.1)）：周期 T_f = 10 s，每个关节 L = 5 个谐波，共 60 个系数；θ₀ 为书中的初始姿态。
    限制：偏离 θ₀ 的转角、速度 1.5 rad/s、加速度（示意值）、各关节原点和 TCP 离地 0.15 m 以上。
(2) 优化（26.2.3 节）：目标是基参数回归矩阵的条件数（取对数），一个周期取 60 个时刻；先随机取 40 组系数，挑最好的一组，
    再用鲍威尔法（scipy.optimize.minimize, method="Powell"）局部改进；最后按 1000 个时刻核对限制，不满足时整体缩小幅度。
    结果与 _ch26.py 中保存的轨迹（EXC_A、EXC_B，供后面各节和实验使用）比较。
(3) 三种轨迹的条件数：第 22 章的上下料动作（往返一次）、随机的傅里叶轨迹（满足同样限制的 20 组，取中位数）、优化后的轨迹；
    奇异值（图 26.2.2 的数据）。
(4) 条件数与辨识误差：对三种轨迹，用真参数算出“无误差的力矩”，加上同样的测量噪声，最小二乘求基参数，重复 50 次，
    看参数误差的大小（不经过仿真，只看轨迹本身的影响）。
(5) 习题答案。
"""
import numpy as np
from scipy.optimize import minimize

from _ch26 import (EXC_A, EXC_B, EXC_L, EXC_Q0, EXC_TF, FC_TRUE, FV_TRUE, SIGMA_TAU, Fourier, base_from_full, cell_move,
                   exc_violation, full_pi, full_regressor, quintic, ur_base_set, ur_chain)
from bookout import out, tex

ch = ur_chain()
W, ind, dep, K, rank = ur_base_set()
n = 6
NC = n * EXC_L * 2
TS60 = np.linspace(0, EXC_TF, 61)[:-1]
TS1000 = np.linspace(0, EXC_TF, 1001)[:-1]


def Wb_of(q, qd, qdd):
    return np.vstack([full_regressor(ch, q[k], qd[k], qdd[k]) for k in range(len(q))])[:, ind]


def cond_of(tr, ts):
    return float(np.linalg.cond(Wb_of(*tr.eval(ts))))


def traj_of(x, scale=1.0):
    return Fourier(EXC_Q0, scale * x[:NC // 2].reshape(n, EXC_L), scale * x[NC // 2:].reshape(n, EXC_L), EXC_TF)


def cost(x):
    tr = traj_of(x)
    return np.log10(cond_of(tr, TS60)) + 100 * exc_violation(ch, tr, TS60)


# ---------------------------------------------------------------- (2) 优化
rng = np.random.default_rng(262)
cands = [rng.normal(0, 0.15, NC) for _ in range(40)]
costs = [cost(x) for x in cands]
x0 = cands[int(np.argmin(costs))]
res = minimize(cost, x0, method="Powell", options=dict(maxfev=1500, xtol=1e-3, ftol=1e-4))
scale = 1.0
while exc_violation(ch, traj_of(res.x, scale), TS1000) > 0:
    scale -= 0.01
tr_new = traj_of(res.x, scale)
cond_new = cond_of(tr_new, TS1000)
tr_opt = Fourier(EXC_Q0, EXC_A, EXC_B, EXC_TF)                # 保存的轨迹
assert exc_violation(ch, tr_opt, TS1000) == 0
q, qd, qdd = tr_opt.eval(TS1000)
cond_opt = cond_of(tr_opt, TS1000)
assert cond_new < 1.5 * cond_opt                               # 重新优化的结果不比保存的差太多
cond_start = cond_of(traj_of(x0), TS1000)                    # 初值（随机 40 组中最好的一组），按 1000 个时刻算
assert exc_violation(ch, traj_of(x0), TS1000) == 0
vmax = np.abs(qd).max(0)
amp = np.degrees(np.abs(q - EXC_Q0).max(0))

# ---------------------------------------------------------------- (3) 三种轨迹
thA, thB, T_move = cell_move()
ts_m = np.linspace(0, 2 * T_move, 400)


def cell_round(t):
    return quintic(thA, thB, T_move, t) if t <= T_move else quintic(thB, thA, T_move, t - T_move)


Qm = np.array([cell_round(t) for t in ts_m])
Wm = Wb_of(Qm[:, 0], Qm[:, 1], Qm[:, 2])
sv_m = np.linalg.svd(Wm, compute_uv=False)
rank_m = int(np.sum(sv_m > sv_m[0] * 1e-10))
cond_m = float(sv_m[0] / sv_m[-1])
rand_conds = []
k = 0
while len(rand_conds) < 20:
    x = rng.normal(0, 0.15, NC)
    s = 1.0
    while exc_violation(ch, traj_of(x, s), TS60) > 0 and s > 0.05:
        s *= 0.9
    rand_conds.append(cond_of(traj_of(x, s), TS1000))
cond_rand = float(np.median(rand_conds))
sv_opt = np.linalg.svd(Wb_of(q, qd, qdd), compute_uv=False)

# ---------------------------------------------------------------- (4) 条件数与辨识误差
pi_true = full_pi(ch, FC_TRUE, FV_TRUE)
pb_true = base_from_full(pi_true, ind, dep, K)


def ls_error(Wx, reps=50):
    y0 = Wx @ pb_true
    sig = np.tile(SIGMA_TAU, len(y0) // 6)
    errs = []
    for _ in range(reps):
        pb = np.linalg.lstsq(Wx, y0 + rng.normal(0, 1, len(y0)) * sig, rcond=None)[0]
        errs.append(np.linalg.norm(pb - pb_true) / np.linalg.norm(pb_true))
    return float(np.median(errs))


rand_tr = traj_of(rng.normal(0, 0.15, NC), 0.3)
err_opt = ls_error(Wb_of(q, qd, qdd))
err_rand = ls_error(Wb_of(*rand_tr.eval(TS1000)))
cond_rand1 = cond_of(rand_tr, TS1000)
err_m = ls_error(Wm)

# ---------------------------------------------------------------- (5) 习题答案
# 习题 26.2.3：把优化轨迹的幅度缩小一半，条件数变为多少
tr_half = Fourier(EXC_Q0, 0.5 * EXC_A, 0.5 * EXC_B, EXC_TF)
cond_half = cond_of(tr_half, TS1000)

print("EXC_A =", np.array2string(scale * res.x[:NC // 2].reshape(n, EXC_L), separator=", ", precision=6, max_line_width=200))
print("EXC_B =", np.array2string(scale * res.x[NC // 2:].reshape(n, EXC_L), separator=", ", precision=6, max_line_width=200))
out(n_coef=NC, n_base=len(ind), cond_start=cond_start, cond_new=cond_new, cond_opt=cond_opt, scale=scale, nfev=res.nfev,
    vmax=tex(vmax.reshape(1, -1), 2), amp=tex(amp.reshape(1, -1), 0), rank_m=rank_m, cond_m=cond_m, cond_rand=cond_rand,
    sv_max=float(sv_opt[0]), sv_min=float(sv_opt[-1]), err_opt=err_opt * 100, err_rand=err_rand * 100, err_m=err_m * 100,
    cond_rand1=cond_rand1, cond_half=cond_half)
