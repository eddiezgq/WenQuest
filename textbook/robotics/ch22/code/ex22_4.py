"""22.4 节的计算：笛卡尔直线与圆弧。

(1) 算例 22.4.1：送料。TCP 从卡盘前 B 沿主轴方向（−x_s）直线移动 0.12 m 到 C，姿态不变。沿直线的时间标度用梯形速度曲线，
    速度 0.10 m/s、加速度 0.5 m/s²（示意值）。每 2 ms 求一次解析逆解；关节速度用 θ̇ = J_s⁻¹ V_s，关节加速度用
    θ̈ = J_s⁻¹(V̇_s − J̇_s θ̇)（式 (16.1.8)、定理 16.1.3），分别与逆解序列的差商核对。
    比较：同一时间内在关节空间作五次多项式点到点运动，TCP 偏离直线和姿态偏离的最大值。
(2) 算例 22.4.2：过三点的圆弧（定理 22.4.2）。取 10.5 节去毛刺的圆（圆心 (−0.50, −0.20, 0.25) m、半径 0.10 m）上
    圆心角 0°、50°、140° 的三点，由三点求圆心、半径和圆心角，与原圆核对；沿弧长用梯形（a_t = 0.5 m/s²，v = 0.25 m/s，
    与算例 10.5.1 相同）和 S 形（加加速度 5 m/s³，示意值）时间标度，比较总加速度的最大值与跳变；数值求导核对 a_n = κ ℓ̇²。
(3) 算例 22.4.3：按弧长重新参数化。10.5 节的涂胶椭圆（a = 0.12 m、b = 0.08 m）以 v₀ = √(1/κ_max) 匀速运动：
    每 2 ms 用牛顿法由 ℓ(u) = v₀ t 解出参数 u，统计迭代次数；与匀速增加 u 的做法比较速率的变化。
(4) 算例 22.4.4：经过手腕奇异附近的直线（与算例 15.3.2 相同的直线）。沿直线逐点求逆解，算出各关节对弧长的导数
    θ′(ℓ)，由关节速度上限得到每一点允许的最大直线速度 min_i v_i/|θ_i′(ℓ)|；匀速 0.1 m/s 时关节 4、6 的转速。
"""
import math

import numpy as np

from _traj import (AMAX, VMAX, cell_joints, circle3, follow_line, jacobian_space, jacobian_space_dot, s_quintic, scurve_eval,
                   scurve_plan, tcp_fk, tcp_ik, trap_eval, trap_plan, UR_S, wrist_line, logR, wrap)
from bookout import out, tex

deg = np.degrees
thR, thA, thB, thC = cell_joints()

# ---------------------------------------------------------------- (1) 送料的直线
TB_ = tcp_fk(thB)
TC_ = tcp_fk(thC)
pB, pC = TB_[:3, 3], TC_[:3, 3]
Lins = float(np.linalg.norm(pC - pB))
u = (pC - pB) / Lins
v_lin, a_lin = 0.10, 0.5
P = trap_plan(Lins, v_lin, a_lin)
dt = 0.002
t = np.arange(0, P["T"] + dt / 2, dt)
ell, ld, ldd = trap_eval(P, t)
TH = []
th = thB.copy()
for l in ell:
    T = TB_.copy()
    T[:3, 3] = pB + l * u
    th = tcp_ik(T, th)
    TH.append(th)
TH = np.array(TH)
assert np.allclose(TH[-1], thC, atol=1e-9)
# 关节速度与加速度：微分关系（两种算法核对：差商）
dth_J = np.array([np.linalg.solve(jacobian_space(UR_S, q), np.r_[np.zeros(3), u * v]) for q, v in zip(TH, ld)])
ddth_J = []
for q, qd, a in zip(TH, dth_J, ldd):
    J = jacobian_space(UR_S, q)
    Jd = jacobian_space_dot(UR_S, q, qd)
    ddth_J.append(np.linalg.solve(J, np.r_[np.zeros(3), u * a] - Jd @ qd))
ddth_J = np.array(ddth_J)
dth_fd = (TH[2:] - TH[:-2]) / (2 * dt)
ddth_fd = (TH[2:] - 2 * TH[1:-1] + TH[:-2]) / dt ** 2
# 差商在加速度跳变处（t_a、t_a + t_c 附近）不准，只在远离跳变的点比较
mask = np.ones(len(t) - 2, bool)
for tj in (0.0, P["ta"], P["ta"] + P["tc"], P["T"]):
    mask &= np.abs(t[1:-1] - tj) > 3 * dt
err_v = float(np.max(np.abs(dth_fd[mask] - dth_J[1:-1][mask])))
err_a = float(np.max(np.abs(ddth_fd[mask] - ddth_J[1:-1][mask])))
assert err_v < 1e-6 and err_a < 2e-3
vj_max = deg(np.abs(dth_J).max(0))
aj_max = np.abs(ddth_J).max(0)
k_vmax = int(np.argmax(vj_max))
# 关节空间的五次多项式（同样的时间）
dq = thC - thB
dev, odev = [], []
for tt in t:
    q = thB + s_quintic(tt / P["T"]) * dq
    Tq = tcp_fk(q)
    r = Tq[:3, 3] - pB
    dev.append(np.linalg.norm(r - (r @ u) * u))
    odev.append(np.linalg.norm(logR(TB_[:3, :3].T @ Tq[:3, :3])))
dev_mm = float(max(dev)) * 1000
odev_deg = float(deg(max(odev)))

# ---------------------------------------------------------------- (2) 过三点的圆弧
c0, R0 = np.array([-0.50, -0.20, 0.25]), 0.10
pts = [c0 + R0 * np.array([math.cos(math.radians(a)), math.sin(math.radians(a)), 0]) for a in (0, 50, 140)]
c, rho, uu, ww, ph2, ph3 = circle3(*pts)
assert np.allclose(c, c0, atol=1e-12) and abs(rho - R0) < 1e-12 and abs(math.degrees(ph3) - 140) < 1e-9 and abs(math.degrees(ph2) - 50) < 1e-9
L_arc = rho * ph3
vt, at, jt = 0.25, 0.5, 5.0
Pt = trap_plan(L_arc, vt, at)
Ps = scurve_plan(L_arc, vt, at, jt)


def arc_point(l):
    return c + rho * (math.cos(l / rho) * uu + math.sin(l / rho) * ww)


def accel_profile(kind, n=4001):
    if kind == "trap":
        tt = np.linspace(0, Pt["T"], n)
        l, ldot, lddot = trap_eval(Pt, tt)
    else:
        tt = np.linspace(0, Ps["T"], n)
        l, ldot, lddot, _ = scurve_eval(Ps, tt)
    an = ldot ** 2 / rho
    return tt, l, ldot, lddot, an, np.hypot(lddot, an)


tt_t, l_t, v_t, at_t, an_t, A_t = accel_profile("trap")
tt_s, l_s, v_s, at_s, an_s, A_s = accel_profile("s")
amax_trap = float(A_t.max())
amax_s = float(A_s.max())
# 梯形：加速结束时 |a| 从 √(a_t² + a_n²) 跳到 a_n
jump_trap = math.hypot(at, vt ** 2 / rho) - vt ** 2 / rho
# 数值求导核对（S 形，取中段一点）：p̈ 的法向分量 = κ ℓ̇²
k = 1700
h = 1e-4
f = lambda tq: arc_point(scurve_eval(Ps, tq)[0][0])
acc_num = (f(tt_s[k] + h) - 2 * f(tt_s[k]) + f(tt_s[k] - h)) / h ** 2
tdir = -math.sin(l_s[k] / rho) * uu + math.cos(l_s[k] / rho) * ww
assert abs(acc_num @ tdir - at_s[k]) < 1e-4 and abs(np.linalg.norm(acc_num - (acc_num @ tdir) * tdir) - an_s[k]) < 1e-4
T_arc_t, T_arc_s = Pt["T"], Ps["T"]

# ---------------------------------------------------------------- (3) 按弧长重新参数化：涂胶椭圆
ea, eb = 0.12, 0.08
kmax = ea / eb ** 2
v0 = math.sqrt(1.0 / kmax)
sp = lambda uq: math.hypot(ea * math.sin(uq), eb * math.cos(uq))       # |p′(u)|，p(u) = (a cos u, b sin u)
# 弧长函数 ℓ(u)：每段用 5 点高斯-勒让德积分（段长 2π/2000）
gx, gw = np.polynomial.legendre.leggauss(5)
NU = 2000
ub = np.linspace(0, 2 * math.pi, NU + 1)
seg = []
for a_, b_ in zip(ub[:-1], ub[1:]):
    m, r = (a_ + b_) / 2, (b_ - a_) / 2
    seg.append(r * sum(w * sp(m + r * x) for x, w in zip(gx, gw)))
lcum = np.concatenate([[0.0], np.cumsum(seg)])
L_ell = float(lcum[-1])


def ell_of(uq):
    j = min(int(uq / (2 * math.pi) * NU), NU - 1)
    a_ = ub[j]
    m, r = (a_ + uq) / 2, (uq - a_) / 2
    return lcum[j] + r * sum(w * sp(m + r * x) for x, w in zip(gx, gw))


T_lap = L_ell / v0
dtg = 0.002
N_steps = int(T_lap / dtg)
uq, its, U = 0.0, [], []
for kk in range(N_steps + 1):
    target = v0 * kk * dtg
    n_it = 0
    while True:
        e = ell_of(uq) - target
        if abs(e) < 1e-12 or n_it >= 20:
            break
        uq -= e / sp(uq)
        n_it += 1
    its.append(n_it)
    U.append(uq)
U = np.array(U)
Pell = np.column_stack([ea * np.cos(U), eb * np.sin(U)])
speed = np.linalg.norm(np.diff(Pell, axis=0), axis=1) / dtg
spd_err = float(np.max(np.abs(speed - v0)))
assert max(its) <= 3 and spd_err < 2e-4                 # 差商（弦长/时间）本身有 O(Δt²) 的误差
# 匀速增加参数 u（一圈同样的时间）：速率的变化
w_u = 2 * math.pi / T_lap
uu_ = np.linspace(0, 2 * math.pi, 4001)
sp_u = np.array([sp(x) for x in uu_]) * w_u
ratio_u = float(sp_u.max() / sp_u.min())

# ---------------------------------------------------------------- (4) 经过手腕奇异附近的直线
Tm, dline, th0 = wrist_line()
ells = np.linspace(0, 0.3, 3001)
THL = follow_line(Tm, dline, th0, ells)
dthl = np.gradient(THL, ells, axis=0)                   # θ′(ℓ)，rad/m
v_allow = np.min(VMAX[None, :] / np.maximum(np.abs(dthl), 1e-12), axis=1)
k_mid = int(np.argmin(v_allow))
t5min = float(np.min(np.abs(deg(THL[:, 4]))))
sp46 = deg(0.1 * np.abs(dthl[:, [3, 5]]).max(0))     # 匀速 0.1 m/s 时关节 4、6 的最大转速
lim_joint = int(np.argmin(VMAX[None, :] / np.maximum(np.abs(dthl[k_mid]), 1e-12))) + 1
T_const = 0.3 / 0.1
T_cap = float(np.trapezoid(1.0 / np.minimum(0.1, v_allow), ells))
frac_slow = float(np.mean(v_allow < 0.1))

out(pB=tex(pB, 3), pC=tex(pC, 3), L_ins=Lins, v_lin=v_lin, a_lin=a_lin, T_ins=P["T"], ta_ins=P["ta"],
    vj_max=", ".join(f"{x:.1f}" for x in vj_max), vj_top=float(vj_max.max()), vj_k=k_vmax + 1, aj_top=float(aj_max.max()),
    err_v=err_v, err_a=err_a, dev_mm=dev_mm, odev_deg=odev_deg,
    c=tex(c, 3), rho=rho, ph2=math.degrees(ph2), ph3=math.degrees(ph3), L_arc=L_arc, T_arc_t=T_arc_t, T_arc_s=T_arc_s,
    amax_trap=amax_trap, amax_s=amax_s, jump_trap=jump_trap, an_end=vt ** 2 / rho, tv_arc=Pt["tc"],
    kmax=kmax, v0=v0, L_ell=L_ell, T_lap=T_lap, its_max=max(its), its_mean=float(np.mean(its[1:])), spd_err=spd_err,
    ratio_u=ratio_u, N_steps=N_steps,
    t5min=t5min, v_allow_mid=float(v_allow[k_mid]), v_allow_end=float(min(v_allow[0], v_allow[-1])), sp4=sp46[0], sp6=sp46[1],
    lim_joint=lim_joint, T_const=T_const, T_cap=T_cap, frac_slow=100 * frac_slow, l_mid=float(ells[k_mid]))
