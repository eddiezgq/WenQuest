"""7.2 节的算例（欧拉法、龙格-库塔法、辛积分）。

算例 7.2.1：用欧拉法仿真关节电机的起动（一阶模型），h = 5 ms，t = 50 ms 时与解析解比较；
            把 h 逐次减半，测出误差之比 ≈ 2，即一阶方法。
算例 7.2.2：欧拉法的稳定性：h < 2τ 才不发散；h = 30 ms 与 h = 45 ms 两种步长的对比。
算例 7.2.3：连杆单摆（从水平位置释放）积分 2 s，五种方法在 h、h/2、h/4 下的误差，测出各自的阶。
算例 7.2.4：长时间仿真的能量漂移：欧拉法 10 s；RK4（h = 0.02 s 与 0.08 s）、辛欧拉法、施特默-韦莱法 1000 s。
另：一步映射的雅可比行列式（相空间面积之比）：欧拉法 1 + h²ω_n²，辛方法恰为 1。
"""
import math

import numpy as np
from scipy.integrate import solve_ivp

from _ode import euler, link_params, midpoint, motor_first_order, pend_energy, pend_f, rk4, run, run_pend, symp_euler, verlet
from bookout import out

# ---------------------------------------------------------------- 算例 7.2.1 电机起动
tau, K = motor_first_order()
u = 12.0
w_inf = K * u
f_m = lambda t, x: np.array([(K * u - x[0]) / tau])          # 式 (7.1.4)：ω̇ = (K u − ω)/τ
exact = lambda t: w_inf * (1 - math.exp(-t / tau))
T1 = 0.05
h1 = 0.005
traj = run(euler, f_m, [0.0], T1, h1, keep=True)[:, 0]
w1 = traj[-1]
e1 = w1 - exact(T1)
first_steps = traj[:3]
# 第一步：ω1 = 0 + h · K u/τ
assert abs(first_steps[1] - h1 * w_inf / tau) < 1e-9
hs = [0.005, 0.0025, 0.00125, 0.000625]
errs_m = [abs(run(euler, f_m, [0.0], T1, h)[0] - exact(T1)) for h in hs]
ratios_m = [errs_m[i] / errs_m[i + 1] for i in range(3)]
assert all(1.9 < r < 2.1 for r in ratios_m)                  # 一阶：步长减半，误差减半
# 欧拉法的显式解：ω_k = ω∞ (1 − (1 − h/τ)^k)（式 (7.2.6)）
k = int(round(T1 / h1))
assert abs(w1 - w_inf * (1 - (1 - h1 / tau) ** k)) < 1e-9

# ---------------------------------------------------------------- 算例 7.2.2 稳定性
h_max = 2 * tau
g30 = 1 - 0.030 / tau                                        # 放大因子 1 − h/τ
g45 = 1 - 0.045 / tau
w30 = run(euler, f_m, [0.0], 0.3, 0.030, keep=True)[:, 0]
w45 = run(euler, f_m, [0.0], 0.315, 0.045, keep=True)[:, 0]
assert abs(w30[-1] - w_inf) < abs(w30[1] - w_inf)            # 收敛（有振荡）
assert abs(w45[-1] - w_inf) > 5 * w_inf                      # 发散
w45_last = w45[-1]
n45 = len(w45) - 1

# ---------------------------------------------------------------- 算例 7.2.3 单摆，测阶
Jo, lc, wn2 = link_params()
wn = math.sqrt(wn2)
x0 = np.array([math.pi / 2, 0.0])
T2 = 2.0
ref = solve_ivp(pend_f(wn2), (0, T2), x0, method="DOP853", rtol=1e-13, atol=1e-13).y[:, -1]
hs2 = [0.01, 0.005, 0.0025]
orders, errs_p = {}, {}
for meth in ("euler", "midpoint", "rk4", "symp", "verlet"):
    es = [float(np.linalg.norm(run_pend(meth, wn2, x0, T2, h)[-1] - ref)) for h in hs2]
    errs_p[meth] = es
    orders[meth] = [math.log2(es[i] / es[i + 1]) for i in range(2)]
expect = {"euler": 1, "midpoint": 2, "rk4": 4, "symp": 1, "verlet": 2}
for meth, p in expect.items():
    assert all(abs(o - p) < 0.15 for o in orders[meth]), (meth, orders[meth])

# 中点法的一步误差（局部截断误差）随 h³ 减小
xl = np.array([0.7, -1.3])                                   # 任取一个状态
loc = [float(np.linalg.norm(midpoint(pend_f(wn2), 0, xl, h) -
                            solve_ivp(pend_f(wn2), (0, h), xl, method="DOP853", rtol=1e-13, atol=1e-15).y[:, -1]))
       for h in (0.02, 0.01)]
loc_ratio = loc[0] / loc[1]
assert 7.5 < loc_ratio < 8.5

# ---------------------------------------------------------------- 算例 7.2.4 能量漂移
E0 = float(pend_energy(x0, wn2))


def rel_energy(meth, h, T):
    xs = run_pend(meth, wn2, x0, T, h)
    return (pend_energy(xs, wn2) - E0) / E0


eu = rel_energy("euler", 0.02, 10.0)
r4 = rel_energy("rk4", 0.02, 1000.0)
r4c = rel_energy("rk4", 0.08, 1000.0)
se = rel_energy("symp", 0.02, 1000.0)
vv = rel_energy("verlet", 0.02, 1000.0)
i100 = int(round(100 / 0.02))
eu10 = float(eu[-1])
r4_100, r4_1000 = float(r4[i100]), float(r4[-1])
r4c_100, r4c_1000 = float(r4c[int(round(100 / 0.08))]), float(r4c[-1])
se_max, vv_max = float(np.abs(se).max()), float(np.abs(vv).max())
vv_max_100 = float(np.abs(vv[:i100 + 1]).max())
assert abs(r4_1000) > 5 * abs(r4_100)                        # RK4 的能量误差持续累积
assert vv_max < 1.2 * vv_max_100                             # 韦莱法的能量误差有界：后 900 s 不再变大
assert se_max < 0.06 and abs(r4c_1000) > 0.3

# 一步映射的雅可比行列式（数值求导）：相空间面积之比
def jac_det(step, x, h, eps=1e-7):
    J = np.column_stack([(step(x + eps * e, h) - step(x - eps * e, h)) / (2 * eps) for e in np.eye(2)])
    return float(np.linalg.det(J))


hx = 0.02
xt = np.array([0.7, -1.3])
det_eu = jac_det(lambda x, h: euler(pend_f(wn2), 0, x, h), xt, hx)
det_se = jac_det(lambda x, h: symp_euler(wn2, x, h), xt, hx)
det_vv = jac_det(lambda x, h: verlet(wn2, x, h), xt, hx)
det_r4 = jac_det(lambda x, h: rk4(pend_f(wn2), 0, x, h), xt, hx)
assert abs(det_se - 1) < 1e-8 and abs(det_vv - 1) < 1e-8
assert abs(det_eu - (1 + hx ** 2 * wn2 * math.cos(xt[0]))) < 1e-8   # 1 + h² ω_n² cos θ
# 小摆幅（线性化）时的预测：欧拉法每步能量乘 1 + (hω_n)²；RK4 每步能量乘 |R(ihω_n)|² = 1 − (hω_n)⁶/72 + (hω_n)⁸/576
y = hx * wn
xs_small = run_pend("euler", wn2, [math.radians(1), 0.0], 5.0, hx)
eu_small = float(pend_energy(xs_small[-1], wn2) / pend_energy(xs_small[0], wn2))
eu_small_pred = (1 + y * y) ** int(round(5 / hx))
assert abs(eu_small / eu_small_pred - 1) < 0.02
xs_small = run_pend("rk4", wn2, [math.radians(2), 0.0], 1000.0, hx)
r4_small = float(1 - pend_energy(xs_small[-1], wn2) / pend_energy(xs_small[0], wn2)) * 100
r4_small_pred = (1 - (1 - y ** 6 / 72 + y ** 8 / 576) ** int(round(1000 / hx))) * 100
assert abs(r4_small / r4_small_pred - 1) < 0.02
# 辛欧拉法对小摆幅精确保持 Q = θ̇² + ω_n²θ² − hω_n²θθ̇（式 (7.2.15)），能量本身只在 O(h) 的范围内振荡
xs_small = run_pend("symp", wn2, [math.radians(2), 0.0], 100.0, hx)
from _ode import symp_euler as _se
th_l, om_l = math.radians(2), 0.0
Qs = []
for _ in range(2000):                                         # 线性化的辛欧拉法：sin θ 换成 θ
    om_l = om_l - hx * wn2 * th_l
    th_l = th_l + hx * om_l
    Qs.append(om_l ** 2 + wn2 * th_l ** 2 - hx * wn2 * th_l * om_l)
assert np.ptp(Qs) < 1e-12 * Qs[0]
amp_eu = math.sqrt(1 + (hx * wn) ** 2)
# RK4 在负实轴上的稳定区间 [−x*, 0]：放大因子 G(z) = 1 + z + z²/2 + z³/6 + z⁴/24 在负实轴上为正，区间的端点满足 G = 1
from scipy.optimize import brentq
G4 = lambda z: 1 + z + z * z / 2 + z ** 3 / 6 + z ** 4 / 24
rk4_lim = -brentq(lambda z: G4(z) - 1, -3.5, -2.0)
assert all(abs(G4(z)) <= 1 + 1e-12 for z in np.linspace(-rk4_lim, 0, 200)) and G4(-rk4_lim - 0.01) > 1                       # 线性化后欧拉法每步把振幅放大的倍数
steps_10 = int(round(10 / hx))

out(
    tau_ms=tau * 1e3, w_inf=w_inf, h1_ms=h1 * 1e3, w1=w1, w_exact=exact(T1), e1=e1, e1_rel=abs(e1) / exact(T1) * 100,
    s1=float(first_steps[1]), s2=float(first_steps[2]),
    em1=errs_m[0], em2=errs_m[1], em3=errs_m[2], em4=errs_m[3],
    rm1=ratios_m[0], rm2=ratios_m[1], rm3=ratios_m[2],
    hmax_ms=h_max * 1e3, g30=g30, g45=g45, w30_end=float(w30[-1]), w45_last=w45_last, n45=n45,
    w30_1=float(w30[1]), w30_2=float(w30[2]), w45_1=float(w45[1]), w45_2=float(w45[2]),
    wn=wn, wn2=wn2,
    **{f"e_{m_}{i}": errs_p[m_][i] for m_ in errs_p for i in range(3)},
    **{f"p_{m_}{i}": orders[m_][i] for m_ in orders for i in range(2)},
    loc1=loc[0], loc2=loc[1], loc_ratio=loc_ratio,
    eu10=eu10 * 100, eu10x=1 + eu10, r4_100=-r4_100 * 100, r4_1000=-r4_1000 * 100, r4c_100=-r4c_100 * 100, r4c_1000=-r4c_1000 * 100,
    se_max=se_max * 100, vv_max=vv_max * 100, vv_max_100=vv_max_100 * 100,
    det_eu=det_eu, det_se=det_se, det_vv=det_vv, det_r4=det_r4, amp_eu=amp_eu, steps_10=steps_10,
    amp_eu_10=amp_eu ** steps_10, y=y, eu_small=eu_small, eu_small_pred=eu_small_pred, r4_small=r4_small,
    r4_small_pred=r4_small_pred, y6=y ** 6 / 72, rk4_lim=rk4_lim,
)
