"""22.6 节的计算：沿给定路径的时间最优轨迹。

(1) 算例 22.6.1：关节空间的直线（算例 22.1.1 的 A → B）。时间最优参数化（22.6.4 节的算法，网格 1000）与梯形速度曲线
    （定理 22.2.1、算例 22.2.1）核对；另一种算法（前推、后推的数值积分法）给出同样的时间。
(2) 算例 22.6.2：经过 R、A、M、B 的三次样条路径（算例 22.3.1 的几何路径，以样条的时间作路径参数 s）。
    时间最优参数化（网格 4000）与数值积分法的时间；与样条整体缩放（算例 22.3.1）比较；
    按时间重新采样、用差商检查关节速度、加速度是否超限；每一时刻起作用的约束。
(3) 算例 22.6.3：时间最优轨迹的加速度是 bang-bang 的，加速度跳变。按定理 22.2.2，把 s(t) 用宽 t_j = 1/f_n 的盒形窗
    滑动平均，加加速度有界；滤波后的加速度略超限值，于是把限值按比例 η 降低重新求解，二分法求不超限的最大 η。
    比较三种做法的转移时间、关节 1 的最大加加速度和 22.2 节扭转模态（8 Hz）的残余振幅、等待时间。
(4) 算例 22.6.4：经过手腕奇异附近的直线（算例 22.4.4）。限值：关节速度、加速度同前，TCP 速度 ≤ 0.25 m/s、
    沿直线的加速度 ≤ 1 m/s²（示意值）。时间最优的直线速度曲线、总时间，中点处的速度。
(5) 上下料半个循环的节拍：夹紧 0.3 s + 转移 + 送料 1.4 s（算例 22.4.1）+ 松开 0.3 s（夹紧、松开时间为示意值），
    转移后要等振动衰减到 0.05 mm 才能送料。
"""
import math

import numpy as np

from _traj import (AMAX, FN_TOOL, VMAX, ZETA_TOOL, arclength_path, cell_joints, fir_smooth, follow_line, poly_breaks, resample_path, response_pw,
                   path_constraints, s_quintic, segs_eval, tcp_fk, topp, topp_classic, trap_plan, wrist_line)
from bookout import out
import ex22_3 as E3
import ex22_4 as E4

deg = np.degrees
thR, thA, thB, thC = cell_joints()

# ---------------------------------------------------------------- (1) 关节空间的直线
dq = thB - thA
N1 = 1000
s1 = np.linspace(0, 1, N1 + 1)
D1, DD1 = np.tile(dq, (N1 + 1, 1)), np.zeros((N1 + 1, 6))
x1, u1, t1, K1, XV1 = topp(s1, D1, DD1, VMAX, AMAX)
T_line = float(t1[-1])
xc1, tc1, _ = topp_classic(s1, D1, DD1, VMAX, AMAX)
T_trap = trap_plan(abs(dq[0]), VMAX[0], AMAX[0])["T"]
assert abs(T_line - T_trap) < 1e-5 * T_trap and abs(tc1[-1] - T_trap) < 1e-5 * T_trap
sd_bar = float(min(VMAX / np.abs(dq)))                 # 直线上的 ṡ 上限 min v_i/|Δθ_i|
sdd_bar = float(min(AMAX / np.abs(dq)))

# ---------------------------------------------------------------- (2) 样条路径
# 样条两端速度为零（θ_u = 0），以样条的时间 u 作路径参数时两端退化；改用关节空间中的弧长 σ 作路径参数（‖θ′(σ)‖ = 1）
S, U = E3.S, E3.T_spl
N2 = 4000
fq, f1, f2 = (lambda u: segs_eval(S, u)), (lambda u: segs_eval(S, u, 1)), (lambda u: segs_eval(S, u, 2))
s2, ug2, D2, DD2, u_of = arclength_path(fq, f1, f2, U, N2)
L_sig = float(s2[-1])
x2, u2, t2, K2, XV2 = topp(s2, D2, DD2, VMAX, AMAX)
T_opt = float(t2[-1])
xc2, tc2, MVC2 = topp_classic(s2, D2, DD2, VMAX, AMAX)
T_cls = float(tc2[-1])
assert abs(T_opt - T_cls) < 0.005 * T_opt
# 网格加密时两种算法的差别减小
sa, _, Da, DDa, _ = arclength_path(fq, f1, f2, U, 1000)
xa, ua, ta, _, _ = topp(sa, Da, DDa, VMAX, AMAX)
_, tca, _ = topp_classic(sa, Da, DDa, VMAX, AMAX)
gap1000, gap4000 = float(ta[-1] - tca[-1]), T_opt - T_cls
assert 0 < gap4000 < gap1000
save_opt = 1 - T_opt / U


# 定理 22.6.4 (2) 的充分条件：f_k(x) = min(K_{k+1}, x + 2Δσ u_max(x)) 在 [0, K_k] 上单调不减（22.6.4 节正文）。
def cond_check(s, dq, ddq, K, vmax, amax):
    """返回 (粗判据不满足的点数及位置, 精确判据不满足的点数及位置)。
    粗判据：对每个 θ_i′ ≠ 0 的关节，2Δσ|θ_i″/θ_i′| < 1（各加速度上界的斜率都为正）。
    精确判据：f_k 是凹的分段线性函数，单调不减当且仅当它在右端 K_k 处取到上限 K_{k+1}，或右端的左导数 ≥ 0；
    左导数 = 在 K_k 处起作用的那些上界 x + 2Δσ (a_i ∓ θ_i″x)/|θ_i′| 中最大的斜率。
    另在 [0, K_k] 上取点直接核对（下降段可能很窄，紧挨 K_k，所以在 K_k 左边按对数加密取点）。"""
    ds = np.diff(s)
    crude, exact = [], []
    for k in range(len(s) - 1):
        _, Ga, ha = path_constraints(dq, ddq, vmax, amax, k)
        up = Ga[:, 1] > 1e-12                        # 给出 u 上界的行：u ≤ (h − g_x x)/g_u
        sl = 1 - 2 * ds[k] * Ga[up, 0] / Ga[up, 1]   # 各上界对应的 x + 2Δσ u 的斜率
        if np.any(sl <= 0):
            crude.append(k)

        def f(x):
            return min(K[k + 1], x + 2 * ds[k] * np.min((ha[up] - Ga[up, 0] * x) / Ga[up, 1]))
        x_end = K[k]
        g = x_end + 2 * ds[k] * (ha[up] - Ga[up, 0] * x_end) / Ga[up, 1]
        gmin = g.min()
        bad = False
        if gmin < K[k + 1] - 1e-12 * (1 + K[k + 1]):
            act = g <= gmin + 1e-9 * (1 + abs(gmin))
            bad = sl[act].max() < 0
        xs = np.unique(np.concatenate([np.linspace(0, K[k], 201), K[k] * (1 - np.logspace(-10, -1, 91))]))
        fs = np.array([f(x) for x in xs])
        bad_num = np.any(np.diff(fs) < -1e-9 * (1 + np.abs(fs[1:])))
        assert bad == bad_num
        if bad or bad_num:
            exact.append(k)
    return crude, exact


crude2, exact2 = cond_check(s2, D2, DD2, K2, VMAX, AMAX)
cond_bad = len(exact2)
crude_bad = len(crude2)
# 不满足的点成对出现在某个 θ_i′ 变号处（该关节在那里掉头）：按位置归并，记下位置和关节
groups = []
for k in exact2:
    if groups and k - groups[-1][-1] <= 2:
        groups[-1].append(k)
    else:
        groups.append([k])
cond_where = [(float(s2[g[0]]), int(np.argmin(np.abs(D2[g[0]]))) + 1) for g in groups]
assert cond_bad <= 10 and all(abs(D2[k]).min() < 2e-3 for k in exact2)
assert len(cond_where) == 2                     # 正文按“两处”叙述
# 按时间重新采样，差商检查
dt = 1e-3
tt = np.arange(0, T_opt + dt / 2, dt)
ss = resample_path(t2, s2, x2, u2, tt)
TH = segs_eval(S, np.clip(u_of(ss), 0, U))
V = np.gradient(TH, dt, axis=0)
A = np.gradient(V, dt, axis=0)
rv = float(np.max(np.abs(V) / VMAX))
ra = float(np.max(np.abs(A[2:-2]) / AMAX))
assert rv < 1.001 and ra < 1.01
# 每一网格区间起作用的约束：速度（哪一关节）或加速度（哪一关节、上限还是下限）
sd2 = np.sqrt(np.maximum(x2, 0))
act_v = np.max(np.abs(D2) * sd2[:, None] / VMAX, axis=1)                       # 速度利用率（取最大的关节）
acc2 = D2[:-1] * u2[:, None] + DD2[:-1] * x2[:-1, None]
act_a = np.max(np.abs(acc2) / AMAX, axis=1)
frac_sat = float(np.mean((act_a > 0.999) | (act_v[:-1] > 0.999)))
joint_v = int(np.argmax(np.bincount(np.argmax(np.abs(D2) * sd2[:, None] / VMAX, axis=1)[act_v > 0.999], minlength=6))) + 1 if np.any(act_v > 0.999) else 0
frac_v = float(np.mean(act_v > 0.999))

# ---------------------------------------------------------------- (3) 平滑：盒形窗滤波
tj = 1.0 / FN_TOOL
r_arm = float(np.hypot(*tcp_fk(thB)[:2, 3]))


def smoothed(eta):
    """限值乘 η 求时间最优，再把 s(t) 用宽 t_j 的盒形窗滑动平均；返回 (时刻, 关节角, 速度/加速度的最大利用率, 总时间)。"""
    x, u, t, _, _ = topp(s2, D2, DD2, eta * VMAX, eta * AMAX)
    tg = np.arange(0, t[-1] + dt / 2, dt)
    sg = resample_path(t, s2, x, u, tg)
    tf, sf = fir_smooth(tg, sg, tj, L_sig)
    th = segs_eval(S, np.clip(u_of(sf), 0, U))
    v = np.gradient(th, dt, axis=0)
    a = np.gradient(v, dt, axis=0)
    j = np.gradient(a, dt, axis=0)
    return tf, th, float(np.max(np.abs(v) / VMAX)), float(np.max(np.abs(a[2:-2]) / AMAX)), float(tf[-1]), a, j


tf1, th1, rv1, ra1, Tf1, a1, j1 = smoothed(1.0)
over_pct = 100 * (max(rv1, ra1) - 1)
assert ra1 > 1.0                                        # 不缩小限值时，滤波后略超限
lo, hi = 0.8, 1.0
for _ in range(14):
    mid = 0.5 * (lo + hi)
    if max(smoothed(mid)[2:4]) <= 1.0:
        lo = mid
    else:
        hi = mid
eta = lo
tfE, thE, rvE, raE, T_fir, aE, jE = smoothed(eta)
assert max(rvE, raE) <= 1.0
jmax_fir = float(np.max(np.abs(jE[3:-3, 0])))
# 时间最优（不滤波）的关节 1 加速度在跳变处的差商很大：以跳变量计
jump_opt = float(np.max(np.abs(np.diff(acc2[:, 0]))))


def resid(t_s, acc1):
    br = poly_breaks(lambda tq: np.interp(tq, t_s, acc1), t_s[-1], n=min(6000, len(t_s) - 1))
    return response_pw(br, FN_TOOL, ZETA_TOOL, extra=0.0, nsub=1)[2] * r_arm * 1000


# 三种转移：样条整体缩放、时间最优、时间最优 + 滤波（关节 1 的加速度驱动 22.2 节的扭转模态）
ts_spl = np.arange(0, U + dt / 2, dt)
A_spl = resid(ts_spl, segs_eval(S, ts_spl, 2)[:, 0])
# 时间最优：每个网格区间内 σ̈ 为常数，关节 1 的加速度近似为阶梯函数；按阶梯精确求响应（折点成对给出，时长为零的段跳过）。
# 注意不能只取到最后一个区间的中点：末段时间较长，那时关节仍在减速，截掉会带来明显的误差。
br_opt = [pt for k in range(N2) for pt in ((t2[k], acc2[k, 0]), (t2[k + 1], acc2[k, 0]))]
A_opt = response_pw(br_opt, FN_TOOL, ZETA_TOOL, extra=0.0, nsub=1)[2] * r_arm * 1000


def rk4_amp(t_grid, a_cell, h=2e-5):
    """另一种算法核对：四阶龙格-库塔法逐步积分（步长 h，每个网格区间内加速度为常数）。"""
    w_, z_ = 2 * math.pi * FN_TOOL, ZETA_TOOL
    p_, q_ = 0.0, 0.0
    f_ = lambda p, q, a: (q, -a - 2 * z_ * w_ * q - w_ * w_ * p)
    for k in range(len(a_cell)):
        n_ = max(1, int(math.ceil((t_grid[k + 1] - t_grid[k]) / h)))
        hh = (t_grid[k + 1] - t_grid[k]) / n_
        a = a_cell[k]
        for _ in range(n_):
            k1 = f_(p_, q_, a)
            k2 = f_(p_ + hh / 2 * k1[0], q_ + hh / 2 * k1[1], a)
            k3 = f_(p_ + hh / 2 * k2[0], q_ + hh / 2 * k2[1], a)
            k4 = f_(p_ + hh * k3[0], q_ + hh * k3[1], a)
            p_ += hh / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
            q_ += hh / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
    wd_ = w_ * math.sqrt(1 - z_ * z_)
    return math.hypot(p_, (q_ + z_ * w_ * p_) / wd_) * r_arm * 1000


A_opt_rk = rk4_amp(t2, acc2[:, 0])
assert abs(A_opt_rk - A_opt) < 1e-3 * A_opt
A_fir = resid(tfE, aE[:, 0])
TOL = 0.05
w = 2 * math.pi * FN_TOOL
wait = lambda A_: max(0.0, math.log(A_ / TOL) / (ZETA_TOOL * w))
W_spl, W_opt, W_fir = wait(A_spl), wait(A_opt), wait(A_fir)
GRIP, INS = 0.3, E4.P["T"]
cyc = {k: GRIP + T + Wt + INS + GRIP for k, (T, Wt) in
       {"stop": (E3.T_stop, 0.0), "spl": (U, W_spl), "opt": (T_opt, W_opt), "fir": (T_fir, W_fir)}.items()}
# 每点停下（五次多项式）在 B 处停下时的残余振动
br_stop = []
t0 = 0.0
for k in range(3):
    Tk = E3.T_seg[k]
    d = E3.Q[k + 1][0] - E3.Q[k][0]
    br_stop += [(t0 + tq, d * s_quintic(tq / Tk, 2) / Tk ** 2) for tq in np.linspace(0, Tk, 1500)]
    t0 += Tk
A_stop = response_pw(br_stop, FN_TOOL, ZETA_TOOL, extra=0.0, nsub=1)[2] * r_arm * 1000
W_stop = wait(A_stop)
cyc["stop"] = GRIP + E3.T_stop + W_stop + INS + GRIP

# ---------------------------------------------------------------- (4) 经过手腕奇异附近的直线
Tm, dline, th0 = wrist_line()
N4 = 3000
ells = np.linspace(0, 0.3, N4 + 1)
THL = follow_line(Tm, dline, th0, ells)
DL = np.gradient(THL, ells, axis=0)
DDL = np.gradient(DL, ells, axis=0)
vt, at_ = 0.25, 1.0
x4, u4, t4, K4, XV4 = topp(ells, DL, DDL, VMAX, AMAX, xcap=np.full(N4 + 1, vt ** 2), ucap=at_)
T_sing = float(t4[-1])
sd4 = np.sqrt(x4)
v_mid = float(sd4[N4 // 2])
v_min = float(sd4[1:-1].min())
k_min = int(np.argmin(sd4[1:-1])) + 1
t_slow = float(np.sum(np.diff(t4)[(sd4[:-1] < 0.05)]))
T_free = trap_plan(0.3, vt, at_)["T"]                   # 不考虑关节限值时：TCP 的梯形曲线
assert T_sing > T_free

out(L_sig=L_sig, L_sig_deg=deg(L_sig), T_line=T_line, T_trap=T_trap, sd_bar=sd_bar, sdd_bar=sdd_bar, N1=N1,
    T_opt=T_opt, T_cls=T_cls, T_spl=U, save_opt=100 * save_opt, N2=N2, gap1000=gap1000 * 1000, gap4000=gap4000 * 1000,
    rv=rv, ra=ra, frac_sat=100 * frac_sat, frac_v=100 * frac_v, joint_v=joint_v,
    tj=tj, over_pct=over_pct, eta=eta, T_fir=T_fir, jmax_fir=jmax_fir, jump_opt=jump_opt,
    A_spl=A_spl, A_opt=A_opt, A_opt_rk=A_opt_rk, A_fir=A_fir, A_stop=A_stop, W_spl=W_spl, W_opt=W_opt, W_fir=W_fir, W_stop=W_stop,
    cyc_stop=cyc["stop"], cyc_spl=cyc["spl"], cyc_opt=cyc["opt"], cyc_fir=cyc["fir"], T_stop=E3.T_stop, T_ins=INS, grip=GRIP,
    cond_bad=cond_bad, crude_bad=crude_bad, cond_n=len(cond_where),
    cond_sig1=cond_where[0][0], cond_j1=cond_where[0][1], cond_sig2=cond_where[-1][0], cond_j2=cond_where[-1][1],
    T_sing=T_sing, v_mid=v_mid, v_min=v_min, l_min=float(ells[k_min]), t_slow=t_slow, T_free=T_free, N4=N4)
